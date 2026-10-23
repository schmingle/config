# Claude task handoff

Use this for `delegate-xhigh`; agent descriptions own routing, and dedicated PR
agents retain review and queue repair. Read and follow [the shared launcher
contract](../../scripts/agent-launch.md), [Claude specifics](claude.md), and
[context selection](context.md).

Use the assigned checkout, preserving intentional local work and other writers.
General assignments do not acquire the review-only clean detached checkout,
risk-report, or required Linear rules. Required tools depend on the actual task.

```sh
<config-root>/scripts/agent-launch --role delegate-xhigh --assignment /private/task.json --checkout /absolute/checkout --output /new/private/bundle --timeout 1800
```

Resolve `<config-root>` through the shared contract. Use the actual assigned role,
such as `port-to-claude`, rather than changing direction or executor. The legacy
[claude_delegate.py](scripts/claude_delegate.py) command remains a forwarding shim.
Verify and return the result under the common contract and assignment's acceptance
criteria; the launcher grants no commit, publication, or other external authority.
