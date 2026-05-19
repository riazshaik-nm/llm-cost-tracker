"""CLI for viewing cost reports from saved JSON data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console

from llm_cost_tracker.reports.console import print_breakdown, print_summary
from llm_cost_tracker.tracker import CostTracker


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="llm-cost",
        description="View LLM cost tracking reports",
    )
    parser.add_argument("file", help="JSON file with cost data")
    parser.add_argument("--breakdown", action="store_true", help="Show cost breakdown by model")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output as JSON")

    args = parser.parse_args(argv)
    path = Path(args.file)

    if not path.exists():
        Console().print(f"[red]File not found: {path}[/red]")
        sys.exit(1)

    data = json.loads(path.read_text())
    tracker = CostTracker()
    for entry in data:
        tracker.record(
            provider=entry["provider"],
            model=entry["model"],
            input_tokens=entry["input_tokens"],
            output_tokens=entry["output_tokens"],
            latency_ms=entry.get("latency_ms", 0),
        )

    if args.output_json:
        totals = {
            "total_cost_usd": round(tracker.total_cost, 6),
            "total_tokens": tracker.total_tokens,
            "call_count": tracker.call_count,
            "by_model": {k: round(v, 6) for k, v in tracker.cost_by_model().items()},
        }
        print(json.dumps(totals, indent=2))
        return

    print_summary(tracker)
    if args.breakdown:
        print_breakdown(tracker)
