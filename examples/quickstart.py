"""
quickstart.py — Quick Start Examples

Run this file to see the basic usage of math-modeling-viz.
Each example generates a figure saved to the 'figures/' directory.
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from plot import *
import numpy as np
import matplotlib.pyplot as plt


# Create output directory
os.makedirs('figures', exist_ok=True)


def example1_bar_chart():
    """Simple bar chart."""
    fig = bar_chart(
        [30, 50, 20, 45, 60],
        labels=['Region A', 'Region B', 'Region C', 'Region D', 'Region E'],
        title='Population by Region (2024)',
        ylabel='Population (100M)',
        palette='nature_qual',
        show_values=True,
    )
    save_figure(fig, 'figures/01_bar_chart.png')
    print("✓ Figure 1: Bar Chart")
    plt.close(fig)


def example2_line_chart():
    """Multi-line chart with markers."""
    x = list(range(2015, 2026))
    y = {
        'Model A': [45, 50, 55, 60, 65, 70, 72, 75, 78, 80, 82],
        'Model B': [40, 45, 50, 55, 60, 65, 68, 72, 75, 78, 80],
        'Model C': [35, 40, 48, 52, 58, 62, 65, 68, 72, 75, 78],
    }
    fig = line_chart(
        x, y,
        title='Model Performance Over Time',
        xlabel='Year',
        ylabel='Score',
        markers=True,
        annotate_last=True,
        grid='both',
    )
    save_figure(fig, 'figures/02_line_chart.png')
    print("✓ Figure 2: Line Chart")
    plt.close(fig)


def example3_scatter_plot():
    """Scatter plot with fit line."""
    np.random.seed(42)
    x = np.random.randn(50) * 3 + 10
    y = x ** 1.5 * 2 + np.random.randn(50) * 5

    fig = scatter_plot(
        x, y,
        show_fit=True,
        fit_degree=2,
        title='Growth Pattern Analysis',
        xlabel='Input Variable',
        ylabel='Output Value',
    )
    save_figure(fig, 'figures/03_scatter_plot.png')
    print("✓ Figure 3: Scatter Plot")
    plt.close(fig)


def example4_grouped_bar():
    """Grouped bar chart."""
    data = {
        'Product A': [100, 120, 140, 160, 180],
        'Product B': [80, 95, 110, 130, 150],
        'Product C': [60, 70, 85, 100, 115],
    }
    fig = grouped_bar(
        data,
        labels=['2020', '2021', '2022', '2023', '2024'],
        title='Revenue by Product Line',
        ylabel='Revenue (100M)',
    )
    save_figure(fig, 'figures/04_grouped_bar.png')
    print("✓ Figure 4: Grouped Bar Chart")
    plt.close(fig)


def example5_heatmap():
    """Correlation matrix heatmap."""
    np.random.seed(42)
    data = np.random.randn(50, 5) * np.array([1, 2, 3, 4, 5])
    corr = np.corrcoef(data, rowvar=False)
    labels = ['Feature A', 'Feature B', 'Feature C', 'Feature D', 'Feature E']

    fig = correlation_matrix(
        data,
        labels=labels,
        title='Feature Correlation Matrix',
        cmap='RdBu_r',
    )
    save_figure(fig, 'figures/05_heatmap.png')
    print("✓ Figure 5: Heatmap")
    plt.close(fig)


def example6_radar():
    """Radar chart for multi-dimensional comparison."""
    labels = ['Speed', 'Accuracy', 'Cost', 'Reliability', 'Usability']
    values = [
        [4, 5, 3, 4, 5],
        [3, 4, 4, 5, 3],
        [5, 3, 5, 3, 4],
    ]
    names = ['Model A', 'Model B', 'Model C']

    fig = radar_chart(
        labels, values,
        names=names,
        title='Multi-Metric Model Comparison',
    )
    save_figure(fig, 'figures/06_radar_chart.png')
    print("✓ Figure 6: Radar Chart")
    plt.close(fig)


def example7_dashboard():
    """KPI Dashboard."""
    metrics = [
        {'label': 'Accuracy', 'value': '94.2%', 'change': '+2.3%', 'change_dir': 'up',
         'progress': 0.94},
        {'label': 'F1 Score', 'value': '0.91', 'change': '+0.03', 'change_dir': 'up',
         'progress': 0.91},
        {'label': 'Precision', 'value': '0.93', 'change': '-0.01', 'change_dir': 'down',
         'progress': 0.93},
        {'label': 'Recall', 'value': '0.90', 'change': '+0.02', 'change_dir': 'up',
         'progress': 0.90},
        {'label': 'AUC', 'value': '0.96', 'change': '+0.01', 'change_dir': 'up',
         'progress': 0.96},
        {'label': 'Inference', 'value': '1.2ms', 'change': '-0.3ms', 'change_dir': 'up',
         'progress': 0.88},
    ]
    fig = dashboard(
        metrics,
        title='Model Performance Dashboard',
        ncols=3,
    )
    save_figure(fig, 'figures/07_dashboard.png')
    print("✓ Figure 7: Dashboard")
    plt.close(fig)


def example8_sensitivity():
    """Sensitivity analysis tornado chart."""
    fig = sensitivity_analysis(
        parameters=['Learning Rate', 'Batch Size', 'Layers', 'Dropout', 'Epochs'],
        low_values=[0.92, 0.90, 0.88, 0.85, 0.87],
        high_values=[0.98, 0.96, 0.94, 0.90, 0.93],
        title='Parameter Sensitivity Analysis',
    )
    save_figure(fig, 'figures/08_sensitivity.png')
    print("✓ Figure 8: Sensitivity Analysis")
    plt.close(fig)


def example9_confusion():
    """Confusion matrix."""
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    X, y = make_classification(n_samples=200, n_features=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    fig = confusion_matrix(
        y_test, y_pred,
        labels=['Negative', 'Positive'],
        title='Classification Confusion Matrix',
    )
    save_figure(fig, 'figures/09_confusion_matrix.png')
    print("✓ Figure 9: Confusion Matrix")
    plt.close(fig)


def example10_waterfall():
    """Waterfall chart."""
    fig = waterfall_chart(
        categories=['Start', '+Revenue', '-Cost', '-Tax', '+Subsidy', '-Ops', 'End'],
        values=[100, 50, -30, -20, 15, -10, 105],
        title='Financial Waterfall Analysis',
    )
    save_figure(fig, 'figures/10_waterfall.png')
    print("✓ Figure 10: Waterfall Chart")
    plt.close(fig)


if __name__ == "__main__":
    print("=" * 50)
    print("  Math Modeling Viz — Quick Start Examples")
    print("=" * 50)
    print()

    example1_bar_chart()
    example2_line_chart()
    example3_scatter_plot()
    example4_grouped_bar()
    example5_heatmap()
    example6_radar()
    example7_dashboard()
    example8_sensitivity()
    example9_confusion()
    example10_waterfall()

    print()
    print("=" * 50)
    print("  All 10 figures generated successfully!")
    print(f"  Output directory: figures/")
    print("=" * 50)