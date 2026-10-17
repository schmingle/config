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
automation. Read the [triage pass](references/triage.md) and
[build pass](references/build.md) contracts before acting. Use the private
workflow settings, authenticated Linear identity, and repository checks they
require. Honor an explicit read-only or dry-run request across both passes.
Use triage’s [work routing](references/triage.md#work-routing) for new and resumed
work; this workflow does not execute projects.

Run both passes in order on each invocation:

1. **Triage:** Use listing metadata and checkpoint hints to rank likely
   actionable/due prior work and new candidates. Paginate as needed, but fully
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

This invocation authorizes the bounded Linear and PR actions in the two pass
contracts. It does not authorize merging, auto-merge, deployment, production
writes, or email, SMS, or Slack messages. Do not create or edit automations or
promise an automatic follow-up. Future replies and deadlines require another
explicit user or authorized automation invocation. Report the triage dispositions
and build result, or that no eligible action was due, with issue/PR links when known.
