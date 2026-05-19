"""Budget alerts example — get warned or blocked when spending exceeds a limit."""

from llm_cost_tracker import CostTracker, BudgetAlert, BudgetExceededError
from llm_cost_tracker.budget import BudgetAction


def on_budget_warning(limit: float, current: float) -> None:
    print(f"WARNING: Spending ${current:.4f} has exceeded budget of ${limit:.4f}")


tracker = CostTracker()

alert = BudgetAlert(
    tracker=tracker,
    limit_usd=0.05,
    action=BudgetAction.WARN,
    on_alert=on_budget_warning,
)

tracker.record("openai", "gpt-4o", input_tokens=5000, output_tokens=2000, latency_ms=500)
print(f"Budget remaining: ${alert.remaining:.4f} ({alert.percent_used:.1f}% used)")

tracker.record("openai", "gpt-4o", input_tokens=50000, output_tokens=20000, latency_ms=1500)
print(f"Budget remaining: ${alert.remaining:.4f} ({alert.percent_used:.1f}% used)")


# --- Blocking mode ---
print("\n--- Blocking mode ---")
tracker2 = CostTracker()
BudgetAlert(tracker=tracker2, limit_usd=0.01, action=BudgetAction.BLOCK)

try:
    tracker2.record("openai", "gpt-4o", input_tokens=100000, output_tokens=50000)
except BudgetExceededError as e:
    print(f"Blocked: {e}")
