# sarf #1385 — Symbolic Parametric `stat_task` Emit Subsystem: Design

**Prep Task:** 4 (Priority 2 foundation) · **Date:** 2026-07-16 · **Owner:** Sprint 33 prep (AD/emit specialist)
**Status:** design complete — **PROCEED** to the in-sprint P2 implementation against this spec (a high-risk architectural rebuild; the O(active) budget gate + atomicity + anti-pattern checks are load-bearing).

> **PR24 discipline:** the design is validated read-only (a re-profile + code reads + the banked GAMS data probe); no `src/` change. The O(active) translate-budget gate must pass in-sprint **before** the golden ships.

---

## 1. Day-0 re-confirm (the blow-up locus still holds)

Bounded re-profile of the sarf pipeline on the current tree (Sprint 32 close `ee51ed9e`):

| Stage | Time |
|---|---|
| parse | 18.9 s |
| normalize | ~0 s |
| **`compute_constraint_jacobian`** | **TIMEOUT > 75 s** (cap; the banked run was > 120 s) ← the blow-up |

The `translate_timeout` is in the **constraint Jacobian**, not the stationarity build. The enumeration warnings fire at `src/ad/constraint_jacobian.py:798` + `:1247` and `src/ad/index_mapping.py:648` for `tbal`/`equipb1`/`equipb2` (`taskposs`/`equipposs` are runtime-computed 2-D dynamic sets with 0 static members → `enumerate_equation_instances` includes the full Cartesian). The **2-D constraint gate is absent from `main`** — the symbol `_is_blowup_2d_condition_equation` **does not exist in `src/`** (reverted/removed Sprint 32; `grep -c` = 0 matches — not merely non-firing, as banked); the reusable **1-D base gate** `_is_blowup_dynamic_subset_equation` is present. This reproduces the Sprint-32 Day-6 `SARF_TRANSLATE_REPLAN.md` control.

**Sizing (banked GAMS data probe, byte-identical GAMSlib model):** Cartesian `card(g)·card(t)·card(mn)·card(mn) = 16·24·31·31 = 369,024`; `card(taskposs)=129`, `card(equipposs)=329`; **active `task(g,t,m,n)` (`taskposs(g,t) ∧ tech(g,m,n)`) = 398** — a **927× reduction**. srpchase (the 1-D analogue) translates in **~2.9 s** (6.56 s under the slower Sprint-32 runner) — the O(active) reference.

## 2. The THREE enumeration sites (Unknown 2.1)

The Sprint-32 Day-6 REPLAN's key finding: the 2-D constraint gate short-circuits `tbal`/`equipb1`/`equipb2` (1,152 instances) but is **necessary, not sufficient** — the 369,024 `task(g,t,mn,mn)` columns still materialize at **three** other sites. All three must be eliminated **atomically** (§4):

| # | Site | Why it materializes 369K | Note |
|---|---|---|---|
| **S1** | **`acost3` body-differentiation** in `compute_constraint_jacobian` | `acost3.. cost("operating") =e= sum((g,t,m,n)$taskposs(g,t), oc(g,m,n)·task(g,t,m,n))` is a **scalar** equation (1 head instance, so the 2-D constraint gate does not touch it), but `∂/∂task` of its body sum materializes a Jacobian **column entry for each of the 369K `task` refs**. | The site the Day-6 probe pinned as "insufficient". |
| **S2** | **variable-column enumeration** (`src/ad/index_mapping.py`) | `task(g,t,mn,mn)` is declared over the full 369,024 Cartesian; the column index-mapping enumerates every column (368,626 of which are vacuous — touch no constraint). | Must fix the vacuous columns (`task.fx=0`). |
| **S3** | **variable stationarity** (`src/kkt/stationarity.py`) | the current builder materializes `stat_task(g,t,m,n)` for **every** Cartesian column and differentiates each. | The banked "necessary but insufficient" §2 finding. |

The 2-D **constraint gate** (`tbal`/`equipb1`/`equipb2`) is the *fourth* piece — already designed + reverted; it re-lands with these three (§4).

## 3. The O(active) elimination — per site

- **S1 (`acost3`):** differentiate the `acost3` body **once parametrically** — `∂(sum((g,t,m,n)$taskposs, oc·task))/∂task(g,t,m,n) = oc(g,m,n)·nu_acost3`, carried as the **guarded `stat_task` term 6** (`+ oc(g,m,n)*nu_acost3`), instead of 369K Jacobian column entries. `acost3`'s own row (`stat_cost`/objective coupling) is O(1). No per-column materialization.
- **S2 (variable enumeration):** emit `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;` — fixing the **368,626 vacuous columns** so MCP matching is valid (the mine non-`d` precedent); the index-mapping materializes only the **398 active** columns (or, at translate time, treats `task` as a single guarded symbol — GAMS instantiates the 398 live columns at runtime).
- **S3 (variable stationarity):** emit **one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)`** (§3.1) instead of 369K materialized instances — translate-time cost **O(1 equation)**.

## 3.1 The symbolic `stat_task` emit (the banked 7-term derivation — Unknowns 2.1/2.3)

```gams
task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;   * fix the 368,626 vacuous columns

stat_task(g,t,m,n)$taskposs(g,t)..
    - (nu_tbal(g,t))$tech(g,m,n)                                                                  * [1] tbal
    + (tadj(g)*nu_tbal(g,t))$(sameas(g,'harvest-c') and sameas(m,'cotton-p') and sameas(n,'self-prop'))  * [2] tbal harvest-c adj
    + tech(g,m,n)*lam_labor(t)                                                                    * [3] labor balance
    + (tech(g,m,n)*lam_equipb1(m,t))$equipposs(m,t)                                               * [4] equipb1
    + (tech(g,m,n)*lam_equipb2(n,t))$equipposs(n,t)                                               * [5] equipb2
    + oc(g,m,n)*nu_acost3                                                                         * [6] acost3 (S1)
    - piL_task(g,t,m,n)  =E= 0;                                                                   * [7] lower bound
```

Verified term-for-term against the constraint bodies (`tbal`/`equipb1`/`equipb2`/`acost3`/labor + the `task.lo=0` bound). **Every multiplier is indexed by the stat equation's own domain** — `nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)` — with **no quoted-set-name indices** (the guard against the reverted Sprint-26 `243fe578` `nu_slack("srn")` anti-pattern, Unknown 2.3). GAMS collapses the guarded equation to the **398 live rows** at runtime (`$taskposs` head + `$tech`/`$equipposs`/`sameas` per-term guards; the `task.fx` columns drop under MCP matching).

**Fix surface (hypothesis):** `src/ad/constraint_jacobian.py` — short-circuit the `acost3` body-differentiation (S1) so `task` is not differentiated per-column over the Cartesian (its contribution comes from the parametric path); `src/ad/index_mapping.py` — extend the short-circuit so the `task`-variable stationarity (S3) + column enumeration (S2) are not materialized over the Cartesian; `src/kkt/stationarity.py` — the **new parametric cross-term path**: because the short-circuited constraints (incl. the parametrically-handled `acost3`, S1) enumerate **zero** per-instance Jacobian entries, the `stat_task` cross-terms are built by differentiating each constraint body **once, parametrically in `(g,t,m,n)`** (the 7-term form), carrying the runtime `$` guards.

## 4. Atomicity + the O(active) budget gate (Unknowns 2.2, 2.5)

**Atomic-landing requirement (Unknown 2.2).** The 2-D constraint gate + the S1/S2/S3 parametric emit + `task.fx` land in **one change**. The gate makes `tbal`/`equipb1`/`equipb2` enumerate **zero** instances → their `Jᵀ·λ` contributions to `stat_task` (and `stat_xcrop`/`stat_equipp`/…) **cannot be assembled from per-instance Jacobian entries** — they must come from the parametric path. **Re-emit-without-cross-terms = an inconsistent MCP** (multipliers with no stationarity coupling). There is **no safe partial landing**: the guarded constraint re-emit + the parametric `stat_task` (and every `stat_*` the short-circuited constraints touch) + `task.fx` assemble at a single atomic point.

**O(active) translate-budget gate (the Task-8 Phase-0 gate).** In-sprint, **before** the golden ships:
1. **Translate under budget.** Time `sarf` → `sarf_mcp.gms`; must complete in **seconds** (O(active)/O(constraints), not O(369K)) — the srpchase ~2.9 s reference; the current failure is > 75 s.
2. **`stat_task` matches the banked derivation** (§3.1) term-by-term; **no set-name-literal indices** — the compile-clean scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` returns nothing (Unknown 2.3).
3. **Atomic + complete + byte-stable.** Every `stat_*` the short-circuited constraints touch carries its cross-term; the golden is deterministic ×3 `PYTHONHASHSEED` (Unknown 2.5); `--resolve-changed --since-commit ee51ed9e` GO (sarf is the only changed golden — no regression to the 135 byte-stable models).

## 5. Sizing + REPLAN exit (Unknown 2.5)

**20–28 h** — a from-scratch symbolic-emit subsystem touching **three layers** (`constraint_jacobian.py` [S1] + `index_mapping.py` [S2] + `stationarity.py` [S3]; the 4×-failed Sprint-26 path; **high risk**):
- Re-land + extend the 2-D constraint gate (`_is_blowup_2d_condition_equation`, banked) + the S1 `acost3` short-circuit in `constraint_jacobian.py` + the S2/S3 short-circuit in `index_mapping.py` (~6–9 h).
- The parametric cross-term path in `stationarity.py` (differentiate each short-circuited body once in `(g,t,m,n)`; inject the guarded term into every `stat_*` it touches; the `acost3`/S1 parametric ∂; `task.fx`) (~9–13 h).
- The O(active) budget gate + anti-pattern grep + determinism ×3 + `--resolve-changed` + a shape13 regression fixture (~4–6 h).

**Timeout-re-trigger REPLAN exit:** REPLAN (re-scope to a deeper symbolic-emit workstream) iff the parametric emit **re-triggers the translate timeout** (the O(1) emit unexpectedly still materializes instances), OR the atomic cross-term assembly proves intractable in-budget against the Sprint-26 failure mode. Then sarf stays `translate_timeout` (Translate maintains 135 — the lowest-leverage KPI, moves neither Solve nor Match), and the de-risked hand-off is: the re-confirmed blow-up locus, the working 1-D base gate, the 398-active sizing, the 7-term derivation, and this atomicity spec.

## 6. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **2.1** | ✅ VERIFIED | Eliminating 369K requires **all three** sites atomically — S1 `acost3` body-differentiation (parametric ∂ → term 6), S2 variable-column enumeration (`task.fx` + 398-active mapping), S3 variable stationarity (one symbolic `stat_task`). Fixing only `compute_constraint_jacobian`'s constraint gate is insufficient (the Day-6 finding). |
| **2.2** | ✅ VERIFIED | The constraint short-circuit enumerates zero Jacobian entries, so the `stat_task` cross-terms **must** come from the parametric path; gate + parametric `stat_task` + `task.fx` assemble at a single atomic point — no safe partial (re-emit-without-cross-terms = inconsistent MCP). |
| **2.3** | ✅ VERIFIED | The banked 7-term `stat_task` is symbolic — every multiplier over the stat domain (`nu_tbal(g,t)`, `lam_equipb1(m,t)`, `nu_acost3`, …), **no** quoted-set-name indices; the `grep 'nu_*("' / 'lam_*("'` compile-clean scan is the structural guard against the `243fe578` anti-pattern. |
| **2.4** | ✅ VERIFIED | `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` fixes the 368,626 vacuous columns; the `$(not active)` guard exactly complements the `$taskposs∧$tech`-active 398 (the mine non-`d` precedent) — PATH accepts the fixing, the fixed columns' `stat_task` rows drop under MCP matching. |
| **2.5** | ✅ VERIFIED | Byte-stable/deterministic is enforced by the O(active) budget gate (§4): determinism ×3 + `--resolve-changed` GO + the anti-pattern grep; sized 20–28 h with the timeout-re-trigger REPLAN exit. |

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 prep (AD/emit specialist)
