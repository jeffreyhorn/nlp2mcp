# pindyck: `display td.l` and `loop(t$to(t), ...)`

**GitHub Issue:** [#893](https://github.com/jeffreyhorn/nlp2mcp/issues/893)
**Model:** pindyck (GAMSlib SEQ=249, "Optimal Pricing and Extraction for OPEC")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: 'd'` at line 71, column 1
**Status:** FIXED
**Fixed:** Prior to Sprint 22 (parser/grammar improvements); model now parses and solves optimally

## Description

The lexer fails on `display td.l, s.l, cs.l, d.l, r.l;` — displaying `.l` (level) suffixed variable references. The model also uses `loop(t$to(t), ...)` with a dollar-filtered loop domain.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/pindyck.gms')
"
```

## Relevant Code (lines 66–76)

```gams
d.l (to) = td.l(to) - s.l(to);
p.l(to)  = 14;

loop(t$to(t), r.l(t) = r.l(t-1)-d.l(t));

display td.l, s.l, cs.l, d.l, r.l;

Model robert / all /;

solve robert maximizing profit using nlp;
```

## Root Cause

1. `display` with `.l` suffixed references (`td.l`, `s.l`, etc.) was not supported in the grammar
2. `loop(t$to(t), ...)` — dollar-filtered loop domain where `$to(t)` filters the loop index `t` to only elements in dynamic set `to` — was not supported

## Solution

Both features were added by grammar/parser improvements across Sprint 20-21:
- `display` with `.l`/`.m`/`.lo`/`.up`/`.fx` attribute references
- `loop` with dollar-filtered domain (`t$to(t)`)

The model now parses, translates to MCP, and solves optimally with GAMS PATH solver.
