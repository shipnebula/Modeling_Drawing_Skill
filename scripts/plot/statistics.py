"""
statistics.py — Statistical charts for data analysis sections.

Charts:
    qq_plot             — quantile-quantile normality check
    ecdf_plot           — empirical CDF (single or grouped)
    ridgeline           — joyplot of many distributions
    hexbin_plot         — hexagonal binning of large scatter
    stem_plot           — stem / lollipop chart
    errorbar_chart      — means with error bars
    bubble_chart        — scatter with size dimension
    bump_chart          — rank changes over time
    stream_graph        — smoothed stacked area (centered)
    funnel_chart        — stage-by-stage funnel
    waffle_chart        — 10×10 pictogram grid
    population_pyramid  — two-sided distribution pyramid
    sunburst_chart      — two-ring hierarchical donut
    icicle_chart        — hierarchical nested rectangles
    mosaic_plot         — categorical proportion (Marimekko)
    dendrogram          — hierarchical clustering tree
    distribution_panel  — hist + box + violin + QQ in one figure
    scatter_matrix      — pairwise scatter with KDE/hist diagonal

All functions return a matplotlib Figure ready for publication.
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .palette import auto_colors, get_palette, blend, lightness, contrast_color
from .utils import (
    setup_figure, save_figure, axis_config, format_numbers,
    add_data_labels,
)


def _to_1d(data) -> np.ndarray:
    return np.asarray(data, dtype=float).ravel()



def _vert_kw(vertical: bool = True) -> dict:
    """Compat kwarg for box/violin orientation across matplotlib versions."""
    import matplotlib
    major, minor = (int(x) for x in matplotlib.__version__.split(".")[:2])
    if (major, minor) >= (3, 11):
        return {"orientation": "vertical" if vertical else "horizontal"}
    return {"vert": vertical}


def _kde(values: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Gaussian KDE with graceful fallback to smoothed histogram."""
    try:
        from scipy.stats import gaussian_kde
        return gaussian_kde(values)(grid)
    except Exception:
        hist, edges = np.histogram(values, bins=min(40, max(10, len(values) // 5)),
                                   density=True)
        centers = (edges[:-1] + edges[1:]) / 2
        return np.interp(grid, centers, hist)


# ──────────────────────────────────────────────
#  Q-Q  PLOT
# ──────────────────────────────────────────────

def qq_plot(
    data,
    dist: str = "norm",
    title: str | None = None,
    xlabel: str = "Theoretical quantiles",
    ylabel: str = "Sample quantiles",
    figsize: tuple = (6, 6),
    color: str = "#2E86AB",
    line_color: str = "#C73E1D",
    marker_size: float = 28,
    show_band: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Quantile-quantile plot against a theoretical distribution.

    Parameters
    ----------
    data : array-like
        Sample values.
    dist : str
        scipy.stats distribution name: 'norm', 'expon', 'uniform', ...

    Returns
    -------
    Figure
    """
    from scipy import stats as sps

    values = _to_1d(data)
    values = values[~np.isnan(values)]
    (osm, osr), (slope, intercept, r) = sps.probplot(values, dist=dist)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.scatter(osm, osr, s=marker_size, color=color, alpha=0.75,
               edgecolors="white", lw=0.5, zorder=3)
    ax.plot(osm, slope * osm + intercept, color=line_color, lw=1.8,
            label=f"fit  R² = {r ** 2:.4f}", zorder=4)

    if show_band:
        spread = np.std(osr - (slope * osm + intercept))
        ax.fill_between(osm, slope * osm + intercept - 2 * spread,
                        slope * osm + intercept + 2 * spread,
                        color=line_color, alpha=0.12, lw=0,
                        label="±2σ band")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="upper left")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ECDF
# ──────────────────────────────────────────────

def ecdf_plot(
    data,
    title: str | None = None,
    xlabel: str = "value",
    ylabel: str = "Empirical CDF",
    figsize: tuple = (7.5, 5),
    palette: str = "nature_qual",
    show_markers: bool = False,
    show_median: bool = True,
    names: Sequence[str] | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Empirical CDF for one sample or ``{name: sample}`` groups.

    Returns
    -------
    Figure
    """
    groups = data if isinstance(data, dict) else {(names[0] if names else "Sample"): data}
    if names and not isinstance(data, dict):
        groups = dict(zip(names, data))

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(len(groups), palette)

    for i, (name, values) in enumerate(groups.items()):
        v = np.sort(_to_1d(values))
        v = v[~np.isnan(v)]
        p = np.arange(1, len(v) + 1) / len(v)
        ax.step(v, p, where="post", color=colors[i % len(colors)],
                lw=1.9, label=str(name))
        if show_markers and len(v) <= 60:
            ax.plot(v, p, "o", ms=3, color=colors[i % len(colors)])
        if show_median:
            med = np.median(v)
            ax.plot([med, med], [0, 0.5], color=colors[i % len(colors)],
                    lw=0.8, ls=":", alpha=0.7)
            ax.plot(med, 0.5, "v", ms=5,
                    color=colors[i % len(colors)], zorder=5)

    ax.set_ylim(0, 1.02)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="lower right")
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  RIDGELINE
# ──────────────────────────────────────────────

def ridgeline(
    data,
    title: str | None = None,
    xlabel: str = "value",
    figsize: tuple = (8.5, 6),
    palette: str = "nature_qual",
    overlap: float = 0.72,
    bandwidth_scale: float = 1.0,
    show_labels: bool = True,
    n_points: int = 240,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Ridgeline (joy) plot — stacked density curves for many groups.

    Parameters
    ----------
    data : dict
        ``{group_name: sample_values}`` in top-to-bottom order.
    overlap : float
        Vertical overlap between curves (0–1, higher = more overlap).

    Returns
    -------
    Figure
    """
    if not isinstance(data, dict) or not data:
        raise ValueError("ridgeline expects a non-empty dict {name: values}.")

    names = list(data.keys())
    samples = [_to_1d(v) for v in data.values()]
    lo = min(np.nanmin(s) for s in samples)
    hi = max(np.nanmax(s) for s in samples)
    pad = 0.08 * (hi - lo or 1)
    grid = np.linspace(lo - pad, hi + pad, n_points)

    colors = auto_colors(len(names), palette)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    step = (1 - overlap) * 0.9
    for i, (name, s) in enumerate(zip(names, samples)):
        dens = _kde(s, grid)
        dens = dens / dens.max() * 0.9
        base = len(names) - 1 - i * step
        face = blend(colors[i % len(colors)], "#FFFFFF", 0.25)
        ax.plot(grid, base + dens, color=colors[i % len(colors)],
                lw=1.4, zorder=3 + i)
        ax.fill_between(grid, base, base + dens, color=face,
                        alpha=0.95, lw=0, zorder=2 + i)
        if show_labels:
            ax.text(grid[0] - pad * 1.5, base + 0.08, str(name),
                    ha="right", va="bottom", fontsize=9,
                    color="#333333", zorder=10)

    ax.set_xlim(grid[0] - pad * (4 if show_labels else 0.5), grid[-1])
    top_base = len(names) - 1
    bottom_base = top_base - (len(names) - 1) * step
    ax.set_ylim(bottom_base - 0.35, top_base + 1.15)
    ax.set_yticks([])
    for spine in ("left", "top", "right"):
        ax.spines[spine].set_visible(False)
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  HEXBIN
# ──────────────────────────────────────────────

def hexbin_plot(
    x,
    y,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (7.5, 5.5),
    cmap: str = "viridis",
    gridsize: int = 38,
    show_colorbar: bool = True,
    cbar_label: str = "count",
    mincnt: int = 1,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Hexagonal binning — the honest way to plot hundreds of thousands
    of points.

    Returns
    -------
    Figure
    """
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    hb = ax.hexbin(np.asarray(x, float), np.asarray(y, float),
                   gridsize=gridsize, cmap=cmap, mincnt=mincnt, lw=0.1)
    if show_colorbar:
        cb = fig.colorbar(hb, ax=ax, shrink=0.9, pad=0.02)
        cb.set_label(cbar_label, fontsize=9)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="none")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  STEM / LOLLIPOP
# ──────────────────────────────────────────────

def stem_plot(
    x,
    y=None,
    title: str | None = None,
    xlabel: str = "",
    ylabel: str = "",
    labels: Sequence[str] | None = None,
    figsize: tuple = (8, 4.5),
    color: str = "#2E86AB",
    base_color: str = "#BBBBBB",
    marker_size: float = 42,
    show_values: bool = False,
    value_fmt: str = "{:.2f}",
    horizontal: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Lollipop chart — cleaner than a bar chart when values are close.

    Returns
    -------
    Figure
    """
    if y is None:
        x, y = np.arange(len(x)), x
    x, y = np.asarray(x), np.asarray(y, float)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.axhline if not horizontal else ax.axvline
    ax.plot([x.min() - 0.6, x.max() + 0.6] if not horizontal else [0, 0],
            [0, 0] if not horizontal else [x.min() - 0.6, x.max() + 0.6],
            color=base_color, lw=1, zorder=1) if False else None

    if horizontal:
        ax.hlines(x, 0, y, color=color, lw=2, alpha=0.85, zorder=2)
        ax.scatter(y, x, s=marker_size, color=color, zorder=3,
                   edgecolors="white", lw=0.8)
        if labels is not None:
            ax.set_yticks(x)
            ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlim(0, np.nanmax(y) * 1.12)
        ax.set_xlabel(ylabel or ylabel)
        if show_values:
            for xi, yi in zip(x, y):
                ax.text(yi + np.nanmax(y) * 0.015, xi, value_fmt.format(yi),
                        va="center", fontsize=8, color="#333333")
    else:
        ax.vlines(x, 0, y, color=color, lw=2, alpha=0.85, zorder=2)
        ax.scatter(x, y, s=marker_size, color=color, zorder=3,
                   edgecolors="white", lw=0.8)
        if labels is not None:
            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, np.nanmax(y) * 1.12)
        if show_values:
            for xi, yi in zip(x, y):
                ax.text(xi, yi + np.nanmax(y) * 0.015, value_fmt.format(yi),
                        ha="center", fontsize=8, color="#333333")

    ax.set_ylabel(ylabel) if not horizontal else ax.set_xlabel(ylabel)
    axis_config(ax, grid="y" if not horizontal else "x")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ERRORBAR
# ──────────────────────────────────────────────

def errorbar_chart(
    x,
    y,
    yerr=None,
    title: str | None = None,
    xlabel: str = "",
    ylabel: str = "",
    labels: Sequence[str] | None = None,
    figsize: tuple = (8, 5),
    color: str = "#2E86AB",
    capsize: float = 4,
    marker: str = "o",
    marker_size: float = 6,
    line: bool = True,
    palette: str | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Means with error bars — the workhorse of experimental reports.

    Parameters
    ----------
    x : categories or numeric x
    y : mean values
    yerr : scalar, array, or (2, n) asymmetric errors

    Returns
    -------
    Figure
    """
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    is_categorical = labels is not None or not isinstance(x[0] if x is not None else y, (int, float))
    xpos = np.arange(len(y)) if is_categorical else np.asarray(x, float)

    color_list = auto_colors(len(y), palette) if palette else None
    if color_list:
        colors = color_list
        edge = None
    else:
        colors, edge = color, "white"

    ax.errorbar(
        xpos, np.asarray(y, float), yerr=yerr, fmt=marker,
        ms=marker_size, color=color if not color_list else colors[0],
        ecolor="#666666", elinewidth=1.1, capsize=capsize,
        capthick=1.1, mfc=color, mec="white", mew=0.8,
        ls="-" if line else "none", lw=1.4, zorder=3,
    )
    if is_categorical and labels is not None:
        ax.set_xticks(xpos)
        ax.set_xticklabels(labels, fontsize=9)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  BUBBLE
# ──────────────────────────────────────────────

def bubble_chart(
    x,
    y,
    sizes=None,
    labels: Sequence[str] | None = None,
    names: Sequence[str] | None = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 5.5),
    palette: str = "nature_qual",
    size_range: tuple = (80, 1400),
    alpha: float = 0.65,
    show_legend: bool = True,
    edge_color: str = "white",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Bubble chart — three dimensions on one scatter (x, y, size).

    Parameters
    ----------
    sizes : array-like, optional
        Bubble areas; auto-scaled into ``size_range``.

    Returns
    -------
    Figure
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if sizes is None:
        sizes = np.full(len(x), np.mean(size_range))
    sizes = np.asarray(sizes, float)
    smin, smax = sizes.min(), sizes.max()
    if smax > smin:
        sizes = size_range[0] + (sizes - smin) / (smax - smin) * (
            size_range[1] - size_range[0]
        )
    else:
        sizes = np.full(len(x), np.mean(size_range))

    if names is not None:
        cats = list(dict.fromkeys(names))
        cmap = auto_colors(len(cats), palette)
        for i, cat in enumerate(cats):
            idx = [j for j, n in enumerate(names) if n == cat]
            ax.scatter(x[idx], y[idx], s=sizes[idx], color=cmap[i],
                       alpha=alpha, edgecolors=edge_color, lw=0.8,
                       label=str(cat), zorder=3)
    else:
        ax.scatter(x, y, s=sizes, color=auto_colors(1, palette)[0],
                   alpha=alpha, edgecolors=edge_color, lw=0.8, zorder=3)

    if labels is not None:
        for xi, yi, lab in zip(x, y, labels):
            ax.annotate(str(lab), (xi, yi), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=7.5,
                        color="#333333")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="both")
    if show_legend and names is not None:
        ax.legend(frameon=False, loc="best")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  BUMP  CHART
# ──────────────────────────────────────────────

def bump_chart(
    ranks,
    title: str | None = None,
    xlabel: str = "Time",
    ylabel: str = "Rank",
    figsize: tuple = (8.5, 5.5),
    palette: str = "nature_qual",
    linewidth: float = 2.2,
    marker_size: float = 46,
    show_rank_labels: bool = True,
    invert_y: bool = True,
    x_labels: Sequence[str] | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Bump chart — how rankings shuffle across time points.

    Parameters
    ----------
    ranks : dict
        ``{name: [rank at t1, rank at t2, ...]}``.

    Returns
    -------
    Figure
    """
    if not isinstance(ranks, dict) or not ranks:
        raise ValueError("bump_chart expects {name: [ranks over time]}.")
    names = list(ranks.keys())
    matrix = np.asarray([ranks[n] for n in names], dtype=float)
    n_time = matrix.shape[1]

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(len(names), palette)
    xs = np.arange(n_time)

    for i, name in enumerate(names):
        ax.plot(xs, matrix[i], color=colors[i % len(colors)], lw=linewidth,
                solid_capstyle="round", zorder=3)
        ax.scatter(xs, matrix[i], s=marker_size, color=colors[i % len(colors)],
                   edgecolors="white", lw=1.2, zorder=4)
        ax.annotate(str(name), (xs[-1] + 0.08, matrix[i, -1]),
                    va="center", fontsize=8.5,
                    color=colors[i % len(colors)], zorder=5)
        if show_rank_labels:
            ax.annotate(str(name), (xs[0] - 0.08, matrix[i, 0]),
                        va="center", ha="right", fontsize=8.5,
                        color=colors[i % len(colors)])

    ax.set_xticks(xs)
    if x_labels:
        ax.set_xticklabels(x_labels, fontsize=9)
    ax.set_xlim(-0.9, n_time - 0.4)
    ax.set_yticks(np.arange(1, len(names) + 1))
    if invert_y:
        ax.invert_yaxis()
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    axis_config(ax, grid="y")
    ax.spines["left"].set_visible(False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  STREAM  GRAPH
# ──────────────────────────────────────────────

def stream_graph(
    data,
    x=None,
    title: str | None = None,
    xlabel: str = "time",
    ylabel: str = "",
    figsize: tuple = (9, 4.8),
    palette: str = "nature_qual",
    baseline: str = "sym",
    alpha: float = 0.88,
    smooth: int = 8,
    show_labels: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Stream graph — flowing stacked areas around a center baseline.

    Parameters
    ----------
    data : dict of ``{name: y_values}``
    x : array-like, optional
        Shared x axis.
    baseline : str
        'sym' (ThemeRiver), 'wiggle' (minimized wiggle) or 'zero'.

    Returns
    -------
    Figure
    """
    if not isinstance(data, dict) or not data:
        raise ValueError("stream_graph expects {name: y_values}.")
    names = list(data.keys())
    M = np.asarray([np.asarray(data[n], float) for n in names])
    n_time = M.shape[1]
    xv = np.asarray(x, float) if x is not None else np.arange(n_time)
    if smooth and n_time > smooth * 2:
        xs = np.linspace(xv.min(), xv.max(), n_time * smooth)
        Ms = np.asarray([
            np.interp(xs, xv, row) for row in M
        ])
    else:
        xs, Ms = xv, M

    cum = np.zeros(len(xs))
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(len(names), palette)

    if baseline == "wiggle":
        # Minimized-wiggle baseline: center each running stack
        base = np.zeros(len(xs))
        for k in range(Ms.shape[0]):
            base = base - Ms[:k + 1].sum(axis=0) / 2.0
        lower_prev = base
    elif baseline == "zero":
        lower_prev = np.zeros(len(xs))
    else:
        total = Ms.sum(axis=0)
        lower_prev = -total / 2.0

    lower_prev = lower_prev.astype(float)
    upper = lower_prev.copy()
    for k, name in enumerate(names):
        lower = upper
        upper = upper + Ms[k]
        ax.fill_between(xs, lower, upper, color=colors[k % len(colors)],
                        alpha=alpha, lw=0.6, edgecolor="white")
        if show_labels and k % max(1, len(names) // 12) == 0:
            mid_idx = len(xs) // 2
            ax.text(xs[mid_idx], (lower[mid_idx] + upper[mid_idx]) / 2,
                    str(name), ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold", zorder=5)

    ax.set_xlim(xs.min(), xs.max())
    ax.set_xlabel(xlabel)
    ax.set_yticks([])
    for spine in ("left", "top", "right"):
        ax.spines[spine].set_visible(False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  FUNNEL
# ──────────────────────────────────────────────

def funnel_chart(
    stages,
    values=None,
    title: str | None = None,
    figsize: tuple = (7.5, 5),
    palette: str = "ocean",
    show_pct: bool = True,
    show_values: bool = True,
    value_fmt: str = "{:,.0f}",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Funnel chart — stage-by-stage drop-off (pipeline, conversion,
    algorithm filtering steps).

    Parameters
    ----------
    stages : list of str, or dict ``{stage: value}``
    values : list of float, optional

    Returns
    -------
    Figure
    """
    if values is None:
        if not isinstance(stages, dict):
            raise ValueError("Pass (stages, values) or a dict {stage: value}.")
        stages, values = list(stages.keys()), list(stages.values())
    stages = [str(s) for s in stages]
    values = np.asarray(values, float)
    n = len(stages)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(n, palette)
    width = values / values.max()

    for i in range(n):
        w0, w1 = width[i], width[min(i + 1, n - 1)]
        y_top = n - 1 - i + 0.42
        y_bot = n - 1 - i - 0.42
        ax.fill_between(
            [-w0 / 2, w0 / 2], y_bot, y_top,
            color=colors[i % len(colors)], lw=0,
        )
        if i < n - 1 and w1 != w0:
            y_next_top = n - 1 - (i + 1) + 0.42
            ax.fill(
                [-w0 / 2, w0 / 2, w1 / 2, -w1 / 2],
                [y_top, y_top, y_next_top, y_next_top],
                color=colors[i % len(colors)], alpha=0.45, lw=0,
            )
        txt = stages[i]
        if show_values:
            txt += f"   {value_fmt.format(values[i])}"
        if show_pct and values.max() > 0:
            txt += f"  ({values[i] / values.max():.0%})"
        color_txt = "#FFFFFF" if width[i] > 0.35 else "#333333"
        ax.text(0, n - 1 - i, txt, ha="center", va="center",
                fontsize=9, color=color_txt, zorder=5)

    ax.set_xlim(-0.62, 0.62)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  WAFFLE
# ──────────────────────────────────────────────

def waffle_chart(
    values,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    figsize: tuple | None = None,
    rows: int = 10,
    cols: int = 10,
    palette: str = "nature_qual",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Waffle (pictogram) chart — proportions as a grid of squares.

    Returns
    -------
    Figure
    """
    values = np.asarray(values, float)
    n_cells = rows * cols
    counts = np.round(values / values.sum() * n_cells).astype(int)
    counts[-1] = n_cells - counts[:-1].sum()  # fix rounding

    order = np.argsort(-counts)
    cells = []
    for idx in order:
        cells.extend([idx] * counts[idx])

    if figsize is None:
        figsize = (max(5, cols * 0.5 + 2.4), max(4.5, rows * 0.5 + 1.8))
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    colors = auto_colors(len(values), palette)
    shown = set()
    for k, cat in enumerate(cells):
        row, col = divmod(k, cols)
        label = labels[cat] if labels else str(cat)
        ax.scatter(col, rows - 1 - row, s=290, marker="s",
                   color=colors[cat % len(colors)],
                   edgecolors="white", lw=1.2,
                   label=label if cat not in shown else None)
        shown.add(cat)

    ax.set_xlim(-0.6, cols - 0.4)
    ax.set_ylim(-0.6, rows - 0.4)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_aspect("equal")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5),
              frameon=False, fontsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  POPULATION  PYRAMID
# ──────────────────────────────────────────────

def population_pyramid(
    labels,
    left,
    right,
    title: str | None = None,
    left_label: str = "Male",
    right_label: str = "Female",
    xlabel: str = "count / share",
    figsize: tuple = (8, 6),
    color_left: str = "#2E86AB",
    color_right: str = "#E76F51",
    show_values: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Population pyramid — mirrored horizontal bars (age structure,
    before/after comparison).

    Returns
    -------
    Figure
    """
    left = np.asarray(left, float)
    right = np.asarray(right, float)
    ypos = np.arange(len(labels))

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.barh(ypos, -left, color=color_left, alpha=0.88, height=0.72,
            label=left_label, edgecolor="white", lw=0.5)
    ax.barh(ypos, right, color=color_right, alpha=0.88, height=0.72,
            label=right_label, edgecolor="white", lw=0.5)

    m = max(left.max(), right.max())
    ax.set_xlim(-m * 1.15, m * 1.15)
    ticks = ax.get_xticks()
    ax.set_xticks(ticks)
    ax.set_xticklabels([format_numbers(abs(t)) for t in ticks], fontsize=8.5)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.axvline(0, color="#999999", lw=0.8)

    if show_values:
        for yi, (l, r) in enumerate(zip(left, right)):
            ax.text(-l - m * 0.02, yi, format_numbers(l), ha="right",
                    va="center", fontsize=7.5, color=color_left)
            ax.text(r + m * 0.02, yi, format_numbers(r), ha="left",
                    va="center", fontsize=7.5, color=color_right)

    ax.set_xlabel(xlabel)
    ax.legend(frameon=False, loc="lower right")
    axis_config(ax, grid="x")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SUNBURST
# ──────────────────────────────────────────────

def sunburst_chart(
    data,
    title: str | None = None,
    figsize: tuple = (7, 7),
    palette: str = "nature_qual",
    inner_palette: str | None = None,
    label_size: float = 8.5,
    show_pct: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Sunburst — two-ring hierarchical donut.

    Parameters
    ----------
    data : dict
        ``{group: {leaf: value}}`` for two levels, or
        ``{label: value}`` for a single ring (rendered as donut).

    Returns
    -------
    Figure
    """
    two_level = any(isinstance(v, dict) for v in data.values())
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(12, palette)

    if two_level:
        groups = list(data.keys())
        gvals = [sum(v.values()) if isinstance(v, dict) else v for v in data.values()]
        wedges, _ = ax.pie(
            gvals, radius=0.72, colors=colors[:len(groups)],
            wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2),
            startangle=90, counterclock=False,
        )
        for w, g in zip(wedges, groups):
            ang = np.deg2rad((w.theta1 + w.theta2) / 2)
            r = 0.53
            ax.text(r * np.cos(ang), r * np.sin(ang), str(g),
                    ha="center", va="center", fontsize=label_size + 0.5,
                    fontweight="bold", color="white")

        leaf_vals, leaf_cols, leaf_labs = [], [], []
        for gi, (g, sub) in enumerate(data.items()):
            items = sub.items() if isinstance(sub, dict) else [(str(g), sub)]
            for leaf, val in items:
                leaf_vals.append(val)
                leaf_labs.append(str(leaf))
                base = colors[gi % len(colors)]
                leaf_cols.append(blend(base, "#FFFFFF", 0.35))

        wedges, _, autotexts = ax.pie(
            leaf_vals, radius=1.08, colors=leaf_cols,
            wedgeprops=dict(width=0.34, edgecolor="white", linewidth=2),
            startangle=90, counterclock=False,
            autopct=(lambda p: f"{p:.0f}%" if show_pct and p >= 4 else ""),
            pctdistance=0.91,
        )
        for t, lab in zip(autotexts, leaf_labs):
            t.set_color("#FFFFFF")
            t.set_fontsize(label_size - 1)
        # outer labels via annotation
        for w, lab in zip(wedges, leaf_labs):
            if w.theta2 - w.theta1 < 8:
                continue
            ang = np.deg2rad((w.theta1 + w.theta2) / 2)
            x, y = np.cos(ang), np.sin(ang)
            ha = "left" if x >= 0 else "right"
            ax.annotate(lab, xy=(1.12 * x, 1.12 * y),
                        xytext=(1.22 * x, 1.22 * y),
                        ha=ha, va="center", fontsize=label_size,
                        color="#333333",
                        arrowprops=dict(arrowstyle="-", color="#AAAAAA",
                                        lw=0.7))
    else:
        labels = list(data.keys())
        vals = [float(v) for v in data.values()]
        wedges, _, autotexts = ax.pie(
            vals, radius=0.92, colors=colors[:len(labels)],
            wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
            startangle=90, counterclock=False,
            autopct=(lambda p: f"{p:.0f}%" if show_pct and p >= 4 else ""),
            pctdistance=0.78,
        )
        for t in autotexts:
            t.set_color("white")
            t.set_fontsize(label_size)
        ax.legend(wedges, labels, loc="center left",
                  bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)

    ax.set_aspect("equal")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=16)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ICICLE
# ──────────────────────────────────────────────

def icicle_chart(
    data,
    title: str | None = None,
    figsize: tuple = (9, 4.5),
    palette: str = "nature_qual",
    label_size: float = 8.5,
    min_width_frac: float = 0.015,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Icicle chart — hierarchical rectangles flowing downward.

    Parameters
    ----------
    data : dict
        ``{root: {group: {leaf: value}}}`` — up to 3 levels, or
        ``{group: {leaf: value}}`` for 2 levels.

    Returns
    -------
    Figure
    """
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(12, palette)
    max_depth = [0]

    def _total(v) -> float:
        return float(v) if not isinstance(v, dict) else sum(_total(c) for c in v.values())

    def draw(node_name, value, x0, x1, depth):
        width = x1 - x0
        if width < min_width_frac:
            return
        color = blend(colors[depth % len(colors)], "#FFFFFF", 0.22 * max(depth, 0))
        ax.add_patch(plt.Rectangle(
            (x0, -depth - 1), width, 0.92,
            facecolor=color, edgecolor="white", lw=1.5,
        ))
        name_color = contrast_color(color)
        if width > 0.035:
            ax.text(x0 + width / 2, -depth - 0.54,
                    f"{node_name}", ha="center", va="center",
                    fontsize=label_size, color=name_color,
                    fontweight="bold" if depth <= 0 else "normal")
        if width > 0.06:
            ax.text(x0 + width / 2, -depth - 0.22,
                    f"{value:.4g}", ha="center", va="center",
                    fontsize=label_size - 1.5, color=name_color,
                    alpha=0.85)

    def walk(name, node, x0, x1, depth):
        max_depth[0] = max(max_depth[0], depth)
        if isinstance(node, dict):
            total = _total(node) or 1
            cur = x0
            for child_name, child in node.items():
                w = _total(child) / total * (x1 - x0)
                walk(child_name, child, cur, cur + w, depth + 1)
                cur += w
            draw(name, total, x0, x1, depth)
        else:
            draw(name, node, x0, x1, depth)

    if len(data) == 1:
        (root_name, root), = data.items()
        walk(root_name, root, 0.0, 1.0, 0)
    else:
        total = sum(_total(v) for v in data.values()) or 1
        cur = 0.0
        for name, v in data.items():
            w = _total(v) / total
            walk(name, v, cur, cur + w, 0)
            cur += w

    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-max_depth[0] - 1.25, 0.2)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  MOSAIC  (MARIMEKKO)
# ──────────────────────────────────────────────

def mosaic_plot(
    counts,
    row_labels: Sequence[str] | None = None,
    col_labels: Sequence[str] | None = None,
    title: str | None = None,
    figsize: tuple | None = None,
    palette: str = "nature_qual",
    show_counts: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Mosaic (Marimekko) plot — proportions of two categorical variables;
    column widths show marginal shares.

    Parameters
    ----------
    counts : 2-D array-like, shape (n_rows, n_cols)

    Returns
    -------
    Figure
    """
    M = np.asarray(counts, dtype=float)
    n_rows, n_cols = M.shape
    row_labels = row_labels or [f"R{i + 1}" for i in range(n_rows)]
    col_labels = col_labels or [f"C{j + 1}" for j in range(n_cols)]
    if figsize is None:
        figsize = (max(6, n_cols * 1.3 + 1), max(4.5, n_rows * 0.9 + 1.5))

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(n_rows, palette)
    col_shares = M.sum(axis=0) / M.sum()

    x0 = 0.0
    for j in range(n_cols):
        w = col_shares[j]
        row_share = M[:, j] / M[:, j].sum()
        y0 = 0.0
        for i in range(n_rows):
            h = row_share[i]
            ax.add_patch(plt.Rectangle(
                (x0, y0), w, h, facecolor=colors[i % len(colors)],
                edgecolor="white", lw=1.6, alpha=0.92,
            ))
            if show_counts and h > 0.06 and w > 0.05:
                ax.text(x0 + w / 2, y0 + h / 2, f"{int(M[i, j])}",
                        ha="center", va="center", fontsize=8,
                        color="white")
            y0 += h
        if w > 0.04:
            ax.text(x0 + w / 2, -0.04, col_labels[j], ha="center",
                    va="top", fontsize=9)
        x0 += w

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 1.02)
    ax.axis("off")
    handles = [plt.Rectangle((0, 0), 1, 1, fc=colors[i % len(colors)])
               for i in range(n_rows)]
    ax.legend(handles, row_labels, loc="center left",
              bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DENDROGRAM
# ──────────────────────────────────────────────

def dendrogram(
    data,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    figsize: tuple = (9, 5),
    method: str = "ward",
    metric: str = "euclidean",
    color_threshold: float | None = None,
    palette: str = "nature_qual",
    show_labels: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Hierarchical-clustering dendrogram.

    Parameters
    ----------
    data : 2-D array-like (n_samples × n_features) or precomputed
        linkage matrix.

    Returns
    -------
    Figure
    """
    from scipy.cluster.hierarchy import dendrogram as _dend, linkage as _linkage

    arr = np.asarray(data, dtype=float)
    if arr.ndim == 2 and arr.shape[1] > 3:  # observations, not linkage
        Z = _linkage(arr, method=method, metric=metric)
    else:
        Z = arr
    n_leaves = int(Z[-1, 3]) + 1 if Z.ndim == 2 else len(labels or [])
    if labels is None:
        labels = [f"S{i + 1}" for i in range(n_leaves)]

    if color_threshold is None:
        color_threshold = 0.7 * Z[:, 2].max()

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    with plt.rc_context({"lines.linewidth": 1.6}):
        _dend(
            Z, ax=ax, labels=list(labels), color_threshold=color_threshold,
            above_threshold_color="#999999",
            link_color_func=None if False else None,
        )

    ax.set_ylabel("distance")
    axis_config(ax, grid="y")
    ax.tick_params(axis="x", labelsize=8.5, rotation=90)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DISTRIBUTION  PANEL
# ──────────────────────────────────────────────

def distribution_panel(
    data,
    title: str | None = None,
    figsize: tuple = (9, 7),
    color: str = "#2E86AB",
    dist: str = "norm",
    bins: int | str = "auto",
    show_test: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Four-panel distribution diagnostic — histogram + KDE, box, violin,
    and Q-Q plot in one publication figure.

    Parameters
    ----------
    data : 1-D array-like

    Returns
    -------
    Figure
    """
    from scipy import stats as sps

    values = _to_1d(data)
    values = values[~np.isnan(values)]
    kwargs.pop("style", None)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    (ax1, ax2), (ax3, ax4) = axes

    # Histogram + KDE
    ax1.hist(values, bins=bins, density=True, color=color, alpha=0.75,
             edgecolor="white", lw=0.5)
    grid = np.linspace(values.min(), values.max(), 220)
    ax1.plot(grid, _kde(values, grid), color="#C73E1D", lw=1.8,
             label="KDE")
    mu, sd = values.mean(), values.std()
    if show_test and len(values) >= 8:
        stat, p = sps.shapiro(values) if len(values) <= 5000 else (np.nan, np.nan)
        test_txt = f"Shapiro-Wilk\nW = {stat:.3f}, p = {p:.3g}" if not np.isnan(stat) else ""
        ax1.text(0.97, 0.95, test_txt, transform=ax1.transAxes,
                 ha="right", va="top", fontsize=7.5, color="#555555")
    ax1.axvline(mu, color="#333333", lw=0.9, ls="--", alpha=0.7)
    ax1.set_title("Histogram + KDE", fontsize=10)
    ax1.legend(frameon=False, fontsize=8)

    # Box
    ax2.boxplot(values, **_vert_kw(False), widths=0.55, patch_artist=True,
                boxprops=dict(facecolor=lightness(color, 0.25), edgecolor=color),
                medianprops=dict(color="#C73E1D", lw=1.8),
                whiskerprops=dict(color="#666666"),
                capprops=dict(color="#666666"),
                flierprops=dict(marker="o", ms=4, mfc="#999999", mec="none",
                                alpha=0.6))
    ax2.set_yticks([])
    ax2.set_title("Box plot", fontsize=10)

    # Violin
    parts = ax3.violinplot(values, **_vert_kw(False), widths=0.7, showmedians=True)
    for pc in parts["bodies"]:
        pc.set_facecolor(lightness(color, 0.35))
        pc.set_edgecolor(color)
        pc.set_alpha(0.9)
    parts["cmedians"].set_color("#C73E1D")
    ax3.set_yticks([])
    ax3.set_title("Violin plot", fontsize=10)

    # QQ
    (osm, osr), (_, _, r) = sps.probplot(values, dist=dist)
    ax4.scatter(osm, osr, s=14, color=color, alpha=0.7, zorder=3)
    slope, intercept = np.polyfit(osm, osr, 1)
    ax4.plot(osm, slope * osm + intercept, color="#C73E1D", lw=1.6)
    ax4.set_title(f"Q-Q plot (R² = {r ** 2:.4f})", fontsize=10)

    for ax in (ax1, ax4):
        axis_config(ax, grid="y")
    for ax in (ax2, ax3):
        axis_config(ax, grid="x")

    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SCATTER  MATRIX
# ──────────────────────────────────────────────

def scatter_matrix(
    data,
    title: str | None = None,
    figsize: tuple | None = None,
    palette: str = "nature_qual",
    diagonal: str = "hist",
    alpha: float = 0.65,
    names: Sequence[str] | None = None,
    groups: Sequence | None = None,
    group_labels: Sequence[str] | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Pairwise scatter matrix with histogram or KDE diagonal.

    Parameters
    ----------
    data : 2-D array-like (n_samples × n_features) or DataFrame
    names : list of str
        Variable names (defaults to V1…Vn or DataFrame columns).
    diagonal : str
        'hist' or 'kde'.

    Returns
    -------
    Figure
    """
    arr = np.asarray(data, dtype=float)
    n_vars = arr.shape[1]
    if figsize is None:
        figsize = (max(6, n_vars * 2.1), max(6, n_vars * 2.1))
    if names is None:
        try:
            names = [str(c) for c in data.columns]  # DataFrame
        except Exception:
            names = [f"V{i + 1}" for i in range(n_vars)]

    kwargs.pop("style", None)
    fig, axes = plt.subplots(n_vars, n_vars, figsize=figsize)
    axes = np.atleast_2d(axes)
    base_color = auto_colors(1, palette)[0]

    cats, gcolors, masks = None, None, None
    if groups is not None:
        cats = list(dict.fromkeys(groups))
        gcolors = auto_colors(len(cats), palette)
        masks = {c: np.asarray([g == c for g in groups]) for c in cats}

    for i in range(n_vars):
        for j in range(n_vars):
            ax = axes[i, j]
            if i == j:
                if masks:
                    for c, col in zip(cats, gcolors):
                        if diagonal == "kde":
                            grid = np.linspace(arr[:, i].min(),
                                               arr[:, i].max(), 160)
                            ax.plot(grid, _kde(arr[masks[c], i], grid),
                                    color=col, lw=1.4, label=str(c))
                        else:
                            ax.hist(arr[masks[c], i], bins=16, color=col,
                                    alpha=0.55, edgecolor="white", lw=0.4,
                                    label=str(c))
                elif diagonal == "kde":
                    grid = np.linspace(arr[:, i].min(), arr[:, i].max(), 160)
                    ax.fill_between(grid, _kde(arr[:, i], grid),
                                    color=base_color, alpha=0.4, lw=1.4)
                else:
                    ax.hist(arr[:, i], bins=16, color=base_color, alpha=0.75,
                            edgecolor="white", lw=0.4)
                ax.set_yticks([])
            else:
                if masks:
                    for c, col in zip(cats, gcolors):
                        ax.scatter(arr[masks[c], j], arr[masks[c], i], s=9,
                                   color=col, alpha=alpha, edgecolors="none")
                else:
                    ax.scatter(arr[:, j], arr[:, i], s=9, color=base_color,
                               alpha=alpha, edgecolors="none")
            if i == n_vars - 1:
                ax.set_xlabel(names[j], fontsize=8.5)
            if j == 0:
                ax.set_ylabel(names[i], fontsize=8.5)
            ax.tick_params(labelsize=7)
            axis_config(ax, grid="none")

    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "qq_plot",
    "ecdf_plot",
    "ridgeline",
    "hexbin_plot",
    "stem_plot",
    "errorbar_chart",
    "bubble_chart",
    "bump_chart",
    "stream_graph",
    "funnel_chart",
    "waffle_chart",
    "population_pyramid",
    "sunburst_chart",
    "icicle_chart",
    "mosaic_plot",
    "dendrogram",
    "distribution_panel",
    "scatter_matrix",
    "hypothesis_test", "lorenz_curve", "forecast",
    "biplot", "ks_test", "range_plot", "calendar_heatmap",
    "grouped_scatter", "bland_altman",
    "joint_plot", "forest_plot", "strip_plot", "smooth_plot",
    "scatter_contour", "diverging_bar", "pareto_chart",
    "dot_plot", "volcano_plot", "confidence_ellipse",
    "stacked_histogram",
    "beeswarm", "control_chart", "candlestick", "delta_band",
    "raincloud",
]


# ──────────────────────────────────────────────
#  RAINCLOUD  (half violin + box + points)
# ──────────────────────────────────────────────

def raincloud(
    data,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    ylabel: str = "value",
    figsize: tuple = (9.5, 5.5),
    palette: str = "nature_qual",
    point_size: float = 18,
    point_jitter: float = 0.09,
    point_alpha: float = 0.55,
    violin_alpha: float = 0.8,
    show_box: bool = True,
    seed: int = 42,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Raincloud plot — half violin (the cloud) + thin box + jittered raw
    points (the rain) per category. The most information-dense
    distribution figure: shape, quartiles, and every observation.

    Returns
    -------
    Figure
    """
    from matplotlib.patches import Polygon as MplPolygon

    groups = data if isinstance(data, dict) else {
        (labels[i] if labels else f"G{i + 1}"): np.asarray(v, float).ravel()
        for i, v in enumerate(data)
    }
    names = list(groups.keys())
    colors = auto_colors(len(names), palette)
    rng = np.random.default_rng(seed)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    for i, (name, vals) in enumerate(zip(names, groups.values())):
        vals = np.asarray(vals, float)
        c = colors[i % len(colors)]

        # half violin (left side)
        grid = np.linspace(vals.min() - 0.1 * np.ptp(vals),
                           vals.max() + 0.1 * np.ptp(vals), 120)
        dens = _kde(vals, grid)
        dens = dens / dens.max() * 0.32
        cloud_x = [i - 0.06 - dens, np.full_like(dens, i - 0.06)]
        ax.fill(np.r_[cloud_x[0], cloud_x[1][::-1]],
                np.r_[grid, grid[::-1]], color=c, alpha=violin_alpha,
                lw=0.8, edgecolor="white", zorder=2)

        # thin box (center line)
        q1, med, q3 = np.percentile(vals, [25, 50, 75])
        ax.plot([i - 0.04, i + 0.04], [q1, q1], color="#333333",
                lw=1.1, zorder=4)
        ax.plot([i - 0.04, i + 0.04], [q3, q3], color="#333333",
                lw=1.1, zorder=4)
        ax.plot([i, i], [q1, q3], color="#333333", lw=1.3, zorder=4)
        ax.plot(i, med, "o", ms=4.5, mfc="white", mec="#333333",
                mew=1.2, zorder=5)

        # rain: jittered raw points on the right
        jx = i + 0.10 + np.abs(rng.normal(0, point_jitter, len(vals)))
        ax.scatter(jx, vals, s=point_size, color=c, alpha=point_alpha,
                   edgecolors="none", zorder=3)

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, fontsize=9)
    ax.set_xlim(-0.7, len(names) - 0.3)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  BEESWARM  (non-overlapping strip)
# ──────────────────────────────────────────────

def beeswarm(
    data,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    ylabel: str = "value",
    figsize: tuple = (8, 5),
    palette: str = "nature_qual",
    point_size: float = 26,
    gap: float = 0.9,
    overlay_box: bool = False,
    seed: int = 42,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Beeswarm — every observation visible with zero overlap (points
    slide sideways to dodge each other). Sharper than a jittered strip.

    Returns
    -------
    Figure
    """
    groups = data if isinstance(data, dict) else {
        (labels[i] if labels else f"G{i + 1}"): np.asarray(v, float).ravel()
        for i, v in enumerate(data)
    }
    names = list(groups.keys())
    colors = auto_colors(len(names), palette)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if overlay_box:
        ax.boxplot([groups[n] for n in names], positions=range(len(names)),
                   widths=0.5, patch_artist=True, showfliers=False,
                   boxprops=dict(facecolor="none", edgecolor="#AAAAAA", lw=1),
                   medianprops=dict(color="#C73E1D", lw=1.6),
                   whiskerprops=dict(color="#AAAAAA"),
                   capprops=dict(color="#AAAAAA"))

    # point radius approximated in axis units (x and y differ)
    y_span = max((np.nanmax(v) - np.nanmin(v) for v in groups.values()), default=1) or 1
    r_y = np.sqrt(point_size) / 2 / 100 * 4          # vertical radius units
    r_x = r_y * 8 / figsize[1] * 2                    # x radius in category units

    for i, (name, vals) in enumerate(zip(names, groups.values())):
        vals = np.asarray(vals, float)
        order = np.argsort(vals)
        sorted_v = vals[order]
        offsets = np.zeros(len(sorted_v))
        placed: list = []  # (x_offset, y)
        for k, v in enumerate(sorted_v):
            x_off = 0.0
            step = r_x * gap
            attempts = 0
            while attempts < 300:
                conflict = any(
                    abs(v - py) < 2 * r_y * gap
                    and abs(x_off - px) < 2 * r_x * gap
                    for px, py in placed
                )
                if not conflict:
                    break
                direction = 1 if attempts % 2 == 0 else -1
                x_off = direction * step * (attempts // 2 + 1)
                attempts += 1
            placed.append((x_off, v))
            offsets[order[k]] = x_off
        ax.scatter(i + offsets, vals, s=point_size,
                   color=colors[i % len(colors)], alpha=0.85,
                   edgecolors="white", lw=0.4, zorder=3)

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CONTROL  CHART  (SPC)
# ──────────────────────────────────────────────

def control_chart(
    values: Sequence[float],
    title: str | None = None,
    xlabel: str = "sample",
    ylabel: str = "value",
    figsize: tuple = (10, 5),
    color: str = "#2E86AB",
    center_color: str = "#1D3557",
    limit_color: str = "#C73E1D",
    n_sigma: float = 3.0,
    highlight_violations: bool = True,
    show_zones: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Statistical process control chart — center line (mean), ±2σ/±3σ
    limits, and out-of-control points flagged. Useful for Monte-Carlo
    diagnostics, simulation stability, and quality chapters.

    Returns
    -------
    Figure
    """
    v = np.asarray(values, float).ravel()
    mean = float(v.mean())
    sd = float(v.std())
    ucl, lcl = mean + n_sigma * sd, mean - n_sigma * sd
    warn_hi, warn_lo = mean + 2 * sd, mean - 2 * sd

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    x = np.arange(1, len(v) + 1)

    if show_zones:
        for level, alpha in ((3, 0.05), (2, 0.05)):
            ax.axhspan(mean + level * sd, mean + (level + 1) * sd if level < 3 else v.max(),
                       color="#C73E1D", alpha=alpha * 0.5, lw=0) if level == 3 else None
        ax.axhspan(warn_hi, ucl, color="#F5A623", alpha=0.10, lw=0)
        ax.axhspan(lcl, warn_lo, color="#F5A623", alpha=0.10, lw=0)

    ax.plot(x, v, "-o", color=color, lw=1.5, ms=4, zorder=3)
    ax.axhline(mean, color=center_color, lw=1.5,
               label=f"CL = {mean:.3g}")
    ax.axhline(ucl, color=limit_color, lw=1.2, ls="--",
               label=f"UCL = {ucl:.3g}")
    ax.axhline(lcl, color=limit_color, lw=1.2, ls="--",
               label=f"LCL = {lcl:.3g}")

    if highlight_violations:
        out = (v > ucl) | (v < lcl)
        if out.any():
            ax.scatter(x[out], v[out], s=90, marker="x", color=limit_color,
                       lw=2.2, zorder=5,
                       label=f"out of control ({int(out.sum())})")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right", ncols=2)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CANDLESTICK  (OHLC)
# ──────────────────────────────────────────────

def candlestick(
    open_: Sequence[float],
    high: Sequence[float],
    low: Sequence[float],
    close: Sequence[float],
    title: str | None = None,
    xlabel: str = "period",
    ylabel: str = "price",
    figsize: tuple = (10, 5.5),
    up_color: str = "#26A69A",
    down_color: str = "#EF5350",
    width: float = 0.6,
    show_grid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Candlestick chart for OHLC data — price series, bid/ask ranges,
    or any open-high-low-close quartets (sensitivity envelopes too).

    Returns
    -------
    Figure
    """
    o = np.asarray(open_, float)
    h = np.asarray(high, float)
    l = np.asarray(low, float)
    c = np.asarray(close, float)
    n = len(o)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    for i in range(n):
        up = c[i] >= o[i]
        color = up_color if up else down_color
        ax.plot([i, i], [l[i], h[i]], color=color, lw=1.1, zorder=2)
        body_lo, body_hi = min(o[i], c[i]), max(o[i], c[i])
        ax.add_patch(plt.Rectangle(
            (i - width / 2, body_lo), width, body_hi - body_lo or 1e-9,
            facecolor=color if not up else "white",
            edgecolor=color, lw=1.2, zorder=3,
        ))

    ax.set_xlim(-1, n)
    ax.set_ylim(l.min() - (h.max() - l.min()) * 0.05,
                h.max() + (h.max() - l.min()) * 0.05)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if show_grid:
        axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DELTA  BAND  (two-series difference)
# ──────────────────────────────────────────────

def delta_band(
    x,
    series_a: Sequence[float],
    series_b: Sequence[float],
    label_a: str = "Scenario A",
    label_b: str = "Scenario B",
    title: str | None = None,
    xlabel: str = "time",
    ylabel: str = "value",
    figsize: tuple = (9.5, 5),
    color_a: str = "#2E86AB",
    color_b: str = "#C73E1D",
    band_color: str = "#F4A261",
    band_alpha: float = 0.25,
    annotate_gap: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Two series with their difference shaded — policy-vs-baseline,
    before-vs-after, scenario-vs-reference comparisons.

    Returns
    -------
    Figure
    """
    xv = np.asarray(x, float)
    a = np.asarray(series_a, float)
    b = np.asarray(series_b, float)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.plot(xv, a, color=color_a, lw=2, label=label_a)
    ax.plot(xv, b, color=color_b, lw=2, ls="--", label=label_b)
    ax.fill_between(xv, a, b, where=(a >= b), color=band_color,
                    alpha=band_alpha, lw=0,
                    label=f"{label_a} ≥ {label_b}")
    ax.fill_between(xv, a, b, where=(a < b), color="#7FB3D5",
                    alpha=band_alpha, lw=0,
                    label=f"{label_a} < {label_b}")

    if annotate_gap:
        k = int(np.argmax(np.abs(a - b)))
        ax.annotate(
            f"max |Δ| = {abs(a[k] - b[k]):.3g}",
            xy=(xv[k], (a[k] + b[k]) / 2), xytext=(16, 0),
            textcoords="offset points", va="center", fontsize=9,
            color="#1D3557",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#CCCCCC", alpha=0.9),
            arrowprops=dict(arrowstyle="-|>", color="#666666", lw=1))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=8.5, loc="best", ncols=2)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CLEVELAND  DOT  PLOT
# ──────────────────────────────────────────────

def dot_plot(
    labels: Sequence[str],
    values: Sequence[float],
    values2: Optional[Sequence[float]] = None,
    label2: str = "Series 2",
    label1: str = "Series 1",
    title: str | None = None,
    xlabel: str = "value",
    figsize: tuple = (8, max(4, 0.5 * 8)),
    palette: str = "nature_qual",
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    sort: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Cleveland dot plot — the cleanest comparison of values across
    categories; with two series it doubles as a dumbbell variant.

    Returns
    -------
    Figure
    """
    values = np.asarray(values, float)
    if sort:
        order = np.argsort(values)
    else:
        order = np.arange(len(values))
    values = values[order]
    labels = [str(labels[i]) for i in order]
    ypos = np.arange(len(labels))[::-1]
    colors = auto_colors(2, palette)

    figsize = (figsize[0], max(figsize[1], 0.5 * len(labels) + 1.5))
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if values2 is not None:
        v2 = np.asarray(values2, float)[order]
        ax.plot([values, v2], [ypos, ypos], color="#CCCCCC", lw=2.4,
                zorder=1, solid_capstyle="round")
        ax.scatter(values, ypos, s=64, color=colors[0], zorder=3,
                   edgecolors="white", lw=0.8, label=label1)
        ax.scatter(v2, ypos, s=64, color=colors[1], zorder=3,
                   edgecolors="white", lw=0.8, label=label2)
        ax.legend(frameon=False, loc="lower right", fontsize=9)
    else:
        ax.scatter(values, ypos, s=72, color=colors[0], zorder=3,
                   edgecolors="white", lw=0.8)

    if show_values:
        span = values.max() - values.min() or 1
        for y, v in zip(ypos, values):
            ax.text(v + span * 0.02, y, value_fmt.format(v), va="center",
                    fontsize=8, color="#555555")

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(values.min() - span * 0.12, values.max() + span * 0.14)
    ax.set_xlabel(xlabel)
    axis_config(ax, grid="x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  VOLCANO  PLOT  (fold change vs significance)
# ──────────────────────────────────────────────

def volcano_plot(
    fold_change: Sequence[float],
    p_values: Sequence[float],
    labels: Sequence[str] | None = None,
    title: str | None = None,
    xlabel: str = "log2 fold change",
    ylabel: str = "-log10(p-value)",
    figsize: tuple = (8, 6),
    ns_color: str = "#BBBBBB",
    up_color: str = "#C73E1D",
    down_color: str = "#2E86AB",
    fc_threshold: float = 1.0,
    p_threshold: float = 0.05,
    label_top: int = 8,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Volcano plot — log fold change against significance. Points beyond
    both thresholds (up/down regulated) are colored; the most extreme
    items get labels.

    Parameters
    ----------
    fold_change : array-like
        Fold changes (log2-transformed internally if raw ratios given —
        values in (-inf, inf) are used as-is).
    p_values : array-like
        Raw p-values (−log10 applied here).

    Returns
    -------
    Figure
    """
    fc = np.asarray(fold_change, float)
    if np.nanmax(np.abs(fc)) <= 32:  # probably raw ratios → log2
        fc = np.log2(np.clip(np.abs(fc), 1e-12, None)) * np.sign(
            np.where(fc == 0, 1, fc))
    p = np.asarray(p_values, float)
    score = -np.log10(np.clip(p, 1e-300, None))

    sig = p < p_threshold
    up = sig & (fc > fc_threshold)
    down = sig & (fc < -fc_threshold)
    ns = ~(up | down)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.scatter(fc[ns], score[ns], s=20, color=ns_color, alpha=0.6, lw=0,
               label="not significant")
    ax.scatter(fc[up], score[up], s=26, color=up_color, alpha=0.85, lw=0,
               label=f"up (fc>{fc_threshold:g}, p<{p_threshold:g})")
    ax.scatter(fc[down], score[down], s=26, color=down_color, alpha=0.85,
               lw=0, label=f"down (fc<-{fc_threshold:g})")

    ax.axhline(-np.log10(p_threshold), color="#888888", lw=1, ls="--")
    ax.axvline(fc_threshold, color="#888888", lw=1, ls=":")
    ax.axvline(-fc_threshold, color="#888888", lw=1, ls=":")

    if labels is not None and label_top > 0:
        labels = [str(l) for l in labels]
        order = np.argsort(-score)
        for k in order[:label_top]:
            if not sig[k]:
                continue
            ax.annotate(labels[k], (fc[k], score[k]),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=7.5, color="#333333")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CONFIDENCE  ELLIPSES  (bivariate)
# ──────────────────────────────────────────────

def confidence_ellipse(
    x,
    y,
    groups: Optional[Sequence] = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 6),
    palette: str = "nature_qual",
    n_std: tuple = (1.0, 2.0),
    point_size: float = 26,
    alpha: float = 0.7,
    ellipse_alpha: float = 0.16,
    show_centroid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Scatter with bivariate confidence ellipses per group — the honest
    way to show cluster spread and separation.

    Parameters
    ----------
    n_std : tuple of float
        Ellipse levels in standard deviations (e.g. (1, 2) = ~68%, ~95%).

    Returns
    -------
    Figure
    """
    from matplotlib.patches import Ellipse

    x_arr = np.asarray(x, float)
    y_arr = np.asarray(y, float)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if groups is not None:
        cats = list(dict.fromkeys(groups))
        colors = auto_colors(len(cats), palette)
        pairs = list(zip(cats, colors))
    else:
        cats = [None]
        colors = [auto_colors(1, "nature_qual")[0]]
        pairs = [(None, colors[0])]

    for cat, c in pairs:
        if cat is None:
            m = np.ones(len(x_arr), dtype=bool)
            label = None
        else:
            m = np.asarray([g == cat for g in groups])
            label = str(cat)
        xv, yv = x_arr[m], y_arr[m]
        ax.scatter(xv, yv, s=point_size, color=c, alpha=alpha,
                   edgecolors="white", lw=0.4, label=label, zorder=3)

        for k in n_std:
            cov = np.cov(xv, yv)
            if not np.all(np.isfinite(cov)):
                continue
            eigvals, eigvecs = np.linalg.eigh(cov)
            order = eigvals.argsort()[::-1]
            eigvals, eigvecs = eigvals[order], eigvecs[:, order]
            angle = np.degrees(np.arctan2(eigvecs[1, 0], eigvecs[0, 0]))
            width, height = 2 * k * np.sqrt(np.abs(eigvals))
            ell = Ellipse(
                (xv.mean(), yv.mean()), width, height, angle=angle,
                facecolor=c, alpha=ellipse_alpha, edgecolor=c, lw=1.2,
                zorder=2,
            )
            ax.add_patch(ell)
        if show_centroid:
            ax.plot(xv.mean(), yv.mean(), "x", ms=9, color=c, mew=2.2,
                    zorder=4)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if groups is not None:
        ax.legend(frameon=False, loc="best")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  STACKED  /  OVERLAID  HISTOGRAMS
# ──────────────────────────────────────────────

def stacked_histogram(
    data,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    xlabel: str = "value",
    ylabel: str = "count",
    figsize: tuple = (9, 5),
    palette: str = "nature_qual",
    mode: str = "stacked",
    bins: int = 30,
    density: bool = False,
    show_legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Multi-group histogram — 'stacked', 'overlay' (semi-transparent) or
    'step' (outline only). Shows how a distribution shifts across groups.

    Returns
    -------
    Figure
    """
    groups = data if isinstance(data, dict) else {
        (labels[i] if labels else f"G{i + 1}"): np.asarray(v, float)
        for i, v in enumerate(data)
    }
    names = list(groups.keys())
    arrays = [np.asarray(groups[n], float).ravel() for n in names]
    colors = auto_colors(len(names), palette)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    common = dict(bins=bins, density=density)
    if mode == "stacked":
        ax.hist(arrays, stacked=True, color=colors, edgecolor="white",
                lw=0.5, label=names, **common)
    elif mode == "overlay":
        for arr, c, n in zip(arrays, colors, names):
            ax.hist(arr, color=c, alpha=0.55, edgecolor="white", lw=0.4,
                    label=n, **common)
    elif mode == "step":
        for arr, c, n in zip(arrays, colors, names):
            ax.hist(arr, histtype="step", lw=1.9, color=c, label=n, **common)
    else:
        raise ValueError("mode must be 'stacked', 'overlay' or 'step'.")

    if show_legend:
        ax.legend(frameon=False, fontsize=9)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("density" if density else ylabel)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  JOINT  PLOT  (scatter + marginals)
# ──────────────────────────────────────────────

def joint_plot(
    x,
    y,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (7.5, 7),
    color: str = "#2E86AB",
    marginal: str = "hist",
    show_fit: bool = True,
    show_corr: bool = True,
    height_ratio: tuple = (4, 1),
    bins: int = 25,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Scatter with marginal distributions (seaborn jointplot style) —
    the relationship and each variable's spread in one figure.

    Parameters
    ----------
    marginal : str
        'hist' or 'kde' for the marginal panels.

    Returns
    -------
    Figure
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, width_ratios=(height_ratio[0], height_ratio[1]),
                          height_ratios=(height_ratio[0], height_ratio[1]),
                          hspace=0.06, wspace=0.06)
    ax = fig.add_subplot(gs[0, 0])
    ax_x = fig.add_subplot(gs[1, 0], sharex=ax)
    ax_y = fig.add_subplot(gs[0, 1], sharey=ax)

    ax.scatter(x_arr, y_arr, s=24, color=color, alpha=0.7,
               edgecolors="white", lw=0.4, zorder=3)
    if show_fit:
        b, a = np.polyfit(x_arr, y_arr, 1)
        xf = np.linspace(x_arr.min(), x_arr.max(), 50)
        ax.plot(xf, a + b * xf, color="#C73E1D", lw=1.8, ls="--", zorder=2)
    if show_corr:
        r = float(np.corrcoef(x_arr, y_arr)[0, 1])
        ax.text(0.03, 0.96, f"Pearson r = {r:.3f}", transform=ax.transAxes,
                va="top", fontsize=9.5, color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    common = dict(color=color, alpha=0.65, edgecolor="white", lw=0.4)
    if marginal == "kde":
        grid_x = np.linspace(x_arr.min(), x_arr.max(), 160)
        grid_y = np.linspace(y_arr.min(), y_arr.max(), 160)
        ax_x.fill_between(grid_x, _kde(x_arr, grid_x), color=color, alpha=0.4, lw=1.2)
        ax_y.fill_betweenx(grid_y, _kde(y_arr, grid_y), color=color, alpha=0.4, lw=1.2)
    else:
        ax_x.hist(x_arr, bins=bins, orientation="vertical", **common)
        ax_y.hist(y_arr, bins=bins, orientation="horizontal", **common)

    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax_y.get_yticklabels(), visible=False)
    ax_x.set_xlabel(xlabel)
    ax_y.set_xlabel("density" if marginal == "kde" else "count")
    ax.set_ylabel(ylabel)
    for a_ in (ax, ax_x, ax_y):
        axis_config(a_, grid="none")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  FOREST  PLOT  (effect sizes with CI)
# ──────────────────────────────────────────────

def forest_plot(
    labels: Optional[Sequence[str]],
    estimates: Sequence[float],
    lower: Sequence[float],
    upper: Sequence[float],
    title: str | None = None,
    xlabel: str = "Effect estimate (95% CI)",
    figsize: tuple = (9, max(4.5, 0.55 * 6)),
    color: str = "#2E86AB",
    pooled_line: float | None = None,
    null_line: float = 0.0,
    show_values: bool = True,
    value_fmt: str = "{:.3f} [{:.3f}, {:.3f}]",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Forest plot — point estimates with confidence intervals, the
    standard figure for comparing effect sizes across subgroups,
    scenarios, or studies (meta-analysis style).

    Parameters
    ----------
    pooled_line : float, optional
        Vertical dashed line at the pooled/overall estimate.
    null_line : float
        Vertical dotted line marking "no effect".

    Returns
    -------
    Figure
    """
    est = np.asarray(estimates, float)
    lo = np.asarray(lower, float)
    hi = np.asarray(upper, float)
    if labels is None:
        labels = [f"S{i + 1}" for i in range(len(est))]
    ypos = np.arange(len(labels))[::-1]

    figsize = (figsize[0], max(figsize[1], 0.55 * len(labels) + 1.5))
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    ax.axvline(null_line, color="#BBBBBB", lw=1, ls=":", zorder=1)
    if pooled_line is not None:
        ax.axvline(pooled_line, color="#C73E1D", lw=1.3, ls="--", zorder=1)

    ax.errorbar(est, ypos, xerr=[est - lo, hi - est], fmt="s", ms=6,
                color=color, ecolor=color, elinewidth=1.6, capsize=3.5,
                capthick=1.4, mfc=color, mec="white", mew=0.9, zorder=3)

    if show_values:
        for y, e, l, h in zip(ypos, est, lo, hi):
            ax.text(h + (hi.max() - lo.min()) * 0.015, y,
                    value_fmt.format(e, l, h), va="center", fontsize=7.8,
                    color="#555555")

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(lo.min() - (hi.max() - lo.min()) * 0.08,
                hi.max() + (hi.max() - lo.min()) * 0.22)
    ax.set_xlabel(xlabel)
    axis_config(ax, grid="x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  STRIP  PLOT  (jittered categorical points)
# ──────────────────────────────────────────────

def strip_plot(
    data,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    ylabel: str = "value",
    figsize: tuple = (8, 5),
    palette: str = "nature_qual",
    jitter: float = 0.14,
    point_size: float = 22,
    alpha: float = 0.7,
    overlay_box: bool = False,
    overlay_mean: bool = True,
    seed: int = 42,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Jittered strip plot — every observation visible, ideal over or
    instead of a box plot when sample sizes are small.

    Returns
    -------
    Figure
    """
    groups = data if isinstance(data, dict) else {
        (labels[i] if labels else f"G{i + 1}"): np.asarray(v, float)
        for i, v in enumerate(data)
    }
    names = list(groups.keys())
    rng = np.random.default_rng(seed)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(len(names), palette)

    if overlay_box:
        ax.boxplot([groups[n] for n in names], positions=range(len(names)),
                   widths=0.5, patch_artist=True, showfliers=False,
                   boxprops=dict(facecolor="none", edgecolor="#AAAAAA", lw=1),
                   medianprops=dict(color="#C73E1D", lw=1.6),
                   whiskerprops=dict(color="#AAAAAA"),
                   capprops=dict(color="#AAAAAA"))

    for i, (name, vals) in enumerate(zip(names, groups.values())):
        vals = np.asarray(vals, float).ravel()
        xs = i + rng.uniform(-jitter, jitter, len(vals))
        ax.scatter(xs, vals, s=point_size, color=colors[i % len(colors)],
                   alpha=alpha, edgecolors="white", lw=0.4, zorder=3)
        if overlay_mean:
            ax.plot([i - 0.18, i + 0.18], [vals.mean()] * 2,
                    color="#1D3557", lw=2, zorder=4)

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SMOOTHED  TREND  OVERLAY
# ──────────────────────────────────────────────

def smooth_plot(
    x,
    y,
    method: str = "lowess",
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8.5, 5),
    data_color: str = "#9DB8C9",
    smooth_color: str = "#C73E1D",
    data_size: float = 18,
    frac: float = 0.3,
    window: int = 11,
    polyorder: int = 2,
    show_residual_rms: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Noisy series with a robust smooth overlay — LOESS (statsmodels or
    scipy fallback), Savitzky–Golay, or moving average. Makes the
    underlying trend visible without pretending to be a model fit.

    Parameters
    ----------
    method : str
        'lowess', 'savgol' or 'moving'.
    frac : float
        LOESS smoothing fraction (lower = wigglier).

    Returns
    -------
    Figure
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    order = np.argsort(x_arr)
    xs, ys = x_arr[order], y_arr[order]

    if method == "lowess":
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            smoothed = lowess(ys, xs, frac=frac, return_sorted=True)
            xs_s, ys_s = smoothed[:, 0], smoothed[:, 1]
        except ImportError:
            from scipy.ndimage import uniform_filter1d
            ys_s = uniform_filter1d(ys, size=max(5, int(len(ys) * frac)))
            xs_s = xs
    elif method == "savgol":
        from scipy.signal import savgol_filter
        w = min(window if window % 2 else window + 1, len(ys) - 1)
        if w % 2 == 0:
            w -= 1
        ys_s = savgol_filter(ys, max(w, polyorder + 2), polyorder)
        xs_s = xs
    elif method == "moving":
        from scipy.ndimage import uniform_filter1d
        ys_s = uniform_filter1d(ys, size=max(3, window))
        xs_s = xs
    else:
        raise ValueError("method must be 'lowess', 'savgol' or 'moving'.")

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.scatter(xs, ys, s=data_size, color=data_color, alpha=0.8, lw=0,
               label="data", zorder=2)
    ax.plot(xs_s, ys_s, color=smooth_color, lw=2.4,
            label=f"{method} smooth", zorder=3)
    if show_residual_rms:
        rms = float(np.sqrt(np.mean((ys - np.interp(xs, xs_s, ys_s)) ** 2)))
        ax.text(0.98, 0.04, f"RMS residual = {rms:.3g}",
                transform=ax.transAxes, ha="right", fontsize=8.5,
                color="#555555",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="best")
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SCATTER  +  KDE  CONTOURS
# ──────────────────────────────────────────────

def scatter_contour(
    x,
    y,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (7.5, 6),
    color: str = "#2E86AB",
    contour_color: str = "#C73E1D",
    levels: int = 8,
    point_size: float = 16,
    fill: bool = False,
    fill_alpha: float = 0.12,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Scatter with kernel-density contours — where are the mass and the
    outliers? Softer than hexbin for medium-sized samples.

    Returns
    -------
    Figure
    """
    from scipy.stats import gaussian_kde

    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    kde = gaussian_kde(np.vstack([x_arr, y_arr]))

    xg = np.linspace(x_arr.min() - 0.1 * np.ptp(x_arr),
                     x_arr.max() + 0.1 * np.ptp(x_arr), 180)
    yg = np.linspace(y_arr.min() - 0.1 * np.ptp(y_arr),
                     y_arr.max() + 0.1 * np.ptp(y_arr), 180)
    Xg, Yg = np.meshgrid(xg, yg)
    Zg = kde(np.vstack([Xg.ravel(), Yg.ravel()])).reshape(Xg.shape)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    if fill:
        ax.contourf(Xg, Yg, Zg, levels=levels, cmap="Blues", alpha=fill_alpha * 5)
    ax.contour(Xg, Yg, Zg, levels=levels, colors=contour_color,
               linewidths=0.9, alpha=0.8)
    ax.scatter(x_arr, y_arr, s=point_size, color=color, alpha=0.65,
               edgecolors="none", zorder=3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="none")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DIVERGING  BAR  (signed values)
# ──────────────────────────────────────────────

def diverging_bar(
    labels: Sequence[str],
    values: Sequence[float],
    title: str | None = None,
    xlabel: str = "",
    figsize: tuple = (8.5, 5),
    positive_color: str = "#2A9D8F",
    negative_color: str = "#E76F51",
    show_values: bool = True,
    value_fmt: str = "{:+.2f}",
    sort: str = "none",
    grid: str = "x",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Signed bar chart around a zero line — contributions, deviations
    from baseline, profit/loss, YoY change.

    Parameters
    ----------
    sort : str
        'none', 'asc' or 'desc' ordering by value.

    Returns
    -------
    Figure
    """
    values = np.asarray(values, float)
    labels = [str(l) for l in labels]
    if sort == "asc":
        order = np.argsort(values)
    elif sort == "desc":
        order = np.argsort(-values)
    else:
        order = np.arange(len(values))
    values = values[order]
    labels = [labels[i] for i in order]
    ypos = np.arange(len(values))[::-1]
    colors = [positive_color if v >= 0 else negative_color for v in values]

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.barh(ypos, values, color=colors, alpha=0.9, height=0.62,
            edgecolor="white", lw=0.6)
    ax.axvline(0, color="#666666", lw=1)
    if show_values:
        span = values.max() - values.min() or 1
        for y, v in zip(ypos, values):
            ax.text(v + (span * 0.015 if v >= 0 else -span * 0.015), y,
                    value_fmt.format(v), va="center",
                    ha="left" if v >= 0 else "right", fontsize=8,
                    color="#333333")
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(values.min() - span * 0.12, values.max() + span * 0.12)
    ax.set_xlabel(xlabel)
    axis_config(ax, grid=grid)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PARETO  CHART  (frequency + cumulative %)
# ──────────────────────────────────────────────

def pareto_chart(
    labels: Sequence[str],
    counts: Sequence[float],
    title: str | None = None,
    ylabel: str = "count",
    figsize: tuple = (9, 5.5),
    bar_color: str = "#2E86AB",
    cumulative_color: str = "#C73E1D",
    threshold: float = 0.8,
    show_threshold: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Pareto chart — descending frequency bars with a cumulative-% line
    and the 80% guide. The classic "vital few, trivial many" figure
    (note: different from `pareto_front`, the multi-objective chart).

    Returns
    -------
    Figure
    """
    counts = np.asarray(counts, float)
    order = np.argsort(-counts)
    counts = counts[order]
    labels = [str(labels[i]) for i in order]
    cum = np.cumsum(counts) / counts.sum()

    fig, ax1 = setup_figure(figsize, style="nature", **kwargs)
    ax1.bar(range(len(counts)), counts, color=bar_color, alpha=0.9,
            width=0.68, edgecolor="white", lw=0.5)
    ax1.set_xticks(range(len(counts)))
    ax1.set_xticklabels(labels, fontsize=9, rotation=30, ha="right")
    ax1.set_ylabel(ylabel, color=bar_color)
    ax1.tick_params(axis="y", labelcolor=bar_color)

    ax2 = ax1.twinx()
    ax2.plot(range(len(counts)), cum, "-o", color=cumulative_color,
             lw=1.9, ms=4.5)
    ax2.set_ylabel("cumulative share", color=cumulative_color)
    ax2.tick_params(axis="y", labelcolor=cumulative_color)
    ax2.set_ylim(0, 1.05)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))

    if show_threshold:
        ax2.axhline(threshold, color="#888888", lw=1, ls="--")
        k = int(np.searchsorted(cum, threshold))
        ax2.axvline(k - 0.5, color="#888888", lw=1, ls=":")
        ax2.annotate(f"{k} items = {cum[k - 1]:.0%}",
                     xy=(k - 0.5, threshold), xytext=(12, -20),
                     textcoords="offset points", fontsize=9,
                     color="#1D3557")

    axis_config(ax1, grid="y")
    if title:
        ax1.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PCA  BIPLOT  (scores + loadings)
# ──────────────────────────────────────────────

def biplot(
    data,
    labels: Sequence[str] | None = None,
    groups: Sequence | None = None,
    title: str | None = None,
    figsize: tuple = (9, 7),
    palette: str = "nature_qual",
    standardize: bool = True,
    n_arrows: int | None = None,
    arrow_scale: float = 3.2,
    point_size: float = 30,
    show_variance: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    PCA biplot — sample scores as points, variable loadings as arrows
    from the origin. One figure answers "which variables drive PC1/PC2
    and how do samples arrange along them".

    Parameters
    ----------
    data : 2-D array-like (n_samples × n_features)
    labels : per-sample annotations, optional
    groups : per-sample category, optional (colors points by group)
    n_arrows : int, optional
        Show only the n strongest-loading variables (default: all).

    Returns
    -------
    Figure
    """
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    arr = np.asarray(data, dtype=float)
    if standardize:
        arr = StandardScaler().fit_transform(arr)
    pca = PCA(n_components=2).fit(arr)
    scores = pca.transform(arr)
    loadings = pca.components_.T  # (n_features, 2)
    names = list(labels) if labels is not None else (
        [str(c) for c in getattr(data, "columns",
                                 [f"V{i + 1}" for i in range(arr.shape[1])])]
        if hasattr(data, "columns")
        else [f"V{i + 1}" for i in range(arr.shape[1])])
    if n_arrows is not None and len(names) > n_arrows:
        strength = np.hypot(loadings[:, 0], loadings[:, 1])
        keep = np.argsort(-strength)[:n_arrows]
        mask = np.zeros(len(names), dtype=bool)
        mask[keep] = True
    else:
        mask = np.ones(len(names), dtype=bool)

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if groups is not None:
        cats = list(dict.fromkeys(groups))
        colors = auto_colors(len(cats), palette)
        for cat, c in zip(cats, colors):
            m = np.asarray([g == cat for g in groups])
            ax.scatter(scores[m, 0], scores[m, 1], s=point_size, color=c,
                       alpha=0.8, edgecolors="white", lw=0.5,
                       label=str(cat), zorder=3)
        ax.legend(frameon=False, loc="best")
    else:
        ax.scatter(scores[:, 0], scores[:, 1], s=point_size,
                   color=auto_colors(1, palette)[0], alpha=0.8,
                   edgecolors="white", lw=0.5, zorder=3)

    scale = np.abs(scores[:, :2]).max() * 0.9
    arrow_len = np.abs(loadings).max() or 1
    for i, (name, (lx, ly)) in enumerate(zip(names, loadings)):
        if not mask[i]:
            continue
        ax.annotate(
            "", xy=(lx * scale / arrow_len, ly * scale / arrow_len),
            xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#C73E1D",
                                           lw=1.4),
            zorder=4,
        )
        ax.text(lx * scale / arrow_len * 1.12, ly * scale / arrow_len * 1.12,
                str(name), ha="center", va="center", fontsize=9,
                color="#C73E1D",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.75))

    ax.axhline(0, color="#999999", lw=0.7, ls="--", zorder=1)
    ax.axvline(0, color="#999999", lw=0.7, ls="--", zorder=1)
    pc1, pc2 = pca.explained_variance_ratio_
    if show_variance:
        ax.set_xlabel(f"PC1 ({pc1:.0%} variance)")
        ax.set_ylabel(f"PC2 ({pc2:.0%} variance)")
    else:
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  TWO-SAMPLE  KS  TEST
# ──────────────────────────────────────────────

def ks_test(
    sample1,
    sample2,
    title: str | None = None,
    label1: str = "sample 1",
    label2: str = "sample 2",
    figsize: tuple = (8, 5),
    color1: str = "#2E86AB",
    color2: str = "#C73E1D",
    show_stat: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Two-sample Kolmogorov–Smirnov test visualized: both empirical CDFs
    with the D-statistic distance marked at its argmax.

    Returns
    -------
    Figure
    """
    from scipy import stats as sps

    v1 = np.sort(_to_1d(sample1))
    v2 = np.sort(_to_1d(sample2))
    stat, p_value = sps.ks_2samp(v1, v2)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    for v, c, lab in ((v1, color1, label1), (v2, color2, label2)):
        p = np.arange(1, len(v) + 1) / len(v)
        ax.step(v, p, where="post", color=c, lw=1.9, label=lab)

    # mark the maximum vertical distance
    grid = np.linspace(min(v1[0], v2[0]), max(v1[-1], v2[-1]), 1200)
    cdf1 = np.searchsorted(v1, grid, side="right") / len(v1)
    cdf2 = np.searchsorted(v2, grid, side="right") / len(v2)
    gap = np.abs(cdf1 - cdf2)
    k = int(np.argmax(gap))
    xk = grid[k]
    ax.plot([xk, xk], [cdf1[k], cdf2[k]], color="#1D3557", lw=2.4,
            solid_capstyle="round", zorder=5)
    ax.annotate(f"D = {gap[k]:.3f}\np = {p_value:.3g}",
                xy=(xk, (cdf1[k] + cdf2[k]) / 2), xytext=(18, 0),
                textcoords="offset points", fontsize=10, color="#1D3557",
                va="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.set_xlabel("value")
    ax.set_ylabel("Empirical CDF")
    ax.legend(frameon=False, loc="lower right")
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  RANGE  /  SCENARIO  PLOT
# ──────────────────────────────────────────────

def range_plot(
    labels: Sequence[str],
    low: Sequence[float],
    mid: Sequence[float],
    high: Sequence[float],
    title: str | None = None,
    xlabel: str = "",
    figsize: tuple = (8.5, 5),
    color: str = "#2E86AB",
    mid_color: str = "#C73E1D",
    cap_size: float = 5,
    bar_height: float = 0.34,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Scenario range chart — best/base/worst intervals per option, drawn
    as floating range bars with a median dot. The clear way to compare
    uncertain outcomes across alternatives.

    Returns
    -------
    Figure
    """
    low = np.asarray(low, float)
    mid = np.asarray(mid, float)
    high = np.asarray(high, float)
    ypos = np.arange(len(labels))[::-1]

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    for y, lo, md, hi in zip(ypos, low, mid, high):
        ax.plot([lo, hi], [y, y], color=color, lw=5, alpha=0.55,
                solid_capstyle="round", zorder=2)
        ax.plot([lo, lo], [y - bar_height / 2, y + bar_height / 2],
                color=color, lw=1.6, zorder=3)
        ax.plot([hi, hi], [y - bar_height / 2, y + bar_height / 2],
                color=color, lw=1.6, zorder=3)
        ax.plot([md], [y], "o", ms=7, mfc=mid_color, mec="white", mew=1.1,
                zorder=4)
        if show_values:
            ax.text(hi + (hi - low).max() * 0.015, y,
                    f"{value_fmt.format(lo)} – {value_fmt.format(hi)}",
                    va="center", fontsize=8, color="#555555")

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlim(min(low) - (np.max(high) - np.min(low)) * 0.06,
                max(high) + (np.max(high) - np.min(low)) * 0.14)
    ax.set_xlabel(xlabel)
    axis_config(ax, grid="x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CALENDAR  HEATMAP
# ──────────────────────────────────────────────

def calendar_heatmap(
    values,
    start_date: str = "2025-01-01",
    title: str | None = None,
    figsize: tuple | None = None,
    cmap: str = "YlGnBu",
    day_labels: bool = True,
    month_labels: bool = True,
    show_colorbar: bool = True,
    cbar_label: str = "",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    GitHub-style calendar heatmap — one cell per day, weeks as columns,
    weekdays as rows. Perfect for daily simulation results, demand,
    or activity data.

    Parameters
    ----------
    values : 1-D array-like
        One value per consecutive day starting at ``start_date``.
    start_date : str
        ISO date of the first value.

    Returns
    -------
    Figure
    """
    import datetime as _dt

    vals = np.asarray(values, dtype=float).ravel()
    n = len(vals)
    d0 = _dt.date.fromisoformat(start_date)
    weekday0 = d0.weekday()  # Monday = 0
    n_rows, n_cols = 7, int(np.ceil((weekday0 + n) / 7))

    grid = np.full((n_rows, n_cols), np.nan)
    for i, v in enumerate(vals):
        pos = weekday0 + i
        grid[pos % 7, pos // 7] = v

    if figsize is None:
        figsize = (max(9, n_cols * 0.24 + 2), 2.4)
    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)

    masked = np.ma.masked_invalid(grid)
    im = ax.pcolormesh(masked, cmap=cmap, edgecolors="white", linewidth=1.1)

    if day_labels:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ax.set_yticks(np.arange(7) + 0.5)
        ax.set_yticklabels(days, fontsize=7.5)
    else:
        ax.set_yticks([])
    if month_labels:
        month_ticks, month_names, seen = [], [], None
        for i in range(n):
            d = d0 + _dt.timedelta(days=i)
            if d.month != seen:
                col = (weekday0 + i) // 7
                if not month_ticks or col - month_ticks[-1] >= 3:
                    month_ticks.append(col)
                    month_names.append(d.strftime("%b"))
                seen = d.month
        ax.set_xticks(np.asarray(month_ticks) + 0.5)
        ax.set_xticklabels(month_names, fontsize=8)
    else:
        ax.set_xticks([])
    ax.invert_yaxis()
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    if show_colorbar:
        cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.015)
        if cbar_label:
            cb.set_label(cbar_label, fontsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  GROUPED  SCATTER  (per-group regression)
# ──────────────────────────────────────────────

def grouped_scatter(
    x,
    y,
    groups,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8.5, 5.5),
    palette: str = "nature_qual",
    fit_each: bool = True,
    show_r2: bool = True,
    point_size: float = 30,
    fit_alpha: float = 0.85,
    legend_loc: str = "best",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Scatter colored by group with an independent regression line (and
    R²) per group — "does the relationship differ across segments?"

    Returns
    -------
    Figure
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    cats = list(dict.fromkeys(groups))
    colors = auto_colors(len(cats), palette)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    for cat, c in zip(cats, colors):
        m = np.asarray([g == cat for g in groups])
        ax.scatter(x_arr[m], y_arr[m], s=point_size, color=c, alpha=0.8,
                   edgecolors="white", lw=0.5, label=str(cat), zorder=3)
        if fit_each and m.sum() >= 3:
            b, a = np.polyfit(x_arr[m], y_arr[m], 1)
            xf = np.linspace(x_arr[m].min(), x_arr[m].max(), 40)
            ax.plot(xf, a + b * xf, color=c, lw=1.8, alpha=fit_alpha,
                    ls="--", zorder=2)
            if show_r2:
                yhat = a + b * x_arr[m]
                ss_res = float(np.sum((y_arr[m] - yhat) ** 2))
                ss_tot = float(np.sum((y_arr[m] - y_arr[m].mean()) ** 2)) or 1
                ax.text(xf[-1], a + b * xf[-1], f"  R²={1 - ss_res / ss_tot:.2f}",
                        fontsize=7.5, color=c, va="center")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc=legend_loc)
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  BLAND–ALTMAN  (method comparison)
# ──────────────────────────────────────────────

def bland_altman(
    method1,
    method2,
    title: str | None = None,
    xlabel: str = "Mean of methods",
    ylabel: str = "Difference (method1 − method2)",
    figsize: tuple = (8, 5.5),
    color: str = "#2E86AB",
    agreement: float = 1.96,
    show_loa: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Bland–Altman agreement plot — bias and limits of agreement between
    two measurement methods (model outputs vs ground truth, sensor vs
    sensor).

    Returns
    -------
    Figure
    """
    m1 = _to_1d(method1)
    m2 = _to_1d(method2)
    mean_pair = (m1 + m2) / 2
    diff = m1 - m2
    bias = float(diff.mean())
    sd = float(diff.std())
    loa_lo, loa_hi = bias - agreement * sd, bias + agreement * sd

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.scatter(mean_pair, diff, s=32, color=color, alpha=0.75,
               edgecolors="white", lw=0.5, zorder=3)
    ax.axhline(bias, color="#C73E1D", lw=1.5,
               label=f"bias = {bias:.3g}")
    if show_loa:
        for v, lab in ((loa_hi, f"+{agreement:g}·SD = {loa_hi:.3g}"),
                       (loa_lo, f"−{agreement:g}·SD = {loa_lo:.3g}")):
            ax.axhline(v, color="#888888", lw=1.1, ls="--")
            ax.text(0.99, v, f" {lab}", transform=ax.get_yaxis_transform(),
                    ha="right", va="bottom", fontsize=8, color="#666666")
    ax.axhline(0, color="#BBBBBB", lw=0.8, ls=":")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="upper right")
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  HYPOTHESIS  TEST  VISUALIZATION
# ──────────────────────────────────────────────

def hypothesis_test(
    data,
    mu: float = 0.0,
    test: str = "t",
    alternative: str = "two-sided",
    alpha: float = 0.05,
    title: str | None = None,
    xlabel: str = "test statistic",
    figsize: tuple = (8.5, 5),
    color: str = "#2E86AB",
    reject_color: str = "#C73E1D",
    fill_alpha: float = 0.85,
    show_data_mean: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Test statistic distribution with shaded rejection region(s) —
    makes alpha, the critical value, and the p-value visible at once.

    Parameters
    ----------
    data : 1-D sample
    mu : float
        Null-hypothesis mean.
    test : str
        't' (one-sample t-test) or 'z'.
    alternative : str
        'two-sided', 'less' or 'greater'.

    Returns
    -------
    Figure
    """
    from scipy import stats as sps

    values = _to_1d(data)
    values = values[~np.isnan(values)]
    n = len(values)
    if n < 2:
        raise ValueError("hypothesis_test needs at least 2 observations.")

    if test == "t":
        stat, p_value = sps.ttest_1samp(values, mu)
        df = n - 1
        dist, pdf = df, sps.t.pdf
        if alternative == "two-sided":
            crit = sps.t.ppf(1 - alpha / 2, df)
        else:
            crit = sps.t.ppf(1 - alpha, df)
    elif test == "z":
        se = values.std(ddof=1) / np.sqrt(n) or 1
        stat = (values.mean() - mu) / se
        p_value = 2 * (1 - sps.norm.cdf(abs(stat))) if alternative == "two-sided" \
            else (1 - sps.norm.cdf(stat) if alternative == "greater"
                  else sps.norm.cdf(stat))
        dist, pdf = None, sps.norm.pdf
        crit = sps.norm.ppf(1 - alpha / 2) if alternative == "two-sided" \
            else sps.norm.ppf(1 - alpha)
    else:
        raise ValueError("test must be 't' or 'z'.")

    x = np.linspace(-4.2, 4.2, 500)
    y = pdf(x, dist) if dist is not None else pdf(x)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.plot(x, y, color=color, lw=2.2)
    ax.fill_between(x, y, color=color, alpha=0.12, lw=0)

    def shade(x0, x1):
        m = np.logical_and(x >= x0, x <= x1)
        ax.fill_between(x[m], y[m], color=reject_color, alpha=fill_alpha, lw=0)

    if alternative == "two-sided":
        shade(-4.2, -crit)
        shade(crit, 4.2)
        crit_label = f"±{crit:.2f}"
    elif alternative == "greater":
        shade(crit, 4.2)
        crit_label = f"{crit:.2f}"
    else:
        shade(-4.2, -crit)
        crit_label = f"−{crit:.2f}"

    zc = 1.96 if test == "z" else crit
    ax.annotate(
        f"stat = {stat:.3f}\np = {p_value:.4g}",
        xy=(np.clip(stat, -4.2, 4.2), float(pdf(np.clip(stat, -4.2, 4.2), dist)) if dist is not None else float(pdf(np.clip(stat, -4.2, 4.2)))),
        xytext=(0.97, 0.92), textcoords="axes fraction", ha="right",
        va="top", fontsize=10, color="#1D3557",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  edgecolor="#CCCCCC"),
        arrowprops=dict(arrowstyle="-|>", color="#666666", lw=1),
    )
    ax.text(0.03, 0.92,
            f"H0: μ = {mu:g}   α = {alpha:g}   reject if |stat| > {crit_label}"
            if alternative == "two-sided" else
            f"H0: μ = {mu:g}   α = {alpha:g}",
            transform=ax.transAxes, fontsize=9, color="#555555")

    ax.set_yticks([])
    ax.set_xlabel(xlabel)
    for spine in ("left",):
        ax.spines[spine].set_visible(False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  LORENZ  CURVE  (Gini)
# ──────────────────────────────────────────────

def lorenz_curve(
    data,
    title: str | None = None,
    xlabel: str = "Cumulative share of population",
    ylabel: str = "Cumulative share of value",
    figsize: tuple = (6.5, 6),
    color: str = "#2E86AB",
    show_gini: bool = True,
    compare_bars: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Lorenz curve with Gini coefficient — income/inequality analysis,
    concentration of demand, resource allocation fairness.

    Parameters
    ----------
    data : 1-D array-like of non-negative values

    Returns
    -------
    Figure
    """
    v = np.sort(_to_1d(data).clip(min=0))
    total = v.sum()
    if total <= 0:
        raise ValueError("lorenz_curve needs positive values.")
    cum = np.concatenate([[0.0], np.cumsum(v) / total])
    pop = np.linspace(0, 1, len(v) + 1)

    gini = float(1 - 2 * np.trapezoid(cum, pop)) if hasattr(np, "trapezoid") \
        else float(1 - 2 * np.trapz(cum, pop))

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.fill_between(pop, cum, pop, color=color, alpha=0.15, lw=0)
    ax.plot(pop, cum, color=color, lw=2.2, label="Lorenz curve")
    ax.plot([0, 1], [0, 1], color="#999999", lw=1.2, ls="--", label="equality")

    if compare_bars:
        # where the poorest half holds only X% of the total
        half = float(np.interp(0.5, pop, cum))
        ax.plot([0, 0.5, 0.5], [half, half, 0], color="#F18F01", lw=1,
                ls=":")
        ax.annotate(f"bottom 50% → {half:.0%}", xy=(0.5, half),
                    xytext=(10, 12), textcoords="offset points",
                    fontsize=8.5, color="#B25E00")
    if show_gini:
        ax.text(0.05, 0.90, f"Gini = {gini:.3f}", transform=ax.transAxes,
                fontsize=11, fontweight="bold", color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC"))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="lower right")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  FORECAST  (history + prediction + band)
# ──────────────────────────────────────────────

def forecast(
    history,
    predicted,
    lower=None,
    upper=None,
    title: str | None = None,
    xlabel: str = "time",
    ylabel: str = "value",
    figsize: tuple = (10, 5.5),
    history_color: str = "#2E86AB",
    forecast_color: str = "#C73E1D",
    band_alpha: float = 0.15,
    connect: bool = True,
    split_marker: bool = True,
    history_label: str = "history",
    forecast_label: str = "forecast",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Time-series forecast chart — history line, predicted segment, and
    the confidence band between them. The standard figure for
    prediction questions (GM(1,1), ARIMA, LSTM outputs).

    Parameters
    ----------
    history : 1-D array-like
        Observed values.
    predicted : 1-D array-like
        Forecast values (may or may not include the last observed point).
    lower, upper : 1-D array-like, optional
        Confidence band for the forecast.

    Returns
    -------
    Figure
    """
    h = np.asarray(history, dtype=float)
    p = np.asarray(predicted, dtype=float)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ih = np.arange(len(h))
    ip = np.arange(len(h) - (1 if connect else 0), len(h) + len(p))

    if connect and len(p) > 0:
        p_plot = np.concatenate([[h[-1]], p])
    else:
        p_plot = p
        ip = np.arange(len(h), len(h) + len(p))

    ax.plot(ih, h, color=history_color, lw=2, marker="o", ms=3.5,
            label=history_label)
    ax.plot(ip, p_plot, color=forecast_color, lw=2, marker="s", ms=3.5,
            ls="--", label=forecast_label)

    if lower is not None and upper is not None:
        lo = np.asarray(lower, dtype=float)
        up = np.asarray(upper, dtype=float)
        if connect and len(lo) == len(p):
            lo = np.concatenate([[h[-1]], lo])
            up = np.concatenate([[h[-1]], up])
        ax.fill_between(ip, lo, up, color=forecast_color, alpha=band_alpha,
                        lw=0, label="confidence band")

    if split_marker:
        split_x = len(h) - 1
        ax.axvline(split_x, color="#999999", lw=1, ls=":")
        ax.text(split_x, ax.get_ylim()[1], "  now", fontsize=8.5,
                color="#888888", va="top")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="upper left")
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig
