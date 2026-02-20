# Circle Model MCP is Locally Infeasible (PATH Solver Model Status 5)

**GitHub Issue:** [#753](https://github.com/jeffreyhorn/nlp2mcp/issues/753)
**Status:** CLOSED - Superseded by Issue #803 (deeper MCP formulation problem)
**Severity:** High - MCP generation completes but produced MCP does not solve
**Date:** 2026-02-13
**Investigated:** 2026-02-16
**Closed:** 2026-02-16

---

## CLOSURE NOTE (2026-02-16)

Sprint 20 Day 2 (PR #802) implemented expression-based `.l` initialization emission. The circle model now correctly emits its `.l` initialization expressions:
```gams
a.l = (xmin + xmax)/2;
b.l = (ymin + ymax)/2;
r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
```

However, **the model remains infeasible** with PATH solver (model_status=5). This indicates the infeasibility is NOT due to missing initialization but rather a deeper issue with the MCP formulation itself.

**This issue is now superseded by [Issue #803](https://github.com/jeffreyhorn/nlp2mcp/issues/803)**, which tracks the deeper MCP formulation problem. Possible causes include:
- Incorrect stationarity equation formulation
- Missing or incorrect complementarity conditions  
- Bound handling issues in the KKT transformation

The `.l` initialization work completed in Sprint 20 Day 1-2 is correct; the circle infeasibility requires investigation of the KKT transformation logic itself.

---

## Problem Summary

The circle model (`data/gamslib/raw/circle.gms`) successfully parses and generates an MCP file, but when the generated MCP is solved with the PATH solver, it returns "Locally Infeasible" (model status 5). The original NLP model solves successfully with SNOPT/CONOPT. This indicates an issue with the KKT formulation or initialization, not with parsing or code generation.

Sprint 19 Day 3 (PR #750) added `execseed = 12345;` injection to make the stochastic `uniform()` calls deterministic, but this alone does not resolve the infeasibility.

---

## Original Model

The circle model finds the smallest circle enclosing a set of random 2D points:

```gams
Set i 'points' / p1*p10 /;
Parameter x(i), y(i);
x(i) = uniform(1,10);
y(i) = uniform(1,10);

Variable a 'x center', b 'y center', r 'radius';
Equation e(i) 'points inside circle';

e(i).. sqr(x(i) - a) + sqr(y(i) - b) =l= sqr(r);
r.lo = 0;

Model m / all /;
solve m using nlp minimizing r;
```

**Objective:** Minimize `r` (radius)
**Constraint:** `sqr(x(i) - a) + sqr(y(i) - b) <= sqr(r)` for all points
**Variable bound:** `r >= 0`

---

## Generated MCP Structure

The KKT transformation produces:

**Stationarity equations:**
```gams
stat_a.. 0 - sum(i, 2*(x(i) - a)*(-1)*lam_e(i)) =E= 0;
stat_b.. 0 - sum(i, 2*(y(i) - b)*(-1)*lam_e(i)) =E= 0;
stat_r.. 1 - sum(i, (-1)*(2*r)*lam_e(i)) - piL_r =E= 0;
```

**Complementarity equations:**
```gams
comp_e(i).. (-1)*(sqr(x(i) - a) + sqr(y(i) - b) - sqr(r)) =G= 0;
comp_lo_r.. r - 0 =G= 0;
```

**MCP pairings:**
```gams
Model mcp_model /
    stat_a.a, stat_b.b, stat_r.r,
    comp_e.lam_e, comp_lo_r.piL_r
/;
```

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/circle.gms

# The generated file is at data/gamslib/mcp/circle_mcp.gms
# Run with GAMS/PATH:
# gams data/gamslib/mcp/circle_mcp.gms
# Expected: model status 5 (Locally Infeasible)
```

---

## Root Cause Analysis

### Potential Causes

1. **Lack of variable initialization:** The original NLP sets starting points for `a`, `b`, `r` using computed values:
   ```gams
   a.l = (xmin + xmax)/2;
   b.l = (ymin + ymax)/2;
   r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
   ```
   The MCP preserves these parameter computations (`xmin`, `ymin`, `xmax`, `ymax`) but the `.l` (level) assignments to `a`, `b`, `r` may not be emitted. PATH is sensitive to initial points — starting from all zeros for a nonlinear MCP with `sqr()` terms can easily lead to local infeasibility.

2. **Missing dual variable initialization:** The KKT system requires good starting values for the dual variables (`lam_e`, `piL_r`) as well. The MCP starts all duals at zero, which may not be in the basin of attraction of the KKT solution.

3. **Sign convention in stationarity:** The stationarity equations expand `(-1)` factors from the inequality constraint derivatives. Verify that the sign convention matches: for `=l=` constraints, the multiplier `lam_e` should be non-negative and the gradient contribution should be `+lambda * grad_g` (or `-lambda * grad_g` depending on the formulation). An incorrect sign would make the system unsolvable.

4. **Expression expansion:** The stationarity equations are emitted as expanded per-element expressions rather than using indexed sums. This is correct but makes the equations very long for large sets. The expanded form should be mathematically equivalent.

### Most Likely Cause

**Variable initialization (#1 and #2)** — The original model carefully computes starting points. The MCP system is nonlinear (contains `sqr()` terms) and PATH needs a reasonable starting point. The KKT system should be mathematically correct if the sign conventions are right, so the most likely fix is to emit `.l` values for primal variables and compute reasonable starting values for dual variables.

---

## Suggested Fix

### Step 1: Emit primal variable `.l` (level) values

If the original model sets `.l` values via computed assignments, the MCP emitter should reproduce those assignments:
```gams
a.l = (xmin + xmax)/2;
b.l = (ymin + ymax)/2;
r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
```

### Step 2: Verify sign conventions

Compare the KKT stationarity equations against a hand-derived formulation for a simple 2-point case. The Lagrangian for minimizing `r` subject to `sqr(x(i)-a) + sqr(y(i)-b) - sqr(r) <= 0` is:

```
L = r + sum(i, lam(i) * (sqr(x(i)-a) + sqr(y(i)-b) - sqr(r)))
```

Stationarity conditions:
- dL/da = sum(i, lam(i) * (-2*(x(i)-a))) = 0
- dL/db = sum(i, lam(i) * (-2*(y(i)-b))) = 0
- dL/dr = 1 + sum(i, lam(i) * (-2*r)) - piL_r = 0

### Step 3: Test with manual initialization

Add `.l` values to the generated MCP and test if PATH converges. If it does, the fix is to ensure the emitter includes primal variable initialization.

---

## Related Issues

- **KNOWN_UNKNOWNS.md Unknown 1.1:** `execseed` fix confirmed and implemented (PR #750)
- **KNOWN_UNKNOWNS.md Unknown 1.2:** Originally about the house model, but the same class of issue (MCP infeasibility from KKT formulation/initialization) applies to circle
- **KNOWN_UNKNOWNS.md Unknown 1.3:** Regression risk assessment — confirmed low risk

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | Sign conventions for inequality constraint derivatives |
| `src/kkt/complementarity.py` | Complementarity condition formulation |
| `src/emit/emit_gams.py` | Variable `.l` value emission |
| `src/emit/original_symbols.py` | Parameter and computed expression emission |
| `data/gamslib/mcp/circle_mcp.gms` | Generated MCP file to inspect |

---

## Investigation Results (2026-02-16)

The `execseed = 12345;` fix from PR #750 is confirmed present in the generated MCP. However,
the root cause of the infeasibility is the **missing variable `.l` initialization**.

The original circle model sets starting points after computing bounding box parameters:
```gams
a.l = (xmin + xmax)/2;
b.l = (ymin + ymax)/2;
r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
```

Inspection of `data/gamslib/mcp/circle_mcp.gms` confirms these `.l` assignments are **not
emitted**. The emitter (`src/emit/emit_gams.py`) only emits `.l` values from `var_def.l` and
`var_def.l_map` (i.e., scalar and indexed values parsed at declaration time). Computed
assignments like `a.l = expr;` that appear in the model body are not tracked in the IR.

## What Must Be Done Before Re-attempting Fix

The IR currently does not represent variable attribute assignments (`var.l = expr;`) that appear
in the model body. To fix this issue, the following work is required:

1. **Grammar / parser:** Detect and parse `var.l = expr;` assignments in the model body
   (these are currently parsed as `ref_bound` lvalues but the resulting expression is not
   stored anywhere useful for the emitter).
2. **IR representation:** Add a structure to `VariableDef` (or `ModelIR`) to store post-
   declaration `.l` assignment expressions, analogous to `ParameterDef.expressions`.
3. **Emitter:** In `src/emit/emit_gams.py`, emit these computed `.l` assignments after
   variable declarations and before the MCP model block.
4. **Test:** Add a test that the circle model MCP file contains the three `.l` initialization
   lines and that PATH solves it successfully.
