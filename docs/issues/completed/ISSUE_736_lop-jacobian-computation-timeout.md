# Jacobian Computation Timeout for lop Model

**GitHub Issue:** [#736](https://github.com/jeffreyhorn/nlp2mcp/issues/736)
**Status:** Fixed
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
| Normalize 1 | 0.02s |
| Reformulate | 0.01s |
| Normalize 2 | 0.02s |
| Gradient | 7.78s |
| Jacobian | >120s (timeout) |

---

## Root Cause

### Model size after expansion

The lop model has multiple GAMS `Model` and `Solve` statements, but the tool processes ALL equations from ALL models. After normalization and reformulation:

- **15 variables** (decision variables)
- **24 equations** (7 equalities + many inequalities)
- **546 inequalities** (after index expansion)

The Jacobian computation differentiates each of the 546 inequality constraints with respect to each of the 15 variables, producing up to 8,190 symbolic derivative entries.

### Dynamic subset fallbacks

Many equations reference dynamic subsets (`sol`, `ll`) that have no static members. The system falls back to the parent set `s` (23 members), dramatically expanding the number of indexed instances. This produces hundreds of warnings like:

```
Dynamic subset 'sol' has no static members; falling back to parent set 's' (23 members)
```

### Multi-model processing

The lop file defines 4 separate models (`sp`, `dtlop`/`lopdt`, `ilp`, `evaldt`) with different solve types (LP, MIP). The tool processes all equations from all models rather than scoping to a single NLP/MCP-relevant model. Many of the 546 inequalities belong to LP/MIP models that don't need KKT transformation.

---

## Fix Approach

### Option A: Model-scoped equation processing (architectural)

Only process equations belonging to the selected model/solve statement. This would reduce the equation count from 24 to ~5 (the equations in a single model) and inequalities from 546 to a manageable number. This is a significant architectural change.

### Option B: Performance optimization of Jacobian computation

Profile the Jacobian computation to identify bottlenecks:
- Cache differentiation results for shared subexpressions
- Skip differentiation when the constraint doesn't reference the variable
- Parallelize Jacobian computation across variables or constraints
- Avoid repeated dynamic subset fallback warnings (cache the result)

### Option C: Timeout with informative error

Add a configurable timeout for Jacobian computation so the user gets a clear error instead of an indefinite hang.

---

## Fix Applied

**Approach:** Option B — Performance optimization of Jacobian computation
**Commit:** e635b7e
**Files changed:** `src/ad/constraint_jacobian.py`, `tests/integration/ad/test_bound_jacobian.py`, `tests/integration/ad/test_constraint_jacobian.py`

Three optimizations were applied to `_compute_equality_jacobian()`, `_compute_inequality_jacobian()`, and `_compute_bound_jacobian()`:

1. **Sparsity pre-check**: Before differentiating a constraint with respect to a variable, `find_variables_in_expr()` (from `src/ad/sparsity.py`) is called on the equation template to determine which variables are actually referenced. If the variable is not referenced, differentiation is skipped entirely. For the lop model with 546 inequalities × 15 variables = 8,190 potential derivatives, the majority are zero because each inequality typically references only 1–3 of the 15 variables.

2. **Variable instance caching**: `enumerate_variable_instances()` is now called once per variable via `_precompute_variable_instances()` and shared across all three Jacobian sub-functions, instead of being recomputed per-constraint.

3. **Sparse zero storage**: Derivatives that evaluate to `Const(0)` are no longer stored in the Jacobian structure. Consumers already handle `None` returns from `get_derivative()` as zero.

---

## Additional Context

- The gradient computation (15 variables, 1 objective) completes in ~8s, suggesting per-derivative cost is ~0.5s
- At ~0.5s per derivative, 8,190 Jacobian entries would take ~68 minutes
- The sparsity pre-check eliminates the vast majority of these derivatives, reducing computation to only the nonzero entries
- The dynamic subset fallback warnings suggest the system is doing redundant work expanding set membership for each derivative
- The lop model is a Line Optimization Problem with 4 sub-models; only the NLP-relevant equations need KKT transformation
