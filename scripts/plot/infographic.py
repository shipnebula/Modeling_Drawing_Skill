"""
infographic.py — Infographic and dashboard-style visualizations.

Charts:
    dashboard            — multi-panel KPI dashboard
    kpi_card             — single KPI metric card
    bullet_chart         — bullet chart (actual vs target)
    sparkline            — compact sparkline
    gauge                — gauge / speedometer
    progress_bar         — progress bar
    process_flow         — process flow diagram
    mind_map             — mind map
    kpi_dashboard        — KPI grid dashboard
    comparison_bar       — comparison bar with target lines
"""

from __future__ import annotations

from typing import Optional, Sequence
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (
    Rectangle, FancyBboxPatch, Circle, FancyArrowPatch,
    Wedge, Polygon,
)

from .palette import auto_colors, get_palette, blend, lightness, NEUTRAL, ACCENT
from .styles import apply_style
from .utils import setup_figure, save_figure, axis_config


# ──────────────────────────────────────────────
#  KPI  DASHBOARD
# ──────────────────────────────────────────────

def dashboard(
    metrics: Sequence[dict],
    title: str = "Dashboard",
    subtitle: str | None = None,
    figsize: tuple | None = None,
    ncols: int = 3,
    style: str = "nature",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Multi-panel KPI dashboard.

    Parameters
    ----------
    metrics : list of dict
        Each dict has keys:
            'label'    : str — Metric name
            'value'    : str or float — Current value
            'change'   : str — Change indicator (e.g. '+5.2%', '-1.3%')
            'change_dir': str — 'up' or 'down' (for color)
            'target'   : str — Target value (optional)
            'progress' : float 0-1 — Progress bar value (optional)
            'sparkline': list — Sparkline data (optional)
    ncols : int
        Number of columns.
    """
    n = len(metrics)
    if ncols == 0:
        ncols = 3
    nrows = max(1, (n + ncols - 1) // ncols)

    if figsize is None:
        figsize = (ncols * 3.5, nrows * 2.5)

    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=figsize,
        gridspec_kw={"width_ratios": [1] * ncols},
        **kwargs,
    )
    axes = np.array(axes).flatten() if n > 1 else [axes]

    colors = auto_colors(n, palette="nature_qual")

    for i, (m, ax) in enumerate(zip(metrics, axes)):
        _draw_kpi_card(
            ax,
            label=m.get("label", ""),
            value=m.get("value", ""),
            change=m.get("change", ""),
            change_dir=m.get("change_dir", "up"),
            target=m.get("target"),
            progress=m.get("progress"),
            sparkline=m.get("sparkline"),
            color=colors[i % len(colors)],
        )

    # Hide unused axes
    for i in range(n, len(axes)):
        axes[i].set_visible(False)

    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.02)
    if subtitle:
        fig.text(0.5, 0.96, subtitle, fontsize=9, color="#666666",
                 ha="center", va="top")

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


def _draw_kpi_card(
    ax: plt.Axes,
    label: str,
    value: str,
    change: str = "",
    change_dir: str = "up",
    target: str | None = None,
    progress: float | None = None,
    sparkline: Sequence[float] | None = None,
    color: str = "#2E86AB",
) -> None:
    """Draw a single KPI card."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Background card
    ax.add_patch(FancyBboxPatch(
        (0.02, 0.02), 0.96, 0.96,
        boxstyle="round,pad=0.02",
        facecolor=color, alpha=0.1,
        edgecolor=color, linewidth=1.5,
        zorder=1,
    ))

    # Label
    ax.text(0.08, 0.85, label, fontsize=9, color="#666666",
            fontweight="bold", zorder=3, va="top")

    # Value
    ax.text(0.08, 0.6, str(value), fontsize=22, color=color,
            fontweight="bold", zorder=3, va="top")

    # Change indicator
    if change:
        change_color = "#2D6A4F" if change_dir == "up" else "#C73E1D"
        arrow = "▲" if change_dir == "up" else "▼"
        ax.text(0.08, 0.4, f"{arrow} {change}", fontsize=9,
                color=change_color, fontweight="bold", zorder=3, va="top")

    # Target
    if target:
        ax.text(0.08, 0.3, f"Target: {target}", fontsize=8,
                color="#888888", zorder=3, va="top")

    # Progress bar
    if progress is not None:
        bar_y = 0.12
        bar_h = 0.06
        bg = ax.add_patch(Rectangle(
            (0.08, bar_y), 0.84, bar_h,
            facecolor="#E0E0E0", edgecolor="none", zorder=2,
        ))
        fg = ax.add_patch(Rectangle(
            (0.08, bar_y), 0.84 * progress, bar_h,
            facecolor=color, edgecolor="none", alpha=0.7, zorder=3,
        ))
        ax.text(0.95, bar_y + bar_h / 2, f"{progress*100:.0f}%",
                fontsize=7, color="#666666", ha="right",
                va="center", zorder=4)

    # Sparkline
    if sparkline is not None and len(sparkline) > 1:
        sl_ax = ax.inset_axes([0.05, 0.65, 0.45, 0.2])
        sl_ax.plot(sparkline, color=color, linewidth=1.5, alpha=0.8)
        sl_ax.fill_between(range(len(sparkline)), sparkline, alpha=0.1, color=color)
        sl_ax.axis("off")


def kpi_card(
    label: str,
    value: str | float,
    change: str = "",
    change_dir: str = "up",
    target: str | None = None,
    progress: float | None = None,
    sparkline: Sequence[float] | None = None,
    color: str = "#2E86AB",
    figsize: tuple = (3.5, 2.5),
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Single KPI metric card.

    Parameters
    ----------
    label : str
        Metric name.
    value : str or float
        Current value.
    change : str
        Change indicator (e.g. '+5.2%').
    change_dir : str
        'up' or 'down'.
    target : str, optional
        Target value.
    progress : float 0-1, optional
        Progress bar value.
    sparkline : list, optional
        Sparkline data points.
    color : str
        Accent color.
    """
    fig, ax = setup_figure(figsize)
    _draw_kpi_card(
        ax, label=label, value=value, change=change,
        change_dir=change_dir, target=target,
        progress=progress, sparkline=sparkline,
        color=color,
    )
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  BULLET  CHART
# ──────────────────────────────────────────────

def bullet_chart(
    actual: float | Sequence,
    target: float | Sequence,
    min_val: float = 0,
    max_val: float | None = None,
    title: str = "Bullet Chart",
    xlabel: str | None = None,
    ylabel: str | None = None,
    figsize: tuple = (4, 3),
    actual_color: str = "#2E86AB",
    target_color: str = "#333333",
    benchmark_color: str = "#CCCCCC",
    good_color: str = "#E8F5E9",
    ok_color: str = "#FFF9C4",
    poor_color: str = "#FFEBEE",
    benchmarks: Sequence[float] | None = None,
    labels: Sequence[str] | None = None,
    show_values: bool = True,
    value_fontsize: float = 9,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Bullet chart for target vs actual comparison.

    Parameters
    ----------
    actual : float
        Actual value.
    target : float
        Target value.
    min_val, max_val : float
        Scale range.
    benchmarks : list of float, optional
        Benchmark lines.
    labels : list of str, optional
        Row labels when ``actual``/``target`` are lists (multi-bullet).
    good_color, ok_color, poor_color : str
        Background colors for target ranges.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    multi = not np.isscalar(actual)
    actuals = list(actual) if multi else [actual]
    targets = list(target) if not np.isscalar(target) else [target] * len(actuals)
    if labels is None and isinstance(actual, (list, tuple)) and all(
            isinstance(v, str) for v in actual):
        labels = list(actual)
        actuals = [v for v in actual if not isinstance(v, str)]
    n = len(actuals)

    if max_val is None:
        max_val = max(max(abs(a), abs(t)) for a, t in zip(actuals, targets)) * 1.2

    ax.set_xlim(min_val, max_val)
    ax.set_ylim(0, n)
    ax.axis("off")

    # Background ranges (target zones), one row band per bullet
    range1 = min_val + (max_val - min_val) / 3
    range2 = min_val + 2 * (max_val - min_val) / 3

    for r in range(n):
        y0, y1 = r, r + 1
        ax.add_patch(Rectangle(
            (min_val, y0 + 0.1), range1 - min_val, 0.8,
            facecolor=poor_color, edgecolor="none", zorder=1,
        ))
        ax.add_patch(Rectangle(
            (range1, y0 + 0.1), range2 - range1, 0.8,
            facecolor=ok_color, edgecolor="none", zorder=1,
        ))
        ax.add_patch(Rectangle(
            (range2, y0 + 0.1), max_val - range2, 0.8,
            facecolor=good_color, edgecolor="none", zorder=1,
        ))

        # Benchmark bars
        if benchmarks:
            for bm in benchmarks:
                ax.plot([bm, bm], [r + 0.42, r + 0.62],
                        color=benchmark_color, linewidth=3.5, zorder=3)

        # Actual bar
        actual_val, target_val = actuals[r], targets[r]
        ax.add_patch(Rectangle(
            (min_val, y0 + 0.42), actual_val - min_val, 0.22,
            facecolor=actual_color, edgecolor="white", linewidth=1,
            alpha=0.9, zorder=4,
        ))
        # Target line
        ax.plot([target_val, target_val], [y0 + 0.28, y0 + 0.78],
                color=target_color, linewidth=2.2, zorder=5)

        if labels is not None and r < len(labels):
            ax.text(min_val - (max_val - min_val) * 0.015, y0 + 0.5,
                    str(labels[r]), ha="right", va="center",
                    fontsize=value_fontsize + 1, color="#333333", zorder=6)
        if show_values:
            ax.text(actual_val + (max_val - min_val) * 0.015, y0 + 0.5,
                    f"{actual_val:.2f}", fontsize=value_fontsize,
                    color=actual_color, fontweight="bold", va="center",
                    zorder=6)
            ax.text(target_val, y0 + 0.86, f"{target_val:.2f}",
                    fontsize=value_fontsize - 1, color=target_color,
                    ha="center", va="bottom", zorder=6)

    if title:
        ax.set_title(title, fontsize=11, fontweight="bold",
                     pad=8, x=0.62 if labels else 0.5)
    if xlabel:
        ax.text(0.5, -0.15, xlabel, transform=ax.transAxes,
                fontsize=9, ha="center", color="#666666")

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SPARKLINE
# ──────────────────────────────────────────────

def sparkline(
    values: Sequence[float],
    title: str | None = None,
    figsize: tuple = (3, 1),
    color: str = "#2E86AB",
    fill_alpha: float = 0.2,
    line_width: float = 1.5,
    show_end_dot: bool = True,
    show_values: bool = False,
    value_fontsize: float = 7,
    show_min_max: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Compact sparkline for quick trend display.

    Parameters
    ----------
    values : list of float
        Data points.
    show_end_dot : bool
        Show a dot at the last data point.
    show_min_max : bool
        Show min and max value labels.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    vals = np.array(values, dtype=float)

    ax.plot(range(len(vals)), vals, color=color, linewidth=line_width, zorder=3)
    ax.fill_between(range(len(vals)), vals, alpha=fill_alpha, color=color, zorder=2)

    if show_end_dot and len(vals) > 0:
        ax.scatter(
            len(vals) - 1, vals[-1], c=color, s=30,
            edgecolors="white", linewidth=0.8, zorder=5,
        )

    if show_min_max and len(vals) > 0:
        min_val = vals.min()
        max_val = vals.max()
        min_idx = np.argmin(vals)
        max_idx = np.argmax(vals)
        ax.text(min_idx, min_val, f"{min_val:.2f}", fontsize=value_fontsize,
                color="#666666", va="top", ha="center", zorder=4)
        ax.text(max_idx, max_val, f"{max_val:.2f}", fontsize=value_fontsize,
                color="#666666", va="bottom", ha="center", zorder=4)

    if show_values and len(vals) > 0:
        ax.text(len(vals) - 0.1, vals[-1], f"{vals[-1]:.2f}",
                fontsize=value_fontsize, color=color,
                fontweight="bold", va="center", ha="right", zorder=5)

    if title:
        ax.set_title(title, fontsize=9, fontweight="bold", pad=4)

    ax.set_xlim(-0.5, len(vals) + 0.5)
    y_min = vals.min() - (vals.max() - vals.min()) * 0.15
    y_max = vals.max() + (vals.max() - vals.min()) * 0.15
    ax.set_ylim(y_min, y_max)

    ax.axis("off")
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  GAUGE
# ──────────────────────────────────────────────

def gauge(
    value: float,
    min_val: float = 0,
    max_val: float = 100,
    label: str = "",
    title: str = "Gauge",
    figsize: tuple = (4, 3),
    gauge_color: str = "#2E86AB",
    background_color: str = "#E0E0E0",
    needle_color: str = "#333333",
    value_fontsize: float = 20,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Gauge / speedometer visualization.

    Parameters
    ----------
    value : float
        Current value.
    min_val, max_val : float
        Gauge range.
    label : str
        Value label below the gauge.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.3, 1.2)
    ax.axis("off")
    ax.set_aspect("equal")

    # Background arc
    for i in range(100):
        theta1 = 180 - (i + 1) * 1.8
        theta2 = 180 - i * 1.8
        if i < (value - min_val) / (max_val - min_val) * 100:
            color = gauge_color
        else:
            color = background_color
        ax.add_patch(Wedge(
            (0, 0), 1.0, theta1, theta2,
            width=0.15, facecolor=color, edgecolor="none",
        ))

    # Inner arc
    for i in range(100):
        theta1 = 180 - (i + 1) * 1.8
        theta2 = 180 - i * 1.8
        ax.add_patch(Wedge(
            (0, 0), 0.8, theta1, theta2,
            width=0.02, facecolor="#CCCCCC", edgecolor="none",
        ))

    # Center dot
    ax.add_patch(Circle((0, 0), 0.08, facecolor=needle_color, edgecolor="white", linewidth=1))

    # Value text
    ax.text(0, 0.3, f"{value:.1f}", fontsize=value_fontsize,
            color=gauge_color, fontweight="bold", ha="center", va="center")

    if label:
        ax.text(0, 0.05, label, fontsize=9, color="#666666",
                ha="center", va="center")

    # Min/Max labels
    ax.text(-1.05, -0.05, f"{min_val}", fontsize=8, color="#999999",
            ha="center", va="center")
    ax.text(1.05, -0.05, f"{max_val}", fontsize=8, color="#999999",
            ha="center", va="center")

    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", pad=5)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PROCESS  FLOW
# ──────────────────────────────────────────────

def process_flow(
    steps: Sequence[str],
    title: str = "Process Flow",
    figsize: tuple | None = None,
    palette: str = "nature_qual",
    horizontal: bool = True,
    font_size: float = 11,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Process flow diagram with connected steps.

    Parameters
    ----------
    steps : list of str
        Step names.
    horizontal : bool
        Horizontal (default) or vertical flow.
    """
    n = len(steps)
    if figsize is None:
        figsize = (max(6, n * 2.0), 3) if horizontal else (4, max(6, n * 1.5))

    fig, ax = setup_figure(figsize, **kwargs)
    colors = auto_colors(n, palette)

    ax.set_xlim(-0.5, n + 0.5 if horizontal else 1.5)
    ax.set_ylim(-0.5, 1.5 if horizontal else n + 0.5)
    ax.axis("off")

    if horizontal:
        for i, (step, color) in enumerate(zip(steps, colors)):
            x = i
            # Box
            ax.add_patch(FancyBboxPatch(
                (x - 0.4, 0.2), 0.8, 0.6,
                boxstyle="round,pad=0.05",
                facecolor=color, alpha=0.85,
                edgecolor="white", linewidth=2, zorder=3,
            ))
            # Number
            ax.text(x, 0.65, f"Step {i+1}", fontsize=font_size - 2,
                    color="white", ha="center", va="center",
                    fontweight="bold", zorder=4)
            # Label
            ax.text(x, 0.45, step, fontsize=font_size,
                    color="white", ha="center", va="center",
                    fontweight="bold", zorder=4)
            # Arrow
            if i < n - 1:
                ax.annotate(
                    "", xy=(i + 1 - 0.4, 0.5),
                    xytext=(i + 0.4, 0.5),
                    arrowprops=dict(
                        arrowstyle="-|>", color="#666666",
                        lw=2, connectionstyle="arc3,rad=0",
                    ),
                    zorder=2,
                )
    else:
        for i, (step, color) in enumerate(zip(steps, colors)):
            y = n - 1 - i
            ax.add_patch(FancyBboxPatch(
                (0.1, y + 0.1), 1.2, 0.6,
                boxstyle="round,pad=0.05",
                facecolor=color, alpha=0.85,
                edgecolor="white", linewidth=2, zorder=3,
            ))
            ax.text(0.7, y + 0.55, f"Step {i+1}", fontsize=font_size - 2,
                    color="white", ha="center", va="center",
                    fontweight="bold", zorder=4)
            ax.text(0.7, y + 0.35, step, fontsize=font_size,
                    color="white", ha="center", va="center",
                    fontweight="bold", zorder=4)
            if i < n - 1:
                ax.annotate(
                    "", xy=(0.7, y - 0.1),
                    xytext=(0.7, y + 0.1),
                    arrowprops=dict(
                        arrowstyle="-|>", color="#666666",
                        lw=2,
                    ),
                    zorder=2,
                )

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  MIND  MAP
# ──────────────────────────────────────────────

def mind_map(
    center: str,
    branches: Sequence[dict],
    title: str = "Mind Map",
    figsize: tuple = (10, 8),
    palette: str = "nature_qual",
    center_fontsize: float = 14,
    branch_fontsize: float = 11,
    sub_fontsize: float = 9,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Mind map visualization.

    Parameters
    ----------
    center : str
        Central topic.
    branches : list of dict
        Each dict has:
            'label' : str — Branch topic
            'items' : list of str — Sub-items
    """
    fig, ax = setup_figure(figsize, **kwargs)

    n_branches = len(branches)
    colors = auto_colors(n_branches, palette)

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis("off")
    ax.set_aspect("equal")

    # Central node
    ax.add_patch(FancyBboxPatch(
        (-0.25, -0.15), 0.5, 0.3,
        boxstyle="round,pad=0.05",
        facecolor="#2E86AB", edgecolor="white", linewidth=2,
        zorder=5,
    ))
    ax.text(0, 0, center, fontsize=center_fontsize,
            color="white", ha="center", va="center",
            fontweight="bold", zorder=6)

    # Branches
    angle_step = 2 * np.pi / n_branches
    for i, (branch, color) in enumerate(zip(branches, colors)):
        angle = angle_step * i + np.pi / 2
        r = 0.7
        bx = r * np.cos(angle)
        by = r * np.sin(angle)

        # Line to branch
        ax.plot([0, bx], [0, by], color=color, linewidth=2.5,
                alpha=0.7, zorder=2)

        # Branch node
        ax.add_patch(FancyBboxPatch(
            (bx - 0.15, by - 0.1), 0.3, 0.2,
            boxstyle="round,pad=0.03",
            facecolor=color, alpha=0.85,
            edgecolor="white", linewidth=1.5, zorder=4,
        ))
        ax.text(bx, by, branch["label"], fontsize=branch_fontsize,
                color="white", ha="center", va="center",
                fontweight="bold", zorder=5)

        # Sub-items
        items = branch.get("items", [])
        if items:
            n_items = len(items)
            spread = 0.15
            for j, item in enumerate(items):
                item_angle = angle + (j - (n_items - 1) / 2) * 0.2
                ir = r + 0.4
                ix = ir * np.cos(item_angle)
                iy = ir * np.sin(item_angle)

                # Sub line
                ax.plot([bx, ix], [by, iy], color=color,
                        linewidth=1.2, alpha=0.5, zorder=2)

                # Sub node
                ax.add_patch(FancyBboxPatch(
                    (ix - 0.12, iy - 0.06), 0.24, 0.12,
                    boxstyle="round,pad=0.02",
                    facecolor=color, alpha=0.2,
                    edgecolor=color, linewidth=1, zorder=3,
                ))
                ax.text(ix, iy, item, fontsize=sub_fontsize,
                        color="#333333", ha="center", va="center",
                        zorder=4)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  COMPARISON  BAR  (with target line)
# ──────────────────────────────────────────────

def comparison_bar(
    labels: Sequence[str],
    values: Sequence[float],
    target: float | None = None,
    title: str = "Comparison",
    xlabel: str | None = None,
    ylabel: str | None = None,
    figsize: tuple = (8, 5),
    palette: str = "nature_qual",
    target_color: str = "#C73E1D",
    target_label: str = "Target",
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Comparison bar chart with target reference line.

    Parameters
    ----------
    labels : list of str
        Category labels.
    values : list of float
        Values to compare.
    target : float, optional
        Target threshold line.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    colors = auto_colors(len(labels), palette)

    bars = ax.bar(
        range(len(labels)), values,
        color=colors, edgecolor="white", linewidth=0.8,
        width=0.6, alpha=0.85,
    )

    if target is not None:
        ax.axhline(y=target, color=target_color, linestyle="--",
                   linewidth=1.5, alpha=0.8, label=target_label)
        ax.text(len(labels) - 0.5, target + max(values) * 0.02,
                f"{target_label}: {target:.2f}",
                fontsize=9, color=target_color, ha="right",
                fontweight="bold")

    if show_values:
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + max(values) * 0.02,
                    value_fmt.format(val), ha="center",
                    va="bottom", fontsize=8, color="#333333",
                    fontweight="bold")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if target is not None:
        ax.legend(frameon=False, fontsize=9)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DONUT  PROGRESS  RINGS
# ──────────────────────────────────────────────

def donut_rings(
    values: Sequence[float],
    labels: Sequence[str] | None = None,
    title: str | None = None,
    figsize: tuple = (6.5, 6.5),
    palette: str = "nature_qual",
    center_text: str | None = None,
    ring_width: float = 0.16,
    gap_deg: float = 3,
    track_color: str = "#EEEEEE",
    show_pct: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Concentric progress rings — dashboard-style completion view of
    several KPIs (each value in [0, 1], or normalized automatically).

    Returns
    -------
    Figure
    """
    vals = np.asarray(values, float).ravel()
    if vals.max() > 1.0:
        vals = vals / vals.max()
    vals = np.clip(vals, 0, 1)
    n = len(vals)
    labels = list(labels) if labels else [f"KPI {i + 1}" for i in range(n)]
    colors = auto_colors(n, palette)

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.set_aspect("equal")
    ax.axis("off")

    for i, (v, col, lab) in enumerate(zip(vals, colors, labels)):
        r_outer = 1.0 - i * (ring_width + 0.035)
        r_inner = r_outer - ring_width
        theta_track = np.linspace(gap_deg, 360 - gap_deg, 200)
        ax.fill(
            np.r_[r_outer * np.cos(np.deg2rad(theta_track)),
                  (r_inner * np.cos(np.deg2rad(theta_track)))[::-1]],
            np.r_[r_outer * np.sin(np.deg2rad(theta_track)),
                  (r_inner * np.sin(np.deg2rad(theta_track)))[::-1]],
            color=track_color, lw=0, zorder=1,
        )
        theta_v = np.linspace(90 + gap_deg, 90 + gap_deg + (360 - 2 * gap_deg) * v, 200)
        ax.fill(
            np.r_[r_outer * np.cos(np.deg2rad(theta_v)),
                  (r_inner * np.cos(np.deg2rad(theta_v)))[::-1]],
            np.r_[r_outer * np.sin(np.deg2rad(theta_v)),
                  (r_inner * np.sin(np.deg2rad(theta_v)))[::-1]],
            color=col, lw=0, zorder=2,
        )
        mid_r = (r_outer + r_inner) / 2
        label_ang = np.deg2rad(90 + gap_deg + (360 - 2 * gap_deg) * v)
        if show_pct:
            ax.text(mid_r * np.cos(label_ang - 0.22),
                    mid_r * np.sin(label_ang - 0.22), f"{v:.0%}",
                    ha="center", va="center", fontsize=8, color=col,
                    fontweight="bold", zorder=3)
        ax.text(0, mid_r, lab, ha="center", va="center", fontsize=8.5,
                color="#333333", zorder=3)

    if center_text:
        ax.text(0, 0, center_text, ha="center", va="center",
                fontsize=13, fontweight="bold", color="#1D3557")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "dashboard", "kpi_card", "bullet_chart",
    "sparkline", "gauge", "process_flow",
    "mind_map", "comparison_bar", "donut_rings", "risk_matrix",
]


# ──────────────────────────────────────────────
#  RISK  MATRIX  (probability x impact)
# ──────────────────────────────────────────────

def risk_matrix(
    risks: dict,
    title: str = "Risk Matrix",
    figsize: tuple = (8.5, 6.5),
    x_label: str = "Impact",
    y_label: str = "Probability",
    x_levels: int = 5,
    y_levels: int = 5,
    palette: str = "RdYlGn_r",
    label_size: float = 7.5,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Risk matrix — items placed on a probability × impact grid with a
    green-to-red background. ``risks`` maps item name to
    ``(impact 1-5, probability 1-5)``.

    Returns
    -------
    Figure
    """
    from matplotlib.colors import LinearSegmentedColormap

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    # background score grid (impact + probability)
    bg = np.add.outer(np.arange(1, y_levels + 1), np.arange(1, x_levels + 1))
    cmap = LinearSegmentedColormap.from_list(
        "risk", ["#7CC576", "#F5D76E", "#E74C3C"])
    ax.imshow(bg, cmap=cmap, origin="lower", alpha=0.75,
              extent=(0.5, x_levels + 0.5, 0.5, y_levels + 0.5),
              aspect="auto")

    cell_counts: dict = {}
    for name, (imp, prob) in risks.items():
        key = (int(round(imp)), int(round(prob)))
        cell_counts.setdefault(key, []).append(str(name))

    n_cells = max(len(v) for v in cell_counts.values()) if cell_counts else 1
    for (imp, prob), names in cell_counts.items():
        offsets = np.linspace(-0.18 * (len(names) - 1), 0.18 * (len(names) - 1),
                              len(names))
        for dx, name in zip(offsets, names):
            ax.plot(imp, prob, "o", ms=11, mfc="white", mec="#333333",
                    mew=1.1, zorder=4)
            ax.text(imp, prob + 0.13, name, ha="center", va="bottom",
                    fontsize=label_size, color="#1A1A1A", zorder=5)

    ax.set_xticks(range(1, x_levels + 1))
    ax.set_yticks(range(1, y_levels + 1))
    ax.set_xticklabels(["Very low", "Low", "Medium", "High", "Very high"][:x_levels],
                       fontsize=8.5)
    ax.set_yticklabels(["Very low", "Low", "Medium", "High", "Very high"][:y_levels],
                       fontsize=8.5)
    ax.set_xlim(0.5, x_levels + 0.5)
    ax.set_ylim(0.5, y_levels + 0.5)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(color="white", lw=1.5)
    ax.set_axisbelow(False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig
