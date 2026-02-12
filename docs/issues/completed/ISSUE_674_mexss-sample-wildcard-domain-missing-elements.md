# Mexss/Sample/Blend: Wildcard Domain Missing Elements

**GitHub Issue:** [#674](https://github.com/jeffreyhorn/nlp2mcp/issues/674)

**Issue:** The mexss, sample, and blend models use wildcard `*` domains in tables, but the emitter replaced them with generated named sets, causing domain violations (E171). While the original issue was filed for mexss/sample, the same root cause affected blend.

**Status:** ✅ RESOLVED  
**Severity:** High - Models failed to compile  
**Affected Models:** blend, sample (E171 fixed); mexss (E171 fixed, E149 remains)  
**Date:** 2026-02-10  
**Resolved:** 2026-02-11 (Sprint 18 Day 7, PR #680)

---

## Resolution Summary

### Sprint 18 Day 7 Fix: Wildcard Domain Preservation (PR #680)

The issue was resolved by preserving wildcard `*` domains in parameter declarations instead of replacing them with generated named sets.

**Before Fix:**
```gams
Sets
    wc_rd_d1 /ahmsa, fundidora, hylsa, hylsap, import, sicartsa/
    wc_rd_d2 /'-df', export, guadalaja, mexico, monterrey/
;
Parameters
    rd(wc_rd_d1, wc_rd_d2) /...data.../
;
* Error 171: rd indexed by incompatible sets
```

**After Fix:**
```gams
Parameters
    rd(*,*) /...data.../
;
* OK: wildcard accepts any set
```

### Model-Specific Results

| Model | E171 Status | Other Issues |
|-------|-------------|--------------|
| blend | ✅ FIXED | Now solves successfully |
| sample | ✅ FIXED | `path_solve_terminated` (numerical, not syntax) |
| mexss | ✅ FIXED | E149 remains (cross-indexed sums, ISSUE_670) |

---

## Original Problem Summary

The mexss and sample models have parameters with wildcard domains where:
1. Table data defines some elements
2. Assignment statements reference elements using different sets

The original emission logic replaced `*` wildcards with inferred named sets, which were incompatible with the sets used in assignments.

Original GAMS Error: 171 "Domain violation for set"

---

## Reproduction (Historical)

### Test Case: mexss.gms (before fix)

```bash
# Translate the model
nlp2mcp data/gamslib/raw/mexss.gms -o data/gamslib/mcp/mexss_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams mexss_mcp.gms lo=2

# Check errors (before fix: E171; after fix: E149)
grep -E "171|149" mexss_mcp.lst
```

---

## Technical Details

### Root Cause

In mexss.gms:
```gams
Table rd(*,*) 'rail distances from plants to markets (km)'
            mexico  monterrey  guadalaja  export
ahmsa         1204        218       1125     739
...

* Assignment uses sets i and j
muf(i,j) = (2.48 + 0.0084*rd(i,j))$rd(i,j);
```

The original emission logic inferred `rd(wc_rd_d1, wc_rd_d2)` which was incompatible with indexing by `i` and `j`. Preserving `rd(*,*)` allows any set indexing.

### Fix Location

- `src/emit/original_symbols.py`: Keep `*` in parameter domain declarations (PR #680)

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (affects mexss after E171 fix)
- **ISSUE_671**: Orani dynamic domain extension (similar root cause, also resolved by Day 7 fix)

---

## References

- Sprint 18 Days 5, 7 analysis in SPRINT_LOG.md
- PR #680: Fix E171 domain violation for wildcard parameter domains
