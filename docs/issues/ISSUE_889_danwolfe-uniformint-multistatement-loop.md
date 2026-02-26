# danwolfe: `uniformInt` function and multi-statement loop lines

**GitHub Issue:** [#889](https://github.com/jeffreyhorn/nlp2mcp/issues/889)
**Model:** danwolfe (GAMSlib SEQ=79)
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '1'` at line 77, column 22

## Description

The lexer fails on `uniformInt(1,card(i))` — the `uniformInt` function is not recognized. Additionally, the model has multiple statements on one line inside a `loop` block, separated by `;`.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/danwolfe.gms')
"
```

## Relevant Code (lines 73–82)

```gams
cap(e)  = uniform(50,100)*log(card(k));

loop(k,
   kdem(k) = uniform(50,150);
   inum    = uniformInt(1,card(i)); bal(k,i)$(ord(i) = inum) = kdem(k);
   inum    = uniformInt(1,card(i)); bal(k,i)$(ord(i) = inum) = bal(k,i) - kdem(k);
   kdem(k) = sum(i$(bal(k,i) > 0), bal(k,i));
);
```

## Root Cause

1. `uniformInt` is not in the grammar's `FUNCNAME` terminal or built-in function list
2. Multiple statements on one line with `;` inside a `loop` body may confuse the parser

## Fix Approach

1. Add `uniformInt` to the grammar's `FUNCNAME` list in `gams_grammar.lark`
2. Verify multi-statement lines work correctly inside loop blocks
