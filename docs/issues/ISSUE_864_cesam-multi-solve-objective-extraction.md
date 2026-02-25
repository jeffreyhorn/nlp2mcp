# Cesam: Multi-Solve Model Objective Extraction Failure

**GitHub Issue:** [#864](https://github.com/jeffreyhorn/nlp2mcp/issues/864)
**Status:** OPEN
**Severity:** Medium — Model parses but objective not found (model_no_objective_def)
**Date:** 2026-02-24
**Affected Models:** cesam

---

## Problem Summary

The cesam model parses successfully (fixed in Sprint 21 Day 1 by fixing sameas string literal
handling) but fails validation with `model_no_objective_def`. The model contains multiple
solve statements including both NLP and MCP solves, and the parser fails to extract the
objective variable from the NLP solve statements.

---

## Error Details

```
ModelError: Error: Model has no objective function defined
```

The `ModelIR.objective` field is `None` after parsing.

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
ir = parse_file('data/gamslib/raw/cesam.gms')
print(f'Objective: {ir.objective}')
print(f'Solve stmts: {ir.solve_stmts if hasattr(ir, \"solve_stmts\") else \"N/A\"}')
"
```

---

## Root Cause

The cesam model has multiple solve statements:

```gams
solve SAMENTROP using nlp minimizing dentropy;
solve m_SAMENTROP using mcp;
solve SAMENTROP2 using nlp minimizing dentropy;
```

The parser encounters:
1. `solve SAMENTROP using nlp minimizing dentropy` — NLP solve with objective `dentropy`
2. `solve m_SAMENTROP using mcp` — MCP solve with **no** objective
3. `solve SAMENTROP2 using nlp minimizing dentropy` — NLP solve with objective `dentropy`

The parser likely processes solve statements sequentially, with later statements overwriting
earlier ones. The MCP solve (which has no objective by design) overwrites the objective from
the first NLP solve, leaving `objective = None`.

Alternatively, the parser may only handle a single solve statement and not support
multi-solve models at all.

---

## Suggested Fix

**Option A: Use the first NLP solve's objective**

When processing solve statements, only extract the objective from NLP-type solves (not MCP
solves). If multiple NLP solves exist with the same objective variable, use that. Ignore MCP
solves when setting the objective.

**Option B: Support multi-solve models**

Store all solve statements in the IR and let the emitter choose the appropriate one. The MCP
emitter would use the MCP solve statement, while validation would check that at least one
NLP solve provides an objective if the final solve type requires it.

**Option C: Last-NLP-wins semantics**

Track the objective from the most recent NLP solve statement, ignoring MCP solves. This
matches GAMS semantics where the objective comes from the NLP solve.

**Effort estimate:** ~1-2h

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/parser.py` | Fix objective extraction for multi-solve models |
| `src/ir/model_ir.py` | Possibly store multiple solve statements |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.7 documents the original parse blocker (sameas)
- **Issue #807** (completed): MCP solve without objective — related but different
