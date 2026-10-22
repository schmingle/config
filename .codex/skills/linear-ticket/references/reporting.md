# Run report and outstanding inventory

Every manual or scheduled invocation ends with a user-facing final report,
including unchanged runs, errors, and interrupted execution when a response is
possible. Commentary and private state are not substitutes. Report verified
results, not intended actions. Reporting never authorizes extra execution,
external comments, messages, automation changes, merging, or deployment.

## Inventory scope and reconciliation

Keep a cross-run inventory of tickets this workflow has taken responsibility for
or left with an unresolved disposition: claimed/prepared/built work, questions,
ownership or approval holds, blocked/interrupted work, oversized or project-shaped
work awaiting a next owner or decision, and decomposition parents and children.
Include this run's screened tickets with an unresolved next step even if no
mutation occurred. Unrelated metadata candidates and conclusively excluded
self-created or other-owned tickets are not a permanent watchlist. A previously
tracked ticket does not disappear merely because it changes assignee, status,
estimate, creator eligibility, or falls outside this run's screening budget.

Reconcile the union of this run's dispositions and prior tracked IDs with live
Linear metadata and owning PR states. Discover prior workflow work from native
issue/PR links and workflow comments or disposition history in the configured
team; assignment and status alone do not establish provenance. Reuse prior run
reports, authorized automation history, and private checkpoints as discovery
hints, never proof of current status. Recover outstanding records on a missing
cache rather than treating the current candidate page as the whole inventory.
Check linked decomposition relatives so a parent or child cannot silently vanish.
With an intact inventory, reuse established provenance references and batch live
metadata/PR-state reads; do not reread every tracked conversation each run. Use
targeted historical recovery when provenance or membership is missing. If that
recovery is incomplete, report partial coverage instead of widening execution.

Use the existing private per-issue checkpoint for minimal durable inventory
hints: issue ID, source references establishing inclusion, last disposition and
next owner/action, last verified status/time, terminal transition reference/time,
and an explicit handoff/release reference when applicable. Preserve the shared
checkpoint's privacy, permissions, and other pass state. Record a newly tracked
unresolved disposition before finishing a writable run. No copied conversations,
public workflow ledgers, or Linear comments solely to maintain this inventory.
In read-only mode, reconstruct/report without checkpoint writes.

Read-only inventory metadata and PR-state reconciliation may cover more than 10
tickets. They do not grant additional full issue/comment/code assessment,
mutations, or builds: those remain subject to the existing execution limits.
Read only the targeted history needed to establish provenance or a terminal
transition. If a deeper reassessment cannot fit this run, show the ticket with its
last known disposition and next assessment needed; do not imply its holds were
revalidated. Paginate inventory discovery independently of candidate screening.

Never claim complete coverage if a source, page, or prior inventory cannot be
reconciled. Show all known rows, label stale/unverified facts and the coverage gap,
and state how to recover it. Missing access, a deleted record, or a missing cache
is not verified closure. Do not drop unresolved records to make the report clean.

## Closure and handoff retention

Keep every unresolved tracked ticket in **Still in play**, including unchanged
holds, Draft PRs, ready PRs awaiting the queue, and merged PRs whose tickets remain
open. Identify the actual next owner; assignment alone is not delivery ownership.
An explicit handoff transfers execution to the destination owner but keeps the
open ticket in Still in play with that owner and next action. Only a verified
explicit release from this workflow’s tracking, distinct from reassignment or
handoff alone, removes an open ticket: show the release once under work completed
with evidence, then omit it from future outstanding rows. An unanswered ownership
question is not a completed handoff.

Show tickets with verified native terminal status in **Closed in the last 24
hours** until 24 elapsed hours after the actual terminal transition. Use the
server transition timestamp, not general `updatedAt`, PR merge time, or the time
this run first noticed it. If the transition time cannot be recovered, label it
unknown and retain the row under **Closed, time unverified**, separate from the
verified 24-hour section, until the transition can be established. A reopened ticket returns immediately
to Still in play. After the retention window, omit the closed row from reports;
this does not authorize deleting Linear records or checkpoint evidence needed
for idempotency. Distinguish ticket closure, PR merge, deployment, and acceptance.

## Final format

Use the merge queue's summary, intervention, results, and remaining-work shape,
with ticket-level accounting:

1. **Summary:** Local start/end and elapsed time when measured, timezone,
   screened/mutated counts, build outcome (at most one ticket), open inventory and
   verified recent-closure counts, and stop reason. Count closures with unknown
   timing separately. Identify incomplete coverage here.
2. **Needs your intervention:** Only actual user decisions, authorization, or
   access barriers. Link each ticket, state what is known, the exact action needed,
   and what would allow progress. Ordinary queue waits and unserved work are not
   automatically requests for user intervention. Omit when none.
3. **Work completed this run:** Concise linked dispositions, estimate changes,
   decomposition, implementation, meaningful validation, and Draft/ready handoffs.
   Separate this run's actions from outcomes observed from the merge queue or
   other people. Say explicitly when no changes were made. Never call a proposed
   read-only action completed.
4. **Still in play:** One row per unresolved tracked ticket, intervention first,
   then actionable work, then waits. Use columns
   `Ticket | Status / estimate | This run | PRs | Next owner / blocker / action`.
   Link ticket IDs and all owning PRs; show Draft/ready/merged state. Include
   unchanged tickets and tickets not screened this run. Give concrete next steps
   and useful question/review deadlines. Preserve distinct parent/child rows and
   relationships. Use `unknown` for missing evidence and `—` only for verified none.
5. **Closed in the last 24 hours:** Linked ticket, terminal outcome and time,
   owning PRs, and any material delivery limitation. Do not duplicate these rows
   in Still in play. Omit the section when empty.

Reconcile inventory counts with the tables; intervention callouts supplement,
not replace, their rows. Summarize unrelated discovery exclusions by reason
instead of listing an entire team backlog. A complete, empty inventory with no
action needs only a concise summary explicitly stating that fact. When relevant,
close with unfinished worker/unpublished work or validation gaps and the next
invocation needed; do not promise a scheduled follow-up. Keep the own-chat report
readable without applying the external Linear comment word cap to its inventory.
