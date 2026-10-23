# Execution helpers

[The shared role launcher](../../../scripts/agent-launch.md) is the provider-neutral entry point for general assignments from either provider. It owns assignment handling, role dispatch, deadlines, execution records, and provider adapters. [The existing runtime](claude_runner.py) supplies process settlement and Claude-specific helpers to it and to specialized reviews. [The Claude handoff](../claude.md) defines provider-specific requirements.

- General tasks: use the shared launcher with the assigned role. [claude_delegate.py](claude_delegate.py) remains a compatibility entry point, following
  [the task handoff](../delegate-claude.md). It permits assigned source changes and
  verification in the existing checkout, saves initial/final state, and has no
  PR/risk/Linear requirement.
- PR reviews: [claude_review.py](claude_review.py), following
  [the review handoff](../pr-review-claude.md). It retains clean pinned snapshots,
  risk reports, required Linear reads, review output, and bounded recovery.

The review helper runs the Claude-backed `pr-review-high`; the default reviewer runs
natively. Review definitions and the posted template remain in
[the shared review contract](../pr-review.md). Common privacy, process settlement,
and verification belong to [the launcher contract](../../../scripts/agent-launch.md);
profile, authentication, and persistence belong to [Claude specifics](../claude.md).
Prepared reviews include the common contract in their hashed guidance snapshot.
Native signoffs come from `reviewer_attribution.py pr-review` or
`reviewer_attribution.py pr-risk`, which reads
the native agent's `model` and `model_reasoning_effort` fields.

Claude runners require Python 3.11+ with POSIX `waitid`/`WNOWAIT` support
and `ps` to verify process-group settlement. Both entrypoints check the current
interpreter before importing the runner, then search installed Python executables
beside it, on `PATH`, and in standard Homebrew/system locations. They probe each
candidate and replace the launcher process with the first compatible runtime,
preserving arguments, environment, working directory, and absolute deadlines.
On macOS, install Python 3.14+ if no compatible build is available. Nothing is
installed automatically; missing runtime capabilities fail before invoking Claude.
Ownership and settlement checks still fail closed.

## Prepare and run

Create a fresh detached checkout at the pinned PR head. Save complete paginated
GitHub responses and write a JSON specification containing `repo`, `number`, `head`,
`base` (commit), `base_ref` (branch), `merge_base`, and `evidence` (plain output filename
to source path), plus `risk_report`. This object contains the coordinator-supplied
assessment's exact `rating`, `body`, and assessed commit fields `head`, `base`, and
`merge_base`. Include `url` only when reusing an already published assessment.
The caller verifies its provenance. Its assessed commits may predate the current
review: reuse a complete final review's Risk section or a legacy separate report
on subsequent reviews without rerunning risk assessment. Missing/incomplete reports
block preparation. Include title/body,
linked issues, mode/scope, and an ISO 8601
`finish_by` with timezone. Additional `guidance` paths and `benchmark: true` are
optional. Never include baseline reports or private coordinator conclusions in a
blind benchmark.

```sh
python3 ~/.codex/agents/scripts/claude_review.py prepare --spec /absolute/spec.json --checkout /absolute/checkout --output /new/bundle
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --timeout 900
```

The initial deadline comes from the specification or `--finish-by` (or the initial
timeout when omitted). Continuation/recovery can shorten but never extend it. Reserve
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
still applies. The caller owns live eligibility, required Linear reads, review-coverage
verification, publication/readback, and worktree cleanup. The helper records preflight
and final transcript status separately. It uses
`--json-schema` and reads `structured_output`, preserving human `result` text only
for diagnostics. It checks initial and final HEAD
and cleanliness, and validates the report envelope and unchanged risk rating.

## Continue a review

```sh
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --resume --prompt-file /absolute/focused-request.txt --timeout 600
```

Use a continuation only for a substantive gap or new evidence, with a verified
persisted transcript. The helper passes its absolute path to `--resume`. Restore the same clean
pinned checkout if necessary. Original launch settings are retained; new deadline
information is sent with the focused request. Each attempt has separate process,
events, report, and metrics files. Execution/report success is never coverage sign-off.
The result includes `risk` (the supplied rating) and `risk_discrepancies` (a list
of concrete contradictions, empty when none). A source URL exists only for an
assessment already published before this review.
The publisher must surface discrepancies and withhold sign-off for unresolved material
contradictions; a structurally valid report is not sign-off.
For a diagnosed infrastructure failure with all owned processes settled, use one
replacement, within the original deadline and execution profile:

```sh
python3 ~/.codex/agents/scripts/claude_review.py run --bundle /new/bundle --replace-failed --recovery-reason missing-session --timeout 600
```

Other verified reasons are `invalid-output` and `cli-error`. A second replacement,
unproven failure, concurrent owned process, or deadline extension is rejected. Do
not reprepare a bundle to reset the assignment's recovery limit. Preserve all prior
attempts. A replacement establishes full review coverage independently.

Coverage explicitly records `scope_complete`, `inspected_sources`, `interfaces`,
`deployment`, `discussion`, and `linear`; the publisher verifies these against actual
inspection evidence. A valid schema or claimed completeness is not sign-off.

Use the final cumulative cost once per session; do not sum it across continuations.

## Verification

Run `python3 scripts/check_config.py` from the config repository, then:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .codex/agents/scripts -p 'test_*.py'
```

Tests use local fixtures and subprocesses. They do not invoke Claude or connected
services. CI installs the small validation dependency from `requirements-dev.txt`.
