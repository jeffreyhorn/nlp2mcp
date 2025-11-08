# Release Process

This document describes the release process for nlp2mcp.

## Overview

nlp2mcp uses semantic versioning and publishes to PyPI. Releases are automated via GitHub Actions with manual approval steps.

## Release Types

- **Beta Release** (`X.Y.Z-beta`): Pre-release for testing (TestPyPI)
- **Release Candidate** (`X.Y.Z-rc.N`): Final testing before production (TestPyPI)
- **Production Release** (`X.Y.Z`): Official PyPI release

## Prerequisites

- [ ] All tests passing on main branch
- [ ] Documentation up to date
- [ ] CHANGELOG.md updated with release notes
- [ ] Version bumped in pyproject.toml
- [ ] No open blocker issues

## Release Checklist

### 1. Pre-Release Validation

```bash
# Ensure on main branch
git checkout main
git pull origin main

# Run full test suite
make typecheck
make lint
make format
make test

# Verify all tests pass
pytest tests/ -v

# Build locally and verify
python -m build
twine check dist/*
```

### 2. Version Bump

Choose appropriate version bump:

```bash
# For bug fixes
python scripts/bump_version.py patch  # 0.5.0 → 0.5.1

# For new features (backward compatible)
python scripts/bump_version.py minor  # 0.5.0 → 0.6.0

# For breaking changes
python scripts/bump_version.py major  # 0.5.0 → 1.0.0

# For beta releases
python scripts/bump_version.py beta   # 0.5.0 → 0.6.0-beta

# For release candidates
python scripts/bump_version.py rc     # 0.5.0-beta → 0.5.0-rc.1
```

Review the change:
```bash
git diff pyproject.toml
```

### 3. Update Changelog

Generate changelog entry:

```bash
# Get commit range
LAST_TAG=$(git describe --tags --abbrev=0)
NEW_VERSION="0.5.0"  # Replace with actual version

# Generate changelog
python scripts/generate_changelog.py --since $LAST_TAG --version $NEW_VERSION

# Review and edit
vim CHANGELOG.md
```

Manually refine the generated changelog:
- Add summary paragraph
- Reorganize items for clarity
- Add any missing details
- Fix formatting

### 4. Commit and Tag

```bash
# Commit version bump and changelog
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to $NEW_VERSION"

# Create annotated tag
git tag -a v$NEW_VERSION -m "Release v$NEW_VERSION"

# Push to GitHub
git push origin main
git push origin v$NEW_VERSION
```

### 5. TestPyPI Release (Beta/RC only)

For beta and release candidate versions, publish to TestPyPI first:

```bash
# Ensure you have TestPyPI credentials configured
# See docs/release/TESTPYPI_PUBLISH.md for setup

# Build distribution
rm -rf dist/ build/ src/*.egg-info
python -m build

# Verify
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

Or use GitHub Actions:

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select `target: testpypi`
4. Click "Run workflow"

### 6. TestPyPI Validation

```bash
# Create fresh test environment
python -m venv /tmp/test_release
source /tmp/test_release/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    nlp2mcp==$NEW_VERSION

# Verify CLI works
nlp2mcp --help

# Test with example file
nlp2mcp examples/scalar_nlp.gms -o /tmp/test_output.gms

# Check output
head -50 /tmp/test_output.gms

# Cleanup
deactivate
rm -rf /tmp/test_release
```

### 7. Production PyPI Release

**Only after TestPyPI validation succeeds:**

#### Option A: GitHub Release (Recommended)

1. Go to https://github.com/jeffreyhorn/nlp2mcp/releases
2. Click "Draft a new release"
3. Choose tag: `v$NEW_VERSION`
4. Release title: `nlp2mcp $NEW_VERSION`
5. Copy changelog entry into description
6. Check "Set as a pre-release" if beta/rc
7. Click "Publish release"

GitHub Actions will automatically publish to PyPI when a release is published.

#### Option B: Manual Upload

```bash
# Ensure you have PyPI credentials configured

# Build distribution
rm -rf dist/ build/ src/*.egg-info
python -m build

# Final verification
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

### 8. Post-Release Validation

```bash
# Wait 60 seconds for PyPI indexing
sleep 60

# Test installation from PyPI
python -m venv /tmp/test_pypi
source /tmp/test_pypi/bin/activate

# Install from production PyPI
pip install nlp2mcp==$NEW_VERSION

# Verify
nlp2mcp --help
nlp2mcp examples/scalar_nlp.gms -o /tmp/test.gms

# Cleanup
deactivate
rm -rf /tmp/test_pypi
```

### 9. Update Documentation

- [ ] Verify PyPI page looks correct: https://pypi.org/project/nlp2mcp/
- [ ] Update README.md if needed (installation instructions, badges)
- [ ] Announce release (if appropriate)

## Rollback Procedure

If a release has critical issues:

### For Pre-releases (TestPyPI)

1. Do not promote to production
2. Fix issues
3. Release new RC version

### For Production Releases

**PyPI does not allow deleting or replacing releases.** Instead:

1. Document the issue immediately
2. Release a patch version with the fix
3. Update CHANGELOG.md with the issue and fix
4. Consider yanking the release on PyPI (makes it unavailable for new installs):
   ```bash
   # This requires PyPI web interface or API
   ```

## Version History

| Version | Date | Type | Notes |
|---------|------|------|-------|
| 0.1.0 | 2025-11-08 | Initial | Day 7: Package configured |
| 0.5.0-beta | 2025-11-08 | Beta | Day 8: TestPyPI release |
| 0.5.0 | TBD | Production | Day 9: Full documentation |
| 1.0.0 | TBD | Production | Post-validation |

## Emergency Contacts

- PyPI Support: https://pypi.org/help/
- TestPyPI Support: https://test.pypi.org/help/
- GitHub Actions: Check workflow logs in repository

## Automation Details

### GitHub Actions Workflow

See `.github/workflows/publish-pypi.yml`:

- **Trigger**: Release published or manual workflow dispatch
- **Steps**:
  1. Checkout code
  2. Set up Python
  3. Install dependencies
  4. Run tests
  5. Run linters
  6. Build distributions
  7. Verify with twine
  8. Publish to PyPI (production) or TestPyPI
  9. Verify installation

### Secrets Required

- `PYPI_API_TOKEN`: Production PyPI API token
- `TEST_PYPI_API_TOKEN`: TestPyPI API token

Setup:
1. Generate tokens on PyPI/TestPyPI
2. Add to GitHub repository secrets
3. Tokens are automatically used by publish workflow

## Troubleshooting

### Build Fails

```bash
# Clean everything
rm -rf dist/ build/ src/*.egg-info .venv

# Recreate virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt

# Try build again
python -m build
```

### Tests Fail

Do not release until all tests pass. Fix issues first.

### Upload Fails

Check:
- API token is correct and not expired
- Network connectivity
- PyPI status: https://status.python.org/

### Version Already Exists

You cannot re-upload the same version. Options:
1. Bump to next patch version
2. Use post-release version (e.g., `0.5.0.post1`)

## References

- [Semantic Versioning](https://semver.org/)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Twine Documentation](https://twine.readthedocs.io/)
