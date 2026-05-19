import pytest

from llm_cost_tracker.budget import BudgetAction, BudgetAlert, BudgetExceededError
from llm_cost_tracker.tracker import CostTracker


def test_budget_warn(capsys):
    alerts = []
    tracker = CostTracker()
    BudgetAlert(
        tracker=tracker,
        limit_usd=0.001,
        action=BudgetAction.WARN,
        on_alert=lambda limit, current: alerts.append((limit, current)),
    )

    tracker.record("openai", "gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000)
    assert len(alerts) == 1
    assert alerts[0][1] >= 0.001


def test_budget_block():
    tracker = CostTracker()
    BudgetAlert(tracker=tracker, limit_usd=0.001, action=BudgetAction.BLOCK)

    with pytest.raises(BudgetExceededError) as exc_info:
        tracker.record("openai", "gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000)

    assert exc_info.value.limit == 0.001
    assert exc_info.value.current >= 0.001


def test_remaining_and_percent():
    tracker = CostTracker()
    alert = BudgetAlert(tracker=tracker, limit_usd=10.0)

    assert alert.remaining == 10.0
    assert alert.percent_used == 0.0

    tracker.record("openai", "gpt-4o", input_tokens=1_000_000, output_tokens=0)
    assert alert.remaining < 10.0
    assert alert.percent_used > 0.0
