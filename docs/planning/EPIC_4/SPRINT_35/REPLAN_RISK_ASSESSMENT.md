# Sprint 35 — Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment + Honest KPI Projection (PR16)

**Prep Task:** 11 (High, on the critical path) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (risk/projection)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `047284de` (`main` at the S35 prep Task-10 merge)
**Scope:** docs-only — applies the PR16 hypothesis-validation discipline to the deep/new tracks, pins the REPLAN exits + freed-budget reallocation, and authors the honest KPI projection + the front-load ordering. No `src/` change.

---

## Executive summary — the structural change from S32/S33/S34

**The three deep tracks did not enter Sprint 35 with un-built fixes to gamble on — they REPLAN'd/deferred IN PREP.** Tasks 6/7/8/9 ran each track's control (or its reachability screen) *before* Day 1 and resolved its disposition:

| Track | Carry | Prep task | Prep disposition | In-sprint REPLAN prior |
|---|---|---|---|---|
| **P1 mine** (#1443) | **×4** (S32→S35) | Task 6 | **REPLAN'd in prep** — the whole keying/pairing space is value-invariant (S34 proved H_dual); no candidate reaches cold-MS-1 | **RESOLVED (already exited)** — 0 bucket |
| **P2 sarf** (#1385) | **×3** (S33→S35) | Task 7 | **DEFER'd in prep** — 20–28 h foundational re-architecture for the lowest-leverage KPI; measured baseline > 303 s | **RESOLVED (already exited)** — 0 bucket |
| **P3 fawley** (#1111/#1112) | **×3** (S33→S35) | Task 8 | **PROCEED correctness-only** — but H-b (re-confirmed + strengthened by the `stat_trans` re-measurement) → **0 bucket** | **Live but 0-bucket** — the only risk is a gate-leak (a correctness regression) |
| **P4 ganges/gangesx** | 1 (NEW first-class) | Tasks 4+5 | **PROCEED (per-root)** — the sole live bucket gate; +2 target | **THE ONLY LIVE IN-SPRINT REPLAN RISK** |
| **P5 camcge/rocket** | — | Task 9 | camcge Epic-5-deferred; rocket → Sprint 36 | a-priori non-mover — 0 bucket |

**So this assessment is fundamentally different from its three predecessors.** In S32/S33/S34 the deep-track REPLAN priors were *prospective probabilities* resolved at Day-1/5/6. In Sprint 35 they are **already resolved** — the risk assessment for P1/P2/P5 is *retrospective* (they've exited), and **the only live in-sprint REPLAN risk is P4's `$149` AD-core fix.** The projection is therefore not "modal-flat beaten maybe by P6"; it is **bimodal on P4**: either P4 lands **+2** (ganges/gangesx recover) or the sprint is **flat**. P4 *is* the failure-cohort class the S33 sample precedent identified as the genuine bucket source — now promoted to first-class and the sole determinant.

**The decisive three-sprint record (the argument for P4-first):** mine ×4, sarf ×3, fawley ×3 have between them consumed roughly half of three sprints' budget and moved **zero** buckets; the only genuine move in that window was S33's P6 sample (the failure cohort). Sprint 35 has now *spent the deep-track design budget in prep* and confirmed 0 in-sprint bucket from all three — so the entire in-sprint bucket hope is **P4 (+ the P6 residual cohort)**, the failure-cohort class. **Front-load P4 from Day 1.**

---

## Track P1 — mine Head-Offset Dual Subsystem (#1443)

**Prep disposition (Task 6):** REPLAN — decided in prep. No emit-side dual architecture can supply the +16000 the `x.m = 0`-degenerate boundary requires; the whole keying/pairing candidate space is value-invariant (S34 proved H_dual value-invariant on the cold solve), and the only non-invariant lever (an LP-side reformulation) is out of emit scope.

**In-sprint REPLAN prior: RESOLVED (already exited).** mine is **four-times-carried** (S32 5th-coupling / S33 H1 / S34 H_dual — each control-refuted; S35 Task 6 screened the *entire* remaining candidate space to zero). There is no fifth in-sprint hypothesis to gamble on — the refuting evidence (value-invariance) is already in hand.

**Refuting evidence + earliest surfacing:** already surfaced (in prep). The cold-MS-1-@-17500 gate is un-reachable; the S34 Day-1 control already refuted the strongest candidate. No Day-5 check needed.

**Exit + reallocation:** mine → the **Sprint-36 PATH consultation** (the primal-degenerate-LP question, bundled with rocket by Task 9); **no `src/`**; the 18–24 h P1 design budget was **spent in prep** — its *in-sprint* footprint is ~0 h (a documentation line + the Sprint-36 hand-off, already in Task 9's bundle). **0 in-sprint bucket / 0 floor.**

---

## Track P2 — sarf Symbolic/Parametric `stat_task` Emit (#1385)

**Prep disposition (Task 7):** DEFER — decided in prep. The design is complete and shippable-to-a-dedicated-effort, but the in-sprint risk/reward is unchanged from S32/S33/S34: a 20–28 h foundational AD-core re-architecture (all 142 models, atomic, no safe partial) for the **lowest-leverage KPI** (+1 Translate).

**In-sprint REPLAN prior: RESOLVED (already exited).** The measured baseline (> 303 s, non-terminating) and the corpus-safety surface (6 call sites) are pinned; the DEFER is a deliberate scope/risk call, the fourth consecutive one.

**Exit + reallocation:** sarf stays `translate_failure` (Translate 135); **no `src/`**; the 20–28 h P2 design budget was **spent in prep** — its in-sprint footprint is ~0 h. Freed → P4/P6/P7. **0 in-sprint bucket.**

---

## Track P3 — fawley Constraint-Index-Diagonal Correction + Forcing (#1111/#1112)

**Prep disposition (Task 8):** PROCEED for correctness IF leak-free — but **0 in-sprint bucket** (H-b, re-confirmed and *strengthened* by the live re-measurement: the emit-correct `stat_trans(tr-2)` residual is now the harness max, confirming the divergence is non-emit).

**In-sprint REPLAN prior: Medium (correctness gate-leak) — but the bucket is 0 either way.** The only risk is that the constraint-index-diagonal guard **leaks onto the mbal term or the 2-D cohort** (cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon) or regresses the 1-D core — a *correctness regression on currently-passing models*, which forbids shipping. **Refuting evidence:** the `/tmp` control does not reach `max|stat_bq| → 0`, OR any cohort/mbal golden changes under `--resolve-changed`. **Earliest surfacing:** the `/tmp` control + the cohort byte-diff, both pre-`src/` (measurable early).

**Exit + reallocation:** gate leak → DEFER again (a dedicated effort + the 2-D-cohort harness); budget → P4. **Crucially: P3 moves 0 in-sprint bucket whether it lands or not** (fawley stays `model_infeasible` under H-b), and its +1 genuine floor is contingent on a cold match that H-b precludes without forcing → the +Solve is a **Sprint-36 `--force` survey** item (Task 9's bundle). So P3 is a **low-priority correctness-only landing** that must not displace P4.

---

## Track P4 — ganges/gangesx Multi-Root Recovery — **THE SOLE LIVE BUCKET GATE**

**Prep disposition (Tasks 4+5):** PROCEED (per-root `$141`→`$145`→`$149`). Target **+2 Solve / +2 Match / −2 path_syntax_error** (+2 genuine floor if ganges/gangesx **cold**-match). `$149` is a code, not a root — only ganges/gangesx are product-rule beneficiaries.

**Per-root REPLAN priors:**
- **`$141` — Low.** The banked fix is **written + re-validated this sprint** (Task 5, scratch re-emit: 15 → 0). The only residual is collateral golden regeneration (~9 `.l`-calibration models), which Task 3 **measured** as regenerable (~8.2 min scoped, fits a normal day).
- **`$145` — Low.** A bounded universal-set (`*`-domain) skip; independence from `$141` verified.
- **`$149` — Medium-High. THIS is the sprint's live REPLAN risk.** The AD-layer `_diff_prod` correction (Task 4) must be made **surgical** — drive ganges's 9 `$149` → 0 while keeping the **18-model prod-in-stationarity regression set byte-identical** (lmp2 the most sensitive — the name-match case the collapsed `_diff_prod` branch relies on). If the fix requires a general restructure of `prod` differentiation that perturbs those 18, it REPLANs.

**Refuting evidence + earliest surfacing:** the `$149` `/tmp` control (before `src/`) — does the correction reproduce Task 4's hand-derived `stat_pc` cross-term AND leave the 18 regression goldens byte-identical? **Measurable by the Day-5 checkpoint IF P4 is front-loaded** (the reason it must run early). A second refutation risk: even if all three roots land clean, **do ganges AND gangesx each actually solve-and-match** (Unknown 4.4, DESIGN-SPECIFIED — the exact assumption S34 got wrong; a fourth per-model root could surface at the compile step).

**Exit + reallocation:** `$149` not surgical → **bank all three** (steps 1–2 alone = 0 bucket + golden churn — the S34-banked outcome; no `src/` ships) and reallocate P4's 14–20 h → **P6** (the residual cohort — the *second* bucket source) + **P7**. **No bucket moves until all three roots land** (Task 5, empirically proven).

**Prior of REPLAN: Medium-High on `$149`; Low on `$141`/`$145`.** P4 is the sole track that can move a bucket, and its bucket is gated on the one deep AD-core fix in the sprint. This is the honest asymmetry: P4 is the *best* shot **and** carries the sprint's only live deep-fix risk.

---

## P5 dispositions (non-firm KPI movers, in the projection for completeness)

**P5-camcge — Epic-5-deferred (Task 9): 0 in-sprint bucket / 0 floor.** The full dual-consistent Walras redefinition's `/tmp` MS-1 gate is **expected MS-4** (the price-pin variant + 3+ sprints of variants all stayed MS-4 at the correct primal); the per-model-numéraire declaration is the documented Epic-5 fallback. camcge is **explicitly excluded from the in-sprint Solve target.** In-sprint footprint: a small slot for the Epic-5 `/tmp` gate (the a-priori-MS-4 confirmation).

**P5-rocket — Sprint-36 hand-off (Task 9): 0 genuine floor.** Case-c re-confirmed live (CASE_C_OBJDEF, dual CONSISTENT); the FINALIZED input submits to **Sprint 36** (with the "Sprint 33"/"Sprint 35" labels retargeted — Task 9's renumbering fix). The sign flip is BANNED (4×). In-sprint footprint: packaging the Sprint-36 bundle (rocket + mine + fawley), a small slot.

---

## Budget-at-risk tally + the retrospective-budget finding

| Track | PROJECT_PLAN sizing | **In-sprint footprint (design spent in prep)** | Bucket at stake | Prior of REPLAN |
|---|---|---|---|---|
| P1 mine | 18–24 h | **~0 h** (REPLAN'd in prep; doc + Sprint-36 hand-off) | 0 | RESOLVED |
| P2 sarf | 20–28 h | **~0 h** (DEFER'd in prep; design done) | 0 | RESOLVED |
| P3 fawley | 12–18 h | **12–18 h IF attempted** (correctness-only, 0 bucket — deferrable) | 0 | Medium (gate-leak) / bucket 0 either way |
| **P4 ganges/gangesx** | 14–20 h | **14–20 h (the sole bucket work)** | **+2** | Med-High on `$149` |
| P5 camcge/rocket | 10–16 h | **~2–4 h** (Epic-5 `/tmp` gate + Sprint-36 bundle) | 0 | a-priori non-mover |
| P6 residual cohort | 8–14 h | **8–14 h (the second bucket source)** | up to +1–2 | (per-model, Task 4 catalog) |
| P7 infrastructure | 6–10 h | 6–10 h | — | — |
| retest | 4 h | 4 h | — | — |

> **The honest budget finding: the 92–134 h estimate is now MOSTLY RETROSPECTIVE.** P1 (18–24 h) + P2 (20–28 h) — ~38–52 h of the estimate — were **spent in prep** (Tasks 6/7), not in-sprint. The **real in-sprint work** is P4 (14–20 h) + P6 (8–14 h) + P7 (6–10 h) + retest (4 h) + the small P5 slot (~2–4 h) + P3 (12–18 h, *optional*, 0 bucket) ≈ **34–70 h** — **less than half the 168 h cap, with enormous slack.** So the sprint can afford a **thorough P4 + P6 push** (the two bucket sources) rather than spreading budget across five deep tracks. The early-REPLAN reallocation is simple: if `$149` REPLANs, P4's freed budget joins P6/P7 (already the plan), and the sprint still has slack.

---

## Honest KPI projection (which KPI survives, given the prep dispositions)

The in-sprint mover set is **{P4 ganges·gangesx}** — plus the P6 residual cohort as a secondary source. P1/P2/P3/P5 are **all 0-bucket** (prep-resolved). So:

- **Solve 108 → +2 (110) IF P4 lands both ganges + gangesx; else 108.** Not P1 (REPLAN'd), not P2 (Translate), not P3 (H-b, +Solve is Sprint-36 forcing), not camcge (Epic-5). **The stretch ≥ 112 is a-priori REFUTED** — the PROJECT_PLAN's ">≥ 112 if the ganges pair + one deep track land" required a deep track, and all three REPLAN'd/deferred in prep; the max reachable is **110** (P4's +2), or **+1 more** only if the P6 residual cohort recovers a model (turkey `$161` or a dinam/indus/turkpow/clearlak *whole-root-set* — a-priori hard per Task 4's multi-root catalog).
- **Match ≥ 93 maintained; genuine floor 75 → +2 (77) ONLY IF ganges/gangesx COLD-match.** The floor needs a **cold-emit** mover that cold-matches — a warm-start/presolve-only match is methodology (0 floor by definition, the S34 P4 precedent). P1 (0), P3 (0 — H-b, no cold match without forcing), camcge (Epic-5) contribute nothing. **The entire floor gain is P4-contingent, and specifically on ganges/gangesx cold-matching (not presolve-only)** — an open question (Unknown 4.4, DESIGN-SPECIFIED).
- **Translate 135 maintained — no +1.** The PROJECT_PLAN's "+1 → 136 via sarf" is **off** (P2 DEFER'd in prep). Translate holds at 135.
- **path_syntax_error 7 → 5 (−2) IF P4 recovers both ganges + gangesx**; else 7. P6 could add −1 more (turkey/dinam/indus/turkpow/clearlak) if a whole root-set clears.
- **model_infeasible ≤ 7 maintained** — no in-sprint recovery of the model_infeasible cohort (mine/camcge/fawley/rocket/cesam/lnts/agreste all 0-bucket or Epic-5/forcing).

**The modal outcome is BIMODAL on P4, not "modal-flat":**
- **P4 lands (all three roots + both models cold-match):** Solve **110**, Match **95**, genuine floor **77**, path_syntax_error **5** — the sprint's headline.
- **P4 `$149` REPLANs (or a model doesn't cold-match):** **flat** — Solve 108, Match 93, floor 75, pse 7 — beaten only if P6 recovers a residual-cohort model.

Unlike S32/S33/S34 (modal-flat, one track maybe delivering), Sprint 35's outcome is **decided by the single P4 `$149` fix** — the deep tracks are already off the board. **Do not promise ≥ 112 or a floor > 77.**

---

## Front-load ordering (argued from the three-sprint record)

**P4 goes FIRST (Days 1–5), not the back half.** The argument, explicitly from the record rather than inherited:

1. **The three-sprint record says the failure-cohort track is the genuine bucket source** (S33 sample), and the deep tracks are not (mine ×4 / sarf ×3 / fawley ×3 = 0 buckets). P4 *is* the failure-cohort class, promoted to first-class. So it is the sprint's designated best shot and gets the prime slot — the exact inversion of the prior sprints' "deep tracks front-loaded, failure-cohort in the back half" that produced three flat closes.
2. **P4's `$149` `/tmp` control is the sprint's only live REPLAN gate** — front-loading it surfaces the REPLAN by the **Day-5 checkpoint** (the requirement), freeing budget to P6/P7 early if it exits.
3. **The golden-regeneration window does not constrain P4's start** — Task 3 measured the slow-emit regen at ~8.2 min scoped (fits a normal ≤ 12 h day; **no overnight slot needed**), so P4 can run Days 1–5 without reserving a nightly window. (Had it needed an overnight slot, P4 would start no later than the day before the Day-5 checkpoint.)

**Recommended ordering:** **P4 (Days 1–5, the bucket work + its `$149` REPLAN gate)** → **P6 (the residual cohort, the second bucket source — Task 4's per-model catalog)** → **P5 (the small camcge Epic-5 `/tmp` gate + the Sprint-36 submission bundle)** → **P3 (correctness-only, if attempted — 0 bucket, low priority, can defer)** → **P7 (fixtures + floor tracking + SUMMARY, back half)** → **retest (Day 13)**. P1/P2 need no in-sprint execution slot (prep-resolved). Checkpoints at Day 5 (P4 PROCEED/REPLAN) + Day 10; Day-13 final retest under ≥ 3 `PYTHONHASHSEED`.

---

## Known Unknowns verified by this task

- **Unknown 1.5** — ✅ **VERIFIED (Task-11 risk-assessment contribution; Task 6 the design primary).** P1's REPLAN prior is **RESOLVED (exited in prep)** — mine is four-times-carried with the entire candidate space screened to zero; no in-sprint hypothesis remains. Its 18–24 h design budget was spent in prep (in-sprint footprint ~0 h); the disposition is the Sprint-36 consultation, and the freed budget flows to P4/P6/P7.
- **Unknown 2.2 (Task-11 contribution)** — P2's timeout-re-trigger risk is **RESOLVED (DEFER'd in prep)** — the measured > 303 s baseline + the corpus-safety surface pin the risk; the 20–28 h design budget was spent in prep (in-sprint footprint ~0 h). Primary: Task 7.
- **Unknown 3.2 (Task-11 contribution)** — P3's gate-leak risk is **Medium**, but the **bucket is 0 either way** (H-b): the risk is a correctness regression on the 2-D cohort/mbal/1-D-core, surfaced by the pre-`src/` `/tmp` control + the cohort byte-diff. P3 is a low-priority correctness-only landing that must not displace P4. Primary: Task 8.
- **Unknown 4.5 (Task-11 contribution)** — the golden-regen budget **makes P4 shippable in-sprint** (Task 3 refuted the S34 "un-regenerable" premise: ~8.2 min scoped, fits a normal day, no overnight slot) — so P4 can be front-loaded Days 1–5 without a nightly window, and the S34-P4 "no bucket → no `src/`" exception is *satisfiable* if a bucket move materializes. Primary: Task 3.

**Handed to Task 12 (schedule):** P4-first (Days 1–5) with its `$149` REPLAN gate by Day 5; P6 second (the residual cohort); the small P5/P7 slots; P3 optional; P1/P2 no in-sprint slot; the bimodal projection (Solve 108 or 110; floor 75 or 77; **do not promise ≥ 112**) binds the acceptance criteria; the retrospective-budget finding (~34–70 h real in-sprint work vs the 168 h cap) gives ample slack for a thorough P4 + P6 push.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 11
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team
