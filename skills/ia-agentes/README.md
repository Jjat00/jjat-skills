# jjat-langsmith Skills

Four improved LangSmith skills for Claude Code, replacing the three official skills (`langsmith-trace`, `langsmith-dataset`, `langsmith-evaluator`) and adding a new production skill.

Based on the [official LangSmith skills](https://github.com/langchain-ai/langsmith-skills) — these skills include **all content from the official versions** plus significant additions from the LangChain Academy course [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents), its [repository](https://github.com/langchain-ai/lca-reliable-agents), and documentation.

## Skills

| Skill | Replaces | Lines |
|---|---|---|
| `jjat-langsmith-tracing` | `langsmith-trace` (265 lines) | ~530 |
| `jjat-langsmith-datasets` | `langsmith-dataset` (295 lines) | ~400 |
| `jjat-langsmith-evaluators` | `langsmith-evaluator` (363 lines) | ~690 |
| `jjat-langsmith-production` | *(new — no official equivalent)* | ~340 |

## Why these are better than the official skills

Each skill is a **strict superset** of its official counterpart — all original content is preserved, plus the additions listed below.

### jjat-langsmith-tracing vs langsmith-trace

The official skill only covers OpenAI with `wrap_openai` and Python. This skill adds:

- **3 providers**: `wrap_openai`, `wrap_anthropic`, `wrap_gemini` with examples for each
- **TypeScript support**: `wrapOpenAI()` + `traceable()` examples
- **All 6 run types**: `llm`, `chain`, `tool`, `retriever`, `embedding`, `agent` — with guidance on when to use each
- **Thread/conversation tracking**: `session_id`/`thread_id` for grouping traces, plus a stateful conversation pattern with thread store
- **3 debugging workflows**: Tracing UI inspection, Playground & Polly for rapid iteration, CLI & coding agents for programmatic analysis
- **7 framework integrations**: LangChain/LangGraph, Claude Agent SDK, OpenAI Agent SDK, Vercel AI SDK, Claude Code, OpenTelemetry
- **Complete CLI tree**: All subcommands including dataset, example, evaluator, experiment (official only lists trace/run)
- **Trace visualization**: ASCII tree showing what parent/child relationships look like
- **Export tips**: `/tmp` for temporary exports, JSONL stitching
- **Troubleshooting section**: Common issues and fixes

### jjat-langsmith-datasets vs langsmith-dataset

The official skill covers basic dataset creation in Python and TypeScript. This skill adds:

- **PRD-driven dataset building**: Structured process — write requirements, derive coverage categories, build examples
- **Coverage categories table**: Maps requirements to test cases systematically
- **4 dataset types with guidance**: `final_response`, `trajectory`, `single_step`, `RAG` — with `trace_id` field for traceability
- **3 creation methods**: UI upload (with CSV format), SDK programmatic creation, and creating from production traces
- **TypeScript SDK examples**: `createDataset()` + `createExamples()`
- **Dataset structure explanation**: Clarifies the `inputs`/`outputs`/`metadata` schema
- **Interactive vs non-interactive `--yes` guidance**: When to use and when not to
- **Best practices**: Minimum dataset sizes, versioning, maintenance over time
- **Extra troubleshooting**: Example count mismatch, field name mismatches

### jjat-langsmith-evaluators vs langsmith-evaluator

The official skill covers basic evaluator creation and running. This skill adds:

- **Complete setup section**: Environment variables, dependencies (Python + TypeScript), CLI install
- **3 evaluator types comparison table**: Code-based vs LLM-as-judge vs Pairwise — when to use each
- **Evaluation levels**: Step/unit, final response, and trajectory evaluation
- **4 evaluator signatures**: `(run, example)`, `(inputs, outputs, reference_outputs)`, `(inputs, outputs)`, `(run)` — with examples
- **Local vs uploaded differences table**: Column naming, `key` field behavior, environment constraints
- **3 rules for LLM judges**: Narrow scope, binary classification, align with humans
- **Async LLM judge pattern**: `async def` + `AsyncOpenAI` for concurrent evaluation
- **Pairwise evaluation**: 3-step process with `randomize_order` for unbiased comparison
- **Trajectory capture**: `stream_mode="debug"` + `subgraphs=True` for LangGraph
- **TypeScript evaluators**: Code-based + LLM-as-judge + `evaluate()` examples
- **Safe evaluator pattern**: Try/except wrapper that returns 0.0 instead of crashing
- **Resource links**: LangSmith docs, Custom Code Evaluators, OpenEvals repo

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
- Official skills: [langchain-ai/langsmith-skills](https://github.com/langchain-ai/langsmith-skills) (base content)
- LangChain Academy course: [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents)
- [lca-reliable-agents](https://github.com/langchain-ai/lca-reliable-agents) repository (Python examples)
- [Course documentation](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction) (23 pages)
- "Agentes IA Confiables" course PDF (27 pages)
- Official LangSmith SDK documentation

## Installation

See the [root README](../README.md) for installation instructions.
