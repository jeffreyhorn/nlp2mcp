# Sprint 40 Preparation Plan

**Purpose:** Complete the preparation tasks that must land before Sprint 40 Day 1
**Timeline:** Complete before Sprint 40 Day 1
**Goal:** Turn the full GAMS license from a possession into *evidence* — a toolchain shown to be licensed, a CI design that never exposes it, and owner decisions taken **before** any license-gated **cohort** result exists — while giving every Sprint-39 carryforward a re-measured disposition

**Anchor:** `bd2af6e9` (Sprint 39 close, 2026-09-18) · plan merged at `912d005c` (PR #1745) · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**

> **Which anchor?** Sprint 39's close documents (`SPRINT_LOG.md` §Day 13, `SPRINT_40_CARRYFORWARDS.md`) measure at **`bd2af6e9`**. `54b4eb23` (the close-PR merge) and `912d005c` (the merge of PR #1745, which inserted Sprint 40 into `PROJECT_PLAN.md` — the commit this prep branch was cut from; this `PREP_PLAN.md` itself arrives with PR #1746) are later, but `git diff bd2af6e9 912d005c -- data/ src/ tests/ scripts/` must be checked in Task 2 rather than assumed empty. Re-derive at the commit you are on, and cite it.

**Sprint definition:** `../PROJECT_PLAN.md` → *Sprint 40 (Weeks 45–46): Sprint 39 Carryforward & the Licensed-GAMS Unlock — the License-Gated Cohorts' First NLP-vs-MCP Comparison, Licensed CI, the P10 Two-Class Triage, lnts, sarf's Jacobian Re-Architecture & the Sprint-39 Process Changes*

**Key insight carried from Sprint 39:** the sprint's recurring failure was not a wrong *fix* but a wrong *claim about evidence* — a figure restated per review round until it rotted (four times), a count where an identity was needed, a probe reported as passing that could not have failed (twice), a classification moved without sweeping the sentences that quoted it. Sprint 40 adds a new way to produce that failure at scale: **twenty first-time in-scope results** — 11 MCP-gated solves plus 9 non-MIP NLP-gated classifications (`andean` is MIP-excluded). This prep plan is therefore weighted toward **establishing what counts as evidence before the evidence arrives** — Tasks 3–6 exist so that the **first licensed cohort result (Task 7)** is read against rules written without knowing it. Task 3's synthetic probes and neutrality sample come first by design; they test the toolchain, not which way any gated model falls.

---

## Process Rules This Prep Applies to Itself

From `../SPRINT_39/SPRINT_RETROSPECTIVE.md` §7 and `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md` §8. The project plan requires prep to *adopt* these; prep adopts them first on its own artifacts:

1. **A figure that changes with the thing it describes is stated once, commit-pinned, and superseded by the next measurement** — every figure in a prep deliverable carries `measured at <sha>`; a later task re-measures rather than re-quotes.
2. **Pin by identity, not by count** — both license-gated populations are recorded as **named lists** with the predicate that produced them, never as "11" and "10" alone.
3. **Anchors are code, scoped, nested-aware, unique** — reuse the resolver in `tests/unit/kkt/test_positional_domain_sites.py`.
4. **The PR description is a pointer, not a mirror** — a two-to-four-line summary, the unknowns verified with their verdicts, and "see `PREP_PLAN.md` Task <Z> *Result*"; never a copy of the `Result` section, which would go stale with the first review round (same rule as `prompts/PREP_TASK_PROMPTS.md`'s standing conventions).
5. **A probe must be shown able to fail before its pass is believed** — every probe in Tasks 3, 7, 8 and 10 records its positive control.
6. **When a classification changes, sweep on the changed SET** — when a cohort model's bucket moves in Task 7, grep every prep doc for that model's name.
7. **Never `git stash` to switch branches** — `git show <ref>:<path>` is read-only.
8. **The leak gate runs ALONE** — no concurrent pytest, GAMS batch, or second gate.

---

## Executive Summary

Sprint 39 closed at **Solve 111 · Match 95 · Translate 135 · floor 75 · `path_solve_terminated` 0** (measured at `bd2af6e9`; Match 96 → 95 was P7's `weapons` **correction**, not a regression). Its carryforwards are each bounded (`../SPRINT_39/SPRINT_40_CARRYFORWARDS.md`), but the sprint they feed has changed shape: **the project now has a GAMS license obtained as size-unlimited — observed so far as a user-level evaluation license (valid to 2027-09-21); whether it is the *effective* license for every pipeline invocation and lifts the limit on every solver path is Unknown 1.1, Task 3's to prove**, and the demo's 1,000-row nonlinear limit has gated two populations at different stages for the whole of Epic 4 — **11 MCP solves** inside the 142-candidate corpus and **10 reference NLP solves** outside it.

Sprint 40 addresses ten priorities:

1. **P1 (Infrastructure, Day 0–1):** the licensed toolchain locally and in CI — **PR workflows stay demo-only**; the licensed tier runs in a new trusted `main`-only workflow via a protected-environment secret; schema **3.1.0** adds a per-row `license_edition`
2. **P2 (Measurement):** the 11-model MCP-gated cohort's first full NLP-vs-MCP comparison — ceiling +11 Solve, **measured, not projected**
3. **P3 (Measurement + decision):** the 10-model NLP-gated set's convexity evaluation and the **corpus-entry decision** (`andean` is MIP — excluded)
4. **P4 (Correctness):** the P10 two-class triage, turkpow first
5. **P5 (KPI):** lnts — **⚠ prep must test whether the banked diff is landable at all** (Sprint 39 Day 5 found a second defect underneath)
6. **P6 (KPI):** sarf's O(active) Jacobian re-architecture — **+1 Translate**
7. **P7 (Correctness):** the diagonal-reference defect (`stat_tsam(i,j).. 1 =E= 0;`)
8. **P8 (Prevention):** the positional-domain follow-ons
9. **P9 (Slack):** the smaller items
10. **P10 (Infrastructure):** the Sprint-39 process changes as mechanisms

This prep plan front-loads the work whose absence would cost the most mid-sprint: **re-deriving both license-gated populations by identity** (Task 2), **proving the installed license is the effective one and lifts the limit for every solver** (Task 3) — it is installed at the **user level**, while the system-directory `gamslice.txt` is still the 2026-07-13 demo file — **designing CI isolation and the schema change** (Tasks 4–5), **taking the owner decisions blind** (Task 6), and only then **dry-running the cohorts** (Task 7) so the sprint opens on fingerprints rather than on surprises.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 40 Goal Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | ✅ Create Sprint 40 Known Unknowns List | Critical | 3-4 hours | None | Proactive unknown identification across all 10 priorities + the license unlock |
| 2 | ✅ Re-Derive the Sprint-39 Baseline & Both License-Gated Populations by Identity | Critical | 2-3 hours | Task 1 | Every priority — the commit-pinned baseline and the two named cohorts |
| 3 | Prove the Effective License — Precedence & Per-Solver Fail-Capable Probes | Critical | 3-4 hours | Tasks 1, 2 | P1 (local) — gates P2/P3 and Tasks 5, 7 |
| 4 | CI License-Isolation Design & Workflow Inventory | High | 3-4 hours | Tasks 1, 3 | P1 (CI) — demo-only PR jobs, trusted licensed workflow |
| 5 | Schema 3.1.0 `license_edition` Design | High | 2-3 hours | Tasks 1, 3 | P1 (schema) — migration, writers, `db_manager`, tests |
| 6 | Owner Decision Brief — Floor Provenance, Corpus Entry & Hosted Runners (written blind) | Critical | 2-3 hours | Tasks 1, 2, 3, 4 | P1/P2/P3 — the three owner decisions, answered in prep before any cohort result exists |
| 7 | License-Gated Cohorts Dry Run — Fingerprints & Routing | Critical | 5-7 hours | Tasks 2, 3, 6 | P2 + P3 — first measurement, GO/NO-GO, never persisted |
| 8 | lnts — Is the Banked Diff Landable? Premise Test & Phase-0 Gate | High | 3-4 hours | Tasks 1, 2, 3, 7 | P5 — the +1 Solve rests on an untested premise |
| 9 | sarf Jacobian O(active) Re-Architecture Design | High | 4-6 hours | Tasks 1, 2 | P6 — the sprint's planned +1 Translate |
| 10 | Correctness-Track Pre-Traces: turkpow Class A, the Diagonal Defect, the Structural Sites | High | 5-7 hours | Tasks 1, 2, 7, 9 | P4, P7, P8 — named layers and reproducers before Day 1 |
| 11 | Process-Mechanism Spec & Smaller-Items Catalog | Medium | 3-4 hours | Tasks 1, 2 | P9 + P10 — the slack absorber and the §7 mechanisms |
| 12 | Plan Sprint 40 Detailed Schedule | Critical | 3-4 hours | All tasks (1–11) | Day-by-day schedule + REPLAN exits + close rules + budget |

**Total Estimated Time:** ~38–53 hours (~5–7 working days)

**Critical Path:** Tasks **1 → 2 → 3 → 4 → 6 → 7 → 10 → 12**

Task 3 gates everything license-dependent: no cohort result is evidence until the edition that produced it is shown — and with a demo file still in the system directory, *which* license runs is a question, not a given. **Task 6 waits on Tasks 3 and 4** because its third decision (CI license use) needs Task 3's binding evidence and Task 4's hosted-runner checklist; without them Task 6 could complete, and unblock Task 7, with that decision still pending. **Task 6 is deliberately placed *before* Task 7** — the floor-provenance and corpus-entry rules must be written while nobody knows which way the cohorts fall; Sprint 39's P1 established that a favourable classification discovered by the person reporting it is exactly the one that should not be self-approved. Task 10 waits on Task 7 because egypt and shale — two of P4's three models with no solve — get their first solve there, and on **Task 9** because Unknown 8.2 maps Task 9's touch set against #1737.

---

## Task 1: Create Sprint 40 Known Unknowns List

**Status:** ✅ **COMPLETE** (2026-10-12)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** n/a — this task *creates* the unknowns (29 across 10 categories)

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/KNOWN_UNKNOWNS.md` enumerating every assumption Sprint 40's plan rests on, categorised by priority, each with research questions, a verification method, a risk-if-wrong and an owner — so that assumptions are refuted **in prep**, when refutation is cheap, rather than on a sprint day.

### Why This Matters

The Known-Unknowns process has caught a materially wrong premise in every recent sprint, and the refutation rate is rising: Sprint 38's prep refuted **32 %** of its assumptions, Sprint 39's **63 %** (19 of 30). Nine of Sprint 39's refuted unknowns changed the sprint rather than a figure — P4's cost premise, P7's "all 14 or none", P10's selection yielding no available qualifier.

Sprint 40 carries a new class of unknown that no prior sprint had: **assumptions about results that have never existed**. That eleven goldens exist says nothing about whether they solve (`ferts`'s emit was silently wrong until Sprint 38 Day 11); that nine models are LP/NLP/QCP says nothing about whether they are convex. And at least one carryforward rests on a premise its own source log contradicts — lnts's "re-apply the banked diff" against Sprint 39 Day 5's *"removing the contradiction is not sufficient"*.

### Background

`../SPRINT_39/KNOWN_UNKNOWNS.md` is the template: 30 unknowns across 10 categories, each with **Priority / Assumption / Research Questions / How to Verify / Risk if Wrong / Estimated Research Time / Owner / Verification Results**, plus a task-mapping appendix. Its final tally was **11 ✅ / 11 ❌ / 8 🔶**. <!-- figures-ok: 30 is SPRINT 39's count (the template), not Sprint 40's -->

⚠ **Sprint 39's Task 1 published a research-time total "derived by summing" that was never summed** (40.0 h written as 33.0 h, then "corrected" to 29.0 h). Derive the total with the snippet in *Verification*, at the point of use.

Candidate seeds, drawn from `../PROJECT_PLAN.md` Sprint 40 and `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md`:

- **License (P1):** is the installed license the full one? Does the `.lst` header distinguish licensed from demo in a parseable way? Do the license terms permit GitHub-hosted ephemeral runners? Can a protected environment's `main`-only branch policy be bypassed by `workflow_dispatch` from another ref?
- **Schema (P1):** are `mcp_solve_result` and `convexity_result` the only result types a license-dependent stage writes? Is `run_full_test.py` a mirror or a second writer?
- **MCP-gated cohort (P2):** do all 11 translate at HEAD within the timeout? Are all 11 goldens byte-identical at HEAD? How many reach a PATH outcome vs. a compile error (`ISSUE_933` tricp)? Is any match a presolve self-match (the `weapons` trap)?
- **NLP-gated set (P3):** are the nine LP/NLP/QCP models really in scope by type? How many classify convex? Do any parse today?
- **P10 two-class (P4):** is turkpow's minting site still `t__kkt1` into both coordinates of `vs(t,v)`? Does the ratchet still read 9?
- **lnts (P5):** is the banked diff landable, given Day 5's REPLAN (`_fx_` rows `INFES`, `robot`/`springchain` drift, a label-enumerated guard, a second dynamics defect)?
- **sarf (P6):** is 70.9 % still in `compute_constraint_jacobian` at HEAD? Is `gradient.py:453` still dead?
- **Diagonal defect (P7):** does `stat_tsam(i,j).. 1 =E= 0;` reproduce on `main`, and is the layer `_diff_sum`?
- **Structural sites (P8):** does a discriminating input exist at 2-D, or only at ≥ 3-D?
- **Process (P10):** does the local `make check-goldens` really lack `--min-scope`? Is the anchor resolver extractable without changing its behaviour?

### What Needs to Be Done

1. **Enumerate the assumptions** in `../PROJECT_PLAN.md`'s Sprint 40 entry and `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md` — every figure, every named file or symbol, every "should".
2. **Group into categories**, one per sprint priority plus one for the license unlock as a whole, numbered `N.M`.
3. **For each unknown, write all eight sections**, leaving *Verification Results* empty for the owning task.
4. **Add a mapping table** — unknown → owning prep task — and add an `**Unknowns Verified:**` line to each of Tasks 2–11 in this plan (Task 12 integrates rather than owns).
5. **Flag lineage** — which unknowns descend from a Sprint-39 disposition, and which are new with the license.
6. **Derive the research-time total by script**, not by addition in prose.

### Changes

- **Created** `docs/planning/EPIC_4/SPRINT_40/KNOWN_UNKNOWNS.md` — 29 unknowns across 10 categories, each with all 8 required sections and 3–5 research questions
- **Added** the Task-to-Unknown mapping appendix, assigning every unknown to exactly one owning prep task
- **Updated** this plan's Tasks 2–11 with `Unknowns Verified` metadata, a deliverable and an acceptance-criteria item each
- **Updated** `CHANGELOG.md` with the Task 1 completion entry

### Result

✅ **COMPLETE — 29 unknowns, 10 categories, 33.0 research hours.**

| metric | target | actual |
|---|---|---|
| Total unknowns | 22–30 (aim 25+) | **29** |
| Critical | ~25 % | **7 (24 %)** |
| High | ~40 % | **11 (38 %)** |
| Medium | ~25 % | **8 (28 %)** |
| Low | ~10 % | **3 (10 %)** |
| Research time | 28–36 h | **33.0 h** — derived by this task's *Verification* snippet, not added in prose |
| Categories | all sprint components | **10** (one per priority; Category 1 is the license toolchain) |

**Every figure above was produced by script at the commit that adds the file**, including the coverage check (every unknown owned by exactly one task; none orphaned). The 33.0 h fits within Tasks 2–11's 32–45 h budget **at its lower bound** — unlike Sprint 39, whose 40.0 h fitted only near the top.

**Three premises were put in doubt by writing the list, before any task ran** — each is an unknown, not a conclusion:

1. **Which license runs, and for which solvers (1.1)** — ⚠ *corrected in PR #1746 review:* this bullet first read *"the license may not be installed"*, from the system-directory `gamslice.txt` (still the 2026-07-13 demo file). The license **is** installed at the **user level** and the log header reports it; the open question is precedence and per-solver coverage. And the license must cover **three** solvers *(four solver paths after PR #1746 review: the QCP model `emfl` selects its own solver, independently of `NLP=`)* — `verify_convexity.py` uses `LP=CPLEX` and `NLP=CONOPT`, MCP solves use PATH — so a solver-selective license would split P3 by license, not by convexity.
2. **The corpus can grow before the owner decides (3.3):** `kpi_block.py:112` and `batch_parse.get_candidate_models` select candidates by `convexity.status`, so the 142 denominator is **derived** — a licensed convexity run that writes a convex status for any NLP-gated model moves it silently. Task 7's never-persist rule is what prevents this in prep; the sprint needs a mechanism.
3. **lnts may not be landable as planned (5.1–5.3):** Sprint 39 Day 5's candidate failed its PROCEED signal on substance (`_fx_` rows `INFES`, `robot`/`springchain` perturbed, a label-enumerated guard), and a second dynamics defect (364 `INFES` rows) sits underneath.

**Lineage:** Sprint 39's 30 unknowns all resolved in prep, so none carries open. Categories 2, 5, 6, 7–8 and 10 continue S39 Unknowns 6.2, 3.1–3.3, 4.1–4.4, 5.1–5.3 and 8.1–8.3 respectively; **S39 10.2 (closed as unreachable) is deliberately not re-asked**, and its recommended GitHub #1668 follow-up is recorded under 9.2.

**One deviation from the task prompt, recorded rather than hidden:** the prompt asked for "5 main categories" while listing ten; ten are used. And it asked for metadata on Tasks 2–10; **Task 11 also owns four unknowns**, so it carries the same metadata.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
KU=docs/planning/EPIC_4/SPRINT_40/KNOWN_UNKNOWNS.md
test -f "$KU" && echo "✅ exists" || { echo "KNOWN_UNKNOWNS.md not yet created"; exit 0; }

# Unknown count (excluding any 'Unknown X.Y' template placeholder)
grep -c "^## Unknown [0-9]" "$KU"

# Every unknown carries all 8 sections; the research-time total is DERIVED here
python3 - "$KU" <<'PY'
import re, sys
s = open(sys.argv[1]).read()
req = ['### Priority','### Assumption','### Research Questions','### How to Verify',
       '### Risk if Wrong','### Estimated Research Time','### Owner','### Verification Results']
blocks = [b for b in re.split(r'^## Unknown ', s, flags=re.M)[1:] if re.match(r'\d', b)]
bad = [b.splitlines()[0] for b in blocks if not all(r in b for r in req)]
hrs = 0.0
for b in blocks:
    m = re.search(r'### Estimated Research Time\s*\n+\s*\**~?([\d.]+)', b)
    hrs += float(m.group(1)) if m else 0
print(f"unknowns: {len(blocks)} | missing-section: {len(bad)} {bad or ''} | research hours (derived): {hrs:.1f}")
PY

# Categories: one per priority, Category 1 being the license toolchain (expect 10)
grep -c "^# Category" "$KU"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/KNOWN_UNKNOWNS.md` with ≥ 22 unknowns across 10 categories (one per priority) <!-- figures-ok: 22 is the task's minimum threshold, not a count; actual is 29 -->
- A mapping table from each unknown to its owning prep task
- An `Unknowns Verified:` line added to each of Tasks 2–11 in this plan (Task 12 integrates)
- A lineage note separating Sprint-39-descended unknowns from license-new ones

### Acceptance Criteria

- [x] Document created at `docs/planning/EPIC_4/SPRINT_40/KNOWN_UNKNOWNS.md`
- [x] ≥ 22 unknowns, each with all 8 required sections — **29**, checked by script
- [x] Every Sprint-40 priority (P1–P10) has at least one category — **10 categories, one per priority; the license unlock is Category 1** *(amended from "plus a separate license-unlock category": the task prompt's category list makes the license toolchain its own category, so a second one would duplicate it)*
- [x] Every unknown maps to exactly one owning prep task; none is orphaned — checked by script
- [x] The lnts-landability premise and the installed-license premise are each an explicit unknown — **5.1** and **1.1**
- [x] The research-time total is the figure the verification snippet derives — **33.0 h**

---

## Task 2: Re-Derive the Sprint-39 Baseline & Both License-Gated Populations by Identity

**Status:** ✅ **COMPLETE** (2026-10-13)
**Priority:** Critical
**Estimated Time:** 2-3 hours
**Time Spent:** ~1.5 hours wall-clock (incl. the 11-min leak gate, the 6-min test suite and two 600 s translate timeouts, all waited out rather than worked)
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 3.1 *(also contributes to 2.1 — derived cohort sizes — and 4.1 — the P2 ratchet)*

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/BASELINE_RECONFIRMATION.md`: the Sprint-39 close figures re-derived on current `main` with their commit, and **both license-gated populations recorded as named lists with the predicate that produced them**, so every later task — and the sprint — cites one pinned source instead of re-typing members.

### Why This Matters

Every Sprint-40 acceptance criterion is a delta against this baseline, and two of them (`path_solve_license` **11 → 0**, the P3 corpus decision) are defined over **sets**, not counts. A count catches an omission; only an identity catches a swap (§7.2). The Sprint-39 handoff itself recorded the license cohort as **10 / +10** when the DB said **11** — caught only because it was derived (`../SPRINT_39/SPRINT_LOG.md` §Day 9).

### Background

- **Close figures** (`../SPRINT_39/SPRINT_40_CARRYFORWARDS.md`, measured at `bd2af6e9`): Solve 111 · Match 95 (65 cold + 30 presolve) · Translate 135 · floor 75 · `path_solve_terminated` 0 · model_infeasible 7 · path_syntax_error 6 · `path_solve_license` 11 · all-219 Match 98 · `make test` 5,444 · leak scope 186 · P2 ratchet 9.
- **MCP-gated predicate:** `mcp_solve.outcome_category == "path_solve_license"`.
- **NLP-gated predicate:** `convexity.error == "Model exceeds demo license limits"` (written by `scripts/gamslib/verify_convexity.py`); one member (`andean`) is MIP — excluded by the MINLP/MIP scope rule, never relaxed.
- **The floor is not derivable from the DB** — `floor_tracker.py` reads `data/floor_provenance.json`; the mechanical count yields 65.

### What Needs to Be Done

1. **Diff the anchors:** `git diff --stat bd2af6e9 HEAD -- data/ src/ tests/ scripts/` — record whether anything substantive moved since the close — `scripts/` is included because the baseline figures are produced by tools under `scripts/gamslib` and `scripts/sprint_audit`, so a tooling change is as substantive as a source change.
2. **Run `kpi_block.py` and `floor_tracker.py`** and paste their output verbatim with the commit they report.
3. **Derive both populations by predicate** and record each as a sorted named list, with model type and (for the NLP-gated set) parse/translate status today.
4. **Record per-model size facts** for the MCP-gated cohort — **generated dimensions, not declarations**: run each golden in a scratch directory with `iterlim=0` and read the listing's `MODEL STATISTICS` — `SINGLE EQUATIONS` and `SINGLE VARIABLES`. Counting declarations in the source does **not** measure size (measured 2026-10-12 on `turkey`'s golden: **89** equation blocks vs **3,866** single equations / 3,753 single variables). The demo license prints `MODEL STATISTICS` **before** refusing an over-limit model, so this needs no license (same figures under both editions) — replacing recalled figures (turkey 3,866; tricp 1,255; egypt ~3,470) with measured ones.
5. **Re-derive the P2 ratchet** (`make check-index-repeats`), the leak-gate inventory (`make check-goldens`, **run alone**), **and `make test` explicitly** — run it (alone, never alongside the leak gate) and record `N passed, M skipped` with the commit, **even though this task is docs-only and its quality gate is N/A**: the baseline's `make test` figure (5,444 at the S39 close) is a close figure like any other, and the gate's waiver must not become a reason to re-quote it.
6. **Record a verdict per figure:** ✅ reproduces / ❌ differs (with the difference routed).

### Changes

- **NEW** `docs/planning/EPIC_4/SPRINT_40/BASELINE_RECONFIRMATION.md` — anchor diff, verbatim KPI/floor output, both populations by identity with predicates, the NLP-gated set's type/parse/translate table, cohort sizes as generated dimensions, the P2 ratchet breakdown, leak gate and test suite, a verdict per figure with routing
- `KNOWN_UNKNOWNS.md` — Unknown **3.1** → ✅ VERIFIED (in scope, and most parse), with the 4/9 translate gap recorded as a separate routed finding; contribution notes under **2.1** (cohort sizes) and **4.1** (ratchet), statuses left to Tasks 7 and 10
- `CHANGELOG.md` — Sprint 40 Prep Task 2 entry

### Result

✅ **COMPLETE — the Sprint 39 baseline reproduces exactly at `366e91f3`; Unknown 3.1 holds, but only 4 of the 9 NLP-gated models translate today.**

**Nothing moved since the close:** `git diff bd2af6e9 HEAD -- data/ src/ tests/ scripts/` is empty (only `docs/` and `CHANGELOG.md` changed). **Every KPI reproduces** — Solve 111 · Match 95 (65 + 30) · Translate 135 · Parse 142 · floor **75** (provenance file; mechanical 65) · pst 0 · mi 7 · pse 6 · `path_solve_license` 11 · all-219 98 — and so do the P2 ratchet (**9 = baseline 9**, turkpow ×3), the leak gate (**186** in-scope clean, run alone) and the test suite (**5,444 passed, 10 skipped**, run explicitly and alone).

**Both populations are now pinned by identity** (`BASELINE_RECONFIRMATION.md` §3): the 11 MCP-gated models, and the 10 NLP-gated models of which `andean` is MIP-excluded.

**Two findings:**

1. **Only 4 of the 9 in-scope NLP-gated models reach a translated MCP today** — a separate finding from **Unknown 3.1, which is ✅ VERIFIED** (all nine in scope by type, none of the six that parse a multi-solve driver, and **6/9 parse**, the majority the assumption expected) (`emfl`, `indus89`, `phosdis` fail on `%new%`, `Singleton Set` and `for … to …` loops) and **4/9 translate** (`airsp` and `msm` time out at 600 s, cause undiagnosed). Routed to Task 6 (the corpus brief must show what each option would actually admit), Task 7 (end-to-end only for the four) and Sprint 40 P3.
2. **egypt's recalled size was approximate:** measured **3,447** single equations / **3,537** variables, not "~3,470". Sizes are now measured for all 11 as generated dimensions — **identical under the demo and the effective license**, so the measurement is license-free — e.g. turkey 3,866 (89 equation blocks), ferts 5,702, srpchase 4,005.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
git rev-parse --short HEAD
git diff --stat bd2af6e9 HEAD -- data/ src/ tests/ scripts/ | tail -1

# Headline KPIs + floor, each carrying its commit
.venv/bin/python scripts/sprint_audit/kpi_block.py
.venv/bin/python scripts/sprint_audit/floor_tracker.py | tail -3

# Both populations BY IDENTITY
.venv/bin/python - <<'PY'
import json
db = json.load(open("data/gamslib/gamslib_status.json"))
mcp = sorted(m["model_id"] for m in db["models"]
             if (m.get("mcp_solve") or {}).get("outcome_category") == "path_solve_license")
nlp = sorted((m["model_id"], m.get("gamslib_type")) for m in db["models"]
             if (m.get("convexity") or {}).get("error") == "Model exceeds demo license limits")
print("MCP-gated", len(mcp), mcp)
print("NLP-gated", len(nlp), nlp)
PY

# P2 ratchet (expect 9 = baseline 9 unless something landed)
make check-index-repeats 2>&1 | tail -3

# The test count, re-derived EXPLICITLY (independent of whether the quality gate applies);
# run alone, never concurrently with the leak gate
make test 2>&1 | tail -3

test -f docs/planning/EPIC_4/SPRINT_40/BASELINE_RECONFIRMATION.md && echo "✅ doc" || echo "doc not yet created"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/BASELINE_RECONFIRMATION.md` — figures with commit, both named populations with predicates, per-model size facts, a verdict per figure
- The MCP-gated and NLP-gated lists in a form Tasks 6, 7 and 12 cite rather than copy
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1

### Acceptance Criteria

- [x] Every close figure re-derived by tool at a stated commit, none hand-counted
- [x] Both populations recorded as **named lists** with the predicate that produced them
- [x] `andean` recorded as MIP-excluded, with the scope rule cited
- [x] Cohort size facts derived from the goldens, not recalled
- [x] The leak gate run **alone** and its scope line recorded (186 or the difference explained)
- [x] `make test` run **explicitly** and its `N passed, M skipped` recorded with the commit — not re-quoted from the S39 close because the task's quality gate is N/A
- [x] Any figure that differs from the close is routed, not silently replaced
- [x] Unknowns 3.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Prove the Effective License — Precedence & Per-Solver Fail-Capable Probes

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team (license file placement: project owner)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.5

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/LICENSE_PROBE.md`: **which license file GAMS actually reads** (the user-level evaluation license, or the system-directory demo file still present), shown by evidence; and **four probes — LP, NLP, QCP and MCP, each sized above its own demo ceiling** (**per model-type demo ceilings** — linear models (LP, CPLEX) are refused only above **2,000** rows/columns; nonlinear types (NLP via CONOPT, MCP via PATH) above **1,000**) — run **on the demo and on the effective license**, showing each fails on one and solves on the other — plus a **non-identifying regex** that distinguishes the two editions in a `.lst` file (recorded with its classification results, never with raw header text), which Task 5's `license_edition` writer will key on — **and a first license-neutrality sample** (Unknown 1.5): a stratified set of models **outside** both gated populations re-solved under the effective license and diffed against the DB.

### Why This Matters

Every license-dependent result in Sprint 40 is only as good as the evidence that the licensed edition produced it. As of 2026-10-12 the license is installed at the **user level** and the log header reports an evaluation license, but the **system-directory** `gamslice.txt` is still the 2026-07-13 demo file — so "the license is installed" and "every pipeline invocation runs licensed, for every solver" are **different claims**, and only the second is evidence. A probe that only ever runs licensed cannot distinguish "licensed" from "the probe was too small to hit the limit" — the vacuous-pass failure §7.5 names.

### Background

- **The demo limit is enforced at solve time**: `scripts/gamslib/test_solve.py` and `verify_convexity.py` both detect it by `.lst` substring (`"exceeds the demo license limits"`). The limits are **per model type**: **2,000** rows/columns for linear models (LP) and **1,000** for nonlinear types (NLP, MCP, …) (measured 2026-10-12 under the system-directory demo file: a 1,500-row LP **solved Optimal**, a 2,500-row LP and a 1,500-row NLP were **refused**; both solved under the effective license — so an LP probe sized "just over 1,000" cannot fail on the demo, and would be a vacuous control).
- **`gams audit lo=2`** prints version information; whether it prints the edition is itself unknown — the `.lst` header's solver-licensing line is the other candidate source (described, never quoted: header content is not committed).
- **`src/ir/preprocessor.py`** emulates `%system.license%`-style attributes with a `"gams.license": "demo"` stub — record whether it matters for any model (it is a parse-time emulation, not a solve-time check).
- **Sensitive data:** never commit, paste or quote any part of the license text in a doc, a log or a PR.

### What Needs to Be Done

1. **Establish precedence by evidence:** with both files present, which does GAMS read? Move the user-level file aside, re-run, restore — **fail-safe:** copy it to a backup **outside the repo** first and install an `EXIT`/`INT`/`TERM` **trap** that moves it back, so an interruption or failed command cannot leave the demo silently effective; **after restoring, re-check the edition** (the restored file is byte-identical to its pre-test checksum **and** a probe listing classifies as licensed) before any later measurement. *(Prefer pointing `license=` at the system-directory demo file wherever that suffices — it displaces nothing.)* Check every invocation path the pipeline uses (`shutil.which("gams")`, subprocesses). Recommend whether the system-directory demo file should also be replaced.
2. **Build four probes from one scalable synthetic model** with a size parameter — **LP** (CPLEX, as `verify_convexity.py` uses `LP=CPLEX`) sized **above 2,000**; **NLP** (CONOPT) **above 1,000**; **QCP above 1,000**, run with `verify_convexity.py`'s own `NLP=CONOPT` option so it exercises the pipeline's real path for `emfl` — **`NLP=` does not select the QCP solver**, so record which solver the listing actually reports (measured 2026-10-12: QCP solver selection is **independent of `NLP=`** — `NLP=IPOPT` still ran CONOPT, `QCP=IPOPT` ran IPOPT; on this install the **default QCP solver is CONOPT**; the demo refused a 1,500-row QCP and allowed a 900-row one); **MCP** (PATH) **above 1,000**. Each must exceed **its own** model type's ceiling, or its demo run cannot fail. Run each also just *under* its ceiling on the demo, to show the size parameter is what flips the result.
3. **Run each on the demo** (`license=` pointed at the system-directory demo file) — record the refusal line verbatim (the positive control: each probe *can* fail).
4. **Run each under the effective license** — record `MODEL STATUS`, the solver line and the **edition classification only** (`licensed` / `demo`). **Inspect `gams audit lo=2` locally but never persist its output** — it can carry the licensee, license ID, license path and node details; record only whether it exposes a usable, non-identifying edition discriminator. A license that lifts the limit for one solver but not another would split P2/P3 by license.
5. **Identify a non-identifying discriminator** for licensed vs. demo `.lst` headers and record **only the regex and its classification results** (each paired file → `licensed` / `demo`, plus the inverted-pattern control) — **never the raw header lines**. Task 5's parser keys on the regex.
6. **License-neutrality sample** (Unknown 1.5): re-solve a stratified sample of models **outside both gated populations** — e.g. 5 cold matches, 5 presolve matches, 1 per failure bucket, named by identity — under the effective license, in a throwaway worktree, and diff outcome / objective / comparison verdict against the DB. **Positive control (synthetic — never a real gated model):** run the **same diff procedure** on Task 3's synthetic over-ceiling NLP probe, demo vs effective license; the procedure **must** report the change. A real size-refused DB model cannot serve: every such model is, by definition, in the MCP-gated or NLP-gated population, and reading its licensed outcome before Task 6's answers are committed would break the blind-decision boundary. Any other row that moves is a toolchain finding to route before any KPI is read. The sprint's first licensed full run is the exhaustive test; this is the early warning.
7. **Record operational facts** Task 4 needs: the license file's install path, whether it is node-locked or otherwise bound, its expiry if any.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
DOC=docs/planning/EPIC_4/SPRINT_40/LICENSE_PROBE.md
test -f "$DOC" && echo "✅ doc" || echo "LICENSE_PROBE.md not yet created"

# Edition evidence, from a scratch dir (never the repo root: GAMS writes next to cwd)
SCR=$(mktemp -d) && cd "$SCR"
printf 'variable x; equation e; e.. x =e= 1; model m /all/; solve m using lp minimizing x;\n' > p.gms
gams p.gms lo=0 >/dev/null 2>&1; grep -i -m2 "licensed\|demo" p.lst | cut -c1-80
cd - >/dev/null

# The doc must record BOTH runs: the demo refusal (positive control) and the licensed solve
grep -c "exceeds the demo license limits" "$DOC" 2>/dev/null
grep -c "MODEL STATUS" "$DOC" 2>/dev/null

# No license text leaked into the repo — FAIL-CLOSED, never prints a match.
# Patterns are built from the effective license file at run time and deleted;
# the positive control is the same scan run against the license file itself.
LIC="${GAMS_LICENSE_FILE:-$HOME/Library/Application Support/GAMS/gamslice.txt}"
PAT=$(mktemp); sed 's/^[[:space:]]*//;s/[[:space:]]*$//' "$LIC" | awk 'length>=8' > "$PAT"
grep -q -F -f "$PAT" "$LIC" || { rm -f "$PAT"; echo "❌ control failed: scan cannot see the license"; exit 1; }
# --untracked: also scan files not yet added (e.g. LICENSE_PROBE.md before its first
# commit); git-ignored files are still skipped. Run this BEFORE committing.
# Each scan checks git grep's OWN status: 0 = hit, 1 = clean, >1 = ERROR (e.g. a
# missing pattern file exits 128). `| wc -l` would turn an error into a clean "0".
scan() { local out rc; out=$(git grep --untracked -l "$@" -- .); rc=$?
  if [ "$rc" -gt 1 ]; then echo "❌ scan ERROR (git grep rc=$rc) — not a clean result" >&2; exit 2; fi
  printf '%s' "$out" | grep -c . || true; }   # grep -c exits 1 on a zero count; that is a clean 0, not an error
N1=$(scan -F -f "$PAT") || exit 2; rm -f "$PAT"
# Fragments of the license's ID-like runs (alphanumeric runs of >= 12 chars that
# contain a digit): every 12-char window, so a PARTIAL quote of such a run is caught.
WIN=$(mktemp); grep -oE '[A-Za-z0-9]{12,}' "$LIC" | grep -E '[0-9]' \
  | awk '{for(i=1;i<=length($0)-11;i++) print substr($0,i,12)}' | sort -u > "$WIN"
N3=$(scan -F -f "$WIN") || exit 2; rm -f "$WIN"
# Header fields that identify the license but are not lines of the file. The regex
# is written so it cannot match its own text (an unredacted 'Licensee:' line has a
# space then an alphanumeric; '<redacted>' does not match).
N2=$(scan -E 'Licensee:[[:space:]]+[[:alnum:]]|node:[0-9]') || exit 2
# ⚠ LIMITED, not proof: measured 2026-10-12, these catch whole license lines, header
# fields and fragments of ID-like runs, but only 4 of 24 planted 14-char fragments
# taken from arbitrary positions in the license's lines (readable text and short
# tokens cannot be matched without false positives). The MANUAL REVIEW below is
# mandatory and is the actual guarantee.
[ "$N1" -eq 0 ] && [ "$N2" -eq 0 ] && [ "${N3:-0}" -eq 0 ] && echo "✅ automated scans clean (limited — complete the manual review)" \
  || { echo "❌ license-identifying text in $N1 + $N2 + ${N3:-0} tracked/untracked file(s)"; exit 1; }
# MANUAL REVIEW (mandatory): read `git diff main --` (working tree + index vs main --
# staged, unstaged AND committed; `git diff main...HEAD` is commits-only and empty on a
# first commit) and every untracked file (`git ls-files --others --exclude-standard`) before
# committing; confirm no license line, header excerpt, ID, node or licensee text,
# whole or partial, and record "manual license review: done" in the task's Result.
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/LICENSE_PROBE.md` — the precedence finding; the four probes (LP > 2,000, NLP > 1,000, QCP > 1,000 with its actual solver recorded, MCP > 1,000) with demo refusal (verbatim) and licensed solve for each; the edition-discriminating regex with its classification results (no raw header text)
- A recommendation on replacing the system-directory demo file (owner action)
- The license-neutrality sample: the named models, their before/after outcome, objective and verdict (none of them gated), and the **synthetic** positive control's demo-vs-licensed change
- Operational facts for Task 4 (install path, binding, expiry)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.5

### Acceptance Criteria

- [ ] Which license file GAMS reads is shown by evidence, not assumed
- [ ] **Each** of the LP, NLP, QCP and MCP probes is sized above its own demo ceiling and **fails on the demo** with the refusal line recorded — the positive control
- [ ] The same four probes **solve under the effective license** with `MODEL STATUS` recorded, and the **QCP probe's actual solver** is recorded
- [ ] A non-identifying edition-discriminating regex identified for `.lst` files, recorded **with its classification of every paired file and its inverted-pattern control** — no raw header text committed
- [ ] No part of the license text appears in any committed file, log excerpt or PR — the automated scans in *Verification* pass **and the mandatory manual review is recorded as done**. The scans are **limited** (measured: whole lines, header fields and ID-run fragments are caught; arbitrary partial quotes mostly are not), so the review, not the scan, is the guarantee
- [ ] A license-neutrality sample of named models outside both populations is re-solved and diffed against the DB, **with a synthetic positive control** (Task 3's over-ceiling probe, through the same diff procedure, must change) — **no gated model's result is read**; every other moved row is routed
- [ ] Direct GAMS probes run from a scratch directory; pipeline invocations (the neutrality sample) run in their normal cwd **inside the disposable worktree**; none runs in the main checkout
- [ ] Unknowns 1.1, 1.2 verified and updated in KNOWN_UNKNOWNS.md; **Unknown 1.5 resolved as far as a sample can** — ❌ if the sample refutes it, otherwise the existing status `🔍 **Status:** INCOMPLETE — sample-neutral at `<sha>`; universal claim routed to the first licensed full run` (never ✅ from the sample)

---

## Task 4: CI License-Isolation Design & Workflow Inventory

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team (environment creation + secret: project owner)
**Dependencies:** Tasks 1, 3
**Unknowns Verified:** 1.3

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/CI_LICENSE_DESIGN.md`: an inventory of every workflow (trigger, whether it installs GAMS, whether it runs PR-controlled code, any demo-motivated exclusion), and a design for the **trusted licensed workflow** — triggers, protected environment, branch policy, secret handling, what it covers — that P1 implements without re-deciding.

### Why This Matters

PR #1745's review found that both GAMS-installing workflows trigger **only on `pull_request`** and run PR-controlled code (`pip install -e .`, repository scripts), so a license secret given to them can be exfiltrated — **same-repository PRs included**; masking and log-scanning cannot stop an encoded or network exfiltration. The plan now keeps PR jobs demo-only and puts the license in a separate `main`-only workflow. That design has load-bearing details (environment branch policy vs. `workflow_dispatch` from another ref; never `pull_request_target` with a PR-head checkout) that must be verified against GitHub's actual behaviour, not assumed.

### Background

- **Installs GAMS:** `.github/workflows/pr19-emit-solve-validation.yml`, `.github/workflows/presolve-divergence.yml` — both pinned to the 54.2.1 `linux_x64_64_sfx.exe` with a SHA-256 guard, in a step named *"Install GAMS demo"*, `pull_request` trigger with path filters.
- **Does not install GAMS — EIGHT workflows, not the plan's "other four":** `ci.yml`, `gamslib-regression.yml`, `golden-staleness.yml`, `lint.yml`, `nightly.yml`, `performance-check.yml`, `phase0-gate.yml`, `publish-pypi.yml` (derived 2026-10-12 with the *Verification* loop below, at `912d005c`). `../PROJECT_PLAN.md` Sprint 40 P1 names only the first four by name and says *"confirm that at prep from the files, do not take it from this line"* — the count was wrong, the conclusion (none installs GAMS) holds. Re-run the loop; do not take this line either.
- **Secrets in use today:** only `publish-pypi.yml` (`PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`).
- **Precedent:** the S35 Day-6 demo-expiry incident (53.1.0 demo expired ~2026-07-29; every solve returned rc=7) — the edition-printing `gams audit lo=2` line exists because of it.

### What Needs to Be Done

1. **Inventory all workflows** from the files: trigger(s), path filters, GAMS install (yes/no), secrets referenced, PR-code execution (yes/no). Record by name, not count.
2. **Catalog demo-motivated exclusions**: model lists, tiers or skips whose comment or history attributes them to the 1,000-row limit (e.g. `.github/path-solve-ci-targets.txt`, the PR19 tier definitions).
3. **Design `licensed-solve.yml`**: triggers (`push` to `main`, `schedule`, `workflow_dispatch`); the `gams-licensed` environment with a **`main`-only deployment-branch policy** and optional required reviewers; secret written to `$GAMS_DIR/gamslice.txt` at run time **and removed by an always-run cleanup step** (`if: always()`, deleting the file and any copy of it) so it does not outlive the job — on a GitHub-hosted runner the VM is discarded anyway, but the step is mandatory because a **self-hosted fallback is only acceptable as a dedicated, ephemeral runner** (fresh per job, registered to this one workflow, **never** eligible to run PR-controlled code), where a leftover file could otherwise be read by a later job; `::add-mask::` per line; in-job output scan with its positive control; what it runs (the two cohorts + each PR workflow's skipped large tier).
4. **Verify the branch-policy claim empirically** — documentation alone is **not** sufficient, because this policy is the control that keeps the license secret from unmerged refs: in a **throwaway test repository**, create an environment with a `main`-only deployment-branch policy and a dummy secret; dispatch from a **non-`main`** branch and record the **refusal** (the negative control), then from **`main`** and record **access**. Cite GitHub's documentation alongside, not instead. Delete the throwaway repository afterwards.
5. **Design the PR-side change**: rename the step, the large-tier skip-with-notice, and the edition print.
6. **Write the owner checklist** for Task 6: license terms for hosted runners; environment creation; reviewer requirement; where the secret is stored (environment only, **not** repository-wide).

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
# Inventory by identity: which workflows install GAMS, and what triggers them
for f in .github/workflows/*.yml; do
  inst=$(grep -c -i "gams-installer\|Install GAMS" "$f")
  trig=$(sed -n '/^on:/,/^[a-z]/p' "$f" | grep -oE "pull_request_target|pull_request|push|schedule|workflow_dispatch" | sort -u | tr '\n' ' ')
  echo "$(basename "$f"): installs_gams=$inst triggers=[$trig]"
done
# Secrets referenced today
grep -rn "secrets\." .github/workflows/ | cut -c1-120

DOC=docs/planning/EPIC_4/SPRINT_40/CI_LICENSE_DESIGN.md
test -f "$DOC" && echo "✅ doc" || echo "CI_LICENSE_DESIGN.md not yet created"
grep -c "pull_request_target" "$DOC" 2>/dev/null   # the design must address it explicitly
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/CI_LICENSE_DESIGN.md` — workflow inventory, demo-exclusion catalog, `licensed-solve.yml` design, PR-side change, owner checklist
- A recorded **throwaway-repository run** showing the environment refuses a non-`main` dispatch and admits a `main` dispatch (documentation cited alongside, never in place of it)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3

### Acceptance Criteria

- [ ] Every workflow inventoried by name with trigger and GAMS-install status, derived from the files
- [ ] The design gives the secret to **no job that runs PR code** — same-repo PRs included
- [ ] The `main`-only branch-policy claim is verified **empirically** in a throwaway repository — non-`main` refusal **and** `main` access both observed — not assumed and not by citation alone
- [ ] `pull_request_target` with a PR-head checkout is explicitly ruled out
- [ ] Masking + output scan are described as defence in depth, with the scan's positive control
- [ ] The post-merge detection trade-off is stated
- [ ] Unknowns 1.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Schema 3.1.0 `license_edition` Design

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 3
**Unknowns Verified:** 1.4

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/SCHEMA_3_1_0_DESIGN.md`: the exact field definitions, every writer and initializer touched, the migration's behaviour on existing rows, and the test list — derived from the code, so P1 implements a closed list rather than discovering writers mid-sprint.

### Why This Matters

`data/gamslib/schema.json` is at **3.0.0** and both result types a license-dependent stage writes declare `additionalProperties: false` — an un-migrated field **fails validation**. PR #1745's review found the plan's first writer list incomplete twice over (the convexity record lacks `gams_version` entirely; `db_manager.py` hard-codes the canonical version for `--empty` and lists the migration chain). A third omission found mid-sprint would land after the P2 batch had already written rows without their edition.

### Background

- **Sprint 39 P7** did the last schema bump (2.2.1 → 3.0.0, `mcp_file_used` → `mcp_file_generated`): `scripts/gamslib/migrate_schema_v3.0.0.py`, `tests/gamslib/test_migrate_schema_v3.py`, and the `db_manager.py` comments explaining why `--empty` stamps the canonical version (`../SPRINT_39/PRESOLVE_RECORD_REMEDY.md` §9).
- **Known writers:** `scripts/gamslib/test_solve.py` (MCP solve record; `extract_gams_version`), `scripts/gamslib/run_full_test.py` (the `gams_version` passthrough), `scripts/gamslib/verify_convexity.py` (convexity record).
- **Research:** `docs/research/JSON_SCHEMA_BEST_PRACTICES.md`, `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md` — additive-change and versioning conventions.

### What Needs to Be Done

1. **Enumerate every writer by grep**, not by recall: every assignment into `mcp_solve` / `convexity` dicts and every `schema_version` literal. **the convexity write path has two pieces the verifier does not cover**: `scripts/gamslib/migrate_catalog.py` (~L156–181) is what **constructs the DB's nested `convexity` object** (from `catalog.json`'s flat fields), and **no command today applies `verify_convexity.py`'s output JSON to `gamslib_status.json`** — so a P3 **application writer** must be designed (and is where KU 3.3's corpus hold lives). Adding fields to `VerificationResult` alone does not reach `convexity_result`: the design must cover **`migrate_catalog.py`** and **define the P3 application writer** (output JSON → `convexity_result`, carrying `license_edition`, `gams_version` and the solver), with tests for both.
2. **Define the fields**: `license_edition` (`"licensed"` / `"demo"` / `null`) in both result types; `gams_version` in `convexity_result`. State the null semantics — **unrecorded, never a guessed `"demo"`**.
3. **Specify the parser extension** to `extract_gams_version` using Task 3's discriminating string; reuse, do not duplicate. **For `verify_convexity.py` this is more than a parser call:** `verify_convexity.py` cannot supply provenance itself: `verify_model` writes its listing to `output.lst` inside a `tempfile.TemporaryDirectory` that is deleted on return, and its `--output` JSON (`VerificationResult.to_dict()`) carries a numeric `solver_status` but **no solver name and no edition** (verified at `912d005c`). The design must read the edition **and the solver name** from the listing **before** the temporary directory is removed, and add both to `VerificationResult` (and so to `--output`); they reach `convexity_result` **only through** the P3 application writer of step 1.
4. **Specify the migration** (`migrate_schema_v3.1.0.py`): additive, idempotent, `null` for existing rows, chain position after 3.0.0 — and it **refreshes the top-level `updated_date`** alongside `schema_version`, as `migrate_schema_v3.0.0.py` does (lines ~151–157, citing `schema.json`'s "timestamp of last modification" and PR #1740's stale-provenance finding) and every prior migration does.
5. **Specify the `db_manager.py` changes**: `--empty` stamp 3.0.0 → 3.1.0 and its comment; the catalog-init warning's chain.
6. **List the tests**: migration test (including an assertion that `updated_date` is refreshed); schema tests (accepts new fields, **still rejects an unknown key**); writer tests per stage from **synthetic, non-identifying** licensed and demo listing snippets (hand-written edition lines, or fixtures generated at test runtime) — **never real `.lst` license-header excerpts**, which would commit licensee, ID or node data; updated `test_db_manager.py` regressions.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
# Current contract
python3 -c "import json;s=json.load(open('data/gamslib/schema.json'));d=s.get('definitions') or s.get('\$defs');[print(k,'additionalProperties=',d[k].get('additionalProperties'),'gams_version' in d[k].get('properties',{})) for k in ('mcp_solve_result','convexity_result')]"
grep -n '"schema_version"' data/gamslib/gamslib_status.json | head -1

# Every schema_version literal and every gams_version writer (the closed list to design against)
grep -rn '"3\.0\.0"' scripts/ tests/ | grep -v __pycache__ | cut -c1-120
grep -rn "gams_version" scripts/gamslib/*.py | grep -v "migrate_" | cut -c1-120

DOC=docs/planning/EPIC_4/SPRINT_40/SCHEMA_3_1_0_DESIGN.md
test -f "$DOC" && echo "✅ doc" || echo "SCHEMA_3_1_0_DESIGN.md not yet created"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/SCHEMA_3_1_0_DESIGN.md` — fields, null semantics, closed writer list, parser extension, migration spec, `db_manager` changes, test list
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.4

### Acceptance Criteria

- [ ] Writer list derived by grep and recorded with the command that produced it
- [ ] Both `mcp_solve_result` and `convexity_result` covered; `gams_version` added to the latter
- [ ] Null semantics stated: existing rows are unknown, never back-filled as `"demo"`
- [ ] `db_manager.py` `--empty` stamp and catalog-init chain included
- [ ] Test list includes "still rejects an unknown key"
- [ ] Unknowns 1.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Owner Decision Brief — Floor Provenance, Corpus Entry & Hosted Runners (written blind)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 2-3 hours
**Deadline:** Before Task 7 runs — the brief **and the owner's three dated answers** must both be committed first
**Owner:** Development team (brief); project owner (decisions)
**Dependencies:** Tasks 1, 2, 3, 4
**Unknowns Verified:** 3.3

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/OWNER_DECISION_BRIEF.md` posing the three owner decisions (scheduled for Day 0 in `PROJECT_PLAN.md`; taken **in prep** here, before Task 7) with their options and consequences — **written and answered before any cohort result exists** (the boundary is the start of Task 7's cohort measurement; Task 3's synthetic probes and neutrality sample, which this task depends on, are not cohort results), and decided before Task 7's results are read.

### Why This Matters

Sprint 39 P1 spent a Day-0 decision on a floor classification that the Sprint-38 closer discovered at close, in the favourable direction, and correctly refused to self-approve. Sprint 40 is about to generate up to twenty such classifications at once. **A rule written after the results is a rule fitted to them.** The three decisions:

1. **Floor provenance:** a license-unlocked cold match is neither *methodology* (the emit was never byte-identical-to-pre-fix and matching via warm start) nor *fix-driven genuine* (no emit changed). New `limb` in `data/floor_provenance.json`, or explicit exclusion?
2. **Corpus entry:** admitting any NLP-gated model moves the denominator off 142. Admit by rule (e.g. "classifies `verified_convex`/`likely_convex` by the existing verifier"), admit case-by-case, or hold at 142 for Epic 4 and record the set as Epic-5 scope?
3. **CI license use:** do the license terms permit GitHub-hosted ephemeral runners; create `gams-licensed` with required reviewers or not?

### Background

- `data/floor_provenance.json` + `scripts/sprint_audit/floor_tracker.py` — the floor's per-model provenance and limbs (`presolve-match-genuine` added in Sprint 39 P1).
- `../SPRINT_39/FLOOR_DECISION_BRIEF.md` — the format that let an owner answer in one sitting: evidence, counter-argument, consequences, and **the exact edit each answer implies**.
- Scope-change precedent: Sprints 23–25 each changed the pipeline scope (160 → 147 → 143 → 142) and footnoted it in the Rolling-KPIs table (`../PROJECT_PLAN.md` footnotes ³, ⁴, ⁶).
- `docs/research/gamslib_kpi_definitions.md` — how the corpus and the KPIs are defined.

### What Needs to Be Done

1. **State each decision as a question with 2–4 options**, each with its consequence for the reported figures and the exact file edit it implies.
2. **Floor:** argue both sides of "license-unlocked matches count toward the genuine floor"; recommend, but leave the decision to the owner.
3. **Corpus:** show how each option changes the headline denominators, and how Sprint 40 would report both (142-continuity + expanded) in one sentence.
4. **CI:** carry Task 4's owner checklist verbatim, with Task 3's node-locking/binding evidence — both are inputs, which is why this task depends on Tasks 3 and 4.
5. **Record the owner's answers in the brief** — one `**Owner answer (YYYY-MM-DD):** …` line under each `## Decision` — and commit them **before Task 7 runs**. The property that matters is that the **last commit that changed any part of a `## Decision` block** (question, options, consequences, exact edits or answer) is a **strict ancestor of Task 7's first commit**, and that **every Task-7 measurement SHA descends from it**; the brief's creation date alone proves nothing (answers could be filled in later, and commit timestamps do not prove history order). **After Task 7 starts, do not edit any `## Decision` block** — a changed decision is recorded as a new, dated decision in the sprint's own docs.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
DOC=docs/planning/EPIC_4/SPRINT_40/OWNER_DECISION_BRIEF.md
test -f "$DOC" && echo "✅ doc" || { echo "OWNER_DECISION_BRIEF.md not yet created"; exit 0; }

# Decided blind -- three checks, each failing with a non-zero exit:
#  (1) STRUCTURE: the answers commit holds exactly three "## Decision" blocks, each
#      with exactly ONE non-empty dated owner answer INSIDE that block (three answers
#      under one heading, a fourth answer, or an answer placed under a later
#      non-Decision heading such as "## Notes" all fail);
#  (2) ORDER: the LAST commit that changed ANY PART OF A DECISION BLOCK -- question,
#      options, consequences, exact edits or answer -- is a STRICT ancestor of the
#      first commit adding the dry-run doc. Fingerprinting only the answer lines would
#      let a decision's wording be refitted after the results while the answer line
#      stays put. Sections outside the "## Decision" blocks may still be edited;
#  (3) MEASUREMENT: every measurement SHA Task 7 records on its "**Measured at:**"
#      line (the head_sha of every retained invocation) DESCENDS from that answers
#      commit -- so the cohort runs, not just the results commit, came after it.
ANS_RE='^\*\*Owner answer \([0-9]{4}-[0-9]{2}-[0-9]{2}\):\*\* *[^ ]'
# Any "## " heading CLOSES the current block; only "## Decision" opens one. An answer
# outside an open Decision block (intro, "## Notes", appendix) is stray and fails.
# ("### " sub-headings do not match "^## " and so stay inside their Decision.)
valid() { awk '/^## / { inb = ($0 ~ /^## Decision/); if (inb) { n++; c[n] = 0 }; next }
  /^\*\*Owner answer \([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\):\*\* *[^ ]/ { if (inb) c[n]++; else stray++ }
  END { if (n != 3 || stray) exit 1; for (i = 1; i <= 3; i++) if (c[i] != 1) exit 1 }'; }
# Every line of every "## Decision" block (heading to the next non-Decision "## "
# heading or EOF) -- the whole decision, not just its answer line.
blocks() { awk '/^## /{ inb = ($0 ~ /^## Decision/) } inb'; }
LAST=""; PREV=""
for c in $(git log --reverse --format=%H -- "$DOC"); do
  A=$(git show "$c:$DOC" 2>/dev/null | blocks)
  [ "$A" != "$PREV" ] && { LAST=$c; PREV=$A; }
done
DRY_DOC=docs/planning/EPIC_4/SPRINT_40/COHORT_DRY_RUN.md
DRY=$(git log --diff-filter=A --format=%H -- "$DRY_DOC" | tail -1)
if [ "$(blocks < "$DOC")" != "$PREV" ]; then echo "❌ uncommitted edits to a decision block"; exit 1
elif [ -z "$LAST" ] || ! git show "$LAST:$DOC" | valid; then echo "❌ the answers commit does not hold exactly one dated answer under each of exactly three ## Decision headings"; exit 1
elif [ -z "$DRY" ]; then echo "✅ answers last changed at ${LAST:0:8}; dry run not yet committed"
elif [ "$LAST" = "$DRY" ]; then echo "❌ answers committed in the SAME commit as the dry run (${DRY:0:8}) — a commit is its own ancestor, so the check must be strict"; exit 1
elif ! git merge-base --is-ancestor "$LAST" "$DRY"; then echo "❌ a decision block (question, options or answer) was committed or REVISED at ${LAST:0:8}, which the dry run (${DRY:0:8}) does not descend from"; exit 1
else
  SHAS=$(grep -m1 '^\*\*Measured at:\*\*' "$DRY_DOC" | grep -oE '[0-9a-f]{40}' | sort -u)
  [ -z "$SHAS" ] && { echo "❌ COHORT_DRY_RUN.md records no full measurement SHA on a **Measured at:** line"; exit 1; }
  for s in $SHAS; do
    git merge-base --is-ancestor "$LAST" "$s" 2>/dev/null \
      || { echo "❌ a measurement ran at ${s:0:8}, which does not descend from the answers commit ${LAST:0:8}"; exit 1; }
  done
  echo "✅ answers (${LAST:0:8}) precede the dry-run commit (${DRY:0:8}) and all $(echo $SHAS | wc -w | tr -d ' ') measurement SHA(s)"
fi

# Three decisions posed
grep -c "^## Decision" "$DOC"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/OWNER_DECISION_BRIEF.md` — three decisions, options, consequences, exact edits
- The owner's three answers, each recorded as a dated `**Owner answer (YYYY-MM-DD):**` line under its decision, committed before Task 7 runs
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.3

### Acceptance Criteria

- [ ] All three decisions posed with options and the exact edit each implies
- [ ] **Exactly one dated owner answer under each of exactly three `## Decision` headings** (`**Owner answer (YYYY-MM-DD):**`) — posing the questions is not completion, and three answers under one heading or a fourth answer fail
- [ ] The **last commit that changed any part of a `## Decision` block** (question, options, consequences, exact edits or answer) holds all three answers and is a **strict ancestor** of the first commit adding `COHORT_DRY_RUN.md` (an earlier, different commit — Git counts a commit as its own ancestor) — so answers revised after the dry run, or committed together with it, fail; **and every measurement SHA on `COHORT_DRY_RUN.md`'s `**Measured at:**` line descends from the answers commit**, so the cohort runs themselves came after the answers (all checked by `git merge-base --is-ancestor` in *Verification*)
- [ ] The corpus option shows both denominators reported in one sentence
- [ ] No result from either cohort is cited in the brief
- [ ] Unknowns 3.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: License-Gated Cohorts Dry Run — Fingerprints & Routing

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Tasks 2, 3, 6
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4, 3.2

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/COHORT_DRY_RUN.md`: the first licensed measurement of both populations — **in a throwaway `git worktree`, never persisted to the committed DB or goldens** (the run writes its rows into the **worktree's own DB copy**, which is how each match's recorded attribution is read, and is discarded with the worktree) — with per-model fingerprints and a pre-registered routing for every non-match, so P2/P3 open on a known work list.

### Why This Matters

None of the eleven MCP-gated emits has ever been exercised by a solve, and none of the nine in-scope NLP-gated models has ever been classified. The sprint's dominant risk is a **cascade of first-time fingerprints** pulling it into open-ended diagnosis. A prep dry run turns that cascade into a list with a size, before Day 1 — and it is where egypt and shale first get the solve that P4's Class-A fixes need to be verified against.

### Background

- **Known going in** (`../PROJECT_PLAN.md` Sprint 40 P2): egypt and shale carry a **live** P10 Class-A emit defect (expect mismatch); ferts's emit was corrected Sprint 38 Day 11; tricp carries the S38 D11 `slp(n,n)` fix and the **untriaged** `docs/issues/ISSUE_933_tricp-mcp-compilation-errors.md`; turkey is the S35 `$161` "licensed testbed +1"; **robot drifted under Sprint 39's lnts candidate** (`../SPRINT_39/SPRINT_LOG.md` §Day 5) — its baseline solve is now measurable.
- **Evidence standard per result:** comparison verdict; **the row's own recorded `mcp_attribution` / `mcp_completed_own_solve`** showing *our* MCP produced its own `MODEL STATUS` (the `weapons` trap) — parsed by `test_solve.py` from the actual solve listing; `scripts/diagnostics/kkt_residual.py` verdict for every non-match. *(The standalone `scripts/sprint_audit/check_mcp_solve_attribution.py` re-emits and re-solves, so it is used only as Unknown 2.3's separate large-model / positive-control exercise.)*
- **Selection rule** (P10, unchanged since Sprint 38): a model is fixed only with a reproduced fingerprint **and** a named fix surface — everything else is routed or banked.
- **Research:** `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`, `docs/research/convexity_detection.md` — the classifier the NLP-gated set will go through; `docs/research/GAMSLIB_MODEL_TYPES.md` — the original catalog that recorded "License limits (11)".

### What Needs to Be Done

1. **Confirm Task 3's edition** in every `.lst` the run produces — a demo-produced result is discarded, not recorded. For convexity runs and MCP solves alike, both tools delete their listing, so the **retention patch** (`docs/planning/EPIC_4/SPRINT_40/artifacts/RETENTION_PATCH.md`) keeps each invocation's own listing.
2. **MCP-gated (11):** in the throwaway worktree, re-emit each at HEAD and diff against its golden; run the MCP solve; compare to the NLP reference; run `kkt_residual.py` on every non-match. **MCP provenance from the recorded invocation, not a different one.** Run the batch with `run_full_test.py` **inside the throwaway worktree**, so the worktree's own DB copy receives each row's `mcp_attribution` / `mcp_completed_own_solve` — `test_solve.py` parses those from the **actual solve listing** (via `parse_solve_summaries` / `Attribution`, which it imports from `scripts/sprint_audit/check_mcp_solve_attribution.py`) before `solve_mcp` deletes it. **Validate every match from those fields.** For the **edition**, use the **recorded invocation's own listing** — never a rerun. `solve_mcp` deletes `output.lst` with its `TemporaryDirectory` (also on `TimeoutExpired`, where it returns from the `except` handler), a cold row records no input path (`mcp_file_generated` is written only after an accepted presolve retry), and `solve_mcp` resolves its own executable (preferring `Versions/Current` over `PATH`) — so the invocation cannot be reconstructed afterwards. In the throwaway worktree, apply the **retention patch** (`docs/planning/EPIC_4/SPRINT_40/artifacts/RETENTION_PATCH.md`). Set **`NLP2MCP_RETAIN_PHASE`** for each tool run (`batch` for the pipeline batch, `convexity` for the verifier, `residual` for `kkt_residual.py`, `attribution` for the standalone attribution exercise); the patch covers all **four** GAMS-launching sites in the toolchain (`solve_mcp`, `verify_model`, `kkt_residual.py::run_gams`, `check_mcp_solve_attribution.py::run_one`), and **no `gams` may be invoked directly** during Task 7. It copies each invocation's own listing out on **every** return path — **including timeout, where the partial listing is kept** — and records the exact command and `cwd` **before** launch. Run the batch with `NLP2MCP_RETAIN_LST_DIR` set; each invocation is retained under a **unique invocation id** (repeated invocations of the same model never overwrite one another). **Associate each row with exactly one invocation** by the artifact's rule — candidates are invocations of the file the row's outcome came from (cold `<id>_mcp.gms`, or `<id>_mcp_presolve.gms` for a presolve outcome), and exactly one must match the row's status, objective and `mcp_attribution` when classified with `parse_solve_summaries` / `Attribution`; zero or several matches → no provenance, result not recorded. Read the edition classification from that one listing. *(Exercised 2026-10-12 — normal, simulated-timeout and verifier-CLI paths; results in the artifact.)* The task branch's `git diff main...HEAD -- scripts/ src/` must stay empty. `check_mcp_solve_attribution.py` re-emits and re-solves a fresh `--nlp-presolve` model, so it is **not** an audit of the dry run's listing — use it only as Unknown 2.3's standalone large-model and positive-control exercise. Record translate and solve wall-clock (input to Task 12's nightly-slot sizing).
3. **NLP-gated (9 in scope):** run `verify_convexity.py` licensed **output-only** (`--model <id> --output <scratch>.json`, never `--update-catalog`; it has no status-DB interface) in the throwaway worktree. `verify_convexity.py` cannot supply provenance itself: `verify_model` writes its listing to `output.lst` inside a `tempfile.TemporaryDirectory` that is deleted on return, and its `--output` JSON (`VerificationResult.to_dict()`) carries a numeric `solver_status` but **no solver name and no edition** (verified at `912d005c`). **Provenance from the verifier's OWN listing — never a rerun** (a second GAMS invocation cannot prove which edition or solver produced the JSON): in the throwaway worktree, apply the **retention patch** (`docs/planning/EPIC_4/SPRINT_40/artifacts/RETENTION_PATCH.md`), which wraps `verify_model`'s `TemporaryDirectory` so its own `output.lst` is copied out on **every** return path (normal, timeout, error) and records the exact command **before** launch. Read the **edition classification** (Task 3's regex) and the **solver actually used** (the `SOLVER … FROM LINE` line — for the QCP `emfl`, whatever QCP selects) from that retained listing; commit only those two values. A model with no licensed retained listing has no recorded result. Then, for each convex classification, attempt parse → translate → solve → compare with the same evidence.
4. **Classify each result** into an existing bucket and **route** every non-match (P4 for egypt/shale; `ISSUE_933` for tricp; a new issue stub otherwise) — no fix attempted.
5. **Record the measurement SHAs:** before removing the worktree, collect the `head_sha` of **every** retained invocation's `cmd.json` — **all four sites and every phase** (`batch`, `convexity`, `residual`, `attribution`), not only those behind a Results value — so the list is complete by construction. **Every GAMS run in Task 7 goes through one of the four patched tools; no direct `gams` calls.** Keep the patch script's output (it asserts the four wrapped sites) and write them, in full, on one `**Measured at:** <sha> …` line near the top of `COHORT_DRY_RUN.md`; a `null` `head_sha` is a failure, never omitted. The worktree must be created from a commit that **descends from Task 6's answers commit**. Task 6's *Verification* checks every recorded SHA against that commit — so the cohort **runs**, not merely the results commit, provably came after the answers.
6. **Do not persist**: no write to the **committed** `gamslib_status.json` and no golden regeneration committed — the throwaway worktree's DB copy *is* written by the run (that is where the recorded attribution comes from) and is discarded with the worktree. The sprint's batch is the measurement of record; this is the rehearsal.
7. **When any model's expected bucket moves**, grep this prep plan and every Sprint-40 prep doc for that model (§7.6).

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
DOC=docs/planning/EPIC_4/SPRINT_40/COHORT_DRY_RUN.md
test -f "$DOC" && echo "✅ doc" || { echo "COHORT_DRY_RUN.md not yet created"; exit 0; }

# Never persisted: neither the task branch's COMMITS nor the working tree touch the
# DB or goldens. `git diff HEAD` alone would pass once a change was committed, and
# misses untracked files — so check the branch against main AND the porcelain status.
P="data/gamslib/gamslib_status.json data/gamslib/mcp/"
git diff --quiet main...HEAD -- $P && [ -z "$(git status --porcelain --untracked-files=all -- $P)" ] \
  && echo "✅ DB + goldens untouched (branch vs main, and working tree)" \
  || { echo "❌ DB or goldens changed on this branch or in the working tree"; exit 1; }

# Every member of BOTH populations has a row, by identity (names from the DB, not from this plan)
.venv/bin/python - "$DOC" <<'PY'
import json, sys
doc = open(sys.argv[1]).read()
db = json.load(open("data/gamslib/gamslib_status.json"))
mcp = {m["model_id"] for m in db["models"] if (m.get("mcp_solve") or {}).get("outcome_category") == "path_solve_license"}
# same type scope as the task: andean (MIP, minlp_out_of_scope) is excluded, never measured
nlp = {m["model_id"] for m in db["models"] if (m.get("convexity") or {}).get("error") == "Model exceeds demo license limits"
       and m.get("gamslib_type") in ("LP", "NLP", "QCP")}
# One RESULT ROW per model in the "## Results" table: a row whose FIRST cell is the
# backticked model id. A name mentioned anywhere else (prose, the confirmation
# list) does not count -- otherwise a doc with no measurements would pass.
import re
sec = doc.split("## Results", 1)[1].split("\n## ", 1)[0] if "## Results" in doc else ""
rows = re.findall(r"^\|\s*`([A-Za-z0-9_]+)`\s*\|", sec, re.M)
want = mcp | nlp
missing = sorted(want - set(rows)); dup = sorted({r for r in rows if rows.count(r) > 1})
extra = sorted(set(rows) - want)
print("missing result rows:", missing or "none", "| duplicate rows:", dup or "none", "| rows outside scope:", extra or "none")
sys.exit(1 if (missing or dup or extra) else 0)
PY
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/COHORT_DRY_RUN.md` — a **`## Results` table with exactly one row per in-scope model, its first cell the backticked model id**, carrying: **stage-qualified sanitized provenance** — one `(stage, edition, solver, invocation id, head_sha)` tuple **per GAMS invocation that produced a recorded value**: `convexity` for the verifier run, `mcp` for the MCP solve, and **`residual` for the `kkt_residual.py` residual-evaluation solve behind a recorded `CASE_A/B/C` verdict**. An NLP-gated model that classifies convex and proceeds carries `convexity` and `mcp`; any row with a recorded residual verdict also carries `residual`. Each tuple is associated with **exactly one** retained invocation by the artifact's per-stage rule (site + phase + input file) This is the only form in which retained-listing evidence leaves the worktree; later tasks (e.g. Task 8's `robot` baseline) use it, never the raw listing, golden drift, MCP outcome, **the NLP reference objective, the MCP objective, and their absolute and relative difference** (blank only where no MCP objective exists) — later tasks need the numbers, not just the label: Task 8 reuses `robot`'s row as its sole baseline, and Task 10 (Unknown 4.2) judges whether hand-patched egypt/shale move **toward** the NLP objective, comparison, attribution, residual verdict, route, wall-clock
- Convexity classifications for the nine in-scope NLP-gated models
- Issue stubs (or routing notes) for every non-match; `ISSUE_933` triaged against a real compile
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4, 3.2

### Acceptance Criteria

- [ ] Every result shown to come from the licensed edition — for convexity runs, by a **retained listing** whose edition classification and solver name are recorded and whose status matches the verifier JSON
- [ ] Every in-scope member of both populations has **exactly one result row** in the `## Results` table (first cell = backticked model id), checked by identity against the DB predicate — a mention elsewhere in the doc does not count
- [ ] Every non-match has a `kkt_residual.py` verdict and a route; no fix attempted
- [ ] Every match has attribution showing our MCP solved
- [ ] DB and goldens untouched — **no change on the branch vs `main` and none in the working tree, untracked included** (checked in *Verification*)
- [ ] A `**Measured at:**` line lists the full `head_sha` of every retained invocation, and each **descends from Task 6's answers commit** (checked by Task 6's *Verification*)
- [ ] Wall-clock per model recorded for scheduling
- [ ] Unknowns 2.1, 2.2, 2.3, 2.4, 3.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: lnts — Is the Banked Diff Landable? Premise Test & Phase-0 Gate

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2, 3, 7 — Task 7 because `robot` is an MCP-gated cohort member: its licensed result may only be read after Task 6's answers are committed, and Task 7's dry run is the first cohort measurement
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/LNTS_LANDABILITY.md`: a verdict on whether P5's plan — *"author the Phase-0 gate first, with the fail-before, then re-apply the banked diff"* — can deliver **+1 Solve** at all, and if so, the gate; if not, the re-scoped P5 with its budget destination.

### Why This Matters

The carryforward and the project plan both schedule lnts as "re-apply the banked diff" for **+1 Solve → 112**. But the source log says more than that the diff lacked a fail-before (`../SPRINT_39/SPRINT_LOG.md` §Day 5):

- the candidate **failed its pre-registered PROCEED signal on substance** — the `_fx_` rows did not bind (`y2.h50` = 4.8997, `y3.h50` = 41.9700, both `INFES`);
- it **perturbed `robot` and `springchain`**;
- its exclusion is **label-enumerated** (`sameas(c,'y2') and sameas(h,'h50')`) — explicitly "not a general fix";
- and **removing the contradiction is not sufficient**: lnts then fails on its own dynamics (364 `INFES` rows — a **second defect**).

A Phase-0 gate cannot make a non-general fix general, and it cannot make the second defect go away. If prep does not test the premise, P5's 6–10 h and its +1 are planned against a REPLAN that has already happened once.

### Background

- `docs/issues/ISSUE_1694_lnts-contradictory-fx-mechanisms-blanket-zeroing.md` — the PROCEED/REPLAN signal fixed in advance.
- `../SPRINT_39/LNTS_PROBE_DESIGN.md` — the runtime bound probe.
- `../SPRINT_39/SPRINT_LOG.md` §Day 4 (layer traced to `emit_gams.py` section 1b; suppression tests `kkt.stationarity_conditions` while the blanket fires on `infer_lead_lag_condition`) and §Day 5 (the REPLAN and the open problem: express "the pruning guard covers the fixed tuple" **symbolically**, via a runtime `ord`/`card` property).
- **robot** is in the MCP-gated cohort — with the license, its drift can now be judged by a solve, not only by an emit diff. **Its baseline is Task 7's committed `## Results` row and its sanitized provenance** (edition, solver, invocation id, `head_sha`) — reused, not re-measured; Task 7's raw retained listings are deleted with its worktree and are not a cross-task artifact — so no cohort result is read before Task 6's answers are committed; this task runs only the **candidate**-emit solve, in a throwaway worktree with the retention patch.

### What Needs to Be Done

1. **Re-read Day 4–5 in full** and list every condition the banked diff failed, with its evidence.
2. **Re-run the runtime bound probe on `main`** (it must still show the contradiction — the positive control).
3. **Assess the symbolic formulation** the Day-5 open problem names: is a runtime `ord`/`card` guard expressible at section 1b without labels? Sketch it; do not land it.
4. **Assess the second defect** (dynamics `INFES` rows): is it in scope for P5, or a separate issue?
5. **Verdict:** (A) landable as banked + gate — with evidence the Day-5 failures do not apply; (B) landable only via the symbolic guard — re-estimate; (C) not landable this sprint — bank, free the budget, and remove the +1 from projections.
6. **Write the Phase-0 gate** for whichever branch survives, including the perturbation criterion for `robot`/`springchain`/`otpop`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
# The Day-5 REPLAN evidence this task must answer
grep -n "REPLAN\|INFES\|springchain\|label-enumerated\|not sufficient" docs/planning/EPIC_4/SPRINT_39/SPRINT_LOG.md | sed -n '1,15p' | cut -c1-140
# The fix site still exists where Day 4 traced it
grep -n "fix_rhs" src/emit/emit_gams.py | head -5

DOC=docs/planning/EPIC_4/SPRINT_40/LNTS_LANDABILITY.md
test -f "$DOC" && echo "✅ doc" || echo "LNTS_LANDABILITY.md not yet created"
grep -c "Verdict" "$DOC" 2>/dev/null
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/LNTS_LANDABILITY.md` — the Day-5 failure list, the re-run probe, the symbolic-guard sketch, the second-defect scoping, a verdict A/B/C, the Phase-0 gate
- If verdict C: a recommended edit to P5's projection for Task 12
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [ ] Every Day-5 REPLAN condition listed with its evidence and an answer
- [ ] The runtime probe re-run on `main` and shown to reproduce (positive control)
- [ ] A verdict A, B or C with its budget consequence
- [ ] The gate's perturbation criterion names `robot`, `springchain` and `otpop`
- [ ] The +1 Solve is either justified against Day 5 or removed from the projection
- [ ] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: sarf Jacobian O(active) Re-Architecture Design

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4-6 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 6.1, 6.2, 6.3

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/SARF_JACOBIAN_DESIGN.md`: a re-measured profile of sarf at HEAD, the specific entry points in `compute_constraint_jacobian` an O(active) re-architecture must change, an atomicity plan (what must land together), and the gate — so P6's 20–28 h start on code, not on profiling.

### Why This Matters

Sprint 39 Day 0 re-pointed this work twice: Task 6 refuted the "four call sites" premise (0.5 % of wall-clock), and the attribution placed **70.9 %** in `compute_constraint_jacobian`. That figure is from Sprint 39; the re-architecture's design depends on *where inside* the Jacobian the time goes, which has not been broken down. And three of the four Day-7 defects produced a **wrong answer rather than a crash** — a partial landing is an inconsistent MCP, so the atomicity boundary must be known before any code changes.

### Background

- `../SPRINT_39/SARF_CALLSITE_PLAN.md` — the Sprint-39 attribution and its three branches (B taken).
- `../SPRINT_38/SARF_REARCH_DESIGN.md` · `../SPRINT_38/DAY7_SARF_GATE_P6C.md` — the O(active) design and the Day-7 lessons (narrowing that is itself O(removed work) does not help; a precomputed position map did).
- `docs/issues/ISSUE_1385_sarf-symbolic-emit-o-active.md` — the issue and its gate.
- Gate peculiarities: `make leak-check MODEL=sarf` reports `NO-OP` (no golden); the real gate is the full leak gate plus sarf producing a golden (186 → 187); sarf cannot be its own fail-before fixture (369,024 declared columns).

### What Needs to Be Done

1. **Re-profile sarf at HEAD** with a bounded run (time-boxed; it does not terminate) — confirm or update the 70.9 % and break it down by callee.
2. **Confirm `gradient.py:453` is still dead** and `_diff_sum`'s self/inclusive shares.
3. **Name the entry points** inside `compute_constraint_jacobian` that iterate the full rather than the active set, with `file:line` anchors resolved by the shared resolver (§7.3).
4. **Define the atomicity boundary**: which changes must land in one commit for the MCP to remain consistent.
5. **Choose a fail-before fixture** that is not sarf (a smaller model sharing the shape) and show it fails before: **hold the active (referenced) set fixed and scale only the declared cardinality** across at least three sizes, recording translate time **and a work count** (e.g. `differentiate_expr` calls); the positive control is that work grows with **declared** size while the active set does not change — **linear growth is the expected signature**, not super-linear, since the documented bottleneck is O(declared) per row (`../SPRINT_38/SARF_REARCH_DESIGN.md`: differentiation volume "directly proportional to declared columns"; `../SPRINT_38/DAY7_SARF_GATE_P6C.md`: "O(declared) per row"). After the O(active) change the same sweep should be ~flat in declared size.
6. **Re-estimate** P6 against the breakdown and state its REPLAN exit (timeout re-trigger; atomicity violation).

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
grep -n "def compute_constraint_jacobian" src/ad/*.py
sed -n '445,460p' src/ad/gradient.py
DOC=docs/planning/EPIC_4/SPRINT_40/SARF_JACOBIAN_DESIGN.md
test -f "$DOC" && echo "✅ doc" || echo "SARF_JACOBIAN_DESIGN.md not yet created"
grep -c "measured at" "$DOC" 2>/dev/null   # every profile figure carries its commit
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/SARF_JACOBIAN_DESIGN.md` — profile at HEAD with commit, entry points, atomicity boundary, fail-before fixture, re-estimate and REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3

### Acceptance Criteria

- [ ] Profile re-measured at a stated commit, with the per-callee breakdown inside the Jacobian
- [ ] Entry points anchored by code, not by line number alone
- [ ] Atomicity boundary stated
- [ ] A non-sarf fail-before fixture shown to fail before — work growing with **declared** cardinality while the active set is held fixed (linear growth suffices)
- [ ] P6 re-estimated with an explicit REPLAN exit
- [ ] Unknowns 6.1, 6.2, 6.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Correctness-Track Pre-Traces — turkpow Class A, the Diagonal Defect, the Structural Sites

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 5-7 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2, 7, 9
**Unknowns Verified:** 4.1, 4.2, 4.3, 7.1, 7.2, 8.1, 8.2

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/CORRECTNESS_PRETRACES.md` giving each of P4, P7 and P8 a **traced layer**, a minimal reproducer and a Phase-0 gate outline before Day 1 — and file the diagonal-reference defect's issue.

### Why This Matters

Three of Sprint 38's four Phase-0 gates named the wrong layer; Sprint 39 added the layer field to the template for that reason. All three tracks here have a *named* surface that is still a hypothesis: turkpow's minting site (`t__kkt1` into both coordinates of `vs(t,v)`), the diagonal defect's "probably `_diff_sum`", and the two structural-only sites' guards. Tracing in prep is cheap; discovering the wrong layer on Day 6 costs the day.

### Background

- **P4:** `../SPRINT_39/P2_VIOLATION_TRIAGE.md` — the two-class work list (Class A: dinam, egypt, turkpow ×3, nonsharp ×1; Class B: gussrisk, nonsharp ×1, shale). Task 7 gives egypt and shale their first solve. The P2 ratchet (`scripts/sprint_audit/check_index_repeat_properties.py`) stands at 9 = baseline 9.
- **P7:** `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md` §5 — `diagsum(j).. sum(i, tsam(i,i))` emits `stat_tsam(i,j).. 1 =E= 0;`; B-3 is called 0× for it.
- **P8:** `../SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` · `tests/unit/kkt/test_positional_domain_sites.py` — 16 pinned sites, 11 structural-only; `_match_subset_domain` and `_compute_index_offset_key` (both in `src/kkt/stationarity.py`) indistinguishable across a nine-shape probe with guards disabled. #1737 (`docs/issues/ISSUE_1737_repeated-equation-domain-index-collapse.md`) is load-bearing for the AD layer — **do not narrow it**.
- **Research:** `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`.

### What Needs to Be Done

1. **turkpow:** trace the alias-minting site from the emitted `vs(t__kkt1,t__kkt1)`-shaped reference back to the code that substitutes it; record the layer with a one-line justification; write the fail-before property test outline.
2. **egypt / shale:** fold in Task 7's solve results — does the Class-A fingerprint explain the mismatch, or is there a second defect?
3. **Diagonal defect:** build the minimal reproducer, confirm it on `main`, trace the layer (do not assume `_diff_sum`), and **file the issue** with the reproducer.
4. **Structural sites:** extend the nine-shape probe to ≥ 3-D and subset-of-subset shapes; either find a discriminating input (shown to fail with the guard disabled — positive control) or record the dead-code finding with its proof scope.
5. **Write a Phase-0 outline per track** with layer and positive control (the P10b field).

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
make check-index-repeats 2>&1 | tail -2
grep -n "def _match_subset_domain\|def _compute_index_offset_key" src/kkt/stationarity.py
grep -n "test_the_AD_collapse_is_reachable_but_EMIT_refuses_it" tests/unit/kkt/test_positional_domain_sites.py
DOC=docs/planning/EPIC_4/SPRINT_40/CORRECTNESS_PRETRACES.md
test -f "$DOC" && echo "✅ doc" || echo "CORRECTNESS_PRETRACES.md not yet created"
grep -c -i "layer:" "$DOC" 2>/dev/null          # one per track (expect >= 3)
ls docs/issues/ | grep -i "diagonal\|tsam" || echo "diagonal-defect issue not yet filed"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/CORRECTNESS_PRETRACES.md` — per track: traced layer + justification, reproducer, Phase-0 outline with positive control
- A new issue file for the diagonal-reference defect with its minimal reproducer
- The structural-site verdict: discriminating input, or dead-code finding with proof scope
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 7.1, 7.2, 8.1, 8.2

### Acceptance Criteria

- [ ] Each of P4, P7, P8 has a **traced** layer, not a named-by-assumption one
- [ ] The diagonal-defect issue is filed with a reproducer confirmed on `main`
- [ ] egypt/shale mismatch explained by the Class-A fingerprint or a second defect named
- [ ] Every probe records its positive control
- [ ] #1737 left untouched
- [ ] Unknowns 4.1, 4.2, 4.3, 7.1, 7.2, 8.1, 8.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Process-Mechanism Spec & Smaller-Items Catalog

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 40 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 9.1, 9.2, 10.1, 10.2

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/PROCESS_AND_SMALL_ITEMS.md`: (a) a spec for each P10 mechanism (10a–10e) with its fail-before test, and (b) the P9 smaller-items catalog with each item's next step re-verified on `main` — the sprint's slack absorber.

### Why This Matters

Sprint 39's retrospective recorded seven process changes because each had failed at least once *after* it was written down — the node count rotted once more after the rule existed. A rule that is only written down is the state that already failed; P10 converts the mechanizable ones into checks. P9 is deliberately the schedule filler, which only works if each item is small, known and verified to still exist.

### Background

- `../SPRINT_39/SPRINT_RETROSPECTIVE.md` §7 (seven changes) and `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md` §8 (plus "the leak gate runs ALONE").
- `../SPRINT_39/PROCESS_INFRA_SPEC.md` — Sprint 39's P8 spec (the layer field) — the precedent for 10b.
- `scripts/sprint_audit/check_phase0_doc.py` · `Makefile` target `check-goldens` (no `--min-scope` locally; CI derives it from `git ls-files`) · `../SPRINT_39/prompts/PLAN_PROMPTS.md`.
- **P9 items:** `scripts/integration_health_check.py` bootstrap; the 7 `model_infeasible` models' `skipped` vs `mismatch` (KPI-visible — needs its own Phase-0 doc); `kpi_block.py`'s `all_219_match` key; filing the ganges embedded-NLP-diverges issue (#1378/#1424 class; #1667, #929/#930 open).

### What Needs to Be Done

1. **For each of 10a–10e**, write: the mechanism, where it lives, the fail-before test, and its estimate.
2. **10a:** confirm the resolver in `test_positional_domain_sites.py` is extractable without behaviour change — list its call sites.
3. **10b:** draft the positive-control field for the Phase-0 template and the `check_phase0_doc.py` assertion.
4. **10c:** confirm `make check-goldens` lacks `--min-scope` locally and specify the `git ls-files`-derived value.
5. **P9:** re-verify each item on `main` (does it still reproduce?), record its next step and estimate; mark the `model_infeasible` comparison change as KPI-visible with its own gate.
6. **Draft the ganges issue text** (to be filed in-sprint or in prep).

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
grep -n "^check-goldens" -A2 Makefile
grep -n "min-scope\|MIN_SCOPE" .github/workflows/golden-staleness.yml | head -3
.venv/bin/python -S scripts/integration_health_check.py --help >/dev/null 2>&1 && echo "bootstrap OK" || echo "uninstalled-checkout failure reproduces"
grep -n "all_219_match" scripts/sprint_audit/kpi_block.py | head -2
DOC=docs/planning/EPIC_4/SPRINT_40/PROCESS_AND_SMALL_ITEMS.md
test -f "$DOC" && echo "✅ doc" || echo "PROCESS_AND_SMALL_ITEMS.md not yet created"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/PROCESS_AND_SMALL_ITEMS.md` — 10a–10e specs with fail-before tests; the P9 catalog with re-verified next steps
- The ganges embedded-NLP-diverges issue text
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 9.1, 9.2, 10.1, 10.2

### Acceptance Criteria

- [ ] Each mechanism has a location, a fail-before test and an estimate
- [ ] Each P9 item re-verified on `main` (still reproduces, or closed)
- [ ] The `model_infeasible` comparison change marked KPI-visible with its own Phase-0 requirement
- [ ] The ganges issue drafted
- [ ] Unknowns 9.1, 9.2, 10.1, 10.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 12: Plan Sprint 40 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 40 Day 0
**Owner:** Development team
**Dependencies:** All tasks (1–11)

### Objective

Produce `docs/planning/EPIC_4/SPRINT_40/PLAN.md` and `docs/planning/EPIC_4/SPRINT_40/prompts/PLAN_PROMPTS.md`: the 14-day schedule with per-day budgets, REPLAN exits, checkpoints, pre-registered close rules with preconditions, the risk register, acceptance criteria with each figure's source, and one prompt per day.

### Why This Matters

Sprint 40 has three fixed points the schedule must honour rather than discover: **P1 before any license-dependent measurement**, **the three owner decisions — already answered and committed in prep (Task 6) — before any cohort measurement**, and **P4 after P2** (egypt/shale need their solves). It also inherits a lesson about close rules: Sprint 38 pre-registered a rule against an unstarted track and it went unmet for unrelated reasons; Sprint 39 required every rule to state its precondition, so an unmet rule can be told apart from a missed target.

### Background

- `../SPRINT_39/PLAN.md` + `../SPRINT_39/artifacts/validate_plan.py` — the format and the committed validator (a schedule that validates rather than asserts).
- `../SPRINT_39/prompts/PLAN_PROMPTS.md` — the day-prompt format, including the "re-derive the PR's file list after committing" and attribution checks.
- `../PROJECT_PLAN.md` Sprint 40 — per-priority budgets (114–162 h), acceptance criteria, REPLAN exits.

### What Needs to Be Done

1. **Assign priorities to days** with per-day budgets summing ≤ 168 h, no day over 12 h; P1 on Days 0–1; the P2 batch on a nightly slot sized from Task 7's wall-clock.
2. **Fold in prep verdicts**: Task 8's lnts verdict (keep/re-scope/remove the +1), Task 9's sarf re-estimate, Task 7's routing list, and **Task 6's recorded answers** — consumed as fixed inputs. There is **no Day-0 fallback**: Task 6 is complete only once all three answers are committed, Task 7 must descend from that commit, and this task depends on both. *(This supersedes `PROJECT_PLAN.md`'s "Day-0 owner decision" timing — the decisions move earlier, into prep, which is what the blind-decision gate requires.)*
3. **Write the REPLAN exit per track** — the evidence that triggers it and where the budget goes.
4. **Schedule checkpoints** (Day 5, Day 10) and the final retest, with `--resolve-changed --since-commit bd2af6e9` and the **license-neutrality** check (every row outside the two cohorts keeps its outcome).
5. **Pre-register the close rules**, each with its precondition; state which take none.
6. **Write the day prompts** (`prompts/PLAN_PROMPTS.md`), each naming its branch, deliverable and gate, and embedding the §7 rules (PR body as a pointer; figures stated once with commit; leak gate alone; no `git stash`).
7. **Route every unresolved Known Unknown** to the day that closes it — including **1.5's universal neutrality claim** (at most `🔍 INCOMPLETE — sample-neutral, routed` from Task 3's sample) to the day of the first licensed full run.
8. **Commit a validator** beside the plan, as Sprint 39 did, and run it.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
PLAN=docs/planning/EPIC_4/SPRINT_40/PLAN.md
if [ ! -f "$PLAN" ]; then
  echo "PLAN.md does not exist yet — expected until Task 12 produces it; skipping its checks"
  exit 0
fi
echo "✅ PLAN.md"
test -f docs/planning/EPIC_4/SPRINT_40/prompts/PLAN_PROMPTS.md && echo "✅ prompts"
test -f docs/planning/EPIC_4/SPRINT_40/artifacts/validate_plan.py && .venv/bin/python docs/planning/EPIC_4/SPRINT_40/artifacts/validate_plan.py
grep -c "REPLAN" "$PLAN"
grep -c -i "precondition" "$PLAN"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_40/PLAN.md` — schedule, budgets, REPLAN exits, checkpoints, close rules with preconditions, risk register, acceptance criteria with sources, unknown routing, prep refutation summary
- `docs/planning/EPIC_4/SPRINT_40/prompts/PLAN_PROMPTS.md` — one prompt per day
- `docs/planning/EPIC_4/SPRINT_40/artifacts/validate_plan.py` — the committed schedule validator
- `CHANGELOG.md` — Sprint 40 Prep entry

### Acceptance Criteria

- [ ] ≤ 12 h/day and ≤ 168 h total, **validated by the committed script**
- [ ] P1 precedes every license-dependent measurement; Task 6's prep-recorded answers are consumed as fixed inputs (no Day-0 slot); P4 follows P2
- [ ] Every track has a REPLAN exit with its budget destination
- [ ] Every close rule states its precondition (or explicitly takes none)
- [ ] Every unresolved Known Unknown routed to a day
- [ ] Day prompts embed the §7 rules and the no-attribution check

---

## Summary and Critical Path

### Critical Path

```
Task 1 (Known Unknowns)
   └─> Task 2 (Baseline + Both Populations by Identity)
          ├─> Task 3 (Effective License + Per-Solver Probes)
          │      ├─> Task 4 (CI Isolation Design) ──┐
          │      │                                  ├─> Task 6 (Owner Decision Brief — written blind)
          │      │      (Task 2 also feeds Task 6) ─┘        └─> Task 7 (Cohort Dry Run) ─┐
          │      └─> Task 5 (Schema 3.1.0 Design) ───────────────────────────────────────┤
          │                         Task 7 ──> Task 8 (lnts Landability; reuses Task 7's robot baseline) ──┤
          ├─> Task 9 (sarf Jacobian Design) ──> (touch set) ──┐                          │
          │                                                   └─> Task 10 (Pre-Traces) <─┘
          │                                                          └─> Task 12 (Schedule)
          └─> Task 11 (Process + Small Items) ───────────────────────────> Task 12
```

**Task 7 depends on Task 3 as well as Task 6** (results must come from the licensed edition); **Task 6 depends on Tasks 3 and 4** (its CI decision needs their evidence); **Task 10 depends on Tasks 7 and 9**; **Task 8 depends on Task 7** (it reads `robot`, a cohort member, so it must follow the first cohort measurement and reuse its baseline). **Tasks 5, 9 and 11 are parallelisable** once their inputs land; Task 4 is now on the critical path. Task 6 is short but on the critical path because its whole value is being committed before Task 7 runs.

### Time Budget

| Phase | Tasks | Hours |
|---|---|---|
| Foundation | 1, 2 | 5–7 |
| License infrastructure | 3, 4, 5 | 8–11 |
| Decision | 6 | 2–3 |
| Measurement | 7 | 5–7 |
| Carryforward designs & traces | 8, 9, 10 | 12–17 |
| Process & slack | 11 | 3–4 |
| Scheduling | 12 | 3–4 |
| **Total** | **1–12** | **38–53** |

### Success Criteria for the Prep Phase

- [ ] **The license is shown, not asserted** — a probe that fails on the demo and solves licensed, with the edition string identified
- [ ] **No CI design gives the license to a job that runs PR code**, and the `main`-only branch policy is verified
- [ ] **The schema change has a closed, grep-derived writer list** including `db_manager.py`
- [ ] **The three owner decisions are answered before any cohort result exists** (before Task 7's first commit), provably from history
- [ ] **Both populations are measured by identity**, every non-match carrying a residual verdict and a route
- [ ] **Every Critical/High Known Unknown is resolved or explicitly deferred with a reason**
- [ ] **lnts's +1 Solve is either justified against Sprint 39 Day 5 or removed from the projection**
- [ ] **Every carryforward track has a traced layer** before Day 1
- [ ] **The schedule fits** (≤ 12 h/day, ≤ 168 h), validated by a committed script
- [ ] **Prep found at least one wrong premise** — and recorded what it changed

### What Would Make This Prep a Failure

Recorded in advance, so it can be recognised:

- A cohort result is reported without evidence of the edition that produced it
- The floor-provenance or corpus-entry rule is written after Task 7's results are known
- Any part of the license text appears in a commit, log excerpt or PR
- lnts is scheduled as "re-apply the banked diff" without answering Day 5
- A Sprint-40 day spends its budget diagnosing a cohort fingerprint that Task 7 could have produced
- A figure in a prep doc is restated in a later doc instead of re-measured or cited by commit

---

## Appendix: Document Cross-References

### Sprint 40 definition
- `../PROJECT_PLAN.md` → *Sprint 40 (Weeks 45–46)* — goal, ten priorities, deliverables, acceptance criteria, effort (114–162 h), risk; and the 2026-10-12 changelog entry recording the insertion and the PR #1745 review changes
- `../GOALS.md` — Epic 4 goals: §7 *Solve Stage: PATH Convergence and Solution Matching* (the NLP-vs-MCP comparison P2/P3 extend to the large models), §8 *Performance, Quality & Release* (P6, P10), §*Success Metrics*, §*Risks & Mitigation* (Risk 2 MCP-NLP divergence, Risk 6 infeasible MCP formulations), §*Dependencies* (External: *"GAMS software installed locally (with valid license)"* — now a user-level evaluation license obtained as size-unlimited; its effectiveness and per-solver coverage are Task 3's to prove)

### Sprint 39 hand-off (the primary source for every carryforward)
- `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md` — §1 P10 two-class · §2 lnts · §3 sarf · §4 #1737 · §5 diagonal defect · §6 structural sites · §7 smaller items + the license cohort · §8 process findings · §9 banked
- `../SPRINT_39/SPRINT_RETROSPECTIVE.md` — §7 the seven process changes
- `../SPRINT_39/SPRINT_LOG.md` — §Day 4–5 (lnts trace and REPLAN), §Day 9 (license cohort 10 → 11 derived), §Day 13 (close figures)
- `../SPRINT_39/PLAN.md` · `../SPRINT_39/artifacts/validate_plan.py` · `../SPRINT_39/prompts/PLAN_PROMPTS.md` — schedule, validator and prompt formats
- *Follow-on items:* Epic 4 records follow-ons as the per-sprint carryforwards file above (the convention since Sprint 33); the only `follow-ons/` directory in the repo is `../../EPIC_1/SPRINT_5/follow-ons/`, which has no bearing on this sprint

### Per-priority background
- **P1 license + CI + schema:** `.github/workflows/pr19-emit-solve-validation.yml` · `.github/workflows/presolve-divergence.yml` · `data/gamslib/schema.json` · `scripts/gamslib/migrate_schema_v3.0.0.py` · `scripts/gamslib/db_manager.py` · `tests/gamslib/test_migrate_schema_v3.py` · `tests/gamslib/test_db_manager.py` · `../SPRINT_39/PRESOLVE_RECORD_REMEDY.md` §9
- **P2 MCP-gated cohort:** `scripts/gamslib/run_full_test.py` · `scripts/gamslib/test_solve.py` (`compare_solutions`, `extract_gams_version`) · `scripts/sprint_audit/check_mcp_solve_attribution.py` · `docs/issues/ISSUE_933_tricp-mcp-compilation-errors.md`
- **P3 NLP-gated set:** `scripts/gamslib/verify_convexity.py` · `data/floor_provenance.json` · `scripts/sprint_audit/floor_tracker.py` · `../SPRINT_39/FLOOR_DECISION_BRIEF.md`
- **P4 two-class:** `../SPRINT_39/P2_VIOLATION_TRIAGE.md` · `scripts/sprint_audit/check_index_repeat_properties.py` · `scripts/sprint_audit/index_repeat_p2_baseline.json`
- **P5 lnts:** `docs/issues/ISSUE_1694_lnts-contradictory-fx-mechanisms-blanket-zeroing.md` · `../SPRINT_39/LNTS_PROBE_DESIGN.md`
- **P6 sarf:** `docs/issues/ISSUE_1385_sarf-symbolic-emit-o-active.md` · `../SPRINT_39/SARF_CALLSITE_PLAN.md` · `../SPRINT_38/SARF_REARCH_DESIGN.md`
- **P7 / P8 positional domain:** `../SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` · `tests/unit/kkt/test_positional_domain_sites.py` · `docs/issues/ISSUE_1737_repeated-equation-domain-index-collapse.md` · `docs/issues/ISSUE_1741_pattern-c-b3-repeated-index-collapse.md`
- **P9 smaller items:** `scripts/integration_health_check.py` · `scripts/sprint_audit/kpi_block.py` · `docs/issues/ISSUE_1667_ganges-deferred-bounds-before-include.md` · `docs/issues/ISSUE_929_ganges-translation-timeout.md`
- **P10 process:** `../SPRINT_39/PROCESS_INFRA_SPEC.md` · `scripts/sprint_audit/check_phase0_doc.py` · `Makefile` (`check-goldens`)

### Research documents
- `docs/research/gamslib_kpi_definitions.md` — KPI and corpus definitions (P3's denominator question)
- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` · `docs/research/convexity_detection.md` — the convexity classifier the NLP-gated set goes through; the design's solver table records which solvers run under the demo
- `docs/research/GAMSLIB_MODEL_TYPES.md` — the original catalog, which already recorded "License limits (11)" at Epic 3
- `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` · `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md` — schema versioning and validation (Task 5)
- `docs/research/multidimensional_indexing.md` · `docs/research/nested_subset_indexing_research.md` — background for the positional-domain tracks (Task 10)

### Tooling the prep tasks use
- `scripts/sprint_audit/kpi_block.py` — derived KPI block, carries its commit, warns on a dirty DB
- `scripts/sprint_audit/floor_tracker.py` — the floor, from provenance, never from the DB
- `scripts/sprint_audit/check_golden_staleness.py` (`make check-goldens`) — the full-corpus leak gate (186 in-scope); **run alone**
- `scripts/sprint_audit/check_index_repeat_properties.py` (`make check-index-repeats`) — P1 hard gate + P2 ratchet
- `scripts/sprint_audit/check_mcp_solve_attribution.py` — spurious-match discriminator
- `scripts/sprint_audit/check_phase0_doc.py` — Phase-0 compliance
- `scripts/sprint_audit/check_doc_figures.py` (`make check-doc-figures`) — figures in changed doc lines vs. their sources
- `scripts/diagnostics/kkt_residual.py` — `CASE_A` / `CASE_B` / `CASE_C` verdicts
- `scripts/gamslib/run_full_test.py` — pipeline runner, `--resolve-changed --since-commit <SHA>` checkpoint
