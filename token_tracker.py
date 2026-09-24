from dataclasses import dataclass


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    calls: int = 0


class TokenTracker:

    def __init__(self):
        self.usage = TokenUsage()

    def record(self, response):

        usage = response.usage

        input_tokens = getattr(
            usage,
            "prompt_tokens",
            0
        )

        output_tokens = getattr(
            usage,
            "completion_tokens",
            0
        )

        total_tokens = getattr(
            usage,
            "total_tokens",
            input_tokens + output_tokens
        )

        self.usage.input_tokens += input_tokens
        self.usage.output_tokens += output_tokens
        self.usage.total_tokens += total_tokens
        self.usage.calls += 1

    def reset(self):
        self.usage = TokenUsage()

    def report(self):

        return {
            "calls": self.usage.calls,
            "input_tokens": self.usage.input_tokens,
            "output_tokens": self.usage.output_tokens,
            "total_tokens": self.usage.total_tokens,
        }