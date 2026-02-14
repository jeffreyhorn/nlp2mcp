# Grammar: Dollar Conditional in Loop Domain

**GitHub Issue:** [#711](https://github.com/jeffreyhorn/nlp2mcp/issues/711)

**Issue:** The parser cannot handle dollar conditionals inside a `loop()` domain specification, e.g., `loop(r$(ord(r) > 1 and card(unvisit)), ...)`. The `$` after the loop index variable is not recognized in this context.

**Status:** Completed
**Severity:** Medium — Loop domain filtering with `$` is a common GAMS pattern
**Discovered:** 2026-02-13 (Sprint 19, after Issue #706 fix advanced lop past its solve keyword typo)
**Fixed:** 2026-02-13 (Sprint 19)
**Affected Models:** lop (confirmed, line 176)

---

## Problem Summary

GAMS `loop()` statements can filter the loop domain using dollar conditionals:

```gams
loop(r$(condition), body);
```

The grammar already had `loop_stmt_filtered` rules to handle this at the top level, but the failure occurred because the filtered loop appeared *inside another loop* (nested). The `exec_stmt` and `exec_stmt_final` rules (which define what can appear inside loop/if bodies) did not include `loop_stmt` or `if_stmt`, so nested loops and nested if statements were not supported.

---

## Root Cause

The `exec_stmt` and `exec_stmt_final` rules in `src/gams/gams_grammar.lark` listed all statement types that could appear inside loop/if bodies, but omitted `loop_stmt` and `if_stmt`. This prevented any nested loop or if statement from parsing, including the `loop(r$(ord(r) > 1 and card(unvisit)), ...)` inside the outer `loop(root, ...)` in the lop model.

---

## Fix Applied

Added `loop_stmt` and `if_stmt` to both `exec_stmt` and `exec_stmt_final` rules in `src/gams/gams_grammar.lark`:

```lark
?exec_stmt: ...
          | loop_stmt            // Sprint 19: Support nested loops
          | if_stmt              // Sprint 19: Support nested if statements
          | assignment_stmt
          | SEMI

?exec_stmt_final: ...
                | loop_stmt      // Sprint 19: Support nested loops
                | if_stmt        // Sprint 19: Support nested if statements
                | SEMI
```

No parser handler changes were needed — `_handle_loop_stmt` already handles all loop variants, and nested loops/ifs inside loop bodies are automatically dispatched through the existing tree-walking mechanism.

**Verification:**
- lop now parses past line 176 (the nested loop with dollar conditional)
- lop hits a new, unrelated error at line 208 (`Set` statement after the loop block — separate issue)
- Nested loops (2-deep, 3-deep), nested loops with dollar filters, and nested if statements all parse correctly

**Quality gate:** All 3299 tests pass. Typecheck, lint, and format all clean.
