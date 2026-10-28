# Model selection reference

Reviewed: 2026-10-28. These are provisional recommendations for engineering and
knowledge work, prioritizing quality and low supervision, then speed and usage.
They are not measured optima or a universal model ranking.

This document is advisory. It does not override an explicit model request,
agent execution fields, workflow requirements, or available runtime capabilities.
Do not change configurations or start additional model runs merely to apply it.

## Recommended mapping

Use **GPT-6.1 Sol at medium** as the everyday default. Increase effort for concrete
technical complexity; use specialist models when the task warrants their role.
Keep the default when evidence for switching is weak or the benefit is immaterial.

| Task | Model / effort | Trigger and evidence limits |
| --- | --- | --- |
| Project supervision and workflow coordination | GPT-6.1 Sol / medium | Routine ownership, dependencies, next actions, and evidence reconciliation. No direct comparative supervisor evidence. |
| Scoped implementation and PR authoring | GPT-6.1 Sol / medium | Use high for difficult diagnosis, interacting contracts, or substantial changes across modules. Exact effort is a judgment call. |
| Operations and verification | GPT-6.1 Sol / medium | Use high for diagnosis. Keep operational proof and approval gates independent of model choice. |
| Investigation and quantitative analysis | GPT-6.1 Sol / medium | Use high for difficult causal or statistical reasoning; retain explicit uncertainty and source checks. |
| Architecture, strategy, and consequential decisions | GPT-6 Astra / high | Specialist for challenging assumptions, conflicting evidence, and consequential ambiguity. Superiority over Sol high is unproven. |
| Writing, synthesis, and reporting | GPT-6.1 Sol / medium | Preserve facts, audience, voice, and exact revision constraints. No established personal voice winner. |
| Routine independent code review | GPT-6.1 Sol / high | Provisional effort choice; implementation scores do not establish review quality. |
| Difficult correctness and architectural review | Claude Opus 5.5 / high | Specialist for complex independent review. Relevant review evidence exists, but high is not a demonstrated optimum or proven superior to Sol. |

## Evidence and confidence

- **Default: moderate confidence.** [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection)
  positions Sol medium for complex technical work and coordinated deliverables,
  and Astra for demanding analysis. This is vendor guidance, not independent proof
  of these assignments.
- **Review specialist: provisional.** [CodeRabbit's Opus 5.5 study](https://www.coderabbit.ai/blog/opus-5-5-model-review)
  evaluated 80 known bug patterns. Standard caught 51 and Max caught 50; Standard
  produced fewer comments and higher actionable precision. The settings combine
  multiple pipeline stages and cannot be translated into a single effort value.
  Its baseline was a production model mix, not a direct Sol comparison.
- **Exact effort: generally low confidence.** [Anthropic's Opus guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)
  starts at medium and reports gains over an earlier Opus generation at higher
  effort. High for difficult review is a conservative recommendation. Effort
  labels are not equivalent compute budgets across models or vendors.
- **Environment matters.** [Databricks' adopter study](https://www.databricks.com/blog/benchmarking-coding-agents-databricks-multi-million-line-codebase)
  found more than twofold task-cost differences for the same model and effort
  across harnesses. Its July 2026 results predate the current models and do not
  establish their ranking.
- **Capabilities differ.** [Artificial Analysis](https://artificialanalysis.ai/agents/coding-agents)
  distinguishes implementation, terminal execution, and repository understanding.
  No model-specific chart values from that page were verified for this mapping.

## Candidates outside the default mapping

- GPT-6.1 Terra / medium: supplied-material writing and computer use candidate,
  supported by OpenAI positioning; no established advantage worth a routine switch.
- Claude Sonnet 5.5 / medium: Claude-native everyday candidate. Current evidence
  does not establish a reason to migrate an existing Sol workflow.
- GPT-6 Luna or Claude Haiku: candidates for prescribed edits and mechanical
  extraction. No exact effort recommendation is established here.
- Other providers: add only for a concrete relevant capability or substantial
  advantage that outweighs another environment and its maintenance.

## Using and revisiting the mapping

Judge success by correct outcomes, avoidable supervision, completion time, and
usage. A completed run, merged PR, or absence of corrections alone is not proof
of quality. Historical assignments are confounded by task difficulty, prompts,
tools, and human intervention; do not infer missing model or effort provenance.

Revisit when a model, execution environment, or relevant evidence materially
changes, or when repeated observed failures challenge a route. Do not multiply
specialists to fill gaps in evidence. Research can conclude that no meaningful
advantage is established; new benchmark runs are not required by this guide.
