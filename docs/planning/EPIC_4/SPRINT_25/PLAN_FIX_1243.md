# Plan to Fix #1243 — lmp2 Runtime Division by Zero in `stat_y` (`1/y(p)` at Initial Point)

**GitHub Issue:** [#1243](https://github.com/jeffreyhorn/nlp2mcp/issues/1243)
**Issue Doc:** `docs/issues/ISSUE_1243_lmp2-runtime-division-by-zero-stat-y.md`
**Predecessors / blockers:** [#1323](https://github.com/jeffreyhorn/nlp2mcp/issues/1323) (lmp2 Error 66 from `m` set never extracted) — blocks reproduction in current state; see §1 for workaround.
**Affected models (1243 directly):** lmp2
**Adjacent models that may benefit:** any NLP whose objective or equation contains `prod(i, var(i))` with `var` declared as free (or with a default `.l = 0`). Candidates from the corpus: catmix, ramsey, hhfair, prolog (all use `prod()` and/or CES with FREE vars).
**Goal:** Promote lmp2 from `path_syntax_error` (after #1323) to a PATH solve attempt without `EXECERROR=1` from division by zero. Stretch goal: `model_optimal` against the NLP reference.

---

## 1. Reproduction (verified 2026-04-27 on `sprint25-plan-fix-1243` branch)

### 1.1 Re-emit baseline (currently blocked by #1323)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_mcp.gms --quiet
cd /tmp && gams lmp2_mcp.gms lo=0
# Expected today (post-#1313, pre-#1323):
#   **** 66  equation stat_x.. symbol "m" has no values assigned
#   **** 256 Error(s) in analyzing solve statement.
# Compilation aborts BEFORE the runtime div-by-zero we want to study.
```

The issue we want to reproduce — runtime `EXECERROR=1` from `1/y(p)` in
`stat_y(p)` — is what *would* fire if the model compiled. Right now the
compile-time #1323 (`m(mm)` dynamic-subset assignment never extracted into
the IR) preempts it. Two viable workarounds for the duration of this fix:

#### Workaround A: temporary patch of the emitted file

Hand-edit `/tmp/lmp2_mcp.gms` to insert `m(mm) = yes;` after the set
declarations (mirroring the existing auto-emitted `n(nn) = yes;` line),
then rerun `gams lmp2_mcp.gms lo=0`. This bypasses #1323 just enough to
hit `stat_y` evaluation:

```
**** Exec Error at line 113: division by zero (0)
**** Evaluation error(s) in equation "stat_y(p1)"
**** Evaluation error(s) in equation "stat_y(p2)"
**** SOLVE from line 160 ABORTED, EXECERROR = 1
```

This matches the `EXECERROR=1` reported in the issue doc.

#### Workaround B: synthetic minimal repro

A 12-line standalone GAMS file is sufficient to reproduce — does **not**
need `data/gamslib/raw/`:

```gams
Set p /p1*p3/;
Variable y(p), obj;
Equation Objective, Products(p);
Objective.. obj =e= prod(p, y(p));
Products(p).. y(p) =e= 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
```

Translate this with `nlp2mcp`, observe the emitted MCP contains:

```
stat_y(p).. prod(p__, y(p__)) * sum(p__, 1 / y(p__)) + nu_Products(p) =E= 0;
```

with no `y.l(p) = ...;` line. Solve it; PATH aborts with `EXECERROR=1`
on `stat_y` for the same root cause. This synthetic repro is preferable
for unit testing.

### 1.2 Inspect the offending stationarity term

```bash
grep "stat_y" /tmp/lmp2_mcp.gms
# stat_y(p).. prod(p__, y(p__)) * sum(p__, 1 / y(p__)) + nu_Products(p) =E= 0;
```

The `1 / y(p__)` divisor is the proximate cause. `y` is a free variable
with no initialization, so all `y(p)` default to 0.

### 1.3 Inspect the existing variable-init section

```bash
grep -A2 "y\.l\|y\.fx" /tmp/lmp2_mcp.gms
# (no output — y has no init)
```

Compared with `x` (also free, also no `.l`), `y` is identical: neither
gets initialized. The reason `x` doesn't blow up is that `stat_x` doesn't
contain `1/x` — only `stat_y` has the div-by-zero pattern.

### 1.4 Confirm the original NLP solves cleanly

```bash
cp data/gamslib/raw/lmp2.gms /tmp/lmp2_orig.gms
cd /tmp && gams lmp2_orig.gms lo=2
# Expected: SOLVER STATUS 1, MODEL STATUS 2 Locally Optimal (random seed
# affects objective value).
```

The original NLP avoids the issue because the source contains `y.l(p) = 0;`
(yes, *zero*) inside the `loop` body — but each `solve` re-initializes
`y.l = 1` via `cc(p,n)*x.l(n) = uniform(...)` constraints, so `y` ends
up nonzero by the time the NLP solver is called. The MCP emitter does
not capture this loop-time initialization (and even if it did, the
source's literal `y.l(p) = 0` would be no help to us).

### 1.5 Check whether `--nlp-presolve` rescues the model

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_ps.gms \
    --nlp-presolve --quiet
cd /tmp && gams lmp2_ps.gms lo=0
# Result (verified 2026-04-27): still aborts with #1323's compile-time
# Error 66. The presolve path is `Solve nlp ... ; Solve mcp ...` but the
# MCP block still has the same `m` set undefined, so we never reach the
# div-by-zero. Even if #1323 were fixed first, the warm-start from the
# NLP solve would set y.l > 0, so #1243 would NOT fire under presolve.
```

So `--nlp-presolve` is a *de-facto* workaround for #1243 *if and only if*
#1323 is fixed first. That is too circuitous to be the recommended path
on its own.

---

## 2. Root cause (full details in issue doc)

The AD engine differentiates `prod(i, f(i))` via the logarithmic form
(`src/ad/derivative_rules.py:_diff_prod`, line 2885+):

```
d(prod(i, f(i)))/dx = prod(i, f(i)) * sum(i, df(i)/dx / f(i))
```

For an objective `obj =e= prod(p, y(p))`, differentiating w.r.t. `y(p)`
produces the `1 / y(p__)` denominator inside the `sum`. Mathematically
this is fine — when all `y > 0`, the value of the expression is
well-defined — but evaluation order in GAMS computes `1/y(p__)` *before*
the surrounding `prod * sum` collapses, so any `y(p) = 0` triggers
EXECERROR=1 at model-listing time.

`y` is declared `Variable y(p)` (free, default lo=`-inf`, up=`+inf`).
The MCP emitter's variable-init pass (`emit_gams.py:1626-1650`) only
auto-initializes `POSITIVE` variables to 1 — FREE variables are left at
the GAMS default of `.l = 0`, which is the proximate cause of the EXECERROR.

This is the same *class* of issue as #1192 (gtm runtime div-by-zero from
`s(d) = 0`), but the trigger is different: gtm's was `1/distance(d)`
where `distance` was a free var with default 0; lmp2's is `1/y(p)`
arising from `_diff_prod`'s logarithmic form.

---

## 3. Fix Approaches Considered

### Approach 1 — Variable-in-denominator detection + auto-init in MCP emit (RECOMMENDED)

Add a new emitter pre-pass `_collect_var_in_denominator_refs(kkt)`
that scans every stationarity-equation body for `Binary("/", _, VarRef)`
patterns (and divisors transitively containing `VarRef`). For each
distinct free-variable name that appears as a denominator (or inside a
denominator), emit a default `.l = 1` initialization in the variable-init
section, mirroring the existing POSITIVE-var auto-init.

For lmp2, this produces:

```gams
* Issue #1243: variables that appear in denominators of stationarity
* equations need nonzero .l to avoid EXECERROR=1 during model listing.
y.l(p) = 1;
```

(The same emitter already emits `x.l(nn) = 1` for POSITIVE `x` — so the
new code path simply adds FREE vars to the same logic when they are
denominator-positioned.)

**Pros:**
- Minimal, surgical — adds 1 init line per offending FREE variable.
- Reuses the existing variable-init section and the existing pattern
  walker from `_collect_divisor_param_refs` (see §4.2).
- Symmetric with the POSITIVE-var auto-init (`emit_gams.py:1639-1650`).
- Generalizes to other `prod()`/`log()`/CES models with FREE vars in
  similar positions (the issue doc lists catmix, ramsey, hhfair,
  prolog as candidates).
- Does not change AD output; surgical to the emitter.

**Cons:**
- Cannot distinguish "user wanted y.l = 0 explicitly" from "user didn't
  set anything" — but in lmp2 the source literally sets `y.l(p) = 0`
  inside a loop, and the NLP solve re-initializes via constraint values.
  Forcing `y.l = 1` is the right choice for MCP-side warm-starts.
- May over-init in pathological cases where `prod(i, f(i))` always
  evaluates to a context where some `f(i_0) = 0` is intentional. The
  test plan checks the corpus for any such case.

### Approach 2 — Use the algebraic product-derivative form (REJECTED)

Switch `_diff_prod` from logarithmic to algebraic form:

```
d(prod(i, f(i)))/dx = sum(j, df(j)/dx * prod(i!=j, f(i)))
```

This avoids the division entirely. The `i!=j` form requires an `$(ord(i)<>ord(j))`
guard inside the inner `prod`, which works in GAMS.

**Pros:**
- Mathematically eliminates the div-by-zero at the source.
- No emitter-side init logic needed.

**Cons:**
- AD-side change: every model with `prod()` would generate larger
  expressions (the inner `prod` is now O(n) terms in the outer `sum`).
  Empirically tested during prior work: produces `O(n^2)` Jacobian
  rows, which bloats the MCP for catmix (n=200) by ~40×.
- Breaks `_diff_prod` invariants relied on by the existing AD test
  suite — lots of golden-file churn.
- Doesn't help with `1/var` patterns from other sources (e.g., explicit
  `1/y(p)` in user-written equations differentiated by something else).

### Approach 3 — Inject runtime guards `(1/y(p))$(y(p) <> 0)` into stat equations (REJECTED)

Wrap divisions by FREE vars with `$-conditions` at emit time, mirroring
the parameter-side fix in #1320:

```gams
stat_y(p).. prod(p__, y(p__)) * sum(p__, (1 / y(p__))$(y(p__) <> 0)) + nu_Products(p) =E= 0;
```

**Pros:**
- Avoids EXECERROR=1 at model-listing time.
- Reuses existing #1320 guard-injection infrastructure
  (`_inject_divisor_guards`).

**Cons:**
- *Changes the equation's mathematical meaning*: when `y(p) = 0`, the
  guarded term evaluates to 0 instead of being undefined. PATH would
  see a different equation than the true KKT condition. Solver
  convergence behaviour is undefined.
- The *correct* equation requires `y > 0` to be feasible — masking
  the singularity is hiding a bug, not fixing it. (Approach 1 fixes
  the bug by ensuring `y > 0` at the start.)

### Approach 4 — Use `--nlp-presolve` (REJECTED, but deserves mention)

Run the NLP solve first via `--nlp-presolve`; the warm-start sets
`y.l > 0` from the NLP solution, so the MCP's `1/y(p)` evaluates fine.

**Pros:**
- Already implemented (PR #1321); zero new code.
- Mathematically the cleanest answer (use the NLP's locally-optimal
  point as the MCP starting point).

**Cons:**
- Requires #1323 to be fixed first (currently blocks lmp2 compilation
  on either path).
- Not a fix for #1243 itself — it's a *workaround for a workaround*.
  Any user who runs without `--nlp-presolve` (the default) still hits
  the EXECERROR.
- Doesn't help when the user has a model where the NLP isn't easily
  solvable separately (e.g., infeasibility studies, sensitivity
  analyses where the MCP is the artifact of interest).

We will document `--nlp-presolve` in the issue doc as a workaround,
but the durable fix is Approach 1.

---

## 4. Recommended Implementation: Approach 1

### 4.1 Overview

Augment the existing variable-init pass in `emit_gams.py` (around line
1626) so that, in addition to the POSITIVE-var auto-init branch, a new
parallel branch fires for FREE variables that appear in denominator
positions in any stationarity equation body. The branch emits the same
`var.l(d) = 1;` pattern (without the upper-bound clamp, since FREE
vars have no upper bound).

### 4.2 Code sites

| File | Function | Change |
|------|----------|--------|
| `src/emit/equations.py` | new `_collect_divisor_var_refs(expr) -> set[VarRef]` | Mirror the existing `_collect_divisor_param_refs` (line 242) but collect `VarRef` instead of `ParamRef`. Walks divisor positions in `Binary("/")`, `log()`, `log2()`, `log10()`. Returns the set of indexed VarRefs that appear in divisor position. |
| `src/emit/emit_gams.py` | new module-level helper `_compute_denominator_free_vars(kkt)` | Iterate `kkt.equations` (stationarity equations); for each equation body, call `_collect_divisor_var_refs`; collect the set of VAR NAMES (not VarRefs — we just want the names) that are FREE (i.e., `model_ir.variables[name].kind == VarKind.FREE`). Return as `set[str]`. |
| `src/emit/emit_gams.py` | inside the variable-init loop (~line 1626) | After the existing POSITIVE-var branch, add a parallel branch: `elif var_def.kind == VarKind.FREE and var_name.lower() in denominator_free_vars and not has_init:` then emit `var.l(d) = 1;` if domain non-empty, else `var.l = 1;`. Track with a new `has_free_denom_init` flag for the section-comment trigger. |
| `src/emit/emit_gams.py` | section header | When `has_free_denom_init` is True, prepend a comment line to the variable-init section: `* Issue #1243: FREE variables appearing in denominators of stationarity equations need .l = 1 to avoid EXECERROR=1 from div-by-zero at model listing.` |

### 4.3 Detection criterion: "FREE var in denominator position"

A `VarRef` is in scope iff:

1. It appears in the divisor side of a `Binary("/", _, ·)` (or transitively
   inside arithmetic that occupies that side), OR
2. It appears as an argument to `log`/`log2`/`log10` (which generate
   `1/x` after differentiation — same root cause).

**AND** the named variable's `VarDef.kind` is `VarKind.FREE` (we don't
init POSITIVE vars here — they already get `var.l = 1` from the existing
branch). For NEGATIVE/SOS vars, this case isn't expected to arise; if it
does, leave them alone (they're out of scope for now).

The walker reuses the dataclass-fields fallback from
`_collect_divisor_param_refs:302-314`, so it generically traverses any
new node types added later.

### 4.4 Filter: only stationarity equations

We should NOT run this detection on the original equations
(comp/Objective/Equality) — the user's source code is the user's
problem. We run only on stat_X equations because those are AD-generated
and the `1/var` pattern is created by us (`_diff_prod`).

`KKTSystem.stationarity_equations` (or whatever the field is called in
`src/kkt/system.py`) already separates stat equations from the rest.
The implementation should use that boundary.

### 4.5 Idempotency and ordering

- The init line is naturally idempotent.
- It must come BEFORE the solve statement and AFTER any explicit
  `var.l(d) = ...` from `l_map`/`l_expr_map` (else we'd overwrite the
  user's choice). The current code already orders `l_map` checks before
  the kind-based default (lines 1569-1582 → 1626), so the new branch
  fits naturally at the same point with the same `not has_init` guard.

### 4.6 Interaction with `--nlp-presolve`

Under `--nlp-presolve`, the MCP's variable-init lines run AFTER the
NLP `solve` block, which writes `y.l(p)` from the NLP optimum. Our
emitted `y.l(p) = 1;` would then *overwrite* the warm-start. To preserve
the warm-start, gate the new branch on `not config.nlp_presolve`:

```python
if (
    var_def.kind == VarKind.FREE
    and var_name.lower() in denominator_free_vars
    and not has_init
    and not config.nlp_presolve  # let the NLP warm-start dictate y.l
):
    ...
```

(If `config.nlp_presolve` is not currently exposed at the emit site,
add it to the call signature — it's already on `Config`.)

### 4.7 Worked example for lmp2

Before fix:
```gams
Variables y(p), x(nn), obj, nu_Products(p);
Positive Variables lam_Constraints(m), piL_x(nn);
* (no y.l, no x.l for FREE vars; piL_x.l = 1 for POSITIVE)
piL_x.l(nn) = 1;
piL_x.l(nn) = min(piL_x.l(nn), piL_x.up(nn));
```

After fix:
```gams
Variables y(p), x(nn), obj, nu_Products(p);
Positive Variables lam_Constraints(m), piL_x(nn);
* Issue #1243: FREE variables appearing in denominators of stationarity ...
y.l(p) = 1;
piL_x.l(nn) = 1;
piL_x.l(nn) = min(piL_x.l(nn), piL_x.up(nn));
```

The `y.l(p) = 1` makes `1/y(p) = 1` finite at the initial point;
`prod(p, y(p)) * sum(p, 1/y(p)) = 1 * |p|` evaluates cleanly; PATH
proceeds with the solve.

---

## 5. Test Plan

### 5.1 New unit tests — `tests/unit/emit/test_var_in_denominator_init.py`

5 cases:

1. **Stationarity body has `1/y(p)` and `y` is FREE**: emitter emits
   `y.l(p) = 1;` line with the issue-#1243 comment.
2. **Stationarity body has `1/y(p)` but `y` is POSITIVE**: no new line
   (existing POSITIVE branch handles it).
3. **Stationarity body has `1/y` (scalar, no domain) and `y` is FREE**:
   emitter emits `y.l = 1;` (no parenthesized index).
4. **Stationarity body has `1/y(p)` BUT `y.l(p)` is already set in
   source via `l_map`**: emitter does NOT add the auto-init (existing
   `has_init` short-circuits).
5. **Stationarity body has `log(y(p))` and `y` is FREE**: emitter emits
   `y.l(p) = 1;` (because `log(0)` produces UNDF, same root cause).

### 5.2 `_collect_divisor_var_refs` walker test — `tests/unit/emit/test_collect_divisor_var_refs.py`

Mirror the existing `_collect_divisor_param_refs` walker test
(`tests/unit/emit/test_collect_divisor_param_refs.py` if it exists,
otherwise create alongside). 5 cases:

1. `Binary("/", Const(1), VarRef("y", ("p",)))` → returns `{VarRef y(p)}`.
2. `Binary("/", VarRef("z", ()), Const(2))` → numerator, returns `{}`.
3. Nested: `Binary("/", _, Binary("+", VarRef("y", ("p",)), Const(1)))`
   → returns `{VarRef y(p)}` (inside a denominator subtree).
4. `Call("log", [VarRef("y", ("p",))])` → returns `{VarRef y(p)}`.
5. `Sum(("p",), Binary("/", _, VarRef("y", ("p",))))` → returns
   `{VarRef y(p)}` (recurses into Sum body).

### 5.3 Integration test — `tests/integration/emit/test_lmp2_y_init.py`

```python
@pytest.mark.integration
def test_lmp2_emits_y_l_init_for_stat_y_denominator():
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("requires data/gamslib/raw/lmp2.gms")
    output = _emit_mcp_for(src)
    # The fix emits y.l(p) = 1 because stat_y has 1/y(p).
    assert re.search(r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE)
    # Existing POSITIVE-var auto-init still works.
    assert re.search(r"^\s*piL_x\.l\(nn\)\s*=\s*1\s*;", output, re.MULTILINE)
    # x is FREE but does NOT appear in denominator → no init.
    assert not re.search(r"^\s*x\.l\(nn\)\s*=\s*1\s*;", output, re.MULTILINE)
```

### 5.4 Synthetic-NLP integration test — `tests/integration/emit/test_prod_objective_div_init.py`

```python
@pytest.mark.integration
def test_synthetic_prod_objective_emits_y_init():
    """A minimal NLP `obj = prod(p, y(p))` with free y should emit
    `y.l(p) = 1` to avoid EXECERROR=1 from `_diff_prod`'s 1/y term."""
    src = textwrap.dedent("""
        Set p /p1*p3/;
        Variable y(p), obj;
        Equation Objective, Products(p);
        Objective.. obj =e= prod(p, y(p));
        Products(p).. y(p) =e= 1;
        Model nlp /all/;
        Solve nlp using nlp minimizing obj;
    """)
    output = _emit_mcp_for_source(src)
    assert re.search(r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE)
```

This test does NOT need `data/gamslib/raw/` — it uses a string source.

### 5.5 Pipeline retest (acceptance criterion)

Because lmp2 is blocked by #1323 today, the strict acceptance signal is
indirect: the MCP file should *contain* the new `y.l(p) = 1` line.
Verify at the integration-test level (5.3 above).

If #1323 is fixed in the same sprint, the full pipeline retest is:

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model lmp2 --quiet
```

Acceptance:
- lmp2 compiles cleanly (no Error 66 — from #1323's fix).
- lmp2's MCP solve does not abort with `EXECERROR=1` on `stat_y`.
- Stretch goal: `Match: 1 (100.0%)` against the NLP reference.

If #1323 is NOT fixed in the same sprint, the integration tests in
§5.3-5.4 are sufficient acceptance for #1243's code change. The
end-to-end pipeline test is moved to the meta-issue closing both
#1243 and #1323 jointly.

### 5.6 Regression sweep

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --solve-success --quiet
```

Acceptance: 0 NEW translate failures, 0 NEW solve regressions, no NEW
mismatches on currently-matching models. Particular attention to:

- **Models with `prod()`**: lmp2, catmix, ramsey, hhfair, prolog.
  Check whether they get incidental progress from the new init.
- **Models with `log()` of a free var**: any nonlinear-utility CGE
  (irscge, lrgcge, moncge, stdcge, twocge, splcge, quocge). Check
  for objective-value drift; the new `y.l = 1` could nudge PATH to a
  different KKT point on non-convex models.
- **Models whose source has explicit `y.l = 0`** (lmp2 itself): the
  new init must NOT fire when the source provides explicit init via
  `l_map`/`l_expr_map`. The `not has_init` guard handles this; verify
  via test 5.1 case 4.

### 5.7 Adjacent-model probe

After lmp2 passes, also run camcge (#1324) and elec (#1325) to see
whether Approach 1 has any spillover benefit. Expected: marginal —
those models have different root causes (KKT-side div-by-zero for
camcge, distance-zero for elec), but document any progress.

---

## 6. Time Estimate

| Phase | Work | Hours |
|-------|------|-------|
| 1. Setup | branch, reproduce via Workaround A (manual `m(mm)=yes` edit), verify EXECERROR pattern | 0.5 |
| 2. Walker function | `_collect_divisor_var_refs(expr)` (mirror of `_collect_divisor_param_refs`, ~70 lines) | 1.0 |
| 3. Emitter wiring | `_compute_denominator_free_vars(kkt)` + new branch in variable-init loop + `--nlp-presolve` interaction gate | 2.0 |
| 4. Walker unit tests | 5 cases in `tests/unit/emit/test_collect_divisor_var_refs.py` | 1.0 |
| 5. Emitter unit tests | 5 cases in `tests/unit/emit/test_var_in_denominator_init.py` | 1.5 |
| 6. Integration test | lmp2 + synthetic prod test (`tests/integration/emit/test_prod_objective_div_init.py`) | 0.75 |
| 7. lmp2 validation | re-emit, manual `m(mm)=yes` patch (or wait for #1323), GAMS solve, verify no EXECERROR | 0.5 |
| 8. Regression sweep | full-corpus solve-success, diagnose any drift | 1.5 |
| 9. Quality checks | `make typecheck && make format && make lint && make test` | 0.5 |
| 10. PR + review | open PR, address Copilot review (~1 round) | 1.0 |
| **Total** | **~10.25 hours (best case 7h, worst case 13h)** | |

**Sprint placement:** fits Sprint 26 alongside #1323 (the two are
naturally a pair — fixing both unblocks lmp2 end-to-end). Effort-vs-reward:
1 model unblock (lmp2 → likely match), with possible incidental benefit
on prod/log-using models in the corpus.

---

## 7. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **`y.l = 1` over-init breaks a model where `y(p) = 0` is the optimum.** Forcing `y.l = 1` is a starting point, not a constraint, so PATH should still find the optimum — but on non-convex models it may converge to a different local optimum than the NLP did. | Medium | The regression sweep at 5.6 catches this. If a canary regresses, narrow the criterion: only emit when ALL stat-equation occurrences of `var` are denominator-positioned (not just any). Or expose a `--no-denominator-var-init` flag for users who want to override. |
| **Misclassification: a `Binary("/", _, expr)` where `expr` is `var * const` or `const * var` — the walker may miss this pattern if it doesn't recurse properly.** | Low | Walker test §5.2 case 3 explicitly covers this. The `_collect_divisor_param_refs` model is already proven to recurse correctly. |
| **`_collect_divisor_var_refs` recurses into Sum/Prod bodies and treats them as divisor scope when they're not.** This is the bug class Sprint 25 saw with the param-side walker on stat equations with `sum(j, 1/y(j))`. | Low | The walker resets `in_divisor=False` on Sum/Prod boundaries (line 294 of `_collect_divisor_param_refs`); mirror exactly. Test §5.2 case 5 verifies. |
| **Interaction with `--nlp-presolve`**: the new `y.l = 1` fires AFTER the NLP solve, overwriting the warm-start. | Low | §4.6's gate on `not config.nlp_presolve` prevents this. Add an integration test that runs with `--nlp-presolve` and verifies `y.l = 1` is NOT emitted. |
| **`emitted_y_init_for_stat_y` test fragility**: the assertion uses a regex on the emitted text, which can break if a future PR rewrites the emit format. | Low | Keep the assertion narrow (`y\.l\(p\)\s*=\s*1`), not a full-line match. |
| **Model has FREE var that's denominator-positioned BUT also has explicit `y.l(p) = 0` in source** (lmp2 is exactly this case). Our `not has_init` guard would skip the new init, leaving the EXECERROR in place. | Medium | For lmp2 specifically, the source's `y.l = 0` is *inside a loop body* and so is NOT extracted by the IR (today). If the IR ever learns to extract it (Sprint 26+), we'll need to *override* the `0` with our `1` (or warn the user). For now, the IR-doesn't-extract behavior is what lets the fix work. Add a test (§5.1 case 4) that documents this interaction so a future change doesn't silently regress. |
| **Performance**: the recursive walker over every stat equation body adds emit-time cost. | Very low | Single pass per stat equation; trivial cost vs. the rest of emission. The corpus has ~50 models with stat equations averaging <500 nodes each. |

---

## 8. Out-of-scope (deferred to follow-up issues)

- **Switching `_diff_prod` to algebraic form**: out of scope. That's
  Approach 2; tracked separately if Approach 1 doesn't catch enough
  cases. Filing a placeholder issue for it is part of the PR follow-up.
- **Fixing #1323** (`m(mm)` not extracted) — separate issue, separate
  fix. They are paired for lmp2's end-to-end pipeline result but
  independent at the code level. The PR will note that lmp2 won't
  fully pass until both are merged.
- **Non-stationarity equations with `1/var`**: if user-written original
  equations have `1/var` patterns, the user's original NLP would also
  have failed. We don't auto-init for user equations.
- **Init values other than 1**: future work could pick a smarter starting
  point (e.g., from constraint algebra or from a pre-solve iteration),
  but `1` is conservative and correct for "any positive value" semantics.
- **Re-emit stale checked-in MCP artifacts**: out of scope; queue for
  the post-Sprint-26 housekeeping PR.
- **NEGATIVE / SOS variable kinds**: not expected to arise in
  denominator position; if they do, escalate as a separate issue.

---

## 9. PR Title and Branch

- **Branch:** `sprint26-fix-1243-lmp2-y-init`
- **PR title:** `Sprint 26: Fix #1243 — emit .l = 1 for FREE vars in stationarity-equation denominators`
- **PR body:** standard structure (Summary / Root cause / Fix / Test plan / Refs).
- **Closes:** #1243. Notes #1323 as a paired blocker for the
  end-to-end lmp2 pipeline result. Notes adjacent models (catmix,
  ramsey, etc.) for follow-up if regression sweep shows incidental
  benefit.

---

## 10. Acceptance Criterion (Definition of Done)

1. ✅ The MCP emitted for lmp2 (or for the synthetic 12-line repro from
   §1.1 Workaround B) contains `y.l(p) = 1;` (or `y.l = 1;` for the
   scalar case) when `y` is FREE and appears in a stationarity-equation
   denominator.
2. ✅ The new init line is NOT emitted when the source provides explicit
   `y.l(p) = ...;` via `l_map`/`l_expr_map`.
3. ✅ The new init line is NOT emitted under `--nlp-presolve` (the warm-start
   takes precedence).
4. ✅ POSITIVE variables continue to be initialized via the existing
   branch (`var.l(d) = 1; var.l(d) = min(var.l, var.up);`); the new
   branch adds to that, doesn't replace.
5. ✅ All 3,648+ unit tests still pass.
6. ✅ Tier-1 canaries (sparta, gussrisk, prolog, partssupply, ship,
   paklive, quocge, splcge, gtm) still match. CGE family doesn't drift
   in objective value.
7. ✅ Full corpus regression sweep on solve-success canary: 0 NEW
   translate or solve regressions.
8. ✅ `make typecheck && make format && make lint && make test` clean.
9. ✅ PR opened, Copilot review addressed.

If criterion 1 holds but lmp2 doesn't yet reach `model_optimal`
end-to-end (because #1323 is still open), the fix for #1243 is still
complete on its own merits — it eliminates the EXECERROR class for any
model with the `1/var` stationarity pattern. Document the residual as
"awaiting #1323" and proceed.
