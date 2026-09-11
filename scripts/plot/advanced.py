"""
advanced.py — Advanced visualization charts.

Charts:
    heatmap              — annotated heatmap
    network_graph        — node-link network diagram
    sankey_diagram       — Sankey flow diagram
    radar_chart          — radar / spider chart
    treemap              — treemap
    timeline             — timeline visualization
    waterfall_chart      — waterfall (bridge) chart
    dumbbell_plot        — dumbbell (change) plot
    slope_chart          — slope chart (pre/post comparison)
    treemap_custom       — custom treemap
    parallel_coordinates — parallel coordinates plot
    gantt_chart          — Gantt chart
    sankey_sankey        — Sankey diagram (alias)
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import matplotlib.patches as mpatches

from .palette import auto_colors, get_palette, blend, lightness, NEUTRAL, ACCENT
from .styles import apply_style
from .utils import setup_figure, save_figure, axis_config, auto_layout


# ──────────────────────────────────────────────
#  NETWORK  GRAPH
# ──────────────────────────────────────────────

def network_graph(
    nodes: Sequence[int],
    edges: Sequence[tuple[int, int]],
    node_labels: Optional[Sequence[str]] = None,
    edge_labels: Optional[Sequence[str]] = None,
    title: str = "Network Graph",
    figsize: tuple = (8, 6),
    palette: str = "network",
    node_size: float = 300,
    node_alpha: float = 0.85,
    edge_width: float = 1.5,
    edge_alpha: float = 0.6,
    font_color: str = "white",
    label_fontsize: float = 9,
    show_labels: bool = True,
    grid: bool = False,
    layout: str = "spring",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a network graph visualization.

    Parameters
    ----------
    nodes : list of int
        Node identifiers.
    edges : list of (int, int)
        Edge connections.
    node_labels : list of str, optional
        Display labels for nodes.
    edge_labels : list of str, optional
        Labels for edges.
    layout : str
        'spring', 'circular', 'shell', 'random'.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Layout
    if layout == "spring":
        pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "shell":
        pos = nx.shell_layout(G, nlist=[nodes])
    elif layout == "random":
        pos = nx.random_layout(G, seed=42)
    else:
        pos = nx.spring_layout(G, seed=42)

    # Color nodes by degree
    degrees = [G.degree(n) for n in nodes]
    max_deg = max(degrees) if degrees else 1
    node_colors = []
    for d in degrees:
        color = get_palette(palette)[0]
        # Scale brightness by degree
        factor = 0.4 + 0.6 * (d / max_deg if max_deg > 0 else 1)
        node_colors.append(blend("#2E86AB", "#E63946", 1 - factor))

    nx.draw_networkx_nodes(
        G, pos, ax=ax, node_size=node_size,
        node_color=node_colors, alpha=node_alpha,
        edgecolors="white", linewidths=1,
    )

    nx.draw_networkx_edges(
        G, pos, ax=ax, width=edge_width,
        edge_color="#999999", alpha=edge_alpha,
    )

    if show_labels and node_labels:
        nx.draw_networkx_labels(
            G, pos, ax=ax,
            labels={n: node_labels[i] for i, n in enumerate(nodes)},
            font_size=label_fontsize, font_color=font_color,
            font_weight="bold",
        )

    if edge_labels:
        edge_dict = {tuple(e): e_labels[i] for i, e in enumerate(edges)}
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=edge_dict,
            font_size=label_fontsize - 1, font_color="#666666",
        )

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.axis("off")

    if grid:
        ax.grid(True, alpha=0.1)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SANKEY  DIAGRAM
# ──────────────────────────────────────────────

def sankey_diagram(
    flows: Sequence[tuple[int, int, float]],
    labels: Optional[Sequence[str]] = None,
    title: str = "Sankey Diagram",
    figsize: tuple = (10, 6),
    palette: str = "nature_qual",
    font_color: str = "#333333",
    label_fontsize: float = 10,
    node_width: float = 0.04,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Create a Sankey diagram for flow visualization.

    Parameters
    ----------
    flows : list of (source, target, value)
        Flow connections. Source/target are node indices.
    labels : list of str, optional
        Node labels.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    if labels is None:
        max_node = max(f[0] for f in flows)
        max_node = max(max_node, max(f[1] for f in flows))
        labels = [f"Node {i}" for i in range(max_node + 1)]

    n_nodes = len(labels)
    colors = auto_colors(n_nodes, palette)

    # Calculate node positions
    # Group nodes by column (source = 0, target = 1)
    from collections import defaultdict
    node_flows = defaultdict(lambda: {"in": [], "out": []})

    for src, tgt, val in flows:
        node_flows[src]["out"].append(val)
        node_flows[tgt]["in"].append(val)

    # Calculate node heights
    node_values = {}
    for node in range(n_nodes):
        nf = node_flows[node]
        node_values[node] = max(sum(nf["in"]), sum(nf["out"]))

    # Scale and position nodes
    total_height = sum(node_values.values())
    scale = 0.8 / total_height if total_height > 0 else 0.8
    node_positions = {}
    current_y = 0
    for node in range(n_nodes):
        h = node_values[node] * scale
        node_positions[node] = {
            "x": 0 if all(f[0] == node for f in flows if node in (f[0], f[1]))
            else 1,
            "y": current_y,
            "h": h,
        }
        current_y += h

    # Draw nodes as rectangles
    for node, pos in node_positions.items():
        color = colors[node % len(colors)]
        ax.add_patch(Rectangle(
            (pos["x"], pos["y"]), node_width, pos["h"],
            facecolor=color, edgecolor="white", linewidth=1.5,
            alpha=0.85, zorder=3,
        ))
        # Label
        text_y = pos["y"] + pos["h"] / 2
        ax.text(
            pos["x"] + node_width / 2, text_y,
            labels[node], ha="center", va="center",
            fontsize=label_fontsize, fontweight="bold",
            color=font_color, zorder=5,
        )

    # Draw flows as bezier curves
    flow_y_offsets = defaultdict(lambda: {"src": 0, "tgt": 0})
    for src, tgt, val in flows:
        v_scale = val * scale
        src_y = node_positions[src]["y"] + flow_y_offsets[src]["src"]
        tgt_y = node_positions[tgt]["y"] + flow_y_offsets[tgt]["tgt"]

        # Bezier control points
        src_x = node_positions[src]["x"] + node_width
        tgt_x = node_positions[tgt]["x"]
        mid_x = (src_x + tgt_x) / 2

        # Draw as filled polygon
        points = []
        n_steps = 50
        for i in range(n_steps + 1):
            t = i / n_steps
            # Bezier curve top edge
            x = (1-t)**2 * src_x + 2*(1-t)*t * mid_x + t**2 * tgt_x
            y = (1-t)**2 * src_y + 2*(1-t)*t * (src_y + tgt_y)/2 + t**2 * tgt_y
            points.append((x, y))
        # Bottom edge
        for i in range(n_steps, -1, -1):
            t = i / n_steps
            x = (1-t)**2 * src_x + 2*(1-t)*t * mid_x + t**2 * tgt_x
            y = (1-t)**2 * (src_y + v_scale) + 2*(1-t)*t * ((src_y + tgt_y)/2 + v_scale/2) + t**2 * (tgt_y + v_scale)
            points.append((x, y))

        color = blend(
            colors[src % len(colors)],
            colors[tgt % len(colors)],
            0.5,
        )
        from matplotlib.patches import Polygon
        ax.add_patch(Polygon(
            points, facecolor=color, edgecolor="none",
            alpha=0.5, zorder=1,
        ))

        flow_y_offsets[src]["src"] += v_scale
        flow_y_offsets[tgt]["tgt"] += v_scale

        # Flow value label
        mid_y = (src_y + tgt_y) / 2 + v_scale / 2
        ax.text(
            mid_x, mid_y, f"{val:g}",
            fontsize=8, color="#666666", ha="center", va="center",
            zorder=6,
        )

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  RADAR  CHART
# ──────────────────────────────────────────────

def radar_chart(
    labels: Sequence[str],
    values: Sequence[Sequence[float]],
    names: Optional[Sequence[str]] = None,
    title: str = "Radar Chart",
    figsize: tuple = (7, 7),
    palette: str = "nature_qual",
    fill_alpha: float = 0.15,
    line_width: float = 2.0,
    marker_size: float = 6,
    font_size: float = 10,
    grid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Radar / spider chart for multi-dimensional comparison.

    Parameters
    ----------
    labels : list of str
        Dimension labels (axes).
    values : list of arrays
        Values for each series.
    names : list of str, optional
        Series names for legend.
    """
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True), **kwargs)

    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    colors = auto_colors(len(values), palette)

    for i, (vals, name) in enumerate(zip(values, names or [f"Series {i+1}" for i in range(len(values))])):
        v = list(vals) + [vals[0]]  # close
        ax.plot(angles, v, color=colors[i], linewidth=line_width,
                marker="o", markersize=marker_size, label=name)
        ax.fill(angles, v, color=colors[i], alpha=fill_alpha)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=font_size)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=20)

    if grid:
        ax.grid(True, alpha=0.3)

    ax.legend(frameon=False, fontsize=font_size - 1, loc="upper right",
              bbox_to_anchor=(1.3, 1.1))

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  WATERFALL  CHART
# ──────────────────────────────────────────────

def waterfall_chart(
    categories: Sequence[str],
    values: Sequence[float],
    title: str = "Waterfall Chart",
    xlabel: str | None = None,
    ylabel: str | None = None,
    figsize: tuple = (10, 6),
    palette: str = "nature_qual",
    increase_color: str | None = None,
    decrease_color: str | None = None,
    total_color: str | None = None,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    value_fontsize: float = 8,
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Waterfall (bridge) chart showing cumulative changes.

    Parameters
    ----------
    categories : list of str
        Step labels.
    values : list of float
        Change values (positive = increase, negative = decrease).
        First value should be the starting total, last value should be the final total.
    increase_color, decrease_color, total_color : str, optional
        Override default colors.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    n = len(categories)
    values = list(values)

    if increase_color is None:
        increase_color = "#2D6A4F"
    if decrease_color is None:
        decrease_color = "#C73E1D"
    if total_color is None:
        total_color = "#2E86AB"

    # Calculate running totals
    running_total = 0
    bottoms = []
    heights = []
    colors = []
    types = []

    for i, v in enumerate(values):
        if i == 0 or i == n - 1:
            # Total bars (first and last)
            bottoms.append(0)
            heights.append(abs(v))
            colors.append(total_color)
            types.append("total")
        else:
            if v >= 0:
                bottoms.append(running_total)
                heights.append(v)
                colors.append(increase_color)
                types.append("increase")
                running_total += v
            else:
                bottoms.append(running_total)
                heights.append(abs(v))
                colors.append(decrease_color)
                types.append("decrease")
                running_total += v

    # Draw bars
    x = np.arange(n)
    for i in range(n):
        bottom = bottoms[i]
        height = heights[i]
        color = colors[i]

        ax.bar(
            i, height, bottom=bottom,
            color=color, width=0.6,
            edgecolor="white", linewidth=0.8,
            alpha=0.85,
        )

        # Connector line
        if i < n - 1:
            ax.plot(
                [i + 0.3, i + 1 - 0.3],
                [bottom + height, bottoms[i + 1] + heights[i + 1]],
                color="#999999", linewidth=0.8, linestyle="--",
                zorder=1,
            )

        if show_values:
            y_pos = bottom + height + max(h for h in heights) * 0.02
            ax.text(i, y_pos, value_fmt.format(values[i]),
                    ha="center", va="bottom", fontsize=value_fontsize,
                    color="#333333", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9, rotation=15, ha="right")

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)

    if grid != "none":
        axis_config(ax, grid=grid)

    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  DUMBBELL  PLOT
# ──────────────────────────────────────────────

def dumbbell_plot(
    labels: Sequence[str],
    old_values: Sequence[float],
    new_values: Sequence[float],
    title: str = "Dumbbell Plot",
    xlabel: str | None = None,
    ylabel: str | None = None,
    figsize: tuple = (8, 5),
    old_color: str = "#999999",
    new_color: str = "#2E86AB",
    old_label: str = "Before",
    new_label: str = "After",
    marker_size: float = 100,
    line_width: float = 2.0,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    value_fontsize: float = 8,
    grid: str = "x",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Dumbbell plot for comparing two values across categories.

    Parameters
    ----------
    labels : list of str
        Category names.
    old_values, new_values : list of float
        Two sets of values to compare.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    n = len(labels)
    y_pos = np.arange(n)

    # Draw lines and dots
    for i in range(n):
        old_v = old_values[i]
        new_v = new_values[i]
        # Line
        ax.plot(
            [old_v, new_v], [i, i],
            color="#CCCCCC", linewidth=line_width, zorder=1,
        )
        # Old dot
        ax.scatter(old_v, i, c=old_color, s=marker_size,
                   edgecolors="white", linewidth=1, zorder=3,
                   label=old_label if i == 0 else None)
        # New dot
        ax.scatter(new_v, i, c=new_color, s=marker_size,
                   edgecolors="white", linewidth=1, zorder=4,
                   label=new_label if i == 0 else None)

        if show_values:
            ax.text(old_v, i + 0.15, value_fmt.format(old_v),
                    fontsize=value_fontsize, color=old_color,
                    ha="center", va="bottom")
            ax.text(new_v, i + 0.15, value_fmt.format(new_v),
                    fontsize=value_fontsize, color=new_color,
                    ha="center", va="bottom", fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel(xlabel or "Value", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=9, loc="lower right")

    axis_config(ax, grid=grid)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  SLOPE  CHART
# ──────────────────────────────────────────────

def slope_chart(
    labels: Sequence[str],
    y1: Sequence[float],
    y2: Sequence[float],
    x1: float = 0,
    x2: float = 1,
    title: str = "Slope Chart",
    xlabel: str | None = None,
    ylabel: str | None = None,
    figsize: tuple = (8, 5),
    palette: str = "nature_qual",
    marker_size: float = 80,
    line_width: float = 2.0,
    show_values: bool = True,
    value_fmt: str = "{:.2f}",
    value_fontsize: float = 8,
    grid: str = "y",
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Slope chart for comparing rankings before/after.

    Parameters
    ----------
    labels : list of str
        Category labels.
    y1, y2 : list of float
        Values at x1 and x2 positions.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    n = len(labels)
    colors = auto_colors(n, palette)

    for i, (lbl, y_v1, y_v2) in enumerate(zip(labels, y1, y2)):
        color = colors[i % len(colors)]
        ax.plot([x1, x2], [y_v1, y_v2], color=color,
                linewidth=line_width, alpha=0.7, zorder=2)
        ax.scatter([x1, x2], [y_v1, y_v2], c=color,
                   s=marker_size, edgecolors="white", linewidth=1,
                   zorder=3)

        if show_values:
            ax.text(x1 - 0.05, y_v1, value_fmt.format(y_v1),
                    fontsize=value_fontsize, color=color,
                    ha="right", va="center", fontweight="bold")
            ax.text(x2 + 0.05, y_v2, value_fmt.format(y_v2),
                    fontsize=value_fontsize, color=color,
                    ha="left", va="center", fontweight="bold")

    ax.set_xticks([x1, x2])
    ax.set_xticklabels(["Before", "After"], fontsize=10)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    # Add label annotations
    for i, lbl in enumerate(labels):
        color = colors[i % len(colors)]
        ax.text(x1 - 0.1, y1[i], lbl, fontsize=value_fontsize + 1,
                ha="right", va="center", color="#333333")
        ax.text(x2 + 0.1, y2[i], lbl, fontsize=value_fontsize + 1,
                ha="left", va="center", color="#333333")

    ax.set_xlim(x1 - 0.2, x2 + 0.2)
    axis_config(ax, grid=grid)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  TIMELINE
# ──────────────────────────────────────────────

def timeline(
    events: Sequence[dict],
    title: str = "Timeline",
    figsize: tuple = (12, 4),
    palette: str = "nature_qual",
    event_height: float = 0.15,
    show_labels: bool = True,
    label_fontsize: float = 9,
    grid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Timeline visualization with event markers.

    Parameters
    ----------
    events : list of dict
        Each dict has keys: 'time' (float or date), 'label' (str),
        'category' (str, optional), 'duration' (float, optional),
        'description' (str, optional).
    """
    fig, ax = setup_figure(figsize, **kwargs)

    n_events = len(events)
    colors = auto_colors(len(set(e.get("category", "default") for e in events)), palette)

    categories = []
    for e in events:
        cat = e.get("category", "default")
        if cat not in categories:
            categories.append(cat)
    cat_to_color = {c: colors[i] for i, c in enumerate(categories)}

    for i, event in enumerate(events):
        t = event["time"]
        label = event.get("label", "")
        desc = event.get("description", "")
        duration = event.get("duration", 0.05)
        cat = event.get("category", "default")
        color = cat_to_color.get(cat, colors[0])

        y = i / n_events

        # Duration bar
        ax.barh(
            y, duration, left=t, height=event_height,
            color=color, alpha=0.7, edgecolor="white", linewidth=0.5,
        )

        # Event dot
        ax.scatter(t, y, c=color, s=100, edgecolors="white",
                   linewidth=1.5, zorder=5)

        if show_labels:
            ax.text(t, y + 0.1, label, fontsize=label_fontsize,
                    ha="center", va="bottom", color="#333333",
                    fontweight="bold", clip_on=False)
            if desc:
                ax.text(t, y - 0.1, desc, fontsize=label_fontsize - 1,
                        ha="center", va="top", color="#666666",
                        style="italic", clip_on=False)

    ax.set_yticks([])
    ax.set_xlim(
        min(e["time"] for e in events) - 0.1,
        max(e.get("time", 0) + e.get("duration", 0.05) for e in events) + 0.1,
    )
    ax.set_ylim(-0.2, n_events / n_events + 0.2)

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    if grid:
        ax.grid(axis="x", alpha=0.2)

    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  PARALLEL  COORDINATES
# ──────────────────────────────────────────────

def parallel_coordinates(
    data: Sequence[Sequence[float]],
    labels: Optional[Sequence[str]] = None,
    title: str = "Parallel Coordinates",
    xlabel: str | None = None,
    figsize: tuple = (10, 6),
    palette: str = "nature_qual",
    line_width: float = 1.5,
    alpha: float = 0.6,
    show_labels: bool = True,
    label_fontsize: float = 9,
    grid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Parallel coordinates plot for multi-dimensional data.

    Parameters
    ----------
    data : array-like of shape (N, D)
        Data matrix.
    labels : list of str, optional
        Dimension labels.
    """
    fig, ax = setup_figure(figsize, **kwargs)
    data_arr = np.array(data, dtype=float)
    n_points, n_dims = data_arr.shape

    if labels is None:
        labels = [f"Dim {i+1}" for i in range(n_dims)]

    x_pos = np.arange(n_dims)
    colors = auto_colors(n_points, palette)

    for i, row in enumerate(data_arr):
        ax.plot(x_pos, row, color=colors[i % len(colors)],
                linewidth=line_width, alpha=alpha, zorder=2)
        ax.scatter(x_pos, row, c=colors[i % len(colors)], s=20,
                   alpha=alpha, zorder=3)

    if show_labels:
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=label_fontsize)

    if grid:
        axis_config(ax, grid="y")

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  GANTT  CHART
# ──────────────────────────────────────────────

def gantt_chart(
    tasks: Sequence[dict],
    title: str = "Gantt Chart",
    figsize: tuple = (10, 5),
    palette: str = "nature_qual",
    show_values: bool = True,
    value_fontsize: float = 8,
    grid: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Gantt chart for project timelines.

    Parameters
    ----------
    tasks : list of dict
        Each dict has keys: 'name' (str), 'start' (float),
        'end' (float), 'progress' (float 0-1, optional),
        'category' (str, optional).
    """
    fig, ax = setup_figure(figsize, **kwargs)

    n_tasks = len(tasks)
    categories = list(set(t.get("category", "default") for t in tasks))
    colors = auto_colors(len(categories), palette)
    cat_to_color = {c: colors[i] for i, c in enumerate(categories)}

    for i, task in enumerate(tasks):
        name = task["name"]
        start = task["start"]
        end = task["end"]
        duration = end - start
        progress = task.get("progress", 1.0)
        cat = task.get("category", "default")
        color = cat_to_color.get(cat, colors[0])

        y = n_tasks - 1 - i

        # Background bar (full duration)
        ax.barh(
            y, duration, left=start, height=0.5,
            color=color, alpha=0.2, edgecolor="none",
        )

        # Progress bar
        progress_end = start + duration * progress
        ax.barh(
            y, progress_end - start, left=start, height=0.5,
            color=color, alpha=0.8, edgecolor="white", linewidth=0.5,
        )

        if show_values:
            ax.text(
                start - 0.05, y, name,
                fontsize=value_fontsize, va="center",
                ha="right", color="#333333",
            )
            ax.text(
                end + 0.05, y, f"{duration:.1f}",
                fontsize=value_fontsize, va="center",
                ha="left", color="#666666",
            )

    ax.set_yticks([])
    ax.set_xlabel("Time", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    if grid:
        ax.grid(axis="x", alpha=0.2)

    ax.tick_params(axis="both", labelsize=9)

    fig.tight_layout()

    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  TREEMAP  (simplified)
# ──────────────────────────────────────────────

def treemap(
    data: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    title: str = "Treemap",
    figsize: tuple = (10, 6),
    palette: str = "nature_qual",
    font_size: float = 10,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Simple treemap visualization.

    Parameters
    ----------
    data : list of float
        Values (sizes) for each rectangle.
    labels : list of str, optional
        Labels for rectangles.
    """
    fig, ax = setup_figure(figsize, **kwargs)

    data_arr = np.array(data, dtype=float)
    labels_arr = labels or [f"{i+1}" for i in range(len(data_arr))]
    colors = auto_colors(len(data_arr), palette)
    total = data_arr.sum()

    # Simple squarified treemap algorithm
    def _squarify(values, x, y, width, height):
        """Simple squarified treemap."""
        rects = []
        sorted_idx = np.argsort(values)[::-1]
        values = values[sorted_idx]

        remaining_x = x
        remaining_y = y
        remaining_w = width
        remaining_h = height

        while len(values) > 0 and remaining_w > 0 and remaining_h > 0:
            if remaining_w >= remaining_h:
                # Horizontal strip
                strip_width = remaining_w
                n_in_strip = 0
                strip_sum = 0
                for v in values:
                    if n_in_strip == 0 or strip_sum > 0:
                        aspect = (strip_sum + v) / strip_width
                        if aspect >= remaining_h / remaining_h:
                            break
                    strip_sum += v
                    n_in_strip += 1
                if n_in_strip == 0:
                    n_in_strip = 1
                    strip_sum = values[0]

                strip_height = strip_sum / strip_width if strip_width > 0 else 0
                strip_height = min(strip_height, remaining_h)
                strip_width_actual = strip_sum / strip_height if strip_height > 0 else remaining_w

                sub_x = remaining_x
                for i in range(n_in_strip):
                    sub_h = values[i] / strip_sum * strip_height if strip_sum > 0 else strip_height
                    rects.append((sub_x, remaining_y, values[i] / strip_width * strip_width_actual if strip_width > 0 else 0, sub_h))
                    sub_x += values[i] / strip_width * strip_width_actual if strip_width > 0 else 0

                remaining_x += strip_width_actual
                remaining_w -= strip_width_actual
                values = values[n_in_strip:]
            else:
                # Vertical strip
                strip_height = remaining_h
                n_in_strip = 0
                strip_sum = 0
                for v in values:
                    if n_in_strip == 0 or strip_sum > 0:
                        aspect = (strip_sum + v) / strip_height
                        if aspect >= remaining_w / remaining_w:
                            break
                    strip_sum += v
                    n_in_strip += 1
                if n_in_strip == 0:
                    n_in_strip = 1
                    strip_sum = values[0]

                strip_width = strip_sum / strip_height if strip_height > 0 else 0
                strip_width = min(strip_width, remaining_w)
                strip_height_actual = strip_sum / strip_width if strip_width > 0 else remaining_h

                sub_y = remaining_y
                for i in range(n_in_strip):
                    sub_w = values[i] / strip_sum * strip_width if strip_sum > 0 else strip_width
                    rects.append((remaining_x, sub_y, sub_w, values[i] / strip_height * strip_height_actual if strip_height > 0 else 0))
                    sub_y += values[i] / strip_height * strip_height_actual if strip_height > 0 else 0

                remaining_y += strip_height_actual
                remaining_h -= strip_height_actual
                values = values[n_in_strip:]

        return rects, sorted_idx

    rects, order = _squarify(data_arr, 0, 0, 1, 1)

    for i, (rx, ry, rw, rh) in enumerate(rects):
        orig_idx = order[i]
        color = colors[orig_idx % len(colors)]
        ax.add_patch(Rectangle(
            (rx, ry), rw, rh,
            facecolor=color, edgecolor="white", linewidth=1.5,
            alpha=0.85, zorder=2,
        ))
        if labels_arr[orig_idx]:
            cx = rx + rw / 2
            cy = ry + rh / 2
            # Adjust font size based on rectangle size
            fs = min(font_size, max(6, int(min(rw, rh) * 40)))
            ax.text(
                cx, cy, f"{labels_arr[orig_idx]}\n{data_arr[orig_idx]:.1f}",
                ha="center", va="center", fontsize=fs,
                color="white", fontweight="bold",
                zorder=5, linespacing=1.2,
            )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    try:
        fig.tight_layout()
    except (UserWarning, ValueError):
        pass

    if save_path:
        save_figure(fig, save_path)
    return fig


__all__ = [
    "network_graph", "sankey_diagram", "radar_chart",
    "waterfall_chart", "dumbbell_plot", "slope_chart",
    "timeline", "parallel_coordinates", "gantt_chart", "treemap",
]