"""Decorators for automatic cost tracking of LLM API calls."""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

from llm_cost_tracker.tracker import CostTracker

F = TypeVar("F", bound=Callable[..., Any])

_default_tracker: CostTracker | None = None


def get_default_tracker() -> CostTracker:
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = CostTracker()
    return _default_tracker


def set_default_tracker(tracker: CostTracker) -> None:
    global _default_tracker
    _default_tracker = tracker


def track_cost(
    provider: str,
    model: str,
    tracker: CostTracker | None = None,
) -> Callable[[F], F]:
    """Decorator that tracks cost of a function returning (input_tokens, output_tokens, result)."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            t = tracker or get_default_tracker()
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000

            if isinstance(result, tuple) and len(result) == 3:
                input_tokens, output_tokens, value = result
                t.record(provider, model, input_tokens, output_tokens, elapsed)
                return value

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def track_openai(
    tracker: CostTracker | None = None,
) -> Callable[[F], F]:
    """Decorator for functions that return an OpenAI ChatCompletion response."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            t = tracker or get_default_tracker()
            start = time.perf_counter()
            response = fn(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000

            usage = getattr(response, "usage", None)
            model = getattr(response, "model", "unknown")
            if usage:
                t.record(
                    provider="openai",
                    model=model,
                    input_tokens=getattr(usage, "prompt_tokens", 0),
                    output_tokens=getattr(usage, "completion_tokens", 0),
                    latency_ms=elapsed,
                )
            return response

        return wrapper  # type: ignore[return-value]

    return decorator


def track_anthropic(
    tracker: CostTracker | None = None,
) -> Callable[[F], F]:
    """Decorator for functions that return an Anthropic Message response."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            t = tracker or get_default_tracker()
            start = time.perf_counter()
            response = fn(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000

            usage = getattr(response, "usage", None)
            model = getattr(response, "model", "unknown")
            if usage:
                t.record(
                    provider="anthropic",
                    model=model,
                    input_tokens=getattr(usage, "input_tokens", 0),
                    output_tokens=getattr(usage, "output_tokens", 0),
                    latency_ms=elapsed,
                )
            return response

        return wrapper  # type: ignore[return-value]

    return decorator
