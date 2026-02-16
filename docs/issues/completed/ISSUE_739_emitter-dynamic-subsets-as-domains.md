# MCP Emission: Dynamic/Assigned Subsets Used as Declaration Domains (GAMS Error 187)

**GitHub Issue:** [#739](https://github.com/jeffreyhorn/nlp2mcp/issues/739)
**Status:** Fixed
**Severity:** Medium -- Generated MCP files fail GAMS compilation for affected models
**Discovered:** 2026-02-15 (Sprint 19, during Issue #730 investigation)
**Affected Models:** ganges, gangesx (and likely other models with dynamically assigned subsets)

---

## Problem Summary

The ganges and gangesx MCP output produces 6 instances of GAMS Error 187 ("Assigned set used as domain") because dynamically assigned subsets (`im(i)`, `ie(i)`) are used as domains in variable and equation declarations. GAMS requires that sets used as declaration domains be statically defined, not dynamically assigned.

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
 418      nu_pmdef(im)
****                $187
 420      nu_taumdet(im)
****                  $187
 463      nu_export(ie)
****                 $187
 859      export(ie)
****              $187
 917      pmdef(im)
****             $187
 944      taumdet(im)
****               $187
```

The errors occur in both original equation declarations (`export(ie)`, `pmdef(im)`, `taumdet(im)`) and their corresponding KKT multiplier declarations (`nu_export(ie)`, `nu_pmdef(im)`, `nu_taumdet(im)`).

---

## Root Cause

In the original ganges model (`data/gamslib/raw/ganges.gms`), the subsets `im` and `ie` are defined dynamically via assignment statements:

```gams
Set
   im(i)  'importing sectors'
   ie(i)  'exporting sectors' ;

* Dynamic assignment (lines 143-144)
im(i) = yes$dat("cons-imp",i);
ie(i) = yes$dat("xvoli",i);
```

These sets are then used as domains in equation declarations:

```gams
* Original equation declarations (lines 932, 936, 1036)
pmdef(im)..    pm(im) =e= pim(im)*(1 + trmm(im) + tfm(im) + taum(im));
taumdet(im)$(not sc(im))..  pm(im) =e= px(im);
export(ie)..   ex(ie) =e= exscale*aex(ie)*(er00*pie(ie)/(pq(ie)*(1 + trmx(ie))))**eta(ie);
```

GAMS allows dynamically assigned sets in dollar conditions and sum/prod index filters, but NOT as declaration domains for variables and equations. The `im` and `ie` subsets are populated at runtime based on data, making them "assigned sets" which cannot be used as domains.

The emitter faithfully reproduces these declarations, including the KKT multiplier variables and equations that inherit the same domains:
- `nu_pmdef(im)` — multiplier for `pmdef(im)`
- `nu_taumdet(im)` — multiplier for `taumdet(im)`
- `nu_export(ie)` — multiplier for `export(ie)`

### Why this works in the original model but not in the MCP

In the original GAMS model, the `solve` statement likely works because GAMS processes the model in a way that resolves the dynamic sets before compilation of the solve block. However, in the MCP reformulation, all declarations must be valid at compile time since the entire model (including KKT conditions) is declared statically.

---

## Fix Approach

Several possible approaches:

### Option A: Replace dynamic subset domains with parent set + dollar condition
Convert declarations like:
```gams
Equation pmdef(im);
pmdef(im).. pm(im) =e= ...;
```
to:
```gams
Equation pmdef(i);
pmdef(i)$im(i).. pm(i) =e= ...;
```

This uses the parent set `i` as the domain and applies the subset as a dollar condition. This is the standard GAMS pattern for working with dynamic subsets.

The same transformation applies to multiplier variables:
```gams
Variable nu_pmdef(i);
nu_pmdef.fx(i)$(not im(i)) = 0;  * Fix to zero for non-members
```

### Option B: Convert dynamic subsets to static subsets
If the subset membership can be determined at parse time (e.g., from the data), convert the dynamic assignment to a static set definition:
```gams
Set im(i) / cons-good, cap-good, int-good /;
```

This requires resolving `yes$dat("cons-imp",i)` at parse time.

### Option C: Use `$onMulti` and pre-declare
Use GAMS' `$onMulti` directive to allow re-declaration, and pre-declare the sets as static before the dynamic assignment.

### Recommended approach
Option A is the cleanest and most general solution. It requires:
1. Detecting which sets are dynamically assigned (the IR likely already tracks this)
2. In the emitter, replacing the dynamic subset domain with the parent set
3. Adding a dollar condition `$subset(indices)` to the equation definition
4. For multiplier variables, fixing non-member values to zero

---

## Affected Declarations in ganges MCP Output

### Original equations (3 declarations)
| Equation | Current Domain | Should Be |
|----------|---------------|-----------|
| `pmdef(im)` | `im` (dynamic) | `pmdef(i)$im(i)` |
| `taumdet(im)` | `im` (dynamic) | `taumdet(i)$im(i)` |
| `export(ie)` | `ie` (dynamic) | `export(i)$ie(i)` |

### KKT multiplier variables (3 declarations)
| Variable | Current Domain | Should Be |
|----------|---------------|-----------|
| `nu_pmdef(im)` | `im` (dynamic) | `nu_pmdef(i)` with `.fx(i)$(not im(i)) = 0` |
| `nu_taumdet(im)` | `im` (dynamic) | `nu_taumdet(i)` with `.fx(i)$(not im(i)) = 0` |
| `nu_export(ie)` | `ie` (dynamic) | `nu_export(i)` with `.fx(i)$(not ie(i)) = 0` |

---

## Fix Details

**Approach:** Modified variant of Option A — Replace dynamic subset names with parent set names in *declarations only*, leave equation definitions unchanged.

**Key insight:** GAMS allows the equation *declaration* to use the parent set while the equation *definition* uses the dynamic subset as the controlling index:
```gams
Equation pmdef(i);              * Declaration uses parent set i
pmdef(im).. pm(im) =e= ...;    * Definition uses subset im as controlling index
```
This is valid GAMS — the equation is only generated for elements in `im`, and the parent set `i` in the declaration is compatible.

**Implementation:** In `src/emit/templates.py`:

1. Added `_build_dynamic_subset_map(model_ir)` — builds a mapping from dynamically assigned subset names (lowercase) to their parent set names. A set qualifies if it: (a) has entries in `model_ir.set_assignments`, (b) has no static members, and (c) has a single-element domain.

2. Added `_remap_domain(domain, dynamic_map)` — replaces dynamic subset names in a domain tuple with their parent sets.

3. Modified `emit_variables()` — applies `_remap_domain` to all variable domain tuples in declarations.

4. Modified `emit_equations()` — applies `_remap_domain` to all equation domain tuples in declarations.

5. Equation definitions (`emit_equation_def` in `equations.py`) are NOT modified — they continue to use the original subset names as controlling indices, which is valid.

**Result:** All 6 instances of GAMS Error 187 eliminated for ganges/gangesx. Both original equations (`export(ie)`, `pmdef(im)`, `taumdet(im)`) and KKT multiplier variables (`nu_export(ie)`, `nu_pmdef(im)`, `nu_taumdet(im)`) now use parent set `i` in their declarations.

**Quality Gate:** All checks pass (typecheck, lint, format, 3339 tests).

---

## Relevant Files

- `src/emit/templates.py` — Fix location: `_build_dynamic_subset_map()`, `_remap_domain()`, and their use in `emit_variables()` and `emit_equations()`
- `src/ir/symbols.py` — `SetDef.domain` and `SetAssignment` used for detection
- `src/ir/model_ir.py` — `model_ir.set_assignments` lists dynamic set assignments
- `data/gamslib/raw/ganges.gms` — Original model (lines 27-28, 143-144 for set defs; 932, 936, 1036 for equations)
- `data/gamslib/raw/gangesx.gms` — Same structure as ganges
