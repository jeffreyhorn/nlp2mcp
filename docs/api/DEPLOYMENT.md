# API Documentation Deployment Guide

**How to build and deploy the Sphinx API documentation**

Version: 0.5.0-beta  
Last Updated: 2025-11-08

---

## Overview

nlp2mcp uses Sphinx to auto-generate API documentation from Python docstrings. This guide covers building, viewing, and deploying the documentation.

---

## Quick Start

### Build Documentation Locally

```bash
cd docs/api
make html
```

### View Documentation

```bash
# Open in browser
open build/html/index.html  # macOS
xdg-open build/html/index.html  # Linux
start build/html/index.html  # Windows
```

---

## Building Documentation

### Prerequisites

Install documentation dependencies:

```bash
pip install nlp2mcp[docs]
```

Or manually:

```bash
pip install sphinx>=7.0.0 sphinx-rtd-theme>=1.3.0 sphinx-autodoc-typehints>=1.25.0
```

### Build Commands

**Full HTML build:**
```bash
cd docs/api
make html
```

**Clean build (remove cached files):**
```bash
cd docs/api
make clean
make html
```

**Check for warnings:**
```bash
cd docs/api
make html 2>&1 | grep WARNING
```

**Build with specific verbosity:**
```bash
cd docs/api
sphinx-build -v source build/html  # Verbose
sphinx-build -q source build/html  # Quiet
```

### Output Location

Built documentation is in `docs/api/build/html/`:

- `index.html` - Main landing page
- `api/` - Module documentation
- `_static/` - CSS, JavaScript, images
- `_sources/` - ReStructuredText sources

---

## Configuration

### Sphinx Configuration

Main configuration file: `docs/api/source/conf.py`

**Key settings:**

```python
project = "nlp2mcp"
author = "Jeffrey Horn"
release = "0.5.0-beta"

extensions = [
    "sphinx.ext.autodoc",         # Auto-generate from docstrings
    "sphinx.ext.napoleon",        # Google/NumPy docstring support
    "sphinx.ext.viewcode",        # Link to source code
    "sphinx.ext.intersphinx",     # Link to external docs
    "sphinx_autodoc_typehints",   # Better type hint rendering
]

html_theme = "sphinx_rtd_theme"  # ReadTheDocs theme
```

### Updating Version Number

When releasing a new version:

1. Update `docs/api/source/conf.py`:
   ```python
   release = "0.6.0"  # Update version
   ```

2. Rebuild documentation:
   ```bash
   cd docs/api
   make clean
   make html
   ```

### Adding New Modules

Sphinx auto-discovers modules in `src/`. To add a new module:

1. **No action needed** - autodoc automatically finds new modules
2. Rebuild: `make html`
3. Verify module appears in API docs

### Customizing Theme

Edit `docs/api/source/conf.py`:

```python
html_theme_options = {
    "navigation_depth": 4,          # Sidebar depth
    "collapse_navigation": False,   # Keep sidebar expanded
    "sticky_navigation": True,      # Sticky sidebar
    "includehidden": True,          # Show hidden toctree
    "titles_only": False,           # Show full headings
}
```

---

## Deployment Options

### Option 1: GitHub Pages (Recommended)

**Setup:**

1. Create `docs` branch:
   ```bash
   git checkout -b docs
   ```

2. Copy built HTML to root:
   ```bash
   cp -r docs/api/build/html/* .
   git add .
   git commit -m "Update API docs"
   git push origin docs
   ```

3. Enable GitHub Pages:
   - Go to repository Settings → Pages
   - Source: Deploy from branch `docs`
   - Save

**Automated deployment with GitHub Actions:**

Create `.github/workflows/docs.yml`:

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -e .[docs]
      
      - name: Build docs
        run: |
          cd docs/api
          make html
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/api/build/html
```

**Access:** https://jeffreyhorn.github.io/nlp2mcp/

---

### Option 2: ReadTheDocs

**Setup:**

1. Sign up at https://readthedocs.org/
2. Import repository
3. Configure build:
   - Create `.readthedocs.yaml`:
     ```yaml
     version: 2

     build:
       os: ubuntu-22.04
       tools:
         python: "3.12"

     sphinx:
       configuration: docs/api/source/conf.py

     python:
       install:
         - method: pip
           path: .
           extra_requirements:
             - docs
     ```

4. Trigger build

**Access:** https://nlp2mcp.readthedocs.io/

**Advantages:**
- Automatic builds on push
- Version management
- Search functionality
- No GitHub Actions needed

---

### Option 3: Local Hosting

**For development/testing:**

```bash
cd docs/api/build/html
python -m http.server 8000
```

**Access:** http://localhost:8000

**For production (nginx):**

Copy `docs/api/build/html/` to web server:

```bash
scp -r docs/api/build/html/* user@server:/var/www/nlp2mcp-docs/
```

---

## Troubleshooting

### Issue: "No module named 'src'"

**Problem:** Sphinx can't find source modules.

**Solution:** Check `conf.py` has correct path:

```python
import sys
import os
sys.path.insert(0, os.path.abspath("../../.."))  # Points to project root
```

### Issue: "WARNING: autodoc: failed to import module"

**Problem:** Missing dependencies.

**Solution:**

```bash
pip install -e .[docs]
```

### Issue: "Theme not found: sphinx_rtd_theme"

**Problem:** ReadTheDocs theme not installed.

**Solution:**

```bash
pip install sphinx-rtd-theme
```

### Issue: Build has many warnings

**Problem:** Docstring formatting issues.

**Common warnings:**
- Title underline too short
- Unexpected indentation
- Duplicate label

**Solution:** Fix docstrings or suppress warnings in `conf.py`:

```python
suppress_warnings = [
    'docutils',  # Suppress docutils formatting warnings
]
```

### Issue: "make: command not found"

**Problem:** No `make` on Windows.

**Solution:** Use sphinx-build directly:

```bash
cd docs/api
sphinx-build -b html source build/html
```

---

## Documentation Quality Checks

### Check for Broken Links

```bash
cd docs/api
make linkcheck
```

### Check Coverage

```bash
cd docs/api
sphinx-build -b coverage source build/coverage
cat build/coverage/python.txt  # See undocumented items
```

### Validate HTML

```bash
# Install html5validator
pip install html5validator

# Validate
html5validator --root docs/api/build/html/ --also-check-css
```

---

## Continuous Integration

### GitHub Actions Workflow

Example `.github/workflows/docs-check.yml`:

```yaml
name: Docs Check

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -e .[docs]
      
      - name: Build docs
        run: |
          cd docs/api
          make html
      
      - name: Check for warnings
        run: |
          cd docs/api
          make html 2>&1 | tee build.log
          ! grep -i warning build.log
```

---

## Best Practices

### 1. Keep Docstrings Updated

**Good:**
```python
def compute_gradient(model_ir: ModelIR) -> GradientVector:
    """
    Compute symbolic gradient of objective function.
    
    Args:
        model_ir: Normalized model intermediate representation
    
    Returns:
        Sparse gradient vector with symbolic derivatives
    
    Raises:
        ValueError: If objective not defined
    """
```

**Bad:**
```python
def compute_gradient(model_ir):
    """Compute gradient."""  # Too brief, no types
```

### 2. Use Type Hints

Sphinx-autodoc-typehints automatically documents types:

```python
def process_model(
    model_ir: ModelIR,
    options: dict[str, Any] | None = None
) -> KKTSystem:
    ...
```

### 3. Cross-Reference

Use Sphinx roles for cross-references:

```python
"""
See :class:`ModelIR` for the input format.
Calls :func:`compute_derivatives` internally.
"""
```

### 4. Include Examples

```python
"""
Examples:
    >>> model = parse_model_file("example.gms")
    >>> gradient = compute_gradient(model)
    >>> print(gradient.num_cols)
    10
"""
```

### 5. Rebuild Regularly

Rebuild docs after changes:

```bash
cd docs/api
make clean && make html
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- Build and review for warnings
- Check links: `make linkcheck`

**Per Release:**
- Update version in `conf.py`
- Rebuild: `make clean && make html`
- Deploy to hosting
- Tag documentation release

**Per Major Version:**
- Review and update landing page
- Archive old version docs (ReadTheDocs handles this automatically)

---

## Resources

- **Sphinx Documentation:** https://www.sphinx-doc.org/
- **reStructuredText Primer:** https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
- **ReadTheDocs Theme:** https://sphinx-rtd-theme.readthedocs.io/
- **Napoleon Extension:** https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

---

## Contact

For questions about documentation:
- GitHub Issues: https://github.com/jeffreyhorn/nlp2mcp/issues
- Email: jeffreydhorn@gmail.com

---

**Last updated:** November 8, 2025
