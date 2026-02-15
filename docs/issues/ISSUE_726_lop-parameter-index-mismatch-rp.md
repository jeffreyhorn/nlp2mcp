# Parser: Parameter Index Count Mismatch for Runtime-Reassigned Parameters (lop)

**GitHub Issue:** [#726](https://github.com/jeffreyhorn/nlp2mcp/issues/726)
**Status:** Open
**Severity:** High -- Blocks parsing of lop model entirely
**Discovered:** 2026-02-14 (Sprint 19, after Issues #722 fixed inline comments and lead operator)
**Affected Models:** lop (and any model that declares parameters with more indices than used at runtime)

---

## Problem Summary

The lop model fails to parse with the error:

```
Error: Parse error at line 222, column 1: Parameter 'rp' expects 3 indices, got 2 [context: expression]
  rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
  ^
```

The parameter `rp` is declared with 3 index positions (`rp(s,s,s)`) but is assigned and used with only 2 indices (`rp(ll,s)`). In GAMS, this is valid -- parameter declarations specify the maximum dimensionality and the domain sets, but runtime assignments can use fewer indices (the remaining indices are effectively projected out or the parameter is treated as having a reduced effective domain). The parser enforces strict index count matching, which is too restrictive.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms
```

**Error output:**
```
Error: Unexpected error - Error: Parse error at line 222, column 1:
Parameter 'rp' expects 3 indices, got 2 [context: expression]
  rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
  ^

Suggestion: Provide exactly 3 indices to match the parameter declaration
```

---

## Root Cause

### GAMS parameter declaration vs. usage

In `data/gamslib/raw/lop.gms`, lines 220-224:

```gams
Parameter
   rp(s,s,s)   'rank of node'
   lastrp(s,s) 'rank of the last node in line';

rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
lastrp(ll) = smax(s,rp(ll,s));
```

The parameter `rp` is declared as `rp(s,s,s)` (3-dimensional over set `s`), but assigned as `rp(ll,s)` (2-dimensional, where `ll` is a subset of `s`). The assignment `rp(ll,s) = sum(r$lr(ll,s,r), ord(r))` collapses the third dimension via the `sum` over `r`.

Similarly, `lastrp` is declared as `lastrp(s,s)` but assigned as `lastrp(ll)` (1 index).

In GAMS, this pattern is valid and common. The declaration specifies the maximum domain, but assignments can reference fewer indices when the intent is to assign across a slice or when some indices are implicitly free.

### Parser enforcement

The parser validates that every reference to a declared parameter uses exactly the declared number of indices. This validation is too strict for GAMS semantics where:

1. Parameters can be assigned with fewer indices than declared (remaining indices implied)
2. The set aliases (`ll` is a subset/alias of `s`) further complicate matching
3. GAMS resolves this at runtime through domain checking, not at compile time

---

## Fix Approach

The parser's parameter index count validation should be relaxed to allow:
- Fewer indices than declared (GAMS allows this for parameter assignments and references)
- The validation should warn rather than error, or be removed entirely for parameter references in assignment context

The relevant validation likely occurs in the parser or semantic analysis stage when resolving parameter references. The error message "Parameter 'rp' expects 3 indices, got 2" suggests a strict arity check.

---

## Additional Context

- The `rp` parameter is used extensively throughout the lop model (lines 254, 284, 351-355, 359)
- All subsequent uses reference `rp(ll,s)` or `rp(sol,s)` with 2 indices, never 3
- The 3-index declaration appears to be a GAMS convention for declaring the maximum domain
- The `lastrp(s,s)` parameter has the same pattern: declared with 2 indices, used with 1
- This issue blocks the lop model from proceeding past the parse stage; all downstream stages (normalization, differentiation, KKT assembly, MCP emission) are unreachable
