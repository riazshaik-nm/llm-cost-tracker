"""Rich console reports for LLM cost data."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from llm_cost_tracker.tracker import CostTracker


def print_summary(tracker: CostTracker, title: str = "LLM Cost Summary") -> None:
    console = Console()

    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold cyan", justify="right")
    summary.add_column()
    summary.add_row("Total Cost", f"${tracker.total_cost:.4f}")
    summary.add_row("Total Tokens", f"{tracker.total_tokens:,}")
    summary.add_row("API Calls", str(tracker.call_count))

    if tracker.calls:
        avg_latency = sum(c.latency_ms for c in tracker.calls) / len(tracker.calls)
        summary.add_row("Avg Latency", f"{avg_latency:.0f}ms")

    console.print(Panel(summary, title=title, border_style="green"))


def print_breakdown(tracker: CostTracker) -> None:
    console = Console()

    by_model = tracker.cost_by_model()
    if not by_model:
        console.print("[dim]No calls recorded yet.[/dim]")
        return

    table = Table(title="Cost Breakdown by Model", show_lines=True)
    table.add_column("Provider/Model", style="cyan")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("% of Total", justify="right")

    total = tracker.total_cost
    for model, cost in sorted(by_model.items(), key=lambda x: -x[1]):
        pct = (cost / total * 100) if total > 0 else 0
        bar_len = int(pct / 5)
        bar = Text("█" * bar_len, style="green") + Text("░" * (20 - bar_len), style="dim")
        table.add_row(model, f"${cost:.4f}", bar)

    console.print(table)


def print_call_log(tracker: CostTracker, last_n: int = 10) -> None:
    console = Console()
    calls = tracker.calls[-last_n:]

    if not calls:
        console.print("[dim]No calls recorded yet.[/dim]")
        return

    table = Table(title=f"Last {len(calls)} API Calls")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Model", style="cyan")
    table.add_column("Tokens", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Latency", justify="right", style="yellow")

    for i, call in enumerate(calls, 1):
        table.add_row(
            str(i),
            f"{call.provider}/{call.model}",
            f"{call.total_tokens:,}",
            f"${call.cost_usd:.4f}",
            f"{call.latency_ms:.0f}ms",
        )

    console.print(table)
