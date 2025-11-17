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
  **Created:** `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (XXX lines)
  
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

**Unknowns to Verify:** 4.1, 4.2, 4.3, 4.4

Update each unknown with verification results based on error type survey and design.

### 4-9. [Standard sections for PREP_PLAN, CHANGELOG, Quality Gates, Commit, PR, Acceptance Criteria]

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

**Unknowns to Verify:** 6.1, 6.2, 6.3, 6.4

### 4-9. [Standard sections]

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

**Unknowns to Verify:** 5.1, 5.2, 5.3, 5.4

### 4-9. [Standard sections]

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

**Unknowns to Verify:** 3.1, 3.2, 3.3

### 4-9. [Standard sections]

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

**Unknowns to Verify:** 7.1, 7.2, 7.3

### 4-9. [Standard sections]

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

**Unknowns to Verify:** 6.4

### 4-9. [Standard sections]

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

**Unknowns to Verify:** 8.1, 8.2, 8.3

All unknowns should be verified by now - synthesize findings.

### 4-9. [Standard sections]

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
