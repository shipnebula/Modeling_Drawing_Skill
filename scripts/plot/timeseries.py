"""
timeseries.py — Time-series diagnostics without statsmodels.

Charts:
    acf_pacf               — correlogram + partial autocorrelation
    seasonal_decomposition — trend / seasonal / residual panels

Everything is computed with numpy (Durbin–Levinson for the PACF,
centered moving average for the trend), so no extra dependency is
required beyond scipy's normal distribution for the confidence bands.

All functions return a matplotlib Figure ready for publication.
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .utils import setup_figure, save_figure, figsubplots, axis_config


# ──────────────────────────────────────────────
#  CORRELATION  HELPERS  (pure numpy)
# ──────────────────────────────────────────────

def _acf_values(x: np.ndarray, nlags: int) -> np.ndarray:
    x = x - x.mean()
    denom = float(np.dot(x, x)) or 1.0
    return np.array([
        1.0 if k == 0 else float(np.dot(x[:-k], x[k:]) / denom)
        for k in range(nlags + 1)
    ])


def _pacf_values(x: np.ndarray, nlags: int) -> np.ndarray:
    """Durbin–Levinson recursion."""
    acf = _acf_values(x, nlags)
    pacf = np.ones(nlags + 1)
    if nlags >= 1:
        pacf[1] = acf[1]
        phi = np.zeros((nlags + 1, nlags + 1))
        if nlags >= 1:
            phi[1, 1] = acf[1]
        for k in range(2, nlags + 1):
            num = acf[k] - np.dot(phi[k - 1, 1:k], acf[k - 1:0:-1])
            den = 1.0 - np.dot(phi[k - 1, 1:k], acf[1:k])
            pacf[k] = num / (den or 1e-12)
            phi[k, k] = pacf[k]
            phi[k, 1:k] = phi[k - 1, 1:k] - pacf[k] * phi[k - 1, k - 1:0:-1]
    return pacf


def _bar_panel(ax, values, nlags, conf, title, color):
    lags = np.arange(len(values))
    band = conf / np.sqrt(max(len(values) * 0.0 + 0, 1))  # replaced by caller
    ax.vlines(lags, 0, values, color=color, lw=2.2)
    ax.scatter(lags, values, s=18, color=color, zorder=3)
    ax.axhline(0, color="#666666", lw=0.8)
    ax.set_xlabel("lag")
    ax.set_title(title, fontsize=10)
    axis_config(ax, grid="y")


# ──────────────────────────────────────────────
#  ACF  +  PACF
# ──────────────────────────────────────────────

def acf_pacf(
    data,
    nlags: int | None = None,
    title: str | None = None,
    figsize: tuple = (10, 4.2),
    acf_color: str = "#2E86AB",
    pacf_color: str = "#A23B72",
    alpha: float = 0.05,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Correlogram pair for ARIMA order identification — ACF and PACF
    bars with the ± significance band.

    Parameters
    ----------
    data : 1-D array-like
        Stationary series (difference it yourself first).
    nlags : int, optional
        Defaults to ``min(40, n // 2 - 1)``.

    Returns
    -------
    Figure
    """
    from scipy.stats import norm

    x = np.asarray(data, dtype=float).ravel()
    n = len(x)
    if nlags is None:
        nlags = int(min(40, max(10, n // 2 - 1)))
    z = norm.ppf(1 - alpha / 2)
    band = z / np.sqrt(n)

    acf = _acf_values(x, nlags)
    pacf = _pacf_values(x, nlags)

    kwargs.pop("style", None)
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    lags = np.arange(nlags + 1)

    for ax, vals, color, name in (
        (axes[0], acf, acf_color, "ACF"),
        (axes[1], pacf, pacf_color, "PACF"),
    ):
        ax.vlines(lags, 0, vals, color=color, lw=2.2)
        ax.scatter(lags, vals, s=18, color=color, zorder=3)
        ax.axhline(band, color="#999999", lw=1, ls="--")
        ax.axhline(-band, color="#999999", lw=1, ls="--")
        ax.axhspan(-band, band, color="#CCCCCC", alpha=0.15, lw=0)
        ax.axhline(0, color="#666666", lw=0.8)
        ax.set_xlabel("lag")
        ax.set_ylabel(name)
        ax.set_title(f"{name} with {int((1 - alpha) * 100)}% band",
                     fontsize=10)
        axis_config(ax, grid="y")

    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SEASONAL  DECOMPOSITION
# ──────────────────────────────────────────────

def seasonal_decomposition(
    data,
    period: int,
    title: str | None = None,
    figsize: tuple = (10, 7),
    color: str = "#2E86AB",
    trend_color: str = "#C73E1D",
    model: str = "additive",
    panels: tuple = ("observed", "trend", "seasonal", "residual"),
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Classical decomposition (additive or multiplicative) computed with
    a centered moving average — trend, seasonal, and residual panels
    without statsmodels.

    Parameters
    ----------
    data : 1-D array-like
    period : int
        Season length (12 for monthly, 7 for daily-of-week...).
    model : str
        'additive' (x = trend + seasonal + resid) or
        'multiplicative' (x = trend · seasonal · resid).

    Returns
    -------
    Figure
    """
    x = np.asarray(data, dtype=float).ravel()
    n = len(x)
    if period < 2 or n < 2 * period:
        raise ValueError(
            f"seasonal_decomposition needs n >= 2×period; got n={n}, period={period}."
        )

    # centered moving average trend
    kernel = np.ones(period) / period
    if period % 2 == 0:  # 2×m MA for even periods
        trend = np.convolve(x, kernel, mode="valid")
        trend = np.convolve(trend, np.ones(2) / 2, mode="valid")
        pad = period // 2
    else:
        trend = np.convolve(x, kernel, mode="valid")
        pad = (period - 1) // 2
    trend_full = np.full(n, np.nan)
    trend_full[pad:n - pad] = trend

    if model == "multiplicative":
        detrended = x / trend_full
    else:
        detrended = x - trend_full

    # seasonal profile: mean detrended value per phase, tiled
    seasonal_profile = np.full(period, np.nan)
    for k in range(period):
        vals = detrended[k::period]
        vals = vals[~np.isnan(vals)]
        if len(vals):
            seasonal_profile[k] = vals.mean()
    if model == "multiplicative":
        seasonal_profile = seasonal_profile / np.nanmean(seasonal_profile)
    seasonal = np.tile(seasonal_profile, n // period + 1)[:n]

    if model == "multiplicative":
        residual = x / (trend_full * seasonal)
    else:
        residual = x - trend_full - seasonal

    kwargs.pop("style", None)
    rows = len(panels)
    fig, axes = plt.subplots(rows, 1, figsize=figsize, sharex=True)
    axes = np.atleast_1d(axes)
    series_map = {
        "observed": (x, color, "Observed"),
        "trend": (trend_full, trend_color, "Trend"),
        "seasonal": (seasonal, "#2A9D8F", "Seasonal"),
        "residual": (residual, "#888888", "Residual"),
    }
    for ax, name in zip(axes, panels):
        vals, c, label = series_map[name]
        kind = "bar" if name == "seasonal" and n <= 4 * period else "line"
        if kind == "bar":
            ax.bar(np.arange(n), vals, color=c, alpha=0.8, width=0.8)
        else:
            ax.plot(np.arange(n), vals, color=c, lw=1.5)
        ax.set_ylabel(label, fontsize=9.5)
        ax.grid(axis="y", alpha=0.15)
        ax.set_axisbelow(True)
    axes[0].set_title(title or f"Classical {model} decomposition "
                           f"(period = {period})",
                      fontsize=12, fontweight="bold", pad=10)
    axes[-1].set_xlabel("time")

    resid = residual[~np.isnan(residual)]
    if len(resid):
        axes[-1].axhline(0 if model == "additive" else 1,
                         color="#C73E1D", lw=0.9, ls="--", alpha=0.7)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig




# ──────────────────────────────────────────────
#  CROSS-CORRELATION  (lead–lag)
# ──────────────────────────────────────────────

def cross_correlation(
    series1,
    series2,
    max_lag: int = 24,
    title: str | None = None,
    xlabel: str = "lag (series1 vs series2)",
    figsize: tuple = (9, 4.5),
    color: str = "#2E86AB",
    highlight_color: str = "#C73E1D",
    norm: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Cross-correlation between two series across lags — identifies
    whether one series leads or lags the other, and by how much.
    The best-matching lag is highlighted.

    Parameters
    ----------
    series1, series2 : 1-D array-like
    max_lag : int
        Lags from -max_lag to +max_lag (positive = series1 is shifted
        forward relative to series2).

    Returns
    -------
    Figure
    """
    a = np.asarray(series1, dtype=float).ravel()
    b = np.asarray(series2, dtype=float).ravel()
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    a = a - a.mean()
    b = b - b.mean()

    lags = np.arange(-max_lag, max_lag + 1)
    values = []
    for lag in lags:
        if lag >= 0:
            u, v = a[lag:], b[:n - lag]
        else:
            u, v = a[:n + lag], b[-lag:]
        if len(u) < 10:
            values.append(np.nan)
            continue
        c = float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))) \
            if norm else float(np.dot(u, v))
        values.append(c)
    values = np.asarray(values)

    best = int(lags[int(np.nanargmax(values))])

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = [highlight_color if l == best else color for l in lags]
    ax.vlines(lags, 0, values, color=colors, lw=2.4)
    ax.scatter(lags, values, s=18,
               c=[highlight_color if l == best else color for l in lags],
               zorder=3)
    ax.axhline(0, color="#666666", lw=0.8)
    ax.annotate(
        f"best lag = {best:+d}\nr = {values[int(np.nanargmax(values))]:.3f}",
        xy=(best, values[int(np.nanargmax(values))]),
        xytext=(20, -8), textcoords="offset points", fontsize=9,
        color="#1D3557",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#CCCCCC", alpha=0.9))
    ax.set_xlabel(xlabel)
    ax.set_ylabel("correlation" if norm else "covariance")
    ax.set_xlim(-max_lag - 1, max_lag + 1)
    axis_config(ax, grid="y")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "acf_pacf",
    "seasonal_decomposition",
    "cross_correlation",
]
