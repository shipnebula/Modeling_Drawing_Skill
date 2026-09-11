#!/usr/bin/env python3
"""
render.py — CLI tool for Math Modeling Viz.

Usage:
    python render.py --chart bar_chart --data '[10,20,30]' --labels 'A,B,C' --title 'Results'
    python render.py --chart line_chart --data-file data.csv --title 'Trend'
    python render.py --list-charts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _setup_path():
    """Add the scripts directory to sys.path so `plot` can be imported."""
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))


def main():
    parser = argparse.ArgumentParser(
        description="Math Modeling Viz — CLI renderer",
    )
    parser.add_argument("--chart", type=str, help="Chart type to render")
    parser.add_argument("--data", type=str, help="Data as JSON list (e.g. '[10,20,30]')")
    parser.add_argument("--data-file", type=str, help="Path to CSV/JSON data file")
    parser.add_argument("--labels", type=str, help="Comma-separated labels")
    parser.add_argument("--title", type=str, default=None, help="Chart title")
    parser.add_argument("--xlabel", type=str, default=None, help="X-axis label")
    parser.add_argument("--ylabel", type=str, default=None, help="Y-axis label")
    parser.add_argument("--palette", type=str, default="nature_qual", help="Color palette")
    parser.add_argument("--figsize", type=str, default="8x5", help="Figure size (WxH)")
    parser.add_argument("--style", type=str, default="nature", help="Style preset")
    parser.add_argument("--output", type=str, default="output.png", help="Output file")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI")
    parser.add_argument("--list-charts", action="store_true", help="List all available charts")
    parser.add_argument("--list-palettes", action="store_true", help="List all palettes")

    args = parser.parse_args()

    _setup_path()

    if args.list_charts:
        from plot import __all__ as charts
        print("Available charts:")
        for c in sorted(charts):
            print(f"  • {c}")
        return

    if args.list_palettes:
        from plot.palette import ALL_PALETTES
        for family, palettes in ALL_PALETTES.items():
            print(f"\n{family.upper()}:")
            for name, colors in palettes.items():
                preview = " ".join(colors[:5])
                print(f"  {name}: {preview}{'…' if len(colors) > 5 else ''}")
        return

    if not args.chart:
        parser.error("--chart is required (or use --list-charts)")

    # Parse data
    data = None
    if args.data:
        data = json.loads(args.data)
    elif args.data_file:
        path = Path(args.data_file)
        if path.suffix == ".json":
            with open(path) as f:
                data = json.load(f)
        elif path.suffix == ".csv":
            import csv
            with open(path) as f:
                reader = csv.reader(f)
                rows = list(reader)
            data = [[float(x) for x in row[1:]] for row in rows] if len(rows) > 1 else rows
        else:
            print(f"Unsupported file format: {path.suffix}")
            sys.exit(1)

    if data is None:
        parser.error("Data required: --data or --data-file")

    # Parse labels
    labels = None
    if args.labels:
        labels = [l.strip() for l in args.labels.split(",")]

    # Parse figsize
    fig_w, fig_h = [int(x) for x in args.style.replace("x", "x").split("x")]
    figsize = (fig_w, fig_h)

    # Import and render
    from plot import __import__ as _imp
    import importlib

    chart_module = importlib.import_module("plot")
    chart_func = getattr(chart_module, args.chart, None)

    if chart_func is None:
        print(f"Unknown chart: {args.chart}")
        print("Use --list-charts to see available charts.")
        sys.exit(1)

    # Build kwargs
    kwargs = {}
    if args.title:
        kwargs["title"] = args.title
    if args.xlabel:
        kwargs["xlabel"] = args.xlabel
    if args.ylabel:
        kwargs["ylabel"] = args.ylabel
    if labels:
        kwargs["labels"] = labels

    try:
        fig = chart_func(data, figsize=figsize, **kwargs)
        fig.savefig(args.output, dpi=args.dpi, bbox_inches="tight")
        print(f"✓ Saved to {args.output}")
    except TypeError as e:
        print(f"Parameter error: {e}")
        print(f"Chart signature: {args.chart}(...)")
        sys.exit(1)
    except Exception as e:
        print(f"Error rendering chart: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()