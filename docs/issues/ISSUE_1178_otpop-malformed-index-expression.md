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

## Fix Approach

These are deep issues in the stationarity builder's handling of IndexOffset/arithmetic indices:
1. The `pd(tt-l)` pattern uses a scalar constant `l /4/` as a lead/lag offset — the stationarity builder must preserve the symbolic `tt-l` form rather than substituting a concrete year
2. The `p(t + (card(t) - ord(t)))` pattern is a "time reversal" that needs special handling
3. Both require preserving the symbolic structure through differentiation, which is architecturally complex

This is related to the broader issue of how the AD pipeline handles non-trivial index arithmetic in differentiated expressions.
