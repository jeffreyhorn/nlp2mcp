# GAMS Nested/Subset Indexing Research for Sprint 11

**Date:** 2025-11-25  
**Sprint:** Sprint 11 Prep - Task 2  
**Purpose:** Implementation-ready research for nested/subset indexing support  
**Prior Work:** Sprint 10 Blocker Analysis (docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md)

---

## Executive Summary

### Research Focus

This research provides **implementation-ready guidance** for adding GAMS nested/subset indexing support to the nlp2mcp parser. Sprint 10 deferred maxmin.gms due to high complexity (9/10) and risk. Sprint 11 Task 2 evaluates whether to implement in Sprint 11 or defer to Sprint 12.

### Key Questions Answered

1. **What is subset indexing in GAMS?** ✅ Subset-based equation domain filtering with nested indices
2. **How complex is the implementation?** ✅ 10-14 hours (grammar 3-4h, AST 2-3h, semantic 4-6h, tests 1-2h)
3. **What are the risks?** ✅ HIGH (9/10) - grammar recursion, semantic complexity, limited testing coverage
4. **Should we implement in Sprint 11?** ✅ **RECOMMENDATION: DEFER TO SPRINT 12** (see Section 10)

### Implementation Effort Breakdown

| Component | Effort | Risk | Priority |
|-----------|--------|------|----------|
| Grammar changes | 3-4 hours | HIGH | Critical |
| AST node definitions | 2-3 hours | MEDIUM | Critical |
| Semantic resolution | 4-6 hours | HIGH | Critical |
| Testing & validation | 1-2 hours | MEDIUM | Critical |
| **TOTAL** | **10-14 hours** | **HIGH** | **Critical** |

### Sprint 11 Recommendation

**DEFER nested/subset indexing to Sprint 12**

**Rationale:**
- **High risk:** 10-14 hour budget could slip to 16-20 hours (unknown unknowns)
- **Low ROI:** Only unlocks maxmin.gms to 56% (still has 4 more blocker categories)
- **Better alternatives:** Aggressive simplification + CI guardrails have higher value
- **Sprint 11 capacity:** 20-30 hours total, aggressive simplification alone is 12-15 hours
- **Fallback viable:** 90% Tier 1 parse rate (9/10 models) is excellent progress

**Sprint 12 Proposal:**
- Dedicated sprint for maxmin.gms (all 5 blocker categories)
- Budget: 23-40 hours total (nested indexing 10-14h + other features 13-26h)
- Goal: 100% Tier 1 parse rate (10/10 models)
- Lower risk: No competition for sprint capacity

---

## Section 1: GAMS Subset Indexing Semantics

### 1.1 Overview

GAMS subset indexing allows **conditional equation generation** by filtering equation domains through subset membership. This is more efficient than generating all equations and using conditional logic inside equation bodies.

**Example:**
```gams
Set n / p1*p10 /;
Set low(n,n) 'lower triangle';
low(n,nn) = ord(n) > ord(nn);  // Subset assignment: 45 pairs

Equation dist(n,n);
dist(low(n,nn)).. d(n,nn) =e= sqrt(sqr(x(n) - x(nn)));  // Only 45 equations generated
```

**Without subset filtering (inefficient):**
```gams
dist(n,nn)$(ord(n) > ord(nn)).. d(n,nn) =e= sqrt(sqr(x(n) - x(nn)));  // 100 equations, 55 skipped
```

### 1.2 Subset Declaration Syntax

**2D Subset:**
```gams
Set low(n,n) 'lower triangle';  // 2D subset of n x n
```

**Subset Assignment:**
```gams
low(n,nn) = ord(n) > ord(nn);  // Boolean expression assigns membership
```

**Resulting Subset (for n=p1*p3):**
```
low = {(p2,p1), (p3,p1), (p3,p2)}  // 3 pairs where ord(n) > ord(nn)
```

### 1.3 Subset Usage in Equation Domains

**Full Form (Explicit Indices):**
```gams
defdist(low(n,nn))..   dist(low) =e= sqrt(...);
```
- Generates equations ONLY for pairs in `low` subset
- Indices `n` and `nn` are bound to each subset member pair
- Inside equation: `low` refers to current pair `(n,nn)`

**Shorthand Form (Implicit Indices):**
```gams
mindist1(low)..        mindist   =l= dist(low);
```
- Equivalent to `mindist1(low(n,nn))..` when `low` dimensionality is known
- GAMS infers indices from subset declaration `low(n,n)`
- Parser must track subset dimensionality for shorthand resolution

### 1.4 Index Binding and Scoping Rules

**Binding Rules:**
1. Indices in subset reference become available in equation body
2. `defdist(low(n,nn))` binds `n` and `nn` for equation body scope
3. Can use `n`, `nn` in variable references: `point(n,d)`, `point(nn,d)`
4. Index names must match alias declarations (e.g., `Alias (n,nn)`)

**Scoping:**
```gams
defdist(low(n,nn))..   
    dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
    //                                    ^n^         ^^nn^^
    //                 Indices n, nn available in entire equation body
```

### 1.5 Static vs. Dynamic Subset Evaluation

**Static Evaluation (compile-time):**
```gams
Set low(n,n);
low(n,nn) = ord(n) > ord(nn);  // Evaluated once at model compile
Equation dist(low(n,nn))..     // Subset membership fixed
```

**Key Characteristics:**
- Subset assignment must precede equation declaration
- Subset membership cannot change after equation generation
- Parser can expand subset to concrete pairs at parse time
- No runtime subset membership checks needed

**Dynamic Evaluation (runtime, NOT applicable here):**
- Would require subset membership checks during solve
- GAMS equation domains are static (fixed at model generation)
- Our implementation can assume static evaluation

### 1.6 Subset Membership Testing Algorithm

**Algorithm for `low(n,nn) = ord(n) > ord(nn)`:**

```python
def evaluate_subset_membership(subset_condition, set_members):
    """
    Evaluate subset membership for all set member combinations.
    
    Args:
        subset_condition: AST node for condition (e.g., ord(n) > ord(nn))
        set_members: List of set members (e.g., ['p1', 'p2', 'p3'])
    
    Returns:
        List of tuples representing subset members
    """
    subset_members = []
    for i, n_val in enumerate(set_members):
        for j, nn_val in enumerate(set_members):
            # Bind n=n_val, nn=nn_val, evaluate condition
            # ord(n) returns 1-based index (i+1)
            if (i + 1) > (j + 1):  # ord(n) > ord(nn)
                subset_members.append((n_val, nn_val))
    return subset_members

# For n = ['p1', 'p2', 'p3']:
# Result: [('p2','p1'), ('p3','p1'), ('p3','p2')]
```

**Performance:**
- Time complexity: O(n²) for 2D subsets (n = cardinality of set)
- For maxmin.gms with 13 points: 13² = 169 pairs evaluated → 78 in subset
- Acceptable for typical model sizes (n < 100)
- Large models (n > 1000) may need optimization

### 1.7 Edge Cases

**Empty Subset:**
```gams
Set empty(n,n);
empty(n,nn) = 1 = 0;  // Always false
Equation e(empty)..   // Generates ZERO equations
```
- Valid GAMS syntax, no equations generated
- Parser must handle gracefully (no error)

**Complex Conditions:**
```gams
Set complex(n,n);
complex(n,nn) = (ord(n) > ord(nn)) and (ord(n) < 5);
```
- Must evaluate arbitrary boolean expressions
- Requires full expression evaluator in semantic analyzer

**Nested Subset References (NOT in maxmin.gms):**
```gams
Set a(n), b(a,a);  // b is subset of a x a where a is subset of n
```
- Not encountered in maxmin.gms
- Can defer to Sprint 12 if needed

---

## Section 2: Grammar Design

### 2.1 Current Grammar Limitations

**Current Lark Rule:**
```lark
equation_def: ID "(" id_list ")" ".." equation_body

id_list: ID ("," ID)*
```

**What It Handles:**
```gams
equation(i,j)..  // Simple identifiers only
```

**What It Fails On:**
```gams
equation(low(n,nn))..  // Nested parentheses: ID "(" ID "(" ID "," ID ")" ")"
```

**Error:**
```
No terminal matches '(' at line 51 col 12
defdist(low(n,nn))..
           ^
```

### 2.2 Grammar Design Alternatives

**Option 1: Explicit Subset Syntax (Recommended)**

```lark
equation_def: ID "(" domain_list ")" ".." equation_body

domain_list: domain_element ("," domain_element)*

domain_element: ID                       # Simple: i
              | ID "(" id_list ")"       # Subset: low(n,nn)

id_list: ID ("," ID)*
```

**Pros:**
- Clear separation of simple vs. subset domains
- Easy to implement (2 levels only)
- Covers maxmin.gms patterns

**Cons:**
- Doesn't handle arbitrary nesting (but not needed for maxmin.gms)

**Option 2: Recursive Domain Syntax**

```lark
equation_def: ID "(" domain_list ")" ".." equation_body

domain_list: domain_element ("," domain_element)*

domain_element: ID
              | ID "(" domain_list ")"  # Recursive: allows infinite nesting
```

**Pros:**
- Handles arbitrary nesting depth
- Future-proof for complex models

**Cons:**
- More complex to implement
- May introduce parsing ambiguities
- Overkill for current needs

**Option 3: Flat Syntax with Semantic Resolution**

```lark
equation_def: ID "(" expr_list ")" ".." equation_body

expr_list: expr ("," expr)*

expr: ID | ID "(" expr_list ")"  # Treat as general expression
```

**Pros:**
- Most flexible
- Reuses expression parsing logic

**Cons:**
- Defers complexity to semantic analyzer
- Harder to validate at parse time
- Can accept invalid syntax

### 2.3 Recommended Approach: Option 1 (Explicit Subset Syntax)

**Rationale:**
- Sufficient for maxmin.gms (only 2-level nesting)
- Clear AST structure (distinct node types)
- Easier to validate at parse time
- Can extend to Option 2 later if needed

**Implementation:**

```lark
equation_def: ID "(" domain_list ")" ".." equation_body

domain_list: domain_element ("," domain_element)*

domain_element: simple_domain | subset_domain

simple_domain: ID

subset_domain: ID "(" id_list ")"

id_list: ID ("," ID)*
```

**Backward Compatibility:**
- `simple_domain` matches current behavior
- Existing models continue to parse correctly
- Only adds new syntax, doesn't break old syntax

---

## Section 3: AST Representation Design

### 3.1 Current AST Structure

```python
@dataclass
class EquationDef:
    name: str
    domain: list[str]  # Simple list: ['i', 'j']
    body: EquationBody
```

**Limitation:** Cannot represent subset domains like `low(n,nn)`

### 3.2 Proposed AST Node Types

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class DomainElement(ABC):
    """Base class for equation domain elements"""
    
    @abstractmethod
    def get_identifiers(self) -> list[str]:
        """Return list of index identifiers bound by this domain element"""
        pass

@dataclass
class SimpleDomain(DomainElement):
    """Simple identifier domain: i, j, k"""
    identifier: str
    
    def get_identifiers(self) -> list[str]:
        return [self.identifier]
    
    def __str__(self):
        return self.identifier

@dataclass
class SubsetDomain(DomainElement):
    """Subset with explicit indices: low(n,nn)"""
    subset_name: str
    indices: list[str]
    
    def get_identifiers(self) -> list[str]:
        return self.indices
    
    def __str__(self):
        return f"{self.subset_name}({','.join(self.indices)})"

@dataclass
class EquationDef:
    """Equation definition with support for subset domains"""
    name: str
    domain: list[DomainElement]  # Can be SimpleDomain or SubsetDomain
    body: EquationBody
    
    def get_all_indices(self) -> list[str]:
        """Get all index identifiers from all domain elements"""
        indices = []
        for elem in self.domain:
            indices.extend(elem.get_identifiers())
        return indices
```

### 3.3 AST Construction Examples

**Example 1: Simple Domain**
```gams
equation(i,j)..
```

**AST:**
```python
EquationDef(
    name='equation',
    domain=[
        SimpleDomain(identifier='i'),
        SimpleDomain(identifier='j')
    ],
    body=...
)
```

**Example 2: Subset Domain (maxmin.gms line 51)**
```gams
defdist(low(n,nn))..
```

**AST:**
```python
EquationDef(
    name='defdist',
    domain=[
        SubsetDomain(subset_name='low', indices=['n', 'nn'])
    ],
    body=...
)
```

**Example 3: Mixed Domains**
```gams
equation(i, low(n,nn), j)..
```

**AST:**
```python
EquationDef(
    name='equation',
    domain=[
        SimpleDomain(identifier='i'),
        SubsetDomain(subset_name='low', indices=['n', 'nn']),
        SimpleDomain(identifier='j')
    ],
    body=...
)
```

### 3.4 Visitor Pattern Implications

**Current Visitor:**
```python
def visit_equation_def(self, node: EquationDef):
    for index in node.domain:  # Assumes list[str]
        process_index(index)
```

**Updated Visitor:**
```python
def visit_equation_def(self, node: EquationDef):
    for domain_elem in node.domain:  # Now list[DomainElement]
        if isinstance(domain_elem, SimpleDomain):
            process_simple_domain(domain_elem.identifier)
        elif isinstance(domain_elem, SubsetDomain):
            process_subset_domain(domain_elem.subset_name, domain_elem.indices)
```

**Impact:**
- All visitors must be updated to handle `DomainElement` types
- Can use `get_identifiers()` method for generic processing
- Type checking ensures correct handling

---

## Section 4: Semantic Resolution Algorithm

### 4.1 Overview

Semantic resolution converts subset domains from AST to concrete equation instances.

**Input:** `EquationDef` with `SubsetDomain` in `domain` list  
**Output:** List of equation instances with bound index values

### 4.2 Algorithm Steps

```python
def resolve_subset_domain(equation_def: EquationDef, symbol_table: SymbolTable):
    """
    Resolve subset domains to concrete equation instances.
    
    Steps:
    1. Identify subset domains in equation.domain
    2. Look up subset definition in symbol table
    3. Verify index compatibility
    4. Expand subset to member pairs
    5. Generate equation instance for each member
    """
    
    # Step 1: Extract domain elements
    domain_elements = equation_def.domain
    
    # Step 2: Process each domain element
    concrete_instances = []
    for domain_elem in domain_elements:
        if isinstance(domain_elem, SubsetDomain):
            # Step 3: Look up subset in symbol table
            subset_def = symbol_table.lookup(domain_elem.subset_name)
            if subset_def is None:
                raise UndefinedSymbolError(f"Subset '{domain_elem.subset_name}' not defined")
            
            if not isinstance(subset_def, SetDef):
                raise TypeError(f"'{domain_elem.subset_name}' is not a set/subset")
            
            # Step 4: Verify index compatibility
            if len(domain_elem.indices) != len(subset_def.domain):
                raise IndexMismatchError(
                    f"Subset '{domain_elem.subset_name}' expects "
                    f"{len(subset_def.domain)} indices, got {len(domain_elem.indices)}"
                )
            
            # Step 5: Verify indices are valid (exist in parent sets)
            for idx, parent_set in zip(domain_elem.indices, subset_def.domain):
                if not symbol_table.is_valid_index(idx, parent_set):
                    raise InvalidIndexError(f"Index '{idx}' not valid for set '{parent_set}'")
            
            # Step 6: Expand subset to concrete members
            subset_members = expand_subset(subset_def, symbol_table)
            
            # Step 7: Generate equation instance for each member
            for member_tuple in subset_members:
                # Bind indices to member values
                bindings = dict(zip(domain_elem.indices, member_tuple))
                instance = instantiate_equation(equation_def, bindings)
                concrete_instances.append(instance)
    
    return concrete_instances
```

### 4.3 Subset Expansion

```python
def expand_subset(subset_def: SetDef, symbol_table: SymbolTable) -> list[tuple]:
    """
    Expand subset to concrete member tuples.
    
    Args:
        subset_def: SetDef node with domain and assignment
        symbol_table: For looking up parent set members
    
    Returns:
        List of tuples representing subset members
    """
    # Get parent set members for each domain dimension
    parent_sets = []
    for parent_set_name in subset_def.domain:
        parent_set = symbol_table.lookup(parent_set_name)
        parent_sets.append(parent_set.members)  # e.g., ['p1', 'p2', 'p3']
    
    # Generate all combinations
    all_combinations = itertools.product(*parent_sets)
    
    # Filter by subset condition
    subset_members = []
    for combination in all_combinations:
        # Bind indices to combination values
        bindings = dict(zip(subset_def.domain, combination))
        
        # Evaluate subset condition with bindings
        if evaluate_condition(subset_def.assignment, bindings):
            subset_members.append(combination)
    
    return subset_members
```

### 4.4 Error Cases and Validation

**Error 1: Undefined Subset**
```gams
Equation e(undefined_set)..
```
**Validation:** Symbol table lookup fails → `UndefinedSymbolError`

**Error 2: Index Count Mismatch**
```gams
Set low(n,n);
Equation e(low(n))..  // Expected 2 indices, got 1
```
**Validation:** `len(indices) != len(subset.domain)` → `IndexMismatchError`

**Error 3: Invalid Index Name**
```gams
Set low(n,n);
Equation e(low(i,j))..  // i,j not aliases of n
```
**Validation:** Index not in parent set → `InvalidIndexError`

**Error 4: Circular Dependency**
```gams
Set a(b), b(a);  // Circular
```
**Validation:** Dependency graph traversal detects cycle → `CircularDependencyError`

---

## Section 5: Subset Expansion Strategies

### 5.1 Eager Expansion (Recommended)

**Approach:** Expand subset to all member tuples at equation declaration time

**Algorithm:**
```python
def eager_expand(subset_def):
    # Evaluate subset condition for all combinations
    # Generate complete list of member tuples
    # Store in symbol table
    pass
```

**Pros:**
- Simple implementation
- No runtime overhead during equation generation
- Easy to debug (can inspect expanded subset)

**Cons:**
- Memory usage for large subsets
- One-time cost at parse time

**Performance (maxmin.gms):**
- Subset `low(n,n)` with n=13 points
- All combinations: 13² = 169 pairs
- Subset members: 78 pairs (lower triangle)
- Memory: ~1KB (negligible)
- Time: <1ms (negligible)

### 5.2 Lazy Expansion (Alternative)

**Approach:** Generate subset members on-demand during equation instantiation

**Algorithm:**
```python
def lazy_expand(subset_def, requested_combination):
    # Check if requested_combination satisfies subset condition
    # Return boolean
    pass
```

**Pros:**
- Lower memory usage (no storage of member list)
- Scales better for very large subsets (rare)

**Cons:**
- More complex implementation
- Repeated evaluation overhead
- Harder to debug

**Performance:**
- For maxmin.gms: No benefit (subset is small)
- Only beneficial for subsets with >10,000 members

### 5.3 Recommendation: Eager Expansion

**Rationale:**
- Simpler implementation (lower risk)
- Better performance for typical models
- Easier to debug and validate
- maxmin.gms subset is small (78 members)

**Benchmark Estimates:**
- Parse time increase: <5ms for maxmin.gms
- Memory increase: <10KB
- Acceptable tradeoff for simplicity

---

## Section 6: IR and MCP Generation

### 6.1 IR Data Structure Design

**Current IR:**
```python
@dataclass
class IREquation:
    name: str
    indices: list[str]  # Simple indices only
    body: IRExpression
```

**Proposed IR:**
```python
@dataclass
class IREquation:
    name: str
    domain_spec: list[DomainElement]  # Supports SubsetDomain
    expanded_instances: Optional[list[EquationInstance]]  # Eagerly expanded
    body: IRExpression

@dataclass
class EquationInstance:
    """Concrete equation instance with bound indices"""
    equation_name: str
    index_bindings: dict[str, str]  # e.g., {'n': 'p2', 'nn': 'p1'}
    body: IRExpression  # Body with indices substituted
```

### 6.2 MCP Generation Algorithm Modifications

**Current Algorithm:**
```python
def generate_mcp(ir_equation):
    for index_values in expand_domain(ir_equation.indices):
        emit_equation_instance(ir_equation, index_values)
```

**Updated Algorithm:**
```python
def generate_mcp(ir_equation):
    if ir_equation.expanded_instances:
        # Subset domain: use pre-expanded instances
        for instance in ir_equation.expanded_instances:
            emit_equation_instance(instance)
    else:
        # Simple domain: expand as before
        for index_values in expand_domain(ir_equation.domain_spec):
            emit_equation_instance(ir_equation, index_values)
```

### 6.3 Example Transformation

**GAMS Input (maxmin.gms line 51):**
```gams
Set n / p1*p3 /;
Set low(n,n);
low(n,nn) = ord(n) > ord(nn);

Equation defdist(low(n,nn));
defdist(low(n,nn)).. dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
```

**IR Representation:**
```python
IREquation(
    name='defdist',
    domain_spec=[SubsetDomain('low', ['n', 'nn'])],
    expanded_instances=[
        EquationInstance(
            equation_name='defdist',
            index_bindings={'n': 'p2', 'nn': 'p1'},
            body=<expression with p2, p1 substituted>
        ),
        EquationInstance(
            equation_name='defdist',
            index_bindings={'n': 'p3', 'nn': 'p1'},
            body=<expression with p3, p1 substituted>
        ),
        EquationInstance(
            equation_name='defdist',
            index_bindings={'n': 'p3', 'nn': 'p2'},
            body=<expression with p3, p2 substituted>
        )
    ],
    body=<original equation body>
)
```

**MCP GAMS Output:**
```gams
// 3 equation instances (subset has 3 members)
defdist_p2_p1.. dist_p2_p1 =e= sqrt(sqr(point_p2_x - point_p1_x) + sqr(point_p2_y - point_p1_y));
defdist_p3_p1.. dist_p3_p1 =e= sqrt(sqr(point_p3_x - point_p1_x) + sqr(point_p3_y - point_p1_y));
defdist_p3_p2.. dist_p3_p2 =e= sqrt(sqr(point_p3_x - point_p2_x) + sqr(point_p3_y - point_p2_y));
```

---

## Section 7: Testing Strategy

### 7.1 Unit Tests

**Grammar Tests:**
```python
def test_parse_simple_domain():
    parse("equation(i,j).. x =e= y;")

def test_parse_subset_domain():
    parse("equation(low(n,nn)).. x =e= y;")

def test_parse_mixed_domain():
    parse("equation(i, low(n,nn), j).. x =e= y;")

def test_parse_error_nested_subset():
    with pytest.raises(ParseError):
        parse("equation(a(b(c))).. x =e= y;")  # Too nested
```

**AST Tests:**
```python
def test_simple_domain_ast():
    ast = parse("equation(i).. ...")
    assert isinstance(ast.domain[0], SimpleDomain)
    assert ast.domain[0].identifier == 'i'

def test_subset_domain_ast():
    ast = parse("equation(low(n,nn)).. ...")
    assert isinstance(ast.domain[0], SubsetDomain)
    assert ast.domain[0].subset_name == 'low'
    assert ast.domain[0].indices == ['n', 'nn']
```

**Semantic Tests:**
```python
def test_subset_expansion():
    # Define subset low(n,n) = ord(n) > ord(nn)
    # Verify expansion produces correct member list
    pass

def test_undefined_subset_error():
    # Reference undefined subset
    # Verify UndefinedSymbolError raised
    pass

def test_index_mismatch_error():
    # Subset expects 2 indices, provide 1
    # Verify IndexMismatchError raised
    pass
```

### 7.2 Integration Tests

**Test Case 1: Minimal Subset**
```gams
Set n / p1*p3 /;
Set low(n,n);
low(n,nn) = ord(n) > ord(nn);

Equation e(low(n,nn));
e(low(n,nn)).. x(n) + x(nn) =e= 0;
```

**Expected:** Parse succeeds, 3 equation instances generated

**Test Case 2: Empty Subset**
```gams
Set n / p1*p3 /;
Set empty(n,n);
empty(n,nn) = 1 = 0;  // Always false

Equation e(empty);
e(empty).. x =e= 0;
```

**Expected:** Parse succeeds, 0 equation instances generated

**Test Case 3: Complex Condition**
```gams
Set n / p1*p10 /;
Set complex(n,n);
complex(n,nn) = (ord(n) > ord(nn)) and (ord(n) < 5);

Equation e(complex);
e(complex).. x(n) =e= x(nn);
```

**Expected:** Parse succeeds, 6 instances: {(p2,p1), (p3,p1), (p3,p2), (p4,p1), (p4,p2), (p4,p3)}

### 7.3 End-to-End Tests

**Test Case: maxmin.gms Subset Patterns**
```gams
// From maxmin.gms lines 51, 53, 55
defdist(low(n,nn))..   dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
mindist1(low)..        mindist   =l= dist(low);
mindist1a(low(n,nn)).. mindist   =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
```

**Expected:**
- Parse succeeds for all 3 lines
- 78 equation instances generated for each (13 choose 2)
- Parse rate: 18% → 27% (3 lines unlocked, next blocker at line 57)

---

## Section 8: Implementation Complexity Assessment

### 8.1 Effort Breakdown

| Component | Tasks | Estimated Time | Risk Level |
|-----------|-------|----------------|------------|
| **Grammar** | Add `domain_element`, `subset_domain` rules; Update `equation_def` | 3-4 hours | HIGH |
| **AST** | Define `DomainElement`, `SimpleDomain`, `SubsetDomain`; Update `EquationDef`; Update visitors | 2-3 hours | MEDIUM |
| **Semantic** | Symbol table lookup; Index validation; Subset expansion; Error handling | 4-6 hours | HIGH |
| **IR/MCP** | Add `expanded_instances` field; Update MCP generator | 1-2 hours (included in Semantic) | MEDIUM |
| **Testing** | Unit tests (10+); Integration tests (5+); End-to-end (maxmin.gms) | 1-2 hours | MEDIUM |
| **TOTAL** | | **10-14 hours** | **HIGH** |

### 8.2 Risk Assessment

**Risk Level: HIGH (9/10)**

**Risk Factors:**
1. **Grammar Complexity:** Recursive parsing rules can introduce ambiguities
2. **Semantic Complexity:** Subset expansion requires full expression evaluator
3. **Limited Testing:** Only 1 test file (maxmin.gms) with subset patterns
4. **Unknown Unknowns:** May discover additional complexity during implementation
5. **Slippage Risk:** 14-hour estimate could become 16-20 hours

**Mitigation:**
- Thorough design upfront (this document)
- Incremental implementation with testing at each phase
- Fallback: Revert if exceeding 16 hours

### 8.3 Partial Implementation Feasibility

**Question:** Can we implement partial subset support (e.g., shorthand only)?

**Answer:** **NO - All-or-nothing**

**Rationale:**
- maxmin.gms uses BOTH explicit `low(n,nn)` AND shorthand `low`
- Cannot support one without the other
- Lines 51, 53, 55 are interdependent (all needed for model to work)

---

## Section 9: Alternative Approaches (Considered and Rejected)

### 9.1 Preprocessing Transformation

**Idea:** Transform subset syntax to conditional syntax during preprocessing

**Example:**
```gams
// Original
defdist(low(n,nn)).. dist(low) =e= ...

// Transformed
defdist(n,nn)$(ord(n) > ord(nn)).. dist(n,nn) =e= ...
```

**Rejected Because:**
- Requires runtime subset membership checks (less efficient)
- Changes GAMS semantics (more equations generated, some skipped)
- Doesn't match GAMS behavior (defeats purpose of subset filtering)

### 9.2 Explicit Index Expansion

**Idea:** Manually expand subset to explicit indices

**Example:**
```gams
// Original
defdist(low(n,nn)).. ...

// Expanded
defdist('p2','p1').. ...
defdist('p3','p1').. ...
...
```

**Rejected Because:**
- Not scalable (13 points = 78 equations to write)
- Error-prone (easy to miss combinations)
- Defeats abstraction (GAMS purpose is to avoid this)

### 9.3 Modified GAMSLIB Files

**Idea:** Rewrite maxmin.gms to avoid subset syntax

**Rejected Because:**
- Parser must support standard GAMS syntax
- Cannot modify test suite files
- Subset indexing is idiomatic GAMS (used in many models)

---

## Section 10: GO/NO-GO Decision for Sprint 11

### 10.1 Sprint 11 Context

**Sprint 11 Scope (from PROJECT_PLAN.md):**
1. **Aggressive Simplification:** 12-15 hours (primary feature)
2. **CI Regression Guardrails:** 6-8 hours
3. **Diagnostics Mode:** 4-5 hours
4. **Process Improvements:** 2-3 hours

**Total Committed:** 24-31 hours  
**Sprint 11 Capacity (from Sprint 10 velocity):** 20-30 hours

### 10.2 maxmin.gms ROI Analysis

**Effort:** 10-14 hours (nested indexing only)  
**Benefit:** Unlocks maxmin.gms from 18% to 56% parse rate  
**Remaining Blockers:** 4 more categories (aggregation, multi-model, loop tuples, misc)

**To reach 100% parse on maxmin.gms:**
- Nested indexing: 10-14 hours
- Aggregation functions: 6-10 hours (same as circle.gms)
- Multi-model declarations: 3-4 hours
- Loop tuples: 2-3 hours
- Misc features: 2-3 hours
- **Total: 23-34 hours** for complete maxmin.gms support

**Alternative: Aggressive Simplification**
- Effort: 12-15 hours
- Benefit: ≥20% derivative term reduction on ≥50% models
- Impact: Core feature for Sprint 11, high user value

### 10.3 Risk Analysis

**If GO (implement in Sprint 11):**
- **Risk:** 10-14 hour estimate may slip to 16-20 hours
- **Impact:** Crowds out aggressive simplification or CI guardrails
- **Consequence:** Sprint 11 goals not met (neither simplification nor maxmin complete)
- **Probability:** 40% (based on complexity 9/10)

**If DEFER (defer to Sprint 12):**
- **Risk:** Maintains 90% Tier 1 parse rate (9/10 models)
- **Impact:** Sprint 11 focuses on high-value features (simplification, CI, diagnostics)
- **Consequence:** All Sprint 11 goals met, maxmin.gms addressed in dedicated sprint
- **Probability:** 90% success rate

### 10.4 Sprint 12 Proposal

**Sprint 12 Theme:** "Complete Tier 1 Coverage" (100% parse rate)

**Sprint 12 Scope:**
1. **Nested/Subset Indexing:** 10-14 hours
2. **Aggregation Functions (circle.gms + maxmin.gms):** 6-10 hours
3. **Multi-Model Declarations:** 3-4 hours
4. **Loop Tuples:** 2-3 hours
5. **Misc Features:** 2-3 hours

**Total:** 23-34 hours (fits within sprint capacity with dedicated focus)

**Sprint 12 Goal:** 100% Tier 1 parse rate (10/10 models)

**Sprint 12 Benefits:**
- Dedicated sprint for maxmin.gms (no competing priorities)
- Can address ALL blockers (not just subset indexing)
- Lower risk (no rush, thorough implementation)
- Clear success metric (100% Tier 1)

### 10.5 FINAL RECOMMENDATION

## ✅ **DEFER nested/subset indexing to Sprint 12**

### Rationale

1. **Sprint 11 Capacity Conflict:**
   - Aggressive simplification (12-15h) + CI guardrails (6-8h) + Diagnostics (4-5h) = 22-28h
   - Adding nested indexing (10-14h) would require 32-42h total
   - Sprint 11 capacity: 20-30h (from Sprint 10 velocity)
   - **Conclusion:** Cannot fit both aggressive simplification AND nested indexing

2. **High Risk, Low Immediate ROI:**
   - Complexity 9/10, high slippage risk (10-14h could become 16-20h)
   - Only unlocks maxmin.gms to 56% (still 4 blocker categories remaining)
   - Better to wait for Sprint 12 and do ALL maxmin.gms blockers together

3. **Better Alternatives:**
   - Aggressive simplification: Higher user value (≥20% term reduction)
   - CI guardrails: Critical for preventing regressions
   - Diagnostics: Improves developer UX
   - All three have clearer value propositions than partial maxmin.gms unlock

4. **Sprint 12 is Better Positioned:**
   - Dedicated sprint for 100% Tier 1 coverage
   - Can implement ALL maxmin.gms blockers (23-34h total)
   - Lower risk (no competing priorities)
   - Clear success criteria (10/10 models)

5. **90% is Excellent Progress:**
   - Current: 90% Tier 1 parse rate (9/10 models)
   - Sprint 10 achieved this 4 days ahead of schedule
   - Demonstrates parser maturity
   - Final 10% (maxmin.gms) deserves dedicated sprint

### Implementation Plan

**Sprint 11:**
- Focus: Aggressive simplification + CI guardrails + Diagnostics + Process improvements
- maxmin.gms: Remains at 18% (deferred)
- Parse rate: 90% maintained

**Sprint 12:**
- Theme: "Complete Tier 1 Coverage"
- Implement: All 5 maxmin.gms blocker categories
- Goal: 100% Tier 1 parse rate (10/10 models)
- Budget: 23-34 hours

### Acceptance

This recommendation should be reviewed with the team and accepted/rejected before Sprint 11 Day 1. If rejected (GO decision), this research provides implementation-ready guidance for Sprint 11 implementation.

---

## Appendix A: References

**GAMS Documentation:**
- GAMS User Guide: Sets and Subsets
- GAMS User Guide: Equation Domains
- GAMS User Guide: Conditional Set Operations

**Prior Work:**
- Sprint 10 Blocker Analysis: docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md
- Sprint 10 Retrospective: docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md

**Test Files:**
- maxmin.gms: tests/fixtures/gamslib/maxmin.gms

---

## Appendix B: Implementation Checklist (If GO Decision)

### Phase 1: Grammar (3-4 hours)
- [ ] Add `domain_element` rule to grammar
- [ ] Add `simple_domain` rule
- [ ] Add `subset_domain` rule
- [ ] Update `equation_def` to use `domain_element`
- [ ] Test grammar on maxmin.gms lines 51, 53, 55
- [ ] Verify backward compatibility on existing tests

### Phase 2: AST (2-3 hours)
- [ ] Define `DomainElement` abstract base class
- [ ] Define `SimpleDomain` dataclass
- [ ] Define `SubsetDomain` dataclass
- [ ] Update `EquationDef` to use `list[DomainElement]`
- [ ] Update AST construction logic
- [ ] Update all visitors to handle new types
- [ ] Write unit tests for AST nodes

### Phase 3: Semantic (4-6 hours)
- [ ] Implement subset lookup in symbol table
- [ ] Implement index validation logic
- [ ] Implement subset expansion algorithm
- [ ] Implement equation instance generation
- [ ] Add error handling (undefined, mismatch, invalid)
- [ ] Write unit tests for semantic resolution
- [ ] Test on maxmin.gms patterns

### Phase 4: Testing (1-2 hours)
- [ ] Write integration tests (minimal subset, empty subset, complex)
- [ ] Test maxmin.gms end-to-end
- [ ] Verify parse rate improvement: 18% → 27%
- [ ] Run full test suite (verify no regressions)

### Phase 5: Documentation
- [ ] Update KNOWN_UNKNOWNS.md with verification results
- [ ] Update PREP_PLAN.md with implementation status
- [ ] Update CHANGELOG.md

**Total:** 10-14 hours (optimistic), 16-20 hours (realistic with unknowns)

---

**End of Research Document**

**Next Steps:**
1. Review recommendation with team
2. Make GO/NO-GO decision
3. If GO: Use this document as implementation guide
4. If DEFER: Proceed with Sprint 11 aggressive simplification focus
