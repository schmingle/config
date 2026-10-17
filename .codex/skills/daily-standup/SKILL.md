---
name: daily-standup
description: Generate the user's evidence-based daily standup from work activity. Use when asked to prepare, regenerate, or improve a daily standup; do not use for weekly updates or project status reports.
---

# Daily Standup

Produce a copy-ready daily standup from the available evidence, not an activity dump.

## Reporting window

- Use an explicit user-supplied window when given. Otherwise report from the start
  of the most recent concluded Daily Standup the user attended until now, resolving
  both boundaries once in the user's timezone.
- Establish attendance from the user's confirmation or reliable attendance evidence,
  such as a participant record or transcript. An invitation or accepted RSVP alone
  is insufficient. Reuse a confirmed boundary in the current conversation.
- If the last attended standup cannot be established, ask for its date/time; continue
  independent source discovery, but do not guess a cutoff or substitute 24 hours.
- State the exact window at the top. Do not include work outside it.

## Gather context

Read and use [gather-context](../gather-context/SKILL.md) to collect and reconcile the evidence. Pass the exact reporting start and end, the user's timezone, any OOO exclusions, and the current task's source authorizations or exclusions. Do not use its rolling last-24-hours default for a standup.

Gather the full range of work in the reporting window before choosing themes. Use the returned work items, references, supported statuses, and coverage gaps to produce the summary below. Keep meaningful unshipped analysis and proposals alongside delivered work. The gather-context skill owns source collection, attribution, deduplication, and delivery verification; this skill owns the standup window, clustering, and synthesis.

## Synthesize themes

1. Gather all available evidence of the user's work in the reporting window through gather-context before deciding what to feature.
2. Consider the evidence as a whole and synthesize the themes of the work: the objectives pursued, problems addressed, or capabilities advanced. Connect related investigations, decisions, implementation, and follow-ups across sources. Do not start with fixed categories or merely turn each artifact into a bullet.
3. Select a small set of themes worth sharing at standup and place the supporting work beneath each. Consolidate overlapping evidence and minor tasks into concise outcomes. Group by meaningful relationships, not just shared tools or terminology; allow genuinely distinct work to stand alone.
4. Rank themes by prominence and value to the audience: material progress, customer or team impact, important decisions, risks, and blockers. Activity volume and PR count alone do not determine rank. Order supporting work by significance within each theme.
5. Edit for a concise, coherent update. Each theme should communicate the main point, and each supporting item should add concrete evidence of progress, a decision, or a relevant next step. Broad evidence collection does not require an exhaustive final inventory.

## Output

- Output only the standup, with no research narrative.
- Use a nested bullet list: concise synthesized themes as top-level bullets, with supporting work underneath. Aim for a handful of themes, usually 3–5 when the evidence supports it; this is a guide, not a quota.
- Write supporting bullets as `Outcome (status) - detail. [Reference](URL)`. Keep them short, clear, and understandable to a mixed technical and non-technical audience. Explain practical progress and keep specialist details in the source links.
- Keep statuses and reference links on the outcome sub-bullets so each item's delivery state remains clear. A genuinely unrelated outcome may stand alone as a top-level outcome bullet; avoid empty themes and unnecessary one-item wrappers.
- Example structure (illustrative themes only):

  ```markdown
  - **Production reliability**
    - Added uptime checks (live) - Detects service outages sooner. [Monitor](URL)
    - Designed browser checks (proposal) - Covers login and key customer flows. [Plan](URL)
  - **Engineering workflow**
    - Automated commitment capture (in progress) - Routes actionable follow-ups into Linear. [Workflow](URL)
    - Expanded regression tests (merged) - Protects common workflows from recurring bugs. [PR](URL)
  ```
- Use truthful statuses such as `deployed`, `merged`, `in progress`, `decision recorded`, or `proposal`. Never upgrade a status based on assumption.
- Preserve distinct delivery states within a theme. If one item merged while related implementation remains open, label them separately rather than assigning the strongest status to the whole theme.
- Keep links last. Use direct source links when available.
- Add one concise italicized source disclosure only for material sources that were unavailable or intentionally not reviewed.

## Quality bar

- Check that the most prominent or worth-sharing themes lead, supported by evidence rather than activity counts.
- Check the final structure: related outcome items should be visibly nested under shared themes. A flat list of all activity should be rare; reconsider shared objectives and initiatives before concluding every item is unrelated. Keep grouping meaningful rather than forcing arbitrary buckets.
- Preserve uncertainty when evidence is incomplete.
- Do not expose sensitive details from private notes, email, or Codex task history. Summarize at the appropriate audience level.
