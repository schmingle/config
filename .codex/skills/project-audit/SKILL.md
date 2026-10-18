---
name: project-audit
description: Read-only assessment of whether an existing Linear project's plan meets the shared execution-readiness standards, reporting gaps and recommendations. Run only when explicitly invoked; it changes no records.
disable-model-invocation: true
---

# Audit project readiness

Run on explicit human invocation. Creating or reviewing this configuration does not invoke it. Read [the shared readiness standards](../project-init/references/execution-readiness.md) and [the shared project contract rules](../project-init/references/project-contract.md). Follow the [shared PR ownership model](../../AGENTS.md#pr-delivery-ownership-in-project-workflows).

1. **Resolve and read.** Accept a project URL, ID, or name, or derive a unique project from verified context; clarify only genuine ambiguity. Verify the workspace/account, then read the contract, milestones, relevant tickets, and linked evidence. Disclose coverage or access gaps.
2. **Assess against the shared standards.** Check KR and phase coverage, decisions, priorities, dependencies and phase exits, acceptance and validation, execution buckets, human checkpoints, and access and executor capabilities.
3. **Report.** Give **Ready**, **Gaps found**, or **Unverified**. List each finding with its affected ticket links, immediately followed by a nested numbered recommendation naming the concrete action. Keep it concise and use this format:

   ```markdown
   1. [Finding and affected ticket links]
      1. Recommendation: [Concrete recommended action]
   ```

Stay read-only: make no Linear or other record writes, probe no sensitive access, and run no acceptance checks. Do not fix the plan or create a readiness certificate, registry, or audit ledger. Do not invoke another explicit-only skill.
