# Sprint 33 — Day 2: P1 mine H1 control → **REPLAN (H3)**

**Date:** 2026-07-17 · **Day:** 2 · **Branch:** `planning/sprint33-day2-mine-h1`
**Disposition: REPLAN (H3) — H1 head-label multiplier re-keying is empirically REFUTED by the pre-`src/` control.** mine stays `model_infeasible`; P1 hands off a dedicated head-offset dual-architecture subsystem to Sprint 34. **No `src/` change** (the control caught H1 before any emit change — the 8th consecutive control-first disposition; Task 9's P1 High-prior REPLAN projection realized on Day 2, surfaced early by the front-load).

---

## 1. The control (PR24/PR27, `MINE_CROSSTERM_DESIGN.md` §5 probe 2)

Built on the Day-1 residual decomposition (which reproduces the harness residuals row-for-row), the warm-point control compares the current emit against the design's H1 re-keying and two alternatives — all evaluated at the NLP KKT point, `modelstat` asserted, `x.up=inf` BANNED. Nonzero-residual-row count (`|N|>1`, over the `d`-domain):

| Hypothesis | nonzero rows | Finding |
|---|---|---|
| **baseline** (current emit) | **22** | the CASE_B warm residual (matches the harness) |
| **H1 head-label re-keying** | **22** | **IDENTICAL to baseline** — `d_N` = `d_Nh1` row-for-row; **value-invariant** |
| obj-sign flip (BANNED, diagnostic only) | 11 | only halves; refuted 4× S30–S31; would break the cold emit |
| max-convention upper-bound transfer | 19 | closes only the 3 upper-bound-active `x.m>0` rows; not the `c`-boundary |

## 2. Why H1 cannot close the residual (the value-invariance proof, empirically confirmed)

The NLP precedence constraint is head-placed: `pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j)`, so its dual lives at the head label `pr.m(k,l+1,i,j)`. The emit transfer (line 79) already reads the head-label dual and stores it at the body label: `lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))`. Therefore, for any read in the `stat_x` cross-term:

- **body-keyed** `lam_pr(k,l,·)` = `abs(pr.m(k,l+1,·))` = the value a **head-keyed** `lam_pr_head(k,l+1,·)` would hold.

So the head-keyed cross-term is **value-identical** to the current body-keyed one (`d_Nh1` = `d_N`, confirmed 22 = 22 row-for-row). The design's H1 "re-key `comp_pr`/`lam_pr` + the cross-term to the head label" changes the **complementarity pairing** (a solve-structure change) but **not the `stat_x` warm residual** — and the design's own gate is *warm residual `N → 0`*, which H1 leaves untouched. **H1 cannot pass its own gate.**

## 3. Why no emit-consistent change closes the `c`-boundary (the deeper gap)

At the max row `stat_x(3,1,1)` (Day-1 decomposition): `x` at its **upper bound**, NLP reduced cost `x.m = 0` (degenerate — the NLP puts the binding entirely into the precedence duals), so no bound multiplier is available; `dbg_obj = −16000`; the cross-term is **structurally correct** (Task 3) and equals **−16000** (`= −Σ_k lam_pr(k,2,1,1)`, `lam_pr ≥ 0` for the `≥`-complementarity). Residual `N = −32000`. To close it the cross-terms must supply **+16000**, but:
- the lag coefficient is structurally **−1** and `lam_pr ≥ 0` ⇒ the term is ≤ 0 (cannot be +16000 without a **banned** sign flip or a **structural** cross-term change Task 3 refuted);
- `x.m = 0` ⇒ no bound multiplier can absorb the gap.

So the NLP KKT point is **genuinely not an MCP-stationary point under the correct emit** at the `c`-boundary — a **head-offset dual-architecture mismatch** (the head-placed precedence dual does not map to the MCP `stat_x` stationarity at the boundary), not a keying or bound-transfer defect. The residual spans **22 rows** — materially broader than the banked "6 bound-active rows" characterization.

## 4. Disposition — REPLAN (H3), no `src/`

- **H1 REFUTED** (value-invariant), **H2 insufficient** (the `d\c`-ring reconciliation targets 3 ring rows; the ≥19 `c`-boundary/other rows remain), the bound-transfer variant closes only 3, and the obj-sign flip is BANNED and only halves. Per `MINE_CROSSTERM_DESIGN.md` §5 ("… else REPLAN (H3)"), the residual is an **intrinsic head-offset dual-architecture gap** → **REPLAN to a dedicated head-offset dual subsystem (Sprint 34)**.
- **The de-risked hand-off:** this document + the Day-1 residual decomposition + `MINE_CROSSTERM_DESIGN.md` pin the exact gap (the head-placed precedence dual `pr.m(k,l+1)` vs the `stat_x` boundary stationarity; 22-row breadth; the `x.m=0` degeneracy at the `c`-boundary). A Sprint-34 subsystem must reconcile the head-offset dual with the MCP stationarity at the boundary — likely a reformulation of how head-placed constraint duals enter `stat_x`, not a keying tweak.
- **mine stays `model_infeasible`.** No Solve/floor gain from P1.
- **Freed budget ~14–18 h → P6 + P7** (Task 9 reallocation order): the P6 failure-cohort (agreste scope-verify + the `path_syntax_error` 8-cohort) and the P7 fixtures/tracking.

## 5. KPI impact (honest projection realized)

Task 9 rated P1 **High**-prior for REPLAN (its banked premise was twice-refuted in prep). That is now realized on **Day 2** — the earliest possible, exactly what the deep-track front-load is for. The in-sprint Solve movers reduce to **{fawley [P3-H-a]}** alone; Solve +1 now rests entirely on P3 (Days 4–5). The modal flat-KPI outcome (Task 9) tightens. **The sprint's product here is the de-risking: a control-confirmed refutation of H1 + a precisely-characterized Sprint-34 hand-off, with zero broken code shipped.**

---
**Document Created:** 2026-07-17 · **Owner:** Sprint 33 execution (Day 2) · Disposition: REPLAN (H3) → Sprint 34.
