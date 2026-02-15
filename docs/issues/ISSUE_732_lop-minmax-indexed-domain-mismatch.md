# Min/Max Reformulation: Auxiliary Variables Ignore Equation Domain (lop)

**GitHub Issue:** [#732](https://github.com/jeffreyhorn/nlp2mcp/issues/732)
**Status:** Open
**Severity:** High -- Blocks MCP translation of lop model
**Discovered:** 2026-02-15 (Sprint 19, after Issue #729 fixed multi-model attribute assignment)
**Affected Models:** lop (and any model using `min()` or `max()` inside indexed equations)

---

## Problem Summary

The lop model fails during normalization with:

```
Error: Invalid model - Domain mismatch during normalization
```

After parsing succeeds (Issue #729 fixed), the min/max reformulation pass in `src/kkt/reformulation.py` replaces `min()`/`max()` calls with scalar auxiliary variables (`domain=()`), even when the `min()`/`max()` appears inside an indexed equation. The replacement `VarRef` has no domain attributes, causing `_merge_domains()` in `src/ir/normalize.py` to fail when it tries to merge `('s1', 's2')` with `None`.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms --skip-convexity-check
```

**Error output:**
```
Error: Invalid model - Domain mismatch during normalization
```

---

## Root Cause

### Min/max in indexed equations

The lop model uses `min()` and `max()` inside three indexed equations:

**1. `dtlimit(s1,s2)`** (line 253-254):
```gams
dtlimit(s1,s2)$od(s1,s2)..
   dt(s1,s2) =l= min(od(s1,s2),maxtcap)*sum(ll$(rp(ll,s1) and rp(ll,s2)), phi(ll));
```

**2. `dtllimit(sol,s,s1)`** (lines 350-356):
```gams
dtllimit(l(sol,s,s1))..
   sum((s2,s3)$(od(s2,s3) and rp(sol,s2) and rp(sol,s3) and
       (min(rp(sol,s),rp(sol,s1)) >= rp(sol,s2) and
        max(rp(sol,s),rp(sol,s1)) <= rp(sol,s3) or
        min(rp(sol,s),rp(sol,s1)) >= rp(sol,s3) and
        max(rp(sol,s),rp(sol,s1)) <= rp(sol,s2))),
   dtr(sol,s2,s3)) =l= cap(sol);
```

**3. `sumbound(s2,s3)`** (lines 358-359) -- uses `dt(s2,s3)` whose domain propagation is affected by the `dtlimit` equation's auxiliary variable.

### Scalar auxiliary variables

The reformulation code creates auxiliary variables with `domain=()` (scalar) regardless of the equation domain:

**`src/kkt/reformulation.py` line ~813:**
```python
aux_var = VariableDef(
    name=result.aux_var_name,
    domain=(),           # <-- Always scalar
    kind=VarKind.CONTINUOUS,
    lo=None,
    up=None,
)
```

**`src/kkt/reformulation.py` line ~499:**
```python
aux_var_ref = VarRef(aux_var_name, ())  # <-- Scalar VarRef
```

**`src/kkt/reformulation.py` line ~516:**
```python
constraint = EquationDef(
    name=constraint_name,
    domain=(),  # Scalar for now; indexed handling in future  <-- Known limitation
    relation=Rel.LE,
    lhs_rhs=(lhs, rhs),
)
```

The code has an explicit comment: `# Scalar for now; indexed handling in future`.

### Domain propagation failure

After reformulation, the equations have mismatched LHS/RHS domains:

| Equation | Domain | LHS domain | RHS domain | Failure reason |
|---|---|---|---|---|
| `dtlimit` | `(s1, s2)` | `(s1, s2)` | `None` | `aux_min_dtlimit_0` is scalar |
| `dtllimit` | `(sol, s, s1)` | `None` | `(sol, s, s1)` | `aux_min_dtllimit_0` is scalar |
| `sumbound` | `(s2, s3)` | `(s2, s3)` | `None` | Domain propagation from affected `dt` |

The `_merge_domains()` function in `src/ir/normalize.py:284` requires all sub-expressions to have the same domain tuple. When one side has `('s1', 's2')` and the other has `None` (from the scalar `VarRef`), it raises `ValueError("Domain mismatch during normalization")`.

### Auxiliary variables created for lop

| Variable | Source equation | Equation domain |
|---|---|---|
| `aux_min_dtlimit_0` | `dtlimit(s1,s2)` | `(s1, s2)` |
| `aux_min_dtllimit_0` | `dtllimit(sol,s,s1)` | `(sol, s, s1)` |
| `aux_max_dtllimit_0` | `dtllimit(sol,s,s1)` | `(sol, s, s1)` |
| `aux_min_dtllimit_1` | `dtllimit(sol,s,s1)` | `(sol, s, s1)` |
| `aux_max_dtllimit_1` | `dtllimit(sol,s,s1)` | `(sol, s, s1)` |

All are created as scalar but should inherit their parent equation's domain.

---

## Fix Approach

The min/max reformulation must propagate the parent equation's domain to auxiliary variables, their VarRefs, and the complementarity constraint equations:

1. **`_create_min_reformulation()` / `_create_max_reformulation()`**: Accept the equation domain as a parameter. Create `VarRef(aux_var_name, domain_indices)` instead of `VarRef(aux_var_name, ())`.

2. **Auxiliary variable creation** (line ~813): Set `domain=eq_domain` to match the parent equation.

3. **Complementarity constraint creation** (line ~516): Set `domain=eq_domain` to match the parent equation.

4. **VarRef domain attributes**: Ensure the replacement `VarRef` gets proper `domain`, `free_domain`, and `rank` attributes matching the equation domain (or propagated from the `min()`/`max()` call's domain).

5. **Multiplier variables**: The complementarity multipliers should also be indexed over the equation domain.

### Complexity notes

- The `dtllimit` equation uses `min()`/`max()` inside a dollar condition within a `sum()`. The min/max arguments (`rp(sol,s)`, `rp(sol,s1)`) reference the equation's domain indices. The auxiliary variables need these indices to be well-defined.
- The `dtlimit` case is simpler: `min(od(s1,s2), maxtcap)` directly in the equation body, with both arguments using the equation's domain indices.
- Note that `min()`/`max()` of two **parameters** (not variables) could potentially be constant-folded rather than reformulated, which would sidestep the domain issue entirely. In `dtlimit`, `od(s1,s2)` and `maxtcap` are both parameters.

---

## Additional Context

- The lop model is a Line Optimization Problem that compares DT, ILP, and EvalDT solution approaches
- It uses multiple `Model` and `Solve` statements (Issue #729 addressed the multi-model parsing)
- Even after fixing this issue, lop may encounter further downstream issues since it uses MIP models and multiple sequential solves
- The existing code explicitly acknowledges this limitation with the comment `# Scalar for now; indexed handling in future`
