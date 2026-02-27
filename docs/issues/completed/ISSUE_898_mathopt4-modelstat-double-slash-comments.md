# mathopt4: `.modelStat` model attribute and `//` comments

**GitHub Issue:** [#898](https://github.com/jeffreyhorn/nlp2mcp/issues/898)
**Model:** mathopt4 (GAMSlib SEQ=202, "MathOptimizer Example 4")
**Error category:** `parser_invalid_expression`
**Status:** RESOLVED
**Error message:** `Unsupported expression type: attr_access`

## Description

The parser fails on `m.modelStat` — accessing the `.modelStat` attribute of a model object. The model also uses `//` end-of-line comments.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/mathopt4.gms')
"
```

## Relevant Code (lines 44–54)

```gams
solve m using nlp min obj;

report('one','x1.l') = x1.l;
report('one','x2.l') = x2.l;
report('one','modelstat') = m.modelStat;

x1.l = -2; x2.l = -1; // leads to local optimum
report('two','x1_0') = x1.l;
report('two','x2_0') = x2.l;
```

## Root Cause

1. `m.modelStat` is a model-level attribute access — the grammar's `attr_access` rule does not recognize model attributes like `.modelStat`, `.solveStat`, `.objVal`, etc.
2. `//` end-of-line comments are a GAMS feature (similar to `$eolcom` but using `//` by default in newer GAMS) — the lexer may not strip these
3. The parser sees `attr_access` but the IR builder's `_expr()` method does not have a handler for it

## Related Issues (duplicate cluster: `attr_access` / model attributes)

This issue shares the `attr_access` root cause with:
- [#897](https://github.com/jeffreyhorn/nlp2mcp/issues/897) — feasopt1: `.infeas` attribute + `File` declaration (primary issue)
- [#899](https://github.com/jeffreyhorn/nlp2mcp/issues/899) — trnspwl: `.off` set attribute

**Primary fix:** Add `attr_access` and `attr_access_indexed` handlers to the IR builder's `_expr()` method. Fixing #897 should also resolve the `attr_access` portion of this issue. This issue has an additional blocker: `//` end-of-line comments.

## Resolution

Added `attr_access` handler to `_expr()` in `src/ir/parser.py`. Model attributes like `m.modelStat` are handled as `ParamRef` placeholders (they return numeric values used for reporting). The `//` end-of-line comments are already handled by the existing `strip_eol_comments()` preprocessor step (mathopt4 has `$eolCom //` at line 21). The model now parses successfully.
