---
name: linear-ticket
description: >-
    Triage Linear tickets for readiness, advance specific follow-ups, and implement
    one ready Medium-or-smaller ticket. Report outstanding work and resolve user
    decisions one ticket at a time. Explicit invocation only; no merging or deployment.
disable-model-invocation: true
---

# Linear Ticket

**Triage readiness → follow up or implement → report → resolve user decisions.**
Priority selects among ready tickets; readiness does not itself authorize an action.

## Setup and limits

Honor read-only, report-only, and ticket-scoped requests. Normal runs authorize
Linear assessment/updates and one ticket's implementation, commits, pushes, Draft
PRs, and ready handoff. They exclude merging, auto-merge, deployment, production
writes, project creation/reorganization, email/SMS/Slack messages, and automation
changes. Follow applicable approvals; silence never grants permission. Don't wait
in the background or promise automatic follow-up.

Read `~/.codex/private/linear-ticket-workflows.json`: require `team`, `repository`,
numeric `maxEstimate`, and `mediumEstimateLabel`. Verify authenticated Linear
user/workspace, statuses, and live estimate scale; verify the repository remote
before code access. Use current-user lookup or an explicitly confirmed Linear
identity, not OS/Git identity. The ceiling is **M or a lower configured maximum**,
even if legacy settings permit more. Keep settings private; unavailable or ambiguous
configuration/access is a blocker, not an empty queue.

Follow repository guidance for isolation, testing, and PRs. Reuse verified context,
but refresh affected tickets, ownership, discussion, prerequisites, and PRs before
mutations. Don't broaden an uncertain target.

## 1. Discover and select

List configured-team Triage/Backlog and Todo/In Progress/In Review metadata,
unassigned or assigned to the current user: IDs/URLs, creator, assignee, status,
priority, estimate, parent, creation/update times. Use supported filters,
independent pagination, and deduplication; unfinished listings don't prove emptiness.
Recover tracked work from prior reports/run history, private checkpoints, and native
ticket/PR evidence, including tickets whose status or assignee changed.

Exclude current-user-created tickets except verified, authorized workflow children;
parent links or caches alone aren't proof. Unverified creator eligibility blocks
mutation. Ignore legacy `triageCreatorEmails` filters.

Rank by human direction and native priority, then impact, urgency, dependencies,
readiness, and meaningful activity. Actionable replies, due feedback windows, and
interrupted work matter; workflow history or newest `updatedAt` alone gives no
priority. Recommend recorded priority changes rather than applying them silently.

**Per run: at most 10 fully assessed tickets, 10 mutated tickets, and one
implementation ticket.** Detailed parent reads and held/unready assessments count.
Metadata inventory may exceed 10; it isn't full assessment. Check unchanged holds
lightly so they don't crowd out new work. Delegate briefs must request readiness,
relevance evidence, and the next disposition.

## 2. Assess readiness

Read the ticket's relevant description, full discussion, attachments, relations,
and PR evidence. Human-prepared work can qualify without prior workflow triage.

| Check | Ready means |
| --- | --- |
| Relevance | The problem persists or the request remains valid. |
| Ownership/fit | Work is available to the current user, with needed context/access. |
| Clarity | Outcome, essential scope, and consequential decisions are clear; safe technical defaults are acceptable. |
| Scope | Independently sized at most M and deliverable in one or two coherent PRs. |
| Prerequisites/permission | Dependencies and required authorizations are satisfied. |
| Validation | Concrete acceptance criteria and practical verification exist. |

Judge the complete outcome, not just the diff. Unresolved multi-phase, multi-owner
rollout/acceptance needs project framing even with M-sized code. An independently
bounded leaf under an approved project can qualify without taking over the initiative.

### Ownership

Before claiming/changing work, check Linear, linked PR activity, and relevant Slack
threads found by ticket ID/URL in the intended workspace. Missing required ownership
evidence blocks the action. Respect directed responsibility and explicit handoffs;
exclude tickets assigned to others. Incidental mentions and age aren't permission.

If no other engineer substantively participated, proceed. Otherwise, when no
explicit direction settles ownership, skip if any issue/Slack/PR activity (including
bots) occurred within seven days. If all activity is older, one takeover ask may
be appropriate; only explicit affirmative handoff clears it. Ordinary reviews on
the current user's own PR don't trigger this new-work veto. Reuse unanswered asks.
Post at most one new ownership or exceptional authorization/risk ask per run;
report additional needs in the user chat.

### Relevance

Consider creation age, last meaningful activity, and its substance. Quickly check
current code, related fixes/tickets, and recent evidence before detailed planning.
Bots and this workflow's updates alone don't renew relevance; age alone doesn't
prove obsolescence. Keep this separate from the ownership activity rule.

- **Still relevant:** Record the current signal and continue.
- **Suspected stale:** Ask once on the ticket whether the issue/request persists,
  stating what was checked. Reuse questions/answers without repeated pings; bring
  a keep/park/close recommendation to the user when useful.
- **Likely stale:** Propose closure and its reason for explicit user confirmation;
  recheck evidence before closing. Never close solely for age or silence.

Report the finding, evidence/access gap, and next action. Missing implementation
plans aren't relevance findings. Unresolved relevance blocks implementation;
feedback timeouts don't establish relevance or authorize closure.

### Approach and sizing

For bugs, extract observed/expected behavior, reproduction facts, and constraints;
investigate independently before comparing suggested implementations or estimates.
For nonbug requests, preserve the outcome while choosing implementation and size.
Respect approved behavior, compatibility, permissions, and test contracts; don't
omit essential work to fit. Update the estimate from evidence without claiming
oversized work or automatically removing its assignee.

**L+ is triage-only:** recommend independently useful S/M pieces or finite project
framing. No automatic children, parent execution, or large changes squeezed into
two PRs. Creation/splitting/project changes need applicable approval; approved
children qualify only after their own readiness checks.

## 3. Act on the disposition

| Result | Next action |
| --- | --- |
| Ready, selected | Confirm fields/plan and assignment; new work enters Todo, existing work resumes its lifecycle. Implement. |
| Ready, unselected | Keep queued without inventing a blocker. |
| Missing obtainable facts | Investigate within the assessment budget. |
| Consequential uncertainty | Ask the right person; use the interview for user decisions. |
| Likely stale | Review closure with the user. |
| Other-owned | Respect/report ownership; obtain handoff if appropriate. |
| Too large | Recommend a split/project and seek approval. |
| Dependency/access/permission blocked | Park with the exact blocker, owner, and resumption condition. |

Perform the smallest authorized follow-up; it needn't be a comment. Don't claim
work merely to leave a known hold. Reuse answers/defaults; ask current consequential
gaps without a lifetime question cap. Don't repeat unanswered asks or unchanged
reminders. Keep parked work visible, rechecking on new evidence or actionable
follow-up. If nothing useful can be done, explain the specific reason.

## 4. Implement and hand off

Work on one selected ticket; a newly discovered blocker doesn't authorize a second
build. Preserve partial work. Reuse owning branches/PRs; necessary two-PR outcomes
share acceptance criteria and the feedback window, and require combined validation.

Follow repository investigation, regression, checks, commit, and PR conventions.
Move implementing work to In Progress, then In Review on ready handoff; don't
round-trip resumed work through Todo. Keep PR links current. Create PRs Draft,
link the ticket, and explain intended behavior, approach, acceptance, and validation.
Honor protected-test approvals. Post one brief delivery comment linking all owning
PRs, verification, and remaining delivery steps.

Safe technical defaults can proceed during ordinary feedback. Explain a material
approach departure once with its reason and Draft PR link. Changed intended
behavior/scope or unsafe unknowns require approval before affected work.

**Feedback window:** Initial clarification questions or a material approach-review
notice start one 48-hour window from original server publication. Keep affected
PRs Draft until substantive feedback is incorporated or the window expires and
recorded safe defaults are applied. Edits, other PRs, and reruns don't reset it.
Recheck answers and verification before readying; never invent timestamps/defaults,
override human Draft holds, or let time bypass relevance, ownership, dependencies,
authorization, or tests. Without a feedback wait, verified complete work can be ready.

Before handoff, apply or explicitly resolve in-scope feedback; reading isn't applying.
Ready verified PRs and follow repository review-request policy. **The merge queue
owns ready PRs:** observe/report, without competing pushes, Draft reversions, or
review/CI/merge work. Route later findings through authorized channels; explicit
user direction can override. Merge, deployment, and operational acceptance differ.

## 5. Communicate and retain state

Use the current user's voice and [canonical writing guide](../../agents/writer.md#guide-location).
Comments lead with the outcome/needed response and next action, at most 100 words.
No interview provenance, workflow receipts, UUIDs, or hidden bookkeeping.

Once necessary decisions are settled, publish one cohesive plan: what I'll do,
why, what I need, and how we'll verify it. Update an existing plan where appropriate,
preserving useful discussion/approval evidence. Don't post each partial answer.
Necessary questions, material blocker changes, and delivery results may merit
separate comments; technical detail belongs in specifications/PR descriptions.

Private checkpoints at
`~/.codex/private/linear-ticket-workflow-state/<verified-issue-uuid>.json` are caches,
not authority (directory 0700, files 0600). Preserve fields and minimal source,
ask/decision, original feedback-time, next-action, and inventory/closure evidence;
keep assessed and applied feedback distinct. Recover stale/missing caches from
live sources. No private state in tickets/PRs/repo tracking files. Respect rejected
or approval-gated writes while continuing independent work; cache sync never
blocks the interview.

## 6. Report and interview

Every run, including unchanged/blocked runs, gives:

- One outcome sentence with screened/changed/build, open/recent-closed counts,
  and coverage limits; timing once when useful.
- Up to three result/intervention bullets, without repeating table notes.
- **Still in play:** Every tracked open ticket for the user or unresolved ownership,
  including unchanged holds and inventory-only rows.
- **Closed in the last 24 hours:** Native terminal transitions, retained from actual
  closure time, not PR merge/`updatedAt`. Keep unknown times separately unverified;
  reopened work returns to open inventory.
- **Owned by others:** Linked `<ticket> - owned by <owner>` entries for current
  exclusions and tracked open handoffs, without duplicating table rows.

Both tables: `Ticket | Status | Estimate | PRs | Action | Update/notes`.
Sort Action alphabetically (Skipped last), native status order, oldest creation
(unknown last; ID breaks ties). Link ticket IDs and PRs/states. Action is this run's
actual work; observed merges/closures are Assessed, inventory-only is Not assessed.
Notes give a brief disposition/evidence/next owner/action, or closure time. Use
unknown for unverified facts and — for verified none.

Reconcile live metadata/PR states without exceeding deep-assessment limits.
Keep tracked open work until verified closure or explicit tracking release;
reassignment alone isn't release. Label carried-forward findings and incomplete
recovery. Shorten prose, not required inventory; omit empty sections and routine
operational narration. Unrelated discovered candidates aren't a permanent watchlist.

### Continuing interview

Unless report-only, choose the most useful unresolved user decision/closure review
and investigate available facts first. Ask **one question per turn**, with numbered
choices, **(Recommended)** on choice 1, and brief tradeoffs. Apply to every question;
factual questions without meaningful alternatives can be direct. Use this contract
without invoking grill-me unless its policy permits or the user explicitly asks.
If no interview can help, give the evidence-backed reason; "no build," "already
interviewed," or a historical hold alone isn't sufficient.

**After every answer:** incorporate it, perform specifically authorized actions,
reassess the same ticket, and ask its next consequential question. An approved
write doesn't end the interview. Don't repeat decisions or jump between unfinished
tickets. When settled/parked, summarize the plan/exact dependency, publish the
cohesive comment if authorized, and offer numbered choices to review the next
ticket or finish. Recommend finishing when useful questions are exhausted.

Replies don't restart queue/build runs or reset budgets. Tracking approval isn't
implementation approval. Execute newly ready work only with remaining invocation
authority/budget or an explicit implementation request; otherwise keep it ready
for the next authorized run. Never invent questions to prolong the interview.
