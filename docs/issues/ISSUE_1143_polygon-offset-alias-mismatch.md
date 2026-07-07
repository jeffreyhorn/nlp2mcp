# polygon: Offset-Alias Gradient Complete Failure (100% Mismatch)

**GitHub Issue:** [#1143](https://github.com/jeffreyhorn/nlp2mcp/issues/1143)
**Status:** **Sprint 30 Day 7 (2026-07-07): FIX CONFIRMED via control experiment — 4 coupled missing cross-terms, ready to implement.** A hand-patched emit with all four missing terms warm-matches (**0.780 ≈ NLP 0.7797**, up from the 0.516 mismatch); each subset alone fails (the distance-only patch → 0.000), confirming the "land both together" coupling. See the Day-7 block below. _(was: Sprint 29 Day 5 REVERTED → re-deferred to Sprint 30)_
**Severity:** Medium — **solve mismatch / KKT inconsistency** (objective-gradient cross-term + the `distance(i,j)` constraint-Jacobian symmetry must both be fixed for polygon to match; matches warm today). _(The old "MCP compilation failure / compile errors" framing was stale — confirmed at Day 0: polygon translates + compiles cleanly and matches warm; the live issue is the cold-solve KKT inconsistency.)_
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** polygon

---

## Sprint 30 Day 7 — FIX CONFIRMED (control experiment; the exact 4 terms)

Day-0 harness re-confirmed CASE_B (`stat_theta(i12)` rel 0.492, dual-transfer CONSISTENT). Baseline: cold MCP 0.514 / warm (presolve) MCP **0.516** — both **mismatch** the NLP ref **0.7797** (polygon does NOT match warm today; the earlier "matches warm" framing was wrong). A control experiment hand-patching the emitted `stat_r`/`stat_theta` with the four missing cross-terms **warm-matches: 0.780 ≈ 0.7797** (cold stays MS-5 — non-convex area-max — so this is a **presolve/warm match**, converting polygon **mismatch → match, +1 Match**). The distance-only subset alone → **0.000** (broken), confirming the "land all together" coupling.

**The two bug classes (both drop the second contribution when a variable appears at two offset/alias positions):**

1. **Objective successor cross-term** (obj `polygon_area = 0.5·sum(i, r(i+1)·r(i)·sin(θ(i+1)−θ(i)))`). `r(i)` and `θ(i)` each appear as both the base `(i)` and the successor `(i+1)` in the summand, so `∂obj/∂r(i)` gets contributions from **both** the `i`-th and the `(i−1)`-th summand — the emit keeps only the `i`-th. Missing terms:
   - `stat_r(i)`: `+ ((-1) * (0.5 * sin(theta(i) - theta(i-1)) * r(i-1) * 1$(j(i-1))))`
   - `stat_theta(i)`: `+ ((-1) * (0.5 * r(i) * r(i-1) * cos(theta(i) - theta(i-1)) * 1$(j(i-1))))`
   - Fix surface: the objective-gradient path (`src/ad/gradient.py` / `_diff_varref` / `_partial_collapse_sum` non-circular-offset branch — the reverted representative-selection).

2. **Distance constraint-Jacobian second-index symmetry** (`distance(i,j)$(ord(j)>ord(i))..  sqr(r(i))+sqr(r(j)) − 2·r(i)·r(j)·cos(θ(j)−θ(i)) =l= 1`). `r`/`θ` appear at **both** indices; the emit only emits the `∂/∂·(i)` cross-term (`sum(j>i, …·lam_distance(i,j))`), dropping the `∂/∂·(j)` term (`sum(i'<i, …·lam_distance(i',i))`). Missing terms (with `j` = the alias, `ord(j)<ord(i)`):
   - `stat_r(i)`: `+ sum(j, ((2 * r(i) - cos(theta(j) - theta(i)) * r(j) * 2) * lam_distance(j,i))$(ord(j) < ord(i)))`
   - `stat_theta(i)`: `+ sum(j, ((2 * r(i) * r(j) * sin(theta(i) - theta(j))) * lam_distance(j,i))$(ord(j) < ord(i)))`
   - Fix surface: `src/ad/constraint_jacobian.py` (the dropped second-index cross-term for a 2-index constraint whose variable appears at both indices).

**Disposition: PROCEED** — both AD paths, tightly gated to the offset/alias shape, landed together (neither alone matches). REPLAN to Sprint 31 (#1111/#1112 general alias differentiation) only if a tight shape-gate proves infeasible.

---

## Problem Summary

The polygon model (Largest Small Polygon) uses offset-based aliasing with
`sum(j(i+1), ...)` patterns where `j` is an alias of `i` and the sum
iterates over the successor element. The MCP objective is 0.0 versus
the NLP objective of 0.780, indicating complete failure of the gradient
computation.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| polygon | 0.780 | 0.0 | 100% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/polygon.gms -o /tmp/polygon_mcp.gms
gams /tmp/polygon_mcp.gms lo=2
# Objective: 0.0, expected: 0.780
```

---

## Root Cause Analysis

The polygon model uses:

```gams
Alias(i, j);
```

With offset-indexed alias sums like:

```gams
eq(i).. var(i) =e= sum(j$(ord(j) = ord(i)+1), expr(i,j));
```

This pattern selects the successor element using an ordinal condition on the
alias. The combination of alias + offset creates a challenging pattern for the
AD engine.

### Why 100% Failure

A 100% mismatch (objective = 0.0) suggests that the gradient is entirely zero
for all primal variables, which would cause the stationarity equations to
degenerate to `0 = 0` or trivially satisfied conditions. This can happen when:

1. **All VarRef derivatives return 0**: The `_diff_varref` index matching fails
   for every variable reference because aliased+offset indices never match the
   expected `wrt_indices` tuple.

2. **Sum collapse produces empty results**: The `_partial_collapse_sum` cannot
   find a valid matching for offset-alias patterns, returning 0 derivative.

3. **Stationarity equations become trivial**: With zero objective gradient and
   zero constraint Jacobian terms, all stationarity equations are `piL - piU = 0`,
   and the solver converges to a trivial feasible point (all variables at bounds).

### Investigation Steps

1. Generate the MCP and check if stationarity equations contain any non-trivial terms
2. Test the AD output directly: differentiate the polygon objective w.r.t. each variable
3. Check if `_partial_collapse_sum` can handle `sum(j$(ord(j)=ord(i)+1), ...)`
4. Verify if the offset-alias pattern is fundamentally unsupported

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/polygon.gms` — Source model

## Current Status (2026-03-30)

Translates but MCP compilation fails with $120/$149/$171 errors. Stationarity equations use literal elements with arithmetic offsets (e.g., `theta(i1+1)`) and unknown alias sets. This is distinct from the standard alias differentiation root cause.

## Phase 0: Acceptance Gate

> **🔄 Sprint-30 refresh (Prep Task 5, 2026-07-05): coordinated offset-alias fix; #1111/#1112 architectural-REPLAN boundary.** The Sprint-29 Day-5 revert showed the successor-offset cross-term is **coupled with the distance-Jacobian** (the representative-selection fix made polygon's gradient correct but regressed its **solve** to a spurious 0.0 optimum). Disposition: **PROCEED** to a **coordinated** fix landing the successor-offset cross-term (polygon `stat_theta`) **together with** the distance-Jacobian, gated to the cyclic/successor shape (Unknown 5.2). **Cold-robustness / genuine-floor** (polygon already matches warm), not +Match. **REPLAN to Sprint 31** (the #1111/#1112 AD-engine core) if a localized gate cannot make it correct. Verify: `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms`.

> **Day-0 status (Sprint 29 Prep Task 3/4, 2026-06-25):** the "compile fails / 100% mismatch" status above is **stale (2026-03-30)**. On the current Day-0 DB polygon **matches warm** (`model_optimal_presolve`, 0.7797 ≈ 0.7797) and the harness verdict is **Case b**, `max_residual_row = stat_theta`, rel = **0.492**, dual-transfer consistent → **PROCEED**. The fix is **cold-robustness** (polygon already matches warm), not headline +Match — Class A in `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md`. Also a Case-b validation target for the parent offset-alias-AD architecture (#1111/#1112).

### Hand-Derived KKT Shape

polygon (Largest Small Polygon) optimizes over the angle variables `theta(i)` and radii `r(i)` with offset-alias constraints of the form `… sum(j$(ord(j) = ord(i)+1), expr(i,j)) …` (`j` = alias of `i`, successor element). The angle-variable stationarity must carry, for each constraint `g` in which `theta(i)` (and its offset image `theta(i+1)`) appears, the Jacobian-transpose term `∂g/∂theta(i) · nu_g` summed with the **offset-shifted** contribution from the `i-1`-indexed instance (where `theta(i)` appears as the `j=i` successor of row `i-1`):

```
stat_theta(i)..  ∂obj/∂theta(i) + sum(g, ∂g/∂theta(i)·nu_g)  +  [offset-image cross-term from row i-1]  =E= 0
```

A **non-integer** residual (0.492) indicates a *partial* / mis-scaled offset-alias cross-term (an offset image dropped or mis-weighted), not a cleanly missing unit term — consistent with the offset-alias AD composing the successor selection incorrectly.

### Expected Emit Pattern

`polygon_mcp.gms` `stat_theta(i)` should contain the direct `∂g/∂theta(i)·nu_g` terms **and** the offset-image cross-term contributed by the `ord(j)=ord(i)+1` selection at the predecessor row (the `theta(i)`-as-successor term). (Hypothesis — the actual builder `file:line` to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms --json /tmp/phase0_polygon.json
```

- **PROCEED (Case b):** `max_residual_row = stat_theta`, rel ≈ 0.49. ✅ confirmed Day-0.
- **REPLAN (Case c):** clean residual but cold PATH diverges → non-convexity → Sprint 30. (Not the case here.)
- Post-fix: residual → 0 (Case a) and `compare_objective_match` on the **cold** solve; **add a property-test fixture** for the `ord(j)=ord(i)+1` offset-alias shape (parent #1111/#1112).

### PROCEED/REPLAN Signal

> **🔴 REVERTED — Sprint 29 Day 5 Checkpoint 1 (2026-06-29). Re-deferred to Sprint 30 COUPLED with the distance-Jacobian fix.** The Day-4 representative-selection fix made polygon's *objective gradient* correct (`stat_theta`/`stat_r` got the predecessor cross-term), but the Day-5 Checkpoint-1 **re-solve** caught a regression the Day-4 verification (golden-staleness + harness residual, no actual solve) missed: **polygon went `match` (0.7797) → `mismatch` (spurious 0.0 optimum)**. Root cause = polygon has a SECOND, independent bug — the `distance(i,j)` **constraint-Jacobian symmetry** (`stat_r` sums only the `ord(j)>ord(i)` first-index direction, dropping the symmetric second-index `r(j)` term; the "Multi-pattern Jacobian: skipping correction for distance/r" warning). With the now-complete objective gradient, the still-inconsistent KKT admits a degenerate `area=0` solution → mismatch. Because it broke the **Match ≥ 92 maintain floor**, the fix was **reverted** (`stationarity.py` representative-selection + `_distinct_base_offsets` removed; polygon golden restored byte-identical to pre-Day-4; `shape8` test → strict xfail). **Sprint-30 plan: land the objective-gradient cross-term AND the distance-constraint-Jacobian symmetry TOGETHER** so polygon goes Case a (the two fixes are coupled — neither alone matches). The reverted representative-selection logic is correct and preserved in this issue + the `shape8` fixture/xfail for re-landing.

> **(historical) 🟢 PROCEED — objective-gradient cross-term FIXED (Sprint 29 Day 4, 2026-06-29).** Root pinned: the AD offset enumeration (`_try_diff_sum_offset_crossterms`) and the re-symbolization (`_resymbolize_offset_gradient`) both work — the drop was purely **representative-instance selection** in `src/kkt/stationarity.py` `_build_indexed_gradient_term`. It used the first nonzero instance (polygon's `theta('i1')`, a **boundary** column whose predecessor row is out of range, so its gradient holds only the `+1` offset), and generalized that incomplete gradient to every interior row. **Fix:** when the gradient carries the offset signature, re-select the representative as the nonzero instance with the **maximal distinct-offset set** (new `_distinct_base_offsets` helper). Now `stat_theta(i)` carries BOTH the own-row successor `r(i+1)*r(i)*cos(theta(i+1)-theta(i))$(j(i))` AND the predecessor `r(i)*r(i-1)*cos(theta(i)-theta(i-1))$(j(i-1))`; `stat_r` likewise. Harness `stat_theta` residual **0.49 → 0** (the row is now correct). **No alias-AD-core threading** (Unknown 7.2 PROCEED — the AD/re-symbolization were already correct; only the representative pick was wrong). **cclinpts byte-identical** (the existing #1387 model — no regression). Property fixture `shape8_offset_alias_successor.gms` guards it.
>   **Not yet full Case a:** the residual moved to `stat_r(i14)` rel **0.12** — a **separate** `distance(i,j)` constraint-Jacobian bug (the "Multi-pattern Jacobian: skipping correction for distance/r" warning: `r(i)` appears as both constraint indices, only the `ord(j)>ord(i)` direction is summed). Tracked as the remaining polygon work (constraint-Jacobian symmetry), distinct from this objective-gradient fix.

- **PROCEED** — Day-0 Case b on `stat_theta`, rel ≈ 0.49 (✅ confirmed). _[Day-4: objective-gradient successor cross-term landed (representative-selection fix); residual → separate distance-Jacobian bug.]_
- **Traced Fix-Surface (Day-0) — CONFIRMED (Sprint 29 Day 0, 2026-06-29):** harness re-confirmed **Case b**, `max_residual_row = stat_theta(i12)`, rel = **0.492** (raw 0.492), dual transfer **CONSISTENT** (`/tmp/day0_polygon.json`). The objective `polygon_area =e= 0.5*sum(j(i+1), r(i+1)*r(i)*sin(theta(i+1)-theta(i)))` means `theta(i)` appears in **two** area terms — its own row (as `-theta(i)`) and the predecessor row `i-1` (as `+theta(i+1)`). The regenerated `polygon_mcp.gms:97` emits only the own-row gradient `(-0.5*r(i+1)*r(i)*cos(theta(i+1)-theta(i))*(-1)*1$(j(i)))` and is **missing the predecessor offset-image cross-term** (`+0.5*r(i)*r(i-1)*cos(theta(i)-theta(i-1))` from where `theta(i+1)` resolves to `theta(i)` at row `i-1`) → residual ≈ 0.49 (the dropped term). **Surface:** the successor-offset selection in `src/ad/derivative_rules.py` `_diff_varref` (:371) / `_partial_collapse_sum` non-circular branch (~:1989/:2022) over the dynamic-subset successor `j(i+1)`; index-sub `src/kkt/stationarity.py:3486` `_replace_indices_in_expr`. Cleaner than himmel16 (#1146, cyclic + objvar-gradient sign) — polygon is a **straight dropped offset-image cross-term**. Trace command: `kkt_residual.py data/gamslib/raw/polygon.gms --json /tmp/day0_polygon.json` + `grep stat_theta polygon_mcp.gms`.
