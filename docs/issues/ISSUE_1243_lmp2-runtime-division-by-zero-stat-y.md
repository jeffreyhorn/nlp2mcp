# lmp2: Runtime Division by Zero in stat_y (1/y(p) at Initial Point)

**GitHub Issue:** [#1243](https://github.com/jeffreyhorn/nlp2mcp/issues/1243)
**Status:** OPEN
**Severity:** Medium — Model compiles but EXECERROR=1 aborts solve
**Date:** 2026-04-09
**Last Updated:** 2026-04-09
**Affected Models:** lmp2

---

## Problem Summary

After fixing compilation errors (#952), lmp2 compiles cleanly but GAMS aborts
the solve with EXECERROR=1 from division by zero in `stat_y(p)`. The
stationarity equation contains `1/y(p)` from the logarithmic derivative of
`prod(p, y(p))`, which is undefined when `y(p) = 0` at the initial point.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: EXECERROR=1 (division by zero during model generation)
- **Pipeline category**: path_syntax_error (was $66 error, now runtime error)
- **Previous fixes**: #952 (inner loop parameter extraction)

---

## Root Cause

The objective function is `prod(p, y(p))` — a product aggregation. The AD
engine's logarithmic derivative produces:

```
stat_y(p).. prod(p__, y(p__)) * sum(p__, 1 / y(p__)) + nu_Products(p) =E= 0;
```

The `1/y(p__)` term causes division by zero when `y(p) = 0` at the initial
point. Variable `y` is a free variable with no `.l` initialization and no
lower bound, so it defaults to 0.

This is the same class of issue as #1192 (gtm runtime division by zero) —
nonlinear KKT conditions that are undefined at the default starting point.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/`.

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_mcp.gms --quiet
gams /tmp/lmp2_mcp.gms lo=0

# Output:
# **** Exec Error at line 113: division by zero (0)
# **** Evaluation error(s) in equation "stat_y(p1)"
# **** Evaluation error(s) in equation "stat_y(p2)"
# **** SOLVE from line 160 ABORTED, EXECERROR = 1
```

---

## Potential Fix Approaches

1. **Initialize y.l to nonzero values**: Emit `y.l(p) = 1;` before the solve.
   The product derivative `prod * sum(1/y)` is well-defined when all `y > 0`.
   Requires detecting when prod-derivative terms create `1/variable` patterns.

2. **Guard derivative terms**: Emit `(1/y(p))$(y(p) <> 0)` instead of
   `1/y(p)`. This prevents the division by zero but may affect solver
   convergence (the guard changes the equation structure).

3. **Use alternative product derivative form**: Instead of the logarithmic
   derivative `prod * sum(1/y)`, use the algebraic form
   `sum(j, dy(j)/dx * prod(i!=j, y(i)))`. This avoids division but is
   computationally more expensive for large products.

---

## Files Involved

- `src/ad/derivative_rules.py` — `_diff_prod` (logarithmic derivative)
- `src/emit/emit_gams.py` — Variable initialization emission
- `data/gamslib/raw/lmp2.gms` — Original model (~100 lines)

---

## Related Issues

- #952 (FIXED) — Compilation error from inner loop parameter extraction
- #1192 — gtm: Same class of runtime division-by-zero issue
