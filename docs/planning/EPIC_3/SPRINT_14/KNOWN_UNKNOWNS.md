# Sprint 14 Known Unknowns

**Created:** January 1, 2026  
**Status:** Active - Pre-Sprint 14  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 14 complete convexity verification, JSON database schema design, database management scripts, and version control strategy

---

## Executive Summary

This document identifies all assumptions and unknowns for Sprint 14 features **before** implementation begins. This proactive approach continues the highly successful methodology from previous sprints that prevented late-stage surprises.

**Sprint 14 Scope:**
1. Complete Convexity Verification - Batch verification on all candidate models, results integration
2. JSON Database Schema Design - Comprehensive schema for pipeline tracking, validation with jsonschema
3. Database Management Scripts - db_manager.py with CRUD operations, queries, exports
4. JSON Database Version Control Strategy - Schema versioning, migration patterns
5. Multi-Solver Validation (Optional) - Secondary solver verification if available

**Reference:** See `docs/planning/EPIC_3/PROJECT_PLAN.md` lines 92-223 for complete Sprint 14 deliverables and acceptance criteria.

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 4: 23 unknowns, zero blocking issues
- Sprint 5: 22 unknowns, all resolved on schedule
- Sprint 6: 22 unknowns, enabled realistic scope setting
- Sprint 7: 25 unknowns, achieved 30% parse rate goal
- Sprint 13: 26 unknowns verified, 100% acceptance criteria met

**Sprint 13 Key Learning:** GAMSLIB corpus infrastructure is complete with 219 models cataloged, 160 verified as convex/likely_convex. Sprint 14 builds on this foundation to design the JSON database schema and run batch verification through the nlp2mcp pipeline.

---

## How to Use This Document

### Before Sprint 14 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE -> [x] COMPLETE or ❌ WRONG (with correction)

### During Sprint 14
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 26  
**By Priority:**
- Critical: 6 (unknowns that could derail sprint or block database integration)
- High: 11 (unknowns requiring upfront research)
- Medium: 6 (unknowns that can be resolved during implementation)
- Low: 3 (nice-to-know, low impact)

**By Category:**
- Category 1 (Complete Convexity Verification): 5 unknowns
- Category 2 (JSON Database Schema Design): 7 unknowns
- Category 3 (Database Management Scripts): 6 unknowns
- Category 4 (JSON Database Version Control Strategy): 4 unknowns
- Category 5 (Multi-Solver Validation): 4 unknowns

**Estimated Research Time:** 28-36 hours (spread across prep phase)

---

## Table of Contents

1. [Category 1: Complete Convexity Verification](#category-1-complete-convexity-verification)
2. [Category 2: JSON Database Schema Design](#category-2-json-database-schema-design)
3. [Category 3: Database Management Scripts](#category-3-database-management-scripts)
4. [Category 4: JSON Database Version Control Strategy](#category-4-json-database-version-control-strategy)
5. [Category 5: Multi-Solver Validation](#category-5-multi-solver-validation)
6. [Template for New Unknowns](#template-for-new-unknowns)
7. [Next Steps](#next-steps)

---

# Category 1: Complete Convexity Verification

## Unknown 1.1: How long will batch verification of 160+ models take?

### Priority
**High** - Affects Sprint 14 scheduling

### Assumption
Batch verification of 160 verified_convex and likely_convex models through the nlp2mcp pipeline will complete in a reasonable time (under 2 hours).

### Research Questions
1. What is the average parse/translate time per model in the current nlp2mcp pipeline?
2. Are there models that take significantly longer due to size or complexity?
3. Should verification run in parallel or sequential to avoid resource contention?
4. How does GAMS license affect batch execution (demo limits)?
5. What is the timeout strategy for hung models?

### How to Verify

**Test Case 1: Measure single model timing**
```bash
time python3 -m src.cli data/gamslib/raw/trnsport.gms --parse-only
# Record: parse time for simple LP model
```

**Test Case 2: Sample batch timing**
```bash
# Run on 10 representative models, extrapolate to 160
for model in $(head -10 verified_models.txt); do
    time python3 -m src.cli data/gamslib/raw/$model.gms --parse-only 2>&1
done
```

**Test Case 3: Measure nlp2mcp full pipeline**
```bash
time python3 -m src.cli data/gamslib/raw/trnsport.gms -o /tmp/output.gms
# Record: parse + translate time
```

### Risk if Wrong
- Sprint 14 scheduling may be unrealistic
- May need parallelization strategy mid-sprint
- Could run out of GAMS license executions

### Estimated Research Time
2-3 hours (sample timing, extrapolation, resource planning)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: What percentage of verified models will successfully parse through nlp2mcp?

### Priority
**Critical** - Determines Sprint 14 baseline and success metrics

### Assumption
At least 30% of the 160 verified models will parse successfully through nlp2mcp, based on prior parser improvements.

### Research Questions
1. What is the current parse success rate for GAMSLIB models?
2. Which syntax features block the most models (from prior analysis)?
3. Has the parser been enhanced since the last GAMSLIB parse rate measurement?
4. Are LP models more likely to parse than NLP models?
5. What are the top 5 parse failure reasons?

### How to Verify

**Test Case 1: Run parse on sample**
```bash
# Sample 20 models, measure parse success
python3 scripts/gamslib/test_parse_sample.py --sample-size=20
```

**Test Case 2: Categorize failures**
```bash
# Group parse errors by category
python3 -m src.cli data/gamslib/raw/problem.gms 2>&1 | grep -i "error"
```

**Test Case 3: Compare LP vs NLP success rates**
```bash
# Parse LP models (86 total)
# Parse NLP models (120 total)
# Compare success percentages
```

### Risk if Wrong
- If <10% parse rate: Sprint 14 value significantly reduced
- If >50% parse rate: May need to adjust testing scope
- Inaccurate baseline leads to wrong KPIs

### Estimated Research Time
3-4 hours (batch parse, error analysis, categorization)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: How should models with license limit errors be handled?

### Priority
**High** - 10 models affected per catalog quality analysis

### Assumption
Models that hit GAMS demo license limits should be marked as "license_limited" and excluded from pipeline testing until full license is available.

### Research Questions
1. Can we detect license limit errors programmatically from parse/solve output?
2. Should we attempt to simplify models to fit within demo limits?
3. Are there alternative solvers that have more generous demo limits?
4. Should license-limited models be tracked separately in the database?
5. Can we get a full GAMS license for CI/CD?

### How to Verify

**Test Case 1: Identify license error pattern**
```bash
# Run a known license-limited model
python3 -m src.cli data/gamslib/raw/large_model.gms 2>&1 | grep -i "license"
```

**Test Case 2: Check if parse alone hits limits**
```bash
# Does parsing (no solve) trigger license limits?
python3 -m src.cli data/gamslib/raw/large_model.gms --parse-only 2>&1
```

**Test Case 3: Document license limit thresholds**
```
# GAMS Demo license limits:
# - Variables: ?
# - Equations: ?
# - Nonzero elements: ?
```

### Risk if Wrong
- License errors may be misclassified as parse/translate errors
- May pollute error statistics with license issues
- Incorrect baseline if license-limited models are included

### Estimated Research Time
1-2 hours (test detection, document thresholds)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings from Catalog Quality Analysis (Task 2):**

1. **License-limited model count:** 10 models (not 11 as originally reported)
   - LP: 6 (airsp, airsp2, andean, emfl, indus89, phosdis)
   - NLP: 3 (jbearing, minsurf, torsion)
   - QCP: 1 (msm)

2. **Detection pattern:** `verification_error: "Model exceeds demo license limits"`
   - This string is consistently used in catalog.json
   - Can be detected programmatically during batch processing

3. **Recommended handling:**
   - Add `license_limited: true` flag in new database schema
   - Skip these 10 models during batch verification
   - Track separately for future verification with full license
   - Do NOT attempt to simplify models (would change problem structure)

4. **nlp2mcp parsing:** License limits are a GAMS execution issue, not a parsing issue
   - nlp2mcp parsing does NOT hit license limits (parsing is independent of GAMS)
   - License limits only affect GAMS solve verification

**Decision:** ✅ Mark as `license_limited` in database, skip during batch verification, track separately for future full-license testing

**Evidence:** See `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md` for full analysis

---

## Unknown 1.4: How should models with missing $include files be handled?

### Priority
**Medium** - Only 2 models truly affected (not 18 as originally reported)

### Assumption
Models with missing $include files should be marked as "dependency_missing" and excluded from pipeline testing, or have their dependencies resolved if feasible.

### Research Questions
1. Which 18 models have missing includes?
2. Are the included files available elsewhere in GAMSLIB?
3. Can we stub out includes with empty files?
4. Should we attempt to resolve dependencies or skip entirely?
5. Are these models otherwise parseable if includes are present?

### How to Verify

**Test Case 1: List models with missing includes**
```bash
# Grep for $include in model files
# Cross-reference with actual file existence
find data/gamslib/raw -name "*.gms" -exec grep -l '\$include' {} \;
```

**Test Case 2: Check if includes exist in GAMSLIB**
```bash
# For each missing include, check GAMSLIB
# gamslib -l | grep "included_file.gms"
```

**Test Case 3: Test with stub includes**
```bash
# Create empty include file
touch data/gamslib/raw/missing_include.gms
# Re-run parse
python3 -m src.cli data/gamslib/raw/affected_model.gms --parse-only
```

### Risk if Wrong
- May waste time on unsolvable models
- May exclude fixable models
- Incomplete corpus coverage

### Estimated Research Time
2 hours (list models, check includes, test stubs)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings from Catalog Quality Analysis (Task 2):**

1. **Corrected count:** Only **2 models** have truly missing includes (not 18)
   - gqapsdp: uses `$include '%instance%'` (parameterized path)
   - kqkpsdp: uses `$include 'kQKP%instance%.gms'` (parameterized path)

2. **Models with $include directives:** 11 total
   - Most include files ARE present in `data/gamslib/raw/`
   - Examples: qpdata.inc, poolmod.inc, t1000d.inc (all exist)

3. **Root cause of "18 models" error:** The original Sprint 13 report conflated:
   - Models with $include that work (9 models)
   - Models with parameterized includes that can't work (2 models)
   - Models with GAMS compilation errors from other causes (19 models total)

4. **Recommended handling:**
   - The 2 parameterized-include models cannot be fixed (require runtime parameters)
   - Mark as `dependency_missing` in database
   - Do NOT stub includes (would produce invalid models)
   - These 2 models are already in the "error" category

**Decision:** ✅ Only 2 models have true missing includes. Mark as `dependency_missing`, no action needed (already classified as errors).

**Evidence:** See `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md` for full analysis

---

## Unknown 1.5: Should batch verification update catalog.json or the new database?

### Priority
**High** - Affects Sprint 14 workflow and data migration

### Assumption
Batch verification should update the new gamslib_status.json database, not the existing catalog.json, to avoid mixing old and new schema formats.

### Research Questions
1. Should we migrate catalog.json data to gamslib_status.json?
2. Can both files coexist during the transition?
3. What fields from catalog.json need to be preserved in the new schema?
4. Should verify_convexity.py output to both formats or just new format?
5. When should catalog.json be deprecated?

### How to Verify

**Test Case 1: Schema comparison**
```python
# Compare catalog.json fields with new schema
# Identify migration mapping
```

**Test Case 2: Migration script prototype**
```python
# Create function to transform catalog entry to new format
def migrate_entry(old_entry) -> new_entry:
    pass
```

**Test Case 3: Dual-write test**
```bash
# Test updating both files to ensure consistency
# during transition period
```

### Risk if Wrong
- Data inconsistency between old and new formats
- Lost data during migration
- Confusion about which file is authoritative

### Estimated Research Time
2 hours (schema mapping, migration design)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings from Catalog Quality Analysis (Task 2):**

1. **Migration approach:** Create new `gamslib_status.json`, migrate data from `catalog.json`
   - catalog.json is high quality (9.75/10 score)
   - All 20 fields use consistent snake_case naming
   - Clean 1:1 field mapping possible

2. **Field preservation:** All catalog.json fields should be preserved
   - Core fields: model_id, sequence_number, model_name, gamslib_type, source_url, etc.
   - Convexity fields: convexity_status, verification_date, solver_status, model_status, etc.
   - New schema adds: nlp2mcp_parse, nlp2mcp_translate, mcp_solve nested objects

3. **Coexistence strategy:**
   - Keep catalog.json as read-only archive (Sprint 13 deliverable)
   - Create gamslib_status.json as new authoritative source
   - Do NOT dual-write (adds complexity, risk of inconsistency)

4. **Migration timing:**
   - Sprint 14 Day 1-2: Create migration script
   - One-time migration when db_manager.py is ready
   - catalog.json remains but is not updated after migration

5. **Schema version bump:** 1.0.0 → 2.0.0
   - Breaking change (new nested structure)
   - Migration script handles transformation

**Decision:** ✅ Create new gamslib_status.json, one-time migration from catalog.json, no dual-write. catalog.json remains as Sprint 13 archive.

**Evidence:** See `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md` for full analysis

---

# Category 2: JSON Database Schema Design

## Unknown 2.1: Should schema use Draft-07 or Draft 2020-12?

### Priority
**High** - Affects validation library compatibility and features

### Assumption
JSON Schema Draft-07 should be used for maximum compatibility with the jsonschema Python library and existing tooling.

### Research Questions
1. What is the current jsonschema library version and which draft does it fully support?
2. What features differ between Draft-07 and Draft 2020-12?
3. Do we need any Draft 2020-12 features (e.g., $dynamicRef, unevaluatedProperties)?
4. What are the compatibility implications for downstream tools?
5. What schema version do similar projects use?

### How to Verify

**Test Case 1: Check library support**
```python
import jsonschema
print(jsonschema.__version__)
# Check which validators are available
from jsonschema import Draft7Validator, Draft202012Validator
```

**Test Case 2: Feature comparison**
```markdown
| Feature | Draft-07 | Draft 2020-12 |
|---------|----------|---------------|
| $ref    | Yes      | Yes           |
| if/then/else | Yes | Yes          |
| ...     | ...      | ...           |
```

**Test Case 3: Test validation with both drafts**
```python
from jsonschema import validate
# Test same schema with Draft7Validator vs Draft202012Validator
```

### Risk if Wrong
- Validation errors if using unsupported features
- Incompatibility with CI/CD tools
- Difficulty migrating to newer draft later

### Estimated Research Time
1-2 hours (library check, feature comparison, decision)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings from JSON Schema Best Practices Research (Task 3):**

1. **Python jsonschema library support:**
   - Current version: 4.25.x
   - Full support for both Draft-07 and Draft 2020-12
   - Both `Draft7Validator` and `Draft202012Validator` classes available

2. **Key differences between drafts:**
   - **Array/Tuple handling:** Draft 2020-12 replaces `items`/`additionalItems` with `prefixItems`/`items` (breaking change)
   - **Dynamic references:** Draft 2020-12 adds `$dynamicRef`/`$dynamicAnchor` (not needed for our use case)
   - **Unevaluated properties:** Draft 2020-12 adds `unevaluatedProperties`/`unevaluatedItems` (adds overhead)

3. **Features needed for nlp2mcp:**
   - Basic type validation ✓ (both drafts)
   - Required/optional fields ✓ (both drafts)
   - Enum values ✓ (both drafts)
   - Nested object validation ✓ (both drafts)
   - $ref for definitions ✓ (both drafts)
   - **No advanced features needed** that require Draft 2020-12

4. **Ecosystem status (2025):**
   - Draft-07 and Draft 2020-12 are both LTS (long-term support)
   - OpenAPI 3.1 uses Draft 2020-12, but OpenAPI 3.0 uses Draft-07
   - Most Python tools default to Draft-07

**Decision:** ✅ Use **Draft-07** for nlp2mcp database schema

**Rationale:**
- Simpler syntax, no breaking changes from tuple handling
- Wider compatibility with existing tools
- Python jsonschema library defaults to Draft-07
- No advanced features (dynamic refs, unevaluated properties) needed
- Lower validation overhead

**Evidence:** See `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` for full analysis

---

## Unknown 2.2: Should convexity data be a nested object or flat fields?

### Priority
**High** - Affects schema design and query patterns

### Assumption
Convexity data should be a nested object (as shown in PROJECT_PLAN.md) for better organization and future extensibility.

### Research Questions
1. Does nesting affect query performance or complexity?
2. How do flat vs nested structures affect db_manager queries?
3. What are the pros/cons for export to CSV (flat) vs JSON (nested)?
4. How does nesting affect jsonschema validation patterns?
5. What do similar database schemas use?

### How to Verify

**Test Case 1: Nested structure**
```json
{
  "model_id": "trnsport",
  "convexity": {
    "status": "verified_convex",
    "solver": "CONOPT",
    "solve_time_sec": 0.12
  }
}
```

**Test Case 2: Flat structure**
```json
{
  "model_id": "trnsport",
  "convexity_status": "verified_convex",
  "convexity_solver": "CONOPT",
  "convexity_solve_time_sec": 0.12
}
```

**Test Case 3: Query comparison**
```python
# Nested: entry["convexity"]["status"]
# Flat: entry["convexity_status"]
# Which is more ergonomic for db_manager queries?
```

### Risk if Wrong
- Awkward query patterns
- Complex CSV export logic
- Schema migration difficulty if we change later

### Estimated Research Time
1-2 hours (prototype both, compare usability)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings from JSON Schema Best Practices Research (Task 3):**

1. **Trade-off analysis:**

   | Aspect | Nested Structure | Flat Structure |
   |--------|-----------------|----------------|
   | Readability | Better grouping | More verbose |
   | Query Access | `entry["convexity"]["status"]` | `entry["convexity_status"]` |
   | CSV Export | Requires flattening | Direct mapping |
   | Extensibility | Easy to add fields to groups | Pollutes namespace |
   | Validation | Can validate sub-objects independently | All at same level |

2. **Best practice guidelines:**
   - Limit nesting to 3-4 levels maximum
   - Group logically related fields together
   - Keep independent data flat
   - Consider access patterns when designing structure

3. **nlp2mcp-specific considerations:**
   - Pipeline has distinct stages (convexity, parse, translate, solve)
   - Each stage has related fields (status, date, version, time, error)
   - Future stages may be added
   - CSV export needed but not primary use case

4. **Existing catalog.json uses flat structure:**
   - All 20 fields at top level with prefixes (`convexity_status`, `verification_date`)
   - Works but clutters namespace as fields grow

**Decision:** ✅ Use **moderate nesting (2 levels)** for pipeline stages

**Recommended structure:**
```json
{
  "model_id": "trnsport",
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP",
  
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2026-01-01T12:00:00Z",
    "solver_status": 1,
    "model_status": 1
  },
  
  "nlp2mcp_parse": {
    "status": "success",
    "parse_date": "2026-01-02T10:00:00Z",
    "nlp2mcp_version": "0.10.0"
  }
}
```

**Rationale:**
- Clear separation between pipeline stages
- Easy to add new fields within each stage
- Query pattern `model["nlp2mcp_parse"]["status"]` is intuitive
- CSV export: flatten with dot notation (`nlp2mcp_parse.status`)
- Validation: can validate each stage object independently

**Evidence:** See `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` for full analysis

---

## Unknown 2.3: What fields should be required vs optional?

### Priority
**Critical** - Affects data integrity and incremental updates

### Assumption
Core identification fields (model_id, model_name, gamslib_type) are required; pipeline stage fields (nlp2mcp_parse, nlp2mcp_translate, mcp_solve) are optional to allow incremental population.

### Research Questions
1. Which fields are known at discovery time (always present)?
2. Which fields are populated during different pipeline stages?
3. How to handle partial entries during incremental updates?
4. Should missing optional fields be null or absent?
5. What validation rules apply to optional nested objects?

### How to Verify

**Test Case 1: Minimal valid entry**
```json
{
  "model_id": "trnsport",
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP"
}
// Should this validate with only required fields?
```

**Test Case 2: Incremental update**
```json
// After parse stage:
{
  "model_id": "trnsport",
  "nlp2mcp_parse": {
    "status": "success",
    "parse_time_sec": 0.05
  }
}
// Should update merge with existing entry
```

**Test Case 3: Null vs absent fields**
```json
{
  "model_id": "trnsport",
  "nlp2mcp_parse": null
}
// vs
{
  "model_id": "trnsport"
}
// Which is preferred?
```

### Risk if Wrong
- Validation failures on partial entries
- Confusing null handling semantics
- Data integrity issues with missing required fields

### Estimated Research Time
2-3 hours (design required/optional, test validation)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: How should pipeline status enums be defined?

### Priority
**High** - Affects consistency and reporting

### Assumption
Each pipeline stage should have a status enum with consistent values across stages (success, failure, not_tested, etc.).

### Research Questions
1. Should status values be identical across all stages?
2. Are there stage-specific statuses (e.g., "partial" for parse)?
3. How to represent "skipped due to prior failure"?
4. Should statuses be strings or numeric codes?
5. How do statuses map to reporting (success rate calculations)?

### How to Verify

**Test Case 1: Define stage-specific statuses**
```python
# Parse: success, failure, partial, not_tested
# Translate: success, failure, not_tested
# Solve: success, failure, mismatch, not_tested
```

**Test Case 2: Cross-stage consistency**
```json
{
  "nlp2mcp_parse": {"status": "success"},
  "nlp2mcp_translate": {"status": "not_tested"},
  "mcp_solve": {"status": "not_tested"}
}
// Is "not_tested" appropriate for stages not yet run?
```

**Test Case 3: Success rate calculation**
```python
# How to calculate parse success rate?
# success / (success + failure) or success / (success + failure + partial)?
```

### Risk if Wrong
- Inconsistent reporting
- Confusion about status meanings
- Incorrect KPI calculations

### Estimated Research Time
1-2 hours (define statuses, document meanings)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: How should error messages be stored (structured vs string)?

### Priority
**Medium** - Affects error analysis and debugging

### Assumption
Error messages should be stored as structured objects with error_type, error_message, and error_line when applicable.

### Research Questions
1. Should we store raw error message strings or structured error objects?
2. What error categories should be standardized?
3. How to handle multiple errors (array of errors)?
4. Should error line numbers be stored separately?
5. How do error structures affect query and filtering?

### How to Verify

**Test Case 1: Structured error**
```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "error": {
      "type": "syntax_error",
      "message": "Unexpected token at line 42",
      "line": 42,
      "column": 15
    }
  }
}
```

**Test Case 2: String error**
```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "error_message": "Unexpected token at line 42"
  }
}
```

**Test Case 3: Multiple errors**
```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "errors": [
      {"type": "syntax_error", "message": "...", "line": 42},
      {"type": "syntax_error", "message": "...", "line": 58}
    ]
  }
}
```

### Risk if Wrong
- Difficult error analysis if unstructured
- Overly complex schema if over-structured
- Query complexity for error filtering

### Estimated Research Time
1-2 hours (design structure, test queries)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.6: Should schema include nlp2mcp version tracking?

### Priority
**Medium** - Affects reproducibility and regression tracking

### Assumption
Each pipeline stage result should record the nlp2mcp version used to enable regression tracking and reproducibility.

### Research Questions
1. How to get nlp2mcp version programmatically?
2. Should version be per-entry or per-stage?
3. How to handle version changes during batch runs?
4. Should we track git commit hash in addition to version?
5. How does version tracking affect historical comparisons?

### How to Verify

**Test Case 1: Get version programmatically**
```python
from src import __version__
print(__version__)  # e.g., "0.10.0"
```

**Test Case 2: Version in schema**
```json
{
  "nlp2mcp_parse": {
    "status": "success",
    "nlp2mcp_version": "0.10.0",
    "tested_date": "2026-01-15"
  }
}
```

**Test Case 3: Git commit tracking**
```python
import subprocess
commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()[:8]
```

### Risk if Wrong
- Cannot reproduce results from specific versions
- Difficulty tracking regressions across versions
- Incomplete audit trail

### Estimated Research Time
1 hour (version access, schema design)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.7: How to handle schema migrations for future changes?

### Priority
**Critical** - Affects long-term maintainability

### Assumption
Schema should include a version field and db_manager should validate/migrate entries when schema version changes.

### Research Questions
1. Where should schema_version be stored (top-level or per-entry)?
2. What migration strategy: in-place update or copy-transform?
3. Should old versions be archived or converted?
4. How to handle partial migrations (some entries updated)?
5. What tooling exists for JSON schema migrations?

### How to Verify

**Test Case 1: Version in database file**
```json
{
  "schema_version": "1.0.0",
  "models": [...]
}
```

**Test Case 2: Migration function**
```python
def migrate_v1_to_v2(entry: dict) -> dict:
    """Migrate entry from schema v1 to v2."""
    # Transform fields as needed
    return new_entry
```

**Test Case 3: Version check on load**
```python
def load_database(path):
    data = json.load(path)
    if data["schema_version"] != CURRENT_VERSION:
        data = migrate(data)
    return data
```

### Risk if Wrong
- Data loss during migrations
- Version incompatibility between tools
- Manual intervention required for schema changes

### Estimated Research Time
2-3 hours (migration strategy, prototype implementation)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings from JSON Schema Best Practices Research (Task 3):**

1. **Versioning strategy options:**

   | Approach | Format | Use Case |
   |----------|--------|----------|
   | Semantic Versioning | MAJOR.MINOR.PATCH | Standard, well-understood |
   | SchemaVer | MODEL-REVISION-ADDITION | Schema-specific, less common |
   | Date-based | YYYY.MM.DD | Simple, chronological |
   | Integer | 1, 2, 3... | Minimal, for simple schemas |

2. **Migration strategy options:**

   | Strategy | Description | Use Case |
   |----------|-------------|----------|
   | Eager Migration | Migrate all entries at schema change | Small databases |
   | Lazy Migration | Migrate entries on read/write | Large databases |
   | Dual-Write | Write to both old and new formats | Zero-downtime |

3. **Best practices for schema evolution:**
   - Never remove required fields without major version bump
   - Add new fields as optional with default values
   - Deprecate before removing
   - Provide migration scripts for major changes
   - Document all changes in CHANGELOG.md

4. **nlp2mcp-specific considerations:**
   - Small database (219 models, <200KB)
   - Schema changes only at sprint boundaries (infrequent)
   - Single-user access (no concurrent migrations needed)
   - Sprint 14 is first major schema change (v1.0.0 → v2.0.0)

**Decision:** ✅ Use **semantic versioning** with **eager migration**

**Implementation approach:**
1. **Version field:** Top-level `schema_version` field (not per-entry)
   ```json
   {
     "schema_version": "2.0.0",
     "models": [...]
   }
   ```

2. **Migration script:** `scripts/gamslib/migrate_schema.py`
   - One function per version transition: `migrate_v1_to_v2()`
   - Migrate entire database at once (eager)
   - Create backup before migration
   - Validate after migration

3. **Version history:**
   - 1.0.0: catalog.json (Sprint 13)
   - 2.0.0: gamslib_status.json with nested pipeline stages (Sprint 14)

4. **Backward compatibility:**
   - Keep catalog.json as read-only archive
   - New gamslib_status.json is authoritative after migration
   - No dual-write needed (clean cutover)

**Rationale:**
- Semantic versioning is industry standard
- Eager migration is appropriate for small, single-user database
- Top-level version simplifies validation (no mixed versions)
- One-time migration aligns with Sprint 14 schedule

**Evidence:** See `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` for full analysis

---

# Category 3: Database Management Scripts

## Unknown 3.1: What subcommands are essential for db_manager.py?

### Priority
**Critical** - Defines Sprint 14 scope

### Assumption
Essential subcommands are: init, add, update, get, query, list, validate, export. Nice-to-have: delete, backup, stats.

### Research Questions
1. Which subcommands are needed for Sprint 14 workflows?
2. What arguments should each subcommand accept?
3. How to design consistent CLI interface across subcommands?
4. Should query support complex filters or simple key-value matching?
5. What export formats are needed (CSV, Markdown, JSON)?

### How to Verify

**Test Case 1: Essential workflow**
```bash
# Initialize database
python db_manager.py init

# Add model
python db_manager.py add trnsport --name "A Transportation Problem" --type LP

# Update after parse
python db_manager.py update trnsport nlp2mcp_parse.status success

# Query by status
python db_manager.py query --parse-status=success

# Export report
python db_manager.py export --format=markdown
```

**Test Case 2: Subcommand help**
```bash
python db_manager.py --help
python db_manager.py query --help
```

**Test Case 3: Complex query**
```bash
# Find all LP models that parse but fail to translate
python db_manager.py query --type=LP --parse-status=success --translate-status=failure
```

### Risk if Wrong
- Missing essential functionality delays sprint
- Over-engineering subcommands wastes time
- Inconsistent CLI confuses users

### Estimated Research Time
2 hours (workflow analysis, CLI design)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: How should concurrent access be handled?

### Priority
**High** - Affects batch operations and CI/CD

### Assumption
File-level locking is sufficient for concurrent access protection since database operations are infrequent.

### Research Questions
1. Can multiple processes (e.g., parallel batch verification) update the database simultaneously?
2. What locking mechanism should be used (fcntl, portalocker, separate lock file)?
3. Should updates be atomic (write to temp, then rename)?
4. How to handle lock timeouts?
5. Is concurrent read access safe without locking?

### How to Verify

**Test Case 1: Atomic write**
```python
import tempfile
import shutil

def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=path.parent) as f:
        json.dump(data, f)
        temp_path = f.name
    shutil.move(temp_path, path)
```

**Test Case 2: File locking**
```python
import fcntl

with open(db_path, 'r+') as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    # Read, modify, write
    fcntl.flock(f, fcntl.LOCK_UN)
```

**Test Case 3: Concurrent stress test**
```bash
# Run 4 parallel processes updating different entries
parallel -j4 "python db_manager.py update model_{} status success" ::: 1 2 3 4
```

### Risk if Wrong
- Data corruption from race conditions
- Deadlocks blocking batch operations
- Lost updates from concurrent writes

### Estimated Research Time
2-3 hours (locking strategy, atomic writes, testing)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: What query interface should db_manager support?

### Priority
**High** - Affects usability and reporting

### Assumption
Simple key-value filtering (--field=value) is sufficient for Sprint 14; complex queries (AND/OR, regex) can be deferred.

### Research Questions
1. What query patterns are needed for Sprint 14 reporting?
2. Should queries support nested field access (--convexity.status=verified)?
3. How to handle list/array fields in queries?
4. Should query output be JSON, table, or both?
5. Is pagination needed for large result sets?

### How to Verify

**Test Case 1: Simple query**
```bash
# All verified_convex models
python db_manager.py query --convexity-status=verified_convex
```

**Test Case 2: Multi-field query**
```bash
# LP models that successfully parsed
python db_manager.py query --type=LP --parse-status=success
```

**Test Case 3: Output formats**
```bash
# JSON output for scripting
python db_manager.py query --parse-status=success --output=json

# Table output for humans
python db_manager.py query --parse-status=success --output=table
```

### Risk if Wrong
- Insufficient query power for reporting needs
- Over-complex query language hard to use
- Poor output formatting

### Estimated Research Time
1-2 hours (query pattern analysis, interface design)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: How should export formats be implemented?

### Priority
**Medium** - Affects reporting and documentation

### Assumption
CSV and Markdown table exports are sufficient for Sprint 14 reporting needs.

### Research Questions
1. Which fields should be included in exports?
2. How to handle nested objects in flat CSV format?
3. Should Markdown export be a simple table or structured document?
4. Should export support field selection (--fields=model_id,status)?
5. How to handle missing/null values in exports?

### How to Verify

**Test Case 1: CSV export**
```bash
python db_manager.py export --format=csv > models.csv
# Check: proper escaping, headers, null handling
```

**Test Case 2: Markdown export**
```bash
python db_manager.py export --format=markdown > REPORT.md
# Check: table formatting, alignment, special characters
```

**Test Case 3: Field selection**
```bash
python db_manager.py export --format=csv --fields=model_id,parse_status,translate_status
```

### Risk if Wrong
- Malformed exports break downstream tools
- Missing fields in reports
- Poor formatting reduces usability

### Estimated Research Time
1-2 hours (export design, test with sample data)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.5: Should db_manager follow existing script patterns?

### Priority
**Medium** - Affects code consistency

### Assumption
db_manager.py should follow the same patterns as existing scripts (discover_models.py, download_models.py, verify_convexity.py) for consistency.

### Research Questions
1. What CLI patterns are used in existing GAMSLIB scripts?
2. What logging conventions are followed?
3. How are errors and exceptions handled?
4. What testing patterns are used (pytest, fixtures)?
5. Should db_manager reuse catalog.py dataclasses?

### How to Verify

**Test Case 1: CLI pattern analysis**
```bash
# Review existing scripts
head -100 scripts/gamslib/download_models.py | grep -A10 "argparse"
```

**Test Case 2: Logging conventions**
```python
# Check: Do existing scripts use logging or print?
# Check: What log levels are used?
```

**Test Case 3: Error handling**
```python
# Check: How do existing scripts handle exceptions?
# Check: What exit codes are used?
```

### Risk if Wrong
- Inconsistent codebase
- Harder to maintain
- Confusion for contributors

### Estimated Research Time
1 hour (review existing scripts, document patterns)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.6: What backup strategy should db_manager use?

### Priority
**Low** - Nice-to-have feature

### Assumption
Automatic backup before destructive operations (init, major updates) is sufficient; manual backup command is nice-to-have.

### Research Questions
1. When should backups be created automatically?
2. What backup naming convention: timestamp, sequence number?
3. Where should backups be stored (archive/ subdirectory)?
4. How many backups to retain before pruning?
5. Should backup be a separate subcommand or automatic?

### How to Verify

**Test Case 1: Automatic backup**
```python
def backup_database(db_path: Path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / "archive" / f"{timestamp}_{db_path.name}"
    shutil.copy(db_path, backup_path)
```

**Test Case 2: Backup retention**
```python
def prune_backups(archive_dir: Path, keep_count: int = 10):
    backups = sorted(archive_dir.glob("*_gamslib_status.json"))
    for old_backup in backups[:-keep_count]:
        old_backup.unlink()
```

### Risk if Wrong
- Data loss on accidental overwrites
- Disk space issues from too many backups
- Low risk overall

### Estimated Research Time
1 hour (backup design, test implementation)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: JSON Database Version Control Strategy

## Unknown 4.1: Should database file be version controlled?

### Priority
**High** - Affects workflow and CI/CD

### Assumption
The database file (gamslib_status.json) should be version controlled in git for traceability and collaboration.

### Research Questions
1. How large will the database file be (JSON overhead for 219 entries)?
2. Will frequent updates create noisy git history?
3. Should database be in .gitignore with separate release snapshots?
4. How do other projects handle version-controlled JSON databases?
5. Should CI/CD auto-commit database updates?

### How to Verify

**Test Case 1: Estimate file size**
```python
# 219 models × ~500 bytes per entry (estimate)
# ~110 KB for full database
# Acceptable for git
```

**Test Case 2: Diff readability**
```bash
# Make two database versions
# Check: git diff gamslib_status.json
# Is the diff readable and meaningful?
```

**Test Case 3: CI/CD workflow**
```yaml
# Should CI commit database changes?
- name: Update database
  run: python db_manager.py update ...
- name: Commit changes
  run: git commit -am "Update database" && git push
```

### Risk if Wrong
- Noisy git history if not managed
- Data loss if not version controlled
- Merge conflicts if multiple PRs update database

### Estimated Research Time
1-2 hours (size analysis, workflow design)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: How to handle database updates in PRs?

### Priority
**Medium** - Affects collaboration workflow

### Assumption
Database updates should be committed alongside code changes in the same PR for atomic updates.

### Research Questions
1. How to resolve merge conflicts in JSON database?
2. Should PRs that only update database be allowed?
3. How to validate database changes in CI?
4. Should database be regenerated rather than merged?
5. What review process for database changes?

### How to Verify

**Test Case 1: Merge conflict resolution**
```bash
# Create conflicting database updates
# Test: git merge resolution
# Is it clear how to resolve?
```

**Test Case 2: CI validation**
```yaml
- name: Validate database
  run: python db_manager.py validate
```

**Test Case 3: Review checklist**
```markdown
## Database PR Checklist
- [ ] Schema version unchanged or migrated
- [ ] New entries have required fields
- [ ] No duplicate model_ids
```

### Risk if Wrong
- Merge conflicts block development
- Invalid database states merged
- Lost updates from poor merge resolution

### Estimated Research Time
1-2 hours (workflow design, CI integration)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Should schema.json be separate from database file?

### Priority
**High** - Affects validation architecture

### Assumption
Schema definition (schema.json) should be a separate file from the database (gamslib_status.json) for cleaner separation of concerns.

### Research Questions
1. Where should schema.json be located?
2. How does db_manager locate and load the schema?
3. Should schema be embedded in db_manager or external?
4. How to ensure schema and database stay in sync?
5. Should schema be versioned separately from database?

### How to Verify

**Test Case 1: Separate files**
```
data/gamslib/
  gamslib_status.json   # Database
  schema.json           # Schema definition
```

**Test Case 2: Schema loading**
```python
SCHEMA_PATH = Path(__file__).parent / "../../data/gamslib/schema.json"

def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)
```

**Test Case 3: Validation with external schema**
```python
from jsonschema import validate
schema = load_schema()
database = load_database()
for entry in database["models"]:
    validate(entry, schema)
```

### Risk if Wrong
- Confusion about which file is which
- Schema/database version mismatch
- Validation failures from wrong schema

### Estimated Research Time
1 hour (file organization, loading design)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: What archive strategy should be used for database snapshots?

### Priority
**Low** - Nice-to-have for history tracking

### Assumption
Timestamped snapshots in an archive/ directory are sufficient for historical tracking.

### Research Questions
1. When should snapshots be created (daily, per-sprint, manually)?
2. What naming convention: YYYYMMDD_gamslib_status.json?
3. Should snapshots be version controlled or .gitignored?
4. How long to retain snapshots?
5. Should snapshots be compressed?

### How to Verify

**Test Case 1: Archive structure**
```
data/gamslib/
  archive/
    20260101_gamslib_status.json
    20260115_gamslib_status.json
```

**Test Case 2: Snapshot creation**
```bash
python db_manager.py snapshot
# Creates: archive/YYYYMMDD_HHMMSS_gamslib_status.json
```

### Risk if Wrong
- Lost historical data
- Disk space issues
- Low risk overall

### Estimated Research Time
30 minutes (design, simple implementation)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: Multi-Solver Validation

## Unknown 5.1: Which secondary solvers are available for validation?

### Priority
**Medium** - Optional Sprint 14 feature

### Assumption
CONOPT and IPOPT are the most likely secondary solvers available; KNITRO requires commercial license.

### Research Questions
1. Which NLP solvers are available in the current GAMS installation?
2. Do secondary solvers have demo license limitations?
3. How does solver availability differ between local dev and CI?
4. Are there open-source alternatives (e.g., IPOPT)?
5. What is the cost/benefit of multi-solver validation?

### How to Verify

**Test Case 1: Check available solvers**
```bash
gams -? | grep -i solver
# Or check gams.gms listing
```

**Test Case 2: Test secondary solver**
```gams
option NLP = IPOPT;
solve model using NLP minimizing obj;
```

**Test Case 3: License check**
```bash
# Run model with each solver
# Check for license limit errors
```

### Risk if Wrong
- Multi-solver validation impossible if no secondary solver available
- Time wasted on unavailable feature
- Medium risk since feature is optional

### Estimated Research Time
1-2 hours (solver inventory, license check)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: What constitutes a solution match between solvers?

### Priority
**Medium** - Affects validation accuracy

### Assumption
Objective value match within relative tolerance (1e-6) and absolute tolerance (1e-8) indicates solution agreement.

### Research Questions
1. What tolerances are appropriate for different model types?
2. Should solution values (x*) be compared in addition to objective?
3. How to handle local optima (different x* with same objective)?
4. How to handle numerical noise near constraint bounds?
5. What if one solver finds infeasible and another finds optimal?

### How to Verify

**Test Case 1: Objective comparison**
```python
def solutions_match(obj1, obj2, rtol=1e-6, atol=1e-8):
    return abs(obj1 - obj2) <= atol + rtol * abs(obj1)
```

**Test Case 2: Different local optima**
```python
# Model with multiple optima
# Solver A: x* = (1, 0), obj = 5
# Solver B: x* = (0, 1), obj = 5
# These should match (same objective)
```

**Test Case 3: Status mismatch**
```python
# Solver A: optimal, obj = 5
# Solver B: infeasible
# This is a mismatch - flag for review
```

### Risk if Wrong
- False positives (declare match when solutions differ)
- False negatives (flag valid matches as mismatches)
- Incorrect convexity conclusions

### Estimated Research Time
1-2 hours (tolerance research, test cases)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Should multi-solver validation be synchronous or parallel?

### Priority
**Low** - Implementation detail

### Assumption
Sequential solver execution is sufficient since multi-solver validation is optional and not time-critical.

### Research Questions
1. Can GAMS run multiple solvers in parallel?
2. Would parallel execution reduce validation time significantly?
3. Are there resource conflicts (license, memory) with parallel solvers?
4. Is the complexity of parallel execution worth the speedup?
5. How does this affect CI/CD run time?

### How to Verify

**Test Case 1: Sequential timing**
```bash
time gams model.gms --solver=CONOPT
time gams model.gms --solver=IPOPT
# Total: sum of individual times
```

**Test Case 2: Parallel execution**
```bash
# Run both solvers in parallel
parallel ::: "gams model.gms --solver=CONOPT" "gams model.gms --solver=IPOPT"
```

### Risk if Wrong
- Slower validation if sequential is too slow
- Complexity for minimal benefit if parallel overkill
- Low risk overall

### Estimated Research Time
1 hour (timing analysis, decision)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.4: How should solver disagreements be recorded and resolved?

### Priority
**Medium** - Affects data quality

### Assumption
Solver disagreements should be flagged in the database with both results recorded for manual review.

### Research Questions
1. What fields needed to record disagreements?
2. Should disagreements block classification or just flag for review?
3. How to prioritize which disagreements to investigate?
4. Should there be an automated re-test on disagreements?
5. What documentation/notes should accompany disagreements?

### How to Verify

**Test Case 1: Disagreement schema**
```json
{
  "multi_solver": {
    "status": "disagreement",
    "solver1": {"name": "CONOPT", "objective": 5.0, "status": "optimal"},
    "solver2": {"name": "IPOPT", "objective": 5.5, "status": "optimal"},
    "notes": "Objective difference exceeds tolerance"
  }
}
```

**Test Case 2: Query disagreements**
```bash
python db_manager.py query --multi-solver-status=disagreement
```

### Risk if Wrong
- Lost data on disagreements
- Incorrect convexity conclusions
- Manual review becomes overwhelming

### Estimated Research Time
1 hour (schema design, workflow)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Template for New Unknowns

```markdown
## Unknown X.Y: [Title]

### Priority
**[Critical/High/Medium/Low]** - [Brief justification]

### Assumption
[State the assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify
[Concrete test cases, experiments, or code snippets]

### Risk if Wrong
[Impact on sprint if assumption is incorrect]

### Estimated Research Time
[X hours]

### Owner
[Team/person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

# Next Steps

1. Review and prioritize Critical and High priority unknowns
2. Schedule research time for prep phase (28-36 hours estimated)
3. Create test cases for verification
4. Update this document with findings before Sprint 14 Day 1
5. Use as living document during sprint - add new unknowns as discovered

## Success Criteria
- All Critical unknowns resolved before Day 1
- All High unknowns resolved before their implementation day
- Medium unknowns resolved during implementation
- Low unknowns can be deferred or resolved opportunistically

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Review Sprint 13 Catalog Quality | 1.3, 1.4, 1.5 | Catalog quality informs migration and error handling |
| Task 3: Survey JSON Schema Best Practices | 2.1, 2.2, 2.7 | Schema research informs design decisions |
| Task 4: Research jsonschema Library Usage | 2.1, 2.3, 2.5 | Library capabilities inform schema validation approach |
| Task 5: Design Database Schema Draft | 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.3 | Core schema design addresses multiple unknowns |
| Task 6: Analyze Parse Rate for Verified Models | 1.1, 1.2, 1.3 | Parse testing establishes baseline metrics |
| Task 7: Review Existing db_manager Patterns | 3.1, 3.5, 3.6 | Existing patterns inform db_manager design |
| Task 8: Establish Performance Baselines | 1.1, 5.3 | Timing data informs batch and solver strategy |
| Task 9: Review Sprint 13 Retrospective Items | 1.3, 1.4, 1.5 | Lessons learned inform error handling |
| Task 10: Plan Sprint 14 Detailed Schedule | All | Integrates all verified unknowns into plan |

### Coverage Summary

| Category | Unknowns | Verified By Tasks |
|----------|----------|-------------------|
| 1. Convexity Verification | 5 | Tasks 2, 6, 8, 9 |
| 2. Database Schema Design | 7 | Tasks 3, 4, 5 |
| 3. Database Management Scripts | 6 | Tasks 5, 7 |
| 4. Version Control Strategy | 4 | Tasks 5, 7 |
| 5. Multi-Solver Validation | 4 | Task 8 |

---

## Document History

- January 1, 2026: Initial creation (pre-Sprint 14)
