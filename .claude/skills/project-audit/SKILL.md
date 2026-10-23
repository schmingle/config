---
name: project-audit
description: Groom an existing Linear project to reflect verified reality, then assess contract sufficiency and execution readiness. Recommend the smallest corrections or next execution steps. May be invoked by agents; audit-only requests remain read-only.
disable-model-invocation: false
---

# Groom and audit a project

**Goal:** Ensure the project has a sufficient, concise contract for its intended outcome and is prepared for effective execution by reconciling verified facts, identifying material gaps, and recommending concrete next actions.

The audit is the quality authority for assessing the contract, not authority to change approved human intent. Challenge goals and approach when the evidence warrants it, recommend the smallest correction, and obtain approval before changing the approved plan.

**Key questions:**

1. Is this project ready for work by its intended executors?
2. Is it organized so work can progress smoothly?
3. Does it have clear, finite completion criteria so it can be finished and closed?

May be invoked by a human or agent within the existing task scope. Creating or reviewing this configuration does not invoke it. Read [the shared project contract rules](../project-init/references/project-contract.md) and [the shared readiness standards](../project-init/references/execution-readiness.md). Follow the [shared PR ownership model](../../CLAUDE.md#pr-delivery-ownership-in-project-workflows). Keep durable project state in Linear, with no local registry or project-management files. An explicit audit-only or read-only request skips writes, assesses the project against verified evidence, and reports factual corrections as recommendations.

1. **Resolve and inspect.** Accept a project URL, ID, or name, or derive a unique project from verified context; clarify only genuine ambiguity. Verify the workspace/account. Initially read the contract, decisions, relevant updates, milestones, ticket inventory, linked evidence, and current execution ownership. On later checks, reuse the previous task context and refresh current Linear and relevant PR evidence to identify changes; expand inspection where changes or uncertain coverage require it. The absence of a new human message does not establish that nothing changed. Separate verified facts from unknowns and disclose coverage or access gaps.
2. **Groom verified state first.** Follow [plan and state permissions](../project-init/references/project-contract.md#plan-and-state-permissions): update verified statuses, PR/evidence links, observed blockers, and progress under the existing plan. Never infer deployment or human acceptance from a merged PR. Propose plan amendments, including description normalization, duplicate closures, or reorganizing phase parent tickets into native Linear milestones, and apply only specifically approved amendments; reuse prior approval without asking again. Preserve concurrent edits and in-flight work. Re-read before consequential writes, apply minimal patches, and read back results; unchanged records need no writes.
3. **Audit the resulting project.** First read and apply the [contract rubric](references/contract-quality.md) in order: intention, consequential decisions, results and completion proof, then plan. Assess contract sufficiency independently of the existing ticket inventory. Then use the shared readiness standards to check ticket alignment and coverage, priorities, dependencies and phase exits, milestone alignment under the shared contract rules, acceptance, and each intended executor's fit, access, and checkpoints. Give contract sufficiency and execution readiness separate **Ready**, **Gaps found**, or **Unverified** verdicts. Block readiness only for a material threat to successful execution; wording, organization, or elegance are optional improvements unless they obscure intent or create consequential ambiguity. Human-owned work and the absence of autonomous implementation work are not themselves gaps. Ready means prepared for the remaining work, not currently startable or completed. An unresolved consequential decision is a contract gap; a ready discovery or decision task does not make the whole contract Ready. Identify clearly assessed independent ready work separately.
4. **Recommend according to readiness.** If gaps remain, identify the missing decision or concrete plan amendment, its affected work, and the smallest action needed; do not reduce a known question to a vague pending status. Hold affected execution while recommending any clearly assessed independent ready work. If readiness is unverified, identify the evidence or decision needed to establish it. If Ready, recommend the next concrete execution steps in dependency/priority order, with intended executors and human checkpoints. Include meaningful opportunities for agents to reduce human work, separately from readiness defects. Recommend work without performing it or starting another workflow.
5. **Report concisely.** State the contract sufficiency and execution readiness verdicts with their material reasons, then identify what can start now, by which intended executor, and what is gated. If none can start within the requesting workflow's scope, say so even when the project is Ready. Report material grooming changes, held proposals, and concrete recommendations with affected ticket links. For each finding or next step, use a nested numbered list of concrete actions or viable options. Distinguish actions to take together from alternatives; order alternatives from most recommended, label the preferred choice **Recommended**, and briefly explain material tradeoffs. Do not invent alternatives to fill the list. For an incremental check with no consequential change, briefly report the unchanged verdicts and evidence checked; do not repeat the full audit or unchanged decision notifications. Post project summaries only when the [status update policy](../../CLAUDE.md#project-status-updates) permits. Use this format:

   ```markdown
   1. [Finding or next step and affected ticket links]
      1. Recommendation: [Concrete action or option; label Recommended for a preferred choice]
      2. [Additional action or alternative, when applicable]
   ```

Do not execute tickets, change PRs, run acceptance checks, probe sensitive access, deploy, or mutate production. Do not start supervision, separate worker sessions, or automations, create a readiness certificate or audit ledger, or invoke another explicit-only skill.
