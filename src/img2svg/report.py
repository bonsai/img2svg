"""JSONL run/report helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def run_record(input_path, output_path, route, verification=None) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "route": route.to_dict(),
        "verification": verification,
    }
