# Public configuration repository

This repository and its Git history are public. These rules apply to every file,
commit, generated artifact, and contribution, including work by delegated agents.

## Workflow

For this personal repository, work directly on `main` and commit verified changes.
If work is already on a task branch, merge it into `main` after verification.
Use a separate task branch or pull request only when explicitly requested.

## Agent definitions

Use each agent's `description` as the routing decision layer: explain when to choose
it and meaningful boundaries with other agents. Keep native model and effort values
only in `model` and `model_reasoning_effort`, not descriptions or instruction prose.
Claude delegates may reference their canonical execution profile from
`developer_instructions` because the native fields configure the wrapper.
Derive reviewer signoffs from the execution settings instead of duplicating values.

Follow the shared [context-selection policy](.codex/agents/context.md). Give agents a
small, sufficient starting brief with known decisions and approvals; let them select
applicable instructions and gather more evidence without waiting for the coordinator
to supply everything. Required guidance and role-specific coverage still apply.

## Port Codex changes to Claude

After completing a batch of changes under `.codex/`, call
[port-to-claude](.codex/agents/port-to-claude.toml) before final delivery or
committing. Supply the config repository root; Claude inspects the current
folders and determines whether any porting changes are needed. The agent may
also be called independently. No diff is required, and Codex must not pre-exclude
files or prepare a separate diff bundle.

Have Claude assess the current Codex configuration as a whole and recommend
the coherent collection of Claude changes needed to preserve its intended
behavior. Every public custom Codex agent and skill needs a Claude counterpart;
Codex-managed `.system` skills and provider-only runtime internals are excluded.
Match actual execution settings: Luna/Sol roles call Codex CLI with their source
model and effort, while Claude-backed roles use the shared Claude profile directly.
Preserve provider-specific permissions and tools, and distinguish wrappers from
executors. This remains one-way Codex-to-Claude adaptation. Its source inspection and
any diff inspection must be scoped to `.codex/`; it may read relevant existing Claude
files as target context, but must not inspect diffs outside `.codex/`.

Review and apply recommendations within the authorized scope; surface unresolved
questions. If no Claude changes are needed, report why. Run once per completed
batch, not per file; reassess later Codex changes, but applying Claude-only
recommendations does not trigger another port. Porting does not authorize staging
or committing, and explicit user instructions to defer either still apply.

## What belongs here

Track reusable development configuration, agent definitions, skills, scripts, and
instructions. Development preferences and public technical references are allowed
when relevant. Include only information necessary to explain or use the
configuration.

Development relevance alone does not make information safe to publish. Company,
customer, and third-party confidential information must remain outside this repo.
This includes proprietary business rules, internal architecture, schemas, and
documentation, whether copied, paraphrased, summarized, or reconstructed from
private sources. A generic request to edit, improve, or commit configuration does
not authorize publishing private material. Publication requires explicit
authorization for the specific material and public destination.

## Never include

- Credentials or authentication material: passwords, API keys, tokens, cookies,
  private keys, recovery codes, credential-bearing URLs, or secret environment values.
- Personal information unrelated to development: private correspondence, personal
  contact details, family information, financial records, health information,
  travel details, or calendar contents.
- Private source material: chat/session transcripts, memories, writing samples,
  meeting notes, customer data, internal tickets, private document contents, or
  proprietary code and operational details without explicit authorization to publish.
- Local runtime state: authentication stores, session databases, logs, caches,
  benchmark evidence bundles, backups, or generated exports containing private data.

Do not copy entire configuration directories or follow symlinks into private files.
Select and inspect individual files. A referenced private file is not permission to
copy its contents into this repository.

## Make configuration portable

Keep reusable skills and agent definitions repository-agnostic unless an explicit
policy names a repository. Resolve repository targets from the invocation context,
not the definition's installation or configuration-repository location: use an
explicit PR URL or `OWNER/REPO`, then an unambiguous current chat or project
repository, then the invocation worktree's remote. Honor a clear explicit target;
clarify unexplained conflicts or ambiguous remotes rather than inventing an upstream
default. For GitHub actions, verify the host and canonical repository, pass that
target to delegated agents, and scope commands explicitly. Never infer a
target from an authenticated username or unrelated chat history. Preserve explicit
repository policies and non-GitHub workflows; do not add repository discovery when
the task needs no repository action.

Use environment variables, home-relative paths, and clearly labeled placeholders
instead of personal absolute paths, real account identifiers, or private service
addresses. Reference secrets by environment-variable name; never supply real values.
Keep local overrides and sensitive source material outside the repository, with
appropriate ignore rules for any local-only files. Ignoring a file does not protect
it if it is already tracked.

The explicit local-only exception is `.codex/AGENTS-PRIVATE.md`, which holds private
preferences, identifying details, and account context. Keep it gitignored and
untracked; never force-add it, copy its contents into tracked files, or include it
in public artifacts. Its installed path is `~/.codex/AGENTS-PRIVATE.md`, symlinked to the ignored file.
`.claude/CLAUDE-PRIVATE.md` is the same kind of local-only file for Claude Code (installed as
`~/.claude/CLAUDE-PRIVATE.md`): keep it ignored and untracked under the same rules.

## Before staging, committing, or pushing

The local privacy gate is mandatory for every change, including Markdown-only
edits. Install the [versioned hooks](README.md#validate-changes), scan the exact
staged index before committing, and scan every outgoing commit before pushing.
Run the [validation commands](README.md#validate-changes) as applicable. Checks
must fail closed when a required dependency or scan cannot run; fix the blocker
before committing or pushing. CI runs after publication and cannot replace these
local checks. Do not bypass hooks with `--no-verify`, override `core.hooksPath`, or
otherwise disable a safeguard without explicit user authorization for that
specific bypass and reason.

1. Inspect the exact files and complete diff, including new, hidden, generated,
   and binary files. Review staged content again before committing. Do not use
   blanket staging to import unreviewed files.
2. Check for credentials, personal information, private references, and sensitive
   information in comments, examples, filenames, and metadata. Use a secret scanner
   when available; a clean scan does not replace content review.
3. Verify that only the intended, reviewed files are included. When pushing existing
   local commits, inspect all outgoing commits, not only the final tree: deleting a
   secret in a later commit does not remove it from public history.
4. If information may be sensitive, omit or sanitize it. Ask the owner only when
   its inclusion is necessary and publication authority is unclear. Never print
   suspected secret values in reports or tool output; identify the file and location.

If a secret or private information is discovered in tracked content or history,
stop the affected commit/push and notify the owner with its location, without
repeating the value. If already published, flag the exposure immediately and
recommend credential revocation/rotation where applicable. Coordinate history
cleanup with the owner; do not rewrite shared history unilaterally.

## Validate changes

Follow the [validation commands](README.md#validate-changes) for agent and skill
changes. The checks run locally and in CI without invoking a paid model or connected
service. They supplement the privacy and full-diff review above.
