"""
styles.py — Style presets for publication-quality matplotlib figures.

Each preset is a dictionary of rcParams that can be applied with
`plt.rcParams.update()` or via `apply_style()`.

Available presets:
    'nature'       — clean, minimal, inspired by Nature journal
    'publication'  — academic standard with full spines and grid
    'economist'    — modern editorial style with muted colors
    'minimal'      — ultra-minimal, axes-free
    'dark'         — dark background for presentations
    'poster'       — large fonts for conference posters

Usage:
    from plot.styles import apply_style, get_style_config
    apply_style('nature')
    config = get_style_config('publication')
"""

from __future__ import annotations


# ──────────────────────────────────────────────
#  STYLE  PRESETS
# ──────────────────────────────────────────────

_STYLES: dict[str, dict] = {}

# ── Nature ────────────────────────────────────
_STYLES["nature"] = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "DejaVu Sans", "Helvetica Neue", "Arial", "Liberation Sans",
    ],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "axes.labelweight": "normal",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "legend.frameon": False,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#888888",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": False,
    "ytick.right": False,
    "xtick.minor.visible": False,
    "ytick.minor.visible": False,
    "grid.alpha": 0.12,
    "grid.linestyle": "-",
    "grid.linewidth": 0.5,
    "grid.color": "#CCCCCC",
    "lines.linewidth": 1.8,
    "lines.markeredgewidth": 0.5,
    "patch.linewidth": 0.6,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
    "figure.autolayout": False,
    "figure.constrained_layout.use": False,
    "image.cmap": "viridis",
}

# ── Publication (academic standard) ──────────
_STYLES["publication"] = {
    **_STYLES["nature"],
    "axes.spines.top": True,
    "axes.spines.right": True,
    "xtick.top": True,
    "ytick.right": True,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "grid.alpha": 0.2,
    "grid.linestyle": "--",
    "grid.linewidth": 0.4,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "#999999",
}

# ── Economist (editorial) ────────────────────
_STYLES["economist"] = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "DejaVu Sans", "Helvetica Neue", "Arial", "Liberation Sans",
    ],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "legend.frameon": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#D3D3D3",
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "grid.alpha": 0.1,
    "grid.linestyle": "-",
    "grid.linewidth": 0.4,
    "grid.color": "#E0E0E0",
    "lines.linewidth": 2.0,
    "lines.markersize": 5,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "image.cmap": "viridis",
}

# ── Minimal ──────────────────────────────────
_STYLES["minimal"] = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "DejaVu Sans", "Helvetica Neue", "Arial", "Liberation Sans",
    ],
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "legend.frameon": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "none",
    "axes.linewidth": 0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.spines.bottom": False,
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "grid.alpha": 0.08,
    "grid.linestyle": "-",
    "grid.linewidth": 0.4,
    "grid.color": "#E0E0E0",
    "lines.linewidth": 1.8,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "image.cmap": "viridis",
}

# ── Dark ─────────────────────────────────────
_STYLES["dark"] = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "DejaVu Sans", "Helvetica Neue", "Arial", "Liberation Sans",
    ],
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "legend.frameon": True,
    "legend.framealpha": 0.8,
    "legend.edgecolor": "#444444",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.facecolor": "#1A1A2E",
    "savefig.facecolor": "#1A1A2E",
    "axes.facecolor": "#16213E",
    "axes.edgecolor": "#444444",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "xtick.color": "#CCCCCC",
    "ytick.color": "#CCCCCC",
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "grid.alpha": 0.15,
    "grid.linestyle": "-",
    "grid.linewidth": 0.5,
    "grid.color": "#2A2A4A",
    "text.color": "#EEEEEE",
    "axes.labelcolor": "#EEEEEE",
    "axes.titlecolor": "#EEEEEE",
    "xtick.labelcolor": "#CCCCCC",
    "ytick.labelcolor": "#CCCCCC",
    "lines.linewidth": 2.0,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "image.cmap": "inferno",
}

# ── Poster ───────────────────────────────────
_STYLES["poster"] = {
    **_STYLES["nature"],
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 15,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
    "figure.titlesize": 20,
    "lines.linewidth": 2.5,
    "lines.markersize": 8,
}

# ── Dark poster ──────────────────────────────
_STYLES["dark_poster"] = {
    **_STYLES["dark"],
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 15,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
    "figure.titlesize": 20,
    "lines.linewidth": 2.5,
    "lines.markersize": 8,
}


# ──────────────────────────────────────────────
#  COLOR  THEME  CONFIGS  (default colors per style)
# ──────────────────────────────────────────────

COLOR_THEMES: dict[str, dict] = {
    "nature": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "accent": "#F18F01",
        "highlight": "#C73E1D",
        "neutral": "#D3D3D3",
        "text": "#333333",
        "grid": "#CCCCCC",
        "background": "white",
    },
    "publication": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "accent": "#F18F01",
        "highlight": "#C73E1D",
        "neutral": "#D3D3D3",
        "text": "#333333",
        "grid": "#CCCCCC",
        "background": "white",
    },
    "economist": {
        "primary": "#76b7b2",
        "secondary": "#5b5b5b",
        "accent": "#ff9833",
        "highlight": "#e3707c",
        "neutral": "#d9d9d9",
        "text": "#333333",
        "grid": "#E0E0E0",
        "background": "white",
    },
    "minimal": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "accent": "#F18F01",
        "highlight": "#C73E1D",
        "neutral": "#D3D3D3",
        "text": "#333333",
        "grid": "#E0E0E0",
        "background": "white",
    },
    "dark": {
        "primary": "#4ECDC4",
        "secondary": "#F15BB5",
        "accent": "#FEE440",
        "highlight": "#00BBF9",
        "neutral": "#2A2A4A",
        "text": "#EEEEEE",
        "grid": "#2A2A4A",
        "background": "#1A1A2E",
    },
}


# ──────────────────────────────────────────────
#  API
# ──────────────────────────────────────────────


def get_style_config(style_name: str = "nature") -> dict:
    """
    Return the rcParams dict for a given style.

    Parameters
    ----------
    style_name : str
        One of: 'nature', 'publication', 'economist', 'minimal',
        'dark', 'poster', 'dark_poster'.

    Returns
    -------
    dict
        Matplotlib rcParams dictionary.
    """
    if style_name not in _STYLES:
        raise ValueError(
            f"Unknown style '{style_name}'. "
            f"Available: {sorted(_STYLES.keys())}"
        )
    return dict(_STYLES[style_name])


def get_color_theme(style_name: str = "nature") -> dict:
    """Return the color theme dict for a given style."""
    if style_name not in COLOR_THEMES:
        raise ValueError(
            f"Unknown style '{style_name}'. "
            f"Available: {sorted(COLOR_THEMES.keys())}"
        )
    return dict(COLOR_THEMES[style_name])


def apply_style(style_name: str = "nature") -> dict:
    """
    Apply a style preset to matplotlib's global rcParams.

    Parameters
    ----------
    style_name : str
        Style preset name.

    Returns
    -------
    dict
        The rcParams that were applied.
    """
    import matplotlib as mpl

    config = get_style_config(style_name)
    mpl.rcParams.update(config)
    return config


def apply_style_to_axes(ax, style_name: str = "nature") -> None:
    """
    Apply style settings to a specific Axes object (not global).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to style.
    style_name : str
        Style preset name.
    """
    config = get_style_config(style_name)

    for key, val in config.items():
        if key == "axes.facecolor":
            ax.set_facecolor(val)
        elif key == "axes.edgecolor":
            ax.patch.set_edgecolor(val)
        elif key == "axes.linewidth":
            ax.patch.set_linewidth(val)
        elif key == "axes.spines.top":
            ax.spines["top"].set_visible(val)
        elif key == "axes.spines.right":
            ax.spines["right"].set_visible(val)
        elif key == "axes.spines.left":
            ax.spines["left"].set_visible(val)
        elif key == "axes.spines.bottom":
            ax.spines["bottom"].set_visible(val)
        elif key == "xtick.direction":
            ax.tick_params(axis="x", direction=val)
        elif key == "ytick.direction":
            ax.tick_params(axis="y", direction=val)
        elif key == "xtick.top":
            ax.tick_params(axis="x", top=val)
        elif key == "ytick.right":
            ax.tick_params(axis="y", right=val)
        elif key == "xtick.major.size":
            ax.tick_params(axis="x", width=0, length=val)
        elif key == "ytick.major.size":
            ax.tick_params(axis="y", width=0, length=val)
        elif key == "xtick.major.width":
            ax.tick_params(axis="x", width=val, length=4)
        elif key == "ytick.major.width":
            ax.tick_params(axis="y", width=val, length=4)


def list_styles() -> list[str]:
    """Return all available style names."""
    return sorted(_STYLES.keys())


__all__ = [
    "get_style_config",
    "get_color_theme",
    "apply_style",
    "apply_style_to_axes",
    "list_styles",
    "COLOR_THEMES",
]