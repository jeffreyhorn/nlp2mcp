# Emit: Alias Statement Ordering Causes Undefined Set Reference

**Status:** Open  
**Priority:** High  
**Affects:** cpack.gms, potentially other models using Alias with multi-dimensional sets  
**GitHub Issue:** [#621](https://github.com/jeffreyhorn/nlp2mcp/issues/621)

---

## Summary

The MCP emitter outputs set declarations before Alias statements, but some sets reference aliased indices. In `cpack_mcp.gms`, the set `ij(i,j)` is declared before `Alias(i, j)`, causing `j` to be undefined at parse time. This causes GAMS Error 140 "Unknown symbol".

## Symptoms

- **Model:** cpack.gms
- **Parse:** SUCCESS
- **Translate:** SUCCESS (generates MCP file)
- **Solve:** FAILS with GAMS compilation error

```
Error 140: Unknown symbol 'j'
```

## Root Cause

In `src/emit/original_symbols.py` (or similar emit module), the code emits declarations in a fixed order:
1. Sets
2. Alias statements
3. Parameters
4. etc.

But when a set like `ij(i,j)` references an alias `j`, the alias must be declared first.

**Problem Code in Generated MCP:**
```gams
Sets
    i /i1, i2, i3, i4, i5/
    ij(i,j)        * ERROR: j is not yet defined!
;

Alias(i, j);       * j is defined here, but too late
```

**Correct Code Should Be:**
```gams
Sets
    i /i1, i2, i3, i4, i5/
;

Alias(i, j);       * Define j first

Sets
    ij(i,j)        * Now j is valid
;
```

## Analysis

The original `cpack.gms` model (circle packing problem) uses:
- Set `i` for circles
- `Alias(i, j)` to create a second index for pairwise constraints
- Set `ij(i,j)` to track valid pairs

The GAMS language requires symbols to be defined before use. The emitter needs to analyze dependencies and order declarations accordingly.

## Proposed Solution

In the emit module:
1. Build a dependency graph of set declarations
2. Identify sets that reference aliased indices
3. Emit Alias statements before any sets that depend on them
4. Alternatively, split set declarations into pre-alias and post-alias groups

**Likely Code Locations:**
- `src/emit/original_symbols.py` - Symbol emission ordering
- `src/emit/emit_gams.py` - Main emission logic

## Reproduction Steps

```bash
# 1. Parse and translate cpack.gms
cd /Users/jeff/experiments/nlp2mcp
python -m src.cli data/gamslib/raw/cpack.gms -o /tmp/cpack_mcp.gms

# 2. Attempt to run with GAMS (will fail)
gams /tmp/cpack_mcp.gms

# 3. Observe Error 140 on the ij(i,j) set declaration
```

## Impact

- Models using Alias with multi-dimensional sets
- Common pattern in models with pairwise constraints
- cpack.gms is a circle packing optimization model from GAMSLIB

## Testing

1. Unit test: Verify Alias statements are emitted before dependent sets
2. Integration test: cpack.gms compiles successfully after fix
3. Regression test: Models without Alias dependencies still work

## References

- `data/gamslib/mcp/cpack_mcp.gms` - Generated MCP file showing the bug
- `data/gamslib/raw/cpack.gms` - Original GAMS model
- `src/emit/original_symbols.py` - Symbol emission code
- PR #619 review comment identifying this issue

---

**Created:** 2026-02-04  
**Sprint:** Sprint 17 Day 9
