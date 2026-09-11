"""
utils.py — Shared helper utilities for publication-quality figures.

Provides:
    setup_figure()    — create a figure with correct styling
    save_figure()     — save with proper DPI and format
    format_numbers()  — human-readable number formatting
    auto_palette()    — auto-generate colors
    add_annotation()  — annotation with arrow
    axis_config()     — configure axis styling
    add_grid()        — add publication-style grid
    add_data_labels() — add value labels to bars
    figsubplots()     — multi-panel figure helper
"""

from __future__ import annotations

import os
from typing import Any, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .palette import auto_colors as _auto_colors
from .styles import apply_style as _apply_style


# ──────────────────────────────────────────────
#  FIGURE  SETUP
# ──────────────────────────────────────────────

# Standard figure sizes (in inches)
FIGSIZE = {
    "small": (4, 3),
    "medium": (8, 5),
    "large": (10, 6),
    "wide": (12, 5),
    "tall": (5, 8),
    "square": (6, 6),
    "poster": (16, 10),
}


def setup_figure(
    figsize: tuple[float, float] | str = "medium",
    style: str = "nature",
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Create a figure and axes with publication-quality defaults.

    Parameters
    ----------
    figsize : tuple or str
        (width, height) in inches, or a preset name from FIGSIZE.
    style : str
        Style preset name (default 'nature').
    **kwargs
        Passed to plt.subplots().

    Returns
    -------
    (fig, ax) : tuple
    """
    _apply_style(style)

    if isinstance(figsize, str):
        figsize = FIGSIZE.get(figsize, (8, 5))

    fig, ax = plt.subplots(figsize=figsize, **kwargs)
    return fig, ax


def figsubplots(
    nrows: int = 1,
    ncols: int = 1,
    figsize: tuple[float, float] | str = "large",
    style: str = "nature",
    sharex: bool = False,
    sharey: bool = False,
    **kwargs,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Multi-panel figure with consistent styling.

    Parameters
    ----------
    nrows, ncols : int
        Grid dimensions.
    figsize : tuple or str
        Figure size.
    style : str
        Style preset.
    sharex, sharey : bool
        Share axes.
    **kwargs
        Passed to plt.subplots().

    Returns
    -------
    (fig, axes) : tuple
    """
    _apply_style(style)

    if isinstance(figsize, str):
        figsize = FIGSIZE.get(figsize, (10, 6))

    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=figsize,
        sharex=sharex, sharey=sharey, **kwargs,
    )
    return fig, axes


def save_figure(
    fig: plt.Figure,
    filename: str = "output.png",
    dpi: int = 300,
    fmt: str | None = None,
    bbox_inches: str = "tight",
    pad_inches: float = 0.08,
    transparent: bool = False,
    close: bool = True,
) -> str:
    """
    Save a figure with publication-quality settings.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    filename : str
        Output file path.
    dpi : int
        Resolution (default 300 for print).
    fmt : str, optional
        Override format (png, pdf, svg). Auto-detected from extension.
    bbox_inches : str
        'tight' trims white space.
    pad_inches : float
        Padding around content.
    transparent : bool
        Transparent background.
    close : bool
        Close the figure after saving to free memory (default True).

    Returns
    -------
    str
        The resolved output file path.
    """
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    if fmt is None:
        fmt = filename.rsplit(".", 1)[-1].lower()
        if fmt not in ("png", "pdf", "svg", "jpg", "jpeg", "tif", "tiff", "eps"):
            fmt = "png"
    else:
        filename = os.path.splitext(filename)[0] + f".{fmt.lower()}"

    fig.savefig(
        filename,
        dpi=dpi,
        format=fmt.lower(),
        bbox_inches=bbox_inches,
        pad_inches=pad_inches,
        facecolor=fig.get_facecolor() if not transparent else "none",
        transparent=transparent,
    )
    if close:
        plt.close(fig)
    return filename


# ──────────────────────────────────────────────
#  NUMBER  FORMATTING
# ──────────────────────────────────────────────

def format_numbers(
    value: float | int,
    style: str = "smart",
    decimals: int = 2,
) -> str:
    """
    Format a number for display.

    Parameters
    ----------
    value : float or int
        Number to format.
    style : str
        'smart' — auto-scales with K/M/B suffixes
        'thousands' — comma separators
        'decimal' — fixed decimal places
        'scientific' — scientific notation
        'percent' — as percentage
        'scientific_2' — 2 significant digits
    decimals : int
        Decimal places for 'decimal' style.

    Returns
    -------
    str
    """
    v = abs(value)
    if style == "smart":
        if v >= 1e9:
            return f"{value / 1e9:.1f}B"
        if v >= 1e6:
            return f"{value / 1e6:.1f}M"
        if v >= 1e4:
            return f"{value / 1e3:.1f}K"
        if v < 0.01 and v > 0:
            return f"{value:.2e}"
        if v == 0:
            return "0"
        # Format as integer if it's a whole number
        if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
            return str(int(value))
        return f"{value:.{decimals}f}"

    if style == "thousands":
        if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
            return f"{int(value):,}"
        return f"{value:,.{decimals}f}"
    if style == "decimal":
        return f"{value:.{decimals}f}"
    if style == "scientific":
        return f"{value:.2e}"
    if style == "scientific_2":
        return f"{value:.2e}"
    if style == "percent":
        return f"{value * 100:.1f}%"

    # Default: format as integer if it's a whole number, otherwise use decimals
    if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
        return str(int(value))
    return f"{value:.{decimals}f}"


# ──────────────────────────────────────────────
#  AXIS  CONFIGURATION
# ──────────────────────────────────────────────

def axis_config(
    ax: plt.Axes,
    style: str = "nature",
    grid: str = "y",
    grid_alpha: float = 0.15,
    show_top: bool = False,
    show_right: bool = False,
    spine_color: str = "#666666",
) -> None:
    """
    Configure axis spines and grid.

    Parameters
    ----------
    ax : Axes
    style : str
        'nature' (minimal, no top/right), 'publication' (full), 'minimal' (none)
    grid : str
        'y', 'x', 'both', 'none'
    grid_alpha : float
    show_top, show_right : bool
    spine_color : str
    """
    if style == "nature" or style == "economist":
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    elif style == "minimal":
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(bottom=False, left=False)
    elif style == "publication":
        pass  # keep all spines

    ax.spines["left"].set_color(spine_color)
    ax.spines["bottom"].set_color(spine_color)
    ax.spines["top"].set_visible(show_top)
    if show_top:
        ax.spines["top"].set_color(spine_color)
    ax.spines["right"].set_visible(show_right)
    if show_right:
        ax.spines["right"].set_color(spine_color)

    if grid in ("y", "both"):
        ax.grid(
            axis="y", alpha=grid_alpha, linestyle="-",
            linewidth=0.5, color="#CCCCCC",
        )
        ax.set_axisbelow(True)
    if grid in ("x", "both"):
        ax.grid(
            axis="x", alpha=grid_alpha, linestyle="-",
            linewidth=0.5, color="#CCCCCC",
        )
        ax.set_axisbelow(True)


def add_grid(
    ax: plt.Axes,
    axis: str = "y",
    alpha: float = 0.15,
    linestyle: str = "-",
    linewidth: float = 0.5,
    color: str = "#CCCCCC",
) -> None:
    """Add a grid to the axes."""
    if axis == "both":
        ax.grid(axis="both", alpha=alpha, linestyle=linestyle,
                linewidth=linewidth, color=color)
    else:
        ax.grid(axis=axis, alpha=alpha, linestyle=linestyle,
                linewidth=linewidth, color=color)
    ax.set_axisbelow(True)


# ──────────────────────────────────────────────
#  ANNOTATIONS
# ──────────────────────────────────────────────

def add_annotation(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    arrow: bool = True,
    arrow_to: tuple[float, float] | None = None,
    text_color: str = "#333333",
    arrow_color: str = "#666666",
    fontsize: float = 9,
    fontweight: str = "normal",
    bbox: dict | None = None,
    arrow_props: dict | None = None,
    va: str = "top",
    ha: str = "center",
    xytext: tuple[float, float] | None = None,
    annotation_clip: bool = False,
) -> plt.text.Text:
    """
    Add an annotation with optional arrow.

    Parameters
    ----------
    ax : Axes
    x, y : float
        Annotation text position (in data coords if xytext is None,
        else the arrow target).
    text : str
        Annotation text.
    arrow : bool
        Draw an arrow.
    arrow_to : (float, float), optional
        Arrow target (data coords).
    text_color, arrow_color : str
    fontsize : float
    fontweight : str
    bbox : dict, optional
        Bbox dict for text background.
    arrow_props : dict, optional
        Arrow style dict.
    va, ha : str
        Vertical/horizontal alignment.
    xytext : (float, float), optional
        If provided, text position in display coords; arrow goes to (x, y).
    annotation_clip : bool
        Whether to clip annotation at axes boundary.

    Returns
    -------
    Text
        The annotation text object.
    """
    text_kwargs = dict(
        color=text_color,
        fontsize=fontsize,
        fontweight=fontweight,
        va=va,
        ha=ha,
    )
    if bbox:
        text_kwargs["bbox"] = bbox

    if arrow_props is None:
        arrow_props = dict(
            arrowstyle="-|>",
            color=arrow_color,
            lw=1,
            connectionstyle="arc3,rad=0",
        )

    if xytext is not None:
        return ax.annotate(
            text,
            xy=(x, y),
            xytext=xytext,
            textcoords="data",
            arrowprops=arrow_props if arrow else None,
            annotation_clip=annotation_clip,
            **text_kwargs,
        )

    if arrow and arrow_to is not None:
        return ax.annotate(
            text,
            xy=arrow_to,
            xytext=(x, y),
            textcoords="data",
            arrowprops=arrow_props,
            annotation_clip=annotation_clip,
            **text_kwargs,
        )

    return ax.text(x, y, text, **text_kwargs)


def add_data_labels(
    bars: Sequence,
    ax: plt.Axes,
    fmt: str = "{:.2f}",
    fontsize: float = 8,
    color: str = "#333333",
    offset: float = 0.01,
    horizontal: bool = False,
) -> None:
    """
    Add value labels on top of bars.

    Parameters
    ----------
    bars : list of BarContainer
    ax : Axes
    fmt : str
        Format string for the value.
    fontsize : float
    color : str
    offset : float
        Offset from bar top (fraction of max data).
    horizontal : bool
        If True, position labels to the right of bars (for barh).
    """
    data = [b.get_height() if not horizontal else b.get_width() for b in bars]
    max_val = max(abs(v) for v in data) if data else 1

    for bar in bars:
        val = bar.get_height() if not horizontal else bar.get_width()
        if horizontal:
            x = val + max_val * offset
            y = bar.get_y() + bar.get_height() / 2
            ax.text(x, y, fmt.format(val),
                    va="center", ha="left", fontsize=fontsize, color=color)
        else:
            x = bar.get_x() + bar.get_width() / 2
            y = val + max_val * offset
            ax.text(x, y, fmt.format(val),
                    ha="center", va="bottom", fontsize=fontsize, color=color)


# ──────────────────────────────────────────────
#  COLOR  HELPERS
# ──────────────────────────────────────────────

def auto_palette(
    n: int,
    palette: str = "nature_qual",
    skip: int = 0,
) -> list[str]:
    """Auto-generate *n* colors from a palette."""
    return _auto_colors(n, palette, skip=skip)


# ──────────────────────────────────────────────
#  TICK  FORMATTERS
# ──────────────────────────────────────────────

def format_ticks(
    ax: plt.Axes,
    axis: str = "y",
    style: str = "smart",
    decimals: int = 2,
) -> None:
    """
    Format axis ticks with human-readable numbers.

    Parameters
    ----------
    ax : Axes
    axis : str
        'x', 'y', or 'both'.
    style : str
        Format style (see format_numbers).
    decimals : int
        Decimal places.
    """
    axes = ["y", "x"] if axis == "both" else [axis]
    for a in axes:
        formatter = _TickFormatter(style, decimals)
        ax.set_yticklabels(
            [formatter.format(v) for v in ax.get_yticks()],
            axis=a,
        )


def _TickFormatter(style: str, decimals: int):
    """Internal formatter for tick labels."""
    def format(v: float) -> str:
        return format_numbers(v, style=style, decimals=decimals)
    return type("Formatter", (), {"format": staticmethod(format)})()


# ──────────────────────────────────────────────
#  LAYOUT  HELPERS
# ──────────────────────────────────────────────

def auto_layout(
    fig: plt.Figure,
    pad: float = 0.1,
    hspace: float | None = None,
    wspace: float | None = None,
) -> None:
    """
    Apply tight layout with custom padding.

    Parameters
    ----------
    fig : Figure
    pad : float
        Edge padding (fraction of figure).
    hspace, wspace : float, optional
        Row/column spacing.
    """
    hspace = hspace if hspace is not None else pad
    wspace = wspace if wspace is not None else pad
    fig.subplots_adjust(
        left=pad, right=1 - pad,
        top=1 - pad, bottom=pad,
        hspace=hspace, wspace=wspace,
    )


def add_figure_title(
    fig: plt.Figure,
    title: str,
    subtitle: str | None = None,
    fontsize: float = 14,
    pad: float = 12,
    color: str = "#1A1A1A",
    y: float = 0.98,
) -> None:
    """Add a figure-level title with optional subtitle."""
    fig.suptitle(
        title,
        fontsize=fontsize,
        fontweight="bold",
        color=color,
        y=y,
        x=0.5,
    )
    if subtitle:
        fig.text(
            0.5, y - 0.04, subtitle,
            fontsize=fontsize * 0.7,
            color="#666666",
            ha="center", va="top",
        )


# ──────────────────────────────────────────────
#  EXPORT  METADATA  (for reproducibility)
# ──────────────────────────────────────────────

def add_source_note(
    ax: plt.Axes,
    note: str,
    fontsize: float = 7,
    color: str = "#999999",
    x: float = 0.0,
    y: float = -0.08,
) -> None:
    """
    Add a source note below the axes (for academic papers).

    Parameters
    ----------
    ax : Axes
    note : str
        Source text.
    """
    ax.text(
        x, y, note,
        transform=ax.transAxes,
        fontsize=fontsize, color=color,
        ha="left", va="top",
    )


__all__ = [
    "FIGSIZE",
    "setup_figure",
    "figsubplots",
    "save_figure",
    "format_numbers",
    "axis_config",
    "add_grid",
    "add_annotation",
    "add_data_labels",
    "auto_palette",
    "format_ticks",
    "auto_layout",
    "add_figure_title",
    "add_source_note",
]