# LangSmith Evaluator v2 - Reference Documentation

> Compiled from: langchain-ai/lca-reliable-agents repo + mintlify docs (23 pages) + local Python source (19 files) + PDF "Agentes_IA_Confiables" (27 pages)

---

## TABLE OF CONTENTS

1. [Setup & Configuration](#1-setup--configuration)
2. [Agent Engineering Lifecycle](#2-agent-engineering-lifecycle)
3. [Tracing Fundamentals](#3-tracing-fundamentals)
4. [Agent Patterns](#4-agent-patterns)
5. [Analyzing & Debugging Agents](#5-analyzing--debugging-agents)
6. [Datasets](#6-datasets)
7. [Evaluation Approach (Levels & Metrics)](#7-evaluation-approach-levels--metrics)
8. [The Four-Step Eval Flow](#8-the-four-step-eval-flow)
9. [Running Experiments](#9-running-experiments)
10. [Code-Based Evaluators](#10-code-based-evaluators)
11. [LLM-as-Judge Evaluators](#11-llm-as-judge-evaluators)
12. [Pairwise Comparison Evaluators](#12-pairwise-comparison-evaluators)
13. [Evaluator Signatures & Return Formats](#13-evaluator-signatures--return-formats)
14. [Online Evaluation (Production)](#14-online-evaluation-production)
15. [Insights Agent (Scaling Analysis)](#15-insights-agent-scaling-analysis)
16. [Automations & Continuous Monitoring](#16-automations--continuous-monitoring)
17. [Trace Upload at Scale](#17-trace-upload-at-scale)
18. [Best Practices & Pitfalls](#18-best-practices--pitfalls)
19. [Complete Code Examples](#19-complete-code-examples)

---

## PDF-SOURCED CONTENT (Agentes_IA_Confiables.pdf - 27 pages)

The following sections are sourced from or enriched by the PDF course material.

---

## 2. AGENT ENGINEERING LIFECYCLE

The lifecycle has four stages that repeat iteratively:

```
Build → Observe → Offline Evals → Production (Online Evals)
  ↑                                        |
  └────────────────────────────────────────┘
```

### Stage 1: Build
- Create your agent with foundation model, system prompt, and tools
- Define your PRD (Product Requirements Document)

### Stage 2: Observe (Pre-Production)
- Set up tracing with LangSmith
- Run agent against PRD scenarios
- Debug using three workflows: Tracing UI, Playground & Polly, CLI & Coding Agents
- Track failure modes for later evaluation

### Stage 3: Offline Evals
- Turn failure modes into automated evaluations
- Create datasets from PRD scenarios
- Write evaluators (code-based, LLM-as-judge, pairwise)
- Run experiments to measure quality

### Stage 4: Production (Online Evals)
- Upload traces at scale
- Online evaluations score every production trace automatically
- Automations act on scores (route low-scoring to human review, add high-quality to datasets)
- Insights Agent analyzes patterns across hundreds of traces

---

## 5. ANALYZING & DEBUGGING AGENTS

### Step 0: Create Your Agent
Start with a working agent that has tracing enabled.

### Step 1: Create Your Agent's PRD
A simple one-page document defining what your agent should do, scenarios it should handle, and what success looks like. Closely aligned with your agent's system prompt.

**Example PRD structure:**

```markdown
# Agent Name - PRD

## Purpose
What the agent does and who it serves.

## Tools
- Tool 1 --- description
- Tool 2 --- description

## Behavior Rules
- Always use X tool for Y questions
- Never reveal Z information
- Professional tone
- If out of scope, say so politely

## Scenarios and Expected Behavior

| Input | Expected Behavior |
|-------|-------------------|
| "Do you have X?" | Use SQL tool -> find product -> respond appropriately |
| "What's your return policy?" | Use KB tool -> cite specific policy details |
| "What's the weather?" | Politely decline -- outside scope |
```

### Step 2: Run, Observe, Debug (Iterative Loop)

Run agent against PRD scenarios. When something breaks, use LangSmith to investigate.

**Three debugging workflows:**

1. **LangSmith Tracing UI** - Open trace, inspect each step, identify where the agent went wrong
2. **Playground & Polly** - Freeze successful steps, iteratively debug the failing step without re-running the entire agent
3. **CLI & Coding Agents** - Query trace data programmatically from terminal

```bash
# Install LangSmith CLI
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh

# View available commands
langsmith --help
```

### Step 3: Track Failure Modes

Common failure patterns to look for:
- Agent didn't use tools correctly
- Agent revealed sensitive information
- Agent struggled with specific query types
- Agent took too many steps (inefficient)
- Agent ignored tool results

These failures become the basis for your evaluations in the next stage.

---

## 7. EVALUATION APPROACH (LEVELS & METRICS)

### Evaluation Levels

**Step or Unit Evaluation:**
Evaluating a single step or decision (tool call, retrieval query, parsing function). Test components in isolation if you can define expected input/output.

**Final Response / End-to-End Evaluation:**
Input in, output out. Evaluate the agent's final response. Simplest to set up. Can still use trace information from internal steps.

**Trajectory Evaluation:**
Evaluate the path the agent takes, not just where it ends up. Measures: number of steps, number of tool calls, order of tool calls. "An agent's path to a final answer is suboptimal even when the answer itself is correct."

### Metrics Taxonomy

**Operational metrics:**
- Latency / time to first token / end-to-end response time
- Token usage (input, output, total)
- Cost per run / per session

**Output quality metrics:**
- Correctness / accuracy against a reference answer
- Relevance -- does the response address the question?
- Faithfulness / groundedness -- grounded in context or hallucinated?
- Toxicity / safety -- harmful or inappropriate?
- Conciseness -- appropriately brief or unnecessarily verbose?

**Trajectory metrics:**
- Task completion / success rate
- Tool selection/call accuracy
- Planning -- did the agent create and follow a plan?
- Efficiency -- completed without repeating steps or redundant calls?

---

## 8. THE FOUR-STEP EVAL FLOW

1. **Decide on Your Eval** - What would tell me if my agent is working well?
2. **Create a Dataset** - Inputs, optional expected outputs, metadata
3. **Create an Evaluator** - Code-based, LLM-as-judge, or human review (best: combination of all three)
4. **Run an Experiment** - Execute eval, collect results, track over time

---

## 15. INSIGHTS AGENT (SCALING ANALYSIS)

When you have 500+ traces from beta testers, manual analysis doesn't scale. The Insights Agent automatically analyzes traces.

### Three-Step Pipeline

1. **Summarize traces** - Each trace condensed into a one-line summary using an LLM
2. **Cluster summaries** - Grouped by another LLM into clusters of similar behavior
3. **Generate report** - Key findings and actionable insights

Can process hundreds of traces in minutes.

---

## 16. AUTOMATIONS & CONTINUOUS MONITORING

Online evals score every trace. Automations filter and act on those scores:

- **Low-scoring traces** → Route to human review queue
- **High-quality traces** → Add to golden dataset
- **Error traces** → Flag for investigation
- **Sentiment analysis** → Track user satisfaction across conversations

This replaces manual trace review with a system that works at any volume.

### Thread-Based Online Evals

Online evals can evaluate entire conversations (threads), not just individual traces. Example: measuring user sentiment across an entire conversation.

---

## 1. SETUP & CONFIGURATION

### Environment Variables

```bash
# Required
OPENAI_API_KEY='your_openai_api_key_here'
LANGSMITH_API_KEY='your_langsmith_api_key_here'
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=your-project-name

# Optional
ANTHROPIC_API_KEY='your_anthropic_key'           # For multi-model consensus
LANGSMITH_WORKSPACE_ID=your-workspace-id          # For org-scoped keys
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com  # EU users
```

### Python Dependencies

```bash
pip install langsmith>=0.6.0 openai python-dotenv numpy langchain-openai
# or with uv:
uv sync
```

### CLI Tool (for uploading evaluators)

```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```

---

## 2. TRACING FUNDAMENTALS

### Core Concepts

Tracing captures:
- Inputs and outputs at every step
- Timing and latency for performance analysis
- Parent-child relationships showing how operations nest
- Metadata and tags for filtering and organization
- Errors and exceptions with full context

### Instrumenting an Agent

Two modifications needed:
1. Wrap OpenAI client with `wrap_openai()` for automatic LLM call tracing
2. Add `@traceable` decorator to functions requiring observation

```python
from openai import AsyncOpenAI
from langsmith import traceable, uuid7
from langsmith.wrappers import wrap_openai

client = wrap_openai(AsyncOpenAI())
thread_id = str(uuid7())

@traceable(name="query_database", run_type="tool")
def query_database(query: str, db_path: str) -> str:
    """Execute SQL query against the inventory database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return str(results)
    except Exception as e:
        return f"Error: {str(e)}"

@traceable(name="search_knowledge_base", run_type="tool")
async def search_knowledge_base(query: str, top_k: int = 2) -> str:
    """Search knowledge base using semantic similarity."""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding
    # ... cosine similarity logic ...
    return "\n".join(results)

@traceable(name="Emma", metadata={"thread_id": thread_id})
async def chat(question: str) -> dict:
    """Process a user question and return assistant response."""
    # ... agent logic ...
    return {"messages": messages, "output": final_content}
```

### Run Type Categories

- **llm**: Direct language model calls (auto-traced by wrap_openai)
- **chain**: Operation sequences and orchestration logic
- **tool**: Database queries, API calls, retrieval operations
- **retriever**: Specialized vector database searches
- **embedding**: Embedding generation (auto-traced with wrapped clients)
- **agent**: High-level agent execution

### Metadata and Tags

```python
@traceable(
    name="Emma",
    run_type="chain",
    metadata={"thread_id": thread_id, "version": "v1"}
)
async def chat(question: str) -> str:
    pass

# Programmatic tags
@traceable
async def chat(question: str) -> str:
    tags = ["production", "customer-support"]
    if "urgent" in question.lower():
        tags.append("urgent")
    pass
```

### Trace Visualization Structure

```
chat (chain) - 2.3s
|-- ChatOpenAI (llm) - 0.8s
|   |-- Input: "Do you have printer paper?"
|   +-- Output: [tool_call: query_database]
|-- query_database (tool) - 0.1s
|   |-- Input: "SELECT * FROM products WHERE name LIKE '%paper%'"
|   +-- Output: [("Premium Copy Paper", 450, 24.99), ...]
+-- ChatOpenAI (llm) - 1.2s
    |-- Input: [previous messages + tool result]
    +-- Output: "Yes, we have several printer paper options..."
```

---

## 3. AGENT PATTERNS

### Basic Agent with Tool Calling

```python
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable

client = wrap_openai(OpenAI())

@traceable(run_type="tool")
def weather_retriever():
    """Retrieve current weather information."""
    return "It is sunny today"

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "weather_retriever",
        "description": "Get the current weather conditions",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

@traceable
def agent(question: str) -> dict:
    messages = [{"role": "user", "content": question}]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[WEATHER_TOOL],
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": response_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response_message.tool_calls
            ]
        })

        for tool_call in response_message.tool_calls:
            if tool_call.function.name == "weather_retriever":
                result = weather_retriever()
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "weather_retriever",
                    "content": result
                })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=[WEATHER_TOOL],
            tool_choice="auto"
        )
        response_message = response.choices[0].message

    messages.append({"role": "assistant", "content": response_message.content})
    return {"messages": messages, "output": response_message.content}
```

### Async Agent with Agentic Loop (Multiple Tools)

```python
import asyncio
import json
from openai import AsyncOpenAI
from langsmith import traceable, uuid7
from langsmith.wrappers import wrap_openai

client = wrap_openai(AsyncOpenAI())
thread_id = str(uuid7())
thread_store: dict[str, list] = {}

@traceable(name="Agent", metadata={"thread_id": thread_id})
async def chat(question: str) -> dict:
    tools = [QUERY_DATABASE_TOOL, SEARCH_KNOWLEDGE_BASE_TOOL]

    history_messages = thread_store.get(thread_id, [])
    messages = [
        {"role": "system", "content": system_prompt}
    ] + history_messages + [
        {"role": "user", "content": question}
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    # Agentic loop - keeps calling tools until no more tool_calls
    while response_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": response_message.content or "",
            "tool_calls": [
                {"id": tc.id, "type": tc.type,
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in response_message.tool_calls
            ]
        })

        for tool_call in response_message.tool_calls:
            function_args = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "query_database":
                result = query_database(**function_args)
            elif tool_call.function.name == "search_knowledge_base":
                result = await search_knowledge_base(**function_args)
            else:
                result = f"Error: Unknown tool {tool_call.function.name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result
            })

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message

    final_content = response_message.content
    messages.append({"role": "assistant", "content": final_content})
    thread_store[thread_id] = messages[1:]  # Save without system prompt

    return {"messages": messages, "output": final_content}
```

### Conversational Agent with Thread History

```python
from openai import OpenAI
from langsmith import traceable, uuid7
from langsmith.wrappers import wrap_openai

client = wrap_openai(OpenAI())
THREAD_ID = str(uuid7())
thread_store: dict[str, list] = {}

def get_thread_history(thread_id: str) -> list:
    return thread_store.get(thread_id, [])

def save_thread_history(thread_id: str, messages: list):
    thread_store[thread_id] = messages

@traceable(name="Name Agent", metadata={"thread_id": THREAD_ID})
def chat_pipeline(messages: list):
    history_messages = get_thread_history(THREAD_ID)
    all_messages = history_messages + messages

    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=all_messages
    )

    response_message = chat_completion.choices[0].message
    full_conversation = all_messages + [
        {"role": response_message.role, "content": response_message.content}
    ]
    save_thread_history(THREAD_ID, full_conversation)

    return {"messages": full_conversation}
```

---

## 4. DATASETS

### Why Datasets Matter

- Track performance across agent versions
- Catch regressions before deploying changes
- Benchmark systematically against production scenarios
- Share evaluation criteria with your team

Recommendation: Start with 10-25 examples covering core use cases.

### Dataset Structure

Each test case contains:
- **Input**: User question/prompt
- **Expected Output** (optional): Reference answer
- **Metadata** (optional): Tags, difficulty, type

### Creation Methods

**Method 1: UI Upload**
Navigate to Datasets > New Dataset > Upload CSV > Map columns

**Method 2: Programmatic Creation**

```python
from langsmith import Client

client = Client()

dataset = client.create_dataset(
    dataset_name="officeflow-dataset",
    description="Customer support evaluation dataset"
)

client.create_example(
    dataset_id=dataset.id,
    inputs={"question": "Do you have printer paper in stock?"},
    outputs={
        "expected_tool": "query_database",
        "reference_answer": "Should check database and provide current inventory"
    }
)
```

**Method 3: Production Trace Import**
Filter production runs by feedback criteria, populate datasets from real interactions using `list_runs()`.

### Coverage Categories

- inventory_queries (product availability, pricing)
- policy_questions (shipping, returns, ordering)
- frustrated_customers (escalation handling)
- multi_part_requests (complex workflows)
- edge_cases (ambiguous, out-of-scope)

---

## 5. RUNNING EXPERIMENTS

### Anatomy of an Experiment

1. **Target**: The agent/function being evaluated
2. **Dataset**: Test cases with inputs and optional expected outputs
3. **Evaluators**: Functions that score agent outputs

### Basic Experiment (Sync)

```python
from langsmith import evaluate

def dummy_app(inputs: dict) -> dict:
    return {"response": "Sure! In OfficeFlow, you can reset your password..."}

def mentions_officeflow(outputs: dict) -> bool:
    return "officeflow" in outputs["response"].lower()

results = evaluate(
    dummy_app,
    data="officeflow-dataset",
    evaluators=[mentions_officeflow],
    experiment_prefix="basic-test"
)
```

### Async Experiment with aevaluate

```python
import asyncio
from langsmith import aevaluate, uuid7

async def chat_wrapper(inputs: dict) -> dict:
    question = inputs.get("question", "")
    result = await chat(question)
    return {"answer": result["output"], "messages": result["messages"]}

async def main():
    await load_knowledge_base(kb_dir="./knowledge_base")

    results = await aevaluate(
        chat_wrapper,
        data="officeflow-dataset",
        experiment_prefix="agent-v5",
        max_concurrency=5,  # Parallel execution
    )

    print(f"Evaluation complete! Results: {results}")

asyncio.run(main())
```

### Running Agent with Test Isolation

```python
from langsmith import evaluate, uuid7
import agent_v5
from agent_v5 import chat, load_knowledge_base

async def setup():
    await load_knowledge_base(kb_dir)

def run_agent(inputs: dict) -> dict:
    # Fresh thread_id per evaluation for test isolation
    agent_v5.thread_id = str(uuid7())
    return asyncio.run(chat(inputs["question"]))

results = evaluate(
    run_agent,
    data="officeflow-dataset",
    evaluators=[schema_before_query],
    experiment_prefix="schema-check-v5",
)
```

### ExperimentResults Object

- `experiment_name` - Name of the experiment
- `dataset_name` - Dataset used
- `experiment_url` - Link to LangSmith UI
- Individual results with inputs, outputs, evaluation scores

### Key Parameters for evaluate/aevaluate

- `data` - Dataset name or ID
- `evaluators` - List of evaluator functions
- `experiment_prefix` - Creates names like "prefix-{timestamp}"
- `max_concurrency` - Parallel execution (aevaluate only)

### Running Evals with Pytest

LangSmith integrates directly with pytest:
- Familiar workflow: write evals as test functions, run with pytest, integrate into CI/CD
- Granular control: each test case can have its own custom evaluation logic
- Results are logged to LangSmith automatically

### LangSmith Framework Integrations

LangSmith supports auto-tracing for:
- LangChain, LangGraph and Deep Agents
- Claude Agent SDK
- OpenAI Agent SDK
- Vercel AI SDK
- Claude Code
- OpenTelemetry (OTel) as receiver and exporter

### Manual Tracing Wrappers (Multiple Providers)

```python
# OpenAI
from langsmith.wrappers import wrap_openai
wrapped_client = wrap_openai(OpenAI())

# Anthropic
from langsmith.wrappers import wrap_anthropic
wrapped_client = wrap_anthropic(Anthropic())

# Gemini
from langsmith.wrappers import wrap_gemini
wrapped_client = wrap_gemini(genai.Client())
```

---

## 6. CODE-BASED EVALUATORS

### Use Cases

- Tool invocation patterns verification
- Response schema conformance
- Keyword presence detection
- Sequential workflow validation
- Deterministic, objective checks

### Evaluator Signatures

**1. Outputs-only (simplest)**

```python
def mentions_officeflow(outputs: dict) -> bool:
    return "officeflow" in outputs["response"].lower()
```

**2. Inputs + Outputs**

```python
def response_length_score(outputs: dict) -> dict:
    response = outputs.get("response", "")
    length = len(response)

    if length < 100:
        score = 1.0
        comment = "Response is concise"
    elif length < 200:
        score = 0.7
        comment = "Response is moderately concise"
    else:
        score = 0.3
        comment = "Response is verbose"

    return {"score": score, "comment": comment, "metadata": {"length": length}}
```

**3. Run context (inspect full trace including tool calls)**

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
        return {"score": 1, "comment": "No query_database calls -- schema check not applicable"}

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

    return {"score": 1, "comment": "All query_database calls were schema inspections"}
```

**4. Safe evaluator pattern (handles both RunTree and dict)**

```python
def safe_evaluator(run, example) -> dict:
    try:
        outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {})
        if not outputs:
            return {"score": 0, "comment": "No outputs found"}
        response = outputs.get("response", "")
        if not response:
            return {"score": 0, "comment": "Empty response"}
        return {"score": 1, "comment": "Success"}
    except Exception as e:
        return {"score": 0, "comment": f"Evaluation error: {str(e)}"}
```

### Limitations

Cannot assess subjective qualities, semantic equivalence, tone, or nuanced reasoning.

---

## 7. LLM-AS-JUDGE EVALUATORS

### When to Use

Subjective, semantic, contextual, or nuanced criteria. Slower and more expensive than code-based.

### Correctness Evaluator (with reference)

```python
from openai import OpenAI

client = OpenAI()

CORRECTNESS_PROMPT = """You are evaluating an AI customer support agent's response.

User Question: {question}

Agent Response: {response}

Reference Context: {reference}

Is the agent's response correct and helpful? Consider:
- Does it answer the question accurately?
- Does it use appropriate tools if needed?
- Is the information factually correct?

Respond with a score from 0 to 1:
- 1.0: Completely correct and helpful
- 0.5: Partially correct but missing important details
- 0.0: Incorrect or unhelpful

Output only the numeric score."""

def evaluate_correctness(run, example) -> dict:
    question = example.inputs.get("question", "")
    response = run.outputs.get("answer", "")
    reference = example.outputs.get("reference_answer", "N/A")

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an evaluator. Respond with only a number."},
            {"role": "user", "content": CORRECTNESS_PROMPT.format(
                question=question,
                response=response,
                reference=reference
            )}
        ]
    )

    score = float(result.choices[0].message.content.strip())

    return {
        "score": score,
        "comment": f"LLM judge scored {score} for correctness"
    }
```

### Binary Classification (Helpfulness)

```python
from openai import OpenAI

client = OpenAI()

def is_helpful(inputs: dict, outputs: dict) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are evaluating customer service responses. Reply with only 'yes' or 'no'."},
            {"role": "user", "content": f"""Question: {inputs['question']}
Response: {outputs['answer']}

Is this response helpful? Answer yes or no."""}
        ]
    )

    verdict = response.choices[0].message.content.strip().lower()
    score = 1 if verdict == "yes" else 0

    return {
        "score": score,
        "comment": f"LLM judged response as {'helpful' if score else 'not helpful'}"
    }
```

### Multi-Criteria Evaluation

```python
import json
from openai import OpenAI

client = OpenAI()

def multi_criteria_eval(inputs: dict, outputs: dict) -> dict:
    prompt = f"""Evaluate this customer service response on these criteria (1-5 scale):

1. Helpfulness: Does it answer the question?
2. Accuracy: Is the information correct?
3. Conciseness: Is it brief and to the point?
4. Professionalism: Is the tone appropriate?

Question: {inputs['question']}
Response: {outputs['answer']}

Respond with JSON: {{"helpfulness": 1-5, "accuracy": 1-5, "conciseness": 1-5, "professionalism": 1-5, "explanation": "..."}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    scores = [result["helpfulness"], result["accuracy"], result["conciseness"], result["professionalism"]]
    overall_score = sum(scores) / len(scores) / 5

    return {
        "score": overall_score,
        "comment": result["explanation"],
        "metadata": result
    }
```

### Structured Output (with langchain-openai)

```python
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI

class Grade(TypedDict):
    reasoning: Annotated[str, ..., "Explain your reasoning"]
    is_accurate: Annotated[bool, ..., "True if response is accurate"]

judge = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Grade, method="json_schema", strict=True)

async def accuracy_evaluator(run, example):
    run_outputs = run.outputs if hasattr(run, "outputs") else run.get("outputs", {}) or {}
    example_outputs = example.outputs if hasattr(example, "outputs") else example.get("outputs", {}) or {}
    grade = await judge.ainvoke([{"role": "user", "content": f"Expected: {example_outputs}\nActual: {run_outputs}\nIs this accurate?"}])
    return {"score": 1 if grade["is_accurate"] else 0, "comment": grade["reasoning"]}
```

### Multi-Model Consensus

Using multiple LLMs (OpenAI + Anthropic) for higher confidence when both agree.

### Three Rules for Reliable LLM Judges (from PDF)

1. **Keep a narrow scope.** Most common mistake: asking the judge to evaluate too much at once. Focus on ONE specific criterion per judge. Not "Is this a good response?" but "Did the agent leak stock information?" or "Does the agent have a professional tone?"

2. **Binary classification or categorization only.** Rating helpfulness 1-5 creates nice graphs but what's the difference between 3.2 and 3.7? Make evals binary (yes/no) or categorical for actionable results.

3. **Align your judge with human reviewers.** Have human reviewers label a sample of the same outputs your judge is scoring, then compare verdicts. Where they disagree, refine the judge's prompt. This feedback loop turns a rough heuristic into a reliable evaluator.

### Best Practices

- Specific rubrics over vague instructions
- Calibrate on known test cases
- temperature=0 for reproducibility
- Structured JSON output
- Use more powerful models as judges (GPT-4 judging GPT-4-mini outputs)
- Narrow scope: one criterion per judge
- Binary/categorical over numeric scales
- Align with human reviewers iteratively

### Limitations

- Position bias, length bias, inconsistency
- Cost scales poorly
- Slower than code-based
- Without alignment, LLM judge inherits same biases as models it evaluates

---

## 8. PAIRWISE COMPARISON EVALUATORS

### Use Cases

- Determining which version is more concise, helpful, or accurate
- Relative assessment easier than absolute ratings
- A/B testing for production deployment

### Workflow

1. Run experiments on both versions against identical datasets
2. Build pairwise evaluator returning `[1, 0]`, `[0, 1]`, or `[0, 0]`
3. Execute comparison with `randomize_order=True`

### Complete Pairwise Evaluator

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
        messages=[
            {"role": "system", "content": "You are a conciseness evaluator. Respond with only a single number: 0, 1, or 2."},
            {"role": "user", "content": CONCISENESS_PROMPT.format(
                question=inputs["question"],
                response_a=outputs[0].get("answer", "N/A"),
                response_b=outputs[1].get("answer", "N/A"),
            )}
        ],
    )

    preference = int(response.choices[0].message.content.strip())

    if preference == 1:
        return [1, 0]
    elif preference == 2:
        return [0, 1]
    else:
        return [0, 0]
```

### Complete Pairwise Pipeline

```python
import asyncio
from langsmith import evaluate, aevaluate, uuid7

DATASET_NAME = "officeflow-dataset"

async def chat_wrapper_v4(inputs: dict) -> dict:
    agent_v4.thread_id = str(uuid7())
    result = await agent_v4.chat(inputs["question"])
    return {"answer": result["output"], "messages": result["messages"]}

async def chat_wrapper_v5(inputs: dict) -> dict:
    agent_v5.thread_id = str(uuid7())
    result = await agent_v5.chat(inputs["question"])
    return {"answer": result["output"], "messages": result["messages"]}

async def main():
    # Step 1: Run both agents
    v4_results = await aevaluate(
        chat_wrapper_v4,
        data=DATASET_NAME,
        experiment_prefix="agent-v4"
    )
    v5_results = await aevaluate(
        chat_wrapper_v5,
        data=DATASET_NAME,
        experiment_prefix="agent-v5"
    )

    # Step 2: Extract experiment names
    v4_experiment = v4_results.experiment_name
    v5_experiment = v5_results.experiment_name

    # Step 3: Run pairwise comparison
    evaluate(
        (v4_experiment, v5_experiment),
        evaluators=[conciseness_evaluator],
        randomize_order=True,  # CRITICAL: prevents position bias
    )

asyncio.run(main())
```

### CLI Usage for Pairwise

```python
import sys
from langsmith import evaluate

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python eval_conciseness_pairwise.py <experiment-a> <experiment-b>")
        sys.exit(1)

    evaluate(
        (sys.argv[1], sys.argv[2]),
        evaluators=[conciseness_evaluator],
        randomize_order=True,
    )
```

### Advanced Patterns

- **Simple Preference**: Binary win/loss/tie
- **Strength of Preference**: Normalized scores summing to 1
- **Multiple Criteria**: JSON responses across dimensions, overall winner by count
- **Statistical Significance**: Binomial test, alpha threshold 0.05

---

## 9. EVALUATOR SIGNATURES & RETURN FORMATS

### Signature Types

| Signature | Parameters | Use Case |
|---|---|---|
| `(outputs)` | Agent outputs only | Simple output checks |
| `(inputs, outputs)` | Dataset inputs + agent outputs | Input-aware evaluation |
| `(run, example)` | Full run context + dataset example | Trace inspection, tool call analysis |
| `(inputs, outputs: list)` | Pairwise comparison | A/B testing between experiments |

### Return Format Options

**Boolean (pass/fail)**
```python
def simple_check(outputs: dict) -> bool:
    return len(outputs["response"]) > 0
```

**Score Dictionary**
```python
def detailed_check(outputs: dict) -> dict:
    return {
        "score": 0.8,          # Required: numeric score
        "comment": "Good",     # Optional: explanation
        "metadata": {}         # Optional: extra data
    }
```

**Pairwise**
```python
def pairwise_check(inputs: dict, outputs: list[dict]) -> list[int]:
    return [1, 0]  # A wins, or [0, 1] B wins, or [0, 0] tie
```

### Local vs Uploaded Differences (Python)

| | Local `evaluate()` | Uploaded to LangSmith |
|---|---|---|
| **`run` type** | `RunTree` object -> `run.outputs` (attribute) | `dict` -> `run["outputs"]` (subscript) |
| **Handle both** | `run.outputs if hasattr(run, "outputs") else run.get("outputs", {})` | Same |
| **Column name** | Auto-derived from function name | Comes from evaluator name set at upload |
| **Return** | `{"score": value, "comment": "..."}` | `{"score": value, "comment": "..."}` |

### One Metric Per Evaluator Rule

Each evaluator returns ONE metric only. For multiple metrics, create multiple evaluator functions. Do NOT return `{"metric_name": value}` or lists of metrics.

---

## 10. ONLINE EVALUATION (PRODUCTION)

### Why Online Evaluation

- Distribution shift: user queries diverging from test data
- Edge cases: rare inputs not in test datasets
- Performance degradation: model updates, API changes
- Cost monitoring: token usage, latency

### Four Production Evaluator Functions

**1. check_answer_correctness** - LLM-as-judge comparing outputs against references

**2. check_helpfulness** - Rates 0-1 for helpful/actionable answers

**3. check_latency** - 3-second SLA threshold

```python
def check_latency(run) -> dict:
    latency_ms = (run.end_time - run.start_time).total_seconds() * 1000
    return {
        "score": 1.0 if latency_ms < 3000 else 0.0,
        "comment": f"Latency: {latency_ms:.0f}ms (SLA: 3000ms)"
    }
```

**4. check_policy_compliance** - Scans for prohibited terms

```python
def check_policy_compliance(run) -> dict:
    prohibited = ["confidential", "internal only", "not for distribution"]
    output = str(run.outputs)
    violations = [term for term in prohibited if term in output.lower()]
    if violations:
        return {"score": 0.0, "comment": f"Policy violation: {violations}"}
    return {"score": 1.0, "comment": "No policy violations"}
```

### Sampling Strategies

- Random: 10% rate
- Stratified by category: inventory 10%, policy 20%, out_of_scope 5%
- Always evaluate errors (100%)

### Production Thresholds

- correctness: 0.85
- helpfulness: 0.80
- latency_sla: 0.95
- policy_compliance: 0.99
- Borderline score range: 0.4-0.6 (flag for human review)

### Deployment Validation

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

---

## 11. TRACE UPLOAD AT SCALE

### Core Pattern

```python
from langsmith import Client, RunTree, uuid7
from datetime import datetime, timezone

client = Client()

def main():
    # Load traces from JSON
    with open("synthetic_traces.json") as f:
        traces = json.load(f)

    # Calculate time shift to present
    latest_ts = max(parse_dt(r["end_time"]) for t in traces for r in t["runs"])
    time_delta = datetime.now(timezone.utc) - latest_ts

    # Group traces and upload
    for trace in traces:
        id_map = {}

        # Regenerate IDs preserving relationships
        for run in trace["runs"]:
            old_id = run["id"]
            new_id = str(uuid7())
            id_map[old_id] = new_id

        # Build RunTree with parent-child hierarchy
        root_run = RunTree(
            name=root["name"],
            run_type=root["run_type"],
            inputs=root["inputs"],
            outputs=root["outputs"],
            start_time=shift_time(root["start_time"], time_delta),
            end_time=shift_time(root["end_time"], time_delta),
            id=id_map[root["id"]],
            project_name="prod-agent",
            client=client,
        )

        # Create children
        for child_data in children:
            child = root_run.create_child(
                name=child_data["name"],
                run_type=child_data["run_type"],
                inputs=child_data["inputs"],
                outputs=child_data["outputs"],
                start_time=shift_time(child_data["start_time"], time_delta),
                end_time=shift_time(child_data["end_time"], time_delta),
                id=id_map[child_data["id"]],
            )
            child.end()

        root_run.end()
        root_run.post(exclude_child_runs=False)

    # CRITICAL: Always flush before exit
    client.flush()
```

### Six Implementation Patterns

1. **Timestamp Shifting**: Offset to present time uniformly
2. **UUID7 ID Mapping**: Fresh IDs preserving temporal ordering
3. **Trace Grouping**: defaultdict by trace_id, root runs first
4. **Run Tree Construction**: Root with create_child() for dependents
5. **Reverse-Order Completion**: Children end() before parents
6. **Upload and Flushing**: post() with exclude_child_runs=False, then flush()

### Production Considerations

- **Rate Limiting**: Exponential backoff for HTTP 429 (wait = 2^attempt)
- **Batch Processing**: Chunks of 100, flush after each, 1s delays
- **Error Recovery**: Catch exceptions, log failures, write to disk
- **Parallel Upload**: ThreadPoolExecutor, max_workers=5

---

## 12. BEST PRACTICES & PITFALLS

### Best Practices

1. **Inspect Before Implement**: Run agent, inspect output, then write evaluators
2. **Match evaluator to dataset type**: Final Response -> LLM judge; Trajectory -> Custom Code
3. **Use async for LLM judges**: Enables parallel evaluation
4. **Test evaluators independently**: Validate on known good/bad examples
5. **Start small**: 10-20 dataset examples, basic evaluators first
6. **Test isolation**: Fresh thread_id per example (`uuid7()`)
7. **Reproducibility**: `temperature=0` and `seed` parameters
8. **Version datasets**: Update examples without breaking experiments
9. **Combine evaluators**: Code-based (fast) + LLM-judge (quality)
10. **Trace entry points**: Always trace main agent functions

### Common Pitfalls

- **Dataset Overfitting**: Maintain separate dev and validation datasets
- **Flaky Evaluators**: Run multiple times, check variance, temperature=0
- **Ignoring Latency**: Include performance evaluators
- **Binary Thinking**: Use multiple evaluators, document trade-offs
- **Evaluator Drift**: LLM evaluators drift with model updates; re-validate
- **Sampling Bias**: Risk of missing failures if only sampling successes
- **Alert Fatigue**: Start with high-severity metrics only
- **Field name mismatch**: Run function output must match dataset schema
- **RunTree vs dict**: Handle both with hasattr() pattern

### Agent Evolution Pattern

```
v0: Baseline (no tracing)
v1: + LangSmith tracing (@traceable, wrap_openai)
v2: + Enhanced tool instructions (schema discovery)
v3: + Business logic in prompts (stock information policy)
v4: + Improved RAG (whole documents, no chunking)
v5: + Conciseness improvements (prompt directive)
```

Key insight: Each improvement is measurable through evaluators.

---

## 13. COMPLETE CODE EXAMPLES

### Example 1: Full Evaluation Pipeline

```python
import asyncio
from langsmith import aevaluate, uuid7
from openai import OpenAI

# Import your agent
import agent_v5
from agent_v5 import chat, load_knowledge_base

# Setup
KB_DIR = "./officeflow-agent/knowledge_base"
DATASET = "officeflow-dataset"
judge_client = OpenAI()

# Evaluator 1: Code-based (schema check)
def schema_before_query(run, example) -> dict:
    tool_calls = _extract_tool_calls(run)
    db_calls = [tc for tc in tool_calls if tc["name"] == "query_database"]
    if not db_calls:
        return {"score": 1, "comment": "No DB calls"}
    # ... schema check logic ...

# Evaluator 2: LLM-as-Judge (correctness)
def evaluate_correctness(run, example) -> dict:
    question = example.inputs.get("question", "")
    response = run.outputs.get("answer", "")
    reference = example.outputs.get("reference_answer", "N/A")

    result = judge_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an evaluator. Respond with only a number 0-1."},
            {"role": "user", "content": f"Question: {question}\nResponse: {response}\nReference: {reference}\nScore (0-1):"}
        ]
    )
    score = float(result.choices[0].message.content.strip())
    return {"score": score, "comment": f"Correctness: {score}"}

# Run function with test isolation
async def chat_wrapper(inputs: dict) -> dict:
    agent_v5.thread_id = str(uuid7())
    result = await chat(inputs["question"])
    return {"answer": result["output"], "messages": result["messages"]}

# Execute
async def main():
    await load_knowledge_base(KB_DIR)
    results = await aevaluate(
        chat_wrapper,
        data=DATASET,
        evaluators=[schema_before_query, evaluate_correctness],
        experiment_prefix="full-eval-v5"
    )
    print(f"Results: {results.experiment_url}")

asyncio.run(main())
```

### Example 2: Full Pairwise Comparison

```python
import asyncio
from langsmith import evaluate, aevaluate, uuid7
from openai import OpenAI

import agent_v4
import agent_v5
from agent_v4 import chat as chat_v4, load_knowledge_base as load_kb_v4
from agent_v5 import chat as chat_v5, load_knowledge_base as load_kb_v5

DATASET = "officeflow-dataset"
client = OpenAI()

CONCISENESS_PROMPT = """..."""  # See section 8

def conciseness_evaluator(inputs: dict, outputs: list[dict]) -> list[int]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Respond with only: 0, 1, or 2."},
            {"role": "user", "content": CONCISENESS_PROMPT.format(
                question=inputs["question"],
                response_a=outputs[0].get("answer", "N/A"),
                response_b=outputs[1].get("answer", "N/A"),
            )}
        ],
    )
    preference = int(response.choices[0].message.content.strip())
    if preference == 1:
        return [1, 0]
    elif preference == 2:
        return [0, 1]
    return [0, 0]

async def main():
    await load_kb_v4("./officeflow-agent/knowledge_base")
    await load_kb_v5("./officeflow-agent/knowledge_base")

    async def wrapper_v4(inputs):
        agent_v4.thread_id = str(uuid7())
        r = await chat_v4(inputs["question"])
        return {"answer": r["output"], "messages": r["messages"]}

    async def wrapper_v5(inputs):
        agent_v5.thread_id = str(uuid7())
        r = await chat_v5(inputs["question"])
        return {"answer": r["output"], "messages": r["messages"]}

    v4_results = await aevaluate(wrapper_v4, data=DATASET, experiment_prefix="agent-v4")
    v5_results = await aevaluate(wrapper_v5, data=DATASET, experiment_prefix="agent-v5")

    evaluate(
        (v4_results.experiment_name, v5_results.experiment_name),
        evaluators=[conciseness_evaluator],
        randomize_order=True,
    )

asyncio.run(main())
```

### Example 3: Uploading Evaluators via CLI

```bash
# List all evaluators
langsmith evaluator list

# Upload offline evaluator (attached to dataset)
langsmith evaluator upload my_evaluators.py \
  --name "Schema Check" --function schema_before_query \
  --dataset "officeflow-dataset" --replace

# Upload online evaluator (attached to project)
langsmith evaluator upload my_evaluators.py \
  --name "Policy Compliance" --function check_policy_compliance \
  --project "Production Agent" --replace

# Delete
langsmith evaluator delete "Schema Check"
```

**Important notes for uploaded evaluators:**
- Run in sandboxed environment with limited packages
- Place all imports inside the function body
- Only use built-in/standard library imports
- Code evaluators only (no LLM-as-Judge via CLI)
- Uploaded to dataset = auto-run on experiments
- Uploaded to project = run on production traces

---

## SOURCE FILES REFERENCE

### Local Repository: ~/projects/jjat/learning/lca-reliable-agents/python/

```
python/
├── env_utils.py                              # Environment setup verification
├── officeflow-agent/
│   ├── agent_v0.py                           # Baseline (no tracing)
│   ├── agent_v1.py                           # + LangSmith tracing
│   ├── agent_v2.py                           # + Enhanced tool instructions
│   ├── agent_v3.py                           # + Stock information policy
│   ├── agent_v4.py                           # + No-chunking RAG
│   ├── agent_v5.py                           # + Conciseness improvements
│   ├── inventory/                            # SQLite product database
│   └── knowledge_base/
│       ├── documents/                        # 5 company policy .md files
│       ├── embeddings/                       # embeddings.json cache
│       └── generate_embeddings.py
├── module-1/lesson-2/
│   ├── thread_agent.py                       # Conversational agent
│   └── third_party_agent.py                  # Weather agent with tools
├── module-2/
│   ├── lesson-3/run_experiment.py            # Basic experiment runner
│   ├── lesson-4/
│   │   ├── eval_schema_check.py              # Code-based evaluator
│   │   └── run_eval.py                       # Run schema check eval
│   ├── lesson-5/run_experiment.py            # LLM-as-judge eval
│   └── lesson-6/
│       ├── run_agents.py                     # Run two agents for comparison
│       ├── eval_conciseness_pairwise.py      # Pairwise evaluator
│       └── run_pairwise_experiment.py        # Complete pairwise pipeline
└── module-3/lesson-2/
    ├── generate_traces.py                    # Generate 1000 synthetic traces
    └── upload_traces.py                      # Upload traces to LangSmith
```
