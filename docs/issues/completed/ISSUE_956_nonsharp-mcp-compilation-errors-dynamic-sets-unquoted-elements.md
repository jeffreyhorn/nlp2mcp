# nonsharp: 37 GAMS Compilation Errors in MCP Output

**GitHub Issue:** [#956](https://github.com/jeffreyhorn/nlp2mcp/issues/956)
**Status:** FIXED (all 37 compilation errors resolved by prior fixes)
**Severity:** High — Model parses and translates but MCP output had 37 compilation errors
**Date:** 2026-02-27
**Fixed:** 2026-04-01 (verified — no code changes needed)
**Model:** nonsharp (GAMSlib, nonsharp separation sequencing via Benders decomposition)

---

## Problem Summary

The nonsharp MCP output had **37 compilation errors** across four categories:

1. **Bug A**: Unquoted set elements in `.l` initialization (18 errors)
2. **Bug B**: Dynamic subset `k(km)` used as variable domain (2 errors)
3. **Bug C**: Dynamic subset domains lost in equation translation (2+ errors)
4. **Bug D**: Undefined parameter `nfeas` in conditional `.fx` (1 error)
5. **Bug E**: Cascading errors ($257, $141)

---

## Resolution

All 37 compilation errors were resolved by accumulated fixes across multiple PRs without any nonsharp-specific changes:

- **Bug A** (unquoted elements): Fixed by quoting improvements in the emitter
- **Bug B** (dynamic subset domain): Fixed by dynamic subset handling and `_emit_dynamic_subset_defaults`
- **Bug C** (subset-filtered sum domains): Fixed by expression emission improvements
- **Bug D** (loop-body parameter): Fixed by `_collect_loop_referenced_params` (PR #1183) and `emit_pre_solve_param_assignments`

**Result:** nonsharp compiles cleanly (0 errors) and solves to MODEL STATUS 1 Optimal (SOLVER STATUS 1). Objective mismatch with reference is expected — the original model uses Benders decomposition with dynamic iterations, and the MCP captures a single iteration snapshot.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/nonsharp.gms -o /tmp/nonsharp_mcp.gms --skip-convexity-check
(cd /tmp && gams nonsharp_mcp.gms lo=2)
# 0 errors, MODEL STATUS 1 Optimal
```
