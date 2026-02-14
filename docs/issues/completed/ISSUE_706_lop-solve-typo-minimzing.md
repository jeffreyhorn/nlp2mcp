# lop Model: Typo in Solve Statement ("minimzing" instead of "minimizing")

**GitHub Issue:** [#706](https://github.com/jeffreyhorn/nlp2mcp/issues/706)

**Issue:** The `lop` gamslib model contains a typo on line 149: `minimzing` instead of `minimizing` in a solve statement. The parser correctly rejects this as an unrecognized keyword. This is a source data issue, not a parser bug.

**Status:** Fixed
**Severity:** Low — Source data typo in a single model; requires a workaround or source correction
**Discovered:** 2026-02-13 (Sprint 19 Day 1, after Subcategory G grammar fix advanced lop past its original set element description error)
**Affected Models:** lop

---

## Problem Summary

The `lop` model has a misspelling in its solve statement. GAMS itself may tolerate this typo (GAMS has flexible keyword matching), but our parser requires exact keyword matching for `minimizing`/`maximizing`.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Failing line (149/151 — the model has two solve statements):**
```gams
Model sp 'shortest path model' / balance, defspobj /;

solve sp minimzing spobj using lp;
```

The word `minimzing` is missing the second `i` (`minim_z_ing` instead of `minim_iz_ing`).

**Command to reproduce:**
```bash
.venv/bin/python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/lop.gms')"
```

**Error output:**
```
Error: Parse error at line 149, column 10: Unexpected character: 'm'
  solve sp minimzing spobj using lp;
           ^
```

---

## Root Cause

The `solve_stmt` rule in `gams_grammar.lark` uses `MINIMIZING_K` and `MAXIMIZING_K` keywords which match exact spellings (case-insensitive). The typo `minimzing` doesn't match `minimizing`.

```lark
solve_stmt: "Solve"i ID obj_sense ID "using"i solver_type SEMI
obj_sense: MINIMIZING_K | MAXIMIZING_K
```

Where `MINIMIZING_K` likely matches `/minimiz(e|ing)/i` or similar.

---

## Possible Fixes

**Option A: Fix the source data** (recommended)
Create a corrected copy of `lop.gms` with `minimizing` spelled correctly. This is the cleanest fix since the typo is in the upstream gamslib source.

**Option B: Add typo tolerance to solve keyword**
Extend `MINIMIZING_K` to also match `minimzing`:
```lark
MINIMIZING_K: /minimi[sz]ing/i
```
This is fragile and sets a bad precedent for accommodating typos.

**Option C: Preprocessing step**
Add a preprocessing pass that corrects known typos in gamslib models before parsing.

---

## Context

This issue was exposed by the Sprint 19 Day 1 grammar fix that added `NUMBER STRING -> set_element_with_desc` support. The lop model previously failed at its set element description (`1 'every 60 minutes'`). With that fix, it now parses 148 lines before hitting this typo in the solve statement.

The lop model also contains a second solve statement later in the file (`solve minlop ...`) which may have additional issues.

---

## Fix Details

**Fixed in:** Sprint 19 (branch `sprint19-fix-issues-703-706`)

Used Option B (typo tolerance) after testing GAMS's actual keyword matching behavior. GAMS 51.3.0 accepts any word starting with `min` (at least 3 chars) as a minimize directive, and any word starting with `max` as maximize. For example: `min`, `minimize`, `minimizing`, `minimzing`, `minfoo` all work. Updated `MINIMIZING_K` and `MAXIMIZING_K` terminals in `src/gams/gams_grammar.lark` to match this behavior:

```lark
MINIMIZING_K: /(?i:min)\w*/
MAXIMIZING_K: /(?i:max)\w*/
```

**Verification:** `lop.gms` now parses past line 149 (hits a new unrelated error at line 176 — dollar conditional in loop domain).
