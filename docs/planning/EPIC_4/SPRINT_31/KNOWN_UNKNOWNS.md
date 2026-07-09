# Sprint 31 Known Unknowns

**Created:** 2026-07-08
**Status:** Active — Pre-Sprint 31
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 31 (Sprint 30 carryforwards — head-offset IR plumbing, general-alias AD #1111/#1112, dual-consistent CGE Walras, symbolic runtime-guard emit, cold-convex obj-grad residue, non-convex forcing) before implementation begins

---

## Overview

This document identifies all assumptions and unknowns for the Sprint 31 implementation tracks **before** any `src/` change. It continues the Known-Unknowns methodology that has run since Epic 1 Sprint 4, sharpened by the Sprint 27 PR24 rule (prep records the *symptom + reproducer*; the fix surface is a Day-0-re-confirm hypothesis, never trusted from the prep doc) and the Sprint 28 PR27 rule (the KKT-residual harness Case-(a/b/c) verdict is the standard verification instrument).

Sprint 31 is **specification-bound, not diagnosis-bound** — every core carryforward inherits a Sprint-30 *control-verified* recipe or a *precisely-pinned* root cause, so Sprint 31 implements against a banked specification rather than re-diagnosing. But two structural Sprint-30 lessons dominate the unknowns: **(1)** the banked recipe is still a hypothesis that must survive a **control experiment before any high-blast-radius `src/` change** — Sprint 30 *refuted five* banked diagnoses this way (the obj-grad sign flip three times, the Class-B `stat_pz` "coefficient bug" which was really case-normalization, and the camcge Walras drop-row which broke the dual); the single-point harness residual is systematically misleading for non-convex / objective-defining-intermediate-variable shapes. **(2)** "Solution-preserving on paper" ≠ "correct in the MCP" — **always check the dual side** (the camcge lesson). So the Sprint 31 unknowns are less "what is the bug?" and more "does the banked recipe still reproduce on today's tree, and does the *foundational* change (P1 IR plumbing) / the *dual side* (P3) / the *coupled* half (P2) behave as the recipe assumes?"

**Sprint 31 Scope** (`docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31 (Weeks 27–28)"):
1. **mine head-offset IR plumbing + shared 3-site helper** (#1443) — Sprint 30 Day 6 found the head-offset detail is *not stored in the IR* (`pr.has_head_domain_offset` is a bare bool), so Sprint 31 plumbs the head-offset δ + `li(k)`/`lj(k)` through parse → normalize → KKT *then* builds the shared 3-site index-map helper (+1 Solve)
2. **offset-alias general-alias core #1111/#1112** (polygon) — the Day-7 control-verified 4-term fix (warm-match 0.780) + the Day-8 objective-successor half (reverted) must land coupled with the **distance-Jacobian second-index** cross-term (genuine-floor +1)
3. **camcge #1330 → dual-consistent Walras transform** (Epic 5) — the Day-11 price-pin reaches the correct omega 191.735 but the naive drop-row breaks the MCP *dual*; the fix is a dual-consistent multiplier redefinition (potential +1 Solve)
4. **#1385 sarf — symbolic runtime-guard cross-term emit** — a dedicated builder-pipeline-aware rebuild of the Sprint-26-failed architecture (2-D dynamic-subset extension + the banked `stat_task` derivation) (+Translate)
5. **cold-convex obj-grad residue** (hhfair `stat_u` / CGE `stat_xp`) — the objective-defining-intermediate-variable family whose sign-flip fix was *control-refuted three times*; needs the ν_objective reduction, not a sign flip (+Match / genuine-floor)
6. **rocket #1462 — non-convex forcing → PATH-consultation input** — the `--force` scaffold landed Sprint 30; exhaust the emittable levers + author the concrete PATH-consultation question (conditional +1 Solve / Sprint-32 hand-off)
7. **Infrastructure** — property-test catalog completion (`shape8` enable + head-offset fixture) + the PR25 genuine-floor tracking recompute against the S31–S33 re-baselined Match KPIs

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31" (Priorities 1–7 + Acceptance Criteria + Estimated Effort 92–134h + Risk HIGH); prep tasks: `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md`. (No separate `PRELIMINARY_PLAN.md` exists for Sprint 31 — the PROJECT_PLAN §"Sprint 31" entry + this PREP_PLAN are the planning source.)

**Lessons from Sprint 30** (`docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md`):
- §4 "Sprint-31 carryforwards" — the seven tracks below carry a *control-verified* Sprint-30 recipe (the SPRINT_LOG per-day entries + the per-track ISSUE docs), so Sprint 31 implements rather than re-diagnoses; but each banked recipe is re-framed here as a Day-0 hypothesis (PR24).
- §3 lesson 1 — **five banked diagnoses were refuted by control experiments before any bad ship** (the obj-grad sign flip three times, the Class-B `stat_pz` case-normalization, the camcge drop-row). → Every Category-5 unknown bans the sign flip and requires the ν_objective control experiment; every emit-touching Critical is gated on a control experiment (Task 6).
- §3 lesson 2 — **"solution-preserving on paper" ≠ "correct in the MCP" — check the dual side** (camcge). → Category 3's unknowns center the dual-consistent redefinition, not the primal-correct drop-row.
- §3 lesson 3 — **the Task-6 REPLAN prediction was accurate** (mine, rocket, camcge all REPLAN'd; polygon surfaced the #1111/#1112 boundary). → The genuine-floor ramp (→≥73) is treated as *conditional* on the #1111/#1112 core (P2) + the dual-consistent CGE work (P3) + the obj-grad reduction (P5), not as independent +1s (Task 7).
- §3 lesson 5 — **front-load the tractability probes** (the mine IR-plumbing blocker + the polygon #1111/#1112 boundary were Day-0-discoverable). → Task 3 designs the P1 IR plumbing + round-trip *before* the schedule; Day 0 runs the P1 round-trip + P3 `/tmp` prototype + P5 hhfair control experiment.

**Deferred unknowns carried from Sprint 30:** all 25 Sprint 30 prep unknowns were VERIFIED or documented WRONG-with-correction (`docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §"Next Steps"). Several Sprint-30 unknowns became the direct parents of Sprint-31 categories: **Sprint-30 Unknown 1.1** (❌ WRONG — robert does NOT generalize to mine; robert landed standalone, mine REPLAN'd) → the Sprint-31 mine head-offset IR-plumbing track (Category 1); **Sprint-30 Unknown 1.2** (mine is a coordinated 3-site fix that needs the IR change first) → Category 1; **Sprint-30 Unknown 5.1/5.2** (the offset-alias Day-5 revert coupling is the #1111/#1112 general-alias core) → Category 2; **Sprint-30 Unknown 6.1/6.2** (the camcge Walras transform breaks the dual) → Category 3; **Sprint-30 Unknown 2.2** (rocket intrinsic non-convergence → PATH-side) → Category 6. The Sprint 31 unknowns are net-new, derived from the six carryforward priorities + the infrastructure track.

---

## How to Use This Document

### Before Sprint 31 Day 1
1. Research and verify all **Critical** and **High** priority unknowns during prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases / run the `kkt_residual.py` trace + the cold-solve control experiment for validation.
3. Document findings in each "Verification Results" section.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 31
1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly discovered unknowns (template below).
3. Update with implementation findings.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

### Priority Definitions
- **Critical:** Wrong assumption derails a priority or forces a mid-sprint REPLAN (>8 hours of churn / a lost target).
- **High:** Wrong assumption causes significant rework (4–8 hours) or a scope reduction.
- **Medium:** Wrong assumption causes minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 25

**By Priority:**
- Critical: 6 (the foundational IR-plumbing round-trip + the coupled offset-alias core + the dual-consistent Walras + its false-positive detector + the control-refuted obj-grad reduction)
- High: 10 (unknowns requiring upfront research before their priority's Day-0 re-confirm)
- Medium: 6 (resolvable during the relevant prep task)
- Low: 3 (nice-to-know / low impact)

**By Category:**
- Category 1 (mine head-offset IR plumbing + shared 3-site helper — #1443): 4 unknowns
- Category 2 (offset-alias general-alias core #1111/#1112 — polygon): 4 unknowns
- Category 3 (camcge #1330 → dual-consistent Walras transform): 4 unknowns
- Category 4 (#1385 sarf — symbolic runtime-guard cross-term emit): 3 unknowns
- Category 5 (cold-convex obj-grad residue — hhfair `stat_u` / CGE `stat_xp`): 4 unknowns
- Category 6 (rocket #1462 — non-convex forcing → PATH-consultation input): 3 unknowns
- Category 7 (infrastructure — property-test catalog + genuine-floor tracking): 3 unknowns

**Estimated Research Time:** 28–36 hours (the per-unknown estimates below sum to ~36h, but many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping". The authoritative scheduling budget is the per-task total in `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md`: 35–49h across Tasks 1–10.)

---

## Table of Contents

1. [Category 1: mine Head-Offset IR Plumbing + Shared 3-Site Helper (#1443)](#category-1-mine-head-offset-ir-plumbing--shared-3-site-helper-1443)
2. [Category 2: Offset-Alias General-Alias Core #1111/#1112 (polygon)](#category-2-offset-alias-general-alias-core-11111112-polygon)
3. [Category 3: camcge #1330 → Dual-Consistent Walras Transform](#category-3-camcge-1330--dual-consistent-walras-transform)
4. [Category 4: #1385 sarf — Symbolic Runtime-Guard Cross-Term Emit](#category-4-1385-sarf--symbolic-runtime-guard-cross-term-emit)
5. [Category 5: Cold-Convex Obj-Grad Residue (hhfair `stat_u` / CGE `stat_xp`)](#category-5-cold-convex-obj-grad-residue-hhfair-stat_u--cge-stat_xp)
6. [Category 6: rocket #1462 — Non-Convex Forcing → PATH-Consultation Input](#category-6-rocket-1462--non-convex-forcing--path-consultation-input)
7. [Category 7: Infrastructure — Property-Test Catalog Completion + Genuine-Floor Tracking](#category-7-infrastructure--property-test-catalog-completion--genuine-floor-tracking)
8. [Template for New Unknowns](#template-for-new-unknowns)
9. [Next Steps](#next-steps)
10. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: mine Head-Offset IR Plumbing + Shared 3-Site Helper (#1443)

## Unknown 1.1: Can the head-offset detail round-trip through normalization so the KKT layer can read it?

### Priority
**Critical** — this is the *foundational* blocker Sprint 30 Day 6 hit. If the head-offset δ + `li(k)`/`lj(k)` cannot be stored on `EquationDef` and survive `normalize_model` (which today collapses `pr.domain` to `(k,l,i,j)` and drops the `l+1` head), the shared 3-site helper cannot be built at all, and the entire P1 timeline — and the mine +1 Solve — shifts.

### Assumption
The head-offset detail (position `l`, amount `+1`) and the body parameter offsets `li(k)`/`lj(k)` can be stored on `EquationDef` (or an `IndexOffset`-carrying structure) as a **field addition** that round-trips cleanly through parse → normalize → KKT, without altering the domain semantics other equations rely on — i.e. normalization can be made to *preserve* the head-offset detail rather than actively rewriting it away.

### Research Questions
1. Where exactly in `src/ir/normalize.py` is `pr.domain` collapsed to `(k,l,i,j)` and the `l+1` head lost — is it a destructive rewrite or a lossy projection?
2. Can the head-offset δ + `li(k)`/`lj(k)` be attached to `EquationDef` and read at the KKT/emit layer with a field addition, or does normalization actively re-derive the domain (so preserving the head needs a deeper change)?
3. Does preserving the head-offset detail change the normalized domain any *other* equation depends on (blast-radius against the emit core)?
4. Does the round-trip unit reproduction (parse→normalize asserting the head-offset survives) pass with the minimal change?

### How to Verify
Trace the normalize collapse site; design the `EquationDef` storage; author a minimal mine-shaped fixture and assert its parse→normalize output carries the head-offset δ + `li(k)`/`lj(k)`:
```bash
grep -rn "has_head_domain_offset" src/ir/
grep -n "domain" src/ir/normalize.py | head
# Expect: the head-offset detail attaches to EquationDef + survives normalize (field addition) → P1 Phase 1 gate green
#         normalization re-derives the domain destructively → deeper IR change, re-size P1 Phase 1
```

### Risk if Wrong
- **Normalization re-derives destructively:** P1 Phase 1 (IR plumbing) is a deeper change than a field addition → the ~11h heaviest day overruns, mine REPLANs to Sprint 32 with the IR-plumbing partially landed.
- **Blast radius into other equations' domains:** a naive preserve corrupts unrelated normalized domains → a hidden regression the golden-staleness gate must catch before ship.

### Estimated Research Time
3 hours (Task 3 — the normalize-collapse trace + the `EquationDef` storage design + the round-trip fixture spec)

### Owner
Development team (IR/AD specialist)

### Verification Results
✅ **Status:** VERIFIED — favorable: a field addition, not a deep normalize rewrite
**Verified by:** Task 3 (Head-Offset IR-Plumbing Design)
**Date:** 2026-07-08
**Findings:** The head offset is discarded at **parse**, NOT at normalization. A read-only parse of `mine.gms` shows `pr.domain=('k','l','i','j')` (base labels) + `has_head_domain_offset=True` — the `l+1` is already gone before normalize runs. The culprit is `_domain_list_has_offset` (`src/ir/parser.py:932`), which walks the domain elements but returns only a bool; `_extract_domain_indices` (`:956`) strips each element to its base name. **Normalization does not re-collapse** — `NormalizedEquation` (`src/ir/normalize.py:13`) doesn't even carry `has_head_domain_offset`, and the KKT/emit consumers read the original `EquationDef` from `model_ir.equations[name]`. So the fix is a **field addition** on `EquationDef` (`head_domain_offsets`, a per-position `IndexOffset` tuple mirroring the `declaration_domain` precedent from #1327) + copy-through at the ~3 reconstructor sites (`sqr_reformulation.py:88/:108`, `complementarity.py:242`) that already copy `has_head_domain_offset`. The parameter offsets `li(k)`/`lj(k)` are ALREADY preserved in the body (`lhs = x(l, IndexOffset('i',ParamRef(li(k))), IndexOffset('j',ParamRef(lj(k))))`); only the domain head δ needs plumbing. The round-trip unit fixture (`tests/fixtures/head_offset_ir_roundtrip.gms`) asserting `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)` is the Phase-1 gate.
**Evidence:** `docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md` §0–§4 (empirical parse + code trace + fixture spec).
**Decision:** PROCEED with the Phase-1 IR field addition (favorable — not a deep normalize rewrite); the round-trip fixture gates Phase 2. The hard/REPLAN-prone work stays in Phase 2 (the shared helper + `comp_pr` coupling).

---

## Unknown 1.2: Does one shared index-map helper drive all three sites, or does a 4th site surface?

### Priority
**Critical** — sizes the P1 Phase-2 budget; a "4th site" outcome is the deeper-architecture slip the Sprint 30 REPLAN warned about (→ Sprint-32 REPLAN exit).

### Assumption
Once the head-offset detail is plumbed (Unknown 1.1), a **single index-map helper** parameterized by (head-offset δ on `l`, param offsets `li(k)`/`lj(k)`) correctly drives all **three** emit sites — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer, (3) the landed `stat_x` cross-term — applied atomically, with no fourth site (e.g. a `comp_lo_x`/`comp_up_x` bound-complementarity coupling) surfacing in the cold LCP.

### Research Questions
1. Are the three sites the *complete* set after the IR plumbing, or does the cold LCP surface a fourth (bound-complementarity) coupling?
2. Can all three sites share one head-offset index-map helper, or does each need bespoke logic?
3. Sprint 30 (`ISSUE_1443` Day-7): hand-fixing Site 2 (dual transfer) cleared only the `nw` direction (`li=lj=0`), leaving `ne`/`se`/`sw` at ~1e10 — is that the parameter-offset composition the helper closes, or a separate `comp_pr` re-derivation?
4. What is the realistic hour estimate for the coordinated 3-site change + its blast-radius regen, within the ~14–20h P1 ceiling?

### How to Verify
Trace the three emit sites against the plumbed IR; prototype the shared helper (env-guarded, zero `src/`) and evaluate mine's cold LCP by k-direction; measure which INFES rows remain:
```bash
grep -n "_emit_nlp_presolve\|comp_pr\|stat_x" src/emit/emit_gams.py src/kkt/stationarity.py | head
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms
# Expect: shared helper drives all three sites → cold MS 1 across all four k-directions → PROCEED
#         a 4th site (bound coupling) or the ne/se/sw cascade persists → REPLAN mine to Sprint 32
```

### Risk if Wrong
- **4th site / cascade:** P1 overruns → REPLAN mine to Sprint 32; the freed ~10–16h re-allocates to the genuine-floor P5 obj-grad + P2 polygon work (Task 7 reallocation).

### Estimated Research Time
2.5 hours (Task 3 — the 3-site trace against the plumbed IR + the shared-helper prototype)

### Owner
Development team (AD/KKT specialist)

### Verification Results
✅ **Status:** VERIFIED — mine-only; 3 sites confirmed with a bounded 4th-site risk
**Verified by:** Task 3 (Head-Offset IR-Plumbing Design)
**Date:** 2026-07-08
**Findings:** Once the head δ is plumbed (1.1), a single helper parameterized by (head δ from `head_domain_offsets`, param offsets from the body) drives the three sites atomically: Site 1 `comp_pr` head var (`emit_gams.py:2951/:3125`, `equations.py:1072/:1103/:1173`), Site 2 the `--nlp-presolve` dual transfer (`_emit_nlp_presolve`, `emit_gams.py:1354`), Site 3 the landed `stat_x` cross-term (`_try_build_param_offset_crossterm`, `stationarity.py:5618/:5825`). Partial application is the Day-7 failure mode (Site-2-only clears `nw` but leaves `ne/se/sw` at ~1e10) → the helper is the single source of truth, applied to all three or none. The **4th-site risk** is a bound-complementarity coupling (`comp_lo_x`/`comp_up_x` ⊥ `piL_x`/`piU_x`) surviving after the `comp_pr` fix (Day-4 saw 49 INFES across comp_pr/comp_lo_x/comp_up_x/stat_x/def; Day-6 attributed the driver to the 38 comp_pr rows) — the explicit Sprint-32 REPLAN exit.
**Evidence:** `HEAD_OFFSET_IR_PLUMBING_DESIGN.md` §5–§6 (helper signature + the three sites with current file:line + the cold-INFES-by-direction gate); `ISSUE_1443` Day-6/7.
**Decision:** PROCEED with the shared 3-site helper; REPLAN mine to a Sprint-32 head-offset-Phase-3 workstream if the bound rows persist after the comp_pr fix (the IR plumbing + helper still land as reusable foundation).

---

## Unknown 1.3: Does the head-offset fix leave the cold LCP feasible (mine's ~4.07e10 blowup resolved)?

### Priority
**High** — a residual bound-complementarity coupling after the head-offset fix would mean mine needs a *second* fix (bounds), extending P1.

### Assumption
mine's cold failure (MS 5, `x → ~4.07e10` across all four k-directions, `comp_pr` LCP infeasibility) is driven *entirely* by the head-offset mis-alignment; so a correct head-offset emit (via the shared helper) drives the cold LCP to MS 1 with no residual bound-complementarity coupling — mine is a convex LP (a monotone LCP), so a correct emit MUST cold-solve (no warm-start escape, no Case-c).

### Research Questions
1. After the head-offset fix, do the `comp_lo_x`/`comp_up_x` bound rows clear, or does a residual remain?
2. Is the ~4.07e10 blowup purely the `comp_pr` LCP residual (Sprint 30 Day 6 finding), fully resolved by the head-offset fix?
3. Does mine reach MS 1 *cold* (not just warm-started), confirming the convex-LP expectation?

### How to Verify
After the Task-3 design, evaluate mine's corrected cold emit and confirm the LCP residual → 0 and MS 1 by direction:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms
# Expect: residual → 0 at the head-offset fix, cold MS 1 across all four k-directions (convex LP)
```

### Risk if Wrong
- **Residual bound coupling:** P1 needs a second (bounds) fix → +2–4h; if the coupling is deep, mine REPLANs.

### Estimated Research Time
2 hours (Task 3 — the cold-LCP-consistency check after the head-offset design)

### Owner
Development team (AD/KKT specialist)

### Verification Results
✅ **Status:** VERIFIED (hypothesis firm) — convex LP ⇒ no Case-c escape
**Verified by:** Task 3 (Head-Offset IR-Plumbing Design)
**Date:** 2026-07-08
**Findings:** mine is a convex LP (a monotone LCP), so a correct emit MUST cold-solve — there is no warm-start escape and no Case-c exit (cold infeasibility here *is* the emit bug). The Phase-2 completion gate is the cold-INFES-by-direction histogram driven to zero: baseline ~4.07e10 across nw/ne/se/sw → the shared 3-site helper must drive all four `comp_pr` directions to 0 → cold MS 1 with `x ≤ x.up = 1` (no `x → 4e10`) and `compare_objective_match`. A residual after the 3-site fix is a remaining emit/index-map bug (still Case-b — take the 4th-site bound-complementarity exit, Unknown 1.2), NOT non-convexity. (This is the same convex-LP guarantee `ISSUE_1443` Day-0/Day-6 established; unchanged by the IR-plumbing design.)
**Evidence:** `HEAD_OFFSET_IR_PLUMBING_DESIGN.md` §6 (the cold-INFES histogram + the `kkt_residual.py` / cold-solve gate); `ISSUE_1443` Day-0 (convex LP, no Case-c).
**Decision:** the cold-LCP-consistency criterion (all four directions → 0, cold MS 1) is the Phase-2 PROCEED gate; a residual → the 4th-site Sprint-32 REPLAN, never a warm-start fallback.

---

## Unknown 1.4: Is the IR plumbing blast-radius-safe (no regression to other equations' normalized domains)?

### Priority
**Medium** — a preserve-the-head change that leaks into unrelated normalized domains is a hidden regression, but the golden-staleness gate + the full retest catch it; the impact is rework, not a lost target.

### Assumption
Storing + preserving the head-offset detail on `EquationDef` touches *only* the head-offset-bearing equations (mine's `pr`, and any structurally identical shape); every other model's normalized domain is byte-identical, so the IR change is additive with a bounded blast radius verifiable by the golden-staleness gate + a full re-solve.

### Research Questions
1. How many corpus models have a head-domain-offset equation shape (the blast-radius set)?
2. Does the preserve-the-head change alter any non-head-offset equation's normalized domain (a byte diff in its golden)?
3. Does the `--resolve-changed` checkpoint select exactly the head-offset-bearing models after the IR change?

### How to Verify
Scan the corpus for the head-offset shape; regen goldens; confirm only head-offset models diff:
```bash
grep -rln "has_head_domain_offset" src/ir/
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py
# Expect: only mine (+ any structurally identical shape) diffs; all other goldens byte-stable
```

### Risk if Wrong
- **Leaky change:** unrelated goldens shift → a hidden regression; +2–4h to gate + narrow the change.

### Estimated Research Time
1 hour (Task 3 — the blast-radius scan + the golden-staleness confirmation)

### Owner
Development team (IR specialist)

### Verification Results
✅ **Status:** VERIFIED — zero emit change from the field addition; Phase-2 helper is mine-only
**Verified by:** Task 3 (Head-Offset IR-Plumbing Design)
**Date:** 2026-07-08
**Findings:** The `head_domain_offsets` field addition changes **no emit output** — populating it is inert until a consumer reads it (no Phase-1 emit path branches on it). The meaningful blast radius is the **Phase-2 helper**, gated (as today) to the non-`Const` parameter-offset shape, which fires on **mine only** (the Sprint-28 gate note: launch/camshape/otpop/trnsport byte-identical). A read-only corpus sample shows head-offset *equations* are common (mine `pr`, robert `sb`, camshape `eqrdiff`, ramsey `kk`, abel `stateq`) but the parameter-offset coupling is rare (mine). The IR change touches only additive storage + the ~3 reconstructor copy-through sites; `NormalizedEquation` is unaffected, so no other equation's normalized domain changes.
**Evidence:** `HEAD_OFFSET_IR_PLUMBING_DESIGN.md` §3 (blast-radius guard + the reconstructor touchpoints + the corpus sample table).
**Decision:** the Phase-1 verification (in-sprint) is a full-corpus parse-scan enumerating every `has_head_domain_offset=True` equation + a golden byte-diff showing **zero changes** before Phase 2 touches any emit site.

---

# Category 2: Offset-Alias General-Alias Core #1111/#1112 (polygon)

## Unknown 2.1: Does the Sprint-30 Day-7 control-verified 4-term recipe still reproduce on the current tree?

### Priority
**High** — the P2 design starts from the banked 4-term recipe (warm-match 0.780); PR24 says re-confirm it on today's tree before building on it (the hhfair `$141`→`$184` cautionary tale).

### Assumption
The Sprint-30 Day-7 control experiment — polygon's 4-term coupled fix reaches warm-match 0.780 ≈ NLP 0.7797 — still reproduces on the current `main`, so the banked recipe (`ISSUE_1143` Day-7/8 blocks) is a valid starting point and no re-diagnosis is needed before the coupled-landing design.

### Research Questions
1. Does the 4-term recipe reproduce (warm-match 0.780) on the current tree, or has intervening `src/` drift changed the emit?
2. Does the Day-8 objective-successor half (interior-representative selection in `_build_indexed_gradient_term`) still apply cleanly as the reverted-but-verified half?
3. Is polygon still `model_infeasible` / warm-only-match at Day 0 (the genuine-floor candidate bucket)?

### How to Verify
Re-run the Day-7 control experiment on the current tree; confirm the 4-term recipe reaches warm-match 0.780:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms
# Expect: the 4-term recipe reproduces (warm-match 0.780) → banked recipe valid → build the coupled design
#         drift → re-diagnose before the coupled-landing design (PR24)
```

### Risk if Wrong
- **Recipe drifted:** the P2 design starts from a stale recipe → re-diagnose (the exact churn PR24 prevents); +2–4h.

### Estimated Research Time
1.5 hours (Task 4 — the Day-7 control-experiment re-run on the current tree)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Does the distance-Jacobian second-index cross-term land coupled without regressing the CGE multi-pattern cohort?

### Priority
**Critical** — the Day-8 objective-successor half was *reverted* precisely because it can't ship alone; it needs the coupled distance-Jacobian second-index cross-term (the #1111/#1112 general-alias core). If restoring the second-index term leaks into the CGE multi-pattern cohort, P2 demands the full AD-engine core (→ Sprint-32 filing) and polygon's genuine-floor +1 is at risk.

### Assumption
The distance-Jacobian second-index cross-term — a variable at two index-positions of a 2-index constraint, which `_add_indexed_jacobian_terms` currently drops — can be **restored and tightly gated to the var-at-two-indices shape**, landing coupled with the objective-successor half, without regressing the CGE multi-pattern cohort (the Issue #1110 diagonal-vs-off-diagonal topology is *orthogonal* to var-at-two-indices).

### Research Questions
1. At exactly what point in `_add_indexed_jacobian_terms` is the second-index cross-term dropped, and what is the minimal restoration?
2. Is the Issue #1110 multi-pattern (diagonal-vs-off-diagonal) correction independent of var-at-two-indices, so restoring the second-index term does not disturb the CGE cohort?
3. Does the coupled fix (objective half + second-index half) reach warm-match on polygon with `shape8_offset_alias_successor` enabled?
4. Does the `--resolve-changed` GO list stay green on the CGE multi-pattern models after the change?

### How to Verify
Locate the drop; prototype the second-index restoration (env-guarded); enable `shape8`; run the CGE multi-pattern GO list:
```bash
grep -rn "_add_indexed_jacobian_terms" src/ad/constraint_jacobian.py
grep -n "shape8_offset_alias_successor\|strict=True" tests/integration/emit/test_ad_crossterm_shapes.py
# Expect: second-index restoration gates tightly → shape8 passes, CGE cohort byte-stable → PROCEED
#         the fix leaks into the CGE cohort → #1111/#1112 AD-engine filing → REPLAN P2 to Sprint 32
```

### Risk if Wrong
- **Leaky gate:** polygon's +1 REPLANs to the #1111/#1112 AD-engine workstream (Sprint 32); the genuine-floor ramp loses one contributor (Task 7 flags this as conditional).

### Estimated Research Time
2.5 hours (Task 4 — the `_add_indexed_jacobian_terms` drop-site location + the second-index restoration prototype + the #1110 orthogonality check)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Is the second-index cross-term gateable to var-at-two-indices, or does it need the full #1111/#1112 core?

### Priority
**High** — determines whether P2 is a tightly-gated localized fix (this sprint) or the general-alias AD-engine core (a Sprint-32 architectural filing).

### Assumption
The second-index cross-term restoration can be gated to the *specific* var-at-two-indices offset-alias shape (polygon's successor-offset), so it does NOT require the full #1111 alias-aware-differentiation / #1112 dollar-condition-propagation core — the localized fix ships this sprint and the general core defers.

### Research Questions
1. Can the gate be expressed as a structural predicate on the constraint (var appears at two index-positions with an offset-alias), or does it require alias-aware differentiation to detect?
2. Does the localized fix leave the #1111/#1112 dollar-condition-propagation cases untouched (they are separate shapes)?
3. If the gate cannot be made tight, what is the Sprint-32 #1111/#1112 AD-engine filing scope?

### How to Verify
Prototype the structural gate predicate; confirm it fires on polygon only across the offset-alias/multi-pattern cohort:
```bash
# Enumerate offset-alias / var-at-two-indices constraints across the corpus; confirm the gate is polygon-tight
grep -rn "_add_indexed_jacobian_terms\|indexed_jacobian" src/ad/constraint_jacobian.py | head
# Expect: a structural gate fires on polygon only → localized fix ships; else → Sprint-32 #1111/#1112 filing
```

### Risk if Wrong
- **Needs the full core:** P2 re-scopes to the #1111/#1112 AD-engine filing (Sprint 32); polygon's +1 becomes conditional (Task 7).

### Estimated Research Time
1.5 hours (Task 4 — the gate-predicate design + the corpus-wide fire check)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Is himmel16 confirmed non-convex (no emit fix converts it) — the P2 scope guard?

### Priority
**Medium** — a scope guard: if himmel16 is *not* non-convex, P2 has an extra target; but the Day-7 sign-fix refutation says it is, so mis-scoping himmel16 into P2 would waste budget.

### Assumption
himmel16's circular `i++1` offset-alias `stat_area` residual (2.0) is a *numeric*/sign defect in the objvar-defining-gradient interaction — a documented **non-convexity** (Sprint 30 Day 7 refuted its sign fix; `shape7_offset_alias_cyclic` guards the structural decomposition, but the numeric residual is inherent), NOT something the #1143 representative-selection fix or the P2 second-index restoration converts.

### Research Questions
1. Is the himmel16 `stat_area` residual structurally present (the `shape7` decomposition) but numerically inherent (non-convex), per the Day-7 refutation?
2. Does the P2 second-index restoration touch himmel16's shape at all, or is it orthogonal?
3. Is himmel16 correctly documented as a non-convex hand-off (not a P2 deliverable)?

### How to Verify
Confirm the Day-7 refutation holds; check `shape7` guards the structure without asserting the numeric fix:
```bash
grep -n "shape7_offset_alias_cyclic\|himmel16\|non-convex" tests/integration/emit/test_ad_crossterm_shapes.py
# Expect: shape7 guards the structural decomposition; himmel16 numeric residual documented non-convex (no P2 fix)
```

### Risk if Wrong
- **Convertible after all:** a missed P2 target — low downside (an extra gain, not a lost one).

### Estimated Research Time
1 hour (Task 4 — the himmel16 non-convex scope-guard confirmation)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: camcge #1330 → Dual-Consistent Walras Transform

## Unknown 3.1: Does the dual-consistent multiplier redefinition reach MS 1 at omega 191.735?

### Priority
**Critical** — the Day-11 price-pin proves the *target* allocation (omega 191.735) but the naive drop-row gives omega 299 / MS-4; the dual-consistent redefinition is the *unproven* step. If it doesn't reach MS 1, camcge's +1 Solve REPLANs and the Epic-5 track stalls.

### Assumption
Expressing the dropped market-clearing row's dual via **Walras' law** (∑ excess-demand·price ≡ 0) — so the dropped market's price/wage multiplier stays available in the stationarity — reaches MODEL STATUS 1 at omega 191.735, where the naive drop-row (which orphans that multiplier) gives omega 299 / MS-4.

### Research Questions
1. Does the dual-consistent redefinition (Walras'-law-expressed dual) reach MS 1 at omega 191.735 in a hand-edited `/tmp` MCP (the Day-11-style control experiment)?
2. Which market-clearing multiplier does the naive drop-row orphan, and does the Walras'-law expression restore exactly it in the stationarity?
3. Does the price-ray pin (numéraire) compose with the dual-consistent redefinition, or are they alternatives?

### How to Verify
Prototype the dual-consistent redefinition on `/tmp` (hand-edited from `camcge_mcp.gms`); solve; read MS + omega:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camcge.gms
# Expect: dual-consistent redefinition → MS 1 at omega 191.735 (correct allocation) → PROCEED
#         still MS-4 / omega 299 → the dual side is not yet consistent → re-derive before src (PR24)
```

### Risk if Wrong
- **Still MS-4:** the dual-consistent redefinition is wrong → re-derive; if intractable, camcge REPLANs with the per-model-numéraire-declaration fallback (Epic-5-scoped).

### Estimated Research Time
2.5 hours (Task 5 — the dual-consistent redefinition design + the `/tmp` prototype to MS 1)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Does the S1∧S2∧S3 degeneracy detector flag ONLY camcge (no false-positive)?

### Priority
**Critical** — the "check the dual side" lesson made concrete: silently redefining a dual on a *well-posed* CGE would corrupt it. The detector must be precise; a false-positive is a silent corruption the golden-staleness gate might not catch semantically.

### Assumption
There is a robust S1∧S2∧S3 conjunctive degeneracy signature (the market-clearing redundancy pattern) that flags **camcge** and passes through every other model (irscge/lrgcge/moncge/stdcge and the whole corpus) by default — so the dual-consistent redefinition applies only where the market-clearing system is genuinely rank-deficient.

### Research Questions
1. What are the three conjunctive conditions (S1∧S2∧S3) that characterize camcge's market-clearing redundancy?
2. Do irscge/lrgcge/moncge/stdcge fail at least one condition (pass-through), confirming the detector's precision?
3. Is the pass-through default safe (a non-flagged model emits exactly as today)?
4. Can the detector be unit-tested against the CGE cohort to prove the false-positive rate is zero?

### How to Verify
Define S1∧S2∧S3; evaluate the predicate across the CGE cohort; confirm camcge-only:
```bash
# Run the detector predicate across irscge/lrgcge/moncge/stdcge/camcge; confirm only camcge flags
for m in camcge irscge lrgcge moncge stdcge; do echo "== $m =="; \
  grep -l "$m" data/gamslib/raw/$m.gms >/dev/null 2>&1 && echo "present"; done
# Expect: camcge flags (S1∧S2∧S3 all true); irscge/lrgcge/moncge/stdcge each fail ≥1 → pass-through
```

### Risk if Wrong
- **False-positive:** a well-posed CGE is silently transformed → corrupted output → the per-model-numéraire-declaration fallback (opt-in, not auto-detect) becomes the required design.

### Estimated Research Time
2 hours (Task 5 — the S1∧S2∧S3 signature design + the cohort false-positive check)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Is the redundant-row + numéraire selection a single automatic rule or a per-model declaration?

### Priority
**High** — determines whether P3 ships an automatic transform (converts camcge cleanly) or a per-model-declaration fallback (Epic-5-scoped, lower coverage).

### Assumption
The redundant market-clearing row + the numéraire (price-ray pin) can be selected by a **single automatic rule** (drop the Walras-redundant row, pin the numéraire price) that composes with the dual-consistent redefinition — not a per-model hand declaration.

### Research Questions
1. Is the redundant row identifiable automatically (the linearly-dependent market-clearing equation), or does it require a model-specific choice?
2. Is the numéraire selectable automatically (e.g. a canonical price), or model-specific?
3. If automatic selection is non-robust, what is the per-model-declaration fallback's syntax/scope?

### How to Verify
Attempt automatic redundant-row + numéraire selection on camcge; confirm it matches the Day-11 hand choice (`p('services')=pd0`):
```bash
# Confirm the automatic rule selects the same redundant row + numéraire as the Day-11 hand recipe
grep -in "services\|numeraire\|pd0" docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md | head
# Expect: automatic rule = Day-11 hand choice → single rule; else → per-model-declaration fallback
```

### Risk if Wrong
- **Per-model needed:** P3 ships the declaration fallback (Epic-5-scoped); lower automatic coverage but camcge still lands.

### Estimated Research Time
1.5 hours (Task 5 — the redundant-row + numéraire selection rule design)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: Does the Walras'-law dual expression hold across camcge's full market structure?

### Priority
**High** — the dual-consistent redefinition rests on Walras' law holding exactly at the MCP solution; if a market (e.g. a factor or government-balance row) breaks the ∑ excess-demand·price ≡ 0 identity, the redefinition is incomplete.

### Assumption
Walras' law (∑ excess-demand·price ≡ 0) holds across camcge's full market structure at the MCP solution, so the dropped market's dual is *exactly* recoverable from the others' duals — the redefinition is complete, not approximate.

### Research Questions
1. Does Walras' law hold identically across all of camcge's markets (goods, factors, government balance) at the NLP/MCP solution?
2. Is the dropped market's dual a clean linear combination of the retained duals (exact recovery)?
3. Are there any income-balance / closure rows that break the naive Walras identity?

### How to Verify
Verify the Walras identity numerically at camcge's NLP optimum; confirm the dropped dual is exactly recoverable:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camcge.gms
# Expect: Walras identity holds at the optimum; dropped market dual = linear combo of retained duals (exact)
```

### Risk if Wrong
- **Identity breaks:** the redefinition is approximate → residual dual error → MS-4 persists; re-scope the recovery formula.

### Estimated Research Time
1.5 hours (Task 5 — the Walras-identity numerical verification at the optimum)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: #1385 sarf — Symbolic Runtime-Guard Cross-Term Emit

## Unknown 4.1: Does the 2-D extension + parametric `stat_task` emit materialize the banked derivation with no set-name-literal indices?

### Priority
**High** — this is a *failed-architecture rebuild* (the Sprint-26 `nu_slack("srn")` set-name-literal bug). If the parametric emit re-introduces the set-name-literal multiplier index, it repeats the Sprint-26 failure.

### Assumption
Extending `_is_blowup_dynamic_subset_equation` from srpchase's 1-D to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`, `equipb1`/`equipb2`), plus a new parametric `stat_task` cross-term emit that differentiates each short-circuited body **once parametrically in `(g,t,m,n)`**, materializes the banked 6-guarded-term `stat_task` derivation with **no set-name-literal multiplier indices** (the multiplier is emitted as `nu_tbal(g,t)`, not `nu_tbal("srn")`).

### Research Questions
1. Does the 2-D `_is_blowup_dynamic_subset_equation` gate fire on sarf's `tbal(g,t)$taskposs` shape (and only there)?
2. Does the parametric differentiation emit the multiplier index symbolically in `(g,t,m,n)`, avoiding the Sprint-26 set-name-literal bug?
3. Does the re-emitted `stat_task` match the banked 6-guarded-term hand-derivation?

### How to Verify
Extend the gate to 2-D; emit `sarf_mcp.gms`; compare the `stat_task` row to the banked derivation:
```bash
grep -rn "_is_blowup_dynamic_subset_equation" src/ad/index_mapping.py
# Emit sarf and confirm the stat_task multiplier is nu_tbal(g,t), not a set-name literal
# Expect: 2-D gate fires on sarf only; stat_task matches the banked 6-guarded-term derivation, symbolic indices
```

### Risk if Wrong
- **Set-name-literal recurs:** the Sprint-26 failure repeats → re-scope the parametric emit; +Translate at risk.

### Estimated Research Time
2 hours (Task 9 — the 2-D gate extension surface + the parametric `stat_task` builder site re-confirmation)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Is the symbolic re-emit O(constraints), not O(instances), staying inside the translate budget?

### Priority
**High** — sarf has 1,152 Cartesian instances; the whole point of Option-1's short-circuit was to avoid enumerating them. If the parametric re-emit re-enumerates, it re-triggers the translate timeout.

### Assumption
The symbolic runtime-guard re-emit differentiates each short-circuited body **once per constraint** (O(constraints)), NOT once per instance (O(instances) = sarf's 1,152), so `sarf_mcp.gms` translates well inside the budget rather than re-triggering the Option-1 timeout.

### Research Questions
1. Does the parametric emit produce one `stat_task` row per constraint (O(constraints)), or does it expand per instance?
2. Does `sarf_mcp.gms` translate inside the budget (vs the >180s timeout Option-1 short-circuited)?
3. Is the emit time dominated by the parametric differentiation (bounded) or the instance enumeration (blows up)?

### How to Verify
Time the sarf emit; confirm O(constraints) row count + sub-timeout translate:
```bash
time .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms --emit-mcp -o /tmp/sarf_mcp.gms 2>&1 | tail
grep -c "^stat_task" /tmp/sarf_mcp.gms
# Expect: O(constraints) stat_task rows, translate well under the timeout budget
```

### Risk if Wrong
- **O(instances) re-emit:** the translate timeout re-triggers → re-scope the parametric emit; +Translate REPLANs.

### Estimated Research Time
1.5 hours (Tasks 8 + 9 — the emit-budget timing + the O(constraints) confirmation)

### Owner
Development team (AD/performance specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Do the re-emit and cross-terms land atomically (no inconsistent-MCP intermediate)?

### Priority
**Medium** — a runtime-guarded equation-body re-emit *without* the matching `J_gᵀ·lam` cross-terms is an inconsistent MCP (the Sprint-26 architecture flaw); the two must land together, but this is a sequencing constraint, not an unknown fix surface.

### Assumption
The runtime-guarded equation-body re-emit and the parametric `J_gᵀ·lam` cross-terms are emitted **atomically** in the same code path, so there is no intermediate state where the equation is re-emitted but the stationarity cross-terms are missing (which would be an inconsistent MCP).

### Research Questions
1. Are the equation-body re-emit and the `stat_task` cross-terms in the same emit pass, or separable?
2. Does a partial land (re-emit without cross-terms) produce a detectably-inconsistent MCP (a gate can catch it)?
3. Is the atomicity enforceable structurally (one builder call), or by discipline?

### How to Verify
Confirm the re-emit + cross-term emit are one code path; check a partial-land would fail the golden/consistency gate:
```bash
grep -n "stat_task\|runtime.guard\|re-emit" src/kkt/stationarity.py | head
# Expect: re-emit + cross-terms in one builder path; partial land is structurally prevented
```

### Risk if Wrong
- **Separable:** a partial land ships an inconsistent MCP → +2–4h to enforce atomicity.

### Estimated Research Time
1 hour (Task 9 — the atomicity confirmation in the emit path)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: Cold-Convex Obj-Grad Residue (hhfair `stat_u` / CGE `stat_xp`)

## Unknown 5.1: Does the ν_objective reduction (NOT the sign flip) reach the NLP optimum on hhfair?

### Priority
**Critical** — the obvious sign-flip fix was **control-refuted three times** (hhfair Days 4/6, himmel16 Day 7; flipping made hhfair 72→22 *worse*). The ν_objective reduction is the correct-treatment hypothesis; it MUST pass a control experiment before any high-blast-radius objective-gradient `src/` change (PR24/PR27).

### Assumption
The objective-gradient reduction **through the objective-defining-equation multiplier (ν_objective)** — NOT the refuted sign flip — reaches the NLP optimum on hhfair (the cleanest instance, `stat_u` rel 2.0), because hhfair's `u` appears only in the objective *defining equation* (`obj =e= prod(x**a)`) and the correct stationarity reduces the obj-grad through that equation's multiplier rather than inlining it with a flipped sign.

### Research Questions
1. Does substituting the ν_objective reduction (obj-grad reduced through the defining-equation multiplier) drive hhfair's `stat_u` residual → 0 at the NLP optimum in a control experiment?
2. Is the sign flip conclusively excluded (it made hhfair 72→22 worse — re-confirm on the current tree)?
3. Is hhfair genuinely Case-b (localizable `stat_u` row) after the reduction, or Case-c (inherent non-convexity → Sprint 32)?

### How to Verify
Control experiment: patch hhfair's cold `stat_u` with the ν_objective reduction; solve; confirm the NLP optimum (NOT the sign flip):
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/hhfair.gms
# Expect: ν_objective reduction → hhfair cold-matches the NLP optimum (Case-b, emit-fixable) → PROCEED
#         still off / worse → Case-c inherent non-convexity → documented finding, no src change (REPLAN)
```

### Risk if Wrong
- **Case-c:** the family is inherent non-convexity → documented finding, no `src/` change; hhfair + CGE cluster genuine-floor gains REPLAN (the genuine-floor ramp loses contributors, Task 7).

### Estimated Research Time
2.5 hours (Tasks 6 + 9 — the ν_objective reduction control experiment on hhfair)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Does the same reduction convert the CGE cluster (irscge/lrgcge/moncge `stat_xp`) to Case-a?

### Priority
**High** — the payoff multiplier: if the hhfair reduction generalizes to the CGE `stat_xp` cluster (rel ~0.06 after the Day-5 case-normalization fix), one fix converts several genuine-floor matches.

### Assumption
The objective-defining-intermediate-variable reduction that fixes hhfair (Unknown 5.1) is the **same class** as the CGE cluster's residual (irscge/lrgcge/moncge `stat_xp` rel ~0.06), so the same ν_objective reduction converts the cluster to Case-a (residual → 0) — a shared genuine-floor payoff.

### Research Questions
1. Is the CGE `stat_xp` residual the same objective-defining-intermediate-variable shape as hhfair's `stat_u`?
2. Does the ν_objective reduction drive the CGE `stat_xp` residuals → 0 (Case-a), or is the CGE shape distinct?
3. Is the ~0.06 residual a genuine-floor blocker (converts a methodology match to genuine), or already a genuine match?

### How to Verify
Apply the reduction to the CGE cluster; confirm `stat_xp` → 0 (Case-a):
```bash
for m in irscge lrgcge moncge; do echo "== $m =="; \
  .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms; done
# Expect: the reduction drives stat_xp → 0 (Case-a) across the cluster → shared genuine-floor payoff
#         the CGE shape is distinct → the reduction is hhfair-only, CGE cluster re-scopes
```

### Risk if Wrong
- **CGE shape distinct:** the reduction is hhfair-only → the CGE cluster genuine-floor gains REPLAN; -N genuine floor.

### Estimated Research Time
1.5 hours (Task 9 — the CGE-cluster same-class check + the reduction generalization)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Is the objective-defining-intermediate-variable shape a single reduction rule or per-model?

### Priority
**High** — determines whether P5 ships one general rule (converting the whole hhfair + CGE genuine-floor cohort) or a per-model patch (hhfair only); the genuine-floor ramp (≥73) depends on which.

### Assumption
The objective-defining-intermediate-variable reduction (obj-grad reduced through the defining-equation multiplier) is a **single general rule** applicable wherever a variable appears only in the objective-defining equation and is also market-cleared — not a per-model hand patch.

### Research Questions
1. Is the shape detectable structurally (a variable in the objective-defining equation + a market-clearing constraint)?
2. Does the general rule apply without a per-model coefficient, or does each model need tuning?
3. How many corpus models have this shape (the coverage set)?

### How to Verify
Enumerate the objective-defining-intermediate-variable shape across the corpus; confirm the rule is structural:
```bash
# Count models with a variable appearing only in the objective-defining equation + a market-clearing constraint
grep -rln "=e=.*prod\|=e=.*sum.*log" data/gamslib/raw/ | head
# Expect: a structural rule covers hhfair + the CGE cluster + any same-shape model
```

### Risk if Wrong
- **Per-model:** P5 ships a narrower patch → lower coverage; hhfair still lands.

### Estimated Research Time
1 hour (Task 9 — the shape enumeration + the rule-vs-patch determination)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.4: Does the reduction interact with the landed Day-5 case-normalization fix?

### Priority
**Low** — the CGE `stat_xp` rel ~0.06 is measured *after* the Sprint-30 Day-5 case-normalization fix landed; the reduction must compose with it, but both are in the emit path and a conflict is unlikely and cheaply resolved.

### Assumption
The ν_objective reduction composes cleanly with the landed Sprint-30 Day-5 presolve dual-transfer case-normalization fix (mixed-case equation duals no longer silently skipped) — the two touch different stationarity mechanisms and do not conflict.

### Research Questions
1. Does the case-normalization fix affect the `stat_xp`/`stat_u` rows the reduction targets?
2. Is the ~0.06 residual a *remainder* after case-normalization (so the reduction closes it), or a separate mechanism?

### How to Verify
Confirm the reduction operates on top of the case-normalized duals (no double-handling):
```bash
grep -n "eq_by_lower\|ineq_by_lower\|case.normal" src/emit/emit_gams.py | head
# Expect: the reduction and the case-normalization fix are orthogonal; the ~0.06 residual is the reduction's target
```

### Risk if Wrong
- **Conflict:** minor double-handling → +1–2h to sequence the two.

### Estimated Research Time
0.5 hours (Task 9 — the case-normalization composition check)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: rocket #1462 — Non-Convex Forcing → PATH-Consultation Input

## Unknown 6.1: Do any remaining emittable-GAMS levers cross rocket's INFES, or is it confirmed intrinsic?

### Priority
**High** — determines whether rocket is a conditional +1 Solve this sprint (an emittable lever converges it) or a Sprint-32 PATH-consultation hand-off (intrinsic non-convergence).

### Assumption
The remaining emittable-GAMS levers — reformulating the `1/ht²`,`1/m²` division-by-variable Jacobian; scaled/relaxed continuation schedules — either cross rocket's INFES (477 → 382 best, never converges) or exhaust the emittable space, confirming the residual is intrinsic and the fix is a PATH solver option (the Sprint-32 consultation hand-off).

### Research Questions
1. Does reformulating the `1/ht²`,`1/m²` division-by-variable Jacobian improve convergence (INFES crosses)?
2. Do scaled/relaxed continuation schedules (via the `--force` scaffold) move rocket toward MS 1/2?
3. If no emittable lever converges, is the PATH-consultation question the correct hand-off (Sprint 32)?

### How to Verify
Apply each remaining lever via the `--force` scaffold; record per-lever effect on rocket's MS + INFES:
```bash
grep -n "force\|homotopy\|multistart\|optfile" src/emit/forcing.py src/config.py | head
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms
# Expect: a lever converges rocket → +1 Solve; else → the emittable space is exhausted → PATH-consultation input
```

### Risk if Wrong
- **No lever + no clean hand-off:** rocket neither solves nor produces a usable PATH question → the Sprint-32 consultation lacks a concrete input.

### Estimated Research Time
2 hours (Tasks 8 + 9 — the remaining-lever exhaustion via the `--force` scaffold)

### Owner
Development team (solver/forcing specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Is the emit residual clean at the NLP point (Case-c) before any forcing attempt?

### Priority
**Medium** — the scope guard that keeps rocket a *forcing* problem, not an emit bug. If the emit residual is NOT clean at the NLP point, rocket has a latent emit defect that forcing would mask.

### Assumption
rocket's emitted MCP residual is clean (Case-c) at the NLP point — the emit is correct and the failure is purely non-convex convergence — so any forcing attempt targets convergence, not a hidden emit bug (the PR27 residual-clean-before-forcing rule).

### Research Questions
1. Does `kkt_residual.py` report Case-c (clean emit, non-convex) at rocket's NLP point?
2. Is there any residual `stat_*` row that would indicate a latent emit defect (Case-b)?

### How to Verify
Run the harness at rocket's NLP point; confirm Case-c (clean emit):
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms
# Expect: CASE_C (clean emit at the NLP point, non-convex convergence) → forcing is the right lever
#         CASE_B residual → a latent emit bug to fix first (not a forcing problem)
```

### Risk if Wrong
- **Case-b:** rocket has a latent emit bug → forcing would mask it; re-diagnose the emit first.

### Estimated Research Time
1 hour (Task 6 — the residual-clean-at-NLP-point gate before forcing)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Does the `1/ht²`,`1/m²` division-by-variable Jacobian reformulation help, or is it PATH-side?

### Priority
**Low** — one specific lever within Unknown 6.1; its outcome refines the PATH-consultation question but does not change the sprint's rocket disposition (conditional +1 or hand-off).

### Assumption
The `1/ht²`,`1/m²` division-by-variable terms produce a Jacobian that PATH struggles with; a reformulation (introducing auxiliary variables `w=1/ht²` with defining constraints) either eases convergence or is confirmed to be a PATH-side numerical issue that only a solver option addresses.

### Research Questions
1. Does an auxiliary-variable reformulation of the `1/ht²`,`1/m²` terms change the emitted Jacobian's conditioning?
2. Does the reformulation help PATH converge, or is the difficulty intrinsic to the problem (PATH-side)?
3. Does the reformulation belong in the PATH-consultation question (as a candidate the author can rule in/out)?

### How to Verify
Prototype the auxiliary-variable reformulation on rocket; compare convergence; record for the PATH question:
```bash
grep -in "ht\|1/m\|division" data/gamslib/raw/rocket.gms | head
# Expect: reformulation eases convergence → a lever; else → a documented PATH-side candidate for the consultation
```

### Risk if Wrong
- **Neither:** the reformulation is inconclusive → recorded as an open PATH-consultation candidate (no sprint impact).

### Estimated Research Time
1 hour (Task 9 — the Jacobian-reformulation probe for the PATH-consultation input)

### Owner
Development team (solver specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Infrastructure — Property-Test Catalog Completion + Genuine-Floor Tracking

## Unknown 7.1: Does enabling `shape8` become the P2 gate, and does the new head-offset fixture guard P1?

### Priority
**Medium** — the property fixtures are the P1/P2 completion guards; if `shape8` can't be enabled once the coupled fix lands, or the head-offset fixture can't be authored from the IR-plumbing design, the P1/P2 regression guards are missing.

### Assumption
`shape8_offset_alias_successor` (currently strict-xfail) becomes the P2 completion gate the moment the coupled distance-Jacobian second-index fix lands (its assertion already passes with the objective half applied), and a **new head-domain-offset fixture** (authored from Task 3's round-trip spec) guards the P1 index-map once the IR plumbing lands.

### Research Questions
1. Does `shape8_offset_alias_successor` pass once the coupled P2 fix lands (drop the `strict=True` xfail)?
2. Can a head-domain-offset fixture be authored from the Task-3 round-trip spec (mine-shaped, committed under `tests/fixtures/crossterm_shapes/`)?
3. Do the two fixtures cover the P1 index-map + the P2 second-index cross-term as regression guards?

### How to Verify
Confirm `shape8`'s assertion + scope the head-offset fixture:
```bash
grep -n "shape8_offset_alias_successor\|shape9_objgrad_subset_boundary\|strict=True" tests/integration/emit/test_ad_crossterm_shapes.py
# Expect: shape8 enable is the P2 gate; a new head-offset fixture (from Task 3) guards the P1 index-map
```

### Risk if Wrong
- **Fixture gaps:** P1/P2 land without regression guards → +2–4h to author the fixtures post-hoc.

### Estimated Research Time
1 hour (Task 8 — the property-fixture readiness scope for P1/P2)

### Owner
Development team (test/AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Does the PR25 genuine-floor tracking recompute correctly against the S31–S33 re-baselined Match KPIs?

### Priority
**Medium** — the genuine-floor is the honest headline (the Sprint-30 lesson: Match 92 sits above a genuine floor of 70). The S31 ≥73 ramp must be measured against the re-baselined ≥64% Match line (footnote ⁸), or the KPI is un-auditable.

### Assumption
The PR25 genuine-vs-methodology partition recomputes cleanly at Day 0 (reproducing the genuine floor 70) and tracks the S31 ≥73 ramp against the re-baselined S31–S33 Match KPIs (footnote ⁸), so each Sprint-31 genuine-floor gain (polygon P2, hhfair/CGE P5, robert-class) is attributable to a specific methodology→genuine conversion.

### Research Questions
1. Does the genuine-vs-methodology partition reproduce the genuine floor 70 at Day 0?
2. Does the footnote-⁸ ramp (S31 ≥73) align with the re-baselined ≥64% Match line?
3. Are the Sprint-31 genuine-floor contributors (polygon, hhfair/CGE) each a traceable methodology→genuine conversion?

### How to Verify
Recompute the partition from the Sprint-30-final DB; confirm the floor + the ramp:
```bash
python -c "import json; d=json.load(open('data/gamslib/gamslib_status.json')); \
print('solved', sum(1 for v in d.values() if v.get('solve_status')=='solved'))"
# Expect: genuine floor 70 reproduced at Day 0; the S31 ≥73 ramp aligns with the re-baselined Match line
```

### Risk if Wrong
- **Partition drift:** the genuine floor is mis-measured → the ≥73 target is un-auditable; +2h to reconcile.

### Estimated Research Time
1 hour (Task 2 — the genuine-floor partition recompute + the ramp alignment)

### Owner
Development team (metrics/planning)

### Verification Results
✅ **Status:** VERIFIED — genuine floor 70 reproduced from first principles; footnote-⁸ ramp aligns
**Verified by:** Task 2 (Day-0 Baseline + Genuine-Floor Re-Baseline)
**Date:** 2026-07-08
**Findings:** The canonical-scope recompute from the committed DB (`get_candidate_models`, 142 models) reproduces the **Sprint 30 final headline exactly** — Parse 142 · Translate 135 · **Solve 107** (63 `model_optimal` + 44 `model_optimal_presolve`) · **Match 92** · Mismatch 9 · model_infeasible 7 · path_syntax_error 8 · path_solve_terminated 4 · path_solve_license 9 · Tests 4,997. The PR25 genuine-vs-methodology partition reproduces the **genuine floor 70** (Sprint-28 genuine 68 **+1** S29 maxmin/catmix **+1** S30 robert cold obj-grad) with **methodology 22** (the Sprint-30 set minus robert, now genuine). The footnote-⁸ ramp aligns: **S30 actual 70 → S31 ≥ 73 → S32 ≥ 73 → S33 ≥ 75 → S34 ≥ 78** on the re-baselined ≥ 64% as-measured Match line. The genuine-floor → ≥ 73 conversion map (polygon P2 +1, hhfair P5 +1, CGE cluster irscge/lrgcge/moncge P5 +1–3, mine P1 +0–1) has nominal headroom, but the Sprint-30 retrospective (§3 lesson 3) binds it as **conditional** on the #1111/#1112 core + the dual-consistent CGE + the obj-grad reduction — NOT independent +1s. himmel16 is documented non-convex (not a converter).
**Evidence:** `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` §1–§2 (recompute + partition); the DB is byte-unchanged since the Sprint 28 close (`2717d542`) because both S29 and S30 netted no as-measured bucket change.
**Decision:** Day-0 = Sprint 30 final (Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7 / Translate 135 / Tests 4,997), reused unchanged (no `src/`/`scripts/` drift since the S30 close `ea4191dc`; no fresh retest). The genuine-floor ramp is measured against this floor-70 anchor, conditionally per the Task-7 REPLAN assessment.

**Day-0-bucket aspect of 1.3 / 2.1 / 3.1 / 5.1 / 6.1 (Task 2 contribution; their fix-surface aspect is verified by Tasks 3/4/5/9):** the per-Sprint-31-target Day-0 buckets are pinned (BASELINE_METRICS.md §3) — **mine** `model_infeasible` (16747.072, P1, 1.3), **polygon** `model_optimal_presolve`+match (0.7797, P2, 2.1), **camcge** `model_infeasible` (0.0, P3, 3.1), **hhfair** `model_optimal`+**mismatch** (72.147, P5, 5.1), **rocket** `model_infeasible` (1.137, P6, 6.1) — each still in the bucket its Sprint-31 track targets.

---

## Unknown 7.3: Do the `--resolve-changed` checkpoint targets cover the newly-touched emit sites?

### Priority
**Low** — the checkpoint re-solve is the mid-sprint safety net; if it doesn't select the newly-touched emit sites (the head-offset core, `_add_indexed_jacobian_terms`, the Walras redefinition, the sarf symbolic emit), a regression could slip past the Day-5/Day-10 checkpoints — but the final full retest still catches it.

### Assumption
The `--resolve-changed --since-commit <SHA>` checkpoint re-solve correctly selects every model whose golden changes when the Sprint-31 emit sites are touched (the head-offset core, `_add_indexed_jacobian_terms`, the Walras redefinition, the sarf symbolic emit), so the Day-5/Day-10 checkpoints re-solve exactly the affected models.

### Research Questions
1. Does `changed_emit_artifacts.py` detect a diff for each newly-touched emit site?
2. Does `--resolve-changed` select the head-offset / offset-alias / Walras / sarf models when their emit changes?
3. Are there any emit sites the changed-artifact diff misses?

### How to Verify
Confirm the changed-artifact diff + `--resolve-changed` cover the Sprint-31 emit sites:
```bash
test -f scripts/sprint_audit/changed_emit_artifacts.py && echo "changed-artifact diff present"
grep -rn "resolve.changed\|since.commit" scripts/gamslib/run_full_test.py | head
# Expect: the diff + --resolve-changed select mine/polygon/camcge/sarf when their emit changes
```

### Risk if Wrong
- **Missed sites:** a regression slips past a checkpoint → caught only at the final retest; +re-solve cost.

### Estimated Research Time
0.5 hours (Task 8 — the checkpoint-coverage confirmation for the Sprint-31 emit sites)

### Owner
Development team (tooling specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Template for New Unknowns

```markdown
## Unknown X.Y: [Title / Question]

### Priority
**[Critical/High/Medium/Low]** - [Brief reason]

### Assumption
[The assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, experiments, or analysis to validate the assumption]

### Risk if Wrong
[Impact on the sprint if the assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

> **PREP PHASE IN PROGRESS (Task 1 COMPLETE, 2026-07-08).** This Known Unknowns List (Task 1) is authored; the remaining prep Tasks 2–10 will research and verify each unknown before Sprint 31 Day 1. All **25** prep-time unknowns start 🔍 INCOMPLETE and are assigned to a downstream prep task (2–10) in the §"Appendix: Task-to-Unknown Mapping". The six Critical unknowns — the foundational IR-plumbing round-trip (1.1), the shared-helper-vs-4th-site sizing (1.2), the coupled offset-alias core (2.2), the dual-consistent Walras redefinition (3.1) + its false-positive detector (3.2), and the control-refuted obj-grad reduction (5.1) — are the ones whose WRONG outcome forces a mid-sprint REPLAN, so they carry a single-model or control-experiment verification and feed the Task-7 REPLAN assessment.

**Prep-phase checklist (to complete before Sprint 31 Day 1 — Tasks 1–10):**
1. ✅ Task 1: this Known Unknowns List authored (25 unknowns, 7 categories).
2. 🔵 Research and verify all Critical and High priority unknowns (16 total: 6 Critical + 10 High) via prep Tasks 2–10.
3. 🔵 Create minimal test cases / run the `kkt_residual.py` trace + the cold-solve control experiments.
4. 🔵 Update each "Verification Results" section (🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG with correction).
5. 🔵 Adjust Sprint 31 scope for any WRONG-returning assumption (the PR16 REPLAN exits in Task 7).
6. 🔵 Integrate findings into the sprint plan (Task 10 — `PLAN.md` + `prompts/PLAN_PROMPTS.md`).

**During Sprint 31:**
1. Reference this document daily (especially Critical / High unknowns).
2. Add newly discovered unknowns using the template above.
3. Update verification results as features are implemented.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 31 prep tasks verify which unknowns. Prep Task 10 (Plan Sprint 31 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Sprint 30 → 31 Day-0 Baseline + Genuine-Floor Re-Baseline | 7.2 | Reproduces the genuine floor 70 at Day 0 + the footnote-⁸ S31 ≥73 ramp alignment (7.2); the per-target "still in its bucket at Day 0?" check contributes to 1.3 / 2.1 / 3.1 / 5.1 / 6.1 |
| Task 3: Head-Offset IR-Plumbing Design + Round-Trip Reproduction | 1.1, 1.2, 1.3, 1.4 | Designs the `EquationDef` head-offset storage + the normalize round-trip + the round-trip fixture (1.1); the shared 3-site helper vs 4th-site sizing (1.2); the cold-LCP-consistency check (1.3); the IR blast-radius scan (1.4) |
| Task 4: Offset-Alias Recipe Re-Confirmation + Distance-Jacobian Design | 2.1, 2.2, 2.3, 2.4 | Re-confirms the 4-term recipe on the current tree (2.1); designs the coupled second-index restoration + the #1110 orthogonality (2.2); the tight-gate-vs-full-core decision (2.3); the himmel16 non-convex scope guard (2.4) |
| Task 5: camcge Dual-Consistent Walras Transform Design | 3.1, 3.2, 3.3, 3.4 | Designs the dual-consistent multiplier redefinition to MS 1 / omega 191.735 (3.1); the S1∧S2∧S3 detector + false-positive guard (3.2); the redundant-row + numéraire selection rule (3.3); the Walras-identity verification (3.4) |
| Task 6: Refresh + Author Phase 0 Acceptance Gates | 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 | Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27): the head-offset shared-helper gate (1.2), the coupled offset-alias gate (2.2), the dual-consistent-prototype-first gate (3.1), the sarf O(constraints) gate (4.1), the ν_objective control-before-implement gate (5.1, sign flip banned), the rocket residual-clean-before-forcing gate (6.2) |
| Task 7: Diagnosis-Heavy / REPLAN-Prone Risk Assessment (PR16) | 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 | The four deepest REPLAN-prone tracks — mine foundational IR plumbing (1.1, 1.2), offset-alias general-alias core (2.2, 2.3), sarf symbolic-emit timeout (4.2), cold-convex obj-grad Case-c (5.1, 5.2) — each get a PROCEED/REPLAN signal + Sprint-32 exit + budget reallocation |
| Task 8: Reusable-Tooling Readiness Audit | 4.2, 6.1, 7.1, 7.3 | The sarf emit-budget timing (4.2), the `--force` scaffold's rocket-lever entry (6.1), the `shape8` + head-offset property-fixture readiness (7.1), and the `--resolve-changed` checkpoint coverage (7.3) |
| Task 9: Backlog Fix-Surface Analysis | 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3 | The sarf 2-D gate + parametric `stat_task` builder + atomicity (4.1, 4.3), the ν_objective reduction control experiment + CGE-cluster generalization + rule-vs-patch + case-normalization composition (5.1, 5.2, 5.3, 5.4), and the rocket lever exhaustion + Jacobian-reformulation PATH input (6.1, 6.3) |
| Task 10: Plan Sprint 31 Detailed Schedule | (integrates all) | Sprint 31 14-day schedule + day-by-day prompts; absorbs the PROCEED/REPLAN decisions from Tasks 6/7, the IR-plumbing design from Task 3, the offset-alias + Walras designs from Tasks 4/5, and the fix-surface + tooling readiness from Tasks 8/9; front-loads the Day-0 tractability probes (1.1, 3.1, 5.1) |

**Cross-cutting unknowns** (verified across multiple prep tasks):

- **Unknown 1.1 / 1.2** (head-offset IR plumbing + shared helper) — Task 3 designs the IR plumbing + the round-trip reproduction, Task 6 gates the shared-helper fix-surface, and Task 7 makes the PROCEED/REPLAN call (mine solves vs a 4th-site Sprint-32 slip).
- **Unknown 2.2 / 2.3** (offset-alias coupled core) — Task 4 designs the second-index restoration + the tight gate, Task 6 gates it, and Task 7 makes the localized-vs-#1111/#1112-core decision.
- **Unknown 3.1 / 3.2** (dual-consistent Walras + detector) — Task 5 designs both, Task 6 gates the prototype-on-`/tmp`-first rule, and the false-positive guard protects the whole CGE cohort.
- **Unknown 5.1 / 5.2** (obj-grad ν_objective reduction) — Task 9 runs the control experiment (hhfair) + the CGE-cluster generalization, Task 6 gates it (sign flip banned), and Task 7 makes the Case-b-vs-Case-c decision.
- **Unknown 6.1** (rocket forcing lever) — Task 8 confirms the `--force` scaffold entry, Task 9 exhausts the levers, and Task 6 gates the residual-clean-before-forcing rule.
- **Unknown 7.2** (genuine-floor baseline) — Task 2 establishes it, and every Sprint-31 genuine-floor target delta is measured against it.

**Coverage:** All 25 Sprint 31 prep-time unknowns are assigned to at least one prep task. Each Critical and High-priority unknown is assigned to the task that will act on its findings (e.g., Task 7 verifies the diagnosis-heavy Category 1/2/4/5 deep tracks AND its findings drive Task 10's schedule allocation + the Sprint 32 REPLAN exits).

**Carryforward from Sprint 30** (now informing Sprint 31 prep):
- All 25 Sprint 30 prep unknowns were VERIFIED or documented WRONG-with-correction (see `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §"Next Steps"). Several became the parents of Sprint-31 categories: Sprint-30 Unknown 1.1 (robert does NOT generalize to mine → mine standalone REPLAN → Category 1), Unknown 1.2 (mine 3-site fix needs the IR change first → Category 1), Unknown 5.1/5.2 (offset-alias Day-5 revert coupling = #1111/#1112 core → Category 2), Unknown 6.1/6.2 (camcge Walras breaks the dual → Category 3), Unknown 2.2 (rocket intrinsic non-convergence → Category 6). The Sprint 31 unknowns are net-new, derived from the six carryforward priorities + the infrastructure track.

---

**Document Created:** 2026-07-08
**Last Updated:** 2026-07-08
**Total Unknowns:** 25
**Owner:** Sprint 31 Planning Team
**Review Frequency:** Daily during Sprint 31
