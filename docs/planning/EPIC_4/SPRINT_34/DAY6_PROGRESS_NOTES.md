# Sprint 34 — Day 6 Progress Notes (P2 sarf three-site symbolic emit — assessment → REPLAN)

**Date:** 2026-07-21
**Branch:** `planning/sprint34-day6-sarf-symbolic`
**Track:** P2 — sarf #1385 symbolic/parametric `stat_task` emit-mode
**Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P2 — the three-site O(active) symbolic re-emit, translate in seconds, atomic, `--resolve-changed` GO.
**Disposition:** 🔁 **REPLAN (scope/risk — the design is sound, not refuted). No `src/` shipped.** The atomic three-site symbolic emit is a from-scratch re-architecture of the foundational AD column-index flow (corpus-wide blast radius) for the lowest-leverage KPI (+1 Translate); it exceeds a safe in-session landing. Freed ~9–20 h → P6/P7.

---

## 1. Day-6 live re-confirm (the three sites + the missing gate)

Re-confirmed on `main` (`32f971c4`), consistent with the Day-0 probe (369,024 Cartesian / 398 active / translate `failure`):

| Site | Live locus (re-confirmed) | Status |
|---|---|---|
| **S1** `acost3` body-diff | `compute_constraint_jacobian` (`src/ad/constraint_jacobian.py:679`) differentiates the scalar `acost3.. =e= sum((g,t,m,n)$taskposs, oc·task)` per-column → 369K Jacobian entries | materializes |
| **S2** variable-column enumeration | `enumerate_variable_instances` (`src/ad/index_mapping.py:327`) — called from `build_index_mapping` (`constraint_jacobian.py:78`) **for every variable** — builds all 369,024 `task` columns | materializes |
| **S3** variable stationarity | `src/kkt/stationarity.py` materializes `stat_task(g,t,m,n)` per Cartesian column | materializes |
| 2-D constraint gate | `_is_blowup_2d_condition_equation` — **0 matches in `src/`** (reverted S32) | absent |
| variable-blowup gate | **none exists** — the only blow-up gate is `_is_blowup_dynamic_subset_equation` (`index_mapping.py:402`), which gates **equations** (srpchase's 1-D shape), not **variables** | absent |

## 2. Why this is a foundational re-architecture, not a gated add-on

`enumerate_variable_instances` is the **foundation** of the AD pipeline: `build_index_mapping` calls it for **every** variable (`constraint_jacobian.py:76-79`) to build the `col_to_var` column index that the **entire downstream flow** — the constraint Jacobian, the objective gradient (`gradient.py:287/453`), and the stationarity builder — iterates over. There is no notion of a "symbolic" (non-enumerated) variable anywhere in that flow.

Making `task` symbolic (S2) therefore cascades:
- The **column index** must represent `task` as a single guarded symbol (not 369K columns) — a new column-index concept.
- The **constraint Jacobian** (S1) must carry `task`'s contribution **parametrically** (`oc(g,m,n)·nu_acost3`) instead of per-column entries — a new parametric-derivative path.
- The **stationarity builder** (S3) must emit **one** guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the 7-term form) by differentiating each constraint body **once parametrically** — a **new cross-term path that does not exist today** (the current path assembles cross-terms from per-instance Jacobian entries, which the short-circuited constraints no longer produce).

All four must land **atomically** (design §5): the 2-D constraint gate makes `tbal`/`equipb1`/`equipb2` enumerate zero instances, so their `Jᵀ·λ` contributions to `stat_task` **cannot** come from per-instance entries — they must come from the (new) parametric path. **A partial landing = an inconsistent MCP** (multipliers with no stationarity coupling). And the 398 active columns are **not statically enumerable** (`taskposs(g,t)` is runtime-computed from data, `sarf.gms:371`), so the fix genuinely cannot be "enumerate only the 398" — it must stop enumerating `task`'s columns entirely and emit a symbolic guarded equation.

So the change is a **coordinated re-architecture of the foundational `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow**, all of which is exercised by **all 142 corpus models**. The blast radius is the entire AD core.

## 3. The REPLAN call (scope/risk — design sound)

- **Reward is the lowest-leverage KPI:** +1 Translate (135 → 136) — moves **neither Solve nor Match**. (Design + Task 9: "the lowest-leverage KPI.")
- **Risk is corpus-wide + Medium-High REPLAN prior (Task 9):** a from-scratch AD-core re-architecture (the 4×-failed Sprint-26 path), atomic (no safe partial), where a mis-step in the foundational column-index/parametric-derivative flow regresses the **135 byte-stable models**. Task 9 flagged the "a 4th enumeration site re-triggers the timeout" failure mode explicitly.
- **Not safely landable in-session:** a correct, atomic, gated symbolic emit mode — with a new parametric cross-term path and a new symbolic column-index concept — is a 20–28 h expert AD-architecture undertaking requiring a full-corpus regression harness. A rushed attempt on the foundational AD path is more likely to break the corpus than to cleanly land the timeout fix.
- **No incremental win:** the 2-D constraint gate alone is "necessary but insufficient" (design §5; S32-confirmed) — the 369K columns still materialize at S1/S2/S3, so re-landing just the gate does **not** fix the translate timeout. It is all-or-nothing.

**Disposition: REPLAN (scope/risk).** The design is **sound, not refuted** — the 7-term derivation (§4) is verified term-for-term, the three sites are pinned, the O(active) target is real. This is a **deliberate scope/risk deferral** (re-affirming S32 Day-6 "20–28 h high-risk atomic rebuild for the lowest-leverage bucket" + S33 Day-6 Option-B defer), now with the three sites + the foundational-re-architecture nature directly re-confirmed on the live tree — a de-risked hand-off (`SARF_EMIT_MODE_DESIGN.md` + this assessment) for a dedicated effort with a full-corpus regression harness. **No `src/` shipped** → no regression risk to the 135 byte-stable models; sarf holds at `translate_failure` (Translate 135). Freed ~9–20 h → **P6/P7**.

## 4. Sprint state

- **All three deep tracks have now REPLAN'd/deferred** (P1 mine Day 1 control-refuted · P3 fawley Day 5 risk/reward DEFER · P2 sarf Day 6 scope/risk REPLAN) + **P4 shipped a correctness fix with no +Solve** (Day 4). This is the **Task-9 modal-flat-KPI outcome, fully realized** — exactly as projected.
- **Days 7–9 (the P2 build continuation) are subsumed** by the Day-6 REPLAN → moot. Cumulative freed budget (P1 ~14–18 h + P3 ~6–12 h + P2 ~9–20 h ≈ **30–50 h**) → **P6** (the ganges/gangesx `$141/$145/$149` cohort — the designated best-remaining-shot) + **P7**.
- **KPI unmoved:** Parse 142 / Translate 135 / Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7.

---

**Verdict:** 🔁 **P2 sarf REPLAN (scope/risk, design sound).** The atomic three-site symbolic emit is a foundational AD-core re-architecture (the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow, corpus-wide) for the lowest-leverage KPI; not safely landable in-session. No `src/` shipped; Translate holds 135; ~9–20 h → P6/P7. **The modal-flat-KPI is realized; P6 is the sprint's remaining bucket hope.**
