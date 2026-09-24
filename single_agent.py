import json

from llm import call_llm
from token_tracker import TokenTracker
from tools import (
    web_search,
    python_calculator,
)


SYSTEM_PROMPT = """
You are a general-purpose research and reasoning agent.

You have access to two tools:

1. web_search
   - Use this when you need current or external information.
   - Search only for information that is not already available
     in the conversation.
   - Keep searches focused and concise.

2. python_calculator
   - Use this whenever arithmetic calculations are required.
   - Use ONE mathematical expression per calculator call.
   - Do NOT use variables, assignments, print(), imports,
     or multiple Python statements.
   - Example:
     (100 + 50)
   - Example:
     (100 / 250) * 100

You decide:
- whether a tool is necessary
- which tool to use
- what arguments to give it
- whether to use a tool multiple times
- when you have enough information to answer

Do not perform complicated arithmetic mentally.
Use the calculator tool.

For factual information that may have changed over time,
use web search.

Avoid repeating searches for information that is already
available in previous tool results.

Keep tool usage efficient.

After gathering all required information, provide a clear
final answer to the user.
"""


# ============================================================
# TOOL SCHEMAS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "web_search",

            "description": (
                "Search the public web using a natural-language "
                "search query. Use this for current or external "
                "information. Do not provide URLs, IDs, cursors, "
                "or extra fields."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A concise natural-language search query."
                        ),
                    }
                },

                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "python_calculator",

            "description": (
                "Calculate ONE mathematical expression at a time. "
                "Do not use variables, assignments, print(), "
                "imports, or multiple expressions."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Exactly one arithmetic expression. "
                            "Example: (100 + 50) or "
                            "(100 / 250) * 100."
                        ),
                    }
                },

                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(name, arguments):

    if name == "web_search":

        query = arguments.get("query")

        if not isinstance(query, str) or not query.strip():
            return (
                "Tool error: web_search requires a non-empty "
                "string in the 'query' field."
            )

        return web_search(query)


    if name == "python_calculator":

        expression = arguments.get("expression")

        if not isinstance(expression, str) or not expression.strip():
            return (
                "Tool error: python_calculator requires a "
                "non-empty string in the 'expression' field."
            )

        return python_calculator(expression)


    return f"Unknown tool: {name}"


# ============================================================
# SINGLE AGENT
# ============================================================

def ask_llm(user_query, tracker):

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },

        {
            "role": "user",
            "content": user_query,
        },
    ]


    # Safety limit to prevent infinite tool loops
    max_iterations = 10


    for iteration in range(max_iterations):

        response = call_llm(
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            tracker=tracker,
        )

        message = response.choices[0].message


        # ----------------------------------------------------
        # No tool call = final answer
        # ----------------------------------------------------

        if not message.tool_calls:

            return message.content


        # ----------------------------------------------------
        # Add assistant tool-call message
        # ----------------------------------------------------

        messages.append(message)


        # ----------------------------------------------------
        # Execute requested tools
        # ----------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name


            # Safely parse arguments
            try:

                arguments = json.loads(
                    tool_call.function.arguments
                )

            except json.JSONDecodeError:

                arguments = {}


            print(
                f"\nSINGLE AGENT requested: "
                f"{tool_name}"
            )


            result = execute_tool(
                tool_name,
                arguments,
            )


            # Keep tool result as string
            if not isinstance(result, str):

                result = str(result)


            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )


    # --------------------------------------------------------
    # Maximum iterations reached
    # --------------------------------------------------------

    return (
        "The agent reached the maximum number of tool "
        "iterations before producing a final answer."
    )