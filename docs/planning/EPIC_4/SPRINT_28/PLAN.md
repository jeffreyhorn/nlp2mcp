# Sprint 28 Detailed Schedule (Day 0 + Days 1–13)

**Sprint:** 28 (Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling)
**Budget:** ≤ 12 h/day × 14 days = 168 h cap; estimated work 101–149 h (lower bound assumes the diagnosis-heavy tracks P4/P5/P6 partially slip).
**Risk:** HIGH (three REPLAN-prone diagnosis tracks).
**Authored:** Sprint 28 Prep Task 10, integrating Tasks 1–9.

---

## 1. Sprint 28 Goal

Land the Sprint 27 Solve/Match carryforwards and build the diagnostic + CI tooling the Sprint 27 retrospective recommended. Push **Solve 105 → ≥ 110 (stretch; +4 firm/conditional → 109)** and **Match 62 → ≥ 65 (+3 firm)**. See `PROJECT_PLAN.md` §"Sprint 28".

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 28")

- **Solve** ≥ 110 (stretch; firm path to 109 = mine + camshape + otpop firm + camcge conditional); **Match** ≥ 65 (+3: otpop + cclinpts + kand).
- **model_infeasible** ≤ 5 (−3 via camshape/otpop/mine); **path_syntax_error** maintain ≤ 8; **path_solve_terminated** ≤ 5; **Translate** ≥ 135; **Parse** ≥ 142.
- **Tests** ≥ 4,800; **Determinism** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12).
- **Tooling:** golden-staleness CI live + drift cleared; KKT-residual harness landed + referenced in the Phase-0 template; divergence detector + AD cross-term property tests CI-wired.
- **Process:** PR24 + PR25 codified (✅ landed in prep, Task 3).
- **Quality:** all gates pass; fixes have regression tests; emit-touching PRs carry regenerated `.gms` diffs (PR14) and pass the golden-staleness check (PR26).

## 3. Sequencing Constraints (from the prep-task outputs)

- **PR24 (Task 3):** every carryforward fix surface is a **Day-0-trace hypothesis** — established by a Day-0 trace, never trusted from the prep doc; Phase-0 PROCEED cites the *traced* surface.
- **Front-load the KKT-residual harness (P9, Days 1–3, Task 4):** it is the Case-(a/b/c) instrument for P1/P2/P5 — build it before the diagnoses that consume it.
- **Diagnosis-heavy tracks gated on Task-6 REPLAN signals (Task 6):** #1387 (anchor architectural⇒REPLAN), #1390 (Case-c⇒REPLAN), camcge (inherent-degeneracy⇒Epic-5). Each carries an explicit Sprint 29 exit so a slip is planned, not a surprise.
- **PR25 projection discipline (Task 2):** only genuine bucket-to-success deltas count; the firm tally is Solve +3 (mine/camshape/otpop) + camcge conditional, Match +3 (otpop/cclinpts/kand).
- **Golden refresh first (Task 7):** land the 4-file presolve-golden refresh at Day 0 so the new CI gate starts clean.
- **Infra as lower-risk fill (P8/P10):** interleave after the firm carryforwards so the schedule has REPLAN slack.

---

## 4. Day 0 — Sprint Kickoff + Day-0 Traces (≤ 8 h)

- Confirm the Day-0 baseline = Sprint 27 final (`BASELINE_METRICS.md`; reuse the committed DB — no fresh 4 h retest unless `main` changed).
- **One-time golden refresh (Task 7):** `make regen-goldens` → commit the 4 drifted presolve goldens (camshape/cesam/fawley/korcge) as a single reviewable commit, separate from any fix.
- **Day-0 traces (PR24)** for the firm carryforwards (mine/camshape/otpop) and the diagnosis-heavy three (cclinpts/kand/camcge): instrument the candidate surfaces, emit each `<model>_mcp.gms`, locate the offending row; record the **traced** `file:line` in each Phase-0 gate's `Traced Fix-Surface (Day-0)` line.
- **PR25 Day-0 projection tally:** restate the firm Solve/Match deltas (genuine vs bucket-forward) as the sprint's reference.
- **Est:** ~8 h. **Risk:** the prep-doc surfaces may be wrong (Sprint 27: 4×) — the traces are why Day 0 exists.

## 5. Days 1–3 — Priority 9: KKT-Residual Verification Harness (front-loaded) (~10–14 h)

Build `scripts/diagnostics/kkt_residual.py` per `PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`: CLI (`<model.gms> [--gdx] [--tol] [--json] [--no-cold-start]`), the dual-transfer mechanism (nu/lam/piL/piU + the inequality→`comp_*` generalization, with the constraint-row consistency self-check), the Case-(a/b/c) verdict, JSON+human output; reference it from the Phase-0 template (PR27).

- **Validation against known cases (acceptance):** launch → Case a; camshape → Case b (`stat_r('i1')` ≈ 396); cclinpts → Case c (max\|r\| = 5e-8, cold PATH diverges). All three must reproduce.
- **Per-day:** Day 1 — CLI + dual-transfer mechanism + the constraint-row self-check; Day 2 — Case-(a/b/c) verdict + JSON/human output + `--gdx`; Day 3 — validate against launch/camshape/cclinpts + reference from the Phase-0 template + open the PR.
- **Verifies Unknowns:** 9.1, 9.2, 9.3 (+ unblocks 1.1/2.1/5.1 diagnoses).
- **Est:** ~12 h over 3 days (~4 h/day, leaving slack). **Risk:** dual-transfer correctness (Unknown 9.1) — the constraint-row self-check is the guard.

## 6. Day 4 — Priority 1: #1224 mine — parameter-valued-offset cross-term (~10–14 h budget) (≤ 11 h)

- Phase-0 gate (`ISSUE_1224`): harness on mine → expect **Case b** at `stat_x(l,i,j)` (the non-inverted `lam_pr`); confirm the traced surface; implement the inverted-offset shape (`sum(k, lam_pr(k,l,i-li(k),j-lj(k))) − sum(k, lam_pr(k,l-1,i,j))`); check boundary cells (Unknown 1.3).
- **Target:** mine → MODEL STATUS 1 (**+1 Solve firm**). PR + emit-`.gms` diff (PR14) + golden-staleness check (PR26).
- **Verifies:** 1.1, 1.2, 1.3.

## 7. Day 5 — Checkpoint 1 + Priority 2: #1388 camshape (~10 h)

- **Checkpoint 1:** pipeline retest (`changed_emit_artifacts.py --since-commit <Day-0 SHA>`) + golden-staleness check; **PR25 tally** (genuine gains so far vs target).
- **P2 #1388 camshape:** harness → Case b (`stat_r('i1')` ≈ 396, post-#1424 warm-start valid); per-term `stat_r` fix at the traced surface (prep hypothesis `stationarity.py:1835`). **Target:** camshape MS 1, area ≈ 4.2841 (**+1 Solve firm**).
- **Verifies:** 2.1, 2.2, 2.3.

## 8. Days 6–7 — Priority 3: #1393 + #1335 otpop (~12–16 h)

- **#1393** (kdef Sum-collapse) then **#1335** (zdef `card(t)-ord(t)` cross-term), sequenced; both gate otpop. Harness dual-transfer self-check first; structural greps (regen to `/tmp` first, per the Task-9 lesson). **Target:** otpop cost ≈ 4217.80 (**+1 Solve + 1 Match firm**).
- **Per-day:** Day 6 — #1393 kdef Sum-collapse fix + harness/structural verify; Day 7 — #1335 zdef cross-term (`_try_eval_offset` Approach B) + the combined otpop PR.
- **Verifies:** 3.1, 3.2, 3.3.

## 9. Days 8–9 — Priority 4: #1387 cclinpts (REPLAN-gated) (~12–18 h; heaviest, ~11 h Day 8)

- **Task-6 gate (decision pivot, Unknown 4.1):** re-run the Day-6 `_diff_sum` prototype on current `main`; trace the re-symbolization callers — **local ⇒ PROCEED; architectural ⇒ REPLAN to Sprint 29** (file a re-scoped Phase-0 successor). Sign-flip stays a misdiagnosis.
- If PROCEED: the three coupled changes land together (AD offset-enum + anchor fix + non-convex warm-start). **Target:** cclinpts rel_diff < 1% (**+1 Match firm-if-PROCEED**).
- **Per-day:** Day 8 — Task-6 decision pivot (re-run the prototype + caller trace) + (if PROCEED) start the three coupled changes; Day 9 — close (harness re-check + full-corpus byte-stability + PR), or complete the Sprint 29 REPLAN filing.
- **Verifies:** 4.1, 4.2, 4.3. **REPLAN exit explicit.**

## 10. Day 10 — Checkpoint 2 + Priority 5: #1390 kand (REPLAN-gated) (~10 h)

- **Checkpoint 2:** pipeline retest + golden-staleness + **PR25 tally**.
- **P5 #1390 kand (Task-6 gate, Unknown 5.1):** harness dual-transfer self-check (5.2) → **Case b (localizable row) ⇒ PROCEED; Case c (LP-recourse coupling) ⇒ REPLAN to Sprint 29**. Phantom-term collapse out of scope (inert). NLP-reference check first (5.3). **Target:** kand 2613.0 (**+1 Match firm-if-PROCEED**).
- **Verifies:** 5.1, 5.2, 5.3. **REPLAN exit explicit.**

## 11. Day 11 — Priority 6: camcge (REPLAN-gated) + Priority 7 cleanups (~10 h)

- **P6 camcge (Task-6 gate, Unknown 6.1):** harness → expect **Case c** (singular Jacobian, KKT structurally correct). PATH listing basis-singularity + Jacobian rank check → **single redundant Walras row + solution-preserving numéraire fix ⇒ PROCEED (+1 Solve conditional); else REPLAN to an Epic 5 inherent-degeneracy observation.**
- **P7 cleanups (Task 9):** #1374 robot `.l` dedup (isolatable, ~1–2 h) + #1400 message-field relativization (~1–2 h). **#1385 is a re-scope candidate** (atomic re-emit + symbolic-instance cross-terms, ~6–10 h, HIGH coupling) — land only if Day-11 slack allows; otherwise defer to Sprint 29.
- **Verifies:** 6.1, 6.2 (reconfirmed), 7.1, 7.2, 7.3.

## 12. Day 12 — Priority 8 (golden-staleness CI) + Priority 10 (divergence + property tests) (~10 h)

- **P8 (Task 7):** build `scripts/sprint_audit/check_golden_staleness.py [--fix]` + `.github/workflows/golden-staleness.yml` (parallel regen, `src/{ad,kkt,emit,ir}/` trigger) + `make regen-goldens` (the Day-0 refresh already cleared the drift). **Verifies:** 8.1, 8.2, 8.3.
- **P10 (Task 8):** build `scripts/diagnostics/check_presolve_divergence.py` (replay #1378 + #1424 as the acceptance test) + the 6 AD cross-term property tests (`tests/integration/emit/`, `@pytest.mark.integration`). **Verifies:** 10.1, 10.2, 10.3.

## 13. Day 13 — Final Retest + Closeout (~8 h, tight)

- **Final 3× `PYTHONHASHSEED` retest** (PR12 determinism guard) + the golden-staleness check.
- **PR25 final projection tally:** realized Solve/Match vs target, each delta labeled genuine vs bucket-forward.
- `SPRINT_LOG.md` final entry + `SPRINT_RETROSPECTIVE.md` + Sprint 29 carryforward filings for any REPLAN'd track (#1387/#1390/camcge/#1385 as applicable).

---

## 14. Budget Summary

| Day(s) | Work | Est (h) |
|---|---|---|
| 0 | Kickoff + golden refresh + Day-0 traces | ~8 |
| 1–3 | P9 KKT-residual harness (front-loaded) | ~12 |
| 4 | P1 #1224 mine | ~11 |
| 5 | Checkpoint 1 + P2 #1388 camshape | ~10 |
| 6–7 | P3 #1393+#1335 otpop | ~14 |
| 8–9 | P4 #1387 cclinpts (REPLAN-gated) | ~16 |
| 10 | Checkpoint 2 + P5 #1390 kand (REPLAN-gated) | ~10 |
| 11 | P6 camcge (REPLAN-gated) + P7 #1374/#1400 | ~10 |
| 12 | P8 golden-staleness + P10 divergence/property tests | ~10 |
| 13 | Final retest + closeout | ~8 |
| **Total** | | **~109 h** (lower bound; ~149 h upper if P4/P5/P6/#1385 all land) |

**Fits the 168 h cap** with ≥ 19 h slack at the lower bound; **no day > 12 h** (heaviest ~11 h, Day 8). The lower bound assumes P4/P5/P6 partially slip per Task 6 (~28–46 h at-risk).

## 15. Phase 0 Coverage Audit (PR20 + PR24)

All six carryforwards have a Phase-0 gate authored in prep (Task 5): `ISSUE_1224` (Solve refresh), `ISSUE_1388`, `ISSUE_1393` + `ISSUE_1335`, `ISSUE_1387`, `ISSUE_1390`, `ISSUE_1330` (camcge). Each gate's `Traced Fix-Surface (Day-0)` line is filled on Day 0 before any `src/` change.

## 16. Known Unknowns Status Snapshot + In-Sprint VERIFICATION Day

Day-0 entry state: **10 ✅ VERIFIED** (resolved pre-sprint) + **19 🟡 PARTIALLY VERIFIED (design scope)** (the fix surfaces are Day-0-trace hypotheses; the harness/CI tooling is built in-sprint). The 🟡 unknowns VERIFY on these days:

| Unknowns | Owning priority | VERIFY day |
|---|---|---|
| 9.1, 9.2, 9.3 | P9 harness | Days 1–3 |
| 1.2, 1.3 | P1 mine | Day 4 |
| 2.2, 2.3 | P2 camshape | Day 5 |
| 3.2, 3.3 | P3 otpop | Days 6–7 |
| 4.2, 4.3 | P4 cclinpts | Days 8–9 (or REPLAN) |
| 5.2, 5.3 | P5 kand | Day 10 (or REPLAN) |
| 7.1, 7.2, 7.3 | P7 cleanups | Day 11 |
| 8.2 | P8 golden-staleness | Day 12 |
| 10.1, 10.2 | P10 detector/tests | Day 12 |

(8.2 = the CI-runtime measurement; 10.1/10.2 = the detector replay + the property-test catalog build.)

## 17. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| Prep-doc fix surface wrong (Sprint 27: 4×) | PR24 Day-0 traces (§4); Phase-0 PROCEED cites the *traced* surface |
| Diagnosis-heavy track is architectural / non-convex | Task-6 REPLAN gates (§9/§10/§11) with explicit Sprint 29 exits — a slip is planned |
| Day over-pack (Sprint 27 Day-12 lesson) | No day > 12 h; #1385 is an optional Day-11 fill, not a commitment |
| Silent golden drift noise | golden-staleness check at every checkpoint (PR26) replaces ad-hoc reconciliation |
| Over-optimistic projection (Sprint 27 "+6 firm") | PR25 tally at Day 0 / Day 5 / Day 10 / Day 13 — genuine vs bucket-forward |
| Stale forward-looking prompts (Sprint 27) | PLAN_PROMPTS.md states only the day's scope; no claim about not-yet-done work |

## 18. Related Documents

- `PREP_PLAN.md`, `KNOWN_UNKNOWNS.md`, `BASELINE_METRICS.md` (Task 2)
- `PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` (Task 4), `PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` (Task 6)
- `PRIORITY_8_GOLDEN_STALENESS_DESIGN.md` (Task 7), `PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md` (Task 8), `PRIORITY_7_CLEANUPS_FIX_SURFACE.md` (Task 9)
- The six Phase-0 gates: `docs/issues/ISSUE_{1224,1388,1393,1335,1387,1390,1330}_*.md` (Task 5)
- `CONTRIBUTING.md` §"Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25)" (Task 3)
- `prompts/PLAN_PROMPTS.md` (per-day execution prompts)
