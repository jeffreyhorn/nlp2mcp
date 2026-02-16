# File Handle 'listA1out' Not Declared — Attribute Access Validation Fails for GAMS File Symbols

**GitHub Issue:** [#747](https://github.com/jeffreyhorn/nlp2mcp/issues/747)
**Status:** Fixed
**Severity:** Medium — Blocks full pipeline for 1 NLP model (stdcge) with post-solve CSV output
**Discovered:** 2026-02-13 (Sprint 19 Day 2, after put format fix in PR #745)
**Affected Models:** stdcge

---

## Problem Summary

The Standard CGE Model (stdcge) fails during IR parsing with `Symbol 'listA1out' not declared as a variable, parameter, equation, or model`. The symbol `listA1out` is a GAMS `File` handle declared with `File listA1out / listA1.csv /;` and used for post-solve CSV output via `put` statements. The grammar parses the `file_stmt` rule correctly, but the IR parser has no handler for `file_stmt` nodes — the file handle is never registered in any symbol table. When the attribute assignment `listA1out.pc=5;` is encountered, the attribute access validation fails because file handles are not tracked.

This is the same root cause as the `sol` file handle issue affecting ps5_s_mn, ps10_s, and ps10_s_mn.

---

## Reproduction

**Model:** stdcge (SEQ=359) — A Standard CGE Model

**Command:**
```bash
python -m src.cli data/gamslib/raw/stdcge.gms --diagnostics
```

**Error output:**
```
Error: Invalid model - Symbol 'listA1out' not declared as a variable, parameter, equation, or model [context: expression] (line 368, column 1)
```

**GAMS source context (stdcge.gms, lines 365–370):**
```gams
File listA1out / listA1.csv /;
put  listA1out;

listA1out.pc=5;    ← ERROR: 'listA1out' not recognized
```

**Post-solve output section (lines 365–391):**
```gams
* List A.1: an example of CSV file generation
File listA1out / listA1.csv /;
put  listA1out;

listA1out.pc=5;

* putting a note
put "This is an example of usage of the Put command." / /;

* putting dXp(i)
put "dXp(i)" /;
loop(i, put i.tl dXp(i) /;);
put / /;

* putting dTd
put "dTd" dTd /;
put / /;

* putting F(h,j)
put "F(h,j)" /;
put "";
loop(j, put j.tl);
put /;
```

### Model characteristics

stdcge is a Computable General Equilibrium (CGE) model that uses MPSGE (Mathematical Programming System for General Equilibrium) syntax embedded in `$ontext..$offtext` blocks and processed via `$sysinclude mpsgeset`. The NLP formulation uses 3 sectors, 2 households, 1 government entity, and 2 factors. The model solves correctly in GAMS and is classified as `likely_convex` in gamslib_status.json.

---

## Root Cause

Identical to the `sol` file handle issue:

1. **Grammar level** — `file_stmt` rule at `src/gams/gams_grammar.lark:488` correctly parses `File listA1out / listA1.csv /;`
2. **IR parser level** — No handler for `file_stmt` nodes in `src/ir/parser.py`; the file handle name `listA1out` is never registered
3. **Validation level** — `src/ir/parser.py:3260–3270` checks `attr_access` targets against variables, parameters, equations, and models — but not file handles

---

## Fix Approach

Same fix as the `sol` file handle issue: add a `declared_files` set to the model IR, register file handle names from `file_stmt` nodes, and update the attribute access validation to check `declared_files`.

See the companion issue (file-handle-sol-not-declared.md) for detailed fix options.

---

## Relevant Files

- `src/gams/gams_grammar.lark:488` — `file_stmt` grammar rule
- `src/ir/parser.py:3260–3270` — Attribute access validation
- `data/gamslib/raw/stdcge.gms:365` — `File listA1out / listA1.csv /;`

---

## Fix Details

Fixed by the same change as #746. The `declared_files` set in `ModelIR` and the `_handle_file_stmt()` handler in the IR parser now register all GAMS `File` handle names, including `listA1out`. The attribute access validation checks `declared_files` so `listA1out.pc=5;` passes validation.

**Result:** stdcge now passes through the full pipeline without the `listA1out` validation error. Quality gate: 3390 tests passed, 0 failures.

---

## Related Issues

- [#746](https://github.com/jeffreyhorn/nlp2mcp/issues/746) — ps5_s_mn, ps10_s, ps10_s_mn `sol` file handle issue (same root cause, same fix)
