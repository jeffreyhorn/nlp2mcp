# hydro: Parameter Dimension Mismatch ($148)

**GitHub Issue:** [#911](https://github.com/jeffreyhorn/nlp2mcp/issues/911)
**Model:** hydro (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $148 Dimension different

## Problem

The generated MCP file references parameter `loss(t)` as a 1-dimensional indexed parameter, but GAMS sees `loss` as a scalar (0-dimensional), producing $148 errors.

```gams
comp_demcons(t).. thermal(t) + hydro(t) - (load(t) + loss(t)) =G= 0;
```

GAMS error: "Dimension different — The symbol is referenced with more/less indices than declared."

## Error Output

```
**** 148  Dimension different - The symbol is referenced with more/less
****         indices as declared. Check symbol reference list for the
****         correct number of indices.
```

4 compilation errors on equations referencing `loss(t)`.

## Root Cause

In the original hydro.gms, `loss` is declared as a **scalar** parameter:

```gams
Scalar  loss  'mw transmission losses'  / 0 / ;
```

But the emitter generates `loss(t)` in the KKT equations as if it were indexed. The KKT transformation likely infers the domain from the constraint context (where `loss` appears alongside indexed variables `thermal(t)` and `hydro(t)`) and incorrectly promotes the scalar to indexed form.

## Original GAMS

```gams
Scalar  loss  'mw transmission losses'  / 0 / ;
...
demcons(t) .. thermal(t) + hydro(t) =g= load(t) + loss;
```

Note: `loss` is used **without indices** in the original equation.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/hydro.gms -o /tmp/hydro_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/hydro_mcp.gms o=/tmp/hydro_mcp.lst
grep '^\*\*\*\*' /tmp/hydro_mcp.lst
```

## Suggested Fix

When generating KKT stationarity/complementarity equations, preserve the original parameter's arity. If a scalar parameter appears in an indexed equation, do not promote it to indexed form — emit `loss` (bare) rather than `loss(t)`.

## Impact

4 compilation errors. Model cannot compile.
