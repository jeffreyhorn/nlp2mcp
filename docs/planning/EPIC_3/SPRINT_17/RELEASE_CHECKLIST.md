# v1.1.0 Release Checklist

**Created:** January 30, 2026  
**Sprint:** 17 Prep - Task 8  
**Status:** Complete  
**Purpose:** Comprehensive checklist for v1.1.0 release

---

## Executive Summary

This document provides a complete checklist for the v1.1.0 release at the end of Sprint 17. The release represents the culmination of Epic 3 (GAMSLIB Validation Infrastructure) and includes significant improvements to parse, translate, and solve rates.

**Release Timeline:**
- Sprint 17 Days 1-8: Development and testing
- Sprint 17 Day 9: Pre-release verification
- Sprint 17 Day 10: Release execution

---

## Pre-Release Verification Steps

### 1. Code Quality Gates

| Check | Command | Requirement | Status |
|-------|---------|-------------|--------|
| Type checking | `make typecheck` | 0 errors | [ ] |
| Linting | `make lint` | 0 errors | [ ] |
| Formatting | `make format` | No changes needed | [ ] |
| Unit tests | `make test` | All passing | [ ] |
| Test count | `pytest --collect-only` | ≥3100 tests | [ ] |

**Commands:**
```bash
make typecheck && make lint && make format && make test
```

### 2. Test Requirements

| Test Suite | Requirement | Status |
|------------|-------------|--------|
| Unit tests | 100% passing | [ ] |
| Integration tests | 100% passing | [ ] |
| GAMSLIB pipeline tests | Metrics meet targets | [ ] |
| Reporting tests | All passing | [ ] |
| No regressions | Compare to Sprint 16 baseline | [ ] |

### 3. Metrics Targets

| Metric | Sprint 16 Baseline | v1.1.0 Target | Actual | Status |
|--------|-------------------|---------------|--------|--------|
| Parse Rate | 30.0% (48/160) | ≥70% (112/160) | TBD | [ ] |
| Translate Rate | 43.8% (21/48) | ≥60% of parsed | TBD | [ ] |
| Solve Rate | 52.4% (11/21) | ≥80% of translated | TBD | [ ] |
| Full Pipeline | 3.1% (5/160) | ≥50% (80/160) | TBD | [ ] |

**Verification command:**
```bash
python scripts/gamslib/run_full_test.py --json
```

### 4. Documentation Requirements

| Document | Requirement | Status |
|----------|-------------|--------|
| USER_GUIDE.md | Version updated to 1.1.0 | [ ] |
| TUTORIAL.md | Examples verified working | [ ] |
| DOCUMENTATION_INDEX.md | Updated with current docs | [ ] |
| GAMSLIB_TESTING.md | Current and accurate | [ ] |
| GAMSLIB_USAGE.md | Current and accurate | [ ] |
| API docs (Sphinx) | Builds without errors | [ ] |

### 5. No Blocking Issues

| Check | Requirement | Status |
|-------|-------------|--------|
| GitHub Issues | No P0/Critical open issues | [ ] |
| Known regressions | None from Sprint 16 | [ ] |
| CI pipeline | Green on main branch | [ ] |

---

## Artifact Preparation

### 1. Version Bump

**Files to update:**

| File | Location | Change |
|------|----------|--------|
| `pyproject.toml` | `project.version` | `"1.0.0"` → `"1.1.0"` |

**Command:**
```bash
# Edit pyproject.toml manually or use version script if available
# macOS / BSD:
sed -i '' 's/version = "1.0.0"/version = "1.1.0"/' pyproject.toml

# GNU/Linux:
sed -i 's/version = "1.0.0"/version = "1.1.0"/' pyproject.toml
```

**Verification:**
```bash
grep 'version' pyproject.toml
python -c "import nlp2mcp; print(nlp2mcp.__version__)"
```

### 2. CHANGELOG Update

**Location:** `CHANGELOG.md`

**Format:**
```markdown
## [1.1.0] - 2026-02-XX

### Added
- GAMSLIB validation infrastructure with automated reporting
- Jinja2-based report generation (`src/reporting/`)
- Full pipeline testing scripts (`scripts/gamslib/`)
- Comprehensive GAMSLIB status tracking

### Changed
- Parse rate: 21.2% → XX% (+YY models)
- Solve rate: 17.6% → XX% (+YY models)
- Full pipeline: 0.6% → XX% (+YY models)

### Fixed
- Grammar extensions for FREE keyword, abort syntax, tuple expansion
- emit_gams.py unary minus handling
- emit_gams.py set element quoting
- [List other significant fixes]

### Documentation
- Updated USER_GUIDE.md for v1.1.0
- Created GAMSLIB_TESTING.md user guide
- Updated DOCUMENTATION_INDEX.md
```

### 3. Release Notes

**Location:** `docs/releases/v1.1.0.md`

**Content template:**
```markdown
# Release v1.1.0

**Release Date:** 2026-02-XX  
**Sprint:** 17 (Epic 3 Completion)

## Highlights

- **GAMSLIB Validation Infrastructure:** Comprehensive testing against 160 NLP models
- **Automated Reporting:** Generate status and failure reports with `generate_report.py`
- **Significant Improvements:** Parse XX%, Solve XX%, Full Pipeline XX%

## Metrics Comparison

| Metric | v1.0.0 (Baseline) | v1.1.0 | Improvement |
|--------|-------------------|--------|-------------|
| Parse Rate | 21.2% | XX% | +XX% |
| Translate Rate | 50.0% | XX% | +XX% |
| Solve Rate | 17.6% | XX% | +XX% |
| Full Pipeline | 0.6% | XX% | +XX% |

## Breaking Changes

None. This release is backwards-compatible.

## Installation

\`\`\`bash
pip install nlp2mcp==1.1.0
\`\`\`

## Contributors

- [List contributors]

## Full Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for complete list of changes.
```

---

## Release Execution Steps

### Step 1: Final Verification (Day 9)

```bash
# 1. Ensure on main branch with latest changes
git checkout main
git pull origin main

# 2. Run all quality checks
make typecheck && make lint && make format && make test

# 3. Run full GAMSLIB pipeline test
python scripts/gamslib/run_full_test.py --json > release_metrics.json

# 4. Verify metrics meet targets
cat release_metrics.json | jq '.stages'

# 5. Verify documentation builds
cd docs/api && make html && cd ../..
```

### Step 2: Version Bump and Commit (Day 10)

```bash
# 1. Update version in pyproject.toml
# Edit: version = "1.1.0"

# 2. Update CHANGELOG.md with final content

# 3. Create release notes
# Create: docs/releases/v1.1.0.md

# 4. Commit version bump
git add pyproject.toml CHANGELOG.md docs/releases/v1.1.0.md
git commit -m "Release v1.1.0

Epic 3: GAMSLIB Validation Infrastructure complete.

Key metrics:
- Parse: XX% (YY/160 models)
- Solve: XX% (YY/ZZ models)
- Full Pipeline: XX% (YY/160 models)

See CHANGELOG.md for full details."

# 5. Push to main
git push origin main
```

### Step 3: Create Git Tag

```bash
# 1. Create annotated tag
git tag -a v1.1.0 -m "Release v1.1.0 - Epic 3 Complete

GAMSLIB Validation Infrastructure with:
- Automated reporting
- XX% parse rate
- XX% solve rate
- XX% full pipeline success"

# 2. Push tag
git push origin v1.1.0
```

### Step 4: Create GitHub Release

```bash
# Using gh CLI
gh release create v1.1.0 \
  --title "v1.1.0 - GAMSLIB Validation Infrastructure" \
  --notes-file docs/releases/v1.1.0.md
```

**Or manually via GitHub:**
1. Go to https://github.com/jeffreyhorn/nlp2mcp/releases
2. Click "Draft a new release"
3. Select tag `v1.1.0`
4. Title: "v1.1.0 - GAMSLIB Validation Infrastructure"
5. Body: Copy from `docs/releases/v1.1.0.md`
6. Click "Publish release"

---

## Post-Release Verification

### 1. Smoke Tests

| Test | Command | Expected | Status |
|------|---------|----------|--------|
| Install from tag | `pip install git+https://github.com/...@v1.1.0` | Success | [ ] |
| CLI works | `nlp2mcp --help` | Shows help | [ ] |
| Basic conversion | `nlp2mcp examples/simple.gms` | Produces output | [ ] |
| Version correct | `nlp2mcp --version` | Shows 1.1.0 | [ ] |

### 2. Documentation Live Check

| Check | URL/Location | Status |
|-------|--------------|--------|
| GitHub release visible | `/releases/tag/v1.1.0` | [ ] |
| README accurate | `/blob/v1.1.0/README.md` | [ ] |
| CHANGELOG updated | `/blob/v1.1.0/CHANGELOG.md` | [ ] |

### 3. CI Verification

| Check | Status |
|-------|--------|
| Tag build passed | [ ] |
| All tests green on v1.1.0 | [ ] |

---

## Rollback Plan

### If Critical Issue Found After Release

**Within 24 hours:**
1. Delete the GitHub release (keeps tag for reference)
2. Create issue documenting the problem
3. Fix issue on main branch
4. Re-release as v1.1.1

**Commands:**
```bash
# Delete GitHub release (keeps tag)
gh release delete v1.1.0 --yes

# Do NOT delete the tag unless absolutely necessary
# Tags should be preserved for history

# After fix, create patch release
git tag -a v1.1.1 -m "Patch release fixing [issue]"
git push origin v1.1.1
gh release create v1.1.1 --title "v1.1.1 - Patch Release" --notes "Fixes [issue]"
```

---

## Release Blockers to Monitor

### During Sprint 17

| Blocker | Description | Mitigation | Status |
|---------|-------------|------------|--------|
| CI failures | Tests failing on main | Fix immediately | [ ] |
| Parse rate < 50% | Not hitting minimum target | Prioritize lexer fixes | [ ] |
| Solve rate < 60% | Not hitting minimum target | Prioritize emit fixes | [ ] |
| Documentation incomplete | User docs not ready | Allocate Day 8-9 | [ ] |
| Blocking issues | P0 bugs discovered | Must fix before release | [ ] |

### Day-by-Day Monitoring

| Day | Key Milestone | Blocker Risk |
|-----|---------------|--------------|
| Day 1-3 | Translation fixes | Fix complexity |
| Day 4-5 | Solve improvements | Unexpected bugs |
| Day 6-7 | Parse improvements | Grammar complexity |
| Day 8 | Documentation | Time pressure |
| Day 9 | Pre-release verification | Metrics not met |
| Day 10 | Release | Last-minute issues |

---

## Quality Gate Summary

### Must Pass Before Release

1. **Code Quality:** `make typecheck && make lint && make format && make test` - all green
2. **Metrics:** At least one of the following met:
   - Parse ≥50% (minimum viable)
   - Solve ≥60% (minimum viable)
   - Full Pipeline ≥25% (minimum viable)
3. **No Regressions:** All Sprint 16 passing models still pass
4. **Documentation:** USER_GUIDE.md updated, GAMSLIB guides accurate
5. **No Blockers:** No P0/Critical open issues

### Nice-to-Have (Not Blocking)

- Parse ≥70% (stretch goal)
- Solve ≥80% (stretch goal)
- Full Pipeline ≥50% (stretch goal)
- API docs rebuilt with Sphinx
- All P1 issues addressed

---

## Verification Checklist Summary

- [x] Pre-release verification steps defined
- [x] Quality gates defined
- [x] Artifact preparation documented
- [x] Release execution steps documented
- [x] Post-release verification planned
- [x] Rollback plan created
- [x] Release blockers identified

---

## References

- [VERSIONING.md](../../../release/VERSIONING.md) - Version numbering strategy
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Sprint 17 objectives
- [SPRINT_BASELINE.md](../../../testing/SPRINT_BASELINE.md) - Current metrics
- [DOCUMENTATION_PLAN.md](./DOCUMENTATION_PLAN.md) - Documentation gaps
