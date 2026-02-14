# Validation: False Positive Circular Dependency Detection (ganges, gangesx)

**GitHub Issue:** [#719](https://github.com/jeffreyhorn/nlp2mcp/issues/719)
**Status:** Open
**Severity:** Medium — Blocks pipeline for models with mutually dependent variables across equations
**Discovered:** 2026-02-13 (Sprint 19, after Issues #714 fix advanced ganges/gangesx past level bound and model_with_list errors)
**Affected Models:** ganges, gangesx

---

## Problem Summary

The model validation stage raises a false positive "Circular dependency detected" error for ganges and gangesx. The detector flags equations `prodx` and `infalloc` as creating a circular definition between variables `x` and `g`. However, this is a valid simultaneous equation system — NLP models are solved simultaneously, so mutual dependencies between variables across equations are expected and valid.

---

## Reproduction

**Model:** `ganges` (`data/gamslib/raw/ganges.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -m src.cli data/gamslib/raw/ganges.gms -o /tmp/ganges_mcp.gms --diagnostics
```

**Error output:**
```
Error: Unexpected error - Error: Circular dependency detected: 'x' and 'g' define each other

Suggestion: Equations 'prodx' and 'infalloc' create a circular definition:
  prodx: x depends on g
  infalloc: g depends on x

Reformulate your model to break the cycle.
```

**Model:** `gangesx` (`data/gamslib/raw/gangesx.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -m src.cli data/gamslib/raw/gangesx.gms -o /tmp/gangesx_mcp.gms --diagnostics
```

**Error output:** Same circular dependency error.

---

## Root Cause

The circular dependency detector is in `src/validation/model.py` around line 212. It builds a dependency graph from equality constraints: if equation `e` defines `v1 =e= f(v2, ...)`, it records that `v1` depends on `v2`. If a cycle is found (v1 -> v2 -> v1), it raises an error.

The two flagged equations in ganges are:

```gams
prodx(i)..    x(i) =e= ax(i)*(deltax(i)*z(i)**(-rhox(i)) + (1 - deltax(i))*g(i)**(-rhox(i)))**(-1/rhox(i));
```
(x is defined in terms of g)

```gams
infalloc(i).. g(i) =e= ratinf*dg(i)/sum(j, dg(j))*sum(si, x(si));
```
(g is defined in terms of x)

This creates a cycle: x -> g -> x. The detector treats this as an error, but in NLP models this is a valid simultaneous system. The KKT reformulation should handle both equations as part of the system — there's no need to topologically sort or eliminate variables.

## Proposed Fix

The circular dependency check in `src/validation/model.py` should either:

1. **Be removed entirely** — Circular dependencies in NLP equation systems are normal. The KKT transformation handles all equations simultaneously.

2. **Be downgraded to a warning** — Log a warning but don't block the pipeline. Some users might want to know about cycles for debugging.

3. **Only flag single-equation self-references** — Only raise an error if a single equation defines a variable in terms of itself (e.g., `x =e= f(x)`), which may indicate a modeling error. Cross-equation cycles are expected in simultaneous systems.

Option 3 is the most precise. The current implementation should be modified to only detect self-referential equations, not cross-equation cycles.

---

## Context

Both ganges and gangesx parse successfully after the Issue #714 fixes (last-write-wins bound semantics, dynamic model_ref_list lookup). They have `declared_model=ganges`, 67 model equations, and `model_uses_all=False`. The circular dependency detection is the first pipeline error after successful parsing.
