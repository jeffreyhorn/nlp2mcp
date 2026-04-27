# lmp2: Dynamic-subset SET assignments inside multi-solve loops are not extracted into MCP pre-solve

**GitHub Issue:** [#1315](https://github.com/jeffreyhorn/nlp2mcp/issues/1315)
**Status:** OPEN
**Severity:** Medium-High — blocks lmp2 compile (Error 66) even after #1281's Parameter-redefinition fix
**Discovered:** Sprint 25 Day 9 (PR #1314, post-#1281 verification)
**Affected Models:** lmp2 (observed); other multi-solve models with dynamic-subset assignments inside the solve-loop body may share the same shape

---

## Problem Summary

`emit_pre_solve_param_assignments` extracts PARAMETER assignments from the body of solve-containing loops (issue #1101/#1102), but it does NOT extract SET assignments — even though dynamic subsets like `m(mm)` are computed inside the same loop body and required for the MCP to compile.

For lmp2, the source has:

```gams
Set
   m(mm) 'constraints'
   n(nn) 'variables'
   ...

loop(c,
   m(mm)   = ord(mm) <= cases(c,'m');
   n(nn)   = ord(nn) <= cases(c,'n');
   ...
   solve lmp2 minimizing obj using nlp;
);
```

The MCP emitter:
- Auto-populates `n(nn) = yes;` (line 30 of `lmp2_mcp.gms`) because `n` is referenced in stat_x's domain guard.
- Does NOT populate `m(mm) = ...` even though `m` is used in `comp_Constraints(m)`, `stat_x`'s `sum(m, ...)`, and the model's equation domain — leaving `m` empty at solve time.

Result: GAMS rejects with `Error 66 equation stat_x.. symbol "m" has no values assigned`.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_mcp.gms --skip-convexity-check --quiet
gams /tmp/lmp2_mcp.gms action=c lo=2

# Output:
#   159  Solve mcp_model using MCP;
# ****                           $66,256
# ****  66  Use of a symbol that has not been defined or assigned
# **** 256  Error(s) in analyzing solve statement.
# **** The following MCP errors were detected in model mcp_model:
# ****  66 equation stat_x.. symbol "m" has no values assigned
```

Confirm the missing assignment by inspecting the MCP:

```bash
grep -nE "^m\(mm\)\s*=|^n\(nn\)\s*=" /tmp/lmp2_mcp.gms
# 30:n(nn) = yes;
# (no m(mm) line)
```

## Likely Root Cause

Two independent code paths handle dynamic-subset assignments:

1. **`src/emit/emit_gams.py`** auto-populates dynamic subsets that appear in stationarity domain guards (`n(nn)` is in `stat_x(nn)$(n(nn))`). This is what produces the `n(nn) = yes;` line. It does NOT cover subsets referenced only in equation bodies/domains (like `m`).
2. **`src/emit/original_symbols.py::emit_pre_solve_param_assignments`** extracts assignments from solve-loop bodies. Per its `_ASSIGN_TYPES = {"assign", "conditional_assign_general"}` filter and `if name not in param_names: continue` check at line 3308, it ONLY considers parameter assignments — set assignments are silently skipped.

The fix needs to extend either:
- Path (1) to cover dynamic subsets used in equation domains (not just stationarity guards), or
- Path (2) to also extract dynamic-subset assignments when the subset appears in any equation in the MCP.

Approach (2) is more aligned with the existing pre-solve-extraction flow. The change: in `emit_pre_solve_param_assignments`, expand the `name not in param_names` filter to also accept set names whose set is dynamic (has a parent domain) and is referenced by a model equation.

## Candidate Fix Approaches

1. **Extend pre-solve extraction to include dynamic-subset assignments.** Add a new `set_names_to_extract` set computed from `model_ir.sets` (those with non-empty `domain` and used in any equation domain), and accept assignments whose LHS matches one of those names. Then emit the assignment text verbatim with the loop-index substituted (same mechanism as the existing parameter path).
2. **Extend the auto-populate path** to scan equation domains (not just stationarity guards) for dynamic-subset references and emit `subset(parent) = yes;` for the full parent set.

Approach (1) preserves the source semantics more faithfully (the actual conditional `m(mm) = ord(mm) <= cases(c, 'm')` propagates with the loop-index substituted to a specific case). Approach (2) gives a wider, possibly over-eager subset (`m = full mm`).

Recommend (1) for correctness; (2) is the fallback if (1) turns out to be too invasive.

## Expected Impact

Direct: lmp2's compile error 66 disappears; lmp2 either solves (matching #1281's expected progression from `path_solve_terminated` → some actual solve result) or hits its next latent bug.

Same shape may also affect other multi-solve loop models (need a corpus audit alongside the fix).

## Files

- `src/emit/original_symbols.py::emit_pre_solve_param_assignments` (likely fix site for approach 1).
- `src/emit/emit_gams.py` (auto-populate path; alternative fix site for approach 2).
- `data/gamslib/raw/lmp2.gms` — primary repro corpus.

## Related

- `#1281` (resolved Sprint 25 Day 9): the redundant `Parameter A/b/cc` declarations were the SECOND blocker on lmp2; this is the THIRD.
- `#1243` (lmp2: runtime division by zero in stat_y) — distinct downstream issue.

## Status

Open. Filed during Sprint 25 Day 9 (PR #1314). Targeting Sprint 26 carryforward.
