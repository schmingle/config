---
name: linear-ticket
description: >-
    Triage bugs and one-off work in the configured Linear queue, recommend project
    framing when needed, then implement or update one best eligible bounded
    ticket, preferring a one-to-one mapping between implementation tickets and
    focused PRs. Requires explicit user or authorized automation invocation;
    never merges or deploys.
disable-model-invocation: true
---

# Linear Ticket Workflow

Run only when explicitly invoked by the user or an existing user-authorized
automation. Honor an explicit read-only or dry-run request throughout. This
workflow does not execute projects.

## Lightweight discovery

Before loading either detailed pass, read
`~/.codex/private/linear-ticket-workflows.json`. Require `team` (exact Linear team
key), `repository` (GitHub `owner/repository`), `maxEstimate` (numeric upper bound),
and `mediumEstimateLabel` (the scale label used as Medium). Keep these values
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
remain actionable without an issue metadata change. Exclude tickets created by
the verified current user; any other verified creator may qualify. Do not require
or filter by `triageCreatorEmails`, even if legacy settings contain that field.
Defer parent/leaf checks and other detailed eligibility gates to triage.

Only after exhausting both listing sets without possible candidates, report that
no action is due and stop. Do not load pass references, full issues, comments,
PRs, repositories, broader context, checkpoints or automation memory; do not
write, spawn agents, or start a build. Failed queries or unverifiable coverage
are blockers; unfinished listings never prove an empty queue.

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
   Then proceed to build.
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
completes its preparation, moves it to Todo, and confirms all implementation
gates; read-only assessment alone is insufficient.
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
explicit user or authorized automation invocation. Report the triage dispositions
and build result, or that no eligible action was due, with issue/PR links when known.
