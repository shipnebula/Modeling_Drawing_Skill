"""
generate_examples.py — Generate demonstration figures for math-modeling-viz

Creates SVG and PDF files in the examples_output/ directory.
Shows off the full range of chart types available in the library.
"""
import os, sys
import numpy as np
import matplotlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from plot import *
from plot.styles import apply_style
from plot.utils import save_figure

np.random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), '..', 'examples_output')
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    """Save figure as both SVG and PDF."""
    save_figure(fig, os.path.join(OUT, f'{name}.svg'), dpi=300, fmt='svg')
    save_figure(fig, os.path.join(OUT, f'{name}.pdf'), dpi=300, fmt='pdf')
    print(f"  -> {name}.svg + {name}.pdf")


# ──────────────────────────────────────────────
#  1. BASIC STATISTICAL CHARTS
# ──────────────────────────────────────────────

def demo_01_bar():
    fig = bar_chart(
        [120, 180, 150, 210, 175, 230, 195],
        labels=['2018', '2019', '2020', '2021', '2022', '2023', '2024'],
        title='Annual GDP Growth (100B)',
        ylabel='GDP (100B)',
        palette='nature_qual',
        show_values=True,
    )
    save(fig, '01_bar_chart')


def demo_02_grouped():
    data = {
        'Region A': [100, 120, 140, 160, 180],
        'Region B': [80, 95, 110, 130, 150],
        'Region C': [60, 70, 85, 100, 115],
    }
    fig = grouped_bar(
        data, labels=['2020', '2021', '2022', '2023', '2024'],
        title='Revenue by Region', ylabel='Revenue (M)',
    )
    save(fig, '02_grouped_bar')


def demo_03_line():
    x = list(range(2015, 2025))
    y = {
        'Model A': [45, 50, 55, 60, 65, 70, 72, 75, 78, 80],
        'Model B': [40, 45, 50, 55, 60, 65, 68, 72, 75, 78],
        'Model C': [35, 40, 48, 52, 58, 62, 65, 68, 72, 75],
    }
    fig = line_chart(x, y, title='Model Accuracy Over Time',
                     xlabel='Year', ylabel='Accuracy (%)',
                     markers=True, annotate_last=True, grid='both')
    save(fig, '03_line_chart')


def demo_04_scatter():
    x = np.random.randn(80) * 3 + 10
    y = x * 2.5 + np.random.randn(80) * 3 + 5
    fig = scatter_plot(x, y, show_fit=True, fit_degree=2,
                       title='Linear Relationship with Fit',
                       xlabel='Input (X)', ylabel='Output (Y)')
    save(fig, '04_scatter_plot')


def demo_05_heatmap():
    data = np.random.randn(100, 6) * np.array([1, 2, 3, 4, 5, 6])
    labels = ['GDP', 'Population', 'Urban Rate', 'Education', 'Infra', 'Tech']
    fig = correlation_matrix(data, labels=labels,
                             title='Feature Correlation Matrix', cmap='RdBu_r')
    save(fig, '05_correlation_matrix')


def demo_06_histogram():
    data = np.random.randn(500) * 15 + 100
    fig = histogram(data, bins=30, kde=True,
                    title='Distribution of Test Scores',
                    xlabel='Score', ylabel='Frequency')
    save(fig, '06_histogram')


def demo_07_box():
    data = [
        np.random.randn(50) * 5 + 80,
        np.random.randn(50) * 5 + 85,
        np.random.randn(50) * 5 + 90,
        np.random.randn(50) * 5 + 95,
    ]
    fig = box_plot(data, labels=['Class A', 'Class B', 'Class C', 'Class D'],
                   title='Score Distribution by Class', ylabel='Score')
    save(fig, '07_box_plot')


def demo_08_pie():
    fig = pie_chart([35, 25, 20, 15, 5], labels=['A', 'B', 'C', 'D', 'E'],
                    title='Market Share Distribution', autopct='%.1f%%')
    save(fig, '08_pie_chart')


# ──────────────────────────────────────────────
#  2. MODEL ANALYSIS CHARTS
# ──────────────────────────────────────────────

def demo_09_fit_curve():
    x = np.linspace(1, 10, 30)
    y = x**2 * 0.5 + np.random.randn(30) * 2 + 1
    fig = fit_curve(x, y, ci_degree=3,
                    title='Quadratic Fit with Confidence Band',
                    xlabel='Feature X', ylabel='Target Y')
    save(fig, '09_fit_curve')


def demo_10_sensitivity():
    fig = sensitivity_analysis(
        parameters=['Learning Rate', 'Batch Size', 'Layers', 'Dropout', 'Epochs'],
        low_values=[0.88, 0.85, 0.82, 0.80, 0.83],
        high_values=[0.96, 0.93, 0.90, 0.87, 0.91],
        title='Parameter Sensitivity Analysis',
    )
    save(fig, '10_sensitivity_analysis')


def demo_11_feature_importance():
    features = ['GDP', 'Urban Rate', 'Education', 'Population', 'Infra',
                'Technology', 'Environment', 'Healthcare']
    importances = [0.28, 0.22, 0.18, 0.12, 0.08, 0.06, 0.03, 0.03]
    fig = feature_importance(features, importances,
                             title='Feature Importance Ranking', top_n=8)
    save(fig, '11_feature_importance')


def demo_12_confusion():
    np.random.seed(42)
    y_true = np.array([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,1,1,0,1,0,0,1,1,0,1,1,0])
    y_pred = np.array([0,0,1,0,0,0,0,1,1,1,0,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1,0,1,1,0])
    fig = confusion_matrix(y_true, y_pred, labels=['Negative', 'Positive'],
                           title='Classification Confusion Matrix')
    save(fig, '12_confusion_matrix')


def demo_13_pareto():
    t = np.linspace(0, 1, 50)
    obj1 = [1 - t, t]
    obj2 = [0.5 + 0.5*t, t]
    obj3 = [t**2, t**0.5]
    fig = pareto_front([obj1, obj2, obj3], labels=['Algorithm A', 'Algorithm B', 'Algorithm C'],
                       xlabel='Objective 1 (Cost)', ylabel='Objective 2 (Quality)')
    save(fig, '13_pareto_front')


def demo_14_residual():
    x = np.arange(1, 21)
    y_true = x**1.5 + np.random.randn(20) * 1.5
    y_pred = x**1.5 + np.random.randn(20) * 1.0
    fig = residual_plot(x, y_true, y_pred,
                        title='Model Residual Analysis',
                        show_r_squared=True)
    save(fig, '14_residual_plot')


def demo_15_roc():
    y_true = np.array([0,0,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1,1,0,1,1,0,1,0])
    y_score = np.array([0.1,0.2,0.3,0.4,0.5,0.9,0.8,0.7,0.95,0.85,0.2,0.15,0.88,0.92,0.3,0.78,0.25,0.18,0.85,0.9,0.22,0.82,0.87,0.35,0.75,0.12])
    fig = roc_curve(y_true, y_score, title='ROC Curve with AUC')
    save(fig, '15_roc_curve')


# ──────────────────────────────────────────────
#  3. ADVANCED CHARTS
# ──────────────────────────────────────────────

def demo_16_radar():
    labels = ['Speed', 'Accuracy', 'Cost', 'Reliability', 'Usability']
    values = [[4, 5, 3, 4, 5], [3, 4, 4, 5, 3], [5, 3, 5, 3, 4]]
    fig = radar_chart(labels, values, names=['Model A', 'Model B', 'Model C'],
                      title='Multi-Metric Model Comparison')
    save(fig, '16_radar_chart')


def demo_17_waterfall():
    fig = waterfall_chart(
        categories=['Start', '+Revenue', '-Cost', '-Tax', '+Subsidy', '-Ops', 'End'],
        values=[100, 50, -30, -20, 15, -10, 105],
        title='Financial Waterfall Analysis',
    )
    save(fig, '17_waterfall_chart')


def demo_18_dumbbell():
    fig = dumbbell_plot(
        labels=['Region A', 'Region B', 'Region C', 'Region D', 'Region E'],
        old_values=[30, 50, 20, 40, 35],
        new_values=[42, 55, 28, 48, 40],
        title='Before vs After Comparison',
        old_label='Before', new_label='After',
    )
    save(fig, '18_dumbbell_plot')


def demo_19_network():
    nodes = list(range(8))
    edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,7),(4,5),(6,7)]
    labels = ['Economy','Pop','Env','Edu','Infra','Tech','Health','Science']
    fig = network_graph(nodes, edges, node_labels=labels,
                        title='Development Factor Network', layout='spring')
    save(fig, '19_network_graph')


def demo_20_sankey():
    flows = [(0,1,50),(0,2,30),(1,3,40),(1,4,10),(2,3,20),(2,4,10)]
    labels = ['Source A','Mid A','Mid B','Sink A','Sink B']
    fig = sankey_diagram(flows, labels=labels, title='Flow Analysis')
    save(fig, '20_sankey_diagram')


def demo_21_gantt():
    tasks = [
        {'name': 'Research', 'start': 0, 'end': 5, 'progress': 1.0},
        {'name': 'Modeling', 'start': 5, 'end': 15, 'progress': 0.8},
        {'name': 'Analysis', 'start': 12, 'end': 20, 'progress': 0.5},
        {'name': 'Writing', 'start': 18, 'end': 25, 'progress': 0.3},
        {'name': 'Review', 'start': 23, 'end': 28, 'progress': 0.0},
    ]
    fig = gantt_chart(tasks, title='Project Gantt Chart')
    save(fig, '21_gantt_chart')


def demo_22_timeline():
    events = [
        {'time': 1.0, 'label': 'Phase 1 Start', 'category': 'milestone', 'duration': 3},
        {'time': 4.0, 'label': 'Phase 2 Start', 'category': 'milestone', 'duration': 3},
        {'time': 7.0, 'label': 'Phase 3 Start', 'category': 'milestone', 'duration': 4},
        {'time': 11.0, 'label': 'Final Review', 'category': 'milestone', 'duration': 1},
    ]
    fig = timeline(events, title='Project Timeline')
    save(fig, '22_timeline')


def demo_23_slope():
    fig = slope_chart(
        labels=['A', 'B', 'C', 'D', 'E'],
        y1=[80, 65, 50, 35, 20],
        y2=[70, 55, 45, 30, 25],
        title='Ranking Change Before/After',
    )
    save(fig, '23_slope_chart')


def demo_24_parallel():
    np.random.seed(42)
    data = np.random.randn(30, 5)
    labels = ['F1', 'F2', 'F3', 'F4', 'F5']
    fig = parallel_coordinates(data, labels=labels,
                               title='Parallel Coordinates Plot')
    save(fig, '24_parallel_coordinates')


def demo_25_treemap():
    fig = treemap([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
                  title='Hierarchical Breakdown')
    save(fig, '25_treemap')


# ──────────────────────────────────────────────
#  4. INFOGRAPHIC CHARTS
# ──────────────────────────────────────────────

def demo_26_dashboard():
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
        {'label': 'Speed', 'value': '1.2ms', 'change': '-0.3ms', 'change_dir': 'up',
         'progress': 0.88},
    ]
    fig = dashboard(metrics, title='Model Performance Dashboard', ncols=3)
    save(fig, '26_dashboard')


def demo_27_gauge():
    fig = gauge(value=75, min_val=0, max_val=100, label='Completion',
                title='Project Progress')
    save(fig, '27_gauge')


def demo_28_kpi():
    fig = kpi_card(label='Total Revenue', value='$4.2M', change='+12.5%',
                   change_dir='up', target='$5.0M', progress=0.84)
    save(fig, '28_kpi_card')


def demo_29_bullet():
    fig = bullet_chart(actual=85, target=90, min_val=0, max_val=100,
                       benchmarks=[70, 80], title='Performance vs Target')
    save(fig, '29_bullet_chart')


def demo_30_sparkline():
    np.random.seed(42)
    values = np.cumsum(np.random.randn(50))
    fig = sparkline(values, title='Revenue Trend', show_min_max=True)
    save(fig, '30_sparkline')


def demo_31_process():
    steps = ['Data Collection', 'Preprocessing', 'Model Building',
             'Validation', 'Deployment']
    fig = process_flow(steps, title='ML Pipeline')
    save(fig, '31_process_flow')


def demo_32_mindmap():
    branches = [
        {'label': 'Data', 'items': ['Collection', 'Cleaning', 'Feature Eng']},
        {'label': 'Model', 'items': ['Training', 'Tuning', 'Evaluation']},
        {'label': 'Analysis', 'items': ['Sensitivity', 'Robustness', 'Validation']},
        {'label': 'Results', 'items': ['Visualization', 'Interpretation', 'Reporting']},
    ]
    fig = mind_map('Math Modeling', branches, title='Project Structure')
    save(fig, '32_mind_map')


def demo_33_comparison():
    fig = comparison_bar(['A', 'B', 'C', 'D', 'E'],
                         [85, 72, 90, 68, 78], target=80,
                         title='Performance vs Target', ylabel='Score')
    save(fig, '33_comparison_bar')


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Math Modeling Viz — Example Figure Generator")
    print("=" * 60)
    print()

    apply_style('nature')

    demos = [
        demo_01_bar, demo_02_grouped, demo_03_line, demo_04_scatter,
        demo_05_heatmap, demo_06_histogram, demo_07_box, demo_08_pie,
        demo_09_fit_curve, demo_10_sensitivity, demo_11_feature_importance,
        demo_12_confusion, demo_13_pareto, demo_14_residual, demo_15_roc,
        demo_16_radar, demo_17_waterfall, demo_18_dumbbell,
        demo_19_network, demo_20_sankey, demo_21_gantt, demo_22_timeline,
        demo_23_slope, demo_24_parallel, demo_25_treemap,
        demo_26_dashboard, demo_27_gauge, demo_28_kpi,
        demo_29_bullet, demo_30_sparkline, demo_31_process,
        demo_32_mindmap, demo_33_comparison,
    ]

    for i, demo in enumerate(demos, 1):
        try:
            demo()
        except Exception as e:
            print(f"  FAILED {demo.__name__}: {e}")
            import traceback
            traceback.print_exc()

    # Count output files
    svg_count = len([f for f in os.listdir(OUT) if f.endswith('.svg')])
    pdf_count = len([f for f in os.listdir(OUT) if f.endswith('.pdf')])

    print()
    print("=" * 60)
    print(f"  Generated {svg_count} SVG + {pdf_count} PDF files")
    print(f"  Output: {OUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()