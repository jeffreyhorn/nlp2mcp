# decomp: Multi-Solve Benders Decomposition Unsupported

**GitHub Issue:** [#1222](https://github.com/jeffreyhorn/nlp2mcp/issues/1222)
**Status:** OPEN — Structural limitation (multi-solve model)
**Severity:** Medium — Model requires iterative solve loop, incompatible with single MCP
**Date:** 2026-04-07
**Last Updated:** 2026-04-07
**Affected Models:** decomp

---

## Problem Summary

The decomp model (GAMSlib SEQ=164, "Decomposition Principle - Animated") uses
Benders decomposition with multiple iterative `solve` statements in a loop. The
nlp2mcp tool reformulates a single NLP solve into an MCP, but decomp has 4+
solve statements and references equation marginals (`.m` attribute) between
iterations. The emitter produces invalid GAMS like `ctank = - tbal m ;` instead
of `ctank = -tbal.m;` because the equation marginal attribute is not properly
handled.

---

## Root Cause

1. **Multi-solve structure**: decomp solves `sub` (LP) and `master` (LP)
   iteratively in a loop, using marginal values from one solve to update
   parameters for the next.

2. **Equation marginal references**: Lines like `ctank = -tbal.m;` and
   `rep(ss,'t-pi') = -tbal.m;` reference the marginal (dual value) of
   equation `tbal` from the most recent solve. The emitter doesn't handle
   `.m` attribute access on equations.

3. **Fundamental incompatibility**: The MCP reformulation replaces the
   original model's equations with KKT stationarity conditions. The
   original equations (`tbal`, `convex`) don't exist in the MCP, so their
   marginals (`.m`) are undefined.

---

## Reproduction

```bash
# Translate
.venv/bin/python -m src.cli data/gamslib/raw/decomp.gms -o /tmp/decomp_mcp.gms --quiet

# Compile — Error 140 (Unknown symbol) on "tbal m"
gams /tmp/decomp_mcp.gms lo=0

# Error output:
# ctank = - tbal m ;
#                $140,409
# **** 140  Unknown symbol
```

---

## GAMS Errors

- **Error 140**: Unknown symbol — `tbal` is emitted as a bare identifier, not
  recognized as an equation name
- **Error 409**: Unrecognizable item — the `m` after `tbal` is not parsed as
  an attribute accessor

---

## Potential Fix Approaches

1. **Detect and skip multi-solve models**: If a model has multiple `solve`
   statements, warn and skip MCP reformulation. This is the simplest approach.

2. **Support equation marginal emission**: Emit `.m` references properly
   as `equation_name.m`. However, in the MCP context, the original equation
   doesn't exist, so the marginal is the multiplier variable instead. Would
   need to map `tbal.m` → `nu_tbal.l` in post-solve assignments.

3. **Support iterative solve loops**: Full support for Benders-style
   decomposition. Very complex — requires loop unrolling or multi-stage
   reformulation. Not recommended for near-term.

---

## Files Involved

- `src/emit/emit_gams.py` — Pre-solve assignment emission
- `src/ir/parser.py` — Loop/solve statement handling
- `data/gamslib/raw/decomp.gms` — Original model (138 lines)
