# Emitter: Statement ordering hoists `tmp1 = sum(leaf, ...)` before `leaf(n) = yes$(...)` assignment (clearlak)

**GitHub Issue:** [#1291](https://github.com/jeffreyhorn/nlp2mcp/issues/1291)
**Status:** OPEN — Sprint 25 Priority 2
**Severity:** High — Blocks 1 of 5 Sprint 25 Priority 2 recovered-translate models (`clearlak`)
**Date:** 2026-04-20
**Affected Models:** `clearlak` (observed); any model whose IR normalization hoists a reduction before the set's initialization statement
**Discovered:** Sprint 25 Prep Task 5 (recovered-translate leverage analysis)
**Labels:** `sprint-25`

---

## Problem Summary

The emitter's statement-ordering logic hoists `tmp1 = sum(leaf, nprob(leaf));` (line 64 of the generated MCP) above the `leaf(n)$(ord(n) > ...) = yes;` assignment (line 68). The `sum(leaf, ...)` reads `leaf` before it's been assigned, producing GAMS compile errors:

```
**** 352  Set has not been initialized         (leaf)
**** 149  Uncontrolled set entered as constant
**** 141  Symbol declared but no values have been assigned
```

## Reproduction

```bash
gams data/gamslib/mcp/clearlak_mcp.gms action=c lo=2
# -> 6 errors, compile rejected
```

## Source vs. Generated Order

**Source (clearlak.gms):**
- Line 72: `leaf(n)$(ord(n) > ...) = yes;` (assigned)
- Line 95: `tmp1 = sum {leaf, nprob(leaf)};` (used — after assignment, correct)

**Generated MCP (clearlak_mcp.gms):**
- Line 64: `tmp1 = sum(leaf, nprob(leaf));` (hoisted too early)
- Line 68: `leaf(n) = yes$(ord(n) > ...);` (assigned too late)

## Likely Root Cause

The IR's topological / dependency-aware assignment-ordering pass treats `tmp1 = sum(leaf, ...)` as an assignment with dependency only on `nprob` — but the implicit dependency on `leaf` being initialized is not modeled.

## Distinct From #1283

Verified via `PYTHONHASHSEED=0..2` regeneration: clearlak's compile errors are **deterministic**. This is NOT parser non-determinism (#1283) — it's a genuine emitter statement-ordering bug.

## Candidate Fixes

1. **Augment the dependency graph** with set-initialization dependencies.
2. **Preserve source order** for statements within `$onImplicitAssign` blocks.
3. **Topological sort on (set-init, data-assign)** pairs.

## References

- Sprint 25 Prep Task 5: `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Sibling new issues: #1289, #1290, #1292
- Related: #1279 (robustlp defobj scalar-widening) — also in `src/ir/normalize.py`

## Estimated Effort

3–4h

## Files Involved

- `src/ir/normalize.py` — dependency-graph / assignment-ordering pass
- `src/emit/emit_gams.py` — statement emission
- `tests/unit/ir/` — ordering regression test
- `data/gamslib/raw/clearlak.gms` — reference source
