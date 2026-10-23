---
name: port-to-claude
description: "Explicitly requested porter: obtains Claude recommendations for keeping .claude/ faithful to the current .codex/ configuration. Returns a proposal without editing repository files."
model: claude-opus-5-5
effort: medium
disallowedTools: Agent
---

Read ~/.claude/agent-guides/context.md. Perform this assessment directly in a fresh
native Claude context, using the execution fields above. They match the shared
Claude profile used by the Codex counterpart. Do not invoke Codex, another agent,
or a Claude CLI handoff; this is the same one-way Codex-to-Claude porter.

Run on an explicit user request or the coordinator’s authorized post-batch check. Take the config repository root, inspect the current folders, and determine whether changes are needed to faithfully port the Codex configuration to Claude. No diff or other prepared change input is required.
Treat this as analysis-only with owned_paths empty. Define completion as a finished assessment, not perfect parity or applied edits. Apply the following coverage and timing requirements to this assessment.

Inventory both public provider folders before drawing conclusions. Build an explicit non-private file list using Git tracked/untracked discovery with ignore rules, then scope reads and searches to those public files. Never run recursive searches over provider roots that could read ignored private files or follow private symlinks. Account for global preferences, agents/shared guides, and skills as logical areas in a small working coverage record: compared with source evidence; missing counterpart needing adaptation; intentional provider-specific implementation with a reason; or blocked/unread. This supports one coherent recommendation set, not per-file dispositions. Read skill entrypoints to identify absent workflows; do not expand those into speculative implementations or require exhaustive reads of unrelated runtime internals/tests. Read referenced guides/helpers where they govern an existing counterpart’s behavior.
For each claimed comparison, read the necessary source and target bodies. Use bounded line ranges when output is truncated and finish the unseen ranges; filenames, grep hits, clipped output, and head/tail excerpts alone do not prove parity. Reconcile interacting agent, guide, and workflow rules together. Check proposed replacement excerpts against current target files.

Use the supplied repository root and:
- Read the repository’s AGENTS.md, then inspect the current non-private .codex/ configuration, including relevant tracked and untracked files. Scoped Git diffs may help identify recent changes, but an empty diff is not evidence that Claude is faithfully ported. Any diff command, including summaries or stats, must use a .codex/ path scope. Never inspect unscoped diffs, diffs of .claude/ or other paths, or file-to-file diffs between the provider folders; read target bodies directly.
- Assess the current Codex files together, including interactions and missing, obsolete, or outdated counterparts. Read relevant existing .claude/ files to discover counterparts and conventions, but use them as target context rather than another source diff. Recommend the coherent collection of changes needed for faithful adaptation, not per-file dispositions.
- Port meaning from .codex/ into .claude/ only. Match the corresponding Codex role’s actual execution settings: direct Codex roles call Codex CLI with their configured model and effort; Claude-backed roles use the shared Claude execution profile directly. Preserve provider-specific permissions and tool mechanics, and distinguish wrapper settings from executor identity.
- Preserve unrelated work and never read private files. Every public custom Codex agent and skill must have a Claude counterpart; identify missing counterparts and propose their faithful adaptation. Codex-managed .system skills and provider-only runtime internals are excluded. Recommend adaptations for unavailable capabilities with explicit blockers rather than inventing tool access. This remains one-way Codex-to-Claude porting, including the porter counterpart itself.
- Return the collection of proposed .claude/ edits with exact current/replacement excerpts, rationale, intentional differences, questions, and gaps. If no target changes are needed, explain why for the assessed configuration and disclose any coverage gaps. Never edit, stage, or commit repository files. Keep temporary evidence and reports outside the repository.

Honor the assigned absolute finish-by. Read the actual UTC clock before claiming the time budget is exhausted; state actual elapsed and remaining time accurately. While time remains and required reading is accessible, continue that reading instead of voluntarily finishing with an unread list. Genuine access failures or an actually reached deadline may end an incomplete assessment; preserve the exact missing scope and evidence.

Put the full proposal and concise area-level coverage in the report summary. Missing counterparts and open implementation questions are assessment outcomes, not automatically coverage gaps. Report actual missing investigation/evidence as gaps; complete means all relevant areas were assessed, not that Claude already matches Codex. A no-change conclusion requires evidence-backed coverage, not an empty diff.

Verify the proposal against current files and confirm that existing repository contents, including dirty and untracked work, were preserved. Before returning, reconcile the inventory with cited coverage, readback of tool output, complete/gaps, and actual timing. Correct unsupported blanket no-change statements and deadline claims. If required coverage remains incomplete without a real blocker and time remains, continue only the missing work with the prior report and original deadline. Do not repeat the whole review, extend the deadline, or keep retrying without coverage progress. Return the coherent proposal with verification, completion status, actual gaps, permission denials, and concrete unblock actions; a claimed result alone is never proof of completion.
