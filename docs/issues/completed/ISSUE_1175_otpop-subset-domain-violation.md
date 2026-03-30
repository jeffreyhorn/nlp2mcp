# otpop: Subset-Superset Domain Violation in Stationarity Equations

**GitHub Issue:** [#1175](https://github.com/jeffreyhorn/nlp2mcp/issues/1175)
**Model:** otpop (GAMSlib SEQ=47, "A Dynamic model of OPEC Trade and Production")
**Error category:** `path_syntax_error` ($171 domain violation, $145/$148 parse errors)
**Severity:** High

## Description

The otpop model uses a time hierarchy: `tt` (superset, 1965-1990), `t(tt)` (subset, 1974-1990), `tp(tt)` (subset, 1975-1990). Parameters `db(t)` and `del(t)` are declared over subset `t`, but stationarity equations iterate over superset `tt`. This creates the catch-22:

- `db(tt)` → $171 domain violation (db only declared over t)
- `db(t)` → $149 uncontrolled set (t not controlled in stat_p(tt))

Additionally, `stat_d(tt)` contains `pd(1966-l)` which is a malformed index expression (literal year with arithmetic), and `stat_x(tt)` contains `p(1974+(card(t)-ord(t)))` (complex arithmetic on literal index).

## Root Cause

Same as chenery/shale issue #1164: `_rewrite_subset_to_superset` rewrites `t → tt` for all index references in stationarity equations, but this causes $171 for parameters declared over the subset. Reverting the rewrite causes $149 instead.

The proper fix requires restructuring the stationarity equation domain to match the subset (e.g., `stat_p(t)` instead of `stat_p(tt)`), with `.fx` for superset-only multiplier instances.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --skip-convexity-check
gams /tmp/otpop_mcp.gms lo=2
# $171, $145, $148, $149 errors
```

## Investigation (2026-03-30)

Attempted fix: Modified `_rewrite_subset_to_superset` to skip rewriting ParamRef indices when the parameter's declared domain uses the subset index. This correctly preserves `db(t)` but creates $149 (uncontrolled set) since `t` is not controlled in the equation domain `tt`.

The fundamental issue: GAMS requires every set index in an equation to be either:
1. Part of the equation's domain (controlled), or
2. Inside a sum/prod that iterates over it

Neither `db(tt)` ($171) nor `db(t)` ($149) satisfies both requirements without restructuring the equation.

## Fix Applied (2026-03-30)

**$171 FIXED** via parameter domain widening (PR #1176). The emitter now declares `db` and `del` over `tt` (superset) instead of `t` (subset). Remaining errors ($145/$148) are from malformed `pd(1966-l)` index expression — a separate issue in the stationarity builder's handling of concrete element offsets.

## Related Issues

- #1164: chenery/shale subset domain violation (same catch-22)
- Sprint 23 TRIAGE_PATH_SYNTAX_ERROR_GB.md §4.3
