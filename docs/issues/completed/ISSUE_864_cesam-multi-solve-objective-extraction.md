# Cesam: Multi-Solve Model Objective Extraction Failure

**GitHub Issue:** [#864](https://github.com/jeffreyhorn/nlp2mcp/issues/864)
**Status:** RESOLVED
**Severity:** Medium — Model parses but objective not found (model_no_objective_def)
**Date:** 2026-02-24
**Resolved:** 2026-02-25
**Affected Models:** cesam

---

## Problem Summary

The cesam model parses successfully but fails validation with `model_no_objective_def`. The
model contains multiple solve statements including both NLP and MCP solves, and the parser
unconditionally overwrites `self.model.objective` for every solve statement — including MCP
solves which have no objective by design.

---

## Resolution

**Root cause:** In `_handle_solve`, the `else` branch unconditionally set
`self.model.objective = None` when no objective variable was found (MCP/CNS solves). This
cleared the valid NLP objective set by an earlier solve statement.

**Fix:** Changed the `else` branch to only set `objective = None` when no objective has been
previously set (`elif self.model.objective is None`). This preserves the NLP objective from
earlier solve statements when a subsequent MCP solve has no objective.

```python
# Before:
else:
    self.model.objective = None

# After:
elif self.model.objective is None:
    self.model.objective = None
```

**Result:** cesam now correctly extracts `dentropy` as the objective variable from the first
NLP solve and preserves it through the subsequent MCP and second NLP solves.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ir/parser.py` | Changed `_handle_solve` to not overwrite non-None objective |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.7 documents the original parse blocker (sameas)
- **Issue #807** (completed): MCP solve without objective — related but different
