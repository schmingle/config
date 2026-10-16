NEVER run a skill if it is marked with `disable-model-invocation: true`, those skills can only be invoked explicitly by the user

## Tools

When a task can be done through several interfaces, prefer an installed CLI, then a connected plugin, then a browser. This applies to services such as GitHub (`gh`), Sentry (`sentry-cli`), AWS (`aws`), and Heroku (`heroku`). Follow an explicit tool request or a workflow's required tool when one is specified.

Check whether a suitable CLI is available before falling back. If the service has a CLI that is not installed, suggest installing it and explain the practical benefit. Use the next available interface to finish the current task when it can do so safely; do not silently install a CLI just to satisfy this preference.

Check a CLI from the same tool-run shell that will use it: locate the executable, run a harmless version or identity command, and verify the intended account and target. Authentication in the app terminal, another shell, or a plugin does not establish authentication in this shell. Distinguish a missing executable, signed-out account, sandbox or network denial, and service authorization failure from their actual error messages.

If a harmless CLI check is blocked by the tool sandbox, retry that specific check through the tool's normal permission or escalation mechanism when available. Do not use Computer Use to operate Codex's terminal, change global sandbox settings, or claim that the user's approval of a CLI overrides tool permissions. If access remains unavailable, use the next safe interface and report the exact blocker. Do not repeatedly retry the same failed command.

For 1Password (`op`), prefer the CLI for approved work. Check `op whoami` in the tool-run shell and select the intended account using the private account map; use an explicit account selector for commands when needed. A desktop-app connection or daemon error may be a sandbox boundary, so test the same read-only command through normal escalation before diagnosing 1Password setup. If the escalated check says the account is signed out, follow the supported `op signin` flow and let the user complete any 1Password prompt. Never print secret values, pass them through chat, or put them in command arguments or logs. If the CLI still cannot authenticate, use the connected 1Password plugin when it meets the task's needs.

## Work and personal accounts

Keep work and personal accounts separate. Most connected tools are for work; personal activity is mainly in the personal Chrome profile and a small set of services. Read the local, untracked account map at `~/.codex/private/account-context.md` when choosing an account or tool. Verify the authenticated account before accessing data or making changes, especially when a service is available in both contexts. Do not use a work connection for personal activity, or a personal connection for work activity, merely because it is available. If the intended account remains unclear, ask before accessing either one.

## Writing and outbound communication

Prefer delegating writing tasks to the `writer` agent using `fork_turns="none"` and the compact assignment described in [its workflow](agents/writer.md). This includes short edits, messages, documents, proposals, and posts. Include the relevant facts and sources, audience, channel, requested length, current or approved draft, and all applicable corrections. Reuse the same writer for revisions when practical, and check its result against the brief before presenting it. Code-facing prose, daily standups, and writing-guide maintenance retain their owning workflows; involve the writer for drafting when compatible with those workflows.

For email, SMS, and Slack, show Khang the exact final message and recipients or destination, then obtain explicit confirmation immediately before sending or posting. If the message or destination changes afterward, show the revised preview and confirm again. This gate applies across conversations and delegated agents. For other channels, follow the authorization and publication rules of the task and its owning workflow; this section does not impose a separate preview-and-confirmation gate.

If the writer is unavailable or delegation is disallowed, follow [the writing workflow](agents/writer.md) and the private canonical guide at `~/.codex/writing/style-guide.md` directly, and briefly disclose the fallback. Do not duplicate style preferences in this routing rule.

## Subagent context

When delegation is authorized, always spawn subagents with `fork_turns="none"`. Pass a compact, self-contained assignment containing the objective, scope and file ownership, constraints and applicable approvals, relevant evidence and file/PR references, and expected deliverable and verification. Do not inherit the parent conversation unless Khang explicitly requests full-context inheritance. This rule does not itself authorize delegation.

## Delegation preference

Prefer delegating work to a suitable predefined agent unless Khang specifies otherwise, such as "don't delegate." This preference authorizes delegation within the task's existing scope and approval boundaries; follow the Subagent context requirements above. Choose only agents whose defined roles fit the work. If none is suitable, do the work directly. The coordinating agent remains responsible for integration, verification, and final delivery.

## PR independence and dependency stacking

Avoid stacking by default. Create independent PRs from the repository's current default branch (`main` where applicable).

When PR2 must not merge before PR1, stack PR2 on PR1 to enforce that dependency. Establish actual branch ancestry and set PR2's GitHub base to PR1's branch; draft status, comments, descriptions, and Linear dependencies alone are insufficient. This verified dependency is sufficient reason to stack without a separate stacking request.

Stack only when the child requires a concrete API, schema or behavior absent from current main; identify that dependency before choosing its base. Ancestry, ticket order, file overlap and shared rollout plans are insufficient.

Reassess dependencies when splitting or extracting a PR; default to main, not the source branch. Use the smallest prerequisite and keep independent consumers as siblings.

Before exceeding three open PRs in a chain, check for unnecessary edges or separable shared foundations. Depth alone does not require approval. An explicitly requested linear stack applies only to its requested scope.
