# Sprint 33 — Day 4: P3 fawley `sameas` control → **H-b (forcing hand-off)**

**Date:** 2026-07-17 · **Day:** 4 · **Branch:** `planning/sprint33-day4-fawley-secondindex`
**Status:** WIP — the pre-`src/` control (`FAWLEY_SECOND_INDEX_DESIGN.md` §5) is complete with a **decisive H-b verdict**: the sameas cross-term correction is genuine but does **not** reach MS-1 — fawley's +Solve is a **non-emit LP divergence** that hands off to forcing (P5/Sprint 34). **No `src/` change today** (the control determined the disposition; the genuine sameas correction + the newly-found bound-transfer issue are Day-5/Sprint-34 decisions). `modelstat` asserted throughout.

---

## 1. The control (repo-root presolve substrate)

The fawley `--nlp-presolve` emit **compiles clean and runs** on the current tree (the design's banked domain-redef errors are gone): embedded NLP **MS-1 Optimal**, warm-started MCP **MS-5** @ 6862. On this substrate I evaluated `stat_bq` at the warm point for the current emit vs the sameas-patched qsb/pbal, then patched the actual equation and re-solved.

## 2. Layer 1 — the sameas over-sum is REAL (genuine emit fix, 96%)

Reproduced the banked measurement **exactly**: `max|stat_bq|` **473.412** (baseline) → **18.468** with `$(sameas(cfq__, cf))` added to the qsb/pbal cross-terms. The over-sum is confirmed: `∂qsb(cfq,·)/∂bq(c,cf)` and `∂pbal(cfq,·)/∂bq(c,cf)` are nonzero only when `cfq = cf`, so the emit must carry the same diagonal `sameas` the mbal term has. **This is a genuine cross-term correction.**

## 3. Layer 2 — the residual 18.468 is an untransferred bound multiplier (NOT a second over-sum)

The full sameas generalization (every `cfq`) leaves **18.468 at a single cell** `stat_bq(cc-dist, fuel-oil)` (everything else → ~1e-13). Per-term at that cell: mbal **318.871** + qsb **55.403** + pbal **−355.806** − piL **0** = **18.468**. And decisively:

- `bq(cc-dist, fuel-oil)`: level **0** (at its lower bound), reduced cost `bq.m` = **−18.468**, `bq.lo` 0, `bq.up` +INF.
- The residual **= −bq.m** — i.e. `piL_bq` *should* be 18.468 but the warm-start left it **0**.

**Root:** fawley is a **maximize** (`solve exxon maximizing profit`), but the emitted bound transfer is min-convention: `piL_bq.l(...)$(… and bq.m(c,cf) > 0) = bq.m(c,cf)` — it skips `bq.m < 0`. With a sign-robust transfer (`= abs(bq.m)`), the cc-dist warm residual → **0**. **This is a distinct bound-transfer-sign issue, not the sameas cross-term.**

## 4. The decisive test — H-a vs H-b

Patched the actual `stat_bq` equation with sameas **and** made **all 12** `piL_*/piU_*` transfers sign-robust (warm residual → ~0), then re-solved:

| Emit state | warm <code>max&#124;stat_bq&#124;</code> | MCP MODEL STATUS | obj |
|---|---|---|---|
| baseline | 473 | MS-5 | 6862 |
| + sameas (qsb/pbal) | 18.468 | **MS-5** | 4399.557 |
| + sameas + all bound-transfer signs | ~0 | **MS-5** | 4399.557 |

**H-b confirmed.** Closing the entire emit residual (sameas + the bound-transfer signs) does **not** recover fawley — the MCP stays **MS-5 @ 4399.557**, far from the LP optimum **2899.25**, and the objective is *identical* with or without the bound-transfer fix (PATH lands at the same infeasible point regardless of the warm-start multipliers). The divergence is **non-emit** — an LP-convergence/structural issue at fawley's scale (a large degenerate blending LP), separable from the `stat_bq` emit. This is the design's **H-b** branch (Unknown 3.2), now empirically decisive.

## 5. Disposition

- **fawley's +Solve is H-b → hands off to the P5 forcing survey / Sprint 34.** fawley stays `model_infeasible` in-sprint; **no in-sprint +Solve, and no genuine-floor gain** (a floor match needs the solve, which is forcing-dependent). Per `FAWLEY_SECOND_INDEX_DESIGN.md` §5/§6, this is PROCEED-as-forcing / the gate-leak outcome.
- **The sameas cross-term correction is genuine** (closes the 473 over-sum). It *can* ship as a correctness fix (the `_add_indexed_jacobian_terms` diagonal-`sameas` extension, `FAWLEY_SECOND_INDEX_DESIGN.md` §3), but it moves **no bucket** (fawley stays MS-5) and is a general 2-D-indexed-cross-term emit change needing the full no-regression gate (no mbal / 1-D-core regression). **Decision deferred to Day 5** (ship for correctness + a shape fixture, or fold into the Sprint-34 hand-off).
- **NEW cross-cutting finding — the max-convention bound-transfer-sign gap.** The `piL_*/piU_*` warm-start transfers are gated on the min-convention `.m > 0` / `.m < 0`; for a **maximize** they skip the correctly-signed multipliers (fawley `bq.m<0` at a lower bound; **the same class as mine's** untransferred upper-bound multipliers). This is a **general warm-start-transfer issue** (not fawley-specific), a candidate dedicated track for Sprint 34. It affects the *warm residual* (the harness CASE_B verdict) but — for fawley — **not the solve** (H-b), so it is not by itself a +Solve lever here.

## 6. KPI impact (the modal outcome tightens further)

Both in-sprint Solve movers now resolve to no in-sprint gain: **P1 mine REPLAN'd (Day 2, H3)** and **P3 fawley is H-b (Day 4)**. The Task-9 **modal flat-KPI** outcome is realized — Solve holds 107, genuine floor holds 74. **The sprint's product is the de-risking:** two decisive control-confirmed dispositions (mine H1 value-invariant; fawley H-b) + a new cross-cutting bound-transfer-sign finding, with **zero broken code shipped**. Freed budget (P1 ~14–18h + P3's +Solve) → P6 (failure-cohort) + P7 + the Sprint-34 hand-offs.

---
**Document Created:** 2026-07-17 · **Owner:** Sprint 33 execution (Day 4) · WIP — Day-5 decides the sameas correctness ship vs Sprint-34 hand-off.
