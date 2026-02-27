# danwolfe: Parse Error — GAMS Async Grid Computing Functions

**GitHub Issue:** [#955](https://github.com/jeffreyhorn/nlp2mcp/issues/955)
**Status:** OPEN
**Severity:** Medium — Model partially parses but fails at async grid section
**Date:** 2026-02-27
**Affected Models:** danwolfe (potentially other models using GAMS grid computing)
**Sprint:** 21

---

## Problem Summary

The `danwolfe.gms` model (Dantzig-Wolfe decomposition) fails to parse at line 219 due to unrecognized GAMS async grid computing functions: `handlecollect`, `handledelete`, `sleep`, and `timeelapsed`.

After fixing the initial blockers in PR #954 (`uniformInt`, `while` statement, `display$condition`, indexed loop filter, `%solPrint.*` macros), the parser now reaches line 219 where a `repeat...until` block uses these grid computing intrinsics.

---

## Error Details

```
Parse error at line 219, column 1: Unexpected character: ')'
  );
  ^
```

The parser fails inside the grid async section (lines 190–219) which uses:

```gams
   repeat
      loop(k$h(k),
         if(handlecollect(h(k)),            ← line 203: not recognized
            if(mdefbal.m(k) - z.l > 1e-6,
               ap(nextp(k,p))    = yes;
               pe(nextp(k,p),e)  = round(xe.l(e));
               pcost(nextp(k,p)) = sum(pe(nextp,e), cost(e));
               nextp(k,p)        = nextp(k,p-1);
               abort$(sum(nextp(k,p),1) = 0) 'set p too small';
               done = 0;
            );
            display$handledelete(h(k)) 'trouble deleting handles' ;  ← line 212
            h(k) = 0;
         );
      );
      display$sleep(card(h)*0.1) 'sleep a bit';  ← line 216
   until card(h) = 0 or timeelapsed > %maxtime%;  ← line 217: timeelapsed not recognized
);  ← line 219: unexpected closing paren
```

---

## Root Cause

The parser/grammar lacks support for four GAMS async grid computing functions:

1. **`handlecollect(handle)`** — Checks if an async solve handle has completed. Returns 1 if data ready to collect.
2. **`handledelete(handle)`** — Deletes/frees an async handle after collection. Returns 1 on success.
3. **`sleep(seconds)`** — Pauses execution for specified seconds. Returns 1.
4. **`timeelapsed`** — Built-in scalar tracking elapsed wall-clock time since job start.

These functions are used in the grid async version of the Dantzig-Wolfe algorithm (lines 190–219) to:
- Submit pricing solves in parallel via `solveLink = %solveLink.asyncGrid%`
- Poll results using `repeat...until` with `handlecollect`
- Avoid busy-waiting with `sleep`
- Enforce max runtime with `timeelapsed`

Additionally, the `repeat...until` loop construct is not supported by the grammar.

---

## Proposed Fix

### Option A: Add grid functions + repeat/until (full support)

1. Add `handlecollect`, `handledelete`, `sleep` to `FUNCNAME` in `src/gams/gams_grammar.lark`
2. Add `timeelapsed` as a recognized built-in scalar (or to `FUNCNAME` with 0-arg support)
3. Add `repeat_stmt` grammar rule: `REPEAT_K loop_body UNTIL_K expr SEMI`
4. Add parser handler `_handle_repeat_stmt()`

**Estimated effort:** 3–4h

### Option B: Preprocess out the grid section (workaround)

The model has both serial and grid versions of the algorithm, controlled by `%solveLink%`:
- Serial version: lines 150–167
- Grid async version: lines 190–219

Could strip the grid section in the preprocessor and keep only the serial path.

**Estimated effort:** 1–2h (but fragile and model-specific)

### Recommendation

Option A is preferred for generality, as other GAMSlib models may use these grid functions.

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file

try:
    m = parse_model_file('data/gamslib/raw/danwolfe.gms')
    print(f"Parse success: {len(m.variables)} variables, {len(m.equations)} equations")
except Exception as e:
    print(f"Parse error: {e}")
# → Parse error at line 219, column 1: Unexpected character: ')'
```

---

## GAMS Source Context

### Grid async section (lines 190–219):
```gams
*  Parallel version - submit all subproblems to the grid
   solve submod using lp min xe min;
   repeat
      loop(k$h(k),
         if(handlecollect(h(k)),
            if(mdefbal.m(k) - z.l > 1e-6,
               ap(nextp(k,p))    = yes;
               pe(nextp(k,p),e)  = round(xe.l(e));
               pcost(nextp(k,p)) = sum(pe(nextp,e), cost(e));
               nextp(k,p)        = nextp(k,p-1);
               abort$(sum(nextp(k,p),1) = 0) 'set p too small';
               done = 0;
            );
            display$handledelete(h(k)) 'trouble deleting handles' ;
            h(k) = 0;
         );
      );
      display$sleep(card(h)*0.1) 'sleep a bit';
   until card(h) = 0 or timeelapsed > %maxtime%;
);
```

### Serial version (lines 150–167):
```gams
*  Serial version - solve subproblems one at a time
   loop(k,
      solve submod using lp min xe min;
      if(mdefbal.m(k) - z.l > 1e-6,
         ...
      );
   );
```

---

## Related Issues

- PR #954: Fixed initial danwolfe blockers (uniformInt, while, display$cond, indexed loop filter, macros)
- Issue #889: Original danwolfe tracking issue (partially resolved)
