# CI Workflow Testing Guide

This guide documents best practices for testing GitHub Actions workflows locally before pushing changes to the repository.

## Overview

Our CI pipeline consists of 5 workflows:
- `ci.yml` - Main test suite
- `lint.yml` - Code quality checks
- `performance-check.yml` - Performance budget enforcement
- `gamslib-regression.yml` - Parse rate regression detection
- `publish-pypi.yml` - Package publishing

## Local Validation Tools

### 1. Syntax Validation with yamllint

Validate YAML syntax before committing:

```bash
# Install yamllint
pip install yamllint

# Validate a specific workflow
yamllint .github/workflows/ci.yml

# Validate all workflows
yamllint .github/workflows/
```

Configuration (`.yamllint.yml`):
```yaml
extends: default
rules:
  line-length:
    max: 120
  truthy:
    allowed-values: ['true', 'false', 'on']
```

### 2. Workflow Validation with actionlint

[actionlint](https://github.com/rhysd/actionlint) provides comprehensive GitHub Actions validation:

```bash
# Install actionlint (macOS)
brew install actionlint

# Install actionlint (Linux)
go install github.com/rhysd/actionlint/cmd/actionlint@latest

# Validate all workflows
actionlint

# Validate a specific workflow
actionlint .github/workflows/ci.yml
```

**Common issues actionlint catches:**
- Invalid action references
- Incorrect input names
- Missing required permissions
- Shell script errors
- Expression syntax errors

### 3. Local Workflow Execution with act

[act](https://github.com/nektos/act) runs GitHub Actions locally using Docker:

```bash
# Install act (macOS)
brew install act

# List available jobs
act -l

# Run a specific job
act -j test

# Run with specific event
act push

# Dry run (validate without executing)
act -n
```

**Limitations:**
- Some GitHub-specific contexts unavailable locally
- Secrets must be provided via `.secrets` file or flags
- Large images can be slow to download

## Validation Checklist

Before pushing workflow changes, verify:

### File Path Verification

```bash
# Check that all referenced paths exist
for file in $(grep -oP "(?<=path: )[^\s]+" .github/workflows/*.yml); do
    [ -e "$file" ] || echo "Missing: $file"
done
```

### Action Version Verification

```bash
# List all action references
grep -E "uses: " .github/workflows/*.yml | sort -u

# Check for deprecated actions
# Current recommended versions:
# - actions/checkout@v4
# - actions/setup-python@v5
# - actions/upload-artifact@v4
# - actions/download-artifact@v4
```

### Matrix Build Testing

For matrix builds, verify all combinations work:

```yaml
# Example matrix
strategy:
  matrix:
    python-version: ['3.11', '3.12']
    os: [ubuntu-latest, macos-latest]
```

Test each combination locally:
```bash
# Test with Python 3.11
python3.11 -m pytest tests/

# Test with Python 3.12
python3.12 -m pytest tests/
```

### Permission Checks

Workflows with specific permission requirements:

| Workflow | Permissions | Notes |
|----------|-------------|-------|
| `ci.yml` | `contents: read` | Default for most jobs |
| `publish-pypi.yml` | `id-token: write` | OIDC for PyPI trusted publishing |
| `gamslib-regression.yml` | `pull-requests: write` | PR comments |

### Secrets Verification

Required secrets (Settings > Secrets and variables > Actions):

| Secret | Used By | Purpose |
|--------|---------|---------|
| `PYPI_API_TOKEN` | `publish-pypi.yml` | PyPI publishing (optional with OIDC) |

## Common Pitfalls

### 1. Cache Key Mismatches

```yaml
# Bad: Cache key doesn't include dependencies hash
- uses: actions/cache@v4
  with:
    key: pip-cache

# Good: Include hash of requirements
- uses: actions/cache@v4
  with:
    key: pip-${{ hashFiles('**/requirements*.txt') }}
```

### 2. Missing Checkout for Local Scripts

```yaml
# Bad: Script runs before checkout
- run: python scripts/check.py

# Good: Checkout first
- uses: actions/checkout@v4
- run: python scripts/check.py
```

### 3. Incorrect Working Directory

```yaml
# Bad: Assumes root directory
- run: cd src && python test.py

# Good: Use working-directory
- run: python test.py
  working-directory: src
```

### 4. Shell Script Errors

```yaml
# Bad: Missing error handling
- run: |
    rm important_file
    cp new_file important_file

# Good: Use strict mode
- run: |
    set -euo pipefail
    rm important_file
    cp new_file important_file
```

### 5. Artifact Upload Patterns

```yaml
# Bad: Pattern doesn't match anything
- uses: actions/upload-artifact@v4
  with:
    path: reports/*.xml

# Good: Verify pattern matches files first
- run: ls -la reports/
- uses: actions/upload-artifact@v4
  with:
    path: reports/*.xml
    if-no-files-found: warn
```

## Sprint 11 Lessons Learned

Issues encountered and solutions:

### 1. Matrix Build Failures

**Problem:** CI passed on Ubuntu but failed on macOS due to path differences.

**Solution:** Use `Path` from `pathlib` for cross-platform compatibility.

### 2. Performance Regression

**Problem:** Test time increased from 17s to 30s+ after adding fixtures.

**Solution:** Marked slow tests with `@pytest.mark.slow` and excluded from fast CI.

### 3. Artifact Retention

**Problem:** Artifacts expired before debugging could complete.

**Solution:** Set explicit retention:
```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 90
```

## Make Targets

Integration with project Makefile:

```bash
# Validate all workflows
make validate-workflows

# Run actionlint (requires actionlint installed)
make actionlint
```

Add to Makefile:
```makefile
.PHONY: validate-workflows actionlint

validate-workflows:
	@echo "Validating GitHub Actions workflows..."
	@yamllint .github/workflows/ || true
	@actionlint || true

actionlint:
	@command -v actionlint >/dev/null 2>&1 || { echo "actionlint not installed. Run: brew install actionlint"; exit 1; }
	@actionlint
```

## Quick Reference

### Workflow Testing Sequence

1. **Syntax check:** `yamllint .github/workflows/`
2. **Action validation:** `actionlint`
3. **Local execution:** `act -n` (dry run)
4. **Path verification:** Check all referenced files exist
5. **Matrix testing:** Test each combination locally

### Emergency Rollback

If a workflow change breaks CI:

```bash
# Revert the workflow file
git checkout HEAD~1 -- .github/workflows/ci.yml

# Or revert the entire commit
git revert HEAD
```

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [actionlint Documentation](https://github.com/rhysd/actionlint)
- [act Documentation](https://github.com/nektos/act)
- Project workflows: `.github/workflows/`
