---
name: linear-ticket
description: >-
    Triage bugs and one-off work in the configured Linear queue, recommend project
    framing when needed, independently size work through Large and split cleanly
    decomposable Large tickets, then implement or update one eligible bounded
    leaf, preferring a one-to-one mapping between implementation tickets and
    focused PRs. Requires explicit user or authorized automation invocation;
    never merges or deploys.
disable-model-invocation: true
---

# Linear Ticket Workflow

Run only when explicitly invoked by the user or an existing user-authorized
automation. Honor an explicit read-only or dry-run request throughout. This
workflow does not execute projects.

## Lightweight discovery

Read the [reporting contract](references/reporting.md) for every invocation,
including blocked and empty runs. Before loading either detailed pass, read
`~/.codex/private/linear-ticket-workflows.json`. Require `team` (exact Linear team
key), `repository` (GitHub `owner/repository`), `maxEstimate` (numeric upper bound),
and `mediumEstimateLabel` (the scale label used as Medium for smaller subtickets).
The configured execution ceiling is Large on the team's verified live scale;
resolve `maxEstimate` independently from the Medium label. Keep these values
private. Verify the intended
authenticated Linear workspace, team, statuses, and estimate scale against the
settings. Resolve the current Linear user through the authenticated connector's
current-user lookup (`get_user` with `query: "me"`, or equivalent), or reuse an
explicitly confirmed Linear identity from this conversation. Never infer identity
or settings from the OS, Git, unrelated history, or the current repository.
Missing, invalid, ambiguous, or unverifiable configuration/access is a blocker;
report it, never treat it as an empty queue or broaden the configured team.

List issue metadata in the configured team for **both** sets:

- New work: Triage or Backlog, unassigned or assigned to the current user.
- Possible prior work: Todo, In Progress, or In Review, unassigned or assigned to
  the current user. This is a conservative superset; assignment/status does not
  establish workflow provenance or final eligibility.

Use supported server-side team, status, and assignee filters, separate queries
when needed, and request only IDs/identifiers/URLs, status, assignee, creator,
estimate, parent ID, and `updatedAt` where field selection is supported. If a
filter is unsupported, filter the metadata locally without narrowing coverage.
Keep each listing's pagination independent and deduplicate by issue ID. As soon
as metadata yields a possible candidate, proceed to the detailed passes with the
fetched metadata and remaining cursors; do not exhaust listings first.
Do not filter by recent activity, unchanged `updatedAt`, or presumed provenance:
pending unapplied replies, elapsed 48-hour deadlines, and interrupted builds can
remain actionable without an issue metadata change. Reported or existing estimates
are not discovery exclusions: triage independently sizes the chosen approach.
Exclude tickets created by the verified current user, except native children
created by this workflow's authorized Large-ticket decomposition; a parent ID
alone does not establish that exception. Defer possible decomposition children
to triage for live provenance and eligibility checks; any other verified creator
may qualify. Do not require or filter by `triageCreatorEmails`, even if legacy
settings contain that field. Defer parent/leaf and other detailed gates to triage.

Only after exhausting both listing sets without possible candidates, skip the
detailed passes. Still reconcile and report the outstanding inventory and recent
closures under the reporting contract; no eligible new action does not mean no
work remains. Load only the reporting sources needed for that reconciliation,
not implementation context or unrelated full issues. Do not mutate Linear or PRs,
spawn agents, or start a build on this path. Failed queries or unverifiable
coverage are blockers; unfinished listings never prove an empty queue.

Otherwise, read the [triage pass](references/triage.md) and
[build pass](references/build.md), verify the configured repository as they
require, and reuse the metadata and listing cursors in triage. Apply all live
provenance, ownership, eligibility, and [work-routing](references/triage.md#work-routing)
gates; discovery alone authorizes no disposition or build.

## Detailed passes

Run both passes in order after discovery finds possible candidates:

1. **Triage:** Use listing metadata and checkpoint hints to rank likely
   actionable/due prior work and new candidates. Fully
   screen at most **10 candidate issues** before choosing mutations. Oversized,
   held, blocked, unsuitable, and quiet outcomes still count among the 10.
   Rank and apply bounded dispositions to those screened tickets, then derive an
   in-memory buildable subset with source evidence. Mutate at most 10 distinct tickets and
   make at most one new ownership/exceptional blocking ask across the entire
   invocation. That ask and any oversized estimate change count within the 10.
   Before completing screening, reserve capacity for a clean Large-ticket split:
   the parent and every created or reused child count against screening and
   mutation limits. Follow the [decomposition rules](references/triage.md#large-ticket-decomposition)
   without expanding the parent outcome or approved project plan. Then proceed
   to build.
2. **Build:** Select the best eligible ticket from the triage-produced list,
   re-fetch it, implement or update at most one ticket, and stop this pass. The
   ticket just prepared may qualify, but it has no automatic priority. A blocked
   selected ticket consumes the build pass's one-ticket budget; a necessary second
   PR for the same bounded outcome does not consume another ticket. The two passes
   may act on different tickets.

In each pass, prefer verified existing workflow work with actionable new
information, a due follow-up, or an interrupted In Progress build; among those,
choose newest `updatedAt`. Then
triage chooses the newest eligible Triage/Backlog candidate and build chooses
the newest buildable Todo candidate. Only the 10 screened issues receive full
issue/comment/PR assessment; rank their needed dispositions before mutation.
Each screened issue counts once toward the 10 even if triage makes no change or
changes several fields. Listing pages alone do not count as full screening.
Explicit ticket selection applies to a pass only when the user scopes that pass
to the ticket; it never forces the other pass onto the same ticket.

Build eligibility requires verified prior triage under this workflow. The 10
screened tickets are not automatically build candidates: exclude oversized,
blocked, held, project-shaped, unresolved-routing, unsuitable, duplicate, or
unanswered no-safe-default work. Include previously triaged Todo, In Progress,
and In Review work in the buildable subset
only after checking live issue history, plan, ownership, estimate, discussion,
and linked PR evidence, using the optional private checkpoint when available.
A new Triage/Backlog candidate enters the buildable subset only after triage
completes independent sizing, any clean Large-ticket decomposition, and its
preparation, moves the selected leaf to Todo, and confirms all implementation
gates. Build at most one leaf per invocation, never the parent and its children
as a batch; read-only assessment alone is insufficient.
The checkpoint is a cache, never proof by itself. Do not independently scan a
generic assigned queue during build or infer In Progress eligibility from status
alone. If provenance cannot be verified, exclude the issue from the buildable
subset. Keep machine bookkeeping private under the shared checkpoint contract;
do not add a new handoff format or public metadata.

## Voice and communication

Write authorized ticket comments and external messages in the current user's
first-person voice. Resolve and read the canonical writing guide using the
[writer guide-location rules](../../agents/writer.md#guide-location). Say
"I don't have access" or "Could you take this?", rather than describing the
user's access or requests in the third person. Preserve attribution when
reporting another participant's statements or decisions. Voice does not expand
permission to send or post messages.

This invocation authorizes the bounded Linear and PR actions in the two pass
contracts. It does not authorize merging, auto-merge, deployment, production
writes, or email, SMS, or Slack messages. Do not create or edit automations or
promise an automatic follow-up. Future replies and deadlines require another
explicit user or authorized automation invocation. Finish with one consolidated
user-facing report under the [reporting contract](references/reporting.md),
including actions, all outstanding workflow tickets, and recent closures.
