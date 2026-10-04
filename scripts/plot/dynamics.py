"""
dynamics.py — Iterative-map and simulation charts.

Charts for the simulation / chaos / stability chapters of modeling
papers: bifurcation diagrams, cobweb plots, and Monte-Carlo
convergence diagnostics.

Charts:
    bifurcation             — logistic-map style period doubling
    cobweb                  — orbit of an iterative map x_{n+1} = f(x_n)
    monte_carlo_convergence — running estimate with confidence band

All functions return a matplotlib Figure ready for publication.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .utils import setup_figure, save_figure, axis_config, figsubplots


# ──────────────────────────────────────────────
#  BIFURCATION  DIAGRAM
# ──────────────────────────────────────────────

def bifurcation(
    f: Optional[Callable] = None,
    a_range: tuple = (2.5, 4.0),
    n_transient: int = 200,
    n_plot: int = 120,
    n_a: int = 800,
    title: str | None = None,
    xlabel: str = "parameter a",
    ylabel: str = "x*",
    figsize: tuple = (10, 5.5),
    color: str = "#1D3557",
    point_size: float = 0.15,
    alpha: float = 0.45,
    mark_a: tuple | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Bifurcation diagram of an iterative map — period doubling into
    chaos. Defaults to the logistic map ``f(x, a) = a·x·(1 − x)``.

    Parameters
    ----------
    f : callable ``(x, a) -> x_next``, optional
        Iterated map. Defaults to the logistic map.
    a_range : (low, high)
        Parameter sweep.
    n_transient : int
        Iterations discarded before sampling (removes transients).
    n_plot : int
        Attractor points sampled per parameter value.
    n_a : int
        Parameter grid resolution.
    mark_a : float or tuple, optional
        Vertical guide lines at specific parameter values.

    Returns
    -------
    Figure
    """
    if f is None:
        def f(x, a):
            return a * x * (1.0 - x)

    a_values = np.linspace(*a_range, n_a)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    for a in a_values:
        x = 0.5
        for _ in range(n_transient):
            x = f(x, a)
        xs = np.empty(n_plot)
        for i in range(n_plot):
            x = f(x, a)
            xs[i] = x
        ax.plot(np.full(n_plot, a), xs, ".", ms=point_size, color=color,
                alpha=alpha, rasterized=True)

    if mark_a is not None:
        for av in np.atleast_1d(mark_a):
            ax.axvline(av, color="#C73E1D", lw=1, ls="--", alpha=0.8)

    ax.set_xlim(a_range)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  COBWEB  PLOT
# ──────────────────────────────────────────────

def cobweb(
    f: Callable,
    x0: float,
    n: int = 40,
    a: float | None = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "f(x)",
    figsize: tuple = (6.5, 6),
    curve_color: str = "#2E86AB",
    web_color: str = "#C73E1D",
    web_alpha: float = 0.8,
    show_diagonal: bool = True,
    show_fixed_point: bool = True,
    axis_range: tuple | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Cobweb plot of the orbit ``x_{n+1} = f(x_n)`` — convergence,
    oscillation, or chaos of an iterative process at a glance.

    Parameters
    ----------
    f : callable
        Single-argument map.
    x0 : float
        Starting point.
    n : int
        Number of iterations drawn.

    Returns
    -------
    Figure
    """
    xs = [x0]
    x = x0
    for _ in range(n):
        x = float(f(x))
        xs.append(x)
    xs = np.asarray(xs, dtype=float)

    if axis_range is None:
        probe = np.linspace(xs.min() - 0.2, xs.max() + 0.2, 200) if len(xs) > 1 \
            else np.linspace(-0.1, 1.1, 200)
        fx = f(probe)
        lo = float(min(probe.min(), np.nanmin(fx))) - 0.05
        hi = float(max(probe.max(), np.nanmax(fx))) + 0.05
        axis_range = (lo, hi)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    grid = np.linspace(axis_range[0], axis_range[1], 300)
    ax.plot(grid, f(grid), color=curve_color, lw=2, label="f(x)")
    if show_diagonal:
        ax.plot(grid, grid, color="#999999", lw=1, ls="--", label="y = x")

    # cobweb segments: vertical then horizontal, alternating
    seg_x, seg_y = [xs[0]], [0.0]
    for i in range(len(xs) - 1):
        seg_x += [xs[i], xs[i + 1]]
        seg_y += [xs[i + 1], xs[i + 1]]
    ax.plot(seg_x, seg_y, color=web_color, lw=1.1, alpha=web_alpha,
            label=f"orbit x0={x0:g}, n={n}")

    if show_fixed_point:
        fp_grid = np.linspace(axis_range[0], axis_range[1], 2000)
        g = fp_grid - f(fp_grid)
        sign_change = np.where(np.diff(np.signbit(g)))[0]
        for k in sign_change[:4]:
            root = fp_grid[k]
            ax.plot([root], [root], "o", ms=6, mfc="#F4A261", mec="white",
                    mew=1, zorder=5)

    ax.set_xlim(axis_range)
    ax.set_ylim(axis_range)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  MONTE-CARLO  CONVERGENCE
# ──────────────────────────────────────────────

def monte_carlo_convergence(
    samples: Sequence[float],
    title: str | None = None,
    xlabel: str = "iterations",
    ylabel: str = "running mean",
    figsize: tuple = (9, 5),
    color: str = "#2E86AB",
    band_color: str = "#2E86AB",
    band_alpha: float = 0.18,
    conf: float = 1.96,
    show_true_value: bool = True,
    true_value: float | None = None,
    logx: bool = False,
    n_grid: int = 300,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Running mean of a simulation with a shrinking confidence band —
    the standard "your Monte-Carlo actually converged" figure.

    Parameters
    ----------
    samples : 1-D array-like
        Raw simulation draws (one per iteration).
    conf : float
        z multiplier for the band (1.96 = 95%).
    true_value : float, optional
        Reference line (analytic value); drawn as a dashed line.
    logx : bool
        Log-scale the iteration axis (convergence looks linear there).

    Returns
    -------
    Figure
    """
    v = np.asarray(samples, dtype=float).ravel()
    n = len(v)
    if n < 10:
        raise ValueError("monte_carlo_convergence needs >= 10 samples.")

    iters = np.arange(1, n + 1)
    running_mean = np.cumsum(v) / iters
    running_std = np.sqrt(np.cumsum(v ** 2) / iters - running_mean ** 2)
    half_width = conf * running_std / np.sqrt(iters)

    if n > n_grid:  # thin the band for drawing speed, keep the last point
        idx = np.unique(np.concatenate([
            np.linspace(0, n - 1, n_grid).astype(int), [n - 1]]))
    else:
        idx = np.arange(n)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.fill_between(iters[idx], running_mean[idx] - half_width[idx],
                    running_mean[idx] + half_width[idx],
                    color=band_color, alpha=band_alpha, lw=0,
                    label=f"{int(conf * 100)}% CI")
    ax.plot(iters[idx], running_mean[idx], color=color, lw=1.8,
            label="running mean")
    if true_value is None and show_true_value:
        true_value = float(np.mean(v[-max(n // 10, 10):]))
    if show_true_value and true_value is not None:
        ax.axhline(true_value, color="#C73E1D", lw=1.2, ls="--",
                   label=f"estimate = {true_value:.4g}")
    if logx:
        ax.set_xscale("log")

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


__all__ = [
    "bifurcation",
    "cobweb",
    "monte_carlo_convergence",
]
