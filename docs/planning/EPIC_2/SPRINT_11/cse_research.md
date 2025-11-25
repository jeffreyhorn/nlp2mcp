# Common Subexpression Elimination (CSE) Research

**Date:** 2025-11-25  
**Sprint:** Sprint 11 (Weeks 11-12)  
**Purpose:** Research CSE algorithms, cost models, and integration design for aggressive simplification

---

## Executive Summary

**Research Objective:** Determine the optimal CSE approach for nlp2mcp's aggressive simplification mode, including algorithm selection, cost model design, and scope decision for Sprint 11.

**Key Findings:**
1. **Algorithm:** Hash-based tree traversal (SymPy approach) is most suitable for expression DAGs
2. **Cost Model:** Weighted threshold combining reuse count and operation cost (≥2 for expensive ops, ≥3 for cheap ops)
3. **Threshold:** Variable by operation type to balance benefits vs. overhead
4. **Integration:** CSE as Step 8 (final pass) in transformation pipeline, opt-in via `--cse` flag
5. **Scope Decision:** **Implement basic CSE (T5.1 only) in Sprint 11** - expensive function CSE only, defer nested/complex patterns to Sprint 12

**Estimated Effort:**
- **Sprint 11 Basic CSE (T5.1):** 1.5h algorithm + 0.5h cost model + 0.5h integration + 1h code gen + 1h testing + 0.5h docs = **5 hours total**
- **Sprint 12 Extended CSE (T5.2-T5.4):** 4-5 hours (if needed)

**Recommendation:** Implement T5.1 (Expensive Function CSE) in Sprint 11 as MEDIUM priority transformation. This provides high-value optimization (eliminating redundant exp, log, sin, cos calls) with minimal complexity and risk.

---

## Table of Contents

1. [Background and Motivation](#background-and-motivation)
2. [CSE Algorithm Survey](#cse-algorithm-survey)
3. [Cost Model Research](#cost-model-research)
4. [Integration Design](#integration-design)
5. [Scope Decision](#scope-decision)
6. [Implementation Plan](#implementation-plan)
7. [Risk Assessment](#risk-assessment)
8. [References](#references)

---

## Background and Motivation

### What is CSE?

Common Subexpression Elimination (CSE) is a compiler optimization technique that identifies repeated subexpressions in code and replaces them with temporary variables holding the computed value. This eliminates redundant computations at the cost of introducing additional variables.

**Classic Example:**
```
Before:
  y = a*b + c*d
  z = a*b - c*d

After CSE:
  t1 = a*b
  t2 = c*d
  y = t1 + t2
  z = t1 - t2
```

**Benefits:**
- Reduces FLOPs (floating-point operations), especially for expensive functions
- Can improve runtime performance when subexpression is costly
- Simplifies expressions by factoring out common structure

**Costs:**
- Increases variable count (introduces temporaries)
- Adds code generation complexity (need to emit variable definitions)
- May increase register pressure in generated code
- Only beneficial if overhead < savings

### Why CSE for nlp2mcp?

Automatic differentiation generates expressions with significant redundancy:
- Chain rule creates repeated subexpressions (e.g., `exp(x)` appears in multiple derivative terms)
- Expensive function calls (exp, log, trig) dominate runtime
- Derivatives often share common structure

**Example from AD:**
```python
# Original: f = exp(x) * sin(y)
# Derivative wrt x: df/dx = exp(x) * sin(y)
# Derivative wrt y: df/dy = exp(x) * cos(y)

# Without CSE:
df_dx = exp(x) * sin(y)  # exp(x) computed again
df_dy = exp(x) * cos(y)  # exp(x) computed again

# With CSE:
t1 = exp(x)
df_dx = t1 * sin(y)
df_dy = t1 * cos(y)
```

### CSE in PROJECT_PLAN.md

CSE is listed as **Step 8 (optional)** in the transformation pipeline:
- Position: Final pass after all algebraic simplifications
- Mode: Opt-in via `--cse` flag (not automatic)
- Rationale: "Trade-off: Increases variable count; only beneficial if subexpression reused ≥2 times"

**Design Questions:**
1. When is CSE profitable vs. wasteful?
2. Should threshold vary by operation cost?
3. How to integrate with GAMS code generation?
4. Should CSE be opt-in or default in aggressive mode?

---

## CSE Algorithm Survey

### 1. Compiler Approaches (LLVM, GCC)

**LLVM CSE Pass:**
- Uses **value numbering** for global CSE
- **GVN-PRE** (Global Value Numbering with Partial Redundancy Elimination)
- Works on SSA (Static Single Assignment) form
- Eliminates both full and partial redundancies
- **Complexity:** O(n²) worst case, typically O(n log n)

**Key Insight:** Compilers use sophisticated analysis (dominance frontiers, SSA) but target imperative code with control flow. Our expressions are pure DAGs (directed acyclic graphs) - simpler problem!

**GCC CSE Pass:**
- Local CSE within basic blocks: O(n) within block
- Global CSE across entire function: O(n²) with optimization
- Store motion pass to move computations out of loops
- Load elimination after stores

**Key Insight:** GCC separates local (fast, within block) and global (slower, cross-block) CSE. We only need "local" CSE since expressions are single DAGs without control flow.

### 2. Symbolic Math Approaches (SymPy)

**SymPy `cse()` Function:**
- **Algorithm:** Hash-based tree traversal with frequency counting
- **Threshold:** Simple ≥2 reuse count (no cost model)
- **Canonicalization:** Optional ordering for commutativity detection
- **Temp variables:** Generated via `numbered_symbols()` → `x0, x1, x2, ...`

**Implementation Details (from sympy/simplify/cse_main.py):**

```python
def tree_cse(exprs, symbols):
    """Perform raw CSE on expression trees."""
    seen_subexp = set()
    to_eliminate = set()
    
    # Traverse expressions, collect repeated subexpressions
    for expr in exprs:
        for node in preorder_traversal(expr):
            if node in seen_subexp:
                to_eliminate.add(node)  # Appears ≥2 times
            else:
                seen_subexp.add(node)
    
    # Generate replacements
    replacements = []
    for subexp in to_eliminate:
        sym = next(symbols)
        replacements.append((sym, subexp))
    
    return replacements, substitute(exprs, replacements)
```

**Key Features:**
- Detects atoms/symbols and excludes them (no CSE for single variables)
- Handles matrix expressions specially (preserves dimensionality)
- `opt_cse()` post-optimization: collapses single-arg Mul/Add
- `match_common_args()`: finds common arguments in function calls

**Key Insight:** Simple frequency-based detection (≥2 threshold) works well for symbolic math. Cost model not needed in pure symbolic context since evaluation cost unknown.

### 3. Automatic Differentiation Tools

**Research Finding:** AD tools often integrate CSE for efficiency.

**From literature (ar5iv.labs.arxiv.org/html/1904.02990):**
> "When common subexpressions are allowed in symbolic differentiation, then reverse mode automatic differentiation and symbolic differentiation compute the same result. Common subexpressions are computed in the same way as in reverse mode automatic differentiation."

**Key Insights:**
- Reverse-mode AD naturally creates DAGs with shared subexpressions
- Tape minimization in reverse mode balances storage vs. recomputation
- CSE reduces tape size and FLOPs
- Good AD libraries use structure between primal and derivative for better CSE/SIMD

**Haskell `dvda` Package:**
- Explicit CSE using hashing on computational graphs (FunGraphs)
- Converts expression trees to DAGs before differentiation
- Eliminates redundancy in both forward and reverse passes

**Key Insight:** CSE is most effective when applied to the full computational graph (primal + derivatives together), not just individual expressions.

### 4. Algorithm Comparison

| Approach | Complexity | Strengths | Weaknesses | Suitability for nlp2mcp |
|----------|-----------|-----------|------------|------------------------|
| LLVM GVN-PRE | O(n²) worst, O(n log n) typical | Handles control flow, partial redundancy | Overkill for DAGs, requires SSA | LOW - too complex |
| GCC Local CSE | O(n) | Fast, simple | Only within basic blocks | MEDIUM - concept applicable |
| SymPy Hash-based | O(n) avg, O(n²) worst | Simple, works on expression trees | No cost model, canonicalization optional | **HIGH - best fit** |
| Explicit DAG (dvda) | O(n) | Most efficient representation | Requires full DAG construction | MEDIUM - may need for Sprint 12+ |

**Recommendation:** Use **SymPy-style hash-based traversal** with frequency counting as baseline algorithm. Add cost model on top of frequency detection.

---

## Cost Model Research

### 1. Operation Cost Analysis

**Relative Costs (from research):**

| Operation | Typical CPU Cycles | Relative Cost | Cost Weight |
|-----------|-------------------|---------------|-------------|
| Const/VarRef | 1-2 | 1× (baseline) | 1 |
| Add/Sub | 2-4 | 1× | 1 |
| Mul | 3-5 | 2× | 2 |
| Div | 10-20 | 3-5× | 3 |
| Power (x^n) | 15-30 | 5-10× | 3 |
| sin/cos/tan | 100-200 | 50-100× | 4 |
| exp/log | 100-200 | 50-100× | 5 |
| sqrt | 20-40 | 10-20× | 3 |

**Key Finding (from scicomp.stackexchange.com):**
> "Transcendental functions like exp, sin, tan are defined by infinite power series, which takes effort to evaluate. A sin() function takes approximately 200 cycles on typical CPUs, compared to just a few cycles for basic arithmetic operations."

**Optimization Evidence (OpTuner paper):**
> "OpTuner provides implementations of sin, cos, tan, exp, and log ranging in accuracy across 15 different orders of magnitude with speeds varying by a factor of 58×, achieving speedups of 107% while maintaining high accuracy."

**Implication:** Eliminating a single redundant `exp(x)` call saves ~200 cycles, while eliminating redundant `x*y` saves ~3 cycles. **Cost-aware CSE is essential.**

### 2. Temporary Variable Overhead

**Costs of Introducing Temporaries:**
1. **Memory:** One additional variable per CSE (negligible for <100 temps)
2. **Code Generation:** Need to emit temporary definitions before use
3. **Cognitive:** More variables make generated code harder to read
4. **Register Pressure:** May force spills in generated code (GAMS handles this)

**Overhead Estimate:**
- **Per temporary:** ~1 operation equivalent (assignment cost)
- **Code gen complexity:** O(k) where k = number of temporaries
- **Readability:** Subjective, but generally acceptable for <20 temps

**Threshold Implication:**
- For expensive ops (cost=5): 2 reuses justify 1 temp → `5*2 - 5 - 1 = 4 > 0` ✓
- For cheap ops (cost=1): 3 reuses needed → `1*3 - 1 - 1 = 1 > 0` ✓
- For medium ops (cost=2): 2 reuses → `2*2 - 2 - 1 = 1 > 0` ✓ (marginal)

### 3. Cost Model Formula

**Proposed Cost-Benefit Model:**

```
CSE is beneficial if:
  cost_savings > overhead

Where:
  cost_savings = operation_cost × reuse_count
  overhead = operation_cost + 1  (compute once + assignment)

Simplified:
  operation_cost × reuse_count > operation_cost + 1
  operation_cost × (reuse_count - 1) > 1
  reuse_count > 1 + 1/operation_cost
```

**Threshold by Operation Cost:**

| Operation Cost | Minimum Reuse Count | Rationale |
|----------------|---------------------|-----------|
| 5 (exp, log) | ≥2 | `5*(2-1) = 5 > 1` ✓ High value |
| 4 (trig) | ≥2 | `4*(2-1) = 4 > 1` ✓ High value |
| 3 (power, div, sqrt) | ≥2 | `3*(2-1) = 3 > 1` ✓ Moderate value |
| 2 (mul) | ≥3 | `2*(3-1) = 4 > 1` ✓ Marginal |
| 1 (add, sub) | ≥3 | `1*(3-1) = 2 > 1` ✓ Low value |

**Recommendation:** Use **cost-weighted threshold**:
- **Expensive ops (cost ≥3):** Apply CSE if reuse_count ≥ 2
- **Cheap ops (cost ≤2):** Apply CSE if reuse_count ≥ 3

### 4. Comparison with SymPy

**SymPy Approach:** Fixed ≥2 threshold for all operations

**Pros:**
- Simple, easy to understand
- Conservative (avoids over-aggressive CSE)
- Works well in symbolic math (no runtime cost)

**Cons:**
- Misses optimization: doesn't CSE `x+y` appearing 2 times (low value)
- Over-optimizes: CSEs `x+y` appearing 3 times (marginal benefit)

**Our Improvement:** Cost-aware threshold balances value vs. overhead better for code generation context.

---

## Integration Design

### 1. Position in Transformation Pipeline

**Pipeline Order (from PROJECT_PLAN.md):**
1. Basic simplification
2. Like-term combination
3. Associativity for constants
4. Fraction combining
5. Distribution/Factoring
6. Division simplification
7. Multi-term factoring
8. **CSE** ← Final pass

**Rationale for Position 8:**
- CSE operates on fully simplified expression (no redundant work)
- Algebraic simplifications may eliminate some common subexpressions (via factoring)
- CSE detects remaining structural redundancy that factoring missed
- Temp variables generated have simplified RHS (easier to read)

**Alternative Considered:** CSE before factoring
- **Problem:** Factoring may eliminate CSE opportunities
- **Example:** `x*y + x*z` → factor to `x*(y+z)` (better than CSE)
- **Conclusion:** CSE last is optimal

### 2. Algorithm Implementation

**Step 1: Subexpression Collection**

```python
def collect_subexpressions(expr: Expr) -> dict[Expr, int]:
    """Traverse expression tree, count subexpression occurrences."""
    counts: dict[Expr, int] = {}
    
    def traverse(node: Expr):
        # Skip atoms (constants, variables, parameters)
        if isinstance(node, (Const, VarRef, ParamRef)):
            return
        
        # Count this subexpression
        counts[node] = counts.get(node, 0) + 1
        
        # Recurse on children
        match node:
            case Unary(_, child):
                traverse(child)
            case Binary(_, left, right):
                traverse(left)
                traverse(right)
            case FunctionCall(_, args):
                for arg in args:
                    traverse(arg)
    
    traverse(expr)
    return counts
```

**Step 2: Cost Model Application**

```python
def operation_cost(expr: Expr) -> int:
    """Assign cost weight to expression."""
    match expr:
        case Const(_) | VarRef(_, _) | ParamRef(_, _):
            return 1
        case Binary(op, _, _) if op in ("+", "-"):
            return 1
        case Binary(op, _, _) if op == "*":
            return 2
        case Binary(op, _, _) if op in ("/", "^"):
            return 3
        case FunctionCall(name, _) if name in ("sin", "cos", "tan"):
            return 4
        case FunctionCall(name, _) if name in ("exp", "log", "sqrt"):
            return 5
        case _:
            return 2  # Default for unknown operations

def should_eliminate(expr: Expr, reuse_count: int) -> bool:
    """Determine if CSE is beneficial for this subexpression."""
    cost = operation_cost(expr)
    
    # Threshold: cost-weighted
    if cost >= 3:
        return reuse_count >= 2  # Expensive ops: ≥2 reuses
    else:
        return reuse_count >= 3  # Cheap ops: ≥3 reuses
```

**Step 3: Temporary Variable Generation**

```python
def generate_cse_temporaries(expr: Expr) -> tuple[list[tuple[str, Expr]], Expr]:
    """Apply CSE, return (temporaries, simplified_expr)."""
    
    # Collect subexpressions
    counts = collect_subexpressions(expr)
    
    # Filter to eliminate candidates
    to_eliminate = [
        (subexp, count) 
        for subexp, count in counts.items()
        if should_eliminate(subexp, count)
    ]
    
    # Sort by cost descending (eliminate expensive ops first)
    to_eliminate.sort(key=lambda x: operation_cost(x[0]), reverse=True)
    
    # Generate temporaries
    temporaries = []
    replacements = {}
    temp_counter = 0
    
    for subexp, count in to_eliminate:
        temp_name = f"cse_tmp_{temp_counter}"
        temp_counter += 1
        temporaries.append((temp_name, subexp))
        replacements[subexp] = VarRef(temp_name, temp_name)
    
    # Substitute in original expression
    simplified = substitute(expr, replacements)
    
    return temporaries, simplified
```

**Step 4: Integration with simplify_aggressive()**

```python
def simplify_aggressive(expr: Expr, 
                        enable_cse: bool = False,
                        ...) -> Expr:
    """8-step pipeline with optional CSE."""
    
    current = expr
    
    # Steps 1-7: Algebraic simplifications
    current = simplify(current)  # Step 1
    current = simplify_advanced(current)  # Step 2
    current = simplify_nested(current)  # Step 3
    current = simplify_fractions(current)  # Step 4
    current = simplify_factoring(current)  # Step 5
    current = simplify_division(current)  # Step 6
    current = simplify_multi_term_factoring(current)  # Step 7
    
    # Step 8: CSE (optional)
    if enable_cse:
        temporaries, current = generate_cse_temporaries(current)
        # Store temporaries in metadata for code generation
        current.cse_temporaries = temporaries
    
    return current
```

### 3. GAMS Code Generation Integration

**Challenge:** GAMS requires variable declarations before use.

**Solution:** Emit temporaries as intermediate variables in generated code.

**Example Output:**

```gams
* Original expression with CSE
Equations
  grad_f_eq;

Variables
  grad_f;

* CSE temporary variables
Scalar
  cse_tmp_0
  cse_tmp_1;

* Assign temporaries
cse_tmp_0 = exp(x);
cse_tmp_1 = sin(y);

* Use temporaries in equation
grad_f_eq.. grad_f =E= cse_tmp_0 * cse_tmp_1 + cse_tmp_0 * cos(y);
```

**Implementation Strategy:**
1. During `simplify_aggressive()`, store CSE temporaries in expression metadata
2. During code generation, check for `cse_temporaries` attribute
3. If present, emit `Scalar` declarations for temporaries
4. Emit temporary assignments before equation definitions
5. Use temporary names in equation RHS

**Code Generation Pseudocode:**

```python
def generate_gams_equation(equation_name: str, expr: Expr) -> str:
    """Generate GAMS equation with CSE temporaries."""
    
    lines = []
    
    # Emit temporary declarations if present
    if hasattr(expr, 'cse_temporaries') and expr.cse_temporaries:
        lines.append("* CSE temporary variables")
        lines.append("Scalar")
        for temp_name, _ in expr.cse_temporaries:
            lines.append(f"  {temp_name}")
        lines.append(";")
        lines.append("")
        
        # Emit temporary assignments
        for temp_name, temp_expr in expr.cse_temporaries:
            temp_rhs = expr_to_gams(temp_expr)
            lines.append(f"{temp_name} = {temp_rhs};")
        lines.append("")
    
    # Emit equation
    equation_rhs = expr_to_gams(expr)
    lines.append(f"{equation_name}.. result =E= {equation_rhs};")
    
    return "\n".join(lines)
```

### 4. Flag Design

**Proposed Flags:**

1. **`--cse`** (boolean): Enable CSE in aggressive mode
   - Default: `False` (opt-in)
   - When enabled: Apply CSE as Step 8 in pipeline

2. **`--cse-threshold=N`** (integer): Override reuse threshold
   - Default: Cost-weighted (2 for expensive, 3 for cheap)
   - Range: 2-10 (lower = more aggressive, higher = more conservative)
   - Example: `--cse-threshold=2` forces ≥2 threshold for all ops

3. **`--cse-min-cost=N`** (integer): Only CSE ops with cost ≥ N
   - Default: 3 (expensive ops only: exp, log, trig, power, div)
   - Range: 1-5
   - Example: `--cse-min-cost=4` only CSEs exp/log/trig

**Usage Examples:**

```bash
# Enable basic CSE (expensive ops only, ≥2 reuses)
nlp2mcp model.nl --simplification aggressive --cse

# Aggressive CSE (all ops, ≥2 reuses)
nlp2mcp model.nl --simplification aggressive --cse --cse-min-cost=1 --cse-threshold=2

# Conservative CSE (expensive ops only, ≥3 reuses)
nlp2mcp model.nl --simplification aggressive --cse --cse-threshold=3
```

**Rationale for Opt-In Default:**
- CSE changes code structure (introduces temporaries)
- May not be beneficial for all models
- Users may prefer algebraic-only simplification
- Conservative default reduces surprise

---

## Scope Decision

### Decision Framework

**Factors Considered:**
1. **Value:** How much improvement does CSE provide?
2. **Complexity:** How hard is it to implement?
3. **Risk:** What can go wrong?
4. **Time:** How long will it take?
5. **Dependencies:** What else needs to be done first?

### Analysis

**1. Value Assessment**

**High-Value Scenarios:**
- Models with expensive functions (exp, log, trig) in derivatives
- Derivatives with repeated structure (chain rule patterns)
- Large models where 5-10% FLOP reduction matters

**Low-Value Scenarios:**
- Simple polynomial models (no expensive functions)
- Models where factoring already eliminates most redundancy
- Small models where temporary overhead dominates

**Estimated Impact:**
- **Best case:** 20-30% FLOP reduction for models heavy in exp/log/trig
- **Typical case:** 5-10% FLOP reduction across diverse models
- **Worst case:** 0% (no repeated expensive ops) or negative (overhead > savings)

**Conclusion:** **Medium-High value** for typical AD-generated derivatives.

**2. Complexity Assessment**

**T5.1 (Expensive Function CSE) Complexity:**
- Algorithm: Simple (hash-based traversal + filtering)
- Cost model: Straightforward (predefined weights)
- Integration: Moderate (code gen changes needed)
- Testing: Standard (FD validation, benchmarks)

**Estimated LOC:**
- Core algorithm: ~100 lines
- Cost model: ~50 lines
- Integration: ~80 lines (code gen updates)
- Tests: ~150 lines
- **Total:** ~380 lines

**T5.2-T5.4 (Advanced CSE) Complexity:**
- Nested CSE: Requires recursive CSE application (complex)
- Canonicalization: Requires expression ordering (complex)
- Integration with factoring: Requires conflict resolution (tricky)

**Conclusion:** **Low complexity** for T5.1, **High complexity** for T5.2-T5.4.

**3. Risk Assessment**

**Risks:**
1. **Correctness:** CSE must preserve mathematical equivalence
   - **Mitigation:** FD validation on all transformations
   - **Risk level:** LOW (CSE is well-understood)

2. **Code Generation:** Temporaries may break GAMS syntax
   - **Mitigation:** Careful code gen testing, GAMS validation
   - **Risk level:** MEDIUM (new code path)

3. **Performance Regression:** CSE overhead may exceed savings
   - **Mitigation:** Cost model, conservative thresholds, opt-in flag
   - **Risk level:** LOW (opt-in means no impact if disabled)

4. **Interaction with Factoring:** CSE may conflict with factoring
   - **Mitigation:** CSE last in pipeline (after factoring)
   - **Risk level:** LOW (pipeline ordering prevents conflict)

**Conclusion:** **Low-Medium risk** overall, manageable with testing.

**4. Time Estimate**

**T5.1 Implementation:**
- Core algorithm: 1.5 hours
- Cost model: 0.5 hours
- Integration with pipeline: 0.5 hours
- Code generation updates: 1 hour
- Tests: 1 hour
- Documentation: 0.5 hours
- **Total:** **5 hours**

**T5.2-T5.4 Implementation:**
- Nested CSE: 2 hours
- Canonicalization: 2 hours
- Integration/testing: 2 hours
- **Total:** **6 hours**

**Sprint 11 Budget:**
- Baseline transformations (T1.1-T4.2): 12.5 hours
- Extended transformations (T1.3, T3.2, T4.1, T5.1): 5.5 hours
- **Total with T5.1:** 18 hours
- **Available time:** ~20-22 hours

**Conclusion:** **T5.1 fits in Sprint 11 extended scope.** T5.2-T5.4 would exceed budget.

**5. Dependency Analysis**

**T5.1 Dependencies:**
- ✅ Expression AST structure (exists)
- ✅ Simplification pipeline (Task 3 complete)
- ✅ Code generation framework (exists)
- ✅ FD validation framework (exists)

**Blockers:** None.

### Scope Decision

**DECISION: Implement T5.1 (Expensive Function CSE) in Sprint 11 as MEDIUM priority.**

**Rationale:**
1. **Value:** Medium-high impact for typical models (5-10% FLOP reduction)
2. **Complexity:** Low (simple algorithm, ~5 hours effort)
3. **Risk:** Low-medium (well-understood, opt-in mitigates risk)
4. **Time:** Fits in extended Sprint 11 scope (18h total with MEDIUM priority)
5. **Dependencies:** All satisfied

**Defer to Sprint 12:**
- T5.2 (Nested Expression CSE)
- T5.3 (Multiplicative Subexpression CSE)
- T5.4 (CSE with Aliasing)

**Rationale for Deferral:**
- Lower marginal value (factoring handles most cases)
- Higher complexity (canonicalization, nested detection)
- Sprint 11 focus on high-value, low-risk transformations

---

## Implementation Plan

### Sprint 11: T5.1 (Expensive Function CSE)

**Phase 1: Core Algorithm (1.5 hours)**

Implement subexpression collection and filtering:
- `collect_subexpressions(expr)` → frequency map
- `operation_cost(expr)` → cost weight
- `should_eliminate(expr, count)` → threshold check
- Filter to expensive ops only (cost ≥ 3)

**Phase 2: CSE Application (1 hour)**

Implement temporary generation and substitution:
- `generate_cse_temporaries(expr)` → (temporaries, simplified_expr)
- Sort by cost descending (prioritize expensive ops)
- Generate unique temporary names (`cse_tmp_0`, `cse_tmp_1`, ...)
- Substitute in expression tree

**Phase 3: Pipeline Integration (0.5 hours)**

Add CSE as Step 8:
- Add `enable_cse` parameter to `simplify_aggressive()`
- Apply CSE after Step 7 (multi-term factoring)
- Store temporaries in expression metadata

**Phase 4: Code Generation (1 hour)**

Update GAMS code generator:
- Detect `cse_temporaries` attribute on expressions
- Emit `Scalar` declarations for temporaries
- Emit temporary assignments before equations
- Use temporary variable names in equation RHS

**Phase 5: Testing and Validation (1 hour)**

- Unit tests for CSE algorithm
- FD validation tests
- Benchmark tests (measure FLOP reduction)
- Code generation tests (GAMS syntax validation)

**Phase 6: Documentation (0.5 hours)**

- Update architecture document with CSE details
- Document `--cse`, `--cse-threshold`, `--cse-min-cost` flags
- Add usage examples

**Total: 5 hours**

### Sprint 12: T5.2-T5.4 (Advanced CSE) - Optional

**If Sprint 11 benchmarks show high value:**
- Implement nested CSE (T5.2): 2 hours
- Implement canonicalization for aliasing (T5.4): 2 hours
- Decide on multiplicative CSE (T5.3): 1 hour (likely skip, factoring handles)
- Testing and integration: 1 hour
- **Total:** 6 hours

**Trigger for Sprint 12 work:**
- Benchmark models show ≥15% FLOP reduction with T5.1
- User feedback requests more aggressive CSE
- Profiling shows remaining redundancy in expensive operations

---

## Risk Assessment

### Risk 1: CSE Overhead Exceeds Savings

**Probability:** Low (10%)  
**Impact:** Medium (degraded performance)

**Scenario:** Models with few expensive ops benefit little from CSE, but pay temporary overhead.

**Mitigation:**
- Opt-in via `--cse` flag (default disabled)
- Cost model ensures savings > overhead
- Conservative thresholds (≥2 for expensive, ≥3 for cheap)
- Benchmark testing before release

### Risk 2: Code Generation Bugs

**Probability:** Medium (30%)  
**Impact:** High (invalid GAMS code)

**Scenario:** Temporary variable emission breaks GAMS syntax or semantics.

**Mitigation:**
- Extensive code generation tests
- GAMS compiler validation
- Start with simple test cases, gradually increase complexity
- Manual review of generated code

### Risk 3: Interaction with Factoring

**Probability:** Low (15%)  
**Impact:** Medium (suboptimal simplification)

**Scenario:** CSE prevents later factoring opportunities or vice versa.

**Mitigation:**
- CSE positioned last in pipeline (after all algebraic simplifications)
- Factoring happens first, eliminating most structural redundancy
- CSE only catches what factoring missed

### Risk 4: Temporary Variable Naming Conflicts

**Probability:** Low (10%)  
**Impact:** Medium (variable shadowing, incorrect code)

**Scenario:** Generated `cse_tmp_N` names conflict with user variables.

**Mitigation:**
- Use unique prefix unlikely to conflict (`cse_tmp_` vs `x` or `var`)
- Check for conflicts with existing variable names
- Allow configurable prefix via `--cse-prefix` flag (future enhancement)

### Risk 5: Over-Aggressive CSE

**Probability:** Low (20%)  
**Impact:** Low (too many temporaries, reduced readability)

**Scenario:** CSE generates 50+ temporaries, making code unreadable.

**Mitigation:**
- Conservative thresholds (≥2 expensive, ≥3 cheap)
- Limit to expensive ops only (cost ≥ 3) by default
- Allow user override via `--cse-min-cost` flag
- Monitor temporary count in benchmarks

---

## References

### Academic Literature

1. **CMU Compiler Design Lecture Notes - Common Subexpression Elimination**  
   https://www.cs.cmu.edu/~rjsimmon/15411-f15/lec/18-commonsub.pdf  
   (Attempted access - PDF format, theory-heavy)

2. **On the Equivalence of Automatic and Symbolic Differentiation**  
   ar5iv.labs.arxiv.org/html/1904.02990  
   Key insight: CSE in symbolic differentiation ≡ reverse-mode AD

### Compiler Implementations

3. **LLVM Analysis and Transform Passes**  
   https://releases.llvm.org/2.6/docs/Passes.html  
   GVN-PRE (Global Value Numbering with Partial Redundancy Elimination)

4. **GCC Optimize Options**  
   https://gcc.gnu.org/onlinedocs/gcc-9.2.0/gcc/Optimize-Options.html  
   `-fgcse`, `-fgcse-lm`, `-fgcse-sm` flags

5. **GeeksforGeeks - Common Subexpression Elimination**  
   https://www.geeksforgeeks.org/common-subexpression-elimination-code-optimization-technique-in-compiler-design/  
   Basic overview and examples

### Symbolic Math Tools

6. **SymPy CSE Implementation**  
   https://github.com/sympy/sympy/blob/master/sympy/simplify/cse_main.py  
   Hash-based tree traversal, ≥2 threshold

7. **Using SymPy's CSE to Generate Code**  
   https://bowfinger.de/blog/2024/03/using-sympys-common-subexpression-elimination-to-generate-code/  
   Practical code generation example

8. **SymPy CSE with lambdify**  
   https://stackoverflow.com/questions/30738840/best-practice-for-using-common-subexpression-elimination-with-lambdify-in-sympy  
   Integration with code generation

### Performance Analysis

9. **Why are log and exp considered expensive computations?**  
   https://scicomp.stackexchange.com/questions/37320  
   ~200 cycles for sin vs. ~3 for multiplication

10. **Computational cost of trig functions**  
    https://stackoverflow.com/questions/3842246  
    100-200 cycles typical for sin/cos/exp/log

11. **Faster Math Functions, Soundly (OpTuner)**  
    https://arxiv.org/pdf/2107.05761  
    Speed-accuracy tradeoffs for transcendental functions

### Automatic Differentiation

12. **Direct Automatic Differentiation of Solvers vs Analytical Adjoints**  
    http://www.stochasticlifestyle.com/direct-automatic-differentiation-of-solvers-vs-analytical-adjoints-which-is-better/  
    CSE in AD context, tape minimization

13. **Haskell dvda Package**  
    https://hackage.haskell.org/package/dvda  
    Explicit CSE on computational graphs

---

## Appendices

### Appendix A: Cost Model Derivation

**Goal:** Determine when CSE is beneficial.

**Variables:**
- `C` = operation cost (1-5)
- `R` = reuse count (≥2)
- `O` = overhead per temporary (≈1)

**Without CSE:**
Total cost = `C × R` (compute expression R times)

**With CSE:**
Total cost = `C + O + (R × 0)` = `C + O` (compute once, assign to temp, reuse temp R times)

**CSE is beneficial when:**
```
C + O < C × R
O < C × R - C
O < C × (R - 1)
1 < C × (R - 1)
R > 1 + 1/C
```

**Thresholds:**
- C=5 (exp/log): R > 1.2 → **R ≥ 2**
- C=4 (trig): R > 1.25 → **R ≥ 2**
- C=3 (pow/div): R > 1.33 → **R ≥ 2**
- C=2 (mul): R > 1.5 → **R ≥ 2** (marginal, use ≥3 for safety)
- C=1 (add/sub): R > 2 → **R ≥ 3**

**Conclusion:** Cost-weighted thresholds are mathematically sound.

### Appendix B: Example Transformation

**Input:**
```python
grad_f = exp(x)*sin(y) + exp(x)*cos(y) + 2*exp(x)*tan(y) + log(z) + log(z)
```

**Step 1: Collect subexpressions**
```
{
  exp(x): 3 occurrences (cost=5),
  sin(y): 1 occurrence,
  cos(y): 1 occurrence,
  tan(y): 1 occurrence,
  log(z): 2 occurrences (cost=5),
}
```

**Step 2: Filter by threshold**
```
exp(x): 3 occurrences, cost=5, 5*(3-1)=10 > 1 ✓ ELIMINATE
log(z): 2 occurrences, cost=5, 5*(2-1)=5 > 1 ✓ ELIMINATE
```

**Step 3: Generate temporaries (sorted by cost descending)**
```
cse_tmp_0 = exp(x)    (cost=5, reuse=3)
cse_tmp_1 = log(z)    (cost=5, reuse=2)
```

**Step 4: Substitute**
```python
grad_f = cse_tmp_0*sin(y) + cse_tmp_0*cos(y) + 2*cse_tmp_0*tan(y) + cse_tmp_1 + cse_tmp_1
```

**Step 5: Further simplification (like-term combination)**
```python
grad_f = cse_tmp_0*sin(y) + cse_tmp_0*cos(y) + 2*cse_tmp_0*tan(y) + 2*cse_tmp_1
```

**GAMS Output:**
```gams
Scalar
  cse_tmp_0
  cse_tmp_1;

cse_tmp_0 = exp(x);
cse_tmp_1 = log(z);

grad_f_eq.. grad_f =E= cse_tmp_0*sin(y) + cse_tmp_0*cos(y) + 2*cse_tmp_0*tan(y) + 2*cse_tmp_1;
```

**Metrics:**
- **Before CSE:** 5 exp calls + 2 log calls = 7 expensive operations
- **After CSE:** 1 exp call + 1 log call = 2 expensive operations
- **Savings:** 5 expensive operations eliminated (71% reduction)

---

**END OF DOCUMENT**
