#!/usr/bin/env python3
"""
gallery.py — Render one example of every chart into docs/images/.

Run from the repo root:
    python examples/gallery.py

Every image doubles as living documentation: if a chart regresses,
its gallery PNG changes and the diff shows up in code review.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import matplotlib

matplotlib.use("Agg")

import plot as pl  # noqa: E402
from plot import plot, panel_figure  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)


def _ohlc():
    o = 100 + np.cumsum(rng.normal(0, 1.5, 40))
    c = o + rng.normal(0, 1, 40)
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.8, 40))
    low = np.minimum(o, c) - np.abs(rng.normal(0, 0.8, 40))
    return pl.candlestick(o, h, low, c, title="OHLC")


def _clusters():
    pts = np.vstack([
        rng.normal([2, 2], 0.5, (60, 2)),
        rng.normal([6, 5], 0.6, (60, 2)),
        rng.normal([2, 7], 0.5, (60, 2)),
    ])
    return pts

def save(fig, name):
    png = OUT / f"{name}.png"
    fig.savefig(png, dpi=110, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f"  ✓ {name}")


def main() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    pl.apply_style("nature")

    xs = np.linspace(0, 10, 60)
    xg = np.linspace(0, 2, 40)
    X, Y = np.meshgrid(xg, xg)
    Z = np.sin(3 * X) * np.cos(2 * Y) * np.exp(-0.3 * (X + Y))

    charts = {
        # ── basic ──
        "01_bar": lambda: plot([120, 180, 150, 210], labels=["2022", "2023", "2024", "2025"], title="Annual Revenue"),
        "02_grouped_bar": lambda: plot({"Model A": [88, 91, 94], "Model B": [85, 89, 95]}, labels=["v1", "v2", "v3"], type="grouped", title="Model Comparison"),
        "03_stacked_bar": lambda: plot({"Direct": [40, 55, 60], "Referral": [25, 30, 35]}, labels=["Q1", "Q2", "Q3"], type="stacked", title="Traffic Sources"),
        "04_line": lambda: plot({"Greedy": [0.62, 0.74, 0.81, 0.86, 0.89, 0.90], "GA": [0.60, 0.70, 0.80, 0.87, 0.92, 0.94], "SA": [0.61, 0.76, 0.84, 0.90, 0.93, 0.95]}, x=range(6), title="Convergence"),
        "05_area": lambda: plot({"Web": [3, 4, 6, 5], "App": [2, 3, 4, 6]}, x=[2022, 2023, 2024, 2025], type="area", title="Users by Channel"),
        "06_scatter": lambda: plot(rng.uniform(0, 10, 80), rng.uniform(0, 10, 80) * 0.8 + rng.normal(0, 1.2, 80), type="scatter", show_fit=True, title="Advertising vs Sales"),
        "07_pie": lambda: plot([38, 26, 21, 15], labels=["A", "B", "C", "D"], type="pie", title="Market Share"),
        "08_donut": lambda: plot([45, 30, 25], labels=["X", "Y", "Z"], type="donut", center_text="2025", title="Budget"),
        "09_histogram": lambda: plot(rng.normal(170, 8, 1500), type="hist", kde=True, title="Height Distribution", xlabel="cm"),
        "10_box": lambda: plot([rng.normal(70, 8, 200), rng.normal(75, 9, 200), rng.normal(68, 6, 200)], labels=["A", "B", "C"], type="box", title="Scores by Group"),
        "11_violin": lambda: plot([rng.normal(0, 1, 300), rng.normal(0.8, 1.2, 300)], labels=["Control", "Treatment"], type="violin", title="Response Distribution"),
        "12_step": lambda: pl.step_chart(np.arange(1, 9), np.cumsum(rng.integers(2, 8, 8)), title="Cumulative Users"),
        # ── model ──
        "13_fit_curve": lambda: plot(np.linspace(0, 10, 40), 2.5 * np.linspace(0, 10, 40) ** 1.6 + rng.normal(0, 8, 40), type="fit", title="Power-Law Fit"),
        "14_residual": lambda: plot(np.linspace(0, 10, 60), np.linspace(0, 10, 60), np.linspace(0, 10, 60) + rng.normal(0, 1.5, 60), type="residual", title="Residual Diagnostics"),
        "15_confusion": lambda: pl.confusion_matrix(np.array([[52, 8], [6, 34]]), class_names=["Negative", "Positive"], title="Confusion Matrix"),
        "16_roc": lambda: pl.roc_curve(rng.integers(0, 2, 300), rng.uniform(0, 1, 300) * 0.6 + rng.integers(0, 2, 300) * 0.3, title="ROC Curve"),
        "17_learning_curve": lambda: pl.learning_curve(rng.normal(0, 1, (300, 6)), rng.integers(0, 2, 300), title="Learning Curve"),
        "18_sensitivity": lambda: pl.sensitivity_analysis(parameters=["Price", "Demand", "Capacity", "Lead Time", "Cost"], low_values=[0.86, 0.90, 0.93, 0.96, 0.98], high_values=[0.97, 0.95, 0.94, 0.99, 0.99], title="Sensitivity Analysis"),
        "19_pareto": lambda: pl.pareto_front(rng.uniform(0, 10, 40), 25 - rng.uniform(0, 10, 40) ** 1.2, title="Pareto Front"),
        "20_validation": lambda: pl.validation_plot([rng.normal(0.90, 0.02, 5)], [rng.normal(0.85, 0.03, 5)], metrics=["Accuracy"], title="Cross-Validation"),
        "21_feature_importance": lambda: pl.feature_importance(["Feature A", "Feature B", "Feature C", "Feature D", "Feature E"], [0.32, 0.27, 0.18, 0.13, 0.10], title="Feature Importance"),
        "22_clustering": lambda: pl.clustering_2d(_clusters(), title="Customer Segments"),
        "23_correlation": lambda: pl.correlation_matrix(np.column_stack([rng.normal(0, 1, 200) for _ in range(5)]), labels=["V1", "V2", "V3", "V4", "V5"], title="Correlation Matrix"),
        # ── advanced ──
        "24_network": lambda: pl.network_graph(["Hub", "A", "B", "C", "D", "E"], [("Hub", "A"), ("Hub", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "E")], title="Network"),
        "25_sankey": lambda: pl.sankey_diagram([("Total", "A", 50), ("Total", "B", 30), ("A", "A1", 30), ("A", "A2", 20), ("B", "B1", 30)], title="Flows"),
        "26_radar": lambda: pl.radar_chart(["Speed", "Accuracy", "Cost", "Robustness", "Ease"], [[4.2, 4.8, 3.1, 3.9, 4.4], [3.8, 4.1, 4.5, 3.5, 3.9]], names=["Model A", "Model B"], title="Model Comparison"),
        "27_waterfall": lambda: pl.waterfall_chart(categories=["Start", "Sales", "Returns", "Costs", "End"], values=[100, 40, -15, -25, 100], title="Profit Bridge"),
        "28_dumbbell": lambda: pl.dumbbell_plot(labels=["Speed", "Quality", "Price"], old_values=[30, 55, 70], new_values=[58, 62, 45], title="Before vs After"),
        "29_slope": lambda: pl.slope_chart(labels=["A", "B", "C", "D"], y1=[80, 60, 42, 30], y2=[70, 66, 45, 38], title="Ranking Shift"),
        "30_timeline": lambda: pl.timeline([
            {"time": 0, "label": "Problem A", "duration": 2},
            {"time": 2, "label": "Problem B", "duration": 1.5},
            {"time": 3.5, "label": "Model", "duration": 3},
            {"time": 6.5, "label": "Analysis", "duration": 2},
            {"time": 8.5, "label": "Paper", "duration": 1.5},
        ], title="Project Timeline"),
        "31_parallel": lambda: pl.parallel_coordinates({"M1": [4, 7, 2, 5], "M2": [6, 4, 5, 3], "M3": [2, 5, 8, 6]}, labels=["F1", "F2", "F3", "F4"], title="Parallel Coordinates"),
        "32_gantt": lambda: pl.gantt_chart([{"name": "Data", "start": 0, "end": 2, "progress": 1.0}, {"name": "Model", "start": 2, "end": 5, "progress": 0.8}, {"name": "Tests", "start": 4, "end": 7, "progress": 0.4}], title="Schedule"),
        "33_treemap": lambda: plot([35, 25, 20, 12, 8], labels=["A", "B", "C", "D", "E"], type="treemap", title="Composition"),
        # ── infographic ──
        "34_dashboard": lambda: pl.dashboard([{"label": "Accuracy", "value": "94%", "change": "+2%", "change_dir": "up", "progress": 0.94}, {"label": "F1", "value": "0.91", "change": "+0.03", "change_dir": "up", "progress": 0.91}, {"label": "Latency", "value": "42ms", "change": "-8ms", "change_dir": "down", "progress": 0.75}, {"label": "Cost", "value": "$120", "change": "+$9", "change_dir": "down", "progress": 0.6}], title="Model Dashboard"),
        "35_kpi": lambda: pl.kpi_card("Revenue", value="$4.2M", change="+12%", change_dir="up", progress=0.84, title="Q3 KPI"),
        "36_bullet": lambda: pl.bullet_chart([82, 65, 47], [90, 75, 60], labels=["Sales", "Ops", "R&D"], title="KPI Targets"),
        "37_sparkline": lambda: pl.sparkline(rng.uniform(5, 9, 30), title="30-day Trend"),
        "38_gauge": lambda: pl.gauge(76, label="SLA", title="Service Level"),
        "39_flow": lambda: plot(["Collect", "Clean", "Model", "Validate", "Deploy"], type="flow", title="Pipeline"),
        "40_mindmap": lambda: plot("Model", branches=[{"label": "Theory", "items": ["A1", "A2", "A3"]}, {"label": "Data", "items": ["B1", "B2"]}, {"label": "Solve", "items": ["C1", "C2", "C3"]}], type="mind", title="Mind Map"),
        "41_compare": lambda: pl.comparison_bar(["A", "B", "C", "D"], [85, 72, 90, 66], target=80, title="vs Target"),
        # ── sciences (v2.0) ──
        "42_surface3d": lambda: pl.surface3d(X, Y, Z, title="Objective Surface"),
        "43_contour": lambda: pl.contour_plot(xg, xg, Z, mark_min=False, title="Contours"),
        "44_vector_field": lambda: pl.vector_field(xg, xg, -np.sin(Y), np.cos(X), mode="both", title="Vector Field"),
        "45_phase_portrait": lambda: pl.phase_portrait({"ω=1": (np.sin(xs), np.cos(xs)), "ω=2": (np.sin(2 * xs) / 2, np.cos(2 * xs))}, xlabel="x", ylabel="ẋ", title="Phase Portrait"),
        "46_twin_axis": lambda: pl.twin_axis(np.arange(12), np.linspace(20, 80, 12), np.linspace(1000, 300, 12), ylabel1="Temperature (°C)", ylabel2="Pressure (hPa)", title="Dual-Axis Measurements"),
        "47_errorband": lambda: pl.errorband(np.arange(40), np.sin(np.linspace(0, 6, 40)), yerr=0.25 + 0.1 * np.linspace(0, 1, 40), title="Monte-Carlo Envelope"),
        "48_heatmap": lambda: pl.heatmap(rng.uniform(0, 1, (6, 8)), row_labels=[f"M{i}" for i in range(6)], col_labels=[f"202{i}" for i in range(8)], title="Monthly Activity", cmap="YlGnBu"),
        "49_optimization_trace": lambda: pl.optimization_trace(lambda a, b: (a - 1.2) ** 2 + (b + 0.8) ** 2 + 0.5 * np.sin(3 * a), np.array([[0, 0], [0.3, -0.2], [0.6, -0.5], [0.9, -0.7], [1.1, -0.8], [1.2, -0.8]]), title="Gradient Descent Path"),
        "50_polar": lambda: pl.polar_chart(np.arange(0, 360, 30), {"Speed": np.abs(np.sin(np.linspace(0, 2 * np.pi, 12))) * 8 + 2}, labels=["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N", "NE", "E", "SE"], title="Wind Rose", zero_location="N", clockwise=True),
        "51_loglog": lambda: pl.loglog_plot({"O(n·log n)": [n * np.log2(n) for n in range(1, 60)], "O(n²)": [n ** 2 / 8 for n in range(1, 60)]}, show_fit_slope=True, title="Complexity Scaling"),
        # ── statistics (v2.0) ──
        "52_qq": lambda: pl.qq_plot(rng.normal(0, 1, 250), title="Normality Check"),
        "53_ecdf": lambda: pl.ecdf_plot({"A": rng.normal(0, 1, 150), "B": rng.normal(0.8, 1.2, 150)}, title="Empirical CDF"),
        "54_ridgeline": lambda: pl.ridgeline({f"{y}": rng.normal((y - 2018) * 0.5, 0.9, 300) for y in range(2018, 2026)}, xlabel="value", title="Distribution by Year"),
        "55_hexbin": lambda: pl.hexbin_plot(rng.normal(0, 1, 30000), rng.normal(0, 1, 30000), title="Hexbin Density"),
        "56_stem": lambda: pl.stem_plot(np.arange(12), np.abs(rng.normal(4, 1.4, 12)), labels=[f"m{i}" for i in range(12)], title="Monthly Errors"),
        "57_errorbar": lambda: pl.errorbar_chart(["LR", "RF", "XGB"], [0.82, 0.88, 0.91], yerr=[0.03, 0.02, 0.015], ylabel="accuracy", title="Mean ± SD"),
        "58_bubble": lambda: pl.bubble_chart(rng.uniform(1, 9, 14), rng.uniform(1, 9, 14), sizes=rng.uniform(100, 3000, 14), names=["East"] * 7 + ["West"] * 7, title="Bubble Chart"),
        "59_bump": lambda: pl.bump_chart({"Alpha": [1, 3, 2, 1], "Beta": [2, 1, 3, 2], "Gamma": [3, 2, 1, 3], "Delta": [4, 4, 4, 4]}, x_labels=["Q1", "Q2", "Q3", "Q4"], title="Rank Race"),
        "60_streamgraph": lambda: pl.stream_graph({f"S{i}": np.abs(rng.normal(5 + i, 1.5, 48)) for i in range(5)}, title="Streams"),
        "61_funnel": lambda: pl.funnel_chart({"Raw": 5000, "Deduped": 3800, "Valid": 2600, "Modeled": 1400}, title="Data Pipeline"),
        "62_waffle": lambda: pl.waffle_chart([45, 30, 15, 10], labels=["A", "B", "C", "D"], title="Share of 100"),
        "63_pyramid": lambda: pl.population_pyramid(["0-20", "21-40", "41-60", "61+"], [32, 45, 38, 20], [30, 43, 41, 26], title="Population Structure"),
        "64_sunburst": lambda: pl.sunburst_chart({"Tech": {"HW": 35, "SW": 45}, "Ops": {"Logistics": 25, "Support": 15}}, title="Two-Level Hierarchy"),
        "65_icicle": lambda: pl.icicle_chart({"Total": {"East": {"E1": 20, "E2": 12}, "West": 16, "North": 9}}, title="Icicle"),
        "66_mosaic": lambda: pl.mosaic_plot(np.array([[42, 18], [25, 35]]), row_labels=["Group 1", "Group 2"], col_labels=["Yes", "No"], title="Mosaic"),
        "67_dendrogram": lambda: pl.dendrogram(rng.normal(0, 1, (14, 5)), labels=list("ABCDEFGHIJKLMN"), title="Hierarchical Clustering"),
        "68_distribution_panel": lambda: pl.distribution_panel(rng.normal(3, 1.4, 400), title="Distribution Diagnostics"),
        "69_scatter_matrix": lambda: pl.scatter_matrix(rng.normal(0, 1, (120, 4)), names=["x1", "x2", "x3", "x4"], title="Pairs"),
        # ── calculus (v3.0) ──
        "71_auc": lambda: pl.area_under_curve(lambda x: np.sin(x) + 0.3 * x, a=0.5, b=2.5, title="Definite Integral"),
        "72_riemann": lambda: pl.riemann_sum(lambda x: np.sin(x) + 0.3 * x, a=0.5, b=2.5, n=9, method="mid", title="Riemann Sum (n=9)"),
        "73_tangent": lambda: pl.tangent_line(lambda x: np.sin(x) + 0.3 * x, x0=1.2, title="Tangent Line"),
        "74_interpolation": lambda: pl.interpolation_comparison(np.linspace(0, 3, 9), np.exp(-np.linspace(0, 3, 9) / 2) * np.cos(2 * np.linspace(0, 3, 9)), degree=4, title="Interpolation Methods"),
        # ── ML evaluation (v3.0) ──
        "75_pr_curve": lambda: pl.pr_curve(rng.integers(0, 2, 400), rng.uniform(0, 1, 400) * 0.5 + rng.integers(0, 2, 400) * 0.4, title="Precision-Recall"),
        "76_pred_actual": lambda: pl.prediction_vs_actual(np.linspace(1, 10, 60), np.linspace(1, 10, 60) + rng.normal(0, 0.7, 60), title="Predicted vs Actual"),
        "77_regression_panel": lambda: pl.regression_panel(np.linspace(1, 10, 60), np.linspace(1, 10, 60) + rng.normal(0, 0.7, 60), title="Regression Diagnostics"),
        "78_elbow": lambda: pl.elbow_plot(np.vstack([rng.normal([0, 0], 0.6, (80, 2)), rng.normal([4, 4], 0.6, (80, 2)), rng.normal([0, 4], 0.7, (80, 2))]), k_range=range(2, 9), title="K Selection"),
        "79_silhouette": lambda: pl.silhouette_plot(np.vstack([rng.normal([0, 0], 0.5, (60, 2)), rng.normal([4, 4], 0.5, (60, 2)), rng.normal([0, 4], 0.6, (60, 2))]), np.repeat([0, 1, 2], 60), title="Silhouette Profile"),
        "80_scree": lambda: pl.scree_plot(rng.normal(0, 1, (150, 8)), title="PCA Scree Plot"),
        # ── statistics (v3.0) ──
        "81_hypothesis_test": lambda: pl.hypothesis_test(rng.normal(0.35, 1, 70), mu=0, title="One-Sample t-Test"),
        "82_lorenz": lambda: pl.lorenz_curve(np.sort(rng.pareto(2, 300)) + 0.1, title="Lorenz Curve"),
        "83_forecast": lambda: pl.forecast(np.sin(np.arange(24) * 0.4) * 5 + 10, np.sin(np.arange(24, 30) * 0.4) * 5 + 10, lower=np.sin(np.arange(24, 30) * 0.4) * 5 + 8, upper=np.sin(np.arange(24, 30) * 0.4) * 5 + 12, title="Time-Series Forecast"),
        # ── diagrams (v3.0) ──
        "84_ahp": lambda: pl.ahp_hierarchy("最优方案", ["成本", "性能", "风险"], ["方案A", "方案B", "方案C"], weights=[0.4, 0.35, 0.25], title="AHP 层次结构模型"),
        "85_scatter3d": lambda: pl.scatter3d(rng.normal(0, 1, 120), rng.normal(0, 1, 120), rng.normal(0, 1, 120), names=["East"] * 60 + ["West"] * 60, title="3D Scatter"),
        # ── showcase (v3.0) ──
        "86_palette_preview": lambda: pl.palette_preview(families=("qualitative", "theme", "sequential", "diverging"), title="All Palettes"),
        "87_style_preview": lambda: pl.style_preview(title="All Styles"),

        # ── dynamics & timeseries (v4.0) ──
        "88_bifurcation": lambda: pl.bifurcation(a_range=(2.5, 4.0), n_a=500, n_plot=70, n_transient=120, mark_a=(3.0, 3.45), title="Logistic Map Bifurcation"),
        "89_cobweb": lambda: pl.cobweb(lambda x: 3.9 * x * (1 - x), x0=0.2, n=40, title="Cobweb Plot (a = 3.9)"),
        "90_monte_carlo": lambda: pl.monte_carlo_convergence(rng.normal(3.5, 1.2, 2000), true_value=3.5, title="Monte-Carlo Convergence"),
        "91_acf_pacf": lambda: pl.acf_pacf(np.diff(np.cumsum(rng.normal(0, 1, 200))), nlags=24, title="ARIMA Order Identification"),
        "92_decomposition": lambda: pl.seasonal_decomposition(10 + 3 * np.sin(2 * np.arange(120) * np.pi / 12) + 0.05 * np.arange(120) + rng.normal(0, 0.6, 120), period=12, title="Classical Decomposition"),
        "93_clustermap": lambda: pl.clustermap(rng.normal(0, 1, (12, 8)), standardize=True, row_labels=[f"R{i}" for i in range(12)], col_labels=[f"C{j}" for j in range(8)], title="Clustered Heatmap"),
        "94_corr_network": lambda: pl.correlation_network(rng.normal(0, 1, (7, 90)), threshold=0.15, labels=["GDP", "Pop", "Urban", "Edu", "Infra", "Tech", "Trade"], title="Correlation Network"),
        "95_polar_bar": lambda: pl.polar_bar(np.arange(0, 360, 30), {"Speed": np.abs(rng.normal(5, 2, 12))}, labels=["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N", "NE", "E", "SE"], zero_location="N", clockwise=True, title="Wind Rose (bars)"),
        "96_cvd_preview": lambda: pl.cvd_preview("nature_qual", title="Colorblind Check"),

        # ── evaluation & statistics (v5.0) ──
        "97_fit_comparison": lambda: pl.fit_comparison(np.linspace(1, 10, 45), 3.2 * np.linspace(1, 10, 45) ** 0.8 + rng.normal(0, 1.4, 45), title="Model Fit Comparison"),
        "98_roc_comparison": lambda: pl.roc_comparison(rng.integers(0, 2, 400), {"LR": rng.uniform(0, 1, 400) * 0.5 + rng.integers(0, 2, 400) * 0.30, "RF": rng.uniform(0, 1, 400) * 0.4 + rng.integers(0, 2, 400) * 0.45, "XGB": rng.uniform(0, 1, 400) * 0.3 + rng.integers(0, 2, 400) * 0.55}, title="Model ROC Comparison"),
        "99_calibration": lambda: pl.calibration_curve(rng.integers(0, 2, 400), np.clip(rng.integers(0, 2, 400) * 0.7 + rng.uniform(0, 0.5, 400), 0, 1), title="Calibration Curve"),
        "100_gain_lift": lambda: pl.gain_chart(rng.integers(0, 2, 400), rng.uniform(0, 1, 400) + rng.integers(0, 2, 400) * 0.4, title="Cumulative Gain / Lift"),
        "101_biplot": lambda: pl.biplot(rng.normal(0, 1, (120, 5)), labels=["GDP", "Pop", "Urban", "Edu", "Tech"], groups=["East"] * 60 + ["West"] * 60, title="PCA Biplot"),
        "102_ks_test": lambda: pl.ks_test(rng.normal(0, 1, 160), rng.normal(0.45, 1.1, 180), label1="2024", label2="2025", title="Two-Sample KS Test"),
        "103_range_plot": lambda: pl.range_plot(["Plan A", "Plan B", "Plan C", "Plan D"], [1.8, 2.6, 1.0, 2.2], [3.4, 4.1, 2.9, 3.8], [5.2, 6.4, 4.6, 5.9], xlabel="net benefit (10k)", title="Scenario Ranges"),
        "104_calendar": lambda: pl.calendar_heatmap(50 + 15 * np.sin(np.arange(210) / 9) + rng.normal(0, 6, 210), start_date="2025-01-01", cbar_label="demand", title="Daily Demand Heatmap"),
        "105_grouped_scatter": lambda: pl.grouped_scatter(rng.uniform(0, 10, 80), rng.uniform(0, 10, 80) * 0.6 + rng.normal(0, 1.2, 80), ["Online"] * 40 + ["Offline"] * 40, xlabel="ad spend", ylabel="sales", title="Segmented Elasticity"),
        "106_bland_altman": lambda: pl.bland_altman(rng.normal(50, 6, 70), rng.normal(50, 6, 70) + rng.normal(0, 1.8, 70), title="Method Agreement"),
        "107_tree_plot": lambda: pl.tree_plot(X=rng.normal(0, 1, (150, 4)), y=(lambda X: (X[:, 0] + 0.8 * X[:, 2] > 0).astype(int))(rng.normal(0, 1, (150, 4))), feature_names=["price", "ads", "quality", "brand"], class_names=["reject", "accept"], title="Decision Tree (max depth 3)"),

        # ── statistics & structure (v6.0) ──
        "108_joint_plot": lambda: pl.joint_plot(rng.uniform(0, 10, 90), 0.7 * rng.uniform(0, 10, 90) + rng.normal(0, 1.4, 90), xlabel="ad spend", ylabel="sales", title="Joint Distribution"),
        "109_forest_plot": lambda: pl.forest_plot(["Plan A", "Plan B", "Plan C", "Pooled"], [2.1, 1.4, 2.8, 2.2], [1.2, 0.6, 1.9, 1.7], [3.0, 2.2, 3.7, 2.7], pooled_line=2.2, title="Scenario Effect Sizes"),
        "110_strip_plot": lambda: pl.strip_plot({"Control": rng.normal(70, 8, 45), "Low dose": rng.normal(74, 9, 45), "High dose": rng.normal(79, 7, 45)}, overlay_box=True, ylabel="score", title="Strip + Box"),
        "111_smooth_plot": lambda: pl.smooth_plot(np.linspace(0, 10, 150), np.sin(np.linspace(0, 10, 150) * 1.2) * 2 + np.linspace(0, 4, 150) + rng.normal(0, 0.7, 150), method="lowess", title="Trend Smoothing"),
        "112_scatter_contour": lambda: pl.scatter_contour(rng.normal(2, 1, 500), rng.normal(1, 1.4, 500) * 0.8 + 0.3 * rng.normal(2, 1, 500), fill=True, title="Density Contours"),
        "113_diverging_bar": lambda: pl.diverging_bar(["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"], [3.2, -1.5, 2.1, -0.8, 4.1, -2.3], xlabel="YoY change (%)", title="Quarterly Contributions"),
        "114_cross_correlation": lambda: pl.cross_correlation(np.sin(np.arange(120) * 0.2), np.roll(np.sin(np.arange(120) * 0.2), 7) + rng.normal(0, 0.15, 120), max_lag=24, title="Lead-Lag Analysis"),
        "115_pareto_chart": lambda: pl.pareto_chart(list("ABCDE"), [42, 25, 15, 10, 8], ylabel="defects", title="Pareto Analysis"),
        "116_ternary_plot": lambda: pl.ternary_plot(*(lambda d: (d[:, 0], d[:, 1], d[:, 2]))(rng.dirichlet((2, 3, 4), 80)), labels=["A", "B", "C"], groups=["N"] * 40 + ["S"] * 40, title="Mixture Composition"),
        "117_donut_rings": lambda: pl.donut_rings([0.92, 0.78, 0.61], labels=["Accuracy", "Recall", "F1"], center_text="2025", title="KPI Rings"),

        # ── comparison & risk (v7.0) ──
        "118_dot_plot": lambda: pl.dot_plot(["Plan A", "Plan B", "Plan C", "Plan D", "Plan E"], [3.2, 1.8, 4.1, 2.5, 3.8], [2.9, 2.4, 3.6, 2.9, 3.3], label1="Round 1", label2="Round 2", title="Two-Round Comparison"),
        "119_volcano": lambda: pl.volcano_plot(rng.normal(0, 2, 350), rng.uniform(0, 1, 350) ** 2.2, labels=[f"feat{i}" for i in range(350)], title="Feature Fold-Change"),
        "120_confidence_ellipse": lambda: pl.confidence_ellipse(np.r_[rng.normal(2, 0.8, 60), rng.normal(5, 0.9, 60)], np.r_[rng.normal(1, 1, 60), rng.normal(3, 0.8, 60)], groups=["Class A"] * 60 + ["Class B"] * 60, title="Cluster Separation"),
        "121_stacked_hist": lambda: pl.stacked_histogram({"Low": rng.normal(0, 1, 400), "Mid": rng.normal(1.5, 1.1, 300), "High": rng.normal(3, 0.9, 200)}, title="Stacked Distributions"),
        "122_curve_sweep": lambda: pl.curve_sweep(lambda x, k: k * x / (1 + k * x), np.linspace(0.3, 3, 12), x=np.linspace(0, 6, 200), param_name="k", title="Parameter Sweep"),
        "123_phase_field": lambda: pl.phase_field(lambda x, y: -y, lambda x, y: x - y ** 3 + 0.3 * x ** 3, trajectories=[(0.5, 0.5), (2.2, 0.5), (-1.8, -1.2)], x_range=(-3, 3), y_range=(-3, 3), title="Phase Field"),
        "124_split_violin": lambda: pl.split_violin([rng.normal(70, 8, 150), rng.normal(74, 9, 150), rng.normal(68, 7, 150)], [rng.normal(75, 9, 150), rng.normal(72, 8, 150), rng.normal(70, 6, 150)], labels=["Trial 1", "Trial 2", "Trial 3"], left_label="Control", right_label="Treatment", title="Split Violin"),
        "125_risk_matrix": lambda: pl.risk_matrix({"数据缺失": (2, 4), "模型偏差": (4, 3), "计算超时": (3, 2), "成本超支": (4, 4), "政策变化": (1, 2)}, title="项目风险评估"),

        # ── diagnostics & reporting (v8.0) ──
        "126_beeswarm": lambda: pl.beeswarm({"Control": rng.normal(70, 8, 45), "Low dose": rng.normal(74, 9, 45), "High dose": rng.normal(79, 7, 45)}, overlay_box=True, title="Beeswarm + Box"),
        "127_control_chart": lambda: pl.control_chart(np.r_[rng.normal(50, 3, 56), [62, 63, 41]], title="SPC Control Chart"),
        "128_candlestick": lambda: _ohlc(),
        "129_delta_band": lambda: pl.delta_band(np.linspace(0, 12, 60), np.sin(np.linspace(0, 12, 60)) * 3 + 8 + np.linspace(0, 1.5, 60), np.sin(np.linspace(0, 12, 60) - 0.6) * 3 + 7.5, label_a="Policy", label_b="Baseline", title="Scenario Difference"),

        # ── flow diagrams (v9.0) ──
        "130_chord": lambda: pl.chord_chart(np.array([[0, 20, 10, 5], [15, 0, 12, 8], [8, 10, 0, 18], [6, 7, 14, 0]], float), labels=["East", "West", "North", "South"], title="Trade Flows"),

        # ── distribution & structure (v10.0) ──
        "131_raincloud": lambda: pl.raincloud({"Control": rng.normal(70, 8, 70), "Low dose": rng.normal(74, 9, 70), "High dose": rng.normal(79, 7, 70)}, ylabel="score", title="Raincloud Plot"),
        "132_circle_pack": lambda: pl.circle_pack({"Data": 35, "Model": 28, "Validation": 18, "Analysis": 12, "Writing": 7, "Review": 5}, title="Circle Packing"),
        "133_arc_diagram": lambda: pl.arc_diagram(["Collect", "Clean", "Model", "Validate", "Deploy"], [("Collect", "Clean", 3), ("Clean", "Model", 2), ("Model", "Validate", 2), ("Validate", "Deploy", 1), ("Collect", "Model", 1)], show_edge_labels=True, title="Pipeline Hand-offs"),

        # ── compose ──
        "70_panel_figure": lambda: panel_figure([
            {"type": "bar", "data": [4, 7, 5], "labels": ["A", "B", "C"], "title": "Accuracy"},
            {"type": "line", "data": {"M1": [1, 2, 3, 4]}, "x": [1, 2, 3, 4], "title": "Convergence"},
            {"type": "hist", "data": rng.normal(0, 1, 200), "title": "Residuals"},
            {"type": "radar", "data": ["a", "b", "c", "d"], "args": [[[3, 4, 2, 5]]], "names": ["Model"], "title": "Profile"},
        ], ncols=2, suptitle="Figure 1: Overall Results"),
    }

    print(f"Rendering {len(charts)} gallery images → {OUT}")
    for name, fn in charts.items():
        save(fn(), name)
    from gallery_html import write_html_index
    write_html_index(charts)
    write_html_index(charts)
    print(f"\nDone: {len(charts)} images in {OUT}")




if __name__ == "__main__":
    main()
