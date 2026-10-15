---
name: gather-context
description: Gather evidence of the user's work across connected sources and Codex tasks for a specified time frame, defaulting to the last 24 hours. Use for work-context collection or as input to summaries and reports.
---

# Gather Context

Collect a deduplicated, source-backed account of the user's work for use directly or by another skill. Keep collection independent of the final report's format.

## Writing-sample collection mode

Use this mode when a writing-guide caller explicitly asks for authored writing evidence. This specializes the general work-report output below; candidate-focused mode is for issue enrichment, not writing samples.

- Use the caller's exact window, intended writer, source scope, and exclusions. Resolve the current user's identity from connected account evidence and the conversation; the user-specific defaults in ordinary work collection do not apply to this mode. If account ownership is ambiguous, ask before reading that account. Do not mix personal and work accounts without authorization.
- Collect actual authored text across relevant channels: sent email bodies, authorized Slack messages, user-written documents or passages with established authorship, and the user's drafts, edits, and explicitly accepted writing in Codex tasks. Fetch enough surrounding context to identify audience, intent, and thread stage. Exclude other authors' quoted replies, signatures, boilerplate, and forwarded text from the user's sample.
- Calendar, Fathom, and generated meeting notes may explain context or help locate a source, but they are not authored writing samples. GitHub and Linear text can be included when relevant to the writer's requested channels; distinguish bot or AI-generated text from personal voice evidence. Presence in a document, account, or meeting is not proof of authorship.
- Slack review still requires authorization in the current task. A caller may carry existing authorization forward, but may not invent it. If absent, omit Slack and report the gap while continuing other permitted sources.
- Preserve exact wording, punctuation, line breaks, and emojis. Remove sensitive identifiers only when needed and label every redaction; retain a source pointer. Do not store credentials or unnecessary third-party private content.
- Deduplicate copies and cross-posts. Return each sample's stable ID, exact text, author and attribution confidence, source URL or task ID plus turn, occurrence time, channel, audience/relationship, thread stage, inferred intent, and evidence status (user-authored, explicitly approved, provisional, or unapproved draft).
- Report counts of unique observed samples by channel and intent, the exact window and timezone, reviewed/unavailable/excluded sources, pagination limits, and material uncertainty. These counts describe sampled usage, not exhaustive communication volume. Keep inferred traits separate from explicit user preferences.
- Return the evidence packet to the writing-guide caller without generating a work summary or publishing anything. The caller handles synthesis, user review, guide persistence, and final rendering. Normal work and candidate-focused modes are unchanged.

## Candidate-focused mode

When a caller supplies specific candidate actions for enrichment, use this mode instead of broad work collection. Candidates may be the user-owned or unclaimed; do not filter out unclaimed work merely because it is not yet the user's contribution.

- Require stable candidate IDs/source links, the questions to resolve, an exact start/end window, and an explicit source allowlist. If these are missing, return the missing inputs to the caller rather than expanding into a general scan.
- Treat the allowlist as a hard boundary, including channel, DM-participant, account, and privacy restrictions. Linked evidence outside it is unavailable, not permission to inspect another source. Apply the caller's sensitivity gate before searches that could disclose private information.
- Default budget: at most three candidates and twelve read-only connector calls total per invocation, including pagination. The caller may supply a smaller or larger explicit budget. Stop earlier once the questions are resolved. Never treat a budget-limited search as exhaustive.
- Inspect only evidence relevant to ownership, actionable scope, completion/cancellation, duplicates, dependencies, estimate, or priority for the supplied candidates. Do not discover unrelated work or run the general source sweep below.
- Fetch full relevant threads/documents where needed. If the budget cannot cover required context, return the unresolved question and exact continuation cursor/source; do not decide from a truncated excerpt.
- Return a compact evidence packet per candidate: stable ID, supported action and owner (or unknown), status at cutoff, plausible duplicate IDs, direct source/version references, uncertainties, and coverage/budget used. Label older context and later changes separately. Evidence of no owner found is not proof that no owner exists.
- Return only these packets to the caller, without a second user-facing report. The caller owns checkpoints, candidate queues, eligibility timers, privacy approvals, final decisions, and all writes. This mode is read-only and does not replace discovery, recovery, or write verification.

The time-frame and reconciliation rules below apply to both modes. The general source collection and work-report result contract apply only outside candidate-focused mode.

## Time frame

- Default to the rolling last 24 hours ending now, using the user's timezone for displayed times.
- Accept an optional natural-language time frame, such as `last 3 days`, or explicit start and end timestamps. Resolve relative durations against the current time once at the start.
- An exact window supplied by a caller takes precedence. Preserve its boundaries and exclusions; do not substitute standup, weekday, or OOO rules.
- Record the resolved start, end, and timezone. Use older context when needed to understand activity, but distinguish it from work performed within the window. Keep later status changes separate from status at the cutoff.

## Source collection

Use the available connectors, APIs, or read-only local history. Start with sources most relevant to the requested outcome, then fill material evidence gaps. Reuse unchanged evidence within the invocation and stop when the requested coverage is complete or the caller's deadline is reached; do not impose an arbitrary call limit on general collection. Report unavailable or unreviewed sources honestly. Follow existing access restrictions and user exclusions:

- GitHub: authored commits, PR creation and updates, reviews, merges, checks, and deployment evidence.
- Linear: issue progress, comments, decisions, and linked work.
- Google Calendar: meetings, attendance context, and OOO information when relevant to the caller.
- Google Drive: meeting notes, including Gemini-generated notes, and relevant documents. Search proactively and follow calendar-linked notes for decisions, commitments, and outcomes; attendance alone is not work.
- Fathom: meeting summaries, action items, and transcripts when needed to clarify decisions, outcomes, or the user's contribution. Use the meeting's occurrence time to place it in the window, not the notes' creation or update time.
- Email: material sent updates, replies, decisions, and commitments.
- Codex tasks: material investigation, planning, browser work, reviews, decisions, and outcomes absent from tracked systems. Discover actual task IDs and read relevant activity within the window.
- Slack: messages and surrounding threads only when the user has authorized Slack review in the current task; retain that authorization when called by another skill.

Follow relevant linked evidence to understand ownership and outcome. Include unshipped analysis and proposals. Do not attribute a teammate's work to the user merely because he appeared in a conversation. Distinguish unavailable or unreviewed sources from sources reviewed with no relevant activity.

## Reconciliation

- Deduplicate related evidence into work items, preserving significant distinct outcomes.
- Reconcile Fathom, Gemini/Google Drive notes, and calendar entries for the same meeting before counting outcomes. Match shared meeting or calendar IDs when available; otherwise use meeting date/time, participants, and topic together. A matching title alone is insufficient, especially for recurring meetings.
- Combine overlapping meeting accounts into one set of outcomes and action items, retaining complementary details and useful source links. Prefer the clearest direct evidence for each claim rather than favoring a notes provider. Preserve conflicting decisions or ownership as uncertainty; do not count duplicate notes as separate work or independent corroboration.
- Prefer the source that proves the claim: GitHub for merge state, deployment-provider evidence for completed deployment, and task or meeting notes for decisions and analysis.
- A merged PR or promotion PR does not prove deployment. Confirm the relevant code reached production before labeling it deployed; distinguish deployment from verified production behavior.
- Reconcile PR state with conversation context so proposals and ownership handoffs remain clear. Preserve uncertainty and conflicting evidence.

## Result contract

Return the exact window, consolidated work items, and source coverage. For each material item, retain:

- Outcome or finding, practical significance, and the user's contribution.
- Workstream, timing, and supported status: deployed and verified, deployed, merged, in progress, proposal/handoff, analysis only, or decision recorded.
- Direct source references and concise evidence supporting status and attribution.
- Material uncertainty, blockers, or immediate follow-ups when present.

When called by another skill, supply this context for its final rendering without publishing a second user-facing report. When invoked alone, present a concise context brief with references and coverage gaps. Summarize private content at the appropriate audience level and omit sensitive details. Collection does not authorize posting messages or modifying source systems.
