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

from .palette import auto_colors, get_palette, blend, lightness, is_dark, NEUTRAL, ACCENT
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
        edge_dict = {tuple(e): edge_labels[i] for i, e in enumerate(edges)}
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
        Flow connections. Source/target may be node indices or
        node names (strings are mapped to indices automatically).
    labels : list of str, optional
        Node labels (defaults to the node names, or ``Node i``).
    """
    fig, ax = setup_figure(figsize, **kwargs)

    # Accept string node names in flows
    str_nodes = [v for f in flows for v in (f[0], f[1]) if isinstance(v, str)]
    if str_nodes:
        name_to_idx = {name: i for i, name in enumerate(dict.fromkeys(str_nodes))}
        flows = [
            (name_to_idx.get(s, s), name_to_idx.get(t, t), val)
            for s, t, val in flows
        ]

    if labels is None:
        max_node = max(max(f[0] for f in flows), max(f[1] for f in flows))
        labels = [f"Node {i}" for i in range(max_node + 1)]
        for name, idx in (name_to_idx.items() if str_nodes else ()):
            labels[idx] = str(name)

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
    series_names: Optional[list[str]] = None
    if isinstance(data, dict):
        # {name: [dim values]} — one labeled line per entry
        series_names = [str(k) for k in data.keys()]
        data_arr = np.array([np.asarray(v, dtype=float) for v in data.values()])
    else:
        data_arr = np.array(data, dtype=float)
    n_points, n_dims = data_arr.shape

    if labels is None:
        labels = [f"Dim {i+1}" for i in range(n_dims)]

    x_pos = np.arange(n_dims)
    colors = auto_colors(n_points, palette)

    for i, row in enumerate(data_arr):
        row_label = series_names[i] if series_names else None
        ax.plot(x_pos, row, color=colors[i % len(colors)],
                linewidth=line_width, alpha=alpha, zorder=2,
                label=row_label)
        ax.scatter(x_pos, row, c=colors[i % len(colors)], s=20,
                   alpha=alpha, zorder=3)

    if series_names and n_points <= 15:
        ax.legend(frameon=False, fontsize=label_fontsize, loc="best")

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

    # Squarified treemap (Bruls et al.) — areas normalized to the canvas
    def _squarify(areas, x, y, w, h):
        """Return [(orig_index, (rx, ry, rw, rh)), ...] via squarified layout."""
        rects = []
        order = np.argsort(areas)[::-1]
        items = [(int(order[k]), float(areas[order[k]])) for k in range(len(areas))]

        def worst(row, length):
            s = sum(a for _, a in row)
            if s <= 0 or length <= 0:
                return float("inf")
            mx, mn = max(a for _, a in row), min(a for _, a in row)
            return max(length * length * mx / (s * s), s * s / (length * length * mn))

        rx, ry, rw, rh = x, y, w, h
        while items:
            # items are laid along the shorter side of the remaining rect
            length = min(rw, rh)
            row = [items.pop(0)]
            while items and worst(row + [items[0]], length) <= worst(row, length):
                row.append(items.pop(0))
            s = sum(a for _, a in row)
            if rw >= rh:
                # vertical strip along the left edge (items stacked along rh)
                col_w = s / rh if rh > 0 else 0
                cy = ry
                for oi, a in row:
                    ih = a / col_w if col_w > 0 else 0
                    rects.append((oi, (rx, cy, col_w, ih)))
                    cy += ih
                rx += col_w
                rw -= col_w
            else:
                # horizontal strip along the top edge (items laid along rw)
                row_h = s / rw if rw > 0 else 0
                cx = rx
                for oi, a in row:
                    iw = a / row_h if row_h > 0 else 0
                    rects.append((oi, (cx, ry, iw, row_h)))
                    cx += iw
                ry += row_h
                rh -= row_h
        return rects

    canvas_area = figsize[0] * figsize[1]
    areas = data_arr / total * canvas_area if total > 0 else np.zeros_like(data_arr)
    rects = _squarify(areas, 0.0, 0.0, figsize[0], figsize[1])

    for oi, (rxv, ryv, rwv, rhv) in rects:
        color = colors[oi % len(colors)]
        ax.add_patch(Rectangle(
            (rxv, ryv), rwv, rhv,
            facecolor=color, edgecolor="white", linewidth=1.5,
            alpha=0.85, zorder=2,
        ))
        if labels_arr[oi]:
            cx = rxv + rwv / 2
            cy = ryv + rhv / 2
            fs = min(font_size, max(6, 4 * min(rwv, rhv) ** 0.5))
            ax.text(
                cx, cy, f"{labels_arr[oi]}\n{data_arr[oi]:.1f}",
                ha="center", va="center", fontsize=fs,
                color="white", fontweight="bold",
                zorder=5, linespacing=1.2,
            )

    ax.set_xlim(0, figsize[0])
    ax.set_ylim(0, figsize[1])
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    try:
        fig.tight_layout()
    except (UserWarning, ValueError):
        pass

    if save_path:
        save_figure(fig, save_path)
    return fig

# ──────────────────────────────────────────────
#  AHP  HIERARCHY  (层次分析法结构图)
# ──────────────────────────────────────────────

def ahp_hierarchy(
    goal: str,
    criteria: Sequence[str],
    alternatives: Sequence[str],
    weights: Optional[Sequence[float]] = None,
    title: str | None = None,
    figsize: tuple | None = None,
    palette: str = "nature_qual",
    criterion_weights: Optional[Sequence[float]] = None,
    node_fontsize: float = 9,
    weight_fontsize: float = 7.5,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Analytic Hierarchy Process structure diagram — goal on top,
    criteria in the middle (with optional weights), alternatives at
    the bottom. The standard model-setup figure for evaluation-type
    CUMCM problems.

    Parameters
    ----------
    goal : str
        Top-level objective.
    criteria : list of str
        Middle-layer criteria.
    alternatives : list of str
        Bottom-layer alternatives.
    weights : list of float, optional
        Alias for ``criterion_weights`` — weight of each criterion
        (annotated next to the criterion nodes when given).

    Returns
    -------
    Figure
    """
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    if weights is not None and criterion_weights is None:
        criterion_weights = weights
    n_c, n_a = len(criteria), len(alternatives)
    if figsize is None:
        figsize = (max(8, 1.8 * max(n_c, n_a)), 5.2)

    kwargs.pop("style", None)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    colors = auto_colors(3, palette)
    goal_color, crit_color, alt_color = colors[0], blend(colors[1], "#FFFFFF", 0.15), blend(colors[2], "#FFFFFF", 0.3)

    def box(x, y, text, color, w, h):
        ax.add_patch(FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.012", facecolor=color,
            edgecolor="white", lw=1.4, zorder=3,
        ))
        ax.text(x, y, str(text), ha="center", va="center",
                fontsize=node_fontsize, color="#FFFFFF" if is_dark(color) else "#1A1A1A",
                fontweight="bold", zorder=4)

    box(0.5, 0.90, goal, goal_color, 0.42, 0.09)

    crit_w = 0.84 / max(n_c, 1)
    crit_pos = []
    for i, c in enumerate(criteria):
        cx = 0.08 + crit_w * (i + 0.5)
        crit_pos.append(cx)
        label = str(c)
        if criterion_weights is not None and i < len(criterion_weights):
            label = f"{c}\n({float(criterion_weights[i]):.3f})"
        box(cx, 0.58, label, crit_color, min(crit_w * 0.94, 0.20),
            0.085 + (0.022 if criterion_weights is not None else 0))

    alt_w = 0.88 / max(n_a, 1)
    for i, a in enumerate(alternatives):
        cx = 0.06 + alt_w * (i + 0.5)
        box(cx, 0.22, a, alt_color, min(alt_w * 0.92, 0.18), 0.08)
        # connect every criterion to every alternative
        for cx_c in crit_pos:
            ax.add_patch(FancyArrowPatch(
                (cx_c, 0.535), (cx, 0.262),
                arrowstyle="-", color="#BBBBBB", lw=0.8,
                shrinkA=0, shrinkB=0, zorder=1,
            ))
    for cx_c in crit_pos:
        ax.add_patch(FancyArrowPatch(
            (0.5, 0.853), (cx_c, 0.626),
            arrowstyle="-|>", color="#999999", lw=1,
            shrinkA=0, shrinkB=0, mutation_scale=9, zorder=2,
        ))
    for i in range(n_a):
        cx = 0.06 + alt_w * (i + 0.5)
        best = crit_pos[int(np.argmax(criterion_weights))] if criterion_weights is not None else None
        if best is not None:
            ax.add_patch(FancyArrowPatch(
                (best, 0.535), (cx, 0.262),
                arrowstyle="-", color="#999999", lw=0.8,
                shrinkA=0, shrinkB=0, zorder=1,
            ))

    ax.text(0.015, 0.90, "Goal", fontsize=8.5, color="#888888",
            ha="left", va="center")
    ax.text(0.015, 0.58, "Criteria", fontsize=8.5, color="#888888",
            ha="left", va="center")
    ax.text(0.015, 0.22, "Alternatives", fontsize=8.5, color="#888888",
            ha="left", va="center")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  CLUSTERMAP  (heatmap + dendrograms)
# ──────────────────────────────────────────────

def clustermap(
    data,
    row_labels: Optional[Sequence[str]] = None,
    col_labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    figsize: tuple = (9, 7),
    cmap: str = "RdYlBu_r",
    method: str = "average",
    metric: str = "euclidean",
    standardize: bool = False,
    annot: bool = False,
    dendrogram_ratio: float = 0.16,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Clustered heatmap — rows and columns reordered by hierarchical
    clustering with dendrograms attached (seaborn clustermap style,
    zero extra dependency).

    Parameters
    ----------
    data : 2-D array-like
    standardize : bool
        Z-score columns before clustering and coloring.

    Returns
    -------
    Figure
    """
    from scipy.cluster.hierarchy import dendrogram as _dend, linkage as _linkage

    arr = np.asarray(data, dtype=float).copy()
    if standardize:
        arr = (arr - arr.mean(axis=0)) / np.where(arr.std(axis=0) == 0, 1, arr.std(axis=0))
    n_rows, n_cols = arr.shape
    row_labels = list(row_labels) if row_labels else [f"R{i + 1}" for i in range(n_rows)]
    col_labels = list(col_labels) if col_labels else [f"C{j + 1}" for j in range(n_cols)]

    row_link = _linkage(arr, method=method, metric=metric)
    col_link = _linkage(arr.T, method=method, metric=metric)

    kwargs.pop("style", None)
    fig = plt.figure(figsize=figsize)
    dr = dendrogram_ratio
    gs = fig.add_gridspec(
        2, 2, width_ratios=[dr, 1 - dr], height_ratios=[dr, 1 - dr],
        wspace=0.02, hspace=0.02,
    )
    ax_row = fig.add_subplot(gs[1, 0])
    ax_col = fig.add_subplot(gs[0, 1])
    ax = fig.add_subplot(gs[1, 1])

    _dend(row_link, ax=ax_row, orientation="left", no_labels=True,
          color_threshold=0.7 * row_link[:, 2].max())
    _dend(col_link, ax=ax_col, no_labels=True,
          color_threshold=0.7 * col_link[:, 2].max())
    ax_row.invert_yaxis()
    ax_row.axis("off")
    ax_col.axis("off")

    order_r = row_link[:, :2].astype(int).ravel()
    leaves_r = _leaf_order(row_link, n_rows)
    leaves_c = _leaf_order(col_link, n_cols)
    mat = arr[np.ix_(leaves_r, leaves_c)]

    im = ax.imshow(mat, cmap=cmap, aspect="auto")
    if annot and n_rows * n_cols <= 400:
        for i in range(n_rows):
            for j in range(n_cols):
                ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center",
                        fontsize=7,
                        color="white" if abs(mat[i, j] - np.nanmean(mat)) > 0.8 * np.nanstd(mat) else "#1A1A1A")
    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ax.set_xticklabels([col_labels[k] for k in leaves_c],
                       fontsize=8, rotation=90)
    ax.set_yticklabels([row_labels[k] for k in leaves_r], fontsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cb.outline.set_visible(False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


def _leaf_order(link, n_leaves) -> list[int]:
    """Leaf order from a scipy linkage matrix (iterative)."""
    from scipy.cluster.hierarchy import leaves_list
    return [int(i) for i in leaves_list(link)]


# ──────────────────────────────────────────────
#  CORRELATION  NETWORK
# ──────────────────────────────────────────────

def correlation_network(
    data,
    threshold: float = 0.5,
    labels: Optional[Sequence[str]] = None,
    title: str | None = None,
    figsize: tuple = (8, 7),
    layout: str = "spring",
    positive_color: str = "#C73E1D",
    negative_color: str = "#2E86AB",
    node_color: str = "#F4F1EA",
    edge_alpha: float = 0.75,
    min_abs: float = 1e-9,
    seed: int = 42,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Strong correlations as a network — red edges positive, blue
    negative, width ∝ |r|. The readable alternative to a big
    correlation matrix.

    Parameters
    ----------
    data : 2-D array-like (n_vars × n_obs) or square correlation matrix
        Pass a square symmetric matrix and set ``square=True``.
    threshold : float
        Draw edges only for |r| >= threshold.

    Returns
    -------
    Figure
    """
    import matplotlib.patches as mpatches

    arr = np.asarray(data, dtype=float)
    square = kwargs.pop("square", arr.shape[0] == arr.shape[1])
    if square:
        corr = arr
    else:
        corr = np.corrcoef(arr)
    n = corr.shape[0]
    labels = list(labels) if labels else [f"V{i + 1}" for i in range(n)]

    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    if layout == "spring":
        rng = np.random.default_rng(seed)
        pos = rng.uniform(-1, 1, (n, 2))
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)
                 if abs(corr[i, j]) >= max(threshold, min_abs)]
        k = 1.5 / np.sqrt(n)      # ideal edge length
        temp = 0.15
        cool = temp / 400
        for _ in range(400):      # Fruchterman–Reingold with cooling
            disp = np.zeros_like(pos)
            diff = pos[:, None, :] - pos[None, :, :]
            dist = np.sqrt((diff ** 2).sum(-1)) + 1e-9
            rep = (diff / dist[..., None]) * (k * k / dist)[..., None]
            disp += rep.sum(axis=1)
            for i, j in edges:
                d = dist[i, j]
                disp[i] += (diff[i, j] / d) * (d * d / k)
                disp[j] -= (diff[i, j] / d) * (d * d / k)
            norm = np.sqrt((disp ** 2).sum(1, keepdims=True)) + 1e-12
            disp = disp / norm * np.minimum(norm, temp)
            pos += disp
            temp = max(temp - cool, 0.005)
        pos -= pos.mean(axis=0)
        span = np.abs(pos).max()
        pos /= span if span > 0 else 1
    else:  # circular
        ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
        pos = np.column_stack([np.cos(ang), np.sin(ang)])

    for i in range(n):
        for j in range(i + 1, n):
            r = corr[i, j]
            if abs(r) < max(threshold, min_abs):
                continue
            color = positive_color if r > 0 else negative_color
            ax.plot([pos[i, 0], pos[j, 0]], [pos[i, 1], pos[j, 1]],
                    color=color, lw=0.7 + 2.6 * abs(r), alpha=edge_alpha,
                    solid_capstyle="round", zorder=1)

    ax.scatter(pos[:, 0], pos[:, 1], s=560, c=node_color,
               edgecolors="#8A8A8A", lw=1.1, zorder=3)
    for i, lab in enumerate(labels):
        ax.text(pos[i, 0], pos[i, 1], lab, ha="center", va="center",
                fontsize=8, color="#1A1A1A", zorder=4)

    handles = [
        mpatches.Patch(color=positive_color, label=f"positive ≥ {threshold:g}"),
        mpatches.Patch(color=negative_color, label=f"negative ≤ −{threshold:g}"),
    ]
    ax.legend(handles=handles, frameon=False, loc="lower left", fontsize=8.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig



__all__ = [
    "network_graph", "sankey_diagram", "radar_chart",
    "waterfall_chart", "dumbbell_plot", "slope_chart",
    "timeline", "parallel_coordinates", "gantt_chart", "treemap",
    "ahp_hierarchy", "clustermap", "correlation_network",
    "circle_pack", "arc_diagram",
]


# ──────────────────────────────────────────────
#  CIRCLE  PACKING  (part-to-whole bubbles)
# ──────────────────────────────────────────────

def circle_pack(
    values: dict,
    title: str | None = None,
    figsize: tuple = (8.5, 8.5),
    palette: str = "nature_qual",
    gap: float = 1.06,
    show_labels: bool = True,
    label_size: float = 9,
    show_values: bool = True,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Circle packing — each value becomes a bubble with area ∝ value,
    packed front-of-center outward. An eye-catching part-to-whole
    alternative to pie/treemap.

    Parameters
    ----------
    values : dict ``{name: value}``

    Returns
    -------
    Figure
    """
    names = list(values.keys())
    vals = np.asarray([float(values[n]) for n in names], float)
    if (vals <= 0).any():
        raise ValueError("circle_pack values must be positive.")
    order = np.argsort(-vals)
    radii = np.sqrt(vals) / np.sqrt(vals.max())  # area-proportional
    radii = radii[order]
    names_sorted = [names[i] for i in order]
    vals_sorted = vals[order]

    # greedy packing: each circle touches a placed circle, choose the
    # candidate closest to the origin (classic front-of-center look)
    centers = [(0.0, 0.0)]
    placed_r = [radii[0]]
    for r in radii[1:]:
        best, best_d = None, float("inf")
        for k in range(len(centers)):
            px, py = centers[k]
            pr = placed_r[k]
            for ang in np.linspace(0, 2 * np.pi, 120, endpoint=False):
                cx = px + (pr + r) * gap * np.cos(ang)
                cy = py + (pr + r) * gap * np.sin(ang)
                if all(np.hypot(cx - qx, cy - qy) >= (qr + r) * gap
                       for (qx, qy), qr in zip(centers, placed_r)):
                    d = np.hypot(cx, cy)
                    if d < best_d:
                        best, best_d = (cx, cy), d
        centers.append(best)
        placed_r.append(r)

    scale = 1.0 / (max(placed_r) + max(
        np.hypot(cx, cy) for cx, cy in centers))
    fig, ax = setup_figure(figsize, style="nature", **kwargs)
    colors = auto_colors(len(names_sorted), palette)

    for (cx, cy), r, c, name, v in zip(centers, placed_r, colors,
                                       names_sorted, vals_sorted):
        sx, sy, rr = cx * scale, cy * scale, r * scale
        ax.add_patch(plt.Circle((sx, sy), rr * 0.985,
                                facecolor=c, edgecolor="white", lw=1.6,
                                alpha=0.92, zorder=2))
        if show_labels and rr > 0.08:
            ax.text(sx, sy + rr * 0.12, str(name),
                    ha="center", va="center", fontsize=label_size,
                    color="white" if rr > 0.2 else "#333333",
                    fontweight="bold", zorder=3)
            if show_values:
                ax.text(sx, sy - rr * 0.18,
                        f"{v:.4g}", ha="center", va="center",
                        fontsize=label_size - 1.5, color="white"
                        if rr > 0.2 else "#555555", zorder=3)

    lim = 1.06
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig


# ──────────────────────────────────────────────
#  ARC  DIAGRAM  (sequence relationships)
# ──────────────────────────────────────────────

def arc_diagram(
    nodes: Sequence[str],
    edges: Sequence[tuple],
    title: str | None = None,
    figsize: tuple = (10, 5),
    palette: str = "nature_qual",
    node_size: float = 380,
    linewidth_scale: float = 3.0,
    show_edge_labels: bool = False,
    save_path: str | None = None,
    **kwargs,
) -> plt.Figure:
    """
    Arc diagram — nodes placed along a baseline, relationships drawn as
    arcs above it (thickness ∝ weight). Reads naturally for sequences:
    pipeline steps, process hand-offs, character/page co-occurrence.

    Parameters
    ----------
    nodes : list of str
    edges : list of (node_i, node_j) or (node_i, node_j, weight)

    Returns
    -------
    Figure
    """
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    fig, ax = setup_figure(figsize, style="nature", **kwargs)

    parsed = []
    for e in edges:
        if len(e) == 3:
            i, j, w = idx[e[0]], idx[e[1]], float(e[2])
        else:
            i, j = idx[e[0]], idx[e[1]]
            w = 1.0
        parsed.append((i, j, w))
    max_w = max((w for _, _, w in parsed), default=1.0) or 1.0

    colors = auto_colors(n, palette)
    for i, j, w in parsed:
        x0, x1 = i, j
        cx = (x0 + x1) / 2
        ry = (abs(x1 - x0) / 2) * 1.15 + 0.12
        lw = 1.0 + linewidth_scale * w / max_w
        arc = plt.Rectangle  # noqa: F841  (docstring hint)
        from matplotlib.patches import Arc as _Arc
        ax.add_patch(_Arc((cx, 0), abs(x1 - x0), 2 * ry, theta1=0,
                          theta2=180, edgecolor="#C73E1D", lw=lw,
                          alpha=0.28 + 0.55 * w / max_w, zorder=2))
        if show_edge_labels:
            ax.text(cx, ry + 0.06, f"{w:g}", ha="center", fontsize=8,
                    color="#666666")

    ax.scatter(range(n), np.zeros(n), s=node_size, c=colors[:n],
               edgecolors="white", lw=1.2, zorder=3)
    for i, name in enumerate(nodes):
        ax.text(i, -0.14, str(name), ha="center", va="top", fontsize=9,
                color="#1A1A1A", zorder=4)

    ax.set_xlim(-0.7, n - 0.3)
    max_ry = max(((abs(i - j) / 2) * 1.15 + 0.12 for i, j, _ in parsed),
                 default=1.0)
    ax.set_ylim(-0.35, max_ry + 0.3)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    return fig
