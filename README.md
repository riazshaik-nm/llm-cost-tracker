# llm-cost-tracker

[![CI](https://github.com/riazshaik-nm/llm-cost-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/riazshaik-nm/llm-cost-tracker/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Lightweight cost tracking and budget alerts for LLM API calls. Know exactly what you're spending across OpenAI, Anthropic, Google, and Mistral — before the invoice surprises you.

```
┌──────────────── LLM Cost Summary ────────────────┐
│  Total Cost  $0.0452                              │
│ Total Tokens 22,100                               │
│   API Calls  5                                    │
│  Avg Latency 720ms                                │
└───────────────────────────────────────────────────┘
```

## Features

- **Multi-provider pricing** — OpenAI, Anthropic, Google, Mistral with up-to-date token costs
- **Decorators** — `@track_openai()` and `@track_anthropic()` wrap your existing functions
- **Budget alerts** — Get warned or blocked when spending exceeds a threshold
- **Thread-safe** — Safe for concurrent workloads
- **Rich CLI reports** — Beautiful terminal output with cost breakdowns
- **Zero dependencies on LLM SDKs** — Only requires `rich` for display; provider SDKs are optional
- **Export to JSON** — Pipe data into your own dashboards

## Install

```bash
pip install llm-cost-tracker

# With provider SDK support
pip install llm-cost-tracker[openai]
pip install llm-cost-tracker[anthropic]
pip install llm-cost-tracker[all]
```

## Quick Start

### Track costs manually

```python
from llm_cost_tracker import CostTracker
from llm_cost_tracker.reports.console import print_summary

tracker = CostTracker()

# After each API call, record the token usage
tracker.record("openai", "gpt-4o", input_tokens=2500, output_tokens=800)
tracker.record("anthropic", "claude-sonnet-4", input_tokens=3000, output_tokens=1200)

print_summary(tracker)
# Total Cost:   $0.0243
# Total Tokens: 7,500
# API Calls:    2
```

### Use decorators with OpenAI

```python
from openai import OpenAI
from llm_cost_tracker import CostTracker, track_openai

tracker = CostTracker()
client = OpenAI()

@track_openai(tracker=tracker)
def ask(question: str):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}],
    )

ask("What is the capital of France?")
ask("Explain quantum computing in 3 sentences.")

print(f"Total spent: ${tracker.total_cost:.4f}")
```

### Use decorators with Anthropic

```python
import anthropic
from llm_cost_tracker import CostTracker, track_anthropic

tracker = CostTracker()
client = anthropic.Anthropic()

@track_anthropic(tracker=tracker)
def ask(question: str):
    return client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    )

ask("Write a haiku about Python.")
print(f"Total spent: ${tracker.total_cost:.4f}")
```

### Set budget alerts

```python
from llm_cost_tracker import CostTracker, BudgetAlert
from llm_cost_tracker.budget import BudgetAction

tracker = CostTracker()

# Warn when spending exceeds $5
BudgetAlert(
    tracker=tracker,
    limit_usd=5.00,
    action=BudgetAction.WARN,
    on_alert=lambda limit, current: print(f"⚠️  Budget exceeded: ${current:.2f} / ${limit:.2f}"),
)

# Or hard-block to prevent runaway costs
BudgetAlert(tracker=tracker, limit_usd=10.00, action=BudgetAction.BLOCK)
# Raises BudgetExceededError when limit is hit
```

### Export and analyze

```python
from llm_cost_tracker.storage.json_store import save_json

save_json(tracker, "costs.json")
```

```bash
# View reports from the CLI
llm-cost costs.json --breakdown
```

### Register custom models

```python
from llm_cost_tracker.providers.registry import register_model, ModelPricing

register_model("my-provider", "custom-model", ModelPricing(
    input_per_million=1.50,
    output_per_million=5.00,
))
```

## Supported Models

| Provider | Models |
|----------|--------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1, o1-mini, o3, o3-mini, o4-mini |
| **Anthropic** | claude-opus-4, claude-sonnet-4, claude-haiku-3.5, claude-3-opus, claude-3.5-sonnet, claude-3-haiku |
| **Google** | gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash |
| **Mistral** | mistral-large, mistral-medium, mistral-small, codestral |

Missing a model? Use `register_model()` or open a PR.

## Development

```bash
git clone https://github.com/riazshaik-nm/llm-cost-tracker.git
cd llm-cost-tracker
pip install -e ".[dev]"
pytest -v
ruff check src/ tests/
mypy src/
```

## License

MIT
