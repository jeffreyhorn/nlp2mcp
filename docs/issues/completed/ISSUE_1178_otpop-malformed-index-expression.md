# otpop: Malformed Index Expressions in Stationarity ($145/$148)

**GitHub Issue:** [#1178](https://github.com/jeffreyhorn/nlp2mcp/issues/1178)
**Model:** otpop (GAMSlib SEQ=47)
**Error category:** `path_syntax_error` ($145, $148, $8, $37)
**Previous blocker:** $171 domain violation (fixed in PR #1176 via domain widening)

## Description

After fixing $171 via domain widening, otpop still has compilation errors from malformed index expressions in stationarity equations:

1. `stat_d(tt)`: `pd(1966-l)` — literal year `1966` with subtraction of scalar `l` (`l /4/`, investment lag). The original GAMS has `pd(tt-l)` which is a lead/lag offset by the scalar constant `l`, but after concrete element substitution `tt` became `1966`, producing `pd(1966-l)` which GAMS cannot parse as a valid index.

2. `stat_x(tt)`: `p(1974+(card(t)-ord(t)))` — complex arithmetic expression used as an index. The original has `p(t + (card(t) - ord(t)))` which uses GAMS lead/lag arithmetic, but after substitution the `t` became `1974` (a literal element).

## Reproduction

```bash
python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --skip-convexity-check
(cd /tmp && gams otpop_mcp.gms lo=2)
# $145/$148/$8/$37 errors on stat_d and stat_x
```

## Root Cause

The stationarity builder's element-to-set substitution incorrectly handles cases where:
- A parameter index involves lead/lag with a scalar constant (e.g., `pd(tt-l)` where `l /4/` is a scalar)
- A variable index uses complex lead/lag expressions (e.g., `p(t + (card(t) - ord(t)))`)

After substituting concrete elements, the arithmetic expressions become malformed because literal year values replace symbolic set variables.

## Investigation (2026-03-30)

The malformed expressions come from two equations in the original model:
- `adef(tt)$tp(tt).. as(tt) =e= as(tt-1) + con*d(tt-1)*(pd(tt-l)-ph);` — `pd(tt-l)` where `l /4/` is a scalar constant (investment lag)
- `zdef.. z =e= v*sum(t, .365*(xb(t) - x(t))*p(t + (card(t) - ord(t))));` — `p(t + (card(t) - ord(t)))` is a "reverse time" access pattern

Both involve index arithmetic that the stationarity builder's concrete element substitution cannot handle. After substitution, `tt` becomes `1966` (a literal year), producing `pd(1966-l)` and `p(1974+(card(t)-ord(t)))`.

## Fix (Sprint 24)

**Status: PARTIALLY FIXED** — compilation errors resolved, model now reaches solve stage.

Three changes fixed the `p(t + (card(t) - ord(t)))` compilation error ($154):

1. **`_apply_index_substitution` in `derivative_rules.py`**: Added `IndexOffset` case to recurse into offset expressions during sum index substitution. Previously IndexOffset was passed through unchanged, so `SymbolRef("t")` inside the offset wasn't substituted.

2. **`_replace_indices_in_expr` in `stationarity.py`**: Added `ord()` argument remapping for concrete elements and subset set names. When `ord(t)` appears after sum collapse where `t` is a subset of `tt` (the equation domain), it's remapped to `ord(tt)` so the set is controlled.

3. **IndexOffset offset processing**: VarRef/ParamRef `has_linear_offset` paths now recurse `_replace_indices_in_expr` into the offset expression, fixing concrete elements inside `card()`/`ord()`.

**Result:** otpop compiles without errors. EXECERROR=9 (MCP pairing issues for `stat_d`) is a separate pre-existing problem — the `pd(tt-l)` pattern still needs work.

**Remaining:** The `pd(tt-l)` pattern (scalar constant `l /4/` as lead/lag offset) still causes MCP pairing issues but no longer causes compilation errors.
