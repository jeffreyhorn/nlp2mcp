# Performance Baselines for Sprint 14

**Task:** Sprint 14 Prep Task 8 - Establish Performance Baselines  
**Created:** 2026-01-01  
**Purpose:** Inform Sprint 14 timeout and resource settings

---

## Executive Summary

This document establishes performance baselines for batch operations in Sprint 14. Key findings:

- **Catalog I/O is fast:** Load ~2.5ms, Save ~9ms (negligible overhead)
- **Model processing:** ~1 second per model average
- **Batch time for 160 models:** ~3 minutes (well under concerns)
- **Memory usage:** Minimal (~624KB for catalog)
- **Recommendation:** Sequential processing is sufficient; no parallelization needed

---

## Catalog I/O Performance

### Test Environment

- File: `data/gamslib/catalog.json`
- Size: 176,927 bytes (172.78 KB)
- Models: 219 entries
- Python: 3.12 with standard `json` module

### Measurements (10 runs each)

| Operation | Average | Min | Max |
|-----------|---------|-----|-----|
| Load (json.load) | 2.48 ms | 1.42 ms | 9.30 ms |
| Save (json.dump, indent=2) | 8.94 ms | 7.75 ms | 9.73 ms |

### Analysis

- Load time is dominated by first run (cold cache)
- Save time is consistent due to file I/O
- Both operations are negligible compared to model processing
- No optimization needed for catalog I/O

### Projection for gamslib_status.json

The new database will have similar structure with additional pipeline fields:
- Estimated size: ~200-250 KB (20-40% larger than catalog.json)
- Projected load time: ~3-4 ms
- Projected save time: ~10-12 ms

---

## Model Processing Performance

### nlp2mcp Pipeline Timing

Timing for full pipeline (parse + translate):

| Model | Type | Size | Time | Status |
|-------|------|------|------|--------|
| prodmix | LP | 1,222 | 1.05s | success |
| rbrock | NLP | 531 | 0.75s | success |
| hs62 | NLP | 1,233 | 0.94s | success (warnings) |
| himmel11 | QCP | 1,130 | 0.93s | success (warnings) |
| trnsport | LP | ~1,000 | 0.81s | failure (parse) |

### Parse Rate Analysis (from Task 6)

| Metric | Value |
|--------|-------|
| Average parse time (all models) | 0.97 seconds |
| Average parse time (successful) | 0.95 seconds |
| Minimum parse time | 0.71 seconds |
| Maximum parse time | 2.58 seconds |
| Timeouts (60s limit) | 0/30 |

### Timing Breakdown

Based on measurements:

| Phase | Typical Time | Notes |
|-------|--------------|-------|
| Python startup | ~0.5s | One-time per invocation |
| Parse | ~0.3-0.5s | Depends on model complexity |
| Translate | ~0.2-0.3s | Only for successful parses |
| File write | <0.01s | Negligible |
| **Total** | **~1.0s** | Per model |

---

## Batch Performance Projections

### Scenario: 160 Verified Convex Models

| Metric | Calculation | Result |
|--------|-------------|--------|
| Models to process | 160 | - |
| Average time per model | 0.97s | From Task 6 |
| Base processing time | 160 × 0.97s | 155 seconds |
| With 20% overhead | 155s × 1.2 | 186 seconds |
| **Estimated total** | - | **~3 minutes** |

### Scenario: Full Corpus (219 Models)

| Metric | Calculation | Result |
|--------|-------------|--------|
| Models to process | 219 | - |
| Average time per model | 1.0s | Conservative |
| Base processing time | 219 × 1.0s | 219 seconds |
| With 20% overhead | 219s × 1.2 | 263 seconds |
| **Estimated total** | - | **~4.5 minutes** |

### Comparison with Sprint 13

Sprint 13 convexity verification (GAMS solve):
- 219 models in ~30 minutes
- Average ~8 seconds per model (includes GAMS solve)

Sprint 14 nlp2mcp pipeline (parse + translate):
- 160 models in ~3 minutes
- Average ~1 second per model
- **~8x faster** (no GAMS solve)

---

## Memory Usage

### Measurements

| Metric | Value |
|--------|-------|
| Python baseline | ~10.8 MB |
| After catalog load | ~11.4 MB |
| Catalog memory delta | ~624 KB |

### Analysis

- Catalog memory usage is minimal
- Each model is processed independently (no accumulation)
- Memory is released after each model completes
- No memory concerns for batch operations

### Recommendations

- No special memory management needed
- Default Python garbage collection is sufficient
- No need for streaming or chunked processing

---

## Parallel vs Sequential Processing

### Question: Should batch operations run in parallel?

### Analysis

| Aspect | Sequential | Parallel |
|--------|------------|----------|
| Total time (160 models) | ~3 min | ~1-2 min |
| Implementation complexity | Simple | Complex |
| Error handling | Straightforward | Complex |
| Progress reporting | Easy | Complex |
| Resource contention | None | Possible |

### Recommendation: **Sequential Processing**

**Rationale:**
1. **3 minutes is acceptable** - Well under any time pressure
2. **Simplicity** - Sequential is easier to implement and debug
3. **Progress reporting** - Natural per-model progress updates
4. **Error isolation** - One model failure doesn't affect others
5. **No parallelization overhead** - No process/thread management

### When to Consider Parallel

Parallel processing would only be worthwhile if:
- Batch size grows to 1000+ models
- Per-model time increases significantly (>10s)
- There's a hard time constraint (<1 minute)

None of these apply to Sprint 14.

---

## Recommended Configurations

### Timeout Settings

| Operation | Current | Recommended | Notes |
|-----------|---------|-------------|-------|
| Model parse | 60s | 60s | No changes needed |
| Model translate | N/A | 30s | Add if separate |
| Batch operation | None | 30 min | Safety limit |

### Batch Processing Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Batch size | All (160) | Small enough for single batch |
| Progress interval | 10 models | ~10 seconds between updates |
| Save interval | 10 models | Balance safety vs I/O |
| Retry on failure | 0 | Failures are deterministic |

### Progress Reporting Format

```
[  1/160]  3% Processing prodmix...
[ 10/160]  6% Processing model10... (10 complete, 0.97s avg)
[ 50/160] 31% Processing model50... (50 complete, 0.98s avg)
[100/160] 63% Processing model100... (100 complete, 0.99s avg)
[160/160] 100% Complete. 160 models in 2m 35s (0.97s avg)
```

---

## Performance Bottleneck Analysis

### Current Bottlenecks (in order)

1. **Python startup** (~0.5s per model)
   - Mitigation: Batch processing in single Python process
   - Already planned for db_manager.py

2. **Parse time** (~0.3-0.5s per model)
   - Limited by grammar complexity and model size
   - No easy optimization without parser rewrite

3. **Catalog I/O** (~10ms per save)
   - Already negligible
   - Batched saves further reduce impact

### Non-Bottlenecks

- File I/O for models (<1ms)
- Memory allocation (minimal)
- JSON serialization (~9ms per save)

---

## Sprint 14 Implications

### Confirmed Expectations

1. **Batch time is not a concern**
   - 160 models in ~3 minutes
   - Well under Sprint 13's 30-minute verification

2. **Sequential processing is appropriate**
   - Simple, reliable, sufficient speed
   - No parallelization needed

3. **Current timeouts are adequate**
   - 60s per model handles all tested cases
   - No models approached timeout

### Unknowns Verified

| Unknown | Finding |
|---------|---------|
| 1.1: Batch verification time | ~3 minutes for 160 models |
| 5.3: Sequential vs parallel | Sequential recommended |

---

## Test Commands

### Catalog I/O Timing

```python
import json
import time
from pathlib import Path

CATALOG_PATH = Path("data/gamslib/catalog.json")

# Load timing
start = time.perf_counter()
with open(CATALOG_PATH) as f:
    data = json.load(f)
print(f"Load: {(time.perf_counter() - start) * 1000:.2f} ms")

# Save timing
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
    start = time.perf_counter()
    json.dump(data, f, indent=2)
    f.flush()
    print(f"Save: {(time.perf_counter() - start) * 1000:.2f} ms")
```

### Model Processing Timing

```bash
# Time single model
time python -m src.cli data/gamslib/raw/prodmix.gms -o /tmp/test.gms

# Time multiple models
for model in prodmix rbrock hs62 himmel11; do
    echo "=== $model ==="
    time python -m src.cli data/gamslib/raw/$model.gms -o /tmp/test.gms
done
```

---

## Document History

- 2026-01-01: Initial creation (Sprint 14 Prep Task 8)
