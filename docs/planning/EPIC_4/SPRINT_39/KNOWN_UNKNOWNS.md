# Sprint 39 Known Unknowns

**Created:** 2026-08-26
**Status:** Active — Pre-Sprint 39
**Purpose:** Proactive documentation of the assumptions and unknowns for Sprint 39 (the Sprint-38 carryforward sprint) **before** implementation begins — so each carryforward is verified in the prep phase rather than discovered on a sprint day.

---

## Executive Summary

This document identifies every open question, assumption and risk across the ten Sprint-39 priorities defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 39, Weeks 43–44).

Sprint 38 closed by **clearing an entire failure category** — `path_solve_terminated` **4 → 0** — taking **Solve 108 → 111** and **Match 94 → 96** through four firm landings, every one leak-gated unqualified. But it handed forward an unusually uncomfortable shape: **two of its four fixes revealed *new* defects underneath them**, and **three of its four Phase-0 gates named the wrong *layer***.

That is the principal risk this document is organised around. Sprint 38's most transferable finding was not about any model — it was that **a gate can be confidently wrong about which layer a defect lives in**, twice by under-scoping (naming `emit_gams.py` for defects decided upstream in AD/KKT) and once by over-scoping (demanding new logic for a diagonal-triviality test that had existed since #942). Sprint 39 carries three tracks whose fix surfaces are *currently hypotheses*, and one (lnts) that has **never been traced at all**.

**Sprint 39 Scope (per `PROJECT_PLAN.md`):**
1. **P1 (Decision)** — the genuine-floor classification: **it blocks the sprint's own baseline**
2. **P2 (Critical)** — dyncge's second emit defect (`CASE_B`): the sprint's only *new* diagnosis
3. **P3 (Critical)** — lnts: hypothesis *and* fix surface untraced
4. **P4 (KPI)** — sarf's four located call sites: **+1 Translate**, the only KPI mover
5. **P5 (Prevention)** — the positional-vs-declared-domain audit
6. **P6 (Date-gated)** — consultation reply integration, or the 2026-09-09 follow-up
7. **P7 (Integrity)** — the presolve-record systemic remedy: all 14 rows or none
8. **P8 (Infrastructure)** — the four Sprint-38 retrospective process findings
9. **P9 (Epic 5)** — the numéraire-selection rule + degeneracy detection, **design only**
10. **P10 (Slack)** — the general emit-backlog sweep

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 39 section — goal, 10 priorities, deliverables, acceptance criteria, effort, risk) · `docs/planning/EPIC_4/SPRINT_39/PREP_PLAN.md` (the 12 prep tasks that verify these unknowns) · `docs/planning/EPIC_4/SPRINT_38/SPRINT_39_CARRYFORWARDS.md` (the eight carryforward sections with bounded next steps) · `docs/planning/EPIC_4/SPRINT_38/SPRINT_RETROSPECTIVE.md` §§2–4, 7 · `docs/planning/EPIC_4/SPRINT_38/SPRINT_LOG.md` (close figures + the three-gate rule applied) · `docs/planning/EPIC_4/GOALS.md` (Epic-4 goals 6, 7, 8). *(No `PRELIMINARY_PLAN.md` exists for Sprint 39; the `PROJECT_PLAN.md` section, the `PREP_PLAN.md` and the carryforwards doc are the planning sources.)*

**Lessons from Previous Sprints:**
- **⚠ Three of four Phase-0 gates named the wrong LAYER** (S38): tricp and elec under-scoped, dyncge over-scoped. The standing rule ("fix surfaces are hypotheses") held but under-describes the failure — the error was not the *line*, it was the *layer*. **Re-trace from `stationarity.py` and the AD entry points outward, not from the emitter inward.**
- **Before writing new emit logic, check whether the logic exists for a different POPULATION** (S38): dyncge's gate demanded new machinery for a test that had existed since #942 and was only ever applied to inequalities.
- **A repeated symbol in a DECLARATION domain is safe until something resolves an index positionally against it** (S38, twice in two days, in two different layers). Neither instance crashed where the defect was.
- **`CASE_B` is a refusal, not a caveat** — it is what stopped dyncge being booked as a Match, and `CASE_A` is what validated elec. **A non-erroring emit is not a pass.**
- **A shared signature is not a shared mechanism** — cesam shows lnts's MS-4-at-iteration-0 signature but has **0 `_fx_` equations**, so lnts's mechanism cannot apply. Checked, not assumed.
- **A long-carried package rots in place** (S38, five carries) — prep re-verified the consultation's *conclusion* and stamped the toolchain, but not its *description*, which had stopped reproducing.
- **A count of findings is a figure — derive it, don't recall it** (S38 Day 13): the closeout claimed a gate mis-traced "three consecutive days"; it was two days and three of four gates, and the retrospective also double-counted one gate. Caught in review.
- **The genuine floor cannot be derived from the DB** — a mechanical `Match − (presolve ∧ match)` count yields **65** and looks authoritative.
- **The control-first REPLAN discipline has held for nine consecutive sprints** — zero broken code across S30–S38.

**Deferred-unknown lineage:** these unknowns descend from Sprint-38 dispositions — the floor question is the S38 **Day-13 close finding** (the tracker says 73, the written definition arguably says 75; S38 close rule #3); dyncge's second defect is the S38 **Day-12 discovery** that the empty-pair abort was *masking* a `CASE_B` residual (`ISSUE_1693` closed on its own terms); lnts is the S38 **Day-12 budget casualty** — never started, never traced; sarf is the S38 **Day-7 gate NOT MET** (28 m 40 s vs ≤300 s, the remaining cost located at four untouched call sites); the positional-domain class is the S38 **retrospective §3** generalisation of tricp (D11) and elec (D12); the presolve-record items are the S38 **Day-10 findings** (weapons spurious, 14 dangling rows), reported and deliberately not corrected; the process findings are the S38 **retrospective §7**; Epic-5 carries from Sprints 32–38 with its BANNED list intact; **Unknown 10.2 re-asks S38's Unknown 1.5**, which closed 🔍 INCOMPLETE because its measurement window required a fix in the tree that P1's REPLAN never produced.

---

## How to Use This Document

### Before Sprint 39 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (19 total)
2. Create minimal test cases / `/tmp` controls for validation (the dyncge and lnts controls are minutes-scale and local; the full-corpus leak run is ~50 min; **the sarf blow-up does not terminate and must be capped**)
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 39
1. Review daily during standup
2. Add newly discovered unknowns (use the Template below)
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption breaks the fix or forces a mid-sprint REPLAN (>8 hours rework)
- **High:** Wrong assumption causes significant rework (4–8 hours)
- **Medium:** Wrong assumption causes minor issues (2–4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 30

**By Priority:**
- Critical: 7 (23% — could derail a track or force a mid-sprint REPLAN: the floor's cold-emit premise, dyncge's reachability and locus, lnts's runtime collision, sarf's site locations and cost attribution, and whether *any* single remedy covers all 14 presolve rows)
- High: 12 (40% — require upfront research or design before Day 1)
- Medium: 8 (27% — resolvable during implementation)
- Low: 3 (10% — nice-to-know, low impact)

**By Category:**
- Category 1 (The Genuine-Floor Classification Decision): 3 unknowns
- Category 2 (dyncge — the Second Emit Defect That the Abort Was Masking): 4 unknowns
- Category 3 (lnts — the Contradictory `.fx` Mechanisms): 3 unknowns
- Category 4 (sarf #1385 — the Four Untouched Call Sites): 4 unknowns
- Category 5 (The Positional-vs-Declared-Domain Audit): 3 unknowns
- Category 6 (Consultation Reply Integration or Follow-Up): 3 unknowns
- Category 7 (The Presolve-Record Systemic Remedy): 3 unknowns
- Category 8 (Infrastructure — the Sprint-38 Retrospective's Four Process Findings): 3 unknowns
- Category 9 (Epic-5 Handoff — the Two Answerable Open Questions): 2 unknowns
- Category 10 (General Emit-Backlog Sweep): 2 unknowns

**Estimated Research Time:** **40.0 hours** — re-derived mechanically on 2026-08-27 by summing the 30 per-unknown estimates. **This exceeds the 28–36 hour target by 4 h.** The previously published figure of 29.0 h was wrong at every commit of this file, despite being labelled as derived. Spread across prep Tasks 2–11 (budgeted 34–47 h), so the prep is only completable near the top of that range.

**By Resolution Status (as of creation, 2026-08-26):**
- ✅ VERIFIED: 0
- ❌ WRONG: 0
- 🔶 PARTIALLY WRONG: 0
- 🔍 INCOMPLETE: 30 — all unknowns open; prep Tasks 2–11 resolve them

---

## Table of Contents

1. [Category 1: The Genuine-Floor Classification Decision](#category-1-the-genuine-floor-classification-decision)
2. [Category 2: dyncge — the Second Emit Defect That the Abort Was Masking](#category-2-dyncge--the-second-emit-defect-that-the-abort-was-masking)
3. [Category 3: lnts — the Contradictory `.fx` Mechanisms](#category-3-lnts--the-contradictory-fx-mechanisms)
4. [Category 4: sarf #1385 — the Four Untouched Call Sites](#category-4-sarf-1385--the-four-untouched-call-sites)
5. [Category 5: The Positional-vs-Declared-Domain Audit](#category-5-the-positional-vs-declared-domain-audit)
6. [Category 6: Consultation Reply Integration or Follow-Up](#category-6-consultation-reply-integration-or-follow-up)
7. [Category 7: The Presolve-Record Systemic Remedy](#category-7-the-presolve-record-systemic-remedy)
8. [Category 8: Infrastructure — the Sprint-38 Retrospective's Four Process Findings](#category-8-infrastructure--the-sprint-38-retrospectives-four-process-findings)
9. [Category 9: Epic-5 Handoff — the Two Answerable Open Questions](#category-9-epic-5-handoff--the-two-answerable-open-questions)
10. [Category 10: General Emit-Backlog Sweep](#category-10-general-emit-backlog-sweep)

---

# Category 1: The Genuine-Floor Classification Decision

## Unknown 1.1: Did twocge's and elec's COLD emits actually change, and is the change substantive?

### Priority
**Critical** — the entire case for floor 75 rests on this. If either cold emit is byte-identical to pre-fix, that model is *methodology* by definition and the decision collapses to "73, and Sprint 38 was right".

### Assumption
Both `data/gamslib/mcp/twocge_mcp.gms` (S38 Day 9, `204f35ac`) and `data/gamslib/mcp/elec_mcp.gms` (S38 Day 12, `82b91c94`) changed in their landing commits, and the changes are **substantive emit differences** rather than comment or whitespace churn.

### Research Questions
1. Do `git show --numstat` on both landing commits show a non-zero diff for the **cold** golden (not the `_presolve` variant)?
2. Is each diff *substantive* — new equations, guards or `.fx` lines — rather than comments, blank lines or reordering?
3. Were both models **aborting before** the fix, so the match cannot be attributed to a solver effect or a v54 upgrade?
4. Does the leak gate's byte-diff independently corroborate the elec change (−12 bytes) and the twocge change?
5. Is either change confined to a `_fx_`-only region that a reviewer might reasonably call a methodology artifact?

### How to Verify
`git show --numstat 204f35ac -- data/gamslib/mcp/twocge_mcp.gms` and `git show --numstat 82b91c94 -- data/gamslib/mcp/elec_mcp.gms`, then read the actual diff hunks. Cross-check each model's pre-fix DB row (`path_solve_terminated`) against its post-fix row to confirm the abort. Compare against the leak-gate byte deltas recorded in the Day-11 and Day-12 docs.

### Risk if Wrong
- **The decision is moot** and Sprint 39 opens on floor 73 with P1 collapsing to a 30-minute write-up — cheap, but the sprint's headline changes.
- **Worse, if only *one* qualifies**, the floor is 74 and neither the "73" nor the "75" framing in the plan is right.

### Estimated Research Time
1.0 hour (two `git show`s, two diff reads, two DB row comparisons)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED — with a distinction the Sprint 38 close did not draw

**Verified by:** Sprint 39 Prep Task 2 · **Date:** 2026-08-27 · **Measured at:** `a8669ad6`

**Findings:** Both cold goldens changed at their landing commits, and both models were `path_solve_terminated` with `solver_version: None` beforehand — aborted before PATH ran — so neither match can be a solver effect. The full-population attribution run independently shows both now produce **their own** `MCP MS-1` rather than reading back the embedded NLP's answer.

**But the two changes are not of the same kind**, which research question 5 asks about directly:

| model | cold diff | what changed |
|---|---|---|
| twocge (`204f35ac`) | +10 / −0 | a comment block plus **two `nu_*.fx(...)` guard lines** — *entirely* within the `_fx_` multiplier-fixing region |
| elec (`82b91c94`) | +3 / −3 | the **stationarity equations themselves** — the always-false `ut(i,i)` guard replaced by `ut(i,j__)`, plus a spurious outer sum removed |

**Evidence:** `git show --numstat 204f35ac -- data/gamslib/mcp/twocge_mcp.gms` → `10 0`; same for elec → `3 3`; hunks read in full. Pre/post DB rows via `git show 204f35ac^:data/gamslib/gamslib_status.json` and `git show 204f35ac:data/gamslib/gamslib_status.json` for twocge, and `git show 82b91c94^:data/gamslib/gamslib_status.json` / `git show 82b91c94:data/gamslib/gamslib_status.json` for elec — each read for that model's `mcp_solve.outcome_category` and `solver_version`.

**Decision:** The assumption holds — both cold emits *did* change substantively. **But the floor is now 73, 74 or 75, not 73-or-75.** The 74 reading (elec qualifies, twocge is a `_fx_`-confined methodology artifact) is live and was not considered at Sprint 38 close. **Routed to Task 3, which owns the decision. Task 2 deliberately does not make it.**

---

## Unknown 1.2: Is there a THIRD model that qualifies under the same reading?

### Priority
**High** — if the test was applied wrongly twice, it may have been applied wrongly before. A third instance changes the decision's *shape* from "add two entries" to "the classification needs re-deriving", which is a materially bigger piece of work.

### Assumption
`twocge` and `elec` are the **only** models whose cold emit changed in a landing sprint and that match today without a provenance entry. The baseline of 73 is otherwise correctly constituted.

### Research Questions
1. Across the provenance baseline period, which models' **cold** goldens changed in a landing commit?
2. Of those, which match today?
3. Of those, which have **no** provenance entry and were classified methodology?
4. Does `polygon` — the precedent the definition names — itself have an entry, or is it counted inside the opaque baseline?
5. Is the baseline's opacity (`"per-model records for the opaque 'S28 genuine' block"`) hiding models that would answer this question?

### How to Verify
Walk `git log --follow` over `data/gamslib/mcp/*_mcp.gms` for the baseline period, intersect with today's matching models, and subtract the provenance entries. Where the baseline is opaque, say so explicitly rather than guessing — **the file's own README states the floor cannot be RECONSTRUCTED, only accumulated.**

### Risk if Wrong
- **A third instance means the decision is not "two entries"** but a re-derivation, which the provenance file's design explicitly says is impossible — that would be a genuine methodological problem needing the owner, not a bookkeeping fix.
- **Scope creep into P1's 4–6h budget**, which is sized for a decision package, not an audit.

### Estimated Research Time
1.5 hours (git walk, intersection, provenance diff)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED — no third model, with one conditional

**Verified by:** Sprint 39 Prep Task 3 · **Date:** 2026-08-29 · **Measured at:** `8a5a88bc`

**Findings:** Swept every **cold** golden (`*_mcp.gms`, excluding `_presolve`) changed between the baseline anchor `8cffec29` (S37-close) and `9ab2c0c3` (S38-close) — the only window the opaque baseline does not already absorb. **Five** changed; only **two** match today:

| model | pre-fix | today | qualifies |
|---|---|---|---|
| twocge | `path_solve_terminated` | presolve + match | candidate |
| elec | `path_solve_terminated` | presolve + match | candidate |
| dyncge | `path_solve_terminated` | `model_optimal` + **mismatch** | ✗ (the `CASE_B` defect) |
| tricp | `path_solve_terminated` | `path_solve_license` | ✗ **today** |
| ferts | `path_solve_license` | `path_solve_license` | ✗ untestable throughout |

**⚠ `tricp` is a conditional future candidate** — cold emit changed, abort removed, blocked only by **capacity** (387 → 1,255 rows, past the demo limit). If the #1462 licence ask succeeds and tricp matches, it qualifies on identical terms. Any answer taken today is *"of the models testable today"*.

**Two structural limits, both recorded rather than worked around:** (a) **`polygon` has no provenance entry** — `entries` is `[]` and the baseline is one opaque count, so the precedent the definition names **cannot be audited**; "polygon set the precedent" is an argument from prose. (b) A pre-S38 misclassification is **not addressable**: the README states the floor "cannot be RECONSTRUCTED" (three derivations give 65/93/76), only 14 of 76 were ever attributable by name, and the baseline "is never re-litigated".

**Decision:** No third instance, so the decision keeps its **"append N entries"** shape and does *not* escalate to "the classification needs re-deriving".

---

## Unknown 1.3: Does the "still genuine via warm-start" clause actually apply to twocge?

### Priority
**Medium** — this is the strongest counter-argument for 73, and it deserves to be stated fairly rather than dismissed. It affects one of the two entries, not both.

### Assumption
The definition's clause — *"a model that matches only via the presolve warm-start is still genuine if the fix changed its cold emit (the polygon/ps2 precedent)"* — applies to `twocge` as well as `elec`.

### Research Questions
1. The named precedent is explicitly about **non-convex** models where PATH cold-diverges to a spurious KKT point. Is `twocge` non-convex in that sense, or `likely_convex` with a different reason for needing the warm start?
2. What does twocge's **cold** solve actually do today — diverge to a different point, or fail outright?
3. Does `elec` fit the precedent more cleanly than `twocge` (elec's cold solve reaches a *different* stationary point of the Thomson problem, 244.624 vs 243.8128)?
4. If the clause fits elec but not twocge, is the honest answer **74** rather than 73 or 75?
5. Does the definition need amending so the test that gets applied is the test that is written?

### How to Verify
Read both models' convexity status and cold-solve behaviour from the DB and from a scratch-directory cold run. Compare each against the polygon/ps2 precedent's stated shape.

### Risk if Wrong
- **A 74 answer** that neither the plan nor the carryforwards anticipated, requiring both to be corrected.
- **A definition that keeps producing disputes** if it is not amended — this is the second sprint in which its application has been contested.

### Estimated Research Time
1.0 hour (DB read, two cold runs from a scratch directory, precedent comparison)

### Owner
Sprint 39 execution team

### Verification Results
❌ **Status:** WRONG — the assumption behind the counter-argument does not hold

**Verified by:** Sprint 39 Prep Task 3 · **Date:** 2026-08-29 · **Measured at:** `8a5a88bc`

**The assumption was** that the "still genuine via warm-start" clause was written for the **polygon/ps2 non-convex** shape, which twocge might not fit. **It does not survive contact with the data.**

**Findings:** `polygon` — the only in-corpus member of that precedent, and the one the definition actually names — is **`likely_convex`**, exactly like twocge and elec. The `non_convex` members are `ps2_f_s`, `ps2_s`, `ps3_s_gic`, which are the three **out-of-corpus** models the 2026-08-18 re-baseline *removed* (76 → 73) for being out of scope. Written "polygon/ps2" the precedent reads as one non-convex family; it is not.

Cold behaviour measured live, standalone from a scratch directory with `display nlp2mcp_obj_val` appended:

| model | cold status | cold objective | NLP | cold match? |
|---|---|---|---|---|
| twocge | **MS-1 Optimal** | 55.508 | 56.7778 | ✗ (−2.2 %) |
| elec | **MS-1 Optimal** | 244.624 | 243.8128 | ✗ (+0.33 %) |
| polygon | **MS-5 Infeasible** | — | 0.7797 | ✗ |

Both cold emits now *solve* — that is what the fixes bought — but converge on a **different KKT point**, which is why `_cold_objective_mismatches_nlp` fires and the pipeline retries with the warm start. That is exactly the clause's situation.

**Evidence:** DB `convexity.status` for all six models; cold runs in `/tmp/s39t3/cold*`; objectives read only after asserting `MODEL STATUS 1`.

**Decision:** On convexity, corpus membership, DB outcome and cold-solve failure, **twocge and the precedent are the same shape** — so convexity cannot separate them, and the plan's proposed case for 73 fails on its own terms. A distinction *does* remain, but it is the **nature of the cold change** (twocge's `.fx` bookkeeping vs elec's corrected mathematics), which makes **74** live. Routed to the owner via `FLOOR_DECISION_BRIEF.md` §3; not decided here.

---

# Category 2: dyncge — the Second Emit Defect That the Abort Was Masking

## Unknown 2.1: Is `CASE_A` reachable for dyncge at all, or is it non-convex like elec?

### Priority
**Critical** — P2 is budgeted 16–22h against a `CASE_A` target. If dyncge is non-convex, `CASE_A` is unreachable *by construction* and the honest deliverable is a documented divergence, not a Match. Discovering that on Day 8 wastes the budget.

### Assumption
dyncge's `CASE_B` verdict indicates a **fixable emit defect**, and once fixed the residual reaches `CASE_A` and the cold objective reaches 539570.5027 within tolerance.

### Research Questions
1. Is `CASE_B` distinguishable from `CASE_C` (non-convexity) for dyncge, or could the harness be reporting `CASE_B` for a genuinely non-convex model?
2. elec's harness verdict *changed* between authoring and Sprint 38 (`CASE_B` → `CASE_C_OBJDEF`) as the classifier improved. Could dyncge's `CASE_B` reclassify the same way?
3. Is dyncge's 29.3 % objective gap consistent with a wrong gradient, or with a different local optimum?
4. Does dyncge have the objective-defining-intermediate-variable shape that `case_c_objdef` detects?
5. What evidence would settle "unreachable" — and is it obtainable in prep?

### How to Verify
Re-run `scripts/diagnostics/kkt_residual.py` and read the *full* verdict including any case_c classifier output. Inspect dyncge's objective structure for the `case_c_objdef` shape. Compare the residual's distribution (concentrated vs diffuse) against elec's known non-convex signature and against a known `CASE_B` emit bug.

### Risk if Wrong
- **16–22h spent chasing an unreachable target**, with a REPLAN arriving late in the sprint.
- **A wrong Match projection** in the acceptance criteria (+1 → 97), which then reads as a miss.

### Estimated Research Time
1.5 hours (harness run, objective-structure inspection, signature comparison)

### Owner
Sprint 39 execution team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — `CASE_A` is the right target, but reachability is not yet provable

**Verified by:** Sprint 39 Prep Task 4 · **Date:** 2026-08-30 · **Measured at:** `37665091`

**Findings:** dyncge is **`likely_convex`**, and the harness reports **`CASE_B — emit_bug`**, not `CASE_C_OBJDEF` — so it is not, on today's evidence, elec's non-convexity shape. A concrete structural defect is located (see 2.2), with a well-defined correct target, which makes `CASE_A` the honest goal.

**But reachability cannot be asserted before the fix.** The assumption as written ("`CASE_A` is reachable") over-claims: the residual is currently dominated by the phantom-offset defect, and a second-order non-convexity beneath it would be invisible until that is corrected. **elec's own verdict changed from `CASE_B` to `CASE_C_OBJDEF` as the classifier improved** — precedent for exactly this.

**Evidence:** DB `convexity.status = likely_convex`; `kkt_residual.py` → `CASE_B`, max rel 6.22e-02.

**Decision:** Target `CASE_A`; **pre-register the REPLAN** rather than discovering it mid-sprint — if the residual persists as `CASE_C_OBJDEF` once the offsets are corrected, the honest deliverable becomes a *documented divergence* with `modelstat` asserted, **not** a Match. Written into #1714's PROCEED/REPLAN signal.

---

## Unknown 2.2: Is the defect IN the `pf`/`pq` block, or does it merely SURFACE there?

### Priority
**Critical** — the residual's top rows are the only localisation evidence P2 has. If the defect is upstream and merely *manifests* in `stat_pf`, tracing from those rows leads to the wrong layer — exactly Sprint 38's repeated failure.

### Assumption
The residual concentrating on `stat_pf(CAP,SRV)` / `stat_pq(HMN)` / `stat_pf(LAB,SRV)` means the defect is in how those stationarity rows are built.

### Research Questions
1. Do the top-residual rows share a structural feature (a common equation, a shared multiplier, an alias, a repeated domain)?
2. Is the defect a **wrong coefficient** on an existing term, or a **missing term** — these have different layers?
3. elec's defect surfaced in `stat_x` but originated in `derivative_rules.py`, *upstream of stationarity entirely*. Could dyncge's be the same shape?
4. Does the hand-derived KKT shape for `stat_pf` match the emit term-for-term, and where is the first divergence?
5. Is `eqpf2` — the equation #1693 fixed — genuinely uninvolved, or does it feed these rows indirectly?

### How to Verify
Hand-derive `stat_pf` and `stat_pq` from dyncge's source **before** reading the emitter. Compare term by term against the emitted rows for the top residual instances. Then trace the first divergent term to a layer, starting from AD/KKT and working outward.

### Risk if Wrong
- **The Sprint-38 failure repeated a fourth time** — a gate naming the emitter for a defect decided upstream.
- **A fix that changes the symptom without the cause**, which the `CASE_A` gate would then correctly refuse, burning the budget twice.

### Estimated Research Time
2.5 hours (hand derivation, term-by-term comparison, layer trace)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED — the defect is IN the `pf` block; the `pq` row only surfaces it

**Verified by:** Sprint 39 Prep Task 4 · **Date:** 2026-08-30 · **Measured at:** `37665091`

**Findings — located, not suspected.** `eqXp(i)`'s index `i` is **free and unrelated to the head's `(h,j)`**, so `stat_pf(h,j)` must carry `sum(i, (-1)*alpha(i)*f(h,j)/pq(i) * nu_eqXp(i))`. Instead the emit produces the diagonal plus a fan of manufactured offsets `nu_eqXp(j±1..3)`, each gated on **`$(ord(h) = k)`** — a guard on the **factor** index for a sum over the **goods** index. `h` = {CAP, LAB} has 2 members, so `ord(h)=3` terms are **dead**, and each row keeps a different wrong subset. `eqII` is corrupted identically (CAP rows only), which is why CAP carries the largest residual while LAB rows are also wrong. **dyncge's source contains no lead/lag at all** — every offset is manufactured. Measured: 12 phantom `nu_X(j±k)` refs, `ord(h)` guards ∈ {1,2,3}.

**`stat_pq` is CORRECT** — the decisive control. All seven pq-bearing equations present (exhaustive scan of 29 equation definitions), every coefficient verified term-by-term **including the `eqM`/`eqD` chain rules**, where the emitted tail `/A · B·C/B²` reduces exactly to `1/pq`. It carries **0** phantom refs and **0** `ord()` guards, because it is 1-D head / 1-D equation and never enters the dim-mismatch path.

**Decision:** The defect is **in** the `pf` block. `stat_pq(HMN)`'s residual (5.90e-02, second-largest) is **not explained by its own row** and most plausibly surfaces through the shared `nu_eqXp` multiplier — **not proven**, and #1714's REPLAN signal treats a surviving `stat_pq` residual as evidence of a second defect.

---

## Unknown 2.3: Is this mechanism already known under another name?

### Priority
**High** — Sprint 38's dyncge gate demanded "new logic" for a test that had existed since #942. Asking this question *first* cost ~40 lines of extraction instead of a new mechanism, and inherited three issues' worth of hardening.

### Assumption
dyncge's second defect is a **new** mechanism, not an instance of an already-fixed class wearing a different model's name.

### Research Questions
1. Is this an instance of the **positional-vs-declared-domain** class (Category 5)? dyncge has `Alias (u,v), (i,j), (h,k)` and multi-index equations.
2. Is it an alias-root collision of the kind `_remap_condition_to_domain` needed consume-once matching for (#1062/#1350)?
3. Is it the partial-collapse condition-substitution defect fixed for elec in `_diff_sum`?
4. Does any existing test or property fixture already cover this shape for a different population?
5. If it *is* a known class, why did the existing fix not cover dyncge — a gate too narrow, or a genuinely different variant?

### How to Verify
Cross-check dyncge's structure against the catalog Task 7 produces, and against the S38 fixes' guard conditions. Run dyncge through the existing regression tests for those classes and see whether any *should* have caught it.

### Risk if Wrong
- **New machinery written where extraction would do**, at the cost of the hardening the existing code has accumulated.
- **A missed opportunity to widen an existing fix**, which would protect other models rather than one.

### Estimated Research Time
1.5 hours (structural cross-check, existing-test replay)

### Owner
Sprint 39 execution team

### Verification Results
❌ **Status:** WRONG — the mechanism IS already known, under another name

**Verified by:** Sprint 39 Prep Task 4 · **Date:** 2026-08-30 · **Measured at:** `37665091`

**The assumption was** that this is a new diagnosis. It is not: it is a new *instance* of the **phantom-IndexOffset / plain-alias + dim-mismatch** family already tracked by **#1381** (consolidating camcge **#1354** and cesam2 **#1355** — `ISSUE_1355` is titled "Phantom IndexOffset `nu_COLSUM(i±N)` References in `stat_tsam` Stationarity", the same shape). The `ord(h)=k` guard comes from the **#1081** dimension-mismatch path in `src/kkt/stationarity.py` (~7107–7131), whose own comment describes a genuine lead/lag (`bal4(t) → x(t,l)`).

**⚠ But dyncge adds information the family did not have.** Every previously known member was found because it produced a **PATH `$141` compile failure** on the phantom reference. **dyncge is the first known SILENT instance**: its guards keep every phantom reference in range, so it compiles, solves to `MS-1`, and is wrong by 29.3 % with no diagnostic at all.

**Consequence:** #1381's *"at minimum 13 affected models"* is a census of models that failed **loudly**. Silent instances are invisible to that method, so the family's blast radius is plausibly larger than recorded. A search for the **structural** signature — `nu_X(idx±k)` paired with an `ord(…)=k` guard in a stationarity row — is recommended follow-up.

**Decision:** This is the S38 dyncge lesson repeating one level up: *before writing new emit logic, check whether the logic exists for a different population* — and here, **before filing a new defect, check whether the defect is already filed.** #1714 carries dyncge's gate and evidence, but the **fix probably belongs to #1381's Pattern C Phase B**, not a dyncge-specific patch.

---

## Unknown 2.4: Does `#1693` close cleanly on its own terms?

### Priority
**Medium** — a bookkeeping question with a real trap: widening a closed issue to cover a new defect is how a bounded track becomes unbounded.

### Assumption
`ISSUE_1693` is fully satisfied by the Sprint-38 landing (4 empty-pair errors → 0, `eqpf2` generating 12 off-diagonal rows and 0 diagonal) and the second defect belongs in a **new** issue.

### Research Questions
1. Does #1693's Phase-0 gate have any criterion the Sprint-38 landing did **not** meet?
2. Its PROCEED signal says "dyncge reaches PATH (any `modelstat`)" — is that satisfied, and is "any modelstat" still the right bar given the model now solves to a wrong answer?
3. Does #1693's Bucket/KPI note ("whether it then solves or matches is unclaimed") correctly cover the current state?
4. Would a reader of #1693 alone be misled into thinking dyncge is fully fixed?
5. What is the minimum cross-reference that prevents that?

### How to Verify
Re-read #1693's gate against the Day-12 measurements. Draft the new issue's opening paragraph and check it stands alone without #1693's context.

### Risk if Wrong
- **A widened #1693** that never closes, and a second defect without its own gate — the exact anti-pattern the three-gate firm-landing rule exists to prevent.

### Estimated Research Time
0.5 hours (gate re-read, cross-reference drafting)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED — #1693 closes cleanly; this is not a widening

**Verified by:** Sprint 39 Prep Task 4 · **Date:** 2026-08-30 · **Measured at:** `37665091`

**Findings:** #1693 was the `eqpf2` **empty-pair abort from diagonal self-cancellation**, fixed by reusing section 2c's diagonal-triviality test for equalities (section 3c). That defect is gone: `eqpf2` now generates 12 off-diagonal rows and 0 diagonal, with 0 empty-pair errors, and dyncge reaches `MODEL STATUS 1`.

The defect diagnosed here is a **different mechanism in a different place** — manufactured index offsets on `nu_eqXp`/`nu_eqII` in `stat_pf`, from the dim-mismatch path. It was *masked* by the abort (the model never got far enough to expose it), which is a sequencing relationship, not a shared cause.

**Evidence:** #1693's own resolution record; the located defect's mechanism (`ord(h)` offset guards) is untouched by the 3c change; cold emit compiles and solves.

**Decision:** #1693 stays closed on its own terms. dyncge's second defect is tracked separately as **#1714** — consistent with the Sprint 38 close, which recorded that closing #1693 does **not** mean dyncge is correct.

---

# Category 3: lnts — the Contradictory `.fx` Mechanisms

## Unknown 3.1: Do two `.fx` mechanisms actually collide at runtime?

### Priority
**Critical** — this is P3's entire premise, and it has **never been tested**. If no contradiction exists at runtime, the 14–18h track has no diagnosis and must REPLAN on Day 1.

### Assumption
Two mechanisms act on the same cells: the correct `y_fx_y2_h50.. y("y2","h50") - 5 =E= 0` and a blanket pruned-instance zeroing giving `y.lo = y.up = 0`, producing MS-4 at iteration 0 against equations demanding **5** and **45**.

### Research Questions
1. Are both mechanisms present in the emitted `lnts_mcp.gms` — the `_fx_` equation **and** a blanket zeroing that targets the same tuples?
2. At solve time, what are the **effective** bounds on `y("y2","h50")` after all fixing statements execute?
3. Do those bounds contradict the value the `_fx_` equation demands?
4. Is the contradiction the *cause* of MS-4 at iteration 0, or a coincidence alongside a different cause?
5. Do the values **5** and **45** appear where the hypothesis says they do?

### How to Verify
**A runtime bound probe, not a source read** — the claim is about the emitted model's bounds *at solve time*. Inject a `display y.lo, y.up;` after all fixing statements (or read the equation listing's bound columns) and compare against the `_fx_` equations' demanded values. **State the confirm and refute criteria before running.**

### Risk if Wrong
- **P3 has no diagnosis** and its 14–18h becomes a re-diagnosis with no bounded next step — the situation the selection rule exists to prevent.
- **A source-read "confirmation"** that agrees with the hypothesis while the runtime behaviour differs — the failure mode the probe requirement exists for.

### Estimated Research Time
2.0 hours (emit inspection, probe construction, run, comparison)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED — confirmed at RUNTIME, criteria fixed in advance

**Verified by:** Sprint 39 Prep Task 5 · **Date:** 2026-08-31 · **Measured at:** `4bbe7c3c`

**Findings:** The collision is real. A bound probe (`display` of effective `y.lo`/`y.up`, injected after all fixing and before `Solve`) was designed with **confirm/refute criteria written and committed before it ran** — `LNTS_PROBE_DESIGN.md` — then executed:

| tuple | `_fx_` demands | effective `lo` | effective `up` | verdict |
|---|---|---|---|---|
| `y("y2","h50")` | **5** | **0.000** | **0.000** | **CONTRADICTED** |
| `y("y3","h50")` | **45** | **0.000** | **0.000** | **CONTRADICTED** |
| `y("y4","h50")` | 0 | 0.000 | 0.000 | consistent — control ✓ |
| `y("y1","h0")` | 0 | −INF | +INF | blanket doesn't reach it |

All three CONFIRM criteria hold: a `D ≠ 0` tuple shows `lo = up = 0`; the contradiction is **exactly** zero rather than merely different (so it is the blanket, not a third writer); and the `D = 0` control is consistent, so the probe is not over-reporting. **No refute criterion fires.**

**Evidence:** fresh emit byte-identical to the golden; `MODEL STATUS 4` / `SOLVER STATUS 1` / `ITERATION COUNT 0` from GAMS's own anchored lines, with **no `**** ERROR` lines** — infeasibility is declared from bounds before any iteration.

**Decision:** The hypothesis banked since Sprint 38 is **confirmed**, and for the first time by runtime observation rather than a source read. Recorded in #1694's addendum.

---

## Unknown 3.2: Is the `fix_rhs = "0"` fallback even reached for lnts?

### Priority
**High** — the named fix surface is in `emit_gams.py`, which is where **three of four Sprint-38 gates wrongly pointed**. If the fallback is not reached, the surface is wrong and the trace must start over.

### Assumption
The blanket zeroing originates in the `fix_rhs = "0"` fallback in `emit_gams.py`, and the fix is to skip tuples already carrying a `<var>_fx_<labels>` equation — "the same shape as the Sprint-33 P6 fix".

### Research Questions
1. Is the `fix_rhs = "0"` fallback executed during lnts's emit — confirmed by instrumentation, not by reading?
2. Does it produce the specific lines that zero the contested tuples?
3. Is the Sprint-33 P6 fix's shape genuinely analogous, or is the analogy superficial?
4. If the fallback is *not* reached, which code path emits the blanket zeroing?
5. Is the decision made in the emitter at all, or upstream in IR/KKT — the layer question?

### How to Verify
Instrument the fallback (a temporary log or breakpoint) and re-emit lnts. Trace the actual origin of the zeroing lines. **Then** compare against the Sprint-33 P6 fix and state whether the analogy holds.

### Risk if Wrong
- **A fourth wrong-layer gate**, and 14–18h spent editing the wrong file.
- **A fix "the same shape as" a precedent that does not actually match**, which is how a superficial analogy becomes a wrong implementation.

### Estimated Research Time
1.5 hours (instrumentation, re-emit, origin trace, precedent comparison)

### Owner
Sprint 39 execution team

### Verification Results
❌ **Status:** WRONG — the named surface is not reached; the real one is elsewhere

**Verified by:** Sprint 39 Prep Task 5 · **Date:** 2026-08-31 · **Measured at:** `4bbe7c3c`

**The assumption was** that the fix surface is the **`fix_rhs = "0"` fallback** (`src/emit/emit_gams.py:3060–3061`). The carryforwards flagged it as an *untraced hypothesis*. It was traced by **instrumentation, not reading**, and it is wrong.

Instrumenting every site in `emit_gams.py` that emits a variable `.fx(...)$(not (...)) = …` line and re-emitting lnts:

```
SITE-S3005: y.fx(c,h)$(not (ord(c) <= card(c) - 2 and … or ord(h) > 1 or …)) = 0;
SITE-S3121: y.fx(c,h)$(not ((ord(c) <= card(c) - 2) and (ord(h) <= card(h) - 1))) = 0;
```

Line **3061 fired once — for variable `u`, taking the `u.lo(h)` branch** — and the `fix_rhs = "0"` fallback printed **nothing at all**. The blanket that pins `y` at `h50` is emitted at **line 3121**; line 3005 emits a wider first guard.

**Layer: EMIT**, `src/emit/emit_gams.py` ~3121 (and ~3005). Unlike three of four Sprint-38 gates, the emitter genuinely *is* the layer here — and that was established by **running the code**. The site collects equation conditions where `eq_domain == var_def.domain` and fixes the variable wherever the combined condition fails, **without consulting `var_def.fx_map`**, so it cannot see that a cell already carries an authoritative `_fx_` equation.

**The machinery to fix it already exists** (the S38 dyncge lesson): `_fx_eq_name()` at `emit_gams.py:711` is the canonical namer; `emit_gams.py:920` already builds a `suppressed` set of `_fx_` equation names — the same reasoning in the opposite direction; and `var_def.fx_map` already enumerates the fixed values (`partition.py:180`). **The fix is a lookup, not new machinery.**

**Is the "same shape as the Sprint-33 P6 fix" analogy genuine? Yes — structurally.** S33 P6 made the emitter skip an expression `.l` init when its `.l` refs were not a subset of `_declared_mcp_vars`: *guard an emission on the state of another emitted artifact*. The lnts fix is the same shape with a different predicate. ⚠ But note the analogy was cited **alongside a fix surface that turned out to be wrong** — soundness of the shape did not transfer to the location.

**Decision:** Surface corrected in #1694's addendum. The banked location would have sent Day 1 to a branch that never executes.

---

## Unknown 3.3: Does lnts's failure still reproduce as MS-4 at iteration 0 on current `main`?

### Priority
**High** — the whole track assumes a fingerprint nobody has re-measured since it was banked. Sprint 38 proved a five-times-carried failure description can stop reproducing entirely.

### Assumption
On current `main`, lnts emits byte-identically to its committed golden and its MCP still reaches **MS-4 at iteration 0**.

### Research Questions
1. Is a fresh emit byte-identical to `data/gamslib/mcp/lnts_mcp.gms`?
2. Does the MCP still return MS-4, and still at **iteration 0**?
3. What are the anchored `^****` diagnostics, and what does GAMS's own terminal line say?
4. Did Sprint 38's landings (`repeated_domain.py`, the `_diff_sum` fix, section 3c) change lnts's emit at all? The leak gate says no — is that confirmed?
5. Is lnts's DB row (`model_infeasible`) consistent with a fresh run?

### How to Verify
Re-emit, `diff` against the golden, run from a **scratch directory**, and read counts from GAMS's own `**** ... EXECERROR = n` / `MODEL STATUS` lines — **never** from a marker `grep -c`, which counts lines and undercounts under listing truncation.

### Risk if Wrong
- **The banked fingerprint is stale** and P3's diagnosis describes a failure that no longer occurs — the consultation-package failure mode, repeated.
- **A wasted probe design** aimed at the wrong symptom.

### Estimated Research Time
1.0 hour (re-emit, diff, scratch-dir run, anchored diagnostics)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED

**Verified by:** Sprint 39 Prep Task 5 · **Date:** 2026-08-31 · **Measured at:** `4bbe7c3c`

**Findings:** lnts still reproduces exactly. A fresh emit is **byte-identical** to the committed golden (`diff -q` clean), so the measurement describes the golden rather than a rebuild. From a scratch directory: `**** SOLVER STATUS 1 Normal Completion`, `**** MODEL STATUS 4 Infeasible`, `ITERATION COUNT 0`, `1 NONOPT` — and **zero anchored `**** ERROR` lines**, confirming this is a bounds contradiction detected in presolve rather than a compile or execution failure.

**Evidence:** `/tmp/s39t5` — emit + `gams lnts_mcp.gms lo=0 errmsg=1`; status read from GAMS's own lines, anchored `^****`; diagnostics fingerprinted with numbers collapsed.

**Decision:** Unchanged since Sprint 38 and since Task 2's independent reproduction. Safe to build the gate on.

---
# Category 4: sarf #1385 — the Four Untouched Call Sites

## Unknown 4.1: Are the four call sites still where Sprint 38 Day 7 recorded them?

### Priority
**Critical** — P4's 20–28h estimate rests on the cost being *located, not suspected*. Both `stationarity.py` and `emit_gams.py` changed materially in Sprint 38 (Days 9, 11, 12), so the recorded locations may have moved or been restructured.

### Assumption
The four call sites the Day-7 change deliberately did not touch are still present, at or near their recorded locations, and still carry the same cost shape.

### Research Questions
1. Do all four sites exist on current `main`, and at what file:line now?
2. Did Sprint 38's landings (`repeated_domain.py` as cli step 2.7, the `_diff_sum` condition fix, the `_replace_indices_in_expr` guard, section 3c) touch any of them?
3. Has the *shape* of any site changed — e.g. is a loop now guarded where it was not?
4. Are the six corpus-safety call sites from the earlier design still identifiable?
5. Does `SARF_REARCH_DESIGN.md` still describe the current code, or is it now a historical document?

### How to Verify
Locate each site by symbol rather than by line number, and diff `stationarity.py` / the AD layer between `8cffec29` and `9ab2c0c3` for anything intersecting them. Record the *current* file:line for each.

### Risk if Wrong
- **The 20–28h estimate is wrong** because the work starts with a re-location rather than an implementation.
- **The design doc becomes a trap** — a reader follows stale line numbers into unrelated code, which is precisely how three Sprint-38 gates went wrong.

### Estimated Research Time
1.0 hour (symbol search, targeted diff, re-record)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED — and PREP_PLAN's own check for this is wrong

**Verified by:** Sprint 39 Prep Task 2 · **Date:** 2026-08-27 · **Measured at:** `a8669ad6`

**Findings:** All four call sites are at their **exact** recorded line numbers: `src/ad/gradient.py:287`, `src/ad/gradient.py:453`, `src/kkt/complementarity.py:367`, `src/kkt/complementarity.py:512`. Neither file has changed since the Day-7 measurement anchor `949a4587` (**0** commits each).

**⚠ Two corrections, both routed to Task 6:**
1. **PREP_PLAN's Task 6 verification snippet checks the wrong thing** — it greps `referenced-instance|_is_concrete_instance_of|resolve_set_members` in `constraint_jacobian.py`, `index_mapping.py`, `stationarity.py`, none of which hold the four sites. Its comment even claims those files "moved in Sprint 38", which is inverted: `gradient.py`/`complementarity.py` have 0 commits since the anchor while `stationarity.py`/`emit_gams.py` have 2 and 4. Replace with the Day-7 form, `grep -n "enumerate_variable_instances(var_def" src/ad/gradient.py src/kkt/complementarity.py`.
2. **The four sites may not be where the time goes.** A live capped translate sits in **`enumerate_equation_instances`** (via `constraint_jacobian.py:947/1117/1424`), not in variable-instance enumeration — see Unknown 4.2.

**Evidence:** `grep -n "enumerate_variable_instances(var_def" src/ad/gradient.py src/kkt/complementarity.py` (4 hits, at the recorded lines); `git log --oneline 949a4587..HEAD -- src/ad/gradient.py` and `git log --oneline 949a4587..HEAD -- src/kkt/complementarity.py` (**0** commits each), against `-- src/kkt/stationarity.py` (2) and `-- src/emit/emit_gams.py` (4).

**Decision:** The sites are intact, so Task 6's premise holds. Its *verification command* and its *cost assumption* both need revision.

#### Task 6 addendum — both routed corrections resolved

**Re-confirmed by:** Sprint 39 Prep Task 6 · **Date:** 2026-08-31 · **Measured at:** `6b58d0ca`

**Still at the same lines**, re-located by **symbol** rather than by line number: `gradient.py:287` is in `compute_objective_gradient`, `gradient.py:453` in `compute_gradient_for_expression`, `complementarity.py:367` and `:512` both in `build_complementarity_pairs`. Still 0 commits to either file since `949a4587`.

**Correction 1 is APPLIED** — PREP_PLAN's Task 6 verification block now greps `grep -nE "=[[:space:]]*enumerate_variable_instances\("` in `gradient.py` and `complementarity.py`, and carries the inverted-rationale note so it is not reintroduced. The `=` anchor matters: an unanchored grep also picks up 3 imports, the `def`, three `>>>` doctest examples in `index_mapping.py` and a prose line at `gradient.py:48` — **8 non-call mentions**, so it reports 14 "callers" rather than 6. **The anchor is an ERE with `[[:space:]]*`, not a fixed string** (review finding): the fixed form `"= enumerate_variable_instances("` scores **1 of 3** against the whitespace variants `x = …` / `y=…` / `z  =  …`. Both the anchor's positive control and a cross-check listing every non-call mention are now part of the block, because a grep that silently under-reports looks exactly like a grep that found nothing.

**⚠ There are six callers, not four.** The other two — `constraint_jacobian.py:80` and `index_mapping.py:634` — are the ones the Day-7 referenced-instance filter already covers. That is consistent with "four *untouched* sites", but the phrase reads easily as "four sites total", and the difference is exactly what decides 4.2.

**⚠ Correction 2 is itself WRONG, and this matters more than the original claim.** At a 900 s cap, `enumerate_equation_instances` costs **0.329 s over 82 calls** — 0.04 %, not the hot path. Task 2's shorter cap stopped while the run was still *in* equation enumeration, so the deepest live frame read as the cost. **A capped profile's top frame is where the run currently is, not where the time goes** — a cumulative-time attribution needs the phase to have completed, or a cap chosen past it. See 4.2 for what the cost actually is.

**Decision:** Location holds under both measurements. What the location *means* for cost does not — see 4.2.

---

## Unknown 4.2: Do the four sites actually account for the bulk of the remaining wall-clock?

### Priority
**Critical** — "the remaining cost is at four call sites" is an attribution claim, and Sprint 38 Day 7 already demonstrated that an intuitive attribution can be wrong: the first narrowing traded 436 M differentiations for 436 M dict lookups and still did not terminate.

### Assumption
Fixing the four untouched call sites is sufficient to bring sarf from 28 m 40 s under the ≤300 s gate.

### Research Questions
1. In a bounded profile, what fraction of wall-clock do the four sites account for?
2. Is there a fifth cost centre that Day 7's profile did not surface because the run was capped?
3. Does the cost distribution change after Sprint 38's landings?
4. Is the remaining cost **per-column** (which the O(active) argument addresses) or **per-row** (which it explicitly does not — the 1,183 rows are untouched)?
5. If the four do not dominate, what is the revised estimate?

### How to Verify
Profile a **capped** sarf translate (the uncapped run does not terminate) and attribute cumulative time per site. Compare the row-vs-column split against the Day-7 projection of ~141 s at 1,183 rows × 398 cols.

### Risk if Wrong
- **P4's budget is wrong**, and the sprint's only KPI mover is mis-sized — with knock-on effects for every other priority's schedule slot.
- **A partial landing that leaves an inconsistent MCP**, since the atomicity argument assumes the four are the unit.

### Estimated Research Time
2.5 hours (capped profile, attribution, row/column split)

### Owner
Sprint 39 execution team

### Verification Results
❌ **Status:** WRONG — the four account for 0.5 %, not the bulk

**Verified by:** Sprint 39 Prep Task 6 · **Date:** 2026-08-31 · **Measured at:** `6b58d0ca`

**Findings — measured, not read.** Capped 900 s `cProfile` of a sarf translate (did not finish):

| frame | cumulative | % | ncalls |
|---|---|---|---|
| `compute_constraint_jacobian` | **637.9 s** | **70.9 %** | 1 |
| `_diff_sum` | 513.6 s | 57.1 % | 1,641,023 |
| `_is_concrete_instance_of` | 306.2 s | 34.0 % | **13,344,770** |
| `resolve_set_members` | 165.0 s | 18.3 % | **13,348,120** |
| `compute_objective_gradient` | 156.9 s | 17.4 % | 1 |
| **`enumerate_variable_instances`** | **4.4 s** | **0.5 %** | **40** |

`build_complementarity_pairs` does not appear in the top twelve.

**⚠ Task 2's routed correction is also wrong.** It named `enumerate_equation_instances` as the hot path; at this cap it costs **0.329 s over 82 calls (0.04 %)**. Task 2's shorter cap stopped while the run was still inside equation enumeration, so the deepest live frame read as the cost. Both the original claim and its correction located the cost at an *enumeration* function; neither is where it is.

**The charitable reading fails too.** "The four *emit* the instances later differentiated" would rescue the premise, but `compute_constraint_jacobian` (70.9 %) takes its columns from `constraint_jacobian.py:80`'s cache — **not** one of the four, and already narrowed by the Day-7 filter (`_REFERENCED_TUPLE_CAP = 200_000`; sarf's worst row is 51,840, so it engages). Narrowing the four leaves the dominant path untouched.

**And one of the four is dead code:** `gradient.py:453` sits in `compute_gradient_for_expression`, which has **no production caller** — only its own docstring and `tests/integration/ad/test_gradient.py`. Confirmed by instrumentation: it never fires during a translate.

**Per-column vs per-row, kept apart:** the blow-up is per-**column** differentiation inside the Jacobian, reached via `_diff_sum`. The 1,183 rows are untouched by the O(active) argument and remain a floor.

**Decision:** **This changes P4's estimate and is reported now.** The honest upper bound on the lever as scoped is `compute_objective_gradient`'s 17.4 %, and only three of the four sites are live. Routed to the owner via `SARF_CALLSITE_PLAN.md` §8 — prep does not silently re-aim the sprint's only KPI mover.

---

## Unknown 4.3: Does the ~141 s O(active) projection still hold?

### Priority
**High** — the ≤300 s gate was revised *because of* this projection (owner decision, 2026-08-18). If the projection has moved, the gate's headroom changes and may need revising again.

### Assumption
The O(active) projection of **~141 s** — 1,183 rows × 398 active columns at 3,343 differentiations/second — still holds on current `main`.

### Research Questions
1. Is the active-column count still **398**, or has the corpus or the filter changed it?
2. Is the row count still **1,183**?
3. Is the throughput still ~3,343 diff/s, given Sprint 38 added work to `_diff_sum` (the condition substitution) and to the cli (step 2.7)?
4. Does the projection have enough headroom under 300 s to survive a modest regression?
5. If the projection now exceeds 300 s, is that a gate revision or a scope expansion (gating the rows too)?

### How to Verify
Re-measure active columns and rows for sarf, and re-measure differentiation throughput on a representative model. Recompute the projection and compare against 300 s.

### Risk if Wrong
- **The gate is unreachable again**, repeating the situation that forced the 2026-08-18 revision from "single-digit seconds".
- **A landing that completes but misses the gate**, which under the three-gate rule is a carryforward rather than a win.

### Estimated Research Time
1.5 hours (column/row census, throughput measurement, recomputation)

### Owner
Sprint 39 execution team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — the rate holds, the scope premise does not

**Verified by:** Sprint 39 Prep Task 6 · **Date:** 2026-08-31 · **Measured at:** `6b58d0ca`

**The claim:** 1,183 rows × 398 active columns = 470,834 differentiations at 3,343/s ⇒ ~141 s. **The arithmetic is correct.**

**The rate survives.** Measured **1,146/s profiled** (1,031,810 `differentiate_expr` calls in 900 s). `cProfile` typically costs 2–4×, which brackets the claim — at 3× the implied true rate is **3,439/s** against the claimed 3,343/s.

**The scope premise does not.** The run performed **1,031,810** differentiations — **2.2× the projection's entire budget** — and had not finished. The code today does not differentiate 470,834 times; 398 active columns describes a state the narrowing is meant to *produce*, not one it has been shown to reach.

**Evidence:** `/tmp/s39t6/sarf.prof`; rate arithmetic reproduced in the plan doc.

**Decision:** The ≤300 s gate was revised *because of* this projection (owner decision, 2026-08-18). Its headroom is intact **conditional on** the narrowing achieving 398 active columns — a conditional that has never been tested and is the whole estimate. Recorded rather than re-baselined.

---

## Unknown 4.4: Can a surrogate fixture be built, and does the scope go 186 → 187?

### Priority
**High** — **sarf cannot be its own fixture** (at 369,024 declared columns the fail-before state does not terminate), so without a surrogate there is no fail-before test, and without that the landing cannot be verified.

### Assumption
A corpus-free surrogate can exercise the same shape at a size that terminates, and sarf newly producing a golden takes the leak-gate scope from **186 → 187**.

### Research Questions
1. What is the minimum surrogate that reproduces the O(declared) blow-up shape while terminating?
2. Does the surrogate exercise **all four** call sites, or only some?
3. When sarf produces a golden, does `--min-scope` need raising from 186 to 187, and is the assertion still on *discovery*?
4. Does `make leak-check MODEL=sarf` still report `NO-OP` today (expected, because sarf has no golden) — and will it stop once it does?
5. Does adding sarf's golden change the leak sweep's runtime materially?

### How to Verify
Build the surrogate and confirm it terminates while reproducing the shape. Check `--min-scope` handling in `scripts/sprint_audit/check_golden_staleness.py`. Time a sweep before and after adding a large golden.

### Risk if Wrong
- **No fail-before evidence** for the sprint's only KPI mover, which fails the Phase-0 gate on process grounds regardless of whether the code works.
- **A scope assertion that silently narrows**, which Sprint 37 established is a false-negative generator and worse than no check.

### Estimated Research Time
1.5 hours (surrogate design, scope check, sweep timing)

### Owner
Sprint 39 execution team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — a surrogate is buildable, but "all four" is impossible

**Verified by:** Sprint 39 Prep Task 6 · **Date:** 2026-08-31 · **Measured at:** `6b58d0ca`

**Findings:** sarf cannot be its own fixture — at **369,024** declared `task` columns (99.96 % of its 369,165) the fail-before state does not terminate. A corpus-free surrogate was **built and verified**, not merely specified: `task(g,t,mn,mn)` at 2×3×4×4 = **96** columns, preserving the shape (4-D variable with a **repeated declaration index**, driven by an objective and an inequality).

| site | hits | note |
|---|---|---|
| `gradient.py:287` | 3 | |
| `complementarity.py:367` | 2 | needs per-element `.lo` overrides |
| `complementarity.py:512` | 2 | needs per-element `.up` overrides |
| `gradient.py:453` | **0** | **unreachable — dead code** |

**It is a translate-path fixture, not a solve fixture.** The assertion is on the emit and on which sites execute while producing it. The two-line `Variable` → `Positive Variable` re-typing was challenged in review as a probable redefinition error; it is legal GAMS, and **GAMS 54.2.1 compiles the file with 0 compilation errors**. As an NLP it is **unbounded** (`MODEL STATUS 3`) — irrelevant to the purpose, recorded so "built and verified" is not read as "solves end to end".

**Two things the build taught that a specification would not have:** a first surrogate without per-element bound overrides reached **only 1 of 4** sites — the complementarity sites require `.lo`/`.up` *overrides*, not merely bounded variables. And the fourth site cannot be reached at any size, because nothing in production calls it.

**Decision:** "Hits all four" is unachievable **by construction, not by fixture design** — three of four is the maximum. Scope **186 → 187** is unchanged as a target, since it depends on sarf producing a golden, which depends on the ≤300 s gate.

---

# Category 5: The Positional-vs-Declared-Domain Audit

## Unknown 5.1: How many sites resolve an index positionally against a declared domain?

### Priority
**High** — P5's 12–16h is sized for an audit, and the audit's cost is a direct function of the site count. Two known instances were found by chasing unrelated symptoms; nobody has counted the population.

### Assumption
The number of positional-resolution sites in `stationarity.py` and the AD layer is small enough to audit exhaustively within P5's budget.

### Research Questions
1. How many sites index a declared domain positionally (`domain[pos]`, `smt_domain[pos]`, `var_domain[pos]`, `set_declared_domain[pos]`)?
2. How many perform a **first-match scan** over a domain tuple — the #1350 shape that needed consume-once matching?
3. Which sites are reachable with a domain that repeats a symbol, and which are provably not?
4. Do any sites exist outside `stationarity.py` — in `derivative_rules.py`, `emit_gams.py`, the IR layer?
5. What is each site's blast radius — how many corpus models reach it?

### How to Verify
Grep for the positional-indexing and first-match-scan patterns across `src/kkt/`, `src/ad/`, `src/emit/` and `src/ir/`. For each hit, determine reachability with a repeated domain by reading the call chain, **and record an argument for any "not reachable" verdict rather than asserting it**.

### Risk if Wrong
- **An audit that overruns its budget** if the site count is large, squeezing the KPI-moving priorities.
- **An audit that misses the layer where it matters** — elec's instance was in `stationarity.py` but tricp's required a fix *before differentiation*.

### Estimated Research Time
2.0 hours (multi-directory grep, call-chain reading, reachability arguments)

### Owner
Sprint 39 execution team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — auditable, but the population is not where the question looked

**Verified by:** Sprint 39 Prep Task 7 · **Date:** 2026-09-01 · **Measured at:** `52cb2da0`

**Findings.** Enumerated by **AST scan** over `src/kkt/`, `src/ad/`, `src/emit/`, `src/ir/` — not grep, so a shape spread across lines cannot hide.

The question's framing does not survive. "Indexes a declared domain positionally" is too wide to filter on: **173** subscripted-domain expressions and **33** `zip`-against-a-domain sites exist, and almost none can break, because `zip`/`enumerate` pair position *i* with position *i* and are repeat-safe. What breaks is a **symbol → (position | value)** step. **21 primary sites** carry one.

| verdict | sites |
|---|---|
| ALREADY GUARDED | **9** |
| NEEDS A TEST | **7** |
| NEEDS A GUARD | **4** |
| NOT REACHABLE (in sample) | **1** |

**The assumption holds — 21 is auditable inside P5's 12–16 h.** But three of the four highest-reach sites are *outside* `stationarity.py`: `constraint_jacobian.py:1466/1513` (12/15 and 11/15 sampled models) and `empty_equation_detector.py:127` (10/15). Q4 asked whether sites exist outside `stationarity.py`; **most of the reach does.**

**Blast radius was measured, not argued** — `sys.settrace` line tracing over 15 adversarially chosen models (both known instances, five of the six emit-level offenders, controls; `nonsharp` surfaced later). No source instrumentation, so nothing could be left in the tree.

**Membership tests are not in the class** (27 sites): `i in ('i','i')` behaves as `i in ('i',)`. They matter only as the **gate** in front of a positional step — which is exactly elec.

**Positive control:** the scan rediscovers both known instances — tricp at `stationarity.py:1500`, elec at `stationarity.py:3931/3954/3966`.

**Evidence:** `docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` §1–2.

**Decision:** The catalog is P5's input. **Reprioritise away from `stationarity.py`** — the class's reach is in the AD layer and the IR.

---

## Unknown 5.2: How many corpus models have a repeated-symbol SET domain (the elec shape)?

### Priority
**High** — the *variable*-domain case was measured in Sprint 38 (exactly two models: `tricp`, `ferts`). The **set**-domain case was never surveyed — elec was found by chasing a division-by-zero, not by looking.

### Assumption
The set-domain shape (`Set ut(i,i)`) is as rare as the variable-domain shape, so the audit's corpus exposure is small.

### Research Questions
1. How many of the 219 corpus models declare a **set** whose domain repeats a symbol?
2. How many of those are in the 142 convex candidates?
3. Of those, how many currently match — i.e. how many might be silently wrong today?
4. Is `elec` the only one whose emit was actually affected, or were others affected and not noticed?
5. Does the same question apply to **parameter** domains (`ferts` declares `rail(i,i)`), and does any code path resolve those positionally?

### How to Verify
Parse the corpus and inspect `model_ir.sets` (and `model_ir.params`) for repeated-symbol domains. Cross-reference the hits against their DB rows and against the emitted goldens for the collapse signature.

### Risk if Wrong
- **A larger affected population than expected**, which turns a 0-bucket prevention task into a correctness sweep with bucket implications — a good problem, but not the one budgeted.
- **A silently-wrong matching model**, which is the worst outcome in this class because nothing surfaces it.

### Estimated Research Time
2.0 hours (corpus parse, set/param domain census, golden cross-check)

### Owner
Sprint 39 execution team

### Verification Results
❌ **Status:** WRONG — the set-domain shape is 8× the variable-domain shape, and two banked counts are wrong

**Verified by:** Sprint 39 Prep Task 7 · **Date:** 2026-09-01 · **Measured at:** `52cb2da0`

**Findings — two independent methods.** An IR census over all 219 models and a source-level prescan of the raw `.gms`. They agree on **24** models; union **44**.

| kind | models | ∩ the 142 convex candidates |
|---|---|---|
| **set** domain | **16** | 11 |
| **parameter** domain | **21** | 16 |
| **variable** domain | **5** | 4 |
| equation domain | 0 | 0 |
| **any** | **34** | **25** |

**The assumption is refuted.** It states the set-domain shape is "as rare as the variable-domain shape, so the audit's corpus exposure is small". The set shape is **16**, **8×** the variable count — and **parameter** domains, never counted by anyone, are larger still at **21**.

**⚠ A second banked figure is also wrong.** The plan records the variable-domain case as **"exactly two models: `tricp`, `ferts`"** (S38-measured). It is **five**: `ferts`, `lop`, `maxmin`, `sarf`, `tricp`. `lop` declares `dtr(s,s,s,s)` — a **four-fold** repeat.

**Q3 — is a matching model silently wrong?** **11 of the 34 match**: `bearing`, `cesam2`, `chenery`, `elec`, `gussrisk`, `kand`, `maxmin`, `mexss`, `robustlp`, `srkandw`, `weapons`. **Carrying the declaration shape is not being wrong.** The emit-level property (5.3) is the discriminator, and it puts exactly **one** matching model in the suspect set — `gussrisk`, and its instance is **latent** (an NA-guard narrowed to the diagonal, on data that is never NA). (`weapons` is separately a known **spurious** match, S38 Day 10.)

**Q4 — is elec the only one whose EMIT was affected? NO.** The property finds **9 violations in 6 current goldens**: `dinam`, `egypt`, `turkpow` carry repeats the **source never declared** — manufactured by our emit — and `shale`, `gussrisk`, `nonsharp` carry declaration-derived ones (`nonsharp` also carries a manufactured `inter(col__kkt1,col__kkt1,stm)`). None of the five non-`gussrisk` models can affect a reported KPI today: four are `mcp_solve: failure` and `nonsharp` is convexity-`excluded` with no MCP solve. **`nonsharp` is 3-arity and was invisible to the original binary `name(x,x)` matcher — found only when review forced the matcher to be generalised.**

**Q5 — parameter domains: yes, and there is a site.** `stationarity.py:3432` resolves a **param's** declared domain positionally while keying `offset_map` by symbol, so `ferts`'s `rail(i,i)` receives the same offset at both positions.

**⚠ Coverage limit, stated not buried:** the IR census could not parse **41 of 219** models, 10 of them prescan candidates (`dinam` timed out at 120 s; several `$include` a file the corpus lacks). The per-kind figures are **lower bounds**.

**Evidence:** survey §4; reproducible via `docs/planning/EPIC_4/SPRINT_39/artifacts/census.py` and `prescan.py` (committed; their JSON outputs are run artifacts and are not).

**Decision:** The audit's corpus exposure is **an order of magnitude larger than budgeted for**, and it is concentrated in the two sub-shapes with **no** global guard. P5 stays 0-bucket, but its site prioritisation should follow §6 of the survey.

---

## Unknown 5.3: Is a generic property test expressible for this class?

### Priority
**Medium** — a per-site test protects each site; a property test protects the *shape*, including sites added later. The audit's long-term value depends on which is achievable.

### Assumption
A property test can express "no emitted equation head or guard may repeat a controlling index symbol where the declared domain repeats a set", generically across the corpus.

### Research Questions
1. Can the property be stated over the **emitted output** (no repeated symbol in a `stat_*`/`comp_*` head), the **IR**, or both?
2. Would such a property hold for models where a repeated head *is* legitimate — is there such a case?
3. Does the existing property-test catalog have a home for this shape?
4. Can the test run at corpus scale within CI's budget, or must it sample?
5. Does the guard `dedupe_repeated_variable_domains` already make part of the property trivially true, and does that weaken it?

### How to Verify
Draft the property and evaluate it against the current corpus goldens; check for legitimate counter-examples. Time it at full scale.

### Risk if Wrong
- **Per-site tests only**, meaning a future site introduced without the guard is unprotected — the class recurs.

### Estimated Research Time
1.0 hour (property drafting, corpus evaluation, timing)

### Owner
Sprint 39 execution team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — expressible and cheap, but ONE property cannot cover the class

**Verified by:** Sprint 39 Prep Task 7 · **Date:** 2026-09-01 · **Measured at:** `52cb2da0`

**Findings.** The assumption — that a single property can state "no emitted head or guard may repeat a controlling index symbol where the declared domain repeats a set" — **conflates two properties that behave differently.** Two are needed.

**P1 — no emitted equation HEAD repeats a controlling index symbol.** Stated over the emitted output, because that is where the GAMS semantics bite.
- **193 goldens, 3,100 heads, 0 violations, under 3 s.** Full corpus scale, no sampling.
- **Mutation-killed, not merely green:** with `dedupe_repeated_variable_domains` monkeypatched to a no-op, tricp emits **4** violations (`stat_slp(n,n)`, `stat_sln(n,n)`, `comp_lo_slp(n,n)`, `comp_lo_sln(n,n)`).
- **⚠ Q5 answered, and it is the key limit: the #1062 guard makes P1 trivially true *for variable domains*.** P1 is a regression test on one sub-shape. **Proof: P1 scores 0 on elec's pre-fix golden** — elec's defect was in a `$(...)` guard, never in a head.

**P2 — no emitted `$(...)` guard references a *symbol* at a repeated index.** Not set-specific — the matcher is `name(x,x)`, and the live hits are parameters as much as sets. The complement, and the one that finds live defects. **⚠ Known gap (PR #1718 review): it scans guard CONTENT only, not an assignment's left-hand side** — `gussrisk` is caught only because its repeat appears in both.
- Control: **elec pre-fix 1 violation, elec today 0.**
- **9 violations across 6 current goldens** (see 5.2 Q4).
- **Scoping is load-bearing:** a naive whole-file form flags `Set ut(i,i)` in elec's declaration block **both before and after** the fix — a false positive that would have made the check useless and, eventually, deleted.

**Q2 — legitimate counter-examples?** For **P1, none** (0 in 3,100 heads); a repeated head is never wanted, since the MCP is then left with unmatched columns. For **P2, yes** — a declaration and a genuinely diagonal reference are both legitimate; `gussrisk`/`shale` are the residue after guard-scoping: a *reference* built from the declared domain's own symbols.

**A third sub-shape neither known instance showed:** a manufactured repeat can be identically **TRUE** (`turkpow`: `vs(t,v) = ord(t) >= ord(v)` ⇒ `vs(v,v)` always holds ⇒ silently **over**-inclusive) as easily as identically false. **An "is this guard unsatisfiable?" check would miss half the population** — the property must be *"the index repeats"*.

**Q4 — CI budget:** both are pure text scans of `data/gamslib/mcp/`; **under 3 s over 193 goldens**, no re-emission, no GAMS. They belong beside the golden-level gates, not in the unit suite. No sampling required.

**Evidence:** survey §5.

**Decision:** Specify **two** properties, and **land P2 first** — it is the only artefact here that finds live defects and it gives every subsequent guard a fail-before.

---

# Category 6: Consultation Reply Integration or Follow-Up

## Unknown 6.1: Will a reply arrive by 2026-09-09, and would it be actionable?

### Priority
**High** — P6's 6–10h splits entirely on this, and **the date gate cannot be moved**. Both branches must be prepared because the answer is not knowable in prep.

### Assumption
A reply, if it arrives, will contain at least one of: a concrete option set / `optfile`, a regularization or continuation schedule, or a named reformulation class — the three things pre-registered as actionable.

### Research Questions
1. Has any reply arrived on #1462 or #1443 as of the prep date?
2. If a reply arrives, does the `--force {homotopy,multistart,optfile}` scaffold still accept a recommended option set directly?
3. What would a *non*-actionable reply look like (a diagnosis with no lever), and what is the response to that?
4. Does the license thread need a different follow-up cadence than the technical threads?
5. Is the follow-up comment drafted such that it does **not** re-open the send decision — the failure mode that produced five carries?

### How to Verify
Check both issues' comment history. Verify the `--force` scaffold still emits the μ-continuation driver and `optfile` on current `main`. Draft the follow-up and check its wording against the "do not re-open" constraint.

### Risk if Wrong
- **Improvisation on a date-gated day**, which is how a 6–10h slot becomes a lost day.
- **Re-opening the send decision**, which is the specific behaviour that caused the consultation to slip five sprints.

### Estimated Research Time
1.0 hour (issue check, scaffold verification, follow-up drafting)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: If a license arrives, does the 11-model batch actually solve?

### Priority
**Medium** — the cohort's **+11 ceiling is explicitly not a Sprint-39 projection**, so a disappointing result costs nothing in the acceptance criteria. But the *procedure* must be right, and one member is known to have had a wrong emit.

### Assumption
A single `--only-solve` pass over the 11 license-gated models is sufficient, and their committed goldens are correct.

### Research Questions
1. Is the cohort still exactly 11 (`egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `tricp`, `turkey`)?
2. Does `scripts/gamslib/run_full_test.py --only-solve` handle a batch of license-gated models correctly, given they currently have `solver_version: None`?
3. **`ferts`'s emit was silently wrong until Sprint 38 Day 11** — has any *other* cohort member's golden been exercised by anything stronger than byte-stability?
4. What would a per-model sanity check cost before spending license capacity on a batch?
5. Are the goldens current, or would the batch need a re-translate first?

### How to Verify
Confirm the cohort membership from the DB. Dry-run the `--only-solve` path. Review each member's golden provenance for whether it has ever run.

### Risk if Wrong
- **License capacity spent on goldens that do not execute**, which is exactly the `weapons` lesson ("a golden can pass structure/DB/NA-guard/determinism review and still not RUN") applied to eleven models at once.

### Estimated Research Time
1.0 hour (cohort confirmation, dry run, provenance review)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Does `agreste` need a new owning issue?

### Priority
**Low** — a bookkeeping question, but it gates whether an actionable reply about agreste can be acted on cleanly.

### Assumption
`agreste` has **no open owning issue** — #1068 covers an earlier, closed diagnosis — so an actionable reply would need a new one.

### Research Questions
1. Is #1068 genuinely closed, and does its content describe a different defect from today's MS-5-after-9,734-iterations?
2. Is there any other open issue referencing agreste?
3. What would the new issue's Phase-0 gate assert, given the fingerprint is *reproducible today* (LP, verified convex, NLP MS-1 @ 17706.43)?
4. Should the issue be filed pre-emptively in prep, or only if a reply arrives?
5. Does the same gap exist for any other banked candidate (`cesam`, `indus`, `dinam`)?

### How to Verify
Query the issue tracker for agreste and the other banked models. Read #1068's diagnosis against the current fingerprint.

### Risk if Wrong
- **An actionable reply with nowhere to land**, delaying work by the time it takes to author a gate.

### Estimated Research Time
0.5 hours (issue queries, #1068 read)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: The Presolve-Record Systemic Remedy

## Unknown 7.1: Is the population still 14, and is `weapons` still the only spurious match?

### Priority
**High** — P7's "all 14 rows or none" framing depends on the count, and Sprint 38 adopted goldens on Days 8 and 12 that may have changed it.

### Assumption
There are **14** dangling `mcp_file_used` rows (13 pre-existing plus `weapons`, whose presolve golden was reverted in review), and `weapons` remains the **only** spurious match of the presolve population.

### Research Questions
1. How many rows have a `mcp_file_used` pointing at a non-existent file today?
2. Is `weapons` among them, and is it still recorded as a match?
3. Re-running `scripts/sprint_audit/check_mcp_solve_attribution.py` over the full presolve population — is the spurious count still exactly 1?
4. Did Day 12's `elec` adoption (and the `dyncge` *non*-adoption) change either count?
5. Is the presolve population itself still the size the Day-10 census used?

### How to Verify
Count dangling references directly from the DB against the filesystem. Re-run the attribution checker over every `model_optimal_presolve` row and compare against Day 10's 33-row census.

### Risk if Wrong
- **A remedy scoped to the wrong population**, which is the specific failure Day 10 warned about: *"a partial heuristic applied to 30 models would manufacture a worse number than the one being checked."*

### Estimated Research Time
1.0 hour (dangling census, attribution re-run, comparison)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED

**Verified by:** Sprint 39 Prep Task 2 · **Date:** 2026-08-27 · **Measured at:** `a8669ad6`

**Findings:** The dangling population is **14**, unchanged, and `weapons` is among them (13 pre-existing + `weapons`). Spuriousness was re-checked over the **entire** presolve∧match population rather than spot-checked: of **34** models, **33** produced their own `MCP MS-1/MS-2` and exactly **1** — `weapons` — reported only an embedded solve.

**Four distinct populations, all correct, none to be reconciled into another:** 48 presolve rows (all-219) · 40 presolve goldens on disk · 34 presolve∧match (the attribution scope) · 31 presolve∧match∧convex-candidate (the KPI "presolve" line) · 14 of the 48 dangling.

**Evidence:** `scripts/sprint_audit/check_mcp_solve_attribution.py` over all 34; DB scan for the dangling rows.

**Decision:** Assumption holds exactly. P7's "all 14 rows or none" should state **which** population it means — routed to Task 8.

#### Task 8 addendum — re-derived at the point of use

**Re-confirmed by:** Sprint 39 Prep Task 8 · **Date:** 2026-09-01 · **Measured at:** `15fb4a78`

All five populations reproduce **exactly**: 48 presolve rows · 40 goldens on disk · 34 presolve∧match · 31 ∧convex · **14 dangling**. The attribution checker over all 34 again reports **33 MCP-SOLVED / 1 EMBEDDED-ONLY**, and the one is still `weapons` (`war/NLP MS-2`, no MCP summary).

The 14, named: `aircraft`, `apl1p`, `apl1pca`, `china`, `circle`, `imsl`, `lmp2`, `prodsp2`, `ps10_s_mn`, `ps5_s_mn`, `senstran`, `spatequ`, `trig`, `weapons`.

**The routed question is answered:** "all 14 rows or none" refers to the **dangling** population. The spurious population is **1**, and their intersection is `weapons` alone — which is why one remedy cannot cover both (see 7.2).

---

## Unknown 7.2: Which remedy shape covers ALL affected rows?

### Priority
**Critical** — Sprint 38 established that a model-by-model correction manufactures a worse number than the one being checked. If no single remedy covers every row, P7 cannot land as specified and must be re-scoped before the sprint, not during it.

### Assumption
One of two remedies covers the whole population: either wiring the attribution check into the pipeline's record-writing so a spurious match cannot be recorded, **or** re-specifying `mcp_file_used` (e.g. null unless a committed golden exists) and back-filling.

### Research Questions
1. Does the attribution-gate remedy fix the *dangling reference* problem, or only the spurious-match problem?
2. Does the field-respecification remedy fix the *spurious match*, or only the dangling references?
3. Is one remedy sufficient, or are both needed — and if both, is that still "systemic" or two fixes?
4. Where in `scripts/gamslib/run_full_test.py` does the record get written (`~954` per the Day-10 note), and is that the right insertion point?
5. Does either remedy change the DB in a way that breaks `--resolve-changed`, the KPI helper, or the floor tracker?

### How to Verify
Trace the record-writing path and enumerate which of the 14 rows each remedy would correct. Check each consumer of `mcp_file_used` and `outcome_category` for breakage.

### Risk if Wrong
- **P7 lands a partial remedy**, leaving a known-bad record in the DB that every future KPI derives from.
- **A DB change that breaks a gate**, since the DB is the substrate the KPI helper, the floor tracker and the checkpoint all read.

### Estimated Research Time
2.0 hours (path trace, per-row coverage analysis, consumer check)

### Owner
Sprint 39 execution team

### Verification Results
❌ **Status:** WRONG — neither remedy covers both defects; P7 needs two changes at one site

**Verified by:** Sprint 39 Prep Task 8 · **Date:** 2026-09-01 · **Measured at:** `15fb4a78`

**The assumption is that "one of two remedies covers the whole population". Neither does**, because the two findings are different kinds of defect that merely share a row:

- the **spurious match** is a *truth* defect — the row asserts something untrue;
- the **dangling reference** is a *specification* defect — the field records a real artifact under a name implying a different one.

| | spurious match (1 row) | dangling refs (14 rows) |
|---|---|---|
| **A** — gate the retry-success branch on attribution | **1 of 1** | **1 of 14** (`weapons` only, and only because its row reverts to the cold golden, which exists) |
| **B** — re-specify `mcp_file_used` + back-fill | **0 of 1** | **14 of 14** |

**A does not fix the other 13**: their retries genuinely succeeded, and `mcp_file_used` faithfully records a *generated* artifact never adopted as a golden. **B is a code change AND a back-fill**, not a back-fill alone — `run_full_test.py:954` rewrites the field on every successful retry.

**⚠ A is a prerequisite for B's durability on the weapons row.** B alone nulls the path but leaves the match; the next re-solve restores both defects. **Recommendation: land A and B together at one site** — still systemic, but it must be *described* as two rules, because "all 14 rows or none" is true of B and false of A.

**Q4 — the insertion point.** `run_full_test.py:936`, `if retry_result["status"] == "success":`, which sets `presolve_required` (`:949`), `mcp_file_used` (`:954`), `outcome_category` (`:955`). **The Day-10 note's `~954` is one of the three and is the wrong place to gate.** Located by symbol, then read back.

**The fix does not invent a category.** Measured: weapons' **cold** emit solves — `MODEL STATUS 1` @ **1700.397** vs NLP 1735.5696, a **2.03 %** divergence, so the retry was correctly triggered. The right record is weapons' own cold result, and the `else` branch already restores exactly that (`original_mcp_solve`). **The remedy declines to overwrite rather than choosing a replacement.**

**Q5 — consumer breakage:** see 7.3.

**Evidence:** `docs/planning/EPIC_4/SPRINT_39/PRESOLVE_RECORD_REMEDY.md` §2–3.

**Decision:** P7 does **not** need re-scoping, but its acceptance statement does: two rules, one insertion point, one PR.

---

## Unknown 7.3: Does the Match 96 → 95 correction break any gate or report that assumes monotonicity?

### Priority
**High** — a **falling** Match is unusual, and Sprint 38's close rule #2 exists precisely because a lateral or downward move reported alone reads as a regression. If a gate treats it as one, P7 cannot land.

### Assumption
Reclassifying `weapons` takes Match 96 → 95, and no gate, CI check or report treats a falling Match as a failure.

### Research Questions
1. Does any CI workflow or script assert a **non-decreasing** Match?
2. Does `check_parse_rate_regression.py` or any sibling have a Match analogue?
3. Do the Sprint-39 acceptance criteria as written (`Match ≥ 96`) contradict the correction — and how should they be phrased instead?
4. Does the Rolling-KPIs table or `SUMMARY.md` need a footnote so the fall is not read as a regression later?
5. Does the floor change? (It should not — `weapons` is a presolve match, so cold stays 65 either way.)

### How to Verify
Grep the CI workflows and `scripts/` for Match-monotonicity assertions. Re-read the Sprint-39 acceptance criteria and draft the corrected wording. Confirm the floor is unaffected via `scripts/sprint_audit/floor_tracker.py`.

### Risk if Wrong
- **A gate fails on a correct correction**, which is the worst kind of gate failure because the fix is to weaken the gate.
- **A future sprint reads the fall as a regression** and "fixes" it back.

### Estimated Research Time
1.0 hour (CI grep, criteria redraft, floor confirmation)

### Owner
Sprint 39 execution team

### Verification Results
🔶 **Status:** PARTIALLY WRONG — no gate breaks, but the fall is bigger than one figure

**Verified by:** Sprint 39 Prep Task 8 · **Date:** 2026-09-01 · **Measured at:** `15fb4a78`

**Q1/Q2 — no gate asserts Match monotonicity.** `scripts/check_parse_rate_regression.py` reads only `parse_rate_percent`, `convert_rate_percent` and `avg_time_ms` from a report JSON — **there is no Match analogue and it never reads the DB**. Across all ten workflows, `ci.yml` touches `gamslib_status.json` solely as a **cache key**. So the assumption "no gate treats a falling Match as a failure" **holds**.

**⚠ But "Match 96 → 95" understates it. Three figures move:**

| KPI-block row | before | after |
|---|---|---|
| **Match** | 96 | **95** |
| &nbsp;&nbsp;**cold-optimal** | 65 | **65 — unchanged** |
| &nbsp;&nbsp;**presolve** | 31 | **30** |
| **all-219 Match** | 99 | **98** |
| **Solve** | 111 | **111 — unchanged** |
| **`path_solve_terminated`** | 0 | **0 — unchanged** |

*Row names and order are `kpi_block.py`'s own, so the table cross-references the block a reader meets in a report.*

**Two feared collisions do not happen, and both had to be measured to rule out.** An earlier pass here assumed weapons should be recorded as a *failure* and reported `Solve 111 → 110` and **`path_solve_terminated` 0 → 1** — which would have collided head-on with Sprint 39's pre-registered criterion that it must **maintain 0**. Running weapons' cold emit refuted both: it solves (`MS-1` @ 1700.397), so only the *comparison* was untrue.

**Q5 — the floor cannot change, structurally.** `floor_tracker.compute_floor(provenance)` takes only the provenance dict and never reads the DB. Not "should be unaffected" — unaffected by construction.

**⚠ The one real gate interaction is `--resolve-changed`.** `_bucket_severity = compare_rank × 10 + outcome_rank`: weapons is `match` + `model_optimal_presolve` ⇒ **22** today, `mismatch` + `model_optimal` ⇒ **12** corrected. A drop classifies `backward`, the checkpoint's only NO-GO. It does **not** fire for P7 (the checkpoint selects on *changed goldens*, and P7 changes none) — but the mechanism matters inverted: **without Remedy A, a later re-solve re-records the spurious match and the checkpoint reads 12 → 22 as `forward`, applauding the regression.** That is the sharpest argument for A.

**Two consumers need care, neither a break.** `check_doc_figures.py`'s `dangling mcp_file_used rows` fact goes 14 → 0 and `Match` 96 → 95, so it will flag any **changed** doc line citing the old figures — correct behaviour, but the docs must move in the same PR. And `tests/gamslib/test_run_full_test_path_relative.py` (Sprint 27 #1400) requires a repo-relative path *when one is written*; a null must be an explicit allowed case.

**No test breaks.** `test_check_doc_figures.py`'s `TRUTHS` are **pinned** fixtures, deliberately not derived, and no test asserts derived == pinned.

**Q3 — Sprint 39's `Match ≥ 96` criterion must be restated** as: *Match ≥ 95, and exactly 95 if P7 lands, reported as a correction with its reason in the same sentence.* Wording pre-written in §5 of the remedy doc.

**Evidence:** remedy doc §4; CI grep across all 10 workflows; `kpi_block.compute_kpis` on a rewritten row.

**Decision:** P7 can land. Restate the acceptance criterion, and use the pre-written wording.

---
# Category 8: Infrastructure — the Sprint-38 Retrospective's Four Process Findings

## Unknown 8.1: Can `scripts/sprint_audit/check_phase0_doc.py` assert a "layer" field without breaking the existing gates?

### Priority
**Medium** — 8a is the direct response to three gates naming the wrong layer, but it changes a **required CI status check**, so a badly-scoped assertion blocks every emit-touching PR.

### Assumption
A `layer` field can be added to the Phase-0 template and asserted by `scripts/sprint_audit/check_phase0_doc.py` without invalidating the ~30 gates authored across Sprints 37–38.

### Research Questions
1. How many issue docs currently carry a `## Phase 0: Acceptance Gate` section, and would all of them fail a new `layer` assertion?
2. Should the assertion apply only to **new** gates, and if so how is "new" determined mechanically?
3. What is the field's vocabulary — parser / IR / AD / KKT / emit — and is it sufficient? tricp's fix was a *pre-differentiation IR pass*, which is arguably its own layer.
4. Does the checker's existing structural rule (canonical `###` subsections must sit directly under the `##` header) interact with a new field?
5. Is a warning-then-error rollout needed, or can it be a hard assertion immediately?

### How to Verify
Count existing gates and dry-run a prototype assertion over all of them. Draft the vocabulary against the four Sprint-38 defects and check each maps cleanly.

### Risk if Wrong
- **A required status check that fails on every existing PR**, which forces either a mass backfill or an immediate revert.

### Estimated Research Time
1.0 hour (gate census, prototype assertion, vocabulary check)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.2: Where does the "does this logic already exist for another population?" check live?

### Priority
**Medium** — 8b is the cheapest of the four findings to state and the hardest to enforce, because it is a *habit* rather than a mechanism.

### Assumption
The check can be embedded in the authoring workflow (the Phase-0 template or CONTRIBUTING) in a form specific enough to be actionable rather than aspirational.

### Research Questions
1. What would the check actually ask? "Does a similar test/guard exist for a different population (equalities vs inequalities, variables vs sets, cold vs presolve)?"
2. Can it be made mechanical at all — e.g. a required "considered and rejected" line naming the nearest existing mechanism?
3. Would it have caught dyncge's case, where section 2c's test existed for inequalities?
4. Would it have produced false friction on the Sprint-38 landings where new logic *was* the right answer (tricp's IR pass)?
5. Is the right home the Phase-0 template, CONTRIBUTING, or the PR checklist?

### How to Verify
Retro-apply the drafted check to all four Sprint-38 P8 gates and record whether it would have changed the outcome in each case. **A check that would have fired on all four is too broad; one that fires on none is useless.**

### Risk if Wrong
- **Process theatre** — a checklist item nobody can answer meaningfully, which devalues the rest of the checklist.

### Estimated Research Time
1.0 hour (drafting, retro-application to four gates)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.3: Are close-rule preconditions expressible mechanically?

### Priority
**Low** — 8c is a documentation rule with a small blast radius, but it comes from a real Sprint-38 failure: close rule #2 was written around P1's cascade, P1 was REPLAN'd on Day 1, and a sound rule went unmet for reasons unconnected to the close.

### Assumption
Each pre-registered close rule can carry an explicit **precondition**, so an unmet rule is distinguishable from a missed target.

### Research Questions
1. What form does a precondition take — "this rule applies only if track X landed"?
2. Can the closeout check preconditions mechanically, or is this prose discipline?
3. Would it have prevented Sprint 38's confusion, or merely documented it better?
4. Do the Sprint-39 close rules (`path_solve_terminated` maintain 0; Match may fall to 95) have preconditions that need stating?
5. Is there a risk that preconditions become escape hatches for rules that should simply be met?

### How to Verify
Draft preconditions for Sprint 39's pre-registered close rules and check each against the "could this be used to excuse a miss?" test.

### Risk if Wrong
- **Preconditions as escape hatches**, which would weaken the close discipline rather than sharpen it — the opposite of the intent.

### Estimated Research Time
0.5 hours (drafting, escape-hatch review)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 9: Epic-5 Handoff — the Two Answerable Open Questions

## Unknown 9.1: Is an automatic numéraire-selection rule achievable, or is per-model declaration required?

### Priority
**Medium** — Q1 from `CGE_DEGENERACY_SCOPING.md` §5. Design-only work; a negative answer ("per-model declaration required") is a perfectly good deliverable and may be the honest one.

### Assumption
A robust automatic rule exists — e.g. fix the price of the SAM's largest sector, or a CPI aggregate — that generalises across CGE models without per-model tuning.

### Research Questions
1. How many corpus CGE models are there, and how many declare a numéraire explicitly?
2. For those that do not, is there an unambiguous "largest sector" by SAM value?
3. Would a CPI-aggregate numéraire be expressible in the emitted MCP, or does it require a model-side change?
4. Does the rule need to be *correct* or merely *consistent* — i.e. does any valid numéraire choice resolve the degeneracy?
5. Since camcge is the **sole inherent** Walras case (§2 survey, Q4 answered), is a general rule even warranted, or is a single declaration sufficient?

### How to Verify
Survey the corpus CGE cohort for numéraire declarations and SAM structure. Evaluate each candidate rule against that survey, including its ambiguous cases. **Run no camcge experiment.**

### Risk if Wrong
- **Epic 5 starts with a rule that does not generalise**, discovering it on its own first day — the situation this scoping exists to prevent.

### Estimated Research Time
1.5 hours (CGE cohort survey, rule evaluation)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 9.2: Can Walras-degeneracy be detected without falsely flagging a well-posed model?

### Priority
**High** — Q2, and **the false-positive half is the hard half**. A detector that flags well-posed models is worse than none, because it would route healthy models into a transformation they do not need.

### Assumption
A preprocessing layer can detect Walras-degeneracy — via a PATH basis-singularity report, a rank check on the market-clearing block, or a structural heuristic — with an acceptable false-positive rate on the corpus.

### Research Questions
1. Which detection signal is available *before* solving — a structural rank check, or only a post-hoc solver report?
2. Applied to the 142 convex candidates, how many would a rank check on the market-clearing block flag?
3. Of those, how many are genuinely degenerate (expected: **1**, camcge) and how many are false positives?
4. Can a structural heuristic (redundant market-clearing row, no numéraire) distinguish them?
5. What false-positive rate would make the detector unusable, and is that threshold met?

### How to Verify
Implement the candidate detectors as *analysis only* over the corpus IR and count flags. Use the corpus as the false-positive test set — camcge is the only true positive per the §2 survey. **Run no camcge experiment; this is measurement over IR, not solving.**

### Risk if Wrong
- **A detector that flags healthy CGE models**, which would make the Epic-5 transformation actively harmful if applied automatically.
- **A detector that only works post-solve**, which changes Epic 5's architecture from preprocessing to a retry loop.

### Estimated Research Time
2.0 hours (detector prototyping over IR, corpus flag count, false-positive analysis)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 10: General Emit-Backlog Sweep

## Unknown 10.1: Does the refreshed catalog still yield ≥2 candidates satisfying the selection rule?

### Priority
**Medium** — P10 is the deliberate slack absorber and its deliverable is "≥2 backlog models recovered or re-triaged". Sprint 38 removed four models from `path_solve_terminated` entirely, so the population has changed and may no longer support that target.

### Assumption
After Sprint 38's landings, at least two backlog candidates still satisfy the pre-registered rule: a **reproduced fingerprint** *and* a **named fix surface**.

### Research Questions
1. What is the current non-solving candidate population, by outcome category?
2. Which have an owning issue, and of those, which have a Phase-0 gate? (Sprint 38 found **0 of 5** did, which is why P7 gated P8 that sprint.)
3. Applying the selection rule strictly, how many qualify — and is it still ≥2?
4. Does Task 7's positional-domain survey move any candidate from "new diagnosis" to "named fix surface"?
5. If fewer than two qualify, what absorbs P10's 12–16h instead?

### How to Verify
Rebuild the catalog from the current DB, join against `docs/issues/` for gate presence, and apply the rule. Cross-check the rejects against Task 7's survey output.

### Risk if Wrong
- **P10 has nothing to do**, and 12–16h of the sprint is unallocated — which either inflates the deep tracks (the thing P10 exists to prevent) or is simply lost.

### Estimated Research Time
1.5 hours (catalog rebuild, gate join, rule application)

### Owner
Sprint 39 execution team

### Verification Results
✅ **Status:** VERIFIED (contribution)

**Verified by:** Sprint 39 Prep Task 2 · **Date:** 2026-08-27 · **Measured at:** `a8669ad6`

**Findings:** **31** non-solving convex candidates, and the KPI reconciles fully: 142 candidates = 135 translate + **7** that fail to translate (`danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, `sarf` — exactly the 7 with no `mcp_solve` record); of the 135, Solve 111 leaves **24** (7 `model_infeasible` + 6 `path_syntax_error` + 11 `path_solve_license`), and 24 + 7 = 31.

**30 of the 31 have an owning `ISSUE_*.md`. `robot` does not** — it is in the 11-model `license-gated` cohort.

**Evidence:** DB scan joined against `docs/issues/**/ISSUE_*.md`, matched anchored on `^ISSUE_<n>_<model>-` (a substring match misattributes — `cesam` would claim `cesam2`'s docs).

**Decision:** Population confirmed for Task 11's catalog refresh. `robot`'s missing owner is routed there.

---

## Unknown 10.2: Is Sprint 38's Unknown 1.5 measurable this sprint?

### Priority
**Low** — it carried from Sprint 38 as 🔍 INCOMPLETE for a structural reason that has not changed. The value here is confirming it is *still* unmeasurable, so it is not re-scheduled optimistically a third time.

### Assumption
Unknown 1.5 — *does a general `$149` fix unblock the `$149` half of dinam / indus / turkpow / clearlak?* — remains unmeasurable, because it requires a `$149` fix in the tree and **P1 ganges was closed as unreachable at the rebind site**.

### Research Questions
1. Is #1668 still closed on both directions — direction 1 a measured no-op (265 fires, zero residual), direction 2 not expressible because ganges and `prolog` are locally indistinguishable?
2. Has anything in Sprint 38's landings changed the rebind site's information content?
3. Would measuring an unpatched tree restate those models' current failure rather than answer the question — the reason it was deferred twice?
4. Is there an *alternative* route to the same answer that does not require the rebind fix?
5. Should the unknown be **closed as unreachable** rather than carried a third time?

### How to Verify
Confirm #1668's state and re-read the Day-1 measurement. Check whether Sprint 38 touched the rebind path. Decide explicitly: carry, or close as unreachable.

### Risk if Wrong
- **A third optimistic carry** of a question that cannot be answered, which is the phantom-upside pattern the license-gated cohort classification exists to prevent.

### Estimated Research Time
0.5 hours (issue state check, path diff, disposition decision)

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Template for Adding New Unknowns During the Sprint

Copy this block, renumber within the appropriate category, and add a Table-of-Contents entry.

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
[Concrete experiment, command or control — not "investigate". Name the measurement.]

### Risk if Wrong
- **[Failure mode]:** [consequence for the sprint, with an hour cost if known]

### Estimated Research Time
[N] hours ([what the time is spent on])

### Owner
Sprint 39 execution team

### Verification Results
🔍 **Status:** INCOMPLETE
```

**Rules for new unknowns discovered mid-sprint:**
1. **Add it the day it is discovered**, not at close — a Sprint-38 finding recorded late was corrected twice before it settled.
2. **State the measurement, not the intent.** "Investigate X" is not a verification method.
3. **If it invalidates a prior unknown's Verification Result, say so explicitly** and update that unknown rather than leaving both.
4. **A count of findings is a figure** — derive it, do not recall it.

---

## Next Steps

### Before Sprint 39 Day 1

1. **Prep Task 2** re-derives the baseline and every quoted fingerprint — this gates every technical unknown (**1.1 · 2.2 · 3.3 · 4.1 · 7.1 · 10.1** contribute).
2. **Prep Tasks 3–11** resolve their assigned unknowns per the mapping table below. Each task's `Unknowns Verified` metadata names its set.
3. **Every Critical and High unknown (19) must reach ✅ VERIFIED, ❌ WRONG or 🔶 PARTIALLY WRONG before Day 1.** A Medium or Low may carry with a stated reason and the day that closes it.
4. **Prep Task 12** integrates the results into the day-by-day schedule, routing every unresolved unknown to the day that closes it.

### Success Criterion for This Document

**Prep should refute something.** Sprint 38's prep refuted 6 of 28 assumptions outright and partially refuted 3 more — a 32 % refutation rate on assumptions that had already survived a planning pass. **A prep phase that confirms everything has probably not looked hard enough.**

### During Sprint 39

- Review at each checkpoint (Day 5, Day 10) and at close
- Add newly discovered unknowns using the Template
- Update Verification Results with implementation findings, including anything that *contradicts* a prep verdict
- At close, the resolution tally feeds `SPRINT_RETROSPECTIVE.md` and the Sprint-40 carryforwards

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns. Task numbers refer to `PREP_PLAN.md`.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Re-Derive the Sprint-38 Baseline & Carryforward Fingerprints | 1.1, 2.2, 3.3, 4.1, 7.1, 10.1 | **Contributes to** each — re-derives the *figures* those unknowns rest on; the deeper verification belongs to the owning task. Gates every technical unknown. |
| Task 3: The Floor-Classification Decision Package (P1) | 1.1, 1.2, 1.3 | Owns Category 1 entirely. 1.1 is shared with Task 2, which supplies the git evidence. |
| Task 4: dyncge Second-Defect Diagnosis & Layer Trace (P2) | 2.1, 2.2, 2.3, 2.4 | Owns Category 2. 2.3 cross-checks against Task 7's survey if that has landed. |
| Task 5: lnts Fingerprint Reproduction & Runtime-Probe Design (P3) | 3.1, 3.2, 3.3 | Owns Category 3. 3.1's runtime probe is the decisive measurement. |
| Task 6: sarf's Four Call Sites — Cost Attribution & Atomicity Plan (P4) | 4.1, 4.2, 4.3, 4.4 | Owns Category 4. 4.2's attribution can invalidate P4's 20–28h estimate. |
| Task 7: Positional-vs-Declared-Domain Site Survey (P5) | 5.1, 5.2, 5.3 | Owns Category 5. Its output feeds Task 4 (2.3) and Task 11 (10.1). |
| Task 8: Presolve-Record Remedy Design (P7) | 7.1, 7.2, 7.3 | Owns Category 7. 7.1 is shared with Task 2, which supplies the population count. |
| Task 9: Consultation Reply-Integration & Follow-Up Package (P6) | 6.1, 6.2, 6.3 | Owns Category 6. Date-gated; both branches must be prepared regardless of 6.1's answer. |
| Task 10: Epic-5 Design Scoping — Numéraire Rule & Degeneracy Detection (P9) | 9.1, 9.2 | Owns Category 9. **Design only — no camcge experiment.** |
| Task 11: Emit-Backlog Catalog Refresh & Process-Infrastructure Spec (P8, P10) | 8.1, 8.2, 8.3, 10.1, 10.2 | Owns Categories 8 and 10. Depends on Task 7 for the 10.1 cross-check. |
| Task 12: Plan Sprint 39 Detailed Schedule | *(integrates all)* | Consumes every verified unknown; routes any unresolved one to the sprint day that closes it. |

**Coverage check:** every unknown 1.1–10.2 appears in at least one task's owned set. Tasks 2 and 12 are the only tasks that *contribute to* or *integrate* rather than own.

---

## Appendix: Document Cross-References

- **Sprint definition:** `../PROJECT_PLAN.md` → *Sprint 39 (Weeks 43–44)* — goal, ten priorities, deliverables, acceptance criteria, effort, risk
- **Prep tasks:** `PREP_PLAN.md` — the 12 tasks that verify these unknowns
- **Epic goals:** `../GOALS.md` — Epic-4 goals 6, 7, 8; success metrics; the deferred-work inventory
- **Sprint-38 hand-off:** `../SPRINT_38/SPRINT_39_CARRYFORWARDS.md` · `../SPRINT_38/SPRINT_LOG.md` · `../SPRINT_38/SPRINT_RETROSPECTIVE.md`
- **Per-category background:** see `PREP_PLAN.md`'s Appendix for the full per-priority document list
- **Research documents:** `docs/research/gamslib_kpi_definitions.md` · `docs/research/convexity_detection.md` · `docs/research/multidimensional_indexing.md`
- **Prior sprint deferred unknowns:** `../SPRINT_38/KNOWN_UNKNOWNS.md` (28 unknowns; **1.5** carries here as **10.2**)

*(No `PRELIMINARY_PLAN.md` exists for Sprint 39.)*
