# Sprint 30 Per-Day Execution Prompts

One self-contained prompt per day (Day 0 + Days 1–13). Each is derived from `PLAN.md` and the Sprint-30 prep outputs. Run one per day.

## How to Use

Paste the day's prompt as the task. Each prompt names its objective, branch, Phase-0 gate, quality gate, and the PR + wait-for-review step. Branches: `planning/sprint30-dayN-<slug>`.

## Cross-Cutting Rules (every day)

- **PR24 (Day-0 traced fix surface):** the banked `file:line` is a *hypothesis* — re-confirm it with `kkt_residual.py` / a cold-solve control before any `src/` change (Sprint 29 proved the hhfair `$141` attribution wrong).
- **PR25 (projection discipline):** track genuine-floor vs methodology separately; re-baseline after any pipeline-methodology change.
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14), pass the golden-staleness check (PR26) + the presolve-divergence detector, and (Day 5+) the `--resolve-changed` checkpoint.
- **Quality gate (any `*.py` change):** `make typecheck && make format && make lint && make test` must pass before commit.
- **REPLAN honesty:** each REPLAN-gated day has a firm part that lands regardless of the decision; file the Sprint-31 carryforward on REPLAN.

---

## Day 0 Prompt — Kickoff + Day-0 Traces (~6 h)

Confirm the Day-0 baseline = Sprint 29 final (`BASELINE_METRICS.md`: Solve 107 / Match 92 / model_infeasible 7 / Translate 135). Verify `git diff <S29-close SHA>..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest. Then run the **Day-0 traces (PR24)** and fill each Phase-0 gate's `Traced Fix-Surface (Day-0)` `file:line`: **robert** (re-run the cold-solve control — `stat_s`-patch → 11025.0; the harness top `stat_x` is the same-index transfer artifact), **mine** (`kkt_residual.py` → CASE_B `stat_x(4,1,1)` 1.33 + the cold-INFES-by-row histogram: is the 3-site set complete or does a 4th bound-row site surface?), **rocket** (Case-c clean residual + stand up the forcing-scaffold plumbing), **hhfair** (reproduce the `$184` widened-VARIABLE compile blocker), **Class-B** (re-confirm irscge/lrgcge/moncge `stat_pz` rel 1.00 CONSISTENT), **polygon/himmel16/camcge/sarf** (confirm banked surfaces). Restate the PR25 tally (genuine 69 / methodology ~23; firm path = robert + Class-B + offset-alias + hhfair-if-Case-b). Docs/trace-only (no `src/`). **No PR needed** (or a docs-only trace-notes PR).

## Day 1 Prompt — Priority 1a: robert objective-gradient fix (firm genuine-floor, decoupled) (~7 h)

Branch `planning/sprint30-day1-robert`. Land robert's **objective-gradient boundary-term fix** in `stat_s` (the decoupled half of P1 — Task 3 refuted the head-offset premise): drop-in `- misc("res-value",r)` at `ord(tt)=card(tt)` + guard `misc("storage-c",r)` to the `t(tt)` subset. Surface = the objective-gradient emit (`src/ad/gradient.py` `find_objective_expression` / `src/kkt/stationarity.py`), the #1447 family — **NOT** the head-offset builder; **do NOT touch robert's `stat_x`** (`nu_sb(r,tt)` is already correct, Unknown 1.4). **Phase-0 gate:** `ISSUE_robert_objgrad_boundary_term.md` — cold-confirm robert → MODEL STATUS 1 at **profit 11025.0** (= NLP optimum; convex LP ⇒ no REPLAN branch). +1 genuine floor. Blast-radius: byte-scan the corpus for the "terminal stock valued at res-value" pattern; `--resolve-changed` GO. Quality gate + emit-touching PR + wait for review.

## Day 2 Prompt — Priority 2: rocket forcing scaffold (firm P8) (~6 h)

Branch `planning/sprint30-day2-rocket-scaffold`. Build the **solution-forcing harness scaffold** (the firm P8 deliverable + the Sprint-31 entry point, `NONCONVEX_FORCING_SURVEY.md` §4): a `--force <strategy>` driver (or template) wrapping `Solve mcp_model using MCP;` in one of {homotopy/continuation loop, multi-start `.l`-perturbation loop, emitted PATH `optfile`} + a MODEL-STATUS reporter (strategy as a parameter). Validate the plumbing on rocket's presolve MCP (it *runs* the levers). This lands regardless of whether rocket converges. Quality gate + PR + wait for review.

## Day 3 Prompt — Priority 2: rocket forcing REPLAN decision (~6 h)

With the scaffold up, drive the **emittable-GAMS levers** (homotopy/multi-start — the ones Task 4 did not exhaustively probe) on rocket. **PROCEED** if any scaffold strategy reaches MODEL STATUS 1/2 at 1.0128 (+1 Solve, genuine). **REPLAN rocket's +1 Solve to the Sprint-31 PATH consultation** (prior High) if none converges — file the scoped hand-off (which PATH option set / regularization schedule / reformulation converges the division-by-variable optimal-control MCP; Task-4 evidence: INFES 477 → 382, no config converges even from the NLP optimum). The scaffold + hand-off land regardless; freed budget → scaffold hardening + Day-4 hhfair. Docs + any scaffold-hardening PR; wait for review.

## Day 4 Prompt — Priority 3: hhfair widened-VARIABLE `$184` fix + CES verdict (~10 h)

Branch `planning/sprint30-day4-hhfair`. Generalize #1449 to the **widened-VARIABLE** case (Task 9 Part D): hhfair's `$184` blocker is source `n(t)` vs MCP-widened `n(tl)` for the live nonlinear-stat coefficient `n`; add a **companion-variable + value-coupling** emit path (the `__pw`-parameter fix does not transfer). **Blast-radius:** the #1449 widened-**parameter** presolve cohort = cclinpts/chain/otpop/rocket must stay **byte-identical** (byte-scan + `--resolve-changed` GO); only hhfair's golden changes. **Phase-0 gate:** `ISSUE_1236` — once `$184` clears and the residual MCP compiles, run `kkt_residual.py`; **PROCEED** to the CES/product `stat_*` fix on a localizable **Case-b** row (+1 Match — the last live objective-mismatch target); **REPLAN to Sprint 31** if inherent non-convexity (the CES `prod` nest). Quality gate + emit-touching PR + wait for review.

## Day 5 Prompt — Checkpoint 1 + Priority 7 (Class-B `stat_pz`) start (~10 h)

**Checkpoint 1:** run `--resolve-changed --since-commit <Day-0 SHA>` (re-solve the changed-golden set, bucket-diff vs the committed DB) + golden-staleness + the **PR25 re-baseline** recompute. GO/NO-GO: any changed-golden model that moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort) is a NO-GO → investigate before proceeding. Then start **P7 Class-B `stat_pz`** (branch `planning/sprint30-day5-classB`): the general-emit **coefficient** fix on the `pz`-cross-term Jacobian-transpose (`src/kkt/stationarity.py` / `src/ad/constraint_jacobian.py`). Task 9 confirmed irscge/lrgcge/moncge all rel 1.00 (identical fingerprint) → **one fix converts all three**. Harness Case-a (residual → 0) is the acceptance; genuine-floor (all warm-match). Quality gate + PR + wait for review.

## Day 6 Prompt — Priority 1b: mine head-domain-offset architecture (start, REPLAN-gated) (~7 h)

Branch `planning/sprint30-day6-mine`. Begin the coordinated **3-site head-offset index-map** re-derivation (the REPLAN-prone half of P1): a **single shared helper** parameterized by (head-offset δ on `l`, parameter offsets `li(k)`/`lj(k)` on `i,j`) called by (1) `comp_pr` head-var emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve`), (3) the landed `stat_x` cross-term. Land the helper + Sites 1–2; evaluate mine's cold LCP from the NLP optimum. **Phase-0 gate:** `ISSUE_1443` (mine-only). mine is a convex LP ⇒ the cold `x → 4e10` is the `comp_pr` LCP residual. Quality gate + PR (WIP if incomplete) + wait for review.

## Day 7 Prompt — Priority 1b: mine close-or-REPLAN (~7 h)

Complete Site 3 + the cold-LCP consistency; re-solve mine cold. **PROCEED** (+1 Solve, mine `model_infeasible → model_optimal`) if the coordinated 3-site fix drives the cold LCP to MODEL STATUS 1. **REPLAN mine (not robert) to a Sprint-31 head-offset-architecture workstream** if the cold-INFES histogram shows a 4th bound-row site (`comp_lo_x`/`comp_up_x`) or the Day-7 `ne`/`se`/`sw` parameter-offset cascade persists (each fixed site exposes the next). File the Sprint-31 carryforward on REPLAN; freed ~10–16 h → P7 Class-B / P5 offset-alias genuine-floor. robert (Day 1) is unaffected. The fix is **atomic** (a partial 3-site fix = no Solve gain). Quality gate + emit-touching PR + wait for review.

## Day 8 Prompt — Priority 5: offset-alias cross-terms (polygon + himmel16) (~10 h)

Branch `planning/sprint30-day8-offset-alias`. Land the **coordinated** offset-alias fix (Task 9 Part B; genuine-floor — both match warm). **polygon:** the successor-offset objective cross-term (`_diff_varref` / the `_partial_collapse_sum` non-circular-offset branch, the reverted representative-selection) **+** the `distance(i,j)` **constraint-Jacobian second-index symmetry** (`src/ad/constraint_jacobian.py` — the dropped `r(j)` term) — **land both together** (neither alone matches, the Day-5-revert coupling). **himmel16:** the objvar-gradient-**sign** reconciliation (`_diff_varref(circular=True)` branch + the dual-transfer sign — the cyclic cross-term is already present). **Property fixtures (P8):** drop the `@pytest.mark.xfail` on `shape8_offset_alias_successor` (the polygon completion gate) + add a numeric assertion to `shape7_offset_alias_cyclic`. **Phase-0 gate:** `ISSUE_1143`/`ISSUE_1146` — PROCEED if a tight shape-gate makes each correct; **REPLAN to Sprint 31** (#1111/#1112 core) if it needs general alias differentiation. Quality gate + emit-touching PR + wait for review.

## Day 9 Prompt — Priority 4: #1385 sarf symbolic cross-terms (~7 h)

Branch `planning/sprint30-day9-sarf`. Land the **atomic** symbolic runtime-guard cross-term emit (Task 9 Part A): (1) extend `src/ad/index_mapping.py` `_is_blowup_dynamic_subset_equation` from srpchase's **1-D** to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`, `equipb1(m,t)$equipposs`, `equipb2(n,t)$equipposs`); (2) a **new symbolic cross-term emit** in `src/kkt/stationarity.py` differentiating each body **once** parametrically in `(g,t,m,n)` — the banked 6-guarded-term `stat_task` derivation, `$taskposs`/`$equipposs` guards, **no set-name multiplier indices**. **Tractability gate (Unknown 4.2):** the emit must be **O(constraints), not O(instances)** (counts 384+648+120 = 1,152) — time `sarf_mcp.gms`; **PROCEED** if it emits under the translate budget (+Translate); **REPLAN to Sprint 31** if it re-triggers the timeout. **Phase-0 gate:** `ISSUE_1385`. Quality gate + emit-touching PR + wait for review.

## Day 10 Prompt — Checkpoint 2 + Priority 4 close (~6 h)

**Checkpoint 2:** `--resolve-changed --since-commit <Day-0 SHA>` re-solve of the changed-golden set + golden-staleness + the PR25 re-baseline tally. NO-GO on any backward bucket move. Close #1385 (sarf translate verified byte-stable + GAMS `action=c` clean, or the Sprint-31 REPLAN filed). Measurement + close only (no new `src/`). PR if any golden regen; wait for review.

## Day 11 Prompt — Priority 6: camcge → Epic 5 Walras transformation (REPLAN-gated) (~10 h)

Branch `planning/sprint30-day11-camcge`. Land the Epic-5 CGE-domain transformation (Task 7): drop **one** redundant market-clearing row instance `lmequil(lc_drop)` (Walras' law ⇒ rank deficiency exactly 1 — **not** the whole `lc` family) + fix the consumption-weighted numéraire `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` (camcge has no `cpi`), gated by the S1∧S2∧S3 degeneracy detector (pass-through default). **Phase-0 gate:** `ISSUE_1330` — **PROCEED** if transformed camcge → MODEL STATUS 1 at 191.7346 with a non-singular basis **and** the detector flags only camcge across irscge/lrgcge/moncge/stdcge; **REPLAN to a per-model-numéraire declaration** (opt-in, still lands camcge) if the auto-heuristic false-flags. Quality gate + emit-touching PR + wait for review.

## Day 12 Prompt — Priority 7 finish + Priority 8 infra + REPLAN-slack (~10 h)

Branch `planning/sprint30-day12-infra`. Finish **P7 Class-B** (verify `stat_pz` converts irscge/lrgcge/moncge, residual → 0; document the cold-convex Case-c residue for Sprint 31). **P8 infrastructure:** finalize the property-test catalog (the head-domain-offset fixture + the enabled `shape7`/`shape8`); apply the **PR25 re-baseline** to the S31–S33 Rolling-KPIs Match targets (off the ≥64% line); finalize the **solution-forcing harness scaffold** + a CONTRIBUTING/Phase-0 note. Absorb whatever the mine/rocket/camcge REPLANs freed (more Class-B / offset-alias genuine-floor per the Task-6 reallocation). Quality gate + PR + wait for review.

## Day 13 Prompt — Final Retest + Closeout (~8 h, tight)

Run the full pipeline retest under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 29 → 30 metrics comparison; recompute the **PR25 genuine-vs-methodology re-baseline** (genuine floor → ≥ 72 target). Author the `SPRINT_LOG.md` final entry (top-table + per-priority summary) + `SPRINT_RETROSPECTIVE.md`; file the Sprint-31 carryforwards (mine if REPLAN'd, the rocket PATH consultation, camcge per-model declaration if REPLAN'd, #1111/#1112 if REPLAN'd). Commit the DB + goldens; revert incidental regens. Docs + measurement PR; wait for review. **Sprint 30 CLOSED.**

## Checkpoint Cadence (Days 5, 10, 13)

Days 5 + 10: `--resolve-changed --since-commit <Day-0 SHA>` (re-solve the changed-golden set, bucket-diff vs the committed DB) + golden-staleness + the PR25 re-baseline tally. Day 13: the full 3× `PYTHONHASHSEED` pipeline retest. A changed-golden model that moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort) is a NO-GO → investigate before the next priority.

## Related Documents

`../PLAN.md` · `../KNOWN_UNKNOWNS.md` · `../REPLAN_RISK_ASSESSMENT.md` · `../HEAD_OFFSET_ARCHITECTURE_DESIGN.md` · `../NONCONVEX_FORCING_SURVEY.md` · `../CAMCGE_WALRAS_TRANSFORM_DESIGN.md` · `../TOOLING_READINESS_AUDIT.md` · `../BACKLOG_FIX_SURFACE_ANALYSIS.md`
