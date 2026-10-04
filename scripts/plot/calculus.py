"""
calculus.py — Calculus visualization charts.

Built for the model-formulation sections of math modeling papers:
definite integrals, Riemann sums, tangent lines, and interpolation.

Charts:
    area_under_curve         — shaded definite integral
    riemann_sum              — numerical integration rectangles
    tangent_line             — derivative at a point
    interpolation_comparison — linear vs polynomial vs spline

All functions return a matplotlib Figure ready for publication.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .palette import ACCENT, NEUTRAL
from .utils import setup_figure, save_figure, axis_config


def _prepare(f: Optional[Callable], x, y):
    """Normalize inputs into (f, x_dense, x_samples, y_samples)."""
    if f is not None:
        x_dense = np.linspace(-2, 2, 400) if x is None else np.linspace(
            np.min(x), np.max(x), 400)
        return f, x_dense, None, None
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    order = np.argsort(x_arr)
    x_arr, y_arr = x_arr[order], y_arr[order]

    def f(v):
        return np.interp(v, x_arr, y_arr)

    x_dense = np.linspace(x_arr[0], x_arr[-1], 400)
    return f, x_dense, x_arr, y_arr


# ──────────────────────────────────────────────
#  AREA  UNDER  CURVE  (definite integral)
# ──────────────────────────────────────────────

def area_under_curve(
    f: Optional[Callable] = None,
    x: Optional[Sequence[float]] = None,
    y: Optional[Sequence[float]] = None,
    a: float = 0,
    b: float = 2,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 5),
    color: str = "#2E86AB",
    fill_color: str = "#2E86AB",
    fill_alpha: float = 0.25,
    show_integral: bool = True,
    show_bounds: bool = True,
    n_grid: int = 400,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Shade the definite integral ∫[a,b] f(x) dx and annotate its value.

    Parameters
    ----------
    f : callable, optional
        Function to integrate. If omitted, pass sample data ``x``/``y``
        (integrand is linearly interpolated).
    a, b : float
        Integration bounds (clipped to the data/function range).
    show_integral : bool
        Annotate the shaded area with its numeric value.

    Returns
    -------
    Figure
    """
    f, x_dense, xs, ys = _prepare(f, x, y)
    lo = np.min(x_dense)
    hi = np.max(x_dense)
    a = np.clip(a, lo, hi)
    b = np.clip(b, lo, hi)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    xg = np.linspace(lo, hi, n_grid)
    ax.plot(xg, f(xg), color=color, lw=2.2, label="f(x)", zorder=3)

    xa = np.linspace(a, b, n_grid)
    ya = f(xa)
    ax.fill_between(xa, ya, color=fill_color, alpha=fill_alpha, lw=0,
                    label="∫ f(x) dx", zorder=2)
    integral = float(np.trapezoid(ya, xa)) if hasattr(np, "trapezoid") else float(np.trapz(ya, xa))

    if show_bounds:
        for xb in (a, b):
            ax.axvline(xb, color="#999999", lw=0.9, ls="--", zorder=1)
            ax.text(xb, ax.get_ylim()[1], f"  {xb:g}", fontsize=8.5,
                    color="#666666", va="top")

    if show_integral:
        ax.text(0.5, 0.92, f"∫[{a:g}, {b:g}] f(x) dx = {integral:.4g}",
                transform=ax.transAxes, ha="center", fontsize=10.5,
                color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="y")
    ax.legend(frameon=False, loc="lower right")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  RIEMANN  SUM
# ──────────────────────────────────────────────

def riemann_sum(
    f: Optional[Callable] = None,
    x: Optional[Sequence[float]] = None,
    y: Optional[Sequence[float]] = None,
    a: float = 0,
    b: float = 2,
    n: int = 10,
    method: str = "mid",
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (8, 5),
    color: str = "#2E86AB",
    rect_color: str = "#F18F01",
    rect_alpha: float = 0.4,
    show_error: bool = True,
    n_grid: int = 400,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Riemann-sum rectangles approximating ∫[a,b] f(x) dx.

    Parameters
    ----------
    n : int
        Number of rectangles.
    method : str
        'left', 'right' or 'mid' sample points.
    show_error : bool
        Annotate the sum and its error vs the exact integral.

    Returns
    -------
    Figure
    """
    f, x_dense, xs, ys = _prepare(f, x, y)
    lo, hi = float(np.min(x_dense)), float(np.max(x_dense))
    a, b = np.clip(a, lo, hi), np.clip(b, lo, hi)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    xg = np.linspace(lo, hi, n_grid)
    ax.plot(xg, f(xg), color=color, lw=2.2, zorder=4)

    edges = np.linspace(a, b, n + 1)
    step = (b - a) / n
    if method == "left":
        pts = edges[:-1]
    elif method == "right":
        pts = edges[1:]
    else:
        pts = edges[:-1] + step / 2

    total = 0.0
    for p, e0, e1 in zip(pts, edges[:-1], edges[1:]):
        h = float(f(p))
        total += h * step
        ax.add_patch(plt.Rectangle(
            (e0, 0), step, h, facecolor=rect_color, alpha=rect_alpha,
            edgecolor=color, lw=0.5, zorder=2,
        ))

    if show_error:
        exact = float(np.trapezoid(f(xg[np.logical_and(xg >= a, xg <= b)]),
                                   xg[np.logical_and(xg >= a, xg <= b)])) \
            if hasattr(np, "trapezoid") else float(np.trapz(
                f(xg[np.logical_and(xg >= a, xg <= b)]),
                xg[np.logical_and(xg >= a, xg <= b)]))
        err = abs(total - exact)
        label = {"mid": "midpoint", "left": "left", "right": "right"}[method]
        ax.text(0.5, 0.92,
                f"{label}, n={n}:  Σ = {total:.4g}   |error| = {err:.2e}",
                transform=ax.transAxes, ha="center", fontsize=10,
                color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.axhline(0, color="#999999", lw=0.8)
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
#  TANGENT  LINE
# ──────────────────────────────────────────────

def tangent_line(
    f: Callable,
    x0: float,
    a: float | None = None,
    b: float | None = None,
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "f(x)",
    figsize: tuple = (8, 5),
    color: str = "#2E86AB",
    tangent_color: str = "#C73E1D",
    n_grid: int = 400,
    h: float = 1e-6,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Function curve with its tangent line at x0 — derivative intuition.

    Parameters
    ----------
    f : callable
        Differentiable function.
    x0 : float
        Point of tangency.
    a, b : float, optional
        Plot range (defaults to [x0-2, x0+2] scaled to curvature).

    Returns
    -------
    Figure
    """
    f0 = float(f(x0))
    df0 = float((f(x0 + h) - f(x0 - h)) / (2 * h))

    if a is None or b is None:
        xs_probe = np.linspace(x0 - 2, x0 + 2, 100)
        span = float(np.nanmax(np.abs(f(xs_probe) - f0)) or 1)
        a = x0 - max(2, span)
        b = x0 + max(2, span)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    xg = np.linspace(a, b, n_grid)
    ax.plot(xg, f(xg), color=color, lw=2.2, label="f(x)")
    xtan = np.linspace(x0 - (b - a) * 0.35, x0 + (b - a) * 0.35, 50)
    ax.plot(xtan, f0 + df0 * (xtan - x0), color=tangent_color, lw=1.9,
            ls="--", label="tangent at x₀")
    ax.plot([x0], [f0], "o", ms=7, mfc=tangent_color, mec="white",
            mew=1.2, zorder=5)

    sign = "+" if df0 >= 0 else "−"
    ax.annotate(f"f'({x0:g}) = {sign}{abs(df0):.3g}",
                xy=(x0, f0), xytext=(15, 25), textcoords="offset points",
                fontsize=10, color=tangent_color,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=tangent_color, alpha=0.85),
                arrowprops=dict(arrowstyle="-|>", color=tangent_color, lw=1))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="both")
    ax.legend(frameon=False, loc="best")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  INTERPOLATION  COMPARISON
# ──────────────────────────────────────────────

def interpolation_comparison(
    x: Sequence[float],
    y: Sequence[float],
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (9, 5.5),
    degree: int = 3,
    methods: Sequence[str] = ("linear", "polynomial", "cubic"),
    sample_points: int = 300,
    data_color: str = "#333333",
    show_train_points: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Compare interpolation methods over the same sample points —
    the classic over/under-fitting illustration.

    Parameters
    ----------
    x, y : array-like
        Sample points to interpolate through.
    degree : int
        Polynomial degree for the 'polynomial' method.
    methods : sequence of str
        Any of 'linear', 'polynomial', 'cubic' (needs scipy).

    Returns
    -------
    Figure
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    order = np.argsort(x_arr)
    x_arr, y_arr = x_arr[order], y_arr[order]
    xd = np.linspace(x_arr[0], x_arr[-1], sample_points)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    if show_train_points:
        ax.scatter(x_arr, y_arr, s=42, color=data_color, zorder=5,
                   edgecolors="white", lw=0.8, label="data")

    from .palette import auto_colors
    colors = auto_colors(len(methods), "nature_qual")

    for i, m in enumerate(methods):
        m = m.lower()
        try:
            if m == "linear":
                yd = np.interp(xd, x_arr, y_arr)
                label = "linear"
            elif m == "polynomial":
                coeffs = np.polyfit(x_arr, y_arr, degree)
                yd = np.polyval(coeffs, xd)
                label = f"poly (deg {degree})"
            elif m == "cubic":
                from scipy.interpolate import CubicSpline
                yd = CubicSpline(x_arr, y_arr)(xd)
                label = "cubic spline"
            else:
                raise ValueError(
                    f"Unknown method '{m}'. Use linear / polynomial / cubic.")
        except ImportError as e:
            raise ImportError(f"Method '{m}' requires scipy installed.") from e
        ax.plot(xd, yd, color=colors[i % len(colors)], lw=1.9, label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    axis_config(ax, grid="both")
    ax.legend(frameon=False, loc="best")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "area_under_curve",
    "riemann_sum",
    "tangent_line",
    "interpolation_comparison",
]
