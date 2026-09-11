# math-modeling-viz

One import, one function call, publication-quality charts. Built for math modeling competition papers.

```python
from plot import plot

fig = plot([120, 180, 150], labels=['2021', '2022', '2023'], title='Revenue')
fig.savefig('revenue.png', dpi=300)
```

That's the whole setup. No rcParams, no copy-paste from Stack Overflow, no 30-line helper functions.

---

## Why this exists

I spent 47 minutes once trying to get a bar chart to look like it belonged in a paper. Not a fancy chart. A *bar chart*. The fight was with rcParams, font sizes, and that one spine that kept disappearing.

Math modeling papers need good figures. Good figures need clean typography, professional colors, and proper spacing. Getting matplotlib to produce any of these usually means either:

- Spending hours googling rcParams
- Copy-pasting code from Stack Overflow and hoping it works with your matplotlib version
- Accepting output that looks like it came from 2005

So I built this. One library that gives you publication-quality charts with one function call.

## Quick start

```bash
# Install
git clone https://github.com/yourname/math-modeling-viz.git
cd math-modeling-viz
pip install -r requirements.txt
```

```python
from plot import plot

# Bar chart — auto-detected
plot([120, 180, 150, 210], labels=['2021', '2022', '2023', '2024'], title='Revenue')

# Line chart with multiple series
plot({'Model A': [10, 12, 15, 18], 'Model B': [8, 11, 14, 17]}, x=[1, 2, 3, 4], title='Convergence')

# Scatter with regression line
import numpy as np
x = np.random.randn(50)
y = x * 2 + np.random.randn(50)
plot(x, y, type='scatter', show_fit=True, title='Relationship')

# Sensitivity analysis (tornado chart)
plot(
    parameters=['Rate', 'Batch Size', 'Layers', 'Dropout'],
    low_values=[0.88, 0.90, 0.85, 0.80],
    high_values=[0.98, 0.96, 0.94, 0.90],
    title='Sensitivity Analysis',
    type='sensitivity',
)

# Dashboard with KPIs
plot([
    {'label': 'Accuracy', 'value': '94.2%', 'change': '+2.3%', 'change_dir': 'up'},
    {'label': 'F1 Score', 'value': '0.91', 'change': '+0.03', 'change_dir': 'up'},
], title='Model Performance', type='dashboard')

# Save as PDF (vector)
fig = plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results')
fig.savefig('results.pdf', format='pdf')
```

### Or use `FigureFactory` for batch generation

```python
from plot import FigureFactory

f = FigureFactory(style='publication', title_prefix='Q1 Report: ')

f.bar([120, 180, 150], labels=['Jan', 'Feb', 'Mar'], title='Monthly Revenue')
f.line({'Revenue': [1, 2, 3, 4]}, x=[1, 2, 3, 4], title='Growth Trend')
f.scatter(x, y, title='Correlation')
f.radar(
    ['Speed', 'Accuracy', 'Cost', 'Reliability'],
    [[4, 5, 3, 4], [3, 4, 4, 5]],
    names=['System A', 'System B'],
    title='Comparison',
)

f.save_all('output/')  # Saves all as figure_01.png, figure_02.png, etc.
```

## For LLMs

If you're an AI assistant using this library, read [SKILL.md](SKILL.md) — it's the primary reference, self-contained, with exact function signatures, data format guides, task→code mappings, and error recovery. It's designed to be parsed by LLMs.

Key things to know:
- `plot()` is the universal entry point — auto-detects chart type from data
- `type=` accepts short aliases: `'bar'`, `'line'`, `'scatter'`, `'pie'`, `'hist'`, `'correlation'`, `'sensitivity'`, `'dashboard'`, etc.
- `FigureFactory` for batch generation with consistent styling
- Save with `fig.savefig('output.pdf', format='pdf')` for papers
- CJK characters work out of the box

## What you get

**40+ chart types** across 4 categories:

| Category | Charts |
|----------|--------|
| Basic statistics | Bar, grouped bar, stacked bar, line, area, scatter, pie, donut, histogram, box, violin, step |
| Model analysis | Fit curve, residual, confusion matrix, ROC, learning curve, sensitivity, Pareto, validation, feature importance, clustering, decision boundary, correlation matrix |
| Advanced | Network graph, Sankey, radar, waterfall, dumbbell, slope, timeline, parallel coordinates, Gantt, treemap |
| Infographics | Dashboard, KPI card, bullet chart, sparkline, gauge, process flow, mind map, comparison bar |

**30+ color palettes**: nature journal colors, colorblind-safe (Paul Tol), Economist style, ocean, sunset, viridis, cividis, and more.

**7 style presets**: nature, publication, economist, minimal, dark, poster, dark_poster. One-liner to switch.

**Auto-detection**: pass data, it figures out what chart to draw. Or force a type with `type='bar'`.

**CJK support**: renders Chinese, Japanese, and Korean characters properly.

**300 DPI output**: PNG, SVG, and PDF. Vector formats for publication.

## Examples

All 33 example figures are in [examples_output/](examples_output/) as both SVG and PDF. Run `python examples/generate_examples.py` to regenerate them.

## For math modeling papers

### CUMCM (国赛)

Put these in your paper:

| Section | Figures |
|---------|---------|
| 摘要 | 1 dashboard or radar chart |
| 模型建立 | 1-2 network graphs or fit curves |
| 结果分析 | 2-3 grouped bars, correlation matrices |
| 灵敏度分析 | 1 sensitivity analysis (tornado) |
| 结论 | 1 radar or dashboard |

### MCM/ICM (美赛)

| Section | Figures |
|---------|---------|
| Summary Sheet | 1 dashboard |
| Model Analysis | 3-4 (grouped bar, fit curve, radar, scatter) |
| Sensitivity | 1 tornado chart |
| Validation | 1-2 (residual plot, confusion matrix) |

See [competition strategy](references/competition-strategy.md) for detailed guidance.

## Chart types at a glance

```python
# Basic
plot([10, 20, 30], labels=['A', 'B', 'C'], title='Bar')
plot([10, 20, 30], labels=['A', 'B', 'C'], type='pie', title='Pie')
plot({'A': [1,2,3], 'B': [4,5,6]}, x=[1,2,3], type='line', title='Line')
plot(x, y, type='scatter', title='Scatter')
plot(np.random.randn(1000), type='hist', title='Histogram')
plot(data_groups, labels=['A','B','C'], type='box', title='Box')

# Model
plot(df, type='correlation', title='Correlation')
plot(y_true, y_pred, type='confusion', title='Confusion')
plot(y_true, y_score, type='roc', title='ROC')
plot(params, low_vals, high_vals, type='sensitivity', title='Sensitivity')
plot(names, values, type='feature_importance', title='Feature Importance')

# Advanced
plot(nodes, edges, type='network', title='Network')
plot(flows, labels=labels, type='sankey', title='Sankey')
plot(labels, values, names=names, type='radar', title='Radar')
plot(categories, values, type='waterfall', title='Waterfall')
plot(tasks, type='gantt', title='Gantt')
plot(values, labels=labels, type='treemap', title='Treemap')

# Infographic
plot(metrics, type='dashboard', title='Dashboard')
plot(value, label=label, type='gauge', title='Gauge')
plot(steps, type='flow', title='Process Flow')
plot(center, branches, type='mind', title='Mind Map')
```

## CLI

```bash
# List available chart types
python scripts/render.py --list-charts

# List available palettes
python scripts/render.py --list-palettes

# Generate a chart from CLI
python scripts/render.py --chart bar --data '[10,20,30]' --labels 'A,B,C' \
    --title 'Results' --output 'output.png'
```

## Project structure

```
scripts/plot/
├── __init__.py         # Main API
├── factory.py          # plot() + FigureFactory (the easy way)
├── palette.py          # Color palettes
├── styles.py           # Style presets
├── utils.py            # Helpers
├── basic.py            # Bar, line, scatter, pie, etc.
├── model.py            # Fit curve, ROC, confusion matrix, etc.
├── advanced.py         # Network, Sankey, radar, etc.
└── infographic.py      # Dashboard, gauge, mind map, etc.
```

## Documentation

- [Chart catalog](references/chart-catalog.md) — every chart with examples
- [Color palettes](references/color-palettes.md) — how to pick the right one
- [Competition strategy](references/competition-strategy.md) — CUMCM/MCM figure plans
- [Typography guide](references/typography-guide.md) — fonts, sizes, formatting
- [API reference](docs/api-reference.md) — full function documentation
- [Usage guide](docs/usage-guide.md) — common patterns

## Development

```bash
make test       # Run tests
make examples   # Generate example figures
make verify     # Test + examples
```

## Contributing

Contributions welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

Ways to help:
- Report bugs
- Add new chart types
- Add new palettes
- Improve documentation
- Add tests

## License

MIT — do whatever you want, just don't claim it's yours.