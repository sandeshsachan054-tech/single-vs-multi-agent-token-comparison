import ast
import operator
import os

from dotenv import load_dotenv
from tavily import TavilyClient


# Load .env
load_dotenv()


# ============================================================
# TAVILY CLIENT
# ============================================================

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# ============================================================
# WEB SEARCH
# ============================================================
def web_search(query: str) -> str:
    print("\nSEARCH TOOL")
    print(f"Query: {query}")

    try:
        response = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=2
        )

        results = response.get("results", [])

        if not results:
            return "No search results found."

        formatted = []

        for result in results:
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")[:500]

            formatted.append(
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}"
            )

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Search error: {e}"

# ============================================================
# PYTHON CALCULATOR
# ============================================================

import ast
import operator


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _calculate_node(node):

    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):

        left = _calculate_node(node.left)
        right = _calculate_node(node.right)

        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError("Operator not allowed.")

        return _ALLOWED_OPERATORS[operator_type](
            left,
            right
        )

    if isinstance(node, ast.UnaryOp):

        operand = _calculate_node(node.operand)

        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError("Operator not allowed.")

        return _ALLOWED_OPERATORS[operator_type](
            operand
        )

    raise ValueError(
        "Invalid mathematical expression."
    )


def python_calculator(expression: str) -> str:

    print("\nCALCULATOR TOOL")
    print(f"Expression: {expression}")

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = _calculate_node(
            tree.body
        )

        return str(result)

    except Exception as e:

        return f"Calculator error: {e}"


# ============================================================
# CALCULATOR TOOL SCHEMA
# ============================================================

CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "python_calculator",
        "description": (
            "Calculate ONE mathematical expression at a time. "
            "Do NOT use variables, assignments, Python statements, "
            "print(), imports, or multiple expressions. "
            "Example valid input: '(1450935791 + 340110988)'. "
            "Example valid input: '(1450935791 / (1450935791 + 340110988)) * 100'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "Exactly one arithmetic expression using numbers, "
                        "+, -, *, /, %, **, and parentheses."
                    )
                }
            },
            "required": ["expression"],
            "additionalProperties": False
        }
    }
}