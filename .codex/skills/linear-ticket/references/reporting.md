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
self-created or other-owned tickets are not a permanent watchlist. Report tickets
determined to belong to someone else in the final ownership list below, rather
than the main table. A previously tracked ticket does not disappear merely
because it changes assignee, status,
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

Keep every unresolved tracked ticket visible in **Still in play** or the final
**Owned by others** list, as appropriate, including unchanged
holds, Draft PRs, ready PRs awaiting the queue, and merged PRs whose tickets remain
open. Identify the actual next owner; assignment alone is not delivery ownership.
An explicit handoff transfers execution to the destination owner but keeps the
open ticket visible in Owned by others with that owner. Only a verified
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
4. **Still in play:** One row per unresolved tracked ticket that remains for the
   current user or has unresolved ownership. Sort report-table rows by Action
   alphabetically, except `Skipped` always sorts last; within each action, sort
   by the team’s native workflow status order, then oldest issue `createdAt` first.
   Unknown creation times sort last within their action/status group; use ticket
   ID to break ties. Fetch creation metadata as needed for reporting; do not use
   `updatedAt` as ticket age. This changes presentation only, not triage or build
   selection order. Keep intervention callouts in their separate section.
   Use exactly these columns, in this order:
   `Ticket | Status | Estimate | PRs | Action | Update/notes`.
   Link ticket IDs and all owning PRs; show Draft/ready/merged state in PRs. Include
   unchanged tickets and tickets not screened this run. Action describes what
   this invocation actually did, using concise labels such as `Skipped`,
   `Assessed`, `Triaged`, `Split`, `PR started`, `PR updated`, or `Marked ready`.
   Use `Not assessed` for inventory-only rows; explain skips and deferrals in
   Update/notes. Read-only assessment is not completed triage, a proposed split
   is not `Split`, and an observed merge by someone else is not this run’s action.
   Put concrete changes, blockers, next owner/action, useful deadlines, and parent/child relationships
   in Update/notes. Use `unknown` for missing evidence and `—` only for verified none.
   Tickets determined to belong to someone else appear in the final ownership
   list instead of duplicating them in this table. Uncertain ownership stays here
   with the uncertainty explained; never invent an owner.
5. **Closed in the last 24 hours:** Linked ticket, terminal outcome and time,
   owning PRs, and any material delivery limitation. Do not duplicate these rows
   in Still in play or Owned by others. If presented as a table, use the same six
   columns and sorting, with closure time and delivery limitations in Update/notes. Omit the
   section when empty.
6. **Owned by others:** End the inventory with a bullet list, one linked ticket per
   item, using exactly `<ticket> - owned by <owner>`. Include tickets excluded this
   run because verified assignment, directed responsibility, or active ownership
   places them with someone else, plus previously tracked open tickets with a
   verified other owner. Retain those tracked tickets across runs until closure
   or explicit release from tracking; newly excluded unrelated tickets need not
   become a permanent watchlist. Use the verified owner’s readable name, linking
   it when a source URL is known. Self-created exclusion alone is not evidence of
   another owner. Omit the section when empty; put any inventory caveats before it. The focused interview follows the report.

Reconcile inventory counts with the tables and tracked entries in the final list;
intervention callouts supplement, not replace, those entries. Summarize unrelated discovery exclusions by reason
instead of listing an entire team backlog. A complete, empty inventory with no
action needs only a concise summary explicitly stating that fact, plus the final
ownership list if this run excluded tickets belonging to others. When relevant,
close with unfinished worker/unpublished work or validation gaps and the next
invocation needed; do not promise a scheduled follow-up. Keep the own-chat report
readable without applying the external Linear comment word cap to its inventory.

## Concise output

Lead with one outcome sentence and compact counts; include timing once when useful.
Keep completed work to at most three short bullets and table notes to one short
sentence per ticket. Do not repeat table details in intervention or results prose.
Omit empty sections and routine tool, identity, policy, and checkpoint narration.
Preserve every required inventory row, ownership entry, important link, material
blocker, and coverage limitation; shorten prose rather than omit work. Put stale
relevance dispositions and the next action in Update/notes; Action remains what
this run actually did (for example, Assessed or Asked), not a proposed closure.

## Focused interview

After the report, begin a grill-me session when user input can materially unblock
or clarify eligible work, including a proposed stale-ticket closure. Follow the
interview contract below. Use the available grill-me skill when explicitly requested
or permitted by its invocation policy; otherwise conduct this workflow-owned
interview directly without invoking a prohibited skill. Explicit
report-only requests suppress the interview. Read-only requests allow discussion
but no ticket writes.

Select the highest-value ticket needing a human decision. Investigate available
evidence first: verify facts yourself, resolve routine implementation choices,
and ask only consequential questions the user must answer. Give a recommendation
and credible alternatives, one question per turn. Keep the opening question short
and avoid repeating the report. If no useful decision remains, end without an
invented interview. Do not wait in the background for an answer or schedule work.

Stay on that ticket until its necessary decisions form a coherent plan or it is
explicitly parked with the exact external dependency. Reuse prior answers and
approvals. Before switching, summarize the settled plan and remaining execution
prerequisites, then publish a cohesive ticket comment under the shared comment
rules when authorized. A settled plan does not authorize production execution.

Interactive questions to the user are distinct from external requester-question
limits. They never reset external deadlines/budgets or bypass ownership, approval,
and project-scope gates. A reply continues clarification in the same chat; it does
not automatically rerun discovery/build or replenish execution budgets. Perform
only the approved follow-up writes; new implementation needs an explicit request
or the next authorized workflow invocation.
