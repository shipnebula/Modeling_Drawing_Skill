"""
palette.py — Professional color palettes for publication-quality figures.

Curated for Nature-style journals, colorblind accessibility, and
mathematical modeling competition papers (CUMCM / MCM-ICM).

Palettes are organized into four families:
    Qualitative   — categorical / discrete data (bars, groups, nodes)
    Sequential    — ordered magnitude (heatmaps, density)
    Diverging     — centered magnitude (correlations, signed values)
    Accent        — highlight a single data series on neutral background

Usage:
    from plot.palette import get_palette, auto_colors, get_color
    colors = auto_colors(5)              # 5 qualitative colors
    pal    = get_palette('viridis')      # full sequential palette
    c      = get_color('nature_qual', 2) # third qualitative color
"""

from __future__ import annotations

import colorsys
from typing import List


# ──────────────────────────────────────────────
#  INTERNAL  COLOR  UTILITIES
# ──────────────────────────────────────────────

def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def _seq(start: str, end: str, n: int = 9) -> list[str]:
    """Linearly interpolate between two hex colors, returning n hex strings."""
    s = _hex_to_rgb(start)
    e = _hex_to_rgb(end)
    return [
        _rgb_to_hex(
            tuple(s[i] + (e[i] - s[i]) * k / (n - 1) for i in range(3))
        )
        for k in range(n)
    ]


def _div(low: str, high: str, n: int = 9) -> list[str]:
    """Diverging palette: low -> white -> high."""
    s = _hex_to_rgb(low)
    e = _hex_to_rgb(high)
    w = (255, 255, 255)
    half = n // 2
    return (
        [
            _rgb_to_hex(
                tuple(s[i] + (w[i] - s[i]) * k / half for i in range(3))
            )
            for k in range(half + 1)
        ]
        + [
            _rgb_to_hex(
                tuple(w[i] + (e[i] - w[i]) * k / (n - half) for i in range(3))
            )
            for k in range(1, n - half)
        ]
    )


# ──────────────────────────────────────────────
#  QUALITATIVE PALETTES  (categorical / discrete)
# ──────────────────────────────────────────────

QUALITATIVE: dict[str, list[str]] = {

    # Inspired by Nature / Science journal color usage
    "nature_qual": [
        "#2E86AB", "#A23B72", "#F18F01", "#C73E1D",
        "#3B1F2B", "#44BBA4", "#E94F37", "#84BC92",
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    ],

    "nature_soft": [
        "#7FB3D5", "#C77DA0", "#F7B733", "#E07A5F",
        "#9D8189", "#87D3C8", "#F2995E", "#A8C7A8",
        "#E8A0A0", "#87CEEB", "#7EC0EE", "#B8E6C8",
    ],

    # Paul Tol – colorblind-safe (https://www.sci.muni.ca/~tol/colour/)
    "tol_8": [
        "#4472C4", "#ED7D31", "#5B9BD5", "#70AD47",
        "#FFC000", "#7030A0", "#00B0F0", "#FFC000",
    ],

    "tol_8_unique": [
        "#4472C4", "#ED7D31", "#5B9BD5", "#70AD47",
        "#FFC000", "#7030A0", "#00B0F0", "#808080",
    ],

    # Dave Green – colorblind-safe
    "green_8": [
        "#009E73", "#E69F00", "#56B4E9", "#CC79A7",
        "#F0E442", "#0072B2", "#D55E00", "#999999",
    ],

    # "Economist" / editorial style — muted, sophisticated
    "economist": [
        "#76b7b2", "#5b5b5b", "#ff9833", "#e3707c",
        "#d75f87", "#4d7f1a", "#84b4e6", "#c7c7c7",
    ],

    # "Pastel" — gentle, soft colors for subtle backgrounds
    "pastel": [
        "#E6F3FF", "#E6FFE6", "#FFF4E6", "#FFE6E6",
        "#F0E6FF", "#E6FFF0", "#FFE6F3", "#F0F0E6",
    ],

    # Dark mode — vibrant on dark background
    "neon": [
        "#00F5D4", "#F15BB5", "#FEE440", "#9B5DE5",
        "#00BBF9", "#F15BB5", "#00F5D4", "#9B5DE5",
    ],

    # Grayscale — for B&W printing
    "grayscale": [
        "#2C3E50", "#7F8C8D", "#BDC3C7", "#E74C3C",
        "#F39C12", "#9B59B6", "#1ABC9C", "#34495E",
    ],

    "grayscale_soft": [
        "#34495E", "#7F8C8D", "#95A5A6", "#BDC3C7",
        "#D5D8DC", "#EAECEE", "#F4F6F7", "#1C2833",
    ],

    # "Ocean" — cool blues and teals for data analysis
    "ocean": [
        "#03045E", "#0077B6", "#00B4D8", "#90E0EF",
        "#48CAE4", "#0096C7", "#023E8A", "#CAF0F8",
    ],

    # "Sunset" — warm tones for comparison / ranking
    "sunset": [
        "#FF6B6B", "#FFA07A", "#FFD93D", "#6BCB77",
        "#4D96FF", "#9B59B6", "#F0932B", "#EB4D4B",
    ],

    # "Forest" — earthy greens and browns
    "forest": [
        "#2D6A4F", "#52B788", "#74C69D", "#B7E4C7",
        "#D8F3DC", "#1B4332", "#40916C", "#95D5B2",
    ],

    # "Berry" — rich, saturated for high-contrast
    "berry": [
        "#6A0572", "#AB63BC", "#3A0CA3", "#4361EE",
        "#4CC9F0", "#F72585", "#B5179E", "#7209B7",
    ],

    # "Metal" — metallic, premium feel
    "metal": [
        "#FFD700", "#C0C0C0", "#CD7F32", "#808080",
        "#E5E4E2", "#B76E79", "#C0A062", "#84BBFF",
    ],
}

# ──────────────────────────────────────────────
#  SEQUENTIAL PALETTES  (ordered magnitude)
# ──────────────────────────────────────────────

# These are listed as lists of hex values. The number of entries
# doesn't matter — colormap interpolation handles arbitrary lengths.

SEQUENTIAL: dict[str, list[str]] = {

    # Matplotlib classics
    "viridis":    _seq("#440154", "#FDE725", 9),
    "cividis":    _seq("#00224E", "#FFE94F", 9),
    "inferno":    _seq("#000004", "#FCFFA4", 9),
    "magma":      _seq("#000004", "#FCFDBF", 9),
    "plasma":     _seq("#0D0887", "#F0F921", 9),
    "blues":      _seq("#F7FBFF", "#08306B", 9),
    "greens":     _seq("#F7FCF5", "#00441B", 9),
    "oranges":    _seq("#FFF5EB", "#7F2704", 9),
    "reds":       _seq("#FFF5F0", "#67000D", 9),
    "purples":    _seq("#FCFBFF", "#40004B", 9),
    "YlGnBu":     _seq("#FFFFE5", "#08519C", 9),
    "YlOrRd":     _seq("#FFFFCC", "#7F0000", 9),
    "PuBuGn":     _seq("#FFF7BC", "#005A52", 9),
    "RdYlBu":     _seq("#FC8D59", "#3282B4", 9),
    "Spectral":   _seq("#9E0142", "#5EF46B", 9),

    # Custom sequential
    "nature_seq": _seq("#E6F0F7", "#1B4965", 9),
    "earth_seq":  _seq("#FFF3B0", "#54243C", 9),
    "ocean_seq":  _seq("#D6F3FF", "#02113B", 9),
}

# ──────────────────────────────────────────────
#  DIVERGING PALETTES  (centered magnitude)
# ──────────────────────────────────────────────

DIVERGING: dict[str, list[str]] = {

    "coolwarm":   _div("#3B4CC0", "#B40426", 9),
    "spectral":   _div("#5E4FA2", "#F46D43", 9),
    "seismic":    _div("#3B4CC0", "#B40426", 9),
    "bwr":        _div("#0000FF", "#FF0000", 9),
    "RdBu":       _div("#67000D", "#053061", 9),
    "RdYlGn":     _div("#A50026", "#006837", 9),
    "RdGy":       _div("#67000D", "#5A5A5A", 9),
    "PiYG":       _div("#6A006A", "#006A00", 9),

    # Custom diverging
    "nature_div": _div("#2166AC", "#B2182B", 9),
    "earth_div":  _div("#2C5530", "#D6604D", 9),
}

# ──────────────────────────────────────────────
#  ACCENT PALETTES  (highlight one series)
# ──────────────────────────────────────────────

# Use the NEUTRAL color for background series and ACCENT for highlight
NEUTRAL = "#D3D3D3"
ACCENT  = "#E63946"

# ──────────────────────────────────────────────
#  THEME-SPECIFIC PALETTES  (per analysis type)
# ──────────────────────────────────────────────

# These define the "go-to" color sequence for a given analysis type.
# Keys match common math-modeling scenarios.

THEME: dict[str, list[str]] = {

    "data_analysis": [
        "#2E86AB", "#A23B72", "#F18F01", "#C73E1D",
        "#3B1F2B", "#44BBA4", "#E94F37", "#84BC92",
    ],

    "optimization": [
        "#003f5c", "#4472c4", "#e69f00", "#cc79a7",
        "#56b4e9", "#f0e442", "#d55e00", "#999999",
    ],

    "time_series": [
        "#0077B6", "#00B4D8", "#90E0EF", "#48CAE4",
        "#023E8A", "#CAF0F8", "#0096C7", "#ADE8F4",
    ],

    "comparison": [
        "#E63946", "#457B9D", "#1D3557", "#A8DADC",
        "#F1FAEE", "#2A9D8F", "#E9C46A", "#F4A261",
    ],

    "classification": [
        "#2E86AB", "#A23B72", "#F18F01", "#C73E1D",
        "#3B1F2B", "#44BBA4", "#E94F37", "#84BC92",
    ],

    "regression": [
        "#0077B6", "#00B4D8", "#90E0EF", "#FF6B6B",
        "#FFA07A", "#FFD93D", "#6BCB77", "#4D96FF",
    ],

    "optimization_multi": [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
        "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    ],

    "clustering": [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
        "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
        "#6C5CE7", "#FDCB6E", "#E17055", "#00B894",
    ],

    "sensitivity": [
        "#03045E", "#0077B6", "#00B4D8", "#90E0EF",
        "#48CAE4", "#CAF0F8", "#0096C7", "#ADE8F4",
    ],

    "decision": [
        "#2D6A4F", "#52B788", "#74C69D", "#B7E4C7",
        "#D8F3DC", "#1B4332", "#40916C", "#95D5B2",
    ],

    "network": [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
        "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
        "#6C5CE7", "#FDCB6E",
    ],

    "dark_mode": [
        "#00F5D4", "#F15BB5", "#FEE440", "#9B5DE5",
        "#00BBF9", "#FF6B6B", "#4ECDC4", "#45B7D1",
    ],
}


def get_palette(name: str, family: str | None = None) -> list[str]:
    """
    Return a full palette by name.

    Parameters
    ----------
    name : str
        Palette key (e.g. 'nature_qual', 'viridis', 'coolwarm').
    family : str, optional
        Which family to search. Auto-detected if None.
        One of: 'qualitative', 'sequential', 'diverging', 'theme'.

    Returns
    -------
    list[str]
        Hex color strings.
    """
    families = {
        "qualitative": QUALITATIVE,
        "sequential": SEQUENTIAL,
        "diverging": DIVERGING,
        "theme": THEME,
    }
    if family:
        pool = families.get(family.lower(), {})
    else:
        pool = {**QUALITATIVE, **SEQUENTIAL, **DIVERGING, **THEME}

    if name not in pool:
        available = sorted(pool.keys())
        raise ValueError(
            f"Unknown palette '{name}'. Available: {available[:15]}…"
        )
    return list(pool[name])


def get_color(name: str, index: int = 0, family: str | None = None) -> str:
    """Return a single hex color at *index* from palette *name*."""
    pal = get_palette(name, family)
    return pal[index % len(pal)]


def auto_colors(
    n: int,
    palette: str = "nature_qual",
    family: str | None = None,
    skip: int = 0,
) -> list[str]:
    """
    Auto-generate *n* colors from a palette, cycling if needed.

    Parameters
    ----------
    n : int
        Number of colors required.
    palette : str
        Palette name.
    family : str, optional
        Palette family. Auto-detected if None.
    skip : int
        Skip the first *skip* colors (useful when you want to start
        after a default gray).

    Returns
    -------
    list[str]
        List of *n* hex color strings.
    """
    pal = get_palette(palette, family)
    pal = pal[skip:]
    out: list[str] = []
    while len(out) < n:
        out.extend(pal)
    return out[:n]


def sequential_colormap(
    name: str = "viridis",
    n: int = 256,
) -> list[str]:
    """
    Build a smooth sequential colormap from a palette.

    Parameters
    ----------
    name : str
        Sequential palette key (e.g. 'viridis', 'blues').
    n : int
        Number of discrete colors in the returned list.

    Returns
    -------
    list[str]
        *n* interpolated hex colors.
    """
    pal = get_palette(name, "sequential")
    start_rgb = _hex_to_rgb(pal[0])
    end_rgb = _hex_to_rgb(pal[-1])
    return [
        _rgb_to_hex(tuple(
            int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * k / (n - 1))
            for i in range(3)
        ))
        for k in range(n)
    ]


def diverging_colormap(
    name: str = "coolwarm",
    n: int = 256,
) -> list[str]:
    """Build a smooth diverging colormap."""
    pal = get_palette(name, "diverging")
    start_rgb = _hex_to_rgb(pal[0])
    end_rgb = _hex_to_rgb(pal[-1])
    return [
        _rgb_to_hex(tuple(
            int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * k / (n - 1))
            for i in range(3)
        ))
        for k in range(n)
    ]


def blend(c1: str, c2: str, t: float = 0.5) -> str:
    """Blend two hex colors. *t* ∈ [0, 1] — 0 = c1, 1 = c2."""
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex((
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    ))


def lightness(c: str, delta: float = 0.3) -> str:
    """Lighten (delta>0) or darken (delta<0) a color.

    Parameters
    ----------
    c : str
        Hex color.
    delta : float
        Amount to shift lightness in HSL space. Range -1.0 (black) to 1.0 (white).
    """
    h, l, s = colorsys.rgb_to_hls(*_hex_to_rgb(c))
    l = max(0.0, min(1.0, l + delta))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return _rgb_to_hex((int(r * 255), int(g * 255), int(b * 255)))


def is_dark(c: str) -> bool:
    """Return True if the color is dark (perceived luminance < 50%)."""
    r, g, b = _hex_to_rgb(c)
    return 0.299 * r + 0.587 * g + 0.114 * b < 128


def contrast_color(c: str) -> str:
    """Return black or white — whichever contrasts more with *c*."""
    return "#FFFFFF" if is_dark(c) else "#1A1A1A"


# ──────────────────────────────────────────────
#  PALETTE  REGISTRY  (for discoverability)
# ──────────────────────────────────────────────

ALL_PALETTES: dict[str, dict] = {
    "qualitative": QUALITATIVE,
    "sequential": SEQUENTIAL,
    "diverging": DIVERGING,
    "theme": THEME,
}

__all__ = [
    "QUALITATIVE", "SEQUENTIAL", "DIVERGING", "THEME",
    "ALL_PALETTES", "NEUTRAL", "ACCENT",
    "get_palette", "get_color", "auto_colors",
    "sequential_colormap", "diverging_colormap",
    "blend", "lightness", "is_dark", "contrast_color",
]