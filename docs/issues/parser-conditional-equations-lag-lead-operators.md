# Parser Limitation: Conditional Equations and Lag/Lead Operators Not Supported

**GitHub Issue**: [#223](https://github.com/jeffreyhorn/nlp2mcp/issues/223)

## Status
**Open** - Parser limitation  
**Priority**: Medium  
**Component**: Parser (src/gams/gams_grammar.lark, src/ir/parser.py)  
**Discovered**: 2025-11-15 during Sprint 7 Day 3 (himmel16.gms testing)

## Description

The GAMS parser does not support two advanced GAMS features that prevent parsing of GAMSLib model himmel16.gms:

1. **Conditional Equations (`$` operator)**: Equations with conditional expressions like `equation(i,j)$(condition)..`
2. **Lag/Lead Operators (`++` and `--`)**: Time-series indexing operators like `x(i++1)` for "next period"

These are standard GAMS syntax features used in many GAMSLib models for optimization problems with conditional constraints and time-series data.

## Current Behavior

When parsing himmel16.gms, the parser fails at line 44 with:

```
No terminal matches '$' in the current parser context, at line 44 col 13

maxdist(i,j)$(ord(i) < ord(j)).. sqr(x(i) - x(j)) + sqr(y(i) - y(j)) =l= 1;
            ^
Expected one of:
	* ASSIGN
	* __ANON_0
```

If the `$` conditional were supported, parsing would fail at line 46 with:

```
No terminal matches '+' in the current parser context

areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));
                                         ^^
```

## Expected Behavior

The parser should accept both syntaxes:

1. **Conditional equations**: `maxdist(i,j)$(ord(i) < ord(j)).. expression`
2. **Lag/lead operators**: `x(i++1)` (next), `x(i--1)` (previous), `x(i+n)`, `x(i-n)`

## Reproduction

### Test File: himmel16.gms (GAMSLib)

Key patterns that fail:

```gams
* Conditional equation (line 44)
maxdist(i,j)$(ord(i) < ord(j)).. sqr(x(i) - x(j)) + sqr(y(i) - y(j)) =l= 1;

* Lag/lead operators (line 46)
areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));

* Another lag/lead example (line 48)
obj1.. totarea =e= 0.5*sum(i, x(i)*y(i++1) - y(i)*x(i++1));
```

### Minimal Test Cases

**Conditional Equation:**
```gams
Set i / 1*5 /;
Variable x(i);
Equation balance(i);

* Only create constraint when i > 2
balance(i)$(ord(i) > 2).. x(i) =e= 1;

Model test / all /;
```

**Lag/Lead Operators:**
```gams
Set t 'time periods' / 1*10 /;
Variable x(t);
Equation flow(t);

* Reference next time period
flow(t).. x(t) =e= x(t++1) + 1;

Model test / all /;
```

## Impact

**High Impact for GAMSLib Coverage:**
- **Conditional equations** are common in GAMSLib models (used in ~30% of models)
- **Lag/lead operators** are essential for time-series and dynamic models (~15% of models)
- Blocks parsing of important model classes:
  - Dynamic optimization models
  - Multi-period planning models  
  - Models with sparse constraint patterns

**Workaround**: None available - these are core GAMS features with no simple alternatives.

## Technical Details

### Feature 1: Conditional Equations (`$` operator)

The `$` operator in equation definitions filters which instances of an indexed equation are actually generated.

**Syntax:**
```gams
equation_name(indices)$(condition).. expression;
```

**Examples:**
- `balance(i,j)$(i <> j)..` - Only when i ≠ j
- `capacity(t)$(ord(t) > 1)..` - Only after first period
- `cost(i)$(demand(i) > 0)..` - Only when demand is positive

**Semantics:**
- The condition is evaluated for each index combination
- Only instances where condition is true generate constraints
- Commonly uses `ord()`, `card()`, and parameter comparisons

### Feature 2: Lag/Lead Operators

GAMS supports several indexing operators for referencing adjacent set elements:

**Operators:**
- `++`: Next element (lag +1)
- `--`: Previous element (lag -1)
- `+n`: n elements ahead
- `-n`: n elements back

**Examples:**
```gams
x(t++1)      * Value in next period
x(t--1)      * Value in previous period  
x(t+3)       * Value 3 periods ahead
x(t-2)       * Value 2 periods back
```

**Edge Behavior:**
- For circular sets: wraps around
- For non-circular sets: `x(t++1)` where `t` is last element typically evaluates to 0 or first element (model-dependent)

### Suggested Implementation

#### 1. Conditional Equations Grammar

```lark
equation_stmt: equation_name domain_spec? condition? ".." relation

condition: "$" "(" expr ")"
```

**Parser Strategy:**
- Parse the condition expression
- During IR building, generate only the instances satisfying the condition
- May need to evaluate condition at parse time or defer to normalization

**Complexity:** Medium
- Grammar change: Simple (add optional condition clause)
- Parser logic: Medium (condition evaluation)
- IR representation: May need to store condition for later evaluation

#### 2. Lag/Lead Operators Grammar

```lark
var_ref: ID "(" index_list ")"

?index_expr: ID
           | ID "++" NUMBER?    -> index_lead
           | ID "--" NUMBER?    -> index_lag
           | ID "+" NUMBER      -> index_offset_plus
           | ID "-" NUMBER      -> index_offset_minus
```

**Parser Strategy:**
- Recognize lag/lead operators in index expressions
- Transform to explicit index calculations
- Handle edge cases (wraparound, out-of-bounds)

**Complexity:** High
- Grammar change: Medium (index expression ambiguity with arithmetic)
- Parser logic: High (need to resolve operator precedence)
- IR representation: Need new IndexExpr node types
- Semantic analysis: Must validate against set definitions

### Parsing Complexity

Both features introduce significant complexity:

1. **Conditional equations**: 
   - Need expression evaluator at parse time OR
   - Defer to normalization phase (preferred)
   - Must handle parameter values in conditions

2. **Lag/lead operators**:
   - Conflicts with arithmetic operators (`+`, `-`)
   - Context-sensitive: `i+1` could be index offset OR arithmetic
   - Requires set element ordering information
   - Edge case handling (circular vs non-circular sets)

### Alternative: Preprocessor Expansion

For lag/lead operators, could implement as preprocessor transformation:

```gams
* Before preprocessing:
x(t++1)

* After preprocessing (if t=5, next is 6):
x(6)
```

This requires:
- Set membership resolution at preprocess time
- May not work for all cases (symbolic indices)
- Simpler than full parser support

## Related Issues

- Issue #136: Set range syntax (✅ RESOLVED in Sprint 7 Days 2-3)
- General parser roadmap for GAMSLib coverage

## Suggested Fix Priority

**Medium-High Priority:**
- Required for ~30-40% of GAMSLib models
- No workarounds available
- Significant implementation effort (10-15 hours estimated)
- Should be tackled after higher-priority parser features

## Testing Requirements

When implementing, add tests for:

### Conditional Equations:
1. Basic condition: `eq(i)$(ord(i) > 1)..`
2. Parameter condition: `eq(i)$(param(i) > 0)..`
3. Set condition: `eq(i,j)$(i <> j)..`
4. Logical operators: `eq(i)$(condition1 and condition2)..`
5. Complex expressions in condition

### Lag/Lead Operators:
1. Next element: `x(t++1)`
2. Previous element: `x(t--1)`
3. Offset: `x(t+3)`, `x(t-2)`
4. In expressions: `x(t) + x(t++1)`
5. Multiple operators: `x(t++1) * y(t--1)`
6. Edge cases: first/last elements
7. Circular vs non-circular sets

## References

- **GAMS Documentation**: 
  - Conditional equations: Dollar operator `$`
  - Lag/lead operators: Dynamic sets and ordered sets
- **GAMSLib Model**: himmel16.gms (minimal polygon area problem)
- **Sprint 7 Day 3**: Discovered during range syntax testing

## Workaround

**None available.** These are fundamental GAMS features that cannot be worked around without significantly changing the model structure.

Models using these features cannot currently be parsed by nlp2mcp.
