# Sambal: KKT Stationarity Domain Conditioning + Wrong Index Reference

**GitHub Issue:** [#862](https://github.com/jeffreyhorn/nlp2mcp/issues/862)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver aborts (path_solve_terminated)
**Date:** 2026-02-24
**Affected Models:** sambal

---

## Problem Summary

The sambal model parses and translates to MCP, but the PATH solver aborts with 15 execution
errors. Two distinct KKT/stationarity builder bugs are present: (1) stationarity equations
are not conditioned on the original equation's domain filter, causing division by zero, and
(2) an incorrect index reference (`x(i,i)` instead of `x(i,j)`) in the stationarity
equation.

---

## Error Details

**Error A — Division by zero (line 85):**

Emitted stationarity equation:

```gams
stat_x(i,j).. xb(i,j) * xw(i,j) * 2 * (xb(i,j) - x(i,i)) * (-1) / xb(i,j) ** 2
              * xw(i,j) + ... =n= 0;
```

The term `/ xb(i,j) ** 2` divides by zero for elements where `xb(i,j) = 0`. The original
objective equation `devsqr` uses `$xw(i,j)` conditioning:

```gams
devsqr.. z =e= sum((i,j)$xw(i,j), sqr((xb(i,j) - x(i,j)) / xb(i,j)));
```

The `$xw(i,j)` condition ensures the term is only evaluated where `xw(i,j)` is nonzero
(and correspondingly `xb(i,j)` is nonzero). But the KKT stationarity builder does not
propagate this dollar condition to the generated stationarity equations.

**Error B — Wrong index reference:**

The stationarity equation references `x(i,i)` instead of `x(i,j)`:

```gams
stat_x(i,j).. ... (xb(i,j) - x(i,i)) ...
```

The derivative of `sqr((xb(i,j) - x(i,j)) / xb(i,j))` with respect to `x(i,j)` should
produce `x(i,j)`, not `x(i,i)`. This appears to be an AD differentiation bug where the
second index is incorrectly bound to the first.

**Error C — Empty stationarity equations:**

13 occurrences of `MCP pair stat_x.x has empty equation but associated variable is NOT
fixed` for elements where `xw(i,j) = 0`. The stationarity equation evaluates to zero/NA
for those elements, but the corresponding `x` variable is not fixed at its current value.

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.mcp.emitter import emit_mcp
ir = parse_file('data/gamslib/raw/sambal.gms')
mcp_code = emit_mcp(ir)
with open('/tmp/sambal_mcp.gms', 'w') as f:
    f.write(mcp_code)
print('Translate OK, check /tmp/sambal_mcp.gms')
"
# Then solve:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/sambal_mcp.gms
```

---

## Root Cause

### Bug 1: Dollar condition not propagated to stationarity

The KKT stationarity builder generates `stat_x(i,j)` for all `(i,j)` pairs, but the
original equation's `$xw(i,j)` condition should restrict the stationarity equation to only
those pairs where `xw(i,j)` is nonzero. Where `xw(i,j) = 0`, the variable `x(i,j)` should
be fixed (it has no effect on the objective).

### Bug 2: Index aliasing in AD differentiation

When differentiating `x(i,j)` with respect to `x(i,j)`, the AD module produces `x(i,i)`
instead of `x(i,j)`. This suggests an index-binding bug in the derivative computation where
the differentiation variable's indices are being reused from the first occurrence.

---

## Suggested Fix

**Bug 1:** Propagate dollar conditions from the original objective equation to the generated
stationarity equations. Where the condition is false, either skip the stationarity equation
entirely or fix the corresponding variable.

**Bug 2:** Fix the index binding in AD differentiation to correctly handle multi-index
variable references. The derivative of `f(x(i,j))` w.r.t. `x(i,j)` should preserve both
indices.

**Effort estimate:** ~4-5h (two separate bugs in stationarity builder and AD)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/mcp/stationarity.py` | Propagate dollar conditions to stationarity equations |
| `src/ad/derivative_rules.py` | Fix index binding in multi-index differentiation |
| `src/mcp/emitter.py` | Fix variable for empty stationarity equation pairs |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.4 documents the original parse blocker (`mapval()`)
- **Issue #764** (mexss): Similar accounting variable / stationarity conditioning issue
- **Issue #826** (decomp): Related empty stationarity equation issue
