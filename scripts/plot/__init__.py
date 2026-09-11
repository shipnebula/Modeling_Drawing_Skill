"""
plot — Math Modeling Viz: Nature-level publication quality plots.

Import everything in one line:
    from plot import *

Modules:
    palette      — Color palettes (Nature, colorblind-safe, sequential, diverging)
    styles       — Style presets (nature, publication, dark, poster)
    utils        — Helper utilities (figure setup, saving, annotations)
    basic        — Basic statistical charts (bar, line, scatter, pie, etc.)
    model        — Model analysis charts (fit curve, confusion matrix, ROC, etc.)
    advanced     — Advanced charts (network, Sankey, radar, treemap, etc.)
    infographic  — Infographic charts (dashboard, KPI, gauge, mind map, etc.)
"""

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
    COLOR_THEMES,
)

from .utils import (
    FIGSIZE,
    setup_figure, figsubplots, save_figure,
    format_numbers,
    axis_config, add_grid,
    add_annotation, add_data_labels,
    auto_palette,
    format_ticks,
    auto_layout,
    add_figure_title,
    add_source_note,
)

from .basic import (
    bar_chart, grouped_bar, stacked_bar,
    line_chart, area_chart, scatter_plot,
    pie_chart, donut_chart,
    histogram, box_plot, violin_plot,
    step_chart,
)

from .model import (
    fit_curve, residual_plot, confusion_matrix,
    roc_curve, learning_curve, sensitivity_analysis,
    pareto_front, validation_plot, feature_importance,
    clustering_2d, decision_boundary, correlation_matrix,
)

from .advanced import (
    network_graph, sankey_diagram, radar_chart,
    waterfall_chart, dumbbell_plot, slope_chart,
    timeline, parallel_coordinates, gantt_chart, treemap,
)

from .infographic import (
    dashboard, kpi_card, bullet_chart,
    sparkline, gauge, process_flow,
    mind_map, comparison_bar,
)

from .factory import (
    plot,
    FigureFactory,
    list_chart_types,
)

__version__ = "1.1.0"

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
    "COLOR_THEMES",

    # Utils
    "FIGSIZE",
    "setup_figure", "figsubplots", "save_figure",
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

    # Infographic charts
    "dashboard", "kpi_card", "bullet_chart",
    "sparkline", "gauge", "process_flow",
    "mind_map", "comparison_bar",

    # Factory
    "plot", "FigureFactory", "list_chart_types",
]