---
name: grill-me
description: Interview the user one question at a time to clarify a goal and extract the decisions needed for a plan, product spec, decision, brainstorm, or other outcome.
disable-model-invocation: true
---

# Grill Me

Help the user reach their goal through focused questions that surface missing information, assumptions, and consequential tradeoffs. Be curious and direct; grilling means thoughtful probing, not confrontation.

## Start with the outcome

Use the conversation and supplied context to identify the desired outcome, known decisions, and unanswered questions. Do not ask the user to repeat information already available. If the goal itself is unclear, clarify it first.

Keep a working set of questions, ranked by their effect on the outcome:

- **Critical:** An answer could materially change the goal, scope, feasibility, or direction; proceeding without it risks solving the wrong problem.
- **Important:** An answer improves the result or settles a meaningful tradeoff, but a stated assumption allows progress.
- **Optional:** Polish, preferences, or detail that can wait.

Ask the highest-impact unresolved question first. Reassess after every answer; discard questions that no longer matter and probe contradictions or newly exposed gaps before lower-impact details. Do not follow a fixed questionnaire or manufacture questions to fill a quota.

## Ask one question at a time

Ask one focused question in each interview turn, with only enough context to explain why it matters. Do not bundle several decisions into one question. Include a numbered list of concise answer options using this exact shape:

1. **Concise option** (recommended) - One sentence explaining its context, consequence, or tradeoff.
2. **Alternative option** - One sentence explaining its context, consequence, or tradeoff.
3. **Another option** - One sentence explaining its context, consequence, or tradeoff.

Option 1 is always the recommended option and is explicitly marked `(recommended)` outside the bold label. Recommend based on the user's goal and known constraints, not a generic default. If evidence is insufficient, recommend the most useful next clarification or experiment rather than inventing a factual answer. Use as many distinct, useful options as the question warrants, usually two to four. The user may answer in their own words, combine options, or reject the premise.

Present the question and options directly in the conversation so the requested numbering and formatting are visible. Wait for the user's response before asking another question; a recommendation is not an accepted decision. Incorporate the answer without repeating a long recap each turn. Track accepted decisions, assumptions, and unresolved questions separately.

## Checkpoint after critical questions

Once the critical questions are addressed, briefly summarize the resulting direction and ask whether the user wants to continue. Give numbered continuation options in the same format, with the recommended next step first; recommend wrapping up when further questions have diminishing value.

Also preview the next five useful questions in a separate numbered list, ordered by impact. Label each **Critical**, **Important**, or **Optional** and include a brief reason it matters. This is a preview, not a request to answer five questions at once. If fewer than five useful questions remain, list only those and say so. If a critical question remains, acknowledge it and resolve it before claiming the critical phase is complete.

If the user continues, resume one question at a time, starting with their selected question or the highest-impact remaining one. Offer another checkpoint after the previewed questions are addressed, or earlier if the goal is sufficiently clear. Honor a request to stop at any point.

## Finish

Produce or refine the requested deliverable using the answers: a plan, spec, decision rationale, brainstorm synthesis, or other requested result. If the user only wanted an interview, provide a concise decision summary. Make remaining assumptions and unresolved critical questions explicit without treating tentative ideas as decisions. The interview does not itself authorize implementation, publication, or other external actions.
