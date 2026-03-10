# trnspwl: `Model / all /` includes MIP equations — MCP reformulation scope not filtered by solve statement

**GitHub Issue:** [#1033](https://github.com/jeffreyhorn/nlp2mcp/issues/1033)
**Status:** OPEN
**Severity:** High — produces incorrect MCP formulation with discrete variables (GAMS Error 65)
**Date:** 2026-03-10
**Affected Models:** trnspwl (GAMSlib SEQ=351), potentially any multi-model file

---

## Problem Summary

The trnspwl model defines **three separate GAMS models** in one file:

1. `Model transport / all /;` — pure NLP with `cost`, `supply`, `demand` (lines 96–107)
2. `Model trnsdiscA / supply, demand, defsos1, defsos2, defsos3, defobjdisc /;` — MIP with SOS2 (line 165)
3. `Model trnsdiscB / supply, demand, defx, defsqrt, defseg, defgs, defobjdisc /;` — MIP with Binary (line 218)

The first solve is `solve transport using nlp minimizing z;` (line 119). The NLP model `transport` only uses continuous variables (`x`, `z`) and three equations (`cost`, `supply`, `demand`).

However, our pipeline generates an MCP formulation that includes **all** equations and variables from the entire file — including SOS2 variable `xs`, Binary variable `gs`, and equations from formulations A and B (`defsos1`, `defsos2`, `defsos3`, `defx`, `defsqrt`, `defseg`, `defgs`, `defobjdisc`). This causes GAMS Error 65 ("discrete variable not allowed") because MCP cannot handle discrete variables.

---

## Root Cause

Two related issues in the pipeline:

### Issue 1: `/ all /` scope not captured at declaration point

In GAMS, `Model transport / all /;` means "all equations **declared up to this point**". At line 107, only three equations exist: `cost`, `supply`, `demand`. The formulation A/B equations (`defsos1`, `defx`, etc.) are declared later and should NOT be part of `transport`.

The parser (`src/ir/parser.py` `_handle_model_all()`) sets `model.model_uses_all = True` but does not snapshot which equations exist at that point. Since equations continue to be added to `model.equations` as the file is parsed, by the end of parsing `model.equations` contains all 11+ equations from all three formulations.

### Issue 2: MCP pipeline does not filter by model membership

The downstream pipeline (`normalize_model` → `partition_constraints` → `assemble_kkt_system` → `emit_gams_mcp`) processes **all** equations in `model_ir.equations` unconditionally. It never consults `model_equations`, `model_uses_all`, or `model_name` to determine which equations belong to the solved model.

The relevant fields exist in `ModelIR`:
```python
declared_models: set[str]           # {"transport", "trnsdisca", "trnsdiscb"}
model_equations: list[str]          # [] (empty because "/ all /")
model_uses_all: bool                # True
model_name: str | None              # "transport" (from solve statement)
```

But these are only used for validation, never for filtering.

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/trnspwl.gms')

# Shows all equations, not just the 3 in the NLP model:
print(list(ir.equations.keys()))
# ['cost', 'supply', 'demand', 'defsos1', 'defsos2', 'defsos3',
#  'defobjdisc', 'defx', 'defsqrt', 'defseg', 'defgs']

# The MCP output includes discrete variables:
# gs (Binary), xs (SOS2) → GAMS Error 65
```

Full pipeline:
```bash
python -m src.cli data/gamslib/raw/trnspwl.gms -o /tmp/trnspwl_mcp.gms
gams /tmp/trnspwl_mcp.gms
# Error 65: discrete variable "gs" not allowed
# Error 65: discrete variable "xs" not allowed
```

---

## Expected Behavior

The MCP reformulation should only include equations and variables from the **solved NLP model** (`transport`):

- **Equations:** `cost`, `supply`, `demand`
- **Variables:** `x(i,j)` (Positive), `z` (Free)
- **No discrete variables** — `xs` (SOS2) and `gs` (Binary) belong to models `trnsdiscA`/`trnsdiscB`

The generated MCP should be a straightforward KKT system for:
```
min  z = sum((i,j), c(i,j)*sqrt(x(i,j)))
s.t. sum(j, x(i,j)) <= a(i)    ∀i
     sum(i, x(i,j)) >= b(j)    ∀j
     x(i,j) >= 0
```

---

## Proposed Fix

### Step 1: Snapshot equation set at `Model / all /` declaration

In `_handle_model_all()`, when `model_uses_all = True`, also record the set of equation names that exist at that point:

```python
def _handle_model_all(self, ...):
    self.model.model_uses_all = True
    self.model.model_equations = list(self.model.equations.keys())  # snapshot
```

This way `model_equations` is populated even for `/ all /` models — it captures the equations declared up to that point.

### Step 2: Filter equations in the MCP pipeline

In `normalize_model()` or `partition_constraints()`, if `model_equations` is non-empty, only include equations that are in that list. All other equations (and their associated variables) should be excluded from the KKT system.

### Step 3: Filter variables by equation membership

Variables that only appear in excluded equations should also be excluded from the MCP formulation. This prevents discrete variables (`gs`, `xs`) from being included when their equations (`defx`, `defsos1`, etc.) are excluded.

---

## Impact

- **trnspwl** would go from Error 65 (cannot solve) to a valid MCP formulation
- Any other multi-model GAMS file where later equations/variables should not be in the NLP model would also benefit
- This is a correctness issue: the current MCP output is mathematically wrong (wrong KKT system for the wrong optimization problem)

---

## Affected Files

| File | Change |
|------|--------|
| `src/ir/parser.py` | Snapshot equation names at `Model / all /` declaration point |
| `src/ir/model_ir.py` | Possibly extend `model_equations` semantics or add `model_all_snapshot` |
| `src/ir/normalize.py` | Filter equations by model membership before partitioning |
| `src/kkt/partition.py` | Alternative location for equation filtering |

---

## Related

- Issue #949 — Previous trnspwl fixes (subset expansion, element quoting) — now in `docs/issues/completed/`
- The original trnspwl.gms uses the NLP solution from `transport` as a starting point, then solves MIP discretizations, then restarts the NLP from the MIP solution
