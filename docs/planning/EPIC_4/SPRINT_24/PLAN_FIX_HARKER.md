# Plan: Fix harker MCP Compilation Error (Error 140)

**Goal:** Fix the GAMS compilation error in harker's MCP output so the
model can be solved by PATH.

**Estimated effort:** 1 hour
**Models unblocked:** harker (and potentially other models with model
attribute access in loop body assignments)

---

## Current State

harker translates successfully but the emitted MCP file fails GAMS
compilation with Error 140 (Unknown symbol) on this line:

```gams
objold = harkoli objVal ;
```

Should be:

```gams
objold = harkoli.objVal ;
```

The dot between the model name and attribute is missing.

---

## Root Cause

The harker model uses a `loop` with a filter condition and body
assignments that reference model attributes:

```gams
loop(iter$(abs(objold - harkoli.objVal) > 1e-5),
   objold = harkoli.objVal;
   solve harkoli maximizing obj using nlp;
   ...
);
```

The emitter has two code paths for loop body trees:

1. **`_loop_tree_to_gams()`** (line 2555 of `original_symbols.py`):
   Correctly handles `attr_access` nodes with `".".join(children)`.

2. **`_loop_tree_to_gams_subst_dispatch()`** (line 2957): Used by
   `emit_pre_solve_param_assignments()` to emit parameter assignments
   from before the first solve in solve-containing loops. This function
   handles many tree node types but **does NOT handle `attr_access`**,
   so it falls through to the fallback at line 3040:
   `" ".join(children)` — producing `harkoli objVal` instead of
   `harkoli.objVal`.

The `objold = harkoli.objVal` assignment is emitted by
`emit_pre_solve_param_assignments()` because the loop contains a solve
statement (so the full loop is skipped by `emit_loop_statements()`),
but the pre-solve assignment `objold = harkoli.objVal` is extracted
and emitted separately.

---

## Fix

### Primary: Add `attr_access` handling to `_loop_tree_to_gams_subst_dispatch()`

**File:** `src/emit/original_symbols.py`, line ~2957

Add a case for `attr_access` (and `attr_access_indexed`, `set_attr`)
to the dispatch function, mirroring the handling in `_loop_tree_to_gams()`:

```python
if data in ("set_attr", "attr_access"):
    return ".".join(_tree_to_gams_subst(c, subst) for c in node.children)
if data == "attr_access_indexed":
    name = _tree_to_gams_subst(node.children[0], subst)
    attr = _tree_to_gams_subst(node.children[1], subst)
    idx = _tree_to_gams_subst(node.children[2], subst)
    return f"{name}.{attr}({idx})"
```

This should also fix the `solPrint` assignment in the same loop body:
```gams
harkoli.solPrint = 0 ;  (currently: harkoli solPrint = 0 ;)
```

### Secondary: Check filter condition emission

The filter condition `$(abs(objold - harkoli.objVal) > 1e-5)` goes
through `_loop_tree_to_gams()` which already handles `attr_access`.
Verify this works correctly after the fix.

---

## Verification

```bash
python -m src.cli data/gamslib/raw/harker.gms -o /tmp/harker_mcp.gms --quiet

# Check the emitted line has the dot
grep "objold.*harkoli" /tmp/harker_mcp.gms
# Expected: objold = harkoli.objVal ;

# Compile check
gams /tmp/harker_mcp.gms lo=0 o=/tmp/harker_check.lst
grep "Error" /tmp/harker_check.lst
# Expected: no errors

# Solve
gams /tmp/harker_mcp.gms lo=3 o=/tmp/harker_solve.lst
grep "MODEL STATUS" /tmp/harker_solve.lst
# Expected: MODEL STATUS 1 or 2
```

---

## Other Models Affected

34 models have model attribute access (`.objVal`, `.modelStat`,
`.solveStat`, `.solPrint`) inside loops. Not all will hit this bug —
only those processed by `emit_pre_solve_param_assignments()` (loops
containing solve statements where pre-solve assignments are extracted).

Models to recheck after the fix: cesam2, danwolfe, dyncge, lmp2,
maxmin, meanvar, partssupply, saras, tricp (all currently failing
with syntax errors or no solve summary).

---

## Success Criteria

- [ ] `objold = harkoli.objVal ;` emitted with dot (not space)
- [ ] harker MCP compiles without GAMS errors
- [ ] harker solves to MODEL STATUS 1 or 2
- [ ] No test regressions (`make test` passes)
- [ ] Other models with loop-body attribute access unaffected or improved

---

## Files to Modify

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Add `attr_access`/`set_attr`/`attr_access_indexed` to `_loop_tree_to_gams_subst_dispatch()` |
| `tests/` | Add test for attr_access in loop body emission |
