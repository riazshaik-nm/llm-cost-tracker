from llm_cost_tracker.decorators import track_anthropic, track_cost, track_openai
from llm_cost_tracker.tracker import CostTracker


def test_track_cost_decorator():
    tracker = CostTracker()

    @track_cost("openai", "gpt-4o", tracker=tracker)
    def my_llm_call():
        return (500, 200, "hello world")

    result = my_llm_call()
    assert result == "hello world"
    assert tracker.call_count == 1
    assert tracker.total_tokens == 700


def test_track_openai_decorator():
    tracker = CostTracker()

    class FakeUsage:
        prompt_tokens = 1000
        completion_tokens = 500

    class FakeResponse:
        usage = FakeUsage()
        model = "gpt-4o"

    @track_openai(tracker=tracker)
    def call_openai():
        return FakeResponse()

    response = call_openai()
    assert response.model == "gpt-4o"
    assert tracker.call_count == 1
    assert tracker.total_tokens == 1500


def test_track_anthropic_decorator():
    tracker = CostTracker()

    class FakeUsage:
        input_tokens = 800
        output_tokens = 400

    class FakeResponse:
        usage = FakeUsage()
        model = "claude-sonnet-4"

    @track_anthropic(tracker=tracker)
    def call_anthropic():
        return FakeResponse()

    response = call_anthropic()
    assert response.model == "claude-sonnet-4"
    assert tracker.call_count == 1
    assert tracker.total_tokens == 1200
