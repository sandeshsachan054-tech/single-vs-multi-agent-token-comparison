from token_tracker import TokenTracker

from single_agent import ask_llm
from multi_agent import run_multi_agent


TEST_QUERY = """
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
"""


def print_usage(title, usage):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print(f"LLM calls:      {usage['calls']}")
    print(f"Input tokens:   {usage['input_tokens']}")
    print(f"Output tokens:  {usage['output_tokens']}")
    print(f"Total tokens:   {usage['total_tokens']}")


def main():

    # ========================================================
    # SINGLE AGENT
    # ========================================================

    print("\n")
    print("#" * 70)
    print("# SINGLE AGENT")
    print("#" * 70)

    single_tracker = TokenTracker()

    single_answer = ask_llm(
        TEST_QUERY,
        single_tracker
    )

    print("\n")
    print("SINGLE AGENT ANSWER")
    print("-" * 70)
    print(single_answer)

    single_usage = single_tracker.report()

    print_usage(
        "SINGLE AGENT TOKEN USAGE",
        single_usage
    )

    # ========================================================
    # MULTI AGENT
    # ========================================================

    print("\n")
    print("#" * 70)
    print("# MULTI AGENT")
    print("#" * 70)

    multi_tracker = TokenTracker()

    multi_answer = run_multi_agent(
        TEST_QUERY,
        multi_tracker
    )

    print("\n")
    print("MULTI AGENT ANSWER")
    print("-" * 70)
    print(multi_answer)

    multi_usage = multi_tracker.report()

    print_usage(
        "MULTI AGENT TOKEN USAGE",
        multi_usage
    )

    # ========================================================
    # COMPARISON
    # ========================================================

    print("\n")
    print("#" * 70)
    print("# COMPARISON")
    print("#" * 70)

    print(
        f"{'Metric':<20}"
        f"{'Single Agent':<20}"
        f"{'Multi Agent':<20}"
    )

    print("-" * 60)

    print(
        f"{'LLM calls':<20}"
        f"{single_usage['calls']:<20}"
        f"{multi_usage['calls']:<20}"
    )

    print(
        f"{'Input tokens':<20}"
        f"{single_usage['input_tokens']:<20}"
        f"{multi_usage['input_tokens']:<20}"
    )

    print(
        f"{'Output tokens':<20}"
        f"{single_usage['output_tokens']:<20}"
        f"{multi_usage['output_tokens']:<20}"
    )

    print(
        f"{'Total tokens':<20}"
        f"{single_usage['total_tokens']:<20}"
        f"{multi_usage['total_tokens']:<20}"
    )


if __name__ == "__main__":
    main()