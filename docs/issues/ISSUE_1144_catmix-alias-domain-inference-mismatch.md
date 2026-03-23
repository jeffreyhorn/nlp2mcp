# catmix: Alias Domain Inference Regression (model_infeasible)

**GitHub Issue:** [#1144](https://github.com/jeffreyhorn/nlp2mcp/issues/1144)
**Status:** OPEN
**Severity:** High — model_infeasible (was model_optimal)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** catmix

---

## Problem Summary

The catmix model (Catalyst Mixing, COPS benchmark SEQ=242) regressed from
`model_optimal` to `model_infeasible` due to the interaction between the
alias pattern and the `skip_lead_lag_inference` change from PR #1076.

The model uses `Alias(nh, i)` with lead-indexed equation domains:

```gams
Set nh /0*100/;
Alias(nh, i);
ode1(nh(i+1)).. x1(i+1) =E= x1(i) + ...
ode2(nh(i+1)).. x2(i+1) =E= x2(i) + ...
```

| Model | NLP Objective | MCP Status | Notes |
|-------|--------------|-----------|-------|
| catmix | -0.048 | model_infeasible | 101 INFES equations |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/catmix.gms -o /tmp/catmix_mcp.gms
gams /tmp/catmix_mcp.gms lo=2
# Expected: MODEL STATUS 5 (Locally Infeasible), 101 INFES
```

---

## Root Cause Analysis

The regression was caused by PR #1076 (Sprint 22 Day 7 WS3, whouse fix):

### Before PR #1076 (correct)
```gams
ode1(i)$(ord(i) <= card(i) - 1).. x1(i+1) =E= x1(i) + ...
ode2(i)$(ord(i) <= card(i) - 1).. x2(i+1) =E= x2(i) + ...
nu_ode1.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;
nu_ode2.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;
```

### After PR #1076 (broken)
```gams
ode1(i).. x1(i+1) =E= x1(i) + ...  -- no domain restriction!
ode2(i).. x2(i+1) =E= x2(i) + ...  -- no domain restriction!
```

The `$(ord(i) <= card(i) - 1)` guard was removed from the equality equations,
and the corresponding `.fx` fixups for the multipliers were also removed.

### Why This Happens

1. The IR parser stores `ode1(nh(i+1))` as `domain=('i',), condition=None` —
   the `nh(i+1)` domain qualifier's lead offset is lost.

2. Previously, the emitter inferred the lead/lag domain condition from
   `IndexOffset` references in the equation body.

3. PR #1076 added `skip_lead_lag_inference=True` for all original equality
   equations to fix the whouse model, which had the opposite problem (lag
   references that GAMS evaluates as 0 rather than skipping).

4. The blanket `skip_lead_lag_inference` doesn't distinguish between:
   - **whouse-style**: lag in body only — equation generated for all elements
   - **catmix-style**: lead in domain qualifier — equation genuinely skipped

### Impact

With equations generated for all 101 elements (instead of 100), the equation
`ode1(100)` references `x1(101)` which doesn't exist, creating infeasible
constraints. All stationarity equations and complementarity conditions are
affected.

---

## Suggested Fix

**Option A (targeted)**: Restore lead/lag inference for equations whose head
domain contained a lead/lag qualifier. This requires the parser to record
whether the equation head had an IndexOffset.

**Option B (proper fix)**: Enhance the IR to store the full domain qualifier
with lead/lag information (e.g., `domain=('i+1',)` or `IndexOffset('i', 1)`).
The emitter would then generate the correct domain condition.

**Option C (pragmatic)**: Restore lead/lag inference for equations with lead
offsets (positive, like `i+1`) while keeping `skip_lead_lag_inference` for
equations with only lag offsets (negative, like `t-1`).

---

## Files

- `src/ir/parser.py` — `_domain_list()`, `_handle_eqn_def_domain()` — domain qualifier lost
- `src/emit/equations.py:469` — `skip_lead_lag_inference=True` for all equalities
- `data/gamslib/raw/catmix.gms` — Source model
