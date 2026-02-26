# nonsharp: `abort.noerror` with double-quoted string

**GitHub Issue:** [#891](https://github.com/jeffreyhorn/nlp2mcp/issues/891)
**Model:** nonsharp (GAMSlib SEQ=233, "Synthesis of General Distillation Sequences")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '"'` at line 442, column 37

## Description

The lexer fails on `abort.noerror$(not relax.marginals) "solver did not provide marginals, cannot continue"`. Two issues: (1) `abort.noerror` is a GAMS `abort` suffix form, and (2) the error message uses double quotes `"..."` instead of single quotes.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/nonsharp.gms')
"
```

## Relevant Code (around line 442)

```gams
   if(((relax.modelStat <> %modelStat.optimal%)        and
       (relax.modelStat <> %modelStat.locallyOptimal%) and
       (relax.modelStat <> %modelStat.feasibleSolution%)), kend = 0);

   abort.noerror$(not relax.marginals) "solver did not provide marginals, cannot continue";
```

## Root Cause

1. `abort.noerror` is a GAMS suffix on `abort` that suppresses the error exit — the grammar only recognizes bare `abort` or `abort$condition`
2. Double-quoted strings `"..."` are not recognized by the lexer (GAMS allows both single and double quotes for strings)
3. The model also uses `relax.modelStat` and `relax.marginals` — model attribute access patterns

## Fix Approach

1. Add `abort.noerror` (and potentially `abort.noError`) to the grammar as an abort variant
2. Add double-quoted string support to the lexer's STRING terminal
3. Alternatively, add a preprocessor step to convert double quotes to single quotes
