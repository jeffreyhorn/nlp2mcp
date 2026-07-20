# Sprint 34 — Day 4 Progress Notes (P4 max-convention bound-transfer-sign)

**Date:** 2026-07-20
**Branch:** `planning/sprint34-day4-bound-transfer`
**Track:** P4 — max-convention bound-transfer-sign (NEW, the fresh lever)
**Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P4 — sign-robust `= abs(var.m)` at the active bound, Option B sense-aware, `--resolve-changed` GO; +Solve survey.
**Disposition:** ✅ **PROCEED — the general warm-start-correctness fix ships (Option B). No +Solve (documented-finding, the a-priori outcome): agreste is structural, not warm-residual-driven.**

---

## 1. Pre-`src/` control — the agreste +Solve survey (the one open candidate)

Per the design's attribution table (§3.1), four of the five MAXIMIZE `model_infeasible` candidates are otherwise-attributed (fawley H-b, mine P1/`x.m=0`, camcge Epic-5, rocket Case-c); the sole open +Solve candidate is **agreste** (P6-entangled). The pre-`src/` `/tmp` control patched agreste's committed presolve golden with the sign-robust transfer (all piL/piU → `abs(var.m)`, sign gate dropped) and solved from the repo root:

| agreste MCP (presolve, MAXIMIZE) | modelstat | yfarm |
|---|---|---|
| **baseline** (min-convention transfer) | **MS-5 Locally Infeasible** | 16277.4895 |
| **sign-robust** (`abs(var.m)`) | **MS-5 Locally Infeasible** | 16277.4895 — **identical** |

**Finding: no +Solve.** The sign-robust transfer leaves agreste at the identical MS-5 — its divergence is **structural**, not warm-residual-driven (consistent with the P6 double-`solve` scenario-driver caveat, `agreste.gms:294`/`:298`; the two NLP presolve solves both reach MS-1, but the MCP does not). Non-regressing (same bucket). This is the a-priori-likely documented-finding outcome (§5): **the MAXIMIZE `model_infeasible` cohort yields no +Solve** — P4's firm value is the general warm-start-correctness fix.

## 2. The fix — Option B sense-aware sign-robust transfer (`src/emit/emit_gams.py`)

A bound multiplier is `|reduced cost|`. The min-convention gates skip the correctly-signed multiplier for MAXIMIZE (at an active lower bound a MAX reduced cost is `≤ 0`, so `and var.m > 0` fails → `piL` left at 0). The fix, **Option B (sense-aware)**:

- `_emit_nlp_presolve`: compute `is_max = kkt.model_ir.objective.sense == ObjSense.MAX` (precedent `src/ad/gradient.py:300`; `ObjSense` added to the `src/ir/symbols` import).
- **MINIMIZE** — keep the existing gates (`piL … and var.m > 0 = var.m`; `piU … and var.m < 0 = -var.m`): **byte-identical**, zero churn.
- **MAXIMIZE** — drop the sign gate, keep the active-bound **position** gate, transfer `= abs(var.m)` (both `piL`/`piU`).

The **sole** fix surface is the two bound-multiplier transfer emits (`src/emit/emit_gams.py`, `piL`/`piU` in `_emit_nlp_presolve`); the inequality-multiplier transfer already uses `abs()` and is untouched.

**Verification of the Option-B property (re-emit):**
- MINIMIZE (chain) presolve golden — **byte-identical** ✓ (no MINIMIZE churn).
- MAXIMIZE (fawley) — the transfer now reads e.g. `piL_bq(...)$(abs(bq.l - bq.lo) < 1e-6) = abs(bq.m);` ✓ (sign gate dropped, supplies the previously-skipped `|bq.m|` at the cc-dist cell).

## 3. Golden churn + no-regression

**Changed goldens (11, all MAXIMIZE presolve, Option B):** agreste, camshape, cclinpts, fawley, korcge, otpop, polygon, ps2_f_s, ps2_s, ps3_s_gic, rocket (each a byte-shrink — the sign-gate text removed, `= var.m`/`-var.m` → `abs(var.m)`). The MINIMIZE-translated presolve cohort (bearing, cesam, chain) is **byte-unchanged** (Option B). *Note:* otpop is multi-solve (`otpop2 minimizing`, `otpop1/otpop3 maximizing`) — its **translated** objective is MAXIMIZE, so `objective.sense == MAX` correctly applies `abs()`.

**No-regression gate — `--resolve-changed --since-commit 750803b2` = GO:** all 11 changed-golden models held their bucket. The presolve-**match** regression-risk cohort held (camshape/cclinpts/polygon/ps2_f_s/ps2_s/ps3_s_gic → `model_optimal_presolve` + match; korcge/otpop → `model_optimal` + match); the `model_infeasible` cohort unchanged (agreste/fawley/rocket → `model_infeasible`). The sign-robust transfer alters the warm-start of these MAXIMIZE models **without regressing any bucket**.

**Determinism:** `make regen-goldens` (`check_golden_staleness.py --fix`) re-emits **and** determinism-checks each refreshed golden ×3 `PYTHONHASHSEED` before writing — all 11 byte-stable. Quality gate: typecheck ✓ / format ✓ / lint ✓ / `make test` 5035 passed (1 wall-clock perf-threshold flake under concurrent GAMS load — `test_performance_overhead_acceptable` passes clean in isolation, unrelated to this change).

## 4. Disposition + KPI

- **PROCEED** — the sign-robust transfer ships as a **general warm-start-correctness fix** (Option B sense-aware). It supplies the previously-skipped `|var.m|` at active bounds for the MAXIMIZE cohort (closing the harness CASE_B warm residual, e.g. fawley cc-dist), improving the presolve-recovery substrate corpus-wide.
- **No +Solve** — the MAXIMIZE `model_infeasible` cohort is otherwise-attributed; agreste (the sole open candidate) is structural (control-confirmed §1). This is the design's documented-finding exit (§5/§6), **not** a correctness REPLAN.
- **0 genuine floor directly** (a warm-start-correctness fix; any floor gain would route through a +Solve, which did not materialize).
- **KPI:** Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 — **unmoved** (the fix is a correctness improvement, not a bucket move).
- **P7 (Day 12):** the optional MAXIMIZE bound-transfer regression fixture guards this fix.

---

**Verdict:** ✅ **P4 PROCEED — Option B sense-aware sign-robust bound-transfer ships (general warm-start correctness). No +Solve (agreste structural, control-confirmed). KPI unmoved; the fix improves the MAXIMIZE presolve-recovery substrate.**
