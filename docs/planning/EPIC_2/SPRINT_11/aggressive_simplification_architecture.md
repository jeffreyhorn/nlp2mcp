# Aggressive Simplification Architecture

**Date:** 2025-11-25  
**Sprint:** Sprint 11 (Weeks 11-12)  
**Status:** Architecture Design (Pre-Implementation)  
**Target:** ≥20% derivative term reduction on ≥50% benchmark models

---

## Executive Summary

This document specifies the architecture for `--simplification aggressive` mode, extending nlp2mcp's existing Basic and Advanced simplification with five new transformation categories: Distribution/Factoring, Fraction Simplification, Nested Operations, Division by Multiplication, and optional Common Subexpression Elimination (CSE).

**Key Design Decisions:**
1. **8-Step Pipeline:** Ordered transformation sequence minimizing interference and maximizing cancellation opportunities
2. **Safety-First Heuristics:** 150% size limit, cancellation detection, rollback on regression
3. **Incremental Extension:** Builds on existing `simplify()` and `simplify_advanced()` infrastructure
4. **Opt-In Validation:** FD checks, PATH alignment, performance budgeting (<10% overhead)
5. **Metrics-Driven:** `--simplification-stats` for transparency and debugging

**Implementation Effort:** 12-15 hours total (2-3h per category, 3-4h pipeline/validation)

---

## Table of Contents

1. [Background and Motivation](#background-and-motivation)
2. [Existing Simplification Architecture](#existing-simplification-architecture)
3. [Aggressive Simplification Design](#aggressive-simplification-design)
4. [Transformation Pipeline](#transformation-pipeline)
5. [Individual Transformation Categories](#individual-transformation-categories)
6. [Heuristics and Safety Mechanisms](#heuristics-and-safety-mechanisms)
7. [Validation Strategy](#validation-strategy)
8. [Metrics and Diagnostics](#metrics-and-diagnostics)
9. [Implementation Plan](#implementation-plan)
10. [Risk Assessment and Mitigations](#risk-assessment-and-mitigations)

---

## Background and Motivation

###  Current Simplification Capabilities

nlp2mcp currently implements two simplification levels (as of Sprint 10):

**Basic Simplification** (`simplify()`):
- Constant folding: `Const(2) + Const(3) → Const(5)`
- Identity operations: `x * 1 → x`, `x + 0 → x`
- Zero elimination: `x * 0 → 0`, `0 / x → 0`
- Double negation: `-(-x) → x`
- Power rules: `x ** 0 → 1`, `x ** 1 → x`

**Advanced Simplification** (`simplify_advanced()`):
- Like-term collection: `x + y + x → 2*x + y`
- Constant collection: `1 + x + 1 → x + 2`
- Multiplicative cancellation: `(c * x) / c → x`
- Power rules: `x^a * x^b → x^(a+b)`, `(x^a)^b → x^(a*b)`

### Why Aggressive Simplification?

**Problem:** Derivative expressions after symbolic differentiation often contain redundant structure that basic/advanced simplification cannot detect:
- **Common factors across terms:** `2*exp(x)*sin(y) + 2*exp(x)*cos(y)` (basic simplification misses the `2*exp(x)` factor)
- **Fraction opportunities:** `(x*y + x*z) / x` (requires distribution then cancellation)
- **Nested constants:** `(x * 2) * 3` (requires associativity reordering)
- **Repeated subexpressions:** `exp(x)*sin(y) + exp(x)*cos(y)` (CSE opportunity)

**Goal:** Reduce derivative term count by ≥20% on ≥50% of benchmark models through algebraic restructuring.

**Target Use Cases:**
1. **Gradient expressions** for KKT stationarity conditions (high redundancy)
2. **Jacobian entries** for complementarity conditions (repeated patterns)
3. **Large-scale models** where compilation and evaluation time matter

---

## Existing Simplification Architecture

### Code Structure (as of Sprint 10)

**Location:** `src/ad/ad_core.py` and `src/ad/term_collection.py`

**Entry Points:**
```python
def simplify(expr: Expr) -> Expr:
    """Basic algebraic simplification (constants, identities, zeros)"""
    
def simplify_advanced(expr: Expr) -> Expr:
    """Advanced simplification with term collection and power rules"""
```

**Key Functions in `term_collection.py`:**
```python
def collect_like_terms(expr: Expr) -> Expr:
    """Flatten additions, extract terms, collect by base, rebuild"""
    
def simplify_multiplicative_cancellation(expr: Expr) -> Expr:
    """Pattern: (c * x) / c → x"""
    
def simplify_power_rules(expr: Expr) -> Expr:
    """Patterns: x^a * x^b → x^(a+b), (x^a)^b → x^(a*b), etc."""
```

### Current Simplification Flow

```
Expression (AST)
     ↓
simplify_advanced(expr)
     ↓
   simplify(expr)  [basic rules bottom-up]
     ↓
   match expr type:
     Binary("+", ...) → collect_like_terms() → simplify()
     Binary("/", ...) → simplify_multiplicative_cancellation() → simplify_power_rules()
     Binary("*", ...) → simplify_power_rules()
     Binary("**", ...) → simplify_power_rules()
     Unary/Call/Sum → recursively process children
     ↓
   Simplified Expression
```

**Design Pattern:** Recursive descent with pattern matching
- Bottom-up: Simplify children first, then parent
- Fixpoint: Recursively apply simplify() after transformations until no change
- Immutable: All transformations return new AST nodes (never mutate input)

### Extension Points for Aggressive Simplification

1. **New function `simplify_aggressive()`:** Top-level orchestrator for 8-step pipeline
2. **New module `src/ad/aggressive_transformations.py`:** Houses new transformation functions
3. **Reuse existing `term_collection.py` helpers:** `_flatten_addition()`, `_extract_term()`, `_collect_terms()`
4. **Integration in `ad_core.py`:** Add `simplify_aggressive()` as third tier above `simplify_advanced()`

---

## Aggressive Simplification Design

### High-Level Architecture

```
                                    ┌─────────────────────────────┐
                                    │   User: --simplification    │
                                    │     (basic|advanced|        │
                                    │      aggressive)            │
                                    └──────────────┬──────────────┘
                                                   │
                          ┌────────────────────────┴────────────────────────┐
                          │                                                 │
                          ▼                                                 ▼
                ┌──────────────────────┐                        ┌──────────────────────┐
                │  simplify_aggressive │ ◄────optional────────  │  --simplification-   │
                │       (expr)         │                        │       stats          │
                └──────────┬───────────┘                        └──────────────────────┘
                           │
                           │  8-Step Pipeline
                           ▼
        ┌──────────────────────────────────────────────────────────────┐
        │                                                              │
        │  Step 1: Basic simplification (existing)                    │
        │  Step 2: Like-term combination (existing)                   │
        │  Step 3: Associativity for constants (NEW)                  │
        │  Step 4: Fraction combining (NEW)                           │
        │  Step 5: Distribution cancellation/factoring (NEW)          │
        │  Step 6: Division simplification (NEW)                      │
        │  Step 7: Multi-term factoring (NEW)                         │
        │  Step 8: CSE (optional, NEW)                                │
        │                                                              │
        │  Each step:                                                  │
        │    - Check applicability (size budget, depth limit)         │
        │    - Apply transformation                                    │
        │    - Validate (FD check if --validate)                      │
        │    - Rollback if size increased >150% with no benefit       │
        │    - Track metrics (term count, operation count)            │
        │                                                              │
        └───────────────────────────┬──────────────────────────────────┘
                                    │
                                    ▼
                            ┌────────────────┐
                            │   Simplified   │
                            │   Expression   │
                            └────────────────┘
```

### Key Design Principles

1. **Ordered Pipeline, Not One-Shot:** Transformations applied sequentially with fixpoint iteration
2. **Safety-First:** Size limits, cancellation detection, rollback on regression
3. **Transparency:** Metrics at every step for debugging and user insight
4. **Backward Compatibility:** Aggressive mode is opt-in; existing modes unchanged
5. **Performance-Bounded:** <10% overhead on total conversion time

---

## Transformation Pipeline

### 8-Step Execution Order

The order is designed to minimize interference between transformations and maximize cancellation opportunities:

```
Step 1: Basic Simplification (existing)
    Purpose: Establish baseline (constants folded, identities eliminated)
    Examples: 1 + 1 → 2, x * 0 → 0, x ** 1 → x
    
Step 2: Like-Term Combination (existing)
    Purpose: Collect coefficients before factoring
    Examples: 2*x + 3*x → 5*x, x + y + x → 2*x + y
    
Step 3: Associativity for Constants (NEW)
    Purpose: Expose more constant folding opportunities
    Examples: (x * 2) * 3 → x * 6, (x / 2) / 3 → x / 6
    Rationale: Must come before factoring to simplify coefficients
    
Step 4: Fraction Combining (NEW)
    Purpose: Consolidate fractions before factoring
    Examples: a/c + b/c → (a + b)/c
    Rationale: Enables detection of common factors in numerators
    
Step 5: Distribution Cancellation/Factoring (NEW)
    Purpose: Factor out common terms
    Examples: x*y + x*z → x*(y + z), 2*exp(x)*sin(y) + 2*exp(x)*cos(y) → 2*exp(x)*(sin(y) + cos(y))
    Rationale: Primary term reduction mechanism; requires consolidated terms from Steps 2-4
    
Step 6: Division Simplification (NEW)
    Purpose: Enable cancellation through division restructuring
    Examples: (x*y) / x → y, (a + b)/c → a/c + b/c (if cancellation detected)
    Rationale: Depends on factored forms from Step 5
    
Step 7: Multi-Term Factoring (NEW)
    Purpose: Expose multiplicative structure across term pairs
    Examples: a*c + a*d + b*c + b*d → (a + b)*(c + d)
    Rationale: Higher-order factoring after simple factoring from Step 5
    
Step 8: CSE (optional, NEW)
    Purpose: Replace repeated subexpressions with temporaries
    Examples: exp(x)*sin(y) + exp(x)*cos(y) → t1 = exp(x); t1*sin(y) + t1*cos(y)
    Rationale: Final pass after all algebraic simplifications complete
```

### Rationale for Ordering

**Why Associativity (Step 3) before Factoring (Step 5)?**
- Example: `(x * 2) + (x * 3) → ?`
- Without Step 3: `(x * 2) + (x * 3)` [cannot factor due to different coefficients]
- With Step 3: `(x * 2) + (x * 3) → x*2 + x*3` [Step 2 collects] `→ x * (2 + 3) → x * 5`

**Why Fraction Combining (Step 4) before Factoring (Step 5)?**
- Example: `a/c + b/c + a/c → ?`
- Without Step 4: Three separate terms, hard to detect `a/c` appears twice
- With Step 4: `(a + b + a)/c → (2*a + b)/c` [more obvious structure]

**Why Division Simplification (Step 6) after Factoring (Step 5)?**
- Example: `(x*y + x*z) / x → ?`
- Without Step 5 first: `(x*y)/x + (x*z)/x` [misses factoring opportunity]
- With Step 5 first: `x*(y + z) / x → (y + z)` [single cancellation]

**Why CSE last (Step 8)?**
- CSE should operate on the fully simplified expression
- Algebraic transformations may eliminate redundancy that CSE would target
- Example: `2*x*exp(y) + 3*x*exp(y)` [Step 2 combines] `→ 5*x*exp(y)` [no CSE needed]

### Fixpoint Iteration

Each step may enable further simplifications in previous steps. Apply fixpoint iteration:

```python
def simplify_aggressive(expr: Expr, max_iterations: int = 5) -> Expr:
    """Apply 8-step pipeline until convergence or max iterations"""
    prev_expr = None
    current_expr = expr
    iteration = 0
    
    while current_expr != prev_expr and iteration < max_iterations:
        prev_expr = current_expr
        current_expr = _apply_pipeline_once(current_expr)
        iteration += 1
    
    return current_expr
```

**Termination:** Either expression stops changing (fixpoint reached) or max iterations hit (5 is reasonable based on typical expression depths).

---

## Individual Transformation Categories

### Category 1: Distribution and Factoring

**Module:** `src/ad/aggressive_transformations.py::simplify_factoring()`

#### Transformation 1.1: Distribution Cancellation (Common Factor Extraction)

**Pattern:** `x*y + x*z → x*(y + z)`

**Algorithm:**
```
1. Flatten addition into list of terms: [x*y, x*z]
2. Extract each term as (coefficient, base):
   - x*y → factors = [x, y]
   - x*z → factors = [x, z]
3. Find common factors across terms:
   - Compute intersection of factor sets
   - Common factors: {x}
4. If common factors exist:
   - Factor out common: x * (y + z)
   - Apply basic simplify() to inner expression
5. Rebuild expression
```

**Implementation:**
```python
def _find_common_factors(terms: list[Expr]) -> list[Expr]:
    """Find factors common to all terms in a sum"""
    if len(terms) == 0:
        return []
    
    # Extract factors from each term
    term_factors = [_get_multiplication_factors(term) for term in terms]
    
    # Find intersection (factors present in ALL terms)
    common = set(term_factors[0])
    for factors in term_factors[1:]:
        common &= set(factors)
    
    return list(common)

def _get_multiplication_factors(expr: Expr) -> list[Expr]:
    """Flatten multiplication into factors: x*y*z → [x, y, z]"""
    if isinstance(expr, Binary) and expr.op == "*":
        return _flatten_multiplication(expr)
    return [expr]

def simplify_factoring(expr: Expr) -> Expr:
    """Factor common terms from sums"""
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr
    
    terms = _flatten_addition(expr)
    common_factors = _find_common_factors(terms)
    
    if len(common_factors) == 0:
        return expr  # No common factors
    
    # Factor out common factors
    # Build: common_factor_1 * common_factor_2 * ... * (remaining_term_1 + remaining_term_2 + ...)
    remaining_terms = []
    for term in terms:
        term_factors = _get_multiplication_factors(term)
        # Remove common factors from this term
        remaining = [f for f in term_factors if f not in common_factors]
        if len(remaining) == 0:
            remaining_terms.append(Const(1))
        elif len(remaining) == 1:
            remaining_terms.append(remaining[0])
        else:
            # Rebuild multiplication
            remaining_expr = remaining[0]
            for factor in remaining[1:]:
                remaining_expr = Binary("*", remaining_expr, factor)
            remaining_terms.append(remaining_expr)
    
    # Build sum of remaining terms
    sum_expr = remaining_terms[0]
    for term in remaining_terms[1:]:
        sum_expr = Binary("+", sum_expr, term)
    
    # Build factored expression: common_factors * sum_expr
    result = sum_expr
    for factor in common_factors:
        result = Binary("*", factor, result)
    
    return simplify(result)  # Basic simplify in case sum reduces to single term
```

**Example:**
```
Input:  2*exp(x)*sin(y) + 2*exp(x)*cos(y)
Terms:  [2*exp(x)*sin(y), 2*exp(x)*cos(y)]
Factors: [[Const(2), exp(x), sin(y)], [Const(2), exp(x), cos(y)]]
Common: {Const(2), exp(x)}
Remaining: [[sin(y)], [cos(y)]]
Output: 2 * exp(x) * (sin(y) + cos(y))
```

#### Transformation 1.2: Multi-Term Factoring

**Pattern:** `a*c + a*d + b*c + b*d → (a + b)*(c + d)`

**Algorithm:**
```
1. Group terms by common factors:
   - {a: [a*c, a*d], b: [b*c, b*d]}
2. For each group, extract remaining factors:
   - a group: [c, d]
   - b group: [c, d]
3. If remaining factors identical across groups:
   - Factor: (a + b) * (c + d)
```

**Complexity:** O(n²) where n = term count. Acceptable for typical expression sizes (<100 terms).

**Heuristic:** Only apply if resulting expression is smaller or enables cancellation.

---

### Category 2: Fraction Simplification

**Module:** `src/ad/aggressive_transformations.py::simplify_fractions()`

#### Transformation 2.1: Combining Fractions (Same Denominator)

**Pattern:** `a/c + b/c → (a + b)/c`

**Algorithm:**
```
1. Flatten addition into terms
2. For each term, check if it's a division
3. Group terms by denominator
4. For groups with ≥2 terms:
   - Combine numerators: (a + b + ...)/c
   - Apply basic simplify() to numerator
```

**Implementation:**
```python
def simplify_fractions(expr: Expr) -> Expr:
    """Combine fractions with common denominators"""
    if not isinstance(expr, Binary) or expr.op != "+":
        return expr
    
    terms = _flatten_addition(expr)
    
    # Group terms by denominator
    divisions = {}  # denominator -> list of numerators
    non_divisions = []
    
    for term in terms:
        if isinstance(term, Binary) and term.op == "/":
            denom = term.right
            numerator = term.left
            if denom not in divisions:
                divisions[denom] = []
            divisions[denom].append(numerator)
        else:
            non_divisions.append(term)
    
    # Combine fractions with same denominator
    combined_terms = non_divisions.copy()
    for denom, numerators in divisions.items():
        if len(numerators) == 1:
            # No combination needed
            combined_terms.append(Binary("/", numerators[0], denom))
        else:
            # Combine: (a + b + ...)/c
            combined_numerator = numerators[0]
            for num in numerators[1:]:
                combined_numerator = Binary("+", combined_numerator, num)
            combined_numerator = simplify(combined_numerator)  # Simplify numerator
            combined_terms.append(Binary("/", combined_numerator, denom))
    
    # Rebuild expression
    if len(combined_terms) == 1:
        return combined_terms[0]
    
    result = combined_terms[0]
    for term in combined_terms[1:]:
        result = Binary("+", result, term)
    
    return result
```

**Example:**
```
Input:  a/c + b/c + x/y
Grouped: {c: [a, b], y: [x]}
Combined: (a + b)/c + x/y
```

#### Transformation 2.2: Distribution Over Division (Conditional)

**Pattern:** `(a + b)/c → a/c + b/c`

**Rationale:** Increases size temporarily but may enable cancellation.

**Heuristic:** Only apply if we detect that `a/c` or `b/c` will simplify further:
- Check if `a` or `b` contains `c` as a factor
- Check if `a` or `b` is a multiplication with constant matching `c`

**Algorithm:**
```
1. Check if numerator is addition
2. Check if distribution enables cancellation:
   - Does a contain c as factor? (common factor detection)
   - Does b contain c as factor?
3. If yes, distribute: (a + b)/c → a/c + b/c
4. Apply simplify() to each resulting division
```

**Trade-off:** This transformation can make expressions larger. Use sparingly and track size budget.

---

### Category 3: Nested Operations

**Module:** `src/ad/aggressive_transformations.py::simplify_nested()`

#### Transformation 3.1: Associativity for Constants

**Pattern:** `(x * c1) * c2 → x * (c1 * c2)`

**Algorithm:**
```
1. Flatten multiplication into factors
2. Separate constants from non-constants
3. Fold constants: c1 * c2 * c3 → c_product
4. Rebuild: x * y * c_product
```

**Implementation:**
```python
def simplify_nested(expr: Expr) -> Expr:
    """Apply associativity to consolidate constants"""
    if not isinstance(expr, Binary) or expr.op not in ("*", "/"):
        return expr
    
    if expr.op == "*":
        # Flatten multiplication
        factors = _flatten_multiplication(expr)
        
        # Separate constants from non-constants
        constants = [f for f in factors if isinstance(f, Const)]
        non_constants = [f for f in factors if not isinstance(f, Const)]
        
        # Fold constants
        const_product = 1.0
        for c in constants:
            const_product *= c.value
        
        # Handle special cases
        if const_product == 0:
            return Const(0)
        if const_product == 1 and len(non_constants) > 0:
            # No constant factor needed
            if len(non_constants) == 1:
                return non_constants[0]
            result = non_constants[0]
            for factor in non_constants[1:]:
                result = Binary("*", result, factor)
            return result
        
        # Rebuild with folded constant at end
        if len(non_constants) == 0:
            return Const(const_product)
        
        result = non_constants[0]
        for factor in non_constants[1:]:
            result = Binary("*", result, factor)
        result = Binary("*", result, Const(const_product))
        return result
    
    elif expr.op == "/":
        # Division chain simplification: (x / c1) / c2 → x / (c1 * c2)
        if isinstance(expr.left, Binary) and expr.left.op == "/":
            inner_numerator = expr.left.left
            inner_denominator = expr.left.right
            outer_denominator = expr.right
            
            # Check if both denominators are constants
            if isinstance(inner_denominator, Const) and isinstance(outer_denominator, Const):
                # Combine: x / (c1 * c2)
                combined_denom = inner_denominator.value * outer_denominator.value
                return Binary("/", inner_numerator, Const(combined_denom))
        
        return expr
```

**Example:**
```
Input:  (x * 2) * 3
Factors: [x, Const(2), Const(3)]
Constants: [Const(2), Const(3)] → product = 6
Non-constants: [x]
Output: x * 6
```

---

### Category 4: Division by Multiplication

**Module:** `src/ad/aggressive_transformations.py::simplify_division()`

#### Transformation 4.1: Constant Extraction from Denominator

**Pattern:** `x / (y * c) → (x / c) / y` or `(x * c1) / (y * c2) → (x * c1/c2) / y`

**Algorithm:**
```
1. Check if denominator is multiplication
2. Extract constant factors from denominator
3. Apply constant division to numerator first
4. Simplify resulting expression
```

**Example:**
```
Input:  (6*x) / (y * 2)
Denominator factors: [y, Const(2)]
Extract constant: (6*x / 2) / y
Simplify numerator: (3*x) / y
Output: (3*x) / y
```

#### Transformation 4.2: Variable Extraction (Cancellation Detection)

**Pattern:** `(x*a) / (x*b) → a / b`

**Algorithm:**
```
1. Flatten numerator and denominator into factors
2. Find common factors between numerator and denominator
3. Cancel common factors
4. Rebuild simplified division
```

**Implementation:**
```python
def simplify_division(expr: Expr) -> Expr:
    """Simplify divisions by extracting and canceling factors"""
    if not isinstance(expr, Binary) or expr.op != "/":
        return expr
    
    numerator = expr.left
    denominator = expr.right
    
    # Extract factors
    num_factors = _get_multiplication_factors(numerator)
    denom_factors = _get_multiplication_factors(denominator)
    
    # Find common factors
    common = []
    remaining_num = num_factors.copy()
    remaining_denom = denom_factors.copy()
    
    for factor in num_factors:
        if factor in remaining_denom:
            common.append(factor)
            remaining_num.remove(factor)
            remaining_denom.remove(factor)
    
    if len(common) == 0:
        return expr  # No cancellation possible
    
    # Rebuild simplified numerator and denominator
    if len(remaining_num) == 0:
        simplified_num = Const(1)
    elif len(remaining_num) == 1:
        simplified_num = remaining_num[0]
    else:
        simplified_num = remaining_num[0]
        for factor in remaining_num[1:]:
            simplified_num = Binary("*", simplified_num, factor)
    
    if len(remaining_denom) == 0:
        # All factors canceled: (x*y) / (x*y) → 1
        return Const(1)
    elif len(remaining_denom) == 1:
        simplified_denom = remaining_denom[0]
    else:
        simplified_denom = remaining_denom[0]
        for factor in remaining_denom[1:]:
            simplified_denom = Binary("*", simplified_denom, factor)
    
    # Rebuild division
    result = Binary("/", simplified_num, simplified_denom)
    return simplify(result)  # Basic simplify for edge cases
```

**Example:**
```
Input:  (x*a*2) / (x*b*3)
Numerator factors: [x, a, Const(2)]
Denominator factors: [x, b, Const(3)]
Common: [x]
Remaining num: [a, Const(2)] → a * 2
Remaining denom: [b, Const(3)] → b * 3
Output: (a * 2) / (b * 3)
Further simplification: (2*a) / (3*b)
```

---

### Category 5: Common Subexpression Elimination (CSE)

**Module:** `src/ad/aggressive_transformations.py::apply_cse()` (optional)

**Pattern:** Replace repeated subexpressions with temporary variables

**Algorithm:**
```
1. Traverse expression tree, collecting all subexpressions with counts
2. Filter subexpressions reused ≥ threshold times (default: 2)
3. Apply cost heuristic: prioritize expensive operations (exp, log, sin, cos, etc.)
4. Generate temporary variables for selected subexpressions
5. Replace occurrences in original expression with temporary references
```

**Cost Model:**
- Constant/VarRef: cost = 1
- Addition/Subtraction: cost = 1
- Multiplication/Division: cost = 2
- Power: cost = 3
- Exponential/Log: cost = 5
- Trig functions: cost = 4

**Threshold:** Only apply CSE if `(cost * reuse_count - cost - 1) > 0`
- Example: `exp(x)` appears 2 times → (5 * 2 - 5 - 1) = 4 > 0 → Apply CSE
- Example: `x + y` appears 2 times → (1 * 2 - 1 - 1) = 0 → Do NOT apply CSE

**Implementation Note:** CSE is OPT-IN via `--cse` flag. May be deferred to Sprint 12 if time constrained.

---

## Heuristics and Safety Mechanisms

### Size Budget (150% Growth Limit)

**Rule:** Reject transformation if expression grows >150% without subsequent simplification benefit.

**Measurement:**
```python
def _expression_size(expr: Expr) -> int:
    """Count total AST nodes in expression"""
    match expr:
        case Const(_) | VarRef(_, _) | ParamRef(_, _):
            return 1
        case Unary(_, child):
            return 1 + _expression_size(child)
        case Binary(_, left, right):
            return 1 + _expression_size(left) + _expression_size(right)
        case Call(_, args):
            return 1 + sum(_expression_size(arg) for arg in args)
        case _:
            return 1

def _check_size_budget(original: Expr, transformed: Expr) -> bool:
    """Return True if size increase is acceptable"""
    original_size = _expression_size(original)
    transformed_size = _expression_size(transformed)
    
    if transformed_size <= original_size:
        return True  # Size decreased or same: always accept
    
    size_increase_ratio = transformed_size / original_size
    return size_increase_ratio <= 1.5  # Accept up to 150% growth
```

**Application:**
```python
def _apply_transformation_with_budget(expr: Expr, transform_func) -> Expr:
    """Apply transformation only if size budget allows"""
    transformed = transform_func(expr)
    
    if _check_size_budget(expr, transformed):
        return transformed
    else:
        # Size budget exceeded: rollback
        return expr
```

### Cancellation Detection

**Goal:** Prioritize transformations that enable immediate cancellation.

**Heuristic for Distribution Over Division:**
```python
def _will_enable_cancellation(numerator: Expr, denominator: Expr) -> bool:
    """Check if distributing numerator will enable cancellation with denominator"""
    if not isinstance(numerator, Binary) or numerator.op != "+":
        return False
    
    # Check if denominator appears as factor in any numerator term
    terms = _flatten_addition(numerator)
    for term in terms:
        factors = _get_multiplication_factors(term)
        if denominator in factors:
            return True  # Cancellation opportunity detected
    
    return False

def simplify_division_distribution(expr: Expr) -> Expr:
    """Conditionally distribute (a + b)/c if cancellation detected"""
    if not isinstance(expr, Binary) or expr.op != "/":
        return expr
    
    numerator = expr.left
    denominator = expr.right
    
    if _will_enable_cancellation(numerator, denominator):
        # Distribute: (a + b)/c → a/c + b/c
        terms = _flatten_addition(numerator)
        distributed = [Binary("/", term, denominator) for term in terms]
        
        # Rebuild sum and simplify
        result = distributed[0]
        for term in distributed[1:]:
            result = Binary("+", result, term)
        
        return simplify(result)  # Let basic simplification handle cancellations
    
    return expr
```

### Depth Limit

**Rule:** Avoid transformations that increase nesting depth beyond threshold.

**Threshold:** Depth limit = 20 (reasonable for typical expressions)

**Measurement:**
```python
def _expression_depth(expr: Expr) -> int:
    """Calculate maximum nesting depth of expression"""
    match expr:
        case Const(_) | VarRef(_, _) | ParamRef(_, _):
            return 0
        case Unary(_, child):
            return 1 + _expression_depth(child)
        case Binary(_, left, right):
            return 1 + max(_expression_depth(left), _expression_depth(right))
        case Call(_, args):
            return 1 + max((_expression_depth(arg) for arg in args), default=0)
        case _:
            return 0

def _check_depth_limit(expr: Expr, max_depth: int = 20) -> bool:
    """Return True if depth is within limit"""
    return _expression_depth(expr) <= max_depth
```

### Rollback Mechanism

**Strategy:** If transformation increases size without benefit, revert to original.

```python
def _apply_transformation_safely(expr: Expr, transform_func, 
                                  simplify_after: bool = True) -> Expr:
    """Apply transformation with automatic rollback if no benefit"""
    original = expr
    original_size = _expression_size(original)
    
    # Apply transformation
    transformed = transform_func(expr)
    
    # Optionally simplify result
    if simplify_after:
        transformed = simplify(transformed)
    
    transformed_size = _expression_size(transformed)
    
    # Check if transformation provided benefit
    if transformed_size <= original_size:
        return transformed  # Size decreased or same: accept
    elif transformed_size / original_size <= 1.5:
        # Size increased but within budget: accept if depth OK
        if _check_depth_limit(transformed):
            return transformed
    
    # No benefit or exceeded limits: rollback
    return original
```

---

## Validation Strategy

### Finite Difference (FD) Validation

**Purpose:** Verify that transformations preserve mathematical correctness.

**Approach:**
```python
def validate_transformation_fd(original: Expr, transformed: Expr, 
                                variables: list[str], 
                                num_test_points: int = 3,
                                epsilon: float = 1e-6) -> bool:
    """Validate transformation using finite difference checks"""
    import numpy as np
    from ..ad.evaluator import evaluate
    
    # Generate random test points
    for _ in range(num_test_points):
        # Create random variable bindings
        bindings = {var: np.random.uniform(-10, 10) for var in variables}
        
        # Evaluate both expressions
        try:
            original_value = evaluate(original, bindings)
            transformed_value = evaluate(transformed, bindings)
            
            # Check if values match within tolerance
            if not np.isclose(original_value, transformed_value, rtol=epsilon, atol=epsilon):
                return False  # Mismatch detected
        except (ZeroDivisionError, ValueError, OverflowError):
            # Skip test points that cause domain errors
            continue
    
    return True  # All test points passed
```

**Integration:**
```python
def simplify_aggressive(expr: Expr, validate: bool = False, 
                        variables: list[str] = None) -> Expr:
    """Apply aggressive simplification with optional validation"""
    transformed = _apply_pipeline(expr)
    
    if validate and variables:
        if not validate_transformation_fd(expr, transformed, variables):
            raise ValueError("Transformation failed FD validation")
    
    return transformed
```

**Note:** FD validation is opt-in via `--validate` flag due to performance overhead.

### PATH Solver Alignment

**Purpose:** Ensure simplified expressions produce same solve results as baseline.

**Approach:**
1. Convert original NLP to MCP, solve with PATH
2. Convert simplified NLP to MCP, solve with PATH
3. Compare:
   - Objective function value
   - Solution vectors (variable values)
   - Solve status (OPTIMAL, INFEASIBLE, etc.)
   - Iteration count (should be similar, ±20%)

**Threshold:** Solutions must match within `tolerance = 1e-4` (relative error)

**Implementation:** Integrated into CI regression tests (Sprint 11 Task: CI Regression Guardrails)

### Performance Budgeting

**Rule:** Aggressive simplification overhead must be <10% of total conversion time.

**Measurement:**
```python
import time

def simplify_aggressive(expr: Expr, performance_budget: float = 0.1) -> Expr:
    """Apply aggressive simplification with performance monitoring"""
    start_time = time.perf_counter()
    
    # Estimate baseline conversion time (from historical data or measurement)
    baseline_time = _estimate_conversion_time(expr)  # Placeholder
    max_allowed_time = baseline_time * performance_budget
    
    # Apply pipeline with timeout
    transformed = _apply_pipeline_with_timeout(expr, timeout=max_allowed_time)
    
    elapsed_time = time.perf_counter() - start_time
    
    # Log performance metrics
    overhead_ratio = elapsed_time / baseline_time if baseline_time > 0 else 0
    logging.info(f"Simplification overhead: {overhead_ratio:.1%} of conversion time")
    
    return transformed
```

**Fallback:** If simplification exceeds budget, abort and return partially simplified expression.

---

## Metrics and Diagnostics

### `--simplification-stats` Output

**Purpose:** Provide transparency into simplification process for debugging and optimization.

**Output Format:**
```
Simplification Statistics:
==========================
Mode: aggressive

Expression Metrics:
  Original:
    - Term count: 42
    - Operation count: 68 (add: 18, mul: 25, div: 12, pow: 4, func: 9)
    - Depth: 7
    - Size (nodes): 94
  
  Simplified:
    - Term count: 31  (-26.2%)
    - Operation count: 48 (add: 14, mul: 18, div: 8, pow: 3, func: 5)  (-29.4%)
    - Depth: 6
    - Size (nodes): 72  (-23.4%)

Pipeline Steps:
  Step 1 (Basic):           94 → 87 nodes  (-7.4%)
  Step 2 (Like-terms):      87 → 81 nodes  (-6.9%)
  Step 3 (Associativity):   81 → 78 nodes  (-3.7%)
  Step 4 (Fractions):       78 → 76 nodes  (-2.6%)
  Step 5 (Factoring):       76 → 68 nodes  (-10.5%)  [BEST]
  Step 6 (Division):        68 → 68 nodes  (0.0%)
  Step 7 (Multi-factor):    68 → 72 nodes  (+5.9%)  [REJECTED: size increased]
  Step 8 (CSE):             72 → 72 nodes  (0.0%)    [skipped: no repeated expensive subexpressions]

Performance:
  Simplification time: 0.042s
  Total conversion time: 0.385s
  Overhead: 10.9%  [WARNING: exceeds 10% target]

Transformations Applied:
  - Constant folding: 5 instances
  - Like-term combination: 3 instances
  - Associativity consolidation: 2 instances
  - Fraction combining: 1 instance
  - Common factor extraction: 2 instances (saved 8 operations)

Validation:
  FD checks: PASSED (3/3 test points within 1e-6 tolerance)
```

### Metrics Data Structure

```python
@dataclass
class SimplificationMetrics:
    original_term_count: int
    original_op_count: dict[str, int]  # {"+": 18, "*": 25, ...}
    original_depth: int
    original_size: int
    
    simplified_term_count: int
    simplified_op_count: dict[str, int]
    simplified_depth: int
    simplified_size: int
    
    step_sizes: list[tuple[str, int]]  # [(step_name, size_after_step), ...]
    
    simplification_time: float
    total_conversion_time: float
    
    transformations_applied: dict[str, int]  # {transformation_name: count}
    
    validation_passed: bool
    validation_details: str

def collect_metrics(original: Expr, simplified: Expr, 
                     step_history: list[tuple[str, Expr]]) -> SimplificationMetrics:
    """Collect comprehensive simplification metrics"""
    # Implementation omitted for brevity
    pass
```

### Integration with `--diagnostic` Mode

Sprint 11 will also introduce `--diagnostic` mode (separate task). Simplification metrics should integrate:

```
--diagnostic output:
  ...
  Stage 4: Differentiation
    ...
  Stage 5: Simplification (aggressive)
    [Simplification Statistics as above]
  Stage 6: Jacobian Assembly
    ...
```

---

## Implementation Plan

### Module Structure

```
src/ad/
  ├── ad_core.py                      [MODIFY: add simplify_aggressive()]
  ├── term_collection.py              [REUSE: _flatten_addition, _extract_term, etc.]
  ├── aggressive_transformations.py   [NEW: all new transformation functions]
  └── simplification_metrics.py       [NEW: metrics collection and reporting]
```

### New Module: `aggressive_transformations.py`

```python
"""
Aggressive simplification transformations for nlp2mcp.

This module implements advanced algebraic transformations that extend
beyond basic and advanced simplification:
  - Distribution and factoring (common factor extraction, multi-term factoring)
  - Fraction simplification (combining, distribution over division)
  - Nested operations (associativity, division chains)
  - Division by multiplication (constant/variable extraction)
  - Optional CSE (common subexpression elimination)

Each transformation is implemented as a pure function: Expr → Expr.
Transformations never mutate input expressions (immutable AST design).
"""

from ..ir.ast import Expr, Binary, Const, Unary
from .term_collection import _flatten_addition, _flatten_multiplication

# Category 1: Distribution and Factoring
def simplify_factoring(expr: Expr) -> Expr: ...
def simplify_multi_term_factoring(expr: Expr) -> Expr: ...

# Category 2: Fraction Simplification
def simplify_fractions(expr: Expr) -> Expr: ...
def simplify_division_distribution(expr: Expr) -> Expr: ...

# Category 3: Nested Operations
def simplify_nested(expr: Expr) -> Expr: ...

# Category 4: Division by Multiplication
def simplify_division(expr: Expr) -> Expr: ...

# Category 5: CSE (optional)
def apply_cse(expr: Expr, threshold: int = 2) -> Expr: ...

# Helpers
def _find_common_factors(terms: list[Expr]) -> list[Expr]: ...
def _get_multiplication_factors(expr: Expr) -> list[Expr]: ...
def _will_enable_cancellation(numerator: Expr, denominator: Expr) -> bool: ...
```

### Modified: `ad_core.py`

```python
def simplify_aggressive(expr: Expr, 
                         enable_cse: bool = False,
                         collect_metrics: bool = False,
                         validate: bool = False,
                         variables: list[str] = None) -> tuple[Expr, SimplificationMetrics | None]:
    """
    Apply aggressive simplification with 8-step pipeline.
    
    Args:
        expr: Expression to simplify
        enable_cse: Apply CSE in Step 8 (default: False)
        collect_metrics: Collect and return metrics (default: False)
        validate: Apply FD validation (default: False)
        variables: Variable list for validation (required if validate=True)
    
    Returns:
        Tuple of (simplified_expr, metrics or None)
    """
    from .aggressive_transformations import (
        simplify_factoring, simplify_fractions, simplify_nested,
        simplify_division, simplify_multi_term_factoring, apply_cse
    )
    from .simplification_metrics import collect_metrics
    
    if collect_metrics:
        metrics_tracker = MetricsTracker(expr)
    
    # 8-step pipeline with fixpoint iteration
    current = expr
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        prev = current
        
        # Step 1: Basic simplification
        current = simplify(current)
        if collect_metrics: metrics_tracker.record_step("basic", current)
        
        # Step 2: Like-term combination
        current = simplify_advanced(current)
        if collect_metrics: metrics_tracker.record_step("like-terms", current)
        
        # Step 3: Associativity for constants
        current = _apply_transformation_safely(current, simplify_nested)
        if collect_metrics: metrics_tracker.record_step("associativity", current)
        
        # Step 4: Fraction combining
        current = _apply_transformation_safely(current, simplify_fractions)
        if collect_metrics: metrics_tracker.record_step("fractions", current)
        
        # Step 5: Distribution cancellation/factoring
        current = _apply_transformation_safely(current, simplify_factoring)
        if collect_metrics: metrics_tracker.record_step("factoring", current)
        
        # Step 6: Division simplification
        current = _apply_transformation_safely(current, simplify_division)
        if collect_metrics: metrics_tracker.record_step("division", current)
        
        # Step 7: Multi-term factoring
        current = _apply_transformation_safely(current, simplify_multi_term_factoring)
        if collect_metrics: metrics_tracker.record_step("multi-factor", current)
        
        # Step 8: CSE (optional)
        if enable_cse:
            current = _apply_transformation_safely(current, lambda e: apply_cse(e, threshold=2))
            if collect_metrics: metrics_tracker.record_step("cse", current)
        
        # Check fixpoint convergence
        if current == prev:
            break
        
        iteration += 1
    
    # Validation
    if validate:
        if not validate_transformation_fd(expr, current, variables):
            raise ValueError("Aggressive simplification failed FD validation")
    
    # Collect final metrics
    final_metrics = None
    if collect_metrics:
        final_metrics = metrics_tracker.finalize(current)
    
    return current, final_metrics
```

### Implementation Phases

**Phase 1: Core Infrastructure (3-4 hours)**
- Create `aggressive_transformations.py` module skeleton
- Implement helper functions (`_find_common_factors`, `_get_multiplication_factors`, size/depth checkers)
- Implement safety wrappers (`_apply_transformation_safely`, `_check_size_budget`)
- Add `simplify_aggressive()` skeleton to `ad_core.py`

**Phase 2: Transformations Category 1 (Distribution/Factoring, 2-3 hours)**
- Implement `simplify_factoring()` (common factor extraction)
- Implement `simplify_multi_term_factoring()` (multi-term patterns)
- Unit tests for both functions

**Phase 3: Transformations Categories 2-4 (Fractions, Nested, Division, 4-5 hours)**
- Implement `simplify_fractions()` (combining same denominator)
- Implement `simplify_division_distribution()` (conditional distribution)
- Implement `simplify_nested()` (associativity, division chains)
- Implement `simplify_division()` (constant/variable extraction)
- Unit tests for all functions

**Phase 4: Pipeline Integration (2-3 hours)**
- Complete `simplify_aggressive()` with 8-step pipeline
- Implement fixpoint iteration logic
- Add validation hooks (FD checks)
- Integration tests with realistic expressions

**Phase 5: Metrics and Diagnostics (2-3 hours)**
- Implement `simplification_metrics.py` module
- Implement `--simplification-stats` output formatting
- Add performance monitoring
- CLI integration (`--simplification aggressive`, `--simplification-stats`)

**Phase 6: CSE (Optional, 2-3 hours or defer to Sprint 12)**
- Implement `apply_cse()` with cost model
- Add `--cse` flag
- Unit tests

**Total:** 12-15 hours baseline, 15-18 hours with CSE

---

## Risk Assessment and Mitigations

### Risk 1: Expression Size Explosion

**Probability:** 30%  
**Impact:** HIGH (unacceptable performance, unusable expressions)

**Mitigation:**
- 150% size budget enforced at every transformation
- Automatic rollback if budget exceeded
- Cancellation detection before applying expansive transformations
- Depth limit prevents pathological nesting

**Fallback:** If aggressive simplification causes size explosion, fall back to advanced simplification.

### Risk 2: Incorrect Transformations (Correctness Bugs)

**Probability:** 20%  
**Impact:** CRITICAL (wrong KKT conditions, incorrect MCP solve)

**Mitigation:**
- Comprehensive unit tests for each transformation (50+ test cases)
- FD validation (opt-in via `--validate`)
- PATH solver alignment in CI regression tests
- Extensive test coverage on benchmark models before release

**Fallback:** If validation fails, raise error and reject transformation.

### Risk 3: Performance Overhead >10%

**Probability:** 25%  
**Impact:** MEDIUM (user frustration, slower conversion)

**Mitigation:**
- Performance budgeting with timeout enforcement
- Metrics collection to identify bottleneck transformations
- Early termination if overhead exceeds threshold
- Profiling and optimization before Sprint 11 completion

**Fallback:** Make aggressive simplification opt-in or reduce transformation scope.

### Risk 4: Insufficient Term Reduction (<20% on <50% models)

**Probability:** 35%  
**Impact:** MEDIUM (fails benchmark target, limited value)

**Mitigation:**
- Prioritize high-value transformations (factoring, fraction combining)
- Test on benchmark models early (Sprint 11 Day 3-4)
- Iterate on heuristics based on benchmark results
- Document which model types benefit most

**Fallback:** Adjust target to "≥15% on ≥50% models" or "≥20% on ≥40% models" if initial results underwhelming.

### Risk 5: Transformation Ordering Wrong

**Probability:** 20%  
**Impact:** MEDIUM (suboptimal simplification, missed opportunities)

**Mitigation:**
- Extensive testing of pipeline ordering
- A/B test alternative orderings on benchmark models
- Metrics at each step show which steps provide most value
- Iterate on ordering based on data

**Fallback:** Allow users to customize ordering via config file (future enhancement).

---

## Appendix A: Example Transformations

### Example 1: Gradient with Common Factors

**Input:**
```
grad_x = 2*exp(x)*sin(y) + 2*exp(x)*cos(y) + 3*exp(x)*sin(z)
```

**Step-by-step:**
1. **Basic simplification:** No change
2. **Like-term combination:** No change (different bases)
3. **Associativity:** No change
4. **Fractions:** No change (no divisions)
5. **Factoring (common factor extraction):**
   - Common factors in all terms: `{Const(2), exp(x)}` (first two terms), `{Const(3), exp(x)}` (third term)
   - Partial factoring: `2*exp(x)*(sin(y) + cos(y)) + 3*exp(x)*sin(z)`
   - Further factoring: `exp(x) * (2*(sin(y) + cos(y)) + 3*sin(z))`

**Output:**
```
grad_x = exp(x) * (2*(sin(y) + cos(y)) + 3*sin(z))
```

**Metrics:**
- Before: 8 operations (4 mul, 2 add, 2 func)
- After: 5 operations (3 mul, 2 add)
- Reduction: 37.5%

### Example 2: Fraction Simplification

**Input:**
```
grad_y = a/c + b/c + x/d + y/d
```

**Step-by-step:**
1. **Basic simplification:** No change
2. **Like-term combination:** No change
3. **Associativity:** No change
4. **Fraction combining:**
   - Group by denominator: `{c: [a, b], d: [x, y]}`
   - Combine: `(a + b)/c + (x + y)/d`

**Output:**
```
grad_y = (a + b)/c + (x + y)/d
```

**Metrics:**
- Before: 6 operations (4 div, 2 add)
- After: 4 operations (2 div, 2 add)
- Reduction: 33.3%

### Example 3: Division with Cancellation

**Input:**
```
grad_z = (x*y + x*z) / x
```

**Step-by-step:**
1. **Basic simplification:** No change
2. **Like-term combination:** No change
3. **Associativity:** No change
4. **Fractions:** No change (only one fraction)
5. **Factoring (numerator):** `x*(y + z) / x`
6. **Division simplification (cancellation):** `(y + z)`

**Output:**
```
grad_z = y + z
```

**Metrics:**
- Before: 4 operations (2 mul, 1 add, 1 div)
- After: 1 operation (1 add)
- Reduction: 75%

---

## Appendix B: Configuration Options

### CLI Flags

```bash
# Simplification mode selection
--simplification {basic|advanced|aggressive}  # Default: advanced

# Aggressive simplification options
--cse                       # Enable CSE in Step 8 (default: disabled)
--simplification-stats      # Print detailed simplification metrics
--validate                  # Enable FD validation (slower)

# Performance tuning
--simplification-timeout SECONDS  # Max time for simplification (default: no limit)
--size-budget-ratio FLOAT         # Max size increase ratio (default: 1.5)
--depth-limit INT                 # Max expression depth (default: 20)
```

### Configuration File (`config.yaml`)

```yaml
simplification:
  mode: aggressive
  
  aggressive:
    enable_cse: false
    collect_metrics: true
    validate: false
    
    heuristics:
      size_budget_ratio: 1.5
      depth_limit: 20
      cancellation_detection: true
    
    performance:
      timeout_seconds: 10
      max_overhead_ratio: 0.10  # 10% of conversion time
    
    pipeline:
      max_iterations: 5
      steps:
        - basic
        - like_terms
        - associativity
        - fractions
        - factoring
        - division
        - multi_factoring
        - cse  # Only if enable_cse: true
```

---

## Document Control

**Version:** 1.0  
**Date:** 2025-11-25  
**Author:** Claude (Sprint 11 Prep Task 3)  
**Status:** Architecture Design (Pre-Implementation)  
**Next Review:** Sprint 11 Day 1 (before implementation begins)

**Change History:**
- 2025-11-25: Initial version (comprehensive architecture design)

**Related Documents:**
- `docs/planning/EPIC_2/PROJECT_PLAN.md` (Sprint 11 specification, lines 436-638)
- `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknowns 1.2-1.11)
- `src/ad/ad_core.py` (existing simplification implementation)
- `src/ad/term_collection.py` (existing term collection utilities)
