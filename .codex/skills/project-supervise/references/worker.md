# Project Worker

Execute the assigned approved work in this standalone chat. The supervisor inspects
progress here; this worker has no automation or reporting destination.

## Assignment

The supervisor supplies:

- Project/contract and ticket links, approved deliverable, relevant constraints,
  decisions and authority sources, and the path to this protocol.
- Stable worker slot/chat ID, verified repository/isolated worktree, explicit ownership
  envelope and a distinct ordered shortlist.
- Absolute start/deadline with timezone, normally a 50-minute batch including
  cleanup/reporting, plus relevant corrections or temporary limits.

## Flow

1. **Accept Assignment.** Verify scope, approvals, contract, tickets, applicable
   repository guidance, current checkout/branch/PR and other owners' work. Before
   repository work, verify this chat's dedicated managed Git worktree is separate
   from the base/shared checkout and other workers. Hold unverified isolation for
   supported handoff; preserve work and explicitly stopped assignments. Missing
   scope, authority or consequential decisions hold affected work, not independent
   approved work.
2. **Execute.** Take the first ready item inside the shortlist and ownership envelope;
   own one active ticket at a time. Continue through ready items until the deadline's
   cleanup/report reserve. Respect milestone approval gates. Diagnose and resolve
   routine blockers, bypass blocked paths for independent work, and distinguish
   source dependencies from merge/deployment dependencies under repository stacking
   rules. Inspect relevant pending changes before implementation. Shared contracts,
   semantic/test regions, barrels, generated metadata, mocks, fixtures and runtime
   resources require the assigned owner or serialized edits. Hold overlaps and report
   the needed ownership decision rather than claiming another worker's files/tickets.
3. **Deliver.** For approved discovery/planning, provide source-linked findings,
   limits and concrete proposals here; preparation does not authorize implementation
   or plan/ticket changes. For implementation, create a draft PR with ticket/dependency
   links, implement and run meaningful local validation, then check against ticket
   criteria and the project contract. Fix in-scope drift in the draft and disclose
   material limits. Only this author marks it ready; that hands ownership to the
   existing queue for risk, review, findings, CI/conflict repair and merging. Report
   subsequent problems rather than pushing competing changes. Continue other ready
   work; source/PR delivery alone is not deployment, acceptance or project completion.
4. **Settle and Report.** Before advancing to another ticket, settle owned execution
   and helpers from the prior assignment. At deadline or explicit stop, start no
   new work; use supported controls to stop/settle commands, helpers and writes and
   inspect their states. A deadline, completed turn or heartbeat pause proves no
   settlement. Report running/unknown work so later batches cannot overlap. On early
   exhaustion, identify blocked/skipped paths, attempted unblocks and the next ready
   step or exact input/refreshed shortlist needed. Keep the original deadline when steered.

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
