# shale: Alias index emitted as string literal in parameter/set assignment ($170)

**GitHub Issue:** [#1015](https://github.com/jeffreyhorn/nlp2mcp/issues/1015)
**Model:** shale (GAMSlib SEQ=46)
**Status:** OPEN
**Error category:** `gams_compilation_error` (Subcategory — $170)
**Severity:** Medium — model translates but GAMS compilation fails (5 $170 errors + cascading $257/$141)

---

## Problem Summary

The emitter produces `ts('1985-89','tfp') = 1;` where `'tfp'` is a string literal. But `ts` is declared over domain `(tf,tf)`, and `'tfp'` is not an element of set `tf` — it is an **alias** for `tf` (`Alias (tf,tfp)`). GAMS raises $170 (domain violation) because the literal `'tfp'` is not a member of the `tf` set.

In the original model, `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` is a conditional loop assignment that iterates over all `(tf,tfp)` pairs. The parser/IR builder incorrectly "evaluates" this by expanding `tf` to concrete elements but leaves the alias `tfp` as a literal string in the value map key.

---

## Error Details

```
 150  ts('1985-89','tfp') = 1;
****                   $170
**** 170  Domain violation for element
 151  ts('1990-94','tfp') = 1;
****                   $170
 152  ts('1995-99','tfp') = 1;
****                   $170
 153  ts('2000-04','tfp') = 1;
****                   $170
 154  ts('2005-09','tfp') = 1;
****                   $170
```

5 `$170` errors, each because `'tfp'` is not a valid element of set `tf`.

---

## Original GAMS Context

```gams
Set tf / 1975-79, 1980-84, 1985-89, 1990-94, 1995-99, 2000-04, 2005-09, 2010-14 /
    t(tf) 'active time periods' / 1975-79, 1980-84, 1985-89, 1990-94, 1995-99, 2000-04 / ;

Alias (tf,tfp) ;

Parameter ts(tf,tf) 'time summation matrix' ;
ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1 ;
```

The assignment `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` iterates over all `(tf,tfp)` pairs and assigns 1 where `ord(tfp) < ord(tf)`. This produces a lower-triangular matrix of 1s.

---

## Root Cause

**Primary file:** `src/ir/parser.py` (IR builder)

The IR builder processes the conditional assignment `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` and attempts to evaluate it. It correctly iterates over `tf` elements for the first index, but treats the alias `tfp` as a literal string rather than iterating over `tf` elements for the second index. The resulting `ParameterDef.values` contains keys like `('1985-89', 'tfp')` instead of the expected expanded pairs like `('1985-89', '1975-79')`, `('1985-89', '1980-84')`, etc.

The emitter then faithfully emits these incorrect key tuples as `ts('1985-89','tfp') = 1`, which GAMS rejects because `'tfp'` is not a member of set `tf`.

### Expected Behavior

Either:
1. The IR builder should fully expand both indices, evaluating `ord()` to produce the correct set of key tuples, OR
2. The assignment should be preserved as a computed/dynamic assignment and emitted as `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1;` in the MCP file

---

## Reproduction Steps

```bash
.venv/bin/python -m src.cli data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms --quiet
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/shale_mcp.gms lo=2 o=/tmp/shale_mcp.lst
grep '$170' /tmp/shale_mcp.lst
```

---

## Affected Statements

| Line | Statement | Problem |
|------|-----------|---------|
| 150 | `ts('1985-89','tfp') = 1;` | `'tfp'` is alias, not element |
| 151 | `ts('1990-94','tfp') = 1;` | same |
| 152 | `ts('1995-99','tfp') = 1;` | same |
| 153 | `ts('2000-04','tfp') = 1;` | same |
| 154 | `ts('2005-09','tfp') = 1;` | same |

---

## Notes

- The $257 (solve not checked) and $141 (unassigned symbol) errors are cascading consequences of the $170 errors
- This is an IR builder issue, not an emitter issue — the emitter correctly emits whatever the IR contains
- The `Alias (tf,tfp)` declaration is correctly parsed (it appears in `model_ir.aliases`)
- Similar patterns may affect other models that use alias indices in conditional parameter assignments
- Separate from Issue #1005 ($149 uncontrolled set), which is fixed
