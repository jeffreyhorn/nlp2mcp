# Sprint 37 Per-Day Execution Prompts

**Covers:** Sprint 37 Day 0 + Days 1–13 (P1 markov front-loaded Days 1–3 with its leak gate Day 2; P2 ganges Days 4–6; P4 fawley Days 7–8; P7/P6 Day 9; Checkpoints Day 5 / Day 10; P5 sarf Days 11–12; final retest Day 13). Schedule: `../PLAN.md`.

## How to Use

Paste one day's prompt per session. Each references the prep docs in `docs/planning/EPIC_4/SPRINT_37/` (this file is in `prompts/`, so sibling docs are `../<DOC>.md`). Per-day workflow: branch `planning/sprint37-dayN-<slug>` from `main` → work → quality gate ONLY if `*.py` changed → commit → push → PR → wait for review → on merge, "checkout main and pull".

## Cross-Cutting Rules (every day)

- **Anchor:** the DB / `--resolve-changed --since-commit` / banked-fingerprint anchor is **`78ceaead`** (DB byte-unchanged since it; `stationarity.py` + `derivative_rules.py` byte-identical; the only `src/` delta is `emit_gams.py` +37 and `original_symbols.py` +52, both outside the S37 tracks). The S37 Day-0 *code* state = S36 close `935d94b7`.
- **The leak gate is the sprint's defining discipline.** Emit-touching PRs run `make leak-check MODEL=<id>` and must reach the **unqualified `LEAK GATE PASS`** — a `PARTIAL` verdict fails (the sweep was narrowed), as does any `LEAK:` or `NO-OP:` line. **Never clear drift with `make regen-goldens`** — it refreshes every drifted golden and launders the leak into the corpus (the S36 failure mode). **sarf is the exception**: it has no golden, so its gate is `make check-goldens` (zero drift across 163) + sarf newly producing one.
- **Phase-0 doc BEFORE the `src/` commit** for `src/{ad,kkt,emit}` changes (CONTRIBUTING §392–447). P1/P4 already have conforming docs (`ISSUE_1110`, `ISSUE_1111`); **P2 and P5 must author theirs** on Days 4 and 11. Four canonical `###` subsections, and the `PROCEED/REPLAN Signal` must carry a `Traced Fix-Surface (Day-0)` `file:line`.
- **`/tmp` control BEFORE `src/`** on every emit-touching gate (PR24/PR27); cite `kkt_residual.py`.
- **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the Case-c objective-gradient sign flip BANNED (refuted ×4); the camcge drop-row transformation BANNED (breaks the MCP dual).**
- **No co-authored-by / no Claude-Code attribution** in commits/PRs; reply to each PR review comment thread individually.

## Day 0 Prompt — Kickoff + baseline re-confirm + GO/NO-GO + the P3 sends (≤ 6 h)

Confirm Day-0 = S36 close (Solve 108 / Match 93 [63 cold + 30 presolve] / genuine floor 75 / Translate 135 / Parse 142 / mi 7 / pse 7 / all-219 96 — `../BASELINE_RECONFIRMATION.md`). Verify `git diff 78ceaead..HEAD -- src/` = only `emit_gams.py` +37 and `original_symbols.py` +52, i.e. `stationarity.py` + `derivative_rules.py` byte-identical, so every banked fingerprint reproduces. Re-confirm the Task-2 fingerprints: **markov** `CASE_B` rel 13.3 + dual CONSISTENT + ∈ the methodology partition; **ganges** cascade surfaces + `a8ff626c` reachable; **fawley** `CASE_B`, `stat_bq` rel 0.973; **sarf** non-terminating at cap. Restate the PR25 tally (floor 75; the markov +1 is a **partition transfer**, Match stays 93).

**Then send.** Transmit the FINALIZED rocket consultation package to the PATH authors and pose the mine LP-degeneracy question (`../CONSULTATION_INTEGRATION_PREP.md` §1–§2; `../../SPRINT_36/CONSULTATION_BUNDLE.md`), and tick the bundle's action checkbox. It has been submission-ready since 2026-07-15 across four sprint boundaries; it costs ~30 min and starts the only clock the sprint does not control.

**GO/NO-GO — all four must hold:** baseline re-confirmed; `make leak-check` working on `main`; `ISSUE_1110` + `ISSUE_1111` present and conforming; all 27 unknowns resolved with zero INCOMPLETE (`../KNOWN_UNKNOWNS.md`, `../PLAN.md` §19). Docs/trace-only. **No PR** (or a docs-only trace-notes PR).

## Day 1 Prompt — P1 markov: discriminator control, `/tmp` only (~6 h)

Branch `planning/sprint37-day1-markov-control`. **PR24/PR27 control before any `src/`.** Implement the Task-4 conjoined predicate as a scratch patch (`../MARKOV_DISCRIMINATOR_DESIGN.md` §3): **(1)** the domain-collision signature — a constraint/multiplier domain index whose alias-canon matches ≥2 variable positions, a later position an exact declared-name match and an earlier one canon-only; ∧ **(2)** a `ParamRef` reachable through **value** positions only (never a `$`-condition or a `Sum`/`Prod` condition) carrying an equation-index value **and** the variable's collision-position value at **two distinct positions** of its own index tuple. The distinct-position clause is what excludes `iobalance`'s single-index value coincidence — do not drop it.

Re-run the corpus scan and confirm it still fires on exactly `['markov']` (Task 4: 14 models reach the domain gate, 13 excluded by the derivative conjunct, including S36's `cesam`/`sroute` leaks). Then `kkt_residual.py markov` → **`CASE_A`** (rel ≈ 2.8e-16, from `CASE_B` 13.3), and emit the cold MCP: assert `modelstat` = 1, `pvcost = 2401.577`, match.

**REPLAN exit:** the predicate fires on any model besides markov, or the cold solve misses `MODEL STATUS 1` → do not proceed to `src/`; fall back to the narrower per-signature allowlist (`ISSUE_1110` *REPLAN exit*), and if that also leaks, re-bank. `/tmp`-only. Docs/control-notes PR. Then wait for reviewer comments.

## Day 2 Prompt — P1 markov: `src/` land + full-corpus leak gate + cold-solve gate (~11 h)

Branch `planning/sprint37-day2-markov-land`. Land the discriminator in `src/kkt/stationarity.py` per `ISSUE_1110`'s traced surface: **detect** at the `offset_groups` construction (`:6136–6158`, before the `#1038` consolidation at `:6171`), **suppress** the spurious groups in that same dict, **emit** the collapsed off-diagonal at `:7214+`. **Do NOT touch `_compute_index_offset_key` (`:4969`)** — that shared matcher is the cohort-leak surface and leaving it alone is Mechanism C's premise.

Target emit: `stat_z(s,i,sp).. c(s,sp,i) + nu_constr(s,i) + sum(j, ((-1)*(b*pi(s,i,sp,j,sp))) * nu_constr(sp,j)) - piL_z(s,i,sp) =E= 0;` — **zero** `s__kkt*` groups (baseline: 45).

**The gate that defines this day:** `make leak-check MODEL=markov` → **unqualified `LEAK GATE PASS`**. `cesam`, `ferts`, `sroute` (the S36 leaks) and the 2-D cohort must be byte-identical. Never regen to clear drift. Then the cold-solve gate (`modelstat` asserted, `pvcost = 2401.577`, match) and `--resolve-changed --since-commit 78ceaead`. **This is where the +1 floor lands or REPLANs.** Quality gate (Python touched). Emit-touching PR. Then wait for reviewer comments.

## Day 3 Prompt — P1 markov: fixtures + floor verify / REPLAN absorption (~5 h)

Branch `planning/sprint37-day3-markov-fixture`. Land `tests/unit/kkt/test_shape_markov_diagonal_kronecker.py` — **corpus-free, `pytest.mark.unit`, no skip guard** (`../P7_INFRA_CATALOG.md` §1.1: `ci.yml` provisions only `chenery, abel, partssupply, ps2_f, himmel11`, so a skip-guarded fixture is inert in CI). Build the inline synthetic through `parse_model_text` → `normalize_model` → gradient/Jacobian → `assemble_kkt_system` → `build_stationarity_equations` (~0.6 s measured). Assert the **structural** split — `nu_constr(s,i)` moves from inside `sum((s__kktN,j), …)` to a bare additive term — and **do not** assert the `s__kktN` count (15 synthetic vs 45 real).

Flip and sharpen `tests/integration/kkt/test_markov_multi_pattern.py::…::test_markov_stationarity_has_correction_term` to the `σ=sp` target, and **add the `determinism` marker** so `nightly.yml`'s `slow and determinism` selector reaches it — today it runs in no CI lane at all.

Recompute the PR25 partition: floor 75 → 76, presolve-match 30 → 29, cold-optimal 63 → 64, **Match unchanged at 93** (a partition transfer, not a Match gain). This day is light by design and absorbs a Day-2 REPLAN. Quality gate. PR. Then wait for reviewer comments.

## Day 4 Prompt — P2 ganges: `rPower` ordering fix + cascade re-apply (~9 h)

Branch `planning/sprint37-day4-ganges-rpower`. **Author the P2 Phase-0 doc first** (`docs/issues/ISSUE_<N>_*.md`, 4 canonical subsections + a traced `file:line`) — P2 has none yet.

Re-apply the verified cascade (`$141`/`$145` from git `a8ff626c`, helper `_expr_contains_varref_attribute`; `$149` `_diff_prod` §5 at `:3410`), then take **`rPower` first** — Task 5 re-diagnosed it as a **bounded ordering bug**, not the deep class (`../GANGES_RECOVERY_DESIGN.md` §2.3): the emitter hoists `.l`-dependent bound statements into a "Deferred Variable Bounds" block emitted *before* the `$include` that assigns those `.l`s (source `ls.l` :593 → `ls.fx$(not ls.l)` :1071; emitted guard :484 → `$include` :515 — inverted), so the guard fires for every sector and fixes `ls` to 0. Two independent `/tmp` controls (move the block / delete it) each took the run from `rc=3` to `rc=0`. Reuse the existing halves: #1378's `$include`-supplied skip and #1449's Layer-4 post-`$include` correction pass.

Emits are 259–293 s ⇒ **async golden-regen slot**, not the PR gate. `/tmp` control before `src/`. Docs/control PR. Then wait for reviewer comments.

## Day 5 Prompt — Checkpoint 1 + P2 `$66` (~9 h)

Branch `planning/sprint37-day5-checkpoint1`. **Checkpoint 1 (~4 h):** `--resolve-changed --since-commit 78ceaead` bucket-diff + `make check-goldens` + the presolve-divergence detector + the PR25 recompute. **NO-GO if any *unchanged* golden moved backward** (`match→mismatch`, `model_optimal→model_infeasible`). Record markov's floor verdict and P2's `rPower` disposition. **Freed-budget reallocation:** a markov REPLAN releases ~10 h → it goes to P5 sarf, **not** to re-attempting markov.

**P2 `$66` (~5 h):** emit the real assignments for the 16 symbols (`deltax, aid, aex, adst, as, deltas, av, deltav, aq, deltaq, az, deltaz, an, deltan, pnm00, cg`) — all **computable cold** (every feeding `.l` is data-initialised at `ganges.gms:557–745`; the only `solve` is at `:1150`, after the calibration block). **The bank's `param(domain)=0` default is WRONG and must not be used** — `as`/`deltas`/`av`/`deltav` are CES/LES share and scale parameters, so zeroing them compiles a different model that could not legitimately match. Docs/control or emit PR. Then wait for reviewer comments.

## Day 6 Prompt — P2 ganges: `ac(i+2,r)` + atomic land-or-bank verdict (~8 h)

Branch `planning/sprint37-day6-ganges-verdict`. The second cold blocker: **`ac(i+2,r)` still present in `stat_pc(i)` with `$149` applied** — a spurious index offset on a data Table (`ganges.gms:211`), the same `_compute_index_offset_key` family as markov's `σ=sp`. It **compiles**, so the `$NNN` protocol is blind to it, but it corrupts `stat_pc` ⇒ a **match-correctness** blocker beyond `$66`.

Per-model verify **both** ganges and gangesx independently: emit → compile → count residual `$NNN` (assert 0) → solve cold AND presolve (`modelstat` asserted) → bucket → match. **Compile-clean-but-not-solving is NOT a recovery** — report `path_syntax_error → model_infeasible` as such.

**Recovery is atomic** — a partial churns 259–293 s goldens for 0 bucket. **REPLAN exit:** `ac(i+2,r)` unresolved, or the embedded MS-5 divergence persists (with `rPower` removed the embedded `ganges0` solves **MS-5 @ −386785.5017** vs the raw standalone **MS-2 @ 6395.5444** — the genuine #1378/#1424 class Task 5 relocated behind `rPower`) → **bank**; ganges/gangesx stay `path_syntax_error`, Solve 108. If it lands: `make leak-check MODEL=ganges,gangesx` (the `$149` `_diff_prod` fix is a *general* AD change — the widest blast radius of any S37 landing). **+2 Solve/Match if both land, else 0.** Quality gate if Python touched. Emit-touching PR IF it lands; else docs/bank. Then wait for reviewer comments.

## Day 7 Prompt — P4 fawley: narrow conjunct 2 → leak gate (~9 h)

Branch `planning/sprint37-day7-fawley-narrow`. **Do not start by landing — the gate is currently red.** Correctness is already control-verified (`sameas` 1 → 3; `stat_bq` out of the residual rows) and the path is located: the **"truly disjoint by NAME"** branch (`:7069–7096`) falling to `Sum(mult_domain, …)` at `:7096` with `dual_binding=None`, because the name-based overlap test misses `cfq ⊂ cf` (`../FAWLEY_DISCRIMINATOR_REFRESH.md` §1).

The open work is **narrowing conjunct 2**: its `mult_idx ∉ _collect_free_indices(coefficient)` test is name-based and misses the AD layer's `__`-suffixed re-symbolisation, the likely reason it under-fires on `dinam`/`shale`. Compare on the **suffix-stripped canonical** name, and/or require the subset's parent to be the *specific* var-domain index the coefficient references (`ISSUE_1111` *REPLAN exit* — note conjunct 1 alone and conjunct 1 + the S36 `_collect_free_indices` test have **both already been tried and both leaked**; do not re-run them).

Then `make leak-check MODEL=fawley` to an **unqualified PASS** — recall `prolog` is a live `model_optimal` + match model that conjunct 1 alone drifted. `/tmp` control. Docs/control PR. Then wait for reviewer comments.

## Day 8 Prompt — P4 fawley: land-or-defer + fixture (~7 h)

> **✅ COMPLETED ON DAY 6** (pulled forward with P2's freed budget; landed in PR #1671,
> `main` `eb89d0df`). The leak gate returned an unqualified `LEAK GATE PASS` — 163 goldens,
> 0 unverified, fawley only — so the *land* branch was taken, not the defer branch. The
> corpus-free fixture shipped with it (3 tests, 0 executable `pytest.skip()` calls).
> **Do not re-execute this day.**
>
> ⚠ **The KPI figure below was stale even when written:** it says `108/93/75`, but the
> genuine floor moved to **76** on Day 3 when markov landed. The correct assertion is
> **Solve 108 / Match 93 / floor 76 unchanged**.

Branch `planning/sprint37-day8-fawley-land`. If Day 7 reached an unqualified `LEAK GATE PASS`: land it, add the corpus-free `tests/unit/kkt/test_shape_fawley_2d_second_index.py` (`pytest.mark.unit`, no skip guard, matching **`cfq\w*`** not the literal `cfq__` — `../P7_INFRA_CATALOG.md` §1.2), and assert **KPIs unchanged — 108 / 93 / floor ~~75~~ 76**: fawley is H-b and 0-bucket by construction, so claiming a bucket gain here would be wrong.

**REPLAN exit:** still leaking → **re-defer**, and record it as a **carryforward, not a landing**. fawley is 0-bucket, so it must never ship at the cost of a shared-function regression. A deferred fawley is the correct outcome, not a failure. Quality gate if Python touched. Emit-touching PR IF it lands; else docs/defer. Then wait for reviewer comments.

## Day 9 Prompt — P7 infra + the P6 v54 re-baseline (async) (~9 h)

> **Scope changed during execution.** **P7(b) is already done** — CONTRIBUTING §392 was
> reworded to rule C in PR #1670 (Day 5 review), and all 23 Phase-0 docs verify clean
> against it. **P7(c)'s floor tracking is resolved** — the floor is **76**, not contingent.
> **Three items were discovered during execution and belong to this day:**
> 1. **Leak-gate load-dependence** — the sweep's verdict varies with machine load at its
>    default 6 workers (measured 4 / 2 / 0 timeouts across three runs on Day 2), because
>    `ganges`/`clearlak` sit near the hardcoded 600 s emit budget
>    (`scripts/gamslib/batch_translate.py:265`). Every Sprint-37 gate run needed
>    `MAX_WORKERS = 3`. Fix: lower the default, raise the cap, or route the full sweep
>    to a nightly lane. This is now load-bearing — `golden-staleness` is a *required* check.
> 2. **Golden coverage is asymmetric** — **153 cold goldens vs 17 presolve** (Day 4). A
>    presolve-only emit change is far less protected than the "163 in-scope goldens"
>    headline implies; ganges/gangesx carry **no** presolve golden at all.
> 3. **The Phase-0 CI check (P7(a)) would now enforce rule C**, which CONTRIBUTING already
>    states — so the check and the doc agree before it lands, rather than after.

Branch `planning/sprint37-day9-p7-infra`. **P7(a):** wire the **Phase-0-doc CI check** from `../P7_INFRA_CATALOG.md` §2.3 — trigger `src/{ad,kkt,emit}/**/*.py` (deliberately narrower than the leak gate's, which also arms on `src/ir/**`); PR-level doc resolution (a changed conforming `docs/issues/ISSUE_*.md` **or** a PR-body `ISSUE_<N>`/`#<N>` reference); **prefix matching at both the heading and subsection level**; the 4 canonical names required with extras allowed; `skip-phase0` label escape hatch; **CI job, not pre-commit**. The reference implementation is in §2.3 and passes 21/21 on the remediated corpus. **P7(b):** reword CONTRIBUTING §392 from "exactly these 4" to "these 4 … extras permitted" so the doc and the gate agree. **P7(c):** recompute the genuine-floor tracking + draft the SUMMARY row-37 fill (§5.2's pre-registered rules).

**P6 async (~30 min):** snapshot the DB (record md5 — the re-baseline is the one operation that legitimately persists), re-solve the 142 candidates under GAMS 54 demo, diff into `GAMS54_REBASELINE_DIFF.md`. Quality gate (Python/CI touched). PR. Then wait for reviewer comments.

## Day 10 Prompt — Checkpoint 2 + the v54 decision + P3 camcge (~9 h)

Branch `planning/sprint37-day10-checkpoint2`. **Checkpoint 2 (~4 h):** `--resolve-changed --since-commit 78ceaead` + `make check-goldens` + the PR25 tally.

**The v54 decision (~2 h)** using the **three-way** rule (`../GAMS54_REBASELINE_PLAN.md` §3): *Regression* (a v54-attributable bucket downgrade → **blocks** the re-pin), *neutral churn* (recorded), and **stale-entry correction** (the v53 row predates a landed fix — **turkey is exactly this**, `path_syntax_error → path_solve_license`, `pse` 7 → 6 with **no Solve/Match change**; call it out separately or it will be miscounted as a v54 effect). **Re-pin only on zero Regressions.** While re-baselining, populate `solver_version` (currently `null` for all 219 rows).

**P3 camcge (~3 h):** the `/tmp` Walras control (641 rows, demo-reachable; emit ~18 s; embedded NLP MS-2 @ omega 191.7346; MCP MS-4 — `../CONSULTATION_INTEGRATION_PREP.md` §3). **Expected MS-4** → confirms the Epic-5 per-model-numéraire fallback. **The drop-row half is BANNED** (primal-correct but breaks the MCP dual → omega 299). ~~Also record the **Day-10 budget fork** (`../PLAN.md` §17)~~ — **already resolved on Day 7**: sarf was profiled and deferred a sixth time on *measured* grounds (a constant-factor fix was tried and bought only ~5 % throughput against the ~66× needed), so Days 11–12 are already free. Record the fork as **closed**, not open. PR. Then wait for reviewer comments.

## Day 11 Prompt — P5 sarf: symbolic-emit re-architecture, part 1 (~10 h)

> **⚠ The Day-10 fork already resolved to DEFER (Day 7).** sarf was profiled and the cheap
> alternative measured and refuted; the 20–28 h atomic re-architecture was not started.
> **`ISSUE_1385` now exists** (`docs/issues/ISSUE_1385_sarf-symbolic-emit-o-active.md`) with
> the four canonical Phase-0 subsections, the three materialisation sites re-located on
> current `main`, the **inverted gate**, and the constraint that **sarf cannot be its own
> fixture model** (at 369,024 columns the fail-before state does not terminate). Execute
> this day only on an explicit decision to re-open P5.

Branch `planning/sprint37-day11-sarf-rearch`. ~~**Only if the Day-10 fork said GO.** **Author the P5 Phase-0 doc first** — P5 has none yet.~~ **The Phase-0 doc exists** (see the banner); start from its PROCEED/REPLAN signal.

The 369,024-column `task(g,t,mn,mn)` blow-up (`|g|`=16, `|t|`=24, `|mn|`=31; active = 398, both runtime-computed, so static enumeration of the 398 is not available — `../SARF_REARCH_REFRESH.md`). The O(active) guarded emit is **validated at real scale** (GAMS 54.2.1, `ncart` = 369,024, `rc=0`). Short-circuit the three materialisation sites — `constraint_jacobian.py:78` (S1), `index_mapping.py:634` (S2), and `stationarity.py`'s per-column `stat_task` (S3) — while leaving all **six** `enumerate_variable_instances` call sites provably unperturbed (the other three: `gradient.py:287`/`:453`, `complementarity.py:367`/`:512`).

PR27 timing control first: the re-emit must complete in **single-digit seconds** (baseline `>330 s` / non-terminating at cap). *A partial improvement that does not cross the threshold is a REPLAN, not progress.* `/tmp`/control PR. Then wait for reviewer comments.

## Day 12 Prompt — P5 sarf: part 2 + verdict + carryforward staging (~10 h)

Branch `planning/sprint37-day12-sarf-verdict`. If Day 11's control passed, land **atomically**: the 2-D constraint gate + the S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx` in **one** change (a partial yields an inconsistent MCP — multipliers with no stationarity coupling). Verify `stat_task` matches the banked **7-term** derivation term-for-term (tbal ×2, labor, equipb1, equipb2, acost3, `task.lo`) — a silently-wrong `stat_task` is the worst failure mode.

**Gate: `make check-goldens` — ZERO drift across all 163 — plus sarf newly producing a golden (163 → 164).** **NOT `leak-check`**: sarf has no golden, so `--expect-drift sarf` reports `NO-OP` and fails for a non-correctness reason. Also assert no set-name-literal indices (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` empty — the reverted S26 `nu_slack("srn")` anti-pattern) + determinism ×3.

**REPLAN exits (any → bank, sixth deferral, no `src/`):** the parametric emit re-triggers the timeout; a fourth materialisation site surfaces; any unrelated golden drifts; determinism breaks. Then draft `SPRINT_38_CARRYFORWARDS.md` and stage the Day-13 retest. Quality gate if Python touched. Emit-touching PR IF it lands; else docs/bank. Then wait for reviewer comments.

## Day 13 Prompt — Final Retest + Closeout (~8 h)

Branch `planning/sprint37-day13-close`. Determinism ×3 `{0,1,42}` (a stable-model md5); `--resolve-changed --since-commit 78ceaead` GO; DB byte-check; `make check-goldens` clean; the PR25 floor recompute (**76** — no longer contingent; markov cold-matched on Day 2 with `modelstat` asserted, and Day 3 persisted the row). Write `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`; fill `../../SUMMARY.md` **row 37** using the pre-registered rules (`../P7_INFRA_CATALOG.md` §5.2):

- floor **76** — resolved, not contingent: markov cold-matched (`modelstat` asserted, `pvcost` 2401.5774), the DB row was persisted Day 3, and the partition is presolve-match **29** / cold-optimal **64** with Match unchanged at 93;
- a track counts as a **firm landing** only if it passed all three gates (Phase-0 doc → fixture → leak gate). A correctness fix that never passed its leak gate is a **carryforward** — ~~fawley is the live candidate~~ **fawley passed its gate on Day 6 and is a firm landing**; the rule now applies to the *ganges* cascade, which is verified-working but **blocked by #1668** and must be recorded as a carryforward, not a landing;
- carryforwards carry the *bounded next step*, not the track name;
- state the DB byte-status explicitly — it is what makes "flat" a measurement rather than an absence.

Docs/DB PR. Then wait for reviewer comments.

---

**Covers:** Sprint 37 Day 0 + Days 1–13.

**Projection as written (prep Task 11):** genuine floor 75 or 76 (markov-contingent); Solve 108 or 110 (P2-bimodal); Match 93 or 95; Translate 135 or 136 (sarf); `path_syntax_error` 7 → 6 as a stale-entry correction, 5 if P2 lands; turkey +1 license-deferred; rocket +1 contingent on the Day-0 send.

**Actuals through Day 8** — most contingencies are now settled:

| KPI | projected | actual |
|---|---|---|
| genuine floor | 75 **or 76** | **76** — markov landed (Day 2–3) |
| Solve | 108 **or 110** | **108** — P2 REPLAN'd, blocked by #1668 |
| Match | 93 **or 95** | **93** (64 cold + 29 presolve) |
| Translate | 135 **or 136** | **135** — sarf deferred on measured grounds (Day 7) |
| `path_syntax_error` | 7 → 6 or 5 | **7** — the turkey correction needs a persisting v54 re-solve (Day 9/10) |
| rocket +1 | contingent on the send | **still unsent — owner-assigned** |

Landed: **P1 markov** (+1 floor) and **P4 fawley** (0 bucket, leak-free). Deferred with banked Phase-0 gates: **P2 ganges** (#1667, #1289, blocked by #1668) and **P5 sarf** (#1385).
