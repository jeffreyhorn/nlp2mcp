# Grammar: Model Equation List Allows Whitespace Separation (No Commas Between Lines)

**GitHub Issue:** [#710](https://github.com/jeffreyhorn/nlp2mcp/issues/710)

**Issue:** The `model_ref_list` grammar rule requires commas between all equation names, but GAMS allows whitespace (including newlines) as separators in model equation lists. Multi-line lists without trailing commas at line ends fail to parse.

**Status:** Open
**Severity:** Medium — Affects models with large equation lists spanning multiple lines
**Discovered:** 2026-02-13 (Sprint 19, after Issues #704/#705 fixes advanced ganges/gangesx past their original errors)
**Affected Models:** ganges (confirmed, line 1082), gangesx (confirmed, line 1368)

---

## Problem Summary

GAMS model statements list equation names inside `/ ... /` delimiters. These lists can use commas, whitespace, or both as separators. Our grammar requires commas:

```lark
model_ref_list: ID ("," ID)*
```

But GAMS source files commonly use multi-line lists where the last identifier on a line is NOT followed by a comma, relying on newline + whitespace to separate from the next line's identifiers:

```gams
Model ganges 'basic version of the India cge'
      / infalloc, wdet,    valueq,  prodq,   firstq,  supply,  pmdef
        taumdet,  valuex,  prodx,   firstx,  valuez,  prodz,   firstz
        ...
        export,   equil,   margdet, fbudget, invsav,  utildef, obj    /
```

Note: `pmdef` at end of line 1 has NO trailing comma, and `taumdet` starts line 2.

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
Error: Parse error at line 1082, column 1: Unexpected character: 't'
  taumdet,  valuex,  prodx,   firstx,  valuez,  prodz,   firstz
  ^
```

**Model:** `gangesx` (`data/gamslib/raw/gangesx.gms`)

**Command to reproduce:**
```bash
source .venv/bin/activate
python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/gangesx.gms')"
```

**Error output:**
```
Error: Parse error at line 1368, column 1: Unexpected character: 'v'
  valuex,   prodx,   firstx,  valuez,  prodz,   firstz,  valuen,  prodn
  ^
```

---

## Root Cause

The `model_ref_list` rule in `src/gams/gams_grammar.lark` (line 396):

```lark
model_ref_list: ID ("," ID)*
```

This requires commas between all identifiers. GAMS allows both comma and whitespace separation within `/ ... /` delimiters in model statements.

---

## Proposed Fix

Change the `model_ref_list` rule to allow optional commas:

```lark
model_ref_list: ID (","? ID)*
```

Or equivalently, use a simpler pattern:

```lark
model_ref_list: ID+
```

Note: The `+` approach works because the `/` delimiter terminates the list, so there's no ambiguity. Commas within the list are optional in GAMS.

The parser handler for `model_ref_list` may need minor updates if it relies on comma tokens being present.

---

## Context

This issue was exposed by the Sprint 19 fixes for Issues #704 (table negative number) and #705 (assignment dollar conditional with suffix) which advanced ganges and gangesx past their earlier errors. Both models now parse through their table data and assignment sections but fail when they reach the `Model` statement with multi-line equation lists.
