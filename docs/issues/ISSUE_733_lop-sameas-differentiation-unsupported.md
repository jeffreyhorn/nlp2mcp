# Differentiation fails for `sameas()` function (lop)

**GitHub Issue:** [#733](https://github.com/jeffreyhorn/nlp2mcp/issues/733)
**Status:** Open
**Severity:** Medium -- Blocks MCP translation of lop model (after Issue #732 fix)
**Discovered:** 2026-02-15 (Sprint 19, after Issue #732 fixed domain mismatch)
**Affected Models:** lop, and potentially asyncloop, cesam, circpack, gqapsdp, popdynm, sddp, sroute (8 gamslib models use `sameas`)

---

## Problem Summary

The lop model fails during differentiation with:

```
Error: Invalid model - Differentiation not yet implemented for function 'sameas'.
Supported functions: power, exp, log, log10, log2, sqrt, sin, cos, tan, abs, sqr, smin, smax.
Note: abs() requires --smooth-abs flag (non-differentiable at x=0).
```

After Issue #732 fixed the domain mismatch, the pipeline advances to the differentiation stage where `sameas(s,s1)` in the `balance` equation is not recognized by the derivative rule engine.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms --skip-convexity-check
```

**Error output:**
```
Error: Invalid model - Differentiation not yet implemented for function 'sameas'.
Supported functions: power, exp, log, log10, log2, sqrt, sin, cos, tan, abs, sqr, smin, smax.
Note: abs() requires --smooth-abs flag (non-differentiable at x=0).
```

---

## Root Cause

### `sameas` in the lop model

The `balance` equation (line 144 of `lop.gms`) uses `sameas`:

```gams
balance(s,s1)..
   sum(d(s1,s2), f(s,d)) =e= sum(d(s2,s1), f(s,d)) + sameas(s,s1)*card(s) - 1;
```

`sameas(s,s1)` is a GAMS built-in function that returns 1 if set elements `s` and `s1` are the same, 0 otherwise. It acts as a Kronecker delta. `card(s)` returns the cardinality of set `s`. Both are constants with respect to decision variables.

### Missing derivative rule

`src/ad/derivative_rules.py` implements differentiation for mathematical functions (`power`, `exp`, `log`, `sqrt`, `sin`, `cos`, etc.) but has no entry for `sameas`. Since `sameas` does not depend on any decision variable (it operates on set elements), its derivative with respect to any variable is 0.

Similarly, `card` is also a set operation (returns set cardinality as a constant), and its derivative is also 0.

### Scope of impact

The `balance` equation belongs to model `sp` (shortest path), which is solved as LP. However, the tool currently processes ALL equations in the file regardless of which model/solve statement is targeted. The `sameas` call is in an equation that wouldn't need KKT transformation in a model-aware pipeline.

---

## Fix Approach

### Option A: Add derivative rules for set operations (recommended)

Add `sameas` (and `card`, `ord`) to the derivative rule engine as zero-derivative functions. These are constant with respect to all decision variables:

```python
# In src/ad/derivative_rules.py
# sameas(a,b) returns 0 or 1 based on set membership - constant w.r.t. variables
# card(s) returns set cardinality - constant w.r.t. variables
# ord(s) returns element position - constant w.r.t. variables
"sameas": lambda args, dargs: Const(0),
"card": lambda args, dargs: Const(0),
"ord": lambda args, dargs: Const(0),
```

### Option B: Treat unrecognized non-variable functions as constants

In the differentiation engine, if a `Call` node's arguments contain no decision variables, treat the entire call as a constant (derivative = 0). This would handle `sameas`, `card`, `ord`, and any other set/data functions without needing explicit rules for each.

### Option C: Model-scoped equation processing

Only process equations belonging to the selected model/solve statement. This would skip `balance` entirely since it belongs to `sp` (LP), not the NLP/MCP model being processed. However, this is a larger architectural change.

---

## Affected gamslib models using `sameas`

| Model | `sameas` usage context |
|---|---|
| lop | `sameas(s,s1)*card(s)` in flow balance constraint |
| asyncloop | Unknown |
| cesam | Unknown |
| circpack | Unknown |
| gqapsdp | Unknown |
| popdynm | Unknown |
| sddp | Unknown |
| sroute | Fails at parse time (undefined symbol) |

---

## Additional Context

- The `balance` equation is part of model `sp` which is solved as LP, not NLP
- `sameas` is parsed as a `Call` node in the AST (not a `ParamRef`)
- Some models (sroute) fail to parse `sameas` entirely, indicating inconsistent handling
- `card` appears in the same expression; it may also lack a derivative rule
