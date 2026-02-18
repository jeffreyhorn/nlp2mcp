# Parser: Equation Multiplier Assignment (eqname.m = value) Not Supported

**Status:** OPEN
**Severity:** Low — blocks parse of otpop.gms; `eqname.m` assignments appear post-solve in reporting code and do not affect the optimization model
**Date:** 2026-02-18
**Affected Models:** otpop.gms
**GitHub Issue:** [#783](https://github.com/jeffreyhorn/nlp2mcp/issues/783)

---

## Problem Summary

`otpop.gms` fails to parse at line 125:

```
internal_error: Bounds reference unknown variable 'kdef' [context: expression] (line 125, column 1)
```

Lines 126-127:
```gams
kdef.m = 1;
zdef.m = 1;
```

`kdef` and `zdef` are **equation names** (not variables). The `.m` attribute on an
equation name accesses its **marginal value** (dual variable / shadow price) after a
solve. The assignment `kdef.m = 1;` sets the initial value or starting point for the
equation marginal.

The parser interprets `kdef` as a variable bound statement (`x.m` is a valid bound-type
accessor), fails to find `kdef` in the variable registry, and raises "Bounds reference
unknown variable".

---

## GAMS Code Pattern

```gams
Equation
   kdef  'capital definition'
   zdef  'profit definition';

Model otpop1 / dem, sup, adef, pdef, kdef, zdef, obj /;

solve otpop2 minimizing pdev using nlp;
solve otpop3 maximizing pi using nlp;

* Post-solve: set initial marginal values for equations
kdef.m = 1;
zdef.m = 1;

solve otpop1 maximizing pi using nlp;
```

In GAMS, `equation.m` accesses the marginal value (Lagrange multiplier) for the equation.
Assigning `kdef.m = 1` provides an initial value hint to the solver for the dual variable
associated with the `kdef` constraint.

The `.m`, `.l`, `.lo`, `.up`, `.fx` attributes are valid on both **variables** and
**equations** in GAMS. The parser currently only handles these attributes for variables.

---

## Root Cause

The bound/attribute assignment handler in the parser checks whether the identifier
before `.` is a known variable. When it is an equation name (like `kdef`), the check
fails with "unknown variable". The grammar and parser need to also allow `equation.m`
and `equation.l` assignments.

Additionally, `otpop.gms` also uses `p(t + (card(t) - ord(t)))` on lines 101 and 110,
which requires `offset_paren` support (added in Sprint 19 Day 13). After the
`offset_paren`/`offset_func` fix lands, the `kdef.m` issue becomes the next blocker.

---

## Expected Behavior

`kdef.m = 1;` should be recognized as an equation attribute assignment and either:
1. Stored as an initial marginal value hint (if the pipeline needs it), or
2. Silently ignored (for NLP-to-MCP purposes, equation marginal initial values are not
   needed to construct the KKT system — the KKT conditions provide the multiplier
   equations directly)

Option 2 is preferred: equation `.m` assignments are post-solve bookkeeping and do not
affect the MCP formulation.

---

## Proposed Fix

In the bound/attribute assignment handler, add a check: if the identifier resolves to a
known **equation name** (in `self.model.equations`), treat `.m` and `.l` assignments as
no-ops (or store in a separate `equation_level_values` dict). Do not raise "unknown
variable".

```python
# In _handle_bound_assignment or equivalent:
if var_name in self.model.equations:
    # Equation attribute assignment (.m, .l) — ignore for MCP purposes
    return
```

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/parser.py` | Bound/attribute assignment handler (~line 3515); `_apply_variable_bound()` |
| `data/gamslib/raw/otpop.gms` | Affected model; lines 101, 110, 126-127 |

---

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/otpop.gms')
"
# ParserSemanticError: Bounds reference unknown variable 'kdef' (line 125, column 1)
```

---

## Minimal Reproducer

```gams
Variable x;
Equation eq1;
eq1.. x =e= 1;
Model m / eq1 /;
solve m minimizing x using nlp;
eq1.m = 1;   * <-- This fails
```

---

## Related Issues

- Variable attribute assignments (`.lo`, `.up`, `.fx`, `.l`, `.m`) are handled for variables
- Equation attribute access (`.l`, `.m`) already supported in GAMS; parser gap is on the assignment side
- otpop also requires `offset_paren` fix (Sprint 19 Day 13) before this issue is reachable
