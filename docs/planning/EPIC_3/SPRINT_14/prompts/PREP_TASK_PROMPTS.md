# Sprint 14 Prep Task Prompts

This document contains prompts for executing each preparation task for Sprint 14. Each prompt includes full task objectives, deliverables, and instructions for completing the task.

---

## Table of Contents

- [Task 2: Review Sprint 13 Catalog Quality](#task-2-review-sprint-13-catalog-quality)
- [Task 3: Survey JSON Schema Best Practices](#task-3-survey-json-schema-best-practices)
- [Task 4: Research jsonschema Library Usage](#task-4-research-jsonschema-library-usage)
- [Task 5: Design Database Schema Draft](#task-5-design-database-schema-draft)
- [Task 6: Analyze Parse Rate for Verified Models](#task-6-analyze-parse-rate-for-verified-models)
- [Task 7: Review Existing db_manager Patterns](#task-7-review-existing-db_manager-patterns)
- [Task 8: Establish Performance Baselines](#task-8-establish-performance-baselines)
- [Task 9: Review Sprint 13 Retrospective Items](#task-9-review-sprint-13-retrospective-items)
- [Task 10: Plan Sprint 14 Detailed Schedule](#task-10-plan-sprint-14-detailed-schedule)

---

## Task 2: Review Sprint 13 Catalog Quality

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 2: Review Sprint 13 Catalog Quality.

## Task Overview

**Priority:** High  
**Estimated Time:** 2 hours  
**Dependencies:** None  
**Unknowns to Verify:** 1.3, 1.4, 1.5

## Objective

Validate the quality and completeness of Sprint 13's catalog.json to ensure it's ready for Sprint 14 database integration.

## Why This Matters

Sprint 14 will build the new database schema on top of Sprint 13 data. Any quality issues in the catalog will propagate to the new database.

## Background

Sprint 13 delivered `data/gamslib/catalog.json` with:
- 219 models (86 LP, 120 NLP, 13 QCP)
- All models downloaded (100%)
- 160 verified as convex/likely_convex
- 48 with errors, 4 excluded, 7 unknown

## What Needs to Be Done

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

## Deliverables

- `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md`
- List of any data quality issues
- Recommendations for Sprint 14 schema design

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 1.3: How should models with license limit errors be handled?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add findings about license error detection patterns
- Document license limit thresholds if discoverable
- Add evidence and decision

### Unknown 1.4: How should models with missing $include files be handled?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- List the 18 models with missing includes
- Document if includes are available elsewhere
- Add evidence and decision

### Unknown 1.5: Should batch verification update catalog.json or the new database?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document migration approach recommendation
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 2 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with summary of findings
4. Check off all acceptance criteria:
   - [ ] All 219 models validated
   - [ ] No missing required fields identified
   - [ ] Error categories documented
   - [ ] Quality report created
   - [ ] Recommendations for new schema documented
   - [ ] Unknowns 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Key findings

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 2: Review Sprint 13 Catalog Quality

- Created CATALOG_QUALITY_REPORT.md with quality analysis
- Validated all 219 models in catalog.json
- Documented error categories and recommendations
- Verified Unknowns 1.3, 1.4, 1.5 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 2 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 2: Review Sprint 13 Catalog Quality" \
  --body "## Summary

Completed Sprint 14 Prep Task 2: Review Sprint 13 Catalog Quality.

## Changes

- Created \`docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results for Unknowns 1.3, 1.4, 1.5
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 2 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 1.3: License limit error handling
- Unknown 1.4: Missing \$include file handling
- Unknown 1.5: Catalog vs database update strategy

## Acceptance Criteria

- [x] All 219 models validated
- [x] No missing required fields identified
- [x] Error categories documented
- [x] Quality report created
- [x] Recommendations for new schema documented
- [x] Unknowns 1.3, 1.4, 1.5 verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 3: Survey JSON Schema Best Practices

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 3: Survey JSON Schema Best Practices.

## Task Overview

**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** Task 1 (Known Unknowns) - COMPLETE  
**Unknowns to Verify:** 2.1, 2.2, 2.7

## Objective

Research JSON Schema best practices to inform the database schema design for Sprint 14.

## Why This Matters

Sprint 14 deliverable includes `data/gamslib/schema.json` for validation. Understanding best practices ensures a well-designed, extensible schema.

## Background

PROJECT_PLAN.md specifies a comprehensive schema with nested objects for:
- Convexity verification results
- nlp2mcp parse status
- nlp2mcp translate status
- MCP solve status

## What Needs to Be Done

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

## Deliverables

- `docs/research/JSON_SCHEMA_BEST_PRACTICES.md`
- Recommended schema draft version
- Field naming convention guide
- Nested vs flat structure recommendation

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 2.1: Should schema use Draft-07 or Draft 2020-12?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document which draft version to use and why
- Add findings about library compatibility
- Add evidence and decision

### Unknown 2.2: Should convexity data be a nested object or flat fields?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document pros/cons of each approach
- Make recommendation for Sprint 14
- Add evidence and decision

### Unknown 2.7: How to handle schema migrations for future changes?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document versioning strategy
- Document migration approach
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 3 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with summary of findings
4. Check off all acceptance criteria:
   - [ ] JSON Schema specification reviewed
   - [ ] Versioning strategy documented
   - [ ] Best practices documented
   - [ ] Recommendations for Sprint 14 schema provided
   - [ ] Unknowns 2.1, 2.2, 2.7 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Key recommendations

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 3: Survey JSON Schema Best Practices

- Created JSON_SCHEMA_BEST_PRACTICES.md research document
- Documented Draft-07 vs Draft 2020-12 comparison
- Established field naming conventions
- Recommended nested structure approach
- Verified Unknowns 2.1, 2.2, 2.7 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 3 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 3: Survey JSON Schema Best Practices" \
  --body "## Summary

Completed Sprint 14 Prep Task 3: Survey JSON Schema Best Practices.

## Changes

- Created \`docs/research/JSON_SCHEMA_BEST_PRACTICES.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results for Unknowns 2.1, 2.2, 2.7
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 3 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 2.1: Schema draft version selection
- Unknown 2.2: Nested vs flat structure decision
- Unknown 2.7: Schema migration strategy

## Key Recommendations

[Include key recommendations from research]

## Acceptance Criteria

- [x] JSON Schema specification reviewed
- [x] Versioning strategy documented
- [x] Best practices documented
- [x] Recommendations for Sprint 14 schema provided
- [x] Unknowns 2.1, 2.2, 2.7 verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 4: Research jsonschema Library Usage

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 4: Research jsonschema Library Usage.

## Task Overview

**Priority:** High  
**Estimated Time:** 2 hours  
**Dependencies:** Task 3 (JSON Schema Best Practices)  
**Unknowns to Verify:** 2.1, 2.3, 2.5

## Objective

Research the Python jsonschema library to understand validation capabilities and integration patterns.

## Why This Matters

Sprint 14 requires schema validation integrated into db_manager.py. Understanding the library ensures correct implementation.

## Background

From PROJECT_PLAN.md: "Implement JSON schema validation (jsonschema library)"

## What Needs to Be Done

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

## Deliverables

- `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md`
- Example validation code snippets
- Error handling recommendations

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 2.1: Should schema use Draft-07 or Draft 2020-12?
- Update status if not already verified by Task 3
- Add library-specific findings about draft support
- Add evidence and decision

### Unknown 2.3: What fields should be required vs optional?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document how jsonschema handles required/optional
- Document partial validation approach
- Add evidence and decision

### Unknown 2.5: How should error messages be stored (structured vs string)?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document jsonschema error formats
- Recommend error storage approach
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 4 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with summary of findings
4. Check off all acceptance criteria:
   - [ ] jsonschema library version confirmed
   - [ ] Validation patterns documented
   - [ ] Example code created
   - [ ] Integration approach defined
   - [ ] Unknowns 2.1, 2.3, 2.5 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Key findings about the library

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 4: Research jsonschema Library Usage

- Created JSONSCHEMA_LIBRARY_GUIDE.md with usage patterns
- Documented validation API and error handling
- Created example code snippets
- Verified Unknowns 2.1, 2.3, 2.5 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 4 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 4: Research jsonschema Library Usage" \
  --body "## Summary

Completed Sprint 14 Prep Task 4: Research jsonschema Library Usage.

## Changes

- Created \`docs/research/JSONSCHEMA_LIBRARY_GUIDE.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results for Unknowns 2.1, 2.3, 2.5
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 4 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 2.1: Schema draft version (library support)
- Unknown 2.3: Required vs optional field handling
- Unknown 2.5: Error message storage approach

## Key Findings

[Include key findings about the library]

## Acceptance Criteria

- [x] jsonschema library version confirmed
- [x] Validation patterns documented
- [x] Example code created
- [x] Integration approach defined
- [x] Unknowns 2.1, 2.3, 2.5 verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 5: Design Database Schema Draft

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 5: Design Database Schema Draft.

## Task Overview

**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Tasks 3, 4 (Schema research)  
**Unknowns to Verify:** 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.3

## Objective

Create draft database schema based on PROJECT_PLAN.md specification and research findings.

## Why This Matters

The database schema is a central Sprint 14 deliverable. Having a validated draft before Day 1 prevents design iteration during the sprint.

## Background

PROJECT_PLAN.md (lines 130-175) provides a detailed schema template with:
- Model identification fields
- Convexity verification nested object
- nlp2mcp_parse nested object
- nlp2mcp_translate nested object
- mcp_solve nested object

## What Needs to Be Done

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

## Deliverables

- `docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json`
- `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md`
- Field descriptions and valid values
- Migration notes from current catalog

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 2.2: Should convexity data be a nested object or flat fields?
- Update status to ✅ VERIFIED with final decision
- Document chosen approach and rationale

### Unknown 2.3: What fields should be required vs optional?
- Update status to ✅ VERIFIED
- Document required field list
- Document optional field handling

### Unknown 2.4: How should pipeline status enums be defined?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document status values for each stage
- Document consistency approach

### Unknown 2.5: How should error messages be stored (structured vs string)?
- Update status to ✅ VERIFIED with final decision
- Document error structure in schema

### Unknown 2.6: Should schema include nlp2mcp version tracking?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document version tracking approach
- Add evidence and decision

### Unknown 2.7: How to handle schema migrations for future changes?
- Update status to ✅ VERIFIED with final decision
- Document schema_version field placement

### Unknown 4.3: Should schema.json be separate from database file?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document file organization decision
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 5 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with summary of schema design
4. Check off all acceptance criteria:
   - [ ] Draft schema created following PROJECT_PLAN.md template
   - [ ] Schema is valid JSON Schema (Draft-07)
   - [ ] All fields documented
   - [ ] Tested against sample catalog entries
   - [ ] Migration approach documented
   - [ ] Unknowns 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.3 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Schema highlights

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

Validate the schema:
```bash
python3 -c "
import json
from jsonschema import Draft7Validator
with open('docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json') as f:
    schema = json.load(f)
Draft7Validator.check_schema(schema)
print('Schema is valid JSON Schema')
"
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 5: Design Database Schema Draft

- Created DRAFT_SCHEMA.json with comprehensive field definitions
- Created SCHEMA_DESIGN_NOTES.md with rationale and examples
- Documented migration approach from catalog.json
- Verified Unknowns 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 5 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 5: Design Database Schema Draft" \
  --body "## Summary

Completed Sprint 14 Prep Task 5: Design Database Schema Draft.

## Changes

- Created \`docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json\`
- Created \`docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 5 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 2.2: Nested structure decision
- Unknown 2.3: Required vs optional fields
- Unknown 2.4: Pipeline status enums
- Unknown 2.5: Error message structure
- Unknown 2.6: Version tracking approach
- Unknown 2.7: Schema migration strategy
- Unknown 4.3: Schema file organization

## Schema Highlights

[Include key schema decisions]

## Acceptance Criteria

- [x] Draft schema created following PROJECT_PLAN.md template
- [x] Schema is valid JSON Schema (Draft-07)
- [x] All fields documented
- [x] Tested against sample catalog entries
- [x] Migration approach documented
- [x] Unknowns verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 6: Analyze Parse Rate for Verified Models

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 6: Analyze Parse Rate for Verified Models.

## Task Overview

**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** Task 2 (Catalog Quality Review)  
**Unknowns to Verify:** 1.1, 1.2, 1.3

## Objective

Determine the current nlp2mcp parse success rate for the 160 verified convex models to establish a baseline for Sprint 14.

## Why This Matters

Sprint 14 will track parse/translate/solve status for all models. Understanding current parse rate helps set realistic targets and identify blockers.

## Background

From Sprint 13:
- 57 verified_convex models (LP)
- 103 likely_convex models (NLP/QCP)
- Total: 160 models ready for pipeline testing

From prior work (docs/research/gamslib_parse_errors.md):
- Known parse blockers exist (unsupported syntax)
- Tier 1 models have 100% parse rate
- Tier 2 models have partial parse rate

## What Needs to Be Done

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

## Deliverables

- `docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md`
- Sample of 20-30 models tested
- Parse success rate percentage
- Top failure categories

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 1.1: How long will batch verification of 160+ models take?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document average parse time per model
- Project total batch time
- Add evidence and decision

### Unknown 1.2: What percentage of verified models will successfully parse through nlp2mcp?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document actual parse success rate from sample
- Project rate for full corpus
- Add evidence and decision

### Unknown 1.3: How should models with license limit errors be handled?
- Update status if additional findings from parse testing
- Document if license errors occur during parsing

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 6 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with parse rate findings
4. Check off all acceptance criteria:
   - [ ] 20+ models tested with nlp2mcp parser
   - [ ] Parse success rate calculated
   - [ ] Failure reasons categorized
   - [ ] Baseline documented for Sprint 14
   - [ ] Unknowns 1.1, 1.2, 1.3 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Key metrics (parse rate, timing)

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 6: Analyze Parse Rate for Verified Models

- Created PARSE_RATE_BASELINE.md with sample testing results
- Tested X models with Y% parse success rate
- Documented top failure categories
- Verified Unknowns 1.1, 1.2, 1.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 6 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 6: Analyze Parse Rate for Verified Models" \
  --body "## Summary

Completed Sprint 14 Prep Task 6: Analyze Parse Rate for Verified Models.

## Changes

- Created \`docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 6 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 1.1: Batch verification timing
- Unknown 1.2: Parse success rate baseline
- Unknown 1.3: License error handling (additional findings)

## Key Metrics

- Models tested: X
- Parse success rate: Y%
- Average parse time: Z seconds

## Acceptance Criteria

- [x] 20+ models tested with nlp2mcp parser
- [x] Parse success rate calculated
- [x] Failure reasons categorized
- [x] Baseline documented for Sprint 14
- [x] Unknowns verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 7: Review Existing db_manager Patterns

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 7: Review Existing db_manager Patterns.

## Task Overview

**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Dependencies:** None  
**Unknowns to Verify:** 3.1, 3.5, 3.6

## Objective

Review existing script patterns in the codebase to inform db_manager.py design.

## Why This Matters

Consistent patterns improve maintainability. Understanding existing conventions ensures db_manager.py follows project standards.

## Background

Sprint 13 created several GAMSLIB scripts:
- `scripts/gamslib/discover_models.py`
- `scripts/gamslib/download_models.py`
- `scripts/gamslib/verify_convexity.py`
- `scripts/gamslib/catalog.py` (dataclasses)

## What Needs to Be Done

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

## Deliverables

- `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md`
- CLI subcommand specification
- Reusable pattern notes

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 3.1: What subcommands are essential for db_manager.py?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document essential subcommand list
- Document nice-to-have subcommands
- Add evidence and decision

### Unknown 3.5: Should db_manager follow existing script patterns?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document which patterns to follow
- Document any deviations needed
- Add evidence and decision

### Unknown 3.6: What backup strategy should db_manager use?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document backup strategy recommendation
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 7 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with design summary
4. Check off all acceptance criteria:
   - [ ] Existing scripts reviewed
   - [ ] CLI patterns documented
   - [ ] db_manager interface designed
   - [ ] Subcommand list finalized
   - [ ] Unknowns 3.1, 3.5, 3.6 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Key design decisions

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 7: Review Existing db_manager Patterns

- Created DB_MANAGER_DESIGN.md with CLI specification
- Documented existing script patterns
- Defined subcommand structure
- Verified Unknowns 3.1, 3.5, 3.6 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 7 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 7: Review Existing db_manager Patterns" \
  --body "## Summary

Completed Sprint 14 Prep Task 7: Review Existing db_manager Patterns.

## Changes

- Created \`docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 7 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 3.1: Essential subcommands list
- Unknown 3.5: Script pattern conformance
- Unknown 3.6: Backup strategy

## db_manager Subcommands

[List finalized subcommands]

## Acceptance Criteria

- [x] Existing scripts reviewed
- [x] CLI patterns documented
- [x] db_manager interface designed
- [x] Subcommand list finalized
- [x] Unknowns verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 8: Establish Performance Baselines

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 8: Establish Performance Baselines.

## Task Overview

**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** Task 6 (Parse Rate Analysis)  
**Unknowns to Verify:** 1.1, 5.3

## Objective

Establish performance baselines for batch operations to inform Sprint 14 timeout and resource settings.

## Why This Matters

Sprint 14 involves batch verification of 160+ models. Understanding performance characteristics prevents timeout issues and enables progress estimation.

## Background

From Sprint 13 verification:
- Individual model verification: ~1-60 seconds
- Batch of 219 models: ~30 minutes total
- Timeouts configured at 60 seconds

## What Needs to Be Done

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

## Deliverables

- `docs/planning/EPIC_3/SPRINT_14/PERFORMANCE_BASELINES.md`
- Catalog I/O performance metrics
- Batch operation projections
- Recommended configurations

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 1.1: How long will batch verification of 160+ models take?
- Update status to ✅ VERIFIED with timing projections
- Document measured times
- Project total batch time
- Add evidence and decision

### Unknown 5.3: Should multi-solver validation be synchronous or parallel?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Document timing comparison if tested
- Make recommendation for Sprint 14
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 8 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with performance findings
4. Check off all acceptance criteria:
   - [ ] Catalog load/save times measured
   - [ ] Single model verification time measured
   - [ ] Batch performance projected
   - [ ] Recommendations documented
   - [ ] Unknowns 1.1, 5.3 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Key performance metrics

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 8: Establish Performance Baselines

- Created PERFORMANCE_BASELINES.md with timing metrics
- Documented catalog I/O performance
- Projected batch verification time
- Verified Unknowns 1.1, 5.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 8 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 8: Establish Performance Baselines" \
  --body "## Summary

Completed Sprint 14 Prep Task 8: Establish Performance Baselines.

## Changes

- Created \`docs/planning/EPIC_3/SPRINT_14/PERFORMANCE_BASELINES.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with verification results
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 8 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 1.1: Batch verification timing (confirmed)
- Unknown 5.3: Parallel vs sequential validation

## Key Metrics

- Catalog load time: X ms
- Catalog save time: X ms
- Single model parse time: X seconds
- Projected batch time: X minutes

## Acceptance Criteria

- [x] Catalog load/save times measured
- [x] Single model verification time measured
- [x] Batch performance projected
- [x] Recommendations documented
- [x] Unknowns verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 9: Review Sprint 13 Retrospective Items

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 9: Review Sprint 13 Retrospective Items.

## Task Overview

**Priority:** High  
**Estimated Time:** 1 hour  
**Dependencies:** None  
**Unknowns to Verify:** 1.3, 1.4, 1.5

## Objective

Review Sprint 13 retrospective and ensure all follow-up items are captured for Sprint 14.

## Why This Matters

Sprint 13 identified lessons learned and recommendations. Ensuring these are incorporated prevents repeating issues.

## Background

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

## What Needs to Be Done

1. **Review SPRINT_SUMMARY.md**
   - Extract all action items
   - Categorize by priority

2. **Map to Sprint 14 tasks**
   - Which items apply to Sprint 14?
   - Which should be deferred?

3. **Update Sprint 14 planning**
   - Add relevant items to Known Unknowns
   - Include in detailed schedule

## Deliverables

- Checklist of Sprint 13 follow-up items
- Mapping to Sprint 14 tasks
- Items to defer documented

## Known Unknowns to Verify

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` with verification results for:

### Unknown 1.3: How should models with license limit errors be handled?
- Update status with retrospective insights
- Document filter strategy from lessons learned
- Add evidence and decision

### Unknown 1.4: How should models with missing $include files be handled?
- Update status with retrospective insights
- Document handling strategy
- Add evidence and decision

### Unknown 1.5: Should batch verification update catalog.json or the new database?
- Update status with retrospective insights
- Document migration/transition approach
- Add evidence and decision

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 9 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with summary of items captured
4. Check off all acceptance criteria:
   - [ ] SPRINT_SUMMARY.md reviewed
   - [ ] All recommendations captured
   - [ ] Items mapped to Sprint 14 or deferred
   - [ ] No items lost between sprints
   - [ ] Unknowns 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Key items captured/mapped

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 9: Review Sprint 13 Retrospective Items

- Reviewed SPRINT_SUMMARY.md recommendations
- Mapped action items to Sprint 14 tasks
- Documented deferred items
- Verified Unknowns 1.3, 1.4, 1.5 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 9 status to COMPLETE"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 9: Review Sprint 13 Retrospective Items" \
  --body "## Summary

Completed Sprint 14 Prep Task 9: Review Sprint 13 Retrospective Items.

## Changes

- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` with retrospective insights
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 9 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Unknowns Verified

- Unknown 1.3: License limit handling (retrospective insights)
- Unknown 1.4: Missing include handling (retrospective insights)
- Unknown 1.5: Database update strategy (retrospective insights)

## Items Captured

[List key items from retrospective]

## Items Deferred

[List any deferred items]

## Acceptance Criteria

- [x] SPRINT_SUMMARY.md reviewed
- [x] All recommendations captured
- [x] Items mapped to Sprint 14 or deferred
- [x] No items lost between sprints
- [x] Unknowns verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.
```

---

## Task 10: Plan Sprint 14 Detailed Schedule

### Prompt

```
On branch `planning/sprint14-prep`, complete Sprint 14 Prep Task 10: Plan Sprint 14 Detailed Schedule.

## Task Overview

**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** All previous tasks  
**Unknowns to Verify:** All (integrates findings from all unknowns)

## Objective

Create detailed day-by-day Sprint 14 plan incorporating all prep task findings.

## Why This Matters

A detailed schedule ensures all deliverables are completed on time and dependencies are respected.

## Background

From PROJECT_PLAN.md, Sprint 14 has three major components:
1. Complete Convexity Verification (~10-12h)
2. JSON Database Schema Design (~6-8h)
3. Database Management Scripts (~8-10h)

Total estimated effort: 24-30 hours (~10 working days)

## What Needs to Be Done

1. **Synthesize prep task findings**
   - Known unknowns verification results
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

## Deliverables

- `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- Day-by-day schedule with tasks
- Checkpoints with success criteria
- Risk mitigation strategies

## Known Unknowns Status Check

Before completing this task, verify all unknowns in KNOWN_UNKNOWNS.md have been addressed:

### Category 1: Complete Convexity Verification
- [ ] Unknown 1.1: Verified by Tasks 6, 8
- [ ] Unknown 1.2: Verified by Task 6
- [ ] Unknown 1.3: Verified by Tasks 2, 9
- [ ] Unknown 1.4: Verified by Tasks 2, 9
- [ ] Unknown 1.5: Verified by Tasks 2, 9

### Category 2: JSON Database Schema Design
- [ ] Unknown 2.1: Verified by Tasks 3, 4
- [ ] Unknown 2.2: Verified by Tasks 3, 5
- [ ] Unknown 2.3: Verified by Tasks 4, 5
- [ ] Unknown 2.4: Verified by Task 5
- [ ] Unknown 2.5: Verified by Tasks 4, 5
- [ ] Unknown 2.6: Verified by Task 5
- [ ] Unknown 2.7: Verified by Tasks 3, 5

### Category 3: Database Management Scripts
- [ ] Unknown 3.1: Verified by Task 7
- [ ] Unknown 3.2: Document in PLAN.md (implementation detail)
- [ ] Unknown 3.3: Document in PLAN.md (implementation detail)
- [ ] Unknown 3.4: Document in PLAN.md (implementation detail)
- [ ] Unknown 3.5: Verified by Task 7
- [ ] Unknown 3.6: Verified by Task 7

### Category 4: Version Control Strategy
- [ ] Unknown 4.1: Document in PLAN.md
- [ ] Unknown 4.2: Document in PLAN.md
- [ ] Unknown 4.3: Verified by Task 5
- [ ] Unknown 4.4: Document in PLAN.md (low priority)

### Category 5: Multi-Solver Validation
- [ ] Unknown 5.1: Document as optional in PLAN.md
- [ ] Unknown 5.2: Document as optional in PLAN.md
- [ ] Unknown 5.3: Verified by Task 8
- [ ] Unknown 5.4: Document as optional in PLAN.md

Update any remaining unknowns with decisions or mark as "DEFERRED to Sprint implementation".

## Update PREP_PLAN.md

After completing the task, update `docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md`:

1. Change Task 10 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in the **Changes** section with files created/modified
3. Fill in the **Result** section with plan summary
4. Check off all acceptance criteria:
   - [ ] All prep task findings incorporated
   - [ ] 10-day schedule created
   - [ ] Checkpoints defined (Days 3, 5, 7, 10)
   - [ ] Acceptance criteria for each deliverable
   - [ ] Risks identified with mitigations
   - [ ] PLAN.md reviewed and approved
   - [ ] All unknowns verified and updated in KNOWN_UNKNOWNS.md

5. Update Summary section to check off all success criteria

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` with:
- Task name and date
- Branch name
- Summary of work completed
- Files created/modified
- Sprint 14 ready status

## Quality Gate

If any Python code was created or modified:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 14 Prep Task 10: Plan Sprint 14 Detailed Schedule

- Created PLAN.md with 10-day schedule
- Defined checkpoints and acceptance criteria
- Documented risks and mitigations
- Integrated all prep task findings
- Verified all remaining unknowns in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 10 status to COMPLETE
- All prep tasks now complete - Sprint 14 ready to begin"

git push origin planning/sprint14-prep
```

## Create Pull Request

Use `gh` to create a pull request:

```bash
gh pr create --title "Sprint 14 Prep Task 10: Plan Sprint 14 Detailed Schedule" \
  --body "## Summary

Completed Sprint 14 Prep Task 10: Plan Sprint 14 Detailed Schedule.

**All 10 prep tasks are now COMPLETE. Sprint 14 is ready to begin.**

## Changes

- Created \`docs/planning/EPIC_3/SPRINT_14/PLAN.md\`
- Updated \`docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md\` (all unknowns addressed)
- Updated \`docs/planning/EPIC_3/SPRINT_14/PREP_PLAN.md\` Task 10 status to COMPLETE
- Updated \`CHANGELOG.md\`

## Sprint 14 Schedule Overview

- Days 1-2: Schema design and validation
- Days 3-5: db_manager.py implementation
- Days 6-7: Batch verification execution
- Days 8-9: Integration and testing
- Day 10: Documentation and review

## Checkpoints

- Day 3: Schema complete and validated
- Day 5: db_manager core functions working
- Day 7: Verification batch complete
- Day 10: All deliverables ready

## Prep Phase Summary

| Task | Status | Unknowns Verified |
|------|--------|-------------------|
| Task 1: Known Unknowns | ✅ COMPLETE | N/A |
| Task 2: Catalog Quality | ✅ COMPLETE | 1.3, 1.4, 1.5 |
| Task 3: JSON Schema Best Practices | ✅ COMPLETE | 2.1, 2.2, 2.7 |
| Task 4: jsonschema Library | ✅ COMPLETE | 2.1, 2.3, 2.5 |
| Task 5: Schema Draft | ✅ COMPLETE | 2.2-2.7, 4.3 |
| Task 6: Parse Rate | ✅ COMPLETE | 1.1, 1.2, 1.3 |
| Task 7: db_manager Patterns | ✅ COMPLETE | 3.1, 3.5, 3.6 |
| Task 8: Performance Baselines | ✅ COMPLETE | 1.1, 5.3 |
| Task 9: Retrospective | ✅ COMPLETE | 1.3, 1.4, 1.5 |
| Task 10: Schedule | ✅ COMPLETE | All |

## Acceptance Criteria

- [x] All prep task findings incorporated
- [x] 10-day schedule created
- [x] Checkpoints defined (Days 3, 5, 7, 10)
- [x] Acceptance criteria for each deliverable
- [x] Risks identified with mitigations
- [x] PLAN.md reviewed and approved
- [x] All unknowns verified and updated" \
  --base main
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback.

---

## Final Notes

After Task 10 is complete and the PR is merged, Sprint 14 preparation is complete. The team can proceed with Sprint 14 Day 1 using the detailed schedule in PLAN.md.
```

---

## Usage Notes

1. **Execute tasks in order** - Tasks 3-5 have dependencies on earlier tasks
2. **Branch management** - All tasks use the same `planning/sprint14-prep` branch
3. **PR strategy** - Each task creates a separate PR for review, or alternatively, batch related tasks into a single PR
4. **Quality gate** - Always run quality checks before committing Python code
5. **Unknown verification** - Each task must update the associated unknowns in KNOWN_UNKNOWNS.md
6. **Changelog entries** - Add entries chronologically under `## [Unreleased]`
