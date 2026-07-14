# sarf 4-D `task`-Variable Stationarity Sparsification — Design

**Created:** 2026-07-13
**Prep Task:** 4 (Priority 2 foundation)
**Issue:** #1385
**Status:** Design (prep) — the fix is designed here; the in-sprint P2 work implements + validates it behind the Phase-0 gate (Task 8).

**Objective:** Design the **O(active-instances) symbolic `stat_task` emit** over the `$taskposs`-active subset that makes sarf translate, sparsifying the 369,024-instance 4-D `task(g,t,mn,mn)` variable's stationarity to the active entries, coupled atomically with the 2-D dynamic-subset constraint gate (built + reverted Sprint 31). All experiments below are read-only (a GAMS data probe + code reads); no `src/` change.

---

## §1. Sizing: 369,024 Cartesian vs the `$taskposs`-active subset (Unknown 2.4)

A GAMS data probe (loads sarf's `treq`/`tech`/`taskposs` data, aborts before the model) gives the hard counts:

| quantity | value |
|---|---|
| `card(g)` (agricultural tasks) | 16 |
| `card(t)` (fortnights) | 24 |
| `card(mn)` (implements + power sources) | 31 |
| **Cartesian** `card(g)·card(t)·card(mn)·card(mn)` | **369,024** |
| `card(taskposs)` (active `(g,t)`) | 129 |
| `card(equipposs)` (active `(mn,t)`) | 329 |
| **`card(taskact)` = active `task(g,t,m,n)`** (`taskposs(g,t)` ∧ `tech(g,m,n)`) | **398** |

**The O(active) target is 398, a 927× reduction from the 369,024 Cartesian.** So the sparsified emit is decisively tractable — the whole timeout is the translate-time enumeration/differentiation of the 369K Cartesian; 398 active entries (or, at translate time, a **single symbolic guarded equation**) is trivial.

Probe (inserted after sarf.gms's `display …` at line 386, aborting before the solve):
```gams
Set taskact(g,t,mn,mn);
taskact(g,t,m,n) = yes$(taskposs(g,t) and tech(g,m,n));
display card(g), card(t), card(mn), card(taskposs), card(equipposs), card(taskact);
* → 16, 24, 31, 129, 329, 398 ;  Cartesian = 16*24*31*31 = 369,024
```

---

## §2. Model structure (why `stat_task` blows up)

```gams
Set m(mn) 'implements';  n(mn) 'power sources';          * static subsets of mn (not aliases)
Variable task(g,t,mn,mn) 'agricultural tasks by technology';   * declared over the full 369,024 Cartesian
taskposs(g,t) = sum((c,s), yes$treq(g,t,c,s));           * data-derived dynamic subset (0 static members at compile time)
tbal(g,t)$taskposs(g,t)..    … =e= sum((m,n)$tech(g,m,n), task(g,t,m,n)) - tadj(g)*task('harvest-c',t,'cotton-p','self-prop');
equipb1(m,t)$equipposs(m,t)..  sum((g,n)$taskposs(g,t), tech(g,m,n)*task(g,t,m,n)) =l= avail(m)*equipp(m);
equipb2(n,t)$equipposs(n,t)..  sum((g,m)$taskposs(g,t), tech(g,m,n)*task(g,t,m,n)) =l= avail(n)*equipp(n);
acost3..  cost('operating') =e= sum((g,t,m,n)$taskposs(g,t), oc(g,m,n)*task(g,t,m,n));
```

`task(g,t,m,n)` is **declared** over the full `(g,t,mn,mn)` = 369,024, but only ever **appears** conditioned on `$taskposs(g,t)` ∧ `$tech(g,m,n)` (and `$oc`), i.e. the **398 active entries**. The other 369,024 − 398 = **368,626 columns are vacuous** (touch no constraint) — they must be **fixed** (`task.fx = 0`) so MCP matching is valid (exactly the mine non-`d` precedent).

**The blow-up:** the current variable-stationarity builder materializes `stat_task(g,t,m,n)` for **every** Cartesian instance (369K) and differentiates each — `differentiate_expr` over 369K is the `translate_timeout` (>180s). The 2-D constraint gate (Sprint-31 Day 8) short-circuits `tbal`/`equipb1`/`equipb2` (1,152 constraint instances) but does **nothing** about the 369K `stat_task` enumeration — necessary but insufficient.

---

## §3. The sparsified `stat_task` emit (Unknown 2.1)

**Emit ONE symbolic, guarded `stat_task` equation** (the banked ISSUE_1385 hand-derivation) instead of 369K materialized instances, plus fix the inactive columns:

```gams
task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;    * fix the 368,626 vacuous columns

stat_task(g,t,m,n)$taskposs(g,t)..
    - (nu_tbal(g,t))$tech(g,m,n)
    + (tadj(g)*nu_tbal(g,t))$(sameas(g,'harvest-c') and sameas(m,'cotton-p') and sameas(n,'self-prop'))
    + tech(g,m,n)*lam_labor(t)
    + (tech(g,m,n)*lam_equipb1(m,t))$equipposs(m,t)
    + (tech(g,m,n)*lam_equipb2(n,t))$equipposs(n,t)
    + oc(g,m,n)*nu_acost3
    - piL_task(g,t,m,n)  =E= 0;
```

**Translate-time cost = O(1 symbolic equation)** (a handful of parametric terms), not O(369K). GAMS instantiates the guarded equation at **runtime**: the `$taskposs(g,t)` head + per-term `$tech`/`$equipposs`/`sameas` guards + the `task.fx$(not active)` fixing collapse it to the **398 live rows** (the fixed columns' paired `stat_task` rows drop under MCP matching).

**Emit sites (2, coordinated):**
- `src/ad/index_mapping.py` — extend the short-circuit so the **`task`-variable stationarity** enumeration is not materialized over the 369K Cartesian (the analogue of `_is_blowup_dynamic_subset_equation` for a variable whose defining constraints are all `$dynamic-subset`-guarded). The 4-D `task` stationarity is emitted parametrically, not per-instance.
- `src/kkt/stationarity.py` — the **new symbolic runtime-guard cross-term emit path**: because the short-circuited constraints enumerate **zero** per-instance Jacobian entries, the `stat_task` cross-terms are built by **symbolically differentiating each constraint body once, parametrically in `(g,t,m,n)`** (the banked 7-term form above), carrying the `$taskposs`/`$equipposs`/`$tech` runtime guards; plus the `task.fx$(not active)` fixing.

---

## §4. 2-D-gate atomicity coupling (Unknown 2.2)

The re-landed **2-D constraint gate** (`_is_blowup_2d_condition_equation` — extend `_is_blowup_dynamic_subset_equation`'s `len(eq_domain) != 1` bail to the 2-D `taskposs(g,t)`/`equipposs(m,t)` shape on `tbal`/`equipb1`/`equipb2`) and the **4-D `task` sparsification** (§3) must land **atomically** in one change:

- The constraint gate makes `tbal`/`equipb1`/`equipb2` enumerate **zero** instances → their `J_gᵀ·lam` contributions to `stat_task` (and to `stat_xcrop`, `stat_equipp`, …) **cannot be assembled from per-instance Jacobian entries**; they must come from the §3 parametric cross-term path.
- **Re-emit-without-cross-terms = an inconsistent MCP** (multipliers `nu_tbal`/`lam_equipb1`/`lam_equipb2` with no stationarity coupling) — ISSUE_1385's atomicity constraint. There is **no safe partial landing**: the guarded constraint re-emit + the parametric `stat_task` (and every other `stat_*` the short-circuited constraints touch) + the `task.fx` fixing assemble at a **single atomic point**.

**Coupling design:** the 2-D gate signals which constraints are short-circuited; the parametric cross-term path in `stationarity.py` iterates those constraints, differentiates each body once in the stat variable's domain, and injects the guarded term into every `stat_*` it touches — so the constraint short-circuit and its cross-term compensation are produced together, never separately.

---

## §5. Symbolic-index anti-pattern guard (Unknown 2.3)

The Sprint-26-Day-4 architecture (commit `243fe578`, reverted) emitted **set-name-literal multiplier indices** — `nu_slack("srn")`/`lam_demand("srn")` where `srn` is a *set name*, not an element — producing UEL/domain errors and dropped cross-terms. The banked `stat_task` (§3) is **already symbolic**: every multiplier is indexed by the stat equation's own domain — `nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)` — with **no quoted-set-name indices**. The structural guard (ISSUE_1385's committed check) is a compile-clean scan of the emitted MCP:

```bash
# must be empty — no quoted-set-name multiplier indices
grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms
```

The parametric emit path must build multiplier references from the constraint's **declared domain symbols** (mapped to the stat variable's domain), never from a literal set name encountered during body traversal.

---

## §6. O(active) translate-budget gate + re-scoping REPLAN exit

**Gate (in-sprint P2, behind the Task-8 Phase-0 gate):**
1. **Translate under budget.** Time `sarf` translate → `sarf_mcp.gms`; it must complete **well under the timeout** (the current failure is >180s; the O(1-symbolic-equation) emit should be seconds — srpchase's 1-D analogue is 6.56s). The emit must be **O(active)/O(constraints), not O(369K instances)**.
2. **`stat_task` matches the banked derivation.** The emitted `stat_task` equals the §3 7-term form (verify term-by-term); no set-name-literal indices (§5).
3. **Atomic + complete.** Every `stat_*` the short-circuited constraints touch carries its cross-term; the golden is byte-stable; `--resolve-changed` GO (sarf is the only changed golden — no regression to the 136 byte-stable models or the other timeout cohort).
4. **(Post-fix) harness verifier.** Once sarf emits a *complete* MCP, `kkt_residual.py data/gamslib/raw/sarf.gms` becomes the correctness verifier (Case-a/b) — but the Task-4 deliverable is **+Translate** (`translate_failure → translate`), not Solve/Match.

**Re-scoping REPLAN exit:** REPLAN (re-scope to a deeper Sprint-33 symbolic-emit workstream) iff the parametric emit **re-triggers the translate timeout** (the O(1) emit unexpectedly still materializes instances), OR the atomic cross-term assembly proves intractable in-budget against the Sprint-26 failure mode. In that case the P2 budget reallocates per Task 9; the 398-active sizing + the banked `stat_task` + the atomicity spec remain the de-risked hand-off.

---

## §7. Summary + Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 2.1 | Does the sparsified `stat_task` emit make sarf O(active), not O(369K)? | ✅ VERIFIED — YES: emit ONE symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (translate-time O(1 equation)) + `task.fx$(not active)`; sites `src/ad/index_mapping.py` (variable-stationarity short-circuit) + `src/kkt/stationarity.py` (parametric cross-term path). |
| 2.2 | Does the 4-D sparsification couple atomically with the 2-D constraint gate? | ✅ VERIFIED (design) — the constraint short-circuit enumerates zero Jacobian entries, so the `stat_task` cross-terms MUST come from the parametric path; re-emit + cross-terms + `task.fx` assemble at a single atomic point (no safe partial). |
| 2.3 | Does the parametric `stat_task` avoid set-name-literal indices? | ✅ VERIFIED — the banked derivation is symbolic (`nu_tbal(g,t)`, `lam_equipb1(m,t)`, …, over the stat domain); the `grep 'nu_*("' / 'lam_*("'` compile-clean scan is the structural guard against the 243fe578 anti-pattern. |
| 2.4 | What is the `$taskposs`-active subset size (the O(active) target)? | ✅ VERIFIED — **398** active `task(g,t,m,n)` (`taskposs(g,t)` ∧ `tech(g,m,n)`) vs **369,024** Cartesian (a 927× reduction); GAMS data probe. |

**Decision: PROCEED** to the in-sprint P2 implementation — the sparsification target is decisively small (398 vs 369K), the banked `stat_task` is symbolic and complete, and the atomic-coupling design is pinned to `src/ad/index_mapping.py` + `src/kkt/stationarity.py`. It remains a **high-risk architectural rebuild** (the 4×-failed Sprint-26 path), so the Task-8 O(active) translate-budget gate + the atomicity/anti-pattern checks + the explicit re-scoping REPLAN exit are load-bearing.

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team (AD/emit specialist)
**Evidence:** GAMS data probe on `sarf.gms` (Cartesian 369,024; taskposs 129; active task 398); `src/ad/index_mapping.py` `_is_blowup_dynamic_subset_equation` (1-D gate, `len(eq_domain) != 1` bail; cross-terms deferred) — 2-D gate confirmed **absent from main** (reverted Day 8); the banked `stat_task` derivation (ISSUE_1385) + the `243fe578` `nu_slack("srn")` anti-pattern.
