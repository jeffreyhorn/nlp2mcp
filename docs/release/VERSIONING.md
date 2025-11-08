# Versioning Strategy

## Overview

This project follows [Semantic Versioning 2.0.0](https://semver.org/) for version numbering.

## Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

### Version Components

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible new functionality
- **PATCH**: Backwards-compatible bug fixes
- **PRERELEASE** (optional): alpha, beta, rc.N
- **BUILD** (optional): Build metadata

## Version Evolution

### Current State (Sprint 5)

- **Current Version**: `0.1.0` (initial package version from Day 7)
- **Development Status**: Beta (as declared in pyproject.toml)

### Planned Version Path

#### Phase 1: Sprint 5 Completion (Priority 1-4)
```
0.1.0 → 0.5.0-beta
```
- **Trigger**: Completion of Days 1-8 (hardening, packaging, automation)
- **Justification**: 
  - 0.5.x signals "halfway to 1.0"
  - Beta prerelease tag matches pyproject.toml Development Status
  - TestPyPI publication for validation

#### Phase 2: Documentation & Polish (Priority 5)
```
0.5.0-beta → 0.5.0
```
- **Trigger**: Completion of Day 9 (documentation)
- **Justification**:
  - Remove beta tag after full documentation
  - Still pre-1.0 allows for API refinement based on user feedback

#### Phase 3: Production Release
```
0.5.0 → 1.0.0
```
- **Trigger**: 
  - User validation complete
  - No critical bugs
  - API stable
  - Documentation comprehensive
  - Performance validated
- **Justification**:
  - 1.0.0 declares production-ready
  - Commits to API stability
  - Signals confidence to users

## Version Bump Rules

### MAJOR (X.0.0)

Increment when making incompatible API changes:
- Removing or renaming public functions/classes
- Changing function signatures (parameters, return types)
- Modifying CLI interface (removing flags, changing behavior)
- Changing output format in breaking ways

**Reset**: MINOR and PATCH to 0

### MINOR (0.X.0)

Increment when adding backwards-compatible functionality:
- New CLI flags or options
- New API functions/methods
- New features (e.g., new constraint types support)
- Performance improvements (non-breaking)

**Reset**: PATCH to 0

### PATCH (0.0.X)

Increment for backwards-compatible bug fixes:
- Bug fixes that don't change API
- Documentation corrections
- Internal refactoring (no public API changes)
- Dependency updates (no breaking changes)

## Pre-release Versions

### Alpha (`-alpha` or `-alpha.N`)
- Early development
- API unstable
- For internal testing only
- **Not used in this project** (already past this stage)

### Beta (`-beta` or `-beta.N`)
- Feature complete
- API mostly stable
- External testing encouraged
- **Current phase** for Sprint 5

### Release Candidate (`-rc.N`)
- Final testing before release
- No new features
- Bug fixes only
- **Future use** before 1.0.0

## Practical Examples

### Sprint 5 Progress

```
0.1.0         # Day 7: Initial package with basic PyPI metadata
0.5.0-beta    # Day 8: TestPyPI release with automation
0.5.0         # Day 9: Full documentation, remove beta tag
1.0.0         # Post-Sprint 5: Production release after validation
```

### Post-1.0 Examples

```
1.0.0 → 1.0.1  # Bug fix in gradient computation
1.0.1 → 1.1.0  # Add support for new GAMS function (e.g., arctan2)
1.1.0 → 2.0.0  # Change CLI interface (remove deprecated flags)
```

## Version Bumping Process

### Manual Process (Current)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with version and date
3. Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push tag: `git push origin vX.Y.Z`

### Automated Process (Task 8.2)

```bash
# Bump version automatically
python scripts/bump_version.py [major|minor|patch|beta|rc]

# Examples:
python scripts/bump_version.py patch   # 0.5.0 → 0.5.1
python scripts/bump_version.py minor   # 0.5.0 → 0.6.0
python scripts/bump_version.py major   # 0.5.0 → 1.0.0
python scripts/bump_version.py beta    # 0.5.0 → 0.6.0-beta
```

## Integration with PyPI

### TestPyPI (Pre-release testing)
- All pre-release versions (e.g., `0.5.0-beta`)
- RC candidates before production release
- Allows testing installation without affecting production PyPI

### Production PyPI
- Stable releases only (no pre-release tags)
- Starting with `0.5.0` or `1.0.0`
- Only push after full validation

## Versioning in Code

### Reading Current Version

```python
# From pyproject.toml (authoritative source)
import tomli

with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)
    version = pyproject["project"]["version"]
```

### Version in CLI

The `--version` flag (to be implemented) should show:
```bash
$ nlp2mcp --version
nlp2mcp 0.5.0-beta
```

## Decision Log

### Unknown 4.4 Resolution (2025-11-08)

**Decision**: Use version path `0.1.0 → 0.5.0-beta → 0.5.0 → 1.0.0`

**Rationale**:
1. **0.5.x signals progress**: Midpoint between initial development and 1.0 release
2. **Beta tag for TestPyPI**: Matches Development Status classifier, signals testing phase
3. **Remove beta for production**: Clean version number after documentation complete
4. **1.0.0 after validation**: Only declare production-ready after user feedback

**Alternatives Considered**:
- ~~0.1.0 → 1.0.0 directly~~: Too aggressive, skips validation phase
- ~~0.4.0 → 0.5.0~~: Confusing (Sprint 4 was a different project phase)
- ~~Stay at 0.1.x~~: Doesn't signal significant progress made in Sprint 5

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [PEP 440 – Version Identification](https://peps.python.org/pep-0440/)
- [Python Packaging User Guide - Version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)
