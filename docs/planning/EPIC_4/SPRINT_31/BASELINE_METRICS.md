# Sprint 31 Day-0 Baseline Metrics + Bucket Provenance + Re-Baseline Discipline

**Task:** Sprint 31 Prep Task 2 (PR15 + PR17 + PR25)
**Day-0 source:** Sprint 30 final state (the "SPRINT 30 CLOSED" commit `ea4191dc`, 2026-07-08) — reused unchanged; no fresh retest.
**Owner:** Sprint 31 Planning Team

---

## 0. Day-0 = Sprint 30 Final (no fresh retest)

`git diff <S30-close>..HEAD -- src/ scripts/` is **empty** — no `src/` or `scripts/` drift since the Sprint 30 close, so the Day-0 metrics equal the Sprint 30 final without a ~4 h retest.

```bash
# The robust close-SHA anchor (see the finding below): pin the subject-anchored commit.
S30=ea4191dcf0cf6fad695816d0dc4edda02ee71717   # "Sprint 30 Day 13: Final retest (determinism verified) + closeout — SPRINT 30 CLOSED"
git diff --quiet "$S30"..HEAD -- src/ scripts/ && echo "no src/ drift — reuse the committed DB" || git diff --stat "$S30"..HEAD -- src/ scripts/
# → no src/ drift — reuse the committed DB
```

**Two confirmations that Day-0 = Sprint 30 final:**

1. **No `src/`/`scripts/` drift** since `ea4191dc` — every commit since the close is docs-only (PR #1514 the Sprint-31 PROJECT_PLAN insertion + renumber, PR #1515 the Sprint-31 prep phase).
2. **The committed DB (`data/gamslib/gamslib_status.json`) is byte-unchanged since the Sprint 28 close** (`2717d542`, 2026-06-21) — because **both Sprint 29 and Sprint 30 netted no as-measured bucket change**: every headline mover REPLAN'd (mine #1443, rocket #1462 across both sprints; camcge #1330; polygon #1143), and the firm deliverables were **cold-correctness / genuine-floor / general-robustness** wins that did not move any as-measured Solve/Match bucket — Sprint 29's `_fx_` warm-start + #1447 maxmin objvar fix + catmix; Sprint 30's robert objective-gradient fix + the hhfair `$184` widened-VARIABLE companion-variable emit + the Class-B `stat_pz` presolve dual-transfer **case-normalization** fix. So the Sprint 28 close DB *is* the Sprint 30 final DB, and the recompute in §1 reproduces the Sprint 30 final headline exactly. (`git diff --quiet ea4191dc..HEAD -- data/gamslib/gamslib_status.json` → byte-identical.)

> **⚠️ Finding (PR24-style latent-bug in the prep snippets), carried from Sprint 30.** The auto-deriving snippet `git log --grep='SPRINT 30 CLOSED' -1 --format=%H` is **ambiguous**: later prep commits quote the literal phrase "SPRINT 30 CLOSED" in their bodies, so `-1` (newest match) can resolve to a docs-only review-fix commit, not the true close (`ea4191dc`). For the drift check the *result* is identical (every commit in between is docs-only → still "no `src/` drift"), so the check is not wrong — but the reported SHA is misleading. **Robust forms:** pin the SHA (as above), or anchor on the subject with `git log --grep='SPRINT 30 CLOSED' --format=%H | tail -1` (oldest match = the real close, verified to resolve to `ea4191dc`). The runnable Verification snippets in `PREP_PLAN.md` (Task 2), `KNOWN_UNKNOWNS.md` (Unknown 7.2), and `prompts/PREP_TASK_PROMPTS.md` (Task 2) use the robust `| tail -1` form; this §0 block pins the SHA directly. Task 8 (tooling audit) + Task 10 (schedule) should keep to the pinned/`tail -1` form.

---

## 1. Day-0 Headline Counts (142-model GAMSlib corpus)

Recomputed from the committed DB over the **canonical 142-model scope** (`get_candidate_models` = `convexity.status ∈ {verified_convex, likely_convex}`). Reproduces the Sprint 30 final headline (`docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` §1).

| Metric | Sprint 31 Day 0 | Sprint 31 Target | Gap |
|---|---|---|---|
| Parse | **142** / 142 | ≥ 142 | met |
| Translate | **135** / 142 | ≥ 135 (stretch +1 via #1385) | met (maintain) |
| Solve (`model_optimal[_presolve]`) | **107** / 142 | ≥ 109 | −2 (mine + camcge) |
| Match (`compare_objective_match`) | **92** / 142 | maintain ≥ 92 / **genuine floor 70 → ≥ 73** | met / −3 to floor |
| Mismatch (`compare_objective_mismatch`) | **9** | — | (solved-but-diverging) |
| path_syntax_error | **8** | maintain ≤ 8 | met |
| path_solve_terminated | **4** | maintain ≤ 5 | met |
| model_infeasible | **7** | ≤ 5 | −2 (mine + camcge) |
| Tests | **4,997** | ≥ 5,000 | −3 |

Recompute (canonical scope, committed DB): **Parse 142 · Translate 135 · Solve 107** (63 `model_optimal` + 44 `model_optimal_presolve`) **· Match 92 · Mismatch 9 · multi-solve-skip 6 · not-tested 35** (the 7 translate-fails + the 28 solve-fails/uncompared). Of the 107 solved, 92 match, 9 mismatch, 6 are uncompared (`compare_multi_solve_skip`).

> **Scope note.** A naive recompute over every translate-success row returns 115 solve / 92 match / 17 mismatch — it includes 8 out-of-scope non-NLP/QCP rows (`abel` + `ps10_s`/`ps2_f_s`/`ps2_s`/`ps3_s`/`ps3_s_gic`/`ps3_s_mn`/`ps3_s_scp`). The canonical `get_candidate_models` scope excludes them → the authoritative Solve 107 / Match 92.

### Failure-bucket membership (frozen Day-0 reference)

- **Translate failures (7):** `danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, **`sarf`**.
- **model_infeasible (7):** `agreste`, **`camcge`**, `cesam`, `fawley`, `lnts`, **`mine`**, **`rocket`**.
- **path_syntax_error (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`.
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`.
- **path_solve_terminated (4):** `dyncge`, `elec`, `tricp`, `twocge`.
- **mismatch (9):** `chain`, `china`, `circle`, **`hhfair`**, `imsl`, `lmp2`, `prodsp2`, `spatequ`, `trig` (`abel` is out-of-scope non-NLP).

The Sprint 31 target models are highlighted: **mine** + **camcge** + **rocket** (model_infeasible), **hhfair** (the live objective-mismatch, P5), **sarf** (translate-failure, P4 #1385). The buckets are **byte-identical to Sprint 30 Day-0** (= Sprint 29 final = Sprint 28 close) — Sprint 30's landed fixes were genuine-floor / general-robustness, not as-measured bucket movers.

---

## 2. Re-Baseline: Genuine vs Methodology Match Split (PR25)

The as-measured Match 92 carries forward from Sprint 28's 62 → 92 (+30) jump, whose decomposition is **+7 genuine + ~24 methodology − 1 stale-baseline** (`SPRINT_28/SPRINT_LOG.md` §"Day 13"). Sprint 29 raised the **genuine floor 68 → 69** (the #1447 maxmin objvar `-1` fix + catmix recovery), and Sprint 30 raised it **69 → 70** (the **robert** objective-gradient boundary-term fix, which cold-matches at 11025.0 → a methodology match reclassified genuine) while the as-measured 92 stayed flat both sprints (no pipeline-methodology change landed). So Sprint 31's re-baseline floor is **70**, methodology **22**.

| Component | Count | Notes |
|---|---|---|
| **Genuine, stable** (the re-baseline floor) | **70** | the Sprint-28 genuine 68 (cold matches incl. otpop/chakra/chenery/kand/srkandw + the 6 non-methodology presolve matches) **+1** Sprint 29 (maxmin genuine after #1447; catmix recovered) **+1** Sprint 30 (**robert** cold obj-grad fix → genuine) |
| **Methodology-recovered** (the Sprint-28 Day-9 presolve-retry-on-cold-mismatch broadening, `_cold_objective_mismatches_nlp`) | **22** | himmel16, weapons, harker, **polygon**, sambal, markov, worst, **irscge**, **lrgcge**, **moncge**, stdcge, like, mathopt1, mathopt4, mingamma, paperco, qsambal, marco, etamac, cpack, tforss (+ residue) — the Sprint-30 set minus **robert** (now genuine) |
| **As-measured total** | **92** | — |

**Operational definition** of the methodology set (unchanged from PR25): `mcp_solve.outcome_category = model_optimal_presolve` **AND** `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*), cold emit byte-identical to its pre-Day-9 state. These are *already emit-correct* models the broadened retry warm-start-*validates* — not repeatable cross-term gains.

**Genuine-floor → ≥ 73 conversion map (Sprint 31 tracks that convert a methodology/warm match — or a live mismatch — into a genuine cold match, +1 genuine floor each):**

| Track | Models it converts | Genuine-floor delta |
|---|---|---|
| **P2 offset-alias core (#1111/#1112, polygon)** | `polygon` (cold offset-alias fix → genuine cold match) | +1 |
| **P5 cold-convex obj-grad (hhfair `stat_u`)** | `hhfair` — *not* methodology (currently **mismatch**); a fix is a **new** genuine match (+1 as-measured Match **and** +1 floor) | +1 |
| **P5 cold-convex obj-grad (CGE `stat_xp`)** | `irscge`, `lrgcge`, `moncge` (one ν_objective reduction → several cold; rel ~0.06 after the S30 case-normalization fix) | +1 to +3 |
| **P1 head-offset (#1443, mine)** | `mine` — infeasible → optimal; **+1 genuine floor** if the cold LCP also cold-matches (also +1 Solve) | +0 to +1 |

> **⚠️ Conditionality (Sprint-30 retrospective §3, lesson 3 — binding for Sprint 31).** The genuine-floor lift proved *less robust than projected* in Sprint 30 because its contributors are entangled with non-convexity / general-alias differentiation: **"Sprint-31 planning should treat the genuine-floor ramp (→ ≥73/75/78) as conditional on the #1111/#1112 core + the dual-consistent CGE work, not as independent +1s."** So the +3 (70 → ≥73) has *nominal* headroom, but each contributor carries a Task-7 REPLAN exit. **himmel16 is NOT a converter** — it is documented **non-convex** (Sprint 30 Day-7 sign-fix refuted; no emit fix converts it), a change from the Sprint-30 P5 framing.

---

## 3. Per-Sprint-31-Target Bucket Provenance

Per-model trajectory: Sprint 30 final (= Sprint 31 Day-0) bucket + the gating issue + the **PR25 projection label** (genuine bucket-to-success vs methodology-already-banked). Buckets pinned from the committed DB.

| Model / Track | Day-0 bucket | Gating issue | Projected delta | PR25 label |
|---|---|---|---|---|
| **mine** (P1) | `model_infeasible` (16747.072) | #1443 head-offset **IR plumbing** + shared 3-site helper (foundational IR change; REPLAN'd S30 Day 6) | +1 Solve (+1 genuine floor if cold-matches) | **genuine** (infeasible → optimal) |
| **polygon** (P2) | `model_optimal_presolve` + **match** (0.7797) | #1111/#1112 offset-alias general-alias core (distance-Jacobian second-index; obj-half reverted S30 Day 8) | 0 net Match; **+1 genuine floor** | **methodology → genuine** |
| **himmel16** (P2 scope guard) | `model_optimal_presolve` + **match** (0.675) | documented **non-convex** (S30 Day-7 sign-fix refuted) | 0 (no emit fix) | **non-convert** (non-convex) |
| **camcge** (P3) | `model_infeasible` (0.0) | #1330 **dual-consistent** Walras transform (Epic 5; naive drop-row breaks the MCP dual, S30 Day 11) | +1 Solve (if the dual-consistent redefinition reaches MS 1 @ omega 191.735) | **genuine** (infeasible → optimal), Epic-5 |
| **sarf** (P4) | `translate_failure` | #1385 symbolic runtime-guard cross-terms (2-D dynamic-subset; REPLAN'd S30 Day 9) | +1 Translate (if the O(constraints) atomic re-emit lands) | **genuine** (translate_failure → translate) |
| **hhfair** (P5) | `model_optimal` + **mismatch** (72.147) | cold-convex obj-grad **ν_objective reduction** (sign-flip control-refuted 3× in S30) | +1 Match (firm if the reduction reaches the NLP optimum) | **genuine** (mismatch → match) — new genuine, +as-measured |
| **irscge/lrgcge/moncge** (P5) | `model_optimal_presolve` + **match** (26.09/25.77/25.98) | CGE `stat_xp` obj-grad reduction (rel ~0.06 after S30 case-normalization) | 0 net Match; **up to +3 genuine floor** (one fix, several cold) | **methodology → genuine** |
| **rocket** (P6) | `model_infeasible` (1.137) | #1462 non-convex forcing → **PATH-consultation input** (`--force` scaffold landed S30; intrinsic non-convergence) | **conditional** +1 Solve OR the finalized Sprint-32 PATH-consultation hand-off | **genuine** (infeasible → match), conditional |

### Key scope findings (PR25 discipline)

1. **Solve ≥ 109 rests on mine (P1) + camcge (P3), with rocket (P6) a conditional third.** mine (P1, foundational IR plumbing) and camcge (P3, dual-consistent Walras) are the two firm headline Solve movers this sprint; rocket (P6) is a *conditional* +1 (or a clean Sprint-32 PATH-consultation hand-off). All three are REPLAN-prone (Task 7). model_infeasible ≤ 5 needs ≥ 2 of {mine, camcge, rocket} to recover.
2. **Most Match-side tracks are genuine-floor (re-baseline) work, not as-measured +Match.** polygon (P2) and the CGE cluster irscge/lrgcge/moncge (P5) already **match via the warm-start** — their Sprint-31 fixes convert methodology matches into genuine cold matches (raising the floor 70 → ≥ 73), they do **not** move the as-measured 92. The two as-measured +Match tracks are **hhfair** (P5, mismatch → match) and **rocket** (P6, infeasible → match, conditional).
3. **+Translate is a single-model track (sarf, P4 #1385)** — the other timeout-cohort members (iswnm/mexls/nebrazil) remain translate-failures (not Sprint-31-scoped).
4. **The genuine-floor ramp is conditional (Sprint-30 retro §3).** Treat polygon [P2] + hhfair/CGE [P5] + mine [P1] as *conditional* on the #1111/#1112 general-alias core, the ν_objective reduction, and the head-offset IR plumbing respectively — not as independent +1s. Each has a Task-7 REPLAN exit.

### PR25 Projection Tally (genuine bucket-to-success only)

- **Solve (107 → ≥ 109):** genuine = mine +1 (#1443) + camcge +1 (#1330 Epic-5 dual-consistent) → **109**; rocket +1 (#1462) is a conditional third. REPLAN-gated (Task 7).
- **Match (92 as-measured → maintain ≥ 92):** genuine new transitions = hhfair +1 (P5) + rocket +1 (#1462, conditional) → **93–94** if both land; the methodology→genuine conversions (polygon/CGE cluster) do **not** move the as-measured 92.
- **Genuine floor (70 → ≥ 73):** polygon +1 (P2) + hhfair +1 (P5) + CGE cluster +1–3 (P5) + mine +0–1 (P1 if cold-matches) → **≥ 73** with nominal headroom, **conditional** on the #1111/#1112 core + the obj-grad reduction (retro §3).
- **Translate (135 → stretch 136):** sarf +1 (#1385) if the O(constraints) symbolic runtime-guard re-emit lands.
- **model_infeasible (7 → ≤ 5):** −2 via any two of mine/camcge/rocket.
- **Bucket-forward / no target credit:** the already-banked methodology matches (polygon/CGE cluster) until a Sprint-31 cold fix reclassifies them genuine.

**Footnote-⁸ ramp alignment (PROJECT_PLAN):** the Sprint-31 genuine floor sits on the re-baselined ≥ 64% as-measured Match line, and the genuine-floor ramp is **S30 actual 70 → S31 ≥ 73 → S32 maintain ≥ 73 → S33 ≥ 75 → S34 ≥ 78** (footnote ⁸). This Day-0 baseline (floor 70) is the ramp's S30 anchor; Sprint 31 targets the S31 ≥ 73 step.

---

## 4. Scope Freeze (PR17)

- **In-target (genuine, headline-moving):** mine (#1443, +1 Solve — head-offset IR plumbing), camcge (#1330, +1 Solve via the Epic-5 dual-consistent Walras transform), hhfair (P5 obj-grad, +1 Match), sarf (#1385, +1 Translate), rocket (#1462, conditional +1 Solve / Sprint-32 PATH-consultation hand-off).
- **In-target (genuine emit-correctness, re-baseline / genuine-floor only):** polygon (P2 #1111/#1112), the CGE cluster irscge/lrgcge/moncge (P5) — convert methodology matches into genuine cold matches (raise the floor 70 → ≥ 73) without moving the as-measured 92.
- **Out-of-scope / Sprint-32-deferred (REPLAN exits):** the #1443 mine **4th-site** slip (deeper IR architecture), the #1111/#1112 offset-alias **AD-engine core** if the tight gate leaks, the #1385 sarf **timeout re-trigger**, the P5 **genuine Case-c** non-convexity finding, the rocket **PATH-option** forcing (all Task-7 REPLAN exits). **himmel16** documented non-convex (no emit fix).
- **Committed regression-guard sets:** the 92 matching + 107 solving models (the Sprint-30-final sets) — any Sprint-31 emit change must re-solve the changed-golden subset (`--resolve-changed`, Day-5/Day-10 checkpoints) and not regress these.

### Checkpoint anchor (PR15 / Priority-8 `--resolve-changed`)

The Day-5 / Day-10 checkpoint re-solve anchors on the Sprint-30 close SHA:

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit ea4191dc
```

At **Day 0** this selects **0 models** — `git diff --name-only ea4191dc..HEAD -- 'data/gamslib/mcp/*_mcp.gms' 'data/gamslib/mcp/*_mcp_presolve.gms'` is empty (no emit golden has changed since the close), confirming the clean baseline. During Sprint 31, as the emit sites change (the head-offset core, `_add_indexed_jacobian_terms`, the Walras redefinition, the sarf symbolic emit), the anchor selects exactly the emit-touched models for a bounded re-solve rather than a full ~4 h pipeline run.

---

**Document Created:** 2026-07-08
**Owner:** Sprint 31 Planning Team
**Authoritative scheduling budget:** the per-task totals in `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` (35–49 h across Tasks 1–10).
