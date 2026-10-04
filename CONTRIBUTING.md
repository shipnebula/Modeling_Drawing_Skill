# Contributing

Thanks for considering contributing. Here's how to get started.

---

## First time here?

1. Fork the repo
2. Clone it locally
3. Install dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Run tests: `python -m pytest tests/ -v` (250+ tests must stay green)
6. Submit a PR

That's it. No formal process, no approval committee. Just make something good.

---

## What we're looking for

### Chart types
Add a new chart if it's useful for math modeling papers. Good candidates:
- Violin plot with KDE overlay
- Heatmap with annotations
- Small multiples
- Slope chart variants

### Palettes
Add new color palettes. Guidelines:
- Name it clearly (e.g. `warm_accents`, `cool_sequential`)
- At least 8 colors for qualitative
- Include lightness variants for sequential
- Test in grayscale

### Style presets
Add a new style preset if you have a use case. Guidelines:
- Must work with all chart types
- Test with Chinese characters
- Test in dark mode

### Documentation
Any improvement is welcome:
- Fix typos
- Add examples
- Improve explanations
- Translate to other languages

### Tests
Add tests for new features:
- Test the happy path
- Test edge cases
- Test error handling

---

## Code style

### Structure
- Use `from __future__ import annotations` at the top of every module
- Type hints on all public functions
- Docstrings on all public functions
- Keep functions under 100 lines

### Naming
- Functions: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_CASE`
- Classes: `PascalCase`

### Chart functions
Every chart function should:
- Accept `title`, `xlabel`, `ylabel`, `palette`, `save_path`
- Return a `matplotlib.figure.Figure`
- Call `setup_figure()` for consistent defaults
- Call `save_figure()` if `save_path` is provided

### Error handling
- Validate inputs early
- Raise `ValueError` for bad arguments
- Raise `TypeError` for wrong types

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run a single test
python -m pytest tests/test_basic_charts.py::TestBarChart::test_basic -v

# Run with coverage
python -m pytest tests/ --cov=plot --cov-report=html
```

### Adding tests
- Put tests in the `tests/` directory
- Name files `test_*.py`
- Use descriptive test names
- Test both happy paths and edge cases

---

## Submitting a PR

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make changes
4. Run tests
5. Push and open a PR

PR titles should be clear:
- "Add violin plot with KDE"
- "Fix save_figure format detection"
- "Add warm_accents palette"
- "Improve Chinese font handling"

---

## Code of Conduct

Be kind. Be respectful. Assume good intent. If you disagree with someone, say so respectfully. If you're being harassed, contact a maintainer.

We follow the [Contributor Covenant v1.4](CODE_OF_CONDUCT.md).

---

## Getting help

If you're stuck:
1. Check the [usage guide](docs/usage-guide.md)
2. Read the [API reference](docs/api-reference.md)
3. Look at the [examples](examples/)
4. Open an issue

We're humans too. We've all been confused by our own code.