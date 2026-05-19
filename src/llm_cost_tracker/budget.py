"""Budget alerts and limits for LLM spending."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from llm_cost_tracker.tracker import CostTracker, LLMCall


class BudgetAction(Enum):
    WARN = "warn"
    BLOCK = "block"


class BudgetExceededError(Exception):
    def __init__(self, limit: float, current: float) -> None:
        self.limit = limit
        self.current = current
        super().__init__(f"Budget exceeded: ${current:.4f} >= ${limit:.4f}")


@dataclass
class BudgetAlert:
    """Attach spending limits to a CostTracker."""

    tracker: CostTracker
    limit_usd: float
    action: BudgetAction = BudgetAction.WARN
    on_alert: Callable[[float, float], None] | None = None

    def __post_init__(self) -> None:
        self.tracker.on_record(self._check)

    def _check(self, call: LLMCall, tracker: CostTracker) -> None:
        total = tracker.total_cost
        if total >= self.limit_usd:
            if self.on_alert:
                self.on_alert(self.limit_usd, total)
            if self.action == BudgetAction.BLOCK:
                raise BudgetExceededError(self.limit_usd, total)

    @property
    def remaining(self) -> float:
        return max(0.0, self.limit_usd - self.tracker.total_cost)

    @property
    def percent_used(self) -> float:
        if self.limit_usd <= 0:
            return 100.0
        return min(100.0, (self.tracker.total_cost / self.limit_usd) * 100)
