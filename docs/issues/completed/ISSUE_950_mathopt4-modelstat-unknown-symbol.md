# mathopt4: m.modelStat emitted as unknown symbol ($140)

**GitHub Issue:** [#950](https://github.com/jeffreyhorn/nlp2mcp/issues/950)
**Model:** mathopt4 (GAMSlib SEQ=258)
**Status:** RESOLVED (already fixed by Issue #985 post-solve calibration skip)
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

## Root Cause

The `report` parameter contains expressions referencing both `VarRef(x1.l)` (variable level values) and `ModelAttrRef(m.modelStat)` (model attributes). Because `report` contains `VarRef` with `.l` attributes, it is classified as a "calibration" parameter. In the full MCP emission pipeline, post-solve calibration assignments are intentionally skipped (Issue #985) because they may divide by zero and are not needed for MCP correctness.

---

## Resolution

**Already fixed by:** Issue #985 (post-solve calibration skip), implemented prior to Sprint 22.

The `report` parameter's computed assignments (including the `m.modelStat` references) are classified as calibration parameters due to their `VarRef.l` content, and are excluded from the MCP output by the `varref_filter="no_varref_attr"` pass. The current MCP output contains zero `modelStat` references and compiles cleanly.

**Current pipeline status:** mathopt4 solves (MODEL STATUS 1, Optimal) with objective 15.356. The objective mismatch vs NLP (0.0) is expected — mathopt4 is a non-convex multi-solve model where the NLP finds a global optimum and the MCP/PATH finds a different valid KKT point.

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
