# Sprint 38 Known Unknowns

**Created:** 2026-08-17
**Status:** Active — Pre-Sprint 38
**Purpose:** Proactive documentation of the assumptions and unknowns for Sprint 38 (the Sprint-37 carryforward sprint) **before** implementation begins — so each carryforward (ganges P1 `$149` rebind predicate, sarf P2 O(active) re-architecture, the P3 consultation decision) and each inherited measurement is verified in the prep phase, not discovered on Day 3.

---

## Executive Summary

This document identifies every open question, assumption, and risk across the eight Sprint-38 priorities defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 38, Weeks 41–42). Sprint 37 closed with the **genuine floor advancing 75 → 76** — the first advance since Sprint 33, ending four consecutive modal-flat closes — and deferred its two deep tracks with **measured refutations** rather than judgement calls. Sprint 38's unknowns are therefore mostly *inherited measurements* rather than open problems: the ganges cascade was verified working, the sarf bottleneck was profiled, and the cheap sarf shortcut was measured dead at ~5%.

That inheritance is itself the sprint's principal risk. The Sprint-37 retrospective's most general finding was **banked staleness** — figures accurate when written go wrong when used — demonstrated three times in that sprint alone, including inside its own closeout. **Every inherited figure below is registered as an unknown pending re-derivation by prep Task 2.** This is the deliberate difference from Sprint 37's prep, which verified fingerprints against documentation rather than recomputing them.

**Sprint 38 Scope (per `PROJECT_PLAN.md`):**
1. **P1 ganges/gangesx** — the `$149` rebind-predicate re-scope (all four cascade fixes VERIFIED working; blocked solely by a `prolog` over-fire; **0 bucket**, lateral `path_syntax_error → model_infeasible`)
2. **P2 sarf** (#1385) — the O(active) atomic re-architecture (**the sprint's only KPI mover**, +1 Translate → 136)
3. **P3 consultation** — the ownership decision: **send it or strike it** (Day 0; unsent across S33–S37)
4. **P4 presolve goldens** — close the 153-cold/17-presolve coverage asymmetry (scope 163 → ~199)
5. **P5 camcge** Epic-5 handoff + **turkey** licensed-testbed re-solve
6. **P6 (infrastructure)** — measurement integrity: the retrospective's three recurring defects + the DB re-anchor
7. **P7** — Phase-0 backfill for long-open issues (`$66`/#1289 has been un-implementable since Sprint 25)
8. **P8** — general emit-backlog sweep (the deliberate slack absorber, with a pre-registered selection rule)

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 38 section — goal, 8 priorities, deliverables, acceptance criteria, effort, risk) · `docs/planning/EPIC_4/SPRINT_38/PREP_PLAN.md` (the 11 prep tasks that verify these unknowns) · `docs/planning/EPIC_4/SPRINT_37/SPRINT_38_CARRYFORWARDS.md` (the six carryforwards with bounded next steps) · `docs/planning/EPIC_4/SPRINT_37/SPRINT_RETROSPECTIVE.md` §7 (the six Sprint-38 recommendations) · `docs/planning/EPIC_4/GOALS.md` (Epic-4 goals 6, 7, 8). *(No `PRELIMINARY_PLAN.md` exists for Sprint 38; the `PROJECT_PLAN.md` section, the `PREP_PLAN.md`, and the carryforwards doc are the planning sources.)*

**Lessons from Previous Sprints:**
- **The control-first REPLAN discipline (PR24/PR27) has held for eight consecutive sprints** — zero broken code across S30–S37. Every deep track is banked on control evidence *before* any bad ship.
- **Full-corpus (163-golden) leak verification is mandatory** for any shared-`_add_indexed_jacobian_terms` change (the S36 lesson: a 6-model cohort missed all three markov leaks). A "leak-free by construction" claim is a hypothesis, not a result.
- **A narrowing predicate that over-fires is usually fixed by ADDING a positive requirement, not subtracting exclusions** (S37 fawley landed on attempt 3 after two subtract-only failures). This is the direct model for Unknown 1.2.
- **Assert a gate's SCOPE, not just its verdict** (S37) — a check that silently narrows passes while the property is false, which is a false-negative generator and worse than no check.
- **The genuine floor cannot be derived from the DB** — a mechanical count yields **65** against the recorded **76**, because the "cold emit byte-identical to pre-fix" qualifier lives only in the hand-partition.
- **Prep-doc `file:line` fix-surfaces are HYPOTHESES** — wrong ~4× in S27, and S37 found one stale precondition (sarf's site files) plus one false-positive fingerprint match.

**Deferred-unknown lineage:** these unknowns descend from Sprint-37 dispositions — the ganges cascade is the S37 **Day-4 REPLAN** (four fixes verified, `$149` over-fires on `prolog`; S37 Unknowns 2.1/2.3, GitHub #1667/#1668); sarf is the S37 **Day-7 DEFER on measured grounds** (the profile relocated the bottleneck; the memoization measured ~5% vs ~66× needed; S37 Unknown 5.1, `ISSUE_1385`); the consultation is the S37 **Day-0 finding** that it was never executable — the bundle names no recipient (S37 Unknown 3.1, **refuted**: the input had never been sent); the presolve goldens are the S37 **Day-9 incident** (36 regenerated and swept in by `git add -A`, removed in review); camcge/turkey carry forward from Sprints 32–37 (S37 Unknowns 6.1 **refuted** — no licensed testbed procurable — and 3.3); the measurement-integrity items are the S37 retrospective §2–§4 process findings.

---

## How to Use This Document

### Before Sprint 38 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (18 total)
2. Create minimal test cases / `/tmp` controls for validation (the ganges and prolog controls are minutes-scale and local; the full-corpus leak run is minutes-scale; the sarf blow-up does **not** terminate and must be capped)
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 38
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

**Total Unknowns:** 28

**By Priority:**
- Critical: 7 (25% — could derail a track or force a mid-sprint REPLAN; the ganges cascade premise + positive predicate + leak gate, the sarf volume-removal + timing premises, the consultation recipient, the floor-provenance reproduction)
- High: 11 (39% — require upfront research/design before Day 1)
- Medium: 7 (25% — resolvable during implementation)
- Low: 3 (11% — nice-to-know, low impact)

**By Category:**
- Category 1 (ganges/gangesx — the `$149` Rebind Predicate Re-Scope): 5 unknowns
- Category 2 (sarf #1385 — the O(active) Atomic Re-Architecture): 5 unknowns
- Category 3 (The Consultation Ownership Decision — Send It or Strike It): 3 unknowns
- Category 4 (The 36 Presolve Goldens — Close the Coverage Asymmetry): 4 unknowns
- Category 5 (camcge Epic-5 Scoping + turkey Testbed): 3 unknowns
- Category 6 (Infrastructure — Measurement Integrity): 4 unknowns
- Category 7 (Phase-0 Backfill for Long-Open Issues): 2 unknowns
- Category 8 (General Emit-Backlog Sweep): 2 unknowns

**Estimated Research Time:** ~33.5 hours (within the 28–36 hour target; spread across prep Tasks 2–10)

**By Resolution Status (as of creation, Prep Task 1):**
- ✅ VERIFIED: 0
- 🔍 INCOMPLETE: 28

---

## Table of Contents

1. [Category 1: ganges/gangesx — the `$149` Rebind Predicate Re-Scope](#category-1-gangesgangesx--the-149-rebind-predicate-re-scope)
2. [Category 2: sarf #1385 — the O(active) Atomic Re-Architecture](#category-2-sarf-1385--the-oactive-atomic-re-architecture)
3. [Category 3: The Consultation Ownership Decision — Send It or Strike It](#category-3-the-consultation-ownership-decision--send-it-or-strike-it)
4. [Category 4: The 36 Presolve Goldens — Close the Coverage Asymmetry](#category-4-the-36-presolve-goldens--close-the-coverage-asymmetry)
5. [Category 5: camcge Epic-5 Scoping + turkey Testbed](#category-5-camcge-epic-5-scoping--turkey-testbed)
6. [Category 6: Infrastructure — Measurement Integrity](#category-6-infrastructure--measurement-integrity)
7. [Category 7: Phase-0 Backfill for Long-Open Issues](#category-7-phase-0-backfill-for-long-open-issues)
8. [Category 8: General Emit-Backlog Sweep](#category-8-general-emit-backlog-sweep)

---

# Category 1: ganges/gangesx — the `$149` Rebind Predicate Re-Scope

## Unknown 1.1: Does the four-fix cascade still take ganges AND gangesx to `rc=0` on current `main`?

### Priority
**Critical** — if the verified cascade no longer reproduces, P1's entire premise collapses and the priority becomes a re-diagnosis rather than a predicate design (>8h).

### Assumption
The Sprint-37 Day-4 measurement still holds on current `main`: re-applying the four-fix scratch patch takes **both** ganges and gangesx from `rc=2` (78 × `$141`, 3 × `$145`, 9 × `$149`) to **`rc=0`, zero `$NNN`, zero `rPower`**, with EXECERROR cleared.

### Research Questions
1. Do ganges and gangesx still produce exactly 78 / 3 / 9 `$141` / `$145` / `$149` errors on a cold compile from current `main`?
2. Does re-applying the four-fix patch still drive all three counts to 0 on **both** models, verified per-model rather than inferred from one?
3. Has `src/` drifted since the S37 close (`8cffec29`) in any way that touches the cascade's surfaces?
4. Is `$149` still load-bearing — does reverting only `$149` still return `rc=2` with 9 × `$149`?
5. Is the `rPower` gate still reachable only through the cascade?

### How to Verify
Cold-compile both raw models on current `main` and count error signatures by **specific code**, not by non-zero total. Re-apply the banked four-fix patch on a scratch branch, re-count per model, then revert. Confirm `src/` delta since `8cffec29` via `git diff`.

### Risk if Wrong
- **Premise collapse:** P1 becomes a re-diagnosis, not a predicate re-scope; the 18–24h budget is wrong.
- **Split-cascade illusion:** if `$149` is no longer load-bearing, the whole "no leak-free subset" conclusion changes and a much cheaper fix may exist — worth knowing before designing.

### Estimated Research Time
1.5 hours (cold compile ×2, scratch re-apply, per-model re-count, revert)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Can the `$149` rebind be narrowed by a POSITIVE requirement that excludes `prolog` while preserving `rc=0`?

### Priority
**Critical** — this is P1's entire deliverable. If no positive requirement separates the cases, the cascade stays unlandable and P1 produces documentation rather than a landing (>8h REPLAN).

### Assumption
Following the Sprint-37 fawley pattern, a **positive** requirement — restricting the rebind trigger to a *genuinely-free `prod` bound* (#1668 direction 2) — separates ganges' case from `prolog`'s, where two subtract-only narrowings would not.

### Research Questions
1. What structurally distinguishes the bound `prolog`'s rebind fires on from the one ganges needs — expressed in IR/AST terms, not model names?
2. Can "genuinely-free `prod` bound" be expressed with predicates available at the emit site?
3. Does the positive requirement still admit every rebind ganges and gangesx need for `rc=0`?
4. Does #1668's direction 1 (rebind parameter indices consistently) offer a cheaper separation, or is it strictly worse?
5. Is there any model where the requirement is *ambiguous* — neither clearly free nor clearly bound?

### How to Verify
Reproduce the `prolog` drift and capture which rebind fires on which expression shape. Draft the positive requirement, then hand-evaluate it against `prolog`'s and ganges' shapes before writing code. Reject any predicate keyed on model name or domain alone — that is the S35–S37 leak pattern.

### Risk if Wrong
- **No landing:** the cascade stays banked for a second sprint with the same blocker.
- **Subtract-only relapse:** a predicate that merely excludes `prolog` will leak on the next model with a similar shape, exactly as the two prior fawley attempts did.

### Estimated Research Time
3 hours (reproduce drift, characterise both shapes, draft and hand-evaluate the requirement)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: Does the narrowed predicate pass the full-corpus (163-golden) leak gate with `prolog` byte-identical?

### Priority
**Critical** — the full-corpus gate is what refused the cascade in Sprint 37. A predicate that passes a cohort but not the corpus is not landable.

### Assumption
The narrowed predicate drifts **only** ganges and gangesx, leaving all other in-scope goldens — `prolog` above all — byte-identical.

### Research Questions
1. Which models' emit traverses the same rebind path? (This is the true risk cohort, and it must be derived, not guessed.)
2. Does `make check-goldens` at full scope show only ganges/gangesx drifting?
3. Is `prolog` byte-identical, and does it still solve `model_optimal` + match?
4. Does the gate run cleanly at 3 workers with 0 timeouts, given the 335s slow-emit goldens?
5. If the gate runs *after* P4's scope change, does the enlarged corpus change the answer?

### How to Verify
Map the leak surface from the emit path, not from a hand-picked cohort. Run the full-corpus sweep with the scratch predicate applied. Assert scope explicitly (`--min-scope`) so a silently narrowed sweep cannot masquerade as a pass — the S37 lesson.

### Risk if Wrong
- **Second-sprint refusal:** the same gate blocks the same cascade again, with 18–24h spent.
- **False pass:** a narrowed sweep reports clean while a leak exists — the false-negative mode the S37 retrospective calls worse than no check.

### Estimated Research Time
2 hours (leak-surface mapping + one full-corpus sweep with the scratch predicate)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.4: Is P1's bucket really 0, and does any gate or report assume `model_infeasible` is monotone non-increasing?

### Priority
**High** — if a KPI gate treats a rise in `model_infeasible` as a regression, a correct landing will be reported as a failure (4–8h of argument and rework).

### Assumption
A clean cascade moves ganges and gangesx from `path_syntax_error` to `model_infeasible` — a **lateral** move (pse 6 → 4, **mi 7 → 9**) with Solve 108 and Match 94 unchanged. The prep-era "+2 or 0" was refuted on S37 Days 4–5 and must not be reinstated.

### Research Questions
1. Does the 6th blocker still hold — embedded `ganges0` **MS-5 @ −386785.5017** against raw standalone **MS-2 @ 6395.5444**, with `mcp_model` **MS-4**?
2. Does any acceptance criterion, CI gate, or report treat rising `model_infeasible` as a regression?
3. Does `--resolve-changed` classify a `path_syntax_error → model_infeasible` transition as a bucket *hold* or a *move*?
4. Are the prep-era "+2 or 0" occurrences confined to historical documents, with no live plan carrying it?
5. Would a genuine +2 require anything beyond the #1378/#1424 embedded-divergence class?

### How to Verify
Re-measure the embedded-vs-standalone divergence. Grep the acceptance criteria, KPI table, and gate scripts for monotonicity assumptions on `model_infeasible`. Confirm the Sprint-38 plan and KPI column already state the mi-rise as expected.

### Risk if Wrong
- **Correct work reported as regression:** the sprint's one landing gets recorded as a KPI failure.
- **Re-inflated projection:** if "+2 or 0" survives anywhere live, the sprint over-promises by two buckets.

### Estimated Research Time
1 hour (re-measure divergence; grep gates and criteria for monotonicity assumptions)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.5: Does the general `$149` fix unblock the `$149` half of dinam, indus, turkpow and clearlak?

### Priority
**Medium** — a bonus rather than a commitment; wrong only costs the P8 sweep some candidates (2–4h).

### Assumption
The `$149` fix is general, so the four residual multi-root models see their `$149` errors clear — even though each retains other blockers (turkpow's ragged `Table mdatat`, clearlak's dynamic sets).

### Research Questions
1. Do all four currently fail with a `$149` component, and what else fails alongside?
2. Does the narrowed predicate clear the `$149` half for each?
3. Which of the four is closest to a full recovery once `$149` is cleared?
4. Do any of them enter P8's candidate pool as a result?

### How to Verify
Cold-compile all four with the scratch predicate applied and count remaining error codes per model. Feed the results into Task 10's candidate catalog.

### Risk if Wrong
- **Overstated P8 pool:** if none unblocks, P8 loses four candidates and may fall below its ≥2 threshold.

### Estimated Research Time
1 hour (cold-compile ×4 with the scratch predicate, per-model error census)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: sarf #1385 — the O(active) Atomic Re-Architecture

## Unknown 2.1: Are the three materialization sites and six call sites still where the design says, after `stationarity.py` gained +311 lines?

### Priority
**High** — a stale `file:line` surface costs re-tracing at the start of a 20–28h atomic change (4–8h).

### Assumption
S1 `constraint_jacobian.py:78`, S2 `index_mapping.py:634`, and S3 in `stationarity.py` are intact, and all six corpus-safety call sites remain at their recorded lines — as Sprint 37 confirmed even though `stationarity.py` is +311 since the anchor.

### Research Questions
1. Do the three sites still sit at their recorded lines and still perform the materialization the design targets?
2. Are all six corpus-safety call sites present and unchanged?
3. Did the markov (+259) and fawley (+54) landings perturb any of them, even incidentally?
4. Does the S37 "one stale precondition" note need updating again for Sprint 38?

### How to Verify
Read each site directly and confirm it does what the design assumes — the S27 lesson is that prep-doc `file:line` surfaces are hypotheses. Diff each file against the anchor for the specific regions.

### Risk if Wrong
- **Re-tracing under time pressure:** the atomic change's first hours go to locating surfaces rather than building.

### Estimated Research Time
1 hour (read and confirm 3 sites + 6 call sites)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Does the O(active) short-circuit actually remove `differentiate_expr` volume, not merely the column enumeration?

### Priority
**Critical** — the design's premise. Sprint 37's profile *moved* the bottleneck; if the short-circuit only skips enumeration, the re-architecture will not reach its target and 20–28h buys nothing (>8h REPLAN).

### Assumption
Short-circuiting to the 398 active columns removes the ~762K top-level `differentiate_expr` calls proportionally, because those calls are made *per column*.

### Research Questions
1. Is the ~762K differentiation count actually proportional to declared columns (369,024), or is it driven by expression size independent of columns?
2. Does the guarded emit path avoid entering `_diff_sum` for inactive columns at all, or does it enter and discard?
3. What is the predicted post-re-arch call count, and is it consistent with single-digit seconds?
4. Does `simplify` (10.5M calls, 49.7s) scale down with the same factor, or is it an independent cost?
5. Would the 927× declared-to-active ratio translate to anything near the required 66× wall-clock reduction?

### How to Verify
Trace the call path from column enumeration to `differentiate_expr` and establish the proportionality analytically before building. Cross-check against the S37 profile's per-function counts. Do **not** re-profile in full — Task 2 confirms the blow-up, Task 5 owns the analysis.

### Risk if Wrong
- **A 20–28h build that misses its target:** the change lands, is atomic, and sarf still times out.
- **Wasted atomicity:** because the change must land as one unit, a wrong premise cannot be discovered incrementally.

### Estimated Research Time
2.5 hours (call-path trace + proportionality analysis against the profile)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Does the re-architecture actually reach single-digit seconds — the ~66× reduction required?

### Priority
**Critical** — the Phase-0 gate (PR20) asserts single-digit seconds. Nothing has ever measured the post-re-arch time; the design predicts it (>8h if wrong).

### Assumption
Eliminating the 369,024-column materialization in favour of the 398 active ones takes sarf from **>330 s** to **single-digit seconds**.

### Research Questions
1. What is the predicted post-re-arch time, derived from the profile rather than asserted?
2. Which functions remain hot after the short-circuit — does `simplify` or `_diff_sum` become the new bottleneck, as it did under memoization?
3. Is there a partial measurement possible without the full atomic change (e.g. a bounded prototype on a reduced model)?
4. What time would still count as success if single-digit seconds is not reached — is 30s acceptable, or is the gate binary?
5. Does the 1-D analogue (srpchase, ~2.9s at O(active=398)) remain a valid reference point?

### How to Verify
Derive the predicted time from the profile's per-function costs scaled by the active/declared ratio. Identify a bounded prototype if one exists. Record the fallback threshold **before** the sprint so the gate is not renegotiated mid-flight.

### Risk if Wrong
- **Gate failure after a full build:** the change is correct and atomic but misses the acceptance threshold.
- **Threshold drift:** without a pre-registered fallback, a 40s result invites an argument rather than a decision.

### Estimated Research Time
2 hours (profile-based derivation + fallback threshold decision)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Can a surrogate fixture be built, given that sarf cannot be its own fixture?

### Priority
**High** — the Phase-0 gate needs a fail-before/pass-after fixture, and sarf's fail-before state does not terminate (4–8h to discover mid-sprint).

### Assumption
A small model exercising the same guarded 2-D-constraint path can serve as the fixture, with a terminating fail-before state — because at 369,024 columns sarf itself cannot.

### Research Questions
1. What is the minimal model that exercises the guarded path — how few columns still trigger the materialization?
2. Does the surrogate genuinely fail before and pass after, or does it pass trivially either way?
3. Is srpchase (the 1-D analogue) usable directly, or does the 2-D gate require a purpose-built model?
4. Can the fixture be corpus-free, so it runs in CI where `data/gamslib/raw/` is absent?
5. Does the S37 lesson apply — that a skip-if-absent fixture is inert in CI and therefore not a guard at all?

### How to Verify
Construct candidate surrogates and confirm fail-before/pass-after against the scratch re-arch. Require corpus-free construction so CI actually executes it.

### Risk if Wrong
- **No regression guard:** the largest single change of the sprint lands without a fixture, or with an inert one.

### Estimated Research Time
1.5 hours (construct and validate candidate surrogates)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Does sarf's new golden pass determinism ×3, and does its scope change collide with P4's?

### Priority
**Medium** — both P2 and P4 move the golden scope; an unresolved interaction costs a confusing gate failure (2–4h).

### Assumption
sarf newly producing a golden takes in-scope 163 → 164 (discovered 170 → 171), the golden is byte-stable across `PYTHONHASHSEED {0,1,42}`, and this composes cleanly with P4's separate 163 → ~199 adoption.

### Research Questions
1. Is the new sarf golden deterministic across the three seeds?
2. If P2 and P4 land in either order, does `--min-scope` end up correct in both sequences?
3. Does the allowlist need an entry for sarf (e.g. if its emit is slow enough to time out)?
4. Does the combined scope (~200) still sweep within the 3-worker budget?

### How to Verify
Emit sarf three times under the three seeds and compare md5s. Work through both landing orders on paper and confirm the `--min-scope` value each implies.

### Risk if Wrong
- **Gate confusion:** a scope assertion fails for bookkeeping reasons rather than a real leak, eroding trust in the gate.

### Estimated Research Time
1 hour (determinism ×3 + ordering analysis)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: The Consultation Ownership Decision — Send It or Strike It

## Unknown 3.1: Who is the recipient, and by what channel?

### Priority
**Critical** — this single unanswered question has blocked the item for five sprints. It is not an engineering unknown, and no amount of engineering effort resolves it.

### Assumption
A human owner can name a recipient and a channel by Day 0 — or, failing that, the item is struck and rocket/fawley's +Solve is removed from projections.

### Research Questions
1. Who are the intended recipients (the bundle references the PATH authors — Michael Ferris, Steven Dirkse), and is there a current address or channel for them?
2. Is there an existing contact route (issue tracker, mailing list, direct correspondence) already used by this project?
3. Who on the project side owns the send and the follow-up?
4. If no recipient can be named by Day 0, is the strike branch authorised to execute by default?
5. What record proves the send happened, given issue #1462 currently carries only the Sprint-28 bisect comment?

### How to Verify
This is answered by a **person**, not an experiment. Task 7 prepares both branches so the answer converts to action immediately; the verification is that a recipient and channel are written down, or that the strike decision is.

### Risk if Wrong
- **A sixth carry:** the item persists as a permanent fixture, and every sprint continues to count rocket's +1 as reachable while the gating action goes undone.
- **Silent projection inflation:** fawley's +Solve is in the same class and is inflated by the same omission.

### Estimated Research Time
0.5 hours (assemble the question; the answer is a decision, not research)

### Owner
**Requires a human decision-maker — not resolvable by an execution agent**

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: What does the strike branch actually cost, and what depends on it?

### Priority
**High** — if the strike removes a Sprint-39 dependency, striking has downstream schedule consequences that must be known before choosing (4–8h).

### Assumption
Striking removes rocket's +1 Solve and fawley's +Solve from projections, and requires updating Sprint 39's antecedent — which `PROJECT_PLAN.md` now records as Sprint 38 P3.

### Research Questions
1. Exactly which projected gains disappear if the item is struck?
2. Sprint 39 is "PATH Author Consultation & Solution Forcing" — is that sprint viable if the consultation was never sent?
3. Does striking imply re-scoping Sprint 39, or merely re-labelling its input?
4. Are there other models (beyond rocket and fawley) whose only remaining lever is this consultation?
5. What wording makes the strike executable same-day rather than opening a discussion?

### How to Verify
Trace every projection that depends on the consultation through `PROJECT_PLAN.md` and the Sprint-39 section. Draft the reclassification wording and confirm it is complete enough to apply without further decisions.

### Risk if Wrong
- **Hidden downstream cost:** striking silently invalidates a later sprint's premise.
- **Undecidable decision:** an uncosted branch means the Day-0 decision stalls again.

### Estimated Research Time
1 hour (trace dependencies; draft reclassification wording)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Would a reply be actionable as-is, or does the bundle need more before sending?

### Priority
**Medium** — a reply that cannot be acted on wastes the send (2–4h).

### Assumption
The bundle — finalized 2026-07-15 — is complete: question set, reproducible cases, and the ruled-out-lever survey, such that a recommended option-set or continuation schedule could be applied directly to `--force homotopy`.

### Research Questions
1. Are the reproducible cases still reproducible under GAMS 54.2.1, given the corpus was re-pinned after the bundle was written?
2. Does the ruled-out-lever survey still reflect current state (the S36 `--force` survey was NEGATIVE for fawley)?
3. Is the question set specific enough that a reply maps to an implementable change?
4. Does the bundle mention the v53→v54 transition at all, and does that matter to the recipients?

### How to Verify
Re-read the bundle against current state and list anything stale. Confirm at least one reproducible case still reproduces under v54.

### Risk if Wrong
- **A stale send:** recipients receive cases that no longer reproduce, which costs credibility and a round-trip.

### Estimated Research Time
0.5 hours (bundle review + one reproduction check)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: The 36 Presolve Goldens — Close the Coverage Asymmetry

## Unknown 4.1: Are all 36 presolve goldens reproducible from a clean re-solve?

### Priority
**High** — a non-reproducible golden is not adoptable, and discovering that mid-adoption invalidates the batch (4–8h).

### Assumption
A clean `--only-solve` regenerates all 36 identically to the ones Sprint 37 Day 9 produced and then removed.

### Research Questions
1. Do all 36 reappear, and are they byte-identical to the removed set?
2. Which models produced them, and does each correspond to a `model_optimal_presolve` outcome?
3. Are any dependent on solve-order or timing rather than being deterministic?
4. Does regenerating them require the full corpus re-solve, or can they be produced per-model?
5. Does the count stay 36, or has the v54 re-pin changed which models take the presolve path?

### How to Verify
Run a clean re-solve in a scratch directory (**never** `git add -A` afterward — the S37 Day-9 incident), inventory the produced goldens, and diff against the removed set.

### Risk if Wrong
- **Batch invalidation:** if some are non-reproducible, the adoption is partial and the coverage asymmetry only half-closes.

### Estimated Research Time
1 hour (clean re-solve + inventory + diff)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Does each golden match its model's EXPECTED presolve emit, rather than merely the run that produced it?

### Priority
**High** — this is the difference between a reference set and a self-certifying one; getting it wrong makes the leak gate weaker, not stronger (4–8h).

### Assumption
Each of the 36 can be reviewed against what its model's presolve emit *should* contain, so adoption is a reviewed decision rather than a snapshot of one run.

### Research Questions
1. What does "expected presolve emit" mean concretely for a given model — which properties must hold?
2. Can the review be done per-model in reasonable time for 36 goldens, or does it need sampling?
3. Are there models whose presolve emit is known-suspect and should be excluded?
4. Does any of the 36 encode a *bug* that adoption would freeze into the reference set?
5. What is the rejection criterion, and where is an exclusion justified?

### How to Verify
Define the review protocol first, then apply it to a pilot subset before committing to all 36. Prioritise models whose presolve path is load-bearing for a match (29 of the 94 matches are presolve).

### Risk if Wrong
- **Self-certifying references:** the gate expands to sweep references generated by the very run being certified — "how a gate stops being a gate."
- **Frozen bug:** a defective emit becomes the expected result.

### Estimated Research Time
1.5 hours (define protocol + pilot subset review)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: What is the leak-sweep runtime at ~199 in-scope, and does 3 workers still give 0 timeouts?

### Priority
**High** — the leak gate is the sprint's slowest and most depended-upon gate; pushing it into timeouts breaks P1's acceptance path (4–8h).

### Assumption
Going from 163 to ~199 in-scope goldens keeps the sweep within budget at the 3-worker default, which Sprint 37 chose after measuring 4/2/0 timeouts at 6 workers.

### Research Questions
1. What is the measured wall-clock at 163 in-scope today?
2. What does 199 project to, and is the relationship linear or dominated by the slow-emit outliers?
3. Do any of the 36 new goldens come from slow-emit models (the 335s class)?
4. Does 3 workers still yield 0 timeouts at the larger scope, or is a nightly split needed?
5. Does the CI job's timeout need raising, and is that a required-check risk?

### How to Verify
Time the sweep at the current scope, identify the slow-emit members of the new batch, and project. Decide the mitigation in prep if the projection is marginal.

### Risk if Wrong
- **A required check that times out:** golden-staleness is a required status check; a timing-out gate blocks every PR, not just P4's.

### Estimated Research Time
1 hour (time current sweep, classify new goldens, project)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: Does `--min-scope` need 170 → 206, and does the assertion still fire on discovery?

### Priority
**High** — a scope assertion that lags the corpus silently under-guards, which is precisely the defect class `--min-scope` was built to prevent (4–8h).

### Assumption
Adoption raises discovered goldens 170 → 206 and in-scope 163 → 199, so `--min-scope` must move to 206 in the same change, and the assertion must continue to fire on **discovery** before allowlist narrowing.

### Research Questions
1. Is `--min-scope` asserted on discovery (pre-narrowing) or on the swept set (post-narrowing)?
2. What value is correct after adoption — 206 discovered, or 199 in-scope?
3. If adoption is partial, how is the value kept consistent with the actual corpus?
4. Does raising it in a separate commit from the adoption create a window where the assertion is wrong in either direction?
5. Should the value be derived from the corpus rather than hard-coded, to prevent recurrence?

### How to Verify
Read the assertion's implementation to confirm where it fires. Work through the partial-adoption case. Consider deriving the value rather than hard-coding it — this is the same "derive, don't quote" principle as P6a.

### Risk if Wrong
- **Silent under-guarding:** the gate passes while sweeping fewer goldens than the corpus contains — a false-negative generator.

### Estimated Research Time
0.5 hours (read the assertion; work the partial-adoption case)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: camcge Epic-5 Scoping + turkey Testbed

## Unknown 5.1: Is a licensed >1000-row GAMS-54 environment obtainable at all?

### Priority
**High** — turkey's +1 has been carried as "pending a testbed" since Sprint 35 and was already refuted once in Sprint 37 prep. Carrying it again without an answer inflates the projection (4–8h).

### Assumption
Either a licensed environment can be procured (with a cost and a date), or turkey's +1 must be reclassified as **blocked** rather than pending.

### Research Questions
1. Is a GAMS licence covering >1000 nonlinear rows obtainable, at what cost, and on what timeline?
2. Are there alternatives — an academic licence, a hosted runner, a time-limited evaluation?
3. Could turkey be verified another way (a reduced instance that preserves the failure mode)?
4. What exactly would the licence buy: turkey alone, or other license-gated work as well?
5. If unobtainable, what is the correct wording so turkey stops appearing as reachable upside?

### How to Verify
Investigate licensing options concretely and record cost/timeline or a definitive negative. This is procurement, not engineering.

### Risk if Wrong
- **A fourth carry of phantom upside:** turkey's +1 keeps appearing in projections while being unreachable.

### Estimated Research Time
1.5 hours (licensing investigation + reclassification wording if negative)

### Owner
Sprint 38 execution team (**procurement decision may require a human**)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Does the camcge Epic-5 handoff need anything not already measured?

### Priority
**Medium** — the handoff's value is the refutation record; a gap means Epic 5 repeats an experiment (2–4h).

### Assumption
Sprint 37 Day 10's control measured everything Epic 5 needs — emit 19 s, 641 equations/variables, embedded NLP MS-2 @ omega 191.7346, `mcp_model` MS-4 — so the handoff is assembly, not new work.

### Research Questions
1. Is every refuted Walras variant recorded with its sprint, outcome, and structural reason?
2. Is the two-nullspaces diagnosis stated reusably, or only implicitly?
3. Does `../EPIC_5/CGE_DEGENERACY_SCOPING.md` already contain part of this, and what would duplicate?
4. Is the drop-row BAN recorded with its reason (primal-correct, breaks the MCP dual)?
5. Are there CGE-cluster models beyond camcge that share the structure and should be named?

### How to Verify
Audit the existing Epic-5 scoping doc against the S32–S37 refutation history and list the gaps.

### Risk if Wrong
- **Epic 5 repeats refuted work:** the drop-row variant in particular is primal-correct and therefore tempting.

### Estimated Research Time
1 hour (audit against refutation history)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Is the per-model-numéraire fallback still the right Epic-5 recommendation?

### Priority
**Low** — a recommendation, not a commitment; Epic 5 re-evaluates regardless (<2h).

### Assumption
The per-model-numéraire declaration remains the correct fallback given that a numéraire alone fixes the price-scaling ray but not the row-redundancy nullspace.

### Research Questions
1. Has anything since Sprint 32 changed the two-nullspaces analysis?
2. Does the v54 re-pin affect camcge's behaviour at all?
3. Are there published CGE-MCP approaches worth naming for Epic 5's benefit?

### How to Verify
Re-read the two-nullspaces diagnosis against the S37 Day-10 control figures and confirm consistency.

### Risk if Wrong
- **A weaker Epic-5 starting point**, but no Sprint-38 impact.

### Estimated Research Time
0.5 hours (consistency re-read)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: Infrastructure — Measurement Integrity

## Unknown 6.1: Do both gate-narrowing modes reproduce live, as fail-before evidence?

### Priority
**High** — P6b fixes two specific defects; if they cannot be reproduced, the fix is unverifiable and may not address the real behaviour (4–8h).

### Assumption
Both modes reproduce on demand: `--resolve-changed` selects by **git diff** so an uncommitted golden is invisible (this produced a false GO in Sprint 37), and `make leak-check MODEL=<id>` reports `NO-OP` for a model with no golden (which is how sarf's gate fails for a non-correctness reason).

### Research Questions
1. Does an uncommitted golden still produce a silent GO from `--resolve-changed`?
2. Does `leak-check` on a golden-less model still exit 0 with `NO-OP`?
3. Are there other narrowing modes not yet catalogued — e.g. allowlist growth, or a model absent from `raw/`?
4. What exit code and message should each produce instead?
5. Is there a legitimate case where an empty selection is correct, and how is it expressed without weakening the guard?

### How to Verify
Reproduce both modes deliberately: stage an uncommitted golden change and run the checkpoint; run `leak-check` against sarf. Capture the current output as the fail-before record.

### Risk if Wrong
- **Fixing the wrong thing:** a guard is added for behaviour that does not occur, while the real narrowing mode persists.

### Estimated Research Time
1.5 hours (reproduce both modes; catalogue any others; design exit semantics)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Can a provenance file reproduce the genuine floor of 76 exactly?

### Priority
**Critical** — if the provenance file cannot reproduce 76, the floor remains hand-maintained and unverifiable, and every future report of it is unauditable (>8h).

### Assumption
A per-model provenance file — recording for each counted model which limb it satisfies (cold match, or a fix that changed the cold emit) and when it began counting — sums to exactly **76**, against the mechanical count's **65**.

### Research Questions
1. Can every one of the 76 be attributed to a specific limb with evidence?
2. Which models count under the second limb (a fix changed the cold emit) but read `model_optimal_presolve` in the DB?
3. Does the S30-era robert precedent generalise — are there other models counted before their DB row caught up?
4. What is the exact gap composition between 65 and 76?
5. How does the tracker fail if its total diverges from the hand-partition — loudly, or by reporting its own number?

### How to Verify
Build the partition from Task 2's draft and reconcile to 76. Any model that cannot be attributed is a finding: either the floor is wrong, or the provenance is incomplete.

### Risk if Wrong
- **An unauditable headline metric:** the project's primary quality figure cannot be reproduced by anyone but its author.
- **Silent 65:** a future automation reports the mechanical count and looks authoritative.

### Estimated Research Time
1.5 hours (build partition, reconcile to 76, specify divergence behaviour)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Is the Sprint-37 close the correct re-anchor, and what does re-anchoring cost?

### Priority
**Medium** — a wrong anchor makes the checkpoint measure the wrong interval, but is cheaply corrected (2–4h).

### Assumption
`8cffec29` (the Sprint 37 close) is the correct new anchor for `--resolve-changed --since-commit`, replacing `78ceaead` (the S34 close), because the DB changed in Sprint 37 for the first time since S33.

### Research Questions
1. What does `--resolve-changed` select at `8cffec29` versus at `78ceaead`?
2. Does re-anchoring lose useful signal — the S34–S37 drift stops being re-checked every run?
3. Should the anchor be the close commit or the last DB-modifying commit?
4. Is there a convention in prior sprints for when the anchor moves?
5. Does anything else reference `78ceaead` that would need updating?

### How to Verify
Run the checkpoint selection at both anchors and compare the model sets. Grep for other references to the old anchor.

### Risk if Wrong
- **Mis-scoped checkpoint:** either too many models re-solve every run, or real drift goes unchecked.

### Estimated Research Time
0.5 hours (compare selections at both anchors; grep references)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.4: Do the new gate-scope assertions have false-positive modes that would block legitimate work?

### Priority
**Medium** — an over-strict guard that fires on valid states gets disabled, which is worse than a weak one (2–4h).

### Assumption
The assertions can distinguish "narrowed by accident" from "legitimately empty", so a genuinely empty diff or a genuinely golden-less model does not block a correct PR.

### Research Questions
1. What legitimate states produce an empty `--resolve-changed` selection?
2. Is a golden-less model ever a valid state that should pass rather than fail?
3. What escape hatch is appropriate — a flag, a label, an allowlist — and how is it prevented from becoming routine?
4. Does the Sprint-37 `skip-phase0` label precedent apply here?
5. How would we detect the escape hatch being over-used?

### How to Verify
Enumerate legitimate empty/narrow states from recent PR history and confirm each remains expressible under the new semantics.

### Risk if Wrong
- **A disabled guard:** an over-firing assertion gets bypassed by habit, restoring the original defect with extra ceremony.

### Estimated Research Time
1 hour (enumerate legitimate states from PR history; design the escape hatch)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Phase-0 Backfill for Long-Open Issues

## Unknown 7.1: How many open backlog issues lack a `## Phase 0: Acceptance Gate` section?

### Priority
**Medium** — the count determines P7's real size; wrong only mis-sizes an 8–10h priority (2–4h).

### Assumption
A meaningful number of open emit/AD/KKT-touching issues lack a Phase-0 section — as `$66`/#1289 (open since Sprint 25) and sarf/#1385 both did — and are therefore not implementable under CONTRIBUTING §392–447.

### Research Questions
1. How many open issues would a future sprint plausibly schedule, and how many have an issue doc at all?
2. Of those with a doc, how many carry a compliant Phase-0 section under "rule C" (the four canonical `###` names, prefix-matched, extras permitted)?
3. Does `check_phase0_doc.py` classify them consistently with a manual read?
4. Which are highest-priority to backfill — i.e. most likely to be scheduled next?
5. Are any issues *closed* that should have had a gate, indicating the problem is historical rather than current?

### How to Verify
Run the CI gate's own semantics across `docs/issues/ISSUE_*.md` and cross-reference against open GitHub issues. Classify three ways: compliant / doc-without-gate / no doc.

### Risk if Wrong
- **Mis-sized priority:** P7's 8–10h is either far too much or far too little.

### Estimated Research Time
1 hour (run the gate across the backlog; three-way classification)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Is `$66`/#1289's authored Phase-0 gate complete?

### Priority
**Low** — a single document's completeness; cheaply finished if not (<2h).

### Assumption
The Phase-0 gate authored for #1289 during Sprint 37 Day 5 is complete and compliant, so `$66` is now implementable whenever the cascade unblocks it.

### Research Questions
1. Does `ISSUE_1289`'s Phase-0 section contain all four canonical subsections?
2. Does it pass `check_phase0_doc.py`?
3. Does it reflect the *current* understanding — that `$66` is reachable only after the cascade lands?
4. Does it carry the `ac(i+2,r)` match-correctness risk noted in Sprint 36?

### How to Verify
Run the gate against the doc and read the section against rule C.

### Risk if Wrong
- **A still-unimplementable issue** that the plan assumes is ready.

### Estimated Research Time
0.5 hours (gate run + read)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 8: General Emit-Backlog Sweep

## Unknown 8.1: Does P8 have at least 2 candidates with a reproduced fingerprint AND a named fix surface?

### Priority
**High** — P8 absorbs 12–16h of slack. If it has no eligible candidates, that budget should move **before** the sprint, not during it (4–8h).

### Assumption
The candidate pool — the `$149`-half unblocks, the `path_solve_terminated` cohort, and bounded-defect `model_infeasible` models — yields at least two that satisfy the pre-registered rule.

### Research Questions
1. Which models sit outside the deep tracks in `path_solve_terminated`, `path_syntax_error`, and `model_infeasible`?
2. For each, is there a **reproduced** fingerprint (the specific mechanism, not a grep hit) and a **named** fix surface?
3. Which are structurally blocked and must be excluded (turkpow's ragged `Table mdatat`, clearlak's dynamic sets)?
4. Do any lack a Phase-0 doc and therefore fail eligibility on Task 9's criterion?
5. If fewer than 2 survive, where should the 12–16h go instead?

### How to Verify
Query the DB for the pool, apply the pre-registered rule to each candidate, and reproduce fingerprints for the top few. Record rejections with reasons.

### Risk if Wrong
- **An open-ended sweep:** without eligible candidates, P8 becomes the diagnosis sprint its selection rule exists to prevent.

### Estimated Research Time
1.5 hours (pool query, rule application, top-candidate fingerprint reproduction)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.2: Can a fingerprint match be a false positive, and does the rule guard against it?

### Priority
**Low** — a known failure mode with a known remedy; cheap to guard (<2h).

### Assumption
"Reproduced fingerprint" must mean the specific mechanism reproduces, not that a pattern matched — because Sprint 37 Day 0 recorded exactly this false positive, where a helper matching the `$141` pattern came from an unrelated cesam fix.

### Research Questions
1. What distinguishes a mechanism reproduction from a pattern match, operationally?
2. Does the selection rule as written admit pattern matches?
3. What is the minimum evidence for "reproduced" — a failing compile with the specific code, or more?
4. Should each catalogued candidate carry its reproduction command?

### How to Verify
Re-read the S37 Day-0 false positive and derive the operational criterion. Apply it to Task 10's catalog entries.

### Risk if Wrong
- **A candidate that isn't:** the sweep starts on a model whose fingerprint never actually matched, wasting a slot.

### Estimated Research Time
0.5 hours (derive criterion from the S37 case; apply to the catalog)

### Owner
Sprint 38 execution team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Newly Discovered Unknowns

*(Add unknowns discovered during Sprint 38 here, using the Template below. None yet.)*

---

## Confirmed Knowledge (From Sprint 37 and Earlier)

These were unknowns in prior sprints and are now settled. They are recorded so Sprint 38 does not re-litigate them.

- **The genuine floor is 76** and advanced from 75 via markov's `σ=sp` discriminator — the first advance since Sprint 33.
- **The floor cannot be derived from the DB.** A mechanical `Match − (presolve ∧ match)` count yields 65; the qualifier lives only in the hand-partition. (This motivates Unknown 6.2.)
- **ganges' cascade works.** All four fixes take both models to `rc=0`; the blocker is the `$149` rebind's over-fire onto `prolog`, and `$149` cannot be dropped.
- **ganges is 0 bucket.** The prep-era "+2 or 0" was refuted on S37 Days 4–5; the 6th blocker (embedded MS-5 divergence) is untouched.
- **sarf's cheap fix is dead.** Memoizing `resolve_set_members` bought ~5% against ~66× needed. Recorded in `ISSUE_1385` so it is not re-attempted.
- **sarf's bottleneck is per-column differentiation**, not column enumeration — the 369K-column framing is superseded by the profile.
- **The consultation was never sent** (S37 Unknown 3.1, refuted). The bundle names no recipient; this is not an engineering blocker.
- **No licensed >1000-row testbed was procurable** as of Sprint 37 (S37 Unknown 6.1, refuted). Unknown 5.1 re-asks because circumstances may change.
- **camcge is MS-4 against a correct NLP optimum** — structural Walras rank-deficiency, not an emit defect. Drop-row remains **BANNED**.
- **A numéraire alone is insufficient** for camcge: it fixes the price-scaling ray, not the row-redundancy nullspace.
- **Skip-if-absent fixtures are inert in CI** (S37 Unknown 7.3, refuted) — fixtures must be corpus-free to guard anything.
- **A positive requirement beats subtracted exclusions** for narrowing an over-firing predicate (S37 fawley, attempt 3).

---

## Template for New Unknowns

When adding unknowns during Sprint 38:

```markdown
## Unknown X.Y: [Question/Assumption]

### Priority
**[Critical/High/Medium/Low]** — [One-line impact]

### Assumption
[State the assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, /tmp controls, experiments, analysis to validate the assumption]

### Risk if Wrong
[Impact if the assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

**Before Sprint 38 Day 1:**
1. Research and verify all **Critical** and **High** priority unknowns (18 total) via prep Tasks 2–10
2. Execute the ganges/`prolog` controls and the full-corpus leak sweep; cap the sarf blow-up rather than letting it run; run the clean presolve-golden re-solve **from a scratch directory**
3. Update this document's Verification Results as each prep task completes
4. Adjust Sprint 38 scope if a Critical assumption is wrong — especially **1.1** (cascade premise), **1.2** (the positive predicate), **2.2**/**2.3** (sarf's volume and timing premises), **3.1** (the consultation recipient), and **6.2** (floor provenance)
5. Confirm zero Day-0 blockers at the Task-11 GO/NO-GO

**Two unknowns cannot be closed by an execution agent:**
- **3.1** (recipient and channel) requires a human decision-maker. Task 7 prepares both branches so the answer converts to action on Day 0; if no answer arrives, the **strike branch executes by default** — a sixth carry is not an acceptable outcome.
- **5.1** (testbed procurement) may require a purchasing decision. If negative, turkey's +1 is reclassified as blocked rather than pending.

**During Sprint 38:**
1. Reference this document daily
2. Add newly discovered unknowns (use the Template above)
3. Update verification results as features are implemented
4. Move resolved items to "Confirmed Knowledge"

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from `PREP_PLAN.md`) verify which unknowns. Each prep task's "Unknowns Verified" metadata mirrors this table.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| **Task 2:** Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints | **1.1, 2.1, 4.1** | Re-derives every inherited figure rather than re-reading it. Confirms the ganges cascade premise, the sarf site locations, and the presolve-golden reproducibility. Also produces the per-model floor-partition draft that Task 3 consumes for 6.2. |
| **Task 3:** Measurement-Integrity Design (P6) | **6.1, 6.2, 6.3, 6.4** | Owns all of Category 6. Requires both narrowing modes reproduced live as fail-before evidence (6.1), the provenance file reconciled to exactly 76 (6.2), the re-anchor chosen and costed (6.3), and false-positive modes enumerated so the guard is not disabled in practice (6.4). |
| **Task 4:** ganges P1 — `$149` Rebind-Predicate Design & Leak-Surface Analysis | **1.2, 1.3, 1.4, 1.5** | Owns the P1 design. 1.2 is the deliverable (the positive requirement); 1.3 is the gate that refused Sprint 37; 1.4 protects a correct landing from being reported as a regression; 1.5 feeds Task 10's candidate pool. |
| **Task 5:** sarf P2 — O(active) Re-Architecture Design Refresh & Atomicity Plan | **2.2, 2.3, 2.4, 2.5** | Owns the P2 design. 2.2 and 2.3 are the premises that a 20–28h atomic build rests on and must be settled before the build starts; 2.4 supplies the fixture sarf cannot be; 2.5 resolves the scope collision with Task 6. |
| **Task 6:** Presolve-Golden Adoption Plan & Runtime Impact (P4) | **4.2, 4.3, 4.4** | Owns adoption. 4.2 is the self-certification hazard; 4.3 protects a required status check from timing out; 4.4 keeps the scope assertion from lagging the corpus. Depends on Task 4 because P4 changes the gate P1 runs against. |
| **Task 7:** Consultation Ownership Decision Package (P3) | **3.1, 3.2, 3.3** | Prepares the Day-0 decision. **3.1 is answered by a person, not an experiment**; Task 7's job is to make both branches executable so the answer converts to action immediately. |
| **Task 8:** camcge Epic-5 Handoff Scoping + turkey Testbed Procurement (P5) | **5.1, 5.2, 5.3** | 5.1 is procurement, not engineering, and was already refuted once in Sprint 37 prep. 5.2 and 5.3 assemble the Epic-5 refutation record so Epic 5 does not repeat banned experiments. |
| **Task 9:** Phase-0 Compliance Survey over the Open Backlog (P7) | **7.1, 7.2** | Sizes P7 and determines which backlog candidates are even eligible for Task 10 — an issue without a Phase-0 section is not implementable under CONTRIBUTING §392–447. |
| **Task 10:** Emit-Backlog Candidate Catalog & Selection-Rule Dry Run (P8) | **8.1, 8.2** | Dry-runs the pre-registered selection rule. 8.1 decides whether P8's 12–16h is viable at all; 8.2 guards against the S37 false-positive fingerprint mode. Consumes 1.5 (from Task 4) and 7.1 (from Task 9). |
| **Task 11:** Plan Sprint 38 Detailed Schedule | *Integrates all 28* | Consumes every verified unknown; schedules the design-verified ones into the sprint day that closes them; sets REPLAN exits from the Critical unknowns and the Day-0 GO/NO-GO from Task 2's re-derivation. |

**Coverage check:** all 28 unknowns are assigned. Categories 1–2 split between Task 2 (premises) and Tasks 4–5 (designs); Categories 3, 5, 6, 7, 8 map to a single owning task each; Category 4 splits between Task 2 (reproducibility) and Task 6 (adoption).

---

**END OF SPRINT 38 KNOWN UNKNOWNS**
