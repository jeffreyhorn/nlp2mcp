# maxmin: stat_mindist stationarity residual (Case b) — objective-variable cross-term missing

**GitHub:** #1447
**Status:** DEFERRED → Sprint 29
**Filed:** Sprint 28 Day 5 (2026-06-16)

## Summary

`maxmin` (circle-packing: `solve maxmin1a max mindist using dnlp;`) emits an MCP whose **`stat_mindist` stationarity row is wrong** (Case b). The model reaches MODEL STATUS 1 but at a **wrong objective** (mismatch).

## How it surfaced

**Surfaced, not caused, by #1388** (Sprint 28 Day 5, PR #1446). Before #1388, maxmin's MCP was `path_solve_terminated`. The #1388 offset-cross-term condition-guard fix (correct) changed maxmin's `stat` emit so PATH now converges to a (wrong) MODEL STATUS 1, exposing this separate, pre-existing `stat_mindist` bug.

## Evidence

- Cold solve (post-#1388): **MODEL STATUS 1, obj ≈ 0.104** — a mismatch.
- KKT-residual harness: **Case b**, max-residual row **`stat_mindist`**, residual ≈ **1.0** at the NLP KKT point.

## Root cause (hypothesis)

`mindist` is the **objective variable** (`max mindist`) and appears in `mindist1a(low(n,nn)).. mindist =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))))`. The objective-variable stationarity should be:

```
stat_mindist..  (-1) + sum(low, lam_mindist1a(low))  =E= 0     (sum of constraint multipliers = 1)
```

A residual of **exactly 1.0** = the bare objective gradient (`-1`) with **nothing balancing it** → the `sum(low, lam_mindist1a)` cross-term is **missing** (or mis-emitted) from `stat_mindist`. `low(n,nn)` is a 2-D subset and `mindist` is scalar, so the gap is plausibly a scalar-objvar ← 2-D-subset-domain-constraint Jacobian-transpose path.

## Scope

- **Sprint 29.** Not a Sprint-28 target. maxmin was already failing (`path_solve_terminated`) — not a regression of a previously-correct behavior, but it now mis-solves (a confident wrong answer).
- maxmin uses **DNLP** (`sqrt` non-smooth at 0; pairwise distances > 0 at a feasible packing) — verify the fix against the NLP/DNLP reference objective once `stat_mindist` is corrected.

## Acceptance

`stat_mindist` residual → 0 at the NLP KKT point (harness Case a), and maxmin's MCP objective matches the NLP/DNLP reference (`compare_objective_match`).

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 3/4, 2026-06-25):** harness verdict **Case b**, `max_residual_row = stat_mindist`, rel = **1.000**, dual-transfer consistent. **PROCEED** confirmed. maxmin already matches *warm* (`model_optimal_presolve`), so the fix is **cold-robustness** (removes the warm-start dependency), not headline +Match — see `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` (Class A, the lead).

### Hand-Derived KKT Shape

maxmin maximizes the scalar objective variable `mindist` subject to the pairwise lower-bounding constraints
`mindist1a(low(n,nn))..  mindist =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))))`.

Lagrangian (write the maximize as minimize `-mindist`, so the objective-variable gradient is `-1`; `=l=` constraint `mindist - rhs(low) ≤ 0` with multipliers `lam_mindist1a ≥ 0`):

```
L = -mindist + sum(low, lam_mindist1a(low) · (mindist - rhs(low)))
∂L/∂mindist = -1 + sum(low, lam_mindist1a(low)) · (+1) = 0
⇒  stat_mindist..  (-1) + sum(low, lam_mindist1a(low))  =E= 0
```

The objective-variable stationarity must carry the **`sum(low, lam_mindist1a)` constraint-multiplier cross-term**. A residual of exactly **1.0** = the bare objective gradient (`-1`) with that cross-term **absent** (scalar objvar ← 2-D subset-domain `=l=` constraint Jacobian-transpose path).

### Expected Emit Pattern

`maxmin_mcp.gms` `stat_mindist` should read (modulo sign convention):

```
stat_mindist..  -1 + sum(low(n,nn), lam_mindist1a(n,nn))  =E= 0 ;
```

i.e. the bare `-1` gradient **plus** the full `sum(low, lam_mindist1a(low))` term. (Hypothesis — the actual builder `file:line` is to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/maxmin.gms --json /tmp/phase0_maxmin.json
```

- **PROCEED (Case b):** `max_residual_row = stat_mindist`, relative residual ≈ 1.0 (the missing cross-term). ✅ confirmed Day-0.
- **REPLAN (Case c):** clean residual but cold PATH diverges → non-convexity, warm-start not emit fix → Sprint 30. (Not the case here.)
- Post-fix: residual → 0 (Case a) **and** `compare_objective_match` against the NLP/DNLP reference on the **cold** solve.

### PROCEED/REPLAN Signal

- **PROCEED** — Day-0 Case b on `stat_mindist`, rel ≈ 1.0 (✅ confirmed).
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — follow `stat_mindist` back to the objective-variable stationarity builder in `src/kkt/stationarity.py` (the scalar-objvar ← subset-domain `=l=` Jacobian-transpose path that drops the `sum(low, lam_mindist1a)` term). Trace command: regenerate `maxmin_mcp.gms`, grep `stat_mindist`, and step the builder that assembles the objective-variable row; cite the `file:line` that omits the cross-term. The exact integer residual (1.0) shared with himmel16 (`stat_area` 2.0) / like (`stat_p` 2.0) suggests a **shared Class-A fix** (one `stationarity.py` correction may land several — see COLD_CONVEX_COHORT_SURVEY §4).

## Provenance

- #1388 camshape offset-cross-term guard fix (Sprint 28 Day 5, PR #1446) — surfaced this. maxmin's `_mcp.gms` golden was regenerated there (the correct guard re-index); its `stat_mindist` cross-term gap is **this** issue.
