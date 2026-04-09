# camcge: Runtime Division by Zero for Non-Traded Elements

**GitHub Issue:** [#1245](https://github.com/jeffreyhorn/nlp2mcp/issues/1245)
**Status:** OPEN
**Severity:** Medium — Model compiles but EXECERROR=4 aborts solve
**Date:** 2026-04-09
**Last Updated:** 2026-04-09
**Affected Models:** camcge

---

## Problem Summary

After resolving MCP pairing errors (#882), camcge compiles cleanly but GAMS
aborts the solve with EXECERROR=4 from division-by-zero and power-domain errors
in stationarity equations for non-traded elements (`services`, `publiques`).

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: EXECERROR=4 (division by zero during model generation)
- **Pipeline category**: path_solve_terminated
- **Previous fixes**: #882 (MCP pairing, CLOSED), #871 (subset conditioning), #879 (Jacobian domain)

---

## Error Details

```
**** Exec Error at line 529: division by zero (0)
**** Exec Error at line 529: A constant in a nonlinear expression in equation stat_pd evaluated to UNDF
**** Evaluation error(s) in equation "stat_pd(services)"
**** Evaluation error(s) in equation "stat_pd(publiques)"
**** Exec Error at line 543: rPower: FUNC DOMAIN: x**y, x=0,y<0
**** Evaluation error(s) in equation "stat_xxd(services)"
**** Evaluation error(s) in equation "stat_xxd(publiques)"
**** SOLVE from line 738 ABORTED, EXECERROR = 4
```

---

## Root Cause

The elements `services` and `publiques` are non-traded goods (in set `in`,
not in traded set `it`). Variables `e`, `m`, `pm`, `pwe` are fixed to 0 for
these elements via `.fx`. However, the stationarity equations `stat_pd` and
`stat_xxd` contain nonlinear terms (CES function derivatives with negative
exponents and division by price variables) that are evaluated at all `i`
instances, including non-traded ones where prices/quantities are 0.

At `pd('services') = 0` or `xxd('services') = 0`, expressions like
`pd(i) ** (sigma - 1)` (with `sigma < 1`) or `1/pd(i)` produce domain errors.

The original NLP model avoids this because GAMS doesn't evaluate equations
for fixed variables. But the MCP stationarity equations are generated for
all domain instances, including those where the underlying economic variables
are structurally zero.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/`.

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/camcge_mcp.gms --quiet
gams /tmp/camcge_mcp.gms lo=0

# Output:
# **** Exec Error at line 529: division by zero (0)
# **** SOLVE from line 738 ABORTED, EXECERROR = 4
```

---

## Potential Fix Approaches

1. **Condition stationarity on traded subset**: Add `$(it(i))` condition on
   `stat_pd(i)` and `stat_xxd(i)` to skip non-traded elements. Requires
   detecting that the variables' meaningful domain is the traded subset.

2. **Initialize non-traded prices to safe values**: Set `pd.l('services') = 1`
   etc. to avoid 0-denominators. The stationarity terms would still evaluate
   but to finite values.

3. **General EXECERROR tolerance**: Same class as #1192 (gtm) and #1243 (lmp2).
   A general solution for derivative singularities at initial points would
   fix all three models.

---

## Files Involved

- `src/kkt/stationarity.py` — Stationarity equation generation/conditioning
- `src/emit/emit_gams.py` — Variable initialization
- `data/gamslib/raw/camcge.gms` — Original model (~400 lines)

---

## Related Issues

- #882 (FIXED) — MCP pairing errors (12 unmatched equations)
- #871 (FIXED) — Subset conditioning
- #1192 — gtm: Same class of runtime division-by-zero
- #1243 — lmp2: Same class of runtime division-by-zero
