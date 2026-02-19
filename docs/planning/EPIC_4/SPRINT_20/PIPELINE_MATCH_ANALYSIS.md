# Sprint 20 Prep Task 6: Full Pipeline Match Divergence Analysis

**Date:** 2026-02-19
**Branch:** `planning/sprint20-task6`
**Status:** COMPLETE

## Background

Sprint 19 final state:
- 25 models solve successfully (PATH model status 1)
- 9 full pipeline matches: ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport
- 16 models solve but fail the pipeline match check (15 mismatch + 1 comparison error)

This document classifies each of the 16 divergences and predicts the impact of the Sprint 20
`.l` initialization emission fix.

---

## Section 1: Per-Model Classification Table

| Model | NLP Obj | MCP Obj | Obj Gap % | Has .l | Has .scale | Divergence Type | Likely Cause |
|-------|---------|---------|-----------|--------|------------|-----------------|--------------|
| chem | -47.71 | -47.71 | 0.001% | No | No | Tolerance | rtol too tight (abs_diff=5e-4) |
| dispatch | 7.955 | 7.955 | 0.005% | No | No | Tolerance | rtol too tight (abs_diff=4e-4) |
| hhmax | 13.929 | 13.929 | 0.001% | No | No | Tolerance | rtol too tight (abs_diff=2e-4) |
| mhw4d | 27.872 | 27.872 | 0.0004% | Yes | No | Tolerance | rtol too tight (abs_diff=1e-4) |
| mhw4dx | 27.872 | 27.872 | 0.0004% | Yes | No | Tolerance | rtol too tight (abs_diff=1e-4) |
| abel | 225.19 | 1013691.67 | 99.98% | No* | No | Missing .l init | Expr-based: `x.l(n,k)=xinit(n)`, `u.l(m,k)=uinit(m)` dropped by IR |
| chakra | 179.13 | 153.24 | 14.46% | No* | No | Missing .l init | Expr-based: `y.l(t)=y0*(1.06)**(ord(t)-1)` formula; 3 vars |
| alkyl | -1.765 | -1.894 | 6.81% | Yes | No | Multiple optima | NLP locally optimal; different stationary point |
| himmel16 | 0.675 | ~0 | 100% | Yes | No | Multiple optima | NLP locally optimal; .l correctly emitted; PATH finds trivial KKT point |
| mathopt1 | 1.0 | ~0 | 100% | Yes | No | Multiple optima | Non-convex global opt; .l emitted; PATH finds different stationary point |
| process | 2410.83 | 1161.34 | 51.83% | Yes | No | Multiple optima | NLP locally optimal; .l emitted; PATH finds different local opt |
| trig | 0.0 | 1.93 | 100% | Yes | No | Multiple optima | Non-convex global opt; .l emitted; PATH finds non-minimum KKT point |
| aircraft | 1566.04 | 7332.5 | 78.64% | No | No | LP multi-model | Two solve statements (alloc1, alloc2); IR picks alloc2, NLP reference is alloc1 |
| apl1p | 24515.65 | 23700.15 | 3.33% | No | No | LP multi-model | `solve apl1p` in apl1pca.gms; apl1p itself has no .l inits; PATH finds different LP basis |
| apl1pca | 15902.49 | 23700.15 | 32.90% | No | No | LP multi-model | `solve apl1p` in apl1pca.gms; model set differs from NLP reference |
| port | 0.2984 | null | N/A | No | No | Obj not tracked | LP model; MCP objective variable not captured in output |

**Notes:**
- `Has .l`: Yes = IR captures ≥1 `.l` constant init AND it is emitted in MCP file
- No* = model has `.l` assignments in source but they are expression-based (param/formula); IR silently drops them
- None of the 16 non-matching models (including port) use `.scale`

---

## Section 2: Divergence Type Summary

| Type | Count | Models |
|------|-------|--------|
| **Tolerance too tight** | 5 | chem, dispatch, hhmax, mhw4d, mhw4dx |
| **Missing .l init (expr-based)** | 2 | abel, chakra |
| **Multiple optima / different local KKT** | 5 | alkyl, himmel16, mathopt1, process, trig |
| **LP multi-model / wrong model selected** | 3 | aircraft, apl1p, apl1pca |
| **Obj not tracked** | 1 | port |
| **Total** | **16** | |

---

## Section 3: Predicted Impact of Sprint 20 `.l` Emission Fix

The `.l` emission fix (Task 1 in Sprint 20) will emit expression-based `.l` assignments that
are currently dropped at `parser.py:3562`.

### Models directly helped:

| Model | Fix Type | Confidence | Notes |
|-------|----------|------------|-------|
| abel | Emit `x.l(n,k)=xinit(n)`, `u.l(m,k)=uinit(m)` | High | Param-based expressions; xinit/uinit are known at emission time |
| chakra | Emit `y.l(t)=y0*(1.06)**(ord(t)-1)` and derived | Medium | Formula-based with `ord(t)`; requires expression IR |

### Models NOT helped by `.l` fix:

| Model | Reason |
|-------|--------|
| himmel16, mathopt1, process, trig, alkyl | `.l` already emitted correctly; PATH finds different KKT point |
| chem, dispatch, hhmax, mhw4d, mhw4dx | Tolerance issue, not initialization |
| aircraft, apl1pca | Wrong model selected (multi-model LP) |
| apl1p | No `.l` in source; LP basis selection issue |
| port | MCP obj tracking missing for LP |

### Predicted match count after `.l` fix:

- Current: **9 matches**
- If abel fix succeeds: +1 → **10 matches**
- If chakra fix succeeds: +1 → **11 matches**
- Conservative estimate: **+1 to +2** new matches (9 → 10 or 11)

The `.l` fix will NOT close the gap to 25 — the remaining 14 divergences have structural causes
(multiple optima, LP model selection, tolerance, obj tracking) that require separate workstreams.

---

## Section 4: Tolerance Analysis

**Current tolerances:** `atol=1e-8`, `rtol=1e-6`

**Comparison formula:** `|nlp_obj - mcp_obj| <= atol + rtol * max(|nlp_obj|, |mcp_obj|)`

The 5 near-match models fail only because the tolerance is very tight:

| Model | Abs Diff | Required rtol to pass | Current rtol |
|-------|----------|-----------------------|--------------|
| mhw4d | 1.0e-4 | 3.6e-6 | 1e-6 |
| mhw4dx | 1.0e-4 | 3.6e-6 | 1e-6 |
| hhmax | 2.0e-4 | 1.4e-5 | 1e-6 |
| chem | 5.0e-4 | 1.1e-5 | 1e-6 |
| dispatch | 4.0e-4 | 5.0e-5 | 1e-6 |

All 5 would pass with `rtol=1e-4`. These are **numerical noise** differences (PATH vs IPOPT
solver precision), not structural mismatches. Loosening `rtol` to `1e-4` would add 5 matches,
bringing the total to **14–16 matches** (depending on whether 0, 1, or both of abel/chakra also fix).

**Recommendation for Sprint 20:** Consider raising default `rtol` to `1e-4` for the pipeline
comparison as a separate improvement — but this is separate from the `.l` emission fix.

**Models within 5% gap (excluding near-matches):**

| Model | Gap % | Would pass at rtol=5% |
|-------|-------|-----------------------|
| apl1p | 3.33% | Yes (if rtol raised to 0.05) |
| alkyl | 6.81% | No (requires ~7%) |

apl1p is within 5% of reference and could pass with `rtol=0.05`, but this is too loose for
a meaningful pipeline check.

---

## Section 5: Golden-File Test Coverage for 9 Matching Models

The 9 currently-matching models are:
**ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport**

**Coverage status:**

| Model | Golden file test | Integration test | Solve test |
|-------|-----------------|-----------------|------------|
| ajax | No | No | No |
| blend | No | No | No |
| demo1 | No | No | No |
| himmel11 | No | No | No |
| house | No | No | No |
| mathopt2 | No | No | No |
| prodmix | No | No | No |
| rbrock | No | Parse-only (`test_rbrock_gms_parses`) | No |
| trnsport | No | No | No (catalog/DB tests only) |

**None of the 9 matching models have end-to-end golden-file or solve-level test coverage.**

The existing `tests/e2e/test_golden.py` only covers `simple_nlp.gms`, `indexed_balance.gms`,
and `scalar_nlp.gms` (synthetic examples, not gamslib models).

**Regression risk assessment:**
- None of the 9 models use IndexOffset, `.scale`, dollar conditions, or other patterns
  targeted by Sprint 20 workstreams.
- Risk of regression from Sprint 20 changes is **low** but not zero — any grammar/parser
  change could affect these models.
- Recommendation: add golden-file tests for the 9 matching models as a Sprint 20 task
  to guard against regression.

---

## Section 6: KKT Formulation Review Candidates

Models with >100% relative gap (MCP finds a solution far from the NLP reference) warrant
review to confirm the KKT system is correctly formulated:

| Model | NLP Obj | MCP Obj | Gap % | Notes |
|-------|---------|---------|-------|-------|
| abel | 225.19 | 1,013,691.67 | 99.98% | No warm start; PATH finds spurious stationary point |
| himmel16 | 0.675 | ~0 | 100% | .l emitted; maximization; PATH finds zero-area solution |
| mathopt1 | 1.0 | ~0 | 100% | Global opt (LGO model); PATH finds local min |
| trig | 0.0 | 1.93 | 100% | Global opt (LGO model); PATH finds local max |

For himmel16, mathopt1, and trig: the KKT formulation appears correct (PATH solves to a
valid KKT point) but these are non-convex problems where PATH finds a non-global stationary
point. This is expected behavior, not a formulation bug.

For abel: the 4500x gap strongly suggests a warm-start dependency. With correct `.l` inits,
PATH should find the same local optimum as IPOPT.

---

## Section 7: `.scale` Analysis

**No model in the non-matching set uses `.scale`.** All 15 mismatch models were checked for
`varname.scale` assignments in their raw `.gms` source — none found. (port has no `.gms`-level
`.scale` usage either.)

`.scale` is therefore **not a primary blocker** for any of the 16 divergences.

---

## Appendix: Data Sources

- `data/gamslib/gamslib_status.json` — solve status, objective values, comparison results
- `data/gamslib/raw/*.gms` — original GAMS source for `.l` / `.scale` inspection
- `data/gamslib/mcp/*.gms` — generated MCP files for `.l` emission verification
- `scripts/gamslib/test_solve.py:78-79` — `DEFAULT_RTOL=1e-6`, `DEFAULT_ATOL=1e-8`
- `src/ir/parser.py:3568-3571` — `_handle_assign` where expression-based `.l` is dropped (early `return` when `is_variable_bound` and `_extract_constant` raises)
