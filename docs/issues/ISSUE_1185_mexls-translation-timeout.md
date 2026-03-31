# mexls: Translation Timeout (Large LP)

**GitHub Issue:** [#1185](https://github.com/jeffreyhorn/nlp2mcp/issues/1185)
**Model:** mexls (GAMSlib SEQ=210, "Mexico Steel - Large Static")
**Error category:** `translation_timeout`
**Previous blocker:** Universal set `*` not found (fixed in PR #1184)

## Description

After fixing the universal set `*` error, mexls progresses to the differentiation phase but does not complete translation within 300s. This is a large LP model with many multi-dimensional variables and equations, creating a combinatorial explosion during Jacobian computation even with the LP basic simplification fast path.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/mexls.gms -o /tmp/mexls_mcp.gms --skip-convexity-check
# Runs for 14+ minutes without completing
```

## Root Cause

Same class as other LP translation timeout models (iswnm #931, nebrazil #932, lop #1169). The symbolic differentiation generates too many variable instance x equation instance pairs. The LP basic simplification fast path (PR #1172) reduces overhead but is insufficient for this model's size.

## Related Issues

- #940: Universal set `*` error (fixed)
- #931, #932, #1169: Same LP translation timeout class
