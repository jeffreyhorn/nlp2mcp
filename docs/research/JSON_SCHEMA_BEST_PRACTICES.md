# JSON Schema Best Practices for nlp2mcp

**Created:** January 1, 2026  
**Purpose:** Research findings to inform Sprint 14 JSON database schema design  
**Task:** Sprint 14 Prep Task 3

---

## Executive Summary

This document summarizes JSON Schema best practices researched for the Sprint 14 database schema design (`data/gamslib/schema.json`). Key decisions:

1. **Schema Draft Version:** Use **Draft-07** for maximum compatibility with Python jsonschema library and tooling
2. **Naming Convention:** Use **snake_case** for consistency with existing catalog.json and Python codebase
3. **Structure:** Use **moderate nesting** (2-3 levels) for logical grouping of pipeline stages
4. **Migration Strategy:** Use **semantic versioning** with explicit schema_version field and eager migration

---

## 1. JSON Schema Draft Version Comparison

### Overview

JSON Schema has multiple draft versions. The two most relevant for 2025 projects are:

| Feature | Draft-07 | Draft 2020-12 |
|---------|----------|---------------|
| $schema URI | `http://json-schema.org/draft-07/schema#` | `https://json-schema.org/draft/2020-12/schema` |
| Release Year | 2018 | 2020 |
| LTS Status | Yes (long-term support) | Yes (current stable) |
| OpenAPI Compatibility | 3.0 | 3.1 |
| Python jsonschema Support | Full (v4.x) | Full (v4.x) |

### Key Differences

#### Array/Tuple Handling
- **Draft-07:** Uses `items` for tuple validation with `additionalItems` for trailing items
- **Draft 2020-12:** Replaces with `prefixItems` and new `items` keyword (breaking change)

```json
// Draft-07 tuple validation
{
  "type": "array",
  "items": [{"type": "string"}, {"type": "number"}],
  "additionalItems": false
}

// Draft 2020-12 tuple validation
{
  "type": "array",
  "prefixItems": [{"type": "string"}, {"type": "number"}],
  "items": false
}
```

#### Dynamic References
- **Draft-07:** Uses `$ref` only
- **Draft 2020-12:** Adds `$dynamicRef` and `$dynamicAnchor` (advanced feature)

#### Format Vocabulary
- **Draft 2020-12:** Separates format vocabulary into annotation and assertion modes

### Recommendation: Draft-07

**Use Draft-07 for nlp2mcp database schema.**

Rationale:
1. **Simpler syntax:** No tuple validation needed for our schema
2. **Wider compatibility:** Works with all JSON Schema tools from 2018+
3. **Python jsonschema:** Both drafts supported (v4.25+), but Draft-07 is default
4. **No advanced features needed:** We don't need `$dynamicRef`, `unevaluatedProperties`, etc.
5. **Performance:** Draft-07 validators have lower overhead (no unevaluated* checks)

```python
# Python jsonschema usage
from jsonschema import Draft7Validator

# Explicitly use Draft-07
validator = Draft7Validator(schema)
validator.validate(instance)
```

### Sources
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [JSON Schema Specification Links](https://json-schema.org/specification-links)
- [jsonschema Python Library](https://python-jsonschema.readthedocs.io/)
- [Ajv Schema Language Guide](https://ajv.js.org/guide/schema-language.html)

---

## 2. Nested Objects vs Flat Structure

### Trade-offs

| Aspect | Nested Structure | Flat Structure |
|--------|-----------------|----------------|
| Readability | Better grouping | More verbose |
| Query Access | `entry["convexity"]["status"]` | `entry["convexity_status"]` |
| CSV Export | Requires flattening | Direct mapping |
| Schema Complexity | Nested definitions | Simple properties |
| Extensibility | Easy to add fields to groups | Pollutes top-level namespace |
| Validation | Can validate sub-objects independently | All fields at same level |

### Best Practice Guidelines

1. **Limit nesting to 3-4 levels maximum** - deeper nesting impacts performance and usability
2. **Group logically related fields** - e.g., all parse-related fields in `nlp2mcp_parse` object
3. **Keep independent data flat** - don't nest just for organization
4. **Consider access patterns** - if fields are always read together, nest them

### nlp2mcp Schema Recommendation: Moderate Nesting

Use nested objects for pipeline stages, but keep nesting shallow (2 levels):

```json
{
  "model_id": "trnsport",
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP",
  
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2026-01-01T12:00:00Z",
    "solver_status": 1,
    "model_status": 1,
    "objective_value": 153.675
  },
  
  "nlp2mcp_parse": {
    "status": "success",
    "parse_date": "2026-01-02T10:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "parse_time_seconds": 0.05
  },
  
  "nlp2mcp_translate": {
    "status": "not_tested"
  },
  
  "mcp_solve": {
    "status": "not_tested"
  }
}
```

**Rationale:**
1. Clear separation between pipeline stages
2. Easy to add new fields within each stage
3. Query pattern: `model["nlp2mcp_parse"]["status"]` is intuitive
4. CSV export: flatten with dot notation (`nlp2mcp_parse.status`)
5. Validation: can validate each stage object independently

### Anti-patterns to Avoid

```json
// BAD: Too flat - clutters namespace
{
  "convexity_status": "verified",
  "convexity_date": "...",
  "convexity_solver_status": 1,
  "convexity_model_status": 1,
  "parse_status": "success",
  "parse_date": "...",
  "parse_version": "...",
  "translate_status": "..."
}

// BAD: Too deep - hard to query
{
  "pipeline": {
    "stages": {
      "parse": {
        "results": {
          "status": "success"
        }
      }
    }
  }
}
```

### Sources
- [Firebase Database Structure Guide](https://firebase.google.com/docs/database/web/structure-data)
- [MongoDB Flat vs Nested Structure](https://www.mongodb.com/community/forums/t/flat-vs-nested-structure/8027)
- [JSON Best Practices](https://jsonconsole.com/blog/json-best-practices-writing-clean-maintainable-data-structures)

---

## 3. Field Naming Conventions

### Common Conventions

| Convention | Example | Common Use |
|------------|---------|------------|
| camelCase | `modelId`, `parseStatus` | JavaScript, JSON-API |
| snake_case | `model_id`, `parse_status` | Python, databases, Ruby |
| kebab-case | `model-id`, `parse-status` | HTML, URLs (avoid in JSON) |
| PascalCase | `ModelId`, `ParseStatus` | .NET, class names |

### nlp2mcp Recommendation: snake_case

**Use snake_case for all field names.**

Rationale:
1. **Consistency with existing code:** catalog.json already uses snake_case (20 fields)
2. **Python alignment:** PEP 8 recommends snake_case for variables
3. **Database compatibility:** SQL databases typically use snake_case
4. **No conversion needed:** Python code can access fields directly without case conversion

```python
# Direct field access without conversion
model = db.get("trnsport")
print(model["convexity_status"])  # Natural in Python
print(model["nlp2mcp_parse"]["status"])
```

### Naming Guidelines

1. **Use descriptive names:** `verification_date` not `vdate`
2. **Prefix nested objects with context:** `nlp2mcp_parse`, `mcp_solve`
3. **Use plurals for arrays:** `keywords`, `errors`
4. **Avoid abbreviations except common ones:** `url`, `id`, `nlp`
5. **Boolean fields:** use `is_` or `has_` prefix when clarifying (optional)

### Catalog.json Field Inventory (snake_case)

Existing fields to preserve:
```
model_id, sequence_number, model_name, gamslib_type, source_url,
web_page_url, description, keywords, download_status, download_date,
file_path, file_size_bytes, notes, convexity_status, verification_date,
solver_status, model_status, objective_value, solve_time_seconds,
verification_error
```

All 20 fields use consistent snake_case.

### Sources
- [JSON Naming Conventions](https://www.w3tutorials.net/blog/json-naming-convention-snake-case-camelcase-or-pascalcase/)
- [Adidas API Guidelines](https://adidas.gitbook.io/api-guidelines/general-guidelines/json)
- [camelCase vs snake_case](https://apidog.com/blog/camelcase-vs-snake_case/)

---

## 4. Schema Versioning Strategy

### Versioning Approaches

| Approach | Format | Use Case |
|----------|--------|----------|
| Semantic Versioning | MAJOR.MINOR.PATCH | Standard, well-understood |
| SchemaVer | MODEL-REVISION-ADDITION | Schema-specific, less common |
| Date-based | YYYY.MM.DD | Simple, chronological |
| Integer | 1, 2, 3... | Minimal, for simple schemas |

### nlp2mcp Recommendation: Semantic Versioning

**Use semantic versioning (MAJOR.MINOR.PATCH) with explicit `schema_version` field.**

```json
{
  "schema_version": "2.0.0",
  "created_date": "2026-01-15T10:00:00Z",
  "updated_date": "2026-01-15T12:00:00Z",
  "models": [...]
}
```

Version semantics:
- **MAJOR (2.x.x):** Breaking changes - removed fields, changed types, restructuring
- **MINOR (x.1.x):** Backward-compatible additions - new optional fields
- **PATCH (x.x.1):** Documentation/metadata updates, no schema changes

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Sprint 13 | Initial catalog.json schema |
| 2.0.0 | Sprint 14 | New gamslib_status.json with nested pipeline stages |

### Schema Version Field Placement

Place at the **top level** of the database file, not per-entry:

```json
{
  "schema_version": "2.0.0",  // Top-level, single source of truth
  "gams_version": "51.3.0",
  "total_models": 219,
  "models": [
    // Individual entries do NOT have schema_version
    {"model_id": "trnsport", ...}
  ]
}
```

Rationale:
1. Single version for entire database (simpler)
2. Migration applies to all entries at once
3. No per-entry version inconsistencies

### Sources
- [Schema Versioning Strategies](https://app.studyraid.com/en/read/12384/399934/schema-versioning-strategies)
- [Couchbase Schema Versioning Tutorial](https://developer.couchbase.com/tutorial-schema-versioning?learningPath=learn/json-document-management-guide)
- [Best Practices for JSON Schema Version Management](https://trycatchdebug.net/news/1327354/json-schema-versioning)

---

## 5. Migration Patterns

### Migration Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Eager Migration | Migrate all entries when schema changes | Small databases, infrequent changes |
| Lazy Migration | Migrate entries on read/write | Large databases, gradual rollout |
| Dual-Write | Write to both old and new formats | Zero-downtime migrations |
| Transform Layer | Apply transformations at read time | Read-heavy workloads |

### nlp2mcp Recommendation: Eager Migration

**Use eager migration with a dedicated migration script.**

Rationale:
1. **Small database:** 219 models, <200KB - migration is instant
2. **Infrequent changes:** Schema changes only at sprint boundaries
3. **Simplicity:** No runtime version checks in db_manager
4. **Atomicity:** Entire database migrated at once, no mixed states

### Migration Implementation

```python
# scripts/gamslib/migrate_schema.py

def migrate_v1_to_v2(old_entry: dict) -> dict:
    """Migrate catalog.json entry to gamslib_status.json format."""
    return {
        "model_id": old_entry["model_id"],
        "sequence_number": old_entry["sequence_number"],
        "model_name": old_entry["model_name"],
        "gamslib_type": old_entry["gamslib_type"],
        # ... core fields ...
        
        # Restructure convexity fields into nested object
        "convexity": {
            "status": old_entry.get("convexity_status", "not_tested"),
            "verification_date": old_entry.get("verification_date"),
            "solver_status": old_entry.get("solver_status"),
            "model_status": old_entry.get("model_status"),
            "objective_value": old_entry.get("objective_value"),
            "solve_time_seconds": old_entry.get("solve_time_seconds"),
            "error": old_entry.get("verification_error")
        },
        
        # Initialize new pipeline stages
        "nlp2mcp_parse": {"status": "not_tested"},
        "nlp2mcp_translate": {"status": "not_tested"},
        "mcp_solve": {"status": "not_tested"}
    }

def migrate_database(old_path: Path, new_path: Path):
    """Migrate entire database from v1 to v2."""
    with open(old_path) as f:
        old_data = json.load(f)
    
    new_data = {
        "schema_version": "2.0.0",
        "migrated_from": old_data.get("schema_version", "1.0.0"),
        "created_date": old_data.get("created_date"),
        "updated_date": datetime.now(UTC).isoformat(),
        "gams_version": old_data.get("gams_version"),
        "total_models": len(old_data["models"]),
        "models": [migrate_v1_to_v2(m) for m in old_data["models"]]
    }
    
    with open(new_path, "w") as f:
        json.dump(new_data, f, indent=2)
```

### Backward Compatibility Guidelines

1. **Never remove required fields** without major version bump
2. **Add new fields as optional** with default values
3. **Deprecate before removing** - mark fields as deprecated for one version
4. **Provide migration scripts** for major version changes
5. **Document all changes** in CHANGELOG.md

### Sources
- [Schema Registry Best Practices](https://docs.solace.com/Schema-Registry/schema-registry-best-practices.htm)
- [Confluent Schema Registry Best Practices](https://www.confluent.io/blog/best-practices-for-confluent-schema-registry/)
- [Schema Evolution](https://hackolade.com/help/Schemaversioning.html)

---

## 6. Required vs Optional Fields

### Principles

1. **Core identification fields:** Always required (model_id, model_name, gamslib_type)
2. **Pipeline stage objects:** Optional (populated incrementally)
3. **Fields within stages:** Required once stage is present
4. **Timestamps:** Required for completed operations, absent for not_tested

### nlp2mcp Schema Field Requirements

```json
{
  "type": "object",
  "required": ["model_id", "model_name", "gamslib_type"],
  "properties": {
    "model_id": {"type": "string"},
    "model_name": {"type": "string"},
    "gamslib_type": {"type": "string", "enum": ["LP", "NLP", "QCP", "MIP", "MINLP", "MIQCP"]},
    
    "convexity": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {"type": "string", "enum": ["verified_convex", "likely_convex", "error", "excluded", "unknown", "not_tested"]},
        "verification_date": {"type": "string", "format": "date-time"},
        "solver_status": {"type": "integer"},
        "model_status": {"type": "integer"},
        "objective_value": {"type": "number"},
        "solve_time_seconds": {"type": "number"},
        "error": {"type": "string"}
      }
    },
    
    "nlp2mcp_parse": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {"type": "string", "enum": ["success", "failure", "partial", "not_tested"]},
        "parse_date": {"type": "string", "format": "date-time"},
        "nlp2mcp_version": {"type": "string"},
        "parse_time_seconds": {"type": "number"},
        "error": {"type": "object"}
      }
    }
  }
}
```

### Handling Missing Optional Fields

**Preferred approach:** Absent fields (not null)

```json
// GOOD: Field absent when not tested
{
  "model_id": "trnsport",
  "convexity": {"status": "verified_convex"}
  // nlp2mcp_parse is absent, not null
}

// AVOID: Explicit null
{
  "model_id": "trnsport",
  "nlp2mcp_parse": null  // Creates noise in diffs
}
```

In Python, handle with `.get()`:
```python
parse_status = model.get("nlp2mcp_parse", {}).get("status", "not_tested")
```

---

## 7. Error Representation

### Structured vs String Errors

| Approach | Pros | Cons |
|----------|------|------|
| String | Simple, human-readable | Hard to query, parse |
| Structured Object | Queryable, analyzable | More verbose, more schema |
| Hybrid | Categorized + message | Good balance |

### nlp2mcp Recommendation: Structured with Categories

```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "error": {
      "category": "syntax_error",
      "message": "Unexpected token 'loop' at line 42",
      "line": 42,
      "column": 15
    }
  }
}
```

Error categories for parsing:
- `syntax_error` - Parser grammar failure
- `unsupported_feature` - Valid GAMS but not supported
- `missing_include` - $include file not found
- `timeout` - Parsing exceeded time limit
- `internal_error` - Unexpected parser error

### Multiple Errors

For stages that can have multiple errors, use an array:

```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "errors": [
      {"category": "syntax_error", "message": "...", "line": 42},
      {"category": "syntax_error", "message": "...", "line": 58}
    ]
  }
}
```

---

## 8. Validation Strictness

### Strictness Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| Strict | All fields validated, no extra fields | Production data |
| Moderate | Required fields validated, extras allowed | Development |
| Lenient | Type validation only, minimal constraints | Migration/import |

### nlp2mcp Recommendation: Strict Validation

Use `additionalProperties: false` for strict validation:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "model_id": {"type": "string"},
    "model_name": {"type": "string"}
  }
}
```

This prevents:
- Typos in field names going unnoticed
- Unplanned field additions
- Schema drift over time

### Validation Integration

```python
# db_manager.py validation
from jsonschema import Draft7Validator, ValidationError

def validate_entry(entry: dict, schema: dict) -> list[str]:
    """Validate entry and return list of error messages."""
    validator = Draft7Validator(schema)
    errors = []
    for error in validator.iter_errors(entry):
        errors.append(f"{error.json_path}: {error.message}")
    return errors

def add_model(entry: dict):
    errors = validate_entry(entry, ENTRY_SCHEMA)
    if errors:
        raise ValueError(f"Invalid entry: {errors}")
    # Proceed with add
```

---

## 9. Sprint 14 Recommendations Summary

### Schema Design Decisions

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| Draft Version | Draft-07 | Compatibility, simplicity, no advanced features needed |
| Naming | snake_case | Consistency with catalog.json, Python alignment |
| Structure | Moderate nesting (2 levels) | Logical grouping, easy queries, extensible |
| Versioning | Semantic (MAJOR.MINOR.PATCH) | Industry standard, clear change semantics |
| Migration | Eager, one-time | Small database, infrequent changes |
| Required Fields | Core identification only | Allow incremental population |
| Errors | Structured with categories | Queryable, analyzable |
| Validation | Strict | Prevent schema drift |

### File Organization

```
data/gamslib/
  catalog.json           # Sprint 13 archive (read-only)
  gamslib_status.json    # Sprint 14 new database (v2.0.0)
  schema.json            # JSON Schema definition (Draft-07)
  archive/               # Timestamped backups
```

### Next Steps

1. **Task 4:** Research jsonschema library integration
2. **Task 5:** Create draft schema based on these recommendations
3. **Sprint 14:** Implement db_manager.py with schema validation

---

## Appendix: JSON Schema Template

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/jeffreyhorn/nlp2mcp/data/gamslib/schema.json",
  "title": "GAMSLIB Model Status Database",
  "description": "Schema for tracking GAMSLIB model status through the nlp2mcp pipeline",
  "type": "object",
  "required": ["schema_version", "models"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version of the database schema"
    },
    "created_date": {
      "type": "string",
      "format": "date-time"
    },
    "updated_date": {
      "type": "string",
      "format": "date-time"
    },
    "gams_version": {
      "type": "string"
    },
    "total_models": {
      "type": "integer",
      "minimum": 0
    },
    "models": {
      "type": "array",
      "items": {"$ref": "#/definitions/model_entry"}
    }
  },
  "definitions": {
    "model_entry": {
      "type": "object",
      "required": ["model_id", "model_name", "gamslib_type"],
      "additionalProperties": false,
      "properties": {
        "model_id": {"type": "string"},
        "model_name": {"type": "string"},
        "gamslib_type": {
          "type": "string",
          "enum": ["LP", "NLP", "QCP", "MIP", "MINLP", "MIQCP"]
        },
        "convexity": {"$ref": "#/definitions/convexity_result"},
        "nlp2mcp_parse": {"$ref": "#/definitions/parse_result"},
        "nlp2mcp_translate": {"$ref": "#/definitions/translate_result"},
        "mcp_solve": {"$ref": "#/definitions/solve_result"}
      }
    },
    "convexity_result": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["verified_convex", "likely_convex", "error", "excluded", "unknown", "not_tested", "license_limited"]
        },
        "verification_date": {"type": "string", "format": "date-time"},
        "solver_status": {"type": "integer"},
        "model_status": {"type": "integer"},
        "objective_value": {"type": "number"},
        "solve_time_seconds": {"type": "number"},
        "error": {"type": "string"}
      }
    },
    "parse_result": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["success", "failure", "partial", "not_tested"]
        },
        "parse_date": {"type": "string", "format": "date-time"},
        "nlp2mcp_version": {"type": "string"},
        "parse_time_seconds": {"type": "number"},
        "error": {
          "type": "object",
          "properties": {
            "category": {"type": "string"},
            "message": {"type": "string"},
            "line": {"type": "integer"},
            "column": {"type": "integer"}
          }
        }
      }
    },
    "translate_result": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["success", "failure", "not_tested"]
        },
        "translate_date": {"type": "string", "format": "date-time"},
        "nlp2mcp_version": {"type": "string"},
        "translate_time_seconds": {"type": "number"},
        "output_file": {"type": "string"},
        "error": {"type": "object"}
      }
    },
    "solve_result": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["success", "failure", "mismatch", "not_tested"]
        },
        "solve_date": {"type": "string", "format": "date-time"},
        "solver": {"type": "string"},
        "objective_value": {"type": "number"},
        "solve_time_seconds": {"type": "number"},
        "objective_match": {"type": "boolean"},
        "error": {"type": "object"}
      }
    }
  }
}
```

---

## Document History

- January 1, 2026: Initial creation (Sprint 14 Prep Task 3)
