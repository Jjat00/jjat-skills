---
name: jjat-langsmith-datasets
description: "INVOKE THIS SKILL when creating evaluation datasets for LangSmith, uploading test cases, managing dataset examples, or building test scenarios from a PRD or production traces. Use this skill whenever the user mentions LangSmith datasets, evaluation data, test cases for agents, golden answers, or wants to create/upload/manage datasets for agent evaluation — even if they just say 'I need test data for my agent'."
---

# LangSmith Datasets

Datasets are the foundation of repeatable agent evaluation. Without a good dataset, your evals are meaningless — you're testing against nothing. This skill covers how to build, structure, and manage datasets that actually catch regressions and measure quality.

## Where datasets fit in the lifecycle

```
Build → Observe → **Offline Evals** → Production
                   ^^^^^^^^^^^^^^
                   You are here: Step 2 of 4 (Decide → Dataset → Evaluator → Experiment)
```

The Four-Step Eval Flow: (1) Decide what to measure, (2) **Create a dataset**, (3) Write an evaluator, (4) Run an experiment. This skill is Step 2.

<setup>

## Setup

```bash
# Required
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_PROJECT=your-project-name

# Optional
LANGSMITH_WORKSPACE_ID=your_workspace_id  # For org-scoped API keys
```

```bash
pip install langsmith python-dotenv
```

```bash
npm install langsmith  # TypeScript/Node.js
```

**CLI:**
```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```

Check `LANGSMITH_PROJECT` in the user's `.env` — this tells you which project has their traces (useful when creating datasets from production data).
</setup>

<dataset_structure>

## Dataset Structure

Each example in a dataset has three parts:

- **Inputs** (required): what gets sent to your agent — typically `{"question": "..."}`.
- **Reference outputs** (optional): expected answers or metadata for evaluators. These are NOT sent to the agent — they're only used by evaluators to compare against.
- **Metadata** (optional): tags, difficulty, category — useful for filtering and analysis.

```json
{
  "inputs": {"question": "Do you have printer paper in stock?"},
  "outputs": {
    "reference_answer": "Should check database and provide current inventory",
    "expected_tool": "query_database",
    "should_check_schema": true
  },
  "metadata": {"category": "inventory_check", "difficulty": "easy"}
}
```

The outputs schema is yours to define — it just needs to match what your evaluators expect.
</dataset_structure>

<building_datasets>

## How to Build a Good Dataset

Building a dataset isn't just dumping questions into a file. The quality of your dataset directly determines the quality of your evals. Here's the process that works:

### 1. Start with Your PRD

Your agent's Product Requirements Document defines what it should and shouldn't do. This is where your test scenarios come from.

```markdown
# Agent PRD — Key Scenarios

## Happy Paths
- Inventory queries: "Do you have spiral notebooks?"
- Policy questions: "What's your return policy?"

## Edge Cases
- Vague inputs: "Notebooks" (no context)
- Multi-part: "Do you have notebooks, and what's bulk pricing?"

## Out of Scope
- "What's the weather?" → politely decline

## Failure Modes (from debugging)
- Agent guesses schema instead of discovering it
- Agent reveals exact stock quantities
```

### 2. Derive Test Scenarios

Turn each PRD scenario into one or more dataset examples. Cover:
- **Happy paths** — core use cases that should always work
- **Edge cases** — ambiguous, multi-part, unusual inputs
- **Error scenarios** — invalid inputs, out-of-scope requests
- **Complex workflows** — multi-step, multiple tools needed
- **Known failures** — bugs you've found and fixed (regression tests)

### 3. Write the Questions

Start small: 10-25 high-quality examples that cover your key scenarios. You can write these by hand or use an LLM to generate diverse variations.

### 4. Add Reference Outputs (If Needed)

If your evaluator compares agent output against a reference answer (like an LLM-as-judge checking correctness), include those as reference outputs. Not every evaluator needs them — code-based evals that check tool usage don't.

### 5. Involve Domain Experts

Building a dataset is a great opportunity to involve subject matter experts. They know the desired behavior better than anyone and can flag edge cases you'd miss.

### Improving Your Dataset Over Time

A dataset isn't static. Keep improving it:

- **Add low-scoring examples from online evals** — if production traces score poorly, add those scenarios to track improvement
- **Add negative user feedback** — real user complaints point to gaps in your test coverage
- **Add unexpected inputs** — anything users send that your PRD didn't anticipate
- **Version your datasets** — LangSmith datasets are versioned, so you can update examples without breaking existing experiments
</building_datasets>

<coverage_categories>

## Example Coverage Categories

Organize your dataset by category so you can track which areas are well-tested and which have gaps:

| Category | Example Input | What It Tests |
|---|---|---|
| inventory_queries | "Do you have spiral notebooks in stock?" | SQL tool usage, product lookup |
| policy_questions | "What's your return policy?" | Knowledge base search, policy citation |
| frustrated_customers | "I've been waiting 3 weeks for my order!" | Tone, escalation, empathy |
| multi_part_requests | "Do you have notebooks, and what's bulk pricing?" | Multiple tools, combined answers |
| edge_cases | "Notebooks" (vague) | Clarification, best-effort handling |
| out_of_scope | "What's the weather?" | Polite decline, scope boundaries |
| regression_tests | Cases from past bugs | Prevent re-introducing fixed issues |

Start with 2-3 examples per category. That gives you 14-21 examples — a solid starting dataset.
</coverage_categories>

<creation_methods>

## Three Ways to Create Datasets

### Method 1: LangSmith UI Upload

The simplest approach for small datasets:

1. Navigate to **Datasets** in LangSmith
2. Click **New Dataset**
3. Name it and upload a CSV
4. Map columns to inputs/outputs

CSV format:
```csv
question,reference_answer,expected_tool,category
"Do you have printer paper?","Should check inventory","query_database","inventory"
"What's your return policy?","60-day return window, RMA required","search_knowledge_base","policy"
```

### Method 2: Programmatic Creation (SDK)

Best for building datasets from code or generating them dynamically:

```python
from langsmith import Client

client = Client()

# Create the dataset
dataset = client.create_dataset(
    dataset_name="officeflow-dataset",
    description="Customer support evaluation dataset"
)

# Add examples one at a time
client.create_example(
    dataset_id=dataset.id,
    inputs={"question": "Do you have printer paper in stock?"},
    outputs={
        "reference_answer": "Should check database and provide current inventory",
        "expected_tool": "query_database",
        "should_check_schema": True
    },
    metadata={"category": "inventory_check"}
)

# Or add multiple at once
client.create_examples(
    inputs=[
        {"question": "What's your return policy?"},
        {"question": "How long does shipping take?"},
    ],
    outputs=[
        {"reference_answer": "60-day return window, RMA required", "expected_tool": "search_knowledge_base"},
        {"reference_answer": "Standard 3-5 days, $8.95, free over $100", "expected_tool": "search_knowledge_base"},
    ],
    dataset_name="officeflow-dataset",
)
```

**TypeScript:**
```typescript
import Client from "langsmith";

const client = new Client();

const dataset = await client.createDataset("officeflow-dataset", {
  description: "Customer support evaluation dataset",
});

await client.createExamples({
  inputs: [{ question: "Do you have printer paper?" }],
  outputs: [{ reference_answer: "Should check inventory", expected_tool: "query_database" }],
  datasetId: dataset.id,
});
```

### Method 3: From Production Traces

The most powerful approach — build datasets from real user interactions:

```bash
# Export traces from your project
langsmith trace export ./traces --project my-project --limit 50 --full
```

```python
import json
from pathlib import Path
from langsmith import Client

client = Client()

# Process exported traces into dataset examples
examples = []
for jsonl_file in Path("./traces").glob("*.jsonl"):
    runs = [json.loads(line) for line in jsonl_file.read_text().strip().split("\n")]
    root = next((r for r in runs if r.get("parent_run_id") is None), None)
    if root and root.get("inputs") and root.get("outputs"):
        examples.append({
            "inputs": root["inputs"],
            "outputs": root["outputs"],
            "trace_id": root.get("trace_id", root.get("id"))
        })

# Upload as a dataset
with open("/tmp/dataset.json", "w") as f:
    json.dump(examples, f, indent=2)
```

```bash
langsmith dataset upload /tmp/dataset.json --name "Production Traces Dataset"
```

You can also filter traces by feedback scores to only include high-quality or problematic interactions.
</creation_methods>

<dataset_types>

## Dataset Types by Evaluation Goal

Different evaluation goals need different dataset structures:

### Final Response (most common)
Test the agent's complete answer. Simplest to set up.
```json
{"inputs": {"question": "Do you have copy paper?"}, "outputs": {"reference_answer": "Should check inventory and report availability"}, "trace_id": "optional-source-trace-id"}
```

### Trajectory
Test the path the agent takes — which tools it calls and in what order.
```json
{"inputs": {"question": "Do you have copy paper?"}, "outputs": {"expected_trajectory": ["query_database", "query_database"]}, "trace_id": "optional-source-trace-id"}
```

### Single Step
Test a specific node in isolation (one LLM call, one tool).
```json
{"inputs": {"messages": [{"role": "user", "content": "..."}]}, "outputs": {"content": "expected output"}, "metadata": {"node_name": "query_database"}, "trace_id": "optional-source-trace-id"}
```

### RAG
Test retrieval quality — what was retrieved, what was cited.
```json
{"inputs": {"question": "What's the return policy?"}, "outputs": {"answer": "60-day window...", "retrieved_chunks": ["..."], "cited_chunks": ["..."]}, "trace_id": "optional-source-trace-id"}
```

The `trace_id` field is optional — it links a dataset example back to the source production trace for traceability.
</dataset_types>

<cli_reference>

## CLI Reference

```bash
# List all datasets
langsmith dataset list

# Get dataset details
langsmith dataset get "officeflow-dataset"

# Create an empty dataset
langsmith dataset create --name "My Dataset" --description "For evaluation"

# Upload a local JSON file as a dataset
langsmith dataset upload /tmp/dataset.json --name "My Dataset"

# Export a dataset to local file
langsmith dataset export "My Dataset" /tmp/exported.json --limit 100

# Delete a dataset
langsmith dataset delete "My Dataset"

# List examples in a dataset
langsmith example list --dataset "My Dataset" --limit 10

# Add a single example
langsmith example create --dataset "My Dataset" \
  --inputs '{"question": "test query"}' \
  --outputs '{"answer": "expected result"}'

# Delete an example
langsmith example delete <example-id>

# List experiments for a dataset
langsmith experiment list --dataset "My Dataset"

# Get experiment results
langsmith experiment get "eval-v1"
```

**Safety:** The CLI prompts for confirmation before destructive operations.
- If running with user input: ALWAYS wait for user confirmation
- If running non-interactively (scripts/CI): use `--yes` to skip prompts
- Never use `--yes` in interactive sessions unless the user explicitly requests it
</cli_reference>

<best_practices>

## Best Practices

1. **Start small, iterate.** 10-25 examples covering core scenarios is enough to start. Expand as you discover new failure modes.

2. **Match your dataset schema to your run function output.** If your agent returns `{"answer": "...", "messages": [...]}`, your evaluator needs to know those field names. Keep them consistent.

3. **Include challenging examples.** A dataset of only easy questions won't catch regressions. Include at least 30% edge cases and known-difficult scenarios.

4. **Separate dev and validation sets.** If you're tuning prompts against your dataset, keep a held-out validation set to avoid overfitting.

5. **Use metadata for filtering.** Tag examples by category, difficulty, and source so you can analyze eval results by segment.

6. **Datasets are versioned.** You can update examples in LangSmith without breaking existing experiments. Old experiments keep their snapshot.

7. **Reference outputs are optional.** Code-based evaluators that check tool usage (like `schema_before_query`) don't need reference answers at all — they inspect the run's trace directly.
</best_practices>

<troubleshooting>

## Troubleshooting

**Dataset upload fails:**
- Verify `LANGSMITH_API_KEY` is set
- Check JSON is valid: each element needs an `inputs` key (and optionally `outputs`)
- Dataset name must be unique — delete existing first with `langsmith dataset delete` if needed

**Empty dataset after upload:**
- Verify JSON contains an array of objects with `inputs` key
- Check with `langsmith example list --dataset "Name"`

**Export has no data:**
- Ensure traces were exported with `--full` flag to include inputs/outputs
- Verify traces have both `inputs` and `outputs` populated

**Example count mismatch:**
- Use `langsmith dataset get "Name"` to check the remote example count
- Compare with your local file: `cat dataset.json | python -c "import json,sys; print(len(json.load(sys.stdin)))"`
- Re-upload if counts differ

**Field name mismatches in evals:**
- Your run function output keys must match what your evaluators expect
- Use `client.read_example(example_id)` to inspect dataset schema
- Print your run function output first: `print(f"DEBUG: {result.keys()}")`
</troubleshooting>
