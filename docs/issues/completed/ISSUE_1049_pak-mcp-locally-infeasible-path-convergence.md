# pak: MCP Locally Infeasible — Fixed-Index Jacobian Guard Missing

**GitHub Issue:** [#1049](https://github.com/jeffreyhorn/nlp2mcp/issues/1049)
**Status:** FIXED
**Severity:** Medium
**Date:** 2026-03-11 (opened), 2026-04-09 (fixed)
**Affected Models:** pak (and any model where a variable appears in a constraint with a fixed literal index)

---

## Problem Summary

The pak model generated an MCP that was MODEL STATUS 5 (Locally Infeasible). Deep investigation on Sprint 24 Day 11 revealed the root cause: a missing `$(sameas(...))` guard in the stationarity equation builder for the indexed constraint path.

---

## Root Cause (Bug 4 — Fixed 2026-04-09)

### Fixed-Index Jacobian Guard Missing in Indexed Constraint Path

**Location:** `src/kkt/stationarity.py:_add_indexed_jacobian_terms()` (line ~4812)

When a variable like `v(t,j)` appears in an indexed constraint with a **fixed literal index** — e.g., `tgap(t).. f(t) = m(t) - e(t) - v(t,"traded")` — the stationarity builder must only include the Jacobian contribution for the specific index value (`j='traded'`). However, the code was adding the multiplier term for **all** values of `j`.

**Generated (wrong):**
```gams
stat_v(t,j).. (-1)*nu_gnpd(t) + nu_tgap(t) + lam_capb(t,j) - piL_v(t,j) =E= 0;
```

**Correct (fixed):**
```gams
stat_v(t,j).. (-1)*nu_gnpd(t) + nu_tgap(t)$(sameas(j,'traded')) + lam_capb(t,j) - piL_v(t,j) =E= 0;
```

The scalar constraint path already had this guard logic (Issue #767/#764, lines 4845-4848), but the indexed constraint path was missing it. The fix adds the same `_build_sameas_guard()` call for indexed constraints, but only when the variable has MORE dimensions than the constraint domain (indicating fixed literal indices, not domain subset restrictions).

### Verification

Residual analysis at the LP optimal solution confirmed:
- All 9 stationarity equations except `stat_v` had zero residuals at the LP solution
- `stat_v(t,'non-traded')` had residuals up to -1.687 due to the spurious `nu_tgap(t)` term
- After the fix: MODEL STATUS 1 (Optimal), w = 1075.547 (matches LP optimal exactly)

---

## Previous Bugs (All Fixed Before This Investigation)

### Bug 1: Subset/Superset Domain Mismatch (Fixed in Sprint 24)
Multipliers from subset-domain constraints were sum-wrapped instead of direct. Now uses `sum(t$(sameas(t,te)), ...)` pattern.

### Bug 2: First-Instance Gradient Template (Fixed in Sprint 24)
Gradient used first instance as template; now uses sameas pattern for all instances.

### Bug 3: Quoted String Literal Index (Fixed in Sprint 24)
`gnp("1985")` stored index with quotes, preventing differentiation match.

---

## Fix Applied

**File:** `src/kkt/stationarity.py`
**Change:** Added `_build_sameas_guard()` call in the indexed constraint path of `_add_indexed_jacobian_terms()`, guarded by `len(var_domain) > len(mult_domain)` to avoid spurious guards for domain subset cases.

---

## Test Results

- All 4400 tests pass (no regressions)
- pak: MODEL STATUS 1 Optimal, w = 1075.547 (exact LP match)
- Reference models (dispatch, ramsey, sparta, ajax) all optimal with unchanged objectives

---

## Related Issues

- #1042 — pak MCP unmatched equation comp_conl(1962) — FIXED (by #1045)
- #1045 — etamac MCP lead/lag stationarity — FIXED (PR #1047)
- #767 / #764 — Scalar constraint sameas guard — FIXED (original guard implementation)
