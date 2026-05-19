import json
import tempfile

from llm_cost_tracker.cli import main


def _make_data_file(data: list) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        return f.name


def test_cli_summary(capsys):
    path = _make_data_file([
        {
            "provider": "openai",
            "model": "gpt-4o",
            "input_tokens": 1000,
            "output_tokens": 500,
            "cost_usd": 0.0075,
            "latency_ms": 200,
            "timestamp": 1700000000,
        }
    ])
    main([path])
    captured = capsys.readouterr()
    assert "Cost" in captured.out


def test_cli_json_output(capsys):
    path = _make_data_file([
        {
            "provider": "openai",
            "model": "gpt-4o",
            "input_tokens": 1000,
            "output_tokens": 500,
            "cost_usd": 0.0075,
            "latency_ms": 200,
            "timestamp": 1700000000,
        }
    ])
    main([path, "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total_cost_usd" in data
    assert data["call_count"] == 1
