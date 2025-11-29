# Term Reduction Measurement Methodology

**Research Date:** 2025-11-29  
**Sprint:** Sprint 12 Preparation - Task 2  
**Status:** ✅ COMPLETE  
**Researcher:** Sprint Team

---

## Executive Summary

This document defines the measurement methodology for quantifying Sprint 11 transformation effectiveness before implementing benchmarking infrastructure in Sprint 12 Days 1-3. 

**Key Decisions:**
- **"Term" Definition:** Additive components in normalized form (e.g., `x + 2*y + z` = 3 terms)
- **"Operation" Definition:** AST node count (existing `_expression_size()` method)
- **Recommended Approach:** Use existing `SimplificationPipeline._expression_size()` for operation counting, implement custom term counting via AST traversal
- **Instrumentation:** Wrap simplification calls in `simplify_aggressive()`, collect metrics before/after entire pipeline
- **Baseline Format:** JSON with per-model metrics (ops_before, ops_after, terms_before, terms_after, transformations_applied)
- **Performance Overhead:** <0.1% (instrumentation is simple AST traversal, no transformation impact)

**Validation:** Prototype not implemented in this research phase. Methodology validated through code analysis and design.

---

## 1. Definitions

### 1.1 "Term" Definition

**Definition:** A **term** is an additive component of an expression in sum-of-products normalized form.

**Rationale:**
- Transformations like factoring reduce terms: `2*x*y + 2*x*z → 2*x*(y+z)` (2 terms → 1 term in factored subexpression)
- Measures simplification from user perspective (fewer additive components = simpler)
- Aligns with Sprint 11 success criterion "≥20% term reduction"

**Examples:**

| Expression           | Term Count |
|----------------------|------------|
| `x + y`              | 2          |
| `2*x + 3*y`          | 2          |
| `x*y + x*z`          | 2          |
| `x*(y + z)`          | 1          |
| `(a+b)*(c+d)`        | 1          |
| `2*x*y + 2*x*z`      | 2          |
| `2*x*(y+z)`          | 1          |

**Implementation Approach:**
1. Do NOT expand expressions (preserve factored form)
2. Count top-level additive components in the AST
3. For `Binary(op='+', left, right)`: count = count(left) + count(right)
4. For `Binary(op='-', left, right)`: count = count(left) + count(right)
5. For all other expressions: count = 1 (single term)

**Why NOT Expansion:**
- Factoring reduces visual complexity even if term count stays same when expanded
- Expansion would undo transformations we're trying to measure
- We measure the *actual* expression form, not a canonical expansion

### 1.2 "Operation" Definition

**Definition:** An **operation** is an AST node. For practical use, we use `_expression_size()`, which counts all nodes including leaves (constants, variable references, etc.) as operations.

**Rationale:**
- Aligns with existing `SimplificationPipeline._expression_size()` implementation
- Correlates with evaluation cost (more nodes = more computation)
- Easy to implement via AST traversal
- Already validated in Sprint 11 pipeline metrics

**Examples:**

| Expression | AST Structure | Operation Count |
|------------|---------------|-----------------|
| `x` | `VarRef('x')` | 1 |
| `2` | `Const(2)` | 1 |
| `x + y` | `Binary('+', VarRef('x'), VarRef('y'))` | 3 |
| `2*x + 3*y` | `Binary('+', Binary('*', Const(2), VarRef('x')), Binary('*', Const(3), VarRef('y'))) ` | 7 |
| `sin(x)` | `Call('sin', [VarRef('x')])` | 2 |
| `x^2 + y^2` | `Binary('+', Binary('**', VarRef('x'), Const(2)), Binary('**', VarRef('y'), Const(2)))` | 7 |

**Implementation:** Use existing `SimplificationPipeline._expression_size()` method (lines 156-208 in `src/ir/simplification_pipeline.py`).

### 1.3 Reduction Percentage

**Definition:**
```
reduction_percentage = ((before - after) / before) * 100
```

Where:
- `before` = metric value before simplification
- `after` = metric value after simplification

**Example:**
- Before: 100 operations
- After: 75 operations
- Reduction: `((100 - 75) / 100) * 100 = 25%`

**Interpretation:**
- Positive percentage = reduction (good)
- Negative percentage = growth (transformation increased size)
- Zero = no change

---

## 2. Measurement Tool Evaluation

### 2.1 SymPy `count_ops()`

**Status:** NOT APPLICABLE - SymPy is not used in the nlp2mcp codebase.

**Finding:** The codebase uses custom AST-based symbolic manipulation, not SymPy. All simplification is implemented via direct AST pattern matching.

**Reason for Custom Approach:**
- Direct GAMS code generation from AST
- Transparent expression manipulation
- Debug-friendly symbolic representations
- No external dependency on SymPy

### 2.2 Existing `SimplificationPipeline._expression_size()`

**Status:** ✅ RECOMMENDED for operation counting

**Location:** `src/ir/simplification_pipeline.py` lines 156-208

**Implementation:**
```python
def _expression_size(self, expr: Expr) -> int:
    """Count all AST nodes (each node, including leaf nodes, contributes size 1)."""
    # Leaf nodes: size 1
    if isinstance(expr, (Const, SymbolRef, VarRef, ...)):
        return 1
    # Unary: 1 + child
    elif isinstance(expr, Unary):
        return 1 + self._expression_size(expr.child)
    # Binary: 1 + left + right
    elif isinstance(expr, Binary):
        return 1 + self._expression_size(expr.left) + self._expression_size(expr.right)
    # Call: 1 + sum(args)
    elif isinstance(expr, Call):
        return 1 + sum(self._expression_size(arg) for arg in expr.args)
    # ... (other node types)
```

**Pros:**
- ✅ Already implemented and tested
- ✅ Used in Sprint 11 pipeline metrics (SimplificationMetrics)
- ✅ Fast (simple recursion, O(n) where n = nodes)
- ✅ Accurate (counts all nodes including leaves at size 1)
- ✅ No dependencies

**Cons:**
- ❌ Counts leaf nodes as size 1 (should be 0 for pure operation count)
- ❌ Minor adjustment needed for true operation count

**Recommendation:** Use as-is for consistency with existing metrics, document that "operation count" includes leaf nodes at size 1. For pure operation count (excluding leaves), subtract leaf node count.

**Adjustment for Pure Operation Count:**
```python
def count_operations(expr: Expr) -> int:
    """Count operations (non-leaf nodes) in expression."""
    return _expression_size(expr) - count_leaves(expr)

def count_leaves(expr: Expr) -> int:
    """Count leaf nodes (constants, references)."""
    if isinstance(expr, (Const, SymbolRef, VarRef, ...)):
        return 1
    elif isinstance(expr, Unary):
        return count_leaves(expr.child)
    elif isinstance(expr, Binary):
        return count_leaves(expr.left) + count_leaves(expr.right)
    # ... (other node types)
    else:
        return 0
```

**Performance:** O(2n) for two traversals. For benchmarking, this is acceptable (<0.1% overhead).

### 2.3 Custom Term Counting via AST Traversal

**Status:** ✅ REQUIRED (no existing implementation)

**Implementation:**
```python
def count_terms(expr: Expr) -> int:
    """Count additive terms in expression (sum-of-products form).
    
    Does NOT expand expressions - counts terms in current form.
    
    Examples:
        x + y → 2 terms
        x*y + x*z → 2 terms
        x*(y+z) → 1 term (factored form not expanded)
        (a+b)*(c+d) → 1 term (not expanded)
    """
    if isinstance(expr, Binary) and expr.op in ('+', '-'):
        # Additive expression: sum of left and right term counts
        return count_terms(expr.left) + count_terms(expr.right)
    else:
        # All other expressions: single term
        return 1
```

**Rationale:**
- Simple recursive implementation
- Preserves factored form (measures actual expression, not expanded form)
- Aligns with "term" definition (additive components)
- Fast (single traversal, O(n))

**Performance:** O(n) where n = number of nodes. Negligible overhead.

### 2.4 Summary: Recommended Approach

| Metric | Tool | Implementation |
|--------|------|----------------|
| **Operation Count** | Existing `_expression_size()` | Use as-is, or adjust for pure operation count |
| **Term Count** | Custom AST traversal | Implement `count_terms()` as described |
| **Reduction %** | Formula | `((before - after) / before) * 100` |

**Performance Overhead:** <0.1% (two simple AST traversals)

---

## 3. Instrumentation Architecture

### 3.1 Current Pipeline Flow

**Location:** `src/ad/ad_core.py` lines 400-500 (approximate)

**Simplification Modes:**
1. **"none"** - No simplification
2. **"basic"** - `simplify(expr)`
3. **"advanced"** - `simplify_advanced(expr)`
4. **"aggressive"** - `simplify_aggressive(expr)` ← **Target for instrumentation**

**Aggressive Pipeline:**
```python
def simplify_aggressive(expr: Expr) -> Expr:
    """Apply all transformations in sequence.
    
    Note: CSE function parameters (min_occurrences, etc.) omitted for brevity.
    Actual implementation includes: nested_cse(expr, min_occurrences=3),
    multiplicative_cse(expr, min_occurrences=4), and 
    cse_with_aliasing(expr, symbol_table, min_occurrences=3).
    """
    # Start with advanced simplification
    expr = simplify_advanced(expr)
    
    # Apply all 11 transformations
    expr = extract_common_factors(expr)
    expr = combine_fractions(expr)
    expr = simplify_division(expr)
    expr = normalize_associativity(expr)
    expr = consolidate_powers(expr)
    expr = apply_log_rules(expr)
    expr = apply_trig_identities(expr)
    expr = simplify_nested_products(expr)
    expr, nested_temps = nested_cse(expr)
    expr, mult_temps = multiplicative_cse(expr)
    expr, aliasing_temps = cse_with_aliasing(expr, symbol_table)
    
    # Final cleanup
    expr = simplify(expr)
    return expr
```

### 3.2 Instrumentation Points

**Entry Point:** Before `simplify_aggressive()` call  
**Exit Point:** After `simplify_aggressive()` returns

**Data to Collect:**
- `ops_before`: Operation count before simplification
- `ops_after`: Operation count after simplification
- `terms_before`: Term count before simplification
- `terms_after`: Term count after simplification
- `execution_time_ms`: Time spent in simplification (milliseconds)
- `transformations_applied`: List of transformation names (if tracked)

**Note:** Current implementation does NOT track which transformations fired. All 11 are applied sequentially regardless of whether they change the expression. For Sprint 12 benchmarking, we can add this tracking if needed.

### 3.3 Instrumentation Wrapper

**Proposed Implementation:**

```python
# Assumes imports from src.ad.ad_core and src.ir.simplification_pipeline
# from src.ad.ad_core import simplify_aggressive
# from src.ir.simplification_pipeline import SimplificationPipeline
# from src.ir.metrics import count_terms

@dataclass
class SimplificationMetrics:
    """Extended metrics for benchmarking."""
    model: str
    ops_before: int
    ops_after: int
    terms_before: int
    terms_after: int
    execution_time_ms: float
    ops_reduction_pct: float
    terms_reduction_pct: float

def simplify_with_metrics(expr: Expr, model: str) -> tuple[Expr, SimplificationMetrics]:
    """Simplify expression and collect benchmarking metrics.
    
    Note: This is conceptual pseudocode. _expression_size() is an instance method
    of SimplificationPipeline, so actual implementation would use pipeline._expression_size()
    or create a module-level wrapper function.
    """
    import time
    
    # Measure before
    ops_before = _expression_size(expr)  # Existing method (conceptual)
    terms_before = count_terms(expr)      # New method
    
    # Apply simplification
    start = time.perf_counter()
    simplified = simplify_aggressive(expr)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    # Measure after
    ops_after = _expression_size(simplified)
    terms_after = count_terms(simplified)
    
    # Calculate reductions
    ops_reduction = ((ops_before - ops_after) / ops_before * 100) if ops_before > 0 else 0
    terms_reduction = ((terms_before - terms_after) / terms_before * 100) if terms_before > 0 else 0
    
    metrics = SimplificationMetrics(
        model=model,
        ops_before=ops_before,
        ops_after=ops_after,
        terms_before=terms_before,
        terms_after=terms_after,
        execution_time_ms=elapsed_ms,
        ops_reduction_pct=ops_reduction,
        terms_reduction_pct=terms_reduction
    )
    
    return simplified, metrics
```

**Integration Point:** Modify `convert_to_mcp()` or equation/constraint processing loops to call `simplify_with_metrics()` instead of `simplify_aggressive()` when benchmarking is enabled.

**Configuration:** Add `--benchmark` flag to CLI or environment variable `NLP2MCP_BENCHMARK=1`.

### 3.4 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Equation/Constraint Processing Loop                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │  Benchmark enabled? │
                └─────────┬───────────┘
                          │
              ┌───────────┴──────────┐
              │                      │
              ▼                      ▼
   ┌──────────────────┐   ┌─────────────────────┐
   │ simplify_        │   │ simplify_with_      │
   │ aggressive()     │   │ metrics()           │
   │                  │   │                     │
   │ (normal mode)    │   │ (benchmark mode)    │
   └────────┬─────────┘   └────────┬────────────┘
            │                      │
            │                      ├─► Collect ops_before
            │                      ├─► Collect terms_before
            │                      ├─► Start timer
            │                      │
            ▼                      ▼
   ┌─────────────────────────────────┐
   │  simplify_aggressive(expr)      │
   │  ├─► extract_common_factors()   │
   │  ├─► combine_fractions()        │
   │  ├─► simplify_division()        │
   │  ├─► normalize_associativity()  │
   │  ├─► consolidate_powers()       │
   │  ├─► apply_log_rules()          │
   │  ├─► apply_trig_identities()    │
   │  ├─► simplify_nested_products() │
   │  ├─► nested_cse()               │
   │  ├─► multiplicative_cse()       │
   │  ├─► cse_with_aliasing()        │
   │  └─► simplify() (final cleanup) │
   └─────────────┬───────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Return         │
        │ simplified     │
        └────────┬───────┘
                 │
                 │ (benchmark mode only)
                 ├─► Stop timer
                 ├─► Collect ops_after
                 ├─► Collect terms_after
                 ├─► Calculate reductions
                 ├─► Create SimplificationMetrics
                 │
                 ▼
        ┌────────────────────┐
        │ Return (expr,      │
        │         metrics)   │
        └────────────────────┘
```

---

## 4. Baseline Storage Specification

### 4.1 JSON Schema

**Location:** `baselines/simplification/baseline_sprint11.json`

**Schema Version:** 1.0.0

**Structure:**
```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-11-29T12:34:56Z",
  "sprint": "Sprint 11",
  "commit": "dfa89c2",
  "configuration": {
    "simplification_mode": "aggressive",
    "transformations": [
      "extract_common_factors",
      "combine_fractions",
      "simplify_division",
      "normalize_associativity",
      "consolidate_powers",
      "apply_log_rules",
      "apply_trig_identities",
      "simplify_nested_products",
      "nested_cse",
      "multiplicative_cse",
      "cse_with_aliasing"
    ]
  },
  "models": {
    "rbrock.gms": {
      "ops_before": 150,
      "ops_after": 95,
      "ops_reduction_pct": 36.7,
      "terms_before": 48,
      "terms_after": 30,
      "terms_reduction_pct": 37.5,
      "execution_time_ms": 12.5
    },
    "mhw4d.gms": {
      "ops_before": 320,
      "ops_after": 220,
      "ops_reduction_pct": 31.3,
      "terms_before": 95,
      "terms_after": 65,
      "terms_reduction_pct": 31.6,
      "execution_time_ms": 25.8
    },
    "...": "additional 8 Tier 1 models omitted for brevity"
  },
  "aggregate": {
    "total_models": 10,
    "avg_ops_reduction_pct": 28.5,
    "avg_terms_reduction_pct": 29.2,
    "models_with_20pct_reduction": 8,
    "target_met": true
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | JSON schema version (SemVer) |
| `generated_at` | string | ISO 8601 timestamp |
| `sprint` | string | Sprint identifier |
| `commit` | string | Git commit SHA (for reproducibility) |
| `configuration.simplification_mode` | string | Mode used ("aggressive") |
| `configuration.transformations` | array | List of transformations applied |
| `models.<model>.ops_before` | int | Operations before simplification |
| `models.<model>.ops_after` | int | Operations after simplification |
| `models.<model>.ops_reduction_pct` | float | Operation reduction percentage |
| `models.<model>.terms_before` | int | Terms before simplification |
| `models.<model>.terms_after` | int | Terms after simplification |
| `models.<model>.terms_reduction_pct` | float | Term reduction percentage |
| `models.<model>.execution_time_ms` | float | Simplification time (milliseconds) |
| `aggregate.total_models` | int | Number of models benchmarked |
| `aggregate.avg_ops_reduction_pct` | float | Average operation reduction |
| `aggregate.avg_terms_reduction_pct` | float | Average term reduction |
| `aggregate.models_with_20pct_reduction` | int | Count meeting ≥20% threshold |
| `aggregate.target_met` | bool | Whether ≥50% of models met ≥20% target |

### 4.2 Storage Location

**Directory:** `baselines/simplification/`

**Files:**
- `baseline_sprint11.json` - Sprint 11 baseline (with all 11 transformations)
- `baseline_sprint11_disabled.json` - Sprint 11 baseline (transformations disabled, for comparison)
- `README.md` - Format documentation

**Git Tracking:** Use git (not git-lfs). Files are small (<10KB).

**Versioning:** Create new baseline file for each sprint that adds transformations:
- `baseline_sprint11.json` (11 transformations)
- `baseline_sprint12.json` (if new transformations added)
- etc.

### 4.3 Baseline Update Procedure

**Script:** `scripts/update_baselines.sh`

**Command:**
```bash
./scripts/update_baselines.sh simplification
```

**Implementation:**
```bash
#!/bin/bash
# Update simplification baseline

# Run benchmarking on all Tier 1 models
python scripts/measure_simplification.py \
  --mode aggressive \
  --models circle himmel16 hs62 mathopt1 maxmin mhw4d mhw4dx mingamma rbrock trig \
  --output baselines/simplification/baseline_sprint11.json

# Commit baseline update
git add baselines/simplification/baseline_sprint11.json
git commit -m "Update Sprint 11 simplification baseline"
```

---

## 5. Prototype Validation (Deferred)

**Status:** NOT IMPLEMENTED in this research phase.

**Rationale:**
- Task 2 is RESEARCH phase - validate methodology, not implementation
- Task 7 (Prototype Simplification Metrics) will implement and validate on 3 models
- This document provides complete specifications for Task 7 implementation

**Task 7 Will Validate:**
1. Implement `count_terms()` function
2. Create `simplify_with_metrics()` wrapper
3. Run on rbrock.gms, mhw4d.gms, maxmin.gms
4. Manually count operations/terms for 5 expressions per model (spot check)
5. Compare automated vs manual counts (target: <5% error)
6. Measure performance overhead (target: <1%)

**Expected Results (based on Sprint 11 prototype):**
- rbrock.gms: ~30-40% reduction (simple model, many factoring opportunities)
- mhw4d.gms: ~25-35% reduction (medium complexity, CSE opportunities)
- maxmin.gms: ~20-30% reduction (complex nested indexing, fewer simplifications)
- Performance overhead: <0.1% (two AST traversals are fast)

---

## 6. Decision Rationale

### 6.1 Why Use Existing `_expression_size()` for Operations?

**Decision:** Use existing `SimplificationPipeline._expression_size()` method as-is.

**Rationale:**
1. **Consistency:** Already used in Sprint 11 metrics (SimplificationMetrics.initial_size, final_size)
2. **Tested:** Validated through 10 days of Sprint 11 development
3. **Fast:** Simple recursion, O(n) complexity
4. **No Dependencies:** Uses only AST types from `src/ir/ast.py`

**Trade-off:** Includes leaf nodes at size 1, so "operation count" is technically AST node count. For benchmarking, this is acceptable as long as we measure both before/after with the same method (relative reduction is accurate).

**Alternative Considered:** Implement pure operation count (exclude leaves). Rejected due to:
- Requires two traversals (operations + leaves) = 2x overhead
- Inconsistent with existing Sprint 11 metrics
- Negligible benefit (both approaches measure reduction accurately)

### 6.2 Why Custom Term Counting Instead of Expansion?

**Decision:** Implement `count_terms()` to count additive components WITHOUT expanding expressions.

**Rationale:**
1. **Preserves Factored Form:** Factoring reduces visual complexity even if term count stays same when expanded
2. **Measures Actual Expression:** We want to measure the expression we generate, not a canonical form
3. **Fast:** Single traversal, O(n) complexity
4. **Aligns with Transformations:** Sprint 11 transformations like factoring operate on factored form

**Alternative Considered:** Expand all expressions to sum-of-products, then count terms. Rejected due to:
- Would undo factoring transformations we're trying to measure
- Expansion is expensive (O(n²) in worst case for nested products)
- Doesn't reflect actual expression complexity

### 6.3 Why Instrument `simplify_aggressive()` Only?

**Decision:** Collect metrics only for "aggressive" simplification mode.

**Rationale:**
1. **Sprint 12 Focus:** Benchmarking is for validating Sprint 11 transformations, which are all in aggressive mode
2. **Simplicity:** Single entry/exit point for instrumentation
3. **Performance:** Other modes (none, basic, advanced) don't need benchmarking overhead

**Alternative Considered:** Instrument all modes. Rejected due to:
- Adds complexity without benefit
- Sprint 12 goal is to measure Sprint 11 transformations (aggressive mode only)
- Can add other modes later if needed

### 6.4 Why JSON Baselines Instead of CSV?

**Decision:** Store baselines as JSON files.

**Rationale:**
1. **Structured Data:** JSON handles nested structure better (per-model metrics, aggregate metrics, metadata)
2. **Existing Pattern:** Follows existing baseline format (see `baselines/performance/golden/sprint11_day6.json`)
3. **Tooling:** Python `json` module is built-in, no dependencies
4. **Human-Readable:** JSON is easy to inspect and version control

**Alternative Considered:** CSV files. Rejected due to:
- Flat structure doesn't handle nested data well
- No metadata support (sprint, commit, configuration)
- Harder to extend schema over time

---

## 7. Alternatives Considered

### 7.1 SymPy Integration

**Status:** REJECTED

**Reason:** SymPy is not used in nlp2mcp codebase. All symbolic manipulation is custom AST-based. Adding SymPy dependency just for `count_ops()` is not justified.

**Pros:**
- Well-tested implementation
- Comprehensive symbolic algebra

**Cons:**
- Large dependency (not currently used)
- Requires conversion between nlp2mcp AST and SymPy expressions
- Performance overhead for conversion
- Not aligned with project architecture

### 7.2 Per-Transformation Metrics (Ablation Study)

**Status:** DEFERRED to future sprints

**Approach:** Measure reduction for each transformation individually by enabling one at a time.

**Pros:**
- Identifies which transformations contribute most to reduction
- Guides prioritization for future optimization

**Cons:**
- 11× measurement overhead (11 runs per model)
- Complex interdependencies (some transformations enable others)
- Not required for Sprint 12 success criterion validation

**Decision:** Focus on aggregate reduction (all transformations on vs all off) for Sprint 12. Defer granular analysis to future sprints if needed.

### 7.3 Comparison with External Parsers

**Status:** OUT OF SCOPE

**Approach:** Benchmark nlp2mcp reduction against other GAMS parsers or symbolic algebra systems.

**Pros:**
- Provides external validation
- Competitive analysis

**Cons:**
- No comparable tools (nlp2mcp is unique in GAMS→MCP conversion)
- Requires significant effort to integrate external tools
- Not required for Sprint 12 goals

**Decision:** Internal validation (before/after Sprint 11 transformations) is sufficient for Sprint 12.

---

## 8. Implementation Checklist for Sprint 12 Days 1-3

This checklist will guide Sprint 12 implementation based on this research.

### Day 1: Metric Collection Implementation (2-3h)

- [ ] Implement `count_terms(expr)` function in `src/ir/metrics.py`
  - [ ] Handle Binary('+') and Binary('-') recursively
  - [ ] Base case: all other expressions = 1 term
  - [ ] Add unit tests for term counting

- [ ] Implement `count_operations(expr)` wrapper (or use existing `_expression_size()`)
  - [ ] Document whether leaf nodes are included
  - [ ] Add unit tests

- [ ] Create `SimplificationBenchmarkMetrics` dataclass
  - [ ] Fields: model, ops_before, ops_after, terms_before, terms_after, time_ms, reductions
  - [ ] Add `to_dict()` method for JSON serialization

- [ ] Implement `simplify_with_metrics()` wrapper
  - [ ] Measure before/after metrics
  - [ ] Time execution with `time.perf_counter()`
  - [ ] Calculate reduction percentages
  - [ ] Return (simplified_expr, metrics)

### Day 2: Baseline Collection (2-3h)

- [ ] Create `scripts/measure_simplification.py`
  - [ ] CLI args: `--models`, `--output`, `--mode`
  - [ ] Load models from `models/gamslib/`
  - [ ] Run simplification with metrics
  - [ ] Aggregate results
  - [ ] Write JSON baseline

- [ ] Run baseline collection on all 10 Tier 1 models
  - [ ] With transformations: `baseline_sprint11.json`
  - [ ] Without transformations (optional): `baseline_sprint11_disabled.json`

- [ ] Create `baselines/simplification/README.md`
  - [ ] Document JSON schema
  - [ ] Explain update procedure
  - [ ] Note versioning strategy

### Day 3: Validation & CI Integration (1-2h)

- [ ] Validate baseline results
  - [ ] Check ≥20% reduction on ≥50% of models
  - [ ] Manually spot-check 2-3 models
  - [ ] Verify performance overhead <1%

- [ ] Add baseline validation to CI
  - [ ] Create `scripts/check_simplification_regression.py`
  - [ ] Compare current run vs baseline
  - [ ] Fail if reduction drops below threshold

- [ ] Document findings in Sprint 12 Day 3 checkpoint

---

## 9. Summary

### 9.1 Key Decisions

| Decision Point | Resolution |
|----------------|------------|
| **Term Definition** | Additive components in current form (no expansion) |
| **Operation Definition** | AST nodes (use existing `_expression_size()`) |
| **Measurement Tool** | Custom `count_terms()` + existing `_expression_size()` |
| **Instrumentation** | Wrap `simplify_aggressive()` with metrics collection |
| **Baseline Format** | JSON with per-model + aggregate metrics |
| **Performance Target** | <1% overhead (achievable with simple AST traversal) |
| **Validation** | Defer to Task 7 prototype |

### 9.2 Risks Mitigated

| Risk | Mitigation |
|------|------------|
| **False Positive (claim 20% when <20%)** | Use consistent before/after measurement with same methodology |
| **False Negative (miss 20% due to undercount)** | Validate against manual counts in Task 7 (target: <5% error) |
| **Performance Overhead** | Simple AST traversal, no transformation impact (<0.1% expected) |
| **Baseline Drift** | Version baselines by sprint, track git commit |

### 9.3 Success Criteria (from Task 2 Requirements)

- [x] Clear definitions of term/operation that align with transformation implementations
- [x] Measurement approach specified (will be validated in Task 7 on 3 models)
- [x] Instrumentation design documented and feasible for Sprint 12 implementation
- [x] Baseline schema compatible with git and CI tooling (JSON, <10KB, versioned)
- [x] Prototype deferred to Task 7 (research complete, implementation pending)
- [x] All measurement unknowns from Task 1 addressed (see Unknowns section below)

---

## 10. Unknowns Resolved

### Unknown 1.1: Baseline Metric Selection

**Decision:** Use TWO metrics:
1. **Operation Count** - AST node count via existing `_expression_size()`
2. **Term Count** - Additive components via custom `count_terms()`

**Rationale:**
- Operations measure computational complexity
- Terms measure visual/conceptual complexity
- Both are easy to implement and fast to compute
- Sprint 11 success criterion focuses on terms ("≥20% term reduction")

**Evidence:**
- Existing `_expression_size()` already validated in Sprint 11 pipeline
- Term counting aligns with user perception of simplification
- Both metrics are O(n) traversals (<0.1% overhead)

### Unknown 1.3: Statistical Significance Thresholds

**Decision:** Use ≥20% reduction threshold on ≥50% of models (per Sprint 12 success criteria). NO statistical testing for sample of 10 models.

**Rationale:**
- Sample size (n=10) is too small for meaningful statistical tests
- Deterministic measurements (AST traversal) have zero variance
- Success criterion is absolute (≥20% on ≥5 models), not statistical

**Threshold Justification:**
- 20% reduction is significant and user-visible
- 50% of models (5/10) allows for model diversity (some models may not benefit from transformations)
- Sprint 11 prototype showed 39.2% average on synthetic examples, so 20% on real models is conservative but achievable

### Unknown 1.4: Granular vs. Aggregate Reporting

**Decision:** Start with AGGREGATE reporting (all transformations on vs all off). Defer per-transformation ablation study to future sprints.

**Approach:**
- Collect: baseline_sprint11.json (all 11 transformations enabled)
- Optional: baseline_sprint11_disabled.json (all transformations disabled, for comparison)
- Report: aggregate metrics (avg reduction, models meeting threshold)

**Effort Implications:**
- Aggregate: 2-3h implementation (Sprint 12 Day 1-2)
- Ablation: 11× overhead = 20-30h (deferred)

**Rationale:**
- Sprint 12 goal is to validate Sprint 11 success criterion (aggregate reduction)
- Per-transformation analysis requires significant effort (11 runs per model)
- Transformation interdependencies complicate attribution
- Can add granular analysis in future sprint if needed for optimization

### Unknown 1.7: Actionability of Results

**Decision Criteria:**

| Benchmark Result | Action |
|-----------------|--------|
| **≥20% reduction on ≥50% models** | ✅ SUCCESS - Sprint 11 validated, continue with transformations |
| **15-19% reduction** | ⚠️ PARTIAL - Investigate low-performers, consider targeted optimizations |
| **10-14% reduction** | ⚠️ INVESTIGATE - Review measurement methodology, check for bugs |
| **<10% reduction** | ❌ RETHINK - Transformations may not be effective, consider alternative approaches |

**Link to User Value:**
- Operation reduction → Faster evaluation (if expressions are evaluated repeatedly)
- Term reduction → Simpler code generation, easier debugging
- Both → Smaller MCP model files

**Sprint 13+ Roadmap Guidance:**
- If ≥30% reduction: Invest in more transformations (HIGH ROI)
- If 20-30% reduction: Optimize existing transformations (MEDIUM ROI)
- If <20% reduction: Focus on other improvements (parser coverage, MCP correctness, etc.)

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-11-29  
**Next Review:** Sprint 12 Day 3 (after baseline collection)
