"""
chord.py — Chord diagram for flow / relationship matrices.

Charts:
    chord_chart — group arcs sized by total flow, quadratic-Bezier ribbons
            connecting every pairwise flow

All functions return a matplotlib Figure ready for publication.
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Polygon, Wedge

from .palette import auto_colors, blend
from .utils import setup_figure, save_figure


def _arc_point(center, radius, angle_deg):
    a = np.deg2rad(angle_deg)
    return center[0] + radius * np.cos(a), center[1] + radius * np.sin(a)


def _ribbon(center, radius, a_start, a_end, b_start, b_end, color, alpha):
    """Classic chord ribbon: both edges are quadratic Beziers whose
    control point is the circle center, so ribbons curve through the
    middle without crossing it chaotically."""
    p_as = np.array(_arc_point(center, radius, a_start))
    p_ae = np.array(_arc_point(center, radius, a_end))
    p_bs = np.array(_arc_point(center, radius, b_start))
    p_be = np.array(_arc_point(center, radius, b_end))
    ctrl = np.array(center)

    t = np.linspace(0, 1, 40)[:, None]
    edge1 = ((1 - t) ** 2 * p_as + 2 * (1 - t) * t * ctrl + t ** 2 * p_be)
    edge2 = ((1 - t) ** 2 * p_bs + 2 * (1 - t) * t * ctrl + t ** 2 * p_ae)
    # close the band along the ring arcs (not straight chords)
    arc_b = np.array([_arc_point(center, radius, a)
                      for a in np.linspace(b_end, b_start, 10)])
    arc_a = np.array([_arc_point(center, radius, a)
                      for a in np.linspace(a_end, a_start, 10)])

    verts = np.vstack([edge1, arc_b, edge2[::-1], arc_a])
    return Polygon(verts, closed=True, facecolor=color, edgecolor="none",
                   alpha=alpha, zorder=1)


def chord_chart(
    matrix,
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    figsize: tuple = (8.5, 8),
    palette: str = "nature_qual",
    gap_deg: float = 4,
    inner_radius: float = 0.72,
    ribbon_alpha: float = 0.42,
    label_size: float = 10,
    show_totals: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Chord diagram — group arcs sized by total flow, ribbons connecting
    every pairwise flow. Ideal for migration matrices, trade flows,
    resource exchange, and interaction summaries.

    Parameters
    ----------
    matrix : 2-D array-like (n x n)
        Square flow matrix; ``matrix[i, j]`` = flow from i to j.
        The diagonal is ignored.
    labels : list of str, optional
        Node names.

    Returns
    -------
    Figure
    """
    M = np.asarray(matrix, dtype=float).copy()
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError(
            f"chord needs a square matrix, got shape {M.shape}.")
    np.fill_diagonal(M, 0)
    n = M.shape[0]
    labels = list(labels) if labels else [f"N{i + 1}" for i in range(n)]
    totals = M.sum(axis=1) + M.sum(axis=0) - M.sum() / n  # avoid double count
    totals = M.sum(axis=1) + M.sum(axis=0)
    if totals.sum() <= 0:
        raise ValueError("chord matrix has no positive flows.")

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize, **kwargs)
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.axis("off")

    center = (0.0, 0.0)
    r_outer, r_inner = 1.0, inner_radius
    colors = auto_colors(n, palette)

    # angular budget: full circle minus n gaps, split by node totals
    gap_total = gap_deg * n
    usable = 360 - gap_total
    shares = totals / totals.sum()
    angles = []
    start = 90.0  # start at top, clockwise
    for sh in shares:
        span = sh * usable
        angles.append((start, start + span))
        start += span + gap_deg

    # draw node arcs (outer ring)
    for i, (a0, a1) in enumerate(angles):
        ax.add_patch(Wedge(center, r_outer, a0, a1, width=r_outer - r_inner,
                           facecolor=colors[i % len(colors)], edgecolor="white",
                           lw=1.4, zorder=3))
        mid = (a0 + a1) / 2
        lx, ly = _arc_point(center, r_outer + 0.07, mid)
        ha = "left" if np.cos(np.deg2rad(mid)) > 0.05 else (
            "right" if np.cos(np.deg2rad(mid)) < -0.05 else "center")
        va = "bottom" if np.sin(np.deg2rad(mid)) > 0.7 else (
            "top" if np.sin(np.deg2rad(mid)) < -0.7 else "center")
        txt = labels[i]
        if show_totals:
            txt += f"  ({totals[i]:.4g})"
        ax.text(lx, ly, txt, ha=ha, va=va, fontsize=label_size,
                color="#1A1A1A", zorder=5)

    # ribbons for each flow i -> j (upper triangle only, drawn both ends)
    # per-node flow budget tracking along its arc
    node_budget = {i: (angles[i][0], angles[i][0]) for i in range(n)}

    def next_segment(i, width_deg):
        lo, cur = node_budget[i]
        seg = (cur, cur + width_deg)
        node_budget[i] = (lo, cur + width_deg)
        return seg

    flows = []
    for i in range(n):
        for j in range(i + 1, n):
            if M[i, j] > 0:
                flows.append((i, j, M[i, j]))
            if M[j, i] > 0:
                flows.append((j, i, M[j, i]))
    flows.sort(key=lambda f: -f[2])

    for i, j, val in flows:
        w_i = val / totals[i] * (angles[i][1] - angles[i][0])
        w_j = val / totals[j] * (angles[j][1] - angles[j][0])
        si = next_segment(i, w_i)
        sj = next_segment(j, w_j)
        # ribbons start from the node's inner edge, sweeping outward flow
        color = blend(colors[i % len(colors)], colors[j % len(colors)], 0.5)
        ax.add_patch(_ribbon(center, r_inner, si[0], si[1],
                             sj[0], sj[1],
                             color=color, alpha=ribbon_alpha))

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.4, 1.4)
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=16)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = ["chord_chart"]
