# Sprint 15 Performance Measurement Approach

**Created:** January 12, 2026  
**Status:** Complete  
**Purpose:** Define accurate timing methodology and baseline metrics for Sprint 15 pipeline testing

---

## Executive Summary

This document defines the performance measurement approach for Sprint 15's parse, translate, and solve pipeline. It specifies timing methodology, statistical analysis, baseline documentation format, and implementation guidelines.

**Key Decisions:**
- Use `time.perf_counter()` for all timing (highest resolution, monotonic)
- Record timing for both success and failure cases
- Use wall time (not CPU time) to capture subprocess overhead
- Document baselines in both JSON (machine-readable) and Markdown (human-readable)
- Establish per-stage and per-model-type baselines

---

## 1. Timing Methodology

### 1.1 Timer Function Selection

**Chosen: `time.perf_counter()`**

| Timer | Resolution | Monotonic | Includes Sleep | Use Case |
|-------|------------|-----------|----------------|----------|
| `time.time()` | ~1ms | No | Yes | Wall clock time |
| `time.perf_counter()` | ~100ns | Yes | Yes | **Performance measurement** |
| `time.process_time()` | ~1ms | Yes | No | CPU time only |
| `time.monotonic()` | ~1ms | Yes | Yes | Timeouts, scheduling |

**Rationale:**
- `time.perf_counter()` provides the highest resolution available
- Monotonic: immune to system clock adjustments
- Already used in `batch_parse.py` and `batch_translate.py`
- `verify_convexity.py` uses `time.time()` - should be updated for consistency

**Reference:** [Python time documentation](https://docs.python.org/3/library/time.html#time.perf_counter)

### 1.2 Parse Timing

**What's Measured:** Time to parse a single GAMS model file into IR.

**Start Point:** Before calling `parse_model_file()`

**End Point:** After `parse_model_file()` returns (success) or exception caught (failure)

**Includes:**
- File reading (I/O)
- Lexical analysis
- Parsing (grammar)
- IR construction

**Excludes:**
- Database loading/saving
- Progress reporting
- Error categorization overhead

**Implementation Pattern (existing in batch_parse.py):**
```python
import time

def parse_single_model(model_path: Path) -> dict:
    start_time = time.perf_counter()
    try:
        ir = parse_model_file(model_path)
        elapsed = time.perf_counter() - start_time
        return {
            "status": "success",
            "parse_time_seconds": round(elapsed, 4),
            # ...
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {
            "status": "failure",
            "parse_time_seconds": round(elapsed, 4),  # Still record time
            # ...
        }
```

### 1.3 Translate Timing

**What's Measured:** Time to translate parsed IR to MCP format.

**Start Point:** Before creating subprocess for translation

**End Point:** After subprocess completes or timeout

**Includes:**
- Subprocess creation overhead
- Translation execution
- MCP file writing
- Process cleanup

**Excludes:**
- Database loading/saving
- Model selection logic

**Implementation Pattern (existing in batch_translate.py):**
```python
def translate_single_model(model_id: str, gms_path: Path, output_path: Path) -> dict:
    start_time = time.perf_counter()
    try:
        proc = subprocess.Popen(
            ["python", "-m", "src.cli", str(gms_path), "-o", str(output_path), "--quiet"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(timeout=60)
        elapsed = time.perf_counter() - start_time
        # ... handle result
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        elapsed = time.perf_counter() - start_time
        return {"status": "failure", "translate_time_seconds": round(elapsed, 4), ...}
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {"status": "failure", "translate_time_seconds": round(elapsed, 4), ...}
```

### 1.4 Solve Timing

**What's Measured:** Time to solve MCP model using PATH solver.

**Start Point:** Before creating GAMS subprocess

**End Point:** After GAMS subprocess completes or timeout

**Includes:**
- GAMS startup overhead
- Model compilation
- PATH solver execution
- Solution file writing

**Available Time Sources:**
1. **Wall time (subprocess):** `time.perf_counter()` around subprocess call
2. **GAMS-reported time:** `RESOURCE USAGE` in .lst file

**Recommendation:** Use wall time (subprocess) for:
- Consistency with parse/translate timing
- Captures full subprocess overhead
- Always available (even on solver failure)

**Optional:** Extract GAMS-reported time from .lst file for:
- Solver-only timing (excludes startup)
- Detailed performance analysis

**Implementation Pattern:**
```python
def solve_mcp_model(mcp_path: Path, timeout: int = 60) -> dict:
    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            ["gams", str(mcp_path), "lo=3"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=mcp_path.parent,
        )
        elapsed = time.perf_counter() - start_time
        
        # Optionally extract GAMS-reported time from .lst
        lst_path = mcp_path.with_suffix(".lst")
        gams_time = extract_resource_usage(lst_path)  # From "RESOURCE USAGE" line
        
        return {
            "status": "success" if result.returncode == 0 else "failure",
            "solve_time_seconds": round(elapsed, 4),  # Wall time
            "gams_resource_seconds": gams_time,       # Optional: solver-reported
            # ...
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start_time
        return {
            "status": "timeout",
            "solve_time_seconds": round(elapsed, 4),
            # ...
        }
```

**Extracting GAMS Resource Time:**
```python
import re

def extract_resource_usage(lst_path: Path) -> float | None:
    """Extract RESOURCE USAGE from GAMS .lst file."""
    try:
        content = lst_path.read_text()
        # Pattern: "RESOURCE USAGE, LIMIT          0.155 10000000000.000"
        match = re.search(r"RESOURCE USAGE, LIMIT\s+([\d.]+)", content)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return None
```

### 1.5 Failure Timing

**Policy:** Always record timing, even for failures.

**Rationale:**
- Failure timing helps identify slow-failing models
- Timeout cases should record the timeout duration
- Enables analysis of "why did this model take so long to fail?"

**Status-Time Relationship:**
| Status | Time Recorded | Notes |
|--------|---------------|-------|
| success | Actual time | Normal case |
| failure | Actual time | Time until exception |
| timeout | Timeout value | e.g., 60.0 seconds |
| not_tested | null | Stage not attempted |

---

## 2. Statistical Analysis

### 2.1 Summary Statistics

For each pipeline stage (parse, translate, solve), compute:

| Statistic | Description | Formula/Notes |
|-----------|-------------|---------------|
| count | Number of models | Total attempted |
| success_count | Successful runs | Status = success |
| failure_count | Failed runs | Status = failure |
| timeout_count | Timed out runs | Status = timeout |
| mean | Average time | sum(times) / count |
| median | Middle value | 50th percentile |
| stddev | Standard deviation | Population stddev |
| min | Minimum time | Fastest model |
| max | Maximum time | Slowest model |
| p25 | 25th percentile | First quartile |
| p75 | 75th percentile | Third quartile |
| p90 | 90th percentile | Slower 10% |
| p99 | 99th percentile | Slowest 1% |

**Implementation:**
```python
import statistics
from typing import NamedTuple

class TimingStats(NamedTuple):
    count: int
    success_count: int
    failure_count: int
    timeout_count: int
    mean: float
    median: float
    stddev: float
    min: float
    max: float
    p25: float
    p75: float
    p90: float
    p99: float

def compute_timing_stats(times: list[float]) -> TimingStats:
    """Compute timing statistics from a list of times."""
    if not times:
        return TimingStats(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    sorted_times = sorted(times)
    n = len(times)
    
    def percentile(p: float) -> float:
        k = (n - 1) * p / 100
        f = int(k)
        c = f + 1 if f < n - 1 else f
        return sorted_times[f] + (k - f) * (sorted_times[c] - sorted_times[f])
    
    return TimingStats(
        count=n,
        success_count=n,  # Caller should provide actual counts
        failure_count=0,
        timeout_count=0,
        mean=statistics.mean(times),
        median=statistics.median(times),
        stddev=statistics.pstdev(times) if n > 1 else 0.0,
        min=min(times),
        max=max(times),
        p25=percentile(25),
        p75=percentile(75),
        p90=percentile(90),
        p99=percentile(99),
    )
```

### 2.2 Outlier Detection

**Definition:** A model is an outlier if its time exceeds mean + 2 * stddev.

**Purpose:** Identify models that take unusually long, which may indicate:
- Complex models requiring optimization
- Parser/translator bugs causing exponential behavior
- Edge cases worth investigating

**Implementation:**
```python
def detect_outliers(times: list[tuple[str, float]], threshold: float = 2.0) -> list[tuple[str, float]]:
    """Detect timing outliers.
    
    Args:
        times: List of (model_id, time) tuples
        threshold: Number of standard deviations for outlier threshold
    
    Returns:
        List of (model_id, time) for outliers
    """
    if len(times) < 3:
        return []
    
    values = [t for _, t in times]
    mean = statistics.mean(values)
    stddev = statistics.pstdev(values)
    cutoff = mean + threshold * stddev
    
    return [(model_id, t) for model_id, t in times if t > cutoff]
```

### 2.3 By Model Type Analysis

Compute separate statistics for each model type:

| Type | Description |
|------|-------------|
| LP | Linear Programming |
| NLP | Nonlinear Programming |
| QCP | Quadratically Constrained |
| MIP | Mixed Integer Programming |
| MIQCP | Mixed Integer QCP |
| Other | Remaining types |

**Rationale:** Different model types may have significantly different timing characteristics. NLP models may parse slower due to complexity.

---

## 3. Baseline Documentation Format

### 3.1 JSON Format (Machine-Readable)

Store baselines in `data/gamslib/baseline_metrics.json`:

```json
{
  "schema_version": "1.0.0",
  "baseline_date": "2026-01-XX",
  "sprint": "Sprint 15",
  "nlp2mcp_version": "0.3.0",
  "total_models": 160,
  
  "parse": {
    "attempted": 160,
    "success": 34,
    "failure": 126,
    "success_rate": 0.2125,
    "timing": {
      "mean": 0.95,
      "median": 0.72,
      "stddev": 0.43,
      "min": 0.15,
      "max": 3.21,
      "p90": 1.65,
      "p99": 2.89
    },
    "by_type": {
      "LP": {"attempted": 45, "success": 12, "success_rate": 0.267, "mean_time": 0.65},
      "NLP": {"attempted": 80, "success": 15, "success_rate": 0.188, "mean_time": 1.12},
      "QCP": {"attempted": 35, "success": 7, "success_rate": 0.200, "mean_time": 0.89}
    }
  },
  
  "translate": {
    "attempted": 34,
    "success": 32,
    "failure": 2,
    "success_rate": 0.941,
    "timing": {
      "mean": 0.32,
      "median": 0.28,
      "stddev": 0.15,
      "min": 0.12,
      "max": 0.87
    }
  },
  
  "solve": {
    "attempted": 32,
    "success": 30,
    "failure": 2,
    "success_rate": 0.938,
    "timing": {
      "mean": 0.15,
      "median": 0.12,
      "stddev": 0.08,
      "min": 0.05,
      "max": 0.45
    }
  },
  
  "comparison": {
    "attempted": 30,
    "match": 28,
    "mismatch": 2,
    "match_rate": 0.933
  },
  
  "full_pipeline": {
    "success": 28,
    "total": 160,
    "success_rate": 0.175
  },
  
  "outliers": {
    "parse": ["model_x", "model_y"],
    "translate": [],
    "solve": ["model_z"]
  }
}
```

### 3.2 Markdown Format (Human-Readable)

Store in `docs/planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md`:

```markdown
# Sprint 15 Baseline Metrics

**Established:** January XX, 2026  
**nlp2mcp Version:** 0.3.0  
**Total Models:** 160 (GAMSLIB verified_convex)

## Executive Summary

| Stage | Attempted | Success | Rate | Mean Time |
|-------|-----------|---------|------|-----------|
| Parse | 160 | 34 | 21.3% | 0.95s |
| Translate | 34 | 32 | 94.1% | 0.32s |
| Solve | 32 | 30 | 93.8% | 0.15s |
| Compare | 30 | 28 | 93.3% | - |

**Full Pipeline Success:** 28/160 (17.5%)

## Parse Stage

### Success Rate
- **Total:** 160 models
- **Success:** 34 (21.3%)
- **Failure:** 126 (78.8%)

### Timing Statistics
| Metric | Value |
|--------|-------|
| Mean | 0.95s |
| Median | 0.72s |
| Stddev | 0.43s |
| Min | 0.15s |
| Max | 3.21s |
| P90 | 1.65s |
| P99 | 2.89s |

### By Model Type
| Type | Attempted | Success | Rate | Mean Time |
|------|-----------|---------|------|-----------|
| LP | 45 | 12 | 26.7% | 0.65s |
| NLP | 80 | 15 | 18.8% | 1.12s |
| QCP | 35 | 7 | 20.0% | 0.89s |

### Outliers (>2 stddev)
- `model_x`: 3.21s (parse)
- `model_y`: 2.95s (parse)

## Translate Stage

[Similar structure...]

## Solve Stage

[Similar structure...]

## Comparison Stage

[Similar structure...]

## Error Distribution

### Parse Errors
| Category | Count | % |
|----------|-------|---|
| syntax_error | 97 | 77.0% |
| unsupported_feature | 18 | 14.3% |
| validation_error | 7 | 5.6% |
| missing_include | 3 | 2.4% |
| internal_error | 1 | 0.8% |

### Translate Errors
[...]

## Notes

- Baseline established using GAMSLIB models with `convexity_status = verified_convex`
- All timing using `time.perf_counter()` (wall time)
- Tests run on [machine specs]
```

---

## 4. Implementation Guidelines

### 4.1 Database Storage

Timing is stored in the existing schema fields:

```json
{
  "nlp2mcp_parse": {
    "status": "success",
    "parse_time_seconds": 0.95,
    "parse_date": "2026-01-15T10:00:00Z"
  },
  "nlp2mcp_translate": {
    "status": "success",
    "translate_time_seconds": 0.32,
    "translate_date": "2026-01-15T10:00:05Z"
  },
  "mcp_solve": {
    "status": "success",
    "solve_time_seconds": 0.15,
    "solve_date": "2026-01-15T10:00:10Z"
  }
}
```

### 4.2 Reporting Format

**Progress Output (during batch run):**
```
[10/160] Processing model_x... success (0.95s)
[20/160] Processing model_y... failure (0.12s)
         ETA: 2m 30s remaining
```

**Summary Output (after batch run):**
```
=== Parse Results ===
Total: 160 | Success: 34 (21.3%) | Failure: 126 (78.8%)
Mean: 0.95s | Median: 0.72s | Stddev: 0.43s
Range: 0.15s - 3.21s

Outliers (>2 stddev):
  - model_x: 3.21s
  - model_y: 2.95s

Error Distribution:
  syntax_error: 97 (77.0%)
  unsupported_feature: 18 (14.3%)
  ...
```

### 4.3 Precision and Rounding

- Store times with 4 decimal places (0.0001s = 0.1ms precision)
- Display times with 2 decimal places in reports
- Use `round(elapsed, 4)` when storing to database

### 4.4 Warmup Considerations

**For single runs (current approach):** No warmup needed.

**For benchmarking (future enhancement):**
- First run may be slower due to Python/OS caching
- Consider discarding first run or running 3+ times and taking median
- Document if warmup runs were used

---

## 5. Sprint 15 Baseline Plan

### 5.1 When to Record

1. **Initial Baseline:** After implementing test infrastructure (Sprint 15 Day 5-6)
2. **Final Baseline:** End of Sprint 15 (Sprint 15 Day 10)
3. **On Demand:** After significant parser/translator changes

### 5.2 What Models to Include

- All 160 GAMSLIB models with `convexity_status = verified_convex`
- Run full pipeline: parse → translate → solve → compare

### 5.3 How to Document

1. Run `run_full_test.py --json > results.json`
2. Generate `data/gamslib/baseline_metrics.json` from results
3. Create `docs/planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md` from template
4. Commit baseline files with message: "Establish Sprint 15 baseline metrics"

### 5.4 Environment Documentation

Record in baseline:
- Machine specs (CPU, RAM)
- OS version
- Python version
- nlp2mcp version
- GAMS version
- PATH solver version

---

## 6. Regression Detection (Future)

### 6.1 Thresholds

| Metric | Warning | Alert |
|--------|---------|-------|
| Success rate drop | >5% | >10% |
| Mean time increase | >20% | >50% |
| New outliers | Any | >3 |

### 6.2 Comparison Script (Sprint 16+)

```python
def compare_baselines(old: dict, new: dict) -> list[str]:
    """Compare two baselines and return warnings."""
    warnings = []
    
    for stage in ["parse", "translate", "solve"]:
        old_rate = old[stage]["success_rate"]
        new_rate = new[stage]["success_rate"]
        if new_rate < old_rate - 0.05:
            warnings.append(f"{stage} success rate dropped: {old_rate:.1%} → {new_rate:.1%}")
        
        old_mean = old[stage]["timing"]["mean"]
        new_mean = new[stage]["timing"]["mean"]
        if new_mean > old_mean * 1.2:
            warnings.append(f"{stage} mean time increased: {old_mean:.2f}s → {new_mean:.2f}s")
    
    return warnings
```

---

## Appendix A: Existing Implementation Review

### batch_parse.py (Sprint 14)
- ✅ Uses `time.perf_counter()`
- ✅ Records time on success and failure
- ✅ Stores as `parse_time_seconds` (4 decimal places)
- ⚠️ Progress reporting every 10 models with ETA

### batch_translate.py (Sprint 14)
- ✅ Uses `time.perf_counter()`
- ✅ Records time on success, failure, and timeout
- ✅ Stores as `translate_time_seconds`
- ✅ 60-second timeout with proper cleanup

### verify_convexity.py (Sprint 13)
- ⚠️ Uses `time.time()` - should update to `time.perf_counter()`
- ✅ Records time for GAMS subprocess
- ✅ Extracts solver/model status from .lst file

### Recommendation
Update `verify_convexity.py` to use `time.perf_counter()` for consistency. This is a minor change and can be done during Sprint 15 implementation.

---

## Appendix B: References

1. [Python time module documentation](https://docs.python.org/3/library/time.html)
2. [Python statistics module](https://docs.python.org/3/library/statistics.html)
3. [GAMS .lst file format](https://www.gams.com/latest/docs/UG_GamsOutput.html)
4. Sprint 14 SPRINT_SUMMARY.md - baseline metrics
5. PATH solver documentation
