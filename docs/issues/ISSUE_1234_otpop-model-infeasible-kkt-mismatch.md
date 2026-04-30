# otpop: MODEL STATUS 5 (Locally Infeasible) — KKT Mismatch

**GitHub Issue:** [#1234](https://github.com/jeffreyhorn/nlp2mcp/issues/1234)
**Status:** OPEN — partial fix shipped 2026-04-30 (Approach 1 from "Potential Fix Approaches" — scalar-constant offset resolution). Remaining AD bugs (time-reversal, missing terms in `stat_x`/`stat_d`) still cause `EXECERROR=1`.
**Severity:** Medium — Model compiles and PATH solves, but KKT system is infeasible
**Date:** 2026-04-08
**Last Updated:** 2026-04-30
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

### Required next steps before another fix attempt

1. Hand-derive `∂zdef/∂x(t')` and compare against the AD's emitted
   `stat_x(t')` body. Identify why the time-reversal contribution
   shows `(0)*p(...)` instead of the correct `0.365*v*(...)*1` form.

2. Investigate whether the `card(t) - ord(t)` index arithmetic
   produces an `IndexOffset` with a non-Const offset that escapes
   the new resolver (it would, since `card(t)` and `ord(t)` aren't
   scalar parameters — they're GAMS built-in functions).

3. Consider a more general "evaluate at compile time" pass for
   `card(t)` / `ord(t)` constant arithmetic.

Estimated remaining effort: **6–10 hours** (similar shape to other
AD-bug investigations in this codebase).
