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
#  CJK  FONT  AUTO-DETECTION
# ──────────────────────────────────────────────

_CJK_FONT_CANDIDATES: tuple[str, ...] = (
    "Microsoft YaHei",   # Windows
    "SimHei",            # Windows
    "SimSun",            # Windows
    "PingFang SC",       # macOS
    "Hiragino Sans GB",  # macOS
    "Noto Sans CJK SC",  # Linux
    "Source Han Sans SC",
    "WenQuanYi Micro Hei",
    "Malgun Gothic",     # Korean
)

_cjk_fonts_cache: list[str] | None = None


def detect_cjk_fonts() -> list[str]:
    """Return CJK fonts installed on this system (scanned once)."""
    global _cjk_fonts_cache
    if _cjk_fonts_cache is not None:
        return _cjk_fonts_cache
    found: list[str] = []
    try:
        from matplotlib import font_manager
        installed = {f.name for f in font_manager.fontManager.ttflist}
        found = [f for f in _CJK_FONT_CANDIDATES if f in installed]
    except Exception:
        found = []
    _cjk_fonts_cache = found
    return found


def setup_cjk() -> list[str]:
    """
    Prepend installed CJK fonts to ``font.sans-serif`` so Chinese /
    Japanese / Korean labels render without manual rcParams edits.

    Called automatically by :func:`apply_style`; safe to call directly.
    Returns the fonts that were applied (empty if none found).
    """
    import matplotlib as mpl

    found = detect_cjk_fonts()
    if found:
        current = [f for f in mpl.rcParams["font.sans-serif"]
                   if f not in found]
        mpl.rcParams["font.sans-serif"] = found + current
        mpl.rcParams["axes.unicode_minus"] = False
    return found


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


# Last style applied at global level — lets repeated calls with the
# same name skip the (relatively slow) rcParams.update.
_last_applied: str | None = None


def apply_style(style_name: str = "nature") -> dict:
    """
    Apply a style preset to matplotlib's global rcParams.

    Repeated calls with the same name are no-ops (cached), which keeps
    per-figure overhead near zero in batch rendering.

    Parameters
    ----------
    style_name : str
        Style preset name.

    Returns
    -------
    dict
        The rcParams that were applied.
    """
    global _last_applied
    import matplotlib as mpl

    if style_name == _last_applied:
        return get_style_config(style_name)

    config = get_style_config(style_name)
    mpl.rcParams.update(config)
    _last_applied = style_name
    setup_cjk()
    return config


def use_latex(enabled: bool = True):
    """Context manager to render all text with LaTeX/mathtext.

    Uses real LaTeX when installed (``text.usetex``), otherwise falls
    back to matplotlib's built-in mathtext so math never breaks.

    >>> with use_latex():
    ...     plot(x, y, title=r"$\\eta$ vs $\\tau$", xlabel=r"$t/\\mathrm{s}$")
    """
    import matplotlib as mpl

    class _Latex:
        def __enter__(self):
            self._old = {k: mpl.rcParams[k] for k in (
                "text.usetex", "text.latex.preamble", "font.family")}
            try:
                mpl.rcParams["text.usetex"] = bool(enabled)
            except Exception:
                pass
            return self

        def __exit__(self, exc_type, exc, tb):
            mpl.rcParams.update(self._old)
            return False

    return _Latex()


# ──────────────────────────────────────────────
#  THEMES  (style + palette bundles)
# ──────────────────────────────────────────────

THEMES: dict[str, dict] = {
    # classic paper themes
    "nature": {"style": "nature", "palette": "nature_qual"},
    "publication": {"style": "publication", "palette": "nature_qual"},
    "economist": {"style": "economist", "palette": "economist"},
    "dark": {"style": "dark", "palette": "vivid_dark"},
    "poster": {"style": "poster", "palette": "nature_qual"},
    # accessibility-first themes
    "colorblind": {"style": "nature", "palette": "tol_8"},
    "colorblind_dark": {"style": "dark", "palette": "tol_8"},
    "morandi_paper": {"style": "nature", "palette": "morandi"},
    # analysis-flavored themes
    "ocean": {"style": "nature", "palette": "ocean"},
    "sunset_report": {"style": "economist", "palette": "sunset"},
    "forest_report": {"style": "nature", "palette": "forest"},
}


def apply_theme(name: str = "nature") -> dict:
    """
    Apply a curated theme — a style preset + palette + sensible
    defaults in one call (e.g. 'colorblind' for accessibility-first
    figures, 'dark' for slides).

    Returns
    -------
    dict
        The theme definition that was applied.

    See Also
    --------
    list_themes
    """
    if name not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Available: {sorted(THEMES)}")
    theme = dict(THEMES[name])
    apply_style(theme["style"])
    from .palette import auto_colors
    auto_colors(8, theme["palette"])  # warm the palette cache
    return theme


def list_themes() -> list[str]:
    """Return all available theme names."""
    return sorted(THEMES)


# ──────────────────────────────────────────────
#  USER  CONFIG  (.mmvrc.json)
# ──────────────────────────────────────────────


def load_config(path: str | None = None) -> dict:
    """
    Apply user defaults from a JSON config and return it.

    Recognized keys: ``style``, ``palette``, ``theme``, ``dpi``,
    ``figsize``. With no ``path``, searches ``./.mmvrc.json`` then
    ``~/.mmvrc.json`` (first hit wins).

    Example ``.mmvrc.json``::

        {"theme": "colorblind", "dpi": 200, "figsize": [9, 5]}

    Called automatically at import when such a file exists next to the
    running script — project-local look defaults with zero code.
    """
    import json
    import os

    if path is None:
        for candidate in (os.path.join(os.getcwd(), ".mmvrc.json"),
                          os.path.join(os.path.expanduser("~"), ".mmvrc.json")):
            if os.path.exists(candidate):
                path = candidate
                break
    if path is None or not os.path.exists(path):
        return {}

    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)

    if "theme" in cfg:
        apply_theme(cfg["theme"])
    elif "style" in cfg:
        apply_style(cfg["style"])
    if "palette" in cfg:
        import matplotlib as mpl
        from .palette import get_palette
        try:
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(
                color=get_palette(cfg["palette"]))
        except ValueError:
            pass
    if "dpi" in cfg:
        import matplotlib as mpl
        mpl.rcParams["figure.dpi"] = cfg["dpi"]
        mpl.rcParams["savefig.dpi"] = cfg["dpi"]
    if "figsize" in cfg:
        import matplotlib as mpl
        mpl.rcParams["figure.figsize"] = list(cfg["figsize"])
    return cfg


class style:
    """
    Context manager for temporary styles — the original style is
    restored on exit.

    Example
    -------
    >>> from plot import style
    >>> with style("dark"):
    ...     fig = plot(data)          # rendered dark
    ...     fig.savefig("dark.png")
    >>> fig = plot(data)              # back to the previous style
    """

    def __init__(self, style_name: str = "nature"):
        self.name = style_name
        self._previous: str | None = None
        self._previous_params: dict | None = None

    def __enter__(self):
        import matplotlib as mpl
        self._previous = _last_applied
        self._previous_params = {k: mpl.rcParams[k]
                                 for k in get_style_config(self.name)}
        apply_style(self.name)
        return self

    def __exit__(self, exc_type, exc, tb):
        import matplotlib as mpl
        if self._previous_params:
            mpl.rcParams.update(self._previous_params)
        globals()["_last_applied"] = self._previous
        return False


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
    "detect_cjk_fonts",
    "setup_cjk",
    "style",
    "use_latex",
    "apply_theme",
    "list_themes",
    "THEMES",
    "load_config",
]