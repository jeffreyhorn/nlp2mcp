# GAMSLIB KPI Definitions and Baseline Targets

**Date:** 2025-11-12  
**Unknown:** 3.5 (High Priority)  
**Owner:** Validation Team  
**Status:** ✅ RESOLVED

---

## Assumption

Sprint 6 needs clear KPI definitions and baseline targets to measure nlp2mcp's performance against the GAMSLIB benchmark suite. KPIs should reflect the three-stage pipeline: parse → convert → solve.

---

## Research Questions

1. What KPIs should we track: parse%, convert%, solve%, or others?
2. How do we compute each KPI given a set of test models?
3. What are realistic baseline targets for Sprint 6 with 10 models?
4. Should we track additional metrics like error rates, performance, correctness?
5. How do we handle partial failures (e.g., parses but doesn't convert)?

---

## Investigation

### Sprint 6 Pipeline Architecture

nlp2mcp has a 3-stage pipeline for each model:

```
Stage 1: PARSE          Stage 2: CONVERT        Stage 3: SOLVE
┌─────────────┐        ┌─────────────┐         ┌─────────────┐
│ GAMS Model  │   →    │  Model IR   │    →    │ MCP Solution│
│  (.gms)     │        │  (Python)   │         │  (PATH)     │
└─────────────┘        └─────────────┘         └─────────────┘
     ↓                       ↓                       ↓
  SUCCESS or             SUCCESS or              SUCCESS or
  PARSE_FAILED          CONVERT_FAILED          SOLVE_FAILED
```

**Success Criteria:**
- **PARSE:** Model loads into IR without syntax errors
- **CONVERT:** IR successfully generates MCP format (`.mcp` file)
- **SOLVE:** PATH solver returns optimal/feasible solution

**Failure Modes:**
- **PARSE_FAILED:** Syntax error, unsupported feature in parser
- **CONVERT_FAILED:** IR is valid but MCP generation fails (e.g., convexity issue)
- **SOLVE_FAILED:** MCP file generated but PATH solver fails to solve

---

## KPI Definitions

### KPI 1: Parse Rate (parse%)

**Definition:** Percentage of models that successfully parse into IR

**Formula:**
```python
parse% = (count_parse_success / count_total_models) * 100
```

**Interpretation:**
- Measures parser robustness
- High parse% → Parser handles diverse GAMS syntax well
- Low parse% → Many unsupported syntax features

**Example:**
- Total models: 10
- Parse success: 6
- Parse rate: 6/10 = 60%

---

### KPI 2: Convert Rate (convert%)

**Definition:** Percentage of **successfully parsed models** that convert to MCP format

**Formula:**
```python
convert% = (count_convert_success / count_parse_success) * 100
```

**Interpretation:**
- Measures MCP generation robustness (conditional on parsing)
- High convert% → IR → MCP transformation is reliable
- Low convert% → Many IR constructs can't be converted to MCP

**Example:**
- Parse success: 6 models
- Convert success: 5 models (1 parsed but didn't convert)
- Convert rate: 5/6 = 83.3%

**Important:** Convert rate is **conditional on parsing**. We only attempt conversion for models that parse successfully.

---

### KPI 3: Solve Rate (solve%)

**Definition:** Percentage of **successfully converted models** that PATH solves

**Formula:**
```python
solve% = (count_solve_success / count_convert_success) * 100
```

**Interpretation:**
- Measures end-to-end success (conditional on parsing + converting)
- High solve% → MCP reformulation is mathematically correct
- Low solve% → Generated MCP files may be nonconvex or ill-conditioned

**Example:**
- Convert success: 5 models
- Solve success: 3 models (2 converted but didn't solve)
- Solve rate: 3/5 = 60%

**Important:** Solve rate is **conditional on conversion**. We only attempt solving for models that convert successfully.

---

### KPI 4: End-to-End Success Rate (e2e%)

**Definition:** Percentage of **all models** that successfully parse, convert, AND solve

**Formula:**
```python
e2e% = (count_solve_success / count_total_models) * 100
```

**Alternative Formula:**
```python
e2e% = parse% × convert% × solve%  (approximately, due to rounding)
```

**Interpretation:**
- Measures overall nlp2mcp reliability
- This is the **most important KPI** for users
- Represents the probability a random GAMS model will work end-to-end

**Example:**
- Total models: 10
- End-to-end success: 3 models
- E2E rate: 3/10 = 30%

**Verification:**
- parse% = 60%, convert% = 83.3%, solve% = 60%
- e2e% ≈ 0.60 × 0.833 × 0.60 = 0.30 = 30% ✓

---

## Cascade Relationships

The KPIs form a cascade where each stage depends on the previous:

```
All Models (N=10)
│
├─ PARSE SUCCESS (6) ───────────────→ parse% = 60%
│  │
│  ├─ CONVERT SUCCESS (5) ──────────→ convert% = 83.3% (of 6)
│  │  │
│  │  ├─ SOLVE SUCCESS (3) ────────→ solve% = 60% (of 5)
│  │  │                                e2e% = 30% (of 10)
│  │  │
│  │  └─ SOLVE FAILED (2)
│  │
│  └─ CONVERT FAILED (1)
│
└─ PARSE FAILED (4)
```

**Key Insight:** A model can only reach stage N if it succeeded at stage N-1.

---

## Baseline Targets for Sprint 6

### Context: Tier 1 (10 Models)

Sprint 6 focuses on establishing the benchmark infrastructure with a small set of models.

### Conservative Targets (Minimum Acceptance Criteria)

**Target 1: Minimum Model Count**
- **Goal:** N ≥ 10 models in Tier 1
- **Rationale:** Statistically meaningful sample size
- **Status:** ✅ Achieved (10 models downloaded in Task 7)

**Target 2: Parse Rate**
- **Goal:** parse% ≥ 50%
- **Rationale:** At least half of models should parse (conservative estimate from Unknown 3.3)
- **Interpretation:** If parse% < 50%, parser needs significant enhancement

**Target 3: Convert Rate**
- **Goal:** convert% ≥ 80% (of parsed models)
- **Rationale:** IR → MCP conversion should be reliable for parsed models
- **Interpretation:** If convert% < 80%, MCP generation has major gaps

**Target 4: Solve Rate**
- **Goal:** solve% ≥ 50% (of converted models)
- **Rationale:** PATH should solve at least half of well-formed MCPs
- **Interpretation:** If solve% < 50%, many models may be nonconvex or ill-conditioned

**Target 5: End-to-End Success**
- **Goal:** e2e% ≥ 20%
- **Calculation:** 50% × 80% × 50% = 20%
- **Rationale:** At least 2 models (2/10 = 20%) should work completely
- **Interpretation:** This is a **minimum viability threshold**

### Stretch Targets (Desirable Goals)

**Stretch 1: Parse Rate**
- **Goal:** parse% ≥ 70%
- **Interpretation:** Parser handles most common GAMS syntax

**Stretch 2: Convert Rate**
- **Goal:** convert% ≥ 90%
- **Interpretation:** Very reliable IR → MCP transformation

**Stretch 3: Solve Rate**
- **Goal:** solve% ≥ 70%
- **Interpretation:** Most generated MCPs are solvable

**Stretch 4: End-to-End Success**
- **Goal:** e2e% ≥ 45%
- **Calculation:** 70% × 90% × 70% ≈ 44%
- **Interpretation:** Nearly half of all models work end-to-end

---

## Summary Table: Sprint 6 Targets

| KPI | Formula | Conservative Target | Stretch Target | Why This Matters |
|-----|---------|---------------------|----------------|------------------|
| **parse%** | parse_success / total | ≥ 50% | ≥ 70% | Parser robustness |
| **convert%** | convert_success / parse_success | ≥ 80% | ≥ 90% | MCP generation reliability |
| **solve%** | solve_success / convert_success | ≥ 50% | ≥ 70% | Mathematical correctness |
| **e2e%** | solve_success / total | ≥ 20% | ≥ 45% | Overall user experience |

**Minimum Acceptance:** Meet all conservative targets (50%, 80%, 50%, 20%)  
**Success Criteria:** Meet 3/4 stretch targets

---

## Decision

✅ **Use 4-KPI system with conservative + stretch targets for Sprint 6**

### Rationale

1. **Clear Metrics:** Each KPI has an unambiguous definition and formula
2. **Cascading Design:** KPIs reflect the 3-stage pipeline naturally
3. **Realistic Targets:** Conservative targets are achievable with 10 models
4. **Growth Path:** Stretch targets provide clear improvement goals
5. **Actionable:** Low KPI values point to specific areas for improvement

---

## Python Implementation

### Data Structure

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class StageStatus(Enum):
    """Status for each pipeline stage"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"

@dataclass
class ModelResult:
    """Result for a single model through the pipeline"""
    model_name: str
    gms_file: str
    
    # Stage 1: Parse
    parse_status: StageStatus
    parse_error: Optional[str] = None
    parse_error_category: Optional[str] = None  # From Unknown 3.3
    
    # Stage 2: Convert
    convert_status: StageStatus
    convert_error: Optional[str] = None
    mcp_file: Optional[str] = None
    
    # Stage 3: Solve
    solve_status: StageStatus
    solve_error: Optional[str] = None
    solve_time: Optional[float] = None  # seconds
    objective_value: Optional[float] = None
    
    def is_parse_success(self) -> bool:
        return self.parse_status == StageStatus.SUCCESS
    
    def is_convert_success(self) -> bool:
        return self.convert_status == StageStatus.SUCCESS
    
    def is_solve_success(self) -> bool:
        return self.solve_status == StageStatus.SUCCESS
    
    def is_e2e_success(self) -> bool:
        return (self.is_parse_success() and 
                self.is_convert_success() and 
                self.is_solve_success())

@dataclass
class BenchmarkKPIs:
    """Computed KPIs for benchmark run"""
    
    # Counts
    total_models: int
    parse_success: int
    convert_success: int
    solve_success: int
    
    # Rates (percentages)
    parse_rate: float
    convert_rate: float
    solve_rate: float
    e2e_rate: float
    
    # Targets
    meets_conservative: bool
    meets_stretch: bool
    
    def __str__(self) -> str:
        return f"""Benchmark KPIs:
  Total Models: {self.total_models}
  
  Parse Success:   {self.parse_success:2d} / {self.total_models:2d} = {self.parse_rate:.1f}%
  Convert Success: {self.convert_success:2d} / {self.parse_success:2d} = {self.convert_rate:.1f}%
  Solve Success:   {self.solve_success:2d} / {self.convert_success:2d} = {self.solve_rate:.1f}%
  E2E Success:     {self.solve_success:2d} / {self.total_models:2d} = {self.e2e_rate:.1f}%
  
  Targets Met:
    Conservative: {'✅ PASS' if self.meets_conservative else '❌ FAIL'}
    Stretch:      {'✅ PASS' if self.meets_stretch else '❌ FAIL'}
"""
```

### KPI Computation Function

```python
def compute_kpis(results: List[ModelResult]) -> BenchmarkKPIs:
    """
    Compute KPIs from a list of model results.
    
    Args:
        results: List of ModelResult objects from benchmark run
    
    Returns:
        BenchmarkKPIs with computed metrics
    """
    
    # Count successes at each stage
    total_models = len(results)
    parse_success = sum(1 for r in results if r.is_parse_success())
    convert_success = sum(1 for r in results if r.is_convert_success())
    solve_success = sum(1 for r in results if r.is_solve_success())
    
    # Compute rates (handle division by zero)
    parse_rate = (parse_success / total_models * 100) if total_models > 0 else 0.0
    convert_rate = (convert_success / parse_success * 100) if parse_success > 0 else 0.0
    solve_rate = (solve_success / convert_success * 100) if convert_success > 0 else 0.0
    e2e_rate = (solve_success / total_models * 100) if total_models > 0 else 0.0
    
    # Check targets
    meets_conservative = (
        total_models >= 10 and
        parse_rate >= 50.0 and
        convert_rate >= 80.0 and
        solve_rate >= 50.0 and
        e2e_rate >= 20.0
    )
    
    stretch_count = sum([
        parse_rate >= 70.0,
        convert_rate >= 90.0,
        solve_rate >= 70.0,
        e2e_rate >= 45.0
    ])
    meets_stretch = stretch_count >= 3  # 3 out of 4 stretch targets
    
    return BenchmarkKPIs(
        total_models=total_models,
        parse_success=parse_success,
        convert_success=convert_success,
        solve_success=solve_success,
        parse_rate=parse_rate,
        convert_rate=convert_rate,
        solve_rate=solve_rate,
        e2e_rate=e2e_rate,
        meets_conservative=meets_conservative,
        meets_stretch=meets_stretch
    )
```

### Usage Example

```python
# Run benchmark
results = []

for model_file in tier1_models:
    result = ModelResult(
        model_name=model_file.stem,
        gms_file=str(model_file),
        parse_status=StageStatus.NOT_ATTEMPTED,
        convert_status=StageStatus.NOT_ATTEMPTED,
        solve_status=StageStatus.NOT_ATTEMPTED
    )
    
    # Stage 1: Parse
    try:
        ir = parse_model_file(model_file)
        result.parse_status = StageStatus.SUCCESS
    except Exception as e:
        result.parse_status = StageStatus.FAILED
        result.parse_error = str(e)
        result.parse_error_category = classify_parse_error(e, model_file)
        results.append(result)
        continue  # Skip to next model
    
    # Stage 2: Convert
    try:
        mcp_file = convert_to_mcp(ir, output_dir)
        result.convert_status = StageStatus.SUCCESS
        result.mcp_file = str(mcp_file)
    except Exception as e:
        result.convert_status = StageStatus.FAILED
        result.convert_error = str(e)
        results.append(result)
        continue  # Skip to next model
    
    # Stage 3: Solve
    try:
        solution = solve_with_path(mcp_file)
        if solution.is_optimal():
            result.solve_status = StageStatus.SUCCESS
            result.objective_value = solution.objective
            result.solve_time = solution.time
        else:
            result.solve_status = StageStatus.FAILED
            result.solve_error = f"Solver status: {solution.status}"
    except Exception as e:
        result.solve_status = StageStatus.FAILED
        result.solve_error = str(e)
    
    results.append(result)

# Compute KPIs
kpis = compute_kpis(results)
print(kpis)

# Example output:
# Benchmark KPIs:
#   Total Models: 10
#   
#   Parse Success:    6 / 10 = 60.0%
#   Convert Success:  5 /  6 = 83.3%
#   Solve Success:    3 /  5 = 60.0%
#   E2E Success:      3 / 10 = 30.0%
#   
#   Targets Met:
#     Conservative: ✅ PASS
#     Stretch:      ❌ FAIL
```

---

## Additional Metrics (Optional)

While the 4 primary KPIs are sufficient for Sprint 6, we may want to track additional metrics in future sprints:

### Performance Metrics
- **Parse time:** Average time to parse models
- **Convert time:** Average time to generate MCP
- **Solve time:** Average time for PATH to solve
- **Total time:** End-to-end time per model

### Error Metrics
- **Parse error breakdown:** Count per error category (from Unknown 3.3)
- **Convert error types:** Common conversion failures
- **Solve failure modes:** PATH status codes (infeasible, unbounded, etc.)

### Quality Metrics
- **Solution correctness:** Compare against GAMS reference solutions (if available)
- **Objective value accuracy:** Relative error in objective value
- **Constraint satisfaction:** Verify KKT conditions are met

**Decision for Sprint 6:** Track only the 4 primary KPIs. Add additional metrics in Sprint 7+ if needed.

---

## Implementation Plan for Day 6

When Unknown 3.5 resolution is applied during dashboard generation:

### Step 1: Implement Data Structures (30min)

Create `src/benchmark/types.py` with:
- `StageStatus` enum
- `ModelResult` dataclass
- `BenchmarkKPIs` dataclass

### Step 2: Implement KPI Computation (30min)

Create `src/benchmark/kpis.py` with:
- `compute_kpis()` function
- Helper functions for target checking
- Unit tests for edge cases (zero division, empty results)

### Step 3: Integrate into Benchmark Script (30min)

Modify `scripts/gamslib_benchmark.py` to:
- Collect `ModelResult` objects during execution
- Call `compute_kpis()` after all models processed
- Display KPI summary to console
- Save KPIs to JSON for dashboard

### Step 4: Test KPI Computation (30min)

Create test cases:
- All models succeed (parse% = convert% = solve% = e2e% = 100%)
- All models fail parse (parse% = 0%, others undefined)
- Parse succeeds, convert fails (parse% = 100%, convert% = 0%)
- Mixed results (realistic scenario)

### Estimated Implementation Time: 2 hours on Day 6

---

## Test Cases

### Test 1: Perfect Run (All Succeed)
```python
results = [
    ModelResult(name="m1", parse=SUCCESS, convert=SUCCESS, solve=SUCCESS),
    ModelResult(name="m2", parse=SUCCESS, convert=SUCCESS, solve=SUCCESS),
]
kpis = compute_kpis(results)

assert kpis.parse_rate == 100.0
assert kpis.convert_rate == 100.0
assert kpis.solve_rate == 100.0
assert kpis.e2e_rate == 100.0
```

### Test 2: All Parse Failures
```python
results = [
    ModelResult(name="m1", parse=FAILED, convert=NOT_ATTEMPTED, solve=NOT_ATTEMPTED),
    ModelResult(name="m2", parse=FAILED, convert=NOT_ATTEMPTED, solve=NOT_ATTEMPTED),
]
kpis = compute_kpis(results)

assert kpis.parse_rate == 0.0
assert kpis.convert_rate == 0.0  # Undefined, but returns 0.0
assert kpis.solve_rate == 0.0    # Undefined, but returns 0.0
assert kpis.e2e_rate == 0.0
```

### Test 3: Cascade Failure (Parse → Convert Fails)
```python
results = [
    ModelResult(name="m1", parse=SUCCESS, convert=FAILED, solve=NOT_ATTEMPTED),
    ModelResult(name="m2", parse=SUCCESS, convert=SUCCESS, solve=SUCCESS),
]
kpis = compute_kpis(results)

assert kpis.parse_rate == 100.0   # 2/2
assert kpis.convert_rate == 50.0  # 1/2
assert kpis.solve_rate == 100.0   # 1/1
assert kpis.e2e_rate == 50.0      # 1/2
```

### Test 4: Realistic Sprint 6 Scenario
```python
results = [
    # 6 models parse successfully
    ModelResult(name="m1", parse=SUCCESS, convert=SUCCESS, solve=SUCCESS),
    ModelResult(name="m2", parse=SUCCESS, convert=SUCCESS, solve=SUCCESS),
    ModelResult(name="m3", parse=SUCCESS, convert=SUCCESS, solve=SUCCESS),
    ModelResult(name="m4", parse=SUCCESS, convert=SUCCESS, solve=FAILED),
    ModelResult(name="m5", parse=SUCCESS, convert=SUCCESS, solve=FAILED),
    ModelResult(name="m6", parse=SUCCESS, convert=FAILED, solve=NOT_ATTEMPTED),
    # 4 models fail parse
    ModelResult(name="m7", parse=FAILED, convert=NOT_ATTEMPTED, solve=NOT_ATTEMPTED),
    ModelResult(name="m8", parse=FAILED, convert=NOT_ATTEMPTED, solve=NOT_ATTEMPTED),
    ModelResult(name="m9", parse=FAILED, convert=NOT_ATTEMPTED, solve=NOT_ATTEMPTED),
    ModelResult(name="m10", parse=FAILED, convert=NOT_ATTEMPTED, solve=NOT_ATTEMPTED),
]
kpis = compute_kpis(results)

assert kpis.total_models == 10
assert kpis.parse_success == 6
assert kpis.convert_success == 5
assert kpis.solve_success == 3

assert kpis.parse_rate == 60.0     # 6/10
assert kpis.convert_rate == 83.3   # 5/6 (rounded)
assert kpis.solve_rate == 60.0     # 3/5
assert kpis.e2e_rate == 30.0       # 3/10

assert kpis.meets_conservative == True   # All targets met
assert kpis.meets_stretch == False       # Only parse% >= 50% (not 70%)
```

---

## Deliverable

This research document confirms:

✅ **4 KPIs defined with clear formulas (parse%, convert%, solve%, e2e%)**  
✅ **Cascading relationship between KPIs documented**  
✅ **Conservative targets set (≥50%, ≥80%, ≥50%, ≥20%)**  
✅ **Stretch targets set (≥70%, ≥90%, ≥70%, ≥45%)**  
✅ **Python implementation provided with data structures and functions**  
✅ **Test cases defined for validation**  
✅ **Implementation plan defined for Day 6**

**Ready for Day 6 dashboard generation:** Yes

---

## References

- Unknown 3.3: Parse Error Categories (`docs/research/gamslib_parse_errors_preliminary.md`)
- Task 7: GAMSLIB Model Downloader (`scripts/download_gamslib_models.py`)
- Task 8: GAMSLIB Benchmark Script (`scripts/gamslib_benchmark.py`)
- Task 9: GAMSLIB Dashboard Generator (`scripts/generate_gamslib_dashboard.py`)
- KNOWN_UNKNOWNS.md: Unknown 3.5 (lines 959-1042)
