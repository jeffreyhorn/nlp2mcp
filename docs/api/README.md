# API Documentation

This directory contains the Sphinx configuration for auto-generating API reference documentation from the nlp2mcp source code docstrings.

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

This installs:
- Sphinx >= 7.0.0
- sphinx-rtd-theme >= 1.3.0
- sphinx-autodoc-typehints >= 1.25.0

### Build HTML Documentation

```bash
cd docs/api
make html
```

The generated HTML documentation will be in `build/html/`.

### View Documentation

Open the generated documentation in your browser:

```bash
# macOS
open build/html/index.html

# Linux
xdg-open build/html/index.html

# Windows
start build/html/index.html
```

### Other Build Targets

```bash
make clean      # Remove build artifacts
make help       # Show all available targets
make linkcheck  # Check for broken links
```

## Documentation Structure

- `source/conf.py` - Sphinx configuration
- `source/index.rst` - Documentation homepage
- `source/api.rst` - API reference index
- `source/api/` - Per-module documentation files
  - `ir.rst` - Intermediate Representation module
  - `ad.rst` - Automatic Differentiation module
  - `kkt.rst` - KKT Assembly module
  - `emit.rst` - GAMS Code Generation module
  - `cli.rst` - Command-Line Interface module
  - `validation.rst` - PATH Solver Validation module

## Docstring Style

This project uses Google-style docstrings, which are automatically parsed by Sphinx with the Napoleon extension.

Example:

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of function.

    More detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised

    Examples:
        >>> my_function("test", 42)
        True
    """
    return True
```

## Improving Documentation

To improve API documentation coverage:

1. Add docstrings to undocumented functions/classes
2. Use Google-style docstring format
3. Include type hints in function signatures
4. Add examples where helpful
5. Rebuild docs to see changes: `make html`

## Warnings

Some warnings during build are expected and can be safely ignored:

- Module import warnings for internal modules
- Docstring formatting warnings (we're using Google style, which may have minor quirks)
- Duplicate object warnings (from multiple imports)

Critical errors will prevent the build from completing.
