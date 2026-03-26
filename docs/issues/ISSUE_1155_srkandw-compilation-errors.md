# srkandw: Multiple GAMS Compilation Errors in Generated MCP

**GitHub Issue:** [#1155](https://github.com/jeffreyhorn/nlp2mcp/issues/1155)
**Status:** OPEN
**Severity:** High — generated MCP does not compile
**Date:** 2026-03-25
**Affected Models:** srkandw

---

## Problem Summary

The generated MCP for srkandw has three compilation errors that prevent GAMS from solving it:

1. **$125 "Set is under control already"** (line 54): `leaf(n) = yes$(sum(n$(tn('time-2',n)), 1));` — GAMS rejects using `n` as both the outer set control variable in `leaf(n)` and as a sum index in `sum(n$(...), 1)`. **Note:** PR #1153 partially addressed this by preserving the literal co-index and filtering `n` from sum_indices, but the emitted form may still produce an empty `Sum(index_sets=())` which needs to be collapsed to a non-iterating conditional or the original subset-domain form.

2. **$311 "ord function needs second argument"** (line 65): `ScenRedParms('reduction_method') = ord('0-default') - 1;` — `ord()` with a quoted literal is invalid GAMS. This is GUSS-related post-solve code that should be stripped during preprocessing.

3. **$141** (line 184): `nlp2mcp_obj_val = cost.l;` — variable attribute reference error.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/srkandw.gms -o /tmp/srkandw_mcp.gms --skip-convexity-check
gams /tmp/srkandw_mcp.gms lo=2
```

**GAMS output:**
```
****                      $125
**** 125  Set is under control already
****                                                    $311
**** 311  The function ord('string',expr) needs the second argument
****                         $141
****                           $257
**** 257  Solve statement not checked because of previous errors
```

---

## Error Details

### Error 1: $125 — Set under control (leaf/sum index conflict)

**Generated line:**
```gams
leaf(n) = yes$(sum(n$(tn('time-2',n)), 1));
```

**Original GAMS:**
```gams
leaf(n)$(sum(tn('time-2',n), 1)) = yes;
```

The original uses `tn('time-2',n)` as the sum domain directly — GAMS interprets this as iterating over the `tn` subset filtered by `'time-2'` in the first dimension. The parser correctly preserves `n` as the sum index now, but emits it in a way where `n` is both the `leaf(n)` set control and the `sum(n$...)` iteration variable.

**Fix:** The emitter should either:
- Emit the sum domain as `tn('time-2',n)` directly (without expanding to `sum(n$(tn('time-2',n)), 1)`)
- OR use an alias for the inner sum index to avoid the control conflict

### Error 2: $311 — ord() with string literal

**Generated line:**
```gams
ScenRedParms('reduction_method') = ord('0-default') - 1;
```

This is from the GUSS (General Uniform Scenario Solver) post-solve block in the original model. It should be stripped during preprocessing as it's not part of the mathematical model.

**Fix:** Add `ScenRedParms` or the GUSS block to the preprocessor's directive stripping list, or detect `ord()` with string literal arguments and strip those statements.

### Error 3: $141 — cost.l attribute reference

**Generated line:**
```gams
nlp2mcp_obj_val = cost.l;
```

This likely fails because `cost` is the objective variable and `.l` (level) attribute access doesn't work in the MCP context before solving.

**Fix:** This is in the nlp2mcp epilogue code. Either guard it or ensure the variable is properly declared before use.

---

## Root Cause

Three separate issues:
1. **Parser/emitter**: Sum domain with literal-subset not emitted in GAMS-compatible form
2. **Preprocessor**: GUSS-related post-solve code not stripped
3. **Emitter**: Objective value capture uses invalid attribute access

**Affected files:**
- `src/emit/emit_gams.py` or `src/emit/original_symbols.py` — sum domain emission
- `src/ir/preprocessor.py` — GUSS/ScenRedParms stripping
- `src/emit/emit_gams.py` — objective value epilogue

---

## Fix Approach

1. For $125: Emit `sum(tn('time-2',n), 1)` with the subset as the domain directly, or introduce an alias to avoid the set control conflict. (~2h)
2. For $311: Strip GUSS-related statements (`ScenRedParms`, `scenred_*`) in the preprocessor. (~1h)
3. For $141: Fix objective value capture in the emitter epilogue. (~0.5h)

**Total effort estimate:** 3-4 hours
