# srkandw: `$ libInclude scenred` (space after $)

**GitHub Issue:** [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894)
**Model:** srkandw (GAMSlib SEQ=353, "Stochastic Programming Scenario Reduction")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '$'` at line 136, column 1

## Description

The lexer fails on `$     libInclude scenred kandw scen_red n tree prob na sprob dem` — a `$libInclude` directive with spaces between `$` and `libInclude`. The preprocessor does not handle `$libInclude` directives at all, and the space-separated form adds another layer of complexity.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/srkandw.gms')
"
```

## Relevant Code (lines 131–141)

```gams
*     these parms control the tree output from ScenRed
*     at least one of the following two parameters is required
      ScenRedParms('red_num_leaves') = ord(run);
*     ScenRedParms('red_percentage') = 0.5;

$     libInclude scenred kandw scen_red n tree prob na sprob dem

      sn(n) = sprob(n);
      display ScenRedParms, ScenRedReport, sprob, sn;

      psum = sum{leaf(sn), sprob(sn)};
```

## Root Cause

1. `$libInclude` is not handled by the preprocessor's `strip_unsupported_directives()` — same issue as clearlak (SEQ=64)
2. GAMS allows spaces between `$` and the directive name (e.g., `$     libInclude` is valid)
3. The symbols defined by the scenred library (`ScenRedParms`, `ScenRedReport`, `sprob`, etc.) are never declared, causing downstream errors
4. The model also uses `sum{...}` with curly braces instead of parentheses

## Related Issues (duplicate cluster: `$libInclude`)

This issue shares a root cause with:
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (primary issue)
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) — srpchase: `$libInclude scenred` + `File`/`putClose`

**Primary fix:** Add `$libInclude` (case-insensitive, with optional spaces) to `strip_unsupported_directives()` in the preprocessor. Fixing #888 should also resolve the `$libInclude` portion of this issue. This issue has an additional blocker: `sum{...}` curly-brace syntax.

## Fix Approach

1. Add `$libInclude` (case-insensitive, with optional spaces) to `strip_unsupported_directives()` — shared with #888, #895
2. Pre-declare standard scenred library symbols, OR use a lenient mode for undeclared symbols
3. Add `sum{...}` curly-brace syntax support to the grammar (equivalent to `sum(...)`)
