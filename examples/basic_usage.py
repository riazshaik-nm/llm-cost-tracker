"""Basic usage of llm-cost-tracker."""

from llm_cost_tracker import CostTracker
from llm_cost_tracker.reports.console import print_summary, print_breakdown, print_call_log
from llm_cost_tracker.storage.json_store import save_json

tracker = CostTracker()

tracker.record("openai", "gpt-4o", input_tokens=2500, output_tokens=800, latency_ms=1200)
tracker.record("openai", "gpt-4o-mini", input_tokens=5000, output_tokens=1500, latency_ms=400)
tracker.record("anthropic", "claude-sonnet-4", input_tokens=3000, output_tokens=1200, latency_ms=900)
tracker.record("anthropic", "claude-haiku-3.5", input_tokens=8000, output_tokens=2000, latency_ms=300)
tracker.record("openai", "gpt-4o", input_tokens=1500, output_tokens=600, latency_ms=800)

print_summary(tracker)
print()
print_breakdown(tracker)
print()
print_call_log(tracker)

save_json(tracker, "cost_report.json")
print("\nSaved to cost_report.json")
