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
