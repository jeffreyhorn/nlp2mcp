# Emit: Invalid Parameter Data Entries with Set Name as Element

**Status:** Open  
**Priority:** High  
**Affects:** trussm.gms, potentially other models with complex parameter initialization  
**GitHub Issue:** [#622](https://github.com/jeffreyhorn/nlp2mcp/issues/622)

---

## Summary

The MCP emitter generates invalid parameter data entries where a set name is used as an element label. In `trussm_mcp.gms`, the parameter `f(j,k)` includes entries `j.k2 0.0, j.k3 0.0` where `j` is the set name, not a valid element of set `j` (which contains `/j1, j2, j3, j4/`). This causes GAMS Error 170 "Domain violation" or introduces unintended set elements.

## Symptoms

- **Model:** trussm.gms
- **Parse:** SUCCESS
- **Translate:** SUCCESS (generates MCP file)
- **Solve:** FAILS with GAMS compilation error or incorrect results

```
Error 170: Domain violation for element 'j'
```

Or GAMS silently adds `j` as a new element to set `j`, corrupting the model.

## Root Cause

In the parameter data emission code (likely `src/emit/original_symbols.py`), when serializing parameter values, the code is incorrectly using the set/index variable name instead of iterating over actual set elements.

**Problem Code in Generated MCP:**
```gams
Sets
    j /j1, j2, j3, j4/
    k /k1, k2, k3/
;

Parameters
    f(j,k) /j1.k1 0.0008, j1.k2 1.0668, j1.k3 0.2944, 
            j2.k1 0.0003, j2.k2 0.0593, j2.k3 -1.3362, 
            j3.k1 -0.0006, j3.k2 -0.0956, j3.k3 0.7143, 
            j4.k1 -1.0003, j4.k2 -0.8323, j4.k3 1.6236, 
            j.k2 0.0, j.k3 0.0/    * BUG: 'j' is not an element!
;
```

**Correct Code Should Be:**
```gams
Parameters
    f(j,k) /j1.k1 0.0008, j1.k2 1.0668, j1.k3 0.2944, 
            j2.k1 0.0003, j2.k2 0.0593, j2.k3 -1.3362, 
            j3.k1 -0.0006, j3.k2 -0.0956, j3.k3 0.7143, 
            j4.k1 -1.0003, j4.k2 -0.8323, j4.k3 1.6236/
    * Remove the invalid j.k2 and j.k3 entries entirely
;
```

## Analysis

The invalid entries `j.k2 0.0, j.k3 0.0` appear to be:
1. A bug where the index variable name `j` is being emitted instead of actual element labels
2. Possibly from default value initialization logic gone wrong
3. Or from incorrectly parsing/storing parameter data from the original model

The original `trussm.gms` model (truss optimization) likely doesn't have these entries - they're being introduced during the MCP generation.

## Proposed Solution

In the parameter emission code:
1. Validate that all element labels in parameter data are actual members of their respective sets
2. Filter out entries where the "element" is actually the set/index variable name
3. Add a sanity check that emitted labels don't match set names

**Likely Code Locations:**
- `src/emit/original_symbols.py` - Parameter data emission
- `src/emit/emit_gams.py` - Data serialization

## Reproduction Steps

```bash
# 1. Parse and translate trussm.gms (from repo root)
python -m src.cli data/gamslib/raw/trussm.gms -o /tmp/trussm_mcp.gms

# 2. Inspect the generated file
grep "j.k2\|j.k3" /tmp/trussm_mcp.gms
# Should show the invalid entries

# 3. Attempt to run with GAMS (will fail or produce wrong results)
gams /tmp/trussm_mcp.gms
```

## Impact

- Models with multi-dimensional parameters
- Can cause silent data corruption if GAMS auto-extends the set
- trussm.gms is a truss design optimization model from GAMSLIB

## Testing

1. Unit test: Verify parameter emission only uses valid set elements
2. Unit test: Verify set names are never emitted as element labels
3. Integration test: trussm.gms compiles successfully after fix
4. Regression test: Other models with parameters still work

## References

- `data/gamslib/mcp/trussm_mcp.gms` - Generated MCP file showing the bug
- `data/gamslib/raw/trussm.gms` - Original GAMS model
- `src/emit/original_symbols.py` - Parameter emission code
- PR #619 review comment identifying this issue

---

**Created:** 2026-02-04  
**Sprint:** Sprint 17 Day 9
