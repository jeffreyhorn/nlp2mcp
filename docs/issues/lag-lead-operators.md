# Issue: Lag/Lead Operators in Set Indexing

**GitHub Issue:** [#361](https://github.com/jeffreyhorn/nlp2mcp/issues/361)  
**Status:** Open  
**Priority:** HIGH  
**Complexity:** MEDIUM (6-8h)  
**Impact:** 2 Tier 2 models (chain, polygon)  
**Sprint:** Sprint 13+

---

## Problem Description

GAMS supports dynamic set indexing using lag/lead operators (`+` and `-`) for accessing adjacent elements in ordered sets. This is essential for time-series models, network flows, and sequential optimization problems.

**Syntax:**
- `set(i+1)` - next element in ordered set
- `set(i-1)` - previous element
- `sum(i+1, ...)` - sum over next elements
- `var(i+1)` - reference next variable index

Current parser treats `+` and `-` as arithmetic operators, not set lag/lead operators.

---

## Affected Models

### 1. chain.gms (line 56)

**GAMS Syntax:**
```gams
Set i 'nodes' /1*10/;
Alias (i, nh);

Equation link(i);
link(i)$(ord(i) < card(i))..
    sum(nh(i+1), y(nh)) =g= x(i);
```

**Error:**
```
Error: Parse error at line 56, column 37: Unexpected character: '*'
```

**Blocker:** `nh(i+1)` in sum expression not parsed. The `i+1` lag operator is treated as arithmetic.

---

### 2. polygon.gms (line 45)

**GAMS Syntax:**
```gams
Set i 'vertices' /1*n/;
Alias (i, j);

Variable r(i) 'radius at vertex i';
Equation objective;
objective..
    z =e= sum(i, sqr(r(i)) + sqr(r(j(i+1))));

Equation constraint(i);
constraint(i)$(ord(i) < card(i))..
    r(i) + r(i+1) =l= maxval;
```

**Error:**
```
Error: Parse error at line 45, column 30: Unexpected character: '+'
```

**Blocker:** Both `j(i+1)` in sum and `r(i+1)` in constraint use lag operators.

---

## Root Cause Analysis

### Grammar Issue

**Current Grammar:**
```lark
index_list: ID ("," ID)*
sum_expr: SUM_K "(" id_list "," expr ")"
```

**Problem:** Index lists are simple identifiers. No support for `ID(expr)` with lag/lead.

**Required Grammar:**
```lark
index_item: ID                          -> simple_index
          | ID "(" index_expr ")"       -> filtered_index

index_expr: ID                          -> index_ref
          | ID "+" NUMBER               -> index_lead
          | ID "-" NUMBER               -> index_lag

sum_expr: SUM_K "(" index_list "," expr ")"
index_list: index_item ("," index_item)*
```

---

### Semantic Interpretation

**Lag Operator `i-1`:**
- Get previous element in ordered set
- For set `{1,2,3,4,5}`, if `i=3` then `i-1` → `2`
- Undefined for first element (needs boundary check)

**Lead Operator `i+1`:**
- Get next element in ordered set
- For set `{1,2,3,4,5}`, if `i=3` then `i+1` → `4`
- Undefined for last element (needs boundary check)

**Common Patterns:**
```gams
sum(i(i+1), ...)        $ iterate over next elements
sum(i(i-1), ...)        $ iterate over previous elements
x(i) + x(i+1)           $ adjacent variable reference
constraint(i)$(ord(i) < card(i))  $ boundary condition
```

---

## Implementation Requirements

### Feature 1: Grammar Extension

**Add lag/lead syntax to grammar:**

```lark
// Index expressions for filtered sets
index_item: ID                              -> simple_index
          | ID "(" index_filter ")"         -> filtered_index

index_filter: index_expr                    -> filter_expr
            | index_expr ".." index_expr    -> filter_range

index_expr: ID                              -> index_ref
          | ID "+" INT                      -> index_lead
          | ID "-" INT                      -> index_lag
          | index_expr "+" INT              -> expr_add
          | index_expr "-" INT              -> expr_sub

// Update sum and other aggregations
sum_expr: SUM_K ("(" | "{") index_list "," expr (")" | "}")
prod_expr: PROD_K ("(" | "{") index_list "," expr (")" | "}")

// Variable/parameter indexing with lag/lead
indexed_ref: ID "[" index_expr_list "]"
           | ID "(" index_expr_list ")"

index_expr_list: index_expr ("," index_expr)*
```

---

### Feature 2: Parser Implementation

**Transform lag/lead operators to IR:**

```python
def _handle_index_filter(self, node):
    """Handle filtered index like i(i+1)."""
    set_name = _token_text(node.children[0])
    filter_node = node.children[1]
    
    if filter_node.data == "index_lead":
        base_index = _token_text(filter_node.children[0])
        offset = int(_token_text(filter_node.children[1]))
        return ir.IndexLead(set_name, base_index, offset)
    
    elif filter_node.data == "index_lag":
        base_index = _token_text(filter_node.children[0])
        offset = int(_token_text(filter_node.children[1]))
        return ir.IndexLag(set_name, base_index, offset)
```

**IR Representation:**
```python
@dataclass
class IndexLead:
    """Lead operator: i+offset"""
    set_name: str
    base_index: str
    offset: int

@dataclass
class IndexLag:
    """Lag operator: i-offset"""
    set_name: str
    base_index: str
    offset: int
```

---

### Feature 3: Converter Implementation

**Convert lag/lead to target framework (e.g., Pyomo):**

```python
def _convert_index_lead(self, lead: ir.IndexLead) -> str:
    """
    Convert i+k to next element access.
    
    In Pyomo: model.i.next(k)
    In math: i_{t+k}
    """
    if lead.offset == 1:
        return f"{lead.set_name}.next({lead.base_index})"
    else:
        return f"{lead.set_name}.next({lead.base_index}, {lead.offset})"

def _convert_index_lag(self, lag: ir.IndexLag) -> str:
    """
    Convert i-k to previous element access.
    
    In Pyomo: model.i.prev(k)
    In math: i_{t-k}
    """
    if lag.offset == 1:
        return f"{lag.set_name}.prev({lag.base_index})"
    else:
        return f"{lag.set_name}.prev({lag.base_index}, {lag.offset})"
```

**Note:** Target framework must support ordered sets and lag/lead operators.

---

### Feature 4: Boundary Conditions

**GAMS uses dollar conditions for boundaries:**
```gams
constraint(i)$(ord(i) < card(i))..
    x(i) =e= y(i+1);
```

**Semantic:**
- `ord(i)` - ordinal position of i (1-indexed)
- `card(i)` - cardinality (size) of set i
- Constraint only defined when `ord(i) < card(i)` (not last element)

**Implementation:**
- Parse dollar conditions (already supported in grammar)
- Evaluate condition to filter equation domain
- Skip lag/lead access for boundary elements

---

## Implementation Options

### Option A: Full Grammar + IR + Converter Support (RECOMMENDED)

**Approach:** Complete implementation across all layers.

**Components:**
1. Grammar: Add lag/lead syntax to index expressions
2. Parser: Transform to IR lag/lead nodes
3. Converter: Map to target framework (Pyomo, CVX, etc.)
4. Validation: Check boundary conditions

**Pros:**
- Clean semantic representation
- Extensible to other lag/lead patterns
- Proper error handling

**Cons:**
- Requires converter updates for each target framework

**Effort:** 6-8h
- Grammar extension: 2h
- Parser implementation: 2h
- IR nodes: 1h
- Converter (Pyomo): 2h
- Testing: 1h

---

### Option B: Preprocessor Expansion

**Approach:** Expand lag/lead operators in preprocessor before parsing.

**Transformation:**
```gams
sum(nh(i+1), y(nh))
→
sum(nh$(ord(nh) = ord(i)+1), y(nh))
```

**Implementation:**
```python
def expand_lag_lead_operators(source: str) -> str:
    """Expand i+k to ord-based filter."""
    # Pattern: ID(ID+NUM) or ID(ID-NUM)
    pattern = r'(\w+)\((\w+)([\+\-])(\d+)\)'
    
    def replacer(match):
        set_name, index, op, offset = match.groups()
        if op == '+':
            return f'{set_name}$(ord({set_name}) = ord({index})+{offset})'
        else:
            return f'{set_name}$(ord({set_name}) = ord({index})-{offset})'
    
    return re.sub(pattern, replacer, source)
```

**Pros:**
- No grammar changes
- Works with existing parser
- Quick implementation (2-3h)

**Cons:**
- Loses semantic information (can't distinguish lag from ord filter)
- May break roundtrip
- Doesn't handle all edge cases

**Effort:** 2-3h

---

### Option C: Partial Implementation (Sum Only)

**Approach:** Only support lag/lead in sum/prod aggregations, not general variable references.

**Scope:**
- `sum(i(i+1), expr)` ✓
- `prod(j(j-1), expr)` ✓
- `x(i+1)` in expressions ✗

**Effort:** 4-5h (subset of Option A)

---

## Recommendation

**Option A: Full Grammar + IR + Converter Support** (6-8h)

**Rationale:**
1. **Semantic clarity**: Proper IR representation for lag/lead operators
2. **Extensibility**: Foundation for more complex time-series features
3. **Unlocks 2 models**: chain.gms, polygon.gms (11% of Tier 2)
4. **Moderate effort**: 6-8h is reasonable for the value provided
5. **Future-proof**: Many optimization models use lag/lead for dynamic constraints

**Implementation Order:**
1. Grammar extension (2h)
2. Parser + IR (3h)
3. Converter (Pyomo support) (2h)
4. Testing (1h)

---

## Testing Requirements

### Unit Tests

**Lead Operator:**
```gams
Set i /1*5/;
Alias (i, j);
sum(j(i+1), x(j))
```
Expected IR: `Sum(FilteredSet('j', IndexLead('i', 1)), Var('x', ['j']))`

**Lag Operator:**
```gams
Set t /1*10/;
Variable y(t);
y(t) =e= y(t-1) + 1;
```
Expected IR: `Equation(y[t], Add(Var('y', [IndexLag('t', 1)]), 1))`

**Multiple Offsets:**
```gams
sum(i(i+2), ...)  $ i+2
sum(i(i-3), ...)  $ i-3
```

**Boundary Conditions:**
```gams
Equation eq(i);
eq(i)$(ord(i) > 1 and ord(i) < card(i))..
    x(i) =e= x(i-1) + x(i+1);
```

### Integration Tests

- chain.gms: `sum(nh(i+1), ...)` in constraint
- polygon.gms: `r(i+1)` in variable reference and `j(i+1)` in sum

---

## References

- GAMS Documentation: Lag and Lead Operations
- Failing models: `tests/fixtures/tier2_candidates/{chain,polygon}.gms`
- Grammar: `src/gams/gams_grammar.lark` (sum_expr, index_list)
- Parser: `src/ir/parser.py` (sum handling)
- IR: `src/ir/base.py` (add IndexLead, IndexLag nodes)
