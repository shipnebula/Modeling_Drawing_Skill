# Chart Catalog

Every chart in the library, with code you can copy-paste.

---

## Quick reference

```python
from plot import plot

# Use plot() with type= for any chart below
# Or import the specific function: from plot import bar_chart
```

---

## Basic Statistics (12 charts)

### Bar chart
Category comparison. The workhorse.

```python
plot([120, 180, 150, 210], labels=['2021', '2022', '2023', '2024'],
     title='Annual Revenue', ylabel='Revenue (M)')
# Auto-detected from list + labels
```

### Grouped bar
Compare multiple series across categories.

```python
plot({'Model A': [10, 20, 30], 'Model B': [15, 25, 35]},
     labels=['X', 'Y', 'Z'], type='grouped', title='Comparison')
```

### Stacked bar
Show composition within categories.

```python
plot({'A': [10, 20], 'B': [15, 25], 'C': [5, 10]},
     labels=['Q1', 'Q2'], type='stacked', title='Composition')
```

### Line chart
Trends over time or another continuous variable.

```python
plot({'Model A': [10, 12, 15, 18, 22], 'Model B': [8, 11, 14, 17, 20]},
     x=[1, 2, 3, 4, 5], markers=True, title='Convergence')
```

### Area chart
Cumulative or stacked line. Good for volume over time.

```python
plot([1, 2, 3, 4, 5], {'Revenue': [10, 15, 20, 25, 30]},
     type='area', title='Volume')
```

### Scatter plot
Relationship between two variables. Add a fit line with `show_fit=True`.

```python
plot(x, y, type='scatter', show_fit=True, title='Relationship')
```

### Pie chart
Proportions. Use donut chart instead if you want a hole in the middle.

```python
plot([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
     type='pie', title='Distribution')
```

### Donut chart
Pie chart with center text.

```python
plot([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
     type='donut', title='Market Share', center_text='Total: $1M')
```

### Histogram
Distribution of a single variable. Add KDE curve with `kde=True`.

```python
import numpy as np
plot(np.random.randn(200), type='hist', kde=True, title='Distribution')
```

### Box plot
Compare distributions across groups.

```python
import numpy as np
data = [np.random.randn(50), np.random.randn(50), np.random.randn(50)]
plot(data, labels=['A', 'B', 'C'], type='box', title='Distribution')
```

### Violin plot
Box plot on steroids. Shows the shape of the distribution.

```python
plot(data, labels=['A', 'B', 'C'], type='violin', title='Distribution')
```

### Step chart
Discrete changes. Good for price changes, regime shifts.

```python
plot([1, 2, 3, 4, 5], [10, 10, 15, 15, 20],
     type='step', title='Price Changes')
```

---

## Model Analysis (12 charts)

### Fit curve
Regression with confidence bands. The classic "does my model fit?" plot.

```python
plot(x, y, type='fit', title='Regression')
```

### Residual plot
Model diagnostics. Residuals should be random, not patterned.

```python
plot(y_true, y_pred, type='residual', title='Residuals')
```

### Confusion matrix
Classification evaluation. Good for precision/recall visualization.

```python
plot(y_true, y_pred, type='confusion', title='Confusion Matrix')
```

### ROC curve
Binary classification. AUC tells you how good your classifier is.

```python
plot(y_true, y_score, type='roc', title='ROC Curve')
```

### Learning curve
Bias-variance analysis. Shows training vs validation error as more data is added.

```python
plot(train_scores, val_scores, type='learning', title='Learning Curve')
```

### Sensitivity analysis (tornado)
Parameter sensitivity. Shows which parameters matter most.

```python
plot(
    parameters=['Rate', 'Batch Size', 'Layers', 'Dropout'],
    low_values=[0.88, 0.90, 0.85, 0.80],
    high_values=[0.98, 0.96, 0.94, 0.90],
    type='sensitivity', title='Sensitivity Analysis',
)
```

### Pareto front
Multi-objective optimization. Shows the tradeoff frontier.

```python
plot(x_values, y_values, type='pareto', title='Pareto Front')
```

### Validation plot
Cross-validation stability. Shows mean ± std across folds.

```python
plot(cv_scores, type='validation', title='Cross-Validation')
```

### Feature importance
Feature ranking. Which features matter most?

```python
plot(names, values, type='feature_importance', title='Feature Importance')
```

### Clustering (2D)
Cluster visualization with boundaries.

```python
plot(X, labels, type='cluster', title='Clustering')
```

### Decision boundary
Classifier regions in 2D.

```python
plot(X, y, model, type='decision', title='Decision Boundary')
```

### Correlation matrix
Variable relationships. Heatmap of correlations.

```python
import pandas as pd
df = pd.read_csv('data.csv')
plot(df, type='correlation', title='Correlations')
```

---

## Advanced (10 charts)

### Network graph
Network topology. Nodes and edges.

```python
plot(nodes, edges, type='network', title='Network')
```

### Sankey diagram
Flow analysis. Where things go from A to B.

```python
plot(flows, labels=labels, type='sankey', title='Flow Analysis')
```

### Radar chart
Multi-dimensional comparison. Compare two systems across multiple criteria.

```python
plot(
    ['Speed', 'Accuracy', 'Cost', 'Reliability', 'Usability'],
    [[4, 5, 3, 4, 5], [3, 4, 4, 5, 3]],
    names=['System A', 'System B'],
    type='radar', title='Comparison',
)
```

### Waterfall chart
Cumulative changes. Start value, then add/subtract.

```python
plot(
    categories=['Start', '+Revenue', '-Cost', 'End'],
    values=[100, 50, -30, 120],
    type='waterfall', title='Cash Flow',
)
```

### Dumbbell plot
Before/after comparison. Shows change with two dots.

```python
plot(
    labels=['A', 'B', 'C'],
    old_values=[30, 50, 20],
    new_values=[40, 60, 25],
    type='dumbbell', title='Before vs After',
)
```

### Slope chart
Ranking changes. Good for "how did positions change?"

```python
plot(
    labels=['A', 'B', 'C'],
    y1=[80, 60, 40],
    y2=[70, 50, 45],
    type='slope', title='Rank Changes',
)
```

### Timeline
Event sequences. Milestones and durations.

```python
plot(
    events=[
        {'time': 1.0, 'label': 'Start', 'category': 'milestone', 'duration': 2},
        {'time': 3.0, 'label': 'End', 'category': 'milestone', 'duration': 1},
    ],
    type='timeline', title='Project Timeline',
)
```

### Parallel coordinates
Multi-dimensional data in one chart. Each line is a data point.

```python
plot(df, type='parallel', title='Parallel Coordinates')
```

### Gantt chart
Project schedules. Tasks with start/end/progress.

```python
plot(
    tasks=[
        {'name': 'Task 1', 'start': 0, 'end': 5, 'progress': 1.0},
        {'name': 'Task 2', 'start': 5, 'end': 10, 'progress': 0.5},
    ],
    type='gantt', title='Project Schedule',
)
```

### Treemap
Hierarchical proportions. Like a pie chart but rectangular.

```python
plot([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
     type='treemap', title='Treemap')
```

---

## Infographics (8 charts)

### Dashboard
Multi-KPI summary. Put this in your 摘要.

```python
plot([
    {'label': 'Accuracy', 'value': '94%', 'change': '+2%', 'change_dir': 'up', 'progress': 0.94},
    {'label': 'F1', 'value': '0.91', 'change': '+0.03', 'change_dir': 'up', 'progress': 0.91},
], title='Model Performance', type='dashboard', ncols=2)
```

### KPI card
Single metric highlight.

```python
plot('Revenue', value='$4.2M', change='+12%',
     change_dir='up', progress=0.84, title='KPI', type='kpi')
```

### Bullet chart
Actual vs target with benchmarks.

```python
plot(actual=85, target=90, min_val=0, max_val=100,
     benchmarks=[70, 80], title='Target', type='bullet')
```

### Sparkline
Compact trend. Small enough to put next to a table cell.

```python
plot(np.cumsum(np.random.randn(50)), title='Sparkline', type='spark')
```

### Gauge
Value on a scale. Good for percentages and KPIs.

```python
plot(75, min_val=0, max_val=100, label='Progress',
     title='Gauge', type='gauge')
```

### Process flow
Sequential steps. Good for "problem restatement" sections.

```python
plot(['Data', 'Clean', 'Model', 'Validate', 'Deploy'],
     title='Pipeline', type='flow')
```

### Mind map
Topic hierarchy. Good for "problem definition" sections.

```python
plot('Center', branches=[
    {'label': 'Branch A', 'items': ['Item 1', 'Item 2']},
    {'label': 'Branch B', 'items': ['Item 3', 'Item 4']},
], title='Mind Map', type='mind')
```

### Comparison bar
Compare values against a target line.

```python
plot(['A', 'B', 'C'], [85, 72, 90], target=80,
     title='Target Comparison', type='compare')
```

---

## Listing all types

```python
from plot import list_chart_types
print(list_chart_types())
```

---

# Sciences & Statistics charts (v2.0)

Scientific-computing and statistical charts added in v2.0. All accept
`title`, `figsize`, `save_path`; images live in `docs/images/`.

| Chart | Call | Example image |
|---|---|---|
| 3-D surface | `plot(X, Y, Z, type='surface')` | [surface3d](../docs/images/42_surface3d.png) |
| Contour map | `plot(x, y, Z, type='contour', mark_min=True)` | [contour](../docs/images/43_contour.png) |
| Vector field | `plot(x, y, u, v, type='vector', mode='both')` | [vector field](../docs/images/44_vector_field.png) |
| Phase portrait | `plot(x, y, type='phase')` | [phase](../docs/images/45_phase_portrait.png) |
| Dual axis | `plot(x, y1, y2, type='twin')` | [twin axis](../docs/images/46_twin_axis.png) |
| Confidence band | `plot(x, y, yerr=err, type='band')` | [errorband](../docs/images/47_errorband.png) |
| Annotated heatmap | `plot(matrix, type='heatmap', row_labels=..., col_labels=...)` | [heatmap](../docs/images/48_heatmap.png) |
| Optimizer trace | `plot(f, path, type='trace')` | [trace](../docs/images/49_optimization_trace.png) |
| Wind rose | `plot(theta, r, type='polar', zero_location='N', clockwise=True)` | [polar](../docs/images/50_polar.png) |
| Log-log lines | `plot(series, type='loglog', show_fit_slope=True)` | [loglog](../docs/images/51_loglog.png) |
| Q-Q plot | `plot(sample, type='qq')` | [qq](../docs/images/52_qq.png) |
| Empirical CDF | `plot(groups, type='ecdf')` | [ecdf](../docs/images/53_ecdf.png) |
| Ridgeline | `plot(groups, type='ridge')` | [ridgeline](../docs/images/54_ridgeline.png) |
| Hexbin | `plot(x, y, type='hexbin')` | [hexbin](../docs/images/55_hexbin.png) |
| Stem / lollipop | `plot(x, y, type='stem')` | [stem](../docs/images/56_stem.png) |
| Error bars | `plot(x, y, yerr, type='errorbar')` | [errorbar](../docs/images/57_errorbar.png) |
| Bubble | `plot(x, y, sizes, type='bubble')` | [bubble](../docs/images/58_bubble.png) |
| Bump | `plot(ranks, type='bump')` | [bump](../docs/images/59_bump.png) |
| Stream graph | `plot(series, type='streamgraph')` | [stream](../docs/images/60_streamgraph.png) |
| Funnel | `plot(stages, values, type='funnel')` | [funnel](../docs/images/61_funnel.png) |
| Waffle | `plot(values, labels=..., type='waffle')` | [waffle](../docs/images/62_waffle.png) |
| Pyramid | `plot(labels, left, right, type='pyramid')` | [pyramid](../docs/images/63_pyramid.png) |
| Sunburst | `plot(tree, type='sunburst')` | [sunburst](../docs/images/64_sunburst.png) |
| Icicle | `plot(tree, type='icicle')` | [icicle](../docs/images/65_icicle.png) |
| Mosaic | `plot(counts, type='mosaic')` | [mosaic](../docs/images/66_mosaic.png) |
| Dendrogram | `plot(observations, type='dendrogram')` | [dendrogram](../docs/images/67_dendrogram.png) |
| Distribution panel | `plot(sample, type='distpanel')` | [panel](../docs/images/68_distribution_panel.png) |
| Scatter matrix | `plot(matrix, type='pairplot')` | [pairs](../docs/images/69_scatter_matrix.png) |
| Multi-panel figure | `panel_figure([specs], ncols=2)` | [composite](../docs/images/70_panel_figure.png) |

---

# Calculus, ML & diagram charts (v3.0)

| Chart | Call | Example image |
|---|---|---|
| Definite integral | `plot(f, type='integral', a=0, b=2)` | [auc](../docs/images/71_auc.png) |
| Riemann sum | `plot(f, type='riemann', a=0, b=2, n=9)` | [riemann](../docs/images/72_riemann.png) |
| Tangent line | `plot(f, type='tangent', x0=1.2)` | [tangent](../docs/images/73_tangent.png) |
| Interpolation | `plot(x, y, type='spline')` | [interp](../docs/images/74_interpolation.png) |
| PR curve | `plot(y_true, y_score, type='pr')` | [pr](../docs/images/75_pr_curve.png) |
| Predicted vs actual | `plot(y_true, y_pred, type='pred_actual')` | [pred](../docs/images/76_pred_actual.png) |
| Regression panel | `plot(y_true, y_pred, type='regdiag')` | [panel](../docs/images/77_regression_panel.png) |
| Elbow | `plot(X, type='elbow')` | [elbow](../docs/images/78_elbow.png) |
| Silhouette | `plot(X, labels, type='silhouette')` | [silhouette](../docs/images/79_silhouette.png) |
| Scree | `plot(X, type='pca')` | [scree](../docs/images/80_scree.png) |
| Hypothesis test | `plot(sample, type='ttest', mu=0)` | [ttest](../docs/images/81_hypothesis_test.png) |
| Lorenz curve | `plot(values, type='gini')` | [lorenz](../docs/images/82_lorenz.png) |
| Forecast | `plot(history, predicted, type='prediction', lower=lo, upper=hi)` | [forecast](../docs/images/83_forecast.png) |
| AHP hierarchy | `plot(goal, criteria, alternatives, type='ahp', weights=[...])` | [ahp](../docs/images/84_ahp.png) |
| 3-D scatter | `plot(x, y, z, type='scatter_3d')` | [scatter3d](../docs/images/85_scatter3d.png) |
| Palette gallery | `palette_preview()` | [palettes](../docs/images/86_palette_preview.png) |
| Style gallery | `style_preview()` | [styles](../docs/images/87_style_preview.png) |

---

# Dynamics, time-series & accessibility charts (v4.0)

| Chart | Call | Example image |
|---|---|---|
| Bifurcation | `plot(a_range=(2.5, 4.0), type='bifurcation')` | [bifurcation](../docs/images/88_bifurcation.png) |
| Cobweb | `plot(f, x0=0.3, type='cobweb')` | [cobweb](../docs/images/89_cobweb.png) |
| Monte-Carlo | `plot(samples, type='montecarlo', true_value=3.5)` | [mc](../docs/images/90_monte_carlo.png) |
| ACF/PACF | `plot(series, type='acf', nlags=24)` | [acf](../docs/images/91_acf_pacf.png) |
| Decomposition | `plot(series, period=12, type='decomposition')` | [decomp](../docs/images/92_decomposition.png) |
| Clustermap | `plot(matrix, type='cluster_heatmap', standardize=True)` | [clustermap](../docs/images/93_clustermap.png) |
| Correlation network | `plot(data, type='corr_network', threshold=0.3)` | [corrnet](../docs/images/94_corr_network.png) |
| Polar bars | `plot(theta, r, type='rose', zero_location='N')` | [polarbar](../docs/images/95_polar_bar.png) |
| Colorblind check | `cvd_preview('nature_qual')` | [cvd](../docs/images/96_cvd_preview.png) |

---

# Evaluation & statistics charts (v5.0)

| Chart | Call | Example image |
|---|---|---|
| Fit comparison | `plot(x, y, type='model_comparison')` | [fits](../docs/images/97_fit_comparison.png) |
| Multi-model ROC | `plot(y_true, scores, type='multi_roc')` | [roc](../docs/images/98_roc_comparison.png) |
| Calibration | `plot(y_true, y_prob, type='reliability')` | [calibration](../docs/images/99_calibration.png) |
| Gain / lift | `plot(y_true, y_score, type='lift')` | [gain](../docs/images/100_gain_lift.png) |
| PCA biplot | `plot(matrix, type='pca_biplot')` | [biplot](../docs/images/101_biplot.png) |
| KS test | `plot(s1, s2, type='kstest')` | [ks](../docs/images/102_ks_test.png) |
| Scenario ranges | `plot(labels, low, mid, high, type='scenario')` | [range](../docs/images/103_range_plot.png) |
| Calendar heatmap | `plot(values, type='calendar', start_date='2025-01-01')` | [calendar](../docs/images/104_calendar.png) |
| Grouped scatter | `plot(x, y, groups, type='group_scatter')` | [grouped](../docs/images/105_grouped_scatter.png) |
| Bland-Altman | `plot(m1, m2, type='agreement')` | [ba](../docs/images/106_bland_altman.png) |
| Decision tree | `tree_plot(X=X, y=y)` | [tree](../docs/images/107_tree_plot.png) |

---

# Structure & diagnostics charts (v6.0)

| Chart | Call | Example image |
|---|---|---|
| Joint plot | `plot(x, y, type='jointplot')` | [joint](../docs/images/108_joint_plot.png) |
| Forest plot | `plot(labels, est, lo, hi, type='forest')` | [forest](../docs/images/109_forest_plot.png) |
| Strip plot | `plot(groups, type='jitter', overlay_box=True)` | [strip](../docs/images/110_strip_plot.png) |
| Smooth trend | `plot(x, y, type='lowess')` | [smooth](../docs/images/111_smooth_plot.png) |
| Density contours | `plot(x, y, type='kde_scatter', fill=True)` | [contour](../docs/images/112_scatter_contour.png) |
| Diverging bars | `plot(labels, values, type='signed_bar')` | [diverging](../docs/images/113_diverging_bar.png) |
| Cross-correlation | `plot(s1, s2, type='lead_lag', max_lag=24)` | [ccf](../docs/images/114_cross_correlation.png) |
| Pareto chart | `plot(labels, counts, type='vital_few')` | [pareto](../docs/images/115_pareto_chart.png) |
| Ternary diagram | `plot(a, b, c, type='ternary')` | [ternary](../docs/images/116_ternary_plot.png) |
| KPI rings | `plot(values, type='rings')` | [rings](../docs/images/117_donut_rings.png) |

---

# Comparison & risk charts (v7.0)

| Chart | Call | Example image |
|---|---|---|
| Dot plot | `plot(labels, values, type='cleveland')` | [dot](../docs/images/118_dot_plot.png) |
| Volcano | `plot(fc, p_values, type='volcano')` | [volcano](../docs/images/119_volcano.png) |
| Confidence ellipses | `plot(x, y, groups=g, type='ellipses')` | [ellipse](../docs/images/120_confidence_ellipse.png) |
| Stacked histogram | `plot(groups, type='stacked_hist')` | [stacked](../docs/images/121_stacked_hist.png) |
| Parameter sweep | `plot(f, params, type='sweep')` | [sweep](../docs/images/122_curve_sweep.png) |
| Phase field | `plot(fx, fy, type='phase_diagram', trajectories=[...])` | [phase](../docs/images/123_phase_field.png) |
| Split violin | `plot(left, right, type='half_violin')` | [violin](../docs/images/124_split_violin.png) |
| Risk matrix | `plot(risks, type='riskmap')` | [risk](../docs/images/125_risk_matrix.png) |

---

# Diagnostics & reporting charts (v8.0)

| Chart | Call | Example image |
|---|---|---|
| Beeswarm | `plot(groups, type='swarm', overlay_box=True)` | [beeswarm](../docs/images/126_beeswarm.png) |
| Control chart | `plot(series, type='spc')` | [spc](../docs/images/127_control_chart.png) |
| Candlestick | `plot(o, h, low, c, type='ohlc')` | [ohlc](../docs/images/128_candlestick.png) |
| Delta band | `plot(x, a, b, type='delta')` | [delta](../docs/images/129_delta_band.png) |

---

# Flow diagrams (v9.0)

| Chart | Call | Example image |
|---|---|---|
| Chord diagram | `plot(matrix, type='chord', labels=[...])` | [chord](../docs/images/130_chord.png) |
| Correlation + stars | `correlation_matrix(df, show_significance=True, n_obs=150)` | [corr](../docs/images/23_correlation.png) |

---

# Distribution & structure charts (v10.0)

| Chart | Call | Example image |
|---|---|---|
| Raincloud | `plot(groups, type='cloud')` | [raincloud](../docs/images/131_raincloud.png) |
| Circle pack | `plot(values, type='packed_circles')` | [pack](../docs/images/132_circle_pack.png) |
| Arc diagram | `plot(nodes, edges, type='arcgraph')` | [arc](../docs/images/133_arc_diagram.png) |
