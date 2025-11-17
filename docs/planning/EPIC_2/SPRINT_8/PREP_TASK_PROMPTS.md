# Sprint 8 Preparation Task Prompts

**Purpose:** Comprehensive prompts for executing Sprint 8 prep tasks (Tasks 2-10)  
**Usage:** Use each prompt to guide task execution, ensuring all deliverables, unknowns verification, and documentation updates are completed  
**Format:** Each prompt is standalone and includes full context from PREP_PLAN.md

---

## Task 2: Analyze GAMSLib Per-Model Feature Dependencies

**On a new branch:** `prep/sprint8-task2-feature-matrix`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Create comprehensive feature dependency matrix for all 10 GAMSLib models showing: (1) which features each model needs to parse, (2) which models are "close" (1-2 features away), (3) feature unlock rates, (4) recommended Sprint 8 feature priority.

**Deliverable:** `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md`

**Why This Matters:**
Sprint 7 retrospective identified this as critical gap: *"Didn't deeply analyze what each individual model needs to parse... some models have multiple blocking issues (e.g., circle.gms needs preprocessor AND function call syntax)."*

Feature-based analysis (Sprint 7 approach) assumed preprocessor unlocks 3 models. Actual result: unlocked 1 model (20% vs 30% target). Per-model analysis prevents this.

**Key questions:**
- Which models need only 1 feature to parse? (high ROI targets for Sprint 8)
- Which feature appears in most models? (option statements? indexed assignments?)
- What's the realistic parse rate for Sprint 8? (25%? 30%? depends on overlap)
- Should Sprint 8 prioritize indexed assignments or function calls?

**Background:**
From Sprint 7 RETROSPECTIVE.md (lines 146-160):
> **Recommendations for Sprint 8:**
> - Create per-model feature dependency matrix before sprint planning
> - Understand which models are "close" to parsing (1-2 features away)
> - Map out multi-feature dependencies
> - Prioritize models with single blocking issues

Current GAMSLib status (from `docs/status/GAMSLIB_CONVERSION_STATUS.md`):
- **Parsing:** mhw4d.gms ✅, rbrock.gms ✅ (20%)
- **Failing:** circle, himmel16, hs62, mathopt1, maxmin, mhw4dx, mingamma, trig (80%)

Sprint 8 targets (from PROJECT_PLAN.md lines 84-148):
- Option statements (unlocks mhw4dx.gms - known)
- One additional feature: indexed assignments OR function calls (TBD - depends on this analysis)

### 2. WHAT TO DELIVER

**1. Per-Model Error Deep Dive (3-4 hours)**

For each of the 8 failing models, document:
- Primary error message and location
- Root cause (missing feature? parser bug? grammar limitation?)
- Secondary errors (what breaks if primary is fixed?)
- Estimated parsing percentage if primary error fixed
- Dependencies (which features needed for full parse)

**Models to analyze:**
1. **circle.gms** - Last seen: ParserSemanticError on uniform() function call
2. **himmel16.gms** - Last seen: UnexpectedCharacters on i++1 (lead/lag indexing)
3. **hs62.gms** - Last seen: UnexpectedCharacters on model section (mx)
4. **mathopt1.gms** - Last seen: ParserSemanticError on indexed assignment
5. **maxmin.gms** - Last seen: UnexpectedCharacters on low(n,nn) nested indexing
6. **mhw4dx.gms** - Last seen: UnexpectedCharacters on option limCol
7. **mingamma.gms** - Last seen: UnexpectedCharacters on model section (m2)
8. **trig.gms** - Last seen: ParserSemanticError on bound_scalar

For each model, create section:
```markdown
### Model: circle.gms

**Primary Error:**
- Type: ParserSemanticError
- Location: Line 32, column 15
- Message: "Assignments must use numeric constants; got Call(uniform, ...)"
- Code: `size = uniform(1.0, 10.0);`

**Root Cause:**
- Missing feature: Function calls in assignments
- Parser expects numeric constants, gets function call AST node

**Secondary Errors (if primary fixed):**
- Likely: Additional preprocessor directives ($if not set)
- Possible: Set range syntax if used elsewhere in model

**Parsing Percentage if Primary Fixed:**
- Estimated: 70-80% (function calls fix, but preprocessor may block)

**Full Parse Dependencies:**
- [ ] Function call syntax in assignments (6-8 hours)
- [ ] Preprocessor directives (already implemented in Sprint 7)
- Total features needed: 2 (multiple-feature dependency)

**Priority for Sprint 8:**
- Medium-Low (needs 2 features, both Medium complexity)
```

**2. Feature Dependency Matrix (2-3 hours)**

Create table showing feature overlap across models:

| Feature | Complexity | Effort | Models Needing | Unlock Rate | Priority |
|---------|------------|--------|----------------|-------------|----------|
| Option statements | Low | 6-8h | mhw4dx, ? | 10-20% | High |
| Indexed assignments | Medium | 6-8h | mathopt1, ? | ?% | TBD |
| Function calls in assignments | Medium | 6-8h | circle, ? | ?% | TBD |
| Lead/lag indexing (i++1) | High | 8-10h | himmel16 | 10% | Low (Sprint 8b) |
| Model sections (mx) | Medium | 5-6h | hs62, mingamma | 20% | Low (Sprint 8b) |
| Nested indexing | High | 8-10h | maxmin | 10% | Low |

**3. Sprint 8 Feature Recommendation (2-3 hours)**

Based on matrix, recommend:
- **Confirmed Sprint 8 Feature:** Option statements (known to unlock mhw4dx)
- **Candidate Sprint 8 Feature:** Indexed assignments OR Function calls
  - Calculate unlock rate for each
  - Estimate combined parse rate (option + candidate)
  - Validate 25% target achievability
  - Recommend priority

Analysis framework:
```markdown
## Sprint 8 Feature Recommendation

### Confirmed: Option Statements
- Unlocks: mhw4dx.gms (confirmed)
- Unlock rate: +10% (2/10 → 3/10)
- Effort: 6-8 hours
- Risk: Low
- Status: Include in Sprint 8

### Candidate A: Indexed Assignments
- Appears in: mathopt1.gms, [others?]
- Potential unlock rate: +10% (if only mathopt1) or +20% (if 2 models)
- Effort: 6-8 hours
- Complexity: Medium (grammar changes)
- Combined with options: 30% parse rate (realistic)

### Candidate B: Function Calls in Assignments
- Appears in: circle.gms, [others?]
- Potential unlock rate: +0% (circle needs 2 features) or +10% (if unlocks 1 model)
- Effort: 6-8 hours
- Complexity: Medium
- Combined with options: 20-30% parse rate

### Recommendation: [TBD based on matrix]
- Rationale: [Higher unlock rate / fewer dependencies / Sprint 8b deferral strategy]
- Parse rate projection: 25% (conservative) to 30% (optimistic)
- Risk assessment: [LOW/MEDIUM]
```

**4. Models "Close" to Parsing (1 hour)**

Identify quick wins:
- Models needing only 1 feature (high priority for Sprint 8)
- Models needing 2 features where 1 is already implemented (Sprint 7 features)
- Models needing 2 features where both are Sprint 8 candidates

**5. Sprint 8b Boundary Recommendation (<1 hour)**

List features deferred to Sprint 8b:
- Advanced indexing (i++1) - himmel16.gms
- Model sections (mx) - hs62.gms, mingamma.gms
- Other high-complexity features

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (400+ lines)
- Per-model analysis for all 8 failing models
- Feature dependency matrix with unlock rates
- Sprint 8 feature recommendation (indexed assignments vs function calls)
- Models "close" to parsing (1-2 features away)
- Sprint 8b feature boundary

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 2.1, 2.2, 2.3

**Unknown 2.1: Can per-model analysis be completed in 8-10 hours?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 2 (Analyze GAMSLib Per-Model Feature Dependencies)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Per-model deep dive: [X hours actual] × 8 models
  - Feature matrix creation: [Y hours actual]
  - Recommendation write-up: [Z hours actual]
  - Total: [Total hours] (within/exceeds 8-10 hour estimate)
  
  **Evidence:**
  - Created comprehensive analysis for all 8 failing models
  - Feature dependency matrix shows clear unlock rates
  - Identified [N] models needing only 1 feature
  
  **Decision:**
  - 8-10 hour estimate [confirmed/needs adjustment to X-Y hours]
  - Per-model analysis approach is [feasible/requires more time in future]
  
  **Impact:**
  - Task 2 estimate accurate for prep phase planning
  - [If over estimate: Future per-model analyses should allocate X-Y hours]
  ```

**Unknown 2.2: Do most models have 1-feature or multi-feature dependencies?**
- Add verification results with:
  - Findings: "Found [N] models with 1-feature dependency, [M] with multi-feature"
  - Evidence: Feature matrix showing dependency counts
  - Decision: "[Indexed assignments/Function calls] selected based on ROI analysis"
  - Impact: "Parse rate projection: [25%/30%] achievable with [feature choice]"

**Unknown 2.3: How do we validate that per-model analysis prevents Sprint 7 underestimation?**
- Add verification results comparing Sprint 7 vs Sprint 8 methodology
- Document how per-model matrix captures multi-feature dependencies
- Confirm confidence level in parse rate projections

### 4. UPDATE PREP_PLAN.md

**Task 2 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` [XXX lines]
  
  **Per-Model Analysis:**
  - Analyzed all 8 failing GAMSLib models with primary/secondary errors
  - Documented root causes, parsing percentages, and feature dependencies
  - Identified [N] models with single-feature dependencies (high ROI)
  - Identified [M] models with multi-feature dependencies
  
  **Feature Dependency Matrix:**
  - Created comprehensive matrix with [N] features analyzed
  - Calculated unlock rates for each feature
  - Identified option statements: [unlock rate]
  - Identified [indexed assignments/function calls]: [unlock rate]
  
  **Sprint 8 Recommendation:**
  - Confirmed: Option statements (unlocks mhw4dx.gms, +10%)
  - Recommended: [Indexed assignments OR Function calls] (unlocks [models], +[X]%)
  - Combined parse rate projection: [25-30%] (conservative to optimistic)
  
  **Sprint 8b Boundary:**
  - Deferred: [List of features] to Sprint 8b based on complexity/ROI analysis
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] All 8 failing models analyzed with primary/secondary errors
  - [x] Feature dependency matrix created with unlock rates
  - [x] Sprint 8 feature recommendation provided with rationale
  - [x] Parse rate projection for Sprint 8 (25% conservative, 30% optimistic)
  - [x] Models "close" to parsing identified
  - [x] Sprint 8b boundary defined
  - [x] Cross-referenced with Sprint 7 RETROSPECTIVE.md recommendations
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 2 - Analyze GAMSLib Per-Model Feature Dependencies - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Created comprehensive per-model feature dependency matrix for all 10 GAMSLib models, identifying which features each model needs to parse and calculating unlock rates for Sprint 8 feature prioritization. This analysis prevents the feature-based underestimation that occurred in Sprint 7 (20% actual vs 30% target).

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (XXX lines)
  - Per-model analysis for 8 failing models (circle, himmel16, hs62, mathopt1, maxmin, mhw4dx, mingamma, trig)
  - Feature dependency matrix with unlock rates
  - Sprint 8 feature recommendation: Option statements + [Indexed assignments OR Function calls]
  - Models "close" to parsing identified ([N] models need only 1 feature)
  - Sprint 8b boundary defined

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 2.1, 2.2, 2.3)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 2 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Per-Model Analysis:**
- [N] models have single-feature dependencies (high ROI for Sprint 8)
- [M] models have multi-feature dependencies (Sprint 8b candidates)
- Primary blockers identified for each model with parsing percentages

**Feature Unlock Rates:**
- Option statements: Unlocks mhw4dx.gms (+10% parse rate, 2/10 → 3/10)
- [Indexed assignments/Function calls]: Unlocks [models] (+[X]% parse rate)
- Combined: [25-30%] parse rate achievable (meets Sprint 8 target)

**Sprint 8 Recommendation:**
- **Confirmed:** Option statements (Low complexity, High ROI, 6-8 hours)
- **Recommended:** [Indexed assignments OR Function calls] ([Rationale])
- **Deferred to Sprint 8b:** [List features] (High complexity or Low ROI)

**Methodology Validation:**
- Per-model analysis took [X] hours (within 8-10 hour estimate)
- Approach successfully identifies multi-feature dependencies
- Higher confidence in parse rate projections vs Sprint 7

#### Unknown Verification

**2.1: Can per-model analysis be completed in 8-10 hours?**
- ✅ VERIFIED: Completed in [X] hours ([within/slightly over] estimate)
- Pilot test on 2 models validated effort extrapolation

**2.2: Do most models have 1-feature or multi-feature dependencies?**
- ✅ VERIFIED: [N] models have 1-feature, [M] have multi-feature
- Sprint 8 targeting 1-feature models for 25% parse rate goal

**2.3: How do we validate that per-model analysis prevents Sprint 7 underestimation?**
- ✅ VERIFIED: Matrix explicitly shows multi-feature dependencies
- Sprint 7 missed circle.gms needing 2 features (preprocessor + function calls)
- Sprint 8 analysis prevents similar underestimation

#### Next Steps

**Task 3:** Research Option Statement Syntax
- Validate 6-8 hour implementation estimate for option statements
- Design grammar for `option limrow = 0, limcol = 0;` pattern from mhw4dx.gms
- Confirm option statements are straightforward (as assumed in PREP_PLAN)

**Task 7:** Survey High-ROI Parser Features
- Deep dive on [Indexed assignments OR Function calls] based on recommendation
- Validate 6-8 hour implementation estimate
- Design grammar and test strategy for selected feature
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (RETROSPECTIVE.md, CONVERSION_STATUS.md, PROJECT_PLAN.md)
- ✅ Verify all 8 models analyzed with complete sections
- ✅ Verify feature matrix has unlock rate calculations
- ✅ Verify Sprint 8 recommendation has clear rationale
- ✅ Verify all 3 unknowns (2.1, 2.2, 2.3) have complete verification results
- ✅ Verify all Task 2 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task2-feature-matrix
git add -A
git commit -m "Complete Sprint 8 Prep Task 2: Analyze GAMSLib Per-Model Feature Dependencies

Created comprehensive feature dependency matrix for all 10 GAMSLib models,
providing data-driven feature prioritization for Sprint 8.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md (XXX lines)
  - Per-model analysis for 8 failing models
  - Feature dependency matrix with unlock rates
  - Sprint 8 feature recommendation
  - Sprint 8b boundary definition

PER-MODEL ANALYSIS:
- circle.gms: Function calls + preprocessor (2 features)
- himmel16.gms: Lead/lag indexing (i++1)
- hs62.gms: Model sections (mx)
- mathopt1.gms: Indexed assignments
- maxmin.gms: Nested indexing
- mhw4dx.gms: Option statements (CONFIRMED)
- mingamma.gms: Model sections (m2)
- trig.gms: [Analysis results]

SPRINT 8 RECOMMENDATION:
- Confirmed: Option statements (unlocks mhw4dx, +10%)
- Recommended: [Indexed assignments OR Function calls] (unlocks [models], +[X]%)
- Parse rate projection: [25-30%] (meets Sprint 8 target)
- Rationale: [Higher ROI / Single-feature models / Sprint 8b deferral]

UNKNOWN VERIFICATION:
- 2.1: Per-model analysis completed in [X] hours (within estimate)
- 2.2: [N] models have 1-feature dependencies (high ROI targets)
- 2.3: Matrix prevents Sprint 7-style underestimation

FILES MODIFIED:
- Created: GAMSLIB_FEATURE_MATRIX.md
- Modified: KNOWN_UNKNOWNS.md (verified 2.1, 2.2, 2.3)
- Modified: PREP_PLAN.md (Task 2 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task2-feature-matrix
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 2: Analyze GAMSLib Per-Model Feature Dependencies" \
  --body "Completes Task 2 of Sprint 8 prep phase.

## Deliverables
- ✅ GAMSLIB_FEATURE_MATRIX.md with per-model analysis
- ✅ Feature dependency matrix with unlock rates
- ✅ Sprint 8 feature recommendation: [Indexed assignments OR Function calls]
- ✅ Sprint 8b boundary defined
- ✅ Unknowns 2.1, 2.2, 2.3 verified

## Key Findings
- Option statements unlock mhw4dx.gms (+10%)
- [Recommended feature] unlocks [models] (+[X]%)
- Combined parse rate: [25-30%] (meets Sprint 8 target)
- [N] models have single-feature dependencies

## Unknown Verification
- 2.1: ✅ Analysis completed in [X] hours
- 2.2: ✅ [N] single-feature, [M] multi-feature models
- 2.3: ✅ Matrix prevents underestimation

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] All 8 failing models analyzed with primary/secondary errors
- [x] Feature dependency matrix created with unlock rates
- [x] Sprint 8 feature recommendation provided with rationale
- [x] Parse rate projection for Sprint 8 (25% conservative, 30% optimistic)
- [x] Models "close" to parsing identified
- [x] Sprint 8b boundary defined
- [x] Cross-referenced with Sprint 7 RETROSPECTIVE.md recommendations
- [x] Unknowns 2.1, 2.2, 2.3 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 2 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 3: Research Option Statement Syntax

**On a new branch:** `prep/sprint8-task3-option-research`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Comprehensive research of GAMS option statement syntax, semantics, and usage patterns to design parser implementation for Sprint 8. Focus on basic options (limrow, limcol) that unlock mhw4dx.gms while cataloging other option types for future work.

**Why This Matters:**
Option statements are confirmed high-priority for Sprint 8 (unlocks mhw4dx.gms = +10% parse rate). PROJECT_PLAN.md estimates 6-8 hours with "Low risk (grammar extension, semantic handling straightforward)". This research validates that estimate and identifies any hidden complexity.

From Sprint 7 retrospective: *"Prefer complete implementations of fewer features over partial implementations of many."* Need to define scope clearly: what's "basic options" vs deferred to Sprint 8b/9?

**Background:**
From `docs/status/GAMSLIB_CONVERSION_STATUS.md`, mhw4dx.gms fails on:
```
option limcol = 0, limrow = 0;
       ^
No terminal matches 'l' in the current parser context
```

Parser doesn't recognize `option` keyword at statement level. Need to:
1. Add `option` to grammar as statement type
2. Parse option name and value
3. Handle semantic meaning (or mock for Sprint 8)

From Sprint 7 fixtures, `tests/fixtures/statements/04_option_statement.gms` documents:
> Note: Option statements not yet supported, so they are commented out

Sprint 8 will uncomment and implement these.

### 2. WHAT TO DELIVER

**1. GAMS Documentation Survey (2-3 hours)**

Survey official GAMS documentation for option statement syntax:
- Statement format: `option name = value;` or `option name;` (boolean)?
- Value types: Integer? Float? String? Boolean?
- Multi-option format: `option a = 1, b = 2;` (comma-separated)?
- Scope rules: Global? Local to model? File-level?
- Common options: limrow, limcol, solprint, sysout, decimals, etc.

Create catalog:
```markdown
## Option Statement Syntax Patterns

### Basic Integer Options (Sprint 8 Target)
- `option limrow = 0;` - Limit number of rows in listing
- `option limcol = 0;` - Limit number of columns in listing
- `option decimals = 3;` - Decimal places in output
- Format: `option <name> = <integer>;`

### Boolean Options
- `option solprint = off;` - Suppress solution listing
- Format: `option <name> = on|off;` or `option <name>;` (implicitly on)

### Multi-Option Statements
- `option limrow = 0, limcol = 0, solprint = off;`
- Format: Comma-separated list

### String Options
- `option title = "My Model";`
- Format: `option <name> = "<string>";`

### Specialized Options (Defer to Sprint 8b/9)
- Solver-specific options
- File I/O options
- Advanced formatting options
```

**2. GAMSLib Usage Analysis (1-2 hours)**

Scan all 10 GAMSLib models for option statement usage:
```bash
grep -n "^option\|^ option" tests/fixtures/gamslib/*.gms
```

Catalog:
- Which models use options? (mhw4dx known, others?)
- Which option types? (Integer? Boolean? String?)
- How many options per model?
- Any edge cases or complex usage?

Example output:
```markdown
## GAMSLib Option Usage

### mhw4dx.gms
- Line 37: `option limcol = 0, limrow = 0;`
- Type: Multi-option, integer values
- Sprint 8 target: YES (unlocks model)

### [other models if applicable]
- Line X: `option ...`
- Type: ...
- Sprint 8 scope: YES/NO

### Summary
- Models using options: X/10
- Sprint 8 scope options: limrow, limcol (integer)
- Deferred options: [list]
```

**3. Grammar Design (2-3 hours)**

Design Lark grammar rules for option statements:

**Option 1: Simple approach (Sprint 8)**
```lark
// Add to statement-level grammar
statement: ... | option_stmt

option_stmt: "option" option_list ";"
option_list: option_item ("," option_item)*
option_item: NAME "=" (INTEGER | "on" | "off")

// NAME already defined
// INTEGER already defined
```

**Option 2: Comprehensive (Sprint 8b if needed)**
```lark
option_stmt: "option" option_list ";"
option_list: option_item ("," option_item)*
option_item: NAME "=" option_value
option_value: INTEGER | FLOAT | STRING | "on" | "off"
```

**Semantic handling:**
- Sprint 8: Store in AST, don't process (mock/skip approach)
- Future: Map to nlp2mcp behavior (e.g., limrow affects output verbosity)

**4. Test Fixture Planning (1 hour)**

Identify test cases for option statements:
```markdown
## Option Statement Test Fixtures

### Fixture 1: Single Integer Option
```gams
option limrow = 0;
```
Expected: Parse successfully, store in AST

### Fixture 2: Multi-Option Statement
```gams
option limrow = 0, limcol = 0;
```
Expected: Parse successfully, store multiple options

### Fixture 3: Boolean Option
```gams
option solprint = off;
```
Expected: Parse successfully

### Fixture 4: Option in Context (mhw4dx pattern)
```gams
Set i / 1*10 /;
option limrow = 0, limcol = 0;
Scalar x;
```
Expected: Parse successfully, option doesn't break surrounding statements

### Edge Cases
- Empty option list (syntax error)
- Missing semicolon (syntax error)
- Invalid option name (accept any NAME in Sprint 8)
- Invalid value type (e.g., `option limrow = "string";` - error or accept?)
```

**5. Implementation Effort Validation (1 hour)**

Validate PROJECT_PLAN.md estimate (6-8 hours):
- Grammar changes: 1-2 hours (straightforward)
- AST node creation: 1 hour
- Test fixtures: 2-3 hours (4 fixtures + edge cases)
- Integration testing: 1-2 hours (verify mhw4dx.gms parses)
- Documentation: 1 hour

**Total: 6-9 hours** ✅ (matches estimate)

If complexity higher than expected (e.g., semantic handling required), document risk and recommend scope reduction.

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (200+ lines)
- GAMS option syntax catalog
- GAMSLib usage analysis
- Lark grammar design
- Test fixture plan (4+ fixtures)
- Effort estimate validation

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 1.1, 1.2, 1.3

**Unknown 1.1: Is option statement semantic handling truly "straightforward"?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add verification results with findings from GAMS documentation survey
- Document whether mock/skip approach is sufficient or semantic processing required
- Validate 6-8 hour estimate based on complexity findings

**Unknown 1.2: What is the actual scope of option statements in GAMSLib models?**
- Add verification results with GAMSLib grep analysis results
- List which models use options and which types
- Confirm Sprint 8 scope (basic integer options) is sufficient

**Unknown 1.3: How do we know option statements unlock mhw4dx.gms?**
- Add verification results confirming option statement is the primary blocker
- Document any secondary errors found
- Validate +10% parse rate assumption

### 4. UPDATE PREP_PLAN.md

- Change Task 3 status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** and **Result** sections
- Check off ALL acceptance criteria:
  - [x] Option syntax patterns documented (integer, boolean, multi-option, string)
  - [x] GAMSLib usage analyzed (which models, which options)
  - [x] Lark grammar designed for Sprint 8 scope
  - [x] Test fixtures identified (4+ cases)
  - [x] Implementation effort validated (6-8 hours confirmed or adjusted)
  - [x] Sprint 8 vs Sprint 8b scope defined (basic options vs advanced)
  - [x] Semantic handling approach decided (mock/skip vs full processing)

### 5. UPDATE CHANGELOG.md

Add entry documenting Task 3 completion with key findings about option statement complexity and scope.

### 6. QUALITY GATES

- ✅ All cross-references valid
- ✅ All 3 unknowns (1.1, 1.2, 1.3) verified
- ✅ Grammar design is implementable
- ✅ Test fixtures cover Sprint 8 scope
- ✅ Documentation-only (skip code quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task3-option-research
git add -A
git commit -m "Complete Sprint 8 Prep Task 3: Research Option Statement Syntax

[Detailed commit message with findings and recommendations]"
git push -u origin prep/sprint8-task3-option-research
```

### 8. PULL REQUEST & REVIEW

```bash
gh pr create \
  --title "Complete Sprint 8 Prep Task 3: Research Option Statement Syntax" \
  --body "[PR description with deliverables and key findings]"

# Wait for Copilot review
# Address comments
# Merge when approved
```

### 9. ACCEPTANCE CRITERIA

- [x] Option syntax patterns documented (integer, boolean, multi-option, string)
- [x] GAMSLib usage analyzed (which models, which options)
- [x] Lark grammar designed for Sprint 8 scope
- [x] Test fixtures identified (4+ cases)
- [x] Implementation effort validated (6-8 hours confirmed or adjusted)
- [x] Sprint 8 vs Sprint 8b scope defined (basic options vs advanced)
- [x] Semantic handling approach decided (mock/skip vs full processing)
- [x] Unknowns 1.1, 1.2, 1.3 verified
- [x] PR created and merged

---

## Task 4: Design Parser Error Line Number Tracking

**On a new branch:** `prep/sprint8-task4-error-line-numbers`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Design approach to extend SourceLocation tracking from convexity warnings (Sprint 7) to ALL parser errors, achieving 100% coverage of parse errors with file/line/column information. Build on existing infrastructure for low-risk, high-impact UX improvement.

**Why This Matters:**
Sprint 7 delivered line number tracking for convexity warnings (W301-W305), dramatically improving developer experience. PROJECT_PLAN.md identifies parser error line numbers as Sprint 8 high priority: *"Extend SourceLocation tracking to parser errors (builds on Sprint 7 work)... Risk: Very Low (infrastructure exists)"*

**Current state:**
- Convexity warnings: ✅ Line numbers (format: "W301 in eq (10:1): message")
- Parser errors: ❌ No line numbers (just error message and type)

**Target state:**
- Parser errors: ✅ Line numbers (format: "E101: Parse error at file.gms:15:8: message")

**Background:**
From Sprint 7 Day 8, line number tracking implementation:
- **SourceLocation dataclass:** Already exists in `src/ir/symbols.py`
- **Lark metadata extraction:** `_extract_source_location()` in `src/ir/parser.py`
- **Integration pattern:** Add `source_location` field to data structures
- **String formatting:** `SourceLocation.__str__()` produces "file.gms:15:8"

Parser errors are simpler than convexity (no normalization step), so 4-6 hours is reasonable.

### 2. WHAT TO DELIVER

**1. Survey Parser Error Types (1-2 hours)**

Catalog all parser error types:
```bash
# Find all parser error raises
grep -r "raise.*Error" src/ir/parser.py src/ir/normalize.py

# Find exception definitions
grep -r "class.*Error" src/
```

Create catalog:
```markdown
## Parser Error Types

### Lark-Native Errors (from grammar)
1. **UnexpectedCharacters** - Token not recognized
   - Example: "No terminal matches 'm' at line 35 col 4"
   - Source: Lark parser, generated automatically
   - Location: ✅ Already includes line/column from Lark

2. **UnexpectedToken** - Wrong token in context
   - Example: "Unexpected token Token('RPAR', ')') at line 10"
   - Source: Lark parser
   - Location: ✅ Already includes line/column

### Custom Parser Errors (nlp2mcp-specific)
3. **ParserSemanticError** - Semantic validation failure
   - Example: "Assignments must use numeric constants; got Call(...)"
   - Source: `src/ir/parser.py` validation logic
   - Location: ❌ No line/column tracking
   - Fix: Extract from Lark Tree metadata before validation

4. **UnsupportedSyntaxError** - Feature not yet implemented
   - Example: "Indexed assignments not supported yet"
   - Source: Parser feature flags
   - Location: ❌ No line/column tracking
   - Fix: Extract from Lark Tree metadata

## Coverage Analysis
- Lark errors: ✅ Already have line numbers
- Custom errors: ❌ Need enhancement (X error types found)
```

**2. Design Location Extraction Pattern (1-2 hours)**

Design patterns for extracting location from Lark trees and enhancing exceptions.

**3. Identify All Error Raise Points (1 hour)**

List all `raise` statements in parser that need location extraction.

**4. Test Strategy Design (1 hour)**

Design tests for 100% line number coverage.

**5. Effort Breakdown (<1 hour)**

Validate 4-6 hour implementation estimate.

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (150+ lines)
- Parser error type catalog
- Location extraction patterns
- Exception class enhancement design
- Parser raise point inventory
- Test strategy
- Effort validation

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 4.1, 4.2, 4.3, 4.4

**Unknown 4.1: Do Lark-native errors already have line numbers?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 4 (Design Parser Error Line Number Tracking)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Lark UnexpectedCharacters: [Has/doesn't have] line numbers
  - Lark UnexpectedToken: [Has/doesn't have] line numbers
  - [Other Lark errors surveyed]
  
  **Evidence:**
  - Error type catalog shows [N] Lark-native errors
  - [Sample error messages with/without line numbers]
  
  **Decision:**
  - [If has line numbers: Only custom errors need enhancement]
  - [If doesn't have: All errors need location extraction]
  
  **Impact:**
  - Implementation scope: [X] error types need enhancement
  - 4-6 hour estimate [confirmed/needs adjustment]
  ```

**Unknown 4.2: Can we extract location from all parser error contexts?**
- Add verification results with:
  - Findings: "Location extraction pattern works for [context types]"
  - Evidence: Design patterns documented in deliverable
  - Decision: "All [N] custom error raise points can be enhanced"
  - Impact: "100% coverage achievable in Sprint 8"

**Unknown 4.3: Are there parser errors in places without Lark tree context?**
- Add verification results with:
  - Findings: "[Found/Didn't find] errors outside tree context"
  - Evidence: Raise point inventory showing context availability
  - Decision: "[All/Some] errors have tree context for location extraction"
  - Impact: "[100%/X%] coverage achievable"

**Unknown 4.4: Is 4-6 hours sufficient for implementation?**
- Add verification results with:
  - Findings: "Implementation requires [X] error types × [Y] hours each"
  - Evidence: Effort breakdown from deliverable
  - Decision: "4-6 hours [confirmed/needs adjustment to X-Y hours]"
  - Impact: "Sprint 8 effort estimate accurate"

### 4. UPDATE PREP_PLAN.md

**Task 4 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` [XXX lines]
  
  **Error Type Catalog:**
  - Surveyed [N] Lark-native errors (UnexpectedCharacters, UnexpectedToken, etc.)
  - Surveyed [M] custom errors (ParserSemanticError, UnsupportedSyntaxError, etc.)
  - Determined [X] errors already have line numbers, [Y] need enhancement
  
  **Location Extraction Design:**
  - Designed pattern for extracting location from Lark Tree metadata
  - Designed exception class enhancement pattern
  - Identified [N] raise points needing location extraction
  
  **Test Strategy:**
  - Test coverage plan for [N] error types
  - Validation approach for 100% line number coverage
  
  **Effort Validation:**
  - Confirmed 4-6 hour estimate [or adjusted to X-Y hours]
  - Breakdown: [grammar: X hours, exceptions: Y hours, tests: Z hours]
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] All parser error types cataloged (Lark-native and custom)
  - [x] Location extraction patterns designed
  - [x] Exception class enhancements designed
  - [x] All parser raise points identified
  - [x] Test strategy for 100% coverage defined
  - [x] Implementation effort validated (4-6 hours)
  - [x] Cross-referenced with Sprint 7 SourceLocation implementation
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 4 - Design Parser Error Line Number Tracking - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Designed approach to extend SourceLocation tracking from Sprint 7 convexity warnings to ALL parser errors, achieving 100% coverage. Builds on existing infrastructure for low-risk, high-impact UX improvement.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` [XXX lines]
  - Parser error type catalog ([N] Lark-native, [M] custom errors)
  - Location extraction patterns for Lark Tree metadata
  - Exception class enhancement design
  - Parser raise point inventory ([N] raise statements)
  - Test strategy for 100% coverage
  - Effort validation (4-6 hours confirmed)

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 4.1, 4.2, 4.3, 4.4)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 4 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Error Type Coverage:**
- Lark-native errors: [N] types ([Has/Doesn't have] line numbers already)
- Custom errors: [M] types (need enhancement)
- Total raise points: [X] locations needing location extraction

**Location Extraction:**
- Pattern: Extract from Lark Tree.meta before validation
- Implementation: Enhance [X] exception classes with source_location field
- Format: Reuse SourceLocation.__str__() from Sprint 7 ("file.gms:15:8")

**Test Strategy:**
- Test fixtures: [N] error types × 2-3 test cases each
- Validation: Grep all error messages for line number format
- Coverage target: 100% of parser errors include location

**Effort Breakdown:**
- Extract location from Lark trees: [X] hours
- Enhance exception classes: [Y] hours
- Update raise statements: [Z] hours
- Test fixtures: [W] hours
- Total: [4-6 hours confirmed/adjusted to X-Y hours]

#### Unknown Verification

**4.1: Do Lark-native errors already have line numbers?**
- ✅ VERIFIED: [Yes/No], [findings]
- [Impact on scope]

**4.2: Can we extract location from all parser error contexts?**
- ✅ VERIFIED: Location extraction pattern works for [all/most] contexts
- [X] error types can be enhanced

**4.3: Are there parser errors in places without Lark tree context?**
- ✅ VERIFIED: [All/Some] errors have tree context
- [100%/X%] coverage achievable

**4.4: Is 4-6 hours sufficient for implementation?**
- ✅ VERIFIED: 4-6 hours [confirmed/adjusted to X-Y hours]
- Effort breakdown validated

#### Next Steps

**Task 5:** Design Partial Parse Metrics
- Define statement-level parse success tracking
- Design dashboard integration showing "himmel16: 85% parsed"
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (Sprint 7 SourceLocation code, parser.py, normalize.py)
- ✅ Verify all deliverables are complete
- ✅ Verify all unknowns (4.1, 4.2, 4.3, 4.4) have complete verification results
- ✅ Verify all Task 4 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task4-error-line-numbers
git add -A
git commit -m "Complete Sprint 8 Prep Task 4: Design Parser Error Line Number Tracking

Designed approach to extend SourceLocation tracking to all parser errors,
building on Sprint 7 infrastructure for 100% error line number coverage.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md [XXX lines]
  - Error type catalog ([N] Lark-native, [M] custom errors)
  - Location extraction patterns
  - Exception class enhancement design
  - Raise point inventory
  - Test strategy for 100% coverage

ERROR TYPE ANALYSIS:
- Lark-native errors: [Results]
- Custom errors: [Results]
- Total raise points: [N] locations need enhancement

LOCATION EXTRACTION DESIGN:
- Pattern: Extract from Tree.meta before validation
- Reuse: Sprint 7 SourceLocation infrastructure
- Format: \"file.gms:15:8\" (consistent with warnings)

IMPLEMENTATION PLAN:
- Enhance [X] exception classes with source_location field
- Update [N] raise statements with location extraction
- Add test fixtures for [M] error types
- Effort: [4-6 hours confirmed/adjusted]

UNKNOWN VERIFICATION:
- 4.1: Lark errors [have/don't have] line numbers
- 4.2: Location extraction works for [all/most] contexts
- 4.3: [100%/X%] coverage achievable
- 4.4: 4-6 hour estimate [confirmed/adjusted]

FILES MODIFIED:
- Created: PARSER_ERROR_LINE_NUMBERS.md
- Modified: KNOWN_UNKNOWNS.md (verified 4.1, 4.2, 4.3, 4.4)
- Modified: PREP_PLAN.md (Task 4 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task4-error-line-numbers
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 4: Design Parser Error Line Number Tracking" \
  --body "Completes Task 4 of Sprint 8 prep phase.

## Deliverables
- ✅ PARSER_ERROR_LINE_NUMBERS.md with error type catalog
- ✅ Location extraction patterns designed
- ✅ Exception class enhancement design
- ✅ Raise point inventory ([N] locations)
- ✅ Test strategy for 100% coverage
- ✅ Unknowns 4.1, 4.2, 4.3, 4.4 verified

## Key Findings
- [N] Lark-native errors, [M] custom errors cataloged
- Location extraction builds on Sprint 7 SourceLocation
- [X] raise points need enhancement
- 4-6 hour effort [confirmed/adjusted]

## Unknown Verification
- 4.1: ✅ [Lark error line number status]
- 4.2: ✅ Location extraction feasible
- 4.3: ✅ [Coverage percentage] achievable
- 4.4: ✅ Effort estimate validated

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] All parser error types cataloged (Lark-native and custom)
- [x] Location extraction patterns designed
- [x] Exception class enhancements designed
- [x] All parser raise points identified
- [x] Test strategy for 100% coverage defined
- [x] Implementation effort validated (4-6 hours)
- [x] Cross-referenced with Sprint 7 SourceLocation implementation
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 4 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 5: Design Partial Parse Metrics

**On a new branch:** `prep/sprint8-task5-partial-metrics`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Design system to track and report statement-level parse success for models that partially parse. Enables dashboard to show "himmel16: 85% parsed, needs [i++1 indexing]" instead of binary "FAILED".

**Why This Matters:**
Sprint 7 retrospective: *"Consider 'partial parse' metric... Shows progress on models that partially parse."*

Binary pass/fail hides progress. Better: "himmel16 = 85% parsed (only i++1 indexing missing)".

PROJECT_PLAN.md acceptance criterion: *"Dashboard shows statement-level parse success (e.g., 'himmel16: 85% parsed')"*

### 2. WHAT TO DELIVER

**1. Define "Statement" for Parsing Metrics (1-2 hours)**
**2. Design Counting Mechanism (1-2 hours)**
**3. Design Missing Feature Extraction (1 hour)**
**4. Dashboard Integration Design (1 hour)**
**5. Ingestion Pipeline Update (<1 hour)**

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (150+ lines)
- Statement definition
- Counting mechanism design
- Missing feature extraction patterns
- Dashboard mockup
- Ingestion pipeline updates

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 6.1, 6.2, 6.3, 6.4

**Unknown 6.1: What counts as a "statement" for parsing metrics?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 5 (Design Partial Parse Metrics)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Statement definition: [Top-level AST nodes / Line-based / Section-based]
  - Granularity: [Set declarations, Parameter declarations, Equations, Solve statements, etc.]
  - Countable: [Yes/No with rationale]
  
  **Evidence:**
  - Statement definition documented in deliverable
  - Examples from GAMSLib models showing countable units
  
  **Decision:**
  - Statement = [Definition chosen]
  - Counting mechanism: [AST traversal / Line counting / Other]
  
  **Impact:**
  - Enables "85% parsed" metrics
  - Dashboard can show statement-level progress
  ```

**Unknown 6.2: Can we count statements in partially-parsed models?**
- Add verification results with:
  - Findings: "Partial parse produces AST with [N] statements before error"
  - Evidence: Counting mechanism design from deliverable
  - Decision: "[Can/Cannot] count successfully parsed statements before error point"
  - Impact: "Partial metrics [feasible/infeasible] in Sprint 8"

**Unknown 6.3: How do we extract "missing feature" from parse failures?**
- Add verification results with:
  - Findings: "Error messages contain [feature hints / no hints]"
  - Evidence: Missing feature extraction patterns from deliverable
  - Decision: "Extract from [error message patterns / error type mapping / other]"
  - Impact: "Dashboard can show 'needs [i++1 indexing]' annotations"

**Unknown 6.4: Can dashboard show partial metrics without major refactoring?**
- Add verification results with:
  - Findings: "Dashboard template requires [minor/major] changes"
  - Evidence: Dashboard integration design from deliverable
  - Decision: "Backward compatible = [Yes/No]"
  - Impact: "Sprint 8 dashboard effort = [X] hours"

### 4. UPDATE PREP_PLAN.md

**Task 5 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` [XXX lines]
  
  **Statement Definition:**
  - Defined "statement" as [chosen definition]
  - Granularity: [Set/Parameter/Equation/Solve/etc.]
  - Countable via [AST traversal / other mechanism]
  
  **Counting Mechanism:**
  - Designed [mechanism description]
  - Works for partial parses: [Yes/No with details]
  - Implementation complexity: [Low/Medium/High]
  
  **Missing Feature Extraction:**
  - Pattern: Extract from [error messages / error types]
  - Example: "himmel16.gms needs [i++1 indexing]"
  - Coverage: [Can identify X% of missing features]
  
  **Dashboard Integration:**
  - Template changes: [Description]
  - Backward compatible: [Yes/No]
  - Effort estimate: [X] hours
  
  **Ingestion Pipeline:**
  - Updates needed: [Description]
  - Effort estimate: [Y] hours
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] "Statement" defined for parse metrics
  - [x] Counting mechanism designed for partial parses
  - [x] Missing feature extraction patterns designed
  - [x] Dashboard mockup created with partial metrics
  - [x] Ingestion pipeline updates documented
  - [x] Backward compatibility validated
  - [x] Implementation effort estimated (4-6 hours total)
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 5 - Design Partial Parse Metrics - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Designed system to track and report statement-level parse success for models that partially parse. Enables dashboard to show "himmel16: 85% parsed, needs [i++1 indexing]" instead of binary FAILED status.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` [XXX lines]
  - Statement definition for parse metrics ([chosen definition])
  - Counting mechanism design (works for partial parses)
  - Missing feature extraction patterns
  - Dashboard mockup with partial metrics
  - Ingestion pipeline update design

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 6.1, 6.2, 6.3, 6.4)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 5 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Statement Definition:**
- Statement = [Chosen definition: top-level AST nodes / line-based / etc.]
- Granularity: [Set, Parameter, Equation, Solve, etc.]
- Countable via: [AST traversal / other mechanism]

**Counting Mechanism:**
- Design: [Mechanism description]
- Partial parse support: [Yes - counts statements before error / No - needs workaround]
- Example: himmel16.gms = [X] statements parsed, [Y] statements total = 85%

**Missing Feature Extraction:**
- Pattern: Extract from [error message text / error type mapping]
- Example annotations:
  - "himmel16.gms: needs [i++1 indexing]"
  - "circle.gms: needs [function calls]"
- Coverage: [Can identify X% of missing features from error patterns]

**Dashboard Integration:**
- Template changes: [Minor/Major] modifications to GAMSLIB_CONVERSION_STATUS.md
- New format: "Model | Status | Parse % | Missing Features"
- Backward compatible: [Yes/No]
- Color coding: ✅ 100% | 🟡 75-99% | ⚠️ 25-74% | ❌ <25%

**Implementation Effort:**
- Counting mechanism: [X] hours
- Missing feature extraction: [Y] hours
- Dashboard updates: [Z] hours
- Ingestion pipeline: [W] hours
- Total: [4-6 hours estimated]

#### Unknown Verification

**6.1: What counts as a "statement" for parsing metrics?**
- ✅ VERIFIED: Statement = [chosen definition]
- Countable via [mechanism]

**6.2: Can we count statements in partially-parsed models?**
- ✅ VERIFIED: [Yes/No], [counting approach]
- Partial metrics [feasible/require workaround]

**6.3: How do we extract "missing feature" from parse failures?**
- ✅ VERIFIED: Extract from [error messages/types]
- Coverage: [X%] of failures can be annotated

**6.4: Can dashboard show partial metrics without major refactoring?**
- ✅ VERIFIED: [Minor/Major] changes needed
- Backward compatible: [Yes/No]

#### Next Steps

**Task 6:** Research Error Message Enhancement Patterns
- Survey error message best practices from mature parsers
- Design "did you mean?" suggestions for GAMS parser
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (Sprint 7 retrospective, dashboard files)
- ✅ Verify all deliverables are complete
- ✅ Verify all unknowns (6.1, 6.2, 6.3, 6.4) have complete verification results
- ✅ Verify all Task 5 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task5-partial-metrics
git add -A
git commit -m "Complete Sprint 8 Prep Task 5: Design Partial Parse Metrics

Designed system to track statement-level parse success, enabling dashboard
to show partial parse percentages instead of binary pass/fail.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md [XXX lines]
  - Statement definition: [chosen definition]
  - Counting mechanism design
  - Missing feature extraction patterns
  - Dashboard mockup
  - Ingestion pipeline updates

STATEMENT DEFINITION:
- Statement = [chosen definition]
- Granularity: [Set/Parameter/Equation/Solve]
- Countable via: [AST traversal/other]

COUNTING MECHANISM:
- Design: [description]
- Partial parse support: [Yes/No]
- Example: himmel16.gms = 85% parsed

MISSING FEATURE EXTRACTION:
- Pattern: Extract from [error messages/types]
- Example: \"needs [i++1 indexing]\"
- Coverage: [X%] of failures annotatable

DASHBOARD INTEGRATION:
- New format: Status | Parse % | Missing Features
- Color coding: ✅ 🟡 ⚠️ ❌ based on percentage
- Backward compatible: [Yes/No]

IMPLEMENTATION EFFORT:
- Counting: [X] hours
- Feature extraction: [Y] hours
- Dashboard: [Z] hours
- Total: [4-6 hours]

UNKNOWN VERIFICATION:
- 6.1: Statement = [definition]
- 6.2: Partial counting [feasible/infeasible]
- 6.3: Missing feature extraction [approach]
- 6.4: Dashboard changes [minor/major]

FILES MODIFIED:
- Created: PARTIAL_PARSE_METRICS.md
- Modified: KNOWN_UNKNOWNS.md (verified 6.1, 6.2, 6.3, 6.4)
- Modified: PREP_PLAN.md (Task 5 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task5-partial-metrics
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 5: Design Partial Parse Metrics" \
  --body "Completes Task 5 of Sprint 8 prep phase.

## Deliverables
- ✅ PARTIAL_PARSE_METRICS.md with statement definition
- ✅ Counting mechanism for partial parses
- ✅ Missing feature extraction patterns
- ✅ Dashboard mockup with parse percentages
- ✅ Ingestion pipeline design
- ✅ Unknowns 6.1, 6.2, 6.3, 6.4 verified

## Key Findings
- Statement = [definition chosen]
- Counting mechanism: [description]
- Example: \"himmel16: 85% parsed, needs [i++1 indexing]\"
- Dashboard shows partial progress (not binary pass/fail)

## Unknown Verification
- 6.1: ✅ Statement definition validated
- 6.2: ✅ Partial counting [feasible/infeasible]
- 6.3: ✅ Feature extraction [approach]
- 6.4: ✅ Dashboard [backward compatible/needs updates]

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] "Statement" defined for parse metrics
- [x] Counting mechanism designed for partial parses
- [x] Missing feature extraction patterns designed
- [x] Dashboard mockup created with partial metrics
- [x] Ingestion pipeline updates documented
- [x] Backward compatibility validated
- [x] Implementation effort estimated (4-6 hours total)
- [x] Unknowns 6.1, 6.2, 6.3, 6.4 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 5 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 6: Research Error Message Enhancement Patterns

**On a new branch:** `prep/sprint8-task6-error-messages`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Research error message enhancement patterns from mature parsers (Rust, Python, TypeScript) to design actionable, helpful error messages for GAMS parser.

**Why This Matters:**
Current error messages are cryptic. Better messages with "did you mean?" suggestions improve UX.

PROJECT_PLAN.md: *"Improved Error Messages... add 'did you mean?' hints (Effort: 3-5 hours)"*

### 2. WHAT TO DELIVER

**1. Survey Error Message Best Practices (1-2 hours)**
**2. Categorize GAMS Parser Errors (1 hour)**
**3. Design Enhancement Framework (1 hour)**
**4. Test Strategy (<1 hour)**

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (120+ lines)
- Error message pattern catalog (5+ patterns)
- GAMS error categorization
- Enhancement framework design
- Enhancement rules (10+ patterns)
- Test strategy

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 5.1, 5.2, 5.3, 5.4

**Unknown 5.1: What error message patterns are most effective?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 6 (Research Error Message Enhancement Patterns)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Best practices surveyed from [Rust/Python/TypeScript/etc.]
  - Effective patterns: [List 5+ patterns with examples]
  - "Did you mean?" effectiveness: [High/Medium/Low]
  
  **Evidence:**
  - Pattern catalog with examples from mature parsers
  - Applicability analysis for GAMS parser
  
  **Decision:**
  - Adopt patterns: [List chosen patterns]
  - GAMS-specific adaptations: [Description]
  
  **Impact:**
  - Sprint 8 error messages will include [pattern types]
  - UX improvement measurable via [metric]
  ```

**Unknown 5.2: Can we categorize GAMS parser errors systematically?**
- Add verification results with:
  - Findings: "GAMS errors fall into [N] categories"
  - Evidence: Error categorization from deliverable
  - Decision: "Categories: [List categories]"
  - Impact: "Each category gets tailored enhancement rules"

**Unknown 5.3: How much effort for each enhancement type?**
- Add verification results with:
  - Findings: "Pattern X = [Y] hours, Pattern Z = [W] hours"
  - Evidence: Effort breakdown from deliverable
  - Decision: "Total effort = [3-5 hours confirmed/adjusted]"
  - Impact: "Sprint 8 can implement [N] patterns"

**Unknown 5.4: Are "did you mean?" suggestions feasible for GAMS syntax?**
- Add verification results with:
  - Findings: "GAMS has [definable/undefined] suggestion space"
  - Evidence: Enhancement framework from deliverable
  - Decision: "[Can/Cannot] implement suggestions for [error types]"
  - Impact: "Sprint 8 includes suggestions for [X%] of errors"

### 4. UPDATE PREP_PLAN.md

**Task 6 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` [XXX lines]
  
  **Error Message Pattern Catalog:**
  - Surveyed best practices from [Rust/Python/TypeScript/etc.]
  - Documented [5+] effective patterns with examples
  - Analyzed applicability to GAMS parser
  
  **GAMS Error Categorization:**
  - Identified [N] error categories
  - Examples: [Syntax errors, Semantic errors, Unsupported features, etc.]
  - Each category mapped to enhancement rules
  
  **Enhancement Framework:**
  - Designed framework for applying patterns to GAMS errors
  - "Did you mean?" rules: [N] rules defined
  - Context-aware suggestions: [Description]
  
  **Test Strategy:**
  - Test approach for validating enhancements
  - Coverage: [X%] of error types can be enhanced
  
  **Effort Validation:**
  - Confirmed 3-5 hour estimate [or adjusted to X-Y hours]
  - Breakdown: [pattern implementation: X hours, testing: Y hours]
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] Error message pattern catalog created (5+ patterns)
  - [x] GAMS parser errors categorized systematically
  - [x] Enhancement framework designed
  - [x] Enhancement rules documented (10+ patterns)
  - [x] Test strategy defined
  - [x] Implementation effort validated (3-5 hours)
  - [x] "Did you mean?" feasibility determined
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 6 - Research Error Message Enhancement Patterns - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Researched error message enhancement patterns from mature parsers (Rust, Python, TypeScript) to design actionable, helpful error messages for GAMS parser. Identified patterns, categorized GAMS errors, and designed enhancement framework.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` [XXX lines]
  - Error message pattern catalog ([N] patterns from mature parsers)
  - GAMS error categorization ([M] categories)
  - Enhancement framework design
  - Enhancement rules (10+ patterns for GAMS)
  - Test strategy

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 5.1, 5.2, 5.3, 5.4)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 6 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Error Message Patterns (from mature parsers):**
1. **Pattern 1:** [Name and description]
   - Example: [From Rust/Python/TypeScript]
   - GAMS applicability: [High/Medium/Low]
2. **Pattern 2:** [Name and description]
   - Example: [From Rust/Python/TypeScript]
   - GAMS applicability: [High/Medium/Low]
3. [Additional patterns...]

**GAMS Error Categorization:**
- Category 1: [Name] ([N] error types)
  - Enhancement approach: [Description]
- Category 2: [Name] ([M] error types)
  - Enhancement approach: [Description]
- [Additional categories...]

**Enhancement Framework:**
- Design: [Framework description]
- "Did you mean?" suggestions: [Feasible for X error types]
- Context-aware hints: [Pattern description]
- Example enhancement:
  - Before: "No terminal matches 'l' at line 37"
  - After: "Unrecognized keyword 'limcol' at line 37. Did you mean 'option limcol = ...'?"

**Enhancement Rules:**
1. **Rule 1:** [Description]
   - Applies to: [Error types]
   - Implementation: [Pattern]
2. **Rule 2:** [Description]
   - Applies to: [Error types]
   - Implementation: [Pattern]
3. [Additional rules... total 10+]

**Implementation Effort:**
- Pattern implementation: [X] hours
- Testing: [Y] hours
- Total: [3-5 hours confirmed/adjusted]

#### Unknown Verification

**5.1: What error message patterns are most effective?**
- ✅ VERIFIED: Patterns [list] most effective
- Adopted for GAMS: [patterns chosen]

**5.2: Can we categorize GAMS parser errors systematically?**
- ✅ VERIFIED: [N] categories identified
- Each category has tailored enhancement approach

**5.3: How much effort for each enhancement type?**
- ✅ VERIFIED: [Pattern X] = [Y] hours, [Pattern Z] = [W] hours
- Total: 3-5 hours [confirmed/adjusted]

**5.4: Are "did you mean?" suggestions feasible for GAMS syntax?**
- ✅ VERIFIED: Feasible for [X%] of error types
- Sprint 8 will implement suggestions for [categories]

#### Next Steps

**Task 7:** Survey High-ROI Parser Features
- Deep dive on [indexed assignments OR function calls]
- Validate implementation effort and design grammar
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (mature parser documentation, GAMS error examples)
- ✅ Verify all deliverables are complete
- ✅ Verify all unknowns (5.1, 5.2, 5.3, 5.4) have complete verification results
- ✅ Verify all Task 6 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task6-error-messages
git add -A
git commit -m "Complete Sprint 8 Prep Task 6: Research Error Message Enhancement Patterns

Researched error message patterns from mature parsers and designed
enhancement framework for GAMS parser to improve UX.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md [XXX lines]
  - Pattern catalog ([N] patterns from Rust/Python/TypeScript)
  - GAMS error categorization ([M] categories)
  - Enhancement framework
  - Enhancement rules (10+ patterns)
  - Test strategy

ERROR MESSAGE PATTERNS:
- Pattern 1: [name and description]
- Pattern 2: [name and description]
- [Additional patterns...]
- Total: [N] patterns surveyed

GAMS ERROR CATEGORIZATION:
- Category 1: [name] ([X] error types)
- Category 2: [name] ([Y] error types)
- [Additional categories...]
- Total: [M] categories

ENHANCEMENT FRAMEWORK:
- \"Did you mean?\" suggestions: Feasible for [X%] errors
- Context-aware hints: [Pattern description]
- Example: \"Unrecognized keyword 'limcol'. Did you mean 'option limcol = ...'?\"

ENHANCEMENT RULES:
- Rule 1: [description]
- Rule 2: [description]
- [Additional rules...]
- Total: 10+ rules defined

IMPLEMENTATION EFFORT:
- Pattern implementation: [X] hours
- Testing: [Y] hours
- Total: 3-5 hours [confirmed/adjusted]

UNKNOWN VERIFICATION:
- 5.1: Patterns [list] most effective
- 5.2: [N] error categories identified
- 5.3: 3-5 hour estimate [confirmed/adjusted]
- 5.4: \"Did you mean?\" feasible for [X%] errors

FILES MODIFIED:
- Created: ERROR_MESSAGE_ENHANCEMENTS.md
- Modified: KNOWN_UNKNOWNS.md (verified 5.1, 5.2, 5.3, 5.4)
- Modified: PREP_PLAN.md (Task 6 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task6-error-messages
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 6: Research Error Message Enhancement Patterns" \
  --body "Completes Task 6 of Sprint 8 prep phase.

## Deliverables
- ✅ ERROR_MESSAGE_ENHANCEMENTS.md with pattern catalog
- ✅ GAMS error categorization ([M] categories)
- ✅ Enhancement framework design
- ✅ Enhancement rules (10+ patterns)
- ✅ Test strategy
- ✅ Unknowns 5.1, 5.2, 5.3, 5.4 verified

## Key Findings
- [N] error message patterns from mature parsers
- [M] GAMS error categories identified
- \"Did you mean?\" feasible for [X%] of errors
- 3-5 hour implementation effort [confirmed/adjusted]

## Unknown Verification
- 5.1: ✅ Patterns [list] most effective
- 5.2: ✅ [N] categories identified
- 5.3: ✅ Effort validated
- 5.4: ✅ Suggestions feasible

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] Error message pattern catalog created (5+ patterns)
- [x] GAMS parser errors categorized systematically
- [x] Enhancement framework designed
- [x] Enhancement rules documented (10+ patterns)
- [x] Test strategy defined
- [x] Implementation effort validated (3-5 hours)
- [x] "Did you mean?" feasibility determined
- [x] Unknowns 5.1, 5.2, 5.3, 5.4 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 6 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 7: Survey High-ROI Parser Features

**On a new branch:** `prep/sprint8-task7-high-roi-feature`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Deep research on the second Sprint 8 feature (indexed assignments OR function calls based on Task 2 analysis). Validate effort estimate, identify risks, design implementation.

**Why This Matters:**
Sprint 8 success (25% parse rate) depends on choosing the right feature. Task 2 determines which; Task 7 designs implementation.

PROJECT_PLAN.md: *"One Additional High-ROI Feature... Either indexed assignments OR function calls... Effort: 6-8 hours, Risk: Medium"*

### 2. WHAT TO DELIVER

**1. Review Task 2 Feature Recommendation (1 hour)**
**2A. Indexed Assignments Deep Dive (4-6 hours if selected)**
  - GAMS syntax survey
  - Grammar design
  - Implementation plan
  - Test fixture design
**2B. Function Calls Deep Dive (4-6 hours if selected)**
  - GAMS function survey
  - Grammar design
  - Implementation plan
  - Test fixture design
**3. Risk Assessment (1 hour)**

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/[INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md` (200+ lines)
- GAMS syntax survey
- Grammar design
- Implementation plan (6-8 hour breakdown)
- Test fixtures (4-5 cases)
- Risk assessment

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 3.1, 3.2, 3.3

**Unknown 3.1: Is indexed assignments OR function calls the right choice?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 7 (Survey High-ROI Parser Features)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Task 2 recommended: [Indexed assignments / Function calls]
  - Rationale: [Higher unlock rate / Fewer dependencies / etc.]
  - Deep dive confirms: [Chosen feature is appropriate]
  
  **Evidence:**
  - GAMS syntax survey shows [complexity level]
  - Grammar design is [straightforward / complex]
  - Implementation plan validates 6-8 hour estimate
  
  **Decision:**
  - Sprint 8 feature: [Indexed assignments / Function calls]
  - Rationale: [Detailed reasoning from deep dive]
  
  **Impact:**
  - Unlocks [N] models: [list models]
  - Parse rate increase: +[X]%
  - Combined with options: [25-30%] total parse rate
  ```

**Unknown 3.2: Are there hidden complexities in [chosen feature]?**
- Add verification results with:
  - Findings: "[Hidden complexity found / No hidden complexity]"
  - Evidence: Deep dive research from deliverable
  - Decision: "6-8 hour estimate [confirmed / needs adjustment to X-Y hours]"
  - Impact: "Sprint 8 plan [unchanged / needs revision]"

**Unknown 3.3: What test fixtures are needed for [chosen feature]?**
- Add verification results with:
  - Findings: "[N] test fixtures identified"
  - Evidence: Test fixture design from deliverable
  - Decision: "Fixtures cover [basic / intermediate / advanced] cases"
  - Impact: "Sprint 8 testing effort = [X] hours"

### 4. UPDATE PREP_PLAN.md

**Task 7 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/[INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md` [XXX lines]
  
  **Feature Selection:**
  - Reviewed Task 2 recommendation: [Indexed assignments / Function calls]
  - Confirmed choice based on [unlock rate / dependencies / ROI]
  
  **GAMS Syntax Survey:**
  - Documented [N] syntax patterns for [chosen feature]
  - Complexity assessment: [Low / Medium / High]
  - Examples from GAMSLib models: [list models using feature]
  
  **Grammar Design:**
  - Lark grammar rules designed for [chosen feature]
  - Integration points identified in existing grammar
  - Estimated grammar changes: [X] lines
  
  **Implementation Plan:**
  - Grammar changes: [X] hours
  - AST node creation: [Y] hours
  - Semantic handling: [Z] hours
  - Test fixtures: [W] hours
  - Total: 6-8 hours [confirmed / adjusted to A-B hours]
  
  **Test Fixture Design:**
  - Designed [N] test fixtures covering [basic / edge cases]
  - Examples: [list fixture types]
  
  **Risk Assessment:**
  - Risks identified: [list risks]
  - Mitigation strategies: [list mitigations]
  - Overall risk: [Low / Medium / High]
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] Task 2 feature recommendation reviewed
  - [x] GAMS syntax survey completed for [chosen feature]
  - [x] Lark grammar designed
  - [x] Implementation plan created (6-8 hour breakdown)
  - [x] Test fixtures designed (4-5 cases)
  - [x] Risk assessment completed
  - [x] Effort estimate validated
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 7 - Survey High-ROI Parser Features - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Deep research on [indexed assignments / function calls] based on Task 2 recommendation. Validated effort estimate, designed grammar, and created implementation plan for Sprint 8's second high-ROI feature.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/[INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md` [XXX lines]
  - GAMS syntax survey for [chosen feature]
  - Lark grammar design
  - Implementation plan with 6-8 hour breakdown
  - Test fixture design (4-5 cases)
  - Risk assessment

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 3.1, 3.2, 3.3)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 7 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Feature Selection:**
- Task 2 recommended: [Indexed assignments / Function calls]
- Rationale: [Unlocks X models / Higher ROI / Fewer dependencies]
- Deep dive confirms: Appropriate choice for Sprint 8

**GAMS Syntax Patterns:**
1. **Pattern 1:** [Description]
   - Example: [GAMS code example]
   - GAMSLib usage: [models using this pattern]
2. **Pattern 2:** [Description]
   - Example: [GAMS code example]
   - GAMSLib usage: [models using this pattern]
3. [Additional patterns...]

**Grammar Design:**
```lark
[Grammar rules for chosen feature]
```
- Integration: [Where in existing grammar]
- Complexity: [Low / Medium / High]
- Estimated changes: [X] lines

**Implementation Plan:**
- Grammar changes: [X] hours
  - Add [grammar rule descriptions]
- AST node creation: [Y] hours
  - Create [AST node types]
- Semantic handling: [Z] hours
  - [Validation / Processing requirements]
- Test fixtures: [W] hours
  - [Number] fixtures covering [cases]
- Total: 6-8 hours [confirmed / adjusted to A-B hours]

**Test Fixtures:**
1. **Fixture 1:** [Name and description]
   - Tests: [What it tests]
2. **Fixture 2:** [Name and description]
   - Tests: [What it tests]
3. [Additional fixtures... total 4-5]

**Risk Assessment:**
- Risk 1: [Description]
  - Mitigation: [Strategy]
  - Likelihood: [Low / Medium / High]
- Risk 2: [Description]
  - Mitigation: [Strategy]
  - Likelihood: [Low / Medium / High]
- Overall risk: [Low / Medium / High]

**Models Unlocked:**
- [Model 1]: [How this feature unlocks it]
- [Model 2]: [How this feature unlocks it]
- Total unlock rate: +[X]% (combined with options: [25-30%])

#### Unknown Verification

**3.1: Is indexed assignments OR function calls the right choice?**
- ✅ VERIFIED: [Chosen feature] confirmed
- Rationale: [Unlock rate / ROI / Dependencies]

**3.2: Are there hidden complexities in [chosen feature]?**
- ✅ VERIFIED: [Hidden complexity found / None found]
- Effort: 6-8 hours [confirmed / adjusted to X-Y hours]

**3.3: What test fixtures are needed for [chosen feature]?**
- ✅ VERIFIED: [N] fixtures identified
- Coverage: [Basic / Intermediate / Advanced] cases

#### Next Steps

**Task 8:** Create Parser Test Fixture Strategy
- Define comprehensive test fixture strategy for Sprint 8
- Include option statements + [chosen feature] + partial metrics
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (Task 2 GAMSLIB_FEATURE_MATRIX.md, GAMS documentation)
- ✅ Verify all deliverables are complete
- ✅ Verify all unknowns (3.1, 3.2, 3.3) have complete verification results
- ✅ Verify all Task 7 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task7-high-roi-feature
git add -A
git commit -m "Complete Sprint 8 Prep Task 7: Survey High-ROI Parser Features

Deep research on [indexed assignments / function calls] validates Sprint 8
feature selection and provides detailed implementation plan.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/[INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md [XXX lines]
  - GAMS syntax survey
  - Lark grammar design
  - Implementation plan (6-8 hour breakdown)
  - Test fixture design (4-5 cases)
  - Risk assessment

FEATURE SELECTION:
- Task 2 recommended: [Chosen feature]
- Rationale: [Unlock rate / ROI details]
- Deep dive confirms: Appropriate for Sprint 8

GAMS SYNTAX PATTERNS:
- Pattern 1: [description]
- Pattern 2: [description]
- [Additional patterns...]
- Total: [N] patterns documented

GRAMMAR DESIGN:
- Grammar rules: [description]
- Integration: [where in existing grammar]
- Complexity: [Low/Medium/High]
- Estimated changes: [X] lines

IMPLEMENTATION PLAN:
- Grammar: [X] hours
- AST nodes: [Y] hours
- Semantics: [Z] hours
- Testing: [W] hours
- Total: 6-8 hours [confirmed/adjusted]

TEST FIXTURES:
- Fixture 1: [description]
- Fixture 2: [description]
- [Additional fixtures...]
- Total: 4-5 fixtures

RISK ASSESSMENT:
- Risk 1: [description] - Mitigation: [strategy]
- Risk 2: [description] - Mitigation: [strategy]
- Overall: [Low/Medium/High] risk

MODELS UNLOCKED:
- [Model 1, Model 2, ...]
- Unlock rate: +[X]%
- Combined with options: [25-30%] parse rate

UNKNOWN VERIFICATION:
- 3.1: [Chosen feature] confirmed
- 3.2: Hidden complexity [found/not found]
- 3.3: [N] fixtures identified

FILES MODIFIED:
- Created: [INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md
- Modified: KNOWN_UNKNOWNS.md (verified 3.1, 3.2, 3.3)
- Modified: PREP_PLAN.md (Task 7 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task7-high-roi-feature
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 7: Survey High-ROI Parser Features" \
  --body "Completes Task 7 of Sprint 8 prep phase.

## Deliverables
- ✅ [INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md with syntax survey
- ✅ Lark grammar design
- ✅ Implementation plan (6-8 hour breakdown)
- ✅ Test fixture design (4-5 cases)
- ✅ Risk assessment
- ✅ Unknowns 3.1, 3.2, 3.3 verified

## Key Findings
- Feature: [Indexed assignments / Function calls]
- Unlocks: [N] models ([list models])
- Parse rate: +[X]% (combined: [25-30%])
- Effort: 6-8 hours [confirmed/adjusted]
- Risk: [Low/Medium/High]

## Unknown Verification
- 3.1: ✅ [Chosen feature] confirmed
- 3.2: ✅ Effort validated
- 3.3: ✅ [N] fixtures identified

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] Task 2 feature recommendation reviewed
- [x] GAMS syntax survey completed for [chosen feature]
- [x] Lark grammar designed
- [x] Implementation plan created (6-8 hour breakdown)
- [x] Test fixtures designed (4-5 cases)
- [x] Risk assessment completed
- [x] Effort estimate validated
- [x] Unknowns 3.1, 3.2, 3.3 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 7 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 8: Create Parser Test Fixture Strategy

**On a new branch:** `prep/sprint8-task8-test-fixtures`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Define comprehensive test fixture strategy for Sprint 8 parser features (option statements, indexed assignments OR function calls, partial parse metrics). Follow Sprint 7 pattern (34 fixtures).

**Why This Matters:**
Sprint 7 delivered 34 fixtures with comprehensive documentation. Sprint 8 needs similar strategy.

PROJECT_PLAN.md: *"All existing tests pass, new features have comprehensive test coverage."*

### 2. WHAT TO DELIVER

**1. Option Statement Fixtures (1 hour)**
**2. High-ROI Feature Fixtures (1-1.5 hours)**
**3. Partial Parse Metric Fixtures (<1 hour)**
**4. expected_results.yaml Design (30 min)**
**5. README.md Templates (30 min)**

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (150+ lines)
- Option fixtures (5 fixtures)
- High-ROI feature fixtures (5 fixtures)
- Partial parse fixtures (3 fixtures)
- expected_results.yaml structure
- README templates
- Total: 13+ fixtures planned

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 7.1, 7.2, 7.3

**Unknown 7.1: How many fixtures are needed for comprehensive coverage?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 8 (Create Parser Test Fixture Strategy)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Option statements: [N] fixtures identified
  - [Indexed assignments / Function calls]: [M] fixtures identified
  - Partial parse metrics: [P] fixtures identified
  - Total: [N+M+P] fixtures for Sprint 8
  
  **Evidence:**
  - Test fixture strategy documents all cases
  - Each fixture has clear purpose and expected results
  
  **Decision:**
  - Sprint 8 will create [total] fixtures
  - Coverage: [Basic / Intermediate / Advanced] cases
  
  **Impact:**
  - Testing effort = [X] hours
  - Sprint 8 plan includes fixture creation time
  ```

**Unknown 7.2: Can we reuse Sprint 7 fixture patterns?**
- Add verification results with:
  - Findings: "Sprint 7 patterns [are/are not] reusable"
  - Evidence: Comparison with Sprint 7 TEST_FIXTURE_STRATEGY.md
  - Decision: "Reuse [README structure / expected_results.yaml format / directory organization]"
  - Impact: "Fixture creation time reduced by [X] hours"

**Unknown 7.3: What is the expected_results.yaml structure for new features?**
- Add verification results with:
  - Findings: "YAML structure needs [fields] for new features"
  - Evidence: expected_results.yaml design from deliverable
  - Decision: "Add fields: [list new fields]"
  - Impact: "Ingestion script needs [minor/major] updates"

### 4. UPDATE PREP_PLAN.md

**Task 8 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` [XXX lines]
  
  **Option Statement Fixtures:**
  - Designed [N] fixtures for option statements
  - Examples: [Single option, Multi-option, Boolean options, etc.]
  - Coverage: [Basic / Edge cases]
  
  **High-ROI Feature Fixtures:**
  - Designed [M] fixtures for [indexed assignments / function calls]
  - Examples: [list fixture types]
  - Coverage: [Basic / Intermediate / Advanced]
  
  **Partial Parse Metric Fixtures:**
  - Designed [P] fixtures for partial parse testing
  - Examples: [Models that partially parse with known errors]
  - Purpose: Validate statement counting and missing feature extraction
  
  **expected_results.yaml Structure:**
  - Defined YAML format for new features
  - Added fields: [list new fields for options, chosen feature, partial metrics]
  - Backward compatible with Sprint 7 fixtures
  
  **README Templates:**
  - Created README template for option fixtures
  - Created README template for [chosen feature] fixtures
  - Created README template for partial parse fixtures
  - Follows Sprint 7 pattern
  
  **Total Fixtures:**
  - Option statements: [N] fixtures
  - [Chosen feature]: [M] fixtures
  - Partial metrics: [P] fixtures
  - Total: [N+M+P] = 13+ fixtures planned
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] Option statement fixtures designed (5 fixtures)
  - [x] High-ROI feature fixtures designed (5 fixtures)
  - [x] Partial parse metric fixtures designed (3 fixtures)
  - [x] expected_results.yaml structure defined
  - [x] README templates created
  - [x] Total 13+ fixtures planned
  - [x] Sprint 7 fixture patterns reused
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 8 - Create Parser Test Fixture Strategy - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Defined comprehensive test fixture strategy for Sprint 8 parser features (option statements, [indexed assignments / function calls], partial parse metrics). Designed 13+ fixtures following Sprint 7 patterns.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` [XXX lines]
  - Option statement fixtures (5 fixtures)
  - [Indexed assignments / Function calls] fixtures (5 fixtures)
  - Partial parse metric fixtures (3 fixtures)
  - expected_results.yaml structure
  - README templates
  - Total: 13+ fixtures planned

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 7.1, 7.2, 7.3)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 8 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Option Statement Fixtures (5 fixtures):**
1. **Fixture 1:** [Name]
   - Tests: [What it tests]
   - Example: [GAMS code snippet]
2. **Fixture 2:** [Name]
   - Tests: [What it tests]
   - Example: [GAMS code snippet]
3. [Additional fixtures...]

**[Indexed Assignments / Function Calls] Fixtures (5 fixtures):**
1. **Fixture 1:** [Name]
   - Tests: [What it tests]
   - Example: [GAMS code snippet]
2. **Fixture 2:** [Name]
   - Tests: [What it tests]
   - Example: [GAMS code snippet]
3. [Additional fixtures...]

**Partial Parse Metric Fixtures (3 fixtures):**
1. **Fixture 1:** [Name]
   - Tests: [Statement counting / Missing feature extraction]
   - Example: [Model with known partial parse]
2. **Fixture 2:** [Name]
   - Tests: [What it tests]
   - Example: [GAMS code snippet]
3. [Additional fixtures...]

**expected_results.yaml Structure:**
```yaml
# New fields for Sprint 8 features
parse_success: true/false
parse_percentage: 85  # For partial metrics
missing_features:
  - "i++1 indexing"
  - "model sections"
option_statements:
  - name: "limrow"
    value: 0
[chosen_feature]:
  [structure specific to feature]
```
- Backward compatible: Yes
- Ingestion updates needed: [Minor/Major]

**README Templates:**
- Template 1: Option statement fixtures
  - Sections: [Purpose, Syntax, Expected Behavior, Test Cases]
- Template 2: [Chosen feature] fixtures
  - Sections: [Purpose, Syntax, Expected Behavior, Test Cases]
- Template 3: Partial parse fixtures
  - Sections: [Purpose, Metrics, Expected Results]
- Pattern: Follows Sprint 7 fixture documentation style

**Coverage Analysis:**
- Option statements: [Basic / Edge] cases covered
- [Chosen feature]: [Basic / Intermediate / Advanced] cases covered
- Partial metrics: [Statement counting / Feature extraction] tested
- Total coverage: [X%] of feature space

**Effort Estimate:**
- Fixture creation: [X] hours ([N+M+P] fixtures × [Y] hours each)
- expected_results.yaml updates: [Z] hours
- README documentation: [W] hours
- Total: [Total] hours for fixture work

#### Unknown Verification

**7.1: How many fixtures are needed for comprehensive coverage?**
- ✅ VERIFIED: 13+ fixtures identified
- Breakdown: [N] option + [M] feature + [P] partial = [total]

**7.2: Can we reuse Sprint 7 fixture patterns?**
- ✅ VERIFIED: Sprint 7 patterns fully reusable
- Reusing: README structure, YAML format, directory organization

**7.3: What is the expected_results.yaml structure for new features?**
- ✅ VERIFIED: YAML structure defined
- New fields: [list fields]
- Backward compatible: Yes

#### Next Steps

**Task 9:** Design Dashboard Enhancements
- Design dashboard to display partial parse metrics
- Create mockup showing "himmel16: 85% parsed, needs [i++1 indexing]"
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (Sprint 7 TEST_FIXTURE_STRATEGY.md, existing fixtures)
- ✅ Verify all deliverables are complete
- ✅ Verify all unknowns (7.1, 7.2, 7.3) have complete verification results
- ✅ Verify all Task 8 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task8-test-fixtures
git add -A
git commit -m "Complete Sprint 8 Prep Task 8: Create Parser Test Fixture Strategy

Defined comprehensive test fixture strategy for Sprint 8 features,
following Sprint 7 patterns with 13+ fixtures planned.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md [XXX lines]
  - Option fixtures (5)
  - [Chosen feature] fixtures (5)
  - Partial parse fixtures (3)
  - expected_results.yaml structure
  - README templates
  - Total: 13+ fixtures

OPTION STATEMENT FIXTURES (5):
- Fixture 1: [name and description]
- Fixture 2: [name and description]
- [Additional fixtures...]

[CHOSEN FEATURE] FIXTURES (5):
- Fixture 1: [name and description]
- Fixture 2: [name and description]
- [Additional fixtures...]

PARTIAL PARSE FIXTURES (3):
- Fixture 1: [name and description]
- Fixture 2: [name and description]
- Fixture 3: [name and description]

EXPECTED_RESULTS.YAML:
- New fields: [list fields]
- Backward compatible: Yes
- Supports: Options, [chosen feature], partial metrics

README TEMPLATES:
- Template 1: Option fixtures
- Template 2: [Chosen feature] fixtures
- Template 3: Partial parse fixtures
- Pattern: Sprint 7 style

COVERAGE:
- Option statements: [Basic/Edge] cases
- [Chosen feature]: [Basic/Intermediate/Advanced] cases
- Partial metrics: Statement counting + feature extraction
- Total: [X%] feature coverage

EFFORT ESTIMATE:
- Fixture creation: [X] hours
- YAML updates: [Y] hours
- Documentation: [Z] hours
- Total: [Total] hours

UNKNOWN VERIFICATION:
- 7.1: 13+ fixtures identified
- 7.2: Sprint 7 patterns fully reusable
- 7.3: YAML structure defined

FILES MODIFIED:
- Created: TEST_FIXTURE_STRATEGY.md
- Modified: KNOWN_UNKNOWNS.md (verified 7.1, 7.2, 7.3)
- Modified: PREP_PLAN.md (Task 8 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task8-test-fixtures
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 8: Create Parser Test Fixture Strategy" \
  --body "Completes Task 8 of Sprint 8 prep phase.

## Deliverables
- ✅ TEST_FIXTURE_STRATEGY.md with 13+ fixtures
- ✅ Option fixtures (5)
- ✅ [Chosen feature] fixtures (5)
- ✅ Partial parse fixtures (3)
- ✅ expected_results.yaml structure
- ✅ README templates
- ✅ Unknowns 7.1, 7.2, 7.3 verified

## Key Findings
- Total fixtures: 13+ (5 option + 5 feature + 3 partial)
- Sprint 7 patterns fully reusable
- YAML structure defined with backward compatibility
- Coverage: [X%] of feature space

## Unknown Verification
- 7.1: ✅ 13+ fixtures identified
- 7.2: ✅ Sprint 7 patterns reusable
- 7.3: ✅ YAML structure defined

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] Option statement fixtures designed (5 fixtures)
- [x] High-ROI feature fixtures designed (5 fixtures)
- [x] Partial parse metric fixtures designed (3 fixtures)
- [x] expected_results.yaml structure defined
- [x] README templates created
- [x] Total 13+ fixtures planned
- [x] Sprint 7 fixture patterns reused
- [x] Unknowns 7.1, 7.2, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 8 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 9: Design Dashboard Enhancements

**On a new branch:** `prep/sprint8-task9-dashboard`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Design enhancements to `GAMSLIB_CONVERSION_STATUS.md` to display partial parse metrics, missing features, and color-coded status. Maintain backward compatibility.

**Why This Matters:**
Current dashboard shows binary pass/fail. Sprint 8 adds partial metrics to show progress.

PROJECT_PLAN.md: *"Dashboard shows statement-level parse success (e.g., 'himmel16: 85% parsed')"*

### 2. WHAT TO DELIVER

**1. Dashboard Mockup Design (1-2 hours)**
**2. Ingestion Script Updates (1 hour)**
**3. Dashboard Template Design (1 hour)**
**4. Backward Compatibility Check (<1 hour)**

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (120+ lines)
- Dashboard mockup with partial metrics
- Color coding (✅ 🟡 ⚠️ ❌)
- Ingestion script design
- Dashboard template
- Backward compatibility analysis

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 6.4

**Unknown 6.4: Can dashboard show partial metrics without major refactoring?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 9 (Design Dashboard Enhancements)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Current dashboard template: [Simple Markdown table]
  - Required changes: [Add columns for parse %, missing features]
  - Backward compatibility: [Yes - new columns optional]
  
  **Evidence:**
  - Dashboard mockup shows feasible design
  - Ingestion script needs [minor/major] updates
  - Template structure remains [mostly unchanged/significantly changed]
  
  **Decision:**
  - Dashboard refactoring: [Minor - add columns / Major - redesign]
  - Implementation effort: [X] hours
  
  **Impact:**
  - Sprint 8 includes dashboard updates
  - Backward compatible with Sprint 7 data
  - No breaking changes to existing dashboards
  ```

### 4. UPDATE PREP_PLAN.md

**Task 9 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` [XXX lines]
  
  **Dashboard Mockup:**
  - Designed new table format with partial metrics
  - Added columns: [Parse %, Missing Features, Status (color-coded)]
  - Example row: "himmel16.gms | 🟡 PARTIAL | 85% | i++1 indexing"
  
  **Color Coding:**
  - ✅ GREEN (100%): Fully parsed
  - 🟡 YELLOW (75-99%): Mostly parsed, minor issues
  - ⚠️ ORANGE (25-74%): Partially parsed, major blockers
  - ❌ RED (<25%): Failed to parse
  
  **Ingestion Script Updates:**
  - Designed updates to parse partial metrics from test results
  - Extract parse percentage from [statement counting mechanism]
  - Extract missing features from [error message patterns]
  - Estimated changes: [X] lines in [script name]
  
  **Dashboard Template:**
  - Modified template structure: [Description]
  - Backward compatible: [Yes/No with details]
  - Sample output format documented
  
  **Backward Compatibility:**
  - Sprint 7 data displays correctly: [Yes/No]
  - New columns default to [N/A / - / empty] for old data
  - No breaking changes to existing workflows
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] Dashboard mockup created with partial metrics
  - [x] Color coding defined (✅ 🟡 ⚠️ ❌)
  - [x] Ingestion script updates designed
  - [x] Dashboard template modified
  - [x] Backward compatibility validated
  - [x] Implementation effort estimated (3-4 hours)
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 9 - Design Dashboard Enhancements - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Designed enhancements to `GAMSLIB_CONVERSION_STATUS.md` to display partial parse metrics, missing features, and color-coded status. Maintains backward compatibility while adding statement-level progress visibility.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` [XXX lines]
  - Dashboard mockup with partial metrics
  - Color coding scheme (✅ 🟡 ⚠️ ❌)
  - Ingestion script update design
  - Dashboard template modifications
  - Backward compatibility analysis

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknown 6.4)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 9 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Dashboard Mockup:**
```markdown
| Model | Status | Parse % | Missing Features | Notes |
|-------|--------|---------|------------------|-------|
| mhw4d.gms | ✅ PASS | 100% | - | Fully parsed |
| rbrock.gms | ✅ PASS | 100% | - | Fully parsed |
| himmel16.gms | 🟡 PARTIAL | 85% | i++1 indexing | 17/20 statements |
| circle.gms | ⚠️ PARTIAL | 40% | function calls, preprocessor | 8/20 statements |
| hs62.gms | ❌ FAIL | 15% | model sections (mx) | 3/20 statements |
| [others...] | | | | |
```

**Color Coding:**
- ✅ GREEN (100%): Full parse success
  - Example: mhw4d.gms, rbrock.gms
- 🟡 YELLOW (75-99%): Mostly parsed, minor blockers
  - Example: himmel16.gms (needs only i++1 indexing)
- ⚠️ ORANGE (25-74%): Partially parsed, major blockers
  - Example: circle.gms (needs 2 features)
- ❌ RED (<25%): Mostly failed
  - Example: hs62.gms (early syntax error)

**Ingestion Script Updates:**
- Parse percentage extraction:
  - Source: [Statement counting from partial parse metrics]
  - Calculation: (parsed_statements / total_statements) × 100
- Missing feature extraction:
  - Source: [Error message pattern matching]
  - Format: Comma-separated list (e.g., "i++1 indexing, model sections")
- Status determination:
  - Logic: if parse % = 100 → ✅, elif ≥75 → 🟡, elif ≥25 → ⚠️, else → ❌
- Estimated changes: [X] lines in `[script_name.py]`

**Dashboard Template:**
- Current structure: [Simple Markdown table]
- Modifications:
  - Add "Parse %" column (after Status)
  - Add "Missing Features" column (after Parse %)
  - Update Status to use color-coded symbols
  - Add "Notes" column for statement counts
- Backward compatibility: ✅ Yes
  - Old data shows: Status = ✅/❌, Parse % = 100%/0%, Missing = "-"

**Backward Compatibility:**
- Sprint 7 data displays: ✅ Correctly (100% or 0%, no missing features)
- New columns: Default to "-" for models without partial data
- No breaking changes: Existing workflows unaffected
- Migration: None needed (ingestion script auto-populates)

**Implementation Effort:**
- Ingestion script: [X] hours
- Template updates: [Y] hours
- Testing: [Z] hours
- Total: 3-4 hours estimated

#### Unknown Verification

**6.4: Can dashboard show partial metrics without major refactoring?**
- ✅ VERIFIED: Minor refactoring only
- Changes: Add 2 columns, update status symbols
- Backward compatible: Yes, no breaking changes
- Effort: 3-4 hours (confirmed)

#### Next Steps

**Task 10:** Plan Sprint 8 Detailed Schedule
- Create day-by-day execution plan incorporating all prep findings
- Define checkpoints, quality gates, and risk mitigation
- Cross-reference Tasks 2-9 deliverables
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (current dashboard, Sprint 7 data format)
- ✅ Verify all deliverables are complete
- ✅ Verify unknown 6.4 has complete verification results
- ✅ Verify all Task 9 acceptance criteria are checked in PREP_PLAN.md
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task9-dashboard
git add -A
git commit -m "Complete Sprint 8 Prep Task 9: Design Dashboard Enhancements

Designed dashboard enhancements to display partial parse metrics with
backward compatibility, enabling visibility into statement-level progress.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md [XXX lines]
  - Dashboard mockup with partial metrics
  - Color coding (✅ 🟡 ⚠️ ❌)
  - Ingestion script updates
  - Template modifications
  - Backward compatibility analysis

DASHBOARD MOCKUP:
- New columns: Parse %, Missing Features, Notes
- Color-coded status: ✅ (100%), 🟡 (75-99%), ⚠️ (25-74%), ❌ (<25%)
- Example: \"himmel16.gms | 🟡 PARTIAL | 85% | i++1 indexing\"

COLOR CODING:
- ✅ GREEN: 100% parsed (mhw4d, rbrock)
- 🟡 YELLOW: 75-99% (himmel16 - needs 1 feature)
- ⚠️ ORANGE: 25-74% (circle - needs 2 features)
- ❌ RED: <25% (hs62 - early failure)

INGESTION SCRIPT UPDATES:
- Parse percentage: (parsed_statements / total) × 100
- Missing features: Extract from error patterns
- Status: Threshold-based (100 → ✅, 75-99 → 🟡, etc.)
- Estimated changes: [X] lines

DASHBOARD TEMPLATE:
- Add columns: Parse %, Missing Features
- Update Status to color-coded symbols
- Backward compatible: Old data shows 100%/0%, \"-\"

BACKWARD COMPATIBILITY:
- Sprint 7 data: ✅ Displays correctly
- New columns: Default to \"-\" for old models
- No breaking changes: Existing workflows unaffected

IMPLEMENTATION EFFORT:
- Ingestion: [X] hours
- Template: [Y] hours
- Testing: [Z] hours
- Total: 3-4 hours

UNKNOWN VERIFICATION:
- 6.4: Minor refactoring only, 3-4 hours confirmed

FILES MODIFIED:
- Created: DASHBOARD_ENHANCEMENTS.md
- Modified: KNOWN_UNKNOWNS.md (verified 6.4)
- Modified: PREP_PLAN.md (Task 9 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task9-dashboard
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 9: Design Dashboard Enhancements" \
  --body "Completes Task 9 of Sprint 8 prep phase.

## Deliverables
- ✅ DASHBOARD_ENHANCEMENTS.md with mockup
- ✅ Color coding (✅ 🟡 ⚠️ ❌)
- ✅ Ingestion script design
- ✅ Template modifications
- ✅ Backward compatibility validated
- ✅ Unknown 6.4 verified

## Key Findings
- Dashboard shows: \"himmel16: 85% parsed, needs [i++1 indexing]\"
- Color-coded progress: ✅ 🟡 ⚠️ ❌ based on parse %
- Backward compatible: Sprint 7 data displays correctly
- Implementation: 3-4 hours (minor refactoring)

## Unknown Verification
- 6.4: ✅ Minor refactoring, no breaking changes

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] Dashboard mockup created with partial metrics
- [x] Color coding defined (✅ 🟡 ⚠️ ❌)
- [x] Ingestion script updates designed
- [x] Dashboard template modified
- [x] Backward compatibility validated
- [x] Implementation effort estimated (3-4 hours)
- [x] Unknown 6.4 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 9 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

## Task 10: Plan Sprint 8 Detailed Schedule

**On a new branch:** `prep/sprint8-task10-detailed-plan`

### 1. OBJECTIVE & CONTEXT

**Objective:**
Create detailed day-by-day execution plan for Sprint 8, incorporating findings from all prep tasks (1-9). Define deliverables, effort estimates, checkpoints, quality gates.

**Deliverable:** `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (1500+ lines, similar to Sprint 7)

**Why This Matters:**
Sprint 7 PLAN.md provided detailed daily breakdown. Sprint 8 needs similar rigor for 25-35 hour execution.

All prep tasks feed into this plan.

### 2. WHAT TO DELIVER

**1. Day-by-Day Breakdown (3-4 hours)**

Days 0-10 with objectives, tasks, deliverables, quality gates

**2. Checkpoint Definitions (1-2 hours)**

3-4 checkpoints with clear go/no-go criteria

**3. Effort Allocation Validation (1 hour)**

Verify 25-35 hour total

**4. Quality Gates & Testing Strategy (1 hour)**

Define continuous checks and feature-specific gates

**5. Risk Mitigation (1 hour)**

Plan for Known Unknowns and risks

**6. Cross-Reference All Prep Tasks (<1 hour)**

Link each day to relevant tasks

**Deliverables:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (1500+ lines)
- Day-by-day breakdown (Days 0-10)
- Checkpoint definitions (3-4 checkpoints)
- Effort allocation breakdown
- Quality gates
- Risk mitigation
- Cross-references to all prep tasks

### 3. VERIFY KNOWN UNKNOWNS

Update `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` for unknowns verified by this task:

**Unknowns to Verify:** 8.1, 8.2, 8.3

All unknowns should be verified by now - synthesize findings.

**Unknown 8.1: Can Sprint 8 fit in 25-35 hours?**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add **Verification Results** section:
  ```markdown
  ✅ **Status:** VERIFIED  
  **Verified by:** Task 10 (Plan Sprint 8 Detailed Schedule)  
  **Date:** 2025-11-17
  
  **Findings:**
  - Option statements: [6-8 hours confirmed]
  - [Indexed assignments / Function calls]: [6-8 hours confirmed]
  - Parser error line numbers: [4-6 hours confirmed]
  - Partial parse metrics: [4-6 hours confirmed]
  - Error message enhancements: [3-5 hours confirmed]
  - Dashboard updates: [3-4 hours confirmed]
  - Test fixtures: [X hours for 13+ fixtures]
  - Documentation: [Y hours]
  - Total: [Sum] hours
  
  **Evidence:**
  - Tasks 2-9 validated all effort estimates
  - Day-by-day breakdown shows realistic timeline
  - Checkpoints allow for mid-sprint adjustments
  
  **Decision:**
  - Sprint 8 duration: [25-35 hours is achievable / needs adjustment to X-Y hours]
  - Timeline: [Conservative / Optimistic / Realistic]
  
  **Impact:**
  - Sprint 8 is [feasible / tight / needs scope reduction]
  - Buffer for unknowns: [X] hours
  ```

**Unknown 8.2: What checkpoints should Sprint 8 have?**
- Add verification results with:
  - Findings: "[N] checkpoints identified at critical decision points"
  - Evidence: Checkpoint definitions from deliverable
  - Decision: "Checkpoints: [list checkpoint names and days]"
  - Impact: "Mid-sprint course correction possible at [days]"

**Unknown 8.3: How do we synthesize all prep findings into execution plan?**
- Add verification results with:
  - Findings: "Tasks 2-9 feed into daily breakdown as follows..."
  - Evidence: Cross-references in PLAN.md
  - Decision: "Each day references [specific prep tasks]"
  - Impact: "Execution plan is fully grounded in research"

### 4. UPDATE PREP_PLAN.md

**Task 10 Status Update:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```markdown
  **Created:** `docs/planning/EPIC_2/SPRINT_8/PLAN.md` [XXX lines]
  
  **Day-by-Day Breakdown:**
  - Detailed breakdown for Days 0-10 (or Days 0-X based on effort)
  - Each day includes: Objective, Tasks, Deliverables, Quality Gates
  - Cross-references to prep tasks: [list which prep tasks inform each day]
  
  **Checkpoint Definitions:**
  - Checkpoint 1: [Name] (Day X)
    - Criteria: [Go/No-Go criteria]
    - Decision: [What to evaluate]
  - Checkpoint 2: [Name] (Day Y)
    - Criteria: [Go/No-Go criteria]
    - Decision: [What to evaluate]
  - Checkpoint 3: [Name] (Day Z)
    - Criteria: [Go/No-Go criteria]
    - Decision: [What to evaluate]
  - [Additional checkpoints if needed]
  
  **Effort Allocation:**
  - Option statements: [X] hours (Days A-B)
  - [Chosen feature]: [Y] hours (Days C-D)
  - Error line numbers: [Z] hours (Day E)
  - Partial metrics: [W] hours (Day F)
  - Error messages: [V] hours (Day G)
  - Dashboard: [U] hours (Day H)
  - Test fixtures: [T] hours (Days I-J)
  - Documentation: [S] hours (Day K)
  - Total: [Sum] hours ([within / exceeds] 25-35 hour target)
  
  **Quality Gates:**
  - Continuous: [make test, make typecheck, etc.]
  - Feature-specific: [list quality gates per feature]
  - Integration: [GAMSLib conversion tests]
  - Final: [all tests pass, parse rate ≥25%]
  
  **Risk Mitigation:**
  - Risk 1: [from Known Unknowns]
    - Mitigation: [strategy from prep tasks]
  - Risk 2: [from prep research]
    - Mitigation: [strategy]
  - [Additional risks...]
  
  **Cross-References:**
  - Task 2 (Feature Matrix) → Days [X-Y] (feature selection)
  - Task 3 (Option Research) → Days [A-B] (option implementation)
  - Task 7 (High-ROI Feature) → Days [C-D] (feature implementation)
  - Task 8 (Test Fixtures) → Days [I-J] (fixture creation)
  - [All prep tasks mapped to execution days]
  ```

- Fill in **Result** section with key achievements
- Check off ALL acceptance criteria items:
  ```markdown
  - [x] Day-by-day breakdown created (Days 0-10 or 0-X)
  - [x] Checkpoint definitions documented (3-4 checkpoints)
  - [x] Effort allocation validated (25-35 hours total)
  - [x] Quality gates defined (continuous + feature-specific)
  - [x] Risk mitigation planned
  - [x] All prep tasks cross-referenced
  - [x] Sprint 8 PLAN.md follows Sprint 7 format (1500+ lines)
  ```

### 5. UPDATE CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 8 Prep: Task 10 - Plan Sprint 8 Detailed Schedule - 2025-11-17

**Status:** ✅ COMPLETE

#### Summary

Created detailed day-by-day execution plan for Sprint 8, incorporating findings from all prep tasks (2-9). Defined deliverables, effort estimates, checkpoints, quality gates, and risk mitigation for 25-35 hour sprint execution.

#### Deliverables

**Created:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` [XXX lines]
  - Day-by-day breakdown (Days 0-10 or 0-X)
  - Checkpoint definitions (3-4 checkpoints)
  - Effort allocation breakdown
  - Quality gates (continuous + feature-specific)
  - Risk mitigation strategies
  - Cross-references to all prep tasks

**Modified:**
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (verified unknowns 8.1, 8.2, 8.3)
- `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` (Task 10 marked complete)
- `CHANGELOG.md` (this entry)

#### Key Findings

**Effort Allocation:**
- Option statements: [X] hours (Days A-B)
  - Based on Task 3 research
- [Indexed assignments / Function calls]: [Y] hours (Days C-D)
  - Based on Task 7 research
- Parser error line numbers: [Z] hours (Day E)
  - Based on Task 4 design
- Partial parse metrics: [W] hours (Day F)
  - Based on Task 5 design
- Error message enhancements: [V] hours (Day G)
  - Based on Task 6 research
- Dashboard updates: [U] hours (Day H)
  - Based on Task 9 design
- Test fixtures: [T] hours (Days I-J)
  - Based on Task 8 strategy (13+ fixtures)
- Documentation: [S] hours (Day K)
- **Total: [Sum] hours** ([Conservative: 25 / Optimistic: 35 / Actual: X])

**Day-by-Day Breakdown:**
- **Day 0:** Sprint planning and setup
  - Review PLAN.md, set up branch, confirm scope
- **Days 1-2:** Implement option statements
  - Grammar changes, AST nodes, tests
  - Checkpoint 1: Option statements parsing
- **Days 3-4:** Implement [chosen feature]
  - Grammar changes, AST nodes, tests
  - Checkpoint 2: [Feature] parsing
- **Day 5:** Parser error line numbers
  - Extract location, enhance exceptions
- **Day 6:** Partial parse metrics
  - Statement counting, missing feature extraction
- **Day 7:** Error message enhancements
  - "Did you mean?" suggestions
- **Day 8:** Dashboard updates
  - Ingestion script, template modifications
  - Checkpoint 3: All features integrated
- **Days 9-10:** Test fixtures and documentation
  - 13+ fixtures, README updates
  - Final checkpoint: Parse rate ≥25%

**Checkpoint Definitions:**
1. **Checkpoint 1: Option Statements Parsing** (End of Day 2)
   - Criteria: mhw4dx.gms parses successfully
   - Go: Continue to [chosen feature]
   - No-Go: Debug option implementation (allocate buffer hours)

2. **Checkpoint 2: [Chosen Feature] Parsing** (End of Day 4)
   - Criteria: [Model(s)] parse successfully
   - Go: Continue to polish features
   - No-Go: Assess scope reduction (defer partial metrics or error messages)

3. **Checkpoint 3: All Features Integrated** (End of Day 8)
   - Criteria: All features work together, tests pass
   - Go: Final testing and documentation
   - No-Go: Defer test fixtures, focus on core functionality

4. **Final Checkpoint: Sprint Complete** (End of Day 10)
   - Criteria: Parse rate ≥25%, all tests pass
   - Go: Create PR, mark sprint complete
   - No-Go: Document blockers, plan Sprint 8b

**Quality Gates:**
- **Continuous (every commit):**
  - `make test` passes
  - `make typecheck` passes
  - `make lint` passes
  - No regressions in existing tests

- **Feature-Specific:**
  - Option statements: mhw4dx.gms parses (Day 2)
  - [Chosen feature]: [Model(s)] parse (Day 4)
  - Error line numbers: All errors include location (Day 5)
  - Partial metrics: Dashboard shows parse % (Day 8)

- **Integration (Day 8):**
  - GAMSLib conversion test suite passes
  - Parse rate ≥25% (3+ models out of 10)
  - No regressions in mhw4d.gms, rbrock.gms

- **Final (Day 10):**
  - All acceptance criteria met
  - Documentation complete
  - CHANGELOG updated
  - Ready for PR

**Risk Mitigation:**
- **Risk 1:** Option statements take longer than 6-8 hours
  - Mitigation: Checkpoint 1 at Day 2, can defer error messages if needed
  - Buffer: [X] hours available in Days 9-10

- **Risk 2:** [Chosen feature] has hidden complexity
  - Mitigation: Task 7 deep dive identified risks, Checkpoint 2 at Day 4
  - Fallback: Reduce scope to basic cases, defer advanced syntax

- **Risk 3:** Parse rate doesn't reach 25%
  - Mitigation: Task 2 feature matrix validates unlock rates
  - Fallback: Document findings, plan Sprint 8b with adjusted scope

- **Risk 4:** Test fixtures take longer than estimated
  - Mitigation: Fixtures are lowest priority, can defer some to Sprint 8b
  - Essential: Only option and [chosen feature] fixtures critical

**Cross-References:**
- **Task 2 (Feature Matrix)** → Days 1-4 (feature selection validated)
- **Task 3 (Option Research)** → Days 1-2 (option implementation)
- **Task 4 (Error Line Numbers)** → Day 5 (line number design)
- **Task 5 (Partial Metrics)** → Day 6 (metrics implementation)
- **Task 6 (Error Messages)** → Day 7 (message enhancements)
- **Task 7 (High-ROI Feature)** → Days 3-4 (feature implementation)
- **Task 8 (Test Fixtures)** → Days 9-10 (fixture creation)
- **Task 9 (Dashboard)** → Day 8 (dashboard updates)

#### Unknown Verification

**8.1: Can Sprint 8 fit in 25-35 hours?**
- ✅ VERIFIED: [Yes / Tight fit / Needs adjustment]
- Total effort: [Sum] hours
- Timeline: [Conservative / Optimistic / Realistic]

**8.2: What checkpoints should Sprint 8 have?**
- ✅ VERIFIED: 4 checkpoints at Days 2, 4, 8, 10
- Allow mid-sprint course correction

**8.3: How do we synthesize all prep findings into execution plan?**
- ✅ VERIFIED: Each day cross-references prep tasks
- Research fully integrated into execution

#### Next Steps

**Sprint 8 Execution:**
- Review PLAN.md
- Wait for prep phase completion (all Tasks 2-10 done)
- Create Sprint 8 execution branch
- Begin Day 0: Sprint planning
```

### 6. QUALITY GATES

**Before committing:**
- ✅ Verify all cross-references are valid (all prep tasks 2-9, Sprint 7 PLAN.md format)
- ✅ Verify all deliverables are complete
- ✅ Verify all unknowns (8.1, 8.2, 8.3) have complete verification results
- ✅ Verify all Task 10 acceptance criteria are checked in PREP_PLAN.md
- ✅ Verify PLAN.md follows Sprint 7 format (1500+ lines, detailed daily breakdown)
- ✅ Documentation-only changes (no code modified, skip quality checks)

### 7. COMMIT & PUSH

```bash
git checkout -b prep/sprint8-task10-detailed-plan
git add -A
git commit -m "Complete Sprint 8 Prep Task 10: Plan Sprint 8 Detailed Schedule

Created detailed day-by-day execution plan for Sprint 8, incorporating
all prep findings (Tasks 2-9) with checkpoints, quality gates, and risk mitigation.

DELIVERABLES:
- docs/planning/EPIC_2/SPRINT_8/PLAN.md [XXX lines]
  - Day-by-day breakdown (Days 0-10)
  - Checkpoint definitions (4 checkpoints)
  - Effort allocation breakdown
  - Quality gates (continuous + feature-specific)
  - Risk mitigation strategies
  - Cross-references to Tasks 2-9

EFFORT ALLOCATION:
- Option statements: [X] hours (Days 1-2)
- [Chosen feature]: [Y] hours (Days 3-4)
- Error line numbers: [Z] hours (Day 5)
- Partial metrics: [W] hours (Day 6)
- Error messages: [V] hours (Day 7)
- Dashboard: [U] hours (Day 8)
- Test fixtures: [T] hours (Days 9-10)
- Total: [Sum] hours

DAY-BY-DAY:
- Day 0: Sprint planning
- Days 1-2: Option statements (Checkpoint 1)
- Days 3-4: [Chosen feature] (Checkpoint 2)
- Day 5: Error line numbers
- Day 6: Partial metrics
- Day 7: Error enhancements
- Day 8: Dashboard (Checkpoint 3)
- Days 9-10: Fixtures & docs (Final Checkpoint)

CHECKPOINTS:
- Checkpoint 1 (Day 2): Option statements parsing
- Checkpoint 2 (Day 4): [Chosen feature] parsing
- Checkpoint 3 (Day 8): All features integrated
- Final (Day 10): Parse rate ≥25%

QUALITY GATES:
- Continuous: make test, typecheck, lint
- Feature-specific: [gates per feature]
- Integration: GAMSLib tests, parse rate ≥25%
- Final: All criteria met, ready for PR

RISK MITIGATION:
- Risk 1: Options take longer → Checkpoint 1 catches early
- Risk 2: [Feature] complexity → Task 7 identified, Checkpoint 2
- Risk 3: Parse rate miss → Task 2 matrix validates
- Risk 4: Fixture time → Lowest priority, can defer

CROSS-REFERENCES:
- Task 2 → Days 1-4 (feature selection)
- Task 3 → Days 1-2 (option implementation)
- Task 4 → Day 5 (error line numbers)
- Task 5 → Day 6 (partial metrics)
- Task 6 → Day 7 (error messages)
- Task 7 → Days 3-4 (high-ROI feature)
- Task 8 → Days 9-10 (test fixtures)
- Task 9 → Day 8 (dashboard)

UNKNOWN VERIFICATION:
- 8.1: Sprint 8 fits in [25-35 / X-Y] hours
- 8.2: 4 checkpoints at Days 2, 4, 8, 10
- 8.3: All prep tasks integrated into daily plan

FILES MODIFIED:
- Created: PLAN.md [1500+ lines]
- Modified: KNOWN_UNKNOWNS.md (verified 8.1, 8.2, 8.3)
- Modified: PREP_PLAN.md (Task 10 complete)
- Modified: CHANGELOG.md"

git push -u origin prep/sprint8-task10-detailed-plan
```

### 8. PULL REQUEST & REVIEW

```bash
# Create PR
gh pr create \
  --title "Complete Sprint 8 Prep Task 10: Plan Sprint 8 Detailed Schedule" \
  --body "Completes Task 10 of Sprint 8 prep phase.

## Deliverables
- ✅ PLAN.md with day-by-day breakdown (1500+ lines)
- ✅ Checkpoint definitions (4 checkpoints)
- ✅ Effort allocation ([Sum] hours)
- ✅ Quality gates (continuous + feature-specific)
- ✅ Risk mitigation strategies
- ✅ Cross-references to all prep tasks
- ✅ Unknowns 8.1, 8.2, 8.3 verified

## Key Findings
- Sprint 8 duration: [Sum] hours ([within / near / exceeds] 25-35 target)
- Checkpoints at Days 2, 4, 8, 10 allow course correction
- All prep findings (Tasks 2-9) integrated into execution plan
- Parse rate ≥25% achievable with [option + chosen feature]

## Unknown Verification
- 8.1: ✅ Sprint 8 [fits / needs adjustment]
- 8.2: ✅ 4 checkpoints defined
- 8.3: ✅ Prep findings synthesized

Closes #[issue] (if applicable)"

# Wait for Copilot review
# Address any review comments
# Wait for approval
# Merge when ready
```

**After PR is created:**
1. ✅ Wait for Copilot review comments
2. ✅ Address each comment (fix issues, reply with explanations)
3. ✅ Push fixes if needed
4. ✅ Wait for review approval
5. ✅ Merge PR when all checks pass

### 9. ACCEPTANCE CRITERIA

Verify ALL criteria before closing task:

- [x] Day-by-day breakdown created (Days 0-10 or 0-X)
- [x] Checkpoint definitions documented (3-4 checkpoints)
- [x] Effort allocation validated (25-35 hours total)
- [x] Quality gates defined (continuous + feature-specific)
- [x] Risk mitigation planned
- [x] All prep tasks cross-referenced
- [x] Sprint 8 PLAN.md follows Sprint 7 format (1500+ lines)
- [x] Unknowns 8.1, 8.2, 8.3 verified in KNOWN_UNKNOWNS.md
- [x] PREP_PLAN.md Task 10 marked complete
- [x] CHANGELOG.md updated
- [x] PR created and merged

---

# USAGE NOTES

**For each task:**
1. Create new branch with suggested name
2. Follow "What to Deliver" section step-by-step
3. Verify all unknowns with complete findings
4. Update all documentation (PREP_PLAN, CHANGELOG, KNOWN_UNKNOWNS)
5. Run quality gates before committing
6. Create PR and wait for review
7. Address review comments
8. Merge when approved
9. Move to next task

**Documentation-only tasks (all prep tasks):** Skip `make typecheck && make lint && make format && make test`

**Critical Success Factors:**
- Complete verification of all assigned unknowns
- All acceptance criteria checked before PR
- Cross-references validated
- Clear, actionable findings documented
