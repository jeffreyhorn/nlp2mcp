# Sprint 37 Detailed Schedule (Day 0 + Days 1–13)

**Prep:** Tasks 1–11 complete (10 design/scoping docs + this schedule). **Anchor:** the S37 Day-0 *code* state = S36 close `935d94b7` (prep is docs-only); the `--resolve-changed --since-commit` / DB / banked-fingerprint anchor is **`78ceaead`** — the DB is byte-unchanged since it, and `src/kkt/stationarity.py` + `src/ad/derivative_rules.py` are **byte-identical** since it (the only `src/` delta is `emit_gams.py` +37 [S36 P7 robustlp] and `original_symbols.py` +52 [S35 turkey `$161`], both outside the S37 emit tracks — Task 2 `BASELINE_RECONFIRMATION.md`).
**Budget:** ≤ 12 h/day over 14 days (Day 0 + Days 1–13); 168 h cap; nominal **~116 h**. Risk **HIGH** (P1 and P4 both touch the shared `_add_indexed_jacobian_terms`; P2 and P5 are deep AD / re-architecture), mitigated by every track inheriting a **Sprint-36 empirically-reproduced diagnosis with proven components**.

---

## 1. Sprint 37 Goal

Land the Sprint-36 carryforwards. The sprint's shape is set by one asymmetry the prep phase confirmed from three independent directions: **markov is the only track that can move the genuine floor**, and its emission is already PROVEN in `src/` (S36 Day 2: `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16, cold MCP solved to the reference 2401.577 + match). Its sole blocker was the gate, and **Task 4 designed a discriminator that fires on exactly `['markov']` across 142 scanned models** after measurement refuted two earlier designs. So P1 is front-loaded Days 1–3 with the full-corpus leak gate on Day 2.

Everything else is bounded downward by prep rather than upward: **P2 ganges** is +2 or 0 with an honest modal 0 (two of five blockers now bounded, two deep); **P3** is a *send*, not an integration (the consultation was never transmitted); **P4 fawley** is 0-bucket by construction and its leak gate currently **fails**; **P5 sarf** is the lowest-leverage track (+1 Translate) and the sprint's largest single cost; **P6** is a 30-minute re-baseline plus a license-gated turkey; **P7** is mostly already on `main`.

## 2. Acceptance Criteria (honest projection)

| KPI | Day-0 (S36 close) | markov lands | markov REPLANs |
|---|---|---|---|
| **genuine floor** | **75** | **76** (+1, methodology→genuine) | **75** (flat) |
| Solve | 108 | 108, or **110** if P2 lands both ganges paths | 108 |
| Match | 93 | 93, or **95** with P2 | 93 |
| Translate | 135 | **136** if the sarf re-arch lands | 135 |
| path_syntax_error | 7 | **6** on the v54 re-baseline (turkey stale-entry correction), **5** if P2 lands | 7 or 6 |

Four things this table deliberately does **not** claim:

- **markov is +1 floor, not +1 Match.** markov already counts in Match 93 as a presolve (methodology) match. Landing it moves presolve-match 30 → 29 and cold-optimal 63 → 64 with **Match unchanged**. Reporting it as a Match gain would double-count (Task 10 §4).
- **The `path_syntax_error` 7 → 6 move is a stale-entry correction, not a win.** turkey's DB row predates the S35 `$161` fix by seven weeks; a *persisting* re-solve reclassifies it `path_syntax_error → path_solve_license` with **no Solve or Match change** (Task 8 §1). It must be reported in that category or it will read as a recovery.
- **fawley cannot contribute a bucket.** It is H-b: with `stat_bq` fully corrected the harness max is still the emit-correct `stat_trans(tr-2)` rel 1.00, the MCP stays MS-5, and the S36 `--force` survey was NEGATIVE (Task 6 §5). It is a 0-bucket correctness fix or nothing.
- **rocket's +1 is contingent on a human action, not on engineering.** The package has been submission-ready since 2026-07-15 across four sprint boundaries (Task 9 §1).

**Do not promise floor > 76 or Solve > 110.** Given four consecutive flat sprints, the realistic close is **floor 75 or 76, decided by markov**, with P2 the bimodal upside.

## 3. Sequencing Constraints (from the prep outputs)

- **P1 markov first (Days 1–3)** — the only floor lever, fully local (2 vars / 3 eqns, no testbed). Its full-corpus leak gate runs **Day 2**, so a REPLAN surfaces well before Checkpoint 1.
- **P4 fawley strictly after P1** — not a preference, a structure. Both sit in the same `if/elif` chain: fawley's branch is `elif not _did_dim_mismatch_alias_fix:` (`:7060`), and markov's path is the one that **sets that flag `True`** (`:6925`). A term taking markov's path cannot reach fawley's. Landing markov first also means fawley's leak-check runs against a tree already carrying markov — the configuration that must actually be proven clean (Tasks 4, 6, 10 §3).
- **P4 enters Day 7 with a FAILING gate.** `make leak-check MODEL=fawley` reported `LEAK: dinam, prolog, shale` (conjunct 1) and `LEAK: dinam, shale` (with conjunct 2). `prolog` is a live `model_optimal` + **match** model. Day 7's first job is narrowing conjunct 2 — its name-based test misses the AD layer's `__`-suffixed re-symbolisation — **not** landing (Task 6 §3, §6).
- **P5 sarf's P7 precondition is already satisfied** — the leak harness shipped to `main` in prep (Task 3). But sarf's gate is **inverted**: `make leak-check MODEL=sarf` **cannot work** (sarf has no golden, so `--expect-drift sarf` reports `NO-OP` and fails for a non-correctness reason). sarf's gate is **`make check-goldens` — zero drift across the 163 — plus sarf newly producing a golden, 163 → 164** (Task 7 §4).
- **P3's send moves to Day 0.** S36 scheduled it Day 11 — a slack-absorbing day — and it did not happen, for the fourth consecutive sprint. It costs minutes, and sending on Day 0 is the only way a reply can plausibly arrive inside the sprint (Task 9 §1).
- **P6's re-baseline is ~30 minutes, not a workstream.** Measured at ~12 s/model ⇒ ~30 min for 142; the 5 OBJ-GAP risk models showed **zero** bucket change under v54 (Task 8 §2). It runs async from Day 9 and is decided Day 10. turkey is **NO-GO** — no licensed >1000-row environment exists or is procurable.
- **Checkpoints:** Day 5 (P1 + P2 verdict), Day 10 (Checkpoint 2 + the v54 decision), Day 13 (final retest under ≥ 3 `PYTHONHASHSEED`).
- **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the Case-c objective-gradient sign flip BANNED (refuted ×4).**

## 4. Day 0 — Kickoff + baseline re-confirm + GO/NO-GO + **the P3 sends** (≤ 6 h)

Confirm Day-0 = S36 close (Solve 108 / Match 93 [63 cold + 30 presolve] / genuine floor 75 / Translate 135 / Parse 142 / mi 7 / pse 7 / all-219 96). Verify `git diff 78ceaead..HEAD -- src/` = only `emit_gams.py` +37 and `original_symbols.py` +52 (⇒ `stationarity.py` + `derivative_rules.py` byte-identical, so every banked fingerprint reproduces). Re-confirm the Task-2 fingerprints: **markov** `CASE_B` rel 13.3, dual CONSISTENT, ∈ the methodology partition; **ganges** the cascade surfaces + `a8ff626c` reachable; **fawley** `CASE_B`, `stat_bq` rel 0.973; **sarf** non-terminating at cap. Restate the PR25 tally (floor 75; the markov +1 is a partition transfer).

**Then do the thing that has slipped four sprints: send.** Transmit the FINALIZED rocket consultation package to the PATH authors and pose the mine LP-degeneracy question (Task 9 §1–§2; `SPRINT_36/CONSULTATION_BUNDLE.md`). Tick the bundle's action checkbox. This is ~30 min and it starts the only clock the sprint does not control.

**GO/NO-GO gate — all four must hold:** (a) baseline re-confirmed [Task 2]; (b) `make leak-check` present and working on `main` [Task 3]; (c) the markov and fawley Phase-0 docs exist and satisfy the canonical structure [Tasks 4, 6, 10 — `ISSUE_1110`, `ISSUE_1111`, both remediated in prep]; (d) all 27 unknowns resolved, **zero INCOMPLETE** [Task 10]. Docs/trace-only. **No PR** (or a docs-only trace-notes PR).

## 5. Day 1 — P1 markov: discriminator control, `/tmp` only (~6 h)

Branch `planning/sprint37-day1-markov-control`. **PR24/PR27 control before any `src/`.** Implement the Task-4 conjoined predicate as a scratch patch: **(1)** the domain-collision signature (alias-canon match across ≥2 variable positions, a later position an exact declared-name match, an earlier one canon-only) ∧ **(2)** a value-branch `ParamRef` coupling an equation index and the variable's collision-position index at **two distinct positions** of its own tuple. Re-run the corpus scan and confirm it still fires on exactly `['markov']` (Task 4 measured 14 models reaching the domain gate, 13 excluded by the derivative conjunct — including S36's `cesam`/`sroute` leaks, and `iobalance` excluded by the distinct-position refinement). Then drive `kkt_residual.py markov` → **`CASE_A`** and emit the cold MCP: assert `modelstat` = 1 and `pvcost = 2401.577` + match.

**REPLAN exit:** the predicate fires on any model besides markov, or the cold solve does not reach `MODEL STATUS 1` → do not proceed to `src/`; fall back to the narrower per-signature allowlist in `ISSUE_1110` *REPLAN exit*, and if that also leaks, re-bank with the new evidence. `/tmp`-only. Docs/control-notes PR.

## 6. Day 2 — P1 markov: `src/` land + **full-corpus leak gate** + cold-solve gate (~11 h) ← heaviest day

Branch `planning/sprint37-day2-markov-land`. Land the discriminator in `src/kkt/stationarity.py` — detect at the `offset_groups` construction (`:6136–6158`, before the `#1038` consolidation at `:6171`), suppress the spurious groups in that same dict, emit the collapsed off-diagonal at `:7214+`. **`_compute_index_offset_key` (`:4969`) is NOT touched** — that shared matcher is the cohort-leak surface and leaving it alone is Mechanism C's premise.

**The gate that defines this day:** `make leak-check MODEL=markov` must print the **unqualified `LEAK GATE PASS`**. A `PARTIAL` verdict fails (the sweep was narrowed); any `LEAK:` or `NO-OP:` line fails. **Never** clear drift with `make regen-goldens` — that launders a leak into the goldens, which is precisely the S36 failure mode Task 3 instrumented against. Then the cold-solve gate (`modelstat` asserted) and `--resolve-changed --since-commit 78ceaead`.

**This is where the +1 floor lands or REPLANs.** Quality gate (Python touched). Emit-touching PR.

## 7. Day 3 — P1 markov: fixtures + floor verify / REPLAN absorption (~5 h)

Branch `planning/sprint37-day3-markov-fixture`. Land `tests/unit/kkt/test_shape_markov_diagonal_kronecker.py` — **corpus-free, no skip guard** (Task 10 §1.1: `ci.yml` provisions only 5 raw models and markov is not among them, so a skip-guarded fixture would be inert in CI). Assert the structural split — `nu_constr(s,i)` moves from *inside* `sum((s__kktN,j), …)` to a bare additive term — and **do not** assert the `s__kktN` group count (scale-dependent). Flip and sharpen `test_markov_stationarity_has_correction_term` to the `σ=sp` target, and give it the `determinism` marker so `nightly.yml`'s `slow and determinism` selector actually reaches it (it currently runs in **no** CI lane). Recompute the PR25 partition: floor 75 → 76, presolve-match 30 → 29, cold-optimal 63 → 64, **Match unchanged at 93**. Light by design — this day absorbs a Day-2 REPLAN. Quality gate. PR.

## 8. Day 4 — P2 ganges: `rPower` ordering fix + cascade re-apply (~9 h)

Branch `planning/sprint37-day4-ganges-rpower`. Re-apply the verified cascade (`$141`/`$145` from git `a8ff626c`; `$149` `_diff_prod` §5) and take **`rPower` first** — Task 5 re-diagnosed it as a **bounded ordering bug**, not the deep class: the emitter hoists `.l`-dependent bound statements into a "Deferred Variable Bounds" block emitted *before* the `$include` that assigns those `.l`s (source order `ls.l` :593 → `ls.fx$(not ls.l)` :1071; emitted order guard :484 → `$include` :515 — inverted), so the guard fires for every sector and fixes `ls` to 0. **Two independent `/tmp` controls** (move the block / delete it) each took the full run from `rc=3` to `rc=0` with `rPower` gone. The emitter already has both halves of the pattern (#1378's `$include`-supplied skip, #1449's Layer-4 post-`$include` correction pass). Emits are 259–293 s ⇒ use the **async golden-regen slot**, not the PR gate. `/tmp` control before `src/`. Docs/control PR.

## 9. Day 5 — Checkpoint 1 + P2 `$66` (~9 h)

Branch `planning/sprint37-day5-checkpoint1`. **Checkpoint 1 (~4 h):** `--resolve-changed --since-commit 78ceaead` bucket-diff + `make check-goldens` + the presolve-divergence detector + the PR25 recompute. **NO-GO if any *unchanged* golden moved backward** (`match→mismatch`, `model_optimal→model_infeasible`). Record markov's floor verdict and P2's `rPower` disposition. **Freed-budget reallocation:** a markov REPLAN releases ~10 h — it goes to P5 sarf (§17), not to re-attempting markov.

**P2 `$66` (~5 h):** the 16 symbols (`deltax, aid, aex, adst, as, deltas, av, deltav, aq, deltaq, az, deltaz, an, deltan, pnm00, cg`) are **computable cold** — every `.l` feeding them is data-initialised (`ganges.gms:557–745`) and the only `solve` is at `:1150`, *after* the calibration block. Emit the real assignments. **The bank's `param(domain)=0` default is wrong and must not be used** — `as`/`deltas`/`av`/`deltav` are CES/LES share and scale parameters, so zeroing them compiles a *different model* that could not legitimately match (Task 5 §2.2).

## 10. Day 6 — P2 ganges: `ac(i+2,r)` + atomic land-or-bank verdict (~8 h)

Branch `planning/sprint37-day6-ganges-verdict`. The second cold blocker: **`ac(i+2,r)` is still present in `stat_pc(i)` with `$149` applied** — a spurious index offset on a data Table (`ganges.gms:211`), the same `_compute_index_offset_key` family as markov's `σ=sp`. It **compiles**, so the `$NNN` protocol is blind to it, but it corrupts `stat_pc` ⇒ a **match-correctness** blocker beyond `$66`.

Per-model verify **both** ganges and gangesx independently: emit → compile → count residual `$NNN` (assert 0) → solve cold AND presolve (`modelstat` asserted) → bucket → match. **Compile-clean-but-not-solving is NOT a recovery** — report `path_syntax_error → model_infeasible` as such.

**Recovery is atomic.** A partial landing churns 259–293 s goldens for 0 bucket. **REPLAN exit:** `ac(i+2,r)` unresolved, or the embedded MS-5 divergence persists (the genuine deep blocker Task 5 relocated *behind* `rPower`: with `rPower` removed the embedded `ganges0` solves **MS-5 @ −386785.5017** while the raw source standalone solves **MS-2 @ 6395.5444** — the real #1378/#1424 class) → **bank**, ganges/gangesx stay `path_syntax_error`, Solve 108. **+2 Solve/Match if both land, else 0.** Emit-touching PR IF it lands; else docs/bank.

## 11. Day 7 — P4 fawley: narrow conjunct 2 → leak gate (~9 h)

Branch `planning/sprint37-day7-fawley-narrow`. **Do not start by landing.** The correctness half is already control-verified (`sameas` 1 → 3; `stat_bq` out of the residual rows), and the emission path is located — the **"truly disjoint by NAME"** branch (`:7069–7096`) falling to the `Sum(mult_domain, …)` fallback at `:7096` with `dual_binding=None`, because the name-based overlap test misses `cfq ⊂ cf`. The open work is **narrowing conjunct 2**: its `mult_idx ∉ _collect_free_indices(coefficient)` test is name-based and misses the AD layer's `__`-suffixed re-symbolisation, which is the likely reason it under-fires on `dinam`/`shale`. Compare on the **suffix-stripped canonical** name, and/or require the subset's parent to be the *specific* var-domain index the coefficient references (`ISSUE_1111` *REPLAN exit*). Then `make leak-check MODEL=fawley` to an **unqualified PASS**. `/tmp` control. Docs/control PR.

## 12. Day 8 — P4 fawley: land-or-defer + fixture (~7 h)

Branch `planning/sprint37-day8-fawley-land`. If Day 7 reached an unqualified `LEAK GATE PASS`: land it, add the corpus-free `tests/unit/kkt/test_shape_fawley_2d_second_index.py` (matching `cfq\w*`, **not** the literal `cfq__` — Task 10 §1.2), and assert **KPIs unchanged** (108/93/75) since this is 0-bucket by construction. Claiming a bucket gain here would be wrong.

**REPLAN exit:** still leaking → **re-defer**. fawley is 0-bucket, so it must never ship at the cost of a shared-function regression, and `prolog` (a live match) is in the blast radius. A deferred fawley is the correct outcome, not a failure — and it must be recorded as a **carryforward, not a landing** (Task 10 §5.2 fill rule). Emit-touching PR IF it lands; else docs/defer.

## 13. Day 9 — P7 infra + the P6 v54 re-baseline (async) (~9 h)

Branch `planning/sprint37-day9-p7-infra`. **P7:** (a) wire the **Phase-0-doc CI check** drafted in Task 10 §2.3 — trigger `src/{ad,kkt,emit}/**/*.py` (narrower than the leak gate's, which also arms on `src/ir/**`), PR-level doc resolution (a changed conforming doc **or** a PR-body `ISSUE_<N>` reference), prefix matching at both heading and subsection level, `skip-phase0` label escape hatch, CI job **not** pre-commit. The reference implementation is in the catalog and passes **21/21** on the remediated corpus. (b) Reword CONTRIBUTING §392 from "exactly these 4" to "these 4 … extras permitted", so the doc and the gate agree. (c) Recompute the genuine-floor tracking and draft the SUMMARY row-37 fill.

**P6 async (~30 min):** snapshot the DB (record md5 — this is the one operation that legitimately persists), re-solve the 142 candidates under GAMS 54 demo, diff into `GAMS54_REBASELINE_DIFF.md`. Quality gate (Python/CI touched). PR.

## 14. Day 10 — Checkpoint 2 + the v54 decision + P3 camcge (~9 h)

Branch `planning/sprint37-day10-checkpoint2`. **Checkpoint 2 (~4 h):** `--resolve-changed --since-commit 78ceaead` + `make check-goldens` + the PR25 tally.

**The v54 decision (~2 h)** using Task 8 §3's **three-way** rule — *Regression* (a v54-attributable bucket downgrade → **blocks** the re-pin), *neutral churn* (recorded), and **stale-entry correction** (the v53 row predates a landed fix — **turkey is exactly this**, and must be called out separately or it will be miscounted as a v54 effect). **Re-pin only on zero Regressions.** While re-baselining, populate `solver_version` (currently `null` for all 219 rows), so the next version transition is a DB query rather than a 30-minute re-solve.

**P3 camcge (~3 h):** run the `/tmp` Walras control (641 rows, demo-reachable; emit ~18 s; embedded NLP MS-2 @ omega 191.7346; MCP MS-4). **Expected MS-4** — price-pin, single-dual-pin and drop-row have all been refuted across 3+ sprints, so this confirms the Epic-5 per-model-numéraire fallback rather than attempting the refuted transformation. **The drop-row half is BANNED** (primal-correct but breaks the MCP dual → omega 299). **Sprint-37 budget-fork decision recorded here** (§17). PR.

## 15. Days 11–12 — P5 sarf: symbolic-emit re-architecture (~20 h)

Branches `planning/sprint37-day11-sarf-rearch`, `planning/sprint37-day12-sarf-verdict`. The 369,024-column `task(g,t,mn,mn)` blow-up (`|g|`=16, `|t|`=24, `|mn|`=31; active = 398, both runtime-computed, so "statically enumerate the 398" is not available). The O(active) guarded emit is **validated at sarf's real scale** — compiled under GAMS 54.2.1 at `ncart` = 369,024, `rc=0`, instantiation restricted to the guard domain then the live set (Task 7 §3). Short-circuit the three materialisation sites (`constraint_jacobian.py:78`, `index_mapping.py:634`, and `stationarity.py`'s per-column `stat_task`) while leaving all **six** `enumerate_variable_instances` call sites provably unperturbed.

**Atomic:** the 2-D constraint gate + the S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx` land in **one** change; a partial yields an inconsistent MCP (multipliers with no stationarity coupling). **Gate: `make check-goldens` — zero drift across all 163 — plus sarf newly producing a golden (163 → 164)**, NOT `leak-check` (§3). Also assert no set-name-literal indices (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("'` empty — the reverted S26 `nu_slack("srn")` anti-pattern).

**REPLAN exits (any one → bank, sixth deferral, no `src/`):** the parametric emit re-triggers the timeout; a fourth materialisation site surfaces; any unrelated golden drifts; determinism breaks. **+1 Translate is the lowest-leverage KPI and never displaces a bucket track.** Day 12 also stages the Day-13 retest and drafts `SPRINT_38_CARRYFORWARDS.md`. Emit-touching PR IF it lands; else docs/bank.

## 16. Day 13 — Final Retest + Closeout (~8 h)

Branch `planning/sprint37-day13-close`. Determinism ×3 `{0,1,42}` (a stable-model md5); `--resolve-changed --since-commit 78ceaead` GO; DB byte-check; `make check-goldens` clean; the PR25 floor recompute (75 or 76). Write `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`, and fill Epic-4 `SUMMARY.md` **row 37** using the pre-registered rules (Task 10 §5.2) rather than narrative:

- **floor 76 only** if markov cold-matched with `modelstat` asserted; else 75 with the methodology partition still at 30;
- a track is a **firm landing** only if it passed all three gates (Phase-0 doc → fixture → leak gate). **A correctness fix that never passed its leak gate is a carryforward, not a landing** — fawley is the live candidate for exactly this mislabelling;
- carryforwards carry the *bounded next step*, not the track name — the banked-diagnosis pipeline is the epic's most reliably valuable output and its value is entirely in the specificity;
- state the DB byte-status explicitly: it is what makes "flat" a measurement rather than an absence.

Also record the two owner-assigned items if still open: making `golden-staleness` (and `phase-0-gate`) **required** status checks, and any consultation reply. Docs/DB PR.

## 17. Budget Summary — and the two priorities prep measured *down*

| Days | Priority / work | Nominal h |
|---|---|---|
| 0 | Kickoff + baseline re-confirm + GO/NO-GO + **the P3 sends** | ≤ 6 |
| 1–3 | **P1 markov** discriminator (control → land + leak gate → fixture) — the +1-floor lever | ~22 |
| 4–6 | **P2 ganges/gangesx** (`rPower` → `$66` → `ac(i+2,r)` → atomic verdict) + Checkpoint 1 | ~26 |
| 7–8 | **P4 fawley** (narrow conjunct 2 → gate → land-or-defer) | ~16 |
| 9 | **P7** Phase-0 CI wiring + fixtures + floor tracking · **P6** v54 re-baseline (async) | ~9 |
| 10 | Checkpoint 2 + the v54 decision + **P3** camcge Epic-5 control | ~9 |
| 11–12 | **P5 sarf** atomic re-architecture + carryforward staging | ~20 |
| 13 | Final retest + closeout | ~8 |

**Nominal ~116 h against the 168 h cap; heaviest day 11 h (Day 2 — the P1 land + full-corpus leak verify + cold-solve gate).**

**Two of PROJECT_PLAN's per-priority budgets are stale, because prep measured them down:**

| priority | PROJECT_PLAN budget | measured need | why |
|---|---|---|---|
| **P3** consultation | 12–16 h | **~3.5 h** | the reply cannot have arrived — nothing was sent (Task 9). The work is a 30-min send + a ~3 h camcge control. The 12–16 h assumed a reply to integrate. |
| **P6** turkey + v54 | 10–14 h | **~2.5 h** | turkey is NO-GO (license-gated, unprocurable); the re-baseline measured at ~12 s/model ⇒ ~30 min for 142, plus the decision (Task 8). |

That frees **~20 h** — which is exactly what makes P5 sarf reachable at Days 11–12 at the **bottom** of its 20–28 h band. **This is the sprint's one real scheduling choice, and it is contingent:** sarf gets 20 h only if P1/P2/P4 consume no more than their allocation. **Decision point: Day 10.** If the sprint is running over by ≥ 10 h at Checkpoint 2, sarf is formally deferred a sixth time on Day 11 and Days 11–12 become carryforward + slack. Recording that fork now is what prevents sarf from silently eating the closeout — the failure mode a 20–28 h track scheduled last invites.

## 18. Phase-0 Coverage (PR24 + PR27)

Emit-touching tracks: **P1 markov**, **P2 ganges**, **P4 fawley**, **P5 sarf**, **P7** (CI wiring only — `scripts/`/`.github/`, exception-scope). **P3 ships no `src/`.** Each emit-touching gate runs a `/tmp` control BEFORE `src/` (markov Day 1; ganges `rPower` Day 4; fawley Day 7; sarf Day 11), cites `kkt_residual.py` (PR27), and passes determinism ×3 (PR12) + `--resolve-changed --since-commit 78ceaead`.

**Phase-0 docs already exist and conform** for P1 (`ISSUE_1110`) and P4 (`ISSUE_1111`) — both restructured in prep to carry the four canonical `###` subsections and the mandatory `Traced Fix-Surface (Day-0)` line. **P2 ganges and P5 sarf have no Phase-0 doc yet** and must author one **before** their `src/` commit (Days 4 and 11 respectively) — and once Day 9 wires the check, that requirement is enforced rather than remembered.

**The composed emit-PR gate:** Phase-0 doc (before) → property fixture (fail-before/pass-after) → leak gate (after). Per-track: markov/fawley `make leak-check MODEL=<id>`; **sarf `make check-goldens`** (inverted); ganges `make leak-check MODEL=ganges,gangesx` — the `$149` `_diff_prod` fix is a *general* AD change with the widest blast radius of any S37 landing, so its leak gate is the whole safety argument.

## 19. Known Unknowns Status + GO/NO-GO

| Status | Count | Notes |
|---|---|---|
| ✅ VERIFIED | 20 | all Critical resolved |
| 🔶 DESIGN-VERIFIED | 4 | 1.3 (markov leak — the definitive gate is Day 2), 3.3 (camcge MS-1 — Day 10), 4.2 (fawley partial — Day 7), 6.2 (v54 diff — Day 9/10) |
| ❌ WRONG (refuted) | 3 | 3.1 rocket never sent → **Day 0**; 6.1 no licensed testbed → turkey NO-GO; 7.3 skip-if-absent fixtures inert → corpus-free (Days 3, 8) |
| 🔍 INCOMPLETE | **0** | — |

**Every 🔶 maps to the sprint day that closes it**, and no unknown is unmapped. The three refutations are absorbed: one becomes a Day-0 action, one removes a track from the projection, one changed a fixture design in prep.

**⇒ GO for Day 0.** All four gate conditions hold: baseline re-confirmed and byte-identical to the anchor; the leak harness is on `main` and has already caught a real leak in prep; both P1/P4 Phase-0 docs exist and conform; zero unresolved unknowns.

## 20. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| The markov discriminator leaks full-corpus (Med — the one floor lever) | Task 4 refuted two designs by corpus scan *before* any `src/` change; the final predicate fires on exactly `['markov']` across 142. Day 1 re-scans, Day 2 gates on `leak-check`. REPLAN → the narrower per-signature allowlist, then re-bank. |
| **`make regen-goldens` launders a leak** (the S36 failure mode) | `--expect-drift` refuses to `--fix` unexpected models and fails on no-op/unverified. The rule is explicit on Days 2, 7, 11: never clear drift with a regen. |
| fawley's gate stays red and it ships anyway (Med-High — `prolog`, a live match, is in the blast radius) | Day 8 is explicitly *land-or-defer*; 0-bucket means a defer costs nothing. The Day-13 fill rule classifies a never-gated fix as a **carryforward, not a landing**. |
| P2's deep blocker (embedded MS-5 vs standalone MS-2 @ 6395.5444) is unmovable | `rPower` is surfaced Day 4 and `ac(i+2,r)` Day 6, so the deep terminal surfaces by Checkpoint 1 rather than Day 12. REPLAN → bank; +2 or 0 was always the honest range. |
| sarf consumes the closeout (High — 20–28 h scheduled last) | The Day-10 budget fork (§17) makes the sixth deferral an explicit decision with a trigger, not a drift. |
| **Every gate is advisory — a red PR can merge** | `golden-staleness` is still not a *required* status check (`required_status_checks.contexts` = `[]`). **Owner-assigned, not schedulable**; flagged Day 0 and Day 9. This is the single highest-leverage P7 action and it is not a code change. |
| The sprint closes flat (markov REPLANs, P2 banks) | Within the projection. The firm product is the P7 gates + the de-risked banks + the consultation finally sent — zero broken code, the S32–S36 pattern. |

## 21. Related Documents

- **Prep:** `PREP_PLAN.md` · `KNOWN_UNKNOWNS.md` · `BASELINE_RECONFIRMATION.md` (T2) · `LEAK_HARNESS_DESIGN.md` (T3) · `MARKOV_DISCRIMINATOR_DESIGN.md` (T4) · `GANGES_RECOVERY_DESIGN.md` (T5) · `FAWLEY_DISCRIMINATOR_REFRESH.md` (T6) · `SARF_REARCH_REFRESH.md` (T7) · `GAMS54_REBASELINE_PLAN.md` (T8) · `CONSULTATION_INTEGRATION_PREP.md` (T9) · `P7_INFRA_CATALOG.md` (T10) · this `PLAN.md` (T11)
- **Phase-0 docs:** `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md` · `docs/issues/ISSUE_1111_fawley-constraint-index-diagonal.md`
- **Execution:** `prompts/PLAN_PROMPTS.md` (Day 0 + Days 1–13)
- **Banked S36:** `../SPRINT_36/SPRINT_37_CARRYFORWARDS.md` · `DAY2_MARKOV_OFFDIAG_CONTROL.md` · `DAY8_P4_GANGES_BANK.md` · `CONSULTATION_BUNDLE.md`

---

**Status:** Sprint 37 is **GO for Day 0** — all 11 prep tasks complete, all 27 unknowns resolved. The schedule front-loads P1 markov (Days 1–3) with its full-corpus leak gate on Day 2, sequences P4 fawley strictly after it (shared `if/elif` chain), enters P4 with a knowingly-failing gate whose narrowing is Day 7's job, and makes P5 sarf's sixth-deferral decision an explicit Day-10 fork rather than a drift. The honest projection binds: **genuine floor 75 or 76 (markov-contingent); Solve 108 or 110 (P2-bimodal); Match 93 or 95; Translate 135 or 136 (sarf); `path_syntax_error` 7 → 6 as a stale-entry correction; turkey +1 license-deferred; rocket +1 contingent on a send that happens Day 0.**
**Last Updated:** 2026-08-11 · **Owner:** Sprint 37 Execution Team
