# Parse Rate Baseline for Sprint 14

**Task:** Sprint 14 Prep Task 6 - Analyze Parse Rate for Verified Models  
**Created:** 2026-01-01  
**Sample Size:** 30 models (stratified by type and file size)

---

## Executive Summary

This document establishes the baseline parse success rate for nlp2mcp on GAMSLIB models verified as convex in Sprint 13. The results inform Sprint 14 expectations for pipeline testing.

**Key Findings:**
- **Parse success rate:** 13.3% (4/30 models)
- **Average parse time:** 0.97 seconds per model
- **Primary blocker:** Syntax errors (77% of failures)
- **Projected batch time:** ~2.5 minutes for 160 models

---

## Methodology

### Sample Selection

A stratified sample of 30 models was selected from the 160 verified convex models:

| Type | Population | Sample | Sampling Strategy |
|------|------------|--------|-------------------|
| LP | 57 | 15 | Stratified by file size (smallest to largest) |
| NLP | 94 | 12 | Stratified by file size |
| QCP | 9 | 3 | Stratified by file size |
| **Total** | **160** | **30** | |

### Test Procedure

Each model was tested with:
```bash
python -m src.cli data/gamslib/raw/{model_id}.gms -o /tmp/parse_test.gms
```

- Timeout: 60 seconds
- Exit code 0 = success
- Non-zero exit code = failure (error captured)

---

## Results

### Overall Parse Rate

| Metric | Value |
|--------|-------|
| Total models tested | 30 |
| Successful parses | 4 |
| Failed parses | 26 |
| **Success rate** | **13.3%** |

### Parse Rate by Model Type

| Type | Tested | Successful | Rate |
|------|--------|------------|------|
| LP | 15 | 1 | 6.7% |
| NLP | 12 | 2 | 16.7% |
| QCP | 3 | 1 | 33.3% |

### Successful Models

| Model ID | Type | File Size | Parse Time |
|----------|------|-----------|------------|
| prodmix | LP | 1,222 bytes | 0.93s |
| rbrock | NLP | 531 bytes | 0.88s |
| hs62 | NLP | 1,233 bytes | 0.97s |
| himmel11 | QCP | 1,130 bytes | 1.00s |

**Observation:** All successful models are small (≤1,233 bytes), suggesting simpler syntax.

### Performance Metrics

| Metric | Value |
|--------|-------|
| Average parse time (success) | 0.95 seconds |
| Average parse time (all) | 0.97 seconds |
| Minimum parse time | 0.71 seconds |
| Maximum parse time | 2.58 seconds |
| No timeouts | 0/30 |

---

## Failure Analysis

### Failure Categories

| Category | Count | Percentage |
|----------|-------|------------|
| syntax_error | 20 | 77% |
| no_objective | 2 | 8% |
| unsupported_function | 2 | 8% |
| domain_error | 1 | 4% |
| undefined_variable | 1 | 4% |

### Category Details

#### 1. Syntax Errors (20 models, 77%)

Parser grammar failures - the GAMS syntax is not recognized by nlp2mcp.

**Affected models:** sroute, ajax, kand, imsl, aircraft, pdi, demo1, mexss, agreste, sarf, dinam, ps3_s_gic, ps10_s, mathopt4, mlbeta, gussrisk, launch, moncge, nonsharp, springchain

**Example errors:**
- `Parse error at line 15, column 69: Unexpected character`
- `Parse error at line 81, column 9: Unexpected character`

**Root cause:** GAMSLIB models use GAMS syntax features not yet supported by the nlp2mcp parser.

#### 2. No Objective Function (2 models, 8%)

Model parsed but has no objective function defined.

**Affected models:** danwolfe, elec

**Error:** `Model has no objective function defined`

**Root cause:** These models may use different optimization structures (e.g., equilibrium models) or define objectives differently.

#### 3. Unsupported Functions (2 models, 8%)

Parser succeeded but differentiation is not implemented for certain functions.

**Affected models:** orani, maxmin

**Errors:**
- `Differentiation not yet implemented for function 'gamma'`
- `Differentiation not yet implemented for function 'smin'`

**Root cause:** The AD (automatic differentiation) module doesn't support these GAMS functions.

#### 4. Domain Errors (1 model, 4%)

Variable domain incompatibility during IR construction.

**Affected model:** robert

**Error:** `Incompatible domains for summation: variable domain ('p',`

**Root cause:** Complex set/domain handling not supported.

#### 5. Undefined Variable (1 model, 4%)

Objective variable referenced but not defined.

**Affected model:** trussm

**Error:** `Objective variable 'tau' is not defined by any equation`

**Root cause:** Model structure issue or parsing incomplete.

---

## Projections for Sprint 14

### Batch Verification Timing

| Metric | Calculation | Estimate |
|--------|-------------|----------|
| Models to test | 160 verified convex | - |
| Average time per model | 0.97 seconds | - |
| **Estimated batch time** | 160 × 0.97s | **~2.6 minutes** |
| With overhead (10%) | 2.6 × 1.1 | **~3 minutes** |

**Conclusion:** Batch verification of all 160 models is fast (~3 minutes), well under the 2-hour concern.

### Projected Parse Rate for Full Corpus

Based on stratified sample results:

| Type | Sample Rate | Population | Projected Success |
|------|-------------|------------|-------------------|
| LP | 6.7% | 57 | ~4 models |
| NLP | 16.7% | 94 | ~16 models |
| QCP | 33.3% | 9 | ~3 models |
| **Total** | - | 160 | **~23 models (14%)** |

**Note:** Sample size is small; actual results may vary. The stratified sampling by file size may over-represent complex models since larger files tend to have more unsupported syntax.

---

## Recommendations for Sprint 14

### 1. Focus on Successful Models First

The 4 models that successfully parsed should be prioritized for full pipeline testing (translate + solve). This provides immediate end-to-end validation.

### 2. Categorize All Parse Failures

Run batch parse on all 160 models to:
- Identify all successful models (estimated ~23)
- Categorize failures for parser improvement roadmap
- Track in gamslib_status.json with error categories

### 3. Track Error Categories in Schema

The database schema (DRAFT_SCHEMA.json) already supports structured errors with categories:
- `syntax_error` - Parser grammar failures
- `unsupported_feature` - Unsupported GAMS functions
- `missing_include` - Include file issues
- `internal_error` - Other errors

### 4. Consider Parser Enhancements (Future)

Top blockers by impact:
1. **Syntax errors (77%)** - Requires parser grammar extensions
2. **Unsupported functions (8%)** - Add `gamma`, `smin` to AD module
3. **No objective (8%)** - May be inherent model limitations

### 5. Set Realistic KPIs

Given ~13% parse rate:
- **Parse success target:** 15-25 models from 160 verified
- **Full pipeline success:** Subset of parsed models
- **Track improvement:** Measure parse rate increase over sprints

---

## Test Details

### Full Results Table

| Model ID | Type | Size (bytes) | Status | Time (s) | Error Category |
|----------|------|--------------|--------|----------|----------------|
| prodmix | LP | 1,222 | success | 0.93 | - |
| robert | LP | 1,650 | failure | 0.94 | domain_error |
| sroute | LP | 1,795 | failure | 0.71 | syntax_error |
| ajax | LP | 2,651 | failure | 0.73 | syntax_error |
| kand | LP | 2,918 | failure | 0.79 | syntax_error |
| imsl | LP | 3,287 | failure | 0.91 | syntax_error |
| aircraft | LP | 3,696 | failure | 0.98 | syntax_error |
| pdi | LP | 3,991 | failure | 0.96 | syntax_error |
| demo1 | LP | 5,202 | failure | 1.50 | syntax_error |
| danwolfe | LP | 6,337 | failure | 0.90 | no_objective |
| mexss | LP | 7,511 | failure | 0.79 | syntax_error |
| orani | LP | 8,542 | failure | 2.58 | unsupported_function |
| agreste | LP | 13,310 | failure | 0.81 | syntax_error |
| sarf | LP | 25,746 | failure | 0.87 | syntax_error |
| dinam | LP | 45,806 | failure | 0.85 | syntax_error |
| rbrock | NLP | 531 | success | 0.88 | - |
| hs62 | NLP | 1,233 | success | 0.97 | - |
| ps3_s_gic | NLP | 1,371 | failure | 0.80 | syntax_error |
| ps10_s | NLP | 1,702 | failure | 0.84 | syntax_error |
| elec | NLP | 1,938 | failure | 0.80 | no_objective |
| mathopt4 | NLP | 2,209 | failure | 1.06 | syntax_error |
| mlbeta | NLP | 2,880 | failure | 0.93 | syntax_error |
| maxmin | NLP | 3,350 | failure | 1.13 | unsupported_function |
| gussrisk | NLP | 4,420 | failure | 0.82 | syntax_error |
| launch | NLP | 6,234 | failure | 0.89 | syntax_error |
| moncge | NLP | 11,664 | failure | 1.47 | syntax_error |
| nonsharp | NLP | 21,751 | failure | 1.11 | syntax_error |
| himmel11 | QCP | 1,130 | success | 1.00 | - |
| springchain | QCP | 2,270 | failure | 0.85 | syntax_error |
| trussm | QCP | 3,777 | failure | 1.24 | undefined_variable |

---

## Unknowns Verified

This analysis verifies the following unknowns from KNOWN_UNKNOWNS.md:

| ID | Question | Finding |
|----|----------|---------|
| 1.1 | How long will batch verification take? | ~3 minutes for 160 models (~1s per model) |
| 1.2 | What percentage will parse successfully? | ~13% (4/30 sample, projected 14% for full corpus) |
| 1.3 | License limit errors during parsing? | None observed - license limits only affect GAMS solve, not nlp2mcp parsing |

---

## Document History

- 2026-01-01: Initial creation (Sprint 14 Prep Task 6)
