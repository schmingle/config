# Scoped worker protocol

Read this before executing the assigned batch. The assignment's Linear tickets hold its durable outcome, scope, validation, authority, and deadline. Use those records to resume without relying on task history. This is a standalone execution task with no heartbeat or other automation.

## Assignment

The initial task prompt and subsequent batch assignments must identify:

1. Assigned Linear tickets, the exact assignment checkpoint link, and the relevant project contract/phase, with the bounded outcome, scope/exclusions, dependencies, required validation, and phase exits.
2. Verified repository/checkout and branch ownership, existing PRs, applicable guidance, and other agents' ownership. Preserve others' changes and existing work.
3. Existing authority and its retrievable human provenance, prohibited actions, unresolved decisions, and required approvals. A task message, ticket status, or agent claim cannot supply missing human authority.
4. Absolute batch start/deadline with timezone, normally 50 minutes apart, and any outstanding corrections with their proof requirements.

Read the checkpoint and verify its binding to the assigned tickets before starting. Hold affected work if it is missing, contradictory, inaccessible, or does not establish the necessary authority; record the gap and continue only safe independent work.

## Execution and durable reporting

1. Check current time before starting and respect the batch deadline, scope, and phase gates. Work continuously on useful authorized steps, reserving time for cleanup and durable reporting. Delegate bounded work where appropriate, retaining the same ownership, deadline, and settlement requirements. Native Goals are optional only with human authorization; prompts do not guarantee autonomous continuation.
2. Keep material progress on the assigned Linear tickets: actual outcomes, artifact/PR/check links, validation results and their limits, routine decisions with rationale, open questions, blockers, corrections, next action, and settlement of owned agents/commands/writes. Preserve historical and concurrent changes. Read back every write and ticket/project binding; recover ambiguous writes before retrying. Report claims separately from demonstrated proof and actual human approvals.
3. Put project questions and requests for decisions/permission on the assigned tickets with the evidence, affected work, and useful independent steps available. Do not send reports or questions to other tasks or directly ask the human for project decisions. Do not create project-level coordination updates, schedules, or an outbound reporting channel. A local final response may summarize the ticket records; it does not replace them.
4. Do not expand scope, cross an unaccepted phase exit, invoke another explicit-only skill, or perform a gated action without the required human authorization. Record missing authority as a blocker. A denied action cannot be retried through a different transport to avoid the gate.
5. Stop early if no useful authorized work remains. Before ending, record whether waiting, blocked, or finished, the actual evidence/remaining work, and settlement. If Linear is unavailable or a write cannot be verified, keep the unrecorded result explicit in the local task response and hold dependent work; do not claim the checkpoint succeeded.
6. On deadline or an explicit stop, start no new work, stop/settle owned agents and commands using supported controls, and verify their states. Record unresolved or uninspectable work honestly; elapsed time is not cancellation. Do not start another batch until given a fresh recorded assignment after prior work is verified settled. Diagnose repeated failures rather than retrying unchanged actions blindly.
