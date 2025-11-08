# TestPyPI Publishing Guide

## Overview

This document describes how to publish nlp2mcp to TestPyPI for validation before production release.

## Prerequisites

### 1. Create TestPyPI Account

1. Visit https://test.pypi.org/account/register/
2. Create an account and verify your email
3. Enable two-factor authentication (recommended)

### 2. Generate API Token

1. Go to https://test.pypi.org/manage/account/
2. Scroll to "API tokens" section
3. Click "Add API token"
4. Token name: `nlp2mcp-testpypi`
5. Scope: "Entire account" (or specific to nlp2mcp project after first upload)
6. Copy the token (starts with `pypi-`)
7. **Important**: Save token securely - it won't be shown again

### 3. Configure Token Locally

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

**Security Note**: Ensure `.pypirc` has restrictive permissions:
```bash
chmod 600 ~/.pypirc
```

## Publishing Process

### Step 1: Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Build packages
python -m build
```

**Expected output**:
```
Successfully built nlp2mcp-0.5.0b0.tar.gz and nlp2mcp-0.5.0b0-py3-none-any.whl
```

### Step 2: Verify Packages

```bash
# Check with twine
twine check dist/*
```

**Expected output**:
```
Checking dist/nlp2mcp-0.5.0b0-py3-none-any.whl: PASSED
Checking dist/nlp2mcp-0.5.0b0.tar.gz: PASSED
```

### Step 3: Upload to TestPyPI

```bash
# Upload
twine upload --repository testpypi dist/*
```

**Expected output**:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading nlp2mcp-0.5.0b0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 138.0/138.0 kB • 00:00
Uploading nlp2mcp-0.5.0b0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 120.0/120.0 kB • 00:00

View at:
https://test.pypi.org/project/nlp2mcp/0.5.0b0/
```

### Step 4: Verify on TestPyPI

1. Visit https://test.pypi.org/project/nlp2mcp/
2. Verify metadata:
   - Version: 0.5.0b0
   - Development Status: Beta
   - Python: >=3.11
   - License: MIT
   - All 18 classifiers present
3. Check "Download files" tab:
   - Wheel: `nlp2mcp-0.5.0b0-py3-none-any.whl`
   - Source: `nlp2mcp-0.5.0b0.tar.gz`

## Installation Testing

### Fresh Virtual Environment Test

```bash
# Create fresh environment
python -m venv /tmp/test_testpypi
source /tmp/test_testpypi/bin/activate  # On Windows: test_testpypi\Scripts\activate

# Install from TestPyPI
# Note: --extra-index-url needed for dependencies (lark, numpy, click)
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    nlp2mcp

# Verify installation
nlp2mcp --help

# Test conversion
nlp2mcp path/to/test.gms -o /tmp/output.gms

# Cleanup
deactivate
rm -rf /tmp/test_testpypi
```

## Troubleshooting

### Error: "File already exists"

If you try to upload the same version twice:

```bash
# Use --skip-existing flag
twine upload --repository testpypi --skip-existing dist/*
```

Or bump the version:
```bash
python scripts/bump_version.py patch  # 0.5.0b0 → 0.5.1
python -m build
```

### Error: "Invalid or non-existent authentication information"

1. Verify API token in `~/.pypirc`
2. Ensure token starts with `pypi-`
3. Check token hasn't expired
4. Regenerate token if needed

### Error: "403 Forbidden"

1. Verify account has permission to upload
2. Check project name is available
3. Ensure token scope includes the project

### Dependencies Not Found

TestPyPI doesn't mirror production PyPI. When installing, always use:
```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    nlp2mcp
```

The `--extra-index-url` allows pip to fetch dependencies (lark, numpy, click) from production PyPI.

## GitHub Actions Integration

### Setup Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `TEST_PYPI_API_TOKEN`
4. Value: Your TestPyPI API token
5. Click "Add secret"

### Trigger Workflow

```bash
# Manual trigger via GitHub UI
# Actions → Publish to PyPI → Run workflow
# Select: target = testpypi

# Or use GitHub CLI
gh workflow run publish-pypi.yml -f target=testpypi
```

## Version History on TestPyPI

TestPyPI allows testing multiple versions:

- `0.5.0b0` - Initial beta release (Sprint 5 Day 8)
- `0.5.0rc1` - Release candidate (if needed)
- `0.5.0` - Final release (Sprint 5 Day 9)

**Note**: TestPyPI periodically deletes old files to conserve space. Don't rely on it for long-term storage.

## Next Steps

After successful TestPyPI validation:

1. Document any installation issues
2. Test on multiple platforms (Linux, macOS, Windows)
3. Verify CLI works in fresh environments
4. Review package metadata on TestPyPI web interface
5. Prepare for production PyPI release

## References

- [TestPyPI Homepage](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PyPA Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)
