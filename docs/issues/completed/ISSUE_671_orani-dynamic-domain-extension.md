# Orani: Dynamic Domain Extension Not Supported

**GitHub Issue:** [#671](https://github.com/jeffreyhorn/nlp2mcp/issues/671)

**Issue:** The orani model uses dynamic domain extension where computed parameter assignments add new elements to wildcard domains. This was not supported by the original emission logic, but was partially resolved by PR #680 (Day 7 wildcard fix). The remaining blocker is E149 from cross-indexed sums (ISSUE_670).

**Status:** FULLY RESOLVED — E170/E171 fixed (Sprint 18 Day 7 PR #680), E149 fixed (Sprint 19 via ISSUE_670 fix). Orani now translates successfully.  
**Severity:** Medium - Affects 1 model  
**Affected Models:** orani  
**Date:** 2026-02-10  
**Updated:** 2026-02-11 (Sprint 18 Day 9)

---

## Sprint 18 Day 7-8 Update

### Day 7 Fix: Wildcard Domain Preservation (PR #680)

The Sprint 18 Day 7 fix (PR #680) preserves wildcard `*` domains in parameter declarations instead of replacing them with generated named sets. This resolves the E170/E171 domain violation errors.

**Before Day 7 Fix:**
```gams
Sets
    wc_amc_d3 /agric, duty, exp, families, manuf/
;
Parameters
    amc(c,s,wc_amc_d3) /...data.../
;
amc(c,s,"total") = ...;  * ERROR: "total" not in wc_amc_d3
```

**After Day 7 Fix:**
```gams
Parameters
    amc(c,s,*) /...data.../
;
amc(c,s,"total") = ...;  * OK: "total" allowed by wildcard
```

### Remaining Issue: E149 Cross-Indexed Sums (ISSUE_670)

After the Day 7 fix resolves E170/E171 errors, the orani model still fails with E149 "Uncontrolled set entered as constant" due to cross-indexed sums in the stationarity equations. This is an architectural issue documented in ISSUE_670.

**Current Status:**
- E170/E171: ✅ FIXED (Day 7 wildcard preservation)
- E149: ❌ ARCHITECTURAL (cross-indexed sums)

---

## Original Problem Summary

The orani model declares parameters with wildcard `*` domains and then extends those domains dynamically through assignment statements. The original emission logic inferred wildcard elements only from the table data, missing dynamically added elements.

Original GAMS Errors (before Day 7 fix):
- Error 170: Domain violation for element
- Error 171: Domain violation for set

---

## Reproduction

### Test Case: orani.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/orani.gms -o data/gamslib/mcp/orani_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams orani_mcp.gms lo=2

# Check errors (after Day 7 fix, expect E149 only)
grep -E "149" orani_mcp.lst | head -10
```

### Root Cause Analysis

In orani.gms:

```gams
Table amc(c,s,*) 'accounting matrix for commodities'
*                       industries  households  exports  import
                       agric manuf    families      exp    duty
   food.domestic          10     8          17       19
   ...

* Later, a new element "total" is added dynamically:
amc(c,s,"total") = sum(i, amc(c,s,i)) + amc(c,s,"families") + amc(c,s,"exp") + amc(c,s,"duty");
```

The Day 7 fix preserves `amc(c,s,*)` which allows the dynamic `"total"` element.

---

## Resolution Summary

| Error | Status | Fix |
|-------|--------|-----|
| E170/E171 (Domain violation) | ✅ FIXED | Day 7 wildcard preservation (PR #680) |
| E149 (Uncontrolled set) | ❌ ARCHITECTURAL | Requires ISSUE_670 fix |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums produce uncontrolled set error 149 (architectural)
- **ISSUE_674**: mexss/sample wildcard domain (fully resolved by Day 7 fix)

---

## References

- Sprint 18 Days 5, 7-8 analysis in SPRINT_LOG.md
- PR #680: Wildcard domain preservation fix
