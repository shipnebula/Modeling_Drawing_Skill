"""
sciences.py — Scientific-computing charts for mathematical modeling.

Charts aimed at the model-building / model-solving sections of
CUMCM / MCM-ICM papers: optimization objectives, differential
equations, fitted dynamics, and matrix data.

Charts:
    surface3d           — 3D surface plot (objective functions)
    contour_plot        — filled contour with inline labels
    vector_field        — quiver / streamlines (ODEs, flows)
    phase_portrait      — 2D phase trajectories with direction
    twin_axis           — dual y-axis line chart
    errorband           — line with shaded confidence band
    heatmap             — annotated matrix heatmap
    optimization_trace  — optimizer path over the objective contour
    polar_chart         — polar line/area chart
    loglog_plot         — log-scale multi-series line chart

All functions return a matplotlib Figure ready for publication.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .palette import auto_colors, get_palette
from .utils import setup_figure, save_figure, axis_config, format_numbers


def _as_2d_xyz(X, Y, Z) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Normalize mesh inputs: accept 1D axes + 2D Z, or three 2D arrays."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Z = np.asarray(Z, dtype=float)
    if X.ndim == 1 and Y.ndim == 1:
        X, Y = np.meshgrid(X, Y)
    if Z.ndim != 2:
        raise ValueError(
            f"Z must be 2-D after broadcasting, got shape {Z.shape}. "
            "Pass x (1-D), y (1-D), Z (2-D) or X, Y, Z all 2-D."
        )
    return X, Y, Z


# ──────────────────────────────────────────────
#  3D  SURFACE
# ──────────────────────────────────────────────

def surface3d(
    X,
    Y=None,
    Z=None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    zlabel: str = "z",
    cmap: str = "viridis",
    figsize: tuple = (9, 6.5),
    elevation: float = 28,
    azimuth: float = -58,
    alpha: float = 0.95,
    rstride: int = 1,
    cstride: int = 1,
    contour_project: bool = False,
    show_colorbar: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Plot a 3-D surface — the objective landscape of an optimization model.

    Parameters
    ----------
    X, Y, Z : array-like
        Either three 2-D arrays (from meshgrid), or x/y as 1-D axes
        with Z a 2-D matrix.
    elevation, azimuth : float
        Camera angles in degrees.
    contour_project : bool
        Project filled contours onto the bottom pane.
    show_colorbar : bool

    Returns
    -------
    Figure
    """
    if Z is None:  # called as surface3d(Z)
        Z, X, Y = X, None, None
    if X is None:
        X, Y = np.meshgrid(np.arange(Z.shape[1]), np.arange(Z.shape[0]))
    X, Y, Z = _as_2d_xyz(X, Y, Z)

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize, **kwargs)
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(
        X, Y, Z, cmap=cmap, alpha=alpha,
        rstride=rstride, cstride=cstride,
        linewidth=0, antialiased=True,
    )
    if contour_project:
        z_min = float(np.nanmin(Z))
        ax.contourf(
            X, Y, Z, levels=18, cmap=cmap,
            offset=z_min - (np.nanmax(Z) - z_min) * 0.06, alpha=0.6,
        )
        ax.set_zlim(z_min - (np.nanmax(Z) - z_min) * 0.08, np.nanmax(Z))

    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_xlabel(xlabel, labelpad=8)
    ax.set_ylabel(ylabel, labelpad=8)
    ax.set_zlabel(zlabel, labelpad=8)
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=14)
    if show_colorbar:
        fig.colorbar(surf, ax=ax, shrink=0.62, aspect=22, pad=0.09)

    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CONTOUR
# ──────────────────────────────────────────────

def contour_plot(
    X,
    Y=None,
    Z=None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    cmap: str = "viridis",
    figsize: tuple = (8, 5.5),
    levels: int = 14,
    filled: bool = True,
    show_labels: bool = True,
    show_colorbar: bool = True,
    label_fmt: str = "%.2f",
    mark_min: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Filled contour map with labeled iso-lines.

    Parameters
    ----------
    X, Y, Z : array-like
        meshgrid-style inputs (2-D each, or 1-D x/y with 2-D Z).
    levels : int or sequence
        Number of contour levels (or explicit levels).
    mark_min : bool
        Mark the global minimum with a star (optimization optimum).

    Returns
    -------
    Figure
    """
    if Z is None:
        Z, X, Y = X, None, None
    if X is None:
        X, Y = np.meshgrid(np.arange(Z.shape[1]), np.arange(Z.shape[0]))
    X, Y, Z = _as_2d_xyz(X, Y, Z)

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if filled:
        cf = ax.contourf(X, Y, Z, levels=levels, cmap=cmap, alpha=0.92)
    cs = ax.contour(
        X, Y, Z, levels=levels, colors="white" if filled else None,
        linewidths=0.7,
    )
    if show_labels:
        ax.clabel(cs, inline=True, fontsize=7.5, fmt=label_fmt)
    if show_colorbar and filled:
        fig.colorbar(cf, ax=ax, shrink=0.9, pad=0.02)
    if mark_min:
        idx = np.unravel_index(np.nanargmin(Z), Z.shape)
        ax.plot(X[idx], Y[idx], marker="*", ms=14, mfc="#E63946",
                mec="white", mew=0.8, ls="none", zorder=6,
                label=f"min = {Z[idx]:.3g}")
        ax.legend(loc="upper right", frameon=False)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  VECTOR  FIELD
# ──────────────────────────────────────────────

def vector_field(
    x,
    y,
    u=None,
    v=None,
    mode: str = "both",
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 5.5),
    color: str = "#2E86AB",
    density: float = 1.2,
    scale: float | None = None,
    cmap: str | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Vector field as arrows, streamlines, or both.

    Parameters
    ----------
    x, y : 1-D or 2-D arrays
        Grid points (1-D axes are broadcast with meshgrid).
    u, v : arrays matching the grid
        Velocity components.
    mode : str
        'quiver' (arrows), 'stream' (streamlines) or 'both'.
    density : float
        Streamline density (higher = more lines).

    Returns
    -------
    Figure
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim == 1 and y.ndim == 1:
        X, Y = np.meshgrid(x, y)
    else:
        X, Y = x, y
    U, V = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
    if U.shape != X.shape or V.shape != X.shape:
        raise ValueError(
            f"u/v shape {U.shape} does not match grid shape {X.shape}."
        )

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    mode = mode.lower()
    kw_color = {"color": color} if cmap is None else {"cmap": cmap}

    if mode in ("quiver", "both"):
        ax.quiver(X, Y, U, V, scale=scale, width=0.0035,
                  alpha=0.85, **kw_color)
    if mode in ("stream", "both"):
        speed = np.hypot(U, V)
        lw = 0.6 + 1.6 * (speed / (speed.max() + 1e-12))
        ax.streamplot(
            X, Y, U, V, density=density, linewidth=lw,
            color=speed if cmap else color,
            cmap=cmap, arrowsize=1.1,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect("equal", adjustable="box")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PHASE  PORTRAIT
# ──────────────────────────────────────────────

def phase_portrait(
    x,
    y=None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (7, 6),
    colors: Sequence[str] | None = None,
    palette: str = "nature_qual",
    linewidth: float = 1.8,
    n_arrows: int = 5,
    show_start_end: bool = True,
    show_grid: bool = True,
    legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    2-D phase portrait with direction arrows and start/end markers.

    Parameters
    ----------
    x, y : array-like or list of array-like
        Trajectory coordinates. Pass a list of (x, y) pairs to draw
        several trajectories (e.g. different initial conditions).
        A dict ``{name: (x, y)}`` also works and names each orbit.

    Returns
    -------
    Figure
    """
    if y is not None:
        trajectories = [(None, np.asarray(x, float), np.asarray(y, float))]
    elif isinstance(x, dict):
        trajectories = [
            (name, np.asarray(v[0], float), np.asarray(v[1], float))
            for name, v in x.items()
        ]
    else:
        trajectories = [
            (None, np.asarray(t[0], float), np.asarray(t[1], float))
            for t in x
        ]

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = colors or auto_colors(len(trajectories), palette)

    for i, (name, tx, ty) in enumerate(trajectories):
        c = colors[i % len(colors)]
        ax.plot(tx, ty, color=c, lw=linewidth,
                label=name, solid_capstyle="round", zorder=3)

        if n_arrows > 0 and len(tx) > 4:
            idx = np.linspace(1, len(tx) - 2, min(n_arrows, len(tx) - 2),
                              dtype=int)
            for k in idx:
                ax.annotate(
                    "", xy=(tx[k + 1], ty[k + 1]), xytext=(tx[k], ty[k]),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.1),
                    zorder=4,
                )
        if show_start_end:
            ax.plot(tx[0], ty[0], "o", ms=6, mfc="white", mec=c,
                    mew=1.4, zorder=5)
            ax.plot(tx[-1], ty[-1], "s", ms=6, mfc=c, mec="white",
                    mew=0.8, zorder=5)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if show_grid:
        axis_config(ax, grid="both")
    if legend and any(name for name, _, _ in trajectories):
        ax.legend(frameon=False, loc="best")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  TWIN  AXIS
# ──────────────────────────────────────────────

def twin_axis(
    x,
    y1,
    y2=None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel1: str = "y1",
    ylabel2: str = "y2",
    label1: str = "Series 1",
    label2: str = "Series 2",
    color1: str = "#2E86AB",
    color2: str = "#E63946",
    figsize: tuple = (8.5, 5),
    kind1: str = "line",
    kind2: str = "line",
    grid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Two related quantities with different scales on one figure.

    Parameters
    ----------
    x : array-like
        Shared x values.
    y1, y2 : array-like
        Left- and right-axis series.
    kind1, kind2 : str
        'line' or 'bar' for each axis.

    Returns
    -------
    Figure
    """
    fig, ax1 = setup_figure(figsize, style="nature", **kwargs)
    y1, y2 = np.asarray(y1, float), np.asarray(y2, float)

    # Numeric x positions; categorical x becomes 0..n-1 with labels
    x_cat: list | None = None
    try:
        x_num = np.asarray(x, dtype=float)
        if x_num.ndim == 0:
            x_num = np.arange(len(y1), dtype=float)
    except (TypeError, ValueError):
        x_cat = [str(v) for v in x]
        x_num = np.arange(len(y1), dtype=float)

    if kind1 == "bar":
        ax1.bar(x_num, y1, color=color1, alpha=0.85, width=0.55, label=label1)
    else:
        ax1.plot(x_num, y1, color=color1, lw=2, marker="o", ms=3.5, label=label1)

    ax2 = ax1.twinx()
    offset = 0.28 if (kind1 == "bar" or kind2 == "bar") else 0.0
    if kind2 == "bar":
        ax2.bar(x_num + offset, y2, color=color2, alpha=0.85, width=0.55,
                label=label2)
    else:
        ax2.plot(x_num + offset, y2, color=color2, lw=2, marker="s", ms=3.5,
                 label=label2, ls="--")

    if x_cat is not None:
        ax1.set_xticks(x_num)
        ax1.set_xticklabels(x_cat, fontsize=9)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel1, color=color1)
    ax2.set_ylabel(ylabel2, color=color2)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax2.tick_params(axis="y", labelcolor=color2)
    if grid:
        ax1.grid(axis="y", alpha=0.12, lw=0.5)
        ax1.set_axisbelow(True)

    lines = [ax1.get_legend_handles_labels(), ax2.get_legend_handles_labels()]
    handles = [h for hl in lines for h in hl[0]]
    labels_ = [l for ll in lines for l in ll[1]]
    ax1.legend(handles, labels_, loc="upper left", frameon=False)
    if title:
        ax1.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ERROR  BAND
# ──────────────────────────────────────────────

def errorband(
    x,
    y,
    lower=None,
    upper=None,
    yerr=None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 5),
    color: str = "#2E86AB",
    band_alpha: float = 0.18,
    band_label: str | None = "±1σ",
    line_label: str | None = "mean",
    show_mean_line: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Line chart with a shaded uncertainty band — experiment repetition,
    Monte-Carlo envelopes, or confidence intervals.

    Parameters
    ----------
    x, y : array-like
        Central estimate. ``y`` may be 2-D (runs × time) — the mean and
        band are computed automatically.
    lower, upper : array-like, optional
        Band bounds. If omitted, ``yerr`` (scalar/array) is used.
    y : 2-D case
        Band = mean ± std across runs.

    Returns
    -------
    Figure
    """
    x = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    if y_arr.ndim == 2 and lower is None and yerr is None:
        mean, std = y_arr.mean(axis=0), y_arr.std(axis=0)
        lower, upper = mean - std, mean + std
        y_arr = mean
        band_label = band_label or "±1σ"
    elif yerr is not None:
        yerr = np.broadcast_to(np.asarray(yerr, float), y_arr.shape)
        lower, upper = y_arr - yerr, y_arr + yerr
    elif lower is None or upper is None:
        raise ValueError(
            "Provide lower/upper, yerr, or pass y as a 2-D (runs × time) array."
        )

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.fill_between(x, lower, upper, color=color, alpha=band_alpha,
                    lw=0, label=band_label)
    if show_mean_line:
        ax.plot(x, y_arr, color=color, lw=2, label=line_label, zorder=4)
    if band_label or line_label:
        ax.legend(frameon=False, loc="best")
    axis_config(ax, grid="y")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  HEATMAP  (generic annotated matrix)
# ──────────────────────────────────────────────

def heatmap(
    data,
    row_labels: Sequence[str] | None = None,
    col_labels: Sequence[str] | None = None,
    title: str | None = None,
    xlabel: str = "",
    ylabel: str = "",
    cmap: str | None = None,
    palette: str | None = None,
    figsize: tuple | None = None,
    annot: bool = True,
    annot_fmt: str = ".2f",
    annot_size: float = 8,
    show_colorbar: bool = True,
    center: float | None = None,
    linewidths: float = 0.5,
    grid_color: str = "white",
    cbar_label: str = "",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Annotated matrix heatmap for any 2-D data (not just confusion).

    Parameters
    ----------
    data : 2-D array-like
    row_labels, col_labels : lists of str
    cmap : str
        Matplotlib colormap; defaults to a diverging map when ``center``
        is given, else 'viridis' (or the sequential palette name).
    center : float, optional
        Value at the colormap midpoint (e.g. 0 for signed data).

    Returns
    -------
    Figure
    """
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"heatmap expects a 2-D matrix, got ndim={arr.ndim}.")
    n_rows, n_cols = arr.shape

    if row_labels is None:
        row_labels = [str(i) for i in range(n_rows)]
    if col_labels is None:
        col_labels = [str(j) for j in range(n_cols)]

    if figsize is None:
        cell = 0.55
        figsize = (
            max(6, min(14, n_cols * cell + 2.2)),
            max(4, min(12, n_rows * cell + 1.6)),
        )

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)

    if cmap is None and palette is not None:
        cmap = palette
    if cmap is None:
        cmap = "coolwarm" if center is not None else "viridis"

    if center is not None:
        vmax = np.nanmax(np.abs(arr - center)) or 1.0
        vmin, vmax = center - vmax, center + vmax
    else:
        vmin, vmax = np.nanmin(arr), np.nanmax(arr)

    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")

    if annot and n_rows * n_cols > 2500:
        import warnings
        warnings.warn(
            f"heatmap: {n_rows}x{n_cols} cells — annotations disabled "
            f"for performance (pass annot=True to force)."
        )
        annot = False
    if annot:
        thresh = vmin + (vmax - vmin) * 0.55
        for i in range(n_rows):
            for j in range(n_cols):
                val = arr[i, j]
                if np.isnan(val):
                    continue
                color = "white" if val > thresh else "#1A1A1A"
                if center is not None:
                    color = "white" if abs(val - center) > (vmax - center) * 0.55 else "#1A1A1A"
                ax.text(j, i, format(val, annot_fmt), ha="center",
                        va="center", fontsize=annot_size, color=color)

    if linewidths > 0:
        ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
        ax.grid(which="minor", color=grid_color, linewidth=linewidths)
        ax.tick_params(which="minor", length=0)

    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ax.set_xticklabels(col_labels, fontsize=8.5)
    ax.set_yticklabels(row_labels, fontsize=8.5)
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if show_colorbar:
        cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
        if cbar_label:
            cbar.set_label(cbar_label, fontsize=9)

    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  OPTIMIZATION  TRACE
# ──────────────────────────────────────────────

def optimization_trace(
    func: Callable,
    path,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 5.5),
    x_range: tuple | None = None,
    y_range: tuple | None = None,
    resolution: int = 220,
    cmap: str = "viridis",
    path_color: str = "#E63946",
    show_numbers: bool = True,
    number_every: int = 1,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Optimizer iterates over the objective's contour map.

    Parameters
    ----------
    func : callable
        Objective ``f(x, y) -> float`` (vectorized with numpy).
    path : array-like, shape (n_iter, 2)
        Sequence of visited points, first = start.

    Returns
    -------
    Figure
    """
    path = np.asarray(path, dtype=float)
    if path.ndim != 2 or path.shape[1] != 2:
        raise ValueError(
            f"path must have shape (n_iter, 2), got {path.shape}."
        )

    if x_range is None:
        pad = 0.15 * (np.ptp(path[:, 0]) or 1.0)
        x_range = (path[:, 0].min() - pad, path[:, 0].max() + pad)
    if y_range is None:
        pad = 0.15 * (np.ptp(path[:, 1]) or 1.0)
        y_range = (path[:, 1].min() - pad, path[:, 1].max() + pad)

    xs = np.linspace(*x_range, resolution)
    ys = np.linspace(*y_range, resolution)
    X, Y = np.meshgrid(xs, ys)
    Z = func(X, Y)

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    cf = ax.contourf(X, Y, Z, levels=18, cmap=cmap, alpha=0.9)
    ax.contour(X, Y, Z, levels=18, colors="white", linewidths=0.4)
    fig.colorbar(cf, ax=ax, shrink=0.9, pad=0.02, label="f(x, y)")

    ax.plot(path[:, 0], path[:, 1], "-o", color=path_color, lw=1.8,
            ms=4, mfc="white", mec=path_color, mew=1.1, zorder=5,
            label="optimizer path")
    ax.plot(path[0, 0], path[0, 1], marker="^", ms=10, mfc="#2A9D8F",
            mec="white", ls="none", zorder=6, label="start")
    ax.plot(path[-1, 0], path[-1, 1], marker="*", ms=15, mfc="#F4A261",
            mec="white", ls="none", zorder=6,
            label=f"best = {func(path[-1, 0], path[-1, 1]):.4g}")

    if show_numbers:
        for i in range(0, len(path), number_every):
            ax.annotate(str(i), (path[i, 0], path[i, 1]),
                        textcoords="offset points", xytext=(4, 4),
                        fontsize=6.5, color="#555555")

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="upper right")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  POLAR  CHART
# ──────────────────────────────────────────────

def polar_chart(
    theta,
    r,
    title: str | None = None,
    labels: Sequence[str] | None = None,
    names: Sequence[str] | None = None,
    figsize: tuple = (6.5, 6.5),
    palette: str = "nature_qual",
    fill: bool = True,
    fill_alpha: float = 0.18,
    linewidth: float = 1.9,
    grid_color: str = "#CCCCCC",
    r_label: str | None = None,
    zero_location: str | None = None,
    clockwise: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Polar line/area chart (directional data, wind rose, periodic signal).

    Parameters
    ----------
    theta : array-like
        Angles (degrees by default).
    r : array-like or dict of series
        Radii — a single series or ``{name: radii}`` for several.
    labels : list of str
        Tick labels around the circle (categories/directions).
    zero_location : str, optional
        Compass point at theta=0: 'N', 'E', 'S' or 'W'
        (e.g. 'N' puts north at the top for wind roses).
    clockwise : bool
        Increase theta clockwise (combine with zero_location='N').

    Returns
    -------
    Figure
    """
    theta = np.asarray(theta, dtype=float)
    series = r if isinstance(r, dict) else {"Series 1": r}
    if names:
        series = dict(zip(names, r.values() if isinstance(r, dict) else r))

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize, **kwargs)
    ax = fig.add_subplot(111, projection="polar")
    if zero_location:
        ax.set_theta_zero_location(zero_location.upper())
    if clockwise:
        ax.set_theta_direction(-1)
    theta_rad = np.deg2rad(theta) if np.nanmax(np.abs(theta)) > 2 * np.pi + 0.1 else theta

    colors = auto_colors(len(series), palette)
    for (name, radii), c in zip(series.items(), colors):
        radii = np.asarray(radii, dtype=float)
        ax.plot(theta_rad, radii, color=c, lw=linewidth, label=name,
                marker="o", ms=3.5)
        if fill:
            ax.fill(theta_rad, radii, color=c, alpha=fill_alpha, lw=0)

    if labels is not None:
        ax.set_xticks(theta_rad)
        ax.set_xticklabels(labels, fontsize=9)
    ax.grid(color=grid_color, alpha=0.6, lw=0.5)
    ax.spines["polar"].set_color("#999999")
    if r_label:
        ax.set_rlabel_position(90 / len(series) + 12)
        ax.set_ylabel(r_label, fontsize=9, labelpad=-38)
    if len(series) > 1:
        ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.08),
                  frameon=False, fontsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=18)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  LOG-SCALE  LINE  CHART
# ──────────────────────────────────────────────

def loglog_plot(
    data,
    x=None,
    title: str | None = None,
    xlabel: str = "x (log)",
    ylabel: str = "y (log)",
    logx: bool = True,
    logy: bool = True,
    figsize: tuple = (8, 5),
    palette: str = "nature_qual",
    markers: bool = True,
    show_fit_slope: bool = False,
    grid: str = "both",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Multi-series line chart on log axes — convergence rates,
    error decay, power laws, and complexity curves.

    Parameters
    ----------
    data : dict of series or list
        ``{name: y_values}`` (x shared) or a single y list.
    x : array-like, optional
        Shared x values.
    show_fit_slope : bool
        Fit a straight line in log-log space and annotate its slope
        (the power-law exponent).

    Returns
    -------
    Figure
    """
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(8, palette)
    series = data if isinstance(data, dict) else {"Series 1": data}

    for i, (name, yv) in enumerate(series.items()):
        yv = np.asarray(yv, dtype=float)
        xv = np.asarray(x, dtype=float) if x is not None else np.arange(1, len(yv) + 1)
        mask = yv > 0
        ax.plot(xv[mask] if logx else xv, yv[mask] if logy else yv,
                color=colors[i % len(colors)], lw=1.9,
                marker="o" if markers else None, ms=3.2, label=name)

        if show_fit_slope and len(yv) >= 3:
            slope, intercept = np.polyfit(
                np.log(xv[mask]), np.log(yv[mask]), 1
            )
            x_line = np.linspace(xv[mask].min(), xv[mask].max(), 50)
            ax.plot(x_line if not logx else x_line,
                    np.exp(intercept) * x_line ** slope,
                    color=colors[i % len(colors)], lw=1, ls=":", alpha=0.8)
            ax.annotate(
                f"slope = {slope:.2f}",
                xy=(0.97, 0.05 - 0.07 * i), xycoords="axes fraction",
                ha="right", fontsize=8.5,
                color=colors[i % len(colors)],
            )

    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    axis_config(ax, grid=grid)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if len(series) > 1:
        ax.legend(frameon=False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


def polar_bar(
    theta,
    r,
    title: str | None = None,
    labels: Sequence[str] | None = None,
    names: Sequence[str] | None = None,
    figsize: tuple = (6.8, 6.8),
    palette: str = "nature_qual",
    width: float | None = None,
    alpha: float = 0.88,
    edge_color: str = "white",
    zero_location: str | None = None,
    clockwise: bool = False,
    show_values: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Polar bar chart — wind-rose style bars, radial rankings, hourly /
    directional histograms.

    Parameters
    ----------
    theta : array-like
        Bar angles (degrees by default).
    r : array-like or dict of series
        Bar lengths; a dict draws grouped sectors.

    Returns
    -------
    Figure
    """
    theta = np.asarray(theta, dtype=float)
    series = r if isinstance(r, dict) else {"Series 1": r}
    if names and isinstance(r, (list, tuple)):
        series = dict(zip(names, r))

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize, **kwargs)
    ax = fig.add_subplot(111, projection="polar")
    if zero_location:
        ax.set_theta_zero_location(zero_location.upper())
    if clockwise:
        ax.set_theta_direction(-1)
    theta_rad = np.deg2rad(theta) if np.nanmax(np.abs(theta)) > 2 * np.pi + 0.1 else theta

    colors = auto_colors(len(series), palette)
    n_series = len(series)
    if width is None:
        width = 0.8 * (theta_rad[1] - theta_rad[0]) / n_series if len(theta_rad) > 1 else 0.8 / n_series

    for k, ((name, radii), c) in enumerate(zip(series.items(), colors)):
        radii = np.asarray(radii, dtype=float)
        offset = (k - (n_series - 1) / 2) * width
        bars = ax.bar(theta_rad + offset, radii, width=width * 0.94,
                      color=c, alpha=alpha, edgecolor=edge_color, lw=0.8,
                      label=str(name))
        if show_values and n_series == 1:
            for bar, val in zip(bars, radii):
                ang = bar.get_x() + bar.get_width() / 2
                ax.text(ang, bar.get_height() + max(radii) * 0.03,
                        f"{val:g}", ha="center", va="bottom", fontsize=7.5,
                        color="#333333")

    if labels is not None:
        ticks = theta_rad if n_series == 1 else theta_rad
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=9)
    ax.grid(color="#CCCCCC", alpha=0.6, lw=0.5)
    ax.spines["polar"].set_color("#999999")
    if len(series) > 1:
        ax.legend(loc="upper right", bbox_to_anchor=(1.26, 1.08),
                  frameon=False, fontsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=18)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig




def ternary_plot(
    a,
    b,
    c,
    labels: Sequence[str] = ("A", "B", "C"),
    groups: Sequence | None = None,
    title: str | None = None,
    figsize: tuple = (7, 6.5),
    palette: str = "nature_qual",
    point_size: float = 30,
    alpha: float = 0.8,
    show_grid: bool = True,
    grid_levels: int = 5,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Ternary diagram — compositions of three components summing to 1
    (mixture design, resource allocation, soil/chemical composition).

    Parameters
    ----------
    a, b, c : array-like
        Component fractions (any scale — normalized internally).

    Returns
    -------
    Figure
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    c = np.asarray(c, float)
    total = a + b + c
    a, b, c = a / total, b / total, c / total

    # corners: A top, B bottom-left, C bottom-right
    A = np.array([0.5, np.sqrt(3) / 2])
    B = np.array([0.0, 0.0])
    C = np.array([1.0, 0.0])

    def to_xy(av, bv, cv):
        return av[:, None] * A + bv[:, None] * B + cv[:, None] * C

    pts = to_xy(a, b, c)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    tri = plt.Polygon([A, B, C], closed=True, facecolor="#FAFAFA",
                      edgecolor="#333333", lw=1.3, zorder=1)
    ax.add_patch(tri)

    if show_grid:
        for k in range(1, grid_levels):
            t = k / grid_levels
            s = 1 - t
            # three families of lines, each parallel to one edge
            for v1, v2, v3 in ((A, B, C), (B, C, A), (C, A, B)):
                p1 = t * v1 + s * v2   # edge near v2
                p2 = t * v1 + s * v3   # edge near v3
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                        color="#CCCCCC", lw=0.5, zorder=1)

    if groups is not None:
        cats = list(dict.fromkeys(groups))
        colors = auto_colors(len(cats), palette)
        for cat, col in zip(cats, colors):
            m = np.asarray([g == cat for g in groups])
            ax.scatter(pts[m, 0], pts[m, 1], s=point_size, color=col,
                       alpha=alpha, edgecolors="white", lw=0.5,
                       label=str(cat), zorder=3)
        ax.legend(frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5))
    else:
        ax.scatter(pts[:, 0], pts[:, 1], s=point_size,
                   color=auto_colors(1, palette)[0], alpha=alpha,
                   edgecolors="white", lw=0.5, zorder=3)

    pad = 0.06
    ax.text(A[0], A[1] + pad, f"{labels[0]} (1−x−y)", ha="center", fontsize=10)
    ax.text(B[0] - pad, B[1] - pad * 0.6, f"{labels[1]} (x)", ha="right", fontsize=10)
    ax.text(C[0] + pad, C[1] - pad * 0.6, f"{labels[2]} (y)", ha="left", fontsize=10)

    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.12, np.sqrt(3) / 2 + 0.12)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig



def scatter3d(
    x,
    y,
    z,
    names: Sequence[str] | None = None,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    zlabel: str = "z",
    figsize: tuple = (9, 6.5),
    palette: str = "nature_qual",
    size: float = 30,
    alpha: float = 0.8,
    elevation: float = 22,
    azimuth: float = -60,
    show_colorbar: bool = False,
    cmap: str | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    3-D scatter — decision variables of an optimization, embeddings,
    or any three-dimensional point cloud.

    Parameters
    ----------
    x, y, z : array-like
        Coordinates. Give ``names`` (one per point) to color by group,
        or leave ``names`` empty to color by z-value.

    Returns
    -------
    Figure
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)
    if not (len(x) == len(y) == len(z)):
        raise ValueError("x, y, z must have the same length.")

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize, **kwargs)
    ax = fig.add_subplot(111, projection="3d")

    if names is not None:
        groups = list(dict.fromkeys(names))
        colors = auto_colors(len(groups), palette)
        for g, c in zip(groups, colors):
            m = np.asarray([n == g for n in names])
            ax.scatter(x[m], y[m], z[m], s=size, c=c, alpha=alpha,
                       edgecolors="white", lw=0.4, label=str(g))
        ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.02, 0.95))
    else:
        sc = ax.scatter(x, y, z, s=size, c=z, cmap=cmap or "viridis",
                        alpha=alpha, edgecolors="white", lw=0.4)
        if show_colorbar or cmap:
            fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1)

    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_xlabel(xlabel, labelpad=6)
    ax.set_ylabel(ylabel, labelpad=6)
    ax.set_zlabel(zlabel, labelpad=6)
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    if labels is not None:
        for xi, yi, zi, lab in zip(x, y, z, labels):
            ax.text(xi, yi, zi, f"  {lab}", fontsize=7, color="#555555")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=14)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "surface3d",
    "contour_plot",
    "vector_field",
    "phase_portrait",
    "twin_axis",
    "errorband",
    "heatmap",
    "optimization_trace",
    "polar_chart",
    "loglog_plot",
    "scatter3d",
    "polar_bar",
    "ternary_plot",
    "curve_sweep",
    "phase_field",
]


# ──────────────────────────────────────────────
#  PARAMETER  SWEEP  CURVE  FAMILY
# ──────────────────────────────────────────────

def curve_sweep(
    f: Callable,
    param_values: Sequence[float],
    x: Sequence | None = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "f(x)",
    figsize: tuple = (9, 5.5),
    cmap: str = "viridis",
    param_name: str = "parameter",
    n_grid: int = 300,
    linewidth: float = 1.6,
    colorbar: bool = True,
    colorbar_label: str | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Curve family across a parameter sweep — every curve colored by its
    parameter value. The elegant way to show how a solution reacts to
    a continuous input ("as the tax rate rises, demand shifts from …").

    Parameters
    ----------
    f : callable ``f(x, param)``
        Family of functions.
    param_values : array-like
        Sweep values; curves are colored by a shared colormap.

    Returns
    -------
    Figure
    """
    params = np.asarray(param_values, dtype=float)
    if x is None:
        x = np.linspace(0, 1, n_grid)
    xg = np.asarray(x, dtype=float)
    if xg.size > n_grid:
        xg = np.linspace(xg.min(), xg.max(), n_grid)

    norm = plt.Normalize(params.min(), params.max())
    cmap_obj = plt.get_cmap(cmap)

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    for pv in params:
        ax.plot(xg, f(xg, pv), color=cmap_obj(norm(pv)), lw=linewidth,
                solid_capstyle="round")

    if colorbar:
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap_obj)
        cb = fig.colorbar(sm, ax=ax, shrink=0.92, pad=0.02)
        cb.set_label(colorbar_label or param_name, fontsize=9.5)
        cb.outline.set_visible(False)

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
#  PHASE  FIELD  (portrait + vector field)
# ──────────────────────────────────────────────

def phase_field(
    fx: Callable,
    fy: Callable,
    trajectories: Optional[Sequence] = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 6.5),
    grid_n: int = 18,
    palette: str = "nature_qual",
    stream_color: str = "#B8C4CE",
    traj_color: str | None = None,
    n_time: int = 200,
    t_max: float = 10.0,
    x_range: tuple | None = None,
    y_range: tuple | None = None,
    show_fixed_points: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Phase portrait over its vector field — streamlines show the flow
    field, colored trajectories show integrated solutions from given
    initial conditions, fixed points are marked. The definitive ODE
    analysis figure.

    Parameters
    ----------
    fx, fy : callables ``f(x, y) -> dx/dt, dy/dt``
        The right-hand side of the ODE system.
    trajectories : list of (x0, y0) initial conditions, optional
    x_range, y_range : tuple, optional
        Plot window (required when no trajectories are given).

    Returns
    -------
    Figure
    """
    from scipy.integrate import solve_ivp

    if trajectories:
        x0 = np.asarray([t[0] for t in trajectories], dtype=float)
        y0 = np.asarray([t[1] for t in trajectories], dtype=float)
        if x_range is None:
            x_range = (float(x0.min()) - 1, float(x0.max()) + 1)
        if y_range is None:
            y_range = (float(y0.min()) - 1, float(y0.max()) + 1)
    else:
        if x_range is None or y_range is None:
            raise ValueError("phase_field needs trajectories or x/y ranges.")

    kwargs.pop("style", None)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    xs = np.linspace(*x_range, grid_n)
    ys = np.linspace(*y_range, grid_n)
    Xg, Yg = np.meshgrid(xs, ys)
    U, V = fx(Xg, Yg), fy(Xg, Yg)
    speed = np.hypot(U, V) + 1e-12
    lw = 0.5 + 1.4 * (speed / speed.max())
    ax.streamplot(Xg, Yg, U, V, density=0.9, color=stream_color,
                  linewidth=lw, arrowsize=0.9, zorder=1)

    if show_fixed_points:
        # near-zero speed local minima as fixed-point candidates
        from scipy.ndimage import minimum_filter
        mask = (speed == minimum_filter(speed, size=5)) & (speed < speed.mean() * 0.08)
        for i, j in zip(*np.where(mask)):
            ax.plot(Xg[i, j], Yg[i, j], "o", ms=9, mfc="#F4A261",
                    mec="white", mew=1.2, zorder=5)

    if trajectories:
        colors = auto_colors(len(trajectories), traj_color or palette)
        t_eval = np.linspace(0, t_max, n_time)
        for (sx, sy), c in zip(trajectories, colors):
            sol = solve_ivp(
                lambda t, z: [float(fx(z[0], z[1])), float(fy(z[0], z[1]))],
                (0, t_max), [sx, sy], t_eval=t_eval,
                rtol=1e-7, atol=1e-9,
            )
            if sol.success:
                ax.plot(sol.y[0], sol.y[1], color=c, lw=2, zorder=4)
                ax.plot(sx, sy, "o", ms=6, mfc="white", mec=c, mew=1.4,
                        zorder=5)

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig
