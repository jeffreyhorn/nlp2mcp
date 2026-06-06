# cclinpts: stat_b / stat_fb condition-guard or sign bug producing ~70% rel_diff (post-Pattern-A reclassification)

**GitHub Issue:** [#1387](https://github.com/jeffreyhorn/nlp2mcp/issues/1387)
**Status:** OPEN — **Sprint 27 Day 6 diagnosis re-scopes this (the documented two-bug framing is partly wrong); see "Day 6 diagnosis" below.**
**Severity:** Medium — MCP cold-solves to a spurious degenerate KKT point (ObjV≈0 vs NLP −3.0011); not a Pattern A AD-layer bug.
**Date:** 2026-05-12
**Last Updated:** 2026-06-06 (Sprint 27 Day 6 — empirical diagnosis: sign "bug" is a misdiagnosis; cross-term form confirmed via residual check; non-convex warm-start need identified)
**Affected Models:** cclinpts
**Target Sprint:** ~~Sprint 27~~ → likely **Sprint 28** (the legitimate fix is a high-blast-radius AD change that, alone, does not deliver the match — non-convex warm-start also required; see Day 6 diagnosis).

## Sprint 27 Day 6 diagnosis (2026-06-06) — empirical; re-scopes the §3.3 two-bug framing

Implementation was greenlit Day 6. Before editing `src/`, traced the actual AD gradient + ran an eliminated-KKT residual check at the NLP optimum. Findings (NO `src/` changes made — all probing on scratch copies):

1. **Bug 1 (sign-flip) is a MISDIAGNOSIS.** The outer `(-1)` in `stat_b`/`stat_fb` is the **standard maximize negation** (`src/ad/gradient.py:265-267`, applied to every MAX model); combined with the inner `(-1)` from `d(b_M − b_j)/db_j` it yields the CORRECT `T1 − T2` signs under the codebase's `stat = −∇f + Jᵀν = 0` convention. `PRIORITY_7_FIX_SURFACE.md` §3.1/§3.3 hand-derived the **un-negated** `∂ObjV` and so flagged a sign error that does not exist. **Do NOT touch the sign logic — it would break every maximize model.**
2. **Bug 2 (missing j+1 offset cross-terms) is REAL, and the corrected form is CONFIRMED.** The per-instance objective gradient omits the `j+1`-offset contributions (where the wrt-variable appears as `fb((j+1)−1)`/`b((j+1)−1)` inside the sum). Hand-patching the emit with the missing **negated** terms — `stat_b += 0.5*(fb(j+1)−fb(j))*1$(not first(j+1))`; `stat_fb += −(b('s30')−b(j))*1$(not last(j)) + (b('s30')−b(j+1))*1$(not last(j+1)) + 0.5*(b(j+1)−b(j))*1$(not first(j+1))` — makes the NLP optimum satisfy the eliminated KKT condition `objgrad_b(j) + b(j)^(−γ)·objgrad_fb(j) = 0` to **max|residual| = 5e-8**. So the cross-term form is correct.
3. **BUT the cross-term fix does NOT make cclinpts MATCH in the cold pipeline.** cclinpts is **non-convex with a spurious degenerate KKT point** (b≈const ⇒ all difference-based gradient terms vanish ⇒ trivially stationary for ANY version of the stat equations, ObjV=0). PATH converges there from BOTH the cold `b=5` start AND a near-optimal ramp start. So §3.6 PROCEED criterion #5 ("MODEL STATUS 1, rel_diff < 1%") **cannot be met by the gradient fix alone** — cclinpts additionally needs an **nlp-presolve warm start** (start PATH at the NLP optimum, which the fix makes a valid KKT point).

**Re-scoped verdict:** the legitimate fix is the **objective-gradient offset cross-term enumeration** (Bug 2) — a **high-blast-radius AD change** (affects every model with an offset-indexed sum in the objective; needs full-corpus byte-stability + re-solve verification) which **on its own does not deliver the cclinpts +1 Solve/Match** (the non-convex warm-start is also required). Recommend implementing the AD cross-term fix as its own focused, fully-verified PR and handling the cclinpts warm-start separately — likely **Sprint 28** given the combined blast radius + non-convexity. The Day-6 probe established the correct target shape + residual-verified acceptance, so the implementation is well-specified for that session.

### Day 6 implementation ATTEMPT (2026-06-06) — AD enumeration done, reverted: hit the re-symbolization-anchor blocker (confirms Sprint 28)

Per a follow-up greenlight, implemented the offset cross-term enumeration in `src/ad/derivative_rules.py` `_diff_sum`'s collapse path (new tightly-gated `_try_diff_sum_offset_crossterms` + `_distinct_var_offsets_in_body` + `_shift_concrete_element`): for a single-index collapsing `Sum` where the wrt-variable appears at ≥1 NON-zero offset of the sum index, sum the per-offset contributions `Σ_δ ∂body/∂var(j+δ)|_{j=W−δ}·c(W−δ)` instead of only the diagonal `δ=0` term. The per-instance derivatives produced are **mathematically correct** (e.g. for ∂/∂b of T2 it generates the `δ=0` term `+(fb(j)−fb(j-1))` and the `δ=−1` term at the shifted element `−(fb(s11)−fb(s10))` for col `b('s10')`).

**Blocker (reverted):** the objective gradient is stored per concrete instance and re-symbolized to the stationarity index downstream by **anchoring on the element that maps to `j`**. The `δ=−1` term is **pure-`fb`** (the `b` dependence is differentiated away), so it contains NO reference to the col index `b('s10')` to anchor on. The re-symbolizer anchors it on `s11` instead of the col index `s10`, mapping `fb(s11)−fb(s10) → fb(j)−fb(j-1)` (offset 0) rather than the correct `fb(j+1)−fb(j)`. The mis-anchored `δ=−1` term then **cancels** the `δ=0` term to zero — leaving cclinpts *worse* than baseline. So the AD enumeration is **necessary but not sufficient**: it also needs a companion fix so the gradient→stationarity re-symbolization anchors a pure-offset term on the **differentiated variable instance's own index** (the col), not on an arbitrary element present in the term. That is a second, separate deep change in the (unexplored) objective-gradient re-symbolization path.

**Decision:** reverted the `_diff_sum` change (tree clean; cclinpts byte-identical to baseline). #1387 → **Sprint 28**: it requires (1) the AD offset-enumeration (done, well-specified above), (2) the re-symbolization-anchor fix, AND (3) the non-convex warm-start — three coupled changes, well beyond the documented "condition-guard or sign bug." This is exactly the §3.7 escalation trigger ("Day-1 diagnosis reveals a broader AD-architecture issue").

### (prior framing — superseded by the Day 6 diagnosis above)
**Cross-references:**
- Predecessor: #1145 (now CLOSED 2026-05-12 via Sprint 26 Day 6 — see [docs/issues/completed/ISSUE_1145_cclinpts-alias-mismatch.md](completed/ISSUE_1145_cclinpts-alias-mismatch.md)).
- Reclassification source: [docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md](../planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md) §"Issue #1145".

## Problem Summary

cclinpts produces `solution_comparison.comparison_status = mismatch` with NLP-MCP rel_diff ~69.9% on the obj. The Sprint 25 Day 7 cohort sweep determined this is NOT a Pattern A AD-layer bug (the emit has legitimate `fb(j-1) * 1$(not last(j))` lag offsets matching the source body) — it's a condition-guard or sign issue downstream of AD.

Sprint 26 Prep Task 4 re-verification (2026-05-07) confirmed Day 7's classification on current main:

```
$ grep -E "^stat_b\(j\)|^stat_fb" /tmp/sprint26-task4-verify/cclinpts_mcp.gms | head -2
stat_b(j).. ((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j)))))
  + 0.5 * (fb(j) - fb(j-1)) * 1$((not first(j)))))
  + ((-1) * ((1 - gamma) * b(j) ** (1 - gamma) * (1 - gamma) / b(j) / sqr(1 - gamma) ...
stat_fb(j).. ((-1) * (0.5 * (b(j) - b(j-1)) * 1$((not first(j)))))
  + nu_FBCalc(j) =E= 0;
```

The `(j-1)` lag offsets matching the source ARE present — so this is NOT the missing-cross-term shape that #1145's "Alias-Aware Gradient Mismatch" framing implied. The 69.9% rel_diff comes from a condition-guard or sign bug somewhere downstream of AD (not yet localized).

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/cclinpts.gms \
  -o /tmp/cclinpts_mcp.gms --skip-convexity-check --quiet
gams /tmp/cclinpts_mcp.gms lo=2
# Compare obj vs cclinpts NLP solve
```

## Investigation pointers

1. Inspect `stat_b(j)` and `stat_fb(j)` emit for sign convention vs the source NLP's `=e=` direction.
2. Look at the `fb(j) - fb(j-1)` / `b(j) - b(j-1)` cross terms — does the AD layer correctly distinguish first-order forward vs first-order backward differences?
3. Compare against a manually-computed KKT for one stationarity equation (Sprint 25 Day 5 methodology).

## Files involved (preliminary)

- `src/kkt/stationarity.py` (likely fix site)
- `data/gamslib/raw/cclinpts.gms` (source)
- `data/gamslib/mcp/cclinpts_mcp.gms` (current emit with the bug)

## Effort estimate

3–6h investigation + fix.

## Related

- **#1145** — closed 2026-05-12 via Sprint 26 Day 6 PR; the original alias-AD framing, reclassified out via Sprint 25 Day 7 cohort sweep + Sprint 26 Prep Task 4 (this issue is the successor).
- Sprint 26 Prep Task 4: `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` §"Issue #1145" — full reclassification rationale.

---

## Phase 0: Acceptance Gate

**Authored:** 2026-05-27 (Sprint 27 Prep Task 2 per PR20 codification)
**Target equation(s):** `stat_b(j)` + `stat_fb(j)` at `data/gamslib/mcp/cclinpts_mcp.gms:133-134`
**Bug class:** Condition-guard / sign bug in the AD-computed gradient of the `object` equation w.r.t. `b(j)` and `fb(j)`. The `(j-1)` lag offsets are correctly present (so NOT a Pattern A AD-layer issue), but the relative-sign between the two `0.5 * (...) * 1$(...)` terms in `stat_fb(j)` may be inverted, or the `1$((not first(j)))` / `1$((not last(j)))` guards may be applied to the wrong terms relative to the source NLP.

### Hand-Derived KKT Shape

Source NLP objective (from `data/gamslib/raw/cclinpts.gms`):

```
object..
   ObjV =e=     sum(j$(not last(j)),  [b('%last%') - b(j)]*[fb(j) - fb(j-1)])
         +  0.5*sum(j$(not first(j)), [b(j) - b(j-1)]*[fb(j) - fb(j-1)]);

FBCalc(j).. fb(j) =e= power(b(j),(1 - gamma))/(1 - gamma);
```

The objective minimizes the area-under-curve approximation using a trapezoid-like sum. Two terms per breakpoint `j`:
- **Term 1 (rectangle, fires for j ∉ last):** `[b(last) - b(j)] * [fb(j) - fb(j-1)]`
- **Term 2 (triangle, fires for j ∉ first):** `0.5 * [b(j) - b(j-1)] * [fb(j) - fb(j-1)]`

For the stationarity equation `stat_b(j)`, hand-derive `∂ObjV / ∂b(j)`:

- Contribution from Term 1 at index `j`: `-1 * [fb(j) - fb(j-1)] * 1$(not last(j))` (the `-b(j)` factor gives `-1`; the `[b(last) - b(j)]` factor's `last` dependency on `j` is handled via the `1$(not last(j))` guard)
- Contribution from Term 1 at index `j+1` (note: `b(j)` appears in the j+1-th term's `fb(j+1) - fb(j)` via `fb(j)`): this is actually a contribution from Term 1 at j via the `fb(j) - fb(j-1)` factor, but partial w.r.t. `b(j)` is through `[b(last) - b(j)]`, not `fb`. So skip.
- Contribution from Term 2 at index `j`: `0.5 * [fb(j) - fb(j-1)] * 1$(not first(j))` (from `+b(j)` factor; sign positive)
- Contribution from Term 2 at index `j+1`: `0.5 * [fb(j+1) - fb(j)] * (-1) * 1$(not first(j+1))` (from `-b(j)` factor inside `[b(j+1) - b(j)]`; sign negative)

Combining for `stat_b(j)`:

```
∂ObjV/∂b(j) = -[fb(j) - fb(j-1)] * 1$(not last(j))                          (Term 1 contribution at j)
            + 0.5 * [fb(j) - fb(j-1)] * 1$(not first(j))                    (Term 2 contribution at j)
            - 0.5 * [fb(j+1) - fb(j)] * 1$(not first(j+1))                  (Term 2 contribution at j+1)

stat_b(j).. ∂L/∂b(j) = 0
         = -∂ObjV/∂b(j) + ∂FBCalc/∂b(j) * nu_FBCalc(j) + (fixup multipliers) - piL_b(j) + piU_b(j)
```

The KEY analysis points are:
1. **Sign of the Term 1 contribution:** Should be NEGATIVE (since `-b(j)` in the `[b(last) - b(j)]` factor). Current emit shows `((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j))))))` — double negation flattens to positive. **Suspected sign bug at the Lagrangian-sign conversion step.**
2. **The Term 2 contribution at j+1 is MISSING from the current emit** — only the Term-2-at-j contribution `0.5 * (fb(j) - fb(j-1)) * 1$((not first(j)))` appears. The `0.5 * (fb(j+1) - fb(j)) * 1$(not first(j+1))` term should also be present with a negative sign.

For `stat_fb(j)`, hand-derive `∂ObjV / ∂fb(j)`:
- Term 1 at j: `[b(last) - b(j)] * (+1) * 1$(not last(j))`
- Term 1 at j+1: `[b(last) - b(j+1)] * (-1) * 1$(not last(j+1))` (`fb(j)` appears as `fb(j+1-1)` with negative sign in `[fb(j+1) - fb(j)]`)
- Term 2 at j: `0.5 * [b(j) - b(j-1)] * (+1) * 1$(not first(j))`
- Term 2 at j+1: `0.5 * [b(j+1) - b(j)] * (-1) * 1$(not first(j+1))`

Current `stat_fb(j)` emit shows only `((-1) * (0.5 * (b(j) - b(j-1)) * 1$((not first(j)))))` — i.e., only the Term-2-at-j contribution with the Lagrangian-sign flip. **Missing all Term 1 contributions + the Term 2 at j+1 contribution.**

### Expected Emit Pattern

```gams
stat_b(j)..
  + (fb(j) - fb(j-1)) * 1$(not last(j))           * (-1)  /* Term 1 at j; Lagrangian-flipped */
  + 0.5 * (fb(j) - fb(j-1)) * 1$(not first(j))    * (-1)  /* Term 2 at j; Lagrangian-flipped */
  - 0.5 * (fb(j+1) - fb(j)) * 1$(not first(j+1))  * (-1)  /* Term 2 at j+1; Lagrangian-flipped */
  + ((1 - gamma) * b(j) ** (1 - gamma) * (1 - gamma) / b(j) / sqr(1 - gamma)) * (-1) * nu_FBCalc(j)
  + nu_b_fx_s1$(sameas(j, 's1')) + nu_b_fx_s30$(sameas(j, 's30'))
  - piL_b(j) + piU_b(j) =E= 0;

stat_fb(j)..
  + (b('s30') - b(j)) * 1$(not last(j))                 * (-1)  /* Term 1 at j */
  - (b('s30') - b(j+1)) * 1$(not last(j+1))             * (-1)  /* Term 1 at j+1 */
  + 0.5 * (b(j) - b(j-1)) * 1$(not first(j))            * (-1)  /* Term 2 at j */
  - 0.5 * (b(j+1) - b(j)) * 1$(not first(j+1))          * (-1)  /* Term 2 at j+1 */
  + nu_FBCalc(j) =E= 0;
```

(The exact sign conventions depend on how nlp2mcp wraps the gradient with the Lagrangian-sign flip; the emit may use a different but equivalent form. The PROCEED criterion is **per-term presence-and-sign verification via pattern-match grep, NOT a literal byte-diff** — see §"Verification Methodology" for the explicit `grep -F` patterns to check, one per expected term. The hand-derived KKT above lists the canonical expected terms; the emit may reorder or differently-parenthesize them. PROCEED if every expected term's pattern-match grep returns ≥ 1 hit AND no unexpected/spurious terms are present.)

### Verification Methodology

The acceptance check is **per-term presence-and-sign verification via pattern-match grep**, NOT a literal byte-diff (the emit may reorder or differently-parenthesize terms vs the canonical hand-derived form).

```bash
# Step 1: regenerate the emit with the prototype fix
.venv/bin/python -m src.cli data/gamslib/raw/cclinpts.gms \
  -o /tmp/cclinpts_mcp.gms --skip-convexity-check --quiet

# Step 2: extract stat_b + stat_fb for visual inspection
grep -nE '^stat_b\(j\)\.\.|^stat_fb\(j\)\.\.' /tmp/cclinpts_mcp.gms > /tmp/stat_b_fb_after.txt
cat /tmp/stat_b_fb_after.txt

# Step 3: per-term presence check — each grep MUST return ≥ 1 hit
# (extracts just the stat_b line to scope the patterns to that equation)
STAT_B=$(grep -E '^stat_b\(j\)\.\.' /tmp/cclinpts_mcp.gms)
STAT_FB=$(grep -E '^stat_fb\(j\)\.\.' /tmp/cclinpts_mcp.gms)

# stat_b(j) MUST contain Term 1 at j (rectangle, fires for j ∉ last)
echo "$STAT_B" | grep -cF 'fb(j) - fb(j-1)' | grep -v '^0$' > /dev/null || echo "MISSING stat_b Term 1: fb(j) - fb(j-1) with last(j) guard"
echo "$STAT_B" | grep -cF 'not last(j)' | grep -v '^0$' > /dev/null || echo "MISSING stat_b last(j) guard"
# stat_b(j) MUST contain Term 2 at j (triangle, factor 0.5, fires for j ∉ first)
echo "$STAT_B" | grep -cE '0\.5.*fb\(j\) - fb\(j-1\)' | grep -v '^0$' > /dev/null || echo "MISSING stat_b Term 2 at j: 0.5 * (fb(j) - fb(j-1))"
echo "$STAT_B" | grep -cF 'not first(j)' | grep -v '^0$' > /dev/null || echo "MISSING stat_b first(j) guard"
# stat_b(j) MUST contain Term 2 at j+1 (the offset-indexed cross-term)
echo "$STAT_B" | grep -cE '0\.5.*fb\(j\+1\) - fb\(j\)' | grep -v '^0$' > /dev/null || echo "MISSING stat_b Term 2 at j+1: 0.5 * (fb(j+1) - fb(j))"

# stat_fb(j) MUST contain all 4 contributions (Term 1 at j, Term 1 at j+1,
# Term 2 at j, Term 2 at j+1). Pre-fix it contains only 1 of 4.
echo "$STAT_FB" | grep -cE 'b\(.*30.*\) - b\(j\)' | grep -v '^0$' > /dev/null || echo "MISSING stat_fb Term 1 at j: b(s30) - b(j)"
echo "$STAT_FB" | grep -cE 'b\(.*30.*\) - b\(j\+1\)' | grep -v '^0$' > /dev/null || echo "MISSING stat_fb Term 1 at j+1: b(s30) - b(j+1)"
echo "$STAT_FB" | grep -cE '0\.5.*b\(j\) - b\(j-1\)' | grep -v '^0$' > /dev/null || echo "MISSING stat_fb Term 2 at j: 0.5 * (b(j) - b(j-1))"
echo "$STAT_FB" | grep -cE '0\.5.*b\(j\+1\) - b\(j\)' | grep -v '^0$' > /dev/null || echo "MISSING stat_fb Term 2 at j+1: 0.5 * (b(j+1) - b(j))"

# Step 4: sign-flip check — confirm no double-negation pattern remains
# (pre-fix shows ((-1) * (((-1) * ...))) which flattens to positive)
echo "$STAT_B" | grep -F '((-1) * (((-1) *' && echo "WARNING: double-negation pattern detected — Lagrangian-sign convention may have a bug"

# Step 5: PATH solve — should reach MODEL STATUS 1 (Optimal) with obj
# matching the NLP solve (rel_diff < 1% post-fix; was 69.9% pre-fix).
#
# Approach A (quick local check via .lst inspection — recommended for the
# Phase 0 prototype iteration). gams writes the .lst to a path determined
# by the `o=` flag; without `o=`, gams defaults to writing
# `<basename>.lst` in the CURRENT WORKING DIRECTORY (NOT alongside the
# input .gms). Pass `o=` explicitly so the .lst location is reproducible:
gams /tmp/cclinpts_mcp.gms lo=2 o=/tmp/cclinpts_mcp.lst
grep -E 'MODEL STATUS|SOLVER STATUS|OBJECTIVE VALUE' /tmp/cclinpts_mcp.lst
# Expected post-fix: MODEL STATUS 1 (Optimal); OBJECTIVE VALUE matches the
# NLP solve's objective (re-run cclinpts as NLP to compare if not cached).
#
# Approach B (full-pipeline verification — recommended before the PR ships,
# to update data/gamslib/gamslib_status.json and confirm rel_diff via the
# canonical solution_comparison stage). gamslib_status.json is produced by
# the pipeline runner, NOT by gams alone; running gams on a single model
# leaves the JSON stale:
.venv/bin/python scripts/gamslib/run_full_test.py --only cclinpts
.venv/bin/python -c "
import json
with open('data/gamslib/gamslib_status.json') as f:
    d = json.load(f)
m = d['models']['cclinpts']
print(f\"comparison: {m.get('solution_comparison', {}).get('comparison_status')}\")
print(f\"rel_diff: {m.get('solution_comparison', {}).get('rel_diff')}\")
"
```

### PROCEED/REPLAN Signal

**PROCEED** with Sprint 27 Priority 7 implementation if ALL of:

- (a) `stat_b(j)` emit contains BOTH the Term-1-at-j contribution AND the Term-2-at-j+1 (`fb(j+1) - fb(j)`) contribution (was missing pre-fix)
- (b) `stat_fb(j)` emit contains all 4 contributions (Term 1 at j, Term 1 at j+1, Term 2 at j, Term 2 at j+1) — was missing 3 of 4 pre-fix
- (c) PATH solve reaches MODEL STATUS 1 with `rel_diff < 1%` (was 69.9% pre-fix)
- (d) Tier 0/1 canary byte-stability preserved

**REPLAN** if:

- (a) Hand-derivation above is wrong — re-derive against the source NLP and update the Expected Emit Pattern before committing src/ changes
- (b) The bug is upstream of stat_b/stat_fb emit (e.g., AD layer's handling of indexed-sum partial derivatives w.r.t. an index-bound variable) — Priority 7 effort estimate may need adjustment + bundle with Priority 3 (AD redesigns)
- (c) PATH solve reaches MODEL STATUS 1 but rel_diff still > 5% — investigate whether the bug is a complementarity sign issue (piL_b / piU_b) rather than a gradient term-omission

