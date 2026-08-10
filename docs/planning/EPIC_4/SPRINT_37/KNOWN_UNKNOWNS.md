# Sprint 37 Known Unknowns

**Created:** 2026-08-09
**Status:** Active — Pre-Sprint 37
**Purpose:** Proactive documentation of the assumptions and unknowns for Sprint 37 (the Sprint-36 carryforward sprint) **before** implementation begins — so each deep track (markov P1 `σ=sp` discriminator, ganges P2 `$66`/`rPower`, fawley P4 emission-path relocate) and each empirically-reproduced blocker is verified or designed in the prep phase, not discovered on Day 3.

---

## Executive Summary

This document identifies every open question, assumption, and risk across the seven Sprint-37 priorities defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 37, Weeks 39–40). Sprint 36 closed **FLAT** (Solve 108 / Match 93 / genuine floor 75 / Translate 135 — the projection's 75 branch, the fourth consecutive modal-flat close), so each carryforward inherits an **empirically-reproduced diagnosis with proven components** rather than a raw problem — a *sharper* hand-off than a prep bank, because every blocker was reproduced live in `src/` during Sprint 36. Sprint 37's unknowns are therefore the *residual* questions those sharpened banks leave open — e.g. "can a derivative-structure key distinguish markov's param-coupled `σ=sp` from cesam's variable-bilinear and sroute's conditional-constant?", "is `rPower` tractable in-sprint or the deep #1378/#1424 divergence class?", "does the fawley discriminator collide with the markov P1 change in the shared `_add_indexed_jacobian_terms`?".

**Sprint 37 Scope (per `PROJECT_PLAN.md`):**
1. **P1 markov** — `σ=sp` derivative-structure discriminator +1-floor lever (the emission is PROVEN — `CASE_A` + cold-match 2401.577; the sole blocker is the leak-free discriminator; methodology→genuine, floor 75→76)
2. **P2 ganges/gangesx** — ≥5-blocker recovery (`$141`/`$145`/`$149` VERIFIED working; `$66` cold + `rPower` presolve the terminals; +2 or 0)
3. **P3 rocket/mine** consultation + **camcge** Walras (Epic 5)
4. **P4 fawley** (#1111/#1112) — constraint-index-diagonal correction (emission-path relocate + discriminator) + the `--force` forcing hand-off
5. **P5 sarf** (#1385) — symbolic-emit subsystem (O(active=398), not O(369K))
6. **P6 turkey** testbed +1 + the full GAMS-54 v54 re-baseline + residual multi-root cohort
7. **P7 (infrastructure)** — the full-corpus (163-golden) leak-verification harness + Phase-0-doc CI enforcement + property fixtures + genuine-floor tracking

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 37 section) · `docs/planning/EPIC_4/SPRINT_37/PREP_PLAN.md` (the 11 prep tasks that verify these unknowns) · `docs/planning/EPIC_4/SPRINT_36/SPRINT_37_CARRYFORWARDS.md` (the sharpened banks) · `docs/planning/EPIC_4/SPRINT_36/SPRINT_RETROSPECTIVE.md` §4–§5 (the process lessons + the carryforward priority). *(No `PRELIMINARY_PLAN.md` exists for Sprint 37; the `PREP_PLAN.md` + the carryforward doc are the planning sources.)*

**Lessons from Previous Sprints:** the control-first REPLAN discipline (PR24/PR27) held for the sixth+ consecutive sprint — every deep track was banked/deferred on control evidence *before* any bad ship (zero broken code; `src/kkt/stationarity.py` / `src/ad/derivative_rules.py` byte-identical to the anchor all sprint). **The Sprint-36 top process lesson:** full-corpus (163-golden) leak verification is *mandatory* for any shared-`_add_indexed_jacobian_terms` change — the 6-model cohort missed all three markov Day-2 leaks (cesam/ferts/sroute). A "leak-free by construction" design claim is a hypothesis (markov's Mechanism C was argued leak-free and leaked). "Prep-doc `file:line` fix-surfaces are HYPOTHESES — verify before implementing" (wrong ~4× in S27).

**Deferred-unknown lineage:** these unknowns descend from Sprint-36 dispositions — the markov lever is the S36 Day-3 BANK (the emission proven Day 2, the discriminator the residual; S36 Unknowns 1.2/1.3); ganges/gangesx is the S36 Day-8 BANK (the ≥5-blocker cascade; S36 Unknowns 4.1/4.3); fawley's constraint-index-diagonal is the S36 Day-4 DEFER (the emission-path finding; S36 Unknowns 3.1/3.2); sarf is the S36 Day-6 BANK (S36 Unknowns 2.1/2.2); the GAMS-54 re-baseline + turkey are `GAMS54_TESTBED_PLAN.md` §3–§4 (S36 Unknowns 6.1/7.1/7.2); the full-corpus leak harness is the S36 retrospective §4 process lesson (S36 Unknown 7.4). camcge/rocket/mine carry forward from Sprints 32–36 (camcge → Epic 5).

---

## How to Use This Document

### Before Sprint 37 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (18 total)
2. Create minimal test cases / `/tmp` controls for validation (markov + fawley + ganges controls are seconds-to-minutes-scale and local; the full-corpus leak run is minutes-scale/nightly)
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 37
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

**Total Unknowns:** 27

**By Priority:**
- Critical: 7 (26% — could derail a track or force a mid-sprint REPLAN; the markov discriminator + leak gate, the ganges cascade + `rPower`, the fawley predicate, the full-corpus leak harness)
- High: 11 (41% — require upfront research/design before Day 1)
- Medium: 7 (26% — resolvable during implementation)
- Low: 2 (7% — nice-to-know, low impact)

**By Category:**
- Category 1 (markov `σ=sp` — Derivative-Structure Discriminator +1-Floor Lever): 5 unknowns
- Category 2 (ganges/gangesx ≥5-Blocker Recovery): 4 unknowns
- Category 3 (rocket/mine Consultation + camcge Walras [Epic 5]): 4 unknowns
- Category 4 (fawley #1111/#1112 — Constraint-Index-Diagonal + Forcing): 4 unknowns
- Category 5 (sarf #1385 — Symbolic-Emit Subsystem): 3 unknowns
- Category 6 (turkey Testbed +1 + Full GAMS-54 v54 Re-Baseline): 3 unknowns
- Category 7 (Infrastructure — Full-Corpus Leak Harness + Property Fixtures + Genuine-Floor Tracking + Phase-0 Enforcement): 4 unknowns

**Estimated Research Time:** ~36 hours (within the 28–36 hour target; spread across prep Tasks 2–10)

---

## Table of Contents

1. [Category 1: markov `σ=sp` — Derivative-Structure Discriminator +1-Floor Lever](#category-1-markov-σsp--derivative-structure-discriminator-1-floor-lever)
2. [Category 2: ganges/gangesx ≥5-Blocker Recovery](#category-2-gangesgangesx-5-blocker-recovery)
3. [Category 3: rocket/mine Consultation + camcge Walras (Epic 5)](#category-3-rocketmine-consultation--camcge-walras-epic-5)
4. [Category 4: fawley #1111/#1112 — Constraint-Index-Diagonal + Forcing](#category-4-fawley-11111112--constraint-index-diagonal--forcing)
5. [Category 5: sarf #1385 — Symbolic-Emit Subsystem](#category-5-sarf-1385--symbolic-emit-subsystem)
6. [Category 6: turkey Testbed +1 + Full GAMS-54 v54 Re-Baseline](#category-6-turkey-testbed-1--full-gams-54-v54-re-baseline)
7. [Category 7: Infrastructure — Full-Corpus Leak Harness + Property Fixtures + Genuine-Floor Tracking + Phase-0 Enforcement](#category-7-infrastructure--full-corpus-leak-harness--property-fixtures--genuine-floor-tracking--phase-0-enforcement)

---

# Category 1: markov `σ=sp` — Derivative-Structure Discriminator +1-Floor Lever

## Unknown 1.1: Does the reverted Day-2 Mechanism C prototype still drive `CASE_B` → `CASE_A` + cold-match 2401.577 on current `main`?

### Priority
**Critical** — if the proven emission no longer reproduces, the entire markov lever premise (methodology→genuine) is in doubt, forcing a re-diagnosis (>8h).

### Assumption
The Sprint-36 Day-2 finding still holds on current `main`: re-applying the reverted Mechanism C prototype (Kronecker `nu_constr(s,i)` + `−b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))`) drives markov `kkt_residual.py` from `CASE_B` (rel 13.3) to `CASE_A` (rel 2.8e-16), and the cold MCP solves to the reference **2401.577 + match**.

### Research Questions
1. Does `kkt_residual.py data/gamslib/raw/markov.gms` still report `CASE_B`, `max|stat_z|` rel ≈ 13.3 on current `main`?
2. Re-applying the reverted Day-2 Mechanism C prototype on a scratch branch, does the residual drop to `CASE_A` (rel ≈ 2.8e-16)?
3. Does the cold MCP then solve to `model_optimal` @ 2401.577 with a genuine match?
4. Has `_add_indexed_jacobian_terms` / `_compute_index_offset_key` drifted on `main` since the S36 close (`935d94b7`) in a way that affects the markov diagonal/off-diagonal groups?

### How to Verify
Run the markov control on current `main` (tiny model, seconds-scale, fully local); re-apply the reverted Day-2 prototype on a scratch branch, re-run the control + the cold solve, then revert. Confirm the `src/` delta since the anchor via `git diff`.

### Risk if Wrong
- **Premise collapse:** if the prototype no longer reaches `CASE_A`, the markov +1-floor lever is unverified and P1 becomes a re-diagnosis, not a discriminator design.
- **Silent `main` drift:** an unrelated shared-function change could have altered the markov groups, invalidating the S36 design.

### Estimated Research Time
1 hour (re-run the control + scratch re-apply/cold-solve/revert)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-09

**Findings:** The `CASE_B` baseline reproduces exactly on current `main` — `kkt_residual.py markov` → verdict **CASE_B**, max `stat_z(empty,disrupted,empty)` rel **1.33e+01** (raw −4.79e+04), dual **CONSISTENT** (scale 3.6e+03). markov is `verified_convex` + `model_optimal_presolve` + match @ **mcp_objective 2401.5773** (the reference) in the byte-unchanged DB. `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms`) is **byte-identical to the anchor `78ceaead`**, so the Day-2 Mechanism C prototype's proven `CASE_B` 13.3 → `CASE_A` 2.8e-16 + cold-solve **2401.577 + match** reproduces **deductively on identical code + golden**.

**Evidence:** `kkt_residual.py markov` → verdict CASE_B / `stat_z(empty,disrupted,empty)` rel 1.33e+01; `git diff 78ceaead..HEAD -- src/kkt/stationarity.py` empty; DB markov `model_optimal_presolve`+match @ 2401.5773. See `BASELINE_RECONFIRMATION.md` §3.1.

**Decision:** ✅ The proven emission holds. No scratch re-apply of the reverted prototype was needed — the emit path is provably identical (the only `src/` delta since the anchor is the unrelated turkey `original_symbols.py` + the P7 `emit_gams.py`). Task 4 designs the discriminator (the sole blocker).

---

## Unknown 1.2: Can a derivative-structure discriminator distinguish markov's param-coupled `σ=sp` from cesam's variable-bilinear and sroute's conditional-constant derivatives?

### Priority
**Critical** — this is the deep unknown gating the markov +1; without a leak-free discriminator the proven emission cannot ship (>8h REPLAN).

### Assumption
A **derivative-structure key** (inspecting the off-diagonal Jacobian coefficient's AST/IR shape) can fire the Mechanism C emission *only* on markov's genuine param-coupling (`−b·pi(s,i,σ,τ,sp)` — a parameter coupling the constraint index to the variable's independent index) and *not* on sroute's conditional-constant (`1$(darc(ip,ipp))`) or cesam's variable-bilinear derivatives.

### Research Questions
1. What is the exact IR/AST shape of the off-diagonal term as it reaches `_add_indexed_jacobian_terms` for markov (genuine), sroute (leak), and cesam (leak)?
2. Can a structural key encode "the off-diagonal coefficient is a *parameter reference* whose index tuple couples the constraint's aliased index and the variable's independent index"?
3. Does that predicate evaluate TRUE for markov and FALSE for both leak structures against the concrete IR node types (`ParamRef`, `IndexOffset`, `SubsetIndex`, conditional `$`)?
4. What is the smallest-blast-radius hook point in `_add_indexed_jacobian_terms` / `_compute_index_offset_key` for the predicate?
5. Does a `/tmp` hand-edit confirming the discriminated form still reach `CASE_A` for markov while leaving sroute/cesam emit byte-identical?

### How to Verify
Extract the three derivative structures from the committed goldens + a trace of `_add_indexed_jacobian_terms`; prototype the predicate; confirm it fires on markov only (log every model it fires on) *before* choosing a `src/` mechanism.

### Risk if Wrong
- **No separable key:** if the three structures aren't separable by a local predicate, P1 falls back to a narrower per-signature allowlist (the REPLAN exit) or banks again — the sprint's headline upside slips.
- **Wrong target form:** if the discriminated hand-edit doesn't reach `CASE_A`, the derived form is incomplete and the design must be re-derived.

### Estimated Research Time
3.5 hours (three-structure characterization + predicate prototype + the `/tmp` `CASE_A` control)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — with two corrections found by measurement
**Verified by:** Task 4 (markov P1 — Derivative-Structure Discriminator Design)
**Date:** 2026-08-10

**Findings:** All three derivative structures were **extracted from the live Jacobian** (not assumed): markov's off-diagonal is `Unary(-, Binary(*, ParamRef b(), ParamRef pi(s,i,σ,τ,sp)))` — a value-branch parameter carrying the equation index σ (position 2) and the variable's own `sp` (position 4); sroute's is `DollarCond(VAL: Const(1.0), COND: ParamRef darc(...))` — the parameter appears **only in the `$`-condition**; cesam's is `Binary(+, VarRef x(...), VarRef err1(...))` — **no ParamRef at all**. They separate cleanly. **Correction 1:** the derivative test *alone* is far too broad — a corpus scan fires on **15** models (`agreste, ajax, cesam, cesam2, china, fawley, marco, markov, orani, prolog, shale, tfordy, tforss, twocge, uimp`); a parameter coupling an equation index to a variable index is an ordinary modelling pattern. It is only valid **conjoined** with the S36 domain-collision signature. **Correction 2:** the naive conjunction *still leaked* — on `iobalance`, whose `colbal(j)`/`a(i,j)` derivative `ParamRef x(1)` has a single index coincidentally equal to both the eq value and the collision value. The fix is to require the two matches at **distinct positions** of the parameter's own index tuple (markov's `pi` carries them at positions 2 and 4; a 1-index param cannot).

**Evidence:** measured ASTs per model (§1 of the design doc); the two corpus scans (deriv-only → 15 fires; conjoined+distinct-position → `['markov']`). See `MARKOV_DISCRIMINATOR_DESIGN.md` §1–§3.

**Decision:** ✅ The discriminator is the **conjunction** (1) domain-collision signature ∧ (2) value-branch parameter coupling **at distinct positions**. Both refutations were caught at design time, before any `src/` change — the S36 lesson applied.

---

## Unknown 1.3: Does the markov discriminator pass the full-corpus (163-golden) leak gate, not just the 6-model cohort?

### Priority
**Critical** — the 6-model cohort missed all three markov Day-2 leaks (cesam/ferts/sroute); a full-corpus leak breaks currently-matching models and forces a revert + re-design (>8h).

### Assumption
After the discriminator (Unknown 1.2) is applied, a full-corpus golden-staleness run (163 goldens) shows **only markov drifts** — every other model (including cesam/ferts/sroute and the 2-D cohort) stays byte-identical.

### Research Questions
1. Does `check_golden_staleness.py` in full-corpus mode (the Task-3 harness) show only markov drifting after a scratch discriminator change?
2. Do the three Day-2 leak models (cesam, ferts, sroute) specifically stay byte-identical under the discriminated gate?
3. Does the `--expect-drift markov` pass criterion (Task 3) hold across all 163 goldens including the slow CGE/dynamic tail?
4. Does the markov gate interact with the fawley P4 discriminator (Unknown 4.2) that also touches this function?

### How to Verify
Run the Task-3 full-corpus leak harness (`make leak-check MODEL=markov`) after a scratch discriminator change; confirm only markov drifts (cesam/ferts/sroute + the full corpus byte-identical); coordinate with Task 6 (fawley).

### Risk if Wrong
- **Full-corpus regression:** a leak silently changes a matching model's emit → a Solve/Match regression discovered only at checkpoint (the exact S36 Day-2 failure mode the cohort missed).
- **Revert cost:** the markov Mechanism C precedent shows a "leak-free by construction" claim can leak — the full-corpus gate is the only proof.

### Estimated Research Time
2 hours (full-corpus leak run + the three-leak-model spot check)

### Owner
Sprint 37 execution team

### Verification Results
🔶 **Status:** DESIGN-VERIFIED — the instrument is ready and the predicate scan is strong, but the gate has not empirically run
**Verified by:** Task 3 (the instrument) + Task 4 (the predicate scan) (Full-Corpus Leak-Verification Harness Design & Setup)
**Date:** 2026-08-10

**Findings:** The instrument that catches the cesam/ferts/sroute leaks the 6-model cohort missed now exists and is tested: **`make leak-check MODEL=markov`** (= `check_golden_staleness.py --expect-drift markov`) sweeps all 163 in-scope goldens and passes **only** if markov is the sole drifter. Verified against 4 simulated scenarios: **(A)** clean tree → `NO-OP` (the fix didn't change the emit) exit 1; **(B)** markov-only drift → `LEAK GATE PASS` exit 0; **(C)** markov + cesam drift → `LEAK DRIFT: cesam_mcp.gms` + `LEAK: 1 unexpected model(s) drifted: cesam` exit 1 — **the exact S36 leak shape**; **(D)** the same logic under `--fix`, re-run on the fast `rbrock`+`trig` pair (cesam's emit is too slow for `--fix`'s determinism double-emit) → the expected golden is refreshed while **the leaked golden is left byte-untouched and named**, so it cannot be silently absorbed (the laundering path that hid the leak). Timeouts block the claim (unverified ≠ clean), so a pass is conclusive. Guardrails close the remaining ways a claim could be silently degraded: an **empty** `--expect-drift` is rejected (exit 2 — it would otherwise disable the gate while leaving `--fix` unrestricted), and **any** narrowing of what was compared (a `--models` subset, or timed-out goldens waved through with `--allow-unverified`) downgrades the verdict to `LEAK GATE PASS (PARTIAL — NOT a full-corpus leak claim)` with an explicit caveat per gap, `leak_claim_scope: partial` + a `claim_caveats` list in the JSON, and the line *"Byte-identity is NOT asserted for the models above"* — so a degraded run can never be pasted as Phase-0 evidence.

**Evidence:** the 4 scenario runs on this branch (goldens perturbed then `git checkout --` restored; corpus verified clean afterwards). See `LEAK_HARNESS_DESIGN.md` §3.

**Decision:** ✅ The full-corpus leak gate is the Task-4 Phase-0 acceptance criterion: markov's discriminator must produce `LEAK GATE PASS` on `make leak-check MODEL=markov`. Task 6 (fawley) cites the same instrument (`MODEL=fawley`, additionally proving markov untouched — the S35 fawley→markov precedent). The design-level "leak-free by construction" claim stays a hypothesis until this gate passes empirically.

**Task-4 addendum (2026-08-10):** the predicate scan strengthens but does not close this. The conjoined discriminator fires on exactly `['markov']` across **142** of the 163 in-scope models, excluding 13 of the 14 that reach the domain gate (incl. `cesam`, `sroute`). **Still not a leak-gate pass:** 6 models were skipped as pathologically slow and 4 timed out (`clearlak/dinam/ferts/tabora` — `ferts` is the third S36 leak), so **10 of 163 are unverified at design time**, and a predicate scan is not a golden byte-diff. Status stays 🔶 DESIGN-VERIFIED until `make leak-check MODEL=markov` passes at landing. See `MARKOV_DISCRIMINATOR_DESIGN.md` §3.

---

## Unknown 1.4: Does markov cold-solve to `model_optimal` + genuine match once the discriminator gates `CASE_A` (methodology→genuine, 75→76)?

### Priority
**High** — the +1 genuine floor depends on markov flipping from `model_optimal_presolve` (methodology) to cold `model_optimal` (genuine); if it doesn't cold-solve, there is no floor gain (4–8h).

### Assumption
markov is `verified_convex` and currently `model_optimal_presolve` + match (methodology), so a discriminated `CASE_A` cold emit lets the cold MCP solve to `model_optimal` @ 2401.577, moving markov into the genuine floor (75→76).

### Research Questions
1. After the discriminator reaches `CASE_A`, does the *cold* MCP solve (no presolve) reach `model_optimal` @ 2401.577?
2. Does the resulting solution match the reference (a genuine, not methodology, match)?
3. Is markov still counted in the S36 methodology partition (the 30-model presolve-match set), so the flip is a true +1 (not double-count)?
4. Does markov's tiny size keep the cold solve fully local (no >1000-row testbed gate)?

### How to Verify
After a scratch discriminated `CASE_A` emit, run the cold MCP solve locally (markov is tiny); confirm `model_optimal` + match @ 2401.577; confirm markov's current methodology classification in the DB / `BASELINE_METRICS.md`.

### Risk if Wrong
- **No floor gain:** if markov needs presolve even with a correct discriminated emit, the +1 evaporates to correctness-only.
- **Partition error:** if markov is already counted genuine, fixing it adds 0 to the floor.

### Estimated Research Time
1.5 hours (cold solve + match + partition confirmation)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 4 (design) + Task 2 (baseline re-confirmation) + S36 Day-2 (the proven emission)
**Date:** 2026-08-10

**Findings:** Sprint 36 Day 2 proved the emission end-to-end: Mechanism C drove markov `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16 **and** the **cold** MCP solved `MODEL STATUS 1 Optimal` with `pvcost = 2401.577` (the NLP reference) + match. Task 2 re-confirmed on current `main` that markov is `verified_convex`, `model_optimal_presolve` + match @ `mcp_objective 2401.5773`, and sits in the **30-model presolve-match (methodology) partition** — so the flip is a **true +1** (genuine floor **75 → 76**), not a double-count. markov is tiny, so the cold solve is fully local (no >1000-row testbed gate).

**Evidence:** `SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md` §2 (CASE_A + cold-match table); `SPRINT_37/BASELINE_RECONFIRMATION.md` §1–§3.1 (partition + fingerprint).

**Decision:** ✅ The methodology→genuine +1 is real and locally confirmable; the cold-solve assertion is Phase-0 gate item 2 (`modelstat` asserted, not inferred).

---

## Unknown 1.5: Does the markov discriminator co-exist with the fawley P4 change in the shared `_add_indexed_jacobian_terms`?

### Priority
**High** — both P1 and P4 modify the same high-blast-radius function this sprint; a collision breaks *both* tracks (the S35 fawley-leak-onto-markov precedent; 4–8h).

### Assumption
The markov `σ=sp` discriminator and the fawley constraint-index-diagonal discriminator live in non-overlapping branches of `_add_indexed_jacobian_terms` (disjoint firing signatures), so the combined change leaves the full corpus byte-identical except markov + fawley, and neither fix disturbs the other.

### Research Questions
1. Which branches/keys does each change touch (a joint change-surface map with Task 6)?
2. Does the markov discriminator's firing condition (param-coupled `σ=sp`) ever overlap the fawley discriminator's (summed constraint index absent from the coefficient)?
3. If staged (markov first, fawley second), does a full-corpus leak run between them confirm no interaction?
4. Combined, does the full corpus (including the 2-D cohort) stay byte-identical except markov + fawley?

### How to Verify
Build the joint change-surface map from the Task-4 (markov) and Task-6 (fawley) designs; apply both on a scratch branch; run the full-corpus leak harness (only markov + fawley drift).

### Risk if Wrong
- **Double breakage:** a collision means neither track lands and the corpus regresses — the worst-case for the two shared-function tracks.

### Estimated Research Time
1.5 hours (joint change-surface map + combined full-corpus leak run)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — disjoint by construction *and* by measurement
**Verified by:** Task 4 (joint change-surface analysis)
**Date:** 2026-08-10

**Findings:** Stronger than "non-overlapping firing conditions": **fawley declares no aliases at all** (`ir.aliases == {}`), and the markov gate's conjunct (1) requires an alias-canon match across ≥2 variable positions — so it is **structurally unsatisfiable** on fawley. Measured: fawley's `domain_gate_pairs` is **empty**; the markov gate never even reaches it, let alone fires. Conversely the two predicates are logical complements on one axis: fawley's discriminator fires when the summed constraint index is **absent** from the derivative coefficient, whereas markov's requires a parameter carrying it **present** (at distinct positions). Their hook points also differ — markov gates the `offset_groups` construction (`:6136+`), fawley the constraint-index-diagonal `sameas` guard.

**Evidence:** `parse_model_file("fawley.gms").aliases == {}`; the fawley scan → `{"domain_gate_pairs": [], "fires": false}`; fawley's domains `qsb(cfq,l,s)`/`pbal(cfq,m)` vs `bq(c,cf)`. See `MARKOV_DISCRIMINATOR_DESIGN.md` §8.

**Decision:** ✅ No collision possible. Land order markov (Task 4) → fawley (Task 6) with `make leak-check` between them, per the S35 fawley→markov leak precedent; Task 6 re-checks the reverse direction on the fawley side.

---

# Category 2: ganges/gangesx ≥5-Blocker Recovery

## Unknown 2.1: Do the `$141`/`$145`/`$149` cascade fixes still apply byte-clean on current `main`?

### Priority
**Critical** — the cascade fixes are the verified core of the P4 recovery *and* the `$149` fix unblocks the `$149` half of four other models; if they no longer apply, P2 (and part of P6) re-opens (>8h).

### Assumption
The banked cascade fixes still apply on current `main`: the `$141`/`$145` helper (`_expr_contains_varref_attribute`) + the `$149` `_diff_prod` §5 patch (git `a8ff626c` + `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5) drive the cold compile's `$141`/`$145`/`$149` count → 0 for both ganges and gangesx.

### Research Questions
1. Is `src/ad/derivative_rules.py` (`_diff_prod`) byte-unchanged since the anchor `78ceaead` (does the banked §5 patch still apply)?
2. Is the existing `_expr_contains_varref_attribute` still present at `original_symbols.py` (not the buggy `_expr_contains_varref_attr` PR-#1617 review catch)?
3. Does re-applying the cascade fixes still drive `$141`/`$145`/`$149` → 0 for both ganges AND gangesx?
4. Does the general `$149` fix still leave lmp2/camcge byte-identical?

### How to Verify
Diff the `_diff_prod` + helper surfaces vs the banked patches; scratch-apply on current `main`; re-emit ganges + gangesx and confirm the `$NNN` count → 0.

### Risk if Wrong
- **P2 re-diagnosis:** a drifted fix surface means re-deriving from the banked analysis (recoverable but costs budget).

### Estimated Research Time
1 hour (fix-surface diff + scratch re-apply + recount)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-09

**Findings:** The `$141`/`$145`/`$149` cascade-fix surfaces are byte-clean on current `main`. `src/ad/derivative_rules.py` (`_diff_prod` at `:3276`) is **byte-unchanged since the anchor** → the banked `$149` `_diff_prod` §5 patch applies to the same surface. The correct `$141` helper `_expr_contains_varref_attribute` is present (`src/emit/original_symbols.py:1392`); the buggy `_expr_contains_varref_attr` (PR-#1617 catch) is **absent**. The banked `$141`/`$145` WIP patch is reachable at git **`a8ff626c`**. (The original_symbols.py +52 delta since the anchor is the turkey `$161` fix, NOT the ganges helper.)

**Evidence:** `git diff 78ceaead..HEAD -- src/ad/derivative_rules.py` empty; `_diff_prod:3276`; `grep def _expr_contains_varref_attribute` → `original_symbols.py:1392`; `git cat-file -t a8ff626c` = commit. See `BASELINE_RECONFIRMATION.md` §3.2.

**Decision:** ✅ The banked cascade fixes still apply byte-clean. The full cold-cascade re-apply + the 335s emit + GAMS compile (`$141`/`$145`/`$149` → 0; the `$66`/`rPower` terminals) is Task 5's deep re-verification — the S36 Day-8 result these byte-clean surfaces guarantee.

---

## Unknown 2.2: Is `$66` a bounded emit fix or a deeper divergence (the `ac(i+2,r)` match-correctness risk)?

### Priority
**High** — `$66` is one of the two atomic-recovery terminals; if it's not a bounded fix (or a naive fix changes the matched solution), the +2 is unreachable this sprint (4–8h).

### Assumption
`$66` (×17, cold) is the presolve-gated calibration params unassigned-but-referenced in stationarity; assigning them (or guarding the reference) is a *bounded* emit fix that does not change ganges's matched solution (the `ac(i+2,r)` risk is manageable).

### Research Questions
1. Which calibration params are unassigned-but-referenced in stationarity, and why does the presolve gate leave them cold?
2. Is assigning/guarding them a bounded emit change, or does it require the deeper embedded-NLP treatment?
3. Does a naive fix change the matched solution (the `ac(i+2,r)` match-correctness risk)?
4. Does `$66` reproduce identically on ganges AND gangesx?

### How to Verify
After the cascade fixes (Unknown 2.1), attempt the cold ganges compile past `$149`; inspect the `$66` params; prototype the assign/guard and check the matched solution.

### Risk if Wrong
- **Match regression:** a `$66` fix that shifts `ac(i+2,r)` breaks the match (a Match loss, not a gain).
- **Deeper root:** if `$66` needs the embedded-NLP treatment, the +2 is `rPower`-and-`$66`-blocked.

### Estimated Research Time
1.5 hours (cold-compile probe + `$66` param analysis + match spot-check)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — bounded, but the bank's proposed fix was WRONG, and a second cold blocker exists
**Verified by:** Task 5 (ganges/gangesx P2 Cascade Re-Verification & Recovery Sequencing)
**Date:** 2026-08-10

**Findings:** `$66` is **exactly 16 symbols** (measured from the GAMS-54 listing on both models): `deltax, aid, aex, adst, as, deltas, av, deltav, aq, deltaq, az, deltaz, an, deltan, pnm00, cg`, referenced by `stat_ax/deprec/exscale/invtot/ls/lw/m/n/nd/nm` + `fddef`. **They are computable cold:** every `.l` feeding them is *data-initialized* (`ganges.gms:557–745` from the `stock`/`dat` tables) and **the only `solve` is at line 1150 — after the whole calibration block (598–746)**. The cold MCP already carries those `.l` inputs (`ls.l`×14, `pk.l`×10, `s.l`×49, …) but drops the calibration assignments (0 occurrences) purely because they *syntactically* reference a `.l` attribute. **Correction to the bank:** `GANGES_RECOVERY_SEQUENCING.md` §3 proposed "a default cold assignment, e.g. `param(domain)=0`" — that is **wrong**, because `as`/`deltas`/`av`/`deltav` are CES/LES **share and scale** parameters; zeroing them degenerates the production functions, so the cold MCP would compile while encoding a *different model* and could not legitimately match. The correct fix is to emit the real assignments cold. **Second cold blocker found:** with the `$149` fix applied the emitted cold MCP **still contains `ac(i+2,r)`** in `stat_pc(i)` — `ac` is a data Table (`:211`), so the `+2` is a spurious index offset (the same `_compute_index_offset_key` family as markov's `σ=sp`). It compiles, so the `$NNN` protocol cannot see it, but it corrupts `stat_pc` ⇒ a **match-correctness** blocker surviving the `$66` fix.

**Evidence:** the 16-symbol listing block; `ganges.gms` line numbers (593/598–746/1150); `grep` counts in `/tmp/gng/ganges_cold.gms`; `ac(i+2,r)` present in the emitted `stat_pc(i)`. See `GANGES_RECOVERY_DESIGN.md` §2.

**Decision:** ✅ `$66` is bounded (emit the assignments, **not** a zero default). The cold path needs `$66` **and** `ac(i+2,r)` — the latter may ride on the P1 markov offset work, since it is the same misattribution family.

---

## Unknown 2.3: Is `rPower` tractable in-sprint, or the deep #1378/#1424 embedded-NLP-divergence class?

### Priority
**Critical** — `rPower` is the second atomic terminal and the reproduced #1378/#1424 deep class; if it's not bounded, P2 recovers 0 bucket (the S36 outcome) despite the verified cascade fixes (>8h).

### Assumption
`rPower` (presolve — the `.l`-based power calibrations `k(i)**(-rhos(i))` re-run non-idempotently under the presolve `$onMultiR` `$include`, producing `x**y, x=0, y<0` at generation) can be broken by an NA-guard-style emit fix (cf. the P7 robustlp `.L`-guard idiom) or a re-declaration reset — OR it is the deep #1378/#1424 class beyond a bounded sprint fix.

### Research Questions
1. Does `rPower` reproduce on current `main` under presolve (the `$onMultiR` re-run of `ganges0`)?
2. Can an NA-guard / `.l`-reset / re-declaration idiom break the non-idempotency at the generation point?
3. Is the root exactly the #1378/#1424 embedded-NLP-divergence class (raw ganges NLP solves fine standalone)?
4. Is there any bounded emit lever, or is this a Sprint-38+ deep-class effort?

### How to Verify
Reproduce `rPower` under presolve; prototype the NA-guard/reset idioms in a `/tmp` control; classify against the #1378/#1424 signature.

### Risk if Wrong
- **0-bucket recovery:** if `rPower` is unbounded, the verified cascade + `$66` fix still recovers 0 bucket (a partial = golden churn) — P2 re-scopes to "land the general `$149` fix + document the residual".

### Estimated Research Time
2 hours (presolve reproduce + NA-guard/reset prototypes + classification)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — `rPower` is NOT the deep class; the deep class is one level behind it
**Verified by:** Task 5 (two independent `/tmp` controls + a raw-source reference control)
**Date:** 2026-08-10

**Findings:** The bank recorded `rPower` as the #1378/#1424 embedded-divergence class caused by `.l`-based power calibrations re-running non-idempotently. **The measured root is different and bounded.** Reproduced on both models: `Exec Error … rPower: FUNC DOMAIN: x**y, x=0,y<0` with `Evaluation error(s) in equation "prods(...)"` for cons-good/cap-good/int-good/service. The failing object is the **equation** `prods(i).. s(i) =e= as(i)*(deltas(i)*k(i)**(-rhos(i)) + ((1-deltas(i))*ls(i)**(-rhos(i)))$(not si(i)))**(-1/rhos(i))`, where **`ls` is a variable** evaluated at its *level* during generation. The level is 0 because nlp2mcp hoists the source's `.l`-dependent bound statements into a *"Deferred Variable Bounds"* block emitted **before** the `$include` that assigns those `.l`s: source order is `ls.l(i)=stock(...)` at **593** → `ls.fx(i)$(not ls.l(i))=0` at **1071** (correct); emitted order is the guard at MCP **484** → `$include` at **515** (inverted), so the guard sees `ls.l=0` for *every* sector and fixes `ls` to 0. **Two independent controls eliminate it** — (A) move the block after `$offMulti`, (B) delete it (the `$include` supplies those statements) — both take the full run from **rc=3 to rc=0** with `rPower` gone. The emitter already has both halves of this pattern (#1378 skips `$include`-supplied statements; the #1449 Layer-4 block is already a post-`$include` correction pass), so neither control invents machinery. **But behind `rPower` sits the real blocker:** with it removed, the embedded `ganges0` solves **MS-5 Locally Infeasible @ −386785.5017** while the **raw source standalone solves MS-2 Locally Optimal @ 6395.5444** (reference control) — *that* divergence is the genuine #1378/#1424 class, previously masked.

**Evidence:** the reproduction listings; the source-vs-emitted ordering table; controls A/B (`/tmp/gng/ganges_presolve_{FIXED,SKIP}.gms`, both rc=0); the raw-source reference run. See `GANGES_RECOVERY_DESIGN.md` §3–§4.

**Decision:** ✅ `rPower` is a bounded emit-ordering fix (control-verified twice). The deep blocker is relocated to the embedded-NLP MS-5-vs-MS-2 divergence — a sharper, correctly-placed hand-off than the bank's.

---

## Unknown 2.4: Is the recovery truly atomic (+2 or 0), and does the general `$149` fix unblock dinam/indus/turkpow/clearlak?

### Priority
**Medium** — mis-sequencing churns goldens for 0 bucket; the `$149` spillover affects the P6 residual cohort (2–4h).

### Assumption
The ganges/gangesx recovery is atomic — landing `$141`/`$145`/`$149` without also clearing `$66` and `rPower` produces 0 bucket + golden churn — and the general `$149` fix additionally unblocks the `$149` half of dinam/indus/turkpow/clearlak.

### Research Questions
1. Does a partial recovery (cascade only, no `$66`/`rPower`) leave ganges/gangesx at 0 bucket while churning the 335s goldens?
2. Is the correct sequence cascade → `$66` → `rPower`, per-model (ganges AND gangesx)?
3. Does the general `$149` fix remove the `$149` half of dinam/indus/turkpow/clearlak (a spillover to P6)?
4. Can the 335s slow-emit goldens be regenerated in a nightly slot within the sprint budget?

### How to Verify
Map the per-step Phase-0 gate (emit → compile → count → solve cold+presolve → bucket → match); confirm the `$149`-half spillover by emitting the four residual-cohort models with the fix.

### Risk if Wrong
- **Golden churn for 0 bucket:** a partial land wastes the P2 budget and dirties the DB.

### Estimated Research Time
1 hour (sequencing map + `$149`-spillover check)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 5
**Date:** 2026-08-10

**Findings:** Atomicity holds, with the blocker set now correctly enumerated: the **cold** bucket needs `$141`+`$145`+`$149` (✅ verified working) **+ `$66`** (bounded) **+ `ac(i+2,r)`** (match-correctness, newly surfaced); the **presolve** bucket needs the cascade **+ the `rPower` ordering fix** (control-verified) **+ the embedded-NLP MS-5 divergence** (the deep one). A partial landing churns the ganges/gangesx goldens (~9 collateral calibration goldens too) for **0 bucket** — the prohibition that banked S35 and S36. The pipeline seal is unchanged (the presolve retry fires only on a cold STATUS-5/spurious mismatch, not on a cold `path_syntax_error`), so a single-path fix cannot recover ganges. **`$149` spillover:** the `_diff_prod` fix is general and removes the `$149` blocker from dinam/indus/turkpow/clearlak — necessary-not-sufficient (turkpow ragged `Table`, clearlak dynamic sets, dinam/indus `$140`+`$149`); flagged for P6's residual cohort.

**Evidence:** the per-model (ganges AND gangesx) compile matrix; the recovery sequence with per-step gates. See `GANGES_RECOVERY_DESIGN.md` §5–§6.

**Decision:** ✅ Recovery stays atomic; **realistic in-sprint outcome 0 bucket**, but for a better-understood reason — 2 of 5 blockers are now bounded and specified, 2 remain deep (`ac(i+2,r)` possibly riding on P1's offset work; the embedded-NLP divergence).

---

# Category 3: rocket/mine Consultation + camcge Walras (Epic 5)

## Unknown 3.1: Has the PATH authors' rocket #1462 reply arrived, and does it map to a `--force homotopy` option-set (+1 contingent)?

### Priority
**High** — the rocket +1 Solve is contingent on the reply; if it hasn't arrived or doesn't map to the scaffold, the +1 slips (4–8h to re-scope the integration).

### Assumption
The FINALIZED rocket input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`) submitted from the S36 carryforward has (or will) elicit a PATH-author reply whose recommended option-set / continuation schedule plugs into the `--force homotopy` scaffold, yielding +1 Solve.

### Research Questions
1. Has the PATH authors' reply arrived by Sprint 37 Day 0?
2. Does the recommended option-set / continuation schedule map into the existing `--force homotopy` scaffold?
3. Is the integration a bounded step (option plumbing), or does it require new forcing machinery?
4. Does the Case-c objective-gradient sign flip stay BANNED (control-refuted 4×)?

### How to Verify
Check the consultation channel for the reply; map the recommended options onto `--force homotopy`; scope the integration step. If no reply, document rocket as reply-pending.

### Risk if Wrong
- **+1 slips:** no reply (or a non-mapping reply) means rocket's +1 is deferred again.

### Estimated Research Time
1 hour (reply check + option-set mapping)

### Owner
Sprint 37 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Is the mine primal-degenerate-LP question truly 0-bucket (LP-side reformulation out of emit scope)?

### Priority
**Medium** — mis-scoping mine wastes effort on a non-invariant lever (2–4h).

### Assumption
mine #1443's only non-invariant lever is an LP-side reformulation (out of emit scope), so the consultation question is 0-bucket; `x.up=inf` stays BANNED (control-refuted).

### Research Questions
1. Is the mine primal-degenerate-LP reconciliation question (`SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`) still correctly posed?
2. Is the only lever an LP-side reformulation (not an emit fix)?
3. Does `x.up=inf` stay BANNED (the refuted lever)?

### How to Verify
Re-read the mine dual-architecture design; confirm the LP-side lever is out of emit scope; confirm the question is tracked for the consultation.

### Risk if Wrong
- **Wasted effort:** treating mine as emit-reachable burns budget on a value-invariant lever.

### Estimated Research Time
0.5 hours (design re-read + question confirmation)

### Owner
Sprint 37 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Is the camcge three-part Walras redefinition reachable to MS-1 in a `/tmp` demo control (641 rows)?

### Priority
**Medium** — camcge is Epic-5-scoped; the prototype's reachability determines whether it's an Epic-5 MS-1 deliverable or the per-model-numéraire fallback (2–4h).

### Assumption
The full three-part dual-consistent Walras redefinition (numéraire + the Walras-law dual redefinition, the row-redundancy fix) can be prototyped in a `/tmp` demo control (641 rows, demo-reachable) targeting MS-1; the S36 finding was numéraire-alone → MS-4 (the two-nullspaces diagnosis).

### Research Questions
1. Does the camcge MCP (641 rows) compile + solve in a `/tmp` demo control (demo-reachable, < 1000 rows)?
2. Does the three-part Walras redefinition reach MS-1, or stay MS-4 (numéraire fixes the price-scaling ray, not the row-redundancy nullspace)?
3. Is the per-model-numéraire declaration the correct Epic-5 fallback (`EPIC_5/CGE_DEGENERACY_SCOPING.md`)?

### How to Verify
Prototype the three-part redefinition in a `/tmp` demo control; solve; assert `modelstat`; compare to the S36 numéraire-alone MS-4.

### Risk if Wrong
- **Mis-scoped Epic-5 gate:** if the three-part redefinition doesn't reach MS-1, the Epic-5 deliverable is the per-model-numéraire fallback, not the full redefinition.

### Estimated Research Time
1.5 hours (three-part prototype + demo solve)

### Owner
Sprint 37 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: Is the per-model-numéraire fallback the correct Epic-5 scoping (the two-nullspaces diagnosis)?

### Priority
**Low** — a wrong Epic-5 scoping is a documentation refinement, not a sprint blocker (<2h).

### Assumption
The S36 two-nullspaces diagnosis (numéraire fixes the price-scaling ray; a separate row-redundancy nullspace remains) holds, so the Epic-5 declaration is the per-model-numéraire fallback plus the Walras-law dual redefinition — both Epic-5, not Sprint-37 buckets.

### Research Questions
1. Does the two-nullspaces diagnosis (price-scaling ray + row-redundancy nullspace) hold on re-inspection?
2. Is the per-model-numéraire declaration the right fallback scoping in `EPIC_5/CGE_DEGENERACY_SCOPING.md`?
3. Are there other CGE models (cesam, etc.) that share this structure and belong in the same Epic-5 declaration?

### How to Verify
Re-read the S36 camcge Day-11 findings + the Epic-5 scoping doc; confirm the two-nullspaces framing; note any CGE cohort members.

### Risk if Wrong
- **Scoping drift:** a mis-framed Epic-5 declaration only costs a later documentation fix.

### Estimated Research Time
0.5 hours (diagnosis re-read + scoping confirmation)

### Owner
Sprint 37 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: fawley #1111/#1112 — Constraint-Index-Diagonal + Forcing

## Unknown 4.1: Where does the `qsb`/`pbal` emission path actually run (≠ the design's partial-overlap branch)?

### Priority
**High** — the Day-4 attempt found the emission path is not the design's assumed branch; locating it is prerequisite to any fawley fix (4–8h).

### Assumption
The `qsb`/`pbal` constraint terms emit via a specific branch of `_add_indexed_jacobian_terms` that is NOT the design's assumed partial-overlap branch, and the S35 constraint-index-diagonal orientation predicate is reverted/absent there — so the path can be located and the predicate rebuilt.

### Research Questions
1. Which branch of `_add_indexed_jacobian_terms` actually emits the `qsb`/`pbal` terms on current `main`?
2. Why does the S35 orientation predicate no longer fire there (reverted/absent)?
3. Is the located path stable, or does it depend on emit ordering / the presolve variant?
4. Does the located path also carry other models' terms (blast-radius check)?

### How to Verify
Trace the `qsb`/`pbal` terms through `_add_indexed_jacobian_terms` (instrument the branches); identify the real emission path; confirm the S35 predicate's absence.

### Risk if Wrong
- **No fix surface:** if the path can't be located, fawley re-DEFERs (0 bucket, no correctness landing).

### Estimated Research Time
1.5 hours (branch instrumentation + path trace)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 6 (fawley P4 — Emission-Path Location & Discriminator Design)
**Date:** 2026-08-10

**Findings:** Located by instrumenting `_add_indexed_jacobian_terms` for `var_name == "bq"`. Both terms take the **"truly disjoint by NAME"** branch (`src/kkt/stationarity.py:7069–7096`) and fall through to the `else: term = Sum(mult_domain, term)` fallback at **`:7096`**, with `dual_binding=None`: `[BQ] DISJOINT branch: mult_domain=('cfq','l','s') var_domain=('c','cf') dual_binding=None` and `mult_domain=('cfq','m')`. **Root cause:** the branch tests domain overlap **by name**, and `cfq ∉ {c, cf}` — but `cfq` is **declared a subset of `cf`** (`model_ir.sets['cfq'].domain == ('cf',)`), so it is not an independent iteration index and summing the whole domain over-counts. The handling for exactly this shape already exists on the *scalar*-constraint branch (Issue #1393, `_subset_alias_superset_index` at `:7251` — whose comment names **fawley** explicitly); it is simply absent from the indexed disjoint branch. Two competing hypotheses were tested and **rejected**: the `:7120` uncontrolled-free-index branch (a `_subset_alias_superset_index` fallback there left the `sameas` count at 1) and the `:6946` fresh-alias branch (it mints `root__kktN`, markov's convention, not the AD layer's `cfq__`).

**Evidence:** the instrumentation output; `model_ir.sets['cfq'].domain == ('cf',)`; `_subset_alias_superset_index('cfq__', ('c','cf')) → 'cf'`. See `FAWLEY_DISCRIMINATOR_REFRESH.md` §1.

**Decision:** ✅ The Day-4 blocker ("locate the actual emission path") is closed. The fix is a subset-aware binding in the disjoint branch, not a rebuild from scratch.

---

## Unknown 4.2: Can the constraint-index-diagonal orientation predicate be rebuilt + layered with a discriminator that co-exists with the markov P1 change?

### Priority
**Critical** — fawley P4 and markov P1 share `_add_indexed_jacobian_terms`; a predicate that collides breaks both tracks + the corpus (the S35 leak precedent; >8h).

### Assumption
At the located emission path (Unknown 4.1), the constraint-index-diagonal orientation predicate can be rebuilt and layered with a discriminator (summed constraint index absent from the derivative coefficient) that fires only on fawley — mutually exclusive with the markov `σ=sp` discriminator (Unknown 1.2).

### Research Questions
1. Can the orientation predicate be re-specified against current-tree IR node types at the located path?
2. Does the discriminator "summed constraint index absent from the coefficient" fire on fawley's `qsb`/`pbal` and never on markov's `σ=sp` (which carries the index via `pi`)?
3. Do the markov and fawley predicates partition cleanly (the joint change-surface map with Task 4)?
4. Does a full-corpus leak run show only fawley drifts (markov + the 2-D cohort byte-identical)?

### How to Verify
Re-specify the predicate + discriminator; build the joint change-surface map with Task 4; prototype both on a scratch branch; run `make leak-check MODEL=fawley` (only fawley drifts).

### Risk if Wrong
- **Double breakage:** a collision with markov P1 means neither lands and the corpus regresses.

### Estimated Research Time
2 hours (predicate rebuild + markov co-existence analysis + leak run)

### Owner
Sprint 37 execution team

### Verification Results
🔶 **Status:** PARTIAL — predicate rebuilt ✅ and markov co-existence ✅, but **leak-freedom REFUTED (twice)**
**Verified by:** Task 6 (scratch `src/` control + two full-corpus leak runs)
**Date:** 2026-08-10

**Findings:** **(Rebuilt + correctness ✅)** the orientation predicate — a multiplier index declared as a single-parent **subset** of a variable-domain index binds via `$(sameas(…))` rather than being summed — drives `stat_bq`'s `sameas` count **1 → 3** (`mbal` + `qsb` + `pbal`) and removes `stat_bq` from the KKT-residual rows entirely (baseline rel 0.973), reproducing the Day-9 target **from a real `src/` change**. **(markov co-existence ✅, structurally, both directions)** this fix sits under `elif not _did_dim_mismatch_alias_fix:` (`:7060`) while markov's `σ=sp` fix sits on the path that **sets that flag `True`** (`:6925`) — alternative branches of the same if/elif chain, so a term cannot reach both; and fawley declares **no aliases**, making markov's collision signature unsatisfiable there (Task 4). **(Leak-freedom ❌ REFUTED)** `make leak-check MODEL=fawley` — Task 3's gate, first production use — reported **`LEAK: dinam, prolog, shale`** (conjunct 1 alone) and, after adding conjunct 2 (the S36 discriminator: the coefficient must not depend on the summed index), still **`LEAK: dinam, shale`** (`prolog` excluded; `dinam` drift +190 → +40 B). **Severity is not uniform: `prolog` is a live `model_optimal` + *match* model**, so the v1 predicate could have cost a Match. All three leak models are **outside** the Sprint-36 6-model cohort — a cohort-only check would have shown clean.

**Evidence:** the two `make leak-check` runs; the shale diff (`$(sameas(t, tf))` added to six `stat_z` sums); the DB statuses (prolog `model_optimal`+match; dinam `path_syntax_error`; shale `path_solve_license`). See `FAWLEY_DISCRIMINATOR_REFRESH.md` §2–§4.

**Decision:** 🔶 Must **not** land. Remaining work is bounded and specified (`FAWLEY_DISCRIMINATOR_REFRESH.md` §6): narrow conjunct 2 — the current test is name-based and misses the AD layer's `__`-suffixed re-symbolization — then re-run to an unqualified `LEAK GATE PASS`. fawley is 0-bucket, so it must never ship at the cost of a shared-function regression.

---

## Unknown 4.3: Does the fawley `stat_bq` control still drive `max|stat_bq|` 473 → 1.14e-13 on current `main`?

### Priority
**High** — the correctness fix's premise is the verified control; a non-reproducing control re-opens the diagnosis (4–8h).

### Assumption
The S36 Day-4 control still holds: hand-applying the `qsb`/`pbal` `sameas` correction drives `max|stat_bq|` 473 → 1.14e-13 on byte-identical goldens, and fawley is still `CASE_B` with the emit-correct `stat_trans` H-b divergence dominating.

### Research Questions
1. Does `kkt_residual.py fawley` still report `CASE_B`, `stat_bq` ≈ 0.973 on current `main`?
2. Does the hand-edited golden (`qsb`/`pbal` + `sameas`) still drive `max|stat_bq|` → 1.14e-13?
3. Is the `stat_trans` H-b (non-emit) divergence still the harness max?

### How to Verify
Re-run the fawley control on current `main`; re-apply the documented hand-edit and re-measure the residual.

### Risk if Wrong
- **Premise drift:** a changed control means the fawley design must be re-derived.

### Estimated Research Time
1 hour (fawley control re-run + hand-edit re-measure)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-09

**Findings:** The fawley control reproduces exactly on current `main` — `kkt_residual.py fawley` → verdict **CASE_B**, `stat_bq(res-arab-l,fuel-oil)` rel **9.73e-01** (the qsb/pbal over-sum still present), dual **CONSISTENT**; the harness max is the emit-correct **`stat_trans(tr-2)` rel 1.00e+00** (raw −4.88e+02) — the H-b non-emit divergence dominating `stat_bq`. The fawley emit code (`stationarity.py`) + goldens are byte-identical to the anchor, so the Day-4 `/tmp` hand-edit control (`max|stat_bq|` 473 → 1.14e-13) reproduces on identical inputs.

**Evidence:** `kkt_residual.py fawley` → verdict CASE_B / `stat_bq` rel 9.73e-01 / max-residual `stat_trans(tr-2)` rel 1.00e+00; `git diff 78ceaead..HEAD -- src/kkt/stationarity.py` empty. See `BASELINE_RECONFIRMATION.md` §3.3.

**Decision:** ✅ The fawley correctness-fix premise holds (the qsb/pbal `sameas` over-sum is real and reproduces) and the +Solve is H-b (`stat_trans` dominates → closing `stat_bq` yields 0 bucket without a `--force` lever). Task 6 designs the emission-path relocate + the discriminator.

---

## Unknown 4.4: Is fawley's +Solve truly H-b (the `--force` survey NEGATIVE → a Sprint-38 consultation)?

### Priority
**Medium** — mis-scoping the +Solve wastes forcing effort or over-claims a Solve gain (2–4h).

### Assumption
Even with `stat_bq` fully closed, fawley's MCP solves MS-5 — a non-emit `stat_trans` divergence — and the S36 `--force` survey was NEGATIVE (homotopy/multistart/optfile all MS-5), so the correctness fix yields 0 Solve and the +Solve is a Sprint-38 PATH-consultation question (a stronger continuation/reformulation).

### Research Questions
1. With the `sameas` correction applied, does the MCP still solve MS-5 (not MS-1)?
2. Is the residual divergence the emit-correct `stat_trans` H-b (not a remaining emit bug)?
3. Does the S36 `--force` survey NEGATIVE result still hold (no homotopy/multistart/optfile crosses to MS-1)?
4. What stronger-continuation/reformulation question does this pose for the Sprint-38 consultation?

### How to Verify
Solve the corrected fawley MCP; assert `modelstat`; re-confirm the S36 `--force` survey; frame the Sprint-38 consultation question.

### Risk if Wrong
- **Over-claim:** treating fawley's +Solve as emit-reachable wastes the P4 budget on the wrong lever.

### Estimated Research Time
1 hour (corrected-MCP solve + `--force` re-confirm + consultation framing)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 6 (re-confirmed with `stat_bq` corrected) + S36 Day-11 (`--force` survey)
**Date:** 2026-08-10

**Findings:** With the `stat_bq` correction applied in scratch `src/`, the KKT-residual harness max is **still `stat_trans(tr-2)` rel 1.00** — an **emit-correct** divergence, unchanged by the fix. fawley's MCP stays MS-5 (LP optimum 2899.25), and Sprint 36's `--force` survey was **NEGATIVE** (homotopy/multistart/optfile all MS-5). So the correctness fix is **0 bucket by construction**: Solve/Match/genuine floor must be asserted **unchanged** (108/93/75) when it eventually lands, and claiming a bucket gain would be wrong.

**Evidence:** `kkt_residual.py fawley` with the control applied → `max-residual row: stat_trans(tr-2) rel = 1.00e+00`, no `stat_bq` row; `SPRINT_36/DAY11_P5_CONSULTATION.md` §4.

**Decision:** ✅ H-b confirmed. The +Solve is a **stronger-continuation / reformulation** question for the Sprint-38 PATH consultation, not a Sprint-37 emit fix.

---

# Category 5: sarf #1385 — Symbolic-Emit Subsystem

## Unknown 5.1: Is the 369K-column `task` blow-up still >100s / non-terminating on current `main`?

### Priority
**High** — if the baseline changed, the O(active) design and its timing gate must be re-scoped (4–8h).

### Assumption
`enumerate_variable_instances` still materializes 369,024 `task` columns, and a sarf emit still exceeds the 100s cap (non-terminating) — the O(369K) failure the symbolic re-emit must fix.

### Research Questions
1. Attempting a sarf emit under a time cap on current `main`, is it still >100s / non-terminating?
2. Is the 369,024 column count unchanged (has any parser/emitter change since S36 altered the `task` instantiation)?
3. Are the 6 call sites (`enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity) byte-unchanged since the anchor?

### How to Verify
Run a capped sarf emit; record the wall-clock at the cap; grep the enumeration path for the `task`-column materialization; diff the 6 site files vs the anchor.

### Risk if Wrong
- **Stale baseline:** a changed blow-up invalidates the O(active) timing gate.

### Estimated Research Time
1 hour (capped emit + enumeration grep + site diff)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-09

**Findings:** The 369K blow-up reproduces — a capped sarf emit on current `main` is **>105s / NON-TERMINATING** (killed at the 105.2s cap), the O(369K) failure identical to the S36 >303s baseline. The **6 call sites, spanning 3 files** (`src/ad/index_mapping.py`, `src/ad/constraint_jacobian.py`, `src/kkt/stationarity.py`), are **byte-unchanged since the anchor**; `enumerate_variable_instances` at `index_mapping.py:327`. The declared column count is `task(g,t,mn,mn)` (`sarf.gms:394` — dimensions 3 and 4 are **both** the `mn` set, with `m`/`n` its aliases), so |g|·|t|·|mn|² = 16·24·31·31 = **369,024** declared / 398 active (`taskposs ∧ tech`, runtime-computed) — structural to the byte-stable `sarf.gms`.

**Evidence:** capped emit >105s non-terminating (105.2s cap); `git diff 78ceaead..HEAD -- src/ad/index_mapping.py src/ad/constraint_jacobian.py src/kkt/stationarity.py` empty. See `BASELINE_RECONFIRMATION.md` §3.4.

**Decision:** ✅ The blow-up + the 6 sites apply unchanged; the Task-7 re-arch baseline holds.

---

## Unknown 5.2: Does the O(active=398) symbolic/parametric emit form pass GAMS instantiation?

### Priority
**High** — the whole symbolic re-emit hinges on GAMS correctly instantiating the guarded form; if it doesn't, the approach re-scopes (4–8h).

### Assumption
Emitting one guarded `stat_task(g,t,m,n)$taskposs` + `task.fx(...)$(not (...)) = 0` and letting GAMS instantiate only the live rows (`taskposs ∧ tech` = 398) produces a correct, compilable MCP under GAMS 54 — replacing the 369K explicit columns.

### Research Questions
1. Does GAMS 54 instantiate `stat_task(g,t,m,n)$taskposs` to the 398 active rows (not the full 369K)?
2. Is `taskposs` runtime-computed such that the active subset is not statically enumerable (confirming the guarded-emit necessity)?
3. Does the `task.fx(...)$(not (...)) = 0` guard correctly fix the inactive columns without a domain error?
4. Does the guarded form compile clean (no set-name-literal indices, no `$`-condition errors)?

### How to Verify
Hand-construct the guarded `stat_task` + `task.fx` for a `/tmp` sarf MCP; compile under GAMS 54; confirm the instantiated row count ≈ 398 and clean compilation.

### Risk if Wrong
- **Approach failure:** if GAMS over-instantiates or errors on the guard, the symbolic re-emit doesn't solve the blow-up → P5 re-scopes.

### Estimated Research Time
2 hours (hand-construct + GAMS-54 compile of the guarded form)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — at sarf's **real** scale, strengthening the Sprint-36 result
**Verified by:** Task 7 (sarf P5 — Symbolic-Emit Re-Architecture Design Refresh)
**Date:** 2026-08-10

**Findings:** Sprint 36 validated the guarded-emit shape on a *synthetic* 3·2·3·3 = 54-cell model (ncart 54 → nactive 4) — enough to establish the mechanism, not that it holds at the size that actually breaks. Re-ran under **GAMS 54.2.1 with sarf's actual cardinalities** (`g` 16 · `t` 24 · `mn` 31, re-counted live from `sarf.gms`): `stat_task(g,t,m,n)$taskposs(g,t)` + `task.fx(g,t,m,n)$(not (taskposs and tech)) = 0` **compiles clean (`rc=0`, 0 errors)** with `ncart` = **369,024** — exactly sarf's declared Cartesian — while instantiation is restricted to the guard domain (`ndomain` 46,128, an 8× cut from the `$taskposs` guard alone) and then to the live set (`nactive` 96) by the per-term `$tech` guard + `task.fx`. (The synthetic guards are denser than sarf's real ones, so those two figures are upper bounds on the 398 analogue; the *scaling behaviour* is the claim.) ⇒ **the guarded shape is valid GAMS 54 at 369,024 and instantiates O(guard), not O(Cartesian).**

**Evidence:** `/tmp/sarf_scale.gms` compiled under GAMS 54.2.1 → `PARAMETER ncart = 369024.000 / ndomain = 46128.000 / nactive = 96.000`, rc=0. See `SARF_REARCH_REFRESH.md` §3.

**Decision:** ✅ The emit shape is proven at real scale. The parametric emit's remaining job is to *produce* it without materializing the 369K instances (the S1/S2/S3 short-circuit).

---

## Unknown 5.3: Can the sarf re-arch land against the full-corpus regression harness (the P7 precondition)?

### Priority
**Medium** — the re-arch is not landable without the full-corpus harness proving the symbolic-branch predicate is sarf-only; a mis-ordered attempt churns goldens (2–4h).

### Assumption
The 20–28h atomic re-arch (6 call sites) is landable *only after* the Task-3/P7 full-corpus leak harness is wired — the byte-stable proof that the symbolic-branch predicate fires on sarf and no other of the 142 models — so sarf is sequenced after the P7 harness.

### Research Questions
1. Does the symbolic-branch predicate fire only on sarf (or does it touch other parametric-emit models)?
2. Is the full-corpus `--resolve-changed` regression the right landing gate (only sarf drifts)?
3. Does the re-arch stay byte-stable across determinism ×3 with no set-name-literal indices (the reverted Sprint-26 `nu_slack("srn")` anti-pattern)?
4. What is the correct sprint ordering (sarf after the P7 harness, not before)?

### How to Verify
Spec the symbolic-branch predicate; confirm the full-corpus regression is the gate; flag the sarf-after-P7-harness ordering for the schedule.

### Risk if Wrong
- **Golden churn:** landing sarf before the harness risks an undetected symbolic-branch leak onto another parametric-emit model.

### Estimated Research Time
1 hour (predicate scope + harness-precondition + ordering)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — with a correction: **the corpus-safety gate is INVERTED for sarf**
**Verified by:** Task 7 (sarf P5 — Symbolic-Emit Re-Architecture Design Refresh)
**Date:** 2026-08-10

**Findings:** The P7 precondition is **satisfied today** — Task 3's harness (`make leak-check MODEL=<id>`, `--expect-drift`) is on `main`, so the instrument the banked design demanded exists. **But the standard invocation cannot be used for sarf:** sarf has **no committed golden** (`data/gamslib/mcp/` contains **0** sarf files, because `nlp2mcp_translate: failure` — the emit never completes). So `--expect-drift sarf` would place sarf in the *expected* set but never in the *drifted* set and report **`NO-OP: expected drift on sarf but the emit was byte-identical`** → exit 1 — a failure with nothing to do with correctness. **sarf's gate is the inverse assertion:** `make check-goldens` must report **ZERO drift across all 163 goldens** (the symbolic-branch predicate fires on no existing model) **plus** sarf newly *producing* a golden (163 → 164). Since sarf contributes no golden, its corpus-safety proof is entirely the **absence** of drift elsewhere. Also re-located the **6** `enumerate_variable_instances` call sites live (`index_mapping.py:634`, `constraint_jacobian.py:78`, `gradient.py:287`/`:453`, `complementarity.py:367`/`:512`) and confirmed the 3 materialization-site files are byte-unchanged since the anchor — no fourth site.

**Evidence:** `ls data/gamslib/mcp/ | grep sarf` → 0; DB `sarf.nlp2mcp_translate.status == "failure"`; the `--expect-drift` semantics in `check_golden_staleness.py`. See `SARF_REARCH_REFRESH.md` §2, §4.

**Decision:** ✅ Ordering for the Task-11 schedule: sarf after the P7 **CI wiring** (the instrument itself is already available), and its Phase-0 corpus gate is **`make check-goldens`**, not `leak-check` — recorded because running the P1/P4 recipe here would produce a confusing false failure.

---

# Category 6: turkey Testbed +1 + Full GAMS-54 v54 Re-Baseline

## Unknown 6.1: Is a licensed >1000-row GAMS-54 testbed procurable in the sprint window (turkey's 3,866-row MCP)?

### Priority
**High** — turkey's +1 Solve/Match is the sole externally-gated bucket move; no licensed >1000-row GAMS-54 testbed exists (local + CI both demo), so procurement is an external dependency for a bonus +1 (not a core-lever blocker), but its resolution shapes the sprint's Solve ceiling (4–8h to re-scope if unavailable).

### Assumption
A licensed >1000-row GAMS-54 environment (a licensed local install, a cloud GAMS, or a CI secret) is procurable in the sprint window to re-solve turkey's 3,866-row MCP and realize the +1 Solve/Match.

### Research Questions
1. Is a licensed >1000-row GAMS-54 environment available (local, cloud, or CI)?
2. If yes, can turkey's 3,866-row MCP be solved to `model_optimal` + match there?
3. If no, is turkey's +1 documented as license-gated with the exact blocker (the S36 disposition)?
4. Does turkey's compile-recovery (the S35 `$161` fix) still reach PATH on the testbed?

### How to Verify
Determine testbed availability; if available, plan the turkey re-solve; if not, document turkey as license-gated (+1 deferred) with the exact blocker.

### Risk if Wrong
- **+1 unreachable:** no testbed means turkey's +1 stays deferred (the S36 disposition) — the sprint's Solve ceiling drops by 1.

### Estimated Research Time
1 hour (testbed availability determination)

### Owner
Sprint 37 execution team

### Verification Results
❌ **Status:** WRONG — the assumption is refuted; **no licensed environment exists or is procurable**
**Verified by:** Task 8 (GAMS-54 v54 Re-Baseline Plan + turkey Testbed Procurement)
**Date:** 2026-08-10

**Findings:** Every candidate path checked: **all three local GAMS installs (51 / 53 / 54.2.1) are `GAMS_Demo`**, and CI holds only `PYPI_API_TOKEN` — **no GAMS license secret**; the workflows install the public demo. No licensed >1000-row GAMS-54 environment is available or procurable from within the repo (acquiring one is a purchasing decision outside the sprint's control). **turkey's block measured precisely:** compiling the committed `turkey_mcp.gms` under GAMS 54.2.1 gives `SINGLE EQUATIONS 3,866` / `SINGLE VARIABLES 3,753` and `**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns` — the banked 3,866 figure now **measured, not cited**. Critically the compile is otherwise **clean: zero `$NNN` errors**, so the S35 Day-6 `$161` compile-recovery genuinely worked and **the license is the only remaining blocker** — the +1 would be realized immediately on a licensed run. **Bonus finding:** turkey's DB row is **stale** — `path_syntax_error`, `solve_date 2026-06-20`, i.e. seven weeks *before* the `$161` fix landed (2026-08-03) — because `--resolve-changed` **deliberately never persists** (`run_full_test.py:1267`). A persisting re-solve moves turkey `path_syntax_error → path_solve_license`, i.e. **pse 7 → 6, with no Solve/Match change**.

**Evidence:** the three `gamslice.txt` headers; `gh secret list`; the turkey compile listing (3,866 rows + the demo refusal + 0 `$NNN`); the DB row's `solve_date`; `run_full_test.py:1267`. See `GAMS54_REBASELINE_PLAN.md` §1.

**Decision:** ❌ turkey's +1 is **NO-GO for this sprint — license-gated**, not technically blocked. Nothing further in prep can move it. The stale-DB finding is carried into the re-baseline decision rule (§3) so it is not miscounted as a v54 effect.

---

## Unknown 6.2: Does the full v54 demo re-baseline of the 142 candidates show zero bucket regressions (the re-pin decision)?

### Priority
**High** — the canonical-version decision (keep v53 vs re-pin to v54) depends on a zero-regression re-baseline; a missed regression mis-pins the DB (4–8h).

### Assumption
The 142-candidate solving set is demo-solvable (the baseline is demo-built), so a full GAMS-54 demo re-solve is runnable; re-pin the DB to v54 only on confirmed **zero bucket regressions**, else keep v53(51.3.0).

### Research Questions
1. Does the full v54 demo re-solve of the 142 candidates complete (all demo-solvable)?
2. Does the bucket-diff vs the v53 DB show zero regressions (a bucket downgrade), or are there regressions to document?
3. Does P7's robustlp v54-solvability restoration hold in the re-baseline?
4. What is the re-pin decision (v54 on zero regressions, else v53)?

### How to Verify
Run the `run_full_test.py` re-solve of the 142 candidates under GAMS 54 demo; diff buckets vs the v53 DB; produce `GAMS54_REBASELINE_DIFF.md`; apply the decision rule.

### Risk if Wrong
- **Mis-pinned DB:** re-pinning to v54 with an undetected regression mis-reports the KPIs; keeping v53 with a clean v54 leaves the transition incomplete.

### Estimated Research Time
1.5 hours (demo re-solve + bucket-diff + decision)

### Owner
Sprint 37 execution team

### Verification Results
🔶 **Status:** DESIGN-VERIFIED — procedure + decision rule specified; the full 142-model diff is the gate
**Verified by:** Task 8
**Date:** 2026-08-10

**Findings:** The re-baseline is **cheap and low-risk**: measured cost ~**12 s/model** (agreste 0.85 s, chain 10.5 s, fawley 12.7 s, rocket 31.9 s) ⇒ **~30 minutes for all 142** — not the blocker the bank implied. Procedure specified: snapshot the DB (with md5) → re-solve the 142 convex candidates under GAMS 54 demo → per-model bucket diff into `GAMS54_REBASELINE_DIFF.md` → re-check the 5 OBJ-GAP models → apply the decision rule → commit or restore. **The decision rule needs three categories, not two:** *Regression* (a bucket downgrade attributable to v54 — blocks the re-pin), *neutral churn* (in-tolerance jitter / lateral move — recorded, does not block), and **stale-entry correction** (the v53 row predates a landed fix, so the change reflects *our* code, not v54 — **turkey is exactly this**, and would otherwise be miscounted as a spurious v54 effect). **Rule: re-pin only if the diff contains zero Regressions.** **Gap noted:** the DB records `solver_version: None` for all 219 models — there is no per-row version provenance, which is why this question can only be answered by re-running; the re-baseline should populate it.

**Evidence:** the measured per-model timings; the three-way classification derived from the turkey stale-row finding (6.1); `solver_version` null across all 219 rows. See `GAMS54_REBASELINE_PLAN.md` §3.

**Decision:** 🔶 Deliberately **not** upgraded to VERIFIED — only **5 of 142** models were actually re-solved in this task (§6.3). The zero-regression claim over the full corpus requires the full run, which is an in-sprint execution step.

---

## Unknown 6.3: Which of the 5 OBJ-GAP models shift buckets under v54, and does the `$149` fix unblock the residual cohort?

### Priority
**Medium** — the OBJ-GAP models + the residual multi-root cohort are secondary bucket movers; a mis-read costs a minor re-triage (2–4h).

### Assumption
The 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket) are the v54-strictness risk set (re-check their buckets), and the P2 general `$149` fix unblocks the `$149` half of the residual cohort (turkpow/clearlak/dinam/indus) — each a per-model dedicated effort otherwise.

### Research Questions
1. Do any of agreste/cesam/chain/fawley/rocket shift buckets under v54 demo?
2. Does the P2 general `$149` fix remove the `$149` half of turkpow (ragged `Table mdatat`) / clearlak (dynamic sets) / dinam / indus?
3. Is any residual-cohort model a bounded per-model effort for the sprint tail?

### How to Verify
Re-check the 5 OBJ-GAP buckets in the v54 re-baseline (Unknown 6.2); emit the residual cohort with the `$149` fix; count remaining `$NNN`.

### Risk if Wrong
- **Minor re-triage:** a mis-read OBJ-GAP or a non-unblocked `$149` half only costs a per-model re-scoping.

### Estimated Research Time
1 hour (OBJ-GAP re-check + residual-cohort `$149` emit)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — **none of the five shift**
**Verified by:** Task 8 (live re-solve under GAMS 54.2.1)
**Date:** 2026-08-10

**Findings:** All 5 OBJ-GAP models re-solved under **GAMS 54.2.1** (DB snapshotted → mutated → **restored byte-identical**, md5 `6166acab…` before and after): `agreste` `model_infeasible` → **unchanged**; `cesam` `model_infeasible` → **unchanged**; `chain` `model_optimal_presolve` + mismatch, nlp **5.0723** / mcp **5.1199** → **unchanged, objectives byte-identical**; `fawley` `model_infeasible` → **unchanged**; `rocket` `model_infeasible` → **unchanged**. **Zero bucket changes and not even numerical drift** on the models Sprint 36 named as the v54-strictness risk set — materially de-risking the re-pin decision. **Residual cohort** (`turkpow`/`clearlak`/`dinam`/`indus`) re-confirmed all still `path_syntax_error`; the P2 general `$149` fix removes that blocker but each carries other roots (turkpow ragged `Table`, clearlak dynamic sets, dinam/indus `$140`+`$149`) ⇒ **necessary-not-sufficient**. Note `dinam` is also one of the models the fawley predicate leaks onto (Task 6), so it is touched by two open tracks and should not be worked in isolation.

**Evidence:** the before/after bucket table; the DB md5 identical across the run; the residual-cohort DB statuses. See `GAMS54_REBASELINE_PLAN.md` §2, §4.

**Decision:** ✅ The named risk set is clean under v54. No in-sprint effort on the residual cohort.

---

# Category 7: Infrastructure — Full-Corpus Leak Harness + Property Fixtures + Genuine-Floor Tracking + Phase-0 Enforcement

## Unknown 7.1: Can the full-corpus (163-golden) leak harness run as a required PR gate within CI budget (fast + nightly modes)?

### Priority
**Critical** — this is the Sprint-36 top process lesson and the gate P1/P4 design against; if it can't run within budget as a required gate, the shared-function landings ship un-leak-verified (>8h / re-introduces the S36 cohort miss).

### Assumption
`check_golden_staleness.py` can run in two modes — a PR-blocking fast mode (fast/medium goldens, within CI time budget) + a nightly full mode (all 163 including the slow CGE/dynamic/ganges tail) — armed by a path/function-scoped trigger, with an `--expect-drift <model>` pass criterion.

### Research Questions
1. What is the full-corpus regen wall-clock, and which goldens are the slow tail (the CGE/dynamic/ganges 335s models)?
2. Does the fast mode (fast/medium goldens) complete within the CI time budget as a PR-blocking gate?
3. Can the trigger be scoped to `_add_indexed_jacobian_terms` / `_compute_index_offset_key`-relevant changes (not arm on unrelated emit changes)?
4. Does `--expect-drift markov` / `--expect-drift fawley` correctly pass when only that model drifts?
5. Does a dry-run on a clean tree show zero false-positive drift (the harness is deterministic)?

### How to Verify
Inventory + cost-classify the 163 goldens; time a full regen + the fast subset; prototype the `--expect-drift` criterion; dry-run on a clean tree (zero drift).

### Risk if Wrong
- **Un-gated shared-function landings:** if the harness can't be a required gate, P1/P4 ship without full-corpus leak proof — the exact S36 cohort miss.

### Estimated Research Time
2 hours (golden inventory + timing + `--expect-drift` prototype + dry-run)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED — with a correction to the premise
**Verified by:** Task 3 (Full-Corpus Leak-Verification Harness Design & Setup)
**Date:** 2026-08-10

**Findings:** The premise ("a full-corpus mode must be built as a required gate within CI budget") is **partly wrong**. (1) The full-corpus sweep **already exists**: `.github/workflows/golden-staleness.yml` runs `check_golden_staleness.py` with **no `--models` restriction** → all 163 in-scope goldens, on every PR touching `src/{ad,kkt,emit,ir}/**`, inside a **25-min** ceiling, and it has been green on every triggering PR (S35 Day-6, S36 Day-10). **Budget is not the constraint, and no fast/nightly split is warranted** — splitting would reintroduce exactly the cohort-incompleteness that caused the S36 miss. (2) The **path trigger is already correct**: both shared functions live in `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms:5861`, `_compute_index_offset_key:4969`), covered by `src/kkt/**/*.py`; narrowing to *function* scope would be fragile and strictly worse. (3) The **real gaps**: the gate is **not a required check** (`branches/main/protection` → `required_status_checks.contexts` = `[]`), and its verdict is binary — it answers "did anything drift?" when a shared-function change needs "did *exactly* the intended model drift?". Its remediation advice (`make regen-goldens`) refreshes **every** drifted golden, so a leak is **laundered into the corpus** and the gate goes green (the S36 markov failure mode, traced step-by-step).

**Evidence:** `golden-staleness.yml` (no `--models`, 25-min timeout, `src/{ad,kkt,emit,ir}/**` paths); `gh api .../branches/main/protection` → `contexts: []`; `check_one(..., fix=args.fix)` applied to all in-scope models + the printed "Run `make regen-goldens`" advice. See `LEAK_HARNESS_DESIGN.md` §1–§2.

**Decision:** ✅ Implemented `--expect-drift` + `make leak-check MODEL=<id>` — exactly-the-expected-set semantics with **anti-laundering** (`--fix` refreshes only expected models), **no-op detection** (an expected model that *doesn't* drift fails), and **unverified≠clean** (timeouts block the claim). Verified against 4 simulated scenarios (§3). Two items remain for P7 in-sprint: making `golden-staleness` a *required* check (a maintainer branch-protection setting) and wiring `leak-check` into the emit-PR Phase-0 rule.

---

## Unknown 7.2: Where does the Phase-0-doc CI enforcement check hook (which changed-path glob triggers it)?

### Priority
**Medium** — a mis-scoped trigger either misses emit PRs (the S36 robustlp gap) or false-fires on unrelated PRs (2–4h to tune).

### Assumption
A lint/CI check can enforce that any PR touching `src/{ad,kkt,emit}` has a `docs/issues/ISSUE_<N>_*.md` with the `## Phase 0: Acceptance Gate` heading + its 4 `### ` subsections, triggered by a changed-path glob.

### Research Questions
1. Which changed-path glob correctly captures emit-touching PRs (`src/ad/`, `src/kkt/`, `src/emit/`) without false-firing on tests/docs?
2. How does the check detect the `## Phase 0: Acceptance Gate` heading + 4 `### ` subsections in the referenced issue doc?
3. Does it hook as a CI job, a pre-commit lint, or both (the S36 robustlp lesson: needed under review, not before)?
4. What is the failure message that points the author to CONTRIBUTING.md §392–447?

### How to Verify
Prototype the changed-path trigger + the heading/subsection check on a sample emit PR; confirm it fires on `src/{ad,kkt,emit}` and not on docs-only PRs.

### Risk if Wrong
- **Missed enforcement:** a mis-scoped trigger re-allows an emit PR without its Phase-0 doc (the S36 robustlp gap).

### Estimated Research Time
1 hour (trigger glob + heading-check prototype)

### Owner
Sprint 37 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.3: Do the property fixtures (`shape_markov_diagonal_kronecker`, `shape_fawley_2d_second_index`) fail-before/pass-after and skip-if-absent?

### Priority
**High** — the fixtures are the inline `make test` guards for the P1/P4 landings; a fixture that doesn't fail-before can pass on a partially-correct emit (4–8h to catch a silent regression later).

### Assumption
The two shape fixtures land *with* their fixes — `shape_markov_diagonal_kronecker` (with P1, asserting the discriminated `σ=sp` split), `shape_fawley_2d_second_index` (with P4, asserting the second-index term fires only when the summed index is absent from the coefficient) — each fail-before/pass-after and `pytest.skip` when the gitignored raw source is absent.

### Research Questions
1. Does `shape_markov_diagonal_kronecker` fail on the current (pre-fix) emit and pass on the discriminated emit?
2. Does `shape_fawley_2d_second_index` fail-before/pass-after on the fawley discriminator?
3. Do both `pytest.skip` when `data/gamslib/raw/*.gms` is absent (CI lacks the raw sources)?
4. Are the fixtures fast (in-process, inline `make test`), not slow subprocess tests?

### How to Verify
Spec each fixture's assertion against the discriminated target form (from Tasks 4, 6); confirm the fail-before on the current emit; confirm the skip-if-absent guard.

### Risk if Wrong
- **Silent regression window:** a fixture that doesn't fail-before can pass on a partially-correct emit (the markov `slow`-test-red-since-March failure mode).

### Estimated Research Time
1 hour (fixture assertion specs + fail-before confirmation)

### Owner
Sprint 37 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.4: Does the genuine-floor tracking recompute hold at anchor 75 at S37 open (markov ∈ methodology → the +1 is real)?

### Priority
**Low** — the floor anchor is the PR25 baseline; a wrong anchor mis-reports the +1 target but is a bookkeeping fix (<2h).

### Assumption
The PR25 genuine-floor tracking recomputes to 75 at S37 open (DB byte-unchanged since the anchor `78ceaead` → the S34–S36 hand-partition carries forward), and markov is in the 30-model presolve-match (methodology) partition, so the markov lever is a true +1 (75→76), not a double-count.

### Research Questions
1. Does the recompute over the 142 convex candidates still give Solve 108 / Match 93 with the genuine floor at 75?
2. Is markov still in the methodology partition (`model_optimal_presolve` + match, `verified_convex`)?
3. Does the Epic-4 `SUMMARY.md` row-37 groundwork reflect the anchor 75 → ≥76 target?

### How to Verify
Recompute the PR25 partition from the committed DB; confirm the floor anchor 75 and markov's methodology membership; draft the SUMMARY row-37 skeleton.

### Risk if Wrong
- **Mis-reported target:** a shifted anchor mis-states the +1 floor goal and the SUMMARY row-37.

### Estimated Research Time
0.5 hours (PR25 recompute + SUMMARY row-37 skeleton)

### Owner
Sprint 37 execution team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints)
**Date:** 2026-08-09

**Findings:** The PR25 recompute over the 142 convex candidates (verified_convex 54 + likely_convex 88) gives **Solve 108 / Match 93 (63 cold + 30 presolve) / Translate 135 / Parse 142 / mi 7 / pse 7 / all-219 96** — matching the S36 close exactly. The DB is **byte-identical to the anchor `78ceaead`** (0 bucket move), so the S34–S36 genuine-floor hand-partition carries forward → the anchor holds at **75**. markov is in the **30-model presolve-match (methodology) partition** (`model_optimal_presolve` + match, `verified_convex`), so the markov methodology→genuine lever (Task 4) is a **true +1** (75→76), not a double-count.

**Evidence:** the DB partition recompute (108 / 93 = 63+30; the 30-model methodology partition; markov ∈ it); `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` empty. See `BASELINE_RECONFIRMATION.md` §1–§2.

**Decision:** ✅ Floor anchor **75 → ≥76** target (markov); the Epic-4 SUMMARY row-37 groundwork (Task 10) anchors at 75.

---

## Confirmed Knowledge (From Sprint 36 and Earlier)

The following are **established** (control-confirmed or measured in Sprint 36) and are NOT open unknowns — they are the de-risked premises Sprint 37 builds on:

- **The markov emission is PROVEN** — S36 Day 2 drove `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16 (Mechanism C) and the cold MCP solved to the reference **2401.577 + match**. The open part is the leak-free derivative-structure discriminator (Unknown 1.2). (`SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md`)
- **The ganges `$141`/`$145`/`$149` cascade fixes are VERIFIED working** — S36 Day 8 drove the cold compile's `$141`/`$145`/`$149` → 0. The open parts are `$66` (cold) + `rPower` (presolve). (`SPRINT_36/DAY8_P4_GANGES_BANK.md`, git `a8ff626c`)
- **The fawley `stat_bq` correction is control-VERIFIED** (`max|stat_bq|` 473 → 1.14e-13) — the open part is the emission-path relocate + the discriminator that avoids the markov leak. (`SPRINT_36/DAY4_FAWLEY_DEFER.md`)
- **The `_add_indexed_jacobian_terms` shared-function leak is a proven hazard** — the fawley Day-9 change leaked onto markov, and markov's Mechanism C leaked full-corpus (cesam/ferts/sroute). **Any change here needs the full-corpus (163-golden) leak gate — the 6-model cohort is NOT the risk set.** (`SPRINT_36/SPRINT_RETROSPECTIVE.md` §4)
- **`rPower` is the #1378/#1424 embedded-NLP-divergence class** — the `.l`-based power calibrations re-run non-idempotently under the presolve `$onMultiR` `$include`. (`SPRINT_36/DAY8_P4_GANGES_BANK.md`)
- **The fawley `--force` survey is NEGATIVE** (homotopy/multistart/optfile all MS-5) — the +Solve is a Sprint-38 consultation, not the current scaffold. (`SPRINT_36/DAY11_P5_CONSULTATION.md` §4)
- **camcge is MS-4 with a numéraire alone insufficient** (the two-nullspaces diagnosis) — the full three-part Walras redefinition is the Epic-5 gate. (`SPRINT_36/DAY11_P5_CONSULTATION.md` §3, `EPIC_5/CGE_DEGENERACY_SCOPING.md`)
- **P7 robustlp shipped** (the NA-guard de-allowlist; `_emit_nlp_presolve` NA-guards the presolve marginal→multiplier `.L` warm-start incl `_fx_`) — robustlp is v54-solvable + de-allowlisted (not a bucket; already counted). (`SPRINT_36/DAY10_P7_ROBUSTLP.md`, `docs/issues/ISSUE_1322_*.md`)
- **The GAMS demo license caps at 1000 rows** (v53 and v54) — turkey's 3,866-row solve is testbed-only; the 142-candidate re-baseline is demo-runnable; emit-level gates stay local.
- **The Case-c objective-gradient sign flip + `x.up=inf` stay BANNED** (control-refuted 4×).
- **Sprint 36 closed 108/93/75/135** (DB byte-unchanged since the anchor `78ceaead`; S36 close `935d94b7`).

---

## Template for New Unknowns

When adding unknowns during Sprint 37:

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

**Before Sprint 37 Day 1:**
1. Research and verify all Critical and High priority unknowns (18 total) via prep Tasks 2–10
2. Execute the markov + fawley + ganges controls (local) and the `/tmp` `CASE_A` / `max|stat_bq|→0` / cascade experiments; stand up the full-corpus leak harness (Task 3)
3. Update this document's Verification Results as each prep task completes
4. Adjust Sprint 37 scope if a Critical assumption is wrong (esp. Unknown 1.2 the discriminator, Unknown 1.3/7.1 the full-corpus leak gate, Unknown 2.3 `rPower`, Unknown 4.2 the fawley/markov collision, Unknown 6.1 testbed access)
5. Confirm zero Day-0 blockers at the Task-11 GO/NO-GO

**During Sprint 37:**
1. Reference this document daily
2. Add newly discovered unknowns (use the Template above)
3. Update verification results as features are implemented
4. Move resolved items to "Confirmed Knowledge"

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from `PREP_PLAN.md`) verify which unknowns. Each prep task's "Unknowns Verified" metadata mirrors this table.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints | 1.1, 2.1, 4.3, 5.1, 7.4 | Re-confirms the four proven-component fingerprints on current `main`: markov emission (1.1), ganges cascade (2.1), fawley control (4.3), sarf blow-up (5.1); + the PR25 floor recompute at anchor 75 (7.4) |
| Task 3: Full-Corpus (163-Golden) Leak-Verification Harness Design & Setup | 7.1, 1.3 | Stands up the full-corpus leak harness (7.1) — the gate the markov leak (1.3, jointly with Task 4) and every shared-function landing design against |
| Task 4: markov P1 — Derivative-Structure Discriminator Design | 1.2, 1.3, 1.4, 1.5 | The discriminator (1.2), the full-corpus leak gate (1.3, with Task 3), the methodology→genuine cold-solve (1.4), and the fawley co-existence (1.5, with Task 6) |
| Task 5: ganges/gangesx P2 — Cascade Re-Verification & Recovery Sequencing | 2.2, 2.3, 2.4 | The `$66` terminal (2.2), the `rPower` deep-class verdict (2.3), and the atomic sequencing + `$149`-half spillover (2.4); 2.1 is re-confirmed in Task 2 |
| Task 6: fawley P4 — Emission-Path Location & Discriminator Design | 4.1, 4.2, 4.4 | Locates the `qsb`/`pbal` emission path (4.1), rebuilds the predicate + markov co-existence (4.2), and scopes the +Solve H-b hand-off (4.4); 4.3 is re-confirmed in Task 2 |
| Task 7: sarf P5 — Symbolic-Emit Re-Architecture Design Refresh | 5.2, 5.3 | Validates the O(active=398) guarded emit under GAMS 54 (5.2) and the full-corpus-harness precondition + ordering (5.3); 5.1 is re-measured in Task 2 |
| Task 8: GAMS-54 v54 Re-Baseline Plan + turkey Testbed Procurement | 6.1, 6.2, 6.3 | The turkey testbed procurement (6.1), the full v54 re-baseline + re-pin decision (6.2), and the OBJ-GAP + residual-cohort scoping (6.3) |
| Task 9: Consultation Reply-Integration Prep + camcge Epic-5 Walras Gate Scoping | 3.1, 3.2, 3.3, 3.4 | The rocket reply integration (3.1), the mine question (3.2), the camcge three-part Walras Epic-5 gate (3.3), and the per-model-numéraire fallback scoping (3.4) |
| Task 10: Property-Fixture Catalog + Phase-0-Doc CI + Genuine-Floor Tracking | 7.2, 7.3, 7.4 | The Phase-0-doc CI enforcement (7.2), the two property fixtures (7.3), and the genuine-floor tracking recompute (7.4, with Task 2) |
| Task 11: Plan Sprint 37 Detailed Schedule | All (integration) | Integrates every verified unknown into the day-by-day schedule, the per-track REPLAN exits, and the Day-0 GO/NO-GO |

**Note:** every unknown (1.1–7.4) is verified by at least one prep task; the Critical unknowns (1.1, 1.2, 1.3, 2.1, 2.3, 4.2, 7.1) are front-loaded into Tasks 2–8 so they resolve before the fixture catalog (Task 10) and the schedule (Task 11).

> **Numbering note.** Unknowns are numbered per-category as `X.Y` (category.index). New unknowns discovered during the sprint append to their category (e.g. the next Category-1 unknown is `1.6`).

---

**Document Status:** Active — Pre-Sprint 37 (register complete; unknowns advance from `🔍 INCOMPLETE` to ✅ VERIFIED / ❌ WRONG during prep Tasks 2–11)
**Last Updated:** 2026-08-09
**Owner:** Sprint 37 Planning Team
**Review Frequency:** Daily during Sprint 37
