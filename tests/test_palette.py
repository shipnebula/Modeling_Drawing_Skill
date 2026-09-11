"""
tests/test_palette.py — Test palette module.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest


class TestPalettes:
    def test_get_palette_qualitative(self):
        from plot.palette import get_palette
        p = get_palette('nature_qual')
        assert isinstance(p, list)
        assert len(p) >= 8
        assert all(c.startswith('#') for c in p)

    def test_get_palette_sequential(self):
        from plot.palette import get_palette
        p = get_palette('viridis')
        assert len(p) == 9
        assert all(c.startswith('#') for c in p)

    def test_get_palette_diverging(self):
        from plot.palette import get_palette
        p = get_palette('coolwarm')
        assert len(p) == 9
        assert all(c.startswith('#') for c in p)

    def test_get_palette_theme(self):
        from plot.palette import get_palette
        p = get_palette('data_analysis')
        assert len(p) == 8

    def test_get_palette_unknown_raises(self):
        from plot.palette import get_palette
        with pytest.raises(ValueError):
            get_palette('nonexistent')

    def test_get_color(self):
        from plot.palette import get_color
        c = get_color('nature_qual', 0)
        assert c.startswith('#')
        assert len(c) == 7

    def test_auto_colors(self):
        from plot.palette import auto_colors
        c = auto_colors(5)
        assert len(c) == 5
        assert all(x.startswith('#') for x in c)

    def test_auto_colors_cycling(self):
        from plot.palette import auto_colors
        c = auto_colors(20, 'nature_qual')
        assert len(c) == 20

    def test_sequential_colormap(self):
        from plot.palette import sequential_colormap
        colors = sequential_colormap('viridis', n=50)
        assert len(colors) == 50
        assert all(c.startswith('#') for c in colors)

    def test_diverging_colormap(self):
        from plot.palette import diverging_colormap
        colors = diverging_colormap('coolwarm', n=50)
        assert len(colors) == 50

    def test_blend(self):
        from plot.palette import blend
        result = blend('#FF0000', '#00FF00', 0.5)
        assert result.startswith('#')
        assert len(result) == 7

    def test_blend_endpoints(self):
        from plot.palette import blend
        assert blend('#FF0000', '#00FF00', 0.0) == '#FF0000'
        assert blend('#FF0000', '#00FF00', 1.0) == '#00FF00'

    def test_lightness(self):
        from plot.palette import lightness
        c = lightness('#808080', 0.3)
        assert c.startswith('#')
        assert len(c) == 7

    def test_is_dark(self):
        from plot.palette import is_dark
        assert is_dark('#000000')
        assert not is_dark('#FFFFFF')

    def test_contrast_color(self):
        from plot.palette import contrast_color
        # Dark background → white text
        assert contrast_color('#000000') == '#FFFFFF'
        # Light background → dark text
        assert contrast_color('#FFFFFF') == '#1A1A1A'

    def test_neutral_and_accent(self):
        from plot.palette import NEUTRAL, ACCENT
        assert NEUTRAL.startswith('#')
        assert ACCENT.startswith('#')