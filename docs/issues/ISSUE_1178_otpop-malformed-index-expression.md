# otpop: Malformed Index Expressions in Stationarity ($145/$148)

**GitHub Issue:** [#1178](https://github.com/jeffreyhorn/nlp2mcp/issues/1178)
**Model:** otpop (GAMSlib SEQ=47)
**Error category:** `path_syntax_error` ($145, $148, $8, $37)
**Previous blocker:** $171 domain violation (fixed in PR #1176 via domain widening)

## Description

After fixing $171 via domain widening, otpop still has compilation errors from malformed index expressions in stationarity equations:

1. `stat_d(tt)`: `pd(1966-l)` — literal year `1966` with subtraction of variable `l`. The original GAMS has `pd(tt-l)` inside a sum over `n` where `l = ord(n)-1`, but after concrete element substitution, it became `pd(1966-l)` which is nonsensical.

2. `stat_x(tt)`: `p(1974+(card(t)-ord(t)))` — complex arithmetic expression used as an index. The original has `p(t + (card(t) - ord(t)))` which uses GAMS lead/lag arithmetic, but after substitution the `t` became `1974` (a literal element).

## Reproduction

```bash
python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --skip-convexity-check
(cd /tmp && gams otpop_mcp.gms lo=2)
# $145/$148/$8/$37 errors on stat_d and stat_x
```

## Root Cause

The stationarity builder's element-to-set substitution incorrectly handles cases where:
- A parameter index involves arithmetic on the set variable (e.g., `tt-l` where `l` is `ord(n)-1`)
- A variable index uses complex lead/lag expressions (e.g., `t + (card(t) - ord(t))`)

After substituting concrete elements, the arithmetic expressions become malformed because literal year values replace symbolic set variables.

## Fix Approach

The stationarity builder needs to:
1. Detect when a concrete element is used with arithmetic offset in a ParamRef/VarRef index
2. Preserve the original symbolic expression structure (e.g., keep `tt-l` rather than substituting `1966-l`)
3. Handle complex lead/lag patterns like `t + (card(t) - ord(t))` by preserving the symbolic form
