from llm_cost_tracker.providers.registry import (
    ModelPricing,
    get_cost,
    list_models,
    register_model,
)


def test_openai_gpt4o_cost():
    cost = get_cost("openai", "gpt-4o", input_tokens=1_000_000, output_tokens=0)
    assert cost == 2.50


def test_anthropic_sonnet_cost():
    cost = get_cost("anthropic", "claude-sonnet-4", input_tokens=0, output_tokens=1_000_000)
    assert cost == 15.00


def test_mixed_tokens():
    cost = get_cost("openai", "gpt-4o", input_tokens=500_000, output_tokens=500_000)
    expected = (500_000 / 1_000_000) * 2.50 + (500_000 / 1_000_000) * 10.00
    assert abs(cost - expected) < 0.001


def test_unknown_provider():
    cost = get_cost("unknown", "some-model", input_tokens=1000, output_tokens=1000)
    assert cost == 0.0


def test_fuzzy_model_match():
    cost = get_cost("openai", "gpt-4o-2024-08-06", input_tokens=1_000_000, output_tokens=0)
    assert cost > 0


def test_register_custom_model():
    register_model("custom", "my-model", ModelPricing(1.0, 2.0))
    cost = get_cost("custom", "my-model", input_tokens=1_000_000, output_tokens=1_000_000)
    assert cost == 3.0


def test_list_models():
    models = list_models()
    assert "openai" in models
    assert "anthropic" in models
    assert "gpt-4o" in models["openai"]


def test_list_models_single_provider():
    models = list_models("openai")
    assert list(models.keys()) == ["openai"]
