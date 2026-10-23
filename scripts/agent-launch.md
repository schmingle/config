# Shared agent launcher

Use [agent-launch](agent-launch) from either Codex or Claude to execute one scoped
role. The caller does not select a direction or replace execution settings. Native
Codex roles read their model, effort, and instructions from the canonical Codex
agent TOML; Claude-backed roles use the shared Claude profile. Wrapper settings are
not executor identity. Configuration adaptation remains one-way Codex to Claude.

## Assignment and execution

Save a private JSON assignment outside the checkout and configuration repository:

- `objective`, `scope`, and `expected_result`: nonempty strings.
- `owned_paths`: string array of files/modules the task may edit; empty for analysis.
- `constraints`, `approvals`, `sources`, and `verification`: string arrays. Carry
  actual approvals and prohibitions, useful evidence, and the expected checks.
- `finish_by`: optional absolute ISO 8601 deadline with timezone. A CLI deadline may
  shorten it, never extend it. Preserve the original deadline on follow-up work.

Provide a compact factual brief. Let the executor gather authorized relevant
context; do not send credentials or unrelated private material. The same assignment
format works with both providers:

```sh
/absolute/config/scripts/agent-launch --role delegate-low --assignment /private/task.json --checkout /absolute/checkout --output /new/private/bundle --finish-by 2030-01-01T12:00:00Z
```

Replace paths and deadline with the real inputs. Locate this launcher by resolving
the installed provider paths back to the configuration checkout. For copied provider
folders, set `AGENT_LAUNCH_ROOT` to the checkout containing this shared launcher.
Keep the canonical provider definitions and shared helpers available there.

The canonical [role capability table](agent_launcher.py) selects filesystem defaults,
required network reads, and approval settings separately. `requires_network_reads`
describes a role requirement; `false` does not prohibit optional, task-authorized
network research by generic delegates.

- `pr-review` and `pr-green` default to a `read-only` filesystem. Their external action
  ceilings are a GitHub COMMENT review and a justified CI rerun, respectively,
  when the assignment explicitly authorizes that action and the role workflow's
  gates pass.
- `pr-resolve` and `pr-update` default to `workspace-write` and require nonempty
  `owned_paths`. Generic delegates and `writer` default to `read-only`; select
  `--sandbox workspace-write` for explicitly assigned edits with owned paths.
- `pr-risk`, `port-to-claude`, and the generic `pr-review-high` launch are analysis
  only. They reject writable filesystem requests and permit no external writes.
  `pr-risk` requires live evidence and can request approval for scoped network
  reads. The specialized high-review workflow owns its publication path.

Native roles that require network reads, can edit, or can perform a scoped external action use
`approval_policy="on-request"` with `approvals_reviewer="auto_review"`. This allows
normal review of network or external-action escalation requests. An offline native
analysis role with no write capabilities can keep `approval_policy="never"`.
The launcher uses the separate
[documented configuration settings](https://learn.chatgpt.com/docs/config-file/config-reference),
with strict config validation; it does not use `--approve-for-me`, which also
selects a writable sandbox. An unsupported setting, managed restriction, denied
approval, or unavailable reviewer remains a blocker.

Capabilities are ceilings, not authorization. The unchanged assignment approvals
and constraints still decide which actions may be attempted. The default sandbox
applies to ordinary commands. An approved `require_escalated` command runs outside
that sandbox, so a read-only default is not a hard filesystem guarantee for an
escalated command. Source boundaries rely on the default sandbox for ordinary
commands, role instructions, and approval review of each escalation. A scoped
network-read approval grants no authority to edit source or perform external writes.
Escalation does not expand assigned source ownership or the role's action ceiling.
Claude's own permission and tool
mechanics still apply; do not assume a Codex filesystem sandbox applies to Claude.
The launcher never creates worktrees, commits, pushes, or publishes on its own.

Verify the assigned checkout, repository, branch, HEAD, and local changes. Preserve
intentional dirty work and other writers. Prepare a fresh pinned review checkout
when the role requires it. Keep output private and fresh; never reuse a bundle to
hide a previous attempt or blindly retry after partial work. `--dry-run` prepares
settings without invoking a model. `--timeout` and `--max-turns` bound execution
where supported; the absolute deadline remains authoritative.

## Verification and boundaries

Run in the foreground and wait through bounded tool calls, keeping the coordinator
informed. The launcher checks provider availability/authentication, records actual
execution settings, role capability ceilings, selected sandbox, and launch arguments,
and settles owned processes. Provider
adapters handle their own CLI arguments, authentication, and output formats.
Recursive launcher calls are rejected; executors perform their assigned work
directly instead of handing it back to the other provider.

Read the report, execution record, logs, and final checkout state. Verify material
claims against source, checks, and any published artifacts. Exit success and valid
output are not proof of task completion. Preserve partial work and disclose gaps,
denials, unsettled processes, and actual unblock actions. Required connectors must
be verified inside the actual executor; a connection in the caller is insufficient.
Attribute source work to recorded executor settings rather than wrapper frontmatter.

The existing Codex/Claude handoff commands remain compatibility entry points. Legacy `--brief-file` input is read-only; writable tasks require the structured JSON assignment with explicit owned paths. The
specialized [Claude PR review workflow](../.codex/agents/pr-review-claude.md) retains
its evidence, publication, and recovery contract and shares process-settlement code;
a generic role launch does not replace those checks or grant publication.
