# qdemo7: Solve regression — `model_optimal` → `model_infeasible (status 4)`

**GitHub Issue:** [#1352](https://github.com/jeffreyhorn/nlp2mcp/issues/1352)
**Status:** OPEN — investigation done, fix deferred (requires deeper KKT-correctness review)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve, +1 model_infeasible)
**Date:** 2026-05-03
**Affected Models:** qdemo7 (SEQ=292, QCP, Nonlinear Simple Agricultural Sector Model QCP)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`qdemo7` solved at Sprint 25 Day 0 (model_optimal, obj=1134.681). On the current branch solve regresses to global `Infeasible (status 4)` (note: globally infeasible, not "Locally Infeasible" — strictly worse than #1351's status 5).

---

## Investigation results (2026-05-03)

### Root cause located (multiple structural changes)

Diff between Day 0 (`git show 2bcd4b09:data/gamslib/mcp/qdemo7_mcp.gms`) and current branch reveals **multiple post-Day-0 emit changes** that interact to produce structural infeasibility:

1. **#1322 NA-cleanup** added: `beta(c)$(NOT (beta(c) > -inf and beta(c) < inf)) = 0;`
2. **#1192 bounds-collapse guard** wraps `stat_flab(t)` in `$(flab.up(t) - flab.lo(t) > 1e-10)` and adds `flab.fx(t)$(not (flab.up(t) - flab.lo(t) > 1e-10)) = flab.lo(t);` plus multiplier fixes.
3. **stat_exports** gained `((-1) * pe(c))` (an NLP-objective contribution that wasn't being attributed at Day 0).
4. **stat_imports** gained `pm(c)` (similar — missing obj-gradient contribution at Day 0).
5. **stat_natcon** gained `((-1) * (alpha(c) + beta(c) * natcon(c)))` (the QCP demand-curve derivative).
6. **stat_natprod** gained `$(cn(c))` guard on `nu_dem(c)`.
7. The Day 0 line `nu_dem.fx(c)$(not (cn(c))) = 0;` is REMOVED (replaced by the in-equation guard above).

Item (5) is genuinely correct — the QCP source `dem(c)$cn(c).. natcon(c) =e= alpha(c) + beta(c)*natprod(c) + ...` should produce a `natcon`-derivative contribution to `stat_natcon`. Day 0 was missing it.

But the COMBINATION of (1)-(7) — particularly (5) which adds a non-trivial dependence on `alpha`/`beta` parameters that may have problematic values, plus (6) which gates `nu_dem` differently from Day 0 — appears to over-constrain the system and PATH reports global infeasibility.

### Why this is deferred

A proper fix requires:

1. **Identify which structural change tipped the scale**: revert each of the seven changes individually (in a temporary branch off this one) and run `gams data/gamslib/mcp/qdemo7_mcp.gms`. The smallest-set revert that restores `model_optimal` localises the offender.
2. **Fix the offender without losing #1322 / #1192 elsewhere**: the changes weren't gratuitous — `#1322` fixed camcge NA propagation, `#1192` fixed gtm's bounds-collapse listing-time crash. Any qdemo7-specific revert must be conditional or otherwise narrowly scoped.
3. **Verify with the pre-existing mismatch (#918)**: qdemo7's MCP/NLP comparison was already a mismatch at Day 0 due to empty MCP equations for conditionally-absent variables. A successful fix here means status 1 again, not necessarily a comparison match.

Constructing the minimal revert experiments and judging the right scope adjustment is multi-hour work; it doesn't fit inside the same change as the simpler #1350 stationarity-condition remap.

### Local reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/qdemo7.gms -o /tmp/qdemo7_mcp.gms
gams /tmp/qdemo7_mcp.gms lo=2
# → *** EXIT - infeasible.
```

### Pipeline status (post #1350 fix)

The #1350 `_remap_condition_to_domain` fix does NOT affect qdemo7 (verified via diff of pre- and post-fix `qdemo7_mcp.gms`: identical). qdemo7 still fails with `Infeasible (status 4)`.

---

## What must be done before another fix attempt

1. **Targeted revert experiments**: Hand-edit `data/gamslib/mcp/qdemo7_mcp.gms` to revert each of the seven changes (1)-(7) above one at a time, run `gams qdemo7_mcp.gms`, and log which combination(s) produce `model_optimal` again.
2. **Map back to source**: for each "offending" emit change, find the corresponding `src/` source change (`git log --oneline 2bcd4b09..HEAD -- src/`).
3. **Scope the fix**: decide whether the offending change should be (a) reverted entirely (last resort — would re-break the model that motivated it), (b) gated on some model property (e.g., presence of `=g=`/`=l=` constraints with conditional variables), or (c) augmented with an additional fix that re-balances qdemo7's KKT.
4. **Regression cover**: integration test asserting `qdemo7_mcp.gms` reaches `model_optimal` with obj ≈ 1134.681.

---

## Acceptance Criteria (unchanged)

- `qdemo7` solve returns `model_optimal` with obj ≈ 1134.681.
- The pre-existing #918 mismatch is unchanged (covered separately).
- Add a regression test asserting status 1 for qdemo7.

---

## Related

- #918 (open) — qdemo7 empty MCP equations for conditionally-absent variables (pre-existing).
- #1192 — bounds-collapse guard (suspected contributor to current infeasibility via item 2 above).
- #1322 — NA-cleanup (item 1 above).
- Sister regression: `launch` (#1351, similar deferral).
