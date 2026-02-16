# File Handle 'sol' Not Declared — Attribute Access Validation Fails for GAMS File Symbols

**GitHub Issue:** [#746](https://github.com/jeffreyhorn/nlp2mcp/issues/746)
**Status:** Open
**Severity:** Medium — Blocks full pipeline for 3 NLP models with post-solve CSV output
**Discovered:** 2026-02-13 (Sprint 19 Day 2, after put format fix in PR #745)
**Affected Models:** ps5_s_mn, ps10_s, ps10_s_mn

---

## Problem Summary

Three Parts Supply models (ps5_s_mn, ps10_s, ps10_s_mn) fail during IR parsing with `Symbol 'sol' not declared as a variable, parameter, equation, or model`. The symbol `sol` is a GAMS `File` handle declared with `File sol /solution_lic.csv/;` and used for post-solve CSV output via `put` statements. The grammar parses the `file_stmt` rule correctly, but the IR parser has no handler for `file_stmt` nodes — the file handle is never registered in any symbol table. When subsequent attribute assignments like `sol.pc = 5;` are encountered, the attribute access validation in `src/ir/parser.py` checks variables, parameters, equations, and models but not file handles, causing the validation error.

---

## Reproduction

**Models:** ps5_s_mn (SEQ=286), ps10_s (SEQ=274), ps10_s_mn (SEQ=275)

**Command:**
```bash
python -m src.cli data/gamslib/raw/ps5_s_mn.gms --diagnostics
python -m src.cli data/gamslib/raw/ps10_s.gms --diagnostics
python -m src.cli data/gamslib/raw/ps10_s_mn.gms --diagnostics
```

**Error output (ps5_s_mn):**
```
Error: Invalid model - Symbol 'sol' not declared as a variable, parameter, equation, or model [context: expression] (line 130, column 1)
```

**Error output (ps10_s):**
```
Error: Invalid model - Symbol 'sol' not declared as a variable, parameter, equation, or model [context: expression] (line 59, column 1)
```

**Error output (ps10_s_mn):**
```
Error: Invalid model - Symbol 'sol' not declared as a variable, parameter, equation, or model [context: expression] (line 129, column 1)
```

**GAMS source context (ps5_s_mn, lines 127–131):**
```gams
File sol /solution_lic.csv/;
put  sol;

sol.pc =     5;    ← ERROR: 'sol' not recognized
sol.pw = 32767;
```

---

## Root Cause

### Grammar level (working correctly)

The grammar at `src/gams/gams_grammar.lark` line 488 defines:
```lark
file_stmt: "file"i ID "/" file_path "/" SEMI
```

This correctly parses `File sol /solution_lic.csv/;` into a `file_stmt` AST node.

### IR parser level (missing handler)

The IR parser at `src/ir/parser.py` has no handler for `file_stmt` tree nodes. When the Lark tree is walked during IR construction, `file_stmt` nodes are silently skipped. The file handle name `sol` is never added to any symbol table (not `model.variables`, `model.params`, `model.equations`, or `model.declared_models`).

### Validation level (triggers the error)

When `sol.pc = 5;` is parsed as an `attr_access` node, the validation at `src/ir/parser.py:3260–3270` checks:
```python
if (
    base_name not in self.model.variables
    and base_name not in self.model.params
    and base_name not in self.model.equations
    and base_name.lower() not in self.model.declared_models
):
    raise self._error(
        f"Symbol '{base_name}' not declared as a variable, parameter, equation, or model",
        target,
    )
```

Since `sol` is not in any of these tables, the error is raised.

---

## Fix Approach

### Option A: Track file handles in a `declared_files` set (Recommended)

Add a `declared_files: set[str]` field to the model IR. When a `file_stmt` node is encountered, add the file handle name to `declared_files`. Update the attribute access validation to also check `declared_files`:

```python
if (
    base_name not in self.model.variables
    and base_name not in self.model.params
    and base_name not in self.model.equations
    and base_name.lower() not in self.model.declared_models
    and base_name not in self.model.declared_files  # NEW
):
    raise self._error(...)
```

File handle attribute assignments (`sol.pc`, `sol.pw`, etc.) and `put` statements referencing file handles should be silently skipped (they are I/O operations irrelevant to the NLP→MCP transformation).

**Complexity:** Low. Add one set, one handler, one validation check.

### Option B: Skip file_stmt and all subsequent file handle references

Instead of tracking file handles, detect `file_stmt` in the grammar output and skip the entire block of file I/O operations (all `put` statements and attribute assignments on file handles). This is more complex because it requires look-ahead or block detection.

**Complexity:** Medium. More fragile.

### Recommended approach

Option A is simpler and more robust. The `File` declaration is the canonical signal that a symbol is a file handle, and tracking it in the IR allows all downstream validation to work correctly.

---

## Relevant Files

- `src/gams/gams_grammar.lark:488` — `file_stmt` grammar rule (working correctly)
- `src/ir/parser.py:3260–3270` — Attribute access validation (needs `declared_files` check)
- `src/ir/parser.py` — Needs `file_stmt` handler to register file handle names
- `data/gamslib/raw/ps5_s_mn.gms:127` — `File sol /solution_lic.csv/;`
- `data/gamslib/raw/ps10_s.gms:57` — `File sol / solution_lic.csv /;`
- `data/gamslib/raw/ps10_s_mn.gms:127` — `File sol / solution_lic.csv /;`

---

## Related Issues

- [#747](https://github.com/jeffreyhorn/nlp2mcp/issues/747) — stdcge `listA1out` file handle issue (same root cause, different file handle name)
