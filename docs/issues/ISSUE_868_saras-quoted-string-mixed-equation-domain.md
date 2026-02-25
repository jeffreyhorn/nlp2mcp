# Saras: Quoted String in Mixed Equation Domain Rejected as Unknown Set

**GitHub Issue:** [#868](https://github.com/jeffreyhorn/nlp2mcp/issues/868)
**Status:** OPEN
**Severity:** Medium — Model fails to parse (blocks translate/solve)
**Date:** 2026-02-24
**Affected Models:** saras

---

## Problem Summary

The saras model fails during IR building because equation definitions use mixed domains
containing both set references and quoted string literals (e.g., `Rcon1(r,"aland")..`).
The parser only handles the case where ALL domain elements are quoted strings (Issue #774),
not the mixed case where some are sets and some are literal element selectors.

---

## Error Details

```
ParserSemanticError: Unknown set or alias 'aland' referenced in equation 'Rcon1' domain
[context: expression] (line 1310, column 1)
```

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.preprocessor import preprocess_text
from src.ir.parser import parse_model_text
with open('data/gamslib/raw/saras.gms') as f:
    raw = f.read()
ir = parse_model_text(preprocess_text(raw))
"
```

---

## Root Cause

The equation `Rcon1` is declared without an explicit domain:

```gams
Equation
   rcon1    'regional arable land constrain'
```

But the equation definition uses a mixed domain with set `r` and literal `"aland"`:

```gams
Rcon1(r,"aland").. sum((f,t,p), cx(r,f,t,p)*cres(r,t,p,"aland")*nf(r,f)) =l= RLC(r,"aland");
```

In GAMS, `"aland"` is a fixed element selector — the equation is defined only for that
specific element, not iterated over a set. This is a common GAMS pattern for resource
constraint equations.

The handler at `src/ir/parser.py:3009-3016` (`_handle_eqn_def_domain`) detects quoted
string literals in the domain and skips set validation, BUT only when **all** domain
tokens are string literals (line 3015 uses `all(...)`). In the mixed case (`r` is a set,
`"aland"` is a literal), the check fails and `"aland"` is passed to `_ensure_sets()`
which rejects it.

### Key Code Location

`src/ir/parser.py`, `_handle_eqn_def_domain()` (lines ~3009-3018):

```python
raw_tokens = [
    c.children[0]
    for c in domain_list_node.children
    if isinstance(c, Tree) and c.data == "domain_element" and c.children
]
if raw_tokens and all(isinstance(t, Token) and _is_string_literal(t) for t in raw_tokens):
    domain = self._equation_domains.get(name.lower(), ())
# Then: self._ensure_sets(domain, ...)  ← "aland" fails here
```

---

## Suggested Fix

Instead of requiring ALL domain tokens to be string literals, filter out the quoted
string literal tokens from the domain before calling `_ensure_sets()`. For each domain
element, if the raw token is a quoted string literal, replace it with the corresponding
declared domain element (or skip it in validation). The non-literal tokens should still
be validated as sets.

**Approach:** Build a filtered domain list that replaces quoted string elements with
the corresponding declared domain set (or drops them from validation):

```python
# Filter: only validate non-literal domain elements
filtered_domain = []
for i, name_str in enumerate(domain):
    if i < len(raw_tokens) and isinstance(raw_tokens[i], Token) and _is_string_literal(raw_tokens[i]):
        continue  # Skip literal element — not a set reference
    filtered_domain.append(name_str)
self._ensure_sets(filtered_domain, f"equation '{name}' domain", node)
```

This pattern appears in ~10 equations in saras (Rcon1-6, Fcon1-6, nRcon1-6, etc.).

**Effort estimate:** ~1h

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/parser.py` | Update `_handle_eqn_def_domain()` to handle mixed quoted/set domains |

---

## Related Issues

- **Issue #774**: Original fix for all-literal equation domains (singleton instantiation)
- **Issue #857** (completed): Previous saras blocker (attribute access validation)
- **Issue #840** (completed): Earlier saras blocker (`%system.nlp%` macro)
