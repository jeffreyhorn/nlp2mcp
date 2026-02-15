# MCP Emission: Uncontrolled Set Indices in Stationarity Equations (ganges, gangesx)

**GitHub Issue:** [#730](https://github.com/jeffreyhorn/nlp2mcp/issues/730)
**Status:** Open (investigation complete, fix deferred)
**Severity:** High -- Generated MCP files fail GAMS compilation
**Discovered:** 2026-02-15 (Sprint 19, after Issues #726 and #727 fixed parse and derivative errors)
**Affected Models:** ganges, gangesx (and likely other models with multi-indexed equations)

---

## Problem Summary

The ganges and gangesx models now translate to MCP without errors (after Issues #726 and #727), but the generated `.gms` files fail GAMS compilation with ~4153 errors, primarily:

```
**** 149  Uncontrolled set entered as constant
```

The stationarity equations contain free/uncontrolled set indices that are not declared in the equation domain and not controlled by any enclosing `sum()`. These dangling indices come from original constraint expressions where index substitution was incomplete during KKT assembly and emission.

---

## Reproduction

**Models:** `ganges` and `gangesx`

**Commands:**
```bash
# Generate MCP
python -m src.cli data/gamslib/raw/ganges.gms -o /tmp/ganges_mcp.gms --skip-convexity-check

# Attempt to solve (fails)
gams /tmp/ganges_mcp.gms
```

**GAMS compilation output:**
```
--- ganges_mcp.gms(1447) 3 Mb 4153 Errors
*** Status: Compilation error(s)
```

**Error breakdown:**
- 23+ instances of Error 149 "Uncontrolled set entered as constant"
- 1 instance of Error 130 "Division not defined for a set"
- Remaining errors are cascading (Error 300 "Remaining errors not printed")

---

## Root Cause

### Affected stationarity equations

21 stationarity equations have uncontrolled set indices:

**Scalar equations** (no domain, but contain bare `i`, `r`, `j`):
`stat_dumgrt`, `stat_dumshr`, `stat_dumtg`, `stat_exscale`, `stat_invtot`,
`stat_marg`, `stat_ochs`, `stat_ocns`, `stat_oexp`, `stat_ogdp`, `stat_ogdpmp`,
`stat_ogfi`, `stat_oimp`, `stat_oinv`, `stat_savf`, `stat_savg`, `stat_thetai`

**Indexed equations** (domain `i`, but contain bare `j` or `r`):
`stat_nd(i)`, `stat_pq(i)`, `stat_tnd(i)`, `stat_tnm(i)`

### Specific dangling index patterns

**Pattern 1: Bare `r` in `gamma(j, r)` inside scalar equations**

In `stat_dumgrt..`:
```gams
ac("agricult","rural") * (mc("rural") - sum(j, pc00(j) * gamma(j, r)))
                                                              ^^^
                                                              r is uncontrolled
```

The `les(i,r)` equation uses `gamma(i,r)`. When instantiated for specific `(i,r)` values like `("agricult","rural")`, the `i` index in `gamma(i,r)` was substituted but `r` was not. Expected: `gamma(j, "rural")`.

**Pattern 2: Bare `i` in `ri(r,i)` inside scalar equations**

In `stat_dumgrt..`:
```gams
sum(r$(ri(r,i)), 0)
              ^^^
              i is uncontrolled (86 occurrences in this equation)
```

Multiple original equations use `sum(r$(ri(r,i)), ...)` where `i` is the equation domain. When these constraint contributions are emitted in a scalar stationarity equation, the `i` should have been substituted with a specific element value.

**Pattern 3: Bare `j` in `a(i,j)` inside indexed equations**

In `stat_pq(i)..`:
```gams
((-1) * ((1 + tnd(i)) * a(i,j))) * nu_pnddet(i)
                            ^^^
                            j is uncontrolled
```

The original equation `pnddet(i).. pnd(i) =e= sum(j, a(j,i)*pq(j)*(1+tnd(j)))`. When differentiating w.r.t. `pq(i)`, the sum over `j` should collapse to the specific term where `j` matches the stationarity variable's index. Instead, the derivative leaves `j` as a bare index.

### Root cause in the pipeline

The issue is in the stationarity equation assembly and emission pipeline (primarily `src/kkt/stationarity.py`). When building the stationarity condition for a variable `x(domain)`:

1. For each constraint `g(indices)` that references `x`, the pipeline computes `dg/dx * nu_g`
2. When the constraint has more indices than the variable, those extra indices must be summed over (or, for scalar variables, all constraint indices must be summed over)
3. When the constraint has different index names, index substitution must map constraint indices to the stationarity equation's domain

Steps 2 and 3 appear to be incomplete: some index substitutions are performed (e.g., `i` → `"agricult"` in some places) while others are missed (e.g., `r` remaining bare in `gamma(j, r)`), and some summations that should wrap the entire constraint contribution are absent.

---

## Investigation Results (Sprint 19)

A thorough investigation of the pipeline identified the following specific code locations needing fixes:

### Critical fix points in `src/kkt/stationarity.py`

1. **`_add_indexed_jacobian_terms()` (~lines 977-1090)**: The summation policy at lines ~1041-1059 only considers indices in the multiplier domain (`mult_domain`), not indices in the derivative expression itself. If the derivative contains indices not in `var_domain` and not in `mult_domain`, they are never summed.

2. **`_add_jacobian_transpose_terms_scalar()` (~lines 1211-1268)**: For scalar stationarity equations, when a constraint is indexed, the code builds `derivative * multiplier` terms but never wraps them in `Sum()` over the constraint indices. All constraint indices should be summed over since the stationarity equation is scalar.

3. **`_replace_indices_in_expr()` (~lines 621-770)**: After index substitution, there is no validation that all indices in the expression are controlled (either in the equation domain or inside a `sum()`). Parameters with declared domains containing indices not in the variable domain are not flagged for summation.

4. **`_build_element_to_set_mapping()` (~lines 478-550)**: The mapping is built only from variable instances. Indices appearing in constraint domains or parameter declarations that are not in the variable domain are not captured, leading to missed substitutions.

5. **`_replace_matching_indices()` (~lines 811-950)**: Only handles forward substitution (element → set name), does not recognize when an index in a declared domain has no equivalent in the variable's domain and needs summation.

### Why this fix is deferred

This is a systemic issue spanning multiple interconnected components of the KKT pipeline:
- Automatic differentiation (symbolic derivatives containing sum indices)
- Constraint Jacobian construction (per-instance derivative storage)
- Stationarity equation assembly (index mapping, substitution, summation wrapping)
- GAMS code emission

Fixing this correctly requires:
1. Enhancing the summation logic in `_add_indexed_jacobian_terms()` to detect and sum over all uncontrolled indices in derivative expressions
2. Adding summation wrapping in `_add_jacobian_transpose_terms_scalar()` for all constraint indices
3. Expanding `_build_element_to_set_mapping()` to include constraint-domain indices
4. Adding post-substitution validation in `_replace_indices_in_expr()`
5. Comprehensive test coverage for cross-domain index scenarios

The risk of regressions to the existing 3325 passing tests (many of which test stationarity assembly) is significant. This fix should be planned as a dedicated sprint task with careful incremental testing.

---

## Fix Approach

The fix requires ensuring that during stationarity equation assembly:

1. **All constraint indices not in the stationarity equation's domain must be summed over.** If `stat_dumgrt` is scalar and the constraint `les(i,r)` contributes a derivative term, that term must be wrapped in `sum((i,r), ...)`.

2. **Index substitution must be complete.** When instantiating a constraint contribution for a specific variable instance, all references to the constraint's domain indices must either (a) be substituted with the concrete element value, or (b) be controlled by an explicit `sum()`.

3. **Derivative expressions must not contain indices from the differentiated expression that aren't controlled.** The derivative of `sum(j, a(j,i)*pq(j))` w.r.t. `pq(i)` should produce a term with `j` substituted or summed, not left dangling.

### Suggested implementation order

1. Start with `_add_jacobian_transpose_terms_scalar()` — add `Sum(constraint_domain, term)` wrapping for indexed constraints contributing to scalar stationarity equations (addresses Patterns 1 and 2)
2. Enhance `_add_indexed_jacobian_terms()` to detect uncontrolled indices in the derivative expression and wrap in additional `Sum()` nodes (addresses Pattern 3)
3. Expand `_build_element_to_set_mapping()` to include constraint indices
4. Add post-substitution validation pass
5. Add targeted integration tests for each pattern

### Relevant files
- `src/kkt/stationarity.py` -- stationarity equation assembly (primary)
- `src/ad/index_mapping.py` -- index mapping and enumeration
- `src/emit/emit_gams.py` -- GAMS code emission
- `tests/integration/kkt/test_stationarity.py` -- stationarity tests (~1600 lines, 7 test classes)

---

## Additional Context

- The ganges model has 6 sectors (set `i`), 2 regions (set `r`), and 5 income types (set `ty`), leading to many indexed equations
- The model uses region-sector mapping via `ri(r,i)` as dollar conditions, which complicates index handling
- The `gamma(i,r)` parameter (Issue #727 fix) now correctly differentiates to 0, but its non-differentiated appearances in constraint bodies still need proper index substitution
- gangesx has the same structure and would have the same errors
- This issue is in the KKT/emission pipeline, not in parsing or differentiation
- There are also `SetMembershipTest` condition evaluation warnings during generation, which cause some equation instances to be over-included (separate issue)
