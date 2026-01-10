# Comprehensive Error Taxonomy

**Task:** Sprint 15 Prep Task 4  
**Date:** January 10, 2026  
**Purpose:** Design comprehensive error classification for parse, translate, and solve pipeline stages

---

## Executive Summary

This document defines a comprehensive error and outcome taxonomy for all three nlp2mcp pipeline stages. The taxonomy refines Sprint 14's 6 broad categories into 44 specific outcome types (40 error types + 4 success outcomes) that enable targeted analysis and improvement.

**Key Changes from Sprint 14:**
- Parse errors: 6 categories → 16 refined categories
- Translation errors: 3 categories → 12 refined categories
- Solve outcomes: New stage with 16 categories (12 error types + 4 success outcomes)

**Benefits:**
1. Identify specific failure patterns for targeted fixes
2. Enable prioritized improvement roadmap
3. Track progress on specific error reduction
4. Better user error messages with actionable suggestions

---

## Section 1: Parse Error Taxonomy

### 1.1 Overview

Sprint 14 parse error distribution (126 failures):
- `syntax_error`: 121 (96%) - Too broad, needs subcategorization
- `internal_error`: 4 (3%)
- `validation_error`: 1 (1%)

### 1.2 Refined Parse Error Categories

#### Category 1.2.1: Lexer Errors (Tokenization)

Errors during tokenization phase - invalid characters or token formation.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `lexer_invalid_char` | Invalid Character | Character not valid in GAMS syntax | `"Unexpected character:"` |
| `lexer_unclosed_string` | Unclosed String | String literal missing closing quote | `"unclosed string"` or `"unterminated string"` |
| `lexer_invalid_number` | Invalid Number | Malformed numeric literal | `"invalid number"` or `"malformed number"` |
| `lexer_encoding_error` | Encoding Error | Non-UTF8 or invalid character encoding | `"encoding"` or `"decode"` |

**Example Error Messages:**

```
lexer_invalid_char:
  Error: Parse error at line 18, column 24: Unexpected character: '-'
    k 'horizon' / 1964-i, 1964-ii /
                       ^

lexer_unclosed_string:
  Error: Parse error at line 5, column 10: Unclosed string literal
    set i "items;
             ^
```

#### Category 1.2.2: Parser Errors (Grammar)

Errors during grammar parsing - valid tokens but invalid syntax structure.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `parser_unexpected_token` | Unexpected Token | Token not expected at this position | `"Unexpected token"` or `"expected"` |
| `parser_missing_semicolon` | Missing Semicolon | Statement not terminated with semicolon | `"Missing semicolon"` |
| `parser_unmatched_paren` | Unmatched Parenthesis | Parentheses/brackets not balanced | `"unmatched"` and (`"("` or `")"` or `"["` or `"]"`) |
| `parser_invalid_declaration` | Invalid Declaration | Malformed set/parameter/variable/equation declaration | (manual classification - no auto-detect) |
| `parser_invalid_expression` | Invalid Expression | Malformed mathematical expression | (manual classification - no auto-detect) |
| `parser_unexpected_eof` | Unexpected End of File | File ended unexpectedly | `"unexpected eof"` or `"unexpected end"` |

**Example Error Messages:**

```
parser_missing_semicolon:
  Error: Parse error at line 43, column 6: Unexpected character: 'V'
    Free Variable tcost 'total cost';
         ^
  Missing semicolon at end of line 42. Add ';' after: * -------

parser_unexpected_token:
  Error: Parse error at line 10: Unexpected token 'model' - expected ';'
```

#### Category 1.2.3: Semantic Errors (Meaning)

Errors after parsing - valid syntax but semantic issues.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `semantic_undefined_symbol` | Undefined Symbol | Reference to undeclared set/parameter/variable | `"not defined"` or `"undefined"` (not in "not defined by any equation") |
| `semantic_type_mismatch` | Type Mismatch | Wrong type used in context | `"type"` and (`"mismatch"` or `"expected"`) |
| `semantic_domain_error` | Domain Error | Invalid domain specification or usage | `"domain"` or `"incompatible domains"` |
| `semantic_duplicate_def` | Duplicate Definition | Same name declared twice | `"duplicate"` or `"already defined"` |

**Example Error Messages:**

```
semantic_undefined_symbol:
  Error: Symbol 'x' is not defined
  Suggestion: Declare 'x' as a variable before using it

semantic_domain_error:
  Error: Incompatible domains for summation: variable domain ('i',), 
         multiplier domain ('i', 'j')
```

#### Category 1.2.4: Include/File Errors

Errors related to file inclusion and external dependencies.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `include_file_not_found` | Include File Not Found | $include file doesn't exist | `"include"` and (`"not found"` or `"could not"`) |
| `include_circular` | Circular Include | Circular $include dependency | `"circular"` and `"include"` |

**Example Error Messages:**

```
include_file_not_found:
  Error: Include file 'data.gms' not found
  Suggestion: Verify the file exists and the path is correct
```

### 1.3 Sprint 14 Migration Mapping

| Sprint 14 Category | Sprint 15 Categories |
|-------------------|---------------------|
| `syntax_error` | `lexer_*`, `parser_*` (analyze message to subcategorize) |
| `validation_error` | `semantic_*` |
| `missing_include` | `include_*` |
| `internal_error` | `internal_error` (unchanged) |
| `timeout` | `timeout` (unchanged) |
| `unsupported_feature` | (move to translation stage) |

### 1.4 Parse Error Detection Algorithm

```python
def categorize_parse_error(error_message: str) -> str:
    """Categorize parse error into refined taxonomy."""
    msg_lower = error_message.lower()
    
    # Lexer errors
    if "unexpected character:" in msg_lower:
        return "lexer_invalid_char"
    if "unclosed string" in msg_lower or "unterminated string" in msg_lower:
        return "lexer_unclosed_string"
    if "invalid number" in msg_lower or "malformed number" in msg_lower:
        return "lexer_invalid_number"
    if "encoding" in msg_lower or "decode" in msg_lower:
        return "lexer_encoding_error"
    
    # Parser errors
    if "missing semicolon" in msg_lower:
        return "parser_missing_semicolon"
    if "unexpected eof" in msg_lower or "unexpected end" in msg_lower:
        return "parser_unexpected_eof"
    if "unmatched" in msg_lower and any(c in msg_lower for c in ["(", ")", "[", "]"]):
        return "parser_unmatched_paren"
    if "unexpected token" in msg_lower or ("expected" in msg_lower and "got" in msg_lower):
        return "parser_unexpected_token"
    
    # Semantic errors
    if "incompatible domains" in msg_lower or "domain" in msg_lower:
        return "semantic_domain_error"
    if "duplicate" in msg_lower or "already defined" in msg_lower:
        return "semantic_duplicate_def"
    if "type" in msg_lower and ("mismatch" in msg_lower or "expected" in msg_lower):
        return "semantic_type_mismatch"
    if ("not defined" in msg_lower or "undefined" in msg_lower) and \
       "not defined by any equation" not in msg_lower:
        return "semantic_undefined_symbol"
    
    # Include errors
    if "include" in msg_lower:
        if "circular" in msg_lower:
            return "include_circular"
        if "not found" in msg_lower or "could not" in msg_lower:
            return "include_file_not_found"
    
    # Fallback: route generic parse/syntax errors to internal_error (no dedicated schema category)
    return "internal_error"
```

---

## Section 2: Translation Error Taxonomy

### 2.1 Overview

Sprint 14 translation error distribution (17 failures out of 34 attempts):
- `unsupported_feature`: 8 (47%)
- `validation_error`: 8 (47%)
- `syntax_error`: 1 (6%)

### 2.2 Translation Error Categories

#### Category 2.2.1: Differentiation Errors

Errors during symbolic differentiation for KKT stationarity conditions.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `diff_unsupported_func` | Unsupported Function | Function not implemented for differentiation | `"Differentiation not yet implemented for function"` |
| `diff_chain_rule_error` | Chain Rule Error | Error applying chain rule | `"chain rule"` |
| `diff_numerical_error` | Differentiation Numerical Error | NaN/Inf during differentiation | `"numerical"` and `"differentiation"` |

**Unsupported Functions (from Sprint 14 data):**
- `card` - Set cardinality (not differentiable)
- `ord` - Set element ordinal (not differentiable)
- `smin`/`smax` - Set min/max (need smooth approximation)
- `gamma`/`loggamma` - Gamma functions (complex derivatives)

**Example Error Messages:**

```
diff_unsupported_func:
  Error: Differentiation not yet implemented for function 'card'. 
  Supported functions: power, exp, log, sqrt, sin, cos, tan, abs, sqr.
  Note: abs() requires --smooth-abs flag (non-differentiable at x=0).
```

#### Category 2.2.2: Model Structure Errors

Errors related to model structure during translation.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `model_no_objective_def` | Objective Not Defined | Objective variable has no defining equation | `"Objective variable"` and `"not defined by any equation"` |
| `model_domain_mismatch` | Domain Mismatch | Incompatible domains in summation/product | `"Incompatible domains"` |
| `model_missing_bounds` | Missing Variable Bounds | Required bounds not specified | `"bounds"` and `"missing"` |

**Example Error Messages:**

```
model_no_objective_def:
  Error: Invalid model - Objective variable 'f' is not defined by any equation. 
  ObjectiveIR.expr is None and no defining equation found. 
  Available equations: ['objective', 'alkylshrnk', ...]
```

#### Category 2.2.3: Unsupported Construct Errors

GAMS constructs not yet supported by nlp2mcp.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `unsup_index_offset` | Index Offset Unsupported | Lead/lag indexing not supported | `"IndexOffset not yet supported"` |
| `unsup_dollar_cond` | Dollar Conditional Unsupported | $-conditional not supported in context | `"DollarConditional"` or `"dollar conditional"` |
| `unsup_expression_type` | Unknown Expression Type | Unrecognized expression type | `"Unknown expression type"` |
| `unsup_special_ordered` | SOS Unsupported | Special Ordered Sets not supported | `"SOS"` or `"special ordered"` |

**Example Error Messages:**

```
unsup_index_offset:
  Error: IndexOffset not yet supported in this context: 
  IndexOffset(base='t', offset=SymbolRef(+), circular=False)
```

#### Category 2.2.4: Code Generation Errors

Errors during MCP GAMS code emission.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `codegen_equation_error` | Equation Generation Error | Failed to generate equation GAMS code | `"equation"` and `"generation"` |
| `codegen_variable_error` | Variable Generation Error | Failed to generate variable GAMS code | `"variable"` and `"generation"` |
| `codegen_numerical_error` | Numerical Error in Codegen | NaN/Inf value in generated code | `"Numerical error"` or (`"NaN"` or `"Inf"`) |

**Example Error Messages:**

```
codegen_numerical_error:
  Error: Numerical error in parameter 'Ndata[Antwerpen,slo]': Invalid value (value is -Inf)
  Suggestion: Check your GAMS model for division by zero or invalid operations.
```

### 2.3 Translation Error Detection Algorithm

```python
def categorize_translation_error(error_message: str) -> str:
    """Categorize translation error into refined taxonomy."""
    msg_lower = error_message.lower()
    
    # Differentiation errors
    if "differentiation not yet implemented for function" in msg_lower:
        return "diff_unsupported_func"
    if "chain rule" in msg_lower:
        return "diff_chain_rule_error"
    if "numerical" in msg_lower and "differentiation" in msg_lower:
        return "diff_numerical_error"
    
    # Model structure errors
    if "objective variable" in msg_lower and "not defined by any equation" in msg_lower:
        return "model_no_objective_def"
    if "incompatible domains" in msg_lower:
        return "model_domain_mismatch"
    if "bounds" in msg_lower and "missing" in msg_lower:
        return "model_missing_bounds"
    
    # Unsupported construct errors
    if "indexoffset not yet supported" in msg_lower:
        return "unsup_index_offset"
    if "dollarconditional" in msg_lower or "dollar conditional" in msg_lower:
        return "unsup_dollar_cond"
    if "unknown expression type" in msg_lower:
        return "unsup_expression_type"
    if "sos" in msg_lower or "special ordered" in msg_lower:
        return "unsup_special_ordered"
    
    # Code generation errors (check specific patterns before general numerical)
    if "equation" in msg_lower and "generation" in msg_lower:
        return "codegen_equation_error"
    if "variable" in msg_lower and "generation" in msg_lower:
        return "codegen_variable_error"
    if ("numerical error" in msg_lower or "nan" in msg_lower or "inf" in msg_lower) and "differentiation" not in msg_lower:
        return "codegen_numerical_error"
    
    return "internal_error"
```

---

## Section 3: Solve Outcome Taxonomy

### 3.1 Overview

This is a new stage for Sprint 15 - comparing MCP solutions with original NLP solutions.

### 3.2 Solve Outcome Categories

#### Category 3.2.1: PATH Solver Status Outcomes

Outcomes from PATH solver execution (includes both success and error states).

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `path_solve_normal` | Normal Completion | Solver completed normally (not an error) | solver_status == 1 |
| `path_solve_iteration_limit` | Iteration Limit | Solver hit iteration limit | solver_status == 2 |
| `path_solve_time_limit` | Time Limit | Solver hit time limit | solver_status == 3 |
| `path_solve_terminated` | Solver Terminated | Solver terminated by error | solver_status == 4 |
| `path_solve_eval_error` | Evaluation Error | Function evaluation errors | solver_status == 5 |
| `path_solve_license` | License Error | GAMS/PATH license issue | solver_status == 7 |

#### Category 3.2.2: Model Status Outcomes

MCP model status from solve (includes both success and error states).

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `model_optimal` | Optimal | Model solved optimally (not an error) | model_status == 1 |
| `model_locally_optimal` | Locally Optimal | Locally optimal solution found | model_status == 2 |
| `model_infeasible` | Infeasible | Model is infeasible | model_status == 4 or 5 |
| `model_unbounded` | Unbounded | Model is unbounded | model_status == 3 |

#### Category 3.2.3: Solution Comparison Outcomes

Outcomes from comparing NLP and MCP solutions.

| Error Code | Name | Description | Detection Pattern |
|------------|------|-------------|-------------------|
| `compare_objective_match` | Objective Match | Objectives match within tolerance | comparison result |
| `compare_objective_mismatch` | Objective Mismatch | Objectives differ beyond tolerance | comparison result |
| `compare_status_mismatch` | Status Mismatch | NLP and MCP have different solve status | comparison result |
| `compare_nlp_failed` | NLP Solve Failed | NLP solver failed (pre-comparison) | nlp solver_status != 1 |
| `compare_mcp_failed` | MCP Solve Failed | MCP solver failed unexpectedly (pre-comparison) | mcp solver_status not in (1,2,3,4,5,7) |
| `compare_both_infeasible` | Both Infeasible | Both NLP and MCP infeasible | both model_status in (4,5) |

Note: `compare_nlp_failed` and `compare_mcp_failed` are pre-comparison outcomes that prevent objective comparison. Specific PATH solver failures (iteration limit, time limit, etc.) are categorized in 3.2.1.

### 3.3 Solve Error Detection

```python
def categorize_solve_result(
    nlp_solver_status: int,
    nlp_model_status: int,
    mcp_solver_status: int,
    mcp_model_status: int,
    objective_match: bool | None
) -> str:
    """Categorize solve result based on status codes and comparison."""
    
    # Check solver status first (NLP)
    if nlp_solver_status != 1:
        return "compare_nlp_failed"
    
    # Check solver status (MCP/PATH)
    if mcp_solver_status != 1:
        if mcp_solver_status == 2:
            return "path_solve_iteration_limit"
        if mcp_solver_status == 3:
            return "path_solve_time_limit"
        if mcp_solver_status == 4:
            return "path_solve_terminated"
        if mcp_solver_status == 5:
            return "path_solve_eval_error"
        if mcp_solver_status == 7:
            return "path_solve_license"
        return "compare_mcp_failed"
    
    # Both solvers completed normally - check model status
    nlp_optimal = nlp_model_status in (1, 2)
    mcp_optimal = mcp_model_status in (1, 2)
    nlp_infeasible = nlp_model_status in (4, 5)
    mcp_infeasible = mcp_model_status in (4, 5)
    nlp_unbounded = nlp_model_status == 3
    mcp_unbounded = mcp_model_status == 3
    
    # Both optimal - compare objectives
    if nlp_optimal and mcp_optimal:
        if objective_match:
            return "compare_objective_match"
        else:
            return "compare_objective_mismatch"
    
    # Both infeasible
    if nlp_infeasible and mcp_infeasible:
        return "compare_both_infeasible"
    
    # MCP-specific model status outcomes
    if mcp_infeasible:
        return "model_infeasible"
    if mcp_unbounded:
        return "model_unbounded"
    
    # Status mismatch (different model statuses)
    if nlp_optimal != mcp_optimal:
        return "compare_status_mismatch"
    
    # Fallback for unexpected combinations: use generic status mismatch category
    return "compare_status_mismatch"
```

---

## Section 4: Database Storage Format

### 4.1 Error Object Structure

```json
{
  "error": {
    "category": "lexer_invalid_char",
    "subcategory": null,
    "message": "Error: Parse error at line 18, column 24: Unexpected character: '-'",
    "location": {
      "line": 18,
      "column": 24,
      "source_line": "k 'horizon' / 1964-i, 1964-ii /"
    },
    "suggestion": "This character is not valid in this context"
  }
}
```

### 4.2 Category Hierarchy

Categories follow a hierarchical naming convention:
- **Stage prefix:** `parse_`, `translate_`, `solve_`
- **Substages:** `lexer_`, `parser_`, `semantic_`, `diff_`, `model_`, `unsup_`, `codegen_`, `path_`, `compare_`
- **Specific error:** descriptive name

### 4.3 Schema Extension for Outcome Categories

```json
{
  "outcome_category": {
    "description": "Category for both error and success outcomes",
    "type": "string",
    "enum": [
      "lexer_invalid_char",
      "lexer_unclosed_string",
      "lexer_invalid_number",
      "lexer_encoding_error",
      "parser_unexpected_token",
      "parser_missing_semicolon",
      "parser_unmatched_paren",
      "parser_invalid_declaration",
      "parser_invalid_expression",
      "parser_unexpected_eof",
      "semantic_undefined_symbol",
      "semantic_type_mismatch",
      "semantic_domain_error",
      "semantic_duplicate_def",
      "include_file_not_found",
      "include_circular",
      "diff_unsupported_func",
      "diff_chain_rule_error",
      "diff_numerical_error",
      "model_no_objective_def",
      "model_domain_mismatch",
      "model_missing_bounds",
      "unsup_index_offset",
      "unsup_dollar_cond",
      "unsup_expression_type",
      "unsup_special_ordered",
      "codegen_equation_error",
      "codegen_variable_error",
      "codegen_numerical_error",
      "path_solve_normal",
      "path_solve_iteration_limit",
      "path_solve_time_limit",
      "path_solve_terminated",
      "path_solve_eval_error",
      "path_solve_license",
      "model_optimal",
      "model_locally_optimal",
      "model_infeasible",
      "model_unbounded",
      "compare_objective_match",
      "compare_objective_mismatch",
      "compare_status_mismatch",
      "compare_nlp_failed",
      "compare_mcp_failed",
      "compare_both_infeasible",
      "internal_error",
      "timeout"
    ]
  }
}
```

---

## Section 5: Migration Plan

### 5.1 Migration Strategy

Sprint 14 data will be re-categorized using the new detection algorithms. Since error messages are preserved in the database, we can reprocess them.

### 5.2 Migration Script Pseudocode

```python
def migrate_error_categories():
    """Migrate Sprint 14 error categories to Sprint 15 taxonomy."""
    db = load_database()
    
    for model in db['models']:
        # Migrate parse errors
        if model.get('nlp2mcp_parse', {}).get('status') == 'failure':
            error_msg = model['nlp2mcp_parse']['error']['message']
            old_category = model['nlp2mcp_parse']['error']['category']
            new_category = categorize_parse_error(error_msg)
            
            model['nlp2mcp_parse']['error']['category'] = new_category
            model['nlp2mcp_parse']['error']['legacy_category'] = old_category
        
        # Migrate translation errors
        if model.get('nlp2mcp_translate', {}).get('status') == 'failure':
            error_msg = model['nlp2mcp_translate']['error']['message']
            old_category = model['nlp2mcp_translate']['error']['category']
            new_category = categorize_translation_error(error_msg)
            
            model['nlp2mcp_translate']['error']['category'] = new_category
            model['nlp2mcp_translate']['error']['legacy_category'] = old_category
    
    save_database(db)
```

### 5.3 Backward Compatibility

- Keep `legacy_category` field for Sprint 14 category reference
- New categories are supersets - no information lost
- Reporting can show both for comparison during transition

---

## Section 6: Implementation Guidelines

### 6.1 Error Categorization Best Practices

1. **Check specific patterns first:** More specific patterns should be checked before general ones
2. **Use lowercase matching:** Convert to lowercase for case-insensitive matching
3. **Preserve original message:** Always store the full original error message
4. **Add structured location:** Extract line/column when available
5. **Include suggestions:** Provide actionable suggestions for user errors

### 6.2 Adding New Error Categories

When adding a new error category:
1. Add to the appropriate section in this taxonomy
2. Add detection pattern to categorization function
3. Add to schema enum
4. Add example error message
5. Update migration script if needed

### 6.3 Reporting Format

```markdown
## Parse Error Summary

| Category | Count | % | Top Subcategory |
|----------|-------|---|-----------------|
| Lexer Errors | 45 | 36% | lexer_invalid_char (42) |
| Parser Errors | 60 | 48% | parser_missing_semicolon (15) |
| Semantic Errors | 15 | 12% | semantic_domain_error (10) |
| Include Errors | 5 | 4% | include_file_not_found (5) |
```

---

## Section 7: Summary

### 7.1 Category Counts

| Stage | Categories | Subcategories | Success Outcomes | Error Types |
|-------|------------|---------------|------------------|-------------|
| Parse | 4 | 16 | 0 | 16 |
| Translation | 4 | 12 | 0 | 12 |
| Solve | 3 | 16 | 4 | 12 |
| **Total** | **11** | **44** | **4** | **40** |

**Note:** The 4 success outcomes are: `path_solve_normal`, `model_optimal`, `model_locally_optimal`, and `compare_objective_match`. All other outcomes are error types.

### 7.2 Sprint 15 Priorities

Based on Sprint 14 error distribution:

**Parse Stage (Priority 1):**
1. `lexer_invalid_char` - 96% of parse failures
2. `parser_missing_semicolon` - Common pattern in error messages

**Translation Stage (Priority 2):**
1. `model_no_objective_def` - 5 failures
2. `unsup_index_offset` - 3 failures
3. `diff_unsupported_func` - 5 failures (card, gamma, etc.)

**Solve Stage (Priority 3):**
1. Implement `compare_objective_match`/`compare_objective_mismatch`
2. Handle `compare_status_mismatch` cases

### 7.3 Future Enhancements

1. **Auto-suggestion system:** Generate fix suggestions based on error category
2. **Error clustering:** Group similar errors for batch fixes
3. **Improvement tracking:** Track error reduction per category over sprints
4. **Parser enhancement hints:** Use error patterns to guide parser improvements

---

*Document created: January 10, 2026*  
*Sprint 15 Prep Task 4*
