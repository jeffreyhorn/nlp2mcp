# Sprint 32 Day 6 — sarf P2 REPLAN: 2-D gate necessary but insufficient → Sprint 33

**Date:** 2026-07-14
**Day:** 6 (Priority 2 — sarf 4-D `task` stationarity sparsification, #1385)
**Outcome:** 🔴 **REPLAN → Sprint 33 symbolic-emit workstream.** No `src/` change (the insufficient 2-D gate was reverted).
**Discipline:** a bounded implementation attempt + a profiling probe established the exact blow-up locus **before** committing any partial src — the Day-7 tractability gate, front-loaded to Day 6.

---

## 1. The blow-up locus (profiled, confirmed)

Per-stage timing of the sarf pipeline (hard-capped):

| Stage | Time |
|---|---|
| parse | 11.3 s |
| normalize | 0.0 s |
| **`compute_constraint_jacobian`** | **TIMEOUT > 120 s** ← the blow-up |

The `translate_timeout` is in the **constraint Jacobian**, not the stationarity build. GAMS warnings pinpoint the cause: `tbal(g,t)$taskposs`, `equipb1(m,t)$equipposs`, `equipb2(n,t)$equipposs` — the conditions are **runtime-computed 2-D dynamic sets** (`taskposs(g,t) = sum((c,s), yes$treq(...))`), so they cannot be evaluated at compile time and `enumerate_equation_instances` falls back to the **full Cartesian** ("Including unevaluable instances by default"). The Jacobian then differentiates each body against the **369,024-Cartesian `task(g,t,mn,mn)`** variable.

## 2. The bounded attempt — the 2-D gate is necessary but insufficient

Implemented `_is_blowup_2d_condition_equation` (`src/ad/index_mapping.py`) — extends the 1-D `_is_blowup_dynamic_subset_equation` to the 2-D dynamic-subset-**condition** shape (a `SetMembershipTest` on a 2-D dynamic set with 0 static members + a ≥100-instance Cartesian domain), wired into the same `enumerate_equation_instances` short-circuit.

- **The detector is correct + well-scoped:** it fires for exactly `sarf:tbal`, `sarf:equipb1`, `sarf:equipb2` and for **no other** sampled corpus model (srpchase/otpop/launch/camcge/hhfair/robert) — no false-fire blast radius.
- **But `compute_constraint_jacobian` still TIMES OUT > 90 s with the gate active.** Skipping the 3 constraints does **not** resolve the blow-up, because the **369,024 `task`-variable columns** still enumerate elsewhere in the Jacobian:
  - `acost3.. cost("operating") =E= sum((g,t,m,n)$taskposs(g,t), oc(g,m,n)·task(g,t,m,n))` — a **scalar** equation (not a 2-D-conditioned one, so the gate does not touch it) whose `∂/∂task` produces a Jacobian entry for **each** of the 369K `task` columns;
  - plus the `task`-variable instance enumeration itself (the 369K columns are materialized regardless of the 3 constraints).

This is **exactly the design's finding** (`SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` §5 / Task 4): *"The 2-D constraint gate short-circuits `tbal`/`equipb1`/`equipb2` but does **nothing** about the 369K `stat_task` enumeration — necessary but insufficient."* The empirical probe confirms it.

## 3. Diagnosis — the real fix is a from-scratch symbolic parametric emit

Making sarf translate requires the **369K `task` columns to never be materialized** — in the constraint Jacobian (incl. `acost3`), the variable enumeration, AND the variable stationarity — replaced by **one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)`** (the banked 7-term derivation) + `task.fx$(not active)=0`, with the cross-terms differentiated **once parametrically** (not per-instance). The current architecture builds cross-terms from **enumerated** Jacobian entries; there is **no existing path** to construct them symbolically from a short-circuited constraint. That new parametric symbolic-emit path is a **from-scratch subsystem** touching the variable-enumeration, constraint-Jacobian, and stationarity layers — not a bounded in-sprint change. This is the design's explicit re-scoping REPLAN exit (§6): *"REPLAN … iff the parametric emit re-triggers the translate timeout … OR the atomic cross-term assembly proves intractable in-budget against the Sprint-26 failure mode."*

## 4. Disposition

- **REPLAN sarf [P2] → Sprint 33** (a dedicated symbolic-emit workstream). **No `src/` change** — the insufficient 2-D gate was **reverted** (shipping the gate alone would drop cross-terms for a still-timing-out emit; no KPI gain, correctness risk). The 8th consecutive control/probe-first REPLAN across S30–S32.
- **+1 Translate deferred;** sarf stays `translate_timeout` (Translate maintains 135). This is the **lowest-leverage KPI** (moves neither Solve nor Match) — the Task-9-ranked outcome.
- **The de-risked Sprint-33 hand-off:** the profiled blow-up locus (`compute_constraint_jacobian`, the 369K `task` columns via `acost3` + the variable enumeration); the **working, well-scoped 2-D detector** (`_is_blowup_2d_condition_equation`, fires sarf-only — the "necessary" half, ready to reuse); and the confirmed requirement that the fix must eliminate the 369K `task`-column materialization everywhere + emit the symbolic parametric `stat_task` + `task.fx` (the "sufficient" half).
- **All three deep tracks have now REPLAN'd** (mine Solve Day 1, camcge Solve Day 5, sarf Translate Day 6) — every headline KPI mover REPLAN'd. **Solve 107 / Translate 135 / genuine floor 74 all hold at Day-0**; any Sprint-32 KPI gain now rests **entirely on P6** (cpack offset-alias / fawley second-index Case-b). Freed P2 budget (~14–20 h) + the mine/camcge freed budget → **P6 + P7** (Task 9 reallocation).

## 5. Evidence

The per-stage profiling (parse 11.3 s, `compute_constraint_jacobian` TIMEOUT > 120 s); the detector unit-fire check (`_is_blowup_2d_condition_equation` = True for tbal/equipb1/equipb2, and the corpus blast-radius sample = sarf-only); the re-profile with the gate active (`compute_constraint_jacobian` still TIMEOUT > 90 s). `git checkout src/ad/index_mapping.py` reverted the gate. Anchor `4cbf8bff`. See `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` §5–§6 + `docs/issues/ISSUE_1385_*.md` §"Phase 0".

---

**Document Created:** 2026-07-14
**Owner:** Sprint 32 execution (AD/emit specialist)
