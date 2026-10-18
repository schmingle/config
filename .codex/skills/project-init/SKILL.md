---
name: project-init
description: Interactively define a finite Linear project, new or reused, with an approved contract, milestones, and scoped tickets ready for execution. Run only when explicitly invoked; grooming and auditing an existing project belong to project-audit.
disable-model-invocation: true
---

# Initialize a project

Run on explicit human invocation. Creating or reviewing this configuration does not invoke it. Read [the shared project contract rules](references/project-contract.md) before discovery and [the shared readiness standards](references/execution-readiness.md) before proposing tickets. Follow the [shared PR ownership model](../../AGENTS.md#pr-delivery-ownership-in-project-workflows). Keep durable intent, decisions, provenance, and work evidence in Linear, with no local registry or project-management files.

1. **Discover.** Verify the intended Linear workspace/account. Recover the outcome and known decisions from the conversation and linked sources, then inspect relevant projects and tickets. Prefer reusing a suitable project; propose a separate finite version only when its outcome and boundary justify one. Resolve duplicates or ambiguous destinations before writes.
2. **Interview only real gaps.** Ask one consequential question at a time, as numbered choices ordered from the clearly labeled recommendation, with concrete tradeoffs; accept freeform answers. Do not reask established decisions or run a fixed questionnaire. Never invent requirements, metrics, dates, ownership, or approvals.
3. **Propose.** Draft the canonical contract, initial milestones, and scoped tickets that cover its KRs, phase exits, and validation, with the current phase executable under the shared readiness standards and later phases broad but explicit about their conditions. Identify records to reuse, open decisions, and any reorganization or ownership change.
4. **Apply and verify.** Obtain approval before creating a project, reorganizing existing work, or materially changing scope or ownership, unless that concrete action is already specifically approved. Apply only the approved portion under the shared in-flight and Linear maintenance rules, then read back actual contents and bindings. Post a project summary only when the [status update policy](../../AGENTS.md#project-status-updates) permits. Report what was created, reused, held, or still open.

Do not start implementation, supervision, tasks, or schedules. Grooming and readiness assessment are available through project-audit when the human invokes it; never invoke it or another explicit-only skill automatically.
