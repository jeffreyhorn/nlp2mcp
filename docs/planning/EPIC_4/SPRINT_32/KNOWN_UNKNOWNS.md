# Sprint 32 Known Unknowns

**Created:** 2026-07-13
**Status:** Active — Pre-Sprint 32
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 32 (Sprint 31 carryforwards — mine head-offset 4th bound-complementarity site, sarf 4-D `task`-variable stationarity sparsification, camcge dual-consistent Walras / CASE_B `stat_mps`, rocket PATH-consultation forcing input, hhfair + CGE-cluster Case-c formalization) before implementation begins

---

## Executive Summary

This document identifies all assumptions and unknowns for the Sprint 32 implementation tracks **before** any `src/` change. It continues the Known-Unknowns methodology that has run since Epic 1 Sprint 4, sharpened by the Sprint 27 PR24 rule (prep records the *symptom + reproducer*; the fix surface is a Day-0-re-confirm hypothesis, never trusted from the prep doc) and the Sprint 28 PR27 rule (the KKT-residual harness Case-(a/b/c) verdict is the standard verification instrument).

Sprint 32 is **specification-bound, not diagnosis-bound** — every core carryforward inherits a Sprint-31 *precisely-pinned* root cause (mine's bound-complementarity localization; sarf's 369K finding; camcge's `stat_mps` CASE_B verdict; rocket's exhausted-lever survey; the CGE-cluster Case-c control), so Sprint 32 implements against a banked specification rather than re-diagnosing. But two structural Sprint-31 lessons dominate the unknowns: **(1)** the pinned root cause is still a hypothesis that must survive a **control experiment before any high-blast-radius `src/` change** — Sprint 31 *REPLAN'd all five* deep tracks after a control or harness re-diagnosis refuted the original design premise (the mine "MS-1 17500" measurement error; the camcge CASE_B-not-Walras verdict; the sarf 369K-not-1,152 finding; the P5 inert-reduction control; the rocket exhausted-lever survey). **(2)** **Always assert `modelstat` before reading an objective off a solve** — the Sprint-31 Day-2 measurement error (relaxing `x.up=inf` produced 34 unmatched-variable errors, so the "MS-1 17500" was the embedded LP, not the MCP). So the Sprint 32 unknowns are less "what is the bug?" and more "does the banked root cause still reproduce on today's tree, and does the *bound-multiplier derivation* (P1) / the *O(active) sparsification* (P2) / the *`stat_mps`-first ordering* (P3) behave as the pinned diagnosis assumes?"

**Sprint 32 Scope** (`docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32 (Weeks 29–30)"):
1. **mine 4th bound-complementarity site** (#1443) — Sprint 31 landed the head-offset IR foundation (`EquationDef.head_domain_offsets` + the Site-2 dual transfer, on `main`) but Day 3 found mine still `model_infeasible`: the LP bound-duals warm-started into `piU_x` don't satisfy the emitted `stat_x` at bound-active rows; the fix is a stationarity-consistent bound-multiplier derivation (+1 Solve)
2. **sarf 4-D `task`-variable sparsification** (#1385) — the 2-D constraint gate fires but sarf still times out on the **369,024-instance** 4-D `task(g,t,mn,mn)` `stat_task` enumeration; the fix is an O(active-instances) symbolic `stat_task` emit over the `$taskposs`-active subset (+Translate)
3. **camcge #1330 → dual-consistent Walras / CASE_B `stat_mps`** (Epic 5) — Sprint 31 re-diagnosed camcge as CASE_B (`stat_mps` rel 1.05, the `nu_mps_fx` fixing-multiplier defect); fix the `stat_mps` residual first, then the dual-consistent numéraire (price-pin omega 191.735) (potential +1 Solve)
4. **rocket #1462 — PATH-consultation forcing input** — Sprint 31 exhausted the division-by-variable reformulation (intrinsic non-convergence); package the concrete PATH-consultation question for the renumbered Sprint 33 (conditional +1 Solve / hand-off)
5. **hhfair + CGE-cluster Case-c formalization** (#1236) — Sprint 31 control-refuted the ν_objective reduction; formalize the objective-defining-intermediate-variable family as genuine non-convex Case-c (harness auto-classifier + ISSUE closure; no emit fix)
6. **Adjacent backlog + deferred cross-terms** — the #1111/#1112 offset-alias second-index-transpose generalization beyond polygon/ps2 + the residual `model_infeasible` cohort re-triage
7. **Infrastructure** — property-catalog extension (head-offset 4th-site + sarf 4-D shapes) + the PR25 genuine-floor tracking recompute against the S32–S35 re-baselined Match KPIs + the Epic-4-`SUMMARY` groundwork

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32" (Priorities 1–7 + Acceptance Criteria + Estimated Effort 80–120h + Risk HIGH); prep tasks: `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md`. (No separate `PRELIMINARY_PLAN.md` exists for Sprint 32 — the PROJECT_PLAN §"Sprint 32" entry + this PREP_PLAN are the planning source.)

**Lessons from Sprint 31** (`docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md`):
- §4 "Sprint-32 carryforwards" — the five tracks below carry a *precisely-pinned* Sprint-31 root cause (the SPRINT_LOG per-day entries + the per-track ISSUE docs), so Sprint 32 implements rather than re-diagnoses; but each pinned root cause is re-framed here as a Day-0 hypothesis (PR24).
- §3 lesson 1 — **all five deep tracks REPLAN'd after a control or harness re-diagnosis refuted the original premise** (the mine measurement error, the camcge CASE_B verdict, the sarf 369K finding, the P5 inert reduction, the rocket exhausted survey). → Every emit-touching Critical is gated on a control experiment (Task 8); every Category-5 unknown re-confirms the sign-flip BAN.
- §3 lesson 2 — **always assert `modelstat` before reading an objective** (the Day-2 mine measurement error). → Category 1's warm-start-experiment unknowns require the `modelstat` assertion as a verification precondition.
- §3 lesson 3 — **the genuine-floor ramp is carried by whichever track's fix genuinely changes the emit** (Sprint 30 retro §3, realized in Sprint 31: P2 alone carried +4). → The genuine floor (74 → ≥75) is treated as *conditional* on mine (P1) + camcge (P3) cold-matching, not as independent +1s (Task 9).
- §3 lesson 4 — **every Match number must carry its scope (142-corpus vs all-219)** (the Sprint-31 closeout finding: the +3 ps2/ps3 land on non-candidate `non_convex` models). → Category 6/7 unknowns + Task 2 record the corpus scope of every candidate gain.
- §3 lesson 5 — **each REPLAN produces a de-risked hand-off (a recipe, not an open question)** — Sprint 32 inherits specifications. → Task 9 pins the Sprint-33 REPLAN exit per deep track.

**Deferred unknowns carried from Sprint 31:** **24 of the 25** Sprint 31 prep unknowns were ✅ VERIFIED, with **no unknown returned WRONG** (`docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §"Next Steps"); the lone 🔍 INCOMPLETE, Unknown 4.2, was the in-sprint sarf O(constraints) empirical-timing gate — now superseded by the Sprint-31 Day-8 finding that the blow-up is the 369K 4-D `task` variable. Several Sprint-31 unknowns became the direct parents of Sprint-32 categories: **Sprint-31 Unknown 1.2** (the head-offset shared helper vs a 4th site — the 4th site surfaced) → the Sprint-32 mine bound-multiplier track (Category 1); **Sprint-31 Unknown 4.2** (sarf O(constraints) timing) → the 369K 4-D `task` finding → Category 2; **Sprint-31 Unknown 3.1/3.2** (camcge dual-consistent + detector — re-diagnosed CASE_B) → Category 3; **Sprint-31 Unknown 5.1/5.2** (obj-grad ν_objective reduction — control-refuted) → the Case-c formalization (Category 5); **Sprint-31 Unknown 6.1/6.3** (rocket lever exhaustion) → Category 4. The Sprint 32 unknowns are net-new, derived from the five carryforward priorities + the backlog + the infrastructure track.

---

## How to Use This Document

### Before Sprint 32 Day 1
1. Research and verify all **Critical** and **High** priority unknowns during prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases / run the `kkt_residual.py` trace + the cold-solve control experiment for validation (asserting `modelstat` before any objective read).
3. Document findings in each "Verification Results" section.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 32
1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly discovered unknowns (template below).
3. Update with implementation findings.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

### Priority Definitions
- **Critical:** Wrong assumption derails a priority or forces a mid-sprint REPLAN (>8 hours of churn / a lost target).
- **High:** Wrong assumption causes significant rework (4–8 hours) or a scope reduction.
- **Medium:** Wrong assumption causes minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 25

**By Priority:**
- Critical: 6 (the bound-multiplier reconciliation + the 5th-coupling risk + the O(active) sparsification + the `stat_mps`-first ordering + the dual-consistent Walras MS-1 + its false-positive detector)
- High: 10 (unknowns requiring upfront research before their priority's Day-0 re-confirm)
- Medium: 6 (resolvable during the relevant prep task)
- Low: 3 (nice-to-know / low impact)

**By Category:**
- Category 1 (mine #1443 — head-offset 4th bound-complementarity site): 4 unknowns
- Category 2 (sarf #1385 — 4-D `task`-variable stationarity sparsification): 4 unknowns
- Category 3 (camcge #1330 → dual-consistent Walras / CASE_B `stat_mps`): 4 unknowns
- Category 4 (rocket #1462 — PATH-consultation forcing input): 3 unknowns
- Category 5 (hhfair + CGE cluster #1236 — Case-c formalization): 4 unknowns
- Category 6 (adjacent backlog + deferred cross-terms): 3 unknowns
- Category 7 (infrastructure — property-catalog + genuine-floor tracking + checkpoint refresh): 3 unknowns

**Priority Distribution:** 24% Critical / 40% High / 24% Medium / 12% Low

**Estimated Research Time:** 28–36 hours (the per-unknown estimates below sum to ~36h, but many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping". The authoritative scheduling budget is the per-task total in `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md`: 36–51h across Tasks 1–11.)

---

## Table of Contents

1. [Category 1: mine #1443 — Head-Offset 4th Bound-Complementarity Site](#category-1-mine-1443--head-offset-4th-bound-complementarity-site)
2. [Category 2: sarf #1385 — 4-D `task`-Variable Stationarity Sparsification](#category-2-sarf-1385--4-d-task-variable-stationarity-sparsification)
3. [Category 3: camcge #1330 → Dual-Consistent Walras / CASE_B `stat_mps`](#category-3-camcge-1330--dual-consistent-walras--case_b-stat_mps)
4. [Category 4: rocket #1462 — PATH-Consultation Forcing Input](#category-4-rocket-1462--path-consultation-forcing-input)
5. [Category 5: hhfair + CGE Cluster #1236 — Case-c Formalization](#category-5-hhfair--cge-cluster-1236--case-c-formalization)
6. [Category 6: Adjacent Backlog + Deferred Cross-Terms](#category-6-adjacent-backlog--deferred-cross-terms)
7. [Category 7: Infrastructure — Property-Catalog + Genuine-Floor Tracking + Checkpoint Refresh](#category-7-infrastructure--property-catalog--genuine-floor-tracking--checkpoint-refresh)
8. [Template for New Unknowns](#template-for-new-unknowns)
9. [Next Steps](#next-steps)
10. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: mine #1443 — Head-Offset 4th Bound-Complementarity Site

## Unknown 1.1: Can the bound-active `stat_x` be reconciled with a stationarity-consistent bound-multiplier?

### Priority
**Critical** — this is the residual blocker Sprint 31 Day 3 REPLAN'd on, and mine's +1 Solve (one of the two firm Solve movers) hinges on it. If the emitted `stat_x` cannot be made to balance at bound-active rows via a stationarity-consistent bound-multiplier, mine stays `model_infeasible` and the +1 Solve / model_infeasible −1 do not land.

### Assumption
The bound-active `stat_x` residual is caused by warm-starting the LP reduced costs (`x.m`) into `piU_x`/`piL_x`, which are NOT the multipliers the head-offset-coupled `stat_x` needs; a **stationarity-consistent bound-multiplier derivation** (deriving `piU_x`/`piL_x` from the stationarity balance rather than the LP reduced cost) reconciles the residual and reaches MODEL STATUS 1, without a deeper IR change.

### Research Questions
1. For the bound-active `x` elements, what is the exact discrepancy between the LP reduced cost (`x.m`), the emitted `piU_x`/`piL_x`, and the head-offset-coupled `stat_x` residual (per-element table)?
2. Can the bound-multiplier be derived from the stationarity balance (a local per-row derivation), or does it require information the emit layer doesn't have at that site?
3. Which emit site(s) in `src/emit/`/`src/kkt/` own the `piU_x`/`piL_x` transfer, and is the change local?
4. Does the derivation reduce the warm-start `stat_x` residual to ≈ 0 (harness Case-a) before the cold solve is attempted?

### How to Verify
Run the KKT-residual harness on the current tree; tabulate the per-element bound-dual mismatch; prototype the stationarity-consistent derivation in a `/tmp` control (asserting `modelstat`):
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms 2>&1 | grep -iE "CASE_B|stat_x"
# Expect: CASE_B stat_x localizes to bound-active rows (dual-transfer consistent)
#         → the bound-multiplier derivation reduces the warm residual to ~0 → PROCEED
#         → residual persists / needs non-local info → 5th-coupling REPLAN (Unknown 1.2)
```

### Risk if Wrong
- **Non-local derivation:** the bound-multiplier needs information beyond the emit site → a deeper IR/emit change, the ~11h heaviest day overruns, mine REPLANs to a Sprint-33 head-offset-Phase-4.
- **Residual not fully reconciled:** the warm residual doesn't reach ~0 → the cold solve stays MS-5, +1 Solve does not land.

### Estimated Research Time
3 hours (Task 3 — the harness localization + the per-element bound-dual mismatch table + the stationarity-consistent derivation design)

### Owner
Development team (KKT/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (favorable — a single local presolve-transfer fix)
**Verified by:** Task 3 (mine 4th-Site Localization + Bound-Multiplier Design)
**Date:** 2026-07-13
**Findings:** The bound-active `stat_x` **can** be reconciled by construction. The harness reproduces the Day-3 fingerprint exactly (CASE_B, `stat_x(3,1,1)` rel 2.37 / raw −3.2e4, dual-transfer CONSISTENT, dual scale 1.35e4). The residual localizes entirely to `stat_x` rows with the duals CONSISTENT, so `lam_pr`/`pr.m` are correct and the mismatch is the **warm-start bound-multiplier transfer** at `src/emit/emit_gams.py:1548–1577`: it sets `piL_x/piU_x = ±x.m` (the LP reduced cost), but at mine's degenerate LP vertex `x.m ≠ N` (the non-bound part of `stat_x` = `−obj_grad + Σ_k[lam_pr(k,l,i-li,j-lj)$c − lam_pr(k,l-1,i,j)$c]`), so `stat_x = N − (±x.m) ≠ 0`. The fix: derive `piL_x = max(N,0)`, `piU_x = max(−N,0)` — which closes `stat_x = N − piL_x + piU_x = 0` exactly and respects the complementarity pairing.
**Evidence:** `docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md` §1–§3 (harness output + the emitted `stat_x` + the emit-site trace `src/emit/emit_gams.py:1548–1577`).
**Decision:** PROCEED to the in-sprint stationarity-consistent bound-multiplier derivation (presolve, local emit change), behind the Task-8 warm-residual→0 gate.

---

## Unknown 1.2: Is the residual a single 4th site, or does a 5th coupling surface?

### Priority
**Critical** — determines whether mine REPLANs again. Sprint 31 landed 3 sites (comp emission, Site-2 dual transfer, `stat_x` cross-term) and hit a 4th; if fixing the 4th surfaces a 5th coupling, mine slips to a deeper Sprint-33 head-offset architecture and the Solve ≥ 109 target loses one of its two firm movers.

### Assumption
The bound-active `stat_x` residual is a **single** 4th site (the bound-complementarity reconciliation), not the head of a chain — once the bound-multiplier is derived stationarity-consistently, mine reaches MS 1 with no further coupling surfacing.

### Research Questions
1. After the bound-multiplier derivation reduces the warm `stat_x` residual to ~0, does the cold LCP reach MS 1, or does a new residual (a 5th site) appear?
2. Is the bound-complementarity coupling orthogonal to the head-offset cross-term (independent), or do they interact (so fixing one perturbs the other)?
3. What is the cold-INFES-by-direction signature after the warm residual is reconciled — does it collapse cleanly?

### How to Verify
After the Unknown-1.1 warm reconciliation, attempt the cold solve (asserting `modelstat`) and re-run the harness:
```bash
# After the /tmp bound-multiplier prototype:
# Expect: cold MS 1 (single 4th site) → PROCEED; a fresh residual → 5th coupling → REPLAN
```

### Risk if Wrong
- **5th coupling surfaces:** mine REPLANs to a deeper Sprint-33 architecture; ~14–20h P1 budget partially reallocates to P6/P7 (Task 9); Solve ≥ 109 rests on camcge alone (a miss risk).

### Estimated Research Time
2 hours (Task 3 — the post-reconciliation cold solve + the 5th-coupling probe)

### Owner
Development team (KKT/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (design — the single decisive in-sprint gate is defined)
**Verified by:** Task 3 (mine 4th-Site Localization + Bound-Multiplier Design)
**Date:** 2026-07-13
**Findings:** The residual is localized to a **single** site — the `x.m` bound-multiplier transfer (the duals are CONSISTENT, so `lam_pr`/`pr.m`/complementarity are all correct; only `stat_x` fails to close, and only via the `piL_x/piU_x = ±x.m` warm-start). The in-sprint decisive test is the **warm-residual→0 gate**: after the `N`-derivation transfer, the harness must report Case-a (`stat_x` ≈ 0 at the NLP optimum). Because the `N`-split closes `stat_x` by construction, the only way a **5th coupling** surfaces is if (a) a fresh residual persists at the NLP optimum after the fix, or (b) the sign of `N` contradicts `x`'s bound-active status at some row (⇒ the emitted `stat_x` cross-term itself is still inconsistent) — both are explicit REPLAN triggers.
**Evidence:** `MINE_BOUND_MULTIPLIER_DESIGN.md` §3–§4 (the `N`-derivation + the warm→cold gate + the 5th-coupling exit).
**Decision:** PROCEED with the single-site fix + the warm-residual→0 gate; REPLAN to a Sprint-33 deeper head-offset architecture only if the warm residual does not close (budget → P6/P7 per Task 9).

---

## Unknown 1.3: Does the fix preserve the head-offset IR foundation + Site-2 dual transfer (zero regression)?

### Priority
**High** — the head-offset IR foundation (`EquationDef.head_domain_offsets`) + the Site-2 `head_offset_marginal_index_map` dual transfer landed on `main` in Sprint 31 and guard 5 head-offset models. The bound-multiplier change must not regress them.

### Assumption
The bound-multiplier derivation is a **local emit change** at the `piU_x`/`piL_x` transfer site that does not touch the head-offset IR field or the Site-2 dual transfer, so the 5 head-offset models (and their goldens) stay byte-stable.

### Research Questions
1. Which head-offset models are guarded by the Sprint-31 property fixtures, and are their cold/presolve goldens byte-stable under the bound-multiplier change?
2. Does the bound-multiplier site share code with the Site-2 dual transfer, or is it independent?
3. Does the `--resolve-changed` GO gate confirm no changed-golden regression across the 92 matches / 107 solves?

### How to Verify
Run the head-offset regression tests + the `--resolve-changed` checkpoint after the design's emit site is identified:
```bash
.venv/bin/python -m pytest tests/unit/ir/test_head_domain_offsets.py tests/integration/emit/test_head_offset_presolve_transfer.py -q
# Expect: green (foundation intact); the design names the emit site as independent of Site-2
```

### Risk if Wrong
- **Foundation regression:** the bound-multiplier change perturbs the head-offset field/Site-2 transfer → the 5 head-offset models regress; the golden-staleness gate must catch it before ship (a hidden-regression risk).

### Estimated Research Time
1.5 hours (Task 3 — the regression-guard scan + the emit-site independence check)

### Owner
Development team (IR/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (favorable — local, foundation-independent)
**Verified by:** Task 3 (mine 4th-Site Localization + Bound-Multiplier Design)
**Date:** 2026-07-13
**Findings:** The fix is confined to the presolve bound-multiplier **warm-start value** transfer (`src/emit/emit_gams.py:1548–1577`, "Transfer variable marginals to bound multipliers"), a block **independent** of the Site-2 `head_offset_marginal_index_map` constraint-dual transfer (`src/emit/emit_gams.py:1354/1545`) and of the `EquationDef.head_domain_offsets` IR field. The cold `mine_mcp.gms` and the `stat_x`/`comp_*` equation bodies are unchanged. The head-offset foundation regression guard passes on the current tree — **16 passed** (`tests/unit/ir/test_head_domain_offsets.py` + `tests/integration/emit/test_head_offset_presolve_transfer.py` + `tests/unit/emit/test_head_offset_marginal_map.py`). Caveat: the `x.m`→bound-multiplier transfer is a **generic** block, so the in-sprint implementation must gate the `N`-derivation to the head-offset-coupled case (or `--resolve-changed`-verify) to keep other presolve goldens byte-stable.
**Evidence:** `MINE_BOUND_MULTIPLIER_DESIGN.md` §3; the 16-test head-offset guard run; `src/emit/emit_gams.py` block trace.
**Decision:** PROCEED — favorable (local change, foundation provably preserved); the in-sprint change must be gated/`--resolve-changed`-verified for the non-mine presolve cohort.

---

## Unknown 1.4: Does the warm→cold gate assert `modelstat` at each step (the Day-2 lesson)?

### Priority
**Medium** — a methodology guard, not a correctness unknown, but it directly prevents repeating the Sprint-31 Day-2 measurement error (reading an objective off a model that never solved).

### Assumption
The mine warm→cold verification protocol asserts `mcp_model.modelstat` (== 1) **before** reading any objective, and never uses a structurally invalid experiment (e.g. `x.up=inf`, which produced 34 unmatched-variable errors and made the "17500" the embedded LP).

### Research Questions
1. Does the Task-3/Task-8 verification protocol explicitly assert `modelstat` before every objective read?
2. Are the invalid experiments (freeing non-`d` via `x.up=inf`) recorded as banned in the design?
3. Is the warm-residual → 0 → cold MS 1 sequence gated on `modelstat` at each step?

### How to Verify
Review the Task-3 design doc + the Task-8 P1 gate for the `modelstat`-assertion precondition; confirm the banned-experiment note is present.

### Risk if Wrong
- **Measurement error repeats:** a "solved" reading off an unsolved model mis-attributes the residual → wasted diagnosis (the Sprint-31 Day-2/3 churn).

### Estimated Research Time
0.5 hours (Task 3 — protocol review)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 3 (mine 4th-Site Localization + Bound-Multiplier Design)
**Date:** 2026-07-13
**Findings:** The warm→cold verification protocol asserts `mcp_model.modelstat` (== 1) **before** any objective read at each step (warm residual → 0 [harness Case-a] → presolve MS-1 → cold MS-1 stretch). The structurally invalid `x.up=inf` experiment is recorded **BANNED** — it produces 34 "Unmatched variable not free or fixed" errors (a variable paired with a vacuous conditioned `stat_x` MUST stay fixed for MCP matching), and the Sprint-31 Day-2 "MS-1 17500" was the embedded `$include` LP, not the MCP. The design's gate (§4) makes the `modelstat` assertion an explicit precondition of every solve step.
**Evidence:** `MINE_BOUND_MULTIPLIER_DESIGN.md` §4 (the protocol + the banned-experiment note); ISSUE_1443 Day-2 correction.
**Decision:** PROCEED — the protocol is defined and binding for the in-sprint P1 work.

---

# Category 2: sarf #1385 — 4-D `task`-Variable Stationarity Sparsification

## Unknown 2.1: Does the sparsified `stat_task` emit make sarf O(active-instances), not O(369K)?

### Priority
**Critical** — sarf's +1 Translate hinges on it. Sprint 31 Day 8 confirmed the 2-D constraint gate fires but sarf STILL times out because `stat_task` is enumerated over the full 369,024-instance Cartesian product of `task(g,t,mn,mn)`. If the symbolic emit can't sparsify to the `$taskposs`-active subset, sarf stays `translate_timeout`.

### Assumption
A symbolic `stat_task` emit that differentiates each short-circuited body **once parametrically** and restricts enumeration to the `$taskposs`-active entries makes sarf **O(active-instances)**, staying inside the translate budget — the 369K → active reduction is the load-bearing change (the 2-D constraint gate alone is necessary but insufficient).

### Research Questions
1. What is the `$taskposs`-active subset size vs the 369,024 Cartesian instances (the O(active) target)?
2. Can `stat_task` be emitted symbolically over the active subset (one differentiation, parametric in `(g,t,mn,mn)`), or does the enumeration path force per-instance expansion?
3. Which sites in `src/kkt/stationarity.py` + `src/ad/index_mapping.py` own the `task`-variable stationarity enumeration?
4. Does the sparsified emit keep `sarf_mcp.gms` inside the translate-time budget (no Option-1 timeout re-trigger)?

### How to Verify
Enumerate the active subset size; design the symbolic emit; time the translate:
```bash
# Enumerate task(g,t,mn,mn) Cartesian (16*24*31*31 = 369,024) vs $taskposs-active
# Design the sparsified stat_task emit; then time sarf translate against the budget
# Expect: O(active) emit stays in budget → PROCEED; still times out → re-scope REPLAN (Unknown 2.2/2.4)
```

### Risk if Wrong
- **Still O(369K):** the parametric emit re-triggers the Option-1 timeout → sarf stays `translate_timeout`, +1 Translate does not land, P2 REPLANs to Sprint 33.

### Estimated Research Time
3 hours (Task 4 — the active-subset sizing + the sparsified `stat_task` emit design + the translate-time probe)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (favorable — 927× reduction, O(1 symbolic equation) at translate time)
**Verified by:** Task 4 (sarf 4-D `task`-Variable Stationarity Sparsification Design)
**Date:** 2026-07-13
**Findings:** The sparsified emit makes sarf O(active), not O(369K). Emit **one symbolic guarded equation** `stat_task(g,t,m,n)$taskposs(g,t)..` (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` — translate-time cost is O(1 symbolic equation), not O(369,024). GAMS instantiates the guarded equation at runtime, collapsing to the 398 live rows (the fixed inactive columns' paired `stat_task` rows drop under MCP matching). Sites: `src/ad/index_mapping.py` (extend the short-circuit so the `task`-variable stationarity isn't materialized over the 369K Cartesian) + `src/kkt/stationarity.py` (the new symbolic parametric cross-term path — the short-circuited constraints enumerate zero per-instance Jacobian entries, so `stat_task` cross-terms are built by differentiating each body once, parametrically in `(g,t,m,n)`).
**Evidence:** `docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` §1–§3 (sizing probe + the emit design + sites).
**Decision:** PROCEED to the in-sprint parametric `stat_task` emit; the O(active) translate-budget gate (Task 8) is the decisive test.

---

## Unknown 2.2: Does the 4-D sparsification couple atomically with the 2-D constraint gate?

### Priority
**High** — ISSUE_1385's atomicity constraint: re-emitting the short-circuited constraints without the cross-terms yields an inconsistent MCP. The 2-D constraint gate (built + reverted S31) and the 4-D `task` sparsification must land together.

### Assumption
The re-landed 2-D constraint gate (`_is_blowup_2d_condition_equation` on `tbal`/`equipb1`/`equipb2`) and the 4-D `task` sparsification compose into a single atomic emit (re-emit + `J_gᵀ·lam` cross-terms together), producing a complete, internally-consistent MCP.

### Research Questions
1. Do the 2-D constraint gate and the 4-D `task` sparsification touch overlapping enumeration code, or are they independent short-circuits that must be coordinated?
2. Does the atomic emit produce a complete MCP (every short-circuited multiplier has its complementarity coupling), or does a partial land leave orphaned multipliers?
3. What is the minimal coupling point where both short-circuits + their cross-terms are assembled together?

### How to Verify
Design the coupled emit path; confirm the atomic re-emit + cross-terms assemble together (no partial-land path):
```bash
grep -n "_is_blowup_2d_condition_equation\|_is_blowup_dynamic_subset_equation" src/ad/index_mapping.py
# Expect: the design specifies a single atomic assembly point for both short-circuits + cross-terms
```

### Risk if Wrong
- **Non-atomic land:** a partial emit (constraints short-circuited but cross-terms dropped) produces the inconsistent MCP that failed in Sprint 26 → sarf translates but the MCP is wrong (no Solve/Match), a false +Translate.

### Estimated Research Time
2 hours (Task 4 — the atomic-coupling design)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (design — atomic single-assembly-point coupling)
**Verified by:** Task 4 (sarf 4-D `task`-Variable Stationarity Sparsification Design)
**Date:** 2026-07-13
**Findings:** The 2-D constraint gate and the 4-D `task` sparsification **must** land atomically. The re-landed 2-D gate (`_is_blowup_2d_condition_equation`, extending the 1-D `_is_blowup_dynamic_subset_equation` `len(eq_domain) != 1` bail to sarf's `taskposs(g,t)`/`equipposs(m,t)` shape on `tbal`/`equipb1`/`equipb2`) makes those constraints enumerate **zero** per-instance Jacobian entries, so their `J_gᵀ·lam` contributions to `stat_task` (and `stat_xcrop`, `stat_equipp`, …) cannot be assembled per-instance — they come from the §3 parametric cross-term path. Re-emit-without-cross-terms = an inconsistent MCP (ISSUE_1385 atomicity); there is no safe partial. The design assembles the guarded constraint re-emit + the parametric `stat_*` cross-terms + the `task.fx` fixing at a **single atomic point**.
**Evidence:** `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` §4; the 1-D gate at `src/ad/index_mapping.py:402` (2-D gate confirmed absent from main).
**Decision:** PROCEED — the atomic-coupling design is pinned; the re-emit + cross-terms + fixing land together.

---

## Unknown 2.3: Does the parametric `stat_task` avoid set-name-literal multiplier indices (the Sprint-26 anti-pattern)?

### Priority
**High** — the Sprint-26-Day-4 architecture failed precisely because it emitted set-name-literal multiplier indices (`nu_slack("srn")`, commit `243fe578`, reverted). The rebuild must use symbolic indices.

### Assumption
The parametric `stat_task` cross-term emit uses **symbolic** multiplier indices (e.g. `lam_tbal(g,t)`, parametric in the domain), never set-name-literal indices (`nu_slack("srn")`), so the emitted MCP is valid GAMS.

### Research Questions
1. Where did the Sprint-26 architecture emit the set-name-literal index, and what is the correct symbolic form for sarf's `stat_task`?
2. Does the banked `stat_task` hand-derivation (in ISSUE_1385) use symbolic indices throughout?
3. Does a compile check of a minimal sarf-shaped fixture confirm no set-name-literal indices in the emitted `stat_task`?

### How to Verify
Cross-check the banked derivation + the design against the `243fe578` anti-pattern; compile-check a minimal fixture:
```bash
# Expect: the design's stat_task uses symbolic lam_*(domain) indices; a compile check is clean (action=c, 0 errors)
```

### Risk if Wrong
- **Set-name-literal indices:** the emitted MCP fails to compile (the Sprint-26 failure mode) → sarf stays broken, the rebuild repeats the failed architecture.

### Estimated Research Time
1.5 hours (Task 4 — the anti-pattern cross-check against the banked derivation)

### Owner
Development team (AD/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (favorable — the banked derivation is already symbolic)
**Verified by:** Task 4 (sarf 4-D `task`-Variable Stationarity Sparsification Design)
**Date:** 2026-07-13
**Findings:** The parametric `stat_task` uses **symbolic** multiplier indices over the stat equation's own domain — `nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)` — with **no quoted-set-name indices** (the banked ISSUE_1385 derivation). The Sprint-26 anti-pattern (commit `243fe578`, reverted) emitted `nu_slack("srn")`/`lam_demand("srn")` where `srn` is a set name → UEL/domain errors + dropped cross-terms. The structural guard is a compile-clean scan of the emitted MCP: `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` must be empty. The parametric emit must build multiplier refs from the constraint's **declared domain symbols** (mapped to the stat variable's domain), never from a literal set name.
**Evidence:** `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` §5; the banked `stat_task` (ISSUE_1385); the `243fe578` `nu_slack("srn")` emit sample.
**Decision:** PROCEED — the banked spec is symbolic; the grep scan gates against the anti-pattern at implementation.

---

## Unknown 2.4: What is the `$taskposs`-active subset size (the O(active) target)?

### Priority
**High** — the O(active) budget target depends on the active-subset cardinality. If `$taskposs` is nearly dense (close to 369K), the sparsification buys little and sarf may still time out.

### Assumption
The `$taskposs`-active subset of `task(g,t,mn,mn)` is a small fraction of the 369,024 Cartesian instances (sparse enough that O(active) enumeration is tractable within the translate budget).

### Research Questions
1. How many `(g,t,mn,mn)` tuples satisfy `$taskposs` (the active cardinality)?
2. What fraction of the 369,024 Cartesian product is active?
3. Is the active enumeration tractable within the translate-time budget at that cardinality?

### How to Verify
Enumerate the `$taskposs`-active set from `sarf.gms`; compute the fraction:
```bash
# Parse sarf.gms $taskposs; count active (g,t,mn,mn); compare to 16*24*31*31 = 369,024
# Expect: active << 369K (sparse) → O(active) tractable; nearly dense → re-scope
```

### Risk if Wrong
- **`$taskposs` nearly dense:** O(active) ≈ O(369K) → the sparsification doesn't help, sarf stays `translate_timeout` → P2 REPLANs.

### Estimated Research Time
1.5 hours (Task 4 — the active-subset enumeration)

### Owner
Development team (AD specialist)

### Verification Results
✅ **Status:** VERIFIED (favorable — 398 active vs 369,024 Cartesian, a 927× reduction)
**Verified by:** Task 4 (sarf 4-D `task`-Variable Stationarity Sparsification Design)
**Date:** 2026-07-13
**Findings:** A GAMS data probe on `sarf.gms` gives the hard counts: `card(g)=16`, `card(t)=24`, `card(mn)=31` → Cartesian `task(g,t,mn,mn)` = 16·24·31·31 = **369,024**; `card(taskposs)` = 129 active `(g,t)`; `card(equipposs)` = 329; and the active `task(g,t,m,n)` subset (`taskposs(g,t)` ∧ `tech(g,m,n)`) = **398**. So the O(active) target is **398, a 927× reduction** — decisively tractable. `$taskposs` is far from dense (129 of 16·24 = 384 possible `(g,t)`, and only ~3 tech-active `(m,n)` per active `(g,t)`), so O(active) ≈ O(398), not O(369K).
**Evidence:** `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` §1 (the GAMS probe: 16/24/31/369,024/129/329/398).
**Decision:** PROCEED — the active subset is sparse enough that the sparsified emit is tractable within the translate budget.

---

# Category 3: camcge #1330 → Dual-Consistent Walras / CASE_B `stat_mps`

## Unknown 3.1: Does resolving the `stat_mps`/`nu_mps_fx` CASE_B residual first reach the correct stationarity balance?

### Priority
**Critical** — the Sprint-31 CASE_B verdict established the ordering: the `nu_mps_fx` fixing-multiplier defect must be resolved BEFORE the dual-consistent Walras numéraire (the Sprint-30 "check the dual side" lesson — layering Walras on an unresolved `stat_mps` residual mis-attributes the failure). If the `stat_mps` fix doesn't balance the stationarity, the whole P3 chain stalls.

### Assumption
The `stat_mps` residual (harness rel 1.05 / raw −210) is a **`nu_mps_fx` fixing-multiplier transfer/stationarity defect** (`mps` is a fixed variable), and emitting/transferring `nu_mps_fx` correctly balances `stat_mps` — a distinct, resolvable-first step before the Walras numéraire.

### Research Questions
1. What is the exact `stat_mps` stationarity (the gradient terms + the `nu_mps_fx` fixing multiplier), and why does the current transfer leave a −210 residual?
2. Is `nu_mps_fx` warm-started (does the `mps.fx` synthetic equation have an NLP marginal), or is it absent and needs a derived value?
3. Which emit site owns the fixing-multiplier transfer for fixed variables?
4. Does resolving `stat_mps` change the harness verdict (CASE_B → closer to Case-a) independent of the Walras step?

### How to Verify
Re-run the harness; localize `stat_mps`; design the `nu_mps_fx` fix; verify the residual drops:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camcge.gms 2>&1 | grep -iE "CASE_B|stat_mps"
# Expect: CASE_B stat_mps rel ~1.05 reproduced; the nu_mps_fx fix reduces the residual → PROCEED to Walras
```

### Risk if Wrong
- **`stat_mps` isn't the fixing-multiplier defect:** the CASE_B residual has a different cause → the Walras design targets the wrong layer, camcge stays MS-4, +1 Solve does not land.

### Estimated Research Time
2 hours (Task 5 — the `stat_mps` localization + the `nu_mps_fx` fix design)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
✅ **Status:** VERIFIED (empirically — a general emit fix, precisely localized)
**Verified by:** Task 5 (camcge `stat_mps` CASE_B + Dual-Consistent Walras Design)
**Date:** 2026-07-13
**Findings:** The harness re-confirms CASE_B `stat_mps` rel 1.05 / raw −210 (duals CONSISTENT). The emitted `stat_mps` is structurally correct; the defect is that **`nu_mps_fx` is never warm-started** — the `--nlp-presolve` "Transfer fixed-variable marginals to `_fx_` multipliers (#1462)" block emits transfers only for the two `$include`-fixed `l(i,lc)` elements (the #1449-widened case), with **no `nu_mps_fx.l = …` line** for the general `mps.fx=.09305` scalar fixing → `nu_mps_fx = 0` → `stat_mps = gradient = −210`. **Empirical confirmation:** the NLP marginal probe gives `mps.m = −209.861`, matching the −210 residual — so `nu_mps_fx` is derived from the fixed variable's reduced cost `mps.m` with the `stat_mps` sign: `nu_mps_fx.l = -mps.m` (= +209.861, cancels the −210 gradient). The fix (extend the #1462 block to transfer `nu_<var>_fx.l = ±<var>.m` — sign per the multiplier's stationarity role — for every scalar `var.fx` fixing) is a **general nlp2mcp emit-correctness fix** (not camcge-specific), landable in Sprint 32; it closes `stat_mps` (harness → Case-a).
**Evidence:** `docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §1–§2 (harness + the emitted #1462 block + the `mps.m = −209.861` probe).
**Decision:** PROCEED — step 1 is a general emit fix in `src/emit/emit_gams.py` (the #1462 transfer block); it resolves the CASE_B residual before the Walras step.

---

## Unknown 3.2: Does the dual-consistent Walras redefinition then reach MS 1 at omega 191.735?

### Priority
**Critical** — camcge's +1 Solve (the second firm Solve mover) hinges on the dual-consistent Walras numéraire reaching the correct allocation. Sprint 31 established the price-pin reaches omega 191.735 (MS-4); the dual-consistent redefinition is the unproven step to MS 1.

### Assumption
After the `stat_mps` fix, a **dual-consistent multiplier redefinition** (express the dropped market's dual via Walras' law so it stays available in the stationarity) reaches MODEL STATUS 1 at omega 191.735, where the naive drop-row gave omega 299 / MS-4.

### Research Questions
1. Which market-clearing multiplier is the numéraire's dual, and how is it expressed via Walras' law so it stays in the stationarity?
2. Does the `/tmp` prototype (with the `stat_mps` fix + the dual-consistent redefinition) reach MS 1 at omega 191.735 (asserting `modelstat`)?
3. Does the redefinition preserve every needed price/wage dual (no orphaned multiplier → the omega-299 corruption)?

### How to Verify
Prototype the `stat_mps` fix + the dual-consistent redefinition on `/tmp`; solve; confirm MS 1 + omega 191.735:
```bash
# /tmp: emit camcge MCP with the stat_mps fix + the dual-consistent numéraire; solve; assert modelstat==1
# Expect: MS 1 at omega 191.735 → PROCEED; MS-4 or omega drift → Epic-5-deferral REPLAN
```

### Risk if Wrong
- **Still MS-4 / omega drift:** the dual-consistent redefinition is deeper Epic-5 research → camcge REPLANs to the per-model-numéraire fallback; Solve ≥ 109 rests on mine alone (miss risk).

### Estimated Research Time
2 hours (Task 5 — the dual-consistent redefinition design + the `/tmp` prototype)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
✅ **Status:** VERIFIED (design; MS-1 is the in-sprint gate)
**Verified by:** Task 5 (camcge `stat_mps` CASE_B + Dual-Consistent Walras Design)
**Date:** 2026-07-13
**Findings:** The residual Walras singularity is **independent** of `stat_mps` (an inherent rank-deficiency: `equil(i)`+`lmequil(lc)` dependent via budget balance + no numéraire fixed → 1-D nullspace). The design keeps every market-clearing row (no orphaned dual — the Day-11 "check the dual side" lesson: dropping a row → omega 299 broken) + fixes the consumption-weighted numéraire (`sum(i$cles(i), cles(i)·p(i)) = sum(…, cles(i)·pd0(i))`) + redefines the redundant market's dual via Walras' law. The Day-11 price-pin reaches the correct **omega 191.735** but stays MS-4 **without** the `stat_mps` fix; the re-scoped hypothesis is `stat_mps`-first-then-numéraire. **MS-1 is unproven in prep** (the Day-6/7 numéraire variants stayed MS-4, but on an inconsistent warm point); the combined (step 1 + step 2) `/tmp`-to-MS-1 prototype is the Task-8 in-sprint gate.
**Evidence:** `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §3; `EPIC_5/CGE_DEGENERACY_SCOPING.md` §1/§3; the Day-11 price-pin (omega 191.735, MS-4).
**Decision:** PROCEED to the dual-consistent Walras as an Epic-5 step gated on step 1; the `/tmp`-to-MS-1 prototype is the gate, with an explicit Epic-5-deferral exit (per-model-numéraire fallback) if MS-4 persists.

---

## Unknown 3.3: Does the degeneracy detector flag ONLY camcge across irscge/lrgcge/moncge/stdcge?

### Priority
**Critical** — silently redefining a dual on a well-posed CGE would corrupt it (the "check the dual side" lesson). The detector must flag only the degenerate camcge, never a healthy CGE.

### Assumption
The degeneracy detector (S1∧S2∧S3 or equivalent — redundant market-clearing row + no numéraire) flags **only** camcge across the CGE cohort (irscge/lrgcge/moncge/stdcge all solve today), with a pass-through default for non-degenerate models.

### Research Questions
1. What are the discriminating conditions (S1∧S2∧S3) that separate camcge's Walras degeneracy from a well-posed CGE?
2. Does the detector return false for irscge/lrgcge/moncge/stdcge (all currently solve)?
3. Is the pass-through default safe (a non-flagged model gets the identity transform)?

### How to Verify
Design the detector; run it across the CGE cohort; confirm it flags only camcge:
```bash
# Run the detector across camcge + irscge/lrgcge/moncge/stdcge
# Expect: flags ONLY camcge; the other four pass through unchanged (byte-stable goldens)
```

### Risk if Wrong
- **False-positive on a well-posed CGE:** the detector redefines a dual on a healthy model → corrupts it (a silent regression the golden-staleness gate must catch); the cohort's matches break.

### Estimated Research Time
2 hours (Task 5 — the detector-scope design + the cohort false-positive check)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
✅ **Status:** VERIFIED (cohort precision confirmed — Day-7 banked)
**Verified by:** Task 5 (camcge `stat_mps` CASE_B + Dual-Consistent Walras Design)
**Date:** 2026-07-13
**Findings:** The detector flags **only** camcge. The S1∧S2∧S3 conditions: S1 (market-clearing block dependent via budget balance) ∧ S2 (no numéraire fixed) ∧ **S3 (cold MCP singular at iteration 0 = MS-4)** — S3 is the false-positive guard: a well-posed CGE with a determined closure passes S1∧S2 structurally but has a nonsingular Jacobian → fails S3 → pass-through. The Sprint-31 Day-7 cohort test (banked) confirms the cold MCP MODEL STATUS: **irscge / lrgcge / moncge / stdcge all MS-1 Optimal** (pass-through) vs **camcge MS-4** (flags). Pass-through default = the identity transform (faithful KKT emission); a per-model-numéraire declaration is the Epic-5 fallback for the flagged model.
**Evidence:** `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §4; the Sprint-31 Day-7 cohort-precision test (ISSUE_1330 Day-7 close); `EPIC_5/CGE_DEGENERACY_SCOPING.md` §2 (camcge is the sole inherent-Walras case).
**Decision:** PROCEED — the S3 guard makes the detector fire on only camcge; no risk of corrupting a well-posed CGE.

---

## Unknown 3.4: Is the numéraire selection a single automatic rule or a per-model fallback?

### Priority
**Medium** — determines whether camcge's fix is a general emit rule or a per-model-numéraire declaration fallback (the Epic-5-scoped alternative).

### Assumption
The redundant-row + numéraire selection can be a **single automatic rule** (Walras' law picks the dropped market + the numéraire), but a per-model-numéraire declaration fallback is available if the automatic rule proves camcge-specific.

### Research Questions
1. Can the numéraire be selected automatically (e.g. the consumption-weighted price ray), or does it require a per-model declaration?
2. Does the automatic rule generalize, or is it camcge-specific (→ the Epic-5 per-model fallback)?
3. What is the fallback's declaration surface (a per-model numéraire annotation)?

### How to Verify
Design both the automatic rule + the fallback; assess generality against the CGE cohort.

### Risk if Wrong
- **Automatic rule is camcge-specific:** the fix is a per-model fallback (Epic-5-scoped) rather than a general emit rule → still lands camcge but doesn't generalize (acceptable; documented in `CGE_DEGENERACY_SCOPING.md`).

### Estimated Research Time
1 hour (Task 5 — the rule-vs-fallback design)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
✅ **Status:** VERIFIED (favorable — automatic rule + per-model fallback, camcge is the sole case)
**Verified by:** Task 5 (camcge `stat_mps` CASE_B + Dual-Consistent Walras Design)
**Date:** 2026-07-13
**Findings:** For camcge the **consumption-weighted numéraire** (`sum(i$cles(i), cles(i)·p(i)) = sum(…, cles(i)·pd0(i))`) is the automatic rule — it reproduces the NLP optimum's `p=pd0` (a selection, not a perturbation). Whether it generalizes is `CGE_DEGENERACY_SCOPING.md` §5 Q1 (which row is redundant + which price is the numéraire is per-model, depending on the closure + SAM). Since **camcge is the sole inherent-Walras case in the corpus**, a **per-model-numéraire declaration** fallback is acceptable: the automatic consumption-weighted rule is the camcge instance, and the S1∧S2∧S3 detector (Unknown 3.3) ensures it applies nowhere else.
**Evidence:** `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §5; `EPIC_5/CGE_DEGENERACY_SCOPING.md` §2/§5.
**Decision:** PROCEED — automatic consumption-weighted numéraire for camcge; per-model-numéraire declaration as the Epic-5 fallback (safe because camcge is the sole detected case).

---

# Category 4: rocket #1462 — PATH-Consultation Forcing Input

## Unknown 4.1: Is the emit residual clean at the NLP point (Case-c) so rocket stays a forcing problem?

### Priority
**High** — the scope guard for the whole track. If the residual is NOT clean at the NLP point, rocket has a latent emit bug (Case-b) that must be fixed before any forcing/consultation, changing the track entirely.

### Assumption
The rocket emit residual is **clean at the NLP point** (the Case-c boundary signature per ISSUE_1462 — the `stat_ht(h0)`/`stat_step` boundary rows move with the warm-start value, a non-convex signature, not a cleanable emit bug), so rocket is a genuine forcing problem, not a latent emit bug.

### Research Questions
1. Does `kkt_residual.py` confirm the Case-c boundary signature at the NLP point (residual clean except the h0/h50 boundary rows that move with the warm-start)?
2. Is the boundary residual the non-convex Case-c signature (per ISSUE_1462) rather than a fixable Case-b?
3. Does the scope guard hold on the current tree (no emit regression since Sprint 31)?

### How to Verify
Re-run the harness on rocket; confirm the Case-c boundary signature:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms 2>&1 | grep -iE "CASE_|boundary|clean"
# Expect: residual clean at the NLP point (Case-c boundary) → forcing problem confirmed
```

### Risk if Wrong
- **Latent Case-b emit bug:** rocket has a fixable emit bug, not just non-convergence → the track becomes an emit fix (different scope), and the PATH-consultation packaging is premature.

### Estimated Research Time
1.5 hours (Task 6 — the Case-c scope-guard re-confirmation)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Do any remaining emittable levers cross the intrinsic non-convergence?

### Priority
**Medium** — Sprint 31 exhausted the known levers (PATH-option INFES 477→382; continuation/multistart MS-5; the division-by-variable reformulation), but the packaging may surface an untried scaled/relaxed continuation schedule.

### Assumption
No remaining emittable-GAMS lever crosses rocket's intrinsic non-convergence (the packaged PATH-consultation input is the deliverable, not a rocket solve), but a final sweep confirms no untried scaled/relaxed continuation schedule was missed.

### Research Questions
1. Are there scaled/relaxed continuation schedules not tried in Sprint 30/31 (the `--force` scaffold's parameter space)?
2. Does any untried lever reduce INFES below the Sprint-31 best (382), or does it plateau?
3. Is a Day-1 attempt warranted, or is the hand-off the deliverable?

### How to Verify
Sweep the remaining `--force` continuation parameter space; record whether any lever crosses:
```bash
# Sweep any untried scaled/relaxed continuation via --force; assert modelstat at each step
# Expect: no lever crosses (hand-off is the deliverable); a lever crosses → conditional +1 Solve
```

### Risk if Wrong
- **A lever crosses (unlikely):** rocket gets a conditional +1 Solve (a positive surprise), reallocating the packaging budget.
- **A lever is missed:** the PATH consultation is asked a question already answerable in-house (wasted consultation cycle).

### Estimated Research Time
1 hour (Task 6 — the remaining-lever sweep)

### Owner
Development team (solver specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Is the packaged PATH-consultation question concrete enough for the Sprint-33 hand-off?

### Priority
**Low** — a packaging-quality unknown; the question's content is banked (BACKLOG §3), only its final framing is open.

### Assumption
The packaged PATH-consultation question (the reformulation now a ruled-out candidate, sharpening the question toward the intrinsic discretized-optimal-control structure) is concrete enough that the Sprint-33 consultation can proceed without re-diagnosis.

### Research Questions
1. Does the question set include the ruled-out-lever survey (PATH-option 477→382; continuation/multistart MS-5; the reformulation) so the PATH authors don't re-suggest them?
2. Is the intrinsic-structure question specific (the `1/ht²`,`1/m²` Jacobian conditioning ruled out; the discretization structure the target)?
3. Does the `--force` scaffold + the finalized question form a self-contained hand-off?

### How to Verify
Review the packaged input against the Sprint-33 consultation needs; confirm the ruled-out survey + the concrete question are present.

### Risk if Wrong
- **Vague question:** the Sprint-33 consultation re-diagnoses instead of consulting → a wasted cycle (low impact — recoverable in Sprint 33).

### Estimated Research Time
0.5 hours (Task 6 — the hand-off review)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: hhfair + CGE Cluster #1236 — Case-c Formalization

## Unknown 5.1: Does the `kkt_residual.py` Case-c classifier flag the objective-defining-intermediate-variable family without false-positing Case-b?

### Priority
**High** — the P5 deliverable is a classifier extension. If it false-positives on genuine Case-b rows, it would wrongly suppress future fixable-emit-bug diagnoses.

### Assumption
The objective-defining-intermediate-variable shape (a variable appearing only in `obj =e= prod(x**a)` AND market-cleared, whose cold solve reaches a spurious local KKT point) is a **precise, detectable discriminator** that the harness can auto-flag as Case-c without false-positing genuine Case-b rows.

### Research Questions
1. What is the exact structural discriminator (variable appears only in the objective defining equation + is market-cleared + cold-diverges to a spurious KKT point)?
2. Does the discriminator distinguish hhfair `stat_u` / CGE `stat_xp` (Case-c) from a genuine Case-b emit residual?
3. Does a test across the corpus confirm no false-positive on a known Case-b model?

### How to Verify
Design the discriminator; test it across hhfair + the CGE cluster + a known Case-b model:
```bash
# Design the Case-c discriminator; run kkt_residual.py across hhfair/irscge/lrgcge/moncge + a Case-b control
# Expect: flags the family as Case-c; the Case-b control stays Case-b (no false-positive)
```

### Risk if Wrong
- **False-positive on Case-b:** the classifier suppresses a future fixable diagnosis → a real emit bug is mislabeled non-convex (a hidden lost gain).

### Estimated Research Time
2 hours (Task 7 — the discriminator design + the false-positive test)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Is the sign flip re-confirmed BANNED (control-refuted 4× across S30–S31)?

### Priority
**Medium** — a well-established ban (refuted 4×), but it must be recorded so no Day-1 sign-flip attempt is made.

### Assumption
The inlined objective-gradient **sign flip is BANNED** — control-refuted 4× across Sprint 30–31 (hhfair 72→22 worse; irscge/lrgcge/moncge inert) — and the Case-c formalization records this so no future sprint re-attempts it.

### Research Questions
1. Is the 4× control-refutation history recorded in ISSUE_1236 + the Case-c design?
2. Does the formalization explicitly ban the sign flip (not just "deferred")?
3. Is the ν_objective reduction also recorded inert (not merely the sign flip)?

### How to Verify
Review ISSUE_1236 + the Case-c design for the explicit sign-flip ban + the control-refutation history.

### Risk if Wrong
- **Ban not recorded:** a future sprint re-attempts the refuted sign flip → wasted churn (the exact anti-pattern the KU methodology prevents).

### Estimated Research Time
0.5 hours (Task 7 — the ban re-confirmation)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Are hhfair AND the CGE cluster all genuine Case-c, or is any fixable?

### Priority
**High** — if any of hhfair/irscge/lrgcge/moncge is actually fixable (Case-b), formalizing it as Case-c would forfeit a genuine-floor gain.

### Assumption
hhfair AND irscge/lrgcge/moncge are **all** genuine non-convex Case-c (the cold solve sits at a spurious local KKT point; the match is reachable only via the presolve warm-start) — none is a fixable Case-b emit bug.

### Research Questions
1. Does the cold solve of each (hhfair, irscge, lrgcge, moncge) sit at a spurious local KKT point (asserting `modelstat`), with the match only via presolve?
2. Is any member's residual actually a fixable Case-b (a lost gain if mislabeled)?
3. Does the Sprint-31 Day-10 control (the ν_objective reduction inert for all three; hhfair sign-flip refuted) still hold on the current tree?

### How to Verify
Re-run the Sprint-31 Day-10 control across the four models (asserting `modelstat`); confirm all Case-c:
```bash
# Cold-solve each; confirm spurious-KKT (cold != match) + presolve-match; re-confirm the reduction is inert
# Expect: all four genuine Case-c → formalize; any fixable → carve out as a genuine-floor candidate
```

### Risk if Wrong
- **A member is fixable:** formalizing it as Case-c forfeits a genuine-floor gain (a lost +1).

### Estimated Research Time
1.5 hours (Task 7 — the cold/presolve re-confirmation across the four models)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.4: What are the ISSUE-closure criteria for "documented Case-c"?

### Priority
**Low** — a documentation-completeness unknown; the closure criteria only affect the ISSUE lifecycle, not a metric.

### Assumption
"Documented Case-c" closure means: the harness auto-classifies the family, the sign flip is recorded BANNED, the models are handed to the Sprint-33 forcing/PATH work, and `ISSUE_1236` is closed as documented-non-convex (no emit fix).

### Research Questions
1. What criteria constitute a clean Case-c closure (classifier + ban + hand-off + ISSUE state)?
2. Does the hand-off to Sprint-33 forcing/PATH work capture hhfair + the CGE cluster?
3. Is the ISSUE closed as "documented-non-convex" vs "wontfix" (the correct disposition)?

### How to Verify
Define the closure checklist; confirm the hand-off + the ISSUE disposition.

### Risk if Wrong
- **Ambiguous closure:** the ISSUE lingers or is re-opened without new information → minor process friction (low impact).

### Estimated Research Time
0.5 hours (Task 7 — the closure-criteria definition)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: Adjacent Backlog + Deferred Cross-Terms

## Unknown 6.1: Does the #1111/#1112 second-index-transpose core generalize beyond polygon/ps2?

### Priority
**High** — the P6 "fill the budget + absorb REPLAN slack" track's main candidate. If the offset-alias general-alias core corrects other 2-index-transpose models' cold emits, it lands additional genuine-floor gains.

### Assumption
The Sprint-31 #1111/#1112 second-index-transpose core (the general-alias `_var_at_two_indices_complement` / `_build_complement_index_sum`) generalizes to **other 2-index-transpose models** in the corpus (a variable at two index-positions of a 2-index constraint), correcting their cold emits.

### Research Questions
1. Which corpus models have the var-at-two-indices 2-index-transpose shape (an audit)?
2. For each candidate, does the general-alias core change the cold emit (a real cross-term correction) vs no-op?
3. Do the candidates cold-match or presolve-match after the correction (genuine-floor vs methodology)?

### How to Verify
Audit the corpus for the 2-index-transpose shape; for each candidate, check whether the general-alias core corrects the cold emit:
```bash
# Audit for var-at-two-indices 2-index constraints; emit each candidate; diff cold golden
# Expect: ≥1 candidate corrected (genuine-floor gain) OR none (the core is polygon/ps2-specific)
```

### Risk if Wrong
- **No generalization:** the core is polygon/ps2-specific → P6 yields no offset-alias gain (acceptable; the failure-cohort re-triage (6.2) is the fallback P6 work).

### Estimated Research Time
2 hours (Task 10 — the corpus audit + the per-candidate cold-emit check)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Do any residual `model_infeasible` cohort members re-triage to a fixable Case-b?

### Priority
**Medium** — the P6 fallback work. agreste/cesam/fawley/lnts are non-Sprint-32-scoped `model_infeasible` members; the harness may re-triage one to a fixable Case-b.

### Assumption
Running the KKT-residual harness on the residual `model_infeasible` cohort (agreste, cesam, fawley, lnts) may re-triage one or more to a fixable Case-b (a candidate +1 Solve), or confirm them genuine Case-c (banked diagnoses for Sprint 33).

### Research Questions
1. What is the harness verdict for each of agreste/cesam/fawley/lnts (Case-a/b/c)?
2. Does any re-triage to a fixable Case-b emit bug (a candidate gain)?
3. For the Case-c members, what is the banked diagnosis for Sprint 33?

### How to Verify
Run the harness across the four cohort members; record the verdict + any fixable Case-b:
```bash
for m in agreste cesam fawley lnts; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "CASE_"; done
# Expect: verdicts recorded; any Case-b is a candidate; Case-c members get banked diagnoses
```

### Risk if Wrong
- **All Case-c:** no additional +Solve from the cohort (acceptable; the diagnoses still bank for Sprint 33).

### Estimated Research Time
1.5 hours (Task 10 — the cohort harness sweep)

### Owner
Development team (KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Does any P6 candidate pass the `--resolve-changed` GO gate without regressing the 92 matches / 107 solves?

### Priority
**High** — any P6 emit change must not regress the committed regression-guard sets (the 92 matches / 107 solves). The `--resolve-changed` checkpoint is the gate.

### Assumption
Any P6 candidate emit change (offset-alias generalization or a re-triaged Case-b fix) passes the `--resolve-changed --since-commit <Sprint-31-final-SHA>` GO gate — no changed golden moves backward across the 92 matches / 107 solves.

### Research Questions
1. Does each P6 candidate's changed-golden set stay within its target models (bounded blast radius)?
2. Does `--resolve-changed` report GO (no backward bucket move) for each candidate?
3. Is the golden-staleness gate + the presolve-divergence detector clean for each candidate?

### How to Verify
For each P6 candidate, run the checkpoint gate:
```bash
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit <Sprint-31-final-SHA>
# Expect: GO (no changed golden moves backward) for each candidate that lands
```

### Risk if Wrong
- **A candidate regresses:** a P6 change moves a committed golden backward → NO-GO, the candidate is reverted (the checkpoint working as intended; no net loss).

### Estimated Research Time
1 hour (Task 10 — the checkpoint-gate confirmation per candidate)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Infrastructure — Property-Catalog + Genuine-Floor Tracking + Checkpoint Refresh

## Unknown 7.1: Do the new head-offset-4th-site + sarf-4-D property fixtures guard P1/P2 once they land?

### Priority
**Medium** — the property-catalog extension guards the new emit paths; if the fixtures don't capture the P1/P2 shapes, a future regression goes uncaught.

### Assumption
The AD cross-term property catalog (`tests/integration/emit/test_ad_crossterm_shapes.py`) can be extended with a **head-offset 4th-site fixture** (guarding the mine bound-multiplier emit) and a **sarf 4-D `task` fixture** (guarding the sparsified `stat_task` emit), once P1/P2 land.

### Research Questions
1. What minimal fixtures capture the mine bound-multiplier + the sarf 4-D `task` shapes?
2. Do the fixtures fail before the fix + pass after (a genuine guard)?
3. Do they integrate into the existing `test_ad_crossterm_shapes.py` catalog?

### How to Verify
Design the fixtures; confirm they guard the P1/P2 shapes (fail-before/pass-after):
```bash
# Design the head-offset-4th-site + sarf-4-D fixtures; confirm they fail on the pre-fix emit, pass post-fix
```

### Risk if Wrong
- **Fixtures don't guard the shape:** a future regression to the mine/sarf emit goes uncaught (a latent-regression risk).

### Estimated Research Time
1 hour (Task 10 — the fixture design)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Does the PR25 genuine-floor tracking recompute against the S32–S35 re-baselined Match KPIs?

### Priority
**Low** — a tracking-recompute unknown; the ramp targets are set (footnote ⁸), only the recompute surface is open.

### Assumption
The PR25 genuine-floor tracking recomputes cleanly against the S32–S35 re-baselined Match KPIs (footnote ⁸ ramp: S31 74 → S32 ≥ 75 → S33 maintain ≥ 75 → S34 ≥ 77 → S35 ≥ 78), with the genuine floor 74 as the Day-0 anchor.

### Research Questions
1. Does the footnote-⁸ ramp align (S32 ≥ 75) with the mine + camcge genuine-floor conversion targets?
2. Does the genuine floor 74 reproduce as the Day-0 anchor (Task 2)?
3. Are the 142-corpus vs all-219 scopes correctly carried in the recompute?

### How to Verify
Recompute the genuine-floor tracking against the footnote-⁸ ramp; confirm the S32 ≥ 75 step + the Day-0 anchor.

### Risk if Wrong
- **Ramp misalignment:** the genuine-floor tracking targets the wrong step → a reporting inconsistency (low impact; corrected in the recompute).

### Estimated Research Time
0.5 hours (Task 10 — the tracking recompute; cross-checked in Task 2)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Sprint 31 → Sprint 32 Day-0 Baseline + Genuine-Floor Re-Baseline)
**Date:** 2026-07-13
**Findings:** The PR25 genuine-floor tracking recomputes cleanly. Day-0 = Sprint 31 final (no `src/`/`scripts/` drift since the S31 close `4cbf8bff`), so the committed DB is the Day-0 source and the canonical 142-candidate recompute reproduces the S31 headline exactly: **Parse 142 · Translate 135 · Solve 107** (63 `model_optimal` + 44 `model_optimal_presolve`) **· Match 92 · model_infeasible 7 · Tests 5,074**. The PR25 partition reproduces the **genuine floor 74** (methodology 21; all-219 Match 95 = 74 genuine + 21 methodology) from first principles: S30 70 + P2's +4 (polygon methodology→genuine + ps2_f_s/ps2_s/ps3_s_gic mismatch→genuine). The footnote-⁸ ramp aligns (S30 70 → S31 74 → **S32 ≥ 75** → S33 maintain ≥ 75 → S34 ≥ 77 → S35 ≥ 78), with genuine floor 74 as the S31 anchor. The **142-corpus vs all-219** distinction is recorded: headline Match 92 (over the 142 convex candidates) vs all-219 tally 95 (+3 non-candidate `non_convex` ps2/ps3); the genuine floor 74 spans candidates + non-candidates. The S32 conversion targets that would reach ≥ 75 are mine [P1] + camcge [P3] (both `model_infeasible` candidates → genuine cold match), conditional per the Sprint-30-retro §3 warning.
**Evidence:** `docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md` §1–§6 (DB recompute + the genuine-vs-methodology partition + the per-target bucket table + the checkpoint anchor).
**Decision:** Genuine-floor tracking recomputes correctly; the S32 ≥ 75 step is well-defined and conditional on mine + camcge cold-matching. Day-0 bucket aspect of Unknowns 1.1 / 2.1 / 3.1 recorded (their fix-surface aspect is verified by Tasks 3/4/5): mine `model_infeasible`, sarf translate-failure, camcge `model_infeasible`. The `--resolve-changed --since-commit 4cbf8bff` anchor selects **0 models at Day 0** (clean baseline; GO) — the checkpoint-coverage aspect (Unknown 7.3) is confirmed by Task 10.

---

## Unknown 7.3: Do the `--resolve-changed` checkpoint targets cover the newly-touched emit sites?

### Priority
**High** — the checkpoint re-solve is the sprint's regression gate; if it doesn't cover the newly-touched emit sites (the bound-multiplier site, the sarf `stat_task` site, the camcge `stat_mps`/Walras site), a regression could slip through.

### Assumption
The `--resolve-changed --since-commit <Sprint-31-final-SHA>` checkpoint selects every model whose emit golden changes under the Sprint-32 tracks (mine, sarf, camcge, plus any P6 candidate), so the Day-5/Day-10 checkpoints re-solve exactly the touched set.

### Research Questions
1. Does `--resolve-changed` select the mine / sarf / camcge goldens when their emit sites change?
2. Is the Sprint-31-final SHA the correct anchor (the DB changed at S31 Day 13)?
3. Does the checkpoint cover any P6-candidate goldens too?

### How to Verify
Confirm the checkpoint anchor + the changed-golden selection for the Sprint-32 emit sites:
```bash
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit <Sprint-31-final-SHA> --dry-run
# Expect: 0 at Day 0 (clean baseline); selects mine/sarf/camcge goldens once their emit changes
```

### Risk if Wrong
- **Uncovered emit site:** a changed golden isn't re-solved → a regression slips past the checkpoint (the exact gap the `--resolve-changed` gate exists to close).

### Estimated Research Time
1 hour (Task 10 — the checkpoint-coverage confirmation; anchor pinned in Task 2)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Template for New Unknowns

```markdown
## Unknown X.Y: [Title / Question]

### Priority
**[Critical/High/Medium/Low]** - [Brief reason]

### Assumption
[The assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, experiments, or analysis to validate the assumption]

### Risk if Wrong
[Impact on the sprint if the assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

> **🔵 PREP PHASE IN PROGRESS (Task 1 COMPLETE, 2026-07-13).** This Known Unknowns List is authored (**25 unknowns across 7 categories** aligned to the PROJECT_PLAN Sprint-32 priorities); every unknown starts 🔍 INCOMPLETE and is assigned to a downstream prep task (2–11) in §"Appendix: Task-to-Unknown Mapping". The six REPLAN-prone Criticals (1.1/1.2 mine bound-multiplier + 5th-coupling, 2.1 sarf O(active) sparsification, 3.1/3.2 camcge `stat_mps`-first + dual-consistent Walras, 3.3 detector false-positive) + the two dominant Sprint-31 lessons (control-experiment-first hypothesis; assert `modelstat` before an objective read) thread through the Category-1/3 unknowns. Prep Tasks 2–11 will move each unknown 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG with correction).

**Prep-phase checklist (before Sprint 32 Day 1 — Tasks 1–11):**
1. ✅ Task 1: this Known Unknowns List authored (25 unknowns, 7 categories).
2. 🔵 Research + verify all Critical + High priority unknowns via prep Tasks 2–10 (in progress).
3. 🔵 Run the `kkt_residual.py` traces + the cold-solve/read-only control experiments (asserting `modelstat`) (Tasks 3–7, 10).
4. 🔵 Update each "Verification Results" section (🔍 INCOMPLETE → ✅ VERIFIED / ❌ WRONG).
5. 🔵 Sprint 32 scope carries the PR16 REPLAN exits (Task 9) for the three deepest tracks (mine, sarf, camcge).
6. 🔵 Findings integrated into the sprint plan (Task 11 — `PLAN.md` + `prompts/PLAN_PROMPTS.md` + `SPRINT_LOG.md`).

**During Sprint 32:**
1. Reference this document daily (especially Critical / High unknowns).
2. Add newly discovered unknowns using the template above.
3. Update verification results as features are implemented.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 32 prep tasks verify which unknowns. Prep Task 11 (Plan Sprint 32 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Sprint 31 → 32 Day-0 Baseline + Genuine-Floor Re-Baseline | 7.2 | Reproduces the genuine floor 74 at Day 0 + the footnote-⁸ S32 ≥ 75 ramp alignment (7.2); records the 142-corpus vs all-219 scope; the per-target "still in its bucket at Day 0?" check contributes to 1.1 / 2.1 / 3.1 baselines; pins the Sprint-31-final SHA that anchors 7.3 |
| Task 3: mine 4th-Site Localization + Bound-Multiplier Design | 1.1, 1.2, 1.3, 1.4 | Localizes the 4th site + designs the stationarity-consistent bound-multiplier (1.1); the single-4th-site vs 5th-coupling sizing (1.2); the head-offset-foundation regression guard (1.3); the `modelstat`-assertion protocol (1.4) |
| Task 4: sarf 4-D `task` Sparsification Design | 2.1, 2.2, 2.3, 2.4 | Designs the O(active) `stat_task` sparsification (2.1); the 2-D-gate atomicity coupling (2.2); the set-name-literal anti-pattern guard (2.3); the `$taskposs`-active subset sizing (2.4) |
| Task 5: camcge `stat_mps` + Dual-Consistent Walras Design | 3.1, 3.2, 3.3, 3.4 | Designs the `nu_mps_fx` `stat_mps` fix first (3.1); the dual-consistent Walras redefinition to MS 1 / omega 191.735 (3.2); the degeneracy-detector false-positive scope (3.3); the automatic-rule-vs-per-model-fallback (3.4) |
| Task 6: rocket PATH-Consultation Input Packaging | 4.1, 4.2, 4.3 | Re-confirms the Case-c scope guard (4.1); sweeps the remaining emittable levers (4.2); packages the concrete PATH-consultation question for the Sprint-33 hand-off (4.3) |
| Task 7: hhfair + CGE Cluster Case-c Formalization + Classifier Design | 5.1, 5.2, 5.3, 5.4 | Designs the Case-c auto-classifier discriminator (5.1); re-confirms the sign-flip BAN (5.2); re-confirms all four members are genuine Case-c (5.3); defines the ISSUE-closure criteria (5.4) |
| Task 8: Refresh + Author Phase 0 Acceptance Gates | 1.1, 2.1, 3.1, 4.1, 5.1 | Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27): the mine bound-multiplier warm→cold gate (1.1), the sarf O(active) translate-budget gate (2.1), the camcge `stat_mps`-then-Walras `/tmp`-prototype gate (3.1), the rocket residual-clean-before-forcing gate (4.1), the hhfair control-before-implement gate (5.1, sign flip BANNED) |
| Task 9: Diagnosis-Heavy / REPLAN-Prone Risk Assessment (PR16) | 1.1, 1.2, 2.1, 3.1, 3.2 | The three deepest REPLAN-prone tracks — mine 4th-site bound-dual (1.1, 1.2), sarf 4-D sparsification timeout (2.1), camcge `stat_mps`-first + dual-consistent Walras (3.1, 3.2) — each get a PROCEED/REPLAN signal + a Sprint-33 exit + budget reallocation |
| Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface | 6.1, 6.2, 6.3, 7.1, 7.3 | The offset-alias generalization audit (6.1), the failure-cohort re-triage (6.2), the `--resolve-changed` GO gate per candidate (6.3), the property-catalog fixtures (7.1), and the checkpoint-coverage confirmation (7.3); cross-checks 7.2 with Task 2 |
| Task 11: Plan Sprint 32 Detailed Schedule | (integrates all) | Sprint 32 14-day schedule + day-by-day prompts; absorbs the PROCEED/REPLAN decisions from Tasks 8/9, the bound-multiplier design from Task 3, the sarf + camcge designs from Tasks 4/5, the rocket/hhfair packaging from Tasks 6/7, and the tooling/backlog analysis from Task 10; front-loads the Day-0 tractability probes (1.1, 3.1) |

**Cross-cutting unknowns** (verified across multiple prep tasks):

- **Unknown 1.1 / 1.2** (mine bound-multiplier + 5th coupling) — Task 3 designs the bound-multiplier + the 4th-site sizing, Task 8 gates the warm→cold fix-surface, and Task 9 makes the PROCEED/REPLAN call (mine solves vs a 5th-coupling Sprint-33 slip).
- **Unknown 2.1** (sarf O(active) sparsification) — Task 4 designs the sparsification, Task 8 gates the translate-budget, and Task 9 makes the timeout-re-trigger REPLAN call.
- **Unknown 3.1 / 3.2** (camcge `stat_mps`-first + dual-consistent Walras) — Task 5 designs both (ordered), Task 8 gates the `/tmp`-prototype-first rule, and Task 9 makes the Epic-5-deferral call.
- **Unknown 3.3** (detector false-positive) — Task 5 designs the detector scope; the false-positive guard protects the whole CGE cohort (irscge/lrgcge/moncge/stdcge).
- **Unknown 4.1** (rocket Case-c scope guard) — Task 6 re-confirms it before any forcing; Task 8 gates the residual-clean-before-forcing rule.
- **Unknown 5.1 / 5.3** (Case-c classifier + all-members-Case-c) — Task 7 designs the classifier + re-confirms the family; Task 8 gates the control-before-implement (sign flip BANNED).
- **Unknown 7.2 / 7.3** (genuine-floor tracking + checkpoint coverage) — Task 2 pins the anchor + the genuine floor 74, and Task 10 recomputes the tracking + confirms the checkpoint coverage.

**Coverage:** All 25 Sprint 32 prep-time unknowns are assigned to at least one prep task. Each Critical and High-priority unknown is assigned to the task that will act on its findings (e.g., Task 9 verifies the diagnosis-heavy Category-1/2/3 deep tracks AND its findings drive Task 11's schedule allocation + the Sprint-33 REPLAN exits).

**Carryforward from Sprint 31** (now informing Sprint 32 prep):
- **24 of the 25** Sprint 31 prep unknowns were ✅ VERIFIED, with **no unknown returned WRONG** (see `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §"Next Steps"); the lone 🔍 INCOMPLETE, Unknown 4.2, was the in-sprint sarf O(constraints) timing gate, superseded by the Day-8 369K finding. Several became the parents of Sprint-32 categories: Sprint-31 Unknown 1.2 (head-offset shared helper vs a 4th site — the 4th site surfaced → Category 1), Unknown 4.2 (sarf O(constraints) timing → the 369K 4-D `task` finding → Category 2), Unknown 3.1/3.2 (camcge dual-consistent + detector — re-diagnosed CASE_B → Category 3), Unknown 5.1/5.2 (obj-grad ν_objective reduction — control-refuted → Category 5 Case-c), Unknown 6.1/6.3 (rocket lever exhaustion → Category 4). The Sprint 32 unknowns are net-new, derived from the five carryforward priorities + the backlog + the infrastructure track.

---

**Document Created:** 2026-07-13
**Last Updated:** 2026-07-13
**Total Unknowns:** 25
**Owner:** Sprint 32 Planning Team
**Review Frequency:** Daily during Sprint 32
