"""Pricing registry for LLM providers — cost per 1M tokens in USD."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: float
    output_per_million: float


PROVIDERS: dict[str, dict[str, ModelPricing]] = {
    "openai": {
        "gpt-4o": ModelPricing(2.50, 10.00),
        "gpt-4o-mini": ModelPricing(0.15, 0.60),
        "gpt-4-turbo": ModelPricing(10.00, 30.00),
        "gpt-4": ModelPricing(30.00, 60.00),
        "gpt-3.5-turbo": ModelPricing(0.50, 1.50),
        "o1": ModelPricing(15.00, 60.00),
        "o1-mini": ModelPricing(3.00, 12.00),
        "o3": ModelPricing(10.00, 40.00),
        "o3-mini": ModelPricing(1.10, 4.40),
        "o4-mini": ModelPricing(1.10, 4.40),
    },
    "anthropic": {
        "claude-opus-4": ModelPricing(15.00, 75.00),
        "claude-sonnet-4": ModelPricing(3.00, 15.00),
        "claude-haiku-3.5": ModelPricing(0.80, 4.00),
        "claude-3-opus": ModelPricing(15.00, 75.00),
        "claude-3.5-sonnet": ModelPricing(3.00, 15.00),
        "claude-3-haiku": ModelPricing(0.25, 1.25),
    },
    "google": {
        "gemini-2.5-pro": ModelPricing(1.25, 10.00),
        "gemini-2.5-flash": ModelPricing(0.15, 0.60),
        "gemini-2.0-flash": ModelPricing(0.10, 0.40),
        "gemini-1.5-pro": ModelPricing(1.25, 5.00),
        "gemini-1.5-flash": ModelPricing(0.075, 0.30),
    },
    "mistral": {
        "mistral-large": ModelPricing(2.00, 6.00),
        "mistral-medium": ModelPricing(2.70, 8.10),
        "mistral-small": ModelPricing(0.20, 0.60),
        "codestral": ModelPricing(0.30, 0.90),
    },
}


def get_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    provider_lower = provider.lower()
    model_lower = model.lower()

    models = PROVIDERS.get(provider_lower, {})

    pricing = models.get(model_lower)
    if pricing is None:
        for name, p in models.items():
            if name in model_lower or model_lower in name:
                pricing = p
                break

    if pricing is None:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * pricing.input_per_million
    output_cost = (output_tokens / 1_000_000) * pricing.output_per_million
    return input_cost + output_cost


def register_model(provider: str, model: str, pricing: ModelPricing) -> None:
    provider_lower = provider.lower()
    if provider_lower not in PROVIDERS:
        PROVIDERS[provider_lower] = {}
    PROVIDERS[provider_lower][model.lower()] = pricing


def list_models(provider: str | None = None) -> dict[str, list[str]]:
    if provider:
        models = PROVIDERS.get(provider.lower(), {})
        return {provider.lower(): list(models.keys())}
    return {p: list(m.keys()) for p, m in PROVIDERS.items()}
