# ISSUE #1772 — emfl: inline-guarded `$eval` does not define `%new%` (it reaches the lexer)

**GitHub:** [#1772](https://github.com/jeffreyhorn/nlp2mcp/issues/1772) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** P3 parse (Sprint 40 P3 routing note) · **Model:** `emfl` (NLP-gated, `likely_convex`, admitted by rule Sprint 40 Day 3) · **Measured at:** `de0a7186`

## Fingerprint (reproduced)

`parse: failure`, `lexer_invalid_char`:

```
Parse error at line 36, column 46: Unexpected character: '%'
  n  'total number of new facilities'    / n1*n%new%  /
```

`%new%` is never defined, because its `$eval` is **inline, behind a conditional**:

```gams
$if not set N1  $set N1    5
$if not set N2  $set N2    5
$if not set N   $eval new  %N1%*%N2%
```

`%old%`, `%N1%` and `%N2%` expand. `%new%` stays literal and reaches the lexer.

## Diagnosis (corrected in PR #1777 review)

**`$eval` itself is already supported:** `extract_eval_directives` (`src/ir/preprocessor.py`, Sprint 21 Day 3) is covered by `tests/unit/ir/test_preprocessor.py::TestEvalDirective`. The missed case is narrower:
- `extract_eval_directives` matches only a **line-leading** `$eval` (`^\s*\$eval\s+(\w+)…`), so `$if not set N $eval new …` never matches;
- it runs at Step 2a of the pipeline, **before** `process_conditionals` (Step 3);
- Step 1, `extract_conditional_sets`, recognizes `$if not set X $set X …` but not a `$eval` behind the condition.

## Fix direction

Handle the inline form in the **conditional-directive processing** (`extract_conditional_sets` / `process_conditionals`), reusing the existing evaluator (`_safe_eval_arithmetic`). Do not implement `$eval` a second time.
- The condition (`not set N`) must be honoured: evaluate only when it holds.
- A result `_safe_eval_arithmetic` cannot evaluate should fail loudly, not stay literal.

**Reach in the corpus:** the inline form appears in **`emfl`** and in **`srpchase`** (`$ifE mod(%DIM%,2)=1 $eval DIM %DIM%+1`). srpchase parses today, so its inline `$eval` is skipped **silently**. That is harmless only while `%DIM%` is already odd. Check srpchase's `DIM` after the fix. The line-leading form (supported) appears in `gqapsdp`, `spbenders4` and `springchain`.

**Not fixed in place.**
