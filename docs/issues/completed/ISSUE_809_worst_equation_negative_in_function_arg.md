# Equation Definition: Negative Sign in Function Argument Not Recognized

**GitHub Issue:** [#809](https://github.com/jeffreyhorn/nlp2mcp/issues/809)

## Issue Type
Parser Error

## Affected Models
- worst (GAMSlib model)

## Description
GAMS allows negative signs in function arguments within equation definitions, such as:

```gams
equation.. expr =e= func(-arg1) - func(-arg2);
```

The parser fails to recognize the second minus sign (before `d1(i,t,j)`), treating it as an unexpected character instead of a unary minus operator in the function argument.

## Error Details

### worst
```
Error: Parse error at line 99, column 118: Unexpected character: '-'
  putval(i,t,j)$(pdata(i,t,j,"type") eq puto).. p(i,j,t)  =e= exp(-r(t)*tdata(t,"term"))*(pdata(i,t,j,"strike")*errorf(-d2(i,t,j)) -  f(i,t)*errorf(-d1(i,t,j)));
                                                                                                                       ^
```

Full equation:
```gams
putval(i,t,j)$(pdata(i,t,j,"type") eq puto).. 
   p(i,j,t) =e= exp(-r(t)*tdata(t,"term")) * (
      pdata(i,t,j,"strike")*errorf(-d2(i,t,j)) 
      - f(i,t)*errorf(-d1(i,t,j))
   );
```

The error points to the second `-` before `d1(i,t,j)`.

## Root Cause Analysis

The parser successfully handles:
1. `exp(-r(t)*tdata(t,"term"))` - negative in first function argument
2. `errorf(-d2(i,t,j))` - negative in first errorf call

But fails on:
3. `errorf(-d1(i,t,j))` - negative in second errorf call after binary minus operator

This suggests a context-dependent parsing issue where the grammar doesn't properly handle a unary minus following a binary minus operator in nested function calls.

Possible causes:
- Precedence/associativity issue in the expression grammar
- Look-ahead ambiguity between binary minus and unary minus
- Token stream issue where `- -` (binary minus followed by unary minus) isn't being parsed correctly

## Reproduction
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/worst.gms')"
```

Minimal reproduction:
```gams
Variables x, y;
Equations eq;
eq.. x =e= func(-y) - func(-y);
```

Or more specifically:
```gams
Variables x, y, z;
Equations eq;
eq.. x =e= y*func(-z) - y*func(-z);
```

## Expected Behavior
The parser should correctly handle unary minus in function arguments even when preceded by binary operators.

## Investigation Needed

1. Check expression grammar in `src/gams/gams_grammar.lark`:
   - `arith_expr` rule (handles binary +/-)
   - `factor` rule (handles unary +/-)
   - Interaction between binary and unary operators

2. Check if whitespace affects parsing:
   - Does `- func(-)` parse differently than `-func(-)`?
   - Is there a tokenization issue with adjacent minus signs?

3. Test simpler cases:
   - `x =e= -func(-y);` (unary minus of function call)
   - `x =e= y - (-z);` (binary minus with parenthesized unary minus)
   - `x =e= y - -z;` (binary minus with unary minus, no parens)

## Proposed Investigation Steps

1. Create unit test with minimal reproduction case
2. Enable Lark debug output to see token stream
3. Check if adding parentheses fixes it: `- (f(i,t)*errorf(-d1(i,t,j)))`
4. Check if spacing affects it: `- f(i,t)*errorf(-d1(i,t,j))`

## Related
- May be related to Issue #780 (IndexOffset parameter references) if the issue is about handling complex nested expressions
- Similar to adjacent operator issues resolved in Sprint 20 Day 3 (PR #805) for IndexOffset expressions

## Files to Review
- `src/gams/gams_grammar.lark` (expression grammar, especially arith_expr, factor, atom)
- `src/ir/parser.py` (expression builders)

## Test Case
```gams
Variables x, y, z;
Parameters a, b;
Equations test1, test2, test3;

test1.. x =e= exp(-a) - exp(-b);
test2.. x =e= y*func(-z) - y*func(-z);
test3.. x =e= (a*errorf(-b)) - (a*errorf(-b));
```

## Priority
Medium - affects 1 GAMSlib model (worst). Acronym declaration now parses correctly after Sprint 20 Day 4, but equation definition fails.

## Sprint Context
Discovered during Sprint 20 Day 4 (WS3 Lexer Phase 1) after fixing Subcat M Acronym declaration. The Acronym declaration now parses successfully, but the model fails later at an equation definition with complex nested function calls.

## Resolution

**Status:** FIXED

### Root Cause (Corrected)
The issue was NOT about unary minus handling or operator precedence. The actual root cause was that `errorf` (the GAMS error function / normal CDF) was missing from the `FUNCNAME` terminal regex. Without `FUNCNAME` recognition, `errorf(...)` was parsed as an indexed reference (`ref_indexed`), which doesn't allow unary minus inside its argument list. Adding `errorf` to `FUNCNAME` allows it to be parsed as a proper `func_call` with full expression support in arguments.

### Changes
1. **`src/gams/gams_grammar.lark`**: Added `errorf` to the `FUNCNAME` terminal regex.
2. **`tests/unit/test_issue_fixes_807_808_809.py`**: Added 3 unit tests covering `errorf(x)`, `errorf(-x)`, and `a*errorf(-b) - c*errorf(-d)`.

### Verification
- `worst.gms` now parses successfully.
- 3,622 tests pass, 10 skipped, 2 xfailed.
