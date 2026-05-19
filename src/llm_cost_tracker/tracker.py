from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from llm_cost_tracker.providers.registry import get_cost


@dataclass(frozen=True)
class LLMCall:
    """Record of a single LLM API call with cost metadata."""

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class CostTracker:
    """Thread-safe tracker that accumulates LLM call costs."""

    def __init__(self, budget: float | None = None) -> None:
        self._calls: list[LLMCall] = []
        self._lock = threading.Lock()
        self._budget = budget
        self._callbacks: list[Any] = []

    def record(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> LLMCall:
        cost = get_cost(provider, model, input_tokens, output_tokens)
        call = LLMCall(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            timestamp=time.time(),
            metadata=metadata or {},
        )
        with self._lock:
            self._calls.append(call)
        for cb in self._callbacks:
            cb(call, self)
        return call

    def on_record(self, callback: Any) -> None:
        self._callbacks.append(callback)

    @property
    def calls(self) -> list[LLMCall]:
        with self._lock:
            return list(self._calls)

    @property
    def total_cost(self) -> float:
        with self._lock:
            return sum(c.cost_usd for c in self._calls)

    @property
    def total_tokens(self) -> int:
        with self._lock:
            return sum(c.total_tokens for c in self._calls)

    @property
    def call_count(self) -> int:
        with self._lock:
            return len(self._calls)

    def cost_by_model(self) -> dict[str, float]:
        result: dict[str, float] = {}
        with self._lock:
            for c in self._calls:
                key = f"{c.provider}/{c.model}"
                result[key] = result.get(key, 0.0) + c.cost_usd
        return result

    def cost_by_provider(self) -> dict[str, float]:
        result: dict[str, float] = {}
        with self._lock:
            for c in self._calls:
                result[c.provider] = result.get(c.provider, 0.0) + c.cost_usd
        return result

    def reset(self) -> None:
        with self._lock:
            self._calls.clear()

    def export(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {
                    "provider": c.provider,
                    "model": c.model,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "cost_usd": round(c.cost_usd, 6),
                    "latency_ms": round(c.latency_ms, 2),
                    "timestamp": c.timestamp,
                    **c.metadata,
                }
                for c in self._calls
            ]
