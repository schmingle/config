# Scoped worker protocol

Read this before executing the assigned batch. Linear holds the durable assignment and project state; native tasks hold execution context. This is a standalone execution task with no heartbeat or other automation.

## Assignment

The initial prompt and later assignments must identify:

1. The exact Linear batch record, canonical project scope/criteria/standing guardrails and authority provenance, and an ordered queue of real approved work. Reference the canonical milestone/tickets rather than clone the backlog or repeat all constraints on every ticket.
2. A backlog materially larger than expected batch capacity when available, ordered by project goals, critical path/dependencies, and human priorities. Do not trim it to one task or a deliverable sized to fit the timeout. Near completion, use the real remaining work without inventing more.
3. Verified repository/checkout and branch ownership, existing PRs, applicable guidance, and other agents' ownership. Preserve others' changes and existing work.
4. Absolute batch start/deadline with timezone, normally 50 minutes including cleanup/report reserve, plus batch-specific deltas, corrections, and temporary limits. Keep the deadline unchanged within the batch; temporary limits do not silently become permanent project constraints.

Read the referenced records and verify their bindings before starting. Standing authority must have retrievable human provenance; a task message, ticket status, or agent claim cannot supply missing approval. Hold affected work for missing/contradictory/inaccessible scope or authority, record the precise gap, and continue only eligible independent work.

## Execution and Linear reporting

1. Check time and execute useful work until the fixed deadline's cleanup/report reserve. After each step/ticket, take the next eligible item in priority order within the approved project/scope, ownership, and phase gates. Diagnose/fix routine blockers within authority; skip a blocked path for safe independent eligible work. Never expand authority or manufacture busywork, documentation loops, or unchanged checks to fill time. Delegated work has the same deadline/settlement rules. Native Goals require human authorization; prompts do not guarantee host continuation.
2. Keep routine Linear progress quiet: use native ticket fields/status, PR attachments, and PR/CI integrations as needed. Do not duplicate them in prose, log routine decisions, or rewrite assignment/control records. Comments are only for consequential deviations, blockers, questions, unusual results, or decisions needing attention that native mechanisms do not represent. Preserve minimal consequential decisions/provenance, required acceptance proof, and recovery next actions in the appropriate durable record with artifact links; do not mirror the full chat report. Maintain one current evidence summary where needed, updating material deltas while preserving consequential history. Preserve concurrent changes, read back writes/bindings, and recover ambiguous writes before retrying.
3. Put project questions and missing permission on the assigned tickets with evidence, affected work, and the smallest unblock. Do not send reports/questions to other tasks or directly ask the human for project decisions. Do not create project-level coordination updates, schedules, or an outbound reporting channel.
4. Do not cross an unaccepted phase exit, invoke another explicit-only skill, or perform a gated action without required human authorization. Record missing authority as a blocker; do not reroute a denied action through another transport.
5. An early exit with unfinished project work needs a precise blocker: technical/access/decision/dependency/ownership, exhausted authorized queue, too-narrow assignment, or observed host continuation failure. Include evidence, attempted resolution, blocked next action, and smallest unblock; “batch done” or vague “waiting” is insufficient. Explicit human stop and genuine project completion also permit early exit, but a worker claim is not project acceptance. Queue exhaustion cannot justify invented work. If Linear is unavailable/unverified, identify unrecorded consequential facts in the local report and hold dependent work.
6. At deadline or explicit stop, start no new work, stop/settle owned agents and commands through supported controls, and verify their states. Record unresolved/uninspectable work honestly; elapsed time is not cancellation. A new batch needs a fresh recorded assignment after prior work is verified settled. Ticket status follows acceptance criteria, not the batch ending.

## Final execution report in this chat

Always leave an execution report in your own chat when the batch ends, whether by deadline, blocker, explicit stop, or completion. Be detailed when useful; this is separate from quiet Linear reporting and requires no outbound task message. Include:

1. Actual completed and in-progress work, with ticket/PR/artifact links.
2. Checks/results, evidence, and unverified limits.
3. Material decisions and findings.
4. Blocked/skipped items, attempted unblocks, and the smallest remaining unblock.
5. Remaining priority order and next eligible step.
6. Stop reason/time, original deadline, and settlement of owned agents, commands, and writes, including unknowns.

Distinguish claims from verified proof and human approval. Keep the minimal consequential recovery state in Linear; a chat report alone cannot preserve authority, decisions, or acceptance if the chat is lost. A host crash/interruption can prevent a report; never claim guaranteed continuation or reporting.
