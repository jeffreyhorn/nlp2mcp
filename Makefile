.PHONY: help install install-dev lint format test typecheck coverage clean ingest-gamslib

# Detect virtual environment
VENV_BIN := $(shell if [ -d ".venv/bin" ]; then echo ".venv/bin/"; else echo ""; fi)
PYTHON := $(VENV_BIN)python
PIP := $(shell if [ -f ".venv/bin/pip" ]; then echo ".venv/bin/pip"; else echo "$(PYTHON) -m pip"; fi)

# Default target
help:
	@echo "Available targets:"
	@echo "  install         - Install the package"
	@echo "  install-dev     - Install the package with development dependencies"
	@echo "  lint            - Run code linters (ruff, mypy, black)"
	@echo "  typecheck       - Run mypy type checker only"
	@echo "  format          - Format code with black and ruff"
	@echo "  test            - Run tests with pytest (skips slow tests)"
	@echo "  test-all        - Run all tests including slow ones"
	@echo "  coverage        - Run tests with coverage report"
	@echo "  ingest-gamslib  - Run GAMSLib ingestion and generate dashboard"
	@echo "  clean           - Remove build artifacts and caches"
	@echo ""
	@echo "Note: If .venv/ exists, it will be used automatically"

# Install the package
install:
	$(PIP) install -e .

# Install with development dependencies
install-dev:
	$(PIP) install -e ".[dev]"

# Run linters
lint:
	@echo "Running ruff..."
	$(PYTHON) -m ruff check src/ tests/
	@echo "Running mypy..."
	$(PYTHON) -m mypy src/
	@echo "Checking formatting with black..."
	$(PYTHON) -m black --check src/ tests/

# Format code
format:
	@echo "Formatting with black..."
	$(PYTHON) -m black src/ tests/
	@echo "Sorting imports with ruff..."
	$(PYTHON) -m ruff check --fix --select I src/ tests/

# Run tests (parallel execution with pytest-xdist, skip slow tests by default)
test:
	$(PYTHON) -m pytest tests/ -n auto -m "not slow"

# Run all tests including slow ones (benchmarks, production, research)
test-all:
	$(PYTHON) -m pytest tests/ -n auto

# Run type checker
typecheck:
	@echo "Running mypy type checker..."
	$(PYTHON) -m mypy src/

# Run tests with coverage
# Note: Some parser tests may be slow; use 'make test' for faster runs
coverage:
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest --cov=src tests/

# Run GAMSLib ingestion pipeline
ingest-gamslib:
	@echo "Starting GAMSLib ingestion pipeline..."
	@if [ ! -d "tests/fixtures/gamslib" ]; then \
		echo "ERROR: GAMSLib models not found. Run ./scripts/download_gamslib_nlp.sh first"; \
		exit 1; \
	fi
	@PYTHONHASHSEED=0 $(PYTHON) scripts/ingest_gamslib.py \
		--input tests/fixtures/gamslib \
		--output reports/gamslib_ingestion_sprint8.json \
		--dashboard docs/status/GAMSLIB_CONVERSION_STATUS.md
	@echo ""
	@echo "✅ Ingestion complete!"
	@echo "   Report: reports/gamslib_ingestion_sprint8.json"
	@echo "   Dashboard: docs/status/GAMSLIB_CONVERSION_STATUS.md"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.swp" -delete
	@echo "Clean complete!"
