# Sprint 39 Preparation Plan

**Purpose:** Complete the preparation tasks that must land before Sprint 39 Day 1
**Timeline:** Complete before Sprint 39 Day 1
**Goal:** De-risk the Sprint 38 carryforwards so every Sprint-39 priority starts from a *measured* disposition rather than a banked claim

**Anchor:** `9ab2c0c3` (Sprint 38 close, 2026-08-26) · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**

> **Which Sprint-38 anchor?** Sprint 38's own close artifacts (`SPRINT_LOG.md`, `SPRINT_RETROSPECTIVE.md`, `SPRINT_39_CARRYFORWARDS.md`) cite **`8e32be09`**, not `9ab2c0c3`. Both are correct for what they describe and **neither is a wrong baseline**:
> - `8e32be09` is the merge of PR #1705, the HEAD those documents were *written against* — a close document cannot cite its own merge commit, which does not exist yet at authoring time.
> - `9ab2c0c3` is the merge of PR #1706, the close PR itself, and is therefore the commit at which Sprint 38 is actually closed on `main`. **Use it.**
>
> **The distinction cannot change a re-derived figure.** `git diff 8e32be09 9ab2c0c3` is **docs-only** — CHANGELOG plus four Sprint-38 planning documents; no `src/`, no goldens, and `gamslib_status.json` and `floor_provenance.json` are byte-identical at both. Verified by deriving at each: **Solve 111 · Match 96** either way. Re-anchoring to `8e32be09` by mistake is therefore harmless for KPIs, but cite `9ab2c0c3` so the provenance is unambiguous.
**Sprint definition:** `../PROJECT_PLAN.md` → *Sprint 39 (Weeks 43–44): Sprint 38 Carryforward — the dyncge Second Defect, lnts, sarf's Four Call Sites, the Floor-Classification Decision & the Positional-Domain Audit*

**Key insight carried from Sprint 38:** the sprint's two most expensive days each turned out to be **two defects wearing one fingerprint**, and **three of its four Phase-0 gates named the wrong *layer*** — two under-scoped (naming `emit_gams.py` for defects decided upstream in AD/KKT), one over-scoped (demanding new logic for a diagonal-triviality test that had existed since #942). This prep plan is therefore weighted toward **tracing and reproduction** rather than design: Tasks 4–7 exist because their sprint priorities each rest on a claim nobody has yet re-measured on current `main`.

---

## Executive Summary

Sprint 38 closed by **clearing an entire failure category** — `path_solve_terminated` **4 → 0** — taking **Solve 108 → 111** and **Match 94 → 96** through four firm landings, every one leak-gated unqualified. It handed forward an unusually sharp set of carryforwards (`../SPRINT_38/SPRINT_39_CARRYFORWARDS.md`), but two of them are sharp in an uncomfortable way: **fixing a defect revealed a second defect underneath it** (dyncge), and **one candidate was never traced at all** (lnts).

Sprint 39 addresses ten priorities:

1. **P1 (Decision):** the genuine-floor classification — **it blocks the sprint's own baseline**
2. **P2 (Critical):** dyncge's second emit defect (`CASE_B`) — the sprint's only *new* diagnosis
3. **P3 (Critical):** lnts — hypothesis *and* fix surface untraced
4. **P4 (KPI):** sarf's four located call sites — **+1 Translate**, the only KPI mover
5. **P5 (Prevention):** the positional-vs-declared-domain audit
6. **P6 (Date-gated):** consultation reply integration, or the 2026-09-09 follow-up
7. **P7 (Integrity):** the presolve-record systemic remedy — all 14 rows or none
8. **P8 (Infrastructure):** the four Sprint-38 retrospective process findings
9. **P9 (Epic 5):** the numéraire-selection rule + degeneracy detection, **design only**
10. **P10 (Slack):** the general emit-backlog sweep

This prep plan front-loads the work that would otherwise be discovered mid-sprint: **re-deriving the baseline** (Task 2), **assembling the floor decision so an owner can answer it on Day 0** (Task 3), and **tracing the three technical tracks whose fix surfaces are currently hypotheses** (Tasks 4–6). Tasks 7–11 produce the surveys, designs and catalogs the remaining priorities consume.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 39 Goal Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | ✅ Create Sprint 39 Known Unknowns List | Critical | 3-4 hours | None | Proactive unknown identification across all 10 priorities |
| 2 | ✅ Re-Derive the Sprint-38 Baseline & Carryforward Fingerprints | Critical | 3-4 hours | Task 1 | Verify 111/96/135/floor-73 and every banked fingerprint on current `main` |
| 3 | ✅ The Floor-Classification Decision Package (P1) | Critical | 2-3 hours | Tasks 1, 2 | P1 — the Day-0 decision that blocks the sprint's baseline |
| 4 | ✅ dyncge Second-Defect Diagnosis & Layer Trace (P2) | Critical | 5-7 hours | Tasks 1, 2 | P2 — the sprint's only new **instance**; the mechanism is the known #1381 family, and dyncge is its first **silent** case |
| 5 | ✅ lnts Fingerprint Reproduction & Runtime-Probe Design (P3) | Critical | 4-6 hours | Tasks 1, 2 | P3 — an entirely untraced hypothesis |
| 6 | ✅ sarf's Four Call Sites — Cost Attribution & Atomicity Plan (P4) | Critical | 5-7 hours | Tasks 1, 2 | P4 — the only KPI mover (+1 Translate) |
| 7 | ✅ Positional-vs-Declared-Domain Site Survey (P5) | High | 4-5 hours | Tasks 1, 2 | P5 — the audit's input catalog |
| 8 | Presolve-Record Remedy Design (P7) | High | 3-4 hours | Tasks 1, 2 | P7 — all 14 rows or none |
| 9 | Consultation Reply-Integration & Follow-Up Package (P6) | Medium | 2-3 hours | Task 1 | P6 — both branches prepared before the date gate |
| 10 | Epic-5 Design Scoping: Numéraire Rule & Degeneracy Detection (P9) | Medium | 3-4 hours | Tasks 1, 2 | P9 — design only, no camcge experiment |
| 11 | Emit-Backlog Catalog Refresh & Process-Infrastructure Spec (P8, P10) | Medium | 3-4 hours | Tasks 1, 2, 7 | P8 infrastructure + P10 slack absorber |
| 12 | Plan Sprint 39 Detailed Schedule | Critical | 3-4 hours | All tasks (1–11) | Day-by-day schedule + REPLAN exits + budget |

**Total Estimated Time:** ~40–55 hours (~5–7 working days)

**Critical Path:** Tasks **1 → 2 → {3, 4, 5, 6} → 12**

Task 2 gates everything technical: four priorities rest on fingerprints measured at `8e32be09` or earlier, and Sprint 38 established that **a banked figure goes stale in as little as 24 hours**. Tasks 4, 5 and 6 are the three tracks whose fix surfaces are currently *hypotheses*; they are parallelisable once Task 2 lands. Task 3 is short but sits on the critical path because **Sprint 39 cannot report a floor movement until it resolves** — it is a decision, not engineering, and it needs a package an owner can answer from.

Task 7 feeds Task 11 (the catalog refresh reuses the survey's method). Task 12 depends on everything.

---

## Task 1: Create Sprint 39 Known Unknowns List

**Status:** ✅ **COMPLETE** (2026-08-26)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Time Spent:** 3 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** n/a — this task *creates* the unknowns (30 across 10 categories)

### Objective

Produce `docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md` enumerating every assumption Sprint 39's plan rests on, categorised by priority, each with research questions, a verification method, a risk-if-wrong, and an owner — so that assumptions are refuted **in prep**, when refutation is cheap, rather than on a sprint day.

### Why This Matters

The Known-Unknowns process has caught a materially wrong premise in every recent sprint. Sprint 38's prep alone found that **the ganges `$149` rebind fix was a no-op** (265 fires, zero residual), that **the Epic-5 handoff was already written**, that **14 of 36 presolve goldens would have pinned emits that do not reproduce their NLP solution**, and that **the floor's provenance credited three out-of-corpus models** — a −3 re-baseline. Each was a plan premise that would have failed mid-sprint.

Sprint 39 carries at least four premises that have never been tested: lnts's mechanism *and* its fix surface, dyncge's residual being in the `pf`/`pq` block, sarf's remaining cost being confined to four call sites, and the assumption that the positional-domain defect class has only the two known instances.

### Background

`../SPRINT_38/KNOWN_UNKNOWNS.md` is the template: 28 unknowns across 8 categories, each with **Priority / Assumption / Research Questions / How to Verify / Risk if Wrong / Estimated Research Time / Owner / Verification Results**. Its final tally was **18 ✅ VERIFIED / 6 ❌ WRONG / 3 🔶 PARTIALLY WRONG / 1 🔍 INCOMPLETE** — a 32 % refutation rate on assumptions that had already survived a planning pass.

Categories should map to Sprint 39's priorities. Candidate seeds, drawn from `../SPRINT_38/SPRINT_39_CARRYFORWARDS.md`:

- **Floor (P1):** is the definition's test the one that was actually applied? Does `polygon` really carry the identical DB shape? Are there *other* models that qualify under the same reading and were also mis-classified?
- **dyncge (P2):** is the residual in the `pf`/`pq` block, or does it merely *surface* there? Is `CASE_B` reachable to `CASE_A` at all, or is dyncge non-convex like elec?
- **lnts (P3):** does the two-`.fx`-mechanism story survive a runtime bound probe? Is the `fix_rhs = "0"` fallback even reached for lnts?
- **sarf (P4):** are the four call sites still at their recorded locations? Does the O(active) projection still hold at ~141 s, or has the corpus moved?
- **Positional domain (P5):** how many sites resolve positionally against a declared domain, and do the two known instances generalise?
- **Presolve records (P7):** are there still exactly 14 affected rows, or did Sprint 38's adoptions change the count?

### What Needs to Be Done

1. **Enumerate the assumptions** in `../PROJECT_PLAN.md`'s Sprint 39 entry and `../SPRINT_38/SPRINT_39_CARRYFORWARDS.md` — every figure, every named fix surface, every "should".
2. **Group into categories**, one per sprint priority, numbered `N.M`.
3. **For each unknown, write all eight sections**: Priority · Assumption · Research Questions · How to Verify · Risk if Wrong · Estimated Research Time · Owner · Verification Results *(left empty for prep to fill)*.
4. **Add a mapping table** — unknown → the prep task that verifies it — so no unknown is orphaned and every later task carries an `Unknowns Verified:` line.
5. **Flag the deferred-unknown lineage** — which unknowns descend from a Sprint-38 disposition, so a reader can tell a fresh question from a re-asked one.

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md` — 30 unknowns across 10 categories, each with all 8 required sections
- **Added** the Task-to-Unknown mapping table (Appendix), assigning every unknown to an owning prep task
- **Updated** `PREP_PLAN.md` Tasks 2–12 with `Unknowns Verified` metadata, a deliverable, and an acceptance-criteria item each
- **Updated** `CHANGELOG.md` with the Task 1 completion entry

### Result

✅ **COMPLETE — 30 unknowns, 10 categories, 40.0 research hours** (⚠ over the 28–36 h target — see correction 1 below).

| metric | target | actual |
|---|---|---|
| Total unknowns | 22–30 (aim 25+) | **30** |
| Critical | ~25 % | **7 (23 %)** |
| High | ~40 % | **12 (40 %)** |
| Medium | ~25 % | **8 (27 %)** |
| Low | ~10 % | **3 (10 %)** |
| Research time | 28–36 h | **40.0 h** ⚠ **over target by 4 h** |
| Categories | all sprint components | **10** |

**Every unknown is owned by exactly one prep task**, with Tasks 2 and 12 *contributing to* / *integrating* rather than owning. Coverage was checked mechanically, not by eye.

**Two corrections made during creation, both of the "derive it, don't recall it" class:**

1. **The research-time total was written as ~33.0 h from memory, "corrected" to 29.0 h — and 29.0 was ALSO wrong.** The derived sum is **40.0 h**, and it has been 40.0 h since the file's first commit (`60e2581a`); no per-unknown estimate has changed since, so this was never a drift — the figure was simply never summed. It was published with the words *"derived by summing the per-unknown estimates, not recalled"*, which made an unaudited number look audited. Caught by the mechanical snippet pass (PR #1709), not by review or by the correction that claimed to have fixed it.
   **The lesson is not "derive it, don't recall it" — that was already the lesson, and it still produced a wrong number.** It is that *a claim of having derived a figure is itself unverifiable prose*; only a re-derivation at the point of use is evidence. **Consequence:** at 40.0 h the research no longer fits the **34–47 h** budgeted for Tasks 2–11 at its lower bound — the prep is only completable near the top of its range, which Task 12 must schedule around.
2. **The prompt's category list numbered `Category 9` twice** (Epic-5 Handoff and General Emit-Backlog Sweep) and described "5 main categories" while listing ten. Resolved as **10 categories**, with the emit-backlog sweep as Category 10.

**The heaviest category is not the one with the most hours.** Category 4 (sarf) has four unknowns and 6.5 h, but Category 2 (dyncge) carries **two Criticals** because it is the sprint's only new **instance** *and* the model whose previous gate mis-scoped. *(Task 4: the mechanism turned out to be the known #1381 family — the two Criticals were still the right call, since the instance is the family's first silent one.)*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# Document exists
test -f docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md && echo "✅ exists"

# Unknown count (excluding any 'Unknown X.Y' template placeholder)
grep -c "^## Unknown [0-9]" docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md

# Every unknown carries all 8 required sections
python3 - <<'PY'
import re
s = open('docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md').read()
req = ['### Priority','### Assumption','### Research Questions','### How to Verify',
       '### Risk if Wrong','### Estimated Research Time','### Owner','### Verification Results']
# drop the 'Unknown X.Y' template placeholder -- same predicate as the grep above,
# or this reports 31 and contradicts the count two lines earlier
blocks = [b for b in re.split(r'^## Unknown ', s, flags=re.M)[1:] if re.match(r'\d', b)]
bad = [b.splitlines()[0] for b in blocks if not all(r in b for r in req)]
print(f"unknowns: {len(blocks)} | missing-section: {len(bad)} {bad if bad else ''}")
PY

# Categories cover every Sprint-39 priority (expect >= 10)
grep -c "^# Category" docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md

# Mapping table present and non-empty
grep -E -A3 "unknown .*prep task|Mapping" docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md | head -5
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md` with ≥ 20 unknowns across ≥ 10 categories
- A mapping table from each unknown to the prep task that verifies it
- A deferred-unknown lineage note distinguishing fresh questions from re-asked ones

### Acceptance Criteria

- [x] Document created at `docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md`
- [x] ≥ 20 unknowns, each with all 8 required sections
- [x] Every Sprint-39 priority (P1–P10) has at least one category
- [x] Every unknown maps to a prep task; no unknown is orphaned
- [x] Critical/High unknowns are scheduled into a prep task that completes before Day 1
- [x] The lineage note identifies which unknowns descend from Sprint-38 dispositions

---

## Task 2: Re-Derive the Sprint-38 Baseline & Carryforward Fingerprints

**Status:** ✅ COMPLETE (2026-08-27)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Time Spent:** 3.5 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 1.1, 2.2, 3.3, 4.1, 7.1, 10.1

### Objective

Re-derive every headline figure and every banked fingerprint Sprint 39's plan quotes, **on current `main`**, and record which reproduce and which do not — before any design work assumes them.

### Why This Matters

Sprint 38 proved twice that a banked figure is a liability. Its Day-8 prompt sweep corrected six stale figures and was **re-staled by that same sprint's Day-9 re-baseline within 24 hours**. And at consultation send time, a package carried for **five sprints** turned out to describe a failure mode (`EXIT — other error`) that **no longer reproduced** — prep had re-verified the *conclusion* and stamped the toolchain, but not the *description*.

Sprint 39 quotes a lot: `CASE_B` at 6.22e-02, sarf at 28 m 40 s, 14 presolve rows, 9,734 iterations for agreste. Every one is a premise for a priority.

### Background

**Sprint 38 close (`9ab2c0c3`), to be re-derived not copied:**

| quantity | figure |
|---|---|
| Solve / Match | **111** / **96** (65 cold + 31 presolve) |
| Translate / Parse | **135** / **142** of 142 candidates |
| `path_solve_terminated` | **0** — the category Sprint 38 emptied |
| `path_solve_license` | **11** |
| model_infeasible / path_syntax_error | **7** / **6** |
| all-219 Match | **99** |
| genuine floor | **73** (`floor_provenance.json`, baseline 73 + 0 entries) |
| leak-gate scope | **186** in-scope goldens (7 allowlisted) |

**Fingerprints to re-reproduce**, each from `../SPRINT_38/`:

- **dyncge** — `scripts/diagnostics/kkt_residual.py` → `CASE_B`, max relative **6.22e-02** at `stat_pf(CAP,SRV)`; cold MCP MS-1 @ **381401.119** vs NLP **539570.5027**
- **lnts** — MS-4 at iteration 0; the `y("y2","h50")` / `5` and `45` values
- **sarf** — killed at **28 m 40 s** against the ≤300 s gate; the four untouched call sites still at their recorded locations
- **agreste / mine** — MS-5 Locally Infeasible after **9,734** / **10,662** PATH iterations, NLP MS-1 @ 17706.43 / 17500.0
- **weapons** — still a spurious presolve match; `mcp_file_used` still dangling for **13** other rows

**Method notes carried from Sprint 38, to avoid re-learning them:**
- **`grep -c` counts lines, not occurrences** — it understated two of three error classes on a first pass.
- **Read counts from GAMS's own `**** N ERROR(S)` / `EXECERROR = n` line**, never from a marker count, which undercounts under listing truncation.
- **Run GAMS from a scratch directory** — corpus sources write artifacts to `cwd` (four models `execute_unload "result.gdx"`).
  - **Documented exception: `scripts/diagnostics/kkt_residual.py` runs GAMS with `cwd=PROJECT_ROOT`** (`scripts/diagnostics/kkt_residual.py:928`). That is deliberate, not an oversight — it is how the repo-relative `$include` resolves (#1275). It does *not* pollute the repo root, because the harness redirects both outputs: `o=<scratch>/<stem>.lst` and `ScrDir=<scratch>`. **Measured on dyncge at Sprint 38 close: 0 new repo-root entries** in `git status --porcelain`. Do not "fix" this by changing its `cwd`. Still run the artifact check below after using it — the guarantee comes from two flags that a future edit could drop silently.
- **Anchor `^****` when grepping a `.lst`** — it contains echoed source too.

### What Needs to Be Done

1. **Re-derive the KPI block** with `scripts/sprint_audit/kpi_block.py` and the floor with `scripts/sprint_audit/floor_tracker.py`; confirm each line against the table above and record the commit.
2. **Re-reproduce each fingerprint** from a scratch directory, using GAMS's own terminal line for any count.
3. **Confirm the leak-gate inventory** — 186 in-scope, 7 allowlisted — with `--min-scope` still asserted on discovery.
4. **Verify the four sarf call sites still exist at their recorded locations** (`git log -L` or a symbol search), since `stationarity.py` and `emit_gams.py` both changed in Sprint 38.
5. **Re-count the presolve-record population** — the live count of dangling `mcp_file_used` rows is **14** (13 pre-existing plus `weapons`, whose presolve golden was reverted). Confirm it, and confirm `weapons` is still the only spurious match.
6. **Write `BASELINE_RECONFIRMATION.md`** recording, per figure: reproduced / corrected / not reproducible, each with the command and the commit. **A correction here is a finding, and must be routed to the task that depends on it.**

### Changes

- **NEW** `docs/planning/EPIC_4/SPRINT_39/BASELINE_RECONFIRMATION.md` — 14 figures, each with a verdict, the command that produced it, and the commit it was measured at
- `KNOWN_UNKNOWNS.md` — Unknowns **1.1, 2.2, 3.3, 4.1, 7.1, 10.1** moved from 🔍 INCOMPLETE to ✅ VERIFIED, each with Verified by / Date / Measured at / Findings / Evidence / Decision
- `CHANGELOG.md` — Sprint 39 Prep entry

### Result

✅ **COMPLETE — no baseline figure is wrong.** All 14 figures re-derived at `a8669ad6`: 12 reproduced outright, 1 reproduced with a caveat (agreste's source runs two solves; the banked figure is the second), and 1 — sarf's "28 m 40 s" — turns out **not to be a reproducible quantity**: it is a kill time, not a property of the model. The claim it stands for (*sarf does not terminate; the ≤300 s gate is not met*) reproduces and then some — a capped run reached **1900 s** (~6.3× the gate) still enumerating, with no output file.

**Four corrections, each routed:**

| # | correction | routed to |
|---|---|---|
| 1 | PREP_PLAN's own Task 6 check greps the wrong files/symbols for the four sarf call sites; its "these files moved" rationale is inverted | **Task 6** ✅ applied |
| 2 | Five distinct presolve populations (48 / 40 / 34 / 31 / 14 dangling), all correct — P7 must name which it means | **Task 8** |
| 3 | sarf's hot path at the cap is `enumerate_equation_instances`, not the four `enumerate_variable_instances` sites — Unknown 4.2 is genuinely open<br>⚠ **Task 6 found this correction itself wrong**: at a 900 s cap `enumerate_equation_instances` is 0.329 s / 0.04 %. Task 2's shorter cap stopped *inside* that phase, so the deepest live frame read as the cost. The premise it refutes still fails — just not for this reason. | **Task 6** ✅ |
| 4 | `robot` is the one non-solving candidate with no owning issue doc | **Task 11** |

**The finding that matters most is for Task 3.** twocge's and elec's cold emits both changed, but **not in the same way**: twocge's entire cold delta is a comment block plus two `nu_*.fx` guard lines, while elec's changed the stationarity equations themselves. Unknown 1.1 asks exactly this. **The floor is 73, 74 or 75** — the 74 reading was not considered at Sprint 38 close. Task 2 deliberately does not decide it.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# Headline KPIs + floor, both carrying their commit
.venv/bin/python scripts/sprint_audit/kpi_block.py --format line
.venv/bin/python scripts/sprint_audit/floor_tracker.py
# EXPECT: Solve 111 · Match 96 (65 cold + 31 presolve) · Translate 135 · mi 7 · pse 6 · all-219 99
# EXPECT: Genuine floor: 73  = baseline 73 + 0 recorded movement(s)

# path_solve_terminated must still be empty
.venv/bin/python -c "
import json; from collections import Counter
d=json.load(open('data/gamslib/gamslib_status.json'))
c=Counter(m.get('mcp_solve',{}).get('outcome_category') for m in d['models']
          if m.get('convexity',{}).get('status') in ('verified_convex','likely_convex'))
print('terminated:', c['path_solve_terminated'], '| license:', c['path_solve_license'])"

# dyncge's CASE_B fingerprint
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/dyncge.gms | tail -8
# EXPECT: verdict: CASE_B ... max-residual row: stat_pf(CAP,SRV) rel = 6.22e-02

# Leak-gate inventory (scope assertion, not just the verdict)
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py 2>&1 | head -2
# EXPECT: checked 186 in-scope golden(s) (7 allowlisted, ...)

# Presolve-record population
# Same predicate as Task 8's block, deliberately: the canonical population is the
# PRESOLVE rows (P7's remedy is "all 14 rows or none"). Both forms return 14 today
# only because every dangling row happens to be a presolve row -- drop the
# restriction and the two blocks would report different values for the same figure.
.venv/bin/python -c "
import json,os
d=json.load(open('data/gamslib/gamslib_status.json'))
pre=[m for m in d['models'] if m.get('mcp_solve',{}).get('outcome_category')=='model_optimal_presolve']
dang=[m['model_id'] for m in pre if (f:=m['mcp_solve'].get('mcp_file_used')) and not os.path.exists(f)]
print('dangling mcp_file_used:', len(dang), sorted(dang))"

# The reconfirmation doc exists and records a verdict per figure
test -f docs/planning/EPIC_4/SPRINT_39/BASELINE_RECONFIRMATION.md && \
  # Count VERDICT CELLS, not free words. The prose form under-counts (a
  # case-sensitive "reproduced|corrected|NOT reproducible" returns 3 against 14
  # verdicts, because every verdict token is uppercase) and -i over-counts
  # (18 — it matches narrative prose too). What the criterion actually asserts
  # is "one verdict per figure", so count rows and verdicts and compare.
  R=docs/planning/EPIC_4/SPRINT_39/BASELINE_RECONFIRMATION.md
  rows=$(grep -cE '^\| *[0-9]+ *\|' "$R")
  verdicts=$(grep -cE '^\| *[0-9]+ *\|.*\| *(✅|🔶|❌) ' "$R")
  echo "figures=$rows verdicts=$verdicts  $([ "$rows" = "$verdicts" ] && echo OK || echo MISMATCH)"
  grep -oE '\| *(✅|🔶|❌) \*\*[A-Z, ]+\*\*' "$R" | sed 's/^| *//' | sort | uniq -c
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/BASELINE_RECONFIRMATION.md` — per-figure verdict with the command and commit for each
- A corrections list, each routed to the prep task or sprint priority that depends on it
- Confirmation that the four sarf call sites still exist where recorded
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.2, 3.3, 4.1, 7.1, 10.1

### Acceptance Criteria

- [x] Every headline KPI re-derived at execution time and matching, or the discrepancy recorded
- [x] Genuine floor read from `floor_provenance.json`, never a mechanical DB count
- [x] `path_solve_terminated` confirmed still **0**
- [x] Every quoted fingerprint re-reproduced or explicitly marked NOT reproducible
- [x] Leak-gate scope asserted at **186** with 7 allowlisted
- [x] Every correction routed to a named downstream task
- [x] All GAMS runs performed from a scratch directory; zero repo-root artifacts afterwards
  - Assert it, do not eyeball it — `scripts/diagnostics/kkt_residual.py` is an intentional `cwd=PROJECT_ROOT` exception (above), so the repo root is genuinely in play:
    ```bash
    git status --porcelain -z | tr '\0' '\n' | sort > /tmp/before.txt
    # ... run the harness / GAMS steps ...
    git status --porcelain -z | tr '\0' '\n' | sort > /tmp/after.txt
    comm -13 /tmp/before.txt /tmp/after.txt   # MUST be empty
    ```
- [x] Unknowns 1.1, 2.2, 3.3, 4.1, 7.1, 10.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: The Floor-Classification Decision Package (P1)

**Status:** ✅ COMPLETE (2026-08-29)
**Priority:** Critical
**Estimated Time:** 2-3 hours
**Time Spent:** 2.5 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team (decision: repository owner)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.3

### Objective

Assemble a one-page package an owner can decide from on Day 0: is the genuine floor **73**, **74**, or **75**? *(Scoped as "73 or 75" when written. Task 3's own measurements added **74**: the counter-argument this task was asked to state for 73 is refuted — `polygon`, the precedent, is `likely_convex` like twocge and elec — while the two cold changes turn out to differ in kind, which 74 turns on.)* Include the evidence, the counter-argument, the downstream consequences of each answer, and the exact edit each implies.

### Why This Matters

**Sprint 39 cannot report a floor movement until this resolves** — its own baseline depends on the answer. Carrying it undecided a second time turns a KPI into something unfalsifiable.

It is also the second consecutive sprint where a *decision*, not engineering effort, was the blocker: the consultation slipped five sprints on the absence of a named recipient. Scheduling the decision on Day 0 with a ready package is the mitigation.

### Background

`scripts/sprint_audit/floor_tracker.py` reports **73** (`baseline 73 + 0 entries`), which is the number of record under Sprint 38's close rule #3. **The written definition appears to owe two entries.**

> *methodology* = cold emit **byte-identical to pre-fix**, matches only via warm-start; *genuine* = a real emit fix **changed the cold emit** — still genuine if it matches only via the presolve warm-start (the polygon/ps2 precedent).

| model | cold emit changed? | matches? | in the 142? | was aborting before? |
|---|---|---|---|---|
| **twocge** (S38 D9) | ✅ 2 `.fx` guard lines added (`204f35ac`) | ✅ | ✅ | ✅ |
| **elec** (S38 D12) | ✅ −12 bytes, confirmed by the leak gate | ✅ | ✅ | ✅ |

Both were **aborting before the fix**, so neither match is a solver effect. `polygon` — the precedent the definition names — carries the identical DB shape today.

**Sprint 38 Day 9 applied the wrong test** ("it matched via the presolve retry"); the definition turns on whether the *cold emit* changed. Day 12 inherited that reasoning without re-checking it. The close flagged this rather than self-applying it, because **the plan pre-registered flat-73** and a +2 discovered by the closer, in the direction the closer would prefer, is exactly what a process built on *"an unqualified pass or it is not a landing"* should refuse to approve for itself.

### What Needs to Be Done

1. **Re-verify both claims from git**, not from prose: that `twocge_mcp.gms` and `elec_mcp.gms` — the **cold** emits, not the presolve variants — changed in their landing commits, and what changed.
2. **Search for other models that qualify under the same reading.** If the test was applied wrongly twice, it may have been applied wrongly before. Sweep the provenance file's baseline period for models whose cold emit changed in a landing sprint and that match today. **A third instance changes the shape of the decision from "add two entries" to "the classification needs re-deriving".**
3. **State the counter-argument fairly** — the strongest case for 73 is that the presolve retry is doing the work at solve time, and that the definition's "still genuine" clause was written for the polygon/ps2 *non-convex* case, which twocge may not be. Check twocge's convexity status and cold-solve behaviour and say so either way.
4. **Write the exact edit each answer implies** — the two JSON entries with `limb`, `since_sprint`, `evidence`, `pr`; and the list of downstream reports needing re-baselining (Rolling-KPIs floor line, footnote ⁸, `SUMMARY.md` rows 38–39).
5. **State the consequence for Sprint 39's acceptance criteria** under each answer.

### Changes

- **NEW** `docs/planning/EPIC_4/SPRINT_39/FLOOR_DECISION_BRIEF.md` — evidence, both counter-arguments, all three answers' consequences, the exact edit each implies
- **NEW** `docs/planning/EPIC_4/SPRINT_39/floor_provenance_entries.draft.json` — ready-to-apply entries, validated against the live `_entry_schema` and against `compute_floor` (74 with one, 75 with both)
- `KNOWN_UNKNOWNS.md` — **1.1 ✅ VERIFIED**, **1.2 ✅ VERIFIED**, **1.3 ❌ WRONG**
- `CHANGELOG.md` — Sprint 39 Prep entry

### Result

✅ **COMPLETE — and the decision's shape changed during preparation.** The plan frames this as "73 or 75". Two measurements move it:

**1. The counter-argument the plan proposed for 73 is refuted.** It rests on the "still genuine via warm-start" clause having been written for a **non-convex** shape that twocge might not fit. But `polygon` — the only in-corpus member of the "polygon/ps2" precedent, and the one the definition names — is **`likely_convex`**, exactly like twocge and elec. The `non_convex` members are `ps2_*`/`ps3_*`, the three **out-of-corpus** models the 2026-08-18 re-baseline removed. Convexity cannot separate twocge from the precedent.

**2. A distinction the plan did not anticipate makes 74 live.** The two cold changes differ in kind: elec's rewrote the **stationarity equations** (a wrong derivative made right); twocge's entire delta is **two `nu_*.fx` multiplier-fixing lines** for MCP-excluded instances. One may call that bookkeeping rather than a correctness fix — though those lines are load-bearing, since twocge aborted without them.

**Measured, not inferred.** Both cold emits now *solve* (`MS-1`) but converge on a different KKT point — twocge **55.508** vs NLP 56.7778, elec **244.624** vs 243.8128 — which is why the pipeline retries with the warm start. `polygon` does not solve cold at all (MS-5). All three match only via presolve: the clause's exact situation.

**No third model.** Five cold goldens changed in S38; only twocge and elec match today. **`tricp` is a conditional future candidate** — abort removed, blocked only by capacity — so any answer is *"of the models testable today"*. Two structural limits recorded: `polygon` has **no provenance entry** (the named precedent is not auditable), and a pre-S38 misclassification is not addressable by design.

**Not decided here**, deliberately — see the brief's §7.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# The cold emits changed in their landing commits (NOT the presolve variants)
git show --numstat 204f35ac -- data/gamslib/mcp/twocge_mcp.gms
git show --numstat 82b91c94 -- data/gamslib/mcp/elec_mcp.gms

# What changed in twocge's cold emit
git diff 204f35ac^ 204f35ac -- data/gamslib/mcp/twocge_mcp.gms | grep '^+' | head

# The precedent model's shape today
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
for m in d['models']:
    if m['model_id'] in ('polygon','twocge','elec'):
        s=m['mcp_solve']; c=m['solution_comparison']; v=m['convexity']
        print(f\"{m['model_id']:8s} cvx={v['status']:16s} {s['outcome_category']:26s} match={c.get('comparison_status')}\")"

# Provenance file state and the mechanical proxy it must NOT be confused with
.venv/bin/python scripts/sprint_audit/floor_tracker.py
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
cand=[m for m in d['models'] if m.get('convexity',{}).get('status') in ('verified_convex','likely_convex')]
match=[m for m in cand if m.get('solution_comparison',{}).get('comparison_status')=='match']
cold=[m for m in match if not m.get('mcp_solve',{}).get('presolve_required')]
print('mechanical proxy (NOT the floor):', len(cold))"

# Decision package exists and states both answers with their consequences
test -f docs/planning/EPIC_4/SPRINT_39/FLOOR_DECISION_BRIEF.md && \
  grep -cE "^## |73|75" docs/planning/EPIC_4/SPRINT_39/FLOOR_DECISION_BRIEF.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/FLOOR_DECISION_BRIEF.md` — one page: the evidence, the counter-argument, both answers' consequences, and the exact edit each implies
- A sweep result stating whether any **third** model qualifies under the same reading
- Draft `floor_provenance.json` entries, ready to apply if the answer is 75
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3

### Acceptance Criteria

- [x] Both cold-emit changes re-verified **from git**, not from prose
- [x] The sweep for additional qualifying models is complete and its result stated
- [x] The counter-argument for 73 is stated fairly, including twocge's convexity and cold-solve behaviour
- [x] Draft provenance entries written with `limb`, `since_sprint`, `evidence`, `pr`
- [x] Downstream reports needing re-baselining are enumerated
- [x] Sprint 39's acceptance criteria are restated under each answer
- [x] The brief names the single question the owner must answer
- [x] Unknowns 1.1, 1.2, 1.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: dyncge Second-Defect Diagnosis & Layer Trace (P2)

**Status:** ✅ COMPLETE (2026-08-30)
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Time Spent:** 5 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

### Objective

Take dyncge's `CASE_B` residual from a *symptom* to a *located defect with a named layer*, and author its Phase-0 acceptance gate — so Sprint 39 Day 1 starts implementing rather than diagnosing.

### Why This Matters

P2 is **the sprint's only new diagnosis** — *as scoped. Task 4 refuted that: the mechanism is the already-tracked #1381 phantom-IndexOffset family (camcge #1354, cesam2 #1355). What is new is the **instance**, and specifically that dyncge is the family's first **silent** case — every prior member announced itself with a PATH `$141` compile failure. See Unknown 2.3.* — and dyncge is precisely the model whose previous gate mis-scoped: `ISSUE_1693` demanded *"new logic rather than a widened condition-lift"* for a diagonal-triviality test that **had existed since #942** and was merely applied to inequalities. Reusing it cost ~40 lines of extraction.

Sprint 38's most transferable finding is that **three of four Phase-0 gates named the wrong layer**. A gate authored in prep, from a trace rather than an inspection, is the mitigation.

### Background

Fixing #1693's empty-pair abort revealed a defect it had been **masking**:

```
verdict: CASE_B — emit_bug
max-residual row: stat_pf(CAP,SRV)   rel = 6.22e-02   (tol 1e-3)
top: stat_pf(CAP,SRV) · stat_pq(HMN) · stat_pf(LAB,SRV) · stat_pf(LAB,HMN) · stat_pf(CAP,LMN)
dual transfer: CONSISTENT
```

Warm-started at the NLP's own KKT point, dyncge's stationarity rows do **not** evaluate to zero. The cold MCP solves to `MODEL STATUS 1 Optimal` at **381401.119** against the NLP's **539570.5027** — a **29.3 %** mismatch. The presolve retry also fails to match (`0/1`), so **there is no spurious match to adjudicate**.

The residual concentrates on the **`pf`/`pq` block, not `eqpf2`** — so this is a new diagnosis, and #1693 closes on its own terms.

**Relevant precedent:** elec's fix (S38 D12) required **two** defects in two files — one in `src/ad/derivative_rules.py` (upstream of stationarity entirely) and one in a different function of `stationarity.py`. `CASE_A` is what validated it; `CASE_B` is what refused dyncge. **A non-erroring emit is not a pass.**

### What Needs to Be Done

1. **Re-reproduce the residual** on current `main` and confirm the top rows (Task 2 dependency).
2. **Hand-derive the KKT shape** for `stat_pf` and `stat_pq` from dyncge's source — what *should* those rows contain? This is the step that distinguishes a wrong coefficient from a missing term.
3. **Compare the emitted rows against the hand derivation**, term by term, for the top residual instances.
4. **Trace the defect to a LAYER, then a site** — parser / IR / AD / KKT / emit. **Start from `stationarity.py` and the AD entry points and work outward**; do not begin at the emitter. Record which layer and why.
5. **Check whether the mechanism already exists elsewhere** — the S38 lesson. Is this a known shape (a repeated domain, an alias-root collision, a positional lift) wearing a new model's name? Cross-check against Task 7's survey if it has landed.
6. **Author the Phase-0 acceptance gate** in a new issue: hand-derived shape, expected emit pattern, fail-before/pass-after with the **`CASE_A` requirement**, leak-gate expectation, determinism, and a **named layer with a one-line justification**.
7. **Decide whether `CASE_A` is even reachable.** dyncge may be non-convex like elec, in which case the honest target is a *documented* divergence with `modelstat` asserted, not a match. **State this before the sprint, not during it.**

### Changes

- **NEW** `docs/issues/ISSUE_1714_dyncge-phantom-indexoffset-stat-pf.md` + GitHub issue **#1714** — full Phase-0 gate with all four required subsections, a hand-derived KKT shape, and a **named layer**
- `KNOWN_UNKNOWNS.md` — **2.1 🔶 PARTIALLY WRONG**, **2.2 ✅ VERIFIED**, **2.3 ❌ WRONG**, **2.4 ✅ VERIFIED**
- `CHANGELOG.md` — Sprint 39 Prep entry

### Result

✅ **COMPLETE — the defect is located, and it is not a new one.**

**The defect.** `eqXp(i)`'s index `i` is free and unrelated to the head's `(h,j)`, so `stat_pf(h,j)` must carry `sum(i, …·nu_eqXp(i))`. The emit instead produces the diagonal plus manufactured offsets `nu_eqXp(j±1..3)`, each gated on **`$(ord(h) = k)`** — a guard on the **factor** index for a sum over the **goods** index. `h` = {CAP, LAB} has 2 members, so `ord(h)=3` terms are **dead** and each row keeps a different wrong subset. dyncge's source contains **no lead/lag at all**; every offset is manufactured. `eqII` is corrupted identically (CAP only), explaining why CAP rows carry the largest residual while LAB rows are also wrong.

**Layer: KKT / stationarity** — `src/kkt/stationarity.py` ~7107–7131, the #1081 dimension-mismatch branch. Not the emitter (which prints faithfully) and not AD (per-term derivatives verify by hand, including the `eqM`/`eqD` chain rules). Reached because `Alias (i,j)` makes `i` and `j` share a set root, so a free equation index is mistaken for a shifted head index.

**The control that made it decisive:** `stat_pq` is **correct** — all seven pq-bearing equations present, every coefficient verified term-by-term, **0** phantom refs, **0** `ord()` guards — because it is 1-D head / 1-D equation and never enters the dim-mismatch path.

**⚠ The mechanism is already known (2.3 refuted the "new diagnosis" framing).** This is the phantom-IndexOffset / plain-alias + dim-mismatch family tracked by **#1381** (camcge #1354, cesam2 #1355). **But dyncge is the first known SILENT instance:** every prior member was found via a PATH `$141` compile failure, whereas dyncge's guards keep the phantom references in range, so it compiles, solves to `MS-1`, and is wrong by 29.3 % with no diagnostic. **#1381's "at minimum 13 affected models" therefore counts only the models that failed loudly** — the family's blast radius is plausibly larger. A structural search (`nu_X(idx±k)` beside an `ord(…)=k` guard) is recommended follow-up.

**`CASE_A` reachability is NOT asserted.** It is the right target, but a second-order non-convexity beneath the offset defect would be invisible until the offsets are fixed — and elec's verdict changed from `CASE_B` to `CASE_C_OBJDEF` as the classifier improved. The REPLAN is **pre-registered** in #1714 rather than left to be discovered mid-sprint.

**#1693 closes cleanly** — a different mechanism in a different place, masked by the abort rather than caused by it.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# The residual, re-derived
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/dyncge.gms | tail -10

# The emitted rows under scrutiny
grep -n "^stat_pf(" data/gamslib/mcp/dyncge_mcp.gms | cut -c1-200
grep -n "^stat_pq(" data/gamslib/mcp/dyncge_mcp.gms | cut -c1-200

# Their source counterparts
grep -nE "eqpf|eqpq|pf\(|pq\(" data/gamslib/raw/dyncge.gms | head -20

# Convexity + the reference objective the match would have to reach
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
m=[x for x in d['models'] if x['model_id']=='dyncge'][0]
print('convexity:', m['convexity']['status'], '| NLP obj:', m['convexity']['objective_value'])
print('MCP:', m['mcp_solve']['outcome_category'], '| obj:', m['mcp_solve']['objective_value'])"

# The NEW dyncge CASE_B issue exists and its Phase-0 gate names a LAYER.
# Two traps here. (a) No 2>/dev/null: a missing or renamed doc must announce
# itself, not read as a clean "no output". (b) An `*dyncge*pf*` glob FALSE-PASSES
# on ISSUE_1693 -- the CLOSED Sprint 38 empty-pair defect -- because its slug
# contains "eqpf2". Exclude it explicitly, or this step reports a gate that
# belongs to a different, already-closed defect.
found=$(find docs/issues -name "ISSUE_*dyncge*.md" ! -name "ISSUE_1693_*")
if [ -z "$found" ]; then
  echo "NO new dyncge CASE_B issue doc yet (expected until Task 2 lands it)"
else
  printf '%s\n' "$found" | while IFS= read -r f; do
    echo "== $f"; grep -A3 "^## Phase 0" "$f" | head -12
  done
fi
```

### Deliverables

- A new `docs/issues/ISSUE_1714_dyncge-phantom-indexoffset-stat-pf.md` with a complete Phase-0 acceptance gate, including a **named layer** *(written as `ISSUE_<n>_dyncge-*.md` when the task was scoped; the number was assigned on filing)*
- A hand-derived KKT shape for `stat_pf` / `stat_pq` and a term-by-term comparison against the emit
- A stated position on whether `CASE_A` is reachable, or whether a documented divergence is the honest target
- A cross-check result: is this mechanism already known under another name?
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

### Acceptance Criteria

- [x] The residual re-reproduced on current `main` with its top rows confirmed
- [x] The KKT shape hand-derived from source before any code reading
- [x] The defect traced to a **layer** with a written justification, starting from AD/KKT rather than the emitter
- [x] A Phase-0 gate authored with the **`CASE_A` requirement** as its accept criterion
- [x] The "does this mechanism already exist?" check performed and its answer recorded
- [x] A REPLAN exit defined: what evidence would say `CASE_A` is unreachable
- [x] `#1693` confirmed closeable on its own terms, not widened
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: lnts Fingerprint Reproduction & Runtime-Probe Design (P3)

**Status:** ✅ COMPLETE (2026-08-31)
**Priority:** Critical
**Estimated Time:** 4-6 hours
**Time Spent:** 4.5 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 3.1, 3.2, 3.3

### Objective

Reproduce lnts's failure from anchored GAMS diagnostics, design the **runtime bound probe** that would confirm or refute the two-`.fx`-mechanism hypothesis, and trace the fix surface — because none of the three has ever been done.

### Why This Matters

lnts is the one Sprint-38 P8 candidate whose budget never arrived, so **both its mechanism and its fix surface are untraced**. Its stated surface — the `fix_rhs = "0"` fallback in `emit_gams.py` — is the *emitter*, which is exactly where three of Sprint 38's four gates wrongly pointed.

The plan requires confirmation by **runtime bound probe, not a source read**, because the claim is about the emitted model's bounds *at solve time*. A source read can show two mechanisms exist; only a probe shows they collide.

### Background

**The hypothesis, as banked and never tested:** two `.fx` mechanisms act on the same cells. The correct one emits

```gams
y_fx_y2_h50..  y("y2","h50") - 5 =E= 0;
```

while a blanket pruned-instance zeroing fires on exactly those cells, giving `y.lo = y.up = 0` against equations demanding **5** and **45** — hence **MS-4 at iteration 0**. The named surface is the `fix_rhs = "0"` fallback, *"the same shape as the Sprint-33 P6 fix"*.

**`cesam` is NOT the same defect and must not be batched with it.** Sprint 38 checked rather than assumed: cesam shows MS-4 at 0 iterations — the same *signature* — but has **0 `_fx_` equations**, so lnts's mechanism cannot apply. This is the single most useful thing prep can repeat: **a shared signature is not a shared mechanism.**

**The §4.1 reproduction criteria** that every Sprint-38 P8 candidate had to meet: anchored `^****` GAMS diagnostics (a `.lst` contains echoed source too); a terminal state read from **GAMS's own line**; **runtime observation** for runtime properties; and **a passing negative control**.

### What Needs to Be Done

1. **Re-emit lnts** and confirm the fresh emit is byte-identical to its committed golden — so the measurement describes the golden.
2. **Reproduce the failure** from a scratch directory: anchored `^****` diagnostics, the terminal state from GAMS's own line, and the model status with its iteration count.
3. **Confirm both `.fx` mechanisms are present in the emit** — locate the `y_fx_*` equation(s) and any blanket zeroing that targets the same tuples.
4. **Design the runtime bound probe.** The probe must read the *effective* bounds GAMS computes at solve time (e.g. a `display y.lo, y.up;` injected after all fixing, or the equation listing's bound columns), and show the contradiction against the `_fx_` equation's demanded value. **Specify exactly what output would confirm the hypothesis and what would refute it.**
5. **Trace the fix surface from `stationarity.py` / the AD entry points outward**, and only then consider the emitter. Record the layer.
6. **Author the Phase-0 gate** with the probe as the fail-before evidence and a passing negative control.
7. **Define the REPLAN exit:** if the probe shows no contradictory bounds, the hypothesis is refuted — bank the real mechanism and do not widen the track.

### Changes

- **NEW** `docs/planning/EPIC_4/SPRINT_39/LNTS_PROBE_DESIGN.md` — the runtime bound probe, with confirm/refute criteria **written before execution**
- `docs/issues/ISSUE_1694_lnts-contradictory-fx-mechanisms-blanket-zeroing.md` — Task 5 addendum: runtime confirmation, the **corrected fix surface**, the named layer, the existing-machinery note, and the S33-P6 analogy verdict
- `KNOWN_UNKNOWNS.md` — **3.1 ✅**, **3.2 ❌ WRONG**, **3.3 ✅**
- `CHANGELOG.md` — Sprint 39 Prep entry

### Result

✅ **COMPLETE — the hypothesis is confirmed and the banked fix surface is refuted.**

**The collision is now a runtime fact, not a source reading.** The probe was designed with confirm/refute criteria fixed in advance, then run: `y("y2","h50")` and `y("y3","h50")` carry `_fx_` equations demanding **5** and **45**, and their **effective bounds at solve time are `lo = up = 0`**. All three CONFIRM criteria hold — including that the contradiction is *exactly* zero (so it is the blanket, not some third writer) and that the `D = 0` control `y("y4","h50")` is consistent (so the probe is not over-reporting). No refute criterion fires.

**⚠ The banked fix surface is wrong.** The carryforwards named the `fix_rhs = "0"` fallback (`emit_gams.py:3060–3061`) and flagged it as untraced. Instrumented: line 3061 fired **once, for variable `u`**, taking the `u.lo(h)` branch, and the `"0"` fallback printed **nothing**. The blanket that pins `y` is emitted at **line 3121** (with a wider first guard at 3005). Day 1 would have opened on a branch that never executes.

**Layer: EMIT** — and unlike three of four Sprint-38 gates, the emitter genuinely *is* the layer here, established by **running the code** rather than reading it. The site fixes pruned instances **without consulting `var_def.fx_map`**, so it cannot see that a cell already carries an authoritative `_fx_` equation.

**The machinery already exists** — `_fx_eq_name()` (`emit_gams.py:711`), the `suppressed` set at `emit_gams.py:920` doing the same reasoning in the opposite direction, and `var_def.fx_map` (`partition.py:180`). The fix is a lookup, not new machinery. The **Sprint-33 P6 analogy is structurally genuine** (guard an emission on the state of another emitted artifact) — though it was cited alongside a *location* that proved wrong.

**REPLAN exit** written before the result and did not fire.

### Verification

```bash
REPO="$(git rev-parse --show-toplevel)"
# GAMS writes scratch files to cwd -- run from a scratch dir, never the repo root
mkdir -p /tmp/lnts_prep && cd /tmp/lnts_prep

# Fresh emit == committed golden (absolute interpreter + PYTHONPATH: cwd is NOT the repo)
PYTHONPATH="$REPO" "$REPO/.venv/bin/python" -m src.cli "$REPO/data/gamslib/raw/lnts.gms" -o lnts_mcp.gms
diff -q lnts_mcp.gms "$REPO/data/gamslib/mcp/lnts_mcp.gms" && echo "✅ golden-identical"

# Reproduce, reading counts from GAMS's own lines (anchored)
gams lnts_mcp.gms lo=0 errmsg=1 > /dev/null 2>&1; echo "rc=$?"
grep '^\*\*\*\*' lnts_mcp.lst | sed 's/[0-9][0-9]*/N/g' | sort | uniq -c | sort -rn | head
# Each alternative anchored to ITS OWN prefix: STATUS lines start with ****,
# but ITERATION COUNT starts with a single space -- folding both under ^\*\*\*\*
# would silently drop every iteration line.
grep -E '^(\*\*\*\* (SOLVER|MODEL) STATUS|[[:space:]]*ITERATION COUNT)' lnts_mcp.lst

# Both .fx mechanisms present?
grep -n "y_fx_" lnts_mcp.gms | head
grep -nE "^y\.fx\(|^y\.lo\(|^y\.up\(" lnts_mcp.gms | head

# The values the _fx_ equations demand
grep -oE "y\(\"[^\"]+\",\"[^\"]+\"\) - [0-9.]+ =E= 0" lnts_mcp.gms | head

cd "$(git rev-parse --show-toplevel)"
# Guard against batching cesam with it: cesam must have 0 _fx_ equations
grep -c "_fx_" data/gamslib/mcp/cesam_mcp.gms || echo "0 (mechanism cannot apply)"

# Probe design + gate exist
test -f docs/planning/EPIC_4/SPRINT_39/LNTS_PROBE_DESIGN.md && echo "✅ probe design"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/LNTS_PROBE_DESIGN.md` — the runtime bound probe, with confirm/refute criteria stated in advance
- A reproduced fingerprint meeting all four §4.1 criteria, including a passing negative control
- A traced fix surface with its **layer** named, reached from AD/KKT outward
- A Phase-0 gate on the lnts issue, or the issue created if none exists
- A written REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3

### Acceptance Criteria

- [x] Fresh emit confirmed byte-identical to the committed golden
- [x] Failure reproduced with **anchored** `^****` diagnostics and a terminal state from GAMS's own line
- [x] Both `.fx` mechanisms located in the emit, or the hypothesis marked unconfirmed
- [x] The runtime probe designed with **confirm and refute criteria written before it is run**
- [x] Fix surface traced from `stationarity.py`/AD outward, with the layer named
- [x] A passing negative control specified
- [x] `cesam` explicitly excluded from the track, with the 0-`_fx_` reason restated
- [x] REPLAN exit defined
- [x] Unknowns 3.1, 3.2, 3.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: sarf's Four Call Sites — Cost Attribution & Atomicity Plan (P4)

**Status:** ✅ COMPLETE (2026-08-31)
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Time Spent:** 5 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Confirm the four untouched call sites still exist, attribute the remaining wall-clock cost to them by measurement, and produce an atomicity plan — so P4's 20–28 h is spent implementing rather than re-profiling.

### Why This Matters

P4 is **Sprint 39's only KPI mover** (+1 Translate → 136). Its Sprint-38 change is already in `main` and **emit-preserving**, but sarf still ran **28 m 40 s** against a **≤300 s** gate. The remaining cost is described as *located, not suspected* — that claim is the whole basis for the estimate and has not been re-checked since Sprint 38 Day 7.

Both `stationarity.py` and `emit_gams.py` changed materially in Sprint 38 (Days 9, 11, 12), so the recorded locations may have moved.

### Background

**Sprint 38 Day 7's measured findings:**

- The referenced-instance filter works as Day 6 measured and is **emit-preserving** — the leak gate was clean over 163 goldens at the time, `make test` green.
- sarf still does not complete: **killed at 28 m 40 s** against a **≤300 s** gate (owner-revised 2026-08-18 from the unreachable "single-digit seconds", because the O(active) projection measured **~141 s** — 1,183 rows × 398 cols at 3,343 diff/s).
- **The remaining cost is at four call sites the change deliberately did not touch.**

**Two lessons that bound the approach:**

1. ***Narrowing a loop's body does not help if the narrowing itself is O(the thing you removed).*** The first attempt traded 436 M differentiations for 436 M dict lookups and still did not terminate; the fix was a precomputed position map, O(|referenced| log |referenced|).
2. **Three of the four defects found on the way produced a *wrong answer* rather than a crash** — which is the case for why this cannot be landed on inspection.

**Two gate peculiarities, not to be rediscovered:** `make leak-check MODEL=sarf` reports `NO-OP` because sarf has no golden — the real gate is `make check-goldens` at full scope **plus sarf newly producing a golden (186 → 187)**. And **sarf cannot be its own fixture**: at 369,024 declared columns the fail-before state does not terminate.

### What Needs to Be Done

1. **Locate the four call sites on current `main`** and record their present file:line, noting any that moved since Sprint 38 Day 7.
2. **Attribute cost by measurement, not by reading.** Profile a bounded sarf run and report what fraction of wall-clock each of the four accounts for. **If the four do not account for the bulk, that is a finding that changes P4's estimate and must be reported now.**
3. **Re-validate the O(active) projection** — does ~141 s still hold, given the corpus and the emit changed?
4. **Write the atomicity plan.** Which changes must land as one unit, and why a partial landing is an *inconsistent MCP* rather than partial progress. Enumerate the corpus-safety call sites that must be provably unperturbed.
5. **Design the fixture.** sarf cannot be its own fixture; specify a corpus-free surrogate that exercises the same shape at a size that terminates.
6. **Restate the Phase-0 gate** with the ≤300 s threshold, the symbolic-index assertion, byte-stable golden, determinism ×3, and `--min-scope` raised to 187.

### Changes

- **NEW** `docs/planning/EPIC_4/SPRINT_39/SARF_CALLSITE_PLAN.md` — the four sites at their current locations, the measured cost attribution, the re-validated O(active) projection, the atomicity plan, the verified surrogate, the restated Phase-0 gate, and a REPLAN exit
- `KNOWN_UNKNOWNS.md` — Unknowns **4.1 ✅ VERIFIED**, **4.2 ❌ WRONG**, **4.3 🔶 PARTIALLY WRONG**, **4.4 🔶 PARTIALLY WRONG**
- `CHANGELOG.md` — Sprint 39 Prep entry

### Result

✅ **COMPLETE — and the finding is that P4's premise does not survive measurement.**

**The sites are where they were recorded** (4.1 ✅): `gradient.py:287`, `gradient.py:453`, `complementarity.py:367`, `complementarity.py:512`, all at their exact Day-7 lines, with **0** commits to either file since the anchor `949a4587`. Located by symbol, not by line number. ⚠ But there are **six** callers of `enumerate_variable_instances`, not four — `constraint_jacobian.py:80` and `index_mapping.py:634` are the two the Day-7 filter already covers.

**The cost is not at those sites** (4.2 ❌). A capped 900 s `cProfile` of a sarf translate:

| frame | cumulative | % | ncalls |
|---|---|---|---|
| `compute_constraint_jacobian` | **637.9 s** | **70.9 %** | 1 |
| `_diff_sum` | 513.6 s | 57.1 % | 1,641,023 |
| `_is_concrete_instance_of` | 306.2 s | 34.0 % | 13,344,770 |
| `compute_objective_gradient` | 156.9 s | 17.4 % | 1 |
| **`enumerate_variable_instances`** | **4.4 s** | **0.5 %** | **40** |

The charitable reading — *the four emit the instances later differentiated* — fails too: the 70.9 % path takes its columns from `constraint_jacobian.py:80`, which is **not** one of the four and which Day 7 already narrowed. **And `gradient.py:453` is dead code** — `compute_gradient_for_expression` has no production caller, confirmed by instrumentation. So the lever is **three live sites** with an honest upper bound of 17.4 %, not four sites accounting for the bulk.

**The projection's rate holds; its scope premise does not** (4.3 🔶). 1,183 × 398 = 470,834 at 3,343/s ⇒ 141 s is arithmetically right, and the measured 1,146/s profiled implies ~3,439/s at a 3× cProfile overhead. But the run performed **1,031,810** differentiations — 2.2× the projection's entire budget — without finishing. The ≤300 s gate's headroom is intact **only if** the narrowing reaches 398 active columns, a conditional that has never been tested.

**The surrogate was built and verified, not specified** (4.4 🔶): `task(g,t,mn,mn)` at 96 columns hits **3 of 4** sites; a first attempt without per-element `.lo`/`.up` overrides hit only 1. The fourth is **unreachable by construction**, because nothing calls it.

**Routed to the owner, not decided here.** P4 is the sprint's only KPI mover; re-scoping it onto the differentiation path, keeping it with a much smaller expected gain, or deferring are decisions with different costs and different KPI consequences. `SARF_CALLSITE_PLAN.md` §8 states the options.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# The four call sites — do they still exist where recorded?
# ⚠ CORRECTED by Task 2 and re-corrected here. The original form grepped
# constraint_jacobian.py / index_mapping.py / stationarity.py, none of which
# holds any of the four; and its "these files moved in Sprint 38" rationale is
# inverted — gradient.py and complementarity.py did NOT move (0 commits since
# 949a4587), while the files it grepped did. Symbols, not line numbers:
# ⇒ gradient.py:287, gradient.py:453, complementarity.py:367, complementarity.py:512
# ERE with `[[:space:]]*`, NOT a fixed-string "= enumerate...": the fixed form is
# brittle to formatting and would miss `instances=enumerate_variable_instances(`.
grep -nE "=[[:space:]]*enumerate_variable_instances\(" \
  src/ad/gradient.py src/kkt/complementarity.py

# POSITIVE CONTROL for that anchor — run it, do not assume it. ⇒ 3
# (The fixed-string form scores 1 of 3 here. That is the whole reason for the ERE.)
printf 'x = enumerate_variable_instances(a)\ny=enumerate_variable_instances(a)\nz  =  enumerate_variable_instances(a)\n' \
  | grep -cE "=[[:space:]]*enumerate_variable_instances\("

# ⚠ There are SIX callers, not four. The other two — constraint_jacobian.py:80
# and index_mapping.py:634 — are the ones the Day-7 referenced-instance filter
# already covers. Count them, so the difference is visible rather than assumed.
grep -rnE "=[[:space:]]*enumerate_variable_instances\(" src/ | sort   # ⇒ exactly 6

# CROSS-CHECK that the `=` anchor is not hiding a site: list every OTHER mention
# and eyeball it. ⇒ 8 — 3 imports, 1 def, 3 `>>>` doctest examples, 1 prose line
# (gradient.py:48). An unanchored grep picks all 8 up and reports 14 "callers".
grep -rn "enumerate_variable_instances" src/ \
  | grep -vE "=[[:space:]]*enumerate_variable_instances\("
# ⚠ Known blind spot, accepted deliberately: the `=` anchor cannot see a bare
# statement call, `enumerate_variable_instances(x)` with the result discarded.
# The function exists to return a list, so such a call would be dead — but if
# the cross-check above ever returns something that is not an import, a def, a
# doctest or prose, that is the case, and the count is wrong.

# gradient.py:453 is DEAD CODE in the translate path — its enclosing function has
# no production caller. Expect hits only in tests and in its own docstring.
grep -rn "compute_gradient_for_expression" src/ tests/ | grep -v "def compute_gradient_for_expression"

# sarf has no golden (so leak-check will report NO-OP — expected, not a failure)
ls data/gamslib/mcp/sarf_mcp.gms 2>/dev/null || echo "no golden — leak-check NO-OP is expected"

# Bounded profile (do NOT run to completion; it does not terminate)
# timeout is intentional: we want the profile, not the result
# Drives an actual translate (NOT just an import -- an import-only profile
# captures ~0.4s of module load and none of the call sites we need to attribute).
# cProfile dumps the file from a `finally`, so the profile survives the alarm.
REPO="$(git rev-parse --show-toplevel)"
PYTHONPATH="$REPO" "$REPO/.venv/bin/python" -c "
import cProfile, pstats, sys, signal
sys.setrecursionlimit(50000)
from src.cli import main
def bail(*a): raise TimeoutError
signal.signal(signal.SIGALRM, bail); signal.alarm(900)
try:
    cProfile.run(
        'main(args=[\"$REPO/data/gamslib/raw/sarf.gms\",\"-o\",\"sarf_mcp.gms\"],'
        ' standalone_mode=False)', '/tmp/sarf.prof')
except (TimeoutError, SystemExit):
    pass
pstats.Stats('/tmp/sarf.prof').sort_stats('cumulative').print_stats(15)
"
# ⚠ Bound-vs-reach: at a 10 s bound sarf is still inside parse_model_text, so the
# four AD/KKT call sites are NOT yet on the stack. Raise the alarm until the
# profile shows frames past the parser, or the attribution will be all parsing.
# 900 s is the bound the SARF_CALLSITE_PLAN.md §2 figures were measured at;
# parse completes at 33.1 s, so the remaining 867 s is AD/KKT.

# The plan exists and names the four sites + the atomic unit
test -f docs/planning/EPIC_4/SPRINT_39/SARF_CALLSITE_PLAN.md && \
  grep -cE "call site|atomic|surrogate" docs/planning/EPIC_4/SPRINT_39/SARF_CALLSITE_PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/SARF_CALLSITE_PLAN.md` — the four sites at their **current** locations, with measured cost attribution
- A re-validated O(active) projection, or a corrected one
- An atomicity plan naming the unit and the corpus-safety sites that must be unperturbed
- A corpus-free surrogate fixture specification
- The restated Phase-0 gate
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [x] All four call sites located on current `main`, with any movement since S38 D7 recorded — none moved (0 commits to either file since `949a4587`); located by symbol
- [x] Cost attributed **by measurement**; if the four do not dominate, that finding is reported and P4's estimate revised — **they do not** (0.5 %), reported in `SARF_CALLSITE_PLAN.md` §2 and §8
- [x] The ~141 s O(active) projection re-validated or corrected — rate survives, scope premise does not (§3)
- [x] The atomic unit defined, with the inconsistent-MCP argument written out (§6)
- [x] A surrogate fixture specified (sarf cannot be its own) — specified **and run**; 3 of 4 sites, the 4th unreachable (§5)
- [x] The gate restated with ≤300 s, symbolic-index assertion, `--min-scope` → 187 (§7)
- [x] A REPLAN exit defined for a timeout re-trigger (§7)
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Positional-vs-Declared-Domain Site Survey (P5)

**Status:** ✅ COMPLETE (2026-09-01)
**Priority:** High
**Estimated Time:** 4-5 hours
**Time Spent:** 5 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Enumerate every site that resolves an index **positionally against a declared domain**, and classify each by whether it mishandles a domain that repeats a symbol — producing the catalog P5's audit consumes.

### Why This Matters

This is the defect class that produced **wrong answers in two different layers on two consecutive days** in Sprint 38, and **neither instance crashed at the point of the defect** — both surfaced far away, found while chasing unrelated symptoms. That is precisely the profile of a class worth surveying rather than waiting to trip over.

A survey is also the cheapest possible form of this work: P5 is budgeted 12–16 h and is **0-bucket by design**. Prep produces the catalog; the sprint produces the guards and tests.

### Background

**A repeated symbol in a *declaration* domain is harmless until something resolves an index positionally against it.**

- **tricp (S38 D11)** — `slp(n,n)` as a **variable** domain. In a GAMS equation *definition*, a repeated controlling index binds to the **same element**, so the head generated **zero rows** and 108 on-edge columns went unmatched. Fixed by `dedupe_repeated_variable_domains`, a **pre-differentiation IR pass**, because the body is built positionally from the same tuple and the collapse reached back into the objective gradient.
- **elec (S38 D12)** — `Set ut(i,i)` as a **set** domain. `_replace_indices_in_expr`'s `Sum` branch overlays `{idx: idx}` self-mappings so AD names like `j__` survive — **which also puts them in `element_to_set`**, the very membership the `SetMembershipTest` branch used to decide *"concrete element ⇒ resolve positionally"*. Both declared positions being `i`, the guard collapsed to `ut(i,i)` — the diagonal of a **strictly upper-triangular** set, identically false, **silently dropping half the gradient**.

**Corpus incidence, measured in S38:** exactly **two** models have a repeated-symbol *variable* domain (`tricp`, `ferts`). The *set*-domain case was not surveyed at all — elec was found by chasing a division-by-zero.

> **⚠ HISTORICAL — both figures in the paragraph above were SUPERSEDED by this task's own Result below (2026-09-01).** The variable-domain count is **five** (`ferts`, `lop`, `maxmin`, `sarf`, `tricp`), not two; the set-domain case is now surveyed and is **16** models, with **21** more carrying a repeated *parameter* domain. The paragraph is kept as written because it is the premise Task 7 was scoped against.

**Known related machinery** worth including in the survey: `_remap_condition_to_domain` (#1062/#1350's parent-set lookup, which needed consume-once matching), `_replace_indices_in_expr`'s `SetMembershipTest` branch, and any `smt_domain[pos]` / `var_domain[pos]` positional indexing.

### What Needs to Be Done

1. **Enumerate the sites.** Grep `src/kkt/stationarity.py` and the AD layer for positional resolution against a declared domain — `domain[pos]`, `smt_domain[pos]`, `var_domain[pos]`, `set_declared_domain[pos]`, and any first-match scan over a domain tuple.
2. **For each site, determine behaviour under a repeated domain.** Does it collapse, and does the collapse produce a wrong answer or merely a harmless rename?
3. **Measure corpus incidence per shape** — how many models have a repeated-symbol *set* domain (the elec case), as distinct from the two with repeated *variable* domains.
4. **Classify each site**: already guarded / needs a guard / needs only a test / not reachable with a repeated domain. **The last category needs an argument, not an assertion.**
5. **Rank by blast radius** — a site reached by every model is worth more than one reached by two.
6. **Specify the property test** that would cover the class generically, so the audit adds a test per site plus one property test for the shape.

### Changes

- **NEW** `docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` — 21 primary sites classified and ranked by **measured** blast radius, corpus incidence by symbol kind, two property specs, and a ranked recommendation
- **NEW** `docs/planning/EPIC_4/SPRINT_39/artifacts/` — the 9 measurement scripts behind every figure, so the survey is reproducible from the repo rather than from prose. `mutation_controls.py` re-derives §5's claims and **exits non-zero if either property is vacuous**. Outside the quality gate's scope (`src/`, `tests/`); one-off prep scripts, not maintained tooling
- `KNOWN_UNKNOWNS.md` — Unknowns **5.1 🔶**, **5.2 ❌**, **5.3 🔶**
- `CHANGELOG.md` — Sprint 39 Prep entry

### Result

✅ **COMPLETE — and three inherited figures are wrong, one of them a live correctness finding.**

**The catalog (5.1 🔶).** "Resolves positionally against a declared domain" is too wide to filter on — **173** subscripted-domain expressions and **33** `zip`-against-a-domain sites exist, and almost none can break, because `zip`/`enumerate` pair position *i* with position *i*. What breaks is a **symbol → (position | value)** step: **21 primary sites**, enumerated by AST scan. **9 ALREADY GUARDED · 7 NEEDS A TEST · 4 NEEDS A GUARD · 1 NOT REACHABLE (in sample)**. 21 is auditable inside P5's 12–16 h, so the assumption holds — **but the reach is not in `stationarity.py`**: the top three sites are `constraint_jacobian.py:1466/1513` (12/15 and 11/15 sampled models) and `empty_equation_detector.py:127` (10/15). Blast radius was **measured** by `sys.settrace` line tracing over 15 adversarially chosen models — no source instrumentation, so nothing could be left in the tree.

**The organising fact.** `dedupe_repeated_variable_domains` (#1062, `cli.py:476`) runs unconditionally before differentiation and iterates `model_ir.variables` **only**. So the **variable**-domain sub-shape is globally neutralised and the **set** (16 models) and **parameter** (21 models) sub-shapes are not. Most `NEEDS A TEST` verdicts are "safe today, but by something upstream and incidental".

**Corpus incidence (5.2 ❌ WRONG).** Two independent methods — a 219-model IR census and a source prescan — agreeing on 24, union 44. **Sets 16 · params 21 · variables 5 · equations 0; 34 models total, 25 in the 142 convex candidates.** The assumption that the set shape is "as rare as the variable shape" is wrong by **8×**, and the banked **"exactly two models (tricp, ferts)"** for variable domains is also wrong — it is **five** (`ferts`, `lop`, `maxmin`, `sarf`, `tricp`; `lop` declares `dtr(s,s,s,s)`, a four-fold repeat). **41 of 219 models did not parse, so the per-kind figures are lower bounds** — stated, not buried.

**⚠ The live finding.** The emit-level property finds **7 violations in 5 CURRENT goldens**. `dinam`, `egypt`, `turkpow` carry repeats the **source never declared** — manufactured by our emit; `shale`, `gussrisk` carry declaration-derived ones. **11 of the 34 models match, but only `gussrisk` is in the suspect set, and its instance is latent** (an NA-guard narrowed to the diagonal, on data that is never NA). The other four are `mcp_solve: failure`, so no reported KPI is affected today.

**The property test (5.3 🔶).** One property cannot cover the class; **two** are needed. **P1** (no repeated symbol in an emitted head) is **mutation-killed** — the tricp mutant with #1062 disabled emits 4 violations — but **scores 0 on elec's pre-fix golden**, because the #1062 guard makes it trivially true for variable domains. **P2** (no repeated index in an emitted `$(...)` guard) is the complement and the one that finds live defects; its guard-scoping is load-bearing, since a naive whole-file form flags elec's legitimate declaration both before *and* after the fix. Both run in **under 3 s over 193 goldens**. A third sub-shape falls out that neither known instance showed: a manufactured repeat can be identically **TRUE** (`turkpow`) as easily as identically false, so the property must be *"the index repeats"*, not *"the guard is unsatisfiable"*.

**Routed to P5, not decided here:** the four `NEEDS A GUARD` sites are **candidates**, not confirmed defects — each needs the Day-0 trace the S38 retrospective requires, since three of four S38 gates named the wrong layer.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# Candidate sites: positional resolution against a declared domain
grep -nE "domain\[pos\]|smt_domain\[|var_domain\[|set_declared_domain\[" \
  src/kkt/stationarity.py src/ad/*.py | head -30

# First-match scans over a domain tuple (the #1350 shape)
grep -E -n "for vd in var_domain|for .* in .*_domain" src/kkt/stationarity.py | head -20

# Corpus incidence: repeated-symbol SET domains (the elec shape)
# FULL corpus by default -- the acceptance criterion is corpus incidence, and a
# sample cannot establish it. `LIMIT=N` only for fast iteration.
# Two things this must NOT do silently: swallow parse failures (a low count would
# be indistinguishable from a broken scan) and hang. 7 models exceed a 20s parse,
# so each file is individually alarm-bounded and timeouts are reported, not hidden.
# Measured at Sprint 38 close: 219 scanned | 16 hits | 34 unparsed | 7 timed out.
# Runtime ~7 min for the full corpus.
PYTHONPATH=. .venv/bin/python -c "
import sys, glob, os, signal
sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
files = sorted(glob.glob('data/gamslib/raw/*.gms'))
limit = int(os.environ.get('LIMIT', '0'))
per = int(os.environ.get('PER_FILE_TIMEOUT', '20'))
if limit: files = files[:limit]
def bail(*a): raise TimeoutError
signal.signal(signal.SIGALRM, bail)
hits, failed, slow = [], [], []
for f in files:
    signal.alarm(per)
    try:
        ir = parse_model_file(f)
        rep = {n: st.domain for n, st in ir.sets.items()
               if st.domain and len(st.domain) != len({d.lower() for d in st.domain})}
        if rep: hits.append((os.path.basename(f)[:-4], rep))
    except TimeoutError: slow.append(os.path.basename(f)[:-4])
    except Exception:    failed.append(os.path.basename(f)[:-4])
    finally:             signal.alarm(0)
print(f'scanned {len(files)} | repeated-symbol SET domain: {len(hits)} | unparsed: {len(failed)} | timed out >{per}s: {len(slow)}')
for h in hits[:12]: print('  ', h[0], dict(list(h[1].items())[:2]))
"

# Repeated-symbol domains in the emitted goldens, e.g. `e(n,n)` (known: tricp, ferts)
# NOTE: this predicate needs a BACK-REFERENCE (the two symbols must be the SAME),
# which POSIX ERE does not have -- and `\s`/`\w`/`\1` are handled differently by
# every grep. Measured on this corpus: BSD grep finds 3 sites in tricp; ugrep 7.5
# finds 0 for the same pattern, because it reads `\1` as a literal `1`. Use Python
# so the count is implementation-independent.
.venv/bin/python -c "
import pathlib, re
pat = re.compile(r'^\s+\w+\((\w+),\1\)')
for f in sorted(pathlib.Path('data/gamslib/mcp').glob('*_mcp.gms')):
    hits = [l.strip() for l in f.read_text().splitlines() if pat.match(l)]
    if hits: print(f'{f.name}: {len(hits)} site(s), e.g. {hits[0][:60]}')
"   # expect 18 files at the Sprint 38 close emit (tricp + ferts among them)

# The survey exists and classifies every site
test -f docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md && \
  grep -cE "guarded|needs a guard|needs a test|not reachable" \
    docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` — every positional-resolution site, classified and ranked by blast radius
- Corpus incidence per shape: repeated *variable* domains vs repeated *set* domains
- A property-test specification covering the class generically
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [x] Every positional-resolution site in `stationarity.py` and the AD layer enumerated — by **AST scan** over all four packages, not grep; 21 primary sites after applying the symbol→position discriminator
- [x] Each site classified, with "not reachable" cases carrying an **argument**, not an assertion — the single such verdict (`emit_gams.py:795`) is stated as **"not reachable *in sample*"**, 0 of 15, and explicitly labelled a measured absence rather than a proof
- [x] Corpus incidence measured for both shapes, not just the variable-domain one — and for a third (**parameter** domains, 21 models) that was not in the question
- [x] Sites ranked by blast radius — **measured** by `sys.settrace` over 15 models, not argued from call chains
- [x] A generic property test specified — **two** specified, because one cannot cover the class; P1 mutation-killed, P2 finds 7 live violations
- [x] The two known instances (tricp, elec) appear in the catalog and are marked already-fixed — used as the survey's **positive control**
- [x] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Presolve-Record Remedy Design (P7)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 7.1, 7.2, 7.3

### Objective

Design a **systemic** remedy covering all affected presolve-record rows — the spurious match and the dangling `mcp_file_used` references — and codify the presolve-golden adoption rule that emerged in Sprint 38.

### Why This Matters

**Match 96 is overstated by 1** and has been since Day 10, when Sprint 38 found `weapons`'s MCP had aborted while the objective read back the embedded NLP's own answer. Sprint 38 deliberately **reported rather than corrected** it, because a model-by-model fix manufactures a worse number than the one being checked.

The correction is also a KPI *fall*, which makes it exactly the kind of change that needs to be designed and explained in advance rather than discovered at close.

### Background

**Two findings sharing a population and a cause:**

1. **`weapons` is a spurious presolve match** — a presolve emit warm-starts by solving the original model inside the generated file, so if the MCP aborts, `nlp2mcp_obj_val = <objvar>.l` reads back **the NLP's own answer and matches itself**. weapons' listing held a single solve summary (the embedded NLP's, MS-2 @ 1735.5696); the MCP aborted with `EXECERROR = 1`.
2. **`mcp_file_used` dangles for 14 rows** — 13 pre-existing (exactly Day 8's Tier 2) plus `weapons`, whose presolve golden was reverted in review. The field records the artifact the solve *generated*, not a committed golden, so it points at a non-existent file for every model that solved via presolve without an adopted golden. **`weapons` is therefore in both findings**, which is part of why one remedy has to cover both.

**The tooling exists and is proven.** `scripts/sprint_audit/check_mcp_solve_attribution.py` distinguishes *"our MCP produced its own `MODEL STATUS`"* from *"only the embedded NLP did"*, using **positional attribution** — every status line belongs to the solve summary above it. It is **deliberately not keyed on `EXECERROR`**, which conflates MCP-side and NLP-side aborts and is how weapons was first reported against the wrong half of the file. Of 33 rows checked, **exactly 1** was spurious.

**The adoption rule that emerged (S38 D12):** a presolve golden is adopted only if attribution reports `MCP-SOLVED` **and** `check_presolve_divergence.py --model X` passes **and** the DB's `mcp_file_used` references it. elec's qualified; **dyncge's did not** (its retry failed) and was declined.

### What Needs to Be Done

1. **Re-count the population** (Task 2 dependency) — 14 dangling rows as measured at `8b3db6be`; confirm the count and the membership, since Day 8 and Day 12 both adopted goldens.
2. **Choose the remedy shape** and argue it: either wire the attribution check into the pipeline's record-writing so a spurious match cannot be recorded, **or** re-specify `mcp_file_used` (e.g. null unless a committed golden exists) and back-fill. **Say why the chosen one covers all rows.**
3. **Design the KPI-fall communication.** If weapons is reclassified, Match goes 96 → 95. Specify the wording that reports it **as a correction with its reason in the same sentence** — Sprint 38's close rule #2 exists because a lateral move reported alone reads as a regression.
4. **Codify the adoption rule** for CONTRIBUTING, including the weapons lesson: *a golden can pass structure/DB/NA-guard/determinism review and still not RUN* — "the emit actually executes" belongs in any adoption protocol.
5. **Specify the regression test**: a fixture whose MCP aborts must **not** be recordable as a match.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# The population, re-counted
.venv/bin/python -c "
import json, os
d=json.load(open('data/gamslib/gamslib_status.json'))
pre=[m for m in d['models'] if m.get('mcp_solve',{}).get('outcome_category')=='model_optimal_presolve']
dang=[m['model_id'] for m in pre if (f:=m['mcp_solve'].get('mcp_file_used')) and not os.path.exists(f)]
print('presolve rows:', len(pre), '| dangling mcp_file_used:', len(dang))
print(sorted(dang))"

# Attribution over the presolve population (the Day-10 census, re-run)
.venv/bin/python scripts/sprint_audit/check_mcp_solve_attribution.py 2>&1 | tail -8

# weapons specifically
.venv/bin/python scripts/sprint_audit/check_mcp_solve_attribution.py --models weapons 2>&1 | tail -5

# What Match becomes if weapons is reclassified
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
cand=[m for m in d['models'] if m.get('convexity',{}).get('status') in ('verified_convex','likely_convex')]
match=sum(1 for m in cand if m.get('solution_comparison',{}).get('comparison_status')=='match')
print(f'Match now: {match} | after reclassifying weapons: {match-1}')"

# The design exists and covers the whole population
test -f docs/planning/EPIC_4/SPRINT_39/PRESOLVE_RECORD_REMEDY.md && \
  grep -cE "all 14|systemic|adoption rule" docs/planning/EPIC_4/SPRINT_39/PRESOLVE_RECORD_REMEDY.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/PRESOLVE_RECORD_REMEDY.md` — the chosen remedy with its coverage argument
- The KPI-fall communication wording, pre-written
- The presolve-golden adoption rule, drafted for CONTRIBUTING
- A regression-test specification: an aborting MCP must not be recordable as a match
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2, 7.3

### Acceptance Criteria

- [ ] The affected population re-counted, not assumed
- [ ] A remedy chosen with a written argument for why it covers **every** row
- [ ] The Match 96 → 95 correction wording pre-written, with the reason in the same sentence
- [ ] The adoption rule drafted, including "the emit actually executes"
- [ ] A regression test specified for the aborting-MCP case
- [ ] The attribution tool's positional method is preserved — **not** re-keyed on `EXECERROR`
- [ ] Unknowns 7.1, 7.2, 7.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Consultation Reply-Integration & Follow-Up Package (P6)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 6.1, 6.2, 6.3

### Objective

Prepare **both branches** of the date-gated consultation priority — integrate a reply, or post the follow-up — so neither requires improvisation on the day.

### Why This Matters

P6 is **date-gated at 2026-09-09** and cannot be pulled earlier. Its value depends entirely on whether a reply arrives, and the failure mode is well documented: the consultation slipped **five sprints** on the absence of an owner, and re-opening the send decision is what caused each slip.

There is a second, subtler risk. The package sent on 2026-08-26 was itself corrected at send time because its banked failure description had **rotted over five carries** — `EXIT — other error` no longer reproduced. Whatever arrives in reply will be read against measurements that must be current.

### Background

**Sent 2026-08-26** to `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`, carrying three threads:

1. **rocket** — the discretized optimal-control MCP: `SOLVER STATUS 1 Normal Completion` / `MODEL STATUS 5 Locally Infeasible` after **9,241 iterations**, 0 evaluation errors; residual concentrated on `stat_step` under three of PATH's four final norms. Attached: `../SPRINT_38/ROCKET_CONSULTATION_EXTERNAL.md` + the generated MCP.
2. **The 11-model license-capacity ask** — `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `tricp`, `turkey`, all rejected at *generation* by the demo 1000-row nonlinear limit.
3. **`agreste` + `mine` as one question** — two verified-convex **LPs** whose MCPs PATH declares MS-5 *Locally* Infeasible after **9,734** / **10,662** iterations. Structurally odd for a pure LCP.

Tracked on **#1462** (rocket + the send record) and **#1443** (the LP question). **An actionable reply** is a concrete option set / `optfile`, a regularization or continuation schedule, or a named reformulation class — a diagnosis without one of those three does not unblock rocket.

### What Needs to Be Done

1. **Draft the follow-up comment** for the no-reply branch, ready to post on 2026-09-09. It must **not** re-open the send decision.
2. **Prepare the reply-integration checklist** for each thread: where a recommended option set plugs into the `--force {homotopy,multistart,optfile}` scaffold; what a license grant triggers (a single `--only-solve` batch over the 11); what an answer on the LCP question would mean for `agreste` (which has **no open owning issue** — #1068 is an earlier, closed diagnosis).
3. **Re-measure the three threads' figures** so a reply is read against current numbers, not the send-time ones.
4. **Pre-write the cohort re-test procedure** — one `--only-solve` pass, and the caveat that **`ferts`'s emit was silently wrong until S38 D11**, so *"a golden exists"* has never meant *"the golden is correct"* for this cohort.
5. **State the projection discipline explicitly:** rocket's +1 and the cohort's +11 are **not Sprint-39 projections** and must not enter acceptance criteria.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# Tracking state on both issues
gh issue view 1462 --json comments --jq '.comments | length' | sed 's/^/#1462 comments: /'
gh issue view 1443 --json comments --jq '.comments | length' | sed 's/^/#1443 comments: /'

# Re-measure the LP-question figures
for m in agreste mine; do
  echo "--- $m ---"
  .venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
x=[y for y in d['models'] if y['model_id']=='$m'][0]
print(' type', x['gamslib_type'], '| cvx', x['convexity']['status'],
      '| NLP', x['convexity']['objective_value'], '| MCP', x['mcp_solve']['outcome_category'])"
done

# The license-gated cohort is still 11
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
lic=sorted(m['model_id'] for m in d['models']
           if m.get('mcp_solve',{}).get('outcome_category')=='path_solve_license')
print(len(lic), lic)"

# The forcing scaffold a recommendation would plug into
# NB: --force and the strategy names never share a line, so a `force.*homotopy`
# pattern matches nothing even though the scaffold is present (src/cli.py:208-216)
grep -E -n 'homotopy|multistart|optfile|"--force"' src/cli.py | head -5

# Package exists with both branches
test -f docs/planning/EPIC_4/SPRINT_39/CONSULTATION_FOLLOWUP_PACKAGE.md && \
  grep -cE "reply|follow-up|2026-09-09" docs/planning/EPIC_4/SPRINT_39/CONSULTATION_FOLLOWUP_PACKAGE.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/CONSULTATION_FOLLOWUP_PACKAGE.md` — both branches prepared
- A ready-to-post follow-up comment that does not re-open the send decision
- A per-thread reply-integration checklist, including where an option set plugs into `--force`
- The 11-model cohort re-test procedure with the `ferts` caveat
- Re-measured figures for all three threads
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3

### Acceptance Criteria

- [ ] The follow-up comment drafted and explicitly does **not** re-open the send decision
- [ ] An integration checklist exists for each of the three threads
- [ ] All three threads' figures re-measured on current `main`
- [ ] The cohort re-test procedure written, with the `ferts` "golden ≠ correct" caveat
- [ ] `agreste`'s missing owning issue noted, with the condition under which one is filed
- [ ] rocket's +1 and the cohort's +11 explicitly excluded from Sprint-39 projections
- [ ] Unknowns 6.1, 6.2, 6.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Epic-5 Design Scoping — Numéraire Rule & Degeneracy Detection (P9)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 9.1, 9.2

### Objective

Scope the two **answerable** Epic-5 open questions as design work — the numéraire-selection rule and degeneracy detection — without running any camcge experiment, and with the banned variants recorded as banned.

### Why This Matters

Epic 5's value is its **refutation record**: three-plus sprints of camcge variants have all stayed MS-4, and the most dangerous one is *primal-correct*, which makes it perpetually tempting. Scoping the answerable questions in prep is what lets Epic 5 **start** rather than re-scope — and prep is where the temptation to re-run a banned experiment is cheapest to refuse.

### Background

**camcge #1330 stays Epic-5-scoped and is NOT implemented in Sprint 39.** MS-4 against a *correct* NLP optimum is structural Walras rank-deficiency, not an emit defect. Sprint 37 Day 10's control reproduced every predicted figure under GAMS 54.2.1: emit **19 s**, **641** single equations / 641 variables, embedded NLP **MS-2 @ omega 191.7346**, `mcp_model` **MS-4**.

**⚠ BANNED variants — consolidated in `../../EPIC_5/CGE_DEGENERACY_SCOPING.md` §4a. Do not re-run any of them:**

- **price-pin** → MS-4
- **single-dual-pin** → MS-4
- **drop-row** → **primal-correct at omega 299 but breaks the MCP dual silently** — the dropped market's multiplier is orphaned out of the stationarity. This is the dangerous one.

**The five open questions**, of which **Q3 is answered (NO)** and **Q4 is answered and narrows the scope** — the §2 survey found camcge is the **sole inherent** Walras case; every other "CGE cohort" issue is an ordinary emit/AD bug, several of which Sprint 38 fixed (#1331 twocge landed D9).

**The two answerable ones:**

- **Q1 — Numéraire-selection rule.** Is there a robust automatic rule (largest-SAM-sector price, a CPI aggregate), or must each CGE model declare its numéraire?
- **Q2 — Degeneracy detection.** How does a preprocessing layer *detect* Walras-degeneracy (a PATH basis-singularity report, a rank check on the market-clearing block, a structure heuristic) **without falsely flagging a well-posed model?** The false-positive half is the hard half.

### What Needs to Be Done

1. **Survey the corpus's CGE models** for what a numéraire-selection rule would have to handle — how many declare one, how many have an obvious largest sector, how many would be ambiguous.
2. **Draft the numéraire-selection rule** with its failure modes, and state whether a fully automatic rule is achievable or whether a per-model declaration is required.
3. **Draft the degeneracy-detection design**, and spend the effort on the **false-positive analysis**: what well-posed models would a rank check or heuristic wrongly flag? Use the corpus as the test set.
4. **Record both as *proposed*, not open**, in `CGE_DEGENERACY_SCOPING.md`, keeping Q3/Q4's answers intact.
5. **Re-state the BANNED list** at the top of whatever is written, so the next reader meets it before the temptation.
6. **Run no camcge experiment.** If a measurement seems necessary, that is a finding — record what would need measuring and why it is out of scope here.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# The banned list is intact and reachable
grep -n -A8 "BANNED" docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head -20

# Which open questions remain open
grep -n -A2 "^## 5. Open questions" docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head

# CGE cohort for the numéraire survey
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
cge=[m['model_id'] for m in d['models'] if 'cge' in m['model_id'].lower()]
print(len(cge), sorted(cge))"

# camcge's recorded state — read, do not re-run
.venv/bin/python -c "
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
m=[x for x in d['models'] if x['model_id']=='camcge'][0]
print('convexity:', m['convexity']['status'], '| NLP obj:', m['convexity']['objective_value'])
print('MCP:', m['mcp_solve']['outcome_category'])"

# Q1/Q2 moved to proposed, Q3/Q4 answers preserved
grep -cE "proposed|PROPOSED" docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md
grep -c "ANSWERED" docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md
```

### Deliverables

- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` extended with a proposed numéraire-selection rule and a degeneracy-detection design
- A **false-positive analysis** for the detection design, tested against the corpus
- A CGE-cohort numéraire survey
- Q1 and Q2 moved from *open* to *proposed*, with Q3/Q4's answers preserved
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 9.1, 9.2

### Acceptance Criteria

- [ ] The BANNED variants restated at the top of the new material
- [ ] **No camcge experiment run** — anything requiring one is recorded as out of scope
- [ ] A numéraire-selection rule drafted with its failure modes
- [ ] A degeneracy-detection design drafted, with the false-positive analysis given the majority of the effort
- [ ] The corpus used as the false-positive test set
- [ ] Q1/Q2 marked *proposed*; Q3/Q4's existing answers untouched
- [ ] camcge confirmed to remain Epic-5-scoped and out of Sprint-39 implementation
- [ ] Unknowns 9.1, 9.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Emit-Backlog Catalog Refresh & Process-Infrastructure Spec (P8, P10)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2, 7
**Unknowns Verified:** 8.1, 8.2, 8.3, 10.1, 10.2

### Objective

Refresh the emit-backlog candidate catalog against the post-Sprint-38 corpus, and specify the four process-infrastructure changes the Sprint-38 retrospective recommended.

### Why This Matters

**P10 is the deliberate schedule filler**, and its pre-registered selection rule is what stops it becoming an open-ended diagnosis sprint. That rule needs a current catalog: Sprint 38 removed four models from `path_solve_terminated` entirely, so the previous catalog's population has changed.

**P8 is the infrastructure that would have prevented Sprint 38's most repeated failure.** Three of four gates named the wrong layer; one demanded new logic for logic that existed. Both are cheap to guard against, and both guards are template/checklist changes rather than code.

### Background

**The pre-registered selection rule (unchanged, because it worked):** a model enters the sweep only with a **reproduced fingerprint** and a **named fix surface**. Anything needing a new diagnosis is **banked, not started**.

**Current bank, from `../SPRINT_38/SPRINT_39_CARRYFORWARDS.md` §8:**

- **`agreste`** — the highest-value bank. An **LP**, `verified_convex`, NLP MS-1 @ 17706.43, MCP **MS-5 after 9,734 iterations**. A *locally* infeasible pure LCP is structurally odd. **Also now posed to the PATH authors**, so check #1443 before starting local work. Has **no open owning issue**.
- **`cesam`** — new diagnosis; MS-4 at 0 iterations, same *signature* as lnts but **0 `_fx_` equations**, so lnts's mechanism cannot apply.
- **`indus`** (31 errors across 7 families), **`dinam`** (22), **`turkpow`**, **`clearlak`** — broad, not bounded, or structurally excluded.

**Unknown 1.5 carries and stays unmeasurable:** does a general `$149` fix unblock the `$149` half of dinam/indus/turkpow/clearlak? It needs a fix in the tree, and **P1 ganges was closed as unreachable at the rebind site** — #1668 direction 1 is a measured **no-op** (265 fires, zero residual) and direction 2's information is absent, since ganges and `prolog` are *locally indistinguishable* there. **Do not re-open the rebind site.**

**The four process findings (S38 retrospective §7):**

- **8a.** Record the **LAYER** in a Phase-0 gate, not just `file:line`.
- **8b.** Check whether the logic already exists for another **population** before authoring new emit logic.
- **8c.** Stop pre-registering close rules against **unstarted** carryforward tracks (S38's close rule #2 went unmet because P1 was REPLAN'd on Day 1).
- **8d.** Re-derive a carried package's **evidence** at use time, not only its conclusion. Corollary: an internal planning doc is not an external deliverable.

### What Needs to Be Done

1. **Refresh the catalog** against the current DB — every non-solving candidate, with its outcome category, whether it has an owning issue, whether that issue has a Phase-0 gate, and whether a fingerprint is reproduced.
2. **Apply the selection rule** and produce a ranked shortlist, with the rejected entries carrying their reason.
3. **Cross-check against Task 7's survey** — is any backlog model an instance of the positional-domain class? That would move it from "new diagnosis" to "named fix surface".
4. **Specify 8a**: the Phase-0 template's new *layer* field, and the `scripts/sprint_audit/check_phase0_doc.py` assertion for it.
5. **Specify 8b**: where the "does this exist for another population?" check lives in the authoring workflow.
6. **Specify 8c and 8d** as CONTRIBUTING rules, each with the Sprint-38 incident that motivates it.
7. **Write the fail-before test for each** — a template change without a test is a suggestion.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# Current non-solving candidates — the catalog's population
.venv/bin/python -c "
import json
from collections import Counter
d=json.load(open('data/gamslib/gamslib_status.json'))
cand=[m for m in d['models'] if m.get('convexity',{}).get('status') in ('verified_convex','likely_convex')]
bad=[m for m in cand if m.get('mcp_solve',{}).get('outcome_category') not in
     ('model_optimal','model_optimal_presolve')]
print(Counter(m['mcp_solve']['outcome_category'] for m in bad))
for m in sorted(bad, key=lambda x: x['model_id']):
    print(' ', m['model_id'], m['mcp_solve']['outcome_category'])" | head -30

# Which of them have an owning issue with a Phase-0 gate.
# Three defects fixed here, all of which made this read as a clean result:
#   (a) `grep -i "$m"` is a SUBSTRING match -- `cesam` claimed cesam2's issue doc,
#       and both are real, distinct corpus models (same for indus/indus89).
#       Anchored to the ISSUE_<n>_<model>- naming convention instead.
#   (b) `head -1` hid multiple owners -- camcge has 9 -- and hid that all of
#       cesam's live in completed/, which for a backlog sweep is the whole point.
#   (c) the model list was 5 hard-coded names standing in for "them", i.e. the
#       failing candidates printed just above. Derived from the DB now.
# Python rather than shell: the natural shell form needs word-splitting over
# find output, and zsh does not split unquoted $vars.
.venv/bin/python -c "
import json, re, pathlib
d=json.load(open('data/gamslib/gamslib_status.json'))
cand=[m for m in d['models'] if m.get('convexity',{}).get('status') in ('verified_convex','likely_convex')]
bad=sorted(m['model_id'] for m in cand
           if m.get('mcp_solve',{}).get('outcome_category') not in ('model_optimal','model_optimal_presolve'))
docs=list(pathlib.Path('docs/issues').rglob('ISSUE_*.md'))
owned=0
for m in bad:
    pat=re.compile(rf'^ISSUE_\d+_{re.escape(m)}-')
    hits=sorted(p for p in docs if pat.match(p.name))
    if not hits:
        print(f'{m:10} -> NO ISSUE DOC'); continue
    owned+=1
    for p in hits:
        g=sum(1 for l in p.read_text().splitlines() if l.startswith('## Phase 0'))
        print(f'{m:10} -> {p.relative_to(\"docs/issues\")} (phase0: {g})')
print(f'--- {len(bad)} failing candidates, {owned} with an owning issue doc')
"

# Phase-0 checker: does it yet assert a layer field?
grep -E -n "layer|Layer" scripts/sprint_audit/check_phase0_doc.py | head

# Deliverables exist
test -f docs/planning/EPIC_4/SPRINT_39/BACKLOG_CANDIDATE_CATALOG.md && echo "✅ catalog"
test -f docs/planning/EPIC_4/SPRINT_39/PROCESS_INFRA_SPEC.md && echo "✅ infra spec"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/BACKLOG_CANDIDATE_CATALOG.md` — refreshed population, selection rule applied, ranked shortlist with rejection reasons
- `docs/planning/EPIC_4/SPRINT_39/PROCESS_INFRA_SPEC.md` — specifications for 8a–8d, each with its motivating incident and a fail-before test
- A cross-check result: which backlog models, if any, are instances of the positional-domain class
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.1, 8.2, 8.3, 10.1, 10.2

### Acceptance Criteria

- [ ] Catalog refreshed against the current DB, not the Sprint-38 population
- [ ] Selection rule applied; every rejection carries a reason
- [ ] Cross-check against Task 7's survey performed
- [ ] 8a specified, including the `scripts/sprint_audit/check_phase0_doc.py` assertion
- [ ] 8b, 8c, 8d specified as CONTRIBUTING rules with their motivating incidents
- [ ] A fail-before test specified for each of the four
- [ ] `agreste`'s consultation dependency noted — check #1443 before local work
- [ ] The ganges rebind site explicitly marked do-not-re-open
- [ ] Unknowns 8.1, 8.2, 8.3, 10.1, 10.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 12: Plan Sprint 39 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 39 Day 1
**Owner:** Development team
**Dependencies:** All tasks (1–11)
**Unknowns Verified:** (integrates all)

### Objective

Convert the prep findings into a day-by-day Sprint 39 schedule with per-day budgets, pre-registered REPLAN exits, checkpoints, and the close rules — the document the sprint is actually executed from.

### Why This Matters

Sprint 38's schedule absorbed a **Day-1 REPLAN of its top priority** without losing the sprint, because the REPLAN exits and the budget reallocation were pre-registered. Sprint 39 carries three tracks that could REPLAN (P2's residual persisting, P3's probe refuting the hypothesis, P4's timeout re-triggering) and one that is **date-gated** and cannot be moved.

This task also owns the close rules — and Sprint 38 learned the hard way that **a close rule pre-registered against an unstarted track is a bet** (its rule #2 went unmet because P1 was REPLAN'd on Day 1).

### Background

**Budget:** 14 days (Day 0 + Days 1–13) at ≤ 12 h/day = **168 h cap**. The plan's estimate is **116–160 h**, heaviest day ~11.4 h.

**Fixed points that constrain the schedule:**

- **P1 is Day 0** — a decision, and the sprint's baseline depends on it.
- **P6 is date-gated at 2026-09-09** and cannot be pulled earlier.
- **P4 is the only KPI mover** and the largest single cost (20–28 h).
- **P7 changes how the pipeline records solves** — the DB is the substrate every KPI derives from, so it is scheduled **after P1 settles the baseline**.
- **Checkpoints** at Day 5 and Day 10, final retest Day 13 under ≥ 3 `PYTHONHASHSEED`.

**Close rules to pre-register (learning from S38's rule #2):**

- The **three-gate firm-landing rule**: per-model Phase-0 gate + an **unqualified** leak-gate pass + in `main`. Anything else is a carryforward with a bounded next step.
- **`path_solve_terminated` must maintain 0** — a model returning to it is a **regression**, not churn.
- **Match may FALL to 95** if P7 reclassifies `weapons` — a **correction, not a regression**, reported with its reason in the same sentence.
- The floor is read from the provenance file, on whichever baseline P1 settles.
- **Every figure derived at execution time**; anything quoted carries its commit.

### What Needs to Be Done

1. **Assign priorities to days**, honouring the fixed points, with a per-day hour budget summing under 168 and no day over 12.
2. **Write the REPLAN exit for each track** — the specific evidence that triggers it and where the budget goes.
3. **Schedule the checkpoints** and the final retest, with the DB checkpoint re-anchored to `9ab2c0c3`.
4. **Pre-register the close rules**, and for each, **state its precondition explicitly** so an unmet rule can be distinguished from a missed target.
5. **Write the day prompts** (`prompts/PLAN_PROMPTS.md`), each naming its branch, its deliverable, and its gate.
6. **Record the risk register** with mitigations, and the acceptance criteria with each figure's source.
7. **Route every unresolved Known Unknown** to the day that closes it.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"

# Plan + prompts exist. PLAN.md is THIS task's own deliverable, so before Task 12
# runs every check below has nothing to read -- guard once and say so, rather than
# emitting four "No such file" errors and a Python traceback.
PLAN=docs/planning/EPIC_4/SPRINT_39/PLAN.md
if [ ! -f "$PLAN" ]; then
  echo "PLAN.md does not exist yet — expected until Task 12 produces it; skipping its checks"
  exit 0
fi
echo "✅ PLAN.md"
test -f docs/planning/EPIC_4/SPRINT_39/prompts/PLAN_PROMPTS.md && echo "✅ prompts"

# 14 days covered (Day 0 + Days 1-13)
grep -cE "^### Day [0-9]+" "$PLAN"

# Budget check: no day over 12h, total under 168
PLAN="$PLAN" python3 - <<'PY'
import re, os
s=open(os.environ['PLAN']).read()
hrs=[int(x) for x in re.findall(r'^\|\s*\d+\s*\|.*\|\s*(\d+)\s*\|', s, re.M)]
if hrs:
    print(f"days: {len(hrs)} | total: {sum(hrs)}h | max/day: {max(hrs)}h "
          f"| under cap: {sum(hrs)<=168 and max(hrs)<=12}")
else:
    print("no day-budget table found — add one")
PY

# Every priority has a REPLAN exit
grep -c "REPLAN" "$PLAN"

# Close rules present, each with its precondition
grep -E -A2 "Close Rules|Pre-registered Close" "$PLAN" | head -12

# Every unknown routed to a day
grep -c "Unknown [0-9]" "$PLAN"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_39/PLAN.md` — day-by-day schedule, per-day budgets, REPLAN exits, checkpoints, risk register, acceptance criteria
- `docs/planning/EPIC_4/SPRINT_39/prompts/PLAN_PROMPTS.md` — one prompt per day, each naming branch, deliverable and gate
- A pre-registered close-rule set, **each rule carrying its precondition**
- A routing table from every unresolved Known Unknown to the day that closes it
- Every unresolved Known Unknown routed to the sprint day that closes it

### Acceptance Criteria

- [ ] 14 days scheduled (Day 0 + Days 1–13) with per-day budgets
- [ ] No day exceeds 12 h; total ≤ 168 h and consistent with the plan's 116–160 h estimate
- [ ] P1 on Day 0; P6 respecting the 2026-09-09 date gate; P7 after P1
- [ ] A REPLAN exit for every track, naming the triggering evidence and the budget's destination
- [ ] Close rules pre-registered, **each with its precondition stated**
- [ ] Checkpoints at Days 5 and 10; final retest Day 13 under ≥ 3 `PYTHONHASHSEED`
- [ ] Every unresolved Known Unknown routed to a specific day
- [ ] Day prompts written, each naming its branch, deliverable and gate
- [ ] All 30 unknowns are either resolved in prep or routed to a specific sprint day

---

## Summary and Critical Path

### Critical Path

```
Task 1 (Known Unknowns)
   └─> Task 2 (Baseline & Fingerprint Re-Derivation)
          ├─> Task 3  (Floor Decision Package)      ─┐
          ├─> Task 4  (dyncge Layer Trace)           │
          ├─> Task 5  (lnts Probe Design)            ├─> Task 12 (Detailed Schedule)
          ├─> Task 6  (sarf Call Sites)              │
          ├─> Task 7  (Positional-Domain Survey) ──> Task 11 (Catalog + Infra Spec)
          ├─> Task 8  (Presolve-Record Remedy)       │
          └─> Task 10 (Epic-5 Design Scoping)       ─┘
   └─> Task 9 (Consultation Package)  ──────────────┘
```

**Tasks 4, 5, 6, 7, 8 and 10 are parallelisable** once Task 2 lands. Task 3 is short but on the critical path because it gates the sprint's baseline.

### Time Budget

| Phase | Tasks | Hours |
|---|---|---|
| Foundation | 1, 2 | 6–8 |
| Decision | 3 | 2–3 |
| Technical traces | 4, 5, 6 | 14–20 |
| Surveys & designs | 7, 8, 10 | 10–13 |
| Packages & specs | 9, 11 | 5–7 |
| Scheduling | 12 | 3–4 |
| **Total** | **1–12** | **40–55** |

### Success Criteria for the Prep Phase

- [ ] **Every Critical/High Known Unknown is resolved or explicitly deferred with a reason** — a deferred unknown carries the day that closes it
- [ ] **Every figure Sprint 39's plan quotes has been re-derived on current `main`**, or its discrepancy recorded and routed
- [ ] **The floor decision is a package an owner can answer in one sitting** — evidence, counter-argument, both consequences, both edits
- [ ] **All three untraced tracks (P2, P3, P4) have a named layer and a Phase-0 gate** before Day 1
- [ ] **No prep task ran a banned experiment** — camcge's variants in particular
- [ ] **The schedule fits**: ≤ 12 h/day, ≤ 168 h total, with a REPLAN exit per track and close rules carrying their preconditions
- [ ] **Prep found at least one wrong premise.** Sprint 38's prep refuted 6 of 28 assumptions outright and partially refuted 3 more; a prep phase that confirms everything has probably not looked hard enough

### What Would Make This Prep a Failure

Recorded in advance, so it can be recognised:

- A Sprint-39 day spends its budget *diagnosing* rather than implementing, because a trace was deferred to the sprint
- A fix surface is discovered mid-sprint to be in a different **layer** than the gate named — the failure Sprint 38 had three times
- The floor decision is carried undecided into Sprint 40
- A banned camcge variant is re-run "just to check"

---

## Appendix: Document Cross-References

### Sprint 39 definition
- `../PROJECT_PLAN.md` → *Sprint 39 (Weeks 43–44)* — goal, ten priorities, deliverables, acceptance criteria, effort, risk
- `../GOALS.md` — Epic 4 goals, success metrics, and the deferred-work inventory this sprint draws from

### Sprint 38 hand-off (the primary source for every priority)
- `../SPRINT_38/SPRINT_39_CARRYFORWARDS.md` — §1 floor decision · §2 dyncge `CASE_B` · §3 lnts · §4 sarf · §5 ganges closed · §6 consultation · §7 process findings · §8 banked candidates
- `../SPRINT_38/SPRINT_LOG.md` — the close figures, the four-destination table, the three-gate rule applied
- `../SPRINT_38/SPRINT_RETROSPECTIVE.md` — §2 the gate-layer finding · §3 the positional-domain class · §4 the floor question · §7 the four process changes
- `../SPRINT_38/PLAN.md` §9 — the pre-registered close rules Sprint 39 inherits and amends

### Per-priority background
- **P1 floor:** `data/floor_provenance.json` · `scripts/sprint_audit/floor_tracker.py` · `../SPRINT_38/MEASUREMENT_INTEGRITY_DESIGN.md` (P6c)
- **P2 dyncge:** `docs/issues/completed/ISSUE_1693_dyncge-empty-mcp-pair-eqpf2-diagonal-cancellation.md` · `../SPRINT_38/DAY12_P8_ELEC.md` §6
- **P3 lnts:** `../SPRINT_38/BACKLOG_CANDIDATE_CATALOG.md` · `../SPRINT_38/PLAN.md` Day-12 entry
- **P4 sarf:** `docs/issues/ISSUE_1385*` · `../SPRINT_38/SARF_REARCH_DESIGN.md` · `../SPRINT_38/DAY6_SARF_PROBE_DECISION.md` · `../SPRINT_38/DAY7_SARF_GATE_P6C.md`
- **P5 positional domain:** `../SPRINT_38/DAY11_P5_CLOSE_P8_TRICP.md` · `../SPRINT_38/DAY12_P8_ELEC.md` · `docs/issues/ISSUE_1062_*` · `docs/issues/ISSUE_1325_*`
- **P6 consultation:** `../SPRINT_38/CONSULTATION_DECISION_BRIEF.md` · `../SPRINT_38/ROCKET_CONSULTATION_EXTERNAL.md` · GitHub #1462, #1443
- **P7 presolve records:** `../SPRINT_38/DAY10_SPURIOUS_MATCH_P5.md` · `../SPRINT_38/DAY8_PRESOLVE_GOLDEN_ADOPTION.md` · `scripts/sprint_audit/check_mcp_solve_attribution.py`
- **P8 process:** `../SPRINT_38/SPRINT_RETROSPECTIVE.md` §7 · `scripts/sprint_audit/check_phase0_doc.py` · `../SPRINT_38/PHASE0_COMPLIANCE_CATALOG.md`
- **P9 Epic 5:** `../../EPIC_5/CGE_DEGENERACY_SCOPING.md` (§2 cohort survey · §4a BANNED variants · §5 open questions) · `../SPRINT_38/CAMCGE_EPIC5_HANDOFF.md`
- **P10 backlog:** `../SPRINT_38/BACKLOG_CANDIDATE_CATALOG.md` · `docs/issues/` open backlog

### Research documents
- `docs/research/gamslib_kpi_definitions.md` — how the KPIs are defined and scoped
- `docs/research/convexity_detection.md` · `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` — the `verified_convex` / `likely_convex` classification the 142-candidate corpus rests on
- `docs/research/multidimensional_indexing.md` — background for the positional-domain class (P5)
- `docs/research/minmax_objective_reformulation.md` · `docs/research/nested_minmax_semantics.md` — reformulation precedents for P2/P3 shapes

### Tooling the prep tasks use
- `scripts/sprint_audit/kpi_block.py` — derived KPI block, carries its commit, warns on a dirty DB
- `scripts/sprint_audit/floor_tracker.py` — the floor, from provenance, never from the DB
- `scripts/sprint_audit/check_golden_staleness.py` — the full-corpus leak gate (186 in-scope)
- `scripts/sprint_audit/check_mcp_solve_attribution.py` — spurious-match discriminator (positional, not `EXECERROR`-keyed)
- `scripts/sprint_audit/check_phase0_doc.py` — Phase-0 compliance
- `scripts/diagnostics/kkt_residual.py` — `CASE_A` / `CASE_B` / `CASE_C` verdicts
- `scripts/diagnostics/check_presolve_divergence.py` — embedded-NLP divergence
- `scripts/gamslib/run_full_test.py` — pipeline runner, `--resolve-changed` checkpoint
