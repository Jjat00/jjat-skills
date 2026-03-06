# jjat-langsmith Skills

Four improved LangSmith skills for Claude Code, replacing the three official skills (`langsmith-trace`, `langsmith-dataset`, `langsmith-evaluator`) and adding a new production skill.

## Skills

| Skill | Replaces | Lines |
|---|---|---|
| `jjat-langsmith-tracing` | `langsmith-trace` | ~450 |
| `jjat-langsmith-datasets` | `langsmith-dataset` | ~360 |
| `jjat-langsmith-evaluators` | `langsmith-evaluator` | ~560 |
| `jjat-langsmith-production` | *(new)* | ~340 |

## Why these are better than the official skills

### jjat-langsmith-tracing vs langsmith-trace

The official skill only covers OpenAI with `wrap_openai`. This skill adds:

- **3 providers**: `wrap_openai`, `wrap_anthropic`, `wrap_gemini` with examples for each
- **All 6 run types**: `llm`, `chain`, `tool`, `retriever`, `embedding`, `agent` — the official skill doesn't document run types at all
- **Thread/conversation tracking**: `session_id`/`thread_id` for grouping traces into conversations, plus a stateful conversation pattern with thread store
- **3 debugging workflows**: Tracing UI inspection, Playground & Polly for rapid iteration, CLI & coding agents for programmatic analysis
- **7 framework integrations**: LangChain/LangGraph, Claude Agent SDK, OpenAI Agent SDK, Vercel AI SDK, Claude Code, OpenTelemetry — the official skill mentions none
- **Trace visualization**: Explains what parent/child relationships look like in the UI
- **Troubleshooting section**: Common issues and fixes

### jjat-langsmith-datasets vs langsmith-dataset

The official skill covers basic dataset creation. This skill adds:

- **PRD-driven dataset building**: A structured process — write requirements first, derive coverage categories, then build examples that cover each category
- **Coverage categories table**: Maps requirements to test cases systematically instead of ad-hoc example creation
- **4 dataset types with guidance**: `final_response`, `trajectory`, `single_step`, `RAG` — explains when to use each and what the schema looks like
- **3 creation methods**: UI upload, SDK programmatic creation, and creating from production traces — the official skill only covers SDK
- **Dataset structure explanation**: Clarifies the `inputs`/`outputs`/`metadata` schema that trips people up
- **Best practices**: Minimum dataset sizes, when to version, how to maintain datasets over time

### jjat-langsmith-evaluators vs langsmith-evaluator

The official skill covers basic evaluator creation and running. This skill adds:

- **3 evaluator types comparison table**: Code-based vs LLM-as-judge vs Pairwise — when to use each
- **Evaluation levels**: Step/unit, final response, and trajectory evaluation — the official skill doesn't distinguish these
- **4 evaluator signatures**: `(run, example)`, `(inputs, outputs, reference_outputs)`, `(inputs, outputs)`, `(run)` — with examples for each
- **3 rules for LLM judges**: Narrow scope, binary classification, align with humans — based on the course material
- **Pairwise evaluation**: 3-step process with `randomize_order` for unbiased comparison
- **Safe evaluator pattern**: Try/except wrapper that returns 0.0 instead of crashing the experiment
- **Test isolation**: `LANGSMITH_TEST_TRACKING=false` for CI environments
- **Combining evaluators**: Running multiple evaluators in a single experiment

### jjat-langsmith-production (new)

No official equivalent exists. This skill covers the production phase of the agent lifecycle:

- **Online evaluations**: 4 production evaluators (latency SLA, policy compliance, answer correctness, helpfulness)
- **Online evaluator signatures**: `(run)` only — no `example` parameter
- **Sampling strategies**: Random and stratified sampling to control LLM judge costs
- **Production thresholds**: Metric thresholds with recommended actions
- **Deployment validation**: Statistical comparison (scipy t-test) before promoting new versions
- **Trace upload at scale**: RunTree API with 6 key patterns (timestamp shifting, UUID7 mapping, trace grouping, etc.)
- **Insights Agent**: Automated analysis of 500+ traces via summarize/cluster/report
- **Automations**: Score-based routing (low scores to human review, high scores to golden dataset)
- **Deployment strategies**: Blue-green, canary, and shadow mode

## Source material

All skills are based on:
- [lca-reliable-agents](https://github.com/langchain-ai/lca-reliable-agents) repository (Python examples)
- [Course documentation](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction) (23 pages)
- "Agentes IA Confiables" course PDF (27 pages)
- Official LangSmith SDK documentation

## Installation

```bash
# Install all 4 skills
claude skill install --path /path/to/jjat-skills/skills/jjat-langsmith-tracing
claude skill install --path /path/to/jjat-skills/skills/jjat-langsmith-datasets
claude skill install --path /path/to/jjat-skills/skills/jjat-langsmith-evaluators
claude skill install --path /path/to/jjat-skills/skills/jjat-langsmith-production
```
