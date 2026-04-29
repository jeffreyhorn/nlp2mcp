# gtm: PATH terminates at iteration 0 with INFEASIBLE from default starting point (residual after #1192 + #1320 + #1322)

**GitHub Issue:** [#1326](https://github.com/jeffreyhorn/nlp2mcp/issues/1326)
**Status:** OPEN — Sprint 26 follow-up
**Severity:** Medium — gtm now compiles cleanly and reaches PATH (no listing-time aborts; no NA-derived gigantic coefficients), but PATH gives up at iteration 0 without attempting to iterate
**Date:** 2026-04-29
**Affected Models:** gtm
**Predecessors / closely-related:**
- [#1192](https://github.com/jeffreyhorn/nlp2mcp/issues/1192) (closed by PR #1321) — stat_s listing-time div-by-zero
- [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320) (closed by PR #1321) — bdef listing-time div-by-zero
- [#1322](https://github.com/jeffreyhorn/nlp2mcp/issues/1322) (closed by PR #1321) — NA-propagation through supb/supa
- [#1313](https://github.com/jeffreyhorn/nlp2mcp/issues/1313) — `--nlp-presolve` Error 141 cascade (currently blocks the warm-start path that would otherwise resolve this)

---

## Problem Summary

After PR #1321 closes #1192 / #1320 / #1322, gtm's emitted MCP file:

- Compiles cleanly under GAMS (no Error 141, no listing-time EXECERROR).
- Has no NA-derived gigantic coefficients (max ~86 vs pre-fix ~5e30).
- Successfully invokes the PATH solver.

**However, PATH terminates at iteration 0 (`ITERATION COUNT = 0`)** without attempting any major iterations and reports `MODEL STATUS 4 Infeasible`. The default starting point produces 60 INFES equations with max residual 1939.15, and PATH's crash preprocessor classifies the system as structurally infeasible without trying to solve it.

The original NLP (which uses the same data and equations) iterates from the same starting point and converges to `Locally Optimal` with `OBJECTIVE VALUE = -543.5651`. The structural difference is solver semantics: NLP solvers (CONOPT/MINOS) handle large initial-point infeasibilities via interior-point/penalty methods; PATH's default Newton-with-linesearch can't navigate from a starting point this far from feasibility.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: SOLVER STATUS 1 Normal Completion, MODEL STATUS 4 Infeasible, **ITERATION COUNT = 0**
- **Pipeline category**: `model_infeasible`
- **Predecessors fixed**: #1192, #1320, #1322 all closed by PR #1321

---

## Reproduction (verified 2026-04-29 with PR #1321 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/gtm.gms \
    -o /tmp/gtm_mcp.gms --skip-convexity-check
cd /tmp && gams gtm_mcp.gms lo=2

# Expected output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      4 Infeasible
#
#  RESOURCE USAGE, LIMIT          0.035 10000000000.000
#  ITERATION COUNT, LIMIT         0    2147483647     ← key signal: zero iterations
#  EVALUATION ERRORS              0             0
```

Inspect the equation listing to see the structural infeasibility:

```bash
grep -A20 "EQU stat_d" /tmp/gtm_mcp.lst | head -25
# stat_d(mexico) etc. show LEVEL ≠ 0 (their =E= constraints fail at the
# initial point because dema(j)*d(j)**demb(j)*demb(j)/d(j) evaluates to
# large nonzero values when d.l is at its initial value).
```

Compare to NLP (works):

```bash
cp /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/gtm.gms /tmp/gtm_orig.gms
cd /tmp && gams gtm_orig.gms lo=2

# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      2 Locally Optimal
# **** OBJECTIVE VALUE             -543.5651
# (NLP iterates to converge from the same data; PATH does not.)
```

---

## Root Cause Detail

### The starting point is far from feasibility

The MCP-emitted variable initialization sets:

```
x.l(i,j) = 1;        # then clamped to .up
s.l(i)   = 1;        # then clamped to .up; for zero-supc indices, s.l = 0
d.l(j)   = 0.2;      # then clamped to .up
```

For most demand regions (new-engl, ny-nj, midwest, etc.), the demand stationarity is

```
stat_d(j).. ((-1) * (dema(j) * d(j)**demb(j) * demb(j) / d(j))) + lam_db(j) - piL_d(j) =E= 0
```

where `demb(j) ≈ -1.5` to `-2.5` (negative — inverse demand elasticity). At
initial `d(j) = 0.2`, the term `dema * d^demb * demb / d` evaluates to large
negative values like `-86.7` (new-engl), `-1939.15` (west). With initial
multipliers `lam_db = 0` and `piL_d = 0`, the LHS evaluates to `-86.7 ≠ 0`,
giving INFES = 86.7 for that equation.

PATH sees these large residuals at iteration 0, applies its "crash" heuristic to determine if a basis can be found, and bails out when it can't.

### Why the NLP works but PATH doesn't

The NLP solver (CONOPT/MINOS) uses interior-point or active-set methods that can
navigate from large initial residuals via penalty/barrier formulations. PATH
uses Newton's method on the FOC system, which is sensitive to ill-conditioning
near the starting point. When the initial step direction points away from
feasibility (or the linearized system is singular), PATH's default crash
preprocessor declares the model infeasible without attempting refinement.

### Why warm-start would work

If we could supply PATH with a starting point near the NLP solution, the
Newton step would be small and convergent. The `--nlp-presolve` flag does
exactly this: it solves the NLP first and uses the optimum as PATH's starting
point. Unfortunately, **#1313 blocks the warm-start path** for gtm-class
models — the emitted presolve file hits Error 141 cascades on dual-transfer
lines.

---

## Fix Approaches

### Approach 1 — Fix #1313 first (RECOMMENDED, low risk)

Once #1313 is fixed, gtm's `--nlp-presolve` path will work and supply PATH with
a feasible warm start. Estimated effort for #1313: 4–8h (per its own issue
doc). After #1313 lands, gtm should reach `model_optimal_presolve` (the
PR pipeline runner already retries with presolve when the default solve fails).

**Pros:** unblocks gtm AND the broader bearing/qabel/abel non-convex warm-start
class. Reuses existing infrastructure (the pipeline runner already has
two-pass retry logic).

**Cons:** depends on a separate issue. If #1313 turns out to be more involved
than estimated, gtm stays blocked.

### Approach 2 — Smarter default variable initialization (RECOMMENDED for non-warm-start path)

Detect that gtm-style demand stationarity has near-singular gradients at
`d = 0.2` (because `d^demb` with negative `demb` blows up) and emit a
better default initialization. For `d` variables that appear in
`d^negative_exponent` patterns, initialize to a value where the gradient
magnitude is moderate.

For gtm specifically, initializing `d.l(j) = ddat(j, "ref-q")` (the
reference quantity) would put PATH near the NLP optimum from the start.

**Pros:** doesn't require fixing #1313; works on its own; generalizes to
other CES-utility / Cobb-Douglas demand models.

**Cons:** requires symbolic detection of the offending pattern in the
equation expressions; more invasive than Approach 1.

Estimated effort: 8–12h (detect + emit + regress).

### Approach 3 — PATH crash-method options

Pass solver options to PATH to disable its crash preprocessor and force it to
iterate from the default starting point. Specifically:

```
mcp_model.optfile = 1;
$echo "crash_method none" > path.opt
```

**Pros:** trivial change.

**Cons:** PATH may still fail to converge; just from a different code path.
Also adds GAMS file-emit overhead (the .opt file).

Estimated effort: 1–2h trial; uncertain success.

### Approach 4 — Document as a known limitation; close as wontfix

Recognize that gtm is fundamentally non-convex and PATH may simply not be
able to solve it from default initial values. Document this in the
known-limitations list (alongside `elec`, `bearing`, etc.) and accept the
`model_infeasible` outcome.

**Pros:** zero engineering effort; aligns with the existing
non-convex-warm-start-required class.

**Cons:** doesn't actually fix gtm; remains a permanent gap.

---

## Recommended Approach

**Approach 1 + Approach 2 in parallel:**

1. Fix #1313 first (independent issue; small, well-scoped) → unblocks gtm via
   the warm-start path. Probably resolves this issue too.
2. Independently, work on Approach 2 (better default initialization) for the
   broader class of non-warm-start models. This benefits other models in the
   div-by-zero/distance/CES-derivative family that may not have a warm-start
   path.

If only one path is taken, **Approach 1** is the cleaner Sprint 26 bet — it
unblocks gtm via well-understood infrastructure and helps adjacent models.

---

## Files Involved

- `src/emit/emit_gams.py` — variable-initialization section (around the
  `Variable Initialization` comment); would need extension for Approach 2.
- `src/emit/nlp_presolve_emitter.py` (or wherever the warm-start emission
  lives) — affected by Approach 1 / #1313 fix.
- `data/gamslib/raw/gtm.gms` — original source (unchanged).

---

## Acceptance Criterion

1. ✅ gtm reaches a PATH outcome better than `MODEL STATUS 4 Infeasible`. The
   minimum target is `model_optimal_presolve` (warm-start success); the
   stretch goal is `model_optimal` matching the NLP reference (`-543.5651`).
2. ✅ ITERATION COUNT > 0 (PATH actually attempts to solve, not just bail at
   crash).

---

## Related Issues

- **#1192** (closed by PR #1321) — stat_s listing-time div-by-zero (parent)
- **#1320** (closed by PR #1321) — bdef listing-time div-by-zero (parent)
- **#1322** (closed by PR #1321) — NA-propagation through supb/supa (parent)
- **#1313** — `--nlp-presolve` Error 141 cascade (THE blocker for the
  warm-start path that would resolve this). Fixing #1313 likely closes this
  issue as a side-effect.
- **#983** (elec), **#1245** (camcge), **#1234** (otpop): adjacent non-convex
  models with similar PATH-from-default-start failures.
- **bearing**: non-convex model that already uses `--nlp-presolve` warm-start
  (when not blocked by #1313) to reach `model_optimal_presolve`.
