# Claude task handoff

Use this for Claude-backed roles such as `port-to-claude`; agent descriptions own
routing, and dedicated PR agents retain review and queue repair. Read and follow
[the shared launcher contract](../../scripts/agent-launch.md), [Claude specifics](claude.md), and
[context selection](context.md).

Use the assigned checkout, preserving intentional local work and other writers.
General assignments do not acquire the review-only clean detached checkout,
risk-report, or required Linear rules. Required tools depend on the actual task.

```sh
<config-root>/scripts/agent-launch --role port-to-claude --assignment /private/task.json --checkout /absolute/checkout --output /new/private/bundle --timeout 1800
```

Resolve `<config-root>` through the shared contract. Use the actual assigned role,
rather than changing direction or executor. Generic delegates, including
`delegate-xhigh`, execute natively in Codex and do not use this Claude handoff.
The legacy [claude_delegate.py](scripts/claude_delegate.py) command remains a
provider-neutral forwarding shim, defaulting to native `delegate-xhigh`.
Verify and return the result under the common contract and assignment's acceptance
criteria; the launcher grants no commit, publication, or other external authority.
