# MCP Models: Solve Without Objective Function Fails

**GitHub Issue:** [#807](https://github.com/jeffreyhorn/nlp2mcp/issues/807)

## Issue Type
Parser Error

## Affected Models
- cesam (GAMSlib model)
- spatequ (GAMSlib model)

## Description
MCP (Mixed Complementarity Problem) models do not require an objective function, but the current grammar requires objective specification in solve statements. The grammar expects:

```gams
solve modelname using mcp minimizing|maximizing objvar;
```

However, valid GAMS syntax for MCP allows:

```gams
solve modelname using mcp;
```

## Error Details

### cesam
```
Error: Parse error at line 538, column 28: Unexpected character: ';'
  solve m_SAMENTROP using mcp;
                             ^
```

### spatequ
```
Error: Parse error at line 163, column 25: Unexpected character: ';'
  solve P2R3_MCP using mcp;
                          ^
```

## Root Cause
The `solve_stmt` grammar rule in `src/gams/gams_grammar.lark` requires an objective specification:

```lark
solve_stmt: "Solve"i ID obj_sense ID "using"i solver_type SEMI     -> solve
          | "Solve"i ID "using"i solver_type obj_sense ID SEMI     -> solve
obj_sense: MINIMIZING_K | MAXIMIZING_K
```

Both variants require `obj_sense ID` (objective direction + variable).

## Reproduction
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/cesam.gms')"
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/spatequ.gms')"
```

## Expected Behavior
MCP models should be able to solve without specifying an objective function. The parser should accept:
- `solve modelname using mcp;` (no objective)
- `solve modelname using mcp minimizing objvar;` (with objective)

## Proposed Fix
Extend `solve_stmt` in `src/gams/gams_grammar.lark` to make objective optional for certain solver types (MCP, CNS):

```lark
solve_stmt: "Solve"i ID obj_sense ID "using"i solver_type SEMI     -> solve
          | "Solve"i ID "using"i solver_type obj_sense ID SEMI     -> solve
          | "Solve"i ID "using"i solver_type SEMI                  -> solve_no_objective
```

Update IR builder in `src/ir/parser.py` to handle `solve_no_objective` tree node (set objective to None or empty).

## Related
- GAMS documentation: MCP and CNS solvers do not require objective functions
- This is distinct from Sprint 20's `model_no_objective_def` category (which is about models without defined objective equations)

## Files to Modify
- `src/gams/gams_grammar.lark` (solve_stmt rule)
- `src/ir/parser.py` (add _handle_solve_no_objective or extend _handle_solve)
- `tests/unit/gams/test_parser.py` (add test for MCP solve without objective)

## Test Case
```gams
Equations eq1;
Variables x;
Model m / eq1.x /;
solve m using mcp;
```

## Priority
Medium - affects 2 GAMSlib models that successfully parse model definitions but cannot solve

## Sprint Context
Discovered during Sprint 20 Day 4 (WS3 Lexer Phase 1) after fixing Subcat L model exclusion patterns. These models now parse their model definitions successfully but fail at the solve statement.
