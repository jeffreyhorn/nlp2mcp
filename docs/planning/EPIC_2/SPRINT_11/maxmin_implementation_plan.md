# GAMS Nested/Subset Indexing Implementation Plan

**Date:** 2025-11-25
**Status:** DEFER to Sprint 12
**Effort Estimate:** 10-14 hours
**Risk Level:** HIGH (9/10)

## Executive Summary

This document provides a detailed implementation plan for adding GAMS nested/subset indexing support to nlp2mcp. The feature enables equation domains like `equation(low(n,nn))` where `low` is a subset with explicit indices.

**Key Decision:** Based on Sprint 11 capacity analysis, this implementation is **DEFERRED to Sprint 12**. Sprint 11 is already at capacity (22-28h committed vs 20-30h capacity) with higher-priority features (aggressive simplification, CI guardrails, diagnostics). This feature would push the sprint to 32-42h with high slippage risk.

**Sprint 12 Rationale:** Deferring allows us to implement ALL maxmin.gms features together (23-34h total effort) rather than partially implementing nested indexing now and still having 4 more blocker categories remaining.

## Background

### Current State

The nlp2mcp parser currently supports simple equation domains:
```gams
Equation supply(i), demand(j);
supply(i)..  sum(j, x(i,j)) =l= capacity(i);
```

### Target State

We need to support subset-based equation domains:
```gams
Set low(n,n) 'lower triangle';
low(n,nn) = ord(n) > ord(nn);

Equation defdist(low(n,nn));
defdist(low(n,nn))..  dist(low) =e= sqrt(...);
```

### Blocker Analysis

From maxmin.gms analysis, nested/subset indexing appears in:
- **Line 51:** `defdist(low(n,nn))..` - Subset with explicit indices
- **Line 56:** `mindist1(low)..` - Subset with inferred indices (shorthand)
- **Impact:** Primary blocker preventing parsing of 5+ equations in maxmin.gms

Current parser error:
```
No terminal matches '(' at line 51 col 12
Expected: ')', 'comma'
```

The grammar expects `equation_def: ID "(" id_list ")"` where `id_list` is flat identifiers, not nested expressions.

## Implementation Architecture

### Phase Overview

1. **Phase 1: Grammar Changes** (3-4 hours, HIGH risk)
2. **Phase 2: AST Changes** (2-3 hours, MEDIUM risk)
3. **Phase 3: Semantic Analyzer** (4-6 hours, HIGH risk)
4. **Phase 4: IR/MCP Generation** (included in Phase 3)
5. **Phase 5: Testing & Validation** (1-2 hours, MEDIUM risk)

**Total:** 10-14 hours baseline, 16-20 hours with 40% slippage risk

---

## Phase 1: Grammar Changes (3-4 hours)

### Objective

Extend the Lark grammar to support nested domain elements in equation definitions.

### Current Grammar

```lark
equation_def: ID "(" id_list ")" ".." equation_body

id_list: ID ("," ID)*
```

### Proposed Grammar (Option 1 - Recommended)

```lark
equation_def: ID "(" domain_list ")" ".." equation_body
            | ID ".." equation_body  // No domain shorthand

domain_list: domain_element ("," domain_element)*

domain_element: simple_domain | subset_domain

simple_domain: ID

subset_domain: ID "(" id_list ")"

id_list: ID ("," ID)*
```

**Rationale:**
- Explicit syntax clearly distinguishes simple domains from subset domains
- Easier to parse and validate (no ambiguity)
- Better error messages for malformed input
- Lower implementation risk than alternatives

### Alternative Grammar Options (NOT Recommended)

**Option 2: Recursive Domain Elements**
```lark
domain_element: ID ("(" domain_list ")")?
```
- Risk: Ambiguity with function calls
- Risk: Harder to validate at parse time

**Option 3: Unified with Indexing Expressions**
```lark
domain_element: indexing_expr
```
- Risk: Over-generalization (allows invalid GAMS syntax)
- Risk: Grammar conflicts with other rules

### Implementation Steps

1. **Backup current grammar** (`src/nlp2mcp/grammar.lark`)
2. **Add new rules:**
   - `domain_list` rule (replaces direct `id_list` in `equation_def`)
   - `domain_element` rule (base for simple/subset)
   - `simple_domain` rule (wraps ID)
   - `subset_domain` rule (ID with nested id_list)
3. **Update `equation_def` rule:**
   - Change `ID "(" id_list ")"` to `ID "(" domain_list ")"`
4. **Test grammar in isolation:**
   - Create test cases for simple domains: `supply(i)`
   - Create test cases for subset domains: `defdist(low(n,nn))`
   - Create test cases for mixed domains: `foo(i, low(n,nn), k)`
   - Verify error messages for invalid syntax
5. **Run existing parser tests:**
   - Ensure no regressions in simple domain parsing
   - Validate that all existing test fixtures still parse correctly

### Testing Strategy

**Unit tests:**
```python
def test_simple_domain_parsing():
    """Test that simple domains still parse correctly"""
    code = "equation supply(i);"
    tree = parse_gams(code)
    assert tree is not None

def test_subset_domain_parsing():
    """Test that subset domains parse correctly"""
    code = "equation defdist(low(n,nn));"
    tree = parse_gams(code)
    assert tree is not None

def test_mixed_domain_parsing():
    """Test mixed simple and subset domains"""
    code = "equation foo(i, low(n,nn), k);"
    tree = parse_gams(code)
    assert tree is not None

def test_invalid_nested_domain():
    """Test that deeply nested domains are rejected"""
    code = "equation foo(bar(baz(i)));"
    with pytest.raises(ParseError):
        parse_gams(code)
```

### Risk Mitigation

- **Risk:** Grammar conflicts with existing rules (function calls, indexing)
  - **Mitigation:** Use explicit `subset_domain` rule with clear structure
  - **Mitigation:** Extensive grammar testing before AST integration

- **Risk:** Breaking existing equation parsing
  - **Mitigation:** Keep `simple_domain` as separate rule (backward compatible)
  - **Mitigation:** Run full test suite after grammar changes

- **Risk:** Ambiguity in parser precedence
  - **Mitigation:** Use explicit rule ordering in Lark (simple_domain | subset_domain)
  - **Mitigation:** Add negative test cases for ambiguous inputs

---

## Phase 2: AST Changes (2-3 hours)

### Objective

Create AST nodes to represent simple and subset domain elements in equation definitions.

### Current AST

```python
@dataclass
class EquationDef(Statement):
    name: str
    domain: list[str]  # Flat list of identifiers
    body: EquationBody
```

### Proposed AST

```python
from abc import ABC, abstractmethod

@dataclass
class DomainElement(ABC):
    """Base class for equation domain elements"""
    
    @abstractmethod
    def get_identifiers(self) -> list[str]:
        """Return all identifiers used in this domain element"""
        pass

@dataclass
class SimpleDomain(DomainElement):
    """Simple identifier domain: i, j, k
    
    Examples:
        supply(i) -> SimpleDomain(identifier='i')
        demand(j) -> SimpleDomain(identifier='j')
    """
    identifier: str
    
    def get_identifiers(self) -> list[str]:
        return [self.identifier]

@dataclass
class SubsetDomain(DomainElement):
    """Subset with explicit indices: low(n,nn)
    
    Examples:
        defdist(low(n,nn)) -> SubsetDomain(subset_name='low', indices=['n', 'nn'])
        foo(active(i)) -> SubsetDomain(subset_name='active', indices=['i'])
    """
    subset_name: str
    indices: list[str]
    
    def get_identifiers(self) -> list[str]:
        return self.indices

@dataclass
class EquationDef(Statement):
    """Equation definition with support for subset domains
    
    Examples:
        supply(i)..  -> EquationDef(name='supply', domain=[SimpleDomain('i')], ...)
        defdist(low(n,nn)).. -> EquationDef(name='defdist', 
                                             domain=[SubsetDomain('low', ['n','nn'])], ...)
        foo(i, low(n,nn), k).. -> EquationDef(name='foo',
                                               domain=[SimpleDomain('i'),
                                                       SubsetDomain('low', ['n','nn']),
                                                       SimpleDomain('k')], ...)
    """
    name: str
    domain: list[DomainElement]  # Changed from list[str]
    body: EquationBody
```

### Implementation Steps

1. **Create domain element classes:**
   - Add `DomainElement` abstract base class to `src/nlp2mcp/ast_nodes.py`
   - Add `SimpleDomain` concrete class
   - Add `SubsetDomain` concrete class
   - Add docstrings with examples

2. **Update EquationDef:**
   - Change `domain: list[str]` to `domain: list[DomainElement]`
   - Update docstring with new examples

3. **Update transformer:**
   - Modify `GAMSTransformer` in `src/nlp2mcp/transformer.py`
   - Add `simple_domain` transformation: `return SimpleDomain(identifier=str(children[0]))`
   - Add `subset_domain` transformation: `return SubsetDomain(subset_name=str(children[0]), indices=[str(c) for c in children[1:]])`
   - Add `domain_list` transformation: `return list(children)`
   - Update `equation_def` transformation to handle `DomainElement` list

4. **Update helper methods:**
   - Create `EquationDef.get_all_identifiers() -> list[str]` method
   - Flatten all identifiers from domain elements for compatibility

5. **Test AST construction:**
   - Unit tests for SimpleDomain creation
   - Unit tests for SubsetDomain creation
   - Integration tests for EquationDef with mixed domains

### Testing Strategy

**Unit tests:**
```python
def test_simple_domain_ast():
    """Test SimpleDomain AST node"""
    domain = SimpleDomain(identifier='i')
    assert domain.get_identifiers() == ['i']

def test_subset_domain_ast():
    """Test SubsetDomain AST node"""
    domain = SubsetDomain(subset_name='low', indices=['n', 'nn'])
    assert domain.get_identifiers() == ['n', 'nn']

def test_equation_def_mixed_domains():
    """Test EquationDef with mixed domain types"""
    eq = EquationDef(
        name='foo',
        domain=[
            SimpleDomain('i'),
            SubsetDomain('low', ['n', 'nn']),
            SimpleDomain('k')
        ],
        body=...
    )
    all_ids = [id for d in eq.domain for id in d.get_identifiers()]
    assert all_ids == ['i', 'n', 'nn', 'k']
```

**Integration tests:**
```python
def test_parse_subset_domain_to_ast():
    """Test parsing subset domain into correct AST"""
    code = """
    equation defdist(low(n,nn));
    defdist(low(n,nn)).. dist(low) =e= 1;
    """
    ast = parse_gams_to_ast(code)
    eq_def = ast.statements[0]
    assert isinstance(eq_def, EquationDef)
    assert len(eq_def.domain) == 1
    assert isinstance(eq_def.domain[0], SubsetDomain)
    assert eq_def.domain[0].subset_name == 'low'
    assert eq_def.domain[0].indices == ['n', 'nn']
```

### Risk Mitigation

- **Risk:** Breaking existing code that expects `domain: list[str]`
  - **Mitigation:** Add compatibility method `get_all_identifiers()` that returns flat list
  - **Mitigation:** Audit all code that accesses `EquationDef.domain`
  - **Mitigation:** Update incrementally with deprecation warnings

- **Risk:** Transformer complexity
  - **Mitigation:** Keep transformation logic simple (direct children mapping)
  - **Mitigation:** Add comprehensive transformer unit tests
  - **Mitigation:** Use explicit tree matching in transformer methods

---

## Phase 3: Semantic Analyzer (4-6 hours)

### Objective

Implement semantic resolution for subset domains in equation definitions, including:
1. Subset lookup and validation
2. Index matching and validation
3. Subset expansion to concrete equation instances
4. Error reporting for invalid subset usage

### Current Semantic Analysis

The semantic analyzer currently:
- Resolves set and parameter declarations
- Validates simple equation domain identifiers
- Does NOT handle subset expansion

### Proposed Semantic Resolution

#### Algorithm Overview

```
For each EquationDef with SubsetDomain elements:
  1. Resolve subset reference (lookup Set declaration)
  2. Validate subset dimensionality matches indices
  3. Expand subset to concrete members (static evaluation)
  4. Generate equation instances for each subset member
  5. Store instances in symbol table with metadata
```

#### Detailed Algorithm

**Step 1: Subset Lookup**
```python
def resolve_subset_domain(self, subset_domain: SubsetDomain, scope: SymbolTable) -> SetInfo:
    """Resolve subset reference to Set declaration"""
    subset_name = subset_domain.subset_name
    
    # Lookup in symbol table
    set_info = scope.lookup(subset_name, SymbolType.SET)
    if set_info is None:
        raise SemanticError(f"Undefined subset '{subset_name}'")
    
    # Validate it's actually a subset (has parent set)
    if not set_info.is_subset:
        raise SemanticError(f"'{subset_name}' is not a subset (no parent set)")
    
    return set_info
```

**Step 2: Dimensionality Validation**
```python
def validate_subset_indices(self, subset_domain: SubsetDomain, set_info: SetInfo):
    """Validate subset indices match subset dimensionality"""
    expected_dim = set_info.dimensionality
    actual_dim = len(subset_domain.indices)
    
    if expected_dim != actual_dim:
        raise SemanticError(
            f"Subset '{subset_domain.subset_name}' expects {expected_dim} indices, "
            f"got {actual_dim}: {subset_domain.indices}"
        )
    
    # Validate index names are valid identifiers
    for idx in subset_domain.indices:
        if not idx.isidentifier():
            raise SemanticError(f"Invalid index name: '{idx}'")
```

**Step 3: Subset Expansion (Eager Strategy)**
```python
def expand_subset(self, set_info: SetInfo) -> list[tuple[str, ...]]:
    """Expand subset to concrete members
    
    For Sprint 11, use EAGER evaluation (expand at compile time).
    Future: Support LAZY evaluation for runtime subsets.
    """
    # Check if subset is static (evaluable at compile time)
    if not set_info.is_static:
        raise SemanticError(
            f"Dynamic subsets not yet supported: '{set_info.name}'. "
            f"Subset condition contains runtime expressions."
        )
    
    # Evaluate subset condition
    members = []
    parent_set = set_info.parent_set
    
    # Iterate over parent set Cartesian product
    for element_tuple in itertools.product(*[parent_set.members] * set_info.dimensionality):
        # Evaluate subset condition with element_tuple
        if self.evaluate_subset_condition(set_info.condition, element_tuple):
            members.append(element_tuple)
    
    return members
```

**Step 4: Generate Equation Instances**
```python
def generate_equation_instances(self, eq_def: EquationDef) -> list[EquationInstance]:
    """Generate concrete equation instances for subset domains
    
    Examples:
        defdist(low(n,nn)) with low = {(p1,p2), (p2,p3), ...}
        -> [defdist['p1','p2'], defdist['p2','p3'], ...]
    """
    instances = []
    
    # Build Cartesian product of all domain elements
    domain_iterators = []
    for domain_elem in eq_def.domain:
        if isinstance(domain_elem, SimpleDomain):
            # Simple domain: use full set
            set_info = self.lookup_set(domain_elem.identifier)
            domain_iterators.append([(domain_elem.identifier, m) for m in set_info.members])
        
        elif isinstance(domain_elem, SubsetDomain):
            # Subset domain: use expanded subset members
            set_info = self.resolve_subset_domain(domain_elem, self.scope)
            self.validate_subset_indices(domain_elem, set_info)
            subset_members = self.expand_subset(set_info)
            
            # Map subset members to index bindings
            domain_iterators.append([
                (domain_elem.indices, member_tuple) 
                for member_tuple in subset_members
            ])
    
    # Generate instances from Cartesian product
    for binding in itertools.product(*domain_iterators):
        # Flatten bindings into index_map
        index_map = {}
        for idx_name, value in binding:
            if isinstance(idx_name, list):
                # SubsetDomain: multiple indices
                for i, idx in enumerate(idx_name):
                    index_map[idx] = value[i]
            else:
                # SimpleDomain: single index
                index_map[idx_name] = value
        
        # Create equation instance
        instance = EquationInstance(
            equation_name=eq_def.name,
            index_map=index_map,
            body=eq_def.body
        )
        instances.append(instance)
    
    return instances
```

**Step 5: Store Instances**
```python
def register_equation_instances(self, eq_def: EquationDef):
    """Register equation instances in symbol table"""
    instances = self.generate_equation_instances(eq_def)
    
    # Store in symbol table
    eq_info = EquationInfo(
        name=eq_def.name,
        domain=eq_def.domain,
        instances=instances,
        has_subset_domain=any(isinstance(d, SubsetDomain) for d in eq_def.domain)
    )
    
    self.scope.register(eq_def.name, SymbolType.EQUATION, eq_info)
```

### Implementation Steps

1. **Add SetInfo metadata:**
   - Add `is_subset: bool` field (True if has parent set)
   - Add `parent_set: Optional[SetInfo]` field
   - Add `condition: Optional[Expression]` field (subset assignment condition)
   - Add `is_static: bool` field (True if condition is compile-time evaluable)
   - Add `dimensionality: int` field

2. **Implement subset resolution:**
   - `resolve_subset_domain()` method
   - `validate_subset_indices()` method
   - Error handling for undefined subsets

3. **Implement subset expansion:**
   - `expand_subset()` method (eager evaluation)
   - `evaluate_subset_condition()` helper (evaluate ord(), etc.)
   - Handle 2D subsets (Cartesian product of parent set)

4. **Implement instance generation:**
   - `generate_equation_instances()` method
   - Cartesian product logic for mixed domains
   - Index binding map construction

5. **Update symbol table:**
   - Add `EquationInfo` class with `instances` field
   - `register_equation_instances()` method
   - Query methods for instance lookup

6. **Error handling:**
   - Undefined subset errors
   - Dimensionality mismatch errors
   - Dynamic subset errors (not supported yet)
   - Circular dependency errors

### Testing Strategy

**Unit tests:**
```python
def test_subset_resolution():
    """Test subset lookup and validation"""
    # Setup symbol table with subset
    scope = SymbolTable()
    scope.register('n', SymbolType.SET, SetInfo(name='n', members=['p1','p2','p3']))
    scope.register('low', SymbolType.SET, SetInfo(
        name='low',
        is_subset=True,
        parent_set='n',
        dimensionality=2
    ))
    
    # Resolve subset domain
    analyzer = SemanticAnalyzer(scope)
    subset_domain = SubsetDomain(subset_name='low', indices=['n', 'nn'])
    set_info = analyzer.resolve_subset_domain(subset_domain, scope)
    
    assert set_info.name == 'low'
    assert set_info.is_subset == True

def test_subset_expansion():
    """Test subset expansion to concrete members"""
    # Setup subset: low(n,nn) = ord(n) > ord(nn)
    set_info = SetInfo(
        name='low',
        is_subset=True,
        parent_set=SetInfo(name='n', members=['p1','p2','p3']),
        condition=OrdComparison(...),  # ord(n) > ord(nn)
        is_static=True,
        dimensionality=2
    )
    
    analyzer = SemanticAnalyzer()
    members = analyzer.expand_subset(set_info)
    
    # low = {(p2,p1), (p3,p1), (p3,p2)}
    assert len(members) == 3
    assert ('p2', 'p1') in members
    assert ('p3', 'p1') in members
    assert ('p3', 'p2') in members

def test_equation_instance_generation():
    """Test equation instance generation for subset domains"""
    eq_def = EquationDef(
        name='defdist',
        domain=[SubsetDomain('low', ['n', 'nn'])],
        body=...
    )
    
    analyzer = SemanticAnalyzer()
    # Mock subset expansion
    analyzer.expand_subset = lambda si: [('p2','p1'), ('p3','p1'), ('p3','p2')]
    
    instances = analyzer.generate_equation_instances(eq_def)
    
    assert len(instances) == 3
    assert instances[0].index_map == {'n': 'p2', 'nn': 'p1'}
    assert instances[1].index_map == {'n': 'p3', 'nn': 'p1'}
    assert instances[2].index_map == {'n': 'p3', 'nn': 'p2'}
```

**Integration tests:**
```python
def test_maxmin_subset_semantic_analysis():
    """Test full semantic analysis of maxmin.gms subset usage"""
    code = """
    Set n / p1*p3 /;
    Set low(n,n);
    Alias (n, nn);
    low(n,nn) = ord(n) > ord(nn);
    
    Equation defdist(low(n,nn));
    defdist(low(n,nn)).. dist(low) =e= 1;
    """
    
    ast = parse_gams_to_ast(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    
    # Validate equation instances
    eq_info = analyzer.scope.lookup('defdist', SymbolType.EQUATION)
    assert eq_info.has_subset_domain == True
    assert len(eq_info.instances) == 3
```

### Risk Mitigation

- **Risk:** Subset condition evaluation complexity (ord(), card(), etc.)
  - **Mitigation:** Implement only `ord()` function for Sprint 11 (covers maxmin.gms)
  - **Mitigation:** Add clear error for unsupported subset conditions
  - **Mitigation:** Document limitations in KNOWN_UNKNOWNS.md

- **Risk:** Performance issues with large subsets (n=100 -> 9900 pairs)
  - **Mitigation:** Eager evaluation is acceptable for Sprint 11 scope
  - **Mitigation:** Add performance benchmarks to test suite
  - **Mitigation:** Document performance characteristics

- **Risk:** Index binding conflicts in complex cases
  - **Mitigation:** Use explicit index_map structure
  - **Mitigation:** Add validation for index name collisions
  - **Mitigation:** Comprehensive test coverage for edge cases

---

## Phase 4: IR/MCP Generation (included in Phase 3)

### Objective

Generate correct IR and MCP representations for equations with subset domains.

### Changes Required

**IR Generation:**
```python
def generate_equation_ir(self, eq_def: EquationDef, eq_info: EquationInfo) -> list[IREquation]:
    """Generate IR equations from instances"""
    ir_equations = []
    
    for instance in eq_info.instances:
        # Create IR equation with concrete indices
        ir_eq = IREquation(
            name=f"{eq_def.name}[{','.join(instance.index_map.values())}]",
            body=self.instantiate_body(eq_def.body, instance.index_map),
            type=eq_def.body.constraint_type
        )
        ir_equations.append(ir_eq)
    
    return ir_equations
```

**MCP Generation:**
```python
def generate_equation_mcp(self, ir_equations: list[IREquation]) -> dict:
    """Generate MCP constraint objects"""
    mcp_constraints = []
    
    for ir_eq in ir_equations:
        mcp_constraint = {
            "type": ir_eq.type,  # "eq", "le", "ge"
            "name": ir_eq.name,  # "defdist[p2,p1]"
            "lhs": self.generate_expression_mcp(ir_eq.body.lhs),
            "rhs": self.generate_expression_mcp(ir_eq.body.rhs)
        }
        mcp_constraints.append(mcp_constraint)
    
    return {"constraints": mcp_constraints}
```

### Testing Strategy

**Integration tests:**
```python
def test_subset_equation_ir_generation():
    """Test IR generation for subset equations"""
    code = """
    Set n / p1*p3 /;
    Set low(n,n);
    low(n,nn) = ord(n) > ord(nn);
    
    Equation defdist(low(n,nn));
    defdist(low(n,nn)).. dist(low) =e= 1;
    """
    
    ir = generate_ir(code)
    
    # Should generate 3 concrete equations
    assert len(ir.equations) == 3
    assert ir.equations[0].name == "defdist[p2,p1]"
    assert ir.equations[1].name == "defdist[p3,p1]"
    assert ir.equations[2].name == "defdist[p3,p2]"

def test_subset_equation_mcp_generation():
    """Test MCP generation for subset equations"""
    code = """
    Set n / p1*p3 /;
    Set low(n,n);
    low(n,nn) = ord(n) > ord(nn);
    
    Equation defdist(low(n,nn));
    defdist(low(n,nn)).. x =e= 1;
    """
    
    mcp = generate_mcp(code)
    
    # Should generate 3 MCP constraints
    assert len(mcp["constraints"]) == 3
    assert mcp["constraints"][0]["name"] == "defdist[p2,p1]"
    assert mcp["constraints"][0]["type"] == "eq"
```

---

## Phase 5: Testing & Validation (1-2 hours)

### Test Coverage Strategy

**1. Unit Tests (Phases 1-4)**
- Grammar rules (simple_domain, subset_domain, domain_list)
- AST nodes (SimpleDomain, SubsetDomain)
- Transformer methods
- Semantic resolution methods
- IR generation methods

**2. Integration Tests**
- End-to-end parsing: grammar -> AST -> semantic -> IR -> MCP
- Minimal test case: `tests/synthetic/nested_subset_indexing.gms`
- maxmin.gms equation parsing (lines 51, 56)

**3. Regression Tests**
- All existing test fixtures must still pass
- No breaking changes to simple equation domains

### Minimal Test Case

Create `tests/synthetic/nested_subset_indexing.gms`:
```gams
$title Nested/Subset Indexing Test Case

Set n 'base set' / p1*p3 /;
Set low(n,n) 'lower triangle subset';

Alias (n, nn);

* Subset assignment: static condition
low(n,nn) = ord(n) > ord(nn);

* Display subset members (should be 3 pairs)
Display low;

Variable dist(n,n);
Equation defdist(low(n,nn));

* Equation with explicit subset indices
defdist(low(n,nn)).. dist(n,nn) =e= 1;

Model test /all/;
```

**Expected results:**
- Parse rate: 100%
- AST: 1 EquationDef with SubsetDomain
- Semantic: 3 equation instances
- IR: 3 concrete equations
- MCP: 3 constraints

### Validation Against maxmin.gms

**Target lines:**
- Line 51: `defdist(low(n,nn)).. dist(low) =e= sqrt(...);`
- Line 56: `mindist1(low).. mindist =l= dist(low);`

**Expected improvements:**
- Parse rate: 18% -> 56% (38% improvement)
- Successfully parse 5+ equations with subset domains

**Remaining blockers:**
- Aggregation operators (sum, sqrt)
- Multi-model blocks
- Loop tuples
- Misc (variable bounds, display)

---

## Integration with Sprint 11 (IF GO Decision Made)

**Note:** Current recommendation is DEFER to Sprint 12. This section describes integration IF the GO decision is made despite capacity concerns.

### Timeline

**Week 1 (Days 1-3):**
- Day 1: Grammar changes + AST changes (5-7h)
- Day 2-3: Semantic analyzer (4-6h)

**Week 2 (Days 4-5):**
- Day 4: IR/MCP generation + testing (3-4h)
- Day 5: maxmin.gms validation + documentation (2-3h)

**Total:** 10-14 hours baseline, 16-20 hours with slippage

### Dependencies

**Before starting:**
- Sprint 11 Prep Task 2 complete (this document)
- Decision: GO vs DEFER
- Sprint 11 capacity reconfirmed

**Blocks:**
- Aggressive simplification (if conflicts in semantic analyzer)
- CI guardrails (if breaking test coverage)

**Blocked by this:**
- None (independent feature)

### Risk Assessment

**Likelihood of slippage:** 40% (HIGH)

**Slippage scenarios:**
1. Grammar conflicts with existing rules (3-5h debugging)
2. Transformer edge cases (2-3h debugging)
3. Subset expansion bugs (2-4h debugging)
4. Performance issues with large subsets (1-2h optimization)

**Total slippage:** +6-14 hours -> 16-28 hours total

### Rollback Plan

**If blocked during Sprint 11:**
1. Create feature branch `feature/nested-subset-indexing-partial`
2. Commit completed phases (grammar, AST)
3. Document blocker in KNOWN_UNKNOWNS.md
4. Defer remaining work to Sprint 12
5. Do NOT merge partial implementation to main

---

## Sprint 12 Alternative (RECOMMENDED)

### Why Sprint 12 is Better

**1. Capacity Alignment**
- Sprint 12 can dedicate 23-34h to complete ALL maxmin.gms features
- No capacity conflict with high-priority features
- Full implementation vs partial implementation

**2. Complete Feature Set**
- Implement nested/subset indexing (10-14h)
- Implement aggregation operators (8-12h)
- Implement multi-model blocks (3-5h)
- Implement loop tuples (2-3h)
- **Result:** maxmin.gms 18% -> 100% (vs 18% -> 56% for Sprint 11)

**3. Lower Risk**
- More time for testing and validation
- Can address slippage without sprint failure
- Holistic approach to maxmin.gms (fewer integration issues)

**4. Better ROI**
- Sprint 11: 10-14h for 38% improvement (still 44% blocked)
- Sprint 12: 23-34h for 82% improvement (fully unblocked)
- Sprint 12 has 2.4x better efficiency

### Sprint 12 Plan

**Phase 1: Nested/Subset Indexing (10-14h)**
- Use this implementation plan

**Phase 2: Aggregation Operators (8-12h)**
- sum(), sqrt(), sqr() support
- Grammar, AST, semantic, IR changes
- Test with maxmin.gms lines 51-54

**Phase 3: Multi-Model Blocks (3-5h)**
- Model statement parsing
- Model solve statements
- Multiple objectives

**Phase 4: Loop Tuples (2-3h)**
- Loop statement with tuple iteration
- Dynamic set assignments

**Phase 5: Integration Testing (2-4h)**
- Complete maxmin.gms end-to-end test
- Validation against GAMSLib expected output

**Total:** 23-34 hours (fits Sprint 12 capacity)

---

## Conclusion

This implementation plan provides a detailed roadmap for adding GAMS nested/subset indexing support to nlp2mcp. The feature is well-scoped with clear phases, testing strategies, and risk mitigations.

**FINAL RECOMMENDATION: DEFER to Sprint 12**

**Rationale:**
1. Sprint 11 capacity conflict (22-28h committed vs 20-30h capacity)
2. High slippage risk (40% probability of 16-20h total)
3. Partial benefit (only 38% improvement, still 44% blocked)
4. Better alternative: Sprint 12 complete implementation (82% improvement)

**Next Steps:**
1. Review and approve this implementation plan
2. Make final GO/NO-GO decision based on Sprint 11 priorities
3. If DEFER: Document decision in PREP_PLAN.md
4. If GO: Create feature branch and begin Phase 1

---

## Appendix A: GAMS Subset Semantics Reference

### Subset Declaration
```gams
Set n / p1*p13 /;
Set low(n,n) 'lower triangle';  // 2D subset of n x n
```

### Subset Assignment
```gams
Alias (n, nn);
low(n,nn) = ord(n) > ord(nn);  // Static condition using ord()
```

**Static conditions:** Evaluable at compile time (ord(), card())
**Dynamic conditions:** Require runtime evaluation (variable references)

### Subset Usage in Equations

**Explicit indices:**
```gams
Equation defdist(low(n,nn));
defdist(low(n,nn)).. dist(n,nn) =e= sqrt(...);
```
- Subset name: `low`
- Indices: `n`, `nn`
- Generates equations only for members of `low`

**Shorthand notation:**
```gams
Equation mindist1(low);
mindist1(low).. mindist =l= dist(low);
```
- Subset name: `low`
- Indices: inferred from subset dimensionality (2D -> `low(n,nn)`)
- Equivalent to `mindist1(low(n,nn))..`

### Subset Member Calculation

For `n = {p1, p2, p3}` and `low(n,nn) = ord(n) > ord(nn)`:
```
ord(p1) = 1, ord(p2) = 2, ord(p3) = 3

low members:
  (p2,p1): ord(p2) > ord(p1) -> 2 > 1 -> TRUE
  (p3,p1): ord(p3) > ord(p1) -> 3 > 1 -> TRUE
  (p3,p2): ord(p3) > ord(p2) -> 3 > 2 -> TRUE

Total: 3 members
```

For `n = {p1*p13}` (13 elements):
```
low members = (13 * 12) / 2 = 78 pairs
(p2,p1), (p3,p1), (p3,p2), ..., (p13,p12)
```

---

## Appendix B: Grammar Evolution

### Current Grammar (Sprint 10)
```lark
equation_def: ID "(" id_list ")" ".." equation_body
            | ID ".." equation_body

id_list: ID ("," ID)*
```

### Proposed Grammar (Sprint 11)
```lark
equation_def: ID "(" domain_list ")" ".." equation_body
            | ID ".." equation_body

domain_list: domain_element ("," domain_element)*

domain_element: simple_domain | subset_domain

simple_domain: ID

subset_domain: ID "(" id_list ")"

id_list: ID ("," ID)*
```

**Changes:**
- Replace `id_list` with `domain_list` in `equation_def`
- Add `domain_element` base rule
- Add `simple_domain` wrapper for backward compatibility
- Add `subset_domain` for nested subset syntax

**Backward compatibility:** All existing equations parse identically
- `supply(i)` -> `domain_list: [simple_domain('i')]`
- `cost(i,j)` -> `domain_list: [simple_domain('i'), simple_domain('j')]`

---

## Appendix C: Example Transformations

### Example 1: Simple Domain (Unchanged)
```gams
Equation supply(i);
supply(i).. sum(j, x(i,j)) =l= capacity(i);
```

**AST:**
```python
EquationDef(
    name='supply',
    domain=[SimpleDomain(identifier='i')],
    body=EquationBody(...)
)
```

**Instances:** One per member of set `i`

### Example 2: Subset Domain (New)
```gams
Set n / p1*p3 /;
Set low(n,n);
low(n,nn) = ord(n) > ord(nn);

Equation defdist(low(n,nn));
defdist(low(n,nn)).. dist(n,nn) =e= 1;
```

**AST:**
```python
EquationDef(
    name='defdist',
    domain=[SubsetDomain(subset_name='low', indices=['n', 'nn'])],
    body=EquationBody(...)
)
```

**Instances:**
```python
[
    EquationInstance(equation_name='defdist', index_map={'n':'p2','nn':'p1'}, ...),
    EquationInstance(equation_name='defdist', index_map={'n':'p3','nn':'p1'}, ...),
    EquationInstance(equation_name='defdist', index_map={'n':'p3','nn':'p2'}, ...)
]
```

**IR:**
```python
[
    IREquation(name='defdist[p2,p1]', body=..., type='eq'),
    IREquation(name='defdist[p3,p1]', body=..., type='eq'),
    IREquation(name='defdist[p3,p2]', body=..., type='eq')
]
```

### Example 3: Mixed Domains (New)
```gams
Equation foo(i, low(n,nn), k);
foo(i, low(n,nn), k).. x(i,n,nn,k) =e= 1;
```

**AST:**
```python
EquationDef(
    name='foo',
    domain=[
        SimpleDomain(identifier='i'),
        SubsetDomain(subset_name='low', indices=['n', 'nn']),
        SimpleDomain(identifier='k')
    ],
    body=EquationBody(...)
)
```

**Instances:** Cartesian product of:
- Set `i` members
- Subset `low` members
- Set `k` members

**Example:** If `i={i1,i2}`, `low={(p2,p1),(p3,p1)}`, `k={k1}`:
```python
[
    EquationInstance(..., index_map={'i':'i1','n':'p2','nn':'p1','k':'k1'}),
    EquationInstance(..., index_map={'i':'i1','n':'p3','nn':'p1','k':'k1'}),
    EquationInstance(..., index_map={'i':'i2','n':'p2','nn':'p1','k':'k1'}),
    EquationInstance(..., index_map={'i':'i2','n':'p3','nn':'p1','k':'k1'})
]
```

Total: 2 * 2 * 1 = 4 instances

---

## Appendix D: Risk Register

| Risk | Probability | Impact | Mitigation | Residual Risk |
|------|-------------|--------|------------|---------------|
| Grammar conflicts with existing rules | 30% | HIGH | Use explicit subset_domain rule, extensive testing | MEDIUM |
| Transformer edge cases | 40% | MEDIUM | Comprehensive unit tests, clear tree structure | LOW |
| Subset expansion performance | 20% | MEDIUM | Eager evaluation acceptable for Sprint 11, add benchmarks | LOW |
| Breaking existing equation parsing | 15% | HIGH | Backward-compatible AST changes, regression tests | LOW |
| Subset condition evaluation complexity | 50% | HIGH | Implement only ord() for Sprint 11, document limitations | MEDIUM |
| Index binding conflicts | 25% | MEDIUM | Explicit index_map structure, validation | LOW |
| Slippage beyond Sprint 11 capacity | 40% | HIGH | DEFER to Sprint 12 (recommended) | LOW (if deferred) |

**Overall Risk Assessment:** HIGH (9/10) for Sprint 11 implementation

**Risk Reduction:** DEFER to Sprint 12 reduces overall risk to MEDIUM (5/10)

---

## Document Control

**Version:** 1.0
**Date:** 2025-11-25
**Author:** Claude (nlp2mcp Sprint 11 Prep Task 2)
**Status:** DRAFT - Awaiting approval
**Next Review:** After GO/NO-GO decision

**Change History:**
- 2025-11-25: Initial version (comprehensive implementation plan)
