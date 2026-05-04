# cesam2: Translate regression — `Failed to evaluate condition SetMembershipTest(ICOEFF, ...)`

**GitHub Issue:** [#1344](https://github.com/jeffreyhorn/nlp2mcp/issues/1344)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (translate stage)
**Date:** 2026-05-03
**Affected Models:** cesam2 (SEQ=53, NLP, Cross Entropy SAM Estimation)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`cesam2` translated successfully at the Sprint 25 Day 0 baseline. On the current branch the translate stage now fails (categorized as `unsup_expression_type`) with this UserWarning surfacing as a hard error:

```
src/ad/index_mapping.py:556: UserWarning: Failed to evaluate condition for equation 'asameq':
  Failed to evaluate condition SetMembershipTest(ICOEFF, (SymbolRef(ii), SymbolRef(jj)))
  with indices ('ACT', 'ACT'): Set membership for 'ICOEFF' cannot be evaluated statically
  because the set has no concrete members at compile time. Including unevaluable
  instances by default.
```

This is the same pattern that gates the `mine` model out of translate (baseline `internal_error`; tracked in `DESIGN_SMALL_PRIORITIES.md`) — except that `cesam2` was *not* affected at Day 0 and now is.

---

## Resolution

**The issue's hypothesis was incorrect.** The `Failed to evaluate condition SetMembershipTest(...)` line in stderr is a `UserWarning` (soft signal) — it has always been informational and never raised. The translate stage continues past it, "Including unevaluable instances by default," and emits the corresponding `$nonzero(ii,jj)` guards into the MCP. So the SetMembershipTest path was never the cause of the failure.

The actual cause of the recorded `nlp2mcp_translate.status = "failure"` (with `category = "unsup_expression_type"`) was a separate hard error at AD/emit time. `expr_to_gams` reached a `case _:` fallback for `IndexOffset` when an `IndexOffset` appeared as a *direct index* of a `SetMembershipTest` (e.g. `nh(i+1)` synthesized from offset equation domains), raising `Unknown expression type: IndexOffset`. That error message did contain "unknown expression type", which is what the categorizer matched as `unsup_expression_type`.

That fix landed earlier today in:

- `12548337` — Fix #1338 #1339 #1340 #1341: handle IndexOffset in SetMembershipTest indices
- `7dd94cd7` — Fix #1342 #1343: accept subset/alias keys in up_expr_map / lo_expr_map

The pipeline run that recorded the failure (translate_date 2026-05-03T05:37:10) preceded those commits. After re-running the pipeline on the current branch:

```
Translate Results:
  Success: 1 (100.0%)
  Failure: 0
```

`data/gamslib/gamslib_status.json` now records `cesam2.nlp2mcp_translate.status = "success"`.

### Regression test

Added `tests/integration/emit/test_cesam2_translate_setmembership.py::test_cesam2_translate_completes`. It runs the parse → normalize → AD → emit pipeline on `data/gamslib/raw/cesam2.gms` and asserts:

1. The emit returns a non-empty MCP without raising.
2. The dynamic-subset guard `$nonzero(...)` survives into the MCP body — confirming the SetMembershipTest soft path is preserved end-to-end.

Test passes locally (130s).

### Acceptance Criteria status

- ✅ `cesam2` translate exits success — confirmed via direct CLI invocation and `run_full_test.py --model cesam2 --only-translate`.
- ✅ The `SetMembershipTest` condition path remains soft (warning, not error) — verified by the new integration test, which lets the warning fire but asserts the emit completes.
- ✅ Integration test added asserting cesam2 translate completes.

---

## Reproduce (post-fix)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/cesam2.gms -o /tmp/cesam2_mcp.gms
# → ✓ Generated MCP: /tmp/cesam2_mcp.gms (exit 0)
```

```bash
.venv/bin/python -m pytest tests/integration/emit/test_cesam2_translate_setmembership.py -v
# → 1 passed
```

---

## Related

- `mine` (#1224 / DESIGN_SMALL_PRIORITIES.md) — same SetMembershipTest family. Distinct: still gated out at translate at Day 0 and beyond, separate root cause.
- #1338, #1339, #1340, #1341 — IndexOffset-in-SetMembershipTest fix (commit `12548337`).
- #1342, #1343 — subset/alias keys in `up_expr_map`/`lo_expr_map` (commit `7dd94cd7`).
- #1041 (open) — older cesam2 MCP-pair issue (post-translate); distinct from this.
- #817, #858, #869, #1022, #1025 (closed) — historical cesam2 fixes.
