# harker: Multi-dimensional set used as sum domain emits uncontrolled indices

**GitHub Issue:** [#1002](https://github.com/jeffreyhorn/nlp2mcp/issues/1002)
**Model:** harker (GAMSlib SEQ=85)
**Status:** FIXED
**Error category:** `path_syntax_error` (Subcategory C — $149)
**Severity:** Medium — model parses and translates but GAMS compilation fails (16 $149 errors)

---

## Problem Summary

The harker MCP output uses `sum(arc, ...)` where `arc(n,np)` is a 2-dimensional set. In the original GAMS, `sum(arc, pairs(arc,"kappa") * t(arc))` implicitly binds both `n` and `np` through the multi-dimensional set `arc`. Our parser expands the parameter/variable indices to `pairs(n,np,"kappa") * t(n,np)` but keeps `arc` as the single sum index, leaving `n` and `np` as uncontrolled set references.

---

## Root Cause

**Primary file:** `src/ir/parser.py` — `_handle_aggregation()` method
**Related component:** Sum domain handling for multi-dimensional sets

When parsing `sum(arc, ...)` where `arc(n,np)` is a 2D set:
1. The parser's `_make_symbol()` correctly expands body references: `t(arc)` → `t(n,np)`, `pairs(arc,...)` → `pairs(n,np,...)`
2. But the Sum node stored the original indices `("arc",)` instead of the expanded domain `("n", "np")`
3. The emitter faithfully output `sum(arc, ...)` with expanded body → GAMS $149 errors

---

## Resolution

Added domain-based expansion for multi-dimensional sets in `_handle_aggregation()` (parser.py):

1. When a sum index is a set with `len(set_def.domain) > 1`, expand the Sum domain to the constituent indices from `set_def.domain`
2. Add a `SetMembershipTest` dollar condition to restrict iteration to the subset (e.g., `$(arc(n,np))`)
3. Store the expanded indices in the Sum node instead of the original set name

**Before**: `sum(arc, pairs(n,np,"kappa") * t(n,np))` → $149 errors
**After**: `sum((n,np)$(arc(n,np)), pairs(n,np,"kappa") * t(n,np))` → valid GAMS

### Verification

- harker MCP compiles with zero GAMS errors
- Model solves to optimal (Solver Status 1, Model Status 1)
- All 3976 tests pass, 10 skipped, 1 xfailed
- The fix is in the parser, not the emitter — the Sum IR node now correctly stores expanded domain indices

---

## Notes

- The `in(l)` equation already worked correctly because its original GAMS uses `sum(arc(n,l), t(arc))` where the domain indices are explicitly given via `_extract_domain_indices()`
- The fix triggers only for sets whose `domain` field has more than one element, so single-dimensional sets are unaffected
- If an existing dollar condition is present from the parse tree, the set membership condition is AND-combined with it
