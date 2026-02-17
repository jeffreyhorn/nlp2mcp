# Pipeline: MCP Objective Comparison Guesses Variable Name Instead of Using NLP Objective Variable

**GitHub Issue:** [#769](https://github.com/jeffreyhorn/nlp2mcp/issues/769)
**Status:** FIXED
**Severity:** Medium — causes false `compare_objective_mismatch` results for models whose NLP objective variable is not in the hardcoded guess list; also may produce false matches if an unrelated variable happens to match a guessed name
**Date:** 2026-02-17
**Affected Models:** house (confirmed); any model whose NLP objective variable is not in the guess list

---

## Problem Summary

The MCP pipeline compares the NLP optimal objective value against the MCP solution to verify
correctness. MCP problems have no `**** OBJECTIVE VALUE` line in the GAMS listing (because
MCP has no objective function). The pipeline falls back to
`extract_objective_from_variables()` in `scripts/gamslib/test_solve.py`, which tries a
hardcoded list of common variable names to find the objective:

```python
obj_var_names = [
    "obj", "z", "objective", "cost", "profit",
    "total_cost", "totalcost", "total", "f", "fobj",
]
```

If the NLP objective variable is not in this list, the function returns `None` and the
pipeline records no MCP objective — or worse, picks up a stale or incorrect value from a
prior run in `gamslib_status.json`.

---

## Concrete Example: house model

The house NLP maximizes `ta` (total area). The MCP currently solves correctly:
- Solver Status 1 Normal Completion
- Model Status 1 Optimal  
- `ta.l = 4500.0` (matches NLP optimum)

But `ta` is not in the hardcoded guess list. The pipeline records:

```json
"mcp_objective": 45.5305,
"objective_match": false,
"comparison_result": "compare_objective_mismatch"
```

This is a **false mismatch** — the model is actually correct.

---

## Root Cause

`extract_objective_from_variables()` in `scripts/gamslib/test_solve.py` (lines 260–309)
uses a hardcoded guess list of common objective variable names. It has no connection to
the actual NLP objective variable known from the model IR or the NLP solve.

The NLP objective variable name is available in the `convexity` section of
`gamslib_status.json` (captured during the original GAMS solve via the listing file),
but is not currently stored there explicitly.

---

## Proposed Fix

**Option A (Preferred): Emit `Display <obj_var>;` in the MCP file**

The emitter knows the NLP objective variable name from the model IR (`model_ir.objective`).
Add a `Display <obj_var>;` statement after the `Solve` in the emitted MCP file:

```gams
Solve mcp_model using MCP;
Display ta;   * NLP objective variable for pipeline comparison
```

The `**** OBJECTIVE VALUE` pattern won't appear, but the listing will contain:
```
---- VAR ta    ...    4500.0000    ...
```

The pipeline's `extract_objective_from_variables()` can then search for the known variable
name in the listing. To make it unambiguous, the MCP file can emit a scalar assignment
after the solve with a fixed well-known name:

```gams
Scalar nlp_obj_val;
nlp_obj_val = ta;
Display nlp_obj_val;
```

This produces a `----    NNN PARAMETER nlp_obj_val          =     4500.000` line in the listing (not `**** OBJECTIVE VALUE`).
The pipeline's `extract_objective_from_variables()` should be updated to include
`nlp_obj_val` in its search list, or better, the `objective_pattern` regex should be
extended to also match `---- PARAMETER nlp_obj_val` output.

**Option B: Store objective variable name during NLP solve**

During `verify_convexity.py`, capture the objective variable name from the NLP listing
(the line immediately before `**** OBJECTIVE VALUE`) and store it in
`gamslib_status.json` as `convexity.objective_variable`. Then in `test_solve.py`,
read this field and search the MCP listing for `---- VAR <objective_variable>`.

**Option C: Extend the guess list**

Low-effort partial fix: add more common GAMS objective variable names to the list
(e.g., `ta`, `obj_val`, `value`, `revenue`, `welfare`, `util`, `utility`).
Not recommended as a primary fix — the list will never be complete.

---

## Reproduction

```bash
# Generate and run house MCP
python -m src.cli data/gamslib/raw/house.gms -o /tmp/house_mcp.gms
gams /tmp/house_mcp.gms lo=3 o=/tmp/house_mcp.lst

# Check: ta = 4500 in listing (correct)
grep "VAR ta" /tmp/house_mcp.lst

# Check pipeline status: reports mismatch (wrong)
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f:
    d = json.load(f)
models = d['models']
for m in models:
    if m.get('model_id') == 'house':
        print(json.dumps(m.get('solution_comparison', {}), indent=2))
"
```

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `scripts/gamslib/test_solve.py` | `extract_objective_from_variables()` lines 260–309; MCP solve pipeline |
| `scripts/gamslib/verify_convexity.py` | NLP solve — could capture objective variable name here |
| `src/emit/emit_gams.py` | MCP emitter — could add `Display <obj_var>;` or scalar assignment |
| `data/gamslib/gamslib_status.json` | Pipeline database — `house` entry shows false mismatch |

---

## Fix Applied

**Implemented Option A** — emitter + pipeline sentinel approach.

### `src/emit/emit_gams.py`
After the `Solve mcp_model using MCP;` statement, emit a fixed-name sentinel scalar
using the NLP objective variable name from `obj_info.objvar`:

```gams
Scalar nlp_obj_val;
nlp_obj_val = ta.l;
Display nlp_obj_val;
```

GAMS produces `----    NNN PARAMETER nlp_obj_val          =     4500.000` in the listing.

### `scripts/gamslib/test_solve.py`
Updated `extract_objective_from_variables()` to check for the sentinel **first** before
falling back to the heuristic variable-name scan. Added primary regex:

```python
r"----\s+\d*\s*PARAMETER\s+nlp_obj_val\s+=\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
```

### Golden files updated
`tests/golden/simple_nlp_mcp.gms`, `indexed_balance_mcp.gms`, `scalar_nlp_mcp.gms`
all updated to include the new sentinel block.

### Verification
- house model: pipeline now extracts `nlp_obj_val = 4500.0` (was incorrectly 45.5305)
- 3475 tests pass, zero regressions

---

## Related Issues

- Identified during Day 7 house model investigation
- house model MCP actually solves correctly (ta=4500 = NLP optimum) despite pipeline reporting mismatch
