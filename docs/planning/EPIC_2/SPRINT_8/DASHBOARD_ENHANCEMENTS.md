# Dashboard Enhancements for Partial Parse Metrics

**Sprint:** Epic 2 - Sprint 8 Prep  
**Task:** Task 9 - Design Dashboard Enhancements  
**Created:** 2025-11-17  
**Purpose:** Design enhancements to GAMSLIB_CONVERSION_STATUS.md to display partial parse metrics, missing features, and color-coded status  
**Document Size:** 821 lines

---

## Executive Summary

**Objective:** Transform dashboard from binary pass/fail to granular progress tracking showing "himmel16: 92% parsed (22/24 lines), needs [i++1 indexing]".

**Current State:**
- Binary status: ✅ PASS (100% parsed) or ❌ FAIL (0% parsed)
- No visibility into partial progress (e.g., himmel16 parses 92% before hitting i++1 error)
- No indication of which features are missing
- 20% parse rate (2/10 models) appears stagnant

**Target State:**
- Color-coded status: ✅ (100%), 🟡 (75-99%), ⚠️ (25-74%), ❌ (<25%)
- Parse percentage displayed: "92% (22/24 lines)"
- Missing features annotated: "i++1 indexing, model sections"
- Progress visible: himmel16 is 92% done, not 0% done

**Implementation Complexity:** Low (3-4 hours)
- Dashboard template: 1 hour (add 2 columns, update symbols)
- Ingestion script: 2 hours (extract metrics from parse results)
- Testing: 1 hour (validate backward compatibility)

**Backward Compatibility:** ✅ Full compatibility
- Sprint 7 data displays correctly (shows 100% or 0%, "-" for missing features)
- No breaking changes to existing workflows
- Optional columns (default to "-" if data unavailable)

---

## Table of Contents

1. [Dashboard Mockup Design](#dashboard-mockup-design)
2. [Color Coding Scheme](#color-coding-scheme)
3. [Ingestion Script Updates](#ingestion-script-updates)
4. [Dashboard Template Modifications](#dashboard-template-modifications)
5. [Backward Compatibility Analysis](#backward-compatibility-analysis)
6. [Implementation Plan](#implementation-plan)

---

## Dashboard Mockup Design

### Enhanced Model Status Table

**New Format:**
```markdown
| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| mhw4d | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
| rbrock | ✅ PASS | 100% (156/156) | - | - | - | ❌ |
| himmel16 | 🟡 PARTIAL | 92% (22/24) | i++1 indexing | - | - | ❌ |
| circle | 🟡 PARTIAL | 100% (24/24) | function calls in assignments | - | - | ❌ |
| mathopt1 | 🟡 PARTIAL | 100% (156/156) | indexed assignments | - | - | ❌ |
| trig | 🟡 PARTIAL | 100% (67/67) | variable attributes (.l) | - | - | ❌ |
| mhw4dx | ⚠️ PARTIAL | 66% (12/18) | option statements | - | - | ❌ |
| maxmin | ⚠️ PARTIAL | 48% (42/87) | nested indexing, option statements | - | - | ❌ |
| hs62 | ❌ FAIL | 15% (11/72) | model sections (mx) | - | - | ❌ |
| mingamma | ❌ FAIL | 22% (10/45) | multiple model definitions | - | - | ❌ |
```

**Key Changes from Current Format:**
1. **Status Column:** Changed from ✅/❌ to ✅/🟡/⚠️/❌ (4 levels instead of 2)
2. **New "Progress" Column:** Shows parse percentage + line counts (e.g., "92% (22/24)")
3. **New "Missing Features" Column:** Lists features needed to achieve 100% parse
4. **More granular insight:** Can see himmel16 is 92% done vs hs62 at 15% done

### Comparison: Current vs Enhanced

**Current Dashboard (Sprint 7):**
```markdown
| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| himmel16 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| circle | ❌ | - | - | ❌ | Parse error: ParserSemanticError |
| mhw4d | ✅ | - | - | ❌ | Parsed successfully |
```

**Problem:** himmel16 and circle both show ❌, but:
- circle parses 100% of statements (semantic error after parse)
- himmel16 parses 92% of statements (syntax error on line 23/24)
- No way to distinguish "close to working" vs "completely broken"

**Enhanced Dashboard (Sprint 8):**
```markdown
| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| himmel16 | 🟡 PARTIAL | 92% (22/24) | i++1 indexing | - | - | ❌ |
| circle | 🟡 PARTIAL | 100% (24/24) | function calls in assignments | - | - | ❌ |
| mhw4d | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
```

**Benefits:**
- ✅ himmel16 clearly "closer" to working (92% vs 100% with semantic error)
- ✅ Missing features explicitly listed (i++1 indexing vs function calls)
- ✅ Progress quantified (22/24 lines vs 24/24 lines)
- ✅ Color-coded at-a-glance status (🟡 = mostly working, needs 1 feature)

---

## Color Coding Scheme

### Four-Level Status Classification

**Tier 1: ✅ GREEN (100% Parsed)**
- **Criteria:** All lines parsed successfully, no syntax or semantic errors
- **Parse %:** Exactly 100%
- **Symbol:** ✅ PASS
- **Examples:** mhw4d.gms (18/18 lines), rbrock.gms (156/156 lines)
- **User Interpretation:** "Model fully supported, ready for conversion"

**Tier 2: 🟡 YELLOW (Mostly Parsed, 75-99%)**
- **Criteria:** 75-99% of lines parsed, or 100% parsed with semantic errors
- **Parse %:** 75% ≤ progress < 100%, or 100% with semantic error
- **Symbol:** 🟡 PARTIAL
- **Examples:**
  - himmel16.gms: 92% (22/24 lines, syntax error on line 23)
  - circle.gms: 100% (24/24 lines, semantic error after parse)
  - mathopt1.gms: 100% (156/156 lines, semantic error "indexed assignments not supported")
- **User Interpretation:** "Model almost working, needs 1-2 features to unlock"

**Tier 3: ⚠️ ORANGE (Partially Parsed, 25-74%)**
- **Criteria:** 25-74% of lines parsed
- **Parse %:** 25% ≤ progress < 75%
- **Symbol:** ⚠️ PARTIAL
- **Examples:**
  - mhw4dx.gms: 66% (12/18 lines, option statement error)
  - maxmin.gms: 48% (42/87 lines, nested indexing error mid-file)
- **User Interpretation:** "Model has major blockers, needs multiple features or early error fix"

**Tier 4: ❌ RED (Mostly Failed, <25%)**
- **Criteria:** Less than 25% of lines parsed (early syntax error)
- **Parse %:** progress < 25%
- **Symbol:** ❌ FAIL
- **Examples:**
  - hs62.gms: 15% (11/72 lines, error on line 35)
  - mingamma.gms: 22% (10/45 lines, error on line 26)
- **User Interpretation:** "Model fails early, fundamental syntax issue or unsupported pattern"

### Rationale for Thresholds

**Why 75% cutoff for YELLOW?**
- Models ≥75% parsed are "close to working" (need 1-2 features typically)
- Sprint 8 targets: himmel16 (92%), circle (100% semantic), mathopt1 (100% semantic)
- Visual distinction: 🟡 = "high priority to fix" vs ⚠️ = "medium priority"

**Why 25% cutoff for RED?**
- Models <25% have early fundamental errors (not just missing features)
- Distinguishes "early blocker" (hs62 at line 35/72) from "mid-file blocker" (maxmin at line 42/87)
- RED suggests: "Check basic syntax compatibility first"

**Why include 100% semantic errors in YELLOW?**
- Semantic errors occur **after** successful parse (full AST exists)
- Indicates parser grammar is fine, just missing runtime feature
- Examples: circle (function calls), mathopt1 (indexed assignments), trig (variable attributes)
- These are "closer to working" than syntax errors (no AST)

### Color Accessibility

**Considerations:**
- Symbols used (✅ 🟡 ⚠️ ❌) are distinct even in grayscale
- Text labels (PASS, PARTIAL, FAIL) provide redundancy for color-blind users
- Dashboard is Markdown (not terminal colors), so emoji symbols render universally

---

## Ingestion Script Updates

### Current Ingestion Pipeline

**File:** `scripts/ingest_gamslib_results.py` (assumed location based on `gamslib_ingestion_sprint6.json` reference)

**Current Behavior:**
1. Parse each `.gms` model file
2. Capture parse result: SUCCESS (✅) or FAILED (❌)
3. If FAILED, capture error type and message
4. Generate `GAMSLIB_CONVERSION_STATUS.md` dashboard
5. Generate `reports/gamslib_ingestion_sprintN.json` data file

**Current Data Model (inferred from dashboard):**
```python
@dataclass
class ModelResult:
    model_name: str
    parse_status: Literal["SUCCESS", "FAILED"]
    parse_error_type: Optional[str]  # e.g., "UnexpectedCharacters"
    parse_error_message: Optional[str]
    # ... (convert_status, solve_status, etc.)
```

### Enhanced Data Model

**New Fields:**
```python
@dataclass
class ModelResult:
    # Existing fields (unchanged)
    model_name: str
    parse_status: Literal["SUCCESS", "FAILED", "PARTIAL"]  # ← PARTIAL is new
    parse_error_type: Optional[str]
    parse_error_message: Optional[str]
    
    # NEW: Partial parse metrics
    parse_progress_percentage: float  # e.g., 92.0
    parse_progress_lines_parsed: int  # e.g., 22
    parse_progress_lines_total: int   # e.g., 24
    missing_features: List[str]       # e.g., ["i++1 indexing", "model sections"]
    
    # Optional: Error location (for partial parse debugging)
    error_line: Optional[int]         # e.g., 23
    error_column: Optional[int]       # e.g., 39
```

### Parse Progress Calculation

**Algorithm (from Task 5 design):**
```python
def extract_error_line(error: Exception) -> Optional[int]:
    """Extract line number from exception."""
    if hasattr(error, 'line') and error.line is not None:
        return error.line
    # Fallback: parse from error message
    match = re.search(r'line (\d+)', str(error))
    if match:
        return int(match.group(1))
    return None


def calculate_parse_progress(source_file: Path, error: Optional[Exception]) -> Dict:
    """
    Calculate parse progress metrics.
    
    Returns:
        {
            'percentage': float,      # 0-100
            'lines_parsed': int,      # lines successfully parsed
            'lines_total': int,       # total logical lines in file
            'error_line': int|None    # line where error occurred
        }
    """
    source = source_file.read_text()
    total_lines = count_logical_lines(source)
    
    if error is None:
        # Successful parse: 100%
        return {
            'percentage': 100.0,
            'lines_parsed': total_lines,
            'lines_total': total_lines,
            'error_line': None
        }
    
    # Failed parse: count lines before error
    error_line = extract_error_line(error)
    
    if error_line is None:
        # Can't determine error location, assume early failure
        parsed_lines = 0
    else:
        parsed_lines = count_logical_lines_up_to(source, error_line)
    
    percentage = (parsed_lines / total_lines * 100) if total_lines > 0 else 0.0
    
    return {
        'percentage': round(percentage, 1),
        'lines_parsed': parsed_lines,
        'lines_total': total_lines,
        'error_line': error_line
    }


def count_logical_lines(source: str) -> int:
    """Count non-empty, non-comment lines in GAMS source."""
    lines = source.split('\n')
    in_multiline_comment = False
    count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Handle multiline comments ($ontext ... $offtext)
        if stripped.startswith('$ontext'):
            in_multiline_comment = True
            continue
        if stripped.startswith('$offtext'):
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue
        
        # Skip blank lines and single-line comments
        if not stripped or stripped.startswith('*'):
            continue
        
        # This is a logical line
        count += 1
    
    return count


def count_logical_lines_up_to(source: str, line_number: int) -> int:
    """Count logical lines from start of file up to (but not including) line_number."""
    lines = source.split('\n')
    in_multiline_comment = False
    count = 0
    
    # Process lines 0 to line_number-2 (up to but not including line_number-1, which is line_number in 1-based indexing)
    for i in range(line_number - 1):
        line = lines[i]
        stripped = line.strip()
        
        # Handle multiline comments
        if stripped.startswith('$ontext'):
            in_multiline_comment = True
            continue
        if stripped.startswith('$offtext'):
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue
        
        # Skip blank/comment lines
        if not stripped or stripped.startswith('*'):
            continue
        
        count += 1
    
    return count
```

### Missing Feature Extraction

**Algorithm (pattern matching on error messages):**
```python
def extract_missing_features(error: Exception, error_message: str) -> List[str]:
    """
    Extract missing features from parse error.
    
    Uses pattern matching on error messages to identify GAMS features
    that are blocking the parse.
    
    Returns:
        List of missing feature names (e.g., ["i++1 indexing", "option statements"])
    """
    features = []
    
    # Pattern 1: Lead/lag indexing (i++1, i--1)
    if 'i++' in error_message or 'i--' in error_message or \
       re.search(r'[a-z]\+\+\d', error_message) or re.search(r'[a-z]--\d', error_message):
        features.append("i++1 indexing (lead/lag)")
    
    # Pattern 2: Option statements
    if 'option' in error_message.lower() and 'limrow' in error_message.lower():
        features.append("option statements")
    elif 'option' in error_message.lower() and 'limcol' in error_message.lower():
        features.append("option statements")
    elif 'option' in error_message.lower() and 'decimals' in error_message.lower():
        features.append("option statements")
    
    # Pattern 3: Model sections (mx, my)
    if re.search(r'model sections?[:\s(]*m[xyz]\b', error_message, re.IGNORECASE):
        features.append("model sections (mx, my, etc.)")
    
    # Pattern 4: Nested indexing
    if re.search(r'[a-z]+\([a-z]+\(', error_message):
        features.append("nested indexing")
    
    # Pattern 5: Multiple model definitions
    if re.search(r'\bm2\b', error_message, re.IGNORECASE) or re.search(r'multiple.*model', error_message, re.IGNORECASE):
        features.append("multiple model definitions")
    
    # Pattern 6: Indexed assignments (from ParserSemanticError)
    if 'Indexed assignments' in error_message and 'not supported' in error_message:
        features.append("indexed assignments")
    
    # Pattern 7: Function calls in assignments
    if 'Call(' in error_message and 'uniform' in error_message:
        features.append("function calls in assignments (uniform, normal)")
    
    # Pattern 8: Variable attributes (.l, .m)
    if 'bound_scalar' in error_message or '.l' in error_message or '.m' in error_message:
        features.append("variable attributes (.l, .m, etc.)")
    
    # If no patterns matched, use generic message
    if not features:
        features.append("unknown syntax pattern")
    
    return features[:2]  # Limit to 2 features for readability
```

### Status Determination Logic

**Algorithm:**
```python
def determine_status_symbol(percentage: float, error: Optional[Exception]) -> str:
    """
    Determine color-coded status symbol based on parse percentage.
    
    Returns:
        "✅ PASS" | "🟡 PARTIAL" | "⚠️ PARTIAL" | "❌ FAIL"
    """
    if percentage == 100.0 and error is None:
        return "✅ PASS"
    elif percentage == 100.0 and isinstance(error, ParserSemanticError):
        # Semantic error after full parse → YELLOW (close to working)
        return "🟡 PARTIAL"
    elif percentage >= 75.0:
        return "🟡 PARTIAL"
    elif percentage >= 25.0:
        return "⚠️ PARTIAL"
    else:
        return "❌ FAIL"
```

### Ingestion Script Integration Points

**Modified Workflow:**
```python
def ingest_model(model_path: Path) -> ModelResult:
    """Enhanced ingestion with partial parse metrics."""
    source = model_path.read_text()
    model_name = model_path.stem
    
    try:
        # Attempt parse
        ast = parse_text(source)
        
        # Success: 100% parsed
        return ModelResult(
            model_name=model_name,
            parse_status="SUCCESS",
            parse_progress_percentage=100.0,
            parse_progress_lines_parsed=count_logical_lines(source),
            parse_progress_lines_total=count_logical_lines(source),
            missing_features=[],
            error_line=None,
            # ...
        )
    
    except (UnexpectedToken, UnexpectedCharacters, ParserSemanticError) as e:
        # Parse failed: calculate partial progress
        progress = calculate_parse_progress(model_path, e)
        features = extract_missing_features(e, str(e))
        
        # Determine if PARTIAL or FAILED
        if progress['percentage'] >= 25.0 or isinstance(e, ParserSemanticError):
            status = "PARTIAL"
        else:
            status = "FAILED"
        
        return ModelResult(
            model_name=model_name,
            parse_status=status,
            parse_error_type=type(e).__name__,
            parse_error_message=str(e),
            parse_progress_percentage=progress['percentage'],
            parse_progress_lines_parsed=progress['lines_parsed'],
            parse_progress_lines_total=progress['lines_total'],
            missing_features=features,
            error_line=progress['error_line'],
            # ...
        )
```

### Estimated Changes

**Lines of Code:**
- New functions: ~100 lines (calculate_parse_progress, count_logical_lines, extract_missing_features, determine_status_symbol)
- Modified ingestion: ~30 lines (integrate new functions into existing workflow)
- Data model: ~10 lines (add new fields to ModelResult)
- **Total:** ~140 lines

**Complexity:** Medium
- Line counting: Straightforward (string parsing)
- Feature extraction: Pattern matching (can refine over time)
- Integration: Fits into existing try/except structure

**Implementation Time:** 2 hours
- 1 hour: Implement line counting + feature extraction functions
- 30 minutes: Integrate into ingestion workflow
- 30 minutes: Testing + refinement

---

## Dashboard Template Modifications

### Template Structure Changes

**Current Template (Sprint 7):**
```markdown
| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| {model} | {✅/❌} | {✅/❌/-} | {✅/❌/-} | {✅/❌} | {notes} |
```

**Enhanced Template (Sprint 8):**
```markdown
| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| {model} | {✅/🟡/⚠️/❌ + label} | {pct}% ({parsed}/{total}) | {features or "-"} | {✅/❌/-} | {✅/❌/-} | {✅/❌} |
```

**Changes:**
1. **"Parse" → "Status":** Column renamed to accommodate new 4-level status
2. **New "Progress" column:** Shows "{percentage}% ({lines_parsed}/{lines_total})"
3. **New "Missing Features" column:** Shows comma-separated feature list or "-"
4. **"Notes" column removed:** Information now in Status/Progress/Missing columns

### Template Generation Logic

**Pseudocode:**
```python
def generate_model_row(result: ModelResult) -> str:
    """Generate Markdown table row for model."""
    
    # Status column: symbol + label
    status = determine_status_symbol(result.parse_progress_percentage, result.parse_error_type)
    
    # Progress column: percentage + line counts
    progress = f"{result.parse_progress_percentage:.0f}% ({result.parse_progress_lines_parsed}/{result.parse_progress_lines_total})"
    
    # Missing Features column: comma-separated or "-"
    if result.missing_features:
        features = ", ".join(result.missing_features)
    else:
        features = "-"
    
    # Convert/Solve/E2E columns (unchanged logic)
    convert = format_status(result.convert_status)
    solve = format_status(result.solve_status)
    e2e = format_status(result.e2e_status)
    
    return f"| {result.model_name} | {status} | {progress} | {features} | {convert} | {solve} | {e2e} |"
```

### Example Rows

**Successful Parse (100%):**
```markdown
| mhw4d | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
```

**High Partial Parse (92%, 🟡):**
```markdown
| himmel16 | 🟡 PARTIAL | 92% (22/24) | i++1 indexing (lead/lag) | - | - | ❌ |
```

**Semantic Error After Full Parse (100%, 🟡):**
```markdown
| circle | 🟡 PARTIAL | 100% (24/24) | function calls in assignments (uniform, normal) | - | - | ❌ |
```

**Medium Partial Parse (66%, ⚠️):**
```markdown
| mhw4dx | ⚠️ PARTIAL | 66% (12/18) | option statements | - | - | ❌ |
```

**Low Partial Parse (15%, ❌):**
```markdown
| hs62 | ❌ FAIL | 15% (11/72) | model sections (mx, my, etc.) | - | - | ❌ |
```

### Legend Updates

**Current Legend:**
```markdown
**Legend:**
- ✅ Success
- ❌ Failed
- `-` Not attempted (stage not implemented yet)
```

**Enhanced Legend:**
```markdown
**Legend:**
- ✅ PASS: 100% parsed successfully
- 🟡 PARTIAL: 75-99% parsed, or 100% with semantic errors
- ⚠️ PARTIAL: 25-74% parsed
- ❌ FAIL: <25% parsed
- `-` Not attempted (stage not implemented yet)
```

### Overall KPIs Section

**Current KPIs:**
```markdown
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 20.0% (2/10) | ≥10% | ✅ |
```

**Enhanced KPIs (Optional - not required for Sprint 8):**
```markdown
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 20.0% (2/10) | ≥10% | ✅ |
| **Partial Parse** | 60.0% (6/10) | N/A | ℹ️ 6 models parse ≥75% |
| **Avg Parse %** | 71.3% | N/A | ℹ️ Average across all models |
```

**Rationale:** Optional enhancement shows that 60% of models are "close to working" (parse ≥75%), highlighting Sprint 8's impact.

---

## Backward Compatibility Analysis

### Compatibility Matrix

| Aspect | Sprint 7 Data | Sprint 8 Data | Backward Compatible? |
|--------|---------------|---------------|----------------------|
| **Data Model** | ModelResult v1 | ModelResult v2 (+ 5 new optional fields) | ✅ Yes - old parsers ignore new fields |
| **Dashboard Columns** | 6 columns | 7 columns (Parse → Status + Progress + Missing) | ✅ Yes - pure Markdown, no schema |
| **Status Symbols** | ✅/❌ | ✅/🟡/⚠️/❌ | ✅ Yes - ✅/❌ still valid values |
| **JSON Schema** | `parse_status: SUCCESS\|FAILED` | `parse_status: SUCCESS\|PARTIAL\|FAILED` | ⚠️ Minor - need PARTIAL enum value |
| **Ingestion Script** | Old version | New version | ✅ Yes - can read old + new data |
| **Rendering** | GitHub Markdown | GitHub Markdown | ✅ Yes - emojis render natively |

### Sprint 7 Data Handling

**Scenario:** Ingestion script runs on Sprint 7 data (no partial metrics available)

**Solution:** Default values for missing fields
```python
# When parsing Sprint 7 results (missing new fields)
if result.parse_status == "SUCCESS":
    # Default: 100% parsed
    result.parse_progress_percentage = 100.0
    result.parse_progress_lines_parsed = count_logical_lines(source)
    result.parse_progress_lines_total = result.parse_progress_lines_parsed
    result.missing_features = []
elif result.parse_status == "FAILED":
    # Default: 0% parsed
    result.parse_progress_percentage = 0.0
    result.parse_progress_lines_parsed = 0
    result.parse_progress_lines_total = count_logical_lines(source)
    result.missing_features = ["Parse failed - see error details"]
```

**Dashboard Output for Sprint 7 Data:**
```markdown
| mhw4d | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
| himmel16 | ❌ FAIL | 0% (0/24) | Parse failed - see error details | - | - | ❌ |
```

**Degradation:** Minimal
- Sprint 7 models show as 100% or 0% (binary, as before)
- Missing features default to generic message for FAILED models
- No functionality lost, just less granular than fresh Sprint 8 data

### Schema Evolution Strategy

**JSON Schema Versioning:**
```json
{
  "schema_version": "2.0",
  "generated_at": "2025-11-17T10:30:00Z",
  "sprint": "Sprint 8",
  "models": [
    {
      "model_name": "himmel16",
      "parse_status": "PARTIAL",
      
      // Sprint 7 fields (preserved)
      "parse_error_type": "UnexpectedCharacters",
      "parse_error_message": "...",
      
      // Sprint 8 fields (new)
      "parse_progress_percentage": 92.0,
      "parse_progress_lines_parsed": 22,
      "parse_progress_lines_total": 24,
      "missing_features": ["i++1 indexing (lead/lag)"],
      "error_line": 23,
      "error_column": 39
    }
  ]
}
```

**Versioning Rules:**
1. `schema_version: "1.0"` → Sprint 7 data (no partial metrics)
2. `schema_version: "2.0"` → Sprint 8 data (includes partial metrics)
3. Readers check `schema_version` and handle accordingly
4. Old readers (v1) ignore unknown fields (JSON is forward-compatible)

### Breaking Changes: None

**Validation:**
- ✅ No removal of existing fields
- ✅ No change to existing field types (except parse_status enum extension)
- ✅ All new fields are optional (can be omitted or defaulted)
- ✅ Dashboard is pure Markdown (no schema to break)
- ✅ Ingestion script can read Sprint 7 + Sprint 8 data

**Migration Required:** None
- Existing dashboards continue to work (just less detailed)
- Existing JSON reports remain valid (just missing new fields)
- Existing workflows (CI, scripts) unaffected

---

## Implementation Plan

### Phase 1: Ingestion Script Updates (2 hours)

**Tasks:**
1. Implement `count_logical_lines(source)` function (30 min)
   - Handle blank lines, comments, multiline comments
   - Test on GAMSLib models for accuracy
2. Implement `calculate_parse_progress(source, error)` function (30 min)
   - Extract error line from exception
   - Calculate parsed/total line counts
3. Implement `extract_missing_features(error, error_msg)` function (45 min)
   - Pattern matching for 8+ known feature types
   - Test on GAMSLib errors for coverage
4. Integrate into existing ingestion workflow (15 min)
   - Modify try/except to capture new metrics
   - Update ModelResult with new fields

**Deliverables:**
- Modified ingestion script with ~140 new lines
- Unit tests for line counting + feature extraction
- Verified on GAMSLib test set (10 models)

### Phase 2: Dashboard Template Updates (1 hour)

**Tasks:**
1. Update table header (5 min)
   - Rename "Parse" → "Status"
   - Add "Progress" column
   - Add "Missing Features" column
2. Update `generate_model_row()` function (20 min)
   - Format status symbol (✅/🟡/⚠️/❌ + label)
   - Format progress (percentage + line counts)
   - Format missing features (comma-separated or "-")
3. Update legend (5 min)
   - Add 4-level status descriptions
4. Test rendering (30 min)
   - Generate dashboard from Sprint 8 data
   - Verify Markdown rendering on GitHub
   - Verify emoji compatibility

**Deliverables:**
- Updated dashboard template
- Example dashboard output (all 10 models)
- Screenshot/preview of rendered dashboard

### Phase 3: Backward Compatibility Testing (1 hour)

**Tasks:**
1. Test with Sprint 7 data (30 min)
   - Run ingestion on old JSON reports
   - Verify default values populate correctly
   - Verify dashboard renders without errors
2. Test schema evolution (15 min)
   - Add `schema_version` field to JSON output
   - Verify old readers ignore new fields
3. Validate no breaking changes (15 min)
   - Check existing CI scripts still work
   - Check existing workflows unaffected

**Deliverables:**
- Test report confirming backward compatibility
- Documentation of default value behavior
- Schema version migration plan (if needed)

### Total Effort Estimate

- Phase 1: 2 hours (ingestion script)
- Phase 2: 1 hour (dashboard template)
- Phase 3: 1 hour (testing)
- **Total: 4 hours**

**Risk Buffer:** Low (simple enhancements, well-defined scope)
- No parser changes required (pure post-processing)
- No breaking changes (additive only)
- Markdown rendering is straightforward (GitHub supports emojis natively)

### Implementation Schedule (Sprint 8 Days 4-5)

**Day 4 (2 hours):**
- Morning: Implement ingestion script updates
- Afternoon: Test on GAMSLib models

**Day 5 (2 hours):**
- Morning: Update dashboard template
- Afternoon: Backward compatibility testing + documentation

**Checkpoint:** End of Day 5
- ✅ Dashboard shows partial metrics for all 10 models
- ✅ Backward compatibility verified with Sprint 7 data
- ✅ All tests pass

---

## Summary

**Dashboard Enhancements for Sprint 8:**

1. **Color-Coded Status:** ✅ (100%), 🟡 (75-99%), ⚠️ (25-74%), ❌ (<25%)
2. **Parse Progress:** Shows percentage + line counts (e.g., "92% (22/24)")
3. **Missing Features:** Lists blockers (e.g., "i++1 indexing, option statements")
4. **Backward Compatible:** Sprint 7 data displays correctly with defaults

**Key Benefits:**
- ✅ Visibility into partial progress (himmel16 is 92% done, not 0%)
- ✅ Clear prioritization (🟡 models need only 1-2 features)
- ✅ Feature-based roadmap (missing features drive Sprint 8b/9 planning)
- ✅ Motivational impact (progress visible even when not at 100%)

**Implementation:**
- Effort: 4 hours (2h ingestion + 1h template + 1h testing)
- Complexity: Low (no parser changes, pure post-processing)
- Risk: Low (additive changes, full backward compatibility)

**Example Output:**
```markdown
| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| himmel16 | 🟡 PARTIAL | 92% (22/24) | i++1 indexing (lead/lag) | - | - | ❌ |
| circle | 🟡 PARTIAL | 100% (24/24) | function calls in assignments | - | - | ❌ |
| mhw4d | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
```

**Sprint 8 Impact:**
- Parse rate visibility: 20% (binary) → "60% of models parse ≥75%" (nuanced)
- Feature prioritization: "What's blocking circle?" → "Function calls in assignments"
- Progress tracking: "himmel16 stuck at 0%" → "himmel16 at 92%, needs i++1 indexing"
