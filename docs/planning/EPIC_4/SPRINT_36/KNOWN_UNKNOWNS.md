# Sprint 36 Known Unknowns

**Created:** 2026-08-06
**Status:** Active — Pre-Sprint 36
**Purpose:** Proactive documentation of the assumptions and unknowns for Sprint 36 (the Sprint-35 carryforward sprint) **before** implementation begins — so each deep track (markov P1 `σ=sp`, fawley P3 discriminator, ganges P4 `$66`/`rPower`) and each banked diagnosis is verified or designed in the prep phase, not discovered on Day 3.

---

## Executive Summary

This document identifies every open question, assumption, and risk across the seven Sprint-36 priorities defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 36, Weeks 37–38). Sprint 35 closed **modal-flat** (Solve 108 / Match 93 / genuine floor 75 — the third consecutive), so each carryforward inherits a **control-confirmed, banked diagnosis** rather than a raw problem. Sprint 36's unknowns are therefore the *residual* questions those carryforwards leave open — e.g. "does the markov Part-1 diagonal split still reduce the residual on current `main`?", "can the `σ=sp` off-diagonal be represented in the offset machinery?", "does the fawley discriminator collide with the markov change in the shared `_add_indexed_jacobian_terms`?".

**Sprint 36 Scope (per `PROJECT_PLAN.md`):**
1. **P1 markov** — `stat_z` diagonal-Kronecker +1-floor lever (methodology→genuine; Part-1 verified, Part-2 `σ=sp` the deep unknown)
2. **P2 sarf** (#1385) — symbolic-emit subsystem (O(active=398), not O(369K))
3. **P3 fawley** (#1111/#1112) — constraint-index-diagonal correction (derivative-structure discriminator) + `--force` survey
4. **P4 ganges/gangesx** — ≥5-blocker cascade recovery
5. **P5 rocket/mine** consultation trio + **camcge** Walras (Epic 5)
6. **P6 turkey** testbed re-solve + residual multi-root cohort
7. **P7 (infrastructure)** — GAMS-54 corpus re-baseline + robustlp NA fix + property fixtures + genuine-floor tracking

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 36 section) · `docs/planning/EPIC_4/SPRINT_36/PREP_PLAN.md` (the 10 prep tasks that verify these unknowns) · `docs/planning/EPIC_4/SPRINT_35/SPRINT_36_CARRYFORWARDS.md` (the banked diagnoses). *(No `PRELIMINARY_PLAN.md` exists for Sprint 36; the `PREP_PLAN.md` + the carryforward doc are the planning sources.)*

**Lessons from Previous Sprints:** the control-first REPLAN discipline (PR24/PR27) held for the fifth+ consecutive sprint — every deep track was refuted or banked on control evidence *before* any bad ship. The recurring hazard is the shared high-blast-radius `_add_indexed_jacobian_terms` (the fawley Day-9 change leaked onto markov). "Prep-doc `file:line` fix-surfaces are HYPOTHESES — verify before implementing" (wrong ~4× in S27).

**Deferred-unknown lineage:** these unknowns descend from Sprint-35 dispositions — the markov lever is the Day-11 discovery (S35 Follow-up 3, resolved to a `CASE_B` bug); fawley's constraint-index-diagonal is the S35 Day-9 DEFER (its S35 Unknown re: the leak onto markov #1110); ganges/gangesx is the S35 Day-3 BANK (the ≥5-blocker cascade); the GAMS-54 re-baseline is `FOLLOWUPS_GAMS54_TRANSITION.md` Follow-up 2; the robustlp NA fix is Follow-up 1; the markov `slow`-test disposition is Follow-up 3. camcge/rocket/mine carry forward from Sprints 32–35 (camcge → Epic 5).

---

## How to Use This Document

### Before Sprint 36 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (20 total)
2. Create minimal test cases / `/tmp` controls for validation (markov + fawley controls are seconds-scale and local)
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 36
1. Review daily during standup
2. Add newly discovered unknowns (use the Template below)
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption breaks the fix or forces a mid-sprint REPLAN (>8 hours rework)
- **High:** Wrong assumption causes significant rework (4–8 hours)
- **Medium:** Wrong assumption causes minor issues (2–4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 30

**By Priority:**
- Critical: 8 (27% — could derail a track or force a mid-sprint REPLAN; the markov lever + the ganges cascade + the shared-function collision + the testbed dependency)
- High: 12 (40% — require upfront research/design before Day 1)
- Medium: 7 (23% — resolvable during implementation)
- Low: 3 (10% — nice-to-know, low impact)

**By Category:**
- Category 1 (markov — Diagonal-Kronecker +1-Floor Lever): 5 unknowns
- Category 2 (sarf #1385 — Symbolic-Emit Subsystem): 4 unknowns
- Category 3 (fawley #1111/#1112 — Constraint-Index-Diagonal): 4 unknowns
- Category 4 (ganges/gangesx Multi-Root Recovery): 5 unknowns
- Category 5 (rocket/mine Consultation Trio + camcge Walras): 4 unknowns
- Category 6 (turkey Testbed Re-Solve + Residual Cohort): 3 unknowns
- Category 7 (Infrastructure — GAMS-54 Re-Baseline + robustlp NA + Fixtures + Floor Tracking): 5 unknowns

**Estimated Research Time:** ~35 hours (within the 28–36 hour target; spread across prep Tasks 2–9)

---

## Table of Contents

1. [Category 1: markov — Diagonal-Kronecker +1-Floor Lever](#category-1-markov--diagonal-kronecker-1-floor-lever)
2. [Category 2: sarf #1385 — Symbolic-Emit Subsystem](#category-2-sarf-1385--symbolic-emit-subsystem)
3. [Category 3: fawley #1111/#1112 — Constraint-Index-Diagonal Correction](#category-3-fawley-11111112--constraint-index-diagonal-correction)
4. [Category 4: ganges/gangesx Multi-Root Recovery](#category-4-gangesgangesx-multi-root-recovery)
5. [Category 5: rocket/mine Consultation Trio + camcge Walras](#category-5-rocketmine-consultation-trio--camcge-walras)
6. [Category 6: turkey Testbed Re-Solve + Residual Multi-Root Cohort](#category-6-turkey-testbed-re-solve--residual-multi-root-cohort)
7. [Category 7: Infrastructure — GAMS-54 Corpus Re-Baseline + robustlp NA Fix + Property Fixtures + Genuine-Floor Tracking](#category-7-infrastructure--gams-54-corpus-re-baseline--robustlp-na-fix--property-fixtures--genuine-floor-tracking)

---

# Category 1: markov — Diagonal-Kronecker +1-Floor Lever

## Unknown 1.1: Does the markov Part-1 diagonal split still drive the residual 13.3 → 1.55 on current `main`?

### Priority
**Critical** — if the Part-1 result no longer reproduces, the entire markov lever premise (methodology→genuine) is in doubt, forcing a re-diagnosis (>8h).

### Assumption
The S35 Day-11 finding still holds on current `main`: markov's cold emit is `CASE_B` (`max|stat_z|` rel 13.3), and applying the Part-1 diagonal-Kronecker split reduces it to ≈ 1.55 (the remaining residual being the Part-2 `σ=sp` off-diagonal).

### Research Questions
1. Does `kkt_residual.py data/gamslib/raw/markov.gms` still report `CASE_B`, `max|stat_z|` rel ≈ 13.3 on `stat_z(empty,disrupted,*)` with dual transfer CONSISTENT?
2. Re-applying the documented Part-1 change (`DAY11_MARKOV_DIAGONAL_LEVER.md` §6) on a scratch branch, does the residual drop to ≈ 1.55?
3. Has `_add_indexed_jacobian_terms` drifted on `main` since the S35 close (`597d9d08`) in a way that affects the diagonal group `(0,0,999)`?
4. Is markov still classified `verified_convex` + `model_optimal_presolve` + `match` (methodology) in the committed DB?

### How to Verify
Run the markov control on current `main` (tiny model, seconds-scale, fully local); optionally re-apply the Part-1 change on a scratch branch, re-run the control, then revert. Confirm the DB fields via `gamslib_status.json`.

### Risk if Wrong
- **Premise collapse:** if Part-1 no longer reduces the residual, the markov +1-floor lever is unverified and P1 becomes a re-diagnosis, not a landing.
- **Silent `main` drift:** an unrelated `_add_indexed_jacobian_terms` change could have altered the diagonal group, invalidating the S35 design.

### Estimated Research Time
1 hour (re-run the control + optional scratch re-apply/revert)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-06

**Findings:** The markov control reproduces the S35 Day-11 fingerprint exactly — `CASE_B`, `max|stat_z|` rel 13.3 on `stat_z(empty,disrupted,empty)`, dual CONSISTENT (dual scale 3.6e3). markov remains `verified_convex` + `model_optimal_presolve` + match (**methodology**) in the byte-unchanged DB, so the methodology→genuine +1 is still available. The emit/AD code path is byte-identical to the Day-11 measurement tree, so the documented Part-1 diagonal split's 13.3→1.55 reduction reproduces on identical code + golden.

**Evidence:** `kkt_residual.py markov` → `verdict: CASE_B`, `max-residual stat_z(empty,disrupted,empty) rel 1.33e+01 (raw -4.79e+04)`. `git diff 78ceaead..HEAD -- src/kkt/stationarity.py src/ad/derivative_rules.py` = empty (both UNCHANGED); `git diff --name-only 78ceaead..HEAD -- data/gamslib/mcp/` = only `turkey_mcp.gms` (`markov_mcp.gms` unchanged). See `DAY0_TRACE_NOTES.md` §3.

**Decision:** ✅ The Part-1 premise holds (13.3 baseline reproduced; the 13.3→1.55 reduction reproduces deductively on byte-identical emit code + golden). No full scratch re-apply was needed — the emit path is provably identical (the only `src/` delta since S35 is the unrelated turkey `original_symbols.py`). Task 3 designs Part-2 (`σ=sp`).

---

## Unknown 1.2: Can the `σ=sp` off-diagonal enumeration be represented with a bounded offset-key mechanism?

### Priority
**Critical** — this is the deep unknown gating the markov +1; if `σ=sp` needs an architectural rewrite, P1 slips to a REPLAN (>8h).

### Assumption
The off-diagonal contribution `−b·Σ_τ pr(i,τ)·nu_constr(sp,τ)` (multiplier index `σ=sp`, the variable's *3rd, independent* index) can be emitted via a bounded extension of the offset/multi-pattern machinery (a new "bound-to-var-index" marker, or a `sameas`-guarded direct term) — not a from-scratch rewrite of `enumerate_variable_instances`.

### Research Questions
1. Why does `_compute_index_offset_key` produce `(offset-from-s, …, SENTINEL)` and fail to encode `σ=sp` (an independent var index, not an offset of `s`)?
2. Can a new offset-key marker map a multiplier position directly to a var position (analogous to the SENTINEL), and does the sub-group emission consume it correctly?
3. Alternatively, can the `σ=sp` slice be emitted as a `sameas`-guarded direct term (like the Part-1 diagonal), avoiding the 44 spurious groups?
4. Which candidate has the smallest blast radius on the shared `_add_indexed_jacobian_terms` (i.e. touches the fewest existing `sameas`/offset paths)?
5. Does a `/tmp` hand-edit of the emitted `stat_z` (the correct `σ=sp` form) drive `kkt_residual.py markov` → `CASE_A` (rel < tol)?

### How to Verify
Trace `_compute_index_offset_key` + the sub-group emission for markov's off-diagonal groups; sketch each candidate mechanism's emitted GAMS; run the `/tmp` hand-edit control to confirm the target form reaches `CASE_A` *before* choosing a `src/` mechanism.

### Risk if Wrong
- **Architectural depth:** if no bounded mechanism exists, P1 lands only Part 1 (no bucket) and banks Part 2 — the sprint's headline upside slips.
- **Wrong target form:** if the hand-edit doesn't reach `CASE_A`, the derived off-diagonal form is incomplete and the whole design must be re-derived.

### Estimated Research Time
4 hours (offset-key trace + candidate sketches + the `/tmp` `CASE_A` control)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED (a bounded mechanism is specified — a coordinated offset-key + emission change, not a trivial tweak)
**Verified by:** Task 3 (markov P1 — Part-2 `σ=sp` Off-Diagonal Enumeration Design)
**Date:** 2026-08-06

**Findings:** Root-caused precisely: `_compute_index_offset_key`'s greedy first-canonical-match (`stationarity.py:5099`) binds constr's `sp` index to var **position 0 (`s`, canon-only)** instead of **position 2 (`sp`, exact-name)** — because `s`/`sp`/`spp` are aliases (same canon). `σ=sp` is then expressed as an **offset-from-`s`**, degenerating into 44 spurious groups. A scratch prototype (exact-declared-name-first matching) confirmed that changing the offset-key alone is **insufficient** (`ngroups` stayed 45) **and crashes the emission** → Part-2 is inherently a *coordinated* offset-key + emission change. The bounded mechanism is **Mechanism C** — a targeted additive off-diagonal correction (parallel to the verified Part-1 `_kronecker_diag_correction`), gated on the `σ=sp` signature, that suppresses the 44 groups and emits `− b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))`, keeping the shared offset-key matcher untouched.

**Evidence:** instrumentation `[OD] 44 off-diagonal offset keys (-7..+7,{-1,0,1},999); σ bound to var pos 0 (s)`; the sibling `equil(s,spp)` binds correctly (1 group `(0,999,0)`); the prototype `ngroups=45` + emission crash. See `MARKOV_OFFDIAGONAL_DESIGN.md` §1–§4.

**Decision:** ✅ A bounded (additive, gated) mechanism exists (C); two higher-blast-radius alternatives (A: fix the shared matcher; B: a bound-to-var-index marker) are documented as fallbacks. Landable in the P1 budget with the Phase-0 `CASE_A` control (§5) as the gate + a REPLAN exit.

---

## Unknown 1.3: Will the markov fix leak onto the 2-D cohort (cesam2/camcge/ps2/ps3/polygon)?

### Priority
**Critical** — a cohort leak breaks currently-matching models (the fawley Day-9 precedent); it would force a revert and a re-design (>8h).

### Assumption
The markov diagonal-split + `σ=sp` change can be gated (by offset-key + derivative-structure) so that only markov's emit drifts — the 2-D cohort (cesam2 `model_optimal`+match, camcge, ps2_f_s, ps2_s, ps3_s_gic, polygon) stays byte-identical.

### Research Questions
1. Which of the cohort models traverse the same `(0,0,999)` diagonal group / off-diagonal enumeration branches the markov fix touches?
2. Does the gating condition (`_mult_var_collision and _all_zero_offset`, plus the `σ=sp` marker) fire on any cohort model?
3. Does a golden-staleness run after the markov change show only markov drifting (cohort byte-identical)?
4. How does the markov gate interact with the fawley discriminator (Unknown 3.2) that also touches this function?

### How to Verify
Instrument the markov gate to log every model it fires on; run `check_golden_staleness.py` (or a targeted cohort emit-diff) after a scratch markov change; confirm only markov drifts. Coordinate with Task 4 (fawley).

### Risk if Wrong
- **Cohort regression:** a leak silently changes a matching cohort model's emit → a Solve/Match regression discovered only at checkpoint.
- **Revert cost:** the fawley Day-9 precedent shows this costs a full revert + re-design.

### Estimated Research Time
2 hours (gate instrumentation + cohort golden-staleness diff)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED (design-level — leak-free by construction; the golden-staleness confirmation is the Day-1 Phase-0 gate)
**Verified by:** Task 3 (design + leak-freedom gate) — the empirical run is retained in Task 9's 2-D-cohort harness
**Date:** 2026-08-06

**Findings:** The recommended Mechanism C is **additive and gated on the markov-specific `σ=sp` signature** (a mult index whose canon matches ≥2 var positions, with a later exact-name position) and does **not** touch the shared `_compute_index_offset_key` matcher — so it cannot re-group cohort entries by construction. The leak-freedom gate is specified: `check_golden_staleness.py` over cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon must show **only markov drifts**. (The cohort emits are minutes-scale → a nightly/async or per-model diff, not an inline `make test` step.) Coordinated with Task 4 (fawley) via a joint change-surface map (both are additive gated branches with non-overlapping firing conditions).

**Evidence:** Mechanism C's design (§3–§4) leaves `_compute_index_offset_key` untouched; the leak gate + cohort-cost caveat are specified in `MARKOV_OFFDIAGONAL_DESIGN.md` §6.

**Decision:** ✅ Leak-free by design; the empirical golden-staleness run is the Day-1 Phase-0 gate (and the fallback Mechanisms A/B, which *do* touch the shared matcher, are only adopted if C's gate somehow leaks).

---

## Unknown 1.4: Does markov cold-solve to `model_optimal` once `CASE_A` is reached (is the +1 truly methodology→genuine)?

### Priority
**Critical** — the +1 genuine floor depends on markov flipping from `model_optimal_presolve` (methodology) to cold `model_optimal` (genuine); if it doesn't cold-solve, there is no floor gain.

### Assumption
markov is `verified_convex`, so a correct cold emit (`CASE_A`) will let the cold MCP solve to `model_optimal`, moving markov out of the methodology partition into the genuine floor (75→76).

### Research Questions
1. After the fix reaches `CASE_A`, does the *cold* MCP solve (no presolve) reach `model_optimal`?
2. Does the resulting solution match the reference (a genuine, not methodology, match)?
3. Is markov currently counted in the S35 methodology partition (`BASELINE_METRICS.md`), so the flip is a true +1 (not double-count)?
4. Does markov's tiny size (2 vars / 3 eqns) keep the cold solve fully local (no testbed gate)?

### How to Verify
After a scratch `CASE_A` emit, run the cold MCP solve locally (markov is tiny); confirm `model_optimal` + match; confirm markov's current methodology classification in `SPRINT_35/BASELINE_METRICS.md`.

### Risk if Wrong
- **No floor gain:** if markov needs presolve even with a correct emit, the +1 evaporates and the lever's value drops to correctness-only.
- **Partition error:** if markov is already counted genuine, fixing it adds 0 to the floor.

### Estimated Research Time
1.5 hours (cold solve + match + partition confirmation)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED (design-level — markov is `verified_convex` + methodology, so `CASE_A` → cold `model_optimal` is expected; the cold solve is the Day-1 Phase-0 gate)
**Verified by:** Task 3 (cold-solve feasibility) + Task 2 (methodology classification re-confirmed)
**Date:** 2026-08-06

**Findings:** markov is `verified_convex` and currently `model_optimal_presolve` + match (**methodology**; re-confirmed Task 2, DB byte-unchanged). A `CASE_A` cold emit ⇒ the cold MCP solves `model_optimal` ⇒ genuine match ⇒ **genuine floor 75→76 (+1)**. markov is tiny (2 vars / 3 eqns), so the cold solve is fully **local** (no testbed gate) and the Phase-0 `CASE_A` control includes a direct cold-solve confirmation.

**Evidence:** Task-2 DB re-confirm (markov methodology, `model_optimal_presolve`+match); `MARKOV_OFFDIAGONAL_DESIGN.md` §5 (the Phase-0 `CASE_A` + cold-solve gate).

**Decision:** ✅ The methodology→genuine +1 is expected and cheaply confirmable; the direct cold-solve is folded into the Phase-0 `CASE_A` control (Day 1). If the cold solve needs presolve even at `CASE_A`, the lever downgrades to correctness-only (the REPLAN exit).

---

## Unknown 1.5: What is the correct disposition of the markov `slow` test once the fix lands?

### Priority
**Medium** — a wrong disposition leaves the fix un-guarded or the test misleadingly skipped (2–4h to reconcile).

### Assumption
`test_markov_stationarity_has_correction_term` (currently `pytest.mark.slow`, red since birth) flips red→green with the P1 fix, and should then be un-marked `slow` (or replaced by a fast unit-level shape guard) so it runs in `make test`.

### Research Questions
1. Does the P1 fix make the test's assertion pass (the correct `#1110` split emitted)?
2. Is the current assertion still correct, or does it need updating to match the exact `σ=sp` target form (per the S35 Follow-up-3 sharpening)?
3. Should the test be un-marked `slow`, converted to a fast in-process shape guard, or kept `slow` with an added fast unit fixture?
4. Does un-marking `slow` add acceptable time to `make test` (markov emit is minutes-scale via subprocess CLI)?

### How to Verify
Run the test against the fixed emit; compare the assertion to the emitted `stat_z`; measure the test's wall-clock; decide the marker with the fix.

### Risk if Wrong
- **Silent regression window:** leaving it `slow` re-hides any future regression (the exact failure mode that let it stay red since March).
- **Stale assertion:** if the assertion isn't updated to the `σ=sp` target, the test could pass on a partially-correct emit.

### Estimated Research Time
1 hour (test run + marker decision)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 9 (Property-Fixture & Regression-Harness Catalog)

---

# Category 2: sarf #1385 — Symbolic-Emit Subsystem

## Unknown 2.1: Is the 369K-column `task` blow-up still >303s / non-terminating on current `main`?

### Priority
**High** — if the baseline changed, the O(active) design and its timing gate must be re-scoped (4–8h).

### Assumption
`enumerate_variable_instances` still materializes 369,024 `task` columns, and a sarf emit still exceeds 303s (non-terminating at the cap) — the O(369K) failure the symbolic re-emit must fix.

### Research Questions
1. Attempting a sarf emit under a time cap on current `main`, is it still >303s / non-terminating?
2. Is the 369,024 column count unchanged (has any parser/emitter change since S35 altered the `task` instantiation)?
3. Does `enumerate_variable_instances` still build the `col_to_var` index the whole flow iterates for all 142 models (i.e. still foundational)?

### How to Verify
Run a capped sarf emit; record the wall-clock at the cap; grep the enumeration path for the `task`-column materialization.

### Risk if Wrong
- **Stale baseline:** a changed blow-up invalidates the O(active) timing gate (the Phase-0 acceptance criterion).
- **Wasted budget:** P2 is the highest-budget track (20–28h); a stale premise costs the most.

### Estimated Research Time
1 hour (capped emit + enumeration grep)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 5 (sarf P2 Design Refresh & Blow-Up Re-Measurement)
**Date:** 2026-08-07

**Findings:** The 369K blow-up is unchanged. **Timing re-measured:** the sarf emit is still running at a 330s cap without completing ⇒ **>303s / non-terminating** (identical to the S35 baseline — the O(369K) failure). Counts re-verified: g=16, t=24, mn=31 ⇒ 16·24·31·31 = **369,024** declared / **398** active (`taskposs∧tech`, runtime-computed). The 3 sites are re-confirmed and the code surfaces (`constraint_jacobian.py`, `index_mapping.py`, `stationarity.py`) are **byte-unchanged since the anchor `78ceaead`**; `enumerate_variable_instances` present at `index_mapping.py:327`. No fourth materialization site.

**Evidence:** the capped-emit measurement (`>303s / non-terminating CONFIRMED`); the set re-count; `git diff 78ceaead..HEAD` empty for the three site files. See `SARF_DESIGN_REFRESH.md` §1.

**Decision:** ✅ The blow-up + the 3 sites apply unchanged; the banked design's baseline holds.

---

## Unknown 2.2: Does the O(active=398) guarded-emit form pass GAMS instantiation?

### Priority
**High** — the whole symbolic re-emit hinges on GAMS correctly instantiating the guarded form; if it doesn't, the approach re-scopes (4–8h).

### Assumption
Emitting one guarded `stat_task(g,t,m,n)$taskposs` + `task.fx(...)$(not (...)) = 0` and letting GAMS instantiate only the live rows (`taskposs ∧ tech` = 398) produces a correct, compilable MCP — replacing the 369K explicit columns.

### Research Questions
1. Does GAMS instantiate `stat_task(g,t,m,n)$taskposs` to the 398 active rows (not the full 369K)?
2. Is `taskposs` runtime-computed such that the active subset is *not* statically enumerable (confirming the guarded-emit necessity)?
3. Does the `task.fx(...)$(not (...)) = 0` guard correctly fix the inactive columns without a domain error?
4. Does the guarded form compile clean (no set-name-literal indices, no `$` condition errors)?

### How to Verify
Hand-construct the guarded `stat_task` + `task.fx` for a `/tmp` sarf MCP; compile it under GAMS 54; confirm the instantiated row count ≈ 398 and clean compilation.

### Risk if Wrong
- **Approach failure:** if GAMS over-instantiates or errors on the guard, the symbolic re-emit doesn't solve the blow-up.
- **Re-scope:** P2 becomes a documented re-scoping (the deliverable's fallback).

### Estimated Research Time
2 hours (hand-construct + GAMS-54 compile of the guarded form)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 5 (sarf P2 Design Refresh)
**Date:** 2026-08-07

**Findings:** The O(active=398) guarded-emit shape is valid under GAMS 54.2.1. A `/tmp` fragment mirroring `stat_task(g,t,m,n)$taskposs(g,t)` + `task.fx(...)$(not (taskposs(g,t) and tech(g,m,n)))=0` **compiles clean** (no `****` errors) and GAMS natively prunes the instantiation: synthetic `ncart=54` (full Cartesian) vs `ndomain=18` (what `stat_task$taskposs` actually instantiates) vs `nactive=4` (the taskposs∧tech live set). So the equation scales O(taskposs-active), not O(Cartesian), and the per-term `$tech` guards + `task.fx` reduce to the fully-active set (the 398 analogue for sarf).

**Evidence:** the GAMS-54 compile + `display` output (`ncart=54 / ndomain=18 / nactive=4`). See `SARF_DESIGN_REFRESH.md` §2.

**Decision:** ✅ The guarded-emit shape achieves O(active) by construction under GAMS 54; the parametric emit's job is to *produce* it without materializing the 369K instances.

---

## Unknown 2.3: Is the banked 7-term `stat_task` derivation still valid vs `sarf.gms` (no source drift)?

### Priority
**High** — the symbolic re-emit must reproduce the correct `stat_task`; a stale derivation ships a wrong MCP (4–8h).

### Assumption
The 7-term `stat_task` derivation banked in `SARF_SYMBOLIC_EMIT_DESIGN.md` still matches `sarf.gms` (no source drift), so the symbolic emit can be verified against it.

### Research Questions
1. Do the 7 terms (tbal, labor balance, equipb1/equipb2, acost3 parametric ∂, task.lo) still match `sarf.gms`?
2. Has `sarf.gms` (the raw source) changed since the S35 derivation?
3. Are the multiplier indices still the stat equation's own domain (no set-name-literal indices)?

### How to Verify
Re-derive `stat_task` from `sarf.gms` line-by-line against the banked 7-term derivation; diff the raw source vs the S35-referenced revision.

### Risk if Wrong
- **Wrong emit:** a drifted derivation ships an incorrect `stat_task`, failing the Phase-0 verify.

### Estimated Research Time
1 hour (re-derivation cross-check)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 5 (sarf P2 Design Refresh)
**Date:** 2026-08-07

**Findings:** The banked 7-term `stat_task` derivation is still valid — all seven constraint bodies are present and structurally unchanged in `sarf.gms`: `tbal(g,t)$taskposs(g,t)` (`:426`, terms 1–2 + the `tadj` harvest-c adjustment), `labor(t)` (`:438`, term 3), `equipb1(m,t)$equipposs` (`:442`, term 4), `equipb2(n,t)$equipposs` (`:445`, term 5), `acost3` (`:454`, term 6, the S1 parametric ∂), and `task.lo=0` (term 7). Line numbers drifted a few lines vs the S35 refs (the raw source is the gitignored corpus) but the structures are identical. Every multiplier is indexed by the stat equation's own domain — no set-name-literal indices.

**Evidence:** the `grep` of the constraint bodies in `sarf.gms`. See `SARF_DESIGN_REFRESH.md` §3.

**Decision:** ✅ The banked 7-term form applies unchanged; it is the correctness anchor at landing (a silently-wrong `stat_task` is the worst failure mode).

---

## Unknown 2.4: Will the symbolic re-emit stay byte-stable across determinism ×3 with no set-name-literal indices?

### Priority
**Medium** — determinism / literal-index failures are caught late (at the golden-staleness gate) but are fixable in-place (2–4h).

### Assumption
The parametric symbolic emit produces a byte-stable golden across `PYTHONHASHSEED ∈ {0,1,42}` and emits no set-name-literal (quoted-set-name) multiplier indices (the reverted Sprint-26 `nu_slack("srn")` anti-pattern).

### Research Questions
1. Does the guarded `stat_task` emit deterministically across the three hashseeds?
2. Does the compile-clean scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` return empty?
3. Does the full-corpus `--resolve-changed` harness stay GO (only sarf drifts)?

### How to Verify
Emit under the three hashseeds and diff; run the set-name-literal scan; run `--resolve-changed`.

### Risk if Wrong
- **Golden-staleness / CI failure:** non-determinism or literal indices fail the gate, blocking the PR.

### Estimated Research Time
1 hour (determinism ×3 emit + literal-index scan)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED (design-level — the 7-term form has no set-name-literal indices; the empirical determinism ×3 + the anti-pattern scan are landing gates)
**Verified by:** Task 5 (sarf P2 Design Refresh)
**Date:** 2026-08-07

**Findings:** The banked 7-term `stat_task` uses own-domain multipliers (`nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)`) — **no set-name-literal (quoted-set-name) indices** (the reverted Sprint-26 `nu_slack("srn")` anti-pattern), so the landing scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` will be empty. Determinism ×3 `{0,1,42}` + 141 byte-stable goldens + `--resolve-changed` GO are the full-corpus regression harness (the shippability / corpus-safety gate). These are **landing gates** (they need the fix's emitted output) — design-level VERIFIED, empirical at landing.

**Evidence:** the 7-term derivation's own-domain multipliers (`SARF_DESIGN_REFRESH.md` §3–§4); the regression-harness spec (`../SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` §7).

**Decision:** ✅ No set-name-literal indices by design; the determinism ×3 + byte-stable-golden harness is the atomic-landing gate (retained in Task 9's catalog + the Task-10 schedule).

---

# Category 3: fawley #1111/#1112 — Constraint-Index-Diagonal Correction

## Unknown 3.1: Can a derivative-structure key distinguish fawley's constraint-index-diagonal from the markov #1110 off-diagonal?

### Priority
**High** — the discriminator is the whole reason fawley can land this sprint (the surface-pattern predicate leaked); without it fawley re-DEFERs (4–8h).

### Assumption
A derivative-structure key (extending `_derivative_structure_key`) can fire the fawley `sameas` guard *only* when the summed multiplier index is a constraint-domain index in the variable's stat position — distinct from markov's off-diagonal derivative — so the S35 Day-9 leak does not recur.

### Research Questions
1. What derivative-structure feature distinguishes fawley's `cfq=cf` constraint-index-diagonal from markov's #1110 off-diagonal (same surface shape, different derivative)?
2. Can `_derivative_structure_key` (or a targeted extension) encode that distinction as a predicate?
3. Does the discriminator fire on fawley's qsb/pbal terms and NOT on markov's `stat_z` off-diagonal?
4. Does it leave the 2-D cohort (cesam2/camcge/ps2/ps3/polygon) untouched?

### How to Verify
Compare the `_derivative_structure_key` output for fawley qsb/pbal vs markov off-diagonal; prototype the predicate; confirm it fires on fawley only (log every model it fires on).

### Risk if Wrong
- **Repeat-DEFER:** if no derivative-structure distinction exists, fawley cannot land without re-leaking onto markov.

### Estimated Research Time
2 hours (structure-key comparison + predicate prototype)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 4 (fawley P3 — Derivative-Structure Discriminator Design)
**Date:** 2026-08-06

**Findings:** A derivative-structure key distinguishes fawley's constraint-index-diagonal from markov's #1110 off-diagonal. The precise test: **fire the `$(sameas(cfq__,cf))` guard only when the summed constraint index is ABSENT from the derivative coefficient** (appears only in the multiplier + domain guards). fawley's qsb/pbal coefficients (`prop(c,s)·char(c,m)·1$(bposs(cf,c))` / `char(c,m)·1$(bposs(cf,c))`) do **not** contain `cfq__` → the sum is a pure over-count the diagonal guard corrects. markov's off-diagonal coefficient (`(-1)·b·pi(s,i,s,i-1,s__kkt2)`) **contains** the summed index `s__kkt2` (via `pi`) → the sum is genuine, so no `sameas` is added. This is exactly the derivative-structure refinement the S35 Day-9 *surface-pattern* predicate lacked (it checked position, not whether the derivative depends on the index).

**Evidence:** the two committed goldens (`fawley_mcp_presolve.gms` `stat_bq` qsb/pbal terms; `markov_mcp.gms` `stat_z` off-diagonal). See `FAWLEY_DISCRIMINATOR_DESIGN.md` §1–§2.

**Decision:** ✅ The discriminator is `summed_idx not in _collect_free_indices(deriv_coeff)`, layered on the existing constraint-index-diagonal orientation check. It fires on fawley and never on markov.

---

## Unknown 3.2: Does the fawley discriminator co-exist with the markov P1 change in the shared `_add_indexed_jacobian_terms`?

### Priority
**Critical** — both fixes touch the same ~1430-line function this sprint; a collision breaks *both* tracks and the 2-D cohort (>8h).

### Assumption
The fawley discriminator and the markov `σ=sp` change live in non-overlapping branches of `_add_indexed_jacobian_terms`, so the combined change leaves the 2-D cohort byte-identical and neither fix disturbs the other.

### Research Questions
1. Which branches/keys does each change touch (a joint change-surface map)?
2. Does the markov gate (`_mult_var_collision and _all_zero_offset` + `σ=sp` marker) ever overlap the fawley discriminator's firing condition?
3. If staged (markov first, fawley second), does a golden-staleness gate between them confirm no interaction?
4. Combined, do cesam2/camcge/ps2/ps3/polygon stay byte-identical?

### How to Verify
Build the joint change-surface map from the Task-3 and Task-4 designs; apply both on a scratch branch; run golden-staleness (only markov + fawley drift; cohort byte-identical).

### Risk if Wrong
- **Double breakage:** a collision means neither track lands and the cohort regresses — the worst-case outcome for the two highest-value emit tracks.

### Estimated Research Time
2 hours (joint change-surface map + combined golden-staleness)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED (design-level — non-overlapping firing conditions; the golden-staleness confirmation is the Day-1 gate)
**Verified by:** Task 4 (fawley discriminator design; builds on the Task-3 markov design)
**Date:** 2026-08-06

**Findings:** The fawley discriminator and the Task-3 markov change fire on **disjoint** structural signatures (joint change-surface map in `FAWLEY_DISCRIMINATOR_DESIGN.md` §3): markov's terms **all** carry the summed index in the derivative coefficient (via `pi`) and/or an additive `Const` (`1−b·pi`); fawley's qsb/pbal carry it in **neither**. The single `summed-index-in-coefficient` test cleanly partitions them — the fawley discriminator never fires on any markov term (this *is* the fix for the S35 leak), and the Task-3 markov mechanisms (gated on the additive `Const` / the `σ=sp` alias-collision) never fire on fawley. Both are additive gated branches; neither touches the shared `_compute_index_offset_key` matcher. Recommended land order: markov first, then fawley, with a golden-staleness gate between.

**Evidence:** the joint change-surface map (§3) + the per-term structural table (§2); the coefficient contrast from the two goldens.

**Decision:** ✅ Non-overlapping by construction ⇒ no interaction. The empirical leak-freedom gate (`check_golden_staleness` — only fawley drifts; markov + the 2-D cohort byte-identical) is the Day-1 Phase-0 confirmation (retained in Task 9's harness).

---

## Unknown 3.3: Does the fawley control still drive `max|stat_bq|` 473 → 1.14e-13 on current `main`?

### Priority
**High** — the correctness fix's premise is the verified control; a non-reproducing control re-opens the diagnosis (4–8h).

### Assumption
The S35 Day-9 `/tmp` control still holds: hand-applying the qsb/pbal `$(sameas(cfq__,cf))` guard drives `max|stat_bq|` 473.4 → 1.14e-13, and fawley is still `CASE_B` (`stat_bq` 0.973) with the emit-correct `stat_trans(tr-2)` H-b divergence.

### Research Questions
1. Does `kkt_residual.py` still report fawley `CASE_B`, `stat_bq` ≈ 0.973?
2. Does the hand-edited golden (qsb/pbal + `sameas`) still drive `max|stat_bq|` → 1.14e-13?
3. Is the `stat_trans(tr-2)` H-b (non-emit) divergence still the harness max?

### How to Verify
Re-run the fawley control on current `main`; re-apply the documented `/tmp` hand-edit and re-measure the warm residual.

### Risk if Wrong
- **Premise drift:** a changed control means the fawley design (and its blast-radius analysis) must be re-derived.

### Estimated Research Time
1 hour (fawley control re-run + hand-edit re-measure)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-06

**Findings:** The fawley control reproduces the S35 fingerprint — `CASE_B`, `stat_bq` rel 0.973 (the qsb/pbal over-sum still present), dual CONSISTENT. The fawley emit code (`stationarity.py`) and goldens (`fawley_mcp.gms`, `fawley_mcp_presolve.gms`) are byte-identical to the Day-9 measurement tree, so the Day-9 `/tmp` hand-edit control (`max|stat_bq|` 473.4 → 1.14e-13) reproduces on identical inputs.

**Evidence:** `kkt_residual.py fawley` → `verdict: CASE_B`; `stat_bq(res-arab-l,fuel-oil) rel 9.73e-01` (and siblings); `git diff 78ceaead..HEAD -- src/kkt/stationarity.py` empty; `fawley_mcp.gms` + `fawley_mcp_presolve.gms` unchanged since the anchor. See `DAY0_TRACE_NOTES.md` §4.

**Decision:** ✅ The fawley correctness-fix premise holds (the qsb/pbal `sameas` gap is real and the control reproduces). Task 4 designs the derivative-structure discriminator that closes it without the markov #1110 leak.

---

## Unknown 3.4: Is fawley's +Solve truly H-b (0 bucket without forcing)?

### Priority
**Medium** — mis-scoping the +Solve wastes forcing effort or over-claims a Solve gain (2–4h).

### Assumption
Even with `stat_bq` fully closed, fawley's MCP solves MS-5 @ 4399.557 (LP optimum 2899.25) — a non-emit `stat_trans(tr-2)` divergence — so the correctness fix yields 0 Solve/floor without a `--force`/continuation lever.

### Research Questions
1. With the `sameas` correction applied, does the MCP still solve MS-5 (not MS-1)?
2. Is the residual divergence the emit-correct `stat_trans(tr-2)` (H-b), not a remaining emit bug?
3. Does any `--force` lever (homotopy/multistart/optfile) cross to MS-1?

### How to Verify
Solve the corrected fawley MCP; assert `modelstat`; run the `--force` survey (cross-reference Task 8 / `CONSULTATION_BUNDLE.md` §3).

### Risk if Wrong
- **Over-claim:** treating fawley's +Solve as emit-reachable wastes the P3 budget on the wrong lever.

### Estimated Research Time
1 hour (corrected-MCP solve + `--force` spot-check)

### Owner
Sprint 36 execution team

### Verification Results
✅ **Status:** VERIFIED (H-b re-confirmed; the `--force` +Solve scoping remains a Task-8 item)
**Verified by:** Task 2 (Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-06

**Findings:** fawley's harness max is the emit-correct `stat_trans(tr-2)` rel 1.00 — a *non-emit* divergence — dominating `stat_bq` (0.973). So even with `stat_bq` fully closed, the MCP's H-b divergence remains: the correctness fix yields 0 Solve/floor without a `--force`/continuation lever. This confirms fawley's +Solve is a forcing hand-off, not emit-reachable.

**Evidence:** `kkt_residual.py fawley` → `max-residual row: stat_trans(tr-2) rel 1.00e+00 (raw -4.88e+02)` (above `stat_bq` 0.973). See `DAY0_TRACE_NOTES.md` §4.

**Decision:** ✅ fawley's +Solve is H-b (0 bucket from the correctness fix alone). The `--force`/continuation survey (`CONSULTATION_BUNDLE.md` §3) is the +Solve avenue — scoped in Task 8. The P3 correctness fix is worth landing for the genuine floor (if fawley cold-matches) but the Solve gain is forcing-contingent.

---

# Category 4: ganges/gangesx Multi-Root Recovery

## Unknown 4.1: Does the banked `$149` `_diff_prod` fix still apply cleanly on current `main`?

### Priority
**Critical** — the `$149` fix is the verified core of the P4 recovery *and* unblocks the `$149` half of four other models; if it no longer applies, P4 (and part of P6) re-opens (>8h).

### Assumption
The banked `$149` `_diff_prod` fix (rebind the collapsed prod-dummy → the original wrt index in the cross-index CES/LES case) still applies at `src/ad/derivative_rules.py` and still drives ganges `$149` 9→0 with lmp2/camcge byte-identical.

### Research Questions
1. Is the `_diff_prod` collapse branch in `derivative_rules.py` unchanged on `main` (does the banked patch still apply)?
2. Does re-applying it still remove all 9 ganges `$149` and leave lmp2/camcge byte-identical?
3. Does it still unblock the `$149` half of dinam/indus/turkpow/clearlak (Unknown 6.3)?

### How to Verify
Diff the `_diff_prod` surface vs the S35-banked patch; re-apply on a scratch branch; re-emit ganges and confirm `$149` 9→0 + cohort byte-identical.

### Risk if Wrong
- **P4 re-diagnosis:** a drifted fix surface means re-deriving from `GANGES_149_PRODUCT_RULE_ANALYSIS.md` (the derivation is banked, so recoverable, but costs budget).

### Estimated Research Time
1 hour (fix-surface diff + scratch re-apply)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 6 (ganges Cascade Re-Verification); Task 2 contributes the fix-surface-unchanged check

**Task-2 contribution (2026-08-06):** `src/ad/derivative_rules.py` is **UNCHANGED** since the anchor and `_diff_prod` is present at `:3276` (dispatched at `:200`), so the banked `$149` `_diff_prod` fix still applies to the same surface. The existing `_expr_contains_varref_attribute` (for the `$141` helper) is present at `original_symbols.py:1392`; the buggy `_expr_contains_varref_attr` is absent. (Task 6 does the full scratch re-apply + `$149` 9→0 re-measure + the `$66`/`rPower` probe.) See `DAY0_TRACE_NOTES.md` §5.

---

## Unknown 4.2: Is the `$141` helper plan correct (use the existing `_expr_contains_varref_attribute`, not the buggy proposed variant)?

### Priority
**High** — using the buggy proposed helper re-introduces the PR-review-caught defect (4–8h to catch again).

### Assumption
The `$141` NaN-cleanup skip should reuse the **existing** `_expr_contains_varref_attribute` (`original_symbols.py:1340`), not the proposed `_expr_contains_varref_attr` (which misses attributed VarRefs in index exprs — a banked PR-review catch).

### Research Questions
1. Does `_expr_contains_varref_attribute` exist on current `main` and correctly detect attributed VarRefs in index exprs?
2. Does the proposed `_expr_contains_varref_attr` appear anywhere (it should NOT be introduced)?
3. Does reusing the existing helper remove all 15 ganges `$141`?

### How to Verify
Grep for both helper names; confirm the existing one's behavior; scratch-apply the `$141` skip using it and count remaining `$141`.

### Risk if Wrong
- **Re-introduced defect:** the buggy helper silently mishandles index-expr VarRefs, a defect already caught once.

### Estimated Research Time
0.5 hours (grep + helper behavior confirm)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 6 (ganges Cascade Re-Verification)

---

## Unknown 4.3: Are `$66` (cold) and `rPower` (presolve) still the terminal blockers after `$141`/`$145`/`$149`?

### Priority
**Critical** — if the terminal blockers changed (or there are more), P4's recovery path is different and the +2 Solve/Match may be unreachable this sprint (>8h).

### Assumption
After `$141`/`$145`/`$149` are fixed, ganges/gangesx hit exactly `$66` (cold — presolve-gated `.l`-calibration params unassigned-but-referenced-in-stationarity) then `rPower` (presolve `$onMultiR` re-runs `ganges0`, aborting `x**y, x=0, y<0`) — and no *sixth* blocker beyond these.

### Research Questions
1. After the three fixes (notionally applied), does ganges compile past `$149` to `$66`?
2. Is `$66` the presolve-gated calibration-param root (adst/aid/deltax unassigned-but-referenced)?
3. Is `rPower` the embedded-NLP-diverges root (raw ganges NLP solves fine standalone MS2)?
4. Is there any additional blocker beyond `$66`/`rPower` (a ≥6-blocker cascade)?

### How to Verify
Scratch-apply the three banked fixes; attempt a ganges emit/compile within the emit budget; record the next blocker(s).

### Risk if Wrong
- **Deeper cascade:** a sixth blocker means P4 recovers 0 bucket again (the S35 BANK outcome) — the recovery would re-bank.

### Estimated Research Time
1.5 hours (scratch three-fix apply + compile probe)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 6 (ganges Cascade Re-Verification)

---

## Unknown 4.4: Can the slow ganges/gangesx CGE goldens be regenerated within the sprint budget?

### Priority
**High** — the S35 ship-blocker was un-regenerable slow goldens; if that persists, P4 cannot land even with the fixes (4–8h scheduling impact).

### Assumption
The slow-emit ganges/gangesx CGE goldens can be regenerated in a dedicated/nightly budget slot within the sprint (unlike the S35 CI budget that blocked it).

### Research Questions
1. What is the measured emit wall-clock for ganges/gangesx (minutes-scale)?
2. Is a nightly/dedicated slot (not the CI budget) available to regenerate the goldens + run determinism ×3?
3. Does `--resolve-changed` gate the regenerated goldens correctly?

### How to Verify
Measure the ganges/gangesx emit time; identify a budget slot in the Day plan; confirm the regen + determinism ×3 fits.

### Risk if Wrong
- **Ship-blocker recurrence:** un-regenerable goldens block the P4 landing regardless of the fixes (the exact S35 constraint).

### Estimated Research Time
1 hour (emit timing + budget-slot identification)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 6 (ganges Recovery Sequencing)

---

## Unknown 4.5: Does the `$149` fix unblock the `$149` half of dinam/indus/turkpow/clearlak?

### Priority
**Low** — a cross-track bonus; if it doesn't unblock them, those models stay multi-root deferred (no P4 impact).

### Assumption
The general `$149` `_diff_prod` fix removes the `$149` blocker from dinam/indus/turkpow/clearlak (their other roots remain, but the `$149` half is resolved).

### Research Questions
1. Do dinam/indus/turkpow/clearlak share the same `$149` cross-index CES/LES product-rule root?
2. After the fix, is `$149` removed from each of their emit failures?
3. What roots remain (per the S35 multi-root characterization)?

### How to Verify
Scratch-apply the `$149` fix; re-emit each of the four; confirm `$149` removed and record remaining roots.

### Risk if Wrong
- **No cross-track bonus:** the four stay fully deferred (the S35 status quo) — no sprint impact, just no bonus.

### Estimated Research Time
0.5 hours (four re-emits, `$149` count)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 6 (ganges Cascade Re-Verification)

---

# Category 5: rocket/mine Consultation Trio + camcge Walras

## Unknown 5.1: Is the rocket PATH-consultation input still submission-ready?

### Priority
**Medium** — an incomplete input turns P5 into re-authoring instead of submitting (2–4h).

### Assumption
The FINALIZED rocket input (`CONSULTATION_BUNDLE.md` §1; renumbered S33→S36 ×11, authoring preserved) is complete and submission-ready: the concrete question + the ruled-out-lever survey + the reproducible case + the `--force` scaffold reference.

### Research Questions
1. Are all four input components present and internally consistent?
2. Are the renumbered references (S33→S36) correct and pointing at live docs?
3. Does the reproducible case still reproduce (Case-c, dual CONSISTENT) on current `main`?

### How to Verify
Read `CONSULTATION_BUNDLE.md` §1 + `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`; confirm completeness; spot-check the reproducer.

### Risk if Wrong
- **Re-authoring:** an incomplete input consumes P5 budget on writing, not submitting.

### Estimated Research Time
0.5 hours (readiness read-through)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 8 (Consultation Bundle Finalization)

---

## Unknown 5.2: Is the mine primal-degenerate-LP question precise, with the value-invariance finding and the `x.up=inf` BAN stated?

### Priority
**Low** — a fuzzy question is a documentation fix, not a blocker (<2h).

### Assumption
The mine question (`CONSULTATION_BUNDLE.md` §2 + `MINE_DUAL_ARCHITECTURE_DESIGN.md`) is precisely framed as a primal-degenerate-LP reconciliation question, states the S34 value-invariance proof, and restates the `x.up=inf` BAN.

### Research Questions
1. Is the primal-degenerate-LP framing precise (the warm KKT point not MCP-reconcilable by any emit-side dual architecture)?
2. Is the value-invariance finding (S34) cited?
3. Is the `x.up=inf` measurement-error BAN restated?

### How to Verify
Read `CONSULTATION_BUNDLE.md` §2 + the mine design doc; confirm the three elements.

### Risk if Wrong
- **Imprecise hand-off:** the LP-degeneracy question is less actionable — minor.

### Estimated Research Time
0.5 hours (read-through)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 8 (Consultation Bundle Finalization)

---

## Unknown 5.3: Is the camcge dual-consistent Walras MS-1 gate reachable in a `/tmp` control (Epic 5)?

### Priority
**High** — camcge → MS-1 is an Epic-5 deliverable; if the gate is unreachable, the Epic-5 hand-off is the per-model-numéraire fallback (4–8h to scope).

### Assumption
The full dual-consistent Walras redefinition (keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law) can be prototyped to MS-1 in a `/tmp` control — the Epic-5 gate — even though the banked price-pin variant reaches the correct primal but stays MS-4.

### Research Questions
1. Does the S1∧S2∧S3 detector still fire only camcge (cold MS-4 @ omega 191.7346)?
2. Does the price-pin variant still reach the correct primal but stay MS-4 (INFES on gdp/depreq/hhsaveq/gruse)?
3. Is a full Walras redefinition `/tmp` control feasible within the local 1000-row demo limit (camcge size)?
4. If unreachable, is the per-model-numéraire fallback the Epic-5 deliverable?

### How to Verify
Re-confirm the detector from the DB; attempt the Walras-redefinition `/tmp` control if size permits; otherwise scope the per-model-numéraire fallback.

### Risk if Wrong
- **Epic-5 slip:** if MS-1 is unreachable, camcge stays Epic-5-research (the S35 status) — expected, but the fallback must be scoped.

### Estimated Research Time
1.5 hours (detector re-confirm + Walras `/tmp` feasibility)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 8 (camcge Epic-5 Gate Scoping)

---

## Unknown 5.4: Does the camcge S1∧S2∧S3 degeneracy detector still fire only on camcge?

### Priority
**Low** — if it fires on a sibling, the per-model-numéraire scope widens, but it doesn't block P5 (<2h).

### Assumption
The S1∧S2∧S3 detector fires only on camcge (cold MS-4); the four CGE siblings (irscge/lrgcge/moncge/stdcge) cold-solve MS-1 — re-confirmable from the committed DB.

### Research Questions
1. From the committed DB, does only camcge show the cold MS-4 @ omega 191.7346 signature?
2. Do the four CGE siblings still cold-solve MS-1?
3. Has any DB drift since the anchor changed the cohort?

### How to Verify
Re-confirm the detector cohort from `gamslib_status.json` (no re-solve needed — the DB is byte-unchanged since the anchor).

### Risk if Wrong
- **Wider scope:** a second firing model widens the per-model-numéraire Epic-5 scope — minor.

### Estimated Research Time
0.5 hours (DB re-confirm)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 8 (Consultation Bundle Finalization); Task 2 contributes the DB re-confirm

**Task-2 contribution (2026-08-06):** the committed DB is **byte-unchanged** since the anchor (`git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` empty), so the S1∧S2∧S3 detector cohort is intact — no re-solve could have shifted the camcge signature. (Task 8 does the explicit per-model DB re-confirm.) See `DAY0_TRACE_NOTES.md` §6.

---

# Category 6: turkey Testbed Re-Solve + Residual Multi-Root Cohort

## Unknown 6.1: Is a licensed GAMS-54 testbed available to solve turkey's 3,866-row MCP?

### Priority
**Critical** — two Sprint-36 outcomes (turkey +1, the GAMS-54 re-baseline) are testbed-gated; no testbed = both stall (>8h / a carry-out).

### Assumption
A licensed GAMS-54 environment (CI runner or dedicated machine) capable of solving >1000-row MCPs is available and can be invoked for turkey's 3,866-row MCP (the local demo license caps at 1000 rows).

### Research Questions
1. Is there a licensed GAMS-54 environment that can solve >1000-row MCPs?
2. How is it invoked (CI job / dedicated machine / async)?
3. Can it run the turkey solve and the full-corpus re-baseline within the sprint?
4. If unavailable, what is the carry-out plan (report v53 KPIs, defer the testbed run)?

### How to Verify
Identify the testbed environment; document the invocation; confirm >1000-row solve capability (or flag its absence as a Day-0 risk).

### Risk if Wrong
- **Both P6 turkey + P7 re-baseline stall:** the +1 and the version decision carry to a later testbed cycle (the emit-level gates stay local and valid).

### Estimated Research Time
1 hour (testbed access confirmation)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 7 (GAMS-54 Licensed-Testbed Re-Baseline Harness Plan)

---

## Unknown 6.2: Does turkey solve to `model_optimal` + match under GAMS 54 (realizing the +1)?

### Priority
**High** — the turkey +1 depends on the testbed solve actually reaching optimal + match, not just compiling.

### Assumption
turkey (compile-recovered on Day 6; `path_syntax_error → path_solve_license` at the demo limit) solves to `model_optimal` + match on a licensed GAMS-54 testbed, realizing +1 Solve/Match.

### Research Questions
1. On the testbed, does turkey's 3,866-row MCP solve to `model_optimal`?
2. Does the solution match the reference NLP (a +1 Match)?
3. Is the compile-recovery byte-identical to the committed golden on the testbed?

### How to Verify
Run the turkey solve on the testbed (via `run_full_test.py`); record the bucket + comparison.

### Risk if Wrong
- **No +1:** if turkey solves to a non-optimal/mismatch bucket, the compile-recovery yields no bucket move — a re-triage.

### Estimated Research Time
1 hour (turkey testbed solve — async)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 7 (GAMS-54 Testbed Harness Plan)

---

## Unknown 6.3: Are the residual cohort roots (turkpow/clearlak/dinam/indus) still accurate and bounded-tractable?

### Priority
**Medium** — a stale characterization could send a bonus-recovery attempt down the wrong root, or miss a now-tractable model after the `$149` fix (2–4h).

### Assumption
The residual cohort roots hold: turkpow = a ragged fixed-width `Table mdatat` parse bug; clearlak = uninitialized dynamic/computed sets; dinam/indus = `$140`+`$149` — all heavily multi-root (6/9 root codes each), none bounded-tractable like turkey's single quoting root.

### Research Questions
1. Do the per-model root characterizations still hold on current `main`?
2. Does the `$149` fix (Unknown 4.5) reduce any of them to a bounded remainder?
3. Is any one now bounded-tractable enough for a bonus recovery?

### How to Verify
Re-emit each; confirm the root codes; check if the `$149` fix leaves a tractable remainder.

### Risk if Wrong
- **Missed bonus (or wasted attempt):** minor — these stay deferred regardless of P4/P6 core outcomes.

### Estimated Research Time
0.5 hours (four re-emits, root-code check)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 6 (ganges Cascade Re-Verification, which covers the residual `$149` cohort)

---

# Category 7: Infrastructure — GAMS-54 Corpus Re-Baseline + robustlp NA Fix + Property Fixtures + Genuine-Floor Tracking

## Unknown 7.1: Do any of the 5 OBJ-GAP models shift buckets under GAMS 54?

### Priority
**High** — a bucket shift in agreste/cesam/chain/fawley/rocket would change the headline KPIs and the re-baseline decision (4–8h).

### Assumption
The 5 OBJ-GAP models flagged under GAMS 54 (agreste/cesam/chain/fawley/rocket) show benign local-optima objective differences, not bucket shifts — so the v53-built 108/93/75 baseline is preserved under v54.

### Research Questions
1. Under a GAMS-54 testbed re-solve, do any of the 5 change `outcome_category` or `comparison_status` vs the v53-built DB?
2. Are the OBJ-GAPs benign (non-convex local optima) or a real regression?
3. Does the overall bucket tally (108/93/75) hold under v54?

### How to Verify
Testbed re-solve the corpus under v54; diff the buckets for the 5 (and the whole corpus) vs the v53 DB.

### Risk if Wrong
- **Baseline shift:** a bucket change under v54 changes the headline figures and forces a re-baseline decision mid-sprint.

### Estimated Research Time
1 hour (targeted re-solve diff for the 5 — async testbed)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 7 (GAMS-54 Testbed Harness Plan)

---

## Unknown 7.2: Should the canonical validation baseline pin to GAMS 54 or keep GAMS 53?

### Priority
**High** — this is the re-baseline *decision*; getting it wrong mis-anchors every subsequent KPI (4–8h to re-decide).

### Assumption
The recommended framing holds: report the v53-built KPIs as the S36 baseline (emit-level gates are version-independent), and open the v54 corpus re-baseline as a decision output — pin the DB to v54 only if the corpus re-solve shows the buckets are stable.

### Research Questions
1. Do the emit-level gates (determinism / `--resolve-changed` / golden-staleness) stay valid regardless of version (confirming they need no re-baseline)?
2. Does the v54 corpus re-solve (Unknown 7.1) support pinning to v54, or is keeping v53 (where a license solves) safer?
3. What is the concrete decision artifact (a note pinning the DB version)?

### How to Verify
Combine the Unknown-7.1 re-solve result with the emit-level-gate confirmation; write the decision note per `DAY13_RETEST_STAGING.md` §3 / `FOLLOWUPS_GAMS54_TRANSITION.md` Follow-up 2.

### Risk if Wrong
- **Mis-anchored KPIs:** pinning to the wrong version mis-reports every downstream Solve/Match figure.

### Estimated Research Time
1 hour (decision synthesis + artifact)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 7 (GAMS-54 Testbed Harness Plan)

---

## Unknown 7.3: What is the robustlp NA-coefficient root term, and is the emit fix bounded?

### Priority
**High** — robustlp is allowlisted (WARN); the real fix (a #1322-class NA-cleanup) must be bounded to de-allowlist this sprint (4–8h).

### Assumption
robustlp's GAMS-54 EXECERROR-84 ("coefficient in variable below is NA") comes from a specific emitted term going NA (the #1322 NA-propagation class — a division/arithmetic producing NA that flows into the matrix), and the emit fix is a bounded NA-cleanup extension.

### Research Questions
1. Which emitted robustlp term goes NA under GAMS 54 (trace the #1322-family root)?
2. Is it an `emit_post_assignment_na_cleanup` gap not covering the offending param?
3. Is the fix bounded enough to land + de-allowlist this sprint?

### How to Verify
Reproduce the EXECERROR-84 on the committed `robustlp_mcp_presolve.gms`; trace the NA term; scope the cleanup extension + the de-allowlist step.

### Risk if Wrong
- **Stays allowlisted:** an unbounded root keeps robustlp on the WARN allowlist (the S35 interim state) — no de-allowlist this sprint.

### Estimated Research Time
1 hour (EXECERROR reproduce + NA-term trace)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 9 (Property-Fixture & robustlp NA Survey)

---

## Unknown 7.4: Do the markov + fawley property fixtures need a shared 2-D-cohort golden-staleness harness?

### Priority
**Medium** — without a shared harness the two shared-function fixes are guarded ad-hoc; a mechanical leak-freedom gate is preferable (2–4h).

### Assumption
The markov and fawley fixes (both touching `_add_indexed_jacobian_terms`) are best guarded by (a) per-fix fail-before/pass-after fixtures *and* (b) one shared 2-D-cohort golden-staleness harness that mechanically confirms cesam2/camcge/ps2/ps3/polygon byte-identical after either change.

### Research Questions
1. Can `check_golden_staleness.py --models <cohort>` serve as the shared leak-freedom gate?
2. What are the exact fixture assertions (markov diagonal-Kronecker; fawley `shape_fawley_2d_second_index`)?
3. Do the fixtures follow the skip-if-absent (gitignored raw) pattern where they emit from raw?

### How to Verify
Prototype the cohort golden-staleness invocation; spec each fixture's assertion + skip-if-absent; map each fixture to the Task-3/Task-4 landing it guards.

### Risk if Wrong
- **Ad-hoc guarding:** without the shared harness, a cohort leak is caught late (at checkpoint), not at PR time.

### Estimated Research Time
1 hour (harness prototype + fixture specs)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 9 (Property-Fixture & 2-D-Cohort Regression-Harness Catalog)

---

## Unknown 7.5: Does the genuine-floor tracking recompute hold at anchor 75 at S36 open?

### Priority
**Medium** — the floor anchor is the PR25 baseline; a wrong anchor mis-reports the +1 target (2–4h).

### Assumption
The PR25 genuine-floor tracking recomputes to 75 at S36 open (DB byte-unchanged since the anchor → the S34/S35 hand-partition carries forward), so the S36 target is a clean 75 → ≥76.

### Research Questions
1. Does the recompute over the 142 convex candidates still give Solve 108 / Match 93 with the genuine floor at 75?
2. Is the methodology partition (30 presolve-match candidates; markov among them) unchanged?
3. Does the Epic-4 `SUMMARY.md` row-36 groundwork reflect the anchor 75?

### How to Verify
Recompute the PR25 partition from the committed DB; confirm the floor anchor 75 and markov's methodology membership.

### Risk if Wrong
- **Mis-reported target:** a shifted anchor mis-states the +1 floor goal and the SUMMARY row-36.

### Estimated Research Time
0.5 hours (PR25 recompute)

### Owner
Sprint 36 execution team

### Verification Results
🔍 **Status:** INCOMPLETE — to be verified by Task 9 (genuine-floor tracking); Task 2 contributes the baseline recompute

**Task-2 contribution (2026-08-06):** the PR25 recompute over the 142 convex candidates gives Solve 108 / Match 93 (63 cold-optimal + 30 presolve), and the DB is byte-unchanged since the anchor, so the S34/S35 methodology hand-partition carries forward → the genuine-floor anchor holds at **75**. (Task 9 does the full PR25 recompute + the SUMMARY row-36 groundwork.) See `DAY0_TRACE_NOTES.md` §1.

---

## Confirmed Knowledge (From Sprint 35 and Earlier)

The following are **established** (control-confirmed or measured in Sprint 35) and are NOT open unknowns — they are the de-risked premises Sprint 36 builds on:

- **markov is a `CASE_B` emit bug, not a stale test** — the Day-11 KKT-residual control confirmed `max|stat_z|` rel 13.3; the archaeology proved the correct `#1110` split was never emitted. (`DAY11_MARKOV_DIAGONAL_LEVER.md`)
- **The markov Part-1 diagonal split is implemented + verified** (residual 13.3→1.55) — the open part is Part-2 (`σ=sp`). (Unknown 1.2)
- **The fawley `sameas` correction is control-verified** (`max|stat_bq|` 473→1.14e-13) — the open part is the derivative-structure discriminator that avoids the markov #1110 leak. (`DAY9_P3_FAWLEY_CONTROL_DEFER.md`)
- **The ganges `$149` `_diff_prod` fix is verified + banked** (ganges `$149` 9→0; lmp2/camcge byte-identical). (`GANGES_149_PRODUCT_RULE_ANALYSIS.md`)
- **The `_add_indexed_jacobian_terms` shared-function leak is a proven hazard** — the fawley Day-9 change leaked onto markov #1110 → reverted. Any change here needs a golden-staleness leak-freedom gate.
- **The GAMS demo license caps at 1000 rows** (v53 and v54) — turkey's 3,866-row solve and the corpus re-baseline are testbed-only; emit-level gates stay local.
- **The Case-c objective-gradient sign flip + `x.up=inf` stay BANNED** (control-refuted 4×).
- **Sprint 35 closed 108/93/75** (DB byte-unchanged since anchor `78ceaead`; S35 close `597d9d08`).

---

## Template for New Unknowns

When adding unknowns during Sprint 36:

```markdown
## Unknown X.Y: [Question/Assumption]

### Priority
**[Critical/High/Medium/Low]** — [One-line impact]

### Assumption
[State the assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, /tmp controls, experiments, analysis to validate the assumption]

### Risk if Wrong
[Impact if the assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

**Before Sprint 36 Day 1:**
1. Research and verify all Critical and High priority unknowns (20 total) via prep Tasks 2–9
2. Execute the markov + fawley controls (seconds-scale, local) and the `/tmp` `CASE_A` / `max|stat_bq|→0` experiments
3. Update this document's Verification Results as each prep task completes
4. Adjust Sprint 36 scope if a Critical assumption is wrong (esp. Unknown 1.2 `σ=sp`, Unknown 3.2 shared-function collision, Unknown 6.1 testbed access)
5. Confirm zero Day-0 blockers at the Task-10 GO/NO-GO

**During Sprint 36:**
1. Reference this document daily
2. Add newly discovered unknowns (use the Template above)
3. Update verification results as features are implemented
4. Move resolved items to "Confirmed Knowledge"

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from `PREP_PLAN.md`) verify which unknowns. Each prep task's "Unknowns Verified" metadata mirrors this table.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints | 1.1, 3.3, 3.4 | Re-confirms the banked fingerprints on current `main`: markov Part-1 residual (1.1), fawley control + H-b (3.3, 3.4). Contributes the fix-surface-unchanged / DB re-confirm for 4.1, 5.4, 7.5 |
| Task 3: markov P1 — Part-2 (`σ=sp`) Off-Diagonal Enumeration Design | 1.2, 1.3, 1.4 | Primary for the `σ=sp` mechanism (1.2), the cohort-leak gate (1.3, jointly with Task 9), and the cold-solve/methodology→genuine confirmation (1.4) |
| Task 4: fawley P3 — Derivative-Structure Discriminator Design | 3.1, 3.2 | The discriminator (3.1) and its co-existence with the Task-3 markov change in the shared `_add_indexed_jacobian_terms` (3.2) |
| Task 5: sarf P2 — Symbolic-Emit Subsystem Design Refresh & Blow-Up Re-Measurement | 2.1, 2.2, 2.3, 2.4 | Re-measures the 369K blow-up (2.1), validates the O(active=398) guarded emit (2.2), the 7-term derivation (2.3), and determinism/literal-index (2.4) |
| Task 6: ganges/gangesx P4 — ≥5-Blocker Cascade Re-Verification & Recovery Sequencing | 4.1, 4.2, 4.3, 4.4, 4.5, 6.3 | The full cascade: `$149` fix (4.1), the `$141` helper (4.2), the `$66`/`rPower` terminals (4.3), the golden-regen budget (4.4), the `$149` cross-track unblock (4.5), and the residual-cohort roots (6.3) |
| Task 7: GAMS-54 Licensed-Testbed Re-Baseline Harness Plan (P7 + turkey P6) | 6.1, 6.2, 7.1, 7.2 | Testbed access (6.1), turkey solve (6.2), the OBJ-GAP bucket check (7.1), and the v53-vs-v54 canonical-baseline decision (7.2) |
| Task 8: Consultation Bundle Finalization (rocket/mine P5) + camcge Epic-5 Gate Scoping | 5.1, 5.2, 5.3, 5.4 | rocket submission-readiness (5.1), the mine question (5.2), the camcge Walras Epic-5 gate (5.3), and the detector cohort (5.4) |
| Task 9: Property-Fixture & 2-D-Cohort Regression-Harness Catalog + robustlp NA Survey | 1.3, 1.5, 7.3, 7.4, 7.5 | The cohort regression harness for the markov leak (1.3, jointly with Task 3), the markov `slow`-test disposition (1.5), the robustlp NA survey (7.3), the shared fixture harness (7.4), and the genuine-floor recompute (7.5) |
| Task 10: Plan Sprint 36 Detailed Schedule | All (integration) | Integrates every verified unknown into the day-by-day schedule, the per-track REPLAN exits, and the Day-0 GO/NO-GO |

**Note:** every unknown (1.1–7.5) is verified by at least one prep task; the Critical unknowns (1.1, 1.2, 1.3, 1.4, 3.2, 4.1, 4.3, 6.1) are front-loaded into Tasks 2–7 so they resolve before the fixture catalog (Task 9) and the schedule (Task 10).

> **Numbering note.** Unknowns are numbered per-category as `X.Y` (category.index). New unknowns discovered during the sprint append to their category (e.g. the next Category-1 unknown is `1.6`).

---

**Document Status:** 🔵 DRAFT — Pre-Sprint 36
**Last Updated:** 2026-08-06
**Owner:** Sprint 36 Planning Team
**Review Frequency:** Daily during Sprint 36
