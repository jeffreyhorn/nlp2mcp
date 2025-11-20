# Sprint 9 Prep Task Prompts

This document contains ready-to-use prompts for executing Sprint 9 Prep Tasks 2-10. Each prompt includes full task context, unknown verification instructions, documentation updates, quality gates, and PR creation.

---

## Task 2: Complete Secondary Blocker Analysis for mhw4dx.gms

Execute Sprint 9 Prep Task 2 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 488-640).

### Objective

Identify ALL blockers (not just primary) preventing mhw4dx.gms from parsing. Update `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` with complete findings to prevent Sprint 8-style underestimation.

### Context

**Why This Matters:**
Sprint 8 retrospective identified this as **High Priority Recommendation #1**: "Sprint 8 assumed option statements alone would unlock mhw4dx.gms, but secondary blockers exist." Complete blocker analysis prevents underestimation and enables accurate Sprint 9/10 planning.

**Current State:**
- mhw4dx.gms: FAILED (partial parse ~51% per Sprint 8 dashboard)
- Primary Blocker: Option statements (✅ RESOLVED in Sprint 8)
- Secondary Blocker: Unknown (this task identifies it)
- Lines to Analyze: 37-63 (post-option-statement errors)

### What to Do

**1. Current State Verification (15 min)**
- Re-parse mhw4dx.gms with Sprint 8 parser (option statements enabled)
- Verify option statements parse correctly (lines 37, 47)
- Capture first error after option statements
- Record line number and error message

**2. Complete Error Capture (30 min)**
- Parse mhw4dx.gms with error recovery (try `maybe_placeholders=True`)
- Collect all syntax errors, not just first
- Manual inspection of lines 37-63
- Catalog all unsupported features

**3. Secondary Blocker Classification (30 min)**
- Categorize blockers by complexity (Simple/Medium/Complex)
- Prioritize by unlock potential (which appears in most models?)
- Estimate unlock timeline (Sprint 9? Sprint 10?)

**4. Documentation Update (45 min)**
- Update GAMSLIB_FEATURE_MATRIX.md (mhw4dx section with secondary blocker)
- Create `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md` with:
  - Executive summary (which features block mhw4dx?)
  - Line-by-line error catalog (lines 37-63)
  - Feature complexity analysis
  - Unlock recommendations (Sprint 9/10/later)

**5. Validation (15 min)**
- Verify all lines 37-63 analyzed
- Verify all unsupported features cataloged
- Review against Sprint 8 retrospective criteria

### Deliverables

1. Updated `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (mhw4dx section)
2. New `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md` (detailed report)
3. Error catalog (all errors in lines 37-63)
4. Feature complexity estimates (simple/medium/complex)
5. Unlock timeline recommendation (Sprint 9/10/later)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` with verification results:**

**Unknown 9.3.4: Secondary Blocker Analysis Methodology**
- Change status from `🔍 INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG`
- Add **Verification Results** section with:
  - Date verified
  - Findings: Can Lark error recovery capture all errors?
  - Evidence: List all errors found in mhw4dx.gms lines 37-63
  - Decision: Document secondary blocker(s) found
  - Answer to research questions:
    - Can Lark continue parsing after first error? (Yes/No + how)
    - How many errors found? (complete count)
    - Document in GAMSLIB_FEATURE_MATRIX.md or separate file? (decision made)

### Documentation Updates

**1. Update PREP_PLAN.md Task 2:**
- Change status from `🔵 NOT STARTED` to `✅ COMPLETE`
- Fill in **Changes** section:
  ```
  **Created:**
  - docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md (X lines)
  
  **Updated:**
  - docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md (mhw4dx section)
  
  **Verified:**
  - Unknown 9.3.4: Secondary Blocker Analysis Methodology
  ```

- Fill in **Result** section:
  ```
  **Secondary Blocker(s) Found:**
  - [List all secondary blockers identified]
  
  **Complexity Analysis:**
  - Simple: [count] features
  - Medium: [count] features
  - Complex: [count] features
  
  **Unlock Timeline:**
  - Sprint 9: [features that could be addressed]
  - Sprint 10: [features deferred]
  
  **mhw4dx.gms Unlock Probability:**
  - After addressing secondary blocker: [High/Medium/Low]
  ```

- Check off all acceptance criteria (9 items)

**2. Update CHANGELOG.md:**
Add entry under `## [Unreleased]`:
```markdown
### Sprint 9: Prep Task 2 - Secondary Blocker Analysis for mhw4dx.gms - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Completed comprehensive secondary blocker analysis for mhw4dx.gms. Identified [count] secondary blockers preventing full parse after Sprint 8's option statement implementation. Created detailed blocker analysis report with complexity estimates and unlock timeline recommendations.

#### Deliverables

**MHW4DX_BLOCKER_ANALYSIS.md:**
- [X] lines of detailed analysis
- Line-by-line error catalog for lines 37-63
- [count] secondary blockers identified
- Complexity classification: [simple/medium/complex breakdown]
- Unlock timeline: Sprint 9 vs Sprint 10 recommendations

**GAMSLIB_FEATURE_MATRIX.md Updates:**
- Updated mhw4dx.gms section with secondary blocker documentation
- Parse progress: 51% (27/53 lines)
- Primary blocker: Option statements ✅ RESOLVED
- Secondary blocker(s): [list]

#### Key Findings

**Secondary Blockers Identified:**
1. [Blocker 1]: [description] - [complexity]
2. [Blocker 2]: [description] - [complexity]
...

**Unlock Timeline:**
- Sprint 9 candidates: [features]
- Sprint 10 deferrals: [features]

**Verification Results:**
- Unknown 9.3.4: ✅ VERIFIED - [methodology used successfully]
```

### Quality Gates

**Before committing:**
1. Verify GAMSLIB_FEATURE_MATRIX.md updated correctly
2. Verify MHW4DX_BLOCKER_ANALYSIS.md is comprehensive (all lines 37-63 analyzed)
3. Verify KNOWN_UNKNOWNS.md Unknown 9.3.4 has complete verification results
4. Run: `make typecheck && make lint && make format && make test` (should pass if no code changes)

### Commit Instructions

**Create branch:**
```bash
git checkout -b prep/sprint9-task2-secondary-blocker-analysis
```

**Commit message:**
```
Complete Sprint 9 Prep Task 2: Secondary Blocker Analysis for mhw4dx.gms

Identified [count] secondary blockers preventing mhw4dx.gms from parsing
after Sprint 8's option statement implementation.

Secondary blockers found:
- [Blocker 1]: [complexity] - [brief description]
- [Blocker 2]: [complexity] - [brief description]
...

Deliverables:
- MHW4DX_BLOCKER_ANALYSIS.md ([X] lines)
- Updated GAMSLIB_FEATURE_MATRIX.md (mhw4dx section)
- Verified Unknown 9.3.4: Secondary Blocker Analysis Methodology

Unlock timeline:
- Sprint 9 candidates: [count] features
- Sprint 10 deferrals: [count] features

All acceptance criteria met.
```

**Push and create PR:**
```bash
git push -u origin prep/sprint9-task2-secondary-blocker-analysis
gh pr create --title "Sprint 9 Prep Task 2: Secondary Blocker Analysis for mhw4dx.gms" \
  --body "Completes Sprint 9 Prep Task 2 from PREP_PLAN.md.

## Summary
Comprehensive secondary blocker analysis for mhw4dx.gms identifying all features preventing full parse after Sprint 8's option statement implementation.

## Secondary Blockers Identified
- [List all blockers with complexity]

## Deliverables
- ✅ MHW4DX_BLOCKER_ANALYSIS.md ([X] lines)
- ✅ Updated GAMSLIB_FEATURE_MATRIX.md
- ✅ Verified Unknown 9.3.4

## Unlock Timeline
- Sprint 9 candidates: [features]
- Sprint 10 deferrals: [features]

## Acceptance Criteria
- [x] All 9 acceptance criteria met (see PREP_PLAN.md Task 2)

Addresses Sprint 8 Retrospective Recommendation #1." \
  --base main
```

**Wait for reviewer comments before proceeding to Task 3.**

---

## Task 3: Research Advanced Indexing (i++1, i--1) Syntax

Execute Sprint 9 Prep Task 3 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 642-845).

### Objective

Research GAMS lead/lag indexing operators (i++1, i--1) to design grammar rules, semantic handling, and IR representation. Produce comprehensive implementation guide for Sprint 9 Day 3-4 work.

### Context

**Why This Matters:**
Advanced indexing is Sprint 9's highest-effort parser feature (8-10 hours) with "Medium-High" risk due to grammar changes and semantic complexity. Thorough research prevents mid-sprint discovery of unsupported syntax variations.

himmel16.gms unlock depends on i++1 support (PRIMARY blocker per Sprint 8 feature matrix). Successful implementation unlocks 10% parse rate improvement (1/10 models).

**Background:**
- Used in time-series models for referencing adjacent periods
- Example: `x[i++1]` refers to next period's variable
- Common in dynamic optimization, inventory models

### What to Do

**1. GAMS Documentation Survey (2 hours)**
- Read GAMS User Guide on lead/lag operators
- Catalog variations: i++1, i++2, i++N, i--1, i--2, i--N
- Identify semantic constraints (time indices only? ordered sets?)
- Boundary behavior: wrap-around vs error

**2. GAMSLib Pattern Analysis (1.5 hours)**
- Search: `grep -r "++[0-9]" data/gamslib/*.gms`
- Search: `grep -r "--[0-9]" data/gamslib/*.gms`
- Analyze himmel16.gms specific usage (lines where i++1 appears)
- Catalog all unique patterns found

**3. Grammar Design (2 hours)**
- Design Lark grammar rules for lead/lag indexing
- Test grammar conflicts (++ vs + operator precedence)
- Prototype with minimal test cases
- Document AST structure

**4. Semantic Handler Design (1.5 hours)**
- Design IR representation (IndexOffset vs alternatives)
- Design semantic validation (boundary checks, circular sets)
- Design offset calculation logic

**5. Test Fixture Design (45 min)**
- Identify 4-5 test cases (simple lead, simple lag, multi-dim, boundaries)
- Create fixture directory structure
- Design expected_results.yaml schema

**6. Documentation (45 min)**
- Create LEAD_LAG_INDEXING_RESEARCH.md (600-800 lines)
- Create implementation guide (step-by-step)
- Validate effort estimate (should align with 8-10h in PROJECT_PLAN.md)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md` (600-800 lines)
2. GAMS lead/lag operator syntax catalog (5-10 variations)
3. Lark grammar design for i++1/i--1
4. IR representation design (IndexOffset or equivalent)
5. Semantic validation logic specification
6. Test fixture strategy (4-5 fixtures)
7. Implementation guide (step-by-step)
8. Effort estimate validation (7-10h)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` with verification results:**

**Unknown 9.1.1: i++1/i--1 Lead/Lag Indexing Complexity**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: Does i++1 work in time-indexed sets only or general ordered sets?
- Evidence: GAMS User Guide citations, GAMSLib pattern counts
- Decision: 8-10h estimate validated or adjusted
- Answer all 5 research questions with evidence

**Unknown 9.1.2: i++1/i--1 Grammar Integration**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: Lark grammar prototype results
- Evidence: Test cases showing ++ precedence, conflicts (if any)
- Decision: Grammar design chosen (context-aware vs token-level)
- Answer all 5 research questions

**Unknown 9.1.3: i++1/i--1 Semantic Handling**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: IR representation chosen (IndexOffset vs alternatives)
- Evidence: Design rationale, pros/cons analysis
- Decision: Boundary validation approach (parse-time vs runtime)
- Answer all 5 research questions

**Unknown 9.1.8: himmel16.gms Unlock Probability**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: Secondary blockers found (or not found) in himmel16.gms
- Evidence: Manual inspection results, parse attempt after i++1
- Decision: Unlock probability (High/Medium/Low)

**Unknown 9.1.10: Advanced Feature Test Coverage**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: Fixture count for i++1 feature (4-6 fixtures)
- Evidence: Test case breakdown (simple lead, lag, multi-dim, boundaries, etc.)

### Documentation Updates

**1. Update PREP_PLAN.md Task 3:**
- Change status to `✅ COMPLETE`
- Fill in **Changes** section:
  ```
  **Created:**
  - docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md (X lines)
  
  **Verified:**
  - Unknown 9.1.1: i++1/i--1 complexity (8-10h estimate validated)
  - Unknown 9.1.2: Grammar integration (Lark prototype successful)
  - Unknown 9.1.3: Semantic handling (IndexOffset IR design chosen)
  - Unknown 9.1.8: himmel16.gms unlock (High/Medium/Low probability)
  - Unknown 9.1.10: Test coverage (X fixtures planned)
  ```

- Fill in **Result** section:
  ```
  **GAMS Operator Variations Cataloged:**
  - [count] lead/lag patterns found in GAMSLib
  - Variations: i++1, i++2, i--1, etc.
  
  **Grammar Design:**
  - Approach: [context-aware vs token-level]
  - Conflicts: [None / details]
  - AST structure: [description]
  
  **IR Representation:**
  - Chosen: IndexOffset(base='i', offset=1)
  - Rationale: [why this design]
  
  **Implementation Effort:**
  - Grammar: 2-3h
  - Semantic handler: 3-4h
  - Tests: 2-3h
  - Total: 7-10h (validates PROJECT_PLAN estimate)
  
  **himmel16.gms Unlock:**
  - Probability: [High/Medium/Low]
  - Secondary blockers: [None / list]
  ```

- Check off all acceptance criteria (11 items)

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 3 - Research Advanced Indexing (i++1, i--1) - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Completed comprehensive research on GAMS lead/lag indexing operators (i++1, i--1). Designed grammar rules, IR representation, and semantic validation logic. Created implementation guide validating 8-10 hour effort estimate for Sprint 9 Days 3-4.

#### Deliverables

**LEAD_LAG_INDEXING_RESEARCH.md ([X] lines):**
- GAMS operator syntax catalog: [count] variations
- Lark grammar design with precedence rules
- IR representation: IndexOffset(base, offset)
- Semantic validation specification
- Test fixture strategy: [count] fixtures
- Step-by-step implementation guide

**Key Findings:**
- **Operator variations:** i++1, i++2, i--1, i--2, i++N, i--N
- **Grammar approach:** [context-aware / token-level]
- **Boundary handling:** [wrap-around / error / depends on set type]
- **himmel16.gms unlock:** [High/Medium/Low] probability
- **Implementation effort:** 7-10h validated (aligns with PROJECT_PLAN)

**Unknowns Verified:**
- 9.1.1: ✅ i++1/i--1 complexity (8-10h realistic)
- 9.1.2: ✅ Grammar integration (no major conflicts)
- 9.1.3: ✅ Semantic handling (IndexOffset IR design)
- 9.1.8: ✅ himmel16.gms unlock ([probability])
- 9.1.10: ✅ Test coverage ([count] fixtures)
```

### Quality Gates

**Before committing:**
1. Verify LEAD_LAG_INDEXING_RESEARCH.md is 600-800 lines
2. Verify all 5 unknowns have complete verification results in KNOWN_UNKNOWNS.md
3. Verify grammar prototype tested (include test results)
4. Run: `make typecheck && make lint && make format && make test`

### Commit Instructions

**Branch & Commit:**
```bash
git checkout -b prep/sprint9-task3-lead-lag-indexing-research

git commit -m "Complete Sprint 9 Prep Task 3: Research Advanced Indexing (i++1, i--1)

Comprehensive research on GAMS lead/lag indexing operators.

Key findings:
- [count] operator variations cataloged from GAMSLib
- Grammar design: [approach] (no major conflicts)
- IR representation: IndexOffset(base, offset)
- himmel16.gms unlock: [probability] (secondary blockers: [none/list])
- Implementation effort: 7-10h validated

Deliverables:
- LEAD_LAG_INDEXING_RESEARCH.md ([X] lines)
- Grammar design with Lark prototype
- Semantic validation specification
- Test fixture strategy ([count] fixtures)
- Step-by-step implementation guide

Verified unknowns:
- 9.1.1: i++1/i--1 complexity ✅
- 9.1.2: Grammar integration ✅
- 9.1.3: Semantic handling ✅
- 9.1.8: himmel16.gms unlock ✅
- 9.1.10: Test coverage ✅

All acceptance criteria met."
```

**Push and create PR:**
```bash
git push -u origin prep/sprint9-task3-lead-lag-indexing-research
gh pr create --title "Sprint 9 Prep Task 3: Research Advanced Indexing (i++1, i--1)" \
  --body "Completes Sprint 9 Prep Task 3 from PREP_PLAN.md.

## Summary
Comprehensive research on GAMS lead/lag indexing operators (i++1, i--1) with grammar design, IR representation, and implementation guide.

## Key Findings
- **Operator variations:** [count] patterns in GAMSLib
- **Grammar approach:** [context-aware / token-level]
- **IR design:** IndexOffset(base, offset)
- **himmel16.gms unlock:** [probability]

## Deliverables
- ✅ LEAD_LAG_INDEXING_RESEARCH.md ([X] lines)
- ✅ Grammar design with Lark prototype
- ✅ Semantic validation specification
- ✅ Implementation guide (7-10h effort validated)

## Unknowns Verified
- ✅ 9.1.1: i++1/i--1 complexity
- ✅ 9.1.2: Grammar integration
- ✅ 9.1.3: Semantic handling
- ✅ 9.1.8: himmel16.gms unlock
- ✅ 9.1.10: Test coverage

## Acceptance Criteria
- [x] All 11 acceptance criteria met" \
  --base main
```

**Wait for reviewer comments before proceeding to Task 4.**

---

## Task 4: Research Model Section Syntax (mx/my)

Execute Sprint 9 Prep Task 4 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 847-1050).

### Objective

Research GAMS model section syntax (`model mx / eq1, eq2 /;`) to design grammar rules and semantic handling. Unlock hs62.gms and mingamma.gms (2 models = +20% parse rate).

### Context

**Why This Matters:**
Model sections unlock 2 GAMSLib models with "Medium" risk and 5-6 hour implementation effort. This is a high-ROI feature (20% parse rate improvement for 5-6 hours).

Sprint 8 achieved 40% parse rate. Sprint 9 target is ≥30% (conservative). Model sections help maintain/exceed 40% rate.

**Background:**
- Models group equations for solving
- Syntax: `model <name> / <equation_list> /;`
- Can have multiple models in one file

### What to Do

**1. GAMS Documentation Survey (1.5 hours)**
- Read GAMS User Guide on model declarations
- Catalog syntax variations (simple, explicit equations, multiple models, empty, "all" keyword)
- Identify semantic meaning (grouping only? required before solve?)

**2. GAMSLib Pattern Analysis (1 hour)**
- Analyze hs62.gms model usage (lines, model name, equation list)
- Analyze mingamma.gms model usage
- Search: `grep -r "^model " data/gamslib/*.gms`
- Count occurrences, catalog variations

**3. Grammar Design (1 hour)**
- Design Lark grammar rules for model sections
- Test grammar conflicts ("/" vs division operator)
- Prototype with minimal test cases
- Verify AST structure

**4. Semantic Handler Design (30 min)**
- Design IR representation (ModelDef dataclass)
- Design semantic validation (equation existence, name uniqueness, "all" keyword)
- Design solve statement integration

**5. Test Fixture Design (30 min)**
- Identify 4-5 test cases (simple model, multiple equations, "all" keyword, multiple models, error case)
- Create fixture directory structure

**6. Documentation (30 min)**
- Create MODEL_SECTIONS_RESEARCH.md (400-600 lines)
- Estimate implementation effort (5-8h validates 5-6h estimate)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md` (400-600 lines)
2. GAMS model section syntax catalog (4-6 variations)
3. Lark grammar design for model statements
4. IR representation design (ModelDef dataclass)
5. Semantic validation logic specification
6. Test fixture strategy (4-5 fixtures)
7. hs62.gms and mingamma.gms usage analysis
8. Implementation guide
9. Effort estimate validation (5-8h)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`:**

**Unknown 9.1.4: Model Section Syntax Variations**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: Single vs multiple models, "all" keyword exists, empty sections allowed
- Evidence: GAMSLib pattern counts, hs62/mingamma analysis
- Answer all 5 research questions

**Unknown 9.1.5: Model Section Grammar Conflicts**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: "/" disambiguation strategy (context vs keyword)
- Evidence: Grammar prototype test results
- Decision: Grammar design approach

**Unknown 9.1.9: hs62.gms/mingamma.gms Unlock Dependencies**
- Change status to `✅ VERIFIED` or `❌ WRONG`
- Add findings: Both models use same pattern or different, secondary blockers found
- Evidence: Parse attempt results, model section usage analysis
- Decision: Unlock probability (both, one, or neither)

**Unknown 9.1.10: Advanced Feature Test Coverage**
- Update with model section fixture count (4-5 fixtures)

### Documentation Updates

**1. Update PREP_PLAN.md Task 4:**
- Change status to `✅ COMPLETE`
- Fill in **Changes** and **Result** sections (similar format to Task 3)
- Check off all acceptance criteria (11 items)

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 4 - Research Model Section Syntax - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Completed comprehensive research on GAMS model section syntax. Designed grammar rules and IR representation for model declarations. Analyzed hs62.gms and mingamma.gms to validate 20% parse rate improvement potential.

#### Key Findings
- **Syntax variations:** [count] patterns cataloged
- **hs62.gms analysis:** [model usage details]
- **mingamma.gms analysis:** [model usage details]
- **Unlock probability:** [both/one/neither models will unlock]
- **Implementation effort:** 5-8h validated

#### Unknowns Verified
- 9.1.4: ✅ Model section syntax variations
- 9.1.5: ✅ Grammar conflicts (disambiguation strategy)
- 9.1.9: ✅ hs62/mingamma unlock (probability)
- 9.1.10: ✅ Test coverage ([count] fixtures)
```

### Quality Gates & Commit

Same process as Task 3:
```bash
git checkout -b prep/sprint9-task4-model-sections-research
# ... create deliverables ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 4: Research Model Section Syntax..."
git push -u origin prep/sprint9-task4-model-sections-research
gh pr create --title "Sprint 9 Prep Task 4: Research Model Section Syntax" ...
```

**Wait for reviewer comments before proceeding to Task 5.**

---

## Task 5: Design Conversion Pipeline Architecture

Execute Sprint 9 Prep Task 5 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 1052-1261).

### Objective

Design end-to-end conversion pipeline architecture for transforming parsed GAMS ModelIR into MCP GAMS format. Enable at least 1 simple model (mhw4d or rbrock) to convert successfully.

### Context

**Why This Matters:**
Conversion pipeline is Sprint 9's new infrastructure component with "Medium" risk (6-8 hour effort). This is the first step toward end-to-end GAMS→MCP→PATH workflow. Successful design prevents mid-sprint architecture pivots.

PROJECT_PLAN.md acceptance criterion: "At least 1 model (mhw4d or rbrock) successfully converts end-to-end."

**Background:**
- Parser produces ModelIR (AST + semantic information)
- No conversion infrastructure exists yet
- Goal: ModelIR → MCP GAMS transformation
- Target models: mhw4d.gms (14 lines), rbrock.gms (8 lines)

### What to Do

**1. Architecture Design (2 hours)**
- Define conversion pipeline stages (5 stages: validate, normalize, transform, validate MCP, serialize)
- Choose architecture pattern (single-pass visitor vs multi-pass)
- Design error handling strategy
- Design module structure (`src/conversion/`)

**2. IR-to-MCP Mapping Design (2 hours)**
- Audit current ModelIR coverage
- Design IR-to-MCP mappings (VariableDef → MCP variable, etc.)
- Identify mapping gaps
- Design unsupported feature handling

**3. Simple Model Analysis (1 hour)**
- Analyze mhw4d.gms IR requirements
- Analyze rbrock.gms IR requirements
- Identify conversion blockers
- Estimate conversion coverage (100%? 80%?)

**4. MCP Schema Review (1 hour)**
- Review existing MCP GAMS schema
- Identify GAMS-specific extensions needed
- Design schema validation approach

**5. Test Strategy Design (45 min)**
- Define conversion test levels (unit, integration, schema validation)
- Design test fixtures
- Define acceptance criteria for conversion

**6. Documentation (45 min)**
- Create CONVERSION_PIPELINE_ARCHITECTURE.md (800-1000 lines)
- Create implementation plan (4 phases, 7-8h breakdown)
- Document conversion coverage for mhw4d/rbrock

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md` (800-1000 lines)
2. Architecture design (5-stage pipeline)
3. IR-to-MCP mapping table (all IR nodes mapped)
4. Module structure specification (`src/conversion/`)
5. mhw4d.gms conversion feasibility analysis
6. rbrock.gms conversion feasibility analysis
7. Unsupported feature handling strategy
8. Test strategy (unit, integration, schema validation)
9. Implementation plan (7-8 hour breakdown)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` for ALL conversion unknowns (9.2.1 through 9.2.9):**

**Unknown 9.2.1: Conversion Pipeline Architecture**
- Findings: Single-pass vs multi-pass decision with rationale
- Evidence: Architecture diagram, stage definitions

**Unknown 9.2.2: IR-to-MCP Mapping Coverage**
- Findings: Conversion coverage % for mhw4d/rbrock
- Evidence: Complete IR-to-MCP mapping table

**Unknown 9.2.3: Simple Model Conversion Scope**
- Findings: Which model is simpler (mhw4d or rbrock), can we convert 100%?
- Evidence: IR analysis results

**Unknown 9.2.4: MCP GAMS Schema Compatibility**
- Findings: GAMS extensions needed or not
- Evidence: Schema review results

**Unknown 9.2.5: Conversion Pipeline Testing Strategy**
- Findings: Test levels chosen, PATH integration needed or not
- Decision: Acceptance criteria for "successful conversion"

**Unknown 9.2.6: Conversion Pipeline Error Reporting**
- Findings: Error reporting design (line numbers, actionable suggestions)

**Unknown 9.2.7: Conversion Pipeline Performance**
- Findings: Complexity estimate (O(n)? optimization needed?)

**Unknown 9.2.8: Dashboard Conversion Tracking**
- Findings: Dashboard columns design (parse/convert/solve status)

**Unknown 9.2.9: Conversion Pipeline Incremental Development**
- Findings: Start with mhw4d or rbrock, incremental milestones
- Decision: Checkpoint 4 (Day 8) criteria

### Documentation Updates

**1. Update PREP_PLAN.md Task 5:**
- Change status to `✅ COMPLETE`
- Fill in **Changes**:
  ```
  **Created:**
  - CONVERSION_PIPELINE_ARCHITECTURE.md (X lines)
  
  **Verified:**
  - Unknowns 9.2.1-9.2.9 (all 9 conversion unknowns)
  ```

- Fill in **Result**:
  ```
  **Architecture:**
  - Pattern: [single-pass / multi-pass]
  - Stages: 5 (validate, normalize, transform, validate MCP, serialize)
  
  **IR-to-MCP Mapping:**
  - Coverage: X% for mhw4d, Y% for rbrock
  - Gaps: [list unsupported features]
  
  **Conversion Feasibility:**
  - mhw4d.gms: [can/cannot] convert 100%
  - rbrock.gms: [can/cannot] convert 100%
  - Blocker: [none / list]
  
  **Implementation Effort:**
  - Phase 1: Scaffolding (2h)
  - Phase 2: IR-to-MCP mappings (3h)
  - Phase 3: MCP validation (1h)
  - Phase 4: Tests (1-2h)
  - Total: 7-8h (validates estimate)
  ```

- Check off all acceptance criteria (10 items)

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 5 - Design Conversion Pipeline Architecture - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Designed comprehensive conversion pipeline architecture for ModelIR → MCP GAMS transformation. Analyzed mhw4d.gms and rbrock.gms for conversion feasibility. Created IR-to-MCP mapping table and implementation plan validating 6-8 hour effort estimate.

#### Architecture Design
- **Pattern:** [single-pass visitor / multi-pass]
- **Stages:** 5 (validate IR, normalize, transform to MCP, validate MCP, serialize)
- **Module structure:** src/conversion/ with 4 files
- **Error handling:** [strategy]

#### Conversion Feasibility
- **mhw4d.gms:** [X]% coverage ([can/cannot] convert fully)
- **rbrock.gms:** [Y]% coverage ([can/cannot] convert fully)
- **Target:** At least 1 model converts (acceptance criterion)

#### Unknowns Verified (9 total)
- 9.2.1: ✅ Architecture ([single/multi]-pass)
- 9.2.2: ✅ IR-to-MCP mapping ([X]% coverage)
- 9.2.3: ✅ Simple model scope (feasibility confirmed)
- 9.2.4: ✅ MCP schema ([extensions needed/not needed])
- 9.2.5: ✅ Testing strategy (unit + integration)
- 9.2.6: ✅ Error reporting (line numbers + suggestions)
- 9.2.7: ✅ Performance (O(n), negligible)
- 9.2.8: ✅ Dashboard tracking (3-column design)
- 9.2.9: ✅ Incremental development (start with [rbrock/mhw4d])
```

### Quality Gates & Commit

```bash
git checkout -b prep/sprint9-task5-conversion-architecture
# ... create deliverables ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 5: Design Conversion Pipeline Architecture..."
git push -u origin prep/sprint9-task5-conversion-architecture
gh pr create --title "Sprint 9 Prep Task 5: Design Conversion Pipeline Architecture" ...
```

**Wait for reviewer comments before proceeding to Task 6.**

---

## Task 6: Design Automated Fixture Test Framework

Execute Sprint 9 Prep Task 6 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 1263-1483).

### Objective

Design pytest-based framework to automatically validate all 13 test fixtures (from Sprint 8) against expected_results.yaml. Address Sprint 8 retrospective recommendation #2: "13 fixtures created, 0 automated tests."

### Context

**Why This Matters:**
Sprint 8 retrospective identified this as **High Priority Recommendation #2**: "Create automated fixture tests for regression protection." Without automated tests, fixtures can drift from expected behavior without detection.

**Current Fixture Count:**
- 5 option statement fixtures
- 5 indexed assignment fixtures
- 3 partial parse fixtures
- Total: 13 fixtures

### What to Do

**1. Pytest Framework Design (1 hour)**
- Design fixture discovery mechanism (scan tests/fixtures/ recursively)
- Design parametrized test structure (@pytest.mark.parametrize)
- Design fixture data loading (PyYAML for expected_results.yaml)

**2. Validation Logic Design (1.5 hours)**
- Define validation assertions (parse status, statement count, line count, feature presence)
- Design assertion helpers
- Design error reporting

**3. Test Coverage Design (30 min)**
- Identify validation levels (Level 1-4: status, counts, features, AST)
- Choose validation level for Sprint 9 (recommend Level 1+2)
- Design opt-in for deep validation

**4. Integration with Existing Tests (30 min)**
- Decide test file location (tests/test_fixtures.py)
- Design fixture test markers (@pytest.mark.fixtures)
- Integrate with CI (add to make test)

**5. Documentation (30 min)**
- Create FIXTURE_TEST_FRAMEWORK.md (400-600 lines)
- Update fixture README files with "Automated Testing" section
- Estimate implementation effort (3h validates 2-3h estimate)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/FIXTURE_TEST_FRAMEWORK.md` (400-600 lines)
2. Pytest framework design (fixture discovery, parametrization)
3. Validation logic specification (4 levels)
4. Assertion helper designs (parse status, counts, features)
5. Test file structure (`tests/test_fixtures.py`)
6. CI integration plan
7. Implementation effort estimate (3h breakdown)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`:**

**Unknown 9.3.1: Automated Fixture Test Framework Design**
- Findings: pytest parametrization successful, discovery mechanism chosen
- Evidence: Framework design prototype (pseudocode)
- Decision: Validation level (recommend Level 1+2)

**Unknown 9.3.2: Fixture Test Validation Scope**
- Findings: Level 1+2 sufficient for Sprint 9 (status + counts)
- Rationale: Level 3+4 add 2-3h, defer to Sprint 10
- Decision: Opt-in for deep validation in YAML

### Documentation Updates

**1. Update PREP_PLAN.md Task 6:**
- Status → `✅ COMPLETE`
- Fill in Changes and Result
- Check off all 8 acceptance criteria

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 6 - Design Automated Fixture Test Framework - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Designed pytest-based automated fixture test framework to validate all 13 Sprint 8 fixtures. Framework supports 4 validation levels with Level 1+2 recommended for Sprint 9 (3h implementation).

#### Framework Design
- **Discovery:** Recursive scan of tests/fixtures/
- **Parametrization:** @pytest.mark.parametrize over all fixtures
- **Validation levels:**
  - Level 1: Parse status (SUCCESS/FAILED/PARTIAL)
  - Level 2: Statement/line counts
  - Level 3: Feature presence (option statements, indexed assignments)
  - Level 4: Deep AST structure
- **Recommended:** Level 1+2 for Sprint 9 (3h effort)

#### Unknowns Verified
- 9.3.1: ✅ Framework design (pytest parametrization)
- 9.3.2: ✅ Validation scope (Level 1+2 sufficient)

Addresses Sprint 8 Retrospective Recommendation #2.
```

### Quality Gates & Commit

```bash
git checkout -b prep/sprint9-task6-fixture-framework
# ... create deliverables ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 6: Design Automated Fixture Test Framework..."
git push -u origin prep/sprint9-task6-fixture-framework
gh pr create --title "Sprint 9 Prep Task 6: Design Automated Fixture Test Framework" ...
```

**Wait for reviewer comments before proceeding to Task 7.**

---

## Task 7: Design Fixture Validation Script

Execute Sprint 9 Prep Task 7 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 1485-1716).

### Objective

Design pre-commit validation script (`scripts/validate_fixtures.py`) to prevent manual counting errors in expected_results.yaml. Address Sprint 8 retrospective recommendation #3: "PR #254 had 5 review comments on incorrect counts."

### Context

**Why This Matters:**
Sprint 8 retrospective identified this as **High Priority Recommendation #3**. PR #254 required 5 review comments to fix line number and statement count errors, delaying merge by 1 day.

**Sprint 8 Issue:**
- 3 partial parse fixtures created
- 5 errors in expected_results.yaml (incorrect line numbers, statement counts, percentages)

### What to Do

**1. Statement Counting Algorithm Design (1 hour)**
- Define "statement" for counting (Variable x; = 1, multi-line statements = 1)
- Design line counting algorithm (logical vs physical lines)
- Handle edge cases (multi-line statements, inline comments, $ontext...$offtext)
- Design counting algorithm pseudocode

**2. Validation Logic Design (45 min)**
- Design 4 validation checks (statement count, line count, parse percentage, feature lists)
- Design discrepancy reporting
- Design exit codes (0: valid, 1: errors, 2: script error)

**3. CLI Design (30 min)**
- Design command-line interface (validate all, validate one, --fix mode)
- Design output format (✅/⚠️ per check)
- Design auto-fix behavior (safety, confirmation prompt)

**4. Integration Design (15 min)**
- Design pre-commit hook integration
- Design CI integration (run before fixture tests)

**5. Documentation (30 min)**
- Create FIXTURE_VALIDATION_SCRIPT.md (300-500 lines)
- Estimate implementation effort (2.5h validates 2-3h estimate)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/FIXTURE_VALIDATION_SCRIPT.md` (300-500 lines)
2. Statement counting algorithm specification
3. Line counting algorithm specification
4. Validation logic design (4 checks)
5. CLI design (usage examples, output format)
6. Auto-fix mode design (safety, confirmation)
7. Integration plan (pre-commit, CI)
8. Implementation effort estimate (2.5h breakdown)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`:**

**Unknown 9.3.3: Fixture Validation Script Algorithm**
- Findings: Statement counting heuristic (ends with ; or ..)
- Evidence: Algorithm pseudocode, edge case handling
- Decision: Logical lines (exclude blank/comments)
- Answer all 5 research questions

### Documentation Updates

**1. Update PREP_PLAN.md Task 7:**
- Status → `✅ COMPLETE`
- Fill in Changes and Result
- Check off all 9 acceptance criteria (note: effort updated from 1h to 2-3h per detailed breakdown)

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 7 - Design Fixture Validation Script - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Designed pre-commit validation script to prevent manual counting errors in fixture expected_results.yaml. Script validates statement counts, line counts, parse percentages, and feature lists with auto-fix mode.

#### Script Design
- **Counting algorithm:** Statement = ends with ; or ..
- **Validation checks:** 4 (statements, lines, percentages, features)
- **CLI modes:** Validate all, validate one, --fix (with confirmation)
- **Integration:** Pre-commit hook + CI
- **Implementation effort:** 2.5h

#### Unknown Verified
- 9.3.3: ✅ Algorithm design (heuristic validated)

Addresses Sprint 8 Retrospective Recommendation #3.
```

### Quality Gates & Commit

```bash
git checkout -b prep/sprint9-task7-validation-script
# ... create deliverables ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 7: Design Fixture Validation Script..."
git push -u origin prep/sprint9-task7-validation-script
gh pr create --title "Sprint 9 Prep Task 7: Design Fixture Validation Script" ...
```

**Wait for reviewer comments before proceeding to Task 8.**

---

## Task 8: Research Equation Attributes (.l/.m) Handling

Execute Sprint 9 Prep Task 8 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 1718-1907).

### Objective

Research GAMS equation attributes (.l for level, .m for marginal) to design parsing and storage strategy. This is foundational work for conversion pipeline (equations need attributes for MCP).

### Context

**Why This Matters:**
Equation attributes are part of Sprint 9 Advanced Parser Features (4-6 hour effort). While lower priority than i++1 and model sections, equation attributes are "foundation for conversion pipeline."

**Background:**
- `.l` (level): Equation left-hand side value
- `.m` (marginal): Equation dual value (shadow price)
- Used post-solve to inspect equation values
- Variable attributes (.l, .m, .lo, .up, .fx) already supported in Sprint 8

### What to Do

**1. GAMS Documentation Survey (1 hour)**
- Read GAMS User Guide on equation attributes
- Catalog attribute types (.l, .m, .lo, .up, .scale?)
- Identify semantic constraints (pre-solve vs post-solve, read-only vs writable)

**2. GAMSLib Pattern Analysis (45 min)**
- Search: `grep -r "\\.l" data/gamslib/*.gms | grep -v "variable"`
- Search: `grep -r "\\.m" data/gamslib/*.gms | grep -v "variable"`
- Catalog patterns (display, assignment, expression)
- Identify most common usage

**3. Grammar Design (45 min)**
- Review existing variable attribute grammar (ref_bound rule)
- Design equation attribute grammar extension (reuse ref_bound or new rule?)
- Test grammar conflicts (variable.l vs equation.l disambiguation)

**4. Semantic Handler Design (45 min)**
- Design IR representation (add .l_value, .m_value to EquationDef)
- Design attribute access handling (pre-solve: None? Error? Mock?)
- Design storage strategy (parse and store approach like Sprint 8 options)

**5. Test Fixture Design (30 min)**
- Identify 3-4 test cases (display, assignment, expression, error case)
- Create fixture directory structure

**6. Documentation (30 min)**
- Create EQUATION_ATTRIBUTES_RESEARCH.md (300-500 lines)
- Estimate implementation effort (4-6h validates estimate)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md` (300-500 lines)
2. GAMS equation attribute catalog (.l, .m, others)
3. Grammar design (reuse ref_bound or new rule)
4. Semantic handler design (mock/store approach)
5. IR representation design (EquationDef enhancements)
6. Test fixture strategy (3-4 fixtures)
7. GAMSLib usage pattern analysis
8. Implementation effort estimate (4-6h)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`:**

**Unknown 9.1.6: Equation Attributes Scope**
- Findings: Attribute types cataloged (.l, .m, others?)
- Evidence: GAMS User Guide citations, GAMSLib pattern counts
- Answer all 5 research questions

**Unknown 9.1.7: Equation Attributes Semantic Meaning**
- Findings: Parse and store is sufficient for Sprint 9
- Decision: Mock values for pre-solve access
- Rationale: Full semantic handling deferred to Sprint 10+

**Unknown 9.1.10: Advanced Feature Test Coverage**
- Update with equation attribute fixture count (3-4 fixtures)

### Documentation Updates

**1. Update PREP_PLAN.md Task 8:**
- Status → `✅ COMPLETE`
- Fill in Changes and Result
- Check off all 9 acceptance criteria

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 8 - Research Equation Attributes (.l/.m) - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Completed research on GAMS equation attributes (.l, .m). Designed grammar extension (reuse ref_bound) and IR representation (EquationDef enhancements). Parse-and-store approach validated for Sprint 9 scope.

#### Key Findings
- **Attribute types:** .l (level), .m (marginal), [others if found]
- **Grammar approach:** [Reuse ref_bound / new rule]
- **IR design:** Add .l_value, .m_value to EquationDef
- **Semantic handling:** Parse and store (mock values for pre-solve)
- **Implementation effort:** 4-6h validated

#### Unknowns Verified
- 9.1.6: ✅ Equation attributes scope
- 9.1.7: ✅ Semantic meaning (parse-and-store sufficient)
- 9.1.10: ✅ Test coverage ([count] fixtures)
```

### Quality Gates & Commit

```bash
git checkout -b prep/sprint9-task8-equation-attributes-research
# ... create deliverables ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 8: Research Equation Attributes (.l/.m)..."
git push -u origin prep/sprint9-task8-equation-attributes-research
gh pr create --title "Sprint 9 Prep Task 8: Research Equation Attributes" ...
```

**Wait for reviewer comments before proceeding to Task 9.**

---

## Task 9: Design Performance Baseline & Budget Framework

Execute Sprint 9 Prep Task 9 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 1909-2129).

### Objective

Design performance baseline measurement framework and test suite performance budgets. Address Sprint 8 retrospective recommendation #5: "Establish test suite performance budget on Day 0."

### Context

**Why This Matters:**
Sprint 8 retrospective emphasized "test performance matters throughout sprint." Test optimization on Day 9 benefited Days 1-8 retroactively. Establishing performance budget on Day 0 benefits ALL sprint days.

**Sprint 8 History:**
- Days 1-8: Test suite ran in 120+ seconds (slow feedback)
- Day 9: Reduced to 24 seconds with slow test markers (5x faster)
- Lesson: Performance budget should be Day 0, not Day 9

**Current State:**
- Fast tests: ~24 seconds (1349 tests)
- Full suite: Unknown (not measured)

### What to Do

**1. Performance Metrics Selection (1 hour)**
- Define baseline metrics (test suite timing, per-model parse/convert timing, memory, AST/IR size)
- Choose critical metrics for Sprint 9 (test suite + per-model parse timing)
- Define metric storage format (JSON schema)

**2. Performance Budget Design (45 min)**
- Define budgets (<30s fast tests, <5min full suite, <100ms parse per model)
- Define enforcement strategy (CI failure vs warning)
- Design budget adjustment policy

**3. Benchmark Harness Design (1 hour)**
- Choose benchmarking tool (pytest-benchmark recommended)
- Design benchmark suite structure
- Design benchmark result storage (docs/performance/baselines/)

**4. CI Integration Design (45 min)**
- Design CI performance check workflow (time tests, compare to budget, fail/warn)
- Design performance report format
- Design historical tracking (per-commit data, trend plotting)

**5. Documentation (30 min)**
- Create PERFORMANCE_FRAMEWORK.md (400-600 lines)
- Estimate implementation effort (3.5-4.5h validates 4-5h estimate)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md` (400-600 lines)
2. Performance metrics specification (test suite, parse, convert, memory)
3. Performance budgets (<30s fast, <5min full)
4. Benchmark harness design (pytest-benchmark)
5. Baseline storage format (JSON schema)
6. CI integration plan (performance checks, reporting)
7. Implementation effort estimate (3.5-4.5h)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`:**

**Unknown 9.4.1: Performance Baseline Metrics Selection**
- Findings: Critical metrics chosen (test suite timing, per-model parse timing)
- Evidence: Metric definitions, storage format
- Decision: Memory/AST metrics deferred to Sprint 10

**Unknown 9.4.2: Performance Budget Enforcement**
- Findings: Budget thresholds (<30s, <5min), enforcement strategy
- Evidence: CI workflow design
- Decision: Fail at 100% budget, warn at 90%

### Documentation Updates

**1. Update PREP_PLAN.md Task 9:**
- Status → `✅ COMPLETE`
- Fill in Changes and Result
- Check off all 8 acceptance criteria

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 9 - Design Performance Baseline & Budget Framework - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Designed performance baseline measurement framework and test suite performance budgets. Framework enforces <30s fast tests and <5min full suite budgets from Sprint 9 Day 0.

#### Performance Framework
- **Budgets:** <30s fast tests, <5min full suite, <100ms parse per model
- **Benchmark harness:** pytest-benchmark
- **Baseline storage:** JSON format in docs/performance/baselines/
- **CI integration:** Fail at 100% budget, warn at 90%
- **Implementation effort:** 3.5-4.5h

#### Unknowns Verified
- 9.4.1: ✅ Metrics selection (test suite + parse timing)
- 9.4.2: ✅ Budget enforcement (90%/100% thresholds)

Addresses Sprint 8 Retrospective Recommendation #5.
```

### Quality Gates & Commit

```bash
git checkout -b prep/sprint9-task9-performance-framework
# ... create deliverables ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 9: Design Performance Baseline & Budget Framework..."
git push -u origin prep/sprint9-task9-performance-framework
gh pr create --title "Sprint 9 Prep Task 9: Design Performance Framework" ...
```

**Wait for reviewer comments before proceeding to Task 10.**

---

## Task 10: Plan Sprint 9 Detailed Schedule

Execute Sprint 9 Prep Task 10 from `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (lines 2131-2490).

### Objective

Synthesize all prep work (Tasks 1-9) into comprehensive Sprint 9 execution plan with day-by-day breakdown, 4 checkpoints, effort allocation, quality gates, and risk mitigation.

### Context

**Why This Matters:**
Sprint 9 is the most complex sprint to date: advanced parser features (grammar changes), new pipeline stage (conversion infrastructure), and test infrastructure improvements. Comprehensive planning prevents mid-sprint pivots and scope creep.

Sprint 8 PLAN.md was 1715 lines with 4 checkpoints, all passed on schedule. Sprint 9 PLAN.md should match that level of detail.

**Sprint 9 Goals:**
1. Parse rate: 40% → ≥30% baseline (maintain with advanced features)
2. Advanced features: i++1 indexing, model sections, equation attributes
3. Conversion pipeline: At least 1 model converts end-to-end
4. Test infrastructure: Automated fixtures, validation script, secondary blocker analysis
5. Performance: Baseline + budgets

### What to Do

**1. Executive Summary (1 hour)**
- Write Sprint 9 overview (goals, differences from Sprint 8, prep summary, critical path)
- Synthesize prep task findings (Tasks 1-9 results)

**2. Day-by-Day Breakdown (3 hours)**
- Define Sprint 9 schedule (10-11 days, Days 0-10)
- Day 0: Sprint planning & setup (2-3h)
- Days 1-2: Test Infrastructure (5-6h) → Checkpoint 1
- Days 3-4: Advanced Indexing (8-10h) → Checkpoint 2
- Days 5-6: Model Sections + Equation Attributes (9-12h) → Checkpoint 3
- Days 7-8: Conversion Pipeline (6-8h) → Checkpoint 4
- Day 9: Dashboard + Performance (4-5h)
- Day 10: Documentation, PR, Closeout (2-3h) - BUFFER DAY
- For each day: objectives, tasks with time estimates, quality gates, deliverables

**3. Checkpoint Definitions (1.5 hours)**
- Checkpoint 1 (Day 2 End): Test Infrastructure Complete
  - Success criteria: mhw4dx blocker documented, fixtures automated, validation script working, budgets established
  - Go/No-Go decision
- Checkpoint 2 (Day 4 End): i++1 Indexing Working
  - Success criteria: himmel16.gms parses, parse rate ≥40%
- Checkpoint 3 (Day 6 End): All Parser Features Complete
  - Success criteria: hs62/mingamma parse, parse rate ≥60%
- Checkpoint 4 (Day 8 End): Conversion Pipeline Working
  - Success criteria: 1 model converts, MCP GAMS validates

**4. Effort Allocation (1 hour)**
- Validate 30-41 hour budget (sum components)
- Identify critical path (Tasks 1 → 2 → 3 → 5 → 10)
- Allocate buffer (Day 10)

**5. Risk Mitigation (1 hour)**
- Identify Sprint 9 risks (5+ risks)
- For each risk: Mitigation + Contingency
- Examples:
  - i++1 more complex than 8-10h → Use Day 10 buffer
  - Conversion pipeline blocks on IR gaps → Document gaps, defer to Sprint 10

**6. Quality Gates (30 min)**
- Define continuous quality gates (all days: make test passes, typecheck, lint, format)
- Define feature-specific quality gates (Day 2: fixtures validated, Day 4: himmel16 parses, etc.)

**7. Deliverables & Acceptance Criteria (30 min)**
- Compile all Sprint 9 deliverables from PROJECT_PLAN.md + Tasks 1-9
- Compile all acceptance criteria

**8. Cross-References & Appendices (1 hour)**
- Create cross-reference table (prep tasks → sprint days)
- Appendices: Quality gates, Sprint 9 vs 8 comparison, lessons, dependencies

**9. Document Writing (1 hour)**
- Write complete PLAN.md (target 1500-2000 lines, similar to Sprint 8's 1715)
- Final review (verify all day breakdowns, checkpoints, effort sums, cross-references)

### Deliverables

1. `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (1500-2000 lines)
2. Executive summary (goals, strategy, prep summary, critical path)
3. Day-by-day breakdown (Days 0-10, each with objectives, tasks, quality gates)
4. 4 checkpoint definitions with go/no-go criteria
5. Effort allocation table (30-41h validated)
6. Risk register (5+ risks with mitigation)
7. Quality gates (continuous + feature-specific)
8. Deliverables section (compiled from PROJECT_PLAN + Tasks 1-9)
9. Acceptance criteria (compiled)
10. Cross-reference table (prep tasks → sprint days)
11. Appendices (quality gates, comparison, lessons, dependencies)

### Unknown Verification

**Update `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`:**

**Unknown 9.5.1: 30-41 Hour Budget Allocation**
- Findings: Effort summation (test infra 5-6h + parser 15-20h + conversion 10-15h = 34-44h)
- Evidence: Component breakdown, critical path analysis
- Decision: Budget validated, Day 10 buffer sufficient

**Unknown 9.5.2: Checkpoint Strategy**
- Findings: 4 checkpoints sufficient (Days 2, 4, 6, 8)
- Evidence: Checkpoint success criteria defined
- Decision: Go/No-Go criteria for each checkpoint

### Documentation Updates

**1. Update PREP_PLAN.md Task 10:**
- Status → `✅ COMPLETE`
- Fill in **Changes**:
  ```
  **Created:**
  - docs/planning/EPIC_2/SPRINT_9/PLAN.md (X lines)
  
  **Verified:**
  - Unknown 9.5.1: Budget allocation (34-44h validated)
  - Unknown 9.5.2: Checkpoint strategy (4 checkpoints sufficient)
  ```

- Fill in **Result**:
  ```
  **Sprint 9 Schedule:**
  - Duration: 11 days (Days 0-10)
  - Critical path: 18-24h (fits in 10 days at 2-3h/day)
  - Buffer: Day 10 (2-3h capacity for overruns)
  
  **Checkpoint Strategy:**
  - Checkpoint 1 (Day 2): Test infrastructure complete
  - Checkpoint 2 (Day 4): i++1 indexing working, himmel16 parses
  - Checkpoint 3 (Day 6): All parser features, hs62/mingamma parse
  - Checkpoint 4 (Day 8): Conversion pipeline, 1 model converts
  
  **Effort Allocation:**
  - Test infrastructure: 5-6h
  - Advanced indexing: 8-10h
  - Model sections + equation attributes: 9-12h
  - Conversion: 6-8h
  - Dashboard + performance: 4-5h
  - Documentation: 2-3h
  - Total: 34-44h (aligns with 30-41h estimate)
  
  **Risk Mitigation:**
  - 5 risks identified with mitigation + contingency
  - Day 10 buffer handles critical path overruns
  ```

- Check off all 12 acceptance criteria

**2. Update CHANGELOG.md:**
```markdown
### Sprint 9: Prep Task 10 - Plan Sprint 9 Detailed Schedule - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Synthesized all prep work (Tasks 1-9) into comprehensive Sprint 9 execution plan. Created day-by-day breakdown with 4 checkpoints, effort allocation, quality gates, and risk mitigation. PLAN.md totals [X] lines matching Sprint 8's level of detail.

#### Sprint 9 Schedule
- **Duration:** 11 days (Days 0-10, Day 10 as buffer)
- **Checkpoints:** 4 (Days 2, 4, 6, 8) with go/no-go criteria
- **Effort:** 34-44h validated (aligns with 30-41h estimate)
- **Critical path:** 18-24h (Test infra → i++1 → Conversion → Closeout)

#### Day-by-Day Breakdown
- **Day 0:** Sprint planning & setup (2-3h)
- **Days 1-2:** Test infrastructure (5-6h) → Checkpoint 1
- **Days 3-4:** i++1 indexing (8-10h) → Checkpoint 2
- **Days 5-6:** Model sections + equation attributes (9-12h) → Checkpoint 3
- **Days 7-8:** Conversion pipeline (6-8h) → Checkpoint 4
- **Day 9:** Dashboard + performance (4-5h)
- **Day 10:** Documentation, PR, closeout (2-3h buffer)

#### Unknowns Verified
- 9.5.1: ✅ Budget allocation (34-44h validated)
- 9.5.2: ✅ Checkpoint strategy (4 checkpoints sufficient)

**All Sprint 9 Prep Tasks Complete (1-10).** Ready for Sprint 9 execution.
```

### Quality Gates & Commit

```bash
git checkout -b prep/sprint9-task10-detailed-schedule
# ... create PLAN.md (1500-2000 lines) ...
make typecheck && make lint && make format && make test
git commit -m "Complete Sprint 9 Prep Task 10: Plan Sprint 9 Detailed Schedule

Comprehensive Sprint 9 execution plan synthesizing all prep work.

Sprint 9 schedule:
- 11 days (Days 0-10, Day 10 as buffer)
- 4 checkpoints (Days 2, 4, 6, 8) with go/no-go criteria
- Effort: 34-44h validated (aligns with 30-41h estimate)

Day-by-day breakdown:
- Day 0: Sprint planning (2-3h)
- Days 1-2: Test infrastructure (5-6h) → Checkpoint 1
- Days 3-4: i++1 indexing (8-10h) → Checkpoint 2
- Days 5-6: Model sections + eq attrs (9-12h) → Checkpoint 3
- Days 7-8: Conversion pipeline (6-8h) → Checkpoint 4
- Day 9: Dashboard + performance (4-5h)
- Day 10: Documentation, PR, closeout (2-3h buffer)

Deliverables:
- PLAN.md ([X] lines)
- 4 checkpoint definitions with go/no-go criteria
- Risk register (5+ risks with mitigation)
- Quality gates (continuous + feature-specific)
- Cross-reference tables
- 4 appendices

Verified unknowns:
- 9.5.1: Budget allocation ✅
- 9.5.2: Checkpoint strategy ✅

All Sprint 9 Prep Tasks Complete (1-10).
All acceptance criteria met."
git push -u origin prep/sprint9-task10-detailed-schedule
gh pr create --title "Sprint 9 Prep Task 10: Plan Sprint 9 Detailed Schedule" \
  --body "Completes Sprint 9 Prep Task 10 from PREP_PLAN.md.

## Summary
Comprehensive Sprint 9 execution plan (PLAN.md, [X] lines) synthesizing all prep work from Tasks 1-9.

## Sprint 9 Schedule
- **Duration:** 11 days (Days 0-10)
- **Checkpoints:** 4 with clear go/no-go criteria
- **Effort:** 34-44h (validated against 30-41h estimate)

## Day-by-Day Breakdown
- Day 0: Sprint planning & setup
- Days 1-2: Test infrastructure → Checkpoint 1
- Days 3-4: i++1 indexing → Checkpoint 2
- Days 5-6: Model sections + eq attrs → Checkpoint 3
- Days 7-8: Conversion pipeline → Checkpoint 4
- Day 9: Dashboard + performance
- Day 10: Documentation, PR, closeout (buffer)

## Deliverables
- ✅ PLAN.md ([X] lines)
- ✅ 4 checkpoint definitions
- ✅ Risk register (5+ risks)
- ✅ Quality gates
- ✅ Cross-references
- ✅ 4 appendices

## Unknowns Verified
- ✅ 9.5.1: Budget allocation
- ✅ 9.5.2: Checkpoint strategy

## Acceptance Criteria
- [x] All 12 acceptance criteria met

**All Sprint 9 Prep Tasks Complete (1-10). Ready for Sprint 9 execution.**" \
  --base main
```

**Wait for reviewer comments. After approval, Sprint 9 Prep Phase is COMPLETE.**

---

## Summary

All 9 task prompts (Tasks 2-10) are now ready to use. Each prompt includes:

✅ Full task objectives and deliverables from PREP_PLAN.md
✅ Instructions to verify associated Known Unknowns
✅ Instructions to update PREP_PLAN.md (status, Changes, Result, acceptance criteria)
✅ Instructions to update CHANGELOG.md
✅ Quality gates (make typecheck && make lint && make format && make test)
✅ Commit message format
✅ Instructions to create PR with gh and wait for reviewer comments

**Usage:** Copy the prompt for each task and execute sequentially (Task 2 → Task 3 → ... → Task 10).
