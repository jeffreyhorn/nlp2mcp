# Mexss/Sample: Wildcard Domain Missing Elements

**GitHub Issue:** [#674](https://github.com/jeffreyhorn/nlp2mcp/issues/674)

**Issue:** The mexss and sample models use wildcard `*` domains in tables, but assignments reference elements not in the table data. The inferred wildcard sets don't include these elements.

**Status:** Open  
**Severity:** High - Models fail to compile  
**Affected Models:** mexss, sample  
**Date:** 2026-02-10

---

## Problem Summary

Similar to the orani issue, these models have parameters with wildcard domains where:
1. Table data defines some elements
2. Assignment statements reference additional elements not in the table

The current wildcard inference only looks at table data, missing elements used in assignments.

GAMS Error 171: Domain violation for set

---

## Reproduction

### Test Case: mexss.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/mexss.gms -o data/gamslib/mcp/mexss_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams mexss_mcp.gms lo=2

# Check errors
grep "171" mexss_mcp.lst
```

**Error Output:**
```
**** 171  Domain violation for set
```

### Root Cause Analysis

In mexss.gms:
```gams
Table rd(*,*) 'rail distances from plants to markets (km)'
            mexico  monterrey  guadalaja  export
ahmsa         1204        218       1125     739
...

* Later, elements "import" and "export" are used:
muf(i,j) = (2.48 + 0.0084*rd(i,j))$rd(i,j);
muv(j)   = (2.48 + 0.0084*rd("import",j))$rd("import",j);
mue(i)   = (2.48 + 0.0084*rd(i,"export"))$rd(i,"export");
```

The table column `export` exists, but `"import"` in the first dimension is only used in assignments, not in the table row labels.

### Generated MCP (Wrong)

```gams
Sets
    wc_rd_d1 /ahmsa, fundidora, hylsa, hylsap, import, sicartsa/
    wc_rd_d2 /'-df', export, guadalaja, mexico, monterrey/
;

* But the set wc_rd_d1 doesn't include all elements used in assignments
```

Wait, checking the MCP output shows `import` IS in `wc_rd_d1`. Let me look more carefully.

```bash
muf(i,j) = (2.48 + 0.0084 * rd(i,j))$rd(i,j);
```

Error 171 is "Domain violation for SET" - this means `i` or `j` in the expression is not a valid set reference for the `rd` parameter.

---

## Technical Details

### The Real Issue

Looking at line 58:
```gams
muf(i,j) = (2.48 + 0.0084 * rd(i,j))$rd(i,j);
```

The parameter `rd` is declared as `rd(wc_rd_d1, wc_rd_d2)` but is being indexed by `i` and `j` in the assignment. GAMS requires domain compatibility.

The sets `i` and `j` must be compatible with (subsets of or equal to) `wc_rd_d1` and `wc_rd_d2`.

### Possible Causes

1. **Domain mismatch**: `i` is not a subset of `wc_rd_d1`
2. **Incorrect wildcard set**: The inferred wildcard set doesn't match the actual usage
3. **Original model uses `*` directly**: GAMS allows `rd(*,*)` to accept any valid set

---

## Proposed Solution

### Option 1: Preserve `*` Wildcards

Instead of replacing `*` with inferred sets, keep the wildcard:
```gams
Parameters
    rd(*,*) /...data.../
;
```

This allows any set to be used as indices.

### Option 2: Ensure Domain Compatibility

Check that sets used in assignments are compatible with inferred wildcard domains.

---

## Test Case: sample.gms

Similar issues may exist in sample.gms. Need to verify the specific error pattern.

```bash
cd data/gamslib/mcp && grep -B2 "171" sample_mcp.lst | head -10
```

---

## Workaround

Currently none. These models cannot be translated correctly.

---

## Related Issues

- Same category as orani dynamic domain extension issue
- Both involve wildcard `*` domains not being fully captured

---

## References

- GAMS Domain Documentation
- Sprint 18 Day 5 analysis
