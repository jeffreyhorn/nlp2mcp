# Sprint 34 — Day 1 Progress Notes (P1 mine H_dual — control executed, H3′ REPLAN)

**Date:** 2026-07-20
**Branch:** `planning/sprint34-day1-mine-hdual`
**Track:** P1 — mine head-offset dual subsystem (#1443)
**Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P1 — the H_dual `/tmp` cold-MS-1 prototype must pass **before** any `src/` change (PR27 control-first).
**Disposition:** ❌ **H3′ REPLAN — control-refuted before any `src/` change.** mine stays `model_infeasible`. **No `src/` shipped.** Budget ~14–18 h freed → P6/P7 (Task 9 reallocation).

---

## 1. What was run (the pre-`src/` `/tmp` control, `MINE_DUAL_SUBSYSTEM_DESIGN.md` §5)

The control ran **before** any `src/` edit — the whole point of the PR27 gate. Two cold MCP solves from the repo root:

| Prototype | comp_pr / lam_pr / stat_x | Cold solve |
|---|---|---|
| **Baseline** (`data/gamslib/mcp/mine_mcp.gms`) | **body**-keyed (`comp_pr(k,l,i,j)$c(l,i,j)`, `x(l,i+li,j+lj) − x(l+1,i,j)`) | **MS-5 Locally Infeasible**, profit **16747.0723**, **51 INFES** |
| **H_dual** (`/tmp/mine_hdual_cold.gms`) | **head**-anchored (`comp_pr(k,l,i,j)$c(l-1,i,j) and ord(l)≥2`, `x(l-1,i+li,j+lj) − x(l,i,j)`; `lam_pr` head-labeled; `stat_x` cross-terms re-indexed to the head-labeled `lam_pr`; `lam_pr.fx` gated to the head domain) | **MS-5 Locally Infeasible**, profit **16747.0723**, **51 INFES** — **byte-identical to baseline** |

The H_dual prototype compiled with **0 errors** (well-formed) yet produced the **identical scalar result** (same modelstat, same profit to 4 dp, same INFES count). The gate — **the cold MCP reaching MS-1 @ 17500** (`modelstat=1`; `x.up=inf` BANNED) — is **NOT met**.

### The re-keying, concretely (the faithful H_dual per §4.1/§4.2)

`pr` is head-placed in the source: `pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li,j+lj) =g= x(l+1,i,j)` (`mine.gms:62`) — GAMS stores `pr.m` at the head label `(k,l+1,i,j)`. The emit re-keys `comp_pr`/`lam_pr` to the body label `l`. H_dual re-anchors to the head label:

```
comp_pr(k,l,i,j)$((c(l,i,j)) and (ord(l)<=card(l)-1)).. x(l,i+li(k),j+lj(k)) - x(l+1,i,j) =G= 0;   # body
comp_pr(k,l,i,j)$((c(l-1,i,j)) and (ord(l)>=2)).. x(l-1,i+li(k),j+lj(k)) - x(l,i,j) =G= 0;          # head (H_dual)

stat_x … sum(k, lam_pr(k,l,i-li,j-lj)$c(l,i-li,j-lj) - lam_pr(k,l-1,i,j)$c(l-1,i,j)) …             # body
stat_x … sum(k, lam_pr(k,l+1,i-li,j-lj)$c(l,i-li,j-lj) - lam_pr(k,l,i,j)$c(l-1,i,j)) …             # head (H_dual)
```

## 2. The finding — H_dual is value-invariant on the *cold* solve (extends S33)

Re-keying `comp_pr` + `lam_pr` + `stat_x` **together** to the head label produces the **identical scalar MCP**: each `(inequality ⊥ dual)` pair is the same physical pair, only relabeled `l ↔ l+1`, and `stat_x`'s cross-term **values** are unchanged (the same `lam_pr` instances, relabeled). GAMS therefore generates the same scalar complementarity system → the cold solve is invariant.

- **S33 Day-2 proved:** H1 head-label re-keying is value-invariant on the **warm residual** (22→22 rows, `d_N=d_Nh1`).
- **S34 Day-1 now proves:** H_dual re-anchoring is value-invariant on the **cold solve** too (the scalar MCP is unchanged: identical MS-5 / profit / 51 INFES).

So the **reframed cold-MS-1 gate** — the correct diagnostic in principle (§4.1) — is **not passable by any keying/pairing reformulation.** The design's own §3.2 predicted this: at `stat_x(3,1,1)`, `N = obj(−16000) + lag(−16000) = −32000`; closing needs **+16000**, but the lag coefficient is structurally `−1·lam_pr` with `lam_pr ≥ 0` (≤ 0, cannot be +16000 without the **banned** sign flip or a **structural cross-term change the S33 re-derivation refuted**), and `x.m=0` ⇒ **no bound multiplier** to absorb it.

## 3. Where the infeasibility sits — a genuine dual-degeneracy

- The **51 INFES rows are the `comp_pr` precedence complementarities** (indexed `k.l.i.j` — e.g. `nw.1.3.1`, marginals ~4e10) + the `def` accounting equality — the precedence **dual** system cannot be reconciled in the cold solve.
- The **LP primal is feasible/optimal at 17500** (mine NLP reference `model_status=1, obj 17500.0`). So mine's MCP failure is **purely a dual-reconciliation degeneracy**, not a primal one: the boundary rows (`c`-boundary + `d\c` ring, 22 rows) exhibit primal degeneracy (`x` at a bound, `x.m=0`, the shadow value pushed into the precedence duals), and **no emit-consistent keying/pairing change reaches a feasible MCP stationary point.**

## 4. Disposition — H3′ REPLAN (the designed exit, `MINE_DUAL_SUBSYSTEM_DESIGN.md` §6)

**H3′ REPLAN — control-confirmed, before any `src/`.** The `/tmp` H_dual prototype cannot drive the cold MCP to MS-1 @ 17500; the boundary is a **genuine dual-degeneracy the emit cannot deterministically reconcile** via keying/pairing. Per the pinned exit:

- **mine stays `model_infeasible`.** No `src/` shipped (the 9th+ control-first mine disposition — zero broken code, matching S31/S32/S33).
- **Hand-off to Sprint 35:** either a **deeper head-offset dual architecture** (a reformulation that genuinely changes the scalar system without a sign flip / bound multiplier / LP-altering domain change — an open research question), **or the PATH-consultation track** — mine is exactly the design's §6 candidate: *an LP whose warm KKT point is not MCP-reconcilable*. The de-risked hand-off is `MINE_DUAL_SUBSYSTEM_DESIGN.md` + this Day-1 control (baseline + H_dual prototype both cold MS-5, scalar-invariant).
- **Budget reallocation (Task 9):** mine's remaining ~14–18 h → **P6** (the ganges/gangesx `$141/$145/$149` cohort — the designated best-remaining-shot) + **P7**. The P1 REPLAN surfaces on **Day 1**, ahead of the Day-3 close / Day-5 checkpoint — exactly what front-loading the High-prior track is for (S33 surfaced mine's REPLAN by Day 2).

## 5. No-regression

No `src/` change → the corpus is trivially byte-stable; `--resolve-changed --since-commit 750803b2` remains GO (Day-0 result stands). The KPI baseline is unmoved: Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7.

---

**Verdict:** ❌ **P1 mine H3′ REPLAN (control-refuted, Day 1).** H_dual re-anchoring is value-invariant on the cold solve (the scalar MCP is unchanged); the reframed cold-MS-1 gate is not passable by keying/pairing; mine's boundary is a genuine dual-degeneracy. Handed to Sprint 35 (deeper dual architecture or PATH-consultation). No `src/` shipped; ~14–18 h → P6/P7.
