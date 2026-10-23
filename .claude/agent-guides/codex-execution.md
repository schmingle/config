# Codex role execution from Claude

The native Claude agent is an orchestration wrapper. The shared
[role launcher](../../scripts/agent-launch.md) reads the corresponding public Codex TOML for
the actual model, effort, and role instructions. Codex executors retain their canonical Codex guide paths; native Claude roles use their Claude counterparts. It never launches Claude again. Native Claude roles execute
directly and must not launch another copy of their role. Keep both public provider folders installed;
`AGENT_LAUNCH_ROOT`, when set, selects the complete configuration checkout for role definitions, profiles, and helpers. Otherwise resolved installed symlinks locate that checkout. `CODEX_HOME` still belongs to the Codex CLI environment; it does not select a second role-definition source for this launcher.

## Prepare and execute

1. Read [the shared launcher contract](../../scripts/agent-launch.md). Use a compact, self-contained assignment with the objective, scope and owned
   paths (empty for analysis), constraints, actual approvals/prohibitions, known
   facts, source links, expected result, verification, and absolute finish-by.
   Follow [context selection](context.md). Pass the assignment unchanged; do not
   add inferred approval or transmit unrelated private context or credentials.
2. Verify the exact target checkout, repository identity, branch, HEAD, and local
   changes. Use the assigned checkout, including intentional local work, subject
   to repository isolation rules. For review, prepare or verify a separate clean
   detached checkout pinned to the assigned head with actual base and ancestry.
   Supply the full risk report, factual PR evidence, publication permissions, and
   accepted prior coverage without writer/coordinator conclusions. The runner
   creates no worktree and does not assume a default branch.
3. Save the JSON assignment defined by the shared contract outside the checkout and public configuration repository with
   restrictive permissions. Choose a new private output directory alongside it.
   Preserve the original deadline. A missing deadline may be set once from the
   assignment's stated time budget; ask the coordinator if neither is supplied.
4. Select `read-only` for analysis and review. `pr-green`, `pr-review`, and `pr-risk`
   enforce that filesystem sandbox. Select `workspace-write` only for explicitly
   assigned edits to owned files, including an explicitly assigned writer draft
   artifact. Filesystem permissions do not authorize GitHub or other external
   writes: the brief must preserve those exact permissions and restrictions.
5. Run in the foreground, replacing the placeholders with the actual inputs:

   ```sh
   <config-root>/scripts/agent-launch --role <assigned-role> --assignment <private-task.json> --checkout <absolute-checkout> --output <new-private-output> --finish-by <absolute-ISO-deadline> --sandbox <read-only-or-workspace-write>
   ```

   Resolve `<config-root>` through the installed symlink or `AGENT_LAUNCH_ROOT`, as the shared contract describes. The old `codex-delegate.sh --brief-file` command remains a read-only compatibility entry point; writable tasks require the structured JSON assignment and explicit owned paths.

   The runner checks the actual CLI version and `codex login status`, reads its
   canonical role settings, disables further agent delegation, and bounds its
   process by finish-by. `CODEX_BIN` may select an installed executable. A missing
   CLI, authentication failure, sandbox denial, or unavailable capability returns
   its actual blocker. Use normal permission escalation when authorized; never
   bypass hooks or sandboxing, silently change the model, or do substitute work.
   `--dry-run` prepares the private command/settings bundle without model use.
   Wait through successive tool calls as needed while keeping the coordinator
   informed. Never detach, fire and forget, or launch a duplicate invocation.

## Verify and return

The output contains the unchanged brief, canonical execution identity, exact
launch command, initial/final Git state, JSONL events, diagnostics, final report,
and process-settlement record. It is private runtime state, not public config.
The runner reuses the shared Codex process-group cleanup, including timeout and
interruption handling. A recorded running group or settlement error is a blocker;
reconcile it before starting another attempt or releasing the checkout. Do not
blindly retry partial work or extend the original deadline.

Read the report, events, process record and final checkout state. Verify material
claims against source, changed files, actual checks, and any published artifact.
For PR review/risk, use the recorded executor model/effort and derived attribution,
after verifying the launch and successful execution; Haiku frontmatter identifies
the wrapper only. Required live Linear access must succeed inside the Codex
execution environment; the Claude wrapper's connection is not inherited evidence.
Do not claim a clean review from a missing report, unsupported summary, incomplete
coverage, failed publication, or process exit alone.

Return the verified outcome, relevant file/PR links, checks, actual gaps, partial
changes, permission denials, remaining decisions, and whether writes stopped.
The runner never stages, commits, pushes, opens PRs, changes hooks, or publishes on
its own. The executor may perform only task-authorized actions under repository
guidance, including checks, protected-behavior gates, and commit attribution.
