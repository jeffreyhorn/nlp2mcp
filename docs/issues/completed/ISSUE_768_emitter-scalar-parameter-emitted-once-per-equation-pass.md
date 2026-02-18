# Emitter: Scalar Parameter Emitted Once Per Equation Pass (Triplication)

**GitHub Issue:** [#768](https://github.com/jeffreyhorn/nlp2mcp/issues/768)
**Status:** FIXED — PR #772
**Severity:** Low — MCP is still syntactically valid and solves correctly; duplicate assignments are redundant but not harmful
**Date:** 2026-02-17
**Affected Models:** harker

---

## Problem Summary

When the original NLP model reassigns a scalar parameter (e.g., `tm = 1/3`) after its
initial declaration, the emitter reproduces the assignment once per equation pass rather
than once total. This produces duplicate (or triplicate) assignment statements in the
generated MCP file.

---

## Example

### harker — `harker_mcp.gms:45-47`

Original model assigns `tm` once:
```gams
Scalar tm /1.0/;
...
tm = 1 / 3;
```

Generated MCP contains:
```gams
Scalars
    pm /1.0/
    tm /1.0/
    ...
;

tm = 1 / 3;
tm = 1 / 3;
tm = 1 / 3;
```

The assignment `tm = 1 / 3;` appears three times — once for each equation in the model
that the emitter iterates over when assembling the parameter assignment section.

---

## Root Cause

In `emit_gams.py`, scalar parameter reassignment statements (non-indexed assignments
that appear in the model body, outside equation definitions) are emitted inside or
alongside a loop over equations or variables. Each loop iteration re-emits the same
assignments, resulting in one copy per loop iteration.

The emission of scalar parameter body assignments should be collected into a set
(deduplicated) before writing to the output file.

---

## Reproduction

```bash
# Generate MCP for harker
python -m src.cli data/gamslib/raw/harker.gms -o /tmp/harker_mcp.gms

# Check for duplicate assignments:
grep "tm = 1" /tmp/harker_mcp.gms
# Output shows three identical lines
```

---

## Generated MCP (Relevant Section)

```gams
* harker_mcp.gms lines ~45-47 (current — wrong):
tm = 1 / 3;
tm = 1 / 3;
tm = 1 / 3;

* Correct:
tm = 1 / 3;
```

---

## Suggested Fix

**Option A (Preferred): Deduplicate before emitting**

Collect all scalar parameter body assignments into a list/set, then deduplicate before
writing:

```python
seen_assignments = set()
for assignment in scalar_assignments:
    text = render_assignment(assignment)
    if text not in seen_assignments:
        seen_assignments.add(text)
        emit(text)
```

**Option B: Move assignment emission outside the per-equation loop**

Refactor the emitter so that scalar body assignments are gathered in a single pass
(not inside the equation iteration loop) and written once after all equations are
processed.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/emit/emit_gams.py` | Scalar parameter assignment emission — locate the loop causing duplication |
| `data/gamslib/mcp/harker_mcp.gms` | Generated — shows the bug (do not edit directly) |

---

## Related Issues

- **ISSUE_767**: Per-instance bound multipliers not index-guarded — separate emitter bug identified in same PR review
- Identified during PR #762 review
