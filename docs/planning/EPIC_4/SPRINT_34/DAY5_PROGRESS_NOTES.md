# Sprint 34 — Day 5 Progress Notes (P3 fawley constraint-index-diagonal + Checkpoint 1)

**Date:** 2026-07-20
**Branch:** `planning/sprint34-day5-fawley-secondindex`
**Track:** P3 — fawley #1111/#1112 second-index correction + forcing
**Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P3 — the constraint-index-diagonal `sameas` correction (473→18.468), no mbal/1-D-core regression; +Solve = P5 forcing hand-off (H-b).
**Disposition:** ⏸️ **DEFER (risk/reward, re-affirming the S33 Day-5 call) — the correction is fully characterized but not shipped. No `src/`. Checkpoint 1 GO. Zero in-sprint bucket (H-b), so nothing lost.**

---

## 1. The gap re-confirmed (live emit)

The committed `stat_bq` (`data/gamslib/mcp/fawley_mcp.gms:238`) confirms the design's characterization exactly:

```gams
stat_bq(c,cf).. ( sum(cfq__, (((-1)*1$(bposs(cfq__,c)))*nu_mbal(c))$(sameas(cfq__, cf)))          # mbal — HAS sameas ✓
  + sum((cfq__,l,s), ((prop(c,s)*sum(m$(ms(m,s)),char(c,m))*1$(bposs(cf,c))*nu_qsb(cfq__,l,s))$(cfq(cfq__)))$(specs(cfq__,l,s)))   # qsb — NO sameas ✗
  + sum((cfq__,m),   ((((-1)*(char(c,m)*1$(bposs(cf,c))))*nu_pbal(cfq__,m))$(cfq(cfq__)))$(cfm(cfq__,m)))                          # pbal — NO sameas ✗
  - piL_bq(c,cf) )$(cfq(cf)) =E= 0;
```

`bq(c,cf)` is a **2-D** variable. `mbal(c)` sums `bq` over its **second** index `cfq` → the diagonal logic restricts it `$(sameas(cfq__,cf))`. `qsb(cfq,l,s)`/`pbal(cfq,m)` sum `bq` over its **first** index `c`, and the constraint's **own** index `cfq` = `bq`'s second index = the stat index `cf` — a **constraint-index diagonal**. Since `∂qsb(cfq,·)/∂bq(c,cf)` is nonzero only when `cfq=cf`, the qsb/pbal terms must carry `$(sameas(cfq__,cf))` too. They **over-sum** all `cfq__` — the bug. `max|stat_bq|` 473 (Day-0 fingerprint re-confirmed CASE_B `stat_bq(res-arab-l,fuel-oil)` 0.973 raw 473).

## 2. H-b re-confirmed — zero in-sprint bucket

Per Task 5 / S33 Day-4 (control-proven, `modelstat` asserted): sameas (qsb/pbal) gives `max|stat_bq|` **473 → 18.468**; the residual-18.468 is the **P4 cc-dist bound-transfer cell** (shipped Day 4), not a second over-sum; sameas + all bound-transfer signs → warm `max|stat_bq| ~0` but the MCP **still solves MS-5 @ 4399.557** (LP opt 2899.25). **H-b: the +Solve divergence is non-emit** (LP-convergence at fawley's scale). So:

- fawley's **+Solve** is a **P5 `--force` forcing hand-off** (not in-sprint).
- Under H-b fawley **does not cold-match**, so the +1 genuine floor is **contingent on forcing** (P5), **not** an in-sprint P3 gain.
- The correction moves **no bucket** in-sprint (fawley stays `model_infeasible` with or without it).

## 3. Fix-surface examination — why DEFER (not ship)

The fix (add `$(sameas(cfq__,cf))` to the qsb/pbal cross-terms) lands in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`, **~1430 lines**) — the single most-patched, most-fragile function in the KKT emit, with a dozen interacting issue-specific `sameas` paths (#764/#767/#1049/#1110/#1111/#1112/#1131/#1224/#1306/#1351). The qsb/pbal cross-terms for the 2-D `bq` flow through the **#1104/#1111 offset-group / fresh-alias machinery** (`_get_or_create_fresh_alias` @ `:6953`; the `sameas_conds`/subset-rename logic), **shared** with the mbal term and every other 2-D indexed-cross-term user (cesam2 `stat_w3`, camcge, the ps2 family).

The constraint-index diagonal is a **genuinely new pattern**, not covered by any existing guard:
- **#1049** (`:7174`) fires only when `len(var_domain) > len(mult_domain)` (the variable has *more* dims than the constraint — fixed literal indices). qsb is the **opposite**: the 3-D `qsb(cfq,l,s)` has *more* dims than the 2-D `bq`, so #1049 does not fire.
- **#1110/#1111** handle the *variable*-index diagonal (mbal's summed variable index), not the *constraint*-index diagonal.

A correct addition must detect "the constraint's own index occupies the variable's non-summed (stat) index position" and add the guard **only** there — a new pattern-detection in the middle of the fragile shared machinery. Getting the detection precise enough to fire for qsb/pbal **without** misfiring on the rest of the 2-D indexed-cross-term cohort (a **correctness regression on currently-passing models**) is a dedicated multi-hour effort requiring a full 2-D-cohort regression harness.

**Risk/reward:** high blast radius (a fragile general emit function shared across the 2-D cohort) for **zero in-sprint bucket** (H-b). Shipping a rushed change here risks regressing cesam2/camcge/ps2 — a real correctness harm — to "fix" a model that stays broken either way. This is exactly the calculus **S33 Day 5 faced and deliberately deferred** (`SPRINT_33` memory: "high blast radius for ZERO in-sprint bucket — deliberate risk/reward defer, not a correctness REPLAN"). The Sprint-34 design's PROCEED was prep-time optimism; the execution re-affirms the defer, now with the constraint-index-diagonal **fully characterized** and the fix surface **directly examined** — a de-risked hand-off for a dedicated effort.

This is the design's own **gate-leak-risk REPLAN exit** (`FAWLEY_CORRECTION_FORCING_DESIGN.md` §6) firing on the execution reality (the shared-machinery blast radius), before any `src/`.

## 4. Checkpoint 1 + disposition

- **Checkpoint 1 — `--resolve-changed --since-commit 750803b2` = GO** (the cumulative sprint state, incl. the Day-4 P4 goldens, holds; every changed golden retains its bucket). No `src/`/golden change on Day 5 → the baseline is unmoved.
- **KPI:** Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 — **unchanged**.
- **Split outcome (final):** the **cc-dist bound-transfer cell shipped Day 4** (P4, general MAXIMIZE warm-start correctness); the **constraint-index-diagonal `sameas` correction is deferred** (a dedicated effort + 2-D-cohort regression harness); fawley's **+Solve → P5 `--force` survey** (H-b); the +1 genuine floor is **contingent on forcing**. No P7 fawley 2-D fixture this sprint (it lands only once the correction lands).
- **All front-loaded gates have now fired:** P1 cold-MS-1 (Day 1, H3′ REPLAN) · P4 +Solve survey (Day 4, no +Solve, fix shipped) · P3 correctness (Day 5, DEFER); P2's timeout risk cleared at the Day-0 probe. **Freed ~6–12 h → P6/P7.**

---

**Verdict:** ⏸️ **P3 DEFER (risk/reward, re-affirming S33).** The constraint-index-diagonal `sameas` gap is fully characterized + the fix surface directly examined; a leak-free implementation is a dedicated effort (shared #1104/#1111 machinery, high blast radius) for **zero in-sprint bucket** (H-b). No `src/` shipped; Checkpoint 1 GO; baseline unmoved. fawley's +Solve → P5 forcing; the cc-dist cell shipped Day 4 (P4).
