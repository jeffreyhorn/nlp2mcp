# Saras: Case-Sensitive Attribute Access Validation Rejects `Rcon1.scale`

**GitHub Issue:** [#857](https://github.com/jeffreyhorn/nlp2mcp/issues/857)
**Status:** FIXED
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

## Root Cause

The attribute access validation checks `self.model.equations` (a `CaseInsensitiveDict`
populated when equations are *defined* with `..` syntax), but `.scale` assignments appear
BEFORE equation definitions in saras. At the time the `.scale` assignment is processed,
`self.model.equations` is empty — equations have only been *declared* (stored in
`self._declared_equations`, a `set[str]` of lowercase names), not yet *defined*.

The validation blocks at lines ~3787-3824 did not check `self._declared_equations`, so
any `.scale` assignment on a declared-but-not-yet-defined equation would fail validation.

### Key Code Location

`src/ir/parser.py`, attribute access validation blocks (lines ~3787-3824):
both `attr_access` and `attr_access_indexed` handlers.

---

## Fix Applied

Added `self._declared_equations` to the validation checks in both `attr_access` and
`attr_access_indexed` blocks:

```python
if (
    base_lower not in self.model.variables
    and base_lower not in self.model.params
    and base_lower not in self.model.equations
    and base_lower not in self._declared_equations  # <-- NEW
    and base_lower not in self.model.declared_models
    and base_lower not in self.model.declared_files
):
    raise self._error(...)
```

This allows `.scale` (and other attribute) assignments on equations that have been
declared but not yet defined.

**Note:** saras still fails at a later point (line 1310) with a different error about
`aland` not being a known set — this is a separate issue (quoted string domain elements
in equation definitions), not related to #857.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ir/parser.py` | Added `self._declared_equations` to attribute access validation in both `attr_access` and `attr_access_indexed` blocks |

---

## Related Issues

- **Issue #840**: Previous saras blocker (`%system.nlp%` macro not expanded) — fixed in Sprint 21 Day 2
- This is a **separate** issue from #840; saras now has two sequential blockers
