"""JEV-compatible routing contract.

JEV can make the routing decision externally by emitting one JSON object per
input. img2svg also has a deterministic fallback so the pipeline remains
usable without an agent.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass
class Route:
    intent: str = "graphic"
    engine: str = "vtracer"
    mode: str = "spline"
    hierarchical: str = "stacked"
    max_colors: int | None = None
    filter_speckle: int = 4

    def to_dict(self) -> dict:
        return asdict(self)


def heuristic_route(path: Path) -> Route:
    name = path.stem.lower()
    if any(x in name for x in ("logo", "icon", "mark")):
        return Route(intent="logo", mode="polygon", hierarchical="cutout", max_colors=16)
    if any(x in name for x in ("line", "scan", "sketch", "ink")):
        return Route(intent="lineart", mode="spline", hierarchical="stacked", max_colors=2)
    if any(x in name for x in ("photo", "portrait", "image")):
        return Route(intent="photo", mode="spline", hierarchical="stacked", max_colors=32)
    return Route()


def load_jev_routes(path: Path) -> dict[str, Route]:
    routes: dict[str, Route] = {}
    if not path.exists():
        return routes
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
        key = str(obj.get("input") or obj.get("path") or "")
        if not key:
            continue
        routes[key] = Route(
            intent=obj.get("intent", "graphic"),
            engine=obj.get("engine", "vtracer"),
            mode=obj.get("mode", "spline"),
            hierarchical=obj.get("hierarchical", "stacked"),
            max_colors=obj.get("max_colors"),
            filter_speckle=int(obj.get("filter_speckle", 4)),
        )
    return routes


def resolve_route(input_path: Path, jev_path: Path | None = None) -> Route:
    if jev_path:
        routes = load_jev_routes(jev_path)
        for key in (str(input_path), input_path.name, input_path.as_posix()):
            if key in routes:
                return routes[key]
    return heuristic_route(input_path)
