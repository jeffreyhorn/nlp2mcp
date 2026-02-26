# pindyck: `display td.l` and `loop(t$to(t), ...)`

**GitHub Issue:** [#893](https://github.com/jeffreyhorn/nlp2mcp/issues/893)
**Model:** pindyck (GAMSlib SEQ=249, "Optimal Pricing and Extraction for OPEC")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: 'd'` at line 71, column 1

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

1. `display` with `.l` suffixed references (`td.l`, `s.l`, etc.) is not supported in the grammar — the `display_stmt` rule likely only handles plain identifiers
2. `loop(t$to(t), ...)` — dollar-filtered loop domain where `$to(t)` filters the loop index `t` to only elements in dynamic set `to` — may also be unsupported
3. The actual first failure may be earlier in the file (e.g., the `loop` or `.l` assignment lines)

## Fix Approach

1. Add `.l`, `.m`, `.lo`, `.up`, `.fx` attribute references to `display_stmt` item list
2. Verify `loop` with dollar-filtered domain (`t$to(t)`) is supported
3. These are common GAMS patterns that would unblock several other models
