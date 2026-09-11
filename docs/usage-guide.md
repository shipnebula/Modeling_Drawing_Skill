# Usage Guide

Common patterns and tips.

---

## The two ways to use this library

### Way 1: `plot()` — the easy way

One function. Pass data. Get a chart.

```python
from plot import plot

# It auto-detects the chart type
fig = plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results')

# Or force a type
fig = plot(x, y, type='scatter', title='Relationship')

# With styling
fig = plot(data, labels=labels, style='dark', palette='ocean')
```

### Way 2: Specific functions — the explicit way

```python
from plot import bar_chart, line_chart, sensitivity_analysis

fig = bar_chart([10, 20, 30], labels=['A', 'B', 'C'], title='Results')
fig = line_chart(x, y_series, markers=True, title='Trend')
fig = sensitivity_analysis(parameters, low_values, high_values)
```

Both work. `plot()` is simpler. Specific functions give you more control.

---

## Common patterns

### 1. One-off chart

```python
from plot import plot

fig = plot([120, 180, 150], labels=['2021', '2022', '2023'],
           title='Revenue', ylabel='Revenue (M)')
fig.savefig('revenue.png', dpi=300)
```

### 2. Multiple charts in a script

```python
from plot import apply_style, plot

apply_style('nature')

# Figure 1
plot([10, 20, 30], labels=['A', 'B', 'C'], title='Figure 1: Results')

# Figure 2
plot({'Model A': [1,2,3], 'Model B': [4,5,6]},
     x=[1,2,3], title='Figure 2: Convergence')
```

### 3. Batch generation with FigureFactory

```python
from plot import FigureFactory

f = FigureFactory(style='publication', title_prefix='Q1 Report: ')

f.bar([120, 180, 150], labels=['Jan', 'Feb', 'Mar'], title='Revenue')
f.line({'Revenue': [1, 2, 3, 4]}, x=[1, 2, 3, 4], title='Growth')
f.scatter(x, y, title='Correlation')
f.radar(
    ['Speed', 'Accuracy', 'Cost', 'Reliability'],
    [[4, 5, 3, 4], [3, 4, 4, 5]],
    names=['A', 'B'],
    title='Comparison',
)

f.save_all('output/')
```

### 4. Custom styling

```python
from plot import apply_style, plot

# Switch styles
apply_style('economist')
fig = plot(data, labels=labels, title='Results')

# Change palette
fig = plot(data, labels=labels, palette='ocean', title='Results')

# Dark mode
apply_style('dark')
fig = plot(data, labels=labels, palette='dark_qual', title='Results')
```

### 5. Saving in multiple formats

```python
from plot import plot

fig = plot([10, 20, 30], labels=['A', 'B', 'C'], title='Results')

# PNG for slides
fig.savefig('results.png', dpi=300)

# PDF for paper
fig.savefig('results.pdf', format='pdf')

# SVG for web
fig.savefig('results.svg', format='svg')
```

### 6. Using with pandas

```python
import pandas as pd
from plot import plot

df = pd.read_csv('data.csv')

# Auto-detects best chart from DataFrame
fig = plot(df, title='Data Overview')

# Or force a specific type
fig = plot(df, type='correlation', title='Correlations')
fig = plot(df, type='line', title='Trends')
```

### 7. Competition paper workflow

```python
from plot import FigureFactory

# Setup
f = FigureFactory(style='nature', title_prefix='Figure ')

# 摘要
f.dashboard([
    {'label': 'Accuracy', 'value': '94.2%', 'change': '+2.3%',
     'change_dir': 'up', 'progress': 0.94},
    {'label': 'F1 Score', 'value': '0.91', 'change': '+0.03',
     'change_dir': 'up', 'progress': 0.91},
], title='Model Performance', ncols=2)

# 灵敏度分析
f.sensitivity(
    parameters=['Rate', 'Batch', 'Layers', 'Dropout'],
    low_values=[0.88, 0.90, 0.85, 0.80],
    high_values=[0.98, 0.96, 0.94, 0.90],
    title='Sensitivity Analysis',
)

# Save all
f.save_all('figures/', fmt='pdf')
```

---

## Troubleshooting

### "Chart type not found"

```python
from plot import list_chart_types
print(list_chart_types())  # See all available types
```

### "Color palette not found"

```python
from plot import get_palette
print(get_palette('nature_qual'))  # See all palettes
```

### Figures look ugly

Try switching styles:
```python
apply_style('nature')      # Clean, minimal
apply_style('publication') # Formal
apply_style('economist')   # Modern editorial
```

### Fonts don't render

For CJK characters, make sure you have a CJK font installed:
```bash
# Windows: SimSun, SimHei (usually pre-installed)
# macOS: PingFang, STHeiti (usually pre-installed)
# Linux: apt install fonts-noto-cjk
```

### Figures are too small/large

```python
fig = plot(data, labels=labels, figsize=(10, 6))
```

### Save fails

Make sure the output directory exists:
```python
import os
os.makedirs('output', exist_ok=True)
fig.savefig('output/figure.png')
```

---

## Quick reference

| Task | Code |
|------|------|
| Bar chart | `plot([10,20,30], labels=['A','B','C'])` |
| Line chart | `plot({'A':[1,2,3]}, x=[1,2,3])` |
| Scatter | `plot(x, y, type='scatter')` |
| Pie | `plot([30,25,20,15,10], labels=labels, type='pie')` |
| Histogram | `plot(np.random.randn(1000), type='hist')` |
| Correlation | `plot(df, type='correlation')` |
| Sensitivity | `plot(params, low, high, type='sensitivity')` |
| Dashboard | `plot(metrics, type='dashboard')` |
| Save | `fig.savefig('output.png', dpi=300)` |
| Batch | `FigureFactory(...)` |