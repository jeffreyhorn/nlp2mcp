# lmp2: Set `m` not extracted into MCP pre-solve, residual after #1320 divisor-guard

**GitHub Issue:** [#1323](https://github.com/jeffreyhorn/nlp2mcp/issues/1323)
**Status:** RESOLVED — fixed alongside #1315 in PR (this branch)
**Severity:** High — `path_syntax_error` (Error 66) prevented PATH from being invoked at all
**Date:** 2026-04-29
**Fixed:** 2026-04-29
**Affected Models:** lmp2

---

## Problem Summary

This issue documented the same root cause as #1315 — the post-#1320 reproduction cleanly isolated that PR #1321 fixed gtm but lmp2 was unaffected because lmp2's blocker was structural (set-extraction), not divisor-guard. Both issues are addressed by a single fix in this PR.

lmp2's source defines a dynamic subset `m(mm)` whose membership is set inside a multi-solve `loop(...)` body. The MCP emitter referenced `m(mm)` in stationarity equations but did not extract the `m(mm) = ord(mm) <= cases(c, 'm')` set assignment into the MCP pre-solve. Result: GAMS Error 66 on `equation stat_x.. symbol "m" has no values assigned`.

## Resolution Summary

The fix described in [ISSUE_1315](./ISSUE_1315_lmp2-multi-solve-set-assignment-not-extracted.md) directly addresses this issue. Both #1315 and #1323 are about the same code path; the single fix closes both.

### Code changes

See ISSUE_1315 for full details. Summary:

1. `emit_pre_solve_param_assignments` now extracts dynamic-subset SET assignments alongside parameter assignments.
2. A new helper `collect_pre_solve_referenced_params` surfaces params referenced via the extracted assignments so their Table values are emitted (`cases` for lmp2).
3. `emit_subset_value_assignments` now correctly force-quotes literal element names that collide with set names (e.g., `cases('c1','m')` not `cases('c1',m)`).

### Verification

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_mcp.gms --quiet
grep "^m(mm)\|^n(nn)" /tmp/lmp2_mcp.gms
# Output:
#   n(nn) = yes;
#   m(mm) = ord(mm) <= cases('c1','m') ;
#   n(nn) = ord(nn) <= cases('c1','n') ;
```

GAMS no longer aborts with Error 66. Acceptance criterion 1 of this issue is met:
> 1. `gams lmp2_mcp.gms` compiles cleanly (no Error 66 on symbol `m`).

### Residual blocker (out of scope, filed as #1327)

Acceptance criterion 2 ("lmp2 progresses past `path_syntax_error`") is partially met: lmp2 now hits a *different* compile-time error (#1327 — Error 187, "Assigned set used as domain") on the KKT-generated `lam_Constraints(m)` and `comp_Constraints(m)`. The KKT system uses the dynamic-subset's body domain (`m`) instead of the declaration's parent domain (`mm`). This is a multiplier-domain issue that surfaces only because #1315/#1323 are now fixed — it was previously masked by Error 66.

The corrected emission for `lam_Constraints` and `comp_Constraints` should be:
```gams
Positive Variables lam_Constraints(mm);
Equations comp_Constraints(mm);
lam_Constraints.fx(mm)$(not m(mm)) = 0;
comp_Constraints(mm)$(m(mm)).. ...
```

### Tests added

Same as ISSUE_1315.

## Related

- **#1281** (resolved) — Parameter redeclaration, fixed in PR #1314
- **#1315** (resolved jointly with this issue) — Multi-solve dynamic-subset set assignment not extracted
- **#1243** (resolved earlier in this PR's branch) — Next-in-line residual after #1315/#1323
- **#1327** (NEW — filed during this fix) — lam_Constraints / comp_Constraints declared over dynamic subset, surfaces post-#1315/#1323 as Error 187
- **#810** — lmp2 multi-solve loop extraction (parent class issue)
- **#1320** (closed by PR #1321) — Sprint 25 fix that addressed gtm but NOT lmp2
