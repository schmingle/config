# Shared Claude execution handoff

Use this contract whenever a Codex agent proxies assigned work to Claude CLI.
The native agent is an orchestration wrapper; Claude performs the source work.
Agent descriptions own routing. Role-specific handoffs own task coverage,
permissions, evidence, and acceptance criteria:
[general tasks](delegate-claude.md) and [PR reviews](pr-review-claude.md).

[The execution profile](scripts/claude-review.toml) is the shared source of Claude's
model, effort, display name, and tool permissions. Its historical filename remains
compatible with existing review bundles. Native TOML fields configure wrappers.
[The shared runner](scripts/claude_runner.py) owns launch arguments, authentication,
session persistence, deadlines, and process settlement. Role runners select their
own prompts, output schema, task evidence, and acceptance checks. Never silently
substitute another model or effort or perform a native replacement for Claude's work.

## Scope and preparation

Start from a compact, self-contained assignment with known facts, decisions,
approvals, ownership, source references, and expected verification. Follow
[the context policy](context.md). The executor selects applicable guidance and
gathers more evidence when needed. Tools do not expand scope or grant authorization.
Neither wrapper nor executor spawns additional agents.

Preserve the assigned checkout and unrelated work. A role may require a clean,
pinned checkout; general implementation may intentionally begin with local changes.
Record the starting state and verify the final state according to that role.

Keep assignments, raw evidence, logs, transcripts, launch arguments, and reports
outside the checkout and public configuration repository. They may contain private
source material. Do not copy local credentials into bundles.

## Authentication and sessions

Before spending model tokens, verify the installed CLI's authentication and writable
actual session directory under the permissions that will launch it. Preserve normal
subscription authentication, configuration directory, and inherited MCP access.
If sandbox permissions block the check or write probe, request authorized
command-level escalation. Missing credentials or unavailable tools return a concrete
unblock action; do not bypass authentication or switch models.

Use one owned fresh session at a time. Resume or replacement requires the role's
specific recovery procedure, a verified transcript or diagnosed failure, settled
processes, and the original deadline. Never blindly relaunch after partial work.
The shared runner terminates and waits for its process on timeout, interruption,
and errors. After a hard kill or crash, reconcile the recorded process identity
before releasing the checkout or starting another session.

## Verification

Verify actual model identity and requested effort, source evidence, changed files,
checks, permissions, and transcript persistence. A valid structured result or
successful process is not proof of task completion. Role-specific acceptance gates
still apply. Surface gaps and preserve partial work; never present unverified claims
as complete. Attribute source work to the recorded Claude profile, rather than the
native wrapper.
