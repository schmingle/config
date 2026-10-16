---
name: linear-ticket-triage
description: >-
    Prepare an eligible Linear ticket in the configured work queue for immediate
    implementation: validate its estimate, respect active engineering discussions and confirm stale-work
    takeover, ask only necessary product questions with safe defaults, and hand
    one suitable leaf to linear-ticket-build in the same invocation.
disable-model-invocation: true
---

# Linear Ticket Triage

Prepare one Medium-or-smaller ticket on the current user's behalf. Do not
implement it or edit repository files. Hand implementation to
[linear-ticket-build](../linear-ticket-build/SKILL.md); unanswered questions with
safe defaults must not delay that handoff once the ownership gate below is clear.

A user-authorized invocation of this skill also explicitly requests
[linear-ticket-build](../linear-ticket-build/SKILL.md) for one eligible leaf in the
same invocation. Do not ask the user to invoke build separately. Triage prepares
the ticket; build owns code, verification, and the PR. Share one ticket budget.
Posting a new ownership or exceptional blocking question consumes that budget and
ends the run; never fan out new questions across the backlog. Existing pending
asks are quiet skips and do not consume it.
Either skill may be invoked manually or by an existing user-authorized periodic
run. Do not create an automation or promise a background follow-up.

## Private workflow settings

Before accessing the queue, read `~/.codex/private/linear-ticket-workflows.json`.
It must supply `team` (the exact Linear team key), `repository` (the GitHub
`owner/repository`), `triageCreatorEmails` (the nonempty exact creator allowlist),
`maxEstimate` (the numeric upper bound), and `mediumEstimateLabel` (the scale label
used as Medium below). Resolve these values from that private file only; never
copy them into this skill or public configuration. Verify the intended authenticated
Linear workspace, team/estimate scale, and repository against those settings.
If the file or any required value is missing, invalid, or cannot be verified,
stop before ticket mutations and report the configuration blocker. Never guess
settings, substitute the current repository/team, or broaden queue filters.

## Identity and authorization

Resolve the current user through the authenticated Linear connector's current-user
lookup (`get_user` with `query: "me"`, or the equivalent available tool). Alternatively, resolve an explicit Linear identity or reuse an identity
already explicitly confirmed in this conversation. Use the resulting Linear user
ID for assignee, creator, and estimate-history comparisons. Never infer identity
from the OS account, Git, repository history, or an unrelated conversation.
Ask for identity only when it cannot be resolved unambiguously.

Invoking this skill authorizes its normal Linear comments, assignment, estimate,
and status changes, plus the build handoff and implementation PR work within this
scope. No separate approval or `auto` keyword is required. Honor an explicit
read-only or dry-run request: inspect and report the proposed actions without
mutations or build execution.

Before each mutation, re-fetch every affected issue and recheck eligibility,
ownership, blockers, new discussion, and linked-PR activity. Material changes
require reassessment under the gates below, not a routine approval stop. This
authorization does not cover merging, deployment, production changes, or other
communication channels. Email, SMS, and Slack retain their preview-and-confirm
gates under applicable `AGENTS.md` guidance.

## Resume prior workflow work

Before selecting new work, inspect the current user's previously managed leaves
in the configured team in Todo, In Progress, or In Review and their linked PRs.
Require a traceable
Linear/PR handoff from this workflow with the bounded scope, verified ownership,
and estimate; assignment or status alone is not eligibility. Re-fetch replies,
edits, blockers, and PR state. Prefer an actionable answer, scope change, or
48-hour readiness transition, then hand that one ticket to build using its
[existing-work path](../linear-ticket-build/SKILL.md). This consumes the same
one-ticket build/update budget as a new selection.

Preserve unresolved ownership holds and check for actual reassignment or newer
conflicting ownership. Do not reapply the new-work seven-day participation veto
to ordinary reviews on the current user's recorded implementation PR. An
unchanged ticket waiting before its deadline is a quiet skip; continue the queue
so waiting work does not starve new candidates. This continuation path does not
broaden the creator filter for new work below.

## Candidates

Process newest `updatedAt` first. Paginate until a candidate is selected or the
eligible set is exhausted; do not report no work from one page. Paginate relevant
comments and relations before deciding suitability or whether feedback is new:

```text
team = settings.team
status in (Triage, Backlog)
assignee in (none, current user)
creator in settings.triageCreatorEmails
estimate = unset or Medium-or-smaller (at most settings.maxEstimate)
```

Resolve the configured creators by exact email and compare user IDs. Skip tickets
already estimated above Medium. Read existing questions and answers; do not repost
questions or skip an otherwise suitable ticket merely because answers are pending.
Only after the ownership gate is clear, if a linked PR already exists, hand off
to build to update it rather than creating a second implementation.

## Ownership gate

Target up-for-grabs work and confirm stale-work takeover. For new selections,
apply this gate before any ticket field change (including an oversized estimate),
normal triage comment, or linked-PR handoff. Recorded prior-work continuations
use the ownership checks in Resume prior workflow work above. Check a parent
before selecting its direct child, then check the child's own discussion and linked PRs too; a child cannot bypass an
unresolved parent ownership gate. The assignee filter above always applies:
assignment to another engineer excludes the issue even when stale or a takeover
is offered.

Read all comments, replies, and available linked-PR conversation, code activity,
and reviews. Identify another engineer's actual participation using available
people/role context; a mention, bot comment, or configured-team membership alone
does not establish engineer participation. If participant identity, discussion coverage,
or activity cannot be established reliably, skip with the reason.

Use server timestamps and a current evaluation time. Latest activity is the
maximum of issue `createdAt`/`updatedAt`, every comment/reply's creation/update,
and available linked-PR conversation, code, and review timestamps. **Active** means
any activity at or after `now - 7 * 24 hours`, including the cutoff; **stale** means
all activity is older. Count activity from anyone, including bots and people who
are not engineers; engineer participation and activity recency are separate checks.

- **No other engineer involved:** continue normal triage.
- **Another engineer involved and active:** skip without comments, field changes,
  or build handoff; report the engineer and latest activity as the reason.
- **Another engineer involved and stale:** post one top-level Linear comment:
  “Do we still want to address this? If so, shall I take this?” Mention the involved
  engineer and requester when useful.
  Hold all field changes and build handoff pending an explicit affirmative
  confirmation that the work is still wanted and the current user may take it.

An explicit affirmative takeover/handoff from the involved engineer or requester
can clear this gate even though that reply itself makes the issue active. Re-read
the full discussion for newer conflicting ownership or scope before continuing;
an ambiguous reply, renewed engineering discussion, or another engineer retaining
ownership does not clear it. Other eligibility checks still apply.

Reuse an existing equivalent takeover question and its replies on later
invocations; never repost it or add a reminder. Check the quiet-run gate below
before posting a new ownership question. A pending question remains a hold
even when the question itself is recent activity. This is an ownership permission
check, separate from the three product questions: silence, safe defaults, skill
invocation, and the product questions' 48-hour deadline never authorize claiming,
assigning, moving to Todo, or invoking build. Once confirmed, retain the question
and affirmative reply links in the Linear handoff so later invocations can verify
that ownership was cleared.

## Assess

For each candidate:

1. Read the issue, comments, attachments, relations, estimate history, and direct
   sub-issues, then apply the ownership gate before proceeding.
2. Inspect the configured repository’s relevant code, tests, schemas, history, and
   applicable `AGENTS.md` files. Run `nvm use` first. Investigation is read-only.
3. Trust an existing estimate only when the current user set it. Otherwise
   estimate from product impact, implementation complexity, and risk using the
   configured team’s estimate scale. If estimate authorship is unavailable, assess
   it rather than claiming it was verified.
4. If larger than Medium, set the estimate (propose it in read-only mode), make
   no other ticket change, and continue.
5. For Medium-or-smaller parents with eligible direct sub-issues, triage the
   newest eligible child whose ownership gate is also clear. Consider relevant
   parent discussion as well as the child's own activity and ownership. The creator
   filter applies only to the parent. Never move a parent to Todo.
6. Assess Medium-or-smaller leaves for a bounded implementation and objective
   verification path.

A suitable leaf fits roughly one reviewable PR and can be implemented safely
using explicit defaults for unanswered product questions. Missing permission,
required data, an unfinished prerequisite, or a decision with no safe bounded
default remains a blocker. Do not force such work into Todo or treat silence as
authorization. If more than three unresolved decisions prevent a coherent bounded
implementation, narrow the scope or leave it in triage with the blocker explained.

## Questions and defaults

This is the shared clarification contract for triage and build for the lifetime
of the same bounded ticket. Read all historical comments and replies, including
legacy questions in any format, before asking anything. Reuse relevant answered
context from related tickets too; a different issue does not justify asking a
known decision again. Count prior product questions toward the shared budget;
invocation, edits, partial answers, missing metadata, and a move between skills never reset it.

Post **one initial product-question comment at most**, containing no more than
**three meaningful questions in total across both skills**. Ask fewer or none.
Ask only when the answer changes observable behavior and is not already known;
avoid compound questions and low-level implementation choices. If questions were
already asked, reuse their decisions, answers, defaults, and original timestamp
without posting another question set or filling unused slots later.

Write as the current user: friendly, direct, concise, and human. Follow applicable
writing guidance. Never identify the comment as agent-generated or use a templated
heading. Number questions with mutually exclusive lettered choices; A is the safe
default and the only option labeled `[Recommended]`. Invite a compact reply such
as `1A, 2C`; add `Other — please specify` only when useful.

```text
1. <question that changes observable behavior>
   A. [Recommended] <safe default to implement now>
   B. <alternative>
```

State that implementation proceeds immediately with these defaults. An initial
unanswered question set keeps the PR Draft until a reply settles the assumptions
or 48 elapsed hours after the original question `createdAt`. Build may then mark
a verified PR ready on that invocation; time alone never substitutes for its
verification and readiness checks. Do not imply an automatic wake-up or merge.

Honor clear parts of any reply and infer reasonable intent for partial or
ambiguous parts. Record the best-supported assumptions in the implementation
plan/PR; **do not ask a routine follow-up**, repeat a question, send a reminder or
ping, or notify people about question edits. A thanks or status question alone is
not a substantive answer. After the first substantive reply/answer, exhaustion of
the question budget, expiration of the original 48-hour deadline, or a declined
clarification, settle ordinary questions using answers and safe defaults. Silence
at the deadline has the same result. Exhausting the question budget forbids more
questions; it does not shorten the fresh unanswered set's Draft window. Later
replies may change the implementation but do not reopen ordinary questioning.
An old ambiguous follow-up is historical context, not evidence of a new risk.

For legacy questions without recorded defaults, choose and record safe assumptions
now without a new timer or ordinary question. Reuse known original timestamps;
never invent missing timestamps or claim an unverified deadline has elapsed.
Missing timestamp evidence alone is not proof that a PR can leave Draft.

Only **new evidence of a material risk** that is unsafe without authorization,
required data, or permission, or an explicit user reopening of that risk, can
justify one precise blocking ask. Persist a stable fingerprint of the risk,
bounded scope, and latest supporting source IDs alongside the ask ID and
resolution. On later invocations, an unresolved identical blocker is a quiet skip,
not another ask. Routine edits, ambiguous replies, and the skill's own comment
`updatedAt` are not new evidence. Reassess genuinely new scope or risk without
automatically opening another product-question round.

## Durable handoff and quiet runs

Keep a minimal durable handoff in Linear and the implementation PR, never repository
tracking files. Reuse an existing record and change it only for substantive new
information. Include:

- Workflow provenance, verified owner/estimate, bounded scope, acceptance criteria,
  answers/defaulted assumptions, and the original question-comment ID/link,
  `createdAt`, and deadline (`createdAt` + 48 elapsed hours), when known. Omit
  question metadata when none were asked; mark missing evidence explicitly.
- Processed reply IDs with their `updatedAt`, and clarification state: `open`,
  `settled` (answered/defaulted), or `blocked`. Preserve the state across runs.
- Ownership-ask IDs/links and their resolution; any exceptional blocking-ask
  fingerprint, source IDs, ask ID, and resolution.

On every invocation, re-fetch and read replies, comparing their IDs and `updatedAt`
with the durable record. For previously recorded tickets, if there are no new
requirements or actionable state changes, take no action and continue the eligible
queue. A fresh eligible candidate can still receive its initial plan/handoff
without a recent requirements change. Do not
post acknowledgements, reminders, unchanged plans, repeated questions, or edit
notifications. A pending ownership or material-risk ask follows this same quiet
gate. The skill's own comment update alone must never trigger another question.

Post only the initial combined plan/questions and one PR-delivery comment as
routine updates. Later updates require substantive code, decision, readiness, or
blocker changes; combine related updates into one comment. Persist processed-reply
state in the existing handoff/PR without a separate acknowledgement comment.

## Finish triage immediately

For a suitable leaf whose ownership gate is clear, without waiting for product
answers:

1. Re-fetch every blocker before any handoff fields, comments, or deadline are
   recorded. Continue only when all are Done; otherwise skip without preparing
   the ticket. Recheck duplicate, obsolete, and bounded-scope eligibility too.
2. Set or confirm its Medium-or-smaller estimate, and assign it to the current
   user if unassigned.
3. Reuse the existing plan/questions and answers, or post the single initial
   combined approach/questions comment when needed. Record the bounded scope,
   acceptance criteria, and durable handoff above without redundant updates.
4. Move it to Todo last, then invoke build immediately for this same leaf. Pass
   its issue ID, verified ownership/estimate/blockers, handoff state, and any
   existing PR. A linked implementation PR must be updated rather than duplicated;
   for that continuation, an explicitly verified owner/estimate handoff may bypass
   Todo, with the reason and existing PR passed to build.

Never change priority. Never move oversized, unsuitable, duplicate, obsolete,
parent, blocked, or ownership-held tickets to Todo. Defaults and elapsed time do
not override those limits. Build owns implementation, subsequent answers, and PR
readiness in this invocation and later authorized invocations.

Report the issue, estimate evidence, actual comment action/link, assumptions,
readiness, resulting assignee/status, and build's verified PR outcome. Include
ownership skips/pending confirmation with activity/comment links and newer
oversized candidates assessed. For open questions, give the known deadline
without promising automatic promotion. In explicit read-only mode, label actions
as proposed and do not execute the handoff.
