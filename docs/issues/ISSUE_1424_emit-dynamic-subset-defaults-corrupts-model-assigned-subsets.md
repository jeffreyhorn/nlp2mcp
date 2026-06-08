# `_emit_dynamic_subset_defaults` blanket-populates model-assigned dynamic subsets, corrupting constraint domains

**GitHub Issue:** [#1424](https://github.com/jeffreyhorn/nlp2mcp/issues/1424)
**Status:** FIXED (Sprint 27 Day 11, 2026-06-08).
**Severity:** Medium — the emitted MCP solves the *wrong problem* for affected models (constraint domains corrupted). For camshape it also corrupted the `--nlp-presolve` warm-start (embedded NLP infeasible instead of optimal).
**Date:** 2026-06-08
**Affected Models:** camshape (`first/last/middle`) and cclinpts (`first/last`) — genuinely corrupted. ~17 others (qdemo7, cesam2, korcge, srpchase, …) had only a redundant-and-overwritten blanket → byte-only golden change, runtime/solve-identical.

## Problem Summary

`_emit_dynamic_subset_defaults` (`src/emit/emit_gams.py`, Issue #952) emits a blanket `subset(parent) = yes;` for every dynamic subset that (a) has no *static* members and (b) is referenced in a stationarity condition. This is correct for genuinely-empty subsets, but camshape populates `first/last/middle` at runtime **element-wise**:

```gams
first('i1')   = yes;
last('i100')  = yes;
middle(i)     = yes;
middle(first) = no;
middle(last)  = no;
```

The emitted blanket `first(i) = yes; last(i) = yes; middle(i) = yes;` runs *first* and is NOT cleared by the element assignment, so `first`/`last` become the whole parent set and `middle(first) = no` (with `first` = all) empties `middle`. Every constraint domain conditioned on these subsets (`convexity(middle)`, `convex_edge*(first/last)`) is corrupted.

Discovered during the Sprint 27 Day 11 #1388 §4.6 discriminator: camshape's `--nlp-presolve` embedded NLP was MODEL STATUS 4 Infeasible (area=5.009) vs the standalone optimum (area=**4.2841**, MS 2). Removing the blanket restored `first={i1}`, `last={i100}`, `middle={i2..i99}` and a feasible embedded NLP.

## Phase 0: Acceptance Gate

**Authored:** 2026-06-08 (Sprint 27 Day 11; per CONTRIBUTING PR20 — this fix touches `src/emit/`).
**Target surface:** dynamic-subset default population (`_emit_dynamic_subset_defaults` in `src/emit/emit_gams.py`), NOT a KKT-equation shape. This is a set-population bug; the stationarity/complementarity *structure* is unchanged.

### Hand-Derived KKT Shape

The KKT system shape is **unchanged** by this fix. The defect is purely in dynamic-subset *membership*, which gates the `$`-conditions on the (otherwise-correct) constraint and stationarity equations. The correct memberships for camshape (`i = i1..i100`) are:

```
first  = { i1 }
last   = { i100 }
middle = { i2, ..., i99 }   ( = all i except first and last )
```

With these, `convexity(middle(i))` fires for interior points only, `convex_edge1(first(i))` for `i1` only, and `convex_edge3/4(last(i))` for `i100` only — matching the source NLP model (`data/gamslib/raw/camshape.gms:65-71`). The blanket `first(i)=yes` etc. makes `first`/`last` = all `i` and `middle` = ∅, so `convexity` never fires and the edge constraints fire everywhere — a different (wrong) model.

### Expected Emit Pattern

For a dynamic subset the model assigns itself (LHS of a `set_assignment`), the emit must **NOT** add the blanket default — the model's own assignment populates it:

```gams
* CORRECT: no blanket first(i)/last(i)/middle(i) = yes; the model's
* own first("i1")=1; last("i100")=1; middle(i)=1; middle(first)=0; ...
* (re-emitted from the source) populate them.
```

The blanket default is retained ONLY for genuinely model-unpopulated dynamic subsets referenced in stationarity (the original Issue #952 case — e.g. nonsharp's `acol`), which are not in `set_assignments`.

For models that reassign the subset **wholesale** after the blanket (`cn(c)=yes$(...)`, `srn(n)=prob(n)`), removing the blanket is runtime-identical (the wholesale assignment overrides it either way), so those goldens change byte-wise but solve identically.

### Verification Methodology

```bash
# 1. camshape: blanket gone; model's own element assignments retained.
.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms -o /tmp/cs.gms --skip-convexity-check --quiet
grep -cE '^(first|last|middle)\(i\) = yes;' /tmp/cs.gms              # expect: 0
grep -nE 'first\("i1"\)|last\("i100"\)|middle\(first\)' /tmp/cs.gms  # expect: present

# 2. Subset membership correct in a GAMS run.
#    display first, last, middle;  ->  first={i1}, last={i100}, middle={i2..i99}

# 3. No regression on currently-matching models (wholesale-assigned -> byte-only,
#    solve-identical). Re-solve and confirm compare_status unchanged:
.venv/bin/python scripts/gamslib/run_full_test.py --model qdemo7 --only-solve   # stays match
#    (also cesam2, korcge, qabel)

# 4. genuinely-empty subsets still get the blanket (Issue #952 preserved):
#    nonsharp's acol is NOT in set_assignments -> blanket retained.
```

### PROCEED/REPLAN Signal

**PROCEED** if ALL of:

- (a) camshape/cclinpts emit drops the blanket `first/last/middle(i)=yes` lines and retains the model's own assignments; subsets resolve to the correct memberships (Steps 1–2). ✅
- (b) The 4 currently-matching affected models (qdemo7, cesam2, korcge, qabel) stay `compare_match`; the solving-mismatch ones (abel, cclinpts, lmp2) do not regress (Step 3). ✅
- (c) Genuinely model-unpopulated subsets (Issue #952, e.g. nonsharp `acol`) still receive the blanket default (Step 4). ✅

**REPLAN** if:

- A wholesale-assigned model's solve changes (would indicate the wholesale reassignment does not actually override the blanket — execution-order assumption wrong).
- A genuinely-empty subset loses its default (Issue #952 regression — the skip is firing too broadly).

**Result: PROCEED — all criteria met (Sprint 27 Day 11).**

## Fix

`_emit_dynamic_subset_defaults` skips the blanket default for any subset in `model_ir.set_assignments` (model-populated). camshape/cclinpts get correct domains; the ~17 wholesale models change byte-wise but solve identically; genuinely-empty subsets (Issue #952) keep the default.

**Note:** This fix corrects camshape's constraint domains and `--nlp-presolve` warm-start, but does NOT recover camshape's solve — the residual MODEL STATUS 5 (from a valid NLP-KKT warm-start, `stat_r` INFES≈396) is a separate Case-(b) stationarity-emit divergence carried forward to Sprint 28 under [#1388](ISSUE_1388_camshape-path-infeasible.md).
