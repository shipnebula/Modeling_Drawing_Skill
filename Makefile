.PHONY: install test examples lint clean

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Generate example figures
examples:
	python examples/generate_examples.py

# Run linters
lint:
	python -m flake8 scripts/ examples/ tests/ --max-line-length 120
	python -m black --check scripts/ examples/ tests/

# Format code
format:
	python -m black scripts/ examples/ tests/

# Clean generated files
clean:
	rm -rf __pycache__/ .pytest_cache/ build/ dist/ *.egg-info/

# Full verification
verify: test examples