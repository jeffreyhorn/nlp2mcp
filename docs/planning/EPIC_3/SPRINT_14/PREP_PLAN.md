# Sprint 14 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 14 begins  
**Timeline:** Complete before Sprint 14 Day 1  
**Goal:** Prepare for Complete Convexity Verification & JSON Database Infrastructure

**Key Insight from Sprint 13:** GAMSLIB corpus infrastructure is complete with 219 models cataloged, 160 verified as convex/likely convex. Sprint 14 builds on this foundation to design the JSON database schema and run batch verification through the nlp2mcp pipeline.

---

## Executive Summary

Sprint 14 focuses on three major areas per `docs/planning/EPIC_3/PROJECT_PLAN.md`:

1. **Complete Convexity Verification (~10-12h)**
   - Batch verification on all candidate models
   - Multi-solver validation (optional)
   - Results integration into catalog

2. **JSON Database Schema Design (~6-8h)**
   - Comprehensive schema for tracking model status through pipeline
   - Schema validation with jsonschema library
   - Extensible design for parse/translate/solve stages

3. **Database Management Scripts (~8-10h)**
   - `db_manager.py` with CRUD operations and queries
   - Version control strategy for database file
   - Export to CSV/Markdown for reporting

This prep plan identifies unknowns, validates the existing catalog, designs the schema, and establishes baselines before Sprint 14 implementation.

**Sprint 13 Handoff:**
- 219 models in `data/gamslib/catalog.json`
- 57 verified_convex, 103 likely_convex, 48 errors, 4 excluded, 7 unknown
- Scripts: `discover_models.py`, `download_models.py`, `verify_convexity.py`
- 54 unit tests for catalog and verification

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Unknowns Verified | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|-------------------|----------------------|
| 1 | Create Sprint 14 Known Unknowns List | Critical | 2-3h | None | N/A | Risk identification |
| 2 | Review Sprint 13 Catalog Quality | High | 2h | None | 1.3, 1.4, 1.5 | Verification foundation |
| 3 | Survey JSON Schema Best Practices | High | 2-3h | Task 1 | 2.1, 2.2, 2.7 | Database schema design |
| 4 | Research jsonschema Library Usage | High | 2h | Task 3 | 2.1, 2.3, 2.5 | Schema validation |
| 5 | Design Database Schema Draft | Critical | 3-4h | Tasks 3, 4 | 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.3 | Database schema design |
| 6 | Analyze Parse Rate for Verified Models | High | 2-3h | Task 2 | 1.1, 1.2, 1.3 | Pipeline testing readiness |
| 7 | Review Existing db_manager Patterns | Medium | 1-2h | None | 3.1, 3.5, 3.6 | Database management scripts |
| 8 | Establish Performance Baselines | Medium | 2h | Task 6 | 1.1, 5.3 | Batch verification |
| 9 | Review Sprint 13 Retrospective Items | High | 1h | None | 1.3, 1.4, 1.5 | Process improvement |
| 10 | Plan Sprint 14 Detailed Schedule | Critical | 3-4h | All tasks | All | Sprint 14 planning |

**Total Estimated Time:** 22-28 hours (~3-4 working days)

**Critical Path:** Tasks 1 → 3 → 4 → 5 → 10 (schema design path)
**Parallel Path:** Tasks 2 → 6 → 8 (verification quality path)

---

## Task 1: Create Sprint 14 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Sprint planning  
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 14 to prevent late discoveries during implementation.

### Why This Matters

Sprint 13's prep work (26 unknowns verified) enabled smooth execution with zero late surprises. Continue this proven methodology for Sprint 14.

### Background

Sprint 14 covers three major areas from `docs/planning/EPIC_3/PROJECT_PLAN.md`:
1. Complete convexity verification for all models
2. JSON database schema design and validation
3. Database management scripts (db_manager.py)

### What Needs to Be Done

1. **Review Sprint 14 scope** from PROJECT_PLAN.md (lines 92-223)
2. **Identify unknowns** for each component:

   **Category 1: Batch Verification**
   - How long will batch verification of 160+ models take?
   - What percentage of models will hit license limits?
   - How to handle models with external dependencies ($include)?
   - Should multi-solver validation be included or deferred?

   **Category 2: JSON Schema Design**
   - What fields are required vs optional?
   - How to handle schema versioning for migrations?
   - Should convexity data be nested object or flat fields?
   - How to represent pipeline stage status consistently?

   **Category 3: Schema Validation**
   - Which jsonschema library version to use?
   - How strict should validation be?
   - How to handle partial entries during incremental updates?

   **Category 4: Database Manager**
   - What subcommands are essential vs nice-to-have?
   - How to handle concurrent access (multiple processes)?
   - What export formats are needed?
   - How to implement atomic updates safely?

   **Category 5: Integration with Existing Code**
   - How does new schema relate to existing catalog.json?
   - Should we migrate catalog.json to new schema or create new file?
   - How to integrate with verify_convexity.py output?

3. **Prioritize by risk** (Critical, High, Medium, Low)
4. **Define verification method** for each unknown
5. **Create document** with all categories and verification plan

### Changes

Created `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with:
- 26 unknowns across 5 categories
- Priority distribution: 6 Critical, 11 High, 6 Medium, 3 Low
- Estimated research time: 28-36 hours
- Task-to-Unknown mapping table

### Result

Document created with comprehensive coverage:
- Category 1: Complete Convexity Verification (5 unknowns)
- Category 2: JSON Database Schema Design (7 unknowns)
- Category 3: Database Management Scripts (6 unknowns)
- Category 4: JSON Database Version Control Strategy (4 unknowns)
- Category 5: Multi-Solver Validation (4 unknowns)

### Verification

```bash
# Verify document exists
cat docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md | head -50

# Count unknowns
grep -c "Unknown [0-9]" docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md
# Result: 26 unknowns
```

### Deliverables

- [x] `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with 26 unknowns
- [x] Unknowns categorized by component (5 categories)
- [x] Verification plan for Critical/High priority items
- [x] Estimated research time for each category
- [x] Task-to-Unknown mapping table

### Acceptance Criteria

- [x] Document created with 15+ unknowns across 5 categories (26 created)
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical/High unknowns have verification plan
- [x] Unknowns cover all Sprint 14 components
- [x] Research time estimated per category

---

## Task 2: Review Sprint 13 Catalog Quality

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 1.3, 1.4, 1.5

### Objective

Validate the quality and completeness of Sprint 13's catalog.json to ensure it's ready for Sprint 14 database integration.

### Why This Matters

Sprint 14 will build the new database schema on top of Sprint 13 data. Any quality issues in the catalog will propagate to the new database.

### Background

Sprint 13 delivered `data/gamslib/catalog.json` with:
- 219 models (86 LP, 120 NLP, 13 QCP)
- All models downloaded (100%)
- 160 verified as convex/likely_convex
- 48 with errors, 4 excluded, 7 unknown

### What Needs to Be Done

1. **Validate catalog completeness**
   - All 219 models have required fields
   - No null/missing values for required fields
   - All dates in ISO 8601 format

2. **Analyze verification results**
   - Breakdown of error categories
   - Identify models that could be re-verified
   - Document any data quality issues

3. **Check field consistency**
   - Consistent naming conventions
   - Consistent value formats
   - No duplicate entries

4. **Create quality report**
   - Summary statistics
   - Issues found (if any)
   - Recommendations for Sprint 14

### Changes

- Created `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md`
- Updated `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 1.4, 1.5

### Result

**Catalog Quality Score: 9.75/10 (Excellent)**

Key findings:
- All 219 models have complete required fields
- No null values in required fields
- No duplicate model_ids or sequence_numbers
- All dates in valid ISO 8601 format
- All 20 fields use consistent snake_case naming

Error categories analyzed:
- GAMS compilation error: 19 models
- No solve summary found: 15 models
- License limits exceeded: 10 models (corrected from 11)
- Solver errors: 4 models

Corrected assumptions:
- License-limited models: 10 (not 11)
- Missing $include files: Only 2 models (not 18) - gqapsdp, kqkpsdp use parameterized paths
- 7 "unknown" status models could be reclassified (4 LP models with status=2)

### Verification

```bash
# Validate catalog structure
python3 -c "
import json
with open('data/gamslib/catalog.json') as f:
    cat = json.load(f)
print(f'Total models: {len(cat[\"models\"])}')
print(f'Schema version: {cat.get(\"schema_version\")}')
"

# Check for missing convexity status
python3 -c "
import json
with open('data/gamslib/catalog.json') as f:
    cat = json.load(f)
missing = [m['model_id'] for m in cat['models'] if not m.get('convexity_status')]
print(f'Missing convexity_status: {len(missing)}')
"
```

### Deliverables

- [x] `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md`
- [x] List of any data quality issues (none blocking)
- [x] Recommendations for Sprint 14 schema design
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 1.4, 1.5

### Acceptance Criteria

- [x] All 219 models validated
- [x] No missing required fields identified
- [x] Error categories documented
- [x] Quality report created
- [x] Recommendations for new schema documented
- [x] Unknowns 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Survey JSON Schema Best Practices

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 2.1, 2.2, 2.7

### Objective

Research JSON Schema best practices to inform the database schema design for Sprint 14.

### Why This Matters

Sprint 14 deliverable includes `data/gamslib/schema.json` for validation. Understanding best practices ensures a well-designed, extensible schema.

### Background

PROJECT_PLAN.md specifies a comprehensive schema with nested objects for:
- Convexity verification results
- nlp2mcp parse status
- nlp2mcp translate status
- MCP solve status

### What Needs to Be Done

1. **Review JSON Schema specification**
   - Draft-07 vs Draft 2020-12 differences
   - Required vs optional fields
   - Nested object patterns
   - Enum definitions for status values

2. **Research versioning strategies**
   - Schema version field placement
   - Migration patterns for schema changes
   - Backward compatibility approaches

3. **Study existing database schemas**
   - Review similar project structures
   - Identify common patterns
   - Note anti-patterns to avoid

4. **Document recommendations**
   - Recommended schema draft version
   - Field naming conventions
   - Nested vs flat structure trade-offs
   - Validation strictness levels

### Changes

- Created `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` with comprehensive research
- Updated `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.2, 2.7

### Result

**Key Recommendations for Sprint 14:**

1. **Schema Draft Version:** Use **Draft-07**
   - Full support in Python jsonschema library (v4.25+)
   - Simpler syntax, no advanced features needed
   - Wider compatibility with existing tools

2. **Naming Convention:** Use **snake_case**
   - Consistency with existing catalog.json (20 fields)
   - Alignment with Python PEP 8 conventions

3. **Structure:** Use **moderate nesting (2 levels)**
   - Nested objects for pipeline stages: `convexity`, `nlp2mcp_parse`, `nlp2mcp_translate`, `mcp_solve`
   - Core identification fields at top level
   - Easy to extend within each stage

4. **Versioning:** Use **semantic versioning** (MAJOR.MINOR.PATCH)
   - Top-level `schema_version` field
   - Migration from 1.0.0 (catalog.json) to 2.0.0 (gamslib_status.json)

5. **Migration Strategy:** Use **eager migration**
   - One-time migration from catalog.json to gamslib_status.json
   - Keep catalog.json as read-only archive

6. **Validation:** Use **strict validation** with `additionalProperties: false`
   - Prevents schema drift
   - Catches typos in field names

### Verification

```bash
# Verify research document exists
cat docs/research/JSON_SCHEMA_BEST_PRACTICES.md | head -30
```

### Deliverables

- [x] `docs/research/JSON_SCHEMA_BEST_PRACTICES.md`
- [x] Recommended schema draft version (Draft-07)
- [x] Field naming convention guide (snake_case)
- [x] Nested vs flat structure recommendation (moderate nesting)
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.7

### Acceptance Criteria

- [x] JSON Schema specification reviewed
- [x] Versioning strategy documented
- [x] Best practices documented
- [x] Recommendations for Sprint 14 schema provided
- [x] Unknowns 2.1, 2.2, 2.7 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Research jsonschema Library Usage

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** Task 3 (JSON Schema Best Practices)  
**Unknowns Verified:** 2.1, 2.3, 2.5

### Objective

Research the Python jsonschema library to understand validation capabilities and integration patterns.

### Why This Matters

Sprint 14 requires schema validation integrated into db_manager.py. Understanding the library ensures correct implementation.

### Background

From PROJECT_PLAN.md: "Implement JSON schema validation (jsonschema library)"

### What Needs to Be Done

1. **Review jsonschema library**
   - Current version and compatibility
   - Validation API usage
   - Error message customization
   - Performance considerations

2. **Test validation patterns**
   - Validate complete objects
   - Validate partial updates
   - Handle optional fields
   - Custom error messages

3. **Document integration approach**
   - Where to call validation
   - How to report errors
   - Performance impact

4. **Create example code**
   - Schema definition
   - Validation wrapper function
   - Error handling pattern

### Changes

- Created `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md` with comprehensive usage guide
- Updated `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.3, 2.5

### Result

**Key Findings:**

1. **Library Version:** jsonschema 4.25.1 with full Draft-07 and Draft 2020-12 support
   - Use `Draft7Validator` (consistent with Task 3 decision)
   - Both validators fully functional

2. **Performance:** ~10,000 validations/second
   - 219 models batch validation: ~22 ms
   - Negligible overhead - always validate

3. **Required vs Optional Fields:**
   - Fields in `required` array must be present
   - Optional fields can be absent without error
   - Use separate CREATE/UPDATE schemas for partial updates

4. **Error Handling:**
   - Rich error objects with path, message, validator details
   - Use `iter_errors()` to collect all errors
   - Structured format recommended for storage

5. **Strict Validation:**
   - Use `additionalProperties: false` to reject unknown fields
   - Prevents typos and schema drift

6. **Format Validation:**
   - `date-time` format not strictly validated by default
   - Use regex patterns or application code for date validation

**Integration Pattern for db_manager.py:**
- Create validators once at module level (singleton)
- Use `iter_errors()` for full error collection
- Store structured errors with field, message, validator
- Separate schemas for create vs update operations

### Verification

```bash
# Check jsonschema is available
python3 -c "import jsonschema; print(jsonschema.__version__)"

# Test basic validation
python3 -c "
from jsonschema import validate, ValidationError
schema = {'type': 'object', 'properties': {'name': {'type': 'string'}}}
validate({'name': 'test'}, schema)
print('Validation works')
"
```

### Deliverables

- [x] `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md`
- [x] Example validation code snippets
- [x] Error handling recommendations
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.3, 2.5

### Acceptance Criteria

- [x] jsonschema library version confirmed (4.25.1)
- [x] Validation patterns documented
- [x] Example code created
- [x] Integration approach defined
- [x] Unknowns 2.1, 2.3, 2.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Design Database Schema Draft

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** Tasks 3, 4 (Schema research)  
**Unknowns Verified:** 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.3

### Objective

Create draft database schema based on PROJECT_PLAN.md specification and research findings.

### Why This Matters

The database schema is a central Sprint 14 deliverable. Having a validated draft before Day 1 prevents design iteration during the sprint.

### Background

PROJECT_PLAN.md (lines 130-175) provides a detailed schema template with:
- Model identification fields
- Convexity verification nested object
- nlp2mcp_parse nested object
- nlp2mcp_translate nested object
- mcp_solve nested object

### What Needs to Be Done

1. **Review PROJECT_PLAN.md schema template**
   - Understand all required fields
   - Identify optional vs required
   - Note nested object structures

2. **Adapt template based on research**
   - Apply best practices from Task 3
   - Ensure jsonschema compatibility from Task 4
   - Add schema_version field

3. **Create draft schema**
   - JSON Schema definition file
   - Field descriptions
   - Valid value enums
   - Required field list

4. **Validate against existing data**
   - Test with catalog.json entries
   - Identify migration needs
   - Document gaps

5. **Create documentation**
   - Schema specification document
   - Field-by-field descriptions
   - Example valid/invalid entries

### Changes

- Created `docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json` with comprehensive JSON Schema (Draft-07)
- Created `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md` with design rationale
- Updated `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.4, 2.6, 4.3

### Result

**Schema Structure:**
- Top-level: 6 properties (schema_version, created_date, updated_date, gams_version, total_models, models)
- model_entry: 17 fields (3 required: model_id, model_name, gamslib_type)
- 5 definitions: model_entry, convexity_result, parse_result, translate_result, solve_result, error_detail

**Key Design Decisions:**
1. **Draft-07** - Maximum compatibility with Python jsonschema
2. **Moderate nesting** - 2 levels for pipeline stages
3. **snake_case** - Consistent with catalog.json and Python
4. **Strict validation** - `additionalProperties: false` everywhere
5. **Stage-specific enums** - Different status values per pipeline stage
6. **Structured errors** - Category, message, optional line/column

**Validation Testing:**
- Schema validated with `Draft7Validator.check_schema()`
- Tested with 6 scenarios: minimal entry, full entry, error entry, unknown field (rejected), wrong enum (rejected), missing nested required (rejected)
- All tests passed

**Field Counts:**
- convexity_result: 8 fields
- parse_result: 7 fields
- translate_result: 8 fields
- solve_result: 10 fields
- error_detail: 5 fields

### Verification

```bash
# Validate draft schema is valid JSON Schema
python3.12 -c "
import json
from jsonschema import Draft7Validator
with open('docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json') as f:
    schema = json.load(f)
Draft7Validator.check_schema(schema)
print('Schema is valid JSON Schema')
"
# Result: Schema is valid JSON Schema
```

### Deliverables

- [x] `docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json`
- [x] `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md`
- [x] Field descriptions and valid values
- [x] Migration notes from current catalog
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.4, 2.6, 4.3

### Acceptance Criteria

- [x] Draft schema created following PROJECT_PLAN.md template
- [x] Schema is valid JSON Schema (Draft-07)
- [x] All fields documented
- [x] Tested against sample catalog entries
- [x] Migration approach documented
- [x] Unknowns 2.4, 2.6, 4.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Analyze Parse Rate for Verified Models

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Catalog Quality Review)  
**Unknowns Verified:** 1.1, 1.2, 1.3

### Objective

Determine the current nlp2mcp parse success rate for the 160 verified convex models to establish a baseline for Sprint 14.

### Why This Matters

Sprint 14 will track parse/translate/solve status for all models. Understanding current parse rate helps set realistic targets and identify blockers.

### Background

From Sprint 13:
- 57 verified_convex models (LP)
- 103 likely_convex models (NLP/QCP)
- Total: 160 models ready for pipeline testing

From prior work (docs/research/gamslib_parse_errors.md):
- Known parse blockers exist (unsupported syntax)
- Tier 1 models have 100% parse rate
- Tier 2 models have partial parse rate

### What Needs to Be Done

1. **Select test subset**
   - Sample 20-30 models from verified set
   - Include mix of LP, NLP, QCP
   - Include varying file sizes

2. **Run nlp2mcp parse**
   - Execute on each model
   - Capture success/failure
   - Record error messages for failures

3. **Analyze results**
   - Calculate parse success rate
   - Categorize failure reasons
   - Identify common blockers

4. **Document findings**
   - Parse rate baseline
   - Top failure categories
   - Recommendations for Sprint 14

### Changes

- Created `docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md` with comprehensive analysis
- Updated `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 1.3

### Result

**Parse Rate Baseline:**
- **Sample size:** 30 models (15 LP, 12 NLP, 3 QCP)
- **Success rate:** 13.3% (4/30 models)
- **Projected for 160 models:** ~14% (~23 models)

**Parse Rate by Type:**
- LP: 6.7% (1/15)
- NLP: 16.7% (2/12)
- QCP: 33.3% (1/3)

**Performance Metrics:**
- Average parse time: 0.97 seconds
- Projected batch time: ~3 minutes for 160 models

**Failure Categories:**
| Category | Count | Percentage |
|----------|-------|------------|
| syntax_error | 20 | 77% |
| no_objective | 2 | 8% |
| unsupported_function | 2 | 8% |
| domain_error | 1 | 4% |
| undefined_variable | 1 | 4% |

**Successful Models:** prodmix, rbrock, hs62, himmel11

**Key Finding:** Assumption of 30% parse rate was wrong - actual rate is ~13%. Sprint 14 KPIs should expect 15-25 models parsing successfully.

### Verification

```bash
# Run parse test in virtual environment
source .venv/bin/activate
python -m src.cli data/gamslib/raw/prodmix.gms -o /tmp/test.gms
# Result: success (0.93s)

# Run batch test on 30 models
# See PARSE_RATE_BASELINE.md for full results
```

### Deliverables

- [x] `docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md`
- [x] Sample of 30 models tested
- [x] Parse success rate: 13.3%
- [x] Top failure categories documented
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3

### Acceptance Criteria

- [x] 20+ models tested with nlp2mcp parser (30 tested)
- [x] Parse success rate calculated (13.3%)
- [x] Failure reasons categorized (5 categories)
- [x] Baseline documented for Sprint 14
- [x] Unknowns 1.1, 1.2, 1.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Review Existing db_manager Patterns

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 3.1, 3.5, 3.6

### Objective

Review existing script patterns in the codebase to inform db_manager.py design.

### Why This Matters

Consistent patterns improve maintainability. Understanding existing conventions ensures db_manager.py follows project standards.

### Background

Sprint 13 created several GAMSLIB scripts:
- `scripts/gamslib/discover_models.py`
- `scripts/gamslib/download_models.py`
- `scripts/gamslib/verify_convexity.py`
- `scripts/gamslib/catalog.py` (dataclasses)

### What Needs to Be Done

1. **Review existing scripts**
   - CLI argument patterns (argparse)
   - Logging conventions
   - Error handling patterns
   - File I/O patterns

2. **Identify reusable patterns**
   - Catalog load/save functions
   - Progress logging
   - JSON formatting

3. **Document conventions**
   - CLI structure for subcommands
   - Standard argument names
   - Output formatting

4. **Design db_manager interface**
   - Subcommand structure
   - Common arguments
   - Output formats

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Review existing CLI patterns
head -100 scripts/gamslib/download_models.py | grep -A5 "argparse"
head -100 scripts/gamslib/verify_convexity.py | grep -A5 "argparse"
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md`
- CLI subcommand specification
- Reusable pattern notes
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.5, 3.6

### Acceptance Criteria

- [ ] Existing scripts reviewed
- [ ] CLI patterns documented
- [ ] db_manager interface designed
- [ ] Subcommand list finalized
- [ ] Unknowns 3.1, 3.5, 3.6 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Establish Performance Baselines

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Development team  
**Dependencies:** Task 6 (Parse Rate Analysis)  
**Unknowns Verified:** 1.1, 5.3

### Objective

Establish performance baselines for batch operations to inform Sprint 14 timeout and resource settings.

### Why This Matters

Sprint 14 involves batch verification of 160+ models. Understanding performance characteristics prevents timeout issues and enables progress estimation.

### Background

From Sprint 13 verification:
- Individual model verification: ~1-60 seconds
- Batch of 219 models: ~30 minutes total
- Timeouts configured at 60 seconds

### What Needs to Be Done

1. **Measure current performance**
   - Time to load/save catalog.json
   - Time to verify single model
   - Memory usage for batch operations

2. **Project batch performance**
   - Estimated time for 160 model batch
   - Identify potential bottlenecks
   - Recommend batch size for progress reporting

3. **Document baselines**
   - Current metrics
   - Projections for Sprint 14
   - Recommended configurations

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Measure catalog load time
time python3 -c "
import json
with open('data/gamslib/catalog.json') as f:
    cat = json.load(f)
print(f'Loaded {len(cat[\"models\"])} models')
"
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_14/PERFORMANCE_BASELINES.md`
- Catalog I/O performance metrics
- Batch operation projections
- Recommended configurations
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 5.3

### Acceptance Criteria

- [ ] Catalog load/save times measured
- [ ] Single model verification time measured
- [ ] Batch performance projected
- [ ] Recommendations documented
- [ ] Unknowns 1.1, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Review Sprint 13 Retrospective Items

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 1 hour  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Sprint planning  
**Dependencies:** None  
**Unknowns Verified:** 1.3, 1.4, 1.5

### Objective

Review Sprint 13 retrospective and ensure all follow-up items are captured for Sprint 14.

### Why This Matters

Sprint 13 identified lessons learned and recommendations. Ensuring these are incorporated prevents repeating issues.

### Background

From `docs/planning/EPIC_3/SPRINT_13/SPRINT_SUMMARY.md`:

**What Went Well:**
- Prep work (26 unknowns verified) enabled smooth execution
- gamslib command provided simple, reliable extraction
- Day-by-day progress with clear checkpoints
- Error handling improved iteratively

**What Could Be Improved:**
- Could filter license-limited models earlier
- Missing $include files affect 18 models
- Initial error detection had false positives

**Recommendations for Sprint 14:**
1. Run batch MCP conversion on verified_convex + likely_convex
2. Add convert_status to catalog schema
3. Consider adding solver_type to ModelIR
4. Skip or document the 48 error models

### What Needs to Be Done

1. **Review SPRINT_SUMMARY.md**
   - Extract all action items
   - Categorize by priority

2. **Map to Sprint 14 tasks**
   - Which items apply to Sprint 14?
   - Which should be deferred?

3. **Update Sprint 14 planning**
   - Add relevant items to Known Unknowns
   - Include in detailed schedule

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Review Sprint 13 recommendations
grep -A10 "Recommendations for Sprint 14" docs/planning/EPIC_3/SPRINT_13/SPRINT_SUMMARY.md
```

### Deliverables

- Checklist of Sprint 13 follow-up items
- Mapping to Sprint 14 tasks
- Items to defer documented
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 1.4, 1.5

### Acceptance Criteria

- [ ] SPRINT_SUMMARY.md reviewed
- [ ] All recommendations captured
- [ ] Items mapped to Sprint 14 or deferred
- [ ] No items lost between sprints
- [ ] Unknowns 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 14 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 14 Day 1  
**Owner:** Sprint planning  
**Dependencies:** All previous tasks  
**Unknowns Verified:** All (integrates findings from all unknowns)

### Objective

Create detailed day-by-day Sprint 14 plan incorporating all prep task findings.

### Why This Matters

A detailed schedule ensures all deliverables are completed on time and dependencies are respected.

### Background

From PROJECT_PLAN.md, Sprint 14 has three major components:
1. Complete Convexity Verification (~10-12h)
2. JSON Database Schema Design (~6-8h)
3. Database Management Scripts (~8-10h)

Total estimated effort: 24-30 hours (~10 working days)

### What Needs to Be Done

1. **Synthesize prep task findings**
   - Known unknowns to verify
   - Schema design decisions
   - Performance baselines
   - Parse rate expectations

2. **Create day-by-day schedule**
   - Days 1-2: Schema design and validation
   - Days 3-5: db_manager.py implementation
   - Days 6-7: Batch verification execution
   - Days 8-9: Integration and testing
   - Day 10: Documentation and review

3. **Define checkpoints**
   - Day 3: Schema complete and validated
   - Day 5: db_manager core functions working
   - Day 7: Verification batch complete
   - Day 10: All deliverables ready

4. **Identify risks and mitigations**
   - Schema design delays
   - Parse failures blocking verification
   - jsonschema integration issues

5. **Create PLAN.md**
   - Full task breakdown
   - Dependencies
   - Acceptance criteria
   - Success metrics

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify PLAN.md exists
cat docs/planning/EPIC_3/SPRINT_14/PLAN.md | head -50

# Check day-by-day structure
grep -c "Day [0-9]" docs/planning/EPIC_3/SPRINT_14/PLAN.md
# Expected: 10 days
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- Day-by-day schedule with tasks
- Checkpoints with success criteria
- Risk mitigation strategies
- Updated KNOWN_UNKNOWNS.md with all verification results integrated

### Acceptance Criteria

- [ ] All prep task findings incorporated
- [ ] 10-day schedule created
- [ ] Checkpoints defined (Days 3, 5, 7, 10)
- [ ] Acceptance criteria for each deliverable
- [ ] Risks identified with mitigations
- [ ] PLAN.md reviewed and approved
- [ ] All unknowns verified and updated in KNOWN_UNKNOWNS.md

---

## Summary

### Success Criteria

All prep tasks complete when:
- [x] Known Unknowns document created with 15+ unknowns (26 created)
- [x] Catalog quality validated, no blocking issues
- [x] JSON Schema best practices researched
- [x] jsonschema library validated
- [x] Draft database schema created
- [x] Parse rate baseline established
- [ ] db_manager design documented
- [ ] Performance baselines established
- [ ] Sprint 13 retrospective items captured
- [ ] Sprint 14 detailed schedule created

### Critical Path

```
Task 1 (Known Unknowns) ✅
    ↓
Task 3 (JSON Schema Best Practices)
    ↓
Task 4 (jsonschema Library)
    ↓
Task 5 (Draft Schema) ──────────────┐
                                    ↓
Task 2 (Catalog Quality) ✅         │
    ↓                               │
Task 6 (Parse Rate)                 │
    ↓                               │
Task 8 (Performance)                │
                                    │
Task 7 (db_manager Patterns)        │
                                    │
Task 9 (Retrospective)              │
                                    ↓
                         Task 10 (Detailed Schedule)
```

### Estimated Total Time

| Category | Tasks | Time |
|----------|-------|------|
| Research | 1, 3, 4, 7 | 7-10h |
| Analysis | 2, 6, 8, 9 | 7-9h |
| Design | 5, 10 | 6-8h |
| **Total** | 10 tasks | **22-28h** |

---

## Appendix A: Document Cross-References

### Sprint 14 Goals
- `docs/planning/EPIC_3/PROJECT_PLAN.md` (lines 92-223)

### Sprint 13 Deliverables
- `docs/planning/EPIC_3/SPRINT_13/SPRINT_SUMMARY.md`
- `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`
- `data/gamslib/catalog.json`

### Related Research Documents
- `docs/research/GAMSLIB_MODEL_TYPES.md`
- `docs/research/gamslib_parse_errors.md`
- `docs/research/gamslib_kpi_definitions.md`

### Epic Goals
- `docs/planning/EPIC_3/GOALS.md`

### Existing Infrastructure
- `scripts/gamslib/catalog.py` - Catalog dataclasses
- `scripts/gamslib/verify_convexity.py` - Verification script
- `tests/test_gamslib_catalog.py` - Catalog tests
- `tests/gamslib/test_verify_convexity.py` - Verification tests

---

## Appendix B: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns from KNOWN_UNKNOWNS.md:

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
