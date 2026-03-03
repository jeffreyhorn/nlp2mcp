# elec: MCP Execution Error — Division by Zero (pairwise distances)

**GitHub Issue:** [#983](https://github.com/jeffreyhorn/nlp2mcp/issues/983)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** elec

---

## Problem Summary

The elec model (electrons on a sphere) parses and translates to MCP successfully, but GAMS aborts during equation generation with `division by zero (0)`. The error occurs in all three stationarity equations (`stat_x`, `stat_y`, `stat_z`) because the KKT gradient contains `1 / distance` terms where `distance = sqrt((x_i - x_j)^2 + (y_i - y_j)^2 + (z_i - z_j)^2)`, and the `.l` initialization places electrons at identical positions (causing zero distances). PATH never runs.

---

## Reproduction

```bash
python scripts/gamslib/run_full_test.py --model elec --verbose
# Output: [SOLVE] FAILURE: path_solve_terminated

# Direct GAMS execution:
gams data/gamslib/mcp/elec_mcp.gms lo=3
# Error at line 90: division by zero (0)
# Error at line 91: division by zero (0)
# Error at line 92: division by zero (0)
# Error at line 95: division by zero (0)
# Evaluation error(s) in equation "stat_x(i1)" through "stat_z(i25)"
```

---

## Root Cause Analysis

The stationarity equations contain gradient terms of the Coulomb potential:

```gams
stat_x(i).. sum(j, ((-1) * (1 / (2 * sqrt(sqr(x(i) - x(j)) + sqr(y(i) - y(j)) + sqr(z(i) - z(j)))) * 2 * (x(i) - x(j)))) / sqrt(sqr(x(i) - x(j)) + sqr(y(i) - y(j)) + sqr(z(i) - z(j))) ** 2) + ... =E= 0;
```

The `.l` initialization uses `cos(theta)*sin(phi)` etc. but these are evaluated with `theta` and `phi` parameters. When two electrons have the same angular coordinates, their pairwise distance is zero, causing division by zero. Also, the `sum(j, ...)` includes the `i == j` case where the self-distance is always zero.

The original NLP model likely uses `$(ord(i) < ord(j))` or similar filtering to exclude self-pairs. This dollar condition may not be propagating to the stationarity gradient.

---

## Suggested Fix

1. **Propagate the dollar condition** from the original objective/constraint to the stationarity gradient — the `sum(j$(...), ...)` filter that excludes `i == j` must appear in the KKT gradient as well.
2. **If dollar condition is already propagated**, check whether GAMS evaluates the full `sum(j, ...)` before applying the condition — may need to restructure as `sum(j$(ord(j) ne ord(i)), ...)`.
3. **Add `option domlim = 100;`** as a workaround to allow PATH to attempt solving despite evaluation errors.

---

## Files

- MCP file: `data/gamslib/mcp/elec_mcp.gms`
- Original GAMS model: `data/gamslib/gms/elec.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- AD differentiation: `src/ad/derivative_rules.py`
