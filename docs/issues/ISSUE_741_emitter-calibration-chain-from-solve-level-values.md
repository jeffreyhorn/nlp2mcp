# MCP Emission: Calibration Parameters Depending on Solve-Level Values (GAMS Error 66)

**GitHub Issue:** [#741](https://github.com/jeffreyhorn/nlp2mcp/issues/741)
**Status:** Open
**Severity:** High -- Blocks ganges/gangesx MCP from compiling; affects any model with post-solve calibration
**Discovered:** 2026-02-16 (Sprint 19, after fixing Issues #738 and #739)
**Affected Models:** ganges, gangesx (and likely other CGE models with calibration blocks)

---

## Problem Summary

The ganges and gangesx MCP output produces 15+ instances of GAMS Error 66 ("The symbol shown has not been defined or assigned") for parameters that are calibrated from `.l` (variable level) values after an initial `solve` statement in the original model. The parser's `_contains_variable_reference()` filter drops all assignments containing `VarRef` nodes, which means the entire calibration chain — including CES/CET share parameters, scale parameters, and baseline snapshots — is missing from the emitted MCP.

This is the root cause behind the residual compilation errors after Issues #738 (Error 141) and #739 (Error 187) were fixed.

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

**GAMS compilation output (relevant Error 66 instances):**
```
equation firstq.. symbol "deltaq" has no values assigned
equation prodq.. symbol "aq" has no values assigned
equation stat_ax.. symbol "aid" has no values assigned
equation stat_ax.. symbol "as" has no values assigned
equation stat_ax.. symbol "deltav" has no values assigned
equation stat_ax.. symbol "deltax" has no values assigned
equation stat_ax.. symbol "dg" has no values assigned
equation stat_exscale.. symbol "aex" has no values assigned
equation stat_invtot.. symbol "adst" has no values assigned
equation stat_lw.. symbol "av" has no values assigned
equation stat_n.. symbol "az" has no values assigned
equation stat_n.. symbol "deltaz" has no values assigned
equation stat_nd.. symbol "an" has no values assigned
equation stat_nd.. symbol "deltan" has no values assigned
equation stat_nm.. symbol "pnm00" has no values assigned
equation stat_pq.. symbol "cg" has no values assigned
equation stat_w.. symbol "dcpi" has no values assigned
```

---

## Root Cause

In the original ganges model (`data/gamslib/raw/ganges.gms`), an extensive calibration block (lines ~597-750) computes dozens of parameters from `.l` (level) values that result from an initial `solve` statement. The parser's `_contains_variable_reference()` method (in `src/ir/parser.py`) intentionally drops all assignments containing `VarRef` nodes because `.l` values are solution-dependent and don't exist before the MCP solve.

### Affected Parameters (17 total)

All assignments reference `.l` values and are therefore dropped by the parser:

**CES/CET share parameters (delta)** — calibrated via two-step pattern:
| Parameter | Assignment (line) | `.l` references |
|-----------|-------------------|-----------------|
| `deltaq(sc)` | Line 680 | `x.l`, `m.l`, `px.l`, `pm.l` |
| `deltax(i)` | Line 659 | `z.l`, `g.l`, `pz.l`, `pg.l` |
| `deltaz(i)` | Line 649 | `v.l`, `n.l`, `pv.l`, `pn.l` |
| `deltan(i)` | Line 641 | `nd.l`, `nm.l`, `pnd.l`, `pnm.l` |
| `deltav(i)` | Line 614 | `s.l`, `lw.l`, `ps.l`, `w.l` |

**CES/CET scale parameters (a)** — depend on deltas AND `.l` values:
| Parameter | Assignment (line) | `.l` references |
|-----------|-------------------|-----------------|
| `aq(sc)` | Line 682 | `q.l`, `x.l`, `m.l` |
| `az(i)` | Line 652 | `z.l`, `v.l`, `n.l` |
| `as(i)` | Line 602 | `s.l`, `ls.l` |
| `av(i)` | Line 617 | `v.l`, `s.l`, `lw.l` |
| `an(i)` | Line 644 | `n.l`, `nd.l`, `nm.l` |
| `aex(i)` | Line 746 | `ex.l`, `pq.l` |

**Baseline snapshots and other calibration parameters:**
| Parameter | Assignment (line) | `.l` references |
|-----------|-------------------|-----------------|
| `adst(i)` | Line 741 | `dst.l` |
| `dg(i)` | Line 658 | `g.l` |
| `pnm00(i)` | Line 628 | `pnm.l` |
| `cg(i)` | Line 747 | `pc.l` |
| `dcpi(r)` | Line 731 | `cpi.l` |
| `aid(i)` | Line 740 | `id.l` |

### Why these parameters matter

These parameters appear in the model's production and trade equations. Without them, the CES/CET production functions (which define the nested structure of the CGE model) have zero share and scale parameters, making the stationarity equations mathematically degenerate.

### Parser filter location

In `src/ir/parser.py`, the `_handle_assign()` method (line ~3230) calls `_contains_variable_reference()` (line ~4556) which returns `True` for any expression containing a `VarRef` node. When `True`, the assignment is skipped entirely:

```python
# In _handle_assign():
if self._contains_variable_reference(expr_tree):
    # Skip assignment - it references variable .l values
    return
```

---

## Fix Approach

### Option A: Capture `.l` values as parameter initial data (Recommended)

Modify the parser to handle assignments where `.l` references can be resolved to known initial values:

1. For variables with explicit `.l` initialization (from `x.l = value;` or `x.l(i) = value;`), store the initial level values in `VariableDef.l` / `VariableDef.l_map`
2. When encountering a parameter assignment with `.l` references, check if all referenced `.l` values have known initial values
3. If yes, evaluate the expression statically and store the computed values in `ParameterDef.values`
4. If no, skip the assignment (current behavior)

**Complexity:** High — requires expression evaluation with `.l` substitution. Many calibration assignments involve complex expressions (`**`, `sum`, conditional `$`).

### Option B: Emit `.l` references as variable.l in GAMS

Instead of dropping `.l` assignments, emit them as-is using GAMS variable `.l` attribute syntax:

```gams
dg(i) = g.l(i);
deltax(i) = (z.l(i)/g.l(i))**(1/sigmax(i))*pz.l(i)/pg.l(i);
```

This requires:
1. Extending the IR to capture VarRef `.l` attribute access
2. Extending `expr_to_gams()` to emit `var_name.l(indices)` syntax
3. Ensuring the original model's initial solve is completed before the MCP section (or providing separate initialization)

**Complexity:** Medium — requires IR and emitter changes but no expression evaluation.

### Option C: Pre-compute calibration values externally

Run the original model through GAMS to the point just after calibration, then extract parameter values from the GDX file and inject them as data into the MCP.

**Complexity:** Low code changes but adds external dependency on running the original model first.

### Option D: Require user-provided calibration data

Document that models with post-solve calibration need manual parameter data files, and provide a mechanism to merge external data with generated MCP.

**Complexity:** Low but shifts burden to users.

### Recommended approach

Option B is the most general and maintainable solution. It preserves the original calibration logic and works with any model structure. The key insight is that in the MCP formulation, the calibration can happen before the `solve` statement using the same `.l` initialization that the original model uses.

---

## Relevant Files

- `src/ir/parser.py` — `_handle_assign()` (line ~3230), `_contains_variable_reference()` (line ~4556)
- `src/emit/original_symbols.py` — `emit_computed_parameter_assignments()`
- `src/emit/expr_to_gams.py` — Would need extension for `.l` attribute emission
- `src/ir/ast.py` — `VarRef` class (currently has no `.l` attribute field)
- `src/ir/symbols.py` — `VariableDef` (has `l`, `l_map` for initial level values)
- `data/gamslib/raw/ganges.gms` — Original model (lines 597-750 for calibration block)
