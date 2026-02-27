# mathopt4: m.modelStat emitted as unknown symbol ($140)

**GitHub Issue:** [#950](https://github.com/jeffreyhorn/nlp2mcp/issues/950)
**Model:** mathopt4 (GAMSlib SEQ=258)
**Status:** OPEN
**Error category:** `gams_compilation_error`
**Severity:** Low — model parses and translates but GAMS compilation fails (3 errors)

---

## Problem Summary

The mathopt4 MCP output includes `m.modelStat` references that GAMS cannot resolve. In the original NLP, `m` is the model name and `.modelStat` is a model attribute returning the solve status. In the MCP output, the original model `m` no longer exists (it was transformed into `mcp_model`), so `m.modelStat` is an undefined reference.

---

## Error Details

```
  74  report("one","modelstat") = m.modelStat;
****                                        $140
**** 140  Unknown symbol
```

Lines 74, 79, 84, 89 all reference `m.modelStat` in computed parameter assignments to `report`.

The secondary errors are cascading:
- `$257` (line 165): Solve statement not checked due to prior errors
- `$141` (line 168): `obj.l` not assigned (no successful solve)

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/mathopt4.gms -o /tmp/mathopt4_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/mathopt4_mcp.gms lo=2
grep '^\*\*\*\*' mathopt4_mcp.lst
```

---

## Root Cause

The parser now handles `m.modelStat` via the `attr_access` handler in `_expr()`, creating a `ParamRef("m.modelStat")`. The emitter then outputs `m.modelStat` literally. However:

1. In the MCP output, the original model `m` is not declared — only `mcp_model` exists
2. Model attributes (`.modelStat`, `.solveStat`, `.objVal`) are runtime values from the solver, not compile-time constants
3. The original model uses `m.modelStat` in `report` parameter assignments between multiple solve statements — these are multi-solve loop patterns that our single-solve MCP transformation doesn't preserve

---

## Fix Options

- **Option A (simple):** Strip/comment out assignments that reference model attributes. Since `m.modelStat` is only used for reporting (not for optimization), removing these assignments won't affect the MCP solution. Add a filter in the emitter to skip computed parameter assignments containing model attribute references.
- **Option B (complete):** Map original model name to `mcp_model` in model attribute references, and declare `mcp_model` before the attribute is accessed. This is more correct but complex.
- **Option C (preprocessor):** Strip model attribute assignments at the IR level, treating them as display-only statements similar to how `display` is handled.

**Recommended:** Option A — filter out model attribute assignments in the emitter.

---

## GAMS Source Context

```gams
solve m using nlp min obj;

report('one','x1.l') = x1.l;
report('one','x2.l') = x2.l;
report('one','modelstat') = m.modelStat;  $ line 49

x1.l = -2; x2.l = -1; // leads to local optimum

solve m using nlp min obj;  $ second solve

report('two','modelstat') = m.modelStat;  $ line 54
```
