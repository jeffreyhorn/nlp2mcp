# Parser: Dollar-Conditioned Assignment Statements Not Supported

**GitHub Issue:** #415  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/415  
**Status:** Open  
**Priority:** High  
**Component:** Parser  
**Tier 2 Candidate:** pool.gms  

## Problem Statement

The parser fails when encountering assignment statements with dollar conditions (conditional assignments). This is blocking pool.gms from parsing completely.

## Current Behavior

**Parse Error:**
```
Error: Parse error at line 850, column 43: Unexpected character: '='
  rep2(case,'optcr')$(abs(sol(case)) > 1e-6)= round(abs((rep2(case,'Obj') - sol(case))/sol(case)),6);
                                            ^
```

**Failing Examples from pool.gms (lines 742-743):**
```gams
rep2(case,'GlobalObj') = sol(case);
rep2(case,'optcr')$(abs(sol(case)) > 1e-6)= round(abs((rep2(case,'Obj') - sol(case))/sol(case)),6);
rep2(case,'optca')$(abs(sol(case)) > 1e-6)= round(abs(rep2(case,'Obj')  - sol(case)),6);
```

Line 741 is a regular assignment (no condition) and parses fine. Lines 742-743 have dollar conditions and fail to parse.

The pattern is: `lhs$(condition) = rhs;` where the assignment only executes if the condition is true.

## Expected Behavior

The parser should successfully parse assignment statements with dollar conditions:
- Simple conditional assignments: `x$(condition) = value;`
- Indexed conditional assignments: `param(i)$(i > 5) = data(i);`
- Complex conditions: `result$(abs(value) > threshold) = calculation;`

## GAMS Language Specification

In GAMS, the dollar operator `$` is used for conditional operations. When applied to assignments, it creates a conditional assignment that only executes when the condition is true.

**Syntax:**
```gams
lhs$(condition) = rhs;
```

**Semantics:**
- If `condition` evaluates to non-zero (true), the assignment executes
- If `condition` evaluates to zero (false), the assignment is skipped
- This is equivalent to: `if(condition, lhs = rhs;)`

**Examples:**
```gams
* Simple conditional assignment
x$(y > 0) = 10;

* Indexed conditional assignment  
param(i)$(data(i) > threshold) = result(i);

* Multiple conditions using logical operators
value$(x > 0 and y < 100) = x * y;

* Nested indexing with condition
rep2(case,'optcr')$(abs(sol(case)) > 1e-6) = calculation;
```

**Common Use Cases:**
1. **Avoiding division by zero:**
   ```gams
   ratio$(denominator <> 0) = numerator / denominator;
   ```

2. **Conditional data assignment:**
   ```gams
   result(i)$(input(i) > 0) = process(input(i));
   ```

3. **Reporting calculations:**
   ```gams
   report('metric')$(baseline > threshold) = (current - baseline) / baseline;
   ```

## Technical Analysis

### Current Grammar State

Looking at the grammar, assignment statements are defined as:

```lark
assignment_stmt: lhs "=" expr SEMI
```

Where `lhs` can be:
- Simple identifier: `x`
- Indexed reference: `param(i,j)`
- Dotted attribute reference: `variable.lo(i)`

The grammar doesn't currently support the `$(condition)` suffix on the left-hand side.

### Required Changes

We need to allow an optional dollar condition on the left-hand side of assignments:

**Option 1: Extend lhs to include dollar condition**
```lark
assignment_stmt: lhs dollar_condition? "=" expr SEMI
dollar_condition: DOLLAR "(" expr ")"
```

**Option 2: Modify lhs directly**
```lark
lhs: lhs_base (DOLLAR "(" expr ")")?
lhs_base: ID
        | ID "(" expr_list ")"
        | ID "." ID
        | ID "." ID "(" expr_list ")"
```

**Option 3: Create conditional_assignment as separate rule**
```lark
assignment_stmt: lhs "=" expr SEMI
               | lhs DOLLAR "(" expr ")" "=" expr SEMI  -> conditional_assignment
```

Option 3 might be cleanest as it keeps the distinction clear and allows for specific handling in the parser.

### Dollar Operator Context

The dollar operator `$` in GAMS has multiple uses:
1. **Set filtering:** `sum(i$condition, expr)`  ✅ Already supported (issue #412)
2. **Conditional assignments:** `lhs$condition = rhs;`  ❌ This issue
3. **Conditional equations:** `equ$(condition).. lhs =e= rhs;`  ⚠️ May need separate handling
4. **Domain restrictions:** `subset(i)$(filter(i))`

We're specifically addressing case #2 (conditional assignments) in this issue.

### Parser Semantic Handling

For the IR, we need to decide how to represent conditional assignments:

**Option A: Transform to if statement**
```python
# rep2(case,'optcr')$(abs(sol(case)) > 1e-6)= value;
# becomes:
If(condition=Binary(">", Call("abs", ...), Const(1e-6)),
   then_block=[Assignment(lhs, rhs)])
```

**Option B: Create ConditionalAssignment node**
```python
@dataclass(frozen=True)
class ConditionalAssignment(Statement):
    lhs: LHS
    condition: Expr
    rhs: Expr
```

Option A (transform to if) might be simpler and reuse existing IR structures.

## Implementation Plan

### 1. Update Grammar (src/gams/gams_grammar.lark)

Add support for conditional assignments:

```lark
assignment_stmt: lhs "=" expr SEMI
               | lhs DOLLAR "(" expr ")" "=" expr SEMI  -> conditional_assignment
```

Or, if we want to keep it unified:

```lark
assignment_stmt: lhs dollar_condition? "=" expr SEMI
dollar_condition: DOLLAR "(" expr ")"
```

### 2. Update Parser (src/ir/parser.py)

In the assignment statement handler:
- Check if there's a dollar_condition node
- If present, extract the condition expression
- Transform to an If statement in the IR:
  ```python
  if dollar_condition:
      condition_expr = self._expr(dollar_condition)
      assignment_node = Assignment(lhs, rhs)
      return If(condition=condition_expr, then_block=[assignment_node], else_block=[])
  else:
      return Assignment(lhs, rhs)
  ```

### 3. Testing Strategy

**Unit Tests:**
- Simple conditional assignment: `x$(y > 0) = 10;`
- Indexed conditional assignment: `param(i)$(i > 5) = data(i);`
- Complex condition: `value$(abs(x) > 1e-6) = calculation;`
- Pool.gms patterns: `rep2(case,'optcr')$(abs(sol(case)) > 1e-6)= round(...);`

**Integration Tests:**
- Verify pool.gms parses successfully past line 742
- Test conditional assignments in different contexts (top-level, inside loops, inside if blocks)

**Test Examples:**
```gams
* Test 1: Simple
x$(y > 0) = 10;

* Test 2: Indexed
param(i)$(data(i) > 0) = result(i);

* Test 3: Complex condition
ratio$(abs(denom) > 1e-10) = numer / denom;

* Test 4: Pool.gms pattern
rep2(case,'optcr')$(abs(sol(case)) > 1e-6)= round(abs((rep2(case,'Obj') - sol(case))/sol(case)),6);
```

## Acceptance Criteria

1. ✅ Grammar supports `lhs$(condition) = rhs;` syntax
2. ✅ Parser correctly transforms conditional assignments to IR
3. ✅ Simple conditional assignments parse correctly
4. ✅ Indexed conditional assignments parse correctly
5. ✅ Pool.gms parses successfully past line 742
6. ✅ All existing tests continue to pass
7. ✅ New tests cover various conditional assignment patterns
8. ✅ Quality gates pass (typecheck, lint, format, test)

## Related Issues

- Issue #409: Pool.gms missing include file (completed)
- Issue #412: Conditional sum syntax (completed) - This implemented `$` in sum contexts
- Issue #413: Option statement multiple assignments (completed)
- Issue #414: Solve statement in loops (completed)

This is the next blocker preventing pool.gms from parsing completely.

## References

- GAMS Documentation: [The Dollar Condition](https://www.gams.com/latest/docs/UG_DollarCondition.html)
- GAMS Documentation: [Conditional Assignments](https://www.gams.com/latest/docs/UG_AssignmentStatement.html)
- File: `tests/fixtures/tier2_candidates/pool.gms` (line 742-743)
- GAMS Library: pool.gms is model 237 in GAMSLib

## Notes

This feature is closely related to issue #412 (conditional sums), which already implemented dollar operator parsing in expression contexts. We're extending that to assignment statement contexts.

The dollar operator is pervasive in GAMS and this is an important pattern for conditional data manipulation, especially for:
- Avoiding division by zero
- Conditional reporting
- Data validation and filtering
- Sparse data assignment
