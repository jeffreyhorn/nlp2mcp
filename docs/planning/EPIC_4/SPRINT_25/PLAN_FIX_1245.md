# Plan to Fix #1245 — camcge runtime division-by-zero / domain errors on non-traded indices

**GitHub Issue:** [#1245](https://github.com/jeffreyhorn/nlp2mcp/issues/1245)
**Issue Doc:** `docs/issues/ISSUE_1245_camcge-runtime-division-by-zero-non-traded.md`
**Predecessors / closely-related:**
- [#882](https://github.com/jeffreyhorn/nlp2mcp/issues/882) (CLOSED) — MCP pairing errors
- [#871](https://github.com/jeffreyhorn/nlp2mcp/issues/871) (CLOSED) — Subset conditioning
- [#1327](https://github.com/jeffreyhorn/nlp2mcp/issues/1327) (CLOSED, PR #1328) — `declaration_domain` for parent/subset equations + `multiplier_domain_widenings` machinery — **this fix builds directly on #1327**
- [#1192](https://github.com/jeffreyhorn/nlp2mcp/issues/1192) (CLOSED) — gtm runtime div-by-zero (related class)
- [#1243](https://github.com/jeffreyhorn/nlp2mcp/issues/1243) (CLOSED, PR #1328) — lmp2 `1/y(p)` div-by-zero (related class)

**Affected models:**
- camcge (primary)
- Adjacent CGE-family models with `it`/`in` traded/non-traded splits and CES production: irscge, lrgcge, moncge, stdcge, twocge, splcge, quocge — likely benefit incidentally if the regression sweep on this fix covers them.

**Goal:** camcge progresses from `path_solve_terminated` (EXECERROR=4 from `1/0`, `0**negative`, UNDF) to PATH-solve invocation. Stretch goal: `model_optimal` matching the NLP reference.

---

## 1. Reproduction (verified 2026-04-30 on `main` with PR #1328 merged)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/camcge_mcp.gms --quiet
cd /tmp && gams camcge_mcp.gms lo=0

# Expected:
# **** Exec Error at line 529: division by zero (0)
# **** Exec Error at line 529: A constant in a nonlinear expression in equation
#       stat_pd evaluated to UNDF
# **** Evaluation error(s) in equation "stat_pd(services)"
# **** Evaluation error(s) in equation "stat_pd(publiques)"
# **** Exec Error at line 543: rPower: FUNC DOMAIN: x**y, x=0,y<0
# **** Evaluation error(s) in equation "stat_xxd(services)"
# **** Evaluation error(s) in equation "stat_xxd(publiques)"
# **** SOLVE from line 738 ABORTED, EXECERROR = 4
```

Inspect `stat_pd(i)` and `stat_xxd(i)` in the emitted MCP — both contain
multiplier-bearing CES-derivative terms multiplied by `nu_esupply(i)`,
`nu_costmin(i)`, `nu_armington(i)`, `nu_cet(i)` — multipliers whose source
equations are defined only on the traded subset `it`. The CES bodies have
`1/gamma(i)`, `pe(i)/pd(i)`, `pd(i)/pm(i)`, `xxd(i)**(rhot-1)` patterns. For
non-traded indices (`services`, `publiques`):
- `gamma(in) = 0` (set explicitly in source line 200)
- `e.fx(in) = 0`, `m.fx(in) = 0`
- `pd`, `pe`, `pm`, `pwe`, `xxd` have no `.lo` / `.fx` for non-traded → default to 0
- Multipliers `nu_esupply.fx(in) = 0` (correctly emitted by #1327's fix-inactive path)

**The pathology:** GAMS evaluates the entire stationarity body before
multiplying by the multiplier. Even with `nu_esupply(in) = 0`, the
intermediate `1/gamma(in) = 1/0` and `pd**negative_exp` raise UNDF /
domain errors at model-listing time, aborting the solve.

---

## 2. Root Cause

For an NLP equation declared over a parent set but defined over a
dynamic / static subset (e.g. `esupply(it)..` over `i`), PR #1328 (#1327)
correctly:
- Declares the multiplier over the parent set: `Positive Variables nu_esupply(i);`
- Fixes inactive instances: `nu_esupply.fx(i)$(not (it(i))) = 0;`
- Emits the comp/equality equation with the parent-set declaration and
  body-subset head: `Equations comp_esupply(i); comp_esupply(it).. ...`

But **the stationarity equation body still emits the multiplier
contribution unguarded**: stat_pd's contribution from differentiating
`esupply(it)` w.r.t. `pd` is

```
... + ((-1) * <CES-derivative-of-esupply-body>) * nu_esupply(i) + ...
```

GAMS evaluates `<CES-derivative-of-esupply-body>` for ALL `i`, including
`in` indices where the inputs are zero. The product is then multiplied
by `nu_esupply(i)`, which would be 0 for non-traded — but GAMS already
crashed during the evaluation of the inner expression.

This is the symmetric problem to #1327: #1327 fixed the **declaration**
side (so GAMS doesn't reject dynamic-subset declaration domains); #1245
fixes the **body-evaluation** side (so GAMS doesn't evaluate a CES
expression that only makes sense on a subset, for instances outside the
subset).

---

## 3. Fix Approaches

### Approach 1 — Emitter-side multiplier-term guard injection (RECOMMENDED)

After the stationarity bodies are built, walk each `stat_X(d)` body and
wrap every term of the form `<expr> * nu_Y(d)` (or `nu_Y(d) * <expr>`,
or `<expr> * lam_Y(d)`) with the source equation Y's body-domain filter
when:
1. `Y` has `multiplier_domain_widenings[mult_Y] = (body_domain, declaration_domain)`,
   AND
2. `body_domain != declaration_domain` (i.e., true parent/subset split).

The wrapping turns

```gams
... + ((-1) * <CES-deriv>) * nu_esupply(i) + ...
```

into

```gams
... + (((-1) * <CES-deriv>) * nu_esupply(i))$(it(i)) + ...
```

GAMS then skips evaluating the term entirely when `it(i)` is false,
sidestepping the inner div-by-zero / domain error.

**Pros:**
- Reuses #1327's `multiplier_domain_widenings` infrastructure — no new
  data flow.
- Localized to the stationarity emit step; doesn't touch AD or
  KKT-build code.
- Mathematically equivalent: `nu_esupply(in) = 0` already, so wrapping
  with `$(it(i))` doesn't change the equation's value, only avoids the
  intermediate UNDF.
- Symmetric with #1320's divisor-guard injection on parameter-side
  expressions.

**Cons:**
- Emitter pattern-matching is fragile — needs to recognize multipliers
  in arbitrary AST positions (inner factor of products, arguments of
  Sums, etc.). The walker must handle `Binary("*", ..., MultiplierRef)`,
  `Binary("*", MultiplierRef, ...)`, and nested cases.
- Doesn't help bound multipliers (`piL_*`, `piU_*`) or other
  non-equation-derived contributions — but those don't have parent/subset
  splits in practice.

### Approach 2 — AD-side body-domain propagation

Modify the stationarity / Jacobian / gradient builders to track each
contribution's source equation. When generating a term `J_eq[X][Y] *
nu_X` for the stat_Y equation, wrap with `$(X_body_domain(d))` if X is
parent-declared / subset-defined.

**Pros:**
- "Right" architectural fix — body-domain restriction lives at the
  point where the contribution is generated.
- Fix carries automatically through any future AD changes.

**Cons:**
- Invasive — touches `src/ad/jacobian.py`, `src/ad/gradient.py`,
  `src/kkt/stationarity.py` build paths.
- Requires tracking provenance metadata on every Expr node OR threading
  the source equation through every AD call. Either is a 1-2 day
  refactor with broad regression risk.

### Approach 3 — Variable-init for non-traded prices/quantities

Emit `pd.l(in) = 1; pe.l(in) = 1; pm.l(in) = 1; xxd.l(in) = 1` etc. so
the CES expressions evaluate to finite values for non-traded indices.

**Pros:**
- 5-line emitter change, mirroring #1243's FREE-var-in-denominator init.

**Cons:**
- Doesn't fix `gamma(in) = 0` — the `1/gamma(in)` term still produces
  UNDF regardless of price initialization. Requires also setting
  `gamma.l(in) = 1`, but `gamma` is a parameter (not a variable), so
  changing it changes the model semantics.
- Even if we make the prices nonzero, the multiplier contribution is
  *meaningless* for non-traded indices — we'd be computing nonzero CES
  derivatives that get multiplied by zero multipliers, which is
  numerically wasteful and obscures the true KKT structure.
- Doesn't fix `0 ** negative_exp` for `xxd(in) = 0` in stat_xxd unless
  `xxd.l(in)` is also non-zero. Cascading inits become messy.

### Approach 4 — Condition entire stat_pd / stat_xxd on `it(i)` (REJECTED)

Wrap the entire body with `$(it(i))`.

**Pros:** trivial.

**Cons:** loses the contributions from `absorption(i)` and `sales(i)` —
which ARE defined over all `i` (parent set, no subset filter on the
body), and contribute to stat_pd validly for non-traded `i`. Wrapping
the whole equation drops these terms and breaks the KKT system for
non-traded primals.

---

## 4. Recommended Implementation: Approach 1 (multiplier-term guard injection)

### 4.1 Overview

Add a post-build pass on `kkt.stationarity` that, for each stationarity
equation body, identifies multiplier-bearing terms whose multiplier has
an entry in `kkt.multiplier_domain_widenings` and wraps them with the
source equation's body-domain filter.

### 4.2 Code sites

| File | Function | Change |
|------|----------|--------|
| `src/emit/equations.py` | new `_inject_multiplier_subset_guards(expr, kkt)` | Walk an Expr; for every `Binary("*", LHS, RHS)` (recursively), if either side is a `MultiplierRef` whose name appears in `kkt.multiplier_domain_widenings` AND the widening represents a true parent/subset split, wrap the entire `Binary("*", ...)` in a `DollarConditional` with `condition = SetMembershipTest(<subset>, <idx>)`. Mirrors `_inject_divisor_guards`'s recursion shape. |
| `src/emit/equations.py` | `emit_equation_definitions` | Call `_inject_multiplier_subset_guards` on each stationarity equation's `lhs_rhs[0]` before emitting. |
| `src/kkt/kkt_system.py` | `KKTSystem` | Add helper `subset_filter_for_multiplier(mult_name) -> Expr | None` returning the subset-membership Expr (e.g., `SetMembershipTest("it", ("i",))`) when the multiplier is parent-widened from a subset. |
| (no IR changes) | — | The information needed (`multiplier_domain_widenings`) is already populated by #1327's fix in `assemble_kkt_system`. |

### 4.3 Detection criterion

A `MultiplierRef("nu_X", indices)` in the stationarity body should
trigger a guard wrap iff:
1. `kkt.multiplier_domain_widenings.get(mult_name)` returns
   `(orig_dom, widened_dom)` with `orig_dom != widened_dom`, AND
2. The body domain (`orig_dom`) consists of dynamic-subset names whose
   parent matches `widened_dom`, AND
3. The arities match (`len(orig_dom) == len(widened_dom)`).

The injected condition is `it(i)` (or whatever the subset name is) with
the equation's index variable.

### 4.4 Walker structure

```python
def _inject_multiplier_subset_guards(expr: Expr, kkt: KKTSystem) -> Expr:
    """Wrap multiplier-bearing terms with their source equation's
    body-domain filter when the multiplier is parent-widened from a
    subset. Mathematically a no-op (the multiplier is fixed to 0
    outside the subset by #1327's fix-inactive emit), but prevents
    GAMS from evaluating the multiplier's coefficient expression
    for instances outside the subset — avoiding the div-by-zero /
    domain errors that arise when the source equation's body
    parameters (e.g., gamma(in) = 0 in camcge) make those expressions
    UNDF.
    """
    # Recursive descent mirroring _inject_divisor_guards. At each
    # Binary("*", ...) node, check whether either side (or any
    # descendant, via flattened factor walk) is a MultiplierRef with
    # an entry in multiplier_domain_widenings; if so, wrap the
    # entire Binary node in DollarConditional($(subset(idx))).
```

### 4.5 Test fixture

Synthetic minimal CGE-shaped repro:

```gams
Set i / a, b, c, d /;
Set it(i) / a, b /;
Set in(i) / c, d /;
Parameter gamma(i) / a 0.5, b 0.3, c 0, d 0 /;
Variable pd(i), pe(i), e(i), xxd(i), obj;
Equation Objective, esupply(i);
Objective.. obj =e= sum(i, pd(i));
esupply(it).. e(it)/xxd(it) =e= (pe(it)/pd(it) * (1-gamma(it))/gamma(it))**(1.5);
e.fx(in) = 0;
xxd.lo(it) = 0.01;
pd.lo(it) = 0.01; pe.lo(it) = 0.01;
Model m / all /;
Solve m using nlp minimizing obj;
```

This produces a stat_pd(i) body with `... * nu_esupply(i)` term that
references `1/gamma(i)`. For non-traded i ∈ in, gamma(i)=0 → UNDF without
the fix; with the fix, the term is wrapped in `$(it(i))` and the UNDF
is sidestepped.

---

## 5. Test Plan

### 5.1 Walker unit tests — `tests/unit/emit/test_inject_multiplier_subset_guards.py`

5 cases:

1. **Multiplier-bearing term gets wrapped**: A `Binary("*", expr,
   MultiplierRef("nu_esupply", ("i",)))` where `multiplier_domain_widenings`
   has `nu_esupply: (("it",), ("i",))` should produce
   `DollarConditional(<original>, SetMembershipTest("it", ("i",)))`.

2. **Non-widened multiplier left untouched**: A multiplier with no
   widening entry (e.g., `nu_balance` over `(i)` with body=`(i)`) is
   not wrapped.

3. **Bound multiplier (piL_*, piU_*) left untouched**: bound
   multipliers don't have parent/subset splits.

4. **Nested wrapping**: stationarity body `(a*nu1) + (b*nu2)` where both
   nu1 and nu2 are widened produces two independent wraps.

5. **Multiplier inside Sum body wraps the Sum**: `Sum(("j",), <expr> *
   nu_X(j))` where nu_X is widened — wrap inside the body, not the Sum.

### 5.2 Integration test — `tests/integration/emit/test_camcge_multiplier_guards.py`

```python
@pytest.mark.integration
def test_camcge_stat_pd_wraps_traded_only_multiplier_terms():
    src = "data/gamslib/raw/camcge.gms"
    if not os.path.exists(src):
        pytest.skip(...)
    output = _emit_mcp_for(src)
    # The nu_esupply / nu_costmin / nu_armington / nu_cet contributions
    # to stat_pd(i) must be wrapped in $(it(i)).
    stat_pd_line = next(l for l in output.splitlines() if l.startswith("stat_pd(i)"))
    assert "nu_esupply(i))$(it(i))" in stat_pd_line or \
           ")$(it(i)) * nu_esupply" in stat_pd_line
    # Must NOT touch the absorption / sales terms (those are over (i)).
    assert "nu_absorption(i)" in stat_pd_line  # bare, not wrapped
```

### 5.3 Pipeline regression sweep

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --solve-success --quiet
```

Acceptance:
- camcge progresses past `path_solve_terminated`.
- Tier-1 canaries (sparta, gussrisk, prolog, partssupply, ship,
  paklive, quocge, splcge, gtm, lmp2) still match.
- CGE family (irscge, lrgcge, moncge, stdcge, twocge) doesn't drift in
  objective value. Particular attention because they share the
  `it`/`in` split pattern and may get incidental progress / regression.

### 5.4 Quality gate

`make typecheck && make lint && make format && make test`

---

## 6. Time Estimate

| Phase | Work | Hours |
|-------|------|-------|
| 1. Setup | branch, reproduce, inspect post-#1327 emission, confirm `multiplier_domain_widenings` is the right hook | 0.5 |
| 2. Helper `subset_filter_for_multiplier` | new method on `KKTSystem` (~20 lines) | 0.5 |
| 3. Walker `_inject_multiplier_subset_guards` | mirror `_inject_divisor_guards` recursion shape (~100 lines) | 2.5 |
| 4. Wire walker into `emit_equation_definitions` | call site for stationarity equations only | 0.5 |
| 5. Walker unit tests | 5 cases | 1.5 |
| 6. Integration test | camcge-specific test | 1.0 |
| 7. camcge end-to-end validation | re-emit, GAMS compile + PATH solve, compare against NLP | 0.75 |
| 8. CGE regression sweep | irscge / lrgcge / moncge / stdcge / twocge / splcge / quocge — verify no drift | 1.5 |
| 9. Full corpus solve-success canary | regression scan | 1.5 |
| 10. Quality gate | typecheck / lint / format / test | 0.5 |
| 11. PR + review | open PR, address Copilot review (~2 rounds) | 1.5 |
| **Total** | **~12.25 hours (best case 8h, worst case 16h)** | |

**Sprint placement:** fits Sprint 26 Day 1–2. Effort-vs-reward: 1
direct unblock (camcge → potentially `model_optimal`), with possible
incidental benefit on the CGE family.

---

## 7. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Walker over-wraps** terms that don't need it (false positives), changing equation semantics. | Low | Wrap is mathematically a no-op when the multiplier is already 0 outside the subset (#1327's fix-inactive emit guarantees this). Test §5.1 case 2 catches false positives on non-widened multipliers. |
| **Walker under-wraps** — misses multipliers in unusual AST positions (Sum body, nested products, Unary). | Medium | Test §5.1 cases 4 + 5 cover Sum/nested scenarios. Mirror `_inject_divisor_guards`'s walker shape for parity. |
| **MultiplierRef identification is fragile** — the AST might use `VarRef` (or something else) for multipliers in some emitter paths. | Medium | Audit the stationarity-build path to confirm multipliers always emit as `MultiplierRef`. Fall back to checking by name (`name in kkt.multipliers_eq` etc.) if needed. |
| **CGE family regressions** — wrapping changes the lst-time evaluation order on models that previously matched. | Medium | The wrap only fires for parent/subset multipliers. For CGE models, the same `it`/`in` pattern is present but is currently handled by other means (probably via `gamma(in)=0` propagating to a multiplier that's also zero, no UNDF). Verify each CGE model post-fix doesn't regress. |
| **Bound multipliers** (`piL_*`, `piU_*`) get accidentally wrapped. | Low | Detection criterion explicitly checks `multiplier_domain_widenings`, which only has equation multipliers (`nu_*`, `lam_*`). |
| **Performance** — the walker adds emit-time cost for every stationarity equation. | Very low | Single recursive pass per body; trivial vs overall emission. |

---

## 8. Out-of-scope (deferred to follow-up issues)

- **AD-side body-domain propagation (Approach 2)** — better architecturally,
  but a 1-2 day refactor. File as a follow-up if the emitter-side
  approach turns out to leak edge cases.
- **Other CGE corpus mismatches** (irscge, lrgcge, moncge, stdcge
  alias-AD mismatches per #1138) — those have a different root cause
  and are out of scope.
- **Re-emit stale checked-in MCP artifacts** for camcge once it solves.

---

## 9. PR Title and Branch

- **Branch:** `sprint26-fix-1245-camcge-multiplier-subset-guards`
- **PR title:** `Sprint 26: Fix #1245 — wrap traded-only multiplier terms in stationarity bodies with subset filter`
- **PR body:** standard structure (Summary / Root cause / Fix / Test plan / Refs).
- **Closes:** #1245. Mentions #1327 as the predecessor whose
  `multiplier_domain_widenings` machinery this PR builds on.

---

## 10. Acceptance Criterion (Definition of Done)

1. ✅ `gams /tmp/camcge_mcp.gms` no longer aborts with EXECERROR=4 from
   `stat_pd(services)` / `stat_pd(publiques)` / `stat_xxd(services)` /
   `stat_xxd(publiques)`.
2. ✅ camcge progresses past `path_solve_terminated`.
3. ✅ Stretch: PATH reaches `model_optimal` matching the NLP reference.
4. ✅ All 4,654+ unit tests still pass.
5. ✅ Tier-1 canaries (sparta, gussrisk, prolog, partssupply, ship,
   paklive, quocge, splcge, gtm, lmp2) still match.
6. ✅ Full corpus regression sweep on solve-success canary: 0 NEW
   translate or solve regressions.
7. ✅ `make typecheck && make lint && make format && make test` clean.
8. ✅ PR opened, Copilot review addressed (~2 rounds expected).

If criterion 1 holds but criterion 3 fails (camcge reaches PATH but
doesn't match), that's still progress — the structural EXECERROR=4
pathology is gone — and any residual mismatch is a separate concern
(likely alias-AD, cf. #1138 family). Document and proceed.
