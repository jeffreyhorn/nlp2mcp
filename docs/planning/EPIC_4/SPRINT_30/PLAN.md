# Sprint 30 Detailed Schedule (Day 0 + Days 1–13)

**Sprint:** 30 (Weeks 25–26) — Sprint 29 Carryforward: Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD
**Budget:** ≤ 12 h/day, 168 h cap (14 × 12). Planned **~110 h** mid-estimate (~92 h if the REPLAN-prone tracks slip early, ~142 h if all 8 priorities PROCEED).
**Source:** `PROJECT_PLAN.md` §"Sprint 30" + the Sprint-30 prep outputs (Tasks 1–9).

---

## 1. Sprint 30 Goal

Land the Sprint-29 REPLAN'd carryforwards: the **head-domain-offset emit architecture** (mine, +1 Solve), **robert** (a *decoupled* objective-gradient genuine-floor +1 — see §3), the **rocket #1462 non-convex forcing** scaffold (+ a conditional +1 Solve), the **hhfair #1236 widened-VARIABLE** presolve fix (+1 Match if Case-b), the **#1385 sarf** symbolic runtime-guard cross-terms (+Translate), the **offset-alias #1111/#1112** cross-terms (polygon + himmel16, genuine-floor), the **camcge #1330 → Epic 5** Walras transformation (conditional +1 Solve), and the adjacent **Class-B CGE `stat_pz`** general-emit fix (genuine-floor). Extend the property-test catalog, re-baseline the Rolling-KPIs Match targets, and scaffold the solution-forcing harness for the Sprint-31 PATH consultation.

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 30")

- **Solve:** ≥ 109 (from 107; the +2 headline target is **mine** [P1] + **rocket** [P2], but **both are conditional — REPLAN-prone**, not firm (§3); camcge is a further conditional +1). The PROJECT_PLAN's "+2 firm" label predates the Task-6 assessment, which found mine (Medium-High) and rocket (High) REPLAN-prone — so Solve ≥ 109 is the most REPLAN-sensitive KPI, while the genuine-floor lift (≥ 72) is the robust deliverable.
- **Match:** maintain ≥ 92 as-measured; **genuine floor 69 → ≥ 72** (robert [P1] + hhfair [P3, if Case-b] + polygon/himmel16 [P5] + Class-B CGE [P7] convert warm/methodology matches into genuine cold matches).
- **model_infeasible:** ≤ 5 (from 7; −2 via mine + rocket; −1 more if camcge lands).
- **path_syntax_error** ≤ 8 · **path_solve_terminated** ≤ 5 · **Translate** ≥ 135 (stretch +1 via #1385 sarf) · **Parse** 142 · **Tests** ≥ 4,990 · **Determinism** byte-identical ×3 `PYTHONHASHSEED`.
- **Epic 5:** the camcge Walras drop-one-row + fix-numéraire transformation lands or is empirically proven.
- **Quality:** all gates pass; emit-touching PRs pass golden-staleness (PR26) + the presolve-divergence detector + the `--resolve-changed` checkpoint.

## 3. Sequencing Constraints (from the prep-task outputs)

- **⚠️ INVERTED Unknown 1.1 — the Task-3 P1 split (the single most important schedule input).** The banked premise "a correct head-offset fix converts **both** mine and robert" is **refuted** (`HEAD_OFFSET_ARCHITECTURE_DESIGN.md`). robert's bug is an **objective-gradient boundary-term drop** in `stat_s` (the #1447 family) — **NOT** the head-offset cross-term — cold-confirmed at 11025.0 by a control experiment. So **P1 splits into two independent tracks**: (a) **robert** — a LOW-risk, standalone objective-gradient fix (~2–4 h, convex LP, **no REPLAN branch**, genuine-floor +1), scheduled **early Day 1**; and (b) **mine** — the HIGH-risk, REPLAN-prone multi-site `comp_pr` head-offset re-derivation (~10–16 h), the actual "head-offset architecture," scheduled Days 6–7. The two share **no** code path.
- **Three REPLAN decision points (Task 6, `REPLAN_RISK_ASSESSMENT.md`), each with a firm part that lands regardless:**
  - **rocket (Day ~2–3, prior High):** PROCEED-to-scaffold (the P8 forcing scaffold is firm); rocket's +1 Solve **REPLANs to the Sprint-31 PATH consultation** if no emittable-GAMS lever converges (Task 4: no PATH-option config converges even from the NLP optimum). Firm part: the scaffold + the hand-off.
  - **mine (Day ~6–7, prior Medium-High):** PROCEED the coordinated 3-site `comp_pr` fix if the cold LCP → MS 1 within budget; **REPLAN mine (not robert)** to a Sprint-31 head-offset-architecture workstream if a 4th site surfaces or the Day-7 cascade persists. Freed ~10–16 h → Class-B / offset-alias genuine-floor. robert (genuine-floor) lands regardless.
  - **camcge (Day ~11, prior Medium):** PROCEED if drop-one-`lmequil(lc_drop)`-instance + fix the consumption-weighted numéraire → **MS 1 at 191.7346** with the detection heuristic clean; **REPLAN to a per-model-numéraire declaration** (opt-in, still lands camcge) if the auto-heuristic false-flags. Firm part: the Class-B `stat_pz` fix (P7, distinct).
- **Solve ≥ 109 is the most REPLAN-sensitive KPI** (needs *both* mine and rocket). The genuine-floor lift (robert / Class-B / offset-alias / hhfair-if-Case-b) is **robust** even under a triple-REPLAN.
- **Day-0-traced fix surfaces (PR24):** every banked `file:line` is a hypothesis to re-confirm Day 0 (Sprint 29 proved the hhfair `$141` attribution wrong — the real blocker was `$184`). **Reuse, don't rebuild** the Sprint-29 tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed`) per `TOOLING_READINESS_AUDIT.md` — the one *optional* ≤1h harness extension (head-label warm-start) is non-blocking (the cold-solve control is the standing method for head-offset localization).

---

## 4. Day 0 — Kickoff + Day-0 Traces (≤ 6 h)

- Confirm the Day-0 baseline = Sprint 29 final (`BASELINE_METRICS.md`; the committed DB recomputes to **Solve 107 / Match 92 / model_infeasible 7 / Translate 135**). **Verify** `git diff <S29-close SHA>..HEAD -- src/ scripts/` is empty before skipping the retest (Unknown 8.2); if non-empty, run a fresh retest.
- **Day-0 traces (PR24)** for the lead + REPLAN-prone tracks — fill each Phase-0 gate's `Traced Fix-Surface (Day-0)` `file:line`:
  - **robert** (objective-gradient `stat_s`): re-run the cold-solve control (`stat_s`-patch → 11025.0; the harness top `stat_x` is the same-index transfer artifact, `TOOLING_READINESS_AUDIT.md` Tool 1).
  - **mine** (`comp_pr` 3-site head-offset): `kkt_residual.py` (CASE_B, `stat_x(4,1,1)` 1.33, CONSISTENT) + the cold-INFES-by-row histogram (is the site set complete or does a 4th bound-row site surface?).
  - **rocket** (Case-c): confirm the residual is clean at the NLP point; stand up the forcing-scaffold plumbing.
  - **hhfair** (`$184` widened-VARIABLE): reproduce the residual-emit compile blocker (first error `$184`, not `$141`).
  - **Class-B** (`stat_pz`): the harness cluster sweep is banked (Task 9: irscge/lrgcge/moncge all rel 1.00, CONSISTENT) — re-confirm on Day 0.
  - **polygon/himmel16, camcge, sarf**: confirm the banked surfaces.
- **PR25 Day-0 tally:** restate genuine 69 / methodology ~23; firm headline path = robert + Class-B + offset-alias + hhfair-if-Case-b (genuine floor → ≥ 72); the +2 Solve (mine + rocket) is REPLAN-gated.
- **Est ~6 h.** **Risk:** the prep surfaces are hypotheses — the traces are why Day 0 exists.

## 5. Day 1 — Priority 1a: robert objective-gradient fix (firm genuine-floor, decoupled) (~7 h)

- **The de-risked, decoupled half of P1 (Task 3).** Land the **objective-gradient boundary-term fix** in robert's `stat_s`: drop-in `- misc("res-value",r)` at the horizon end (`ord(tt)=card(tt)`) + guard `misc("storage-c",r)` to the `t(tt)` subset — the #1447 objective-term-scoping family, in the objective-gradient emit (`src/ad/gradient.py` `find_objective_expression` / `src/kkt/stationarity.py`), **NOT** the head-offset builder. **Do NOT touch robert's `stat_x`** (`nu_sb(r,tt)` is already correct).
- **Cold-confirm** robert → MODEL STATUS 1 at **profit 11025.0** (= NLP optimum, genuine cold match; convex LP ⇒ no non-convexity, **no REPLAN branch**). +1 genuine floor (methodology → genuine cold).
- **Blast-radius (Task 9 for the family):** the "terminal stock valued at res-value" pattern is common — byte-scan the corpus; `--resolve-changed` GO. Start the **P8 head-offset property fixture** groundwork.
- **Verifies:** 1.1 (absorbs the inversion), 1.4. **PR** (emit-touching). **Est ~7 h.**

## 6. Days 2–3 — Priority 2: rocket #1462 non-convex forcing scaffold (REPLAN-gated Day ~2–3) (~12 h)

- **Day 2 — the P8 forcing scaffold (firm, lands regardless):** build the `--force <strategy>` driver + MODEL-STATUS reporter (the stable Sprint-31 entry point, `NONCONVEX_FORCING_SURVEY.md` §4) wrapping `Solve mcp_model using MCP;` — homotopy/continuation + multi-start `.l`-perturbation + optional emitted PATH `optfile`. Validate the plumbing on rocket (it *runs* the levers).
- **Day 3 — the rocket REPLAN decision (Unknown 2.1/2.2, prior High):** drive the emittable-GAMS levers (homotopy/multi-start — the ones Task 4 did **not** exhaustively probe). **PROCEED** if any scaffold strategy reaches MS 1/2 at 1.0128 (+1 Solve); **REPLAN rocket's +1 Solve to the Sprint-31 PATH consultation** (the concrete question: which PATH option set / regularization schedule / reformulation converges the division-by-variable optimal-control MCP; Task-4 evidence: INFES 477 → 382 but no config converges). The scaffold + hand-off land regardless; freed tuning budget → scaffold hardening + P3 hhfair.
- **Verifies:** 2.1, 2.2, 8.3. **REPLAN exit explicit.** **PR. Est ~12 h (~6/day).**

## 7. Day 4 — Priority 3: hhfair #1236 widened-VARIABLE presolve fix (~10 h)

- **Generalize #1449 to the widened-VARIABLE case (Task 9 Part D).** hhfair's blocker is `$184` (source `n(t)` vs MCP-widened `n(tl)` for the live nonlinear-stat coefficient `n`); the parameter `__pw`-companion fix does not transfer → add a **companion-variable + value-coupling** emit path. **Blast-radius:** the #1449 widened-**parameter** presolve cohort = **4 models** (cclinpts/chain/otpop/rocket) must stay **byte-identical** (byte-scan + `--resolve-changed` GO); only hhfair's golden changes.
- **Then read the CES-mismatch verdict (Unknown 3.1/3.2):** once `$184` clears and the residual MCP compiles, run `kkt_residual.py`. **PROCEED** to the CES/product `stat_*` fix on a localizable **Case-b** row (+1 Match — the last live objective-mismatch target); **REPLAN to Sprint 31** if the post-compile mismatch is inherent non-convexity (the `prod(t,u(t)**ufact(t))` CES nest).
- **Verifies:** 3.1, 3.2, 3.3. **PR. Est ~10 h.**

## 8. Day 5 — Checkpoint 1 + Priority 7 (Class-B `stat_pz`) start (~10 h)

- **Checkpoint 1:** `--resolve-changed --since-commit <Day-0 SHA>` re-solve of the changed-golden set + golden-staleness + the **PR25 re-baseline** recompute (genuine/methodology, if any methodology change landed). GO/NO-GO: any changed-golden model moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort) → investigate before proceeding.
- **P7 Class-B `stat_pz` start (genuine-floor, one-fix-several):** the general-emit **coefficient** fix on the `pz`-referencing Jacobian-transpose cross-term (`src/kkt/stationarity.py` / `src/ad/constraint_jacobian.py`). Task 9 confirmed irscge/lrgcge/moncge all rel **1.00** (identical missing-unit-coefficient fingerprint) → **one fix converts all three**; stdcge (`stat_epsilon` 2.0) a probable variant. Harness Case-a (residual → 0) is the acceptance; genuine-floor (all warm-match already).
- **Verifies:** 7.1. **Re-baseline check explicit. Est ~10 h.**

## 9. Days 6–7 — Priority 1b: mine — head-domain-offset architecture (REPLAN-gated Day ~6–7) (~14 h)

- **The REPLAN-prone half of P1 (the actual head-offset architecture, prior Medium-High).** The coordinated 3-site index-map re-derivation: (1) `comp_pr` head-var emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve`), (3) the landed `stat_x` cross-term — a **single shared head-offset index-map helper** parameterized by (head-offset δ on `l`, parameter offsets `li(k)`/`lj(k)` on `i,j`), applied atomically. mine is a convex LP (monotone LCP) ⇒ the cold `x → 4e10` **is** the `comp_pr` LCP residual; a correct 3-site emit must drive it to 0.
- **Day 6:** the shared index-map helper + Sites 1–2. **Day 7 — the mine REPLAN decision:** does the coordinated fix drive the cold LCP to MS 1? **PROCEED** (+1 Solve, mine `model_infeasible → model_optimal`) if yes; **REPLAN mine to a Sprint-31 head-offset-architecture workstream** if the cold-INFES shows a 4th bound-row site or the Day-7 `ne`/`se`/`sw` cascade persists (each fixed site exposes the next). **robert is unaffected** (the split protects it). Freed ~10–16 h → P7 Class-B / P5 offset-alias genuine-floor.
- **Verifies:** 1.1, 1.2, 1.3. **REPLAN exit explicit. PR (atomic — a partial 3-site fix = no Solve gain). Est ~14 h (~7/day) — the heaviest mid-sprint block.**

## 10. Day 8 — Priority 5: offset-alias cross-terms #1111/#1112 (polygon + himmel16) (~10 h)

- **Coordinated fix, gated to the offset-alias shape (Task 9 Part B; genuine-floor — both match warm).** **polygon** = the successor-offset objective cross-term (`_diff_varref` / the `_partial_collapse_sum` non-circular-offset branch, the reverted representative-selection) **+** the `distance(i,j)` **constraint-Jacobian second-index symmetry** (`constraint_jacobian.py` — the dropped `r(j)` term); **land both together** (neither alone matches — the Day-5-revert coupling). **himmel16** = distinct: the cyclic `i++1` cross-term is *present*, so the fix is the objvar-gradient-**sign** reconciliation (`_diff_varref(circular=True)` branch + the dual-transfer sign).
- **Property fixtures (P8):** enable `shape8_offset_alias_successor` (drop the xfail-strict when the polygon fix lands — the completion gate); add a numeric assertion to `shape7_offset_alias_cyclic` when the himmel16 sign fix lands.
- **REPLAN-gated (Unknown 5.2):** PROCEED if a tight shape-gate makes each correct; **REPLAN to Sprint 31** (#1111/#1112 AD-engine core) only if it needs general alias differentiation. **Verifies:** 5.1, 5.2, 5.3. **PR. Est ~10 h.**

## 11. Days 9–10 — Priority 4: #1385 sarf symbolic cross-terms + Checkpoint 2 (~13 h)

- **The atomic symbolic runtime-guard cross-term emit (Task 9 Part A).** Two coupled sites: (1) extend `src/ad/index_mapping.py` (`_is_blowup_dynamic_subset_equation`) from srpchase's **1-D** to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`, `equipb1(m,t)$equipposs`, `equipb2(n,t)$equipposs`); (2) a **new symbolic cross-term emit path** in `src/kkt/stationarity.py` differentiating each body **once** parametrically in `(g,t,m,n)` (the banked 6-guarded-term `stat_task` derivation, `$taskposs`/`$equipposs` guards, **no set-name multiplier indices** — the Day-4 failure mode). **Atomic** (re-emit + cross-terms together).
- **Tractability gate (Unknown 4.2):** the emit must be **O(constraints), not O(instances)** (the counts are 384+648+120 = 1,152). Time `sarf_mcp.gms`; **PROCEED** if it emits under the translate budget (+Translate, sarf `translate_failure → translate`); **REPLAN to Sprint 31** if the symbolic re-emit re-triggers the per-instance enumeration (the timeout).
- **Day 10 — Checkpoint 2:** `--resolve-changed` re-solve + golden-staleness + PR25 tally. **Verifies:** 4.1, 4.2. **PR. Est ~13 h (~6.5/day).**

## 12. Day 11 — Priority 6: camcge → Epic 5 Walras transformation (REPLAN-gated Day ~11) (~10 h)

- **The Epic-5 CGE-domain preprocessing transformation (Task 7; PROCEED-conditional, prior Medium).** Drop **one** redundant market-clearing row *instance* `lmequil(lc_drop)` (Walras' law ⇒ rank deficiency exactly 1 — **not** the whole `lc` family) + fix the consumption-weighted numéraire `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` (camcge has **no `cpi`**). Guard with the S1∧S2∧S3 degeneracy detector (pass-through default — never transform a well-posed model).
- **The empirical gate (Unknown 6.1/6.2):** **PROCEED** if the transformed camcge reaches **MODEL STATUS 1 at omega 191.7346** with a non-singular basis **and** the detector flags only camcge across the cohort (irscge/lrgcge/moncge/stdcge); **REPLAN to a per-model-numéraire declaration** (opt-in, still lands camcge's +1 Solve — camcge is the sole inherent Walras case) if the auto-heuristic false-flags. **Verifies:** 6.1, 6.2, 6.3. **PR. Est ~10 h.**

## 13. Day 12 — Priority 7 finish + Priority 8 infrastructure + REPLAN-slack (~10 h)

- **P7 Class-B finish:** verify the `stat_pz` coefficient fix converts irscge/lrgcge/moncge (residual → 0); document the cold-convex Case-c residue disposition for Sprint 31. (stdcge/marco: land if the same path covers them, else document.)
- **P8 infrastructure:** finalize the property-test catalog extension (the head-domain-offset fixture + the enabled `shape7`/`shape8`); apply the **PR25 re-baseline** to the stale Rolling-KPIs Match targets (S31–S33 off the ≥64% line); finalize the **solution-forcing harness scaffold** + a CONTRIBUTING/Phase-0 note (the Sprint-31 hand-off).
- **REPLAN-slack absorption:** whatever the mine/rocket/camcge REPLANs freed re-allocates here (more Class-B / offset-alias genuine-floor per the Task-6 reallocation). **PR. Est ~10 h.**

## 14. Day 13 — Final Retest + Closeout (~8 h, tight)

- **Full pipeline retest** under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 29 → 30 metrics comparison; **PR25 genuine-vs-methodology re-baseline** recomputed (genuine floor → ≥ 72 target).
- **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; `SPRINT_RETROSPECTIVE.md` authored; Sprint-31 carryforwards filed (mine if REPLAN'd, rocket PATH consultation, camcge per-model declaration if REPLAN'd, #1111/#1112 if REPLAN'd). **Est ~8 h.**

---

## 15. Budget Summary

| Day(s) | Work | Est (h) |
|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) | ~6 |
| 1 | P1a robert objective-gradient fix (firm genuine-floor, decoupled) | ~7 |
| 2–3 | P2 rocket forcing scaffold + REPLAN decision | ~12 |
| 4 | P3 hhfair widened-VARIABLE `$184` fix + CES verdict | ~10 |
| 5 | Checkpoint 1 + P7 Class-B `stat_pz` start | ~10 |
| 6–7 | P1b mine head-domain-offset architecture (REPLAN-gated) | ~14 |
| 8 | P5 offset-alias (polygon + himmel16) | ~10 |
| 9–10 | P4 #1385 sarf symbolic cross-terms + Checkpoint 2 | ~13 |
| 11 | P6 camcge → Epic 5 Walras transformation (REPLAN-gated) | ~10 |
| 12 | P7 finish + P8 infra + REPLAN-slack | ~10 |
| 13 | Final retest + closeout | ~8 |
| **Total** | | **~110 h** (mid; ~92 h if P1b/P2 REPLAN early, ~142 h if all PROCEED) |

**Fits the 168 h cap** with ≥ 58 h slack at the mid-estimate; **no day > 12 h** (heaviest ~7 h/day across the Days 6–7 mine block). The lower bound assumes the REPLAN-prone tracks (P1b mine, P2 rocket +1 Solve) slip per Task 6; the **firm parts land regardless** — robert genuine-floor, the forcing scaffold, hhfair-if-Case-b, offset-alias, Class-B, camcge-declaration-fallback.

## 16. Phase 0 Coverage Audit (PR20 + PR24)

All 8 implementation tracks have a Phase-0 gate authored/refreshed in prep (Task 5): `docs/issues/ISSUE_{1443,1462,1236,1385,1146,1143,1330}_*.md` + `docs/issues/ISSUE_robert_objgrad_boundary_term.md` + `docs/issues/ISSUE_classB_cge_stat_pz.md`. Each gate's `Traced Fix-Surface (Day-0)` line is re-confirmed Day 0 before any `src/`. (robert has its own gate — decoupled from mine's #1443; camcge #1330 is the Epic-5 transformation.)

## 17. Known Unknowns Status Snapshot

All **25** Sprint-30 prep unknowns are **✅ VERIFIED** (or ❌ WRONG with a correction) after Tasks 1–9. The schedule absorbs the three that **INVERTED / returned WRONG**:
- **Unknown 1.1 (❌ WRONG — robert does NOT generalize to mine):** absorbed by the **P1 split** — robert Day 1 (objective-gradient, decoupled, firm genuine-floor); mine Days 6–7 (head-offset architecture, REPLAN-prone).
- **Unknown 1.4 (❌ WRONG — `nu_sb(r,tt+1)` is not robert's fix):** absorbed — Day 1 lands the `stat_s` objective-gradient fix, not the `stat_x` cross-term.
- **Unknown 2.2 (rocket = intrinsic non-convergence, PATH-side):** absorbed by the **rocket REPLAN** (Days 2–3) — the scaffold is firm, the +1 Solve hands off to the Sprint-31 PATH consultation.

## 18. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| Solve ≥ 109 misses (needs mine + rocket, both REPLAN-prone) | Honest projection: the +2 Solve is REPLAN-gated; the genuine-floor lift (≥ 72) is the robust deliverable. Task-6 reallocation redirects freed budget to genuine-floor. |
| mine 3-site fix exposes a 4th site (Day-7 cascade) | Explicit REPLAN mine → Sprint-31 head-offset architecture; robert (genuine-floor) lands regardless. |
| rocket resists every emittable-GAMS lever | The forcing scaffold + the PATH-consultation hand-off are the firm deliverable (Task 6 prior High → likely defers). |
| camcge auto-heuristic false-flags a well-posed model | Per-model-numéraire declaration fallback still lands camcge's +1 Solve (sole inherent case). |
| #1385 symbolic re-emit re-triggers the translate-timeout | The O(constraints) tractability gate (Day 9); REPLAN to Sprint 31 if it re-enumerates. |
| Day over-pack (Sprint 27 Day-12 lesson) | No day > 12 h (heaviest ~7 h/day in the mine block); Day 12 P7-finish/infra/slack is absorptive, not a hard commitment. |

## 19. Related Documents

- `PROJECT_PLAN.md` §"Sprint 30" · `KNOWN_UNKNOWNS.md` · `BASELINE_METRICS.md` · `HEAD_OFFSET_ARCHITECTURE_DESIGN.md` · `NONCONVEX_FORCING_SURVEY.md` · `REPLAN_RISK_ASSESSMENT.md` · `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` · `TOOLING_READINESS_AUDIT.md` · `BACKLOG_FIX_SURFACE_ANALYSIS.md` · `prompts/PLAN_PROMPTS.md`
