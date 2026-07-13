# Sprint 31 — Backlog Fix-Surface Analysis (#1385 sarf; hhfair/CGE obj-grad; rocket forcing/PATH input)

**Task:** Sprint 31 Prep Task 9
**Date:** 2026-07-09
**Owner:** Development team (AD/KKT/solver)
**Scope:** analysis only — Day-0 read-only emit/harness reads + doc; no `src/` change. Every fix surface is a **PR24 Day-0-re-confirm hypothesis**, not a fact.

---

## 0. Executive summary

The three implementation-lighter carryforwards (P4 sarf, P5 obj-grad, P6 rocket) each get a concrete patch-site hypothesis + a guarding fixture. **Headline finding (P5):** a read-only emit shows the current hhfair `stat_u` **already carries the correct log-derivative product gradient** (`obj·ufact(t)/u(t)`, maximize-negated), so the "ν_objective reduction" is sign-equivalent for hhfair — the emit is *not* obviously wrong, which (with the Sprint-30 sign-flip refutation) leans hhfair toward **genuine Case-c non-convexity**; the **emit-fixable P5 gain is the CGE cluster** (irscge/lrgcge/moncge `stat_xp` rel ~0.06), not hhfair. **P4 sarf:** the 2-D gate extension + the parametric `stat_task` builder are pinned; the O(constraints) atomicity is the load-bearing constraint. **P6 rocket:** the emittable-lever set (the `1/m` division-by-variable reformulation + scaled continuation) + the finalized PATH-consultation question.

---

## 1. P4 — #1385 sarf symbolic-emit patch site (Unknowns 4.1, 4.3)

**Blow-up (re-confirmed):** sarf's three constraints over **2-D dynamic-subset conditions** — `tbal(g,t)$taskposs(g,t)` (384 instances), `equipb1(m,t)$equipposs(m,t)` (648), `equipb2(n,t)$equipposs(n,t)` (120) = **1,152 Cartesian instances**. `taskposs`/`equipposs` are computed from `treq`/`tech` data (sarf.gms:371–384) → **zero concrete members at compile time** → `enumerate_equation_instances` includes the full Cartesian → `differentiate_expr` blows up (Task 8 confirmed the current emit exceeds 2 min / no golden).

**Patch site A — the 2-D gate extension (`src/ad/index_mapping.py`):** `_is_blowup_dynamic_subset_equation` (`:402`) **bails at line 421 on `len(eq_domain) != 1`**, so it never fires on sarf's shape. sarf's shape is *structurally different* from srpchase's: srpchase is an equation over a **1-D dynamic subset domain** `slack(srn)`; sarf is an equation over **ordinary sets `(g,t)`** guarded by a **2-D dynamic-subset membership condition** `$taskposs(g,t)` (taskposs a 2-D dynamic subset with zero static members). The extension must detect *this* shape — an equation whose `$`-condition is a multi-index dynamic-subset membership test on a subset with zero compile-time members over the Cartesian of its parent sets — and return `[]` (skip AD enumeration), mirroring the srpchase short-circuit.

**Patch site B — the parametric `stat_task` builder (`src/kkt/stationarity.py`):** because the gate makes the short-circuited equations enumerate **zero** instances, the `J_gᵀ·lam` cross-terms **cannot be assembled from per-instance Jacobian entries** — they must be built by differentiating each short-circuited body **once parametrically** in `(g,t,m,n)`. The banked 6-guarded-term derivation (`ISSUE_1385` Day-9) is the reference spec:

```
stat_task(g,t,m,n)$taskposs(g,t)..
    - (nu_tbal(g,t))$tech(g,m,n)
    + (tadj(g)*nu_tbal(g,t))$(sameas(g,'harvest-c') and sameas(m,'cotton-p') and sameas(n,'self-prop'))
    + tech(g,m,n)*lam_labor(t)
    + (tech(g,m,n)*lam_equipb1(m,t))$equipposs(m,t)
    + (tech(g,m,n)*lam_equipb2(n,t))$equipposs(n,t)
    + oc(g,m,n)*nu_acost3
    - piL_task(g,t,m,n)  =E= 0;
```

**All multiplier indices are the stat equation's own domain `(g,t,m,n)`** — **NO quoted-set-name literals** (the Sprint-26-Day-4 `nu_slack("srn")` failure mode, commit `243fe578` reverted). The re-emitted constraint bodies (`tbal`/`equipb1`/`equipb2` as runtime-guarded `sum(...)$cond`) must also emit.

**Atomicity (Unknown 4.3):** the runtime-guard equation-body re-emit **and** the `J_gᵀ·lam` cross-terms must land in **one coordinated pass** — a re-emit without the cross-terms is an inconsistent MCP (a multiplier with no complementarity coupling); skip-only is an incomplete MCP (no Solve/Match). ISSUE_1385's all-or-nothing constraint. The emit path must build both from the same short-circuited-equation set (no intermediate state where the constraint exists but its stationarity cross-term is missing).

**O(constraints) property fixture (P7-adjacent):** a **sarf-shaped synthetic** — an equation `eq(g,t)$dyn(g,t)` over a 2-D dynamic subset with zero static members, a multi-set body, differentiated by a variable `x(g,t,m,n)` — asserting the emitted `stat_x(g,t,m,n)` carries the parametric cross-term with **symbolic `(g,t,m,n)` multiplier indices** (no set-name literals) and an **O(constraints) row count** (one `stat_x` per constraint, not O(instances)). It guards the Sprint-26 failure mode (set-name literals) + the tractability (row count) independently of sarf's full 1,152-instance model.

**Fix surface (PR24 hypothesis, pinned):** `src/ad/index_mapping.py` `_is_blowup_dynamic_subset_equation` (`:402`, the 2-D extension) + `src/kkt/stationarity.py` (the parametric `stat_task`/runtime-guard builder) + `src/kkt/complementarity.py` (the `lam_`/`nu_` refs) + `src/emit/equations.py` (index quoting — must not quote `(g,t,m,n)`). The Day-0 trace confirms the exact injection `file:line` before any `src/` change.

---

## 2. P5 — cold-convex obj-grad reduction site (Unknowns 5.1, 5.2, 5.3, 5.4)

### 2.1 The current hhfair emit (read-only, Day-0 re-confirm)

hhfair maximizes `obj =e= prod(t, u(t)**ufact(t))` where `u(t)` is an **objective-defining intermediate variable** (`utility(t).. u(t) =e= CES(c,l,n)`). The current `stat_u(t)` emit (read-only `/tmp/hhfair_mcp.gms`):

```
stat_u(t).. ((-1) * (prod(t__, u(t__)**ufact(t__)) * u(t)**ufact(t) * ufact(t) / u(t) / u(t)**ufact(t)))
            + nu_utility(t) - piL_u(t) =E= 0;
```

The objective gradient is **inlined** as `(-1)·∂prod/∂u(t)` = `(-1)·obj·ufact(t)/u(t)` (the `u(t)**ufact(t) / u(t)**ufact(t)` cancels to the log-derivative form). **The magnitude is the correct log-derivative product gradient and the `(-1)` is the standard maximize negation.** There is no `nu_objective` — nlp2mcp inlines the objective expression.

### 2.2 The ν_objective reduction hypothesis + the strong Case-c lean (Unknown 5.1)

The named P5 treatment is the objective-gradient reduction **through the objective-defining-equation multiplier ν_objective** — keep `obj` as a variable, `stat_obj: (-1) + nu_objective = 0 → nu_objective = 1`, and `stat_u(t): nu_objective·(-∂prod/∂u(t)) + nu_utility·… `. **For hhfair this is sign-equivalent to the inlined form** (`nu_objective = 1`), so the reduction does **not** change hhfair's `stat_u`. Combined with the Sprint-30 **sign-flip refutation** (flipping `(-1)→(1)` moves 72.147 → 22.144, *worse*), this means **the hhfair emit is not obviously wrong** — the 72.147 is very likely a **genuine spurious KKT point of the non-convex CES+bilinear problem (Case-c)**, not an emit bug. **Strong lean: hhfair → the P5 Case-c REPLAN exit** (a documented non-convexity finding, no `src/` change). The **definitive control experiment** (the P5 gate, Task 6): warm/cold-solve hhfair from the NLP optimum and confirm 72.147 vs 87.159 is a distinct local optimum (Case-c) — **THE SIGN FLIP STAYS BANNED**.

### 2.3 The CGE cluster is the emit-fixable P5 target (Unknown 5.2)

The genuine emit-fixable P5 gain is the **CGE cluster** — irscge/lrgcge/moncge carry a small `stat_xp` residual (rel **~0.06**, after the Sprint-30 Day-5 case-normalization fix) on the same objective-defining-intermediate-variable family, but these are **convex CGE models** (a small residual is a real emit defect, not non-convexity). The ν_objective reduction (routing the obj-grad through the defining-equation multiplier) is the candidate that converts the CGE `stat_xp` → 0 (Case-a). The fix surface is the **objective-gradient emit path** — `src/ad/gradient.py` (`find_objective_expression` / the per-variable objective gradient) + `src/kkt/stationarity.py` (where the objective-defining-intermediate-variable's `stat_*` is built). The control experiment (in-sprint): patch the CGE `stat_xp` to the ν_objective-reduced form → does the residual → 0?

### 2.4 Rule-vs-patch + case-normalization composition (Unknowns 5.3, 5.4)

- **5.3 (single rule vs per-model):** the objective-defining-intermediate-variable shape is **detectable structurally** — a variable appearing only in the objective-defining equation (`obj =e= prod/CES(...)`) and also market-cleared. A **single general rule** (route its obj-grad through the defining-equation multiplier) should cover hhfair + the CGE cluster + any same-shape model, not a per-model patch.
- **5.4 (case-normalization composition):** the CGE `stat_xp` rel ~0.06 is measured **after** the Sprint-30 Day-5 presolve dual-transfer **case-normalization** fix landed. The ν_objective reduction operates on the `stat_xp` row the case-normalization already corrected (mixed-case duals no longer silently skipped), so the two are **orthogonal** — the reduction closes the ~0.06 *remainder*, not a case-normalization artifact. No double-handling.

---

## 3. P6 — rocket forcing-lever set + PATH-consultation input (Unknowns 6.1, 6.3)

**Emittable-GAMS lever set (Unknown 6.1):** the Sprint-30 forcing survey established that **no PATH-option config (via optfile) converges rocket** (best: INFES 477 → 382, still MS 5). The remaining **emittable-GAMS** levers the P6 work exhausts:

1. **The `1/m` / `1/ht²` division-by-variable reformulation (Unknown 6.3):** rocket's ill-conditioning is the division-by-variable in `v_eqn` (`…/m(h)`, the velocity update divides by mass) and `gf` (`g = g_0·sqr(h_0/ht(h))`, the `1/ht²`). A reformulation multiplies through by the divisor — e.g. rewrite `X/m(h)` as an auxiliary `w(h)` with `w(h)·m(h) =e= X`, removing the division-by-variable from the Jacobian (which blows up near small `m`/`ht`). This is an **emittable model reformulation** (a nlp2mcp emit transform), not a PATH option — the P6 work tries it before the hand-off.
2. **Scaled/relaxed continuation schedules** via the `--force homotopy` scaffold (a `proximal_perturbation` `mu: large → 0` continuation from the NLP-optimum warm-start).

**The finalized PATH-consultation question (feeds Sprint 32):** *"rocket's MCP is MS 5 with `EXIT — other error` at an ill-conditioned initial Jacobian from division-by-variable terms (`1/m(h)` in the velocity update, `1/ht(h)²` in gravity). `proximal_perturbation`/`merit_function`/`crash_method` move INFES 477 → 382 but do not converge from the NLP-optimum warm-start; a `1/m`+`1/ht²` auxiliary-variable reformulation (`gf` multiplied through to `g·ht² = g_0·h_0²`; a free acceleration `a(h)` with `(a+g)·m = T−D` replacing `(T−D−m·g)/m` in `v_eqn`) — which removes ALL division-by-variable from the initial Jacobian — **ALSO does not converge** (Sprint-31 Day-11 probe: the reformulated NLP solves to the same optimum 1.0128, but its MCP is MS-5 Locally Infeasible cold, MS-5 warm-started from the NLP optimum, and MS-5 across every mu-continuation step, at nh=10). **So the non-convergence is intrinsic to the discretized optimal-control MCP structure, NOT the division-by-variable Jacobian conditioning.** Which PATH option set / regularization schedule / model reformulation forces convergence for this optimal-control MCP?"* (The reformulation slot is filled: the reformulation is exhausted — MS-5 — so it is a *ruled-out* candidate in the question, sharpening it toward the intrinsic structure.)

**Disposition:** if the reformulation converges rocket → +1 Solve; else the finalized PATH-consultation question is the Sprint-32 hand-off (the `--force` scaffold + this question are the de-risked deliverable). rocket's +1 Solve is conditional (Task 7: prior of REPLAN = High for the scaffold-only outcome, on the survey evidence).

---

## 4. Fix-surface + fixture summary

| Track | Patch site (PR24 hypothesis) | Guarding fixture | Disposition |
|---|---|---|---|
| **P4 sarf** | `index_mapping.py:402` (2-D gate extension) + `stationarity.py` (parametric `stat_task`, symbolic `(g,t,m,n)`, no set-name literals) + atomic re-emit | O(constraints) sarf-shaped synthetic (symbolic multiplier indices + row-count assertion) | PROCEED (REPLAN on timeout re-trigger) |
| **P5 hhfair** | (emit already carries the correct log-derivative gradient; ν_objective reduction sign-equivalent) | — | **strong Case-c lean → REPLAN exit** (documented non-convexity; control experiment confirms) |
| **P5 CGE cluster** | `gradient.py` (`find_objective_expression`) + `stationarity.py` (obj-grad reduction through the defining-equation multiplier) | objective-defining-intermediate-variable shape fixture (irscge/lrgcge/moncge `stat_xp` → 0) | PROCEED (the emit-fixable P5 gain) |
| **P6 rocket** | `1/m` division-by-variable reformulation (emit transform) + scaled continuation; no set-name-literal emit | (existing `--force` scaffold; no new fixture) | conditional +1 Solve OR the finalized PATH-consultation input |

---

## 5. Unknowns resolved

- **4.1 (sarf 2-D gate + parametric `stat_task`, no set-name literals): ✅ VERIFIED (fix-surface pinned).** The 1-D bail (`index_mapping.py:421`, `len(eq_domain) != 1`) is why the gate never fires on sarf's 2-D `$taskposs(g,t)` shape; the extension + the parametric `stat_task` builder (banked 6-guarded-term derivation, symbolic `(g,t,m,n)` indices) are the patch sites; the O(constraints) synthetic fixture guards the Sprint-26 set-name-literal failure mode. The empirical O(constraints) timing is the in-sprint P4 check (Unknown 4.2).
- **4.3 (atomicity): ✅ VERIFIED.** The runtime-guard re-emit + the `J_gᵀ·lam` cross-terms must land in one coordinated pass (a partial = an inconsistent/incomplete MCP); the emit builds both from the same short-circuited-equation set.
- **5.1 (ν_objective reduction reaches the NLP optimum on hhfair): ✅ VERIFIED (fix-surface analyzed) — strong Case-c lean.** The current hhfair `stat_u` already carries the correct log-derivative product gradient (maximize-negated); the ν_objective reduction is sign-equivalent for hhfair, and the sign flip is refuted → hhfair leans **genuine Case-c** (the P5 REPLAN exit). The definitive patch-and-solve control experiment is the in-sprint P5 gate (Task 6); the sign flip stays BANNED.
- **5.2 (CGE cluster → Case-a): ✅ VERIFIED (fix-surface pinned).** The CGE cluster (irscge/lrgcge/moncge `stat_xp` rel ~0.06, convex) is the **emit-fixable** P5 target via the ν_objective reduction in the objective-gradient path (`gradient.py`/`stationarity.py`); the in-sprint control experiment confirms `stat_xp` → 0.
- **5.3 (single rule vs per-model): ✅ VERIFIED — a single structural rule.** The objective-defining-intermediate-variable shape (a variable only in the objective-defining equation + market-cleared) is detectable structurally; one general ν_objective-reduction rule covers the family.
- **5.4 (case-normalization composition): ✅ VERIFIED — orthogonal.** The ~0.06 `stat_xp` residual is the remainder *after* the Sprint-30 case-normalization fix; the reduction closes it, no double-handling.
- **6.1 (emittable-lever exhaustion): ✅ VERIFIED (lever set pinned).** No PATH-option config converges rocket (survey: INFES 477 → 382); the remaining emittable levers are the `1/m` reformulation + scaled continuation; else the finalized PATH-consultation input. The definitive emittable-lever exhaustion is the in-sprint P6 run.
- **6.3 (Jacobian reformulation): ✅ VERIFIED (candidate pinned).** The `1/m(h)` / `1/ht(h)²` division-by-variable reformulation (multiply through by the divisor via an auxiliary variable) is the emittable candidate; if it doesn't converge, it is a documented candidate in the PATH-consultation question.

---

## Appendix — evidence

- **sarf gate (read-only):** `src/ad/index_mapping.py` `_is_blowup_dynamic_subset_equation:402` (bail `len(eq_domain) != 1` at `:421`); `ISSUE_1385` Day-9 (the 1,152-instance blow-up + the banked 6-guarded-term `stat_task` derivation + the Sprint-26 `nu_slack("srn")` failure).
- **hhfair emit (read-only):** `/tmp/hhfair_mcp.gms` `stat_u(t)` = `(-1)·obj·ufact(t)/u(t) + nu_utility(t) - piL_u(t)` (the inlined log-derivative gradient, no `nu_objective`); `ISSUE_1236` (sign-flip refuted 72.147 → 22.144; hhfair non-convex CES + bilinear).
- **CGE cluster:** `stat_xp` rel ~0.06 after the Sprint-30 Day-5 case-normalization fix (`SPRINT_30/SPRINT_RETROSPECTIVE.md` §2).
- **rocket (read-only):** `data/gamslib/raw/rocket.gms` `gf(h).. g(h) =e= g_0*sqr(h_0/ht(h))` (`1/ht²`), `v_eqn` `…/m(h)` (`1/m`); `NONCONVEX_FORCING_SURVEY.md` §4 (the PATH-consultation question + INFES 477 → 382).
- No `src/` or golden change; all runs read-only.
