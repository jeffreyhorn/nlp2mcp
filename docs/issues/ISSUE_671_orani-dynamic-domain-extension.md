# Orani: Dynamic Domain Extension Not Supported

**GitHub Issue:** [#671](https://github.com/jeffreyhorn/nlp2mcp/issues/671)

**Issue:** The orani model uses dynamic domain extension where computed parameter assignments add new elements to wildcard domains. This is not supported by the current emission logic.

**Status:** Open  
**Severity:** Medium - Affects 1 model  
**Affected Models:** orani  
**Date:** 2026-02-10

---

## Problem Summary

The orani model declares parameters with wildcard `*` domains and then extends those domains dynamically through assignment statements. The current emission logic infers wildcard elements only from the table data, missing dynamically added elements.

GAMS Errors:
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

# Check errors
grep -E "170|171" orani_mcp.lst | head -10
```

**Error Output:**
```
**** 170  Domain violation for element
**** 171  Domain violation for set
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

The table data only contains elements: `agric`, `manuf`, `families`, `exp`, `duty`

But the assignment adds `"total"` which is not in the inferred wildcard set.

### Generated MCP Issue

The emitter creates:
```gams
Sets
    wc_amc_d3 /agric, duty, exp, families, manuf/
;

Parameters
    amc(c,s,wc_amc_d3) /...data.../
;

amc(c,s,"total") = ...;  * ERROR: "total" not in wc_amc_d3
```

---

## Technical Details

### Current Wildcard Inference

`_infer_wildcard_elements()` in `src/emit/original_symbols.py` only looks at parameter values (table data):

```python
for key_tuple in param_def.values.keys():
    for pos in wildcard_positions:
        if pos < len(expanded_key):
            inferred[pos].add(expanded_key[pos])
```

This misses elements that are added via assignment statements like `amc(c,s,"total") = ...`.

### What Would Be Needed

1. **Scan assignment statements**: Look for parameter assignments that use indices not in the current domain
2. **Extend wildcard sets**: Add those new elements to the inferred wildcard set
3. **Handle computed element names**: Some assignments may compute element names dynamically

---

## Proposed Solution

### Option 1: Static Analysis of Assignments

Before emitting wildcard sets, scan all parameter assignment statements for new elements:

```python
def _infer_wildcard_elements_from_assignments(model_ir, param_name, wildcard_positions):
    """Also check assignment statements for additional elements."""
    elements = set()
    for stmt in model_ir.statements:
        if isinstance(stmt, ParameterAssignment) and stmt.name == param_name:
            for pos in wildcard_positions:
                if pos < len(stmt.indices):
                    idx = stmt.indices[pos]
                    if isinstance(idx, str):  # Literal element
                        elements.add(idx.strip('"').strip("'"))
    return elements
```

### Option 2: Use Universal Wildcard

Keep `*` as the domain instead of replacing with an inferred set:

```gams
Parameters
    amc(c,s,*) /...data.../
;
```

This allows any element but loses domain checking.

### Implementation Location

- `src/emit/original_symbols.py`: `_infer_wildcard_elements()` and emission logic

---

## Workaround

Currently none. The orani model cannot be translated to valid MCP format.

---

## Additional Issues in Orani

The orani model also has other emission issues:
- `theta`, `elevel`, `mlevel` may be incorrectly classified (scalars vs sets)
- Complex computed parameter assignments may have domain issues

---

## References

- GAMS Wildcard Domain Documentation
- Sprint 18 Day 5 analysis in SPRINT_LOG.md
