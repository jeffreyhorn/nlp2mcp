# Sprint 31 Per-Day Execution Prompts

One self-contained prompt per day (Day 0 + Days 1–13). Each is derived from `../PLAN.md` and the Sprint-31 prep outputs. Run one per day.

## How to Use

Paste the day's prompt as the task. Each prompt names its objective, branch, Phase-0 gate, quality gate, and the PR + wait-for-review step. Branches: `planning/sprint31-dayN-<slug>`.

## Cross-Cutting Rules (every day)

- **PR24 (Day-0 traced fix surface):** the banked `file:line` is a *hypothesis* — re-confirm it with `kkt_residual.py` / a cold-solve control **before** any `src/` change. **The sign flip is BANNED for P5** (control-refuted 3× in Sprint 30).
- **Check the dual side (Sprint-30 camcge lesson):** any transform that drops/adds rows must reach the target on the KKT *dual* (a `/tmp` prototype to MS-1), not just the primal.
- **PR25 (projection discipline):** track genuine-floor vs methodology separately; re-baseline after any pipeline-methodology change. The genuine-floor ramp is *conditional* (Task 7).
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14), pass the golden-staleness check (PR26) + the presolve-divergence detector, and (Day 5+) the `--resolve-changed` checkpoint.
- **Quality gate (any `*.py` change):** `make typecheck && make format && make lint && make test` must pass before commit.
- **REPLAN honesty:** each REPLAN-gated day has a firm part that lands regardless; file the Sprint-32 carryforward on REPLAN.

---

## Day 0 Prompt — Kickoff + Day-0 Traces + Tractability Probes (~6 h)

Confirm Day-0 = Sprint 30 final (`../BASELINE_METRICS.md`: Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7 / Translate 135 / Tests 4,997). Verify `git diff ea4191dc..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest. Run the **Day-0 traces (PR24)** and re-confirm each Phase-0 gate's `Traced Fix-Surface (Day-0)` `file:line` (`../PHASE_0_ACCEPTANCE_GATES.md`): mine (`kkt_residual.py` → CASE_B `stat_x(4,1,1)` 1.33 + the cold-INFES-by-direction histogram), polygon (CASE_B `stat_theta(i12)` 0.492), camcge (CASE_B + cold MS-4 singular), hhfair (the inlined log-derivative `stat_u`), rocket (Case-c clean at the NLP point), sarf (the emit-timing). Then run the **three tractability probes:** (1) **P1 round-trip** — author + run `tests/fixtures/head_offset_ir_roundtrip.gms`, assert `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)`; (2) **P3 dual-consistent `/tmp` prototype** — hand-edit `camcge_mcp.gms` with the dual-consistent redefinition → reach MS-1 at omega 191.7346 (check the dual side); (3) **P5 hhfair ν_objective control** — confirm the current `stat_u` log-derivative gradient is emit-correct → hhfair is genuine Case-c (documented; sign flip BANNED), pivot P5 to the CGE cluster. Restate the PR25 tally (genuine 70 / methodology 22; the → ≥73 conversion map). Docs/trace-only (no `src/`). **No PR** (or a docs-only trace-notes PR).

## Day 1 Prompt — Priority 1 Phase 1: head-offset IR plumbing (~7 h)

Branch `planning/sprint31-day1-headoffset-ir`. Add `EquationDef.head_domain_offsets` (a per-position `IndexOffset` tuple, mirroring `declaration_domain` — `../HEAD_OFFSET_IR_PLUMBING_DESIGN.md`): the parser producer (`_domain_list_head_offsets` reusing `_process_index_expr`, replacing the bare `has_head_domain_offset` bool at `parser.py:3952`) + copy-through at the reconstructor sites (`sqr_reformulation.py:88/:108`, `complementarity.py:242`); `normalize` is a passthrough. **Phase-1 gate:** the round-trip fixture (`head_offset_ir_roundtrip.gms`) is green + the golden byte-diff shows **zero changes** (the field addition is inert until a consumer reads it — Unknown 1.4). **Phase-0 gate:** `docs/issues/ISSUE_1443_*.md` §P1. Quality gate + PR (src/ir/, tests/) + wait for review.

## Day 2 Prompt — Priority 1 Phase 2: shared 3-site helper (heaviest, ~11 h)

Branch `planning/sprint31-day2-headoffset-helper`. Build the **shared head-offset index-map helper** parameterized by (head-offset δ on `l`, param offsets `li(k)`/`lj(k)` from the body), called **atomically** by the three sites: (1) `comp_pr` head-var emission, (2) the `--nlp-presolve` dual transfer (`_emit_nlp_presolve`, `emit_gams.py:1354`), (3) the landed `stat_x` cross-term (`_add_indexed_jacobian_terms`/`stat_x`, `stationarity.py:5767`). mine is a convex LP ⇒ the cold `x → 4e10` is the `comp_pr` LCP residual. The three sites must apply the same map (a partial 3-site fix = no Solve gain — atomic). Quality gate + emit-touching PR (WIP if incomplete) + wait for review.

## Day 3 Prompt — Priority 1: mine close-or-REPLAN (~6 h)

Complete the cold-LCP consistency; re-solve mine cold. **PROCEED** (+1 Solve, mine `model_infeasible → model_optimal`; +1 genuine floor if it cold-matches) if the shared helper drives **all four k-directions (nw/ne/se/sw) → 0**, cold **MODEL STATUS 1** (from ~4.07e10). **REPLAN mine → a Sprint-32 head-offset-Phase-3 workstream** (prior Medium) if the cold-INFES histogram shows a **4th bound-complementarity site** (`comp_lo_x`/`comp_up_x`) after the `comp_pr` fix — file the carryforward; the IR plumbing + helper land regardless (reusable foundation); freed ~10–14 h → P5/P7 (Task 7). **Phase-0 gate:** `docs/issues/ISSUE_1443_*.md` §P1 (the cold-INFES histogram). Quality gate + emit-touching PR + wait for review.

## Day 4 Prompt — Priority 2: offset-alias #1111/#1112 core (polygon) (~8 h)

Branch `planning/sprint31-day4-offset-alias`. Land the **coupled** offset-alias fix (`../OFFSET_ALIAS_JACOBIAN_DESIGN.md`): the **objective-successor half** (`_build_indexed_gradient_term`, `stationarity.py:2864` — interior-representative selection) **and** the **distance-Jacobian second-index half** (`_add_indexed_jacobian_terms`, `stationarity.py:5767` — the new per-position complementary sum, inverted multiplier order + flipped `ord`) **together** (neither alone matches — objective-alone regresses polygon to MS-5). Tightly gate to var-at-two-indices; confirm #1110 orthogonality (no CGE multi-pattern regression). himmel16 is a non-convex scope guard (no fix). **Phase-0 gate:** `docs/issues/ISSUE_1143_*.md` §P2. Quality gate + emit-touching PR + wait for review.

## Day 5 Prompt — Priority 2 finish + Checkpoint 1 (~8 h)

Complete the polygon coupled fix; **completion gate:** drop `shape8_offset_alias_successor`'s `strict=True` xfail + polygon warm-matches **0.780** + the CGE multi-pattern GO list byte-stable. **REPLAN to the Sprint-32 #1111/#1112 AD-engine filing** if the var-at-two-indices gate leaks into the CGE cohort (polygon's genuine-floor +1 becomes conditional). Then **Checkpoint 1:** `--resolve-changed --since-commit ea4191dc` re-solve of the changed-golden set (bucket-diff vs the committed DB) + golden-staleness + the PR25 re-baseline recompute. **NO-GO** if any changed-golden model moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort) → investigate before proceeding. Quality gate + emit-touching PR + wait for review.

## Day 6 Prompt — Priority 3: camcge dual-consistent Walras (start, REPLAN-gated) (~7.5 h)

Branch `planning/sprint31-day6-camcge`. Land the src from the Day-0-proven `/tmp` dual-consistent prototype (`../CAMCGE_DUAL_CONSISTENT_DESIGN.md`; Epic 5): keep **every** market-clearing row (no orphaned dual) + a consumption-weighted numéraire (on `cles(i)`/`pd0(i)`) + **redefine the redundant market's dual via Walras' law**. Add the **S1∧S2∧S3 degeneracy detector** (S3 cold-MCP-singular = the false-positive guard; pass-through default — never transform a well-posed model). **Phase-0 gate:** `docs/issues/ISSUE_1330_*.md` §P3 (the `/tmp` prototype must have reached MS-1 at 191.7346 Day 0 before src). Quality gate + emit-touching PR (WIP) + wait for review.

## Day 7 Prompt — Priority 3: camcge close-or-REPLAN (~7.5 h)

Re-solve camcge; **PROCEED** (+1 Solve, camcge `model_infeasible → model_optimal`) if it reaches **MODEL STATUS 1 at omega 191.7346** (non-singular basis) **and** the detector flags only camcge across irscge/lrgcge/moncge/stdcge. **REPLAN to a per-model-numéraire declaration** (opt-in — still lands camcge's +1 Solve, the sole inherent Walras case) if the auto-heuristic false-flags or the transform can't reach MS-1. Verify the detector's cohort precision (no false-positive). Quality gate + emit-touching PR + wait for review.

## Day 8 Prompt — Priority 4: #1385 sarf symbolic emit (start, REPLAN-gated) (~8 h)

Branch `planning/sprint31-day8-sarf`. Extend `_is_blowup_dynamic_subset_equation` (`index_mapping.py:402`, the `len(eq_domain) != 1` bail) from srpchase's 1-D to sarf's **2-D** dynamic-subset-condition shape (`tbal(g,t)$taskposs`, `equipb1(m,t)$equipposs`, `equipb2(n,t)$equipposs`); begin the **new parametric `stat_task` emit** in `stationarity.py` differentiating each short-circuited body **once** in `(g,t,m,n)` — the banked 6-guarded-term derivation, `$taskposs`/`$equipposs` guards, **no set-name multiplier indices** (the Sprint-26 `nu_slack("srn")` failure). Atomic (re-emit + cross-terms together). **Phase-0 gate:** `docs/issues/ISSUE_1385_*.md` §P4. Quality gate + emit-touching PR (WIP) + wait for review.

## Day 9 Prompt — Priority 4: sarf tractability gate + Checkpoint 2 (~8 h)

Complete the atomic re-emit + cross-terms. **Tractability gate (Unknown 4.1/4.2/4.3):** the emit must be **O(constraints), not O(instances)** (1,152 Cartesian instances). Time `sarf_mcp.gms`; **PROCEED** (+Translate, sarf `translate_failure → translate`) if sub-budget with an O(constraints) `stat_task` row count + no set-name-literal multiplier indices; **REPLAN to Sprint 32** if the symbolic re-emit re-triggers the per-instance timeout. Verify the re-emitted `stat_task` matches the banked hand-derivation; golden byte-stable. Then **Checkpoint 2:** `--resolve-changed` re-solve + golden-staleness + PR25 tally. Quality gate + emit-touching PR + wait for review.

## Day 10 Prompt — Priority 5: cold-convex obj-grad (CGE cluster) (~11 h)

Branch `planning/sprint31-day10-objgrad`. Land the **ν_objective reduction** on the **CGE cluster** (the emit-fixable P5 target — Task 9 found hhfair is genuine Case-c, so target irscge/lrgcge/moncge `stat_xp` rel ~0.06, convex): route the objective gradient of the objective-defining-intermediate-variable through the defining-equation multiplier ν_objective (`src/ad/gradient.py` / `src/kkt/stationarity.py`) → convert `stat_xp` → 0 (Case-a). A single structural rule; orthogonal to the Day-5 case-normalization fix. **THE SIGN FLIP STAYS BANNED.** **Control gate (Unknown 5.1/5.2):** the reduction must reach the residual → 0 on the CGE cluster in a `/tmp` control **before** the obj-grad `src/` change; **REPLAN** to a documented Case-c finding for the family if it doesn't. **hhfair stays documented genuine Case-c** (no fix). **Phase-0 gate:** `docs/issues/ISSUE_1236_*.md` §P5. Quality gate + emit-touching PR + wait for review.

## Day 11 Prompt — Priority 6: rocket forcing → PATH-consultation input (~9 h)

Branch `planning/sprint31-day11-rocket`. Re-confirm the emit residual is clean at the NLP point (Case-c) **before** forcing (PR27). Try the **`1/m` / `1/ht²` division-by-variable reformulation** (an auxiliary `w(h)` with `w(h)·m(h) =e= X`, removing the division-by-variable from the ill-conditioned Jacobian) + scaled/relaxed continuation via the landed `--force` scaffold. **PROCEED** (+1 Solve) if the reformulation converges rocket; else **finalize the PATH-consultation input** for the renumbered Sprint 32 (`../BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 — the concrete question: which PATH option set / regularization schedule / model reformulation converges this division-by-variable optimal-control MCP). **Phase-0 gate:** `docs/issues/ISSUE_1462_*.md` §P6. Quality gate + PR (emit-touching if the reformulation lands, else docs) + wait for review.

## Day 12 Prompt — Priority 7 infrastructure + REPLAN-slack (~9 h)

Branch `planning/sprint31-day12-infra`. **P7 property fixtures:** confirm `shape8_offset_alias_successor` enabled (the P2 completion gate) + add the head-domain-offset fixture (`head_offset_ir_roundtrip.gms`, guarding the P1 index-map). Recompute the **PR25 genuine-floor tracking** against the S31–S34 re-baselined Match KPIs (footnote ⁸ ramp S31 ≥ 73). Refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites. **REPLAN-slack:** absorb whatever the mine/polygon/sarf/hhfair-CGE REPLANs freed per the Task-7 reallocation order (P5 → P7 → +Translate/forcing tails). Quality gate + PR + wait for review.

## Day 13 Prompt — Final Retest + Closeout (~8 h)

Run the **full pipeline retest** under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 30 → 31 metrics comparison; recompute the **PR25 genuine-vs-methodology re-baseline** (genuine floor → ≥ 73). **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; author `SPRINT_RETROSPECTIVE.md`; file the Sprint-32 carryforwards (mine if REPLAN'd, the #1111/#1112 core if P2 REPLAN'd, sarf if P4 REPLAN'd, the per-model-numéraire fallback if P3 REPLAN'd, rocket PATH consultation, hhfair Case-c). Commit the DB + closeout docs; revert incidental golden regens. **SPRINT 31 CLOSED.** Docs + DB PR + wait for review.
