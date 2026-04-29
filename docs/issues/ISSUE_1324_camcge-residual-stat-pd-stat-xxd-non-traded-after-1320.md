# camcge: stat_pd / stat_xxd div-by-zero on non-traded subset, residual after #1320 divisor-guard

**GitHub Issue:** [#1324](https://github.com/jeffreyhorn/nlp2mcp/issues/1324)
**Status:** OPEN — Sprint 26 follow-up
**Severity:** High — `path_solve_terminated` (EXECERROR=4) prevents PATH from solving
**Date:** 2026-04-29
**Affected Models:** camcge
**Predecessors / closely-related:**
- [#882](https://github.com/jeffreyhorn/nlp2mcp/issues/882) — Subset bound complementarity (CLOSED, fixed in #1264)
- [#1245](https://github.com/jeffreyhorn/nlp2mcp/issues/1245) — Runtime div-by-zero for non-traded elements
- [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320) (closed by PR #1321) — bdef divisor guard. **camcge was probed as an "adjacent model" but Approach 1 from #1320 did NOT unblock it because camcge's blocker is in KKT-built `stat_*` equations (which #1320 explicitly bypasses), not in original parsed equations.**

---

## Problem Summary

camcge has variables `pd(i)` and `xxd(i)` defined over a "traded"
subset `it(i)` of the full sectoral set `i`. For non-traded
elements (`services`, `publiques`), `pd(i)` and `xxd(i)` are
structurally zero. The KKT-built stationarity equations `stat_pd(i)`
and `stat_xxd(i)` contain CES function derivatives with negative
exponents and divisions by `pd(i)` / `xxd(i)`, which evaluate to
`UNDF` for the non-traded indices.

PR #1321's #1320 fix (Approach 1) injects `$(p(i) <> 0)` guards on
**parsed-source equation Sum bodies** but EXPLICITLY BYPASSES KKT-
built `stat_*` equations to avoid double-conditioning with PR
#1321's #1192 bounds-aware guard. camcge's blocker is on the KKT-
built side (stationarity for variables defined over a subset), so
neither #1192 nor #1320 helps it directly.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: EXECERROR=4 (div-by-zero in stat_pd; rPower
  FUNC DOMAIN error in stat_xxd from `x**y` with `x=0, y<0`)
- **Pipeline category**: `path_solve_terminated`
- **Predecessors fixed**: #882 (MCP pairing), #871 (subset cond)

---

## Reproduction (verified 2026-04-29 with PR #1321 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms \
    -o /tmp/camcge_mcp.gms --skip-convexity-check
cd /tmp && gams camcge_mcp.gms lo=2

# Expected output:
# **** Exec Error at line 529: division by zero (0)
# **** Evaluation error(s) in equation "stat_pd(services)"
# **** Evaluation error(s) in equation "stat_pd(publiques)"
# **** Exec Error at line 543: rPower: FUNC DOMAIN: x**y, x=0,y<0
# **** Evaluation error(s) in equation "stat_xxd(services)"
# **** Evaluation error(s) in equation "stat_xxd(publiques)"
# **** SOLVE from line 729 ABORTED, EXECERROR = 4
```

---

## Root Cause Detail

The traded subset is `it(i)` ⊂ `i`. Variables `pd`, `xxd`, `e`,
`m`, `pwe`, `pm` are assigned to vary only over `it`; for non-`it`
indices they are `.fx`'d to 0 (per #882's prior fix). The KKT
stationarity, however, is built over the full domain `i` because
the variables themselves are declared over `i`.

For `services` (∉ `it`), `pd(services).l = 0`, `xxd(services).l = 0`
after initialization. The CES function derivative for `stat_xxd(i)`
contains `xxd(i) ** (sigma - 1)` with `sigma < 1`, so for `xxd = 0`
this is `0 ** (-0.something) = 1/(0 ** 0.something) = 1/0 = UNDF`.
Similarly `stat_pd(i)` has `1/pd(i)` factors.

The original NLP avoids this because GAMS NLP listing skips equations
for fixed variables (since `pd(services).fx = 0`). The MCP can't take
the same shortcut because PATH requires all stationarity rows to be
generated regardless of fix state.

PR #1321's #1192 fix (bounds-aware guard) DOES generate
`pd.fx(i)$(...) = lo` lines and could in principle catch this,
BUT the camcge bounds are NOT parameter-dependent in the sense
my fix detects — they're `.fx`'d via direct `pd.fx(i)$(not
it(i)) = 0;` lines from upstream emission. My `_has_param_dependent_bounds`
check returns `False` for these because the fx came from a static
assignment, not an `up_expr_map`/`lo_expr_map` containing a `ParamRef`.

---

## Fix Approaches

### Approach 1 — Detect "fixed via .fx" as a guard trigger (recommended)

Extend `_has_param_dependent_bounds` (or a sibling helper) to ALSO
fire when the variable's `fx_map` is non-empty AND populated from
parameter-dependent expressions. The bounds-collapse guard then
fires on `(v.up - v.lo > eps)` which would correctly detect that
`pd(services)` is fixed (up == lo == fx == 0) and skip its
stationarity row.

This unifies the #1192 mechanism with the camcge case — making the
guard fire on ANY effectively-fixed variable, not just those with
parameter-dependent bound EXPRESSIONS.

**Estimated effort:** 3–5 hours (extend detection, regression).

### Approach 2 — Subset-condition stationarity equation

Add `$(it(i))` condition on `stat_pd(i)` and `stat_xxd(i)` so
only traded instances generate stationarity rows. Requires the KKT
builder to detect that the variable's effective domain is a subset
(via the `fx_map` for non-subset elements), and emit the
stationarity equation conditioned on the subset.

**Estimated effort:** 6–8 hours (KKT subset detection + regression).

### Approach 3 — Initialize pd, xxd, etc. to small non-zero values
for non-traded indices

`pd.l('services') = 1e-3`. Avoids the listing-time div-by-zero but
does NOT make the math correct. Bad workaround.

**Estimated effort:** 1–2 hours but **not recommended** (semantic
incorrectness).

---

## Recommended Approach

**Approach 1** (extend bounds-collapse detection to include fix_map)
is the cleanest because it reuses the PR #1321 #1192 infrastructure
and generalizes to any effectively-fixed variable.

Approach 2 is a fallback if Approach 1 reveals corner cases (e.g.,
fx_map populated dynamically inside a loop body).

---

## Files Involved

- `src/kkt/stationarity.py` — `_has_param_dependent_bounds`
  helper; needs extension to recognize fix_map.
- `src/emit/emit_gams.py` — fix-inactive emission section 1a.

---

## Acceptance Criterion

1. camcge no longer aborts at GAMS model-listing time with
   EXECERROR=4 on stat_pd / stat_xxd.
2. camcge progresses to PATH solve attempt.
3. Stretch: full match against NLP reference.

---

## Related Issues

- **#882** (CLOSED) — MCP pairing for subset bounds
- **#871** (CLOSED) — Subset stationarity conditioning
- **#1245** — Earlier framing of this same issue (pre-#1320 context)
- **#1192** (CLOSED by PR #1321) — Bounds-aware stationarity guard for
  parameter-dependent bounds (this PR's #1192 fix is the foundation
  Approach 1 extends).
- **#1320** (CLOSED by PR #1321) — Why PR #1321's #1320 didn't help
  camcge: it targets parsed-source equations only.
