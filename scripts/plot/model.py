"""
model.py — Model analysis and validation charts.

Charts for mathematical modeling competitions:
    fit_curve              — regression / curve fitting with confidence bands
    residual_plot          — residual diagnostics
    confusion_matrix       — classification confusion matrix heatmap
    roc_curve              — ROC curve with AUC
    learning_curve         — learning curve (bias-variance)
    sensitivity_analysis   — tornado / sensitivity chart
    pareto_front           — Pareto front for multi-objective optimization
    validation_plot        — train/test score over folds
    feature_importance     — feature importance bar chart
    clustering_2d          — 2D clustering scatter with centroids
    decision_boundary      — decision boundary visualization
    correlation_matrix     — correlation matrix heatmap with annotations
"""

from __future__ import annotations

from typing import Optional, Sequence, Callable

import matplotlib.pyplot as plt
import numpy as np

from .palette import auto_colors, get_palette, NEUTRAL, ACCENT
from .styles import apply_style
from .utils import setup_figure, save_figure, axis_config, auto_layout


# ──────────────────────────────────────────────
#  FIT  CURVE  (regression fitting)
# ──────────────────────────────────────────────

def fit_curve(
    x: Sequence[float],
    y: Sequence[float],
    func: Callable | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    figsize: tuple = (8, 5),
    data_color: str = "#2E86AB",
    fit_color: str = "#C73E1D",
    data_size: float = 50,
    data_alpha: float = 0.7,
    fit_width: float = 2.5,
    show_ci: bool = True,
    ci_alpha: float = 0.15,
    ci_degree: int = 2,
    show_equation: bool = True,
    equation_color: str = "#666666",
    grid: str = "both",
    legend: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Plot data points with a fitted curve and confidence interval.

    Parameters
    ----------
    x, y : array-like
        Data points.
    func : callable, optional
        Fitting function. If None, uses polynomial fit.
    show_ci : bool
        Show confidence interval band (uses std of residuals).
    ci_degree : int
        Polynomial degree for the fit line (when func is None).
    show_equation : bool
        Display the fit equation as text.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)

    # Scatter data
    ax.scatter(x_arr, y_arr, c=data_color, s=data_size, alpha=data_alpha,
               edgecolors="white", linewidth=0.5, label="Data", zorder=3)

    if func is None:
        # Polynomial fit
        coeffs = np.polyfit(x_arr, y_arr, ci_degree)
        x_fit = np.linspace(x_arr.min(), x_arr.max(), 200)
        y_fit = np.polyval(coeffs, x_fit)
        ax.plot(x_fit, y_fit, color=fit_color, linewidth=fit_width,
                label=f"Fit (degree {ci_degree})", zorder=5)

        if show_ci:
            residuals = y_arr - np.polyval(coeffs, x_arr)
            std = np.std(residuals)
            ax.fill_between(x_fit, y_fit - std, y_fit + std,
                            color=fit_color, alpha=ci_alpha,
                            label=f"±1σ (σ={std:.3f})")

        if show_equation:
            eq_str = f"y = {coeffs[0]:.3f}"
            for c in coeffs[1:]:
                eq_str += f" + {c:.3f}" if c >= 0 else f" - {abs(c):.3f}"
            # Simplify display
            eq_parts = []
            if ci_degree == 1:
                eq_parts = [f"{coeffs[0]:.3f}x + {coeffs[1]:.3f}"]
            elif ci_degree == 2:
                eq_parts = [
                    f"{coeffs[0]:.3f}x²",
                    f"+ {coeffs[1]:.3f}x" if coeffs[1] >= 0 else f"- {abs(coeffs[1]):.3f}x",
                    f"+ {coeffs[2]:.3f}" if coeffs[2] >= 0 else f"- {abs(coeffs[2]):.3f}",
                ]
            ax.text(
                0.02, 0.95, " ".join(eq_parts),
                transform=ax.transAxes, fontsize=9,
                color=equation_color, va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="none"),
            )
    else:
        # Custom function — sample points along x
        x_fit = np.linspace(x_arr.min(), x_arr.max(), 200)
        y_fit = np.array([func(xi) for xi in x_fit])
        ax.plot(x_fit, y_fit, color=fit_color, linewidth=fit_width,
                label="Fitted curve", zorder=5)

        if show_ci:
            residuals = y_arr - np.array([func(xi) for xi in x_arr])
            std = np.std(residuals)
            ax.fill_between(x_fit, y_fit - std, y_fit + std,
                            color=fit_color, alpha=ci_alpha)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    if legend:
        ax.legend(frameon=False, fontsize=9, loc="best")

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  RESIDUAL  PLOT
# ──────────────────────────────────────────────

def residual_plot(
    x: Sequence[float],
    y_true: Sequence[float],
    y_pred: Sequence[float],
    title: str | None = "Residual Plot",
    xlabel: str = "Predicted Values",
    ylabel: str = "Residuals",
    figsize: tuple = (8, 5),
    data_color: str = "#2E86AB",
    ref_color: str = "#C73E1D",
    data_size: float = 40,
    grid: str = "both",
    show_r_squared: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Residual plot for model diagnostics.

    Parameters
    ----------
    y_true : array-like
        Actual values.
    y_pred : array-like
        Predicted values.
    show_r_squared : bool
        Display R² value.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    x_arr = np.array(x, dtype=float)
    y_true_arr = np.array(y_true, dtype=float)
    y_pred_arr = np.array(y_pred, dtype=float)
    residuals = y_true_arr - y_pred_arr

    ax.scatter(y_pred_arr, residuals, c=data_color, s=data_size,
               alpha=0.7, edgecolors="white", linewidth=0.5, zorder=3)

    # Reference lines
    ax.axhline(y=0, color=ref_color, linestyle="--", linewidth=1, alpha=0.8,
               label="Zero residual")

    # ±1σ band
    std = np.std(residuals)
    ax.axhline(y=std, color="#999999", linestyle=":", linewidth=0.8, alpha=0.5)
    ax.axhline(y=-std, color="#999999", linestyle=":", linewidth=0.8, alpha=0.5)
    ax.text(
        y_pred_arr.min() + (y_pred_arr.max() - y_pred_arr.min()) * 0.02, std * 1.1,
        f"±1σ = ±{std:.3f}", fontsize=8, color="#666666",
    )

    if show_r_squared:
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y_true_arr - np.mean(y_true_arr)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        ax.text(
            0.02, 0.95, f"R² = {r2:.4f}",
            transform=ax.transAxes, fontsize=10,
            color="#333333", va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="none"),
        )

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    ax.legend(frameon=False, fontsize=9, loc="upper right")

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CONFUSION  MATRIX
# ──────────────────────────────────────────────

def confusion_matrix(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    labels: Optional[Sequence[str]] = None,
    title: str = "Confusion Matrix",
    figsize: tuple = (6, 5),
    show_values: bool = True,
    show_normalize: bool = False,
    cmap: str = "Blues",
    font_color: str = "#333333",
    cell_fontsize: float = 14,
    label_fontsize: float = 11,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Confusion matrix as a heatmap.

    Parameters
    ----------
    y_true, y_pred : array-like
        Ground truth and predicted labels.
    labels : list of str, optional
        Class labels. Auto-detected if None.
    show_normalize : bool
        Show normalized (row percentage) values instead of counts.
    cmap : str
        Colormap name.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)

    if labels is None:
        unique_labels = sorted(set(y_true_arr) | set(y_pred_arr))
    else:
        unique_labels = list(labels)

    n_classes = len(unique_labels)
    # Map raw label values to indices (use actual values from data)
    all_values = sorted(set(y_true_arr.tolist() + y_pred_arr.tolist()))
    value_to_idx = {v: i for i, v in enumerate(all_values)}
    # Display labels for axes
    if labels is not None and len(labels) == n_classes:
        display_labels = list(labels)
    else:
        display_labels = [str(v) for v in all_values]

    # Build matrix
    matrix = np.zeros((n_classes, n_classes), dtype=int)
    for t, p in zip(y_true_arr, y_pred_arr):
        ti = value_to_idx[int(t)]
        pi = value_to_idx[int(p)]
        matrix[ti, pi] += 1

    # Optionally normalize
    display_matrix = matrix.astype(float)
    if show_normalize:
        row_sums = display_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        display_matrix = display_matrix / row_sums

    im = ax.imshow(display_matrix, cmap=cmap, aspect="auto")

    # Annotate cells
    for i in range(n_classes):
        for j in range(n_classes):
            val = matrix[i, j]
            if show_normalize:
                pct = val / matrix[i].sum() * 100 if matrix[i].sum() > 0 else 0
                text = f"{pct:.0f}%"
            else:
                text = f"{val}"

            # Determine text color based on background
            ratio = display_matrix[i, j] / display_matrix.max() if display_matrix.max() > 0 else 0
            tc = "#333333" if ratio > 0.6 else "#333333"

            ax.text(
                j, i, text,
                ha="center", va="center",
                fontsize=cell_fontsize,
                fontweight="bold" if i == j else "normal",
                color=tc,
            )

    # Labels
    ax.set_xticks(range(n_classes))
    ax.set_yticks(range(n_classes))
    ax.set_xticklabels(display_labels, fontsize=label_fontsize)
    ax.set_yticklabels(display_labels, fontsize=label_fontsize)
    ax.set_xlabel("Predicted", fontsize=11)
    ax.set_ylabel("Actual", fontsize=11)

    # Set x-label offset
    ax.tick_params(axis="x", labelbottom=True)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.08)
    cbar.set_label("Count" if not show_normalize else "Probability", fontsize=10)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ROC  CURVE
# ──────────────────────────────────────────────

def roc_curve(
    y_true: Sequence[int],
    y_score: Sequence[float],
    title: str = "ROC Curve",
    figsize: tuple = (6, 6),
    line_color: str = "#2E86AB",
    line_width: float = 2.5,
    show_auc: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    ROC curve with AUC value.

    Parameters
    ----------
    y_true : array-like of {0, 1}
        Ground truth labels.
    y_score : array-like of float
        Prediction scores.
    show_auc : bool
        Display AUC value.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    from sklearn.metrics import roc_curve as _roc_curve, roc_auc_score
    fpr, tpr, _ = _roc_curve(y_true, y_score)
    auc = roc_auc_score(y_true, y_score)

    ax.plot(fpr, tpr, color=line_color, linewidth=line_width,
            label=f"AUC = {auc:.4f}" if show_auc else "ROC")
    ax.plot([0, 1], [0, 1], color="#999999", linestyle="--", linewidth=1,
            label="Random")

    ax.fill_between(fpr, tpr, alpha=0.1, color=line_color)

    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    ax.legend(frameon=False, fontsize=10, loc="lower right")

    axis_config(ax, grid="both")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")

    ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  LEARNING  CURVE
# ──────────────────────────────────────────────

def learning_curve(
    X: Sequence,
    y: Sequence,
    estimator: object | None = None,
    cv: int = 5,
    title: str = "Learning Curve",
    figsize: tuple = (8, 5),
    train_color: str = "#2E86AB",
    test_color: str = "#C73E1D",
    grid: str = "both",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Plot learning curve (bias-variance tradeoff).

    Parameters
    ----------
    X, y : array-like
        Training data.
    estimator : sklearn estimator, optional
        If None, uses a simple model.
    cv : int
        Cross-validation folds.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    from sklearn.model_selection import learning_curve as _learning_curve
    from sklearn.model_selection import ShuffleSplit

    if estimator is None:
        from sklearn.ensemble import RandomForestClassifier
        estimator = RandomForestClassifier(random_state=42)

    train_sizes, train_scores, test_scores = _learning_curve(
        estimator, X, y,
        cv=ShuffleSplit(n_splits=cv, random_state=42),
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring="accuracy",
        refit=False,
        n_jobs=1,
    )

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    test_mean = test_scores.mean(axis=1)
    test_std = test_scores.std(axis=1)

    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                    alpha=0.15, color=train_color)
    ax.plot(train_sizes, train_mean, color=train_color, linewidth=2,
            label="Training score")

    ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std,
                    alpha=0.15, color=test_color)
    ax.plot(train_sizes, test_mean, color=test_color, linewidth=2,
            label="Validation score")

    ax.set_xlabel("Training set size", fontsize=11)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=10, loc="lower right")

    axis_config(ax, grid=grid)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SENSITIVITY  ANALYSIS  (tornado diagram)
# ──────────────────────────────────────────────

def sensitivity_analysis(
    parameters: Sequence[str],
    low_values: Sequence[float],
    high_values: Sequence[float],
    base_value: float | None = None,
    title: str = "Sensitivity Analysis",
    figsize: tuple = (8, 5),
    low_color: str = "#4D96FF",
    high_color: str = "#FF6B6B",
    show_values: bool = True,
    value_fmt: str = "{:.3f}",
    grid: str = "x",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Tornado chart for sensitivity analysis.

    Parameters
    ----------
    parameters : list of str
        Parameter names.
    low_values : list of float
        Output values when each parameter is at low bound.
    high_values : list of float
        Output values when each parameter is at high bound.
    base_value : float, optional
        Base case output value (drawn as reference line).
    """
    fig, ax = setup_figure(figsize, **kwargs)
    n = len(parameters)
    y_pos = np.arange(n)

    if base_value is None:
        base_value = (np.mean(low_values) + np.mean(high_values)) / 2

    # Calculate deviations from base
    low_dev = np.array(low_values) - base_value
    high_dev = np.array(high_values) - base_value

    ax.barh(
        y_pos, low_dev, height=0.6, color=low_color,
        alpha=0.7, edgecolor="white", linewidth=0.5,
        label="Parameter ↓",
    )
    ax.barh(
        y_pos, high_dev, height=0.6, color=high_color,
        alpha=0.7, edgecolor="white", linewidth=0.5,
        label="Parameter ↑",
    )

    if show_values:
        for i, (ld, hd) in enumerate(zip(low_dev, high_dev)):
            if ld < 0:
                ax.text(ld - abs(ld) * 0.05, i, value_fmt.format(ld),
                        va="center", ha="right", fontsize=8, color=low_color)
            if hd > 0:
                ax.text(hd + abs(hd) * 0.05, i, value_fmt.format(hd),
                        va="center", ha="left", fontsize=8, color=high_color)

    ax.axvline(x=0, color="#666666", linewidth=1, linestyle="-")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(parameters, fontsize=10)
    ax.set_xlabel("Output change", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9, loc="lower right")

    axis_config(ax, grid=grid)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PARETO  FRONT
# ──────────────────────────────────────────────

def pareto_front(
    objectives: Sequence[Sequence[float]],
    labels: Optional[Sequence[str]] = None,
    title: str = "Pareto Front",
    xlabel: str = "Objective 1",
    ylabel: str = "Objective 2",
    figsize: tuple = (8, 6),
    palette: str = "nature_qual",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Plot Pareto front for multi-objective optimization.

    Parameters
    ----------
    objectives : list of arrays
        Each array has shape (N, M) where M is number of objectives.
        Pass a list with one element for single solution set, or
        multiple for comparison.
    labels : list of str, optional
        Legend labels.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    colors = auto_colors(len(objectives), palette)

    for i, (obj, lbl) in enumerate(zip(objectives, labels or range(len(objectives)))):
        obj = np.array(obj)
        if obj.ndim == 1:
            obj = obj.reshape(-1, 2)
        x_obj = obj[:, 0]
        y_obj = obj[:, 1] if obj.shape[1] > 1 else np.zeros_like(x_obj)
        ax.scatter(x_obj, y_obj, c=colors[i], s=60, alpha=0.7,
                   edgecolors="white", linewidth=0.5, label=lbl, zorder=3)

    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9)

    axis_config(ax, grid="both")
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  VALIDATION  PLOT  (train/test over folds)
# ──────────────────────────────────────────────

def validation_plot(
    train_scores: Sequence[Sequence[float]],
    test_scores: Sequence[Sequence[float]],
    metrics: Optional[Sequence[str]] = None,
    title: str = "Validation Across Folds",
    figsize: tuple = (8, 5),
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Bar chart of validation scores across CV folds.

    Parameters
    ----------
    train_scores : list of arrays
        Training scores per fold.
    test_scores : list of arrays
        Test/validation scores per fold.
    metrics : list of str, optional
        Metric names (one per score set).
    """
    n_metrics = len(train_scores)
    colors = auto_colors(n_metrics, palette="nature_qual")

    apply_style("nature")
    fig, axes = plt.subplots(
        1, n_metrics, figsize=figsize, sharey=False, **kwargs,
    )
    if n_metrics == 1:
        axes = [axes]

    for i, (tr, te, ax) in enumerate(zip(train_scores, test_scores, axes)):
        metrics_label = metrics[i] if metrics else f"Metric {i+1}"
        n_folds = len(tr)
        x = np.arange(n_folds)

        tr_arr = np.array(tr)
        te_arr = np.array(te)

        ax.bar(x - 0.2, tr_arr, width=0.35, label="Training",
               color=colors[i % len(colors)], alpha=0.7, edgecolor="white", linewidth=0.5)
        ax.bar(x + 0.2, te_arr, width=0.35, label="Validation",
               color="#C73E1D", alpha=0.7, edgecolor="white", linewidth=0.5)

        ax.axhline(y=tr_arr.mean(), color=colors[i % len(colors)], linestyle="--", linewidth=1, alpha=0.5)
        ax.axhline(y=te_arr.mean(), color="#C73E1D", linestyle="--", linewidth=1, alpha=0.5)

        ax.set_xticks(x)
        ax.set_xticklabels([f"F{i+1}" for i in range(n_folds)], fontsize=8)
        ax.set_title(metrics_label, fontsize=10)
        ax.legend(frameon=False, fontsize=8)

        axis_config(ax, grid="y")
        ax.tick_params(axis="both", labelsize=8)

    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold", y=1.02)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  FEATURE  IMPORTANCE
# ──────────────────────────────────────────────

def feature_importance(
    features: Sequence[str],
    importances: Sequence[float],
    title: str = "Feature Importance",
    figsize: tuple = (8, 5),
    palette: str = "nature_qual",
    horizontal: bool = True,
    show_values: bool = True,
    value_fmt: str = "{:.4f}",
    top_n: int | None = None,
    grid: str = "x",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Feature importance bar chart.

    Parameters
    ----------
    features : list of str
        Feature names.
    importances : list of float
        Importance values.
    top_n : int, optional
        Show only top N features.
    """
    if top_n and top_n < len(features):
        idx = np.argsort(importances)[::-1][:top_n]
        features = [features[i] for i in idx]
        importances = [importances[i] for i in idx]

    fig, ax = setup_figure(figsize, **kwargs)
    colors = auto_colors(len(features), palette)

    if horizontal:
        ax.barh(
            range(len(features)), importances,
            color=colors, edgecolor="white", linewidth=0.5,
            height=0.6,
        )
        ax.set_yticks(range(len(features)))
        ax.set_yticklabels(features, fontsize=9)
        if show_values:
            for i, imp in enumerate(importances):
                ax.text(imp + max(importances) * 0.02, i,
                        value_fmt.format(imp), va="center",
                        fontsize=8, color="#333333")
        axis_config(ax, grid="x")
    else:
        ax.bar(
            range(len(features)), importances,
            color=colors, edgecolor="white", linewidth=0.5,
            width=0.6,
        )
        ax.set_xticks(range(len(features)))
        ax.set_xticklabels(features, fontsize=9, rotation=30, ha="right")
        if show_values:
            for i, imp in enumerate(importances):
                ax.text(i, imp + max(importances) * 0.02,
                        value_fmt.format(imp), ha="center",
                        va="bottom", fontsize=8, color="#333333")
        axis_config(ax, grid="y")

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CLUSTERING  2D
# ──────────────────────────────────────────────

def clustering_2d(
    X: Sequence[Sequence[float]],
    labels: Sequence[int],
    centroids: Optional[Sequence[Sequence[float]]] = None,
    title: str = "2D Clustering",
    figsize: tuple = (8, 6),
    palette: str = "clustering",
    marker_size: float = 50,
    alpha: float = 0.7,
    centroid_size: float = 200,
    grid: str = "both",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    2D scatter plot of clustering results.

    Parameters
    ----------
    X : array of shape (N, 2)
        Feature matrix.
    labels : array of int
        Cluster labels.
    centroids : array of shape (K, 2), optional
        Cluster centroids.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    X_arr = np.array(X)
    labels_arr = np.array(labels)

    unique_labels = sorted(set(labels_arr))
    colors = auto_colors(len(unique_labels), palette)
    label_to_color = {l: c for l, c in zip(unique_labels, colors)}

    for label in unique_labels:
        mask = labels_arr == label
        ax.scatter(
            X_arr[mask, 0], X_arr[mask, 1],
            c=label_to_color[label], s=marker_size, alpha=alpha,
            edgecolors="white", linewidth=0.5, label=f"Cluster {label}",
            zorder=3,
        )

    if centroids is not None:
        centroids = np.array(centroids)
        for i, c in enumerate(centroids):
            ax.scatter(
                c[0], c[1], c=label_to_color.get(i, colors[i % len(colors)]),
                s=centroid_size, marker="*", edgecolors="black", linewidth=1,
                zorder=5, label=f"Centroid {i}",
            )

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9, loc="best")

    axis_config(ax, grid=grid)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DECISION  BOUNDARY
# ──────────────────────────────────────────────

def decision_boundary(
    X: Sequence[Sequence[float]],
    y: Sequence[int],
    classifier: object | None = None,
    title: str = "Decision Boundary",
    figsize: tuple = (7, 6),
    palette: str = "classification",
    grid: str = "both",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Decision boundary visualization for a classifier.

    Parameters
    ----------
    X : array of shape (N, 2)
    y : array of int
    classifier : fitted sklearn classifier, optional
        If None, uses a default model.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    X_arr = np.array(X)
    y_arr = np.array(y)

    if classifier is None:
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier(random_state=42)
        classifier.fit(X_arr, y_arr)

    unique_labels = sorted(set(y_arr))
    colors = auto_colors(len(unique_labels), palette)
    label_to_color = {l: c for l, c in zip(unique_labels, colors)}

    # Plot scatter
    for label in unique_labels:
        mask = y_arr == label
        ax.scatter(
            X_arr[mask, 0], X_arr[mask, 1],
            c=label_to_color[label], s=40, alpha=0.7,
            edgecolors="white", linewidth=0.5, label=f"Class {label}",
            zorder=3,
        )

    # Plot decision boundary
    x_min, x_max = X_arr[:, 0].min() - 0.5, X_arr[:, 0].max() + 0.5
    y_min, y_max = X_arr[:, 1].min() - 0.5, X_arr[:, 1].max() + 0.5
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 200),
        np.linspace(y_min, y_max, 200),
    )
    Z = classifier.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, alpha=0.15, cmap="coolwarm", levels=len(unique_labels) + 1)
    ax.contour(xx, yy, Z, colors="#666666", linewidths=0.8, linestyles="--")

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9)

    axis_config(ax, grid=grid)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CORRELATION  MATRIX
# ──────────────────────────────────────────────

def correlation_matrix(
    data,
    labels: Optional[Sequence[str]] = None,
    title: str = "Correlation Matrix",
    figsize: tuple | None = None,
    cmap: str = "RdBu_r",
    vmin: float = -1,
    vmax: float = 1,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    font_color: str = "#333333",
    cell_fontsize: float | None = None,
    label_fontsize: float = 9,
    diagonal_color: str | None = None,
    highlight: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Correlation matrix as an annotated heatmap.

    Parameters
    ----------
    data : array-like or DataFrame
        Data to compute correlation from.
    labels : list of str, optional
        Variable names.
    cmap : str
        Colormap (default 'RdBu_r' — red=positive, blue=negative).
    vmin, vmax : float
        Colormap range.
    show_values : bool
        Annotate cells with correlation values.
    diagonal_color : str, optional
        Override diagonal cell color.
    highlight : bool
        Add border to high-correlation cells.
    """
    if hasattr(data, "corr"):
        corr = data.corr().values
        if labels is None:
            labels = list(data.columns)
    else:
        data_arr = np.array(data, dtype=float)
        corr = np.corrcoef(data_arr, rowvar=False)
        if labels is None:
            labels = [f"Var {i+1}" for i in range(corr.shape[0])]

    labels = list(labels)
    n = len(labels)
    fig_size = figsize or (max(6, n * 0.8), max(5, n * 0.7))

    fig, ax = setup_figure(figsize=fig_size, **kwargs)

    im = ax.imshow(corr, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")

    if show_values:
        if cell_fontsize is None:
            cell_fontsize = max(6, min(14, 20 - n * 0.5))
        for i in range(n):
            for j in range(n):
                val = corr[i, j]
                if diagonal_color and i == j:
                    ax.text(j, i, value_fmt.format(val),
                            ha="center", va="center", fontsize=cell_fontsize,
                            color="white", fontweight="bold")
                else:
                    # Text color based on background
                    ratio = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
                    tc = "white" if ratio > 0.6 else "#333333"
                    fw = "bold" if abs(val) > 0.7 else "normal"
                    ax.text(j, i, value_fmt.format(val),
                            ha="center", va="center", fontsize=cell_fontsize,
                            color=tc, fontweight=fw)

    if diagonal_color and show_values:
        for i in range(n):
            ax.text(i, i, value_fmt.format(corr[i, i]),
                    ha="center", va="center", fontsize=cell_fontsize,
                    color="white", fontweight="bold")

    # Labels
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, fontsize=label_fontsize, rotation=45, ha="right")
    ax.set_yticklabels(labels, fontsize=label_fontsize)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.08)
    cbar.set_label("Correlation", fontsize=10)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "fit_curve", "residual_plot", "confusion_matrix",
    "roc_curve", "learning_curve", "sensitivity_analysis",
    "pareto_front", "validation_plot", "feature_importance",
    "clustering_2d", "decision_boundary", "correlation_matrix",
]