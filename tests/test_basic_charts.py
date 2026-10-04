"""
tests/test_basic_charts.py — Test basic chart functions.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)


class TestBarChart:
    def test_basic(self):
        from plot import bar_chart
        fig = bar_chart([10, 20, 30], labels=['A', 'B', 'C'], title='Test')
        assert fig is not None
        plt.close(fig)

    def test_horizontal(self):
        from plot import bar_chart
        fig = bar_chart([10, 20, 30], labels=['A', 'B', 'C'],
                        horizontal=True, title='Test')
        plt.close(fig)

    def test_no_values(self):
        from plot import bar_chart
        fig = bar_chart([10, 20, 30], show_values=False)
        plt.close(fig)


class TestLineChart:
    def test_single_series(self):
        from plot import line_chart
        fig = line_chart([1, 2, 3], {'A': [4, 5, 6]}, title='Test')
        plt.close(fig)

    def test_multi_series_dict(self):
        from plot import line_chart
        fig = line_chart([1, 2, 3], {'A': [4, 5, 6], 'B': [7, 8, 9]}, title='Test')
        plt.close(fig)

    def test_markers(self):
        from plot import line_chart
        fig = line_chart([1, 2, 3], {'A': [4, 5, 6]}, markers=True, title='Test')
        plt.close(fig)


class TestScatterPlot:
    def test_basic(self):
        from plot import scatter_plot
        fig = scatter_plot([1, 2, 3, 4, 5], [2, 4, 6, 8, 10], title='Test')
        plt.close(fig)

    def test_with_fit(self):
        from plot import scatter_plot
        x = np.random.randn(50)
        y = x * 2 + np.random.randn(50)
        fig = scatter_plot(x, y, show_fit=True, title='Test')
        plt.close(fig)

    def test_color_by(self):
        from plot import scatter_plot
        x = np.random.randn(50)
        y = np.random.randn(50)
        colors = np.random.randn(50)
        fig = scatter_plot(x, y, color_by=colors, title='Test')
        plt.close(fig)


class TestPieChart:
    def test_basic(self):
        from plot import pie_chart
        fig = pie_chart([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
                        title='Test')
        plt.close(fig)

    def test_donut(self):
        from plot import donut_chart
        fig = donut_chart([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
                          title='Test', center_text='100%')
        plt.close(fig)


class TestHistogram:
    def test_basic(self):
        from plot import histogram
        data = np.random.randn(200)
        fig = histogram(data, title='Test')
        plt.close(fig)

    def test_kde(self):
        from plot import histogram
        data = np.random.randn(200)
        fig = histogram(data, kde=True, title='Test')
        plt.close(fig)


class TestBoxPlot:
    def test_basic(self):
        from plot import box_plot
        data = [np.random.randn(50), np.random.randn(50), np.random.randn(50)]
        fig = box_plot(data, labels=['A', 'B', 'C'], title='Test')
        plt.close(fig)


class TestGroupedBar:
    def test_basic(self):
        from plot import grouped_bar
        data = {'A': [10, 20, 30], 'B': [15, 25, 35]}
        fig = grouped_bar(data, labels=['X', 'Y', 'Z'], title='Test')
        plt.close(fig)


class TestStackedBar:
    def test_basic(self):
        from plot import stacked_bar
        data = {'A': [10, 20, 30], 'B': [15, 25, 35]}
        fig = stacked_bar(data, labels=['X', 'Y', 'Z'], title='Test')
        plt.close(fig)


class TestAreaChart:
    def test_basic(self):
        from plot import area_chart
        fig = area_chart([1, 2, 3, 4, 5], {'A': [10, 15, 20, 25, 30]}, title='Test')
        plt.close(fig)


class TestStepChart:
    def test_basic(self):
        from plot import step_chart
        fig = step_chart([1, 2, 3, 4, 5], [10, 10, 15, 15, 20], title='Test')
        plt.close(fig)


class TestViolinPlot:
    def test_basic(self):
        from plot import violin_plot
        data = [np.random.randn(50), np.random.randn(50), np.random.randn(50)]
        fig = violin_plot(data, labels=['A', 'B', 'C'], title='Test')
        plt.close(fig)