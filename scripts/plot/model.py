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
    y_pred: Optional[Sequence[int]] = None,
    labels: Optional[Sequence[str]] = None,
    title: str = "Confusion Matrix",
    figsize: tuple = (6, 5),
    show_values: bool = True,
    show_normalize: bool = False,
    cmap: str = "Blues",
    font_color: str = "#333333",
    cell_fontsize: float = 14,
    label_fontsize: float = 11,
    class_names: Optional[Sequence[str]] = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Confusion matrix as a heatmap.

    Parameters
    ----------
    y_true : array-like
        Ground truth labels — or a precomputed 2-D confusion matrix
        (pass the matrix as ``y_true`` and leave ``y_pred`` empty).
    y_pred : array-like, optional
        Predicted labels (not used when a precomputed matrix is given).
    labels : list of str, optional
        Class labels. Auto-detected if None. Alias: ``class_names``.
    show_normalize : bool
        Show normalized (row percentage) values instead of counts.
    cmap : str
        Colormap name.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    labels = labels if labels is not None else class_names

    precomputed = np.asarray(y_true)
    if precomputed.ndim == 2:
        # Precomputed confusion matrix — render directly
        matrix = precomputed.astype(float)
        display_labels = list(labels) if labels else [str(i) for i in range(matrix.shape[0])]
        n_classes = matrix.shape[0]
        if show_normalize:
            row_sums = matrix.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            display_matrix = matrix / row_sums
        else:
            display_matrix = matrix
    else:
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
                text = f"{val:.0f}" if isinstance(val, float) else f"{val}"

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
    y_values: Optional[Sequence[float]] = None,
    labels: Optional[Sequence[str]] = None,
    title: str = "Pareto Front",
    xlabel: str = "Objective 1",
    ylabel: str = "Objective 2",
    figsize: tuple = (8, 6),
    palette: str = "nature_qual",
    show_front: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Plot Pareto front for multi-objective optimization.

    Parameters
    ----------
    objectives : array-like
        Either an (N, 2) point set / list of point sets for comparison,
        or a 1-D array of objective-1 values paired with ``y_values``.
    y_values : array-like, optional
        Objective-2 values when ``objectives`` is 1-D.
    labels : list of str, optional
        Legend labels per solution set.
    show_front : bool
        Connect the non-dominated points with a step line.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    # Two 1-D arrays → single point cloud
    if y_values is not None and np.ndim(objectives) == 1:
        objectives = [np.column_stack([np.asarray(objectives, float),
                                       np.asarray(y_values, float)])]
        labels = labels or ["Solutions"]

    sets = objectives if isinstance(objectives, (list, tuple)) and (
        len(objectives) > 0 and np.ndim(objectives[0]) == 2
    ) else [np.asarray(objectives)]

    colors = auto_colors(len(sets), palette)
    for i, (obj, lbl) in enumerate(zip(sets, labels or range(len(sets)))):
        obj = np.asarray(obj, dtype=float)
        if obj.ndim == 1:
            obj = obj.reshape(-1, 2)
        x_obj = obj[:, 0]
        y_obj = obj[:, 1] if obj.shape[1] > 1 else np.zeros_like(x_obj)
        ax.scatter(x_obj, y_obj, c=colors[i], s=60, alpha=0.7,
                   edgecolors="white", linewidth=0.5, label=lbl, zorder=3)

        if show_front and len(x_obj) >= 2:
            # Non-dominated (minimize both) points
            order = np.lexsort((y_obj, x_obj))
            front = []
            best_y = np.inf
            for k in order:
                if y_obj[k] < best_y:
                    front.append(k)
                    best_y = y_obj[k]
            front = np.array(front)
            ax.step(np.sort(x_obj[front]), y_obj[np.argsort(x_obj[front])],
                    where="post", color=colors[i], lw=1.6, alpha=0.85,
                    zorder=2)

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
    labels: Optional[Sequence[int]] = None,
    centroids: Optional[Sequence[Sequence[float]]] = None,
    title: str = "2D Clustering",
    figsize: tuple = (8, 6),
    palette: str = "clustering",
    marker_size: float = 50,
    alpha: float = 0.7,
    centroid_size: float = 200,
    grid: str = "both",
    n_clusters: Optional[int] = None,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    2D scatter plot of clustering results.

    Parameters
    ----------
    X : array of shape (N, 2)
        Feature matrix.
    labels : array of int, optional
        Cluster labels. If omitted, K-Means clustering is fitted
        automatically (``n_clusters`` or a sqrt heuristic).
    centroids : array of shape (K, 2), optional
        Cluster centroids.
    n_clusters : int, optional
        K for auto-clustering when ``labels`` is not given.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    X_arr = np.array(X, dtype=float)

    if labels is None:
        try:
            from sklearn.cluster import KMeans
        except ImportError as e:
            raise ValueError(
                "clustering_2d needs labels, or scikit-learn installed "
                "for automatic K-Means clustering."
            ) from e
        k = n_clusters or int(np.clip(np.sqrt(len(X_arr) / 2), 2, 8))
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        labels = km.fit_predict(X_arr)
        if centroids is None:
            centroids = km.cluster_centers_

    labels_arr = np.asarray(labels)

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
    show_significance: bool = False,
    n_obs: int | None = None,
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
    show_significance : bool
        Append significance stars to each cell — requires ``n_obs``
        (two-sided t approximation: * p<0.05, ** p<0.01, *** p<0.001).
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
    star_mat = None
    if show_significance:
        if n_obs is None:
            n_obs = (len(data) if hasattr(data, "__len__")
                     and not np.asarray(data).ndim == 2 and False
                     else (np.asarray(data).shape[0]
                           if np.asarray(data).ndim == 2 else None))
        if n_obs and n_obs > 2:
            from scipy import stats as _sps
            r_clip = np.clip(corr, -0.999999, 0.999999)
            t_stat = r_clip * np.sqrt((n_obs - 2) / (1 - r_clip ** 2))
            p_mat = 2 * _sps.t.sf(np.abs(t_stat), n_obs - 2)
            star_mat = np.empty_like(p_mat, dtype=object)
            for i in range(n):
                for j in range(n):
                    if i == j:
                        star_mat[i, j] = ""
                    elif p_mat[i, j] < 0.001:
                        star_mat[i, j] = "***"
                    elif p_mat[i, j] < 0.01:
                        star_mat[i, j] = "**"
                    elif p_mat[i, j] < 0.05:
                        star_mat[i, j] = "*"
                    else:
                        star_mat[i, j] = ""
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
                    text = value_fmt.format(val)
                    if star_mat is not None and star_mat[i, j]:
                        text += star_mat[i, j]
                    ax.text(j, i, text,
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
    "pr_curve", "prediction_vs_actual", "regression_panel",
    "elbow_plot", "silhouette_plot", "scree_plot",
]

# ──────────────────────────────────────────────
#  FIT  COMPARISON  (multiple models, one figure)
# ──────────────────────────────────────────────

def fit_comparison(
    x: Sequence[float],
    y: Sequence[float],
    models: Sequence[str] = ("linear", "quadratic", "power", "exponential"),
    title: str | None = None,
    xlabel: str = "x",
    ylabel: str = "y",
    figsize: tuple = (9, 5.5),
    palette: str = "nature_qual",
    data_color: str = "#333333",
    data_size: float = 34,
    n_grid: int = 250,
    show_table: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Fit several candidate models to the same data and rank them by R² —
    the figure for every "which functional form fits best" discussion.

    Parameters
    ----------
    models : sequence of str
        Any of 'linear', 'quadratic', 'cubic', 'power', 'exponential',
        'logarithmic'. Only models valid for the data range are drawn
        (e.g. power/log/exp need strictly positive values).

    Returns
    -------
    Figure
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    order = np.argsort(x_arr)
    xs, ys = x_arr[order], y_arr[order]
    xd = np.linspace(xs.min(), xs.max(), n_grid)

    pos = xs > 0
    candidates = {
        "linear": lambda xv, yv: np.polyfit(xv, yv, 1),
        "quadratic": lambda xv, yv: np.polyfit(xv, yv, 2),
        "cubic": lambda xv, yv: np.polyfit(xv, yv, 3),
    }

    def _r2(yv, yhat):
        ss_res = float(np.sum((yv - yhat) ** 2))
        ss_tot = float(np.sum((yv - yv.mean()) ** 2)) or 1.0
        return 1.0 - ss_res / ss_tot

    results = []  # (name, predict-on-xd, predict-on-xs, r2)
    for m in models:
        m = m.lower()
        try:
            if m in candidates:
                coeffs = candidates[m](xs, ys)
                yd = np.polyval(coeffs, xd)
                r2 = _r2(ys, np.polyval(coeffs, xs))
                results.append((m, yd, r2))
            elif m == "power" and pos.all():
                b, log_a = np.polyfit(np.log(xs), np.log(np.clip(ys, 1e-12, None)), 1)
                yd = np.exp(log_a) * xd ** b
                r2 = _r2(np.log(np.clip(ys, 1e-12, None)),
                         log_a + b * np.log(xs))
                results.append((f"power (y={np.exp(log_a):.2g}·x^{b:.2f})", yd, r2))
            elif m == "exponential" and pos.all():
                b, log_a = np.polyfit(xs, np.log(np.clip(ys, 1e-12, None)), 1)
                yd = np.exp(log_a) * np.exp(b * xd)
                r2 = _r2(np.log(np.clip(ys, 1e-12, None)), log_a + b * xs)
                results.append((f"exp (y={np.exp(log_a):.2g}·e^({b:.2f}x))", yd, r2))
            elif m == "logarithmic" and pos.all():
                b, a = np.polyfit(np.log(xs), ys, 1)
                yd = a + b * np.log(xd)
                r2 = _r2(ys, a + b * np.log(xs))
                results.append(("logarithmic", yd, r2))
        except (ValueError, np.linalg.LinAlgError):
            continue  # model not applicable to this data

    if not results:
        raise ValueError(
            "No candidate models applicable — power/exp/log need strictly "
            "positive x and y."
        )
    results.sort(key=lambda r: r[2], reverse=True)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.scatter(xs, ys, s=data_size, color=data_color, alpha=0.75,
               edgecolors="white", lw=0.5, zorder=4, label="data")
    colors = auto_colors(len(results), palette)
    for i, ((name, yd, r2), c) in enumerate(zip(results, colors)):
        ax.plot(xd, yd, color=c, lw=1.9,
                label=f"{name}  (R²={r2:.4f})", zorder=3)

    if show_table and len(results) > 1:
        table = "Best model: " + results[0][0] + f"  (R²={results[0][2]:.4f})"
        ax.text(0.02, 0.96, table, transform=ax.transAxes, va="top",
                fontsize=9, color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  MULTI-MODEL  ROC  COMPARISON
# ──────────────────────────────────────────────

def roc_comparison(
    y_true: Sequence[int],
    scores: dict,
    title: str = "ROC Comparison",
    figsize: tuple = (7, 6.5),
    palette: str = "nature_qual",
    show_diagonal: bool = True,
    auc_table: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Overlay ROC curves of several models on one figure with an AUC
    ranking — pass ``scores = {"LR": ..., "RF": ..., "XGB": ...}``.

    Returns
    -------
    Figure
    """
    from sklearn.metrics import roc_curve, roc_auc_score

    y_arr = np.asarray(y_true)
    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    colors = auto_colors(len(scores), palette)
    ranked = []

    for (name, score), c in zip(scores.items(), colors):
        fpr, tpr, _ = roc_curve(y_arr, np.asarray(score, dtype=float))
        auc = roc_auc_score(y_arr, np.asarray(score, dtype=float))
        ranked.append((float(auc), str(name)))
        ax.plot(fpr, tpr, color=c, lw=1.9,
                label=f"{name}  (AUC = {auc:.3f})")

    if show_diagonal:
        ax.plot([0, 1], [0, 1], color="#BBBBBB", lw=1.1, ls="--",
                label="random (AUC = 0.500)")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)

    if auc_table and ranked:
        ranked.sort(reverse=True)
        best = f"Best: {ranked[0][1]} (AUC = {ranked[0][0]:.3f})"
        ax.text(0.97, 0.06, best, transform=ax.transAxes, ha="right",
                fontsize=9.5, color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CALIBRATION  CURVE
# ──────────────────────────────────────────────

def calibration_curve(
    y_true: Sequence[int],
    y_prob: Sequence[float],
    n_bins: int = 10,
    title: str = "Calibration / Reliability Diagram",
    figsize: tuple = (6.5, 6),
    color: str = "#2E86AB",
    strategy: str = "uniform",
    show_histogram: bool = True,
    show_brier: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Reliability diagram — are predicted probabilities honest?
    Perfect calibration lies on the diagonal; the inset histogram shows
    where the model is actually making predictions.

    Returns
    -------
    Figure
    """
    y_arr = np.asarray(y_true, dtype=float)
    p_arr = np.asarray(y_prob, dtype=float)
    edges = np.linspace(0, 1, n_bins + 1)
    if strategy == "quantile":
        edges = np.unique(np.quantile(p_arr, np.linspace(0, 1, n_bins + 1)))

    bin_centers, bin_obs, bin_counts = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p_arr >= lo) & (p_arr < hi if hi < 1 else p_arr <= hi)
        if m.sum() == 0:
            continue
        bin_centers.append(p_arr[m].mean())
        bin_obs.append(y_arr[m].mean())
        bin_counts.append(int(m.sum()))
    bin_centers = np.asarray(bin_centers)
    bin_obs = np.asarray(bin_obs)
    bin_counts = np.asarray(bin_counts)

    brier = float(np.mean((p_arr - y_arr) ** 2))

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot([0, 1], [0, 1], color="#BBBBBB", lw=1.1, ls="--",
            label="perfectly calibrated")
    ax.plot(bin_centers, bin_obs, "-o", color=color, lw=1.9, ms=6,
            mfc="white", mec=color, mew=1.4, label="model")
    if show_histogram:
        ax_twin = ax.twinx()
        ax_twin.bar(bin_centers, bin_counts, width=0.9 / n_bins,
                    color="#CCCCCC", alpha=0.45, lw=0)
        ax_twin.set_ylabel("count", fontsize=9, color="#888888")
        ax_twin.tick_params(axis="y", labelcolor="#888888")
        ax_twin.set_yticks([])

    if show_brier:
        ax.text(0.04, 0.96, f"Brier score = {brier:.4f}",
                transform=ax.transAxes, va="top", fontsize=9.5,
                color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Observed frequency")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, loc="lower right")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CUMULATIVE  GAIN  /  LIFT
# ──────────────────────────────────────────────

def gain_chart(
    y_true: Sequence[int],
    y_score: Sequence[float],
    title: str = "Cumulative Gain / Lift",
    figsize: tuple = (8.5, 5),
    color: str = "#2E86AB",
    show_lift: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Cumulative gain curve with optional lift overlay — "contacting the
    top 20% of the ranked list captures X% of all responders."

    Returns
    -------
    Figure
    """
    y_arr = np.asarray(y_true, dtype=float)
    s_arr = np.asarray(y_score, dtype=float)
    order = np.argsort(-s_arr)
    hits = y_arr[order]
    total_pos = hits.sum() or 1
    frac = np.arange(1, len(hits) + 1) / len(hits)
    gain = np.cumsum(hits) / total_pos
    lift = gain / frac

    if show_lift:
        kwargs.pop("style", None)
        fig, ax1 = plt.subplots(figsize=figsize)
        ax2 = ax1.twinx()
        ax1.plot(frac, gain, color=color, lw=2.1, label="cumulative gain")
        ax1.plot([0, 1], [0, 1], color="#BBBBBB", lw=1.1, ls="--",
                 label="baseline")
        ax2.plot(frac, lift, color="#A23B72", lw=1.6, ls="-.",
                 label="lift")
        top20 = float(lift[min(19, len(lift) - 1)])
        ax2.annotate(f"lift@20% = {top20:.2f}×",
                     xy=(0.2, top20), xytext=(30, 12),
                     textcoords="offset points", fontsize=9,
                     color="#A23B72",
                     arrowprops=dict(arrowstyle="-|>", color="#A23B72", lw=1))
        ax1.set_xlabel("Fraction of sample (ranked by score)")
        ax1.set_ylabel("Cumulative gain", color=color)
        ax2.set_ylabel("Lift", color="#A23B72")
        ax2.tick_params(axis="y", labelcolor="#A23B72")
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, frameon=False, loc="lower right",
                   fontsize=8.5)
        axis_config(ax1, grid="y")
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1.02)
    else:
        fig, ax1 = setup_figure(figsize, style="nature", **kwargs)
        ax1.plot(frac, gain, color=color, lw=2.1, label="cumulative gain")
        ax1.plot([0, 1], [0, 1], color="#BBBBBB", lw=1.1, ls="--",
                 label="baseline")
        ax1.set_xlabel("Fraction of sample (ranked by score)")
        ax1.set_ylabel("Cumulative gain")
        ax1.legend(frameon=False, loc="lower right")
        axis_config(ax1, grid="y")

    if title:
        fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DECISION  TREE  PLOT  (sklearn wrapper)
# ──────────────────────────────────────────────

def tree_plot(
    model=None,
    X: Sequence[Sequence[float]] | None = None,
    y: Sequence | None = None,
    feature_names: Sequence[str] | None = None,
    class_names: Sequence[str] | None = None,
    max_depth: int | None = 3,
    title: str | None = None,
    figsize: tuple = (14, 7),
    palette: str = "nature_qual",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Publication-styled decision-tree diagram.

    Parameters
    ----------
    model : fitted sklearn DecisionTree, optional
        If omitted, a tree is fitted on ``(X, y)`` with max_depth.
    feature_names, class_names : lists of str
        Defaults to the sklearn convention.

    Returns
    -------
    Figure
    """
    from sklearn.tree import DecisionTreeClassifier, plot_tree

    if model is None:
        if X is None or y is None:
            raise ValueError("tree_plot needs a fitted model or (X, y) data.")
        model = DecisionTreeClassifier(max_depth=max_depth,
                                       random_state=42).fit(X, y)

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    plot_tree(
        model,
        feature_names=list(feature_names) if feature_names else None,
        class_names=list(class_names) if class_names else None,
        filled=True, rounded=True, impurity=False, precision=2,
        fontsize=8, ax=ax,
        proportion=True,
    )
    # soften the box styling
    for artist in ax.findobj():
        pass
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PRECISION-RECALL  CURVE
# ──────────────────────────────────────────────

def pr_curve(
    y_true: Sequence[int],
    y_score: Sequence[float],
    title: str = "Precision-Recall Curve",
    figsize: tuple = (6.5, 6),
    color: str = "#2E86AB",
    baseline_color: str = "#BBBBBB",
    fill: bool = True,
    fill_alpha: float = 0.12,
    label: str = "model",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Precision-recall curve with AUPRC annotation — the honest metric
    when classes are imbalanced.

    Parameters
    ----------
    y_true : array-like of 0/1
    y_score : array-like of floats
        Positive-class scores.

    Returns
    -------
    Figure
    """
    from sklearn.metrics import precision_recall_curve, average_precision_score

    y_arr = np.asarray(y_true)
    s_arr = np.asarray(y_score, dtype=float)
    precision, recall, _ = precision_recall_curve(y_arr, s_arr)
    ap = average_precision_score(y_arr, s_arr)
    prevalence = float(np.mean(y_arr))

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    ax.step(recall, precision, where="post", color=color, lw=2.2,
            label=f"{label}  (AUPRC = {ap:.3f})")
    if fill:
        ax.fill_between(recall, precision, step="post", color=color,
                        alpha=fill_alpha, lw=0)
    ax.axhline(prevalence, color=baseline_color, lw=1.2, ls="--",
               label=f"no-skill ({prevalence:.2f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, loc="lower left")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PREDICTED  vs  ACTUAL
# ──────────────────────────────────────────────

def prediction_vs_actual(
    y_actual: Sequence[float],
    y_predicted: Sequence[float],
    title: str | None = None,
    xlabel: str = "Actual",
    ylabel: str = "Predicted",
    figsize: tuple = (6.5, 6),
    color: str = "#2E86AB",
    identity: bool = True,
    show_fit: bool = True,
    show_r2: bool = True,
    show_rmse: bool = True,
    point_size: float = 38,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Predicted vs actual scatter with the y = x identity line — the
    clearest single view of regression quality.

    Returns
    -------
    Figure
    """
    ya = np.asarray(y_actual, dtype=float)
    yp = np.asarray(y_predicted, dtype=float)

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    ax.scatter(ya, yp, s=point_size, color=color, alpha=0.75,
               edgecolors="white", lw=0.5, zorder=3)

    lo = float(min(ya.min(), yp.min()))
    hi = float(max(ya.max(), yp.max()))
    pad = 0.05 * (hi - lo or 1)
    lims = (lo - pad, hi + pad)
    if identity:
        ax.plot(lims, lims, color="#999999", lw=1.2, ls="--", label="y = x")
    if show_fit:
        b, a = np.polyfit(ya, yp, 1)
        xf = np.linspace(lims[0], lims[1], 50)
        ax.plot(xf, a + b * xf, color="#C73E1D", lw=1.6, label="fit")

    notes = []
    if show_r2:
        ss_res = float(np.sum((ya - yp) ** 2))
        ss_tot = float(np.sum((ya - ya.mean()) ** 2)) or 1
        notes.append(f"R2 = {1 - ss_res / ss_tot:.4f}")
    if show_rmse:
        notes.append(f"RMSE = {float(np.sqrt(np.mean((ya - yp) ** 2))):.4g}")
    if notes:
        ax.text(0.04, 0.96, chr(10).join(notes), transform=ax.transAxes,
                va="top", ha="left", fontsize=9.5, color="#1D3557",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.9))

    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, loc="lower right")
    axis_config(ax, grid="both")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  REGRESSION  DIAGNOSTICS  PANEL  (R-style)
# ──────────────────────────────────────────────

def regression_panel(
    y_actual: Sequence[float],
    y_predicted: Sequence[float],
    title: str | None = None,
    figsize: tuple = (10, 8),
    color: str = "#2E86AB",
    resid_color: str = "#C73E1D",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Four-panel regression diagnostics (R's plot.lm): residuals vs
    fitted, Q-Q of residuals, scale-location, and predicted vs actual.

    Returns
    -------
    Figure
    """
    from scipy import stats as sps

    ya = np.asarray(y_actual, dtype=float)
    yp = np.asarray(y_predicted, dtype=float)
    res = ya - yp
    std_res = (res - res.mean()) / (res.std() or 1)

    kwargs.pop("style", None)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    (ax1, ax2), (ax3, ax4) = axes

    # 1. residuals vs fitted
    ax1.scatter(yp, res, s=22, color=color, alpha=0.75, lw=0)
    ax1.axhline(0, color="#999999", lw=1, ls="--")
    lo, hi = yp.min(), yp.max()
    pad = 0.05 * (hi - lo or 1)
    xf = np.linspace(lo - pad, hi + pad, 40)
    smooth = np.polyval(np.polyfit(yp, res, 1), xf)
    ax1.plot(xf, smooth, color=resid_color, lw=1.6)
    ax1.set_xlabel("Fitted")
    ax1.set_ylabel("Residuals")
    ax1.set_title("Residuals vs Fitted", fontsize=10)

    # 2. QQ of residuals
    (osm, osr), (_, _, r) = sps.probplot(std_res, dist="norm")
    ax2.scatter(osm, osr, s=18, color=color, alpha=0.75, zorder=3)
    slope, intercept = np.polyfit(osm, osr, 1)
    ax2.plot(osm, slope * osm + intercept, color=resid_color, lw=1.6)
    ax2.set_xlabel("Theoretical quantiles")
    ax2.set_ylabel("Standardized residuals")
    ax2.set_title(f"Normal Q-Q (R2 = {r ** 2:.4f})", fontsize=10)

    # 3. scale-location
    root_abs = np.sqrt(np.abs(std_res))
    ax3.scatter(yp, root_abs, s=22, color=color, alpha=0.75, lw=0)
    ax3.plot(np.sort(yp), np.polyval(np.polyfit(yp, root_abs, 1), np.sort(yp)),
             color=resid_color, lw=1.6)
    ax3.set_xlabel("Fitted")
    ax3.set_ylabel("sqrt |standardized residuals|")
    ax3.set_title("Scale-Location", fontsize=10)

    # 4. predicted vs actual
    lo = float(min(ya.min(), yp.min()))
    hi = float(max(ya.max(), yp.max()))
    pad = 0.05 * (hi - lo or 1)
    ax4.scatter(ya, yp, s=22, color=color, alpha=0.75, lw=0)
    ax4.plot([lo - pad, hi + pad], [lo - pad, hi + pad],
             color="#999999", lw=1.2, ls="--")
    ax4.set_xlim(lo - pad, hi + pad)
    ax4.set_ylim(lo - pad, hi + pad)
    ax4.set_xlabel("Actual")
    ax4.set_ylabel("Predicted")
    ax4.set_title("Predicted vs Actual", fontsize=10)

    for ax in axes.ravel():
        axis_config(ax, grid="y")
    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ELBOW  PLOT  (K selection)
# ──────────────────────────────────────────────

def elbow_plot(
    X: Sequence[Sequence[float]],
    k_range: Sequence[int] | None = None,
    title: str | None = None,
    xlabel: str = "Number of clusters k",
    figsize: tuple = (8.5, 5),
    color: str = "#2E86AB",
    elbow_color: str = "#C73E1D",
    show_silhouette: bool = True,
    max_samples: int = 800,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    K-means model selection: inertia elbow with silhouette overlay on
    a twin axis, and the auto-suggested k marked.

    Returns
    -------
    Figure
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    X_arr = np.asarray(X, dtype=float)
    if len(X_arr) > max_samples:
        idx = np.random.default_rng(42).choice(len(X_arr), max_samples, replace=False)
        X_fit = X_arr[idx]
    else:
        X_fit = X_arr
    k_range = list(k_range) if k_range is not None else list(range(2, min(11, len(X_fit))))
    k_range = [k for k in k_range if 2 <= k <= len(X_fit) - 1]

    inertias, sils = [], []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_fit)
        inertias.append(float(km.inertia_))
        if show_silhouette:
            sils.append(float(silhouette_score(X_fit, km.labels_)))
        else:
            sils.append(np.nan)

    # Elbow heuristic: max distance from the line joining the endpoints
    k_arr = np.asarray(k_range, dtype=float)
    p1 = np.array([k_arr[0], inertias[0]])
    p2 = np.array([k_arr[-1], inertias[-1]])
    norm = float(np.hypot(p2[0] - p1[0], p2[1] - p1[1])) or 1.0
    vx, vy = p2[0] - p1[0], p2[1] - p1[1]
    pts = np.column_stack([k_arr, inertias]) - p1
    dists = np.abs(vx * pts[:, 1] - vy * pts[:, 0]) / norm
    k_best = k_range[int(np.argmax(dists))]

    fig, ax1 = setup_figure(figsize, style="nature", **kwargs)
    ax1.plot(k_arr, inertias, "-o", color=color, lw=2, ms=5, label="inertia")
    ax1.plot([k_best], [inertias[int(np.argmax(dists))]], "D", ms=9,
             mfc=elbow_color, mec="white", mew=1.2, zorder=5,
             label=f"elbow k = {k_best}")
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel("Inertia (within-cluster SSE)", color=color)
    ax1.tick_params(axis="y", labelcolor=color)

    if show_silhouette and not all(np.isnan(v) for v in sils):
        ax2 = ax1.twinx()
        ax2.plot(k_arr, sils, "-s", color="#A23B72", lw=1.6, ms=4.5,
                 alpha=0.85, label="silhouette")
        ax2.set_ylabel("Silhouette score", color="#A23B72")
        ax2.tick_params(axis="y", labelcolor="#A23B72")

    ax1.legend(frameon=False, loc="upper right")
    axis_config(ax1, grid="y")
    if title:
        ax1.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SILHOUETTE  PLOT
# ──────────────────────────────────────────────

def silhouette_plot(
    X: Sequence[Sequence[float]],
    labels: Sequence[int],
    title: str | None = None,
    xlabel: str = "Silhouette coefficient",
    figsize: tuple = (8, 6),
    palette: str = "clustering",
    max_samples: int = 3000,
    show_score: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Per-cluster silhouette profile — is every cluster cohesive, or is
    one cluster a dumping ground?

    Returns
    -------
    Figure
    """
    from sklearn.metrics import silhouette_samples, silhouette_score

    X_arr = np.asarray(X, dtype=float)
    labels_arr = np.asarray(labels)
    if len(X_arr) > max_samples:
        idx = np.random.default_rng(42).choice(len(X_arr), max_samples,
                                               replace=False)
        X_arr, labels_arr = X_arr[idx], labels_arr[idx]

    values = silhouette_samples(X_arr, labels_arr)
    score = float(silhouette_score(X_arr, labels_arr))

    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(12, palette)
    y_lower = 10
    clusters = sorted(set(labels_arr.tolist()))

    for i, c in enumerate(clusters):
        cv = np.sort(values[labels_arr == c])
        size = len(cv)
        y_upper = y_lower + size
        ax.fill_betweenx(
            np.arange(y_lower, y_upper), 0, cv,
            facecolor=colors[i % len(colors)], edgecolor="white", lw=0.4,
            alpha=0.9,
        )
        ax.text(-0.06, y_lower + 0.5 * size, str(c), ha="right",
                va="center", fontsize=9, color="#333333")
        y_lower = y_upper + 8

    if show_score:
        ax.axvline(score, color="#C73E1D", lw=1.6, ls="--",
                   label=f"mean = {score:.3f}")
        ax.legend(frameon=False, loc="lower right")
    ax.set_yticks([])
    ax.set_xlim(-0.1, 1.0)
    ax.set_xlabel(xlabel)
    axis_config(ax, grid="x")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SCREE  PLOT  (PCA)
# ──────────────────────────────────────────────

def scree_plot(
    data,
    n_components: int | None = None,
    title: str | None = None,
    xlabel: str = "Principal component",
    figsize: tuple = (8.5, 5),
    color: str = "#2E86AB",
    cum_color: str = "#C73E1D",
    show_cumulative: bool = True,
    threshold: float = 0.90,
    standardize: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    PCA scree plot with cumulative explained variance and the number
    of components needed to reach ``threshold``.

    Parameters
    ----------
    data : 2-D array-like (n_samples x n_features)

    Returns
    -------
    Figure
    """
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    arr = np.asarray(data, dtype=float)
    if standardize:
        arr = StandardScaler().fit_transform(arr)
    n_components = n_components or min(arr.shape)
    pca = PCA(n_components=n_components).fit(arr)
    evr = pca.explained_variance_ratio_
    cum = np.cumsum(evr)
    idx = np.arange(1, len(evr) + 1)
    k = int(np.searchsorted(cum, threshold) + 1) if cum[-1] >= threshold else len(evr)

    fig, ax1 = setup_figure(figsize, style="nature", **kwargs)
    ax1.bar(idx, evr, color=color, alpha=0.85, width=0.6, label="explained ratio")
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel("Explained variance ratio", color=color)
    ax1.tick_params(axis="y", labelcolor=color)

    if show_cumulative:
        ax2 = ax1.twinx()
        ax2.plot(idx, cum, "-o", color=cum_color, lw=1.8, ms=4,
                 label="cumulative")
        ax2.axhline(threshold, color="#999999", lw=1, ls=":")
        ax2.axvline(k, color="#999999", lw=1, ls=":")
        ax2.annotate(f"{k} PCs = {cum[k - 1]:.0%}", xy=(k, cum[k - 1]),
                     xytext=(12, -18), textcoords="offset points",
                     fontsize=9, color=cum_color)
        ax2.set_ylabel("Cumulative", color=cum_color)
        ax2.tick_params(axis="y", labelcolor=cum_color)
        ax2.set_ylim(0, 1.02)

    axis_config(ax1, grid="y")
    if title:
        ax1.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig