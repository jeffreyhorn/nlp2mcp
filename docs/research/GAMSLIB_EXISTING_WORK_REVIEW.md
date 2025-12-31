# Review of Existing nlp2mcp GAMSLIB Work

**Created:** December 31, 2025  
**Sprint 13 Prep Task 6**  
**Purpose:** Inventory existing GAMSLIB-related code and documentation to identify reusable components and gaps for Sprint 13

---

## Executive Summary

This document reviews all existing GAMSLIB-related work in nlp2mcp from EPIC 2 (Sprints 6-12) to inform Sprint 13 development. The review identified:

- **Extensive existing infrastructure** that can be reused
- **100% parse rate achieved** for Tier 1 GAMSLIB models
- **One significant gap** requiring Sprint 13 attention: `solver_type` not stored in ModelIR
- **Reusable scripts** for downloading and ingesting models

**Key Finding:** Sprint 13 can build on a solid foundation rather than starting from scratch.

---

## 1. Inventory of Existing GAMSLIB Files

### 1.1 GAMSLIB-Named Files and Directories

| Path | Type | Description |
|------|------|-------------|
| `tests/fixtures/gamslib/` | Directory | Contains 10 Tier 1 test models |
| `scripts/download_gamslib_nlp.sh` | Script | Downloads GAMSLIB NLP models |
| `scripts/ingest_gamslib.py` | Script | Parses models and generates reports |
| `docs/status/GAMSLIB_CONVERSION_STATUS.md` | Status | Dashboard showing conversion progress |
| `docs/research/gamslib_parse_errors.md` | Research | Sprint 6 parse error analysis |
| `docs/research/gamslib_kpi_definitions.md` | Research | KPI definitions for ingestion |
| `docs/research/ingestion_schedule.md` | Research | Ingestion timeline planning |
| `docs/research/GAMSLIB_NLP_CATALOG.md` | Catalog | NLP model catalog |
| `docs/research/GAMSLIB_MODEL_TYPES.md` | Research | Task 4 model type survey |
| `docs/research/GAMSLIB_ACCESS_RESEARCH.md` | Research | Task 2 access research |
| `reports/gamslib_ingestion_sprint6.json` | Report | Sprint 6 ingestion results |

### 1.2 Tier 1 Test Models (tests/fixtures/gamslib/)

The following 10 models are available as test fixtures:

| Model | Type | Size | Parse Status |
|-------|------|------|--------------|
| circle.gms | NLP | 1,297 bytes | SUCCESS |
| himmel16.gms | NLP | 1,056 bytes | SUCCESS |
| hs62.gms | NLP | 1,124 bytes | SUCCESS |
| mathopt1.gms | NLP | 1,315 bytes | SUCCESS |
| maxmin.gms | NLP | 1,891 bytes | SUCCESS |
| mhw4d.gms | NLP | 729 bytes | SUCCESS |
| mhw4dx.gms | NLP | 2,101 bytes | SUCCESS |
| mingamma.gms | NLP | 1,021 bytes | SUCCESS |
| rbrock.gms | NLP | 531 bytes | SUCCESS |
| trig.gms | NLP | 456 bytes | SUCCESS |

**Result:** All 10 Tier 1 models parse successfully (100% parse rate).

---

## 2. Review of EPIC 2 GAMSLIB Research

### 2.1 Sprint 6: Initial GAMSLIB Integration

**Document:** `docs/research/gamslib_parse_errors.md`

**Key Findings:**
- Initial parse rate was 0% (all 10 Tier 1 models failed)
- Common error patterns identified:
  - Variable level assignment (`.l` suffix)
  - Compiler directives (`$if`, `$set`)
  - Set ranges (`/1*6/`)
  - Model equation lists
- All errors were grammar/parser issues, not fundamental limitations

**Sprint 6 Outcome:** Grammar and parser fixes implemented to address all identified issues.

### 2.2 KPI Definitions

**Document:** `docs/research/gamslib_kpi_definitions.md`

**4-KPI System:**
| KPI | Description | Conservative Target |
|-----|-------------|---------------------|
| parse% | Models that parse without error | ≥50% |
| convert% | Parsed models that convert to MCP | ≥80% |
| solve% | Converted models that solve with PATH | ≥50% |
| e2e% | Models completing full pipeline | ≥20% |

**Important:** KPIs are cascading - each depends on prior stage success.

**Python Implementation:**
```python
@dataclass
class ModelResult:
    model_name: str
    parse_status: str
    convert_status: str | None
    solve_status: str | None
    objective_value: float | None

@dataclass
class BenchmarkKPIs:
    parse_success: int
    parse_failed: int
    convert_success: int
    convert_failed: int
    solve_success: int
    solve_failed: int
```

### 2.3 Ingestion Schedule

**Document:** `docs/research/ingestion_schedule.md`

- Sprint 6 used manual ingestion for initial testing
- Automated ingestion script created for repeatability
- Schedule planned for progressive expansion (Tier 1 → Tier 2 → full corpus)

### 2.4 Current Status Dashboard

**Document:** `docs/status/GAMSLIB_CONVERSION_STATUS.md`

**Sprint 8 Status:**
- Parse Rate: 100% (10/10 models)
- Convert Rate: Not yet implemented
- Solve Rate: Not yet implemented
- E2E Rate: Not yet implemented

---

## 3. Review of Existing Scripts

### 3.1 Download Script: `scripts/download_gamslib_nlp.sh`

**Purpose:** Downloads GAMSLIB models from the GAMS website

**Features:**
- Downloads from `https://www.gams.com/latest/gamslib_ml/{name}.{seq}`
- Supports `--force`, `--dry-run`, `--clean` options
- Creates manifest.csv with download status
- Validates downloaded files contain GAMS keywords
- Retry logic with 3 attempts per model
- Color-coded console output

**Tier 1 Models Configured:**
```bash
TIER1_MODELS=(
    "trig:261:Simple Trigonometric Example"
    "rbrock:83:Rosenbrock Test Function"
    "himmel16:36:Area of Hexagon Test Problem"
    "hs62:264:Hock-Schittkowski Problem 62"
    "mhw4d:84:Nonlinear Test Problem"
    "mhw4dx:267:MHW4D with Additional Tests"
    "circle:201:Circle Enclosing Points - SNOPT Example"
    "maxmin:263:Max Min Location of Points in Unit Square"
    "mathopt1:255:MathOptimizer Example 1"
    "mingamma:299:Minimal y of GAMMA(x)"
)
```

**Reusability:** High - can extend with additional models for Sprint 13.

### 3.2 Ingestion Script: `scripts/ingest_gamslib.py`

**Purpose:** Parses GAMSLIB models and generates JSON reports

**Features:**
- Uses `parse_model_file()` from `src/ir/parser`
- Calculates parse progress metrics (percentage, lines parsed/total)
- Extracts missing features from parse errors
- Generates JSON report with ModelResult dataclasses
- Optional Markdown dashboard generation

**Key Functions:**
```python
def parse_model(gms_path: Path) -> ModelResult:
    """Parse a model and return status with progress metrics."""

def calculate_kpis(models: list[ModelResult]) -> dict:
    """Calculate KPI metrics from results."""

def generate_dashboard(report, output_path, json_report_path):
    """Generate Markdown dashboard from report."""
```

**Reusability:** High - can extend for convert% and solve% metrics.

---

## 4. Parser Capabilities Analysis

### 4.1 Model Type Parsing

**Grammar:** `src/gams/gams_grammar.lark`

The grammar correctly parses the `solver_type` from solve statements:

```lark
solve_stmt: "Solve"i ID obj_sense ID "using"i solver_type SEMI     -> solve
          | "Solve"i ID "using"i solver_type obj_sense ID SEMI     -> solve

solver_type: /(?i:nlp|dnlp|minlp|mip|lp|mcp|cns|qcp|rmip|rminlp)\b/
```

**Supported Types:** NLP, DNLP, MINLP, MIP, LP, MCP, CNS, QCP, RMIP, RMINLP

### 4.2 Gap Identified: solver_type Not Stored in ModelIR

**Issue:** The `solver_type` is parsed by the grammar but NOT stored in ModelIR.

**Current ModelIR fields (from `src/ir/model_ir.py`):**
```python
@dataclass
class ModelIR:
    # Solve info
    declared_model: str | None = None
    model_equations: list[str] = field(default_factory=list)
    model_uses_all: bool = False
    model_name: str | None = None
    objective: ObjectiveIR | None = None
    # NOTE: solver_type NOT stored!
```

**Impact on Sprint 13:**
- Cannot determine model type (LP/NLP/QCP) from parsed ModelIR
- Need to either:
  1. Add `solver_type` field to ModelIR (recommended)
  2. Re-parse solve statement separately to extract type

**Recommendation:** Add `solver_type: str | None = None` to ModelIR and update transformer to populate it during parsing.

### 4.3 Data Structure Serialization

**Existing JSON Support:**
- `src/ir/diagnostics.py` uses `dataclasses.asdict()` for JSON serialization
- `scripts/ingest_gamslib.py` uses same pattern for ModelResult

**Recommendation for Sprint 13 Catalog:**
- Use standalone JSON structure (not tied to ModelIR)
- ModelIR is for internal representation, catalog is for external metadata
- Follow pattern from `ingest_gamslib.py` with dedicated dataclasses

---

## 5. Summary of Reusable Components

### 5.1 Fully Reusable (No Changes Needed)

| Component | Location | Sprint 13 Use |
|-----------|----------|---------------|
| Download script | `scripts/download_gamslib_nlp.sh` | Extend for all 115 candidate models |
| Tier 1 fixtures | `tests/fixtures/gamslib/` | Baseline test set |
| KPI framework | `gamslib_kpi_definitions.md` | Adopt for Sprint 13 metrics |
| Status dashboard | `GAMSLIB_CONVERSION_STATUS.md` | Update format for Sprint 13 |

### 5.2 Reusable with Extension

| Component | Location | Required Changes |
|-----------|----------|------------------|
| Ingestion script | `scripts/ingest_gamslib.py` | Add solve status, objective value |
| ModelResult class | `ingest_gamslib.py` | Add convexity_status field |
| Parse progress | `src/utils/parse_progress.py` | No changes, already comprehensive |

### 5.3 Requires New Development

| Component | Sprint 13 Task | Notes |
|-----------|----------------|-------|
| Convexity verification | Task 5 complete | Design documented, implementation needed |
| solver_type in ModelIR | Sprint 13 Day 1-2 | Simple addition to dataclass and transformer |
| GAMS execution framework | Sprint 13 Day 5-6 | New functionality for running GAMS and parsing .lst |
| JSON catalog | Task 7 pending | New schema for model metadata |

---

## 6. Verification of Unknowns 5.1, 5.2, 5.3

### Unknown 5.1: What GAMSLIB work exists from EPIC 2?

**Status:** VERIFIED

**Findings:**
- Extensive infrastructure exists from EPIC 2 Sprints 6-12
- 10 Tier 1 models in test fixtures with 100% parse rate
- Reusable download and ingestion scripts
- KPI framework and status dashboard established
- Research documents provide baseline and lessons learned

**Evidence:** See Section 1 (Inventory) and Section 2 (Research Review)

### Unknown 5.2: How does nlp2mcp currently parse model type declarations?

**Status:** VERIFIED

**Findings:**
- Grammar parses `solver_type` from solve statements correctly
- Supports: NLP, DNLP, MINLP, MIP, LP, MCP, CNS, QCP, RMIP, RMINLP
- **GAP:** `solver_type` is NOT stored in ModelIR
- Type can be extracted during parsing but requires ModelIR extension

**Evidence:**
- `src/gams/gams_grammar.lark` lines 72-74 (solve_stmt and solver_type rules)
- `src/ir/model_ir.py` (ModelIR class lacks solver_type field)

**Recommendation:** Add `solver_type: str | None = None` to ModelIR

### Unknown 5.3: Should the JSON catalog use existing nlp2mcp data structures?

**Status:** VERIFIED

**Findings:**
- JSON catalog should be **standalone**, not tied to ModelIR
- ModelIR is internal representation optimized for transformation
- Catalog is external metadata for tracking and reporting
- Existing pattern: `ingest_gamslib.py` uses dedicated dataclasses (ModelResult)
- `dataclasses.asdict()` works well for JSON serialization

**Recommendation:**
- Create dedicated catalog dataclasses (e.g., `CatalogEntry`, `ModelCatalog`)
- Use `dataclasses.asdict()` for JSON serialization
- Keep catalog independent of ModelIR for flexibility

**Evidence:**
- `scripts/ingest_gamslib.py` lines 25-40 (ModelResult, IngestionReport classes)
- `src/ir/diagnostics.py` (DiagnosticReport pattern)

---

## 7. Gaps and Required Sprint 13 Work

### 7.1 Critical Gap: solver_type Not in ModelIR

**Impact:** Cannot determine if parsed model is LP, NLP, or QCP

**Fix (estimated 1-2 hours):**
1. Add to `src/ir/model_ir.py`:
   ```python
   solver_type: str | None = None  # LP, NLP, QCP, etc.
   ```
2. Update transformer in `src/ir/transformer.py` to populate during solve statement processing

### 7.2 Missing: GAMS Execution Framework

**Need:** Execute GAMS models and capture solver output

**Components Required:**
- GAMS execution wrapper (subprocess call)
- .lst file parser for MODEL STATUS, SOLVER STATUS, objective
- Timeout handling
- Error capture and logging

**Reference:** Design documented in `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`

### 7.3 Missing: Convexity Classification Logic

**Need:** Classify models based on solver output

**Components Required:**
- Decision tree implementation
- Classification categories (verified_convex, likely_convex, etc.)
- Batch processing support

**Reference:** Algorithm documented in `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`

### 7.4 Missing: Full Model Catalog

**Need:** Catalog of 115 candidate models with metadata

**Components Required:**
- JSON schema (Task 7)
- Catalog population script
- Web scraping or gamslib command expansion

---

## 8. Recommendations for Sprint 13

### 8.1 Day 1-2: Foundation

1. Add `solver_type` to ModelIR (critical gap fix)
2. Extend download script with all 115 candidate models
3. Create JSON catalog schema (Task 7)

### 8.2 Day 3-4: Download Infrastructure

1. Download all LP models (57)
2. Download all NLP models (49)
3. Download all QCP models (9)
4. Validate downloads and create catalog

### 8.3 Day 5-6: Convexity Verification

1. Implement GAMS execution framework
2. Implement .lst file parsing
3. Implement classification logic
4. Run initial verification on Tier 1 models

### 8.4 Day 7-10: Integration and Testing

1. Batch process all models
2. Generate verification report
3. Update status dashboard
4. Documentation and sprint review

---

## Appendix: File Locations Quick Reference

```
nlp2mcp/
├── scripts/
│   ├── download_gamslib_nlp.sh     # Reusable download script
│   └── ingest_gamslib.py           # Reusable ingestion script
├── src/
│   ├── gams/
│   │   └── gams_grammar.lark       # Grammar with solver_type
│   ├── ir/
│   │   ├── model_ir.py             # ModelIR (needs solver_type)
│   │   └── transformer.py          # Updates needed for solver_type
│   └── utils/
│       └── parse_progress.py       # Reusable progress metrics
├── tests/fixtures/gamslib/         # 10 Tier 1 models
├── docs/
│   ├── research/
│   │   ├── gamslib_parse_errors.md
│   │   ├── gamslib_kpi_definitions.md
│   │   ├── ingestion_schedule.md
│   │   ├── GAMSLIB_MODEL_TYPES.md
│   │   ├── GAMSLIB_ACCESS_RESEARCH.md
│   │   └── CONVEXITY_VERIFICATION_DESIGN.md
│   └── status/
│       └── GAMSLIB_CONVERSION_STATUS.md
└── reports/
    └── gamslib_ingestion_sprint6.json
```

---

## Changelog

- **2025-12-31:** Initial document created for Sprint 13 Prep Task 6
