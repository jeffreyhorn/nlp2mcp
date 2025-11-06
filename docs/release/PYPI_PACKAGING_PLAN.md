# PyPI Packaging Plan for nlp2mcp

**Author:** Jeffrey Horn  
**Date:** 2025-11-06  
**Sprint:** Sprint 5 Prep Task 5  
**Purpose:** Survey PyPI packaging best practices and plan Sprint 5 Priority 4 implementation

---

## Executive Summary

This document provides a comprehensive analysis of Python packaging best practices for 2025 and defines the implementation plan for publishing nlp2mcp to PyPI. Based on research and testing, we recommend:

1. **Keep setuptools** as the build backend (stable, PyPA-supported, adequate for pure Python)
2. **Fix license format** to use SPDX expression (required by 2026-Feb-18)
3. **Add optional-dependencies** groups for better dependency organization
4. **Use GitHub Actions OIDC** trusted publisher for secure, tokenless publishing
5. **Avoid upper bounds** on library dependencies except for known incompatibilities

The current build system works successfully, but requires updates to license metadata to comply with modern standards before the February 2026 deprecation deadline.

---

## 1. Current Build System Status

### 1.1 Test Results (Step 1)

**Date Tested:** 2025-11-06  
**Build Tool:** `python -m build` (build 1.3.0)  
**Result:** ✅ SUCCESS

**Artifacts Created:**
- `nlp2mcp-0.1.0-py3-none-any.whl` (121 KB)
- `nlp2mcp-0.1.0.tar.gz` (105 KB)

**Build Configuration:**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

### 1.2 Issues Identified

#### Critical: License Format Deprecation

**Warning Message:**
```
SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated

Please use a simple string containing a SPDX expression for `project.license`. 
You can also use `project.license-files`. (Both options available on setuptools>=77.0.0).

By 2026-Feb-18, you need to update your project and remove deprecated calls
or your builds will no longer be supported.
```

**Current Configuration (Deprecated):**
```toml
[project]
license = {text = "MIT"}
classifiers = [
    # ...
    "License :: OSI Approved :: MIT License",
    # ...
]
```

**Required Fix:**
```toml
[project]
license = "MIT"
license-files = ["LICENSE"]
# Remove "License :: OSI Approved :: MIT License" classifier
```

**Timeline:** Must be fixed before 2026-Feb-18 (setuptools will stop supporting old format)

**Priority:** HIGH - Include in Sprint 5 Priority 4 implementation

---

## 2. Build Backend Research (Step 2)

### 2.1 Market Share Analysis (2025)

Based on analysis of PyPI packages in 2025:

| Backend | Market Share | Maintainer | Status |
|---------|--------------|------------|--------|
| setuptools | 79.0% | PyPA | Dominant, stable |
| Poetry (poetry-core) | 8.4% | Poetry project | Popular alternative |
| Hatchling | 6.5% | PyPA | Growing, modern |
| Flit | 3.8% | Community | Lightweight |
| PDM (pdm-backend) | ~2.0% | PDM project | Feature-rich |
| Others (including uv_build) | ~0.5% | Various | Emerging |

### 2.2 Backend Comparison

#### setuptools

**Pros:**
- Battle-tested with 79% market share
- PyPA-maintained (Python Packaging Authority)
- Excellent compatibility and ecosystem support
- Handles complex builds including C extensions
- Well-documented edge cases
- Stable API with predictable behavior

**Cons:**
- Requires more configuration knowledge than modern alternatives
- Default file inclusion less intuitive than competitors
- Source distributions not reproducible by default
- Some deprecated features (like our license format issue)

**Best For:** Mature projects, complex builds, maximum compatibility

#### Hatchling

**Pros:**
- PyPA-maintained (official backing)
- Default recommendation in Python Packaging User Guide
- Reproducible builds by default (wheels and sdist)
- Simpler configuration with better defaults
- Uses Git .gitignore for default exclusions
- Better editable install behavior for IDEs
- Modern, extensible plugin system
- Supports build hooks and VCS-based versioning (hatch-vcs)

**Cons:**
- Smaller ecosystem than setuptools (~6.5% market share)
- Not recommended for C extension builds
- Fewer answered StackOverflow questions
- Migration requires testing

**Best For:** New pure-Python projects, teams wanting modern defaults

#### Poetry (poetry-core)

**Pros:**
- Most popular alternative (8.4% market share)
- Excellent documentation
- Integrated project management tool
- Strong community support
- Good for end-to-end Poetry workflows

**Cons:**
- **Adds upper bounds to dependencies by default** (major issue for libraries)
- C/C++ extension support is undocumented
- Tightly coupled to Poetry ecosystem
- May conflict with other tools in workflow

**Best For:** Projects using Poetry for development, applications (not libraries)

#### PDM (pdm-backend)

**Pros:**
- Supports dependency locking
- Can integrate with other backends (meson-python, etc.)
- Good for complex builds beyond pure Python
- Modern PEP compliance

**Cons:**
- Smaller market share (~2%)
- Less mature ecosystem
- More complex setup

**Best For:** Complex builds, projects needing dependency locking at build time

#### uv_build (Emerging 2025)

**Pros:**
- Zero-config for simple projects
- Very fast build times
- Tight integration with uv tool
- Modern design

**Cons:**
- Very new (emerging in 2025)
- Limited track record
- Small ecosystem
- Documentation still evolving

**Best For:** New projects fully committed to uv ecosystem

### 2.3 Recommendation for nlp2mcp

**Decision: KEEP setuptools**

**Rationale:**

1. **Current Status:** Our build already works with setuptools
2. **Stability:** 79% market share provides proven stability
3. **PyPA Support:** Officially maintained by Python Packaging Authority
4. **Pure Python:** Our project doesn't need advanced features of alternatives
5. **Risk vs Reward:** Migration effort doesn't justify benefits for our use case
6. **Future Flexibility:** setuptools handles future needs (C extensions, complex builds)
7. **Known Issues:** License format fix is straightforward (single line change)

**Alternative Consideration:** Hatchling would be the natural choice if we were starting fresh, but migration isn't justified for an already-working setup.

**Action Items:**
- Fix license format deprecation (required)
- Update setuptools requirement to >=77.0.0 (enables SPDX format)
- Monitor Hatchling maturity for potential future migration

---

## 3. Dependency Management Analysis (Step 3)

### 3.1 Current Dependencies

**Runtime Dependencies:**
```toml
dependencies = [
    "lark>=1.1.9",
    "numpy>=1.24.0",
    "click>=8.0.0",
    "tomli>=2.0.0; python_version<'3.11'",
]
```

**Development Dependencies:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

### 3.2 Upper Bounds Best Practice (2025)

**General Guidance:**

- **Libraries (like nlp2mcp):** Avoid upper bounds except for known incompatibilities
- **Applications:** Use exact pinning or lock files (requirements.txt, poetry.lock)
- **Reasoning:** Upper bounds in libraries cause dependency conflicts when multiple packages are installed together

**Current Assessment:** ✅ Our dependencies correctly use lower bounds only

**Exception Cases:** Upper bounds are justified when:
- Breaking changes are guaranteed (e.g., `package>=2.0,<3.0` during major API rewrites)
- Known incompatibilities exist
- Security vulnerabilities in specific versions

### 3.3 Dependency Organization

**Current Issue:** All dev tools in single `dev` group

**Best Practice for 2025:** Separate optional-dependencies groups

**Recommended Structure:**
```toml
[project.optional-dependencies]
# Testing dependencies
test = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
]

# Development tools
dev = [
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

# Documentation (if we add docs)
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
]

# Convenience: all development dependencies
all = [
    "nlp2mcp[test,dev,docs]",
]
```

**Benefits:**
- Users can install only what they need: `pip install nlp2mcp[test]`
- CI can install minimal dependencies for faster builds
- Clear separation of concerns
- Standard practice in mature Python projects

### 3.4 Python Version Constraint

**Current:** `requires-python = ">=3.12"`

**Assessment:** ✅ Appropriate - specifies minimum without unnecessary upper bound

**Rationale:** Python 3.12 is our development version, and we haven't tested on earlier versions

### 3.5 Conditional Dependencies

**Current:** `tomli>=2.0.0; python_version<'3.11'`

**Assessment:** ✅ Correct, but effectively unused since we require Python 3.12+

**Recommendation:** Keep for now (harmless), but could remove if we're certain about 3.12+ requirement

### 3.6 Recommendations

**Action Items:**
1. ✅ **Keep current lower-bound-only strategy** - aligns with 2025 best practices
2. 📝 **Split optional-dependencies** into test/dev/docs groups (optional, nice-to-have)
3. 📝 **Consider removing tomli** dependency since Python 3.12+ has built-in TOML support
4. ✅ **No lock files needed** - we're a library, not an application

**Priority:** Medium - current setup is functional, proposed changes are organizational improvements

---

## 4. PyPI Publishing Workflow (Step 4)

### 4.1 Modern Publishing: Trusted Publishers (OIDC)

**What is Trusted Publishing?**

Trusted Publishing uses OpenID Connect (OIDC) to authenticate GitHub Actions with PyPI without manual API tokens. GitHub's OIDC identity provider issues short-lived tokens that PyPI validates based on pre-configured trust relationships.

**Benefits:**

1. **Security:** No long-lived API tokens to manage or leak
2. **Simplicity:** No secrets to configure in GitHub repository settings
3. **Auditability:** PyPI logs include GitHub workflow context (repo, workflow, commit)
4. **2025 Standard:** Recommended by PyPI as the modern approach
5. **Automatic Attestations:** Digital signatures for all distribution files (Sigstore)

### 4.2 Publishing Workflow Architecture

**Components:**

1. **PyPI Trusted Publisher Configuration** (one-time setup on PyPI website)
2. **GitHub Actions Workflow** (YAML file in `.github/workflows/`)
3. **PyPA publish action** (`pypa/gh-action-pypi-publish@release/v1`)
4. **Build artifacts** (wheel and sdist from `python -m build`)

### 4.3 Setup Process

#### A. For New Packages (Pending Publishers)

Since nlp2mcp hasn't been published to PyPI yet, we'll use **pending publishers**:

1. Go to PyPI: https://pypi.org/manage/account/publishing/
2. Add pending publisher with:
   - **PyPI Project Name:** `nlp2mcp`
   - **Owner:** `jeffreyhorn` (or organization name)
   - **Repository:** `nlp2mcp`
   - **Workflow:** `publish.yml`
   - **Environment:** `release` (optional but recommended)

3. First successful publish will claim the package name

#### B. For Existing Packages

If package already exists on PyPI:

1. Go to: https://pypi.org/manage/project/nlp2mcp/settings/publishing/
2. Add trusted publisher with same configuration as above

### 4.4 GitHub Actions Workflow Template

**File:** `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]
  # Optional: manual trigger for testing
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: release
      url: https://pypi.org/project/nlp2mcp/
    permissions:
      id-token: write  # REQUIRED for OIDC
      contents: read
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No with: parameters needed - OIDC handles authentication!
```

**Key Elements:**

1. **Trigger:** `on: release: types: [published]` - publishes when GitHub release is created
2. **Two Jobs:** 
   - `build`: Creates wheel and sdist
   - `publish`: Uploads to PyPI (depends on build)
3. **OIDC Permission:** `permissions: id-token: write` - REQUIRED for trusted publishing
4. **Environment:** `environment: release` - optional but provides environment protection rules
5. **No Secrets:** No API tokens, usernames, or passwords needed!

### 4.5 Attestations (Automatic in 2025)

**What are Attestations?**

Digital signatures for distribution files, automatically generated using Sigstore. They prove:
- Which GitHub workflow built the package
- Which commit/ref was used
- When it was built
- The integrity of the files

**Status:** Enabled by default for all projects using Trusted Publishing as of 2025

**Verification:** Users can verify attestations with:
```bash
pip install sigstore
sigstore verify identity <wheel-file> \
  --cert-identity https://github.com/jeffreyhorn/nlp2mcp/.github/workflows/publish.yml@refs/tags/v0.1.0 \
  --cert-oidc-issuer https://token.actions.githubusercontent.com
```

### 4.6 Testing Strategy

**TestPyPI (Recommended First Step):**

1. Configure separate trusted publisher for TestPyPI: https://test.pypi.org/manage/account/publishing/
2. Use test workflow: `.github/workflows/test-publish.yml`
3. Publish action configuration:
   ```yaml
   - name: Publish to TestPyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       repository-url: https://test.pypi.org/legacy/
   ```
4. Verify installation: `pip install --index-url https://test.pypi.org/simple/ nlp2mcp`

**Workflow:**
1. Test on TestPyPI first (Sprint 5 Day 7)
2. Verify installation and functionality
3. Publish to production PyPI (Sprint 5 Day 8)

### 4.7 Alternative: API Token Method (Not Recommended)

**Legacy Approach:**
- Generate API token at https://pypi.org/manage/account/token/
- Store as `PYPI_API_TOKEN` in GitHub repository secrets
- Add to workflow: `with: password: ${{ secrets.PYPI_API_TOKEN }}`

**Why Not Recommended:**
- Less secure (long-lived token)
- Manual secret management
- No audit trail with GitHub context
- No automatic attestations
- Against PyPI 2025 recommendations

### 4.8 Recommendations

**For Sprint 5 Priority 4 (Days 7-8):**

1. ✅ **Use Trusted Publishers (OIDC)** - modern, secure, simple
2. ✅ **Test on TestPyPI first** - verify workflow before production
3. ✅ **Use environment protection** - add "release" environment with required reviewers
4. ✅ **Trigger on GitHub releases** - clean, auditable versioning
5. ✅ **Separate build and publish jobs** - clearer workflow, reusable artifacts

**Action Items:**
- Create `.github/workflows/publish.yml` (see template above)
- Create `.github/workflows/test-publish.yml` (TestPyPI variant)
- Configure pending publisher on PyPI
- Configure trusted publisher on TestPyPI
- Add "release" environment in GitHub settings (optional)
- Document release process in `docs/release/RELEASE_PROCESS.md`

---

## 5. Sprint 5 Priority 4 Implementation Plan

### 5.1 Prerequisites (Must Complete First)

- ✅ Survey completed (this document)
- ⏳ License format fixed (see Section 6.1)
- ⏳ Quality checks passing (typecheck, lint, format, test)
- ⏳ VERSION file or version strategy defined

### 5.2 Day 7: TestPyPI Setup and Testing

**Duration:** 3-4 hours

**Tasks:**

1. **Fix License Format** (30 min)
   - Update `pyproject.toml`: `license = "MIT"`
   - Add `license-files = ["LICENSE"]`
   - Remove license classifier from `classifiers` list
   - Update setuptools requirement: `setuptools>=77.0.0`
   - Run build test: `python -m build`
   - Verify no deprecation warnings

2. **Enhance Dependency Organization** (30 min, optional)
   - Split `optional-dependencies` into test/dev/docs groups
   - Update documentation and CI scripts if needed
   - Test installation: `pip install -e .[test,dev]`

3. **Create Publishing Workflows** (1 hour)
   - Create `.github/workflows/test-publish.yml`
   - Create `.github/workflows/publish.yml`
   - Add environment protection for "release" (GitHub Settings)
   - Document workflow in `docs/release/RELEASE_PROCESS.md`

4. **Configure TestPyPI Trusted Publisher** (15 min)
   - Go to https://test.pypi.org/manage/account/publishing/
   - Add pending publisher for nlp2mcp
   - Specify repo, workflow, and environment

5. **Test Publish to TestPyPI** (1 hour)
   - Create test tag: `git tag v0.1.0-test && git push origin v0.1.0-test`
   - Trigger test-publish workflow
   - Verify workflow succeeds
   - Install from TestPyPI: `pip install --index-url https://test.pypi.org/simple/ nlp2mcp`
   - Test CLI: `nlp2mcp --version` and basic functionality
   - Verify attestations are created

6. **Quality Checks and Documentation** (30 min)
   - Run: `make typecheck && make lint && make format && make test`
   - Update CHANGELOG.md with TestPyPI test results
   - Document any issues found

### 5.3 Day 8: Production PyPI Release

**Duration:** 2-3 hours

**Tasks:**

1. **Configure Production PyPI Trusted Publisher** (15 min)
   - Go to https://pypi.org/manage/account/publishing/
   - Add pending publisher for nlp2mcp
   - Use same configuration as TestPyPI

2. **Final Pre-Release Checks** (30 min)
   - Verify all tests pass: `make test`
   - Verify clean build: `rm -rf dist/ && python -m build`
   - Check no deprecation warnings
   - Review CHANGELOG.md
   - Review README.md (will be displayed on PyPI)

3. **Create GitHub Release** (1 hour)
   - Finalize version number (e.g., v0.1.0)
   - Update CHANGELOG.md with release notes
   - Commit version updates
   - Create Git tag: `git tag v0.1.0`
   - Push tag: `git push origin v0.1.0`
   - Create GitHub Release at https://github.com/jeffreyhorn/nlp2mcp/releases/new
   - Write release notes (features, fixes, known issues)
   - Publish release (triggers publish.yml workflow)

4. **Monitor and Verify** (30 min)
   - Watch GitHub Actions workflow
   - Verify publish job succeeds
   - Check PyPI page: https://pypi.org/project/nlp2mcp/
   - Verify metadata displays correctly (description, links, classifiers)
   - Verify attestations are present
   - Test installation: `pip install nlp2mcp`
   - Test CLI functionality

5. **Post-Release Tasks** (30 min)
   - Announce release (if applicable)
   - Update documentation with installation instructions
   - Create post-release tag (e.g., v0.1.1-dev) for continued development
   - Update PREP_PLAN.md: check off Priority 4 completion

### 5.4 Acceptance Criteria

From PREP_PLAN.md Task 5:

- ✅ Current build system tested (works, issues documented)
- ✅ Build backend options researched and decision documented
- ✅ Dependency management strategy defined
- ✅ Publishing workflow researched
- ✅ Sprint 5 implementation plan created
- ✅ All 4 Category 4 unknowns addressed
- ✅ PYPI_PACKAGING_PLAN.md created (this document)

**Additional Priority 4 Criteria (Days 7-8):**

- ⏳ License format fixed (SPDX expression)
- ⏳ TestPyPI publish successful
- ⏳ Production PyPI publish successful
- ⏳ Package installable via `pip install nlp2mcp`
- ⏳ CLI functional after PyPI installation
- ⏳ Attestations verified
- ⏳ Documentation updated

---

## 6. Detailed Action Items

### 6.1 Immediate: Fix License Format

**File:** `pyproject.toml`

**Current (lines ~18-28):**
```toml
license = {text = "MIT"}
authors = [
    {name = "Jeffrey Horn", email = "jeffreydhorn@gmail.com"}
]
keywords = ["optimization", "nlp", "mcp", "gams", "kkt"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",  # <-- REMOVE THIS
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Mathematics",
]
```

**Required Changes:**

1. Replace `license = {text = "MIT"}` with `license = "MIT"`
2. Add `license-files = ["LICENSE"]` after license line
3. Remove `"License :: OSI Approved :: MIT License"` from classifiers
4. Update setuptools requirement: `requires = ["setuptools>=77.0.0", "wheel"]`

**Updated (correct format):**
```toml
[project]
name = "nlp2mcp"
version = "0.1.0"
description = "Convert GAMS NLP models to MCP via KKT conditions"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE"]
authors = [
    {name = "Jeffrey Horn", email = "jeffreydhorn@gmail.com"}
]
keywords = ["optimization", "nlp", "mcp", "gams", "kkt"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    # License classifier removed (deprecated in favor of SPDX expression)
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Mathematics",
]
```

**And in build-system section:**
```toml
[build-system]
requires = ["setuptools>=77.0.0", "wheel"]
build-backend = "setuptools.build_meta"
```

**Verification:**
```bash
rm -rf dist/
.venv/bin/python -m build
# Should see NO deprecation warnings
```

### 6.2 Optional: Split Optional Dependencies

**Current:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

**Proposed:**
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
]

dev = [
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

# Future: documentation dependencies
# docs = [
#     "sphinx>=7.0.0",
#     "sphinx-rtd-theme>=1.3.0",
# ]

# Convenience: all development dependencies
all = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

**Update CI/Makefile:** Change `pip install -e .[dev]` to `pip install -e .[all]` or `.[test,dev]`

### 6.3 Create GitHub Actions Workflows

See Section 4.4 for complete workflow template. Files to create:

1. `.github/workflows/test-publish.yml` (TestPyPI)
2. `.github/workflows/publish.yml` (Production PyPI)

### 6.4 Document Release Process

**Create:** `docs/release/RELEASE_PROCESS.md`

**Contents:**
- How to create a release
- Pre-release checklist
- Version numbering scheme
- TestPyPI testing procedure
- Production release procedure
- Post-release verification
- Troubleshooting common issues

---

## 7. Known Issues and Risks

### 7.1 License Format Deprecation

**Status:** Identified in build test  
**Severity:** HIGH (build will fail after 2026-Feb-18)  
**Mitigation:** Fix in Sprint 5 Priority 4 Day 7  
**Effort:** 15 minutes

### 7.2 First-Time Package Publication

**Risk:** Pending publisher configuration errors  
**Mitigation:** Test on TestPyPI first (Day 7)  
**Fallback:** API token method (not preferred)

### 7.3 CLI Entry Point Testing

**Risk:** Entry point configuration may not work after PyPI install  
**Mitigation:** Test on TestPyPI with fresh virtualenv  
**Test Command:** `nlp2mcp --version` and basic model conversion

### 7.4 README Rendering on PyPI

**Risk:** Markdown may render incorrectly on PyPI page  
**Mitigation:** Preview with `twine check dist/*` before publishing  
**Action:** Verify TestPyPI page rendering on Day 7

### 7.5 Version Management

**Current:** Hardcoded version in pyproject.toml (`version = "0.1.0"`)  
**Risk:** Forgetting to update version before release  
**Future Enhancement:** Consider SCM-based versioning (setuptools-scm or hatch-vcs)  
**For Now:** Manual version updates with pre-release checklist

---

## 8. Category 4 Unknown Resolution

This section addresses the 4 CRITICAL unknowns from KNOWN_UNKNOWNS.md Category 4:

### Unknown 4.1: Does pyproject.toml build system work?

**Status:** ✅ RESOLVED

**Answer:** YES, with one caveat

- Build succeeds and creates valid wheel and sdist
- CLI entry point correctly configured
- All source modules included
- **Caveat:** License format deprecation must be fixed before 2026-Feb-18

**Evidence:** Successful build test (see Section 1.1)

### Unknown 4.2: Which build backend to use?

**Status:** ✅ RESOLVED

**Answer:** KEEP setuptools

**Reasoning:**
- Current setup works (79% market share, PyPA-maintained)
- Pure Python project doesn't need advanced features
- Migration effort not justified
- Alternative considered: Hatchling (would be choice for greenfield project)

**Evidence:** Market analysis and backend comparison (see Section 2)

### Unknown 4.3: How to manage dev vs prod dependencies?

**Status:** ✅ RESOLVED

**Answer:** Use optional-dependencies with separate groups

**Strategy:**
- Runtime dependencies in `dependencies` (lower bounds only)
- Development tools in `optional-dependencies.dev`
- Test dependencies in `optional-dependencies.test`
- Optional convenience group `optional-dependencies.all`
- NO upper bounds (library best practice for 2025)
- NO lock files (libraries should be flexible)

**Evidence:** Dependency management research and current configuration analysis (see Section 3)

### Unknown 4.4: What's the modern GitHub Actions workflow?

**Status:** ✅ RESOLVED

**Answer:** Trusted Publishers with OIDC (tokenless authentication)

**Approach:**
- Configure trusted publisher on PyPI (one-time setup)
- Use `pypa/gh-action-pypi-publish@release/v1` with `id-token: write`
- Trigger on GitHub releases
- No API tokens needed
- Automatic attestations included
- Test on TestPyPI first

**Evidence:** PyPI trusted publisher research and workflow template (see Section 4)

---

## 9. References

### 9.1 Python Packaging Standards

- PEP 517: A build-system independent format for source trees
- PEP 518: Specifying Minimum Build System Requirements for Python Projects
- PEP 621: Storing project metadata in pyproject.toml
- PEP 639: Improving License Clarity with Better Package Metadata
- Python Packaging User Guide: https://packaging.python.org/

### 9.2 Build Backend Documentation

- setuptools: https://setuptools.pypa.io/
- Hatchling: https://hatch.pypa.io/
- Poetry: https://python-poetry.org/
- PDM: https://pdm.fming.dev/

### 9.3 PyPI Publishing

- Trusted Publishers: https://docs.pypi.org/trusted-publishers/
- PyPI Publishing Guide: https://packaging.python.org/tutorials/packaging-projects/
- GitHub Actions OIDC: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi
- pypa/gh-action-pypi-publish: https://github.com/pypa/gh-action-pypi-publish

### 9.4 SPDX License Expressions

- SPDX License List: https://spdx.org/licenses/
- PEP 639 Specification: https://peps.python.org/pep-0639/
- License Expression Specification: https://packaging.python.org/en/latest/specifications/license-expression/

### 9.5 Research Sources (2025)

- "Python Build Backends in 2025: What to Use and Why" (Medium, Sep 2025)
- "PEP 517 build system popularity" (Quansight Labs, 2025)
- "Improving licence metadata" (Hugo van Kemenade, 2025)
- PyPI Trusted Publishers announcement (2023, still current in 2025)

---

## 10. Appendices

### Appendix A: Build Test Output

**Date:** 2025-11-06  
**Command:** `.venv/bin/python -m build`

**Full Output:**
```
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - setuptools>=61.0
  - wheel
* Getting build dependencies for sdist...
...
Successfully built nlp2mcp-0.1.0.tar.gz and nlp2mcp-0.1.0-py3-none-any.whl
```

**Warnings:**
- License format deprecation (TOML table → SPDX expression)
- License classifier deprecation (classifier → SPDX expression)

**Artifacts:**
- `dist/nlp2mcp-0.1.0-py3-none-any.whl` (121 KB)
- `dist/nlp2mcp-0.1.0.tar.gz` (105 KB)

### Appendix B: Current pyproject.toml Analysis

**Build System:** setuptools with build_meta backend  
**Python Requirement:** >=3.12  
**Dependencies:** 4 runtime (lark, numpy, click, tomli)  
**Optional Dependencies:** 5 dev tools (pytest, pytest-cov, black, ruff, mypy)  
**Entry Point:** `nlp2mcp` → `src.cli:main`  
**Package Discovery:** setuptools.packages.find from src/  

**Issues Identified:**
1. License format deprecated (HIGH priority fix)
2. Optional dependencies could be better organized (LOW priority)
3. tomli dependency unnecessary for Python 3.12+ (LOW priority)

### Appendix C: Competitive Analysis

**Similar Projects on PyPI:**
- cvxpy: Uses setuptools, 1M+ downloads/month
- pyomo: Uses setuptools, 100K+ downloads/month
- pulp: Uses setuptools, 500K+ downloads/month

**Observation:** Mature optimization libraries predominantly use setuptools, validating our decision to keep it.

---

## 11. Conclusion

This comprehensive survey confirms that nlp2mcp is well-positioned for PyPI publication with minimal required changes:

**Required Actions (HIGH Priority):**
1. Fix license format to SPDX expression (15 min)
2. Create GitHub Actions workflows for trusted publishing (1 hour)
3. Configure PyPI trusted publishers (15 min)
4. Test on TestPyPI (1 hour)
5. Publish to production PyPI (30 min)

**Total Estimated Effort:** 6-8 hours (fits Sprint 5 Days 7-8 allocation)

**Key Decisions:**
- ✅ Keep setuptools (stable, proven, adequate)
- ✅ Use OIDC trusted publishing (modern, secure)
- ✅ Lower bounds only on dependencies (library best practice)
- ✅ Test on TestPyPI first (risk mitigation)

**Next Steps:**
1. Review and approve this plan
2. Schedule Sprint 5 Priority 4 (Days 7-8)
3. Execute Day 7 tasks (TestPyPI)
4. Execute Day 8 tasks (Production PyPI)
5. Verify and celebrate first PyPI release! 🎉

---

**Document Status:** FINAL  
**Reviewed By:** [Pending]  
**Approved By:** [Pending]  
**Implementation Start Date:** [Sprint 5 Day 7]
