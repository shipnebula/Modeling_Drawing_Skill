"""
tests/test_factory.py — Test plot() universal function and FigureFactory.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)


class TestPlotFunction:
    def test_auto_detect_bar(self):
        from plot import plot
        fig = plot([10, 20, 30], labels=['A', 'B', 'C'], title='Test')
        assert fig is not None
        plt.close(fig)

    def test_auto_detect_line(self):
        from plot import plot
        fig = plot({'A': [1, 2, 3], 'B': [4, 5, 6]}, x=[1, 2, 3], title='Test')
        plt.close(fig)

    def test_forced_scatter(self):
        from plot import plot
        x = np.random.randn(50)
        y = x * 2 + np.random.randn(50)
        fig = plot(x, y, type='scatter', title='Test')
        plt.close(fig)

    def test_forced_pie(self):
        from plot import plot
        fig = plot([30, 25, 20, 15, 10], labels=['A', 'B', 'C', 'D', 'E'],
                   type='pie', title='Test')
        plt.close(fig)

    def test_forced_hist(self):
        from plot import plot
        data = np.random.randn(200)
        fig = plot(data, type='hist', title='Test')
        plt.close(fig)

    def test_with_style(self):
        from plot import plot
        fig = plot([10, 20, 30], labels=['A', 'B', 'C'],
                   style='dark', title='Test')
        plt.close(fig)

    def test_with_palette(self):
        from plot import plot
        fig = plot([10, 20, 30], labels=['A', 'B', 'C'],
                   palette='ocean', title='Test')
        plt.close(fig)

    def test_unknown_type_raises(self):
        from plot import plot
        with pytest.raises(ValueError):
            plot([10, 20, 30], type='nonexistent')

    def test_sensitivity(self):
        from plot import plot
        fig = plot(
            parameters=['Rate', 'Batch', 'Layers'],
            low_values=[0.88, 0.90, 0.85],
            high_values=[0.98, 0.96, 0.94],
            type='sensitivity', title='Test',
        )
        plt.close(fig)

    def test_correlation(self):
        from plot import plot
        import pandas as pd
        df = pd.DataFrame({
            'A': np.random.randn(100),
            'B': np.random.randn(100),
            'C': np.random.randn(100),
        })
        fig = plot(df, type='correlation', title='Test')
        plt.close(fig)

    def test_dashboard(self):
        from plot import plot
        metrics = [
            {'label': 'Acc', 'value': '94%', 'change': '+2%',
             'change_dir': 'up', 'progress': 0.94},
            {'label': 'F1', 'value': '0.91', 'change': '+0.03',
             'change_dir': 'up', 'progress': 0.91},
        ]
        fig = plot(metrics, type='dashboard', title='Test')
        plt.close(fig)

    def test_radar(self):
        from plot import plot
        fig = plot(
            ['Speed', 'Accuracy', 'Cost'],
            [[4, 5, 3], [3, 4, 4]],
            names=['A', 'B'],
            type='radar', title='Test',
        )
        plt.close(fig)

    def test_network(self):
        from plot import plot
        nodes = [0, 1, 2, 3]
        edges = [(0, 1), (0, 2), (1, 3)]
        fig = plot(nodes, edges, type='network', title='Test')
        plt.close(fig)


class TestFigureFactory:
    def test_basic_usage(self):
        from plot import FigureFactory
        f = FigureFactory(style='nature')
        assert f.figures == []
        assert len(f) == 0

    def test_add_figure(self):
        from plot import FigureFactory
        f = FigureFactory(style='nature')
        fig = f.add('bar', [10, 20, 30], labels=['A', 'B', 'C'], title='Test')
        assert fig is not None
        assert len(f) == 1
        plt.close(fig)

    def test_bar_convenience(self):
        from plot import FigureFactory
        f = FigureFactory(style='nature')
        fig = f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Test')
        assert len(f) == 1
        plt.close(fig)

    def test_multiple_figures(self):
        from plot import FigureFactory
        f = FigureFactory(style='nature')
        f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Fig 1')
        f.line({'A': [1, 2, 3]}, x=[1, 2, 3], title='Fig 2')
        f.scatter(np.random.randn(50), np.random.randn(50), title='Fig 3')
        assert len(f) == 3
        for fig in f.figures:
            plt.close(fig)

    def test_title_prefix(self):
        from plot import FigureFactory
        f = FigureFactory(style='nature', title_prefix='Report:')
        f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Sales')
        assert 'Report: Sales' in f.titles[0]
        plt.close(f.figures[0])

    def test_repr(self):
        from plot import FigureFactory
        f = FigureFactory(style='nature')
        r = repr(f)
        assert 'FigureFactory' in r
        assert 'nature' in r

    def test_save_all(self):
        import tempfile, shutil
        from plot import FigureFactory
        f = FigureFactory(style='nature', output_format='png')
        f.bar([10, 20, 30], labels=['A', 'B', 'C'], title='Fig 1')
        f.line({'A': [1, 2, 3]}, x=[1, 2, 3], title='Fig 2')
        outdir = os.path.join(os.path.dirname(__file__), '..', '_test_output')
        os.makedirs(outdir, exist_ok=True)
        try:
            saved = f.save_all(outdir, close=True)
            assert len(saved) == 2
            assert all(os.path.exists(p) for p in saved)
        finally:
            shutil.rmtree(outdir, ignore_errors=True)


class TestListChartTypes:
    def test_returns_list(self):
        from plot import list_chart_types
        types = list_chart_types()
        assert isinstance(types, list)
        assert len(types) > 0

    def test_contains_common_types(self):
        from plot import list_chart_types
        types = list_chart_types()
        assert 'bar' in types
        assert 'line' in types
        assert 'scatter' in types