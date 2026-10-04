"""
plot/factory.py — Universal plot() function and FigureFactory class.

The single entry point for everything. One function call, auto-detection,
batch generation, zero boilerplate.
"""
from __future__ import annotations

import difflib
import inspect
import os
from functools import lru_cache
import numpy as np
from typing import Any, Optional, Sequence, Union

import matplotlib.pyplot as plt

from .palette import get_palette, auto_colors
from .styles import apply_style, list_styles
from .utils import setup_figure, save_figure, figsubplots

# Chart function registry: type name -> function
CHART_REGISTRY: dict[str, callable] = {}


def _register(module):
    """Register all chart functions from a module."""
    for name in dir(module):
        if name.startswith('_'):
            continue
        obj = getattr(module, name)
        if callable(obj) and hasattr(obj, '__module__') and obj.__module__ == module.__name__:
            CHART_REGISTRY[name] = obj


def _register_all():
    """Register all chart modules."""
    from . import (basic, model, advanced, infographic, sciences,
                   statistics, calculus, showcase, dynamics, timeseries,
                   chordchart)
    for mod in (basic, model, advanced, infographic, sciences,
                statistics, calculus, showcase, dynamics, timeseries,
                chordchart):
        _register(mod)


# Lazy registration
_registered = False


def _ensure_registered():
    global _registered
    if not _registered:
        _register_all()
        _registered = True


# ──────────────────────────────────────────────
#  CHART TYPE ALIASES
# ──────────────────────────────────────────────

_ALIASES = {
    'bar': 'bar_chart',
    'grouped': 'grouped_bar',
    'stacked': 'stacked_bar',
    'line': 'line_chart',
    'area': 'area_chart',
    'scatter': 'scatter_plot',
    'pie': 'pie_chart',
    'donut': 'donut_chart',
    'hist': 'histogram',
    'histogram': 'histogram',
    'box': 'box_plot',
    'boxplot': 'box_plot',
    'violin': 'violin_plot',
    'step': 'step_chart',
    'fit': 'fit_curve',
    'regression': 'fit_curve',
    'residual': 'residual_plot',
    'confusion': 'confusion_matrix',
    'heatmap': 'confusion_matrix',
    'roc': 'roc_curve',
    'learning': 'learning_curve',
    'tornado': 'sensitivity_analysis',
    'sensitivity': 'sensitivity_analysis',
    'pareto': 'pareto_front',
    'validation': 'validation_plot',
    'importance': 'feature_importance',
    'cluster': 'clustering_2d',
    'decision': 'decision_boundary',
    'correlation': 'correlation_matrix',
    'corr': 'correlation_matrix',
    'network': 'network_graph',
    'graph': 'network_graph',
    'sankey': 'sankey_diagram',
    'radar': 'radar_chart',
    'waterfall': 'waterfall_chart',
    'dumbbell': 'dumbbell_plot',
    'slope': 'slope_chart',
    'timeline': 'timeline',
    'parallel': 'parallel_coordinates',
    'gantt': 'gantt_chart',
    'treemap': 'treemap',
    'dashboard': 'dashboard',
    'kpi': 'kpi_card',
    'bullet': 'bullet_chart',
    'spark': 'sparkline',
    'sparkline': 'sparkline',
    'gauge': 'gauge',
    'flow': 'process_flow',
    'process': 'process_flow',
    'mind': 'mind_map',
    'mindmap': 'mind_map',
    'compare': 'comparison_bar',

    # ── sciences.py (math-modeling / scientific computing) ──
    'surface': 'surface3d',
    'surface_plot': 'surface3d',
    'surf': 'surface3d',
    '3d': 'surface3d',
    'contour': 'contour_plot',
    'contours': 'contour_plot',
    'quiver': 'vector_field',
    'vector': 'vector_field',
    'streamplot': 'vector_field',
    'streamlines': 'vector_field',
    'phase': 'phase_portrait',
    'orbit': 'phase_portrait',
    'twin': 'twin_axis',
    'dual_axis': 'twin_axis',
    'dual': 'twin_axis',
    'second_axis': 'twin_axis',
    'band': 'errorband',
    'confidence': 'errorband',
    'confidence_band': 'errorband',
    'uncertainty': 'errorband',
    'trace': 'optimization_trace',
    'descent': 'optimization_trace',
    'gradient_descent': 'optimization_trace',
    'optimizer_path': 'optimization_trace',
    'polar': 'polar_chart',
    'windrose': 'polar_chart',
    'wind_rose': 'polar_chart',
    'log': 'loglog_plot',
    'loglog': 'loglog_plot',
    'loglog_chart': 'loglog_plot',
    'power_law': 'loglog_plot',
    'convergence': 'loglog_plot',

    # ── statistics.py ──
    'qq': 'qq_plot',
    'quantile': 'qq_plot',
    'ecdf': 'ecdf_plot',
    'cdf': 'ecdf_plot',
    'ridge': 'ridgeline',
    'joyplot': 'ridgeline',
    'joy_plot': 'ridgeline',
    'hexbin': 'hexbin_plot',
    'hex': 'hexbin_plot',
    'stem': 'stem_plot',
    'lollipop': 'stem_plot',
    'errorbar': 'errorbar_chart',
    'error_bars': 'errorbar_chart',
    'means': 'errorbar_chart',
    'bubble': 'bubble_chart',
    'bubbles': 'bubble_chart',
    'bump': 'bump_chart',
    'bumpchart': 'bump_chart',
    'rank_change': 'bump_chart',
    'streamgraph': 'stream_graph',
    'stream': 'stream_graph',
    'theme_river': 'stream_graph',
    'funnel': 'funnel_chart',
    'waffle': 'waffle_chart',
    'pictogram': 'waffle_chart',
    'pyramid': 'population_pyramid',
    'population': 'population_pyramid',
    'sunburst': 'sunburst_chart',
    'sun_burst': 'sunburst_chart',
    'icicle': 'icicle_chart',
    'mosaic': 'mosaic_plot',
    'marimekko': 'mosaic_plot',
    'dendrogram': 'dendrogram',
    'hierarchy': 'dendrogram',
    'tree': 'dendrogram',
    'distpanel': 'distribution_panel',
    'dist_panel': 'distribution_panel',
    'distribution': 'distribution_panel',
    'pairs': 'scatter_matrix',
    'pairplot': 'scatter_matrix',
    'pair_plot': 'scatter_matrix',
    'scattermatrix': 'scatter_matrix',

    # ── compose.py ──
    'panel': 'panel_figure',
    'panels': 'panel_figure',
    'multi': 'panel_figure',
    'multipanel': 'panel_figure',
    'multi_panel': 'panel_figure',

    # ── v3 additions ──
    'auc': 'area_under_curve',
    'integral': 'area_under_curve',
    'definite_integral': 'area_under_curve',
    'riemann': 'riemann_sum',
    'riemannsum': 'riemann_sum',
    'numerical_integration': 'riemann_sum',
    'tangent': 'tangent_line',
    'derivative': 'tangent_line',
    'interpolation': 'interpolation_comparison',
    'spline': 'interpolation_comparison',
    'interp': 'interpolation_comparison',
    'scatter3': 'scatter3d',
    'scatter_3d': 'scatter3d',
    '3d_scatter': 'scatter3d',
    'pr': 'pr_curve',
    'precision_recall': 'pr_curve',
    'auprc': 'pr_curve',
    'pred_actual': 'prediction_vs_actual',
    'predicted_vs_actual': 'prediction_vs_actual',
    'y_vs_ypred': 'prediction_vs_actual',
    'regdiag': 'regression_panel',
    'regression_diagnostics': 'regression_panel',
    'lm_diagnostics': 'regression_panel',
    'elbow': 'elbow_plot',
    'k_selection': 'elbow_plot',
    'kmeans_selection': 'elbow_plot',
    'silhouette': 'silhouette_plot',
    'scree': 'scree_plot',
    'pca': 'scree_plot',
    'variance_explained': 'scree_plot',
    'ttest': 'hypothesis_test',
    'ztest': 'hypothesis_test',
    'significance': 'hypothesis_test',
    'gini': 'lorenz_curve',
    'inequality': 'lorenz_curve',
    'prediction': 'forecast',
    'ts_forecast': 'forecast',
    'gm11': 'forecast',
    'arima_plot': 'forecast',
    'ahp': 'ahp_hierarchy',
    'hierarchy_structure': 'ahp_hierarchy',
    'palettes': 'palette_preview',
    'palette_gallery': 'palette_preview',
    'styles_preview': 'style_preview',
    'style_comparison': 'style_preview',

    # ── v4 additions ──
    'bifurcation_diagram': 'bifurcation',
    'logistic_map': 'bifurcation',
    'chaos': 'bifurcation',
    'period_doubling': 'bifurcation',
    'cobwebplot': 'cobweb',
    'cobweb_plot': 'cobweb',
    'iterative_map': 'cobweb',
    'montecarlo': 'monte_carlo_convergence',
    'mc_convergence': 'monte_carlo_convergence',
    'simulation_convergence': 'monte_carlo_convergence',
    'running_mean': 'monte_carlo_convergence',
    'correlogram': 'acf_pacf',
    'acf': 'acf_pacf',
    'pacf': 'acf_pacf',
    'autocorrelation': 'acf_pacf',
    'arima_order': 'acf_pacf',
    'decomposition': 'seasonal_decomposition',
    'stl': 'seasonal_decomposition',
    'seasonality': 'seasonal_decomposition',
    'cluster_heatmap': 'clustermap',
    'clustered_heatmap': 'clustermap',
    'corr_network': 'correlation_network',
    'corrnet': 'correlation_network',
    'polarbar': 'polar_bar',
    'wind_rose_bar': 'polar_bar',
    'radial_bar': 'polar_bar',
    'rose': 'polar_bar',
    'cvd': 'cvd_preview',
    'colorblind': 'cvd_preview',

    # ── v5 additions ──
    'model_comparison': 'fit_comparison',
    'fitcompare': 'fit_comparison',
    'multi_fit': 'fit_comparison',
    'multi_roc': 'roc_comparison',
    'roc_multi': 'roc_comparison',
    'reliability': 'calibration_curve',
    'reliability_diagram': 'calibration_curve',
    'gain': 'gain_chart',
    'lift': 'gain_chart',
    'cumulative_gain': 'gain_chart',
    'decision_tree': 'tree_plot',
    'dtree': 'tree_plot',
    'pca_biplot': 'biplot',
    'loading_plot': 'biplot',
    'kstest': 'ks_test',
    'ks_plot': 'ks_test',
    'ecdf_compare': 'ks_test',
    'scenario': 'range_plot',
    'intervals': 'range_plot',
    'scenario_range': 'range_plot',
    'calendar': 'calendar_heatmap',
    'github_heatmap': 'calendar_heatmap',
    'daily_heatmap': 'calendar_heatmap',
    'segment_scatter': 'grouped_scatter',
    'group_scatter': 'grouped_scatter',
    'agreement': 'bland_altman',
    'method_comparison': 'bland_altman',
    'spec': 'render_spec',

    # ── v6 additions ──
    'jointplot': 'joint_plot',
    'joint': 'joint_plot',
    'marginals': 'joint_plot',
    'forest': 'forest_plot',
    'effect_sizes': 'forest_plot',
    'meta_analysis': 'forest_plot',
    'jitter': 'strip_plot',
    'strip': 'strip_plot',
    'lowess': 'smooth_plot',
    'savgol': 'smooth_plot',
    'smoothing': 'smooth_plot',
    'trend_smooth': 'smooth_plot',
    'density_scatter': 'scatter_contour',
    'kde_scatter': 'scatter_contour',
    'signed_bar': 'diverging_bar',
    'contribution': 'diverging_bar',
    'pareto_chart': 'pareto_chart',
    'vital_few': 'pareto_chart',
    'ccf': 'cross_correlation',
    'lead_lag': 'cross_correlation',
    'xcorr': 'cross_correlation',
    'ternary': 'ternary_plot',
    'mixture': 'ternary_plot',
    'rings': 'donut_rings',
    'progress_rings': 'donut_rings',
    'kpi_rings': 'donut_rings',

    # ── v7 additions ──
    'cleveland': 'dot_plot',
    'dumbplot': 'dot_plot',
    'volcano': 'volcano_plot',
    'fold_change': 'volcano_plot',
    'ellipses': 'confidence_ellipse',
    'ellipse': 'confidence_ellipse',
    'cluster_ellipse': 'confidence_ellipse',
    'stacked_hist': 'stacked_histogram',
    'overlay_hist': 'stacked_histogram',
    'sweep': 'curve_sweep',
    'param_sweep': 'curve_sweep',
    'curve_family': 'curve_sweep',
    'phase_diagram': 'phase_field',
    'ode_field': 'phase_field',
    'half_violin': 'split_violin',
    'splitviolin': 'split_violin',
    'riskmap': 'risk_matrix',
    'probability_impact': 'risk_matrix',
    'chord_diagram': 'chord_chart',
    'chord': 'chord_chart',

    # ── v8 additions ──
    'beeswarm_plot': 'beeswarm',
    'swarm': 'beeswarm',
    'spc': 'control_chart',
    'spc_chart': 'control_chart',
    'ucl': 'control_chart',
    'ohlc': 'candlestick',
    'ohlc_chart': 'candlestick',
    'delta': 'delta_band',
    'difference_band': 'delta_band',
    'scenario_delta': 'delta_band',

    # ── v10 additions ──
    'cloud': 'raincloud',
    'raincloud_plot': 'raincloud',
    'circlepack': 'circle_pack',
    'packed_circles': 'circle_pack',
    'arcgraph': 'arc_diagram',
}


def resolve_chart_type(type_name: str) -> str:
    """Resolve a chart type alias to the canonical function name."""
    _ensure_registered()
    if type_name in CHART_REGISTRY:
        return type_name
    if type_name in _ALIASES:
        return _ALIASES[type_name]
    # Fuzzy match
    lower = type_name.lower().replace('-', '_').replace(' ', '_')
    if lower in CHART_REGISTRY:
        return lower
    for alias, canonical in _ALIASES.items():
        if alias == lower:
            return canonical
    # Suggest close matches before giving up
    candidates = sorted(set(CHART_REGISTRY) | set(_ALIASES))
    matches = difflib.get_close_matches(lower, candidates, n=3, cutoff=0.55)
    hint = f" Did you mean: {', '.join(repr(m) for m in matches)}?" if matches else ""
    raise ValueError(
        f"Unknown chart type '{type_name}'.{hint} "
        f"Use list_chart_types() to see all {len(candidates)} available types."
    )


# ──────────────────────────────────────────────
#  AUTO-DETECTION
# ──────────────────────────────────────────────

def _detect_from_dataframe(data) -> str:
    """Detect best chart type from a pandas DataFrame."""
    try:
        import pandas as pd
        if not isinstance(data, pd.DataFrame):
            return 'line'
    except ImportError:
        return 'line'

    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    non_numeric_cols = data.select_dtypes(exclude='number').columns.tolist()

    # No numeric data at all → count the first categorical column
    if len(numeric_cols) == 0:
        return 'bar'

    # 1 numeric + ≥1 categorical → bar of the numeric column by category
    if len(numeric_cols) == 1:
        return 'bar' if non_numeric_cols else 'line'

    # Wide all-numeric table → correlation matrix
    if not non_numeric_cols and len(numeric_cols) >= 4:
        return 'correlation'

    # Categorical key + several numerics → grouped comparison
    if non_numeric_cols and len(numeric_cols) >= 2:
        return 'grouped'

    # 2-3 numeric columns → multi-series line over the index
    return 'line'


def _detect_from_numpy(data) -> str:
    """Detect best chart type from a numpy array."""
    if not isinstance(data, np.ndarray):
        return 'bar'
    if data.ndim == 2:
        return 'correlation'
    return 'bar'


def _detect_chart_type(
    data,
    labels: Optional[Sequence[str]] = None,
    x: Any = None,
    y: Any = None,
) -> str:
    """Auto-detect the best chart type for given data."""
    # No data provided — check kwargs for hints
    if data is None:
        if x is not None and y is not None:
            return 'scatter'
        # Check for specific kwargs that imply chart type
        # (sensitivity_analysis, dashboard, etc. use kwargs only)
        return 'bar'

    # DataFrame
    try:
        import pandas as pd
        if isinstance(data, pd.DataFrame):
            return _detect_from_dataframe(data)
    except ImportError:
        pass

    # Dict of series
    if isinstance(data, dict):
        if data and all(np.isscalar(v) for v in data.values()):
            return 'bar'          # {'A': 1, 'B': 2} → category:value
        if x is not None:
            return 'line'
        return 'grouped'

    # List of lists/tuples (2D)
    if isinstance(data, (list, tuple)) and len(data) > 0:
        if isinstance(data[0], (list, tuple, np.ndarray)):
            # [(1, 2), (3, 4)] → scatter points; [[...], [...]] → matrix
            if isinstance(data[0], tuple) and len(data[0]) == 2:
                return 'scatter'
            return 'correlation'

    # Scalar list with labels → bar chart
    if isinstance(data, (list, tuple, np.ndarray)):
        if labels is not None and isinstance(labels, (list, tuple, np.ndarray)):
            return 'bar'
        if x is not None and y is not None:
            return 'scatter'
        if x is not None:
            return 'line'
        # Bare list of numbers
        return 'bar'

    # Numpy array
    return _detect_from_numpy(data)


# ──────────────────────────────────────────────
#  UNIVERSAL plot() FUNCTION
# ──────────────────────────────────────────────

@lru_cache(maxsize=None)
def _cached_accepts(fn) -> frozenset:
    try:
        return frozenset(inspect.signature(fn).parameters)
    except (ValueError, TypeError):
        return frozenset()


def _accepts_param(fn, name: str) -> bool:
    """True when the chart function has a parameter called *name*."""
    return name in _cached_accepts(fn)


def plot(
    data=None,
    *args,
    type: Optional[str] = None,
    title: Optional[str] = None,
    labels: Optional[Sequence[str]] = None,
    x: Any = None,
    y: Any = None,
    style: Optional[str] = None,
    palette: Optional[str] = None,
    figsize: Optional[tuple] = None,
    save_path: Optional[str] = None,
    **kwargs,
) -> plt.Figure:
    """
    Universal plotting function — auto-detects the best chart type.

    This is the simplest way to create any chart. Pass your data and it
    figures out what to draw.

    Examples
    --------
    # Bar chart (auto-detected from list + labels)
    fig = plot([10, 20, 30], labels=['A', 'B', 'C'])

    # Line chart with dict of series
    fig = plot({'Model A': [1,2,3], 'Model B': [4,5,6]}, x=[1,2,3])

    # Scatter plot
    fig = plot(x_data, y_data, type='scatter')

    # Pie chart
    fig = plot([30, 25, 20, 15, 10], labels=['A','B','C','D','E'], type='pie')

    # Histogram
    fig = plot(np.random.randn(1000), type='hist')

    # DataFrame (auto-detects best chart)
    fig = plot(df)

    # Force specific chart type
    fig = plot([10, 20, 30], type='bar', labels=['A','B','C'])

    # With custom styling
    fig = plot(data, labels=labels, style='dark', palette='ocean')

    Parameters
    ----------
    data : array-like
        Primary data. Can be a list, dict, numpy array, or DataFrame.
    *args : positional arguments
        Extra arguments passed to the underlying chart function.
    type : str, optional
        Force a specific chart type (e.g. 'bar', 'line', 'scatter').
        If not provided, auto-detected from data structure.
    title : str, optional
        Chart title.
    labels : list of str, optional
        Category labels.
    x : array-like, optional
        X-axis data.
    y : array-like, optional
        Y-axis data.
    style : str, optional
        Style preset name.
    palette : str, optional
        Color palette name.
    figsize : tuple, optional
        Figure size (width, height) in inches.
    save_path : str, optional
        File path to save the figure.
    **kwargs : dict
        Additional keyword arguments passed to the chart function.

    Returns
    -------
    matplotlib.figure.Figure
    """
    _ensure_registered()

    if data is None and not args and x is None and y is None and not kwargs:
        raise ValueError(
            "plot() received no data. Pass data positionally — "
            "plot([1, 2, 3]), plot(df), plot(x, y, type='scatter') — "
            "or see list_chart_types() for everything available."
        )

    # Auto-apply style if specified
    if style:
        apply_style(style)

    # Determine chart type
    if type is None:
        detected = _detect_chart_type(data, labels=labels, x=x, y=y)
        chart_fn_name = resolve_chart_type(detected)
    else:
        chart_fn_name = resolve_chart_type(type)

    chart_fn = CHART_REGISTRY.get(chart_fn_name)
    if chart_fn is None:
        raise ValueError(f"Chart function '{chart_fn_name}' not found in registry.")

    # Build kwargs for the chart function
    chart_kwargs = dict(kwargs)
    if style:
        chart_kwargs.setdefault('style', style)
    if palette:
        chart_kwargs.setdefault('palette', palette)
    if figsize:
        chart_kwargs.setdefault('figsize', figsize)
    if title:
        chart_kwargs.setdefault('title', title)
    # save once here (not inside the chart fn) so the returned figure
    # stays open and reusable after plot(..., save_path=...)
    chart_kwargs.pop('save_path', None)

    # Handle different data patterns
    fig = _call_chart_fn(
        chart_fn, data, args, labels=labels, x=x, y=y,
        **chart_kwargs
    )

    if save_path:
        save_figure(fig, save_path, close=False)

    return fig


def _bar_chart_route(fn, data, labels, kwargs):
    """bar_chart accepts lists, {'cat': value} dicts, and DataFrames."""
    if isinstance(data, dict) and data and all(np.isscalar(v) for v in data.values()):
        kwargs.setdefault("labels", [str(k) for k in data])
        return fn(list(data.values()), **kwargs)
    try:
        import pandas as pd
        if isinstance(data, pd.DataFrame):
            num = data.select_dtypes(include="number")
            non_num = data.select_dtypes(exclude="number")
            if num.shape[1] == 1:
                if labels is None and non_num.shape[1] >= 1:
                    kwargs.setdefault("labels", non_num.iloc[:, 0].astype(str).tolist())
                return fn(num.iloc[:, 0].tolist(), **kwargs)
    except ImportError:
        pass
    return fn(data, **kwargs)


def _resolve_xy_extras(data, args, x, y):
    """Resolve (first, second, extras) from plot()'s flexible arguments.

    Supports three calling conventions for charts of shape
    ``fn(a, b, e1, e2, ...)``:

    1. Positional:  plot(a, b, e1, e2, type='...')
    2. Mixed:       plot(a, y=b, type='...', e1=..., e2=...)
    3. Full kwargs: plot(x=a, y=b, type='...', e1=..., e2=...)
    """
    a = x if x is not None else data
    b = y if y is not None else (args[0] if args else None)
    extras = list(args) if y is not None else list(args[1:])
    return a, b, extras


def _pop_extras(extras: list, names: Sequence[str], kwargs: dict) -> list:
    """Fill missing extras from kwargs under the given names (in order)."""
    while len(extras) < len(names) and names[len(extras)] in kwargs:
        extras.append(kwargs.pop(names[len(extras)]))
    return extras


def _route_mesh(fn, data, args, x, y, kwargs, chart_fn_name):
    """Route mesh charts (surface3d / contour_plot).

    Accepts:  plot(X, Y, Z)  |  plot(x_1d, y_1d, Z)  |  plot(Z)
    """
    if len(args) >= 2:
        return fn(data, args[0], args[1], **kwargs)
    if x is not None and y is not None and data is not None:
        return fn(x, y, data, **kwargs)
    if data is not None:
        return fn(data, **kwargs)
    raise TypeError(
        f"{chart_fn_name} needs X, Y, Z — pass them positionally "
        f"(plot(X, Y, Z, type=...)), as 1-D axes with a 2-D Z "
        f"(plot(x, y, Z, type=...)), or a lone 2-D Z (plot(Z, type=...))."
    )


def _call_chart_fn(
    fn, data, args,
    labels: Optional[Sequence[str]] = None,
    x: Any = None,
    y: Any = None,
    **kwargs,
) -> plt.Figure:
    """Call a chart function with proper argument routing."""
    fn_name = fn.__name__

    # Special routing for functions where data isn't the first positional arg
    routing = {
        # bar_chart — accept {'A': 1} dicts and single-numeric DataFrames
        'bar_chart': lambda: _bar_chart_route(
            fn, data, labels, kwargs),
        # line_chart(x, y_series)
        'line_chart': lambda: fn(x if x is not None else data, data, **kwargs),
        # loglog_plot(x, y_series)
        'loglog_plot': lambda: fn(x if x is not None else data, data, **kwargs)
        if data is not None else fn(**kwargs),
        # scatter_plot(x, y)
        'scatter_plot': lambda: fn(x if x is not None else data, y if y is not None else (args[0] if args else data), **kwargs),
        # residual_plot(x, y_true, y_pred) — x defaults to sample index
        'residual_plot': lambda: (
            fn(data, args[0], args[1], **kwargs) if len(args) >= 2
            else fn(np.arange(len(data)), data, args[0] if args else y, **kwargs)
        ),
        # confusion_matrix(y_true, y_pred)
        'confusion_matrix': lambda: fn(x if x is not None else data, y if y is not None else (args[0] if args else data), **kwargs),
        # roc_curve(y_true, y_score)
        'roc_curve': lambda: fn(x if x is not None else data, y if y is not None else (args[0] if args else data), **kwargs),
        # fit_curve(x, y)
        'fit_curve': lambda: fn(x if x is not None else data, y if y is not None else (args[0] if args else data), **kwargs),
        # learning_curve(train_scores, val_scores)
        'learning_curve': lambda: fn(x if x is not None else data, y if y is not None else (args[0] if args else data), **kwargs),
        # network_graph(nodes, edges)
        'network_graph': lambda: fn(data, y if y is not None else (args[0] if args else None), **kwargs),
        # radar_chart(labels, values, names=None, ...)
        'radar_chart': lambda: fn(data, args[0] if args else data, **kwargs),
        # step_chart(x, y)
        'step_chart': lambda: fn(x if x is not None else data, y if y is not None else (args[0] if args else data), **kwargs),
        # area_chart(x, y_series)
        'area_chart': lambda: fn(x if x is not None else data, data, **kwargs),
        # clustering_2d(X, labels)
        'clustering_2d': lambda: fn(data, labels if labels is not None else y, **kwargs),
        # decision_boundary(X, y, model)
        'decision_boundary': lambda: fn(data, y if y is not None else labels, **kwargs),
        # feature_importance(names, values)
        'feature_importance': lambda: fn(labels if labels is not None else data, data, **kwargs),
        # pareto_front(objectives) or pareto_front(x_values, y_values)
        'pareto_front': lambda: fn(
            x if x is not None else data,
            args[0] if args else (y if y is not None else None), **kwargs),
        # validation_plot(cv_scores)
        'validation_plot': lambda: fn(data, **kwargs),
        # sensitivity_analysis(parameters, low_values, high_values)
        'sensitivity_analysis': lambda: fn(**kwargs),
        # dashboard(metrics)
        'dashboard': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),

        # ── sciences.py ──
        # surface3d / contour_plot — mesh inputs
        'surface3d': lambda: _route_mesh(fn, data, args, x, y, kwargs, fn_name),
        'contour_plot': lambda: _route_mesh(fn, data, args, x, y, kwargs, fn_name),
        # vector_field(x, y, u, v)
        'vector_field': lambda: _vector_field_route(
            fn, data, args, x, y, kwargs),
        # phase_portrait(x, y)
        'phase_portrait': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else None), **kwargs),
        # twin_axis(x, y1, y2)
        'twin_axis': lambda: _xy_route(fn, data, args, x, y, kwargs, ('y2',)),
        # errorband(x, y, lower, upper) or yerr=
        'errorband': lambda: _errorband_route(fn, data, args, x, y, kwargs),
        # optimization_trace(func, path)
        'optimization_trace': lambda: fn(
            data, args[0] if args else y, **kwargs),
        # polar_chart(theta, r)
        'polar_chart': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else data), **kwargs),

        # ── statistics.py ──
        'hexbin_plot': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else data), **kwargs),
        'stem_plot': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else None), **kwargs),
        'errorbar_chart': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('yerr',)),
        'bubble_chart': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('sizes',)),
        'stream_graph': lambda: fn(data, x=x, **kwargs),
        'funnel_chart': lambda: fn(
            data, args[0] if args else y, **kwargs),
        'population_pyramid': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('right',)),

        # ── v3 ──
        # area_under_curve: fn(f) positional, or data-driven plot(x, y, type='auc')
        'area_under_curve': lambda: (
            fn(data, *args, **kwargs) if callable(data)
            else _route_auc_data(fn, data, args, x, y, kwargs)),
        # scatter3d(x, y, z)
        'scatter3d': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('z',)),
        # pr_curve(y_true, y_score)
        'pr_curve': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else data), **kwargs),
        # prediction_vs_actual(y_actual, y_predicted)
        'prediction_vs_actual': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else data), **kwargs),
        # regression_panel(y_actual, y_predicted)
        'regression_panel': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else data), **kwargs),
        # elbow_plot(X)
        'elbow_plot': lambda: fn(data, **kwargs),
        # silhouette_plot(X, labels)
        'silhouette_plot': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('labels',)),
        # scree_plot(data)
        'scree_plot': lambda: fn(data, **kwargs),
        # hypothesis_test(data)
        'hypothesis_test': lambda: fn(data, **kwargs),
        # lorenz_curve(data)
        'lorenz_curve': lambda: fn(data, **kwargs),
        # forecast(history, predicted)
        'forecast': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('predicted',)),
        # ahp_hierarchy(goal, criteria, alternatives)
        'ahp_hierarchy': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('criteria', 'alternatives')),

        # ── v4 ──
        # bifurcation(f, ...) — f first when callable; bare → logistic map
        'bifurcation': lambda: (
            fn(data, **kwargs) if callable(data)
            else fn(**kwargs)),
        # cobweb(f, x0)
        'cobweb': lambda: (
            fn(data, kwargs.pop('x0', args[0] if args else x), **kwargs)
            if callable(data) else fn(**kwargs)),
        # monte_carlo_convergence(samples)
        'monte_carlo_convergence': lambda: fn(data, **kwargs),
        # acf_pacf(series)
        'acf_pacf': lambda: fn(data, **kwargs),
        # seasonal_decomposition(series)
        'seasonal_decomposition': lambda: fn(data, **kwargs),
        # clustermap(matrix)
        'clustermap': lambda: fn(data, **kwargs),
        # correlation_network(matrix_or_data)
        'correlation_network': lambda: fn(data, **kwargs),
        # polar_bar(theta, r)
        'polar_bar': lambda: fn(
            x if x is not None else data,
            y if y is not None else (args[0] if args else data), **kwargs),
        # cvd_preview(palette_name)
        'cvd_preview': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),

        # ── v5 ──
        # fit_comparison(x, y)
        'fit_comparison': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ()),
        # roc_comparison(y_true, scores_dict)
        'roc_comparison': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('scores',)),
        # calibration_curve(y_true, y_prob)
        'calibration_curve': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('y_prob',)),
        # gain_chart(y_true, y_score)
        'gain_chart': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('y_score',)),
        # tree_plot(model_or_X, y)
        'tree_plot': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('y',)),
        # biplot(data)
        'biplot': lambda: fn(data, **kwargs),
        # ks_test(s1, s2)
        'ks_test': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ()),
        # range_plot(labels, low, mid, high)
        'range_plot': lambda: _range_plot_route(
            fn, data, args, x, y, kwargs),
        # calendar_heatmap(values)
        'calendar_heatmap': lambda: fn(data, **kwargs),
        # grouped_scatter(x, y, groups)
        'grouped_scatter': lambda: _grouped_scatter_route(
            fn, data, args, x, y, kwargs),
        # bland_altman(m1, m2)
        'bland_altman': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ()),

        # ── v6 ──
        'joint_plot': lambda: _xy_route(fn, data, args, x, y, kwargs, ()),
        'forest_plot': lambda: _forest_route(fn, data, args, x, y, kwargs),
        'strip_plot': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
        'smooth_plot': lambda: _xy_route(fn, data, args, x, y, kwargs, ()),
        'scatter_contour': lambda: _xy_route(fn, data, args, x, y, kwargs, ()),
        'diverging_bar': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('values',)),
        'pareto_chart': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('counts',)),
        'cross_correlation': lambda: _xy_route(
            fn, data, args, x, y, kwargs, ('series2',)),
        'ternary_plot': lambda: _ternary_route(fn, data, args, x, y, kwargs),
        'donut_rings': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),

        # ── v7 ──
        'dot_plot': lambda: _dot_plot_route(fn, data, args, x, y, kwargs),
        'volcano_plot': lambda: _xy_route(fn, data, args, x, y, kwargs, ('p_values',)),
        'confidence_ellipse': lambda: _xy_route(fn, data, args, x, y, kwargs, ()),
        'stacked_histogram': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
        'curve_sweep': lambda: (
            fn(data, args[0] if args else kwargs.pop('param_values', None), **kwargs)
            if callable(data) else fn(**kwargs)),
        'phase_field': lambda: (
            fn(data, args[0], **kwargs) if callable(data) and len(args) >= 1
            else fn(data, args[0], args[1], **kwargs) if callable(data) and len(args) >= 2
            else fn(**kwargs)),
        'split_violin': lambda: _xy_route(fn, data, args, x, y, kwargs, ('right_data',)),
        'risk_matrix': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),

        # ── v8 ──
        'beeswarm': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
        'control_chart': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
        'candlestick': lambda: _candlestick_route(fn, data, args, x, y, kwargs),
        'delta_band': lambda: _xy_route(fn, data, args, x, y, kwargs,
                                        ('series_a', 'series_b')),

        # ── v10 ──
        'raincloud': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
        # circle_pack(values_dict)
        'circle_pack': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
        # arc_diagram(nodes, edges)
        'arc_diagram': lambda: fn(
            data, args[0] if args else y, **kwargs),
    }

    if fn_name in routing:
        return routing[fn_name]()

    # Default: pass data as first positional arg if available
    if labels is not None and 'labels' not in kwargs and _accepts_param(fn, 'labels'):
        kwargs['labels'] = labels
    if data is not None:
        try:
            return fn(data, **kwargs)
        except TypeError:
            pass
    try:
        return fn(**kwargs)
    except TypeError as e:
        raise e


def _vector_field_route(fn, data, args, x, y, kwargs):
    """vector_field: plot(x, y, u, v) or plot(x, y, u=..., v=...)."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    extras = _pop_extras(extras, ('u', 'v'), kwargs)
    if len(extras) < 2:
        raise TypeError(
            "vector_field needs u and v components: "
            "plot(x, y, u, v, type='vector') or plot(x, y, u=U, v=V, type='vector')."
        )
    return fn(a, b, extras[0], extras[1], **kwargs)


def _xy_route(fn, data, args, x, y, kwargs, extra_names):
    """Generic (a, b, *extras) routing with kwargs fallback for extras."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    extras = _pop_extras(extras, extra_names, kwargs)
    if a is None or b is None:
        raise TypeError(f"{fn.__name__} is missing required data arguments.")
    return fn(a, b, *extras, **kwargs)


def _candlestick_route(fn, data, args, x, y, kwargs):
    """candlestick: plot(open, high, low, close, type='ohlc')."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    extras = _pop_extras(extras, ('low', 'close'), kwargs)
    if b is None or len(extras) < 2:
        raise TypeError(
            "candlestick needs (open, high, low, close): "
            "plot(o, h, l, c, type='ohlc')."
        )
    return fn(a, b, *extras[:2], **kwargs)


def _dot_plot_route(fn, data, args, x, y, kwargs):
    """dot_plot: (labels, values, values2?) or values with labels= kwarg."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    if a is not None and hasattr(a, "__getitem__") and len(a) > 0 and isinstance(a[0], str):
        return fn(a, b, *extras[:1], **kwargs)
    if b is not None:
        return fn(None, a, b, *extras[:1], **kwargs)
    raise TypeError("dot_plot needs (labels, values) or values with labels=.")


def _forest_route(fn, data, args, x, y, kwargs):
    """forest_plot: (labels, est, lo, hi) or (est, lo, hi) without labels."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    has_labels = (a is not None and hasattr(a, "__getitem__")
                  and len(a) > 0 and isinstance(a[0], str))
    if has_labels:
        if b is None or len(extras) < 2:
            raise TypeError("forest_plot needs (labels, est, lo, hi).")
        return fn(a, b, extras[0], extras[1], **kwargs)
    if b is not None and len(extras) >= 1:
        return fn(None, a, b, extras[0], **kwargs)
    raise TypeError("forest_plot needs (labels, est, lo, hi).")


def _ternary_route(fn, data, args, x, y, kwargs):
    """ternary_plot: plot(a, b, c, type='ternary') or plot(pts, type='ternary')."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    if a is not None and hasattr(a, 'ndim') and getattr(a, 'ndim', 1) == 2:
        return fn(a[:, 0], a[:, 1], a[:, 2], **kwargs)
    extras = _pop_extras(extras, ('b_comp', 'c_comp'), kwargs)
    if a is None or b is None or len(extras) < 1:
        raise TypeError("ternary_plot needs (a, b, c) fractions.")
    return fn(a, b, extras[0], **kwargs)


def _range_plot_route(fn, data, args, x, y, kwargs):
    """range_plot: plot(labels, low, mid, high) or via kwargs."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    extras = _pop_extras(extras, ('mid', 'high'), kwargs)
    if a is None or b is None or len(extras) < 2:
        raise TypeError(
            "range_plot needs (labels, low, mid, high): "
            "plot(labels, low, mid, high, type='scenario')."
        )
    return fn(a, b, extras[0], extras[1], **kwargs)


def _grouped_scatter_route(fn, data, args, x, y, kwargs):
    """grouped_scatter: plot(x, y, groups) or plot(x, y, groups=...)."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    extras = _pop_extras(extras, ('groups',), kwargs)
    if a is None or b is None or not extras:
        raise TypeError(
            "grouped_scatter needs (x, y, groups): "
            "plot(x, y, groups, type='segment_scatter')."
        )
    return fn(a, b, extras[0], **kwargs)


def _route_auc_data(fn, data, args, x, y, kwargs):
    """area_under_curve with sample data: plot(x, y, type='auc')."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    if a is None or b is None:
        raise TypeError("area_under_curve needs f(x) or x/y data.")
    return fn(None, a, b, **kwargs)


def _errorband_route(fn, data, args, x, y, kwargs):
    """errorband: (x, y, lower, upper) or (x, y, yerr=...)."""
    a, b, extras = _resolve_xy_extras(data, args, x, y)
    if len(extras) < 2 and 'lower' not in kwargs and 'yerr' not in kwargs:
        extras = _pop_extras(extras, ('lower', 'upper'), kwargs)
    if a is None or b is None:
        raise TypeError("errorband needs x and y data.")
    return fn(a, b, *extras, **kwargs)


# ──────────────────────────────────────────────
#  LIST TYPES
# ──────────────────────────────────────────────

def list_chart_types() -> list[str]:
    """List all available chart types (aliases and canonical names)."""
    _ensure_registered()
    aliases = list(_ALIASES.keys())
    canonical = list(CHART_REGISTRY.keys())
    return sorted(set(aliases + canonical))


# ──────────────────────────────────────────────
#  FigureFactory — Batch figure generation
# ──────────────────────────────────────────────

class FigureFactory:
    """
    Batch-generate multiple figures with consistent styling.

    Collects figures and saves them all at once, with automatic
    naming, numbering, and consistent style across the whole set.

    Examples
    --------
    # Basic usage
    f = FigureFactory(style='publication', title_prefix='Q1 Report')
    f.add('bar', [10, 20, 30], labels=['A', 'B', 'C'], title='Sales')
    f.add('line', [1,2,3], {'Trend': [4,5,6]}, x=[1,2,3], title='Trend')
    f.save_all('output/')

    # Or use chart-specific methods
    f = FigureFactory(style='nature')
    f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Sales')
    f.line([1,2,3], {'Trend': [4,5,6]}, x=[1,2,3], title='Trend')
    f.scatter(x, y, title='Correlation')
    f.save_all('output/')
    """

    def __init__(
        self,
        style: str = 'nature',
        title_prefix: str = '',
        palette: str = 'nature_qual',
        output_format: str = 'png',
        dpi: int = 300,
        auto_save_dir: str | None = None,
    ):
        """
        Parameters
        ----------
        style : str
            Style preset to apply to all figures.
        title_prefix : str
            Prefix added to every figure title (e.g. 'Q1 Report: ').
        palette : str
            Color palette for all figures.
        output_format : str
            Default output format ('png', 'svg', 'pdf').
        dpi : int
            Resolution for raster formats.
        """
        self.style = style
        self.title_prefix = title_prefix
        self.palette = palette
        self.output_format = output_format
        self.dpi = dpi
        self.figures: list[plt.Figure] = []
        self.titles: list[str] = []
        self._auto_save_dir = auto_save_dir

        # Apply style
        apply_style(style)

    def _full_title(self, title: Optional[str]) -> Optional[str]:
        """Combine prefix with title."""
        if title is None:
            return self.title_prefix if self.title_prefix else None
        if self.title_prefix:
            return f'{self.title_prefix} {title}'
        return title

    def add(
        self,
        chart_type: str,
        data,
        title: Optional[str] = None,
        **kwargs,
    ) -> plt.Figure:
        """
        Add a figure using the universal plot() function.

        Parameters
        ----------
        chart_type : str
            Chart type (alias or canonical name).
        data : array-like
            Data to plot.
        title : str, optional
            Figure title.
        **kwargs : dict
            Additional keyword arguments.
        """
        full_title = self._full_title(title)
        fig = plot(
            data, type=chart_type,
            title=full_title,
            style=self.style,
            palette=self.palette,
            **kwargs,
        )
        self.figures.append(fig)
        self.titles.append(full_title or f'Figure {len(self.figures):02d}')
        return fig

    def save_all(
        self,
        output_dir: str,
        fmt: Optional[str] = None,
        prefix: str = 'figure',
        close: bool = True,
    ) -> list[str]:
        """
        Save all figures to a directory.

        Parameters
        ----------
        output_dir : str
            Output directory path.
        fmt : str, optional
            Output format. Defaults to output_format set in __init__.
        prefix : str
            Filename prefix.
        close : bool
            Close figures after saving.

        Returns
        -------
        list of str
            Paths of saved files.
        """
        fmt = fmt or self.output_format
        os.makedirs(output_dir, exist_ok=True)
        self._auto_save_dir = output_dir

        saved = []
        for i, fig in enumerate(self.figures, 1):
            path = os.path.join(output_dir, f'{prefix}_{i:02d}.{fmt}')
            save_figure(fig, path, fmt=fmt, dpi=self.dpi, close=close)
            saved.append(path)
            print(f"  Saved: {path}")

        print(f"\n  Total: {len(saved)} figures saved to {output_dir}/")
        return saved

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None and self.figures and getattr(self, "_auto_save_dir", None):
            self.save_all(self._auto_save_dir)
        elif exc_type is not None:
            import matplotlib.pyplot as plt
            for fig in self.figures:
                plt.close(fig)
        return False

    def __len__(self):
        return len(self.figures)

    def __repr__(self):
        return f"FigureFactory(style={self.style!r}, figures={len(self.figures)})"

    def __getattr__(self, name: str):
        """Resolve any chart alias as a method: f.qq(...), f.ridgeline(...),
        f.surface(...), f.bump(...) — no per-chart boilerplate needed."""
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            canonical = resolve_chart_type(name)
        except ValueError:
            raise AttributeError(
                f"FigureFactory has no method {name!r} and no chart type "
                f"matches it. See list_chart_types()."
            ) from None

        def _method(data=None, *args, **kwargs):
            return self.add(canonical, data, *args, **kwargs)

        _method.__name__ = name
        _method.__doc__ = f"Add a {canonical} figure (alias '{name}')."
        return _method

    # ── Convenience methods ──

    def bar(self, data, *args, **kwargs):
        """Add a bar chart."""
        return self.add('bar', data, *args, **kwargs)

    def grouped(self, data, *args, **kwargs):
        """Add a grouped bar chart."""
        return self.add('grouped', data, *args, **kwargs)

    def line(self, data, x=None, *args, **kwargs):
        """Add a line chart."""
        if x is not None:
            kwargs['x'] = x
        return self.add('line', data, *args, **kwargs)

    def scatter(self, x, y=None, *args, **kwargs):
        """Add a scatter plot."""
        if y is not None:
            kwargs['y'] = y
        return self.add('scatter', x, *args, **kwargs)

    def pie(self, data, *args, **kwargs):
        """Add a pie chart."""
        return self.add('pie', data, *args, **kwargs)

    def donut(self, data, *args, **kwargs):
        """Add a donut chart."""
        return self.add('donut', data, *args, **kwargs)

    def hist(self, data, *args, **kwargs):
        """Add a histogram."""
        return self.add('hist', data, *args, **kwargs)

    def box(self, data, *args, **kwargs):
        """Add a box plot."""
        return self.add('box', data, *args, **kwargs)

    def violin(self, data, *args, **kwargs):
        """Add a violin plot."""
        return self.add('violin', data, *args, **kwargs)

    def radar(self, data, *args, **kwargs):
        """Add a radar chart."""
        return self.add('radar', data, *args, **kwargs)

    def waterfall(self, data, *args, **kwargs):
        """Add a waterfall chart."""
        return self.add('waterfall', data, *args, **kwargs)

    def network(self, data, *args, **kwargs):
        """Add a network graph."""
        return self.add('network', data, *args, **kwargs)

    def sankey(self, data, *args, **kwargs):
        """Add a sankey diagram."""
        return self.add('sankey', data, *args, **kwargs)

    def timeline(self, data, *args, **kwargs):
        """Add a timeline."""
        return self.add('timeline', data, *args, **kwargs)

    def gantt(self, data, *args, **kwargs):
        """Add a gantt chart."""
        return self.add('gantt', data, *args, **kwargs)

    def treemap(self, data, *args, **kwargs):
        """Add a treemap."""
        return self.add('treemap', data, *args, **kwargs)

    def dashboard(self, data, *args, **kwargs):
        """Add a dashboard."""
        return self.add('dashboard', data, *args, **kwargs)

    def kpi(self, data, *args, **kwargs):
        """Add a KPI card."""
        return self.add('kpi', data, *args, **kwargs)

    def gauge(self, data, *args, **kwargs):
        """Add a gauge."""
        return self.add('gauge', data, *args, **kwargs)

    def mindmap(self, data, *args, **kwargs):
        """Add a mind map."""
        return self.add('mind', data, *args, **kwargs)

    def process_flow(self, data, *args, **kwargs):
        """Add a process flow."""
        return self.add('flow', data, *args, **kwargs)

    def correlation(self, data, *args, **kwargs):
        """Add a correlation matrix."""
        return self.add('correlation', data, *args, **kwargs)

    def sensitivity(self, data, *args, **kwargs):
        """Add a sensitivity analysis."""
        return self.add('sensitivity', data, *args, **kwargs)

    def fit(self, data, *args, **kwargs):
        """Add a fit curve."""
        return self.add('fit', data, *args, **kwargs)

    def residual(self, data, *args, **kwargs):
        """Add a residual plot."""
        return self.add('residual', data, *args, **kwargs)

    def confusion(self, data, *args, **kwargs):
        """Add a confusion matrix."""
        return self.add('confusion', data, *args, **kwargs)

    def roc(self, data, *args, **kwargs):
        """Add a ROC curve."""
        return self.add('roc', data, *args, **kwargs)

    def learning_curve(self, data, *args, **kwargs):
        """Add a learning curve."""
        return self.add('learning', data, *args, **kwargs)

    def feature_importance(self, data, *args, **kwargs):
        """Add a feature importance chart."""
        return self.add('importance', data, *args, **kwargs)

    def pareto(self, data, *args, **kwargs):
        """Add a Pareto front."""
        return self.add('pareto', data, *args, **kwargs)

    def validation(self, data, *args, **kwargs):
        """Add a validation plot."""
        return self.add('validation', data, *args, **kwargs)

    def clustering(self, data, *args, **kwargs):
        """Add a clustering visualization."""
        return self.add('cluster', data, *args, **kwargs)

    def decision_boundary(self, data, *args, **kwargs):
        """Add a decision boundary plot."""
        return self.add('decision', data, *args, **kwargs)

    def dumbbell(self, data, *args, **kwargs):
        """Add a dumbbell plot."""
        return self.add('dumbbell', data, *args, **kwargs)

    def slope(self, data, *args, **kwargs):
        """Add a slope chart."""
        return self.add('slope', data, *args, **kwargs)

    def parallel(self, data, *args, **kwargs):
        """Add parallel coordinates."""
        return self.add('parallel', data, *args, **kwargs)

    def sparkline(self, data, *args, **kwargs):
        """Add a sparkline."""
        return self.add('spark', data, *args, **kwargs)

    def bullet(self, data, *args, **kwargs):
        """Add a bullet chart."""
        return self.add('bullet', data, *args, **kwargs)

    def comparison(self, data, *args, **kwargs):
        """Add a comparison bar."""
        return self.add('compare', data, *args, **kwargs)

    def step(self, data, *args, **kwargs):
        """Add a step chart."""
        return self.add('step', data, *args, **kwargs)

    def area(self, data, *args, **kwargs):
        """Add an area chart."""
        return self.add('area', data, *args, **kwargs)

    def stacked(self, data, *args, **kwargs):
        """Add a stacked bar chart."""
        return self.add('stacked', data, *args, **kwargs)


__all__ = [
    "plot",
    "FigureFactory",
    "list_chart_types",
    "resolve_chart_type",
]