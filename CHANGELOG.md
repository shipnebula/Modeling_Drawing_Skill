# Changelog

All notable changes to this project.

## [10.0.0] - 2026-10-04

### Added
- **3 new chart functions** (155+ charts, 420+ aliases total):
  - `raincloud` — half violin + thin box + jittered raw points per
    category; the most information-dense distribution figure
  - `circle_pack` — part-to-whole bubbles with area proportional to
    value (front-of-center greedy packing)
  - `arc_diagram` — nodes on a baseline, weighted arcs above; reads
    naturally for sequences (pipeline hand-offs, co-occurrence)
- **Project-local defaults** — `.mmvrc.json` (cwd or home) auto-loads at
  import: `theme`, `style`, `palette`, `dpi`, `figsize`. Explicit
  `load_config(path)` also exported.
- **GitHub Pages publishing** — `.github/workflows/docs.yml` rebuilds
  the gallery and deploys the MkDocs site on every push to main.
- Benchmark extended to 26 representative charts.

## [9.0.0] - 2026-10-04

### Added
- **`chord_chart`** — the classic chord diagram for square flow
  matrices: node arcs sized by total flow, Bezier ribbons anchored at
  per-flow arc segments (the last iconic missing chart type).
- **Significance stars** — `correlation_matrix(..., show_significance=True,
  n_obs=N)` annotates cells with */**/*** from the two-sided t
  approximation.
- **Workflow CLI** — `mmv init` writes a starter recipe.json (panel +
  sensitivity + correlation examples); `mmv batch specs/ -o out/`
  renders a whole directory of JSON recipes.
- **MkDocs Material documentation site** — `mkdocs.yml` + docs index +
  gallery page; `mkdocs serve` serves the full documentation locally.
- **Contributor template** — `docs/chart-template.py`: copy-paste
  starter that documents the chart-function contract.

## [8.0.0] - 2026-10-04

### Added
- **4 new chart functions** (145+ charts, 420+ aliases total):
  - `beeswarm` — non-overlapping categorical points (greedy circle
    dodging), optional box overlay
  - `control_chart` — SPC chart with CL/UCL/LCL, warning zones, and
    out-of-control point flagging
  - `candlestick` — OHLC candles
  - `delta_band` — two-series difference shading with max-gap annotation
- **`pdf_report(figures, filename)`** — multi-page PDF with cover page,
  per-page captions, and page numbers: the one-call competition-paper
  appendix builder (CUMCM 支撑材料).
- **`make_gif(frame_fn, n_frames)`** — GIF from a frame-drawing function;
  the README banner animation is generated with it
  (`examples/banner_gif.py`).
- **`scatter_matrix` groups** — points and diagonal distributions
  colored by group with a legend.

## [7.0.0] - 2026-10-03

### Added
- **8 new chart functions** (140+ charts, 395 aliases total):
  - `dot_plot` — Cleveland dot plot; two-series form acts as a dumbbell
  - `volcano_plot` — log fold-change vs significance with up/down
    coloring, threshold guides, and top-item labels (raw ratios are
    log2-transformed automatically)
  - `confidence_ellipse` — 1-sigma/2-sigma bivariate ellipses per group
    with centroid markers
  - `stacked_histogram` — 'stacked' / 'overlay' / 'step' multi-group modes
  - `curve_sweep` — parameter-family curves colored by a shared colormap
    with colorbar
  - `phase_field` — streamplot of the ODE right-hand side + integrated
    trajectories (solve_ivp) + fixed-point markers; the definitive
    dynamical-systems figure
  - `split_violin` — mirrored half violins per category with inner boxes
  - `risk_matrix` — probability x impact grid with green-to-red
    background and labeled items
- **FigureFactory context manager** — `with FigureFactory(auto_save_dir=...) as f:`
  auto-saves all figures on exit; on exception figures are closed.
- **`mmv doctor`** — environment health check: core/optional dependency
  versions, backend, installed CJK fonts, chart-registry size.
- Benchmark extended to 23 representative charts.

## [6.0.0] - 2026-10-03

### Added
- **10 new chart functions** (130+ charts, 360+ aliases total):
  - `joint_plot` — scatter with marginal histograms/KDE (jointplot style)
  - `forest_plot` — effect estimates with CIs, pooled line (meta-analysis style)
  - `strip_plot` — jittered categorical points with optional box overlay
  - `smooth_plot` — LOESS / Savitzky-Golay / moving-average trend overlay
    (statsmodels used when present, scipy fallback otherwise)
  - `scatter_contour` — scatter + kernel-density contours
  - `diverging_bar` — signed bars around a zero line
  - `pareto_chart` — descending frequency bars + cumulative-% line with
    the 80% "vital few" guide (distinct from `pareto_front`)
  - `cross_correlation` — lead/lag CCF plot with best-lag highlight
  - `ternary_plot` — three-component composition diagram with groups
  - `donut_rings` — concentric KPI progress rings
- **Theme presets** — `apply_theme()` / `list_themes()`: 11 curated
  style + palette bundles including accessibility-first (`colorblind`,
  `colorblind_dark`) and presentation (`dark`) looks.
- **Browsable gallery** — `docs/gallery.html` regenerates with the images
  (lazy-loading card grid).
- **`mmv bench`** — render-time benchmark from the CLI.
- **PyPI publish workflow** — trusted-publishing on GitHub releases.

### Fixed
- `network_graph` crashed with a NameError when `edge_labels` was used
  (undefined `e_labels` name).
- Ternary-diagram grid lines extended beyond the triangle; now drawn
  edge-to-edge in the three proper families.

### Removed
- 100+ unused imports across all modules (pyflakes-driven hygiene pass).

## [5.0.0] - 2026-10-03

### Added
- **11 new chart functions** (115+ charts, 334 aliases total):
  - `fit_comparison` — linear / quadratic / cubic / power / exponential /
    logarithmic fits on one axes, ranked by R², fitted equations in the
    legend, best-model callout
  - `roc_comparison` — multi-model ROC overlay with AUC ranking table
  - `calibration_curve` — reliability diagram with Brier score and
    prediction-density histogram
  - `gain_chart` — cumulative gain + lift twin axis (lift@20% annotated)
  - `tree_plot` — publication-styled sklearn decision-tree diagram
  - `biplot` — PCA scores + loading arrows with variance labels
  - `ks_test` — two-sample ECDFs with the D-statistic marked at argmax
  - `range_plot` — best/base/worst scenario intervals per option
  - `calendar_heatmap` — GitHub-style daily heatmap (weekday rows,
    month columns)
  - `grouped_scatter` — per-group regression lines with R²
  - `bland_altman` — method agreement with bias + limits of agreement
- **Declarative rendering** — `render_spec()` / `render_specs()` render
  figures from JSON-safe dict recipes; `mmv spec recipe.json` from the
  shell. Single charts and multi-panel layouts both supported.
- **`use_latex()`** context manager — real LaTeX when installed,
  mathtext fallback otherwise.
- **`examples/benchmark.py`** — render-time table for 18 representative
  charts (regression tripwire for performance work).

### Fixed
- `plot(..., save_path=...)` closed the returned figure (double-save
  path: chart fn saved and closed, then plot() saved again). Saving now
  happens exactly once at the plot() level and the returned Figure
  stays open and reusable.
- `tree_plot` passed a float fontsize rejected by newer scikit-learn.

## [4.0.0] - 2026-10-02

### Added
- **10 new chart functions** (100+ charts, 290+ aliases total):
  - `dynamics` module — `bifurcation` (period doubling into chaos, with
    parameter guides), `cobweb` (orbits of iterative maps with fixed points),
    `monte_carlo_convergence` (running mean + shrinking CI band)
  - `timeseries` module — `acf_pacf` (correlogram pair with significance
    band; Durbin-Levinson PACF in pure numpy, no statsmodels),
    `seasonal_decomposition` (classical additive/multiplicative 4-panel)
  - `clustermap` (hierarchical clustering heatmap with dendrograms),
    `correlation_network` (temperature-cooled Fruchterman-Reingold spring
    layout, red/blue signed edges), `polar_bar` (wind-rose bars, grouped
    sectors, compass orientation)
  - `cvd_preview` (palette under protanopia/deuteranopia/tritanopia
    simulations, Machado et al. 2009 transforms) and `colorblind_safe`
    (quantitative pairwise-separation check)
- **`style()` context manager** — temporary style switch with automatic
  restore (`with style("dark"): ...`).
- **`export_publication(fig, name, formats=("png", "pdf", "svg"))`** —
  one-call multi-format export.
- **`mmv preview <type>`** — instant demo render of any chart type, with
  curated demo data for 60+ types.
- PEP 562 lazy loading for all chart modules.

### Fixed
- `neon` and `tol_8` palettes contained duplicate colors (caught by the
  new `colorblind_safe` check); deduped with distinct replacements.
- `seasonal_decomposition` even-period moving-average padding was
  off by one period (shape mismatch / misaligned trend).
- Correlation-network spring layout collapsed all nodes to a point;
  rewritten with a correct temperature-cooled Fruchterman-Reingold.

### Performance
- **`import plot` is 3x faster** (1.25 s to 0.40 s): chart functions are
  now lazy-loaded via PEP 562 module `__getattr__`; only palette,
  styles, and factory load eagerly. Chart modules import on first use.

### Removed
- Generated artifacts (`figures/`, `__pycache__`) from the tree; added
  to `.gitignore`.

## [3.0.0] - 2026-10-02

### Added
- **18 new chart functions** (85+ charts, 250+ aliases total):
  - `calculus` module — `area_under_curve`, `riemann_sum`, `tangent_line`,
    `interpolation_comparison` (linear vs polynomial vs cubic spline)
  - ML evaluation in `model` — `pr_curve`, `prediction_vs_actual`,
    `regression_panel` (R-style 4-panel OLS diagnostics), `elbow_plot`
    (auto-marks the elbow k + silhouette overlay), `silhouette_plot`,
    `scree_plot` (PCA cumulative variance with threshold annotation)
  - `statistics` — `hypothesis_test` (shaded rejection region + p-value),
    `lorenz_curve` (Gini coefficient), `forecast` (history + prediction +
    confidence band, the standard prediction-paper figure)
  - `advanced` — `ahp_hierarchy` (层次分析法结构图 for evaluation papers)
  - `sciences` — `scatter3d` (grouped or z-colored)
  - `showcase` — `palette_preview` (every palette in one figure),
    `style_preview` (same chart in all 7 styles), `save_gif` (figure
    sequence → animated GIF, Pillow-only)
- **Zero-config CJK**: installed CJK fonts (SimHei, Microsoft YaHei,
  PingFang, Noto Sans CJK, Malgun Gothic…) are scanned once and applied
  automatically by every `apply_style()` call; `axes.unicode_minus` fixed.
- Six new palettes: `morandi` (莫兰迪), `brewer_set2`, `brewer_dark2`,
  `finance`, `vivid_dark` (36 palettes total).
- `py.typed` marker — public API ships type hints.
- `FigureFactory` resolves any chart alias as a method via `__getattr__`
  (`f.qq(...)`, `f.ridgeline(...)`, `f.surface(...)`, `f.ahp(...)`).
- CLI gained `styles` subcommand, exit-code contract, and multi-format
  data loading (CSV/TSV/JSON/XLSX/NPY).

### Removed
- `scripts/render.py` legacy CLI (superseded by `mmv` / `python -m plot.cli`).
- `examples/generate_examples.py` + `examples_output/` (superseded by
  `examples/gallery.py` + `docs/images/`).

### Fixed
- CJK support was documented but never implemented — font auto-detection
  now actually works (glyph warnings are gone for Chinese labels).
- `setup_cjk` initially removed fonts without re-inserting them.
- `treemap` layout was broken (areas never normalized to the canvas →
  giant deformed rectangles); rewritten with the proper squarified
  algorithm and correct label/color mapping.
- `plot()`'s `labels` argument was silently dropped for most chart types;
  it is now forwarded to every chart that accepts it.
- AHP weight annotations clipped at the figure edge; style-preview dark
  panels rendered white; forecast split marker placement.

### Performance
- `get_palette()` results cached (lru_cache) — hot path for every chart.
- `heatmap` auto-disables cell annotations above 2500 cells (with a
  warning) instead of drawing tens of thousands of text objects.
- Friendly `ValueError` with guidance when `plot()` is called without data.

## [2.0.0] - 2026-10-02

### Added
- **29 new chart types** (now 70+ total, 190+ aliases):
  - `sciences` module — `surface3d`, `contour_plot`, `vector_field`, `phase_portrait`,
    `twin_axis`, `errorband`, `heatmap`, `optimization_trace`, `polar_chart`, `loglog_plot`
  - `statistics` module — `qq_plot`, `ecdf_plot`, `ridgeline`, `hexbin_plot`, `stem_plot`,
    `errorbar_chart`, `bubble_chart`, `bump_chart`, `stream_graph`, `funnel_chart`,
    `waffle_chart`, `population_pyramid`, `sunburst_chart`, `icicle_chart`, `mosaic_plot`,
    `dendrogram`, `distribution_panel`, `scatter_matrix`
- **`panel_figure()`** — Nature-style multi-panel composite figures with automatic
  (a)(b)(c) labels; supports polar subplots via spec dicts.
- **`mmv` CLI** (`plot/cli.py`) — render charts from CSV/JSON/XLSX files,
  browse chart types, palettes (with ANSI swatches), and preview auto-detection.
- **Smart auto-detection** — `{'A': 1}` dicts now render as bar charts,
  `(x, y)` tuple lists as scatter, and DataFrames choose bar/line/grouped/correlation
  based on column composition.
- **`confusion_matrix`** accepts precomputed matrices and a `class_names` alias.
- **`clustering_2d`** auto-runs K-Means when labels are omitted.
- **`sankey_diagram`** accepts string node names.
- **`parallel_coordinates`** accepts `{name: values}` dicts with legends.
- **`bullet_chart`** supports multi-row bullet lists.
- **`pareto_front`** accepts two 1-D arrays and draws the non-dominated front line.
- **`polar_chart`** gained `zero_location` / `clockwise` for true wind roses.
- Gallery of 70 rendered examples in `docs/images/`, regenerated by
  `examples/gallery.py`; gallery CI job catches visual regressions.
- GitHub Actions CI (3 OS × Python 3.9–3.13), issue/PR templates, `CITATION.cff`,
  `FUNDING.yml`, `.gitignore`.
- Six new palettes: `morandi` (莫兰迪, popular for CUMCM), `brewer_set2`,
  `brewer_dark2`, `finance` (up/down semantics), `vivid_dark` (dark mode), and
  ColorBrewer-derived qualitative sets (36 palettes total).
- `py.typed` marker — the public API ships type hints for mypy/pyright users.
- `FigureFactory` now resolves ANY chart alias as a method
  (`f.qq(...)`, `f.ridgeline(...)`, `f.surface(...)`) via `__getattr__`.
- Bilingual README (English + 中文) with full gallery and self-rendered banner.

### Fixed
- **`plot(x, y, type='scatter')` and all xy-routed charts** plotted x against x —
  the second positional argument was silently dropped (also affected `fit`,
  `roc`, `confusion`, `step`, `learning` via `plot()`).
- **`residual_plot` via `plot(y_true, y_pred, type='residual')`** was broken
  (signature needs three arguments; index is now used for x).
- `render.py` CLI crashed on `--figsize` parsing and a bogus import; legacy
  entry now delegates to `plot.cli`.
- Console-script entry point in `pyproject.toml` pointed at a non-package module.
- Auto-detection dead branch: wide all-numeric DataFrames now actually reach
  the correlation path.
- Ridgeline figures no longer reserve a large empty area; funnel connectors
  render as proper trapezoids; icicle text contrast and row depth fixed.
- Deprecation: box/violin `vert=` replaced with orientation-compatible kwargs
  (matplotlib 3.11+).

### Performance
- Min/max decimation above 20 000 points per line (~10× faster large line
  charts, visually identical).
- Vectorized colormap interpolation in `palette.py`.
- `apply_style` caches the last-applied preset (no-op on repeats).
- Headless environments auto-select the Agg backend before figure creation.

### Changed
- Version bumped to 2.0.0 (breaking: second positional argument of
  `pareto_front` is now `y_values` instead of `labels` — pass `labels=` by name).

## [1.1.0] - 2025-01-15

### Added
- **`plot()` universal function** — one function for everything. Auto-detects chart type from data structure.
- **`FigureFactory` class** — batch generate multiple figures with consistent styling. Auto-numbered saves.
- **Chart type aliases** — use short names like `type='bar'` instead of `type='bar_chart'`.
- **Auto-detection from DataFrame** — pass a pandas DataFrame and it picks the best chart type.
- **`list_chart_types()`** — returns all available chart type names.

### Changed
- Version bumped to 1.1.0
- `__init__.py` exports `plot()`, `FigureFactory`, `list_chart_types`

## [1.0.0] - 2025-01-14

### Added
- Initial release
- 40+ chart types across 4 categories (basic, model, advanced, infographic)
- 30+ color palettes (qualitative, sequential, diverging, theme)
- 7 style presets (nature, publication, economist, minimal, dark, poster, dark_poster)
- CLI renderer (`scripts/render.py`)
- 50+ unit tests
- 33 example figures (SVG + PDF)
- Competition strategy guides for CUMCM and MCM/ICM

### Fixed
- Figure memory leaks — `save_figure()` now closes figures by default
- `_seq`/`_div` used before definition in palette.py
- `axis_config` boolean check bug
- `correlation_matrix` double figure creation
- `validation_plot` undefined palette variable
- `_rgb_to_hex` float→int cast
- `sequential_colormap`/`diverging_colormap` hex iteration
- `confusion_matrix` numpy int vs Python int key mismatch
- `network_graph` unsupported `zorder` kwarg
- `line_chart` single series detection
- `pie_chart`/`donut_chart` kwargs forwarding
- `violin_plot` deprecated `horizontal` parameter
- `format_numbers` integer K/M suffix
- `auto_layout` h_pad/w_pad parameter names
- `apply_style` invalid rcParam
- `kpi_card` title forwarding

---

## Unreleased

### Ideas
- More chart type aliases
- Auto-title generation from data
- More theme palettes
- LaTeX export
- Interactive mode (plotly backend)
- Template gallery