# Sprint 37 Day 5 — Checkpoint 1 + P2 `$66` Disposition

**Date:** 2026-08-12 · **Branch:** `planning/sprint37-day5-checkpoint1` · **Scope:** docs/verification-only — no `src/` change, DB untouched.

**Verdict: ✅ GO.** All four checkpoint components pass; **no unchanged golden moved backward**. The genuine floor holds at **76**. Two findings the checkpoint surfaced that were not in the plan: the OBJ-GAP set is **8, not the banked 5** (traced to Sprint 36's own final landing), and `$66` turns out to be **Issue #1289**, open since Sprint 25 with **no Phase-0 section** — so it was never implementable under CONTRIBUTING, cascade or not.

---

## 1. Checkpoint 1 — four components, all pass

| # | component | result |
|---|---|---|
| a | PR25 partition recompute | ✅ **exact on every line** |
| b | `--resolve-changed --since-commit 78ceaead` | ✅ **GO** — all 19 changed-golden models held their bucket |
| c | presolve-divergence detector | ✅ no non-allowlisted hard divergence |
| d | `check-goldens` (full 163) | ✅ **all in-scope goldens clean** |

### (a) PR25 partition

| KPI | measured | target |
|---|---|---|
| Parse / Translate | 142 / 135 | 142 / 135 |
| **Solve** | **108** | 108 |
| **Match** | **93** = 64 cold + 29 presolve | 93 = 64 + 29 |
| model_infeasible / path_syntax_error | 7 / 7 | 7 / 7 |
| all-219 Match | 96 | 96 |

**Genuine floor 76** — the P1 markov advance holds two days after landing.

### (b) `--resolve-changed`

`GO: all 19 changed-golden model(s) held their bucket.` Every unchanged model reports `= same`. The only `~ shift` is **turkey** `path_syntax_error → path_solve_license` — the stale-entry correction Task 8 predicted, not a recovery and not a v54 effect.

**The NO-GO condition (`match→mismatch`, `model_optimal→model_infeasible` on an unchanged golden) is not met.**

### (d) `check-goldens`

`checked 163 in-scope golden(s) (7 allowlisted, 3 workers). All in-scope goldens clean.` Run at **3 workers** per the Day-2 load-dependence finding; **zero timeouts**, so this is a full-coverage clean result rather than a partial one.

## 2. The OBJ-GAP set is 8, not the banked 5

The divergence detector reports **8** informational obj-gaps:

```
agreste  cesam  chain  fawley  rocket        <- the 5 Sprint 36 banked
ps2_f_s  ps2_s  ps3_s_gic                    <- three NOT in the banked set
```

**Traced rather than assumed to be a regression.** The three additions' goldens changed in **`ac391bb6` — "Sprint 36 Day 10: P7 robustlp NA-guard de-allowlist (first src landing)"** — and are **untouched during Sprint 37** (`git log 935d94b7..HEAD` on those paths is empty).

So Sprint 36's own final `src/` landing introduced an obj-gap on three models, and S36 closed reporting the **pre-landing** count. A landing changed the very metric its sprint then reported, and the report was taken from before the change.

**No bucket harm:** all three (plus robustlp) still read `model_optimal_presolve` + **match**, and component (b) re-solved all four to `= same`.

**But a banked instruction is now wrong.** `GAMS54_REBASELINE_PLAN.md` (Task 8) §3 step 4 says *"**Re-check** the 5 OBJ-GAP models explicitly"*. That set is incomplete — the v54 re-baseline must re-check **8**, and the three additions are exactly the 2-D cohort members (`ps2_f_s`, `ps2_s`, `ps3_s_gic`) that the leak gate treats as the canonical shared-function collateral set. Corrected in that document.

## 3. P2 `$66` — it is Issue #1289, and it had no Phase-0 gate

Day 5's P2 half was *"emit the real assignments for the 16 symbols"*. Tracing the surface first (PR24) established two things the prompt did not carry.

**It is an existing issue.** `$66` is **#1289** (`docs/issues/ISSUE_1289_ganges-family-calibration-assignment-stripping.md`), open since **2026-04-20 / Sprint 25**, describing exactly this defect. It predates the Phase-0 rule and **carried no `## Phase 0: Acceptance Gate` section** — so under CONTRIBUTING §392–447 it was **not implementable at all**, independent of the cascade being blocked.

**Traced fix surface:** `src/emit/emit_gams.py:2768` — the `if presolve_include_emitted:` gate wrapping
`emit_computed_parameter_assignments(..., varref_filter="only_varref_attr")`. In the cold path that predicate is False, so the **entire** calibration block is skipped. The partitioning itself lives in `original_symbols.py:1716–1742`, which flags a parameter as "calibration" when any assignment references a `VarRef` attribute and propagates that transitively.

**Confirmed in the committed cold golden:** the `.l` inputs are present (`ls.l` ×14, `pk.l` ×10, `s.l` ×49) while every calibration assignment is absent (`deltas`, `as`, `aid`, `adst` — 0 each). The parameters are computable cold; they are dropped purely because they *syntactically* reference `.l`.

**Phase-0 gate authored** (four canonical subsections + traced `file:line`), carrying the correction that the banked `param(domain) = 0` default is **wrong** — `as`/`deltas`/`av`/`deltav` are CES/LES share and scale parameters, so zeroing them compiles a *different model* that could not legitimately match.

**Implementation not attempted, deliberately.** Verifying a `$66` fix requires the cascade applied (its errors only surface once `$141`/`$145`/`$149` clear), and Day 4 established the cascade leaks via **#1668**. Building on a knowingly-leaking foundation would produce a measurement that cannot be trusted.

## 4. P2 disposition — recommend STOP for Sprint 37

Every remaining ganges blocker is individually blocked or worthless:

| blocker | state |
|---|---|
| `$141`/`$145`/`$149` cascade | verified working, **blocked** by #1668 (drifts `prolog`, a matching model) |
| `rPower` (#1667) | control-verified, **unreachable** without the cascade |
| `$66` (#1289) | Phase-0 gate now authored; **unverifiable** without the cascade |
| `ac(i+2,r)` in `stat_pc(i)` | second cold blocker, untouched |
| embedded MS-5 divergence | **the 6th blocker — 0-bucket regardless** |

Even a fully clean cascade buys `path_syntax_error → model_infeasible`, a **lateral** move. Solve stays 108, Match stays 93.

**Day 5's concrete P2 product** is therefore the two Phase-0 gates and two traced fix surfaces (#1667 Day 4, #1289 today) — which is what a future dedicated ganges effort actually needs, and which did not exist before this sprint.

**Freed budget:** P2's Day-6 allocation. The schedule designates freed budget for **P5 sarf** (Days 11–12), but the nearer bounded work is **P4 fawley**'s conjunct-2 narrowing (Days 7–8). Owner's call.

## 5. Checkpoint verdict

**✅ GO to Day 6.** Floor 76 holds; goldens clean at full coverage; no bucket moved backward; the DB is byte-stable except markov's deliberate Day-3 row.

**Recorded for the retrospective:** two banked figures were wrong this sprint in the same way — Task 8's "5 OBJ-GAP models" (§2) and Task 5's "no non-collateral prod model drifts" (Day 4). Both were accurate when written and stale by the time they were used, because a later landing changed the thing they measured. The pattern is not carelessness; it is that **a measurement taken before a landing keeps being cited after it**.

---

**Document Status:** ✅ Complete — Sprint 37 Day 5 (Checkpoint 1 GO; P2 STOP recommended).
**Last Updated:** 2026-08-12 · **Owner:** Sprint 37 execution team
