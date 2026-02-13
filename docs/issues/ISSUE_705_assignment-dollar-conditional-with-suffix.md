# Assignment Dollar Conditional with .l/.m/.lo/.up Suffix Access

**GitHub Issue:** [#705](https://github.com/jeffreyhorn/nlp2mcp/issues/705)

**Issue:** The parser cannot handle assignment statements where a dollar conditional references a variable with a GAMS suffix (`.l`, `.m`, `.lo`, `.up`), e.g., `deltas(i)$ls.l(i) = ...`. The `.l` suffix accesses the level value of variable `ls`.

**Status:** Open
**Severity:** Medium — `.l` suffix access is widespread in GAMS models (30+ models use `.l(`)
**Discovered:** 2026-02-13 (Sprint 19 Day 1, after Subcategory G grammar fix advanced gangesx past its original set element description error)
**Affected Models:** gangesx (confirmed at line 784)

---

## Problem Summary

GAMS variables have suffixes that access different attributes: `.l` (level/solution value), `.m` (marginal), `.lo` (lower bound), `.up` (upper bound), `.fx` (fixed value). These suffixes can appear in dollar conditionals on assignment statements:

```gams
deltas(i)$ls.l(i) = (k(i)/ls.l(i))**(1/sigmas(i))*pk.l(i)/sum(r$ri(r,i), pls.l(r));
```

Here `$ls.l(i)` means "only assign `deltas(i)` where `ls.l(i)` is nonzero". The parser fails because it doesn't recognize `ls.l(i)` as a valid expression after `$` in the assignment context.

---

## Reproduction

**Model:** `gangesx` (`data/gamslib/raw/gangesx.gms`)

**Failing line (784):**
```gams
deltas(i)$ls.l(i)       = deltas(i)/(1 + deltas(i));
```

**Context (lines 783-786):**
```gams
deltas(i)$ls.l(i)       =  (k(i)/ls.l(i))**(1/sigmas(i))*pk.l(i)/sum(r$ri(r,i), pls.l(r));
deltas(i)$ls.l(i)       = deltas(i)/(1 + deltas(i));
deltas(i)$(not ls.l(i)) = 1;
```

Note: Line 785 uses `$(not ls.l(i))` with parentheses — this form may already work. The bare `$ls.l(i)` on line 784 is the failing form.

**Command to reproduce:**
```bash
.venv/bin/python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/gangesx.gms')"
```

**Error output:**
```
Error: Parse error at line 784, column 1: Unexpected character: 'd'
  deltas(i)$ls.l(i)       = deltas(i)/(1 + deltas(i));
  ^
```

---

## Root Cause

Two overlapping grammar issues:

1. **Bare dollar conditional on assignments:** Similar to Issue #703 (equation dollar conditionals), assignment statements may not support the bare `$identifier(args)` form without enclosing parentheses. The grammar's `condition` rule requires `$(expr)` or `$[expr]`.

2. **Suffix access in expressions:** The `.l` suffix on `ls.l(i)` is an attribute access pattern (`variable.suffix(indices)`). The grammar may not fully support this in all expression contexts, particularly after `$`.

The combination means `$ls.l(i)` fails on two fronts: (a) no enclosing parens on the `$`, and (b) the `.l` suffix access pattern.

---

## Proposed Fix

1. Extend the `condition` rule to handle bare dollar conditionals (same as Issue #703 fix).
2. Ensure the expression grammar supports `ID "." SUFFIX "(" args ")"` as a valid expression form, where SUFFIX is one of `l`, `m`, `lo`, `up`, `fx`, `scale`, `prior`, `stage`.

---

## Affected Models

The `.l(` suffix pattern appears in 30+ gamslib models. Not all will fail on this specific issue (many may have other errors first), but this is a common GAMS idiom that needs support for broad compatibility.

---

## Context

This issue was exposed by the Sprint 19 Day 1 grammar fix that added `NUMBER STRING -> set_element_with_desc` support. The gangesx model previously failed at its set element description. With that fix, it now parses 783 lines before hitting this assignment dollar conditional with suffix issue.

## Related Issues

- Issue #703: Equation dollar conditional without enclosing parentheses (same bare `$` pattern, different context)
