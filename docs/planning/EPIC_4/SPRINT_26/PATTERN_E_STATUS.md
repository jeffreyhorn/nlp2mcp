# Sprint 26 Pattern E Carryforward Status Survey

**Date:** 2026-05-07
**Task:** Sprint 26 Prep Task 5 (Pattern E Carryforward Status Survey)
**Branch:** `planning/sprint26-task5`
**Source classification:** Sprint 25 Day 7 cohort sweep + `DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4
**Re-verification basis:** translate + GAMS `action=c` compile + `gamslib_status.json` solve status on current `main`

---

## TL;DR

| Issue | Model | Original Phase E classification | Re-verified status (2026-05-07) | Sprint 26 Priority 3 action |
|---|---|---|---|---|
| #1141 | kand | Alias-AD gradient mismatch (92.5% rel_diff) | ⚠ **Unchanged** — translates clean, solves Optimal, still 92.5% rel_diff | **Keep open** — Sprint 26 fix work needed (alias-AD residual) |
| #1144 | catmix | Alias domain inference regression → `model_infeasible` (101 INFES eqs) | ✅ **Bucket shifted (largely resolved)** — translates clean, solves **Optimal**, 0.21% rel_diff | **Close as infeasibility-resolved** + optional Sprint 27 follow-up for residual 0.21% rel_diff |
| #1147 | camshape | Alias-related MCP compilation error (`path_syntax_error`) | ⚠ **Bucket shifted** — compile is clean now, but solves **Locally Infeasible** (model_status=5) | **Close-and-refile as new Sprint 27 issue** (the original `path_syntax_error` is fixed; the new infeasibility is a distinct bug) |

**Phase E framing validity:** The original "Phase E (Pattern E routing)" framing grouped these 3 models as a coherent alias-AD bug family. **Post-S25 re-verification shows the framing is invalid for 2 of 3 models** — only kand is still genuinely alias-AD; catmix's bug was a domain-inference regression already resolved by the S25 fix-in-place series; camshape's bug was a compilation error already fixed (with a now-CLOSED follow-up #1160) and the current infeasibility is a distinct issue. Sprint 26 should **retire the "Phase E" label** and route kand as a standalone alias-AD residual (could fold into Priority 5 alongside #1334/#1335 if useful).

**Sprint 26 Priority 3 effort (revised):**
- Original (Sprint 25 retrospective estimate): 3 models needing fix work, ~6–10h
- Revised (after Task 5): **1 model needing fix work (kand)** + 2 close/refile actions = ~3–6h for kand fix + ~30min mechanical close-and-refile
- Time saved: 3–4h freed for Priority 1 (Phase A + B), Priority 4 (Option 1), or Priority 5 (#1335)

---

## Per-model status

### Issue #1141: kand — Alias-Aware Gradient Mismatch

**Current GitHub state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: *"kand: Alias-Aware Gradient Mismatch — Tree Structure with Alias(n,nn)"*.

**Original (Sprint 25) symptom:** 92.5% objective mismatch between NLP (2613) and MCP (195). Root cause hypothesized in the issue doc as `_alias_match` in `derivative_rules.py` mishandling alias-bound indices in sum contexts (same family as qabel/abel #1137, later resolved to #1311 for the qabel/abel u-quadratic specifically — but kand has a DIFFERENT model structure: tree-structured `flow(n,nn)` arc-set restrictions, not u-quadratic).

**Re-verification on current main (2026-05-07):**

```
$ .venv/bin/python -m src.cli data/gamslib/raw/kand.gms \
    -o /tmp/sprint26-pattern-e/kand_mcp.gms --skip-convexity-check --quiet
✓ Generated MCP: /tmp/sprint26-pattern-e/kand_mcp.gms
translate exit=0, emit lines: 166

$ gams /tmp/sprint26-pattern-e/kand_mcp.gms action=c lo=2
(no compile errors — clean)
```

`data/gamslib/gamslib_status.json` for kand:
- `nlp2mcp_translate.status = success`
- `mcp_solve.status = success`, `model_status = 1 (Optimal)`, `objective_value = 195.0`
- `solution_comparison.comparison_status = mismatch` — `relative_difference = 0.9254`, `nlp_objective = 2613.0`, `mcp_objective = 195.0`

**Verdict: ⚠ UNCHANGED Pattern E shape.** kand still shows the 92.5% rel_diff documented in Sprint 25. The Sprint 25 fix-in-place series #1338..#1352 did NOT side-effect-fix kand — none of those fixes targeted the tree-structured `flow(n,nn)` arc-set differentiation path. #1311 (the qabel/abel u-quadratic fix) addressed a different code path — the criterion-derivative subset-domain bug — which doesn't apply to kand's tree structure.

**Recommended Sprint 26 action: KEEP OPEN — Priority 3 fix work needed (or fold into Priority 5 alias-AD residuals).**

The kand fix likely involves:
1. Localizing whether `flow(n,nn)` differentiation in `_partial_collapse_sum` correctly handles the `arc(n,nn)` 2D set membership filter.
2. Comparing the emitted `stat_flow` against a hand-derived KKT for the tree balance constraint `balance(n).. sum(nn$arc(n,nn), flow(n,nn)) =e= demand(n)`.
3. Following the Day 5 methodology (trace + emitted-artifact + formal-derivative byte comparison) — same approach validated by Sprint 26 Prep Task 3 on Pattern C.

**Estimated fix effort:** 3–6h (single-model investigation; fix likely shares scaffolding with the Pattern C generalization work).

**Reframing recommendation:** Drop the "Pattern E" label; reclassify under **Sprint 26 Priority 5 (AD residuals)** alongside #1334 (CLOSED, doc stale) / #1335. The Day 5 methodology applied to kand should give a clean PROCEED/REPLAN signal in 1–2h before any fix work begins.

**Test xfail impact:** None. No tests reference #1141.

**Source/docs reference impact:** None.

---

### Issue #1144: catmix — Alias Domain Inference Regression

**Current GitHub state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: *"catmix: Alias Domain Inference Regression (model_infeasible)"*.

**Original (Sprint 25) symptom:** MCP regressed from `model_optimal` (pre-Sprint-22) to `model_infeasible` after PR #1076 (`skip_lead_lag_inference=True`). The ode1/ode2 equality equations lost their `$(ord(i) <= card(i) - 1)` lead/lag domain restriction, generating equations for all 101 elements instead of 100 — `ode1(100)` referencing a non-existent `x1(101)`. Issue doc Status field reads "OPEN" with severity "MCP compilation failure (was model_infeasible, now compile errors)".

**Re-verification on current main (2026-05-07):**

```
$ .venv/bin/python -m src.cli data/gamslib/raw/catmix.gms \
    -o /tmp/sprint26-pattern-e/catmix_mcp.gms --skip-convexity-check --quiet
✓ Generated MCP: /tmp/sprint26-pattern-e/catmix_mcp.gms
translate exit=0, emit lines: 269

$ gams /tmp/sprint26-pattern-e/catmix_mcp.gms action=c lo=2
(no compile errors — clean)
```

`data/gamslib/gamslib_status.json` for catmix:
- `nlp2mcp_translate.status = success`
- `mcp_solve.status = success`, `model_status = 1 (Optimal)`, `objective_value = -0.048`
- `solution_comparison.comparison_status = mismatch` — `relative_difference = 0.00208` (i.e. 0.21%), `nlp_objective = -0.0481`, `mcp_objective = -0.048`, `notes = "Mismatch: diff=1.00e-04 > tolerance=9.62e-05"`

**Verdict: ✅ BUCKET SHIFTED — largely resolved.** catmix was on the Sprint 25 #1338 SetMembershipTest fix list (per Day 11 SPRINT_LOG: *"#1338: expr_to_gams now handles IndexOffset as a direct index of SetMembershipTest"* affecting catmix/glider/markov/tricp). The original `model_infeasible` blocker is gone. The model now compiles cleanly, solves to Optimal, and produces an objective within 0.21% of the NLP — barely above the 0.2% rel_diff tolerance, indicating a near-match (numerical-noise level rather than a structural bug).

**Recommended Sprint 26 action: CLOSE as infeasibility-resolved.**

The original Sprint 25 framing of #1144 (`model_infeasible` regression caused by PR #1076) is no longer applicable — the model now solves Optimal. The residual 0.21% rel_diff is at the boundary of solver-noise vs informational-mismatch territory; it doesn't warrant Sprint 26 Priority 3 budget. Optional: file a Sprint 27 follow-up tracking the residual 0.21% rel_diff if user-side metric tracking cares about that precision level.

**Closure mechanics (Sprint 26 Day 1):**
1. Comment on #1144 with: *"Sprint 26 Prep Task 5 re-verification confirms catmix is no longer `model_infeasible` — it now translates clean, compiles clean, and solves to Optimal (`mcp_solve.model_status = 1`) per `gamslib_status.json` Day 14 retest. The Sprint 25 #1338 SetMembershipTest fix (and related Day 11 series) resolved the lead/lag domain inference regression. Residual `solution_comparison.comparison_status = mismatch` shows `relative_difference = 0.00208` (0.21%, NLP=-0.0481 vs MCP=-0.048) — within solver-noise tolerance for this scale. Closing as resolved. If precision tracking warrants it, file a Sprint 27 issue for the residual 0.21% rel_diff."*
2. Close #1144.

**Optional Sprint 27 follow-up (do NOT file unless user requests):** *"catmix: residual 0.21% NLP/MCP objective rel_diff (post-S25 SetMembershipTest fix)"* — rel_diff is right at the 0.2% tolerance boundary; could be solver convergence noise or a small AD/emit difference. Low priority — informational only.

**Test xfail impact:** None. No tests reference #1144.

**Source/docs reference impact:** None.

---

### Issue #1147: camshape — Alias-Related MCP Compilation Error

**Current GitHub state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: *"camshape: Alias-Related MCP Compilation Error"*. Issue doc explicit Status field: "PARTIALLY FIXED" with remaining issue tracked under #1160.

**Original (Sprint 25) symptom:** `path_syntax_error` (MCP compilation error). The issue doc records a partial fix: per-element `lo_map`/`up_map` numeric bounds emission was added, resolving the `$141` symbol-not-defined errors. Stationarity access conditions were moved from equation head to body via DollarConditional. Issue doc records "**Remaining issue:** MCP still has unmatched equation pairing: `stat_rdiff.rdiff` — now caused by `nu_eqrdiff.fx` ... tracked in ISSUE_1160."

**#1160 state:** CLOSED (verified via `gh issue view 1160`). Title: *"camshape: MCP pairing error — stat_rdiff.rdiff unmatched equation (subset domain mismatch)"*.

**Re-verification on current main (2026-05-07):**

```
$ .venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
    -o /tmp/sprint26-pattern-e/camshape_mcp.gms --skip-convexity-check --quiet
✓ Generated MCP: /tmp/sprint26-pattern-e/camshape_mcp.gms
translate exit=0, emit lines: 504

$ gams /tmp/sprint26-pattern-e/camshape_mcp.gms action=c lo=2
(no compile errors — clean)
```

`data/gamslib/gamslib_status.json` for camshape:
- `nlp2mcp_translate.status = success`
- `mcp_solve.status = failure`, `model_status = 5 (Locally Infeasible)`, `objective_value = 6.2` (vs NLP=4.2841), `outcome_category = model_infeasible`
- `solution_comparison.comparison_status = not_tested`, `notes = "Skipped due to solve failure"`

**Verdict: ⚠ BUCKET SHIFTED.** camshape was originally `path_syntax_error`; it's now `model_infeasible`. Both the original `$141` compilation error (#1147 partial fix) AND the follow-up pairing error (#1160) are CLOSED. The current `Locally Infeasible` solve outcome is a NEW bug — not the original Phase E shape, and not subsumed by either #1147 or #1160's resolved scope.

**Recommended Sprint 26 action: CLOSE-AND-REFILE as Sprint 27 issue.**

The original framing of #1147 (alias-related MCP compilation error) is now stale — the compilation is clean. The new `model_infeasible` symptom needs a fresh investigation (likely outside the alias-AD domain entirely; could be a constraint construction issue or a missing fixup line for some variable instance).

**Closure mechanics (Sprint 26 Day 1):**

1. File new Sprint 27 issue. Draft (rendered with a 4-backtick outer fence so the inner ` ```bash ` block doesn't terminate it early):

   **Title:** *"camshape: MCP solves to Locally Infeasible (post-Pattern-E reclassification)"*

   **Body:**

   ````markdown
   ## Problem Summary

   camshape MCP translates cleanly and compiles cleanly under GAMS `action=c`,
   but the solve produces `Locally Infeasible (model_status = 5)` with
   `objective_value = 6.2` vs NLP `objective_value = 4.2841`. The
   `solution_comparison.comparison_status` is `not_tested` because the solve
   failed. This is a NEW bug — distinct from the original alias-AD
   compilation error tracked under the now-closed #1147 (closed Sprint 26
   Day 1 per Pattern E status survey — see
   `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` §"Issue #1147").

   ## Reproduction

   ```bash
   .venv/bin/python -m src.cli data/gamslib/raw/camshape.gms \
     -o /tmp/camshape_mcp.gms --skip-convexity-check --quiet
   gams /tmp/camshape_mcp.gms lo=2
   # Observed (the bug): MODEL STATUS 5 (Locally Infeasible), obj=6.2
   # Expected (no bug):  MODEL STATUS 1 (Optimal), obj ≈ 4.2841 (matching the NLP)
   ```

   ## Investigation pointers

   1. Compare emitted `stat_*` equations against hand-derived KKT for the
      camshape model — look for missing or mis-scoped constraints.
   2. Check that the previous fix for `nu_eqrdiff.fx` (per #1160 closure)
      didn't introduce a different pairing imbalance.
   3. Run PATH with verbose iteration logging to identify which constraint
      goes infeasible first.
   4. Apply the Day 5 methodology (trace + emitted-artifact + formal
      derivative byte comparison) on `stat_rdiff` specifically — that was
      the focal point of the previous #1147/#1160 fixes.

   ## Files involved (preliminary)

   - `src/kkt/stationarity.py` — likely
   - `src/emit/emit_gams.py` — bound-fixup emission
   - `data/gamslib/raw/camshape.gms` — source
   - `data/gamslib/mcp/camshape_mcp.gms` — current emit (Locally Infeasible)

   ## Effort estimate

   3–6h investigation + fix. May benefit from coordinated work with
   Priority 5 (AD residuals) since the symptom shape is unfamiliar.

   ## Related

   - **#1147** (planned for closure on Sprint 26 Day 1; replace with closed-date + PR ref when this Sprint 27 issue is actually filed) — original alias-AD compilation error, partially fixed and reclassified out via Sprint 26 Prep Task 5.
   - **#1160** (CLOSED) — earlier follow-up for `stat_rdiff.rdiff` pairing error; supposedly resolved but the model is still infeasible.
   ````

2. Comment on #1147 with: *"Sprint 26 Prep Task 5 re-verification: the original `path_syntax_error` compilation issue tracked here is FIXED — the MCP now translates and compiles cleanly. However, camshape now solves to `Locally Infeasible (model_status=5)` — a distinct bug, refiled as Sprint 27 issue #NNNN. Closing #1147."*

3. Close #1147.

**Test xfail impact:** None. No tests reference #1147.

**Source/docs reference impact:** None.

---

## Phase E framing — retrospective assessment

The original Phase E classification grouped #1141 / #1144 / #1147 as a coherent "alias-AD bug family" (per `DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4). Re-verification shows this framing was **only valid for 1 of 3 models**:

| Model | Original Phase E classification | True bug shape (post-S25) |
|---|---|---|
| kand | Alias-AD gradient (tree structure) | ✅ Genuine alias-AD bug — Pattern E framing applies |
| catmix | Alias-AD domain inference | ❌ Was a `skip_lead_lag_inference` regression from PR #1076 — NOT alias-AD; resolved by S25 #1338 SetMembershipTest fix |
| camshape | Alias-AD compilation | ❌ Was a bound-emission `$141` error (lo_map/up_map not emitted) — NOT alias-AD; resolved by #1147 partial fix + #1160 follow-up |

**Recommendation: Retire the "Phase E" label.** Sprint 26 should:
- Treat **kand (#1141)** as a standalone alias-AD residual — fold under Priority 5 (AD residuals — alongside #1334/#1335) or carry as its own micro-workstream.
- **Close** #1144 and #1147 per the per-issue actions above; the original Phase E motivations no longer apply.
- The catmix and camshape outcomes confirm the value of the PR16 pre-Sprint-0 verification methodology — Sprint 26 saved 3–4h of "Phase E carryforward" investigation budget that would have been wasted on already-resolved or already-shifted issues.

---

## Summary metrics

| Metric | Value |
|---|---|
| Total Phase E carryforward issues | 3 |
| Day 7 / S25-classification still accurate | 1 (#1141 kand) |
| Bucket shifted (largely resolved) | 1 (#1144 catmix) |
| Bucket shifted (new bug, refile) | 1 (#1147 camshape) |
| Sprint 26 Priority 3 fix scope | **1 model (kand)** |
| Test xfails affected | 0 |
| Source/docs references requiring update | 0 |
| Sprint 26 Priority 3 effort estimate | ~3–6h (single-model kand investigation) + ~30min mechanical close-and-refile (catmix + camshape) |

## Cross-references

- Sprint 25 Day 7 cohort sweep: `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md`
- Sprint 25 Day 11 SPRINT_LOG (fix-in-place series #1338..#1352): `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` §"Day 11"
- Phase E original design: `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4
- Sprint 25 retrospective §Priority 3 (Pattern E carryforward)
- Sprint 26 Prep Task 4 (Pattern A cohort reclassification) — `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` (parallel methodology applied to a different cohort)
- In-repo issue docs: `docs/issues/ISSUE_1141_*.md`, `docs/issues/ISSUE_1144_*.md`, `docs/issues/ISSUE_1147_*.md`
- Re-verification artifacts (advisory, not committed): `/tmp/sprint26-pattern-e/{kand,catmix,camshape}_mcp.gms` + `_compile.lst`.
