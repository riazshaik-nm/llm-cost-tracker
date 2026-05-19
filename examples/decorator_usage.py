"""Using decorators to automatically track costs from LLM API responses."""

from llm_cost_tracker import CostTracker, track_cost
from llm_cost_tracker.reports.console import print_summary

tracker = CostTracker()


@track_cost("openai", "gpt-4o", tracker=tracker)
def summarize_text(text: str) -> tuple[int, int, str]:
    input_tokens = len(text.split()) * 2
    output_tokens = 150
    summary = f"Summary of {len(text)} chars of text."
    return (input_tokens, output_tokens, summary)


@track_cost("anthropic", "claude-sonnet-4", tracker=tracker)
def analyze_sentiment(text: str) -> tuple[int, int, dict]:
    input_tokens = len(text.split()) * 2
    output_tokens = 50
    result = {"sentiment": "positive", "confidence": 0.92}
    return (input_tokens, output_tokens, result)


article = "The new product launch exceeded expectations with record sales. " * 20

summary = summarize_text(article)
print(f"Summary: {summary}\n")

sentiment = analyze_sentiment(article)
print(f"Sentiment: {sentiment}\n")

print_summary(tracker)
