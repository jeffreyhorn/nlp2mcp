# Issue: Parser Does Not Handle Multi-Line Statement Continuation

**Status:** Open
**Category:** Parser Limitation
**Affected Models:** camcge, and potentially many of the 74 `lexer_invalid_char` failures
**Priority:** High
**GitHub Issue:** #636 (https://github.com/jeffreyhorn/nlp2mcp/issues/636)

## Summary

The nlp2mcp parser fails on valid GAMS statements that span multiple lines. GAMS allows expressions to continue across line boundaries without explicit continuation characters, but the nlp2mcp parser appears to treat each line independently, causing parse failures when parentheses are unbalanced within a single line but balanced across the full statement.

## Reproduction

**Model:** `data/gamslib/raw/camcge.gms`

**Source lines 212-213:**
```gams
at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it))
       * xxd0(it)**rhot(it))**(1/rhot(it));
```

**nlp2mcp Error:**
```
Error: Parse error at line 212, column 63: Unexpected character: ';'
  at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it));
                                                                ^

Suggestion: This character is not valid in this context
```

**GAMS Compilation:** Successful (exit code 0)
```bash
$ gams camcge.gms action=c lo=0
$ echo $?
0
```

## Root Cause Analysis

### The Statement is Valid GAMS

The expression spans two lines:
- **Line 212:** `at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it))`
- **Line 213:** `       * xxd0(it)**rhot(it))**(1/rhot(it));`

**Parentheses count:**
| Scope | Opening `(` | Closing `)` | Balance |
|-------|-------------|-------------|---------|
| Line 212 alone | 8 | 7 | +1 (unbalanced) |
| Line 213 alone | 4 | 5 | -1 (unbalanced) |
| Full statement | 12 | 12 | 0 (balanced) |

GAMS correctly parses this as a single statement because:
1. GAMS allows implicit line continuation for incomplete expressions
2. The statement is only terminated by the semicolon on line 213
3. Parentheses are balanced across the full statement

### Why nlp2mcp Fails

The error message suggests nlp2mcp is interpreting the code incorrectly. The error points to column 63 on line 212 and complains about an unexpected `;`, but line 212 doesn't end with a semicolon — it ends with `)`. This suggests the parser may be:

1. Not properly handling the line continuation, or
2. Reporting the error location incorrectly, or
3. Confusing the structure when it encounters the unbalanced parenthesis at end of line

### Previous Incorrect Diagnosis

The existing issue document `ISSUE_MISMATCHED_PARENTHESES.md` incorrectly diagnosed this as a "bug in the source model." This was proven wrong when `gams action=c` compilation succeeded on all 160 corpus models, including `camcge`.

## Impact

This issue likely affects many of the 74 models in the `lexer_invalid_char` failure category. Multi-line expressions are common in GAMS, especially for:
- Complex mathematical formulas
- CES/CET production functions (common in CGE models)
- Long conditional expressions
- Nested function calls

## Expected Behavior

The parser should:
1. Recognize that GAMS statements continue until a semicolon is reached
2. Track parenthesis balance across line boundaries
3. Not report errors for incomplete expressions mid-line when the expression continues

## Proposed Fix

### Option A: Lexer-Level Line Joining

Before parsing, join lines that have unbalanced parentheses:
```python
def preprocess_multiline(source: str) -> str:
    """Join lines with unbalanced parentheses."""
    lines = source.split('\n')
    result = []
    buffer = ""
    paren_depth = 0
    
    for line in lines:
        buffer += line
        paren_depth += line.count('(') - line.count(')')
        
        if paren_depth == 0 and buffer.rstrip().endswith(';'):
            result.append(buffer)
            buffer = ""
        else:
            buffer += " "  # Replace newline with space
    
    return '\n'.join(result)
```

### Option B: Grammar-Level Continuation

Modify the Lark grammar to explicitly allow newlines within parenthesized expressions:
```lark
// Allow whitespace including newlines within parentheses
_WS_INLINE: /[ \t]+/
_WS_MULTILINE: /[ \t\n\r]+/

// In parenthesized contexts, use _WS_MULTILINE
paren_expr: "(" _WS_MULTILINE? expr _WS_MULTILINE? ")"
```

### Option C: Parser Error Recovery

Implement error recovery that detects unbalanced parentheses at line end and attempts to continue parsing the next line as a continuation.

## Test Cases

### Test 1: Simple Multi-Line Expression
```gams
Parameter x;
x = (1
   + 2);
```
Expected: Parse successfully, x = 3

### Test 2: Nested Multi-Line Expression (camcge pattern)
```gams
Parameter at(i);
at(i) = xd0(i)/(gamma(i)*e0(i)**rhot(i) + (1 - gamma(i))
      * xxd0(i)**rhot(i))**(1/rhot(i));
```
Expected: Parse successfully

### Test 3: Multi-Line with Comments
```gams
Parameter y;
y = (1  $ first term
   + 2  $ second term
   + 3);
```
Expected: Parse successfully (GAMS allows `$` end-of-line comments)

## Related Files

- `src/gams/gams_grammar.lark`: Lark grammar definition
- `src/gams/gams_parser.py`: Parser implementation
- `src/gams/gams_lexer.py`: Lexer (if separate)
- `data/gamslib/raw/camcge.gms`: Primary reproduction case (line 212-213)

## Related Issues

- `ISSUE_MISMATCHED_PARENTHESES.md`: Should be updated or closed — the original diagnosis was incorrect

## Discovery Context

This issue was discovered during Sprint 18 Prep Task 2 (GAMSLIB Corpus Syntax Error Survey). Testing all 160 corpus models with `gams action=c` revealed that all models compile successfully with GAMS, meaning all 99 nlp2mcp parse failures are due to parser limitations, not GAMS syntax errors.

## Document History

- February 5, 2026: Initial creation based on Sprint 18 Prep Task 2 findings
