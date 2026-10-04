"""
compose.py — Multi-panel composite figures.

panel_figure() builds a grid of charts from simple spec dicts, with
automatic (a), (b), (c) panel labels in Nature style — the standard
layout for multi-result figures in competition papers and journals.

Example
-------
>>> fig = panel_figure([
...     {'type': 'bar',  'data': [4, 7, 5], 'labels': ['A', 'B', 'C'],
...      'title': 'Accuracy'},
...     {'type': 'line', 'data': {'M1': [1, 2, 3]}, 'x': [1, 2, 3],
...      'title': 'Convergence'},
...     {'type': 'hist', 'data': [1, 2, 2, 3], 'title': 'Distribution'},
...     {'type': 'pie',  'data': [30, 25, 45], 'title': 'Share'},
... ], ncols=2, panel_labels='letters', suptitle='Overall results')
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt

from .factory import plot as _plot
from .utils import FIGSIZE


def panel_figure(
    charts: Sequence[dict],
    nrows: Optional[int] = None,
    ncols: Optional[int] = None,
    figsize: Optional[tuple] = None,
    panel_labels: str = "letters",
    label_style: str = "nature",
    suptitle: Optional[str] = None,
    title_fontsize: float = 11,
    label_fontsize: float = 13,
    hspace: float = 0.34,
    wspace: float = 0.26,
    save_path: Optional[str] = None,
    **kwargs,
) -> plt.Figure:
    """
    Compose several charts into one labeled multi-panel figure.

    Parameters
    ----------
    charts : list of dict
        Each dict is a ``plot()`` call spec: ``{'type': 'bar', 'data': ...,
        'title': ..., ...}``. Any keyword accepted by the chart function
        can be included. Use ``'xlabel'`` / ``'ylabel'`` as usual; per-panel
        ``figsize`` is ignored (the grid controls size).
    nrows, ncols : int, optional
        Grid shape. Inferred from the number of charts if omitted
        (nearly-square grid).
    figsize : tuple, optional
        Whole-figure size. Defaults to a sensible per-panel size.
    panel_labels : str
        'letters' → (a), (b), (c)…; 'numbers' → 1, 2, 3…;
        'none' → no labels.
    label_style : str
        'nature' places labels at the top-left outside each panel.
    suptitle : str, optional
        Figure-level title.

    Returns
    -------
    matplotlib.figure.Figure
    """
    if not charts:
        raise ValueError("charts list is empty.")
    n = len(charts)
    if nrows is None and ncols is None:
        ncols = np_ceil_sqrt(n)
        nrows = int(-(-n // ncols))  # ceil division
    elif nrows is None:
        nrows = int(-(-n // max(1, ncols or 1)))
    elif ncols is None:
        ncols = int(-(-n // max(1, nrows)))

    if figsize is None:
        figsize = (ncols * 4.4 + 1.2, nrows * 3.4 + 1.0)

    fig = plt.figure(figsize=figsize)
    indices = []
    for i in range(n):
        indices.append(i + 1)

    for i, spec in enumerate(charts):
        spec = dict(spec)
        chart_type = spec.pop("type", None)
        data = spec.pop("data", None)
        extra_args = tuple(spec.pop("args", ()) or ())
        panel_title = spec.pop("title", None)
        spec.pop("figsize", None)
        spec.pop("save_path", None)

        placeholder = fig.add_subplot(nrows, ncols, indices[i])
        inner_kwargs = dict(spec)
        inner_kwargs.setdefault("title", None)
        ax = _plot_into(fig, placeholder, chart_type, data, extra_args,
                        inner_kwargs, nrows=nrows, ncols=ncols,
                        index=indices[i])
        if ax is not placeholder:
            placeholder.remove()  # chart replaced it (e.g. polar projection)

        if panel_title:
            ax.set_title(panel_title, fontsize=title_fontsize,
                         fontweight="bold", pad=8)

        if panel_labels != "none":
            if panel_labels == "numbers":
                label = f"{i + 1}"
            else:
                label = f"({_letters(i)})"
            if label_style == "nature":
                ax.text(
                    -0.08, 1.06, label, transform=ax.transAxes,
                    fontsize=label_fontsize, fontweight="bold",
                    va="bottom", ha="right", color="#1A1A1A",
                )
            else:
                ax.set_title(f"{label} {panel_title or ''}".strip(),
                             fontsize=title_fontsize, fontweight="bold")

    if suptitle:
        fig.suptitle(suptitle, fontsize=13.5, fontweight="bold", y=0.995)
        fig.subplots_adjust(top=0.87, hspace=hspace, wspace=wspace)
    else:
        fig.subplots_adjust(hspace=hspace, wspace=wspace)
    if save_path:
        from .utils import save_figure
        save_figure(fig, save_path)
    return fig


def _letters(i: int) -> str:
    """0 → a, 25 → z, 26 → aa (Nature-style panel ids)."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(97 + r) + s
    return s


def np_ceil_sqrt(n: int) -> int:
    import math
    return max(1, int(math.ceil(math.sqrt(n))))


def _plot_into(fig, ax, chart_type, data, extra_args, kwargs,
               nrows=1, ncols=1, index=1):
    """Render one chart spec into an existing axes.

    Reuses plot()'s routing by monkeypatching plt.subplots for the
    duration of the call — the standard trick used by seaborn. Charts
    that request their own axes (polar, 3-D projections) get a fresh
    subplot in the same grid position.
    """
    import matplotlib.pyplot as plt

    orig_subplots = plt.subplots

    used = [ax]

    def fake_subplots(*a, **kw):
        kw.pop("figsize", None)
        subplot_kw = kw.pop("subplot_kw", None) or {}
        if subplot_kw:
            used[0] = fig.add_subplot(nrows, ncols, index, **subplot_kw)
        return fig, used[0]

    plt.subplots = fake_subplots
    try:
        _plot(data, *extra_args, type=chart_type, **kwargs)
        return used[0]
    finally:
        plt.subplots = orig_subplots




# ──────────────────────────────────────────────
#  DECLARATIVE  RENDERING  (dict / JSON recipes)
# ──────────────────────────────────────────────

def render_spec(spec: dict) -> plt.Figure:
    """
    Render one figure from a declarative dict recipe (JSON-safe).

    Two shapes are accepted:

    1. Single chart: ``{"type": "bar", "data": [...], "title": ...}``
    2. Multi-panel:  ``{"panel": [spec1, spec2, ...], "ncols": 2,
       "suptitle": ...}`` (panel specs, see :func:`panel_figure`)

    This is the machine-friendly entry point: an LLM or config file
    can drive every chart in the library through it.

    >>> render_spec({"type": "line", "data": {"A": [1, 2]}, "x": [1, 2]})
    """
    if not isinstance(spec, dict):
        raise TypeError(f"spec must be a dict, got {type(spec).__name__}.")
    if "panel" in spec:
        charts = spec["panel"]
        kwargs = {k: v for k, v in spec.items()
                  if k not in ("panel",)}
        return panel_figure(charts, **kwargs)
    spec = dict(spec)
    chart_type = spec.pop("type", None)
    data = spec.pop("data", None)
    extra_args = tuple(spec.pop("args", ()) or ())
    return _plot(data, *extra_args, type=chart_type, **spec)


def render_specs(specs, close: bool = False):
    """Render a list of specs; returns the list of Figures."""
    return [render_spec(sp) for sp in specs]


__all__ = ["panel_figure", "render_spec", "render_specs"]
