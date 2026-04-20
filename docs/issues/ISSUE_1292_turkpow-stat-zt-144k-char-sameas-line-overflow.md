# Emitter: stat_zt in turkpow_mcp.gms emits 144k-char line from `sameas()` cross-product (line-length overflow)

**GitHub Issue:** [#1292](https://github.com/jeffreyhorn/nlp2mcp/issues/1292)
**Status:** OPEN — Sprint 25 Priority 2
**Severity:** Medium–High — Blocks 1 of 5 Sprint 25 Priority 2 recovered-translate models (`turkpow`)
**Date:** 2026-04-20
**Affected Models:** `turkpow` (observed); any model with large alias-cross-product bodies emitted without line-wrapping
**Discovered:** Sprint 25 Prep Task 5 (recovered-translate leverage analysis)
**Labels:** `sprint-25`

---

## Problem Summary

The `stat_zt` stationarity equation in `turkpow_mcp.gms` (line 200) is emitted as a **single line 144,454 characters long**. GAMS caps input lines at 80,000 characters; compile fails with cascading errors:

```
**** 98   Non-blank character(s) beyond max input line length (80000)
**** 140  Unknown symbol
**** 170  Domain violation for element
**** 8, 37, 409  syntax-recovery errors
```

## Reproduction

```bash
awk 'NR==200 {print length($0)" chars"}' data/gamslib/mcp/turkpow_mcp.gms
# -> 144454 chars

gams data/gamslib/mcp/turkpow_mcp.gms action=c lo=2
# -> 18 errors, compile rejected
```

## What's On Line 200

A stationarity equation with hundreds of `sameas(m, ...) and sameas(v, ...) and sameas(b, ...) and sameas(t, ...)` clauses joined by `or`, enumerating every valid 4-tuple `(m, v, b, t)` for which the underlying multiplier applies.

## Likely Root Cause

The alias-aware AD / KKT assembly pass generates a `sameas()`-guarded expression per valid index combination (instead of using a compact set-membership guard). The emitter then writes each clause inline and joins with `or`, producing the overflow.

## Candidate Fixes

1. **Line wrapping** (minimum viable): insert `\n` at each `or` separator when accumulated line length exceeds ~10,000 chars. Cheap, localized, no semantic change. 1–2h.
2. **Guard simplification**: replace the Cartesian-product `sameas()` enumeration with a precomputed set membership (`$(mvbt(m,v,b,t))`). Broader benefit but much bigger change. 4–6h.
3. **Hybrid**: line wrapping now to unblock; flag simplification as Sprint 26+ optimization.

## Relation to Alias-AD Fix (Sprint 25 Priority 1)

Task 2's Pattern A fix addresses the derivative-chain logic that produces `sameas()` guards. After Pattern A lands, the specific clause count may change, but turkpow's enumeration is driven by index-set cardinality, not the Pattern A bug. **Not subsumed** by Task 2.

## References

- Sprint 25 Prep Task 5: `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Sibling new issues: #1289, #1290, #1291
- Related: Sprint 25 Unknown 1.5 (sameas guard validation)

## Estimated Effort

1–2h (Option 1, line wrapping); 4–6h (Option 2, guard simplification).

## Files Involved

- `src/emit/equations.py` or `src/emit/emit_gams.py` — equation emission with line wrapping
- `src/kkt/stationarity.py` — sameas-guard generation (for Option 2)
- `tests/unit/emit/` — line-length regression test
- `data/gamslib/raw/turkpow.gms` — reference source
