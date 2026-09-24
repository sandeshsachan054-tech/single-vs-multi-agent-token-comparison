import os

from dotenv import load_dotenv
from groq import Groq

from token_tracker import TokenTracker


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "qwen/qwen3.8-27b"
)


def call_llm(messages, tools=None, tool_choice="auto", tracker=None):
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "max_completion_tokens": 512,
        "reasoning_effort": "none",
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice
        kwargs["parallel_tool_calls"] = False

    response = client.chat.completions.create(**kwargs)

    if tracker:
        tracker.record(response)

    return response