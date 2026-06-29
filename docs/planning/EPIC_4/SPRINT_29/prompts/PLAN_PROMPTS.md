# Sprint 29 Per-Day Execution Prompts

One self-contained prompt per day. Each states **only the day's scope** — no forward-looking claim about work not yet done (the Sprint 27 stale-prompt failure mode). Run the day's prompt, then the next day's. The detailed rationale + budget is in `PLAN.md`.

## How to Use

Paste the day's prompt. It names the day's scope, the Phase-0 gate(s) to clear, the `kkt_residual.py` invocation where relevant, the REPLAN exit for the gated tracks, and the stale-assumption reminder.

## Cross-Cutting Rules (every day)

- **PR24:** the fix surface is whatever the **Day-0 trace** established (the `Traced Fix-Surface (Day-0)` line in the issue's Phase-0 gate) — never the prep-doc guess. A PROCEED that cites only the prep surface is invalid.
- **Quality gate before every commit:** `make typecheck && make format && make lint && make test`.
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14), pass the golden-staleness check (PR26), and (Day 5+) the new `--resolve-changed` checkpoint.
- **PR25 + re-baseline:** when reporting a Solve/Match delta, label it **genuine** (cross-term transition) vs **methodology** (warm-start validation of an already-correct emit). The 21 cold-convex Case-b fixes are **Match-neutral genuine-floor lift** (68 → up), *not* headline Match. After any retry-trigger/comparison-logic/scope change, recompute the genuine/methodology split (Task 8).
- **Flag stale assumptions:** if anything in this prompt or the Phase-0 gate contradicts what you find, STOP and correct the doc before proceeding.

---

## Day 0 Prompt — Kickoff + Day-0 Traces (~6 h)

Confirm the Day-0 baseline equals Sprint 28 final (reuse the committed `gamslib_status.json` — it recomputes to Solve 107 / Match 92 / model_infeasible 7; `git diff 803a259a..HEAD -- src/ scripts/` is empty, so no fresh retest — see `BASELINE_METRICS.md` + Unknown 8.3). The KKT-residual harness, divergence detector, and golden-staleness gate are already built and audited ready (Task 6) — no Day-0 tooling extension. Run the **Day-0 traces (PR24)** for the REPLAN-prone + lead tracks — mine (#1443), rocket (#1462), the cold-convex Class-A leads (maxmin/himmel16/like/catmix/polygon), and hhfair (#1236, first reproduce the `$141`/`$257` residual-emit-compile blocker): instrument the candidate surfaces, emit each `<model>_mcp.gms`, locate the offending row, and **fill the `Traced Fix-Surface (Day-0)` line** in each Phase-0 gate with the confirmed `file:line` + evidence. Restate the PR25 Day-0 tally (genuine floor 68 / methodology ~24; firm headline path = mine + rocket, both REPLAN-gated). Do NOT start any `src/` fix today.

## Day 1 Prompt — Priority 2: #1462 rocket `_fx_`-multiplier warm-start (~7 h)

Clear the `ISSUE_1462` Phase-0 gate (harness Case b `stat_step` 0.497, confirmed). Land the **general** `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` `_fx_`-multiplier warm-start in the presolve emit (`src/emit/emit_gams.py` `_emit_nlp_presolve`) — this is **sprint-wide presolve robustness, firm regardless of rocket's outcome**. Verify **zero byte/solve regression** across the Layer-4-unfix set — enumerate with `grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null || true` (currently otpop/chain/cclinpts/rocket) — and the full presolve golden set. Open the warm-start PR (emit `.gms` diff + golden-staleness pass).

## Day 2 Prompt — Priority 2: #1462 rocket residual (REPLAN-gated) (~7 h)

With the `_fx_` warm-start landed, resolve the **residual MS-5 question** (Unknown 2.2): inject the complete `_fx_`-at-`h0` warm-start for all of ht/v/m, then run the degenerate-bound suppression probe (suppress the Layer-4 unfix where the fixed value equals the relaxed bound, e.g. `v('h0')=0`). **PROCEED** if rocket reaches MODEL STATUS 1 with `compare_objective_match` (**+1 Solve / +1 Match**, genuine). **REPLAN to Sprint 30 forcing** (trust-region / homotopy) if MS-5 persists with a clean residual — rocket is non-convex, so intrinsic non-convergence is the live Case-c; the warm-start (Day 1) still lands as presolve robustness. File the Sprint-30 carryforward if REPLAN. Freed ~4–8 h → Day-8 hhfair.

## Day 3 Prompt — Priority 4 + 7: cold-convex Class-A + offset-alias shared fix (start) (~7 h)

Clear the `ISSUE_1447` / `ISSUE_1146` / `ISSUE_1143` gates (all harness Case b — `stat_mindist` 1.0 / `stat_area` 2.0 / `stat_theta` 0.49). Implement the **shared objective/defining-variable cross-term fix** at the traced surface (`src/kkt/stationarity.py` + `src/ad/derivative_rules.py` `_partial_collapse_sum`/`_diff_varref` for the cyclic/successor offset-alias shapes). This **one fix** is both the P4 Class-A correction and the P7 offset-alias fix. Land maxmin + himmel16 + polygon first; verify each → harness **Case a** (residual → 0). **Match-neutral** (all match warm → genuine-floor lift, not headline Match). **REPLAN (Unknown 7.2)** to Sprint 30 only if the fix must thread the #1111/#1112 alias-AD core (it should gate to the cyclic/successor shape).

## Day 4 Prompt — Priority 4 + 7: extend + property-test fixtures + PR (~7 h)

Extend the Day-3 fix to like (`stat_p` 2.0) + catmix (`stat_x1` 0.95). Add the two property-test fixtures (Task 9 Part C): `tests/fixtures/crossterm_shapes/shape7_offset_alias_cyclic.gms` (himmel16 circular `i++1`) + `shape8_offset_alias_successor.gms` (polygon `ord(j)=ord(i)+1`), wired into `tests/integration/emit/test_ad_crossterm_shapes.py` (in-process `_emit()`/`_stat_row()` pattern). Full-corpus byte-stability + re-solve; open the combined P4-Class-A / P7 PR. Report the genuine-floor lift (number of Case-b cold-recoveries).

## Day 5 Prompt — Checkpoint 1 + Priority 4 Class-C (~10 h)

**Checkpoint 1 (Task 8):** run `--resolve-changed --since-commit <Day-0 SHA>` (re-solve the changed-golden set, bucket-diff vs the committed DB — GO/NO-GO: any model regressed → investigate) + golden-staleness + the **PR25 tally with the re-baseline step** (recompute genuine/methodology if any methodology change landed Days 1–4). Then, as budget allows, take the **Class-C model-specific** cold-convex Case-b (large-residual standalone): tforss (`stat_v` 2052), markov (`stat_z` 13), robert (`stat_x` 7.2), harker (`stat_s` 2.16) — cheapest-localizable first; each a per-model `stat_*` fix, harness Case-a acceptance, Match-neutral. This is slack-absorbing; stop at the budget.

## Day 6 Prompt — Priority 1: #1443 mine head-domain-offset (start, REPLAN-gated) (~7 h)

Clear the `ISSUE_1443` gate (harness Case b `stat_x` 1.33; **mine is a convex LP → no Case-c escape**, so the pivot is single-site vs distributed multi-site re-derivation). Map the cold-INFES by row-type (49 INFES across `comp_pr`/`comp_lo_x`/`comp_up_x`/`stat_x`/`def`). Apply the coordinated **3-site head-offset index map**: (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve` ~line 1281), (3) the landed `stat_x` cross-term — all agreeing on the `l+1`/`±li`/`±lj` correspondence. Drive the cold LCP toward feasibility (`x ≤ x.up=1`, no `x→4e10` blowup).

## Day 7 Prompt — Priority 1: #1443 mine close-or-REPLAN (~7 h)

If the coordinated 3-site fix drives mine's cold MCP to MODEL STATUS 1 with `compare_objective_match` → **+1 Solve firm (genuine** `model_infeasible → model_optimal`), open the PR. **REPLAN to Sprint 30** (a head-domain-offset emit-architecture workstream — still Case b, just multi-site) if the INFES stays distributed across `comp_*`/bound rows or each fixed site only exposes the next (the Day-4 evidence — 22/30 `stat_x` systemic — leans REPLAN). File the Sprint-30 carryforward if REPLAN; freed ~10–16 h → Day-12 Class-C cold-convex.

## Day 8 Prompt — Priority 6: #1236 hhfair (the only live +Match) (~10 h)

hhfair is the **only live P6 +Match** (Task 9 — quocge is Epic 5, prolog resolved, sambal/qsambal Match-neutral). **First** fix the residual-emit-compile blocker (the `$141`/`$257` from the domain-widened `n(tl)` / `n(0)=0` fixup) so `kkt_residual.py data/gamslib/raw/hhfair.gms` produces a verdict; **then** read it. **PROCEED** if Case b on a CES/`prod` `stat_*` row → fix the product log-derivative gradient + the CES `(-a2)`/`(-1/a2)` chain-rule (**+1 Match**, genuine `mismatch → match`); **REPLAN to Sprint 30** if Case c (non-convex `prod`/CES nest). Also run the **sambal/qsambal #1112 consolidation check** (Unknown 6.2) — confirm whether the `$xw(i,j)` dollar-condition fix overlaps the offset-alias #1112 work.

## Day 9 Prompt — Priority 3: #1385 translation-timeout cross-terms (~7 h)

Pick the smallest viable timeout target (iswnm/sarf/mexls/nebrazil — Unknown 3.2, via the emit-size probe in the `ISSUE_1385` gate). Hand-derive its runtime-guard `stat_*` cross-terms, then land the **atomic** pair: the runtime-guard equation-body re-emit (`src/kkt/stationarity.py`) **and** the `J_gᵀ·lam` cross-terms together (a re-emit without cross-terms = an inconsistent MCP, Unknown 3.1). Structural check: **no quoted-set-name multiplier indices** (`grep -qE 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("'` — the Day-4 `nu_slack("srn")` bug). Target: the smallest target → translate-success (**+Translate**).

## Day 10 Prompt — Checkpoint 2 + Priority 3 close (~6 h)

**Checkpoint 2 (Task 8):** `--resolve-changed` + golden-staleness + the PR25 re-baseline tally. Close #1385 (open the PR with the atomic re-emit + cross-terms + the emit `.gms` diff), OR re-defer the cross-term half to Sprint 30 if the smallest target's instance count proved intractable in the budget (keep the translate-only short-circuit).

## Day 11 Prompt — Priority 5: camcge → Epic 5 write-up + Priority 8 infra build (~10 h)

**P5 (no `src/`, Task 7):** finalize `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` — confirm #1330 camcge → Epic 5 (inherent Walras-law singularity, no general emit fix), Priority 5 = write-up only. **P8 (Task 8 design):** build the checkpoint `--resolve-changed` mode in `scripts/gamslib/run_full_test.py` (re-solve the `changed_emit_artifacts.py` golden set, bucket-diff vs the committed DB, GO/NO-GO on any backward move) + add the PR25 **re-baseline step** to the projection template (`CONTRIBUTING.md` §"Projection Discipline"). Quality gate + tests for the new mode.

## Day 12 Prompt — Priority 4 Class-B / inconclusive + REPLAN-slack (~10 h)

Harness-trace the **Class-B CGE family** (irscge/lrgcge/moncge/stdcge/marco — `stat_pz`≈1.0): confirm whether they are the camcge Walras family (→ Epic 5, no fix) or a localizable cross-term; do **not** count as wins without the trace. Re-trace the **2 inconclusive** (paperco dual-transfer-infeasible, weapons harness-abort) to disposition. **REPLAN-slack absorption:** if mine (#1443) and/or rocket (#1462) REPLAN'd, spend their freed ~14–24 h here on more Class-C cold-convex genuine-floor conversions + the sambal/qsambal #1112 side-effect.

## Day 13 Prompt — Final Retest + Closeout (~8 h, tight)

Run the **final 3× `PYTHONHASHSEED` retest** over the full 142-model pipeline (the authoritative measurement) + golden-staleness + the `--resolve-changed` check. Report the **PR25 final tally + re-baseline**: realized Solve/Match vs target (Solve ≥ 109 needs both mine + rocket PROCEED; Match maintain ≥ 92 / genuine floor 68 → realized), each delta labeled genuine vs methodology. Write the `SPRINT_LOG.md` final entry + `SPRINT_RETROSPECTIVE.md`, and file Sprint 30 carryforwards for any REPLAN'd track (#1443 / #1462-residual / #1111-#1112 / camcge-Epic-5).

## Checkpoint Cadence (Days 5, 10, 13)

Days 5 + 10: `--resolve-changed --since-commit <Day-0 SHA>` (re-solve the changed-golden set, bucket-diff vs committed DB) + golden-staleness + PR25 re-baseline tally. Day 13: the full 3× `PYTHONHASHSEED` pipeline retest. A changed-golden model that moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort) is a NO-GO → investigate before the next priority.

## Related Documents

- `PLAN.md` (the detailed schedule + budget + risk register + prep-task→PR mapping)
- `KNOWN_UNKNOWNS.md`, `BASELINE_METRICS.md`, `COLD_CONVEX_COHORT_SURVEY.md`, `REPLAN_RISK_ASSESSMENT.md`, `TOOLING_READINESS_AUDIT.md`, `PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md`, `BACKLOG_FIX_SURFACE_ANALYSIS.md`
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`
- The 10 Phase-0 gates: `docs/issues/ISSUE_{1443,1462,1385,1447,1332,1247,1239,1236,1146,1143}_*.md`
