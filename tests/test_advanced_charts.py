"""
tests/test_advanced_charts.py — Test advanced and infographic charts.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)


class TestRadarChart:
    def test_basic(self):
        from plot import radar_chart
        labels = ['Speed', 'Accuracy', 'Cost', 'Reliability', 'Usability']
        values = [[4, 5, 3, 4, 5], [3, 4, 4, 5, 3]]
        fig = radar_chart(labels, values, names=['A', 'B'], title='Test')
        plt.close(fig)


class TestNetworkGraph:
    def test_basic(self):
        from plot import network_graph
        nodes = [0, 1, 2, 3, 4]
        edges = [(0, 1), (0, 2), (1, 3), (2, 4)]
        fig = network_graph(nodes, edges, title='Test')
        plt.close(fig)


class TestWaterfallChart:
    def test_basic(self):
        from plot import waterfall_chart
        fig = waterfall_chart(
            categories=['Start', '+Rev', '-Cost', 'End'],
            values=[100, 50, -30, 120],
            title='Test',
        )
        plt.close(fig)


class TestDumbbellPlot:
    def test_basic(self):
        from plot import dumbbell_plot
        fig = dumbbell_plot(
            labels=['A', 'B', 'C'],
            old_values=[30, 50, 20],
            new_values=[40, 60, 25],
            title='Test',
        )
        plt.close(fig)


class TestSlopeChart:
    def test_basic(self):
        from plot import slope_chart
        fig = slope_chart(
            labels=['A', 'B', 'C'],
            y1=[80, 60, 40],
            y2=[70, 50, 45],
            title='Test',
        )
        plt.close(fig)


class TestGanttChart:
    def test_basic(self):
        from plot import gantt_chart
        tasks = [
            {'name': 'Task 1', 'start': 0, 'end': 5, 'progress': 1.0},
            {'name': 'Task 2', 'start': 5, 'end': 10, 'progress': 0.5},
        ]
        fig = gantt_chart(tasks, title='Test')
        plt.close(fig)


class TestTreemap:
    def test_basic(self):
        from plot import treemap
        fig = treemap([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
                      title='Test')
        plt.close(fig)


class TestDashboard:
    def test_basic(self):
        from plot import dashboard
        metrics = [
            {'label': 'Accuracy', 'value': '94%', 'change': '+2%', 'change_dir': 'up',
             'progress': 0.94},
            {'label': 'F1', 'value': '0.91', 'change': '+0.03', 'change_dir': 'up',
             'progress': 0.91},
        ]
        fig = dashboard(metrics, title='Test', ncols=2)
        plt.close(fig)


class TestKpiCard:
    def test_basic(self):
        from plot import kpi_card
        fig = kpi_card(label='Revenue', value='$4.2M', change='+12%',
                       change_dir='up', progress=0.84, title='Test')
        plt.close(fig)


class TestGauge:
    def test_basic(self):
        from plot import gauge
        fig = gauge(value=75, min_val=0, max_val=100, label='Progress',
                    title='Test')
        plt.close(fig)


class TestSparkline:
    def test_basic(self):
        from plot import sparkline
        values = np.cumsum(np.random.randn(50))
        fig = sparkline(values, title='Test')
        plt.close(fig)


class TestProcessFlow:
    def test_basic(self):
        from plot import process_flow
        steps = ['Step 1', 'Step 2', 'Step 3', 'Step 4']
        fig = process_flow(steps, title='Test')
        plt.close(fig)


class TestMindMap:
    def test_basic(self):
        from plot import mind_map
        branches = [
            {'label': 'Branch A', 'items': ['Item 1', 'Item 2']},
            {'label': 'Branch B', 'items': ['Item 3', 'Item 4']},
        ]
        fig = mind_map('Center', branches, title='Test')
        plt.close(fig)


class TestComparisonBar:
    def test_basic(self):
        from plot import comparison_bar
        fig = comparison_bar(['A', 'B', 'C'], [85, 72, 90], target=80, title='Test')
        plt.close(fig)


class TestBulletChart:
    def test_basic(self):
        from plot import bullet_chart
        fig = bullet_chart(actual=85, target=90, min_val=0, max_val=100,
                           benchmarks=[70, 80], title='Test')
        plt.close(fig)


class TestTimeline:
    def test_basic(self):
        from plot import timeline
        events = [
            {'time': 1.0, 'label': 'Start', 'category': 'milestone', 'duration': 2},
            {'time': 3.0, 'label': 'End', 'category': 'milestone', 'duration': 1},
        ]
        fig = timeline(events, title='Test')
        plt.close(fig)


class TestSankeyDiagram:
    def test_basic(self):
        from plot import sankey_diagram
        flows = [(0, 1, 50), (0, 2, 30), (1, 3, 40), (2, 3, 40)]
        labels = ['Src', 'Mid', 'Mid2', 'Sink']
        fig = sankey_diagram(flows, labels=labels, title='Test')
        plt.close(fig)