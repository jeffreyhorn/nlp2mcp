# Sprint 29 — Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Task:** Sprint 29 Prep Task 9 (analysis-only — Day-0 hypotheses per PR24; fixtures added in-sprint). Zero `src/` here.
**Date:** 2026-06-27
**Scope:** the Priority-6 objective-mismatch cohort (#1332 quocge, #1247 prolog, #1239 sambal/qsambal, #1236 hhfair) and the Priority-7 offset-alias gradient + dollar-condition AD class (#1146 himmel16, #1143 polygon; backstop #1111/#1112) — framed as Day-0 `kkt_residual.py` fix-surface hypotheses, with a shared-root-cause / consolidation map and a property-test fixture plan.
**Inputs:** the Task-4 Phase-0 gates (per-model harness verdicts), the Task-3 cold-convex survey, the Task-5 REPLAN assessment.

---

## Part A — Objective-mismatch cohort (#1332/#1247/#1239/#1236)

| Issue | Model | Day-0 harness verdict | Day-0 bucket | Fix-surface hypothesis (PR24) | Disposition |
|---|---|---|---|---|---|
| #1332 | quocge | **Case b** `stat_pz` 1.0 — but **matches cold** | `model_optimal` + match | the `stat_pz` residual is the **CGE numéraire/Walras artifact** (camcge family), absorbed by the price normalization → no +Match | **already-banked; Epic 5 (camcge #1330) family, not a P6 fix** |
| #1247 | prolog | **Case a** (healthy) | `model_optimal` + **match** (-6.25e-13 ≈ -0.0) | none — emit is KKT-correct | **resolved — removed from P6** (see §6.3) |
| #1239 | sambal/qsambal | **Case b** `stat_x` 0.78 (both) | `model_optimal_presolve` + match (warm) | the `$xw(i,j)` **dollar-condition not fully propagated** through the conditioned-quadratic-sum gradient (`src/ad/derivative_rules.py` conditioned-sum diff) → **#1112 dollar-condition class** | **cold-robustness (Match-neutral, match warm); consolidates with P7 via #1112** |
| #1236 | hhfair | **harness ERROR** (`$141`/`$257`) | `model_optimal` + **mismatch** (72.147 vs 87.159) | residual MCP won't compile (domain-widened `n(tl)`); then the `prod`/CES log-derivative + chain-rule `stat_*` rows | **the only live P6 +Match — gated on first fixing the residual-emit compile** |

**Net P6 finding:** the cohort has collapsed to **one live +Match target (hhfair)**. quocge is a CGE-numéraire artifact (Epic 5), prolog is resolved, sambal/qsambal are Match-neutral cold-robustness (and consolidate into P7's #1112 work). This confirms the Task-2 / BASELINE_METRICS §3 scope finding from the fix-surface angle.

### §6.3 — prolog's -0.0 reference is valid; prolog is resolved (not CGE-degenerate)

DB check: prolog is `likely_convex`, `model_optimal`, **comparison_status = match**, `nlp_objective = -0.0`, `mcp_objective = -6.25e-13` (≈ -0.0). So the NLP -0.0 reference is a **genuine near-zero optimum**, and the MCP **now reproduces it** (the old -73.5 mismatch is pre-#1227, stale). prolog is **Case-a healthy**, *not* inherently Case-c — the historical #1070 "CES singular Jacobian" framing is superseded (prolog solves cleanly cold). prolog therefore **leaves the Priority-6 mismatch cohort** (already matching), and does **not** move to Category 5 / Epic 5. (Answer to Unknown 6.3: valid reference, real optimum, resolved.)

---

## Part B — Offset-alias gradient (#1146 himmel16, #1143 polygon; #1111/#1112)

**Shared root cause (Unknown 7.1 — confirmed):** both are harness-**Case b** on a single `stat_*` row (himmel16 `stat_area` rel **2.000** cyclic `i++1`; polygon `stat_theta` rel **0.492** `ord(j)=ord(i)+1` successor), both **already match warm**, and both route through the same code — `src/ad/derivative_rules.py` (`_partial_collapse_sum`, `_diff_varref` with `circular=True`) + `src/kkt/stationarity.py` (`_replace_indices_in_expr`). The integer residual (2.0) on himmel16 is the missing-unit-coefficient-cross-term fingerprint. **One offset-alias-AD fix plausibly lands both models.**

**Day-0 fix-surface hypothesis (PR24):** the offset-alias successor/circular selection in `_partial_collapse_sum`/`_diff_varref` drops (himmel16) or mis-scales (polygon) the **offset-image cross-term** — the term contributed when the differentiated variable appears as the `i++1`/`ord=ord+1` image at the predecessor row. The fix corrects that composition for the cyclic + successor shapes.

**Localized-vs-architectural split (the Task-5 REPLAN trigger, Unknown 7.2):** the single-row integer-residual signature **leans localized** — a cross-term correction gated to the cyclic/successor shape, **not** the full #1111 alias-aware-differentiation / #1112 dollar-condition-propagation redesign. **REPLAN to Sprint 30 / Epic 5** only if the prototype must thread the #1111/#1112 core (Task 5 Track C). The #1111/#1112 footprint is small (3 open issues: #1146/#1143/#1162 — Unknown 7.4).

---

## Part C — Property-test fixture plan (Unknown 7.3)

**Catalog gap:** shapes 1–6 (`tests/fixtures/crossterm_shapes/shape{1..6}_*.gms`) do **not** cover the offset-alias gradient shape. The closest, **shape6** (`tree(n,nn)=yes$(ord(nn)=ord(n)+1)` + `sum(nn$tree(nn,n), y(nn))`), is a *tree-predicate-conditioned* aliased sum (the #1390 kand shape) — it tests a predicate-filtered alias sum, **not** the offset-image cross-term in an intermediate/angle variable's stationarity, and it has **no circular (`++`) offset**. So a new fixture is required.

**Plan — two fixtures (himmel16 and polygon are distinct shapes):**

| Fixture | Reproduces | Minimal model sketch | Asserted row |
|---|---|---|---|
| **`shape7_offset_alias_cyclic.gms`** | himmel16 — **circular** `i++1` lead + intermediate-var defining-`=e=`/objective cross-term | `Set i /i1*i4/; Alias(i,j); Variable area(i),x(i),y(i),tot; Equation areadef(i),obj; areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1)); obj.. tot =e= sum(i, area(i)); Model m /all/; solve m maximizing tot using nlp;` | `stat_area(i)` (the unit-coefficient `nu_areadef - nu_obj` cross-term) + the wrapped `stat_x`/`stat_y` `i++1`/`i--1` terms |
| **`shape8_offset_alias_successor.gms`** | polygon — **ordinal-successor** `ord(j)=ord(i)+1` offset-image cross-term (acyclic, boundary) | `Set i /i1*i4/; Alias(i,j); Variable th(i),z; Equation e; e.. z =e= sum(i, sum(j$(ord(j)=ord(i)+1), f(th(i),th(j)))); Model m /all/; solve m maximizing z using nlp;` | `stat_th(i)` (the offset-image cross-term from the `i-1` predecessor row) |

- **Why two, not one:** himmel16's `i++1` is the GAMS **circular-lead** operator (wraps at the set boundary — `_diff_varref` `circular=True`); polygon's `ord(j)=ord(i)+1` is an **acyclic ordinal predicate** with a boundary drop. They exercise different code paths (circular vs predicate offset), and their residual signatures differ (integer 2.0 vs partial 0.49). One fixture would under-test. If the in-sprint prototype shows a single composition fix covers both, the fixtures still both belong in the catalog as regression guards.
- **Always-run, sub-second:** both follow the shapes-1–6 pattern (small synthetic `.gms`, in-process `_emit()` + `_stat_row()` pattern-assert in `test_ad_crossterm_shapes.py`), so they add negligible test time.

---

## Part D — Consolidation map (Unknown 6.2)

| Consolidation | Models | Mechanism | Lands together? |
|---|---|---|---|
| **Offset-alias-AD** (P7) | himmel16 (#1146) + polygon (#1143) | one `_partial_collapse_sum`/`_diff_varref` offset-image composition fix | **Yes** — Task-5 confirmed one fix → two models |
| **Dollar-condition propagation (#1112)** — cross-Category 6↔7 | sambal/qsambal (#1239) **+** the offset-alias pair | sambal/qsambal's `$xw(i,j)` conditioned-sum gradient defect is the **same #1112 dollar-condition-propagation backstop** the offset-alias class routes through | **Possibly** — if the P7 work addresses #1112 dollar-condition propagation (not just #1111 alias-AD), sambal/qsambal may resolve as a side-effect. Worth checking the residual signature overlap in-sprint. |
| **CGE numéraire / Walras** (Epic 5) | quocge (#1332) + camcge (#1330) + the Class-B CGE cohort (irscge/lrgcge/moncge/stdcge) | shared `stat_pz`≈1.0 price-row singularity | **No P6/P7 fix** — Epic 5 transformation (Task 7) |

**Not consolidated (standalone):** hhfair (#1236, product/CES, distinct — the only live P6 +Match). prolog (#1247, resolved).

**Headline consequence:** the genuine fix-class count is small — (1) the offset-alias-AD fix (himmel16+polygon, Match-neutral cold-robustness), possibly extended to (2) the #1112 dollar-condition fix (sambal/qsambal, also Match-neutral), and (3) hhfair as the lone live +Match (gated on its compile fix). quocge → Epic 5.

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo present
grep -Ei '#1332|#1247|#1239|#1236|#1146|#1143|#1111|#1112|shape7|shape8|consolidat' docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md | head
# prolog reference-validity (Unknown 6.3):
.venv/bin/python -c "import json;d=json.load(open('data/gamslib/gamslib_status.json'));m=[x for x in d['models'] if x['model_id']=='prolog'][0];c=m.get('solution_comparison') or {};print('prolog:',c.get('comparison_status'),'| nlp',c.get('nlp_objective'),'mcp',c.get('mcp_objective'))"
# Catalog gap (Unknown 7.3): no offset-alias fixture yet
ls tests/fixtures/crossterm_shapes/ | grep -E 'offset_alias|cyclic' || echo "no offset-alias fixture yet (shape7/shape8 to add)"
```
