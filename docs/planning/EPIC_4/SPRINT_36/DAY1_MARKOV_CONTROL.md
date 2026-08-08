# Sprint 36 — Day 1: markov P1 Phase-0 `CASE_A` `/tmp` Control + Cold-Solve Gate

**Date:** 2026-08-07 · **Branch:** `planning/sprint36-day1-markov-control` · **Scope:** `/tmp`-only control (PR27 discipline — control BEFORE any `src/`); no `src/`, no golden change.

**Outcome: the Phase-0 gate PASSES. The hand-built `CASE_A` markov MCP (reconciliation (a): Kronecker diagonal + full `σ=sp` off-diagonal) COLD-solves (no warm-start) to the reference LP optimum exactly — `pvcost = 2401.577`, `max|Δz| = 4.6e-07`, MODEL STATUS 1 Optimal — whereas the committed (buggy `CASE_B`) MCP cold-solves to a spurious complementary point at `pvcost = 2571.794` (mismatch). So a correct cold emit moves markov out of the methodology partition into a genuine cold match ⇒ genuine floor 75 → 76 (+1). REPLAN NOT triggered; reconciliation (a) is the arbiter's choice (no exclusion guard needed).** Verifies Unknown 1.4 (methodology→genuine); confirms the `MARKOV_OFFDIAGONAL_DESIGN.md` §2 target form + §5 gate.

Reference: `MARKOV_OFFDIAGONAL_DESIGN.md` (Task 3) §2 (target form), §5 (`CASE_A` control); `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` (Part-1 13.3→1.55). markov is an **LP** (`solve strategic using lp minimizing pvcost`) — so the KKT/MCP is exact and a correct emit must cold-solve to the LP optimum.

---

## 1. Method (control before `src/`)

markov is tiny (2 primal var families / 3 constraint families; 213-line MCP) → the control is seconds-scale and fully local. Per `MARKOV_OFFDIAGONAL_DESIGN.md` §5, I hand-edited the emitted `markov_mcp.gms` `stat_z` to the §2 `CASE_A` target and cold-solved it — decoupling the **payoff** (does a correct emit cold-solve to a genuine match?) from the **Part-2 `src/` implementation** (Days 2–3). This is the PR27 "validate the payoff with a control before investing in `src/`" discipline.

**The edit (reconciliation (a)):** replace the 45 spurious `nu_constr` offset-from-`s` groups (the `σ`-as-offset bug) with the clean form, leaving the (correct) `lam_equil` term and `piL_z` untouched:
```
stat_z(s,i,sp)..  c(s,sp,i)
                + nu_constr(s,i)                                    [Kronecker diagonal — direct]
                - sum(j, (b * pi(s,i,sp,j,sp)) * nu_constr(sp,j))   [off-diagonal — σ=sp fixed, j summed]
                + <lam_equil term, unchanged>  - piL_z(s,i,sp)  =E= 0;
```
(`pi(s,i,sp,j,sp)` has its 3rd index = 5th index, so it evaluates to `pr(i,j)` for all `(sp,j)` — the assignment `pi(s,i,sp,j,sp)=pr(i,j)` populates exactly these entries.)

## 2. Results

| MCP | KKT residual @ reference | cold solve (no warm-start) | `pvcost` | vs reference | partition |
|---|---|---|---|---|---|
| **committed (buggy)** | `CASE_B`, max `stat_z` residual rel **13.3** (`stat_z(empty,disrupted,empty)`; harness, dual transfer CONSISTENT) | MODEL STATUS 1, compl. 1.1e-13 | **2571.794** | **mismatch** (+170) | methodology |
| **`CASE_A` (recon (a))** | → 0 (implied: cold-solves to the reference KKT point) | MODEL STATUS 1, compl. 3.7e-09 | **2401.577** | **match** (max `Δz` 4.6e-07) | **genuine** |
| reference LP optimum | — | MODEL STATUS 1 Optimal | **2401.577** | — | — |

- **Baseline `CASE_B` 13.3** re-confirmed authoritatively by `kkt_residual.py data/gamslib/raw/markov.gms` (verdict `CASE_B — emit_bug`, `stat_z(empty,disrupted,empty)` rel 1.33e+01, dual transfer CONSISTENT). **Part-1 → 1.55** stands from `DAY11_MARKOV_DIAGONAL_LEVER.md` §6 (verified there; `src/kkt/stationarity.py` + `src/ad/derivative_rules.py` byte-unchanged since — Day-0 §2 — so it reproduces deductively); the full `CASE_A` endpoint (the actual +1 gate) is directly measured here.
- **The buggy cold mismatch is the methodology mechanism made concrete:** the cold MCP finds a complementary point (compl. 1.1e-13) but at the *wrong* KKT point (2571.794) because the off-diagonal `nu_constr` coupling is mis-emitted; only the presolve warm-start (starting at the NLP solution) lands the correct point — hence `model_optimal_presolve` in the DB.
- **`CASE_A` cold → genuine match:** `pvcost` identical to the LP optimum to 7 figures and `max|Δz| = 4.6e-07` across all 128 `z` entries (16 nonzero) — a genuine primal match, cold, no warm-start.

## 3. Reconciliation arbiter (§2 (a) vs (b))

Reconciliation **(a)** (Part-1 emits the Kronecker-only `+nu_constr(s,i)`; the off-diagonal `-b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))` covers all `σ=sp` entries including the `sp=s,j=i` self-term) reached `CASE_A` with **no residual at the `sp=s,j=i` cell** → **(b)'s exclusion guard `$(not (sameas(sp,s) and sameas(j,i)))` is NOT needed.** The Day-2 `src/` Mechanism C should emit reconciliation (a) (cleaner, no guard).

## 4. Gate verdict + REPLAN status

**PASS — the +1 floor lever is real.** A `CASE_A` cold emit → cold `model_optimal` + genuine match (2401.577, Δz 4.6e-07) ⇒ markov moves methodology → genuine ⇒ **floor 75 → 76 (+1)**. The **REPLAN exit is NOT triggered** (the design's exit was "if the cold solve needs presolve even at `CASE_A`" — it does not; the cold solve reaches the exact match). The +1 is now **contingent only on landing Part-2 in `src/`** (the coordinated offset-key + emission change, Days 2–3) — the design's Mechanism C, emitting reconciliation (a).

## 5. Next

**Day 2 — P1 markov Part-2 `σ=sp`:** implement Mechanism C (`MARKOV_OFFDIAGONAL_DESIGN.md` §3–§4) in a `/tmp` control — the additive gated correction that suppresses the 45 spurious offset groups and appends the reconciliation-(a) off-diagonal, leaving the shared `_compute_index_offset_key` matcher untouched — targeting the same `max|stat_z| → 0` / cold-match this control just validated on the hand-built emit, plus the 2-D-cohort golden-staleness leak gate.

---

**Document Status:** ✅ Complete — Sprint 36 Day 1 (markov Phase-0 `CASE_A` control; gate PASS, +1 confirmed, reconciliation (a))
**Last Updated:** 2026-08-07 · **Owner:** Sprint 36 Execution Team
