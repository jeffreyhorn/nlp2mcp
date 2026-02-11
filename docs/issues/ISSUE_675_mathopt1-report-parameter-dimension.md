# Mathopt1: Report Parameter Dimension Mismatch

**GitHub Issue:** [#675](https://github.com/jeffreyhorn/nlp2mcp/issues/675)

**Issue:** The mathopt1 model declares a parameter without explicit domain, but uses it with 2 indices. The parser interprets it as a scalar, causing Error 148/116.

**Status:** Open  
**Severity:** Medium - Model fails to compile  
**Affected Models:** mathopt1  
**Date:** 2026-02-10

---

## Problem Summary

GAMS allows declaring parameters without explicit domains and using them with any indices:
```gams
Parameter report 'solution summary report';
report('x1','global') = 1;
```

The current parser interprets `Parameter report;` as a scalar, but the assignments use it as 2-dimensional.

GAMS Errors:
- Error 116: Label is unknown
- Error 148: Dimension different - The symbol is referenced with more/less indices as declared

---

## Reproduction

### Test Case: mathopt1.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/mathopt1.gms -o data/gamslib/mcp/mathopt1_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams mathopt1_mcp.gms lo=2

# Check errors
grep -E "116|148" mathopt1_mcp.lst
```

**Error Output:**
```
**** 116  Label is unknown
**** 148  Dimension different - The symbol is referenced with more/less
         indices as declared
```

### Original Model

```gams
Parameter report 'solution summary report';
report('x1','global') = 1;
report('x2','global') = 1;
report('x1','solver') = x1.l;
report('x2','solver') = x2.l;
report('x1','diff')   = report('x1','global') - report('x1','solver');
report('x2','diff')   = report('x2','global') - report('x2','solver');
display report;
```

### Generated MCP (Wrong)

```gams
Scalars
    report /0.0/
;

report("x1","diff") = report("x1","global") - report("x1","solver");
```

The parameter is declared as a scalar but used with indices.

---

## Technical Details

### GAMS Dynamic Parameter Behavior

GAMS allows parameters without explicit domains. The dimension is inferred from usage:
- `Parameter p;` → scalar if used as `p = 5;`
- `Parameter p;` → indexed if used as `p(i,j) = 5;`

### Current Parser Behavior

`src/ir/parser.py` interprets `Parameter report;` as a scalar with empty domain `()`.

### What Would Be Needed

1. **Track indexed assignments**: When a parameter is used with indices in assignments, update its domain
2. **Infer domain from first use**: Examine all assignments to determine actual dimension
3. **Or require explicit domain**: Only support parameters with explicit domains

---

## Proposed Solution

### Option 1: Infer Domain from Assignments

After parsing, scan assignment statements to update parameter domains:
```python
def infer_parameter_domains(model_ir):
    for stmt in model_ir.statements:
        if isinstance(stmt, ParameterAssignment):
            param = model_ir.params.get(stmt.name)
            if param and len(param.domain) == 0:
                # Infer domain from assignment indices
                param.domain = infer_domain_from_indices(stmt.indices)
```

### Option 2: Skip Report Parameters

Report parameters (post-solve) typically reference `.l` values and aren't needed for MCP translation. Skip emitting them entirely.

---

## Related Issue

This is related to the "computed parameter assignment" handling. Report parameters that reference solution values (`.l`) shouldn't be emitted since the MCP format doesn't support them.

---

## Workaround

Manually add domain to the parameter in the source model:
```gams
Set vars /x1, x2/;
Set cols /global, solver, diff/;
Parameter report(vars, cols) 'solution summary report';
```

---

## References

- GAMS Parameter Syntax Documentation
- Sprint 18 Day 5 analysis
