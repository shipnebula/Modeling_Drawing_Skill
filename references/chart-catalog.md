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