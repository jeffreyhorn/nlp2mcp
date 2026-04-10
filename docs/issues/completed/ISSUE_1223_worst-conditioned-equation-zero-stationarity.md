# worst: Conditioned Equation Variables Produce Zero Stationarity

**GitHub Issue:** [#1223](https://github.com/jeffreyhorn/nlp2mcp/issues/1223)
**Status:** FIXED
**Severity:** Medium — was 0=0 stationarity (now resolved)
**Date:** 2026-04-07
**Last Updated:** 2026-04-10
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

## FIXED (Sprint 24)

**Root cause:** The `errorf` derivative IS implemented correctly. The issue was
that `callval`, `putval`, `dd1`, `dd2` equations ALL had 0 instances from
condition evaluation because the condition evaluator couldn't match dotted
parameter keys. `pdata.values` stores keys like `('9000011.jun.1', 'type')`
(dotted) but the evaluator constructed `('9000011', 'jun', '1', 'type')`
(individual elements).

Added `_try_dotted_key_lookup` in `condition_eval.py` that progressively
joins indices from the left with `.` to match the parser's Table format.
For `pdata(i,t,j,"type")` at `('9000011','jun','1')`:
- Direct lookup: `('9000011','jun','1','type')` — fails
- Dotted fallback: `('9000011.jun.1','type')` — matches!

**Result:** worst compiles and solves to MODEL STATUS 1 Optimal.
MCP obj=20,800,200 vs NLP obj=20,941,622 (~0.7% mismatch).
All conditioned equations now have correct instances:
- callval: 5, putval: 3, dd1: 8, dd2: 8, futval: 5

**Files modified:** `src/ir/condition_eval.py`, `tests/unit/ir/test_condition_eval_dotted.py`

## Files Involved

- `src/ir/condition_eval.py` — Parameter value lookup (dotted key handling)
- `src/ad/index_mapping.py` — enumerate_equation_instances
- `src/ad/derivative_rules.py` — errorf derivative (WORKS correctly)
- `src/ad/constraint_jacobian.py` — Jacobian term generation
- `data/gamslib/raw/worst.gms` — Original model (152 lines)
