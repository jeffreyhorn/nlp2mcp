# Sprint 33 — Day 6: P2 sarf Phase-0 re-confirm + tractability assessment

**Date:** 2026-07-17 · **Day:** 6 · **Branch:** `planning/sprint33-day6-sarf-symbolic`
**Status:** WIP — Phase-0 re-confirm + a code-level tractability assessment. **A genuine decision point:** the sarf fix is a **from-scratch symbolic/parametric emit-mode subsystem** (the design's "high-risk, 4×-failed path"), a multi-day atomic effort for the **lowest-leverage bucket (+1 Translate)**, in an already-flat-KPI sprint. **No `src/` change** (atomicity forbids a partial; the decision to commit the multi-day build vs invoke the REPLAN exit is surfaced below).

---

## 1. Phase-0 re-confirm (live tree)

- **Blow-up reproduced:** `sarf` translate **TIMEOUT > 90s** (Day-0: >75s in `compute_constraint_jacobian`).
- **The 2-D constraint gate is absent** from `src/` (`grep -c _is_blowup_2d_condition_equation` = 0 — reverted, as the design states); the **1-D base gate** `_is_blowup_dynamic_subset_equation` is present (`src/ad/index_mapping.py:402`).
- **The 1-D gate's mechanism:** it returns `[]` for the gated equation (skips AD) **and drops the cross-terms** (srpchase translates but the MCP is incomplete → `path_solve_license`, does not solve). It gates **equation** enumeration, not **variable-column** enumeration.

## 2. Why sarf is not the 1-D shape — the blow-up is the `task` VARIABLE

`acost3.. cost("operating") =e= sum((g,t,m,n)$taskposs(g,t), oc(g,m,n)*task(g,t,m,n))` is a **scalar** equation (1 row), so the equation-gate never touches it. The timeout is **per-column differentiation of the `task` variable's 369,024 columns**:

- **S1** — `∂(acost3 body)/∂task(g,t,m,n)` materializes a Jacobian entry per `task` column (369K).
- **S2** — `enumerate_variable_instances(task)` (`index_mapping.py:369`) builds the full Cartesian cross-product **369,024**.
- **S3** — the variable stationarity builds `stat_task` per column.

The 1-D equation-gate cannot fix this (the Sprint-32 "necessary but insufficient" finding, re-confirmed).

## 3. Why there is no cheap gate — the active subset is not statically enumerable

The active `task` columns = `taskposs(g,t) ∧ tech(g,m,n)` = **398** (a 927× reduction). But **`taskposs` is runtime-computed from data** (`taskposs(g,t) = sum((c,s), yes$treq(g,t,c,s))`, `treq` from `atask`/`btask`), so nlp2mcp **cannot statically enumerate the 398** at translate time. Therefore the fix cannot be "enumerate only the 398 columns" — it must **stop enumerating `task`'s columns entirely** and emit a **symbolic guarded equation** (`stat_task(g,t,m,n)$taskposs(g,t)` + `task.fx(g,t,m,n)$(not (taskposs∧tech))=0`), letting **GAMS** instantiate the 398 live rows at runtime.

This is a **different emit MODE** (symbolic/parametric vs the current fully-enumerated per-column architecture) for the blow-up variable — the from-scratch subsystem the design describes, across all three sites, **atomic** (§4: a partial = an inconsistent MCP; the short-circuited constraints enumerate zero Jacobian entries, so every `stat_*` cross-term the constraints touch must come from the new parametric path).

## 4. Tractability verdict + the decision point

**Not refuted — but confirmed a major multi-day architectural effort.** Unlike P1 (H1 value-invariant) and P3 (H-b), sarf's fix is **not** refuted by the assessment; the design's spec is sound. But it is:
- a **from-scratch symbolic/parametric emit mode** for the `task` variable (S1 parametric `acost3` ∂, S2/S3 symbolic-not-enumerated) — no existing per-column-avoidance hook to extend;
- **atomic** (no safe partial — nothing ships until the full three-site change + the 7-term parametric `stat_task` + `task.fx` land together);
- the design's own **20–28 h, high-risk, "4×-failed Sprint-26 path"**;
- for the **lowest-leverage bucket** — **+1 Translate** (135→136), which "moves neither Solve nor Match".

**The decision (surfaced for the sprint owner):**
- **Option A — commit the multi-day build (Days 6–9):** attempt the atomic symbolic-emit subsystem. Realistic +1 Translate if it lands + passes the O(active) budget gate (translate seconds, no set-name literals, byte-stable, det ×3, `--resolve-changed` GO); real risk of the timeout-re-trigger / intractable-atomic-assembly REPLAN (the Sprint-26 failure mode).
- **Option B — invoke the design's REPLAN exit now:** given flat-KPI (P1 REPLAN'd, P3 H-b) + sarf being the lowest-leverage/highest-risk/highest-effort track, defer the symbolic-emit subsystem to a **focused Sprint-34 effort** (the de-risked hand-off: this assessment + the blow-up locus + the 1-D base gate + the 398-active sizing + the 7-term derivation + the atomicity spec), and **reallocate to P6** (agreste + the `path_syntax_error` cohort — the remaining **Solve**-bucket lever, higher EV).

**Recommendation:** given the sprint context, **Option B** is the higher-EV use of the remaining budget — pivot to P6, hand the sarf symbolic-emit subsystem to a focused Sprint-34 effort where the atomic multi-day rebuild gets the room + regression rigor it needs. Option A is defensible only if a firm +1 Translate is specifically wanted over the P6 Solve-bucket attempt.

## 5. KPI status (unchanged)

Checkpoint holds: Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7; src/goldens byte-unchanged since `ee51ed9e`. No `src/` change today.

---
**Document Created:** 2026-07-17 · **Owner:** Sprint 33 execution (Day 6) · WIP — awaiting the Option A / B decision.
