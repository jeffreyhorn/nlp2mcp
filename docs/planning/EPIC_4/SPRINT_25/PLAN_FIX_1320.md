# Plan to Fix #1320 — gtm bdef log-zero residual after #1192 stat_s fix

**GitHub Issue:** [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320)
**Issue Doc:** `docs/issues/ISSUE_1320_gtm-bdef-log-zero-residual-after-1192.md`
**Parent:** #1192 (stat_s portion fixed by PR #1321; this plan covers the residual)
**Affected models (1320 directly):** gtm
**Adjacent models that may benefit:** lmp2 (#1243), camcge (#1245), elec (#983), and any future model with `1/X` or `log(X)` patterns where `X` involves a parameter that may be zero in some indices.
**Goal:** Promote gtm from `path_solve_terminated` to `model_optimal`/`match`, completing the #1192 fix.

---

## 1. Reproduction (verified 2026-04-28 on `main` post-PR #1321)

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/` and PR #1321 merged.

### 1.1 Confirm the residual EXECERROR=2

```bash
.venv/bin/python -m src.cli data/gamslib/raw/gtm.gms \
    -o /tmp/gtm_mcp.gms --skip-convexity-check
cd /tmp && gams gtm_mcp.gms lo=2

# Expected output:
# **** EXECERROR AT LINE 59 CLEARED (EXECERROR=0)
# **** Exec Error at line 172: division by zero (0)
# **** Exec Error at line 172: A constant in a nonlinear expression in equation bdef evaluated to UNDF
# **** SOLVE from line 222 ABORTED, EXECERROR = 2
```

### 1.2 Confirm the original NLP works

```bash
cp data/gamslib/raw/gtm.gms /tmp/gtm_orig.gms
cd /tmp && gams gtm_orig.gms lo=2

# Expected:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      2 Locally Optimal
# **** OBJECTIVE VALUE             -543.5651
```

### 1.3 Identify the offending equation in the emitted MCP

```
$ grep -n "^bdef" /tmp/gtm_mcp.gms
172:bdef.. benefit =E= sum(j, dema(j) * d(j) ** demb(j))
                    - sum(i, supa(i) * s(i) - supb(i) * log((supc(i) - s(i)) / supc(i)))
                    - sum((i,j)$(ij(i,j)), utc(i,j) * x(i,j));
```

Line 172 evaluates `log((supc(i) - s(i))/supc(i))` per `i`. For `mexico`,
`alberta-bc`, `atlantic` (where `sdat(i,"limit")` is empty so `supc(i) = 0`),
the inner division `(0 - 0)/0` triggers GAMS' div-by-zero error class at
model-listing time.

### 1.4 Failed attempts (per the issue doc)

- `option domlim = 100`: only controls solver-level domain violations, not
  listing-time evaluation errors.
- `$onUndf`: allows expressions evaluating to UNDF/NA, but does NOT suppress
  the div-by-zero error class. Verified — same EXECERROR=2.
- Override `supc(i)$(supc(i) = 0) = 1e-30;`: avoids the listing-time abort
  but produces gigantic NA-derived coefficients (e.g., `5E30 * s(mexico)`)
  that PATH rejects as INFEASIBLE (MODEL STATUS 4). NA propagation through
  `supb`/`supa` is the root cause of those coefficients; numerical smoothing
  alone cannot save the model.

---

## 2. Root cause (already in issue doc — short refresher)

For three regions, source data has empty `sdat(i, "limit")` cells. After
`supc(i) = sdat(i, "limit")` plus the `supc$(supc=inf)=100` rewrite (which
matches `inf` only, not `0`), `supc(mexico) = supc(alberta-bc) =
supc(atlantic) = 0`. Consequently `supb(i)` and `supa(i)` evaluate to `NA`
because their pre-solve assignments have `supb / (supc - q1)` and
`supa = ... - supb/(supc - q1)` factors.

**Why the NLP works but the MCP doesn't:** GAMS NLP-mode listing skips
equation evaluation for fixed variables. With `s.up(i) = 0.99 * supc(i) =
0` and `s.lo(i) = 0` (positive default), `s(i)` is implicitly fixed at 0
for those regions, and the bdef body is skipped per-row by NLP listing.

The MCP emits `bdef` verbatim. The body `sum(i, ...)` is at scalar scope
— there is no per-`i` MCP pair to skip — so the entire sum is evaluated at
listing time, including the zero-supc rows.

PR #1321's bounds-aware guard fixes `stat_s(i)` (a KKT-built equation) but
does not touch `bdef` (the parsed-source equation).

---

## 3. Fix Approaches Considered (per issue doc, refined)

### Approach 1 — Equation-body $-condition rewrite (RECOMMENDED)

At MCP emit time, rewrite the bdef body so the offending sum has a
`$(supc(i) <> 0)` condition:

```
bdef..  benefit =e= sum(j, dema(j)*d(j)**demb(j))
                 -  sum(i$(supc(i) <> 0),
                        supa(i)*s(i) - supb(i)*log((supc(i) - s(i))/supc(i)))
                 -  sum((i,j)$ij(i,j), utc(i,j)*x(i,j));
```

**Pros**: structurally correct (zero-supc regions contribute nothing
because they can't supply); fixes the listing-time abort cleanly; pattern
generalizes to lmp2, camcge, elec.

**Cons**: requires AST traversal + rewrite of original equations at emit
time; detection logic must identify "parameter is a denominator" and
"parameter could be zero".

### Approach 2 — Symbolic NA-cleanup (rejected; tested)

Override `supc=0` and `supb=NA`/`supa=NA` to safe values. Tested during
PR #1321 dev: produces INFEASIBLE due to coefficient blow-up. Not viable
on its own.

### Approach 3 — bdef replacement with post-solve assignment (rejected)

Replace `bdef` constraint with a post-solve `benefit.l = ...` assignment.
Large blast radius — changes MCP/NLP equation parity for all output-only
variables. Risky.

---

## 4. Recommended Implementation: Approach 1

### 4.1 Overview

Add an emitter pre-pass that scans original (non-KKT-built) equations'
bodies for **divisor parameters** and rewrites the smallest-enclosing
`Sum` to add a `$(param <> 0)` (per-divisor) condition.

A "divisor parameter" is a `ParamRef` that appears in:
- `Binary("/", numerator, denominator)` as the `denominator`, OR transitively
  inside it via `Binary` arithmetic (e.g., `1/sqr(supc)` → `sqr(supc)` →
  divisor is `supc`).
- `Call("log", arg)` as `arg` or transitively inside, since `log(0) = -inf`
  is a domain error.
- `Call("sqrt", arg)` as `arg` (negative-domain error if arg becomes 0 in
  the wrong sign context). Lower priority — gtm doesn't have this; defer
  to the next pass.

### 4.2 Code sites

| File | Function | Change |
|------|----------|--------|
| `src/emit/equations.py` | new `_collect_divisor_param_refs(expr)` | Walk an Expr tree and return a set of `ParamRef` nodes that appear in a divisor or `log()` argument position. Recursive on `Binary`, `Call`, `Sum`, `Prod`, `DollarConditional`. |
| `src/emit/equations.py` | new `_inject_divisor_guards(expr)` | Walk the tree, find `Sum`/`Prod` nodes whose body contains divisor `ParamRef` nodes from indexed parameters, and AND their existing condition with `(param(d) <> 0)` per offending parameter. |
| `src/emit/equations.py` | `emit_equation_def` | Call `_inject_divisor_guards` on `lhs_rhs` BEFORE `expr_to_gams`. Apply only to original (parsed) equalities, NOT KKT-built stationarity (those have their own machinery from #1192). |
| `src/kkt/kkt_system.py` | (no change needed) | Skip stationarity equations by checking the equation name prefix `stat_` or by routing through a new `is_kkt_built` flag on `EquationDef`. |

The simplest dispatch: `emit_equation_def` already gets called for both
parsed and KKT-built equations, but the parsed equations are stored in
`kkt.model_ir.equations` while the KKT-built ones are in `kkt.stationarity`
+ `kkt.complementarity_*`. The emitter loop in `emit_equation_definitions`
can be modified to call `_inject_divisor_guards` for parsed equations only,
or all equations safely (KKT-built ones from PR #1321 already have body
guards; this new pass would be an idempotent no-op for them).

### 4.3 Detection criterion: "divisor parameter that may be zero"

Conservative version (RECOMMENDED for the first pass):

> Inject a `$(param(d) <> 0)` guard for **every** indexed `ParamRef` that
> appears in a divisor or `log()` argument position **inside a Sum body**,
> when the parameter's domain matches at least one of the Sum's index
> variables.

This is conservative — it adds the guard even when the parameter is never
zero at runtime. Cost: extra runtime check, but in practice GAMS folds it
to a constant. Benefit: no false negatives, no symbolic value-tracking
required.

If empirically over-firing (regression on canaries), tighten the criterion
to "parameter has at least one assignment where the RHS could produce 0"
(e.g., assigned from `Table` or `Parameter / list / ` with potentially
empty cells). This is a heuristic but less invasive than full symbolic
value-tracking.

### 4.4 Worked example for gtm

Input bdef body (per IR dump):

```
Binary(-,
    Binary(-,
        Sum((j), Binary(*, ParamRef(dema(j)), Binary(**, VarRef(d(j)), ParamRef(demb(j))))),
        Sum((i),
            Binary(-,
                Binary(*, ParamRef(supa(i)), VarRef(s(i))),
                Binary(*, ParamRef(supb(i)),
                    Call(log,
                        (Binary(/, Binary(-, ParamRef(supc(i)), VarRef(s(i))), ParamRef(supc(i))))))))),
    Sum((i,j)$SetMembershipTest(ij, ...), Binary(*, ParamRef(utc(i,j)), VarRef(x(i,j)))))
```

`_collect_divisor_param_refs` finds:
- `supc(i)` as the denominator of the inner `Binary(/, ..., supc(i))`
- `supc(i)` as the argument of `Call("log", ...)` (whose body is
  `(supc - s)/supc`, so transitively `supc` is in a divisor position)

`_inject_divisor_guards` finds the smallest enclosing `Sum` whose body
contains these divisor `ParamRef`s — that's the `Sum((i), ...)` at the
second outermost minus. It rewrites it to:

```
Sum((i)$(Binary("<>", ParamRef(supc(i)), Const(0))),
    Binary(-,
        Binary(*, ParamRef(supa(i)), VarRef(s(i))),
        Binary(*, ParamRef(supb(i)), Call(log, ...))))
```

The other `Sum((j), ...)` and `Sum((i,j)$ij, ...)` are untouched because
their bodies don't contain divisor `ParamRef`s.

Emitted GAMS:

```
bdef..  benefit =e= sum(j, dema(j)*d(j)**demb(j))
                 -  sum(i$(supc(i) <> 0),
                        supa(i)*s(i) - supb(i)*log((supc(i) - s(i))/supc(i)))
                 -  sum((i,j)$ij(i,j), utc(i,j)*x(i,j));
```

For mexico/alberta-bc/atlantic, `supc(i) = 0` makes the condition False,
so the inner term is excluded from the sum. The remaining sum is over
the 7 non-zero-supc regions, with well-defined values.

### 4.5 Interaction with PR #1321's stationarity guard

`stat_s(i)` is wrapped in `$(s.up(i) - s.lo(i) > 1e-10)` per PR #1321.
For zero-supc regions, that guard collapses to False, so `stat_s` is
skipped (and `s.fx(i) = 0` is emitted).

`bdef` after this PR has `sum(i$(supc(i) <> 0), ...)` so zero-supc rows
are excluded.

Both fixes together: zero-supc regions are completely degenerate from
the MCP's perspective. `s(i) = 0` for those `i`; the `bdef` summand
contribution is 0; no listing-time evaluation hits div-by-zero.

---

## 5. Test Plan

### 5.1 New unit tests — `tests/unit/emit/test_divisor_guard_injection.py`

5 cases:

1. **Indexed parameter as direct divisor inside a Sum**: input
   `Sum((i), 1/p(i))` → output `Sum((i)$(p(i) <> 0), 1/p(i))`. Assert the
   condition is correctly added.

2. **Parameter inside `log(.../param)`**: input
   `Sum((i), log(x(i)/p(i)))` → output `Sum((i)$(p(i) <> 0), log(x(i)/p(i)))`.

3. **Parameter NOT in divisor position**: input
   `Sum((i), p(i) * x(i))` → unchanged (no rewrite). Assert the body is
   identical.

4. **Multiple offending parameters in one Sum**: input
   `Sum((i), 1/(a(i) * b(i)))` → output
   `Sum((i)$(a(i) <> 0 and b(i) <> 0), 1/(a(i) * b(i)))`.

5. **Existing $-condition preserved**: input
   `Sum((i)$cond, 1/p(i))` → output
   `Sum((i)$(cond and p(i) <> 0), 1/p(i))`.

### 5.2 Integration test — `tests/integration/emit/test_gtm_bdef_guard.py`

Assert that the emitted gtm `bdef` line contains `sum(i$(supc(i) <> 0), ...)`
(or the equivalent `Binary("<>", supc, Const(0))` form) on the supply-cost
sum.

```
@pytest.mark.integration
def test_gtm_bdef_has_supc_nonzero_guard():
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip(...)
    output = _emit_mcp_for(src)
    bdef_lines = [l for l in output.splitlines() if l.startswith("bdef..")]
    assert bdef_lines
    bdef = bdef_lines[0]
    assert "sum(i$(supc(i) <> 0)" in bdef or "sum(i$(supc(i)<>0)" in bdef
```

### 5.3 Pipeline retest (the acceptance criterion)

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model gtm --quiet
```

Acceptance: gtm reaches PATH (no EXECERROR=2). Stretch goal: `Match: 1
(100.0%)` against the NLP reference (`-543.5651`).

If the model now solves but doesn't match, that may indicate the fix is
correct but PATH finds a different KKT point. Document and accept as a
"different KKT point" per Sprint 24 Day 11 classification.

### 5.4 Regression sweep

Same as PR #1321:

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --solve-success --quiet
```

Acceptance: 0 NEW translate failures, 0 NEW solve regressions, no NEW
mismatches on currently-matching models. Particular attention to models
that have nonlinear sums:
- CGE family (irscge, lrgcge, moncge, stdcge, twocge, splcge, quocge,
  cge_*) — many use `prod(i, x(i)**alpha(i))` and similar. The fix should
  be a no-op for these because `x` is a variable (not a parameter) in the
  divisor.
- prolog, partssupply (CES utility / production) — same.

### 5.5 Adjacent-model probe (optional)

After gtm passes, run `lmp2`, `camcge`, `elec` to see if Approach 1 also
unblocks them. Document any progress / new residuals.

---

## 6. Time Estimate

| Phase | Work | Hours |
|-------|------|-------|
| 1. Setup | branch, reproduce, verify EXECERROR=2 baseline | 0.25 |
| 2. Helper functions | `_collect_divisor_param_refs` and `_inject_divisor_guards` (recursive AST walk + smallest-enclosing-Sum logic) | 2.0 |
| 3. Emitter wiring | call `_inject_divisor_guards` from `emit_equation_def` (or in `emit_equation_definitions` loop); skip KKT-built equations | 1.0 |
| 4. Unit tests | 5 cases in `tests/unit/emit/test_divisor_guard_injection.py` | 1.5 |
| 5. Integration test | gtm bdef test in `tests/integration/emit/test_gtm_bdef_guard.py` | 0.5 |
| 6. gtm validation | re-emit, GAMS compile, PATH solve, NLP-vs-MCP comparison | 0.75 |
| 7. Regression sweep | full-corpus solve-success retest, diagnose regressions | 1.5 |
| 8. Adjacent-model probe | quick test of lmp2/camcge/elec | 0.5 |
| 9. Quality checks | `make typecheck && make format && make lint && make test` | 0.5 |
| 10. PR + review | open PR, address Copilot review (~1 round expected) | 1.0 |
| **Total** | **~9.5 hours (best case 7h, worst case 12h)** | |

**Effort-vs-reward:** medium-high effort for 1–4 model unblocks. gtm is
the primary target; lmp2/camcge/elec are bonus if Approach 1 generalizes
cleanly.

**Sprint placement:** fits Sprint 25 stretch (Days 12–13) IF Pattern A
isn't picked up. Otherwise queues to Sprint 26.

---

## 7. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Conservative criterion adds spurious guards** that change canary objective values (e.g., a parameter that's never zero gets a `$(p <> 0)` guard, which GAMS folds to True at compile time but technically alters AST structure — could affect comparison tolerances) | Medium | Tested on `prolog`, `partssupply`, CGE family in regression sweep; if any matches turn into mismatches, the criterion narrows to "parameter has at least one zero value via assignment-RHS analysis" or "parameter is assigned from a Table/list with possibly-empty cells". |
| **Smallest-enclosing-Sum logic misidentifies the right Sum** when divisor `ParamRef` is shared across multiple Sum scopes (e.g., shared between `sum(i, 1/p(i))` and `sum((i,j), q(j)/p(i))` in the same equation). | Low | The walker should attach the guard to EACH Sum that has the divisor inside its body — not just the smallest. Test case 4 in §5.1 covers multi-Sum scope. |
| **Approach 1 doesn't fix lmp2/camcge/elec** because their root causes differ from gtm's pure parameter-zero. | Medium | Explicitly listed as bonus, not acceptance criterion. The plan succeeds even if only gtm is unblocked. |
| **GAMS rejects `$(p(i) <> 0)` syntax** in some edge cases (e.g., when `p` is a non-domain-conforming reference). | Very low | The pattern is GAMS-standard and used throughout the codebase already (e.g., `comp_db(j).. sum(i$(ij(i,j)), x(i,j))` style). |
| **PR #1321's stationarity guard interacts badly** with the new bdef guard (e.g., double-conditioning the same row). | Low | The stationarity guard is on `stat_s` (KKT-built equation); the bdef guard is on `bdef` (parsed equation). Different equations; no interaction. |
| **`prod()` and `smin/smax` aggregations have similar issues** but the fix only covers `Sum`. | Low (gtm-relevant) | Note in the PR description; extend to `Prod` if needed in a follow-up. The detection logic should also apply to `Prod` bodies — same code path with one isinstance check. |
| **Some equations rely on `0/0 = NaN` propagation** for solver-time domain handling. Excluding those rows via $-condition would change the math. | Low (would need a deliberately constructed model) | Document the semantic shift in the PR description: "the rewritten equation excludes rows where the parameter denominator is zero, which is mathematically equivalent to the NLP behavior of fixed-variable equation skipping. If a model relies on `0/0` as a sentinel value, this fix must be opted out." |

---

## 8. Out-of-scope (deferred to follow-up issues)

- **`Prod`/`Smin`/`Smax` aggregation guards**: extend the same pattern. ~1h
  if it surfaces during the regression sweep.
- **Variable-denominator detection** (e.g., `1/x(i)` where x is a variable
  that may be zero at the initial point): different problem class — best
  handled via variable initialization (already done elsewhere) or via a
  PR #1321-style `var.l > eps` guard.
- **`sqrt(0)` and `0**negative` domain errors**: similar pattern, separate
  fix family. Currently no model in the corpus is known to hit these as a
  primary blocker.
- **Generalizing to KKT-built equations**: PR #1321 already handles
  stationarity via the bounds-aware guard. The new pass should explicitly
  skip them to avoid double-conditioning.
- **Re-emit stale checked-in MCP artifacts**: out of scope; queue for the
  post-Sprint-25 housekeeping PR.

---

## 9. PR Title and Branch

- **Branch:** `sprint25-fix-1320-gtm-bdef-divisor-guard`
- **PR title:** `Sprint 25: Fix #1320 — gtm bdef listing-time div-by-zero via parameter-divisor $-condition rewrite`
- **PR body:** standard structure (Summary / Root cause / Fix / Test plan / Refs).
- **Closes:** #1320. Mentions but does not close #1243 / #1245 / #983 unless the regression sweep demonstrates they're unblocked too — in that case, close them in the same PR.

---

## 10. Acceptance Criterion (Definition of Done)

1. ✅ `gtm` no longer aborts at GAMS model-listing time (no EXECERROR=2).
2. ✅ `gtm` reaches PATH; either `model_optimal` (full match preferred) or
   a documented "different KKT point" outcome.
3. ✅ All 3,374+ unit tests still pass.
4. ✅ Tier-1 canaries (sparta, gussrisk, prolog, partssupply, ship,
   paklive, quocge, splcge) still match.
5. ✅ No NEW translate failures, no NEW solve regressions on the
   solve-success canary set.
6. ✅ `make typecheck && make format && make lint && make test` clean.
7. ✅ PR opened, Copilot review addressed.

If criteria 1–2 fail (e.g., gtm still doesn't match), document the residual
and file a follow-up. The fix is still valuable as long as criterion 1
holds (gtm progresses past listing-time abort).
