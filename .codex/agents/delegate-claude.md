# Claude task handoff

Use this for `delegate-high`. Its description owns routing; dedicated PR agents
retain PR review and queue repair work. The Codex wrapper prepares the handoff and
verifies the result; Claude performs the assigned investigation or implementation.
Follow [the shared execution contract](claude.md), applicable repository guidance, and the
user's existing approvals. Neither the wrapper nor Claude delegates further.

[The execution profile](scripts/claude-review.toml) owns Claude's model, effort,
and tool permissions, shared with the escalated reviewer. Native agent fields
configure the wrapper. Do not silently substitute execution settings. The
[task runner](scripts/claude_delegate.py) reuses authentication, transcript
discovery, and owned-process cleanup from the shared execution helper; it does not apply the
review-only clean-checkout, risk-report, or required Linear rules.

## Prepare and run

Verify the assigned working directory and, when it is a Git checkout, its current
branch, HEAD, and local changes.
Use that checkout, including any intentionally uncommitted work; preserve others'
changes. Do not create a detached review checkout for implementation work.

Save a JSON assignment outside the checkout and public configuration repository:

- `objective`, `scope`, and `expected_result`: nonempty strings.
- `owned_paths`: an array of files or modules Claude may edit; use an empty array
  for analysis-only tasks.
- `constraints`, `approvals`, `sources`, and `verification`: string arrays.
  Include the prior medium attempt's findings and remaining question in sources.
  Record actual approvals and prohibitions without inventing authorization.
- Optional `finish_by`: an ISO 8601 absolute deadline with timezone.

Supply complete relevant facts, decisions, source references, and required checks.
The assignment is a starting point; Claude must select applicable instructions and
gather further evidence when needed. Missing decisions that materially affect scope,
correctness, or authorization return to the coordinator.

```sh
python3 ~/.codex/agents/scripts/claude_delegate.py --assignment /absolute/task.json --checkout /absolute/checkout --output /new/private/bundle --timeout 1800
```

Output must be new and outside the checkout and public configuration repository:
assignment copies, logs, and reports may contain private source material.
The timeout bounds this one fresh session; `--finish-by` may shorten it.
Do not relaunch blindly after partial edits or an incomplete result.

The runner verifies authenticated `claude auth status` and writable real session
storage before spending model tokens. Preserve the normal login, configuration,
and inherited MCP access. Request authorized command-level escalation if sandbox
permissions block authentication or persistence. Do not copy credentials or bypass
authentication. Task-specific connected tools are required only when the task
needs them; verify the intended account before accessing data.

Claude may edit owned files and run applicable checks when authorized by the
assignment. Trusted shell/file permissions do not expand scope or authorize merging,
auto-merge, deployment, production mutation, or external communication. Preserve
protected behavior and approval gates. Commit or publication permissions must come
from the actual task; the runner does not grant them.

## Verify and return

The runner saves the exact assignment and execution profile, initial/final Git
state, launch arguments, process identity, events, structured report, and metrics.
It settles its owned process on timeout, interruption, and errors. After a hard
kill or crash, reconcile the recorded process before releasing the checkout or
starting another session.

A successful transport or claimed completion is not verified task completion.
Inspect the actual diff, source evidence, checks, model identity, requested effort,
permission denials, and persisted transcript. Preserve and disclose partial work
when any check fails. Return the outcome, file/PR links, verification evidence,
remaining risks or decisions, and concrete unblock actions. Attribute the source
work to the recorded Claude execution profile, rather than the native wrapper.
