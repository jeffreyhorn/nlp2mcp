# twocge: Empty Trade Equations When r=rr (8 MCP Pairing Errors)

**GitHub Issue:** [#1251](https://github.com/jeffreyhorn/nlp2mcp/issues/1251)
**Status:** OPEN
**Severity:** Medium — Model compiles but EXECERROR=8 aborts solve
**Date:** 2026-04-10
**Last Updated:** 2026-04-10
**Affected Models:** twocge

---

## Problem Summary

After fixing the `ord(JPN)` compilation error (#906), twocge compiles but
GAMS aborts the solve with EXECERROR=8 from empty equation MCP pairing errors.
The trade equations `eqpw(i,r,rr)` and `eqw(i,r,rr)` have condition
`$(ord(r) <> ord(rr))` which evaluates to false when `r = rr` (same country),
producing 0=0 equations for those instances. Their multipliers are not fixed.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: EXECERROR=8 (empty equation, variable NOT fixed)
- **Pipeline category**: path_solve_terminated
- **Previous fixes**: #906 (ord(JPN) compilation, USA SAM data, post-solve ordering)

---

## Error Details

```
**** MCP pair eqpw.nu_eqpw has empty equation but associated variable is NOT fixed
     nu_eqpw(BRD,JPN,JPN)
     nu_eqpw(BRD,USA,USA)
     nu_eqpw(MLK,JPN,JPN)
     nu_eqpw(MLK,USA,USA)
**** MCP pair eqw.nu_eqw has empty equation but associated variable is NOT fixed
     nu_eqw(BRD,JPN,JPN)
     nu_eqw(BRD,USA,USA)
     nu_eqw(MLK,JPN,JPN)
     nu_eqw(MLK,USA,USA)
**** SOLVE from line 672 ABORTED, EXECERROR = 8
```

---

## Root Cause

The trade equations use `$(ord(r) <> ord(rr))` to exclude same-country pairs:

```gams
eqpw(i,r,rr).. (pWe(i,r) - pWm(i,rr))$(ord(r) <> ord(rr)) =e= 0;
eqw(i,r,rr)..  (E(i,r) - M(i,rr))$(ord(r) <> ord(rr)) =e= 0;
```

For instances where `r = rr` (e.g., `(BRD, JPN, JPN)`), the condition is
false and the equation body is 0. GAMS requires the paired multiplier to be
fixed for empty equation instances.

The existing empty equation detector (`src/kkt/empty_equation_detector.py`)
handles sparse coefficient data but not `ord()` comparison conditions.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/`
(run `python scripts/gamslib/download_models.py`).

```bash
.venv/bin/python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms --quiet
gams /tmp/twocge_mcp.gms lo=0

# Output:
# **** MCP pair eqpw.nu_eqpw has empty equation but associated variable is NOT fixed
# **** SOLVE from line 672 ABORTED, EXECERROR = 8
```

---

## Potential Fix Approaches

1. **Emit `ord()` condition on multiplier `.fx`**: Detect equations with
   `$(ord(r) <> ord(rr))` conditions and emit:
   ```gams
   nu_eqpw.fx(i,r,rr)$(ord(r) = ord(rr)) = 0;
   nu_eqw.fx(i,r,rr)$(ord(r) = ord(rr)) = 0;
   ```
   This is the most direct fix — negate the equation condition and apply to
   the multiplier. Requires the emitter to detect `ord()` conditions in the
   original equation and emit the negated form.

2. **Extend empty equation detector**: Add support for `ord()` comparison
   conditions in `detect_empty_equation_instances`. When a condition like
   `$(ord(r) <> ord(rr))` is detected, compute which instances make it false
   (same-set elements at the same ordinal position) and mark those as empty.

3. **Emit equation condition on multiplier**: The equation `eqpw` has
   `condition = None` (the `$` is on the body, not the head). If the
   condition were on the equation head, the existing multiplier `.fx`
   logic would handle it. Could lift the body condition to the head.

---

## Files Involved

- `src/emit/emit_gams.py` — Multiplier `.fx` emission
- `src/kkt/stationarity.py` — Equation condition detection
- `src/kkt/empty_equation_detector.py` — Empty equation detection
- `data/gamslib/raw/twocge.gms` — Original model (~340 lines)

---

## Related Issues

- #906 (PARTIALLY FIXED) — ord(JPN), USA SAM, post-solve ordering
- #1133 (FIXED) — fawley empty equation detection (similar pattern)
