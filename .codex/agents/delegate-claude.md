# Claude task handoff

Use this for `delegate-high`. Its description owns routing; dedicated PR agents
retain PR review and queue repair work. The Codex wrapper prepares the handoff and
verifies the result; Claude performs the assigned investigation or implementation.
Read [the shared execution contract](claude.md) for profile ownership, authentication,
sessions, privacy, process settlement, and verification. Apply repository guidance
and the user's existing approvals.

The [task runner](scripts/claude_delegate.py) does not apply the review-only
clean-checkout, risk-report, or required Linear rules.

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
  When a prior attempt exists, include its useful findings and remaining question
  in sources; a prior attempt is not required.
  Record actual approvals and prohibitions without inventing authorization.
- Optional `finish_by`: an ISO 8601 absolute deadline with timezone.

```sh
python3 ~/.codex/agents/scripts/claude_delegate.py --assignment /absolute/task.json --checkout /absolute/checkout --output /new/private/bundle --timeout 1800
```

Output must be new and satisfy the shared contract's privacy boundary.
The timeout bounds this one fresh session; `--finish-by` may shorten it.
Do not relaunch blindly after partial edits or an incomplete result.

Task-specific connected tools are required only when the task needs them; verify
the intended account before accessing data.

Claude may edit owned files and run applicable checks when authorized by the
assignment. Trusted shell/file permissions do not expand scope or authorize merging,
auto-merge, deployment, production mutation, or external communication. Preserve
protected behavior and approval gates. Commit or publication permissions must come
from the actual task; the runner does not grant them.

## Verify and return

The runner saves the assignment, profile, initial/final Git state, launch arguments,
process identity, events, report, and metrics. Apply the shared verification gates
to the actual diff, source evidence, and checks. Preserve and disclose partial work
when a gate fails. Return the outcome, file/PR links, verification evidence,
remaining risks or decisions, and concrete unblock actions.
