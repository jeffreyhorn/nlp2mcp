# lmp2: Empty Dynamic Subsets and Loop Body Assignments Not Emitted

**GitHub Issue:** [#952](https://github.com/jeffreyhorn/nlp2mcp/issues/952)
**Status:** OPEN
**Severity:** High — 3 compilation errors block solve
**Date:** 2026-02-27
**Affected Models:** lmp2

---

## Problem Summary

The lmp2 MCP output declares dynamic subsets `m(mm)` and `n(nn)` but never assigns members to them. Additionally, parameters `cc(p,nn)`, `f(p)`, `A(mm,nn)`, and `b(mm)` are declared without values because their assignments occur inside a `loop()` statement that the IR parser does not process.

This causes GAMS error $141 ("Symbol declared but no values have been assigned") on `n(nn)` used in `x.fx(nn)$(not (n(nn))) = 0;` and cascading errors.

---

## Error Details

```
 125  x.fx(nn)$(not (n(nn))) = 0;
****                 $141
**** 141  Symbol declared but no values have been assigned.

 152  Solve mcp_model using MCP;
****                           $257
**** 257  Solve statement not checked because of previous errors

 155  nlp2mcp_obj_val = obj.l;
****                        $141
**** 141  Symbol declared but no values have been assigned.
```

Total: **3 errors** (1 primary + 2 cascading)

---

## Root Cause: Loop Body Statements Not Extracted

In the original `lmp2.gms`, sets and parameters are assigned inside a doubly-nested loop:

```gams
loop(c,
   m(mm)   = ord(mm) <= cases(c,'m');
   n(nn)   = ord(nn) <= cases(c,'n');
   cc(p,n) = uniform(0,1);
   ...
   loop(i,
      f(p)    = uniform(0,1);
      cc(p,n) = uniform(0,1);
      A(m,n)  = 2*uniform(0,1) - 1;
      b(m)    = sum(n, A(m,n)) + 2*uniform(0,1);
      solve lmp2 minimizing obj using nlp;
   );
);
```

The IR parser's `_handle_loop_stmt()` stores the loop body as raw AST trees in `model_ir.loop_statements` but does **not** process individual statements to extract:
1. **Set assignments** (`m(mm) = ord(mm) <= cases(c,'m')`) — never added to `model_ir.set_assignments`
2. **Parameter assignments** (`cc(p,n) = uniform(0,1)`) — never added to `ParameterDef.expressions`

The emitter then:
- Declares `m(mm)` and `n(nn)` as empty dynamic subsets (no members)
- Declares parameters `cc`, `f`, `A`, `b` without values (no inline data, no computed assignments)

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/lmp2_mcp.gms lo=2
```

---

## Proposed Fix

### Option A: Extract Loop Body Assignments (Preferred)

Enhance `_handle_loop_stmt()` in `src/ir/parser.py` to walk the loop body and process:
1. Set assignment statements → add to `model_ir.set_assignments`
2. Parameter assignment statements → add to `ParameterDef.expressions`

This is the general solution that would benefit all models with loop-body assignments.

**Challenges:**
- Loop variable bindings (e.g., `c` in `loop(c, ...)`) affect which set members are active
- Stochastic functions (`uniform()`) have no deterministic representation
- For NLP→MCP transformation, we need one "snapshot" of parameter values (e.g., from the last loop iteration)

### Option B: Emit Loop Body as Executable GAMS (Simpler)

Instead of interpreting loop bodies, emit the relevant assignment statements as executable GAMS code in the MCP output. For models where the NLP solve uses parameter values that are set before the solve statement, emit those assignments (with the loop variable fixed to the last iteration or a representative value).

### Option C: `$onImplicitAssign` Workaround (Partial)

Add `$onImplicitAssign` directive to suppress the $141 warning. This doesn't actually fix the empty subset problem (the solve would still use empty sets) but would allow compilation.

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/ir/parser.py` | Walk loop body statements in `_handle_loop_stmt()` |
| `src/emit/original_symbols.py` | Emit set assignments from `model_ir.set_assignments` |
| `src/emit/emit_gams.py` | Ensure loop body assignments emitted in correct order |

---

## Notes

- The `lmp2` model uses stochastic data (`uniform(0,1)`) in a multi-scenario loop, meaning there is no single "correct" parameter value — each loop iteration generates random data
- For MCP transformation purposes, we need representative values; the stochastic parameters (`cc`, `A`, `b`) would need to be initialized with arbitrary values or the loop body partially evaluated
- The dynamic subset population pattern (`m(mm) = ord(mm) <= cases(c,'m')`) is a conditional set assignment that requires runtime evaluation
