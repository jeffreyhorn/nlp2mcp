# Aggressive Simplification Transformation Catalog

**Date:** 2025-11-25  
**Sprint:** Sprint 11 (Weeks 11-12)  
**Purpose:** Comprehensive reference for all aggressive simplification patterns

---

## Overview

This catalog documents all 18 transformation patterns in aggressive simplification mode, organized by category. Each pattern includes:
- **Pattern:** Mathematical transformation rule
- **Applicability:** When to apply this transformation
- **Example:** Before/after with realistic expressions
- **Implementation Notes:** Key algorithms or edge cases
- **Priority:** Importance ranking (HIGH/MEDIUM/LOW)

**Total Transformations:** 18 patterns across 5 categories (includes 1 duplicate pattern T4.3=T2.2, and 3 already-implemented patterns)

---

## Table of Contents

1. [Category 1: Distribution and Factoring (4 patterns)](#category-1-distribution-and-factoring)
2. [Category 2: Fraction Simplification (4 patterns)](#category-2-fraction-simplification)
3. [Category 3: Nested Operations (3 patterns)](#category-3-nested-operations)
4. [Category 4: Division by Multiplication (3 patterns)](#category-4-division-by-multiplication)
5. [Category 5: Common Subexpression Elimination (4 patterns)](#category-5-common-subexpression-elimination)

---

## Category 1: Distribution and Factoring

### T1.1: Common Factor Extraction (Single Term)

**Pattern:** `x*y + x*z → x*(y + z)`

**Applicability:**
- Sum with ≥2 terms sharing common multiplicative factors
- Common factors can be constants, variables, or function calls
- Apply whenever detected (always beneficial)

**Example:**
```
Before: 2*exp(x)*sin(y) + 2*exp(x)*cos(y)
Common factors: {Const(2), exp(x)}
After:  2*exp(x)*(sin(y) + cos(y))

Reduction: 5 operations → 4 operations (20% reduction)
```

**Implementation Notes:**
- Flatten addition into terms
- Extract factors from each term (flatten multiplication)
- Compute intersection of factor sets
- Factor out common factors, rebuild remaining sum
- Recursively simplify inner expression

**Edge Cases:**
- If all factors common: `x*y + x*y → 2*x*y` (handled by like-term combination first)
- Constants with different values: `2*x + 3*x` (handled by like-term combination, not factoring)

**Priority:** HIGH (primary term reduction mechanism)

---

### T1.2: Common Factor Extraction (Multiple Terms)

**Pattern:** `x*y + x*z + x*w → x*(y + z + w)`

**Applicability:**
- Extension of T1.1 to ≥3 terms
- Same applicability criteria as T1.1

**Example:**
```
Before: exp(a)*b + exp(a)*c + exp(a)*d + exp(a)*e
Common factors: {exp(a)}
After:  exp(a)*(b + c + d + e)

Reduction: 7 operations (4 mul, 3 add) → 5 operations (1 mul, 3 add, 1 func)
```

**Implementation Notes:**
- Same algorithm as T1.1
- Scales to arbitrary number of terms
- Intersection computation is O(n*m) where n=term count, m=average factors per term

**Priority:** HIGH

---

### T1.3: Multi-Term Factoring (2x2 Pattern)

**Pattern:** `a*c + a*d + b*c + b*d → (a + b)*(c + d)`

**Applicability:**
- Exactly 4 terms with 2x2 factor structure
- Two groups of terms share partial common factors
- Result expression must be smaller or enable further simplification

**Example:**
```
Before: x*y + x*z + w*y + w*z
Grouping: {x: [x*y, x*z], w: [w*y, w*z]}
Remaining factors: {x group: [y, z], w group: [y, z]}
After:  (x + w)*(y + z)

Reduction: 6 operations (4 mul, 2 add) → 3 operations (2 add, 1 mul)
```

**Implementation Notes:**
- Group terms by common factors
- For each group, extract remaining factors
- If remaining factors identical across ≥2 groups, factor
- Complexity: O(n²) for n terms (acceptable for n < 100)

**Edge Cases:**
- Partial matches: `a*c + a*d + b*c` (cannot factor without 4th term `b*d`)
- Constants: `2*a*c + 2*a*d + 2*b*c + 2*b*d → 2*(a+b)*(c+d)` (extract constant first)

**Priority:** MEDIUM (rare in practice, high complexity)

---

### T1.4: Coefficient Factoring (Already Implemented)

**Pattern:** `2*x + 3*x → 5*x`

**Applicability:**
- Terms with same base, different coefficients
- Already handled by like-term combination in advanced simplification

**Example:**
```
Before: 2*x + 3*x
After:  5*x

Reduction: 3 operations → 2 operations
```

**Implementation Notes:**
- No new implementation needed (existing `collect_like_terms()`)
- Documented here for completeness

**Priority:** N/A (already implemented)

---

## Category 2: Fraction Simplification

### T2.1: Fraction Combining (Same Denominator)

**Pattern:** `a/c + b/c → (a + b)/c`

**Applicability:**
- ≥2 division terms in sum with identical denominators
- Always beneficial (reduces division operation count)

**Example:**
```
Before: x/y + z/y + w/y
Grouped by denominator: {y: [x, z, w]}
After:  (x + z + w)/y

Reduction: 5 operations (3 div, 2 add) → 3 operations (1 div, 2 add)
```

**Implementation Notes:**
- Flatten addition into terms
- Group divisions by denominator (use Expr equality)
- For groups with ≥2 numerators, combine
- Simplify combined numerator before rebuilding

**Edge Cases:**
- Mixed divisions and non-divisions: `a/c + b/c + d` → `(a+b)/c + d`
- Const denominators: `x/2 + y/2 → (x+y)/2` (works naturally)

**Priority:** HIGH (common pattern in derivatives)

---

### T2.2: Distribution Over Division (Conditional)

**Pattern:** `(a + b)/c → a/c + b/c`

**Applicability:**
- Numerator is sum
- **Condition:** Distribution enables cancellation (denominator appears as factor in numerator terms)
- Otherwise: size increases without benefit

**Example (Beneficial):**
```
Before: (x*y + x*z) / x
Cancellation detected: x is factor in both numerator terms
Distribute: (x*y)/x + (x*z)/x
Simplify: y + z

Reduction: 4 operations → 1 operation (75% reduction)
```

**Example (NOT Beneficial):**
```
Before: (a + b) / c
No cancellation detected (c not a factor in a or b)
After:  (a + b) / c  [transformation NOT applied]
```

**Implementation Notes:**
- Check if denominator appears as multiplicative factor in any numerator term
- Only distribute if cancellation detected
- Apply basic simplification after distribution to realize cancellations

**Edge Cases:**
- Partial cancellation: `(x*y + z)/x` (only first term cancels) - still beneficial
- Nested sums: `((a+b) + c)/d` (flatten first)

**Priority:** HIGH (enables critical cancellations)

---

### T2.3: Common Denominator (Defer to Future Sprint)

**Pattern:** `a/b + c/d → (a*d + c*b)/(b*d)`

**Applicability:**
- Two divisions with different denominators
- **Caution:** Significantly increases size (2 operations → 5 operations)
- Only beneficial if numerator `(a*d + c*b)` simplifies substantially (≥40% reduction)

**Example (Rare Beneficial Case):**
```
Before: x/(x*y) + y/(x*y*z)
Common denominator: (x*y*z)
After:  (x*z + y)/(x*y*z)
Further simplification: ?

Size increase: 4 operations → 6 operations (50% increase)
```

**Implementation Notes:**
- **DEFER to Sprint 12:** High complexity, rare benefit
- Requires sophisticated heuristics to detect when numerator will simplify
- Risk: Expression explosion without benefit

**Priority:** LOW (defer implementation)

---

### T2.4: Multiplicative Cancellation (Already Implemented)

**Pattern:** `(c * x) / c → x` or `(x * c) / c → x`

**Applicability:**
- Division where numerator is multiplication containing constant factor matching denominator
- Already handled by existing `simplify_multiplicative_cancellation()`

**Example:**
```
Before: (2 * x) / 2
After:  x

Reduction: 2 operations → 0 operations
```

**Implementation Notes:**
- No new implementation needed
- Documented here for completeness

**Priority:** N/A (already implemented)

---

## Category 3: Nested Operations

### T3.1: Associativity for Constants (Multiplication)

**Pattern:** `(x * c1) * c2 → x * (c1 * c2)` where c1, c2 are constants

**Applicability:**
- Nested multiplication with ≥2 constant factors
- Always beneficial (reduces operations through constant folding)

**Example:**
```
Before: ((x * 2) * 3) * 5
Flatten: [x, Const(2), Const(3), Const(5)]
Fold constants: 2 * 3 * 5 = 30
After:  x * 30

Reduction: 3 operations (3 mul) → 1 operation (1 mul)
```

**Implementation Notes:**
- Flatten multiplication into factor list
- Separate constants from non-constants
- Fold all constants into single value
- Rebuild multiplication with folded constant

**Edge Cases:**
- All constants: `2 * 3 * 4 → 24` (basic simplification handles this)
- Zero constant: `x * 0 * 5 → 0` (basic simplification handles this)

**Priority:** HIGH (enables more constant folding)

---

### T3.2: Division Chain Simplification

**Pattern:** `(x / c1) / c2 → x / (c1 * c2)` where c1, c2 are constants

**Applicability:**
- Nested division with constant denominators
- Always beneficial (consolidates divisions)

**Example:**
```
Before: ((x / 2) / 3) / 5
After:  x / 30

Reduction: 3 operations (3 div) → 1 operation (1 div)
```

**Implementation Notes:**
- Recursively traverse left side of divisions
- Accumulate constant denominators
- Rebuild with single division by product

**Edge Cases:**
- Mixed multiplication and division: `(x * 2) / 3` (handle separately in T3.1)
- Variable denominators: `(x / y) / z` (no simplification possible)

**Priority:** MEDIUM (less common than T3.1)

---

### T3.3: Multiplication-Division Reordering (Defer)

**Pattern:** `(x * y) / z → x * (y / z)` if `y/z` simplifies

**Applicability:**
- Division where numerator is multiplication
- Reordering enables cancellation or simplification

**Example:**
```
Before: (x * (a*b)) / a
Reorder: x * ((a*b) / a)
Simplify: x * b

Reduction: 3 operations → 2 operations
```

**Implementation Notes:**
- **DEFER to Sprint 12:** Complex heuristics needed
- Must predict if reordering beneficial (try speculatively and rollback?)
- Risk: Increases depth without benefit

**Priority:** LOW (defer implementation)

---

## Category 4: Division by Multiplication

### T4.1: Constant Extraction from Denominator

**Pattern:** `x / (y * c) → (x / c) / y` or `(x * c1) / (y * c2) → (x * (c1/c2)) / y`

**Applicability:**
- Denominator is multiplication containing constant factor
- Simplifies constant division first, then variable division

**Example:**
```
Before: (6*x) / (y * 2)
Extract constant 2 from denominator
Apply to numerator: (6*x / 2) / y
Simplify numerator: (3*x) / y
After:  (3*x) / y

Reduction: 4 operations (2 mul, 1 div) → 3 operations (1 mul, 1 div)
```

**Implementation Notes:**
- Extract constant factors from denominator
- Apply constant division to numerator
- Simplify numerator before rebuilding division

**Edge Cases:**
- Multiple constants in denominator: `x / (y * 2 * 3)` → `x / (y * 6)` (apply T3.1 first)
- Constant in numerator and denominator: apply constant division directly

**Priority:** MEDIUM (useful but less common)

---

### T4.2: Variable Factor Cancellation

**Pattern:** `(x*a) / (x*b) → a / b`

**Applicability:**
- Numerator and denominator share common variable factors
- Always beneficial (eliminates redundant multiplications and divisions)

**Example:**
```
Before: (x*y*a) / (x*y*b)
Common factors: {x, y}
Remaining numerator: [a]
Remaining denominator: [b]
After:  a / b

Reduction: 5 operations (4 mul, 1 div) → 1 operation (1 div)
```

**Implementation Notes:**
- Flatten numerator and denominator into factors
- Find intersection (common factors)
- Cancel common factors
- Rebuild simplified division

**Edge Cases:**
- Complete cancellation: `(x*y) / (x*y) → 1`
- Partial cancellation: `(x*y*z) / (x*w) → (y*z) / w`
- Constants with common factors: `(6*x) / (3*x) → 2` (combine T4.1 and T4.2)

**Priority:** HIGH (critical for derivative simplification)

---

### T4.3: Distribution for Cancellation (Same as T2.2)

**Pattern:** `(x*y + x*z) / x → (x*y)/x + (x*z)/x → y + z`

**Applicability:**
- See T2.2 (Distribution Over Division)
- Included here for category completeness

**Priority:** HIGH (see T2.2)

---

## Category 5: Common Subexpression Elimination (Optional)

### T5.1: Expensive Function CSE

**Pattern:** Replace repeated expensive function calls with temporary variable

**Applicability:**
- Subexpression appears ≥2 times
- Subexpression contains expensive operation (exp, log, sin, cos, sqrt, etc.)
- Cost savings: `(cost * reuse_count - cost - 1) > 0`

**Example:**
```
Before: exp(x)*sin(y) + exp(x)*cos(y) + exp(x)*tan(y)
Repeated: exp(x) appears 3 times (cost = 5, reuse = 3)
Cost savings: (5 * 3 - 5 - 1) = 9 > 0 ✓
After:  t1 = exp(x)
        result = t1*sin(y) + t1*cos(y) + t1*tan(y)
```

**Implementation Notes:**
- Traverse expression tree, collect subexpressions with counts
- Apply cost model to prioritize expensive operations
- Generate temporary variables (t1, t2, ...)
- Replace occurrences with temporary references

**Cost Model:**
- Const/VarRef: 1
- Add/Sub: 1
- Mul/Div: 2
- Power: 3
- Trig (sin, cos, tan): 4
- Exponential/Log: 5

**Priority:** MEDIUM (opt-in via `--cse` flag)

---

### T5.2: Nested Expression CSE

**Pattern:** Replace repeated complex subexpressions

**Applicability:**
- Subexpression is composite (e.g., `x*y + z`)
- Appears ≥2 times
- Reuse threshold higher than T5.1 (≥3 times recommended)

**Example:**
```
Before: (x*y + z)^2 + 3*(x*y + z) + sin(x*y + z)
Repeated: (x*y + z) appears 3 times
After:  t1 = x*y + z
        result = t1^2 + 3*t1 + sin(t1)

Reduction: 9 operations → 5 operations + 1 assignment
```

**Implementation Notes:**
- Use hash-based subexpression detection
- Require higher reuse threshold (≥3) to justify overhead
- CSE only after all algebraic simplifications complete

**Priority:** LOW (diminishing returns for most expressions)

---

### T5.3: Multiplicative Subexpression CSE

**Pattern:** Replace repeated multiplication patterns

**Applicability:**
- Subexpression is multiplication (e.g., `x*y`)
- Appears ≥3 times (higher threshold due to low cost)
- Cost savings calculation still positive

**Example:**
```
Before: x*y*a + x*y*b + x*y*c + x*y*d
Repeated: x*y appears 4 times (cost = 2, reuse = 4)
Cost savings: (2 * 4 - 2 - 1) = 5 > 0 ✓
After:  t1 = x*y
        result = t1*a + t1*b + t1*c + t1*d

Note: Factoring (T1.2) would produce same result without CSE:
      (x*y)*(a + b + c + d)
      Factoring is preferred (no temporary variable needed)
```

**Implementation Notes:**
- Apply CSE only if factoring not applicable
- Lower priority than algebraic simplifications

**Priority:** LOW (factoring usually handles this better)

---

### T5.4: CSE with Aliasing (Defer to Future Sprint)

**Pattern:** Detect equivalent subexpressions with commutativity/associativity

**Applicability:**
- Expressions equivalent under commutativity: `x*y` ≡ `y*x`
- Expressions equivalent under associativity: `(x+y)+z` ≡ `x+(y+z)`

**Example:**
```
Before: x*y + y*x + x*y
Canonicalize: x*y ≡ y*x (assume x < y in canonical ordering)
Repeated: x*y appears 3 times
After:  t1 = x*y
        result = t1 + t1 + t1 = 3*t1
```

**Implementation Notes:**
- **DEFER to Sprint 12+:** Requires expression canonicalization
- Complexity: O(n log n) for sorting factors
- Benefit: Marginal (most cases already handled by like-term combination)

**Priority:** LOW (defer implementation)

---

## Transformation Priority Summary

### HIGH Priority (Implement in Sprint 11)

1. **T1.1:** Common Factor Extraction (Single Term)
2. **T1.2:** Common Factor Extraction (Multiple Terms)
3. **T2.1:** Fraction Combining (Same Denominator)
4. **T2.2:** Distribution Over Division (Conditional)
5. **T3.1:** Associativity for Constants (Multiplication)
6. **T4.2:** Variable Factor Cancellation

**Total: 6 transformations** (core aggressive simplification)

### MEDIUM Priority (Implement in Sprint 11 if time permits)

7. **T1.3:** Multi-Term Factoring (2x2 Pattern)
8. **T3.2:** Division Chain Simplification
9. **T4.1:** Constant Extraction from Denominator
10. **T5.1:** Expensive Function CSE

**Total: 4 transformations** (valuable but less critical)

### LOW Priority (Defer to Sprint 12)

11. **T2.3:** Common Denominator
12. **T3.3:** Multiplication-Division Reordering
13. **T5.2:** Nested Expression CSE
14. **T5.3:** Multiplicative Subexpression CSE
15. **T5.4:** CSE with Aliasing

**Total: 5 transformations** (defer due to complexity or low benefit)

### Already Implemented (No Action Needed)

16. **T1.4:** Coefficient Factoring (like-term combination)
17. **T2.4:** Multiplicative Cancellation
18. **Power Rules:** x^a * x^b, (x^a)^b, x^a / x^b (existing `simplify_power_rules()`)

**Total: 3 transformations** (already in codebase)

---

## Implementation Effort Estimate

### Sprint 11 Baseline (HIGH priority only)

| Transformation | Effort | Complexity |
|---|---|---|
| T1.1 Common Factor Extraction | 2h | MEDIUM |
| T1.2 Common Factor (Multiple) | +0.5h | LOW (extends T1.1) |
| T2.1 Fraction Combining | 1.5h | MEDIUM |
| T2.2 Distribution (Conditional) | 2h | MEDIUM |
| T3.1 Associativity | 1h | LOW |
| T4.2 Variable Cancellation | 1.5h | MEDIUM |
| Pipeline integration | 2h | - |
| Metrics/diagnostics | 2h | - |
| **Total** | **12.5h** | - |

### Sprint 11 Extended (+ MEDIUM priority)

| Transformation | Effort | Complexity |
|---|---|---|
| T1.3 Multi-Term Factoring | 2h | HIGH |
| T3.2 Division Chain | 0.5h | LOW |
| T4.1 Constant Extraction | 1h | MEDIUM |
| T5.1 Expensive Function CSE | 2h | MEDIUM |
| **Additional Total** | **5.5h** | - |
| **Grand Total** | **14h** | - |

### Sprint 12 (LOW priority deferred)

| Transformation | Effort | Complexity |
|---|---|---|
| T2.3 Common Denominator | 2h | HIGH |
| T3.3 Reordering | 1.5h | MEDIUM |
| T5.2 Nested CSE | 1h | MEDIUM |
| T5.3 Multiplicative CSE | 0.5h | LOW |
| T5.4 CSE Aliasing | 3h | HIGH |
| **Total** | **8h** | - |

---

## Testing Strategy

### Unit Test Coverage

Each transformation requires:
- **Positive tests:** Transformation applies correctly (5-10 cases per transformation)
- **Negative tests:** Transformation does NOT apply when inappropriate (3-5 cases)
- **Edge cases:** Boundary conditions (zero, one, constants, nested) (3-5 cases)

**Total unit tests:** 6 HIGH transformations * 15 tests = **90 unit tests minimum**

### Integration Tests

- **End-to-end pipeline:** Input expression → full 8-step pipeline → output
- **Benchmark expressions:** Realistic derivative expressions from GAMSLIB models
- **Metric validation:** Term count reduction ≥20% on test cases

**Total integration tests:** 10-15 comprehensive scenarios

### Regression Tests

- All existing simplification tests must pass
- No breaking changes to `simplify()` or `simplify_advanced()`
- Performance regression: <10% overhead on existing benchmarks

---

## Appendix: Transformation Interactions

### Beneficial Interactions

**T1.1 (Factoring) enables T4.2 (Cancellation):**
```
Input:  x*y + x*z / x
Step 1 (T1.1): (x*(y+z)) / x
Step 2 (T4.2): y + z
```

**T2.1 (Fraction Combining) enables T1.1 (Factoring):**
```
Input:  a*x/c + b*x/c
Step 1 (T2.1): (a*x + b*x)/c
Step 2 (T1.1): ((a+b)*x)/c
Step 3 (T4.2): (a+b)*x/c [if c is constant]
```

**T3.1 (Associativity) enables T1.4 (Like-Terms):**
```
Input:  (x*2) + (x*3)
Step 1 (T3.1): (2*x) + (3*x)
Step 2 (T1.4): 5*x
```

### Interference Prevention

**Why T1.1 before T2.2:**
- T2.2 (Distribution) can prevent T1.1 (Factoring)
- Example: `(x*y + x*z)/x` distributed `→ x*y/x + x*z/x` (loses factoring opportunity)
- Solution: Apply T1.1 first to factor numerator before considering distribution

**Why T3.1 before T1.1:**
- T1.1 requires constant coefficients to be consolidated
- Example: `(x*2)*3 + (x*5)*2` cannot factor until constants folded
- Solution: Apply T3.1 first to fold constants

---

## Document Control

**Version:** 1.0  
**Date:** 2025-11-25  
**Author:** Claude (Sprint 11 Prep Task 3)  
**Status:** Transformation Catalog (Pre-Implementation Reference)

**Related Documents:**
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` (architecture design)
- `docs/planning/EPIC_2/PROJECT_PLAN.md` (Sprint 11 specification)
- `src/ad/term_collection.py` (existing transformation utilities)
