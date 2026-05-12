# camshape: MCP solves to Locally Infeasible (post-Pattern-E reclassification)

**GitHub Issue:** [#1388](https://github.com/jeffreyhorn/nlp2mcp/issues/1388)
**Status:** OPEN (filed Sprint 26 Day 6, 2026-05-12)
**Severity:** Medium — translate + compile clean but the PATH solve produces `Locally Infeasible (model_status = 5)` with obj=6.2 vs NLP obj=4.2841.
**Date:** 2026-05-12
**Last Updated:** 2026-05-12
**Affected Models:** camshape
**Target Sprint:** Sprint 27 (3–6h investigation + fix)
**Cross-references:**
- Predecessor: #1147 (now CLOSED 2026-05-12 via Sprint 26 Day 6 — see [docs/issues/completed/ISSUE_1147_camshape-alias-compilation-error.md](completed/ISSUE_1147_camshape-alias-compilation-error.md)).
- Sibling (closed Sprint 25): #1160 ("camshape: MCP pairing error — stat_rdiff.rdiff unmatched equation (subset domain mismatch)") — fixed; current bug is distinct.
- Reclassification source: [docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md](../planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md) §"Issue #1147".

## Problem Summary

camshape MCP translates cleanly and compiles cleanly under GAMS `action=c`, but the solve produces `Locally Infeasible (model_status = 5)` with `objective_value = 6.2` vs NLP `objective_value = 4.2841`. The `solution_comparison.comparison_status` is `not_tested` because the solve failed.

This is a **NEW bug** — distinct from the original alias-AD compilation error tracked under now-closed #1147 (the `$141` symbol-not-defined errors), and distinct from the `stat_rdiff.rdiff` pairing error tracked under the also-closed #1160.

Sprint 26 Prep Task 5 re-verification (2026-05-07) on current main:

```
$ .venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
    -o /tmp/sprint26-pattern-e/camshape_mcp.gms --skip-convexity-check --quiet
✓ Generated MCP: /tmp/sprint26-pattern-e/camshape_mcp.gms
translate exit=0, emit lines: 504

$ gams /tmp/sprint26-pattern-e/camshape_mcp.gms action=c lo=2 \
    o=/tmp/sprint26-pattern-e/camshape_compile.lst
(no compile errors — clean)
```

`data/gamslib/gamslib_status.json` records: `nlp2mcp_translate.status = success`; `mcp_solve.status = failure`, `model_status = 5 (Locally Infeasible)`, `objective_value = 6.2` (vs NLP=4.2841), `outcome_category = model_infeasible`.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
  -o /tmp/camshape_mcp.gms --skip-convexity-check --quiet
gams /tmp/camshape_mcp.gms lo=2
# Observed (the bug): MODEL STATUS 5 (Locally Infeasible), obj=6.2
# Expected (no bug):  MODEL STATUS 1 (Optimal), obj ≈ 4.2841 (matching the NLP)
```

## Investigation pointers

1. Compare emitted `stat_*` equations against hand-derived KKT for the camshape model — look for missing or mis-scoped constraints.
2. Check that the previous fix for `nu_eqrdiff.fx` (per #1160 closure) didn't introduce a different pairing imbalance.
3. Run PATH with verbose iteration logging to identify which constraint goes infeasible first.
4. Apply the Sprint 25 Day 5 methodology (trace + emitted-artifact + formal derivative byte comparison) on `stat_rdiff` specifically — that was the focal point of the previous #1147 / #1160 fixes.

## Files involved (preliminary)

- `src/kkt/stationarity.py` — likely
- `src/emit/emit_gams.py` — bound-fixup emission
- `data/gamslib/raw/camshape.gms` — source
- `data/gamslib/mcp/camshape_mcp.gms` — current emit (Locally Infeasible)

## Effort estimate

3–6h investigation + fix. May benefit from coordinated work with Priority 5 (AD residuals) since the symptom shape is unfamiliar.

## Related

- **#1147** — closed 2026-05-12 via Sprint 26 Day 6 PR; the original alias-AD compilation error, partially fixed and reclassified out via Sprint 26 Prep Task 5 (this issue is the successor).
- **#1160** — CLOSED in Sprint 25; fixed the `stat_rdiff.rdiff` unmatched-equation pairing error. The current `Locally Infeasible` solve is a DISTINCT bug not subsumed by #1160's resolved scope.
- Sprint 26 Prep Task 5: `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` §"Issue #1147" — full reclassification rationale.
