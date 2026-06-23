# Sprint 29 Known Unknowns

**Created:** 2026-06-23
**Status:** Active — Pre-Sprint 29
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 29 (Sprint 28 carryforwards — presolve/warm-start robustness, cold-convex MCP convergence, AD cross-term cleanup) before implementation begins

---

## Overview

This document identifies all assumptions and unknowns for the Sprint 29 implementation tracks **before** any `src/` change. It continues the Known-Unknowns methodology that has run since Epic 1 Sprint 4, sharpened by the Sprint 27 PR24 rule (prep records the *symptom + reproducer*; the fix surface is a Day-0-trace hypothesis, never trusted from the prep doc) and the Sprint 28 PR27 rule (the KKT-residual harness Case-(a/b/c) verdict is the standard verification instrument).

**Sprint 29 Scope** (`docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 29 (Weeks 23–24)"):
1. **#1443 mine** — head-domain-offset MCP infeasibility (+1 Solve)
2. **#1462 rocket** — presolve `_fx_`-multiplier warm-start + non-convex convergence (+1 Solve / +1 Match)
3. **#1385** — translation-timeout Option-1 runtime-guard re-emit + `J_gᵀ·lam` cross-terms (+Translate)
4. **Cold-convex robustness** — the ~24 non-convex models that match only via the `--nlp-presolve` warm-start; partition Case-b (fixable cold-emit bug) from Case-c (inherent non-convexity)
5. **camcge → Epic 5 scoping** (#1330) — CGE Walras-law degeneracy hand-off (no `src/`)
6. **Objective-mismatch cohort** (#1332/#1247/#1239/#1236) — harness-classify + fix Case-b (+Match)
7. **Offset-alias gradient + dollar-condition AD** (#1146/#1143/#1112/#1111) — cross-term correction vs AD-engine redesign (+Match)
8. **Infrastructure** — checkpoint re-solve of the changed-golden set + post-methodology re-baseline

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 29" (Priorities 1–8 + Acceptance Criteria + Estimated Effort 96–134h + Risk HIGH + footnote ⁸ re-baseline note); prep tasks: `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md`.

**Lessons from Sprint 28** (`SPRINT_28/SPRINT_RETROSPECTIVE.md`):
- §"What We'd Do Differently" **#4** — *golden-stability does not catch a broken solve*: the rocket #1462 regression hid behind passing golden-staleness byte-checks until the Day-13 full retest. → Category 8 (checkpoint re-solve).
- §"What We'd Do Differently" **#5** — *re-baseline after a pipeline-methodology change*: the Match 62→92 jump was +24 methodology (the Day-9 presolve-retry-on-cold-mismatch broadening) vs only +7 genuine. → Unknown 8.2/8.3.
- §"What We'd Do Differently" **#1/#3** — PR24 traced-fix-surface + convexity-naive-tooling: every fix surface below is a Day-0 hypothesis, and the cold-convex cohort must be partitioned by convexity, not assumed.

**Deferred unknowns carried from Sprint 28:** all 29 Sprint 28 prep unknowns were resolved or converted to the Sprint 29 carryforwards (`SPRINT_28/SPRINT_RETROSPECTIVE.md` §"KU Coverage Summary"). The Sprint 29 unknowns are net-new, derived from the five carryforwards + the three backlog priorities; the cold-convex partition (Category 4) and the camcge Epic-5 boundary (Category 5) are the direct descendants of the Sprint-28 §"Sprint 29 Recommendations / Carryforwards" items.

---

## How to Use This Document

### Before Sprint 29 Day 1
1. Research and verify all **Critical** and **High** priority unknowns during prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases / run the `kkt_residual.py` trace for validation.
3. Document findings in each "Verification Results" section.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 29
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

**Total Unknowns:** 28

**By Priority:**
- Critical: 7 (the REPLAN-prone tracks + the cold-convex partition size + the re-baseline correctness)
- High: 11 (unknowns requiring upfront research before their priority's Day-0 trace)
- Medium: 6 (resolvable during the relevant prep task)
- Low: 4 (nice-to-know / low impact)

**By Category:**
- Category 1 (#1443 mine — head-domain-offset): 3 unknowns
- Category 2 (#1462 rocket — `_fx_` warm-start + non-convex): 4 unknowns
- Category 3 (#1385 — translation-timeout cross-terms): 3 unknowns
- Category 4 (cold-convex robustness): 4 unknowns
- Category 5 (camcge → Epic 5 scoping): 3 unknowns
- Category 6 (objective-mismatch cohort): 3 unknowns
- Category 7 (offset-alias gradient + dollar-condition AD): 4 unknowns
- Category 8 (infrastructure — checkpoint re-solve + re-baseline): 4 unknowns

**Estimated Research Time:** 28–36 hours (the per-unknown estimates below sum to ~34h, but many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping". The authoritative scheduling budget is the per-task total in `SPRINT_29/PREP_PLAN.md`: 35–48h across Tasks 1–10.)

---

## Table of Contents

1. [Category 1: #1443 mine — Head-Domain-Offset MCP Infeasibility](#category-1-1443-mine--head-domain-offset-mcp-infeasibility)
2. [Category 2: #1462 rocket — Presolve `_fx_`-Multiplier Warm-Start + Non-Convex Convergence](#category-2-1462-rocket--presolve-_fx_-multiplier-warm-start--non-convex-convergence)
3. [Category 3: #1385 — Translation-Timeout Option-1 Short-Circuit Cross-Terms](#category-3-1385--translation-timeout-option-1-short-circuit-cross-terms)
4. [Category 4: Cold-Convex Robustness — Non-Convex Models that Match Only Warm-Started](#category-4-cold-convex-robustness--non-convex-models-that-match-only-warm-started)
5. [Category 5: camcge → Epic 5 Scoping Observation (#1330)](#category-5-camcge--epic-5-scoping-observation-1330)
6. [Category 6: Objective-Mismatch Cohort — Harness-Classify + Fix Case-b](#category-6-objective-mismatch-cohort--harness-classify--fix-case-b)
7. [Category 7: Offset-Alias Gradient + Dollar-Condition AD Architecture](#category-7-offset-alias-gradient--dollar-condition-ad-architecture)
8. [Category 8: Infrastructure — Checkpoint Re-Solve + Post-Methodology Re-Baseline](#category-8-infrastructure--checkpoint-re-solve--post-methodology-re-baseline)
9. [Template for New Unknowns](#template-for-new-unknowns)
10. [Next Steps](#next-steps)
11. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: #1443 mine — Head-Domain-Offset MCP Infeasibility

## Unknown 1.1: Is mine's cold MS-5 a localizable head-offset dual-transfer (Case b) or a deeper cold-infeasible coupling (Case c)?

### Priority
**Critical** — decides PROCEED (+1 Solve, firm) vs Sprint-30 REPLAN for the entire Priority 1.

### Assumption
The corrected mine MCP cold-fails (MS 5, `x → 4e10` despite `x.up=1`, 49 INFES) primarily because the `pr(k,l+1,i,j)` head-domain-offset dual-transfer mis-aligns the multiplier (the presolve warm-start reads `pr.m` at the wrong lead index), i.e. a single localizable Case-b emit bug — not a distributed cold-infeasible complementarity/bound coupling (Case c).

### Research Questions
1. Does `kkt_residual.py data/gamslib/raw/mine.gms` localize a single dominant max-residual row, or is the residual spread across `comp_pr`/`comp_lo_x`/`comp_up_x`/`stat_x`?
2. Is the dominant row a `pr`/`stat_x` dual-transfer row (Case b) or a bound-complementarity row (Case c)?
3. Does the dual-transfer self-check report CONSISTENT (Case-b-localizable) or INCONSISTENT (deeper coupling)?
4. At the NLP KKT point, is the residual ~0 (emit correct, PATH non-convex/cold issue) or ≠0 (genuine emit bug)?
5. Is mine, a convex LP, expected to cold-solve at all (a unique KKT point), making any cold failure a genuine emit bug rather than non-convexity?

### How to Verify
Run the harness at the NLP KKT point and read the verdict + max-residual row:
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms
# Expect: CASE_B + a single dominant pr/stat_x row → PROCEED
#         CASE_C / distributed residual → Sprint-30 REPLAN (file the re-scoped diagnosis)
```
Cross-check the cold solve INFES rows against the localized row.

### Risk if Wrong
- **Case-c (distributed coupling):** Priority 1 yields no Solve in Sprint 29; budget re-allocates to cold-convex Case-b fixes (Task 5 reallocation plan). −1 Solve vs target.
- **Mis-localized surface (PR24):** implementing the head-offset fix when the real surface is elsewhere wastes the P1 budget — the Day-0 trace prevents this.

### Estimated Research Time
2.5 hours (Day-0 `kkt_residual.py` trace + cold-INFES cross-check + Case-b/c decision)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Is the `pr.m`-at-`l+1` dual-transfer the correct fix surface (vs the stationarity emit)?

### Priority
**High** — if the surface is the stationarity emit (not the presolve dual-transfer), the fix and its blast radius differ.

### Assumption
The fix surface is the presolve dual-transfer (`lam_pr.l = abs(pr.m(k,l,i,j))` should read `pr.m` at `l+1` for the head-domain-offset equation), in `src/emit/` (the presolve warm-start emit), not the cold `stat_x` stationarity emit.

### Research Questions
1. Does the `kkt_residual.py` dual-transfer self-check correctly handle the head-domain-offset multiplier, or does it itself mis-transfer (a tooling gap → Task 6)?
2. Is the head-offset multiplier alignment a presolve-only concern, or does the cold `stat_x` emit also carry a head-offset cross-term defect?
3. Which `src/emit/` or `src/kkt/` symbol owns the `pr.m`-at-`l+1` read?

### How to Verify
```bash
# Inspect the presolve golden's dual-transfer line for pr
grep -n "lam_pr\|pr.m" data/gamslib/mcp/mine_mcp_presolve.gms 2>/dev/null | head
# Compare the cold stat_x emit vs the hand-derived head-offset cross-term
grep -n "stat_x" data/gamslib/mcp/mine_mcp.gms | head
```
Confirm via the harness which row the residual lands on (presolve dual-transfer vs cold stationarity).

### Risk if Wrong
- Fixing the dual-transfer when the defect is in the cold stationarity emit (or vice versa) misses the bug; blast radius mis-estimated.

### Estimated Research Time
1.5 hours (presolve-golden inspection + harness row attribution)

### Owner
Development team (Emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: Does mine's convex-LP unique KKT mean a correct emit MUST cold-solve (no warm-start escape)?

### Priority
**Medium** — frames whether the `--nlp-presolve` warm-start is even an option for mine, or whether the cold MCP must solve.

### Assumption
mine is a convex LP (`solve … using lp`, `Positive Variable x`, `x.up=1`) with a unique KKT point, so — unlike the non-convex cold-convex cohort (Category 4) — a *correct* MCP must cold-solve; the warm-start cannot mask a genuine emit bug here.

### Research Questions
1. Is mine's NLP model type LP/convex (cross-check the source + the convexity DB)?
2. If the cold MCP is well-posed, does the warm-start presolve path even apply to mine, or is the head-offset fix necessarily a cold fix?
3. Does this distinguish mine from rocket (Category 2), where the warm-start is the fix vehicle?

### How to Verify
```bash
grep -iE "using (lp|nlp)|Positive Variable|\.up" data/gamslib/raw/mine.gms | head
.venv/bin/python -c "import json;d=json.load(open('data/gamslib/gamslib_status.json'));m=[x for x in (d['models'].values() if isinstance(d.get('models'),dict) else d['models']) if x['model_id']=='mine'][0];print(m.get('convexity'))"
```

### Risk if Wrong
- If mine is actually non-convex, the cold-solve expectation is wrong and Priority 1 joins the cold-convex robustness track instead.

### Estimated Research Time
1 hour (source + convexity-DB inspection)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: #1462 rocket — Presolve `_fx_`-Multiplier Warm-Start + Non-Convex Convergence

## Unknown 2.1: Is the general `nu_*_fx_h0` warm-start sufficient to recover rocket?

### Priority
**Critical** — the whole of Priority 2's +1 Solve / +1 Match hinges on whether the known warm-start fix suffices or whether a second fix is required.

### Assumption
Adding the general `_fx_`-multiplier warm-start (`nu_<var>_fx_<idx>.l = <var>.m(<idx>)`, mirroring the existing `piL_/piU_` warm-starts) is **necessary but not sufficient**: Sprint 28 Day-13 showed it moves the objective 1.137 → 1.016 (near NLP 1.0128) but the MCP stays MS 5 Locally Infeasible. The residual MS-5 needs a second fix (see Unknown 2.2).

### Research Questions
1. After injecting `nu_*_fx_h0.l = <var>.m('h0')`, does rocket's MCP reach MS 1/2 (sufficient) or stay MS 5 (insufficient)?
2. Is the residual gap (1.016 vs 1.0128) a convergence-tolerance issue or a structural one?
3. Does the warm-start generalize across the `_fx_`-bearing presolve models, or is rocket-specific tuning required?

### How to Verify
```bash
# Re-run the Sprint-28 Day-13 experiment: inject the nu_*_fx_h0 warm-start + solve
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms
# Confirm the documented 1.137 → 1.016, MS 5 persists baseline before any fix
```

### Risk if Wrong
- If the warm-start IS sufficient (Day-13 finding superseded), Priority 2 is a quick win and budget frees up. If it's insufficient AND the residual is intrinsic (Unknown 2.2 = Case c), Priority 2 partially REPLANs to Sprint 30 forcing strategies.

### Estimated Research Time
1.5 hours (re-confirm the Day-13 warm-start experiment + objective gap)

### Owner
Development team (Emit / presolve specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Is the residual MS-5 driven by the `piL/piU`-at-`h0` activation (Case b) or intrinsic non-convergence (Case c)?

### Priority
**Critical** — this is the REPLAN-prone question: a localizable bound-complementarity cause is Sprint-29-fixable; intrinsic non-convergence hands to Sprint 30.

### Assumption
After the `_fx_` warm-start, the residual MS-5 is caused by the `piL/piU` bound-complementarity activation at `h0` introduced by the #1449 Layer-4 unfix (which relaxes `v/ht/m('h0')` bounds, making `v('h0')=0` sit at the relaxed lower bound) — a localizable Case-b emit interaction, not intrinsic PATH non-convergence.

### Research Questions
1. Does the harness localize the residual to the `piL_v('h0')`/`comp_lo_v('h0')` rows (Case b) or report a distributed/converged-but-diverging signature (Case c)?
2. Does suppressing the Layer-4 unfix for elements whose fixed value equals the relaxed bound (the degenerate-bound case) clear the MS-5?
3. Is the `v('h0')=0`-at-lower-bound degeneracy the mechanism, as hypothesized in #1462?

### How to Verify
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms
# Probe: emit rocket presolve with the degenerate-bound Layer-4 unfix suppressed; solve; check MS
grep -n "Layer 4\|\.lo('h0')\|piL_v\|comp_lo_v" data/gamslib/mcp/rocket_mcp_presolve.gms | head
```

### Risk if Wrong
- **Case c (intrinsic):** Priority 2 lands only the warm-start (general presolve robustness, no rocket recovery) and REPLANs the rocket match to Sprint 30. −1 of the projected +1 Solve/+1 Match.

### Estimated Research Time
2.5 hours (harness localization + degenerate-bound suppression probe)

### Owner
Development team (Emit / presolve specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Does the general `_fx_`-multiplier warm-start regress any of the 13 Layer-4-unfix presolve models?

### Priority
**High** — a sprint-wide presolve-emit change must not regress the 13 models that currently use the #1449 Layer-4 unfix.

### Assumption
Adding `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` to the presolve emit is byte-stable and solve-stable for the 13 Layer-4-unfix models (catmix, chain, cclinpts, himmel16, irscge, maxmin, lrgcge, polygon, otpop, moncge, rocket, hhfair, stdcge) — it only adds a warm-start that the `_fx_` equation already pins.

### Research Questions
1. Which 13 presolve models carry the Layer-4 unfix block (the regression-test set)?
2. Does the new warm-start change their presolve goldens (byte-diff) or their solve buckets?
3. Are there `_fx_`-bearing models *outside* the Layer-4 set that also gain the warm-start (broader blast radius)?

### How to Verify
```bash
grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms
# After the fix: regen all presolve goldens + re-solve the 13; expect byte-stable + solve-stable
```

### Risk if Wrong
- A regression in any of the 13 is a net-negative; the change must gate to `_fx_` elements only and preserve the existing pin semantics.

### Estimated Research Time
1.5 hours (enumerate the 13 + design the byte/solve regression check)

### Owner
Development team (Emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Does `kkt_residual.py`'s dual-transfer correctly handle the presolve `_fx_` multipliers?

### Priority
**High** — if the harness mis-transfers the `_fx_` duals, every rocket verdict (Unknowns 2.1/2.2) is unreliable.

### Assumption
The Sprint-28 KKT-residual harness's dual-transfer self-check, validated on the carryforward equality/inequality multipliers, also correctly transfers the synthetic `_fx_` equation multipliers (`nu_<var>_fx_<idx>`) — no extension needed.

### Research Questions
1. Does the harness's dual-transfer self-check report CONSISTENT on rocket (a `_fx_`-bearing model)?
2. If it mis-transfers, is the fix a one-line index-mapping extension (Day-0 task) or a redesign?
3. Does the same concern apply to the head-domain-offset multipliers (mine, Unknown 1.2)?

### How to Verify
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms 2>&1 | grep -iE "dual|consistent|transfer"
```

### Risk if Wrong
- A mis-transfer undermines the Day-0 verdicts for Category 2 (and possibly Category 1); a minimal harness extension must land Day 0 before the gates.

### Estimated Research Time
1 hour (harness self-check on rocket + mine)

### Owner
Development team (Tooling)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: #1385 — Translation-Timeout Option-1 Short-Circuit Cross-Terms

## Unknown 3.1: Must the runtime-guard re-emit + `J_gᵀ·lam` cross-terms land atomically?

### Priority
**High** — if they can land separately, the work is decomposable; if atomic, a partial landing produces an inconsistent MCP.

### Assumption
The runtime-guard equation-body re-emit and the `J_gᵀ·lam` stationarity cross-terms must land together — a re-emit that adds the guarded equation body without the corresponding cross-terms yields an inconsistent MCP (stationarity that doesn't match the re-emitted constraints).

### Research Questions
1. Does the runtime-guard re-emit change the constraint set in a way that requires matching stationarity cross-terms in the same pass?
2. Is there a partial-landing that is still consistent (e.g., re-emit only, no new constraints)?
3. What is the minimal atomic unit?

### How to Verify
Hand-derive the re-emitted equation body + its `J_gᵀ·lam` cross-term for one srpchase-class target; confirm the MCP is inconsistent without the cross-term (a dimension/pairing mismatch).

### Risk if Wrong
- A non-atomic landing ships an inconsistent MCP that compiles but solves wrong; the atomicity constraint must be in the Phase-0 gate.

### Estimated Research Time
1.5 hours (hand-derivation + consistency check)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Which translation-timeout model is the smallest viable Phase-0 target?

### Priority
**Medium** — the Phase-0 hand-derivation needs a tractable target; picking a huge model wastes the gate budget.

### Assumption
Among the `translate_timeout` cohort Option-1 was meant to recover (#1228 iswnm, #1185 mexls, #932 nebrazil, sarf), one has a small-enough symbol set that the runtime-guard cross-terms are hand-derivable in the Phase-0 budget.

### Research Questions
1. Which of iswnm/mexls/nebrazil/sarf has the smallest equation/variable count?
2. Does any overlap the srpchase short-circuit shape already landed in Sprint 27 (a known structural template)?
3. Is a synthetic minimal fixture a better Phase-0 target than a real model?

### How to Verify
```bash
for m in iswnm mexls nebrazil sarf srpchase; do
  test -f data/gamslib/raw/$m.gms && wc -l data/gamslib/raw/$m.gms
done
```

### Risk if Wrong
- An intractable target stalls the Phase-0 gate; pick the smallest or a synthetic fixture.

### Estimated Research Time
1 hour (model-size survey)

### Owner
Development team (Sprint planning)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: What is the correct hand-derived `J_gᵀ·lam` cross-term shape for the runtime-guarded equation body?

### Priority
**High** — the cross-term shape is the core deliverable; an incorrect shape ships a wrong MCP.

### Assumption
The runtime-guarded equation body's stationarity contribution is the standard `J_gᵀ·lam` Jacobian-transpose times the constraint multiplier, restricted by the same runtime guard (`$`-condition) as the re-emitted equation.

### Research Questions
1. Does the runtime guard (`$`-condition) propagate identically to the cross-term, or does it shift index?
2. Is the cross-term separable per guarded instance, or does it sum over the guarded domain?
3. Does the Sprint-28 `test_ad_crossterm_shapes.py` catalog already cover this shape (a guarded-sum fixture)?

### How to Verify
Hand-derive against the Lagrangian for the Phase-0 target; cross-check against the existing guarded-sum property-test fixtures.

### Risk if Wrong
- A wrong cross-term shape ships a silently-wrong MCP; the harness residual at the NLP point is the guard.

### Estimated Research Time
1.5 hours (hand-derivation + property-test cross-check)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: Cold-Convex Robustness — Non-Convex Models that Match Only Warm-Started

## Unknown 4.1: What is the Case-b/Case-c partition size of the ~24 cold-convex cohort?

### Priority
**Critical** — the single largest Sprint 29 scope unknown: the Case-b count sizes Priority 4 (and frees budget if mostly Case-c).

### Assumption
A meaningful subset (≥ 2–4) of the ~24 warm-start-only models are Case-b (a genuine cold-emit bug the warm-start masks, like #1447 maxmin's missing `stat_mindist` cross-term), and the rest are Case-c (inherent non-convexity → cold infeasibility is correct → Sprint 30 forcing strategies).

### Research Questions
1. How many of the ~24 are convex models that *should* cold-solve (a convex-cold-fail = strong Case-b signal)?
2. Running `kkt_residual.py` on each, how many show a localizable Case-b residual at the NLP KKT point vs a Case-c converged-but-diverging signature?
3. What is the Sprint-29-fixable count, ranked by residual-localizability?
4. Does the partition free budget (mostly Case-c) that should pre-allocate to Priorities 6/7?

### How to Verify
```bash
# Enumerate the cohort from the Day-13 retest DB
.venv/bin/python - <<'PY'
import json; d=json.load(open("data/gamslib/gamslib_status.json"))
items=list(d["models"].values()) if isinstance(d.get("models"),dict) else d["models"]
coh=[m["model_id"] for m in items if (m.get("mcp_solve") or {}).get("outcome_category")=="model_optimal_presolve" and (m.get("solution_comparison") or {}).get("comparison_status")=="match"]
print(len(coh), sorted(coh))
PY
# Then run kkt_residual.py per model and tally Case-b vs Case-c (Task 3)
```

### Risk if Wrong
- **Over-estimated Case-b:** Priority 4 over-commits and under-delivers. **Under-estimated:** genuine +Match left on the table. Either way the schedule (Task 10) mis-allocates the 12–18h P4 budget.

### Estimated Research Time
2.5 hours (cohort enumeration + per-model harness survey — the bulk is Task 3)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Is #1447 maxmin's `stat_mindist` defect a shared Case-b shape across the cohort?

### Priority
**High** — if the maxmin shape recurs, one fix-class lands several cohort models.

### Assumption
#1447 maxmin's `stat_mindist` missing objective-variable cross-term (Case b, harness-localized in Sprint 28) is the *lead* Case-b target and may be a shared shape — an objective-variable cross-term omission — across multiple cohort members.

### Research Questions
1. Is maxmin's defect specifically "missing the objective-variable (`mindist`) cross-term in stationarity"?
2. Do other cohort members show the same missing-objective-variable-cross-term residual signature?
3. Is the fix a shared `src/kkt/stationarity.py` correction or per-model?

### How to Verify
```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/maxmin.gms 2>&1 | grep -iE "stat_mindist|case|residual"
# Compare the residual signature across the Task-3 Case-b list
```

### Risk if Wrong
- If maxmin is idiosyncratic, each cohort Case-b fix is separate work; the "≥2 Case-b fixes" deliverable needs more budget.

### Estimated Research Time
1.5 hours (maxmin harness trace + cross-cohort signature compare)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Is the DB `convexity.classification` reliable enough to seed the convex-cold-fail → Case-b heuristic?

### Priority
**High** — the partition (Unknown 4.1) leans on convexity; an unreliable classification mis-seeds it.

### Assumption
The `data/gamslib/gamslib_status.json` `convexity.classification` field (verified_convex / likely_convex / nonconvex) is reliable enough that a *verified_convex* model that cold-fails is a strong Case-b signal, even though `likely_convex` is heuristic.

### Research Questions
1. How many cohort members are `verified_convex` vs `likely_convex` vs `nonconvex`?
2. Do any `likely_convex` cohort members actually have multiple local optima (so cold-fail is expected non-convexity, not a bug)?
3. Should the harness Case-(a/b/c) verdict override the classification when they disagree?

### How to Verify
```bash
.venv/bin/python - <<'PY'
import json; d=json.load(open("data/gamslib/gamslib_status.json"))
items=list(d["models"].values()) if isinstance(d.get("models"),dict) else d["models"]
for m in items:
    c=(m.get("convexity") or {})
    if (m.get("mcp_solve") or {}).get("outcome_category")=="model_optimal_presolve":
        print(m["model_id"], c.get("classification"))
PY
```

### Risk if Wrong
- A wrong convexity seed mis-partitions; the harness verdict (not the DB classification) is the tie-breaker — confirm that ordering.

### Estimated Research Time
1 hour (classification audit across the cohort)

### Owner
Development team (Tooling)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: Does `check_presolve_divergence.py` soft-classify the cohort (no false hard-fails)?

### Priority
**Medium** — the cold-convex cohort is *expected* to diverge cold; the detector must classify that as soft `obj_gap`, not hard-fail, or it floods the checkpoints.

### Assumption
The Sprint-28 presolve-divergence detector's DB-reference + hard-fail-only-on-abort/infeasible logic correctly classifies the cold-convex cohort as soft `obj_gap` (expected non-convex local-optima differences), so the Day-5/Day-10 checkpoints aren't flooded with false hard-fails.

### Research Questions
1. Running the detector on the cohort, are they `obj_gap` (soft) or `diverged` (hard)?
2. Are any cohort members in the divergence allowlist (e.g., korcge #1439) that should be?
3. Does the detector's tolerance (1e-3) correctly absorb the cohort's display-precision noise?

### How to Verify
```bash
for m in maxmin catmix himmel16 polygon; do
  .venv/bin/python scripts/diagnostics/check_presolve_divergence.py --model "$m" 2>&1 | tail -1
done
```

### Risk if Wrong
- False hard-fails on the cohort block the checkpoint flow; the detector would need an allowlist extension or tolerance tweak.

### Estimated Research Time
1 hour (detector run on a cohort sample)

### Owner
Development team (Tooling)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: camcge → Epic 5 Scoping Observation (#1330)

## Unknown 5.1: Does the CGE cohort share camcge's Walras redundancy or have distinct degeneracies?

### Priority
**High** — determines whether the Epic-5 scoping doc covers one transformation or several.

### Assumption
The CGE cohort (#1354 camcge, #1355 cesam2, #1317/#1331/#1251 twocge) shares the camcge Walras-law degeneracy class (`equil(i)` goods + `lmequil(lc)` labor market-clearing linearly dependent given budget balance, no price numéraire), so a single named transformation (redundant-row drop + numéraire fix) scopes the whole cohort.

### Research Questions
1. Does each cohort model's cold MCP show the same singular-Jacobian / MS-4-at-iteration-0 signature?
2. Are the linearly-dependent rows the same (`equil`/`lmequil`) across the cohort, or model-specific (e.g., twocge's empty-trade-when-`r=rr` #1251, prolog's CES singular Jacobian #1070)?
3. Is there a single numéraire-selection rule, or per-model numéraire?

### How to Verify
For each cohort model, read the PATH basis-singularity report + the harness Case-C verdict; compare the linearly-dependent rows (paper analysis, no `src/`).

### Risk if Wrong
- If degeneracies are distinct, the Epic-5 scoping doc must enumerate several transformations, not one; scope larger.

### Estimated Research Time
1.5 hours (cohort degeneracy comparison)

### Owner
Development team (CGE / Epic-5 scoping)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Does the numéraire-fix + redundant-row-drop preserve the economic solution (paper)?

### Priority
**Medium** — the proposed transformation must preserve the economic solution to be a valid Epic-5 approach.

### Assumption
Dropping one redundant market-clearing row and fixing a price numéraire preserves the CGE economic solution (Walras' law makes one market-clearing equation redundant; fixing a numéraire removes the price-level indeterminacy) for at least one cohort model on paper.

### Research Questions
1. Which row is provably redundant by Walras' law for camcge?
2. Which price is the natural numéraire (preserving the documented NLP optimum)?
3. Does the transformation generalize, or is it per-model?

### How to Verify
Paper derivation against camcge's NLP optimum (191.7346) — show the dropped row + fixed numéraire reproduce it. No `src/`.

### Risk if Wrong
- A solution-altering transformation is not a valid Epic-5 hand-off; the scoping doc must flag this as an open question if unproven.

### Estimated Research Time
1 hour (paper derivation for one cohort model)

### Owner
Development team (CGE / Epic-5 scoping)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: What is the Epic 5 scope boundary (what stays in nlp2mcp vs CGE-domain)?

### Priority
**Low** — a framing question; mis-framing only affects the scoping doc's clarity.

### Assumption
The numéraire-fix + redundant-row-drop is a CGE-domain *structural transformation* that belongs in Epic 5 (a model-class-specific preprocessing step), not a general nlp2mcp emit change — so Sprint 29 spends no `src/` budget on camcge.

### Research Questions
1. Is there any *general* emit improvement (not CGE-specific) that would help the cohort, keeping a sliver in nlp2mcp?
2. Where does the nlp2mcp/Epic-5 boundary sit for CGE degeneracy?

### How to Verify
Document the boundary in the Epic-5 scoping doc with the rationale (Sprint 28 Day-11 Task-6 gate already established "no general emit fix exists").

### Risk if Wrong
- Minimal — a boundary mis-statement only needs a doc edit.

### Estimated Research Time
0.5 hours (boundary write-up)

### Owner
Development team (Epic-5 scoping)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: Objective-Mismatch Cohort — Harness-Classify + Fix Case-b

## Unknown 6.1: For each of #1332/#1247/#1239/#1236, is it Case-b (fixable) or Case-c (non-convex)?

### Priority
**Critical** — gates whether Priority 6 yields any Match; each Case-b is a +1 Match, each Case-c is a Sprint-30 hand-off.

### Assumption
At least 2 of the objective-mismatch cohort — #1332 quocge (25.683 vs 25.5085), #1247 prolog (−73.5 vs −0.0), #1239 sambal/qsambal (1028 vs 3.97), #1236 hhfair (54.9 vs 87.2) — are Case-b localizable emit bugs the harness can pin to a stationarity/complementarity row.

### Research Questions
1. What is each model's `kkt_residual.py` Case-(a/b/c) verdict at the NLP KKT point?
2. For the Case-b ones, what is the max-residual row (the fix surface hypothesis, PR24)?
3. Is the large-gap pair (sambal 1028 vs 3.97; prolog −73.5 vs −0.0) a Case-b sign/scale bug or a Case-c spurious local optimum?

### How to Verify
```bash
for m in quocge prolog sambal qsambal hhfair; do
  echo "== $m =="; .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "case|residual" | head -2
done
```

### Risk if Wrong
- If all four are Case-c, Priority 6 yields 0 Match and the budget should pre-allocate elsewhere (Task 5/Task 10).

### Estimated Research Time
2 hours (4–5 harness traces + Case verdicts)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Does any cohort member share a root cause with a cold-convex Case-b model or the offset-alias class?

### Priority
**Medium** — a shared root cause consolidates fixes (one fix → multiple models).

### Assumption
One or more of the objective-mismatch cohort shares a root cause with a cold-convex Case-b model (Category 4) or the offset-alias gradient class (Category 7) — e.g., sambal/qsambal is an alias-pair where the alias-AD defect recurs.

### Research Questions
1. Does any objective-mismatch model's residual signature match a cold-convex Case-b model's?
2. Is sambal/qsambal an alias-pair sharing the offset-alias gradient root cause?
3. Which fixes consolidate?

### How to Verify
Cross-reference the Task-3 (cold-convex) and Category-7 (offset-alias) residual signatures with the Category-6 verdicts; record the consolidation map.

### Risk if Wrong
- Missed consolidation = duplicated work; the consolidation map (Task 9) catches it.

### Estimated Research Time
1 hour (cross-signature comparison)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Is prolog's NLP reference (−0.0) a valid comparison target?

### Priority
**Low** — a data-validity question affecting only whether prolog is a meaningful Case-b target.

### Assumption
prolog's NLP reference objective (−0.0, vs MCP −73.5) is a genuine optimum, not a degenerate/zero-objective artifact or a recording error — so the mismatch is a real bug worth fixing.

### Research Questions
1. Is prolog's NLP −0.0 a true optimum or a near-zero/degenerate objective?
2. Does prolog's CES demand singular Jacobian (#1070) make it inherently Case-c (a CGE-cohort member, → Category 5)?

### How to Verify
```bash
.venv/bin/python -c "import json;d=json.load(open('data/gamslib/gamslib_status.json'));m=[x for x in (d['models'].values() if isinstance(d.get('models'),dict) else d['models']) if x['model_id']=='prolog'][0];print(m.get('convexity'),(m.get('solution_comparison') or {}))"
```

### Risk if Wrong
- If prolog is a CGE-degenerate (→ Category 5), it leaves Priority 6's count; minor re-allocation.

### Estimated Research Time
0.5 hours (reference-validity check)

### Owner
Development team (Sprint planning)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Offset-Alias Gradient + Dollar-Condition AD Architecture

## Unknown 7.1: Do #1146 himmel16 and #1143 polygon share the offset-alias gradient root cause?

### Priority
**High** — if shared, one fix lands two models (himmel16 43% + polygon 100% mismatch).

### Assumption
#1146 himmel16 (cyclic offset-alias gradient, 43% mismatch) and #1143 polygon (offset-alias gradient, 100% mismatch) share a single offset-alias gradient root cause in the AD engine, so one fix corrects both.

### Research Questions
1. Do both show the same offset-alias gradient residual signature in the harness?
2. Is the "cyclic" aspect of himmel16 a superset of polygon's, or a distinct sub-case?
3. Is the fix a single `src/ad/` correction or two?

### How to Verify
```bash
for m in himmel16 polygon; do
  echo "== $m =="; .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "case|residual|gradient" | head -2
done
```

### Risk if Wrong
- If distinct, two fixes are needed; the +1–2 Match deliverable holds but the budget doubles.

### Estimated Research Time
1.5 hours (two harness traces + signature compare)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Is the offset-alias fix a localized cross-term correction, or does it require the #1111/#1112 AD-engine redesign?

### Priority
**Critical** — the REPLAN-prone question: a localized correction is Sprint-29-fixable; an alias-aware-differentiation / dollar-condition-propagation redesign hands to Sprint 30.

### Assumption
The himmel16/polygon offset-alias gradient defect is a localized AD cross-term correction (property-test-guardable), NOT the deeper #1111 (alias-aware differentiation with summation-context tracking) / #1112 (dollar-condition propagation through the AD/stationarity pipeline) architectural redesign.

### Research Questions
1. Does the fix touch a single AD cross-term path, or the alias-aware-differentiation core (#1111)?
2. Does correcting himmel16/polygon require dollar-condition propagation (#1112), pulling in the architectural track?
3. What is the blast radius of the candidate fix across the AD cross-term property-test catalog?

### How to Verify
Prototype-then-revert a localized cross-term correction; if it fixes himmel16/polygon without touching the alias-aware core, it's localized (PROCEED); if it requires #1111/#1112, REPLAN to Sprint 30 (file the AD-engine track).

### Risk if Wrong
- **Architectural (Case c):** Priority 7 REPLANs to Sprint 30; −1–2 Match; budget re-allocates to the objective-mismatch cohort (Task 5 reallocation).

### Estimated Research Time
2 hours (localized-fix prototype-then-revert probe + blast-radius scan)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.3: Does the Sprint-28 property-test catalog cover the offset-alias shape, or is a new fixture needed?

### Priority
**Medium** — the P7 fix must be guarded by a property test; a missing fixture is a Day-0 gap.

### Assumption
The Sprint-28 `tests/integration/emit/test_ad_crossterm_shapes.py` catalog (shapes 1–6) does NOT yet cover the himmel16/polygon offset-alias gradient shape, so a new `shape7_offset_alias_*.gms` fixture is needed to guard the P7 fix.

### Research Questions
1. Do any of shapes 1–6 reproduce the offset-alias (cyclic) gradient shape?
2. What minimal synthetic model reproduces the himmel16/polygon defect?
3. Is one fixture sufficient, or are cyclic and acyclic offset-alias distinct fixtures?

### How to Verify
```bash
ls tests/fixtures/crossterm_shapes/
grep -l "offset.alias\|cyclic" tests/fixtures/crossterm_shapes/*.gms 2>/dev/null || echo "no offset-alias fixture yet"
```

### Risk if Wrong
- A fix without a property-test guard can silently regress later; the fixture plan (Task 9) closes this.

### Estimated Research Time
1 hour (catalog review + minimal-fixture sketch)

### Owner
Development team (Test infrastructure)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.4: What is the scope of #1112 dollar-condition propagation beyond himmel16/polygon?

### Priority
**Low** — a forward-scoping question; only matters if Priority 7 REPLANs to the architectural track.

### Assumption
#1112 (dollar-condition propagation through the AD/stationarity pipeline) and #1111 (alias-aware differentiation) are the architectural backstop behind several Sprint 24–28 cross-term defects; their full scope is an Epic-4-late / Epic-5 AD-engine track if the localized fix (Unknown 7.2) fails.

### Research Questions
1. How many open AD cross-term issues trace back to #1111/#1112?
2. Is the architectural redesign a Sprint-30 candidate or an Epic-5 item?

### How to Verify
Survey the open AD/KKT cross-term issues for #1111/#1112 dependencies; record in the REPLAN risk assessment (Task 5).

### Risk if Wrong
- Minimal — only affects the Sprint-30 / Epic-5 forward plan.

### Estimated Research Time
0.5 hours (issue-dependency survey)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 8: Infrastructure — Checkpoint Re-Solve + Post-Methodology Re-Baseline

## Unknown 8.1: What is the wall-clock cost of re-solving the changed-golden set at a checkpoint?

### Priority
**High** — the Day-5/Day-10 checkpoint re-solve must fit the checkpoint budget to be usable.

### Assumption
Re-solving only the models whose golden changed (the `changed_emit_artifacts.py` diff) at a checkpoint is fast enough (minutes, not hours) to run at Day 5 and Day 10 — because a typical emit-change PR touches a handful of goldens, not the full 142.

### Research Questions
1. How many goldens does a typical Sprint-29 emit-change PR touch (the at-risk-list size)?
2. What is the per-model re-solve wall-clock (including the slow models — ganges/clearlak)?
3. Does the re-solve fit inside the checkpoint budget, or must it be backgrounded?

### How to Verify
```bash
test -f scripts/sprint_audit/changed_emit_artifacts.py && echo "diff tool present"
# Estimate: a sample changed-golden set × the per-model solve time from the Day-13 retest
```

### Risk if Wrong
- If too slow, the re-solve must be scoped (changed-golden subset only) or backgrounded; the design (Task 8) handles this.

### Estimated Research Time
1.5 hours (at-risk-list sizing + per-model solve-time estimate)

### Owner
Development team (Tooling / sprint planning)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.2: How should the re-baseline step represent the genuine-vs-methodology split?

### Priority
**High** — the re-baseline is the codification of the Sprint-28 #5 lesson; an unclear representation defeats it.

### Assumption
The PR25 projection template can be extended with a re-baseline step that, after any pipeline-methodology change (retry-trigger or comparison-logic), recomputes the genuine (cross-term-fix) vs methodology (presolve-retry / comparison-broadening) Match split and records the new attributable baseline — so the headline delta stays attributable.

### Research Questions
1. What is the exact genuine vs methodology decomposition of the current Match 92 (≈68 genuine + ≈24 methodology)?
2. How should a future methodology change be flagged so the re-baseline runs?
3. What is the minimal template addition (a labeled table column + a trigger note)?

### How to Verify
Reproduce the Sprint-28 Day-13 partition (the +24 byte-identical-emit presolve-recovered matches vs the +7 genuine), and draft the PR25 template addition.

### Risk if Wrong
- A muddled re-baseline lets the next methodology change silently inflate the headline again (the exact Sprint-28 failure).

### Estimated Research Time
1.5 hours (decomposition reproduction + template draft)

### Owner
Development team (Sprint planning)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.3: Is Day-0 = Sprint 28 final (no fresh retest needed), and is the committed DB the correct baseline?

### Priority
**Critical** — if the committed DB is stale or `src/` changed since the Sprint-28 close, the entire Sprint-29 baseline (and every projection) is wrong.

### Assumption
The committed `gamslib_status.json` is the fresh Sprint-28 Day-13 retest (Solve 107, Match 92, model_infeasible 7), and `git diff <S28-close-SHA>..HEAD -- src/ scripts/` is empty, so Sprint 29 Day 0 = Sprint 28 final with no fresh ~4h retest required.

### Research Questions
1. Is `git diff <S28-close>..HEAD -- src/ scripts/` empty (no pipeline-affecting change since the close)?
2. Does the committed DB recompute to Solve 107 / Match 92 / model_infeasible 7 (the canonical scope)?
3. Are the `mcp_file_used` paths repo-relative (no machine-portability leak, #1400)?

### How to Verify
```bash
git diff --stat "$(git log --oneline --grep='Sprint 28' -1 --format=%H)"..HEAD -- src/ scripts/ | tail -1
grep -c "/Users/" data/gamslib/gamslib_status.json   # expect 0 (repo-relative paths)
```

### Risk if Wrong
- A stale DB or an intervening `src/` change forces a fresh retest before any baseline work (the exact Sprint-28 Day-13 discovery — the DB was stale then).

### Estimated Research Time
1.5 hours (git-diff confirmation + DB recompute + path-leak check)

### Owner
Development team (Sprint planning)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.4: Is the golden-staleness allowlist current?

### Priority
**Low** — a hygiene check; a stale allowlist only causes a flaky gate, not a wrong fix.

### Assumption
The golden-staleness allowlist (6 out-of-scope models + indus #1461 cross-platform non-determinism) and the presolve-divergence allowlist (korcge #1439) are still correct at Sprint 29 Day 0 — no new models need allowlisting or removing.

### Research Questions
1. Does the golden-staleness allowlist still contain exactly the 6 out-of-scope + indus?
2. Is korcge #1439 still the only presolve-divergence allowlist entry, and is #1439 still open?
3. Did any Sprint-28 fix make an allowlisted model in-scope again (allowlist removal)?

### How to Verify
```bash
cat scripts/sprint_audit/golden_staleness_allowlist.txt
cat scripts/diagnostics/presolve_divergence_allowlist.txt
```

### Risk if Wrong
- A stale allowlist causes a flaky golden-staleness / divergence gate; a one-line edit fixes it.

### Estimated Research Time
0.5 hours (allowlist review)

### Owner
Development team (Tooling)

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

**Before Sprint 29 Day 1:**
1. Review all Critical and High priority unknowns (18 total: 7 Critical + 11 High).
2. Execute verification tests for the top unknowns via prep Tasks 2–10 (see §"Appendix: Task-to-Unknown Mapping").
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG).
4. Adjust Sprint 29 scope (PROJECT_PLAN.md or PLAN.md) if major assumptions are wrong — specifically, any of Unknowns 1.1, 2.1, 2.2, 4.1, 6.1, 7.2, 8.3 returning WRONG triggers a Priority re-plan / REPLAN-to-Sprint-30 decision during prep (Task 5).
5. Share findings with the team during sprint planning (Task 10).

**During Sprint 29:**
1. Reference this document daily (especially Critical / High unknowns).
2. Add newly discovered unknowns using the template above.
3. Update verification results as features are implemented.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 29 prep tasks verify which unknowns. Prep Task 10 (Plan Sprint 29 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Bucket-Provenance Baseline + Re-Baseline Discipline | 8.2, 8.3 | Confirms Day-0 = Sprint 28 final + the committed-DB baseline (8.3); reproduces the genuine-vs-methodology Match split and drafts the re-baseline representation (8.2); the per-target "still in its bucket at Day 0?" check contributes to 1.1/2.1/4.1/6.1 |
| Task 3: Cold-Convex Cohort Survey + Case-(b/c) Partition | 4.1, 4.2, 4.3, 4.4 | The harness survey across the ~24 cohort produces the Case-b/Case-c partition (4.1), confirms #1447 maxmin as the lead shared Case-b shape (4.2), audits the convexity-classification seed (4.3), and confirms the divergence detector soft-classifies the cohort (4.4) |
| Task 4: Author Phase 0 Acceptance Gates (PR20 + PR24 + PR27) | 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2 | Each gate frames its fix-surface as a Day-0 hypothesis + cites the `kkt_residual.py` verification method: mine (1.1–1.3), rocket warm-start + residual + regression set (2.1–2.3), #1385 atomic/target/cross-term (3.1–3.3), the cold-convex lead (4.2), the objective-mismatch verdicts (6.1), and the offset-alias gates (7.1, 7.2) |
| Task 5: Diagnosis-Heavy / REPLAN-Prone Risk Assessment (PR16) | 1.1, 2.2, 7.2, 7.4 | The three REPLAN-prone Criticals — mine Case-b/c (1.1), rocket residual non-convergence (2.2), offset-alias localized-vs-architectural (7.2) — each get a PROCEED/REPLAN signal + Sprint-30 exit + budget reallocation; 7.4 scopes the architectural backstop |
| Task 6: Reusable-Tooling Readiness Audit | 1.2, 2.4, 4.4, 8.4 | Validates the harness dual-transfer on the head-domain-offset (1.2) and `_fx_` (2.4) multipliers, confirms the divergence detector won't false-hard-fail the cohort (4.4), and confirms the golden-staleness/divergence allowlists are current (8.4) |
| Task 7: camcge → Epic 5 Scoping Pre-Work | 5.1, 5.2, 5.3 | Surveys the CGE cohort's shared-vs-distinct degeneracies (5.1), the numéraire-fix solution-preservation argument (5.2), and the nlp2mcp/Epic-5 scope boundary (5.3) |
| Task 8: Checkpoint Re-Solve + Re-Baseline Tooling Design | 8.1, 8.2 | Sizes the changed-golden re-solve wall-clock budget (8.1) and specifies the re-baseline step as a PR25 template addition (8.2, with Task 2) |
| Task 9: Backlog Fix-Surface Analysis | 6.1, 6.2, 6.3, 7.1, 7.3, 7.4 | Per-model objective-mismatch verdicts + consolidation (6.1, 6.2), prolog reference validity (6.3), himmel16/polygon shared root cause (7.1), the offset-alias property-test fixture plan (7.3), and the #1112 propagation scope (7.4) |
| Task 10: Plan Sprint 29 Detailed Schedule | (integrates all) | Sprint 29 14-day schedule + day-by-day prompts; absorbs the PROCEED/REPLAN decisions from Tasks 4/5, the cold-convex partition from Task 3, and the infra designs from Tasks 6/8 |

**Cross-cutting unknowns** (verified across multiple prep tasks):

- **Unknown 1.1** (mine Case-b/c) — Task 4 authors the Phase-0 gate (hand-derived shape + traced surface), Task 5 makes the PROCEED/REPLAN decision from the harness verdict, and Task 2 confirms mine is still `model_infeasible` at Day 0.
- **Unknown 2.2** (rocket residual MS-5) — Task 4 gates the residual question, Task 5 makes the Case-b (fix) vs Case-c (Sprint-30) decision, Task 6 confirms the harness dual-transfer is reliable for the `_fx_` duals it depends on (2.4).
- **Unknown 4.1** (cold-convex partition size) — primarily Task 3 (the survey), feeding Task 4 (the Case-b gates) and Task 10 (the P4 budget allocation).
- **Unknown 7.2** (offset-alias localized-vs-architectural) — Task 4 gates it, Task 5 makes the REPLAN decision, Task 9 plans the property-test fixture that would guard a localized fix.
- **Unknown 8.2 / 8.3** (re-baseline + Day-0 baseline) — Task 2 establishes them, Task 8 designs the re-baseline tooling; together they keep the headline Match attributable after the Sprint-28 methodology lift.

**Coverage:** All 28 Sprint 29 prep-time unknowns are assigned to at least one prep task. Each Critical and High-priority unknown is assigned to the task that will act on its findings (e.g., Task 5 verifies the diagnosis-heavy Category 1/2/7 Criticals AND its findings drive Task 10's schedule allocation + the Sprint 30 REPLAN exits).

**Carryforward from Sprint 28** (now informing Sprint 29 prep):
- All 29 Sprint 28 prep unknowns were resolved (see `SPRINT_28/SPRINT_RETROSPECTIVE.md` §"KU Coverage Summary"). The Sprint 29 unknowns are net-new, derived from the §"Sprint 29 Recommendations / Carryforwards" (Categories 1–5) + the additional backlog priorities (Categories 6–7) + the two Day-13 process lessons (Category 8).

---

**Document Created:** 2026-06-23
**Last Updated:** 2026-06-23
**Total Unknowns:** 28
**Owner:** Sprint 29 Planning Team
**Review Frequency:** Daily during Sprint 29
