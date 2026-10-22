---
name: pr-merge-queue
description: Coordinate bounded repairs, independent reviews, and safe merges of the authenticated user's open PRs after explicit invocation. Configuration work does not run the queue.
disable-model-invocation: true
---

# PR merge queue

Run only after explicit invocation, including an approved scheduled prompt that invokes this skill. Editing its configuration does not invoke it. Use direct `gh`/git commands and native task/agent tools; no custom queue scripts, registries, persistent queue state, or locks.

Every manual or scheduled run must end with a concise, user-visible final reply, including errors or interruptions with the outcome and blockers known so far. An early commentary update or automation memory update does not replace the final reply.

## Concurrent-run guard

After parameter validation and recording the invocation start below, but before
GitHub discovery, loading specialists, dispatching work, or making queue changes,
use native task tools (`list_threads` and targeted `read_thread` as needed) to
identify this invocation’s chat ID, execution host, and **current live title**,
then list chats and inspect their live execution status. Resolve the current ID from trusted invocation/runtime context; never
identify this chat by title alone. Call `list_threads` with `limit=50` (the
supported maximum) and inspect both pinned and unpinned results across available
hosts. Recheck known same-title peers from this invocation’s native task context
with targeted `read_thread` calls when they are absent from the listing.
Do not hardcode a title such as "PR merge queue": use the invoking chat's title
so the guard follows future renames. Exclude this chat by identity, not by name.

If **any other chat with exactly the same current title is actively running**,
stop this invocation immediately. Do not wait, interrupt or message that chat,
start specialists, discover PRs, or change queue state. End with a concise final
reply naming the running chat and its ID, stating that this run was skipped to
avoid concurrent runs and made no PR changes. Idle, completed, archived, or
not-loaded chats are not actively running merely because their titles match;
use the native execution status, not recency or an old automation-memory entry.

If this chat’s identity/title cannot be verified, the native listing fails, or a
known same-title peer’s live execution status cannot be verified, stop and report
the specific concurrency-check failure. A successful listing containing 50 chats,
without pagination or a completeness indicator, is **not** a failure and does not
by itself block the run. Do not request unsupported larger limits or require an
exhaustive chat inventory. When visible and known peers show no active match,
continue; note capped coverage or unavailable hosts briefly in the final report
without claiming that no other run exists globally.
Recheck immediately before first specialist dispatch or queue mutation if that
boundary follows the initial check, using the current title and live statuses.
If a same-title peer has become active, stop new work and settle any already
started work under the workflow's existing stopping rules before the final reply.
Use native inspection only; do not introduce persistent locks, registries, or
custom concurrency scripts. This guard detects observed concurrent chats; native
listing and dispatch are not an atomic lock, and capped visibility may miss
peers outside the returned results.

## Lightweight discovery

Perform initial discovery directly in this coordinator; do not delegate or load agent definitions before candidates remain.

1. Validate parameters first: `count=0` by default (nonnegative integer verified merge limit), `timeout=50` minutes, and `timeout_idle=10` minutes (both finite positive numbers). Reject unknown or invalid parameters before discovery or writes. Record invocation start with the clock tool or `date`; discovery counts toward the deadline.
2. In the same tool-run shell, locate `gh`, check its version/authentication, and verify the intended authenticated account and GitHub host. Resolve the target in order: explicit PR URL or `OWNER/REPO`, an unambiguous repository tied to the current task or approved project context, then the invocation worktree's remote. Honor a clear explicit target even when it differs from the current checkout. Clarify unexplained project/worktree/remote or fork conflicts and multiple plausible remotes; do not invent an upstream default. Never derive the target from the skill's installation/configuration repository, an unrelated or stale task, or the authenticated username. Verify the chosen repository with `gh repo view HOST/OWNER/REPO --json nameWithOwner,defaultBranchRef`. Retain the verified `HOST`, canonical `OWNER/REPO`, host-qualified `HOST/OWNER/REPO`, and returned default-branch metadata. A null default branch can occur in an empty repository; require a nonempty verified `DEFAULT_BRANCH` only if candidates remain below, with no assumed branch fallback. Use `--repo HOST/OWNER/REPO` on every repository-scoped command that supports it; for `gh api`, use `--hostname HOST` and the canonical owner/repository in REST paths or GraphQL variables. Do not change global host configuration. Missing/ambiguous account, host or repository, CLI/auth/network failure, malformed output, or incomplete discovery is an error: stop and report the exact blocker, never classify it as an empty queue. Follow applicable sandbox escalation guidance for a denied harmless check.
3. Discover only that account's open PRs with `gh pr list --repo HOST/OWNER/REPO --author @me --state open --limit 100 --json number,url,isDraft,labels`. Ensure completeness: if the result count reaches the requested limit, increase it and repeat until fewer results are returned, or use complete pagination through `gh api --hostname HOST`. A failed page, unverified truncation, or deadline before completeness is a discovery error, even if the partial result has no candidates. Filter drafts and PRs labeled `noautomerge` locally. Retain only candidate metadata and aggregate discovery/exclusion counts; do not fetch checks, reviews, discussions, diffs, or history yet.
4. If successful complete discovery leaves zero candidates, end immediately with a concise final reply. If no open PRs were found, say: "No open PRs found. No PR changes made." If all open PRs were excluded, say: "No eligible PRs found: all N open PRs are drafts or labeled noautomerge. No PR changes made." Replace N with the actual discovered open-PR count; do not add draft and label counts, which may overlap. This reports only the discovery filter result, not an assessment of merge eligibility. Beyond the required native concurrency check, do not read workflow references, agent definitions, memory, task history, or other queue context, and do not spawn agents, perform writes, or fetch deeper GitHub state on this path.
5. Only when candidates remain, require a nonempty verified `DEFAULT_BRANCH` from the repository metadata; a missing/null default branch is an error on this path, with no fallback to `main` or another assumed branch. Then read [the full queue workflow](references/queue.md) and the six `~/.codex/agents/pr-{green,resolve,update,risk,review,review-high}.toml` definitions once, and follow them. Candidate discovery is not merge eligibility: all review, risk, finding, ownership, dependency, current-head, and GitHub merge gates still apply. Recheck open/non-draft/`noautomerge` status before every write.

An invocation authorizes the workflow's scoped repairs, finding dispositions, risk assessments, and independent COMMENT reviews. `count=0` never authorizes a merge; a positive count also authorizes eligible squash merges up to that verified limit. Never enable auto-merge, bypass protections, deploy, or force-push.
