# danwolfe: MCP Compilation Errors ($140/$126/$148/$149)

**GitHub Issue:** [#1182](https://github.com/jeffreyhorn/nlp2mcp/issues/1182)
**Model:** danwolfe (GAMSlib, Dantzig-Wolfe decomposition)
**Error category:** `path_syntax_error` ($140, $126, $135, $148, $149)
**Previous blocker:** Parse error (fixed in PR #1181 — added grid computing functions)

## Description

After fixing the parse error, danwolfe translates successfully but the generated MCP has 8 compilation errors. The errors are in the pre-solve loop setup code, not in the stationarity equations.

## Errors

```
line 71: kdem(k) = uniform(50,150);         — $140 Unknown symbol (kdem not declared)
line 73: bal(k,i)$ord(i) = inum = kdem(k);  — $140 Unknown symbol
line 76: kdem(k) = sum(sum, i $ bal(k,i) > 0); — $126/$148/$149/$135 (malformed sum)
```

## Root Cause

1. **$140 Unknown symbol `kdem`**: The parameter `kdem(k)` is declared in the original model inside a loop-body data setup section. The MCP emitter emits the loop code but may not emit the parameter declaration for `kdem`.

2. **Malformed `sum(sum, ...)`**: The original GAMS has `kdem(k) = sum(i$bal(k,i), 1)` but the emitter produced `sum(sum, i $ bal(k,i) > 0)` — the aggregation function name `sum` is being used as the first argument, and the condition/body structure is wrong.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/danwolfe.gms -o /tmp/danwolfe_mcp.gms --skip-convexity-check
(cd /tmp && gams danwolfe_mcp.gms lo=2)
# 8 ERROR(S)
```

## Fix Approach

1. Investigate why `kdem(k)` is not declared as a parameter in the MCP output
2. Fix the malformed `sum(sum, ...)` expression — likely an IR builder issue where the `sum` aggregation is being parsed/emitted incorrectly
3. Check if the loop-body parameter assignments are being correctly transferred from the original model to the MCP
