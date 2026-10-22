# Linear Ticket Build Pass

Implement one independently sized Large-or-smaller leaf issue in the configured
work queue on the current user's behalf, following triage’s [work routing](triage.md#work-routing). Build
bounded bugs and one-offs immediately using documented defaults instead of waiting
for clarifying answers. Never merge its PRs unless explicitly asked.

Run after the triage pass in the explicitly invoked combined workflow. Select
only from that pass's verified buildable candidate list. Implement or
substantively update at most one ticket in this pass.
Do not create or edit automations, sleep until the deadline, or promise a
background follow-up. Recheck answers and deadlines during this run. Time passing
alone does not change a PR between invocations.

## Shared settings and identity

Use the [private workflow settings](triage.md#private-workflow-settings) and
[identity rules](triage.md#identity-and-authorization) established in triage.
Recheck the intended workspace, team, repository, and current user before build
mutations; do not infer identity from the OS account or Git.

## Build authorization

The combined invocation authorizes one eligible bounded ticket's implementation,
Linear plan/comments, estimate, assignment, and status changes, branch, commits,
pushes, PR creation or updates, Draft/ready transitions, and reviewer requests.
Start with known context and safe defaults; do not stop for routine approval or
require `auto`. Accept `auto` as a compatibility alias for this same scope.
Honor an explicit read-only or dry-run request by proposing changes only.

Before each mutation, re-fetch the issue and its owning PRs. Adapt to material
changes within the authorized scope; stop for missing authorization, an unfinished
prerequisite, a material risk with no safe default, or work outside the bounded
route. This workflow does not authorize merging, auto-merge, deployment, production writes, or email, SMS, or
Slack messages. Draft status and elapsed time never bypass these gates.

## Candidates

Use only the triage-produced buildable list; do not independently scan assigned
issues. Prefer actionable new feedback/edits, a due deadline, or a verified
interrupted In Progress build, newest `updatedAt` first within that tier. Then
prefer the newest
eligible prepared Todo ticket. Re-fetch the selected candidate and paginate its
comments, relations, and PR feedback before deciding readiness or whether
feedback is new. Recheck these underlying filters:

```text
team = settings.team
status in (Todo, In Review), or verified interrupted In Progress
assignee = current user
verified creator != current user, or verified authorized decomposition child
estimate is independently set and at most settings.maxEstimate (Large on the live team scale)
leaf issue
```

The same creator rule governs both passes: exclude self-created tickets except
verified native children of an eligible parent created by this workflow's
[authorized decomposition](triage.md#large-ticket-decomposition). A parent link or
self-created child alone is insufficient; verify the live parent, original
requester and outcome, decomposition evidence, and the child's own ownership
and eligibility. Any other verified creator may qualify; an unverifiable creator
is a skip. Cleanly decomposable Large work must first be split during triage;
select one prepared eligible child. A coherent Large leaf that cannot be cleanly
split may build within the same one-ticket budget. Confirm the issue was
triaged by this workflow from this run's completed preparation or prior live
plan, native field history, discussion, and linked PR evidence, with the private
checkpoint as an
optional aid. For prior work, verify the current user's plan/defaults against
native estimate, assignment, and Todo history or corroborating linked PR evidence
to establish the bounded handoff. A generic issue description, assignment,
status, or checkpoint alone is insufficient. Keep unprepared, oversized,
blocked, held, project-shaped, unresolved-routing, unsuitable, duplicate, or
no-safe-default tickets out of the buildable list.

Read the issue, comments, attachments, relations, sub-issues, and linked PRs.
If any blocker is not Done, use the build pass's one-ticket budget and stop.
With no open owning PR, move the issue to Backlog and make no other change. With
open owning PRs, preserve the issue’s status and PRs; keep affected Draft PRs Draft,
or convert affected ready PRs to Draft because the prerequisite prevents their
completion. Record a newly material blocker in affected PR descriptions and one
issue update; unchanged reruns remain quiet. Do not create a replacement PR or
claim the work is ready. Skip duplicate, obsolete, unsuitable, or
already-complete work. An existing Draft PR awaiting questions or material
approach feedback is eligible for checking replies or its original deadline;
do not skip it merely because no new reply exists.
On a general queue invocation, if no owning PR or unfinished part of the ticket
needs action and its feedback deadline has not arrived, continue to the next
candidate after checking it.
An explicitly selected ticket may simply report that no action is due yet.

An explicitly build-scoped issue may be selected only if triage verified it for
the buildable list. A prior handoff is source context, not automatic eligibility
or priority. A verified prior workflow issue may resume Todo, In Progress, or
In Review work with actionable new feedback/edits, a due deadline, or verified
unfinished implementation. Recover an
interrupted In Progress build without a private checkpoint when live source
evidence establishes the current user's bounded plan and ownership, plus the
user's In Progress transition if no branch/PR exists, or the owning branch and
commits tied to the issue or owning PR with its issue link when one exists.
Triage may include such a verified issue in its list; build never starts a
broad In Progress scan. Check linked PRs before
starting; reuse the owning branches and PRs and never duplicate an implementation.
Current eligibility, ownership holds, and the one-ticket build cap still apply.

Ownership must remain clear. Recheck current assignments, directed ownership,
holds, and authoritative handoffs using the relevant issue, Slack, and PR source
evidence under triage's [ownership gate](triage.md#ownership-gate). Stop affected
implementation if newer evidence directs the work elsewhere. Do not reapply
triage's other-engineer participation veto to ordinary review feedback on an
existing implementation PR already owned by the current user.

Honor applicable `AGENTS.md` files and inspect relevant code, tests, schemas, and
history. Run `nvm use` before checks. Confirm the estimate still fits, the work
has objective acceptance criteria, and any unanswered decision has a safe bounded
default. Missing permission, required data, or a decision with no safe default
remains a blocker; do not guess to force implementation or promotion. Recheck
[work routing](triage.md#work-routing) for the complete ticket before implementation.
If new evidence reveals project-shaped work or unresolved routing, preserve partial
work and stop broader implementation. Record only the material proposal or specific
gap under triage’s routing, comment, and ask-budget rules; keep affected open PRs
Draft where their scope cannot be completed safely. Do not create or modify a
project, start broader execution, or create an automation. This selected ticket
still consumes the one-ticket build budget.

## Questions and plan

Use triage's [independent approach and sizing](triage.md#independent-approach-and-sizing)
for bugs and specific requests. Revalidate the approach against code and the
requested outcome; update its estimate and concise plan when evidence changes.
Explain material implementation departures to the requester once, with the
reason and a link to the Draft PR, inviting feedback without requiring routine
acknowledgement. Safe technical defaults may proceed; changes to expected
behavior, permissions, compatibility, approved scope, or protected tests require
the applicable approval, and unsafe unknowns remain blocked. Keep affected PRs
Draft under the same feedback clock as clarifying questions. Decomposition does
not reset existing questions, answers, holds, or clocks for the same decision.

Follow the shared [comment style](triage.md#comment-style),
[questions and defaults](triage.md#questions-and-defaults), and
[private checkpoint/quiet-run contracts](triage.md#private-checkpoint-and-quiet-runs).
Keep all machine bookkeeping private under that contract.
Use one initial set of at most three meaningful questions for the bounded ticket
across both passes. Recover legacy question comments, thread IDs, answers,
timestamps, and defaults before posting. A separate invocation is
not a new question budget. If no initial set exists, build may ask within that
budget while implementing safe defaults immediately.

Infer ordinary ambiguity from available context. After a reply, the original
48-hour deadline, or exhaustion of the question budget, stop ordinary questioning;
record assumptions in the plan and PR instead. Only a truly new material risk
that cannot safely proceed without authorization or required data permits one
precise blocking ask under the canonical contract. Keep its fingerprint and source
references in the private checkpoint, and quietly skip unchanged later invocations;
timeout never supplies that permission.
A new ownership or risk ask consumes the build pass's one-ticket budget; stop
without asking across other candidates. If triage already posted the combined
invocation's one allowed new ownership or exceptional blocking ask, do not post
another; report the blocker and stop this pass.

Follow the shared comment limits: lead with user impact and next action, and
include only a material decision/default, question, or blocker. Put technical
rationale and validation detail in the repository-required PR description, linked
from the ticket. Never repeat the ticket or append a workflow/metadata inventory.

Reuse a triage plan or existing question set; otherwise post one concise initial
plan and any questions, then implement immediately.
Pending answers alone must not stop implementation. Questions with no safe
bounded default must be reported as blockers instead.

## Route by status

### Todo

Re-fetch the issue and all owning PRs. Move to In Progress and implement the plan
using the documented defaults. Reuse the existing plan, branches, and open PRs when
present. The same route resumes recorded partial In Progress work.

### In Review

Inspect all owning PRs, reviews, checks, and Linear comments since the latest
recorded implementation update, including edits to previously processed comments.

- Ignore generic acknowledgements and status questions. Explicit requester
  agreement with a material approach settles that review even without a code
  change; a generic thanks does not.
- Incorporate in-scope requester answers and requested changes into one concise
  plan update. Move to In Progress only when implementation needs revision;
  update the affected existing branches and PRs, then rerun relevant checks.
- Assess substantive third-party suggestions on their merits. Implement clear
  ordinary code defects within scope. For ordinary product ambiguity, retain the
  recommended default and document the assumption without asking the requester
  again. A suggestion alone does not authorize expanding product behavior.
- For partial, ambiguous, or conflicting replies, settle ordinary details using
  safe assumptions and keep the original clock. Apply the canonical blocking-ask
  gate only to a new material risk with no safe authorized path; keep unfinished
  work Draft rather than treating timeout as approval.
- If only a deadline or PR-readiness update is needed, keep the issue In Review;
  do not manufacture a code change or status round trip.

Process late answers even after timeout promotion, applying in-scope changes to
the affected open owning PRs. Revalidate those PRs; do not reopen a merged or
closed PR or create replacement work without authorization.

## Implement and verify

Preserve unrelated changes and keep the implementation diff minimal. Add needed
regression coverage first, then implement the fix in the same PR.
Follow the repository's test contract change gate when protected behavior changes;
a recommended default does not replace any required explicit approval. Run checks
proportional to risk and fix failures caused by the work before publishing.

After a push, re-fetch the issue, owning PRs, and comments. Incorporate newer in-scope
answers before declaring completion. Record processed reply IDs and `updatedAt`
values privately, including edited comments, only after their implementation or
documented no-code disposition is complete. Compare replies with build's applied
state, not triage's assessed/seen state: a triage assessment does not mean the requested
change has been applied. Reuse legacy processed-reply records only when prior
implementation/disposition evidence supports that meaning. Leave unapplied work
pending so queued feedback cannot be silently skipped.

## Branches and PRs

Prefer a one-to-one mapping between implementation tickets and focused PRs. If a
bounded outcome needs two PRs, follow triage’s
[decomposition rules](triage.md#large-ticket-decomposition) for the authorized
split of cleanly decomposable Large work. Other ticket creation or splitting
still needs its own authorization. Do not build multiple children under one
selected ticket's budget or bypass screening.

Preserve existing multi-PR work. A necessary exception may still use two PRs for
the same complete bounded ticket; state the scope rationale and why the one-to-one
preference cannot reasonably be applied. Keep each PR’s contribution to the
acceptance criteria clear, link both from the issue, and verify their combined
result. The ticket counts once toward the build budget. Do not call it complete
after only one part; two PRs are not a quota.

Create each new implementation PR as Draft while work is underway; the readiness
rules below govern the handoff. Follow the repository’s branch, commit, push,
and PR workflow. Use the Linear ID
in new Todo branches when practical; reuse owning branches and PRs for revisions.
Default each PR to an independent base; stack only for a concrete prerequisite
required by the repository’s dependency rules, with actual ancestry and GitHub base.

Apply the following PR requirements to each owning PR, including its feedback,
blockers, verification, readiness, and reviewer requests. Share the ticket's existing question set, material approach-review notice,
defaults, original 48-hour feedback clock, and ask budget across both PRs; opening a second PR never resets them. A scoped PR may be ready while
another remains Draft, but incomplete combined work is not ticket completion.

Title each PR `<issue identifier>: <concise title>`. Follow the repository’s
description requirements, including the issue, solution, acceptance criteria,
and test plan and results. Include material defaults and unresolved questions
when relevant; link the original question comment instead of repeating it. A useful readiness
deadline may be a readable date/time with timezone. Keep original timestamps,
reply watermarks, provenance, holds, and other machine state in the private
checkpoint, never in human-facing PR text or hidden HTML/JSON blocks. Do not
create repository tracking files or a new question round to normalize old records.

Both Draft and ready-for-review PRs are open on GitHub; use `isDraft` to distinguish
them. Choose or update readiness after implementation and verification:

| Requester feedback | PR readiness |
| --- | --- |
| No questions or material approach departure needing feedback | Open, ready for review after implementation and verification |
| Initial questions or material approach-review notice unanswered and less than 48 hours elapsed | Open, Draft |
| Meaningful feedback incorporated; remaining ordinary ambiguity settled with safe assumptions | Open, ready for review after verification |
| At least 48 hours elapsed; answered choices honored and safe defaults applied | Open, ready for review, subject to the gates below |

Track why the workflow made a PR Draft. Do not promote a human-held Draft or
override an explicit request to wait, including a hold on an already-ready PR.
Request one or two GitHub reviewers when marking ready, based on CODEOWNERS,
meaningful authorship, and package ownership. Never request the current user.
Do not repeatedly request review on unchanged ready PRs.

## Follow-up and 48-hour promotion

On each invocation that selects a ticket with existing owning PRs:

1. Re-fetch the issue, all owning PRs, original question or material approach-review
   thread, replies, and blockers. Read all answers before considering timeout.
   Use server timestamps and 48 elapsed hours from the original feedback comment;
   edits, follow-ups, and routine updates do not reset it.
2. Apply explicit answers and settle ordinary remaining ambiguity with safe
   assumptions. At the deadline, use recorded defaults for unanswered items.
   Partial replies need not keep the PR Draft when the decision set can safely
   be settled; they never reset the deadline or discard choices already made.
3. Revise the plan, code, tests, and affected descriptions where needed. Confirm
   each PR and their combined outcome match the completed decision set. An answer
   that confirms the implementation needs no artificial commit.
4. Mark each PR ready only when its scoped implementation is complete, applicable
   verification passes, blockers are Done, and no unresolved safety or
   authorization constraint or explicit hold remains. Elapsed time clears
   the ordinary unanswered-question or approach-feedback wait only; it never
   overrides these gates or supplies missing approval. Record any gate that
   prevents promotion instead of claiming readiness.
5. If initial questions or the material approach-review notice remain unanswered
   before the original deadline, keep affected PRs Draft. Recover the original
   feedback clock; if already expired,
   apply their defaults and mark verified work ready now, without a fresh Draft
   waiting period.
   Never fabricate a historical timestamp/default or claim elapsed time without
   evidence. Choose and record a safe assumption now to settle an ordinary
   decision without reopening questions. Failed or incomplete verification always
   prevents readiness.

No additional routine approval is needed. Inspect all new feedback, including
edits, before deciding no action is due. On an unchanged rerun, make no external
comments, notifications, commits, or repeated reviewer requests. Continue the
queue if the selected ticket needs no action. Check again only on a later invocation.

## Finish and report

When new work or a meaningful update is complete and all owning PRs together
deliver the ticket’s acceptance criteria using current answers or recorded defaults:

1. Move the issue to In Review, including when an owning PR remains Draft for
   questions or approach feedback.
2. Post one delivery comment within the shared 100-word maximum: link all owning PRs,
   state the user-visible result, one useful combined verification summary, and each
   PR’s Draft/ready state using confirmed choices/defaults. Invite
   optional feedback without requiring acknowledgement.
   Mention only the requester; for an authorized decomposition child, inherit
   the original requester from the parent/source instead of treating the child's
   automation author as requester. GitHub handles reviewer requests. Reuse an existing
   delivery comment instead of posting it again on a later unchanged run.
3. Keep the private checkpoint current without publishing it. Combine substantive
   answer, implementation, readiness, or blocker changes into one short update;
   do not post per-push updates, reminders, or unchanged blocker pings.

For partial delivery, preserve the issue’s In Progress status and report the
remaining acceptance criteria without claiming completion. On later revisions to
work already In Review, use the existing status-routing rules.

Report the actual issue ID and all owning PR links, complete or partial
user-visible outcome, combined verification summary, each PR’s Draft/ready/landed state, and any material
blocker or next action concisely. Include a readable question deadline only when
useful; omit raw bookkeeping and routine field lists.
State that another invocation is needed for future replies or promotion;
do not claim that a follow-up was scheduled.
