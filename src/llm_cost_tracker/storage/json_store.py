"""JSON file persistence for cost tracking data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm_cost_tracker.tracker import CostTracker


def save_json(tracker: CostTracker, path: str | Path) -> None:
    data = tracker.export()
    Path(path).write_text(json.dumps(data, indent=2))


def load_json(path: str | Path) -> list[dict[str, Any]]:
    text = Path(path).read_text()
    return json.loads(text)  # type: ignore[no-any-return]
