---
name: jjat-langsmith-tracing
description: "INVOKE THIS SKILL when setting up LangSmith tracing, adding observability to AI agents, debugging agent behavior with traces, using @traceable or wrap_openai/wrap_anthropic/wrap_gemini, grouping traces into conversation threads, or querying traces with the LangSmith CLI. Use this skill whenever the user mentions LangSmith tracing, agent observability, trace debugging, run types, or wants to instrument any Python/TypeScript application with LangSmith — even if they don't use the word 'tracing' explicitly."
---

# LangSmith Tracing & Observability

Tracing is the foundation of the Agent Engineering Lifecycle. Without it, you can't see what your agent actually did — which tools it called, how it reasoned, or where it went wrong. This skill covers everything from instrumenting your first agent to debugging production traces at scale.

## Where tracing fits in the lifecycle

```
Build → **Observe** → Offline Evals → Production
         ^^^^^^^^
         You are here
```

Tracing is Stage 2: you run your agent, observe what happens in traces, and debug what breaks. The failure modes you discover here become the basis for automated evaluations later.

<setup>

## Environment Setup

```bash
# Required — set in .env or export
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=your-project-name

# Optional
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com   # EU users only
```

Load them in your application:

```python
from dotenv import load_dotenv
load_dotenv()
```

**Dependencies:**
```bash
pip install langsmith openai python-dotenv
```

**CLI (for querying traces):**
```bash
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh
```

Check `LANGSMITH_PROJECT` in the user's `.env` file before querying — this tells you which project contains their traces.
</setup>

<framework_integrations>

## Framework Integrations (Auto-Tracing)

If the agent uses one of these frameworks, tracing is automatic — just set environment variables:

- **LangChain / LangGraph / Deep Agents** — set `LANGSMITH_TRACING=true`
- **Claude Agent SDK** — native LangSmith support
- **OpenAI Agent SDK** — native LangSmith support
- **Vercel AI SDK** — native LangSmith support
- **Claude Code** — native LangSmith support
- **OpenTelemetry** — LangSmith can receive and export OTel traces

For LangChain/LangGraph, that's all you need — every LLM call, tool invocation, and chain step is captured automatically.

For everything else, or if you're building without a framework, use manual tracing below.
</framework_integrations>

<manual_tracing>

## Manual Tracing: Three Steps

When your app doesn't use a framework with built-in integration, add tracing manually. It takes three changes to your code.

### Step 1: Wrap Your LLM Client

Wrapping captures every LLM call automatically — prompts, completions, token counts, and timing.

```python
# OpenAI
from openai import OpenAI  # or AsyncOpenAI
from langsmith.wrappers import wrap_openai
client = wrap_openai(OpenAI())

# Anthropic
from anthropic import Anthropic
from langsmith.wrappers import wrap_anthropic
client = wrap_anthropic(Anthropic())

# Google Gemini
from google import genai
from langsmith.wrappers import wrap_gemini
client = wrap_gemini(genai.Client())
```

### Step 2: Decorate Key Functions with @traceable

Apply `@traceable` to your agent pipeline and tool functions. This creates the parent-child hierarchy visible in the LangSmith UI.

```python
from langsmith import traceable

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
        model="text-embedding-3-small", input=query
    )
    query_embedding = response.data[0].embedding
    # ... cosine similarity logic ...
    return "\n".join(results)

@traceable(name="Emma", metadata={"thread_id": thread_id})
async def chat(question: str) -> dict:
    """Process a user question and return assistant response."""
    # ... agent logic with tool calling loop ...
    return {"messages": messages, "output": final_content}
```

Return the full message list from your agent (not just the final answer). This ensures all tool calls, intermediate steps, and the complete conversation flow are visible in your trace output — which is critical for debugging and evaluation later.

### Step 3: Group Traces into Threads

A thread links multiple traces into a single conversation. Each user message creates its own trace, but they're grouped by a shared identifier.

Pass one of these metadata keys: `session_id`, `thread_id`, or `conversation_id`:

```python
from langsmith import traceable, uuid7

thread_id = str(uuid7())

@traceable(name="Emma", metadata={"thread_id": thread_id})
async def chat(question: str) -> dict:
    # Each call creates a separate trace, all linked by thread_id
    ...
```
</manual_tracing>

<run_types>

## Run Types

The `run_type` parameter on `@traceable` categorizes your function in the LangSmith UI. Use the right type so traces are easy to navigate and filter.

| Run Type | When to Use | Example |
|---|---|---|
| `llm` | Direct LLM calls | Auto-set by `wrap_openai()` — you rarely set this manually |
| `chain` | Orchestration logic, pipelines | Your main agent function, RAG pipeline |
| `tool` | External actions the agent invokes | Database queries, API calls, file operations |
| `retriever` | Vector/semantic search | Knowledge base lookups, document retrieval |
| `embedding` | Embedding generation | Auto-set by wrapped clients for `.embeddings.create()` |
| `agent` | Top-level agent execution | High-level agent entry point |

If you're unsure, `tool` is the right default for functions your agent calls, and leave the main pipeline without a `run_type` (defaults to `chain`).
</run_types>

<metadata_tags>

## Metadata and Tags

Metadata and tags make traces searchable and filterable in the LangSmith UI and CLI.

**Metadata** — key-value pairs attached at decoration time or runtime:

```python
@traceable(
    name="Emma",
    run_type="chain",
    metadata={"thread_id": thread_id, "version": "v2", "environment": "staging"}
)
async def chat(question: str) -> dict:
    ...
```

**Tags** — labels for categorization, added programmatically:

```python
@traceable
async def chat(question: str) -> str:
    tags = ["production", "customer-support"]
    if "urgent" in question.lower():
        tags.append("urgent")
    ...
```

Use metadata for structured data you'll filter on (version, user_id, environment). Use tags for categorical labels (urgent, needs-review).
</metadata_tags>

<stateful_conversations>

## Stateful Conversations

To build a conversational agent that remembers past interactions, you need: (1) a thread store that persists messages, and (2) a thread ID that links traces together.

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

@traceable(name="Agent", metadata={"thread_id": THREAD_ID})
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

In production, replace the in-memory dict with a database. The pattern stays the same.
</stateful_conversations>

<trace_visualization>

## What a Trace Looks Like

A trace is a tree of runs. The root is your agent, and children are LLM calls, tool invocations, and nested operations:

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

Each node shows inputs, outputs, timing, and token usage. You can expand/collapse nodes, inspect I/O at each step, share trace URLs, and filter by metadata or tags.
</trace_visualization>

<debugging>

## Debugging with Traces

LangSmith provides three debugging workflows, each useful in different situations.

### 1. Tracing UI (Most Common)

Open a trace in the LangSmith web UI and walk through the execution tree step by step.

**What to look for:**
- Did the agent call the right tool?
- Were the tool arguments correct?
- Did the agent use the tool's output in its final response?
- How long did each step take?
- Were there errors at any point?

**Common failure patterns to track:**
- Agent didn't use tools correctly (wrong tool, wrong arguments)
- Agent revealed sensitive information
- Agent took too many steps (inefficient)
- Agent ignored tool results in its final response
- Agent struggled with specific query types

### 2. Playground & Polly (Iterative Debugging)

When your agent fails on step 30 of a long run, re-running the whole thing is painful. The Playground lets you freeze the first 29 steps and iteratively debug just the failing step.

Open any trace in LangSmith, click "Open in Playground", modify the prompt or inputs, and re-run just that step. This is the fastest way to iterate on prompt engineering.

### 3. CLI & Coding Agents (Programmatic)

Query trace data from the terminal for automated analysis or to feed into a coding agent:

```bash
# Install CLI
curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh

# View all commands
langsmith --help
```

This is powerful when you want an AI coding agent to help debug — it can pull trace data, analyze patterns, and suggest fixes.
</debugging>

<cli_reference>

## CLI Reference

### Traces vs Runs

Understanding this distinction is critical:

- **Trace** = complete execution tree (root run + all children). One full agent invocation.
- **Run** = single node in the tree (one LLM call, one tool call, etc.)

Start with traces — they provide the full context and hierarchy.

### Command Structure

```
langsmith
├── trace
│   ├── list    - List traces (filters on root run)
│   ├── get     - Get single trace with full hierarchy
│   └── export  - Export traces to JSONL (one file per trace)
│
├── run
│   ├── list    - List individual runs (flat, any run)
│   ├── get     - Get single run
│   └── export  - Export runs to single JSONL file
│
├── thread
│   ├── list    - List conversation threads
│   └── get     - Get thread details
│
└── project
    └── list    - List tracing projects
```

| | `trace *` | `run *` |
|---|---|---|
| Filters apply to | Root run only | Any matching run |
| `--run-type` filter | Not available | Available |
| Returns | Full hierarchy | Flat list |
| Export output | Directory (one file/trace) | Single file |

### Common Queries

```bash
# List recent traces
langsmith trace list --limit 10 --project my-project

# With timing, tokens, and cost metadata
langsmith trace list --limit 10 --include-metadata

# Filter by time
langsmith trace list --last-n-minutes 60
langsmith trace list --since 2025-01-20T10:00:00Z

# Get a specific trace with full hierarchy
langsmith trace get <trace-id>

# Show trace trees inline
langsmith trace list --limit 5 --show-hierarchy

# Export traces (includes all runs)
langsmith trace export ./traces --limit 20 --full

# Find slow traces
langsmith trace list --min-latency 5.0 --limit 10

# Find failed traces
langsmith trace list --error --last-n-minutes 60

# List specific run types (flat)
langsmith run list --run-type llm --limit 20
```

### All Filters

All filters are AND-ed together:

**Basic:** `--trace-ids abc,def` | `--limit N` | `--project NAME` | `--last-n-minutes N` | `--since TIMESTAMP` | `--error / --no-error` | `--name PATTERN`

**Performance:** `--min-latency SECONDS` | `--max-latency SECONDS` | `--min-tokens N` | `--tags tag1,tag2`

**Advanced:** `--filter QUERY` for raw LangSmith filter queries:

```bash
langsmith trace list --filter 'and(eq(feedback_key, "correctness"), gte(feedback_score, 0.8))'
```

### Export Format

JSONL files with one run per line:
```json
{"run_id": "...", "trace_id": "...", "name": "...", "run_type": "...", "parent_run_id": "...", "inputs": {...}, "outputs": {...}}
```

Use `--full` to include inputs/outputs (required for dataset generation).
</cli_reference>

<best_practices>

## Best Practices

1. **Trace entry points first.** Always decorate your main agent function — this creates the root node that everything else nests under.

2. **Trace every tool.** Every function your agent can call should have `@traceable(run_type="tool")`. Without this, you'll have blind spots when debugging.

3. **Use descriptive names.** Name traces by purpose (`query_database`, `search_knowledge_base`) not by structure (`function_1`, `step_2`).

4. **Return the full message list.** Return `{"messages": messages, "output": final_content}` from your agent — not just the final string. This preserves tool calls and intermediate reasoning in the trace, which is essential for trajectory evaluation.

5. **Add metadata for filtering.** Include `version`, `thread_id`, and `environment` at minimum. This lets you compare agent versions and debug specific conversations.

6. **Use `uuid7()` for thread IDs.** LangSmith's `uuid7()` preserves temporal ordering, making it easy to sort and query threads chronologically.

7. **Check your project name.** Always verify `LANGSMITH_PROJECT` before querying — it's the most common reason for "missing traces".
</best_practices>

<troubleshooting>

## Troubleshooting

**Traces not appearing in LangSmith:**
- Verify `LANGSMITH_TRACING=true` is set (not `LANGCHAIN_TRACING_V2`)
- Confirm `LANGSMITH_API_KEY` is valid
- Check `LANGSMITH_PROJECT` matches the project you're looking at
- Ensure `wrap_openai()` or `@traceable` is applied
- Check network access to LangSmith API

**Traces appear but are incomplete:**
- Make sure `@traceable` is on all tool functions, not just the main pipeline
- Verify you're returning complete outputs (not just the final string)

**Reducing trace verbosity:**
Only decorate functions you need visibility into. Internal helpers that don't interact with the LLM or tools can be left undecorated.

**For serverless environments (AWS Lambda, etc.):**
Set `LANGCHAIN_CALLBACKS_BACKGROUND=false` to ensure traces flush before the function exits.
</troubleshooting>
