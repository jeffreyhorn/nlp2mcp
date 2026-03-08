# shale: Alias index emitted as string literal in parameter/set assignment ($170)

**GitHub Issue:** [#1015](https://github.com/jeffreyhorn/nlp2mcp/issues/1015)
**Model:** shale (GAMSlib SEQ=46)
**Status:** FIXED
**Error category:** `gams_compilation_error` (Subcategory — $170)
**Severity:** Medium — model translates but GAMS compilation fails (5 $170 errors + cascading $257/$141)

---

## Problem Summary

The emitter produces `ts('1985-89','tfp') = 1;` where `'tfp'` is a string literal. But `ts` is declared over domain `(tf,tf)`, and `'tfp'` is not an element of set `tf` — it is an **alias** for `tf` (`Alias (tf,tfp)`). GAMS raises $170 (domain violation) because the literal `'tfp'` is not a member of the `tf` set.

In the original model, `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` is a conditional loop assignment that iterates over all `(tf,tfp)` pairs. The parser/IR builder incorrectly "evaluates" this by expanding `tf` to concrete elements but leaves the alias `tfp` as a literal string in the value map key.

---

## Error Details

```
 150  ts('1985-89','tfp') = 1;
****                   $170
**** 170  Domain violation for element
 151  ts('1990-94','tfp') = 1;
****                   $170
 152  ts('1995-99','tfp') = 1;
****                   $170
 153  ts('2000-04','tfp') = 1;
****                   $170
 154  ts('2005-09','tfp') = 1;
****                   $170
```

5 `$170` errors, each because `'tfp'` is not a valid element of set `tf`.

---

## Original GAMS Context

```gams
Set tf / 1975-79, 1980-84, 1985-89, 1990-94, 1995-99, 2000-04, 2005-09, 2010-14 /
    t(tf) 'active time periods' / 1975-79, 1980-84, 1985-89, 1990-94, 1995-99, 2000-04 / ;

Alias (tf,tfp) ;

Parameter ts(tf,tf) 'time summation matrix' ;
ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1 ;
```

The assignment `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` iterates over all `(tf,tfp)` pairs and assigns 1 where `ord(tfp) < ord(tf)`. This produces a lower-triangular matrix of 1s.

---

## Root Cause

**Primary file:** `src/ir/parser.py` (IR builder)

The IR builder's `_handle_conditional_assign_general()` strips the dollar condition from the assignment, then delegates to `_handle_assign()`. The `_handle_assign()` method attempts domain expansion — iterating over set elements for indices that match set names. It correctly expands `tf` but fails to recognize `tfp` as an alias for `tf`, leaving `tfp` as a literal string in the value map keys. The condition is lost during stripping, so even if both indices were expanded, the result would be the full Cartesian product (28 entries) instead of the correct lower-triangular subset (21 entries).

---

## Fix Applied

Two-part fix in `src/ir/parser.py`:

1. **Alias resolution in domain expansion** (line ~4337): Added an else branch in the expansion loop that checks if an index is an alias resolving to the same set as the parameter's domain. Uses `_resolve_set_def()` on both the index and domain name to compare resolved `SetDef` objects by identity.

2. **Conditional expression preservation** (line ~4494): In `_handle_conditional_assign_general()`, before delegating to `_handle_assign()`, check if the LHS is an indexed parameter where all indices are set/alias names (domain-over indices) with no lead/lag offsets. If so, store the conditional expression as a `DollarConditional` in `param.expressions` and return early, skipping the expansion that would ignore the condition.

**Result:**
- `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` is stored as a `DollarConditional` expression in `param.expressions`
- The emitter outputs `ts(tf,tfp) = 1$(ord(tfp) < ord(tf));` — a correct conditional computed assignment
- All 5 $170 errors eliminated, along with cascading $257/$141 errors

Files modified:
- `src/ir/parser.py`: Two changes — alias resolution in expansion loop, conditional assignment stored as expression

### Verification

- All 3973 tests pass
- Quality gate: typecheck, lint, format all pass
- All 5 $170 errors eliminated from shale MCP output
- GAMS compilation: zero errors (only demo license limit)
- Existing lead/lag conditional assignments (e.g. `w(m+1,n)$w(m,n) = 1`) unaffected — the lead/lag offset check skips those cases

---

## Notes

- The $257 (solve not checked) and $141 (unassigned symbol) errors were cascading consequences of the $170 errors
- The emitter already supports `param.expressions` via `emit_computed_parameter_assignments()` — no emitter changes needed
- The `Alias (tf,tfp)` declaration is correctly parsed (it appears in `model_ir.aliases`)
- Similar patterns in other models that use alias indices in conditional parameter assignments will also benefit from this fix
- Separate from Issue #1005 ($149 uncontrolled set), which was fixed in PR #1014
