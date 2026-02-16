# KKT Assembly: Unreferenced Variables Get Stationarity Equations (GAMS Error 69/483)

**GitHub Issue:** [#742](https://github.com/jeffreyhorn/nlp2mcp/issues/742)
**Status:** Fixed
**Severity:** Medium -- Generates invalid MCP pairs for unused variables
**Discovered:** 2026-02-16 (Sprint 19, after fixing Issues #738 and #739)
**Affected Models:** ganges, gangesx (and any model declaring variables not used in equations)

---

## Problem Summary

The ganges and gangesx MCP output produces GAMS Error 69 ("Dimension of variable is unknown") and Error 483 ("Mapped variables have to appear in the model") for variables `dumshr` and `dumtg`. These are scalar variables that are declared in the original model but never referenced in any equation. The KKT assembler generates stationarity equations (`stat_dumshr`, `stat_dumtg`) for them and pairs them in the MCP model declaration, but since the variables don't appear in any equation body, GAMS cannot determine their dimension or validate the MCP pairing.

---

## Reproduction

**Model:** `ganges` (also affects `gangesx`)

**Commands:**
```bash
# Generate MCP using full KKT pipeline
python -c "
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system

model = parse_model_file('data/gamslib/raw/ganges.gms')
normalize_model(model)
gradient = compute_objective_gradient(model)
J_eq, J_ineq = compute_constraint_jacobian(model)
kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
gams_code = emit_gams_mcp(kkt)
open('/tmp/ganges_mcp.gms', 'w').write(gams_code)
"

# GAMS compile check
gams /tmp/ganges_mcp.gms a=c
```

**GAMS compilation output (relevant errors):**
```
 69 dumshr dimension of variable unknown
 69 dumtg dimension of variable unknown
 69  Dimension of variable is unknown
483 dumshr no ref to var in equ.var
483 dumtg no ref to var in equ.var
483  Mapped variables have to appear in the model
256  Error(s) in analyzing solve statement.
```

**Generated MCP output (relevant lines):**
```gams
Variables
    ...
    dumtg
    dumshr
    ...
;

Equations
    ...
    stat_dumshr
    stat_dumtg
    ...
;

stat_dumshr.. <all-zero stationarity body> =E= 0;
stat_dumtg.. <all-zero stationarity body> =E= 0;

Model mcp_model /
    ...
    stat_dumshr.dumshr,
    stat_dumtg.dumtg,
    ...
/;
```

The stationarity equation bodies are entirely zero (every derivative is 0) because these variables don't appear in any model equation.

---

## Root Cause

In the original ganges model (`data/gamslib/raw/ganges.gms`), `dumshr` and `dumtg` are declared as variables but never referenced in any equation:

```gams
Variable
   dumtg       'sum of square deviations                  (absolute)'  * Line 535
   dumshr      'sum of square deviations                 (on shares)'  * Line 537
```

These are "dummy" or reporting variables that exist in the variable declaration block but are not part of the optimization model's constraint system. They may be used in post-solve reporting or were leftover from model development.

### Why the KKT assembler includes them

The `build_stationarity_equations()` function in `src/kkt/stationarity.py` iterates over ALL variables in `kkt.model_ir.variables` (except the objective variable) and generates a stationarity equation for each one. It does not check whether the variable actually appears in any equation body.

The stationarity equation for an unreferenced variable `x` is:
```
∂L/∂x = ∂f/∂x + Σ_j [∂h_j/∂x · ν_j] + Σ_k [∂g_k/∂x · λ_k] - π^L + π^U = 0
```

Since `x` doesn't appear in `f`, `h_j`, or `g_k`, all partial derivatives are zero, producing the trivial equation `0 = 0`. GAMS cannot match this with the variable in the MCP because the variable has no equation references.

---

## Fix Approach

### Option A: Filter unreferenced variables from KKT system (Recommended)

Before building stationarity equations, identify variables that don't appear in any equation body (objective, equalities, or inequalities). Exclude them from:
1. Stationarity equation generation
2. Variable declarations (or at least from the MCP model pairing)
3. Bound multiplier generation

Detection: Walk all equation bodies and collect referenced variable names. Any variable in `model_ir.variables` not in this set is unreferenced.

**Complexity:** Low-medium. Requires an expression walker to collect VarRef names from equation bodies.

### Option B: Exclude from MCP pairing only

Keep the stationarity equations but exclude the `stat_x.x` pair from the `Model` declaration. This avoids the Error 483 but leaves dead equations in the output.

**Complexity:** Low but leaves unnecessary code in output.

### Option C: Fix variables to zero and exclude from MCP

For unreferenced variables, emit `.fx = 0;` and exclude from the MCP pairing. This is mathematically equivalent to removing them entirely.

**Complexity:** Low.

### Recommended approach

Option A is the cleanest solution. It avoids generating unnecessary equations and variables, producing a smaller and more correct MCP output. The variable reference collector could also be useful for other purposes (e.g., dead code elimination).

---

## Affected Variables in ganges/gangesx

| Variable | Domain | Description | Used in equations? |
|----------|--------|-------------|-------------------|
| `dumshr` | scalar | Sum of square deviations (shares) | No |
| `dumtg` | scalar | Sum of square deviations (absolute) | No |

Note: Other models may have different unreferenced variables. The fix should be general, not model-specific.

---

## Fix Details

**Approach:** Option A — Filter unreferenced variables from KKT system before stationarity equation generation.

**Implementation:** In `build_stationarity_equations()` in `src/kkt/stationarity.py`:

1. Added helper `_collect_referenced_variable_names(model_ir)` that walks all equation bodies (LHS, RHS, and conditions) plus the objective variable name and objective expression. Collects all `VarRef` names into a set.

2. In `build_stationarity_equations()`, after grouping variable instances into `var_groups`, filter out any variable whose name is not in the referenced set. The filter only applies when `kkt.model_ir.equations` is non-empty (models with no equations, such as simple variable-objective tests, skip the filter to avoid incorrectly removing the objective variable).

3. This eliminates stationarity equations, bound multipliers, and MCP pairings for unreferenced variables like `dumshr` and `dumtg`.

**Result:** All instances of GAMS Error 69 and Error 483 eliminated for ganges/gangesx. Unreferenced variables no longer produce trivial `0 = 0` stationarity equations or invalid MCP pairings.

**Quality Gate:** All checks pass (typecheck, lint, format, 3369 tests passed, 10 skipped, 1 xfailed).

---

## Relevant Files

- `src/kkt/stationarity.py` — Fix location: `_collect_referenced_variable_names()` helper and filter in `build_stationarity_equations()`
- `src/kkt/assemble.py` — `assemble_kkt_system()` — orchestrates KKT assembly
- `src/emit/templates.py` — `emit_variables()`, `emit_equations()` — emits declarations
- `src/emit/model.py` — `emit_model_mcp()` — emits MCP model pairs
- `data/gamslib/raw/ganges.gms` — Original model (lines 535, 537 for variable declarations)
