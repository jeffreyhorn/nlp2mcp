# otpop: PATH $171 Domain Violations in Stationarity (Sprint 25 Bucket Transfer)

**GitHub Issue:** [#1357](https://github.com/jeffreyhorn/nlp2mcp/issues/1357)
**Status:** OPEN — Sprint 26 carryforward (filed Sprint 25 Day 13). Possibly subsumed by **#1334**.
**Severity:** Medium — model translates cleanly but PATH compilation fails with multiple `$171` errors
**Date:** 2026-05-05
**Last Updated:** 2026-05-05
**Affected Models:** otpop (confirmed)

---

## Problem Summary

After the Sprint 25 wave of otpop fixes (#1232, #1234, #1175, #1178, #1326, #783, #915, plus the Day 12 multi-solve gate #1270 which correctly excluded otpop), the Day 11 retest shows otpop moved from `path_solve_terminated` / `model_infeasible` (depending on era) to **`path_syntax_error`** — the emitted MCP now fails GAMS compilation with **`$171`** ("Domain violation for set") errors at multiple sites.

One of the four bucket additions during Sprint 25 (see SPRINT_LOG.md Day 11 §"Revised Checkpoint 2 evaluation").

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms \
  -o /tmp/otpop_mcp.gms --skip-convexity-check --quiet
gams /tmp/otpop_mcp.gms lo=2

# *** Error 171 in /tmp/otpop_mcp.gms (line 217 ×2, line 247)
# *** Status: Compilation error(s)
```

---

## Diagnostic / Possible Subsumption

The `$171` errors at lines 217 / 247 of the emitted `otpop_mcp.gms` strongly suggest a residual of either:

1. **#1334** — "AD: scalar-constraint stationarity wraps Jacobian terms in spurious Sum when ParamRef domain is a strict subset of equation domain". This issue is open and explicitly lists otpop as the confirmed affected model. The `$171` shape is consistent with the spurious `sum(t__, ...)` over a parameter's declared `t` domain when the equation is over the superset `tt` — GAMS rejects the mismatched domain reference.

2. A new variant of #1175 (subset-superset domain violation in stationarity, CLOSED in Sprint 24). If the closed fix was incomplete or partially regressed by a later Sprint 25 change, this would manifest as a fresh `$171` at related sites.

**Sprint 26 Day 0 action:** verify whether the current `$171` errors at lines 217 / 247 are the same `_replace_indices_in_expr` ParamRef-substitution bug that #1334 documents. If yes, **close this issue as a duplicate of #1334** after the Sprint 26 Day 0 evidence-gathering. If no, this is a new variant requiring its own root cause.

---

## Where to Investigate

1. Open `/tmp/otpop_mcp.gms` (regenerate per "Reproduction") and inspect lines 217 and 247.
2. Match each violating reference back to its source equation in `data/gamslib/raw/otpop.gms`.
3. Compare against the buggy emit shape documented in `docs/issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md` §"Buggy Emit (otpop)". **Note (Sprint 26 Day 9):** #1334 was close-and-refiled to Sprint 27 [#1393](https://github.com/jeffreyhorn/nlp2mcp/issues/1393) with a corrected fix-surface diagnosis (AD `_diff_sum` / `_sum_should_collapse` in `src/ad/derivative_rules.py`, not stationarity-time substitution); the underlying buggy emit shape is unchanged on current main, so the §"Buggy Emit (otpop)" reference remains accurate as a comparison target. Use #1393 (active Sprint 27 carryforward) for cross-references to the work-in-progress fix.
4. If the shape matches (`sum(t__, ...)` over a parameter's declared subset domain): subsumed by #1393 (formerly #1334).
5. If it doesn't: file as a new variant and identify the differing assembly path.

---

## Tests to Add

- **Integration test** in `tests/integration/emit/`: assert otpop's emitted MCP compiles cleanly under GAMS `lo=2`. Currently no such regression test exists.
- If subsumed by #1334: the test under that issue (asserting `stat_x(tt)` and `stat_p(tt)` have no `sum(t__, ...)` substring) should also cover lines 217 / 247.

---

## Files Involved (preliminary)

- `src/kkt/stationarity.py:2295–2479` — `_replace_indices_in_expr` (ParamRef branch — the suspected #1334 site)
- `src/kkt/stationarity.py:5279–5310` — `_add_jacobian_transpose_terms_scalar` (the spurious `Sum` wrap site)
- `data/gamslib/raw/otpop.gms` — source
- `data/gamslib/mcp/otpop_mcp.gms` — current buggy emit

---

## Estimated Effort

- **1–2h** for the Sprint 26 Day 0 subsumption check (if confirmed duplicate of #1334, just close).
- If new: **4–8h** for diagnosis + fix.

---

## Related otpop history (all CLOSED Sprint 23–25)

- #783 (parser: equation attribute assignment)
- #915 (MCP pair unmatched for fixed-var subsets)
- #1175 (subset-superset domain violation in stationarity — same shape family as this issue)
- #1178 (malformed index expressions $145/$148)
- #1232 (stat_d unmatched)
- #1234 (locally infeasible after pairing)
- #1270 (multi-solve gate — correctly excluded otpop in Sprint 25 Day 12)
- #1326 (gtm tangentially related)

---

## Related open issues

- **#1334** (AD: scalar-constraint stationarity spurious Sum on subset ParamRef domain) — likely subsumes this issue.
- **#1335** (AD: missing dzdef/dp cross-term in stat_p) — different bug, also affects otpop's solve correctness; orthogonal to this `$171` issue but on the same model.
- **#1356** (fawley `$171` — also in the four-bucket-additions cohort).
