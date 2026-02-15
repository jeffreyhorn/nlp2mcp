# Parser: Parameter Index Count Mismatch for Runtime-Reassigned Parameters (lop)

**GitHub Issue:** [#726](https://github.com/jeffreyhorn/nlp2mcp/issues/726)
**Status:** Resolved
**Severity:** High -- Blocks parsing of lop model entirely
**Discovered:** 2026-02-14 (Sprint 19, after Issues #722 fixed inline comments and lead operator)
**Resolved:** 2026-02-15 (Sprint 19)
**Affected Models:** lop (and any model that declares parameters with more indices than used at runtime)

---

## Problem Summary

The lop model fails to parse with the error:

```
Error: Parse error at line 222, column 1: Parameter 'rp' expects 3 indices, got 2 [context: expression]
  rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
  ^
```

The parameter `rp` is declared with 3 index positions (`rp(s,s,s)`) but is assigned and used with only 2 indices (`rp(ll,s)`). In GAMS, this is valid because `ll(s,s)` is a 2-dimensional set — when used as a single index position, GAMS implicitly expands it to fill 2 positions, making the effective index count 3 (matching the declaration). The parser enforced strict literal index count matching without accounting for multi-dimensional set expansion.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms
```

**Error output (before fix):**
```
Error: Unexpected error - Error: Parse error at line 222, column 1:
Parameter 'rp' expects 3 indices, got 2 [context: expression]
  rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
  ^

Suggestion: Provide exactly 3 indices to match the parameter declaration
```

---

## Root Cause

### GAMS multi-dimensional set index expansion

In `data/gamslib/raw/lop.gms`, lines 210-225:

```gams
Set ll(s,s) 'station pair representing a line';

Parameter
   rp(s,s,s)   'rank of node'
   lastrp(s,s) 'rank of the last node in line';

rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
lastrp(ll) = smax(s,rp(ll,s));
```

`ll` is declared as `Set ll(s,s)` — a 2-dimensional set. When `ll` is used as a single index position in `rp(ll,s)`, GAMS implicitly expands the 2 dimensions of `ll`, so the effective index count is 2 (from `ll`) + 1 (from `s`) = 3, matching `rp(s,s,s)`.

Similarly, `lastrp(ll)` has effective index count 2 (from `ll`), matching `lastrp(s,s)`.

### Parser enforcement

The parser validated that the literal number of index arguments matched the declared domain length, without accounting for multi-dimensional set expansion. Three locations performed this check:

1. Parameter assignments (`_handle_parameter_assignment`, line ~3362)
2. Variable references in expressions (`_make_symbol`, line ~4142)
3. Parameter references in expressions (`_make_symbol`, line ~4159)

---

## Resolution

Added `_effective_index_count()` helper method to the parser that computes the effective index count by summing each index's dimensionality: multi-dimensional sets (with `len(domain) > 1`) contribute their full dimensionality instead of 1.

Updated all three index count validation locations to use effective count as a fallback when the literal count doesn't match.

### Files Changed

1. **`src/ir/parser.py`**:
   - Added `_effective_index_count(indices)` helper method
   - Updated parameter assignment validation (line ~3362) to check effective count
   - Updated variable expression validation (line ~4142) to check effective count
   - Updated parameter expression validation (line ~4159) to check effective count

2. **`tests/parser/test_indexed_assignments.py`**:
   - Added `TestMultiDimSetIndexExpansion` test class with 3 tests:
     - `test_2d_set_as_single_index_in_assignment`: rp(ll,s) where ll is 2-D, rp is 3-D
     - `test_2d_set_as_single_index_fills_two_dims`: lastrp(ll) where ll is 2-D, lastrp is 2-D
     - `test_effective_count_still_rejects_true_mismatch`: effective count mismatch still errors

### Post-fix status

The lop model now parses past the original error. It encounters a subsequent unrelated error (`Symbol 'ilp' not declared` at line 312) due to model attribute assignments (`ilp.optCr = 0`) which are a separate unsupported parser feature.

---

## Additional Context

- The `rp` parameter is used extensively throughout the lop model (lines 254, 284, 351-355, 359)
- All subsequent uses reference `rp(ll,s)` or `rp(sol,s)` with 2 indices, never 3
- Both `ll(s,s)` and `sol(s,s)` are 2-dimensional sets used as compact indices
- This pattern is common in GAMS models with multi-dimensional subsets
