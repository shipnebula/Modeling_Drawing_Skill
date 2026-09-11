# API Reference

Complete documentation for all functions.

---

## Factory (the easy way)

### `plot()`
Universal plotting function. Auto-detects chart type from data.

```python
plot(data, *args, type=None, title=None, labels=None, x=None, y=None,
     style=None, palette=None, figsize=None, save_path=None, **kwargs)
```

- `data` — primary data (list, dict, array, DataFrame)
- `type` — force chart type (e.g. 'bar', 'line', 'scatter')
- `title` — chart title
- `labels` — category labels
- `x`, `y` — x/y axis data
- `style` — style preset name
- `palette` — color palette name
- `figsize` — (width, height) in inches
- `save_path` — file path to save
- `**kwargs` — passed to the underlying chart function

### `FigureFactory`
Batch figure generation with consistent styling.

```python
f = FigureFactory(style='nature', title_prefix='', palette='nature_qual',
                  output_format='png', dpi=300)
f.add(chart_type, data, title=None, **kwargs)  # Add a figure
f.save_all(output_dir, fmt=None, prefix='figure', close=True)  # Save all
```

Convenience methods: `f.bar()`, `f.line()`, `f.scatter()`, `f.pie()`, `f.hist()`, `f.radar()`, `f.dashboard()`, `f.gauge()`, `f.correlation()`, `f.sensitivity()`, `f.fit()`, `f.residual()`, `f.confusion()`, `f.roc()`, `f.feature_importance()`, `f.pareto()`, `f.validation()`, `f.network()`, `f.sankey()`, `f.timeline()`, `f.gantt()`, `f.treemap()`, `f.dumbbell()`, `f.slope()`, `f.parallel()`, `f.sparkline()`, `f.bullet()`, `f.comparison()`, `f.step()`, `f.area()`, `f.stacked()`, `f.box()`, `f.violin()`, `f.donut()`, `f.kpi()`, `f.mindmap()`, `f.process_flow()`, `f.clustering()`, `f.decision_boundary()`, `f.learning_curve()`, `f.grouped()`

### `list_chart_types()`
Returns all available chart type names (aliases and canonical names).

---

## Palette

### `get_palette(name)`
Returns a list of hex color strings for the given palette.

### `get_color(palette, index)`
Returns a single color from a palette.

### `auto_colors(n, palette='nature_qual')`
Generates `n` colors from the given palette. Cycles if n > palette length.

### `sequential_colormap(palette, n=9)`
Returns `n` colors interpolated across a sequential palette.

### `diverging_colormap(palette, n=9)`
Returns `n` colors interpolated across a diverging palette.

### `blend(color1, color2, ratio)`
Blends two hex colors. ratio=0 gives color1, ratio=1 gives color2.

### `lightness(color, amount)`
Adjusts color lightness. Positive = lighter, negative = darker.

### `is_dark(color)`
Returns True if the color is dark.

### `contrast_color(color)`
Returns white or dark text color for best contrast against the given background.

### Constants
- `QUALITATIVE`, `SEQUENTIAL`, `DIVERGING`, `THEME` — palette dictionaries
- `ALL_PALETTES` — all palettes combined
- `NEUTRAL` — neutral gray color
- `ACCENT` — accent color

---

## Styles

### `apply_style(name)`
Applies a style preset to matplotlib's rcParams.

### `apply_style_to_axes(ax, style)`
Applies style to a specific axes object.

### `get_style_config(name)`
Returns the rcParams dict for a style preset.

### `get_color_theme(style)`
Returns the color theme dict for a style preset.

### `list_styles()`
Returns list of available style names.

### `COLOR_THEMES`
Dictionary of color themes.

---

## Utils

### `setup_figure(figsize=None, **kwargs)`
Creates a new figure with configured defaults.

### `figsubplots(nrows=1, ncols=1, **kwargs)`
Creates figure with subplots.

### `save_figure(fig, path, fmt=None, dpi=300, close=True)`
Saves a figure to file. Auto-detects format from extension.

### `format_numbers(value, style='smart', decimals=2)`
Formats a number for display.

### `axis_config(ax, style='nature', grid='y', grid_alpha=0.15,
                show_top=False, show_right=False, spine_color='#666666')`
Configures axes spines and grid.

### `add_grid(ax, grid='y', alpha=0.15)`
Adds grid to axes.

### `add_annotation(ax, text, xy, xytext=None, arrow=False, ...)`
Adds a text annotation.

### `add_data_labels(ax, bars, fmt='%d', ...)`
Adds data labels to bars.

### `auto_palette(data, palette='nature_qual')`
Returns appropriate palette for the data.

### `format_ticks(ax, style='smart')`
Auto-formats tick labels.

### `auto_layout(fig, pad=0.1, hspace=None, wspace=None)`
Applies tight layout with padding.

### `add_figure_title(fig, title, subtitle=None)`
Adds a figure title with optional subtitle.

### `add_source_note(ax, text)`
Adds a source note to the axes.

---

## Chart Functions

### Basic (12)

`bar_chart(data, labels, title, ...)` — Bar chart
`grouped_bar(data, labels, title, ...)` — Grouped bar
`stacked_bar(data, labels, title, ...)` — Stacked bar
`line_chart(x, y_series, title, ...)` — Line chart
`area_chart(x, y_series, title, ...)` — Area chart
`scatter_plot(x, y, title, ...)` — Scatter plot
`pie_chart(data, labels, title, ...)` — Pie chart
`donut_chart(data, labels, title, ...)` — Donut chart
`histogram(data, title, ...)` — Histogram
`box_plot(data, labels, title, ...)` — Box plot
`violin_plot(data, labels, title, ...)` — Violin plot
`step_chart(x, y, title, ...)` — Step chart

### Model (12)

`fit_curve(x, y, title, ...)` — Regression fit
`residual_plot(y_true, y_pred, title, ...)` — Residual plot
`confusion_matrix(y_true, y_pred, title, ...)` — Confusion matrix
`roc_curve(y_true, y_score, title, ...)` — ROC curve
`learning_curve(train_scores, val_scores, title, ...)` — Learning curve
`sensitivity_analysis(parameters, low_values, high_values, title, ...)` — Tornado
`pareto_front(x_values, y_values, title, ...)` — Pareto front
`validation_plot(cv_scores, title, ...)` — Validation plot
`feature_importance(names, values, title, ...)` — Feature importance
`clustering_2d(X, labels, title, ...)` — Clustering
`decision_boundary(X, y, model, title, ...)` — Decision boundary
`correlation_matrix(df, title, ...)` — Correlation matrix

### Advanced (10)

`network_graph(nodes, edges, title, ...)` — Network graph
`sankey_diagram(flows, labels, title, ...)` — Sankey diagram
`radar_chart(labels, values, names, title, ...)` — Radar chart
`waterfall_chart(categories, values, title, ...)` — Waterfall
`dumbbell_plot(labels, old_values, new_values, title, ...)` — Dumbbell
`slope_chart(labels, y1, y2, title, ...)` — Slope chart
`timeline(events, title, ...)` — Timeline
`parallel_coordinates(df, title, ...)` — Parallel coordinates
`gantt_chart(tasks, title, ...)` — Gantt chart
`treemap(values, labels, title, ...)` — Treemap

### Infographic (8)

`dashboard(metrics, title, ...)` — Dashboard
`kpi_card(label, value, change, ...)` — KPI card
`bullet_chart(actual, target, ...)` — Bullet chart
`sparkline(values, title, ...)` — Sparkline
`gauge(value, min_val, max_val, label, ...)` — Gauge
`process_flow(steps, title, ...)` — Process flow
`mind_map(center, branches, title, ...)` — Mind map
`comparison_bar(labels, values, target, ...)` — Comparison bar

---

## Version

`__version__` — Current library version (1.1.0)