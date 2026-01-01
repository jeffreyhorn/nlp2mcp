# Python jsonschema Library Guide for nlp2mcp

**Created:** January 1, 2026  
**Purpose:** Document jsonschema library usage patterns for Sprint 14 db_manager.py  
**Task:** Sprint 14 Prep Task 4

---

## Executive Summary

This document provides a practical guide for using the Python `jsonschema` library (v4.25.1) in the nlp2mcp project. Key findings:

1. **Library Version:** jsonschema 4.25.1 with full Draft-07 and Draft 2020-12 support
2. **Recommended Validator:** `Draft7Validator` (consistent with Task 3 decision)
3. **Performance:** ~10,000 validations/second - negligible overhead for our use case
4. **Error Handling:** Rich error objects with path, message, and validator details
5. **Partial Validation:** Use separate schemas for create vs update operations

---

## 1. Installation and Setup

### Installation

```bash
pip install jsonschema
```

### Version Check

```python
from importlib.metadata import version
print(version("jsonschema"))  # 4.25.1
```

**Note:** Accessing `jsonschema.__version__` is deprecated. Use `importlib.metadata.version()` instead.

### Available Validators

```python
from jsonschema import Draft7Validator, Draft202012Validator

# Both are fully supported
# Use Draft7Validator per Task 3 recommendation
```

---

## 2. Basic Validation Patterns

### Pattern 1: Simple Validation

```python
from jsonschema import Draft7Validator, ValidationError

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["model_id", "model_name"],
    "properties": {
        "model_id": {"type": "string"},
        "model_name": {"type": "string"}
    }
}

# Create validator once (reuse for multiple validations)
validator = Draft7Validator(schema)

# Validate an entry
entry = {"model_id": "trnsport", "model_name": "Transport"}
errors = list(validator.iter_errors(entry))

if errors:
    for error in errors:
        print(f"Error: {error.message}")
else:
    print("Valid!")
```

### Pattern 2: Quick Validation (raises exception)

```python
from jsonschema import validate, ValidationError

try:
    validate(instance=entry, schema=schema)
    print("Valid!")
except ValidationError as e:
    print(f"Invalid: {e.message}")
```

**Note:** `validate()` raises on first error. Use `iter_errors()` to collect all errors.

### Pattern 3: Check if Valid (boolean)

```python
def is_valid(entry: dict, validator: Draft7Validator) -> bool:
    """Check if entry is valid without collecting errors."""
    return validator.is_valid(entry)
```

---

## 3. Required vs Optional Fields

### Behavior

- **Required fields:** Listed in `required` array - validation fails if missing
- **Optional fields:** Listed in `properties` but not in `required` - can be absent
- **Missing optional fields:** Do NOT cause validation errors

### Example Schema

```python
schema = {
    "type": "object",
    "required": ["model_id", "model_name", "gamslib_type"],  # Must be present
    "properties": {
        "model_id": {"type": "string"},
        "model_name": {"type": "string"},
        "gamslib_type": {"type": "string"},
        "convexity": {"type": "object"},  # Optional - can be absent
        "nlp2mcp_parse": {"type": "object"}  # Optional - can be absent
    }
}
```

### Validation Results

```python
# Valid: only required fields
{"model_id": "x", "model_name": "y", "gamslib_type": "LP"}  # 0 errors

# Valid: required + optional
{"model_id": "x", "model_name": "y", "gamslib_type": "LP", "convexity": {}}  # 0 errors

# Invalid: missing required
{"model_id": "x"}  # Error: 'model_name' is a required property
```

---

## 4. Nested Object Validation

### Schema with Nested Objects

```python
schema = {
    "type": "object",
    "required": ["model_id"],
    "properties": {
        "model_id": {"type": "string"},
        "convexity": {
            "type": "object",
            "required": ["status"],  # Required WITHIN convexity object
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["verified_convex", "likely_convex", "error", "not_tested"]
                },
                "verification_date": {"type": "string"},
                "solver_status": {"type": "integer"}
            }
        }
    }
}
```

### Validation Behavior

```python
# Valid: convexity absent (optional)
{"model_id": "x"}  # 0 errors

# Valid: convexity present with required status
{"model_id": "x", "convexity": {"status": "verified_convex"}}  # 0 errors

# Invalid: convexity present but missing status
{"model_id": "x", "convexity": {}}  # Error: 'status' is a required property

# Invalid: wrong enum value
{"model_id": "x", "convexity": {"status": "invalid"}}  
# Error: 'invalid' is not one of ['verified_convex', ...]
```

---

## 5. Strict vs Lenient Validation

### Strict Mode (Recommended)

Use `additionalProperties: false` to reject unknown fields:

```python
strict_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "model_id": {"type": "string"},
        "model_name": {"type": "string"}
    }
}

# Error: Additional properties are not allowed ('unknown_field' was unexpected)
{"model_id": "x", "model_name": "y", "unknown_field": "z"}
```

**Benefits:**
- Catches typos in field names
- Prevents schema drift
- Ensures data consistency

### Lenient Mode

Use `additionalProperties: true` (or omit) to allow unknown fields:

```python
lenient_schema = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "model_id": {"type": "string"}
    }
}

# Valid: extra fields allowed
{"model_id": "x", "unknown": "allowed"}  # 0 errors
```

**Use case:** Migration periods, backward compatibility

---

## 6. Partial Validation for Updates

### Problem

Full schema requires all fields, but updates may only provide changed fields.

### Solution: Separate Schemas

```python
# Schema for creating new entries (full validation)
CREATE_SCHEMA = {
    "type": "object",
    "required": ["model_id", "model_name", "gamslib_type"],
    "additionalProperties": False,
    "properties": {
        "model_id": {"type": "string"},
        "model_name": {"type": "string"},
        "gamslib_type": {"type": "string"},
        "convexity": {"$ref": "#/definitions/convexity_result"}
    },
    "definitions": {...}
}

# Schema for updates (no required fields)
UPDATE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "model_name": {"type": "string"},
        "gamslib_type": {"type": "string"},
        "convexity": {"$ref": "#/definitions/convexity_result"}
    },
    "definitions": {...}
}

# Usage
create_validator = Draft7Validator(CREATE_SCHEMA)
update_validator = Draft7Validator(UPDATE_SCHEMA)

def add_model(entry: dict):
    errors = list(create_validator.iter_errors(entry))
    if errors:
        raise ValueError(format_errors(errors))
    # ... add to database

def update_model(model_id: str, updates: dict):
    errors = list(update_validator.iter_errors(updates))
    if errors:
        raise ValueError(format_errors(errors))
    # ... apply updates
```

---

## 7. Error Handling

### Error Object Properties

```python
from jsonschema import Draft7Validator

validator = Draft7Validator(schema)
for error in validator.iter_errors(bad_data):
    print(f"message: {error.message}")           # Human-readable message
    print(f"path: {list(error.absolute_path)}")  # Field path as list
    print(f"schema_path: {list(error.schema_path)}")  # Schema location
    print(f"validator: {error.validator}")       # e.g., "type", "enum", "required"
    print(f"validator_value: {error.validator_value}")  # Expected value
```

### Example Error Objects

```python
# Input: {"model_id": 123, "convexity": {"status": "bad"}}

# Error 1:
# message: "123 is not of type 'string'"
# path: ['model_id']
# validator: "type"
# validator_value: "string"

# Error 2:
# message: "'bad' is not one of ['verified_convex', 'likely_convex', ...]"
# path: ['convexity', 'status']
# validator: "enum"
# validator_value: ['verified_convex', 'likely_convex', ...]
```

### Structured Error Format for Storage

```python
def format_validation_error(error) -> dict:
    """Format a ValidationError for database storage."""
    return {
        "field": ".".join(str(p) for p in error.absolute_path) or "(root)",
        "message": error.message,
        "validator": error.validator,
        "expected": str(error.validator_value)[:100]  # Truncate long values
    }

def validate_and_get_errors(entry: dict, validator) -> list[dict]:
    """Validate entry and return structured error list."""
    return [format_validation_error(e) for e in validator.iter_errors(entry)]
```

### Human-Readable Error Messages

```python
def get_human_errors(entry: dict, validator) -> list[str]:
    """Get human-readable error messages."""
    errors = []
    for error in sorted(validator.iter_errors(entry), key=lambda e: e.absolute_path):
        path = ".".join(str(p) for p in error.absolute_path) or "root"
        errors.append(f"{path}: {error.message}")
    return errors

# Usage
errors = get_human_errors(bad_entry, validator)
# ['model_id: 123 is not of type \'string\'', 
#  'convexity.status: \'bad\' is not one of [...]']
```

---

## 8. Performance Considerations

### Benchmarks (MacOS, Python 3.12)

| Operation | Time | Rate |
|-----------|------|------|
| Single validation | 0.099 ms | 10,100/sec |
| 1000 validations | 99 ms | - |
| 219 models (full batch) | ~22 ms | - |

### Performance Best Practices

1. **Create validator once, reuse for multiple validations:**
   ```python
   # GOOD: Create once
   validator = Draft7Validator(schema)
   for entry in entries:
       validator.validate(entry)
   
   # BAD: Create each time
   for entry in entries:
       Draft7Validator(schema).validate(entry)
   ```

2. **Use `is_valid()` for boolean checks:**
   ```python
   # Faster if you only need boolean result
   if validator.is_valid(entry):
       process(entry)
   ```

3. **Validate schema once at startup:**
   ```python
   # Validate schema is correct Draft-07
   Draft7Validator.check_schema(schema)
   ```

### Performance Impact

For nlp2mcp with 219 models:
- **Full batch validation:** ~22 ms (negligible)
- **Per-operation validation:** ~0.1 ms (imperceptible)
- **Recommendation:** Always validate - the cost is minimal

---

## 9. Format Validation

### Available Format Checkers

The default `FORMAT_CHECKER` supports:
- `date` - ISO 8601 date
- `email` - Email address
- `idn-email` - Internationalized email
- `ipv4` - IPv4 address
- `ipv6` - IPv6 address
- `regex` - Regular expression

**Note:** `date-time` format is NOT strictly validated by default.

### Enabling Format Checking

```python
validator = Draft7Validator(
    schema,
    format_checker=Draft7Validator.FORMAT_CHECKER
)

# Now format errors are caught
{"email": "not-an-email"}  # Error: 'not-an-email' is not a 'email'
```

### Recommendation for date-time

Since `date-time` format validation is not reliable, use a regex pattern instead:

```python
{
    "verification_date": {
        "type": "string",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+-]\\d{2}:\\d{2})?$"
    }
}
```

Or validate in application code:

```python
from datetime import datetime

def validate_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False
```

---

## 10. Schema Validation

### Validate Schema Correctness

```python
from jsonschema import Draft7Validator, SchemaError

try:
    Draft7Validator.check_schema(schema)
    print("Schema is valid Draft-07")
except SchemaError as e:
    print(f"Schema error: {e.message}")
```

### Common Schema Errors

```python
# Invalid type
{"type": "invalid_type"}  # SchemaError

# Invalid $ref
{"$ref": "#/definitions/missing"}  # RefResolutionError at validation time

# Invalid pattern
{"pattern": "[invalid"}  # SchemaError
```

---

## 11. Integration Pattern for db_manager.py

### Recommended Implementation

```python
# db_manager.py

import json
from pathlib import Path
from jsonschema import Draft7Validator, ValidationError

# Load schema once at module level
SCHEMA_PATH = Path(__file__).parent / "../../data/gamslib/schema.json"

def load_schema() -> dict:
    """Load and validate the database schema."""
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    Draft7Validator.check_schema(schema)  # Validate schema itself
    return schema

# Create validators at module level (singleton pattern)
_schema = None
_entry_validator = None

def get_entry_validator() -> Draft7Validator:
    """Get or create the entry validator (lazy singleton)."""
    global _schema, _entry_validator
    if _entry_validator is None:
        _schema = load_schema()
        entry_schema = _schema["definitions"]["model_entry"]
        _entry_validator = Draft7Validator(entry_schema)
    return _entry_validator


class ValidationError(Exception):
    """Database validation error with structured details."""
    
    def __init__(self, message: str, errors: list[dict]):
        super().__init__(message)
        self.errors = errors


def validate_entry(entry: dict) -> None:
    """Validate a model entry. Raises ValidationError if invalid."""
    validator = get_entry_validator()
    errors = []
    
    for error in validator.iter_errors(entry):
        errors.append({
            "field": ".".join(str(p) for p in error.absolute_path) or "(root)",
            "message": error.message,
            "validator": error.validator
        })
    
    if errors:
        fields = ", ".join(e["field"] for e in errors)
        raise ValidationError(f"Invalid entry: errors in {fields}", errors)


def add_model(entry: dict) -> None:
    """Add a new model to the database."""
    validate_entry(entry)  # Raises ValidationError if invalid
    # ... proceed with adding to database


def update_model(model_id: str, updates: dict) -> None:
    """Update an existing model."""
    # For updates, validate individual fields rather than full entry
    # or use a separate UPDATE_SCHEMA without required fields
    # ... proceed with update
```

---

## 12. Summary: Sprint 14 Recommendations

### Validation Strategy

| Scenario | Approach |
|----------|----------|
| New model creation | Full validation with required fields |
| Model updates | Partial validation (no required check) |
| Batch import | Validate each entry, collect all errors |
| Schema changes | Validate schema with `check_schema()` |

### Error Storage

Use structured error format:

```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "error": {
      "category": "validation_error",
      "message": "model_id: 123 is not of type 'string'",
      "field": "model_id",
      "validator": "type"
    }
  }
}
```

### Key Decisions

1. **Use Draft7Validator** - consistent with Task 3
2. **Use `additionalProperties: false`** - strict validation
3. **Create validators once** - reuse for performance
4. **Use `iter_errors()`** - collect all errors, not just first
5. **Store structured errors** - for querying and analysis
6. **Validate date-time in code** - format checker unreliable

---

## Appendix: Quick Reference

### Common Operations

```python
from jsonschema import Draft7Validator

# Create validator
validator = Draft7Validator(schema)

# Check if valid (boolean)
validator.is_valid(entry)

# Get all errors
list(validator.iter_errors(entry))

# Validate (raises on first error)
validator.validate(entry)

# Validate schema itself
Draft7Validator.check_schema(schema)
```

### Error Properties

```python
error.message          # Human-readable message
error.absolute_path    # Field path (deque)
error.schema_path      # Schema location (deque)
error.validator        # Validator type (str)
error.validator_value  # Expected value
error.instance         # Actual value
```

---

## Document History

- January 1, 2026: Initial creation (Sprint 14 Prep Task 4)
