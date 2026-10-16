---
name: linear-ticket-build
description: >-
    Implement an eligible Linear ticket in the configured work queue immediately
    using explicit defaults, publish a Draft PR while initial answers are pending
    or a ready PR otherwise, and process answers or a 48-hour timeout on later
    invocations. Requires its own explicit user or authorized automation invocation;
    never invokes triage.
disable-model-invocation: true
---

# Linear Ticket Build

Implement one Medium-or-smaller issue in the configured work queue on the current
user's behalf. Build immediately using documented defaults instead of waiting for
clarifying answers.
Never merge its PR unless explicitly asked.

Run only when independently invoked explicitly by the user or by an existing
user-authorized automation. A triage invocation or persisted handoff is context,
not authorization to run build. Never invoke triage as part of this workflow.
Implement or substantively update at most one ticket per invocation.
Do not create or edit automations, sleep until the deadline, or promise a
background follow-up. Recheck answers and deadlines during this run. Time passing
alone does not change a PR between invocations.

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
ID for assignee and creator comparisons. Never infer identity from the OS account,
Git, repository history, or an unrelated conversation. Ask only when identity
cannot be resolved unambiguously.

Normal invocation authorizes one eligible bounded ticket's implementation,
Linear plan/comments, estimate, assignment, and status changes, branch, commits,
pushes, PR creation or updates, Draft/ready transitions, and reviewer requests.
Start with known context and safe defaults; do not stop for routine approval or
require `auto`. Accept `auto` as a compatibility alias for this same scope.
Honor an explicit read-only or dry-run request by proposing changes only.

Before each mutation, re-fetch the issue and linked PR. Adapt to material changes
within the authorized scope; stop only for missing authorization, an unfinished
prerequisite, or a material risk with no safe default. This workflow does not
authorize merging, auto-merge, deployment, production writes, or email, SMS, or
Slack messages. Draft status and elapsed time never bypass these gates.

## Candidates

Process newest `updatedAt` first. Paginate until a candidate is selected or the
eligible set is exhausted; do not report no work from one page. Paginate relevant
comments, relations, and PR feedback before deciding readiness or whether feedback
is new:

```text
team = settings.team
status in (Todo, In Review)
assignee = current user
creator != current user
estimate is set and Medium-or-smaller (at most settings.maxEstimate on the configured team scale)
leaf issue
```

Read the issue, comments, attachments, relations, sub-issues, and linked PRs.
If any blocker is not Done, move the issue to Backlog, make no other
change, and continue. Skip duplicate, obsolete, unsuitable, or already-complete
work. An existing Draft PR with unanswered questions is eligible for checking
answers or its deadline; do not skip it merely because no new reply exists.
On a general queue invocation, if a PR has no actionable new feedback and its
deadline has not arrived, continue to the next candidate after checking it.
An explicitly selected ticket may simply report that no action is due yet.

On this independent invocation, honor an explicitly selected issue or persisted
workflow handoff before scanning for new work. A handoff may come from an earlier
run; re-fetch and validate its issue, ownership, estimate, blockers, discussion,
and linked PR rather than requiring a same-invocation transfer. Preserve the
queue filters above, including the recorded parent-selection/child-creator
exception: verify that selection and ownership decision rather than selecting a
different candidate. A verified existing workflow record may resume Todo,
In Progress, or In Review work with actionable new feedback/edits or a due deadline.
This consumes the same one-ticket budget; do not also select new work. Resume
In Progress work only through its known owning workflow record. Check linked PRs
before starting; reuse an open owning PR and never duplicate an implementation.
These exceptions do not authorize an unbounded review queue. A handoff never
bypasses current eligibility, ownership holds, or this skill's separate invocation
requirement.

Ownership must be clear. Honor recorded ownership holds and takeover decisions.
Do not reapply triage's other-engineer active-discussion gate to review feedback
on an existing PR already owned by the current user.

Honor applicable `AGENTS.md` files and inspect relevant code, tests, schemas, and
history. Run `nvm use` before checks. Confirm the estimate still fits, the work
has objective acceptance criteria, and any unanswered decision has a safe bounded
default. Missing permission, required data, or a decision with no safe default
remains a blocker; do not guess to force implementation or promotion.

## Questions and plan

Read only the shared [comment style](../linear-ticket-triage/SKILL.md#comment-style),
[questions and defaults](../linear-ticket-triage/SKILL.md#questions-and-defaults), and
[private checkpoint/quiet-run contracts](../linear-ticket-triage/SKILL.md#private-checkpoint-and-quiet-runs)
as reference material; this is not an invocation of triage and does not load its
execution steps. Keep all machine bookkeeping private under that contract.
Use one initial set of at most three meaningful questions for the bounded ticket
across both skills. Recover legacy question comments, thread IDs, answers,
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
A new ownership or risk ask consumes this run's one-ticket budget; end the run
without asking across other candidates.

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

Re-fetch the issue and any linked PR. Move to In Progress and implement the plan
using the documented defaults. Reuse the existing plan, branch, and open PR when
present. The same route resumes recorded partial In Progress work.

### In Review

Inspect the existing PR, reviews, checks, and Linear comments since the latest
recorded implementation update, including edits to previously processed comments.

- Ignore acknowledgements, status questions, and feedback that requests no
  product or implementation change.
- Incorporate in-scope requester answers and requested changes into one concise
  plan update. Move to In Progress only when implementation needs revision;
  update the existing branch and PR, then rerun relevant checks.
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

Process late answers even after a timeout promoted the PR, provided it remains
open and the changes are in scope. Revalidate and update that PR; do not reopen a
merged or closed PR or create replacement work without authorization.

## Implement and verify

Preserve unrelated changes and keep the implementation diff minimal. Add needed
regression coverage first, then implement the fix in the same PR.
Follow the repository's test contract change gate when protected behavior changes;
a recommended default does not replace any required explicit approval. Run checks
proportional to risk and fix failures caused by the work before publishing.

After a push, re-fetch the issue, PR, and comments. Incorporate newer in-scope
answers before declaring completion. Record processed reply IDs and `updatedAt`
values privately, including edited comments, only after their implementation or
documented no-code disposition is complete. Compare replies with build's applied
state, not triage's assessed/seen state: a triage assessment does not mean the requested
change has been applied. Reuse legacy processed-reply records only when prior
implementation/disposition evidence supports that meaning. Leave unapplied work
pending so queued feedback cannot be silently skipped.

## Branch and PR

Follow the repository's branch, commit, push, and PR workflow. Use the Linear ID
in a new Todo branch when practical; reuse the owning branch and PR for revisions.
Default to an independent PR; stack only for a concrete prerequisite required by
the repository's dependency rules.

Title the PR `<issue identifier>: <concise title>`. Follow the repository's description
requirements, including the issue, solution, acceptance criteria, and test plan
and results. Include material defaults and unresolved questions when relevant;
link the original question comment instead of repeating it. A useful readiness
deadline may be a readable date/time with timezone. Keep original timestamps,
reply watermarks, provenance, holds, and other machine state in the private
checkpoint, never in human-facing PR text or hidden HTML/JSON blocks. Do not
create repository tracking files or a new question round to normalize old records.

Both Draft and ready-for-review PRs are open on GitHub; use `isDraft` to distinguish
them. Choose or update readiness after implementation and verification:

| Questions | PR readiness |
| --- | --- |
| No questions posted | Open, ready for review |
| Initial questions unanswered and less than 48 hours elapsed | Open, Draft |
| Meaningful answers incorporated; remaining ordinary ambiguity settled with safe assumptions | Open, ready for review |
| At least 48 hours elapsed; answered choices honored and defaults applied to remaining questions | Open, ready for review, subject to the gates below |

Track why the workflow made a PR Draft. Do not promote a human-held Draft or
override an explicit request to wait, including a hold on an already-ready PR.
Request one or two GitHub reviewers when marking ready, based on CODEOWNERS,
meaningful authorship, and package ownership. Never request the current user.
Do not repeatedly request review on unchanged ready PRs.

## Follow-up and 48-hour promotion

On each invocation that selects an existing PR:

1. Re-fetch its issue, PR, question thread, replies, and blockers. Read all answers
   before considering timeout. Use server timestamps and 48 elapsed hours from the
   original question comment; edits, follow-ups, and routine updates do not reset it.
2. Apply explicit answers and settle ordinary remaining ambiguity with safe
   assumptions. At the deadline, use recorded defaults for unanswered items.
   Partial replies need not keep the PR Draft when the decision set can safely
   be settled; they never reset the deadline or discard choices already made.
3. Revise the plan, code, tests, and description where needed. Confirm the PR
   matches the completed decision set. An answer that confirms the implementation
   needs no artificial commit.
4. Mark ready only when implementation is complete, applicable verification
   passes, blockers are Done, and no unresolved safety or authorization constraint
   or explicit hold remains. Elapsed time clears unanswered questions only; it
   never overrides these gates or supplies missing approval. Record any gate that
   prevents promotion instead of claiming readiness.
5. If the initial set remains unanswered before its deadline, keep it Draft.
   Recover aged legacy questions' original clock; if already expired, apply their
   defaults and mark verified work ready now, without a fresh Draft waiting period.
   Never fabricate a historical timestamp/default or claim elapsed time without
   evidence. Choose and record a safe assumption now to settle an ordinary
   decision without reopening questions. Failed or incomplete verification always
   prevents readiness.

No additional routine approval is needed. Inspect all new feedback, including
edits, before deciding no action is due. On an unchanged rerun, make no external
comments, notifications, commits, or repeated reviewer requests. Continue the
queue if the selected PR needs no action. Check again only on a later invocation.

## Finish and report

When new work or a meaningful update is complete and the PR matches current
answers or recorded defaults:

1. Move the issue to In Review, including when the PR remains Draft for questions.
2. Post one delivery comment within the shared 100-word maximum: link the PR,
   state the user-visible result, one useful verification summary, and whether it
   is Draft awaiting answers or ready using confirmed choices/defaults. Invite
   optional feedback without requiring acknowledgement.
   Mention only the requester; GitHub handles reviewer requests. Reuse an existing
   delivery comment instead of posting it again on a later unchanged run.
3. Keep the private checkpoint current without publishing it. Combine substantive
   answer, implementation, readiness, or blocker changes into one short update;
   do not post per-push updates, reminders, or unchanged blocker pings.

Report the issue/PR links, user-visible outcome, verification summary, Draft/ready
state, and any material blocker or next action concisely. Include a readable
question deadline only when useful; omit raw bookkeeping and routine field lists.
State that another invocation is needed for future replies or promotion;
do not claim that a follow-up was scheduled.
