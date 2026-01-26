# Issue: KKT Transformation Generates Invalid Index Reuse in Sum Expressions

**Status:** Open  
**Category:** KKT Transformation / Code Generation  
**Affected Models:** ajax, apl1p, dispatch, trnsport (4+ models)  
**Priority:** High  
**GitHub Issue:** [#570](https://github.com/jeffreyhorn/nlp2mcp/issues/570)

## Summary

The KKT transformation generates stationarity equations where the equation's domain index is reused inside `sum()` expressions. This causes GAMS Error 125 "Set is under control already" because GAMS doesn't allow a set to be used as both the equation's domain and a summation index within the same equation.

## Reproduction

**Model:** `data/gamslib/mcp/ajax_mcp.gms`

**Generated equation (line 73):**
```gams
stat_outp(g,m).. ((-1) * (sum(g, 0) - pcost(g,m))) + sum(g, sum(m, 0) * nu_dem(g)) + sum(m, sum(g, 0) * lam_cap(m)) =E= 0;
```

**GAMS Error:**
```
*** Error 125 in ajax_mcp.gms
    Set is under control already
```

**Root Cause:**
- The equation is indexed by `(g,m)`: `stat_outp(g,m)..`
- Inside the equation, there are `sum(g, ...)` and `sum(m, ...)` expressions
- GAMS interprets `g` and `m` as already being "controlled" by the equation domain
- You cannot use the same index as both an equation domain and a sum index

## Expected Behavior

The KKT transformation should generate valid GAMS code where:
1. Equation domain indices are NOT reused in inner sum expressions
2. If a sum over the same set is needed, use a different index alias (e.g., `sum(g2, ...)`)

**Valid alternative:**
```gams
stat_outp(g,m).. ((-1) * (sum(g2, 0) - pcost(g,m))) + sum(g2, sum(m2, 0) * nu_dem(g2)) + sum(m2, sum(g2, 0) * lam_cap(m2)) =E= 0;
```

Where `g2` is an alias for set `g`, and `m2` is an alias for set `m`.

## Analysis

The issue occurs in the stationarity equation generation. When computing gradients:
1. The gradient may involve sums over the same indices used in the original constraint
2. The KKT system combines these into equations indexed by the primal variable's domain
3. The emitter doesn't check if sum indices conflict with equation domain indices

## Affected Models

| Model | Error Count | Primary Issue |
|-------|-------------|---------------|
| ajax | 5 | `sum(g,...)` in `stat_outp(g,m)` |
| apl1p | 5+ | Similar index reuse |
| dispatch | 4 | Similar index reuse |
| trnsport | 4 | Similar index reuse |

## Proposed Fix

**Location:** `src/kkt/stationarity.py` or `src/emit/equations.py`

**Approach 1: Index aliasing during KKT generation**
- When generating stationarity equations, track which indices are used for the equation domain
- For any inner sum that would use a conflicting index, substitute an alias
- Requires generating alias declarations in the GAMS output

**Approach 2: Post-processing in emit**
- In the emit phase, scan each equation for index conflicts
- Replace conflicting sum indices with aliases
- Generate necessary alias declarations

**Approach 3: Fix during gradient computation**
- When computing symbolic gradients that involve sums, use fresh index names
- Track index usage throughout the gradient computation

## Test Case

```python
def test_stationarity_no_index_conflict():
    """Stationarity equations should not reuse domain indices in sums."""
    # Parse a model with indexed constraints
    # Generate KKT system
    # Check that no sum() uses the same index as the equation domain
    pass
```

## Related Files

- `src/kkt/stationarity.py`: Stationarity equation generation
- `src/kkt/builder.py`: KKT system construction
- `src/emit/equations.py`: Equation emission to GAMS
- `src/ir/ast.py`: Sum node definition

## Notes

This is a fundamental issue in how the KKT transformation handles indexed constraints. The fix requires understanding the index scoping rules in GAMS and ensuring the generated code respects them.

The `sum(g, 0)` patterns also suggest that some gradient terms are being computed as zero but still emitted, which could be optimized away.
