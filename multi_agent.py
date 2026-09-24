import json
import os

from dotenv import load_dotenv

from llm import call_llm
from token_tracker import TokenTracker
from tools import web_search, python_calculator


load_dotenv()


NOTES_FILE = "notes.txt"


# ============================================================
# MANAGER PROMPT
# ============================================================

MANAGER_SYSTEM_PROMPT = """
You are the manager of a multi-agent research system.

Your job is ONLY to decide what should happen next.

You have two helper agents:

1. SEARCH
   - Can search the web.
   - Use this when external/current information is required.

2. MATH
   - Can perform mathematical calculations.
   - Use this for arithmetic.

You do NOT have access to tools yourself.

You receive:
- the original user question
- notes containing results from previous helper agents

Your job is to decide the next action.

Return ONLY valid JSON.

Possible responses:

{
    "action": "search",
    "task": "exact task for the search agent"
}

or

{
    "action": "math",
    "task": "exact mathematical task for the math agent"
}

or

{
    "action": "finish",
    "answer": "final answer to the user"
}

Important:
- Do not calculate numbers yourself when the calculation
  should be handled by the math agent.
- Do not invent search results.
- Use the notes from previous agents.
- You may request the same helper multiple times.
- Continue requesting helpers until enough information
  exists to answer the original question.
"""


# ============================================================
# SEARCH AGENT
# ============================================================

SEARCH_SYSTEM_PROMPT = """
You are the search specialist in a multi-agent system.

Your ONLY capability is web search.

Your job is to:
1. Understand the research task given by the manager.
2. Search the web.
3. Extract relevant factual information.
4. Return a concise research report.

Do not perform complicated calculations.

If numerical information is found, report the numbers and
their sources accurately.

Always include the source URLs when possible.
"""


# ============================================================
# MATH AGENT
# ============================================================

MATH_SYSTEM_PROMPT = """
You are the mathematics specialist in a multi-agent system.

Your ONLY capability is the Python calculator tool.

Your job is to:
1. Understand the mathematical task.
2. Determine the required mathematical expression.
3. Use the calculator.
4. Return the calculation and result clearly.

Do not search the web.

Do not invent missing numerical values.

If required numbers are not present in the task, explain
that the manager must obtain them from the search specialist.
"""


# ============================================================
# NOTES
# ============================================================

def clear_notes():

    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        f.write("")


def read_notes():

    if not os.path.exists(NOTES_FILE):
        return ""

    with open(
        NOTES_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()


def add_note(agent, task, response):

    with open(
        NOTES_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("\n")
        f.write("=" * 70)
        f.write("\n")

        f.write(f"AGENT: {agent}\n")
        f.write(f"TASK: {task}\n")
        f.write("RESPONSE:\n")
        f.write(response)
        f.write("\n")


# ============================================================
# SEARCH AGENT
# ============================================================

SEARCH_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def ask_search_llm(task, tracker):

    messages = [
        {
            "role": "system",
            "content": SEARCH_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": task
        }
    ]

    while True:

        response = call_llm(
            messages=messages,
            tools=SEARCH_TOOL,
            tool_choice="auto",
            tracker=tracker
        )

        message = response.choices[0].message

        if not message.tool_calls:

            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:

            arguments = json.loads(
                tool_call.function.arguments
            )

            result = web_search(
                arguments["query"]
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            )


# ============================================================
# MATH AGENT
# ============================================================

MATH_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "python_calculator",
            "description": "Perform a mathematical calculation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def ask_maths_llm(task, tracker):

    messages = [
        {
            "role": "system",
            "content": MATH_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": task
        }
    ]

    while True:

        response = call_llm(
            messages=messages,
            tools=MATH_TOOL,
            tool_choice="auto",
            tracker=tracker
        )

        message = response.choices[0].message

        if not message.tool_calls:

            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:

            arguments = json.loads(
                tool_call.function.arguments
            )

            result = python_calculator(
                arguments["expression"]
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            )


# ============================================================
# MANAGER
# ============================================================

def ask_manager_llm(
    original_question,
    notes,
    tracker
):

    manager_prompt = f"""
Original user question:

{original_question}


Information collected so far:

{notes}


Decide the next action.
"""


    messages = [
        {
            "role": "system",
            "content": MANAGER_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": manager_prompt
        }
    ]

    response = call_llm(
        messages=messages,
        tracker=tracker
    )

    content = response.choices[0].message.content

    return json.loads(content)


# ============================================================
# MULTI AGENT ORCHESTRATOR
# ============================================================

def run_multi_agent(
    user_query,
    tracker
):

    clear_notes()

    while True:

        notes = read_notes()

        decision = ask_manager_llm(
            original_question=user_query,
            notes=notes,
            tracker=tracker
        )

        action = decision.get("action")

        print(
            f"\n MANAGER DECISION: {action}"
        )

        # ----------------------------------------------------
        # FINISH
        # ----------------------------------------------------

        if action == "finish":

            return decision["answer"]

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if action == "search":

            task = decision["task"]

            print(
                f"\n SEARCH AGENT TASK:\n{task}"
            )

            result = ask_search_llm(
                task,
                tracker
            )

            add_note(
                "SEARCH",
                task,
                result
            )

        # ----------------------------------------------------
        # MATH
        # ----------------------------------------------------

        elif action == "math":

            task = decision["task"]

            print(
                f"\n MATH AGENT TASK:\n{task}"
            )

            result = ask_maths_llm(
                task,
                tracker
            )

            add_note(
                "MATH",
                task,
                result
            )

        else:

            raise ValueError(
                f"Unknown manager action: {action}"
            )