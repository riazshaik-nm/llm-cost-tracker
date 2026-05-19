"""Lightweight cost tracking and budget alerts for LLM API calls."""

from __future__ import annotations

from llm_cost_tracker.budget import BudgetAlert, BudgetExceededError
from llm_cost_tracker.decorators import track_anthropic, track_cost, track_openai
from llm_cost_tracker.providers.registry import PROVIDERS
from llm_cost_tracker.tracker import CostTracker, LLMCall

__all__ = [
    "CostTracker",
    "LLMCall",
    "track_cost",
    "track_openai",
    "track_anthropic",
    "BudgetAlert",
    "BudgetExceededError",
    "PROVIDERS",
]

__version__ = "0.1.0"
