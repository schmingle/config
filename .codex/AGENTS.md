NEVER run a skill if it is marked with `disable-model-invocation: true`, those skills can only be invoked explicitly by the user

## Outbound communication

- **Email and SMS:** Show Khang the exact final text and recipients, then obtain explicit confirmation immediately before sending.
- **Slack:** Obtain explicit authorization to post. Once a message or workflow is authorized, review the final content and destination, then post within that scope.

These rules apply across conversations and to delegated agents.

## Subagent context

When delegation is authorized, always spawn subagents with `fork_turns="none"`. Pass a compact, self-contained assignment containing the objective, scope and file ownership, constraints and applicable approvals, relevant evidence and file/PR references, and expected deliverable and verification. Do not inherit the parent conversation unless Khang explicitly requests full-context inheritance. This rule does not itself authorize delegation.

## Writing

For substantive writing in Khang's voice (messages, documents, proposals, and posts), delegate to the `writer` agent using `fork_turns="none"` and the compact assignment described in [its workflow](agents/writer.md). Include the relevant facts and sources, audience, channel, requested length, current or approved draft, and all applicable corrections. Reuse the same writer for revisions when practical, and check its result against the brief before presenting it.

Keep trivial edits in the current chat unless Khang requests the writer. Writing-guide initialization and audits follow their respective skills under the coordinating agent; do not route maintenance itself to the writer. Code-facing prose and daily standups follow their owning workflows. If the writer is unavailable or delegation is disallowed, follow [the writing workflow](agents/writer.md) and the private canonical guide at `~/.codex/writing/style-guide.md` directly, and briefly disclose the fallback. Do not duplicate style preferences in this routing rule or treat drafting as authorization to send or publish.

## PR independence and dependency stacking

Avoid stacking by default. Create independent PRs from the repository's current default branch (`main` where applicable).

When PR2 must not merge before PR1, stack PR2 on PR1 to enforce that dependency. Establish actual branch ancestry and set PR2's GitHub base to PR1's branch; draft status, comments, descriptions, and Linear dependencies alone are insufficient. This verified dependency is sufficient reason to stack without a separate stacking request.

Stack only when the child requires a concrete API, schema or behavior absent from current main; identify that dependency before choosing its base. Ancestry, ticket order, file overlap and shared rollout plans are insufficient.

Reassess dependencies when splitting or extracting a PR; default to main, not the source branch. Use the smallest prerequisite and keep independent consumers as siblings.

Before exceeding three open PRs in a chain, check for unnecessary edges or separable shared foundations. Depth alone does not require approval. An explicitly requested linear stack applies only to its requested scope.

Do not create draft PRs or convert PRs to draft unless Khang explicitly requests it. Dependent PRs may be reviewed before their prerequisites merge, but must remain based on their prerequisite branches. Prominently identify those prerequisites. After they merge into the default branch, reconcile each child's ancestry, base and remaining diff, and refresh applicable checks and review evidence before merging. Never merge a child into an unmerged parent branch.

Do not merge prerequisites without separate merge authorization. Regression coverage normally precedes implementation in the same PR; separate regression and implementation PRs require an explicit request for that workflow.
