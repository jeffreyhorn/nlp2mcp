# turkey: parenthesized column groups in Table declaration

**GitHub Issue:** [#896](https://github.com/jeffreyhorn/nlp2mcp/issues/896)
**Model:** turkey (GAMSlib SEQ=395, "Turkey Agricultural Model with Risk")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: 's'` at line 201, column 54

## Description

The lexer fails on Table headers containing parenthesized column groups like `(chickpea,drybean,lentil)`. This is GAMS shorthand for grouping multiple set elements under a common column header, and the lexer/grammar does not support it.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/turkey.gms')
"
```

## Relevant Code (lines 196–206)

```gams
              buffalo .5497, mule .4442, poultry .0025                /;

Scalar evalp 'energy equivalent of pasture (tons per ha)' / .2 /;

Table eval(*,c) 'energy values in starch equivalent (kg per kg)'
                 wheat  corn  rye  barley  (chickpea,drybean,lentil)  sugarbeet  alfalfa  fodder
   product         .72   .78  .65     .71                                             .3      .4
   concentrat      .5         .24     .6                                     .6
   fodder          .13   .15  .17     .23                       .19                             ;
```

## Root Cause

1. `(chickpea,drybean,lentil)` is a parenthesized column group — GAMS interprets this as three separate columns that share the same data values in the rows
2. The table header parser expects plain identifiers separated by whitespace, not parenthesized groups
3. The data rows have blank entries for the grouped columns, and a single value applies to all members of the group

## Fix Approach

1. Extend the table header parser to recognize `(id, id, ...)` as a column group
2. When processing data rows, expand grouped columns so each member gets the same value
3. Alternatively, preprocess the table to expand grouped headers into individual columns
