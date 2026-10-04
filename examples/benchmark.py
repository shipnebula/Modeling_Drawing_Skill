#!/usr/bin/env python3
"""
benchmark.py — Render-time benchmarks for math-modeling-viz.

Run from the repo root:
    python examples/benchmark.py [--repeat 3]

Times a representative chart from each module and prints a table.
Useful for catching performance regressions before they ship.
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import matplotlib

matplotlib.use("Agg")

import plot as pl  # noqa: E402

rng = np.random.default_rng(42)


def _cases():
    xs = np.linspace(0, 10, 200)
    X, Y = np.meshgrid(np.linspace(0, 2, 60), np.linspace(0, 2, 60))
    Z = np.sin(3 * X) * np.cos(2 * Y)
    pts = np.vstack([rng.normal([0, 0], 0.6, (60, 2)),
                     rng.normal([4, 4], 0.6, (60, 2))])
    return {
        "line (200 pts)": lambda: pl.line_chart(xs, np.sin(xs)),
        "line (200k pts, decimated)": lambda: pl.line_chart(
            np.arange(200_000), np.sin(np.arange(200_000) * 0.01)),
        "scatter + fit": lambda: pl.scatter_plot(xs, np.cos(xs)),
        "bar (12)": lambda: pl.bar_chart(np.abs(rng.normal(5, 2, 12))),
        "histogram (5k)": lambda: pl.histogram(rng.normal(0, 1, 5_000)),
        "box (3 groups)": lambda: pl.box_plot([rng.normal(s, 1, 100)
                                               for s in (0, 1, 2)]),
        "correlation (5x5)": lambda: pl.correlation_matrix(rng.normal(0, 1, (80, 5))),
        "heatmap (6x8)": lambda: pl.heatmap(rng.uniform(0, 1, (6, 8))),
        "surface3d (60x60)": lambda: pl.surface3d(X, Y, Z),
        "contour (60x60)": lambda: pl.contour_plot(np.linspace(0, 2, 60),
                                                   np.linspace(0, 2, 60), Z),
        "network (6 nodes)": lambda: pl.network_graph(
            list("ABCDEF"), [("A", "B"), ("B", "C"), ("C", "D")]),
        "radar (5 axes)": lambda: pl.radar_chart(
            list("ABCDE"), [[3, 4, 2, 5, 4]]),
        "qq (200)": lambda: pl.qq_plot(rng.normal(0, 1, 200)),
        "ridgeline (5 groups)": lambda: pl.ridgeline(
            {f"g{i}": rng.normal(i / 2, 1, 200) for i in range(5)}),
        "panel_figure (4 panels)": lambda: pl.panel_figure([
            {"type": "bar", "data": [3, 5, 4], "labels": ["a", "b", "c"]},
            {"type": "line", "data": {"M": [1, 2, 3]}, "x": [1, 2, 3]},
            {"type": "hist", "data": rng.normal(0, 1, 100)},
            {"type": "pie", "data": [2, 3, 5]},
        ], ncols=2),
        "bifurcation (small)": lambda: pl.bifurcation(
            a_range=(2.8, 3.9), n_a=120, n_plot=25, n_transient=40),
        "fit_comparison (3 models)": lambda: pl.fit_comparison(
            np.linspace(1, 9, 30), np.linspace(1, 9, 30) ** 0.7 + 0.1),
        "seasonal_decomposition (96)": lambda: pl.seasonal_decomposition(
            np.sin(2 * np.arange(96) * np.pi / 12) + np.arange(96) * 0.05,
            period=12),
        "dot_plot (8)": lambda: pl.dot_plot(
            list("ABCDEFGH"), rng.uniform(0, 5, 8)),
        "volcano (300)": lambda: pl.volcano_plot(
            rng.normal(0, 2, 300), rng.uniform(0, 1, 300) ** 2),
        "confidence_ellipse (2 groups)": lambda: pl.confidence_ellipse(
            rng.normal(0, 1, 100), rng.normal(0, 1, 100),
            groups=["A"] * 50 + ["B"] * 50),
        "curve_sweep (12 curves)": lambda: pl.curve_sweep(
            lambda x, k: np.sin(x) * k, np.linspace(0.2, 2, 12),
            x=np.linspace(0, 6, 150)),
        "risk_matrix (4 items)": lambda: pl.risk_matrix(
            {f"R{i}": (i % 5 + 1, i % 5 + 1) for i in range(4)}),
        "raincloud (3 groups)": lambda: pl.raincloud(
            {f"G{i}": rng.normal(i, 1, 60) for i in range(3)}),
        "circle_pack (6)": lambda: pl.circle_pack(
            {f"N{i}": 60 - i * 8 for i in range(6)}),
        "arc_diagram (5 nodes)": lambda: pl.arc_diagram(
            list("ABCDE"), [("A", "B", 2), ("B", "C", 1), ("C", "D", 3)]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=3,
                    help="renders per case (median reported)")
    args = ap.parse_args()

    pl.apply_style("nature")
    import matplotlib.pyplot as plt

    print(f"math-modeling-viz {pl.__version__} — "
          f"{len(pl.list_chart_types())} types, "
          f"matplotlib {matplotlib.__version__}\n")
    print(f"{'case':<34}{'median':>10}{'min':>10}")
    print("-" * 54)

    rows = []
    for name, fn in _cases().items():
        times = []
        for _ in range(args.repeat):
            t0 = time.perf_counter()
            fig = fn()
            times.append(time.perf_counter() - t0)
            plt.close(fig)
        med = statistics.median(times)
        rows.append((name, med, min(times)))
        print(f"{name:<34}{med * 1000:>8.0f}ms{min(times) * 1000:>8.0f}ms")

    total = sum(r[1] for r in rows)
    print("-" * 54)
    print(f"{'TOTAL (median)':<34}{total * 1000:>8.0f}ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
