.PHONY: install test gallery banner cli lint format clean verify

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Regenerate the documentation gallery (docs/images/)
gallery:
	python examples/gallery.py

# Regenerate the README banner
banner:
	python examples/banner.py

# Run the CLI end-to-end
cli:
	python -m plot.cli types

# Run linters
lint:
	python -m flake8 scripts/ examples/ tests/ --max-line-length 120
	python -m black --check scripts/ examples/ tests/

# Format code
format:
	python -m black scripts/ examples/ tests/

# Clean generated files
clean:
	rm -rf __pycache__/ .pytest_cache/ build/ dist/ *.egg-info/ figures/
	find . -name "__pycache__" -not -path "./.venv/*" -not -path "./.git/*" -exec rm -rf {} +

# Full verification
verify: test gallery
