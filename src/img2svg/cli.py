"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .report import append_jsonl, run_record
from .router import resolve_route
from .vectorize import vectorize
from .verify import verify_svg


def main() -> int:
    p = argparse.ArgumentParser(description="JEV-routed raster → SVG converter")
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path)
    p.add_argument("--jev", type=Path, help="JEV routing decisions in JSONL")
    p.add_argument("--report", type=Path, help="append execution records to JSONL")
    p.add_argument("--no-verify", action="store_true")
    args = p.parse_args()

    output = args.output or args.input.with_suffix(".svg")
    output.parent.mkdir(parents=True, exist_ok=True)

    route = resolve_route(args.input, args.jev)
    vectorize(args.input, output, route)

    verification = None
    if not args.no_verify:
        verification = verify_svg(args.input, output)

    record = run_record(args.input, output, route, verification)
    if args.report:
        append_jsonl(args.report, record)

    print(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
