# Sprint 33 Detailed Schedule (Day 0 + Days 1–13)

**Created:** 2026-07-16
**Prep Task:** 11 (the final prep task — integrates Tasks 1–10)
**Budget:** 86–126 h work-items over 14 days (Day 0 + Days 1–13) at ≤ 12 h/day (168 h cap); Risk **HIGH**.
**Day-0 code anchor:** `ee51ed9e` (Sprint 32 close). **DB byte-anchor:** `4cbf8bff` (S31 close; DB unchanged since — a *distinct* anchor).

---

## 1. Sprint 33 Goal

Land the five Sprint-32 REPLAN'd carryforwards, each carrying a **Sprint-32 control-confirmed diagnosis** (`SPRINT_32/SPRINT_RETROSPECTIVE.md` §4), not just a pinned location. The three deepest are now **from-scratch AD/emit workstreams**: **P1 mine head-offset bound-active cross-term architecture** (#1443), **P2 sarf three-site symbolic `stat_task` emit subsystem** (#1385), **P3 fawley second-index `sameas`-guard generalization** (#1111/#1112). The two in-sprint **+Solve** movers — **P1 mine** and **P3 fawley** — lead, front-loaded across Days 1–5 so a REPLAN surfaces by the **Day-5 checkpoint** (the Sprint-32 lesson: front-loading mine Day 1 + camcge Day 5 surfaced both REPLANs by Day 5). **The one escalation Sprint 33 carries in (Task 9): P1 mine's banked premise was already refuted during prep** — Task 3 proved the emitted `stat_x` cross-term is *algebraically correct*, so mine enters on an **unproven third hypothesis** (H1 head-label multiplier-keying) at a **High** REPLAN prior, one fewer firm mover than Sprint 32 carried (camcge [P4] is now Epic-5-out-of-sprint).

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 33")

- **Solve 107 → +1 (108), stretch +2 (109) / ≥ 110** — conditional on P1 mine **or** P3 fawley (Task 9: P4 camcge is **Epic-5-deferred**, not an in-sprint Solve mover; P5 rocket is a **Sprint-34** conditional). **model_infeasible ≤ 7** maintain (−1 per landed mover).
- **Match maintain ≥ 92** as-measured (all-219 Match 95); **genuine floor 74 → +1 (75)** conditional on P1 **or** P3 COLD-matching an emit change — **NOT** presolve-methodology reclassification (**P5 delivers 0 floor**).
- **Translate 135 → +1 (136)** via #1385 sarf [P2]; **Parse 142** maintain; **path_syntax_error ≤ 8** maintain.
- **Tests** up from 5,085; **Determinism** byte-identical under ≥ 3 `PYTHONHASHSEED` (PR12).
- **The modal outcome is flat-KPI (Task 9)** — every mover is REPLAN-prone; the sprint's firm product is the de-risking (the control-confirmed root causes, the Epic-5 camcge scope, the Sprint-34 rocket hand-off), not a bucket.

## 3. Sequencing Constraints (from the prep-task outputs)

- **Front-load the two in-sprint +Solve movers (P1 mine Days 1–3 + P3 fawley Days 4–5)** so both close-or-REPLAN gates fire by the **Day-5 checkpoint** (Task 9). P2 sarf's REPLAN risk is retired earliest of all — its **O(active) probe is Day 0** (the cheapest verdict in the sprint); the emit build follows Days 6–9.
- **P1 mine is High-prior (Task 9):** the banked cross-term premise was **twice-refuted** (S32 Day-1 `N`-derivation + S33 Task-3 cross-term-correct). The fix is **multiplier-keying** (H1 head-label re-keying via the unused `head_domain_offsets` IR), **not** a term re-derivation. Run the H1 `/tmp` control **first** (Day 0).
- **P3 fawley is a SPLIT outcome (Task 9):** **H-a** (`max|stat_bq| → 0` → MS-1 @ 2899.25) = +1 Solve + conditional floor; **H-b** (emit closes but MS-5 @ 5739) = the **genuine cross-term correction ships anyway** (a *floor* lever) and the +Solve defers to the P5 forcing survey. Only a **regression onto the mbal / 1-D core** is a REPLAN.
- **The genuine-floor ramp is conditional** (Task 9 / Sprint-30 §3 / Sprint-32 §3): genuine floor +1 advances only via an **emit-changing** cold-match (P1 H1, or P3's genuine correction — which lands even under H-b), **NOT** via presolve-methodology reclassification — **P5 = 0 floor**.
- **P4 camcge is Epic-5-deferred (expected):** the in-sprint work is the `/tmp` full-redefinition gate that **confirms** the MS-4 deferral (the banked evidence: price-pin MS-4, 3+ sprints of MS-4 variants); step 1 already landed S32.
- **Reallocation order on any REPLAN (Task 9):** P6 (the failure-cohort re-triage — agreste scope-verify + the `path_syntax_error` 8-cohort) → P7 (property fixtures + genuine-floor tracking + the Epic-4 `SUMMARY` continuation) → the rocket [P5] forcing tail. The offset-alias generalization is **exhausted** (Task 10 — cpack et al. already solve; fawley promoted to P3).

## 4. Day 0 — Kickoff + Day-0 Traces + Control Probes (≤ 6 h)

- Confirm Day-0 = Sprint 32 close (`BASELINE_METRICS.md`: **Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / all-219 Match 95 / Tests 5,085**). **Verify** `git diff ee51ed9e..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest.
- **Day-0 traces (PR24)** — re-confirm each Phase-0 gate's Day-0 fingerprint (`PHASE_0_ACCEPTANCE_GATES.md` §1): mine (`kkt_residual.py` CASE_B `stat_x(3,1,1)` rel 2.37, duals CONSISTENT — **and** the Task-3 cross-term-correct finding: the residual is the 6 bound-active `c`-boundary rows only, interior at 0), sarf (the three enumeration sites + the 369K-vs-398-active count), fawley (CASE_B `stat_bq`, <code>max&#124;stat_bq&#124;</code> 473 → 18 [96%]), camcge (CASE_B `stat_mps` cleared by S32 step 1; the residual MS-4 Walras), rocket (Case-c clean at the NLP point — boundary `stat_ht`/`stat_step`).
- **The three control probes (Task 9 single-model validations / Task 8 gates):**
  - **P1 H1 `/tmp` control (run first — highest prior):** key `comp_pr`/`lam_pr` + the `stat_x` cross-term to the **head label `(k,l+1,i,j)`** via the unused `head_domain_offsets` IR on a scratch `mine_mcp_presolve.gms` → the harness reports **`N → 0` at ALL 6 bound-active rows AND unchanged (0) at every interior row** (`modelstat` asserted; **`x.up=inf` BANNED**) → presolve **MS-1 @ 17500**, before any `src/` change.
  - **P2 sarf O(active) probe:** confirm the sparsified `stat_task$taskposs` enumerates **398 active**, not 369,024 Cartesian — a lightweight count/scoping probe (the full timing gate is Day 7).
  - **P3 fawley localize-by-column `/tmp`:** re-confirm the Day-11 control (<code>max&#124;stat_bq&#124;</code> 473 → 18) and **localize the residual 18.47 by column** — the **H-a/H-b discriminator** (second-column gate-leak vs non-emit LP-convergence).
- **PR25 Day-0 tally:** restate genuine 74 / methodology (anchor 74); the genuine-floor → +1 conversion map (P1 H1 cold-match; P3's genuine cross-term correction — the firmest lever, lands even under H-b). **Docs/trace-only (no `src/`).**

## 5. Day 1 — Priority 1: mine H1 head-label multiplier re-keying (start) (~7 h)

- **The H1 head-label multiplier-keying (Task 3 — the cross-term is already correct).** Re-key `comp_pr`/`lam_pr` + the `stat_x` cross-term to the shifted head label `(k,l+1,i,j)` (where the NLP stores `pr.m`) via the currently-unused `head_domain_offsets` IR (`src/kkt/stationarity.py` — `_try_build_param_offset_crossterm:5712` + the multiplier keying; `src/ad/…` head-label multiplier plumbing). **Do NOT change the cross-term terms/signs** (refuted twice — S32 `N`-derivation + S33 Task-3). Gate to the head-offset-coupled case so the non-mine param-offset cohort (srpchase) stays byte-stable.
- **Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P1 (the Day-0 H1 `/tmp` warm-residual→0 at the 6 rows must have passed before src). **Emit-touching PR (WIP if incomplete). Est ~7 h.**

## 6. Day 2 — Priority 1: mine warm→cold verification (~7 h)

- **The warm-residual→0 gate (Unknown 1.2).** Re-run `kkt_residual.py data/gamslib/raw/mine.gms` after the H1 re-keying → **warm residual `N → 0` at all 6 bound-active rows, Case-a** (`modelstat` asserted), interior unchanged. Then the **presolve solve → MS-1 @ 17500** (+1 Solve; +1 genuine floor if it cold-matches). Confirm the S31 head-offset foundation guard tests stay green + the non-mine presolve goldens byte-stable (`--resolve-changed --since-commit ee51ed9e`).
- **Verifies (in-sprint):** the P1 gate. **Emit-touching PR. Est ~7 h.**

## 7. Day 3 — Priority 1: mine close-or-REPLAN (~6 h)

- **The deeper-coupling gate (Unknown 1.2, H3).** **PROCEED** (mine `model_infeasible → model_optimal`, +1 Solve; +1 genuine floor if cold-match) if the warm residual closes with no fresh residual and no interior perturbation. **REPLAN (prior High)** if H1 (and the H2 `d\c`-ring reconciliation) cannot drive `N → 0` without perturbing an interior row or regressing srpchase → file a **Sprint-34 deeper head-offset dual-architecture subsystem**; the cross-term-correct finding + the multiplier-coupling characterization + the S31 IR foundation (on `main`) hand off cleanly. Freed ~14–18 h → **P6 + P7** (Task 9 reallocation).
- **REPLAN exit explicit. PR. Est ~6 h.** *(P1 total ~20 h across Days 1–3.)*

## 8. Day 4 — Priority 3: fawley second-index `sameas`-guard generalization (start) (~7 h)

- **The general indexed cross-term `sameas`-guard path (Task 5 — NOT the 1-D polygon core).** Extend the diagonal-`sameas` logic (`src/kkt/stationarity.py` — `_build_sameas_guard:4623` / `_get_or_create_fresh_alias:4496` in `_add_indexed_jacobian_terms`) so **every** second-index `cfq` gets the `$(sameas(cfq__, cf))` restriction, covering the qsb/pbal 2-D cross-terms (`bq(c,cf)`). **Do NOT touch the 1-D core** (`_var_at_two_indices_complement:7291` — polygon/ps2) and **no mbal-term change**.
- **Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P3 (the Day-0 localize-by-column control identified the H-a/H-b split before src). **Emit-touching PR (WIP). Est ~7 h.**

## 9. Day 5 — Priority 3: fawley close-or-REPLAN + Checkpoint 1 (~7 h)

- **The H-a/H-b gate (Unknown 3.1/3.2).** Drive <code>max&#124;stat_bq&#124; → 0</code> (not 96%) at the warm point (`modelstat` asserted). **H-a — PROCEED (+1 Solve):** presolve → **MS-1 @ 2899.25** (+1 genuine floor if cold-match). **H-b — the emit still ships (a floor lever):** <code>max&#124;stat_bq&#124; → 0</code> yet MS-5 @ 5739 (non-emit LP-convergence) → the **genuine cross-term correction lands** (a cold-emit change → +genuine floor) and fawley's +Solve **hands to the P5 forcing survey**. **REPLAN only** if the generalization **leaks onto the mbal / first-index shape or regresses the 1-D polygon core** (correctness risk) → re-scope; freed ~6–12 h → P6/P7.
- **Checkpoint 1 (Day 5):** `--resolve-changed --since-commit ee51ed9e` re-solve of the changed-golden set (bucket-diff vs the committed DB) + golden-staleness + the PR25 re-baseline. **NO-GO** if any changed-golden model moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort). **Both in-sprint +Solve movers (mine + fawley) have now fired their PROCEED/REPLAN gates.**
- **Verifies (in-sprint):** the P3 gate + no-regression (Unknown 3.3). **REPLAN exit explicit. PR (emit-touching). Est ~7 h.** *(P3 total ~14 h across Days 4–5.)*

## 10. Days 6–9 — Priority 2: sarf three-site symbolic `stat_task` emit (~24 h)

- **The atomic three-site O(active) symbolic re-emit (Task 4).** Eliminate the 369,024-column materialization at **all three** sites, landed **atomically** (a partial = an inconsistent MCP): S1 the `acost3` body-differentiation (`src/ad/constraint_jacobian.py`), S2 the variable-column enumeration (`src/ad/index_mapping.py`), S3 the variable stationarity (`src/kkt/stationarity.py`) — replaced by **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation, Task-4-verified) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` over the **398 active** instances (a 927× reduction), **no set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure, commit `243fe578`; scan two greps — `nu_[[:alnum:]_]+\("` and `lam_[[:alnum:]_]+\("` — both empty).
- **The tractability gate (Unknown 2.1, Day 7).** The re-emit must be **O(active = 398), not O(369,024)** — time `sarf_mcp.gms` (target **seconds**, cf. srpchase's 1-D analogue ~2.9s current runner / 6.56s S32 runner; the failure is > 75 s). **PROCEED** (sarf `translate_failure → translate`, +1 Translate) if sub-budget; **REPLAN to Sprint 34** (a documented parametric-emit re-scoping — a 4th enumeration site / builder-pipeline materialization; freed ~8–16 h → P6/P7) if it re-triggers the timeout.
- **Day 9 close:** golden byte-stable (sarf's *new* `sarf_mcp.gms` golden — caught by the golden-staleness gate, since `--resolve-changed` diffs *existing* goldens) + deterministic ×3 `PYTHONHASHSEED`; `--resolve-changed --since-commit ee51ed9e` GO (sarf the only changed golden).
- **Verifies (in-sprint):** the P2 gate + the derivation completeness (Unknown 2.3). **REPLAN exit explicit. PR (emit-touching). Est ~24 h (~6/day).**

## 11. Day 10 — Priority 4 camcge Epic-5 gate + Priority 5 rocket/Case-c + Checkpoint 2 (~10 h)

- **P4 camcge Epic-5 `/tmp` gate (confirm the deferral — Task 6).** Run the `/tmp` prototype of the **full** dual-consistent redefinition (keep every market-clearing row + the consumption-weighted numéraire + **redefine the redundant market's dual via Walras' law**), checking the KKT **dual** side. **Expected: MS-4** (the banked evidence — price-pin MS-4, single-dual-pin MS-4, 3+ sprints of MS-4 variants) → **Epic-5-deferred** (camcge stays `model_infeasible`; the numéraire recipe + the S1∧S2∧S3 detector are the de-risked Epic-5 hand-off). **Promote to +1 Solve only if** the prototype unexpectedly reaches **MS-1 at omega 191.7346**. Step 1 already landed S32.
- **P5 rocket/Case-c forcing survey + submission (Task 7 — no emit fix, sign flip BANNED).** Re-confirm each Case-c model's residual is **clean at the NLP point** *before* any forcing (rocket boundary signature; hhfair/CGE `case_c_objdef`, `nu_obj=±1`). **Submit** the FINALIZED rocket PATH-consultation input to the Sprint-34 hand-off. Run the `--force {homotopy,multistart,optfile}` survey across hhfair + irscge/lrgcge/moncge — "a lever crosses" (global MS-1) = conditional +Match/+genuine; else **banked Case-c** (the modal outcome). **0 genuine floor.**
- **Checkpoint 2 (Day 10):** `--resolve-changed --since-commit ee51ed9e` re-solve + golden-staleness + the PR25 tally.
- **Verifies (in-sprint):** the P4/P5 gates (Unknowns 4.x/5.x). **PR (P4 docs unless the `/tmp` crosses to emit; P5 docs + the survey). Est ~10 h.**

## 12. Day 11 — Priority 6: failure-cohort re-triage + REPLAN-slack (~11 h)

- **P6 agreste scope-verify (Task 10 §2).** Inspect the agreste source for the **double-`solve`** scope (two `solve agreste maximizing yfarm using lp`, lines 294/298) BEFORE treating the CASE_B `stat_sales` rel 2.0 as an emit bug (the multi-solve-gate lesson). If the single-solve scope holds CASE_B → a factor-of-2 dropped-gradient Case-b (+Solve candidate, `--resolve-changed`-gated); if a driver artifact → **bank** (not a fixable emit bug).
- **P6 `path_syntax_error` cohort (Task 10 §2 — bonus back-half).** The 8 convex models whose emitted MCP fails at the PATH **compile** stage (clearlak/dinam/ganges/gangesx/indus/sample/turkey/turkpow) — scope the shared translate-syntax root; a single fix may recover several. Each `--resolve-changed --since-commit ee51ed9e`-gated + a golden-staleness check on the new goldens. (cesam/lnts stay banked Case-c — bilinear SAM / bilinear-`step`.)
- **REPLAN-slack absorption:** whatever the P1/P2/P3 REPLANs freed re-allocates here first (Task 9 order: P6 → P7 → the rocket tail).
- **Deliverable:** ≥ 1 model recovered (Solve/Match/genuine floor) OR the cohort re-triaged with banked diagnoses. **Verifies (in-sprint):** the P6 candidates (Unknowns 6.1/6.2/6.3). **PR (emit-touching if a candidate lands, else docs). Est ~11 h (heaviest day).**

## 13. Day 12 — Priority 7: infrastructure + REPLAN-slack (~8 h)

- **P7 property fixtures (Unknown 7.1) — each fail-before/pass-after, landing only once its fix landed:** **shape12** (head-offset bound-active — guards P1), **shape13** (sarf symbolic `stat_task` — guards P2), and a **new fawley 2-D second-index fixture** (guards P3, distinct from the 1-D shape10/11) → `tests/integration/emit/test_ad_crossterm_shapes.py`.
- **Genuine-floor tracking + checkpoint refresh (Unknowns 7.1/7.3):** recompute the PR25 **genuine-floor tracking** (re-baselined to **74**); refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites.
- **Epic-4 `SUMMARY.md` row-33 continuation (Unknown 7.3):** (1) **reconcile the theme cell** — row 33 currently reads "PATH author consultation & solution forcing" (that is **Sprint 34's** theme); Sprint 33's is "Sprint 32 REPLAN'd carryforwards"; (2) **fill the cells** in the rows-28–32 format {Theme / Headline KPIs / Firm landing(s) / REPLAN'd → carryforward}.
- **REPLAN-slack:** absorb residual freed budget per the Task-9 reallocation order.
- **Verifies (in-sprint):** the P7 infra (Unknowns 7.1/7.3). **PR (tests/ + docs). Est ~8 h.**

## 14. Day 13 — Final Retest + Closeout (~8 h)

- **Full pipeline retest** under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 32 → 33 metrics comparison; **PR25 genuine-vs-methodology re-baseline** recomputed (genuine floor anchor 74).
- **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; `SPRINT_RETROSPECTIVE.md` authored; the Sprint-34 carryforwards filed (mine if REPLAN'd → deeper head-offset dual subsystem; sarf if REPLAN'd → re-scoping; fawley +Solve → the P5 forcing tail if H-b; the camcge numéraire → Epic 5; the rocket PATH-consultation input → the Sprint-34 consultation; cesam/lnts Case-c; any un-landed P6 candidate). **Fill the SUMMARY row-33 cells (Day-12 continuation). Est ~8 h.**

---

## 15. Budget Summary

| Day(s) | Track | Est (h) |
|---|---|---|
| 0 | Kickoff + Day-0 traces + 3 control probes (P1 H1, P2 O(active), P3 localize) | ~6 |
| 1–3 | **P1 mine head-offset bound-active cross-term** (H1 re-keying; close-or-REPLAN Day 3) | ~20 |
| 4–5 | **P3 fawley second-index `sameas` generalization** (H-a/H-b; close-or-REPLAN + Checkpoint 1 Day 5) | ~14 |
| 6–9 | P2 sarf three-site symbolic `stat_task` emit (tractability gate Day 7) | ~24 |
| 10 | P4 camcge Epic-5 `/tmp` gate + P5 rocket/Case-c survey + Checkpoint 2 | ~10 |
| 11 | P6 failure-cohort re-triage (agreste scope + `path_syntax_error` 8-cohort) + REPLAN-slack | ~11 |
| 12 | P7 infrastructure (shape12/13/fawley + tracking + SUMMARY row-33) + REPLAN-slack | ~8 |
| 13 | Final retest (≥ 3 seeds) + closeout | ~8 |
| **Total** | | **~101 h** (mid; ~86 h if the deep tracks REPLAN early, ~126 h if all PROCEED) |

**Fits the 168 h cap** with ≥ 42 h slack at the mid-estimate; **no day > 12 h** (heaviest ~11 h on Day 11, the P6 failure-cohort + REPLAN-slack day). The per-priority sizings (`PROJECT_PLAN.md` §"Sprint 33"): P1 [18–24h] + P2 [20–28h] + P3 [12–18h] + P4 [10–16h] + P5 [8–12h] + P6 [8–14h] + P7 [6–10h] + retest [4h] = **86–126h**. The lower bound assumes the deepest from-scratch tracks (P1 cross-term architecture, P2 symbolic-emit subsystem) slip per Task 9; the **firm parts land regardless** — the mine multiplier-keying design + characterization, the sarf three-site O(active) design (or its re-scoping finding), the fawley genuine cross-term correction (even under H-b), the P4 Epic-5 recipe + detector, the P5 rocket scaffold + consultation input, the P6 banked diagnoses, the P7 infra.

## 16. Phase 0 Coverage Audit (PR20 + PR24 + PR27)

The three emit-touching tracks (P1 mine, P2 sarf, P3 fawley) each have a PROCEED/REPLAN gate in `PHASE_0_ACCEPTANCE_GATES.md` §1. Each gate's Day-0 fingerprint is re-confirmed Day 0 before any `src/` change; each cites `kkt_residual.py` (PR27) + a control-before-`src/` rule (P1 the H1 warm-residual→0 at the 6 bound-active rows; P3 the <code>max&#124;stat_bq&#124;</code>→0 localize-by-column; P2 the O(active=398) probe). P4 camcge is an Epic-5 `/tmp` gate (confirm the MS-4 deferral, no in-sprint emit); P5 rocket is a docs hand-off + forcing survey (no emit); P6 candidates each pass the `--resolve-changed --since-commit ee51ed9e` GO gate before landing. **`modelstat` is asserted before every objective read; `x.up=inf` is BANNED (mine); the objective-gradient sign flip is BANNED (Case-c, refuted 4×).**

## 17. Known Unknowns Status Snapshot

All 27 prep unknowns are resolved (Tasks 1–10): **25 ✅ VERIFIED, 2 ❌ WRONG** (1.1 the cross-term is *correct* / 1.2 no cross-term correction exists — both refuting the banked mine premise, re-scoping P1 to multiplier-keying). Coverage: the mine cross-term architecture (1.1–1.5), the sarf three-site O(active) emit (2.1–2.5), the fawley second-index generalization (3.1–3.4), the camcge Epic-5 Walras (4.1–4.4), the rocket/Case-c forcing (5.1–5.3), the P6 failure-cohort (6.1–6.3), the P7 infra (7.1–7.3). **No Critical/High unknown is `🔍 INCOMPLETE`** — no Day-0 blocker. The in-sprint gates that remain are the **execution** of each track's PROCEED/REPLAN gate (Days 3/5/7), not open prep unknowns.

## 18. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| Solve +1 misses (in-sprint movers = only {mine [P1], fawley [P3-H-a]}) | Honest projection (Task 9): both are front-loaded Days 1–5 so a REPLAN surfaces at Checkpoint 1; freed budget → P6 (agreste / `path_syntax_error` — possible replacement +Solve). P4 camcge is Epic-5-out-of-sprint; P5 rocket is Sprint-34. |
| P1 mine's H1 re-keying surfaces a deeper coupling (High prior — premise twice-refuted) | Explicit REPLAN mine → Sprint-34 deeper head-offset dual subsystem (Day 3); the cross-term-correct finding + the multiplier-coupling characterization + the S31 IR foundation hand off cleanly. Run the H1 `/tmp` control **first** (Day 0). |
| P3 fawley closes the emit but the MCP stays MS-5 (H-b) | **Not a REPLAN** — the genuine cross-term correction ships (a floor lever, a cold-emit change); only the +Solve defers to the P5 forcing survey. The Day-0 localize-by-column control discriminates H-a/H-b early. |
| P2 sarf symbolic re-emit re-triggers the translate timeout (a 4th site) | The O(active=398) probe (Day 0) + the tractability gate (Day 7) resolve it early; REPLAN → a documented re-scoping; +Translate deferred. |
| camcge Walras `/tmp` stays MS-4 (Epic-5 dual rank-deficiency) | **Expected** — camcge is Epic-5-deferred; the `/tmp` gate confirms the deferral; step 1 (on `main`) + the numéraire recipe + the S1∧S2∧S3 detector are the de-risked Epic-5 hand-off. No in-sprint `src/`. |
| genuine floor +1 counted from presolve-methodology | Task 9 / Sprint-32 §3: the floor advances only via an emit change (P1 H1 cold-match, or P3's genuine correction); **P5 is explicitly 0 floor**. |
| a P6 emit change regresses the 92-match / 107-solve guard | Each P6 candidate passes the `--resolve-changed --since-commit ee51ed9e` GO gate before landing (NO-GO → revert, no net loss). |

## 19. Related Documents

- `PROJECT_PLAN.md` §"Sprint 33" · `KNOWN_UNKNOWNS.md` · `BASELINE_METRICS.md` · `MINE_CROSSTERM_DESIGN.md` · `SARF_EMIT_SUBSYSTEM_DESIGN.md` · `FAWLEY_SECOND_INDEX_DESIGN.md` · `CAMCGE_WALRAS_DESIGN.md` · `ROCKET_CASEC_FORCING_PLAN.md` · `PHASE_0_ACCEPTANCE_GATES.md` · `REPLAN_RISK_ASSESSMENT.md` · `TOOLING_AND_BACKLOG_ANALYSIS.md` · `prompts/PLAN_PROMPTS.md`

---

**Document Created:** 2026-07-16
**Owner:** Sprint 33 Planning Team
**Status:** Sprint 33 is **GO for Day 0** — all 11 prep tasks complete; the schedule front-loads the two in-sprint +Solve movers (mine + fawley) so a REPLAN surfaces by the Day-5 checkpoint, with the honest modal-flat-KPI projection binding (P1 High-prior on an unproven H1; P4 Epic-5-out-of-sprint; P5 Sprint-34).
