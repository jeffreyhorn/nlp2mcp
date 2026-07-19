# sarf #1385 — Symbolic/Parametric `stat_task` Emit-Mode: Design (Sprint 34 Prep Task 4)

**Created:** 2026-07-19 · **Owner:** Sprint 34 prep (AD/emit specialist)
**Prep Task:** 4 (Priority 2 foundation) · **Priority:** High
**Day-0 code anchor:** `750803b2` (S33 close) · no `src/` drift since (Task 2 `BASELINE_METRICS.md`)
**Anchors:** `SPRINT_33/DAY6_SARF_ASSESSMENT.md` (Option-B REPLAN → Sprint 34; the tractability verdict) · `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` (the three-site analysis, the 7-term derivation, the atomicity spec)

> **Disposition (prep):** this document carries the Sprint-33 Option-B hand-off into a Sprint-34-executable **emit-mode design** — re-confirmed live on the S33-close tree — for the `task(g,t,mn,mn)` variable: stop enumerating its **369,024** columns at all three sites and emit **one guarded symbolic `stat_task`** + `task.fx`. **No `src/` change** (atomicity forbids a partial); the O(active) translate-budget gate is the Sprint-34 in-sprint gate that must pass **before** the golden ships. sarf is the **lowest-leverage bucket** (+1 Translate → 136, moving neither Solve nor Match) and the **highest-effort/highest-risk** track (the 4×-failed Sprint-26 path).

---

## 1. Day-0 re-confirm (the blow-up locus still holds — live)

Bounded translate probe on the live tree (S33-close `750803b2`, 2026-07-19):

| Stage | Time |
|---|---|
| parse + normalize | ~36 s (reaches "Normalizing model…") |
| **`compute_constraint_jacobian`** | **> 116 s and still running when capped** (`src/ad/constraint_jacobian.py:1247` `enumerate_equation_instances` for `tbal`) ← the blow-up |

The `translate_timeout` is in the **constraint Jacobian**, not the stationarity build — exactly the S33 Day-6 locus (`SPRINT_33/DAY6_SARF_ASSESSMENT.md` §1, which measured > 90 s). Code facts re-confirmed live:
- **The 2-D constraint gate is absent from `src/`** — `_is_blowup_2d_condition_equation` has **0 matches** in `src/` (reverted/removed Sprint 32, not merely non-firing).
- **The 1-D base gate is present** — `_is_blowup_dynamic_subset_equation` (`src/ad/index_mapping.py:402`); it gates **equation** enumeration only (returns `[]` and drops cross-terms), not **variable-column** enumeration.
- The enumeration fires at `src/ad/constraint_jacobian.py:798/1247` (`enumerate_equation_instances`) for the `task`-referencing constraints.

**Sizing (banked GAMS data probe, byte-identical GAMSlib model):** Cartesian `card(g)·card(t)·card(mn)·card(mn) = 16·24·31·31 = 369,024`; `card(taskposs)=129`, `card(equipposs)=329`; **active `task(g,t,m,n)` (`taskposs(g,t) ∧ tech(g,m,n)`) = 398** — a **927× reduction**. srpchase (the 1-D analogue) translates in **~2.9 s** — the O(active) reference. `taskposs` is **runtime-computed from data** (`taskposs(g,t) = sum((c,s), yes$treq(g,t,c,s))`, `data/gamslib/raw/sarf.gms:371`), so the 398 active columns are **not statically enumerable** at translate time — the fix cannot be "enumerate only the 398"; it must **stop enumerating `task`'s columns entirely** and emit a symbolic guarded equation.

---

## 2. The THREE enumeration sites (Unknown 2.1)

The Sprint-32/33 finding: the 2-D constraint gate short-circuits `tbal`/`equipb1`/`equipb2` (1,152 instances) but is **necessary, not sufficient** — the 369,024 `task` columns still materialize at **three** other sites, all of which must be eliminated **atomically** (§5):

| # | Site | Why it materializes 369K | live locus |
|---|---|---|---|
| **S1** | **`acost3` body-differentiation** in `compute_constraint_jacobian` | `acost3.. cost("operating") =e= sum((g,t,m,n)$taskposs(g,t), oc(g,m,n)·task(g,t,m,n))` (`sarf.gms:454`) is a **scalar** equation (1 head instance — the 2-D constraint gate never touches it), but `∂/∂task` of its body sum materializes a Jacobian **column entry per `task` ref** (369K). | `src/ad/constraint_jacobian.py` (`compute_constraint_jacobian`, `:679`) |
| **S2** | **variable-column enumeration** | `task(g,t,mn,mn)` (`sarf.gms:394`) is declared over the full 369,024 Cartesian; `enumerate_variable_instances(task)` builds every column (368,626 of which are vacuous — touch no constraint). | `src/ad/index_mapping.py` (`enumerate_variable_instances`, def `:327`, call `:634`) |
| **S3** | **variable stationarity** | the builder materializes `stat_task(g,t,m,n)` for **every** Cartesian column and differentiates each. | `src/kkt/stationarity.py` |

The 2-D **constraint gate** (`tbal`/`equipb1`/`equipb2`) is the *fourth* piece — designed + reverted Sprint 32; it re-lands with these three (§5).

---

## 3. The symbolic/parametric emit **mode** — O(active) per site

This is a **different emit MODE** for the blow-up variable: symbolic/parametric, not the current fully-enumerated per-column architecture. Per site:

- **S1 (`acost3`):** differentiate the `acost3` body **once parametrically** — `∂(sum((g,t,m,n)$taskposs, oc·task))/∂task(g,t,m,n) = oc(g,m,n)·nu_acost3`, carried as the guarded `stat_task` **term [6]** (`+ oc(g,m,n)*nu_acost3`), instead of 369K Jacobian column entries. `acost3`'s own row is O(1).
- **S2 (variable enumeration):** emit `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;` — fixing the **368,626 vacuous columns** so MCP matching is valid (the mine non-`d` precedent); `task` is treated as a single guarded symbol, and GAMS instantiates only the **398 active** columns at runtime.
- **S3 (variable stationarity):** emit **one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)`** (§4) instead of 369K materialized instances — translate-time cost **O(1 equation)**.

**The 398-row target comes from the *combination*, not the head guard alone:** `$taskposs(g,t)` alone still expands across all `(m,n)` per active `(g,t)` (~124K rows); `task.fx` fixes the non-active columns, and **under MCP matching the fixed columns — and their paired `stat_task` rows — drop**, so GAMS instantiates only the **398** live `taskposs ∧ tech` rows (the per-term `$tech`/`$equipposs`/`sameas` guards zero the remaining terms).

---

## 4. The symbolic `stat_task` emit (the 7-term derivation — Unknowns 2.1/2.3)

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

**Verified term-for-term against the live sarf constraint bodies** (`data/gamslib/raw/sarf.gms`):

| term | source constraint (line) | ∂/∂task(g,t,m,n) |
|---|---|---|
| [1] | `tbal(g,t)..` RHS `sum((m,n)$tech(g,m,n), task(g,t,m,n))` (`:427`) | `−nu_tbal(g,t)$tech(g,m,n)` |
| [2] | the harvest-c mechanical-picking adjustment (`tadj(g) / spray 1 /` `:375`; `taskposs("spray",t)=…+taskposs("harvest-c",t)` `:379`) | `+tadj·nu_tbal` on the `harvest-c/cotton-p/self-prop` cell |
| [3] | `labor(t)..` `+ sum((g,m,n)$taskposs(g,t), tech(g,m,n)*task(g,t,m,n))` (`:~440`) | `+tech(g,m,n)*lam_labor(t)` |
| [4] | `equipb1(m,t)$equipposs(m,t)..` `sum((g,n)$taskposs(g,t), tech·task)` (`:443`) | `+tech(g,m,n)*lam_equipb1(m,t)$equipposs(m,t)` |
| [5] | `equipb2(n,t)$equipposs(n,t)..` `sum((g,m)$taskposs(g,t), tech·task)` (`:446`) | `+tech(g,m,n)*lam_equipb2(n,t)$equipposs(n,t)` |
| [6] | `acost3.. cost("operating") =e= sum((g,t,m,n)$taskposs, oc·task)` (`:454`, **S1**) | `+oc(g,m,n)*nu_acost3` |
| [7] | `task.lo = 0` (Positive Variable `task`, `:402`) | `−piL_task(g,t,m,n)` |

**Every multiplier is indexed by the stat equation's own domain** — `nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)` — with **no quoted-set-name indices** (the guard against the reverted Sprint-26 `243fe578` `nu_slack("srn")` anti-pattern, Unknown 2.3). GAMS collapses the guarded equation to the **398 live rows** at runtime.

**Fix surface (a Day-0-re-confirm hypothesis, PR24):**
- `src/ad/constraint_jacobian.py` — short-circuit the `acost3` body-differentiation (S1) so `task` is not differentiated per-column over the Cartesian (its contribution comes from the parametric path);
- `src/ad/index_mapping.py` — extend the short-circuit so the `task`-variable column enumeration (S2) is not materialized over the Cartesian (`enumerate_variable_instances` treats `task` as guarded-symbolic);
- `src/kkt/stationarity.py` — the **new parametric cross-term path**: because the short-circuited constraints (incl. the parametrically-handled `acost3`, S1) enumerate **zero** per-instance Jacobian entries, the `stat_task` cross-terms are built by differentiating each constraint body **once, parametrically in `(g,t,m,n)`** (the 7-term form), carrying the runtime `$` guards.

The S27 lesson stands: prep-doc `file:line` is wrong ~4× — trace + re-confirm on Day 0/1 before editing.

---

## 5. Atomicity + the O(active) budget gate (Unknowns 2.2, 2.5)

**Atomic-landing requirement (Unknown 2.2).** The 2-D constraint gate + the S1/S2/S3 parametric emit + `task.fx` land in **one change**. The gate makes `tbal`/`equipb1`/`equipb2` enumerate **zero** instances → their `Jᵀ·λ` contributions to `stat_task` (and `stat_xcrop`/`stat_equipp`/…) **cannot be assembled from per-instance Jacobian entries** — they must come from the parametric path. **Re-emit-without-cross-terms = an inconsistent MCP** (multipliers with no stationarity coupling). There is **no safe partial landing**.

**O(active) translate-budget gate (the Task-8 Phase-0 gate).** In-sprint, **before** the golden ships:
1. **Translate under budget.** Time `sarf → sarf_mcp.gms`; must complete in **seconds** (O(active)/O(constraints), not O(369K)) — the srpchase ~2.9 s reference; the current failure is > 116 s.
2. **`stat_task` matches the derivation (§4) term-by-term; no set-name-literal indices** — the compile-clean scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` returns nothing (Unknown 2.3).
3. **Atomic + complete + byte-stable.** Every `stat_*` the short-circuited constraints touch carries its cross-term; the golden is deterministic ×3 `PYTHONHASHSEED`; `--resolve-changed --since-commit 750803b2` **GO** (sarf is the only changed golden — no regression to the 135 byte-stable models) (Unknown 2.5).

---

## 6. Sizing + REPLAN exit (Unknown 2.5)

**20–28 h** — a from-scratch symbolic-emit **mode** touching **three layers** (`constraint_jacobian.py` [S1] + `index_mapping.py` [S2] + `stationarity.py` [S3]; the 4×-failed Sprint-26 path; **high risk**):
- Re-land + extend the 2-D constraint gate (`_is_blowup_2d_condition_equation`, banked) + the S1 `acost3` short-circuit in `constraint_jacobian.py` + the S2 short-circuit in `index_mapping.py` (~6–9 h).
- The parametric cross-term path in `stationarity.py` (differentiate each short-circuited body once in `(g,t,m,n)`; inject the guarded term into every `stat_*` it touches; the `acost3`/S1 parametric ∂; `task.fx`) (~9–13 h).
- The O(active) budget gate + anti-pattern grep + determinism ×3 + `--resolve-changed` + a `shape13` regression fixture (~4–6 h).

**Timeout-re-trigger REPLAN exit:** REPLAN (re-scope to a deeper symbolic-emit workstream, or a later sprint) iff the parametric emit **re-triggers the translate timeout** (the O(1) emit unexpectedly still materializes instances), OR the atomic cross-term assembly proves intractable in-budget against the Sprint-26 failure mode. Then sarf stays `translate_timeout` (Translate maintains 135 — moves neither Solve nor Match), and the de-risked hand-off is: the re-confirmed blow-up locus, the 1-D base gate, the 398-active sizing, the 7-term derivation, and this atomicity spec.

**Front-load:** P2 runs Days 1–7 with the tractability probe first, so the timeout-re-trigger decision surfaces by the **Day-5 checkpoint** (Task 9). Given the lowest-leverage bucket + highest risk, an early REPLAN frees budget → P4/P6.

---

## 7. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **2.1** | ✅ **VERIFIED** | Eliminating 369K requires **all three** sites atomically — S1 `acost3` body-differentiation (parametric ∂ → term [6]), S2 variable-column enumeration (`task.fx` + guarded-symbolic mapping), S3 variable stationarity (one symbolic `stat_task`). Fixing only the constraint gate is insufficient (re-confirmed live: the blow-up persists > 116 s in `compute_constraint_jacobian`). |
| **2.2** | ✅ **VERIFIED** | The constraint short-circuit enumerates zero Jacobian entries, so the `stat_task` cross-terms **must** come from the parametric path; gate + parametric `stat_task` + `task.fx` assemble at a single atomic point — no safe partial (re-emit-without-cross-terms = inconsistent MCP). This is a design/architecture verdict; the **executed** O(active) translate gate is the Sprint-34 in-sprint gate (Task 8 / Day 1–7). |
| **2.3** | ✅ **VERIFIED** | The 7-term `stat_task` is symbolic — every multiplier over the stat domain (`nu_tbal(g,t)`, `lam_equipb1(m,t)`, `nu_acost3`, …), **no** quoted-set-name indices; the term-for-term derivation is re-verified against the live sarf bodies (§4); the compile-clean anti-pattern grep is the structural guard against the `243fe578` anti-pattern. |
| **2.4** | ✅ **VERIFIED** | `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` fixes the 368,626 vacuous columns; the `$(not active)` guard exactly complements the `$taskposs∧$tech`-active 398 (the mine non-`d` precedent) — PATH accepts the fixing, the fixed columns' `stat_task` rows drop under MCP matching. `$taskposs` alone gives ~124K rows, so the 398 comes from the **combination** (head guard + `task.fx` + MCP matching), not the head guard alone. |
| **2.5** | ✅ **VERIFIED** | Byte-stable/deterministic is enforced by the O(active) budget gate (§5): determinism ×3 + `--resolve-changed --since-commit 750803b2` GO + the anti-pattern grep; sized **20–28 h** with the timeout-re-trigger REPLAN exit. |

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 4 (design; no `src/`)
**Last Updated:** 2026-07-19 · **Owner:** Sprint 34 prep (AD/emit specialist)
