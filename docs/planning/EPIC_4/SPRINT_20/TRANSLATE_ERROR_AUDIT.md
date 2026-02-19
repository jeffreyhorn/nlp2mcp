# Sprint 20: Translate Error Audit

**Created:** 2026-02-19
**Task:** Sprint 20 Prep Task 5
**Unknowns Addressed:** 7.1, 7.2, 8.1

---

## Executive Summary

**Translate internal_error count (current): 2** (not 5 — the status JSON was stale).

Three models previously recorded as `internal_error` (orani, prolog, ramsey) now translate
successfully. The Sprint 19 fixes silently resolved them but the status JSON was not re-run.
Only **2 genuine translate-stage internal errors remain**: maxmin (smin aggregation AD rule)
and mlbeta (loggamma/digamma function). Both require deferred architectural work.

**`model_no_objective_def` count: 14 models** (all at parse stage, not translate stage).
Root cause: `process_conditionals` in `src/ir/preprocessor.py` incorrectly treats the
`solve` statement as the excluded body of a preceding `$if set workSpace` directive.
This is a **single preprocessor bug** that affects 13 of the 14 models. The 14th (lmp2)
has its solve in a doubly-nested loop beyond Issue #749's one-level extraction.

---

## Part 1: Translate internal_error Models

### Current Status (True Failures)

Status JSON showed 5 `internal_error` models. Re-running confirms only **2 remain**:

| Model | File | Exception | Function | Root Cause | S20 Fixable? |
|-------|------|-----------|----------|------------|-------------|
| maxmin (Max Min Location) | `maxmin.gms` | `ValueError` | `_diff_smin` (derivative_rules.py:1216) | smin aggregation form: `smin(set, expr)` uses 3 AST args; AD rule expects 2-arg scalar `smin(a,b)` | **Deferred** |
| mlbeta (Beta Distribution MLE) | `mlbeta.gms` | `ValueError` | `_diff_call` (derivative_rules.py:595) | `loggamma(x)` derivative requires digamma/ψ function unavailable in GAMS | **Deferred** |

### Models That Were Stale in Status JSON (Now Fixed)

| Model | File | Old Status JSON Message | Current Status |
|-------|------|------------------------|----------------|
| Orani 78 | `orani.gms` | `Differentiation of 'gamma' requires digamma/psi` | ✅ **SUCCESS** |
| Market Equilibrium | `prolog.gms` | `SetMembershipTest not yet implemented` | ✅ **SUCCESS** |
| Ramsey Savings | `ramsey.gms` | `Equation 'tc' domain set 'tlast' has no members` | ✅ **SUCCESS** |

All three were fixed by Sprint 19 work but the `gamslib_status.json` was not refreshed.

---

### Detailed Root Cause Analysis

#### maxmin.gms — `smin()` Aggregation Form

**Error:** `ValueError: smin() expects 2 arguments, got 3`
**Location:** `src/ad/derivative_rules.py:1216` in `_diff_smin()`

**Root cause:** GAMS has two forms of `smin`:
1. **Scalar form:** `smin(a, b)` — returns the smaller of two values (2 args)
2. **Aggregation form:** `smin(set, expr)` or `smin(i, j, expr)` — returns min over a set (2–3 args)

The AD rule `_diff_smin` only handles the 2-argument scalar form. maxmin.gms uses
the aggregation form in two equations:

```gams
mindist2..  mindist =e= smin(low, dist(low));           * 2 args: (set, expr)
mindist2a.. mindist =e= smin(low(n,nn), sqrt(...));     * 3 args: (n, nn, expr)
```

Parsed as:
- `Call(smin, (SymbolRef(low), VarRef(dist)))` — 2 args but set-indexed form
- `Call(smin, (SymbolRef(n), SymbolRef(nn), Call(sqrt, ...)))` — 3 args

**Why deferred:** The smin aggregation form is mathematically equivalent to `min over set`,
which the reformulation layer should convert to auxiliary variables (like sum/prod). Adding
proper handling requires: (a) distinguishing scalar vs. aggregation smin at parse time, and
(b) applying the min/max reformulation pass to aggregation smin. Estimated ~4–6h. Not a
trivial AD rule addition.

---

#### mlbeta.gms — `loggamma()` Derivative Unavailable

**Error:** `ValueError: Differentiation of 'loggamma' requires the digamma/psi function`
**Location:** `src/ad/derivative_rules.py:595` in `_diff_call()`

**Root cause:** `loggamma(x) = log(Γ(x))`. Its derivative is `ψ(x)` (digamma function),
which GAMS does not support as a built-in function. The AD system explicitly raises on
this case. orani.gms had the same issue with `gamma(x)` — but that was apparently resolved
(possibly by an alternative formulation path).

**Why deferred:** Cannot emit the derivative in GAMS syntax — no digamma function available.
Would require a special-case approximation or declaration that this model is not convertible.
The current explicit error message is correct; this is not a Sprint 20 fix.

---

## Part 2: Other Translate Failures (Non-internal_error)

These are recorded in the status JSON but are not `internal_error` category:

| Model | File | Category | Root Cause | S20 Fixable? |
|-------|------|----------|------------|-------------|
| Decomposition | `decomp.gms` | `codegen_numerical_error` | `rep[2,gap]` parameter has `+Inf` value | Deferred (requires special Inf handling) |
| Gas Transmission | `gastrans.gms` | `codegen_numerical_error` | `Ndata[Antwerpen,slo]` parameter has `-Inf` value | Deferred |
| Gas Trade Model | `gtm.gms` | `codegen_numerical_error` | `sdat[alaska,limit]` parameter has `+Inf` value | Deferred |
| Aluminum Smelter | `ibm1.gms` | `codegen_numerical_error` | `bspec[aluminum,maximum]` parameter has `+Inf` value | Deferred |
| Indus Water | `iswnm.gms` | `timeout` | Translation exceeds 60s limit | Deferred |

**codegen_numerical_error pattern:** All 4 models use `+Inf`/`-Inf` as parameter values
(representing "no upper/lower bound"). GAMS supports this natively but the validator
`validate_parameter_values` raises when it encounters IEEE infinity. Fix would require
treating `+Inf` parameter values as "no bound" and emitting appropriate `.up = +Inf` in the MCP.

---

## Part 3: model_no_objective_def Models (Parse Stage)

**Total count: 14 models** — all fail at parse stage with `model_no_objective_def`.

### Root Cause: `process_conditionals` Eats Solve Statement

**13 of 14 models** share identical root cause: a `$if set workSpace` directive on the
line immediately before the `solve` statement:

```gams
$if set workSpace <model>.workSpace = %workSpace%

solve <model> using nlp minimizing/maximizing <var>;
```

`process_conditionals` in `src/ir/preprocessor.py` evaluates `$if set workSpace` as
`False` (since `workSpace` is not defined in macros) and incorrectly treats the **next
line** — the `solve` statement — as the excluded body of the conditional.

After preprocessing, the output contains:
```
* [Conditional: $if set workSpace <model>.workSpace = %workSpace%]

* [Excluded: solve <model> using nlp maximizing <var>;]

* [Warning: 1 unclosed $if directive(s)]
```

**This is a preprocessor bug.** The `$if set workSpace` line is a **single-line inline
conditional** where the guarded statement is on the **same line** as the `$if`:
```
$if set workSpace   <statement-to-guard>
```
The statement `<model>.workSpace = %workSpace%` is the guarded content, not the following
line. The preprocessor's line-based parsing misidentifies the next line as the excluded body.

**The 1 model with different root cause:**

| Model | File | Root Cause |
|-------|------|------------|
| `lmp2.gms` | Linear Multiplicative Model | Solve inside **doubly-nested loop** (`loop(c, loop(i, solve...))`) — Issue #749 only extracts from one level of nesting |

### Complete model_no_objective_def Model List

| Model | File | $if Bug? | $if Pattern | Solve Statement |
|-------|------|----------|-------------|-----------------|
| Shape optimization cam | `camshape.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve camshape using nlp maximizing area` |
| Catalyst Mixing | `catmix.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve catmix minimizing obj using nlp` |
| Hanging Chain | `chain.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve chain using nlp minimizing energy` |
| ClearLake exercise | `clearlak.gms` | ✅ yes | `$if set noscenred $goTo` (unclosed, excludes solve) | `solve mincost using lp min ec` |
| Dantzig Wolfe | `danwolfe.gms` | ✅ yes | `$if set` block (unclosed, excludes solve) | `solve master using lp minimizing z` (in loop) |
| Electrons on sphere | `elec.gms` | ✅ yes | `$if not set np $set np 25` (line 32, unclosed — excludes everything through EOF) | `solve elec using nlp minimizing potential` |
| Feasopt | `feasopt1.gms` | ✅ yes | `$ifI %system.lp%` variants (unclosed, excludes solve) | `solve transport using lp minimizing z` |
| Linear Multiplicative | `lmp2.gms` | ❌ no | (no `$if`) | `solve lmp2 minimizing obj using nlp` (doubly-nested loop — different root cause) |
| Particle steering | `lnts.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve lnts using nlp minimizing tf` |
| Parts Supply | `partssupply.gms` | ✅ yes | `$if %uselicd%` block (unclosed, excludes solve) | `solve m maximizing Util using nlp` (in loop) |
| Largest polygon | `polygon.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve polygon using nlp maximizing polygon_area` |
| Robot arm | `robot.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve robot minimizing tf using nlp` (typo in source: `miniziming`) |
| Goddard rocket | `rocket.gms` | ✅ yes | `$if set workSpace` (inline guard, line before solve) | `solve rocket using nlp maximizing final_velocity` |
| Scenario Tree | `srpchase.gms` | ✅ yes | `$if not set DIM` + `$ifE` (unclosed, excludes solve) | `solve purchase minimizing cost using lp` |

**Notes:**
- **13 models** (all except lmp2) are confirmed `$if`-bug cases where `process_conditionals` eats the solve statement
- **lmp2** is a separate issue: solve is inside a doubly-nested loop; Issue #749 only extracts from one nesting level
- `elec.gms` has `$if not set np $set np 25` at line 32 — this unclosed inline `$if` excludes everything from line 32 through EOF, including the Model declaration and solve statement
- `robot.gms` source has typo `miniziming`; documented above with correction in parentheses

---

## Part 4: Sprint 20 Recommendations

### Confirmed S20-addressable items (2 internal_error → 0 after stale-JSON correction)

The true `internal_error` count is **2**, both deferred:
- **maxmin**: smin aggregation AD rule (~4–6h, architectural)
- **mlbeta**: loggamma/digamma unavailable in GAMS (~0h, permanently infeasible)

**Revised PROJECT_PLAN.md estimate:** "Translation Internal Error Fixes (~5 models)" needs
correction — only 2 true internal errors remain, both deferred. No Sprint 20 internal_error
fixes needed.

### High-value Sprint 20 opportunity: model_no_objective_def fix

The `$if set workSpace` preprocessor bug affects **13 models**. Fixing `process_conditionals`
to correctly handle single-line inline `$if` directives would potentially unblock all 13
at once. Estimated effort: **~2–3h** (preprocessor fix + tests).

Additional models (lmp2, robot typo) require separate fixes (~1h each).

**Potential new parse successes:** +13 models (from 107 → ~120 parseable)

**Caveats:** These are COPS benchmark models (continuous optimal control problems) — they
may have additional blockers after parsing (complex expressions, lead/lag indexing for
discretized ODEs). But fixing parse is the prerequisite.

---

## Part 5: Impact on PROJECT_PLAN.md Estimates

| Workstream | PROJECT_PLAN.md Estimate | Revised (Post-Audit) |
|-----------|--------------------------|----------------------|
| translate internal_error fixes | 5 models, 6–8h | 0 models addressable; both deferred |
| model_no_objective_def | 5 models, 4h | 14 models; `$if` bug fix ~2–3h |
| codegen_numerical_error | not in plan | 4 models; Inf parameter handling ~2–4h |
| timeout | not in plan | 1 model (iswnm); deferred |

**Key revision:** The ~6–8h "translate internal error" budget should be redirected to the
`model_no_objective_def` preprocessor fix, which has much higher ROI (13 models vs. 0).

---

## Fix Location Summary

| Issue | File | Lines | Fix |
|-------|------|-------|-----|
| `$if` inline directive eating solve | `src/ir/preprocessor.py` | `process_conditionals()` | Detect same-line inline `$if` guard; don't carry exclusion to next line |
| smin aggregation AD | `src/ad/derivative_rules.py` | `_diff_smin()` ~1177 | Deferred: distinguish scalar vs. aggregation form |
| loggamma/gamma derivative | `src/ad/derivative_rules.py` | `_diff_call()` ~595 | Permanently infeasible (no digamma in GAMS) |
| Doubly-nested loop solve | `src/ir/parser.py` | `_handle_loop_stmt` ~3403 | Recursive loop body solve extraction |
| `robot.gms` typo | `src/gams/gams_grammar.lark` | `MINIMIZING_K` | Already handles `min\w*` — robot should parse after `$if` fix |
