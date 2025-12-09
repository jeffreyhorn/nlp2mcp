# Performance Trends

Historical performance metrics across sprints, tracking parse rate, convert rate, test execution time, and simplification effectiveness.

## Sprint Summary Table

| Sprint | Parse Rate | Convert Rate | Test Time | Term Reduction | Key Achievements |
|--------|-----------|--------------|-----------|----------------|------------------|
| Sprint 7 | 20% (2/10) | 100% | ~15s | N/A | Initial parser foundation |
| Sprint 8 | 40% (4/10) | 88% | ~24s | N/A | Option statements, indexed assignments |
| Sprint 9 | 60% (6/10) | 90% | ~29s | N/A | Function calls, error messages |
| Sprint 10 | 90% (9/10) | 90% | ~16s | ~15% est. | Convexity, multiple models, equation attributes |
| Sprint 11 | 100% (10/10) | 90% | ~17s | 26.19% | Aggressive simplification, CSE, maxmin.gms unlock |
| Sprint 12 | 100% (10/10) | 90% | ~24s | 26.19% | JSON diagnostics, dashboard, tier 2 analysis |

## Metric Definitions

### Parse Rate
- **Definition:** Percentage of GAMSLib Tier 1 models that successfully parse to AST
- **Target:** 100% for Tier 1 (achieved Sprint 11)
- **Measurement:** `make ingest-gamslib`

### Convert Rate
- **Definition:** Percentage of parsed models that successfully convert to MCP GAMS
- **Current Blocker:** himmel16.gms fails due to `IndexOffset not yet supported` (circular lag `i++`)
- **Target:** 100% (stretch)
- **Measurement:** `scripts/measure_parse_rate.py --all-metrics`

### Test Time
- **Definition:** Wall clock time for `make test` (parallel execution)
- **Budget:** <30s for fast tests
- **Trend:** Optimized in Sprint 10 with pytest-xdist parallel execution

### Term Reduction
- **Definition:** Average percentage reduction in expression terms after simplification
- **Target:** ≥20% on ≥50% of models (achieved Sprint 11: 26.19% on 70% of models)
- **Measurement:** `scripts/measure_simplification.py --model-set tier1`

## Detailed Sprint Metrics

### Sprint 12 (Current)

**Parse Rate:** 100% (10/10 Tier 1 models)
**Convert Rate:** 90% (9/10 models, himmel16.gms fails at IR conversion)
**Test Time:** ~24s (2279 tests)
**Term Reduction:** 26.19% average

| Model | Parse | Convert | Term Reduction | Notes |
|-------|-------|---------|----------------|-------|
| circle.gms | ✅ | ✅ | 25.0% | |
| himmel16.gms | ✅ | ❌ | 10.0% | IndexOffset not supported |
| hs62.gms | ✅ | ✅ | 30.0% | |
| mathopt1.gms | ✅ | ✅ | 22.2% | |
| maxmin.gms | ✅ | ✅ | 0.0% | Pre-simplified |
| mhw4d.gms | ✅ | ✅ | 52.6% | High factorization |
| mhw4dx.gms | ✅ | ✅ | 52.6% | High factorization |
| mingamma.gms | ✅ | ✅ | 0.0% | Pre-simplified |
| rbrock.gms | ✅ | ✅ | 25.0% | |
| trig.gms | ✅ | ✅ | 44.4% | Trigonometric simplification |

### Sprint 11

**Parse Rate:** 100% (10/10 Tier 1 models)
**Convert Rate:** 90%
**Test Time:** ~17s (1730 tests)
**Term Reduction:** 26.19% average (first measurement)

**Key Achievements:**
- Unlocked maxmin.gms (final Tier 1 model)
- Implemented 11 transformation functions
- 3 CSE variants (extract, hoist, propagate)
- Established CI regression guardrails

### Sprint 10

**Parse Rate:** 90% (9/10 Tier 1 models)
**Convert Rate:** 90%
**Test Time:** ~16s (optimized with pytest-xdist)
**Term Reduction:** ~15% estimated

**Key Achievements:**
- Convexity heuristics
- Multiple model definitions
- Equation attributes
- UX improvements

### Sprint 9

**Parse Rate:** 60% (6/10 Tier 1 models)
**Convert Rate:** 90%
**Test Time:** ~29s

**Key Achievements:**
- Function calls in assignments
- Error line numbers and source context
- Partial parse metrics

### Sprint 8

**Parse Rate:** 40% (4/10 Tier 1 models)
**Convert Rate:** 88%
**Test Time:** ~24s

**Key Achievements:**
- Option statements
- Indexed assignments
- Test fixture strategy

## Trend Charts

### Parse Rate Progression

```
100% |                         ██████████
 90% |                   ██████
 80% |
 70% |
 60% |             ██████
 50% |
 40% |       ██████
 30% |
 20% | ██████
 10% |
  0% +-----------------------------------
      S7    S8    S9    S10   S11   S12
```

### Test Time Evolution

```
30s |             ██
25s |       ██              ██
20s |
15s | ██              ██  ██
10s |
 5s |
 0s +-----------------------------------
      S7    S8    S9    S10   S11   S12
```

*Note: Sprint 10 optimized with parallel test execution*

## Automation

### Update Script

Run after each sprint to capture metrics:

```bash
# Collect current metrics
python scripts/measure_parse_rate.py --all-metrics --output metrics.json

# Update trends document (manual)
# Add row to Sprint Summary Table with:
# - Parse rate from metrics.json
# - Convert rate from metrics.json
# - Test time from `make test`
# - Term reduction from baselines/simplification/
```

### CI Integration

Metrics are automatically collected in CI:
- Parse rate: `.github/workflows/gamslib-regression.yml`
- Performance: `.github/workflows/performance-check.yml`
- Diagnostics: `.github/workflows/ci.yml` (artifacts)

## Related Documentation

- [Simplification Benchmarks](../SIMPLIFICATION_BENCHMARKS.md)
- [Multi-Metric Baselines](../../baselines/multi_metric/README.md)
- [Dashboard](../DASHBOARD.md)
- [Interactive Dashboard](../dashboard.html)
