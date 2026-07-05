# Sprint 30 Day-0 Baseline Metrics + Bucket Provenance + Re-Baseline Discipline

**Task:** Sprint 30 Prep Task 2 (PR15 + PR17 + PR25)
**Day-0 source:** Sprint 29 final state (the "SPRINT 29 CLOSED" commit `68b5b4a7`, 2026-07-01) — reused unchanged; no fresh retest.
**Owner:** Sprint 30 Planning Team

---

## 0. Day-0 = Sprint 29 Final (no fresh retest)

`git diff <S29-close>..HEAD -- src/ scripts/` is **empty** — no `src/` or `scripts/` drift since the Sprint 29 close, so the Day-0 metrics equal the Sprint 29 final without a ~4 h retest.

```bash
# The robust close-SHA anchor (see the finding below): pin the subject-anchored commit.
S29=68b5b4a7fb195f4486cedc274440282840c9a4f5   # "Sprint 29 Day 13: final retest + closeout — SPRINT 29 CLOSED"
git diff --quiet "$S29"..HEAD -- src/ scripts/ && echo "no src/ drift — reuse the committed DB" || git diff --stat "$S29"..HEAD -- src/ scripts/
# → no src/ drift — reuse the committed DB
```

**Two confirmations that Day-0 = Sprint 29 final:**

1. **No `src/`/`scripts/` drift** since `68b5b4a7` — every commit since the close (PRs #1489 Sprint-30 PROJECT_PLAN insertion, #1490 Sprint-30 prep) is docs-only.
2. **The committed DB (`data/gamslib/gamslib_status.json`) is byte-unchanged since the Sprint 28 close** (`2717d542`, 2026-06-21) — because **Sprint 29 netted no bucket change**: all three headline movers (mine #1443, rocket #1462, hhfair #1236) REPLAN'd, and the firm deliverables (the `_fx_` warm-start, the #1447 maxmin objvar fix, catmix) were **cold-correctness / genuine-floor** wins that did not move any as-measured Solve/Match bucket. So the Sprint 28 close DB *is* the Sprint 29 final DB, and the recompute below reproduces the Sprint 29 final headline exactly.

> **⚠️ Finding (PR24-style latent-bug in the prep snippets).** The auto-deriving snippet the Task-2 prompt / `PREP_PLAN.md` / `KNOWN_UNKNOWNS.md` use — `git log --grep='SPRINT 29 CLOSED' -1 --format=%H` — is now **ambiguous**: three later prep commits (PR #1490's "Address PR #1490 review comments" and the merge) quote the literal phrase "SPRINT 29 CLOSED" in their bodies, so `-1` (newest match) resolves to a **docs-only review-fix commit (`7a2d30e3`)**, not the true close (`68b5b4a7`). For the drift check the *result* is identical (every commit in between is docs-only → still "no `src/` drift"), so the check is not wrong — but the reported SHA is misleading. **Robust forms:** pin the SHA (as above), or anchor on the subject with `git log --grep='SPRINT 29 CLOSED' --format=%H | tail -1` (oldest match = the real close). The runnable Verification snippets in `PREP_PLAN.md` (Task 2), `KNOWN_UNKNOWNS.md` (Unknown 8.2), and `prompts/PREP_TASK_PROMPTS.md` (Task 2) now use the robust `git log --grep='SPRINT 29 CLOSED' --format=%H | tail -1` form (verified to resolve to `68b5b4a7`); this §0 block pins the SHA directly. Task 8 (tooling audit) + Task 10 (schedule) should keep to the pinned/`tail -1` form.

---

## 1. Day-0 Headline Counts (142-model GAMSlib corpus)

Recomputed from the committed DB over the **canonical 142-model scope** (`get_candidate_models` = `convexity.status ∈ {verified_convex, likely_convex}`). Reproduces the Sprint 29 final headline (`docs/planning/EPIC_4/SPRINT_29/SPRINT_LOG.md` §"Day 13").

| Metric | Sprint 30 Day 0 | Sprint 30 Target | Gap |
|---|---|---|---|
| Parse | **142** / 142 | ≥ 142 | met |
| Translate | **135** / 142 | ≥ 135 (stretch +1 via #1385) | met (maintain) |
| Solve (`model_optimal[_presolve]`) | **107** / 142 | ≥ 109 | −2 (mine + rocket) |
| Match (`compare_objective_match`) | **92** / 142 | maintain ≥ 92 / **genuine floor 69 → ≥ 72** | met / −3 to floor |
| Mismatch (`compare_objective_mismatch`) | **9** | — | (solved-but-diverging) |
| path_syntax_error | **8** | maintain ≤ 8 | met |
| path_solve_terminated | **4** | ≤ 5 | met |
| model_infeasible | **7** | ≤ 5 | −2 (mine + rocket) |
| Tests | **~4,971** | ≥ 4,990 | −19 |

Recompute (canonical scope, committed DB): **Parse 142 · Translate 135 · Solve 107** (63 `model_optimal` + 44 `model_optimal_presolve`) **· Match 92 · Mismatch 9 · multi-solve-skip 6 · not-tested 35** (the 7 translate-fails + the 28 solve-fails/uncompared). Of the 107 solved, 92 match, 9 mismatch, 6 are uncompared (`compare_multi_solve_skip`).

> **Scope note.** A naive recompute over every translate-success row returns 115 solve / 92 match / 17 mismatch — it includes 8 out-of-scope non-NLP/QCP rows (`abel` + `ps10_s`/`ps2_f_s`/`ps2_s`/`ps3_s`/`ps3_s_gic`/`ps3_s_mn`/`ps3_s_scp`). The canonical `get_candidate_models` scope excludes them → the authoritative Solve 107 / Match 92.

### Failure-bucket membership (frozen Day-0 reference)

- **Translate failures (7):** `danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, **`sarf`**.
- **model_infeasible (7):** `agreste`, `camcge`, `cesam`, `fawley`, `lnts`, **`mine`**, **`rocket`**.
- **path_syntax_error (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`.
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`.
- **path_solve_terminated (4):** `dyncge`, `elec`, `tricp`, `twocge`.
- **mismatch (9):** `abel`-excluded; the in-scope 9 = `chain`, `china`, `circle`, **`hhfair`**, `imsl`, `lmp2`, `prodsp2`, `spatequ`, `trig`.

The Sprint 30 target models are highlighted: **mine** + **rocket** (model_infeasible), **hhfair** (the live objective-mismatch, P3), **sarf** (translate-failure, P4 #1385).

---

## 2. Re-Baseline: Genuine vs Methodology Match Split (PR25)

The as-measured Match 92 carries forward from Sprint 28's 62 → 92 (+30) jump, whose decomposition is **+7 genuine + ~24 methodology − 1 stale-baseline** (`SPRINT_28/SPRINT_LOG.md` §"Day 13"). Sprint 29 then raised the **genuine floor 68 → 69** (Days 3–4: the #1447 maxmin objvar `-1` fix + catmix recovery, both cold-correctness — polygon withdrawn Day 5) while the as-measured 92 stayed flat (no pipeline-methodology change landed). So Sprint 30's re-baseline floor is **69**, methodology **23**.

| Component | Count | Notes |
|---|---|---|
| **Genuine, stable** (the re-baseline floor) | **69** | the Sprint-28 genuine 68 (cold matches incl. otpop/chakra/chenery/kand/srkandw + the 6 non-methodology presolve matches) **+1** from Sprint 29 (maxmin reclassified genuine after #1447; catmix recovered) |
| **Methodology-recovered** (Day-9 presolve-retry-on-cold-mismatch broadening, `_cold_objective_mismatches_nlp`) | **~23** | himmel16, weapons, harker, polygon, sambal, markov, worst, irscge, lrgcge, moncge, stdcge, like, robert, mathopt1, mathopt4, mingamma, paperco, qsambal, marco, etamac, cpack, tforss (+ the residue of the Sprint-28 set minus maxmin/catmix now genuine) |
| **As-measured total** | **92** | — |

**Operational definition** of the methodology set (unchanged from PR25): `mcp_solve.outcome_category = model_optimal_presolve` **AND** `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*), cold emit byte-identical to its pre-Day-9 state. These are *already emit-correct* models the broadened retry warm-start-*validates* — not repeatable cross-term gains.

**Genuine-floor → ≥ 72 conversion map (Sprint 30 tracks that convert a methodology/warm match into a genuine cold match, +1 genuine floor each):**

| Track | Methodology models it converts | Genuine-floor delta |
|---|---|---|
| **P1 head-offset (#1443 robert)** | `robert` (cold head-offset fix → genuine cold match) | +1 |
| **P5 offset-alias (#1146/#1143)** | `himmel16`, `polygon` (cold offset-alias fix) | +1 to +2 |
| **P7 Class-B CGE `stat_pz`** | `irscge`, `lrgcge`, `moncge`, `stdcge`, `marco` (one general-emit fix → several cold) | +1 to +5 |
| **P3 hhfair (#1236)** | `hhfair` — *not* methodology (currently **mismatch**); a fix is a **new** genuine match (+1 as-measured Match **and** +1 floor) | +1 |

Ample headroom for the +3 genuine-floor target (69 → ≥ 72) even if only the highest-residual model of each cluster converts.

---

## 3. Per-Sprint-30-Target Bucket Provenance

Per-model trajectory: Sprint 29 final (= Sprint 30 Day-0) bucket + the gating issue + the **PR25 projection label** (genuine bucket-to-success vs methodology-already-banked / bucket-forward). Buckets pinned from the committed DB.

| Model / Track | Day-0 bucket | Gating issue | Projected delta | PR25 label |
|---|---|---|---|---|
| **mine** (P1) | `model_infeasible` | #1443 head-domain-offset (multi-site, REPLAN'd S29) | +1 Solve (+1 genuine Match if cold-matches) | **genuine** (infeasible → optimal) |
| **robert** (P1) | `model_optimal_presolve` + **match** (11025.0) | #1443 head-offset (constant-offset sub-case; minimal reproduction) | 0 net Match; **+1 genuine floor** (methodology → genuine cold) | **methodology → genuine** |
| **rocket** (P2) | `model_infeasible` | #1462 non-convex forcing (`_fx_` warm-start landed; intrinsic non-convergence) | +1 Solve / +1 Match (if a forcing lever works) | **genuine** (infeasible → match) |
| **hhfair** (P3) | `model_optimal` + **mismatch** (72.147 vs 87.159) | #1236 `$184` widened-VARIABLE + CES verdict | +1 Match (firm if Case b after the `$184` compile) | **genuine** (mismatch → match) — new genuine, +as-measured |
| **sarf** (P4) | `translate_failure` | #1385 symbolic runtime-guard cross-terms | +1 Translate (if the atomic re-emit lands) | **genuine** (translate_failure → translate) |
| **polygon / himmel16** (P5) | `model_optimal_presolve` + **match** (0.7797 / 0.675) | #1146/#1143 offset-alias (coupled w/ distance-Jacobian; reverted S29 Day 5) | 0 net Match; **+1–2 genuine floor** (cold-robustness) | **methodology → genuine** |
| **camcge** (P6) | `model_infeasible` | #1330 Walras degeneracy → Epic 5 transformation | +1 Solve (if the transform empirically reaches MS 1) | **genuine** (infeasible → optimal), Epic-5 preprocessing |
| **irscge/lrgcge/moncge/stdcge** (P7) | `model_optimal_presolve` + **match** (26.09/25.77/25.98/26.09) | Class-B CGE `stat_pz` general-emit (NOT Walras, S29 Day 12) | 0 net Match; **up to +4 genuine floor** (one fix, several cold) | **methodology → genuine** |
| **marco** (P7) | `model_optimal_presolve` + **match** (0.0) | Class-B residue (`stat_w`, model-specific) | 0 net Match; +≤1 genuine floor | **methodology → genuine** |

### Key scope findings (PR25 discipline)

1. **Solve ≥ 109 rests on the two infeasible-recoveries (mine + rocket) plus camcge.** mine (P1) and rocket (P2) are the firm headline Solve movers; camcge (P6) is a third potential +1 Solve via the Epic-5 Walras transform. All three are REPLAN-prone (Task 6). model_infeasible ≤ 5 needs ≥ 2 of {mine, rocket, camcge} to recover.
2. **Most Match-side tracks are genuine-floor (re-baseline) work, not as-measured +Match.** robert (P1), polygon/himmel16 (P5), and the Class-B CGE cluster (P7) already **match via the warm-start** — their Sprint-30 fixes convert methodology matches into genuine cold matches (raising the floor 69 → ≥ 72), they do **not** move the as-measured 92. The two as-measured +Match tracks are **hhfair** (P3, mismatch → match) and **rocket** (P2, infeasible → match).
3. **+Translate is a single-model track (sarf, P4 #1385)** — the smallest of the Sprint-29 timeout cohort; the other cohort members (iswnm/mexls/nebrazil) remain translate-failures (not Sprint-30-scoped).

### PR25 Projection Tally (genuine bucket-to-success only)

- **Solve (107 → ≥ 109):** genuine = mine +1 (#1443) + rocket +1 (#1462) → **109**; camcge +1 (#1330 Epic-5) is a conditional third. REPLAN-gated (Task 6).
- **Match (92 as-measured → maintain ≥ 92):** genuine new transitions = hhfair +1 (#1236) + rocket +1 (#1462) → **94** if both land; the methodology→genuine conversions (robert/polygon/himmel16/Class-B) do **not** move the as-measured 92.
- **Genuine floor (69 → ≥ 72):** robert +1 (P1) + polygon/himmel16 +1–2 (P5) + Class-B CGE +1–5 (P7) + hhfair +1 (P3) → **≥ 72** with headroom.
- **Translate (135 → stretch 136):** sarf +1 (#1385) if the atomic runtime-guard re-emit lands.
- **model_infeasible (7 → ≤ 5):** −2 via any two of mine/rocket/camcge.
- **Bucket-forward / no target credit:** the already-banked methodology matches until a Sprint-30 cold fix reclassifies them genuine.

---

## 4. Scope Freeze (PR17)

- **In-target (genuine, headline-moving):** mine (#1443, +1 Solve), rocket (#1462, +1 Solve/+1 Match), hhfair (#1236, +1 Match after the `$184` compile), sarf (#1385, +1 Translate), camcge (#1330, +1 Solve via Epic-5).
- **In-target (genuine emit-correctness, re-baseline / genuine-floor only):** robert (P1), polygon/himmel16 (P5), the Class-B CGE cluster irscge/lrgcge/moncge/stdcge/marco (P7) — convert methodology matches into genuine cold matches (raise the floor 69 → ≥ 72) without moving the as-measured 92.
- **Out-of-scope / Sprint-31-deferred (REPLAN exits):** the #1443 mine multi-site slip, the #1462 rocket PATH-option forcing, the #1111/#1112 offset-alias AD-engine core, the camcge per-model-numéraire fallback (all Task-6 REPLAN exits).
- **Committed regression-guard sets:** the 92 matching + 107 solving models (the Sprint-29-final sets) — any Sprint-30 emit change must re-solve the changed-golden subset (`--resolve-changed`, Day-5/Day-10 checkpoints) and not regress these.

---

**Document Created:** 2026-07-05
**Owner:** Sprint 30 Planning Team
**Authoritative scheduling budget:** the per-task totals in `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` (34–48 h across Tasks 1–10).
