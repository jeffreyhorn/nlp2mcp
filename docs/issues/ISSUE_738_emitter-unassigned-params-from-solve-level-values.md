# MCP Emission: Unassigned Parameters from Solve-Level Calibration (GAMS Error 141)

**GitHub Issue:** [#738](https://github.com/jeffreyhorn/nlp2mcp/issues/738)
**Status:** Open
**Severity:** Medium -- Generated MCP files fail GAMS compilation for affected models
**Discovered:** 2026-02-15 (Sprint 19, during Issue #730 investigation)
**Affected Models:** ganges, gangesx (and likely other models with post-solve calibration)

---

## Problem Summary

The ganges and gangesx MCP output produces 5 instances of GAMS Error 141 ("Symbol declared but no values have been assigned") for parameters that are calibrated from `.l` (level) values after a `solve` statement in the original model. The emitter outputs self-referencing assignment statements like `deltaq(sc) = deltaq(sc) / (1 + deltaq(sc))` without the preceding initial assignment that computes the value from `.l` attributes.

This is a pre-existing emitter issue, not related to stationarity or KKT assembly.

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
 255  deltaq(sc) = deltaq(sc) / (1 + deltaq(sc));
****                    $141
 256  deltax(i) = deltax(i) / (1 + deltax(i));
****                   $141
 257  deltaz(i) = deltaz(i) / (1 + deltaz(i));
****                   $141
 258  deltan(i) = deltan(i) / (1 + deltan(i));
****                   $141
 260  deltav(i) = deltav(i) / (1 + deltav(i));
****                   $141
```

Note: `deltas(i) = deltas(i) / (1 + deltas(i))` on line 259 does NOT trigger Error 141, likely because its initial assignment does not depend on `.l` values (or its dependency chain is different).

---

## Root Cause

In the original ganges model (`data/gamslib/raw/ganges.gms`), these parameters are calibrated in a two-step pattern that depends on `.l` (level) values from a prior `solve` statement:

```gams
* Step 1: Initial assignment using .l values (e.g., line 680)
deltaq(sc) = (x.l(sc)/m.l(sc))**(1/sigmaq(sc))*px.l(sc)/pm.l(sc);

* Step 2: Self-referencing normalization (e.g., line 681)
deltaq(sc) = deltaq(sc)/(1 + deltaq(sc));
```

The full set of affected parameters and their initial assignments:

| Parameter | Initial Assignment (Step 1) | Self-reference (Step 2) |
|-----------|---------------------------|------------------------|
| `deltaq(sc)` | `(x.l(sc)/m.l(sc))**(1/sigmaq(sc))*px.l(sc)/pm.l(sc)` (line 680) | `deltaq(sc)/(1 + deltaq(sc))` (line 681) |
| `deltax(i)` | `(z.l(i)/g.l(i))**(1/sigmax(i))*pz.l(i)/pg.l(i)` (line 659) | `deltax(i)/(1 + deltax(i))` (line 660) |
| `deltaz(i)` | `(v.l(i)/n.l(i))**(1/sigmaz(i))*pv.l(i)/pn.l(i)` (line 649) | `deltaz(i)/(1 + deltaz(i))` (line 650) |
| `deltan(i)` | `(nd.l(i)/nm.l(i))**(1/sigman(i))*pnd.l(i)/pnm.l(i)` (line 641) | `deltan(i)/(1 + deltan(i))` (line 642) |
| `deltav(i)` | `(s.l(i)/lw.l(i))**(1/sigmav(i))*ps.l(i)/sum(r$ri(r,i), w.l(r))` (line 614) | `deltav(i)/(1 + deltav(i))` (line 615) |

The emitter outputs Step 2 but not Step 1 because Step 1 uses `.l` (variable level) attributes. The `.l` values come from a `solve` statement earlier in the model, but in the MCP reformulation there is no `solve` statement at that point — the model is being restructured into KKT conditions.

### Why the emitter drops Step 1

The emitter likely skips or fails to process assignments containing `.l` attributes because:
1. `.l` attributes reference solution values that don't exist before the MCP solve
2. The parser/IR may not fully capture `.l` attribute assignments
3. The emitter may intentionally skip post-solve calibration code

However, Step 2 is still emitted because it's a plain parameter self-assignment without `.l` references. The result is that Step 2 references parameters that have never been assigned values.

---

## Fix Approach

Several possible approaches:

### Option A: Emit both steps, using variable initial values for `.l`
Replace `.l` references with the variable's initial/starting value (`.l` at model initialization, before any solve). This would produce correct calibration values if the original model initializes variables before the calibration block.

### Option B: Skip Step 2 when Step 1 is skipped
If the initial assignment (Step 1) is not emitted, also suppress the self-referencing normalization (Step 2). The parameter would retain its default value (0), which would be incorrect but wouldn't cause a compilation error. The solve would likely fail at runtime instead.

### Option C: Compute calibration values externally
Pre-compute the calibrated parameter values by running the original model's calibration block, then emit the final values as data statements.

### Option D: Detect and warn
Mark these parameters as requiring post-solve calibration and emit a warning comment in the generated GAMS, along with `$onImplicitAssign` to suppress the error.

### Recommended approach
Option A is mathematically correct if variable starting values are available in the IR. Option D is the pragmatic fallback if `.l` values are not accessible.

---

## Relevant Files

- `src/emit/emit_gams.py` — GAMS code emission (where assignments are emitted)
- `src/emit/model.py` — Model-level emission logic
- `src/ir/model_ir.py` — IR representation (check if `.l` assignments are captured)
- `data/gamslib/raw/ganges.gms` — Original model (lines 597-686 for calibration block)
- `data/gamslib/raw/gangesx.gms` — Same structure as ganges
