# Jacobian Computation Timeout for lop Model

**GitHub Issue:** [#736](https://github.com/jeffreyhorn/nlp2mcp/issues/736)
**Status:** Resolved — model excluded from pipeline; sparsity optimization retained
**Severity:** Medium -- lop model cannot complete MCP translation due to performance
**Discovered:** 2026-02-15 (Sprint 19, after Issues #732 and #733 fixed)
**Affected Models:** lop (and potentially other models with many indexed inequalities)

---

## Problem Summary

The lop model hangs during constraint Jacobian computation. After Issues #732 (domain mismatch) and #733 (sameas differentiation) were fixed, the pipeline advances through parsing, normalization, reformulation, and gradient computation, but times out computing the constraint Jacobian.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms --skip-convexity-check
```

**Behavior:** The process hangs indefinitely during the "Computing derivatives..." stage (specifically `compute_constraint_jacobian()`).

**Timing profile:**
| Stage | Time |
|---|---|
| Parse | ~12s |
| Normalize 1 | 0.03s |
| Reformulate | 0.01s |
| Normalize 2 | 0.03s |
| Gradient | ~11s |
| Jacobian | >120s (timeout) |

---

## Root Cause

### Model is MIP, not NLP

The lop model (`gamslib_type: "LP"`) contains **no NLP solve statements**. All solve statements use LP or MIP:

```gams
solve sp minimzing spobj using lp;
solve lopdt maximizing obj using mip;
solve ilp minimizing obj using mip;
solve evaldt maximizing obj using lp;
```

KKT transformation via nlp2mcp is not applicable to MIP models. The model should never have entered the translation pipeline.

### Combinatorial explosion from dynamic subset fallback

Even setting aside the MIP issue, the model creates an infeasible workload due to dynamic subset fallback:

- Dynamic subset `sol` has 0 static members → falls back to parent set `s` (23 members)
- Equations with domain `(sol, s, s1)` expand to 23³ = **12,167 instances**
- Variable `dtr` expands to **279,841 instances** (23⁴)
- Total estimated differentiation calls: **~4.9 billion**

The variable-level sparsity pre-check helps for models with many variables where most constraints reference only a few, but cannot address the index-level combinatorial explosion where a single equation-variable pair produces millions of (equation instance × variable instance) combinations.

### Model size after expansion

The lop model has multiple GAMS `Model` and `Solve` statements, and the tool processes ALL equations from ALL models. After normalization and reformulation:

- **15 variables** (with up to 279,841 instances each due to subset fallback)
- **24 equations** (7 equalities + many inequalities)
- **546 inequalities** (after index expansion)
- **529 normalized bounds**

---

## Resolution

### 1. Model excluded from pipeline

The lop model has been marked as `convexity.status: "excluded"` in `gamslib_status.json` with the reason: "Model uses MIP solve statements (not NLP). Additionally, dynamic subset fallback causes combinatorial explosion in constraint count."

### 2. Sparsity optimization retained

Three optimizations were applied to `_compute_equality_jacobian()`, `_compute_inequality_jacobian()`, and `_compute_bound_jacobian()` in `src/ad/constraint_jacobian.py`. These benefit legitimate NLP models even though they cannot resolve the lop-specific combinatorial explosion:

1. **Sparsity pre-check**: Before differentiating a constraint with respect to a variable, `find_variables_in_expr()` (from `src/ad/sparsity.py`) is called on the equation template to determine which variables are actually referenced. If the variable is not referenced, differentiation is skipped entirely.

2. **Variable instance caching**: `enumerate_variable_instances()` is now called once per variable via `_precompute_variable_instances()` and shared across all three Jacobian sub-functions, instead of being recomputed per-constraint.

3. **Sparse zero storage**: Derivatives that evaluate to `Const(0)` are no longer stored in the Jacobian structure. Consumers already handle `None` returns from `get_derivative()` as zero.

---

## Fix Approaches Considered

### Option A: Model-scoped equation processing (architectural)

Only process equations belonging to the selected model/solve statement. This would reduce the equation count from 24 to ~5 (the equations in a single model) and inequalities from 546 to a manageable number. This is a significant architectural change.

### Option B: Performance optimization of Jacobian computation (applied)

Profile the Jacobian computation to identify bottlenecks:
- Cache differentiation results for shared subexpressions
- Skip differentiation when the constraint doesn't reference the variable
- Parallelize Jacobian computation across variables or constraints
- Avoid repeated dynamic subset fallback warnings (cache the result)

### Option C: Timeout with informative error

Add a configurable timeout for Jacobian computation so the user gets a clear error instead of an indefinite hang.

### Option D: Exclude model from pipeline (applied)

Mark the model as excluded since it uses MIP solve statements and is not a valid candidate for NLP-to-MCP translation.
