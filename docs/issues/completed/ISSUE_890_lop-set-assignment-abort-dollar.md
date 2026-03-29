# lop: `Set ll(s,s)` and `= no` set assignment

**GitHub Issue:** [#890](https://github.com/jeffreyhorn/nlp2mcp/issues/890)
**Model:** lop (GAMSlib SEQ=192, "Line Optimization")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: 'S'` at line 208, column 1
**Status:** FIXED (already resolved by prior grammar/parser improvements)

## Description

The lexer fails on a multi-dimensional subset declaration `Set ll(s,s) 'starting point of each line'` and/or `= no` set assignment syntax. The model also uses `abort$card(...)` and 4-dimensional set data.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/lop.gms')
"
```

## Relevant Code (around line 208)

```gams
Set ll(s,s) 'starting point of each line' / #s.#s /;
```

## Root Cause

1. The grammar/lexer does not recognize the `Set ll(s,s)` subset definition where a set is defined as a subset of its own domain crossed with itself
2. The `= no` assignment syntax (used to exclude elements) is not supported
3. `abort$card(...)` with a dollar-condition on `abort` may also be unsupported

## Fix

The parse error was already resolved by prior grammar and parser improvements in earlier sprints (subset declarations, `#s.#s` notation, `= no` assignment syntax). The model now parses successfully:

- **Parse:** OK (18 sets, 9 variables, 12 equations)
- **Translation:** Not applicable — lop uses LP/MIP solve types (`solve sp minimzing spobj using lp`, `solve lopdt maximizing obj using mip`), not NLP. MCP conversion is not applicable for this model type.

No code changes required.
