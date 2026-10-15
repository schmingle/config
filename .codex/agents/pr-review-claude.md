# Claude PR review handoff

Use this for `pr-review-high` and explicitly assigned Claude trials, together with
[the shared review contract](pr-review.md). The default `pr-review` runs natively.
Agent descriptions define routing; the shared contract defines review standards and handoff requirements.
The reviewer selects relevant instructions and source context, expanding beyond the
supplied brief as needed under [the context policy](context.md).
The wrapper prepares, verifies, and performs any authorized publication; one Claude
session supplies the independent analysis. Neither reviewer delegates further.

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
   and evidenced prior coverage or an escalation question when applicable. Keep
   writer-private conversation and coordinator conclusions out of the assignment.
2. Verify repository identity and live PR state. Collect full paginated GitHub
   description, discussion, findings, and relevant check evidence. Save complete
   responses outside the checkout. For blind benchmarks, use archived GitHub evidence
   from before the baseline review and keep baseline reports out of reviewer input.
3. Create or verify a fresh, clean detached worktree at the pinned head, with the
   actual base and enough ancestry available. Each simultaneous review gets its own
   directory. Never use an active writer checkout or install dependencies for review.
4. Use [the helper](scripts/claude_review.py) to prepare and run the bundle; see its
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

Start one fresh session for the assignment. Use a focused `--resume` only when a
substantive coverage gap or new evidence requires continuation of that same review;
never use an unrelated prior session. Resume preserves the original launch profile
and saves separate artifacts. Old bundle formats must be prepared again.

Reserve publication/cleanup time before the analysis deadline. The helper terminates
and waits for its owned process on timeout, interruption, and unexpected errors;
SIGTERM enters the same cleanup path. On cancellation, inspect `process.json` and
verify settlement before releasing the checkout. An abrupt SIGKILL or machine crash
can prevent cleanup: the caller must reconcile the recorded owned PID/session.
Never claim an unaccounted reviewer stopped.

## Verify and publish

- Verify the actual model/effort, valid report, pinned final HEAD, clean checkout,
  source/test/caller coverage, full discussion, actual Linear reads, and grounded
  findings with valid anchors. Process success or a JSON report is not sign-off.
- Refresh live PR head/base/discussion before any authorized publication. Follow the
  shared contract's review template, assessments, revalidation, inline findings,
  COMMENT publication, attribution, and readback rules without substituting a wrapper
  LGTM. Incomplete coverage remains Incomplete.
- Keep raw evidence, session/process IDs, launch arguments, report, and diagnostics
  outside the worktree. Once the owned process is settled, remove only that review's
  clean checkout, or return it to the coordinator if the coordinator owns cleanup.
  Preserve unexpected changes and unrelated work.
- Keep telemetry for diagnosis. For comparisons include every necessary continuation
  and failed/incomplete attempt. Use the final cumulative cost once per session;
  API-equivalent cost is not subscription quota consumption. Disclose live Linear
  timing differences when benchmarking historical GitHub snapshots.
