# Sprint 38 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 38 (Weeks 41–42) begins
**Timeline:** Complete before Sprint 38 Day 1
**Goal:** Convert the Sprint 37 carryforwards into scoped, gated, schedulable work — with every figure re-derived rather than inherited

**Key insight from Sprint 37:** the sprint's three recurring defects were all *measurement* defects — verifying a component while asserting a system property, banked staleness, and documentation trusted as specification. This prep plan is written against that finding: **Task 2 re-derives the entire baseline rather than quoting it**, and every task's Verification section runs a command rather than citing a prior document.

---

## Executive Summary

Sprint 37 closed with the **genuine floor advancing 75 → 76** — the first advance since Sprint 33, ending four consecutive modal-flat closes. It landed two `src/` fixes (markov `σ=sp`, fawley constraint-index-diagonal), built four infrastructure gates, and re-pinned the corpus to GAMS 54.2.1. It also deferred two deep tracks with *measured* refutations rather than judgement calls, which is what makes Sprint 38 schedulable.

Sprint 38 (`../PROJECT_PLAN.md`, "Sprint 38 (Weeks 41–42)") has **eight priorities**:

1. **P1 (Critical):** ganges `$149` rebind-predicate re-scope — the cascade is VERIFIED working and blocked by one predicate
2. **P2 (Critical):** sarf O(active) atomic re-architecture — **the sprint's only KPI mover** (+1 Translate)
3. **P3 (Critical, Day 0):** the consultation ownership decision — **send it or strike it**
4. **P4 (High):** the 36 presolve goldens — close the 153-cold/17-presolve coverage asymmetry
5. **P5 (Medium):** camcge Epic-5 handoff + turkey licensed-testbed re-solve
6. **P6 (Infrastructure):** measurement integrity — the retrospective's three recurring defects
7. **P7 (Medium):** Phase-0 backfill over the open backlog
8. **P8 (Medium):** general emit-backlog sweep — the deliberate slack absorber

**The sprint is deliberately NOT floor-targeted**, and this prep plan must not quietly re-introduce a floor target. No carryforward can move the genuine floor: ganges is 0-bucket, sarf is +1 Translate, turkey is license-gated, camcge is Epic-5. The prep tasks below are scoped to that reality — the largest single prep investment (Tasks 4 and 5) goes to the two tracks that produce a *landing*, not a KPI.

This prep plan focuses on research, design, and survey tasks that must complete before Day 1 to prevent blocking issues, in the order that later tasks consume earlier tasks' output.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 38 Goal Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | ✅ Create Sprint 38 Known Unknowns List | Critical | 3-4 hours | None | Proactive unknown identification across all 8 priorities |
| 2 | ✅ Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints | Critical | 3-4 hours | Task 1 | Verify 108/94/76/135 and every banked fingerprint on current `main` |
| 3 | ✅ Measurement-Integrity Design: Gate Scope, Floor Provenance & Re-Anchoring (P6) | Critical | 4-5 hours | Tasks 1, 2 | P6 — and the measurement substrate every other task's gate asserts against |
| 4 | ✅ ganges P1 — `$149` Rebind-Predicate Design & Leak-Surface Analysis | Critical | 5-7 hours | Tasks 1, 2, 3 | P1 ganges/gangesx cascade |
| 5 | ✅ sarf P2 — O(active) Re-Architecture Design Refresh & Atomicity Plan | Critical | 5-7 hours | Tasks 1, 2 | P2 sarf — the only KPI mover |
| 6 | Presolve-Golden Adoption Plan & Runtime Impact (P4) | High | 3-4 hours | Tasks 1, 2, 3, 4 | P4 coverage asymmetry |
| 7 | Consultation Ownership Decision Package (P3) | High | 2-3 hours | Task 1 | P3 — the Day-0 send-or-strike decision |
| 8 | camcge Epic-5 Handoff Scoping + turkey Testbed Procurement (P5) | Medium | 3-4 hours | Tasks 1, 2 | P5 camcge (Epic 5) + turkey |
| 9 | Phase-0 Compliance Survey over the Open Backlog (P7) | Medium | 3-4 hours | Task 1 | P7 Phase-0 backfill |
| 10 | Emit-Backlog Candidate Catalog & Selection-Rule Dry Run (P8) | Medium | 3-4 hours | Tasks 1, 2, 9 | P8 slack absorber — with drift prevention |
| 11 | Plan Sprint 38 Detailed Schedule | Critical | 3-4 hours | All tasks (1–10) | Day-by-day schedule + REPLAN exits + budget |

**Total Estimated Time:** ~37-50 hours (~5-6 working days)

**Critical Path:** Tasks 1 → 2 → 3 → 4 → 6 → 11 (~21-28 hours)

The path runs through P6 rather than around it: Task 3 re-anchors the DB checkpoint and fixes the two known gate-narrowing modes, and **every subsequent task's acceptance gate is expressed in terms of those gates**. Task 4 (ganges) must precede Task 6 (presolve goldens) because P4 changes what `check-goldens` sweeps, and the plan schedules it *after* P1's gate run for exactly that reason — the prep ordering mirrors the sprint ordering.

**Note:** Task 1 (Known Unknowns) is ✅ **COMPLETE** as of 2026-08-17 — `SPRINT_38/KNOWN_UNKNOWNS.md`, **28 unknowns across 8 categories** (7 Critical / 11 High / 7 Medium / 3 Low; 33.5h research). It is the standing first prep task; it must exist before the design tasks (3–10) so each design is scoped against an explicit risk register. Task 9 (Phase-0 survey) precedes Task 10 (backlog catalog) because a backlog candidate without a Phase-0 section is **not implementable** under CONTRIBUTING §392–447 — the survey determines which candidates are even eligible.

---

## Task 1: Create Sprint 38 Known Unknowns List

**Status:** ✅ **COMPLETE** (2026-08-17)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Time Spent:** 3 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** n/a — this task *creates* all 28 unknowns; Tasks 2–10 verify them

### Objective

Create `docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md` cataloguing every assumption Sprint 38's eight priorities rest on, with a verification method and priority for each, so that risks surface in prep rather than mid-sprint.

### Why This Matters

The Known Unknowns process has run every sprint since Epic 1 Sprint 4 and is the mechanism by which this project has kept **zero broken code across S30–S37**. Sprint 37 resolved all 30 of its unknowns with zero INCOMPLETE, and the three that were *corrected empirically in prep* (no licensed testbed; camcge demo-reachable; robustlp's EXECERROR root cause) would each have cost mid-sprint days.

Sprint 38 carries an unusually high proportion of **inherited** assumptions — the ganges cascade and the sarf profile were both measured in Sprint 37 and are being consumed, not re-derived, by the plan. The retrospective's **banked staleness** finding says precisely that such figures go wrong when used. Every inherited figure is therefore an unknown until Task 2 re-derives it.

### Background

- `SPRINT_37/SPRINT_RETROSPECTIVE.md` §7 lists six recommendations, all of which became Sprint 38 priorities.
- `SPRINT_37/SPRINT_38_CARRYFORWARDS.md` §1 gives each carryforward a **bounded next step**; each bounded step embeds assumptions worth registering.
- `SPRINT_37/KNOWN_UNKNOWNS.md` is the format precedent (30 unknowns, 7 categories, all resolved).
- Two Sprint-37 findings are themselves standing unknowns for any sprint: the floor is **not** DB-derivable, and two gates have silent-narrowing modes.

### What Needs to Be Done

1. **Create the document skeleton** (~30 min)
   - `docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md`
   - Sections: How to Use, Priority Definitions, one category per sprint priority, Newly Discovered Unknowns, Confirmed Knowledge
2. **Enumerate unknowns per category** (~2 hours) — target 25–35 total
   - **Category 1 — ganges P1 (target ~6):** does the direction-2 predicate (restrict to a genuinely-free `prod` bound) actually exclude `prolog`? Does it preserve `rc=0` on both ganges and gangesx? Do dinam/indus/turkpow/clearlak's `$149` halves respond to the same narrowing? Is `ac(i+2,r)` reachable once the cascade lands? Does the lateral pse→mi move disturb any KPI gate that assumes mi is monotone non-increasing?
   - **Category 2 — sarf P2 (target ~6):** do the three materialization sites still sit at their recorded lines? Are all six corpus-safety call sites unperturbed by the S37 `stationarity.py` +311? Does the parametric `stat_task` reproduce the banked 7-term derivation? What is the *actual* post-re-arch emit time (the design predicts single-digit seconds; nothing has measured it)? Does sarf's new golden pass determinism ×3?
   - **Category 3 — consultation P3 (target ~3):** who is the recipient? What channel? What does the *strike* branch cost in projected upside (rocket +1, fawley +Solve)?
   - **Category 4 — presolve goldens P4 (target ~5):** are all 36 reproducible from a clean re-solve? Does each match its model's *expected* presolve emit? What does the leak sweep cost at 199 in-scope vs 163? Does `--min-scope` need 170 → 206?
   - **Category 5 — camcge/turkey P5 (target ~3):** is a licensed >1000-row GAMS-54 environment obtainable at all? Does the Epic-5 handoff need anything not already measured?
   - **Category 6 — measurement integrity P6 (target ~4):** what is the correct re-anchor commit? Does the floor provenance file reproduce 76 exactly? Do the two gate-scope assertions have false-positive modes?
   - **Category 7 — Phase-0 / backlog P7+P8 (target ~4):** how many open issues lack a Phase-0 section? How many backlog candidates have both a reproduced fingerprint and a named fix surface?
3. **Assign priority and verification method to each** (~1 hour)
   - Every unknown gets: assumption, priority (Critical/High/Medium/Low), verification method, owner task
   - Every **Critical** unknown must be verifiable by a prep task or Day 0 — nothing Critical may be left to mid-sprint
4. **Cross-link to the resolving prep task** (~30 min)
   - Each unknown names the task (2–10) that resolves it; any unknown with no resolving task is either promoted to a new task or explicitly deferred with a reason

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md` — **28 unknowns across 8 categories**, one category per sprint priority.
- **Added** the Task-to-Unknown mapping table (Appendix), assigning all 28 unknowns to the prep task that verifies each.
- **Updated** this `PREP_PLAN.md`: Tasks 2–10 each gained an `**Unknowns Verified:**` metadata line, a KNOWN_UNKNOWNS deliverable, and a matching acceptance criterion.

### Result

**28 unknowns**, all at 🔍 INCOMPLETE pending Tasks 2–10.

| metric | result | target |
|---|---|---|
| Total unknowns | **28** | 22–30 (aim 25+) ✓ |
| Critical | **7 (25%)** | ~25% ✓ |
| High | **11 (39%)** | ~40% ✓ |
| Medium | **7 (25%)** | ~25% ✓ |
| Low | **3 (11%)** | ~10% ✓ |
| Research time | **33.5h** | 28–36h ✓ |
| Categories | **8** | one per priority ✓ |

**By category:** Cat 1 ganges (5) · Cat 2 sarf (5) · Cat 3 consultation (3) · Cat 4 presolve goldens (4) · Cat 5 camcge/turkey (3) · Cat 6 measurement integrity (4) · Cat 7 Phase-0 (2) · Cat 8 backlog sweep (2).

**Two unknowns are not resolvable by an execution agent** and are marked as such: **3.1** (consultation recipient and channel — requires a human decision-maker; the strike branch executes by default if unanswered by Day 0) and **5.1** (testbed procurement — may require a purchasing decision).

**Every inherited Sprint-37 figure is registered as an unknown pending Task 2's re-derivation** — the ganges cascade counts (1.1), the sarf site locations (2.1), and the presolve-golden reproducibility (4.1) — per the retrospective's banked-staleness finding.

### Verification

```bash
# Document exists
test -f docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md && echo "✓ exists"

# Unknown count, excluding the "Unknown X.Y" template placeholder
grep -c "^## Unknown " docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md   # 29 incl. template
grep "^## Unknown " docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md | grep -vc "X.Y"  # EXPECT 28

# All 8 categories present (the document uses a single '#' for category headers)
grep -c "^# Category " docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md   # EXPECT 8

# Every unknown carries all 8 required sections
.venv/bin/python -c "
import re
t=open('docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md').read()
bs=[b for b in re.split(r'^## Unknown ', t, flags=re.M)[1:] if not b.startswith('X.Y')]
req=['### Priority','### Assumption','### Research Questions','### How to Verify',
     '### Risk if Wrong','### Estimated Research Time','### Owner','### Verification Results']
bad=[b.split(':')[0] for b in bs if any(r not in b for r in req)]
print('unknowns:', len(bs), '| incomplete:', bad or 'none')"

# Mapping table covers every unknown
.venv/bin/python -c "
import re
t=open('docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md').read()
allu={b.split(':')[0].strip() for b in re.split(r'^## Unknown ',t,flags=re.M)[1:] if not b.startswith('X.Y')}
mapped=set(re.findall(r'\b(\d\.\d)\b', t.split('## Appendix: Task-to-Unknown Mapping')[1]))
print('unmapped:', sorted(allu-mapped) or 'none')"

# Tasks 2-10 all carry Unknowns Verified metadata
grep -c "^\*\*Unknowns Verified:\*\*" docs/planning/EPIC_4/SPRINT_38/PREP_PLAN.md  # EXPECT 10 (Tasks 1-10)
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md` — **28 unknowns across 8 categories** (one per sprint priority)
- Each unknown: priority, assumption, 3–5 research questions, how to verify, risk if wrong, research time, owner, verification results
- The **Task-to-Unknown mapping table** (Appendix), covering all 28
- `PREP_PLAN.md` Tasks 2–10 updated with `**Unknowns Verified:**` metadata, deliverables, and acceptance criteria
- A count of Critical unknowns (7) with their resolution deadline (prep or Day 0)

### Acceptance Criteria

- [x] Document created with ≥25 unknowns across 8 categories (one per sprint priority) — **28 across 8**
- [x] All unknowns carry assumption, priority, verification method, and resolving task — verified programmatically, 0 incomplete
- [x] Every Critical unknown resolves in prep or on Day 0 — none deferred to mid-sprint (3.1 is Day 0 with a default branch)
- [x] Every inherited Sprint-37 figure (ganges cascade counts, sarf profile numbers, the 36 goldens) is registered as an unknown pending Task 2 — 1.1, 2.1, 4.1
- [x] Categories cover all 8 sprint priorities
- [x] Research time estimated and compared against the prep budget — **33.5h**, within the 28–36h target
- [x] Task-to-Unknown mapping table created; all 28 unknowns assigned
- [x] `PREP_PLAN.md` Tasks 2–10 updated with Unknowns Verified metadata

---

## Task 2: Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints

**Status:** ✅ **COMPLETE** (2026-08-17)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Time Spent:** 4 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Task 1 (Known Unknowns)
**Unknowns Verified:** 1.1, 2.1, 4.1

### Objective

Re-derive — not re-read — the Sprint-37 close baseline and every banked carryforward fingerprint on current `main`, so Sprint 38 starts from measured state rather than inherited documentation.

### Why This Matters

This task exists because of a specific Sprint-37 failure. The retrospective's §3 finding, **banked staleness**, was demonstrated three times: a prompt sweep re-staled within 24 hours by its own sprint's re-baseline; the S36-close partition written into the close doc as the *mid-sprint* state; and the refuted "+2 or 0" ganges figure carried into `SPRINT_LOG.md` §7 after Days 4–5 had already disproved it.

Sprint 38's plan consumes roughly a dozen inherited figures. **If any has drifted, a priority is mis-scoped before Day 1.** Sprint 37's own Day-0 also produced a *false positive* fingerprint match (a helper matching the `$141` pattern turned out to be from an unrelated cesam fix), so fingerprint checks must assert the specific mechanism, not just a pattern hit.

### Background

Baseline as recorded at Sprint 37 close (`main` `8cffec29`; plan insert at `d9bc9c34`):

| quantity | recorded |
|---|---|
| Solve / Match / genuine floor | 108 / 94 (65 cold + 29 presolve) / **76** |
| Translate · Parse · mi · pse · all-219 | 135 · 142 · 7 · 6 · 97 |
| solver | GAMS **54.2.1** |
| goldens | 170 discovered, 7 allowlisted, **163 in-scope**, 17 presolve |
| leak gate | `--min-scope 170`, 3 workers |
| DB anchor | `78ceaead` (S34 close — **four sprints stale**, P6d re-anchors it) |

### What Needs to Be Done

1. **Re-derive the KPI block from the DB** (~45 min)
   - Recompute Solve / Match / cold-vs-presolve split / Translate / mi / pse / all-219 directly from `data/gamslib/gamslib_status.json`
   - Use `model_id` as the key (**not** `model_name`, which holds the description) and `mcp_solve.outcome_category` + `solution_comparison.comparison_status` as the fields — the S37 Day-0 measurement error was wrong keys returning Solve 0 / Match 0
   - Diff against the recorded block; **any discrepancy is a finding, not a typo to smooth over**
2. **Re-derive the genuine floor from provenance, not the DB** (~30 min)
   - Confirm the mechanical count still yields **65** and the hand-partition still yields **76**
   - This is the input to P6c (the provenance file); record the per-model reasons now
3. **Re-verify the ganges cascade fingerprint** (~45 min)
   - Confirm `src/` is byte-identical to the reverted state (the cascade is **not** on `main`)
   - Re-run the cold compile and confirm the `$141`/`$145`/`$149` counts are **78 / 3 / 9** as banked — assert the *specific* error signature, not merely a non-zero count
   - Confirm `prolog` is still `model_optimal` + match (the model the rebind drifts)
4. **Re-verify the sarf blow-up and profile shape** (~45 min)
   - Confirm the three materialization sites are at their recorded lines (`constraint_jacobian.py:78`, `index_mapping.py:634`, `stationarity.py`) — Sprint 37 already found this precondition stale once (`stationarity.py` is +311 since the anchor, though the sites survived)
   - Confirm the six corpus-safety call sites are unperturbed
   - Re-confirm the blow-up is non-terminating under the cap; **do not** re-profile in full (Task 5 owns that)
5. **Re-verify the golden and gate inventory** (~30 min)
   - Count golden files, allowlist entries, in-scope total, presolve subset
   - Confirm `--min-scope` and `MAX_WORKERS` match their recorded values
6. **Record every derived figure with its commit** (~15 min)
   - Write `BASELINE_RECONFIRMATION.md` where each figure carries the SHA it was measured at — the retrospective's stated remedy for banked staleness

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_38/BASELINE_RECONFIRMATION.md` — every figure carrying the SHA it was measured at (`84fbe43c`).
- **Updated** `KNOWN_UNKNOWNS.md`: **1.1 → 🔍 INCOMPLETE** (its `rc=0` question is untested — Task 4 owns re-applying the cascade — though the banked *baseline* is refuted), **2.1 → ✅ VERIFIED**, **4.1 → ✅ VERIFIED**; Summary Statistics resolution block updated; a Task-2 input note added to **Unknown 6.2**.
- **No `src/`, DB or golden change.** The re-solve ran from `/tmp/task2_scratch`; the DB was restored to md5 `2ed0a42ba6861fd5837399ae88646d76` and the 36 regenerated goldens `git clean`'d.

### Result

**🔶 PROCEED WITH TWO CORRECTIONS.** The KPI block re-derives exactly on every line; the sarf and inventory fingerprints hold; two banked figures do not, and both change what a later task must do.

**✅ Reproduced exactly:** Parse 142 · Translate 135 · Solve 108 · Match 94 (65 cold + 29 presolve) · mi 7 · pse 6 · all-219 97 · goldens 170/7 allowlisted/163 in-scope/17 presolve · `--min-scope 170` · `MAX_WORKERS 3` · the mechanical floor proxy 65 against the recorded 76.

**⚠ Correction 1 — RETRACTED 2026-08-17 by Task 4** (the measurement counted only *printed* markers under a GAMS listing-truncation cap; concurrency was ruled out). Originally reported as: *the ganges `$141` count does not reproduce.* Banked 78; measured **15** (cold) / **49** (presolve), on both models. `$145`×3 and `$149`×9 reproduce *exactly* in both variants — so this is not a different run. `stationarity.py` gained **+53 lines after** the Day-4 measurement (the Day-6 fawley landing, same emit surface), which is a **plausible but unestablished** cause. Task 4 must design against the measured baseline and determine causation. Also: the banked figure came from the **presolve** run, while this task's prompt asked for a *cold* compile — a prompt error, so both variants were measured.

**❌ Correction 2 — the floor's provenance credits three out-of-corpus models.** `ps2_f_s`, `ps2_s`, `ps3_s_gic` are `non_convex` and outside the 142 candidates the floor is reported over, and were **already `non_convex` at the S32 anchor**, immediately after the S31 sprint that credited them. Either the floor has been **overstated by 3 since Sprint 31** (true in-corpus floor **73**) or its scope differs from Solve/Match's and that was never written down. Only **14 of the 76** are attributable by name at all. **Task 3 must resolve the target figure before building the provenance tracker.**

**Two method notes:** `grep -c` counts *lines*, not occurrences, and understated two of three error classes on the first pass; and the scratch-directory mitigation for the S37 Day-9 artifact incident **works** — zero repo-root artifacts, verified before restoring.

### Verification

```bash
# KPI block, re-derived from the DB (correct keys)
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
conv=[e for e in d['models'] if (e.get('convexity') or {}).get('status') in ('likely_convex','verified_convex')]
oc=lambda e:(e.get('mcp_solve') or {}).get('outcome_category')
mt=lambda e:(e.get('solution_comparison') or {}).get('comparison_status')
c=sum(1 for e in conv if oc(e)=='model_optimal' and mt(e)=='match')
p=sum(1 for e in conv if oc(e)=='model_optimal_presolve' and mt(e)=='match')
print('Solve', sum(1 for e in conv if oc(e) in ('model_optimal','model_optimal_presolve')))
print('Match', c+p, f'({c} cold + {p} presolve)')
print('all-219', sum(1 for e in d['models'] if mt(e)=='match'))
"
# EXPECT: Solve 108 · Match 94 (65 cold + 29 presolve) · all-219 97

# Golden + gate inventory
ls data/gamslib/mcp/*.gms | wc -l                                    # EXPECT 170
grep -vc "^#\|^$" scripts/sprint_audit/golden_staleness_allowlist.txt # EXPECT 7
grep -o "min-scope [0-9]*" .github/workflows/golden-staleness.yml     # EXPECT 170
grep -o "MAX_WORKERS = [0-9]*" scripts/sprint_audit/check_golden_staleness.py  # EXPECT 3

# ganges cascade is NOT on main; prolog still matching
git diff --stat 8cffec29..HEAD -- src/ | tail -1                      # EXPECT no cascade
.venv/bin/python -c "
import json; d=json.load(open('data/gamslib/gamslib_status.json'))
b={e['model_id']:e for e in d['models']}
for m in ('prolog','ganges','gangesx','sarf','turkey','camcge'):
    e=b.get(m); print(m, (e.get('mcp_solve') or {}).get('outcome_category'),
                        (e.get('solution_comparison') or {}).get('comparison_status'))
"
# EXPECT prolog model_optimal/match; ganges+gangesx path_syntax_error

# sarf materialization sites still at their recorded lines
sed -n '78p' src/ad/constraint_jacobian.py
sed -n '634p' src/ad/index_mapping.py
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/BASELINE_RECONFIRMATION.md` — every figure with the SHA it was measured at
- A confirmed-or-corrected KPI block (108 / 94 / 76 / 135 / mi 7 / pse 6 / 97)
- Fingerprint verdicts for the ganges cascade, the sarf sites, and the golden/gate inventory
- A per-model floor-provenance draft (input to Task 3's P6c design)
- An updated `KNOWN_UNKNOWNS.md` with every inherited-figure unknown resolved or corrected
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 4.1

### Acceptance Criteria

- [x] Every KPI re-derived from the DB with the correct keys, and matching the recorded block (or the discrepancy documented as a finding) — **all 10 lines matched exactly**
- [x] The mechanical floor count confirmed at **65** and recorded
- [ ] The genuine floor confirmed at **76** from the hand-partition → **NOT confirmed.** Its provenance credits three `non_convex`, out-of-corpus models, and only 14 of the 76 are attributable by name, so the correct target may be **73**. See `BASELINE_RECONFIRMATION.md` §2; resolving the figure is Task 3's precondition.
- [x] ganges cascade confirmed **absent** from `src/` (byte-identical to the S37 close)
- [x] `$145` = 3 and `$149` = 9 confirmed by *specific signature*, in both cold and presolve variants, on both models
- [ ] `$141` = 78 by *specific signature* → **UNRESOLVED. The Task-2 claim that it "does not reproduce" is RETRACTED** (Task 4): the counts were printed-marker undercounts under a GAMS truncation cap (true ≤37 cold / ≤73 presolve vs banked 78). A truncation-free census is required before any comparison.
- [x] `prolog` confirmed `model_optimal` + match (the leak target the rebind must not disturb)
- [x] sarf's three sites and six call sites confirmed intact at their recorded locations
- [x] Golden/gate inventory confirmed: 170 discovered / 7 allowlisted / 163 in-scope / 17 presolve / min-scope 170 / 3 workers
- [x] Every figure in `BASELINE_RECONFIRMATION.md` carries its measurement SHA (`84fbe43c`)
- [x] Any drifted figure is corrected in the plan **before** Day 1, not carried — both corrections are recorded here, in `KNOWN_UNKNOWNS.md`, and as explicit preconditions on Tasks 3 and 4
- [x] Unknowns 1.1, 2.1, 4.1 investigated and updated in KNOWN_UNKNOWNS.md (**1.1 🔍 INCOMPLETE** — its `rc=0` question is untested and owned by Task 4, though the banked baseline is refuted; **2.1 ✅**, **4.1 ✅**)

**On the two unchecked boxes:** Task 2's objective was to *re-derive and report*, and that is complete. Both criteria were drafted assuming the banked figures would hold; they did not, and the boxes stay unchecked to keep that visible rather than reworded to match the outcome. Each compound criterion has been **split** so every checkbox is a single, unambiguous claim — the verified halves (mechanical count 65; cascade absent; `$145`/`$149` exact) are checked, and only the two genuinely-unmet claims remain open. Both feed forward as named preconditions — the floor target to Task 3, the ganges baseline to Task 4.

---

## Task 3: Measurement-Integrity Design — Gate Scope, Floor Provenance & Re-Anchoring (P6)

**Status:** ✅ **COMPLETE** (2026-08-17)
**Priority:** Critical
**Estimated Time:** 4-5 hours
**Time Spent:** 5 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 6.1, 6.2, 6.3, 6.4

### Objective

Design the four P6 deliverables — the derived-figure helper, the two gate-scope assertions, the provenance-carrying floor tracker, and the DB re-anchor — so they can be implemented directly in the sprint, and so every other priority's acceptance gate can be expressed against them.

### Why This Matters

This task is on the critical path ahead of the two deep tracks, which is unusual for infrastructure. The reason is that **P6 defines how Sprint 38 measures itself**. Sprint 37's retrospective found the same failure mode — verifying a component while asserting a system property — in **six** separate places, two of them expensive:

- `solver_version` was a broken *read*; the regex had never matched, so two sprints of "populate it" instructions could not work
- a cleanup loop reported "all 20 artifacts untracked" while `git ls-files` showed 19 still tracked

A check that can pass while its property is false is a **false-negative generator — worse than no check**, because it retires the question. P1 and P4 both depend on gates that have known silent-narrowing modes; designing the assertions first means those gates are trustworthy when the tracks land against them.

### Background

Four sub-deliverables, each traced to a specific S37 defect:

| sub | defect it closes |
|---|---|
| **6a** derived-figure helper | prompt sweep re-staled within 24 h; the "+2 or 0" reaching the close doc |
| **6b** gate-scope assertions | `--resolve-changed` selects by **git diff** (uncommitted goldens invisible — produced a false GO); `leak-check` reports `NO-OP` for a model with no golden (how sarf's gate fails for a non-correctness reason) |
| **6c** floor provenance | mechanical count yields **65** against the recorded **76** |
| **6d** re-anchor | `--resolve-changed --since-commit 78ceaead` has anchored on the S34 close for four sprints; **the DB changed in S37** |

### What Needs to Be Done

1. **6a — design the derived-figure helper** (~1 hour)
   - A `scripts/sprint_audit/` entry point that emits the current KPI block (Solve / Match / split / Translate / mi / pse / all-219 / floor) on demand
   - Decide the output contract: human-readable block **and** a machine-readable form the day-prompt templates can embed
   - Specify the rule: any figure a doc must quote **carries its measurement SHA**
2. **6b — design the two gate-scope assertions** (~1.5 hours)
   - **`--resolve-changed`:** assert the selection is non-empty and covers the expected change set; exit non-zero when the git-diff selection is empty but uncommitted goldens exist. Specify the exact failure message — the S37 false GO was silent
   - **`leak-check`:** distinguish "clean" from "nothing to check". A `NO-OP` must be a **non-zero** exit or an explicit `UNVERIFIED` verdict, never mistakable for a pass
   - Define false-positive modes for both (a legitimately empty diff must remain expressible) and the escape hatch
3. **6c — design the floor provenance file** (~1.5 hours)
   - Schema: per-model entry with `model_id`, limb (`cold-match` | `fix-changed-cold-emit`), the sprint it began counting, and the evidence
   - Must reproduce **76** exactly from Task 2's draft partition; a tracker that cannot reproduce the current figure is not adoptable
   - Specify the guard: the tracker fails loudly if its total diverges from the hand-partition, rather than silently reporting its own number
4. **6d — choose and justify the re-anchor commit** (~45 min)
   - Candidate: the Sprint 37 close (`8cffec29`). Confirm what `--resolve-changed` selects at that anchor versus `78ceaead`
   - Record why re-anchoring is correct *now* (the DB moved) and what it costs (S34–S37 drift stops being re-checked every run)
5. **Write the design document** (~15 min)

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_38/MEASUREMENT_INTEGRITY_DESIGN.md` — all four sub-deliverables (6a–6d), with both gate-narrowing modes **reproduced live** as fail-before evidence.
- **Updated** `KNOWN_UNKNOWNS.md`: **6.1 → 🔶 PARTIALLY WRONG**, **6.2 → ❌ WRONG**, **6.3 → ✅ VERIFIED (conditional)**, **6.4 → ✅ VERIFIED**; Summary Statistics updated.
- **No `src/`, `scripts/`, DB or golden change** — design-only, so no quality gate.

### Result

**🔶 DESIGN COMPLETE, WITH TWO ASSUMPTIONS REFUTED.** Both refutations make P6 *smaller and sharper*.

**❌ `leak-check` already fails correctly (6.1, partial).** The premise that its `NO-OP` is "mistakable for a pass" is **wrong**: `make leak-check MODEL=sarf` **exits 2**. The real defect is the *diagnostic* — for a model with no golden, nothing was compared, yet the message asserts "the emit was byte-identical" and blames an inert fix. **A message asserting a property never measured** — in the tool built to catch exactly that. **P6b is ~half the planned work**: `--resolve-changed` needs a full assertion, `leak-check` needs only a message split.

**✅ `--resolve-changed`'s silent defect is CONFIRMED (6.1).** With a golden modified in the working tree, `_changed_golden_model_ids()` returns `[]` — invisible, because it diffs committed history only — and an empty selection currently reports **GO**.

**❌ The floor cannot be reproduced from existing artifacts (6.2).** Three derivations, three answers: mechanical **65**, golden-changed-ever **93**, documented chain **76**. The new evidence is the middle one — 28 of 29 presolve goldens have >1 commit, so "did the golden change?" is mechanical while "did a *real fix* change it *for this model's correctness*?" is a judgement no artifact records. **The tracker is redesigned as append-only** (`floor = baseline.count + len(entries)`), asserting against a committed `expected_floor` and failing loudly on divergence. **The baseline value is escalated to the owner: 73 or 76.**

**✅ Re-anchor to `8cffec29`, conditional on 6b (6.3).** Selections: `78ceaead` → **19**, `935d94b7` → 2, `8cffec29` → **0**. The candidate selecting zero is precisely 6b's hazard — re-anchoring first would trade a slow checkpoint for a silent one. **Sequence 6b → 6d.**

**✅ Four false-positive modes enumerated, all expressible (6.4).** The riskiest — an empty selection at sprint start — is *guaranteed* by 6d, so it is handled by construction.

### Verification

```bash
# 6b — the two narrowing modes reproduce today (fail-before evidence)
# (a) --resolve-changed selects by git diff: an uncommitted golden is invisible
git status --porcelain data/gamslib/mcp/ | head
# (b) leak-check on a model with no golden reports NO-OP rather than failing
make leak-check MODEL=sarf 2>&1 | tail -3

# 6c — the discrepancy the provenance file must resolve
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
conv=[e for e in d['models'] if (e.get('convexity') or {}).get('status') in ('likely_convex','verified_convex')]
oc=lambda e:(e.get('mcp_solve') or {}).get('outcome_category')
mt=lambda e:(e.get('solution_comparison') or {}).get('comparison_status')
print('mechanical floor proxy:', sum(1 for e in conv if oc(e)=='model_optimal' and mt(e)=='match'))
print('recorded genuine floor: 76')
"

# 6d — what the re-anchor changes
git log --oneline 78ceaead..8cffec29 -- data/gamslib/gamslib_status.json | wc -l

# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_38/MEASUREMENT_INTEGRITY_DESIGN.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/MEASUREMENT_INTEGRITY_DESIGN.md` covering all four sub-deliverables
- The derived-figure helper's output contract (human + machine forms)
- Exact assertion semantics and failure messages for both gate-narrowing modes, with false-positive modes named
- The floor-provenance schema, validated to reproduce **76** from Task 2's partition
- The re-anchor commit chosen, with what it selects and what re-anchoring costs
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 6.4

### Acceptance Criteria

- [x] All four sub-deliverables (6a–6d) designed to implementation detail
- [x] Both gate-narrowing modes **reproduced live** as fail-before evidence, not merely described — `--resolve-changed` returns `[]` for a working-tree golden edit; `make leak-check MODEL=sarf` exits 2
- [x] The `NO-OP`-is-not-a-pass semantics specified, including sarf's case explicitly — **and found already satisfied on the exit code**; the specified change is a *message* split (`UNVERIFIABLE` for golden-less vs `NO-OP` for exists-but-unchanged)
- [x] The floor-provenance schema reproduces its **declared baseline** → the original criterion asked for **76** *reconstructed*, which is **not possible** (three derivations give 65/93/76). **Resolved by decision rather than reconstruction: the owner declared `baseline.count = 73` on 2026-08-18**, and the append-only schema reproduces that exactly by construction. Three derivations give 65 / 93 / 76; the limb-2 qualifier is a judgement no repo artifact records. The schema is redesigned as **append-only from a declared baseline**, and the baseline value (73 or 76) is escalated to the owner. See `MEASUREMENT_INTEGRITY_DESIGN.md` §4.
- [x] The provenance tracker fails loudly on divergence rather than reporting its own number — asserts against a committed `expected_floor`, exits non-zero, and never emits a DB-derived figure
- [x] The re-anchor commit chosen and justified (`8cffec29`), with the cost stated — 19 models of settled S34–S37 drift stop being re-verified each run; **conditional on 6b landing first**, since the candidate selects 0
- [x] Every other priority's acceptance gate can be expressed against these gates — checked against Tasks 4 (full-corpus `--expect-drift` with `prolog` byte-identical), 5 (zero drift ×163 **plus** sarf newly producing a golden — this need drove the `--expect-new` flag in §6), and 6 (`--min-scope` raise)
- [x] Unknowns 6.1, 6.2, 6.3, 6.4 investigated and updated in KNOWN_UNKNOWNS.md (**6.1 🔶 PARTIALLY WRONG**, **6.2 ❌ WRONG**, **6.3 ✅ conditional**, **6.4 ✅**)

**On the unchecked box:** the criterion assumed the floor was reconstructible. It is not — three derivations give three answers, and the qualifier that distinguishes them is a judgement no artifact records. The box stays unchecked rather than reworded to match the outcome. The design adapts (append-only rather than reconstructing) and **one decision is escalated: the baseline is 73 or 76, which changes six sprints of reported history and is the owner's call.**

---

## Task 4: ganges P1 — `$149` Rebind-Predicate Design & Leak-Surface Analysis

**Status:** ✅ **COMPLETE — 🔶 REPLAN outcome** (2026-08-17)
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Time Spent:** 6 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2, 3
**Unknowns Verified:** 1.2, 1.3, 1.4, 1.5

### Objective

Design the narrowed `$149` rebind predicate that keeps ganges and gangesx at `rc=0` while leaving `prolog` byte-identical, and analyse the leak surface well enough that the sprint implements a design rather than searching for one.

### Why This Matters

P1 is the only track whose blocker is a **single named predicate**. Everything else about the cascade is verified working: all four fixes take ganges *and* gangesx from `rc=2` (78 × `$141`, 3 × `$145`, 9 × `$149`) to **`rc=0`, zero `$NNN`, zero `rPower`**, on both models, run per-model and never inferred.

The cascade cannot be split — reverting only `$149` returns `rc=2` with 9 × `$149`, so `$149` is **load-bearing and there is no leak-free subset**. That makes the predicate the whole task.

Sprint 37's fawley track produced the directly applicable lesson: **two narrowings failed because they only ever subtracted exclusions; the third succeeded by adding a positive requirement** about what must be true of the genuine case. The `$149` design should start from "what must be true of a genuinely-free `prod` bound" rather than "what does `prolog` look like".

### Background

- **#1668** records two fix directions: rebind parameter indices consistently, or **restrict the trigger to a genuinely-free `prod` bound**. Direction 2 is closer to the original intent.
- **`ISSUE_1667`** is the deferred-bounds ordering fix — control-verified, landing blocked, unreachable without the cascade.
- **Bucket is 0 and must stay stated as 0.** The 6th blocker (embedded `ganges0` **MS-5 @ −386785.5017** vs raw standalone **MS-2 @ 6395.5444**) is untouched, `mcp_model` stays **MS-4**, and a clean cascade buys the lateral `path_syntax_error → model_infeasible` (pse 6 → 4, **mi 7 → 9**). Solve stays 108, Match stays 94. The prep must not re-inflate this to "+2 or 0" — that figure was refuted on S37 Days 4–5 and still lives in the prep-era docs.
- **`$66` is Issue #1289**, open since Sprint 25; a Phase-0 gate was authored in S37 Day 5. A second cold blocker, `ac(i+2,r)` in `stat_pc(i)`, is untouched.

### What Needs to Be Done

1. **Characterise the `prolog` over-fire precisely** (~1.5 hours)
   - Reproduce the drift on `prolog` and capture *which* rebind fires and on what expression shape
   - Establish what distinguishes `prolog`'s bound from ganges' — structurally, not by name
2. **Draft the positive requirement** (~2 hours)
   - Following the fawley pattern: state what must be **true** of a genuinely-free `prod` bound that the rebind targets
   - Express it in terms available at the emit site; identify the IR/AST predicates needed
   - Explicitly reject a name-based or model-based discriminator (the S35–S37 leak history is entirely name/domain-based gates leaking)
3. **Map the leak surface** (~1.5 hours)
   - Identify every model whose emit passes through the same rebind path — this is the cohort the full-corpus gate must clear
   - **Full-corpus (163-golden), not a cohort subset** — Sprint 36's 6-model cohort missed all three markov leaks, which is why the full sweep is mandatory
4. **Specify the Phase-0 acceptance gate** (~45 min)
   - Per-model (ganges AND gangesx): emit → compile → count `$NNN` (assert 0) → solve cold AND presolve with `modelstat` asserted → bucket
   - `make check-goldens` full-corpus: **only ganges/gangesx drift; `prolog` byte-identical**
   - Determinism ×3; the 335s slow-emit goldens on a nightly regen slot
   - Expressed against Task 3's gate-scope assertions
5. **Define the REPLAN exit** (~15 min)
   - The condition under which the predicate is abandoned for the sprint, and what gets banked

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_38/GANGES_REBIND_PREDICATE_DESIGN.md` — the refutation, the probe methodology, three replacement directions, the Phase-0 gate, the 0-bucket restatement, and the `$141` retraction.
- **Updated** `KNOWN_UNKNOWNS.md`: **1.2 → ❌ WRONG**, **1.3 → 🔍 unreachable**, **1.4 → ✅ VERIFIED**, **1.5 → 🔍 untestable**, and **1.1 corrected** (its retracted finding replaced).
- **Corrected the merged Task-2 records** (per the owner's "fold it into Task 4"): `BASELINE_RECONFIRMATION.md` §3 + verdict, this file's Task-2 Result and acceptance criterion, and the CHANGELOG.
- **No `src/` change** — a read-only probe was inserted, measured and reverted; `src/` is byte-identical to `main`.

### Result

**🔶 REPLAN — #1668 direction 2 is not implementable as specified.**

A **read-only probe** at the exact rebind site shows ganges and `prolog` are **indistinguishable on every locally-available field**: `bound_indices` is `[]` for *both*, both have `e ∈ expr.index_sets`, and both show the same `[ParamRef, VarRef]` occurrence profile in the retained `expr` and in `log_term`.

The obvious candidate — *"fire only when the index is genuinely free"*, using the `bound_indices` parameter `_diff_prod` already receives — is **refuted**: the enclosing `sum(gp, …)` Day 4 identified is **stripped before differentiation reaches `_diff_prod`**, so the site cannot determine freeness at all. **The blocker is missing context, not a missing predicate**, which changes P1 from a predicate tweak into a plumbing or relocation problem.

**This is the fawley lesson inverted:** fawley worked because a positive requirement existed *in the information available at its site*. Here the correct and incorrect cases are locally identical.

**Three replacement directions named**, with **direction C (#1668 direction 1 — rebind parameter indices consistently) recommended first**: cheapest to test, and prematurely deprioritised in favour of the direction now refuted.

**Recommended re-budget:** P1 from 18–24 h to a **~4–6 h direction-C evaluation** using the banked probe, with the remainder to **P2 sarf** (the only KPI mover) or P8. The sprint has no floor lever either way.

**Also verified: 1.4 ✅** — no gate, workflow or script asserts monotonicity on `model_infeasible`, so a correct landing (mi 7 → 9) cannot be misreported as a regression by automation.

### Verification

```bash
# Reproduce the over-fire: prolog must currently be clean, and must stay clean
.venv/bin/python -c "
import json; d=json.load(open('data/gamslib/gamslib_status.json'))
e={x['model_id']:x for x in d['models']}['prolog']
print('prolog:', (e.get('mcp_solve') or {}).get('outcome_category'),
      (e.get('solution_comparison') or {}).get('comparison_status'))"
# EXPECT model_optimal match

# Baseline error counts on the raw models (the fingerprint the cascade clears)
for m in ganges gangesx; do
  test -f data/gamslib/raw/$m.gms && echo "  $m source present"
done

# Phase-0 doc exists for the deferred-bounds fix
ls docs/issues/ISSUE_1667_*.md docs/issues/ISSUE_1289_*.md

# Design doc
test -f docs/planning/EPIC_4/SPRINT_38/GANGES_REBIND_PREDICATE_DESIGN.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/GANGES_REBIND_PREDICATE_DESIGN.md`
- A precise structural characterisation of the `prolog` over-fire
- The **positive requirement** the narrowed predicate asserts, with the IR predicates it needs
- The full-corpus leak surface (which models traverse the rebind path)
- The Phase-0 acceptance gate, expressed against Task 3's assertions
- A stated REPLAN exit and what it banks
- **A restated bucket expectation of 0** (lateral pse → mi), so the sprint cannot drift back to "+2 or 0"
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 1.4, 1.5

### Acceptance Criteria

- [x] The `prolog` over-fire reproduced and characterised structurally, not by model name — reproduced by live probe; characterised as **locally indistinguishable from ganges**, which is a stronger and more useful result than a structural difference would have been
- [ ] The predicate is expressed as a **positive requirement** → **no predicate exists to express.** The candidate positive requirement was built and **refuted by measurement**: `bound_indices` is `[]` for both models. This is the finding, not an omission.
- [x] No name-based or domain-only discriminator in the design — none was adopted; the refuted candidate was structural, and all three replacement directions are structural
- [ ] Leak surface mapped **full-corpus** → **deliberately deferred with a reason.** The rebind path itself moves under each of the three replacement directions, so mapping the current path would produce a figure stale on the day a direction is picked — the banked-staleness failure this sprint keeps correcting. The two known members (ganges/gangesx intended, `prolog` must-not-drift) and `korcge`'s benign `rPower` drift are recorded.
- [x] Phase-0 gate specified per-model for ganges AND gangesx, with `modelstat` asserted — and it is direction-independent, so it survives the REPLAN
- [x] `prolog` byte-identical is an explicit gate criterion
- [x] Bucket expectation stated as **0 (lateral, mi rises to 9)** with the refuted "+2 or 0" called out — and **1.4 independently verifies no gate treats the mi rise as a regression**
- [x] REPLAN exit defined with its banked artifact — exit **taken**; banks the refutation, the probe methodology, three named directions, the gate and the bucket expectation
- [x] Unknowns 1.2, 1.3, 1.4, 1.5 investigated and updated in KNOWN_UNKNOWNS.md (**1.2 ❌ WRONG**, **1.3 🔍 unreachable**, **1.4 ✅**, **1.5 🔍 untestable**) — plus **1.1 corrected** with the `$141` retraction

**On the two unchecked boxes:** both presuppose that a workable predicate exists. Task 4's result is that it does not — the correct and over-firing cases are **locally identical** — so the boxes stay unchecked rather than reworded to match the outcome. The REPLAN is the deliverable: direction 2 is closed, three replacements are named, and P1's budget should drop from 18–24 h to a ~4–6 h direction-C evaluation.

---

## Task 5: sarf P2 — O(active) Re-Architecture Design Refresh & Atomicity Plan

**Status:** ✅ **COMPLETE** (2026-08-17)
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Time Spent:** 6 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.2, 2.3, 2.4, 2.5

### Objective

Refresh the sarf re-architecture design against the Sprint-37 profile, and produce an atomicity plan detailed enough that the 20–28h implementation is a build rather than an investigation.

### Why This Matters

P2 is **the sprint's only KPI mover** (+1 Translate → 136). It is also the largest single cost and the dominant risk: a partial landing is not partial progress but an **inconsistent MCP** — multipliers with no stationarity coupling.

Sprint 37 changed what this track is. The banked design blamed "369K columns"; the profile showed **the columns are cheap and differentiating each one is not**. It also killed the shortcut: the obvious memoization was built, measured at **~5%** against the **~66×** needed, and reverted — recorded in `ISSUE_1385` precisely so a future effort does not re-attempt it.

### Background

Profile (Sprint 37 Day 7, 180 s cap; `compute_constraint_jacobian` = **137 s**):

| function | calls | cum |
|---|---|---|
| `differentiate_expr` | 6,189,439 (761,897 primitive) | 121.6 s |
| `_diff_sum` | 1,154,628 | 104.5 s |
| `_is_concrete_instance_of` | 5,796,109 | 59.0 s |
| `simplify` | 10,486,266 | 49.7 s |
| `resolve_set_members` | 4,618,097 | 29.0 s |

- **The refuted shortcut:** memoizing `resolve_set_members` inside `_is_concrete_instance_of` moved `resolve_set_members` out of the top-14 and cut `_is_concrete_instance_of` 59.0 → 39.7 s, for **761,897 → 802,108** differentiations (~5%). The bottleneck moved to `simplify`/`_diff_sum`.
- **The headroom** is the **927×** ratio between declared columns (369,024) and active ones (398).
- **Three sites:** S1 `constraint_jacobian.py:78`, S2 `index_mapping.py:634`, S3 `stationarity.py`; plus **six** corpus-safety call sites that must be provably unperturbed.
- **Two gate peculiarities:** sarf has **no golden**, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason — the real gate is `make check-goldens` (zero drift ×163) **plus sarf newly producing a golden (163 → 164)**. And **sarf cannot be its own fixture**: at 369,024 columns the fail-before state does not terminate.

### What Needs to Be Done

1. **Re-validate the design premise against the profile** (~1.5 hours)
   - Confirm the O(active) short-circuit actually removes the `differentiate_expr` volume, not just the column enumeration
   - Estimate the post-re-arch call count and sanity-check it against the single-digit-seconds target — the design predicts it; nothing has measured it
2. **Specify the atomic change set** (~2 hours)
   - The 2-D constraint gate + S1/S2/S3 short-circuit + parametric `stat_task` + `task.fx` as **one unit**
   - For each of the three sites: what changes, what the guard is, what the fallback path is for every other model
   - Enumerate the six corpus-safety call sites and how each is shown unperturbed
3. **Design the verification strategy around the two gate peculiarities** (~1.5 hours)
   - Since sarf cannot be its own fixture, specify the **surrogate fixture** — a small model exercising the same guarded path, with a terminating fail-before state
   - Specify the golden-creation step (163 → 164 in-scope; 170 → 171 discovered) and its interaction with Task 6's presolve-golden adoption, which also moves the scope
4. **Specify the Phase-0 acceptance gate (PR20)** (~45 min)
   - `sarf_mcp.gms` completes in **single-digit seconds**
   - `stat_task` matches the banked 7-term derivation with **symbolic** multiplier indices — `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` empty
   - Byte-stable golden; determinism ×3; full-corpus zero drift
5. **Define the REPLAN exit and its trigger point** (~15 min)
   - The plan calls for taking this exit **early rather than nursing it** — specify the day and the observable that triggers it

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_38/SARF_REARCH_DESIGN.md` — profile-validated premise, the atomic change set site-by-site, the six call sites with their unperturbed-proof, the surrogate fixture, the golden/scope interaction, a **revised** Phase-0 gate, and a REPLAN exit with a named trigger.
- **Updated** `KNOWN_UNKNOWNS.md`: **2.2 → ✅**, **2.3 → ❌ WRONG**, **2.4 → ✅**, **2.5 → ✅**.
- **No `src/` change** — a read-only probe was inserted at `constraint_jacobian.py:1013`, measured and reverted; `src/` is byte-identical to `main`.

### Result

**🔶 PROCEED, WITH THE PHASE-0 THRESHOLD REFUTED.**

**✅ The premise (2.2) is confirmed decisively.** The sparsity check in the hot loop is **variable-level only** — once a variable is referenced in a row, the loop differentiates w.r.t. **every declared instance**. A read-only counter shows that after 75 s and 250,000 calls sarf is **still on `rows=1`**, with ~100 % of calls against `task`, at **~3,343 calls/s**. One row costs 369,024 calls ≈ **110 s**. So the short-circuit removes volume proportionally, not merely enumeration.

**❌ The timing claim (2.3) is refuted.** The row count is the other half of the product and the short-circuit does not touch it: **1,183 rows reference `task`** (equipb1 648 · tbal 384 · equipb2 120 · labor 24 · cbal 6 · acost3 1).

| | differentiations | at 3,343/s |
|---|---|---|
| current | **436,555,392** | **~36.3 hours** |
| O(active) | **470,834** | **~141 seconds** |
| gate (PR20) | — | single-digit seconds |

The 36.3-hour figure **explains the non-termination directly**. The short-circuit delivers its full **927×** and still lands **~16× short** of the gate.

**The threshold, not the design, is what fails — and the KPI does not require it.** The KPI is **+1 Translate**: sarf only needs to **complete**, and 141 s does. The 100 s cap that kills it today is a *test-harness* cap. **✅ RESOLVED 2026-08-18: the gate is revised to "sarf completes and produces a byte-stable golden, ≤ 300 s on a nightly slot."** Holding single-digit seconds would require **also gating the 1,183 rows** — scope not in the 20–28 h estimate — and would convert a 927× win into a REPLAN.

**✅ Surrogate fixture (2.4) sized from the measured rate:** ~5,000 declared columns, ~1.5 s un-gated — a genuine terminating fail-before — corpus-free, and asserting the **emitted shape** (symbolic multiplier indices) rather than only wall-clock.

**✅ Scope arithmetic (2.5) is order-independent:** P2 and P4 both finish at **207 discovered / 200 in-scope** in either order, so `--min-scope` ends at 207. A separate dependency does exist: **P6b should precede P2's gate run**, since `leak-check MODEL=sarf` otherwise reports a misleading `NO-OP`.

### Verification

```bash
# The three sites are where the design says they are
sed -n '78p' src/ad/constraint_jacobian.py
sed -n '634p' src/ad/index_mapping.py

# The gate peculiarity: sarf has no golden, so leak-check is a NO-OP
ls data/gamslib/mcp/sarf_mcp.gms 2>/dev/null || echo "  (no sarf golden — expected)"
make leak-check MODEL=sarf 2>&1 | tail -3

# The blow-up still does not terminate under cap (do NOT full-profile here)
timeout 100 .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms -o /tmp/sarf_mcp.gms 2>&1 | tail -2
echo "exit=$?  (124 = timed out, as expected)"

# The refuted shortcut is recorded so it is not re-attempted
grep -c "memoiz" docs/issues/ISSUE_1385_*.md

# Design doc
test -f docs/planning/EPIC_4/SPRINT_38/SARF_REARCH_DESIGN.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/SARF_REARCH_DESIGN.md`
- A profile-validated premise: the short-circuit removes differentiation volume, with an estimated post-re-arch call count
- The atomic change set, site by site, with the guard and fallback for each
- The six corpus-safety call sites enumerated with their unperturbed-proof
- A **surrogate fixture** design (since sarf cannot be its own fixture)
- The golden-creation step and its interaction with Task 6's scope change
- The Phase-0 gate (PR20) and a REPLAN exit with a named trigger day
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.2, 2.3, 2.4, 2.5

### Acceptance Criteria

- [x] The design premise re-validated against the *profile*, not the superseded 369K-column framing — and **re-measured at the call site**, which is stronger: the sparsity check is variable-level only, so volume is per-declared-column
- [x] The refuted memoization explicitly marked do-not-retry, with its measured ~5% recorded — carried in `ISSUE_1385` and the prompt; **not re-attempted**
- [x] The atomic change set specified as one unit, with a stated reason a partial landing is a REPLAN — S1 and S2 must move together or `get_col_id` silently drops live columns
- [x] All three sites confirmed at their recorded lines and all six call sites enumerated, with the unperturbed-proof for the four out-of-scope ones
- [x] Surrogate fixture designed with a terminating fail-before state — **sized from the measured 3,343 calls/s** (~5,000 columns ⇒ ~1.5 s un-gated), corpus-free, asserting the emitted *shape* not just wall-clock
- [x] The `NO-OP`-is-not-a-pass problem handled — real gate is `check-goldens` + new golden; **flagged that P6b must precede P2's gate run** so `leak-check MODEL=sarf` gives `UNVERIFIABLE` rather than a misleading `NO-OP`
- [x] Golden-count interaction with Task 6 resolved — **order-independent**: both orders end at 207 discovered / 200 in-scope
- [x] REPLAN exit has a named trigger day and observable — end of implementation day 2; observable is the per-row call count falling from 369,024 toward ~398, visible in minutes via the probe
- [x] Unknowns 2.2, 2.3, 2.4, 2.5 investigated and updated in KNOWN_UNKNOWNS.md (**2.2 ✅**, **2.3 ❌ WRONG**, **2.4 ✅**, **2.5 ✅**)
- [x] *(added by this task)* The Phase-0 timing gate is achievable **as revised** → the original was refuted at ~141 s vs "single-digit seconds"; **the owner revised it to ≤ 300 s nightly on 2026-08-18**, which ~141 s meets. The 927× column win is real; the 1,183 rows are untouched. The KPI (+1 Translate) does **not** require single-digit seconds, so the recommendation is to revise the gate to "completes, byte-stable golden, ≤ 300 s nightly" rather than expand scope to gate rows.

**On the unchecked box:** it is a criterion this task *added* after measurement, because the original criteria assumed the timing target was reachable and none of them tested it. Left unchecked so the refutation is visible: the design proceeds, the **threshold** needs an owner decision.

---

## Task 6: Presolve-Golden Adoption Plan & Runtime Impact (P4)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2, 3, 4
**Unknowns Verified:** 4.2, 4.3, 4.4

### Objective

Plan the deliberate, reviewed adoption of the 36 presolve goldens — including the per-model review protocol, the `--min-scope` change, and the leak-gate runtime impact at the enlarged scope.

### Why This Matters

The golden corpus is **153 cold vs 17 presolve**, while `model_optimal_presolve` accounts for **29 of the 94 matches**. The presolve emit path is materially less covered than the cold path, and the 36 goldens regenerated during Sprint 37 Day 9 are plausibly the fix.

They are also the sprint's clearest self-certification hazard. Sprint 37 swept them into a commit by accident; adopting them the same way would expand what `check-goldens` sweeps (170 → 206 discovered, 163 → 199 in-scope) **using references generated by that very run** — a reference set certifying itself. The plan's phrasing is deliberate: *generating references and committing them in one unreviewed step is how a gate stops being a gate.*

This task depends on Task 4 because **P4 changes the gate P1 runs against**, and the sprint schedules P4 after P1's gate run for that reason.

### Background

- The 36 were written by the presolve retry during a full `--only-solve` (S37 Day 9), taking presolve goldens 17 → 53.
- Current inventory: **170** golden files discovered, **7** allowlisted, **163** in-scope, **17** presolve.
- `--min-scope 170` is asserted on **discovery** (before allowlist narrowing), so adoption requires raising it to **206** or the assertion silently under-guards.
- The leak sweep is already the slowest gate; it runs at 3 workers after Sprint 37 fixed load-dependent timeouts at 6.

### What Needs to Be Done

1. **Inventory and reproduce the 36** (~1 hour)
   - Regenerate them from a clean re-solve and confirm all 36 reappear identically — if any is non-reproducible it is not adoptable
   - List them by model with the outcome that produced each
2. **Design the per-model review protocol** (~1 hour)
   - What "reviewed" means concretely: each golden checked against its model's *expected* presolve emit, not merely against the run that produced it
   - A triage order (models whose presolve path is load-bearing for a match first)
   - The rejection criterion and where an excluded model's justification is recorded
3. **Measure the runtime impact** (~45 min)
   - Time `make check-goldens` at 163 in-scope today; project 199 and confirm the 3-worker default still yields **0 timeouts**
   - If it does not, decide the mitigation (worker count, nightly split) **in prep**, not mid-sprint
4. **Specify the `--min-scope` change and its ordering** (~30 min)
   - 170 → 206, applied in the same change as the adoption so the assertion never lags the corpus
   - Confirm the assertion still fires on discovery, before narrowing
5. **Sequence against P1** (~15 min)
   - P1's full-corpus gate run must complete at the *old* scope first; specify the handoff

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Current inventory (the before-state)
ls data/gamslib/mcp/*.gms | wc -l                                     # 170 discovered
ls data/gamslib/mcp/*presolve*.gms 2>/dev/null | wc -l                # 17 presolve
grep -vc "^#\|^$" scripts/sprint_audit/golden_staleness_allowlist.txt # 7 allowlisted

# Baseline sweep runtime at the current scope (record for the projection)
time make check-goldens 2>&1 | tail -3

# The min-scope assertion fires on discovery
grep -o "min-scope [0-9]*" .github/workflows/golden-staleness.yml     # 170 -> must become 206

# Plan doc
test -f docs/planning/EPIC_4/SPRINT_38/PRESOLVE_GOLDEN_ADOPTION_PLAN.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/PRESOLVE_GOLDEN_ADOPTION_PLAN.md`
- The 36 goldens inventoried by model, with reproducibility confirmed
- A per-model review protocol with triage order and rejection criterion
- Measured sweep runtime at 163 and a projection at 199, with a mitigation if timeouts appear
- The `--min-scope` 170 → 206 change specified, applied atomically with adoption
- The P1 → P4 sequencing handoff
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.2, 4.3, 4.4

### Acceptance Criteria

- [ ] All 36 goldens regenerated and confirmed reproducible; any non-reproducible one excluded with a reason
- [ ] The review protocol requires checking against **expected** emit, not the generating run
- [ ] Sweep runtime measured at the current scope and projected at the new one, with 0 timeouts confirmed or a mitigation chosen
- [ ] `--min-scope` raise to 206 specified in the same change as adoption
- [ ] The self-certification hazard explicitly addressed in the protocol
- [ ] P1's gate run sequenced before the scope change
- [ ] Unknowns 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Consultation Ownership Decision Package (P3)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** **Requires a human decision-maker — cannot be completed by an execution agent alone**
**Dependencies:** Task 1
**Unknowns Verified:** 3.1, 3.2, 3.3

### Objective

Prepare everything needed for the Day-0 send-or-strike decision, so that the decision itself takes minutes and the outcome is executable either way.

### Why This Matters

This is not an engineering task, and that is precisely the point. The rocket/mine consultation bundle has been **FINALIZED since 2026-07-15** and has slipped **S33 → S34 → S35 → S36 → S37** with its one *action* checkbox unchecked. Sprint 37 Day 0 established why: **the bundle names no recipient, address, or channel**, so it was never executable by an execution agent.

Carrying it a fourth time without an owner converts a task into a permanent fixture and **quietly inflates every sprint's projected upside** — rocket's +1 Solve and fawley's +Solve have both been counted as reachable while the gating action went undone.

### Background

- The finalized input is `../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`; the bundle is `../SPRINT_36/CONSULTATION_BUNDLE.md`.
- **rocket:** +1 Solve contingent on a recommended option-set / continuation schedule.
- **fawley:** the +Solve is the **same class** — the S36 `--force` survey was NEGATIVE (homotopy/multistart/optfile all leave MS-5), so it needs a stronger continuation or reformulation.
- **mine:** **0 bucket** — the only non-invariant lever is an LP-side reformulation, out of emit scope; `x.up=inf` stays **BANNED**.

### What Needs to Be Done

1. **Assemble the send package** (~1 hour)
   - Confirm the bundle is complete and current: the question set, the reproducible cases, the ruled-out-lever survey
   - Draft the covering message, leaving only recipient and channel blank
   - Identify what a reply would need to contain to be actionable
2. **Cost the strike branch** (~45 min)
   - Enumerate exactly what is removed from projections if struck: rocket +1 Solve, fawley +Solve, and any downstream Sprint 39 dependency (S39's antecedent is now S38 P3)
   - Draft the reclassification wording so the strike is executable same-day
3. **Prepare the decision brief** (~30 min)
   - One page: what is being asked, the two branches, what each costs, and the fact that this is the fifth carry
   - **Name the specific question the human must answer:** who receives this, and by what channel
4. **Specify the tracking record** (~15 min)
   - If sent: where the send is recorded, and how a reply is tracked (issue #1462 currently has only the Sprint-28 bisect comment)

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# The finalized input and bundle exist and are unchanged
ls docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md
ls docs/planning/EPIC_4/SPRINT_36/CONSULTATION_BUNDLE.md 2>/dev/null

# No send record exists anywhere (the fact that motivates the decision)
grep -ri "sent to\|submitted to" docs/planning/EPIC_4/SPRINT_3*/CONSULTATION*.md | head

# Issue #1462's comment history (expect: only the Sprint-28 bisect)
gh issue view 1462 --comments 2>/dev/null | tail -20

# Decision brief exists
test -f docs/planning/EPIC_4/SPRINT_38/CONSULTATION_DECISION_BRIEF.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/CONSULTATION_DECISION_BRIEF.md` — one page, two branches, costed
- A send package complete except for recipient and channel
- The strike branch's reclassification wording, executable same-day
- The tracking-record specification for a send
- **An explicit statement of the single question a human must answer**
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3

### Acceptance Criteria

- [ ] Send package assembled and complete except recipient/channel
- [ ] Strike branch costed: rocket +1, fawley +Solve, and the S39 dependency named
- [ ] Decision brief is one page and states the fifth-carry history plainly
- [ ] The specific human question is stated: **who receives this, by what channel**
- [ ] Both branches are executable on Day 0 without further preparation
- [ ] Tracking record specified for the send branch
- [ ] Unknowns 3.1, 3.2, 3.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: camcge Epic-5 Handoff Scoping + turkey Testbed Procurement (P5)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Scope the camcge Epic-5 handoff so Epic 5 starts from Sprint 32–37's refutations rather than repeating them, and determine whether a licensed >1000-row GAMS-54 environment is obtainable for turkey.

### Why This Matters

**camcge's value to Epic 5 is the refutations, not the diagnosis.** Three-plus sprints have tried Walras variants: price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ omega 299. Without those recorded as *ruled out*, Epic 5 will re-run them. The **drop-row half must remain BANNED** — it is primal-correct but breaks the MCP dual.

**turkey is a procurement question, not an engineering one.** Its +1 Solve/Match has been "available pending a testbed" since Sprint 35 and has never been realizable, because no licensed >1000-row environment exists (local and CI are both demo). Sprint 36's prep already corrected an assumption that one was available. If it still is not, turkey should be stated as blocked rather than carried as reachable.

### Background

- **camcge (S37 Day 10 control, GAMS 54.2.1):** emit **19 s**, **641 single equations / 641 variables**, embedded NLP **MS-2 @ omega 191.7346**, `mcp_model` **MS-4 Infeasible**. Every predicted figure reproduced. The MCP is MS-4 against a *correct* NLP optimum — structural Walras rank-deficiency, **not an emit defect**.
- A numéraire alone is insufficient: it fixes the price-scaling ray, not the row-redundancy nullspace (the two-nullspaces diagnosis).
- **turkey:** MCP is **3,866 rows** against the GAMS demo **1000-row nonlinear** limit. The `$161` compile-recovery landed S35; S37 Day 9 corrected its stale row to `path_solve_license` and Day 10 confirmed it stable.

### What Needs to Be Done

1. **Assemble the camcge refutation record** (~1.5 hours)
   - Every Walras variant tried, its sprint, its outcome, and why it fails structurally
   - The two-nullspaces diagnosis stated so it is reusable
   - The **BANNED** list with reasons — drop-row explicitly
2. **Scope the per-model-numéraire fallback** (~45 min)
   - What Epic 5 would implement, and what it does and does not buy
   - Cross-reference `../EPIC_5/CGE_DEGENERACY_SCOPING.md`
3. **Investigate turkey testbed options** (~1 hour)
   - Determine concretely whether a licensed environment is obtainable, at what cost, and by when
   - If not: draft the wording that reclassifies turkey's +1 as blocked rather than pending
4. **Decide what P5 delivers if both are negative** (~15 min)
   - The honest floor for this priority is "two documents"; state that rather than implying bucket movement

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# camcge current state (MS-4 against a correct NLP optimum)
.venv/bin/python -c "
import json; d=json.load(open('data/gamslib/gamslib_status.json'))
e={x['model_id']:x for x in d['models']}['camcge']
print('camcge:', (e.get('mcp_solve') or {}).get('outcome_category'))"

# turkey is license-gated, not broken
.venv/bin/python -c "
import json; d=json.load(open('data/gamslib/gamslib_status.json'))
e={x['model_id']:x for x in d['models']}['turkey']
print('turkey:', (e.get('mcp_solve') or {}).get('outcome_category'))"
# EXPECT path_solve_license

# The Epic-5 scoping doc exists to hand off into
ls docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md 2>/dev/null || echo "  (create in handoff)"

# Handoff doc
test -f docs/planning/EPIC_4/SPRINT_38/CAMCGE_EPIC5_HANDOFF.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/CAMCGE_EPIC5_HANDOFF.md` — refutation record + two-nullspaces diagnosis + BANNED list
- The per-model-numéraire fallback scoped for Epic 5
- A concrete turkey testbed determination: obtainable (with cost/date) or blocked
- Reclassification wording if turkey remains blocked
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [ ] Every Walras variant tried since S32 recorded with its outcome and structural reason
- [ ] Drop-row recorded as **BANNED** with the primal-correct/dual-breaking reason
- [ ] The two-nullspaces diagnosis stated reusably
- [ ] Per-model-numéraire fallback scoped with what it does and does not buy
- [ ] turkey testbed determined concretely — not carried as "pending" for a fourth sprint
- [ ] If both branches are negative, P5's deliverable is honestly stated as documentation
- [ ] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Phase-0 Compliance Survey over the Open Backlog (P7)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 7.1, 7.2

### Objective

Survey the open issue backlog for missing `## Phase 0: Acceptance Gate` sections and produce the catalog that P7 backfills — and that Task 10 uses to determine which backlog candidates are even eligible.

### Why This Matters

Two long-open items were found in Sprint 37 to have **never had a Phase-0 section**, and both were discovered only when a sprint tried to *budget* them:

- **`$66` / #1289** — open since **Sprint 25**, so it was never implementable under CONTRIBUTING §392–447, cascade or not
- **sarf / #1385** — the same gap

An issue without a Phase-0 gate is not schedulable work; it is an idea. Finding that out during a sprint wastes the slot. Sprint 37 shipped `check_phase0_doc.py`, so the survey is now mechanizable.

### Background

- CONTRIBUTING §392–447 requires any `src/{ad,kkt,emit}`-touching PR to carry a `docs/issues/ISSUE_<N>_*.md` with a `## Phase 0: Acceptance Gate` section containing four canonical `###` subsections (prefix-matched, extras permitted — "rule C").
- The Sprint-37 CI gate enforces this **for PRs**, but nothing audits the *backlog*.
- Measured compliance over the three most recent emit-touching PRs before the gate existed: **1 of 3**, and that one only after a reviewer asked.

### What Needs to Be Done

1. **Enumerate the open backlog** (~45 min)
   - Open issues that a future sprint might plausibly schedule (emit/AD/KKT-touching)
   - Cross-reference against `docs/issues/ISSUE_*.md`
2. **Run the compliance check** (~1 hour)
   - Use `check_phase0_doc.py` semantics against each issue doc
   - Classify: compliant / has doc but no Phase-0 section / no doc at all
3. **Prioritise the backfill** (~1 hour)
   - Rank by likelihood of being scheduled — anything in Sprint 38's own P8 catalog ranks first
   - Confirm `$66`/#1289's authored gate is complete, or finish it
4. **Produce the catalog** (~30 min)
   - A table Task 10 can filter on, and P7 can work through in the sprint

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# The gate script exists and its rule is documented consistently
ls scripts/sprint_audit/check_phase0_doc.py
grep -n "these 4 subsections" CONTRIBUTING.md

# Count issue docs and how many carry a Phase-0 section
ls docs/issues/ISSUE_*.md | wc -l
grep -l "## Phase 0: Acceptance Gate" docs/issues/ISSUE_*.md | wc -l

# The two known-missing cases from Sprint 37
grep -c "## Phase 0: Acceptance Gate" docs/issues/ISSUE_1289_*.md docs/issues/ISSUE_1385_*.md

# Catalog
test -f docs/planning/EPIC_4/SPRINT_38/PHASE0_COMPLIANCE_CATALOG.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/PHASE0_COMPLIANCE_CATALOG.md`
- A three-way classification of the open backlog (compliant / doc-without-gate / no doc)
- A prioritised backfill list, with Sprint 38's P8 candidates ranked first
- Confirmation that `$66`/#1289's gate is complete
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2

### Acceptance Criteria

- [ ] Open backlog enumerated for emit/AD/KKT-touching issues
- [ ] Every issue classified three ways, using the CI gate's own semantics
- [ ] Backfill list prioritised by scheduling likelihood
- [ ] `$66`/#1289 confirmed complete or finished in this task
- [ ] The catalog is filterable by Task 10 (eligibility for the P8 sweep)
- [ ] A compliance count recorded, so P7's sprint work has a measurable target
- [ ] Unknowns 7.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Emit-Backlog Candidate Catalog & Selection-Rule Dry Run (P8)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2, 9
**Unknowns Verified:** 8.1, 8.2

### Objective

Build the candidate catalog for the P8 backlog sweep and dry-run the pre-registered selection rule against it, so the sprint's slack absorber cannot drift into an open-ended diagnosis effort.

### Why This Matters

P8 exists because Sprint 38 has **no floor-moving lever**, and the honest response is to spend the slack on adjacent backlog rather than inflating the deep tracks. But an under-specified sweep is exactly how a sprint loses a week.

The plan therefore pre-registers a selection rule: **a model enters the sweep only if it has a reproduced fingerprint AND a named fix surface**; anything requiring a new diagnosis is banked, not started. This is the S30–S37 control-first discipline applied to the backlog. Dry-running the rule in prep tells us whether P8 has ≥2 genuine candidates — and if it does not, the budget should move before the sprint starts, not during it.

### Background

- Candidate pools: the `$149`-half unblocks from P1 (**dinam, indus, turkpow, clearlak**), the residual `path_solve_terminated` cohort, and `model_infeasible` models whose root cause is a *bounded* emit defect rather than a structural one.
- Known structural blockers that must **not** enter: turkpow (ragged `Table mdatat`), clearlak (dynamic sets) — unless P1's `$149` fix demonstrably unblocks their half.
- Sprint 37's Task-9 finding stands: a fingerprint match can be a **false positive** (a helper matched the `$141` pattern but came from an unrelated cesam fix), so "reproduced fingerprint" means the specific mechanism, not a grep hit.

### What Needs to Be Done

1. **Assemble the candidate pool** (~1 hour)
   - Query the DB for `path_solve_terminated`, `path_syntax_error`, and `model_infeasible` models outside the deep tracks
   - Cross-reference each against its issue doc and Task 9's compliance catalog
2. **Apply the selection rule** (~1.5 hours)
   - For each candidate, determine: is there a **reproduced** fingerprint? Is there a **named** fix surface?
   - Reproduce fingerprints for the top candidates — asserting the mechanism, not a pattern hit
   - Record rejections with the reason (new diagnosis required / structural / no Phase-0 doc)
3. **Confirm P8 has ≥2 eligible candidates** (~45 min)
   - If fewer than 2 survive, say so and recommend where the 12–16h goes instead — this is a prep finding, not a mid-sprint discovery
4. **Write the catalog** (~30 min)

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Candidate pool from the DB, outside the deep tracks
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
deep={'ganges','gangesx','sarf','camcge','turkey','rocket','mine','fawley','markov'}
oc=lambda e:(e.get('mcp_solve') or {}).get('outcome_category')
for cat in ('path_solve_terminated','path_syntax_error','model_infeasible'):
    ms=[e['model_id'] for e in d['models'] if oc(e)==cat and e['model_id'] not in deep]
    print(f'{cat}: {len(ms)}  {ms[:10]}')
"

# The four $149-half candidates
.venv/bin/python -c "
import json; d=json.load(open('data/gamslib/gamslib_status.json'))
b={e['model_id']:e for e in d['models']}
for m in ('dinam','indus','turkpow','clearlak'):
    e=b.get(m)
    print(m, (e.get('mcp_solve') or {}).get('outcome_category') if e else 'ABSENT')"

# Catalog
test -f docs/planning/EPIC_4/SPRINT_38/BACKLOG_CANDIDATE_CATALOG.md && echo "✓"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/BACKLOG_CANDIDATE_CATALOG.md`
- The candidate pool with each model's outcome category and issue doc
- Selection-rule verdicts: eligible / rejected, with the rejection reason
- Reproduced fingerprints for the top candidates, asserting mechanism not pattern
- A stated finding on whether P8 has ≥2 eligible candidates, and a budget recommendation if not
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.1, 8.2

### Acceptance Criteria

- [ ] Candidate pool assembled from the DB, deep tracks excluded
- [ ] The pre-registered rule applied to every candidate, with rejections reasoned
- [ ] "Reproduced fingerprint" means the specific mechanism — false-positive risk explicitly handled
- [ ] Structural blockers (turkpow ragged table, clearlak dynamic sets) excluded unless P1 demonstrably unblocks them
- [ ] Cross-referenced against Task 9's Phase-0 catalog for eligibility
- [ ] A clear verdict on whether P8 is viable, with a budget recommendation if it is not
- [ ] Unknowns 8.1, 8.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 38 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 38 Day 1
**Owner:** Development team
**Dependencies:** All tasks (1–10)

### Objective

Produce `SPRINT_38/PLAN.md` and `SPRINT_38/prompts/PLAN_PROMPTS.md` — a Day-0-through-Day-13 schedule with per-priority budgets, checkpoints, REPLAN exits, and a Day-0 GO/NO-GO gate — consuming the designs and findings from Tasks 1–10.

### Why This Matters

This is the task that converts prep into execution. It is last because it depends on every other task: the schedule cannot front-load a track whose design is unresolved, and it cannot budget P8 before Task 10 says whether P8 is viable.

Sprint 38's schedule has one ordering constraint the plan states explicitly: **P4 is scheduled after P1's gate run**, because P4 changes what `check-goldens` sweeps. And one item is fixed at **Day 0**: the P3 consultation decision, placed there precisely because it has slipped five sprints on the absence of an owner rather than on effort.

### Why the schedule must not re-introduce a floor target

The plan states the sprint is **deliberately NOT floor-targeted**. The schedule must preserve that. Sprint 36's reverted landing attempt came from floor pressure; naming the absence of a floor lever is the mitigation, and a schedule that quietly reinstates one undoes it.

### Background

- Sprint 38 budget: **100–134h** over 14 days, cap **168h** (≤12h/day). Upper bound leaves 34h slack; 9.6h/day at the upper bound.
- Per-priority: P1 18–24h · P2 20–28h · P3 4–6h · P4 10–14h · P5 10–14h · P6 14–18h · P7 8–10h · P8 12–16h · retest 4h.
- Format precedent: `../SPRINT_37/PLAN.md` (21 sections, Day 0 + Days 1–13) and `../SPRINT_37/prompts/PLAN_PROMPTS.md`.
- **A Sprint-37 process finding applies directly:** the Day-13 prompt listed only SPRINT_LOG / RETROSPECTIVE / SUMMARY row, so the carryforwards file was missed at close. **Day 13's prompt must name `SPRINT_39_CARRYFORWARDS.md` explicitly.**

### What Needs to Be Done

1. **Build the day-by-day schedule** (~1.5 hours)
   - Day 0: baseline re-confirm + GO/NO-GO + **the P3 decision**
   - Days 1–13 across the eight priorities, honouring P1-before-P4
   - Front-load P1 and P2 (the two that produce landings); P2's REPLAN trigger day named per Task 5
   - Checkpoints at Day 5 and Day 10; final retest Day 13
   - **No day exceeds 12h**; verify by mechanical count, not by eye
2. **Write the per-day prompts** (~1 hour)
   - One prompt per day, following the S37 format
   - **Derive figures at execution time** rather than quoting them (P6a) — this is the sprint whose retrospective demanded it
   - Day 13's prompt explicitly names SPRINT_LOG, SPRINT_RETROSPECTIVE, SUMMARY row **and SPRINT_39_CARRYFORWARDS.md**
3. **Define REPLAN exits and the GO/NO-GO gate** (~45 min)
   - Per-priority REPLAN conditions from Tasks 4, 5, 6, 8, 10
   - Day-0 GO/NO-GO conditions from Task 2's baseline re-derivation
4. **Verify the budget mechanically** (~30 min)
   - Sum per-day hours; assert ≤12/day and <168 total
5. **Record the pre-registered close rules** (~15 min)
   - Firm landing vs carryforward (all three gates); the mi-may-rise-to-9 reporting rule; the floor-from-provenance rule

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Both planning documents exist
test -f docs/planning/EPIC_4/SPRINT_38/PLAN.md && echo "✓ PLAN.md"
test -f docs/planning/EPIC_4/SPRINT_38/prompts/PLAN_PROMPTS.md && echo "✓ PLAN_PROMPTS.md"

# All 14 days present (Day 0 + Days 1-13)
grep -c "^## Day \|^### Day " docs/planning/EPIC_4/SPRINT_38/PLAN.md
grep -c "^## Day " docs/planning/EPIC_4/SPRINT_38/prompts/PLAN_PROMPTS.md

# Budget: no day over 12h, total under 168h
grep -o "~[0-9]\+ *h" docs/planning/EPIC_4/SPRINT_38/PLAN.md | tr -d '~h ' | sort -n | tail -1
# EXPECT <= 12

# Day 13 names the carryforwards file (the S37 miss)
grep -c "SPRINT_39_CARRYFORWARDS" docs/planning/EPIC_4/SPRINT_38/prompts/PLAN_PROMPTS.md
# EXPECT >= 1

# The schedule does not reinstate a floor target
grep -in "floor 76 → 77\|floor.*target\|+1 floor" docs/planning/EPIC_4/SPRINT_38/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_38/PLAN.md` — Day 0 + Days 1–13, per-priority budgets, checkpoints, REPLAN exits, GO/NO-GO gate
- `docs/planning/EPIC_4/SPRINT_38/prompts/PLAN_PROMPTS.md` — one prompt per day, figures derived not quoted
- A mechanical budget verification (≤12h/day, <168h total)
- Pre-registered close rules, including the mi-rise and floor-provenance reporting rules

### Acceptance Criteria

- [ ] Day 0 + Days 1–13 all scheduled, with the P3 decision on Day 0
- [ ] P1's gate run scheduled before P4's scope change
- [ ] P2's REPLAN trigger day named explicitly (per the plan's "early rather than nursed")
- [ ] Checkpoints at Day 5 and Day 10; final retest Day 13
- [ ] No day exceeds 12h and the total is under 168h — verified by count, not by eye
- [ ] Day 13's prompt names `SPRINT_39_CARRYFORWARDS.md` explicitly
- [ ] Day prompts derive figures rather than quoting them
- [ ] The schedule does **not** reinstate a genuine-floor target
- [ ] REPLAN exits defined for every deep track; GO/NO-GO conditions defined from Task 2

---

## Summary

### Critical Path (Must Complete Before Sprint 38 Day 1)

1. ✅ **Task 1: Known Unknowns** (COMPLETE — 2026-08-17, 3 hours) — CRITICAL
2. ✅ **Task 2: Re-Derive the Baseline** (COMPLETE — 2026-08-17, 4 hours) — CRITICAL
3. ✅ **Task 3: Measurement-Integrity Design** (COMPLETE — 2026-08-17, 5 hours) — CRITICAL
4. ✅ **Task 4: ganges Rebind Predicate** (COMPLETE — 2026-08-17, 6 h; **REPLAN outcome**) — CRITICAL
5. **Task 6: Presolve-Golden Adoption** (3-4 hours) — HIGH (gated on Task 4)
6. **Task 11: Plan Sprint 38** (3-4 hours) — CRITICAL

**Total Critical Path Time:** ~21-28 hours (~3-4 working days)

### Also Critical (Parallelisable)

- ✅ **Task 5: sarf Re-Architecture Design** (COMPLETE — 2026-08-17, 6 h) — the only KPI mover; ran parallel to Task 4

### High Priority (Should Complete Before Sprint 38)

- **Task 7: Consultation Decision Package** (2-3 hours) — **requires a human**; start early to leave time for an answer

### Medium Priority (Complete Before Day 1, or by Mid-Sprint)

- **Task 8: camcge Epic-5 + turkey Testbed** (3-4 hours)
- **Task 9: Phase-0 Compliance Survey** (3-4 hours) — gates Task 10
- **Task 10: Backlog Candidate Catalog** (3-4 hours)

### Overall Prep Time: 37-50 hours (~5-6 working days)

---

## Success Criteria for Prep Phase

- [x] ✅ Known Unknowns document created (**28 unknowns, 8 categories**), every Critical one resolved in prep or Day 0
- [ ] The Sprint-37 baseline **re-derived**, not re-read, with every figure carrying its measurement SHA
- [ ] Measurement-integrity design complete for all four sub-deliverables, with both gate-narrowing modes reproduced live
- [ ] ganges `$149` rebind predicate designed as a **positive requirement**, with a full-corpus leak surface
- [ ] sarf re-architecture design refreshed against the profile, with a surrogate fixture and a named REPLAN trigger
- [ ] Presolve-golden adoption planned with a review protocol and a measured runtime projection
- [ ] Consultation decision package ready — **both branches executable on Day 0**
- [ ] camcge Epic-5 handoff scoped; turkey testbed determined concretely
- [ ] Phase-0 compliance catalog produced; `$66`/#1289 confirmed
- [ ] P8 viability determined (≥2 eligible candidates, or a budget recommendation)
- [ ] `SPRINT_38/PLAN.md` and `prompts/PLAN_PROMPTS.md` complete, budget mechanically verified

**Overall Goal:** No blockers, no surprises, high-confidence sprint start — and **no inherited figure carried without re-derivation**.

---

## Notes and Risks

### Key Differences from Sprint 37 Prep

1. **The baseline is re-derived, not re-confirmed.** Sprint 37's prep verified fingerprints against documentation; this prep recomputes them, because banked staleness was the sprint's most general finding.
2. **Infrastructure (P6) is on the critical path ahead of the deep tracks**, because it defines how the sprint measures itself.
3. **One task requires a human** (Task 7). It is scheduled early so an answer has time to arrive.
4. **The sprint has no floor lever**, so prep must resist re-introducing one — Tasks 4 and 11 both carry explicit guards.
5. **Two tasks move the golden scope** (Tasks 5 and 6); their interaction is resolved in prep rather than discovered.

### Potential Risks

1. **Risk:** Task 2 finds a drifted figure that re-scopes a priority
   - **Mitigation:** Task 2 is second on the critical path, before any design work
   - **Contingency:** Re-scope in prep; the plan's per-priority budgets have 34h of slack
2. **Risk:** The `$149` positive requirement cannot be expressed at the emit site
   - **Mitigation:** Task 4 identifies the needed IR predicates explicitly
   - **Contingency:** REPLAN exit defined; the cascade stays banked with a sharper blocker
3. **Risk:** sarf's re-arch cannot be made atomic within budget
   - **Mitigation:** Task 5 specifies the change set site by site before the sprint
   - **Contingency:** REPLAN trigger day named — take the exit early rather than nursing it
4. **Risk:** The consultation decision does not arrive by Day 0
   - **Mitigation:** Task 7 prepares both branches so either is executable immediately
   - **Contingency:** If no answer by Day 0, the strike branch executes by default — a fifth carry is not an acceptable outcome
5. **Risk:** P8 has fewer than 2 eligible candidates
   - **Mitigation:** Task 10 dry-runs the selection rule in prep
   - **Contingency:** Recommend the 12–16h elsewhere before the sprint starts
6. **Risk:** The enlarged golden scope pushes the leak sweep into timeouts
   - **Mitigation:** Task 6 measures at 163 and projects 199
   - **Contingency:** Worker-count or nightly-split mitigation chosen in prep

### Sprint 38 Success Definition

**Minimum Success:**
- P3 resolved (sent or struck) — no sixth carry
- P6 measurement-integrity infrastructure landed
- KPIs maintained: Solve 108 / Match 94 / floor 76 / Translate 135

**Target Success:**
- The above, plus **P2 sarf lands** (+1 Translate → 136)
- P1 ganges cascade lands leak-free (0 bucket; pse 6 → 4, mi 7 → 9)
- P4 presolve goldens adopted (scope 163 → ~199)

**Exceptional Success:**
- All of the above, plus P5/P7/P8 complete
- turkey's +1 realized on a licensed testbed
- ≥2 backlog models recovered

---

## Appendix: Document Cross-References

### Sprint 38 Definition
- `../PROJECT_PLAN.md` — "Sprint 38 (Weeks 41–42): Sprint 37 Carryforward…" — goal, 8 priorities, deliverables, acceptance criteria, effort, risk
- `../PROJECT_PLAN.md` — Rolling KPIs (S38 column), footnote ⁸ (genuine-floor ramp), Sprint-to-Sprint Dependencies
- `../GOALS.md` — Epic 4 goal categories; Sprint 38 serves **6 (Solve Stage: emit_gams.py blockers)**, **7 (PATH Convergence & Solution Matching)**, and **8 (Performance, Quality & Release)**

### Sprint 37 Carryforward Sources
- `../SPRINT_37/SPRINT_38_CARRYFORWARDS.md` — the six carryforwards with bounded next steps; §2 what shipped; §3 Day-0 staging; §4 process carryforwards
- `../SPRINT_37/SPRINT_RETROSPECTIVE.md` §7 — the six Sprint-38 recommendations
- `../SPRINT_37/SPRINT_LOG.md` — close gates, day-by-day, the three-gate landing rule
- `../SPRINT_37/DAY4_GANGES_CONTROL.md` — the verified cascade, the `prolog` over-fire, the load-bearing `$149`
- `../SPRINT_37/DAY5_CHECKPOINT1.md` — P2 disposition; `$66`/#1289's missing Phase-0 section
- `../SPRINT_37/DAY6_FAWLEY_LANDING.md` — the fawley positive-requirement pattern (Task 4's model); Day 7 sarf profile (Task 5's input)
- `../SPRINT_37/DAY10_CHECKPOINT2.md` — camcge control figures; the `solver_version` broken-read
- `../SPRINT_37/GAMS54_REBASELINE_DIFF.md` — the v54 re-pin; the floor-not-DB-derivable finding

### Issue Docs
- `../../../issues/ISSUE_1667_ganges-deferred-bounds-before-include.md` — P1 deferred-bounds ordering (control-verified, landing blocked)
- `../../../issues/ISSUE_1289_ganges-family-calibration-assignment-stripping.md` — `$66`, open since Sprint 25
- `../../../issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` — P2 sarf O(active)
- GitHub **#1667** (deferred-bounds) · **#1668** (the `$149` rebind over-fire, two fix directions)

### Research Documents
- `../../../research/gamslib_kpi_definitions.md` — KPI definitions underpinning the Task-2 re-derivation
- `../../../research/convexity_detection.md` + `CONVEXITY_VERIFICATION_DESIGN.md` — the convex-candidate corpus scope (142)
- `../../../research/multidimensional_indexing.md` — indexing semantics relevant to the `$149` rebind and sarf's `task(g,t,m,n)`
- `../../../research/preprocessor_directives.md` — `$onMultiR`/`$include` semantics behind ganges' 6th blocker

### Process & Standards
- `../../../../CONTRIBUTING.md` §392–447 — the Phase-0 acceptance-gate requirement (Task 9)
- `scripts/sprint_audit/check_phase0_doc.py` — the CI gate implementing it
- `scripts/sprint_audit/check_golden_staleness.py` — the leak gate (`--min-scope`, 3 workers)
- `scripts/gamslib/run_full_test.py` — `--resolve-changed --since-commit` checkpoint (re-anchored by P6d)

### Format Precedents
- `../../EPIC_1/SPRINT_4/PREP_PLAN.md` and `../../EPIC_1/SPRINT_5/PREP_PLAN.md` — prep-plan format
- `../SPRINT_37/PREP_PLAN.md` — the immediately preceding Epic-4 prep cycle (11 tasks, 37–50h)
- `../SPRINT_37/PLAN.md` + `../SPRINT_37/prompts/PLAN_PROMPTS.md` — Task 11's output format

---

**END OF SPRINT 38 PREP PLAN**
