# ISSUE_672 Analysis: MCP Pairing Failures in alkyl and bearing

**GitHub Issue:** [#672](https://github.com/jeffreyhorn/nlp2mcp/issues/672)
**Prep Task:** Sprint 19 Prep Task 8
**Date:** 2026-02-13
**Status:** Analysis Complete

---

## Executive Summary

The "unmatched equation" errors in alkyl (7 errors) and bearing (2 errors) are caused by a **case sensitivity mismatch** between variable names in `CaseInsensitiveDict.keys()` (always lowercase) and variable names in equation AST `VarRef` nodes (original case from GAMS source). This causes the automatic differentiation system to produce zero derivatives for every constraint-variable pair where the GAMS source uses mixed-case variable names, resulting in stationarity equations where all constraint multiplier coefficients are zero.

**Root cause:** `CaseInsensitiveDict.keys()` returns lowercase keys (e.g., `acidfeed`), but equation expressions contain `VarRef("AcidFeed")`. When `differentiate_expr(constraint_expr, "acidfeed", ...)` is called, the name comparison `"AcidFeed" != "acidfeed"` returns `True`, producing `Const(0.0)` instead of the correct derivative.

**The original assumption in Unknown 8.4 is WRONG.** The issue is NOT bound configurations causing empty equations — it is a systematic case sensitivity bug in the AD/Jacobian pipeline that produces zero derivatives for any variable whose GAMS source name uses mixed case.

**Proposed fix:** Normalize variable names in `VarRef` nodes to lowercase at parse time (in `src/ir/parser.py`), making them consistent with the lowercase keys in `CaseInsensitiveDict`. This is a localized fix with low regression risk.

**Effort estimate:** 2-4 hours (down from 4-6h in FIX_ROADMAP)

---

## Error Reproduction

### alkyl model

```
**** MCP pair AcidBal.nu_AcidBal has unmatched equation
**** MCP pair AcidDef.nu_AcidDef has unmatched equation
**** MCP pair AlkylDef.nu_AlkylDef has unmatched equation
**** MCP pair AlkylShrnk.nu_AlkylShrnk has unmatched equation
**** MCP pair F4Def.nu_F4Def has unmatched equation
**** MCP pair IsoButBal.nu_IsoButBal has unmatched equation
**** MCP pair OctDef.nu_OctDef has unmatched equation
**** SOLVE from line 287 ABORTED, EXECERROR = 7
```

ALL 7 equality constraints have "unmatched equation" — every constraint's multiplier variable (`nu_*`) is never referenced with a non-zero coefficient in any stationarity equation body.

### bearing model

```
**** MCP pair comp_radius.lam_radius has unmatched equation
**** MCP pair pumping_energy.nu_pumping_energy has unmatched equation
**** SOLVE from line 311 ABORTED, EXECERROR = 2
```

Only 2 of 13 constraints fail — the rest produce correct derivatives. This partial correctness pattern was the key to diagnosing the bug (see Section 4).

---

## Root Cause Analysis

### The Bug Chain

The bug involves three components interacting:

#### 1. `CaseInsensitiveDict.keys()` returns LOWERCASE keys

**File:** `src/utils/case_insensitive_dict.py:81-83`

```python
def keys(self):  # type: ignore[override]
    """Return view of lowercase keys (for internal use)."""
    return super().keys()
```

The `__setitem__` method stores keys as `key.lower()`:
```python
def __setitem__(self, key: str, value: T) -> None:
    canonical = key.lower()
    super().__setitem__(canonical, value)
```

So `model_ir.variables.keys()` returns `["acidfeed", "alkylyld", "olefinfeed", ...]` — all lowercase.

#### 2. The Jacobian/gradient loops iterate using these lowercase keys

**File:** `src/ad/constraint_jacobian.py:248` (in `_compute_equality_jacobian`):
```python
for var_name in sorted(model_ir.variables.keys()):
```

**File:** `src/ad/gradient.py:248` (in `compute_gradient`):
```python
for var_name in sorted(model_ir.variables.keys()):
```

These produce `var_name = "acidfeed"` (lowercase).

#### 3. Equation AST preserves original mixed case from the GAMS source

**File:** `src/ir/parser.py` (in `_make_symbol` / `_expr`):
```python
name = _token_text(node)       # Returns "AcidFeed" (original case from GAMS source)
expr = VarRef(name, idx_tuple)  # Stores VarRef("AcidFeed", ())
```

The parser checks `name in self.model.variables` (which succeeds due to case-insensitive `__contains__`), but the `name` string itself is never lowered before being stored in the `VarRef` node.

#### 4. The differentiation code does a case-SENSITIVE string comparison

**File:** `src/ad/derivative_rules.py:258` (in `_diff_varref`):
```python
if expr.name != wrt_var:
    return Const(0.0)
```

This comparison is: `"AcidFeed" != "acidfeed"` → `True` → returns `Const(0.0)`.

### The Full Chain

For alkyl's `AcidBal` equation (`0.98*AcidFeed =e= AcidStren*(AlkylYld*AcidDilut/100 + AcidFeed)`):

1. Parser creates: `VarRef("AcidFeed", ())` in the equation AST (original case)
2. Jacobian loop calls: `differentiate_expr(constraint_expr, "acidfeed", (), config)` (lowercase from `keys()`)
3. Inside `_diff_varref`: `"AcidFeed" != "acidfeed"` is `True`
4. Returns `Const(0.0)` — zero derivative

This happens for **every** variable in **every** equation where the GAMS source uses mixed-case names, producing an entirely zero Jacobian and zero gradient for the alkyl model.

### Scope of Impact

Every call site that iterates `model_ir.variables.keys()` and passes the key to `differentiate_expr` is affected:

| File | Line | Function |
|------|------|----------|
| `src/ad/constraint_jacobian.py` | 348 | `_compute_equality_jacobian` |
| `src/ad/constraint_jacobian.py` | 434 | `_compute_inequality_jacobian` |
| `src/ad/constraint_jacobian.py` | 494 | `_compute_bound_jacobian` |
| `src/ad/gradient.py` | 248 | `compute_gradient` |
| `src/ad/index_mapping.py` | ~415 | `build_index_mapping` (stores lowercase in `col_to_var`) |

---

## Per-Model Analysis

### alkyl (7 errors — complete Jacobian failure)

**Variable declarations in GAMS source:** Mixed case (`OlefinFeed`, `IsobutRec`, `AcidFeed`, `AlkylYld`, `IsobutMak`, `AcidStren`, `Octane`, `Ratio`, `AcidDilut`, `F4Perf`, `alkerr`, `octerr`, `aciderr`, `F4err`, `F`)

**Equation bodies in GAMS source:** Use mixed case matching declarations (`AcidBal.. 0.98 * AcidFeed =E= AcidStren * (AlkylYld * AcidDilut / 100 + AcidFeed)`)

**Result:** Parser creates `VarRef("AcidFeed")`, `VarRef("AcidStren")`, `VarRef("AlkylYld")`, etc. But iteration keys are `acidfeed`, `acidstren`, `alkylyld`. Every differentiation produces `Const(0.0)`.

**Evidence from generated MCP:** ALL 14 stationarity equations have the pattern:
```
stat_X.. 0 + 0 * nu_AlkylShrnk + 0 * nu_AcidBal + ... + 0 * nu_F4Def - piL_X + piU_X =E= 0;
```
The leading `0` is the (zero) objective gradient. The `0 * nu_*` terms are the (zero) Jacobian entries. Only the bound multiplier terms (`-piL_X + piU_X`) survive because they are generated directly, not through differentiation.

**Why ALL 7 constraints fail:** Since every Jacobian entry is zero, every constraint multiplier (`nu_*`) is never referenced in any stationarity equation body. GAMS detects that the paired variable (`nu_AcidBal`) does not appear in its paired equation (`AcidBal`), producing the "unmatched equation" error.

### bearing (2 errors — partial Jacobian failure)

**Variable declarations in GAMS source:** Mixed case in Variable statement (`R`, `R0`, `Q`, `PL`, `P0`, `Ef`, `Ep`, `W`, `T`) but lowercase in many equation bodies.

**Key observation:** Some equations use the **declaration case** (mixed) while others use **lowercase**:
- `pumping_energy.. Ep =E= Q*(P0 - P1)/pump_efficiency;` — uses `Ep`, `Q`, `P0` (mixed case matching declaration)
- `friction.. Ef*h =e= sqr(2*pi*N/60)*[(2*pi*mu)]*(r**4 - r0**4)/4;` — uses `r`, `r0`, `mu`, `h` (lowercase, different from declaration `R`, `R0`)

**Result:** Variables referenced in lowercase in equation bodies (`r`, `r0`, `mu`, `h`, `tmp1`, `tmp2`, `delta_t`) match the lowercase iteration keys and produce correct derivatives. Variables referenced in mixed case (`Ep`, `Q`, `P0`, `Ef`, `R`, `R0`, `W`, `T`, `PL`) do not match and produce zero derivatives.

**Failing pairs:**
1. `comp_radius.. R - R0 =G= 0;` — `VarRef("R")` vs `wrt_var="r"` → zero derivative for ∂(R-R0)/∂r → `stat_r` has `0 * lam_radius`
2. `pumping_energy.. Ep =E= Q * (P0 - P1) / pump_efficiency;` — `VarRef("Ep")` vs `wrt_var="ep"` → zero derivative for ∂Ep/∂ep → `stat_ep` has `0 * nu_pumping_energy`

**Working pairs (confirming diagnosis):**
- `stat_h` has `Ef * nu_friction` — because `friction..` uses lowercase `h`: `Ef*h =e= ...`, and ∂(Ef*h)/∂h = Ef (correct, since `VarRef("h")` matches `wrt_var="h"`)
- `stat_mu` has complex expressions for `nu_friction`, `nu_inlet_pressure`, `nu_oil_viscosity` — because equations use lowercase `mu`
- `stat_r` has `nu_friction` term — because `friction..` uses lowercase `r` in `r**4 - r0**4`
- `stat_tmp1` has `W * nu_load_capacity` — because `load_capacity..` uses lowercase-matching reference

**This partial correctness pattern proves the case sensitivity root cause:** only equations that happen to use lowercase variable names in their GAMS source produce correct derivatives.

---

## Empirical Confirmation: All-Lowercase Models Work

Models with all-lowercase variable names produce correct (non-zero) stationarity equations:

- **process** (`olefin`, `alkylate`, `acid` — all lowercase): `stat_alkylate` has `((-1) * (octane * 0.063)) + 1 * nu_yield + ...` (correct non-zero derivatives)
- **himmel16** (`x`, `y`, `area` — all lowercase): `stat_x(i)` has `((-1) * (0.5 * y(i))) + ...` (correct)
- **blend** (`alloy`, `rawmat` — all lowercase): correct non-zero stationarity equations

This confirms that the differentiation engine is correct; the only issue is the case mismatch in variable name lookup.

---

## Proposed Fix

### Recommended Approach: Normalize VarRef names to lowercase at parse time

**Where:** `src/ir/parser.py`, in the code path that creates `VarRef` nodes for equation bodies.

**What:** When the parser resolves a name as a variable (via `name in self.model.variables`), normalize the name to lowercase before storing in the `VarRef`:

```python
# Before (current):
expr = VarRef(name, idx_tuple)

# After (fix):
canonical_name = name.lower()
expr = VarRef(canonical_name, idx_tuple)
```

Using `name.lower()` is consistent with how `CaseInsensitiveDict.keys()` stores keys internally. Note: `get_original_name()` is NOT suitable here — it returns the original casing (e.g., `"AcidFeed"`), not the lowercase canonical form needed for matching.

### Why This Approach

1. **Localized:** Single change point in the parser
2. **Consistent:** Makes AST nodes agree with dictionary keys throughout the pipeline
3. **Low regression risk:** Only affects the name stored in `VarRef`, not the lookup logic
4. **Covers all cases:** Gradient, equality Jacobian, inequality Jacobian, bound Jacobian — all use `model_ir.variables.keys()` which returns lowercase

### Alternative Approaches Considered

| Approach | Pros | Cons |
|----------|------|------|
| **A: Lowercase VarRef at parse time (recommended)** | Single change point, normalizes early | Requires careful scoping to only affect variables |
| **B: Use `original_keys()` in iteration loops** | Preserves original case | Requires changes in 5+ files; `original_keys()` may return different case than AST |
| **C: Case-insensitive comparison in `_diff_varref`** | Minimal change | Breaks the clean semantic contract of exact-match differentiation; may mask other bugs |

### Additional Considerations

- **SymbolRef:** The same normalization should apply to `SymbolRef` nodes if they are used for variables. Check `_diff_symbolref` for the same pattern.
- **Equation names:** Equation names in `model_ir.equalities` / `model_ir.inequalities` may also have case mismatches with equation AST names. Verify that the Jacobian row lookup uses case-insensitive matching.
- **Parameter names:** `ParamRef` nodes are treated as constants (derivative = 0) so case mismatch does not affect differentiation. However, for emit correctness, parameter names should also be normalized.

### Test Strategy

1. **Unit tests:** Add test cases in `tests/unit/ad/` for differentiation with mixed-case variable names
2. **Integration tests:** Regenerate alkyl and bearing MCP files and verify non-zero stationarity equations
3. **GAMS validation:** Run regenerated MCP files through GAMS and confirm zero "unmatched equation" errors
4. **Regression:** Run full test suite (3294 tests) to verify no breakage

---

## Effort Estimate

| Task | Effort |
|------|--------|
| Implement VarRef name normalization in parser | 1h |
| Add unit tests for mixed-case differentiation | 0.5h |
| Regenerate alkyl and bearing MCP files | 0.5h |
| GAMS validation (if GAMS available) | 0.5h |
| Regression testing | 0.5h |
| **Total** | **2-4h** |

This is reduced from the FIX_ROADMAP estimate of 4-6h because the fix is a single-point normalization, not a rework of the MCP pairing logic.

---

## Unknown 8.4 Verification

**Original Assumption:** "The empty MCP equation issue is caused by specific bound configurations (e.g., variables with equal `.lo` and `.up`, or `.fx` bounds) that the MCP pairing logic in `src/kkt/partition.py` doesn't handle correctly."

**Status:** ❌ WRONG

**Correction:** The issue has nothing to do with bound configurations or MCP pairing logic. The root cause is a **case sensitivity mismatch** in the AD differentiation pipeline:
- `CaseInsensitiveDict.keys()` returns lowercase variable names
- Equation AST `VarRef` nodes store original-case variable names from the GAMS source
- `differentiate_expr()` uses case-sensitive string comparison (`expr.name != wrt_var`)
- Result: ALL derivatives are zero for mixed-case variable names, producing empty stationarity equations

The MCP pairing in `src/kkt/partition.py` is correct. The "unmatched equation" error is a downstream symptom of the zero-derivative bug, not a pairing logic defect.

---

## Impact on Sprint 19

- **Effort reduced:** 4-6h (FIX_ROADMAP) → 2-4h (localized parser fix)
- **May unblock additional models:** Any model with mixed-case GAMS variable names that currently produces incorrect MCP output would be fixed
- **Regression risk:** Low-to-moderate — normalization will also cause emitted MCP variable names to be lowercased (since the emit layer in `src/emit/expr_to_gams.py:394` uses `var_ref.name` directly, not `get_original_name()`), which is functionally correct (GAMS is case-insensitive) but may affect code readability; this tradeoff should be explicitly addressed during implementation, either by accepting lowercase output or by updating the emit layer to use `get_original_name()` to preserve original casing
