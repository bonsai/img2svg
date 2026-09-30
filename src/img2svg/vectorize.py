"""VTracer adapter."""

from __future__ import annotations

from pathlib import Path

import vtracer

from .router import Route


def vectorize(input_path: Path, output_path: Path, route: Route) -> None:
    if route.engine != "vtracer":
        raise ValueError(f"Unsupported engine: {route.engine}")

    cfg = vtracer.Config(
        mode=route.mode,
        hierarchical=route.hierarchical,
        filter_speckle=route.filter_speckle,
    )
    if route.max_colors is not None:
        cfg.max_colors = route.max_colors
    cfg.convert_file(str(input_path), str(output_path))
