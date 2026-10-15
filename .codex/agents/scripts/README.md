# Claude review preparation and launch

The helper runs the Claude-backed `pr-review-high`; the default reviewer runs
natively. Review definitions and the posted template remain in
[the shared contract](../pr-review.md). [The execution profile](claude-review.toml)
is the single source for Claude's model, effort, display name, and allowed tools.
Native signoffs come from `reviewer_attribution.py pr-review` or
`reviewer_attribution.py pr-risk`, which reads
the native agent's `model` and `model_reasoning_effort` fields.

## Prepare and run

Create a fresh detached checkout at the pinned PR head. Save complete paginated
GitHub responses and write a JSON specification containing `repo`, `number`, `head`,
`base` (commit), `base_ref` (branch), `merge_base`, and `evidence` (plain output filename
to source path), plus `risk_report`. This object contains the posted report's exact
`rating`, `body`, `url`, and assessed commit fields `head`, `base`, and `merge_base`.
The caller verifies its publication and provenance. Its assessed commits may predate
the current review: reuse the posted report on subsequent reviews without rerunning
risk assessment. Missing/incomplete reports block preparation. Include title/body,
linked issues, mode/scope, and an ISO 8601
`finish_by` with timezone. Additional `guidance` paths and `benchmark: true` are
optional. Never include baseline reports or private coordinator conclusions in a
blind benchmark.

```sh
python3 ~/.codex/agents/scripts/claude_review.py prepare --spec /absolute/spec.json --checkout /absolute/checkout --output /new/bundle
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --timeout 900
```

The deadline comes from the specification; `--finish-by` can override it. Reserve
publication/cleanup time before that deadline. Output belongs outside the checkout
and public configuration repository because it can include private source material.

The bundle preserves full evidence byte-for-byte. It validates visible API errors
and final pagination markers without compacting or reconstructing discussion.
The caller must still prove every REST page was fetched. Guidance includes the
selected global and repository ancestor instruction files (`AGENTS.override.md`
then `AGENTS.md`), root testing guidance, and explicit additional topical guides.
Saved evidence/guidance hashes are checked before launch. Legacy bundles must be
prepared again; they are never silently migrated.

Claude has trusted local shell/file access. Review instructions still prohibit
source edits, tests/installs, delegation, publication, and external mutations.
The reviewer chooses applicable instructions and source context, using the bundle as
a starting point and gathering more evidence when needed. Required review coverage
still applies. The caller owns live eligibility, required Linear reads, review-coverage verification,
publication/readback, and worktree cleanup. The helper checks initial and final HEAD
and cleanliness, validates the report envelope and unchanged risk rating/report URL,
and settles its owned process on normal completion, timeout, interruption, or error. After a hard kill or crash,
inspect the saved process identity and reconcile it manually.

## Continue a review

```sh
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --resume --prompt-file /absolute/focused-request.txt --timeout 600
```

Use a continuation only for a substantive gap or new evidence. Restore the same clean
pinned checkout if necessary. Original launch settings are retained; new deadline
information is sent with the focused request. Each attempt has separate process,
events, report, and metrics files. Execution/report success is never coverage sign-off.
The result includes `risk` (the supplied rating), `risk_report_url` (the supplied
URL), and `risk_discrepancies` (a list of concrete contradictions, empty when none).
The publisher must surface discrepancies and withhold sign-off for unresolved material
contradictions; a structurally valid report is not sign-off.
Use the final cumulative cost once per session; do not sum it across continuations.

## Verification

Run `python3 scripts/check_config.py` from the config repository, then:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .codex/agents/scripts -p 'test_*.py'
```

Tests use local fixtures and subprocesses. They do not invoke Claude or connected
services. CI installs the small validation dependency from `requirements-dev.txt`.
