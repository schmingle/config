NEVER run a skill if it is marked with `disable-model-invocation: true`, those skills can only be invoked explicitly by the user

## Response presentation

When presenting a collection or set--such as choices, steps, findings, or actions--use a list for easy reading. For choices, always use a numbered list ordered starting with most recommended, and clearly label the recommended option. Link important resources whenever their URLs or paths are known, including PRs, tickets, and files. Do not invent links.

## Private customization

At the start of each task, read `~/.codex/AGENTS-PRIVATE.md` if present and apply its relevant preferences, account map, and local context. This local, untracked file is the canonical location for identifying details and personal customization; the reusable defaults here also work without it. Never copy private settings into tracked files or public artifacts.

## Tools

When a task can be done through several interfaces, prefer an installed CLI, then a connected plugin, then a browser. This applies to services such as GitHub (`gh`), Sentry (`sentry-cli`), AWS (`aws`), and Heroku (`heroku`). Follow an explicit tool request or a workflow's required tool when one is specified.

Check whether a suitable CLI is available before falling back. If the service has a CLI that is not installed, suggest installing it and explain the practical benefit. Use the next available interface to finish the current task when it can do so safely; do not silently install a CLI just to satisfy this preference.

Check a CLI from the same tool-run shell that will use it: locate the executable, run a harmless version or identity command, and verify the intended account and target. Authentication in the app terminal, another shell, or a plugin does not establish authentication in this shell. Distinguish a missing executable, signed-out account, sandbox or network denial, and service authorization failure from their actual error messages.

If a harmless CLI check is blocked by the tool sandbox, retry that specific check through the tool's normal permission or escalation mechanism when available. Do not use Computer Use to operate Codex's terminal, change global sandbox settings, or claim that the user's approval of a CLI overrides tool permissions. If access remains unavailable, use the next safe interface and report the exact blocker. Do not repeatedly retry the same failed command.

For 1Password (`op`), prefer the CLI for approved work. Check `op whoami` in the tool-run shell and select the intended account using the private account map; use an explicit account selector for commands when needed. A desktop-app connection or daemon error may be a sandbox boundary, so test the same read-only command through normal escalation before diagnosing 1Password setup. If the escalated check says the account is signed out, follow the supported `op signin` flow and let the user complete any 1Password prompt. Never print secret values, pass them through chat, or put them in command arguments or logs. If the CLI still cannot authenticate, use the connected 1Password plugin when it meets the task's needs.

## Work and personal accounts

Keep work and personal accounts separate. Use the private account map to select the intended service account and browser profile. Verify the authenticated account before accessing data or making changes, especially when a service is available in both contexts. Do not use a work connection for personal activity, or a personal connection for work activity, merely because it is available. If the intended account remains unclear, ask before accessing either one.

When the private account map identifies a GitHub account used for both work and personal repositories, classify activity by the repository owner or organization, remote URL, and task context; the authenticated identity alone does not determine whether a task is work or personal. Verify the target repository before reading or writing repository data.

## Writing and outbound communication

For substantial writing tasks, prefer delegating to the `writer` agent using `fork_turns="none"` and the compact assignment described in [its workflow](agents/writer.md). This can include messages, documents, proposals, and posts. Include the relevant facts and sources, audience, channel, requested length, current or approved draft, and all applicable corrections. Reuse the same writer for revisions when practical, and check its result against the brief before presenting it. Code-facing prose, daily standups, and writing-guide maintenance retain their owning workflows; involve the writer for drafting when compatible with those workflows.

For email, SMS, and Slack, show the user the exact final message and recipients or destination, then obtain explicit confirmation immediately before sending or posting. If the message or destination changes afterward, show the revised preview and confirm again. This gate applies across conversations and delegated agents. For other channels, follow the authorization and publication rules of the task and its owning workflow; this section does not impose a separate preview-and-confirmation gate.

For delegated and direct writing, resolve the private canonical guide using [the writing workflow's guide-location rules](agents/writer.md#guide-location). Include that resolved path in writer assignments. Briefly disclose a fallback when the writer would otherwise have been used. Do not duplicate style preferences in this routing rule.

## Work management

Use Linear as the durable home for work so the user can switch priorities and resume without reconstructing Codex conversations.

1. **Projects track big rocks.** Propose creating or reusing a project when work involves roughly 10 tickets or at least one week of elapsed delivery time, including coordination, rollout, and acceptance. These are signals, not hard cutoffs; smaller efforts may qualify when they have a distinct outcome or significant coordination. Obtain approval before creating a project or reorganizing existing work.
2. **Keep projects finite.** Each project needs a clear outcome, scope boundary, and completion criteria. Chunk larger programs into bounded versions or phases, such as v0, v1, and v2. Avoid continually expanding a project to absorb every related improvement; capture follow-ups separately.
3. **Labels track ongoing workstreams.** Use labels such as Foundation, Recruiting, Security, and Ops for continuing categories of work. Tickets can carry these labels without belonging to a project. Use a project when a finite initiative emerges within a workstream.
4. **Pins reflect current focus.** The user generally focuses on one or two big rocks at a time. Keep roughly two or three major priorities pinned in Codex; use Linear to track the rest. Do not change pins without a request.
5. **Make switching easy.** Keep each project's current state, next action, blockers, consequential decisions, and important links easy to find. A fresh Codex chat should be able to resume from Linear without recovering previous conversations.
6. **Maintain approved tracking directly in Linear.** Publish project summaries under the [project status update policy](#project-status-updates). For normal ticket progress use native fields/status, PR attachments, and PR/CI integrations first; reserve comments for consequential exceptions, deviations, blockers, or decisions needing attention that native mechanisms do not represent. Keep concise descriptions, milestones, links, and evidence current from verified changes without duplicate progress narratives. Distinguish implementation, deployment, and operational acceptance. Reuse existing records, preserve ownership and relationships, and ask before materially changing scope or ownership.
7. **Keep shared status updates quick to read.** Follow the project status update policy below for project posts. For other external status updates, aim for a five-second scan and at most 30 seconds to read, leading with the outcome, blocker, or next action and linking supporting detail. These limits do not apply to useful supervisor own-chat replies or worker own-chat execution reports, which may be detailed when useful, or to project contracts, ticket specifications, and PR descriptions requiring sufficient context.
8. **Reference tickets by ID.** Include the actual ticket identifier whenever mentioning a ticket, optionally followed by its short title, so Linear can link it automatically. In chat and other formats, link the identifier to the known ticket URL when available; never invent identifiers or links.
9. **Prefer a one-to-one mapping between implementation tickets and PRs.** Split work into scoped tickets or sub-issues as needed, with a clear outcome and validation for each implementation ticket. Parent tickets may track the combined outcome. Preserve coherent, atomic changes and existing work; explain necessary exceptions. Follow the owning workflow's authorization and limits when splitting or creating tickets, and retain approval requirements for material scope or ownership changes.

Keep project management in Linear and maintained technical documentation beside the code.

### Project status updates

1. **Batch meaningful changes.** Publish routine project status updates at most once every two hours, measured from the last published project update, including exceptions. Count a later edit timestamp only when it represents a meaningful published revision. Post only meaningful accumulated changes to project progress, outlook, or next action; unchanged runs skip posting even after two hours. Do not bypass this cadence by editing an existing status update or substituting project comments.
2. **Keep exceptions narrow.** Only a genuinely urgent project risk or verified project completion may justify an immediate post. Do not repeat unchanged exceptions. Routine blockers, questions, pauses, stops, resumes, handoffs, worker dispatches, checkpoints, or individual PR/CI changes do not bypass the cadence. Surface needed human input immediately in the owning supervisor chat and relevant ticket without an extra project post.
3. **Use a short summary and bullets.** Write one summary sentence and two to four useful bullets, usually under 100 words total. Cover the material outcome, blocker or decision, and next action as applicable. Link key tickets by actual ID, PRs, and evidence directly using verified URLs. Omit control metadata, exhaustive activity lists, and details already available in linked records; link the coordination document only when useful, never append its contents.
4. **Keep current state durable separately.** Update native tickets, fields, links, and the maintained supervision coordination document promptly as needed; these writes do not require a project status post or reset its publication window. Supervision cadence and mandatory own-chat reports remain unchanged.

### Project descriptions

Use this structure when creating or materially updating a Linear project. The description is the project's current contract: clear enough for the user to assess the direction and for Codex to execute without reconstructing prior conversations.

```markdown
## Summary
[What this project is, why it matters, and the boundary of this version.]

## Key Decisions
- **Decided — [Choice]:** [Brief rationale and consequential constraints.]
- **Starting assumption — [Choice]:** [What must be validated and when.]
- **Open — [Decision needed]:** [How and when it will be resolved.]

## Goal State

### Key Results
- [ ] [Observable outcome, capability, or measurable result.]

### Completion Validation
- **[Corresponding KR]:** [Scenario or check, expected result, and evidence
  needed to demonstrate completion.]

## Plan
1. **[Phase name]** — [Core intention and resulting capability.]
   Exit: [Condition that proves this phase achieved its purpose.]
   Tracking: [Linked Linear milestone or phase ticket.]

## Context and Guardrails
[Consequential dependencies, exclusions, constraints, unresolved questions,
and source links that are not already covered above.]
```

Apply these directions:

1. **Keep it concise and specific.** Capture the intended outcome and approach; keep implementation details in tickets. Do not invent metrics or targets to fill the template.
2. **Always include Key Decisions.** State explicitly if none have been identified. Treat decided choices as constraints and propose changes before departing from them. Keep assumptions and open decisions visibly distinct from commitments.
3. **Separate results from proof.** KRs describe what must become true. Completion validation explains how to demonstrate it. Use user stories for capabilities and appropriate operational, recovery, reconciliation, or performance checks for other outcomes.
4. **Make phases govern execution.** Preserve each phase's core intention and exit condition so its tickets can be checked for alignment. Identify meaningful dependencies and parallel work.
5. **Maintain one current contract.** Refresh the description when approved goals, decisions, or approach change. Use native milestones and tickets for detailed tracking. Keep current progress, next actions, blockers, and requests for the user in native tickets and the maintained supervision coordination document where applicable. The latest published project update is a concise summary under the reporting policy, with supporting evidence in linked records.

## Delegation

Prefer delegating substantial tasks to a suitable predefined agent. Substantial work includes tasks that may take more than 30 seconds or involve more than 10 steps. Examples include creating PRs, running GitHub workflows or deployment skills, and performing bulk repeated actions. These are signals, not limits: Codex may delegate other work when doing so is useful. Respect explicit instructions to work directly, such as "don't delegate" or "do it yourself."

Delegation is authorized within the task's existing scope and approval boundaries. Prefer a predefined agent whose role fits the work; if none fits, use a general-purpose subagent when useful or do the work directly. The coordinating agent remains responsible for integration, verification, and final delivery.

When delegating, always spawn subagents with `fork_turns="none"`. Pass a compact, self-contained assignment containing the objective, scope and file ownership, constraints and applicable approvals, relevant evidence and file/PR references, and expected deliverable and verification. Do not inherit the parent conversation unless the user explicitly requests full-context inheritance.

## PR independence and dependency stacking

Avoid stacking by default. Create independent PRs from the repository's current default branch (`main` where applicable).

When PR2 must not merge before PR1, stack PR2 on PR1 to enforce that dependency. Establish actual branch ancestry and set PR2's GitHub base to PR1's branch; draft status, comments, descriptions, and Linear dependencies alone are insufficient. This verified dependency is sufficient reason to stack without a separate stacking request.

Stack only when the child requires a concrete API, schema or behavior absent from current main; identify that dependency before choosing its base. Ancestry, ticket order, file overlap and shared rollout plans are insufficient.

Reassess dependencies when splitting or extracting a PR; default to main, not the source branch. Use the smallest prerequisite and keep independent consumers as siblings.

Before exceeding three open PRs in a chain, check for unnecessary edges or separable shared foundations. When a stack is deeper than five open PRs, suggest an audit to see whether it can be split or flattened. Depth alone does not require approval. An explicitly requested linear stack applies only to its requested scope.
