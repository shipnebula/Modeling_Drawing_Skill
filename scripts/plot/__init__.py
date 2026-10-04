"""
plot — Math Modeling Viz: Nature-level publication quality plots.

Import everything in one line:
    from plot import *

Chart functions are loaded lazily (PEP 562): `import plot` is fast,
and each chart module is imported on first attribute access.

Modules:
    palette      — Color palettes (Nature, colorblind-safe, sequential, diverging)
    styles       — Style presets (nature, publication, dark, poster)
    utils        — Helper utilities (figure setup, saving, annotations)
    basic        — Basic statistical charts (bar, line, scatter, pie, etc.)
    model        — Model analysis charts (fit curve, confusion matrix, ROC, etc.)
    advanced     — Advanced charts (network, Sankey, radar, treemap, etc.)
    infographic  — Infographic charts (dashboard, KPI, gauge, mind map, etc.)
    sciences     — Scientific charts (3D surface, contour, vector field, phase)
    calculus     — Calculus charts (integral, Riemann sum, tangent, interpolation)
    chordchart   — Chord diagram for flow matrices
    (plus: .mmvrc.json user config auto-loaded at import)
    statistics   — Statistical charts (Q-Q, ECDF, ridgeline, dendrogram, etc.)
    dynamics     — Iterative maps & simulation (bifurcation, cobweb, Monte-Carlo)
    timeseries   — Time-series diagnostics (ACF/PACF, seasonal decomposition)
    compose      — Multi-panel composite figures with (a)(b)(c) labels
    showcase     — Palette/style previews, colorblind check, GIF export, themes
"""

from __future__ import annotations

import os as _os
import sys as _sys


def _select_backend() -> None:
    """Auto-select the Agg backend on headless systems (servers/CI)."""
    if _os.environ.get("MPLBACKEND"):
        return
    headless = (
        (_sys.platform.startswith("linux") and not _os.environ.get("DISPLAY")
         and not _os.environ.get("WAYLAND_DISPLAY"))
        or _os.environ.get("CI") == "true"
        or _os.environ.get("GITHUB_ACTIONS") == "true"
    )
    if headless:
        try:
            import matplotlib as _mpl
            _mpl.use("Agg", force=False)
        except Exception:
            pass


_select_backend()

from .palette import (
    QUALITATIVE, SEQUENTIAL, DIVERGING, THEME, ALL_PALETTES,
    NEUTRAL, ACCENT,
    get_palette, get_color, auto_colors,
    sequential_colormap, diverging_colormap,
    blend, lightness, is_dark, contrast_color,
)

from .styles import (
    get_style_config, get_color_theme,
    apply_style, apply_style_to_axes, list_styles,
    COLOR_THEMES, style, setup_cjk, detect_cjk_fonts, use_latex,
    apply_theme, list_themes, THEMES, load_config,
)

from .utils import (
    FIGSIZE,
    setup_figure, figsubplots, save_figure, export_publication, pdf_report,
    format_numbers,
    axis_config, add_grid,
    add_annotation, add_data_labels,
    auto_palette,
    format_ticks,
    auto_layout,
    add_figure_title,
    add_source_note,
)

from .compose import panel_figure, render_spec, render_specs

from .showcase import (palette_preview, style_preview, save_gif, make_gif,
                       cvd_preview, colorblind_safe)

from .factory import (
    plot,
    FigureFactory,
    list_chart_types,
)

# project-local user defaults (.mmvrc.json) — silent if absent
try:
    load_config()
except Exception:
    pass

__version__ = "10.0.0"

# ──────────────────────────────────────────────
#  PEP 562 LAZY CHART LOADING
#  Chart modules are imported on first attribute access, so
#  `import plot` costs only palette+styles+factory (~0.3 s).
# ──────────────────────────────────────────────

_LAZY_MAP: dict[str, tuple[str, str]] = {}
for _mod, _names in {
    "basic": [
        "bar_chart", "grouped_bar", "stacked_bar", "line_chart",
        "area_chart", "scatter_plot", "pie_chart", "donut_chart",
        "histogram", "box_plot", "violin_plot", "step_chart",
        "split_violin",
    ],
    "model": [
        "fit_curve", "residual_plot", "confusion_matrix", "roc_curve",
        "learning_curve", "sensitivity_analysis", "pareto_front", "validation_plot",
        "feature_importance", "clustering_2d", "decision_boundary", "correlation_matrix",
        "pr_curve", "prediction_vs_actual", "regression_panel", "elbow_plot",
        "silhouette_plot", "scree_plot",
        "fit_comparison", "roc_comparison", "calibration_curve", "gain_chart",
        "tree_plot",
    ],
    "advanced": [
        "network_graph", "sankey_diagram", "radar_chart", "waterfall_chart",
        "dumbbell_plot", "slope_chart", "timeline", "parallel_coordinates",
        "gantt_chart", "treemap", "ahp_hierarchy", "clustermap",
        "correlation_network",
    "circle_pack", "arc_diagram",
    ],
    "infographic": [
        "dashboard", "kpi_card", "bullet_chart", "sparkline",
        "gauge", "process_flow", "mind_map", "comparison_bar", "donut_rings",
        "risk_matrix",
    ],
    "sciences": [
        "surface3d", "contour_plot", "vector_field", "phase_portrait",
        "twin_axis", "errorband", "heatmap", "optimization_trace",
        "polar_chart", "loglog_plot", "scatter3d", "polar_bar", "ternary_plot",
        "curve_sweep", "phase_field",
    ],
    "statistics": [
        "qq_plot", "ecdf_plot", "ridgeline", "hexbin_plot",
        "stem_plot", "errorbar_chart", "bubble_chart", "bump_chart",
        "stream_graph", "funnel_chart", "waffle_chart", "population_pyramid",
        "sunburst_chart", "icicle_chart", "mosaic_plot", "dendrogram",
        "distribution_panel", "scatter_matrix", "hypothesis_test", "lorenz_curve",
        "biplot", "ks_test", "range_plot", "calendar_heatmap", "grouped_scatter",
        "bland_altman",
        "forecast",
        "joint_plot", "forest_plot", "strip_plot", "smooth_plot",
        "scatter_contour", "diverging_bar", "pareto_chart",
        "dot_plot", "volcano_plot", "confidence_ellipse",
        "stacked_histogram",
        "beeswarm", "control_chart", "candlestick", "delta_band",
        "raincloud",
    ],
    "calculus": [
        "area_under_curve", "riemann_sum", "tangent_line", "interpolation_comparison",
    ],
    "dynamics": [
        "bifurcation", "cobweb", "monte_carlo_convergence",
    ],
    "timeseries": [
        "acf_pacf", "seasonal_decomposition", "cross_correlation",
    ],
    "chordchart": [
        "chord_chart",
    ],
    "showcase": [
        "palette_preview", "style_preview", "save_gif", "cvd_preview",
        "colorblind_safe",
    ],
}.items():
    for _name in _names:
        _LAZY_MAP[_name] = (_mod, _name)


def __getattr__(name: str):
    """Load chart functions from their modules on first access."""
    entry = _LAZY_MAP.get(name)
    if entry is None:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        )
    module_name, attr = entry
    from importlib import import_module
    value = getattr(import_module(f".{module_name}", __name__), attr)
    globals()[name] = value  # cache for next time
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_MAP))


__all__ = [
    # Palette
    "QUALITATIVE", "SEQUENTIAL", "DIVERGING", "THEME", "ALL_PALETTES",
    "NEUTRAL", "ACCENT",
    "get_palette", "get_color", "auto_colors",
    "sequential_colormap", "diverging_colormap",
    "blend", "lightness", "is_dark", "contrast_color",

    # Styles
    "get_style_config", "get_color_theme",
    "apply_style", "apply_style_to_axes", "list_styles",
    "COLOR_THEMES", "style", "setup_cjk", "detect_cjk_fonts",

    # Utils
    "FIGSIZE",
    "setup_figure", "figsubplots", "save_figure", "export_publication",
    "pdf_report",
    "format_numbers",
    "axis_config", "add_grid",
    "add_annotation", "add_data_labels",
    "auto_palette",
    "format_ticks",
    "auto_layout",
    "add_figure_title", "add_source_note",

    # Basic charts
    "bar_chart", "grouped_bar", "stacked_bar",
    "line_chart", "area_chart", "scatter_plot",
    "pie_chart", "donut_chart",
    "histogram", "box_plot", "violin_plot",
    "step_chart",

    # Model charts
    "fit_curve", "residual_plot", "confusion_matrix",
    "roc_curve", "learning_curve", "sensitivity_analysis",
    "pareto_front", "validation_plot", "feature_importance",
    "clustering_2d", "decision_boundary", "correlation_matrix",

    # Advanced charts
    "network_graph", "sankey_diagram", "radar_chart",
    "waterfall_chart", "dumbbell_plot", "slope_chart",
    "timeline", "parallel_coordinates", "gantt_chart", "treemap",
    "ahp_hierarchy",

    # Infographic charts
    "dashboard", "kpi_card", "bullet_chart",
    "sparkline", "gauge", "process_flow",
    "mind_map", "comparison_bar",

    # Scientific charts
    "surface3d", "contour_plot", "vector_field", "phase_portrait",
    "twin_axis", "errorband", "heatmap", "optimization_trace",
    "polar_chart", "loglog_plot", "scatter3d",

    # Calculus charts
    "area_under_curve", "riemann_sum", "tangent_line",
    "interpolation_comparison",

    # Statistical charts
    "qq_plot", "ecdf_plot", "ridgeline", "hexbin_plot", "stem_plot",
    "errorbar_chart", "bubble_chart", "bump_chart", "stream_graph",
    "funnel_chart", "waffle_chart", "population_pyramid",
    "sunburst_chart", "icicle_chart", "mosaic_plot", "dendrogram",
    "distribution_panel", "scatter_matrix",
    "hypothesis_test", "lorenz_curve", "forecast",

    # ML model selection (model.py v3)
    "pr_curve", "prediction_vs_actual", "regression_panel",
    "elbow_plot", "silhouette_plot", "scree_plot",

    # Showcase, animation & accessibility
    "palette_preview", "style_preview", "save_gif",
    "cvd_preview", "colorblind_safe",

    # Model comparison & evaluation (v5)
    "fit_comparison", "roc_comparison", "calibration_curve",
    "gain_chart", "tree_plot",

    # Statistical v5
    "biplot", "ks_test", "range_plot", "calendar_heatmap",
    "grouped_scatter", "bland_altman",

    # Declarative rendering (v5)
    "render_spec", "render_specs",
    "use_latex", "apply_theme", "list_themes", "make_gif", "pdf_report",
    "joint_plot", "forest_plot", "strip_plot", "smooth_plot",
    "scatter_contour", "diverging_bar", "pareto_chart",
    "cross_correlation", "ternary_plot", "donut_rings", "chord_chart",

    # Comparison & risk (v7)
    "dot_plot", "volcano_plot", "confidence_ellipse",
    "stacked_histogram", "curve_sweep", "phase_field",
    "split_violin", "risk_matrix",

    # Distribution & structure (v10)
    "raincloud", "circle_pack", "arc_diagram", "load_config",

    # Dynamics & simulation (v4)
    "bifurcation", "cobweb", "monte_carlo_convergence",

    # Time-series diagnostics (v4)
    "acf_pacf", "seasonal_decomposition",

    # Advanced v4
    "clustermap", "correlation_network", "polar_bar",

    # Composition
    "panel_figure",

    # Factory
    "plot", "FigureFactory", "list_chart_types",
]
