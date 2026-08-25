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

**By Resolution Status (as of Sprint 38 Day 4, 2026-08-19):**
- ✅ VERIFIED: 18 — **6.1** (**both gate-narrowing modes reproduced live and fixed with fail-before/pass-after tests**; the `leak-check` NO-OP was a *correctness claim* about a model never compared → split into NO-GOLDEN / ALLOWLISTED / NO-OP), **8.1** (**5 candidates satisfy the rule vs a threshold of 2**, but **0 have a Phase-0 gate ⇒ P7 gates P8**; Task 9's Tier 1 needs correcting both ways), **8.2** (the rule **does** admit pattern matches; four-part criterion from three self-produced false positives, one 83 % wrong), **7.1** (**43 open issues lack a Phase-0 gate** — current, not historical; compliance is binary, zero partial gates; P7 is under-budgeted), **7.2** (#1289's gate complete, with a stale KPI and a missing prerequisite fixed), **5.3** (per-model numéraire still correct, re-confirmed and stamped under GAMS 54.2.1), **3.1** (**channel supplied by the owner 2026-08-18: email to `ferris@cs.wisc.edu` + `steve@gams.com`/`sdirkse@gams.com`; Branch A SEND unblocked after five carries**), **3.2** (strike ⇒ Sprint 39 survives, but rocket/fawley become unreachable, not deferred), **4.3** (presolve-golden sweep fits CI with headroom; the *local* 26.3 min was a 2× trap), **4.4** (derive `--min-scope` from `git ls-files`, not the filesystem), **2.2** (sarf premise confirmed: volume is per-column, measured), **2.4** (corpus-free surrogate sized), **2.5** (P2/P4 scope arithmetic order-independent), **2.1** (sarf sites intact), **4.1** (36 presolve goldens reproducible), **6.3** (re-anchor `8cffec29`, *conditional on 6b*), **6.4** (no false-positive modes), **1.4** (bucket 0; no gate treats a rising `model_infeasible` as a regression)
- ❌ WRONG: 6 — **1.3** (CLOSED as unreachable: no predicate ever existed to gate; **#1668 direction 1 is a no-op** — 265 fires, zero residual — and `prolog` drifts −3 bytes in the full sweep), **5.2** (**the Epic-5 handoff was already written** — three narrow gaps, not a document; writing one would have duplicated ~90 %), **4.2** (**14 of the 36 would pin emits that do not reproduce their NLP solution** — 7 mismatch, 6 skipped, 1 model_infeasible ⇒ two-tier adoption), **2.3** (**the sarf timing gate is refuted: ~141 s projected, not single-digit seconds** — the 927× column win is real but rows are untouched; **gate REVISED to ≤300 s nightly, owner decision 2026-08-18**), **6.2** (the floor cannot be reproduced from existing artifacts at 76 *or any figure*: three derivations give 65 / 93 / 76) · **1.2** (**no positive requirement is expressible at the `$149` rebind site** — ganges and `prolog` are *locally indistinguishable*; #1668 direction 2 is closed)
- 🔶 PARTIALLY WRONG: 3 — **1.1** (the **`$149` component reproduces** on current `main`, 199→178 errors on both models; the full four-fix `rc=0` claim is **not** re-established, and that is stated as a bounded gap), **5.1** (**not turkey alone — a 10-model `license-gated` cohort**, 7 % of the corpus, all emitting correctly and all rejected at generation; excluded from projections but actively pursued, ceiling +10 Solve) · **3.3** (the case reproduces under GAMS 54.2.1, but the bundle is **unstamped** and its figures predate the re-pin by 9 days — one-line fix, do not send without it) · **6.1** → ✅ **VERIFIED Day 4** (both modes reproduced live and now assert scope + exit non-zero; the NO-OP message was a *correctness claim* about a model never compared, now split into NO-GOLDEN / ALLOWLISTED / NO-OP)
- 🔍 INCOMPLETE: 1 — **1.5** (does the general `$149` fix unblock the `$149` half of dinam/indus/turkpow/clearlak). **Carries.** Its Day-3 measurement window required a fix in the tree; the Day-1 P1 REPLAN means there is none, and measuring an unpatched tree would restate those models' current failure rather than answer the question — the same reason Task 4 gave. **Formerly also in this set: 1.1 and 1.3**, both resolved on Day 1 (1.1 → 🔶, 1.3 → ❌).
  - *Standing note carried from Task 4:* Task 2's "the banked baseline is refuted" claim is **RETRACTED** — the `$141` figures were **printed-marker undercounts** under a GAMS listing-truncation cap, not a reproduction failure. `$145`×3 and `$149`×9 reproduce exactly, and Day 1 re-confirmed the `$149` half end-to-end (**GAMS totals 199 → 178** on both models). **Nothing about `$141` is concludable until a truncation-free census exists.**

**⚠ Task 2 surfaced a finding that lands on Unknown 6.2 early:** the genuine floor's provenance chain credits **three models that are outside the 142-candidate corpus** the floor is reported over (`ps2_f_s`, `ps2_s`, `ps3_s_gic` are `non_convex`, and were already so at the S32 anchor, immediately after the S31 sprint that credited them). Either the floor has been **overstated by 3 since Sprint 31** (true in-corpus floor **73**), or the floor's scope legitimately differs from Solve/Match's and that has never been written down. **Task 3 resolved the design question; the figure is now decided — `baseline.count = 73` (owner, 2026-08-18).** A *reconstructing* tracker is impossible (three derivations give 65 / 93 / 76), so the tracker is now **append-only from a declared baseline**. **The baseline is 73** (in-corpus only), decided 2026-08-18; the S31–S37 series was overstated by 3. See `BASELINE_RECONFIRMATION.md` §2 and `MEASUREMENT_INTEGRITY_DESIGN.md` §4.3.

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
🔶 **Status:** PARTIALLY ANSWERED — the **`$149` component reproduces** on current `main`; the full four-fix `rc=0` claim is **not** re-established
**Verified by:** Sprint 38 Day 1 · **Date:** 2026-08-19 · **Measured at:** `1e7b5023`

**Findings:** With the banked `$149` rebind applied as a scratch patch, per model and never inferred across the pair:

| | ganges | gangesx |
|---|---|---|
| **GAMS total errors** | **199 → 178** | **199 → 178** |
| `$149` printed markers | 1 → **0** | 1 → **0** |
| `gams rc` | 2 → 2 | 2 → 2 |

**21 errors cleared on each model and `$149` driven to zero — the component still works.** `rc` remains 2 **only because `$141` and `$145` were not applied**; this control tested #1668 direction 1, not the cascade.

**Why the full claim was not re-established, stated rather than papered over:** doing so means re-applying `a8ff626c` — a patch S37 Day 4 had to **correct mid-flight** as known-defective — to confirm a figure Day 4 already measured per-model. **The cascade was never P1's blocker**; the `prolog` leak is. Reconstructing it is the "nursing" the plan's Day-1 exit exists to prevent.

**Counting note.** The baseline shows **199 errors against ~50 printed markers**, with 2 `Remaining errors not printed` notices. The banked per-code figures (78/3/9) are printed-marker counts and are **undercounts**; the totals above are read from GAMS's own `**** N ERROR(S)` line.

**Evidence:** `DAY1_GANGES_CONTROL.md` §4.

**Decision:** 🔶 The `$149` half is live. **P1 REPLAN'd regardless** — the blocker is the leak, not the cascade.
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
❌ **Status:** WRONG — no positive requirement is expressible at the rebind site
**Verified by:** Task 4 (ganges P1 — `$149` Rebind-Predicate Design)
**Date:** 2026-08-17 · **Measured at:** `f04c3a44`

**Findings:** A **read-only probe** at the exact rebind site shows ganges and `prolog` are **indistinguishable on every locally-available field**:

| field | `prolog` (over-fires) | `ganges` (correct) |
|---|---|---|
| rebind | `gp -> food` | `j -> agricult` |
| `e ∈ bound_indices` | False | False |
| `bound_indices` | **`[]`** | **`[]`** |
| `e ∈ expr.index_sets` | True | True |
| occurs in retained `expr` | `[ParamRef, VarRef]` | `[ParamRef, VarRef]` |
| occurs in `log_term` | `[ParamRef, VarRef]` | `[ParamRef, VarRef]` |

The obvious candidate — *"fire only when the index is genuinely free"*, using the `bound_indices` parameter `_diff_prod` already receives — is **refuted**: `bound_indices` is **empty for both**. The enclosing `sum(gp, …)` that Day 4 identified is **stripped before differentiation reaches `_diff_prod`**, so the site cannot determine freeness at all.

**This is the fawley lesson inverted.** fawley succeeded because a positive requirement existed *in the information available at its site*. Here the correct and incorrect cases are **locally identical**, so no predicate over that tuple can separate them.

**Evidence:** probe v1 (`e_in_bound`, `bound`) and v2 (`prod_binder`, occurrence profile) across both models; 2 prolog sites and 6 ganges sites, all identical. `src/` reverted byte-identical. See `GANGES_REBIND_PREDICATE_DESIGN.md` §2.

**Decision:** ❌ **#1668 direction 2 is closed** — do not re-attempt it. The blocker is **missing context, not a missing predicate**, so P1 is a plumbing/relocation problem. Three replacement directions are named (§3), with **direction C (#1668 direction 1 — rebind parameter indices consistently) recommended first**: it is cheapest to test and was prematurely deprioritised on intent grounds in favour of the direction now refuted.

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
❌ **Status:** CLOSED AS UNREACHABLE — there was never a predicate to gate
**Verified by:** Sprint 38 Day 1 · **Date:** 2026-08-19 · **Measured at:** `1e7b5023`

**Findings:** This unknown asks whether *the narrowed predicate* passes the full-corpus gate with `prolog` byte-identical. **No narrowed predicate exists.** Task 4 refuted #1668 direction 2 (the information is not present at the site), and **Day 1 refuted direction 1 as a no-op** — its premise is false: measured over **265 rebind fires across three models, zero residual**, so `ParamRef` and `VarRef` are *already* rewritten together. **Neither #1668 direction is implementable at the rebind site.**

**What was measured instead — the gate run against the banked rebind**, which is the same emit direction 1 would produce:

```
checked 163 in-scope golden(s) (7 allowlisted)
  DRIFTED: ganges_mcp.gms (-37)  gangesx_mcp.gms (-37)  prolog_mcp.gms (-3)
```

**`prolog` is NOT byte-identical — it drifts −3 bytes.** So the property this unknown asks about is **false** for every predicate available today, and the leak is **exactly one model**, confirming S37 Day 4.

**The mechanism, newly identified:** the asymmetry is manufactured **downstream**, not in `_diff_prod`. The AD layer substitutes consistently; `_replace_indices_in_expr` then lifts concrete elements back to symbolic names **positionally against the declared domain**, and under prolog's `Alias (g,gp)` with `eta(g,gp,h)` the parameter's index **moves back to `gp`** while the variable's stays at `g`.

**Evidence:** `DAY1_GANGES_CONTROL.md` §2, §3, §4a.

**Decision:** ❌ Unreachable as posed. **It re-opens only if direction A lands** (banked, located at `stationarity.py:659/877/1130`, **untested** — owner decision 2026-08-19: **HOLD**).
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
✅ **Status:** VERIFIED — the bucket is 0, and nothing treats a rising `model_infeasible` as a regression
**Verified by:** Task 4 (ganges P1)
**Date:** 2026-08-17 · **Measured at:** `f04c3a44`

**Findings:** Swept `.github/workflows/`, `scripts/sprint_audit/` and `scripts/gamslib/run_full_test.py` for any assertion, threshold or regression check on `model_infeasible`: **none exists**. No gate would fail on mi 7 → 9.

The Sprint-38 acceptance criterion already states it correctly — *"`model_infeasible:` ≤ 7, **or ≤ 9 if the ganges cascade lands** — an increase here is a **lateral move from path_syntax_error, not a regression**, and must be reported as such"* — as does the S38 Rolling-KPIs column. Earlier sprints' rows read "≤ 7 (maintain; −1 per recovery)", but those are **historical targets, not live gates**, and bind nothing.

Bucket confirmed **0**: a clean cascade gives **pse 6 → 4, mi 7 → 9**, Solve 108 and Match 94 unchanged. The 6th blocker (embedded `ganges0` MS-5 @ −386785.5017 vs standalone MS-2 @ 6395.5444; `mcp_model` MS-4) is untouched, and a genuine +2 needs the unscoped #1378/#1424 class.

**Evidence:** grep over workflows/scripts → no monotonicity assertion; `PROJECT_PLAN.md` Sprint-38 acceptance criteria + KPI column. See `GANGES_REBIND_PREDICATE_DESIGN.md` §6.

**Decision:** ✅ A correct P1 landing cannot be misreported as a regression by any automated gate. The remaining risk is **narrative** — a human reading "mi rose" — which the pre-registered close rule already addresses.

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
🔍 **Status:** INCOMPLETE — CARRIES; its measurement window closed with the Day-1 REPLAN
**Verified by:** Sprint 38 Day 1 (disposition) · **Date:** 2026-08-19

**Findings:** The plan scheduled this for Day 3, to be measured *"while the fix is in the tree"*. **P1 REPLAN'd on Day 1, so no fix is in the tree** and Days 2–3 were re-purposed to P7 (owner decision 2026-08-19). Measuring dinam/indus/turkpow/clearlak unpatched would **restate their current failure, not answer the question** — the same reason Task 4 gave, unchanged.

**What is known, from Day 1's baseline compile of the pool:** all four remain broad rather than bounded — indus **31** errors spanning `$130/$140/$141/$148/$149/$408/$409`, dinam **22**, turkpow **14**, clearlak **8** (GAMS totals, not marker counts). Task 10 rejected all four from the P8 pool on exactly this basis.

**Evidence:** `DAY1_GANGES_CONTROL.md` §6.4; `BACKLOG_CANDIDATE_CATALOG.md` §2.2.

**Decision:** 🔍 **Carries to whichever effort lands a `$149` fix.** **Sprint 38 will not answer it**, and the Day-3 prompt now says so explicitly so it is not attempted against an unpatched tree.
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
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints)
**Date:** 2026-08-17 · **Measured at:** `84fbe43c`

**Findings:** All three materialization sites are intact and all six corpus-safety call sites located. **S1 `constraint_jacobian.py:78`** and **S2 `index_mapping.py:634`** both hold the `enumerate_variable_instances(var_def, model_ir)` call the design targets; **S3** is present in `stationarity.py`. The six call sites are `index_mapping.py:634`, `constraint_jacobian.py:78`, `gradient.py:287`, `gradient.py:453`, `complementarity.py:367`, `complementarity.py:512`.

Drift since the S34 anchor `78ceaead`: `index_mapping.py`, `constraint_jacobian.py`, `gradient.py` and `complementarity.py` are **byte-unchanged**. Only `stationarity.py` moved (+311 — markov +259, fawley +54, less deletions), and its site survived, exactly as Sprint 37 recorded.

Also confirmed: the blow-up is still non-terminating (killed at a 100 s cap, not profiled — Task 5 owns profiling), and **no `sarf_mcp.gms` golden exists**, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason — the gate peculiarity the design records.

**Evidence:** `sed -n '78p' src/ad/constraint_jacobian.py` and `sed -n '634p' src/ad/index_mapping.py` show the target call · `grep -rn enumerate_variable_instances src/` yields exactly 6 non-definition call sites · `git diff --stat 78ceaead..HEAD` per file. See `BASELINE_RECONFIRMATION.md` §4.

**Decision:** ✅ Task 5 can design against the recorded locations without re-tracing. The S37 "one stale precondition" note needs no further correction for Sprint 38.

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
✅ **Status:** VERIFIED — the short-circuit removes differentiation volume, not merely enumeration
**Verified by:** Task 5 (sarf P2 — O(active) Re-Architecture Design Refresh)
**Date:** 2026-08-17 · **Measured at:** `949a4587`

**Findings:** Confirmed **structurally and by measurement**. In `constraint_jacobian.py`'s hot loop the sparsity check is at **variable-name level only** — once a variable is referenced in a row, the loop differentiates w.r.t. **every declared instance**, with no active-column filter. So `differentiate_expr` volume is **directly proportional to declared columns**.

A read-only counter at that exact call site (120 s cap):

```
calls=75000   rows=1 elapsed=20.2s rate=3712/s byvar=[('task', 74994), ('sales', 6)]
calls=250000  rows=1 elapsed=74.8s rate=3343/s byvar=[('task', 249994), ('sales', 6)]
```

Three decisive facts: **`rows=1`** after 75 s and a quarter-million calls (still the *first* constraint row); **~100 % of calls are `task`**; **rate ≈ 3,343/s**. One row costs 369,024 calls ≈ **110 s**.

**Evidence:** the loop at `constraint_jacobian.py:1002–1013`; probe output above; `src/` reverted byte-identical. See `SARF_REARCH_DESIGN.md` §1.

**Decision:** ✅ The premise a 20–28 h atomic build rests on is sound — restricting to 398 active columns removes the volume proportionally (927×). **But see 2.3: this does not by itself reach the pre-registered timing gate.**

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
❌ **Status:** WRONG — the projection is **~141 s**, not single-digit seconds
**Verified by:** Task 5 (sarf P2 — O(active) Re-Architecture Design Refresh)
**Date:** 2026-08-17 · **Measured at:** `949a4587`

**Findings:** The column count is only half the product; the **row** count is the other half, and the short-circuit does not touch it.

Row census derived from the IR: **1,183 rows reference `task`** — `equipb1` 648, `tbal` 384, `equipb2` 120, `labor` 24, `cbal` 6, `acost3` 1. Columns: `task(g,t,mn,mn)` = 16×24×31×31 = **369,024** ✓.

| | differentiations | at the measured 3,343/s |
|---|---|---|
| current | 1,183 × 369,024 = **436,555,392** | **~36.3 hours** |
| O(active) columns | 1,183 × 398 = **470,834** | **~141 seconds** |
| Phase-0 gate (PR20) | — | **single-digit seconds** |

The 36.3-hour figure **explains the non-termination directly** — not a pathological hang, but 436 million differentiations. The short-circuit delivers its full **927×** and still lands **~16× short** of the gate.

**Evidence:** IR-derived row census (`eq.lhs_rhs` walked for `VarRef('task')`, multiplied by `eq.domain` set sizes); measured call rate. See `SARF_REARCH_DESIGN.md` §2.

**Decision:** ❌ **The threshold — not the design — is what fails, and the decision is pre-registered here rather than argued in-sprint.** The KPI is **+1 Translate**: sarf only needs to **complete**, and 141 s does that; the 100 s cap that currently kills it is a *test-harness* cap, not a product requirement. **✅ RESOLVED 2026-08-18 (owner decision): the Phase-0 gate is revised to "sarf completes and produces a byte-stable golden, wall-clock ≤ 300 s on a nightly slot."** `PROJECT_PLAN.md`'s Sprint-38 P2 gate is updated to match, so ~141 s reads as **the accepted result, not a shortfall**. Holding single-digit seconds would require **also gating rows** (1,183 → tens) — scope not in the 20–28 h estimate — and would convert a 927× win into a REPLAN.

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
✅ **Status:** VERIFIED — a corpus-free surrogate is constructible, with a genuine terminating fail-before
**Verified by:** Task 5 (sarf P2)
**Date:** 2026-08-17

**Findings:** sarf cannot be its own fixture (at 369,024 columns the fail-before state does not terminate), but the measured call rate makes a surrogate straightforward to size. At **3,343 calls/s**, a surrogate with **~5,000 declared columns and a handful of rows** costs **~1.5 s un-gated** and is near-instant gated — a genuine, fast fail-before/pass-after.

Four requirements, each traced to a prior failure: **corpus-free** (constructed in-test, not read from `data/gamslib/raw/`, which is absent in CI — a skip-if-absent fixture is **inert** and guards nothing, the S37 Unknown 7.3 refutation); **terminating fail-before**; **same guarded path** (a 4-D variable with a 2-D activity set, so the predicate is exercised rather than just the arithmetic); and **asserts the shape, not only the time** — the emitted `stat_*` must carry **symbolic** multiplier indices (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("'` empty), since a timing-only fixture would pass a wrong-but-fast emit.

**Evidence:** call-rate measurement (2.2); `SARF_REARCH_DESIGN.md` §4.2.

**Decision:** ✅ Sized and specified. The shape assertion is the part that matters — it is what distinguishes this from a benchmark.

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
✅ **Status:** VERIFIED — the scope arithmetic is order-independent; determinism is design-verified
**Verified by:** Task 5 (sarf P2)
**Date:** 2026-08-17 · **Measured at:** `949a4587`

**Findings:** Both P2 (sarf's new golden) and P4 (the 36 presolve goldens) move the corpus, and **the end state does not depend on the order**:

| | discovered | in-scope |
|---|---|---|
| start | 170 | 163 |
| P2 → P4 | 171 → **207** | 164 → **200** |
| P4 → P2 | 206 → **207** | 199 → **200** |

Both orders finish at **207 discovered / 200 in-scope**, so `--min-scope` must end at **207**. The only hazard is an intermediate commit where the assertion lags the corpus — mitigated by each landing raising `--min-scope` **in the same change**, as Task 6 specifies.

**Determinism ×3 is DESIGN-VERIFIED only:** the sarf golden does not exist yet, so `PYTHONHASHSEED {0,1,42}` byte-stability is an in-sprint gate, not a prep result. Recorded as such rather than claimed.

**Evidence:** golden/allowlist inventory (Task 2, re-derived); `SARF_REARCH_DESIGN.md` §4.3.

**Decision:** ✅ No ordering constraint between P2 and P4 on scope grounds. **A separate sequencing dependency does exist:** P2's gate needs Task 3's `--expect-new` / `UNVERIFIABLE` verdict, since `leak-check MODEL=sarf` otherwise reports a misleading `NO-OP` — so **P6b should precede P2's gate run**.

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
✅ **Status:** VERIFIED — the channel was supplied by the owner; **Branch A (SEND) is unblocked**
**Verified by:** Task 7 (Consultation Ownership Decision Package) · **resolved by the owner 2026-08-18**
**Date:** 2026-08-18

**Findings:** The question is answered. **Channel: email.**

| recipient | address |
|---|---|
| Michael Ferris | `ferris@cs.wisc.edu` |
| Steven Dirkse | `steve@gams.com` *or* `sdirkse@gams.com` |

Two addresses were supplied for Dirkse as alternatives without a preference; **the package addresses both**, since a bounce on one is silent and this is a one-shot message after five carries.

**The investigation's reframing proved out.** Task 7 found that the standing description — *"the bundle names no recipient, address, or channel"* — was true of the **bundle** but false of the **project**: Ferris and Dirkse were already named four times in `PROJECT_PLAN.md`, so the gap was **one fact, not two**. That prediction held exactly: the outstanding item was a single address, and it was answered in one message rather than needing research.

**Sprint 39's identical gap is closed too.** Its "Submit and Follow Up" step names the same recipients with no channel; the same email channel serves it, so the problem is resolved rather than relocated.

**Evidence:** owner message 2026-08-18; `CONSULTATION_DECISION_BRIEF.md` §1 and §5 (send package, addresses filled).

**Decision:** ✅ **Branch A (SEND).** The pre-send blocker from 3.3 — the missing toolchain stamp — **has been applied** to `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` §1, so the attachment is correct. **Two human actions remain**, neither performable in this session: (1) send the §5 message (no email capability here), and (2) post §7's tracking comment to **#1462** at send time. The strike wording (§6) is retained unused in case delivery fails.

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
✅ **Status:** VERIFIED — the strike is cheaper than feared for Sprint 39, and more expensive than feared for rocket/fawley
**Verified by:** Task 7 (Consultation Ownership Decision Package)
**Date:** 2026-08-18 · **Measured at:** `6c517315`

**Findings:** The assumption was that striking might invalidate Sprint 39, whose title is *"PATH Author Consultation & Solution Forcing"*. **It does not.**

Sprint 39's consultation component (~8–10 h of 22–28 h) compiles the **Sprint-22 case studies** into a *broader* document; the rocket input **feeds** it as one input. Solution Forcing Strategies (~6–8 h), Remaining Pipeline Fixes (~6–8 h) and the retest (~2 h) are untouched. **Sprint 39 loses an input, not its premise.**

**The real cost sits elsewhere, and it is larger than "a deferred +1".** rocket and fawley have **no other lever**: §4 of the consultation input records the remaining-lever sweep as returning **none** — PATH options exhausted (best INFES 382, MS-5), μ-continuation exhausted (MS-5 every step), multistart superseded (warm-from-optimum already fails), and the division-by-variable reformulation exhausted (MS-5). fawley is the same class — the S36 `--force` survey was **NEGATIVE** across homotopy/multistart/optfile. **Striking makes both +Solve unreachable indefinitely, not merely deferred.** mine is unaffected (0 bucket; the only non-invariant lever is an LP-side reformulation, out of emit scope).

**Evidence:** Sprint 39's component breakdown and effort split in `PROJECT_PLAN.md`; §4 of `ROCKET_PATH_CONSULTATION_INPUT.md`; the S36 `--force` survey result. See `CONSULTATION_DECISION_BRIEF.md` §3.

**Decision:** ✅ Both branches costed. **Strike ⇒ Sprint 39 survives; rocket and fawley are reclassified consultation-gated and unreachable.** Reclassification wording is drafted and applies verbatim (§6).

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
🔶 **Status:** PARTIALLY WRONG — the case reproduces, but the bundle is unstamped
**Verified by:** Task 7 (Consultation Ownership Decision Package)
**Date:** 2026-08-18 · **Measured at:** `6c517315`

**Findings:** The assumption was that the bundle is complete and a reply would be actionable as-is. **The failure state does reproduce** — under **GAMS 54.2.1 / PATH 5.2.01**, rocket, mine and fawley are all `model_infeasible`, the bucket the question describes. The question set, the ruled-out-lever survey and the reproduction commands are all intact.

**But the bundle carries no version stamp at all**, and the corpus was **re-pinned to GAMS 54.2.1 on 2026-08-12** — **nine days after** the input was authored (2026-08-03). Its quoted figures (`INFES 477 → 382`, objective `1.0128`, `nh=10`) come from the **pre-re-pin** toolchain. A recipient attempting to reproduce `382` under 54.2.1 could get a different number and conclude the report is unreliable — a credibility cost on a one-shot external message.

**Fix is one line** in §1 of the input, drafted verbatim in the brief: state the original toolchain and the re-confirmation under 54.2.1. Nothing else in the package is stale.

**Evidence:** per-model `mcp_solve.gams_version` = 54.2.1 and `solver_version` = 5.2.01 for rocket/mine/fawley; `git log` authoring date 2026-08-03 vs the S37 Day-9 re-pin; no version string in either document. See `CONSULTATION_DECISION_BRIEF.md` §4.

**Decision:** 🔶 **Actionable after a one-line version stamp — ✅ APPLIED 2026-08-18** to `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` §1, so the attachment is now correct and sendable. Also recorded: `CONSULTATION_BUNDLE.md`'s single unchecked box **conflates three actions** (*submit rocket · pose the mine question · run the fawley survey*), and **the fawley survey was completed in Sprint 36** (NEGATIVE). A checkbox spanning three actions, one already done, is part of why it was never ticked — **split it on send or strike.**

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
✅ **Status:** VERIFIED
**Verified by:** Task 2 (Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints)
**Date:** 2026-08-17 · **Measured at:** `84fbe43c`

**Findings:** A clean `--only-solve` regenerated **exactly 36** presolve goldens (17 → **53**; discovered 170 → **206**), matching the Sprint-37 Day-9 figures precisely. All 36 models recorded in `BASELINE_RECONFIRMATION.md` §6 for Task 6's review protocol. Run time 607.8 s, inflated by concurrent ganges compiles (S37 measured 445 s unloaded) — **not** a runtime finding.

**Zero bucket moves:** the re-solve changed no `outcome_category` and no `comparison_status` for any of the 219 models; the DB delta was metadata only.

**The scratch-directory mitigation works.** Sprint 37 Day 9's in-repo re-solve plus `git add -A` swept 20 runtime artifacts including `decis.lic`. Running from `/tmp/task2_scratch` produced **zero** repo-root artifacts, verified by `git status` before restoring. The tree was then restored to pristine: DB `git checkout`'d back to md5 `2ed0a42ba6861fd5837399ae88646d76`, the 36 untracked goldens `git clean`'d, scratch directory removed.

**Evidence:** golden count 170 → 206 and presolve 17 → 53 during the run · `git status --porcelain data/gamslib/mcp/` listed exactly 36 `??` entries · per-model DB diff showed 0 moves · post-restore `git status` clean. See `BASELINE_RECONFIRMATION.md` §6.

**Decision:** ✅ All 36 are adoptable on reproducibility grounds. Task 6 inherits the model list and can proceed straight to the per-model *expected-emit* review — which is the harder half, and the one that decides whether the reference set is self-certifying.

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
❌ **Status:** WRONG — 14 of the 36 would pin an emit that does not reproduce its NLP solution
**Verified by:** Task 6 (Presolve-Golden Adoption Plan)
**Date:** 2026-08-18 · **Measured at:** `cc8acf6c`

**Findings:** The assumption was that each of the 36 could be reviewed against its model's expected presolve emit and adopted. **Reviewing them split the set in two**, and the second half is exactly the hazard this unknown was written to catch.

**Tier 1 — 22 models where the presolve path is load-bearing for a match** (`model_optimal_presolve` **+ match**): catmix, cpack, etamac, harker, hhfair, himmel16, irscge, like, lrgcge, marco, mathopt1, mathopt4, maxmin, mingamma, moncge, paperco, qsambal, sambal, stdcge, tforss, weapons, worst. The presolve emit *produces the recorded match*, so a golden guards something the KPI depends on.

**Tier 2 — 14 models with a presolve golden but no presolve match:** 7 **`mismatch`** (china, circle, imsl, lmp2, prodsp2, spatequ, trig) whose emit demonstrably does **not** reproduce the NLP solution; 6 **`skipped`** (aircraft, apl1p, apl1pca, ps10_s_mn, ps5_s_mn, senstran) never compared at all; and **`mine`**, which is **`model_infeasible`** — a presolve golden for a model that does not solve.

Pinning a wrong-but-stable emit is *defensible* as drift detection, but it carries a real cost: **when someone later fixes `circle`'s presolve emit the gate flags it as drift**, and the reflex is `make regen-goldens` — the laundering path the leak gate exists to prevent.

**Evidence:** the 36 cross-referenced against `outcome_category` + `comparison_status` in the DB; the existing 17 are a different population (dominated by presolve-match models). See `PRESOLVE_GOLDEN_ADOPTION_PLAN.md` §1–§2.

**Decision:** ❌ **Do not adopt wholesale. Adopt Tier 1 (22) in Sprint 38; put Tier 2 (14) behind a per-model sign-off, defaulting to defer.** That takes in-scope 163 → **185** and closes most of the asymmetry (presolve 17 → 39, ratio 9.0:1 → 3.9:1) without pinning known-wrong emits. The review protocol is specified in §2, with exclusions recorded in the **allowlist** — next to the mechanism rather than in a planning doc.

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
✅ **Status:** VERIFIED — comfortable headroom, **and the local measurement was a trap**
**Verified by:** Task 6 (Presolve-Golden Adoption Plan)
**Date:** 2026-08-18 · **Measured at:** `cc8acf6c`

**Findings:** The measurement that matters is **CI, not the dev machine**, and they disagree by ~2×.

| | at 163 in-scope |
|---|---|
| local (3 workers, quiet) | **1578.9 s = 26.3 min** |
| **CI** (`ubuntu-latest`, 3 workers) | **11.9 – 12.9 min** (29 real sweeps) |

The CI job's budget is **`timeout-minutes: 25`**. **Extrapolating from the local number would have produced a false alarm** — 26.3 min → ~32 min projected → "adoption blocks every PR", since golden-staleness is a **required status check**. That conclusion would have been wrong.

Projection (the `--all` corpus download ~1 min is fixed; only the sweep scales by 199/163 = 1.22×):

| scope | typical | worst observed | budget used | headroom |
|---|---|---|---|---|
| 163 today | 11.9 min | 12.9 min | 52 % | 12.1 min |
| **199** | **14.3 min** | **15.5 min** | **62 %** | **9.5 min** |
| 185 (Tier 1) | ~13.0 min | ~14.1 min | ~56 % | ~10.9 min |

**0 timeouts expected at the 3-worker default.** Per-golden timeout risk comes from slow-emit models, and **none of the known slow-emit class (ganges, gangesx, clearlak, turkpow, dinam) is among the 36**; the allowlist already carries that tail. No mitigation needed.

**Evidence:** `/usr/bin/time -p make check-goldens` locally; `gh run list --workflow="Golden Staleness Check" --limit 60` for real CI durations — the ~0.1-min runs are the **skip path** (the "Decide whether to run" gate), only the 29 runs over 5 minutes are real sweeps. See `PRESOLVE_GOLDEN_ADOPTION_PLAN.md` §3.

**Decision:** ✅ Adoption is safe on runtime. **One follow-up recorded:** at 199 the job uses **62 % of a 25-minute budget** and the corpus only grows — **raise `timeout-minutes` or split the sweep before scope exceeds ~250**, rather than discovering it when a required check starts timing out.

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
✅ **Status:** VERIFIED — derive it, but only from an independent source
**Verified by:** Task 6 (Presolve-Golden Adoption Plan)
**Date:** 2026-08-18 · **Measured at:** `cc8acf6c`

**Findings:** `--min-scope` is compared against the **pre-narrowing discovery count**, which is the property that lets it catch an under-provisioned corpus (`discover_goldens()` silently drops any golden whose raw source is absent). Adoption moves discovered 170 → **206** (both tiers) or **192** (Tier 1), so the hard-coded `170` would under-guard the moment the goldens land.

**Deriving the value is right — but the obvious source makes the check vacuous:**

| candidate | verdict |
|---|---|
| filesystem `ls data/gamslib/mcp/*_mcp*.gms` | ❌ **vacuous** — the same quantity `discover_goldens()` starts from, so the assertion compares a number to itself and always passes. **The self-certification defect this task is about, reappearing inside the guard.** |
| **`git ls-files data/gamslib/mcp/*.gms`** | ✅ **independent** — the git index knows how many goldens are *committed* regardless of raw-source provisioning, which is exactly the failure mode `--min-scope` exists to catch |

Both currently report **170**, so the substitution is verifiable as a no-op *before* the goldens land.

**Evidence:** the `--min-scope` help text and its comparison point in `check_golden_staleness.py`; both counts measured at 170. See `PRESOLVE_GOLDEN_ADOPTION_PLAN.md` §4.

**Decision:** ✅ **Replace the literal with a value derived from `git ls-files`**, so the floor tracks the corpus automatically and the "raise it in the same change" discipline becomes unnecessary. If deferred, the literal must move **170 → 192** (Tier 1) in the adoption commit itself. Applied atomically either way.

---

# Category 5: camcge Epic-5 Scoping + turkey Testbed

## Unknown 5.1: Is a licensed >1000-row GAMS-54 environment obtainable at all?

### Priority
**High** — turkey's +1 has been carried as "pending a testbed" since Sprint 35 and was already refuted once in Sprint 37 prep. Carrying it again without an answer inflates the projection (4–8h).

### Assumption
Either a licensed environment can be procured (with a cost and a date), or turkey's +1 must be reclassified as **blocked** rather than pending.

### Research Questions
1. Is a GAMS license covering >1000 nonlinear rows obtainable, at what cost, and on what timeline?
2. Are there alternatives — an academic license, a hosted runner, a time-limited evaluation?
3. Could turkey be verified another way (a reduced instance that preserves the failure mode)?
4. What exactly would the license buy: turkey alone, or other license-gated work as well?
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
🔶 **Status:** PARTIALLY WRONG — the unknown asked about **turkey**; the real subject is a **10-model cohort**
**Verified by:** Task 8 · **scope corrected by the owner 2026-08-18**
**Date:** 2026-08-18 · **Measured at:** `860b0e7b`

**Findings:** This unknown, and Task 8's first draft, treated turkey as a single model needing a testbed. **It is one of ten**, and singling it out would have left nine unexamined.

| property | value |
|---|---|
| **Cohort (10)** | `egypt` · `ferts` · `glider` · `robot` · `shale` · `sroute` · `srpchase` · `tabora` · `tfordy` · `turkey` |
| Share | **10 of 142 convex candidates (7 %)** |
| Signature | all `path_solve_license`, all `not_tested`, all **`solver_version: None`** — rejected at *generation*, PATH never invoked |
| **Emit** | **all ten have committed goldens** — translate succeeded; only the solve is blocked |

**The shared signature is exact, so this is one license problem rather than ten model problems.** Ceiling: **Solve 108 → 118**, and **one license unlocks all ten as a batch** — a single `--only-solve` pass once capacity exists.

**The procurement question is answered in principle: a license is being actively pursued** (the owner is raising capacity with Dirkse and Ferris). So the earlier draft's recommendation — reclassify turkey as *blocked* — was **wrong on both counts**: wrong scope (one model, not ten) and wrong status ("blocked" misstates an active pursuit).

**Evidence:** DB census of `path_solve_license` (10 models, all `solver_version: None`, all GAMS 54.2.1); golden presence verified for all ten; `gamslice.txt` → `GAMS_Demo`. See `CAMCGE_EPIC5_HANDOFF.md` §4.

**Decision:** 🔶 **Classification: `license-gated`, applied uniformly to all ten.** (1) **Excluded from KPI projections** — this is the phantom-upside failure mode turkey exhibited across S35–S37; (2) **not written off**, since a license is being pursued; (3) **tracked as a named cohort with its ceiling stated (+10 Solve)**, so the license's value is visible; (4) **re-tested as one batch** on capacity. **A reduced instance cannot substitute for any member** — the KPI requires the model itself to solve and match. **Convergence worth using:** the license ask and the P3 consultation go to the **same people**, so the two conversations can be one, with *"10 models, 7 % of our corpus, blocked only by the 1000-row demo limit"* as a concrete ask.

### Close — Sprint 38 Day 11 (2026-08-25)

🔒 **CLOSED as a tracked procurement item.** No engineering result closes this unknown, and none was sought: the block is capacity, the pursuit is live, and the cohort record (`CAMCGE_EPIC5_HANDOFF.md` §4) is now the standing wording wherever these models are projected.

**Two amendments from the same day's P8 work, both measured:**

1. **The cohort is 11.** `tricp` joins it. Sprint 38 Day 11 fixed #1062 (a stationarity head domain collapsed onto the diagonal by a repeated set symbol); removing the collapse takes tricp's MCP from **387 rows to 1,255**, past the demo limit. Classified by `scripts/gamslib/test_solve.py`: `path_solve_terminated` → **`path_solve_license`**. tricp is `likely_convex`, so it is inside the 142. **Ceiling is +11 Solve against the then-current Solve, as one batch.**
2. **"All ten have committed goldens" is not the same claim as "all ten emit correctly", and only the first was ever true.** `ferts` is the *other* model carrying #1062's defect. Its `stat_xi` body emitted conjunctions of the form `sameas(i,'assiout') and sameas(i,'aswan')` — **identically false**, silently dropping every off-diagonal `_fx_` multiplier term. Nothing caught it, because **no cohort member's emit has ever been exercised by a solve**. A license buys not only ten solve attempts but the first real test of ten goldens.

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
❌ **Status:** WRONG — the handoff was **already written**; three narrow gaps, not a document
**Verified by:** Task 8 (camcge Epic-5 Handoff + turkey Testbed Determination)
**Date:** 2026-08-18 · **Measured at:** `860b0e7b`

**Findings:** The assumption was that the Epic-5 handoff needed assembling from the S32–S37 refutation history. **It did not.** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` already carried every substantive item — price-pin → MS-4 (×4), single-dual-pin → MS-4 (×2), drop-row → corrupt @ omega 299 (×4), the **two-nullspaces** diagnosis, the three-part formulation (×3), 191.7346 (×7), 641 rows, per-model numéraire generality, a `⚠ SUPERSEDED IN PART` banner on §3, and **§5 Q3 marked ✅ ANSWERED — NO with an explicit "Do not re-run this experiment."**

**Writing a second document would have duplicated ~90 % of it and created a second artifact to keep in sync.**

**The three real gaps, all now fixed in the scoping doc itself:**

1. emit time recorded as **18 s**; the S37 Day-10 control measured **19 s**
2. **zero mentions of GAMS 54.2.1** — every figure predated the re-pin with no toolchain attribution
3. no **consolidated BANNED list** — the bans were correct but spread through prose, so a reader skimming for *"what must I not do"* had to reconstruct them

**Gap 2 is the second occurrence of the same defect in one prep cycle** — Task 7 found an unstamped consultation bundle whose figures predated the same re-pin. Measurements written before a toolchain change, carrying no version attribution, is now a recognised pattern rather than an isolated slip.

**Evidence:** per-item grep census of the scoping doc; `CAMCGE_EPIC5_HANDOFF.md` §1.

**Decision:** ❌ **Do not write a parallel handoff.** The scoping doc is patched in place (stamp, 19 s, new §4a BANNED list with per-sprint attribution), and `CAMCGE_EPIC5_HANDOFF.md` records the audit and the turkey determination rather than restating the diagnosis. **B1 (drop-row) is flagged as *primal-correct*** — a reader checking only the primal concludes it works, and the failure is silent in the dual.

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
✅ **Status:** VERIFIED — still the right recommendation, and now stamped under v54
**Verified by:** Task 8 (camcge Epic-5 Handoff + turkey Testbed Determination)
**Date:** 2026-08-18 · **Measured at:** `860b0e7b`

**Findings:** Nothing since Sprint 32 has changed the two-nullspaces analysis, and the **Sprint-37 Day-10 control reproduced every predicted figure under GAMS 54.2.1 / PATH 5.2.01**: emit **19 s**, **641 single equations / 641 variables**, embedded NLP **MS-2 @ omega 191.7346**, `mcp_model` **MS-4 Infeasible**.

**The MCP is MS-4 against a *correct* NLP optimum** — structural rank-deficiency, **not an emit defect**. That distinction is what keeps camcge in Epic 5 rather than the emit backlog, and it survives the toolchain change.

**What the per-model-numéraire fallback buys:** a *selection* on the price ray rather than a perturbation, reproducing the documented optimum exactly. **What it does not buy:** closure of the **row-redundancy nullspace** — that is the three-part formulation's part (3), and it is the actual Epic-5 research. Recommending the fallback is therefore recommending a *partial* remedy knowingly, which the scoping doc now states rather than implies.

**Evidence:** S37 Day-10 control figures vs the Task-9 predictions; the two-nullspaces diagnosis in `CGE_DEGENERACY_SCOPING.md` §3 and the new §4a.

**Decision:** ✅ Unchanged and re-confirmed. The recommendation now carries its toolchain stamp, so the next reader does not have to ask whether it predates the re-pin — the question Task 7 and Task 8 both had to answer the hard way.

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
✅ **Status:** VERIFIED — both modes reproduce live, both now assert scope, **both exit non-zero**
**Verified by:** Sprint 38 Day 4 (P6b) · **Date:** 2026-08-19 · **Measured at:** `e34b0d5c`

**Findings:** Both narrowing modes were reproduced against the shipped code, then fixed with **fail-before/pass-after tests** — the fail-before run is the evidence this unknown asked for.

**Mode 1 — `--resolve-changed` (the Sprint-37 false GO): CONFIRMED, and worse than recorded.** The pre-fix code returned `{"verdict": "GO", "note": "no emit goldens changed since …"}` and **exited 0** on an empty selection — a checkpoint that measured *zero models* certifying the tree. Two separate defects, now both guarded:

| defect | assertion added |
|---|---|
| empty selection reads as health | **error + exit 1**; `--allow-empty` is the explicit opt-in, and the GO it produces carries *"This certifies nothing"* in its own note |
| selection is `git diff <since>..HEAD`, so **uncommitted goldens are invisible by construction** | `_uncommitted_golden_model_ids()` refuses the run and names them; checked **independently of** whether the committed selection is empty, because the dangerous shape is a plausible-looking GO over the wrong set |
| silent narrowing | `--min-scope N` (a floor, not an equality) |

**Mode 2 — `leak-check` NO-OP: the earlier reading was right, and incomplete.** Task 3 found `leak-check` already exits 2, so its NO-OP is *not* mistakable for a pass — **that holds**, and the defect is the message. But the message is worse than "misleading": `NO-OP: … the fix did not change the emit` is a **correctness claim about the emit**, asserted for `sarf` on a run that **never compared sarf** (it has no golden). It sends an engineer to debug an emit that was never swept.

**Fixed by splitting the cause into three classes** via a new shipped function `classify_missing_expected()`: **`NO-GOLDEN`** (not in the corpus — never compared), **`ALLOWLISTED`** (has a golden, deliberately skipped), **`NO-OP`** (compared, byte-identical — the genuine case). All three still fail the gate; they no longer claim the same thing. A test asserts the three **partition** `missing`, so nothing falls through unreported.

**A defect in this task's own test suite, found and fixed.** The mode-2 tests initially used a **local mirror** of the classification and therefore **passed against the pre-fix code** — proving only that two copies of the logic agreed. That is the *"verify a component, assert a system property"* failure this very priority exists to catch, reproduced inside its own regression test. The logic was extracted into `classify_missing_expected()` and the tests now import the **shipped** function; the fail-before count rose **8 → 12**.

**Evidence:** fail-before = 12 failed / 10 passed with `src` reverted and tests present; pass-after = **22 passed**. Live exit codes: empty selection **1**, `--allow-empty` **0**, `leak-check --expect-drift sarf` **1**. Full gate green (typecheck / format / lint / **5068 tests**).

**Decision:** ✅ Both modes now **assert their scope and fail loudly**. Day 7's P2 gate will read `NO-GOLDEN` for sarf instead of a false correctness claim, and Day 9's re-anchor cannot pass by measuring nothing.
---

## Unknown 6.2: Can a provenance file reproduce the genuine floor of 76 exactly?

> **⚠ Task 2 input (2026-08-17):** the target may not be 76. Three models in the documented provenance chain (`ps2_f_s`, `ps2_s`, `ps3_s_gic`) are `non_convex` and outside the 142-candidate corpus, and only **14 of the 76** are attributable by name at all — the rest come from an unnamed "S28 genuine 68" block with no per-model record. **Resolve the target figure before building the tracker.** See `BASELINE_RECONFIRMATION.md` §2.

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
❌ **Status:** WRONG — the floor cannot be reproduced from existing artifacts, at 76 or any figure
**Verified by:** Task 3 (Measurement-Integrity Design)
**Date:** 2026-08-17 · **Measured at:** `1a252648`

**Findings:** Three independent derivations give **three different answers**:

| method | result | why it fails |
|---|---|---|
| mechanical `Match − (presolve ∧ match)` | **65** | drops the "a fix changed the cold emit" limb |
| golden-changed-ever (git log per golden) | **93** | 28 of 29 presolve goldens have >1 commit — regeneration happens for many reasons unrelated to a correctness fix |
| the documented provenance chain | **76** | credits 3 **out-of-corpus** models (Task 2); only **14 of 76** attributable by name; ~62 sit in an unnamed "S28 genuine 68" block with no per-model record |

The middle row is this task's new evidence and it is decisive: *"did the golden change?"* is mechanical, but *"did a **real fix** change it **for this model's correctness**?"* is a **judgement**, and no repo artifact records it.

**Evidence:** per-golden `git log` over all 29 in-corpus presolve+match models → 28 with >1 commit (65 + 28 = 93) · mechanical count 65 · documented chain 76. See `MEASUREMENT_INTEGRITY_DESIGN.md` §4.

**Decision:** ❌ **A reconstructing tracker is impossible; an append-only one is straightforward.** Design changed to `floor = baseline.count + len(entries)`, where the baseline is an **opaque, declared** block and every future movement adds an entry with its evidence. The tracker asserts against a committed `expected_floor` and **exits non-zero on divergence**, never emitting a DB-derived figure (that path gives 65 and looks authoritative). **✅ RESOLVED 2026-08-18 (owner decision): `baseline.count = 73`** — the in-corpus reading. The historical 76 credited three `non_convex`, out-of-corpus models, so **the S31–S37 series was overstated by 3** and Sprint 37's advance re-reads as **72 → 73**. **P6c owns re-baselining the downstream reports** (Rolling-KPIs column, footnote ⁸, `SUMMARY.md` row 37, memory); historical CHANGELOG and per-sprint close docs are **left as written**, since rewriting them would destroy the evidence this decision rests on.

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
✅ **Status:** VERIFIED — conditional on 6b landing first
**Verified by:** Task 3 (Measurement-Integrity Design)
**Date:** 2026-08-17 · **Measured at:** `1a252648`

**Findings:** `8cffec29` (the S37 close) is the correct re-anchor. Selections measured:

| anchor | selects |
|---|---|
| `78ceaead` (S34 close — current, 4 sprints old) | **19** models |
| `935d94b7` (S36 close) | 2 |
| **`8cffec29` (S37 close — candidate)** | **0** |

DB-modifying commits: `78ceaead..HEAD` = 3, `8cffec29..HEAD` = 0.

**But the candidate selects zero — which is exactly the hazard 6b addresses.** Re-anchoring today makes the checkpoint **vacuous at sprint start**: it would report GO while checking nothing. That is *semantically correct* (nothing has drifted) but *operationally dangerous* under current code, which cannot distinguish "nothing changed" from "I looked in the wrong place".

**Evidence:** `_changed_golden_model_ids()` at each anchor · `git log --oneline <anchor>..HEAD -- data/gamslib/gamslib_status.json`. See `MEASUREMENT_INTEGRITY_DESIGN.md` §5.

**Decision:** ✅ Re-anchor to `8cffec29`, **but only after 6b lands** — sequencing 6d before 6b trades a slow checkpoint for a silent one. **Cost:** the S34–S37 drift (19 models) stops being re-verified every run; that drift is already settled at each sprint's close, so the cost is re-verification of history, not loss of signal.

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
✅ **Status:** VERIFIED — four legitimate states enumerated, all expressible
**Verified by:** Task 3 (Measurement-Integrity Design)
**Date:** 2026-08-17 · **Measured at:** `1a252648`

**Findings:** Four legitimate states would be broken by a naive assertion, and each has a design response:

1. **Empty selection at sprint start** — the *normal* state right after re-anchoring (6.3 measured `8cffec29` → 0 models). A naive "fail on empty" would fail every run until the first golden lands. ⇒ `GO (VACUOUS)` at exit 0, distinguished by a **clean working tree**; only empty-selection-**with-dirty-goldens** fails.
2. **A golden-less model in `--expect-drift`** — sarf, legitimately, until its re-arch lands. ⇒ distinct `UNVERIFIABLE` verdict plus a `--expect-new` flag, rather than a hard fail that invites a blanket bypass.
3. **Docs-only PRs** — must not trip a required check. ⇒ scope assertions apply only when `--expect-drift`/`--since-commit` is given.
4. **Deliberately narrowed local sweeps** (`--models`) — **already handled**: `subset_scope` downgrades the claim to `PARTIAL` rather than failing.

**Escape-hatch policy:** any bypass must **print its caveat into the verdict line**, as `subset_scope` already does (`LEAK GATE PASS (PARTIAL — NOT a full-corpus leak claim)`). A bypass leaving no trace in the pasted evidence is how a gate quietly stops being one. Over-use is countable in CI, per the `skip-phase0` precedent.

**Evidence:** state 4's existing handling at `check_golden_staleness.py:333` (`subset_scope` warning) and the `claim_caveats` verdict path. See `MEASUREMENT_INTEGRITY_DESIGN.md` §6.

**Decision:** ✅ No assertion in the design fires on a legitimate state. The riskiest is state 1, which is *guaranteed* to occur immediately after 6d — so it is handled by construction rather than discovered in the sprint.

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
✅ **Status:** VERIFIED — **43 open issues lack a gate; the problem is current, not historical**
**Verified by:** Task 9 (Phase-0 Compliance Survey)
**Date:** 2026-08-18 · **Measured at:** `fd3ec910`

**Findings:** Census run using the gate script's **own** functions (`phase0_subsections`, `missing_subsections`), so the classification matches what CI would decide rather than an approximation.

| | compliant | **no gate** | total |
|---|---|---|---|
| **OPEN** | 19 | **43** | 62 |
| CLOSED | 3 | 13 | 16 |
| unknown | 2 | 0 | 2 |
| **total** | 24 | 56 | **80** |

**Two structural findings:**

1. **The problem is current.** 43 of 56 un-gated docs are **open** — **69 % of the open backlog**. Only 13 are closed, so this is not a legacy artifact that stopped accruing.
2. **Compliance is binary — zero partial gates.** Every doc has either all four canonical subsections or no Phase-0 heading at all. **Measured as a three-way classification** (`COMPLETE` / `PARTIAL` / `NO-GATE`, naming every partial found): **`{'NO-GATE': 56, 'COMPLETE': 24}`**, `PARTIAL` absent — a two-way split would have folded partials into the un-gated count and left the claim uncheckable. **Nobody has ever written half a gate.** The backfill is therefore "write one", not "audit and complete", and the count is exact rather than a judgement call.

**Rule C confirmed in practice:** extras are permitted and used — `ISSUE_1110` carries eight subsections, `ISSUE_1289` **seven** (six as surveyed, plus the `Prerequisite` 7.2 adds). **The script agreed with a manual read on every doc inspected**; no false positives or negatives.

**Evidence:** the census script (reproduction in `PHASE0_COMPLIANCE_CATALOG.md` §5); `gh issue list --state all --limit 400`.

**Decision:** ✅ **P7 is under-budgeted at 8–10 h against 43 issues** — roughly 12 minutes each, not credible for a gate requiring a hand-derived KKT shape and a verification methodology. **Realistic sprint scope: Tier 1 (11 P8-pool issues), probably its twocge/elec core (6).** The catalog is ordered so P7 works top-down and stops at budget; **the remaining 32 are a standing backlog item to be reported, not quietly dropped.** Tier 2 (4 license-gated) is deliberately deprioritised — a gate on a model that cannot be solve-verified cannot be exercised. Tier 3 includes several **effective duplicates** whose working gate lives in a different compliant doc (`sarf` #885 vs `ISSUE_1385`; `ganges` #929/#930 vs `ISSUE_1667`), so triage precedes writing.

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
✅ **Status:** VERIFIED — the gate is complete, and **two defects in it were found and fixed**
**Verified by:** Task 9 (Phase-0 Compliance Survey)
**Date:** 2026-08-18 · **Measured at:** `fd3ec910`

**Findings:** `ISSUE_1289`'s gate is **structurally complete** — all four canonical subsections plus `Bucket / KPI` and `Regression guard`, **six as surveyed**; it passes the script. **The `Prerequisite` fix below takes it to seven**, re-checked at 0 missing. It carries the **`ac(i+2,r)`** match-correctness risk and the 6th blocker (embedded `ganges0` **MS-5 @ −386785.5017** vs standalone **MS-2 @ 6395.5444**), correctly framing the fix as **0-bucket**.

**Two things were wrong:**

1. **A stale KPI assertion** — it read *"Solve stays 108, Match stays 93"*. **Match has been 94 since the Sprint-37 Day-9 GAMS-54 re-baseline.** A gate asserting an outdated KPI would fail its own acceptance check. Corrected, with the reason recorded inline.
2. **The cascade prerequisite was absent** — this unknown asks whether the gate records that `$66` is reachable only after the cascade lands. It did not. A **Prerequisite** section now states it, including Task 4's finding that **#1668 direction 2 is not implementable at the rebind site**, so the gate cannot be exercised until a replacement direction lands. **`$66` must not be budgeted as independently schedulable.**

**A correction to this task's own reasoning, recorded because the inference was wrong.** I justified the fix on the grounds that #1289 was an *open* live specification. **It is CLOSED** — and **#1111, which I assumed closed because fawley landed, is OPEN** (it is a broader AD-engine issue; the fawley landing is recorded *within* it). The edit stands on its merits, but **open/closed does not map onto pending/landed** the way I assumed, and any future audit keying on issue state should not make that inference.

**Same pattern checked elsewhere:** `ISSUE_1110` (CLOSED, markov) records *"genuine floor 75 → 76"* — correct when written, a historical record of a landed fix, **left as written**. `ISSUE_1111` carries no KPI assertion. **The stale-figure problem is confined to the one doc.**

**Evidence:** `phase0_subsections(ISSUE_1289)` → **6 subsections, 0 missing as surveyed; 7 and 0 missing after the `Prerequisite` fix**; the corrected lines; `gh issue view` states for #1110/#1111/#1289.

**Decision:** ✅ `$66`'s gate is complete and now accurate. **But #1289 being closed while `$66` is undone means issue state is not a reliable proxy for work state in this repo** — worth knowing before any future automation keys on it.

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
✅ **Status:** VERIFIED — **5 eligible on the pre-registered rule (threshold 2). But 0 eligible today: none has a Phase-0 gate, so P7 gates P8.**
**Verified by:** Task 10 (Backlog Candidate Catalog)
**Date:** 2026-08-18 · **Measured at:** `32a839d5` · **Toolchain:** GAMS 54.2.1 / PATH 5.2.01

**Findings:** The pool is **17 models, 6 deep-track ⇒ 11 candidates**. **All 11 have committed goldens** — emit succeeds for every one, so every failure is at GAMS-compile, GAMS-execution or PATH stage, never at translate.

**Five satisfy the rule (reproduced fingerprint AND named fix surface):**

| model | reproduced fingerprint | terminal state | fix surface |
|---|---|---|---|
| **twocge** | 8 × empty-equation-unfixed over 2 pairs (`eqpw.nu_eqpw`, `eqw.nu_eqw`) | `ABORTED, EXECERROR = 8` | **#1331**, names both |
| **tricp** | 108 × `Unmatched variable not free or fixed` | `ABORTED, EXECERROR = 108` | **#1062** |
| **elec** | div-by-zero at lines 99/100/101 → 30 × `Evaluation error(s) in equation "stat_x(iN)"` | `ABORTED, EXECERROR = 3` | **#983 / #1325** |
| **dyncge** | 4 × empty-equation-unfixed on `eqpf2.nu_eqpf2` | `ABORTED, EXECERROR = 4` | #1331's mechanism, **no own doc** |
| **lnts** | **NEW** — `y.lo = y.up = 0` at `('y2','h50')`/`('y3','h50')` while `y_fx_*` equations demand **5** and **45** | **MS-4 at ITERATION COUNT 0** | pruned-instance `.fx` zeroing in `emit_gams.py`, **no own doc** |

**Rejected (6), with reasons:** **agreste** — new diagnosis (MS-5 after 9,734 iterations; *banked as the highest-value item* — an **LP**, `verified_convex`, NLP MS-1 @ 17706.43, and a *locally* infeasible LCP is structurally odd); **cesam** — new diagnosis (MS-4 at 0 iterations, the same signature as lnts, so it was **checked not assumed**: **0 `_fx_` equations**, so lnts's mechanism cannot apply); **indus** — 31 errors spanning `$130/$140/$141/$148/$149/$408/$409`, broad not bounded; **dinam** — 22 errors, and **1.5 directs treating the `$149` family as untested, not pending-unblock**; **turkpow**, **clearlak** — structurally excluded by the pre-registered exclusions.

**Two findings the DB does not show.** (1) **Its category names mislead on 4 of 11:** `path_solve_terminated` reads as *"PATH gave up"*, but dyncge/elec/tricp/twocge all carry `solver_version: None` and abort at **GAMS execution before PATH is invoked** — they are emit defects, not solver-tuning work. (2) **5 of 11 have no owning issue doc at all** (agreste, cesam, lnts, dyncge, indus), and their DB messages are the generic `Parse error: compilation_error` / `no_solve_summary` / `Model: Infeasible (status 4)` — **no fingerprint whatsoever**, so each had to be reproduced from scratch.

**Evidence:** `BACKLOG_CANDIDATE_CATALOG.md` §1–§3; per-model `.lst` runs from a scratch directory; the lnts runtime bound probe.

**Decision:** ✅ **P8 clears its threshold with room — but P7 is its prerequisite, which neither priority currently states.** **Task 9's Tier 1 needs correcting in both directions:** clearlak #1291 and turkpow #1316 are **structurally excluded** from P8 and should drop out of Tier-1 priority, while **dyncge and lnts are missing entirely** and need a doc *created*, not merely gated. **Recommended P7 order = P8's shortlist:** #1331 → #1062 → #983/#1325 → dyncge (new doc) → lnts (new doc). **Worth stating honestly:** all five are Translate-stable and Solve-uncertain, with **Match unclaimed** — P8 is a slack absorber, not a KPI projection, consistent with Sprint 38 being deliberately not floor-targeted.

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
✅ **Status:** VERIFIED — **yes, and the rule as written admits them.** Criterion derived from **three** false positives this task produced, one of them **83 % wrong**
**Verified by:** Task 10 (Backlog Candidate Catalog)
**Date:** 2026-08-18 · **Measured at:** `32a839d5`

**Findings:** The assumption was right and the guard was missing. *"Reproduced fingerprint"* is **silent on what counts as reproduction**, and every trap below satisfies a plain reading of it. All three were produced *inside this task*, which is why the criterion is concrete rather than a slogan.

**(a) A grep that matched the emitter's own comment.** `grep -c 'division by zero'` returns **1** for dyncge, twocge and tricp — none of which has such an error. The hit is a **comment in the generated MCP source** (`* Initialize variables to avoid division by zero during model generation.`). **A `.lst` contains the echoed source as well as the diagnostics**, so an unanchored search over it reads the model's own text as evidence about its behaviour.

**(b) A structural pattern that is wrong 5 times in 6.** Sizing lnts's defect by scanning for the co-occurrence (a variable with **both** a `_fx_` equation and a blanket pruned zeroing) matches **6 models — lnts plus catmix, otpop, springchain, ganges, gangesx. Five of them solve fine.** Tightening to *"nonzero `_fx_` RHS"* does **not** help: catmix (1), otpop (29.4) and springchain (2) all still match. **The discriminator is whether the pruning guard actually covers the fixed tuple — a runtime property of `ord`/`card` against the model's own set sizes, unreadable from source.** Negative control: probing otpop shows `x.lo` unset at `1974`, `x.up = 32.25`, never zeroed, **MS-1 Optimal**.

**(c) Marker counting undercounts even with no truncation.** clearlak **8** errors vs 5 printed marker lines; dinam **22** vs 9; indus **31** vs 25; turkpow **14** vs 5 — **all with zero truncation notices**. This generalises Task 2's `$141` retraction: that was attributed to listing *truncation*, but marker counting is wrong **even when nothing is truncated**, because one printed line can carry several codes.

**The operational criterion — a fingerprint is REPRODUCED only if all four hold:**

1. **The evidence is a GAMS diagnostic, not echoed source** — match anchored `^\*\*\*\*` lines (trap a).
2. **A terminal state is asserted** — `MODEL STATUS n`, `SOLVE ... ABORTED, EXECERROR = n`, or `**** N ERROR(S)` **read from GAMS's own line**, never a marker or line count (trap c).
3. **The mechanism is observed, not inferred from structure** — where the defect is a runtime property (a guard firing, a bound collapsing), **probe it at runtime** (`display var.lo, var.up` before the solve). A source pattern is a hypothesis to test (trap b).
4. **A negative control passes** — at least one model matching the pattern but *not* exhibiting the defect is probed and shown clean. Without it, an 83 %-wrong pattern looks like a finding.

**Evidence:** `BACKLOG_CANDIDATE_CATALOG.md` §4; the otpop control probe; the four-model marker-vs-total table.

**Decision:** ✅ **Amend the rule with the four criteria.** Every catalog entry carries its reproduction command, and each was **run for this catalog** rather than quoted from a prior sprint — which is what the S37 Day-0 `$141` false positive (`_expr_contains_varref_attribute`, actually from `25feacd3`, an unrelated cesam fix) would have required to be caught at the time.

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
