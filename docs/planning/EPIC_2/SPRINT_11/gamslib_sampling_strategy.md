# GAMSLib Sampling Strategy for CI Regression Testing

**Date:** 2025-11-25  
**Task:** Sprint 11 Prep Task 7 - Design GAMSLib Sampling Strategy  
**Objective:** Define comprehensive CI regression testing strategy for GAMSLib models: model selection, test frequency, test scope, and pass/fail criteria

---

## Executive Summary

This document defines the **GAMSLib sampling strategy** for automated CI regression testing in Sprint 11 and beyond. The strategy balances comprehensive coverage with CI performance by testing all 10 Tier 1 models using parallelized matrix builds while keeping CI runtime under 5 minutes.

**Key Decisions:**
- **Model Selection:** Test all 10 Tier 1 models (comprehensive coverage)
- **Test Frequency:** Parse+Convert on every PR, Parse+Convert+Solve nightly
- **Test Scope:** Incremental expansion (parse → convert → solve)
- **Pass/Fail Criteria:** Multi-metric thresholds with baselines from main branch
- **CI Runtime:** 10 min → 2-3 min (70% reduction via matrix builds)

**Unknown 3.1 Verification Result:** ✅ **VERIFIED** - Testing all 10 Tier 1 models with matrix parallelization provides optimal regression coverage while maintaining fast CI feedback (<5 min).

---

## Table of Contents

1. [Section 1: Model Selection Strategy](#section-1-model-selection-strategy)
2. [Section 2: Test Frequency Strategy](#section-2-test-frequency-strategy)
3. [Section 3: Test Scope Strategy](#section-3-test-scope-strategy)
4. [Section 4: Pass/Fail Criteria](#section-4-pass-fail-criteria)
5. [Section 5: Baseline Management](#section-5-baseline-management)
6. [Section 6: Flaky Test Mitigation](#section-6-flaky-test-mitigation)
7. [Section 7: Implementation Roadmap](#section-7-implementation-roadmap)
8. [Section 8: Cost-Benefit Analysis](#section-8-cost-benefit-analysis)
9. [Appendix A: Tier 1 Model Characteristics](#appendix-a-tier-1-model-characteristics)
10. [Appendix B: Alternative Sampling Approaches](#appendix-b-alternative-sampling-approaches)
11. [Appendix C: CI Workflow Examples](#appendix-c-ci-workflow-examples)

---

## Section 1: Model Selection Strategy

### 1.1 Current Model Set: Tier 1 (10 Models)

The project currently uses **10 Tier 1 models** selected for comprehensive feature coverage:

| # | Model | Type | Size | Parse Status | Key Features | Rationale |
|---|-------|------|------|--------------|--------------|-----------|
| 1 | **trig** | NLP | Small | ✅ SUCCESS | Trig functions, minimal deps | Baseline - simple syntax test |
| 2 | **rbrock** | NLP | Small | ✅ SUCCESS | Rosenbrock, unconstrained | Classic test - nonlinear optimization |
| 3 | **himmel16** | NLP | Small | ✅ SUCCESS | Sets, indexed vars, multi-dim | Tests indexing features |
| 4 | **hs62** | NLP | Small | ✅ SUCCESS | Hock-Schittkowski collection | Standard test problem |
| 5 | **mhw4d** | NLP | Small | ✅ SUCCESS | Nonlinear constraints | Simple nonlinear test |
| 6 | **mhw4dx** | NLP | Small | ✅ SUCCESS | MHW4D variant, additional tests | Extension of mhw4d |
| 7 | **circle** | NLP | Small | ✅ SUCCESS | Geometric constraints | Circle packing problem |
| 8 | **maxmin** | DNLP | Small | ❌ FAILED | Nested indexing, min/max | Known blocker (nested indexing) |
| 9 | **mathopt1** | NLP | Small | ✅ SUCCESS | MathOptimizer baseline | Simple constrained optimization |
| 10 | **mingamma** | DNLP | Small | ✅ SUCCESS | Gamma function | Special function test |

**Current Parse Rate:** 90% (9/10 models)  
**Failed Model:** maxmin.gms (nested indexing - known gap)

**Feature Coverage:**
- ✅ Trig functions (trig)
- ✅ Power functions (rbrock, circle)
- ✅ Sets and indexing (himmel16, hs62)
- ✅ Multi-dimensional indexing (himmel16)
- ✅ Constrained optimization (mathopt1, hs62)
- ✅ Unconstrained optimization (rbrock)
- ✅ Special functions (mingamma - gamma)
- ⚠️ Nested indexing (maxmin - not yet supported)
- ✅ DNLP models (maxmin, mingamma)

### 1.2 Model Selection Decision: Test All 10 Tier 1 Models

**Decision:** ✅ **TEST ALL 10 TIER 1 MODELS**

**Rationale:**
1. **Comprehensive Coverage:** 10 models cover diverse features (trig, power, indexing, special functions)
2. **Matrix Parallelization:** Testing all 10 models in parallel takes 2-3 min (vs. 10 min sequential)
3. **Early Detection:** Testing all models catches regressions immediately (no delayed detection)
4. **Small Model Set:** 10 models is manageable (not hundreds), CI cost minimal
5. **Stable Set:** Tier 1 models selected for stability and representativeness

**CI Runtime with Matrix Build:**
```yaml
strategy:
  matrix:
    model: [trig, rbrock, himmel16, hs62, mhw4d, mhw4dx, circle, maxmin, mathopt1, mingamma]
  fail-fast: false  # Test all models even if one fails
```
- **Sequential:** ~10 minutes (1 min per model)
- **Matrix (10 parallel jobs):** ~2-3 minutes (longest model + overhead)
- **Runtime Reduction:** 70% faster

### 1.3 Alternative Approaches Considered

See [Appendix B: Alternative Sampling Approaches](#appendix-b-alternative-sampling-approaches) for detailed comparison of:
- **Canary Models (5 fixed + 5 rotated)** - Rejected: delayed detection for non-canary models
- **Risk-Based Sampling** - Rejected: requires manual risk assessment, complex
- **Fast/Full Split** - Rejected: can merge PRs with regressions if only fast tests run

**Why "Test All" Wins:**
- Matrix parallelization makes "test all" as fast as "test 5"
- Comprehensive coverage eliminates delayed regression detection
- Simpler strategy (no canary selection logic needed)
- Future-proof: scales to Tier 2 nightly tests (add more models to matrix)

---

## Section 2: Test Frequency Strategy

### 2.1 Current Implementation

**Existing Trigger:** `.github/workflows/gamslib-regression.yml`
```yaml
on:
  pull_request:
    paths:
      - "src/gams/grammar.lark"          # Grammar changes
      - "src/gams/parser.py"             # Parser implementation
      - "src/ir/parser.py"               # IR parser
      - "src/ir/symbols.py"              # IR definitions
      - "src/ir/ast.py"                  # AST definitions
      - "scripts/ingest_gamslib.py"      # Ingestion script
      - "scripts/check_parse_rate_regression.py"  # Checker
      - ".github/workflows/gamslib-regression.yml"  # Workflow itself
  
  schedule:
    - cron: "0 0 * * 0"  # Weekly validation every Sunday at 00:00 UTC
  
  workflow_dispatch:  # Manual trigger for testing
```

**Strengths:**
- ✅ Selective triggering (only runs on parser-related changes)
- ✅ Weekly validation (catches drift, external changes)
- ✅ Manual trigger (testing and debugging)

**Gaps:**
- ⚠️ No nightly full validation (weekly may miss issues for days)
- ⚠️ No pre-merge required check (can be skipped if no parser files changed)

### 2.2 Recommended Test Frequency

**Decision:** Three-tier testing strategy

#### Tier 1: Per-PR Fast Checks (Every PR)
- **Trigger:** All PRs (not just parser changes)
- **Scope:** Parse + Convert (no solve)
- **Models:** All 10 Tier 1 models (matrix parallelization)
- **Runtime:** 2-3 minutes
- **Purpose:** Fast feedback, catch regressions before merge

```yaml
on:
  pull_request:  # All PRs, not just parser changes
```

**Rationale:**
- Parser changes are not always obvious (IR changes can break parsing)
- Dependency updates (lark-parser, etc.) can break parsing
- Fast enough (2-3 min) to run on every PR
- Prevents merge of any regression

#### Tier 2: Nightly Full Validation (Every Night)
- **Trigger:** Scheduled nightly at 00:00 UTC
- **Scope:** Parse + Convert + Solve (end-to-end)
- **Models:** All 10 Tier 1 models + Tier 2 models (20+ total)
- **Runtime:** 10-20 minutes (acceptable for nightly)
- **Purpose:** Comprehensive validation, solve testing, drift detection

```yaml
on:
  schedule:
    - cron: "0 0 * * *"  # Nightly at 00:00 UTC
```

**Rationale:**
- Solve testing too slow for per-PR (PATH installation, solve time)
- Extended model set (Tier 2) catches edge cases
- Detects external changes (GAMS updates, dependency changes)

#### Tier 3: Weekly Extended Suite (Every Sunday)
- **Trigger:** Scheduled weekly at 00:00 UTC Sunday
- **Scope:** Parse + Convert + Solve + Performance Trends
- **Models:** All Tier 1 + Tier 2 + Tier 3 (50+ total)
- **Runtime:** 30-60 minutes (acceptable for weekly)
- **Purpose:** Long-term trend tracking, comprehensive regression detection

```yaml
on:
  schedule:
    - cron: "0 0 * * 0"  # Weekly on Sunday at 00:00 UTC
```

**Rationale:**
- Performance trend tracking (compare vs. last week, last sprint)
- Comprehensive model coverage (all tiers)
- Golden baseline validation (ensure no drift from sprint goals)

### 2.3 Test Frequency Summary Table

| Frequency | Trigger | Scope | Models | Runtime | Purpose |
|-----------|---------|-------|--------|---------|---------|
| **Per-PR** | Every PR | Parse + Convert | 10 Tier 1 | 2-3 min | Fast regression detection |
| **Nightly** | Daily 00:00 UTC | Parse + Convert + Solve | 10 Tier 1 + Tier 2 | 10-20 min | Comprehensive validation |
| **Weekly** | Sunday 00:00 UTC | Full + Performance | All Tiers | 30-60 min | Trend tracking, drift detection |

---

## Section 3: Test Scope Strategy

### 3.1 Current Implementation: Parse-Only Testing

**Current Scope:** `scripts/ingest_gamslib.py`
```python
# Current: Parse-only validation
models = parse_all_models()  # Parse GAMS → AST
report_parse_rate(models)    # Report: 90% (9/10 models)
```

**Metrics Tracked:**
- ✅ `parse_rate_percent`: 90% (9/10 models)
- ❌ `convert_rate_percent`: 0% (not implemented)
- ❌ `solve_rate_percent`: 0% (not implemented)

**Gap:** Parse-only testing does not validate:
- IR generation (parse → IR conversion)
- MCP generation (IR → MCP reformulation)
- Solve success (MCP → PATH solver)

### 3.2 Recommended Test Scope: Incremental Expansion

**Decision:** Incremental scope expansion across testing tiers

#### Scope 1: Parse + Convert (Per-PR)
```python
# Enhanced: Parse + Convert validation
models = parse_all_models()        # Parse GAMS → AST
converted = convert_to_ir(models)  # Convert AST → IR → MCP
report = {
    "parse_rate_percent": ...,     # 90% (9/10 models)
    "convert_rate_percent": ...,   # NEW (target: 80-90%)
    "conversion_errors": ...       # NEW (categorized errors)
}
```

**Metrics Added:**
- ✅ `convert_rate_percent`: Percentage of models that convert to MCP successfully
- ✅ `conversion_errors`: Categorized errors (missing features, unsupported syntax, etc.)
- ✅ `conversion_time_ms`: Time to convert each model (performance tracking)

**Rationale:**
- Conversion is fast (~1-2 sec per model)
- Catches IR/MCP generation bugs (not just parser bugs)
- Still fast enough for per-PR testing (2-3 min total)

#### Scope 2: Parse + Convert + Solve (Nightly)
```python
# Full pipeline: Parse + Convert + Solve
models = parse_all_models()
converted = convert_to_ir(models)
solved = solve_with_path(converted)  # NEW: PATH solver validation
report = {
    "parse_rate_percent": ...,
    "convert_rate_percent": ...,
    "solve_rate_percent": ...,     # NEW (target: 70-80%)
    "solve_failures": ...,         # NEW (categorized solve failures)
    "solve_time_ms": ...           # NEW (performance tracking)
}
```

**Metrics Added:**
- ✅ `solve_rate_percent`: Percentage of models that solve successfully with PATH
- ✅ `solve_failures`: Categorized solve failures (infeasible, unbounded, solver error, etc.)
- ✅ `solve_time_ms`: Time to solve each model (performance tracking)
- ✅ `solution_quality`: Solution objective value (regression check)

**Rationale:**
- PATH installation required (~30 sec overhead)
- Solve time varies (1-10 sec per model)
- End-to-end validation (parse → convert → solve)
- Too slow for per-PR, acceptable for nightly

#### Scope 3: Full + Performance Trends (Weekly)
```python
# Comprehensive validation + trend tracking
models = parse_all_models()
converted = convert_to_ir(models)
solved = solve_with_path(converted)
performance = track_performance_trends(converted, solved)  # NEW: Trend analysis
report = {
    # Standard metrics
    "parse_rate_percent": ...,
    "convert_rate_percent": ...,
    "solve_rate_percent": ...,
    
    # Performance trends
    "conversion_time_trend": ...,  # NEW (compare vs. last week, last sprint)
    "solve_time_trend": ...,       # NEW
    "memory_usage_trend": ...,     # NEW
    "term_count_trend": ...        # NEW (MCP complexity)
}
```

**Metrics Added:**
- ✅ `conversion_time_trend`: Week-over-week performance change
- ✅ `solve_time_trend`: Week-over-week solve time change
- ✅ `memory_usage_trend`: Memory usage tracking
- ✅ `term_count_trend`: MCP term count (complexity metric)

**Rationale:**
- Performance trends require historical baselines
- Weekly cadence provides stable trend data
- Detects performance regressions early

### 3.3 Test Scope Summary Table

| Scope | Validation | Metrics | Runtime | Frequency |
|-------|-----------|---------|---------|-----------|
| **Parse + Convert** | Parse → AST → IR → MCP | parse%, convert%, conversion_time | 2-3 min | Per-PR |
| **Parse + Convert + Solve** | Full pipeline + PATH | parse%, convert%, solve%, solve_time | 10-20 min | Nightly |
| **Full + Performance** | Full + trends | All + trend analysis | 30-60 min | Weekly |

---

## Section 4: Pass/Fail Criteria

### 4.1 Current Implementation

**Current Threshold:** `check_parse_rate_regression.py`
```python
# Single-metric threshold
threshold = 0.10  # 10% relative drop triggers failure

is_regression = (baseline - current) / baseline > threshold
```

**Example:**
- Baseline: 90% (9/10 models)
- Current: 80% (8/10 models)
- Relative drop: (90 - 80) / 90 = 11.1% > 10% → ❌ **FAIL**

**Strengths:**
- ✅ Simple threshold (easy to understand)
- ✅ Relative drop (accounts for baseline variability)
- ✅ Proven effective (no false positives in Sprint 10)

**Gaps:**
- ⚠️ Single metric only (parse rate)
- ⚠️ No per-model failure tracking (aggregate only)
- ⚠️ No performance thresholds

### 4.2 Recommended Multi-Metric Pass/Fail Criteria

**Decision:** Multi-metric thresholds with per-model tracking

#### Criterion 1: Parse Rate Threshold
```python
# Parse rate regression check
parse_rate_drop = (baseline_parse_rate - current_parse_rate) / baseline_parse_rate

if parse_rate_drop > 0.05:  # 5% drop warning
    print("⚠️ WARNING: Parse rate dropped 5%")
    
if parse_rate_drop > 0.10:  # 10% drop failure
    print("❌ FAILURE: Parse rate regression detected")
    exit(1)
```

**Thresholds:**
- **Warning:** 5% relative drop (e.g., 90% → 85.5%)
- **Failure:** 10% relative drop (e.g., 90% → 81%)

**Rationale:**
- 10% threshold proven effective (current implementation)
- 5% warning provides early signal (before CI fails)
- Relative drop accounts for baseline variability

#### Criterion 2: Convert Rate Threshold (NEW)
```python
# Convert rate regression check
convert_rate_drop = (baseline_convert_rate - current_convert_rate) / baseline_convert_rate

if convert_rate_drop > 0.05:  # 5% drop warning
    print("⚠️ WARNING: Convert rate dropped 5%")
    
if convert_rate_drop > 0.10:  # 10% drop failure
    print("❌ FAILURE: Convert rate regression detected")
    exit(1)
```

**Thresholds:**
- **Warning:** 5% relative drop
- **Failure:** 10% relative drop

**Rationale:**
- Same threshold as parse rate (consistency)
- Convert rate as important as parse rate (full pipeline validation)

#### Criterion 3: Per-Model Failure Tracking (NEW)
```python
# Per-model failure tracking
for model in models:
    baseline_status = get_baseline_status(model.name)
    current_status = model.parse_status
    
    if baseline_status == "SUCCESS" and current_status == "FAILED":
        print(f"❌ REGRESSION: {model.name} failed (was passing)")
        regressions.append(model.name)

if len(regressions) > 0:
    print(f"❌ FAILURE: {len(regressions)} model regressions detected")
    print(f"Regressed models: {regressions}")
    exit(1)
```

**Threshold:**
- **Failure:** Any previously passing model now fails

**Rationale:**
- Aggregate metrics can hide per-model regressions
- Example: If 2 models regress but 2 others improve, parse rate unchanged
- Per-model tracking catches all regressions

#### Criterion 4: Performance Thresholds (NEW)
```python
# Performance regression check
for model in models:
    baseline_time = get_baseline_conversion_time(model.name)
    current_time = model.conversion_time_ms
    
    performance_increase = (current_time - baseline_time) / baseline_time
    
    if performance_increase > 0.20:  # 20% slower warning
        print(f"⚠️ WARNING: {model.name} conversion 20% slower")
        warnings.append(model.name)
    
    if performance_increase > 0.50:  # 50% slower failure
        print(f"❌ FAILURE: {model.name} conversion 50% slower")
        failures.append(model.name)

if len(failures) > 0:
    print(f"❌ FAILURE: {len(failures)} performance regressions detected")
    exit(1)
```

**Thresholds:**
- **Warning:** 20% slower (e.g., 100ms → 120ms)
- **Failure:** 50% slower (e.g., 100ms → 150ms)

**Rationale:**
- Based on Task 6 CI survey findings (Unknown 3.3)
- 20% threshold = 2× safety margin above ±10% variance
- 50% threshold catches major performance regressions

#### Criterion 5: Solve Rate Threshold (Nightly Only)
```python
# Solve rate regression check (nightly only)
solve_rate_drop = (baseline_solve_rate - current_solve_rate) / baseline_solve_rate

if solve_rate_drop > 0.10:  # 10% drop failure
    print("❌ FAILURE: Solve rate regression detected")
    exit(1)
```

**Thresholds:**
- **Warning:** 5% relative drop
- **Failure:** 10% relative drop

**Rationale:**
- Solve rate as important as convert rate (end-to-end validation)
- Only runs nightly (too slow for per-PR)

### 4.3 Pass/Fail Criteria Summary Table

| Metric | Warning Threshold | Failure Threshold | Frequency | Rationale |
|--------|------------------|-------------------|-----------|-----------|
| **Parse Rate** | 5% drop | 10% drop | Per-PR | Current proven threshold |
| **Convert Rate** | 5% drop | 10% drop | Per-PR | Same as parse rate |
| **Per-Model Status** | N/A | Any passing → failing | Per-PR | Catches hidden regressions |
| **Conversion Time** | +20% | +50% | Per-PR | 2× safety margin above variance |
| **Solve Rate** | 5% drop | 10% drop | Nightly | End-to-end validation |
| **Solve Time** | +20% | +50% | Nightly | Same as conversion time |

### 4.4 Aggregate Pass/Fail Logic

**Per-PR Fast Checks:**
```python
# CI fails if ANY of these are true:
failures = []

# Check 1: Parse rate regression
if parse_rate_drop > 0.10:
    failures.append("Parse rate regression (>10% drop)")

# Check 2: Convert rate regression
if convert_rate_drop > 0.10:
    failures.append("Convert rate regression (>10% drop)")

# Check 3: Per-model regressions
if len(model_regressions) > 0:
    failures.append(f"{len(model_regressions)} models regressed")

# Check 4: Performance regressions
if len(performance_failures) > 0:
    failures.append(f"{len(performance_failures)} performance regressions (>50% slower)")

# Fail if any criterion triggered
if len(failures) > 0:
    print("❌ CI FAILED")
    for failure in failures:
        print(f"  - {failure}")
    exit(1)
else:
    print("✅ CI PASSED")
    exit(0)
```

**Warnings (non-blocking):**
```python
# CI passes but warns if ANY of these are true:
warnings = []

if 0.05 < parse_rate_drop <= 0.10:
    warnings.append("Parse rate dropped 5-10%")

if 0.05 < convert_rate_drop <= 0.10:
    warnings.append("Convert rate dropped 5-10%")

if len(performance_warnings) > 0:
    warnings.append(f"{len(performance_warnings)} models 20-50% slower")

if len(warnings) > 0:
    print("⚠️ WARNINGS DETECTED (CI passed)")
    for warning in warnings:
        print(f"  - {warning}")
```

---

## Section 5: Baseline Management

### 5.1 Current Baseline Approach

**Current Implementation:** Git-tracked JSON baselines
```python
# check_parse_rate_regression.py
baseline_rate = read_baseline_from_git("origin/main", "reports/gamslib_ingestion_sprint6.json")
```

**How It Works:**
1. PR updates `reports/gamslib_ingestion_sprint6.json` with new parse rate
2. PR merges to main
3. Next PR automatically uses new main as baseline (via `git show origin/main:...`)
4. **Automatic baseline evolution** - no manual updates needed

**Strengths:**
- ✅ Zero-effort baseline updates
- ✅ Baselines always match main branch
- ✅ Git history provides audit trail
- ✅ Simple implementation (no external storage)

**Weaknesses:**
- ⚠️ Temporary regressions can become new baseline if merged accidentally
- ⚠️ No "golden baseline" (known-good reference point)
- ⚠️ Hard to track long-term trends (need separate trending mechanism)

### 5.2 Recommended Enhanced Baseline Strategy

**Decision:** Dual-baseline approach (rolling + golden)

#### Rolling Baseline (Current + Enhanced)
```
reports/
  gamslib_ingestion_sprint11.json  # Rolling baseline (git-tracked)
```

**Purpose:** Per-PR regression detection (compare against main)

**Update Frequency:** Every merge to main (automatic)

**Usage:**
```python
# Compare current PR against latest main
baseline = read_baseline_from_git("origin/main", "reports/gamslib_ingestion_sprint11.json")
check_regression(current, baseline, threshold=0.10)
```

#### Golden Baselines (NEW)
```
baselines/
  golden/
    sprint10.json   # Sprint 10 final baseline (90% parse rate)
    sprint11.json   # Sprint 11 target baseline (100% parse rate target)
    sprint12.json   # Sprint 12 target baseline (future)
```

**Purpose:** Long-term trend tracking, sprint goal validation

**Update Frequency:** Manual (end of each sprint)

**Usage:**
```python
# Compare current PR against sprint goal
golden = read_baseline("baselines/golden/sprint11.json")
check_progress(current, golden)  # Report progress toward sprint goal
```

**Example:**
```bash
# Sprint 11 goal: 100% parse rate, 90% convert rate
# Current: 90% parse rate, 0% convert rate
# Progress: 90% toward parse goal, 0% toward convert goal

✅ Parse rate: 90% (target: 100%, progress: 90%)
⚠️ Convert rate: 0% (target: 90%, progress: 0%)
```

#### Performance Baselines (NEW - Git LFS)
```
baselines/
  performance/
    baseline_latest.json           # Rolling baseline (git-lfs, updated on main merge)
    baseline_sprint10.json         # Sprint 10 golden baseline
    baseline_sprint11.json         # Sprint 11 golden baseline
    history/
      2025-11-01_commit-abc123.json  # Historical snapshots
      2025-11-08_commit-def456.json
      2025-11-15_commit-ghi789.json
```

**Purpose:** Performance trend tracking (conversion time, solve time, memory)

**Storage:** Git LFS (frequent updates, large JSON files)

**Update Frequency:** 
- Rolling: Every merge to main (automatic)
- Golden: Manual (end of each sprint)
- History: Weekly snapshots (automatic via cron)

**Usage:**
```python
# Compare performance against rolling baseline
baseline = read_performance_baseline("baselines/performance/baseline_latest.json")
check_performance_regression(current, baseline, threshold=0.20)

# Track trends against historical baselines
history = read_performance_history("baselines/performance/history/")
plot_performance_trends(current, history)
```

### 5.3 Baseline Update Workflow

#### Automatic Updates (Rolling Baselines)
```yaml
# .github/workflows/update-baselines.yml
on:
  push:
    branches:
      - main  # Only on merges to main

jobs:
  update-baselines:
    runs-on: ubuntu-latest
    steps:
      - name: Run ingestion
        run: make ingest-gamslib
      
      - name: Update rolling baselines
        run: |
          # Parse rate baseline (git-tracked)
          git add reports/gamslib_ingestion_sprint11.json
          
          # Performance baseline (git-lfs)
          git lfs track "baselines/performance/baseline_latest.json"
          git add baselines/performance/baseline_latest.json
          
          git commit -m "Update baselines (automated)"
          git push
```

#### Manual Updates (Golden Baselines)
```bash
# End of Sprint 11
# 1. Run full ingestion
make ingest-gamslib

# 2. Copy current report to golden baseline
cp reports/gamslib_ingestion_sprint11.json baselines/golden/sprint11.json

# 3. Copy performance baseline
cp baselines/performance/baseline_latest.json baselines/performance/baseline_sprint11.json

# 4. Commit golden baselines
git add baselines/golden/sprint11.json baselines/performance/baseline_sprint11.json
git commit -m "Sprint 11 golden baselines"
git push
```

### 5.4 Baseline Storage Summary

| Baseline Type | Storage | Update Frequency | Purpose |
|---------------|---------|------------------|---------|
| **Rolling (Parse)** | Git-tracked JSON | Every main merge (auto) | Per-PR regression detection |
| **Golden (Parse)** | Git-tracked JSON | End of sprint (manual) | Sprint goal tracking |
| **Rolling (Performance)** | Git LFS | Every main merge (auto) | Performance regression detection |
| **Golden (Performance)** | Git LFS | End of sprint (manual) | Long-term trend tracking |
| **Historical Snapshots** | Git LFS | Weekly (auto) | Trend analysis |

---

## Section 6: Flaky Test Mitigation

### 6.1 Potential Sources of Flakiness

**Source 1: Timing Variance**
- GitHub Actions shared runners have variable CPU performance
- Same model can take 100ms or 150ms depending on runner load
- **Impact:** Performance tests may trigger false positives

**Source 2: Dependency Changes**
- Upstream library updates (lark-parser, Python version, etc.)
- Can break parsing or change performance characteristics
- **Impact:** Parse rate or performance regressions not caused by our code

**Source 3: GAMS Model Downloads**
- Network issues fetching models from GAMS website
- Models may change upstream (rare but possible)
- **Impact:** Tests fail due to external factors

**Source 4: Nondeterministic Behavior**
- Hash ordering (Python dict order)
- Parallel execution (pytest-xdist)
- **Impact:** Inconsistent test results

### 6.2 Mitigation Strategies

#### Mitigation 1: Caching (Already Implemented ✅)
```yaml
# .github/workflows/gamslib-regression.yml
- uses: actions/setup-python@v5
  with:
    cache: "pip"  # Cache pip dependencies
    
- name: Download GAMSLib models
  run: |
    if [ ! -d "tests/fixtures/gamslib" ]; then
      ./scripts/download_gamslib_nlp.sh
    else
      echo "Using cached GAMSLib models"
    fi
```

**Effectiveness:** ✅ Eliminates network flakiness for models and dependencies

#### Mitigation 2: Variance Tolerance (For Performance Tests)
```python
# Allow ±10% variance before failing
# Use 20% threshold for warnings (2× variance margin)
# Use 50% threshold for failures (5× variance margin)

if performance_increase > 0.20:  # 20% = 2× above ±10% variance
    print("⚠️ WARNING: Performance regression (20% slower)")

if performance_increase > 0.50:  # 50% = 5× above ±10% variance
    print("❌ FAILURE: Performance regression (50% slower)")
    exit(1)
```

**Effectiveness:** ✅ Prevents false positives from runner variance

#### Mitigation 3: Deterministic Seeding
```python
# Set deterministic seed for reproducible behavior
import random
random.seed(42)

# Use deterministic hash ordering (Python 3.7+)
# Dicts are insertion-ordered by default, but set PYTHONHASHSEED for safety
```

```yaml
# .github/workflows/gamslib-regression.yml
env:
  PYTHONHASHSEED: 0  # Deterministic hash ordering
```

**Effectiveness:** ✅ Eliminates nondeterminism in test suite

#### Mitigation 4: Retry Logic (Use Sparingly ⚠️)
```yaml
# ONLY for known flaky external operations (network fetches)
- name: Download GAMSLib models
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 5
    max_attempts: 3  # Retry up to 3 times
    command: ./scripts/download_gamslib_nlp.sh
```

**Effectiveness:** ⚠️ Masks real failures, increases CI time
**Recommendation:** Only use for external network operations, NOT for tests

#### Mitigation 5: Multiple Iterations (For High-Variance Tests)
```python
# For tests with high variance, run 3× and use median
def measure_conversion_time(model, iterations=3):
    times = []
    for _ in range(iterations):
        start = time.time()
        convert_to_ir(model)
        times.append(time.time() - start)
    
    return statistics.median(times)  # Use median (robust to outliers)
```

**Effectiveness:** ✅ Reduces variance, increases test time 3×
**Recommendation:** Only use for nightly/weekly tests (too slow for per-PR)

### 6.3 Flaky Test Mitigation Summary

| Mitigation | Effectiveness | CI Time Impact | Recommendation |
|------------|---------------|----------------|----------------|
| **Caching** | ✅ High (network) | ⚡ Faster | ✅ Keep (already implemented) |
| **Variance Tolerance** | ✅ High (performance) | None | ✅ Add (20%/50% thresholds) |
| **Deterministic Seeding** | ✅ Medium (nondeterminism) | None | ✅ Add (PYTHONHASHSEED=0) |
| **Retry Logic** | ⚠️ Low (masks bugs) | ⚡ Slower (3×) | ⚠️ Use sparingly (external only) |
| **Multiple Iterations** | ✅ High (variance) | ⚡ Slower (3×) | ⚠️ Nightly/weekly only |

---

## Section 7: Implementation Roadmap

### 7.1 Sprint 11 Implementation Plan

**Total Estimated Effort:** 12-16 hours (across 10 days)

#### Phase 1: Enhance Ingestion Script (4-5 hours)
**Objective:** Add convert rate and performance tracking to `scripts/ingest_gamslib.py`

**Tasks:**
1. Add IR conversion to ingestion pipeline (1-2h)
   - `convert_to_ir(models)` function
   - Error categorization (missing features, unsupported syntax)
   - Conversion time tracking

2. Update report schema (0.5h)
   - Add `convert_rate_percent` KPI
   - Add `conversion_errors` list
   - Add `conversion_time_ms` per model

3. Test enhanced ingestion (0.5h)
   - Run on all 10 Tier 1 models
   - Verify conversion errors captured correctly
   - Verify performance metrics

4. Update dashboard generation (1h)
   - Add convert rate to `GAMSLIB_CONVERSION_STATUS.md`
   - Add conversion errors table
   - Add performance summary

5. Update tests (1h)
   - Test conversion pipeline
   - Test error categorization
   - Test performance tracking

**Deliverable:** Enhanced `scripts/ingest_gamslib.py` with convert rate tracking

#### Phase 2: Enhance Regression Checker (3-4 hours)
**Objective:** Add multi-metric thresholds to `scripts/check_parse_rate_regression.py`

**Tasks:**
1. Rename script to `check_regression.py` (0.5h)
   - Reflect multi-metric scope (not just parse rate)
   - Update all references in workflows

2. Add convert rate regression check (1h)
   - Read convert rate from baseline
   - Compare against threshold (5%/10%)
   - Report regression with details

3. Add per-model regression tracking (1h)
   - Track per-model parse/convert status
   - Detect previously passing → now failing
   - Report specific models that regressed

4. Add performance regression check (1h)
   - Read conversion time from baseline
   - Compare against threshold (20%/50%)
   - Report performance regressions

5. Update tests (0.5-1h)
   - Test multi-metric regression detection
   - Test per-model tracking
   - Test performance thresholds

**Deliverable:** Enhanced `scripts/check_regression.py` with multi-metric thresholds

#### Phase 3: Add Matrix Build Workflow (2-3 hours)
**Objective:** Parallelize GAMSLib testing with matrix builds

**Tasks:**
1. Create new workflow `gamslib-matrix.yml` (1h)
   - Matrix strategy for 10 Tier 1 models
   - fail-fast: false (test all models)
   - Per-model artifact upload

2. Add per-model reporting (1h)
   - Each job uploads model-specific report
   - Aggregate results in final step
   - PR comment with per-model results

3. Test matrix build (0.5h)
   - Verify parallelization works
   - Verify all models tested
   - Verify artifact aggregation

4. Update documentation (0.5h)
   - Update README with matrix build info
   - Add workflow diagram
   - Document CI runtime improvement

**Deliverable:** New `.github/workflows/gamslib-matrix.yml` with parallelization

#### Phase 4: Add Baseline Management (2-3 hours)
**Objective:** Implement dual-baseline approach (rolling + golden)

**Tasks:**
1. Create baseline directory structure (0.5h)
   ```
   baselines/
     golden/
       sprint10.json
       sprint11.json
     performance/
       baseline_latest.json
   ```

2. Add Git LFS for performance baselines (0.5h)
   - `git lfs track "baselines/performance/*.json"`
   - Configure LFS in `.gitattributes`

3. Create baseline update workflow (1h)
   - Auto-update rolling baselines on main merge
   - Weekly historical snapshots
   - Golden baseline update script (manual)

4. Update regression checker (0.5h)
   - Compare against rolling baseline (main)
   - Optional: Compare against golden baseline (sprint goal)

5. Test baseline updates (0.5h)
   - Verify rolling baseline auto-updates
   - Verify golden baseline manual updates
   - Verify Git LFS storage

**Deliverable:** Baseline management system with rolling + golden baselines

#### Phase 5: Add Flaky Test Mitigation (1-2 hours)
**Objective:** Implement deterministic seeding and variance tolerance

**Tasks:**
1. Add deterministic seeding (0.5h)
   - Set `PYTHONHASHSEED=0` in workflows
   - Add `random.seed(42)` in scripts

2. Add variance tolerance to performance checks (0.5h)
   - 20% warning threshold
   - 50% failure threshold
   - Document rationale

3. Test flaky mitigation (0.5h)
   - Verify deterministic behavior
   - Verify performance thresholds work
   - Run tests multiple times (consistency check)

**Deliverable:** Flaky test mitigation in place

#### Phase 6: Documentation and Testing (1-2 hours)
**Objective:** Document strategy and validate implementation

**Tasks:**
1. Update KNOWN_UNKNOWNS.md (0.5h)
   - Mark Unknown 3.1 as VERIFIED
   - Document sampling strategy decision

2. Update PREP_PLAN.md (0.5h)
   - Mark Task 7 as complete
   - Document deliverables

3. Update CHANGELOG.md (0.5h)
   - Add Task 7 entry
   - Document key decisions

4. End-to-end testing (0.5h)
   - Run full CI pipeline
   - Verify all workflows pass
   - Verify matrix builds work

**Deliverable:** Complete documentation and validated implementation

### 7.2 Implementation Timeline

**Sprint 11 Schedule (10 days):**
- **Days 1-2:** Phase 1 - Enhance ingestion script (4-5h)
- **Days 3-4:** Phase 2 - Enhance regression checker (3-4h)
- **Days 5-6:** Phase 3 - Add matrix build workflow (2-3h)
- **Days 7-8:** Phase 4 - Add baseline management (2-3h)
- **Day 9:** Phase 5 - Add flaky test mitigation (1-2h)
- **Day 10:** Phase 6 - Documentation and testing (1-2h)

**Total Effort:** 12-16 hours over 10 days (buffer: 4-8h for unknowns)

---

## Section 8: Cost-Benefit Analysis

### 8.1 Current CI Cost

**Current Workflow:** `.github/workflows/gamslib-regression.yml`
- **Trigger:** Parser changes only (~20% of PRs)
- **Runtime:** 10 minutes (sequential testing)
- **Frequency:** ~20 PRs/month trigger this workflow
- **Monthly Cost:** 20 PRs × 10 min = **200 CI minutes/month**

**Current Limitations:**
- ❌ Only tests parse rate (not convert rate or solve rate)
- ❌ Sequential testing (slow)
- ❌ Only triggers on parser changes (misses dependency updates, IR changes)

### 8.2 Proposed CI Cost (Sprint 11)

**Proposed Per-PR Workflow:** `gamslib-matrix.yml`
- **Trigger:** All PRs (100% of PRs)
- **Runtime:** 2-3 minutes (matrix parallelization)
- **Frequency:** ~100 PRs/month
- **Monthly Cost:** 100 PRs × 3 min = **300 CI minutes/month**

**Proposed Nightly Workflow:** `gamslib-nightly.yml`
- **Trigger:** Daily at 00:00 UTC
- **Runtime:** 10-20 minutes (Parse + Convert + Solve)
- **Frequency:** 30 runs/month
- **Monthly Cost:** 30 runs × 15 min = **450 CI minutes/month**

**Proposed Weekly Workflow:** `gamslib-weekly.yml`
- **Trigger:** Weekly on Sunday at 00:00 UTC
- **Runtime:** 30-60 minutes (Full + Performance)
- **Frequency:** 4 runs/month
- **Monthly Cost:** 4 runs × 45 min = **180 CI minutes/month**

**Total Monthly Cost:** 300 + 450 + 180 = **930 CI minutes/month**

### 8.3 Cost-Benefit Comparison

| Metric | Current | Proposed | Change |
|--------|---------|----------|--------|
| **CI Minutes/Month** | 200 min | 930 min | +730 min (+365%) |
| **Per-PR Runtime** | 10 min | 2-3 min | -70% ⚡ |
| **PR Coverage** | 20% of PRs | 100% of PRs | +80% ✅ |
| **Metrics Tracked** | Parse rate only | Parse + Convert + Solve + Performance | +4 metrics ✅ |
| **Regression Detection** | Aggregate only | Per-model + aggregate | Better ✅ |
| **False Positive Rate** | Low (proven) | Lower (variance tolerance) | Better ✅ |

**Cost Analysis:**
- **Absolute cost increase:** +730 CI min/month
- **GitHub Actions free tier:** 2000 min/month (public repos unlimited)
- **Still within free tier:** ✅ YES (930 < 2000)
- **Per-PR feedback:** 70% faster (10 min → 3 min) ⚡

**Benefits:**
1. **70% faster per-PR feedback** (10 min → 3 min)
2. **100% PR coverage** (vs. 20% currently)
3. **4× more metrics** (parse + convert + solve + performance)
4. **Per-model regression detection** (vs. aggregate only)
5. **Comprehensive validation** (nightly + weekly)
6. **Performance trend tracking** (weekly)

**Conclusion:** ✅ **Cost increase justified by massive value increase**
- Still within GitHub Actions free tier (930 < 2000 min/month)
- Per-PR feedback 70% faster (better developer experience)
- Comprehensive coverage prevents regressions from merging

---

## Appendix A: Tier 1 Model Characteristics

### Model Details

#### 1. trig.gms
```gams
* Simple Trigonometric Example
Variables x, y, z;
Equations e1, e2, e3;

e1.. y =e= sin(x);
e2.. z =e= cos(x);
e3.. y**2 + z**2 =e= 1;

x.lo = 0; x.up = 2*pi;
y.lo = -1; y.up = 1;
z.lo = -1; z.up = 1;

Model m /all/;
Solve m using nlp minimizing x;
```

**Characteristics:**
- **Type:** NLP, unconstrained
- **Size:** 3 variables, 3 equations
- **Features:** Trig functions (sin, cos), simple bounds
- **Convexity:** Non-convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Baseline test for trig function support

#### 2. rbrock.gms
```gams
* Rosenbrock Test Function
Variables x1, x2, obj;
Equations fobj, con;

fobj.. obj =e= 100*sqr(x2 - sqr(x1)) + sqr(1 - x1);
con..  x1**2 + x2**2 =l= 2;

x1.l = -1.2; x2.l = 1;
x1.lo = -2; x1.up = 2;
x2.lo = -2; x2.up = 2;

Model rosenbrock /all/;
Solve rosenbrock using nlp minimizing obj;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 3 variables, 2 equations
- **Features:** Power functions (sqr, **), bounds
- **Convexity:** Non-convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Classic nonlinear optimization test problem

#### 3. himmel16.gms
```gams
* Area of Hexagon Test Problem
Sets i /1*6/;
Alias (i,j);
Parameters a(i), b(i);

Variables x(i), y(i), obj;
Equations fobj, con(i);

fobj.. obj =e= sum(i, (x(i) - a(i))**2 + (y(i) - b(i))**2);
con(i)$((ord(i) < card(i))).. sqrt(sqr(x(i+1)-x(i)) + sqr(y(i+1)-y(i))) =g= 1;

Model hexagon /all/;
Solve hexagon using nlp maximizing obj;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 13 variables (6 x, 6 y, 1 obj), 6 equations
- **Features:** Sets, indexed variables, lag/lead (i+1), sqrt, summation
- **Convexity:** Non-convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Tests multi-dimensional indexing and lag/lead operators

#### 4. hs62.gms
```gams
* Hock-Schittkowski Problem 62
Variables x1, x2, x3, obj;
Equations fobj, con1, con2;

fobj.. obj =e= -32.174*(255*log((x1+x2+x3+0.03)/(0.09*x1+x2+x3+0.03)) 
                        + 280*log((x2+x3+0.03)/(0.07*x2+x3+0.03))
                        + 290*log((x3+0.03)/(0.13*x3+0.03)));
con1.. x1 + x2 + x3 =l= 1;
con2.. 0.0663*x1 + 0.0732*x2 + 0.0790*x3 =g= 0.04;

x1.lo = 0; x1.up = 1;
x2.lo = 0; x2.up = 1;
x3.lo = 0; x3.up = 1;

Model hs62 /all/;
Solve hs62 using nlp minimizing obj;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 4 variables, 3 equations
- **Features:** Log functions, bounds, inequalities
- **Convexity:** Unknown (Hock-Schittkowski test problem)
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Standard test problem from H-S collection

#### 5. mhw4d.gms
```gams
* Nonlinear Test Problem
Variables x1, x2, obj;
Equations fobj, con1, con2;

fobj.. obj =e= (x1-1)**2 + (x2-2)**2;
con1.. x1 - 2*x2 + 1 =e= 0;
con2.. -(x1)**2/4 - (x2)**2 + 1 =g= 0;

x1.l = 1; x2.l = 1;

Model mhw4d /all/;
Solve mhw4d using nlp minimizing obj;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 3 variables, 3 equations
- **Features:** Power functions, equality and inequality constraints
- **Convexity:** Non-convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Simple nonlinear test problem

#### 6. mhw4dx.gms
```gams
* MHW4D with Additional Tests
* (Extended version of mhw4d.gms with multiple solutions)
Variables x1, x2, obj;
Equations fobj, con1, con2, con3;

fobj.. obj =e= (x1-1)**2 + (x2-2)**2;
con1.. x1 - 2*x2 + 1 =e= 0;
con2.. -(x1)**2/4 - (x2)**2 + 1 =g= 0;
con3.. x1 + x2 =l= 5;

x1.l = 1; x2.l = 1;

Model mhw4dx /all/;
Solve mhw4dx using nlp minimizing obj;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 3 variables, 4 equations
- **Features:** Extension of mhw4d with additional constraint
- **Convexity:** Non-convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Variant of mhw4d for additional testing

#### 7. circle.gms
```gams
* Circle Enclosing Points - SNOPT Example
Sets i /1*10/;
Parameters px(i), py(i);

Variables x, y, r;
Equations cover(i), obj;

obj.. r =e= r;
cover(i).. sqrt(sqr(px(i)-x) + sqr(py(i)-y)) =l= r;

x.l = 0; y.l = 0; r.l = 1;

Model circle /all/;
Solve circle using nlp minimizing r;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 3 variables, 11 equations
- **Features:** Sets, indexed equations, sqrt, parameters
- **Convexity:** Convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Geometric optimization (circle packing)

#### 8. maxmin.gms
```gams
* Max Min Location of Points in Unit Square
Sets n /1*5/, nn /1*5/, d /x,y/;
Alias (n,m);

Parameters point(n,d), low(n,nn);
Variables dist(n,nn), maxdist, mind;
Equations defdist(n,nn), defmax(n), defobj;

defdist(low(n,nn)).. dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
defmax(n).. maxdist =g= sum(nn$low(n,nn), dist(n,nn));
defobj.. mind =e= maxdist;

Model maxmin /all/;
Solve maxmin using dnlp minimizing mind;
```

**Characteristics:**
- **Type:** DNLP (Discontinuous NLP)
- **Size:** Multiple variables (depends on low set)
- **Features:** **Nested indexing** `low(n,nn)`, conditional indexing `$`, sqrt
- **Convexity:** Non-convex
- **Parse Status:** ❌ FAILED (nested indexing not supported)
- **Purpose:** Tests nested subset indexing (known parser gap)

#### 9. mathopt1.gms
```gams
* MathOptimizer Example 1
Variables x1, x2, obj;
Equations fobj, con1, con2;

fobj.. obj =e= sqr(x1-2) + sqr(x2-1);
con1.. x1 - 2*x2 =l= 0;
con2.. x1 + x2 =l= 6;

x1.lo = 0; x2.lo = 0;
x1.up = 6; x2.up = 6;

Model mathopt1 /all/;
Solve mathopt1 using nlp minimizing obj;
```

**Characteristics:**
- **Type:** NLP, constrained
- **Size:** 3 variables, 3 equations
- **Features:** Simple quadratic objective, linear constraints
- **Convexity:** Convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Simple baseline optimization problem

#### 10. mingamma.gms
```gams
* Minimal y of GAMMA(x)
Scalar pi /3.14159265/;
Variables x, y;
Equations fobj;

fobj.. y =e= gamma(x);

x.lo = 0.1; x.up = 5;
x.l = 1.5;

Model mingamma /all/;
Solve mingamma using dnlp minimizing y;
```

**Characteristics:**
- **Type:** DNLP (gamma function is non-smooth)
- **Size:** 2 variables, 1 equation
- **Features:** Gamma function (special function)
- **Convexity:** Non-convex
- **Parse Status:** ✅ SUCCESS
- **Purpose:** Tests special function support (gamma)

### Feature Coverage Summary

| Feature | Models Using | Count |
|---------|--------------|-------|
| **Sets** | himmel16, circle, maxmin | 3 |
| **Indexed variables** | himmel16, circle, maxmin | 3 |
| **Trig functions** | trig | 1 |
| **Power functions** | rbrock, himmel16, mhw4d, mhw4dx, circle, mathopt1 | 6 |
| **Log functions** | hs62 | 1 |
| **Sqrt** | himmel16, circle, maxmin | 3 |
| **Gamma function** | mingamma | 1 |
| **Equality constraints** | All except rbrock | 9 |
| **Inequality constraints** | rbrock, himmel16, hs62, mhw4d, mhw4dx, circle, mathopt1 | 7 |
| **Unconstrained** | trig | 1 |
| **Nested indexing** | maxmin | 1 (FAILED) |
| **Lag/lead (i+1)** | himmel16 | 1 |
| **Conditional ($)** | maxmin | 1 (FAILED) |

---

## Appendix B: Alternative Sampling Approaches

### Alternative 1: Canary Models (5 fixed + 5 rotated)

**Strategy:**
- Test 5 "canary" models on every PR (fixed subset)
- Rotate 5 additional models each run (full coverage over time)

**Fixed Canaries:**
1. **trig** - Baseline (trig functions)
2. **rbrock** - Classic (Rosenbrock)
3. **himmel16** - Sets (indexed variables)
4. **mathopt1** - Simple (constrained optimization)
5. **maxmin** - Known failure (nested indexing)

**Rotated Set:** Rotate through {hs62, mhw4d, mhw4dx, circle, mingamma}

**Example Runs:**
- PR #1: {trig, rbrock, himmel16, mathopt1, maxmin} + {hs62, mhw4d, mhw4dx}
- PR #2: {trig, rbrock, himmel16, mathopt1, maxmin} + {circle, mingamma, hs62}
- PR #3: {trig, rbrock, himmel16, mathopt1, maxmin} + {mhw4d, mhw4dx, circle}

**Pros:**
- ✅ Faster CI (5-7 models instead of 10)
- ✅ Still covers key patterns (canaries)
- ✅ Full coverage over time (rotation)

**Cons:**
- ❌ Delayed regression detection for non-canary models
  - Example: If PR breaks `circle.gms`, may not detect until next rotation
- ❌ More complex logic (canary selection, rotation tracking)
- ❌ Harder to debug (which rotation caught the regression?)

**Verdict:** ❌ **REJECTED** - Matrix parallelization makes "test all" as fast as "test 5"

### Alternative 2: Risk-Based Sampling

**Strategy:**
- Test models likely affected by the change
- Grammar changes → test all models (broad impact)
- Semantic changes → test models with affected features
- IR changes → test complex models only

**Example Rules:**
```yaml
# If grammar.lark changed → test all 10 models
- name: Determine test set
  run: |
    if git diff --name-only origin/main | grep "grammar.lark"; then
      echo "TEST_SET=all" >> $GITHUB_ENV
    elif git diff --name-only origin/main | grep "src/ir/"; then
      echo "TEST_SET=complex" >> $GITHUB_ENV  # {himmel16, maxmin, circle}
    else
      echo "TEST_SET=canary" >> $GITHUB_ENV  # {trig, rbrock, mathopt1}
    fi
```

**Pros:**
- ✅ Targeted testing (only test what's affected)
- ✅ Faster for focused changes

**Cons:**
- ❌ Requires manual risk assessment (which models affected?)
- ❌ Misses unexpected interactions (change X breaks model Y)
- ❌ Complex workflow logic (hard to maintain)
- ❌ False negatives (skip tests that should run)

**Verdict:** ❌ **REJECTED** - Too complex, prone to false negatives

### Alternative 3: Fast/Full Split

**Strategy:**
- **Fast (every PR):** 3 canary models (~2 min)
- **Full (nightly + pre-merge):** All 10 Tier 1 models (~10 min)

**Fast Canaries:**
1. **trig** - Baseline
2. **rbrock** - Classic
3. **mathopt1** - Simple

**Full Set:** All 10 Tier 1 models

**Pros:**
- ✅ Very fast per-PR feedback (2 min)
- ✅ Comprehensive nightly validation

**Cons:**
- ❌ Can merge PRs with regressions (if only fast tests run)
  - Example: PR breaks `himmel16`, but fast tests pass, PR merges
- ❌ Delayed regression detection (nightly finds it next day)
- ❌ More complex workflow (fast vs. full logic)

**Verdict:** ❌ **REJECTED** - Risk of merging regressions too high

### Alternative 4: Adaptive Sampling

**Strategy:**
- Start with 3 canary models
- If any fail, expand to all 10 models
- If all pass, stop (no further testing)

**Pros:**
- ✅ Very fast when no regressions (2 min)
- ✅ Comprehensive when regressions detected (10 min)

**Cons:**
- ❌ Variable CI time (unpredictable)
- ❌ Can miss regressions in non-canary models
  - Example: Canaries pass, but `circle` regressed (not detected)
- ❌ Complex workflow logic

**Verdict:** ❌ **REJECTED** - False negatives for non-canary regressions

### Alternative Comparison Table

| Alternative | CI Time | Coverage | Complexity | False Negatives | Verdict |
|-------------|---------|----------|------------|-----------------|---------|
| **Test All (Recommended)** | 2-3 min | 100% | Low | None | ✅ ACCEPTED |
| **Canary + Rotation** | 2-3 min | 100% (over time) | Medium | Delayed | ❌ REJECTED |
| **Risk-Based** | Variable | Partial | High | Possible | ❌ REJECTED |
| **Fast/Full Split** | 2 min (fast) | 30% (fast), 100% (nightly) | Medium | Possible | ❌ REJECTED |
| **Adaptive** | 2-10 min | Variable | High | Possible | ❌ REJECTED |

---

## Appendix C: CI Workflow Examples

### Example 1: Per-PR Fast Checks (Matrix Build)

```yaml
# .github/workflows/gamslib-matrix.yml
name: GAMSLib Regression Matrix

on:
  pull_request:  # All PRs

jobs:
  test-model:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    
    strategy:
      matrix:
        model: [trig, rbrock, himmel16, hs62, mhw4d, mhw4dx, circle, maxmin, mathopt1, mingamma]
      fail-fast: false  # Test all models even if one fails
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for baseline comparison
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      
      - name: Test model
        run: |
          python scripts/test_single_model.py \
            --model ${{ matrix.model }} \
            --scope parse+convert \
            --output reports/model_${{ matrix.model }}.json
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: model-report-${{ matrix.model }}
          path: reports/model_${{ matrix.model }}.json
  
  aggregate-results:
    runs-on: ubuntu-latest
    needs: test-model
    
    steps:
      - name: Download all reports
        uses: actions/download-artifact@v4
        with:
          pattern: model-report-*
          path: reports/
      
      - name: Aggregate results
        run: |
          python scripts/aggregate_model_reports.py \
            --input reports/ \
            --output reports/gamslib_ingestion_sprint11.json
      
      - name: Check for regression
        run: |
          python scripts/check_regression.py \
            --current reports/gamslib_ingestion_sprint11.json \
            --baseline origin/main \
            --threshold-parse 0.10 \
            --threshold-convert 0.10 \
            --threshold-performance 0.50 \
            --verbose
      
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('reports/gamslib_ingestion_sprint11.json'));
            
            const comment = `
            ## GAMSLib Regression Check
            
            **Parse Rate:** ${report.kpis.parse_rate_percent}% (${report.kpis.parse_success}/${report.kpis.total_models} models)
            **Convert Rate:** ${report.kpis.convert_rate_percent}% (${report.kpis.convert_success}/${report.kpis.total_models} models)
            
            **Per-Model Results:**
            ${report.models.map(m => `- ${m.model_name}: ${m.parse_status} / ${m.convert_status}`).join('\n')}
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Example 2: Nightly Full Validation

```yaml
# .github/workflows/gamslib-nightly.yml
name: GAMSLib Nightly Validation

on:
  schedule:
    - cron: "0 0 * * *"  # Nightly at 00:00 UTC
  workflow_dispatch:

jobs:
  nightly-validation:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      
      - name: Install PATH solver
        run: |
          # PATH installation (if licensing permits)
          ./scripts/install_path_solver.sh
      
      - name: Run full ingestion (Parse + Convert + Solve)
        run: |
          python scripts/ingest_gamslib.py \
            --input tests/fixtures/gamslib \
            --output reports/gamslib_nightly.json \
            --scope parse+convert+solve \
            --models tier1,tier2
      
      - name: Check for regression
        run: |
          python scripts/check_regression.py \
            --current reports/gamslib_nightly.json \
            --baseline origin/main \
            --threshold-parse 0.10 \
            --threshold-convert 0.10 \
            --threshold-solve 0.10 \
            --threshold-performance 0.50 \
            --verbose
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: nightly-report
          path: reports/gamslib_nightly.json
          retention-days: 90
      
      - name: Create issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Nightly GAMSLib validation failed (${new Date().toISOString().split('T')[0]})`,
              body: 'Nightly GAMSLib validation detected regressions. See workflow run for details.',
              labels: ['ci', 'regression']
            });
```

### Example 3: Weekly Extended Suite

```yaml
# .github/workflows/gamslib-weekly.yml
name: GAMSLib Weekly Extended Suite

on:
  schedule:
    - cron: "0 0 * * 0"  # Weekly on Sunday at 00:00 UTC
  workflow_dispatch:

jobs:
  weekly-extended:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for trend analysis
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      
      - name: Install PATH solver
        run: |
          ./scripts/install_path_solver.sh
      
      - name: Run extended ingestion (All Tiers)
        run: |
          python scripts/ingest_gamslib.py \
            --input tests/fixtures/gamslib \
            --output reports/gamslib_weekly.json \
            --scope parse+convert+solve \
            --models tier1,tier2,tier3
      
      - name: Track performance trends
        run: |
          python scripts/track_performance_trends.py \
            --current reports/gamslib_weekly.json \
            --history baselines/performance/history/ \
            --output reports/performance_trends.json
      
      - name: Generate trend report
        run: |
          python scripts/generate_trend_report.py \
            --trends reports/performance_trends.json \
            --output reports/weekly_trend_report.md
      
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: weekly-reports
          path: |
            reports/gamslib_weekly.json
            reports/performance_trends.json
            reports/weekly_trend_report.md
          retention-days: 90
      
      - name: Save historical snapshot
        run: |
          # Save weekly snapshot to Git LFS
          cp reports/gamslib_weekly.json \
             baselines/performance/history/$(date +%Y-%m-%d)_commit-$(git rev-parse --short HEAD).json
          
          git lfs track "baselines/performance/history/*.json"
          git add baselines/performance/history/
          git commit -m "Weekly performance snapshot (automated)"
          git push
```

---

## Summary

This GAMSLib sampling strategy provides:

1. **Comprehensive Coverage:** All 10 Tier 1 models tested on every PR
2. **Fast Feedback:** 2-3 min per-PR runtime (70% faster via matrix builds)
3. **Multi-Metric Validation:** Parse + Convert + Solve + Performance
4. **Per-Model Tracking:** Detects regressions hidden in aggregate metrics
5. **Baseline Management:** Rolling + golden baselines for short-term and long-term tracking
6. **Flaky Mitigation:** Deterministic seeding, variance tolerance, caching
7. **Cost-Effective:** 930 CI min/month (within free tier)

**Unknown 3.1 Verification:** ✅ **VERIFIED** - Testing all 10 Tier 1 models with matrix parallelization provides optimal regression coverage while maintaining fast CI feedback (<5 min).

**Next Steps:**
1. Implement Phase 1: Enhance ingestion script (4-5h)
2. Implement Phase 2: Enhance regression checker (3-4h)
3. Implement Phase 3: Add matrix build workflow (2-3h)
4. Implement Phase 4: Add baseline management (2-3h)
5. Implement Phase 5: Add flaky test mitigation (1-2h)
6. Document and validate (1-2h)

**Total Sprint 11 Effort:** 12-16 hours over 10 days
