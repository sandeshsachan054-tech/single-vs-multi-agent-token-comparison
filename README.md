# Single vs Multi-Agent LLM Token Comparison

A Python project that compares two LLM agent architectures on the same research-and-calculation task:

- **Single-Agent System** — one LLM decides when and how to use both tools.
- **Multi-Agent System** — a manager LLM delegates work to specialized Search and Math agents.

The project measures **LLM calls, input tokens, output tokens, and total tokens** for both approaches.

---

## Project Overview

The goal of this project is to understand the token and orchestration overhead introduced when a single general-purpose agent is replaced by a multi-agent architecture.

Both systems receive the **same user query** and use the same underlying Groq model and external tools.

### Tools

#### 1. Tavily Web Search

Used for:

- Current information
- External information
- Web research
- Finding reliable population data

#### 2. Python Calculator

Used for:

- Arithmetic calculations
- Percentages
- Population calculations
- Mathematical operations

The calculator is implemented using Python's `ast` module instead of executing arbitrary Python code.

---

## Architecture

### Single-Agent Architecture

The single agent has access to both tools and independently decides:

- Whether a tool is required
- Which tool to use
- What arguments to provide
- Whether to call a tool multiple times
- When enough information has been collected
- When to produce the final answer

```text
                    USER QUERY
                         |
                         v
                 +---------------+
                 |  SINGLE LLM   |
                 +---------------+
                   /           \
                  /             \
                 v               v
        +-------------+   +------------------+
        | Tavily Web  |   | Python Calculator|
        |   Search    |   |                  |
        +-------------+   +------------------+
                \             /
                 \           /
                  v         v
                 LLM continues
                       |
                       v
                  FINAL ANSWER
```                  

## Multi-Agent Architecture

The multi-agent system separates responsibilities into specialized agents.

Manager LLM

Responsible for:

Understanding the overall task
Deciding which specialist should work next
Giving the specialist a specific task
Reading previous notes
Deciding when the task is complete
Search LLM

Responsible only for:

Web research
Tavily searches
Finding external/current information
Math LLM

Responsible only for:

Mathematical calculations
Using the Python calculator
```text
                         USER QUERY
                              |
                              v
                     +----------------+
                     |  MANAGER LLM   |
                     +----------------+
                       /            \
                      /              \
             search task            math task
                  |                     |
                  v                     v
          +---------------+     +---------------+
          |  SEARCH LLM   |     |   MATH LLM    |
          +---------------+     +---------------+
                  |                     |
                  v                     v
            Tavily Search        Python Calculator
                  |                     |
                  +----------+----------+
                             |
                             v
                       +-----------+
                       |  NOTES    |
                       |   .txt    |
                       +-----------+
                             |
                             v
                       MANAGER LLM
                             |
                             v
                       FINAL ANSWER
```

## Test Query
Both architectures were tested using the same query:
```text
Find the latest available World Bank population data for India
and the United States.

Then:
1. Calculate their combined population.
2. Calculate what percentage of the combined population is India's.
3. Calculate the combined population if both countries'
   populations increased by 2.5%.
4. Calculate the difference between the original combined
   population and the increased combined population.

Use reliable web sources for the population figures and
show the calculations clearly.
```
Using the same query for both systems makes the comparison reproducible for this experiment.

## Token Usage Results
The following results were obtained from one completed run using the project's current configuration.
| Metric           | Single Agent | Multi Agent |
| ---------------- | -----------: | ----------: |
| LLM calls        |           10 |          23 |
| Input tokens     |       27,036 |      54,474 |
| Output tokens    |          739 |       2,224 |
| **Total tokens** |   **27,775** |  **56,698** |

Total Token Difference
```text
56,698 - 27,775 = 28,923 tokens
```
For this particular test run:
```text
56,698 / 27,775 ≈ 2.04x
```
Therefore, the multi-agent implementation used approximately 2.04× as many total tokens as the single-agent implementation for this specific experiment.

Note: This result is specific to the tested query, prompts, model configuration, tool outputs, and implementation. It should not be interpreted as a universal result for all workloads.

## Why Does the Multi-Agent System Use More Tokens?

# The multi-agent architecture introduces additional LLM interactions.

For example:
```bash
User
  ↓
Manager
  ↓
Search Agent
  ↓
Manager
  ↓
Search Agent
  ↓
Manager
  ↓
Math Agent
  ↓
Manager
  ↓
Final Answer
```

Every manager and specialist interaction can introduce additional input and output tokens.

# The single-agent system can instead maintain one agent loop:
```bash
User
  ↓
Single Agent
  ↓
Tool
  ↓
Single Agent
  ↓
Tool
  ↓
Final Answer
```
This experiment therefore demonstrates a measurable token/call overhead associated with the multi-agent orchestration used in this implementation.

## Project Structure
```bash
single-vs-multi-agent-token-comparison/
│
├── .env
├── .gitignore
├── requirements.txt
│
├── tools.py
├── llm.py
├── token_tracker.py
│
├── single_agent.py
├── multi_agent.py
│
├── main.py
├── notes.txt
│
└── README.md
```
## File Responsibilities

File	                              Purpose
main.py	                  Runs the experiment and prints the comparison
single_agent.py           Implements the single-agent architecture
multi_agent.py	          Implements the multi-agent architecture
tools.py	              Contains Tavily search and Python calculator
llm.py	                  Groq API wrapper
token_tracker.py	      Tracks LLM token usage
notes.txt	              Stores helper-agent responses
.env	                  Stores API keys and model configuration
requirements.txt	      Python dependencies

## Tech Stack

Python
Groq API
Tavily Search API
python-dotenv
Python Standard Library
No Agent Frameworks

This project intentionally does not use:

LangChain
LangGraph
CrewAI
AutoGen

The agent orchestration logic is implemented manually in Python.

##  Setup

1. Clone the Repository
```bash
git clone https://github.com/sandeshsachan054-tech/single-vs-multi-agent-token-comparison.git
cd single-vs-multi-agent-token-comparison
```

2. Create Virtual Environment
```bash
Windows PowerShell
python -m venv venv

.\venv\Scripts\Activate.ps1
macOS / Linux
python3 -m venv venv

source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Configure Environment Variables
Create a .env file:
```bash
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_MODEL=qwen/qwen3.8-27b
```
## Never commit .env to GitHub.

The .gitignore file should contain:
```bash
.env
venv/
__pycache__/
*.pyc
```
## Run the Project

Activate the virtual environment and run:
```bash
python main.py
```
The program will:

Run the single-agent system
Track its token usage
Run the multi-agent system
Track manager/search/math LLM usage
Compare both systems
Print the final token statistics

## Token Tracking

Every Groq LLM response is recorded by the token tracker.

The project tracks:

Number of LLM calls
Input tokens
Output tokens
Total tokens

This allows both architectures to be compared using the same workload.

## Design Goals

This project was intentionally built without an agent framework to understand the underlying mechanics of LLM agents.

It demonstrates:

LLM tool calling
Tool schemas
Tool execution loops
Agent delegation
Manager/specialist architecture
Shared state through notes
Token accounting
Multi-agent orchestration
Single-agent orchestration

## Experiment Notes

This is an implementation-level experiment rather than a universal benchmark.

Token usage can change depending on:

Model
Prompt design
Tool-result size
Number of search results
Search queries generated by the model
Number of manager/helper calls
Maximum completion-token settings
Complexity of the user query

A stronger benchmark can be created by running multiple queries and comparing average token usage.

## Future Improvements

Possible improvements include:

Run a larger benchmark set
Compare average token usage
Track latency
Track number of tool calls
Track Tavily API usage
Compare answer quality
Add token-usage charts
Add interactive user input
Store benchmark results in CSV/JSON
Compare additional agent architectures
Add automated evaluation of final answers
## Key Takeaway

For the specific workload tested in this project:

Single Agent
10 LLM calls
27,775 total tokens

Multi Agent
23 LLM calls
56,698 total tokens

The experiment shows how introducing a manager and specialized helper agents can increase LLM-call and token overhead.

The result is workload- and implementation-specific, so additional experiments are needed before generalizing the findings.

## Author

Built as a hands-on project to understand:

LLM Tool Calling • Single Agents • Multi-Agent Systems • Agent Orchestration • Token Usage

Implemented from scratch in Python without LangChain, LangGraph, CrewAI, or AutoGen.


### GitHub ke liye ek chhota description bhi rakhna:

> **A Python project comparing single-agent and multi-agent LLM architectures using Groq, Tavily web search, a Python calculator, and token usage tracking.**

Aur repo ka naam jo humne choose kiya tha:

```text
single-vs-multi-agent-token-comparison
```
Ye README current actual result (10 vs 23 calls, 27,775 vs 56,698 tokens) ke according hai, isliye GitHub par project ka purpose aur experiment dono clearly explain honge.
