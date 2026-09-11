"""
basic.py — Basic statistical charts for math modeling papers.

All functions return a matplotlib Figure object ready for publication.

Charts:
    bar_chart          — standard bar chart
    horizontal_bar     — horizontal bar chart
    grouped_bar        — grouped / side-by-side bars
    stacked_bar        — stacked bar chart
    line_chart         — multi-line chart
    scatter_plot       — scatter plot with optional fit
    area_chart         — area / filled line chart
    pie_chart          — pie chart with percentage labels
    donut_chart        — donut chart
    histogram          — frequency distribution
    box_plot           — box plot
    violin_plot        — violin plot
    heatmap          — correlation / data heatmap
    step_chart         — step chart
"""

from __future__ import annotations

from typing import Optional, Sequence, Union
import warnings

import matplotlib.pyplot as plt
import numpy as np

from .palette import auto_colors, get_palette, NEUTRAL, ACCENT
from .styles import apply_style
from .utils import (
    setup_figure, save_figure, format_numbers,
    axis_config, add_data_labels, auto_layout,
)


# ──────────────────────────────────────────────
#  BAR  CHARTS
# ──────────────────────────────────────────────

def bar_chart(
    data: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (8, 5),
    horizontal: bool = False,
    bar_width: float = 0.6,
    edge_color: str = "white",
    edge_width: float = 0.8,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    value_fontsize: float = 8,
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a publication-quality bar chart.

    Parameters
    ----------
    data : array-like
        Bar heights.
    labels : list of str, optional
        Category labels.
    title : str, optional
    xlabel, ylabel : str, optional
    palette : str
        Color palette name.
    figsize : tuple
    horizontal : bool
        Horizontal bars (barh).
    bar_width : float
        Width (vertical) or height (horizontal) of bars.
    edge_color, edge_width : str, float
    show_values : bool
        Show numeric labels on top of bars.
    value_fmt : str
        Format string for value labels.
    grid : str
        'y', 'x', 'both', 'none'.
    save_path : str, optional
        If provided, saves the figure.

    Returns
    -------
    Figure
    """
    fig, ax = setup_figure(figsize, **kwargs)
    colors = auto_colors(len(data), palette)

    if horizontal:
        bars = ax.barh(
            range(len(data)), data, color=colors,
            edgecolor=edge_color, linewidth=edge_width,
            height=bar_width,
        )
        if labels:
            ax.set_yticks(range(len(data)))
            ax.set_yticklabels(labels, fontsize=9)
        if show_values:
            add_data_labels(bars, ax, fmt=value_fmt,
                            fontsize=value_fontsize, horizontal=True)
        if grid != "none":
            axis_config(ax, grid="x")
    else:
        bars = ax.bar(
            range(len(data)), data, color=colors,
            edgecolor=edge_color, linewidth=edge_width,
            width=bar_width,
        )
        if labels:
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(labels, fontsize=9)
        if show_values:
            add_data_labels(bars, ax, fmt=value_fmt,
                            fontsize=value_fontsize)
        if grid != "none":
            axis_config(ax, grid="y")

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    ax.tick_params(axis="both", labelsize=9)

    # Add subtle value gridlines
    if grid in ("y", "both") and not horizontal:
        ax.set_yticks(np.linspace(0, max(data) * 1.1, 6))

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)

    return fig


def grouped_bar(
    data: dict[str, Sequence[float]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (10, 6),
    bar_width: float = 0.25,
    edge_color: str = "white",
    edge_width: float = 0.6,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    value_fontsize: float = 7,
    grid: str = "y",
    legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a grouped (side-by-side) bar chart.

    Parameters
    ----------
    data : dict[str, list]
        Keys are group names, values are data arrays.
    labels : list of str, optional
        X-axis category labels.
    ...
    """
    groups = list(data.keys())
    n_groups = len(groups)
    n_categories = len(next(iter(data.values())))
    x = np.arange(n_categories)
    colors = auto_colors(n_groups, palette)

    fig, ax = setup_figure(figsize, **kwargs)

    for i, (group, values) in enumerate(data.items()):
        offset = (i - n_groups / 2 + 0.5) * bar_width
        bars = ax.bar(
            x + offset, values, width=bar_width,
            label=group, color=colors[i],
            edgecolor=edge_color, linewidth=edge_width,
        )
        if show_values:
            add_data_labels(bars, ax, fmt=value_fmt,
                            fontsize=value_fontsize)

    if labels:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)

    if legend:
        ax.legend(frameon=False, fontsize=9, loc="upper right")

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


def stacked_bar(
    data: dict[str, Sequence[float]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (8, 5),
    edge_color: str = "white",
    edge_width: float = 0.4,
    show_values: bool = False,
    value_fmt: str = "{:.1f}",
    value_fontsize: float = 7,
    grid: str = "y",
    legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a stacked bar chart.

    Parameters
    ----------
    data : dict[str, list]
        Keys are component names, values are data arrays.
    labels : list of str, optional
        X-axis category labels.
    show_values : bool
        Show values inside each segment (recommended for small counts).
    """
    groups = list(data.keys())
    n_groups = len(groups)
    n_categories = len(next(iter(data.values())))
    x = np.arange(n_categories)
    colors = auto_colors(n_groups, palette)

    fig, ax = setup_figure(figsize, **kwargs)
    bottom = np.zeros(n_categories)

    for i, (group, values) in enumerate(data.items()):
        values = np.array(values, dtype=float)
        bars = ax.bar(
            x, values, bottom=bottom, width=0.6,
            label=group, color=colors[i],
            edgecolor=edge_color, linewidth=edge_width,
        )
        if show_values:
            mid = bottom + values / 2
            for j, (v, m) in enumerate(zip(values, mid)):
                ax.text(x[j], m, value_fmt.format(v),
                        ha="center", va="center",
                        fontsize=value_fontsize,
                        color="#333333")
        bottom += values

    if labels:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)

    if legend:
        ax.legend(frameon=False, fontsize=9, loc="upper right")

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  LINE  CHART
# ──────────────────────────────────────────────

def line_chart(
    x: Sequence[float],
    y_series: Union[Sequence[float], dict[str, Sequence[float]]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (10, 6),
    markers: bool = False,
    marker_size: float = 5,
    line_width: float = 2.0,
    fill_between: bool = False,
    fill_alpha: float = 0.15,
    grid: str = "both",
    legend: bool = True,
    legend_loc: str = "upper right",
    error_bars: bool = False,
    error_alpha: float = 0.2,
    annotate_last: bool = False,
    annotate_last_fontsize: float = 9,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a multi-line chart.

    Parameters
    ----------
    x : array-like
        X-axis values.
    y_series : list of arrays OR dict[str, array]
        If list, labels are used. If dict, keys become legend labels.
    labels : list of str, optional
        Legend labels when y_series is a list.
    markers : bool
        Show markers at data points.
    marker_size : float
    line_width : float
    fill_between : bool
        Fill area between lines (for stacked area effect).
    fill_alpha : float
    grid : str
        'x', 'y', 'both', 'none'.
    legend : bool
    legend_loc : str
    error_bars : bool
        Show confidence band (±1 std or ±error if provided).
    error_alpha : float
    annotate_last : bool
        Add label at the end of each line.
    annotate_last_fontsize : float
    save_path : str, optional
    """
    fig, ax = setup_figure(figsize, **kwargs)

    # Normalize to list of (label, y_data)
    if isinstance(y_series, dict):
        series = list(y_series.values())
        series_labels = list(y_series.keys())
    elif isinstance(y_series, list) and len(y_series) > 0 and isinstance(y_series[0], (list, tuple, np.ndarray)):
        # List of series (list of lists/arrays)
        series = y_series
        series_labels = labels or [f"Series {i+1}" for i in range(len(series))]
    else:
        # Single series (list of scalars or scalar)
        series = [y_series]
        series_labels = labels or ["Series 1"]

    colors = auto_colors(len(series), palette)
    x_arr = np.array(x, dtype=float)

    for i, (y_data, lbl) in enumerate(zip(series, series_labels)):
        y = np.array(y_data, dtype=float)
        style_kwargs = dict(
            color=colors[i], linewidth=line_width,
            marker="o" if markers else None,
            markersize=marker_size,
            label=lbl,
            zorder=3,
        )
        line, = ax.plot(x_arr, y, **style_kwargs)

        if fill_between and len(series) == 1:
            ax.fill_between(x_arr, y, alpha=fill_alpha, color=colors[i])

        if error_bars and len(y) > 1:
            # Use ±1 std as default error
            std = np.std(y)
            ax.fill_between(x_arr, y - std, y + std,
                            alpha=error_alpha, color=colors[i],
                            label=f"{lbl} ±σ" if i == 0 else None)

        if annotate_last and len(y) > 0:
            ax.annotate(
                lbl, xy=(x_arr[-1], y[-1]),
                xytext=(5, 0), textcoords="offset points",
                fontsize=annotate_last_fontsize, color=colors[i],
                va="center", fontweight="bold",
            )

    if legend and len(series) > 1:
        ax.legend(frameon=False, fontsize=9, loc=legend_loc)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)

    # Set nice y-limits
    all_y = np.concatenate(series) if series else np.array([0])
    y_margin = (all_y.max() - all_y.min()) * 0.1
    ax.set_ylim(all_y.min() - y_margin, all_y.max() + y_margin)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  AREA  CHART
# ──────────────────────────────────────────────

def area_chart(
    x: Sequence[float],
    y_series: Union[Sequence[float], dict[str, Sequence[float]]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (10, 6),
    alpha: float = 0.7,
    stacked: bool = True,
    grid: str = "y",
    legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a filled area chart (stacked or overlay).

    Parameters
    ----------
    stacked : bool
        Stacked area (default) or overlay.
    alpha : float
        Fill transparency.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    if isinstance(y_series, dict):
        series = list(y_series.values())
        series_labels = list(y_series.keys())
    else:
        series = y_series if isinstance(y_series, list) else [y_series]
        series_labels = labels or [f"Series {i+1}" for i in range(len(series))]

    colors = auto_colors(len(series), palette)
    x_arr = np.array(x, dtype=float)

    if stacked:
        bottoms = np.zeros(len(x_arr))
        for i, (y_data, lbl) in enumerate(zip(series, series_labels)):
            y = np.array(y_data, dtype=float)
            ax.fill_between(
                x_arr, bottoms, bottoms + y,
                alpha=alpha, color=colors[i],
                label=lbl, edgecolor="white", linewidth=0.5,
            )
            bottoms += y
    else:
        for i, (y_data, lbl) in enumerate(zip(series, series_labels)):
            y = np.array(y_data, dtype=float)
            ax.fill_between(x_arr, y, alpha=alpha, color=colors[i], label=lbl)

    if legend:
        ax.legend(frameon=False, fontsize=9, loc="upper right")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SCATTER  PLOT
# ──────────────────────────────────────────────

def scatter_plot(
    x: Sequence[float],
    y: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (8, 6),
    size: float = 50,
    alpha: float = 0.7,
    edgecolor: str = "white",
    edge_width: float = 0.5,
    show_fit: bool = False,
    fit_degree: int = 2,
    fit_color: str = "#C73E1D",
    show_labels: bool = False,
    label_fontsize: float = 8,
    label_offset: tuple = (5, 5),
    grid: str = "both",
    legend: bool = False,
    color_by: Sequence | None = None,
    colormap: str = "viridis",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a scatter plot.

    Parameters
    ----------
    x, y : array-like
        X and Y coordinates.
    labels : list of str, optional
        Point labels.
    size : float
        Marker size.
    alpha : float
        Marker transparency.
    show_fit : bool
        Add polynomial fit line.
    fit_degree : int
        Polynomial degree (default 2).
    fit_color : str
        Color of fit line.
    show_labels : bool
        Show point labels.
    label_offset : tuple
        (dx, dy) offset for labels in points.
    color_by : array-like, optional
        Color points by a third variable (values).
    colormap : str
        Colormap for color_by.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)

    if color_by is not None:
        cb = np.array(color_by, dtype=float)
        sc = ax.scatter(
            x_arr, y_arr, c=cb, cmap=colormap,
            s=size, alpha=alpha,
            edgecolor=edgecolor, linewidth=edge_width,
        )
        plt.colorbar(sc, ax=ax, shrink=0.8, label="Value")
    else:
        n = len(x_arr)
        colors = auto_colors(n, palette) if labels else [get_palette(palette)[0]] * n
        for i, (xi, yi) in enumerate(zip(x_arr, y_arr)):
            ax.scatter(
                xi, yi, s=size,
                c=[colors[i]], alpha=alpha,
                edgecolor=edgecolor, linewidth=edge_width,
            )

    if show_fit and len(x_arr) >= 2:
        coeffs = np.polyfit(x_arr, y_arr, fit_degree)
        x_fit = np.linspace(x_arr.min(), x_arr.max(), 200)
        y_fit = np.polyval(coeffs, x_fit)
        ax.plot(x_fit, y_fit, color=fit_color, linewidth=2,
                linestyle="--", alpha=0.8,
                label=f"Fit (degree {fit_degree})", zorder=5)
        if legend:
            ax.legend(frameon=False, fontsize=9)

    if show_labels and labels:
        for xi, yi, lbl in zip(x_arr, y_arr, labels):
            ax.annotate(
                lbl, xy=(xi, yi),
                xytext=label_offset, textcoords="offset points",
                fontsize=label_fontsize, color="#333333",
                ha="center", va="center",
            )

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)

    # Equal aspect if not specified
    ax.set_aspect("equal", adjustable="datalim")

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PIE  /  DONUT
# ──────────────────────────────────────────────

def pie_chart(
    data: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (6, 6),
    explode: Sequence[float] | float = 0.02,
    startangle: int = 90,
    autopct: str = "%.1f%%",
    pct_distance: float = 0.6,
    label_distance: float = 1.1,
    legend: bool = True,
    donut: bool = False,
    donut_width: float = 0.35,
    center_text: str = "",
    center_fontsize: float = 16,
    text_fontsize: float = 10,
    pct_fontsize: float = 9,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a pie or donut chart.

    Parameters
    ----------
    data : array-like
        Slice values.
    labels : list of str, optional
        Slice labels.
    explode : float or list
        How far each slice is from center.
    donut : bool
        If True, create a donut chart.
    donut_width : float
        Donut hole radius (0-1).
    """
    fig, ax = setup_figure(figsize)
    colors = auto_colors(len(data), palette)

    if isinstance(explode, (int, float)):
        explode = [explode] * len(data)

    wedges, texts, autotexts = ax.pie(
        data, labels=labels, autopct=autopct,
        startangle=startangle, explode=explode,
        colors=colors,
        pctdistance=pct_distance,
        labeldistance=label_distance,
        textprops={"fontsize": text_fontsize, "color": "#333333"},
        wedgeprops={
            "edgecolor": "white",
            "linewidth": 1.5,
        },
    )

    # Style percentage text
    for at in autotexts:
        at.set_fontsize(pct_fontsize)
        at.set_color("#333333")
        at.set_fontweight("bold")

    if donut:
        circle = plt.Circle((0, 0), donut_width, color="white", zorder=5)
        ax.add_artist(circle)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=15)

    if legend and labels:
        ax.legend(wedges, labels, frameon=False, fontsize=9, loc="upper right")

    ax.set_aspect("equal")
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


def donut_chart(
    data: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    center_text: str = "",
    center_fontsize: float = 16,
    **kwargs,
) -> plt.Figure:
    """
    Create a donut chart with center text.

    Parameters
    ----------
    center_text : str
        Text displayed in the center of the donut.
    """
    return pie_chart(
        data, labels=labels, title=title,
        donut=True, center_text=center_text,
        center_fontsize=center_fontsize,
        **kwargs,
    )


# ──────────────────────────────────────────────
#  HISTOGRAM
# ──────────────────────────────────────────────

def histogram(
    data: Union[Sequence[float], Sequence[Sequence[float]]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (8, 5),
    bins: int = 30,
    density: bool = False,
    kde: bool = True,
    kde_color: str = "#C73E1D",
    alpha: float = 0.7,
    edge_color: str = "white",
    edge_width: float = 0.5,
    grid: str = "y",
    legend: bool = True,
    log_scale: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a histogram with optional KDE curve.

    Parameters
    ----------
    data : array-like or list of arrays
        Data to plot.
    bins : int or array
        Number of bins or explicit bin edges.
    density : bool
        Normalize to probability density.
    kde : bool
        Overlay kernel density estimate.
    kde_color : str
    log_scale : bool
        Use log scale on y-axis.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    if not isinstance(data[0], (list, tuple, np.ndarray)):
        data = [data]
    n_series = len(data)
    colors = auto_colors(n_series, palette)

    for i, (d, lbl) in enumerate(zip(data, labels or range(1, n_series + 1))):
        d_arr = np.array(d, dtype=float)
        ax.hist(
            d_arr, bins=bins, alpha=alpha, color=colors[i],
            label=lbl, edgecolor=edge_color, linewidth=edge_width,
            density=density,
        )
        if kde:
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(d_arr)
            x_range = np.linspace(d_arr.min(), d_arr.max(), 300)
            y_kde = kde(x_range)
            if density:
                ax.plot(x_range, y_kde, color=kde_color,
                        linewidth=1.8, alpha=0.9, zorder=5)
            else:
                ax.plot(x_range, y_kde * len(d_arr) * (d_arr.max() - d_arr.min()) / len(d_arr),
                        color=kde_color, linewidth=1.8, alpha=0.9, zorder=5)

    if log_scale:
        ax.set_yscale("log")

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    if legend and n_series > 1:
        ax.legend(frameon=False, fontsize=9)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  BOX  PLOT
# ──────────────────────────────────────────────

def box_plot(
    data: Union[Sequence[float], Sequence[Sequence[float]]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (8, 5),
    horizontal: bool = False,
    show_outliers: bool = True,
    median_color: str = "#333333",
    mean_marker: str = "D",
    show_mean: bool = True,
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a box plot.

    Parameters
    ----------
    data : array-like or list of arrays
        Data to plot.
    labels : list of str, optional
        Category labels.
    horizontal : bool
        Horizontal box plot.
    show_outliers : bool
        Show outlier points.
    show_mean : bool
        Show mean as a diamond marker.
    mean_marker : str
        Marker style for mean.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    if not isinstance(data[0], (list, tuple, np.ndarray)):
        data = [data]
    n_series = len(data)
    colors = auto_colors(n_series, palette)

    bp = ax.boxplot(
        data,
        patch_artist=True,
        showfliers=show_outliers,
        flierprops=dict(marker="o", markersize=4, alpha=0.6),
        medianprops=dict(color=median_color, linewidth=1.5),
        whiskerprops=dict(color="#666666", linewidth=0.8),
        capprops=dict(color="#666666", linewidth=0.8),
        widths=0.6,
    )

    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i % len(colors)])
        patch.set_alpha(0.7)
        patch.set_edgecolor("white")
        patch.set_linewidth(0.5)

    # Add mean markers
    if show_mean:
        means = [np.mean(d) for d in data]
        positions = np.arange(1, n_series + 1)
        ax.scatter(
            positions if not horizontal else means,
            means if not horizontal else positions,
            marker=mean_marker, color=median_color,
            s=50, zorder=5, edgecolors="white", linewidth=0.5,
        )

    if labels:
        if horizontal:
            ax.set_yticks(np.arange(1, n_series + 1))
            ax.set_yticklabels(labels, fontsize=9)
        else:
            ax.set_xticks(np.arange(1, n_series + 1))
            ax.set_xticklabels(labels, fontsize=9)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  VIOLIN  PLOT
# ──────────────────────────────────────────────

def violin_plot(
    data: Union[Sequence[float], Sequence[Sequence[float]]],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (8, 5),
    horizontal: bool = False,
    show_box: bool = True,
    show_mean: bool = True,
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a violin plot.

    Parameters
    ----------
    data : array-like or list of arrays
    show_box : bool
        Show inner box plot.
    show_mean : bool
        Show mean marker.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    if not isinstance(data[0], (list, tuple, np.ndarray)):
        data = [data]
    n_series = len(data)
    colors = auto_colors(n_series, palette)

    parts = ax.violinplot(
        data,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )

    for i, body in enumerate(parts["bodies"]):
        body.set_facecolor(colors[i % len(colors)])
        body.set_edgecolor("white")
        body.set_linewidth(0.5)
        body.set_alpha(0.7)

    # Add box plots inside violins
    if show_box:
        bp_data = [d for d in data]
        bp = ax.boxplot(
            bp_data,
            patch_artist=False,
            showfliers=False,
            widths=0.1,
            whis=1.5,
            medianprops=dict(color="#333333", linewidth=1.5),
        )

    # Add mean markers
    if show_mean:
        means = [np.mean(d) for d in data]
        positions = np.arange(1, n_series + 1)
        ax.scatter(
            positions if not horizontal else means,
            means if not horizontal else positions,
            marker="D", color="#333333", s=50,
            zorder=5, edgecolors="white", linewidth=0.5,
        )

    if labels:
        if horizontal:
            ax.set_yticks(np.arange(1, n_series + 1))
            ax.set_yticklabels(labels, fontsize=9)
        else:
            ax.set_xticks(np.arange(1, n_series + 1))
            ax.set_xticklabels(labels, fontsize=9)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  STEP  CHART
# ──────────────────────────────────────────────

def step_chart(
    x: Sequence[float],
    y: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    palette: str = "nature_qual",
    figsize: tuple = (10, 5),
    line_width: float = 2.0,
    fill_alpha: float = 0.3,
    fill_color: str | None = None,
    grid: str = "both",
    legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a step chart (good for discrete events).

    Parameters
    ----------
    fill_alpha : float
        Fill transparency under the step line.
    fill_color : str, optional
        Override fill color. Defaults to line color with alpha.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    if isinstance(y, list) and len(y) > 1 and isinstance(y[0], list):
        series = y
        series_labels = labels or [f"Series {i+1}" for i in range(len(series))]
    else:
        series = [y]
        series_labels = [labels[0] if labels else "Series 1"]

    colors = auto_colors(len(series), palette)
    x_arr = np.array(x, dtype=float)

    for i, (y_data, lbl) in enumerate(zip(series, series_labels)):
        y = np.array(y_data, dtype=float)
        ax.step(
            x_arr, y, where="post",
            color=colors[i], linewidth=line_width,
            label=lbl,
        )
        if fill_alpha > 0:
            fc = fill_color or colors[i]
            ax.fill_between(x_arr, y, alpha=fill_alpha, color=fc, step="post")

    if legend:
        ax.legend(frameon=False, fontsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "bar_chart", "grouped_bar", "stacked_bar",
    "line_chart", "area_chart", "scatter_plot",
    "pie_chart", "donut_chart",
    "histogram", "box_plot", "violin_plot",
    "step_chart",
]