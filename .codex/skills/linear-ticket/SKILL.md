---
name: linear-ticket
description: >-
    Triage the Linear queue and deliver one ticket within a configurable estimate
    ceiling, including safe work while clarifying. Report outstanding work
    and critical questions. Explicit invocation only; no merging or deployment.
disable-model-invocation: true
---

# Linear Ticket

Find work for the current user, handle staleness, and deliver one bounded outcome.
Compare actionable tickets before choosing one; report critical questions without an interview.
Triage and deliver efficiently with minimal necessary communication. Comment when participant
input is needed, ownership is redirected, or another meaningful exception warrants an update.

## Parameters

- `count=20`: Positive integer; separate per-run caps on unique tickets deeply assessed
  and unique tickets changed, shared across stages/delegates. Metadata discovery is uncapped.
- `size=m`: Maximum implementation estimate, including Review-and-clarify. Accept short/full
  names case-insensitively: XS/Extra Small, S/Small, M/Medium, L/Large, XL/Extra Large.
  Resolve to the team's live estimate option and order; larger work is triage-only.

## Flow

```mermaid
flowchart TD
    Start[Start Run] -->|Checks Pass| Find[Find Candidates]
    Start -->|Invalid Count, Active Run, or Inspection Error| Report[Report]
    Find --> Project[Route Matching Tickets to Project]
    Project --> Owner{Current Assignee}
    Owner -->|Unassigned| Assign[Determine Intended Owner]
    Owner -->|Someone Else| Handoff[Check for Dropped Work]
    Owner -->|User| Triage[Triage Tickets]
    Assign -->|User or No Intended Owner| Triage
    Assign -->|Assigned Elsewhere or Unclear| Report
    Handoff -->|Transferred to User| Triage
    Handoff -->|Active Owner, Waiting, or Unclear| Report
    Triage -->|Set Triaged: Actionable Tickets| Deliver[Select and Deliver]
    Triage -->|None Actionable| Report
    Deliver -->|At Most One Implementation Ticket| Report
```

### Start Run

Reject invalid `count`. Before discovery, use native `list_threads` and targeted status/history
reads to check recent active chats for another ongoing `linear-ticket` invocation, regardless
of title. Exclude this run and configuration/review discussions. If another run is active,
link it and stop. Correct recoverable inspection errors and retry once; if inspection remains
unavailable or unsuccessful, report that and stop. A bounded listing
is sufficient best effort, not an atomic lock. These exits report only the reason, without
discovery, checkpoint reads, or ticket/PR writes; never interrupt the other run.

### Find Candidates

Verify the intended Linear user/account/workspace
through live lookup or confirmed identity, not OS/Git identity. Read `team`, `repository`, and
the required nonempty `creatorIds` allowlist from `~/.codex/private/linear-ticket-workflows.json`;
verify creator identities in the intended workspace, and stop if the allowlist is missing or invalid.
Normalize `size` aliases and reject unsupported values. Resolve the team's live estimate
options and order to compare sizes; a verified ordered label scale suffices. Never infer
order alphabetically or hardcode numeric values. If the scale is unavailable or ambiguous,
continue independent discovery, routing, ownership and triage; hold only size-dependent
actions and report the gap. Verify the live numeric mapping only when the write interface
requires a number; if unavailable, hold that estimate write without blocking unrelated work.
Legacy `maxEstimate`/`mediumEstimateLabel` don't override `size`.

Verify team/statuses; discover configured-team Triage/Backlog and Todo/In Progress/In Review
tickets across all assignees. For creator filtering only, a subticket inherits its parent's
effective creator recursively; a root ticket uses its own creator. Verify the live parent
chain and compare that effective creator with `creatorIds`, regardless of who created the
subticket. Keep Linear's actual creator unchanged; inheritance grants no ownership,
scope, size, readiness, or implementation exception. If ancestry cannot be verified,
hold creator eligibility rather than assuming a match or excluding the ticket.

Use supported server-side team/status filters and metadata
field selection; inspect the current interface rather than inventing arguments. Collect ID/URL,
team, assignee, status, actual creator, labels, project, priority, estimate, parent, and creation/update times.
Do not use a server-side direct-creator filter that would omit eligible descendants;
discover team/status metadata first, then resolve ancestry, including parents outside the
candidate team/status scope. Paginate each query independently and deduplicate; retain
direct-creator matches for project routing even when effective creator eligibility fails.
Verify effective creators against `creatorIds` before deep assessment or other writes;
the project-routing write below is the only exception. Parent metadata
lookups alone do not consume assessment slots.

Reuse existing private checkpoints/current automation memory as caches for metadata and
unassessed work. With a trustworthy checkpoint matching the verified workspace/user/team,
repository, creator allowlist, and query scope, prefer metadata-first updated-since deltas
with a boundary overlap and ID deduplication. Merge with prior candidates; don't drop older
unassessed work. Refresh tracked IDs regardless of current team/status to detect closure,
reopening, moves, reassignment, and creator or parent changes. Refresh relevant ancestor
metadata and recompute descendant eligibility when ancestry or an ancestor's creator changes;
a child's timestamp alone does not cover those changes. Recover tracked work from history/live
sources; apply the effective-creator filter to inventory/execution eligibility after project
routing. Excluded tickets may
appear as decision/dependency context under Report. Release nonmatching tickets only
from this workflow's inventory, without ticket/PR writes. Parents outside the candidate scope
remain ancestry/dependency context, not automatically executable work.

Use full discovery when the checkpoint is missing/untrusted, scope/filter semantics change,
or the interface cannot cover new/reopened/moved-in/status/creator/ancestry changes reliably. Repeat
full discovery at least every seven days. This backstop is metadata discovery, not unlimited
assessment. Record scan start; advance the checkpoint no later than that time only after all
queries are fully paginated and the result is saved successfully. On partial/error/blocked
saves, retain the previous checkpoint and unresolved inventory; report actual scan coverage
and any save failure. Absence from partial results is never closure. Don't invent a checkpoint.

Issue `updatedAt` alone cannot detect linked PR, dependency, discussion/Slack, or human-decision
changes. Refresh relevant source activity and newly linked references separately, including
during full reconciliation; use supported metadata/deltas before rereading unchanged bodies.
When unavailable, inspect relevant sources within the assessment budget and label uncovered
work accordingly. Recheck due handoff/feedback deadlines and refresh affected live evidence
before consequential writes. Cached summaries never replace exact human approval/STOP sources.

Order assessment by human direction, native priority, impact, urgency, and meaningful
activity. Replies, due feedback, and interrupted work matter; `updatedAt` alone doesn't.
Lightly refresh unchanged holds and queued PRs. Reopen completed assessments only on relevant
new evidence; finish incomplete promising assessments. Use remaining slots for new candidates.
When shown, label inventory-only or deferred assessments Skipped with the actual reason;
new deep investigation still consumes a slot.

### Route Matching Tickets to Project

For discovered tickets whose **actual creator** is in `creatorIds` and whose label matches
the private `bugProjectRouting.labelId`, route to `bugProjectRouting.projectId` before any
other ticket activity. Verify workspace, label, target project, current creator, labels and
project live; add an unprojected ticket and verify the result. Count each changed ticket
toward `count`. Already-targeted tickets need no write. Preserve a different existing project;
hold other activity and report it for the user rather than moving it. If routing is unverified,
fails, or a required routing write would exceed the unique-ticket change budget, hold all other
activity on that ticket and report why. A previously counted changed ticket can still be
updated within its existing slot. Missing/invalid
routing settings or unavailable label/project metadata hold potentially matching tickets,
not verified nonmatches. Never infer creator from a parent
for this routing rule. Refresh matching metadata when reopening cached inventory; changes to
this filter require a full discovery.

### Determine Intended Owner

Check current assignment, description/full discussion, linked PRs, and relevant Slack for
ticket-specific ownership evidence and later completion, withdrawal, refusal, or superseding direction.
Search ID/URL, broadening as needed. Ownership reconciliation needs reasonable evidence
that the person owns this work, independently of full relevance, completion, sizing, or
implementation-readiness investigation. Deep reads consume the assessment budget;
age or lack of a visible update alone isn't proof of inactivity or invalid ownership.

A ticket-specific human request, acknowledgement, or commitment is
  sufficient when no later evidence contradicts it or establishes completed work.
  Among owners established by that human evidence, choose the strongest-supported:
  explicit commitment, current investigation, then responsibility for the affected area. If multiple intended owners
  remain tied, choose the first named in the original human request, not an agent summary or
  generated offer. Exclude incidental mentions, reviewers, FYIs, and people who declined.
  When an intended owner is established, set and verify one assignee, then post one Linear comment; FYI-mention
  the other intended owners using verified native mentions, except the user posting it.
  Add those owners as subscribers through a supported interface, preserving existing subscribers,
  and verify the result. Mentioning alone isn't subscription proof; report unavailable or
  unverified subscription controls separately while preserving the assignment. Unresolved
  identity or applicability of the ownership evidence to this ticket blocks assignment;
  tie-breaking resolves routing, not acceptance or progress. Retain unassigned work without an
  intended owner and work assigned to the user for triage; report unresolved ownership.

### Check for Dropped Work

For other-owned tickets, use lightweight metadata to identify a plausible dropped commitment or
explicit handoff. Reconcile verified superseding handoffs first; otherwise, if the owner is
active or no takeover signal exists, stop and omit the ticket. Age, silence, or routine PR activity alone
doesn't establish dropped work. Investigate credible signals and later human handoffs without
overwriting ownership from weak inference. For a plausible takeover, confirm work remains relevant and
  inspect discussion, PRs, and project/worker activity. Post one Linear handoff offer in the
  user's voice: "Are you still working on this? I can take it if not. Unless you'd prefer to
  keep it, I'll pick it up after [date/time]." Mention the owner and set a deadline two business
  days after publication (Monday–Friday, preserving local time in America/Chicago).
  On a later normal run, after that deadline, recheck replies, assignment, and activity; only
  then assign to the user and comment on the handoff if no objection or competing activity.
  A clear earlier acceptance permits immediate handoff.
  Don't reset the window or duplicate offers. No new schedules or waiting for replies.

For assignment comments, address the assignee naturally and link the source; briefly explain
the handoff when useful. Usually one or two sentences; include constraints when they change
the recipient's next action. Keep tie-break mechanics internal unless useful to the recipient.

Never use silence to override a refusal, active PR/project ownership, or human STOP.
Ticket staleness is separate from stale ownership; don't cancel other-owned tickets.
Keep ownership evidence, original offer/deadline, next action, and ambiguity in report notes/
private checkpoints; include relevant evidence in permitted ownership comments. A missing/
unverified offer or deadline cannot justify takeover. No assignment implies a start,
deadline commitment, or implementation approval.

Retain user-owned tickets and unassigned work with no intended owner for implementation
triage. Retain unresolved ownership/handoffs internally; surface consequential decisions or
passive waits under Report while independent work continues. Other-owned work isn't
executable by this workflow. Reviews on the user's PR
aren't competing ownership. Assignment changes don't override scope, size, or readiness gates.

### Triage Tickets

Build and triage the bounded set incrementally, reserving slots for required parents
before admitting more candidates. Give every retained ticket a disposition or documented
assessment limitation **before selection**; don't build the first actionable ticket found.
Read relevant attachments, relations, and PR evidence. Resolve current relevance/priority
before scope/implementation details; then check context/access, essential behavior,
dependencies/permission, independent size, acceptance criteria, and verification.
Finish obtainable readiness checks for counted tickets; the unique-ticket cap limits admitting
additional tickets, not inspection of those already counted. Human-prepared work needs no prior
workflow triage. Dispositions:

- **Stale:** Apply the age policy, recheck, post a first-person reasoned comment, then set
  native Canceled. Distinguish stale/unprioritized from fixed; invite reopening with current
  impact/example. Verify both writes and reconcile partial failures before retrying.
- **Actionable:** Ready or safe for Review-and-clarify. Technical uncertainty may proceed
  with safe defaults, clarification questions, or a material approach-difference notice.
- **Hold:** Unresolved intended behavior/essential scope, unsafe unknowns, ownership,
  dependencies, access, or
  permission block affected work. Investigate obtainable facts; otherwise report blocker,
  owner, resumption condition, and critical user questions. Don't claim held work for
  implementation. Route follow-up questions and split/project approval requests to the user
  in this chat. Above `size`, recommend a split/project and report needed approval.

Judge complete outcomes, including rollout/acceptance. Multi-phase/multi-owner work may
need project framing; a bounded approved-project leaf can qualify independently. Recheck
holds on new evidence or actionable follow-up.

#### Staleness

Investigate discussion/Slack, related fixes/tickets/PRs, and code/reproduction where practical.
Consider impact, meaningful activity, commitments, and dependencies; bot/workflow updates
don't renew demand. Agent-authored plans, questions, and keep-open statements aren't human
direction, even when posted under the user's account. Trace consequential holds to their original
human instruction; preserve genuine STOP/keep-open directions. Creation age sets disposition,
not proof of a fix:

- **Under 4 weeks (28 days):** Normal triage.
- **4 to under 12 weeks:** Lean toward cancellation for resolved, superseded, abandoned,
  or unprioritized need. Ask the user once in this chat if uncertainty could change the result.
- **12 weeks (84 days) or older:** Default to cancellation unless the bounded check finds
  meaningful persisting impact, renewed demand, active commitment, or a live dependency.
  Cite ticket-specific retention evidence and continue triage. An active project, related product
  interest, or an unanswered agent question alone is insufficient; apply the stale default once
  required ownership/relevance checks pass rather than inventing an indefinite hold.

For a participant demand-confirmation question published under existing comment authority
on an old request, allow **five calendar days from its original ticket server publication**.
User-directed demand decisions stay in chat and require an answer or explicit direction. Edits and reruns preserve the deadline;
an open window takes precedence over age-based cancellation. At expiry, recheck replies
and relevance. If demand remains unconfirmed and there is no persisting impact, active
commitment, live dependency, or explicit keep-open direction, post a brief reason, invite
reopening with current requirements, and cancel within the existing ownership rules.
Missing access or an unverifiable deadline requires investigation, not cancellation.

Unknown creation time blocks age-based cancellation; missing access/ownership isn't
cancellation evidence. Reopens/substantive replies renew assessment, not implementation
permission. Recheck eligibility/readiness; silence isn't resolution. Renewed demand or
explicit human keep-open direction prevents repeat cancellation without new evidence.

#### Approach and Size

For bugs, extract observations, expected behavior, reproduction facts, and constraints;
investigate independently before comparing implementation suggestions/estimates. For
requests, preserve the outcome while independently choosing implementation/size.

The complete outcome must fit **`size` and one or two coherent PRs**. Don't omit essential
behavior, compatibility, permissions, or test protection to fit. Update estimates from
evidence when the write value is verified; otherwise report the pending write. Only implement
when the independently assessed complete size and ceiling can be compared on the verified
live scale. Do not claim oversized work or remove its assignee. Above `size` is triage-only;
no automatic children or oversized parent execution. Splits/project changes need approval.

Before requesting split approval, investigate the complete decomposition. Each implementation
leaf needs an evidence-supported estimate within `size`, a coherent outcome, dependencies,
and acceptance/verification criteria. Cover all essential parent requirements, including
indirect compatibility effects. Larger parents may track the combined outcome; don't relabel
oversized implementation work as tracking or defer requirements to meet the ceiling.

If missing evidence prevents credible sizing, finish obtainable investigation or report the gap
before proposing children. Approved children still need execution readiness checks; tracking
approval isn't implementation approval. If later evidence changes sizing, explain the new facts
or earlier omission and propose one consolidated revision, not successive unassessed splits.

### Select and Deliver

Compare the assessed set's actionable tickets by human direction, native priority, impact,
urgency, dependencies, readiness, and meaningful activity. Recommend priority-field changes;
don't silently apply them. Select **one** authorized outcome within `size`, including safe
Review-and-clarify; leave others queued without invented blockers. Incomplete assessment
isn't readiness. If none qualify, report instead of forcing a build. Assign selected unassigned
work to the user before implementation; ownership reconciliation alone doesn't select a build.

Before implementing, trace the reported case through relevant acceptance behavior to surface
likely questions, policy conflicts, and material approach differences. Post an optional start
comment only for meaningful information to the ticket creator; required participant questions
are posted even when directed elsewhere. Combine relevant approach details and questions.
Native status records routine starts.
Ask user-directed questions/approvals in this chat. State the choice,
recommendation, and whether safe work can proceed or affected work needs an answer.
Route later discoveries and proposed follow-up comments to the user here before publishing.

Follow repository isolation/authoring/testing guidance and protected-test approvals. Once
selected, a new blocker doesn't permit choosing another implementation. Preserve/reuse
existing branches/PRs; two-PR outcomes share acceptance, feedback timing, and combined validation.
Confirm plan/assignment; new work enters Todo then In Progress, while resumed work keeps
its lifecycle. Open only review-ready PRs with ticket links, behavior, approach, acceptance,
and validation. Keep work in progress on the branch.

For Review-and-clarify, publish participant questions before implementation. When safe work
is reviewable, open it ready with `noautomerge` applied at creation. If the tool cannot
create the PR with the label, keep the work on the branch and report the blocker. Verify
the label, record why it was applied, and link the PR in the comment if useful.

Remove only the clarification hold applied by this workflow, after applying substantive
feedback or a documented safe default and validating the result. The default is allowed
after **48 hours from the questions' original ticket server publication**. Edits, reruns,
and other PRs don't reset the window. User-directed questions go in this chat and require
an answer or explicit direction before releasing affected work to the queue. Chat silence
doesn't start or satisfy that window. Preserve separate holds, ownership, relevance,
prerequisites, permissions, and test requirements. Changed intended behavior, essential
scope, or unsafe unknowns still require approval before affected work.

While feedback is pending, keep the appropriate active ticket status and report without
waiting. At queue handoff, request review
under repository policy and move to In Review. Post a delivery comment only when it conveys
meaningful new information to the ticket creator; PR readiness, CI and review handoff alone
do not qualify. PR review follows the user's review workflow; never imply the creator is asked
to review unless explicitly requested. The merge queue owns eligible PRs: observe/report without
competing pushes, Draft reversions, or review/CI/merge work unless explicitly directed.
Distinguish merged, deployed, and operationally accepted.

### Report

Every run, including blocked/unchanged runs, gives one outcome sentence with meaningful
changes/delivery. Include counts, timing or coverage limits only when useful to the decision.
Then use these sections in order, placing each ticket once:

- **Needs Your Input:** Numbered decisions/interventions for currently relevant work.
  Link the ticket, recommendation and what the answer unblocks; identify the actual decision
  owner after investigation. Include proposed outreach with its audience. Retain unanswered
  consequential asks with original links; silence never resolves them. Workflow exclusions
  such as size or creator filters can merit a decision here; exclusion doesn't imply low value.
- **Active Work:** A Markdown table for the user's or unassigned ready candidates,
  implementation or PR delivery, and material scope/size comparisons. Keep decision-only tickets above.
- **Waiting:** A compact list or sentence for prerequisites or handoffs that warrant attention.
  Omit unchanged blocking questions while their feedback window is open. Report replies,
  material changes, or deadline-triggered actions. Demand confirmation uses five calendar
  days; implementation clarification follows the existing 48-hour safe-default rule.
  User-directed asks still require an answer or explicit direction.

Show other-owned tickets only for assignee-flow activity: a new assignment, takeover offer,
meaningful handoff response/change, accepted transfer, or ownership decision needing input.
Omit actively owned work without qualifying assignee-flow activity or a pending ownership
decision, even if its PR changes; routing to the Bugs project alone doesn't qualify. Apply the feedback-window reporting rule to unresolved handoffs, preserving their original deadlines. Report project
routing as a concise count when useful. If reporting counts, call creator matches
`creator-matching`, not eligible or ready; distinguish assessed and implementation-ready.
Apply the same inclusion rules to inbox summaries. Omit inventory-only work needing no input.
Report material actions in the outcome sentence without repeating ticket details.
Sort each section by explicit human direction, priority/impact, then oldest creation
(unknown last; ID breaks ties), not by Action. Omit empty sections and routine execution receipts.

Active Work table: `Ticket | Status | Creator | Assignee | Estimate | PRs | Action | Update/notes`.
Creator: show the actual creator; when different, identify the inherited effective creator
and source parent in notes so eligibility is clear.
Assignee: show the current Linear assignee's name without a qualifier. If unassigned but
context establishes an intended or suggested owner, show `Name (inferred from Slack)` or
`Name (inferred from Linear)` only with a concrete ownership/write blocker or exhausted
change budget stated in notes. Otherwise complete the supported assignment before reporting;
apply the ownership tie-break rather than retaining alternatives. Readiness or subscription
uncertainty alone doesn't justify leaving a supported owner inferred.
An explicit commitment outside the assignee field still uses the inferred-source qualifier.
Otherwise show `Unassigned`, or `unknown` if the field/evidence wasn't verified. Don't add
an Unassigned prefix or separate commitment labels; reporting an owner doesn't assign the ticket.
Link tickets/PR states/evidence. Action is this run's work:
observed merges are Assessed; inventory-only or deferred assessments are Skipped.
Notes explain why the ticket is included when unclear, what was checked/changed, and its
disposition or next action. For Skipped, state the concrete reason, such as unchanged prior
disposition, exhausted budget, or unavailable evidence.
Distinguish verified routing from incomplete assessment; skipped work remains pending where
checks are unfinished. An assignee alone doesn't establish activity or staleness.
Use unknown for unverified facts, — for verified none.
Keep the full internal inventory until verified closure, creator-filter exclusion or explicit
tracking release; report omission and reassignment aren't release. Retain unresolved holds,
offers/deadlines and incomplete checks privately; label carried-forward findings when shown.
Do not collect closed/other-owner inventories solely for reporting. Surfacing excluded work
as a decision or dependency grants no eligibility exception or execution authority.

Finish after reporting: no interview or waiting for replies. Later answers update the
relevant disposition within remaining authority/budget; they don't restart discovery,
replenish budgets, or permit a second implementation. Don't revive completed/withdrawn proposals.

## Rules

- Leave ticket descriptions unchanged unless the user explicitly requests a specific edit.
  Use permitted comments for participant-facing updates; put implementation decisions and
  validation details in the PR. Keep Codex chat links, approval provenance, and workflow
  bookkeeping in chat or private checkpoints, not Linear.
- Honor read-only/report-only limits. Normal runs authorize Linear assessment/updates,
  eligible stale cancellations, and one ticket's implementation/commits/pushes/PR
  handoff. Exclude merging, auto-merge, deployment, production writes, project creation/
  reorganization except the configured bug-project routing above, email/SMS/Slack messages,
  and automation changes. Readiness/silence isn't
  authorization; follow applicable approvals.
- `count` limits assessed tickets and, separately, changed tickets—not API calls. Count
  each deeply read ticket once across ownership/triage/delegates, including holds and parents.
  Metadata-only refreshes consume no assessment slots. Delegate briefs include remaining budgets, `size`, and expected
  readiness/relevance/disposition. Critical questions/approval needs have no separate cap.
- Verify the repository remote before code access. Reuse sufficient evidence; refresh affected
  ownership/discussion/prerequisites/PRs before writes. Missing evidence blocks dependent
  actions, not independent work; report incomplete coverage, never false emptiness.
- STOP holds require fresh resumption direction. Only the explicit handoff process above
  authorizes reassignment after silence; silence never approves implementation or scope changes.
  Completed approvals aren't standing instructions/eligibility exceptions. Don't duplicate external outreach/reminders, invent
  questions, or promise background follow-up.
- Messages intended for the user belong in this chat, including approval requests.
  Otherwise, ticket comments are limited to ownership assignments/handoffs and takeover
  offers/completion; stale cancellation reasons and reopening invitations; the first
  implementation update with the approach and known participant questions; and ready delivery.
  Apply creator relevance to optional start and ready-delivery comments as specified above;
  required participant questions remain mandatory. Add a useful later PR link by editing
  the initial implementation comment when one exists. Route other
  proposed comments to the user here and await explicit instruction before publishing.
  Speak on the user's behalf in their voice, naturally and conversationally, following the
  [canonical writing guide](../../agents/writer.md#guide-location). Keep internal dialogue
  between the user and the agent out of ticket comments.
  State the user's decisions directly as their own; mention approval or feedback only when
  requesting it from another person. Keep the user's approvals and provenance in chat or
  private checkpoints.
  Keep comments within 100 words, lead with important requests in bold, and address recipients
  using verified native mentions: `@person: question`. Consolidate related information into
  the applicable comment; technical detail belongs in specifications/PRs.
- Keep settings/checkpoints private. Checkpoints at
  `~/.codex/private/linear-ticket-workflow-state/<verified-issue-uuid>.json` are caches, not
  authority (directory 0700/files 0600). Preserve sources, approval scope/completion,
  questions/decisions, original feedback time, next action, inventory/closures, and assessed
  versus applied feedback. Recover stale/missing state from live sources; no private
  bookkeeping in tickets/PRs/repo trackers.
- For automation runs, replace superseded memory with one concise current-state note:
  scope, discovery/full-discovery checkpoints, coverage gaps, open-work/checkpoint links,
  holds/deadlines/decisions, and next actions. Keep detailed history retrievable in native
  chat/ticket/PR records or private checkpoints; before removing its only copy, preserve a
  private historical record and reference. Keep the full tracked/unassessed inventory and
  exact approval/STOP provenance recoverable. Memory never proves eligibility or clears a hold.
- Memory/checkpoint saves never block reporting/questions. If blocked, briefly explain,
  retain results in chat, and complete the report. Don't substitute memory approval,
  wait, or bypass the restriction; recover later from chat/live evidence. No grill-me session.
