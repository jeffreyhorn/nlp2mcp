# GAMSLIB Access Research

**Date:** December 29, 2025  
**Status:** Complete  
**Purpose:** Research GAMSLIB structure, organization, and access methods to inform Sprint 13 download script development

---

## Executive Summary

GAMSLIB (GAMS Model Library) provides **437 models** accessible via two methods:

1. **Command-line tool (`gamslib`)**: Recommended approach - fast, reliable, no authentication required
2. **Web interface**: Alternative for browsing and reference, direct .gms file downloads available

**Recommendation:** Use the `gamslib` command-line tool for Sprint 13 download infrastructure. It's faster, simpler, and doesn't require network access or web scraping.

---

## 1. GAMSLIB Overview

### Library Statistics
- **Total Models:** 437
- **Model Types:** LP, NLP, MIP, QCP, MINLP, MCP, EMP, DNLP, CNS, MPSGE
- **Subject Categories:** Management Science, Applied General Equilibrium, Finance, Engineering, Agricultural Economics, Statistics, Mathematics, Energy Economics, Chemical Engineering, Contract Theory

### Model Identification
Each model has:
- **Name:** Unique identifier (e.g., `trnsport`, `circle`, `chem`)
- **Sequence Number:** Integer 1-437 (e.g., SEQ=1 for trnsport)
- **Type:** Problem classification (LP, NLP, MIP, etc.)
- **Description:** Brief text description

---

## 2. Access Method 1: Command-Line Tool (`gamslib`)

### Availability
```bash
$ which gamslib
/Library/Frameworks/GAMS.framework/Versions/51/Resources/gamslib
```

The `gamslib` command is included with GAMS installation and available on PATH.

### Usage Syntax
```bash
gamslib [-lib glbfile] [-q(uiet)] <modelname | modelnum> [target]
```

### Extraction Examples

**By model name:**
```bash
$ gamslib trnsport
Copy ASCII : trnsport.gms
```

**By sequence number:**
```bash
$ gamslib 1
Copy ASCII : trnsport.gms
```

**To specific directory:**
```bash
$ gamslib trnsport /path/to/output/trnsport.gms
```

### Generate Model List
```bash
$ gamslib -g
Writing GAMS data for model to: gamslib.gms
```

This creates `gamslib.gms` containing all model names and descriptions as GAMS data statements.

### Advantages
- **Fast:** Extracts from local library file (no network required)
- **Reliable:** No authentication, rate limits, or web scraping needed
- **Complete:** Access to all 437 models
- **Consistent:** Same output format regardless of GAMS version
- **Scriptable:** Easy to batch extract multiple models

### Limitations
- Requires GAMS installation
- No filtering by model type (must filter after extraction)

---

## 3. Access Method 2: Web Interface

### Main URL
```
https://www.gams.com/latest/gamslib_ml/libhtml/
```

### Navigation Structure
- **Main index:** DataTable with sorting and search
- **By Type:** Filter by LP, NLP, MIP, etc.
- **By Subject:** Filter by domain category
- **Version selector:** Access different GAMS versions (25.1-52)

### URL Patterns

**Model index:**
```
https://www.gams.com/latest/gamslib_ml/libhtml/
```

**Individual model page:**
```
https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_{modelname}.html
```

Example: `https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html`

**Direct .gms file download:**
```
https://www.gams.com/latest/gamslib_ml/{modelname}.{seq}
```

Example: `https://www.gams.com/latest/gamslib_ml/trnsport.1`

### Model Page Metadata
Each model page displays:
- **Title:** Model name with sequence number
- **Type:** "Small Model of Type: LP" (or NLP, MIP, etc.)
- **Description:** Problem description
- **Main file:** Link to .gms file
- **Keywords:** Search terms
- **References:** Academic citations
- **Full source code:** Displayed inline

### Authentication
- **None required:** All models are publicly accessible
- **No rate limiting observed:** Multiple rapid requests succeeded

### Advantages
- Browse and search without GAMS installation
- View model descriptions and metadata
- Access to historical versions

### Limitations
- Requires network access
- Web scraping needed for batch downloads
- URL structure may change between GAMS versions

---

## 4. Model Dependencies

### $include and External Files

Testing the first 50 models found **no $include statements** or external file dependencies:

```bash
$ grep -l '\$include\|\$gdxin' *.gms
# No matches
```

### Findings
- Most GAMSLIB models are **self-contained**
- All data is embedded inline using Set, Parameter, and Table statements
- Some models use `$call` for external program execution (not data dependencies)
- Models in the library are designed to be standalone examples

### Recommendation
Treat GAMSLIB models as self-contained. If a model with dependencies is encountered, flag it for manual review rather than attempting to resolve dependencies automatically.

---

## 5. Version Stability

### Web URL Structure
The URL pattern `/latest/gamslib_ml/` redirects to the current GAMS version. Version-specific URLs are also available:

```
https://www.gams.com/47/gamslib_ml/libhtml/
https://www.gams.com/51/gamslib_ml/libhtml/
https://www.gams.com/52/gamslib_ml/libhtml/
```

### Stability Assessment
- **URL structure:** Stable since at least GAMS 25.1
- **Model naming:** Consistent across versions
- **Model content:** May change between versions (bug fixes, improvements)
- **Sequence numbers:** Stable for existing models; new models added at end

### Recommendation
Use `/latest/` for web access to always get current version. For reproducibility, document the GAMS version used.

---

## 6. Sample Models Downloaded

Successfully extracted 5 sample models for testing:

| Model | Type | Size | Sequence |
|-------|------|------|----------|
| trnsport.gms | LP | 1,751 bytes | 1 |
| blend.gms | LP | 1,699 bytes | 2 |
| circle.gms | NLP | 1,297 bytes | 201 |
| chem.gms | NLP | 1,625 bytes | 21 |
| rbrock.gms | NLP | 531 bytes | 141 |

All models:
- Extracted successfully via `gamslib` command
- Are self-contained (no $include dependencies)
- Include embedded data and complete model definitions

---

## 7. Recommendations for Sprint 13

### Primary Approach: Use `gamslib` Command

```bash
# Extract single model
gamslib trnsport output/trnsport.gms

# Extract by sequence number (useful for iteration)
gamslib 1 output/trnsport.gms

# Generate complete model list
gamslib -g  # Creates gamslib.gms with all model names
```

### Download Script Design

1. **Model Discovery:**
   - Run `gamslib -g` to generate complete model list
   - Parse `gamslib.gms` to extract model names and descriptions
   - Alternatively, iterate through sequence numbers 1-437

2. **Model Extraction:**
   - Use `gamslib <name>` for each model
   - Extract to `data/gamslib/models/` directory
   - Verify extraction success (check file exists)

3. **Type Classification:**
   - Parse `$title` line for SEQ number
   - Parse `Solve ... using TYPE ...` statement for model type
   - Store metadata in JSON catalog

4. **Filtering:**
   - After extraction, filter by model type
   - Include: LP, NLP, QCP
   - Exclude: MIP, MINLP, MPEC, MCP, CNS, DNLP, MPSGE

### Alternative: Web Download (if needed)

```bash
# Direct download pattern
curl -O "https://www.gams.com/latest/gamslib_ml/trnsport.1"
mv trnsport.1 trnsport.gms
```

Use web download only if `gamslib` command is unavailable.

---

## 8. Unknowns Verified

| Unknown | Finding | Status |
|---------|---------|--------|
| 1.1: URL structure | `https://www.gams.com/latest/gamslib_ml/{name}.{seq}` | VERIFIED |
| 1.2: gamslib command | Works: `gamslib <name\|seq> [target]` | VERIFIED |
| 1.3: Metadata available | Type, description, keywords, references | VERIFIED |
| 1.5: Dependencies | No $include in first 50 models tested | VERIFIED |
| 1.6: Version stability | URL structure stable since GAMS 25.1 | VERIFIED |

---

## Appendix: Command Reference

### gamslib Usage
```
Usage:
  gamslib [-lib glbfile] [-q(uiet)] <modelname | modelnum> [target]
         Extract files for model
  gamslib [-lib glbfile] -i
         Convert library to ini format
  gamslib [-lib glbfile] -g
         Generate GAMS data statements
```

### Sample Extraction Session
```bash
$ mkdir -p data/gamslib/models
$ cd data/gamslib/models
$ gamslib trnsport
Copy ASCII : trnsport.gms
$ gamslib circle
Copy ASCII : circle.gms
$ gamslib chem
Copy ASCII : chem.gms
$ ls -la
total 16
-rw-r--r--  1 user  staff  1625 Dec 29 18:11 chem.gms
-rw-r--r--  1 user  staff  1297 Dec 29 18:11 circle.gms
-rw-r--r--  1 user  staff  1751 Dec 29 18:10 trnsport.gms
```

---

## Changelog

- **2025-12-29:** Initial research complete
