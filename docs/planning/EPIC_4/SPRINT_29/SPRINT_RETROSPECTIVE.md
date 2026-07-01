# Sprint 29 Retrospective

**Sprint window:** 2026-06-28 (Day 0) → 2026-07-01 (Day 13)
**Day-0 baseline SHA:** `9a86f8b4` (Sprint 28 final + Day-0 traces).
**Final metrics (142-model GAMSlib corpus):** Parse **142** · Translate **135** · Solve **107** (+0) · Match **92** (+0, genuine floor **68 → 69**) · model_infeasible **7** · Tests **4,971** · Determinism **byte-identical ×3 seeds** ✅

**Headline outcome — an honest one: the two Solve movers and the one live +Match all REPLAN'd, so the as-measured headline did not move.** Solve held at **107** (target ≥ 109 needed *both* mine #1443 and rocket #1462 to PROCEED; both REPLAN'd at their gates). Match held at **92** (maintain-≥92 met; stretch 96 out of reach once hhfair #1236 — the only live +Match — REPLAN'd). The one realized quality gain is the **genuine cold-robustness floor 68 → 69** (maxmin `-1` objvar fix + the catmix Case-A recovery it triggered; polygon's +1 was withdrawn Day 5 when a re-solve caught a regression). model_infeasible held at 7 (target ≤ 5 missed — the deferred mine/camcge infeasibles remain). Translate, Tests, and Determinism **met**.

**This was, by count, a REPLAN-heavy sprint** — four of the sprint's headline tracks (rocket #1462 Day 2, mine #1443 Day 7, hhfair #1236 Day 8, #1385 Day 9) bottomed out at hard architectural workstreams and were deferred to Sprint 30. That pattern was **predicted** by the Task-5 REPLAN risk assessment ("Risk if Wrong" = exactly this Solve/Match path), so the sprint's value is not in the (unmoved) headline but in **three firm deliverables + six sharply-scoped, evidence-backed carryforwards**.

---

## What Went Well

1. **Every REPLAN was evidence-based and left Sprint 30 a sharp surface, not a shrug.** The KKT-residual harness + hand-derivation turned each gate into a decision with a cited cause: mine #1443 (Day 7) — the `l+1` head-offset × `li(k)`/`lj(k)` parameter-offset coupling in `comp_pr`, proven by an `iterlim=0` warm-from-optimum experiment where the `nw` direction cleared but the offset-bearing directions stayed ~1e10; hhfair #1236 (Day 8) — the *first* compile error is `$184` (the #1449 widened-symbol conflict for a live nonlinear-stat variable), not the Day-0-attributed `$141`; #1385 (Day 9) — the sarf cross-terms are hand-derivable (banked) but the atomic symbolic-emit is the Sprint-26-Day-4-failed architecture. None of these was a capitulation; each is a Sprint-30 workstream with a named fix surface and a minimal reproduction.

2. **The `--resolve-changed` checkpoint gate (Priority 8) is the sprint's most durable deliverable** — and it retired Sprint-28 retrospective action items #4 (re-solve the changed-golden set) and #5 (post-methodology re-baseline). It re-solves every model whose emit golden changed since a baseline, bucket-diffs vs the committed DB, exits NO-GO on any backward move, and never mutates the tree. It survived a 12-comment adversarial review that hardened real correctness holes (missing-DB-entry → NO-GO, byte-exact scoped golden restoration, stage-flag/dry-run guards, structured git-error handling, and the `_OUTCOME_RANK` taxonomy gap where `model_locally_optimal`+match had ranked *below* `model_infeasible`+match). It is now the standing checkpoint tool.

3. **The disposition trace (Day 12) *sharpened* an existing carryforward instead of just cataloguing.** Harness-tracing the Class-C cold-convex cohort found **robert is a second instance of the mine #1443 head-domain-offset class** (`sb(r,tt+1)` referencing `x(p,tt)` should emit `nu_sb(r,tt+1)`, not `nu_sb(r,tt)`) — and the *simpler* pure-constant-offset sub-case. So the Sprint-30 head-offset workstream now converts **both** mine (Solve) and robert (genuine-floor), with robert as the minimal reproduction. The same day confirmed the Class-B CGE family (irscge/lrgcge/moncge/stdcge, `stat_pz`≈1.0) is **NOT** the camcge Walras family — removing them from any Epic-5 expansion.

4. **Checkpoint 1 (Day 5) caught a real regression before it shipped.** The Day-4 polygon offset-alias fix looked "Match-neutral" on golden-staleness + harness residual, but the Checkpoint-1 re-solve showed polygon match(0.7797) → mismatch(0.0). It was reverted the same day (Option 1). This is precisely why the re-solve gate exists — and it directly motivated building the automated `--resolve-changed` version on Day 11.

5. **Determinism and hygiene held end-to-end.** The final 3-seed emit byte-comparison (cesam2/otpop/stdcge/robert/launch — spanning the dict-order-sensitive classes) was identical, and every docs PR was hygiene-checked for the U+2212 Unicode-minus trap.

## What We'd Do Differently

1. **Front-load the "is this convex?" check into the Day-0 trace, not Day 8/12.** Two tracks (hhfair #1236, the Class-B CGE family) burned diagnosis effort before the decisive fact surfaced: they are **non-convex**, so even a perfectly correct cold emit won't converge to the match — they *need* the presolve warm-start they already use, so there is no genuine-floor conversion regardless of the cross-term. A convexity gate in the Phase-0 template would have flagged "no cold-conversion available" up front and re-pointed the budget sooner.

2. **The Day-0 traced fix-surfaces were wrong twice more** (continuing the Sprint-27 finding). hhfair's Day-0 surface named the `$141` dual-transfer domain; the real blocker is the upstream `$184`. #1385's Day-0 candidate (restrict the transfer domain) was disproven — the srpchase short-circuit is 1-D-only and doesn't even fire on sarf's 2-D shape. **Treat Day-0 `file:line` surfaces as hypotheses to disprove, and reserve the first hour of each priority day to re-trace before implementing.**

3. **A full solve-retest is redundant when the emit is frozen — say so explicitly in the plan.** Zero `src/` emit change landed after Checkpoint 2 (Day 10), yet the Day-13 prompt still called for a 3× full-142 solve-retest (~12h). The defensible substitute — 3-seed *emit* byte-comparison (determinism) + `--resolve-changed` (no regression) + a DB bucket recompute — is minutes, not hours, and gives the same guarantee. The plan should gate the expensive retest on "did any `src/` emit change land since the last full measurement?".

4. **Scope the REPLAN-slack realistically.** The plan reallocated mine + rocket's freed ~14–24 h to "more Class-C cold-convex genuine-floor conversions," but the trace showed the Class-C cohort (tforss/markov/robert) are all large-residual, distinct per-model diagnoses — not the shared quick-win shape maxmin/catmix were. Freed budget from an architectural REPLAN tends to land on *other* architectural problems; plan the slack as "diagnose + disposition," not "convert N more."

## Metrics vs Targets

| Metric | Day-0 | Final | Target | Verdict |
|---|---|---|---|---|
| Parse | 142 | 142 | 142 | ✓ |
| Translate | 135 | 135 | ≥ 135 | ✓ |
| Solve | 107 | 107 | ≥ 109 | ✗ (mine + rocket REPLAN'd) |
| Match (as-measured) | 92 | 92 | ≥ 92 / stretch 96 | ✓ maintain / ✗ stretch |
| Match (genuine floor) | 68 | 69 | 68 → up | ✓ (+1) |
| model_infeasible | 7 | 7 | ≤ 5 | ✗ |
| Tests | ~4,935 | 4,971 | ≥ 4,960 | ✓ |
| Determinism | — | ✅ ×3 | ×3 seeds | ✓ |

## Firm deliverables (landed to main)

- **#1462 `_fx_`-multiplier presolve warm-start** (Day 1, PR #1476) — sprint-wide presolve robustness (transfers fixed-variable marginals to `_fx_` multipliers).
- **#1447 maxmin objvar multi-model objective-scoping fix** (Day 3, PR #1478) + catmix Case-A recovery — the genuine-floor +1.
- **`--resolve-changed` checkpoint re-solve gate + PR25 re-baseline discipline** (Day 11, PR #1486) — the standing regression-surfacing tool; 29 unit tests.

## Sprint-30 carryforwards

1. **Head-domain-offset emit-architecture** (`ISSUE_1443`) — converts **mine (Solve)** *and* **robert (genuine-floor)**; robert = minimal pure-constant-offset reproduction, mine = full `l+1 × li(k)/lj(k)` multi-site case.
2. **rocket #1462 non-convex forcing** — trust-region / homotopy / multi-start (the `_fx_` warm-start already landed; residual is intrinsic non-convergence).
3. **hhfair #1236 widened-VARIABLE presolve fix** (`ISSUE_1236`) — the `$184` #1449-for-a-live-nonlinear-stat-variable; prerequisite to the CES verdict.
4. **#1385 symbolic runtime-guard cross-term emit** — sarf reference target; cross-terms hand-derived + banked.
5. **Offset-alias cross-terms #1111/#1112** — polygon successor-offset (reverted Day 5, coupled with the distance-Jacobian); file the issue doc in Sprint 30.
6. **camcge #1330 → Epic 5** — Walras drop-row + fix-numéraire (`CGE_DEGENERACY_SCOPING.md`); the Class-B CGE `stat_pz` coefficient discrepancy is a *separate* general-emit backlog item (confirmed NOT Walras).
