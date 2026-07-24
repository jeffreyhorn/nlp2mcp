# Sprint 35 — Reusable-Tooling Readiness Audit + Slow-Emit CGE Golden-Regeneration Budget + P7 Fixture Catalog

**Prep Task:** 3 (High) · **Date:** 2026-07-23 · **Owner:** Sprint 35 prep (tooling/infra)
**Day-0 code anchor:** `78ceaead` (S34 close) · no `src/`/`scripts/` drift since (Task 2 `BASELINE_METRICS.md`)
**Scope:** docs/measurement only — audits the reused tooling, **measures** the slow-emit golden-regeneration budget, and catalogs the P7 fixtures. No `src/` change.

---

## Executive summary

Sprint 35's diagnostic tooling is **reused, not rebuilt** — **zero new diagnostic-tool code**; the only new test artifacts are the P7 fixtures (§4), each gated on its own track's landing. All reusable tools are confirmed present, and the Day-0 gate is ready: `run_full_test.py --resolve-changed --since-commit 78ceaead --dry-run` reports **GO** (no emit goldens changed).

**The headline result is that Sprint 34's ship-blocker does not survive measurement.** S34 Day 11 banked a *written and empirically verified* `$141` fix because the ganges/gangesx/clearlak/turkpow goldens were judged "un-regenerable in the CI budget" — `make regen-goldens` soft-timed-out on exactly those four, refreshing **0** goldens, so shipping would have left stale goldens (`SPRINT_34/DAY11_PROGRESS_NOTES.md` §45). Measured directly, that verdict is **an artifact of how the sweep was invoked, not a property of the models**:

| Measurement | Result |
|---|---|
| Per-model emit, run alone | gangesx **151 s** · clearlak **192 s** · ganges **203 s** · turkpow **442 s** (sum 987 s / 16.5 min) |
| Worst case vs the 600 s per-emit timeout | turkpow 442 s — clears it with **~26 % headroom** |
| **Scoped staleness check, all four in parallel** | **489.63 s (8.2 min) — 0 timeouts, all 4 clean** |
| Re-emit vs the committed goldens | **4/4 byte-identical** (no latent drift) |

So the four models are individually well inside budget; what failed in Sprint 34 was the **full 170-golden sweep at `MAX_WORKERS = 6`**, where the slow four contend with 166 others and each 600 s per-emit subprocess timeout is reached. The scoping flag that fixes this — `check_golden_staleness.py --models` — **already exists** (`:124`), so **no new tooling is required to unblock P4**.

**Verdict for P4: the golden regeneration FITS A NORMAL ≤ 12 h DAY. No dedicated overnight slot is needed.** Worst-case end-to-end (all four goldens drift) ≈ **50 minutes** (§3.4). Task 12 should schedule against that, not against an overnight window.

Two further findings this task surfaced: the P7 **`SUMMARY.md` continuation is larger than "fill row 35"** — after the Sprint-35 insertion the file still carries the *pre-insertion* themes at rows 35/36, so it needs a reconcile-and-append across rows 35→38 (§5); and **`indus` is allowlisted** for cross-environment byte non-determinism (#1461), which matters because indus is in the `$149` cohort — its golden cannot serve as a P4/P6 regression signal (§4.4).

---

## §1. Per-track tooling-readiness audit (Unknowns 7.1 tooling layer)

All reusable tools confirmed present on `main` at the Day-0 anchor (the `--resolve-changed` dry-run, the scoped staleness check, and the four emits were all exercised **this task**):

| Tool | Path | Confirmed |
|---|---|---|
| KKT-residual harness (incl. `case_c_objdef`) | `scripts/diagnostics/kkt_residual.py` | ✅ present; `reclassify_objdef_case_c` at `:621`, the `case_c_objdef` verdict at `:466` |
| `--resolve-changed` checkpoint | `scripts/gamslib/run_full_test.py` | ✅ **GO dry-run at `78ceaead`** this task |
| Golden-staleness gate | `scripts/sprint_audit/check_golden_staleness.py` | ✅ present; **`--models` scoping flag at `:124`** — exercised this task |
| Presolve-divergence detector | `scripts/diagnostics/check_presolve_divergence.py` | ✅ present |
| `--force` solution-forcing scaffold | `src/cli.py` (`--force` at `:207`) | ✅ present |
| AD cross-term property catalog | `tests/integration/emit/test_ad_crossterm_shapes.py` (**shapes 1–11 + `shape_p4_max_bound_transfer`**) | ✅ present; the `_emit` helper takes `nlp_presolve` (S34 P4 addition) |
| Raw-emit regression-fixture pattern | `tests/integration/emit/test_sample_pruned_var_l_init.py` | ✅ present (the S33 raw-emit + skip-if-absent pattern) |

| Track | Guarding tool | New tool code for Sprint 35 |
|---|---|---|
| **P1 mine** (head-offset dual architecture) | `kkt_residual.py` — the **cold**-solve verdict (the reframed gate) + the CASE_B `stat_x` fingerprint; `--resolve-changed` golden-diff on `mine_mcp*.gms` | **None** — new coverage = the **P7 shape12 fixture** (§4), only if P1 lands. |
| **P2 sarf** (symbolic `stat_task` emit mode) | the emit-budget timer (the O(active) probe uses the existing translate path) + the golden-staleness gate on a *new* `sarf_mcp.gms` | **None** — sarf has **no golden today** (`translate_failure`), so the first successful emit *creates* it; the staleness gate then covers it. New coverage = the **P7 shape13 fixture**. |
| **P3 fawley** (constraint-index-diagonal `sameas`) | `kkt_residual.py` — the CASE_B `stat_bq` verdict + <code>max&#124;stat_bq&#124;</code>; `--resolve-changed` on `fawley_mcp*.gms` | **None** — new coverage = the **P7 fawley 2-D second-index fixture**. |
| **P4 ganges/gangesx** (multi-root recovery) | the **raw-emit compile check** (emit → GAMS compile → count `$NNN` by code) + the scoped staleness regen (§3) + `--resolve-changed` | **None** — the compile check is the same procedure S34 Day 11 used; new coverage = the **P7 ganges recovery fixture**. |
| **P6 residual cohort / Case-c** | `kkt_residual.py` (`case_c_objdef`) + the same raw-emit compile check | **None** — documentation path; the Case-c family is settled (sign flip **BANNED**). |

**Conclusion: zero new diagnostic-tool code for Sprint 35** — a pure reuse, as in Sprint 34. No blocking tool gap. The one capability P4 needs that Sprint 34 believed it lacked (a way to regenerate the slow CGE goldens in budget) **already exists** as `check_golden_staleness.py --models`; §3 measures it.

---

## §2. The Sprint-34 ship-blocker, restated precisely

The claim under test (`SPRINT_34/DAY11_PROGRESS_NOTES.md` §45, verbatim):

> **The affected goldens are un-regenerable in budget.** The fix only touches params with `.l`-referencing division assignments — the **slow-emit CGE cohort** (ganges/gangesx). `make regen-goldens` **soft-timed-out** on exactly those models (ganges/gangesx/clearlak/turkpow — "slow-emit, run nightly"), refreshing **0** goldens. […] Shipping the `src/` would leave the committed ganges/gangesx goldens **stale** (old emit) with no in-budget way to regenerate them.

The mechanism behind the soft-timeout, read from the code:

- `make regen-goldens` → `check_golden_staleness.py --fix`, which sweeps **every** discovered golden. There are **170** (`153` cold + `17` presolve).
- The sweep runs `ThreadPoolExecutor(max_workers=6)` (`:36`, `:132`), i.e. **six emit subprocesses at once**.
- Each emit is a subprocess with `translate_timeout = 600` seconds (`scripts/gamslib/batch_translate.py:265`).
- On timeout, `check_one` records a **soft** `"timeout"` status — explicitly *"couldn't verify in budget", NOT drift* (`:88–93`) — and the design comment already routes the full sweep to nightly.

So the S34 observation is real, but its *cause* is contention in the full sweep, and the conclusion drawn from it ("no in-budget way to regenerate them") was never tested against the models in isolation. §3 tests it.

---

## §3. Measured golden-regeneration budget (Unknown 4.5 — primary)

All measurements taken on the Day-0 tree (`78b81615`), macOS, 16 cores, `.venv` interpreter. **Measured, not estimated.**

### 3.1 Per-model emit, run alone

`/usr/bin/time -p .venv/bin/python -m src.cli data/gamslib/raw/<model>.gms -o /tmp/<model>.gms`, sequentially, no other emit running:

| Model | real (s) | user (s) | golden size | raw size | vs 600 s timeout |
|---|---:|---:|---:|---:|---|
| gangesx | **151.00** | 146.70 | 79 KB | 72 KB | ✅ 75 % headroom |
| clearlak | **191.84** | 188.05 | 31 KB | 6.5 KB | ✅ 68 % headroom |
| ganges | **202.57** | 195.25 | 80 KB | 59 KB | ✅ 66 % headroom |
| **turkpow** | **442.15** | 316.13 | 163 KB | 11 KB | ✅ **26 % headroom** (the binding case) |
| **sum** | **987.56 (16.5 min)** | | | | |

**Every model clears the 600 s per-emit timeout on its own.** turkpow is the binding case at 442 s; note its `user` (316 s) sits well below `real` (442 s), so even this sequential run was partly contention-bound — the true isolated cost is lower.

Golden size, not raw size, predicts cost (clearlak: 6.5 KB raw → 31 KB golden → 192 s; turkpow: 11 KB raw → 163 KB golden → 442 s). The cost is in **emit/stationarity expansion**, not parsing.

### 3.2 Byte-identity — no latent drift

All four re-emits are **byte-identical** to their committed goldens (`cmp` clean; ganges md5 `72c5d5f268e9dad458f61f58491872c5` on both sides).

This matters for P4 beyond the timing: the goldens are **not stale today**, so when P4's three root fixes land, the resulting golden diff is **wholly attributable to those fixes** — no pre-existing drift is mixed in, and the `--resolve-changed` signal stays clean.

### 3.3 Scoped staleness check — the decisive measurement

```
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py \
    --models ganges,gangesx,clearlak,turkpow

Golden staleness: checked 4 in-scope golden(s) (0 allowlisted, 6 workers).
  All in-scope goldens clean.
real 489.63   user 1356.92   sys 34.07
```

**489.63 s (8.2 min) wall-clock, 0 timeouts, all 4 clean.** With only four models in scope, all four run concurrently under the 6-worker pool (`user`/`real` ≈ 2.8× confirms real parallelism), and the wall-clock is set by the slowest model (turkpow) rather than the sum. Crucially, **turkpow stayed under the 600 s per-emit timeout even under four-way contention** — the risk that parallelism would push it over did not materialise.

This is the direct refutation of the S34 "un-regenerable in budget" conclusion: **the scoped regen the `--models` flag already supports completes in 8.2 minutes.**

### 3.4 Sprint budget for P4's regeneration

Cost model, from the code path:

- A **clean** golden costs **1 emit** (`check_one` regenerates and byte-compares).
- A **drifted** golden under `--fix` costs **2 emits** — the determinism guard re-emits a second time and requires byte-identity before overwriting (`:105–112`), so a non-deterministic emit can never silently churn a golden.
- The four models have **cold goldens only** (no `_presolve` variants), so P4 refreshes **4 goldens, not 8**.

| Step | Cost | Basis |
|---|---|---|
| Scoped `--fix` regen, all 4 drifting | ~**16.4 min** | 2 × the 8.2 min scoped wall-clock (the determinism guard doubles it) |
| Determinism ×3 `{0,1,42}` (PR12), if run as a separate pass over the four | ~**24.6 min** | 3 × 8.2 min — *optional*: the `--fix` guard already proves per-run determinism |
| Follow-on `--resolve-changed --since-commit 78ceaead` re-solve of the 4 changed goldens | ≤ **8 min** | 4 GAMS solves at the 120 s solve timeout (`run_full_test.py:543`) |
| **Worst-case total** | **≈ 50 min** | all four drift + a separate ×3 pass + full re-solve |

### 3.5 Verdict (the answer Task 12 schedules against)

> **P4's golden regeneration FITS INSIDE A NORMAL ≤ 12 h SPRINT DAY. A dedicated overnight slot is NOT required.**

Worst case ≈ 50 minutes end-to-end; the realistic case (scoped `--fix` + re-solve, relying on the built-in determinism guard) is **≈ 25 minutes**. Recommended invocation for the P4 landing day:

```bash
# after the $141 / $145 / $149 fixes land in src/
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py \
    --models ganges,gangesx,clearlak,turkpow --fix        # ~16 min worst case
.venv/bin/python scripts/gamslib/run_full_test.py \
    --resolve-changed --since-commit 78ceaead             # re-solve the changed goldens
```

**Do NOT run the unscoped `make regen-goldens` on the P4 day** — that is the 170-golden sweep whose contention produced the S34 soft-timeout in the first place. Scope it.

**Consequence for the sprint's shipping rule.** Sprint 34 banked the verified `$141` fix on two grounds: (a) it recovered 0 bucket, and (b) its goldens were un-regenerable. **Ground (b) is now removed.** Ground (a) still stands and is unchanged — the "no bucket → no `src/`" rule still requires P4 to land all three roots and actually move a bucket. What this task establishes is that *if* P4 recovers ganges/gangesx, the goldens are no longer a reason not to ship, and the S34 P4 exception criteria (fast, regenerable goldens + `--resolve-changed` GO) are **satisfiable** for this cohort. Task 11 should weigh P4 with the golden constraint removed.

---

## §4. P7 property-fixture catalog (Unknown 7.1)

Each fixture is **fail-before / pass-after** and lands **only with its own track's fix** — the S33/S34 discipline (S34 correctly *deferred* shape12/shape13/fawley because P1/P2/P3 REPLAN'd; `SPRINT_34/DAY12_P7_INFRA.md` §18).

| Fixture | Gating track | Shape | Pattern | Home |
|---|---|---|---|---|
| **shape12** — head-offset dual | **P1** (mine) | a head-offset constraint whose dual is placed at the shifted label, with a bound-active row | synthetic, in-process (sub-second) | `tests/fixtures/crossterm_shapes/shape12_*.gms` + a case in `test_ad_crossterm_shapes.py` |
| **shape13** — sarf symbolic emit | **P2** (sarf) | a guarded multi-dim variable whose active subset is runtime-computed, asserting the emitted `stat_*` is parametric (one guarded row, not per-instance) | synthetic, in-process | same catalog |
| **fawley 2-D second-index** | **P3** (fawley) | a constraint-index-diagonal `sameas` shape where the constraint dimension ≥ the variable dimension (the #1049-guard's *opposite* orientation) | synthetic, in-process | same catalog |
| **ganges recovery (raw-emit)** | **P4** (ganges) | the emitted MCP must contain no `.l`-referencing NaN-cleanup guard, no `*`-domain cleanup guard, and no free index in `stat_pc` | **raw-emit + skip-if-absent** | `tests/integration/emit/test_ganges_*.py`, following `test_sample_pruned_var_l_init.py` |

**Notes.**

- The first three are **synthetic** fixtures in the existing catalog — the `_emit` helper (`test_ad_crossterm_shapes.py:37`, with the `nlp_presolve` flag S34 added) runs them in-process in under a second, so they carry no regen cost.
- The **ganges fixture must be raw-emit** (the defect only manifests on the real model's CES/LES structure), and `data/gamslib/raw/` is **gitignored / absent in CI** — so it must use the `test_sample_pruned_var_l_init.py` pattern: `@pytest.mark.skipif(not RAW.exists(), reason="raw … not present (gitignored corpus)")`. It should assert on the **emitted text** (a proxy for the GAMS compile error) rather than invoking GAMS, exactly as the sample guard does.
- **If a track REPLANs, its fixture is simply not written.** That is the correct outcome, not a gap — S34's Day-12 deferral of three fixtures is the precedent.

### 4.4 `indus` cannot serve as a P4/P6 regression signal

`indus` is in the golden-staleness **allowlist** (`scripts/sprint_audit/golden_staleness_allowlist.txt`) for **cross-environment byte non-determinism** (#1461): the emit is hash-seed-stable on macOS but the ubuntu CI emit differs by ~45 bytes, so the gate would flap.

This matters because **indus is a member of the `$149` cohort** (`$140` + `$149`, per `SPRINT_34/DAY11_PROGRESS_NOTES.md`). When P4's `$149` fix lands, indus's golden **cannot be used as evidence** the fix worked — its allowlist entry suppresses the gate, and a genuine emit change on it would surface only as a drift *warning*. Task 4's cohort catalog and Task 5's per-model protocol should verify indus by **compile-error count**, not by golden diff.

### 4.5 Genuine-floor tracking (anchor 75)

The PR25 recompute **maintains anchor 75** unless a Sprint-35 track lands a genuine **cold-emit** change that cold-matches. Task 2 reproduced the partition from the DB (63 cold + 12 genuine-presolve = 75; methodology 21; all-219 Match 96) and enumerated both member sets, so the P7 recompute is a re-run of that arithmetic against the Day-13 DB, not a fresh derivation. Per the S34 P4 precedent, a **warm-start-only** fix yields **0** floor by definition.

---

## §5. Epic-4 `SUMMARY.md` continuation (Unknown 7.3) — larger than a row fill

The prompt scopes this as "the row-35 continuation", but the file's current state needs **more than filling one row**. `SUMMARY.md` has 19 numbered rows; rows 33–36 read:

| Row | Current theme | Correct post-insertion theme |
|---|---|---|
| 33 | S32 carryforward — mine cross-term, sarf, fawley 2nd-index, camcge, rocket/Case-c | ✅ correct (filled at the S33 close) |
| 34 | S33 carryforward — mine dual, sarf, fawley, camcge, rocket + P4 bound-transfer + P6 ganges | ✅ correct (filled at the S34 close) |
| **35** | **"Quality, performance & PATH-feedback integration (incl. rocket PATH author consultation)" — `(planned)`** | ❌ **stale — this is the *pre-insertion* theme.** Post-insertion, Sprint 35 = **the S34 carryforward sprint** (mine dual / sarf symbolic / fawley diagonal / **ganges multi-root** / camcge Epic-5 / rocket → S36) |
| **36** | **"v2.0.0 release & Epic 5 planning" — `(planned)`** | ❌ **stale — that is now row 38.** Post-insertion, Sprint 36 = **PATH Author Consultation & Solution Forcing** |
| 37 | *(absent)* | ➕ **add** — Quality, Performance & PATH Feedback Integration |
| 38 | *(absent)* | ➕ **add** — v2.0.0 Release & Epic 5 Planning |

**So the P7 `SUMMARY.md` work is a reconcile-and-append across rows 35→38**, mirroring the reconcile-and-append the S33 and S34 closes each performed (`SPRINT_34/DAY12_P7_INFRA.md` §35 records the same pattern one sprint earlier). Scope for the Day-12/13 close:

1. **Reconcile row 35** to the S34-carryforward theme and fill its cells in the rows-28–34 format (Theme / Headline KPIs at close / Firm landing(s) / REPLAN'd → carryforward).
2. **Reconcile row 36** to the PATH-consultation theme (`(planned)`).
3. **Append rows 37 and 38** for the Quality/Performance and v2.0.0 themes (`(planned)`).

No technical impact — but left undone, the Epic summary contradicts `PROJECT_PLAN.md` for three consecutive sprints.

---

## §6. Day-0 gate

```
run_full_test.py --resolve-changed --since-commit 78ceaead --dry-run
→ GO: no emit goldens changed since 78ceaead
```

Consistent with Task 2's Day-0 record; re-run this task after the four emits (which wrote only to `/tmp`, leaving the tree untouched).

---

## §7. Known Unknowns verified by this task

- **Unknown 4.5 (primary)** — ✅ **VERIFIED, and the S34 premise is REFUTED.** The four slow-emit goldens **are** regenerable in budget: per-model 151 / 192 / 203 / 442 s (all under the 600 s per-emit timeout), and the **scoped** `check_golden_staleness.py --models ganges,gangesx,clearlak,turkpow` completes in **489.63 s (8.2 min) with 0 timeouts and all 4 clean**. The S34 soft-timeout was **full-sweep contention** (170 goldens at `MAX_WORKERS = 6`), not model cost. **Verdict: P4's regen fits a normal ≤ 12 h day (~25 min realistic, ~50 min worst case); no overnight slot required.** The scoping flag needed already exists.
- **Unknown 7.1** — ✅ **VERIFIED.** Zero new diagnostic-tool code; all seven reused tools confirmed present and three of them exercised live. The four P7 fixtures are catalogued with their gating tracks, shapes and homes; the ganges fixture must be raw-emit + skip-if-absent. Additional finding: **indus is allowlisted** (#1461) and therefore cannot serve as a P4/P6 golden-diff regression signal.
- **Unknown 7.3** — ✅ **VERIFIED, with the scope corrected.** The `SUMMARY.md` continuation is **not** a single row fill: rows 35 and 36 still carry pre-insertion themes and rows 37/38 are absent, so the Day-12/13 task is a reconcile-and-append across rows 35→38 (§5).

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 3
**Last Updated:** 2026-07-23
**Owner:** Sprint 35 Planning Team
