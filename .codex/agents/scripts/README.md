# Claude review preparation and launch

This helper performs no publication and no source edits. It standardizes the Claude-backed `pr-review-high` execution while the default `pr-review` runs natively on Sol xhigh. Reviewer definitions, priorities, assessments, and the posted template stay in [../pr-review.md](../pr-review.md).

1. Prepare a fresh, clean detached worktree at the verified PR head. Collect complete paginated GitHub evidence and identify applicable guidance. Do not include private author/coordinator conclusions or a baseline review report in a blind benchmark.
2. Write a specification with `repo`, `number`, `head`, `base`, `merge_base`, `base_ref`, `title`, `body`, `linked_issues`, `finish_by` (ISO 8601 with timezone), `evidence` (output filename to raw source path), and optional `guidance` paths. Set `benchmark: true` only for authorized historical snapshot tests. In normal reviews the caller remains responsible for live eligibility, snapshot/discussion refresh, authorized publication/readback, and worktree cleanup.
3. Run:

```sh
python3 ~/.codex/agents/scripts/claude_review.py prepare --spec /absolute/spec.json --checkout /absolute/checkout --output /new/bundle
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --timeout 900 --finish-by 2026-10-15T20:00:00Z
```

The bundle retains raw data and exact hashes, projects CI transport metadata, preserves discussion bodies and thread/disposition context with deduplicated copies, and includes exact ancestor guidance. Preparation rejects a dirty/wrong checkout, a wrong merge-base, and visibly incomplete pagination. This validation cannot prove that the caller fetched every REST page; the caller must establish completeness.

The launcher uses Opus 5.5 medium, a stable shared contract/checklist prefix, dynamic-section exclusion, deferred tool discovery, subscription authentication, Linear-only MCP filtering, and explicitly allowed read tools/commands. Guidance is embedded exactly once in the initial user assignment. Original source/history and raw evidence remain inspectable. An unavailable required integration is a blocker; a claimed connection is insufficient without actual reads.

Use simple read commands from the already pinned working directory. Do not prepend `cd`, combine commands, broaden permissions, or silently substitute another model. The helper bounds the timeout by `--finish-by` or the manifest deadline, rejects expired/ambiguous deadlines, and stops its owned process group. The caller must reserve publication/cleanup time before that analysis deadline. On external cancellation the caller must still verify owned process termination.

If a substantive gap or changed snapshot requires continuation:

```sh
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --resume --prompt-file /absolute/focused-request.txt --timeout 600
```

Restore the same clean pinned checkout path first if it was removed. Continuation preserves the initial recorded system prompt and launch/tool settings; it does not silently apply later changes to the helper/checklist. Provide new instructions in the focused request. Each continuation gets separate events, metrics, and report files. Formatting/preferences alone do not justify another reasoning pass.

`execution_complete` is not review sign-off. Verify source/test/caller coverage and supported claims, actual Linear reads, exact guidance delivery, model/effort, and finding anchors. Require Incomplete for unresolved material gaps. Count every necessary continuation in the comparison, and report failed/incomplete attempts separately rather than treating their low token count as a quality-preserving saving.

Usage totals are per invocation. Resumed `total_cost_usd` and `modelUsage` costs are cumulative session estimates: take the final value per session, never sum it across continuations. API-equivalent list prices do not establish subscription quota consumption. Historical tests fix code and archived GitHub context; live Linear may have changed and must be disclosed.

Verification:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 ~/.codex/agents/scripts/test_claude_review.py
```
