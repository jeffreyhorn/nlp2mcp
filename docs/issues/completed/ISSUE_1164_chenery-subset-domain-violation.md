# chenery: $171 Domain Violation — Parameters Declared Over Subset Indexed by Superset

**GitHub Issue:** [#1164](https://github.com/jeffreyhorn/nlp2mcp/issues/1164)
**Status:** OPEN
**Severity:** High — MCP fails to compile ($171)
**Date:** 2026-03-27
**Affected Models:** chenery, shale (and potentially any model where parameters/variables are declared over subsets but stationarity equations use the superset domain)

---

## Problem Summary

The stationarity builder maps concrete element indices back to the equation's domain variable (e.g., `i`), but parameters declared over a subset (e.g., `alp(t)` where `Set t(i)`) get indexed as `alp(i)`. GAMS strictly enforces that indices match the declared domain at compile time — `alp(i)` is a domain violation because `i` includes elements not in `t`, regardless of runtime dollar conditions.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp.gms --skip-convexity-check
gams /tmp/chenery_mcp.gms lo=2
# $171 Domain violation for set
```

**Error line:**
```gams
stat_e(i).. (alp(i) * nu_dh(i) + ...)$(t(i)) =E= 0;
****                    $171
```

`alp` is declared as `Parameter alp(t)` where `Set t(i)`. Using `alp(i)` violates GAMS domain checking.

**Also affects shale:**
```bash
python -m src.cli data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms --skip-convexity-check
gams /tmp/shale_mcp.gms lo=2
# $171 Domain violation for set
```

---

## Root Cause

In `_replace_indices_in_expr()` (stationarity.py), the `element_to_set` mapping maps ALL concrete elements to the equation's domain variable. For `stat_e(i)`, element `light-ind` maps to `i` (the equation domain). But `alp` is declared over `t` (a subset of `i`), so `alp(light-ind)` should become `alp(t)` (using the parameter's own domain variable), not `alp(i)`.

The existing `_replace_matching_indices` with `prefer_declared_domain=True` DOES use the declared domain for parameters — but only when the element-to-set mapping doesn't override it. For the stationarity case, `element_to_set` maps `light-ind → i` (the equation domain), and this override wins over the declared domain.

---

## Verified Behavior

```python
# alp(i) where alp has domain (t) and t is subset of i:
# GAMS rejects even within $(t(i)) condition
eq(i).. x(i) + alp(i)$(t(i)) =e= 0;  # $171 error
eq(i)$(t(i)).. x(i) + alp(i) =e= 0;  # $171 error (head condition)
eq(t).. x(t) + alp(t) =e= 0;          # OK (equation domain matches)
```

---

## Fix Approach (Initial Hypothesis — Superseded)

> **Note:** The approach below was an initial hypothesis that was disproven during investigation. Simply rewriting `alp(i)` to `alp(t)` inside `stat_e(i)` leads to GAMS $149 (uncontrolled set). See the Investigation section below for the actual findings and the correct path forward.

~~The stationarity builder needs to preserve subset domain indices for parameters and variables declared over subsets:~~

~~1. In `_replace_matching_indices`: use subset name instead of superset.~~
~~2. Alternative: check declared domain and use subset name.~~
~~3. Key check: `model_ir.sets[t].domain == ('i',)`~~

**Effort estimate:** 3-5 hours (revised upward — requires domain restructuring, not just index rewriting)

---

## Investigation (2026-03-27)

**Attempt 1:** Modified `_replace_matching_indices` to detect when declared domain is a subset of equation domain → returns subset name `t` instead of superset `i`. Successfully produces `alp(t)`.

**Result:** GAMS $149 "Uncontrolled set entered as constant" — `t` is not in the equation domain `(i,)` so GAMS rejects it.

**Attempt 2:** Modified `_rewrite_subset_to_superset` to skip ParamRef rewriting when parameter's declared domain matches the subset. Successfully preserves `alp(t)` through the full pipeline.

**Result:** Same $149 — GAMS cannot accept `alp(t)` in equation `stat_e(i)` because `t` is uncontrolled.

**Catch-22:** GAMS rejects BOTH:
- `alp(i)` → $171 (domain violation: `alp` declared over subset `t`, not `i`)
- `alp(t)` → $149 (uncontrolled set: `t` not in equation domain `(i,)`)

**Only valid GAMS form:** `stat_e(t).. alp(t) * ... =E= 0;` — equation iterates over `t`. But this requires the stationarity equation domain to be `t` (not `i`), which breaks MCP pairing with variable `e(i)`.

**Resolution:** Head conditions do **not** resolve the subset-domain violation. Even with a head condition like `stat_e(i)$(t(i)).. alp(i) * ... =E= 0;`, GAMS still raises $171 because the symbol `alp(i)` is checked against its declared domain before the dollar condition is applied. The code generator must therefore avoid producing `alp(i)` when `alp` is declared over `t`.

**What must be done:**
1. Detect parameters and variables in the stationarity expression that are declared over strict subsets of the equation domain (e.g., `alp(t)` where the equation is over `i` with `Set t(i)`)
2. For such cases, generate stationarity equations whose domain matches the subset (e.g., `stat_e(t).. alp(t) * ... =E= 0;`) or otherwise restructure the generated model so that each indexed symbol is only ever used with indices consistent with its declared domain
3. Preserve MCP pairing for the original variable domain (e.g., `e(i)`) by introducing the necessary mappings or fixings while keeping all symbols indexed by their declared domains — **do not** attempt to fix the issue by merely rewriting `alp(i)` to `alp(t)` inside `stat_e(i)`, which leads to GAMS $149 (uncontrolled set)

---

## Fix Applied (2026-03-30)

**$171 FIXED** via parameter/variable domain widening (PR #1176). Instead of restructuring the equation domain, the emitter now declares subset-declared parameters over the superset domain. Also fixed $445 (negative constant in DollarConditional not parenthesized).

- chenery: Compiles and solves (MODEL STATUS 5, Locally Infeasible — may need further investigation)
- shale: Compiles clean (license limit for solve)

## Related Issues

- PR #1163: Fixed sum-index-vs-condition shadowing (partial fix for chenery)
- #1147/#1160: MCP pairing fixes (stationarity condition to body)
