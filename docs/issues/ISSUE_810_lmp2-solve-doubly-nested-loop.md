# lmp2: solve inside doubly-nested loop not extracted — no objective

**GitHub Issue:** [#810](https://github.com/jeffreyhorn/nlp2mcp/issues/810)

## Issue Type
IR Builder Limitation

## Affected Models
- lmp2 (GAMSlib model)
- lmp1, lmp3 (likely similar nested loop patterns)

## Description
`lmp2.gms` parses successfully but the solve statement is not extracted because it is inside a doubly-nested loop:

```gams
loop(c,
   ...
   loop(i,
      ...
      solve lmp2 minimizing obj using nlp;
   );
);
```

The current `_handle_solve` / loop extraction logic (Issue #749, now closed) only handles solve inside a single `loop()` level. When solve is nested two levels deep, the objective is not extracted, causing the model to fail at the translate stage with `model_no_objective_def`.

## Root Cause Analysis

The loop solve extraction in `src/ir/parser.py` (`_handle_loop`) was implemented in Sprint 18 (Issue #749) to handle the common GAMS pattern of `loop(i, ... solve ...)`. The implementation:

1. Detects a `solve` statement inside a `loop` body
2. Extracts the solve and its surrounding assignments out of the loop
3. Processes them as top-level statements

However, this only works for a single nesting level. When the solve is inside `loop(c, loop(i, solve ...))`, the outer loop's handler processes the inner loop as a single child node and doesn't recurse into it to find the solve.

## Reproduction
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/lmp2.gms')"
```

Minimal reproduction:
```gams
Sets c / c1*c3 /, i / i1*i5 /;
Variables obj, x(i);
Equations defobj;
defobj.. obj =e= sum(i, x(i));
Model lmp2 / all /;

loop(c,
   loop(i,
      solve lmp2 minimizing obj using nlp;
   );
);
```

## Expected Behavior
The solve statement should be extracted from doubly-nested loops and the objective function should be available in the IR.

## Proposed Fix

Extend the loop solve extraction to handle arbitrary nesting depth. Options:

1. **Recursive extraction**: When `_handle_loop` encounters an inner `loop` as a child, recursively check it for solve statements
2. **Flatten-then-extract**: Before solve extraction, flatten nested loops into a single representation
3. **Tree search**: Walk the entire loop subtree to find solve statements at any depth

Option 1 (recursive extraction) is likely the simplest and most targeted fix.

## Files to Review
- `src/ir/parser.py` — `_handle_loop` method, solve extraction logic
- `data/gamslib/raw/lmp2.gms` — doubly-nested loop pattern
- `data/gamslib/raw/lmp1.gms` — likely similar pattern
- `data/gamslib/raw/lmp3.gms` — likely similar pattern

## Related
- Issue #749 (closed) — original loop solve extraction implementation
- Issue #807 — mcp solve without objective (related metric)
- Sprint 20 Day 5 (WS4) — identified this limitation while fixing `$if set workSpace` inline guard bug

## Priority
Medium — affects 3 GAMSlib models (lmp1, lmp2, lmp3). The `model_no_objective_def` metric is currently at 4 (lmp1, lmp2, lmp3, mhw4dxx).

## Sprint Context
Discovered during Sprint 20 Day 5 while fixing the `$if set workSpace` inline guard preprocessor bug. The inline `$if` fix reduced `model_no_objective_def` from 14 to 4, but lmp1/lmp2/lmp3 require a different fix (nested loop extraction). Deferred to Sprint 21.
