# Changelog

All notable changes to this project.

## [1.1.0] - 2025-01-15

### Added
- **`plot()` universal function** — one function for everything. Auto-detects chart type from data structure.
- **`FigureFactory` class** — batch generate multiple figures with consistent styling. Auto-numbered saves.
- **Chart type aliases** — use short names like `type='bar'` instead of `type='bar_chart'`.
- **Auto-detection from DataFrame** — pass a pandas DataFrame and it picks the best chart type.
- **`list_chart_types()`** — returns all available chart type names.

### Changed
- Version bumped to 1.1.0
- `__init__.py` exports `plot()`, `FigureFactory`, `list_chart_types`

## [1.0.0] - 2025-01-14

### Added
- Initial release
- 40+ chart types across 4 categories (basic, model, advanced, infographic)
- 30+ color palettes (qualitative, sequential, diverging, theme)
- 7 style presets (nature, publication, economist, minimal, dark, poster, dark_poster)
- CLI renderer (`scripts/render.py`)
- 50+ unit tests
- 33 example figures (SVG + PDF)
- Competition strategy guides for CUMCM and MCM/ICM

### Fixed
- Figure memory leaks — `save_figure()` now closes figures by default
- `_seq`/`_div` used before definition in palette.py
- `axis_config` boolean check bug
- `correlation_matrix` double figure creation
- `validation_plot` undefined palette variable
- `_rgb_to_hex` float→int cast
- `sequential_colormap`/`diverging_colormap` hex iteration
- `confusion_matrix` numpy int vs Python int key mismatch
- `network_graph` unsupported `zorder` kwarg
- `line_chart` single series detection
- `pie_chart`/`donut_chart` kwargs forwarding
- `violin_plot` deprecated `horizontal` parameter
- `format_numbers` integer K/M suffix
- `auto_layout` h_pad/w_pad parameter names
- `apply_style` invalid rcParam
- `kpi_card` title forwarding

---

## Unreleased

### Ideas
- More chart type aliases
- Auto-title generation from data
- More theme palettes
- LaTeX export
- Interactive mode (plotly backend)
- Template gallery