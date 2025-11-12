# Sprint 6 Known Unknowns

**Created:** November 11, 2025  
**Status:** Active - Pre-Sprint 6  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 6 convexity detection, bug fixes, GAMSLib integration, and UX improvements

---

## Overview

This document identifies all assumptions and unknowns for Sprint 6 features **before** implementation begins. This proactive approach continues the highly successful methodology from Sprint 4 and Sprint 5 that prevented late-stage surprises.

**Sprint 6 Scope:**
1. Convexity Heuristics - Pattern-based detection of nonconvex constructs
2. Critical Bug Fixes - Maximize sense bounds, nested min/max flattening
3. GAMSLib Integration - Model ingestion pipeline and conversion tracking
4. UX Improvements - Enhanced error messages with context and documentation links

**Reference:** See `docs/planning/EPIC_2/PROJECT_PLAN.md` lines 7-38 for complete Sprint 6 deliverables and acceptance criteria.

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results in Sprint 4 (23 unknowns, zero late surprises) and Sprint 5 (22 unknowns resolved on schedule). Continue this approach for Sprint 6.

---

## How to Use This Document

### Before Sprint 6 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE -> [x] COMPLETE or ❌ WRONG (with correction)

### During Sprint 6
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 22  
**By Priority:**
- Critical: 4 (unknowns that could derail sprint)
- High: 9 (unknowns requiring upfront research)
- Medium: 6 (unknowns that can be resolved during implementation)
- Low: 3 (nice-to-know, low impact)

**By Category:**
- Category 1 (Convexity Detection): 7 unknowns
- Category 2 (Bug Fixes): 5 unknowns
- Category 3 (GAMSLib Integration): 6 unknowns
- Category 4 (UX Improvements): 4 unknowns

**Estimated Research Time:** 18-24 hours (spread across prep phase)

---

## Table of Contents

1. [Category 1: Convexity Detection](#category-1-convexity-detection)
2. [Category 2: Bug Fixes](#category-2-bug-fixes)
3. [Category 3: GAMSLib Integration](#category-3-gamslib-integration)
4. [Category 4: UX Improvements](#category-4-ux-improvements)

---

# Category 1: Convexity Detection

## Unknown 1.1: Can pattern matching reliably detect nonlinear equality nonconvexity?

### Priority
**Critical** - Core convexity heuristic

### Assumption
Pattern matching for nonlinear equality constraints (e.g., `x^2 + y^2 = 4`) can reliably detect nonconvex cases without full AST convexity analysis.

### Research Questions
1. Does the pattern "nonlinear expression = constant" catch all circle/sphere constraints?
2. What about `x*y = 1` (hyperbola) - is multiplication pattern sufficient?
3. Can we distinguish `x^2 = 4` (two feasible points, nonconvex) from `x^2 <= 4` (convex)?
4. What about `exp(x) = 5` - is exponential in equality always nonconvex?
5. Do we need to check both sides of equality or just detect nonlinearity?

### How to Verify

**Test Case 1: Quadratic equality (circle)**
```gams
Variables x, y;
Equations eq1;
eq1.. x**2 + y**2 =e= 4;
```
Expected: Heuristic warns "nonlinear equality may be nonconvex"

**Test Case 2: Bilinear equality (hyperbola)**
```gams
Variables x, y;
Equations eq1;
eq1.. x * y =e= 1;
```
Expected: Heuristic warns "bilinear term in equality may be nonconvex"

**Test Case 3: Quadratic inequality (convex)**
```gams
Variables x, y;
Equations ineq1;
ineq1.. x**2 + y**2 =l= 4;
```
Expected: No warning (inequality can be convex)

**Test Case 4: Exponential equality**
```gams
Variables x;
Equations eq1;
eq1.. exp(x) =e= 5;
```
Expected: Warning or no warning? (exp is convex, but equality is not)

**Test Case 5: Linear equality (always convex)**
```gams
Variables x, y;
Equations eq1;
eq1.. 2*x + 3*y =e= 10;
```
Expected: No warning

### Risk if Wrong
- False positives: Users get warnings on actually convex models (annoying but safe)
- False negatives: Users convert nonconvex models without warning (dangerous - wrong solutions)
- May need more sophisticated AST analysis earlier than planned

### Estimated Research Time
3-4 hours (implement pattern detection, test on diverse equality types)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Does trigonometric function detection need domain analysis?

### Priority
**High** - Convexity heuristic accuracy

### Assumption
Detecting `sin()`, `cos()`, `tan()` in expressions is sufficient to warn about nonconvexity without checking if domains are restricted to convex regions.

### Research Questions
1. Is `sin(x)` always nonconvex, or only over certain domains (e.g., x ∈ [-π, π])?
2. Can we detect domain restrictions from bounds: `x.lo = 0; x.up = pi/2;` makes `sin(x)` concave?
3. Should we warn on all trig functions or only in specific contexts (objective vs constraint)?
4. What about `arcsin()`, `arccos()`, `arctan()` - different convexity properties?
5. Does `cos(x)**2 + sin(x)**2 = 1` identity need special handling?

### How to Verify

**Test Case 1: sin() with unrestricted domain**
```gams
Variables x;
x.lo = -10; x.up = 10;
Equations obj;
obj.. z =e= sin(x);
```
Expected: Warning (sin is nonconvex over this domain)

**Test Case 2: sin() with restricted domain (convex region)**
```gams
Variables x;
x.lo = -pi/2; x.up = pi/2;
Equations obj;
obj.. z =e= sin(x);
```
Expected: Should we warn? (sin is neither convex nor concave even here, but problem may still be solvable)

**Test Case 3: Trig identity**
```gams
Variables x;
Equations eq1;
eq1.. cos(x)**2 + sin(x)**2 =e= 1;
```
Expected: Should we recognize this identity and suppress warning?

### Risk if Wrong
- Too many false positives if we warn on all trig regardless of domain
- False negatives if we don't warn on trig that's actually problematic
- Users may ignore warnings if they're too frequent

### Estimated Research Time
2-3 hours (research trig convexity, test domain-restricted cases)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: How to handle bilinear terms in different constraint types?

### Priority
**High** - Common nonconvex pattern

### Assumption
Bilinear terms (`x*y` where both are variables) are always nonconvex and should trigger warnings.

### Research Questions
1. Is `x*y` in objective always nonconvex, or can context matter?
2. What about `x*y <= c` - is this ever convex? (No - bilinear inequality is nonconvex)
3. Should we detect higher-order products: `x*y*z`?
4. What about `x**2 * y` - is this bilinear or a different pattern?
5. Can we distinguish `x*y` from `x*param` where param is a scalar parameter (not nonconvex)?

### How to Verify

**Test Case 1: Bilinear in objective**
```gams
Variables x, y;
x.lo = 0; y.lo = 0;
Equations obj;
obj.. z =e= x * y;
```
Expected: Warning "bilinear term may cause nonconvexity"

**Test Case 2: Bilinear in constraint**
```gams
Variables x, y;
Equations eq1;
eq1.. x * y =l= 10;
```
Expected: Warning

**Test Case 3: Variable times parameter (not bilinear)**
```gams
Variables x;
Parameter a / 5 /;
Equations obj;
obj.. z =e= x * a;
```
Expected: No warning (linear in x)

**Test Case 4: Multilinear term**
```gams
Variables x, y, z;
Equations obj;
obj.. w =e= x * y * z;
```
Expected: Warning (multilinear is nonconvex)

**Test Case 5: Mixed power-bilinear**
```gams
Variables x, y;
Equations obj;
obj.. z =e= x**2 * y;
```
Expected: Warning (nonconvex)

### Risk if Wrong
- Missing bilinear terms is dangerous (false negatives)
- Warning on parameter products is annoying (false positives)
- Need to distinguish variables from parameters in AST

### Estimated Research Time
2-3 hours (implement variable detection, test parameter vs variable cases)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.4: Should quotient detection check for division by variables?

### Priority
**Medium** - Edge case handling

### Assumption
Quotients with variables in the denominator (`x/y` where y is a variable) should trigger nonconvexity warnings.

### Research Questions
1. Is `1/x` always nonconvex, or convex over positive domain (x > 0)?
2. What about `x/y` - is this always nonconvex?
3. Should we check for zero bounds: `y.lo = 0` suggests potential division by zero?
4. Is `x/(constant)` safe (linear, no warning needed)?
5. What about `(x+y)/(z+1)` - quotient of expressions?

### How to Verify

**Test Case 1: Reciprocal (1/x)**
```gams
Variables x;
x.lo = 0.01; x.up = 10;
Equations obj;
obj.. z =e= 1 / x;
```
Expected: Warning or not? (Reciprocal is convex over x > 0, but 1/x objective is still tricky)

**Test Case 2: Quotient of variables**
```gams
Variables x, y;
y.lo = 0.1;
Equations obj;
obj.. z =e= x / y;
```
Expected: Warning (quotient is nonconvex)

**Test Case 3: Variable divided by constant**
```gams
Variables x;
Equations obj;
obj.. z =e= x / 5;
```
Expected: No warning (linear)

**Test Case 4: Quotient of expressions**
```gams
Variables x, y, z;
z.lo = 1;
Equations eq1;
eq1.. w =e= (x + y) / z;
```
Expected: Warning (nonconvex)

### Risk if Wrong
- False negatives could miss dangerous quotients
- False positives on safe reciprocals may be annoying but acceptable
- Need to handle bounds checking carefully

### Estimated Research Time
2 hours (implement quotient detection, test denominator patterns)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.5: How to detect odd powers that break convexity?

### Priority
**Medium** - Completeness of heuristics

### Assumption
Odd powers like `x**3` are nonconvex and should trigger warnings.

### Research Questions
1. Is `x**3` always nonconvex, or convex/concave over restricted domains?
2. What about `x**5`, `x**7` - same pattern?
3. Should we check if power is odd: `x**(2n+1)` for integer n?
4. What about negative odd powers: `x**(-3)` = `1/(x**3)`?
5. Is `abs(x)**3` different from `x**3`?

### How to Verify

**Test Case 1: Cubic term**
```gams
Variables x;
Equations obj;
obj.. z =e= x**3;
```
Expected: Warning "odd power may be nonconvex"

**Test Case 2: Fifth power**
```gams
Variables x;
Equations obj;
obj.. z =e= x**5;
```
Expected: Warning

**Test Case 3: Even power (convex)**
```gams
Variables x;
Equations obj;
obj.. z =e= x**4;
```
Expected: No warning (even powers are convex for positive x)

**Test Case 4: Negative odd power**
```gams
Variables x;
x.lo = 0.1;
Equations obj;
obj.. z =e= x**(-3);
```
Expected: Warning

### Risk if Wrong
- Missing odd powers is a gap in heuristics
- False positives on even powers would be wrong
- Need to distinguish power parity correctly

### Estimated Research Time
1-2 hours (implement power detection, test odd/even cases)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.6: Does `--strict-convexity` flag need different exit codes?

### Priority
**Low** - CLI interface detail

### Assumption
`--strict-convexity` should exit with nonzero code when convexity warnings are detected, allowing CI/CD integration.

### Research Questions
1. What exit code should be used: 1 (general error) or custom code like 2 (convexity warning)?
2. Should there be multiple codes: 2 for warnings, 3 for definite nonconvexity?
3. How to document exit codes for users?
4. Should `--strict-convexity` suppress MCP generation or still generate with error?
5. Can users combine with other flags: `--strict-convexity --force`?

### How to Verify

**Test Case 1: Strict mode with convexity warning**
```bash
nlp2mcp model_with_bilinear.gms --strict-convexity
echo $?  # Should be nonzero
```

**Test Case 2: Normal mode (warnings only)**
```bash
nlp2mcp model_with_bilinear.gms
echo $?  # Should be 0 (success with warnings)
```

**Test Case 3: Strict mode with convex model**
```bash
nlp2mcp convex_model.gms --strict-convexity
echo $?  # Should be 0
```

### Risk if Wrong
- Users can't integrate with CI/CD if exit codes are wrong
- Confusing if exit codes not documented
- Low impact - can fix in patch release

### Estimated Research Time
1 hour (implement flag, test exit codes, document)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.7: Should convexity warnings cite specific equations by line number?

### Priority
**Medium** - UX quality

### Assumption
Convexity warnings should reference specific equation names and line numbers to help users locate problematic constructs.

### Research Questions
1. Can we get line numbers from parser metadata?
2. Should warnings cite equation name: "Warning in equation 'eq1' (line 42)"?
3. What if multiple equations have same pattern - list all or summarize?
4. Should we include expression snippet in warning message?
5. How to format multi-line warnings for readability?

### How to Verify

**Test Case 1: Single nonconvex equation**
```gams
Variables x, y;
Equations eq1;
eq1.. x * y =e= 10;  # Line 42
```
Expected: "Warning: bilinear term in equation 'eq1' (line 42) may cause nonconvexity"

**Test Case 2: Multiple similar warnings**
```gams
Equations eq1, eq2, eq3;
eq1.. x * y =e= 10;
eq2.. x * z =e= 20;
eq3.. y * z =e= 30;
```
Expected: List all three or summarize "3 equations with bilinear terms: eq1, eq2, eq3"?

**Test Case 3: No line number available**
```gams
# What if parser doesn't provide line info?
```
Expected: Still show equation name without line number

### Risk if Wrong
- Poor UX if warnings don't help users locate issues
- Too verbose if listing all warnings individually
- Need parser to track line metadata (may not be available yet)

### Estimated Research Time
2 hours (check parser metadata, implement citation, format messages)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: Bug Fixes

## Unknown 2.1: Do maximize-sense bound multipliers need sign flips in stationarity?

### Priority
**Critical** - Correctness of KKT conditions

### Assumption
When maximizing, the signs of lower/upper bound multipliers in stationarity equations must be flipped compared to minimization.

### Research Questions
1. For minimize: `∂f/∂x - π^L + π^U = 0`. For maximize: `∂(-f)/∂x - π^L + π^U = 0` or `-∂f/∂x - π^L + π^U = 0`?
2. Do we flip signs of ALL multipliers or just bound multipliers?
3. Are equality constraint multipliers affected by objective sense?
4. What about inequality constraint multipliers?
5. Does PATH solver handle maximize MCPs differently?

### How to Verify

**Test Case 1: Maximize with upper bound**
```gams
Variables x;
x.up = 10;
Equations obj;
obj.. z =e= x;  # Maximize x subject to x <= 10
Solve model using NLP maximizing z;
```
Expected: At optimum, x* = 10, multiplier π^U should be negative (for minimize) or positive (for maximize)?

**Test Case 2: Manual KKT derivation**
```
Maximize f(x) = x
Subject to: x <= 10

Lagrangian: L = f(x) - λ(x - 10)
KKT stationarity: ∂L/∂x = f'(x) - λ = 0
So: 1 - λ = 0 => λ = 1 (positive)

For PATH MCP:
maximize f(x) = -minimize (-f(x))
∂(-f)/∂x + π^U = 0
-1 + π^U = 0 => π^U = 1 (positive)
```

**Test Case 3: Compare with existing minimize tests**
```python
# Run existing minimize test suite
# Run new maximize test suite  
# Verify multiplier signs are correct in both cases
```

### Risk if Wrong
- KKT conditions will be mathematically incorrect
- PATH solver may not converge or give wrong solutions
- All maximize tests will fail
- This is a critical correctness bug

### Estimated Research Time
3-4 hours (derive KKT manually, implement fix, test extensively)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Does nested min/max flattening preserve semantics in all cases?

### Priority
**Critical** - Correctness of reformulation

### Assumption
Flattening `min(min(x,y),z)` to `min(x,y,z)` is always semantically equivalent and preserves optimal solutions.

### Research Questions
1. Is `min(min(x,y),z)` always equal to `min(x,y,z)` mathematically?
2. What about `max(max(x,y),z)` to `max(x,y,z)`?
3. Does flattening change differentiability properties at boundary points?
4. Will PATH solver give same solution for flattened vs nested forms?
5. Are there numerical stability differences?

### How to Verify

**Test Case 1: Nested min flattening**
```gams
# Before flattening
Variables x, y, z, aux1, obj;
Equations eq1, eq2;
eq1.. aux1 =e= min(x, y);
eq2.. obj =e= min(aux1, z);
```
```gams
# After flattening  
Variables x, y, z, obj;
Equations eq1;
eq1.. obj =e= min(x, y, z);
```
Expected: Both give same optimal solution

**Test Case 2: Nested max flattening**
```gams
# Before: max(max(x,y),z)
# After: max(x,y,z)
```
Expected: Equivalent solutions

**Test Case 3: Mixed nesting (should NOT flatten)**
```gams
# min(max(x,y),z) cannot flatten
```
Expected: Keep as is or use different reformulation

**Test Case 4: Three-level nesting**
```gams
# min(min(min(x,y),z),w) -> min(x,y,z,w)
```
Expected: Flattening works for arbitrary depth

### Risk if Wrong
- Wrong solutions if flattening changes semantics
- This would be a critical correctness bug
- Need to prove equivalence mathematically

### Estimated Research Time
3-4 hours (prove equivalence, implement algorithm, test all nesting patterns)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: How to detect nested min/max patterns in AST?

### Priority
**High** - Implementation feasibility

### Assumption
We can traverse the AST to detect nested min/max calls and identify flattening opportunities.

### Research Questions
1. How to recursively walk AST looking for min/max inside min/max?
2. Can we use existing IR structures or need new visitor pattern?
3. What if min/max is in subexpression: `x + min(y, min(z,w))`?
4. Should we flatten in-place or create new IR nodes?
5. How to preserve equation context and variable references?

### How to Verify

**Algorithm Design:**
```python
def detect_nested_minmax(expr: IRExpr) -> List[NestingPattern]:
    """
    Recursively find min/max calls that contain other min/max calls.
    
    Returns list of patterns:
    - SAME_TYPE_NESTING: min(min(...), ...) or max(max(...), ...)
    - MIXED_NESTING: min(max(...), ...) or max(min(...), ...)
    """
    if isinstance(expr, MinMaxCall):
        # Check if any arguments are also MinMaxCall
        nested = [arg for arg in expr.args if isinstance(arg, MinMaxCall)]
        if nested:
            return classify_nesting_pattern(expr, nested)
    
    # Recurse into children
    results = []
    for child in expr.children():
        results.extend(detect_nested_minmax(child))
    return results
```

**Test Cases:**
1. `min(min(x,y),z)` -> SAME_TYPE_NESTING
2. `max(max(x,y),z)` -> SAME_TYPE_NESTING
3. `min(max(x,y),z)` -> MIXED_NESTING (do not flatten)
4. `x + min(y, min(z,w))` -> Find nested min in subexpression

### Risk if Wrong
- May miss nested patterns
- May incorrectly flatten mixed nesting
- Algorithm must be robust to complex expressions

### Estimated Research Time
2-3 hours (implement detection, test on diverse expressions)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Will nested min/max flattening break existing tests?

### Priority
**High** - Regression risk

### Assumption
Flattening optimization is backward-compatible and won't break any currently passing tests.

### Research Questions
1. Do we have existing tests with nested min/max?
2. Will flattening change generated MCP structure in ways that break tests?
3. Are there tests that verify specific auxiliary variable names that will change?
4. Do golden file tests need updating with flattened output?
5. Will PATH solver convergence be affected?

### How to Verify

**Step 1: Run existing test suite as baseline**
```bash
pytest tests/ -v > baseline.txt
```

**Step 2: Implement flattening with feature flag**
```python
# Add config flag: enable_minmax_flattening = False (default)
# Run tests again with flag disabled
# Should match baseline
```

**Step 3: Enable flattening and compare**
```python
# Set enable_minmax_flattening = True
pytest tests/ -v > with_flattening.txt
# Compare: diff baseline.txt with_flattening.txt
```

**Step 4: Identify test failures**
```python
# For each failing test:
# - Is it golden file mismatch? Update golden file
# - Is it wrong solution? Fix flattening algorithm
# - Is it PATH convergence? Debug
```

### Risk if Wrong
- Flattening could introduce regressions
- May need to update many golden files
- Could break production models if deployed

### Estimated Research Time
2-3 hours (run tests, analyze failures, update golden files)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Should nested min/max flattening be always-on or configurable?

### Priority
**Low** - Design decision

### Assumption
Flattening should be always enabled (not a CLI flag) since it's a pure optimization.

### Research Questions
1. Are there cases where users would want nested form preserved?
2. Should we add `--no-flatten-minmax` flag for debugging?
3. Does flattening affect diagnostic output or debugging?
4. Should flattening be documented as an optimization pass?
5. Can we make it a default with opt-out?

### How to Verify

**Consider use cases:**
- **Always on:** Simpler for users, fewer decisions, smaller MCPs
- **Configurable:** More flexibility, easier debugging, safer rollout
- **Default on with opt-out:** Balance of both

**Recommendation:**
1. Implement as always-on initially
2. Add `--preserve-nesting` flag if users report issues
3. Document flattening in "Optimizations" section

### Risk if Wrong
- Low risk - can add flag later if needed
- More important to get correctness right first

### Estimated Research Time
1 hour (design decision, document)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: GAMSLib Integration

## Unknown 3.1: Can we download GAMSLib models without GAMS licensing?

### Priority
**Critical** - Blocks GAMSLib integration

### Assumption
GAMSLib models are publicly available and can be downloaded without a GAMS license.

### Research Questions
1. Where are GAMSLib models hosted? (GAMS website, GitHub, other?)
2. Do we need authentication or license to download?
3. Are models available in plain text `.gms` format?
4. Which subset of GAMSLib contains NLP models?
5. Are there licensing restrictions on redistribution or CI use?

### How to Verify

**Step 1: Research GAMSLib sources**
```bash
# Try to find public GAMSLib repository
# Check GAMS documentation for model library location
```

**Step 2: Test download without license**
```bash
# Try downloading a known GAMSLib NLP model
# e.g., from https://www.gams.com/latest/gamslib_ml/libhtml/
```

**Step 3: Check licensing terms**
```
# Read GAMSLib license/terms of use
# Verify we can:
# - Download models
# - Use in CI/CD
# - Track conversion results publicly
```

**Step 4: Create download script**
```bash
#!/bin/bash
# scripts/download_gamslib_nlp.sh
# Downloads target NLP models from GAMSLib
# Without requiring GAMS installation
```

### Risk if Wrong
- Cannot build GAMSLib integration without model access
- May need alternative public NLP benchmarks
- Sprint 6 may be blocked on this unknown

### Estimated Research Time
2-3 hours (research, test download, verify licensing)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: How many GAMSLib NLP models exist and which to target?

### Priority
**High** - Scope definition

### Assumption
There are 50-100 NLP models in GAMSLib, and we should target 10-20 diverse models initially.

### Research Questions
1. How many total NLP models in GAMSLib?
2. What size distribution: small (<100 vars), medium (100-1000), large (>1000)?
3. Which models use features we don't support yet?
4. Are there categories: convex, nonconvex, quadratic, general NLP?
5. Should we start with smallest/simplest models or representative sample?

### How to Verify

**Step 1: Survey GAMSLib NLP catalog**
```bash
# List all models with type=NLP
# Count total number
# Note sizes (vars, equations)
```

**Step 2: Categorize by complexity**
```
Small: < 50 vars, < 100 eqs (quickest wins)
Medium: 50-500 vars (main targets)  
Large: > 500 vars (stretch goals)
```

**Step 3: Select initial target set**
```
Criteria:
- Diverse problem types
- Mix of convex and potentially nonconvex
- Different GAMS language features
- Range of sizes
Target: 10-15 models for Sprint 6
```

**Step 4: Document selection in `CONVERSION_STATUS.md`**
```markdown
# Target GAMSLib Models (Sprint 6)

| Model | Type | Vars | Eqs | Features | Priority |
|-------|------|------|-----|----------|----------|
| model1| NLP  | 10   | 10  | Basic    | High     |
...
```

### Risk if Wrong
- Targeting too many models spreads effort thin
- Targeting too few doesn't show scalability
- Wrong selection may not reveal parser gaps

### Estimated Research Time
2 hours (survey catalog, categorize, select targets)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: What parse error patterns will GAMSLib models reveal?

### Priority
**High** - Determines Sprint 7 work

### Assumption
GAMSLib models will reveal common GAMS syntax we don't support yet (e.g., `.l`/`.m` attributes, dollar conditions, indexed operations).

### Research Questions
1. What are the most common parse failures across target models?
2. Can we bucket errors: syntax, unsupported features, normalization, other?
3. Which features would unlock the most models if implemented?
4. Are there quick wins vs major parser additions?
5. How to track error patterns over time (dashboard)?

### How to Verify

**Step 1: Run ingestion on target models**
```bash
for model in target_models/*.gms; do
    nlp2mcp $model 2>&1 | tee logs/$(basename $model).log
done
```

**Step 2: Parse error logs**
```python
def categorize_errors(log_files: List[Path]) -> Dict[str, List[str]]:
    """
    Extract and categorize parse errors.
    
    Categories:
    - ATTRIBUTE_NOT_SUPPORTED: .l, .m, .lo, .up in expressions
    - DOLLAR_CONDITION: $if, $set, etc.
    - INDEXED_OPERATION: sum(), prod(), etc.
    - SYNTAX_ERROR: Unrecognized tokens
    - OTHER: Uncategorized
    """
    buckets = defaultdict(list)
    for log_file in log_files:
        errors = extract_errors(log_file)
        for error in errors:
            category = classify_error(error)
            buckets[category].append(error)
    return buckets
```

**Step 3: Create error frequency report**
```markdown
# Parse Error Analysis (Sprint 6)

## Top Error Categories
1. ATTRIBUTE_NOT_SUPPORTED: 45 occurrences across 8 models
   - Blocker for: model1, model5, model7
2. DOLLAR_CONDITION: 20 occurrences across 4 models  
3. INDEXED_OPERATION: 15 occurrences across 6 models
...
```

**Step 4: Prioritize for Sprint 7**
```markdown
## Recommended Sprint 7 Parser Work
1. Implement .l/.m attribute support (unlocks 8 models)
2. Add basic dollar condition handling (unlocks 4 models)
3. Indexed operations (unlocks 6 models)
```

### Risk if Wrong
- May not prioritize right features for Sprint 7
- Could miss systematic issues in our parser
- Dashboard may not be informative

### Estimated Research Time
3-4 hours (run ingestion, analyze errors, prioritize features)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: Should conversion dashboard be static HTML or dynamic?

### Priority
**Medium** - Implementation approach

### Assumption
A static HTML dashboard (generated from Markdown) is sufficient for Sprint 6, with dynamic dashboard deferred to later sprints.

### Research Questions
1. Can we generate dashboard from `CONVERSION_STATUS.md` using simple script?
2. Should we use templating (Jinja2) or plain HTML generation?
3. Do we need charts/graphs or is a table sufficient?
4. How to auto-update dashboard in CI/CD?
5. Should dashboard be published to GitHub Pages?

### How to Verify

**Option A: Static Markdown (simplest)**
```markdown
# CONVERSION_STATUS.md
| Model | Parse | Convert | Solve | Error |
|-------|-------|---------|-------|-------|
| model1| ✅    | ✅      | ⏳    |       |
| model2| ❌    | -       | -     | Syntax|
```
View directly in GitHub

**Option B: Static HTML from Markdown**
```bash
# scripts/generate_dashboard.sh
pandoc CONVERSION_STATUS.md -o dashboard.html --standalone
```

**Option C: Dynamic dashboard with charts**
```python
# scripts/generate_dashboard.py
# Read CONVERSION_STATUS.md
# Generate HTML with Chart.js for parse/convert/solve rates
# Update on each CI run
```

**Recommendation:**
- Sprint 6: Use Option A (pure Markdown, simplest)
- Sprint 7+: Add Option B or C if needed

### Risk if Wrong
- Over-engineering dashboard wastes time
- Under-delivering dashboard may not be informative enough
- Medium risk - can iterate

### Estimated Research Time
1-2 hours (choose approach, implement, test)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.5: What KPIs should be tracked: parse%, convert%, solve%?

### Priority
**Medium** - Success metrics

### Assumption
We should track three KPIs: parse success rate, conversion success rate, and PATH solve success rate.

### Research Questions
1. Parse success = models that parse without errors / total models?
2. Convert success = models that generate MCP / models that parse successfully?
3. Solve success = models where PATH finds solution / models that convert?
4. Should we track partial success (e.g., parses but with warnings)?
5. What are realistic Sprint 6 targets: ≥10 models ingested, ≥10% parse?

### How to Verify

**Define KPI calculations:**
```python
def compute_kpis(results: List[ModelResult]) -> KPIs:
    total = len(results)
    parsed = sum(1 for r in results if r.parse_success)
    converted = sum(1 for r in results if r.convert_success)
    solved = sum(1 for r in results if r.solve_success)
    
    return KPIs(
        parse_rate = parsed / total * 100,
        convert_rate = converted / parsed * 100 if parsed > 0 else 0,
        solve_rate = solved / converted * 100 if converted > 0 else 0,
        total_models = total,
        parsed_models = parsed,
        converted_models = converted,
        solved_models = solved,
    )
```

**Sprint 6 Targets:**
```
Baseline (Sprint 6 end):
- Total models: ≥ 10
- Parse rate: ≥ 10% (≥1 model parses)
- Convert rate: ≥ 50% (of parsed models)
- Solve rate: Not required (PATH testing may not be in CI)
```

**Future Targets:**
```
Sprint 7: Parse ≥ 20%, Convert ≥ 50%
Sprint 8: Parse ≥ 50%, Convert ≥ 30%
```

### Risk if Wrong
- Wrong KPIs measure wrong things
- Targets too aggressive cause false failure
- Targets too loose don't drive progress

### Estimated Research Time
1-2 hours (define KPIs, set targets, implement tracking)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.6: Should ingestion run nightly or on-demand?

### Priority
**Low** - Process decision

### Assumption
Nightly automated ingestion is better than on-demand for tracking progress over time.

### Research Questions
1. Should ingestion be a GitHub Action running nightly?
2. Or should it be manual: `make ingest-gamslib`?
3. How long does ingestion take (affects CI time)?
4. Should results be committed to repo or artifacts?
5. What if ingestion fails - how to alert?

### How to Verify

**Option A: Nightly GitHub Action**
```yaml
# .github/workflows/gamslib-ingest.yml
name: GAMSLib Ingestion
on:
  schedule:
    - cron: '0 2 * * *'  # 2am daily
jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - run: make ingest-gamslib
      - run: git commit -am "Update GAMSLib results"
      - run: git push
```

**Option B: Manual invocation**
```bash
# Run when needed
make ingest-gamslib
# Review results
git add docs/planning/EPIC_2/CONVERSION_STATUS.md
git commit -m "Update GAMSLib conversion status"
```

**Recommendation:**
- Sprint 6: Start with Option B (manual, simpler)
- Sprint 7+: Add Option A (automated) once stable

### Risk if Wrong
- Low risk - can change process easily
- Manual is safer initially (no surprise CI failures)

### Estimated Research Time
1 hour (set up process, document)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: UX Improvements

## Unknown 4.1: Can parser provide line and column numbers for errors?

### Priority
**High** - Error message quality

### Assumption
The GAMS parser can be enhanced to track line/column positions and include them in error messages.

### Research Questions
1. Does current parser infrastructure store line/column metadata?
2. How to propagate position info from lexer to parser to error handler?
3. Should we use existing Python parser libraries that track positions?
4. What about errors in normalized IR (after parsing) - can we still cite lines?
5. How to format error messages with position info?

### How to Verify

**Check current parser implementation:**
```python
# In src/parser/*.py
# Look for position tracking in lexer/parser
# Example: Does AST node have .line and .col attributes?
```

**Test error message improvements:**
```gams
Variables x, y;
Equations badEq;
badEq.. x * y * z =e= 10;  # Error: z not declared (line 42, col 15)
```

Expected error message:
```
Error: Undefined variable 'z' in equation 'badEq'
  Line 42, Column 15: x * y * z =e= 10
                             ^
  Suggestion: Declare 'z' in Variables section
  See: https://docs.nlp2mcp.dev/errors/undefined-variable
```

**Implementation approach:**
```python
class ParseError(Exception):
    def __init__(self, message: str, line: int, col: int, 
                 suggestion: str = None, doc_link: str = None):
        self.message = message
        self.line = line  
        self.col = col
        self.suggestion = suggestion
        self.doc_link = doc_link
    
    def format(self) -> str:
        """Format error with position and context."""
        # Build formatted message with caret pointing to error
        ...
```

### Risk if Wrong
- Error messages stay cryptic (bad UX)
- Users struggle to locate issues in large files
- Parser changes may be complex

### Estimated Research Time
3-4 hours (analyze parser, implement position tracking, test formatting)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: What documentation links should be embedded in error messages?

### Priority
**Medium** - Documentation planning

### Assumption
Error messages should link to relevant documentation sections to help users self-serve fixes.

### Research Questions
1. What documentation structure: single page or per-error pages?
2. Should links be to web docs or local docs?
3. What error categories need documentation: syntax, convexity, solver, other?
4. How to maintain doc links in code without hardcoding URLs?
5. Should we use short links (docs.nlp2mcp.dev/errors/E001)?

### How to Verify

**Design error documentation structure:**
```
docs/
  errors/
    index.md          # Error catalog
    syntax-errors.md
    convexity-warnings.md
    solver-errors.md
    E001-undefined-variable.md
    E002-nonlinear-equality.md
    ...
```

**Example error message with link:**
```
Error E001: Undefined variable 'z' in equation 'badEq'
  Line 42: x * y * z =e= 10
  
  This error occurs when a variable is used but not declared.
  
  Fix: Add 'z' to the Variables section.
  Docs: https://docs.nlp2mcp.dev/errors/E001
```

**Link management approach:**
```python
# src/errors.py
ERROR_DOCS = {
    "E001": "https://docs.nlp2mcp.dev/errors/E001",
    "E002": "https://docs.nlp2mcp.dev/errors/E002",
    # ... or use base URL and construct
}

def format_error(code: str, message: str, **kwargs) -> str:
    doc_link = ERROR_DOCS.get(code, "https://docs.nlp2mcp.dev/errors/")
    return f"{message}\n\nDocs: {doc_link}"
```

### Risk if Wrong
- Documentation overhead may be high
- Links may break if docs reorganized
- Medium risk - can start simple and expand

### Estimated Research Time
2 hours (design structure, implement linking, document)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Should convexity warnings be suppressible per-equation?

### Priority
**Low** - Advanced feature

### Assumption
Users should be able to suppress convexity warnings on specific equations if they understand the implications.

### Research Questions
1. How to specify suppression: comments in GAMS code or config file?
2. Should we use `# nlp2mcp-ignore-convexity` pragma?
3. Or use config file: `suppress_warnings: {eq1: [NONLINEAR_EQUALITY]}`?
4. Should suppression only work in non-strict mode?
5. How to document suppression (don't overuse)?

### How to Verify

**Option A: Inline pragma**
```gams
Equations eq1;
# nlp2mcp-ignore-convexity
eq1.. x * y =e= 10;  # No warning emitted
```

**Option B: Config file**
```yaml
# nlp2mcp.yml
suppress_warnings:
  eq1: [BILINEAR_TERM]
  eq2: [NONLINEAR_EQUALITY]
```

**Implementation:**
```python
def should_warn(equation_name: str, warning_type: str) -> bool:
    """Check if warning should be emitted for this equation."""
    suppressed = load_suppressions()  # From config or pragmas
    return (equation_name, warning_type) not in suppressed
```

**Recommendation:**
- Defer to Sprint 7+ (not critical for Sprint 6)
- Start without suppression, add if users request

### Risk if Wrong
- Low risk - nice-to-have feature
- Could lead to users suppressing important warnings

### Estimated Research Time
1-2 hours (if implemented)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: How to display sprint demo checklist progress?

### Priority
**Low** - Process tracking

### Assumption
Sprint demo checklist should be tracked in a dedicated Markdown file with checkboxes for each UX increment.

### Research Questions
1. Where to store checklist: `SPRINT_6_DEMO_CHECKLIST.md`?
2. What format: checkboxes, table, or status badges?
3. Should checklist be auto-generated from tasks?
4. How to integrate with daily standup?
5. Should we track completion percentage?

### How to Verify

**Example checklist structure:**
```markdown
# Sprint 6 Demo Checklist

## Convexity Detection
- [x] Bilinear term detection
- [x] Nonlinear equality detection
- [ ] Trig function detection (in progress)
- [ ] CLI flags (--strict-convexity)

## Bug Fixes
- [x] Maximize multiplier fix
- [ ] Nested min/max flattening

## GAMSLib Integration  
- [x] Download script
- [ ] Ingestion pipeline
- [ ] Conversion dashboard

## UX Improvements
- [ ] Error messages with line numbers
- [ ] Documentation links
```

**Progress tracking:**
```
Total: 12 items
Completed: 4 (33%)
In Progress: 2 (17%)
Remaining: 6 (50%)
```

### Risk if Wrong
- Low risk - internal process tool
- Helps with demo preparation and transparency

### Estimated Research Time
1 hour (create checklist template, document process)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## End of Document

**Next Steps:**
1. Review and prioritize Critical and High priority unknowns
2. Schedule research time for prep phase (18-24 hours estimated)
3. Create test cases for verification
4. Update this document with findings before Sprint 6 Day 1
5. Use as living document during sprint - add new unknowns as discovered

**Success Criteria:**
- All Critical unknowns resolved before Day 1
- All High unknowns resolved before their implementation day
- Medium unknowns resolved during implementation  
- Low unknowns can be deferred or resolved opportunistically

**Document History:**
- November 11, 2025: Initial creation (pre-Sprint 6)
