NEVER run a skill if it is marked with `disable-model-invocation: true`, those skills can only be invoked explicitly by the user

## Tools

When a task can be done through several interfaces, prefer an installed CLI, then a connected plugin, then a browser. This applies to services such as GitHub (`gh`), Sentry (`sentry-cli`), AWS (`aws`), and Heroku (`heroku`). Follow an explicit tool request or a workflow's required tool when one is specified.

Check whether a suitable CLI is available before falling back. If the service has a CLI that is not installed, suggest installing it and explain the practical benefit. Use the next available interface to finish the current task when it can do so safely; do not silently install a CLI just to satisfy this preference.

## Work and personal accounts

Keep work and personal accounts separate. Most connected tools are for work; personal activity is mainly in the personal Chrome profile and a small set of services. Read the local, untracked account map at `~/.codex/private/account-context.md` when choosing an account or tool. Verify the authenticated account before accessing data or making changes, especially when a service is available in both contexts. Do not use a work connection for personal activity, or a personal connection for work activity, merely because it is available. If the intended account remains unclear, ask before accessing either one.

## Writing and outbound communication

Prefer delegating writing tasks to the `writer` agent using `fork_turns="none"` and the compact assignment described in [its workflow](agents/writer.md). This includes short edits, messages, documents, proposals, and posts. Include the relevant facts and sources, audience, channel, requested length, current or approved draft, and all applicable corrections. Reuse the same writer for revisions when practical, and check its result against the brief before presenting it. Code-facing prose, daily standups, and writing-guide maintenance retain their owning workflows; involve the writer for drafting when compatible with those workflows.

Before sending, posting, publishing, or sharing any written communication, present Khang with a preview of the exact final content and destination or recipients, then ask for explicit confirmation to send that version. This applies to email, SMS, Slack, GitHub comments and reviews, documents, and other channels, across conversations and delegated agents. A request to draft or an earlier general authorization does not replace this final confirmation. If the content or destination changes afterward, present the revised preview and confirm again.

If the writer is unavailable or delegation is disallowed, follow [the writing workflow](agents/writer.md) and the private canonical guide at `~/.codex/writing/style-guide.md` directly, and briefly disclose the fallback. Do not duplicate style preferences in this routing rule.

## Subagent context

When delegation is authorized, always spawn subagents with `fork_turns="none"`. Pass a compact, self-contained assignment containing the objective, scope and file ownership, constraints and applicable approvals, relevant evidence and file/PR references, and expected deliverable and verification. Do not inherit the parent conversation unless Khang explicitly requests full-context inheritance. This rule does not itself authorize delegation.

## PR independence and dependency stacking

Avoid stacking by default. Create independent PRs from the repository's current default branch (`main` where applicable).

When PR2 must not merge before PR1, stack PR2 on PR1 to enforce that dependency. Establish actual branch ancestry and set PR2's GitHub base to PR1's branch; draft status, comments, descriptions, and Linear dependencies alone are insufficient. This verified dependency is sufficient reason to stack without a separate stacking request.

Stack only when the child requires a concrete API, schema or behavior absent from current main; identify that dependency before choosing its base. Ancestry, ticket order, file overlap and shared rollout plans are insufficient.

Reassess dependencies when splitting or extracting a PR; default to main, not the source branch. Use the smallest prerequisite and keep independent consumers as siblings.

Before exceeding three open PRs in a chain, check for unnecessary edges or separable shared foundations. Depth alone does not require approval. An explicitly requested linear stack applies only to its requested scope.
