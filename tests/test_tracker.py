from llm_cost_tracker.tracker import CostTracker


def test_record_and_total():
    t = CostTracker()
    t.record("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
    assert t.call_count == 1
    assert t.total_tokens == 1500
    assert t.total_cost > 0


def test_cost_by_model():
    t = CostTracker()
    t.record("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
    t.record("openai", "gpt-4o-mini", input_tokens=2000, output_tokens=1000)
    by_model = t.cost_by_model()
    assert "openai/gpt-4o" in by_model
    assert "openai/gpt-4o-mini" in by_model


def test_cost_by_provider():
    t = CostTracker()
    t.record("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
    t.record("anthropic", "claude-sonnet-4", input_tokens=1000, output_tokens=500)
    by_provider = t.cost_by_provider()
    assert "openai" in by_provider
    assert "anthropic" in by_provider


def test_reset():
    t = CostTracker()
    t.record("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
    assert t.call_count == 1
    t.reset()
    assert t.call_count == 0
    assert t.total_cost == 0


def test_export():
    t = CostTracker()
    t.record("openai", "gpt-4o", input_tokens=1000, output_tokens=500, latency_ms=150.5)
    data = t.export()
    assert len(data) == 1
    assert data[0]["provider"] == "openai"
    assert data[0]["model"] == "gpt-4o"
    assert data[0]["input_tokens"] == 1000
    assert data[0]["output_tokens"] == 500
    assert "cost_usd" in data[0]
    assert "timestamp" in data[0]


def test_unknown_model_returns_zero_cost():
    t = CostTracker()
    call = t.record("unknown_provider", "unknown_model", input_tokens=100, output_tokens=50)
    assert call.cost_usd == 0.0


def test_thread_safety():
    import threading

    t = CostTracker()
    barrier = threading.Barrier(10)

    def record_calls():
        barrier.wait()
        for _ in range(100):
            t.record("openai", "gpt-4o", input_tokens=100, output_tokens=50)

    threads = [threading.Thread(target=record_calls) for _ in range(10)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    assert t.call_count == 1000
