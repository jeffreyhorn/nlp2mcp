# Sprint 33 — Day 5: P3 fawley close (H-b) + Checkpoint 1

**Date:** 2026-07-17 · **Day:** 5 · **Branch:** `planning/sprint33-day5-fawley-sameas`
**Disposition: P3 CLOSES as H-b.** The genuine sameas cross-term correction is **de-risked and handed to Sprint 34** (bundled with the fawley forcing + the bound-transfer finding); it is **not shipped in-sprint** — a deliberate risk/reward decision, not a REPLAN on correctness. **Checkpoint 1: GO** (no regression). **No `src/` change.**

---

## 1. Why the sameas correction is deferred, not shipped

Day 4's control established fawley is **H-b**: the sameas fix is genuine but the MCP stays MS-5 (non-emit divergence), so **fawley moves no bucket** in-sprint (stays `model_infeasible`; no Solve, no cold-match → **no genuine floor**). The Day-5 prompt's H-b branch assumed shipping yields "+genuine floor," but that premise **does not hold for fawley** (it doesn't cold-match). So shipping means a **high-blast-radius change for zero in-sprint bucket gain**.

**The fix surface is genuinely invasive.** The mbal `$(sameas(cfq__, cf))` and the qsb/pbal gap are *structurally different*:
- **mbal** sums over `bq`'s **second (variable) index** `cfq`; the emit restricts that **summed variable index** to the stat index via `sameas(cfq__, cf)` — handled by the existing diagonal logic.
- **qsb/pbal** sum over `bq`'s **first (variable) index** `c`; the needed restriction is on the **constraint's own index** `cfq` (= `bq`'s second index = the stat index `cf`) — a **constraint-index diagonal** the current logic does not recognize.

Emitting the constraint-index diagonal requires extending `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py`, ~1400 lines with a dozen issue-specific `sameas` paths: #767/#764/#1049/#1110/#1224/#1306) — every indexed cross-term in the corpus flows through it. The design's hard constraint ("no mbal-term change for fawley or any other 2-D indexed-cross-term user") makes this a careful, well-gated change deserving a focused effort + the full regression suite, **not** a rushed Day-5 change in a flat-KPI sprint for zero payoff.

**Decision (risk/reward):** defer to Sprint 34 as a **de-risked, ready-to-implement** hand-off. The control (`DAY4_FAWLEY_CONTROL.md`) proves the fix (473→18.468 exactly) and pins the exact surface (the constraint-index diagonal gap). This is the honest disposition — the emit correction is real and worth doing, but responsibly, where zero in-sprint bucket gain does not justify the blast radius.

## 2. Checkpoint 1 (Day 5) — GO

- `.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit ee51ed9e --dry-run` (run from the repo root) → **GO: no emit goldens changed since `ee51ed9e`**.
- `git diff ee51ed9e..HEAD -- src/ scripts/ data/gamslib/mcp/` → **empty**. No `src/`, `scripts/`, or golden change across the sprint (all work has been control/docs).
- **No backward moves:** Solve **107**, Match **92**, genuine floor **74**, model_infeasible **7** all hold at the Day-0 baseline. PR25 tally unchanged (genuine 74 / methodology 21 / all-219 95).

## 3. P3 outcome + the Sprint-34 hand-off package

**fawley P3: H-b — +Solve hands off to forcing (P5/Sprint 34).** The Sprint-34 hand-off carries three de-risked, control-confirmed items:
1. **The genuine sameas cross-term correction** — the qsb/pbal `$(sameas(cfq__, cf))` gap; fix surface = the constraint-index diagonal in `_add_indexed_jacobian_terms`; control-proven (473→18.468); needs the no-regression gate + a fawley 2-D second-index shape fixture (the P7 shape).
2. **The fawley forcing lever** — the MS-5 @ 4399.557 divergence is non-emit (LP-convergence/structural at fawley's scale); feed to the `--force` survey / PATH consultation.
3. **The max-convention bound-transfer-sign gap** (NEW, cross-cutting) — the `piL_*/piU_*` warm-start transfers gated on min-convention `.m>0`/`.m<0` skip the correctly-signed multipliers for MAXIMIZE solves; affects fawley **and mine**; a candidate dedicated warm-start-transfer track, worth checking as a +Solve lever on *other* max models whose divergence is warm-residual-driven (unlike fawley's structural H-b).

## 4. KPI status — modal flat-KPI (Task 9 realized)

Both in-sprint Solve movers have fired their gates with **no in-sprint bucket move**: **P1 mine REPLAN'd (Day 2, H3)**, **P3 fawley H-b (Day 5)**. Solve **107** / genuine floor **74** hold. Task 9's **modal flat-KPI** outcome is realized. The sprint's firm product is the **de-risking**: three control-confirmed dispositions (mine H1 value-invariant; fawley sameas genuine-but-H-b; the bound-transfer finding), zero broken code shipped. **Freed budget (P1 ~14–18h + P3's remaining ~6–12h) → P6 (failure-cohort) + P7 + the Sprint-34 hand-offs.**

**Next (recommendation):** pivot to **P6** (the failure-cohort re-triage — agreste scope-verify + the 8-member `path_syntax_error` cohort) — the only remaining track with a plausible in-sprint bucket move; and **P2 sarf** (+Translate). The genuine emit corrections (fawley sameas, the bound-transfer gap) land in Sprint 34.

---
**Document Created:** 2026-07-17 · **Owner:** Sprint 33 execution (Day 5) · P3 CLOSED (H-b); sameas correction → Sprint 34.
