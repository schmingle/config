# Single-document writing guide format

Use the following order. Render a finished document, not empty template headings. Existing personal guides may use equivalent headings; preserve meaningful user choices.

## Title and metadata

- Writer's preferred name.
- Schema version (start at 1), guide status, and last updated time.
- Last audit activity time, last finalized audit time, and last complete audit time. Use ISO 8601 timestamps with timezone. Unknown dates remain unknown, not invented.
- Audit coverage: complete, partial, deferred, or pending final approval. A finished partial audit does not mean all groups were reviewed.
- Exact evidence window, source coverage, identity basis, and limitations. Keep sensitive identifiers minimal.

## Purpose and context

Describe audience, relationships, typical writing needs, excluded workflows, and how to use this guide. Generated scenarios are examples, not factual work reports.

Define two independent sample properties: provenance (user-authored, assistant-generated, adapted, or redacted) and review status (approved, provisional, candidate, skipped, or superseded). Being authored by the user does not prove it was reviewed for inclusion. Being approved does not prove the user originally authored it.

## General guidelines

Cover voice, purpose, structure, level of detail, evidence and confidence, collaboration, personal communication, editing expectations, and channel adaptation. Mark explicit user requirements separately from inferred patterns. Use samples to show nuance rather than enumerate brittle exceptions or mandatory stock phrases.

Where the user's long-form preference matches the reviewed structure, explain the distinct purpose of tl;dr, Summary, and optional Background/Problem. Otherwise record that user's chosen structure rather than exporting someone else's preferences.

## Channel and intent index

List stable group IDs, channel, intent, observed unique sample count, evidence strength, priority basis, and review state. Counts refer to the stated sample window, not total usage. Give user-prioritized groups precedence. Record exclusions and deferred groups.

## Samples by channel and intent

For each group, give audience/relationship and relevant progression or stakes. Include multiple complementary examples, normally two or three, without flooding the user during interactive review.

For each sample include:

- Stable sample ID and a short scenario label.
- Provenance and review status, with date when known.
- Direct source URL or local task ID and turn/time; label unavailable sources. No invented citations.
- Exact authored text in a blockquote or suitable literal block preserving paragraphs, punctuation, and emoji.
- A short bullet list of traits observed in actual text or applied to generated candidates. Say which is which.
- Material user corrections and why they mattered. Keep original and accepted revision distinguishable; avoid retaining needless drafts.

Show unavailable evidence plainly. Do not infer punctuation, sign-offs, or general style from a Gmail shortcut whose actual expansion is unknown. Label redactions and do not infer style from them.

## Maintaining and auditing

Keep source-backed examples and explicit corrections authoritative over hypotheses. Explain how to add samples, preserve history, audit one group at a time, and defer groups the user rarely uses. Keep personal samples private by default.

## Audit record

Store the latest audit's timestamp, reviewed group IDs, deferred/skipped IDs, scope, significant accepted changes or "no style changes," and final approval status. Prior audit records can live in local Git history to prevent the guide from growing indefinitely. Update this content even when an audit changes no writing rules: Git does not track filesystem modification times.
