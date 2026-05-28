# otpop: PATH $171 Domain Violations in Stationarity (Sprint 25 Bucket Transfer)

**GitHub Issue:** [#1357](https://github.com/jeffreyhorn/nlp2mcp/issues/1357)
**Status:** OPEN — Sprint 27 carryforward (filed Sprint 25 Day 13). Comparison target for Sprint 27 [#1393](https://github.com/jeffreyhorn/nlp2mcp/issues/1393) (the close-and-refile successor of #1334 after Sprint 26 Day 9 reclassification).
**Severity:** Medium — model translates cleanly but PATH compilation fails with multiple `$171` errors
**Date:** 2026-05-05
**Last Updated:** 2026-05-27 (Sprint 27 Prep Task 2 — Phase 0 acceptance-gate section authored per PR20 codification; previous update 2026-05-13 Sprint 26 Day 9 — subsumption reference re-routed from #1334 to its Sprint 27 successor #1393; see §"Where to Investigate" step 3 for the close-and-refile rationale).
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

---

## Phase 0: Acceptance Gate

**Authored:** 2026-05-27 (Sprint 27 Prep Task 2 per PR20 codification)
**Target equation(s):** `comp_up_x(tt)$(t(tt) and xb(tt) < inf)` + `piU_x.fx(tt)$(not (t(tt) and xb(tt) < inf))` at `data/gamslib/mcp/otpop_mcp.gms:217` and `:247`
**Bug class:** comp_up subset/superset domain widening — same shape as fawley #1356. The upper-bound complementarity equation is declared over the superset `tt` (all years) but the bound-defining parameter `xb(tt)` is declared over the subset `t(tt)` (post-1973 years only). GAMS evaluates the `xb(tt) < inf` predicate at compile-time across ALL `tt` values, triggering `$171` ("Domain violation for set") at each `tt` outside `t(tt)`.

This Phase 0 mirrors the structure of #1356 since they share the same root cause. Sprint 27 Priority 5 fix applies to both.

### Hand-Derived KKT Shape

Source NLP variable + bound (from `data/gamslib/raw/otpop.gms`):

```
Variable x(tt);          / declared over tt = full year set (1965–1990) /
x.up(t(tt)) = xb(t);     / upper bound on post-1973 subset only /
```

For each `tt ∈ t` (active years 1974+), there is a finite upper bound `xb(tt)` and the complementarity is meaningful: `xb(tt) - x(tt) ≥ 0 ⊥ piU_x(tt) ≥ 0`.
For each `tt ∉ t` (pre-1974), the variable is fixed to a startup value (`x_fx_1965`, etc.); no upper bound exists; multiplier `piU_x(tt)` must be fixed at zero (matched-pair pairing requires it).

Lagrangian-derived complementarity for `tt ∈ t`:

```
L = ... - piU_x(tt) * (xb(tt) - x(tt))    [tt ∈ t only]

∂L/∂piU_x(tt) ≤ 0    ⊥    piU_x(tt) ≥ 0      for tt ∈ t (and xb(tt) < inf)
piU_x(tt) = 0                                       otherwise
```

### Expected Emit Pattern

Same fix shape as #1356. The complementarity equation MUST be domain-narrowed to `t(tt)` at the equation-domain level, NOT just filtered with a flat `$`-conjunction referencing the subset-restricted parameter:

```gams
* CORRECT — domain restricted to t; xb lookup is safe inside the subset
comp_up_x(t)$(xb(t) < inf).. xb(t) - x(t) =G= 0;

* Matched-pair fixup for x(tt) instances outside t
piU_x.fx(tt)$(not t(tt)) = 0;
piU_x.fx(t)$(not (xb(t) < inf)) = 0;
```

Equivalent acceptable form using nested `$`-filters:

```gams
comp_up_x(tt)$(t(tt))$(xb(tt) < inf).. xb(tt) - x(tt) =G= 0;
piU_x.fx(tt)$(not t(tt)) = 0;
piU_x.fx(tt)$(t(tt))$(not (xb(tt) < inf)) = 0;
```

The currently-emitted `$(t(tt) and xb(tt) < inf)` flat-conjunction form (`data/gamslib/mcp/otpop_mcp.gms:217`) does NOT short-circuit at the parameter-lookup level — GAMS attempts the `xb(tt)` lookup at compile-time for all `tt` values before evaluating the conjunction.

### Verification Methodology

```bash
# Step 1: regenerate the emit with the prototype fix
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms \
  -o /tmp/otpop_mcp.gms --skip-convexity-check --quiet

# Step 2: compile-check — MUST succeed without $171 errors
gams /tmp/otpop_mcp.gms action=c lo=2 o=/tmp/otpop_compile.lst
grep -cE '\*\*\* Error 171' /tmp/otpop_compile.lst
# Expected: 0 (was 3 pre-fix at lines 217×2, 247)

# Step 3: verify the comp_up_x + piU_x.fx emit shape matches the expected pattern
grep -nE '^comp_up_x|^piU_x\.fx' /tmp/otpop_mcp.gms
# Expected: comp_up_x declared over t (or nested $(t(tt))$(...));
# piU_x.fx has separate fixup for "not t(tt)" instances

# Step 4: PATH solve — should compile (Step 2) AND reach a non-$171 outcome.
# NOTE: otpop also has #1335 (missing nu_zdef cross-term) + #1393 (scalar-eq
# Sum-collapse from #1334) bugs that produce model-correctness errors
# orthogonal to this $171 issue. Phase 0 PROCEED here verifies ONLY that
# the comp_up shape compiles cleanly — full MODEL STATUS 1 also requires
# #1393 + #1335 fixes (Sprint 27 Priority 3).
gams /tmp/otpop_mcp.gms lo=2 | grep -E 'MODEL STATUS|SOLVER STATUS'
```

### PROCEED/REPLAN Signal

**PROCEED** with Sprint 27 Priority 5 implementation if ALL of:

- (a) Compile produces 0 `$171` errors (was 3 pre-fix)
- (b) Emit shape matches one of the two acceptable forms above
- (c) Tier 0/1 canary byte-stability preserved
- (d) fawley (#1356) ALSO compiles cleanly under the same fix (since they share root cause; PROCEED requires the fix is general enough to cover both)

**REPLAN** if:

- (a) Compile still produces `$171` errors → investigate whether the nested-`$` form is being flattened by an emit-pipeline normalization step
- (b) fawley still fails → fix is otpop-specific (e.g., model-name-guarded prototype); needs generalization before Priority 5 commit
- (c) Solve produces #1393 / #1335 errors (e.g., wrong `stat_x(tt)` shape, missing `nu_zdef` cross-term) — these are EXPECTED at Phase 0 time and do not block #1357 PROCEED; they require separate Priority 3 fixes

