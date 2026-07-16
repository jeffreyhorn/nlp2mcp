# Sprint 33 — Day 0 Trace Notes (Kickoff + Day-0 Traces + Control Probes)

**Date:** 2026-07-16 · **Day:** 0 · **Branch:** `planning/sprint33-day0-kickoff`
**Scope:** trace/probe-only — read-only harness runs + one `/tmp` control substrate; **no `src/` change**.
**Verdict: GO for Day 1.**

---

## 1. GO/NO-GO gate — `git diff ee51ed9e..HEAD -- src/ scripts/`

**✅ GREEN — empty.** No `src/` or `scripts/` change since the Sprint-32-close code anchor `ee51ed9e`; the S32 pipeline state holds, so the full retest is safely skipped and the S32-close baseline is inherited. (All Sprint-33 prep PRs #1562–1572 were docs-only.)

## 2. Baseline confirmation (142 convex-candidate corpus) — vs the committed DB

| Metric | Day-0 | DB cross-check |
|---|---|---|
| Parse | 142 | 142 convex/likely_convex candidates ✓ |
| Translate | 135 | 7 non-translate ✓ |
| Solve | 107 | 63 `model_optimal` (cold) + 44 `model_optimal_presolve` ✓ |
| Match (as-measured) | 92 | `comparison_status = match` ✓ |
| genuine floor | 74 | PR25 partition (74 genuine + 21 methodology) ✓ |
| model_infeasible | 7 | agreste, camcge, cesam, fawley, lnts, mine, rocket ✓ |
| all-219 Match | 95 | 74 genuine + 21 methodology ✓ |
| Tests | 5,085 | (S32 close) |

All-219 `outcome_category` sweep confirms the adjacent cohorts: 8 `path_syntax_error` (the Task-10 P6 cohort), 9 `path_solve_license`, 4 `path_solve_terminated`, 7 `not_tested`. **Baseline matches `BASELINE_METRICS.md` exactly.**

## 3. Day-0 traces (PR24) — Phase-0 fingerprints re-confirmed on the LIVE tree

Run via `.venv/bin/python scripts/diagnostics/kkt_residual.py <model>.gms --tol 0.001` (the harness emits the MCP internally + warm-starts from the NLP KKT point):

| Track | Model | Verdict (live) | Fingerprint (live vs banked) | Dual transfer |
|---|---|---|---|---|
| **P1** | mine | **CASE_B** | `stat_x(3,1,1)` rel **2.37** (raw −3.20e4), dual scale 1.35e4 — **exact** | **CONSISTENT** (comp 0, eq 0) |
| **P3** | fawley | **CASE_B** | `stat_bq(*,fuel-oil)` rel **0.973** (raw **473**), **uniform** across the whole fuel-oil column (res-arab-l/-h, res-brega, fuel-imp, fuel-equiv) — **exact** | **CONSISTENT** (comp 0, eq 1.8e-12) |
| **P5** | rocket | **CASE_C_OBJDEF** | boundary `stat_ht(h0)` rel **1.00** / `stat_step` 0.497 / `stat_ht(h50)` 0.438, interior near tol — **exact**; the harness itself notes "the sign flip is BANNED" | **CONSISTENT** (closure 1.53e-10) |
| **P2** | sarf | `translate_failure` | no harness (does not translate) — see §4 probe | n/a |
| **P4** | camcge | `model_infeasible` MS-4 | CASE_B `stat_mps` cleared by S32 step 1; residual is the Walras rank-deficiency (harness cold run > 2 min; DB confirms MS-4) | banked |

**The three deep-track / Case-c fingerprints (mine, fawley, rocket) re-confirm EXACTLY on the current tree** — the banked Sprint-32 diagnoses hold at Day 0; no drift. Task 3's finding also holds: mine's residual concentrates on the `stat_x` bound-active `c`-boundary rows (`stat_x(3,1,1)`, `(1,3,1)`, `(4,1,1)`, `(3,1,2)`, …) with the duals CONSISTENT — i.e. the emitted cross-term is not the defect; the multiplier keying is.

## 4. Control probes

**(1) P1 H1 head-label re-keying — control SUBSTRATE set up; the fix surface is pinned; the → MS-1 control is a Day-1 emit-layer prototype.** Generated `/tmp/mine_mcp_presolve.gms` and pinned the exact H1 surface:
- **Line 79:** `lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))` — the transfer reads `pr.m` at the **shifted** head label `l+1` but keys `lam_pr` at the **base** `l`.
- **Line 107 (`stat_x`):** the cross-term (verbatim) `sum(k, lam_pr(k,l,i-li(k),j-lj(k))$(c(l,i-li(k),j-lj(k))) - lam_pr(k,l-1,i,j)$(c(l-1,i,j)))` reads `lam_pr` at `l`/`l-1`.
- **Line 110 (`comp_pr`):** `comp_pr(k,l,i,j)$((c(l,i,j)) and (ord(l) <= card(l) - 1)).. x(l,i+li(k),j+lj(k)) - x(l+1,i,j) =G= 0;` — pairs `lam_pr(k,l)` with this `x(l,.)`/`x(l+1,.)` coupling.
- This is exactly the Task-3 multiplier-keying question (the cross-term is correct; the `lam_pr` value lives at `l+1` while the `stat_x`/`comp_pr` keying reads `l`).
- **Why the → MS-1 control is Day-1, not a Day-0 `/tmp` text edit:** `kkt_residual.py` emits internally (it does not accept a pre-emitted `.gms`), and a standalone `gams /tmp/mine_mcp_presolve.gms` errors on the mine emit's **dynamic-`c`-set membership** (the emit warns "Set membership for `c` cannot be evaluated statically"; `profit.l` unpopulated → 5 compile errors) — the presolve file needs the pipeline's NLP→MCP flow. So the H1 re-keying → `N → 0` at the 6 bound-active rows → MS-1 @ 17500 control is an **emit-layer (`src/`) prototype run through the harness** — the Day-1 opener. Consistent with Task 9 (P1 = the deepest, **High**-prior from-scratch track).

**(2) P2 sarf O(active) — Cartesian confirmed; active count banked.** `task(g,t,mn,mn)` (source line 394) over `card(g)·card(t)·card(mn)·card(mn) = 16·24·31·31 = 369,024` (confirmed from the set declarations), guarded by `taskposs(g,t)` (line 371) ∧ `tech(g,m,n)` (line 131). The **398 active** instances (`taskposs ∧ tech`) — a **927× reduction** — is the banked Task-4 GAMS-data-probe count (369,024 / 398 = 927.2). The three enumeration sites (S1 `acost3` body-diff, S2 variable-column, S3 stationarity) are confirmed present.

**(3) P3 fawley localize-by-column — base 473 re-confirmed; the 473→18 sameas control is a Day-1 emit-layer prototype.** The live harness re-confirms `max|stat_bq|` = **473** (rel 0.973), **uniform** across the entire `fuel-oil` column (the over-sum signature). The `$(sameas(cfq__,cf))` patch that closes 473→18 [96%] + the residual-18.47 localize-by-column (the H-a/H-b discriminator) operate on the emitted `stat_bq` cross-term — like P1, an emit-layer prototype (the harness emits internally), so the H-a/H-b split is the Day-4/5 P3 gate. The uniform-column base residual is exactly the banked transpose-column fingerprint.

## 5. PR25 tally (Day-0 anchor)

genuine floor **74** (S30 70 + S31 P2's +4: polygon + ps2_f_s/ps2_s/ps3_s_gic) · methodology-recovered **21** · all-219 Match **95**. The genuine-floor → +1 conversion map: **P1 mine H1 cold-match** or **P3 fawley's genuine cross-term correction** (the firmest lever — lands even under H-b). **P5 = 0 floor.**

## 6. Disposition

**GO for Day 1.** The gate is GREEN, the baseline is confirmed, and the three deep-track/Case-c fingerprints re-confirm **exactly** on the live tree (no drift from the banked S32 diagnoses). The P1 H1 and P3 sameas controls are correctly **emit-layer prototypes** (the harness emits internally; the standalone-`/tmp` path is blocked by mine's dynamic-`c`-set membership) — they open Days 1 and 4 respectively, each behind its Phase-0 gate. No `src/` change today.

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 execution (Day 0)
