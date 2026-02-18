# Parser: Quoted/Hyphenated Set Element Used as Equation Domain Not Resolved

**GitHub Issue:** [#774](https://github.com/jeffreyhorn/nlp2mcp/issues/774)
**Status:** OPEN
**Severity:** Medium — blocks translation of shale.gms; same class of issue may affect other models with hyphenated time-period set elements used as singleton equation indices
**Date:** 2026-02-18
**Affected Models:** shale.gms

---

## Problem Summary

`shale.gms` parses successfully after Day 8 grammar fixes but fails during translation with:

```
Error: Invalid model - Unknown set or alias '2000-04' referenced in equation 'mmr3' domain
[context: expression] (line 474, column 1)
```

The equation `mmr3` is declared as a scalar equation (no domain) but its definition uses
a quoted string literal `"2000-04"` as a singleton index:

```gams
mmr3("2000-04").. sum(pdu, z(pdu,"2000-04")) =l= .413*sum(pmu, z(pmu,"1990-94"));
```

The parser/translator sees `"2000-04"` in the equation LHS domain position and tries to
resolve it as a set or alias name, but it is a **set element literal** (a member of the
set `tf`), not a set name.

---

## GAMS Code Pattern

```gams
Sets
   tf  'expansion time periods'
       / 1985-89, 1990-94, 1995-99, 2000-04, 2005-09 /
   t(tf) 'time periods'
       / 1990-94, 1995-99, 2000-04, 2005-09 /;

Equations
   mmr3  'mine refilling in third period (million units)'
   mmr4  'mine refilling in fourth period (million units)';

mmr3("2000-04").. sum(pdu, z(pdu,"2000-04")) =l= .413*sum(pmu, z(pmu,"1990-94"));
mmr4("2005-09").. sum(pdu, z(pdu,"2005-09")) =l= .413*sum(pmu, z(pmu,"1990-94") + z(pmu,"1995-99"))
                                                  - sum(pdu, z(pdu,"2000-04"));
```

In GAMS, `mmr3("2000-04")..` is a **singleton equation instance** — the equation `mmr3`
is defined only for the single element `"2000-04"` of the implicit domain. This is
equivalent to writing `mmr3(tf)$(ord(tf)=3)..` but using the literal element instead.

---

## Error Location

Translation failure at `src/ir/parser.py`, in equation domain resolution. The translator
attempts to look up `"2000-04"` as a set/alias name to determine the equation's index
domain, but it is a quoted set element ID, not a set name.

```
line 474: mmr3("2000-04").. sum(pdu, z(pdu,"2000-04")) =l= ...
```

---

## Root Cause

The equation definition parser handles `eq_name(domain_set)..` syntax where
`domain_set` is expected to be a set or alias name. When a **quoted string literal** (set
element) appears in the domain position, the parser cannot resolve it as a set and raises
`Unknown set or alias`.

GAMS allows this pattern as a form of singleton instantiation: the equation is defined
for exactly one element value rather than iterating over a full set. This is semantically
different from a domain set — it is a fixed index value, not a range.

---

## Expected Behavior

The translator should recognize `eq_name("literal")..` as a **singleton equation
definition** — equivalent to a scalar equation that applies only when the index equals
the given literal. The equation body should be extracted and treated as a single
(non-indexed) constraint.

For NLP-to-MCP purposes, this simplifies to treating `mmr3` as a scalar equation with
its body substituted directly.

---

## Proposed Fix

In the equation definition parser, when the domain index resolves to a quoted string
(or a SET_ELEMENT_ID that is not a known set/alias):

1. Recognize this as a singleton instantiation pattern.
2. Treat the equation as a scalar (no iteration domain).
3. Substitute the literal value wherever the implicit index appears in the equation body.

Alternatively, if the equation was declared without an explicit domain (as `mmr3` is
here — just the name, no `(set)` domain in the `Equations` block), the translator could
fall back to treating it as a scalar equation and ignoring the singleton selector in the
definition header.

---

## Related Patterns

The same issue may affect other models that use time-period identifiers like `"1990-94"`,
`"1995-99"` as singleton equation indices. Hyphenated identifiers are quoted by the
preprocessor, making them string literals in the parse tree.

Similar GAMS idiom (also potentially affected):
```gams
constraint("period-1").. x =l= 100;
constraint("period-2").. x =l= 150;
```

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/parser.py` | Equation definition parsing — domain resolution for `eq(literal)..` |
| `data/gamslib/raw/shale.gms` | Affected model; lines 474, 476 |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms
# Error: Invalid model - Unknown set or alias '2000-04' referenced in equation 'mmr3' domain
```
