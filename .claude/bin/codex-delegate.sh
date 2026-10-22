#!/usr/bin/env bash
# Run one delegated task in Codex inside a fresh kt/claude/<slug>-<suffix> worktree (no yarn install).
# Safe to run many times in parallel: names get a random suffix, and the shared-git setup steps
# (fetch, worktree creation) run under a per-repository lock.
#
# Modes:
#   local (default)  Codex works, changes are committed (--no-verify) on the branch, and the worktree
#                    is kept for the coordinator to inspect, verify or continue. Nothing is pushed.
#   pr               Fire-and-forget: commit (--no-verify), push and open a PR for CI and the PR
#                    merge queue to validate, then remove the worktree. Needs --title and --pr-body-file.
#
# Usage:
#   codex-delegate.sh --repo <path> --slug <slug> --brief-file <file> [--effort low|medium|high|xhigh]
#     [--model <codex model>] [--base main] [--mode local|pr] [--title <title>] [--pr-body-file <file>] [--draft]
#
#   codex-delegate.sh --cleanup [--repo <path>] [--older-than-days 7] [--target <state dir or branch>]
#     Removes delegation worktrees and state directories:
#       --target     that run now, deleting its local branch too (the coordinator is done with it)
#       otherwise    runs whose branch is merged into origin/main or pushed to origin, and runs older
#                    than --older-than-days (default 7). Unpushed branches with commits are kept, as are
#                    running runs and worktrees with uncommitted changes.
#
# --model defaults to gpt-6.1-sol. Codex's model catalog depends on the client version, so this uses the
# ChatGPT app's bundled CLI (kept current by the app) unless CODEX_BIN overrides it.
#
# Each run's state directory holds meta, log, brief.md, codex-summary.md (Codex's final message) and
# status: running | no-changes | committed <branch> <worktree> | done <pr url> | failed <step>.

set -euo pipefail

STATE_ROOT="$HOME/.claude/codex-delegate"
base=main
mode=local
model="gpt-6.1-sol"
effort=""
codex_bin="${CODEX_BIN:-/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex}"
[ -x "$codex_bin" ] || codex_bin="$(command -v codex)"
draft=""
cleanup=0
older_than_days=7
target=""
repo="" slug="" title="" brief_file="" body_file=""

while [ $# -gt 0 ]; do
    case "$1" in
        --repo) repo="$2"; shift 2 ;;
        --slug) slug="$2"; shift 2 ;;
        --title) title="$2"; shift 2 ;;
        --brief-file) brief_file="$2"; shift 2 ;;
        --pr-body-file) body_file="$2"; shift 2 ;;
        --base) base="$2"; shift 2 ;;
        --model) model="$2"; shift 2 ;;
        --effort) effort="$2"; shift 2 ;;
        --mode) mode="$2"; shift 2 ;;
        --draft) draft="--draft"; shift ;;
        --cleanup) cleanup=1; shift ;;
        --older-than-days) older_than_days="$2"; shift 2 ;;
        --target) target="$2"; shift 2 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

# Per-repository lock around shared-git mutations. mkdir is atomic; a lock whose holder died is reclaimed.
lock_dir=""
acquire_lock() {
    lock_dir="$(cd "$1" && cd "$(git rev-parse --git-common-dir)" && pwd)/codex-delegate.lock"
    local waited=0 holder
    until mkdir "$lock_dir" 2>/dev/null; do
        holder="$(cat "$lock_dir/pid" 2>/dev/null || true)"
        if [ -n "$holder" ] && ! kill -0 "$holder" 2>/dev/null; then rm -rf "$lock_dir"; continue; fi
        if [ "$waited" -ge 300 ]; then echo "timed out waiting for $lock_dir"; lock_dir=""; return 1; fi
        sleep 1
        waited=$((waited + 1))
    done
    echo $$ > "$lock_dir/pid"
}
release_lock() {
    if [ -n "$lock_dir" ]; then rm -rf "$lock_dir"; lock_dir=""; fi
}

# Deletes a local branch when the coordinator is done with it, or when it holds no commits beyond its base.
drop_branch_if() {
    local run_repo="$1" run_branch="$2" run_base="$3" force="$4"
    git -C "$run_repo" show-ref --verify --quiet "refs/heads/$run_branch" || return 0
    if [ "$force" = 1 ] || [ "$(git -C "$run_repo" rev-list --count "origin/$run_base..$run_branch" 2>/dev/null || echo 1)" = 0 ]; then
        git -C "$run_repo" branch -D "$run_branch" >/dev/null
        echo "  deleted branch $run_branch"
    fi
}

if [ "$cleanup" = 1 ]; then
    [ -n "$repo" ] && repo="$(git -C "$repo" rev-parse --show-toplevel)"
    now="$(date +%s)"
    touched_repos=""
    for state in "$STATE_ROOT"/*; do
        [ -f "$state/meta" ] || continue
        run_repo="$(sed -n 's/^repo=//p' "$state/meta")"
        run_branch="$(sed -n 's/^branch=//p' "$state/meta")"
        run_worktree="$(sed -n 's/^worktree=//p' "$state/meta")"
        run_base="$(sed -n 's/^base=//p' "$state/meta")"
        run_pid="$(sed -n 's/^pid=//p' "$state/meta")"
        run_started="$(sed -n 's/^started=//p' "$state/meta")"
        run_status="$(cat "$state/status" 2>/dev/null || echo unknown)"
        if [ -n "$repo" ] && [ "$run_repo" != "$repo" ]; then continue; fi
        if [ -n "$target" ] && [ "$state" != "${target%/}" ] && [ "$run_branch" != "$target" ]; then continue; fi
        if [ "${run_status%% *}" = running ] && kill -0 "$run_pid" 2>/dev/null; then
            echo "keep (still running) $state"; continue
        fi
        age_days=$(( (now - run_started) / 86400 ))

        reason=""
        if [ -n "$target" ]; then
            reason=requested
        elif [ -n "$run_worktree" ] && [ -d "$run_worktree" ] && [ -n "$run_branch" ]; then
            if git -C "$run_repo" merge-base --is-ancestor "$run_branch" "origin/$run_base" 2>/dev/null; then
                reason=merged
            elif git -C "$run_repo" ls-remote --exit-code --heads origin "$run_branch" >/dev/null 2>&1; then
                reason=pushed
            fi
        fi
        if [ -z "$reason" ] && [ "$age_days" -ge "$older_than_days" ]; then reason=expired; fi
        if [ -z "$reason" ]; then echo "keep ($run_status, ${age_days}d old) $state"; continue; fi

        if [ -n "$run_worktree" ] && [ -d "$run_worktree" ]; then
            if [ -n "$(git -C "$run_worktree" status --porcelain 2>/dev/null)" ]; then
                echo "keep (uncommitted changes in $run_worktree) $state"; continue
            fi
            acquire_lock "$run_repo"
            git -C "$run_repo" worktree remove "$run_worktree"
            echo "  removed worktree $run_worktree"
            if [ "$reason" = requested ]; then drop_branch_if "$run_repo" "$run_branch" "$run_base" 1
            else drop_branch_if "$run_repo" "$run_branch" "$run_base" 0; fi
            release_lock
        elif [ -n "$run_branch" ] && [ -d "$run_repo" ]; then
            acquire_lock "$run_repo"
            if [ "$reason" = requested ]; then drop_branch_if "$run_repo" "$run_branch" "$run_base" 1
            else drop_branch_if "$run_repo" "$run_branch" "$run_base" 0; fi
            release_lock
        fi
        rm -rf "$state"
        echo "removed ($reason) $state"
        case " $touched_repos " in *" $run_repo "*) ;; *) touched_repos="$touched_repos $run_repo" ;; esac
    done
    for touched in $touched_repos; do
        if [ -d "$touched" ]; then git -C "$touched" worktree prune; fi
    done
    exit 0
fi

for required in repo slug brief_file; do
    if [ -z "${!required}" ]; then echo "missing --${required//_/-}" >&2; exit 2; fi
done
if ! [[ "$slug" =~ ^[a-z0-9][a-z0-9-]{1,50}$ ]]; then echo "slug must be lowercase kebab-case" >&2; exit 2; fi
case "$mode" in local|pr) ;; *) echo "--mode must be local or pr" >&2; exit 2 ;; esac
case "$effort" in ""|low|medium|high|xhigh|max) ;; *) echo "--effort must be low, medium, high, xhigh or max" >&2; exit 2 ;; esac
[ -f "$brief_file" ] || { echo "brief file not found: $brief_file" >&2; exit 2; }
if [ "$mode" = pr ]; then
    [ -n "$title" ] || { echo "--mode pr needs --title" >&2; exit 2; }
    [ -f "$body_file" ] || { echo "--mode pr needs an existing --pr-body-file" >&2; exit 2; }
fi

repo="$(git -C "$repo" rev-parse --show-toplevel)"
STATE_DIR="${STATE_DIR:-$STATE_ROOT/$slug-$(date +%Y%m%d-%H%M%S)-$$}"
mkdir -p "$STATE_DIR"
[ "$brief_file" -ef "$STATE_DIR/brief.md" ] || cp "$brief_file" "$STATE_DIR/brief.md"
if [ "$mode" = pr ]; then [ "$body_file" -ef "$STATE_DIR/pr-body.md" ] || cp "$body_file" "$STATE_DIR/pr-body.md"; fi
printf 'repo=%s\nbase=%s\npid=%s\nstarted=%s\n' "$repo" "$base" "$$" "$(date +%s)" > "$STATE_DIR/meta"
exec >>"$STATE_DIR/log" 2>&1

step="start"
branch=""
worktree=""
trap 'release_lock; echo "failed $step" > "$STATE_DIR/status"; echo "FAILED at step: $step${worktree:+ (worktree kept at $worktree)}"' ERR
echo running > "$STATE_DIR/status"

step="worktree"
acquire_lock "$repo"
common_dir="$(cd "$repo" && cd "$(git rev-parse --git-common-dir)" && pwd)"
mkdir -p "$common_dir/info"
grep -qxF '.claude/worktrees/' "$common_dir/info/exclude" 2>/dev/null || echo '.claude/worktrees/' >> "$common_dir/info/exclude"
for attempt in 1 2 3 4 5; do
    candidate="$slug-$(openssl rand -hex 2)"
    if ! git -C "$repo" show-ref --verify --quiet "refs/heads/kt/claude/$candidate" && [ ! -e "$repo/.claude/worktrees/codex-$candidate" ]; then
        slug="$candidate"
        break
    fi
    [ "$attempt" = 5 ] && { echo "could not find a free branch name for $slug"; false; }
done
branch="kt/claude/$slug"
worktree="$repo/.claude/worktrees/codex-$slug"
printf 'branch=%s\nworktree=%s\n' "$branch" "$worktree" >> "$STATE_DIR/meta"
git -C "$repo" fetch origin "$base"
git -C "$repo" worktree add --no-track -b "$branch" "$worktree" "origin/$base"
release_lock
[ -n "$title" ] || title="Codex: $slug"
echo "$(date) mode=$mode repo=$repo branch=$branch worktree=$worktree base=$base codex=$codex_bin ($("$codex_bin" --version)) model=$model effort=${effort:-config default}"

step="codex"
{
    cat <<'EOF'
You are completing a delegated task in this git worktree. Another agent coordinates the work and will read your final reply.

Hard constraints:
- Edit files only inside the current working directory.
- Dependencies are NOT installed. Do not run yarn, npm, npx, tsc, jest, eslint, prettier or any install. Work by reading code.
- Do not run git commit, git push, git checkout, git reset or gh. The coordinator handles git and pull requests.
- Read and follow the AGENTS.md files from the repository root down to every path you change.
- Stay within the task's scope. If it is ambiguous, choose the most conservative reading and say so.

When finished, reply with: the outcome or answer, the files you changed and why, anything in the task you did not do, and any place you are unsure the code compiles or is correct.

Task:

EOF
    cat "$STATE_DIR/brief.md"
} > "$STATE_DIR/codex-prompt.md"

codex_args=(exec -C "$worktree" -s workspace-write -m "$model" -o "$STATE_DIR/codex-summary.md")
if [ -n "$effort" ]; then codex_args+=(-c "model_reasoning_effort=$effort"); fi
"$codex_bin" "${codex_args[@]}" - < "$STATE_DIR/codex-prompt.md"

step="commit"
git -C "$worktree" add -A
if git -C "$worktree" diff --cached --quiet; then
    echo "Codex made no changes"
    acquire_lock "$repo"
    git -C "$repo" worktree remove "$worktree"
    git -C "$repo" branch -D "$branch"
    release_lock
    echo no-changes > "$STATE_DIR/status"
    exit 0
fi
git -C "$worktree" commit --no-verify -F - <<EOF
$title

Written by Codex ($model${effort:+ $effort}) from a Claude Code delegation. Not validated locally
(no install, pre-commit hook skipped).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
git -C "$worktree" diff --stat HEAD~1 HEAD

if [ "$mode" = local ]; then
    echo "committed $branch $worktree" > "$STATE_DIR/status"
    echo "$(date) finished; remove with: $0 --cleanup --target $STATE_DIR"
    exit 0
fi

step="push"
git -C "$worktree" push -u origin "$branch"

step="pr"
{
    cat "$STATE_DIR/pr-body.md"
    printf '\n\n## Codex first-pass notes\n\n'
    cat "$STATE_DIR/codex-summary.md" 2>/dev/null || echo "(Codex left no summary.)"
    printf '\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n'
} > "$STATE_DIR/pr-body-final.md"
pr_url="$(cd "$worktree" && gh pr create --base "$base" --head "$branch" --title "$title" --body-file "$STATE_DIR/pr-body-final.md" $draft)"
echo "PR: $pr_url"

step="cleanup"
acquire_lock "$repo"
git -C "$repo" worktree remove "$worktree"
release_lock
echo "done $pr_url" > "$STATE_DIR/status"
echo "$(date) finished"
