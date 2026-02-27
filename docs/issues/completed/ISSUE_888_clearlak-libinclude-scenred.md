# clearlak: `$libInclude scenred` directive not supported

**GitHub Issue:** [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888)
**Status:** FIXED — Sprint 21 Day 11, PR [#925](https://github.com/jeffreyhorn/nlp2mcp/pull/925)
**Fixed:** 2026-02-26
**Model:** clearlak (GAMSlib SEQ=64)
**Error category:** `internal_error`
**Error message:** `Parameter 'ScenRedParms' not declared [context: expression] (line 142, column 1)`

## Description

The model uses `$libInclude scenred.gms` (line 140) to include the GAMS scenario reduction library. The preprocessor does not resolve `$libInclude` directives, so the symbols defined in the included library (e.g., `ScenRedParms`, `ScenRedReport`) are never declared.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/clearlak.gms')
"
```

## Relevant Code (lines 138–148)

```gams
$if set noscenred $goTo noscenreduction

* now let's shrink the node set
$libInclude scenred.gms

ScenRedParms('num_leaves')     = sum(leaf, 1);
ScenRedParms('num_random')     = 1;
ScenRedParms('num_nodes')      = card(n);
ScenRedParms('num_time_steps') = card(t);
```

## Root Cause

The preprocessor (`src/ir/preprocessor.py`) does not handle `$libInclude` directives. These reference GAMS system library files that are not part of the model source.

## Fix Approach

1. Add `$libInclude` to `strip_unsupported_directives()` so the directive line is removed
2. Pre-declare the standard symbols from the scenred library (ScenRedParms, ScenRedReport, etc.) as known external symbols, OR
3. Add a "lenient" parse mode that treats undeclared symbols as implicit parameter references

## Related Issues (duplicate cluster: `$libInclude`)

This issue shares a root cause with:
- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) — srkandw: `$ libInclude scenred` (space after `$`)
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) — srpchase: `$libInclude scenred` + `File`/`putClose`

**Primary fix:** Add `$libInclude` (case-insensitive, with optional spaces) to `strip_unsupported_directives()` in the preprocessor. Fixing this issue should also resolve #894 and the `$libInclude` portion of #895. Note that #895 has additional blockers (`File` declaration, `putClose`) and #894 has an additional blocker (`sum{...}` curly-brace syntax).

---

## Resolution (Sprint 21 Day 11, 2026-02-26)

### Fix Applied

Added `$libInclude` directive stripping to `strip_unsupported_directives()` in
`src/ir/preprocessor.py`. The fix:

1. Matches `$libInclude` case-insensitively, with optional spaces after `$`
2. Replaces the directive line with a comment: `* Stripped: $libInclude scenred.gms`
3. Handles variants: `$libInclude`, `$LIBINCLUDE`, `$libinclude`, `$ libInclude`

### Code Change

```python
# In src/ir/preprocessor.py, inside strip_unsupported_directives():
# Issue #888: Strip $libInclude directives (GAMS system library includes).
if stripped_lower.startswith("$libinclude") or re.match(
    r"^\$\s+libinclude", stripped_lower
):
    filtered.append(f"* Stripped: {stripped}")
    continue
```

### Tests Added

Three unit tests in `tests/unit/ir/test_preprocessor.py`:
- `test_strip_libinclude_directive`: basic `$libInclude scenred.gms`
- `test_strip_libinclude_case_insensitive`: `$LIBINCLUDE`, `$libinclude`
- `test_strip_libinclude_with_space`: `$ libInclude`

### Post-Fix Status

After this fix, the `$libInclude` directive is stripped, but clearlak still fails at parse
time with `ParserSemanticError: Parameter 'ScenRedParms' not declared`. This is expected —
the library symbols (`ScenRedParms`, `ScenRedReport`, etc.) are defined in the included
`scenred.gms` library file and are not available to the parser. The model advances from
`internal_error` (preprocessor crash) to `ParserSemanticError` (undeclared symbols).

Full resolution of clearlak would require either pre-declaring scenred library symbols or
implementing a lenient parse mode for undeclared symbols.
