# otpop: MODEL STATUS 5 (Locally Infeasible) — KKT Mismatch

**GitHub Issue:** [#1234](https://github.com/jeffreyhorn/nlp2mcp/issues/1234)
**Status:** OPEN — two fixes shipped:
- 2026-04-30 (`f53a4928`): Approach 1 — IR-level scalar-constant offset resolution
- 2026-05-02: Boundary `_fx_` equation deduplication — otpop now reaches MODEL STATUS 1 (Optimal). Objective still differs from the NLP because otpop is nonconvex and the MCP starts from a default warm-start (no replay of the otpop2 → otpop3 → otpop1 chain that warms the NLP).
**Severity:** Medium — Model compiles and now solves to a local KKT point; objective matching to the NLP requires a separate warm-start strategy.
**Date:** 2026-04-08
**Last Updated:** 2026-05-02
**Affected Models:** otpop

---

## Problem Summary

After fixing compilation errors (#1178) and MCP pairing (#1232), otpop now
compiles and PATH attempts to solve, but reports MODEL STATUS 5 (Locally
Infeasible) with 148 infeasible rows. The MCP objective (1487.96) differs
significantly from the NLP objective (4217.80), indicating incorrect KKT
formulation.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success
- **PATH solve**: MODEL STATUS 5 (Locally Infeasible), 148 INFEASIBLE rows
- **Objective**: MCP=1487.96, NLP=4217.80
- **Pipeline category**: model_infeasible
- **Previous fixes**: #1178 (compilation), #1232 (MCP pairing)

---

## Root Cause (Investigation Needed)

The model has several complex features that may cause KKT formulation issues:

1. **Scalar-constant lead/lag offset**: `pd(tt-l)` where `l /4/` is a scalar
   parameter. This produces `IndexOffset("tt", SymbolRef("l"))` which may not
   be differentiated correctly by the AD engine.

2. **Multi-solve model**: otpop has 3 solve statements (otpop2, otpop3, otpop1).
   nlp2mcp reformulates the last one (otpop1). Post-solve assignments from
   earlier solves may affect variable initialization.

3. **Time-reversal index**: `p(t + (card(t) - ord(t)))` in the objective
   equation `zdef`. While the compilation issue is fixed (#1178), the
   derivative through this complex offset may be incorrect.

4. **Subset domain mismatch**: Variable `d(tt)` is accessed over subset `t`
   in some equations and with lead/lag in conditioned equations. The Jacobian
   contributions may be incomplete.

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --quiet
gams /tmp/otpop_mcp.gms lo=0

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      5 Locally Infeasible
# **** REPORT SUMMARY :  0 NONOPT, 148 INFEASIBLE
# nlp2mcp_obj_val = 1487.957 (NLP: 4217.80)
```

---

## Potential Fix Approaches

1. **Resolve scalar-constant offsets at IR build time**: Convert `pd(tt-l)`
   → `pd(tt-4)` by evaluating scalar `l /4/` during parsing. This would make
   the Jacobian builder handle it as a standard integer offset.

2. **Debug stationarity equations**: Compare `stat_d`, `stat_p`, `stat_x`
   against hand-computed KKT conditions to identify missing or incorrect
   Jacobian terms.

3. **Verify time-reversal derivative**: Check that `∂zdef/∂x` correctly
   handles the `p(t + (card(t) - ord(t)))` index arithmetic.

---

## Files Involved

- `src/ad/constraint_jacobian.py` — Jacobian computation
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `src/ir/parser.py` — Scalar constant resolution
- `data/gamslib/raw/otpop.gms` — Original model (136 lines)

---

## Related Issues

- #1178 (FIXED) — Compilation errors from malformed index expressions
- #1232 (FIXED) — MCP pairing error (9 unmatched stat_d instances)
- #1224 — mine: ParamRef index offsets unsupported (similar pattern)

---

## Investigation 2026-04-30 — Approach 1 (scalar-constant offset resolution) shipped; deeper AD bugs remain

### What was investigated

Reproduced the original symptom (now manifests as `EXECERROR=1` instead
of MODEL STATUS 5; symptoms have shifted since the original report due
to upstream changes since 2026-04-08). Hand-derived the KKT system
to identify which terms the AD was missing.

### Root cause confirmed (Approach 1 from the Potential Fix Approaches list)

The model has `Scalar l /4/` and `adef(tt)..  ... pd(tt-l) ...`. The
parser produces:

```
VarRef('pd', (IndexOffset(base='tt', offset=Unary('-', SymbolRef('l')), circular=False),))
```

The AD engine treated `SymbolRef('l')` as opaque and never matched
`pd(tt-l)` to the wrt index when differentiating `adef(tt2)` w.r.t.
`pd(tt')`. As a result, `stat_pd(tt')` was emitted as just
`nu_pdef(tt') =E= 0` — missing the cross-term
`-con*d(tt'+3)*nu_adef(tt'+4)`.

### What was fixed

**`src/ir/scalar_offset_resolver.py`** (new) + **`src/ir/normalize.py`** (wiring):

A new IR-level normalization pass runs before AD/KKT. It walks every
`Expr` in equations / params / variables / objective and rewrites any
`IndexOffset.offset` expression that resolves to a numeric constant
(composed of `Const`, `Unary`, `Binary`, and `SymbolRef`s pointing to
scalar `ParameterDef`s with a single `()` value).

For otpop's `pd(tt-l)` with `l = 4`:
```
IndexOffset('tt', Unary('-', SymbolRef('l')))
  → IndexOffset('tt', Const(-4))
```

The AD then handles it as a standard integer offset. Verified by
inspecting the emitted `stat_pd(tt)`:

```
Pre-fix:
  stat_pd(tt).. nu_pdef(tt) =E= 0;

Post-fix:
  stat_pd(tt).. nu_pdef(tt)
                + ((((-1) * (con * d(tt+3))) * nu_adef(tt+4))
                   $(ord(tt) <= card(tt) - 4))$(tp(tt)) =E= 0;
```

The cross-term is now correctly attributed.

### Synthetic-attribute preservation (subtle implementation detail)

The parser attaches synthetic attributes (`domain`, `symbol_domain`,
`free_domain`, `rank`, `index_values`) to frozen-dataclass `Expr`
instances via `object.__setattr__`. These are read by downstream
normalization (`_merge_domains`) and AD code; reconstructing a
dataclass via `type(expr)(**fields)` would lose them and trigger
"Domain mismatch during normalization" errors.

The resolver:
1. Returns the SAME object identity when no rewrite is needed (so most
   Exprs pass through unchanged).
2. When a rewrite IS needed, copies the synthetic attributes onto the
   newly-constructed instance via `object.__setattr__`.

This was caught by the test suite (86 failures on the first
implementation that didn't preserve synthetic attrs); the fix is
simple but non-obvious and worth documenting here.

### Tests added

- `tests/unit/ir/test_scalar_offset_resolver.py` — 8 unit cases
  (SymbolRef resolution, Unary negation, Binary arithmetic, unresolvable
  cases, end-to-end equation-body rewrite, no-op cases, indexed-param
  rejection).
- `tests/integration/emit/test_otpop_scalar_offset_resolution.py` — 2
  integration cases (otpop's stat_pd has the cross-term, adef body
  emits correctly).

Quality gate clean: `make typecheck && make lint && make format &&
make test` (**4,687 passed**, 10 skipped, 1 xfailed).

### What's still left

otpop still aborts with `EXECERROR=1` due to additional AD bugs that
are NOT covered by this fix:

1. **Time-reversal index** (Approach 3 from the original list):
   `zdef.. z = v * sum(t, .365 * (xb(t) - x(t)) * p(t + (card(t) - ord(t))))`.
   The emitted `stat_x` has `(0)*p(1990)` coefficients, suggesting the
   AD evaluates the cross-coupled time-reversal derivative incorrectly.

2. **Missing constant terms in linearized eqs**: `dem(t).. d(t) + (0)*p(t) =E= 0`
   has the right LHS but PATH's Newton iterate diverges from the
   warm-start (default `.l = 0`).

3. **`stat_k = 1`, `stat_z = 1`**: PATH default-initializes `nu_*.l = 0`,
   but KKT requires `nu_kdef = 1` and `nu_zdef = 1` (gradient of
   maximization objective). PATH should iterate to find these but the
   Jacobian-step diverges because of the residuals from issues 1–2.

### How to proceed (next session)

**Start here.** Branch is `sprint25-fix-1234`; partial fix is committed
at `f53a4928`. Untracked `.claude/` is local-only; ignore.

**Step 0 — reproduce current state (5 min):**

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --quiet
gams /tmp/otpop_mcp.gms lo=0
# Expect: EXECERROR=1 (not MODEL STATUS 5 anymore — symptoms shifted post-#1232)
grep -E "stat_(x|d|z|k)" /tmp/otpop_mcp.gms | head -40
```

Eyeball the emitted `stat_x`, `stat_d`, `stat_z`, `stat_k`. The bug
markers from the 2026-04-30 investigation are `(0)*p(1990)` and
`(0)*p(t)` coefficients — these are where AD failed to resolve a
time-reversal index.

**Step 1 — confirm the suspected escape path for `card(t) - ord(t)`
(1–2 h):**

The new IR-level resolver (`src/ir/scalar_offset_resolver.py`) only
rewrites `IndexOffset.offset` whose leaves are `Const` /
`SymbolRef → ParameterDef`. `card(t)` and `ord(t)` are `Call` nodes,
so they pass through untouched.

The AD-side helper `_try_eval_offset` in
`src/ad/constraint_jacobian.py:133–202` *does* handle
`Call("card", ...)` and `Call("ord", ...)` — but only when the `ord`
argument resolves to a *concrete set element* via `pos_map` lookup
(`:171–192`). For `p(t + (card(t) - ord(t)))` inside
`sum(t, ...)`, the `t` here is the *symbolic sum index*, not yet
substituted, so `pos_map[base]` misses and `_try_eval_offset` returns
`None` (`:191–192`).

**Hypothesis to verify:** during AD differentiation of the `zdef` sum
body, the cross-attribution step iterates over concrete `t` values
but feeds the still-symbolic `card(t) - ord(t)` to
`_try_eval_offset` *before* substitution. Add a debug log at
`src/ad/constraint_jacobian.py:215` (the `evaluated = ...` line) for
otpop to confirm which path is taken.

If confirmed: the fix is to substitute the loop variable into the
offset expression before calling `_try_eval_offset`, OR to handle
`ord(<sum-index-bound-to-element>)` directly in `_try_eval_offset`.

**Step 2 — hand-derive `∂zdef/∂x(t')` and compare (2–3 h):**

`zdef.. z = v * sum(t, .365 * (xb(t) - x(t)) * p(t + (card(t) - ord(t))))`

By hand: for each `t' ∈ t`,
`∂zdef/∂x(t') = -.365 * v * p(t' + (card(t) - ord(t')))`.

For `t = (1990, 1991, ..., 2000)` (card=11), `t' = 1990` should map
to `p(2000)`, `t' = 1991` to `p(1999)`, etc. Print emitted
`stat_x(1990)` and check what it points to. If it shows `(0)*p(1990)`
the AD failed to resolve the offset; if it shows `*p(2000)` the AD
resolved correctly and the bug is elsewhere.

**Step 3 — pick the fix location (1 h):**

Two options, choose based on Step 1's findings:

- **(a) Extend the IR-level resolver** to evaluate `card(<set>)` to a
  numeric constant (it doesn't depend on the loop variable).
  `ord(<symbolic>)` cannot be resolved at IR-build time, so
  `card(t) - ord(t)` would still be partially symbolic. This narrows
  but does not fully close the gap.

- **(b) Add per-instance offset substitution in
  `constraint_jacobian.py`** so that when AD enumerates `t' ∈ t`, it
  substitutes `t → t'` into the offset expression *before* calling
  `_try_eval_offset`. This handles the general
  `f(loop_index, card, ord)` case.

Approach (b) is the more general fix and likely the right one;
approach (a) is a partial mitigation. Discuss with a maintainer
before committing to (b) since it touches AD-core enumeration logic.

**Step 4 — write tests first (1 h), then implement (1–2 h):**

- Unit test in `tests/unit/ad/test_constraint_jacobian.py`: a tiny
  `sum(t, x(t) * p(t + (card(t) - ord(t))))` IR fragment, assert the
  emitted Jacobian has the right `t → reversed-t` mapping.
- Integration test in
  `tests/integration/emit/test_otpop_*.py`: assert `stat_x(1990)`
  contains `*p(2000)` (or whatever the hand-derivation gives).
- Pipeline check: after fix, otpop should reach MODEL STATUS 1
  (Optimal) with `nlp2mcp_obj_val` matching the NLP objective
  (≈ 4217.80). If it still mismatches, items 2 & 3 from the original
  "What's still left" list are the next layer.

**Step 5 — quality gate & PR:**

```bash
make typecheck && make lint && make format && make test
```

Reference `#1234`, link this issue file, summarize hand-derivation
in the PR body.

### Files Involved (next phase)

- `src/ad/constraint_jacobian.py:133–249` — `_try_eval_offset` and
  `_resolve_idx`; primary edit site for Approach (b)
- `src/ad/derivative_rules.py:1847` — `_diff_sum`; verify that the
  sum-body differentiation passes the right context to the offset
  resolver
- `src/ir/scalar_offset_resolver.py` — extend if going with Approach (a)

### Estimated effort

**Total 6–10 h** (Step 1 confirmation + Step 2 derivation + Step 3
choice + Step 4 implement/test). Similar shape to other AD-bug
investigations in this codebase.

---

## Investigation 2026-05-02 — diagnosis was wrong; real bug was a `_fx_` boundary conflict; otpop now reaches MODEL STATUS 1

### What the prior plan got wrong

The 2026-04-30 plan blamed `card(t) - ord(t)` AD evaluation, citing
`(0)*p(...)` coefficients in the listing as evidence. Re-reading the
GAMS `.lst` more carefully: those are **GAMS's normal display of
bilinear terms**, where the *other* factor (e.g., `nu_zdef.l = 0`,
`nu_kdef.l = 0` at the default warm-start) evaluates to zero. They
are not zero coefficients in the symbolic equation — the emitted
`.gms` shows `0.365 * v * p(tt+(card(tt)-ord(tt))) * nu_zdef`, which
is correct.

The **actual abort** was reported one section earlier in the listing:

```
**** MCP pair x_fx_1974.nu_x_fx_1974 has unmatched equation
     x_fx_1974
```

### Real root cause (boundary `_fx_` conflict)

otpop's sets overlap at one element:

```
th(tt) 'historical years' / 1965*1974 /;   * x.fx(th) = x74 = 29.4
t(tt)  'model horizon'    / 1974*1990 /;   * stationarity domain for x
```

For the boundary year **1974** (in BOTH `th` and `t`), the emitter
correctly synthesizes an MCP-paired `_fx_` equation:

```
x_fx_1974.. x("1974") - 29.4 =E= 0;
... x_fx_1974.nu_x_fx_1974, ...   // in the Model statement
```

But at the same time, the `Variable Bounds` section blindly emitted
ALL `var.fx_map` entries as `.fx` lines (Issue #1021's fix —
originally added so spatequ's empty `comp_*` equations had a fixed
paired variable):

```
x.fx('1974') = 29.4;
```

The `.fx` line caused GAMS's `holdFixed=true` pass to **remove the
column** `x("1974")`, leaving the `x_fx_1974` row with no variables.
Its paired multiplier `nu_x_fx_1974` was therefore unmatched →
EXECERROR=1.

Sibling years 1965–1973 didn't trigger this because they're outside
`t`, so their `_fx_` equations are *suppressed* by
`_compute_suppressed_fx_equations` (`src/emit/emit_gams.py:855`) and
fall through to the standard `.fx` + `nu_*.fx = 0` fallback. The
overlap on 1974 is unique.

### What was fixed

**`src/emit/emit_gams.py:1609`** — the `fx_map` re-emission loop in
the variable-bounds pass now skips entries whose `_fx_` equation is
in the MCP (i.e., the equation is in `kkt.model_ir.equalities` AND
NOT in `suppressed_fx`). When the equation will fix the variable
through complementarity, we must NOT also `.fx` the column.

```python
if var_def.fx_map:
    _equalities_set = set(kkt.model_ir.equalities)
    for indices, fx_val in sorted(var_def.fx_map.items()):
        eq_name = _fx_eq_name(var_name, indices)
        if eq_name in _equalities_set and eq_name not in suppressed_fx:
            continue
        ...
```

This preserves Issue #1021's behavior for the unit-test scenarios
(those construct `ModelIR` without calling `normalize_model`, so
`equalities` is empty and the `.fx` is still emitted) and for spatequ
(diagonal entries fall into `suppressed_fx`, so `.fx` is still
emitted). It changes behavior only for the boundary case otpop hit.

### Tests added

- `tests/unit/emit/test_fx_suppression.py::TestSuppressedFxInEmission::test_active_fx_equation_skips_redundant_dot_fx`
  — minimal `ModelIR` with stationarity domain that INCLUDES the
  fx_map index; asserts the `_fx_` equation is paired and the
  redundant `.fx` is NOT emitted.
- `tests/integration/emit/test_otpop_scalar_offset_resolution.py::test_otpop_x_fx_1974_no_redundant_dot_fx`
  — asserts `x_fx_1974` is paired, `x.fx('1974')` is absent, and
  siblings 1965–1973 still get `.fx` (since their equations are
  suppressed).

Quality gate clean: `make typecheck && make lint && make format
&& make test` → **4,689 passed**, 10 skipped, 1 xfailed.

### End-to-end result

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --quiet
gams /tmp/otpop_mcp.gms lo=0
```

- **SOLVER STATUS**: 1 Normal Completion
- **MODEL STATUS**: 1 Optimal
- **REPORT SUMMARY**: 0 NONOPT
- `nlp2mcp_obj_val = 2307.072`

The MCP solves to a local KKT point. The objective differs from the
NLP's `pi = 4217.80` because **otpop is nonconvex** (bilinear
`x*p` in `kdef` and `zdef`) and the original NLP gets warm-started
by a chain of solves (`otpop2 → otpop3 → otpop1`) before the final
solve. The MCP starts from default `.l = 0` initialization and
converges to a different stationary point. Closing this gap is a
warm-start / multi-solve replay concern, not a KKT-correctness one,
and is out of scope for this fix.

### What's still left for `#1234`

Closing the objective gap to `pi ≈ 4217.80`:

1. **Replay-style warm start**: emit a pre-solve block that runs
   `otpop2`, then `otpop3`, then sets `kdef.m = 1; zdef.m = 1;`
   before the MCP solve, mirroring the original GAMS file's
   sequence. This already exists in skeleton form (`_emit_nlp_presolve`
   at `src/emit/emit_gams.py:906`); check whether it activates for
   otpop and what it emits.
2. **Multi-solve initialization**: alternatively, capture the final
   `.l` values from `otpop3` (the warm-up maximize that runs in the
   original) and inject them as `var.l(...) = ...` lines in the MCP.
3. **Validate against NLP solution**: once the MCP converges to
   `pi ≈ 4217.80`, add a pipeline `cmp_obj` assertion in the gamslib
   regression suite.

These are 2–4 h of work each and are independent of the KKT
correctness fix shipped here. They can ship in a follow-up PR or
tracked as a separate issue.
