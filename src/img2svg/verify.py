"""SVG verification by re-rasterizing the result and comparing it to the source."""

from __future__ import annotations

from pathlib import Path
import io
import math
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageStat


def _source_image(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as img:
        return img.convert("RGBA").resize(size)


def _render_svg(path: Path, size: tuple[int, int]) -> Image.Image:
    try:
        import cairosvg
    except ImportError as exc:
        raise RuntimeError(
            "SVG verification needs cairosvg. Install: pip install 'img2svg[verify]'"
        ) from exc
    png = cairosvg.svg2png(url=str(path), output_width=size[0], output_height=size[1])
    return Image.open(io.BytesIO(png)).convert("RGBA")


def verify_svg(source: Path, svg: Path) -> dict:
    with Image.open(source) as img:
        size = img.size

    rendered = _render_svg(svg, size)
    original = _source_image(source, size)
    diff = ImageChops.difference(original, rendered)
    mean = sum(ImageStat.Stat(diff).mean) / 4.0
    rms = math.sqrt(sum(v * v for v in ImageStat.Stat(diff).rms) / 4.0)

    root = ET.parse(svg).getroot()
    elements = sum(1 for _ in root.iter())
    return {
        "verified": True,
        "width": size[0],
        "height": size[1],
        "mean_abs_diff": round(mean, 4),
        "rms_diff": round(rms, 4),
        "svg_elements": elements,
    }
