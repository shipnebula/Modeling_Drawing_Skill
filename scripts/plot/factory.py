"""
plot/factory.py — Universal plot() function and FigureFactory class.

The single entry point for everything. One function call, auto-detection,
batch generation, zero boilerplate.
"""
from __future__ import annotations

import os
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
    from . import basic, model, advanced, infographic
    for mod in (basic, model, advanced, infographic):
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
    'compare': 'comparison_bar',
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
    raise ValueError(
        f"Unknown chart type '{type_name}'. "
        f"Use type=list() to see all available types."
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

    # Multiple numeric columns with an index → line chart (time series style)
    if len(numeric_cols) >= 2 and (len(numeric_cols) == data.shape[1] or len(numeric_cols) >= 2):
        return 'line'

    # One numeric + one categorical → bar chart
    if len(numeric_cols) == 1 and len(non_numeric_cols) == 1:
        return 'bar'

    # All numeric → correlation matrix
    if len(numeric_cols) >= 2 and len(non_numeric_cols) == 0:
        return 'correlation'

    # Just one column → line
    if len(numeric_cols) == 1:
        return 'line'

    return 'line'


def _detect_from_numpy(data) -> str:
    """Detect best chart type from a numpy array."""
    if not isinstance(data, np.ndarray):
        return 'bar'
    if data.ndim == 2:
        return 'correlation'
    if data.ndim == 1:
        return 'bar'
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
        if x is not None:
            return 'line'
        return 'grouped'

    # List of lists/tuples (2D)
    if isinstance(data, (list, tuple)) and len(data) > 0:
        if isinstance(data[0], (list, tuple, np.ndarray)):
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
    if save_path:
        chart_kwargs.setdefault('save_path', save_path)

    # Handle different data patterns
    fig = _call_chart_fn(
        chart_fn, data, args, labels=labels, x=x, y=y,
        **chart_kwargs
    )

    if save_path:
        save_figure(fig, save_path)

    return fig


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
        # line_chart(x, y_series)
        'line_chart': lambda: fn(x if x is not None else data, data, **kwargs),
        # scatter_plot(x, y)
        'scatter_plot': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # residual_plot(y_true, y_pred)
        'residual_plot': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # confusion_matrix(y_true, y_pred)
        'confusion_matrix': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # roc_curve(y_true, y_score)
        'roc_curve': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # fit_curve(x, y)
        'fit_curve': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # learning_curve(train_scores, val_scores)
        'learning_curve': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # network_graph(nodes, edges)
        'network_graph': lambda: fn(data, y if y is not None else (args[0] if args else None), **kwargs),
        # radar_chart(labels, values, names=None, ...)
        'radar_chart': lambda: fn(data, args[0] if args else data, **kwargs),
        # step_chart(x, y)
        'step_chart': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # area_chart(x, y_series)
        'area_chart': lambda: fn(x if x is not None else data, data, **kwargs),
        # clustering_2d(X, labels)
        'clustering_2d': lambda: fn(data, labels if labels is not None else y, **kwargs),
        # decision_boundary(X, y, model)
        'decision_boundary': lambda: fn(data, y if y is not None else labels, **kwargs),
        # feature_importance(names, values)
        'feature_importance': lambda: fn(labels if labels is not None else data, data, **kwargs),
        # pareto_front(x_values, y_values)
        'pareto_front': lambda: fn(x if x is not None else data, y if y is not None else data, **kwargs),
        # validation_plot(cv_scores)
        'validation_plot': lambda: fn(data, **kwargs),
        # sensitivity_analysis(parameters, low_values, high_values)
        'sensitivity_analysis': lambda: fn(**kwargs),
        # dashboard(metrics)
        'dashboard': lambda: fn(data, **kwargs) if data is not None else fn(**kwargs),
    }

    if fn_name in routing:
        return routing[fn_name]()

    # Default: pass data as first positional arg if available
    if data is not None:
        try:
            return fn(data, **kwargs)
        except TypeError:
            pass
    try:
        return fn(**kwargs)
    except TypeError as e:
        raise e


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

        saved = []
        for i, fig in enumerate(self.figures, 1):
            path = os.path.join(output_dir, f'{prefix}_{i:02d}.{fmt}')
            save_figure(fig, path, fmt=fmt, dpi=self.dpi, close=close)
            saved.append(path)
            print(f"  Saved: {path}")

        print(f"\n  Total: {len(saved)} figures saved to {output_dir}/")
        return saved

    def __len__(self):
        return len(self.figures)

    def __repr__(self):
        return f"FigureFactory(style={self.style!r}, figures={len(self.figures)})"

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