# Sprint 27 Priority 7 Fix-Surface Analysis: #1387 cclinpts + #1388 camshape

**Status:** ✅ COMPLETE (Day 0 prep — fix surfaces mapped; implementation lands Sprint 27 Day 1/2 per Task 11 schedule; #1388 binding verdict pending Day 0/1 NLP-warm-start runtime test per Phase 0 PROCEED-with-condition signal)
**Date:** 2026-05-28
**Owner:** Prep Task 8
**Inputs:** `docs/issues/ISSUE_1387_*.md` §"Phase 0 Acceptance Gate" (Sprint 27 Prep Task 2 / PR #1403); `docs/issues/ISSUE_1388_*.md` §"Phase 0 Acceptance Gate" (same); `data/gamslib/mcp/cclinpts_mcp.gms:133-134` (current emit); `data/gamslib/mcp/camshape_mcp.gms:428` (current emit); `data/gamslib/gamslib_status.json` Sprint 27 Day 0 baseline buckets; Sprint 26 retrospective §"Sprint 27 Recommendations" §"Priority 7".

---

## 1. Purpose

This document is the Sprint 27 Day 0 fix-surface analysis for **Priority 7** (the Sprint 26 "Day 6 close-and-refile" carryforwards): **#1387 cclinpts** (~100% relative-difference solve mismatch — Day 0 baseline shows `rel_diff=1.0`; per Phase 0 prep, originally documented at ~70% rel_diff) and **#1388 camshape** (PATH `model_infeasible` despite NLP-feasible). It records, for each issue:

- The **Phase 0 target shape** (cross-referenced from the Sprint 27 Prep Task 2 issue-doc Phase 0 Acceptance Gate sections).
- A **current-emit-vs-target comparison** identifying the bug class.
- **Source-code patch sites** at `file:line` precision (Sprint 27 fix path) OR the **fundamental-property classification** (Sprint 28 carryforward path).
- An **implementation effort estimate** vs Priority 7's combined 6–12h budget.
- A **per-issue verdict** (Sprint 27 fix vs Sprint 28 carryforward). Note: #1388's binding verdict requires a Day 0/1 NLP-warm-started PATH solve test to discriminate between (a/b) emit bug → Sprint 27 fix and (c) fundamental model property → Sprint 28 carryforward. The Phase 0 PROCEED-with-condition signal codifies this.

The fix itself ships at Sprint 27 Day 1/2 (#1387) or Day 0/1 (#1388 runtime test → conditional fix or filing); this document is the engineering input.

---

## 2. Sprint 27 Day 0 Baseline State (per `gamslib_status.json`)

| Model | Translate | Solve | Compare | rel_diff | Notes |
|---|---|---|---|---|---|
| `cclinpts` | success | `model_optimal` | `mismatch` | **1.0 (100%)** | Solves model_optimal but obj mismatches NLP by 100% relative. Day 0 value updated from the originally-filed ~70% — emit may have drifted in subsequent sprints (Sprint 25/26 src/ activity); Phase 0 KKT-derivation analysis remains the same. **+1 Match recovery target** if fixed. |
| `camshape` | success | `model_infeasible` | `not_tested` | n/a | PATH MODEL STATUS 5 Locally Infeasible at obj=6.2 vs NLP optimum 4.2841. Day 0 in `model_infeasible` bucket; comparison cascade-skipped. **+1 Solve recovery target** if fixed. |

Both models are in scope for Sprint 27 Priority 7. Neither is in `path_syntax_error` (so no compile-stage blocker); both have working emit that produces wrong KKT structure (#1387) or wrong-but-compiling KKT (#1388).

---

## 3. Issue #1387 cclinpts — Sign-Flip + Term-Omission Bug

### 3.1 Phase 0 Target Shape (from `docs/issues/ISSUE_1387_*.md` §"Phase 0 Acceptance Gate")

**Source objective** has two terms per breakpoint `j`:

- **Term 1** (when `not last(j)`): `(b('s30') - b(j)) * (fb(j) - fb(j-1))`
- **Term 2** (when `not first(j)`): `0.5 * (b(j) - b(j-1)) * (fb(j) - fb(j-1))`

**Hand-derived KKT for `∂ObjV/∂b(j)`** (3 expected contributions, Lagrangian-sign-flipped to put on LHS of `stat_b(j).. ... =E= 0`):

```
- (fb(j) - fb(j-1)) * 1$(not last(j))           [Term 1 at j; sign NEGATIVE after flip]
+ 0.5 * (fb(j) - fb(j-1)) * 1$(not first(j))    [Term 2 at j; sign POSITIVE after flip]
- 0.5 * (fb(j+1) - fb(j)) * 1$(not first(j+1))  [Term 2 at j+1 (offset); MISSING from current emit]
```

**Hand-derived KKT for `∂ObjV/∂fb(j)`** (4 expected contributions, Lagrangian-flipped):

```
+ (b('s30') - b(j)) * 1$(not last(j))           [Term 1 at j; MISSING from current emit]
- (b('s30') - b(j+1)) * 1$(not last(j+1))       [Term 1 at j+1 offset; MISSING]
+ 0.5 * (b(j) - b(j-1)) * 1$(not first(j))      [Term 2 at j; PRESENT but sign-wrong per Lagrangian flip]
- 0.5 * (b(j+1) - b(j)) * 1$(not first(j+1))    [Term 2 at j+1 offset; MISSING]
```

### 3.2 Current Emit (`data/gamslib/mcp/cclinpts_mcp.gms:133-134`)

```gams
stat_b(j).. ((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j))))) + 0.5 * (fb(j) - fb(j-1)) * 1$((not first(j))))) + ((-1) * ((1 - gamma) * b(j) ** (1 - gamma) * (1 - gamma) / b(j) / sqr(1 - gamma))) * nu_FBCalc(j) + nu_b_fx_s1$(sameas(j, 's1')) + nu_b_fx_s30$(sameas(j, 's30')) - piL_b(j) + piU_b(j) =E= 0;

stat_fb(j).. ((-1) * (0.5 * (b(j) - b(j-1)) * 1$((not first(j))))) + nu_FBCalc(j) =E= 0;
```

### 3.3 Bug Class: TWO compounding errors

**Bug 1 — Sign-flip on `stat_b` Term 1.** The emit shows `((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j))))) + 0.5 * ...))`. Distributing the outer `(-1)` gives `+(fb(j) - fb(j-1)) * 1$(not last(j)) - 0.5 * (fb(j) - fb(j-1)) * 1$(not first(j))`. The expected post-Lagrangian-flip shape is `-(fb(j) - fb(j-1)) * 1$(not last(j)) + 0.5 * (fb(j) - fb(j-1)) * 1$(not first(j))`. **Both terms have the wrong sign** — the Lagrangian-conversion step has double-negated Term 1 (yielding positive instead of negative) AND single-negated Term 2 (yielding negative instead of positive). This indicates the sign-flip logic is applied at the wrong nesting level — the outer `(-1)` should not be present, OR the inner `(-1)` on Term 1 should not be present.

**Bug 2 — Term omission in `stat_fb` (3 of 4 contributions missing).** The emit contains ONLY `((-1) * (0.5 * (b(j) - b(j-1)) * 1$((not first(j)))))` corresponding to Term 2 at j (with wrong sign too — Lagrangian-flipped form should be `+ 0.5 * (b(j) - b(j-1)) * 1$(not first(j))`). MISSING:
- `+ (b('s30') - b(j)) * 1$(not last(j))` — Term 1 at j (∂ObjV/∂fb(j) of the Term 1 product `[b('s30') - b(j)] * [fb(j) - fb(j-1)]`).
- `- (b('s30') - b(j+1)) * 1$(not last(j+1))` — Term 1 at j+1 offset (∂ object/∂fb(j) of Term 1 at j+1 produces a contribution since `fb(j+1) - fb(j)` includes `fb(j)`).
- `- 0.5 * (b(j+1) - b(j)) * 1$(not first(j+1))` — Term 2 at j+1 offset.

**Bug 2 root cause hypothesis:** The AD layer's `_diff_sum` (or its dispatch for product-of-2-IndexOffsets) is not enumerating the j+1 offset-substitution path for cross-terms whose product structure has BOTH operand-indices contain `fb(j)` (i.e., one direct and one inside `IndexOffset(j-1)` ≡ `j+1` after solving for `fb(j+1) - fb(j) = ...`). The missing terms all involve substituting `j → j+1` in the bound index AND the resulting cross-term references `fb(j)` (the wrt variable) once via the IndexOffset.

### 3.4 Source-Code Patch Sites

**Primary site (Bug 2 — term omission):**

- **`src/ad/derivative_rules.py:1847`** (`_diff_sum`) — handles partial derivatives of Sum expressions. The current implementation likely processes each Sum-instance only via the base-index substitution path; the j+1 offset-substitution path (which contributes the offset cross-terms) is missing for products where BOTH factors contain the wrt-variable's index.
- **`src/ad/derivative_rules.py:577`** (`_diff_binary`) — handles `Binary("*", ...)` product-rule dispatch. If `_diff_sum` correctly enumerates index-substitution paths, then `_diff_binary` must apply the product rule across each substitution. Verify cross-term collection is complete.

**Secondary site (Bug 1 — sign-flip nesting):**

- **`src/kkt/stationarity.py:1352`** (`build_stationarity_equations`) or `:1835` (`_build_indexed_stationarity_expr`) — Lagrangian-conversion step that flips the sign of objective-gradient contributions for `=E=` equations. Current double-negation `((-1) * (((-1) * ...)))` suggests the conversion is applied twice (once during AD and once during Lagrangian assembly) for certain term classes (specifically: objective gradients with inner sign already from `_diff_sum`'s expansion). Verify the Lagrangian-flip is applied EXACTLY ONCE to the assembled stationarity body.

**Tertiary site (if Bug 2 root cause is broader):**

- **`src/ad/constraint_jacobian.py:903`** (`_compute_equality_jacobian`) — if the missing offset cross-terms are dropped at the Jacobian-assembly stage rather than the `_diff_sum` stage, the fix moves here. Less likely (the symptoms point at `_diff_sum`'s product-rule enumeration, not Jacobian collection), but worth ruling out via debug-trace during Day 1 implementation.

### 3.5 Implementation Effort Estimate

| Sub-task | Effort | Notes |
|---|---|---|
| Sign-flip diagnosis (Bug 1) — locate double-negation root in stationarity Lagrangian-conversion | 1h | May be a single-line fix in `stationarity.py` once root cause identified |
| Sign-flip fix + unit tests | 1h | Single-line fix likely; regression tests in `tests/integration/emit/test_cclinpts_*.py` |
| Term-omission diagnosis (Bug 2) — trace `_diff_sum` on cclinpts's `obj.. =E= sum(j, Term1 + Term2)` | 1.5h | Debug trace to identify which offset-substitution path is missing |
| Term-omission fix in `_diff_sum` (or `_diff_binary` product-rule + `constraint_jacobian` collection) | 1.5h | Fix scope depends on diagnosis; may be deeper if shared AD-architecture issue surfaces |
| Regression check on 11 Tier 0/1 canaries | 0.5h | Auto via PR19 widening CI (Sprint 27 Day 0 widening lands cclinpts in Pattern C tier) |
| GAMS compile-check + PATH solve verification: cclinpts MODEL STATUS 1 with `rel_diff < 1%` | 1h | Run full solve + compare against NLP optimum |
| Review iteration buffer | 0.5h | PR review may surface refinements |
| **Total** | **~7h** (1 + 1 + 1.5 + 1.5 + 0.5 + 1 + 0.5) | Above the upper edge of Phase 0's 3–6h estimate range due to the explicit per-bug diagnosis steps; within Priority 7 budget when combined with #1388. |

**Risk factor that could expand effort to 8–12h:** if Bug 2 diagnosis reveals a broader AD-architecture issue (e.g., `_diff_sum`'s offset-substitution enumeration is structurally missing for an entire class of expressions, not just cclinpts's product), the fix may need to be deferred to a broader Sprint 28 AD-refactor workstream. In that case, **#1387 escalates to Sprint 28 carryforward.** Day 1 diagnosis is the binding factor here.

### 3.6 PROCEED Criteria (Sprint 27 binding)

Per Phase 0 verification methodology, **PROCEED** when ALL hold (verified post-implementation):

1. Regenerate `cclinpts_mcp.gms`.
2. `stat_b(j)` body matches the hand-derived KKT shape per per-term grep checks (3 contributions: Term 1 at j with negative sign, Term 2 at j with positive sign, Term 2 at j+1 offset with negative sign).
3. `stat_fb(j)` body matches the hand-derived KKT shape per per-term grep checks (4 contributions: Term 1 at j positive, Term 1 at j+1 negative, Term 2 at j positive, Term 2 at j+1 negative).
4. GAMS compile clean (no new errors vs current main).
5. PATH solve reaches MODEL STATUS 1 with `rel_diff < 1%` (Day 0 baseline: 1.0 / 100%).
6. All 11 Tier 0/1 byte-stable canaries unchanged.

### 3.7 Verdict (binding)

**SPRINT 27 FIX** (high confidence). Bug class identified; fix sites located at `file:line` precision; effort ~7h within Priority 7 budget (combined with #1388 — see §5.1 most-likely path). **Conditional escalation to Sprint 28** ONLY IF Day 1 diagnosis reveals broader AD-architecture issue with `_diff_sum`'s offset-substitution enumeration — in that case, file Sprint 28 carryforward and bundle with Priority 3's AD-redesign workstream (Approach C in PRIORITY_3_RISK_ASSESSMENT.md §5.3 may share infrastructure).

---

## 4. Issue #1388 camshape — Root Cause UNKNOWN at Day 0 + PROCEED-with-Condition (boundary-guard hypothesis downgraded per §4.3)

### 4.1 Phase 0 Target Shape (from `docs/issues/ISSUE_1388_*.md` §"Phase 0 Acceptance Gate")

**Hand-derived KKT for `∂L/∂r(i) = 0`** at interior `i` (where `middle(i) = ord(i) > 1 AND ord(i) < card(i)`) combines:

- **Objective gradient:** `+ (-1) * (pi * R_v / 100)` (Lagrangian-flipped from the POSITIVE objective `obj.. area =E= ((pi*R_v)/%n%) * sum(i, r(i))` at `data/gamslib/raw/camshape.gms:63` — `n=100` resolves the `%n%` macro). The positive gradient `+pi * R_v / 100` becomes negative in `stat_r(i)` due to the Lagrangian sign-flip on the objective, NOT because the source objective is negative.
- **`lam_convexity(i)` cross-term:** `(-r(i-1) - r(i+1)) * lam_convexity(i)$(middle(i))`.
- **`lam_convexity(i-1)` cross-term:** `(-r(i-1) + 2*r(i-2)*cos(d_theta)) * lam_convexity(i-1)`. **Canonical guard:** `$(middle(i-1))` — which implies `ord(i-1) > 1 AND ord(i-1) < card(i)`, i.e., `ord(i) > 2 AND ord(i) < card(i)+1` ≡ `ord(i) > 2` for interior `i`.
- **`lam_convexity(i+1)` cross-term:** `(-r(i+1) + 2*r(i+2)*cos(d_theta)) * lam_convexity(i+1)`. **Canonical guard:** `$(middle(i+1))` — which implies `ord(i+1) > 1 AND ord(i+1) < card(i)`, i.e., `ord(i) > 0 AND ord(i) < card(i)-1` ≡ `ord(i) < card(i)-1` for interior `i`.
- **`nu_eqrdiff(i-1)` and `nu_eqrdiff(i)`** offset-indexed cross-terms with signs +1 and -1 respectively, plus edge-case `lam_convex_edge1/edge3/edge4` contributions at `first(i)`/`last(i)`.

### 4.2 Current Emit (`data/gamslib/mcp/camshape_mcp.gms:428`)

The L428 emit (single line, ~600 characters) contains the major components but with potentially-incorrect guards on the `lam_convexity(i±1)` cross-terms. Key extracts:

```gams
stat_r(i)..
  (
    ((-1) * (pi * R_v / 100))                                                                       [obj grad ✓]
  + nu_eqrdiff(i)$(j(i)) + (((-1) * nu_eqrdiff(i-1))$(ord(i) > 1))$(j(i))                          [eqrdiff cross-terms ✓]
  + ((((-1) * r(i-1)) - r(i+1)) * lam_convexity(i))$(middle(i))                                    [lam_convexity(i) ✓]
  + (((((-1) * r(i+1)) + 2 * cos(d_theta) * r(i+2)) * lam_convexity(i+1))$(ord(i) <= card(i) - 1))$(middle(i))
  + (((((-1) * r(i-1)) + 2 * cos(d_theta) * r(i-2)) * lam_convexity(i-1))$(ord(i) > 1))$(middle(i))
  + ... [edge cases for first(i) / last(i)] ...
  - piL_r(i) + piU_r(i)
  )$(r.up(i) - r.lo(i) > 1e-10) =E= 0;
```

### 4.3 Suspected Bug Class: Guard Mis-Specification

**Current `lam_convexity(i-1)` guard:** `$(ord(i) > 1)$(middle(i))`. Expanding `middle(i)` = `ord(i) > 1 AND ord(i) < card(i)` gives effective guard `ord(i) > 1 AND ord(i) < card(i)`. **Canonical** (per Phase 0) is `$(middle(i-1))` = `ord(i-1) > 1 AND ord(i-1) < card(i)` = `ord(i) > 2 AND ord(i) < card(i)+1` = `ord(i) > 2`. **Difference at i=2:** current emit fires the term, canonical doesn't. This over-firing produces a spurious `lam_convexity(1)` reference at the i=2 stationarity, breaking the matched-pair complementarity structure for `comp_convexity(i)` (which itself has guard `$((middle(i)) and ((ord(i) <= card(i) - 1) and (ord(i) > 1)))` per L435 — and `lam_convexity.fx(i)$(not ((ord(i) <= card(i) - 1) and (ord(i) > 1))) = 0` per L467 fixes `lam_convexity(i)` to zero for non-middle `i`).

**Current `lam_convexity(i+1)` guard:** `$(ord(i) <= card(i) - 1)$(middle(i))` = `ord(i) <= card(i)-1 AND ord(i) > 1 AND ord(i) < card(i)`. **Canonical** = `$(middle(i+1))` = `ord(i) > 0 AND ord(i) < card(i)-1` = `ord(i) < card(i)-1`. **Difference at i=card(i)-1:** current emit fires the term, canonical doesn't. Same over-firing issue.

**Mechanism of failure: UNPROVEN — boundary guard over-firing does NOT explain Locally Infeasible.** A prior version of this section asserted that the over-firing creates a structural inconsistency that drives PATH to MODEL STATUS 5. That assertion is incorrect. The emit at L464 + L467 fixes `lam_convexity(<non-middle i>) = 0` via:

```gams
lam_convexity.fx(i)$(not (middle(i))) = 0;                                          [L464]
lam_convexity.fx(i)$(not ((ord(i) <= card(i) - 1) and (ord(i) > 1))) = 0;          [L467, same condition as L464]
```

So the over-fired `lam_convexity(i-1)` term at i=2 references `lam_convexity(1)`, which is fixed to 0 — the contribution is mathematically `<coefficient> * 0 = 0`. Same at i=card(i)-1 for `lam_convexity(card(i)) = 0`. **The over-firing produces identically-zero contributions to `stat_r(i)`; it cannot be the cause of Locally Infeasible.**

**What the guard mis-specification IS:** a Phase 0 form-correctness mismatch. The emit's guard differs from the canonical hand-derived `middle(i±1)` form, which is a documentation / shape concern (the per-term grep checks in Phase 0 §4 of `docs/issues/ISSUE_1388_*.md` will flag this as a non-canonical shape). Cleaning this up to `middle(i±1)` is a low-cost correctness improvement, but it is NOT a fix for the Locally Infeasible outcome on its own.

**Actual cause of Locally Infeasible: UNKNOWN at Day 0 prep stage.** Day 0/1 diagnosis is required (see §4.6).

**Caveat:** This downgrades the prior "STRONG SUSPICION" of guard-mis-specification-as-root-cause to **HYPOTHESIS (UNPROVEN)**. The three Day 0/1 outcomes remain valid as the discrimination structure but with revised meaning:

- **(a) Emit bug, NLP-warm-start solves:** PATH from a verified-loaded NLP warm-start reaches MODEL STATUS 1 with obj ≈ 4.2841. Some emit bug exists; the actual bug location is identified post-hoc by inspecting the PATH listing for which row was reported as infeasible on the default-start solve, then comparing the same row's structure in the emit against hand-derived KKT. Fix scope and patch site are determined at this point. (Bug may or may not be related to the boundary guards.)
- **(b) Emit bug, NLP-warm-start still fails:** PATH from a verified-loaded NLP warm-start still returns MODEL STATUS 5. The emit bug exists but PATH cannot find the feasible region even from the NLP optimum — suggests structural KKT divergence (e.g., a missing or extra term elsewhere in the emit, not the boundary guards). Day 0/1 engineer inspects the PATH listing's infeasibility-row report to identify which residual is non-zero and traces back through the emit.
- **(c) Fundamental property, NLP-warm-start fails AND no shape divergence visible:** No identifiable emit bug; the model itself is a non-convex MCP that PATH cannot solve. **Sprint 28 carryforward** (no Sprint 27 fix possible without changing the model formulation or switching solvers).

### 4.4 Source-Code Patch Site (if Cases a/b — Sprint 27 fix)

**Patch site: TBD pending Day 0/1 diagnosis.** Until Day 0/1 identifies which residual row PATH reports as infeasible, the specific patch site cannot be pinned at `file:line` precision. Two candidate areas remain plausible based on Day 0 evidence:

- **Candidate A — `src/kkt/stationarity.py:1835`** (`_build_indexed_stationarity_expr`): if the actual bug surfaces in stationarity assembly (e.g., a missing or extra term in `stat_r(i)` interior), the fix lands here.
  - The boundary guard mis-specification noted in §4.3 (Phase 0 form-correctness divergence) is a likely cleanup item here too, but it is NOT the demonstrated root cause of Locally Infeasible — only a same-file co-issue worth fixing while touching the area.
- **Candidate B — `src/ad/constraint_jacobian.py:903 + :1027`**: if the missing/extra term traces back to a Jacobian-collection issue at the AD layer (similar in spirit to #1387's Bug 2 hypothesis), the fix lands here.

Day 0/1 engineer inspects the PATH-listing infeasibility-row report from the failing default-start solve to identify which residual is non-zero, traces back through the emit to the originating Python helper, and pins the patch site. The boundary-guard cleanup may or may not be coincidentally on the same fix path.

**Secondary site (if Bug surfaces at AD layer):**

- **`src/ad/constraint_jacobian.py:903` / `:1027`** — if the cross-term guard is inherited from the AD-Jacobian rather than constructed at the stationarity layer, the fix moves here. Less likely (the guard pattern `middle(i)` is a stationarity-layer concept), but worth ruling out.

### 4.5 Implementation Effort Estimate

Since the actual root cause is unknown pre-Day 0 (per §4.3 downgrade), the per-case estimates below INCLUDE a diagnostic step to identify the patch site from the PATH-listing infeasibility-row report.

**Case (a) Emit bug, NLP-warm-start solves (most likely):**

| Sub-task | Effort |
|---|---|
| Diagnose actual root cause from default-start PATH listing's infeasibility-row report | 1h |
| Fix (location depends on diagnosis — Candidate A `_build_indexed_stationarity_expr` OR Candidate B `_compute_equality_jacobian`/`_compute_inequality_jacobian`) | 1.5h |
| Optional Phase 0 form-correctness cleanup: boundary guards `middle(i)` → `middle(i±1)` (cosmetic since fixups zero them, but matches canonical hand-derived form) | 0.5h |
| Unit + integration tests | 0.5h |
| GAMS compile-check + PATH solve verification (camshape MODEL STATUS 1 with obj ≈ 4.2841) | 0.5h |
| 11 Tier 0/1 canary regression check (auto via PR19 widening CI) | 0.5h |
| **Total** | **~4.5h** |

**Case (b) Emit bug + NLP-warm-start guidance needed:**

| Sub-task | Effort |
|---|---|
| Diagnosis + fix (per Case a) | 4.5h |
| Add NLP-warm-start in `solve_mcp` flow OR document it as user-required for camshape | 1h |
| **Total** | **~5.5h** |

**Case (c) Fundamental property — Sprint 28 carryforward:**

| Sub-task | Effort |
|---|---|
| Document diagnostic evidence (PATH-listing infeasibility-row + comparison against hand-derived KKT shape) in `docs/issues/ISSUE_1388_*.md` with formal Sprint 28 classification + budget estimate | 0.75h |
| Update GitHub issue label (remove `sprint-27`, add `sprint-28`) | 0.1h |
| Update PROJECT_PLAN.md Sprint 28 §Priority section to add #1388 | 0.4h |
| **Total** | **~1.25h** |

### 4.6 PROCEED/REPLAN Signal (Phase 0 PROCEED-with-Condition, binding)

The Day 0/1 NLP-warm-started PATH solve test discriminates the three cases.

**Important caveat on GAMS warm-start mechanics:** GAMS does NOT accept a generic `--starting-point=<file>` double-dash parameter to initialize variable levels for an MCP — `--<name>=<value>` is a user-defined parameter, and the generated `camshape_mcp.gms` does NOT have any `execute_loadpoint`/GDX-reading or `$ifthen --starting-point` logic that would consume such a parameter. Setting `--starting-point=...` would be a NO-OP; PATH would still start from the default initial levels emitted at `camshape_mcp.gms:300+` (`r.l(i) = (R_min + R_max) / 2;` plus per-element overrides), which is NOT the NLP solution. The Day 0/1 engineer MUST use one of the two GAMS-supported warm-start mechanisms below.

**Approach A — GDX-loadpoint (canonical GAMS warm-start):**

```bash
# Day 0/1 runtime test, Approach A: GDX loadpoint

# 1. Regenerate the MCP emit:
.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms -o /tmp/camshape_mcp.gms --quiet

# 2. Capture NLP solution to GDX (save *.gdx using `gdx=` argument):
gams data/gamslib/raw/camshape.gms gdx=/tmp/camshape_nlp.gdx o=/tmp/camshape_nlp.lst lo=2

# 3. Inject an `execute_loadpoint` directive into the MCP file BEFORE the
#    `Solve mcp_model using MCP;` statement. The generated emit does not
#    include this, so the test driver must patch it in (or maintain a
#    wrapper script that injects + runs):
SOLVE_LINE_NO=$(grep -n '^Solve mcp_model using MCP' /tmp/camshape_mcp.gms | cut -d: -f1)
sed -i.bak "${SOLVE_LINE_NO}i\\
execute_loadpoint '/tmp/camshape_nlp.gdx';
" /tmp/camshape_mcp.gms

# 4. Re-solve from warm-started point:
gams /tmp/camshape_mcp.gms o=/tmp/camshape_mcp_warm.lst lo=2
grep -E 'MODEL STATUS|OBJECTIVE VALUE' /tmp/camshape_mcp_warm.lst
```

**Approach B — Explicit `.l` overrides extracted from the NLP solve (no GDX required):**

```bash
# Day 0/1 runtime test, Approach B: explicit .l assignments

# 1. Regenerate the MCP emit:
.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms -o /tmp/camshape_mcp.gms --quiet

# 2. Solve NLP and extract r(i) levels from the listing (or write a tiny
#    GAMS script that solves NLP then `display r.l;`):
gams data/gamslib/raw/camshape.gms o=/tmp/camshape_nlp.lst lo=2
# Parse the listing's "---- VAR r" block into a series of
# r.l('i1') = <val>; ... lines; assemble into /tmp/camshape_warm_overrides.gms.

# 3. Inject the per-instance `.l` overrides into the MCP file BEFORE the
#    `Solve mcp_model using MCP;` statement (same sed-injection pattern as
#    Approach A, but inserting the contents of camshape_warm_overrides.gms
#    instead of an `execute_loadpoint` directive).

# 4. Re-solve from warm-started point:
gams /tmp/camshape_mcp.gms o=/tmp/camshape_mcp_warm.lst lo=2
grep -E 'MODEL STATUS|OBJECTIVE VALUE' /tmp/camshape_mcp_warm.lst
```

**Note:** Approach A is canonical (smaller injection footprint; survives `r(i)` set-size changes) but requires GDX-capable GAMS (the demo edition does support GDX). Approach B is more portable but requires per-instance level extraction and re-injection. Day 0/1 engineer picks whichever is cheapest in the local environment.

**Verify the warm-start actually took effect** before classifying the test result. The PATH listing's `---- VAR r` block reports the SOLVER OUTPUT (final iterate, or failure point if MODEL STATUS 5) — not the initial `r.l` levels PATH started from. A failed run would incorrectly look like "the warm-start was loaded but PATH still failed" when in reality PATH may have started from `(R_min+R_max)/2` defaults and never saw the NLP point.

**Correct check: inject a `display r.l;` marker statement IMMEDIATELY AFTER the `execute_loadpoint` (Approach A) or `.l` override block (Approach B) AND IMMEDIATELY BEFORE the `Solve mcp_model using MCP;` line.** Then grep the listing's display block (which is written during compilation, before the solve, and reflects the actual starting levels):

```bash
# Inject `display r.l;` right after the warm-start block (Approach A or B) and
# right before the `Solve mcp_model using MCP;` line. Example (Approach A):
SOLVE_LINE_NO=$(grep -n '^Solve mcp_model using MCP' /tmp/camshape_mcp.gms | cut -d: -f1)
sed -i.bak "${SOLVE_LINE_NO}i\\
display r.l;
" /tmp/camshape_mcp.gms

# After the next `gams` run, the display block appears in the listing BEFORE
# any solver output. Find it via the GAMS display header:
awk '/^---- [0-9]+ VARIABLE r\.L/,/^$/' /tmp/camshape_mcp_warm.lst | head -20
# Each `r.l('i_k')` value here should match the NLP solution, NOT the default
# `(R_min + R_max) / 2;` from camshape_mcp.gms:300. If they match defaults,
# the warm-start did NOT load and the test result is INVALID (classify as
# "warm-start mechanism failed"; rerun after debugging the injection).
```

**Result interpretation (only valid AFTER the warm-start verification above confirms `r.l` was loaded from NLP):**

- **MODEL STATUS 1 with obj ≈ 4.2841** → Case (a); emit bug exists. **PROCEED for Sprint 27 fix.** Day 0/1 engineer inspects the default-start failing-solve listing's infeasibility-row report to identify which residual is non-zero, traces back to the originating Python helper, then pins the patch site at Candidate A `src/kkt/stationarity.py:1835` OR Candidate B `src/ad/constraint_jacobian.py:903/:1027` per §4.4. Effort ~4.5h.
- **MODEL STATUS 5 Locally Infeasible from NLP warm-start** AND the per-term Phase 0 grep checks reveal a shape divergence (other than the inert boundary-guard mis-specification noted in §4.3) → Case (b); emit bug exists but PATH cannot escape the wrong stationary point from NLP either. Day 0/1 engineer applies the same diagnostic-then-fix workflow + adds NLP-warm-start guidance. Effort ~5.5h.
- **MODEL STATUS 5 Locally Infeasible from NLP warm-start** AND per-term Phase 0 grep checks reveal NO non-inert shape divergence → Case (c); no identifiable emit bug. **REPLAN to Sprint 28 carryforward.** Effort ~1.25h filing.

### 4.7 Verdict (binding pending Day 0/1 runtime test + diagnosis)

**SPRINT 27 CONDITIONAL.** The Phase 0 PROCEED-with-condition signal still gates the verdict on the Day 0/1 runtime test, but the prior-version assertion that the boundary-guard mis-specification IS the root cause is downgraded to **UNPROVEN HYPOTHESIS** (per §4.3 — the over-fired terms are zeroed by the L464+L467 fixups, so they cannot drive Locally Infeasible). The binding Sprint 27 fix path requires the FULL 3-way discriminator from §4.6 — the NLP-warm-start runtime test ALONE is NOT sufficient to classify Case (c):

1. **Day 0/1 NLP-warm-start test** (with verified-loaded warm-start per §4.6) — produces MODEL STATUS 1 (→ Case (a) Sprint 27 fix) OR MODEL STATUS 5 (→ further classification needed via step 2 + the shape-divergence check).
2. **Day 0/1 default-start failing-solve listing diagnosis + per-term Phase 0 grep checks for non-inert shape divergence** — identifies the actual residual-causing emit bug (Candidate A `stationarity.py:1835` OR Candidate B `constraint_jacobian.py:903/:1027` per §4.4) AND discriminates Case (b) (MS 5 + non-inert divergence visible → still Sprint 27 fix path) from Case (c) (MS 5 + no non-inert divergence → Sprint 28 carryforward). The "inert" exclusion is critical — the boundary-guard form-mismatch noted in §4.3 is inert (zeroed by L464+L467 fixups) and does NOT trigger Case (b); only divergences elsewhere in the emit do.

- **If Day 0/1 NLP-warm-start test PASSES AND diagnosis identifies the residual-causing emit bug** → **Case (a) Sprint 27 FIX** (~4.5h effort; +1 Solve recovery).
- **If Day 0/1 NLP-warm-start test FAILS AND per-term Phase 0 grep checks reveal a non-inert shape divergence** → **Case (b) Sprint 27 FIX** (~5.5h effort; emit bug + warm-start guidance; +1 Solve recovery).
- **If Day 0/1 NLP-warm-start test FAILS AND no non-inert shape divergence visible from per-term Phase 0 grep checks** → **Case (c) Sprint 28 CARRYFORWARD** (~1.25h filing; no +1 Solve gain in Sprint 27; reclassify as fundamental property).

The Day 0/1 engineer runs the test before any `src/` patching; the binding verdict is recorded in PRIORITY_7_FIX_SURFACE.md §4.7 + KNOWN_UNKNOWNS.md §Unknown 7.2.

---

## 5. Combined Priority 7 Budget Fit

### 5.1 Most-likely path (#1387 Sprint 27 fix + #1388 Case (a/b) Sprint 27 fix)

| Issue | Effort | Sub-priority |
|---|---|---|
| #1387 cclinpts (sign-flip + term-omission) | ~7h | Priority 7a |
| #1388 camshape (diagnose-then-fix, Case a/b) | ~4.5–5.5h | Priority 7b |
| **Combined Sprint 27 effort** | **~11.5–12.5h** | **At-or-just-above 6–12h budget** ⚠️ (upper end of range edges past the 12h ceiling by ~0.5h on the high estimate — see escalation note below) |

**Sprint 27 gains** (if both PROCEED): **+1 Match (cclinpts) + +1 Solve (camshape).**

**Escalation note:** if Day 0/1 diagnosis pushes either issue toward the upper end of its range, the combined effort can edge marginally past the nominal 12h ceiling (e.g., 7h + 5.5h = 12.5h). Sprint 27 retrospective should treat the budget as a soft guideline here; tighten by trimming the 0.5h optional guard cleanup in #1388 if needed, or accept the 0.5h overrun by drawing from the Day 13 buffer.

### 5.2 Mixed path (#1387 Sprint 27 fix + #1388 Case (c) Sprint 28 carryforward)

| Issue | Effort | Sub-priority |
|---|---|---|
| #1387 cclinpts (sign-flip + term-omission) | ~7h | Priority 7a |
| #1388 camshape (carryforward filing) | ~1.25h | Priority 7b (deferred) |
| **Combined Sprint 27 effort** | **~8.25h** | **Within 6–12h budget** ✅ |

**Sprint 27 gains:** **+1 Match (cclinpts) only** (no +1 Solve from camshape; deferred to Sprint 28).

### 5.3 Worst case (#1387 AD-architecture escalation + #1388 Case (a/b) Sprint 27 fix)

| Issue | Effort | Sub-priority |
|---|---|---|
| #1387 cclinpts (escalated to Sprint 28 AD-architecture bundle) | ~1h filing | Priority 7a (deferred) |
| #1388 camshape (diagnose-then-fix, Case a/b) | ~4.5–5.5h | Priority 7b |
| **Combined Sprint 27 effort** | **~5.5–6.5h** | **Within 6–12h budget** ✅ (lower end; reallocate slack to other priorities) |

**Sprint 27 gains:** **+1 Solve (camshape) only.**

### 5.4 Worst-worst case (both deferred)

If #1387 diagnosis reveals AD-architecture issue AND #1388 Day 0/1 test fails AND no shape divergence visible: both deferred to Sprint 28; ~2.25h Sprint 27 effort (filings + label updates). Priority 7 effectively zero Sprint 27 gain; budget reallocates to other priorities. **Less unlikely than the prior version of this section suggested** — #1388's "guard mis-specification is root cause" hypothesis was downgraded to UNPROVEN per §4.3 review, so the Case (c) probability is now higher than the prior "low probability" claim.

---

## 6. Sprint 28 Carryforward Template (if needed)

If either issue defers to Sprint 28, the following template should be filed in `docs/issues/ISSUE_<N>_*.md` as a new "Sprint 28 Carryforward" section, AND the GitHub issue's `sprint-27` label removed + `sprint-28` label added.

```markdown
## Sprint 28 Carryforward (per Sprint 27 Prep Task 8 verdict)

**Sprint 27 Day 0/1 verdict:** <Case (c) fundamental property | AD-architecture bundle | other>
**Sprint 27 Prep Task 8 analysis:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §<3 or 4>
**Effort estimate (Sprint 28):** <T h>
**Sprint 28 Priority placement:** <Priority N, between # and #>
**Phase 0 Acceptance Gate:** <reaffirm existing Phase 0 from ISSUE_<N>.md §"Phase 0 Acceptance Gate" | re-author with updated diagnosis>
**Discriminating evidence from Sprint 27 prep:**
- <evidence 1>
- <evidence 2>
**Recommended Sprint 28 approach:**
- <approach 1>
- <approach 2>
```

**GitHub label update commands** (run only if defer):

```bash
gh issue edit <NNNN> --remove-label sprint-27
gh issue edit <NNNN> --add-label sprint-28
```

**PROJECT_PLAN.md Sprint 28 §Priority update** (run only if defer):

Add to PROJECT_PLAN.md Sprint 28 priorities section with the carryforward rationale + linked PRIORITY_7_FIX_SURFACE.md analysis section.

---

## 7. Verification Summary (Sprint 27 Day 0 Prep)

| Verification Target | Result |
|---|---|
| Phase 0 target shape cross-reference (from Prep Task 2) for #1387 | ✅ §3.1 |
| Phase 0 target shape cross-reference (from Prep Task 2) for #1388 | ✅ §4.1 |
| Current-emit-vs-target comparison for #1387 | ✅ §3.2 + §3.3 (2 bugs identified: sign-flip + term-omission) |
| Current-emit-vs-target comparison for #1388 | ✅ §4.2 + §4.3 (boundary guard shape divergence noted, but UNPROVEN as cause of Locally Infeasible — the over-fired contributions are zeroed by L464+L467 fixups; actual cause requires Day 0/1 diagnosis) |
| Source-code patch sites at file:line precision | ✅ §3.4 (#1387: `derivative_rules.py:1847,577` + `stationarity.py:1352,1835` + `constraint_jacobian.py:903`); §4.4 (#1388: candidates A `stationarity.py:1835` OR B `constraint_jacobian.py:903/1027` — specific patch site is TBD pending Day 0/1 diagnosis of the actual residual-causing bug) |
| Implementation effort estimate per issue | ✅ §3.5 (#1387 ~7h); §4.5 (#1388 ~4.5h Case a, ~5.5h Case b, ~1.25h Case c) |
| Combined Priority 7 budget fit | ⚠️ §5 (most-likely path ~11.5–12.5h — upper end edges past the 12h ceiling by ~0.5h; mitigations documented in §5.1 escalation note) |
| Per-issue verdict | ✅ §3.7 (#1387 SPRINT 27 FIX binding); §4.7 (#1388 SPRINT 27 CONDITIONAL, binding pending Day 0/1 NLP-warm-start runtime test + diagnostic-row identification) |
| Sprint 28 carryforward template documented | ✅ §6 |

**Sprint 27 Priority 7 PROCEED (with caveat).** Most-likely path (both Sprint 27 fix) is ~11.5–12.5h — the upper end edges past the nominal 12h Priority 7 budget by ~0.5h, mitigated by trimming the 0.5h #1388 optional guard cleanup OR drawing from the Day 13 buffer. Mixed path (#1387 fix + #1388 carryforward) is ~8.25h, comfortably within budget. #1387 binding Sprint 27 fix verdict (high confidence). #1388 conditional verdict pending Day 0/1 runtime test AND default-start failing-solve listing diagnosis — Case (c) probability is no longer "low" since the boundary-guard mechanism was disproved (zeroed by fixups); the actual residual-causing emit bug is unknown pre-Day 0.

---

## 8. Sprint 27 Day 0/1 Engineer Handoff

**Day 0/1 morning (before any `src/` patching):**

1. **#1388 NLP-warm-start runtime test** (~45 min including warm-start verification injection per §4.6) — produces MODEL STATUS 1 (→ Case (a)) OR MODEL STATUS 5 (→ Case (b) or Case (c), distinguished by step 2's shape-divergence check). The runtime test alone is NOT sufficient to classify Case (c) — see §4.7.
2. **#1388 default-start failing-solve diagnosis + per-term Phase 0 grep checks** (~1h) — inspect the listing's infeasibility-row report from the default-start failing solve to identify which residual is non-zero; trace back through `camshape_mcp.gms:428` to the originating Python helper (Candidate A `stationarity.py:1835` OR Candidate B `constraint_jacobian.py:903/:1027`); pin patch site. Run per-term Phase 0 grep checks for non-inert shape divergence (excluding the inert boundary-guard form-mismatch per §4.3). Combined with step 1's MODEL STATUS, this discriminates Case (b) (MS 5 + non-inert divergence → Sprint 27 fix) from Case (c) (MS 5 + no non-inert divergence → Sprint 28 carryforward).
3. **#1387 sign-flip diagnosis** (~1h) — debug-trace `stationarity.py` Lagrangian-conversion on cclinpts to locate the double-negation root.

**Day 1/2 (implementation):**

- **#1387** (~6h after diagnosis, total ~7h including the Day 0/1 sign-flip diagnosis step): apply Bug 1 (sign-flip) fix + Bug 2 (term-omission) fix; regenerate `cclinpts_mcp.gms`; verify per-term grep checks + PATH solve + Tier 0/1 canary byte-stability.
- **#1388** (~3.5–4.5h if Case a/b after Day 0/1 diagnosis pins the actual residual-causing emit bug): apply the diagnosed fix at the identified patch site; OPTIONALLY clean up the boundary-guard form-mismatch noted in §4.3 (cosmetic since fixups zero them); regenerate `camshape_mcp.gms`; verify per-term grep checks + PATH solve + Tier 0/1 canary byte-stability.
- **#1388** (~1.25h if Case c): file Sprint 28 carryforward per §6 template with discriminating evidence (PATH-listing infeasibility-row + warm-start-verification confirming NLP point was loaded); update GitHub labels.

**End of Day 1/2:** Both PRs opened (or Sprint 28 carryforward filed); KNOWN_UNKNOWNS.md §Unknowns 7.1, 7.2, 7.3 updated from this prep's projection to the binding Sprint 27 implementation outcome.

---

## 9. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 8 — this task's specification.
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknowns 7.1, 7.2, 7.3 — research questions this task verifies.
- `docs/issues/ISSUE_1387_*.md` §"Phase 0 Acceptance Gate" — #1387 hand-derived KKT (Sprint 27 Prep Task 2 / PR #1403).
- `docs/issues/ISSUE_1388_*.md` §"Phase 0 Acceptance Gate" — #1388 hand-derived KKT + PROCEED-with-condition signal (same).
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §5.3 (#1335 Approach C) — potential Sprint 28 bundle target IF #1387 escalates to AD-architecture issue.
- `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` (Sprint 27 Prep Task 5) — Sprint 27 Day 0 widening lands cclinpts + camshape in PR19 Pattern C tier for automated regression detection.
- `data/gamslib/mcp/cclinpts_mcp.gms:133-134` (current #1387 emit — buggy reference)
- `data/gamslib/mcp/camshape_mcp.gms:428` (current #1388 emit — suspected-buggy reference)
- `data/gamslib/gamslib_status.json` — Sprint 27 Day 0 baseline: cclinpts at `compare=mismatch`/`rel_diff=1.0`; camshape at `solve=model_infeasible`.
- Source code:
  - `src/ad/derivative_rules.py:1847` (`_diff_sum`) — primary #1387 Bug 2 fix site
  - `src/ad/derivative_rules.py:577` (`_diff_binary`) — secondary #1387 Bug 2 fix site
  - `src/kkt/stationarity.py:1352` (`build_stationarity_equations`) — #1387 Bug 1 fix site
  - `src/kkt/stationarity.py:1835` (`_build_indexed_stationarity_expr`) — #1388 primary fix site
  - `src/ad/constraint_jacobian.py:903,1027` — fallback fix sites for both issues
