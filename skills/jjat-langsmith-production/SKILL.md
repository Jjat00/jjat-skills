---
name: jjat-langsmith-production
description: "INVOKE THIS SKILL when deploying agents to production with LangSmith, setting up online evaluations, uploading traces at scale, configuring automations, using the Insights Agent for trace analysis, or monitoring production agent quality. Use this skill whenever the user mentions production deployment, online evals, trace upload, monitoring agents at scale, automations, alerts, or scaling from development to real users — even if they just say 'my agent is going live' or 'how do I monitor my agent'."
---

# LangSmith Production

You've built your agent, written evals, and iterated on failures. Now it's time to put it in front of real users. This skill covers the techniques you need as your agent moves from internal testing to production: online evaluations, trace management at scale, automated monitoring, and deployment strategies.

## Where production fits in the lifecycle

```
Build → Observe → Offline Evals → **Production**
                                    ^^^^^^^^^^
                                    You are here
```

The lifecycle doesn't change in production — you still build, observe, evaluate, and iterate. But the way you execute each step has to evolve. When you had 20 test cases, you could review every trace yourself. With 500+ traces per day, you need systematic tools.

<setup>

## Setup

```bash
# Required
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=your-production-project

# Optional
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com  # EU users
```

```bash
pip install langsmith openai python-dotenv scipy
```

**CLI:**
```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```
</setup>

<online_evals>

## Online Evaluations

Offline evals test against a dataset when you choose to run them. Online evals automatically score every production trace (or a subset) as it's created. This gives you continuous signal on agent quality.

### Why You Need Online Evals

- **Distribution shift** — real user queries diverge from your test dataset
- **Edge cases** — rare inputs you didn't anticipate
- **Performance degradation** — model updates, API changes, infrastructure issues
- **Cost monitoring** — token usage and latency creeping up

### Four Production Evaluators

**1. Latency SLA Check (code-based, fast)**

```python
def check_latency(run) -> dict:
    latency_ms = (run.end_time - run.start_time).total_seconds() * 1000
    return {
        "score": 1.0 if latency_ms < 3000 else 0.0,
        "comment": f"Latency: {latency_ms:.0f}ms (SLA: 3000ms)"
    }
```

**2. Policy Compliance (code-based, fast)**

```python
def check_policy_compliance(run) -> dict:
    prohibited = ["confidential", "internal only", "not for distribution"]
    output = str(run.outputs)
    violations = [term for term in prohibited if term in output.lower()]
    if violations:
        return {"score": 0.0, "comment": f"Policy violation: {violations}"}
    return {"score": 1.0, "comment": "No policy violations"}
```

**3. Answer Correctness (LLM-judge, slower)**

LLM-as-judge comparing outputs against context or expected behavior.

**4. Helpfulness (LLM-judge, slower)**

Rates whether the response is actionable and addresses the question.

### Online Evaluator Signatures

Online evaluators use `(run)` only — no `example` parameter, since there's no dataset reference:

```python
def online_evaluator(run) -> dict:
    # Only has access to run.inputs and run.outputs
    return {"score": 1.0, "comment": "Passed"}
```

### Uploading Online Evaluators

```bash
# Attach to a project (runs on every trace)
langsmith evaluator upload my_evaluators.py \
  --name "Latency Check" --function check_latency \
  --project "Production Agent" --replace

# Attach to a dataset (runs on experiments)
langsmith evaluator upload my_evaluators.py \
  --name "Schema Check" --function schema_before_query \
  --dataset "officeflow-dataset" --replace
```
</online_evals>

<sampling>

## Sampling Strategies

Evaluating 100% of traces with LLM judges is expensive. Use sampling:

**Random sampling:**
```python
import random
if random.random() < 0.10:  # 10% sample rate
    run_llm_evaluation(trace)
```

**Stratified by category:**
| Category | Sample Rate |
|---|---|
| inventory | 10% |
| policy | 20% |
| out_of_scope | 5% |
| errors | 100% (always evaluate) |

**Always evaluate errors.** If a trace errored, you want to know why — don't skip it.

Code-based evaluators are cheap enough to run on 100% of traces. Reserve sampling for LLM judges.
</sampling>

<thresholds>

## Production Thresholds

Set alert thresholds for each metric:

| Metric | Threshold | Action |
|---|---|---|
| Correctness | < 0.85 | Investigate, consider rollback |
| Helpfulness | < 0.80 | Review low-scoring traces |
| Latency SLA | < 0.95 | Check infrastructure |
| Policy Compliance | < 0.99 | Immediate investigation |

### Deployment Validation

Before promoting a new agent version, compare it statistically against the current baseline:

```python
from scipy import stats

def validate_before_deployment(candidate_scores, baseline_scores):
    """Block deployment on significant 5%+ degradation."""
    t_stat, p_value = stats.ttest_ind(candidate_scores, baseline_scores)
    candidate_mean = sum(candidate_scores) / len(candidate_scores)
    baseline_mean = sum(baseline_scores) / len(baseline_scores)
    degradation = (candidate_mean - baseline_mean) / baseline_mean

    if p_value < 0.05 and degradation < -0.05:
        return False, f"Significant degradation: {degradation:.1%}"
    return True, "Passed validation"
```

### Borderline Scores (Human-in-the-Loop)

Flag traces with uncertain scores for human review:

```python
if 0.4 <= score <= 0.6:  # Borderline
    flag_for_human_review(trace)
if trace.error:
    flag_for_human_review(trace)
if len(trace.inputs.get("question", "")) > 500:  # Long/complex queries
    flag_for_human_review(trace)
```
</thresholds>

<trace_upload>

## Trace Upload at Scale

When you need to upload historical or synthetic traces (for testing, migration, or backfill), use the RunTree API:

```python
from langsmith import Client, RunTree, uuid7
from datetime import datetime, timezone
import json

client = Client()

def upload_traces(traces_file: str, project_name: str):
    with open(traces_file) as f:
        traces = json.load(f)

    # Calculate time shift to present
    latest_ts = max(parse_dt(r["end_time"]) for t in traces for r in t["runs"])
    time_delta = datetime.now(timezone.utc) - latest_ts

    for trace in traces:
        id_map = {}
        # Regenerate IDs preserving relationships
        for run in trace["runs"]:
            id_map[run["id"]] = str(uuid7())

        # Separate root from children
        root_data = next(r for r in trace["runs"] if r.get("parent_run_id") is None)
        children = [r for r in trace["runs"] if r.get("parent_run_id") is not None]

        # Build root RunTree
        root = RunTree(
            name=root_data["name"],
            run_type=root_data["run_type"],
            inputs=root_data["inputs"],
            outputs=root_data["outputs"],
            start_time=shift_time(root_data["start_time"], time_delta),
            end_time=shift_time(root_data["end_time"], time_delta),
            id=id_map[root_data["id"]],
            project_name=project_name,
            client=client,
        )

        # Create children
        for child_data in children:
            child = root.create_child(
                name=child_data["name"],
                run_type=child_data["run_type"],
                inputs=child_data["inputs"],
                outputs=child_data["outputs"],
                start_time=shift_time(child_data["start_time"], time_delta),
                end_time=shift_time(child_data["end_time"], time_delta),
                id=id_map[child_data["id"]],
            )
            child.end()

        root.end()
        root.post(exclude_child_runs=False)

    # CRITICAL: Always flush before exit
    client.flush()
```

### Six Key Patterns

1. **Timestamp shifting** — offset historical timestamps to present time
2. **UUID7 ID mapping** — fresh IDs preserving temporal ordering
3. **Trace grouping** — group runs by trace_id, root first
4. **RunTree construction** — root with `create_child()` for dependents
5. **Reverse-order completion** — children `end()` before parents
6. **Flush before exit** — `client.flush()` or traces will be lost

### Production Considerations

- **Rate limiting:** exponential backoff for HTTP 429 (`wait = 2^attempt`)
- **Batch processing:** chunks of 100 traces, flush after each batch
- **Error recovery:** catch exceptions, log failures, write failed traces to disk
- **Parallel upload:** `ThreadPoolExecutor(max_workers=5)` with thread-local clients

```bash
# Upload script usage
python upload_traces.py --input synthetic_traces.json --project prod-agent-v2
```
</trace_upload>

<insights_agent>

## Insights Agent (Scaling Analysis)

When you have 500+ traces, manual analysis doesn't scale. The Insights Agent automatically processes large batches of traces in three steps:

1. **Summarize** — each trace condensed into a one-line summary using an LLM
2. **Cluster** — summaries grouped by another LLM into clusters of similar behavior
3. **Report** — key findings and actionable insights

This can process hundreds of traces in minutes — giving you the same analysis quality you'd get manually reviewing each one.

Use it to discover:
- Common usage patterns across your user base
- Recurring failure modes you didn't anticipate
- Unexpected agent behaviors at scale
</insights_agent>

<automations>

## Automations & Continuous Monitoring

Online evals generate scores. Automations act on those scores:

| Score Range | Action |
|---|---|
| Low-scoring traces | Route to human review queue |
| High-quality traces | Add to golden dataset (improves your test data) |
| Error traces | Flag for investigation |
| Borderline (0.4-0.6) | Send to human reviewer for judgment |

This is what scaled observability looks like: **online evals generate the signal, automations act on it.** Together, they replace the manual trace review from development.

### Thread-Based Online Evals

Online evals can evaluate entire conversations (threads), not just individual traces. For example, measuring user sentiment across a full conversation gives a more representative picture than NPS scores or like/dislike buttons.
</automations>

<deployment_strategies>

## Deployment Strategies

**Blue-Green:** Deploy new version alongside existing. Route a percentage of traffic. Monitor metrics. Gradually increase or rollback.

**Canary:** Deploy to a single region or user segment. Run continuous evaluations. Compare against baseline. Full rollout only after validation.

**Shadow Mode:** Run new version in parallel without serving its outputs. Compare results against the current version. Evaluate edge cases. Promote after building confidence.

All three strategies rely on the same foundation: tracing + online evals + threshold monitoring.
</deployment_strategies>

<best_practices>

## Best Practices

1. **Start simple.** Begin with code-based online evals (latency, policy compliance). Add LLM judges after you understand your traffic patterns.

2. **Always evaluate errors.** 100% sampling for error traces, regardless of your overall sampling rate.

3. **Calibrate thresholds from historical data.** Don't guess — run your evaluators on existing traces first to understand the baseline distribution.

4. **Combine automated + human review.** Use automations to route borderline cases to humans. The human feedback then improves your evaluators.

5. **Monitor evaluator drift.** LLM judges drift when the underlying model is updated. Re-validate periodically against human-labeled samples.

6. **Version your evaluators.** When you update an evaluator, compare the old and new versions on the same traces to understand the impact.

7. **Flush before exit.** Always call `client.flush()` when uploading traces. Failing to do so will lose data.
</best_practices>
