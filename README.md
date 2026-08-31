# LangGraph Workflows

A hands-on implementation of 4 basic workflow patterns using LangGraph — Sequential, Parallel, Conditional, and Iterative/Loop. Each pattern has a simple (non-LLM) example and an LLM-based example, so you can first understand the structure, then see how it works in a real use case.

## Project Structure

```
langgraph-workflows/
│
├── 01-sequential_workflow/
│   ├── 01-state_based_workflow.py
│   ├── 02-llm_based_workflow.py
│   └── 03-prompt_chaining_workflow.py
│
├── 02-parallel_workflow/
│   ├── 01-simple_parallel_workflow.py
│   └── 02-llm_based_parallel_workflow.py
│
├── 03-conditional_workflow/
│   ├── 01-simple_conditional_workflow.py
│   └── 02-llm_based_conditional_workflow.py
│
├── 04-iterative_workflow/
│   ├── 01-simple_iterative_workflow.py
│   └── 02-llm_based_iterative_workflow.py
│
├── venv/
├── .env
├── .gitignore
└── requirements.txt
```

## Sequential Workflow

The simplest pattern. The task is split into a few steps, and each step runs one after another in a fixed order. No branching, just a straight line.

```
START → node_1 → node_2 → node_3 → END
```

- `state_based_workflow.py` — a basic example of how state moves from one node to another
- `llm_based_workflow.py` — calling the LLM at multiple steps in a fixed order
- `prompt_chaining_workflow.py` — using one step's output as the input for the next prompt

## Parallel Workflow

Here, a few nodes run at the same time, independent of each other, and then their results are merged. The problem is, if multiple nodes try to write to the state at once, it causes a conflict. So the state needs `Annotated` and a reducer (like `operator.add`), which tells LangGraph how to combine the values.

```
              ┌─→ node_A ─┐
START ───────┼─→ node_B ─┼───→ merge_node → END
              └─→ node_C ─┘
```

> A separate `merge_node` is optional — it's useful when you want to combine/format the results from all branches before ending. You can also skip it and have each branch (`node_A`, `node_B`, `node_C`) connect directly to `END`.

- `simple_parallel_workflow.py` — shows that parallel branching does not work without a reducer, a basic demo of this idea
- `llm_based_parallel_workflow.py` — running a few independent LLM calls on the same input at once (like getting sentiment and summary at the same time)

## Conditional Workflow

The state is checked at runtime, and a decision is made about which node to go to next. It works like an if-else, but for graphs. The main tool here is `add_conditional_edges()`.

```
                        ┌──→ node_A → END   (condition 1)
START → router_node ────┼──→ node_B → END   (condition 2)
                        └──→ node_C → END   (condition 3)
```

- `simple_conditional_workflow.py` — routing with plain if-else rules (approve/review/reject a loan based on salary)
- `llm_based_conditional_workflow.py` — the LLM classifies the input (like sentiment or issue type), then routes to a different path based on that

## Iterative / Loop Workflow

A node keeps repeating until a certain condition is met (like the quality is good, or the max retry limit is reached). If an edge from `add_conditional_edges()` goes back to an earlier node, that creates a loop.

```
START → generate_node → check_node
              ↑              │
              └──── retry ───┤
                              │
                          (approved)
                              ↓
                             END
```

- `simple_iterative_workflow.py` — a simple counter-based loop (like doubling a number until it reaches a target value)
- `llm_based_iterative_workflow.py` — a generate → check → retry cycle where the LLM creates content (like a LinkedIn post generator that keeps improving until it gets approved)

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Add your API keys in a `.env` file:

```
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
HUGGINGFACEHUB_API_TOKEN=your_key_here
```

## Run

```bash
python 01-sequential_workflow/01-state_based_workflow.py
```

Each file can be run on its own, none of them depend on each other.

## Core idea

The basic structure is the same for every pattern:

```
State → Node → Graph → Add Nodes → Edges → Compile → Execute
```

The real difference is how the Edges are set up — Sequential uses a straight edge, Parallel uses branching plus a reducer, Conditional uses a decision-based edge, and Iterative uses a backward edge.

## Requirements

- Python 3.10+
- langgraph
- langchain-groq / langchain-google-genai / langchain-huggingface
- python-dotenv
- pydantic
