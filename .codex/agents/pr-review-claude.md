# Claude PR review handoff

Use this for `pr-review-high` and explicitly assigned Claude trials, together with
[the shared review contract](pr-review.md) and [shared Claude execution contract](claude.md). The default `pr-review` runs natively.
Agent descriptions define routing; the shared contract defines review standards and handoff requirements.
The reviewer selects relevant instructions and source context, expanding beyond the
supplied brief as needed under [the context policy](context.md).
The wrapper prepares, verifies, and performs any authorized publication; one Claude
session at a time supplies the independent analysis. Neither reviewer delegates further.

## Execution settings

[The execution profile](scripts/claude-review.toml) owns Claude's model, effort,
display name, and tool permissions. The helper records that profile and its exact
reviewer attribution in each bundle. Agent TOMLs own native wrapper settings.
Do not repeat execution settings in this guide or silently substitute them.

Claude is trusted on this machine. The runner permits ordinary shell commands and
file tools rather than maintaining fragile command-prefix rules. Task scope still
applies: review is analysis-only; tool access does not authorize publication, source
changes, test runs, installs, external mutations, or additional reviewers. Preserve
normal subscription authentication and inherited Linear access.

## Prepare

1. Start the wrapper with `fork_turns="none"`. Supply repository/PR, pinned head,
   actual base and merge-base, mode/scope, absolute finish-by, publication permissions,
   the exact coordinator-supplied risk report body, rating, assessed snapshot/provenance,
   any existing source URL, and evidenced prior coverage or an escalation question
   when applicable. Keep
   writer-private conversation and coordinator conclusions out of the assignment.
2. Verify repository identity and live PR state. Collect full paginated GitHub
   description, discussion, findings, and relevant check evidence. Save complete
   responses outside the checkout. For blind benchmarks, use archived GitHub evidence
   from before the baseline review and keep baseline reports out of reviewer input.
3. Create or verify a fresh, clean detached worktree at the pinned head, with the
   actual base and enough ancestry available. Each simultaneous review gets its own
   directory. Never use an active writer checkout or install dependencies for review.
4. Before spending model tokens, run the helper under permissions that support its
   authenticated `claude auth status` check and write probe in the actual session
   directory. Preserve the existing login, configuration directory, and Linear access.
   If preflight fails inside the sandbox, request authorized command-level escalation;
   do not copy credentials or disable persistence to bypass it.
5. Use [the helper](scripts/claude_review.py) to prepare and run the bundle; see its
   [commands and specification](scripts/README.md). It copies evidence unchanged,
   rejects visible API errors/incomplete pagination, selects `AGENTS.override.md`
   before `AGENTS.md`, and includes applicable global/ancestor/testing guidance.
   Supply additional topical or configured fallback guides explicitly. It does not
   prove that every REST page was fetched; collection completeness remains yours.

## Required Linear access

Verify `claude mcp list` in the same execution environment, then require successful
live reads in the actual review session. Codex connectors are not inherited by the
CLI. Keep `ToolSearch` available for deferred tools; a connected status or an empty
initial tool list does not establish usable or missing access.

The current connector is `claude.ai Linear` at `https://mcp.linear.app/mcp`. Discover
its actual issue/comment read tools at runtime. For linked PRs, read the issue and
relevant comment pages; for unlinked PRs, verify a minimal identity read instead.
Do not launch with an empty strict MCP configuration, export credentials, or install
another integration to bypass authentication. Missing required access means
Incomplete without sign-off; surface the exact blocker and unblock action while
continuing independent source inspection. The shared contract owns context judgments.

## Run and settle

Start one fresh session for the assignment, with only one active reviewer process.
Use a focused `--resume` for a substantive coverage gap or new evidence, after the
helper verifies the actual persisted transcript. Never blindly resume a missing
session or use an unrelated session. Resume preserves the original launch profile
and saves separate artifacts. The helper checks authenticated session storage before
launch and records whether the transcript exists afterward. Missing persistence is
an infrastructure gap to surface, even when the analysis otherwise completed.

Allow at most one replacement session for a confirmed missing transcript, invalid
structured output, or CLI execution failure, after diagnosing/correcting its cause
and verifying all owned processes are settled. Use the helper's `--replace-failed`
and matching `--recovery-reason`; it enforces the limit and original deadline. Keep
the pinned evidence, reviewer settings, and publication rules. A replacement must
establish full coverage; never treat partial prior analysis as sign-off. Do not
replace a reviewer just to obtain a better verdict, reset the deadline, or reprepare
a bundle to evade the recovery limit. If recovery fails, return Incomplete with the
concrete blocker. Old bundle formats require fresh preparation; explicit retries of
historical failed runs still count toward the assignment's single replacement.

Use the helper's `--json-schema` result in `structured_output`. Human prose in
`result` is diagnostic, not the machine report. Output shape, process success, and a
saved transcript are distinct from coverage: inspect actual source/tool evidence,
including relevant retained implementations, interfaces, and deployment boundaries.
A name search alone does not prove surviving contracts. Request a focused same-session
continuation for material missing coverage, or the bounded replacement if that
session is unavailable. Withhold sign-off until coverage is established.

Reserve publication/cleanup time before the analysis deadline. The helper terminates
and waits for its owned process on timeout, interruption, and unexpected errors;
SIGTERM enters the same cleanup path. On cancellation, inspect `process.json` and
verify settlement before releasing the checkout. An abrupt SIGKILL or machine crash
can prevent cleanup: the caller must reconcile the recorded owned PID/session.
Never claim an unaccounted reviewer stopped.

## Verify and publish

- Verify the actual model/effort, valid report, pinned final HEAD, clean checkout,
  source/test/caller coverage, full discussion, actual Linear reads, unchanged supplied
  risk rating/report link, any risk contradictions, and grounded
  findings with valid anchors. Process success or a JSON report is not sign-off.
- Refresh live PR head/base/discussion before any authorized publication. Follow the
  shared contract's review template, assessments, revalidation, inline findings,
  COMMENT publication, attribution, and readback rules without substituting a wrapper
  LGTM. Do not perform a second risk assessment or post a separate risk report. Missing reports or unresolved material
  contradictions return to the coordinator; incomplete coverage remains Incomplete.
- Keep raw evidence, session/process IDs, launch arguments, report, and diagnostics
  outside the worktree. Once the owned process is settled, remove only that review's
  clean checkout, or return it to the coordinator if the coordinator owns cleanup.
  Preserve unexpected changes and unrelated work.
- Keep telemetry for diagnosis. For comparisons include every necessary continuation
  and failed/incomplete attempt. Use the final cumulative cost once per session;
  API-equivalent cost is not subscription quota consumption. Disclose live Linear
  timing differences when benchmarking historical GitHub snapshots.
