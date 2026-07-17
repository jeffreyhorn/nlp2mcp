# Sprint 33 — Day 1 Progress Notes (P1 mine: Phase-0 control + residual decomposition)

**Date:** 2026-07-16 · **Day:** 1 · **Branch:** `planning/sprint33-day1-mine-multiplier-keying`
**Status:** WIP — the Phase-0 control (§5 probe 1, residual decomposition) is set up and run with a **validated, precise diagnosis**; the H1 emit-layer re-keying (probe 2 → `src/`) is the Day-2/3 continuation. **No `src/` change today** (the control gate is not yet at PROCEED; the src change awaits the design these findings inform — PR24/PR27).

---

## 1. The standalone presolve control now runs (Day-0 blocker cleared)

Day 0 found `gams /tmp/mine_mcp_presolve.gms` errored (dynamic-`c`-set membership). **Root cause: the emit `$include "data/gamslib/raw/mine.gms"` is repo-relative** — the file must run from the repo root, not `/tmp`. Generated the presolve emit to a repo-root scratch and ran it there:

- Embedded NLP → **MODEL STATUS 1** (the warm-start source).
- Warm-started MCP → **MODEL STATUS 5 Locally Infeasible**, `nlp2mcp_obj_val = 22058.949`.

**This reproduces the banked `MINE_5TH_COUPLING_REPLAN` signature EXACTLY** (MCP MS-5 @ 22058, the NLP optimum being 17500). The `/tmp` control substrate is live for the H1 prototype.

## 2. Residual decomposition (§5 probe 1) — VALIDATED against the harness

Inserted, right before the MCP `Solve`, a term-by-term decomposition of `stat_x` evaluated at the warm (`.l`) point:
`dbg_obj` = `(-1)*(conc*value/100 - cost)` · `dbg_t1` = `sum(k, lam_pr.l(k,l,i-li(k),j-lj(k))$c…)` (lead) · `dbg_t2` = `-sum(k, lam_pr.l(k,l-1,i,j)$c…)` (lag) · `dbg_bnd` = `-piL_x.l + piU_x.l` · `dbg_N` = their sum.

**`dbg_N` reproduces the harness residuals row-for-row** (dual scale 1.35e4):

| Row | `dbg_N` (raw) | harness rel | ✓ |
|---|---|---|---|
| stat_x(3,1,1) | **−32000** | 2.37 | ✓ (−32000/13500 = 2.37) |
| stat_x(1,3,1) | 14500 | 1.07 | ✓ |
| stat_x(4,1,1) | −11000 | 0.82 | ✓ |
| stat_x(2,3,3) | 10000 | 0.74 | ✓ |
| stat_x(3,1,2) | −9000 | 0.67 | ✓ |

The decomposition is faithful — it *is* the `stat_x` residual the harness measures.

## 3. The diagnosis — a cross-term VALUE mismatch at the `c`-boundary (confirms H1 direction)

Per-term breakdown at the **max** row `stat_x(3,1,1)`:

| Term | Value | Reading |
|---|---|---|
| `dbg_obj` | −16000 | the objective gradient |
| `dbg_t1` (lead) | 0 | `i-li`/`j-lj` out of range at `i=j=1` → no lead term (correct) |
| `dbg_t2` (lag) | −16000 | `-sum(k, lam_pr.l(k,2,1,1)$c(2,1,1))` |
| `dbg_bnd` | 0 | **no bound-multiplier contribution** (see below) |
| **`dbg_N`** | **−32000** | obj + t2 (both negative — they *add*) |

**The decisive facts:**
- `dbg_xl(3,1,1) = 1.000` — `x(3,1,1)` is at its **upper bound**.
- `dbg_xm(3,1,1) = 0` — but its **NLP reduced cost is zero** (the NLP puts the binding into the precedence duals, not the box bound), so the bound-multiplier transfer (lines 82–83) correctly yields **`piL=piU=0` everywhere** (`dbg_piL`/`dbg_piU` = ALL 0).
- Therefore the residual is **entirely a cross-term VALUE mismatch**: to close, `stat_x(3,1,1)` needs the cross-terms to supply **+16000** (balancing `obj=−16000` with `piU=0`), but the warm-started `lam_pr` values supply **−16000**. A **32000 gap**, purely in the head-offset dual contribution.

**This confirms Task 3's direction and localizes it:** the cross-term *structure* is correct (Task 3), and the box-bound transfer is correct (0). The defect is the **head-offset marginal VALUE-keying** — the interaction of the line-79 transfer `lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))` (the `l+1` head-label read + `abs`) with the `stat_x` cross-term's `l`/`l-1` keying — so the warm-started `lam_pr` instances do not reproduce the NLP's precedence-dual contribution at the `c`-boundary rows. This is the **H1 head-label multiplier-keying** surface, now backed by term-level evidence (not just the hand-derivation).

## 4. Disposition + next step

- **No `src/` change today.** The residual-decomposition control (§5 probe 1) is complete and the diagnosis is validated; the **H1 hand-patch prototype (§5 probe 2)** — re-key `lam_pr`/`comp_pr` + the `stat_x` cross-term to the head label so `N → 0` at the boundary rows → MS-1 @ 17500 — is the decisive gate that must pass **before** the `src/` change. That prototype + the emit/IR plumbing (`head_domain_offsets` carrier; `_try_build_param_offset_crossterm`) is the Day-2/3 work (sized 10–14 h, `MINE_CROSSTERM_DESIGN.md` §6).
- **Honesty (Task 9, P1 High-prior):** the decomposition shows the residual spans many `c`-boundary rows (not a single term/sign), consistent with the re-scoped multiplier-keying diagnosis. The H3 REPLAN exit stays live if the H1 prototype cannot drive `N → 0` without perturbing interior rows or regressing srpchase.
- **`x.up=inf` BANNED; `modelstat` asserted** (both honored — the control reads the MCP MODEL STATUS directly).

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 execution (Day 1) · WIP — Day-2/3 continues the H1 prototype → `src/`.
