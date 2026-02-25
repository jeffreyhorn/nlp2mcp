# Saras: Case-Sensitive Attribute Access Validation Rejects `Rcon1.scale`

**GitHub Issue:** [#857](https://github.com/jeffreyhorn/nlp2mcp/issues/857)
**Status:** OPEN
**Severity:** Medium — Model fails to parse (blocks translate/solve)
**Date:** 2026-02-24
**Affected Models:** saras

---

## Problem Summary

After the `%system.nlp%` macro expansion fix (Issue #840, Sprint 21 Day 2), the saras model
now progresses past the lexer but fails during IR building with a `ParserSemanticError`:
`Symbol 'Rcon1' not declared`. The equation `rcon1` is declared in lowercase but referenced
with mixed case (`Rcon1`) in `.scale` attribute access. The attribute access validation in
`parser.py` fails to match the mixed-case reference against the lowercase-stored equation.

---

## Error Details

```
ParserSemanticError: Symbol 'Rcon1' not declared
  Context: attribute access 'Rcon1.scale(r,'aland')'
```

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
ir = parse_file('data/gamslib/raw/saras.gms')
"
```

---

## Root Cause

The equation is declared in lowercase at line 1240 of `saras.gms`:

```gams
Equation
   rcon1    'regional arable land constrain'
```

But referenced with mixed case at line 1278:

```gams
Rcon1.scale(r,'aland') = 10000;
```

The IR builder stores equations in a `CaseInsensitiveDict` and adds the name to
`_declared_equations` in lowercase. However, the attribute access validation logic in
`parser.py` (around lines 3787-3797 and 3810-3820) extracts the base name as-is from the
parse tree token (`Rcon1`) and checks it against `self.model.equations` using an exact-case
lookup that does not leverage the `CaseInsensitiveDict.__contains__` properly, or the check
is performed before the equation is registered.

The same pattern appears for multiple equations in saras (e.g., `Rcon1`, `Rcon2`, etc.).

### Key Code Location

`src/ir/parser.py`, attribute access validation blocks (lines ~3787-3820):

```python
base_name = _token_text(target.children[0])  # Gets "Rcon1" as-is
if (
    base_name not in self.model.variables
    and base_name not in self.model.params
    and base_name not in self.model.equations  # Should be case-insensitive
    ...
):
    raise self._error(...)
```

---

## Suggested Fix

Ensure the attribute access validation uses case-insensitive comparison for equations
(and ideally for all symbol types). Since `self.model.equations` is a `CaseInsensitiveDict`,
the `in` operator should already handle case-insensitive lookup — verify that the
`CaseInsensitiveDict.__contains__` method normalizes the key. If it does, the issue may be
that `base_name` includes quotes or whitespace from `_token_text()`.

Alternatively, normalize `base_name` to lowercase before the check:

```python
base_lower = base_name.lower()
if (
    base_lower not in self.model.variables
    and base_lower not in self.model.params
    and base_lower not in self.model.equations
    ...
):
```

**Effort estimate:** ~30min

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/parser.py` | Fix case-insensitive symbol lookup in attribute access validation (~lines 3787-3820) |

---

## Related Issues

- **Issue #840**: Previous saras blocker (`%system.nlp%` macro not expanded) — fixed in Sprint 21 Day 2
- This is a **separate** issue from #840; saras now has two sequential blockers
