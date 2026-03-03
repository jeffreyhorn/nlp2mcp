# srpchase: Set assignment with arithmetic index offset on LHS

**GitHub Issue:** [#976](https://github.com/jeffreyhorn/nlp2mcp/issues/976)
**Model:** srpchase (GAMSlib SEQ=356, "Scenario Tree Construction Example")
**Error category:** `internal_error`
**Error message:** `Parameter 'ancestor' not declared [context: expression] (line 39, column 1)`
**Status:** Fixed

## Description

The parser fails when a set assignment uses an arithmetic index offset expression on the LHS. In `ancestor(n,n-card(leaf))$stage(n,'t3') = yes;`, the second index `n-card(leaf)` is an `IndexOffset` expression. The parser's assignment handler detects the `IndexOffset`, skips the set assignment path, and falls through to the parameter check, which fails because `ancestor` is a set.

## Root Cause

In `src/ir/parser.py`, the `_handle_assign()` method had a guard:

```python
if symbol_name in self.model.sets and not has_lead_lag:
```

When `has_lead_lag` was `True` (due to `IndexOffset` indices), the code skipped the set assignment branch and fell through to the parameter assignment branch, which raised `Parameter 'ancestor' not declared`. The assumption that `IndexOffset` indices cannot appear in set assignments was incorrect -- GAMS allows set assignments with computed indices.

## Fix

1. **`src/ir/parser.py`**: Removed the `and not has_lead_lag` guard from the set assignment condition, allowing `IndexOffset` indices in set assignments.

2. **`src/ir/symbols.py`**: Updated `SetAssignment.indices` type from `tuple[str, ...]` to `tuple[str | IndexOffset, ...]` to accept `IndexOffset` objects.

3. **`src/emit/original_symbols.py`**: Updated set assignment emission to handle `IndexOffset` indices:
   - Extract only string indices for `domain_vars` (skip `IndexOffset` objects)
   - Use `_format_mixed_indices()` to properly emit `IndexOffset` expressions in index strings

### Files Changed

- `src/ir/parser.py`: Removed `not has_lead_lag` guard
- `src/ir/symbols.py`: Updated `SetAssignment.indices` type annotation
- `src/emit/original_symbols.py`: Updated emission to handle mixed indices
- `tests/unit/gams/test_parser.py`: Added `TestSetAssignmentWithIndexOffset` with 2 tests:
  - `test_set_assign_with_index_offset`: Verifies `ancestor(n, n-card(leaf)) = yes;` parses
  - `test_set_assign_with_quoted_element_and_offset`: Verifies both simple and offset set assignments coexist

## Verification

- All 3923 tests pass (2 new tests added)
- mypy, ruff, and black checks pass

## Additional Blockers (srpchase model)

Even after this fix, srpchase has additional blockers:

1. **Undeclared scenred library symbols**: The model uses `$libInclude scenred` (stripped by preprocessor) which defines `ScenRedParms`, `ancestor` modifications, and `tree_con`. These are referenced at lines 77-82 but some are never declared locally.

## Related Issues

- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) -- srpchase: original `$libInclude`/`File`/`putClose` issue (partially resolved)
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) -- clearlak: `$libInclude scenred` (fixed)
