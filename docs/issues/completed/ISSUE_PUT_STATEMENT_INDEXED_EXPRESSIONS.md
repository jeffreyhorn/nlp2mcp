# Issue: Put Statement Indexed Expressions with Commas

## Summary

Put statements containing indexed variable expressions (like `v1("out", omega1)`) fail to parse because the comma inside the expression conflicts with the comma separating put items.

## Error Message

```
Parse error at line 122, column 36: Unexpected character: ','
  loop(omega1, put "x g1  omax g1   ", v1("out", omega1), " period2 ", v1("pro", omega1) /;);
                                    ^
```

## Reproduction Steps

1. Create a GAMS file with a put statement containing indexed expressions:
   ```gams
   loop(omega1, put "x g1  omax g1   ", v1("out", omega1), " period2 ", v1("pro", omega1) /;);
   ```

2. Run the parser:
   ```bash
   python -c "
   from src.gams.parser import parse_gams_file
   result = parse_gams_file('path/to/file.gms')
   print(result)
   "
   ```

3. Observe the parse error at the comma inside the indexed expression.

## Affected Models

- **apl1p** (line 122-130): Multiple put statements with indexed variable expressions

Example GAMS code from apl1p.gms:
```gams
File stg / MODEL.STG /;
put stg;
loop(omega1, put "x g1  omax g1   ", v1("out", omega1), " period2 ", v1("pro", omega1) /;);
loop(omega2, put "x g2  omax g2   ", v2("out", omega2), " period2 ", v2("pro", omega2) /;);
loop(omega1,
loop(omega2, put "x g12 omax g1g2 ", v12("out", omega1, omega2), " period3 ", v12("pro", omega1, omega2) /;));
```

## Root Cause Analysis

The current grammar handles put statements as:

```lark
put_stmt: "put"i put_item* SEMI
        | "put"i put_item* "/" SEMI

put_item: STRING
        | "/" -> put_newline
        | expr
```

The issue is that `put_item` uses `expr` which can match expressions like `v1("out", omega1)`. However, when parsing a sequence of `put_item*`, the parser sees:
1. `"x g1  omax g1   "` - STRING (matches)
2. `,` - separator (expected)
3. `v1` - start of expr
4. `(` - function call start
5. `"out"` - argument
6. `,` - **AMBIGUITY**: Is this a comma inside the function call or a separator between put items?

The Lark parser with the current grammar cannot distinguish between:
- A comma inside a function/indexed expression: `v1("out", omega1)`
- A comma separating put items: `..., v1("out", omega1), " period2 "`

## Proposed Fix

### Option 1: Use parenthesized expressions for put items

Modify `put_item` to require parentheses around expressions that might contain commas:

```lark
put_item: STRING
        | "/" -> put_newline
        | "(" expr ")" -> put_expr_paren
        | simple_expr -> put_expr_simple
```

This approach may be too restrictive as GAMS allows unparenthesized expressions.

### Option 2: Parse put items differently using comma as explicit separator

Redefine put statement to explicitly handle comma-separated items:

```lark
put_stmt: "put"i put_items SEMI
        | "put"i put_items "/" SEMI

put_items: put_item ("," put_item)*

put_item: STRING
        | "/" -> put_newline
        | expr
```

This makes the comma an explicit part of the grammar rather than relying on `put_item*` repetition.

### Option 3: Increase expression priority in put context

Use Lark's contextual lexing or priorities to ensure expressions consume their internal commas before the outer grammar sees them.

### Recommended Approach

**Option 2** is recommended because:
1. It explicitly models GAMS put statement syntax with comma-separated items
2. The expr rule already handles nested commas within function calls correctly
3. Minimal grammar changes required
4. Clear semantic meaning

## Testing

After implementing the fix, verify:
1. `make test` passes
2. apl1p.gms parses without errors
3. Other put statements in the test corpus still parse correctly

## Related Issues

- Issue #554: Stage Attribute Syntax (completed)
- Issue #555: Numeric Values in Set Data (open)
- Issue #556: Unquoted File Path Syntax (completed)

## GitHub Issue

**Issue #:** 557
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/557
