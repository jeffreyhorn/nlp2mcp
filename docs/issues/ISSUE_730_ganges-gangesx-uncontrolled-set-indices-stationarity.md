# MCP Emission: Uncontrolled Set Indices in Stationarity Equations (ganges, gangesx)

**GitHub Issue:** [#730](https://github.com/jeffreyhorn/nlp2mcp/issues/730)
**Status:** Open
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

The issue is in the stationarity equation assembly and emission pipeline (likely `src/kkt/stationarity.py` and `src/emit/emit_gams.py`). When building the stationarity condition for a variable `x(domain)`:

1. For each constraint `g(indices)` that references `x`, the pipeline computes `dg/dx * nu_g`
2. When the constraint has more indices than the variable, those extra indices must be summed over (or, for scalar variables, all constraint indices must be summed over)
3. When the constraint has different index names, index substitution must map constraint indices to the stationarity equation's domain

Steps 2 and 3 appear to be incomplete: some index substitutions are performed (e.g., `i` → `"agricult"` in some places) while others are missed (e.g., `r` remaining bare in `gamma(j, r)`), and some summations that should wrap the entire constraint contribution are absent.

---

## Fix Approach

The fix requires ensuring that during stationarity equation assembly:

1. **All constraint indices not in the stationarity equation's domain must be summed over.** If `stat_dumgrt` is scalar and the constraint `les(i,r)` contributes a derivative term, that term must be wrapped in `sum((i,r), ...)`.

2. **Index substitution must be complete.** When instantiating a constraint contribution for a specific variable instance, all references to the constraint's domain indices must either (a) be substituted with the concrete element value, or (b) be controlled by an explicit `sum()`.

3. **Derivative expressions must not contain indices from the differentiated expression that aren't controlled.** The derivative of `sum(j, a(j,i)*pq(j))` w.r.t. `pq(i)` should produce a term with `j` substituted or summed, not left dangling.

The relevant files to investigate:
- `src/kkt/stationarity.py` -- stationarity equation assembly
- `src/ad/index_mapping.py` -- index mapping and enumeration
- `src/emit/emit_gams.py` -- GAMS code emission for stationarity equations

---

## Additional Context

- The ganges model has 6 sectors (set `i`), 2 regions (set `r`), and 5 income types (set `ty`), leading to many indexed equations
- The model uses region-sector mapping via `ri(r,i)` as dollar conditions, which complicates index handling
- The `gamma(i,r)` parameter (Issue #727 fix) now correctly differentiates to 0, but its non-differentiated appearances in constraint bodies still need proper index substitution
- gangesx has the same structure and would have the same errors
- This issue is in the KKT/emission pipeline, not in parsing or differentiation
