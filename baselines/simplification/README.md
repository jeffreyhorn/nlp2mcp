# Simplification Metrics Baselines

**Purpose:** Store baseline term reduction metrics for Sprint 11+ transformations.

**Created:** 2025-11-30  
**Schema Version:** 1.0.0

---

## Overview

This directory contains baseline metrics for IR simplification transformations. Baselines track:
- Operation count reduction (AST node count)
- Term count reduction (additive terms in sum-of-products form)
- Transformation effectiveness per model

**Use Case:** Detect regressions in simplification effectiveness during CI runs.

---

## JSON Schema (v1.0.0)

### Top-Level Structure

```json
{
  "schema_version": "1.0.0",
  "created_at": "2025-11-30T12:00:00Z",
  "sprint": "sprint11",
  "git_commit": "abc123...",
  "description": "Sprint 11 baseline with 11 transformations",
  "transformations_enabled": [
    "constant_propagation",
    "constant_fold",
    ...
  ],
  "models": {
    "circle.gms": { ... },
    "himmel16.gms": { ... },
    ...
  },
  "aggregate": { ... }
}
```

###  Field Descriptions

**Metadata:**
- `schema_version`: Baseline schema version (SemVer)
- `created_at`: ISO 8601 timestamp
- `sprint`: Sprint identifier (e.g., "sprint11", "sprint12")
- `git_commit`: Git commit SHA when baseline created
- `description`: Human-readable description
- `transformations_enabled`: List of transformation names enabled during collection

**Per-Model Metrics:**
```json
"circle.gms": {
  "ops_before": 150,        // Operation count before simplification
  "ops_after": 120,         // Operation count after simplification
  "terms_before": 45,       // Term count before simplification
  "terms_after": 36,        // Term count after simplification
  "ops_reduction_pct": 20.0,      // (ops_before - ops_after) / ops_before * 100
  "terms_reduction_pct": 20.0,    // (terms_before - terms_after) / terms_before * 100
  "execution_time_ms": 12.5,      // Simplification execution time
  "iterations": 3,                // Number of fixpoint iterations
  "transformations_applied": {
    "constant_propagation": 5,
    "zero_multiply": 2,
    ...
  }
}
```

**Aggregate Metrics:**
```json
"aggregate": {
  "total_models": 10,
  "ops_avg_reduction_pct": 18.5,     // Average across all models
  "terms_avg_reduction_pct": 15.2,   // Average across all models
  "models_meeting_threshold": 6,     // Models with ≥20% reduction
  "threshold_pct": 20.0,             // Threshold used
  "total_execution_time_ms": 125.0   // Sum of all model execution times
}
```

---

## File Naming Convention

**Pattern:** `baseline_sprint<N>.json`

**Examples:**
- `baseline_sprint11.json` - Sprint 11 baseline (11 transformations)
- `baseline_sprint12.json` - Sprint 12 baseline (if new transformations added)
- `baseline_sprint11_disabled.json` - Optional: Sprint 11 with transformations disabled

**When to Create New Baseline:**
- New sprint adds/modifies transformation passes
- Major IR refactoring that changes expression structure
- Significant performance optimization that affects metrics

---

## Update Procedure

### Manual Update

```bash
# Run measurement script on all Tier 1 models
python scripts/measure_simplification.py \
  --mode aggressive \
  --models circle himmel16 hs62 mathopt1 maxmin mhw4d mhw4dx mingamma rbrock trig \
  --output baselines/simplification/baseline_sprint11.json

# Commit baseline update
git add baselines/simplification/baseline_sprint11.json
git commit -m "Update Sprint 11 simplification baseline"
```

### Automated Update

```bash
# Use update script
./scripts/update_baselines.sh simplification
```

---

## Versioning Policy

### Baseline Versioning

**Strategy:** Create new baseline file per sprint that changes transformations.

**Retention:** Keep historical baselines for regression testing across sprints.

**Git Tracking:** All baseline files are git-tracked (not git-lfs). Files are small (<10KB).

### Schema Versioning

**Current:** 1.0.0

**Changes:**
- **MAJOR:** Breaking schema changes (remove fields, change types)
- **MINOR:** Additive changes (new optional fields)
- **PATCH:** Documentation updates, no schema changes

**Migration:** If schema changes, update `schema_version` and create migration script.

---

## Baseline Invalidation Triggers

**When to Recollect Baseline:**

1. **Transformation Code Changes**
   - New transformation added to pipeline
   - Existing transformation logic modified
   - Transformation priority/ordering changed

2. **IR Structure Changes**
   - AST node definitions modified
   - Expression representation changed
   - Term/operation counting logic updated

3. **Model Set Changes**
   - Tier 1 model set expanded/reduced
   - Model parsing fixes that change IR structure

**Do NOT Recollect For:**
- Documentation updates
- Test improvements (unless they reveal measurement bugs)
- Unrelated IR features (e.g., solver integration)

---

## Usage in CI

**Regression Check:**
```bash
# Compare current metrics against baseline
python scripts/check_simplification_regression.py \
  --baseline baselines/simplification/baseline_sprint11.json \
  --threshold 5.0  # Fail if reduction drops >5%
```

**Expected Behavior:**
- ✅ **PASS:** Current reduction ≥ (baseline - threshold)
- ❌ **FAIL:** Current reduction < (baseline - threshold)
- ⚠️ **WARN:** Current reduction significantly higher (possible baseline drift)

---

## Example Baseline Entry

```json
{
  "schema_version": "1.0.0",
  "created_at": "2025-11-30T12:00:00Z",
  "sprint": "sprint11",
  "git_commit": "abc123def456",
  "description": "Sprint 11 baseline with 11 transformations (aggressive mode)",
  "transformations_enabled": [
    "constant_propagation",
    "constant_fold",
    "zero_multiply",
    "identity_add",
    "identity_multiply",
    "double_negation",
    "subtract_zero",
    "divide_one",
    "power_one",
    "power_zero",
    "multiply_one"
  ],
  "models": {
    "circle.gms": {
      "ops_before": 150,
      "ops_after": 120,
      "terms_before": 45,
      "terms_after": 36,
      "ops_reduction_pct": 20.0,
      "terms_reduction_pct": 20.0,
      "execution_time_ms": 12.5,
      "iterations": 3,
      "transformations_applied": {
        "constant_propagation": 5,
        "zero_multiply": 2,
        "identity_add": 3
      }
    }
  },
  "aggregate": {
    "total_models": 10,
    "ops_avg_reduction_pct": 18.5,
    "terms_avg_reduction_pct": 15.2,
    "models_meeting_threshold": 6,
    "threshold_pct": 20.0,
    "total_execution_time_ms": 125.0
  }
}
```

---

## References

- **Task 2:** Term Reduction Measurement (`docs/research/term_reduction_measurement.md`)
- **Task 7:** Simplification Metrics Prototype (`docs/research/simplification_metrics_prototype.md`)
- **Sprint 12 Plan:** Component 1 (Baseline Metrics Collection)

---

**Maintained By:** Sprint Team  
**Last Updated:** 2025-11-30  
**Next Review:** Sprint 12 Day 3 (after baseline collection)
