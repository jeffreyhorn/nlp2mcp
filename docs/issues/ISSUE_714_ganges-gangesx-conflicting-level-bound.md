# Parser: Conflicting Level Bound Error on Repeated .l Assignments (ganges, gangesx)

**GitHub Issue:** [#714](https://github.com/jeffreyhorn/nlp2mcp/issues/714)
**Status:** Open
**Severity:** Medium — Blocks parsing of models that use multiple conditional .l assignments
**Discovered:** 2026-02-13 (Sprint 19, after Issues #710 fix advanced ganges/gangesx past model_ref_list)
**Affected Models:** ganges (line 704), gangesx (line 887)

---

## Problem Summary

The parser raises a `ParserSemanticError: Conflicting level bound` when a variable's `.l` (level) attribute is assigned multiple times with different conditions. GAMS allows this — later assignments overwrite earlier ones, and conditional assignments only apply to matching elements. The parser is too strict and rejects valid GAMS code.

---

## Reproduction

**Model:** `ganges` (`data/gamslib/raw/ganges.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/ganges.gms')"
```

**Error output:**
```
ParserSemanticError: Conflicting level bound for variable 'tw' at indices ('agricult',) [context: expression] (line 704, column 1)
```

**Model:** `gangesx` (`data/gamslib/raw/gangesx.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/gangesx.gms')"
```

**Error output:**
```
ParserSemanticError: Conflicting level bound for variable 'tw' at indices ('agricult',) [context: expression] (line 887, column 1)
```

---

## Root Cause

The GAMS source uses multiple conditional assignments to the same variable's `.l` attribute:

```gams
tw.l(sa) = 0;                       -- line 703 (ganges)
tw.l(i)$(not sa(i)) = 0.045;        -- line 704 (ganges)
```

The first line sets `tw.l` for all elements in subset `sa`. The second sets `tw.l` for elements in `i` that are NOT in `sa`. Since `sa` is a subset of `i`, the element `agricult` (which is in `sa`) was already assigned in line 703. When line 704 is processed, the parser's `_set_bound_value` method in `src/ir/parser.py` (around line 4681) detects that `tw.l('agricult')` already has a value and raises a "Conflicting level bound" error.

In GAMS, this is perfectly valid:
- Multiple `.l` assignments are allowed (last one wins for overlapping indices)
- Conditional assignments (`$(not sa(i))`) filter which elements are actually set
- The parser cannot statically resolve which elements a conditional applies to

The fix should either:
1. Allow repeated `.l` assignments (overwrite previous values), or
2. Only raise the error for unconditional duplicate assignments to the exact same indices

The relevant code is in `_set_bound_value` in `src/ir/parser.py` around line 4681.

---

## Context

This issue was exposed by the Issue #710 fix (model_ref_list whitespace separation) which advanced ganges and gangesx past their model statement parsing errors. Both models now parse their grammar correctly but hit this semantic validation error during IR construction.

The same pattern (`tw.l`, `tk.l`, `thetai.l`) appears multiple times in both models with conditional assignments to different subsets.
