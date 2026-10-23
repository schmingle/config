# Claude execution from Codex

Read and follow [the shared launcher contract](../../scripts/agent-launch.md) for
common assignments, permissions, deadlines, lifecycle, and verification. This guide
adds Claude-specific requirements for both [general tasks](delegate-claude.md) and
[prepared PR reviews](pr-review-claude.md); specialized reviews retain their own
entrypoint, evidence, and recovery gates. For prepared reviews, read the common
contract from the bundle’s hashed guidance.md snapshot.

The native Codex agent is an orchestration wrapper. Claude performs the source
work using [the shared execution profile](scripts/claude-review.toml), which owns
model, effort, display name, and tool permissions. Native TOML fields configure the
wrapper. The general adapter loads the native Claude executor body; pass task facts
and constraints rather than copying standing instructions into the assignment.

Carry [standing Claude handoff authorization](../AGENTS.md#claude-handoff-authorization)
into the assignment and any permission justification. Tools and actual runtime
restrictions still apply. Claude's native permission system applies to Claude;
a Codex sandbox argument does not enforce a Claude filesystem boundary.

Before model execution, the helper checks `claude auth status` and writable session
storage in the actual launch environment. Preserve subscription authentication,
configuration directory, and inherited MCP access. If the harmless preflight is
sandbox-blocked, use normal command-level escalation. Missing credentials or tools
return a concrete unblock action rather than a replacement execution path.

Verify the recorded profile, actual model/effort, persisted transcript, and required
connectors inside the executor. A caller's connection is not inherited evidence.
Apply the common result checks and the owning role's additional acceptance gates.
