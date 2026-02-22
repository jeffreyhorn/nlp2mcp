# Springchain: `$eval`/`$set` Compile-Time Macro Expansion Not Supported

**GitHub Issue:** [#841](https://github.com/jeffreyhorn/nlp2mcp/issues/841)
**Status:** OPEN
**Severity:** Medium — Model fails to parse entirely
**Date:** 2026-02-22
**Affected Models:** springchain

---

## Problem Summary

The springchain model (`data/gamslib/raw/springchain.gms`) fails to parse because it uses
GAMS compile-time directives `$set`, `$eval`, and `$if not set` to define macros that are
referenced throughout the model via `%N%` and `%NM1%` syntax. The preprocessor strips these
directives without executing them, so the `%` characters in macro references reach the lexer
and cause parse errors.

---

## Error Details

```
ParseError: Error: Parse error at line 36, column 45: Unexpected character: '%'
  m(n)  "mass of each hanging node"      /n1*n%NM1% 1/;
                                              ^

Suggestion: This character is not valid in this context
```

---

## Macro Definitions (raw file lines 21-22)

```gams
$if not set N $set N 10
$eval NM1 %N%-1
```

This defines:
- `%N%` = `10` (number of springs, user-settable via command line)
- `%NM1%` = `9` (N minus 1, computed by `$eval`)

---

## All Macro References (8 occurrences across 7 lines)

| Line | Raw GAMS Code | After Expansion |
|------|---------------|-----------------|
| 24 | `Set n "spring index" /n0*n%N%/;` | `/n0*n10/` |
| 31 | `[2*sqrt(sqr(a_x-b_x) + sqr(a_y-b_y))/%N%]` | `...)/10]` |
| 36 | `m(n) "mass of each hanging node" /n1*n%NM1% 1/;` | `/n1*n9 1/` |
| 72 | `x.L(n) = ( (ord(n)-1)/%N% )*b_x + (ord(n)/%N%)*a_x;` | `...)/10)*...` |
| 73 | `y.L(n) = ( (ord(n)-1)/%N% )*b_y + (ord(n)/%N%)*a_y;` | `...)/10)*...` |
| 77 | `x.FX['n%N%'] = b_x;` | `x.FX['n10'] = b_x;` |
| 78 | `y.FX['n%N%'] = b_y;` | `y.FX['n10'] = b_y;` |

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
ir = parse_file('data/gamslib/raw/springchain.gms')
"
```

---

## Root Cause

The preprocessor (`src/ir/preprocessor.py`) currently handles `$set` and `$if not set`
directives by stripping them (converting to comment lines). It does not:

1. **Execute `$set`**: Store the key-value pair for later `%macro%` expansion
2. **Execute `$if not set`**: Check if a macro is already defined before setting it
3. **Execute `$eval`**: Evaluate arithmetic expressions and store the result as a macro
4. **Expand `%macro%` references**: Replace `%name%` tokens with their stored values

---

## Suggested Fix

**Approach: Implement `$set`/`$eval`/`%macro%` expansion in the preprocessor**

1. **Macro store**: Add a `dict[str, str]` to the preprocessor to store macro key-value pairs.

2. **`$if not set` + `$set` handling**: When encountering `$if not set X $set X value`,
   check if `X` is already in the macro store; if not, store `X = value`.
   For standalone `$set X value`, always store `X = value`.

3. **`$eval` handling**: When encountering `$eval NAME expr`:
   - First expand any `%macro%` references in `expr` (e.g., `%N%-1` becomes `10-1`)
   - Evaluate the arithmetic expression (Python `eval()` with safe numeric context or
     a simple expression parser)
   - Store the result: `NAME = str(result)` (e.g., `NM1 = "9"`)

4. **`%macro%` expansion**: After processing all directives on a line, replace all
   `%name%` patterns with their values from the macro store. This should happen as
   a post-processing pass on each line after directive processing.

5. **Safety**: Use `ast.literal_eval` or a restricted evaluator for `$eval` expressions
   to prevent code injection. Only support basic arithmetic (`+`, `-`, `*`, `/`, `**`).

**Implementation sketch:**
```python
class Preprocessor:
    def __init__(self):
        self.macros: dict[str, str] = {}

    def _expand_macros(self, line: str) -> str:
        """Replace %name% with stored macro values."""
        def replace(m):
            name = m.group(1)
            return self.macros.get(name, m.group(0))  # leave unexpanded if unknown
        return re.sub(r'%(\w+)%', replace, line)

    def _handle_set(self, name: str, value: str) -> None:
        self.macros[name] = value

    def _handle_eval(self, name: str, expr: str) -> None:
        expanded = self._expand_macros(expr)
        result = _safe_eval(expanded)  # restricted arithmetic eval
        self.macros[name] = str(int(result) if result == int(result) else result)
```

**Effort estimate:** ~4-6h (includes testing, integration with existing directive handling)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/preprocessor.py` | Add macro store, `$set`/`$eval` execution, `%macro%` expansion |
| `tests/unit/ir/test_preprocessor.py` | Add tests for macro expansion |

---

## Related Issues

- Issue #837 — partially fixed (bracket expressions in scalar data), still blocked by this macro issue
- saras model — also blocked by macro expansion (`%system.nlp%`), though that's a simpler system-macro variant

---

## Note on Issue #837 Relationship

Issue #837 was filed for the bracket expression syntax `[expr]` in scalar data, which has
been fixed. The `$eval`/`$set` macro expansion is a separate, deeper issue that also blocks
springchain. This issue supersedes the remaining blocker described in #837.
