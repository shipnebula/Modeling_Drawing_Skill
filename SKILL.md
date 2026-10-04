---
name: math-modeling-viz
description: "Publication-quality charts for math modeling competitions. 155+ chart types (incl. chord diagrams, rainclouds, circle packing, arc diagrams, beeswarm, SPC control charts, OHLC candles, delta bands, dot plots, volcano plots, confidence ellipses, curve sweeps, phase fields, risk matrices, joint plots, forest plots, Pareto charts, ternary diagrams, LOESS smoothing, cross-correlation, fit comparison, multi-model ROC, calibration, PCA biplot, KS test, calendar heatmap, bifurcation, cobweb, Monte-Carlo, ACF/PACF, seasonal decomposition, clustermap, 3D surface, contour, vector field, phase portrait, sensitivity, Pareto, ridgeline, sunburst, forecast bands, AHP hierarchy diagrams, calculus visuals, multi-panel Nature-style figures), 36 palettes, 7 styles, GIF export, CLI. Smart auto-detection via universal plot() + FigureFactory. Zero-config CJK support. Use when creating figures for competition papers or any publication-quality visualization."
version: 10.0.0
---

# Math Modeling Viz

Publication-quality charts. One import, one function call, done.

```python
from plot import plot

fig = plot([120, 180, 150], labels=['2021', '2022', '2023'], title='Revenue')
fig.savefig('revenue.png', dpi=300)
```

---

## INSTALLATION

```bash
pip install -r requirements.txt
```

Requires: Python 3.9+, matplotlib>=3.7, numpy>=1.24, pandas>=2.0, scipy>=1.10

Optional: seaborn>=0.12, networkx>=3.0, scikit-learn>=1.3

Headless servers / CI: the library auto-selects the Agg backend when no
display is available (or set `MPLBACKEND=Agg` explicitly).

---

## CLI (mmv)

```bash
mmv plot data.csv --type bar --title "Results" -o output.pdf
mmv plot --data '[10,20,30]' --labels 'A,B,C' -o out.png --dpi 300
mmv types                   # all chart types
mmv palettes                # palettes with color swatches
mmv styles                  # style presets
mmv detect data.csv         # preview auto-detection
```

---

## QUICK REFERENCE FOR LLMs

### Most common patterns

```python
from plot import plot

# 1. Bar chart
plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results')

# 2. Line chart (dict of series)
plot({'Model A': [1,2,3], 'Model B': [4,5,6]}, x=[1,2,3], title='Convergence')

# 3. Scatter with fit line
plot(x, y, type='scatter', show_fit=True, title='Relationship')

# 4. Sensitivity analysis (tornado chart)
plot(
    parameters=['Rate', 'Batch Size', 'Layers', 'Dropout'],
    low_values=[0.88, 0.90, 0.85, 0.80],
    high_values=[0.98, 0.96, 0.94, 0.90],
    type='sensitivity', title='Sensitivity Analysis',
)

# 5. Correlation matrix from DataFrame
plot(df, type='correlation', title='Correlations')

# 6. Dashboard with KPIs
plot([
    {'label': 'Accuracy', 'value': '94%', 'change': '+2%', 'change_dir': 'up', 'progress': 0.94},
    {'label': 'F1', 'value': '0.91', 'change': '+0.03', 'change_dir': 'up', 'progress': 0.91},
], title='Model Performance', type='dashboard')

# 7. Save as PDF (vector, for paper)
fig = plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results')
fig.savefig('results.pdf', format='pdf')

# 8. Batch generate multiple figures
from plot import FigureFactory
f = FigureFactory(style='publication', title_prefix='Figure ')
f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Results')
f.line({'Trend': [1,2,3,4]}, x=[1,2,3,4], title='Growth')
f.save_all('output/', fmt='pdf')

# 9. 3D objective surface (optimization)
plot(X, Y, Z, type='surface', title='Objective Landscape')

# 10. Multi-panel Nature-style figure with (a)(b)(c) labels
from plot import panel_figure
panel_figure([
    {'type': 'bar', 'data': [4, 7, 5], 'labels': ['A', 'B', 'C'], 'title': 'Accuracy'},
    {'type': 'line', 'data': {'M1': [1, 2, 3]}, 'x': [1, 2, 3], 'title': 'Loss'},
    {'type': 'hist', 'data': residuals, 'title': 'Residuals'},
    {'type': 'pie', 'data': [30, 25, 45], 'title': 'Share'},
], ncols=2, suptitle='Figure 1: Overall results')
```

---

## UNIVERSAL FUNCTION: plot()

```python
plot(
    data=None,              # Primary data (list, dict, array, DataFrame, or None)
    *args,                  # Extra positional args (routed to underlying function)
    type=None,              # Chart type alias (e.g. 'bar', 'line', 'scatter')
    title=None,             # Chart title
    labels=None,            # Category labels (list of str)
    x=None,                 # X-axis data
    y=None,                 # Y-axis data
    style=None,             # Style preset (e.g. 'nature', 'dark', 'poster')
    palette=None,           # Color palette (e.g. 'nature_qual', 'viridis', 'ocean')
    figsize=None,           # Figure size (width, height) in inches
    save_path=None,         # File path to save (auto-detects format)
    **kwargs                # Passed to underlying chart function
) -> plt.Figure
```

### How plot() works

1. If `type` is provided, use that chart type
2. If `type` is not provided, auto-detect from data structure:
   - `list` + `labels` → `bar`
   - `dict` of lists → `line` (if `x` provided) or `grouped`
   - `2D array` → `correlation`
   - `DataFrame` → auto-detects best chart type
   - `x` + `y` provided → `scatter`
3. Routes arguments to the correct chart function

### Chart type aliases

Use these short names in `type=`:

| Alias | Full name | Description |
|-------|-----------|-------------|
| `bar` | `bar_chart` | Bar chart |
| `grouped` | `grouped_bar` | Grouped bar |
| `stacked` | `stacked_bar` | Stacked bar |
| `line` | `line_chart` | Line chart |
| `area` | `area_chart` | Area chart |
| `scatter` | `scatter_plot` | Scatter plot |
| `pie` | `pie_chart` | Pie chart |
| `donut` | `donut_chart` | Donut chart |
| `hist` | `histogram` | Histogram |
| `box` | `box_plot` | Box plot |
| `violin` | `violin_plot` | Violin plot |
| `step` | `step_chart` | Step chart |
| `fit` | `fit_curve` | Regression fit |
| `residual` | `residual_plot` | Residual plot |
| `confusion` | `confusion_matrix` | Confusion matrix |
| `roc` | `roc_curve` | ROC curve |
| `learning` | `learning_curve` | Learning curve |
| `sensitivity` | `sensitivity_analysis` | Tornado chart |
| `pareto` | `pareto_front` | Pareto front |
| `validation` | `validation_plot` | Validation plot |
| `importance` | `feature_importance` | Feature importance |
| `cluster` | `clustering_2d` | Clustering |
| `decision` | `decision_boundary` | Decision boundary |
| `correlation` | `correlation_matrix` | Correlation matrix |
| `network` | `network_graph` | Network graph |
| `graph` | `network_graph` | Network graph (alias) |
| `sankey` | `sankey_diagram` | Sankey diagram |
| `radar` | `radar_chart` | Radar chart |
| `waterfall` | `waterfall_chart` | Waterfall |
| `dumbbell` | `dumbbell_plot` | Dumbbell |
| `slope` | `slope_chart` | Slope chart |
| `timeline` | `timeline` | Timeline |
| `parallel` | `parallel_coordinates` | Parallel coordinates |
| `gantt` | `gantt_chart` | Gantt chart |
| `treemap` | `treemap` | Treemap |
| `dashboard` | `dashboard` | Dashboard |
| `kpi` | `kpi_card` | KPI card |
| `bullet` | `bullet_chart` | Bullet chart |
| `spark` | `sparkline` | Sparkline |
| `gauge` | `gauge` | Gauge |
| `flow` | `process_flow` | Process flow |
| `process` | `process_flow` | Process flow (alias) |
| `mind` | `mind_map` | Mind map |
| `compare` | `comparison_bar` | Comparison bar |
| `surface` | `surface3d` | 3-D surface |
| `contour` | `contour_plot` | Filled contour |
| `vector` | `vector_field` | Quiver / streamlines |
| `phase` | `phase_portrait` | Phase portrait |
| `twin` | `twin_axis` | Dual y-axis |
| `band` | `errorband` | Confidence band |
| `heatmap` | `heatmap` | Annotated matrix heatmap |
| `trace` | `optimization_trace` | Optimizer path |
| `polar` | `polar_chart` | Polar / wind rose |
| `loglog` | `loglog_plot` | Log-scale lines |
| `qq` | `qq_plot` | Q-Q plot |
| `ecdf` | `ecdf_plot` | Empirical CDF |
| `ridge` | `ridgeline` | Ridgeline / joyplot |
| `hexbin` | `hexbin_plot` | Hexagonal binning |
| `stem` | `stem_plot` | Stem / lollipop |
| `errorbar` | `errorbar_chart` | Error bars |
| `bubble` | `bubble_chart` | Bubble chart |
| `bump` | `bump_chart` | Rank changes |
| `streamgraph` | `stream_graph` | Stream graph |
| `funnel` | `funnel_chart` | Funnel |
| `waffle` | `waffle_chart` | Waffle grid |
| `pyramid` | `population_pyramid` | Population pyramid |
| `sunburst` | `sunburst_chart` | Sunburst |
| `icicle` | `icicle_chart` | Icicle |
| `mosaic` | `mosaic_plot` | Mosaic / Marimekko |
| `tree` | `dendrogram` | Dendrogram |
| `distpanel` | `distribution_panel` | Distribution panel |
| `pairplot` | `scatter_matrix` | Scatter matrix |
| `panel` | `panel_figure` | Multi-panel figure |
| `integral` | `area_under_curve` | Definite integral |
| `riemann` | `riemann_sum` | Riemann sum |
| `tangent` | `tangent_line` | Tangent line |
| `spline` | `interpolation_comparison` | Interpolation comparison |
| `scatter_3d` | `scatter3d` | 3-D scatter |
| `pr` | `pr_curve` | Precision-recall curve |
| `pred_actual` | `prediction_vs_actual` | Predicted vs actual |
| `regdiag` | `regression_panel` | Regression diagnostics |
| `elbow` | `elbow_plot` | K-means elbow |
| `silhouette` | `silhouette_plot` | Silhouette profile |
| `pca` | `scree_plot` | PCA scree |
| `ttest` | `hypothesis_test` | Hypothesis test |
| `gini` | `lorenz_curve` | Lorenz curve |
| `prediction` | `forecast` | Forecast band |
| `ahp` | `ahp_hierarchy` | AHP hierarchy |
| `palettes` | `palette_preview` | Palette gallery |
| `styles_preview` | `style_preview` | Style comparison |
| `bifurcation` | `bifurcation` | Bifurcation diagram |
| `cobweb` | `cobweb` | Cobweb plot |
| `montecarlo` | `monte_carlo_convergence` | MC convergence |
| `acf` | `acf_pacf` | ACF/PACF correlogram |
| `decomposition` | `seasonal_decomposition` | Seasonal decomposition |
| `cluster_heatmap` | `clustermap` | Clustered heatmap |
| `corr_network` | `correlation_network` | Correlation network |
| `rose` | `polar_bar` | Polar bar / wind rose |
| `cvd` | `cvd_preview` | Colorblind simulation |
| `model_comparison` | `fit_comparison` | Multi-model fit |
| `multi_roc` | `roc_comparison` | Multi-model ROC |
| `reliability` | `calibration_curve` | Calibration curve |
| `lift` | `gain_chart` | Gain / lift |
| `pca_biplot` | `biplot` | PCA biplot |
| `kstest` | `ks_test` | KS test |
| `scenario` | `range_plot` | Scenario ranges |
| `calendar` | `calendar_heatmap` | Calendar heatmap |
| `agreement` | `bland_altman` | Bland-Altman |
| `decision_tree` | `tree_plot` | Decision tree |
| `jointplot` | `joint_plot` | Scatter + marginals |
| `forest` | `forest_plot` | Effect sizes + CI |
| `jitter` | `strip_plot` | Strip plot |
| `lowess` | `smooth_plot` | Robust smoothing |
| `kde_scatter` | `scatter_contour` | Density contours |
| `signed_bar` | `diverging_bar` | Diverging bars |
| `vital_few` | `pareto_chart` | Pareto chart |
| `lead_lag` | `cross_correlation` | Cross-correlation |
| `ternary` | `ternary_plot` | Ternary diagram |
| `rings` | `donut_rings` | KPI progress rings |
| `cleveland` | `dot_plot` | Dot plot |
| `volcano` | `volcano_plot` | Volcano plot |
| `ellipses` | `confidence_ellipse` | Confidence ellipses |
| `stacked_hist` | `stacked_histogram` | Stacked histogram |
| `sweep` | `curve_sweep` | Parameter sweep curves |
| `phase_diagram` | `phase_field` | Phase field + orbits |
| `half_violin` | `split_violin` | Split violin |
| `riskmap` | `risk_matrix` | Risk matrix |
| `swarm` | `beeswarm` | Beeswarm |
| `spc` | `control_chart` | SPC control chart |
| `ohlc` | `candlestick` | Candlestick |
| `delta` | `delta_band` | Difference band |
| `chord` | `chord_chart` | Chord diagram |
| `cloud` | `raincloud` | Raincloud plot |
| `packed_circles` | `circle_pack` | Circle packing |
| `arcgraph` | `arc_diagram` | Arc diagram |

---

## DATA FORMAT GUIDE

How to pass data for each chart type:

### bar / grouped / stacked
```python
plot([10, 20, 30], labels=['A', 'B', 'C'])                    # basic bar
plot({'A': [10,20], 'B': [15,25]}, labels=['X','Y'], type='grouped')  # grouped
plot({'A': [10,20], 'B': [15,25]}, labels=['X','Y'], type='stacked')  # stacked
```

### line / area
```python
plot({'A': [1,2,3], 'B': [4,5,6]}, x=[1,2,3], type='line')    # dict of series
plot([1,2,3], {'A': [4,5,6]}, type='area')                     # list + dict
```

### scatter
```python
plot(x_array, y_array, type='scatter')                         # x + y arrays
```

### pie / donut
```python
plot([30, 25, 20, 15, 10], labels=['A','B','C','D','E'], type='pie')
plot([30, 25, 20, 15, 10], labels=['A','B','C','D','E'], type='donut',
     center_text='Total')
```

### hist / box / violin
```python
import numpy as np
plot(np.random.randn(1000), type='hist')                        # single array
plot([np.random.randn(50), np.random.randn(50)], labels=['A','B'], type='box')  # list of arrays
```

### correlation
```python
import pandas as pd
plot(df, type='correlation')                                     # DataFrame
```

### sensitivity (tornado)
```python
plot(
    parameters=['Rate', 'Batch', 'Layers'],                      # list of str
    low_values=[0.88, 0.90, 0.85],                               # list of float
    high_values=[0.98, 0.96, 0.94],                              # list of float
    type='sensitivity',
)
```

### radar
```python
plot(
    ['Speed', 'Accuracy', 'Cost'],                               # list of str (labels)
    [[4,5,3], [3,4,4]],                                          # list of lists (values)
    names=['System A', 'System B'],                              # list of str
    type='radar',
)
```

### network
```python
plot(nodes_list, edges_list, type='network')                     # nodes + edges
```

### waterfall
```python
plot(
    categories=['Start', '+Rev', '-Cost', 'End'],                # list of str
    values=[100, 50, -30, 120],                                  # list of float
    type='waterfall',
)
```

### dumbbell
```python
plot(
    labels=['A', 'B', 'C'],                                      # list of str
    old_values=[30, 50, 20],                                     # list of float
    new_values=[40, 60, 25],                                     # list of float
    type='dumbbell',
)
```

### slope
```python
plot(
    labels=['A', 'B', 'C'],                                      # list of str
    y1=[80, 60, 40],                                             # list of float
    y2=[70, 50, 45],                                             # list of float
    type='slope',
)
```

### gantt
```python
plot(
    tasks=[
        {'name': 'Task 1', 'start': 0, 'end': 5, 'progress': 1.0},
        {'name': 'Task 2', 'start': 5, 'end': 10, 'progress': 0.5},
    ],
    type='gantt',
)
```

### treemap
```python
plot([30, 25, 20, 15, 10], labels=['A','B','C','D','E'], type='treemap')
```

### dashboard
```python
plot([
    {'label': 'Accuracy', 'value': '94%', 'change': '+2%',
     'change_dir': 'up', 'progress': 0.94},
    {'label': 'F1', 'value': '0.91', 'change': '+0.03',
     'change_dir': 'up', 'progress': 0.91},
], title='Model Performance', type='dashboard', ncols=2)
```

### kpi
```python
plot('Revenue', value='$4.2M', change='+12%',
     change_dir='up', progress=0.84, type='kpi')
```

### gauge
```python
plot(75, min_val=0, max_val=100, label='Progress', type='gauge')
```

### process_flow
```python
plot(['Data', 'Clean', 'Model', 'Validate', 'Deploy'], type='flow')
```

### mind_map
```python
plot('Center', branches=[
    {'label': 'Branch A', 'items': ['Item 1', 'Item 2']},
    {'label': 'Branch B', 'items': ['Item 3', 'Item 4']},
], type='mind')
```

### comparison_bar
```python
plot(['A', 'B', 'C'], [85, 72, 90], target=80, type='compare')
```

### surface / contour (3-D objective)
```python
plot(X, Y, Z, type='surface')                    # 2-D meshgrid arrays
plot(x_1d, y_1d, Z_matrix, type='contour')       # 1-D axes + 2-D Z
plot(Z, type='surface')                          # lone 2-D matrix
```

### vector_field (ODEs / flows)
```python
plot(x, y, u, v, type='vector', mode='both')     # quiver + streamlines
```

### phase_portrait
```python
plot(x_traj, y_traj, type='phase')               # one orbit
plot({'ω=1': (x1, y1), 'ω=2': (x2, y2)}, type='phase')  # several orbits
```

### twin_axis (dual y-axis)
```python
plot(x, y1, y2, type='twin', ylabel1='Temp', ylabel2='Pressure')
```

### errorband (confidence envelope)
```python
plot(x, y, yerr=0.2, type='band')                # scalar/array error
runs = np.random.rand(30, 50)                    # 30 runs × 50 steps
plot(np.arange(50), runs, type='band')           # mean ± std auto
```

### heatmap (generic annotated matrix)
```python
plot(matrix, row_labels=[...], col_labels=[...], type='heatmap')
plot(matrix, type='heatmap', center=0)           # diverging around 0
```

### optimization_trace (gradient descent path)
```python
plot(objective_function, path_points, type='trace')  # path = (n_iter, 2)
```

### polar (wind rose)
```python
plot(theta_deg, {'Speed': radii}, type='polar',
     labels=['N','NE','E','SE','S','SW','W','NW'],
     zero_location='N', clockwise=True)
```

### qq / ecdf / ridgeline (distributions)
```python
plot(sample, type='qq')                          # normality check
plot({'A': arr1, 'B': arr2}, type='ecdf')        # empirical CDF
plot({f'{y}': arr, ...}, type='ridge')           # joyplot
```

### bubble / bump / funnel / pyramid
```python
plot(x, y, sizes, type='bubble')
plot({'Alpha': [1,3,2], 'Beta': [2,1,3]}, type='bump', x_labels=['Q1','Q2','Q3'])
plot(['Raw', 'Valid', 'Modeled'], [5000, 2600, 1400], type='funnel')
plot(age_labels, male_counts, female_counts, type='pyramid')
```

### sunburst / icicle (hierarchy)
```python
plot({'Tech': {'HW': 35, 'SW': 45}, 'Ops': 40}, type='sunburst')
plot({'Total': {'East': {'E1': 20, 'E2': 12}, 'West': 16}}, type='icicle')
```

### user config (v10)
```json
// .mmvrc.json next to your script — auto-loaded at import
{"theme": "colorblind", "dpi": 200, "figsize": [9, 5]}
```
```python
plot(groups_dict, type='cloud')                  # raincloud
plot(values_dict, type='packed_circles')         # circle packing
plot(nodes, edges, type='arcgraph')              # arc diagram
```

### flows & workflow (v9)
```python
M = [[0, 20, 10], [15, 0, 12], [8, 10, 0]]
plot(M, type='chord', labels=['A', 'B', 'C'])    # flow matrix
correlation_matrix(df, show_significance=True, n_obs=150)  # */**/***
mmv init                     # starter recipe.json in cwd
mmv batch specs/ -o out/     # render a directory of recipes
```

### diagnostics & reporting (v8)
```python
plot(groups, type='swarm', overlay_box=True)     # beeswarm
plot(series, type='spc')                         # control chart
plot(o, h, low, c, type='ohlc')                  # candlestick
plot(x, a, b, type='delta', label_a='A', label_b='B')
pdf_report([fig1, fig2], 'appendix.pdf', title='支撑材料')
make_gif(lambda i, n: plot(x, y_array(i)), n_frames=24)
```

### comparison & risk (v7)
```python
plot(labels, values, values2, type='cleveland')  # dot plot (dumbbell variant)
plot(fc, p_values, type='volcano', labels=names) # fold change vs significance
plot(x, y, groups=g, type='ellipses')            # 1sigma/2sigma ellipses
plot(f, param_values, type='sweep', x=x_grid)    # colored curve family
plot(fx, fy, type='phase_diagram', trajectories=[(x0, y0), ...])
plot(left, right, type='half_violin')            # mirrored per category
plot({'risk': (impact, prob), ...}, type='riskmap')
```

### structure & statistics (v6)
```python
plot(x, y, type='jointplot')                     # scatter + marginal hists
plot(labels, est, lo, hi, type='forest')         # effect sizes with CI
plot(groups_dict, type='jitter', overlay_box=True)
plot(x, y, type='lowess', frac=0.3)              # robust trend
plot(x, y, type='kde_scatter', fill=True)
plot(labels, values, type='signed_bar', sort='desc')
plot(labels, counts, type='vital_few')           # Pareto chart
plot(series1, series2, type='lead_lag', max_lag=24)
plot(a, b, c, type='ternary')                    # 3-component mixtures
plot([0.9, 0.7], type='rings')                   # KPI progress rings
apply_theme('colorblind')                        # one-call look
```

### model comparison & statistics (v5)
```python
plot(x, y, type='model_comparison')              # linear/poly/power/exp ranked by R2
plot(y_true, {'LR': s1, 'RF': s2}, type='multi_roc')
plot(y_true, y_prob, type='reliability')         # calibration + Brier
plot(sample1, sample2, type='kstest')            # D-statistic marked
plot(labels, low, mid, high, type='scenario')    # best/base/worst
plot(values, start_date='2025-01-01', type='calendar')
plot(matrix, type='pca_biplot')                  # scores + loadings
plot(m1, m2, type='agreement')                   # Bland-Altman
```

### declarative rendering (v5)
```python
render_spec({'type': 'bar', 'data': [3, 5, 4], 'labels': ['a', 'b', 'c']})
render_spec({'panel': [{...}, ...], 'ncols': 2, 'suptitle': '...'})
# from the shell:  mmv spec recipe.json -o out.png
with use_latex():                                # LaTeX/mathtext titles
    plot(x, y, title=r'$\eta$ vs $\tau$')
```

### dynamics & simulation (v4)
```python
plot(a_range=(2.5, 4.0), type='bifurcation')     # logistic map default
plot(f, x0=0.3, type='cobweb', n=40)             # orbit of x_{n+1}=f(x_n)
plot(samples, type='montecarlo', true_value=3.5) # running mean + CI band
```

### time-series diagnostics (v4)
```python
plot(series, type='acf', nlags=24)               # ACF + PACF pair
plot(series, period=12, type='decomposition')    # trend/seasonal/residual
```

### structure & accessibility (v4)
```python
plot(matrix, type='cluster_heatmap', standardize=True)
plot(data, type='corr_network', threshold=0.3)   # spring layout
cvd_preview('nature_qual')                       # colorblind simulation
colorblind_safe('tol_8')                         # quantitative check
with style('dark'):                              # temporary theme
    fig = plot(data)
export_publication(fig, 'figure1', formats=('png', 'pdf', 'svg'))
```

### forecast (history + prediction band)
```python
plot(history_values, forecast_values, type='prediction', lower=lo, upper=hi)
```

### hypothesis_test / lorenz_curve
```python
plot(sample, type='ttest', mu=0)                 # shaded rejection region
plot(values, type='gini')                        # Lorenz + Gini annotation
```

### elbow / silhouette / scree (model selection)
```python
plot(points_2d, type='elbow')                    # auto-marks the best k
plot(points_2d, cluster_labels, type='silhouette')
plot(feature_matrix, type='pca')                 # cumulative variance
```

### calculus visuals
```python
plot(f_callable, type='integral', a=0, b=2)      # shaded definite integral
plot(x_samples, y_samples, type='integral')      # or from data
plot(f_callable, type='tangent', x0=1.2)
plot(x_samples, y_samples, type='spline')        # linear vs poly vs cubic
```

### ahp_hierarchy (评价类建模)
```python
plot('Goal', ['C1', 'C2', 'C3'], ['AltA', 'AltB'], type='ahp',
     weights=[0.6, 0.4])
```

### panel_figure (Nature-style multi-panel)
```python
from plot import panel_figure
panel_figure(charts, ncols=2, panel_labels='letters', suptitle='Figure 1')
# each chart: {'type': ..., 'data': ..., 'args': [...], 'title': ..., **chart_kwargs}
```

---

## FigureFactory

Batch-generate multiple figures with consistent styling.

```python
f = FigureFactory(
    style='nature',                    # Style preset
    title_prefix='',                   # Prefix for all titles
    palette='nature_qual',             # Color palette
    output_format='png',               # Default save format
    dpi=300,                           # Resolution for raster
)

# Add figures
f.add('bar', [10, 20, 30], labels=['A', 'B', 'C'], title='Sales')
f.add('line', {'A': [1,2,3]}, x=[1,2,3], title='Trend')

# Or use convenience methods
f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Sales')
f.line({'A': [1,2,3]}, x=[1,2,3], title='Trend')
f.scatter(x, y, title='Correlation')
f.radar(labels, values, names=names, title='Comparison')
f.dashboard(metrics, title='Performance')
f.gauge(75, min_val=0, max_val=100, label='Progress', title='Gauge')
f.correlation(df, title='Correlations')
f.sensitivity(params, low, high, title='Sensitivity')

# Save all
f.save_all('output/', fmt='pdf', prefix='figure', close=True)
# Saves: output/figure_01.pdf, output/figure_02.pdf, ...

# Check count
len(f)  # Number of figures
f.figures  # List of Figure objects
```

---

## STYLES

```python
from plot import apply_style

apply_style('nature')        # Clean, minimal, no top/right spines (default)
apply_style('publication')   # Full spines, dashed grid, formal
apply_style('economist')     # Modern editorial, muted colors
apply_style('minimal')       # No axes, ultra clean
apply_style('dark')          # Dark background, bright colors
apply_style('poster')        # Large fonts, thick lines
apply_style('dark_poster')   # Dark mode posters

# Or use with plot()
plot(data, labels=labels, style='dark', title='Results')
```

---

## PALETTES

```python
# Qualitative (categorical)
palette='nature_qual'     # Clean, professional (default)
palette='tol_8'           # Colorblind-safe (Paul Tol)
palette='economist'       # Muted, editorial
palette='ocean'           # Cool blues
palette='sunset'          # Warm tones

# Sequential (ordered)
palette='viridis'         # Perceptually uniform (recommended)
palette='cividis'         # Colorblind-safe sequential
palette='inferno'         # Dark to bright

# Diverging (centered)
palette='coolwarm'        # Blue-white-red (recommended)
palette='spectral'        # Rainbow
palette='RdBu'            # Red-blue

# Theme-specific
palette='data_analysis'   # General analysis
palette='classification'  # Classification models
palette='network'         # Network graphs

# Use with plot()
plot(data, labels=labels, palette='ocean', title='Results')
```

### Manual palette access

```python
from plot import get_palette, auto_colors, sequential_colormap, diverging_colormap

colors = get_palette('nature_qual')           # List of hex colors
colors = auto_colors(5, 'viridis')            # 5 colors from viridis
colors = sequential_colormap('viridis', n=50) # 50 interpolated colors
colors = diverging_colormap('coolwarm', n=50) # 50 diverging colors
```

---

## SAVING FIGURES

```python
# Method 1: matplotlib savefig (preferred)
fig = plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results')
fig.savefig('output.png', dpi=300)
fig.savefig('output.pdf', format='pdf')
fig.savefig('output.svg', format='svg')

# Method 2: save_path parameter
plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results',
     save_path='output.png')

# Method 3: save_figure() function
from plot import save_figure
save_figure(fig, 'output.png', dpi=300)

# Method 4: FigureFactory
f.save_all('output/', fmt='pdf')
```

### Format recommendations

| Format | Use case | Notes |
|--------|----------|-------|
| PDF | Paper submission | Vector, scales to any size |
| SVG | Web, LaTeX | Vector, editable in Illustrator |
| PNG | Slides, quick preview | Raster, 300 DPI minimum |

---

## COMPETITION PAPER GUIDE

### CUMCM (国赛) — Figure placement

| Section | Figures | Chart types |
|---------|---------|-------------|
| 摘要 | 1-2 | `dashboard`, `radar` |
| 问题重述 | 1 | `mind`, `flow` |
| 模型建立 | 2-3 | `network`, `fit` |
| 模型求解 | 2-3 | `line`, `learning` |
| 结果分析 | 4-6 | `bar`, `grouped`, `correlation`, `scatter` |
| 灵敏度分析 | 1-2 | `sensitivity`, `importance` |
| 结论 | 1 | `radar`, `dashboard` |

### MCM/ICM (美赛) — Figure placement

| Section | Figures | Chart types |
|---------|---------|-------------|
| Summary Sheet | 1 | `dashboard` |
| Model Formulation | 1-2 | `network`, `flow` |
| Model Analysis | 4-6 | `bar`, `grouped`, `fit`, `radar`, `scatter` |
| Sensitivity | 1-2 | `sensitivity` |
| Validation | 1-2 | `residual`, `confusion` |
| Conclusion | 1 | `radar`, `dashboard` |

### Style recommendations

- CUMCM papers: `apply_style('nature')` or `apply_style('publication')`
- MCM/ICM papers: `apply_style('publication')`
- Posters: `apply_style('poster')`
- Dark presentations: `apply_style('dark')`

### Palette recommendations

- Papers: `palette='nature_qual'` (default) or `palette='tol_8'` (colorblind-safe)
- Dark mode: `palette='dark_qual'` with `style='dark'`

---

## COMMON TASK → CODE

Quick lookup for common user requests:

| User request | Code |
|--------------|------|
| "Make a bar chart" | `plot([10,20,30], labels=['A','B','C'], title='Results')` |
| "Show the trend" | `plot({'A':[1,2,3]}, x=[1,2,3], title='Trend')` |
| "Plot these two variables" | `plot(x, y, type='scatter', show_fit=True)` |
| "Show the distribution" | `plot(data, type='hist', kde=True)` |
| "Compare distributions" | `plot(data_groups, labels=labels, type='box')` |
| "Show proportions" | `plot([30,25,20,15,10], labels=labels, type='pie')` |
| "Show correlations" | `plot(df, type='correlation')` |
| "Show model fit" | `plot(x, y, type='fit')` |
| "Show residuals" | `plot(y_true, y_pred, type='residual')` |
| "Show classification results" | `plot(y_true, y_pred, type='confusion')` |
| "Show ROC curve" | `plot(y_true, y_score, type='roc')` |
| "Show sensitivity" | `plot(params, low, high, type='sensitivity')` |
| "Show feature importance" | `plot(names, values, type='importance')` |
| "Show the network" | `plot(nodes, edges, type='network')` |
| "Show the flow" | `plot(flows, labels=labels, type='sankey')` |
| "Compare systems" | `plot(labels, values, names=names, type='radar')` |
| "Show cumulative changes" | `plot(cats, vals, type='waterfall')` |
| "Show before/after" | `plot(labels, old, new, type='dumbbell')` |
| "Show ranking changes" | `plot(labels, y1, y2, type='slope')` |
| "Show project schedule" | `plot(tasks, type='gantt')` |
| "Show hierarchy" | `plot(values, labels=labels, type='treemap')` |
| "Show dashboard" | `plot(metrics, type='dashboard')` |
| "Show a KPI" | `plot(label, value=val, change=ch, type='kpi')` |
| "Show a gauge" | `plot(val, min_val=0, max_val=100, type='gauge')` |
| "Show process steps" | `plot(steps, type='flow')` |
| "Show mind map" | `plot(center, branches=branches, type='mind')` |
| "Compare to target" | `plot(labels, vals, target=t, type='compare')` |
| "Plot the objective surface" | `plot(X, Y, Z, type='surface')` |
| "Show the contour map" | `plot(x, y, Z, type='contour', mark_min=True)` |
| "Show the vector field" | `plot(x, y, u, v, type='vector')` |
| "Show the phase portrait" | `plot(x_traj, y_traj, type='phase')` |
| "Compare two scales" | `plot(x, y1, y2, type='twin')` |
| "Show confidence band" | `plot(x, y, yerr=e, type='band')` |
| "Show the optimizer path" | `plot(f, path, type='trace')` |
| "Check normality" | `plot(sample, type='qq')` |
| "Compare distributions" | `plot(groups, type='ridge')` |
| "Show rank changes" | `plot(ranks_dict, type='bump')` |
| "Show the funnel" | `plot(stages, values, type='funnel')` |
| "Show hierarchy" | `plot(tree_dict, type='sunburst')` |
| "Cluster my data" | `plot(points_2d, type='cluster')` |
| "Combine into one figure" | `panel_figure([...], ncols=2)` |
| "Make it look professional" | `apply_style('nature')` |
| "Make it dark mode" | `apply_style('dark')` |
| "Colorblind safe" | `palette='tol_8'` |
| "Save for paper" | `fig.savefig('output.pdf', format='pdf')` |
| "Save all figures" | `FigureFactory(...).save_all('output/')` |
| "Plot from a CSV file" | `mmv plot data.csv -t bar -o out.pdf` |
| "Forecast the trend" | `plot(history, predicted, type='prediction', lower=lo, upper=hi)` |
| "Which k for clustering" | `plot(points, type='elbow')` |
| "Shade the integral" | `plot(f, type='integral', a=0, b=2)` |
| "AHP 结构图画出来" | `plot('目标', ['指标1','指标2'], ['方案A','方案B'], type='ahp', weights=[...])` |
| "Show all palettes" | `palette_preview()` |
| "Make an animation" | `save_gif(figures, 'demo.gif', fps=8)` |

---

## ERROR RECOVERY

### "Unknown chart type"
```python
from plot import list_chart_types
print(list_chart_types())  # See all available types (190+ aliases)
# Typos also return suggestions, e.g. type='barr' → "Did you mean: 'bar'?"
```

### "Backend/display errors on a server"
The library auto-selects the Agg backend when no display exists. To force it:
```bash
export MPLBACKEND=Agg
```

### "Figure looks ugly"
```python
apply_style('nature')      # Clean, minimal
apply_style('publication') # Formal
apply_style('economist')   # Modern editorial
```

### "Colors don't look right"
```python
plot(data, labels=labels, palette='nature_qual')   # Default
plot(data, labels=labels, palette='tol_8')         # Colorblind-safe
plot(data, labels=labels, palette='ocean')         # Cool blues
```

### "CJK characters not rendering"
v3.0 auto-detects installed CJK fonts (SimHei, Microsoft YaHei, PingFang,
Noto Sans CJK, Malgun Gothic…) on import and applies them. If glyphs are
still missing, install a font:
- Windows: SimHei (usually pre-installed)
- macOS: PingFang (usually pre-installed)
- Linux: `apt install fonts-noto-cjk`
Then call `from plot import apply_style; apply_style('nature')` to re-scan,
or `from plot.styles import setup_cjk; setup_cjk()`.

### "Figure is too small/large"
```python
plot(data, labels=labels, figsize=(10, 6))  # Custom size
```

### "Save fails"
```python
import os
os.makedirs('output', exist_ok=True)
fig.savefig('output/figure.png')
```

### "Tight layout warning"
This is a known warning for some charts (e.g. treemap). It's harmless — the figure still saves correctly.

---

## FUNCTION SIGNATURES

### plot()
```python
plot(data=None, *args, type=None, title=None, labels=None,
     x=None, y=None, style=None, palette=None, figsize=None,
     save_path=None, **kwargs) -> plt.Figure
```

### FigureFactory
```python
FigureFactory(style='nature', title_prefix='', palette='nature_qual',
              output_format='png', dpi=300)
.add(chart_type, data, title=None, **kwargs) -> plt.Figure
.save_all(output_dir, fmt=None, prefix='figure', close=True) -> list[str]
```

### apply_style()
```python
apply_style(name: str) -> dict
# name: 'nature', 'publication', 'economist', 'minimal', 'dark', 'poster', 'dark_poster'
```

### save_figure()
```python
save_figure(fig, path, fmt=None, dpi=300, close=True)
# fmt: 'png', 'pdf', 'svg' (auto-detected from path if None)
```

### get_palette()
```python
get_palette(name: str) -> list[str]
# Returns list of hex color strings
```

### auto_colors()
```python
auto_colors(n: int, palette: str = 'nature_qual') -> list[str]
# Returns n colors from palette
```

### format_numbers()
```python
format_numbers(value, style='smart', decimals=2) -> str
# style: 'smart', 'thousands', 'decimal', 'percent', 'scientific'
```

### list_chart_types()
```python
list_chart_types() -> list[str]
# Returns all available chart type names (aliases + canonical)
```

---

## REFERENCES

- [Chart catalog](references/chart-catalog.md) — every chart with examples
- [Color palettes](references/color-palettes.md) — palette selection guide
- [Competition strategy](references/competition-strategy.md) — CUMCM/MCM figure plans
- [Typography guide](references/typography-guide.md) — fonts and formatting
- [API reference](docs/api-reference.md) — full function documentation
- [Usage guide](docs/usage-guide.md) — common patterns