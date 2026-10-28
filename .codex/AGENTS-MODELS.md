# Model selection reference

Reviewed: 2026-10-28. These are provisional recommendations for engineering and
knowledge work, prioritizing quality and low supervision, then speed and usage.
They are not measured optima or a universal model ranking.

This document is advisory. It does not override an explicit model request,
agent execution fields, workflow requirements, or available runtime capabilities.
Do not change configurations or start additional model runs merely to apply it.

## Layer 1: nature of work × level

Each cell recommends a model and reasoning effort independently. Levels describe
demand within each work type, not the model's effort setting or an equivalent
absolute difficulty across rows. An xhigh task does not automatically need xhigh
effort, and several levels may use the same model and effort.

| Level | Meaning within the work type |
| --- | --- |
| Low | Prescribed approach, explicit inputs, little judgment, easy verification. |
| Medium | Bounded problem, established patterns, some investigation and choices. |
| High | Substantial ambiguity, interacting constraints, difficult diagnosis or tradeoffs. |
| Xhigh | Deep uncertainty or broad interactions requiring sustained synthesis and independent judgment within the work type. |

Volume alone does not increase the reasoning level. Risk independently governs
approval and verification requirements; high consequence does not automatically
mean high reasoning demand.

| Nature of work | Low | Medium | High | Xhigh |
| --- | --- | --- | --- | --- |
| Code generation — implement, fix, refactor, write tests | Sol · medium | Sol · medium | Sol · high | Sol · xhigh |
| Code review — find defects, regressions, contract violations | Sol · high | Sol · high | Sol · xhigh | Opus 5.5 · medium |
| Architecture / plan generation — design approaches, interfaces, execution plans | Sol · high | Sol · high | Sol · xhigh | Opus 5.5 · medium |
| General review — challenge assumptions, feasibility, boundaries, alternatives in plans, architecture, or other material | Sol · xhigh | Sol · xhigh | Sol · xhigh | Opus 5.5 · medium |
| Investigation and analysis — retrieve evidence, diagnose causes, reconcile findings | Sol · high | Sol · high | Sol · xhigh | Sol · xhigh |
| Codex-specific advice and review — assess Codex behavior, setup, and workflows | Sol · high | Sol · high | Sol · xhigh | Astra · medium |
| Writing and editing — express supplied ideas, adapt voice, improve clarity | Terra · medium | Terra · medium | Terra · high | Terra · xhigh |
| Structured extraction and classification — extract fields, categorize, transform explicit inputs | Terra · medium | Terra · medium | Terra · high | Terra · xhigh |
| Operational execution — follow defined procedures, operate tools, verify outcomes, reconcile affected records | Sol · medium | Sol · medium | Sol · high | Sol · high |

Sol = GPT-6.1 Sol; Astra = GPT-6 Astra; Terra = GPT-6.1 Terra.
Opus = Claude Opus 5.5 in a Claude-capable execution environment.

Classify by the dominant intellectual work. Researching conflicting sources to
form a recommendation is investigation or architecture; polishing the resulting
recommendation is writing. Extraction requiring substantial inference moves into
investigation. Use the specific code-review or Codex-specific row when applicable;
general review covers other critiques, including architecture and plan review.
Concrete tasks can change level with their actual constraints.

Supervision is a separate, manually controlled role: assessing progress, deciding
next work, steering workers, and resolving blockers. It does not inherit the
operational-execution row; no supervisor model mapping is defined here.

### Execution mode: browser and desktop

Browser and desktop control are execution modes that can serve different work
types. For bounded UI execution, use this mode-specific recommendation:

| Execution mode | Low | Medium | High | Xhigh |
| --- | --- | --- | --- | --- |
| Browser / desktop execution — navigate interfaces, fill forms, update records, download reports, verify saved results | Terra · medium | Terra · medium | Terra · high | Terra · xhigh |

Apply this recommendation to operating the interface. Investigation, architecture,
review, and decisions still follow their nature-of-work rows; using a browser
does not reclassify the reasoning. API/CLI execution inherits the applicable
nature-of-work recommendation. Respect available tools and explicit execution
settings. Higher Terra effort choices remain provisional routing preferences.

These nature-of-work and execution-mode cells are a provisional policy, not
independently established results for every cell.
The selected model and effort values reflect approved routing preferences, not
new empirical findings. Review's capable-model floor is a judgment call. Retaining
Terra at higher levels is a specialization hypothesis, not proof it outperforms
stronger models. No direct comparative evidence establishes an optimal model for
supervision, and exact effort choices generally have weak comparative support.

Use **GPT-6.1 Sol at medium** when classification or evidence is insufficient to
justify another recommendation, subject to explicit requests and workflow settings.
Layer 2 will map concrete tasks to work types, default levels, and execution modes,
with conditions that change their classification; it is not defined here yet.

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
  effort. Medium for xhigh review follows the selected policy, not a demonstrated
  optimum for that task level. Effort
  labels are not equivalent compute budgets across models or vendors.
- **Environment matters.** [Databricks' adopter study](https://www.databricks.com/blog/benchmarking-coding-agents-databricks-multi-million-line-codebase)
  found more than twofold task-cost differences for the same model and effort
  across harnesses. Its July 2026 results predate the current models and do not
  establish their ranking.
- **Capabilities differ.** [Artificial Analysis](https://artificialanalysis.ai/agents/coding-agents)
  distinguishes implementation, terminal execution, and repository understanding.
  No model-specific chart values from that page were verified for this mapping.

## Additional candidates

- The Terra writing row follows OpenAI's task positioning. Using Terra for
  extraction and classification is a routing preference; its exact effort choices
  remain provisional. No personal voice advantage or optimum across levels has
  been established.
- Claude Sonnet 5.5 / medium: Claude-native everyday candidate. Current evidence
  does not establish a reason to migrate an existing Sol workflow.
- Claude Haiku: alternative for prescribed edits and mechanical extraction.
  No exact effort recommendation is established here.
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
