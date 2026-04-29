# Plan to Fix #1322 — gtm NA-propagation through `supb`/`supa` parameters blocks PATH feasibility

**GitHub Issue:** [#1322](https://github.com/jeffreyhorn/nlp2mcp/issues/1322)
**Issue Doc:** `docs/issues/ISSUE_1322_gtm-na-propagation-supb-supa-blocks-feasibility.md`
**Predecessors:** PR #1321 (closes #1192 stat_s + #1320 bdef listing-time aborts)
**Affected models (1322 directly):** gtm
**Adjacent models that may benefit:** any model whose pre-solve parameter assignments contain divisions by data-derived parameters that may be zero (most CGE-class models that use empty-cell tables for "no data" semantics).
**Goal:** Promote gtm from `model_infeasible` to `model_optimal` (full match against the NLP reference, `-543.5651`), completing the #1192 / #1320 / #1322 fix family for gtm.

---

## 1. Reproduction (verified 2026-04-29 on `sprint25-plan-fix-1192` branch with PR #1321 in place)

### 1.1 Confirm the residual `model_infeasible`

```bash
.venv/bin/python -m src.cli data/gamslib/raw/gtm.gms \
    -o /tmp/gtm_mcp.gms --skip-convexity-check
cd /tmp && gams gtm_mcp.gms lo=2

# Expected output:
# **** EXECERROR AT LINE 59 CLEARED (EXECERROR=0)
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      4 Infeasible
```

### 1.2 Confirm the original NLP solves (matches as expected)

```bash
cp /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/gtm.gms /tmp/gtm_orig.gms
cd /tmp && gams gtm_orig.gms lo=2

# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      2 Locally Optimal
# **** OBJECTIVE VALUE             -543.5651
```

### 1.3 Inspect the gigantic NA-derived coefficients in the post-PR-#1321 listing

```bash
grep -B1 -A2 "5E30\|2.4E31\|4.5E28" /tmp/gtm_mcp.lst | head -10
# Look for coefficients like `5E30 * s(mexico)`, `2.4E31 * s(alberta-bc)`,
# `4.5E28 * s(atlantic)` in the bdef row.
```

### 1.4 Inspect the parameter expressions in the IR

```bash
.venv/bin/python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
m = parse_model_file('data/gamslib/raw/gtm.gms')
normalize_model(m)
for pn in ('supc', 'supb', 'supa'):
    p = m.params.get(pn)
    print(f'{pn}: domain={p.domain}')
    for i, (ix, expr) in enumerate(p.expressions):
        print(f'  expr[{i}]: indices={ix} expr={repr(expr)[:140]}')
"
# supc has 2 expressions: simple sdat lookup + LhsConditionalAssign(supc=inf → 100)
# supb has 1 DollarConditional with Binary("/") inside
# supa has 2: arithmetic with Binary("/") + round() call
```

`supb` and `supa` both contain `Binary("/")` divisions in their assignments. When `supc(i) = 0`, those divisions produce NA, which propagates through the assignment chain.

---

## 2. Root cause (full details in issue doc)

The original NLP source has:

```gams
supc(i)  = sdat(i,"limit");                                   # mexico/alberta-bc/atlantic → 0
supb(i)  = ((sdat(i,"ref-p1") - sdat(i,"ref-p2"))
         / (1/(supc(i) - sdat(i,"ref-q1"))-1/(supc(i) - sdat(i,"ref-q2"))))
         $ (supc(i) <> inf);                                  # NA when supc=0
supa(i)  = sdat(i,"ref-p1") - supb(i)/(supc(i) - sdat(i,"ref-q1"));   # NA propagates
```

For mexico (supc=0):
- The `(sdat("ref-p1") - sdat("ref-p2"))` numerator is `(NA - NA) = NA` (empty cells in source data).
- The denominator's `1/(0 - q2) - 1/(0 - NA)` propagates NA.
- `NA / NA = NA`. So `supb(mexico) = NA`.
- `supa(mexico) = ref-p1 - NA/(0 - q1) = NA - NA = NA`.

The MCP emits these parameter assignments verbatim. PATH then evaluates the symbolic Jacobian which substitutes the NA-valued parameters into stationarity coefficients, producing extreme values like `5E30 * s(mexico)`. PATH cannot find a feasible point because the model is numerically degenerate.

---

## 3. Fix Approaches Considered

### Approach 1 — Generic NA-cleanup pass at MCP emit (RECOMMENDED)

After the original parameter assignments are emitted, append a sanity-cleanup
loop that overrides any indexed parameter that ends up `NA`/`UNDF`/`±inf`
to `0`:

```gams
* Issue #1322: NA-cleanup for parameters that may go NA during pre-solve assignment
loop(i, supc(i)$(NOT (supc(i) > -inf and supc(i) < inf)) = 0; );
loop(i, supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0; );
loop(i, supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0; );
```

(Using the `(NOT (x > -inf and x < inf))` idiom because GAMS does not have a
direct `isnan(x)` test — this expression evaluates True precisely when `x`
is `NA`, `UNDF`, `+inf`, or `-inf`, which is the safe set to override.)

For gtm, `supb*0 = 0` and `supa*0 = 0` for the zero-supc indices, eliminating
the gigantic Jacobian coefficients.

**Pros:**
- Simple, ~3 emitted lines per offending parameter.
- Safe: no-op when the parameter has valid values; only fires on NA.
- Generalizes to other CGE-class models with similar pre-solve patterns.

**Cons:**
- Requires detecting WHICH indexed parameters could go NA (we don't want to
  emit a cleanup for every parameter — that's clutter).
- Forces NA → 0 globally; if any equation interprets NA as a sentinel
  (rare in this codebase), behavior changes.

### Approach 2 — Targeted parameter-dependency analysis (REJECTED)

Detect that `supb` is computed from `supc` via division, and emit a
targeted reassignment:

```gams
supb(i)$(supc(i) = 0) = 0;
supa(i)$(supc(i) = 0) = 0;
```

**Pros:** more precise (only fires when the upstream cause is detected).

**Cons:** requires symbolic analysis of parameter expressions to find the
"upstream zero parameter". Fragile to non-trivial assignment chains
(e.g., `supa = supb/something_else_too`). More code; less generic.

### Approach 3 — Override `supc(i)$(supc(i) = 0) = epsilon` BEFORE the assignment chain (REJECTED)

Insert `supc(i)$(supc(i) = 0) = 1e-30` BEFORE `supb` is computed, so the
division in `supb`'s assignment uses a tiny non-zero divisor and produces
finite (huge) values instead of NA.

**Pros:** mathematically more "correct" — never lets supc be exactly zero.

**Cons:**
- Requires inserting a line INTO the middle of the original parameter-init
  chain, which the emitter doesn't currently do.
- Still produces gigantic finite coefficients (~1e60 instead of NA), still
  numerically degenerate. Empirically tested during PR #1321 dev — PATH
  still returns INFEASIBLE.

### Approach 4 — `$onUndf` directive + GAMS option NaN handling (REJECTED)

Wrap the equation listing with `$onUndf ... $offUndf` and rely on GAMS
to allow UNDF arithmetic.

**Pros:** 1-line emitter change.

**Cons:** does NOT suppress div-by-zero errors at parameter-assignment
time (only allows arithmetic results to be UNDF without aborting). Tested
during PR #1321 dev — still aborts.

---

## 4. Recommended Implementation: Approach 1

### 4.1 Overview

Add a new emitter pass `emit_post_assignment_na_cleanup(model_ir)` that:

1. Identifies indexed parameters whose `expressions` contain at least one
   `Binary("/")` (division) at any depth — these are the parameters that
   could go NA from arithmetic with bad inputs.
2. For each such parameter, emits a sanity-cleanup line:
   ```
   <param>(<dom>)$(NOT (<param>(<dom>) > -inf and <param>(<dom>) < inf)) = 0;
   ```
3. Inserts the cleanup section after the original parameter-assignment
   section but before the variable initialization / equations / solve.

For gtm, this produces:

```gams
* Sanity cleanup: parameters with division-based assignments that may go NA
supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0;
supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0;
```

(`supc` is excluded because its assignments don't contain division — its
`NA` would come only from sdat data, not arithmetic. We don't want to
override data-driven NAs because they may be intentional sentinels.)

### 4.2 Code sites

| File | Function | Change |
|------|----------|--------|
| `src/emit/original_symbols.py` | new `_param_assignment_has_division(param_def)` | Walk `ParameterDef.expressions[*][1]` (the Expr) and return True if any `Binary("/")` appears anywhere in the tree. |
| `src/emit/original_symbols.py` | new `emit_post_assignment_na_cleanup(model_ir, model_relevant_params)` | Iterate `model_ir.params`; for each indexed param with division-based assignments AND that's referenced by the model (via `model_relevant_params` filter, mirroring `emit_original_parameters`'s filtering), emit the cleanup line. |
| `src/emit/emit_gams.py` | `emit_gams_mcp` orchestration | Call the new function after `emit_original_parameters` and `emit_pre_solve_param_assignments`, before variable bounds. Place the output in a new section labeled `* NA-cleanup for division-based parameter assignments`. |

### 4.3 Detection criterion: "could go NA from arithmetic"

A `ParameterDef` is in scope iff:

1. `param_def.domain` is non-empty (indexed — scalar params would fail
   uniformly; their NA-ness is a static fact and the user can pre-guard
   them differently), AND
2. At least one entry in `param_def.expressions` has an Expr tree
   containing a `Binary` node with `op == "/"` at any depth.

Walking the Expr tree generically via `dataclasses.fields` works the
same way as PR #1320's `_collect_divisor_param_refs` — reuse the
walker pattern.

### 4.4 Filter: only emit cleanup for model-relevant parameters

Mirror `emit_original_parameters`'s `model_relevant_params` filter so we
don't emit cleanup lines for parameters used only in display blocks
(`display sdat;` etc.) but never referenced by any equation. This keeps
the cleanup section short.

### 4.5 Idempotency

The cleanup line is naturally idempotent. Running it twice produces the
same result. Order-of-emission also doesn't matter (it's a strict no-op
when the parameter has finite values).

---

## 5. Test Plan

### 5.1 New unit tests — `tests/unit/emit/test_na_cleanup_emission.py`

5 cases:

1. **Indexed param with division-based assignment**: a synthetic model with
   `parameter p(i); p(i) = 1/q(i);` should produce a cleanup line for `p`.

2. **Indexed param with non-division assignment**: `parameter p(i); p(i) = q(i) + r(i);` should NOT produce a cleanup line.

3. **Scalar param**: scalars are out of scope — no cleanup line emitted.

4. **Indexed param with division but never referenced**: if `p(i)` only
   appears in a `display p;` block and not in any equation, cleanup is
   suppressed (mirrors `model_relevant_params` filter).

5. **Multiple indexed params with division**: cleanup lines emitted for
   each, in deterministic (sorted) order.

### 5.2 Integration test — `tests/integration/emit/test_gtm_na_cleanup.py`

```python
@pytest.mark.integration
def test_gtm_emits_supb_supa_na_cleanup():
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip(...)
    output = _emit_mcp_for(src)
    assert "supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0;" in output
    assert "supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0;" in output
    # supc is data-driven, not arithmetic-driven — should NOT have a cleanup line
    assert "supc(i)$(NOT (supc(i) > -inf and supc(i) < inf))" not in output
```

### 5.3 Pipeline retest (acceptance criterion)

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model gtm --quiet
```

Acceptance:
- gtm reaches PATH (no MODEL STATUS 4 from NA Jacobian).
- Stretch goal: `Match: 1 (100.0%)` against the NLP reference (`-543.5651`).

If gtm now solves but doesn't match the NLP objective: document and
classify as "different KKT point" per Sprint 24 Day 11 framing
(non-convex CGE may have multiple local optima).

### 5.4 Regression sweep

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --solve-success --quiet
```

Acceptance: 0 NEW translate failures, 0 NEW solve regressions, no NEW
mismatches on currently-matching models. Particular attention to:

- **CGE family** (irscge, lrgcge, moncge, stdcge, twocge, splcge,
  quocge): they all have CES-style production functions with parameter
  divisions. The cleanup might fire on parameters that are intentionally
  zero. Verify no objective-value drift.
- **partssupply**, **prolog**, **quocge**: have `prod()` and CES
  utility — same parameter-division concern.
- **catmix, ramsey, hhfair**: use `1/x` derivatives.

### 5.5 Adjacent-model probe

After gtm passes, also run lmp2 (#1323), camcge (#1324), and elec (#1325)
to see whether Approach 1 has any spillover benefit. Expected: none —
those models have different root causes (set-extraction, KKT-side
div-by-zero, distance-zero), but document any progress.

---

## 6. Time Estimate

| Phase | Work | Hours |
|-------|------|-------|
| 1. Setup | branch, reproduce, verify NA-coefficient details in lst | 0.25 |
| 2. Helper function | `_param_assignment_has_division(param_def)` (recursive Expr walker) | 1.0 |
| 3. Emitter wiring | `emit_post_assignment_na_cleanup` + integration into `emit_gams_mcp` orchestration | 1.5 |
| 4. Unit tests | 5 cases in `tests/unit/emit/test_na_cleanup_emission.py` | 1.5 |
| 5. Integration test | gtm-specific test in `tests/integration/emit/test_gtm_na_cleanup.py` | 0.5 |
| 6. gtm validation | re-emit, GAMS compile + PATH solve + NLP comparison | 0.75 |
| 7. Regression sweep | full-corpus solve-success, diagnose any drift | 1.5 |
| 8. Quality checks | `make typecheck && make format && make lint && make test` | 0.5 |
| 9. PR + review | open PR, address Copilot review (~1 round) | 1.0 |
| **Total** | **~8.5 hours (best case 6h, worst case 11h)** | |

**Sprint placement:** fits Sprint 26 Day 1–2 since Sprint 25's Day-N
budget is exhausted. Effort-vs-reward: 1 model unblock (gtm → likely
match given NLP solves cleanly), with some chance of incidental
improvement on CGE-family models.

---

## 7. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Cleanup over-fires** on parameters that are LEGITIMATELY zero/NA in some indices and the model's equations interpret that as sentinel. Could change objective value on currently-matching models. | Medium | Regression-sweep particular attention to CGE family + nonlinear-utility models. If a canary regresses, narrow the criterion: only emit cleanup when the parameter's assignment Expr has a `Binary("/")` whose denominator contains another parameter (not a constant) — the typical NA-from-data pattern. |
| **`(NOT (x > -inf and x < inf))` doesn't catch all NA cases** in some GAMS versions. | Low | Verify on the project's GAMS version (53.1.0 per the lst output). Alternative idiom: `(x = NA or x = +inf or x = -inf or x = UNDF)`. |
| **Emit ordering matters** — the cleanup must come AFTER the original assignments but BEFORE variable initialization that uses the parameters. | Low | Place the new section right after `emit_pre_solve_param_assignments`'s output and before the variable-bounds section. The orchestration in `emit_gams_mcp` already has clear section boundaries. |
| **gtm solve still fails** due to a deeper PATH-level convergence issue (the model is non-convex, after all). | Medium | If post-fix gtm reaches PATH but doesn't match the NLP, that's still progress (`path_solve_terminated` → `model_optimal` or "different KKT point"). The NLP is `Locally Optimal`, so PATH may find a different local optimum. Document and accept. |
| **Cleanup spam**: emitting cleanup for many parameters bloats the MCP file size for CGE models with dozens of parameters. | Low | The `model_relevant_params` filter already restricts to parameters used in equations. Verify the emitted CGE MCPs grow by < 100 lines. |
| **Performance**: the recursive Expr walker for division detection adds emit-time cost. | Very low | Single-pass per parameter; trivial cost vs. the rest of emission. |

---

## 8. Out-of-scope (deferred to follow-up issues)

- **Generalized NaN-detection in any GAMS scope** (not just parameter
  assignments): a future emitter pass could detect NA-prone expressions
  in EQUATION bodies too. PR #1321's #1320 fix is the equation-side
  analog (divisor-guard injection); this PR is the parameter-side
  analog. Any combined "data-flow-aware NA tracking" is out of scope.
- **Detecting upstream root cause** (e.g., that `supb=NA` was caused by
  `supc=0` propagating, not by direct NA input): out of scope.
  Approach 1's "patch any NA" is sufficient for the Sprint goal.
- **Re-emit stale checked-in MCP artifacts**: out of scope; queue for
  the post-Sprint-26 housekeeping PR.
- **Variable-side NA cleanup**: variables don't go NA from arithmetic
  in the same way; this fix is parameter-only.

---

## 9. PR Title and Branch

- **Branch:** `sprint26-fix-1322-gtm-na-cleanup`
- **PR title:** `Sprint 26: Fix #1322 — gtm NA-propagation cleanup for division-based parameter assignments`
- **PR body:** standard structure (Summary / Root cause / Fix / Test plan / Refs).
- **Closes:** #1322. Mentions but does not close #1323 / #1324 / #1325 unless the regression sweep demonstrates incidental unblocks.

---

## 10. Acceptance Criterion (Definition of Done)

1. ✅ gtm no longer returns `MODEL STATUS 4 Infeasible` from NA-derived
   coefficients.
2. ✅ gtm reaches a PATH outcome that is one of: `model_optimal` (full
   match, the stretch goal), `model_optimal_presolve` (warm-start), or
   "different KKT point" (documented).
3. ✅ All 3,374+ unit tests still pass.
4. ✅ Tier-1 canaries (sparta, gussrisk, prolog, partssupply, ship,
   paklive, quocge, splcge) still match. CGE family (irscge, lrgcge,
   moncge, stdcge) doesn't drift in objective value (still pre-existing
   alias-AD mismatches).
5. ✅ Full corpus regression sweep on solve-success canary: 0 NEW
   translate or solve regressions.
6. ✅ `make typecheck && make format && make lint && make test` clean.
7. ✅ PR opened, Copilot review addressed.

If criterion 1 holds but criterion 2 fails (gtm reaches PATH but doesn't
match), the fix is still valuable — it eliminates the NA-Jacobian
pathology — and the residual is a non-convex local-optimum issue
unrelated to #1322. Document and proceed.
