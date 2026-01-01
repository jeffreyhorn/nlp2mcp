# Sprint 13 Catalog Quality Report

**Date:** January 1, 2026  
**Purpose:** Validate catalog.json quality for Sprint 14 database integration  
**Status:** COMPLETE

---

## Executive Summary

The Sprint 13 catalog (`data/gamslib/catalog.json`) is **high quality** and ready for Sprint 14 database integration. All 219 models have complete required fields, consistent formatting, and no data integrity issues.

### Key Findings

| Check | Status | Details |
|-------|--------|---------|
| Required fields | ✅ PASS | All 219 models have all 7 required fields |
| Null values | ✅ PASS | No null values in required fields |
| Duplicates | ✅ PASS | No duplicate model_ids or sequence_numbers |
| Date formats | ✅ PASS | All dates in ISO 8601 format |
| Field naming | ✅ PASS | All fields use consistent snake_case |

### Recommendations for Sprint 14

1. **Migrate catalog.json to new gamslib_status.json** - Clean migration path
2. **Add structured error objects** - Replace `verification_error` string with structured object
3. **Track license-limited models separately** - 10 models need full license to verify
4. **Re-classify "unknown" status models** - 7 models have valid solve but unexpected status

---

## Catalog Overview

```
Schema version: 1.0.0
Total models: 219
GAMS version: 51.3.0
Created: 2026-01-01T06:56:29Z
Updated: 2026-01-01T07:55:20Z
```

### Model Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| LP | 86 | 39.3% |
| NLP | 120 | 54.8% |
| QCP | 13 | 5.9% |
| **Total** | **219** | **100%** |

### Convexity Status Distribution

| Status | Count | Percentage | Description |
|--------|-------|------------|-------------|
| verified_convex | 57 | 26.0% | LP with optimal solution (model_status=1) |
| likely_convex | 103 | 47.0% | NLP/QCP with locally optimal solution |
| error | 48 | 21.9% | Verification failed (various reasons) |
| unknown | 7 | 3.2% | Unexpected status combination |
| excluded | 4 | 1.8% | Infeasible or locally infeasible |
| **Total** | **219** | **100%** | |

---

## Data Quality Validation

### 1. Required Field Validation

**Required Fields:**
- `model_id` - Unique identifier
- `sequence_number` - GAMSLIB sequence number
- `model_name` - Human-readable name
- `gamslib_type` - Model type (LP, NLP, QCP)
- `source_url` - GAMSLIB source URL
- `download_status` - Download status
- `convexity_status` - Verification result

**Result:** ✅ All 219 models have all required fields with non-null values.

### 2. Optional Field Coverage

| Field | Present | Coverage |
|-------|---------|----------|
| web_page_url | 219 | 100% |
| description | 219 | 100% |
| keywords | 219 | 100% (empty arrays) |
| download_date | 219 | 100% |
| file_path | 219 | 100% |
| file_size_bytes | 219 | 100% |
| notes | 219 | 100% (empty strings) |
| verification_date | 219 | 100% |
| solver_status | 171 | 78.1% (not present for some errors) |
| model_status | 171 | 78.1% (not present for some errors) |
| objective_value | 164 | 74.9% (not present for errors) |
| solve_time_seconds | 219 | 100% |
| verification_error | 48 | 21.9% (only error models) |

### 3. Duplicate Check

| Check | Result |
|-------|--------|
| Duplicate model_ids | ✅ None found |
| Duplicate sequence_numbers | ✅ None found |

### 4. Date Format Validation

All date fields use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

| Field | Format Valid |
|-------|--------------|
| download_date | ✅ 100% valid |
| verification_date | ✅ 100% valid |

### 5. Field Naming Consistency

All 20 fields use consistent snake_case naming:

```
convexity_status, description, download_date, download_status, 
file_path, file_size_bytes, gamslib_type, keywords, model_id, 
model_name, model_status, notes, objective_value, sequence_number, 
solve_time_seconds, solver_status, source_url, verification_date, 
verification_error, web_page_url
```

---

## Error Category Analysis

### Error Distribution (48 models)

| Error Category | Count | Models |
|----------------|-------|--------|
| GAMS compilation error | 19 | dqq, gasoil, gqapsdp, kqkpsdp, methanol, pinene, pool, popdynm, qcp1, qp1, qp1x, qp2, qp3, qp4, qp5, qp7, sddp, t1000, trnspwlx |
| No solve summary found | 15 | asyncloop, embmiex1, gussgrid, maxcut, mhw4dxx, netgen, prodsp, qfilter, scenmerge, sipres, sudoku, tanksize, trussm, weapon, weapons |
| License limits exceeded | 10 | airsp, airsp2, andean, emfl, indus89, jbearing, minsurf, msm, phosdis, torsion |
| Solver error (status=14) | 2 | guss2dim, gussex1 |
| Solver incomplete (status=5) | 2 | lmp1, lmp3 |

### License-Limited Models by Type

| Type | Count | Models |
|------|-------|--------|
| LP | 6 | airsp, airsp2, andean, emfl, indus89, phosdis |
| NLP | 3 | jbearing, minsurf, torsion |
| QCP | 1 | msm |

### Models with $include Directives

Total models using `$include`: 11

| Status | Models with Missing Includes |
|--------|------------------------------|
| error | 2 (gqapsdp, kqkpsdp - use parameterized paths) |

**Note:** Most `$include` files are available. Only 2 models use parameterized include paths (`%instance%`) that cannot be resolved without runtime parameters.

---

## Unknown Status Models

7 models have `convexity_status: unknown` with "Unexpected status combination":

| Model | Type | solver_status | model_status | Issue |
|-------|------|---------------|--------------|-------|
| chance | LP | 1 | 2 | LP with model_status=2 (locally optimal) |
| demo7 | LP | 1 | 2 | LP with model_status=2 (locally optimal) |
| gancnsx | NLP | 1 | 16 | model_status=16 (not documented) |
| immun | LP | 1 | 2 | LP with model_status=2 (locally optimal) |
| minlphi | NLP | 1 | 10 | model_status=10 (integer solution) |
| qalan | QCP | 1 | 8 | model_status=8 (integer infeasible) |
| srcpm | LP | 1 | 2 | LP with model_status=2 (locally optimal) |

**Recommendation:** 4 LP models with model_status=2 could be reclassified as `likely_convex`. Other models need manual review.

---

## Excluded Models

4 models have `convexity_status: excluded`:

| Model | Type | Reason |
|-------|------|--------|
| alan | NLP | Infeasible (model_status=4) |
| circpack | NLP | Locally infeasible (model_status=5) |
| epscm | LP | Infeasible (model_status=4) |
| trigx | NLP | Locally infeasible (model_status=5) |

**Note:** These are correctly classified and should remain excluded from convexity testing.

---

## Recommendations for Sprint 14

### 1. Database Migration Strategy

**Recommendation:** Create new `gamslib_status.json` with enhanced schema, migrate data from `catalog.json`.

**Rationale:**
- catalog.json schema is clean and consistent
- New schema adds pipeline tracking fields (parse, translate, solve)
- Migration is straightforward (field mapping is 1:1 for existing fields)

### 2. Enhanced Error Structure

**Current:**
```json
{
  "convexity_status": "error",
  "verification_error": "Model exceeds demo license limits"
}
```

**Recommended:**
```json
{
  "convexity_status": "error",
  "error": {
    "type": "license_limit",
    "message": "Model exceeds demo license limits",
    "recoverable": true
  }
}
```

### 3. License-Limited Model Handling

**Recommendation:** Track separately with flag `license_limited: true`

- 10 models are blocked by demo license limits
- These could be verified with full GAMS license
- Sprint 14 should skip these for batch verification

### 4. Models Needing Reclassification

| Model | Current Status | Recommended |
|-------|----------------|-------------|
| chance | unknown | likely_convex (LP with status=2) |
| demo7 | unknown | likely_convex (LP with status=2) |
| immun | unknown | likely_convex (LP with status=2) |
| srcpm | unknown | likely_convex (LP with status=2) |

### 5. Schema Versioning

**Recommendation:** Increment to schema_version 2.0.0 for new database

- Breaking change: new nested structure for pipeline stages
- Add migration script to transform 1.0.0 → 2.0.0

---

## Quality Score Summary

| Category | Score | Notes |
|----------|-------|-------|
| Completeness | 10/10 | All required fields present |
| Consistency | 10/10 | Uniform naming, formats, types |
| Accuracy | 9/10 | 7 "unknown" could be reclassified |
| Documentation | 10/10 | All fields have clear purpose |
| **Overall** | **9.75/10** | **Excellent quality** |

---

## Appendix: Full Error Model List

### Compilation Errors (19 models)

dqq, gasoil, gqapsdp, kqkpsdp, methanol, pinene, pool, popdynm, qcp1, qp1, qp1x, qp2, qp3, qp4, qp5, qp7, sddp, t1000, trnspwlx

### No Solve Summary (15 models)

asyncloop, embmiex1, gussgrid, maxcut, mhw4dxx, netgen, prodsp, qfilter, scenmerge, sipres, sudoku, tanksize, trussm, weapon, weapons

### License Limited (10 models)

airsp, airsp2, andean, emfl, indus89, jbearing, minsurf, msm, phosdis, torsion

### Solver Errors (4 models)

guss2dim, gussex1, lmp1, lmp3

### Excluded - Infeasible (4 models)

alan, circpack, epscm, trigx

### Unknown Status (7 models)

chance, demo7, gancnsx, immun, minlphi, qalan, srcpm
