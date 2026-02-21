# mexls: `yes$(...)` Conditional Execution Not Supported

**GitHub Issue:** [#816](https://github.com/jeffreyhorn/nlp2mcp/issues/816)
**Model:** `mexls` (GAMSlib)
**Blocking Stage:** Parse (lexer_invalid_char at line 957/1088, 88%)
**Severity:** Medium — blocks full parse of mexls
**Date:** 2026-02-21

---

## Problem Summary

The grammar does not support `yes$(condition)` as a standalone statement or assignment value. GAMS uses `yes` as a special domain membership value, and `yes$(cond)` conditionally assigns domain membership. The parser fails when encountering `yes` as the start of a statement.

---

## Reproduction

### Failing GAMS Pattern (mexls.gms, lines 953–959)

```gams
mrpos(mr,ir) = yes$kr(mr,ir);
mspos(ms,is) = yes$ks(ms,is);

pmpos(pm,im)$sum(cm, am(cm,pm)$res(cm,im) <> 0 ) =
             yes$(sum(mm$(not mmpos(mm,im)), bm(mm,pm) <> 0) = 0);
prpos(pr,ir)$sum(cr, ar(cr,pr) <> 0 ) =
             yes$(sum(mr$(not mrpos(mr,ir)), br(mr,pr) <> 0) = 0);
```

### Error Output

```
Error: Parse error at line 957, column 1: Unexpected character: 'y'
  yes$(sum(mm$(not mmpos(mm,im)), bm(mm,pm) <> 0) = 0);
  ^
```

### Smoke Test Command

```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/mexls.gms')"
```

---

## Root Cause

`yes` is not recognized as a valid token or keyword in assignment RHS context. The grammar needs:

1. `yes` as a special value in assignment expressions (like `inf`, `eps`, `na`)
2. `yes$(condition)` as a conditional expression pattern
3. Multi-line conditional assignments where `yes$(...)` appears on a continuation line

---

## Suggested Fix

1. Add `YES_K` terminal: `/(?i:yes)\b/`
2. Allow `yes` and `no` as special values in `expr` or `atom` rules
3. Handle `yes$(condition)` as a conditional expression
4. May also need `no` as a special value (used in set membership)

### Files to Modify

- `src/gams/gams_grammar.lark` — add `YES_K`/`NO_K` terminals and grammar rules
- `src/ir/parser.py` — handle `yes`/`no` in expression evaluation
- `src/ir/preprocessor.py` — may need multi-line join support for `=\n yes$(...)`

---

## Impact

- Blocks: mexls full parse
- Related: Any GAMSlib model using `yes$()` or `no$()` conditional set membership patterns
