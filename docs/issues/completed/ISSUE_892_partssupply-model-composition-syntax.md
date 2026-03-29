# partssupply: `/ m + mn /` model composition syntax

**GitHub Issue:** [#892](https://github.com/jeffreyhorn/nlp2mcp/issues/892)
**Model:** partssupply (GAMSlib SEQ=245, "Parts Supply Problem")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '+'` at line 125, column 53

## Description

The lexer fails on `Model m_mn 'parts supply model w/ monotonicity' / m + mn /;` — the `+` operator in a Model definition is used to combine equations from multiple models, and this syntax is not supported.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/partssupply.gms')
"
```

## Relevant Code (lines 120–130)

```gams
Model m 'parts supply model w/o monotonicity'
/ all - mn
$if %useic%   == 0 -ic
$if %uselicd% == 0 -licd
$if %uselicu% == 0 -licu
/;

Model m_mn 'parts supply model w/ monotonicity' / m + mn /;
```

## Root Cause

1. The grammar's `model_defn` rule only supports `/all/` or a simple equation list like `/ eq1, eq2 /`
2. The `+` operator for model composition (adding equations from one model to another) is not in the grammar
3. The `-` operator for model exclusion (e.g., `/ all - mn /`) is also likely unsupported
4. Conditional `$if` directives inside model definitions add further complexity

## Fix Applied

1. Extended `model_ref` grammar rule with `model_composition` (`ID "+" ID`) and `model_subtraction` (`ID "-" ID`) alternatives
2. Added handling in `_extract_model_refs()` to extract model names from composition/subtraction nodes
3. Updated validation to allow model names (from `model_equation_map`) in addition to equation names in model ref lists

partssupply now parses successfully (7 equations detected).
