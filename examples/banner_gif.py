#!/usr/bin/env python3
"""banner_gif.py — animated README banner: a GA convergence sequence."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import plot as pl

OUT = Path(__file__).resolve().parent.parent / "docs" / "images" / "banner.gif"


def frame(i: int, n: int):
    pl.apply_style("nature")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    xs = np.arange(60)
    progress = max(i / n, 0.02)

    # candidate population cloud (same length as its x positions)
    cloud_x = rng.uniform(0, 59, 220)
    best_now = 0.35 + 0.55 * (1 - np.exp(-3 * progress))
    cloud = best_now + rng.normal(0, 0.25 * (1 - progress) + 0.01, 220)
    ax.scatter(cloud_x, cloud, s=12, color="#B8C4CE",
               alpha=0.55, lw=0, label="population")

    # best-so-far curve up to this generation
    curve = 0.35 + 0.55 * (1 - np.exp(-3 * xs / max(i * 2, 1)))
    ax.plot(xs, curve, color="#2E86AB", lw=2.4, label="best fitness")

    ax.scatter([xs[-1]], [curve[-1]], s=90, color="#C73E1D", zorder=5,
               edgecolors="white", lw=1.2)
    ax.text(xs[-1] - 1, curve[-1] + 0.06, f"gen {i + 1}/{n}", ha="right",
            fontsize=11, fontweight="bold", color="#1D3557")
    ax.set_title("Genetic Algorithm Convergence — Math Modeling Viz",
                 fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("generation")
    ax.set_ylabel("fitness")
    ax.set_ylim(0.2, 1.05)
    ax.set_xlim(0, 59)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    pl.make_gif(frame, n_frames=24, filename=str(OUT), fps=8, dpi=100)
    print(f"animated banner → {OUT}")
