---
name: jjat-langsmith-evaluators
description: "INVOKE THIS SKILL when writing evaluators for LangSmith, running experiments with evaluate()/aevaluate(), creating code-based evals, LLM-as-judge evaluators, pairwise comparisons, or uploading evaluators via the CLI. Use this skill whenever the user mentions agent evaluation, scoring agent outputs, comparing agent versions, writing evals, checking tool usage, or measuring agent quality — even if they just say 'how do I test my agent' or 'is my agent working correctly'."
---

# LangSmith Evaluators

Evaluators are automated tests that score your agent's outputs. They're how you know whether a prompt change helped or hurt, whether your agent uses tools correctly, and whether it's ready for production. This skill covers all three evaluator types, how to run them, and the patterns that make them reliable.

<setup>

## Setup

```bash
# Required
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_PROJECT=your-project-name
OPENAI_API_KEY=your_openai_key    # For LLM-as-judge evaluators

# Optional
LANGSMITH_WORKSPACE_ID=your_workspace_id  # For org-scoped API keys
```

```bash
pip install langsmith openai python-dotenv
```

```bash
npm install langsmith openai  # TypeScript/Node.js
```

**CLI:**
```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```
</setup>

## Where evaluators fit in the lifecycle

```
Build → Observe → **Offline Evals** → Production
                   ^^^^^^^^^^^^^^
                   Steps 3-4: Create evaluators → Run experiments
```

## Three Evaluator Types

Choose based on what you're measuring:

| Type | Best For | Speed | Cost |
|---|---|---|---|
| **Code-based** | Objective checks: tool usage, format, keywords | Fast | Free |
| **LLM-as-Judge** | Subjective quality: accuracy, helpfulness, safety | Slow | Per-call |
| **Pairwise** | Relative comparison: which version is better? | Slow | Per-call |

The best evaluation strategies combine all three.

## Evaluation Levels

- **Step/Unit** — test a single decision (one tool call, one retrieval query)
- **Final Response** — test the agent's complete output (input in, output out)
- **Trajectory** — test the path the agent takes (which tools, what order, how many steps)

<evaluator_signatures>

## Evaluator Signatures & Return Formats

Every evaluator is just a function. The signature determines what data it receives:

### Signature 1: Outputs Only (simplest)

```python
def mentions_officeflow(outputs: dict) -> bool:
    return "officeflow" in outputs["response"].lower()
```

### Signature 2: Inputs + Outputs

```python
def is_helpful(inputs: dict, outputs: dict) -> dict:
    # Has access to both the question and the agent's answer
    ...
```

### Signature 3: Run + Example (full trace access)

```python
def schema_before_query(run, example) -> dict:
    # run.outputs gives agent output; can inspect tool calls in messages
    # example.inputs / example.outputs gives dataset reference data
    ...
```

### Signature 4: Pairwise (compares two experiments)

```python
def conciseness_evaluator(inputs: dict, outputs: list[dict]) -> list[int]:
    # outputs[0] = experiment A, outputs[1] = experiment B
    # Return [1, 0] if A wins, [0, 1] if B wins, [0, 0] if tie
    ...
```

### Return Formats

**Boolean** — pass/fail:
```python
return True  # or False
```

**Score dictionary** — numeric with explanation:
```python
return {"score": 0.8, "comment": "Mostly correct", "metadata": {"length": 42}}
```

**Pairwise** — preference scores:
```python
return [1, 0]  # A wins
```

### Local vs Uploaded Evaluator Differences

| Behavior | Local (`evaluate()`) | Uploaded (CLI) |
|---|---|---|
| Input type | `RunTree` (attribute access: `run.outputs`) | `dict` (subscript: `run["outputs"]`) |
| Column name | Uses function name or `key` field | Uses `--name` from upload command |
| `key` field | Optional (overrides column name) | Don't include (use `--name` instead) |
| Packages | Full Python environment | Sandboxed, limited packages |

### One Metric Per Evaluator

Each evaluator returns ONE metric. For multiple metrics, create multiple functions. Don't return `{"correctness": 0.8, "helpfulness": 0.9}` — that will error.

### RunTree vs Dict (Python)

Local `evaluate()` passes `RunTree` objects (attribute access: `run.outputs`). Uploaded evaluators receive `dict` (subscript: `run["outputs"]`). Handle both:

```python
run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
```
</evaluator_signatures>

<code_based>

## Code-Based Evaluators

Code-based evals are deterministic, fast, and free. Think of them like unit tests for your agent. The key question: **can I write a function that reliably determines what I'm measuring?** If yes, use code-based.

Good for: tool usage patterns, keyword presence, output format, latency, cost, schema conformance.

### Example: Verify Schema Discovery Before Queries

This checks whether the agent inspects the database schema before querying data — a common best practice:

```python
import re

SCHEMA_PATTERNS = [
    r"PRAGMA\s+table_info",
    r"SELECT\s+.*FROM\s+sqlite_master",
    r"PRAGMA\s+database_list",
    r"\.schema",
]

def _is_schema_query(sql: str) -> bool:
    for pattern in SCHEMA_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            return True
    return False

def _extract_tool_calls(run) -> list[dict]:
    run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
    messages = run_outputs.get("messages", [])
    tool_calls = []
    for msg in messages:
        if isinstance(msg, dict):
            for tc in msg.get("tool_calls", []):
                func = tc.get("function", {})
                tool_calls.append({
                    "name": func.get("name", ""),
                    "arguments": func.get("arguments", ""),
                })
    return tool_calls

def schema_before_query(run, example) -> dict:
    """Score 1 if agent checks DB schema before querying data, 0 otherwise."""
    tool_calls = _extract_tool_calls(run)
    db_calls = [tc for tc in tool_calls if tc["name"] == "query_database"]

    if not db_calls:
        return {"score": 1, "comment": "No query_database calls -- not applicable"}

    seen_schema_check = False
    for tc in db_calls:
        sql = tc.get("arguments", "")
        if _is_schema_query(sql):
            seen_schema_check = True
        else:
            if not seen_schema_check:
                return {
                    "score": 0,
                    "comment": f"Agent queried data without checking schema first. First query: {sql[:200]}",
                }
            break

    if seen_schema_check:
        return {"score": 1, "comment": "Agent checked schema before querying data"}
    return {"score": 1, "comment": "All calls were schema inspections"}
```

### Example: Simple Output Checks

```python
# Boolean: does the response mention the company name?
def mentions_officeflow(outputs: dict) -> bool:
    return "officeflow" in outputs["response"].lower()

# Scored: is the response concise?
def response_length_score(outputs: dict) -> dict:
    length = len(outputs.get("response", ""))
    if length < 100:
        return {"score": 1.0, "comment": "Concise"}
    elif length < 200:
        return {"score": 0.7, "comment": "Moderate"}
    else:
        return {"score": 0.3, "comment": "Verbose", "metadata": {"length": length}}
```

### Safe Evaluator Pattern

Handle both RunTree (local) and dict (uploaded) gracefully:

```python
def safe_evaluator(run, example) -> dict:
    try:
        outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {})
        if not outputs:
            return {"score": 0, "comment": "No outputs found"}
        response = outputs.get("response", "")
        if not response:
            return {"score": 0, "comment": "Empty response"}
        # ... your evaluation logic ...
        return {"score": 1, "comment": "Passed"}
    except Exception as e:
        return {"score": 0, "comment": f"Evaluation error: {str(e)}"}
```
</code_based>

<llm_judge>

## LLM-as-Judge Evaluators

When what you're measuring is too subjective for code — helpfulness, accuracy, tone, safety — use an LLM to judge. This is powerful but requires discipline to be reliable.

### Three Rules for Reliable LLM Judges

1. **Keep a narrow scope.** One specific criterion per judge. Not "Is this a good response?" but "Did the agent leak stock information?" or "Does the agent have a professional tone?"

2. **Binary or categorical only.** Rating helpfulness 1-5 creates nice graphs but what's the difference between 3.2 and 3.7? Make evals binary (yes/no) or categorical for actionable results.

3. **Align with human reviewers.** Have humans label a sample of the same outputs your judge scores. Where they disagree, refine the prompt. This turns a rough heuristic into a reliable evaluator.

### Example: Binary Classification (Stock Leakage)

```python
from openai import OpenAI

client = OpenAI()

def check_stock_leakage(inputs: dict, outputs: dict) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You check if customer support responses leak exact stock quantities. Answer only 'yes' or 'no'."},
            {"role": "user", "content": f"""Question: {inputs['question']}
Response: {outputs['answer']}

Does this response reveal specific stock numbers (e.g., '31 units', '450 in stock')?
Answer yes or no."""}
        ]
    )
    leaked = response.choices[0].message.content.strip().lower() == "yes"
    return {
        "score": 0 if leaked else 1,
        "comment": "Stock quantity leaked" if leaked else "No leakage detected"
    }
```

### Example: Correctness with Reference Answer

```python
from openai import OpenAI

client = OpenAI()

CORRECTNESS_PROMPT = """You are evaluating an AI agent's response.

User Question: {question}
Agent Response: {response}
Reference: {reference}

Is the agent's response correct and helpful?
Answer only 'yes' or 'no'."""

def evaluate_correctness(run, example) -> dict:
    question = example.inputs.get("question", "")
    response = run.outputs.get("answer", "") if hasattr(run, "outputs") else run.get("outputs", {}).get("answer", "")
    reference = example.outputs.get("reference_answer", "N/A") if hasattr(example, "outputs") else example.get("outputs", {}).get("reference_answer", "N/A")

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "user", "content": CORRECTNESS_PROMPT.format(
                question=question, response=response, reference=reference
            )}
        ]
    )

    correct = result.choices[0].message.content.strip().lower() == "yes"
    return {"score": 1 if correct else 0, "comment": "Correct" if correct else "Incorrect"}
```

### Async LLM Judges (Recommended)

LLM judge evaluators benefit from async — they run concurrently during `aevaluate()`:

```python
from openai import AsyncOpenAI

async_client = AsyncOpenAI()

async def check_stock_leakage_async(inputs: dict, outputs: dict) -> dict:
    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You check if responses leak exact stock quantities. Answer only 'yes' or 'no'."},
            {"role": "user", "content": f"Question: {inputs['question']}\nResponse: {outputs['answer']}\n\nDoes this reveal specific stock numbers?"}
        ]
    )
    leaked = response.choices[0].message.content.strip().lower() == "yes"
    return {"score": 0 if leaked else 1, "comment": "Leaked" if leaked else "No leakage"}
```

### Example: Multi-Criteria (use separate evaluators)

Instead of one judge evaluating 4 criteria, create 4 focused judges:

```python
# Each is narrow, binary, and actionable
def eval_helpfulness(inputs, outputs) -> dict: ...
def eval_accuracy(inputs, outputs) -> dict: ...
def eval_conciseness(inputs, outputs) -> dict: ...
def eval_professionalism(inputs, outputs) -> dict: ...

# Run them all
results = evaluate(agent, data="my-dataset",
    evaluators=[eval_helpfulness, eval_accuracy, eval_conciseness, eval_professionalism])
```
</llm_judge>

<pairwise>

## Pairwise Evaluation

Some metrics are too subjective for absolute scoring but easy to judge comparatively. "Is response A or B more concise?" is much easier than "Rate this response's conciseness from 1-5."

Use pairwise when comparing two agent versions (different prompts, models, or tools).

### Three-Step Process

**Step 1: Run both agents on the same dataset**

```python
import asyncio
from langsmith import aevaluate, uuid7

DATASET = "officeflow-dataset"

async def wrapper_v4(inputs: dict) -> dict:
    agent_v4.thread_id = str(uuid7())
    r = await agent_v4.chat(inputs["question"])
    return {"answer": r["output"], "messages": r["messages"]}

async def wrapper_v5(inputs: dict) -> dict:
    agent_v5.thread_id = str(uuid7())
    r = await agent_v5.chat(inputs["question"])
    return {"answer": r["output"], "messages": r["messages"]}

v4_results = await aevaluate(wrapper_v4, data=DATASET, experiment_prefix="agent-v4")
v5_results = await aevaluate(wrapper_v5, data=DATASET, experiment_prefix="agent-v5")
```

**Step 2: Create the pairwise evaluator**

```python
from openai import OpenAI

client = OpenAI()

CONCISENESS_PROMPT = """You are evaluating two responses to the same customer question.
Determine which response is MORE CONCISE while still providing all crucial information.

**Conciseness** means getting straight to the point, avoiding filler, and not repeating information.
**Crucial information** includes direct answers, necessary context, and required next steps.

A shorter response is NOT automatically better if it omits crucial information.

**Question:** {question}

**Response A:**
{response_a}

**Response B:**
{response_b}

Output your verdict as a single number:
1 if Response A is more concise while preserving crucial information
2 if Response B is more concise while preserving crucial information
0 if they are roughly equal"""

def conciseness_evaluator(inputs: dict, outputs: list[dict]) -> list[int]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a conciseness evaluator. Respond with only: 0, 1, or 2."},
            {"role": "user", "content": CONCISENESS_PROMPT.format(
                question=inputs["question"],
                response_a=outputs[0].get("answer", "N/A"),
                response_b=outputs[1].get("answer", "N/A"),
            )}
        ],
    )
    preference = int(response.choices[0].message.content.strip())
    if preference == 1:
        return [1, 0]  # A wins
    elif preference == 2:
        return [0, 1]  # B wins
    return [0, 0]      # Tie
```

**Step 3: Run the pairwise comparison**

```python
from langsmith import evaluate

evaluate(
    (v4_results.experiment_name, v5_results.experiment_name),
    evaluators=[conciseness_evaluator],
    randomize_order=True,  # CRITICAL: prevents position bias
)
```

`randomize_order=True` is essential — LLMs sometimes favor the first or second option systematically.
</pairwise>

<running_experiments>

## Running Experiments

### Basic (Sync)

```python
from langsmith import evaluate

results = evaluate(
    my_agent_function,
    data="my-dataset",
    evaluators=[schema_before_query, eval_correctness],
    experiment_prefix="agent-v5"
)
```

### Async (Recommended for I/O-bound agents)

```python
from langsmith import aevaluate

results = await aevaluate(
    async_agent_wrapper,
    data="my-dataset",
    evaluators=[schema_before_query, eval_correctness],
    experiment_prefix="agent-v5",
    max_concurrency=5,
)
```

### Test Isolation

Create a fresh thread_id for each example so conversations don't leak between test cases:

```python
import agent_v5
from langsmith import uuid7

def run_agent(inputs: dict) -> dict:
    agent_v5.thread_id = str(uuid7())  # Fresh state per example
    return asyncio.run(agent_v5.chat(inputs["question"]))
```

### Combining Evaluators

Mix all three types in one experiment:

```python
results = await aevaluate(
    chat_wrapper,
    data="officeflow-dataset",
    evaluators=[
        schema_before_query,      # Code-based: checks tool usage
        eval_correctness,          # LLM-judge: checks accuracy
        check_stock_leakage,       # LLM-judge: checks safety
        response_length_score,     # Code-based: checks verbosity
    ],
    experiment_prefix="comprehensive-v5"
)
```

### ExperimentResults

The returned object gives you:
- `experiment_name` — for referencing in pairwise comparisons
- `experiment_url` — link to view results in LangSmith UI
- Individual results with inputs, outputs, and scores

### Capturing Trajectories (LangGraph)

For LangGraph agents, capture the full trajectory using `stream_mode="debug"`:

```python
async def run_agent_with_trajectory(inputs: dict) -> dict:
    events = []
    async for event in graph.astream(
        {"messages": [{"role": "user", "content": inputs["question"]}]},
        stream_mode="debug",
        subgraphs=True,
    ):
        events.append(event)
    # Extract tool calls, intermediate steps from events
    return {"answer": final_answer, "trajectory": extracted_steps}
```

For non-LangChain agents, capture trajectories via callbacks, hooks, or parsing your agent's execution logs into the expected format.

### Pytest Integration

LangSmith integrates with pytest for CI/CD:
- Write evals as test functions
- Results logged to LangSmith automatically
- Granular control per test case
</running_experiments>

<uploading_evaluators>

## Uploading Evaluators via CLI

Uploaded evaluators run automatically — you don't need to pass them to `evaluate()`.

**Offline evaluators** (attached to a dataset): auto-run when you run experiments on that dataset.
**Online evaluators** (attached to a project): auto-run on every production trace.

```bash
# List all evaluators
langsmith evaluator list

# Upload offline evaluator (to dataset)
langsmith evaluator upload my_evaluators.py \
  --name "Schema Check" --function schema_before_query \
  --dataset "officeflow-dataset" --replace

# Upload online evaluator (to project)
langsmith evaluator upload my_evaluators.py \
  --name "Policy Compliance" --function check_policy_compliance \
  --project "Production Agent" --replace

# Delete
langsmith evaluator delete "Schema Check"
```

**Constraints for uploaded evaluators:**
- Run in a sandboxed environment with very limited packages
- Place ALL imports inside the function body
- Only use built-in/standard library imports
- CLI only supports code evaluators (not LLM-as-Judge)
- For LLM judges, prefer running locally with `evaluate(evaluators=[...])`

**Safety:** The CLI prompts before destructive operations. Never use `--yes` unless the user explicitly requests it.
</uploading_evaluators>

<typescript_evaluators>

## TypeScript Evaluators

TypeScript evaluators follow the same patterns with slightly different syntax:

```typescript
import { evaluate } from "langsmith/evaluation";
import OpenAI from "openai";

const client = new OpenAI();

// Code-based evaluator
function mentionsOfficeflow({ outputs }: { outputs: Record<string, any> }) {
  return { key: "mentions_officeflow", score: outputs.response?.toLowerCase().includes("officeflow") ? 1 : 0 };
}

// LLM-as-Judge evaluator
async function checkLeakage({ inputs, outputs }: { inputs: Record<string, any>; outputs: Record<string, any> }) {
  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    temperature: 0,
    messages: [
      { role: "system", content: "Check if the response leaks stock numbers. Answer yes or no." },
      { role: "user", content: `Question: ${inputs.question}\nResponse: ${outputs.answer}` },
    ],
  });
  const leaked = response.choices[0].message.content?.trim().toLowerCase() === "yes";
  return { key: "stock_leakage", score: leaked ? 0 : 1 };
}

// Run experiment
await evaluate(myAgentFunction, {
  data: "my-dataset",
  evaluators: [mentionsOfficeflow, checkLeakage],
  experimentPrefix: "agent-v5",
});
```

Key differences from Python:
- Return `{ key: "name", score, comment }` (must include `key` when running locally)
- Omit `key` when uploading evaluators via CLI (use `--name` instead)
- Evaluators receive destructured `{ inputs, outputs, run, example }`
</typescript_evaluators>

<best_practices>

## Best Practices

1. **Inspect before you implement.** Run your agent on sample inputs, look at the actual output structure, then write evaluators. Never assume the output shape.

2. **Start with code-based evals.** They're fast, free, and deterministic. Add LLM judges only for criteria code can't handle.

3. **One criterion per LLM judge.** Narrow scope = reliable results. "Did the agent leak stock info?" not "Is this a good response?"

4. **Binary over numeric scales.** A pass/fail result is actionable. A 3.7/5 score is ambiguous.

5. **Test evaluators on known examples.** Before running at scale, verify your evaluator returns the right score on cases where you know the answer.

6. **Use `temperature=0` for LLM judges.** Reduces variance between runs.

7. **Fresh `uuid7()` per example.** Prevents conversation state from leaking between test cases.

8. **Match run function output to dataset schema.** If your agent returns `{"answer": ...}`, your evaluator should access `outputs["answer"]` — not `outputs["response"]`.
</best_practices>

<troubleshooting>

## Troubleshooting

**Evaluator returns unexpected results:**
- Print your agent's raw output first: `print(run.outputs)` or `print(outputs)`
- Check field names match between run function and evaluator
- Query LangSmith traces to verify what data is actually available

**"Multiple metrics" error:**
- Each evaluator must return ONE metric. Create separate functions for each criterion.

**RunTree vs dict confusion:**
- Use the safe pattern: `run.outputs if hasattr(run, "outputs") else run.get("outputs", {})`

**Uploaded evaluator fails:**
- Imports must be inside the function body
- Only standard library is available in the sandbox
- Test locally with `evaluate(evaluators=[...])` first

**Pairwise comparison issues:**
- Both experiments must use the same dataset
- Always use `randomize_order=True` to prevent position bias
- Experiment names come from `results.experiment_name`, not the prefix

## Resources

- [LangSmith Evaluation Concepts](https://docs.smith.langchain.com/evaluation/concepts)
- [Custom Code Evaluators](https://docs.smith.langchain.com/evaluation/how_to_guides/custom_evaluator)
- [OpenEvals — readymade evaluators](https://github.com/langchain-ai/openevals)
</troubleshooting>
