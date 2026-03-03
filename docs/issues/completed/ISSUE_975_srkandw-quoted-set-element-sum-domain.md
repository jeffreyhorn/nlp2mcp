# srkandw: Quoted set element in sum domain not recognized

**GitHub Issue:** [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975)
**Model:** srkandw (GAMSlib SEQ=353, "Scenario Reduction - Kaut & Wallace")
**Error category:** `internal_error`
**Error message:** `Unknown set or alias 'time-2' referenced in sum indices [context: conditional assignment] [domain: ('n',)] (line 61, column 10)`
**Status:** Fixed

## Description

The parser fails when a quoted string set element (e.g., `'time-2'`) is used as a fixed index in a sum domain filter. In GAMS, `sum(tn('time-2',n), 1)` means "sum over all `n` where `tn('time-2',n)` is true", with `'time-2'` being a literal element of set `t`. The parser treats the quoted string as a symbol name and fails to resolve it.

## Root Cause

The parser's `_extract_domain_indices()` function in `src/ir/parser.py` extracted all identifiers from nested `index_list` nodes, including quoted identifiers (which match the grammar's `ESCAPED` pattern and are parsed as `index_simple` nodes with quoted `ID` tokens). These quoted strings are element literals that fix a dimension in the domain filter, not iteration variables. When passed to `_ensure_sets()`, they fail lookup because they aren't declared sets.

## Fix

Modified `_extract_domain_indices()` in `src/ir/parser.py` to skip quoted identifiers in `index_simple` nodes. Quoted IDs (detected by matching quote delimiters) are element literals, not domain iteration variables, and are excluded from the returned list. Also skip `index_string` nodes for the same reason.

### Files Changed

- `src/ir/parser.py`: Updated `_extract_domain_indices()` to skip quoted `index_simple` tokens and `index_string` nodes
- `tests/unit/gams/test_parser.py`: Added `TestQuotedElementInSumDomain` with 2 tests:
  - `test_quoted_element_filter_in_sum`: Verifies `sum(tn('time-2',n), 1)` parses
  - `test_quoted_element_in_conditional_assignment`: Verifies `leaf(n)$(sum(tn('time-2',n), 1)) = yes;` parses

## Verification

- All 3923 tests pass (2 new tests added)
- mypy, ruff, and black checks pass

## Additional Blockers (srkandw model)

Even after this fix, srkandw has additional blockers:

1. **Undeclared scenred library symbols**: The model uses `$libInclude scenred` (stripped by preprocessor) which defines `ScenRedParms` and `ScenRedReport` parameters. These are referenced at lines 126-134 and 139-150 but never declared locally.

2. **Curly-brace sum syntax**: Lines 141 and 178 use `sum{leaf(sn), sprob(sn)}` with curly braces. This syntax is partially supported (issue #355) but may fail with the specific `leaf(sn)` domain pattern.

## Related Issues

- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) -- srkandw: original `$libInclude` issue (partially resolved)
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) -- clearlak: `$libInclude scenred` (fixed)
- [#355](https://github.com/jeffreyhorn/nlp2mcp/issues/355) -- curly-brace sum syntax (partially implemented)
