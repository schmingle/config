---
name: writing-guide-audit
description: Interactively review a personal writing guide one channel and intent at a time, incorporate feedback, and locally commit the approved guide with an audit record. Use when auditing or refining a writing guide, not for ordinary drafting.
---

# Writing Guide Audit

Run a conversational sample review, then regenerate and locally commit the guide the user approves. Preserve the user's voice through concrete examples rather than turning every correction into a universal rule.

The audit coordinator owns guide maintenance, user review, and approved finalization; ordinary writing-agent routing does not transfer that ownership. A writing agent may draft sample alternatives when assigned and delegation is authorized, but cannot approve preferences or finalize the guide.

## Resolve and prepare

- Use the canonical path supplied by `writing-guide-init` or explicitly by the user, including a path established in private preferences. Otherwise resolve a nonempty `CODEX_HOME`, falling back to the current user's home plus `.codex`, and use `<codex-home>/writing/style-guide.md`. This shared guide remains in the Codex home when used from Claude Code; do not relocate it to `~/.claude`. Never hardcode a username or modify system environment variables.
- Every invocation starts a fresh audit from the canonical guide and the current request. Do not read or write persistent audit progress, resume a prior audit, or carry forward a next-group queue. Read an initialization draft only when handed off in the current task or explicitly supplied by the user. Resolve the intended writer from that context.
- If neither a guide nor an initialization draft exists, offer to invoke `writing-guide-init` or work from a user-supplied guide. Do not fabricate an established style profile.
- Inspect Git state in the guide directory before changing files. Require a dedicated local repository rooted exactly at that directory; don't accidentally use an enclosing application, home, or agent configuration repository. For a new profile, a dedicated local repository may be initialized as part of this authorized workflow. Never configure a remote or push personal content automatically. See [persistence](references/persistence.md).
- If an existing guide repository has unrelated uncommitted or staged work, show it and obtain direction before changes. Recognize tracked audit work already authorized in this same session and reuse prior decisions. Do not discard, stash, reset, or silently include unrelated work.
- Keep the canonical guide's SHA-256 (or absence) in the current conversation as the baseline. Keep the review draft separate from the canonical guide until final approval. A prior draft is not a pending audit; preserve unrelated files without treating them as resumable state.
- Interpret sample provenance and review status independently, including in older guides with a single combined label. User-authored describes provenance, not approval for inclusion; approved describes review status, not authorship. Preserve explicit approvals and candidate/provisional labels. Treat an unstated dimension as unknown rather than inferring it or requiring a format migration.

## Prioritize and introduce

Rank channel/intent combinations by the user's stated priorities, then observed usage from source-backed samples. Use collection windows and observed sample counts only when available and supported; never infer usage from generated examples. If metadata is missing, mark it unknown and prioritize from the current request and available source evidence. Do not invent counts or require a rebuild or new collection just to supply missing metadata. Explain uneven source coverage briefly. Ask which channels matter most only if the guide and conversation don't establish it.

Start with a short explanation that you'll review one combination at a time and the user can comment, rewrite, skip, or stop. Do not dump the full questionnaire. Preserve sample provenance, explicit preferences, and exclusions in the guide. Select scope afresh for this invocation; prior review status does not create a progress queue or prevent revisiting a group. Within this audit, do not repeatedly ask for approval already given.

## Interactive loop

1. Present one channel-plus-intent group. Start with one representative sample and a short bullet list of observed/applied traits. Include a second sample from the same group when it reveals an important difference; otherwise introduce it after initial feedback. Keep replies proportionate to the channel, especially Slack.
2. Ask for comments or the user's rewritten version. End the turn to let them respond. Never answer for the user, infer approval from silence, or advance while feedback is pending. Tool requests for optional input are not substitutes for this review turn.
3. Interpret feedback in context. Preserve their exact rewrite, record why framing or rhythm changed, and distinguish explicit preferences from your own inference. A typo correction doesn't automatically create a universal punctuation rule. “No strong feelings” or “skip” means provisional/deferred, not stylistic endorsement.
4. If the user requests variants, generate them within the same group, with traits applied, and await selection. Incorporate refinements until that group is accepted or deferred. Show an integrated version when useful; don't force another confirmation if the user has already accepted it.
5. Keep feedback and current review position in the conversation. Preserve exact accepted wording and original provenance in the review draft when preparing the proposal. Do not create `audit-progress.md`, checkpoints, paused/closed state records, or next-item metadata.
6. In the same response that acknowledges clear acceptance or a skip, present the next highest-priority unreviewed group. Don't wait for a separate “next.” If feedback is unresolved, remain on that group. Continue until the requested scope is reviewed or the user wants to stop.

When the user says stop, done, or equivalent, end the audit immediately. Do not label it paused, record workflow state, offer resumption, or ask more review questions. A later invocation is a fresh audit. Stopping alone does not authorize replacing or committing the canonical guide; finalization requires the approval below. Retain any existing proposal as content only, without adding closure metadata.
## Regenerate, review, and commit

1. Regenerate the single Markdown review draft from accepted edits, preserving source labels, original samples, exclusions, and unreviewed groups. Apply the existing guide's format; when needed, discover `writing-guide-init` and read its `references/guide-format.md` rather than invent a second schema.
2. Present a concise list of material changes and a clickable link to the entire proposed guide. Include audit coverage, any skipped groups, and the proposed audit record. Ask the user to approve this version for saving and a local commit. Approval of individual samples does not replace final-guide approval unless the user explicitly authorized finalizing the exact resulting guide.
3. On requested revisions, update the proposal and return for review. Do not require repeating approval already given to the same version and save/commit action.
4. After final approval, verify the canonical guide still matches the baseline. If it changed externally, preserve both versions and reconcile with the user. Do not overwrite concurrent edits. Check the final draft contains the exact approved content and audit record.
5. Update the canonical guide and commit only that guide to its local Git repository using [persistence](references/persistence.md). Keep content edits through the environment's supported file-editing tool. Verify the commit and final file. A failed commit is incomplete delivery; report the exact state and resolve routine failures without claiming success.
6. Even with no style changes, update the guide's audit record and last-finalized timestamp, and physically touch it. The content timestamp makes the audit visible in Git; a bare `touch` is insufficient. Only advance last-complete-audit when all intended groups were reviewed. Partial audits record their coverage honestly.

Report the canonical path, short commit ID, audit coverage, and material changes. Do not send posts or messages to external recipients, change global Git identity, rewrite Git history, or publish this repository as part of the audit.
