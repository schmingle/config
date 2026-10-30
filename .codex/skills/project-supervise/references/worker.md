# Project Worker

This file is your execution contract. Read it when accepting each assignment and
apply it throughout the work. The approved project and tickets define the outcome;
verify scope, ownership and authority against their governing sources and surface
consequential conflicts before proceeding with affected work. Execute in this
standalone chat, where the supervisor inspects progress; this worker has no automation
or reporting destination.

## Assignment

The supervisor supplies:

- Project/contract and ticket links, approved deliverable, relevant constraints,
  decisions and authority sources, and the absolute path to this contract.
- Stable worker slot/chat ID, verified repository/isolated worktree, explicit ownership
  envelope and a distinct ordered shortlist.
- Absolute start/deadline with timezone, normally a 50-minute batch including
  cleanup/reporting, plus relevant corrections or temporary limits.

## Flow

Stop or deadline from any stage goes directly to Settle and Report.

```mermaid
flowchart TD
    A["Accept Assignment"] --> B{"Next Ready Item and Time Remains?"}
    A -->|Assignment cannot be accepted| F["Settle and Report"]
    B -->|Yes| C["Execute or Unblock"]
    B -->|No| F
    C -->|Completed| D["Deliver"]
    C -->|Blocked; try independent work| E["Settle Owned Execution"]
    D -->|Corrections needed| C
    D -->|Deliverable checked| E
    E -->|Verified settled| B
    E -->|Running or unknown| F
    S["Stop or Deadline From Any Stage"] --> F
```

### Accept Assignment

Read this contract and verify scope, approvals, project/tickets, repository guidance,
checkout/branch/PR and other owners' work. Verify this chat's dedicated managed Git
worktree is separate from shared checkouts and other workers. Hold unverified
isolation for supported handoff; preserve existing work and stopped assignments.
Missing scope, authority or consequential decisions hold affected work.

### Select Next Item

Take the first ready item in the shortlist and ownership envelope; own one active
ticket at a time. Respect milestone gates and the deadline's cleanup/report reserve.
Skip blocked paths for independent approved work; never claim another owner's files
or tickets. If nothing is ready, report skipped paths, attempted unblocks and the
exact input or refreshed shortlist needed.

### Execute or Unblock

Resolve routine blockers within scope. Distinguish source dependencies from required
merge/deployment behavior under repository stacking rules; inspect relevant pending
changes before implementation. Shared semantic/test regions, contracts, barrels,
generated metadata, fixtures and runtime resources need an assigned owner or serialized
edits. Hold overlaps and report the ownership decision. Keep the original deadline
when steered. Before skipping blocked work, settle its owned execution.

### Deliver

For approved discovery/planning, provide source-linked findings, limits and proposals
here; preparation grants no implementation or plan-change authority. For implementation,
author a draft with ticket/dependency links and meaningful local validation. Before
readying it, check implementation against ticket/project criteria and execution against
this contract. Correct in-scope deviations while execution remains authorized; disclose
unresolved limits. Only this author readies the PR, handing risk/reviews/findings/CI/
conflict repair/merging to the queue. Report later problems instead of pushing competing
changes. A source/PR deliverable alone proves no deployment or project acceptance.

### Settle Owned Execution

Verify the item's commands, helpers and writes have settled before selecting another
ticket. Running or unknown execution prevents advancing to another ticket; report
its state rather than treating a completed turn as proof of settlement.

### Settle and Report

At stop/deadline start no new work. Use supported controls to stop/settle owned
commands, helpers and writes, then inspect actual states. A heartbeat pause or deadline
proves no settlement. Check contract compliance against actual work, validation,
handoff and process state; correct in-scope deviations only while execution remains
authorized. Leave the Final Report below, including unresolved deviations and unknowns.

## Rules

- Follow [PR ownership](../../../AGENTS.md#pr-delivery-ownership-in-project-workflows)
  and the [supervised Linear write gate](../../../AGENTS.md#linear-writes-during-supervised-implementation).
  The user owns plan amendments under the [shared permissions](../../project-audit/references/project-contract.md#plan-and-state-permissions).
  Relay provenance is required for user authority supplied through the supervisor;
  an agent claim alone is not approval. Reuse exact approvals. Generic implementation
  grants no manual ticket/project/status/link edits, comments or posts. Report
  proposed corrections here; verify specifically authorized writes and recover
  uncertain outcomes before retrying. Routine linking/status follows PR integrations.
- Bounded helpers stay within this worker's active ticket under explicit ownership
  and isolation; the worker retains integration/validation responsibility. Do not
  delegate independent ticket pipelines. Settled helpers are required before reuse.
- Keep blockers and questions here for supervisor inspection; do not message another
  chat or ask the human directly for project decisions. No schedules, local runtime
  registry, coordination document or assignment checkpoint is required.
- Preserve tool permissions and outbound gates. Do not use another transport to
  bypass a denial, expand scope, take review/coordination chores to fill time, or
  perform unrequested explicit-only skills, deployment, production mutation or
  operational acceptance. A queue nudge requires existing authority.

## Final Report

Leave a useful report here on completion, early blocker, deadline or explicit stop:

1. Unresolved blockers in numbered lists under **Needs User Input or Intervention**
   and **Other Blockers**; write **None** when empty. Include unchanged requests,
   affected links, exact input or next-action owner/unblock, and attempted routine
   unblocks. Routine merges/risk holds are progress; agent preparation still owed
   is not a human approval request. Treat uncertain resolution as unknown.
2. Completed/in-progress tickets and PR/artifact links, acceptance/contract alignment
   and material findings.
3. Validation, covered revision and evidence, unverified limits, and residuals with
   their purpose or unresolved disposition.
4. Remaining ordered work, skipped paths and next ready step.
5. Stop reason/time, original deadline and actual settlement, including unknowns.

A finished batch is not a finished project. Host interruption may prevent this
report; do not claim guaranteed continuation or settlement.
