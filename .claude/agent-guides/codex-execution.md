# Codex role execution from Claude

Read and follow [the shared launcher contract](../../scripts/agent-launch.md) and
[context selection](context.md). That contract owns assignment fields, capabilities,
permissions, deadlines, lifecycle, and verification. This guide adds Codex specifics.

The native Claude agent is a wrapper. The launcher reads canonical Codex TOML
model/effort and instructions; the Codex executor keeps its Codex guide paths.
Native Claude roles execute directly instead of launching another copy. Keep both
provider folders installed. `AGENT_LAUNCH_ROOT` selects the complete configuration
checkout; `CODEX_HOME` selects the CLI environment, not the role-definition source.

For review, use a clean detached checkout pinned to the assigned head with actual
base and ancestry. Supply the full risk report, factual PR evidence, publication
permissions, and accepted coverage without writer/coordinator conclusions. Follow
the canonical [review contract](../../.codex/agents/pr-review.md); the generic
launcher does not replace the specialized high-review workflow.

```sh
<config-root>/scripts/agent-launch --role <assigned-role> --assignment <private-task.json> --checkout <absolute-checkout> --output <new-private-output> --finish-by <absolute-ISO-deadline> --sandbox <read-only-or-workspace-write>
```

Resolve `<config-root>` using the shared contract. The legacy
[codex-delegate.sh](../bin/codex-delegate.sh) command still forwards to that launcher;
`--brief-file` remains read-only compatibility input.

The adapter checks the installed CLI and `codex login status`. `CODEX_BIN` may select
an executable. Missing installation, authentication, managed restrictions, or denied
approval returns the concrete blocker; normal authorized escalation remains available.
Codex role capabilities and separate filesystem/network/external-action requirements
are owned by the shared contract and table, not this wrapper’s frontmatter.

Read the unchanged assignment, recorded executor identity and argv, process status,
report, events, and final Git state. For review/risk, use verified executor attribution;
Haiku frontmatter identifies only the wrapper. Required live Linear access must
succeed in the actual Codex environment; the wrapper's connection is insufficient.
Verify publications and return the actual result under the shared contract.
