# cclinpts: stat_b / stat_fb condition-guard or sign bug producing ~70% rel_diff (post-Pattern-A reclassification)

**GitHub Issue:** [#1387](https://github.com/jeffreyhorn/nlp2mcp/issues/1387)
**Status:** OPEN (filed Sprint 26 Day 6, 2026-05-12)
**Severity:** Medium — produces a valid MCP solve but with ~70% rel_diff vs the NLP optimum; not a Pattern A AD-layer bug.
**Date:** 2026-05-12
**Last Updated:** 2026-05-12
**Affected Models:** cclinpts
**Target Sprint:** Sprint 27 (3–6h investigation + fix)
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

(The exact sign conventions depend on how nlp2mcp wraps the gradient with the Lagrangian-sign flip; the emit may use a different but equivalent form. The PROCEED criterion is that the BYTE-COMPARED emit matches the hand-derived KKT modulo trivial algebraic simplifications.)

### Verification Methodology

```bash
# Step 1: regenerate the emit with the prototype fix
.venv/bin/python -m src.cli data/gamslib/raw/cclinpts.gms \
  -o /tmp/cclinpts_mcp.gms --skip-convexity-check --quiet

# Step 2: extract stat_b + stat_fb and compare against hand-derived form
grep -nE '^stat_b\(j\)\.\.|^stat_fb\(j\)\.\.' /tmp/cclinpts_mcp.gms > /tmp/stat_b_fb_after.txt
cat /tmp/stat_b_fb_after.txt

# Step 3: PATH solve — should reach MODEL STATUS 1 (Optimal) with obj
# matching the NLP solve (rel_diff < 1% post-fix; was 69.9% pre-fix)
gams /tmp/cclinpts_mcp.gms lo=2
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

