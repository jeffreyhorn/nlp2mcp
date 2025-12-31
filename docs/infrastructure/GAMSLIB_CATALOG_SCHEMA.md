# GAMSLIB Catalog Schema Documentation

**Created:** December 31, 2025  
**Sprint 13 Prep Task 7**  
**Schema Version:** 0.1.0  
**Status:** Draft for Sprint 13

---

## Overview

This document describes the JSON schema for the GAMSLIB model catalog used in nlp2mcp. The catalog stores metadata about GAMSLIB models and their status through the nlp2mcp pipeline.

**Design Principles:**
1. **Minimal for Sprint 13:** Include only fields needed for model discovery and download
2. **Extensible for Sprint 14:** Structure supports adding convexity verification and pipeline status
3. **Standalone Structure:** Not tied to ModelIR - catalog is for external metadata tracking
4. **JSON Serializable:** Uses standard Python types compatible with `json.dump()`

---

## Schema Structure

### Top-Level Structure

```json
{
  "schema_version": "0.1.0",
  "created_date": "2025-12-31T00:00:00Z",
  "updated_date": "2025-12-31T12:00:00Z",
  "gams_version": "51.3.0",
  "total_models": 115,
  "models": [...]
}
```

### Model Entry Structure (Sprint 13)

```json
{
  "model_id": "trnsport",
  "sequence_number": 1,
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP",
  "source_url": "https://www.gams.com/latest/gamslib_ml/trnsport.1",
  "web_page_url": "https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html",
  "description": "Demonstrates a simple transportation model",
  "keywords": ["linear programming", "transportation problem", "scheduling"],
  "download_status": "pending",
  "download_date": null,
  "file_path": null,
  "file_size_bytes": null,
  "notes": ""
}
```

---

## Field Descriptions

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | Yes | Semantic version of the schema (e.g., "0.1.0") |
| `created_date` | string | Yes | ISO 8601 timestamp when catalog was created |
| `updated_date` | string | Yes | ISO 8601 timestamp of last update |
| `gams_version` | string | No | GAMS version used for model discovery |
| `total_models` | integer | Yes | Total number of models in catalog |
| `models` | array | Yes | Array of model entry objects |

### Model Entry Fields

#### Identification Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_id` | string | Yes | Unique identifier (lowercase model name, e.g., "trnsport") |
| `sequence_number` | integer | Yes | GAMSLIB sequence number (used in download URL) |
| `model_name` | string | Yes | Human-readable model name from GAMSLIB |

#### Type and Classification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gamslib_type` | string | Yes | Model type as declared in GAMSLIB (LP, NLP, QCP, etc.) |

**Valid values for `gamslib_type`:**
- `LP` - Linear Program (always convex)
- `NLP` - Nonlinear Program (requires convexity verification)
- `QCP` - Quadratically Constrained Program (requires convexity verification)
- `MIP` - Mixed Integer Program (excluded)
- `MINLP` - Mixed Integer Nonlinear Program (excluded)
- `MIQCP` - Mixed Integer QCP (excluded)
- `MCP` - Mixed Complementarity Problem (excluded)
- `MPEC` - Mathematical Program with Equilibrium Constraints (excluded)
- `CNS` - Constrained Nonlinear System (excluded)
- `DNLP` - Discontinuous NLP (excluded)
- `EMP` - Extended Mathematical Program (excluded)
- `MPSGE` - General Equilibrium (excluded)

#### Source Information

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_url` | string | Yes | Direct download URL for .gms file |
| `web_page_url` | string | No | URL to GAMSLIB documentation page |
| `description` | string | No | Brief description from GAMSLIB |
| `keywords` | array | No | List of keywords/tags from GAMSLIB |

#### Download Status

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `download_status` | string | Yes | Current download status |
| `download_date` | string | No | ISO 8601 timestamp of successful download |
| `file_path` | string | No | Relative path to downloaded .gms file |
| `file_size_bytes` | integer | No | Size of downloaded file in bytes |

**Valid values for `download_status`:**
- `pending` - Not yet downloaded
- `downloaded` - Successfully downloaded
- `failed` - Download failed (see notes for reason)
- `excluded` - Excluded from corpus (wrong type, dependencies, etc.)

#### Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `notes` | string | No | Free-form notes about the model |

---

## Sprint 14 Extension Points

The schema is designed to be extended in Sprint 14 with additional fields for:

### Convexity Verification (Sprint 14)

```json
{
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2025-01-15T10:30:00Z",
    "solver_used": "CONOPT",
    "model_status": 1,
    "solver_status": 1,
    "objective_value": 153.675,
    "solve_time_seconds": 0.05,
    "notes": ""
  }
}
```

**Planned `convexity.status` values:**
- `verified_convex` - LP with MODEL STATUS 1 (proven global optimum)
- `likely_convex` - NLP/QCP with STATUS 1 or 2 (local solver, probably convex)
- `non_convex` - Known non-convex (has non-convex functions)
- `excluded` - Infeasible, unbounded, or error
- `pending` - Not yet verified
- `unknown` - Verification inconclusive

### Pipeline Status (Sprint 14)

```json
{
  "pipeline": {
    "parse_status": "success",
    "parse_date": "2025-01-16T09:00:00Z",
    "parse_error": null,
    "convert_status": "success",
    "convert_date": "2025-01-16T09:01:00Z",
    "convert_error": null,
    "solve_status": "success",
    "solve_date": "2025-01-16T09:02:00Z",
    "solve_error": null,
    "nlp2mcp_version": "0.1.0"
  }
}
```

**Planned status values:**
- `pending` - Not yet attempted
- `success` - Stage completed successfully
- `failed` - Stage failed (see error field)
- `skipped` - Stage skipped (e.g., previous stage failed)

### Version Tracking (Sprint 14)

```json
{
  "versions": {
    "gams_version": "51.3.0",
    "nlp2mcp_version": "0.1.0",
    "last_tested": "2025-01-16T09:02:00Z"
  }
}
```

---

## Python Data Classes

The catalog uses standalone dataclasses following the pattern from `scripts/ingest_gamslib.py`:

```python
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any
import json

@dataclass
class ModelEntry:
    """Single model entry in the GAMSLIB catalog."""
    
    # Identification
    model_id: str
    sequence_number: int
    model_name: str
    
    # Type and classification
    gamslib_type: str
    
    # Source information
    source_url: str
    web_page_url: str | None = None
    description: str | None = None
    keywords: list[str] = field(default_factory=list)
    
    # Download status
    download_status: str = "pending"  # pending, downloaded, failed, excluded
    download_date: str | None = None
    file_path: str | None = None
    file_size_bytes: int | None = None
    
    # Metadata
    notes: str = ""


@dataclass
class GamslibCatalog:
    """GAMSLIB model catalog."""
    
    schema_version: str = "0.1.0"
    created_date: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_date: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    gams_version: str | None = None
    models: list[ModelEntry] = field(default_factory=list)
    
    @property
    def total_models(self) -> int:
        return len(self.models)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["total_models"] = self.total_models
        return data
    
    def save(self, path: str) -> None:
        """Save catalog to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "GamslibCatalog":
        """Load catalog from JSON file."""
        with open(path) as f:
            data = json.load(f)
        
        models = [ModelEntry(**m) for m in data.get("models", [])]
        return cls(
            schema_version=data.get("schema_version", "0.1.0"),
            created_date=data.get("created_date", ""),
            updated_date=data.get("updated_date", ""),
            gams_version=data.get("gams_version"),
            models=models,
        )
```

---

## Example Usage

### Creating a New Catalog

```python
from datetime import datetime

catalog = GamslibCatalog(
    gams_version="51.3.0",
)

# Add a model
model = ModelEntry(
    model_id="trnsport",
    sequence_number=1,
    model_name="A Transportation Problem",
    gamslib_type="LP",
    source_url="https://www.gams.com/latest/gamslib_ml/trnsport.1",
    web_page_url="https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html",
    description="Demonstrates a simple transportation model",
    keywords=["linear programming", "transportation problem"],
)
catalog.models.append(model)

# Save to file
catalog.save("data/gamslib/catalog.json")
```

### Querying the Catalog

```python
# Load catalog
catalog = GamslibCatalog.load("data/gamslib/catalog.json")

# Filter by type
lp_models = [m for m in catalog.models if m.gamslib_type == "LP"]
nlp_models = [m for m in catalog.models if m.gamslib_type == "NLP"]

# Filter by download status
pending = [m for m in catalog.models if m.download_status == "pending"]
downloaded = [m for m in catalog.models if m.download_status == "downloaded"]

# Get model by ID
def get_model(catalog: GamslibCatalog, model_id: str) -> ModelEntry | None:
    for m in catalog.models:
        if m.model_id == model_id:
            return m
    return None

trnsport = get_model(catalog, "trnsport")
```

---

## File Locations

| File | Purpose |
|------|---------|
| `data/gamslib/catalog.json` | Main catalog file (version controlled) |
| `data/gamslib/catalog_example.json` | Example catalog for testing |
| `docs/infrastructure/GAMSLIB_CATALOG_SCHEMA.md` | This documentation |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-12-31 | Initial draft for Sprint 13 |

---

## Design Decision: Standalone vs Integrated

**Decision:** Use standalone dataclasses, NOT tied to ModelIR.

**Rationale:**
1. **Different Purposes:** ModelIR is optimized for internal transformation; catalog is for external metadata tracking
2. **Flexibility:** Catalog can evolve independently of parser/IR changes
3. **Simplicity:** No circular dependencies between catalog and core nlp2mcp modules
4. **Precedent:** Follows pattern from `scripts/ingest_gamslib.py` which uses dedicated `ModelResult` dataclass

**Reference:** See Unknown 5.3 verification in `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md`

---

## Changelog

- **2025-12-31:** Initial schema documentation for Sprint 13 Prep Task 7
