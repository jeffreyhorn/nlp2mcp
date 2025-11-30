# Multi-Metric Baselines

**Purpose:** Store baseline metrics for parse rate, convert rate, and performance regression detection.

**Created:** 2025-11-30  
**Schema Version:** 1.0.0

---

## Overview

This directory contains multi-metric baselines for comprehensive CI regression detection. Baselines track:
- **Parse Rate:** Percentage of models successfully parsed
- **Convert Rate:** Percentage of parsed models successfully converted to MCP format
- **Performance:** Average parse/conversion time per model

**Use Case:** Multi-dimensional regression detection during CI runs with separate warn/fail thresholds per metric.

---

## JSON Schema (v1.0.0)

### Top-Level Structure

```json
{
  "sprint": "Sprint 12",
  "checkpoint": "Day 10 - Sprint Complete",
  "commit": "abc123...",
  "timestamp": "2025-12-13T23:59:59Z",
  "model_set": "tier1",
  "models": {
    "circle.gms": { ... },
    "himmel16.gms": { ... },
    ...
  },
  "summary": { ... }
}
```

### Field Descriptions

**Metadata:**
- `sprint`: Sprint identifier (e.g., "Sprint 11", "Sprint 12")
- `checkpoint`: Sprint checkpoint or milestone description
- `commit`: Git commit SHA when baseline created
- `timestamp`: ISO 8601 timestamp
- `model_set`: Model set identifier ("tier1", "tier2", etc.)

**Per-Model Metrics:**
```json
"circle.gms": {
  "parse_rate": 1.0,         // 1.0 = success, 0.0 = failure
  "convert_rate": 1.0,       // 1.0 = success, 0.0 = failure (requires parse success)
  "parse_time_ms": 45,       // Parse time in milliseconds
  "total_time_ms": 443       // Total time (parse + convert) in milliseconds
}
```

**Aggregate Metrics:**
```json
"summary": {
  "total_models": 10,
  "parse_rate": 1.0,              // Aggregate parse rate (0.0-1.0)
  "parse_rate_pct": 100.0,        // As percentage (0-100)
  "parsed_models": 10,            // Count of successfully parsed models
  "convert_rate": 1.0,            // Aggregate convert rate (0.0-1.0)
  "convert_rate_pct": 100.0,      // As percentage (0-100)
  "converted_models": 10,         // Count of successfully converted models
  "avg_parse_time_ms": 56.2,     // Average parse time across all models
  "avg_total_time_ms": 478.5,    // Average total time across all models
  "p95_parse_time_ms": 89,       // Optional: 95th percentile parse time
  "p95_total_time_ms": 723       // Optional: 95th percentile total time
}
```

---

## File Naming Convention

**Pattern:** `baseline_sprint<N>.json`

**Examples:**
- `baseline_sprint11.json` - Sprint 11 baseline (Tier 1, 10 models)
- `baseline_sprint12.json` - Sprint 12 baseline (Tier 1 + Tier 2, 20 models)
- `baseline_sprint12_tier2.json` - Optional: Tier 2 only baseline

**When to Create New Baseline:**
- Sprint checkpoint reached (Day 6, Day 10, etc.)
- Model set changes (Tier 1 → Tier 2 expansion)
- Major parser/converter changes that affect metrics

---

## Update Procedure

### Manual Update

```bash
# Run ingestion on all models
python scripts/measure_parse_rate.py \
  --models circle himmel16 hs62 mathopt1 maxmin mhw4d mhw4dx mingamma rbrock trig \
  --output baselines/multi_metric/baseline_sprint12.json

# Commit baseline update
git add baselines/multi_metric/baseline_sprint12.json
git commit -m "Update Sprint 12 multi-metric baseline"
```

### Automated Update

```bash
# Use update script
./scripts/update_baselines.sh --multi-metric sprint12
```

---

## Versioning Policy

### Baseline Versioning

**Strategy:** Create new baseline file per sprint checkpoint or model set change.

**Retention:** Keep historical baselines for regression testing across sprints.

**Git Tracking:** All baseline files are git-tracked (not git-lfs). Files are small (<50KB).

### Schema Versioning

**Current:** 1.0.0

**Changes:**
- **MAJOR:** Breaking schema changes (remove fields, change types)
- **MINOR:** Additive changes (new optional fields like p95 metrics)
- **PATCH:** Documentation updates, no schema changes

**Migration:** If schema changes, update `schema_version` field and create migration script.

---

## Baseline Invalidation Triggers

**When to Recollect Baseline:**

1. **Parser Changes**
   - Grammar modifications that affect parse success rate
   - Error recovery improvements
   - New language features supported

2. **Converter Changes**
   - MCP format updates
   - Conversion logic improvements
   - New conversion features

3. **Performance Changes**
   - Major refactoring that affects timing
   - Optimization work
   - Infrastructure changes (e.g., switch to different Python version)

4. **Model Set Changes**
   - New models added to test suite
   - Models removed or renamed
   - Model content updated significantly

**Do NOT Recollect For:**
- Documentation updates
- Test improvements (unless they reveal parser bugs)
- Unrelated features (e.g., simplification, solver integration)

---

## Regression Detection Thresholds

### Recommended Thresholds (from Task 4)

**Parse Rate:**
- Warn: 5% drop from baseline
- Fail: 10% drop from baseline

**Convert Rate:**
- Warn: 5% drop from baseline
- Fail: 10% drop from baseline

**Performance (avg_parse_time_ms):**
- Warn: 20% increase from baseline
- Fail: 50% increase from baseline

### Threshold Methodology

**Approach:** Relative thresholds (% change from baseline)

**Formula (for metrics where higher is better):**
```python
relative_change = (baseline - current) / baseline
status = FAIL if relative_change > fail_threshold
status = WARN if relative_change > warn_threshold
```

**Formula (for metrics where lower is better, e.g., performance):**
```python
relative_change = (current - baseline) / baseline
status = FAIL if relative_change > fail_threshold
status = WARN if relative_change > warn_threshold
```

---

## Usage in CI

**Multi-Metric Regression Check:**
```bash
# Compare current metrics against baseline
python scripts/check_parse_rate_regression.py \
  --current reports/gamslib_ingestion.json \
  --baseline origin/main \
  --parse-warn 0.05 --parse-fail 0.10 \
  --convert-warn 0.05 --convert-fail 0.10 \
  --performance-warn 0.20 --performance-fail 0.50
```

**Expected Output:**
```
📊 Multi-Metric Regression Check

Metric           Status    Current   Baseline   Change   Thresholds (Warn/Fail)
----------------  --------  --------  ---------  -------  -----------------------
Parse Rate       ✅ PASS    100.0%     100.0%    +0.0%   5% / 10%
Convert Rate     ✅ PASS    100.0%     100.0%    +0.0%   5% / 10%
Performance      ✅ PASS    56.2ms     56.2ms    +0.0%   20% / 50%

Exit Code: 0 (PASS)
```

**Exit Code Behavior:**
- **0 (PASS):** All metrics pass
- **1 (WARN):** At least one metric warns, none fail
- **2 (FAIL):** At least one metric fails

---

## Example Baseline Entry

```json
{
  "sprint": "Sprint 12",
  "checkpoint": "Day 10 - Sprint Complete",
  "commit": "abc123def456",
  "timestamp": "2025-12-13T23:59:59Z",
  "model_set": "tier1",
  "models": {
    "circle.gms": {
      "parse_rate": 1.0,
      "convert_rate": 1.0,
      "parse_time_ms": 45,
      "total_time_ms": 443
    },
    "himmel16.gms": {
      "parse_rate": 1.0,
      "convert_rate": 1.0,
      "parse_time_ms": 52,
      "total_time_ms": 389
    },
    "rbrock.gms": {
      "parse_rate": 1.0,
      "convert_rate": 1.0,
      "parse_time_ms": 48,
      "total_time_ms": 412
    }
  },
  "summary": {
    "total_models": 10,
    "parse_rate": 1.0,
    "parse_rate_pct": 100.0,
    "parsed_models": 10,
    "convert_rate": 1.0,
    "convert_rate_pct": 100.0,
    "converted_models": 10,
    "avg_parse_time_ms": 56.2,
    "avg_total_time_ms": 478.5,
    "p95_parse_time_ms": 89,
    "p95_total_time_ms": 723
  }
}
```

---

## Relationship to Existing Baselines

**Legacy Baseline (baselines/performance/golden/):**
- Sprint 11 and earlier used performance-only baselines
- Located in `baselines/performance/golden/sprint11_day6.json`
- Same schema as multi-metric baselines (backward compatible)

**Multi-Metric Baselines (baselines/multi_metric/):**
- Sprint 12+ uses multi-metric regression detection
- Extends legacy format with additional aggregate metrics (p95 timing, separate parse/convert counts)
- Enables per-metric threshold configuration

**Migration Path:**
- Existing baselines can be used with multi-metric checks
- No migration required (schema is backward compatible)
- New baselines should use multi_metric/ directory

---

## References

- **Task 4:** Multi-Metric Thresholds (`docs/research/multi_metric_thresholds.md`)
- **Sprint 12 Plan:** Component 2 (Multi-Metric Thresholds, Days 4-6)
- **Existing Script:** `scripts/check_parse_rate_regression.py`

---

**Maintained By:** Sprint Team  
**Last Updated:** 2025-11-30  
**Next Review:** Sprint 12 Day 6 (after multi-metric implementation)
