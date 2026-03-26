# camshape: Alias-Related MCP Compilation Error

**GitHub Issue:** [#1147](https://github.com/jeffreyhorn/nlp2mcp/issues/1147)
**Status:** PARTIALLY FIXED
**Severity:** Medium — MCP compiles but has unmatched equation pairing
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** camshape

---

## Problem Summary

The camshape model (Camera Shape Design, COPS benchmark) uses `Alias(i, j)`
and fails at the MCP compilation stage rather than producing a solvable MCP.
Unlike the other 20 alias mismatch models that solve with incorrect objectives,
camshape fails earlier with a syntax or compilation error.

| Model | NLP Objective | MCP Status | Notes |
|-------|--------------|-----------|-------|
| camshape | 4.28 | path_syntax_error | Compilation failure |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/camshape.gms -o /tmp/camshape_mcp.gms
gams /tmp/camshape_mcp.gms lo=2
# Expected: Compilation or syntax error
```

---

## Root Cause Analysis

The camshape model uses:

```gams
Alias(i, j);
```

The MCP compilation error suggests that the generated GAMS code contains
invalid syntax, likely caused by:

1. **Malformed alias declarations**: The `_collect_ad_generated_aliases`
   function in the emitter may generate invalid `Alias` statements for
   AD-generated indices like `j__` or `i__`.

2. **Index conflict in emitted equations**: The `resolve_index_conflicts`
   function may fail to properly rename conflicting alias indices, producing
   GAMS code with ambiguous or duplicate index names.

3. **Pre-existing issue**: The camshape regression was confirmed as
   pre-existing (identical MCP output on both main and the alias-integration
   branch), suggesting the root cause predates the Sprint 23 Day 3 changes.

### Investigation Steps

1. Generate the MCP and inspect the GAMS compilation error message
2. Check for malformed `Alias` declarations or duplicate set names
3. Look for index conflict issues in the stationarity equations
4. Determine if this is a separate issue from the alias differentiation fix

---

## Files

- `src/emit/equations.py` — `_collect_ad_generated_aliases`
- `src/emit/expr_to_gams.py` — `resolve_index_conflicts`
- `src/emit/emit_gams.py` — Variable bounds emission
- `data/gamslib/raw/camshape.gms` — Source model

---

## Fix Applied (Partial)

**Root cause of compilation error ($141):** The emitter did not emit numeric per-element bounds from `lo_map`/`up_map` for variables. Domain-wide bounds like `r.lo(i) = R_min` were parsed and stored as per-element values in `lo_map`, but never emitted. Expression bounds in `lo_expr_map` (e.g., `r.lo('i1') = max(expr, r.lo("i1"))`) referenced the unassigned `r.lo("i1")` on the RHS, causing GAMS $141.

**Fix:** Added `lo_map`/`up_map` emission in `emit_gams.py` inside the `for kind in ("lo", "up", "fx")` loop, BEFORE expression bounds. When all values are identical, emits as domain-wide `r.lo(i) = 1;`. This ensures base bounds exist before expression overrides reference them.

**Result:** camshape MCP now compiles with 0 GAMS syntax/compilation errors ($141 resolved).

**Remaining issue:** MCP has unmatched equation pairing error: `stat_rdiff.rdiff has unmatched equation`. This is a separate MCP dimension mismatch where `rdiff` is declared with subset domain `i(j+1)` and the stationarity equation domain doesn't match. This requires separate investigation.
