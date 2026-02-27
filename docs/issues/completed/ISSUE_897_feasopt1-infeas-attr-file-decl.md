# feasopt1: `.infeas` variable attribute and `File` declaration

**GitHub Issue:** [#897](https://github.com/jeffreyhorn/nlp2mcp/issues/897)
**Model:** feasopt1 (GAMSlib SEQ=107, "An Infeasible Transportation Problem analyzed with Cplex option FeasOpt")
**Error category:** `parser_invalid_expression`
**Status:** RESOLVED
**Error message:** `Unsupported expression type: attr_access_indexed`

## Description

The parser fails on `.infeas` variable attribute access (e.g., `x.infeas`, `supply.infeas`, `demand.infeas`). The model also uses `File` declarations and `transport.optFile` model attribute assignment.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/feasopt1.gms')
"
```

## Relevant Code (lines 69–79)

```gams
solve transport using lp minimizing z;

display 'The first phase of the Simplex algorithm distributed the infeasibilities as follows',
         x.infeas, supply.infeas, demand.infeas;

$ifI %system.lp% == cplex  File fslv 'solver option file' / cplex.opt  /; transport.optFile = 1;
$ifI %system.lp% == gurobi File fslv 'solver option file' / gurobi.opt /; transport.optFile = 1;
$ifI %system.lp% == copt   File fslv 'solver option file' / copt.opt   /; transport.optFile = 1;
```

## Root Cause

1. `.infeas` is a variable/equation attribute that reports infeasibility values after a FeasOpt solve — it's not in the grammar's recognized attribute list
2. The grammar recognizes `.l`, `.m`, `.lo`, `.up`, `.fx`, `.prior`, `.scale` but not `.infeas`
3. `transport.optFile = 1` is a model attribute assignment — model-level attributes like `.optFile` are not supported
4. `File fslv 'description' / 'filename' /;` is a File declaration (same issue as srpchase)
5. `$ifI` is a case-insensitive `$if` directive — may need preprocessor support

## Related Issues (duplicate cluster: `attr_access` / model attributes)

This issue shares the `attr_access` root cause with:
- [#898](https://github.com/jeffreyhorn/nlp2mcp/issues/898) — mathopt4: `.modelStat` model attribute
- [#899](https://github.com/jeffreyhorn/nlp2mcp/issues/899) — trnspwl: `.off` set attribute

**Primary fix:** Add `attr_access` and `attr_access_indexed` handlers to the IR builder's `_expr()` method. A unified fix covering `.infeas`, `.modelStat`, `.solveStat`, `.optFile`, and `.off` would resolve all three issues.

The `File` declaration blocker is also shared with:
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) — srpchase: `File` declaration + `$libInclude` + `putClose`

## Resolution

Added `attr_access` and `attr_access_indexed` handlers to `_expr()` in `src/ir/parser.py`. These handle:
- Variable attributes (`.infeas`, etc.) → `VarRef` with attribute field
- Equation attributes → `EquationRef` with attribute field
- Model/other attributes (`.modelStat`, `.optFile`) → `ParamRef` placeholder

The `$ifI` directives are already handled by the preprocessor (`$ifi` lowercases to start with `$if`). The `File` declarations in feasopt1 are behind `$ifI %system.lp% == cplex` conditionals which evaluate to false, so they don't need parsing. The model now parses successfully.
