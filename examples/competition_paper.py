"""
competition_paper.py — Full Competition Paper Figure Set

Generates all figures needed for a mathematical modeling competition paper.
Based on a typical CUMCM Problem C (data analysis) scenario.

Run: python examples/competition_paper.py
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from plot import *
from plot.styles import apply_style
from plot.utils import save_figure

import matplotlib.pyplot as plt

np.random.seed(42)


def generate_sample_data():
    """Generate sample data for a typical modeling competition."""
    # Time series data (2015-2024)
    years = list(range(2015, 2025))
    gdp = [100 + i * 8 + np.random.randn(10) * 2 for i in range(10)]
    population = [50 + i * 2 + np.random.randn(10) * 0.5 for i in range(10)]
    urbanization = [45 + i * 2.5 + np.random.randn(10) * 0.8 for i in range(10)]

    # Feature data for correlation analysis
    features = np.random.randn(200, 6)
    feature_names = ['GDP', 'Population', 'Urban Rate', 'Education', 'Infrastructure', 'Technology']

    return {
        'years': years,
        'gdp': gdp,
        'population': population,
        'urbanization': urbanization,
        'features': features,
        'feature_names': feature_names,
    }


def fig1_summary_dashboard(data):
    """Figure 1: Summary Dashboard — Key Metrics Overview"""
    metrics = [
        {'label': 'GDP Growth', 'value': f"+{data['gdp'][-1]/data['gdp'][0]*100-100:.1f}%",
         'change': f"+{data['gdp'][-1]/data['gdp'][-2]*100-100:.1f}%", 'change_dir': 'up',
         'progress': 0.85, 'sparkline': data['gdp']},
        {'label': 'Population', 'value': f"{data['population'][-1]:.1f}M",
         'change': f"+{data['population'][-1]/data['population'][-2]*100-100:.1f}%", 'change_dir': 'up',
         'progress': 0.72, 'sparkline': data['population']},
        {'label': 'Urban Rate', 'value': f"{data['urbanization'][-1]:.1f}%",
         'change': f"+{data['urbanization'][-1]-data['urbanization'][-2]:.1f}%", 'change_dir': 'up',
         'progress': data['urbanization'][-1]/100, 'sparkline': data['urbanization']},
        {'label': 'Model Accuracy', 'value': '92.5%',
         'change': '+3.2%', 'change_dir': 'up', 'progress': 0.925},
        {'label': 'R² Score', 'value': '0.958',
         'change': '+0.03', 'change_dir': 'up', 'progress': 0.958},
        {'label': 'Efficiency', 'value': '96.3%',
         'change': '-0.5%', 'change_dir': 'down', 'progress': 0.963},
    ]
    fig = dashboard(metrics, title='Development Overview Dashboard', ncols=3)
    save_figure(fig, 'figures/01_summary_dashboard.png')
    print("✓ Figure 1: Summary Dashboard")
    return fig


def fig2_model_structure():
    """Figure 2: Model Structure — Process Flow"""
    steps = [
        'Data Collection',
        'Data Preprocessing',
        'Feature Engineering',
        'Model Building',
        'Parameter Estimation',
        'Model Validation',
        'Sensitivity Analysis',
        'Results Interpretation',
    ]
    fig = process_flow(steps, title='Modeling Process Flow')
    save_figure(fig, 'figures/02_model_structure.png')
    print("✓ Figure 2: Model Structure")
    return fig


def fig3_trend_analysis(data):
    """Figure 3: Multi-variable Trend Analysis"""
    fig = line_chart(
        data['years'],
        {
            'GDP': data['gdp'],
            'Population': data['population'] * 2,
            'Urbanization': data['urbanization'],
        },
        title='Development Indicators (2015-2024)',
        xlabel='Year',
        ylabel='Value',
        markers=True,
        annotate_last=True,
        grid='both',
    )
    save_figure(fig, 'figures/03_trend_analysis.png')
    print("✓ Figure 3: Trend Analysis")
    return fig


def fig4_correlation_matrix(data):
    """Figure 4: Feature Correlation Matrix"""
    fig = correlation_matrix(
        data['features'],
        labels=data['feature_names'],
        title='Feature Correlation Matrix',
        cmap='RdBu_r',
        show_values=True,
    )
    save_figure(fig, 'figures/04_correlation_matrix.png')
    print("✓ Figure 4: Correlation Matrix")
    return fig


def fig5_sensitivity_analysis():
    """Figure 5: Sensitivity Analysis — Tornado Chart"""
    fig = sensitivity_analysis(
        parameters=['GDP Growth Rate', 'Population Density', 'Urban Rate',
                    'Education Level', 'Infrastructure Score', 'Technology Index'],
        low_values=[0.82, 0.78, 0.75, 0.70, 0.68, 0.65],
        high_values=[0.95, 0.92, 0.88, 0.85, 0.82, 0.78],
        title='Parameter Sensitivity Analysis',
    )
    save_figure(fig, 'figures/05_sensitivity.png')
    print("✓ Figure 5: Sensitivity Analysis")
    return fig


def fig6_radar_comparison():
    """Figure 6: Regional Comparison — Radar Chart"""
    indicators = ['Economy', 'Population', 'Urbanization', 'Education', 'Infrastructure', 'Environment']
    values = [
        [8, 6, 7, 5, 6, 7],
        [6, 7, 8, 7, 7, 6],
        [7, 5, 6, 8, 5, 8],
    ]
    fig = radar_chart(
        indicators, values,
        names=['Region A', 'Region B', 'Region C'],
        title='Regional Development Comparison',
    )
    save_figure(fig, 'figures/06_radar_comparison.png')
    print("✓ Figure 6: Radar Comparison")
    return fig


def fig7_fit_curve(data):
    """Figure 7: Model Fitting — GDP Trend"""
    x = np.array(data['years'], dtype=float)
    y = np.array(data['gdp'])

    fig = fit_curve(
        x, y,
        ci_degree=3,
        title='GDP Growth Trend Fitting',
        xlabel='Year',
        ylabel='GDP (100M)',
        show_ci=True,
        show_equation=True,
    )
    save_figure(fig, 'figures/07_fit_curve.png')
    print("✓ Figure 7: Fit Curve")
    return fig


def fig8_feature_importance():
    """Figure 8: Feature Importance Ranking"""
    features = ['GDP', 'Urban Rate', 'Education', 'Population', 'Infrastructure',
                'Technology', 'Environment', 'Healthcare']
    importances = [0.28, 0.22, 0.18, 0.12, 0.08, 0.06, 0.03, 0.03]

    fig = feature_importance(
        features, importances,
        title='Feature Importance Ranking',
        top_n=8,
    )
    save_figure(fig, 'figures/08_feature_importance.png')
    print("✓ Figure 8: Feature Importance")
    return fig


def fig9_network_graph():
    """Figure 9: Factor Relationship Network"""
    nodes = [0, 1, 2, 3, 4, 5, 6]
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 4), (1, 5),
        (2, 4), (2, 6),
        (3, 5), (3, 6),
        (4, 5),
    ]
    node_labels = ['Economy', 'Population', 'Environment',
                   'Education', 'Infrastructure', 'Technology', 'Healthcare']

    fig = network_graph(
        nodes, edges,
        node_labels=node_labels,
        title='Development Factor Network',
        layout='spring',
    )
    save_figure(fig, 'figures/09_network_graph.png')
    print("✓ Figure 9: Network Graph")
    return fig


def fig10_validation():
    """Figure 10: Model Validation — Residual Plot"""
    np.random.seed(42)
    x = np.arange(1, 21)
    y_true = x ** 1.5 + np.random.randn(20) * 2
    y_pred = x ** 1.5 + np.random.randn(20) * 1.5

    fig = residual_plot(
        x, y_true, y_pred,
        title='Model Residual Analysis',
        show_r_squared=True,
    )
    save_figure(fig, 'figures/10_validation.png')
    print("✓ Figure 10: Model Validation")
    return fig


def fig11_timeline():
    """Figure 11: Project Timeline"""
    events = [
        {'time': 1.0, 'label': 'Phase 1 Start', 'category': 'milestone', 'duration': 3},
        {'time': 4.0, 'label': 'Phase 2 Start', 'category': 'milestone', 'duration': 3},
        {'time': 7.0, 'label': 'Phase 3 Start', 'category': 'milestone', 'duration': 4},
        {'time': 11.0, 'label': 'Final Review', 'category': 'milestone', 'duration': 1},
    ]
    fig = timeline(events, title='Project Timeline')
    save_figure(fig, 'figures/11_timeline.png')
    print("✓ Figure 11: Timeline")
    return fig


def fig12_mind_map():
    """Figure 12: Project Mind Map"""
    branches = [
        {'label': 'Data', 'items': ['Collection', 'Cleaning', 'Feature Eng', 'Validation']},
        {'label': 'Model', 'items': ['Building', 'Fitting', 'Tuning', 'Evaluation']},
        {'label': 'Analysis', 'items': ['Correlation', 'Sensitivity', 'Comparison', 'Prediction']},
        {'label': 'Results', 'items': ['Visualization', 'Interpretation', 'Reporting', 'Conclusion']},
    ]
    fig = mind_map('Urban Development Model', branches, title='Project Structure')
    save_figure(fig, 'figures/12_mind_map.png')
    print("✓ Figure 12: Mind Map")
    return fig


if __name__ == "__main__":
    print("=" * 60)
    print("  Competition Paper — Complete Figure Set")
    print("  Scenario: Urban Development Analysis (CUMCM Problem C style)")
    print("=" * 60)
    print()

    os.makedirs('figures', exist_ok=True)
    apply_style('nature')

    data = generate_sample_data()

    figs = [
        fig1_summary_dashboard,
        fig2_model_structure,
        fig3_trend_analysis,
        fig4_correlation_matrix,
        fig5_sensitivity_analysis,
        fig6_radar_comparison,
        fig7_fit_curve,
        fig8_feature_importance,
        fig9_network_graph,
        fig10_validation,
        fig11_timeline,
        fig12_mind_map,
    ]

    for i, func in enumerate(figs, 1):
        if i <= len(figs) and func.__name__ in [
            'fig1_summary_dashboard', 'fig3_trend_analysis',
            'fig4_correlation_matrix', 'fig7_fit_curve',
        ]:
            func(data)
        else:
            func()

    print()
    print("=" * 60)
    print(f"  All {len(figs)} figures generated!")
    print(f"  Output: figures/ (12 PNG files, 300 DPI)")
    print("=" * 60)