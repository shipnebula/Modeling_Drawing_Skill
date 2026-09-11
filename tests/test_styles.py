"""
tests/test_styles.py — Test styles module.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest


class TestStyles:
    def test_list_styles(self):
        from plot.styles import list_styles
        styles = list_styles()
        assert 'nature' in styles
        assert 'publication' in styles
        assert 'dark' in styles
        assert 'poster' in styles
        assert len(styles) >= 7

    def test_get_style_config(self):
        from plot.styles import get_style_config
        config = get_style_config('nature')
        assert isinstance(config, dict)
        assert 'font.size' in config
        assert config['font.size'] > 0

    def test_get_style_config_unknown(self):
        from plot.styles import get_style_config
        with pytest.raises(ValueError):
            get_style_config('nonexistent')

    def test_get_color_theme(self):
        from plot.styles import get_color_theme
        theme = get_color_theme('nature')
        assert isinstance(theme, dict)
        assert 'primary' in theme
        assert 'background' in theme

    def test_apply_style(self):
        from plot.styles import apply_style
        config = apply_style('nature')
        assert isinstance(config, dict)

    def test_apply_style_all_presets(self):
        from plot.styles import apply_style
        from plot.styles import list_styles
        for style in list_styles():
            config = apply_style(style)
            assert isinstance(config, dict)

    def test_color_themes_keys(self):
        from plot.styles import COLOR_THEMES
        assert 'nature' in COLOR_THEMES
        assert 'dark' in COLOR_THEMES
        assert 'economist' in COLOR_THEMES