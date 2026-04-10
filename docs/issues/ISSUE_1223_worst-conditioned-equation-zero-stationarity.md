# worst: Conditioned Equation Variables Produce Zero Stationarity

**GitHub Issue:** [#1223](https://github.com/jeffreyhorn/nlp2mcp/issues/1223)
**Status:** OPEN — KKT formulation bug (conditioned equation gradient)
**Severity:** Medium — Variables d1/d2 get trivial 0=0 stationarity equations
**Date:** 2026-04-07
**Last Updated:** 2026-04-07
**Affected Models:** worst

---

## Problem Summary

The worst model (GAMSlib SEQ=111, "Financial Optimization: Risk Management")
has variables `d1(i,t,j)` and `d2(i,t,j)` that appear in equations `dd1` and
`dd2`, which are conditioned with `$pdata(i,t,j,"strike")`. The stationarity
builder produces `stat_d1(i,t,j).. 0 =E= 0;` and `stat_d2(i,t,j).. 0 =E= 0;`
— the conditioned gradients evaluate to zero across all terms. GAMS then
reports Error 483 ("Mapped variables have to appear in the model") because
d1/d2 don't appear in their paired stationarity equations.

---

## Root Cause

Variables `d1` and `d2` only appear in two types of equations:

1. **Defining equations** `dd1`, `dd2` — conditioned with `$pdata(i,t,j,"strike")`:
   ```gams
   dd1(i,t,j)$pdata(i,t,j,"strike")..
      d1(i,t,j) =e= (log(f(i,t)/pdata(i,t,j,"strike")) + 0.5*sqr(q(t))*tdata(t,"term"))
                     / (q(t)*sqrt(tdata(t,"term")));
   dd2(i,t,j)$pdata(i,t,j,"strike")..
      d2(i,t,j) =e= d1(i,t,j) - q(t)*sqrt(tdata(t,"term"));
   ```

2. **Call/put equations** `c`, `p` — where d1/d2 appear inside `errorf()`:
   ```gams
   c(i,j,t) =e= exp(...) * (f(i,t)*errorf(d1(i,t,j)) - strike*errorf(d2(i,t,j)));
   p(i,j,t) =e= exp(...) * (strike*errorf(-d2(i,t,j)) - f(i,t)*errorf(-d1(i,t,j)));
   ```

The stationarity builder should produce non-zero gradients from equations `c`
and `p` (via `errorf'(d1) = dnorm(d1)`), but these contributions are missing
from the stationarity output, resulting in `0 =E= 0`.

The issue may be that:
- The `errorf()` derivative is not implemented or returns 0
- The conditioned equations `dd1`/`dd2` mask the gradient contributions
- The dollar condition causes ALL stationarity terms to be wrapped and
  evaluated to zero

---

## Reproduction

```bash
# Translate
.venv/bin/python -m src.cli data/gamslib/raw/worst.gms -o /tmp/worst_mcp.gms --quiet

# Compile — Error 483 (Mapped variables have to appear in the model)
gams /tmp/worst_mcp.gms lo=0

# Check stationarity equations:
grep "stat_d1\|stat_d2" /tmp/worst_mcp.gms
# Output:
# stat_d1(i,t,j).. 0 =E= 0;
# stat_d2(i,t,j).. 0 =E= 0;
```

---

## GAMS Errors

- **Error 483**: Mapped variables have to appear in the model — `d1` and `d2`
  are paired with `stat_d1`/`stat_d2` in the MCP but don't appear in those
  equations (which are trivially `0 =E= 0`)

---

## Potential Fix Approaches

1. **Fix conditioned equation gradient propagation**: Ensure that when
   equations `c` and `p` reference `d1`/`d2`, the Jacobian terms are
   correctly included in `stat_d1`/`stat_d2`. The `errorf()` (normal CDF)
   derivative should produce `dnorm(d1)` terms.

2. **Handle `errorf` differentiation**: Verify that `errorf` (Gauss error
   function / normal CDF) is in the AD engine's function table with the
   correct derivative `errorf'(x) = (2/sqrt(pi)) * exp(-x^2)` or
   `normcdf'(x) = normpdf(x)`.

3. **Detect zero-stationarity and warn**: If all stationarity terms for a
   variable evaluate to zero, emit a warning rather than silently producing
   `0 =E= 0`.

---

## Sprint 24 Investigation (NOT FIXED)

**Root cause confirmed:** The `errorf` derivative IS implemented. The issue is
that `callval`, `putval`, `dd1`, `dd2` equations ALL have 0 instances from
condition evaluation — NOT because the conditions are unevaluable (no error),
but because the condition evaluator produces False for all instances.

The condition `pdata(i,t,j,"type") = call` involves a 4D parameter with dotted
keys: `pdata.values` stores keys like `('9000011.jun.1', 'type')` — the first
3 dimensions are dotted together. The condition evaluator constructs a lookup
key from the individual indices `('9000011', 'jun', '1', 'type')` which doesn't
match the dotted format.

With 0 instances for all conditioned equations, no Jacobian entries are generated
for `d1`/`d2`, producing zero stationarity.

**Fix requires:** Improve the condition evaluator's parameter value lookup to
handle dotted multi-dimensional keys. When `pdata(i,t,j,"type")` is evaluated
at indices `('9000011', 'jun', '1')`, the evaluator should try both:
- 4-tuple key: `('9000011', 'jun', '1', 'type')`
- Dotted key: `('9000011.jun.1', 'type')`

This is a ~2-4h fix in `src/ir/condition_eval.py`.

## Files Involved

- `src/ir/condition_eval.py` — Parameter value lookup (dotted key handling)
- `src/ad/index_mapping.py` — enumerate_equation_instances
- `src/ad/derivative_rules.py` — errorf derivative (WORKS correctly)
- `src/ad/constraint_jacobian.py` — Jacobian term generation
- `data/gamslib/raw/worst.gms` — Original model (152 lines)
