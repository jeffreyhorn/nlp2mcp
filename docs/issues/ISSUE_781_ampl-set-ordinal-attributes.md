# Parser: Set Ordinal Attribute Syntax (set.first, set.last) Not Supported

**Status:** OPEN
**Severity:** Medium — blocks parse of ampl.gms; same pattern may affect other models using GAMS set attribute accessors
**Date:** 2026-02-18
**Affected Models:** ampl.gms
**GitHub Issue:** [#781](https://github.com/jeffreyhorn/nlp2mcp/issues/781)

---

## Problem Summary

`ampl.gms` fails to parse at line 57:

```
Error: Parse error at line 57, column 1: Unexpected character: 'M'
  Model ampl 'maximum revenue production problem' / all /;
```

The actual root cause is earlier on lines 54-56:

```gams
obj..  profit =e= sum((p,t), c(p,t)*x(p,t))
               +  sum((r,tl), (-d(r)$t(tl) + f(r)$tl.last)*s(r,tl));

s.up(r,tl)$tl.first = b(r);
```

Two unsupported patterns:
1. **`tl.last`** — set ordinal attribute used in a dollar condition: `f(r)$tl.last`
2. **`tl.first`** — set ordinal attribute used as a bound condition: `s.up(r,tl)$tl.first = b(r)`

These are GAMS **set iterator attributes**: `set.first` returns 1 for the first element,
`set.last` returns 1 for the last element, `set.pos` returns the ordinal position.

---

## GAMS Code Pattern

```gams
Set
   tl    'extended t'  / 1*5 /
   t(tl) 'periods'     / 1*4 /;

Variable s(r,tl);
Parameter b(r), d(r), f(r);

Equation obj, balance(r,tl);

* tl.last evaluates to 1 when tl is the last element of its set
obj..  profit =e= sum((p,t), c(p,t)*x(p,t))
               +  sum((r,tl), (-d(r)$t(tl) + f(r)$tl.last)*s(r,tl));

* tl.first evaluates to 1 when tl is the first element
s.up(r,tl)$tl.first = b(r);

* Also: equation head with lead in domain
balance(r,tl+1)..   s(r,tl+1) =e= s(r,tl) - sum(p, a(r,p)*x(p,tl));
```

The `tl.first` and `tl.last` syntax is GAMS's way of referring to set boundary
conditions. In a dollar condition context, `$tl.first` means "only when `tl` is the
first element of its set". In a bound context, `s.up(r,tl)$tl.first = b(r)` sets the
upper bound only for the first period.

Note: line 51 also uses `balance(r,tl+1)..` — equation head with lead offset — the same
issue as mine.gms (see separate issue).

---

## Root Cause

The grammar and parser do not handle the `ID.first`, `ID.last`, `ID.pos` set attribute
accessor syntax. When the parser encounters `tl.last` or `tl.first` in a dollar
condition context, it fails because `.last` and `.first` are not recognized as valid
attribute names in index/conditional expressions.

The grammar currently handles `.l`, `.lo`, `.up`, `.fx` as variable bound attribute
accessors, but not the set iterator attributes `.first`, `.last`, `.pos`, `.ord`.

---

## Expected Behavior

`set.first` and `set.last` should evaluate to boolean-like integer values (1 for the
boundary element, 0 otherwise) usable in dollar conditions and expressions.

For NLP-to-MCP purposes:
- `$tl.first` in an equation: restrict to first element — equivalent to `$(ord(tl)=1)`
- `$tl.last` in an equation: restrict to last element — equivalent to `$(ord(tl)=card(tl))`

---

## Proposed Fix

1. **Grammar**: Add set attribute terminal for `.first`, `.last`, `.pos`, `.ord` in the
   `index_expr` / `condition` context:
   ```lark
   set_attr: ID "." SET_ATTR_NAME
   SET_ATTR_NAME: "first" | "last" | "pos" | "ord"
   ```

2. **Parser**: In the semantic handler, convert `ID.first` → `Call("ord", (SymbolRef(ID),)) == Const(1)` and
   `ID.last` → `Call("ord", (SymbolRef(ID),)) == Call("card", (SymbolRef(ID),))`.

3. **Emit**: The emit layer should render these as GAMS `set.first` / `set.last` syntax
   in the output.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/gams/gams_grammar.lark` | `condition`, `index_expr`, `atom` rules |
| `src/ir/parser.py` | Dollar condition handler, expression builder |
| `data/gamslib/raw/ampl.gms` | Affected model; lines 51, 54-56 |

---

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/ampl.gms')
"
# ParseError: Error: Parse error at line 57, column 1: Unexpected character: 'M'
#   Model ampl 'maximum revenue production problem' / all /;
# (Root cause: tl.last / tl.first on lines 54-56 not parsed)
```

---

## Related Issues

- Variable attribute access (`.lo`, `.up`, `.fx`, `.l`, `.m`) already supported
- Set iterator attributes (`.first`, `.last`, `.pos`, `.ord`) are a separate grammar gap
- mine.gms has related `eq(i+1)..` equation head lead offset issue
