# Sprint 40 Known Unknowns

**Created:** 2026-10-12
**Status:** Active — Pre-Sprint 40
**Purpose:** Proactive documentation of the assumptions and unknowns for Sprint 40 (the Sprint-39 carryforward sprint **and** the licensed-GAMS unlock) **before** implementation begins — so each assumption is verified in the prep phase rather than discovered on a sprint day.

---

## Executive Summary

This document identifies every open question, assumption and risk across the ten Sprint-40 priorities defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 40, Weeks 45–46).

Sprint 39 closed at **Solve 111 · Match 95 · Translate 135 · floor 75 · `path_solve_terminated` 0** (measured at `bd2af6e9`; Match 96 → 95 was P7's `weapons` **correction**, not a regression). Its carryforwards are each bounded (`../SPRINT_39/SPRINT_40_CARRYFORWARDS.md`). What is new is a GAMS license obtained as **size-unlimited** — observed so far as a **user-level evaluation license** (valid to 2027-09-21); whether it is the *effective* license for every pipeline invocation and lifts the limit on every solver path is **Unknown 1.1, Task 3's to prove**, and with it a kind of unknown no earlier sprint carried: **assumptions about results that have never existed.** Eleven MCP-gated emits have never been solved; nine NLP-gated models have never been classified, parsed or translated — their DB rows have **no `nlp2mcp_parse` key at all**.

That is the principal risk this document is organised around. Sprint 39's retrospective did not record a wrong fix; it recorded **wrong claims about evidence** — a figure restated per round until it rotted, a count where an identity was needed, two probes reported as passing that could not have failed, a classification moved without sweeping the sentences that quoted it. The license multiplies the opportunities for exactly that failure: twenty first-time results, each of which will be *read* by someone who would prefer it to be a match.

Three findings made while writing this list already change the plan's premises — each is an unknown below, not a conclusion:

- **The license IS installed — at the USER level** (`~/Library/Application Support/GAMS/gamslice.txt`, an evaluation license valid to 2027-09-21), **while the system-directory copy is still the 2026-07-13 demo file.** Which file GAMS reads, and whether the license lifts the size limit for **every** solver the pipeline uses, are the open questions (**1.1**). *(Corrected in PR #1746 review: the first version, reading only the system-directory file, said the license appeared not to be installed.)*
- **The 142 denominator is derived, not fixed:** `scripts/sprint_audit/kpi_block.py` selects candidates by `convexity.status ∈ {verified_convex, likely_convex}` (line 112), as does `batch_parse.get_candidate_models`. **A licensed convexity run that writes a convex status for any NLP-gated model grows the corpus silently — before the owner's corpus-entry decision exists** (**3.3**).
- **Sprint 39 Day 5 contradicts the lnts plan:** the banked diff failed its pre-registered PROCEED signal on substance, perturbed `robot` and `springchain`, and was label-enumerated; and removing the contradiction exposed a second (dynamics) defect (**5.1–5.3**).

**Sprint 40 Scope (per `PROJECT_PLAN.md`):**
1. **P1 (Infrastructure, Day 0–1)** — the licensed toolchain locally and in CI; PR workflows stay demo-only; a trusted `main`-only licensed workflow; schema **3.1.0** `license_edition`
2. **P2 (Measurement)** — the 11-model MCP-gated cohort's first NLP-vs-MCP comparison; ceiling +11 Solve, **measured, not projected**
3. **P3 (Measurement + decision)** — the 10-model NLP-gated set's convexity evaluation and the corpus-entry decision (`andean` MIP-excluded)
4. **P4 (Correctness)** — the P10 two-class triage, turkpow first
5. **P5 (KPI)** — lnts, behind a Phase-0 gate (+1 Solve, **premise under test**)
6. **P6 (KPI)** — sarf's O(active) Jacobian re-architecture (+1 Translate)
7. **P7 (Correctness)** — the pre-existing diagonal-reference defect
8. **P8 (Prevention)** — positional-domain follow-ons
9. **P9 (Slack)** — the smaller items
10. **P10 (Infrastructure)** — the Sprint-39 process changes as mechanisms

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 40 section — goal, ten priorities, deliverables, acceptance criteria, effort 114–162 h, risk) · `docs/planning/EPIC_4/SPRINT_40/PREP_PLAN.md` (the 12 prep tasks that verify these unknowns) · `docs/planning/EPIC_4/SPRINT_39/SPRINT_40_CARRYFORWARDS.md` (§1–§9 with bounded next steps) · `docs/planning/EPIC_4/SPRINT_39/SPRINT_RETROSPECTIVE.md` §7 · `docs/planning/EPIC_4/SPRINT_39/SPRINT_LOG.md` (§Day 4–5 lnts, §Day 9 the license cohort derived as 11, §Day 13 close) · `docs/planning/EPIC_4/GOALS.md` (Epic-4 goals 7 and 8; External Dependencies). *(No `PRELIMINARY_PLAN.md` exists for Sprint 40 — the only one in the repository is `../../EPIC_2/SPRINT_7/PRELIMINARY_PLAN.md`. The `PROJECT_PLAN.md` section, `PREP_PLAN.md` and the carryforwards file are the planning sources.)*

**Lessons from Previous Sprints:**
- **⚠ A figure that changes with what it describes rots when restated** (S39 retro §7.1): the node count rotted **four** times, once *after* the rule was written. State it once, with its commit; re-measure, never re-quote.
- **Pin by identity, not by count** (S39 §7.2): the S39 handoff recorded the license cohort as **10 / +10**; the DB said **11** (`../SPRINT_39/SPRINT_LOG.md` §Day 9). Only derivation caught it.
- **A probe must be shown able to fail** (S39 §7.5): two vacuous passes were reported as real. Every "How to Verify" below names its positive control where one applies.
- **A favourable classification found by the person reporting it must not be self-approved** (S38 close → S39 P1): the floor +2 was refused at close and decided by the owner on Day 0. Sprint 40 will produce up to twenty such classifications at once.
- **A golden can pass every static review and still not RUN** (S38 D9, `weapons`): a presolve "match" can read back the embedded NLP's own answer. A first-ever match is exactly where a spurious one is most plausible (S39 Unknown 6.2).
- **"A golden exists" has never meant "the golden is correct" for the license cohort** — `ferts`'s emit was silently wrong until S38 Day 11, and S39 prep found **7 of 11** members carry a repeated-symbol declared domain, **2** (egypt, shale) with a live P2 violation (S39 Unknown 6.2).
- **Fix surfaces are hypotheses, and so are their LAYERS** (S38: three of four Phase-0 gates named the wrong layer). S39 added the layer field to the Phase-0 template for that reason.
- **The genuine floor cannot be derived from the DB** — a mechanical `Match − (presolve ∧ match)` count yields **65**; `data/floor_provenance.json` is the source.
- **Prep should refute something:** S38 refuted 32 %, S39 **63 %** (19 of 30).

**Deferred-unknown lineage:** Sprint 39's 30 unknowns all resolved in prep (11 ✅ / 11 ❌ / 8 🔶), so **none carries open**. These descend from Sprint-39 *dispositions* instead:
- **Category 2** continues **S39 Unknown 6.2** (*"If a license arrives, does the 11-model batch actually solve?"* — ❌ WRONG: the goldens are not safe to assume; the procedure became three stages: P2-property pre-flight → `--only-solve` → attribution). The license has now arrived.
- **Category 5** continues **S39 Unknowns 3.1–3.3** (lnts — ✅ the collision is real) and the **S39 Day-5 REPLAN** that followed them.
- **Category 6** continues **S39 Unknowns 4.1–4.4** (sarf — 4.2 ❌: the four call sites were 0.5 % of wall-clock; branch B taken).
- **Categories 7 and 8** continue **S39 Unknowns 5.1–5.3** (the positional-domain survey) and the two post-survey findings in carryforward §4–§6.
- **Category 10** continues **S39 Unknowns 8.1–8.3** (the layer field — the precedent for the positive-control field).
- **S39 Unknown 10.2** (S38's Unknown 1.5, the `$149` measurement) was **closed as unreachable** and is **deliberately not re-asked**; its recommended follow-up — closing GitHub #1668 with its two directions' measurements — is recorded under **9.2**.

---

## How to Use This Document

### Before Sprint 40 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (18 total)
2. Create minimal controls in a scratch directory — **never the repo root** (GAMS writes `.lst`/`.log` next to its cwd). The license probe and the lnts bound probe are minutes-scale; the cohort dry run is hours (turkey, egypt); **the sarf profile does not terminate and must be time-boxed**
3. Document findings in the "Verification Results" sections, **each with the commit it was measured at**
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED / ❌ WRONG / 🔶 PARTIALLY WRONG (with correction)
5. **Never paste any part of the license text** into this document, a log excerpt or a PR

### During Sprint 40
1. Review daily during standup
2. Add newly discovered unknowns (use the Template below) **the day they are found**
3. Update with implementation findings, including anything that *contradicts* a prep verdict
4. When a cohort model's classification moves, **sweep this document for that model's name** (S39 §7.6)

### Priority Definitions
- **Critical:** Wrong assumption breaks the track, invalidates reported figures, or forces a mid-sprint REPLAN (>8 hours rework)
- **High:** Wrong assumption causes significant rework (4–8 hours)
- **Medium:** Wrong assumption causes minor issues (2–4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 29

**By Priority:**
- Critical: 7 (24% — could invalidate a reported figure or force a mid-sprint REPLAN: which license file GAMS actually reads and whether it covers every solver; whether the license changes any non-cohort outcome; whether the MCP-gated cohort translates and yields a bounded work list; whether the corpus can grow before the owner decides; whether lnts is landable; where sarf's time actually goes)
- High: 11 (38% — require upfront research or design before Day 1)
- Medium: 8 (28% — resolvable during implementation)
- Low: 3 (10% — nice-to-know, low impact)

**By Category:**
- Category 1 (The Licensed Toolchain — Local and CI): 5 unknowns
- Category 2 (The 11-Model MCP-Gated Cohort): 4 unknowns
- Category 3 (The 10-Model NLP-Gated Set): 3 unknowns
- Category 4 (P10 — the Six P2-Flagged Models, Class A First): 3 unknowns
- Category 5 (lnts — Re-Apply the BANKED Diff Behind a Phase-0 Gate): 3 unknowns
- Category 6 (sarf #1385 — the O(active) Re-Architecture at the Jacobian): 3 unknowns
- Category 7 (The Pre-Existing Diagonal-Reference Defect): 2 unknowns
- Category 8 (Positional-Domain Follow-Ons): 2 unknowns
- Category 9 (The Smaller Items): 2 unknowns
- Category 10 (Infrastructure — the Sprint-39 Retrospective's Process Changes as Mechanisms): 2 unknowns

*(The prompt for this task asked for "5 main categories" while listing ten; ten are used, one per sprint priority, so every priority has an owner — the same resolution Sprint 39 reached for the same inconsistency.)*

**Estimated Research Time:** **33.0 hours** — derived by the summing snippet in `PREP_PLAN.md` Task 1 *Verification*, at the commit that adds this file. Within the 28–36 h target. Spread across prep Tasks 2–11 (budgeted 32–45 h, derived from `PREP_PLAN.md`'s overview table) — the research fits at the lower bound, unlike Sprint 39's.

**By Resolution Status (as of creation, 2026-10-12):**
- ✅ VERIFIED: 0
- ❌ WRONG: 0
- 🔶 PARTIALLY WRONG: 0
- 🔍 INCOMPLETE: 29 — all unknowns open; prep Tasks 2–11 resolve them

---

## Table of Contents

1. [Category 1: The Licensed Toolchain — Local and CI](#category-1-the-licensed-toolchain--local-and-ci)
2. [Category 2: The 11-Model MCP-Gated Cohort — the First Full NLP-vs-MCP Comparison](#category-2-the-11-model-mcp-gated-cohort--the-first-full-nlp-vs-mcp-comparison)
3. [Category 3: The 10-Model NLP-Gated Set — Convexity Evaluation & the Corpus-Entry Decision](#category-3-the-10-model-nlp-gated-set--convexity-evaluation--the-corpus-entry-decision)
4. [Category 4: P10 — the Six P2-Flagged Models, Class A First](#category-4-p10--the-six-p2-flagged-models-class-a-first)
5. [Category 5: lnts — Re-Apply the BANKED Diff Behind a Phase-0 Gate](#category-5-lnts--re-apply-the-banked-diff-behind-a-phase-0-gate)
6. [Category 6: sarf #1385 — the O(active) Re-Architecture at the Jacobian](#category-6-sarf-1385--the-oactive-re-architecture-at-the-jacobian)
7. [Category 7: The Pre-Existing Diagonal-Reference Defect](#category-7-the-pre-existing-diagonal-reference-defect)
8. [Category 8: Positional-Domain Follow-Ons](#category-8-positional-domain-follow-ons)
9. [Category 9: The Smaller Items](#category-9-the-smaller-items)
10. [Category 10: Infrastructure — the Sprint-39 Retrospective's Process Changes as Mechanisms](#category-10-infrastructure--the-sprint-39-retrospectives-process-changes-as-mechanisms)

---

# Category 1: The Licensed Toolchain — Local and CI

## Unknown 1.1: Is the user-level license the EFFECTIVE one, and does it lift the size limit for EVERY solver the pipeline uses?

### Priority
**Critical** — every license-dependent result in the sprint is only evidence if the licensed edition produced it. If GAMS can fall back to the system-directory demo file (another binary, another user, a CI runner), or the license covers GAMS but not one of the solvers, P2/P3 produce demo refusals that look like fresh failures.

### Assumption
The user-level license (`~/Library/Application Support/GAMS/gamslice.txt`, evaluation, valid to 2027-09-21) takes precedence over the system-directory demo file for every way the pipeline invokes `gams`, and it lifts the demo limits — **per model-type demo ceilings** — linear models (LP, CPLEX) are refused only above **2,000** rows/columns; nonlinear types (NLP via CONOPT, MCP via PATH) above **1,000** — for **every solver path the pipeline invokes**: **CPLEX** (`verify_convexity.py` uses `LP=CPLEX` for LP models), **CONOPT for NLP** (`NLP=CONOPT`), **the QCP solver** for the QCP model `emfl` — which `NLP=CONOPT` does **not** select; QCP has its own selection, and the default on this install is CONOPT (measured 2026-10-12: QCP solver selection is **independent of `NLP=`** — `NLP=IPOPT` still ran CONOPT, `QCP=IPOPT` ran IPOPT; on this install the **default QCP solver is CONOPT**; the demo refused a 1,500-row QCP and allowed a 900-row one) — and **PATH** (every MCP solve).

### Research Questions
1. **Precedence:** when both exist, which file does GAMS 54.2.1 read — and is that true for every invocation path the pipeline uses (`shutil.which("gams")` in `test_solve.py` / `batch_translate.py`, subprocesses, a different user or `HOME`)? As of 2026-10-12 the log header reports the evaluation license; the system-directory `gamslice.txt` is still the 2026-07-13 demo file.
2. Does the license lift the limits on **every** solver path — CPLEX (LP), CONOPT (NLP), the QCP solver (`emfl`) and PATH (MCP) — or only some of them (licenses can be solver-selective)? And which QCP solver does a `using qcp` solve actually select under `verify_convexity.py`'s command line?
3. Is it node-locked, time-limited, or otherwise bound in a way that affects CI (Unknown 1.3)?
4. Does a probe sized above **its own model type's** demo ceiling (LP > 2,000; NLP/QCP/MCP > 1,000) **fail on the demo** (positive control) and **solve licensed**, for each of the four solver paths?
5. Should the system-directory demo file be replaced too, so no fallback path can silently run the demo — and does `gams audit lo=2` expose a usable, non-identifying edition discriminator? *(Inspected locally only; its raw output can identify the license and is never committed.)*

### How to Verify
Establish precedence by evidence: move the user-level file aside, re-run, restore — **fail-safe:** copy it to a backup **outside the repo** first and install an `EXIT`/`INT`/`TERM` **trap** that moves it back, so an interruption or failed command cannot leave the demo silently effective; **after restoring, re-check the edition** (the restored file is byte-identical to its pre-test checksum **and** a probe listing classifies as licensed) before any later measurement. *(Prefer pointing `license=` at the system-directory demo file wherever that suffices — it displaces nothing.)* Build a scalable synthetic probe with a size parameter in four variants, each sized above **its own** demo ceiling: **LP > 2,000** (CPLEX), **NLP > 1,000** (CONOPT), **QCP > 1,000** (whatever QCP solver the listing reports — run with `verify_convexity.py`'s own options, `NLP=CONOPT`, so the probe exercises the pipeline's real path), **MCP > 1,000** (PATH) (measured 2026-10-12 under the system-directory demo file: a 1,500-row LP **solved Optimal**, a 2,500-row LP and a 1,500-row NLP were **refused**; both solved under the effective license — so an LP probe sized "just over 1,000" cannot fail on the demo, and would be a vacuous control). Run each under the demo (`license=` pointed at the system-directory demo file) — record the refusal line `"exceeds the demo license limits"` verbatim (the positive control) — then under the effective license, recording `MODEL STATUS` and the solver line. All runs in a scratch directory. **Record no license text.**

### Risk if Wrong
- **The whole of P2/P3 measures the demo:** eleven `path_solve_license` rows re-written as `path_solve_license`, or worse, as some other failure mis-attributed to the emit.
- **Solver-selective license:** LP-type NLP-gated models (airsp, airsp2, indus89, msm, phosdis) stay blocked at CPLEX while NLP models proceed — a P3 result split by license, not by convexity.

### Estimated Research Time
1.5 hours (precedence check, four probe variants × two editions, recording)

### Owner
Sprint 40 prep team (license file placement: project owner)

### Verification Results
✅ **Status:** VERIFIED — the user-level license is the effective one for every pipeline invocation, and it lifts the demo limit on all four solver paths

**Verified by:** Sprint 40 Prep Task 3 · **Date:** 2026-10-13 · **Measured at:** `35b296b3`

**Findings:**
- **Q1 — precedence:** with both files present GAMS reads the **user-level** `~/Library/Application Support/GAMS/gamslice.txt`; with it moved aside (backup outside the repo, restore trap) the same over-ceiling probe is **refused** — the system-directory demo is the fallback; restored, it solves again and the file's SHA-256 is identical to before. Every pipeline path (`gams` on `PATH`, `solve_mcp`'s `Versions/Current`, `kkt_residual.py`'s candidates) resolves to the **one** 54.2.1 binary; 51/53 are never invoked.
- **Q2/Q4 — solver coverage:** probes above their own ceilings (LP 2,500; NLP/QCP/MCP 1,500) are **refused on the demo and solve under the effective license** for **CPLEX** (LP), **CONOPT** (NLP), the **QCP solver — CONOPT here, the install default, not selected by `NLP=CONOPT`** — and **PATH** (MCP); under-ceiling demo runs solve, so size is what flips the result. No solver-selective gap.
- **Q3 — binding:** evaluation license, expires 2027-09-21; the run-time header carries node, memory and core-count fields (node-locked in shape) — carried to Task 4 / Unknown 1.3.
- **Q5:** no reinstall needed; `gams audit lo=2` was inspected locally only (its output can identify the license) — the `.lst` discriminator (Unknown 1.2) is the edition source instead.

**Evidence:** `LICENSE_PROBE.md` §1–§2 (precedence table; per-solver table; the four verbatim refusal lines, which also state the ceilings: 2,000 linear, 1,000 nonlinear).

**Decision:** Verified. One residual risk, recorded as a recommendation rather than a defect: a process with a different user or `HOME` silently falls back to the demo — `LICENSE_PROBE.md` §5 recommends the owner replace the system-directory demo file; Task 5's per-row `license_edition` detects any demo run regardless.

---

## Unknown 1.2: Does a `.lst` file carry a parseable string that distinguishes the licensed edition from the demo?

### Priority
**High** — P1's schema 3.1.0 `license_edition` field is populated from this string. If no stable discriminator exists, the writer needs a second source (`gams audit`, an environment flag) and the design changes.

### Assumption
The `.lst` header carries a stable, parseable line that differs between demo and licensed runs, and `test_solve.py::extract_gams_version` can be extended to read it.

### Research Questions
1. Which header line(s) differ between a demo and a licensed `.lst` of the same model — and can that difference be captured by a **non-identifying pattern** (one that matches an edition marker, never licensee, ID or node text)?
2. Is the line present in the `.lst` of **every** stage — convexity solves (`verify_convexity.py` writes to a temp `output.lst`), MCP solves, and the presolve-embedded NLP?
3. Is it stable across solvers and model types (LP / NLP / QCP / MCP)?
4. Can it be read without capturing any license-identifying text (licensee name, serial)?
5. Does a demo-refused run still print it — i.e. can `license_edition: "demo"` be recorded for a refusal?

### How to Verify
Diff the headers of Unknown 1.1's paired probe `.lst` files (demo vs licensed) for each solver **locally, without committing them**; grep the pattern in a convexity, an MCP and a presolve `.lst`. Write the candidate regex and require it to classify **every generated listing** correctly — at least the **eight** probe listings (four solver variants × demo/licensed) plus the convexity-, MCP- and presolve-stage listings. Then **invert the classifier deliberately and assert the check FAILS** (the positive control): a check that still passes under inversion cannot tell the editions apart. **Record only the regex and the classification table** — never the header lines themselves.

### Risk if Wrong
- **`license_edition` written from a guess**, the precise failure the schema's null semantics exist to prevent.
- **Licensee text captured into the DB** — a leak into a committed file.

### Estimated Research Time
1.0 hour (header diffs, regex, cross-stage check)

### Owner
Sprint 40 prep team

### Verification Results
✅ **Status:** VERIFIED — every stage's `.lst` carries a non-identifying edition discriminator

**Verified by:** Sprint 40 Prep Task 3 · **Date:** 2026-10-13 · **Measured at:** `35b296b3`

**Findings:**
- **Q1:** `.lst` headers do **not** carry the license block (that is the GAMS log); the discriminators are generic markers — a completed demo run's `USER: GAMS Demo, …` header, a refused demo run's `**** The model exceeds the demo license limits …` line, and a completed licensed run's `USER:` line that is **not** `GAMS Demo,` (matched by prefix with a negative lookahead; its licensee text is never captured).
- **Q2:** present in the **convexity-stage** (`LP=CPLEX`, as `verify_convexity.py`), **MCP-stage** (golden) and **presolve-stage** (one listing holding an NLP and an MCP solve) listings.
- **Q3:** stable across LP / NLP / QCP / MCP.
- **Q4:** yes — the regex reads no identifying text.
- **Q5:** yes — a refused demo run has no `USER:` line but always the refusal line, so `license_edition: "demo"` can be recorded for a refusal; a listing with neither is `None`, never guessed.

**Evidence:** `LICENSE_PROBE.md` §3 — the regex and the classification table: **20/20** paired listings correct; the **inverted** classifier gives 20/20 mismatches and a non-zero exit.

**Decision:** Verified. Task 5's parser keys on this regex (extend `test_solve.py::extract_gams_version`, read before the temp directory is removed).

---

## Unknown 1.3: Can CI use the license WITHOUT exposing it — do the license terms allow hosted runners, and does a `main`-only environment really refuse other refs?

### Priority
**High** — the CI design (PR #1745 review) rests on two external facts: that the license terms permit GitHub-hosted ephemeral runners, and that a protected environment's deployment-branch policy refuses a `workflow_dispatch` from a non-`main` ref. If either is false, the CI half REPLANs (self-hosted runner, or no licensed CI).

### Assumption
(a) The license terms allow installation on ephemeral hosted runners; (b) an environment secret behind a `main`-only branch policy is unreachable from any job running unmerged code; (c) no existing workflow uses `pull_request_target` with a PR-head checkout.

### Research Questions
1. What do the license terms say about cloud/CI/ephemeral machines and concurrent installations?
2. Does GitHub refuse an environment to a `workflow_dispatch` (or `push`) on a branch other than `main` when the branch policy says `main` only — verified, not read?
3. Which workflows trigger on `pull_request`, and do any reference secrets today (only `publish-pypi.yml` does, at `912d005c`)?
4. Which PR-workflow tiers or target lists (e.g. `.github/path-solve-ci-targets.txt`) were shaped by the demo limit, and would moving them post-merge reduce PR-time coverage?
5. Does the license's binding (Unknown 1.1 Q3) survive a fresh runner each run?

### How to Verify
Read the license terms (owner). In a throwaway repository, create an environment with a `main`-only policy and a dummy secret; dispatch from a non-`main` branch and record the refusal (the negative control), then from `main` and record access. Inventory triggers with the loop in `PREP_PLAN.md` Task 4 *Verification*.

### Risk if Wrong
- **Hosted runners forbidden:** the CI half becomes a self-hosted-runner project — days, not hours.
- **Branch policy bypassable:** the design leaks the license to any contributor who can push a branch — the exact failure the review flagged.

### Estimated Research Time
1.5 hours (terms read, throwaway-repo test, trigger inventory)

### Owner
Sprint 40 prep team (license terms: project owner)

### Verification Results
🔶 **Status:** PARTIALLY WRONG — the isolation controls hold (✅ `main`-only environment refuses other refs; ✅ no `pull_request_target`), but the license cannot safely reach CI today: hosted runners are very unlikely to validate a node-locked license, and the self-hosted fallback cannot be restricted on a personal-account repo

**Verified by:** Sprint 40 Prep Task 4 · **Date:** 2026-10-14 · **Measured at:** `c8f769c4`

**Findings:**
- **Q1 — terms / hosted runners: not established, evidence against.** Task 3: evaluation license, expires 2027-09-21, header carries node, memory and core-count fields — node-locked in shape. Not tested in CI on purpose (installing the real license anywhere in CI before the owner's decision is the exposure this design prevents). Owner question for GAMS.
- **Q2 — branch policy: ✅ verified empirically** in a throwaway public repository: a `main`-only `gams-licensed` environment with a 25-character dummy secret. `main` (`push`, `workflow_dispatch` ×2) reached it (`SECRET_REACHABLE len=25` — the positive control); a branch carrying **its own copy** of the workflow was **refused before the job ran** on `push`, same-repo `pull_request` (`refs/pull/1/merge`) and `workflow_dispatch` ×2 — *"Branch … is not allowed to deploy to gams-licensed due to environment protection rules."*
- **Q3 — workflows:** 10 workflows, parsed as YAML, with their branch/path filters; the two GAMS-installing workflows are `pull_request`-only (to `main`, path-filtered) and run PR-controlled code, so they must stay demo-only. Only `publish-pypi.yml` uses secrets — as **repository** secrets, behind a `workflow_dispatch` that runs any selected branch with an unqualified checkout: a **pre-existing, non-GAMS exposure** (owner checklist item 6). Generally, *no automatic PR trigger* ≠ *cannot run branch code*: `nightly.yml` and `gamslib-regression.yml` also run any dispatched ref.
- **Q4 — demo-motivated exclusions:** none by rule; instead **six MCP-gated models sit in PR19's soft-fail tier** (`egypt`, `ferts`, `shale`, `sroute`, `srpchase`, `tfordy`) and license-fail on every PR, indistinguishable from emit failures.
- **Q5 — binding vs fresh runners:** see Q1.
- **New: the self-hosted fallback fails its own constraint here.** Restricting a runner to selected workflows is an organization runner-group feature; `jeffreyhorn/nlp2mcp` is user-owned, so any branch's workflow could target the runner — and on the licensed machine the license is a file a job could read directly, whatever the environment policy.
- **`pull_request_target`:** none anywhere in `.github/`.

**Evidence:** `CI_LICENSE_DESIGN.md` §1 (inventory), §2 (exclusions), §4 (throwaway-repo table, including a recorded measurement slip caught by the positive control), §5 (runner assessment).

**Decision:** The controls the design relies on are real, but **the licensed tier stays local-only for Sprint 40**, audited by Task 5's `license_edition`; `licensed-solve.yml` (§3) is adopted only if GAMS provides a CI-usable license or the repo moves to an organization. Carried to Task 6 decision 3 (owner checklist, `CI_LICENSE_DESIGN.md` §7).

---

## Unknown 1.4: Can the schema-3.1.0 writer/initializer list be CLOSED — every existing writer found, and the missing P3 convexity application writer designed?

### Priority
**High** — `data/gamslib/schema.json` is at 3.0.0 with `additionalProperties: false` on both result types. PR #1745's review found the plan's writer list incomplete twice; a third omission found after the P2 batch means rows written without their edition.

### Assumption
The code that writes `mcp_solve` or `convexity` records, or stamps a `schema_version`, is: `scripts/gamslib/test_solve.py`, `scripts/gamslib/run_full_test.py` (passthrough), `scripts/gamslib/verify_convexity.py` (output JSON / flat `catalog.json` fields only), **`scripts/gamslib/migrate_catalog.py` (the constructor of the DB's nested `convexity` object, ~L156–181)**, `scripts/gamslib/db_manager.py` (`--empty` and the catalog-init chain) — **plus a P3 application writer that does not exist yet**: nothing today applies verifier output to `gamslib_status.json`, so the closed list is not closed until that writer is designed.

### Research Questions
1. Which files assign into an `mcp_solve` or `convexity` dict, or construct one? (grep, not recall)
2. Which files contain a `"3.0.0"` literal — nine hits across `scripts/` and `tests/` at `912d005c` — and which are writers vs. tests?
3. Does any `scripts/sprint_audit/` tool write `mcp_solve` DB fields? *(At `912d005c`: `check_mcp_solve_attribution.py` writes an `attribution.json` report, not the DB; `mcp_attribution` / `mcp_completed_own_solve` are constructed in `scripts/gamslib/test_solve.py` — confirm no other path does.)*
4. Does `convexity_result` need `gams_version` added as well as `license_edition` (it lacks it today)?
5. Does any reader break on an extra field (a strict reader with its own allow-list)?

### How to Verify
`grep -rn` for assignments into the two dicts and for `schema_version` literals; read each hit; classify writer / reader / test. Validate a hand-edited row carrying the new fields against the current schema to confirm it **fails** (positive control), then against a draft 3.1.0 schema to confirm it passes.

### Risk if Wrong
- **P2 rows written without `license_edition`**, so `path_solve_license 11 → 0` is not checkable from the DB as the acceptance criterion requires.
- **A validation failure mid-batch** if a writer adds the field before the schema allows it.

### Estimated Research Time
1.0 hour (grep, classification, two validation runs)

### Owner
Sprint 40 prep team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — the list **can be closed** (✅), but the assumed list was **incomplete**: grep found three sites it omits — `run_full_test.py::mark_cascade_not_tested` (two `mcp_solve` constructions), `db_manager.py update` (a hand-writer of any nested field) and `schema.json`'s `description` "(v3.0.0)" (the canonical-version source a test reads). The P3 application writer is designed, with the corpus hold built in.

**Verified by:** Sprint 40 Prep Task 5 · **Date:** 2026-10-14 · **Measured at:** `a8bff1d8`

**Findings:**
- **Q1, writers (grep, not recall):** 11 sites, W1–W11 in `SCHEMA_3_1_0_DESIGN.md` §3:
  - `test_solve.py`: `solve_mcp`, plus `update_model_solve_result`, a **fixed-key-list rebuild** (the Sprint 39 "second writer" that once dropped `mcp_attribution`);
  - `run_full_test.py`: `run_solve_stage`, the **cascade** writer (new), and the presolve copy/restore (no change needed);
  - `db_manager.py update` (new);
  - `migrate_catalog.py` (builds `convexity`, but **regenerates a whole DB**, so it is not an apply path);
  - `verify_convexity.py`: `update_catalog_entry` and `verify_model`;
  - the new P3 application writer and the new migration.
- **Q2, `"3.0.0"` literals:** **9** double-quoted hits re-confirmed (`db_manager.py:292`, `migrate_schema_v3.0.0.py:58`, 4 in `test_migrate_schema_v3.py`, 3 in `test_db_manager.py`). An any-quoting grep adds **`schema.json`'s `description`**, which `test_db_manager.py:641` parses as the canonical version. It must move with `db_manager.py:292`.
- **Q3, `sprint_audit/`:** `check_mcp_solve_attribution.py` is an inspector (writes `attribution.json`; version check pattern-only); `floor_tracker.py`, `kpi_block.py` and `check_doc_figures.py` only read. **No `sprint_audit/` tool writes DB fields.**
- **Q4:** **yes.** `convexity_result` lacks `gams_version`. It also defines `solver` but **0/219** rows carry it (nothing writes it), and `solver` / `solver_status` / `model_status` / `objective_value` are non-nullable there, so the new writer must omit them when unknown.
- **Q5, strict readers:** **none break.** No allow-list, `extra='forbid'`, `**row` constructor, exact-key assertion or exact-version comparison on these objects. What does behave differently:
  - `migrate_schema_v3.0.0.py --validate` stops validating a 3.1.0 DB;
  - `test_migrate_schema_v3.py`'s rewind of the committed DB would become a hybrid unless its pop list grows (T6);
  - the top-level `_migration_summary_v3_1_0` must be declared, since the root is `additionalProperties: false`.
- **Measured on synthetic probes:** a refused demo listing **carries** the `GAMS 54.2.1` header but **no** `SOLVER` line, so refused rows record the version and `demo`, with no solver.

**Evidence:** `SCHEMA_3_1_0_DESIGN.md` §3 (grep commands and the classified table), §4 (probe table), §10 (positive control). A real row with the new fields **fails** the current schema and **passes** a draft 3.1.0 schema; the draft **still rejects** `"unknown"`, a misspelled `licence_edition` and an unknown `convexity` key.

**Decision:** P1 implements the closed list in §11's order. **Schema and first writer go in one commit**, so no writer emits the field before the schema allows it. **W10's `--admit` hold** keeps a licensed convexity write from silently growing the 142 before Task 6's corpus-entry decision (the Unknown 3.3 risk).

---

## Unknown 1.5: Is the license OUTCOME-NEUTRAL for every model outside the two gated populations?

### Priority
**Critical** — the sprint's KPI deltas assume the license changes only size-refused solves. If the licensed edition changes any other outcome (different default solver options, threads, a different CONOPT/PATH build path, iteration limits tied to the edition), every Sprint 39 → 40 comparison mixes a toolchain effect with fixes.

### Assumption
For every model not in the MCP-gated or NLP-gated populations, a licensed run reproduces the demo run's outcome category, objective (within tolerance) and comparison verdict.

### Research Questions
1. Does the licensed edition change any solver default that affects small models (iteration limits, threads, option-file search)?
2. Do a sample of currently-matching models (cold and presolve) reproduce byte-identical `MODEL STATUS` and objective licensed?
3. Do a sample of currently-*failing* models keep their failure bucket — or does any "failure" turn out to have been a hidden license effect?
4. Does `gams_version` (54.2.1) stay identical, so per-row provenance changes only in `license_edition`?
5. What sample size makes "neutral" a claim rather than an anecdote? *(Whatever the size, a sample cannot establish the **universal** assumption — see How to Verify.)*

### How to Verify
After Unknown 1.1 installs the license, re-solve a stratified sample (e.g. 5 cold matches, 5 presolve matches, 1 per failure bucket) in a scratch directory and diff outcome/objective/verdict against the DB. **What the sample can and cannot settle:** this assumption is universal ("every model"), so a sample can **refute** it (❌ WRONG, with the moved rows routed) but cannot verify it. A clean sample leaves 1.5 at the **existing** status `🔍 **Status:** INCOMPLETE — sample-neutral at `<sha>`; universal claim routed to the first licensed full run` — recording the sample evidence beneath it — and Task 12 routes it (`PROJECT_PLAN.md` Sprint 40 already makes that run's license-neutrality a gate). **Never mark 1.5 ✅ VERIFIED from the sample alone.** *(This uses the document's existing INCOMPLETE status rather than a new one, so the tally and the prep prompts' status vocabulary need no new category.)* **Positive control (synthetic — never a real gated model):** run the **same diff procedure** on Task 3's synthetic over-ceiling NLP probe, demo vs effective license; the procedure **must** report the change. A real size-refused DB model cannot serve: every such model is, by definition, in the MCP-gated or NLP-gated population, and reading its licensed outcome before Task 6's answers are committed would break the blind-decision boundary. The sprint's first full licensed run is the exhaustive test.

### Risk if Wrong
- **KPI attribution corrupted:** a "+N" partly caused by the toolchain, booked as fixes or cohort unlocks.
- **A hidden license effect in an existing bucket** — a model currently blamed on the emit that was really demo-limited (e.g. through an embedded presolve NLP).

### Estimated Research Time
1.5 hours (sample selection, ~15 re-solves, diff)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE — sample-neutral at `35b296b3`; universal claim routed to the first licensed full run

**Verified by:** Sprint 40 Prep Task 3 · **Date:** 2026-10-13 · **Measured at:** `35b296b3`

**Findings (sample evidence):** 13 models outside both gated populations, chosen by identity across strata — cold match `rbrock`, `house`, `pindyck`, `prolog`, `cesam2`; presolve match `mingamma`, `himmel16`, `harker`, `moncge`, `catmix`; solved-mismatch `weapons`; `model_infeasible` `agreste`; `path_syntax_error` `indus` — run through the real pipeline in a throwaway worktree with the retention patch. **All 20 GAMS invocations classified licensed** from their own listings (`head_sha` `35b296b3`). **0 of 13 rows changed** against the committed demo-era DB on outcome, objective (rel. tol. 1e-6) and verdict. `gams_version` unchanged (54.2.1).

**Positive control:** the same diff on the synthetic over-ceiling NLP probe, demo vs licensed, reports `outcome: license_refused → model_status_1; objective: None → 1500.0`.

**Evidence:** `LICENSE_PROBE.md` §4.

**Decision:** The sample does **not** refute neutrality, and a sample cannot verify a universal claim — so 1.5 stays INCOMPLETE by design, **routed to the sprint's first licensed full run** (a `PROJECT_PLAN.md` Sprint 40 gate; Task 12 schedules it). This is the stated exception in *Next Steps*, not a miss.

---

# Category 2: The 11-Model MCP-Gated Cohort — the First Full NLP-vs-MCP Comparison

## Unknown 2.1: Do all eleven re-emit at HEAD byte-identical to their goldens, within the pipeline's translate timeout?

### Priority
**Critical** — P2's batch reads the committed goldens. If any golden is stale, the batch solves an emit HEAD no longer produces; if any translate exceeds the timeout, that member cannot be re-checked by the licensed workflow on every merge.

### Assumption
All 11 goldens (`egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `tricp`, `turkey`) are byte-identical to a HEAD re-emit, and every member translates within the pipeline timeout.

### Research Questions
1. Is each golden byte-identical to a fresh emit at HEAD? (The leak gate checks this for in-scope goldens — are all 11 in its 186-golden scope?)
2. What is each member's translate wall-clock? S39 prep's census **could not parse `turkey` inside 120 s** (S39 Unknown 6.2).
3. Are the recalled sizes right — turkey 3,866 rows, tricp 1,255, egypt ~3,470 equations (#927) — when derived from the goldens?
4. Does a nightly slot or a CI job timeout fit the batch's total wall-clock?
5. Does `--only-solve` handle rows with `solver_version: None` without re-translating?

### How to Verify
Re-emit each in a scratch copy and `cmp` against `data/gamslib/mcp/<model>_mcp.gms`; time each translate; derive sizes as **generated dimensions, not declarations**: run each golden in a scratch directory with `iterlim=0` and read the listing's `MODEL STATISTICS` — `SINGLE EQUATIONS` and `SINGLE VARIABLES`. Counting declarations in the source does **not** measure size (measured 2026-10-12 on `turkey`'s golden: **89** equation blocks vs **3,866** single equations / 3,753 single variables). The demo license prints `MODEL STATISTICS` **before** refusing an over-limit model, so this needs no license (same figures under both editions); confirm leak-gate scope membership from `check_golden_staleness.py`'s in-scope list.

### Risk if Wrong
- **A first measurement of a stale emit**, attributed to the current code.
- **A member that cannot run in CI**, so its result is measured once and never re-checked — the outcome P1's licensed workflow exists to prevent.

### Estimated Research Time
1.5 hours (11 re-emits with timing, size derivation, scope check)

### Owner
Sprint 40 prep team

### Verification Results
✅ **Status:** VERIFIED — all 11 re-emit **byte-identical** to their goldens at HEAD, and all translate inside the 600 s limit.

**Verified by:** Sprint 40 Prep Task 7 · **Date:** 2026-10-14 · **Measured at:** `79eeccff` (all 53 retained invocations; descends from Task 6's answers commit `b44344a2`)

**Findings:**
- **Q1:** 11/11 goldens are byte-identical to a HEAD re-emit (`run_full_test.py` re-translates in the worktree; `git diff --quiet` on each golden). **All 11 are in the leak gate's in-scope set** (`check_golden_staleness.discover_goldens()` minus its allowlist).
- **Q2, translate wall-clock:** `ferts` 167.1 s · `turkey` 55.1 s · `egypt` 49.0 s · `tabora` 40.9 s · `tfordy` 22.8 s · `shale` 19.5 s · `sroute` 14.9 s · `robot` 4.4 s · `glider` 4.4 s · `tricp` 3.7 s · `srpchase` 2.1 s.
  - **`turkey` translates in 55 s**, so S39 prep's "could not parse inside 120 s" no longer holds.
- **Q3:** sizes as measured by Task 2 (contribution below).
- **Q4:** the whole MCP-gated batch takes **763 s**, ~13 min (max `ferts` 184 s), so it fits a nightly slot.
- **Q5, read from the code, not re-run:** `--only-solve` requires `nlp2mcp_translate.status == "success"` and then solves the existing MCP without re-translating, whatever `solver_version` holds.

**Evidence:** `COHORT_DRY_RUN.md` §Results (golden column), §Wall-clock.

**Decision:** P2's batch can read the committed goldens as they stand. No staleness finding.

**Contribution from Task 2 (2026-10-13, `366e91f3`) — status left to Task 7:** sizes measured as generated dimensions (golden run with `iterlim=0`, `MODEL STATISTICS`), identical under the demo and the effective license: egypt 3,447 eq / 3,537 var · ferts 5,702 / 5,702 · glider 1,531 / 1,637 · robot 1,688 / 1,694 · shale 1,956 / 1,956 · sroute 1,531 / 1,540 · srpchase 4,005 / 4,005 · tabora 1,894 / 1,924 · tfordy 3,155 / 3,157 · tricp 1,255 / 1,400 · turkey 3,866 / 3,753. Recalled turkey 3,866 and tricp 1,255 reproduce; **egypt's "~3,470" does not (3,447)**. Byte-identity, translate times and leak-gate scope membership remain Task 7's. See `BASELINE_RECONFIRMATION.md` §5.

---

## Unknown 2.2: Will the cohort's first solves yield a BOUNDED work list — every non-match residual-classified and routable — rather than open-ended diagnosis?

### Priority
**Critical** — the sprint's dominant risk (PROJECT_PLAN Sprint 40 *Risk Level*) is a cascade of first-time fingerprints. If the dry run produces fingerprints that cannot be classified by `kkt_residual.py` or routed to a known defect class, P2's 16–22 h and the schedule both break.

### Assumption
Every non-match falls into a recognisable class — the P10 Class-A defect (egypt, shale), the repeated-declared-domain class (7 of 11 per S39 Unknown 6.2), a known bucket — and `kkt_residual.py` returns a verdict for each within budget.

### Research Questions
1. How many of the 11 reach a PATH outcome vs. a compile error vs. a translate failure?
2. Of the non-matches, how many get `CASE_A` (genuine local optimum), `CASE_B` (emit bug) or `CASE_C` (solver behaviour)?
3. Do the 7 repeated-domain members fail more often than the other 4 — i.e. is S39's defect-class flag predictive?
4. Can `kkt_residual.py` run on the largest members (turkey, egypt) within a reasonable time, and does it need the license itself?
5. How many fingerprints fail the P10 selection rule (no named fix surface) and must be banked?

### How to Verify
Task 7's dry run: per member, record outcome, comparison, attribution and residual verdict; tabulate classes; cross-tab against S39's repeated-domain flag. Report the count of unroutable fingerprints explicitly.

### Risk if Wrong
- **An open-ended diagnosis sprint** — the failure the P10 selection rule was written to prevent.
- **A schedule built on 16–22 h for P2** that needs double, displacing P6 (sarf) — the sprint's only planned Translate mover.

### Estimated Research Time
2.0 hours (residual runs on non-matches, classification, cross-tab)

### Owner
Sprint 40 prep team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — the work list **is bounded** (**0 unrouted fingerprints**), but `kkt_residual.py` returned a verdict for only **5 of the 11** non-matches with an MCP, and S39's repeated-domain flag is **not predictive**.

**Verified by:** Sprint 40 Prep Task 7 · **Date:** 2026-10-14 · **Measured at:** `79eeccff` (all 53 retained invocations; descends from Task 6's answers commit `b44344a2`)

**Findings:**
- **Q1, how far each of the 11 gets:** **11/11 reach a GAMS listing.**
  - 9 reach a PATH model status: 5 infeasible, 2 solved non-matches, 2 presolve matches.
  - 2 abort before PATH reports (`ferts`, `tabora`: `no_solve_summary`).
  - 0 compile errors, and 0 translate failures.
- **Q2, residual verdicts:** **5 × `case_b` (emit bug):** `glider`, `minsurf`, `robot`, `sroute`, `tricp`. No `case_a`, no `case_c`. The other **6 have no verdict, because the harness itself fails on the `--nlp-presolve` emit** it evaluates:
  - compile errors: `egypt` and `srpchase` (`$140`), `shale` (`$148`), `jbearing` (`$171`);
  - execution aborts: `ferts` (`EXECERROR = 46`), `tabora` (`= 36`).
  - **The assumption "a verdict for each" fails exactly where the presolve emit is defective.**
- **Q3, repeated-domain cross-tab:** flagged members were non-matches **6 of 7** times, unflagged ones **3 of 4**. **Not predictive** at this size.
- **Q4:** the largest members ran in budget (max `ferts` 138 s). It needs the license, since it runs the embedded NLP solve.
- **Q5, P10 selection rule:** only **2** fingerprints meet it today (`egypt`, `shale` → P4). The other 9 non-match models with an MCP are **banked** behind routing notes: R-PRE-140, R-EXEC, R-JB-171, R-B-*.

**Evidence:** `COHORT_DRY_RUN.md` §Routing.

**Decision:** P2's work list is the Routing table, with every class and model named.
- **Not open-ended**, but **not fix-ready either.**
- The `--nlp-presolve` emit defects (R-PRE-140, `shale`'s `$148`, R-JB-171) **block the diagnosis tool** as well as the warm start, so they come first.

---

## Unknown 2.3: Does `check_mcp_solve_attribution.py` work on the licensed large models — can it tell a real MCP solve from a presolve self-match at this size?

### Priority
**High** — every cohort match must show *our* MCP produced its own `MODEL STATUS` (the `weapons` trap). The tool was built and tested on demo-sized models; if it times out or misreads a large `.lst`, P2's matches are unverifiable.

### Assumption
`scripts/sprint_audit/check_mcp_solve_attribution.py` runs on each cohort member within its `reslim`, parses the large `.lst` correctly, and returns `MCP-SOLVED` / not-solved without error.

### Research Questions
1. Do the cohort members even take the presolve path (none has a presolve golden today)?
2. Does the tool's default `reslim` suffice for turkey/egypt-scale MCPs?
3. Does its positional `.lst` parse still find the MCP's own `MODEL STATUS` in a multi-megabyte listing?
4. Does it pass its own positive control on a large model — a known self-match fixture reported as not-solved?
5. Does it need the license (it re-solves), and therefore run only locally or in the licensed workflow?

### How to Verify
**Validate each dry-run match from its own recorded fields** — `mcp_attribution` / `mcp_completed_own_solve`, which `test_solve.py` parses from the **actual solve listing** before deleting it (read from the throwaway worktree's DB copy). The standalone `check_mcp_solve_attribution.py` re-emits and re-solves a **fresh** `--nlp-presolve` model, so it does **not** audit the dry-run's listing; run it **separately** as the large-model exercise on the largest members and on one constructed self-match (the positive control — the `weapons`-shaped fixture in `tests/unit/sprint_audit/test_mcp_solve_attribution.py` shows the pattern). Record wall-clock and verdict for both.

### Risk if Wrong
- **A spurious cohort match booked as Solve/Match**, discovered later as a correction — the `weapons` story at scale.

### Estimated Research Time
1.0 hour (runs on matches + one positive control)

### Owner
Sprint 40 prep team

### Verification Results
✅ **Status:** VERIFIED — the standalone tool works at full size and passes its positive control. Every dry-run match is validated from its **own** recorded `mcp_attribution` / `mcp_completed_own_solve`.

**Verified by:** Sprint 40 Prep Task 7 · **Date:** 2026-10-14 · **Measured at:** `79eeccff` (all 53 retained invocations; descends from Task 6's answers commit `b44344a2`)

**Findings:**
- **Q1, presolve path:** **yes**. 7 of the 11 took the presolve retry (cold MS 5 or a spurious-KKT mismatch).
  - **All 4 matches** (`tfordy`, `turkey`, `airsp2`, `torsion`) are `model_optimal_presolve`, recorded `MCP-SOLVED` / `own=True`.
  - Each was re-derived from that invocation's own retained listing with `parse_solve_summaries` / `Attribution`: 1 candidate, 1 match.
- **Q2/Q3, at size:** `turkey`, the largest member, gives **`MCP-SOLVED`**. The positional parse picks our `mcp_model` out of three summaries (CONOPT NLP, CPLEX LP, PATH MCP).
- **Q4, positive control:** `weapons` (the S38 D9 self-match) gives **`EMBEDDED-ONLY`**, correctly not counted; the tool exits 1 by design. `egypt` is **indeterminate**, because its presolve emit does not compile (`NO-SOLVE`).
- **Q5:** it needs the license, since it re-solves. Wall-clock: **106 s** for all three.

**Evidence:** `COHORT_DRY_RUN.md` §Summary, §Results (attribution column).

**Decision:** P2 validates each match from the row's own recorded attribution fields. The standalone tool remains a spot check, not an audit of the batch's listings.

---

## Unknown 2.4: Does `ISSUE_933` (tricp MCP compilation errors) still reproduce, now that tricp carries the S38 D11 fix?

### Priority
**Medium** — the issue is OPEN and untriaged; tricp's golden changed in S38 D11 (`slp(n,n)`). If the errors are gone, the issue closes; if not, tricp is a cohort member that cannot reach PATH and P2's ceiling is +10, not +11.

### Assumption
`docs/issues/ISSUE_933_tricp-mcp-compilation-errors.md` describes errors that the S38 D11 repeated-domain fix may have removed, and a licensed compile of the current golden settles it.

### Research Questions
1. Which compilation errors does the issue record, and against which golden revision?
2. Does the current golden compile (`gams tricp_mcp.gms action=c`) licensed?
3. If errors remain, are they the issue's, or new?
4. Is the issue's described mechanism related to the repeated-domain class?

### How to Verify
Read the issue; compile the current golden licensed in a scratch directory; diff the error list against the issue's. Close, re-scope or update the issue accordingly.

### Risk if Wrong
- **P2 plans +11 when one member cannot compile**; or an obsolete issue stays open and misdirects a future sprint.

### Estimated Research Time
0.5 hours (read, compile, diff)

### Owner
Sprint 40 prep team

### Verification Results
✅ **Status:** VERIFIED — the S38 D11 fix removed the errors. **`ISSUE_933`'s compile errors do not reproduce**, so the issue is **re-scoped** (not closed).

**Verified by:** Sprint 40 Prep Task 7 · **Date:** 2026-10-14 · **Measured at:** `79eeccff` (all 53 retained invocations; descends from Task 6's answers commit `b44344a2`)

**Findings:**
- **Q1:** the issue's last recorded state (2026-04-01) is **10 compile errors**: `$148` ×2, `$149` ×6, `$141`/`$257`. Its title and early sections still describe the older Sprint 21 translation timeout.
- **Q2:** the current golden (byte-identical to HEAD) has **0** compile-error markers in its own retained listing. Licensed, it **reaches PATH**.
- **Q3:** no errors remain. The open defect is now **wrong**, not uncompilable: cold and retry both MS 5, and `kkt_residual.py` returns `case_b` at `stat_x(n,k0)`, rel 1.69.
- **Q4:** yes. The errors were the repeated-domain class (`(n,n)` multipliers, uncontrolled indices), and the S38 D11 `slp(n,n)` fix removed them.

**Evidence:** `COHORT_DRY_RUN.md` §ISSUE_933; `docs/issues/ISSUE_933_tricp-mcp-compilation-errors.md` *Current Status (2026-10-14)*.

**Decision:** tricp **can** reach PATH, so P2's ceiling is not reduced by a compile failure. tricp is routed as R-B-tricp, an emit-correctness item.

---

# Category 3: The 10-Model NLP-Gated Set — Convexity Evaluation & the Corpus-Entry Decision

## Unknown 3.1: Are the nine non-MIP NLP-gated models in scope by type, and do they parse with the current grammar?

### Priority
**High** — P3 assumes nine candidates. Their DB rows carry **no `nlp2mcp_parse` key at all** — they have never been parsed. If several fail to parse, P3's convexity work produces candidates the pipeline cannot use, and the corpus decision is about models that would sit in `parse` failure.

### Assumption
`airsp`, `airsp2`, `emfl`, `indus89`, `jbearing`, `minsurf`, `msm`, `phosdis`, `torsion` are LP/NLP/QCP (in scope under the MINLP/MIP exclusion rule), `andean` is the only MIP, and most parse with the current grammar.

### Research Questions
1. Does each model's `gamslib_type` match its source (`solve ... using lp|nlp|qcp`), and is any a multi-solve driver (the S24 `decomp`/`danwolfe` exclusion)?
2. Does each parse today, and in what time? (Parsing needs no license.)
3. Does each translate today (also license-free)?
4. Are any duplicates or variants of an in-corpus model (e.g. `airsp2` of `airsp`) that should be treated as one decision?
5. Is `andean` unambiguously MIP (excluded, never relaxed)?

### How to Verify
Read `gamslib_type` from the DB and the `solve` statement from each raw source; run parse and translate for each in a scratch directory (license-free) and record pass/fail and time.

### Risk if Wrong
- **P3 budgets convexity work for models the pipeline cannot parse**, and the owner decides corpus entry for models that would sit in a failure bucket.
- **A multi-solve driver admitted** — the S24 validator-gate class.

### Estimated Research Time
1.0 hour (type check, 9 parse + translate runs)

### Owner
Sprint 40 prep team

### Verification Results
✅ **Status:** VERIFIED — all nine in scope by type, `andean` the only MIP, and **6/9 parse** (a majority, as assumed). *Separate finding, routed below: only **4/9 translate** — translation was not part of this assumption.*

**Verified by:** Sprint 40 Prep Task 2 · **Date:** 2026-10-13 · **Measured at:** `366e91f3`

**Findings:**
- **Q1 — type: ✅.** The raw sources' `solve … using` statements confirm the DB's `gamslib_type` for all nine: LP ×5 (`airsp`, `airsp2`, `indus89`, `msm`, `phosdis`), QCP ×1 (`emfl`), NLP ×3 (`jbearing`, `minsurf`, `torsion`). `andean` is MIP (`minlp_out_of_scope`) — excluded, never relaxed. **No multi-solve driver** among the six that parse, by the pipeline's own `scan_multi_solve_driver` (several have more than one `solve`: `airsp2` ×6, `msm` ×5, `airsp` ×3, `torsion` ×2 — the classifier does not count those as drivers).
- **Q2 — parse: 6/9.** Fails: `emfl` (L36, `%new%` compile-time variable in a set range), `indus89` (L128, `Singleton Set`), `phosdis` (L609, `for(iter = 1 to 7, …)` loop syntax).
- **Q3 — translate: 4/9** (`airsp2` 4.8 s, `jbearing` 74.2 s, `minsurf` 23.5 s, `torsion` 15.4 s). `airsp` and `msm` parse but **time out at the pipeline's 600 s** translate limit — cause not diagnosed.
- **Q4 — duplicates:** `airsp2` is the DECIS stochastic variant of `airsp` (297 vs 170 lines, 355 differing lines) — **not** a near-duplicate; assessed separately.
- **Q5 — `andean`:** unambiguously MIP.

**Evidence:** `parse_model_file` + `scan_multi_solve_driver` per model; `python -m src.cli <raw> -o <scratch>` with a 600 s timeout; per-model times and error lines in `BASELINE_RECONFIRMATION.md` §4.

**Decision:** **Both clauses of the assumption hold** — 9/9 in scope by type (`andean` the only MIP) and 6/9 parse, a majority. *(Corrected in PR #1747 review: this was first graded 🔶 PARTIALLY WRONG, conflating the separate translate result with the parse assumption.)* **Separate finding, routed:** only **4** of the nine reach a translated MCP today — which matters more for P3 than the parse rate does. Routed: **Task 6** (the corpus-entry brief must show how many models each option would actually admit, and that five need work first), **Task 7** (end-to-end dry run only for the four that translate; record the two timeouts and three parse failures as they stand), **Sprint 40 P3** (three grammar items and two undiagnosed translate timeouts).

---

## Unknown 3.2: How many of the nine classify `verified_convex` / `likely_convex` under the existing verifier once licensed?

### Priority
**High** — the corpus-entry decision is about the convex subset; its size bounds how far the denominator could move (142 → at most 151) and how much P3 work follows.

### Assumption
A meaningful fraction of the nine classify convex (several are textbook convex problems — `jbearing`, `minsurf`, `torsion` are COPS-style convex QPs; the LPs are convex by type), and `scripts/gamslib/verify_convexity.py` classifies each without error under the license.

### Research Questions
1. What does the verifier return for each of the nine, licensed?
2. Do the LP models classify `verified_convex` automatically (as other LPs in the corpus did)?
3. Does any NLP classify `non_convex` or `error` for a reason other than the license?
4. How long does each convexity solve take at full size?
5. Does the verifier write anywhere persistent during the run? *(At `912d005c`: only `catalog.json`, and only with `--update-catalog`; it never writes `gamslib_status.json` — see Unknown 3.3 for the application step P3 will need.)*

### How to Verify
`verify_convexity.py` has **no status-DB interface**: it reads `data/gamslib/catalog.json`, writes results to `--output <json>`, and touches `catalog.json` **only** with `--update-catalog` (verified at `912d005c`: `CATALOG_PATH` L25, `--output` / `--update-catalog` in its argument parser). Run it **output-only — `--model <id> --output <scratch>.json`, never `--update-catalog`** — in a throwaway worktree, licensed; record status, objective and time from the output JSON. `verify_convexity.py` cannot supply provenance itself: `verify_model` writes its listing to `output.lst` inside a `tempfile.TemporaryDirectory` that is deleted on return, and its `--output` JSON (`VerificationResult.to_dict()`) carries a numeric `solver_status` but **no solver name and no edition** (verified at `912d005c`) — so **Provenance from the verifier's OWN listing — never a rerun** (a second GAMS invocation cannot prove which edition or solver produced the JSON): in the throwaway worktree, apply the **retention patch** (`docs/planning/EPIC_4/SPRINT_40/artifacts/RETENTION_PATCH.md`), which wraps `verify_model`'s `TemporaryDirectory` so its own `output.lst` is copied out on **every** return path (normal, timeout, error) and records the exact command **before** launch. Read the **edition classification** (Task 3's regex) and the **solver actually used** (the `SOLVER … FROM LINE` line — for the QCP `emfl`, whatever QCP selects) from that retained listing; commit only those two values. A model with no licensed retained listing has no recorded result. Applying any result to `gamslib_status.json` is a **separate, explicit step** (none exists today — the DB's convexity block came from the one-time `migrate_catalog.py`), which Unknown 3.3 governs.

### Risk if Wrong
- **P3 over- or under-sized**; a corpus decision posed for the wrong number of models.

### Estimated Research Time
1.5 hours (9 licensed convexity runs, recording)

### Owner
Sprint 40 prep team

### Verification Results
✅ **Status:** VERIFIED — **all nine classify convex** under the licensed verifier: **5 `verified_convex`** (the LPs) and **4 `likely_convex`** (`emfl`, `jbearing`, `minsurf`, `torsion`), each without error.

**Verified by:** Sprint 40 Prep Task 7 · **Date:** 2026-10-14 · **Measured at:** `79eeccff` (all 53 retained invocations; descends from Task 6's answers commit `b44344a2`)

**Findings:**
- **Q1:** see `COHORT_DRY_RUN.md` §Convexity (classification, model status, objective, solver).
- **Q2:** yes. The five LPs (`airsp`, `airsp2`, `indus89`, `msm`, `phosdis`) are `verified_convex`.
- **Q3:** none classifies `non_convex` or `error`.
  - ⚠ **Four are multi-solve**, and the verifier reads the **last** status: `airsp` 3, `airsp2` 6, `msm` 5, `phosdis` 7 `SOLVE` summaries.
  - **`airsp2`'s classification and objective come from a `DECISM` solve**, not from the requested `LP=CPLEX`.
  - Routed to P3, before W10 applies them.
- **Q4:** every convexity solve took **≤ 7 s** (22 s total), inside the verifier's 60 s default.
- **Q5:** **output-only.** `catalog.json` was unchanged afterwards, and no `gamslib_status.json` was written. Edition and solver come from each run's own retained listing: all `licensed`; CPLEX for the LPs, plus DECISM in `airsp2`; CONOPT for the NLPs and for the QCP `emfl`.

**Evidence:** `COHORT_DRY_RUN.md` §Convexity.

**Decision:** under Task 6 Decision 2 (admit by rule), **all nine are admitted** and the expanded corpus would be **151**. But **five cannot yet reach an MCP** (2 translate timeouts, 3 parse failures). P3 applies the admissions through W10, after settling the multi-solve reference question.

---

## Unknown 3.3: Can the corpus grow BEFORE the owner decides — and can the floor/corpus rules be written without knowing any result?

### Priority
**Critical** — `kpi_block.py` (line 112) and `batch_parse.get_candidate_models` both select candidates by `convexity.status ∈ {verified_convex, likely_convex}`. **The 142 denominator is derived, not fixed.** A licensed convexity run that writes a convex status for any NLP-gated model therefore grows the corpus silently — before the owner's corpus-entry decision, and before any footnote. Separately, the floor-provenance rule for license-unlocked matches must be decided before results exist (Sprint 39 P1's lesson).

### Assumption
(a) P3's convexity writes can be held out of the candidate population until the owner decides (a scratch DB, a status that is not in `CONVEX_STATUSES`, or an explicit gate); (b) the floor-provenance and corpus-entry rules can be stated as decision options without citing any cohort result.

### Research Questions
1. Which code paths select the candidate corpus by convexity status (`kpi_block.py`, `batch_parse.py`, `run_full_test.py`, `check_doc_figures.py`'s facts, `floor_tracker.py`)?
2. Does writing `verified_convex` for, say, `torsion` change `kpi_block.py`'s "convex candidates" from 142 to 143 on the next run? (Positive control on a scratch DB.)
3. What mechanism keeps an un-adopted model out — a holding status, a scope list, or never writing to the committed DB until the decision? **And what step would write a licensed convexity result into `gamslib_status.json` at all?** `verify_convexity.py` writes only `--output` JSON or (with `--update-catalog`) `catalog.json`; the DB's convexity block came from the one-time `migrate_catalog.py` — so P3 needs an explicit application step, and that step is where the hold must live.
4. What are the options for classifying a license-unlocked cold match in `data/floor_provenance.json` (new `limb`, or exclusion), and what does each do to `floor_tracker.py`?
5. Can the owner's three answers be committed before the dry run **provably from history** — the answers commit an ancestor of `COHORT_DRY_RUN.md`'s first commit, not merely the brief's creation earlier in time?

### How to Verify
On a scratch copy of the DB, set one NLP-gated model's `convexity.status` to `verified_convex` and run `kpi_block.py --db <scratch copy>` against it: the candidate count must move (the positive control for the silent-growth claim). Grep every reader of `CONVEX_STATUSES` / the candidate predicate. Draft the brief's options and confirm none cites a result.

### Risk if Wrong
- **The headline denominator moves without a decision or a footnote** — percentages silently re-based, the exact thing the S23–S25 scope footnotes exist to prevent.
- **A floor rule fitted to the results** — a favourable classification self-approved at scale.

### Estimated Research Time
1.0 hour (reader grep, scratch-DB positive control, option drafting)

### Owner
Sprint 40 prep team (decisions: project owner)

### Verification Results
✅ **Status:** VERIFIED — **the corpus can grow silently** (positive control: one convex status on a scratch DB moves `kpi_block`'s candidates 142 → 143 and adds the model to the pipeline's run set), **and it can be held**: the hold lives at the single writer that would apply licensed convexity results. Both rules were written, and the owner's three answers taken, before any cohort result exists.

**Verified by:** Sprint 40 Prep Task 6 · **Date:** 2026-10-14 · **Measured at:** `028dc665`

**Findings:**
- **Q1, readers of the candidate predicate** (`grep -rnE "verified_convex|likely_convex|CONVEX_STATUSES" scripts/ src/`):
  - `kpi_block.py:45,112` (every headline denominator);
  - `check_doc_figures.py`, via `compute_kpis`;
  - `run_full_test.py::get_candidate_models` (**what the pipeline runs**);
  - `batch_parse.py::get_candidate_models`;
  - `floor_tracker.py` (advisory mechanical count only).
- **Q2, positive control** on a scratch copy outside the repo, setting `torsion` (`error` today) to `verified_convex`:
  - `kpi_block --db` candidates **142 → 143**;
  - `run_full_test`'s set 142 → 143, now including torsion;
  - `batch_parse` 140 → 141;
  - copy deleted, `data/` clean.
- **Q3, hold mechanism:**
  - Nothing writes verifier output to the live DB today. The first writer will be Task 5's W10 (`apply_convexity_results.py`), which **refuses** a model entering the convex set unless it is `--admit`ted.
  - Held models are evaluated in a **throwaway worktree**: `run_full_test.py` has no `--db` flag, and `--model` filters *within* the candidates, so a held model cannot run against the committed DB at all.
  - A holding status was rejected: it would need a schema enum change and a re-audit of every reader.
- **Q4, floor options:** `floor = baseline + len(entries)`, so **every entry counts +1 whatever its limb**. A non-counting option therefore needs a separate list, not a new limb. Read literally, the current definition **admits** a license-unlocked cold match, so excluding one means amending it.
- **Q5, provable from history:** the answers are committed in this task's commit, before `COHORT_DRY_RUN.md` exists. The PREP_PLAN *Verification* check was **exercised on a scratch clone**:
  - **pass:** the branch as is, and answers → measurement → dry run;
  - **fail, correctly:** a rewording after the dry run, an answer changed in the dry run's own commit, and a measurement SHA predating the answers;
  - **a stray fourth answer outside the blocks initially *passed*.** `valid()` checked only the last decision-changing commit; it now also checks the current brief, and that case fails.
- **Side finding, routed to Task 12:**
  - `danwolfe` and `decomp` are `pipeline_status: skipped` **and** convex: counted in `kpi_block`'s 142, skipped by `batch_parse` (140), and described as excluded by `PROJECT_PLAN.md` footnote ⁴.
  - The two `get_candidate_models` disagree.

**Evidence:** `OWNER_DECISION_BRIEF.md` §1 (reader table, positive control, hold mechanism) and the three `## Decision` blocks with dated owner answers.

**Decision (owner, 2026-10-14):**
- **Floor: B.** A separate, non-counting `license_unlocked` ledger, with the fail-before sub-rule.
- **Corpus: A.** Admit by rule (the licensed verifier's convex classification), with both denominators in one sentence.
- **CI: B.** Hosted CI gated on GAMS confirming a CI-usable license; `gams-licensed` `main`-only with no required reviewers; REPLAN to local-only if GAMS declines.
- **Routed to Sprint 40:**
  - P1: the `floor_tracker` ledger, `corpus_admissions.json` + `kpi_block --corpus`, and the CI half once GAMS answers;
  - P3: W10's `--admit` from the rule;
  - Task 12: the danwolfe/decomp consistency check.

---

# Category 4: P10 — the Six P2-Flagged Models, Class A First

## Unknown 4.1: Is turkpow's alias-minting site still `t__kkt1` substituted into both coordinates of `vs(t,v)`, and in which LAYER?

### Priority
**High** — turkpow is "first" because its site is named. If the name is stale or the layer is wrong (three of four S38 gates were), P4's first fix starts with a re-diagnosis.

### Assumption
The three turkpow fingerprints in `../SPRINT_39/P2_VIOLATION_TRIAGE.md` share one minting site — an alias `t__kkt1` substituted into both coordinates of `vs(t,v)` — located in the KKT/stationarity layer, and fixing it lowers the P2 ratchet from **9** to **6**.

### Research Questions
1. Does `make check-index-repeats` still report 9 = baseline 9 at HEAD, with turkpow ×3 among them?
2. Which function mints `t__kkt1` and substitutes it into both coordinates?
3. Is the layer KKT (`stationarity.py`), AD, or emit — traced from the emitted reference backwards, not assumed?
4. Do all three fingerprints share the site, or does one have its own?
5. Does turkpow have any solve to check against (it is `path_syntax_error` today), or is property-and-golden the only route?

### How to Verify
Run the ratchet; grep the turkpow golden for the violating references; instrument the substitution (a spy recording call sites when `t__kkt1` is produced), with a positive control that the spy fires on a known alias case.

### Risk if Wrong
- **P4's first fix re-diagnosed on a sprint day**, and the ratchet target (≤ 6) wrong.

### Estimated Research Time
1.5 hours (ratchet run, trace, spy with control)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

**Contribution from Task 2 (2026-10-13, `366e91f3`) — status left to Task 10:** `make check-index-repeats` reports **P2: 9 violations across 6 models; baseline 9** (P1: 0 in 3,109 heads). Per model from `index_repeat_p2_baseline.json`: **turkpow ×3**, nonsharp ×2, dinam, egypt, gussrisk, shale ×1 each. The minting site and its layer remain Task 10's. See `BASELINE_RECONFIRMATION.md` §6.

---

## Unknown 4.2: Does the Class-A fingerprint explain egypt's and shale's licensed mismatch, or is there a second defect underneath?

### Priority
**Medium** — P2 gives egypt and shale their first solve, which P4 needs to verify Class-A fixes. If their mismatch has another cause, a Class-A fix will not make them match, and the "verification" route gained from the license is weaker than planned.

### Assumption
egypt's `tranc(rp,rp)` wrong lookup and shale's `ts(tf,tf)` identically-false guard (both live P2 violations, S39 Unknown 6.2) are the dominant cause of each model's mismatch.

### Research Questions
1. What do egypt and shale return in the dry run — outcome, objective vs. NLP, residual verdict?
2. Does `kkt_residual.py`'s top residual row sit on the equation the Class-A reference feeds?
3. Does hand-correcting the one reference in a scratch copy of the golden move the result toward the NLP objective?
4. Is either model's failure a size/solve effect (iteration limit, PATH stall) rather than an emit effect?

### How to Verify
Using Task 7's results: read the residual's top rows; patch the single violating reference by hand in a scratch copy and re-solve (the experiment that discriminates "this defect" from "another defect").

### Risk if Wrong
- **A Class-A fix landed and "verified" against a model that still mismatches for another reason** — inconclusive evidence booked as evidence.

### Estimated Research Time
1.0 hour (residual read, two hand-patched re-solves)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Is the declaration-vs-assignment context Class B needs available in the IR, or only in the source text?

### Priority
**Medium** — Class B (gussrisk, nonsharp ×1, shale-origin) is scheduled as *design, implement only if budget remains*. Whether the needed distinction exists in the IR decides whether the design is small or a parser change.

### Assumption
The IR records whether a repeated-symbol domain comes from a **declaration** (the full product, legal) or is consumed in an **assignment/guard** context (where GAMS reads the diagonal), so an emit-time rule can distinguish them.

### Research Questions
1. Where does the IR store a symbol's declared domain vs. the indices used at a reference site?
2. Does anything in the emit path know, at the point of reusing a domain, that it came from a declaration?
3. Would the distinction require a parser change, an IR field, or only an emit-time check?
4. Does nonsharp's Class-B reference interact with its Class-A one (carryforward §1: one reference of each class)?

### How to Verify
Trace gussrisk's flagged reference from the parser through the IR to emit, recording what context each layer carries; write the minimal rule and check it against the three Class-B fingerprints on paper.

### Risk if Wrong
- **Class B scoped as design-only when it is cheap**, or attempted mid-sprint when it needs a parser change.

### Estimated Research Time
1.0 hour (trace, rule sketch)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: lnts — Re-Apply the BANKED Diff Behind a Phase-0 Gate

## Unknown 5.1: Is the banked diff LANDABLE at all — or does Sprint 39 Day 5's REPLAN already refute "re-apply it behind a gate"?

### Priority
**Critical** — P5 is planned as *"author the Phase-0 gate first, with the fail-before, then re-apply the banked diff"* for **+1 Solve → 112**. But the Day-5 log records that the candidate **failed its pre-registered PROCEED signal on substance** — not merely for lacking a fail-before. A gate cannot make a non-general fix general.

### Assumption
The Day-5 failure was procedural (no fail-before the leak gate could hold), so authoring the gate and re-applying the diff delivers the +1.

### Research Questions
1. Which of the four PROCEED conditions failed on Day 5, and on what evidence? (`_fx_` rows did not bind — `y2.h50` = 4.8997, `y3.h50` = 41.9700, both `INFES`; `robot` and `springchain` drifted.)
2. Is the exclusion **label-enumerated** (`sameas(c,'y2') and sameas(h,'h50')`), which Day 5 classified as "not a general fix"?
3. Does any of those failures depend on the gate's absence — or would each recur identically with a gate in place?
4. Does the runtime bound probe still reproduce the contradiction on `main` (the positive control that the defect is still there)?
5. What is the honest projection for P5: +1, +0 with a banked mechanism, or "landable only via a different fix" (Unknown 5.2)?

### How to Verify
Re-read `../SPRINT_39/SPRINT_LOG.md` §Day 4–5 and `docs/issues/ISSUE_1694_lnts-contradictory-fx-mechanisms-blanket-zeroing.md`; list each failed condition with its evidence and whether a gate changes it. Re-run the bound probe from `../SPRINT_39/LNTS_PROBE_DESIGN.md` on `main`.

### Risk if Wrong
- **P5's 6–10 h spent re-discovering Day 5's REPLAN**, and a +1 Solve projected that cannot arrive — a phantom upside in the acceptance criteria.

### Estimated Research Time
1.5 hours (log + issue read, probe re-run, verdict)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Can the pruning guard be expressed SYMBOLICALLY (an `ord`/`card` runtime property) at `emit_gams.py` section 1b, with no model's labels in the emit?

### Priority
**High** — Day 5 named this as the open problem for a landable fix. If it is expressible, P5 has a real path (re-estimated); if not, lnts is banked again and its budget freed.

### Assumption
"The pruning guard actually covers the fixed tuple" can be written as a runtime condition over `ord`/`card` (or an existing emitted set), so the suppression and the blanket key on the **same** condition instead of two different ones (`kkt.stationarity_conditions` vs `infer_lead_lag_condition`).

### Research Questions
1. What exactly do the two conditions test, and on which tuples do they disagree for lnts?
2. Is there an emitted set or parameter that already represents "the fixed tuples", which the guard could reference?
3. Would a symbolic guard change the emit of `robot`, `springchain` or `otpop` (the Day-5 perturbation list)?
4. Does it generalise to the five other models that match the source pattern?

### How to Verify
Sketch the guard against Day 4's traced section-1b code; apply it in a scratch branch to lnts and the Day-5 perturbation list and diff the emits — **do not land**. Positive control: the label-enumerated Day-5 guard must show up as different from the symbolic one on at least one model.

### Risk if Wrong
- **A sprint day spent discovering the guard is inexpressible**, or a symbolic guard landed that perturbs the negative controls.

### Estimated Research Time
1.5 hours (condition analysis, sketch, scratch diffs)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Even with the contradiction removed, does lnts reach +1 Solve — or does its SECOND (dynamics) defect still stop it, and was `robot`'s drift harmful?

### Priority
**High** — Day 5 recorded that removing the contradiction is **not sufficient**: lnts then fails on its own dynamics (**364 `INFES` rows**: `velo1_eqn`, `tf_eqn`, `stat_step`; `tf - 50*step =E= 0` at LHS −1). If that defect is out of P5's scope, P5 cannot deliver +1 regardless of 5.1/5.2.

### Assumption
The second defect is either small enough to fold into P5 or is a separate issue whose existence removes the +1 from this sprint's projection.

### Research Questions
1. What is the second defect's mechanism — emit, KKT, or the model's own dynamics under the MCP reformulation?
2. Is it tracked by any issue, or does it need one?
3. `robot` drifted under the Day-5 candidate and is in the MCP-gated cohort: under the license, does `robot`'s baseline solve match, and did the drift change that?
4. Did `springchain`'s behaviour-identical drift (MS-1, 289 iters, obj −185.4461) count as "perturbed" under the pre-registered criterion — and should the criterion change?

### How to Verify
Reproduce the 364-row `INFES` state from Day 5's candidate in a scratch branch; read the top rows' residuals. Take `robot`'s licensed **baseline from Task 7's dry run** (not a new solve — `robot` is a cohort member, readable only after Task 6's answers are committed), solve the **Day-5 candidate emit** licensed, and compare.

### Risk if Wrong
- **+1 Solve projected for a model that needs two fixes**, one unscoped.

### Estimated Research Time
1.0 hour (reproduction, one candidate-emit robot solve against Task 7's baseline)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: sarf #1385 — the O(active) Re-Architecture at the Jacobian

## Unknown 6.1: Is 70.9 % of sarf's wall-clock still in `compute_constraint_jacobian` at HEAD — and WHERE inside it?

### Priority
**Critical** — P6 (20–28 h) is the sprint's only planned Translate mover. Its design depends on a breakdown *inside* `compute_constraint_jacobian` (`src/ad/constraint_jacobian.py:828`) that has never been measured; Sprint 39's Task 6 already refuted one sarf cost premise (the four call sites were 0.5 %).

### Assumption
At HEAD, ~70.9 % of sarf's wall-clock is in `compute_constraint_jacobian`, concentrated in identifiable loops that iterate the full rather than the active set.

### Research Questions
1. Does a time-boxed profile at HEAD reproduce ~70.9 % inclusive in `compute_constraint_jacobian`?
2. Which callees dominate inside it (`_substitute_indices`, `_diff_sum`, index enumeration, expression copying)?
3. Which of them iterate the declared set rather than the active (referenced) instances?
4. Has anything landed since Sprint 39 (the #1737/#1741 guards are in this file's neighbourhood) that changed the profile?
5. Does the profile differ between the first minutes and later (warm-up vs. steady state)?

### How to Verify
Profile sarf with a hard time box (e.g. 10 minutes under `cProfile`/`py-spy`), at a stated commit; compare cumulative shares to Sprint 39's attribution; drill into the top callees. Positive control: the profiler attributes time to a deliberately inserted sleep in a known function.

### Risk if Wrong
- **A re-architecture of the wrong loop** — the S39 Task-6 pattern a second time, at 20–28 h instead of prep cost.

### Estimated Research Time
1.5 hours (time-boxed profiles, drill-down)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Can a non-sarf fixture reproduce the shape, so the re-architecture has a fail-before that terminates?

### Priority
**High** — sarf cannot be its own fail-before (369,024 declared columns; the fail-before state does not terminate), and three of four Day-7 defects produced a **wrong answer rather than a crash**. Without a terminating fixture, correctness cannot be gated.

### Assumption
A smaller model — synthetic, or a corpus model sharing sarf's sparse-active-set shape — exercises the same Jacobian path, terminates before and after, and shows a measurable O(declared) vs O(active) difference.

### Research Questions
1. Which structural property makes sarf expensive (declared columns ≫ active instances)?
2. Does any corpus model share it at a terminating size?
3. Can a synthetic generator scale it so the before/after cost ratio is visible at seconds-scale?
4. Does the fixture's emit stay byte-identical across the change (correctness) while its time drops (performance)?

### How to Verify
Build or select the fixture; **hold the active (referenced) set fixed and scale only the declared cardinality** across at least three sizes, recording translate time **and a work count** (e.g. `differentiate_expr` calls); the positive control is that work grows with **declared** size while the active set does not change — **linear growth is the expected signature**, not super-linear, since the documented bottleneck is O(declared) per row (`../SPRINT_38/SARF_REARCH_DESIGN.md`: differentiation volume "directly proportional to declared columns"; `../SPRINT_38/DAY7_SARF_GATE_P6C.md`: "O(declared) per row"). After the O(active) change the same sweep should be ~flat in declared size. Record its golden.

### Risk if Wrong
- **P6 landed on inspection** — the approach Sprint 38 Day 7 showed produces wrong answers.

### Estimated Research Time
1.0 hour (selection or generator, a ≥3-size declared-cardinality sweep with the active set fixed)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Is `gradient.py:453` still dead, and does the atomicity boundary fit in one commit?

### Priority
**Low** — housekeeping that bounds the change: dead code should not be re-architected, and the atomicity boundary sets the commit structure.

### Assumption
`src/ad/gradient.py:453` is unreachable for every corpus model (as Sprint 39 measured), and the O(active) change can land as one commit without leaving an inconsistent intermediate state.

### Research Questions
1. Is line 453 still the same code, and is it still never executed in a full-corpus emit (coverage)?
2. Which functions must change together for the MCP to stay consistent?
3. Can the change be staged behind a flag instead, to split the commit safely?

### How to Verify
Coverage run over the leak-gate corpus for `gradient.py`; read the call graph of the Unknown-6.1 hot loops.

### Risk if Wrong
- **Effort spent on dead code**, or a split commit that leaves `main` inconsistent between merges.

### Estimated Research Time
0.5 hours (coverage read, call graph)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: The Pre-Existing Diagonal-Reference Defect

## Unknown 7.1: Does `stat_tsam(i,j).. 1 =E= 0;` reproduce on `main` from a minimal model, and is the multiplier term really DROPPED rather than legitimately zero?

### Priority
**High** — the defect was found incidentally while instrumenting #1741 (carryforward §5) and has no issue yet. An emitted `1 =E= 0` is infeasible by construction; if it is real, any corpus model with the shape has an MCP that cannot solve.

### Assumption
A model with `diagsum(j).. sum(i, tsam(i,i)) =E= ...` emits `stat_tsam(i,j).. 1 =E= 0;` on `main`, because the multiplier term for the diagonal reference is dropped — not because the stationarity row is correctly trivial.

### Research Questions
1. Does the minimal model reproduce the emitted line on current `main`?
2. What should the correct stationarity row be (hand-derived KKT)?
3. Does any corpus golden contain a `1 =E= 0`-shaped stationarity row (grep)?
4. Is B-3 really called 0× for it (unrelated to the S39 guards)?

### How to Verify
Write the minimal model; translate on `main`; hand-derive the expected row; grep the goldens for constant-only stationarity equations (`stat_\w+\(.*\)\.\.\s*-?\d+\s*=E=\s*0`). File the issue with the reproducer.

### Risk if Wrong
- **An unfiled correctness defect in live goldens**, or a fix aimed at a row that was correctly trivial.

### Estimated Research Time
1.0 hour (reproducer, hand derivation, corpus grep, issue)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Is the layer `_diff_sum`'s diagonal handling — or somewhere else?

### Priority
**Medium** — the carryforward says *"probably `_diff_sum`'s diagonal handling, but trace before naming"*. Three of four S38 gates named the wrong layer; the P10b positive-control field and the S39 layer field both exist because of that.

### Assumption
The term is dropped in `_diff_sum` when the summed reference is a diagonal (`tsam(i,i)`) and the differentiation variable's indices do not align.

### Research Questions
1. Does the derivative of `sum(i, tsam(i,i))` w.r.t. `tsam(i,j)` come out zero at the AD layer, or is it correct there and lost at emit?
2. If AD: is it `_diff_sum`, the index-matching it calls, or `_substitute_indices`?
3. Does the #1737 refusal path interact (it detects empty instances for repeated *equation* domains)?

### How to Verify
Instrument the AD output for the minimal model (print the derivative expression before emit); if non-zero, bisect through the KKT and emit layers. Record the layer with a one-line justification.

### Risk if Wrong
- **A Phase-0 gate naming the wrong layer** — the S38 failure, a fourth time.

### Estimated Research Time
1.0 hour (AD instrumentation, bisect)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 8: Positional-Domain Follow-Ons

## Unknown 8.1: Does ANY input discriminate `_match_subset_domain` and `_compute_index_offset_key` with their consume-once guards disabled — or are the guards dead code?

### Priority
**Medium** — a nine-shape probe produced byte-identical results with the guards disabled (carryforward §6). Either a discriminating input exists (and becomes a behavioural pin) or the guards are dead at the shapes the corpus uses — a different finding with a different follow-up.

### Assumption
A discriminating input exists at ≥ 3-D or with nested subsets, beyond the 2-D shapes already probed.

### Research Questions
1. Which inputs did the nine-shape probe cover (dimension, subset nesting, offsets)?
2. Does a 3-D repeated-symbol domain, a subset-of-subset, or a domain with an `IndexOffset` make the guarded and unguarded paths differ?
3. Does any corpus model contain such a shape (so the guard is live in practice)?
4. If none discriminates, what is the proof scope of "dead" (shapes tried, corpus scanned)?

### How to Verify
Extend the probe in `tests/unit/kkt/test_positional_domain_sites.py`'s style; for each new shape, compare emits with guards enabled/disabled. Positive control: a deliberately broken guard (wrong index) must change the emit on at least one shape, proving the probe can see a difference.

### Risk if Wrong
- **Guards kept as "protection" that protects nothing**, or removed when a corpus shape needed them.

### Estimated Research Time
1.5 hours (shape construction, paired emits, corpus scan)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.2: Does any planned Sprint-40 change route through #1737's refusal, so that a fix elsewhere could narrow it?

### Priority
**Low** — #1737 is load-bearing for the AD layer (carryforward §4: `_substitute_indices` computes a wrong off-diagonal Jacobian for a repeated domain, and only `detect_empty_equation_instances`' refusal stops it escaping). A Sprint-40 change that alters which equations reach the detector could narrow the refusal unknowingly.

### Assumption
None of P4 (Class-A fixes), P6 (Jacobian re-arch) or P7 (diagonal defect) changes the inputs that reach `src/kkt/empty_equation_detector.py`'s #1737 path.

### Research Questions
1. Which functions does each planned change touch, and do any feed the detector?
2. Does `test_the_AD_collapse_is_reachable_but_EMIT_refuses_it` still pass, and does it pin the refusal by the detector's context string?
3. Would P6's O(active) change alter what `_substitute_indices` receives?

### How to Verify
Map each planned change's touch set (from Tasks 9 and 10) against the detector's callers; run the pinning test.

### Risk if Wrong
- **A wrong Jacobian escapes** because a refactor narrowed the only thing refusing it, with every test green.

### Estimated Research Time
0.5 hours (touch-set mapping, test run)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 9: The Smaller Items

## Unknown 9.1: Would reclassifying the 7 `model_infeasible` comparisons from `skipped` to `mismatch` move any reported figure?

### Priority
**Medium** — carryforward §7 marks this **KPI-visible** and forbids folding it into a review fix. Whether it moves Match, all-219 Match, a denominator, or only a label decides whether it needs a full Phase-0 doc or a note.

### Assumption
The change affects only `compare_solutions`' Case 6 label (`skipped`/`compare_mcp_failed` → `mismatch`), and no headline KPI (Match counts only `match`) changes.

### Research Questions
1. Which of `kpi_block.py`'s quantities read the comparison label, and do any count `mismatch` or `skipped`?
2. Does any report (`SUMMARY.md`, the dashboard, `check_doc_figures.py` facts) count mismatches?
3. Are the 7 models the same 7 at HEAD (derived by identity)?
4. Would the change alter any CI gate's input (e.g. presolve divergence keyed on comparison status)?

### How to Verify
Grep every reader of the comparison status; on a scratch DB, apply the relabel to the 7 rows and diff `kpi_block.py`'s output before/after.

### Risk if Wrong
- **A KPI moved by a "cosmetic" change**, reported as a regression or an improvement it is not.

### Estimated Research Time
1.0 hour (reader grep, scratch-DB diff)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 9.2: Are the remaining small items still exactly as the carryforward describes them?

### Priority
**Low** — they are P9's schedule filler, which only works if each is small, known and still present.

### Assumption
(a) `scripts/integration_health_check.py` still fails from an uninstalled checkout (six module-level `src` imports, no `sys.path` bootstrap); (b) `kpi_block.py` still carries the `all_219_match` key; (c) the ganges embedded-NLP-diverges blocker (#1378/#1424 class) still has no issue of its own while #1667 and #929/#930 stay OPEN; (d) GitHub #1668 is still OPEN despite both its directions being closed on measurement (S39 Unknown 10.2's recommended follow-up).

### Research Questions
1. Does `python -S scripts/integration_health_check.py` fail as described?
2. Is `all_219_match` still a key, and who reads it?
3. Has anyone filed the ganges embedded-NLP-diverges issue since the carryforward — in **any** state (`gh issue list` defaults to open-only, so a closed filing would be missed and duplicated)?
4. Is #1668 still OPEN?

### How to Verify
Run the health check without the package installed; grep `kpi_block.py`; `gh issue list --state all --search ganges`; `gh issue view 1668`.

### Risk if Wrong
- **Filler that is not filler** — an item already done, or larger than described, on a slack day.

### Estimated Research Time
0.5 hours (four quick checks)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 10: Infrastructure — the Sprint-39 Retrospective's Process Changes as Mechanisms

## Unknown 10.1: Can the anchor resolver be extracted from `test_positional_domain_sites.py` into a shared helper WITHOUT changing what it resolves?

### Priority
**Medium** — P10a's mechanism (S39 §7.3: "anchors are code, scoped, nested-aware, unique — reuse the resolver"). An extraction that subtly changes resolution would weaken every structural pin that depends on it, silently.

### Assumption
The resolver is self-contained, its behaviour is fully exercised by the current tests, and moving it to a shared helper is a pure refactor.

### Research Questions
1. What does the resolver depend on (module globals, fixtures, file paths)?
2. Which tests use it, and do they cover its uniqueness and nesting checks with a negative case?
3. Is there a second, weaker resolver elsewhere that should migrate to it?
4. Does the extracted helper produce identical anchors for all 16 pinned sites?

### How to Verify
List call sites; extract in a scratch branch; run the module's tests; compare the resolved anchors for all 16 sites before/after. Positive control: a deliberately ambiguous anchor must still be refused after extraction.

### Risk if Wrong
- **Structural pins that no longer pin**, with the test suite green.

### Estimated Research Time
1.0 hour (dependency read, scratch extraction, comparison)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 10.2: Can `check_phase0_doc.py` require a POSITIVE-CONTROL field without failing every existing Phase-0 doc — and can local `check-goldens` derive `--min-scope` as CI does?

### Priority
**Medium** — P10b and P10c. S39's P8a added a layer field with the same grandfathering problem; P10c closes the "leak gate narrowed silently under contention" hole (carryforward §8.7).

### Assumption
(a) The checker can require the field for docs created after a cutoff, as P8a did for the layer field; (b) the `Makefile`'s `check-goldens` target can pass `--min-scope "$(git ls-files 'data/gamslib/mcp/*.gms' | wc -l)"` the way `golden-staleness.yml` does, and a contention-narrowed run then fails.

### Research Questions
1. How did S39 P8a grandfather existing Phase-0 docs for the layer field — date cutoff, list, or marker?
2. What counts as a positive control in a Phase-0 doc, concretely enough to check mechanically?
3. Does `make check-goldens` lack `--min-scope` today (`Makefile` line 90–91 at `912d005c`)?
4. Does contention actually reduce the *reported* scope count, so `--min-scope` would catch it — or does it cause timeouts that are reported differently?

### How to Verify
Read `check_phase0_doc.py` and `../SPRINT_39/PROCESS_INFRA_SPEC.md`; run the checker against all existing Phase-0 docs with a draft field requirement. For P10c, run the gate with an artificially reduced scope (positive control: it must fail) and read how S39's contention incident was reported in `../SPRINT_39/SPRINT_LOG.md`.

### Risk if Wrong
- **A mechanism that fails every old doc** (and gets disabled), or a min-scope check that misses the failure mode it was added for.

### Estimated Research Time
1.0 hour (checker read, dry run, gate control)

### Owner
Sprint 40 prep team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Template for Adding New Unknowns During the Sprint

Copy this block, renumber within the appropriate category, and add a Table-of-Contents entry if a category is added.

```markdown
## Unknown X.Y: [Question as a single sentence]

### Priority
**[Critical/High/Medium/Low]** — [why this priority; name the rework cost if wrong]

### Assumption
[The specific belief being relied upon, stated so it can be falsified]

### Research Questions
1. [Specific, answerable question]
2. [...]
3. [...]

### How to Verify
[Concrete experiment, command or control — not "investigate". Name the measurement AND its positive control.]

### Risk if Wrong
- **[Failure mode]:** [consequence for the sprint, with an hour cost if known]

### Estimated Research Time
[N] hours ([what the time is spent on])

### Owner
Sprint 40 execution team

### Verification Results
🔍 **Status:** INCOMPLETE
```

**Rules for new unknowns discovered mid-sprint:**
1. **Add it the day it is discovered**, not at close.
2. **State the measurement, not the intent.** "Investigate X" is not a verification method — and a measurement without a positive control is not yet evidence (S39 §7.5).
3. **Record the commit** every result was measured at; re-measure rather than re-quote (S39 §7.1).
4. **Name models, not counts** (S39 §7.2) — especially for either license-gated population.
5. **If it invalidates a prior unknown's result, update that unknown** rather than leaving both, and sweep this document for every sentence that quoted the old result (S39 §7.6).

---

## Next Steps

### Before Sprint 40 Day 1

1. **Prep Task 2** re-derives the baseline and both populations by identity — it owns **3.1** and contributes to **2.1** (size facts) and **4.1** (the ratchet).
2. **Prep Task 3** must land before any license-dependent unknown is answered: **1.1** (the effective license and its per-solver coverage) gates **1.2, 1.5, 2.x, 3.2, 4.2, 5.3**.
3. **Prep Task 6's brief and the owner's three dated answers** must be committed before Task 7 measures anything (the answers commit an ancestor of Task 7's first commit) — it owns **3.3**, whose answer is only valid if written blind.
4. **Every Critical and High unknown (18) must reach ✅ VERIFIED, ❌ WRONG or 🔶 PARTIALLY WRONG before Day 1** — with **one stated exception: Unknown 1.5's universal neutrality claim**, which by construction only the first licensed full run can close; a clean Task-3 sample leaves it at `🔍 INCOMPLETE — sample-neutral at <sha>; routed`, which is a resolution of everything prep *can* establish, not a miss. A Medium or Low may carry with a stated reason and the day that closes it.
5. **Prep Task 12** integrates the results into the schedule — in particular **5.1**'s verdict decides whether P5's +1 Solve stays in the projection.

### Success Criterion for This Document

**Prep should refute something.** Sprint 38 refuted 32 %, Sprint 39 **63 %**. This list has at least three assumptions that the writing of it already put in doubt (1.1, 3.3, 5.1). **A prep phase that confirms everything has probably not looked hard enough.**

### During Sprint 40

- Review at each checkpoint (Day 5, Day 10) and at close
- Add newly discovered unknowns using the Template
- Update Verification Results with implementation findings, including anything that *contradicts* a prep verdict
- At close, the resolution tally feeds `SPRINT_RETROSPECTIVE.md` and `SPRINT_41_CARRYFORWARDS.md`

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns. Task numbers refer to `PREP_PLAN.md`.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Re-Derive the Sprint-39 Baseline & Both License-Gated Populations by Identity | 3.1 | Owns 3.1 (type + license-free parse/translate of the NLP-gated set). **Contributes to** 2.1 (derived cohort sizes) and 4.1 (the P2 ratchet re-derived). License-free, so it does not wait for Task 3. |
| Task 3: Prove the Effective License — Precedence & Per-Solver Fail-Capable Probes | 1.1, 1.2, 1.5 | Owns the local half of Category 1. **1.1 gates every license-dependent unknown.** 1.5's sample re-solve is the first license-neutrality evidence; the sprint's full run is the exhaustive one. |
| Task 4: CI License-Isolation Design & Workflow Inventory | 1.3 | Owns the CI half of Category 1, including the throwaway-repo branch-policy test and the demo-motivated exclusion catalog. |
| Task 5: Schema 3.1.0 `license_edition` Design | 1.4 | Owns the closed writer list. Uses 1.2's discriminating string for the parser extension. |
| Task 6: Owner Decision Brief — Floor Provenance, Corpus Entry & Hosted Runners (written blind) | 3.3 | Owns 3.3, including the scratch-DB positive control for silent corpus growth. **Must be committed before Task 7.** Carries 1.3's license-terms question to the owner. |
| Task 7: License-Gated Cohorts Dry Run — Fingerprints & Routing | 2.1, 2.2, 2.3, 2.4, 3.2 | Owns Category 2 and 3.2. Its results feed 4.2 (egypt/shale) and 5.3 (robot). Never persists to the DB — which is also how it avoids triggering 3.3's silent growth. |
| Task 8: lnts — Is the Banked Diff Landable? Premise Test & Phase-0 Gate | 5.1, 5.2, 5.3 | Owns Category 5. 5.3's `robot` comparison uses Task 7's baseline, so **Task 8 depends on Task 7**. Its verdict decides P5's projection. |
| Task 9: sarf Jacobian O(active) Re-Architecture Design | 6.1, 6.2, 6.3 | Owns Category 6. 6.1 can invalidate P6's 20–28 h estimate, as S39's Task 6 did for the previous premise. |
| Task 10: Correctness-Track Pre-Traces — turkpow Class A, the Diagonal Defect, the Structural Sites | 4.1, 4.2, 4.3, 7.1, 7.2, 8.1, 8.2 | Owns Categories 4, 7 and 8. 4.2 depends on Task 7's egypt/shale results; 8.2 uses Task 9's touch set. The heaviest task by unknown count (7 unknowns, 7.5 h) — Task 12 should check it against the task's 5–7 h estimate. |
| Task 11: Process-Mechanism Spec & Smaller-Items Catalog | 9.1, 9.2, 10.1, 10.2 | Owns Categories 9 and 10. *(Not in the prompt's "Tasks 2–10" range, but it owns four unknowns, so it carries the same metadata.)* |
| Task 12: Plan Sprint 40 Detailed Schedule | *(integrates all)* | Consumes every verified unknown; routes any unresolved one to the sprint day that closes it. |

**Coverage check:** every unknown 1.1–10.2 appears in exactly one task's owned set (Task 2's two *contributions* are in addition to their owners, Tasks 7 and 10). Tasks 2 and 12 are the only tasks that *contribute to* or *integrate* beyond their owned set.

---

## Appendix: Document Cross-References

- **Sprint definition:** `../PROJECT_PLAN.md` → *Sprint 40 (Weeks 45–46)* — goal, ten priorities, deliverables, acceptance criteria, effort, risk
- **Prep tasks:** `PREP_PLAN.md` — the 12 tasks that verify these unknowns
- **Epic goals:** `../GOALS.md` — goal 7 (*Solve Stage: PATH Convergence and Solution Matching*), goal 8 (*Performance, Quality & Release*), External Dependencies (*"GAMS software installed locally (with valid license)"*)
- **Sprint-39 hand-off:** `../SPRINT_39/SPRINT_40_CARRYFORWARDS.md` · `../SPRINT_39/SPRINT_LOG.md` · `../SPRINT_39/SPRINT_RETROSPECTIVE.md` §7
- **Per-category background:** `../SPRINT_39/P2_VIOLATION_TRIAGE.md` (Cat. 4) · `../SPRINT_39/LNTS_PROBE_DESIGN.md` + `docs/issues/ISSUE_1694_lnts-contradictory-fx-mechanisms-blanket-zeroing.md` (Cat. 5) · `../SPRINT_39/SARF_CALLSITE_PLAN.md` + `docs/issues/ISSUE_1385_sarf-symbolic-emit-o-active.md` (Cat. 6) · `../SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` + `docs/issues/ISSUE_1737_repeated-equation-domain-index-collapse.md` (Cat. 7–8) · `../SPRINT_39/PROCESS_INFRA_SPEC.md` (Cat. 10) · `docs/issues/ISSUE_933_tricp-mcp-compilation-errors.md` (2.4)
- **Research documents:** `docs/research/gamslib_kpi_definitions.md` (3.3) · `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` + `docs/research/convexity_detection.md` (3.2) · `docs/research/GAMSLIB_MODEL_TYPES.md` (the Epic-3 catalog that first recorded "License limits (11)") · `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` (1.4) · `docs/research/multidimensional_indexing.md` (8.1)
- **Prior sprint deferred unknowns:** `../SPRINT_39/KNOWN_UNKNOWNS.md` (30 unknowns, all resolved; **6.2** continues here as Category 2; **3.1–3.3** as Category 5; **4.1–4.4** as Category 6; **5.1–5.3** as Categories 7–8; **8.1–8.3** as Category 10; **10.2** closed as unreachable and deliberately not re-asked)

*(No `PRELIMINARY_PLAN.md` exists for Sprint 40.)*
