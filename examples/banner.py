#!/usr/bin/env python3
"""Generate the README banner using the library itself (dogfooding demo)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import plot as pl

OUT = Path(__file__).resolve().parent.parent / "docs" / "images" / "banner.png"


def main() -> None:
    rng = np.random.default_rng(7)
    pl.apply_style("nature")

    fig = plt.figure(figsize=(12, 4.4))
    gs = GridSpec(2, 4, figure=fig, hspace=0.55, wspace=0.42,
                  left=0.05, right=0.985, top=0.80, bottom=0.10)

    # Title
    fig.text(0.5, 0.955, "Math Modeling Viz", ha="center", va="center",
             fontsize=25, fontweight="bold", color="#1A1A1A")
    fig.text(0.5, 0.875, "Publication-quality charts for CUMCM / MCM-ICM — "
             "one import, one call", ha="center", va="center",
             fontsize=11.5, color="#666666")

    # (1) line
    ax = fig.add_subplot(gs[0, 0])
    xs = np.linspace(0, 6, 40)
    ax.plot(xs, np.sin(xs), color="#2E86AB", lw=2)
    ax.plot(xs, np.sin(xs - 0.8), color="#F18F01", lw=2, ls="--")
    ax.set_title("line", fontsize=9, color="#888888")
    ax.set_xticks([]); ax.set_yticks([])

    # (2) sensitivity
    ax = fig.add_subplot(gs[0, 1])
    params = ["Price", "Demand", "Cost"]
    lo, hi = [0.86, 0.90, 0.93], [0.97, 0.95, 0.99]
    base = 0.92
    for i, (l, h) in enumerate(zip(lo, hi)):
        ax.barh(i, base - l, left=l, color="#457B9D", alpha=0.85, height=0.55)
        ax.barh(i, h - base, left=base, color="#E63946", alpha=0.85, height=0.55)
    ax.set_yticks(range(3)); ax.set_yticklabels(params, fontsize=7.5)
    ax.set_title("sensitivity", fontsize=9, color="#888888")
    ax.set_xticks([]); ax.set_xlim(0.8, 1.0)

    # (3) contour
    ax = fig.add_subplot(gs[0, 2])
    g = np.linspace(0, 2, 60)
    X, Y = np.meshgrid(g, g)
    Z = np.sin(3 * X) * np.cos(2 * Y) * np.exp(-0.3 * (X + Y))
    ax.contourf(X, Y, Z, levels=12, cmap="viridis")
    ax.contour(X, Y, Z, levels=12, colors="white", linewidths=0.4)
    ax.set_title("contour", fontsize=9, color="#888888")
    ax.set_xticks([]); ax.set_yticks([])

    # (4) radar
    ax = fig.add_subplot(gs[0, 3], projection="polar")
    cats = ["Speed", "Cost", "Risk", "Scale"]
    vals = [4.2, 3.1, 3.8, 4.6]
    ang = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist()
    ang += ang[:1]; v = vals + vals[:1]
    ax.plot(ang, v, color="#2E86AB", lw=1.8)
    ax.fill(ang, v, color="#2E86AB", alpha=0.2)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(cats, fontsize=7)
    ax.set_yticks([]); ax.grid(alpha=0.3)
    ax.set_title("radar", fontsize=9, color="#888888", pad=9)

    # (5) bars
    ax = fig.add_subplot(gs[1, 0])
    ax.bar(range(4), [3.2, 4.1, 2.8, 4.8],
           color=["#2E86AB", "#A23B72", "#F18F01", "#44BBA4"], width=0.62)
    ax.set_title("bar", fontsize=9, color="#888888")
    ax.set_xticks([]); ax.set_yticks([])

    # (6) scatter
    ax = fig.add_subplot(gs[1, 1])
    n = 60
    sx = rng.uniform(0, 10, n)
    sy = 0.8 * sx + rng.normal(0, 1.1, n)
    ax.scatter(sx, sy, s=16, color="#2E86AB", alpha=0.7, edgecolors="white", lw=0.4)
    b, a = np.polyfit(sx, sy, 1)
    ax.plot([0, 10], [a, a + 10 * b], color="#C73E1D", lw=1.8)
    ax.set_title("scatter + fit", fontsize=9, color="#888888")
    ax.set_xticks([]); ax.set_yticks([])

    # (7) heatmap
    ax = fig.add_subplot(gs[1, 2])
    M = np.array([[52, 8], [6, 34]], float)
    ax.imshow(M, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(M[i, j]), ha="center", va="center",
                    fontsize=10, fontweight="bold",
                    color="white" if M[i, j] > 40 else "#1A1A1A")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("confusion", fontsize=9, color="#888888")

    # (8) dashboard KPI
    ax = fig.add_subplot(gs[1, 3])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.08), 0.96, 0.84, transform=ax.transAxes,
                               facecolor="#F7F9FB", edgecolor="#E3E8ED", lw=1,
                               zorder=1))
    ax.text(0.08, 0.72, "Accuracy", fontsize=8, color="#666666",
            transform=ax.transAxes)
    ax.text(0.08, 0.45, "94.2%", fontsize=17, fontweight="bold",
            color="#1D3557", transform=ax.transAxes)
    ax.text(0.08, 0.20, "▲ +2.1%", fontsize=8.5, color="#2A9D8F",
            fontweight="bold", transform=ax.transAxes)
    ax.add_patch(plt.Rectangle((0.02, 0.08), 0.96 * 0.942, 0.055,
                               transform=ax.transAxes, facecolor="#2A9D8F",
                               edgecolor="none", zorder=2))
    ax.set_title("dashboard", fontsize=9, color="#888888")

    fig.savefig(OUT, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"banner saved → {OUT}")


if __name__ == "__main__":
    main()
