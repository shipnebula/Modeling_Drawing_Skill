"""
tests/test_utils.py — Test utility functions.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import numpy as np
import matplotlib.pyplot as plt


class TestFormatNumbers:
    def test_smart_small(self):
        from plot import format_numbers
        assert format_numbers(1234) == '1234'

    def test_smart_thousands(self):
        from plot import format_numbers
        result = format_numbers(12345)
        assert 'K' in result

    def test_smart_millions(self):
        from plot import format_numbers
        result = format_numbers(1234567)
        assert 'M' in result

    def test_thousands_style(self):
        from plot import format_numbers
        assert format_numbers(1234567, style='thousands') == '1,234,567'

    def test_decimal_style(self):
        from plot import format_numbers
        assert format_numbers(3.14159, style='decimal', decimals=2) == '3.14'

    def test_percent_style(self):
        from plot import format_numbers
        result = format_numbers(0.45, style='percent')
        assert '%' in result

    def test_scientific_style(self):
        from plot import format_numbers
        result = format_numbers(1.234e-5, style='scientific')
        assert 'e' in result

    def test_integer(self):
        from plot import format_numbers
        assert format_numbers(100) == '100'


class TestFigureSetup:
    def test_setup_figure_default(self):
        from plot import setup_figure
        fig, ax = setup_figure()
        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_setup_figure_preset(self):
        from plot import setup_figure
        fig, ax = setup_figure(figsize='large')
        plt.close(fig)

    def test_figsubplots(self):
        from plot import figsubplots
        fig, axes = figsubplots(nrows=2, ncols=2)
        assert axes.shape == (2, 2)
        plt.close(fig)


class TestAutoLayout:
    def test_basic(self):
        from plot import auto_layout, setup_figure
        fig, ax = setup_figure()
        auto_layout(fig)
        plt.close(fig)


class TestAddFigureTitle:
    def test_basic(self):
        from plot import add_figure_title, setup_figure
        fig, ax = setup_figure()
        add_figure_title(fig, 'Title')
        plt.close(fig)

    def test_with_subtitle(self):
        from plot import add_figure_title, setup_figure
        fig, ax = setup_figure()
        add_figure_title(fig, 'Title', subtitle='Subtitle')
        plt.close(fig)


class TestAddSourceNote:
    def test_basic(self):
        from plot import add_source_note, setup_figure
        fig, ax = setup_figure()
        add_source_note(ax, 'Source: Test')
        plt.close(fig)