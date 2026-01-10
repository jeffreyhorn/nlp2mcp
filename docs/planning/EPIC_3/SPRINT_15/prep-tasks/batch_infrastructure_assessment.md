# Batch Infrastructure Assessment

**Task:** Sprint 15 Prep Task 2  
**Date:** January 9, 2026  
**Purpose:** Analyze existing batch_parse.py and batch_translate.py to determine reuse strategy for Sprint 15

---

## Executive Summary

Sprint 14 delivered robust batch processing infrastructure in `batch_parse.py` and `batch_translate.py`. These scripts provide:

- Complete batch processing with progress reporting
- Database integration (load, save, backup)
- Error categorization (6 categories)
- CLI with filtering options (--model, --limit, --dry-run)
- Timing and statistics

**Recommendation:** Sprint 15 should **extend** these scripts rather than create new test_parse.py/test_translate.py. The existing infrastructure handles 90%+ of requirements. Enhancements needed:
1. Add more error subcategories (refine syntax_error)
2. Add --only-failing and status-based filters
3. Create test_solve.py following the same patterns
4. Create run_full_test.py as an orchestrator

**Estimated Effort Savings:** 12-16 hours by reusing existing infrastructure vs. building from scratch.

---

## Section 1: batch_parse.py Analysis

### 1.1 Functionality Overview

| Feature | Implementation | Notes |
|---------|----------------|-------|
| Entry Point | `main()` with argparse | Clean CLI structure |
| Batch Processing | `run_batch_parse()` | Iterates through candidates |
| Single Model Parse | `parse_single_model()` | Uses `src.ir.parser.parse_model_file` |
| Error Categorization | `categorize_error()` | 6 categories from schema |
| Progress Reporting | Every 10 models | Shows success/failure counts, ETA |
| Database Integration | Uses `db_manager` module | Load, save, backup |

### 1.2 Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--dry-run` | flag | false | Preview without changes |
| `--limit N` | int | None | Process first N models |
| `--model ID` | str | None | Process single model |
| `--verbose` | flag | false | Detailed output |
| `--save-every N` | int | 10 | Save frequency |

### 1.3 Database Integration

**Loading:**
```python
from scripts.gamslib.db_manager import load_database, save_database, create_backup
database = load_database()
```

**Model Selection:**
```python
def get_candidate_models(database):
    # Filters for convexity.status in ('verified_convex', 'likely_convex')
```

**Update Pattern:**
```python
parse_entry = {
    "status": result["status"],
    "parse_date": datetime.now(UTC).isoformat(),
    "nlp2mcp_version": nlp2mcp_version,
    "parse_time_seconds": result.get("parse_time_seconds"),
    "variables_count": result.get("variables_count"),  # if success
    "equations_count": result.get("equations_count"),  # if success
    "error": result.get("error"),  # if failure
}
db_model["nlp2mcp_parse"] = parse_entry
```

### 1.4 Error Categorization

Current categories (from `categorize_error()` function):

| Category | Detection Patterns | Sprint 14 % |
|----------|-------------------|-------------|
| `syntax_error` | parse error, unexpected character/token, syntax error | 77% |
| `unsupported_feature` | not yet implemented, unsupported | 14.3% |
| `validation_error` | domain, incompatible, not defined, undefined | 5.6% |
| `missing_include` | include, file not found | 2.4% |
| `timeout` | timeout | 0% |
| `internal_error` | default fallback | 0.8% |

**Note:** "syntax_error" is a catch-all that needs refinement for Sprint 15.

### 1.5 Progress Reporting

```python
logger.info(
    f"[{i:3d}/{len(candidates)}] {i * 100 // len(candidates):3d}% "
    f"Processing {model_id}... "
    f"({stats['success']} success, {stats['failure']} failure, "
    f"~{remaining:.0f}s remaining)"
)
```

### 1.6 Summary Statistics

Collects and reports:
- Total, processed, success, failure, skipped counts
- Error category distribution
- Successful model list
- Total time and average time per model
- Success rate percentage

### 1.7 Strengths

1. **Robust error handling** - try/except with categorization
2. **Progress visibility** - real-time progress with ETA
3. **Periodic saves** - prevents data loss on crash
4. **Backup creation** - automatic before batch operations
5. **Timing measurement** - uses `time.perf_counter()` for accuracy
6. **Clean separation** - single model function vs. batch orchestration
7. **Direct parser import** - calls `parse_model_file()` directly (fast, no subprocess)

### 1.8 Limitations

1. **Limited error subcategories** - 77% in "syntax_error" catch-all
2. **No status-based filtering** - can't filter by --only-failing
3. **No error category filter** - can't re-run specific error types
4. **No partial success tracking** - binary success/failure only
5. **Model statistics not fully utilized** - variables/equations count captured but not for filtering

### 1.9 Extension Opportunities

| Enhancement | Effort | Value |
|-------------|--------|-------|
| Add `--only-failing` filter | 1h | High |
| Add `--error-category` filter | 1h | Medium |
| Refine syntax_error subcategories | 2-3h | High |
| Add `--parse-success/failure` filters | 1h | Medium |
| Add model statistics to output | 0.5h | Low |

---

## Section 2: batch_translate.py Analysis

### 2.1 Functionality Overview

| Feature | Implementation | Notes |
|---------|----------------|-------|
| Entry Point | `main()` with argparse | Mirrors batch_parse.py |
| Batch Processing | `run_batch_translate()` | Iterates through parsed models |
| Single Model Translate | `translate_single_model()` | Uses subprocess to call CLI |
| Error Categorization | `categorize_translation_error()` | 5 categories |
| Progress Reporting | Every 5 models | Shows success/failure counts |
| MCP Output | `data/gamslib/mcp/{model_id}_mcp.gms` | Writes generated MCP files |

### 2.2 Command-Line Arguments

Identical to batch_parse.py:
- `--dry-run`, `--limit`, `--model`, `--verbose`, `--save-every`

### 2.3 Model Selection

```python
def get_parsed_models(database):
    # Filters for nlp2mcp_parse.status == "success"
```

**Key difference:** Only processes successfully parsed models.

### 2.4 Translation Execution

Uses subprocess (not direct import):
```python
cmd = [
    sys.executable,
    "-m",
    "src.cli",
    str(model_path),
    "-o",
    str(output_path),
    "--quiet",
]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = proc.communicate(timeout=60)
```

**Timeout:** 60 seconds with proper cleanup on timeout.

### 2.5 Error Categorization

| Category | Detection Patterns |
|----------|-------------------|
| `timeout` | timeout |
| `unsupported_feature` | not yet implemented, not yet supported, unsupported |
| `validation_error` | invalid model, not defined, undefined, validation, incompatible |
| `syntax_error` | parse error, syntax error, unexpected |
| `internal_error` | default fallback |

### 2.6 MCP Output Management

- Output directory: `data/gamslib/mcp/`
- Naming convention: `{model_id}_mcp.gms`
- Directory created automatically: `output_path.parent.mkdir(parents=True, exist_ok=True)`

### 2.7 Database Update Pattern

```python
translate_entry = {
    "status": result["status"],
    "translate_date": datetime.now(UTC).isoformat(),
    "nlp2mcp_version": nlp2mcp_version,
    "translate_time_seconds": result.get("translate_time_seconds"),
    "output_file": result.get("output_file"),  # if success
    "error": result.get("error"),  # if failure
}
db_model["nlp2mcp_translate"] = translate_entry
```

### 2.8 Strengths

1. **Consistent patterns** - mirrors batch_parse.py structure
2. **Subprocess isolation** - translation in separate process (safer)
3. **Timeout handling** - 60s timeout with proper process cleanup
4. **MCP file management** - writes to organized output directory
5. **Respects pipeline order** - only translates parsed models

### 2.9 Limitations

1. **Subprocess overhead** - slower than direct import
2. **No --only-failing filter** - same as batch_parse.py
3. **No translation-specific error subcategories** - limited differentiation
4. **No syntax validation** - doesn't validate generated MCP syntax before solving

### 2.10 Extension Opportunities

| Enhancement | Effort | Value |
|-------------|--------|-------|
| Add `--only-failing` filter | 1h | High |
| Add `--translate-success/failure` filters | 1h | Medium |
| Refine translation error subcategories | 2h | High |
| Add MCP syntax validation | 2h | Medium |
| Add mcp_variables_count, mcp_equations_count | 1h | Low |

---

## Section 3: Comparison and Shared Patterns

### 3.1 Consistent Patterns (Reusable for test_solve.py)

| Pattern | batch_parse.py | batch_translate.py |
|---------|----------------|-------------------|
| CLI structure | argparse with --dry-run, --limit, --model, --verbose | Same |
| Progress reporting | Every N models with ETA | Same |
| Database backup | `create_backup()` before batch | Same |
| Periodic saves | Every N models | Same |
| Statistics collection | dict with counts, times, lists | Same |
| Summary printing | `print_summary()` function | Same |
| Error categorization | `categorize_*_error()` function | Same |
| Logging | `logging.basicConfig()` with timestamps | Same |

### 3.2 Differences

| Aspect | batch_parse.py | batch_translate.py |
|--------|----------------|-------------------|
| Execution method | Direct import | Subprocess |
| Timeout | No explicit timeout | 60 seconds |
| Output files | None | MCP files in data/gamslib/mcp/ |
| Model selection | convexity.status filter | nlp2mcp_parse.status filter |
| Save frequency | Every 10 | Every 5 |
| Progress frequency | Every 10 | Every 5 |

### 3.3 Code Reuse Opportunities

**Shared utilities that could be extracted:**

1. **Progress reporter class** - encapsulate ETA calculation and formatting
2. **Statistics collector class** - standardize stats collection
3. **Filter builder** - common filter logic for --model, --limit, --only-failing
4. **Summary printer** - unified summary output format

**Estimated refactoring effort:** 4-6 hours (optional, not required for Sprint 15)

---

## Section 4: Sprint 15 Implementation Strategy

### 4.1 Recommended Approach: Extend Existing Scripts

**Option A (Recommended): Extend batch_parse.py and batch_translate.py**
- Add new filter flags (--only-failing, --parse-success, --error-category)
- Refine error categorization with subcategories
- Minimal code changes, proven infrastructure

**Option B: Create new test_parse.py and test_translate.py**
- More flexibility for Sprint 15-specific features
- Risk of duplicating code
- More testing required

**Recommendation:** Option A - extend existing scripts.

### 4.2 New Script: test_solve.py

Create following the batch_translate.py pattern:

```python
# Key functions to implement:
def get_translated_models(database):
    # Filter for nlp2mcp_translate.status == "success"

def solve_single_model(mcp_path, original_model):
    # Run GAMS with PATH solver
    # Extract objective value from .lst
    # Compare with NLP objective

def categorize_solve_error(error_message):
    # solve_optimal, solve_infeasible, comparison_mismatch, etc.
```

### 4.3 New Script: run_full_test.py

Orchestrator that calls the stage scripts:

```python
def run_full_pipeline(args):
    if not args.skip_parse:
        run_batch_parse(...)
    if not args.skip_translate:
        run_batch_translate(...)
    if not args.skip_solve:
        run_batch_solve(...)
    generate_report(...)
```

### 4.4 Implementation Priority

1. **Day 1-2:** Add filters to batch_parse.py and batch_translate.py
2. **Day 3-5:** Create test_solve.py
3. **Day 6-7:** Create run_full_test.py
4. **Day 8-9:** Integration testing and refinements
5. **Day 10:** Documentation and baseline recording

---

## Section 5: Effort Savings Estimate

### 5.1 Build from Scratch Estimate

| Component | Effort |
|-----------|--------|
| test_parse.py | 8-10h |
| test_translate.py | 6-8h |
| test_solve.py | 10-12h |
| run_full_test.py | 6-8h |
| **Total** | **30-38h** |

### 5.2 Extend Existing Estimate

| Component | Effort |
|-----------|--------|
| Extend batch_parse.py | 2-3h |
| Extend batch_translate.py | 2-3h |
| Create test_solve.py (new, using patterns) | 8-10h |
| Create run_full_test.py | 4-6h |
| **Total** | **16-22h** |

### 5.3 Savings

- **Effort saved:** 12-16 hours (40-45% reduction)
- **Risk reduction:** Proven infrastructure vs. new code
- **Consistency:** Same patterns across all stages

---

## Section 6: Verification of Known Unknowns

### Unknown 1.1: Should test_parse.py extend or replace batch_parse.py?

**Status:** ✅ VERIFIED

**Finding:** batch_parse.py should be **extended** rather than replaced. It provides:
- Robust batch processing with progress reporting
- Database integration (load, save, backup)
- Error categorization infrastructure
- CLI with useful filters (--model, --limit, --dry-run)
- Direct parser import for fast execution

**Recommendation:** Add new filter flags to batch_parse.py:
- `--only-failing` - re-run only failed models
- `--error-category=X` - filter by specific error type
- `--parse-success/--parse-failure` - status-based filtering

### Unknown 1.2: What additional error categories are needed beyond Sprint 14's 7 categories?

**Status:** ✅ VERIFIED

**Finding:** The current 6 error categories (syntax_error, unsupported_feature, validation_error, missing_include, timeout, internal_error) are well-structured, but "syntax_error" at 77% needs subcategorization.

**Recommendation:** Refine syntax_error into subcategories in Task 4 (Error Taxonomy):
- `lexer_unknown_character` - unexpected character errors
- `parser_equation_syntax` - equation parsing failures
- `parser_expression_syntax` - expression parsing failures
- `parser_unsupported_construct` - valid GAMS but not in our grammar

These can be implemented as `error.details` or as new enum values in schema v2.1.0.

### Unknown 2.1: Should test_translate.py extend or replace batch_translate.py?

**Status:** ✅ VERIFIED

**Finding:** batch_translate.py should be **extended** rather than replaced. It provides:
- Consistent patterns with batch_parse.py
- Subprocess isolation for translation safety
- Timeout handling (60s with cleanup)
- MCP file output management
- Database integration

**Recommendation:** Add same filter flags as batch_parse.py for consistency.

### Unknown 2.2: How to validate generated MCP syntax without solving?

**Status:** ✅ VERIFIED

**Finding:** GAMS supports compilation without solving using `action=c`:
```bash
gams generated_mcp.gms action=c
```

**Recommendation:** Add optional syntax validation step in test_solve.py before PATH solve:
1. Run `gams model.gms action=c` to check syntax
2. If syntax check fails, categorize as `codegen_syntax_error`
3. If syntax check passes, proceed to PATH solve

This prevents wasting solver time on syntactically invalid MCP files.

---

## Appendix A: db_manager.py Utilities

Key functions used by batch scripts:

```python
# scripts/gamslib/db_manager.py
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

def load_database() -> dict:
    """Load database from JSON file."""

def save_database(database: dict) -> None:
    """Save database to JSON file."""

def create_backup() -> Path:
    """Create timestamped backup in archive/ directory."""
```

---

## Appendix B: Schema Fields Reference

### parse_result (from schema.json)

```json
{
  "status": "success|failure|partial|not_tested",
  "parse_date": "ISO 8601 timestamp",
  "nlp2mcp_version": "0.7.0",
  "parse_time_seconds": 1.234,
  "variables_count": 15,
  "equations_count": 8,
  "error": {
    "category": "syntax_error|unsupported_feature|...",
    "message": "Error details"
  }
}
```

### translate_result (from schema.json)

```json
{
  "status": "success|failure|not_tested",
  "translate_date": "ISO 8601 timestamp",
  "nlp2mcp_version": "0.7.0",
  "translate_time_seconds": 0.567,
  "output_file": "data/gamslib/mcp/model_mcp.gms",
  "error": {
    "category": "unsupported_feature|validation_error|...",
    "message": "Error details"
  }
}
```

---

*Document created: January 9, 2026*  
*Sprint 15 Prep Task 2*
