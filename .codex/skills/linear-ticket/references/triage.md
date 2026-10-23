# Linear Ticket Triage Pass

Inspect repository code and linked PRs read-only. Never implement code, change a
PR, or request reviews during triage. The combined skill's build pass follows
after triage and selects independently from the verified candidate list.

Fully screen at most 10 distinct issues in this invocation, then create, prepare,
or substantively update at most 10 distinct screened issues. A decomposition
parent and every child screened, created, reused, or changed count within these
caps; reserve capacity before completing the scan as described below. Oversized,
held, blocked, unsuitable, and quiet outcomes still count among the 10; each issue counts once
even if preparation changes several fields. Post at most one new ownership or
exceptional blocking ask in the combined invocation. After it, continue with
other screened eligible tickets without another such ask. Do not create or edit
automations, promise implementation
of a particular ticket now, or promise a background follow-up.

## Private workflow settings

Reuse the private settings, fetched listing metadata, and remaining cursors from
[lightweight discovery](../SKILL.md#lightweight-discovery). Resume each listing
without refetching its completed pages. Verify the intended repository against the
private settings before repository access. Never guess missing settings, substitute
the current repository/team, or broaden queue filters.

## Identity and authorization

Reuse discovery's verified authenticated Linear identity. Use its user ID for
assignee, creator, and estimate-history comparisons; never infer a missing identity.

The combined invocation authorizes normal Linear comments, assignment, estimate,
and status changes, plus the narrow native-child creation described in
[Large-ticket decomposition](#large-ticket-decomposition) in this triage pass.
Only the build pass may implement or mutate a PR. No separate approval or `auto`
keyword is required for triage actions.
Honor an explicit read-only or dry-run request: inspect and report proposed actions
without mutations.

Before each mutation, re-fetch every affected issue and recheck eligibility,
ownership, blockers, new discussion, and linked-PR activity. Material changes
require reassessment under the gates below, not a routine approval stop. This
authorization does not cover merging, deployment, production changes, or other
communication channels. Email, SMS, and Slack retain their preview-and-confirm
gates under applicable `AGENTS.md` guidance.

## Resume prior workflow work

While choosing up to 10 issues to screen, consider the current user's previously
managed leaves in the configured team in Todo, In Progress, or In Review.
Substantively assess linked PRs only for screened issues; metadata-only PR-state
reads for the reporting inventory follow [reporting](reporting.md).
Exclude tickets created by the
current user except verified decomposition children under the narrow provenance
rule below; any other verified creator may qualify. Require an existing plan
and source evidence establishing this workflow's bounded scope, verified
ownership, and estimate; assignment or
status alone is not eligibility. Reapply [work routing](#work-routing) after
checking ownership, including to resumed work. Apply the
[directed-ownership rule](#ownership-gate), including relevant Slack decisions;
refresh relevant source evidence before a continuation write. Re-fetch replies,
edits, blockers, and observed PR state. Prefer a new actionable answer, scope
change, newly due 48-hour follow-up, or verified interrupted In Progress build.
When an update
is needed, record only the material decision and next action in a concise Linear
handoff; keep assessment bookkeeping in the private checkpoint below.
Do not change the code, PR, readiness, review requests, or existing issue status
for this continuation. A substantive update counts as one of the 10 triage tickets.

Preserve unresolved ownership holds and check for actual reassignment or newer
conflicting ownership. Do not reapply the new-work seven-day participation veto
to ordinary reviews on the current user's recorded implementation PR. An unchanged
record is a quiet skip, including a previously recorded due follow-up; continue
the queue so waiting work does not starve new candidates. This continuation path
does not broaden the decomposition-child exception to the self-created-ticket
exclusion. Triage records what it assessed
separately from what build has applied; reading feedback never marks it
implemented or consumes build's applied-reply watermark.

## Candidates

Rank candidates with discovery metadata and optional checkpoint hints,
using the entrypoint's value-based selection order. Use age and meaningful activity
as relevance signals, not automatic exclusions or a newest-first rule.
Continue the independent discovery
listings as needed, including both new and possible prior work. Stop after fully
screening 10 candidate issues or exhausting both listings and their collected
candidates. An unfinished listing cannot establish that no candidates remain.
Do not read full issue/comment/PR detail for more than 10 candidates. Paginate
comments and relations for each screened issue before deciding suitability or
whether feedback is new. A parent whose detailed discussion is read to gate a
child counts as one of the 10 distinct screened issues:

```text
team = settings.team
status in (Triage, Backlog)
assignee in (none, current user)
verified creator != current user, or verified authorized decomposition child
estimate = independently assessed later; no reported/native-size prefilter
```

Compare the verified issue creator's user ID with the authenticated current
user's ID. Any other creator may qualify; skip if the creator cannot be verified.
A self-created issue qualifies only when it is a verified native child actually
created by this workflow's authorized decomposition of an otherwise eligible,
non-self-created parent. Require the live native parent relation and human-readable
scope/source evidence tying the child to the parent's bounded outcome and split;
a checkpoint, arbitrary parent relation, or self-authored claim alone is insufficient.
Revalidate provenance and the parent's eligibility apart from its parent role on
later runs. This exception does not recurse through self-created parents or cover
arbitrary self-created children.
Parent selection never waives the child's own ownership and other gates.

Do not exclude an issue because of its reported size, native estimate, or estimate
author. Independently assess the chosen approach before comparing it with
`settings.maxEstimate`. Explicit human execution caps and holds remain binding.
Read existing questions and answers; do not repost questions or skip an otherwise
suitable ticket merely because answers are pending. After the ownership gate is
clear, include linked PR evidence. Do not create or update an implementation PR
during triage.

## Ownership gate

Target up-for-grabs work and confirm stale-work takeover. For new selections,
apply this gate before any ticket field change (including an oversized estimate),
normal triage comment, or implementation handoff record. Recorded prior-work
continuations use the ownership checks in Resume prior workflow work above.
Check a parent before selecting its direct child, then check the child's own
discussion and linked PRs too; a child cannot bypass an unresolved parent
ownership gate. The assignee filter above always applies:
assignment to another engineer excludes the issue even when stale or a takeover
is offered.

For a screened candidate that might be claimed, search the intended Slack
workspace by exact issue identifier or URL and read relevant human discussion
and linked threads for ownership, current work, and handoffs before normal
triage mutations or handoff preparation. Keep this within the screened-candidate
cap; do not search tickets already excluded by metadata gates. Reuse verified
source context from this invocation, refreshing it before a write when ownership
may have changed. If required Slack evidence cannot be checked reliably, skip
the affected candidate and report the limitation. Finding no discussion does not
itself establish that work is available.

Read all issue comments, replies, relevant Slack threads, and available linked-PR
conversation, code activity, and reviews. Treat explicit assignments, handoffs,
or requests directing another person to investigate or implement as ownership
evidence, even when the native assignee is empty or the recipient has not replied.
Distinguish directed responsibility from incidental mentions. Follow the latest
authoritative ownership decision; skip if conflicting directions cannot be
resolved. Work directed to someone else is a quiet exclusion: do not claim it,
change fields, prepare another handoff, or post a takeover question merely because
it is unassigned, unanswered, or old. Only a subsequent explicit handoff to the
current user can supersede that direction, subject to the assignee filter and
other eligibility gates. Apply this directed-ownership rule to prior-work
continuations too.

Otherwise, identify another engineer's actual participation using available
people/role context; an incidental mention, bot comment, or configured-team
membership alone does not establish participation. If participant identity,
discussion coverage, or activity cannot be established reliably, skip with the
reason. Retain the participation and stale-takeover rules below for work without
an outstanding direction to someone else.

Use server timestamps and a current evaluation time. Latest activity is the
maximum of issue `createdAt`/`updatedAt`, every issue comment/reply's
creation/update, relevant Slack message/reply creation/edit timestamps, and
available linked-PR conversation, code, and review timestamps. **Active** means
any activity at or after `now - 7 * 24 hours`, including the cutoff; **stale** means
all activity is older. Count activity from anyone, including bots and people who
are not engineers; engineer participation and activity recency are separate checks.

- **No other engineer involved:** continue normal triage.
- **Another engineer involved and active:** skip without comments, field changes,
  or handoff preparation; report the engineer and latest activity as the reason.
- **Another engineer involved and stale:** mark a prospective ownership ask for
  ranking. If selected for disposition, post one top-level Linear comment:
  “Do we still want to address this? If so, shall I take this?” Mention the involved
  engineer and requester when useful.
  Hold all field changes and handoff preparation pending an explicit affirmative
  confirmation that the work is still wanted and the current user may take it.

If this invocation already posted one new ownership or exceptional blocking ask,
do not post another; keep any newly found held ticket out of the buildable list.

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
assigning, or moving to Todo. Once confirmed, retain the question and affirmative
reply references in the private checkpoint; re-read those sources on later runs
to verify that ownership was cleared. Link them in a human handoff only when useful.

## Independent approach and sizing

For each candidate:

1. Read the issue, comments, attachments, relations, estimate history, and direct
   sub-issues, then apply the ownership gate before proceeding.
2. Inspect the configured repository’s relevant code, tests, schemas, history, and
   applicable `AGENTS.md` files. Run `nvm use` first. Investigation is read-only.
3. For a bug, extract the reported problem, observed and expected behavior,
   reproduction facts, and actual constraints. Independently inspect the code and
   choose the smallest complete fix before comparing reporter-suggested designs or
   estimates. For a specific nonbug request, preserve the requested outcome while
   independently choosing the implementation and size. Treat suggestions and
   estimates, including the current user's earlier estimate, as hypotheses.
   Preserve security, approved intended behavior, compatibility, explicit scope,
   and other real constraints; a simpler approach cannot discard essential work.
4. Estimate that chosen approach using the configured team's scale and update the
   native estimate when it differs. Use `settings.maxEstimate` as the execution
   ceiling, distinct from `settings.mediumEstimateLabel`, the smaller-child
   reference. If above the ceiling, keep it out of build and prepare a concise sizing
   and next-step disposition, rather than silently changing only the estimate.
   Do not claim oversized work or automatically remove its existing assignee.
5. Apply [work routing](#work-routing) to the complete outcome. For each independently
   assessed Large issue, evaluate [Large-ticket decomposition](#large-ticket-decomposition).
   A bounded Large leaf at or below the ceiling may qualify when no clean split
   exists. For existing children, assess parent context before selecting the newest
   eligible direct child; settled independently bounded work may qualify even when
   its parent needs project framing, but cannot bypass unresolved project decisions.
   Apply the child's own ownership, provenance, estimate, and routing gates. Never
   move a parent with children to Todo.
6. Record the chosen approach and material departure from a proposed implementation
   once in the short plan, with the reason in the user's voice. Invite requester
   feedback and link the eventual draft PR when available. Technical differences
   with a safe default can proceed; changed intended behavior, permissions,
   compatibility, approved scope, or a decision without a safe default requires
   approval before affected work. Record the approach-review reason and original
   publication timestamp for the shared Draft window below; do not open a second
   questioning or waiting round.

A suitable leaf passes that routing and can be implemented safely using explicit
defaults for unanswered product questions. Missing permission, required data, an
unfinished prerequisite, or a decision with no safe bounded default remains a
blocker. Do not force such work into Todo or treat silence as
authorization. If more than three unresolved decisions prevent a coherent bounded
implementation, recommend project framing or leave it held with the specific gap;
do not silently remove essential work to make it fit.
Only verified prior workflow work and newly prepared Todo leaves that pass every
implementation gate enter the buildable candidate list. Oversized, blocked,
held, unsuitable, duplicate, obsolete, parent, and no-safe-default tickets stay
out even if triage changed a field or posted a question. A read-only assessment
of a new Triage/Backlog ticket does not make it buildable.

After screening at most 10 issues, rank needed dispositions as described in the
entrypoint. Apply them only to screened tickets, re-fetching each affected issue
and its sources before mutation. An oversized sizing/next-step disposition,
authorized decomposition, new ownership/exceptional blocking ask, substantive continuation handoff,
new leaf preparation, or material routing proposal counts as a disposition of
that screened issue. If a candidate becomes ineligible, skip it and use the next
ranked screened issue; do not pull in an eleventh issue. An unchanged pending ask or quiet skip counts
among the 10 screened issues but requires no mutation. Keep the one-new-ask
limit across both passes even if other screened tickets remain.

## Work routing

Apply after the ownership checks, for new selections and prior workflow work.
Keep all provenance, independently assessed ceiling, leaf, and ownership gates.
Project membership alone does not exclude a bounded fix; honor an active owner or
supervisor’s assignment and do not create competing execution.

1. **Bounded bug or one-off:** The complete cohesive outcome has known acceptance
   criteria and a credible validation path. Prefer a one-to-one mapping between
   implementation tickets and focused PRs; a justified exception may use two PRs
   for the same bounded outcome.
   PR count is a sizing signal, not permission to stuff a large change into two
   PRs or defer essential work. Ordinary unanswered details may use the existing
   safe-default contract; no full project plan is needed for a clear fix.
2. **Project framing needed:** Consequential unresolved decisions or coordinated
   phases, dependencies, rollout, or acceptance need a project-level contract.
   Exclude it from the buildable list and propose the finite outcome, known scope
   and supporting evidence, consequential decisions, and completion validation.
   Recommend a relevant existing project or a new one; reuse known context instead
   of drafting a speculative full plan. Do not create or reorganize projects
   or start broader execution in this workflow. The narrow bounded Large split
   below does not authorize decomposing project-shaped work or changing its contract.
   Project creation/reorganization and broader execution require user approval
   and a separately authorized handoff.
3. **Material uncertainty:** Investigate read-only within the existing screening
   cap. If the route remains unclear, exclude it from build and state the specific
   evidence or decision missing instead of guessing or forcing a project plan.

For a bounded outcome needing two PRs, prefer appropriately scoped tickets or
sub-issues where creation/splitting is already authorized; otherwise propose the
split. Only the narrow Large decomposition below adds creation authority. Each
child independently passes screening, triage, and build selection under the
existing ownership, estimate, and creator/provenance rules.
Preserve the 10-screened/10-mutated caps and one-ticket build cap; a selected parent never authorizes building multiple
children. Preserve existing multi-PR work rather than retroactively splitting it;
use the build pass’s documented exception when necessary.

Apply routing proposals only in the ranked disposition pass, within the same
10-screened/10-mutated ticket limits and comment caps. Reuse the existing plan or
post one concise initial proposal; later proposals require a material change.
A project-approval request or exceptional blocking ask consumes the invocation’s
one new ownership/exceptional blocking ask, with the existing quiet-rerun rules;
it does not open another product-question round. If that ask budget is used,
report the needed decision here without another external ask. Silence, safe
defaults, or 48 elapsed hours never approve project work. Leave project-shaped or
unresolved-routing tickets out of Todo preparation; preserve existing status and
partial work on resumed tickets. If routing evidence invalidates an existing
PR’s readiness or completion claim, identify the affected PR links and concrete
unsupported claim in the material proposal and user report for separately
authorized disposition. A complete bounded PR is not unsafe merely because the
broader ticket needs project framing. For project-shaped or unresolved-routing
dispositions, keep issue statuses unchanged; triage never changes PRs. An unchanged
recommendation remains quiet.

## Large-ticket decomposition

For every independently assessed Large issue, determine whether the existing
bounded outcome splits cleanly into smaller coherent, independently testable
deliverables, each independently sized below Large (Medium-or-smaller on the
verified scale, using `settings.mediumEstimateLabel`). When it does, create or
reuse native children automatically; no separate split approval is
needed within that outcome. If no clean split exists, a coherent Large leaf may
build when it meets the configured ceiling and all other gates. Never split only
by implementation versus testing, invent artificial children to evade a gate,
expand scope, alter an approved project contract, or use this rule to claim
above-ceiling or project-shaped work.

Before any split mutation, screen the parent and existing children, assess every
planned child's eligibility and scope, preserve existing children/PRs, and identify
the complete split. Reserve slots for new children and verify them after creation.
Count the parent and every screened, created, reused, or changed child within
the applicable 10-issue caps;
reserve remaining screening and mutation capacity before completing the scan.
If the full split will not fit, defer the entire split, report the bounded next
step, and create no partial set. Reconcile an ambiguous write against live native
relations and issue contents before retrying; never blindly create duplicates.

Keep the parent responsible for the full outcome and completion validation.
Give each child explicit scope, acceptance criteria, validation, an independent
estimate, an appropriate assignee, the parent's priority, original requester/source,
and relevant context. Add native dependencies only for actual prerequisites. Preserve existing priority;
copying it to a new child does not reprioritize work. Record concise human-readable
source/scope evidence for creation provenance. Every child has its own
creator/provenance, ownership, Slack, routing, blockers, and implementation checks;
parent eligibility grants no takeover permission. Defer a split that needs
unresolved ownership or scope permission rather than creating competing work.
A child waiting on a recorded prerequisite may be created within the complete
split, but remains out of Todo and build until its blockers and all other gates clear.

Only children actually created under this rule may use the narrow self-created
exception; reused self-created children need verified prior authorized provenance.
Do not recursively split such a child to extend the exception. Keep parents out
of Todo and the buildable list. The build cap remains one selected eligible leaf,
never the parent batch; splitting adds no merge, deployment, or broader execution
authority.

## Ticket relevance

After ownership checks and before detailed planning, assess potentially stale
work using creation age, last meaningful activity, and what the activity says.
Run a quick, proportional validation against current implementation, related
issues/PRs, and available recent evidence. Age triggers scrutiny, never closure
or lower priority by itself. Bot updates, metadata edits, and this workflow's own
comments do not by themselves renew relevance. This relevance assessment is
separate from the conservative seven-day ownership activity rule.

- **Likely stale:** Evidence indicates obsolete, resolved, or superseded work.
  Present the evidence and proposed terminal disposition in the focused interview;
  close only after the user explicitly confirms that ticket and reason. Re-fetch
  before closing. Never close merely because it is old or unanswered.
- **Suspected stale:** Relevance remains uncertain. Post one short Linear question
  stating what was checked and asking whether the problem persists or the request
  is still needed. Reuse existing questions/answers; no repeated pings or clock
  resets. Hold detailed planning/build pending relevance evidence, and retain the
  ticket in the report. An unanswered question may later be reviewed with the user.
- **Still relevant:** Proceed through normal sizing, routing, and execution gates.

For each screened potentially stale ticket, record the relevance finding, quick
validation evidence (or exact access limitation), and next disposition in the
report's Update/notes. "Not buildable," an old estimate, project membership, or
an unsettled implementation plan does not establish current relevance. A missing
plan is not a substitute for checking whether the work is still needed. Delegate
assignments must request relevance/disposition findings as well as build readiness.
If quick validation remains inconclusive, use Suspected stale and the bounded
feedback route above; do not silently carry forward an implementation hold.

These checks and writes count within the existing screening/mutation limits.
A relevance question shares the ticket's initial external product-question set
and lifetime three-question budget; it is not a new question round. If that set
already exists, reuse it and surface uncertainty in the user interview instead.
Relevance questions are an exception to waiting for a settled plan, not to
ownership exclusions, read-only requests, or existing permission gates.

## Comment style

This is the shared output contract for both passes. Write naturally as the current
user and follow applicable writing guidance. Post ticket comments directly in
Linear. Lead with the outcome, decision or blocker, and next action. Make the main
point clear in a five-second scan and the full update readable within 30 seconds.
Once necessary decisions are settled, publish one cohesive plan: what I'll do,
why, what I need from the requester, and how we'll verify the outcome. During a
user interview, keep partial decisions in the chat until a coherent plan is ready,
unless the user explicitly requests an interim update. Prefer updating an existing
plan comment when appropriate; preserve useful discussion and approval evidence.
Do not post acknowledgements or decision receipts after each answer. Necessary
relevance/clarification questions, material blocker changes, and delivery results
may warrant separate comments. Omit interview references, option numbers,
"decision source," "approval source," and administrative process language.
Keep required approval evidence retrievable privately or in required PR disclosures.

Use a few short sentences or at most three top-level items; number questions with
compact choices. Mention issues by their actual ticket IDs so Linear can autolink
them; never substitute titles, vague references, or invented IDs.

- All Linear comments and status updates, including initial questions and
  choices, have a **100-word total maximum**; aim much shorter. Keep the lifetime
  three-question budget and existing ask limits. Do not pad to a word target or force a template.
- Include only a material outcome, decision/default, question, blocker, routing
  proposal, or next action. Do not repeat the ticket description or workflow.
- The update cap does not shorten durable specifications. Keep adequate scope
  and acceptance detail in the ticket, with technical rationale, implementation
  detail, and validation evidence in the required PR description. Link the PR from the ticket. Use native assignee, estimate, status,
  and PR links instead of restating fields in prose.

Never put raw UUIDs, timestamp dumps, workflow provenance, processed-reply
watermarks, serialized state/JSON, or HTML comment blocks in Linear comments,
human-facing PR descriptions/comments, or routine user reports. HTML comments may
render visibly in Linear; they are not private storage. Do not move a metadata
wall into the PR or disguise it as hidden text. A useful deadline may appear as a
readable date/time with timezone; retain exact source timestamps privately.

Example triage plan (no questions):

> I propose showing the specific validation error while keeping the user's entries
> intact, so they can correct the form without starting over. The change should
> cover both single-field errors and several invalid fields submitted together.

Example build delivery (replace `URL` with the actual PR URL):

> The [PR](URL) now shows specific validation errors without clearing the form.
> Users can correct the affected fields and retry the save. Focused regression
> checks pass for single-field and combined errors. It is ready for review.

## Questions and defaults

This is the shared clarification contract for triage and build for the lifetime
of the same bounded ticket. Read all historical comments and replies, including
legacy questions in any format, before asking anything. Reuse relevant answered
context from related tickets too; a different issue does not justify asking a
known decision again. Count prior product questions toward the shared budget;
invocation, edits, partial answers, missing metadata, and a move between passes
never reset it.

Post **one initial product-question comment at most**, containing no more than
**three meaningful questions in total across both passes**. Ask fewer or none.
Ask only when the answer changes observable behavior and is not already known;
avoid compound questions and low-level implementation choices. If questions were
already asked, reuse their decisions, answers, defaults, and original timestamp
without posting another question set or filling unused slots later.

Follow the shared comment limits above, including the total word cap for questions.
Never identify the comment as agent-generated or use a templated heading.
Number questions with mutually exclusive lettered choices; A is the safe
default and the only option labeled `[Recommended]`. Invite a compact reply such
as `1A, 2C`; add `Other — please specify` only when useful.

```text
1. <question that changes observable behavior>
   A. [Recommended] <safe default for implementation>
   B. <alternative>
```

During triage, state that these defaults are recorded for build; do not promise
that this ticket will be the one built in the current invocation. When build
selects it, implementation proceeds immediately using those defaults. An
initial unanswered question set and a material technical approach departure
share one Draft review window. Keep the implementation PR Draft until substantive
requester feedback settles the relevant assumptions/approach or 48 elapsed hours
after the original comment that first published the questions or material approach
departure. An earlier routine plan without either feedback trigger starts no
window. Retain that first server timestamp and the approach-review reason;
questions, plan edits, or later passes never restart the same review window.
Approval-required behavior/scope/permission changes remain held even after the
review window.
Only build may update a verified PR's readiness during its own pass; time
alone never substitutes for verification or authorizes triage to change a PR.
Do not imply an automatic wake-up or merge.

Honor clear parts of any reply and infer reasonable intent for partial or
ambiguous parts. Record the best-supported assumptions in the implementation
plan (and, during build only, the PR); **do not ask a routine follow-up**, repeat
a question, send a reminder or ping, or notify people about question edits. A thanks or status question alone is
not a substantive answer. After the first substantive reply/answer, exhaustion of
the question budget, expiration of the shared original 48-hour deadline, or a declined
clarification, settle ordinary questions using answers and safe defaults. Silence
at the deadline has the same result. Exhausting the question budget forbids more
questions; it does not shorten the shared Draft window. Later
replies may change the implementation but do not reopen ordinary questioning.
An old ambiguous follow-up is historical context, not evidence of a new risk.

For legacy questions without recorded defaults, choose and record safe assumptions
now without a new timer or ordinary question. Reuse known original timestamps;
never invent missing timestamps or claim an unverified deadline has elapsed.
Missing timestamp evidence alone is not proof that a PR can leave Draft.

Only **new evidence of a material risk** that is unsafe without authorization,
required data, or permission, or an explicit user reopening of that risk, can
justify one precise blocking ask. Keep its stable risk fingerprint, bounded scope,
source references, ask reference, and resolution in the private checkpoint;
the comment itself states only the blocker and needed decision. On later
invocations, an unresolved identical blocker is a quiet skip, not another ask.
Routine edits, ambiguous replies, and the skill's own comment `updatedAt` are not new evidence. Reassess genuinely new scope or risk without
automatically opening another product-question round.

## Private checkpoint and quiet runs

This is the shared bookkeeping contract for both passes. The human handoff is
the short plan/defaults/next action,
existing issue fields, and useful source/PR links. Do not publish a separate
workflow record in Linear or the PR, and do not create repository tracking files.

When durable idempotency needs a checkpoint, use
`~/.codex/private/linear-ticket-workflow-state/<issue-uuid>.json`, keyed by the
issue UUID verified from the authenticated workspace/team. Keep it outside all
repositories, with directory mode `0700` and file mode `0600`. Store only necessary
source IDs/links and timestamps, bounded decisions/defaults, the original question
reference/`createdAt`, original approach-review notice reference/publication
timestamp and shared deadline, ownership/risk holds and their source references,
separate `triageSeen` and `buildApplied` reply IDs/`updatedAt`, and the minimal
reporting inventory fields described in [reporting](reporting.md). No copied
threads, ticket dumps, credentials, or secrets. Update only the current pass's
assessment/applied state and necessary shared decisions; preserve the other state.
Settled product choices do not mean code was applied. Triage never advances
`buildApplied`; build advances it only after applying or resolving the feedback.

If a checkpoint write is unavailable or requires approval, respect the boundary
and disclose it as needed; continue independently authorized investigation and
discussion. Cache synchronization is not a prerequisite for a substantive question.
Do not bypass a rejected write or treat missing cache as a cleared gate.

Always re-fetch source issues, questions/replies, ownership decisions, blockers,
and PRs. A checkpoint is a cache, never authorization or evidence that a hold
cleared. If absent, stale, or unavailable, reconstruct from live source comments,
server timestamps, native fields, and implementation/disposition evidence.
Legacy machine blocks may be read for reconstruction but must not be recreated
or copied into new comments or PR text. Do not reset the shared original review clock,
reopen the lifetime question budget, repeat an ownership ask, or treat silence as
ownership permission. Never invent a timestamp or applied result. If evidence
cannot establish a needed gate, keep that gate closed and report only the concise
blocker; missing cache data alone does not justify a new product question.

On each invocation compare current source IDs/`updatedAt` with the appropriate
private assessment/applied state, or reconstruct the prior disposition from source
evidence. Triage-seen replies remain pending for build until applied or resolved.
For previously assessed tickets without a new requirement or actionable change,
take no action and continue the eligible queue. An unchanged pending hold or
previously recorded due follow-up is a quiet skip. A fresh eligible candidate can
receive its initial short plan without a recent requirements change.

Post only the initial combined plan/questions as a routine triage comment. Later
comments require a material decision, newly due follow-up, or blocker change;
combine related changes within the follow-up word cap. No acknowledgements,
reminders, unchanged plans, repeated questions, edit notifications, or metadata-only
updates. The skill's own comment update never triggers another question. Only
build posts implementation/delivery results, and unchanged runs post nothing
externally. Every run still produces the user-facing inventory report; quiet
Linear activity does not suppress that report.

## Finish triage and pass candidates to build

For a suitable leaf whose ownership gate is clear, without waiting for product
answers:

1. Re-fetch every blocker before preparing the handoff or posting a comment.
   Continue only when all are Done; otherwise skip without preparing the ticket.
   Recheck duplicate, obsolete, and [work-routing](#work-routing) eligibility too.
2. Set or confirm its independently assessed estimate at or below
   `settings.maxEstimate`, and assign it to the current
   user if unassigned.
3. Reuse the existing plan/questions and answers, or post the single initial
   short plan/questions comment when needed. Link useful existing criteria rather
   than repeating them; retain necessary bookkeeping only in the private checkpoint.
4. Move it to Todo last. The short plan and native issue fields form the
   handoff; include an existing PR link when useful. Add it to the buildable
   list only after verifying completed preparation and current gates.

Never change priority. Never move oversized, unsuitable, duplicate, obsolete,
parent, blocked, project-shaped, unresolved-routing, or ownership-held tickets to
Todo. Defaults and elapsed time do not override those limits. Triage does not
modify code or PR state.

Carry the verified buildable list into the build pass in this invocation. Report
the ticket links, actual triage dispositions, resulting statuses, and material
assumptions or blockers concisely. Link evidence only where it explains a skip
or decision; do not dump timestamps or internal state. An existing PR's observed
state is read-only context, never a verified implementation outcome of triage.
Mention a readable question deadline only when useful. In read-only mode, label
actions as proposed and do not mutate the handoff or checkpoint.

Carry these outcomes into the consolidated [run report](reporting.md); triage
does not replace the outstanding inventory with only this run’s screened issues.
