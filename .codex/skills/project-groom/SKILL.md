---
name: project-groom
description: Reconcile an existing Linear project with verified current reality, including outcomes, PR links, blockers, superseded decisions, duplicates, and statuses. Run only when explicitly invoked; planning belongs to project-init and readiness assessment to project-audit.
disable-model-invocation: true
---

# Groom a project

Run on explicit human invocation. Creating or reviewing this configuration does not invoke it. Read [the shared project contract rules](../project-init/references/project-contract.md) before assessing or changing records. Follow the [shared PR ownership model](../../AGENTS.md#pr-delivery-ownership-in-project-workflows). Keep durable state in Linear, with no local registry or project-management files; never infer approval or acceptance from agent claims.

1. **Resolve and inspect.** Accept a project URL, ID, or name, or derive a unique project from verified context; clarify only genuine ambiguity. Verify the workspace/account. Read the contract, decisions, relevant updates, milestones, ticket inventory, linked PR/CI/deployment evidence, and current native execution ownership. Separate unknown evidence from verified facts.
2. **Reconcile verified reality.** Update records to match evidence: delivered outcomes and PR links, current blockers, approved decisions that superseded earlier ones, duplicate dispositions, and statuses. Normalize a noncanonical description while preserving meaning and provenance. A merged PR does not prove required deployment or operational acceptance; never rewrite goals to fit delivered code.
3. **Preserve intent and work in flight.** Keep approved intent, ownership, relationships, and active or paused work. Do not cancel, move, split, or reassign owned work behind its owner's back; hold the affected change while independent reconciliation continues. Material contract, scope, ownership, or reorganization changes need a concrete proposal and human decision unless already specifically approved.
4. **Verify and report.** Re-read before consequential writes, apply minimal patches, and read back results. Post a project summary only when the [status update policy](../../AGENTS.md#project-status-updates) permits; an unchanged rerun rewrites nothing. Report changes, held proposals, and flagged planning gaps, such as uncovered KRs or unscoped work, with actual ticket links.

Do not design a new plan or audit readiness; flag those needs for the human, who may invoke project-init or project-audit. Do not start supervision, create automations, or invoke another explicit-only skill.
