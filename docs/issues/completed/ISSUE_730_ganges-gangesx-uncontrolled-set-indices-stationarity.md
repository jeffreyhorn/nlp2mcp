# MCP Emission: Uncontrolled Set Indices in Stationarity Equations (ganges, gangesx)

**GitHub Issue:** [#730](https://github.com/jeffreyhorn/nlp2mcp/issues/730)
**Status:** Fixed
**Severity:** High -- Generated MCP files fail GAMS compilation
**Discovered:** 2026-02-15 (Sprint 19, after Issues #726 and #727 fixed parse and derivative errors)
**Fixed:** 2026-02-15 (Sprint 19)
**Affected Models:** ganges, gangesx (and likely other models with multi-indexed equations)

---

## Problem Summary

The ganges and gangesx models now translate to MCP without errors (after Issues #726 and #727), but the generated `.gms` files fail GAMS compilation with ~4153 errors, primarily:

```
**** 149  Uncontrolled set entered as constant
```

The stationarity equations contain free/uncontrolled set indices that are not declared in the equation domain and not controlled by any enclosing `sum()`. These dangling indices come from original constraint expressions where index substitution was incomplete during KKT assembly and emission.

---

## Fix Summary

The fix addressed multiple root causes across 4 files, reducing ganges compilation errors from ~4153 to 12 (the remaining 12 are pre-existing emitter issues unrelated to stationarity: 5x Error 141 unassigned params, 6x Error 187 dynamic set domains, 1x Error 257 cascade).

### Changes by file

#### 1. `src/ad/constraint_jacobian.py`
- **`_substitute_indices()`**: Added handling for `SymbolRef`, `SetMembershipTest`, and `DollarConditional` nodes. Previously, `SymbolRef("r")` inside `Call("gamma", ...)` was not substituted when replacing `r` with a concrete value like `"rural"`.

#### 2. `src/kkt/stationarity.py`
- **`_replace_indices_in_expr()`**: Added `SymbolRef` and `SetMembershipTest` case handling for index replacement.
- **`_replace_matching_indices()`**: Added `prefer_declared_domain` support for alias indices (e.g., `j` alias of `i`).
- **`_add_jacobian_transpose_terms_scalar()`**: Rewrote to group Jacobian terms by constraint and wrap each constraint's contribution in `Sum()` over the constraint domain indices. Previously, scalar stationarity equations had per-instance terms without summation, leaving constraint indices dangling.
- **`_find_variable_access_condition()`**: Added validation that all free indices in extracted conditions are within the variable's domain. Prevents conditions like `ri(r,i)` from being applied to `stat_pls(r)` where `i` would be uncontrolled. Added `_collect_symbolref_names()` helper.

#### 3. `src/emit/expr_to_gams.py`
- **Unary `not` parenthesization**: Changed `not {child_str}` to `(not {child_str})` to prevent GAMS Error 445 ("More than one operator in a row") when `not` follows another operator (e.g., `* not sa(i)` must become `* (not sa(i))`).

#### 4. `src/ad/derivative_rules.py`
- **`_ensure_numeric_condition()` helper**: New function that wraps `SetMembershipTest` nodes in `DollarConditional(Const(1.0), cond)` to emit as `1$ri(r,i)` instead of bare `ri(r,i)`. GAMS treats set membership tests as boolean, not numeric; using them as multiplicative factors causes Error 130 ("Division not defined for a set").
- Applied at all 3 locations where sum-collapse conditions become multiplicative factors (lines ~1467, ~1504, ~1704).

### Error progression
- Start: ~4153 errors (primarily Error 149)
- After fixes 1-5 (index substitution + scalar rewrite): 18 errors
- After fix 6 (Error 445 `not` parens): 16 errors
- After fix 7 (condition index validation): 14 errors
- After fix 8 (Error 130 numeric condition): 12 errors (final)

### Remaining errors (not stationarity-related)
- **5x Error 141**: `deltaq(sc)`, `deltax(i)`, `deltaz(i)`, `deltan(i)`, `deltav(i)` — self-referencing calibration assignments that depend on `.l` values from a `solve` statement. Pre-existing emitter issue.
- **6x Error 187**: `im(i)`, `ie(i)` — dynamic/assigned sets used as variable/equation domains. Pre-existing emitter issue.
- **1x Error 257**: Cascade from above errors.

---

## Reproduction

**Models:** `ganges` and `gangesx`

**Commands:**
```bash
# Generate MCP using full KKT pipeline
python -c "
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system

model = parse_model_file('data/gamslib/raw/ganges.gms')
normalize_model(model)
gradient = compute_objective_gradient(model)
J_eq, J_ineq = compute_constraint_jacobian(model)
kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
gams_code = emit_gams_mcp(kkt)
open('/tmp/ganges_mcp.gms', 'w').write(gams_code)
"

# GAMS compile check
gams /tmp/ganges_mcp.gms a=c
```

---

## Root Cause Analysis

### Affected stationarity equations (before fix)

21 stationarity equations had uncontrolled set indices:

**Scalar equations** (no domain, but contained bare `i`, `r`, `j`):
`stat_dumgrt`, `stat_dumshr`, `stat_dumtg`, `stat_exscale`, `stat_invtot`,
`stat_marg`, `stat_ochs`, `stat_ocns`, `stat_oexp`, `stat_ogdp`, `stat_ogdpmp`,
`stat_ogfi`, `stat_oimp`, `stat_oinv`, `stat_savf`, `stat_savg`, `stat_thetai`

**Indexed equations** (domain `i`, but contained bare `j` or `r`):
`stat_nd(i)`, `stat_pq(i)`, `stat_tnd(i)`, `stat_tnm(i)`

### Specific dangling index patterns

**Pattern 1: Bare `r` in `gamma(j, r)` inside scalar equations**
- Cause: `SymbolRef("r")` inside `Call("gamma", ...)` not handled by `_substitute_indices()`
- Fix: Extended `_substitute_indices()` to recurse into `SymbolRef`, `SetMembershipTest`, `DollarConditional`

**Pattern 2: Bare `i` in `ri(r,i)` inside scalar equations**
- Cause: Scalar stationarity equations built per-instance terms without Sum wrapping
- Fix: Rewrote `_add_jacobian_transpose_terms_scalar()` to group by constraint and wrap in Sum

**Pattern 3: Bare `j` in `a(i,j)` inside indexed equations**
- Cause: Alias indices (`j` alias of `i`) not matched during `_replace_matching_indices`
- Fix: Added `prefer_declared_domain` flag for alias-aware index replacement

**Pattern 4: `* not sa(i)` operator precedence**
- Cause: `not` expressions not parenthesized in GAMS emission
- Fix: Always emit `(not ...)` in `expr_to_gams.py`

**Pattern 5: `ri(r,i)` as numeric factor (Error 130)**
- Cause: Sum collapse converts dollar conditions to multiplicative factors; `SetMembershipTest` is boolean in GAMS
- Fix: `_ensure_numeric_condition()` wraps as `DollarConditional(Const(1.0), cond)` → `1$ri(r,i)`

**Pattern 6: Uncontrolled condition indices (Error 149 on stat_pls)**
- Cause: `_find_variable_access_condition()` extracted `ri(r,i)` as condition for `stat_pls(r)`, but `i` is not in pls's domain
- Fix: Validate condition indices against variable domain; reject conditions with out-of-domain indices

---

## Quality Gate

- Typecheck: pass
- Lint: pass
- Format: pass
- Unit tests: 2246 passed
- Integration tests: 274 passed, 5 skipped
- E2E tests: 42 passed
