# camshape: MCP solves to Locally Infeasible (post-Pattern-E reclassification)

**GitHub Issue:** [#1388](https://github.com/jeffreyhorn/nlp2mcp/issues/1388)
**Status:** OPEN (filed Sprint 26 Day 6, 2026-05-12)
**Severity:** Medium — translate + compile clean but the PATH solve produces `Locally Infeasible (model_status = 5)` with obj=6.2 vs NLP obj=4.2841.
**Date:** 2026-05-12
**Last Updated:** 2026-05-27 (Sprint 27 Prep Task 2 — Phase 0 acceptance-gate section authored per PR20 codification)
**Affected Models:** camshape
**Target Sprint:** Sprint 27 (3–6h investigation + fix)
**Cross-references:**
- Predecessor: #1147 (now CLOSED 2026-05-12 via Sprint 26 Day 6 — see [docs/issues/completed/ISSUE_1147_camshape-alias-compilation-error.md](completed/ISSUE_1147_camshape-alias-compilation-error.md)).
- Sibling (closed Sprint 25): #1160 ("camshape: MCP pairing error — stat_rdiff.rdiff unmatched equation (subset domain mismatch)") — fixed; current bug is distinct.
- Reclassification source: [docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md](../planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md) §"Issue #1147".

## Problem Summary

camshape MCP translates cleanly and compiles cleanly under GAMS `action=c`, but the solve produces `Locally Infeasible (model_status = 5)` with `objective_value = 6.2` vs NLP `objective_value = 4.2841`. The `solution_comparison.comparison_status` is `not_tested` because the solve failed.

This is a **NEW bug** — distinct from the original alias-AD compilation error tracked under now-closed #1147 (the `$141` symbol-not-defined errors), and distinct from the `stat_rdiff.rdiff` pairing error tracked under the also-closed #1160.

Sprint 26 Prep Task 5 re-verification (2026-05-07) on current main:

```
$ .venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
    -o /tmp/sprint26-pattern-e/camshape_mcp.gms --skip-convexity-check --quiet
✓ Generated MCP: /tmp/sprint26-pattern-e/camshape_mcp.gms
translate exit=0, emit lines: 504

$ gams /tmp/sprint26-pattern-e/camshape_mcp.gms action=c lo=2 \
    o=/tmp/sprint26-pattern-e/camshape_compile.lst
(no compile errors — clean)
```

`data/gamslib/gamslib_status.json` records: `nlp2mcp_translate.status = success`; `mcp_solve.status = failure`, `model_status = 5 (Locally Infeasible)`, `objective_value = 6.2` (vs NLP=4.2841), `outcome_category = model_infeasible`.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
  -o /tmp/camshape_mcp.gms --skip-convexity-check --quiet
gams /tmp/camshape_mcp.gms lo=2
# Observed (the bug): MODEL STATUS 5 (Locally Infeasible), obj=6.2
# Expected (no bug):  MODEL STATUS 1 (Optimal), obj ≈ 4.2841 (matching the NLP)
```

## Investigation pointers

1. Compare emitted `stat_*` equations against hand-derived KKT for the camshape model — look for missing or mis-scoped constraints.
2. Check that the previous fix for `nu_eqrdiff.fx` (per #1160 closure) didn't introduce a different pairing imbalance.
3. Run PATH with verbose iteration logging to identify which constraint goes infeasible first.
4. Apply the Sprint 25 Day 5 methodology (trace + emitted-artifact + formal derivative byte comparison) on `stat_rdiff` specifically — that was the focal point of the previous #1147 / #1160 fixes.

## Files involved (preliminary)

- `src/kkt/stationarity.py` — likely
- `src/emit/emit_gams.py` — bound-fixup emission
- `data/gamslib/raw/camshape.gms` — source
- `data/gamslib/mcp/camshape_mcp.gms` — current emit (Locally Infeasible)

## Effort estimate

3–6h investigation + fix. May benefit from coordinated work with Priority 5 (AD residuals) since the symptom shape is unfamiliar.

## Related

- **#1147** — closed 2026-05-12 via Sprint 26 Day 6 PR; the original alias-AD compilation error, partially fixed and reclassified out via Sprint 26 Prep Task 5 (this issue is the successor).
- **#1160** — CLOSED in Sprint 25; fixed the `stat_rdiff.rdiff` unmatched-equation pairing error. The current `Locally Infeasible` solve is a DISTINCT bug not subsumed by #1160's resolved scope.
- Sprint 26 Prep Task 5: `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` §"Issue #1147" — full reclassification rationale.

---

## Phase 0: Acceptance Gate

**Authored:** 2026-05-27 (Sprint 27 Prep Task 2 per PR20 codification)
**Target equation(s):** `stat_r(i)` + `stat_rdiff(i)` at `data/gamslib/mcp/camshape_mcp.gms:428-429`; with the cross-coupling between `lam_convexity(i)`, `lam_convex_edge1(i)`, `lam_convex_edge3(i)`, `lam_convex_edge4(i)`, and `nu_eqrdiff(i)` being the suspected infeasibility driver.
**Bug class:** Open at Phase 0 time — may be (a) emit bug (missing or wrong-signed cross-coupling between the convexity-edge multipliers in stationarity), (b) bound-fixup emission bug (a `.fx` on a multiplier that should be free, locking the system into an infeasible region), or (c) fundamental model property (camshape's KKT genuinely has multiple stationary points and PATH converges to a non-NLP one).

The Phase 0 acceptance gate must distinguish between (a/b) (fixable in Sprint 27 via Priority 7 budget) and (c) (Sprint 28 carryforward filing).

### Hand-Derived KKT Shape

Source NLP (from `data/gamslib/raw/camshape.gms`):

```
obj.. area =e= ((pi*R_v)/n) * sum(i, r(i));

convexity(middle(i))..   -r(i-1)*r(i) - r(i)*r(i+1) + 2*r(i-1)*r(i+1)*cos(d_theta) =l= 0;
convex_edge1(first(i)).. -R_min*r(i)  - r(i)*r(i+1) + 2*R_min*r(i+1)*cos(d_theta)  =l= 0;
convex_edge3(last(i))..  -r(i-1)*r(i) - r(i)*R_max  + 2*r(i-1)*R_max*cos(d_theta)  =l= 0;
convex_edge4(last(i))..  -2*R_max*r(i) + 2*sqr(r(i))*cos(d_theta) =l= 0;
eqrdiff(j(i+1))..        rdiff(i) =e= r(i+1) - r(i);
```

Variables: `r(i)` (radius at each angle), `rdiff(i)` (consecutive differences); multipliers: `lam_convexity(middle)`, `lam_convex_edge1(first)`, `lam_convex_edge3(last)`, `lam_convex_edge4(last)`, `nu_eqrdiff(j)`.

Hand-derive `∂L/∂r(i) = 0` for an interior `i` (i.e., `middle(i)`):

- `∂obj/∂r(i) = (pi * R_v) / n` (objective is linear in `r(i)` via `sum(i, r(i))`)
- `∂convexity(i)/∂r(i) = -r(i-1) - r(i+1)` (the `r(i)` factor appears in two terms)
- `∂convexity(i-1)/∂r(i)`: convexity(i-1) is `-r(i-2)*r(i-1) - r(i-1)*r(i) + 2*r(i-2)*r(i)*cos(d_theta)`; partial w.r.t. `r(i)` = `-r(i-1) + 2*r(i-2)*cos(d_theta)`
- `∂convexity(i+1)/∂r(i)`: convexity(i+1) is `-r(i)*r(i+1) - r(i+1)*r(i+2) + 2*r(i)*r(i+2)*cos(d_theta)`; partial w.r.t. `r(i)` = `-r(i+1) + 2*r(i+2)*cos(d_theta)`
- `∂eqrdiff(i-1)/∂r(i) = +1` (`rdiff(i-1) = r(i) - r(i-1)`; partial w.r.t. r(i) = +1)
- `∂eqrdiff(i)/∂r(i) = -1` (`rdiff(i) = r(i+1) - r(i)`)

Combining for interior `i`:

```
stat_r(i)..   (pi * R_v / n)
            + (-r(i-1) - r(i+1)) * lam_convexity(i)$(middle(i))
            + (-r(i-1) + 2*r(i-2)*cos(d_theta)) * lam_convexity(i-1)$(middle(i-1) and ord(i)>2)
            + (-r(i+1) + 2*r(i+2)*cos(d_theta)) * lam_convexity(i+1)$(middle(i+1) and ord(i)<card(i)-1)
            + nu_eqrdiff(i-1)$(j(i) and ord(i)>1)
            - nu_eqrdiff(i)$(j(i+1))
            - piL_r(i) + piU_r(i)
            = 0   (where r is free; the bound-fixup multiplier emit handles fixed r instances)
```

For edge cases (`first(i)` / `last(i)`), additional terms from `convex_edge*` apply with their own multiplier coefficients.

### Expected Emit Pattern

The current emit at line 428 (`stat_r(i)..`) **DOES contain** the `(pi * R_v / n)` objective gradient term — it appears as `(-1) * (pi * R_v / 100)` (the source uses `n=100`, so this is the correctly-substituted constant; the `(-1)` prefix is the Lagrangian-sign flip, consistent with stationarity convention). The objective gradient term is therefore present and correctly signed; the issue (if any) is elsewhere in `stat_r(i)`. The cross-coupling terms for `lam_convexity(i-1)` and `lam_convexity(i+1)` ARE also present in the emit but have unusual `$(...)$(...)` nested-conditional structures that may guard incorrectly — that is the more likely emit-bug surface to investigate.

**Key Phase 0 verifications:**

1. Check that the constant `(pi * R_v / n)` (or `(pi * R_v / 100)`) appears with the correct sign in `stat_r(i)`. Current emit shows `((-1) * (pi * R_v / 100))` — Lagrangian-sign-flipped, consistent.
2. Check that `lam_convexity(i-1)` cross-term is present for `middle(i)` AND `ord(i) > 1` (not just `middle(i)`).
3. Check that `lam_convexity(i+1)` cross-term is present for `middle(i)` AND `ord(i) <= card(i) - 1`.
4. Check that `nu_eqrdiff(i-1)` (with `+1` coefficient) and `nu_eqrdiff(i)` (with `-1` coefficient) are both present where appropriate.
5. Check the bound-fixup `$(r.up(i) - r.lo(i) > 1e-10)` outer wrap — if it incorrectly fixes `stat_r(i)` to zero on first/last instances where `r` is genuinely free, that creates infeasibility.

If hand-derivation matches the emit byte-for-byte (after equivalence simplifications), then this is case (c) — fundamental model property — and should be Sprint 28 carryforward. If the emit is missing terms or has wrong signs, this is case (a) — fix-and-ship in Sprint 27.

### Verification Methodology

```bash
# Step 1: regenerate the emit
.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
  -o /tmp/camshape_mcp.gms --skip-convexity-check --quiet

# Step 2: extract stat_r and stat_rdiff for byte-comparison
grep -nE '^stat_r\(i\)\.\.|^stat_rdiff\(i\)\.\.' /tmp/camshape_mcp.gms > /tmp/camshape_stat_after.txt
cat /tmp/camshape_stat_after.txt

# Step 3: hand-derive the KKT for one INSTANCE — e.g., stat_r('5') (a middle
# index away from edges) — and byte-compare against the emit. Use the source
# convexity / convex_edge / eqrdiff equations with i=5, i-1=4, i+1=6 substituted.

# Step 4: NLP-warm-started PATH solve test — load the NLP solution as initial
# point and re-run PATH; if PATH converges to MODEL STATUS 1 with obj ≈ 4.28,
# the emit is correct and infeasibility was a starting-point issue (case c
# variant: starting-point sensitive). If still Locally Infeasible from the
# NLP-warm start, the emit has a structural bug.
# (See ISSUE_1378 launch PATH-numerics for the warm-start methodology.)

# Step 5: full PATH solve
gams /tmp/camshape_mcp.gms lo=2 | grep -E 'MODEL STATUS|SOLVER STATUS|OBJECTIVE'
# Expected pre-fix: MODEL STATUS 5 (Locally Infeasible), obj=6.2
# Expected post-fix: MODEL STATUS 1 (Optimal), obj≈4.2841
```

### PROCEED/REPLAN Signal

**PROCEED** with Sprint 27 Priority 7 implementation if ALL of:

- (a) Hand-derived KKT for `stat_r('5')` (middle instance) byte-compares to emit modulo algebraic simplifications → if differences are present, identify the missing/wrong term and fix in src/
- (b) PATH solve reaches MODEL STATUS 1 (Optimal) with `obj ≈ 4.2841` (NLP value) post-fix
- (c) Tier 0/1 canary byte-stability preserved

**REPLAN — Sprint 28 Carryforward** if:

- (a) Hand-derived KKT byte-matches the emit (no emit bug) AND
- (b) NLP-warm-started PATH solve STILL fails to converge to Optimal → this is case (c), fundamental model property; PATH genuinely converges to a non-NLP stationary point because camshape's KKT has multiple stationary points. File for Sprint 28 with formal Phase 0 carryforward documentation; do NOT spend Sprint 27 Priority 7 budget on a non-fixable bug.

**REPLAN — Scope expansion** if:

- (c) The bug requires AD-pipeline changes (e.g., wrong handling of `r(i)`'s appearance in multiple convexity equations at offset indices i-1, i+1) → bundle with Priority 3 (AD architectural redesigns) rather than treat as standalone Priority 7 work

