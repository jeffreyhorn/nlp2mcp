# otpop: MCP Pairing Error — stat_d Unmatched (d not referenced)

**GitHub Issue:** [#1232](https://github.com/jeffreyhorn/nlp2mcp/issues/1232)
**Status:** OPEN
**Severity:** Medium — Model compiles but EXECERROR=9 from 9 unmatched MCP pairs
**Date:** 2026-04-08
**Last Updated:** 2026-04-08
**Affected Models:** otpop

---

## Problem Summary

After fixing the compilation errors (#1178), otpop now compiles but fails at
solve time with EXECERROR=9: "MCP pair stat_d.d has unmatched equation" (9
instances). The stationarity equation `stat_d(tt)` does not reference the
variable `d(tt)`, so GAMS can't verify the MCP pairing.

The root cause is that variable `d` appears in equation `adef` via `d(tt-1)`
(a lagged reference), but the Jacobian contribution from `adef` to `stat_d`
is missing or incomplete — the stationarity equation only contains `nu_adef`
terms from other variables, not the `d`-derivative of `adef`.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (no compilation errors)
- **PATH solve**: EXECERROR=9 (9 unmatched MCP pairs for stat_d.d)
- **Pipeline category**: path_solve_terminated

---

## Root Cause

The original equation `adef(tt)$tp(tt)` references `d(tt-1)`:

```gams
adef(tt)$tp(tt).. as(tt) =e= as(tt-1) + con*d(tt-1)*(pd(tt-l)-ph);
```

The Jacobian `∂adef/∂d` should produce a lagged contribution `con*(pd(tt-l)-ph)`
at offset `-1`. This should appear in `stat_d(tt)` as a term involving
`lam_adef(tt+1)` (shifted by the lag). However, the emitted `stat_d` only has:

```gams
stat_d(tt).. nu_dem(tt) - nu_sup(tt) + ((((-1) * ((pd(tt-l) - ph) * con)) * nu_adef(tt+1))$(ord(tt) <= card(tt) - 1))$(tp(tt)) =E= 0;
```

This term references `pd(tt-l)` where `l` is a scalar parameter `/4/`. The
`pd(tt-l)` is a ParamRef with a scalar-valued offset, which may not be handled
correctly by the Jacobian builder (similar to #1224 mine's `li(k)` issue).

Additionally, `pd(tt-l)` uses a scalar constant `l` as a lead/lag offset,
which is the same pattern identified in the original #1178 investigation.

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --quiet
gams /tmp/otpop_mcp.gms lo=0

# Output:
# **** MCP pair stat_d.d has unmatched equation (9 times)
# **** SOLVE from line 293 ABORTED, EXECERROR = 9
```

---

## Potential Fix Approaches

1. **Fix scalar-constant lead/lag offsets**: Support `pd(tt-l)` where `l /4/`
   is a known scalar constant. Resolve `l` to its value `4` at IR build time,
   converting `pd(tt-l)` → `pd(tt-4)`. This would make the Jacobian builder
   handle it as a standard integer offset.

2. **Debug Jacobian for d(tt-1) in adef**: Trace why the `∂adef/∂d` contribution
   is not appearing in `stat_d`. The lagged reference `d(tt-1)` should produce
   a term with `nu_adef(tt+1)` weighted by `con*(pd(tt-l)-ph)`.

3. **Check stationarity term accumulation**: The `nu_adef(tt+1)` term IS present
   but may be from `∂adef/∂as` or `∂adef/∂pd`, not from `∂adef/∂d`. Verify
   which variable's derivative produces the existing term.

---

## Files Involved

- `src/ad/constraint_jacobian.py` — Jacobian computation for lagged references
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `src/ir/parser.py` — Scalar constant resolution in IndexOffset
- `data/gamslib/raw/otpop.gms` — Original model (136 lines)

---

## Related Issues

- #1178 (FIXED) — Compilation errors from malformed index expressions
- #1224 — mine: ParamRef index offsets unsupported (similar pattern)
