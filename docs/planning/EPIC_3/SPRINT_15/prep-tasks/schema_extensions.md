# Database Schema Extensions for Sprint 15

**Task:** Sprint 15 Prep Task 6  
**Date:** January 12, 2026  
**Purpose:** Design schema extensions to support MCP solve results, solution comparison, and refined error categorization

---

## Executive Summary

This document describes extensions to the GAMSLIB database schema from v2.0.0 to v2.1.0 to support Sprint 15's solve testing infrastructure.

**Key Changes:**
- Version: 2.0.0 → 2.1.0 (minor version, backward compatible)
- New objects: `mcp_solve_result`, `solution_comparison_result`, `model_statistics`
- Extended enums: Error categories expanded from 7 to 36 (Task 4 taxonomy)
- New enums: `solve_outcome_category`, `comparison_result_category`

**Backward Compatibility:** Sprint 14 data validates against v2.1.0 schema without modification. New objects are optional.

---

## 1. Version Change Rationale

### 1.1 Why v2.1.0 (Minor) vs v3.0.0 (Major)?

Per [Semantic Versioning](https://semver.org/):
- **MAJOR:** Incompatible API changes
- **MINOR:** Backward-compatible new functionality
- **PATCH:** Backward-compatible bug fixes

**v2.1.0 is appropriate because:**
1. All new objects (`mcp_solve`, `solution_comparison`) are optional
2. Existing Sprint 14 data remains valid without modification
3. Old error categories are preserved in enum (no removal)
4. No required field changes to existing objects

### 1.2 Changes Summary

| Category | v2.0.0 | v2.1.0 | Change Type |
|----------|--------|--------|-------------|
| Schema version | 2.0.0 | 2.1.0 | Updated |
| model_entry properties | 15 | 17 | Added 2 optional |
| mcp_solve object | Basic (10 fields) | Enhanced (14 fields) | Enhanced |
| solution_comparison | Not present | New (16 fields) | Added |
| model_statistics | Not present | New (4 fields) | Added |
| error_category enum | 7 values | 36 values | Extended |
| solve_outcome_category | Not present | New (10 values) | Added |
| comparison_result_category | Not present | New (7 values) | Added |

---

## 2. New Object: mcp_solve_result

### 2.1 Purpose

Stores results from solving the MCP reformulation with PATH solver. This is an enhanced version of the basic `solve_result` in v2.0.0.

### 2.2 Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | enum | Yes | Overall status: success, failure, timeout, not_tested |
| `solve_date` | date-time | No | ISO 8601 timestamp |
| `solver` | string | No | Solver name (default: "PATH") |
| `solver_version` | string | No | Solver version (e.g., "PATH 5.2.01") |
| `solver_status` | integer | No | GAMS solver status code |
| `solver_status_text` | string | No | Human-readable solver status |
| `model_status` | integer | No | GAMS model status code |
| `model_status_text` | string | No | Human-readable model status |
| `objective_value` | number\|null | No | Objective from MCP solve |
| `solve_time_seconds` | number | No | Solve time in seconds |
| `iterations` | integer\|null | No | Solver iterations |
| `mcp_file_used` | string | No | Path to MCP file solved |
| `outcome_category` | solve_outcome_category | No | Categorized outcome |
| `error` | error_detail | No | Error details if failed |

### 2.3 Status Values

| Status | Description |
|--------|-------------|
| `success` | MCP solved successfully (solver_status=1, model_status in 1,2) |
| `failure` | MCP solve failed (infeasible, error, etc.) |
| `timeout` | MCP solve timed out |
| `not_tested` | Solve not attempted |

### 2.4 Example

```json
{
  "mcp_solve": {
    "status": "success",
    "solve_date": "2026-01-12T10:30:00Z",
    "solver": "PATH",
    "solver_version": "PATH 5.2.01",
    "solver_status": 1,
    "solver_status_text": "Normal Completion",
    "model_status": 1,
    "model_status_text": "Optimal",
    "objective_value": -26272.5145,
    "solve_time_seconds": 0.155,
    "iterations": 27,
    "mcp_file_used": "data/gamslib/mcp/hs62_mcp.gms",
    "outcome_category": "model_optimal"
  }
}
```

### 2.5 Validation Rules

1. If `status` is "success", `solver_status` should be 1 and `model_status` in (1, 2)
2. If `status` is "failure", `error` object should be present
3. `solve_time_seconds` must be >= 0
4. `iterations` must be >= 0 if present

---

## 3. New Object: solution_comparison_result

### 3.1 Purpose

Compares the original NLP solution (from convexity verification) with the MCP solution to validate the KKT reformulation.

### 3.2 Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `comparison_status` | enum | Yes | Overall result: match, mismatch, skipped, error, not_tested |
| `comparison_date` | date-time | No | ISO 8601 timestamp |
| `nlp_objective` | number\|null | No | NLP objective (from convexity) |
| `mcp_objective` | number\|null | No | MCP objective (from mcp_solve) |
| `absolute_difference` | number\|null | No | \|nlp - mcp\| |
| `relative_difference` | number\|null | No | \|nlp - mcp\| / max(\|nlp\|, 1e-10) |
| `objective_match` | boolean\|null | No | True if within tolerance |
| `tolerance_absolute` | number | No | Absolute tolerance (default: 1e-8) |
| `tolerance_relative` | number | No | Relative tolerance (default: 1e-6) |
| `nlp_solver_status` | integer\|null | No | NLP solver status |
| `nlp_model_status` | integer\|null | No | NLP model status |
| `mcp_solver_status` | integer\|null | No | MCP solver status |
| `mcp_model_status` | integer\|null | No | MCP model status |
| `status_match` | boolean\|null | No | True if both have compatible status |
| `comparison_result` | comparison_result_category | No | Detailed outcome category |
| `notes` | string\|null | No | Additional notes |

### 3.3 Comparison Status Values

| Status | Description |
|--------|-------------|
| `match` | Objectives match within tolerance |
| `mismatch` | Objectives differ beyond tolerance |
| `skipped` | Comparison skipped (e.g., NLP infeasible) |
| `error` | Error during comparison |
| `not_tested` | Comparison not performed |

### 3.4 Tolerance Formula

```python
match = abs(nlp_obj - mcp_obj) <= tolerance_absolute + tolerance_relative * abs(nlp_obj)
```

Default values:
- `tolerance_absolute`: 1e-8 (matches IPOPT default)
- `tolerance_relative`: 1e-6 (matches CPLEX/PATH defaults)

### 3.5 Example

```json
{
  "solution_comparison": {
    "comparison_status": "match",
    "comparison_date": "2026-01-12T10:30:05Z",
    "nlp_objective": -26272.5145,
    "mcp_objective": -26272.5145,
    "absolute_difference": 0.0,
    "relative_difference": 0.0,
    "objective_match": true,
    "tolerance_absolute": 1e-8,
    "tolerance_relative": 1e-6,
    "nlp_solver_status": 1,
    "nlp_model_status": 1,
    "mcp_solver_status": 1,
    "mcp_model_status": 1,
    "status_match": true,
    "comparison_result": "compare_objective_match"
  }
}
```

### 3.6 Validation Rules

1. If `comparison_status` is "match", `objective_match` should be true
2. If `comparison_status` is "mismatch", `objective_match` should be false
3. `absolute_difference` and `relative_difference` must be >= 0
4. Tolerance values must be > 0

---

## 4. New Object: model_statistics

### 4.1 Purpose

Stores model statistics extracted from the IR after successful parsing. Enables size-based filtering and complexity analysis.

### 4.2 Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variables` | integer | No | Number of variables |
| `equations` | integer | No | Number of equations |
| `parameters` | integer | No | Number of parameters |
| `sets` | integer | No | Number of sets |

### 4.3 Example

```json
{
  "nlp2mcp_parse": {
    "status": "success",
    "model_stats": {
      "variables": 10,
      "equations": 5,
      "parameters": 3,
      "sets": 2
    }
  }
}
```

---

## 5. Error Category Enums

### 5.1 Extended error_category Enum

The error_category enum expands from 7 to 36 values based on Task 4's comprehensive taxonomy.

**Parse Errors (16 categories):**

| Category | Stage | Description |
|----------|-------|-------------|
| `lexer_invalid_char` | Lexer | Invalid character in source |
| `lexer_unclosed_string` | Lexer | Unclosed string literal |
| `lexer_invalid_number` | Lexer | Malformed number |
| `lexer_encoding_error` | Lexer | Character encoding issue |
| `parser_unexpected_token` | Parser | Unexpected token |
| `parser_missing_semicolon` | Parser | Missing semicolon |
| `parser_unmatched_paren` | Parser | Unmatched parenthesis |
| `parser_invalid_declaration` | Parser | Invalid declaration |
| `parser_invalid_expression` | Parser | Invalid expression |
| `parser_unexpected_eof` | Parser | Unexpected end of file |
| `semantic_undefined_symbol` | Semantic | Undefined symbol |
| `semantic_type_mismatch` | Semantic | Type mismatch |
| `semantic_domain_error` | Semantic | Domain error |
| `semantic_duplicate_def` | Semantic | Duplicate definition |
| `include_file_not_found` | Include | Include file not found |
| `include_circular` | Include | Circular include |

**Translation Errors (12 categories):**

| Category | Stage | Description |
|----------|-------|-------------|
| `diff_unsupported_func` | Differentiation | Unsupported function |
| `diff_chain_rule_error` | Differentiation | Chain rule error |
| `diff_numerical_error` | Differentiation | Numerical error |
| `model_no_objective_def` | Model | No objective definition |
| `model_domain_mismatch` | Model | Domain mismatch |
| `model_missing_bounds` | Model | Missing bounds |
| `unsup_index_offset` | Unsupported | Index offset |
| `unsup_dollar_cond` | Unsupported | Dollar conditional |
| `unsup_expression_type` | Unsupported | Expression type |
| `unsup_special_ordered` | Unsupported | Special ordered set |
| `codegen_equation_error` | Codegen | Equation generation |
| `codegen_variable_error` | Codegen | Variable generation |
| `codegen_numerical_error` | Codegen | Numerical in codegen |

**Legacy Categories (preserved for backward compatibility):**

| Category | Description |
|----------|-------------|
| `syntax_error` | Generic syntax error (Sprint 14) |
| `unsupported_feature` | Unsupported feature (Sprint 14) |
| `missing_include` | Missing include (Sprint 14) |
| `solver_error` | Solver error (Sprint 14) |
| `validation_error` | Validation error (Sprint 14) |
| `timeout` | Timeout |
| `internal_error` | Internal error |

### 5.2 New: solve_outcome_category Enum

For categorizing MCP solve outcomes:

| Category | Description |
|----------|-------------|
| `path_solve_normal` | Normal completion (success) |
| `path_solve_iteration_limit` | Iteration limit hit |
| `path_solve_time_limit` | Time limit hit |
| `path_solve_terminated` | Solver terminated |
| `path_solve_eval_error` | Evaluation error |
| `path_solve_license` | License error |
| `model_optimal` | Optimal solution (success) |
| `model_locally_optimal` | Locally optimal (success) |
| `model_infeasible` | Model infeasible |
| `model_unbounded` | Model unbounded |

### 5.3 New: comparison_result_category Enum

For categorizing solution comparison outcomes:

| Category | Description |
|----------|-------------|
| `compare_objective_match` | Objectives match (success) |
| `compare_objective_mismatch` | Objectives differ |
| `compare_status_mismatch` | Status mismatch |
| `compare_nlp_failed` | NLP solve failed |
| `compare_mcp_failed` | MCP solve failed |
| `compare_both_infeasible` | Both infeasible |
| `compare_not_performed` | Comparison not done |

---

## 6. Migration Plan

### 6.1 Sprint 14 Data Compatibility

Sprint 14 data is fully compatible with v2.1.0:
- No required field changes
- Old error categories still valid
- New objects are optional

### 6.2 Migration Steps

1. **Update schema_version:** Change from "2.0.0" to "2.1.0"
2. **Re-categorize errors (optional):** Use detection algorithms to map old categories to refined taxonomy
3. **Preserve legacy categories:** Store original category in `legacy_category` field
4. **Initialize new objects:** Leave mcp_solve and solution_comparison as undefined until Sprint 15 testing

### 6.3 Migration Script Pseudocode

```python
def migrate_to_v2_1_0():
    db = load_database()
    
    # Update version
    db['schema_version'] = '2.1.0'
    db['updated_date'] = now_iso8601()
    
    for model in db['models']:
        # Re-categorize parse errors (optional enhancement)
        if model.get('nlp2mcp_parse', {}).get('error'):
            old_cat = model['nlp2mcp_parse']['error']['category']
            new_cat = categorize_parse_error(
                model['nlp2mcp_parse']['error']['message']
            )
            model['nlp2mcp_parse']['error']['legacy_category'] = old_cat
            model['nlp2mcp_parse']['error']['category'] = new_cat
        
        # Re-categorize translation errors (optional enhancement)
        if model.get('nlp2mcp_translate', {}).get('error'):
            old_cat = model['nlp2mcp_translate']['error']['category']
            new_cat = categorize_translation_error(
                model['nlp2mcp_translate']['error']['message']
            )
            model['nlp2mcp_translate']['error']['legacy_category'] = old_cat
            model['nlp2mcp_translate']['error']['category'] = new_cat
    
    save_database(db)
```

---

## 7. Implementation Checklist

### 7.1 Schema Implementation

- [x] Create schema_v2.1.0_draft.json
- [x] Define mcp_solve_result object (14 fields)
- [x] Define solution_comparison_result object (16 fields)
- [x] Define model_statistics object (4 fields)
- [x] Extend error_category enum (36 values)
- [x] Add solve_outcome_category enum (10 values)
- [x] Add comparison_result_category enum (7 values)
- [x] Validate schema syntax

### 7.2 Sprint 15 Implementation

- [ ] Create db_manager methods for mcp_solve updates
- [ ] Create db_manager methods for solution_comparison updates
- [ ] Implement error categorization functions
- [ ] Update batch scripts to use new schema
- [ ] Create schema migration script
- [ ] Update validation to use v2.1.0 schema

### 7.3 Testing

- [ ] Validate Sprint 14 data against v2.1.0 schema
- [ ] Test mcp_solve object creation
- [ ] Test solution_comparison object creation
- [ ] Test error categorization functions
- [ ] Test migration script

---

## 8. Field Count Summary

| Object | v2.0.0 Fields | v2.1.0 Fields | Change |
|--------|---------------|---------------|--------|
| model_entry | 15 | 17 | +2 (mcp_solve, solution_comparison) |
| convexity_result | 8 | 8 | No change |
| parse_result | 7 | 8 | +1 (model_stats) |
| translate_result | 8 | 8 | No change |
| mcp_solve_result | 10 | 14 | +4 (enhanced) |
| solution_comparison_result | 0 | 16 | New |
| model_statistics | 0 | 4 | New |
| error_detail | 5 | 8 | +3 (legacy_category, source_line, suggestion) |
| **Total unique fields** | **53** | **75** | **+22** |

---

## Appendix A: Complete Enum Values

### A.1 error_category (36 values)

```
lexer_invalid_char, lexer_unclosed_string, lexer_invalid_number, 
lexer_encoding_error, parser_unexpected_token, parser_missing_semicolon,
parser_unmatched_paren, parser_invalid_declaration, parser_invalid_expression,
parser_unexpected_eof, semantic_undefined_symbol, semantic_type_mismatch,
semantic_domain_error, semantic_duplicate_def, include_file_not_found,
include_circular, diff_unsupported_func, diff_chain_rule_error,
diff_numerical_error, model_no_objective_def, model_domain_mismatch,
model_missing_bounds, unsup_index_offset, unsup_dollar_cond,
unsup_expression_type, unsup_special_ordered, codegen_equation_error,
codegen_variable_error, codegen_numerical_error, timeout, internal_error,
syntax_error, unsupported_feature, missing_include, solver_error, validation_error
```

### A.2 solve_outcome_category (10 values)

```
path_solve_normal, path_solve_iteration_limit, path_solve_time_limit,
path_solve_terminated, path_solve_eval_error, path_solve_license,
model_optimal, model_locally_optimal, model_infeasible, model_unbounded
```

### A.3 comparison_result_category (7 values)

```
compare_objective_match, compare_objective_mismatch, compare_status_mismatch,
compare_nlp_failed, compare_mcp_failed, compare_both_infeasible, compare_not_performed
```
