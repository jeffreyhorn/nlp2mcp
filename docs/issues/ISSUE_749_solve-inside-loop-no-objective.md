# Solve Statement Inside Loop Not Extracted — Model Has No Objective Function

**GitHub Issue:** [#749](https://github.com/jeffreyhorn/nlp2mcp/issues/749)
**Status:** Open
**Severity:** Medium — Blocks full pipeline for 2 NLP models
**Discovered:** 2026-02-13 (Sprint 19, after fixing Issues #746/#747)
**Affected Models:** ps5_s_mn, ps10_s_mn

---

## Problem Summary

Two Parts Supply models (ps5_s_mn, ps10_s_mn) fail with `Error: Model has no objective function defined` during the MCP pipeline. Both models define their `Solve` statements inside a `loop()` block rather than at the top level. The IR parser's `build()` dispatcher only walks top-level tree children, so `_handle_solve()` is never invoked for nested solve statements. The objective variable and sense are never recorded in `model_ir.objective`, causing the validation to fail.

Both models also use multi-model declarations with specific equation lists (`Model SB_lic /obj, rev, pc, licd/ SB_lic2 /obj, rev, pc, licd, mn/;`) rather than `Model m / all /;`.

---

## Reproduction

**Models:** ps5_s_mn (SEQ=377), ps10_s_mn (SEQ=375)

**Command:**
```bash
python -m src.cli data/gamslib/raw/ps5_s_mn.gms --diagnostics
python -m src.cli data/gamslib/raw/ps10_s_mn.gms --diagnostics
```

**Error output (both models):**
```
Error: Unexpected error - Error: Model has no objective function defined

Suggestion: Add an objective definition to your GAMS model:
  Variables z;
  Equations obj_def;
  obj_def.. z =e= <expression>;
  Model mymodel / all /;
  Solve mymodel using NLP minimizing z;
```

**GAMS source context (ps5_s_mn, lines 79–106):**
```gams
Model
   SB_lic  / obj, rev, pc, licd     /
   SB_lic2 / obj, rev, pc, licd, mn /;

* Options to solve models quickly
SB_lic.solveLink  = 5;
SB_lic2.solveLink = 5;

...

loop(t,
   p(i) = pt(i,t);

*  Solving the model w/o MN
   solve SB_lic maximizing Util using nlp;
   ...

*  Solving the model w/ MN
   solve SB_lic2 maximizing Util using nlp;
   ...
);
```

**IR parser output (ps5_s_mn):**
```python
declared_models: {'sb_lic2', 'sb_lic'}
model_name: None        # Never set — _handle_solve not called
model_uses_all: False
model_equations: ['obj', 'rev', 'pc', 'licd']
objective: None          # Never set — _handle_solve not called
```

---

## Root Cause

### 1. Build dispatcher only walks top-level children

The `_ModelBuilder.build()` method at `src/ir/parser.py:1000–1008` iterates over `tree.children` and dispatches to `_handle_{node.data}` methods. It only processes **top-level** AST nodes. Nodes nested inside other constructs (like `solve` inside `loop_stmt`) are not visited.

### 2. Loop handler stores body as raw AST

The `_handle_loop_stmt()` method at `src/ir/parser.py:3025` collects the loop body statements into `LoopStatement.body_stmts` as raw Lark `Tree` objects. It does not recurse into them to process `solve` or other statement types.

### 3. Objective validation requires `model_ir.objective`

The `validate_objective_defined()` function at `src/validation/model.py:44` checks `model_ir.objective is None` and raises `ModelError` if true. Since `_handle_solve` was never called, `objective` remains `None`.

---

## Fix Approach

### Option A: Extract solve info from loop body statements (Recommended)

After `_handle_loop_stmt()` stores the loop body, scan the stored `body_stmts` for `solve` tree nodes and process them with `_handle_solve()`. This would extract the objective variable and sense even when the solve is inside a loop.

The simplest implementation: in `_handle_loop_stmt()`, after collecting `body_stmts`, iterate over them and call the dispatcher for any `solve` nodes:

```python
for stmt in body_stmts:
    if isinstance(stmt, Tree) and stmt.data == "solve":
        self._handle_solve(stmt)
```

This only needs to extract the first solve's objective info — the pipeline only supports one objective per model.

**Complexity:** Low. A few lines added to `_handle_loop_stmt()`.

### Option B: Make build() recursively walk all statement nodes

Change the dispatcher to recursively walk the entire tree rather than just top-level children. This would automatically find solve statements at any nesting depth.

**Complexity:** Medium. Risk of processing statements that should be skipped (e.g., conditional solves in `if` blocks).

### Option C: Post-parse scan for unfound objective

After the initial tree walk, if `model_ir.objective` is still `None`, scan `loop_statements[*].body_stmts` for solve nodes and extract objective info.

**Complexity:** Low-medium. Separate pass but clean separation of concerns.

### Recommended approach

Option A is the simplest and most targeted fix. The solve statement inside a loop is still a valid solve statement — the loop just parameterizes the data. The objective variable and sense are the same regardless of the loop iteration.

---

## Additional Considerations

These models also use **multi-model declarations** (`Model SB_lic /obj, rev, pc, licd/ SB_lic2 /.../ ;`) with specific equation lists. The IR already tracks these correctly via `_handle_model_multi()`:
- `declared_models: {'sb_lic', 'sb_lic2'}`
- `model_equations: ['obj', 'rev', 'pc', 'licd']` (first model's list)
- `model_uses_all: False`

The `model_uses_all: False` flag means the pipeline uses the explicit equation list rather than all equations. This is already handled correctly — the only missing piece is the objective from the solve statement.

---

## Relevant Files

- `src/ir/parser.py:1000–1008` — `build()` dispatcher (top-level only)
- `src/ir/parser.py:2683–2724` — `_handle_solve()` (extracts objective)
- `src/ir/parser.py:3025–3077` — `_handle_loop_stmt()` (stores body as raw AST)
- `src/validation/model.py:44–56` — `validate_objective_defined()` (checks `objective is None`)
- `data/gamslib/raw/ps5_s_mn.gms:79–106` — Model/Solve declarations
- `data/gamslib/raw/ps10_s_mn.gms:79–106` — Model/Solve declarations (identical structure)
