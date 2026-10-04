"""
showcase.py — Meta-charts that showcase the library itself.

Charts:
    palette_preview — grid figure of every palette with swatches
    style_preview   — same chart rendered in every style preset
    save_gif        — stitch a list of figures into an animated GIF

Useful for picking a look, building slides, and showing the library's
range in talks and READMEs.
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .palette import ALL_PALETTES
from .styles import _STYLES


def palette_preview(
    families: Sequence[str] = ("qualitative", "theme"),
    n_swatches: int = 12,
    figsize: tuple | None = None,
    title: str | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    One figure with every palette as a labeled row of color swatches.

    Parameters
    ----------
    families : sequence of str
        Which palette families to include: 'qualitative', 'theme',
        'sequential', 'diverging'.

    Returns
    -------
    Figure
    """
    rows: list[tuple[str, str, list[str]]] = []
    for fam in families:
        for name, colors in ALL_PALETTES.get(fam, {}).items():
            rows.append((fam, name, list(colors)[:n_swatches]))
    if not rows:
        raise ValueError(f"No palettes found for families {families}.")

    n = len(rows)
    if figsize is None:
        figsize = (max(7.5, n_swatches * 0.52 + 3.2), max(4, n * 0.34 + 0.9))

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    for i, (fam, name, colors) in enumerate(rows):
        y = n - 1 - i
        for j, c in enumerate(colors):
            ax.add_patch(plt.Rectangle((j, y - 0.36), 0.92, 0.72,
                                       facecolor=c, edgecolor="none"))
        ax.text(-0.4, y, name, ha="right", va="center", fontsize=8.5,
                color="#333333", fontweight="bold" if fam == "theme" else "normal")

    ax.set_xlim(-3.6, n_swatches)
    ax.set_ylim(-0.7, n - 0.3)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    if save_path:
        from .utils import save_figure
        save_figure(fig, save_path)
    return fig


def style_preview(
    figsize: tuple | None = None,
    title: str | None = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    The same line+scatter chart rendered in every style preset —
    pick your paper's look at a glance.

    Returns
    -------
    Figure
    """
    names = sorted(_STYLES.keys())
    n = len(names)
    ncols = 2 if n <= 4 else (3 if n <= 9 else 4)
    nrows = int(np.ceil(n / ncols))
    if figsize is None:
        figsize = (ncols * 3.6, nrows * 2.9)

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize)

    rng = np.random.default_rng(11)
    xs = np.linspace(0, 10, 30)
    ys = np.sin(xs) * 2 + rng.normal(0, 0.25, 30)

    for slot, name in enumerate(names, start=1):
        config = _STYLES[name]
        with plt.rc_context(config):
            ax = fig.add_subplot(nrows, ncols, slot)
            ax.plot(xs, np.sin(xs) * 2, lw=1.8, color="#2E86AB")
            ax.scatter(xs, ys, s=10, color="#C73E1D", alpha=0.75, lw=0)
            ax.set_title(name, fontsize=10, fontweight="bold", pad=5,
                         color="#333333")  # figure bg is white
            ax.tick_params(labelsize=7)
    # titles for dark panels need the dark color outside the context too
    for name in names:
        pass

    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    if save_path:
        from .utils import save_figure
        save_figure(fig, save_path)
    return fig



# ──────────────────────────────────────────────
#  COLORBLIND  SIMULATION
# ──────────────────────────────────────────────

# Machado et al. (2009) severity-1.0 linear-RGB transforms
_CVD_MATRICES = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def _simulate_cvd(hex_color: str, kind: str) -> str:
    from .palette import _hex_to_rgb, _rgb_to_hex
    m = _CVD_MATRICES[kind]
    r, g, b = _hex_to_rgb(hex_color)
    nr = m[0][0] * r + m[0][1] * g + m[0][2] * b
    ng = m[1][0] * r + m[1][1] * g + m[1][2] * b
    nb = m[2][0] * r + m[2][1] * g + m[2][2] * b
    clip = lambda v: int(min(255, max(0, v)))
    return _rgb_to_hex((clip(nr), clip(ng), clip(nb)))


def cvd_preview(
    palette: str = "nature_qual",
    families: str | None = None,
    n_swatches: int = 8,
    title: str | None = None,
    figsize: tuple = (8.5, 5),
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Render a palette next to protanopia / deuteranopia / tritanopia
    simulations — verify at a glance that your figures are readable
    for colorblind reviewers (5-8% of male readers).

    Returns
    -------
    Figure
    """
    from .palette import get_palette

    colors = get_palette(palette, families)[:n_swatches]
    rows = [("Original", list(colors))] + [
        (kind.title(), [_simulate_cvd(c, kind) for c in colors])
        for kind in _CVD_MATRICES
    ]

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    n = len(rows)
    for i, (label, row) in enumerate(rows):
        y = n - 1 - i
        for j, c in enumerate(row):
            ax.add_patch(plt.Rectangle((j, y - 0.4), 0.92, 0.8,
                                       facecolor=c, edgecolor="none"))
        ax.text(-0.35, y, label, ha="right", va="center", fontsize=10,
                color="#333333",
                fontweight="bold" if i == 0 else "normal")
    ax.set_xlim(-3.2, len(colors))
    ax.set_ylim(-0.7, n - 0.3)
    ax.axis("off")
    ax.set_title(title or f"Colorblind simulation — '{palette}'",
                 fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    if save_path:
        from .utils import save_figure
        save_figure(fig, save_path)
    return fig


def colorblind_safe(
    palette: str = "nature_qual",
    families: str | None = None,
    kinds: Sequence[str] = ("protanopia", "deuteranopia"),
    min_separation: float = 0.04,
    n_check: int = 8,
) -> dict:
    """
    Quantitative colorblind check: simulate the palette, then measure
    the smallest pairwise RGB distance between adjacent colors.

    Returns
    -------
    dict
        ``{'safe': bool, 'min_distance': float, 'closest_pair': (i, j),
        'distances': {kind: value}}`` — safe when every simulated
        distance exceeds ``min_separation``.
    """
    from .palette import get_palette, _hex_to_rgb

    colors = get_palette(palette, families)[:n_check]
    report: dict = {"safe": True, "min_distance": 1.0,
                    "closest_pair": None, "distances": {}}
    for kind in kinds:
        sim = [_hex_to_rgb(_simulate_cvd(c, kind)) for c in colors]
        dmin, pair = 1e9, None
        for i in range(len(sim)):
            for j in range(i + 1, len(sim)):
                d = np.linalg.norm(
                    (np.array(sim[i]) - np.array(sim[j])) / 255.0)
                if d < dmin:
                    dmin, pair = float(d), (i, j)
        report["distances"][kind] = dmin
        if dmin < report["min_distance"]:
            report["min_distance"] = dmin
            report["closest_pair"] = pair
        if dmin < min_separation:
            report["safe"] = False
    return report



# ──────────────────────────────────────────────
#  GIF  EXPORT
# ──────────────────────────────────────────────

def make_gif(
    frame_fn,
    n_frames: int = 30,
    filename: str = "animation.gif",
    fps: int = 10,
    dpi: int = 110,
    loop: bool = True,
) -> str:
    """
    Build an animated GIF from a frame-drawing function — the shortcut
    for convergence animations and parameter sweeps.

    Parameters
    ----------
    frame_fn : callable ``(frame_index, n_frames) -> Figure``
        Draws and returns one frame. Figures are closed automatically.
    n_frames : int
        Number of frames.
    fps : int
        Frames per second in the GIF.

    Example
    -------
    >>> make_gif(lambda i, n: plot.line_chart(np.arange(30),
    ...                                       np.sin(np.linspace(0, i / n * 8, 30))),
    ...          n_frames=24, filename="convergence.gif")
    """
    figs = []
    try:
        for i in range(n_frames):
            figs.append(frame_fn(i, n_frames))
    finally:
        out = save_gif(figs, filename, fps=fps, dpi=dpi, close=True)
    return out


def save_gif(
    figures: Sequence[plt.Figure],
    filename: str = "animation.gif",
    fps: int = 8,
    dpi: int = 110,
    loop: int = 0,
    close: bool = True,
) -> str:
    """
    Stitch a list of matplotlib figures into an animated GIF.

    Perfect for convergence animations, parameter sweeps, and
    presentation assets — no extra dependency (Pillow ships with
    matplotlib).

    Parameters
    ----------
    figures : sequence of Figure
        Frames in play order.
    filename : str
        Output path (.gif).
    fps : int
        Frames per second.
    dpi : int
        Render resolution.
    loop : int
        0 = loop forever (default), 1 = play once, n = n loops.

    Returns
    -------
    str
        The output path.
    """
    import io
    import os

    from PIL import Image

    if not figures:
        raise ValueError("figures list is empty — nothing to animate.")

    frames = []
    try:
        for fig in figures:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi,
                        facecolor=fig.get_facecolor(),
                        bbox_inches=None)
            buf.seek(0)
            frames.append(Image.open(buf).convert("RGB").copy())
            buf.close()
    finally:
        if close:
            for fig in figures:
                plt.close(fig)

    os.makedirs(os.path.dirname(os.path.abspath(filename)) or ".", exist_ok=True)
    frames[0].save(
        filename,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=loop,
    )
    return filename


__all__ = [
    "palette_preview",
    "style_preview",
    "save_gif",
    "make_gif",
    "cvd_preview",
    "colorblind_safe",
]
