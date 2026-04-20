# Emitter: Multiplier naming exceeds GAMS 63-char identifier limit on models with synthetic element hashes (ferts)

**GitHub Issue:** [#1290](https://github.com/jeffreyhorn/nlp2mcp/issues/1290)
**Status:** OPEN — Sprint 25 Priority 2
**Severity:** Medium — Blocks 1 of 5 Sprint 25 Priority 2 recovered-translate models (`ferts`)
**Date:** 2026-04-20
**Affected Models:** `ferts` (observed); any model with hashed element names combined into multiplier names
**Discovered:** Sprint 25 Prep Task 5 (recovered-translate leverage analysis)
**Labels:** `sprint-25`

---

## Problem Summary

The emitter's multiplier naming scheme concatenates the original equation name with element suffixes to produce GAMS-unique identifiers. For `ferts`, this produces names up to 67 characters long — exceeding GAMS's 63-char identifier limit — triggering `Error 109` and `Error 108` at MCP compile.

## Reproduction

```bash
gams data/gamslib/mcp/ferts_mcp.gms action=c lo=2
# -> many × Error 109 / Error 108
```

## Example (67 chars)

```
nu_xi_fx_sulf_acid_c8324d9c_kafr_el_zt_4b0342d5_kafr_el_zt_4b0342d5
```

Decomposition: `nu_` (3) + `xi_fx_sulf_acid_c8324d9c_` (25) + `kafr_el_zt_4b0342d5_` (20) + `kafr_el_zt_4b0342d5` (19) = 67 chars > 63 limit.

## Likely Root Cause

The synthetic-element-hashing pass (used when element names contain GAMS-illegal characters like `-` in `kafr-el-zt` → `kafr_el_zt_<hash>`) adds 8-char hex hashes per transformed element. Two-element products with a prefix easily exceed 63 chars.

## Candidate Fixes

1. **Shorter hash format:** reduce 8-char hex to 6 chars.
2. **Hash the combined name:** if name exceeds 63 chars, hash the full multiplier name to a canonical form + registry for diagnostics.
3. **Abbreviate element names** with length-aware shortening on re-use.

## References

- Sprint 25 Prep Task 5: `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Sibling new issues: #1289, #1291, #1292

## Estimated Effort

2–3h

## Files Involved

- `src/kkt/naming.py` (or wherever synthetic multiplier names are constructed)
- `src/emit/emit_gams.py`
- `tests/unit/kkt/` — name-length regression test
- `data/gamslib/raw/ferts.gms` — reference source
