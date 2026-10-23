---
name: linear-ticket
description: >-
    Triage the configured Linear queue for current relevance, ownership, clarity,
    and bounded scope. Advance the right follow-up for unready work or implement
    one ready Medium-or-smaller ticket, then report outstanding work and resolve
    user decisions one ticket at a time. Explicit invocation only; no merging or
    deployment.
disable-model-invocation: true
---

# Linear Ticket

Turn the queue into delivered small work or clear next actions. Triage asks
**is this ready for work?** Priority chooses which ready ticket to implement;
readiness and permission to act are separate decisions.

## Scope and setup

Run only on an explicit user request or an existing authorized automation.
Honor read-only, report-only, and explicitly scoped requests. Normal runs may
assess and update Linear tickets and implement one eligible ticket, including
branches, commits, pushes, Draft PRs, and the ready-for-review handoff. They do
not authorize merging, auto-merge, deployment, production writes, project
creation/reorganization, or email/SMS/Slack messages. Follow applicable approval
rules; silence never grants ownership, scope, test-contract, or production approval.
Do not create/edit automations, wait in the background, or promise a scheduled
follow-up. A user reply continues the interview in this chat.

Read `~/.codex/private/linear-ticket-workflows.json`. Require the configured
`team`, `repository`, numeric `maxEstimate`, and `mediumEstimateLabel`.
Verify the intended authenticated Linear user/workspace, team statuses, and
live estimate scale; verify the repository remote before accessing code.
Use authenticated current-user lookup or an explicitly confirmed Linear identity,
not OS/Git identity. The execution ceiling is **M**, or a lower configured maximum.
A legacy higher `maxEstimate` never permits L execution. Missing or unverifiable
settings/access are specific blockers, not an empty queue. Keep settings private.

For repository work, follow its applicable guidance, isolation, testing, and PR
conventions. Reuse authenticated identity and source evidence within the run;
refresh affected issues, discussions, ownership, prerequisites, and PRs before
mutations. Don't redo unrelated checks or broaden an uncertain target.

## 1. Discover and choose what to assess

List metadata for the configured team's Triage/Backlog and Todo/In Progress/In
Review tickets, unassigned or assigned to the current user. Use supported filters,
independent pagination, and deduplication. Collect IDs/URLs, creator, assignee,
status, priority, estimate, parent, creation time, and update time. Resume discovery
as needed; an unfinished listing never proves the queue is empty.

Also recover previously tracked work from prior reports, authorized run history,
private checkpoints, and native ticket/PR evidence. Don't lose open tracked tickets
because their status or assignee changed. Metadata inventory can exceed the screen
budget; unrelated listing results are not a permanent watchlist.

Exclude current-user-created tickets except verified workflow children whose
creation was authorized. Assignment, parent links, and a checkpoint alone do not
prove that exception. If creator eligibility cannot be verified, hold the affected mutation. Don't use
legacy `triageCreatorEmails` filters.

Respect human direction and native priority, then current impact, urgency,
dependencies, readiness, and meaningful activity. Actionable replies, due feedback
windows, or interrupted work may deserve attention; prior workflow involvement
or newest `updatedAt` alone gives no priority. Recommend priority changes rather
than silently changing the recorded field.

Fully assess at most **10 distinct tickets**, and mutate at most **10 distinct
tickets** per run. Reading a parent's detailed discussion counts too. A held or
unready ticket still counts when fully assessed. Use lightweight inventory checks
for unchanged holds so they don't repeatedly crowd out new candidates. Never
claim a full assessment based only on metadata. Delegate briefs must request
readiness, relevance evidence, and a next disposition, not just buildability.

## 2. Triage readiness

Read the selected ticket's relevant description, full discussion, attachments,
relations, and existing PR evidence. Resolve these questions:

| Check | Ready means |
| --- | --- |
| Relevance | The problem still exists or the requested outcome is still valid. |
| Ownership and fit | Work is available to the current user, without conflicting ownership, and required context/access are available. |
| Clarity | Desired behavior, essential scope, and consequential decisions are clear enough to proceed; safe technical defaults are acceptable. |
| Scope | Independently sized at most M, with a complete outcome deliverable in one or two coherent PRs. |
| Prerequisites and permission | Required dependencies and authorizations are satisfied. |
| Validation | Concrete acceptance criteria and a practical way to verify success exist. |

Assess the complete outcome, not just its code diff. Work needing an unresolved
multi-phase, multi-owner rollout or acceptance plan needs project framing even
when its code is M-sized. Project membership alone does not exclude an independently
bounded leaf under an approved plan; don't take over the broader initiative.

Urgency and importance determine selection, not whether these conditions hold.
A human-prepared ticket can be ready: prior preparation by this workflow is not
required. Establish readiness from current evidence, and adopt an existing plan
when it is sufficient. Reuse existing branches/PRs; never duplicate work.

### Ownership

Before claiming or changing a candidate, check Linear discussion, linked PR work,
and relevant Slack threads found by ticket ID/URL in the intended workspace.
If required ownership evidence is unavailable, hold the affected action.
Directed responsibility or explicit handoff outweighs the assignee field; a ticket
assigned to someone else remains excluded. An incidental mention is not ownership.
Don't take over another engineer's active work or interpret old age as permission.

If no other engineer has substantively participated, continue normal triage.
When another engineer participated but no explicit direction settles ownership,
preserve the seven-day activity check across issue, Slack, and PR activity,
including bots. Recent activity means skip; if all activity is older, a single
takeover question may be appropriate. Ordinary review feedback on the current
user's already-owned PR does not trigger this new-work participation veto. Only explicit affirmative handoff clears that ownership hold;
reuse an existing ask, and never repeat it. Across a run, post at most one new
ownership or exceptional authorization/risk ask; report other such needs privately.
This conservative activity check is separate from relevance below.

### Relevance, especially old work

Consider creation age, last meaningful activity, and what that activity says.
Run a quick proportional check against current code, related fixes/tickets, and
recent evidence before detailed planning. Bot changes and this workflow's own
updates do not by themselves renew relevance. Age alone never proves obsolescence.

- **Still relevant:** Record the current signal and continue normal triage.
- **Suspected stale:** Evidence is inconclusive. Ask once on the ticket whether
  the problem persists or the request is still needed, stating what was checked.
  Reuse existing questions and answers; if unanswered, don't send repeated pings.
  Bring an evidence-backed keep/park/close decision to the user when useful.
- **Likely stale:** Evidence suggests resolved, duplicate, obsolete, or superseded
  work. Propose the terminal disposition and reason to the user. Close only after
  explicit confirmation for that ticket, rechecking live evidence before writing.

Put the relevance finding, evidence or exact access gap, and next action in the
report. "No implementation plan" and "not buildable" are not relevance findings.
An unresolved relevance question blocks implementation; the Draft feedback timer
below never supplies proof of relevance or closure approval.

### Independent approach and size

For bugs, extract the problem, observed/expected behavior, reproduction facts,
and real constraints. Investigate independently before comparing suggested
implementations or estimates. For specific nonbug requests, preserve the requested
outcome while choosing implementation and size independently. Respect approved
behavior, compatibility, permissions, and test contracts; don't discard essential
work to fit the ceiling. Update the native estimate when the evidence warrants it,
but don't claim oversized work or remove its assignee automatically.

**L or larger is triage-only.** Recommend a clean split into independently useful
S/M outcomes or finite project framing; don't automatically create children,
execute the parent, or hide a large change in two PRs. Ticket creation/splitting
and project changes require their own applicable approval. Existing approved
children can qualify individually after their own readiness checks.

## 3. Choose the next action

| Result | Follow-up |
| --- | --- |
| Ready and selected | Prepare native fields/concise plan, assign if appropriate, move new work to Todo or resume its existing lifecycle, and implement. |
| Ready but not selected | Keep ready in the queue; don't invent a blocker or claim delivery. |
| Facts the agent can obtain are missing | Investigate directly within the assessment budget. |
| Consequential decision or relevance is unclear | Ask the right person one focused question; use the user interview for decisions the current user can settle. |
| Likely stale | Review the proposed closure with the user. |
| Ownership belongs elsewhere | Respect it and report the verified owner; obtain explicit handoff when appropriate. |
| Scope is too large | Explain the sizing and recommend a split/project; seek required approval. |
| Dependency, access, or permission is missing | Park with the exact blocker, responsible person, and condition for resuming. |

Choose and perform the smallest authorized follow-up, not necessarily a comment.
Do not claim/assign a ticket merely to leave it blocked by an already-known gate.
Reuse answered questions and safe defaults. Ask only current consequential gaps;
do not impose a lifetime question count that prevents a later relevance check.
Never repeat unanswered asks or post reminders on unchanged runs. A parked ticket
remains visible, with a next owner/action; recheck it when evidence changes or a
recorded follow-up becomes actionable. If no useful next step can be performed,
state exactly why, rather than carrying forward a generic hold.

## 4. Implement one selected ready ticket

Implement or substantively update at most **one ticket** per run, with one or two
PRs only when the complete bounded outcome requires them. A newly discovered
blocker on that selected work doesn't authorize starting a second build. Preserve
partial work and report the gap. Multiple PRs share the same acceptance criteria
and feedback window; completion requires their combined result.

Follow repository guidance for investigation, regression coverage, checks,
branches, commits, and PR descriptions. Keep changes focused. Reuse the owning
branch/PR. Move to In Progress when implementing, and In Review on the ready
handoff; don't round-trip existing work through Todo. Keep native PR links current
and post one brief delivery comment with all owning PRs, verification, and remaining
delivery steps. Create new PRs Draft while authoring; link the ticket and summarize
its intended behavior, approach, acceptance criteria, and validation. Honor
protected-test approvals; a recommended default cannot replace one.

Safe technical defaults may proceed while ordinary feedback is pending. Explain
material departures from a suggested approach once, with the reason and Draft PR
link. Changed intended behavior/scope or unsafe unknowns require authorization
before affected implementation, not merely a Draft label.

**Draft feedback rule:** Initial clarification questions or a material approach
review notice start one 48-hour window from the original server publication time.
Keep affected PRs Draft until substantive feedback is incorporated or the window
elapses and recorded safe defaults are applied. Edits, another PR, and later runs
never reset the clock. Recheck all answers and verification before marking ready.
Never fabricate original timestamps or defaults, promote a human-held Draft, or
let elapsed time override relevance, ownership, prerequisites, permission, or tests.
No ordinary feedback needed means ready after implementation and verification.

Before handoff, re-fetch feedback and apply or explicitly resolve in-scope replies;
reading a reply is not implementing it. Mark verified, complete PRs ready and
follow the repository's review-request policy. **Ready PRs belong to the merge
queue:** observe/report their outcome, don't push competing changes, return them
to Draft, or take over review/CI/merge work. Route later findings to the owning
workflow through an authorized channel; a direct user request can override this
boundary. PR merge, deployment, and operational acceptance are distinct outcomes.

## 5. Communicate and retain continuity

Write as the current user speaking naturally to a teammate. Resolve the canonical
writing guide through [the writer guide-location rules](../../agents/writer.md#guide-location).
Ticket comments should lead with the outcome or needed response and next action,
usually a few sentences and at most **100 words**. No interview references,
option numbers as decision provenance, UUIDs, workflow receipts, or hidden state.

When necessary decisions are settled, publish one cohesive plan: what I'll do,
why, what I need from the requester, and how we'll verify the result. Prefer
updating an existing plan when appropriate; preserve useful discussion/approval
evidence. Don't publish partial interview answers as a barrage of comments.
A necessary relevance/clarification question, material blocker change, or actual
delivery result can merit a separate comment. Put technical detail in the ticket
specification or required PR description, not repeated status comments.

Use existing private checkpoints at
`~/.codex/private/linear-ticket-workflow-state/<verified-issue-uuid>.json` only as
caches (directory 0700, files 0600). Preserve existing fields; retain minimal source
references, pending asks/decisions, original feedback timestamps, next action, and
inventory/closure evidence. Keep assessed feedback separate from applied feedback.
Never copy private state into Linear, PRs, or repository tracking files. Recover
from live sources when missing/stale; a cache never grants authority. If a write
needs approval or fails, respect that boundary and continue independent discussion
or investigation. Cache synchronization is not a prerequisite for the interview.

## 6. Report, then continue the decision interview

Every run, including unchanged/blocked runs, reports verified results concisely:

- One outcome sentence with screened/changed/build counts, known open/recent-closed
  counts, and any partial coverage. Timing once when useful.
- Up to three short bullets for actual results or needed intervention, without
  repeating table details. Omit empty sections and routine tool/checkpoint narration.
- **Still in play:** All tracked open work needing the current user or unresolved
  ownership, including unchanged holds and inventory-only rows.
- **Closed in the last 24 hours:** Verified native terminal transitions, retained
  for 24 elapsed hours after the actual closure, not PR merge or `updatedAt`.
  Unknown closure time stays separately labeled unverified until resolved;
  reopened tickets immediately return to open inventory.
- **Owned by others:** One linked `<ticket> - owned by <owner>` per item. Include
  current exclusions and tracked open handoffs; don't duplicate them in the tables.

Both open and closed tables use exactly:
`Ticket | Status | Estimate | PRs | Action | Update/notes`.
Sort Action alphabetically with Skipped last, then native workflow status order,
then oldest ticket creation first (unknown times last; ticket ID breaks ties).
Link ticket IDs and owning PRs/states. Action describes this run's actual work
(e.g., Assessed, Asked, Triaged, PR started, PR updated, Marked ready, Skipped);
observing another person's merge/closure is Assessed. Inventory-only is Not assessed.
Notes give a short disposition, evidence, and next owner/action; put closure time
there for terminal rows. Use unknown for unverified facts and — for verified none.

Reconcile tracked inventory with live metadata/PR states without deeply reassessing
all tickets outside the 10-screen budget. Keep unresolved tracked tickets visible
until verified closure or explicit release from tracking; reassignment alone
isn't release. Label carried-forward findings and incomplete recovery honestly.
No required inventory row may be removed merely to shorten the report.

### Interview loop, including replies after the run

After the report, pick the most valuable unresolved user decision or stale-ticket
closure review. Investigate available facts first. Ask **one question per turn**,
followed by numbered choices; put **(Recommended)** on the first choice and give
each a brief consequence/tradeoff. Use this format for the opening and every
follow-up. A factual question with no meaningful alternatives can be direct.
These workflow-specific rules apply even without invoking grill-me; invoke that
skill only when its invocation policy permits or the user explicitly requests it.
A report-only request suppresses the interview. If no question can help, briefly
explain the evidence-backed reason; "no build," "already interviewed," or a
historical hold alone is insufficient.

**After every answer:** incorporate the decision, perform specifically authorized
follow-up actions, and reassess the same ticket's remaining readiness gaps. Then
ask its next consequential question. Completing an approved ticket write does
not end the interview. Don't repeat settled decisions or jump among unfinished
tickets. When settled or genuinely parked, summarize the resulting plan and any
exact external dependency, publish the cohesive plan if authorized, and offer a
numbered checkpoint to review the next ticket or finish. Recommend finishing when
no useful decisions remain; don't invent questions to extend the conversation.

Interview replies continue this decision process, not a new automatic queue/build
run or a reset of execution budgets. Tracking-only approval doesn't authorize
implementation. If the ticket becomes ready, execute only when the current
invocation still has that authority and budget, or the user explicitly requests
implementation; otherwise retain it ready for the next authorized run.
