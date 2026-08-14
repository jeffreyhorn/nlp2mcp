# Sprint 37 → Sprint 38 Carryforwards

**Date:** 2026-08-13 · **Branch:** `planning/sprint37-day13-carryforwards` · **Scope:** docs-only.

**Sprint 37 in one line:** the **genuine floor advanced 75 → 76**, the first advance since Sprint 33, on one real emit fix (**markov `σ=sp`**) — with a second correctness fix landed (**fawley**, 0 bucket), four infrastructure gates built that did not exist before, and the two remaining deep tracks (**ganges**, **sarf**) deferred with *measured* refutations rather than judgement calls.

**Close state (measured at `8cffec29`, 2026-08-13):** Solve **108** · Match **94** (65 cold + 29 presolve) · **genuine floor 76** · Translate **135** · mi **7** · pse **6** · all-219 Match **97**. Corpus re-pinned to **GAMS 54.2.1**.

**Anchor:** `78ceaead` (S34 close — still the `--resolve-changed` / DB anchor). **S37 shipped delta:** `src/kkt/stationarity.py` **+311** (markov +259 P1, fawley +54 P4 — the only `src/` file touched all sprint), 2 new corpus-free fixtures, 4 P7 gates.

**The DB changed this sprint** (first since S33): Day 3 (markov's row) and Day 9 (the v54 re-baseline + provenance). Sprint 38 inherits a DB that agrees with the hand-partition for the first time in five sprints.

---

## 1. Carryforwards (sharpest-first)

### 1.1 P2 ganges/gangesx — the `$149` rebind predicate (**0 bucket**; cascade VERIFIED working)

- **State:** all four fixes are **VERIFIED working on both models**, run per-model and never inferred. `$141`/`$145`/`$149` go **78/3/9 → 0/0/0**, `rPower` (`FUNC DOMAIN: x**y, x=0,y<0`) is **gone**, `gams rc` **2 → 0**, EXECERROR cleared. `src/` was reverted; the tree is byte-identical to `main`.
- **Sole blocker:** the full-corpus leak gate refuses it. The **`$149` rebind drifts `prolog`**, a live `model_optimal` + match model. Reverting *only* `$149` (keeping `$141`/`$145` + the `rPower` gate) returns `rc=2` with 9 × `$149` — **so the cascade cannot be split, and there is no leak-free subset.**
- **Bounded next step:** **re-scope the `$149` rebind predicate — not the fix.** #1668 records two concrete directions: rebind parameter indices consistently, or restrict the trigger to a genuinely-free `prod` bound. **Direction 2 is closer to the original intent.**
- **Value — corrected by this sprint's own measurement:** **0 bucket.** The prep-era banked figure was *"+2 or 0"*; Days 4 and 5 refuted it. The **6th blocker** (embedded `ganges0` **MS-5 Locally Infeasible @ −386785.5017** against raw standalone **MS-2 @ 6395.5444**, matching the banked figure to the decimal) is untouched, and `mcp_model` stays **MS-4**. A fully clean cascade therefore buys `path_syntax_error → model_infeasible` — a **lateral** move (pse 6 → 4, mi 7 → 9). **Solve stays 108, Match stays 94.** A genuine +2 additionally requires resolving the embedded-NLP-divergence class (#1378/#1424), which is **not** scoped here.
- **Also blocked, and worth knowing before budgeting:** `$66` is **Issue #1289**, open since **Sprint 25** with **no Phase-0 section** — it was never implementable under CONTRIBUTING §392–447, cascade or not. A Phase-0 gate was authored on Day 5. A second cold blocker, `ac(i+2,r)` in `stat_pc(i)`, remains untouched.
- **Refs:** `DAY4_GANGES_CONTROL.md`, `DAY5_CHECKPOINT1.md` §3–4, `ISSUE_1667`, `ISSUE_1289`, GitHub **#1667** / **#1668**.

### 1.2 P5 sarf — the O(active) atomic re-architecture (+1 Translate; cheap fix measured dead)

- **State:** **DEFER — the sixth consecutive**, but the first on *evidence* rather than risk/reward. Sprint 37 profiled it and refuted the shortcut.
- **What the profile changed:** the banked design blamed "369 K columns". The profile says **the columns are cheap and differentiating each one is not** — `compute_constraint_jacobian` is 137 s of a 180 s cap, with ~762 K top-level `differentiate_expr` calls against the **398** columns that matter.
- **The cheap fix was built, measured, and reverted:** memoizing `resolve_set_members` inside `_is_concrete_instance_of` (5.8 M invocations) worked exactly as intended — `resolve_set_members` left the top-14, `_is_concrete_instance_of` 59.0 → 39.7 s — and bought **~5 % throughput** (761,897 → 802,108 differentiations). sarf needs `>330 s → single-digit seconds` ≈ **66×**. Recorded in `ISSUE_1385` **so it is not re-attempted as a shortcut**.
- **Bounded next step:** the **20–28 h atomic re-architecture** at all three materialization sites (S1 `constraint_jacobian.py:78`, S2 `index_mapping.py:634`, S3 `stationarity.py`), landing as **one unit** (2-D constraint gate + S1/S2/S3 short-circuit + parametric `stat_task` + `task.fx`) — a partial landing is explicitly a REPLAN, because multipliers without stationarity coupling leave the MCP inconsistent.
- **Two gate peculiarities a future effort must not rediscover:** sarf has **no golden**, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason — the real gate is `make check-goldens` (zero drift ×163) **plus** sarf newly producing a golden (163 → 164). And **sarf cannot be its own fixture**, because at 369,024 columns the fail-before state does not terminate.
- **One stale precondition, corrected:** Task 7 recorded all three site files as byte-unchanged since the anchor. `stationarity.py` is now **+311** (markov Day 2, fawley Day 6). The **sites themselves are intact** and all six corpus-safety call sites remain at their recorded line numbers.
- **Refs:** `DAY6_FAWLEY_LANDING.md` §1–4 (Day 7 sections), `ISSUE_1385`, `SARF_REARCH_REFRESH.md`.

### 1.3 P3 rocket / mine — the consultation **send** (needs a human; UNSENT for a 3rd sprint)

- **State:** the bundle is **FINALIZED** (`../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`) and has been for three sprints. It has never been transmitted.
- **Blocker — not technical:** the bundle **names no recipient, address, or channel**. It was never executable by an execution agent, and each sprint has re-carried it on that basis without the gap being closed.
- **Bounded next step:** **a human names a recipient and channel — or the item is struck from the plan.** Carrying it a fourth time without an owner would make it a permanent fixture rather than a task.
- **What it would buy:** rocket **+1 Solve contingent** on a recommended option-set / continuation schedule. The **fawley `--force` +Solve** belongs to the same class — the Sprint-36 survey was **NEGATIVE** (homotopy / multistart / optfile all leave fawley MS-5), so it needs a stronger continuation or reformulation, i.e. the same consultation. mine is **0 bucket** (the only non-invariant lever is an LP-side reformulation, out of emit scope).
- **Refs:** `CONSULTATION_INTEGRATION_PREP.md`, `DAY0_TRACE_NOTES.md` §5.

### 1.4 camcge — Epic 5 (Walras MS-4; per-model numéraire)

- **State:** the Day-10 `/tmp` control under GAMS 54.2.1 **reproduced every predicted figure**: emit 19 s, 641 single equations / 641 variables, embedded NLP **MS-2 @ omega 191.7346**, `mcp_model` **MS-4 Infeasible**. The MCP is MS-4 against a *correct* NLP optimum — structural Walras rank-deficiency, **not an emit defect**.
- **Deliberately not attempted, and should stay that way:** the three-part dual-consistent Walras redefinition. Price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ omega 299. 3+ sprints of variants have all stayed MS-4. **The drop-row half remains BANNED** — primal-correct but it breaks the MCP dual.
- **Disposition:** **Epic 5**, with the per-model-numéraire fallback confirmed. **0 bucket for Sprint 38** unless Epic 5 is scheduled.
- **Refs:** `DAY10_CHECKPOINT2.md` §5, `../../EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### 1.5 turkey — license-gated +1 (needs a licensed testbed)

- **State:** the `$161` compile-recovery landed in Sprint 35; Day 9's re-baseline corrected its stale row to `path_solve_license`, and Day 10 confirmed it stable (`= same`).
- **Blocker:** turkey's MCP is **3,866 rows** against the GAMS **demo 1000-row nonlinear limit**. Local solve-verification is impossible; this is a **testbed/CI** step, not a local one.
- **Bounded next step:** re-solve turkey on a licensed testbed. **+1 Solve / +1 Match if it converges** — otherwise unchanged.

### 1.6 The 36 presolve goldens — the coverage asymmetry (infra; adopt deliberately)

- **State:** the golden corpus is **153 cold vs 17 presolve**. Day 9's full re-solve regenerated **36 presolve goldens** (17 → 53); they were swept into a commit by `git add -A`, caught in review, and **removed**.
- **Why this is a real carryforward, not just an incident:** those 36 are plausibly the **fix** for the asymmetry — the presolve emit path is far less covered than the cold path.
- **Bounded next step:** adopt them as a **deliberate, reviewed** change. Generating references and committing them in the same unreviewed step would expand what `check-goldens` sweeps (170 → 206) using references produced by that very run — **a self-certifying reference set, which is how a gate stops being a gate.**
- **Refs:** `GAMS54_REBASELINE_DIFF.md` §6, `DAY10_CHECKPOINT2.md` §7.

---

## 2. Shipped in Sprint 37 (**NOT** carried)

| track | what shipped | bucket |
|---|---|---|
| **P1 markov `σ=sp` discriminator** | `_try_build_sigma_sp_crossterm` + 3 helpers in `stationarity.py` (+259). Gated additive early-out for the off-diagonal case where the multiplier index is an independent variable index; refuses conditioned constraints; requires pairwise-distinct index elements. Leak gate **PASS ×163** — the gate that killed it in S36. | **+1 floor (75 → 76)** |
| **P4 fawley constraint-index-diagonal** | Subset-parent binding in the "truly disjoint by NAME" branch (+54), requiring the coefficient to **reference the parent**. Landed on attempt 3 by **adding a positive requirement** where two prior narrowings only subtracted. Unqualified `LEAK GATE PASS`, clearing a gate blocked since S35. | **0 by construction** |
| **P7 infra ×4** | golden-staleness now a **required** check + `--min-scope 170` asserted on *discovery*; **Phase-0 CI gate** calibrated against real history; leak gate 6 → 3 workers (ended load-dependent timeouts); `solver_version` broken-regex fix + new per-row `mcp_solve.gams_version` (×135 rows). | infra |
| **P6 GAMS-54 re-baseline** | Corpus **re-pinned to 54.2.1**, zero Regressions; three movers classified three ways. | +1 Match (hhfair, methodology) |

**`_compute_index_offset_key`** — the shared cohort-leak surface — was deliberately left untouched, and should stay that way absent a full-corpus leak plan.

---

## 3. Sprint 38 Day-0 staging

**Baseline to re-confirm** (all measured at `8cffec29`; re-derive rather than trust these):

| quantity | expected |
|---|---|
| Solve / Match / floor | 108 / 94 (65 cold + 29 presolve) / **76** |
| Translate · mi · pse · all-219 | 135 · 7 · 6 · 97 |
| `--resolve-changed --since-commit 78ceaead` | **GO**, 19 changed-golden models |
| `make check-goldens` | 163 in-scope, clean, 0 timeouts |
| determinism ×3 `{0,1,42}` | byte-identical **and** equal to committed goldens |
| solver | GAMS **54.2.1** |

**The floor is now DB-consistent.** For the first time in five sprints the DB agrees with the hand-partition (robert's stale row was corrected on Day 9). This does **not** make the floor derivable from the DB — see §4.

---

## 4. Process carryforwards (from `SPRINT_RETROSPECTIVE.md`)

These are not track work, but they caused real defects this sprint and will cause more if unaddressed.

1. **Derive figures at execution time; do not quote them.** Day 8's prompt sweep corrected 6 stale figures and was **re-staled by Day 9's own re-baseline within 24 hours**. This bit the closeout itself twice: the S36-close partition was first written as 64/29 (the *mid-sprint* state), and **`SPRINT_LOG.md` §7 carried the prep-era "+2 or 0" for ganges that Days 4–5 had already refuted** (corrected in this change). Where a figure must be quoted, **carry the commit it was measured at**.
2. **Assert a gate's SCOPE, not just its verdict.** A check that silently narrows passes while the property is false — a false-negative generator, worse than no check. `--min-scope N` asserted on *discovery* is the template. Two known narrowing modes remain: `--resolve-changed` selects by **git diff** (uncommitted goldens are invisible — always commit *then* checkpoint), and `make leak-check MODEL=<id>` reports `NO-OP` for a model with no golden.
3. **The genuine floor cannot be derived from the DB.** A mechanical `Match − (presolve ∧ match)` count yields **65** against a recorded **76**, because the *"cold emit byte-identical to pre-fix"* qualifier lives only in the hand-partition. Any floor-tracking automation must carry per-model provenance or it will emit 65 and look authoritative.
4. **Emit PRs need the Phase-0 ISSUE doc before the `src/` commit.** Now CI-enforced, but two long-open items (`$66`/#1289 since S25, sarf/#1385) were found this sprint to have **never had one** — so they were not implementable regardless of budget. Check this before budgeting a track, not during it.
5. **Never `git add -A` after a GAMS run in the repo root.** GAMS writes scratch files to `cwd`. The artifacts are now `.gitignore`d, but the safer habit is to run re-baselines from a scratch directory.

---

## 5. Honest close

Sprint 37 moved the floor for the first time in four sprints, and it moved it by **one model**. The other two partition movers were the DB catching up (robert, counted since S30) and a free solver upgrade (hhfair, methodology) — neither is an achievement, and the log says so.

The two deferred tracks are in materially better shape than they were at sprint start: **ganges** has a verified-working cascade and a named blocker with two fix directions, and **sarf** has a profile that relocated the bottleneck plus a measured refutation of the cheap alternative. Neither is a bank of *hope*; both are banks of *evidence*.

The one item that did not improve is **the consultation send**, which is not a technical problem and cannot be solved by another sprint of the same treatment.

---

**Document Status:** ✅ Complete — Sprint 37 → 38 carryforwards.
**Last Updated:** 2026-08-13 · **Owner:** Sprint 37 execution team
