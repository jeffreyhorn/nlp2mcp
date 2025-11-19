# Sprint 9 Preparation Plan

**Sprint:** Epic 2 - Sprint 9 (Advanced Parser Features & Conversion Pipeline)  
**Duration:** Weeks 7-8  
**Version:** v0.9.0  
**Strategy:** Advanced features + conversion infrastructure + Test infrastructure improvements

---

## Executive Summary

Sprint 9 focuses on **advanced parser features requiring grammar changes** and **beginning conversion pipeline work**. This sprint builds on Sprint 8's foundation (40% parse rate) while incorporating Sprint 8 retrospective recommendations to strengthen test infrastructure.

**Sprint 9 Goals:**
1. **Parse Rate:** 40% → ≥30% baseline (maintain/improve with advanced features)
2. **Advanced Parser Features:** i++1/i--1 indexing, model sections (mx syntax), equation attributes
3. **Conversion Pipeline:** Convert at least 1 model (mhw4d or rbrock) end-to-end
4. **Test Infrastructure:** Automated fixtures, validation script, secondary blocker analysis
5. **Performance:** Baseline benchmarks + performance budgets (<30s fast, <5min full)

**Key Differences from Sprint 8:**
- **Higher complexity features** (grammar changes vs semantic handling)
- **New pipeline stage** (conversion infrastructure vs parser-only work)
- **Test infrastructure first** (Sprint 8 lesson: address gaps early)
- **Complete blocker analysis** (Sprint 8 lesson: prevent underestimation)

**Preparation Effort:** 47-63 hours (~6-8 working days)  
**Critical Path:** Tasks 1 → 2 → 3 → 5 → 10

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|------------------------|
| 1 | Create Sprint 9 Known Unknowns List | Critical | 5-7 hours | None | Proactive risk management |
| 2 | Complete Secondary Blocker Analysis for mhw4dx.gms | Critical | 2-3 hours | Task 1 | Test infrastructure (Sprint 8 retro) |
| 3 | Research Advanced Indexing (i++1, i--1) Syntax | Critical | 6-8 hours | Task 1 | Advanced indexing implementation |
| 4 | Research Model Section Syntax (mx/my) | High | 4-5 hours | Task 1 | Model sections implementation |
| 5 | Design Conversion Pipeline Architecture | Critical | 5-7 hours | Task 1 | Conversion pipeline foundation |
| 6 | Design Automated Fixture Test Framework | High | 3-4 hours | Task 1 | Test infrastructure (Sprint 8 retro) |
| 7 | Design Fixture Validation Script | High | 2-3 hours | Task 6 | Test infrastructure (Sprint 8 retro) |
| 8 | Research Equation Attributes (.l/.m) Handling | Medium | 3-4 hours | Task 1 | Equation attributes parsing |
| 9 | Design Performance Baseline & Budget Framework | Medium | 3-4 hours | Task 1 | Performance instrumentation |
| 10 | Plan Sprint 9 Detailed Schedule | Critical | 7-9 hours | All tasks | Sprint 9 execution planning |

**Total Estimated Time:** 40-54 hours (~5-7 working days) for main tasks + 7-9 hours for Task 10 = **47-63 hours total**

**Critical Path:** Tasks 1 → 2 → 3 → 5 → 10 (must complete before Sprint 9 Day 1)

---

## Task 1: Create Sprint 9 Known Unknowns List

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 5-7 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Identify and document all known unknowns for Sprint 9 across advanced parser features, conversion pipeline architecture, and test infrastructure improvements. Proactively address risks before they block sprint execution.

### Why This Matters

Sprint 9 introduces higher-complexity work than Sprint 8: grammar changes (vs semantic handling), new pipeline stages (vs parser-only), and advanced indexing operators. Sprint 8 retrospective emphasized complete blocker analysis to prevent underestimation (mhw4dx.gms lesson).

**Key questions:**
- How complex is i++1/i--1 lead/lag indexing semantic handling?
- What's the conversion pipeline architecture for IR-to-MCP transformation?
- Which models can convert successfully with current IR coverage?
- How to automate fixture validation without manual counting?
- What performance baseline metrics matter for parse/convert times?

### Background

Sprint 8 Known Unknowns doc had 27 unknowns across 8 categories, all verified before execution. Sprint 9 has different focus areas:
- **Advanced Parser Features:** i++1/i--1 indexing (8-10h), model sections (5-6h), equation attributes (4-6h)
- **Conversion Pipeline:** New infrastructure for IR-to-MCP transformation (6-8h)
- **Test Infrastructure:** Automated fixtures (2-3h), validation script (1h), secondary blocker analysis (2-3h)
- **Performance:** Baseline harness (3-4h) + budgets (1h)

From Sprint 8 retrospective (`docs/planning/EPIC_2/SPRINT_8/RETROSPECTIVE.md` lines 362-412):
- "Complete secondary blocker analysis for mhw4dx.gms (2-3 hours)" - High Priority #1
- "Implement automated fixture tests (2-3 hours)" - High Priority #2
- "Add fixture validation script (1 hour)" - High Priority #3
- "Establish test suite performance budget" - Medium Priority #5

From PROJECT_PLAN.md Sprint 9 section (lines 162-282):
- Risk: "Medium-High (requires grammar changes, semantic complexity)" for i++1 indexing
- Risk: "Medium (new pipeline stage)" for conversion pipeline
- Parse rate target: ≥30% (conservative, down from Sprint 8's 40% to account for complexity)

### What Needs to Be Done

**1. Parser Enhancement Unknowns (10-12 unknowns expected)**

1.1. **i++1/i--1 Lead/Lag Indexing Complexity**
   - Assumption: 8-10 hour estimate for grammar + semantic handling
   - Verification: Survey GAMS documentation for all lead/lag operator variations
   - Questions:
     - Does i++1 only work in time-indexed sets, or general sets?
     - How to handle i++1 at set boundaries (wrap-around vs error)?
     - Are there i++2, i++N patterns to support?
     - Can lead/lag combine with other indexing (i++1, j--1)?
   - Priority: Critical (blocks advanced indexing implementation)

1.2. **i++1/i--1 Grammar Integration**
   - Assumption: Lark can parse i++1 as terminal + operator + number
   - Verification: Prototype grammar rule for lead/lag operators
   - Questions:
     - Precedence of ++ vs other operators?
     - Conflicts with existing index_expr rules?
     - How to distinguish i++1 (lead/lag) from i + +1 (addition)?
   - Priority: Critical (affects grammar design)

1.3. **i++1/i--1 Semantic Handling**
   - Assumption: Semantic handler translates i++1 to offset calculation
   - Verification: Design IR representation for lead/lag indexing
   - Questions:
     - Store as IndexOffset(base='i', offset=1)?
     - How to validate offset doesn't exceed set bounds?
     - How to handle circular sets (time indices)?
   - Priority: High (affects IR design)

1.4. **Model Section Syntax Variations**
   - Assumption: Model sections use "mx / eq1, eq2 /;" syntax
   - Verification: Catalog all model section patterns in GAMSLib
   - Questions:
     - Single model vs multiple models per file?
     - Model declarations vs model definitions?
     - Empty model sections allowed?
     - Model sections with solve statements?
   - Priority: High (affects model section scope)

1.5. **Model Section Grammar Conflicts**
   - Assumption: Can extend existing model_stmt rule
   - Verification: Check for grammar conflicts with equation sets
   - Questions:
     - How to distinguish "model m / all /" from "set s / all /"?
     - Precedence of model sections vs equation declarations?
   - Priority: Medium (grammar extension)

1.6. **Equation Attributes Scope**
   - Assumption: .l and .m attributes are most common
   - Verification: Catalog all equation attribute types in GAMS
   - Questions:
     - Beyond .l (level) and .m (marginal), what else? (.lo, .up, .scale?)
     - Equation attributes vs variable attributes?
     - Where can equation attributes appear (RHS only? LHS?)?
   - Priority: Medium (affects attribute parsing scope)

1.7. **Equation Attributes Semantic Meaning**
   - Assumption: "Parse and store" is sufficient (like Sprint 8 option statements)
   - Verification: Understand semantic difference between pre-solve and post-solve attributes
   - Questions:
     - Are .l/.m values meaningful before solve?
     - How to handle attribute access in pre-solve context?
     - Store as mock values or validate usage?
   - Priority: Low (semantic handling)

1.8. **himmel16.gms Unlock Probability**
   - Assumption: i++1 indexing alone unlocks himmel16.gms
   - Verification: Parse himmel16.gms with i++1 support, check for secondary blockers
   - Questions:
     - After i++1, what's the next error?
     - Is i++1 the ONLY blocker, or one of many?
   - Priority: High (affects parse rate target)

1.9. **hs62.gms/mingamma.gms Unlock Dependencies**
   - Assumption: Model sections (mx syntax) unlocks both models
   - Verification: Parse both models with model section support
   - Questions:
     - Do both models use same model section pattern?
     - Any secondary blockers after model sections?
   - Priority: High (affects parse rate target)

1.10. **Advanced Feature Test Coverage**
   - Assumption: Can create 3-5 fixtures per feature (similar to Sprint 8)
   - Verification: Estimate fixture count for i++1, model sections, equation attributes
   - Questions:
     - How many i++1 variations to test (i++1, i--1, nested, boundaries)?
     - How many model section patterns (single, multiple, empty)?
   - Priority: Medium (affects test strategy)

**2. Conversion Pipeline Unknowns (8-10 unknowns expected)**

2.1. **Conversion Pipeline Architecture**
   - Assumption: Pipeline takes ModelIR → MCP JSON in single pass
   - Verification: Design conversion stages (IR → intermediate → MCP)
   - Questions:
     - Single-pass or multi-pass conversion?
     - Intermediate representations needed?
     - Error handling strategy for unsupported IR nodes?
   - Priority: Critical (architecture decision)

2.2. **IR-to-MCP Mapping Coverage**
   - Assumption: Current IR covers mhw4d.gms and rbrock.gms fully
   - Verification: Audit IR nodes vs MCP requirements for simple models
   - Questions:
     - Which IR nodes have no MCP equivalent yet?
     - Which MCP fields require new IR data?
     - What's the conversion coverage % for parsed models?
   - Priority: Critical (affects conversion feasibility)

2.3. **Simple Model Conversion Scope**
   - Assumption: mhw4d.gms and rbrock.gms are "simple enough" to convert
   - Verification: Analyze both models for conversion blockers
   - Questions:
     - Do they use any features not yet in IR?
     - Do they require runtime evaluation (beyond IR scope)?
     - Can we convert without solving?
   - Priority: High (acceptance criterion: "at least 1 model converts")

2.4. **MCP JSON Schema Compatibility**
   - Assumption: Existing MCP schema handles all GAMS constructs
   - Verification: Review MCP schema for GAMS-specific extensions needed
   - Questions:
     - Does MCP support GAMS-style sets with aliases?
     - Does MCP support GAMS-style parameters with multi-dimensional indices?
     - Does MCP require variable bounds in specific format?
   - Priority: High (affects conversion implementation)

2.5. **Conversion Pipeline Testing Strategy**
   - Assumption: Can validate conversion with PATH solver integration
   - Verification: Design test approach without PATH (JSON validation only?)
   - Questions:
     - How to test conversion correctness without solving?
     - Can we use finite differencing to validate gradients?
     - What's the acceptance criterion for "successful conversion"?
   - Priority: High (affects testing approach)

2.6. **Conversion Pipeline Error Reporting**
   - Assumption: Can report conversion errors with line number context
   - Verification: Design error reporting for unsupported IR nodes
   - Questions:
     - Where to store source location in conversion errors?
     - How to make errors actionable (suggest workarounds)?
   - Priority: Medium (UX consideration)

2.7. **Conversion Pipeline Performance**
   - Assumption: Conversion time is negligible vs parsing time
   - Verification: Estimate conversion complexity (linear in IR size?)
   - Questions:
     - Does conversion require optimization passes?
     - What's the expected conversion time for 100-line models?
   - Priority: Low (optimization concern)

2.8. **Dashboard Conversion Tracking**
   - Assumption: Can extend dashboard to show parse/convert/solve rates
   - Verification: Design dashboard columns for conversion status
   - Questions:
     - How to display "parses but doesn't convert" vs "converts but doesn't solve"?
     - Color coding for 3-stage pipeline (parse → convert → solve)?
   - Priority: Medium (dashboard enhancement)

2.9. **Conversion Pipeline Incremental Development**
   - Assumption: Can build conversion pipeline incrementally (mhw4d first, then rbrock)
   - Verification: Identify shared vs model-specific conversion logic
   - Questions:
     - What's common across all models vs model-specific?
     - Can we ship "partial conversion" (e.g., constraints only)?
   - Priority: Medium (development strategy)

**3. Test Infrastructure Unknowns (6-8 unknowns expected)**

3.1. **Automated Fixture Test Framework Design**
   - Assumption: pytest can iterate over fixture directories automatically
   - Verification: Prototype pytest fixture discovery pattern
   - Questions:
     - How to auto-discover all fixture directories?
     - How to parameterize tests per fixture?
     - How to load expected_results.yaml for assertions?
   - Priority: High (Sprint 8 retro recommendation #2)

3.2. **Fixture Test Validation Scope**
   - Assumption: Validate parse status, statement counts, line numbers
   - Verification: Define complete validation checklist per fixture
   - Questions:
     - Validate AST structure (deep comparison)?
     - Validate IR nodes (specific types)?
     - Validate semantic accuracy (variable values)?
   - Priority: High (acceptance criterion completeness)

3.3. **Fixture Validation Script Algorithm**
   - Assumption: Can count statements and line numbers programmatically
   - Verification: Design statement counting algorithm (what's a "statement"?)
   - Questions:
     - Count declarations separately from assignments?
     - Count multi-line statements as 1 or N?
     - How to validate expected_results.yaml accuracy?
   - Priority: High (Sprint 8 retro recommendation #3)

3.4. **Fixture Validation Script Usage**
   - Assumption: Run validation script before PR creation
   - Verification: Design pre-commit hook integration
   - Questions:
     - Fail PR if validation errors found?
     - Auto-update expected_results.yaml vs fail?
     - How to handle false positives (legitimate changes)?
   - Priority: Medium (workflow integration)

3.5. **Secondary Blocker Analysis Methodology**
   - Assumption: Parse mhw4dx.gms, capture ALL errors, not just first
   - Verification: Design error collection strategy (Lark error recovery?)
   - Questions:
     - Can Lark continue parsing after first error?
     - How many errors constitute "complete analysis"?
     - Document errors in GAMSLIB_FEATURE_MATRIX.md or separate file?
   - Priority: Critical (Sprint 8 retro recommendation #1)

3.6. **Secondary Blocker Priority**
   - Assumption: Secondary blockers are lower priority than primary
   - Verification: Analyze if secondary blockers are easier/harder than primary
   - Questions:
     - Are secondary blockers simpler features (overlooked) or harder (deferred)?
     - Should Sprint 9 address secondary blockers if time permits?
   - Priority: Medium (sprint scope consideration)

3.7. **Test Suite Performance Budget Enforcement**
   - Assumption: CI can enforce <30s fast, <5min full suite budgets
   - Verification: Design CI integration for performance budget checks
   - Questions:
     - Fail CI if budget exceeded by X%? (10%? 20%?)
     - How to identify slow tests automatically?
     - Performance budget per test file or total?
   - Priority: Medium (Sprint 8 retro recommendation #5)

**4. Performance & Metrics Unknowns (4-6 unknowns expected)**

4.1. **Performance Baseline Metrics Selection**
   - Assumption: Measure parse time, convert time, total time
   - Verification: Define complete metric set for baseline
   - Questions:
     - Per-model metrics or aggregate?
     - Include memory usage?
     - Include AST/IR size metrics?
   - Priority: High (baseline definition)

4.2. **Performance Benchmark Harness Design**
   - Assumption: Can reuse existing test infrastructure for benchmarking
   - Verification: Design benchmark runner (pytest-benchmark? custom?)
   - Questions:
     - How many iterations per benchmark?
     - Warmup runs needed?
     - Statistical significance thresholds?
   - Priority: Medium (benchmark infrastructure)

4.3. **Performance Baseline Storage**
   - Assumption: Store baselines in JSON for regression tracking
   - Verification: Design baseline storage format
   - Questions:
     - Per-commit baselines or milestone baselines?
     - Where to store (docs/ or separate perf/ directory)?
     - How to compare baselines (% change threshold)?
   - Priority: Medium (regression tracking)

4.4. **Performance Budget Monitoring**
   - Assumption: CI can report test timing automatically
   - Verification: Design CI integration for timing reports
   - Questions:
     - Per-test timing or total suite timing?
     - Alert on budget violations?
     - Historical timing trends?
   - Priority: Medium (CI integration)

4.5. **Dashboard Performance Display**
   - Assumption: Can extend dashboard to show parse/convert times
   - Verification: Design dashboard columns for timing data
   - Questions:
     - Show absolute times or relative to baseline?
     - Color code slow models (>Xms)?
   - Priority: Low (dashboard enhancement)

**5. Sprint Planning Unknowns (3-4 unknowns expected)**

5.1. **30-41 Hour Budget Allocation**
   - Assumption: 5-6h test infra + 15-20h parser + 10-15h conversion = 30-41h
   - Verification: Sum of component estimates aligns with total
   - Questions:
     - Is 8-10h for i++1 indexing realistic (vs 6-8h)?
     - Is 6-8h for conversion pipeline realistic for first model?
   - Priority: High (budget validation)

5.2. **Checkpoint Strategy**
   - Assumption: 4 checkpoints like Sprint 8 (Days 2, 4, 8, 9)
   - Verification: Define Sprint 9 checkpoint criteria
   - Questions:
     - Checkpoint 1: Test infrastructure complete?
     - Checkpoint 2: i++1 indexing working?
     - Checkpoint 3: Conversion pipeline foundation complete?
     - Checkpoint 4: At least 1 model converts?
   - Priority: High (sprint execution planning)

5.3. **Parse Rate Target Achievability**
   - Assumption: ≥30% (3/10 models) with advanced features
   - Verification: Model unlock analysis (which models need which features?)
   - Questions:
     - Does i++1 unlock himmel16.gms only, or multiple?
     - Does model sections unlock hs62.gms + mingamma.gms (2 models)?
     - What's the realistic parse rate after Sprint 9? 40%? 50%?
   - Priority: High (target validation)

5.4. **Sprint 9 vs Sprint 10 Boundary**
   - Assumption: Sprint 9 = advanced features, Sprint 10 = simplification
   - Verification: Confirm feature split based on complexity
   - Questions:
     - Should Sprint 9 include any Sprint 10 prep work?
     - Should conversion pipeline continue in Sprint 10?
   - Priority: Medium (scope clarification)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify KNOWN_UNKNOWNS.md exists and has all categories
ls -la docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md

# Count unknowns by category
grep -c "^#### Unknown 9.1." docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md  # Parser unknowns
grep -c "^#### Unknown 9.2." docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md  # Conversion unknowns
grep -c "^#### Unknown 9.3." docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md  # Test infra unknowns
grep -c "^#### Unknown 9.4." docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md  # Performance unknowns
grep -c "^#### Unknown 9.5." docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md  # Sprint planning unknowns

# Verify all unknowns have verification status
grep -c "**Status:**" docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md

# Should have 31-40 unknowns total (10-12 + 8-10 + 6-8 + 4-6 + 3-4)
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (1,500-2,000 lines)
- 31-40 documented unknowns across 5 categories
- Each unknown with: description, verification approach, priority, status (🔵/🟡/🟢)
- Cross-references to Sprint 8 retrospective, PROJECT_PLAN.md, GAMSLib models

### Acceptance Criteria

- [ ] KNOWN_UNKNOWNS.md created with all 5 categories
- [ ] Parser Enhancement Unknowns: 10-12 unknowns documented
- [ ] Conversion Pipeline Unknowns: 8-10 unknowns documented
- [ ] Test Infrastructure Unknowns: 6-8 unknowns documented
- [ ] Performance & Metrics Unknowns: 4-6 unknowns documented
- [ ] Sprint Planning Unknowns: 3-4 unknowns documented
- [ ] Each unknown has clear verification approach
- [ ] Critical unknowns identified for Task 2-9 dependencies
- [ ] Cross-references to Sprint 8 retrospective recommendations (lines 362-412)
- [ ] Total unknown count: 31-40

---

## Task 2: Complete Secondary Blocker Analysis for mhw4dx.gms

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknown 9.3.5: Secondary Blocker Analysis Methodology)

### Objective

Identify ALL blockers (not just primary) preventing mhw4dx.gms from parsing. Update `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` with complete findings to prevent Sprint 8-style underestimation.

### Why This Matters

Sprint 8 retrospective identified this as **High Priority Recommendation #1** (lines 366-373): "Sprint 8 assumed option statements alone would unlock mhw4dx.gms, but secondary blockers exist." Complete blocker analysis prevents underestimation and enables accurate Sprint 9/10 planning.

From Sprint 8 retrospective (lines 366-373):
> **1. Complete Secondary Blocker Analysis for mhw4dx.gms**
> - **Effort:** 2-3 hours
> - **Goal:** Identify ALL features needed for mhw4dx.gms to parse
> - **Approach:** 
>   - Manual inspection of mhw4dx.gms lines 37-63
>   - Parse with current parser, capture ALL errors (not just first)
>   - Document: "Primary blocker: option statements. Secondary blocker: [TBD]"
> - **Impact:** Accurate Sprint 9 planning for mhw4dx.gms unlock

### Background

mhw4dx.gms status:
- **Current Parse Status:** FAILED (partial parse ~51% per Sprint 8 dashboard)
- **Primary Blocker:** Option statements (✅ RESOLVED in Sprint 8)
- **Secondary Blocker:** Unknown (this task identifies it)
- **Lines to Analyze:** 37-63 (post-option-statement errors)

Sprint 8 Feature Matrix (`docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md`) shows:
- mhw4dx.gms: "Primary blocker: option statements"
- No secondary blocker analysis performed
- Parse progress: 51% (27/53 lines)

PROJECT_PLAN.md Sprint 9 Test Infrastructure (lines 175-181):
> **Secondary Blocker Analysis for mhw4dx.gms (2-3 hours)**
> - Manual inspection of mhw4dx.gms lines 37-63 to identify ALL blockers
> - Parse with current parser, capture ALL errors (not just first)
> - Document: "Primary blocker: option statements ✅. Secondary blocker: [TBD]"
> - Update GAMSLIB_FEATURE_MATRIX.md with complete findings

### What Needs to Be Done

**1. Current State Verification (15 minutes)**

1.1. Re-parse mhw4dx.gms with Sprint 8 parser (option statements enabled)
   - Verify option statements parse correctly (lines 37, 47)
   - Capture first error after option statements
   - Record line number and error message

1.2. Verify Sprint 8 dashboard partial metrics
   - Confirm 51% parse progress (27/53 lines)
   - Identify where parsing stops (line 28? line 48?)

**2. Complete Error Capture (30 minutes)**

2.1. Parse mhw4dx.gms with error recovery (if Lark supports)
   - Try `lark.Lark(parser='lalr', propagate_positions=True, maybe_placeholders=True)`
   - Collect all syntax errors, not just first
   - Record: line number, error type, error message, source context

2.2. Manual inspection of lines 37-63
   - Line-by-line review of all constructs
   - Catalog: statements, syntax patterns, GAMS features used
   - Cross-reference with current parser capabilities

2.3. Identify unsupported features
   - List all features that current parser doesn't support
   - Examples: if statements, model attributes, compile-time constants, etc.

**3. Secondary Blocker Classification (30 minutes)**

3.1. Categorize blockers by complexity
   - **Simple:** Grammar extension only (5-6h effort)
   - **Medium:** Grammar + semantic handler (8-10h effort)
   - **Complex:** Grammar + semantic + IR changes (12-15h effort)

3.2. Prioritize blockers by unlock potential
   - Which blocker appears in most GAMSLib models?
   - Which blocker is easiest to implement?
   - Which blocker has highest ROI (unlocks multiple models)?

3.3. Estimate unlock timeline
   - If secondary blocker addressed in Sprint 9: mhw4dx unlocks?
   - If deferred to Sprint 10: when does mhw4dx unlock?

**4. Documentation Update (45 minutes)**

4.1. Update GAMSLIB_FEATURE_MATRIX.md
   - Section: mhw4dx.gms analysis
   - Document: Primary blocker (✅ resolved), Secondary blocker(s) (🔵 pending)
   - Add: Complexity estimate, unlock timeline, ROI analysis

4.2. Create secondary blocker report
   - File: `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md`
   - Sections:
     - Executive summary (which features block mhw4dx?)
     - Line-by-line error catalog (lines 37-63)
     - Feature complexity analysis
     - Unlock recommendations (Sprint 9? Sprint 10?)

4.3. Cross-reference to Sprint 9 tasks
   - Does secondary blocker match any Sprint 9 planned feature?
   - Example: If blocker is model attributes, is that in Sprint 9 scope?
   - Update Sprint 9 scope if secondary blocker is quick win

**5. Validation (15 minutes)**

5.1. Verify analysis completeness
   - All lines 37-63 analyzed?
   - All unsupported features cataloged?
   - Complexity estimates reasonable?

5.2. Review against Sprint 8 retrospective
   - Does analysis meet "complete blocker analysis" criteria?
   - Have we identified ALL features needed for mhw4dx unlock?

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify GAMSLIB_FEATURE_MATRIX.md updated
grep -A 10 "mhw4dx.gms" docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md | grep "Secondary blocker"

# Verify blocker analysis document exists
ls -la docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md

# Verify secondary blocker documented
grep "Secondary blocker:" docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md

# Count features blocking mhw4dx
grep -c "Blocker:" docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md
```

### Deliverables

- Updated `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (mhw4dx section with secondary blocker)
- New `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md` (detailed analysis report)
- Error catalog (all errors in lines 37-63)
- Feature complexity estimates (simple/medium/complex)
- Unlock timeline recommendation (Sprint 9/10/later)

### Acceptance Criteria

- [ ] mhw4dx.gms re-parsed with Sprint 8 parser (option statements enabled)
- [ ] All errors in lines 37-63 cataloged (not just first error)
- [ ] Secondary blocker(s) identified and documented
- [ ] Secondary blocker complexity estimated (simple/medium/complex)
- [ ] GAMSLIB_FEATURE_MATRIX.md updated with secondary blocker
- [ ] MHW4DX_BLOCKER_ANALYSIS.md created with complete analysis
- [ ] Unlock timeline recommendation provided (Sprint 9/10/later)
- [ ] Cross-reference to Sprint 9 planned features (does secondary blocker match?)
- [ ] Analysis addresses Sprint 8 retrospective recommendation #1

---

## Task 3: Research Advanced Indexing (i++1, i--1) Syntax

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 6-8 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknowns 9.1.1-9.1.3: i++1 complexity, grammar, semantics)

### Objective

Research GAMS lead/lag indexing operators (i++1, i--1) to design grammar rules, semantic handling, and IR representation. Produce comprehensive implementation guide for Sprint 9 Day 3-4 work.

### Why This Matters

Advanced indexing is Sprint 9's highest-effort parser feature (8-10 hours) with "Medium-High" risk due to grammar changes and semantic complexity (PROJECT_PLAN.md lines 210-214). Thorough research prevents mid-sprint discovery of unsupported syntax variations.

himmel16.gms unlock depends on i++1 support (PRIMARY blocker per Sprint 8 feature matrix). Successful implementation unlocks 10% parse rate improvement (1/10 models).

### Background

From PROJECT_PLAN.md Sprint 9 Advanced Parser Features (lines 210-214):
> **Advanced Indexing (i++1, i--1)**
> - Implement lead/lag indexing operators
> - Unlocks: himmel16.gms and models with sequential indexing
> - Effort: 8-10 hours
> - Risk: Medium-High (requires grammar changes, semantic complexity)

From Sprint 8 Feature Matrix (`docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md`):
- himmel16.gms: "Primary blocker: lead/lag indexing (i++1)"
- Parse progress: ~42% (14/33 lines before i++1 blocker)

GAMS lead/lag indexing context:
- Used in time-series models for referencing adjacent periods
- Example: `x[i++1]` refers to next period's variable
- Common in dynamic optimization, inventory models

### What Needs to Be Done

**1. GAMS Documentation Survey (2 hours)**

1.1. Read GAMS User Guide on lead/lag operators
   - Section on dynamic sets and time indices
   - Section on circular vs linear sets
   - Examples of i++1, i--1, i++N usage

1.2. Catalog lead/lag operator variations
   - Simple lead: i++1, i++2, i++N
   - Simple lag: i--1, i--2, i--N
   - Combined: i++1 with j--1 (multi-dimensional)
   - Nested: (i++1)++1 (double lead?)
   - Boundary behavior: wrap-around vs error

1.3. Identify semantic constraints
   - Which sets support lead/lag (time indices only? all ordered sets?)
   - Boundary handling (i++1 at last element?)
   - Circular vs linear sets (wrap-around allowed?)

**2. GAMSLib Pattern Analysis (1.5 hours)**

2.1. Search GAMSLib for all lead/lag patterns
   ```bash
   grep -r "++[0-9]" data/gamslib/*.gms
   grep -r "--[0-9]" data/gamslib/*.gms
   ```

2.2. Analyze himmel16.gms specific usage
   - Lines where i++1 appears
   - Context: equations? assignments? constraints?
   - Index type: time? spatial? general?

2.3. Catalog all unique patterns
   - i++1 vs i++2 vs i++N
   - Single-dimensional vs multi-dimensional
   - With other operators (i++1*2? i++1+j?)

**3. Grammar Design (2 hours)**

3.1. Design Lark grammar rules for lead/lag
   ```lark
   ?index_expr: simple_index
              | lead_lag_index
   
   lead_lag_index: IDENTIFIER "++" INTEGER
                 | IDENTIFIER "--" INTEGER
   ```

3.2. Test grammar conflicts
   - Does ++ conflict with arithmetic operators?
   - Does i++1 parse as `i + (+1)` or `i ++ 1`?
   - Precedence: ++ before or after +?

3.3. Prototype grammar with Lark
   - Create minimal test grammar
   - Parse sample inputs: "i++1", "i--2", "i++1, j--1"
   - Verify AST structure matches expectations

**4. Semantic Handler Design (1.5 hours)**

4.1. Design IR representation for lead/lag
   - Option A: `IndexOffset(base='i', offset=1)` node
   - Option B: Store as `IndexRef(name='i', lead_lag=1)`
   - Option C: Transform to `IndexRef(name='i+1')` (string manipulation)

4.2. Design semantic validation
   - Validate set is ordered (supports lead/lag)
   - Validate offset doesn't exceed set bounds
   - Validate circular vs linear set boundary behavior

4.3. Design offset calculation logic
   - How to compute i++1 → actual index value?
   - Where to store offset metadata (in IR? in semantic handler?)
   - How to handle runtime vs compile-time offsets?

**5. Test Fixture Design (45 minutes)**

5.1. Identify test cases
   - Simple lead: i++1
   - Simple lag: i--1
   - Large offset: i++10
   - Multi-dimensional: i++1, j--2
   - Boundary cases: i++1 at set end

5.2. Create fixture structure
   - `tests/fixtures/lead_lag_indexing/01_simple_lead.gms`
   - `tests/fixtures/lead_lag_indexing/02_simple_lag.gms`
   - `tests/fixtures/lead_lag_indexing/03_multi_dimensional.gms`
   - `tests/fixtures/lead_lag_indexing/04_boundary_cases.gms`
   - `tests/fixtures/lead_lag_indexing/expected_results.yaml`

**6. Documentation (45 minutes)**

6.1. Create research document
   - File: `docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md`
   - Sections:
     - GAMS lead/lag operator overview
     - Supported syntax variations
     - Grammar design
     - Semantic handler design
     - IR representation
     - Test fixture strategy

6.2. Create implementation guide
   - Step-by-step grammar changes
   - Step-by-step semantic handler changes
   - IR node definitions
   - Validation logic
   - Test cases

6.3. Estimate implementation effort
   - Grammar: 2-3 hours
   - Semantic handler: 3-4 hours
   - Tests: 2-3 hours
   - Total: 7-10 hours (validates 8-10h estimate in PROJECT_PLAN.md)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document exists
ls -la docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md

# Verify grammar design section
grep -A 5 "## Grammar Design" docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md

# Verify test fixture structure documented
grep "tests/fixtures/lead_lag" docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md

# Count syntax variations cataloged
grep -c "Pattern:" docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md

# Should have 5-10 variations
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md` (600-800 lines)
- GAMS lead/lag operator syntax catalog (5-10 variations)
- Lark grammar design for i++1/i--1
- IR representation design (IndexOffset or equivalent)
- Semantic validation logic specification
- Test fixture strategy (4-5 fixtures)
- Implementation guide (step-by-step)
- Effort estimate validation (7-10h)

### Acceptance Criteria

- [ ] GAMS User Guide sections on lead/lag operators reviewed
- [ ] GAMSLib search for ++/-- patterns completed (catalog all occurrences)
- [ ] himmel16.gms lead/lag usage analyzed (lines, context, patterns)
- [ ] Grammar rules designed and prototyped with Lark
- [ ] Grammar conflicts tested (++ vs + precedence)
- [ ] IR representation designed (IndexOffset or alternative)
- [ ] Semantic validation logic specified (boundary checks, circular sets)
- [ ] Test fixture structure defined (4-5 fixtures)
- [ ] Implementation guide created (step-by-step)
- [ ] Effort estimate validated (should align with 8-10h in PROJECT_PLAN.md)
- [ ] Research document completeness: 600-800 lines with all sections

---

## Task 4: Research Model Section Syntax (mx/my)

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 4-5 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknowns 9.1.4-9.1.5: Model section syntax, grammar conflicts)

### Objective

Research GAMS model section syntax (`model mx / eq1, eq2 /;`) to design grammar rules and semantic handling. Unlock hs62.gms and mingamma.gms (2 models = +20% parse rate).

### Why This Matters

Model sections unlock 2 GAMSLib models (hs62.gms, mingamma.gms) with "Medium" risk and 5-6 hour implementation effort (PROJECT_PLAN.md lines 216-220). This is a high-ROI feature (20% parse rate improvement for 5-6 hours).

Sprint 8 achieved 40% parse rate. Sprint 9 target is ≥30% (conservative). Model sections help maintain/exceed 40% rate.

### Background

From PROJECT_PLAN.md Sprint 9 Advanced Parser Features (lines 216-220):
> **Model Sections (mx syntax)**
> - Support multi-line model declarations with `/` syntax
> - Unlocks: hs62.gms, mingamma.gms
> - Effort: 5-6 hours
> - Risk: Medium (grammar extension)

From Sprint 8 Feature Matrix:
- hs62.gms: Parse progress ~61% (11/18 lines), primary blocker likely model sections
- mingamma.gms: Parse progress ~24% (9/37 lines), primary blocker unknown

GAMS model section context:
- Models group equations for solving
- Syntax: `model <name> / <equation_list> /;`
- Can have multiple models in one file
- Example: `model mx / eq1, eq2, eq3 /;`

### What Needs to Be Done

**1. GAMS Documentation Survey (1.5 hours)**

1.1. Read GAMS User Guide on model declarations
   - Section on model statements
   - Section on equation grouping
   - Section on solve statements with models

1.2. Catalog model syntax variations
   - Simple model: `model m / all /;`
   - Explicit equations: `model m / eq1, eq2 /;`
   - Multiple models: `model m1 / eq1 /; model m2 / eq2 /;`
   - Empty models: `model m / /;` (allowed?)

1.3. Identify semantic meaning
   - What does model declaration do? (just grouping?)
   - Required before solve statement?
   - Can equations belong to multiple models?

**2. GAMSLib Pattern Analysis (1 hour)**

2.1. Analyze hs62.gms model usage
   - Line numbers where model appears
   - Model name (mx? my?)
   - Equation list (how many equations?)
   - Solve statement usage

2.2. Analyze mingamma.gms model usage
   - Same analysis as hs62.gms
   - Compare patterns (similar or different?)

2.3. Search GAMSLib for all model patterns
   ```bash
   grep -r "^model " data/gamslib/*.gms
   ```
   - Count occurrences
   - Catalog variations

**3. Grammar Design (1 hour)**

3.1. Design Lark grammar rules for model sections
   ```lark
   model_stmt: "model" IDENTIFIER "/" equation_list "/" ";"
   
   equation_list: IDENTIFIER ("," IDENTIFIER)*
                | "all"
   ```

3.2. Test grammar conflicts
   - Does "/" conflict with division operator?
   - How to distinguish `model m / all /` from `x = y / z /`?
   - Context-aware parsing needed?

3.3. Prototype grammar with Lark
   - Create minimal test grammar
   - Parse sample inputs: "model mx / eq1 /;", "model m / all /;"
   - Verify AST structure

**4. Semantic Handler Design (30 minutes)**

4.1. Design IR representation for models
   - Add `ModelDef` dataclass to `src/ir/symbols.py`
   - Fields: `name: str`, `equations: List[str]`
   - Store in `ModelIR.models: List[ModelDef]`

4.2. Design semantic validation
   - Validate all equations in list are declared
   - Validate model name is unique
   - Validate "all" keyword (includes all declared equations?)

4.3. Design solve statement integration
   - Do solve statements reference model by name?
   - Parse: `solve m using nlp;`
   - Validate model exists before solve?

**5. Test Fixture Design (30 minutes)**

5.1. Identify test cases
   - Simple model: `model m / eq1 /;`
   - Multiple equations: `model m / eq1, eq2, eq3 /;`
   - "all" keyword: `model m / all /;`
   - Multiple models: `model m1 / eq1 /; model m2 / eq2 /;`
   - Error case: undefined equation reference

5.2. Create fixture structure
   - `tests/fixtures/model_sections/01_simple_model.gms`
   - `tests/fixtures/model_sections/02_multiple_equations.gms`
   - `tests/fixtures/model_sections/03_all_keyword.gms`
   - `tests/fixtures/model_sections/04_multiple_models.gms`
   - `tests/fixtures/model_sections/expected_results.yaml`

**6. Documentation (30 minutes)**

6.1. Create research document
   - File: `docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md`
   - Sections:
     - GAMS model section overview
     - Supported syntax variations
     - Grammar design
     - Semantic handler design
     - IR representation (ModelDef)
     - Test fixture strategy

6.2. Estimate implementation effort
   - Grammar: 1-2 hours
   - Semantic handler: 2-3 hours
   - IR changes: 1 hour
   - Tests: 1-2 hours
   - Total: 5-8 hours (validates 5-6h estimate in PROJECT_PLAN.md)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document exists
ls -la docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md

# Verify grammar design section
grep -A 5 "## Grammar Design" docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md

# Verify ModelDef IR design documented
grep "ModelDef" docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md

# Verify hs62/mingamma analysis
grep "hs62.gms" docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md
grep "mingamma.gms" docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md

# Count syntax variations
grep -c "Pattern:" docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/MODEL_SECTIONS_RESEARCH.md` (400-600 lines)
- GAMS model section syntax catalog (4-6 variations)
- Lark grammar design for model statements
- IR representation design (ModelDef dataclass)
- Semantic validation logic specification
- Test fixture strategy (4-5 fixtures)
- hs62.gms and mingamma.gms usage analysis
- Implementation guide
- Effort estimate validation (5-8h)

### Acceptance Criteria

- [ ] GAMS User Guide sections on model declarations reviewed
- [ ] hs62.gms model usage analyzed (line numbers, equation list)
- [ ] mingamma.gms model usage analyzed
- [ ] GAMSLib search for model patterns completed
- [ ] Grammar rules designed and prototyped with Lark
- [ ] Grammar conflicts tested ("/" ambiguity)
- [ ] ModelDef IR representation designed
- [ ] Semantic validation logic specified (equation existence, name uniqueness)
- [ ] Test fixture structure defined (4-5 fixtures)
- [ ] Implementation guide created
- [ ] Effort estimate validated (should align with 5-6h in PROJECT_PLAN.md)

---

## Task 5: Design Conversion Pipeline Architecture

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 5-7 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknowns 9.2.1-9.2.5: Architecture, IR-to-MCP mapping, simple model scope)

### Objective

Design end-to-end conversion pipeline architecture for transforming parsed GAMS ModelIR into MCP JSON format. Enable at least 1 simple model (mhw4d or rbrock) to convert successfully.

### Why This Matters

Conversion pipeline is Sprint 9's new infrastructure component with "Medium" risk (6-8 hour effort). This is the first step toward end-to-end GAMS→MCP→PATH workflow. Successful design prevents mid-sprint architecture pivots.

PROJECT_PLAN.md acceptance criterion (lines 261-263): "At least 1 model (mhw4d or rbrock) successfully converts end-to-end." This task ensures we can meet that criterion.

### Background

From PROJECT_PLAN.md Sprint 9 Conversion & Performance (lines 233-239):
> **Conversion Pipeline Foundation**
> - Begin conversion infrastructure for successfully parsed models
> - Focus on simple models (mhw4d, rbrock) as initial targets
> - Effort: 6-8 hours
> - Risk: Medium (new pipeline stage)

Current state:
- Parser produces ModelIR (AST + semantic information)
- No conversion infrastructure exists yet
- MCP JSON schema defined elsewhere in project
- Goal: ModelIR → MCP JSON transformation

Simple models for initial conversion:
- mhw4d.gms: 14 lines, Sprint 7 unlock (20% parse rate milestone)
- rbrock.gms: 8 lines, Sprint 7 unlock (simplest GAMSLib model)

### What Needs to Be Done

**1. Architecture Design (2 hours)**

1.1. Define conversion pipeline stages
   - **Stage 1:** ModelIR validation (check completeness)
   - **Stage 2:** IR normalization (simplify for conversion)
   - **Stage 3:** MCP transformation (IR → MCP JSON)
   - **Stage 4:** MCP validation (check schema compliance)
   - **Stage 5:** Output serialization (write JSON file)

1.2. Choose architecture pattern
   - **Option A:** Single-pass visitor pattern (IR → MCP in one traversal)
   - **Option B:** Multi-pass (IR → intermediate → MCP)
   - **Option C:** Pipeline with intermediate representations

1.3. Design error handling strategy
   - Unsupported IR nodes: error or warning?
   - Partial conversion: allow or fail?
   - Error reporting: line numbers from SourceLocation?

1.4. Design module structure
   - `src/conversion/` directory
   - `converter.py`: Main conversion orchestrator
   - `ir_to_mcp.py`: IR-to-MCP transformation logic
   - `mcp_schema.py`: MCP JSON schema validation
   - `errors.py`: Conversion error types

**2. IR-to-MCP Mapping Design (2 hours)**

2.1. Audit current ModelIR coverage
   - Which IR nodes exist? (VariableDef, ParameterDef, EquationDef, etc.)
   - Which are needed for mhw4d.gms and rbrock.gms?
   - Which have no MCP equivalent?

2.2. Design IR-to-MCP mappings
   - VariableDef → MCP variable
   - ParameterDef → MCP parameter
   - EquationDef → MCP constraint
   - SetDef → MCP set (if MCP supports)
   - Expressions → MCP expression tree

2.3. Identify mapping gaps
   - Which IR nodes can't convert to MCP?
   - Which MCP fields have no IR equivalent?
   - Document conversion coverage % for simple models

2.4. Design unsupported feature handling
   - Error: "GAMS feature X not supported in MCP"
   - Warning: "Approximated GAMS feature Y as Z"
   - Graceful degradation: Skip unsupported, convert rest?

**3. Simple Model Analysis (1 hour)**

3.1. Analyze mhw4d.gms IR requirements
   - Parse mhw4d.gms, inspect ModelIR
   - List all IR nodes present (variables, parameters, equations)
   - Estimate conversion coverage: 100%? 80%? 50%?

3.2. Analyze rbrock.gms IR requirements
   - Same analysis as mhw4d.gms
   - Compare: Are both convertible with same code?

3.3. Identify conversion blockers
   - Which IR nodes in mhw4d/rbrock have no MCP mapping?
   - Which require special handling (e.g., bounds, domains)?
   - Estimate: Can we convert 100%? Or partial?

**4. MCP Schema Review (1 hour)**

4.1. Review existing MCP JSON schema
   - Where is MCP schema defined? (docs? code?)
   - What fields are required vs optional?
   - What constraints exist (e.g., variable bounds format)?

4.2. Identify GAMS-specific extensions needed
   - Does MCP support GAMS sets with aliases?
   - Does MCP support multi-dimensional parameters?
   - Does MCP support equation attributes (.l, .m)?

4.3. Design schema validation approach
   - Use jsonschema library?
   - Custom validation logic?
   - Validation before or after conversion?

**5. Test Strategy Design (45 minutes)**

5.1. Define conversion test levels
   - **Unit tests:** Individual IR node conversions
   - **Integration tests:** Full model conversions (mhw4d, rbrock)
   - **Schema validation tests:** MCP JSON schema compliance

5.2. Design test fixtures
   - `tests/conversion/test_ir_to_mcp.py`: IR node conversion tests
   - `tests/conversion/test_converter.py`: End-to-end conversion tests
   - `tests/conversion/fixtures/mhw4d_expected.json`: Expected MCP output

5.3. Define acceptance criteria for conversion
   - **Success:** MCP JSON passes schema validation
   - **Success:** MCP JSON can be read by PATH solver (future)
   - **Partial:** Some IR nodes convert, some fail with errors

**6. Documentation (45 minutes)**

6.1. Create architecture design document
   - File: `docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md`
   - Sections:
     - Architecture overview (5 stages)
     - IR-to-MCP mapping table
     - Unsupported feature handling
     - Module structure
     - Test strategy

6.2. Create implementation plan
   - Phase 1: Basic converter scaffolding (2h)
   - Phase 2: IR-to-MCP mappings (3h)
   - Phase 3: MCP validation (1h)
   - Phase 4: mhw4d/rbrock conversion tests (1-2h)
   - Total: 7-8 hours (validates 6-8h estimate)

6.3. Document conversion coverage
   - mhw4d.gms: X% of IR nodes convertible
   - rbrock.gms: Y% of IR nodes convertible
   - Blockers: List unsupported features

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify architecture document exists
ls -la docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md

# Verify architecture stages documented
grep -c "Stage [0-9]:" docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md

# Verify IR-to-MCP mapping table exists
grep "VariableDef.*MCP variable" docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md

# Verify mhw4d/rbrock analysis
grep "mhw4d.gms" docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md
grep "rbrock.gms" docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md

# Verify module structure documented
grep "src/conversion/" docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/CONVERSION_PIPELINE_ARCHITECTURE.md` (800-1000 lines)
- Architecture design (5-stage pipeline)
- IR-to-MCP mapping table (all IR nodes mapped)
- Module structure specification (`src/conversion/`)
- mhw4d.gms conversion feasibility analysis
- rbrock.gms conversion feasibility analysis
- Unsupported feature handling strategy
- Test strategy (unit, integration, schema validation)
- Implementation plan (7-8 hour breakdown)

### Acceptance Criteria

- [ ] Conversion pipeline architecture designed (5 stages defined)
- [ ] IR-to-MCP mapping table created (all IR nodes addressed)
- [ ] mhw4d.gms IR analyzed (conversion coverage estimated)
- [ ] rbrock.gms IR analyzed (conversion coverage estimated)
- [ ] MCP JSON schema reviewed (GAMS extensions identified)
- [ ] Unsupported feature handling strategy defined
- [ ] Module structure specified (`src/conversion/` directory layout)
- [ ] Test strategy designed (unit, integration, schema validation)
- [ ] Implementation plan created (phase breakdown, effort estimates)
- [ ] Effort estimate validated (should align with 6-8h in PROJECT_PLAN.md)

---

## Task 6: Design Automated Fixture Test Framework

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknowns 9.3.1-9.3.2: Framework design, validation scope)

### Objective

Design pytest-based framework to automatically validate all 13 test fixtures (from Sprint 8) against expected_results.yaml. Address Sprint 8 retrospective recommendation #2: "13 fixtures created, 0 automated tests."

### Why This Matters

Sprint 8 retrospective identified this as **High Priority Recommendation #2** (lines 375-382): "Create automated fixture tests for regression protection." Without automated tests, fixtures can drift from expected behavior without detection.

PROJECT_PLAN.md Test Infrastructure (lines 183-190):
> **Automated Fixture Tests (2-3 hours)**
> - Create `tests/test_fixtures.py`: Iterate over all 13 fixture directories
> - For each fixture: Parse GMS file, compare actual vs expected_results.yaml
> - Validate: parse status, statement counts, line numbers, option statements, indexed assignments

### Background

Current fixture count (from Sprint 8):
- 5 option statement fixtures (`tests/fixtures/options/`)
- 5 indexed assignment fixtures (`tests/fixtures/indexed_assign/`)
- 3 partial parse fixtures (`tests/fixtures/partial_parse/`)
- **Total: 13 fixtures**

Each fixture directory contains:
- `.gms` file with GAMS code
- `expected_results.yaml` with expected parse results
- `README.md` with fixture documentation

Sprint 8 retrospective (lines 410-412):
> **4. No Automated Fixture Tests**
> - Issue: 13 fixtures created, 0 automated tests using them
> - Root cause: Fixtures designed for manual validation only
> - Impact: No regression protection for fixture patterns
> - Recommendation: Implement automated fixture test suite in Sprint 9 (2-3 hours)

### What Needs to Be Done

**1. Pytest Framework Design (1 hour)**

1.1. Design fixture discovery mechanism
   - Scan `tests/fixtures/` directory recursively
   - Identify fixture directories (contain `.gms` + `expected_results.yaml`)
   - Auto-generate test cases for each fixture

1.2. Design parametrized test structure
   ```python
   import pytest
   from pathlib import Path
   
   def discover_fixtures():
       """Discover all fixture directories."""
       fixture_root = Path("tests/fixtures")
       fixtures = []
       for fixture_dir in fixture_root.rglob("*"):
           if (fixture_dir / "expected_results.yaml").exists():
               fixtures.append(fixture_dir)
       return fixtures
   
   @pytest.mark.parametrize("fixture_dir", discover_fixtures())
   def test_fixture(fixture_dir):
       """Test a single fixture directory."""
       # Load expected_results.yaml
       # Parse .gms file
       # Assert parse status, counts, etc.
       pass
   ```

1.3. Design fixture data loading
   - Load `expected_results.yaml` with PyYAML
   - Extract expected: parse status, statement count, line count, features
   - Handle missing keys gracefully (not all fixtures have all fields)

**2. Validation Logic Design (1.5 hours)**

2.1. Define validation assertions
   - **Parse status:** SUCCESS vs FAILED vs PARTIAL
   - **Statement count:** Actual vs expected (if present in YAML)
   - **Line count:** Actual vs expected (if present in YAML)
   - **Feature presence:** option_statements, indexed_assignments (if in YAML)
   - **Error message:** Contains expected text (if FAILED in YAML)

2.2. Design assertion helpers
   ```python
   def assert_parse_status(actual_ir, expected_status):
       if expected_status == "SUCCESS":
           assert actual_ir is not None
           assert not hasattr(actual_ir, 'error')
       elif expected_status == "FAILED":
           with pytest.raises(ParserError):
               # Parsing should raise
               pass
   
   def assert_statement_count(actual_ir, expected_count):
       actual_count = len(actual_ir.variables) + len(actual_ir.equations) + ...
       assert actual_count == expected_count
   ```

2.3. Design error reporting
   - On assertion failure: Show fixture name, expected vs actual
   - Include GMS file excerpt (first 10 lines)
   - Include parsed IR summary (if available)

**3. Test Coverage Design (30 minutes)**

3.1. Identify validation levels
   - **Level 1 (Basic):** Parse status only (SUCCESS/FAILED/PARTIAL)
   - **Level 2 (Counts):** Statement count, line count
   - **Level 3 (Features):** Option statements, indexed assignments present
   - **Level 4 (Deep):** AST structure, IR node types

3.2. Choose validation level for Sprint 9
   - Level 1 + 2: Minimum viable (2-3h implementation)
   - Level 1 + 2 + 3: Recommended (add 1h)
   - Level 1-4: Comprehensive (add 2-3h, defer to Sprint 10?)

3.3. Design opt-in for deep validation
   - All fixtures get Level 1+2 by default
   - Fixtures with `validate_ast: true` in YAML get Level 4

**4. Integration with Existing Tests (30 minutes)**

4.1. Decide test file location
   - Option A: `tests/test_fixtures.py` (new file)
   - Option B: `tests/integration/test_fixtures.py` (integration test)
   - Recommendation: Option A (clearly labeled fixture tests)

4.2. Design fixture test markers
   - `@pytest.mark.fixtures` for all fixture tests
   - `@pytest.mark.slow` for large fixtures (if any)
   - Run with: `pytest -m fixtures` to test fixtures only

4.3. Integrate with CI
   - Add fixture tests to `make test` target
   - Ensure all 13 fixtures tested on every commit
   - Fail CI if any fixture test fails

**5. Documentation (30 minutes)**

5.1. Create design document
   - File: `docs/planning/EPIC_2/SPRINT_9/FIXTURE_TEST_FRAMEWORK.md`
   - Sections:
     - Framework overview
     - Fixture discovery mechanism
     - Validation levels (1-4)
     - Assertion helpers
     - Test file structure

5.2. Update fixture README files
   - Add section: "Automated Testing"
   - Explain how fixtures are validated
   - Explain expected_results.yaml schema

5.3. Estimate implementation effort
   - Framework scaffolding: 1h
   - Validation logic (Level 1+2): 1h
   - Feature validation (Level 3): 0.5h
   - Integration + documentation: 0.5h
   - Total: 3h (validates 2-3h estimate)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify design document exists
ls -la docs/planning/EPIC_2/SPRINT_9/FIXTURE_TEST_FRAMEWORK.md

# Verify fixture discovery design documented
grep "discover_fixtures" docs/planning/EPIC_2/SPRINT_9/FIXTURE_TEST_FRAMEWORK.md

# Verify validation levels documented
grep -c "Level [0-9]" docs/planning/EPIC_2/SPRINT_9/FIXTURE_TEST_FRAMEWORK.md

# Should have 4 levels documented
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/FIXTURE_TEST_FRAMEWORK.md` (400-600 lines)
- Pytest framework design (fixture discovery, parametrization)
- Validation logic specification (4 levels)
- Assertion helper designs (parse status, counts, features)
- Test file structure (`tests/test_fixtures.py`)
- CI integration plan
- Implementation effort estimate (3h breakdown)

### Acceptance Criteria

- [ ] Pytest framework design completed (fixture discovery + parametrization)
- [ ] Validation levels defined (1: status, 2: counts, 3: features, 4: AST)
- [ ] Assertion helpers specified (parse status, statement count, line count, features)
- [ ] Test file location chosen (`tests/test_fixtures.py`)
- [ ] CI integration plan defined (add to `make test`, fail on fixture test failure)
- [ ] Documentation created (FIXTURE_TEST_FRAMEWORK.md)
- [ ] Effort estimate validated (should align with 2-3h in PROJECT_PLAN.md)
- [ ] Addresses Sprint 8 retrospective recommendation #2

---

## Task 7: Design Fixture Validation Script

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 6 (Fixture test framework design informs validation script)

### Objective

Design pre-commit validation script (`scripts/validate_fixtures.py`) to prevent manual counting errors in expected_results.yaml. Address Sprint 8 retrospective recommendation #3: "PR #254 had 5 review comments on incorrect counts."

### Why This Matters

Sprint 8 retrospective identified this as **High Priority Recommendation #3** (lines 384-391): "Fixture validation script prevents PR review cycles on manual counting errors." PR #254 required 5 review comments to fix line number and statement count errors.

PROJECT_PLAN.md Test Infrastructure (lines 192-196):
> **Fixture Validation Script (1 hour)**
> - Create `scripts/validate_fixtures.py` for pre-commit validation
> - Input: GMS file + expected_results.yaml
> - Output: Report discrepancies (line numbers, statement counts, feature counts)

### Background

Sprint 8 issue (PR #254):
- Created 3 partial parse fixtures
- expected_results.yaml had 5 errors:
  - Incorrect line numbers (manual counting error)
  - Incorrect statement counts (missed multi-line statements)
  - Incorrect parse percentages (rounding errors)
- Required 5 review comments to fix
- Delayed PR merge by 1 day

Sprint 8 retrospective (lines 406-409):
> **3. Partial Parse Fixture Errors**
> - Issue: PR #254 had 5 review comments on incorrect line numbers/statement counts
> - Root cause: Manual fixture creation without validation
> - Impact: Extra review cycles, delayed PR merge
> - Recommendation: Create fixture validation script (1 hour)

### What Needs to Be Done

**1. Statement Counting Algorithm Design (1 hour)**

1.1. Define "statement" for counting
   - Variable declarations: `Variable x;` = 1 statement
   - Parameter declarations: `Parameter p;` = 1 statement
   - Set declarations: `Set i /1*10/;` = 1 statement
   - Assignments: `p = 5;` = 1 statement
   - Equations: `eq1.. x =E= p;` = 1 statement
   - Multi-line statements: Count as 1 (not N)

1.2. Design line counting algorithm
   - **Logical lines:** Non-empty, non-comment lines
   - **Physical lines:** Total lines in file (including blank/comments)
   - Which to count for expected_results.yaml?
   - Sprint 8 used logical lines (exclude blank/comments)

1.3. Handle edge cases
   - Multi-line statements (`eq1..\n  x =E= p;` = 1 statement, 2 lines)
   - Inline comments (`x = 5; * comment` = 1 line, not 0)
   - Multi-line comments (`$ontext ... $offtext`)
   - Empty lines between statements

1.4. Design counting algorithm pseudocode
   ```python
   def count_statements(gms_file):
       """Count logical statements in GAMS file."""
       statements = 0
       in_multiline_comment = False
       for line in gms_file:
           # Skip blank lines
           if line.strip() == "":
               continue
           # Handle multiline comments
           if "$ontext" in line.lower():
               in_multiline_comment = True
           if "$offtext" in line.lower():
               in_multiline_comment = False
               continue
           if in_multiline_comment:
               continue
           # Skip single-line comments
           if line.strip().startswith("*"):
               continue
           # Count statement (heuristic: ends with ; or ..)
           if ";" in line or ".." in line:
               statements += 1
       return statements
   ```

**2. Validation Logic Design (45 minutes)**

2.1. Design validation checks
   - **Check 1:** Statement count matches expected_results.yaml
   - **Check 2:** Line count matches expected_results.yaml
   - **Check 3:** Parse percentage calculation correct (statements_parsed / statements_total * 100)
   - **Check 4:** Feature lists accurate (option_statements, indexed_assignments present)

2.2. Design discrepancy reporting
   ```python
   def validate_fixture(fixture_dir):
       """Validate fixture expected_results.yaml accuracy."""
       gms_file = fixture_dir / "*.gms"
       yaml_file = fixture_dir / "expected_results.yaml"
       
       actual_counts = count_statements_and_lines(gms_file)
       expected = load_yaml(yaml_file)
       
       discrepancies = []
       if actual_counts['statements'] != expected.get('statements_total'):
           discrepancies.append(f"Statement count: expected {expected['statements_total']}, actual {actual_counts['statements']}")
       
       return discrepancies
   ```

2.3. Design exit codes
   - **0:** All fixtures valid (no discrepancies)
   - **1:** Validation errors found (print discrepancies)
   - **2:** Script error (missing files, invalid YAML)

**3. CLI Design (30 minutes)**

3.1. Design command-line interface
   ```bash
   # Validate all fixtures
   python scripts/validate_fixtures.py
   
   # Validate specific fixture
   python scripts/validate_fixtures.py tests/fixtures/options/01_single_integer.gms
   
   # Auto-fix mode (update expected_results.yaml)
   python scripts/validate_fixtures.py --fix
   ```

3.2. Design output format
   ```
   Validating fixture: tests/fixtures/options/01_single_integer.gms
   ✅ Statement count: 5 (matches expected)
   ✅ Line count: 12 (matches expected)
   ⚠️  Parse percentage: expected 100%, calculated 83% (5/6 statements)
   
   Discrepancies found: 1
   ```

3.3. Design auto-fix behavior
   - Read GMS file, count statements/lines
   - Update expected_results.yaml with actual counts
   - Prompt user: "Update expected_results.yaml? [y/N]"
   - Safety: Require --fix flag + confirmation

**4. Integration Design (15 minutes)**

4.1. Design pre-commit hook integration
   - Add to `.pre-commit-config.yaml` (if exists)
   - Run on fixture changes only (not all commits)
   - Block commit if validation fails

4.2. Design CI integration
   - Run in CI before fixture tests
   - Fail CI if validation errors found
   - Report discrepancies in CI logs

**5. Documentation (30 minutes)**

5.1. Create design document
   - File: `docs/planning/EPIC_2/SPRINT_9/FIXTURE_VALIDATION_SCRIPT.md`
   - Sections:
     - Statement counting algorithm
     - Line counting algorithm
     - Validation checks (4 checks)
     - CLI usage
     - Auto-fix mode
     - Integration (pre-commit, CI)

5.2. Estimate implementation effort
   - Counting algorithms: 1h
   - Validation logic: 0.5h
   - CLI + auto-fix: 0.5h
   - Testing: 0.5h
   - Total: 2.5h (validates 2-3h estimate)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify design document exists
ls -la docs/planning/EPIC_2/SPRINT_9/FIXTURE_VALIDATION_SCRIPT.md

# Verify counting algorithms documented
grep "count_statements" docs/planning/EPIC_2/SPRINT_9/FIXTURE_VALIDATION_SCRIPT.md

# Verify validation checks documented
grep -c "Check [0-9]:" docs/planning/EPIC_2/SPRINT_9/FIXTURE_VALIDATION_SCRIPT.md

# Should have 4 checks documented
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/FIXTURE_VALIDATION_SCRIPT.md` (300-500 lines)
- Statement counting algorithm specification
- Line counting algorithm specification
- Validation logic design (4 checks)
- CLI design (usage examples, output format)
- Auto-fix mode design (safety, confirmation)
- Integration plan (pre-commit, CI)
- Implementation effort estimate (2.5h breakdown)

### Acceptance Criteria

- [ ] Statement counting algorithm designed (handles multi-line, comments, edge cases)
- [ ] Line counting algorithm designed (logical vs physical lines)
- [ ] Validation checks defined (4 checks: statements, lines, percentage, features)
- [ ] Discrepancy reporting designed (clear error messages)
- [ ] CLI interface designed (validate all, validate one, auto-fix mode)
- [ ] Auto-fix mode designed (safety, confirmation prompt)
- [ ] Integration plan defined (pre-commit hook, CI integration)
- [ ] Documentation created (FIXTURE_VALIDATION_SCRIPT.md)
- [ ] Effort estimate validated (originally 1h in PROJECT_PLAN.md; updated to 2-3h based on detailed task breakdown and accepted for this sprint)
- [ ] Addresses Sprint 8 retrospective recommendation #3

---

## Task 8: Research Equation Attributes (.l/.m) Handling

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknowns 9.1.6-9.1.7: Equation attributes scope, semantic meaning)

### Objective

Research GAMS equation attributes (.l for level, .m for marginal) to design parsing and storage strategy. This is foundational work for conversion pipeline (equations need attributes for MCP).

### Why This Matters

Equation attributes are part of Sprint 9 Advanced Parser Features (4-6 hour effort, PROJECT_PLAN.md lines 222-226). While lower priority than i++1 and model sections, equation attributes are "foundation for conversion pipeline."

Conversion pipeline needs equation attributes to produce complete MCP output. Without .l/.m handling, converted models may be incomplete.

### Background

From PROJECT_PLAN.md Sprint 9 Advanced Parser Features (lines 222-226):
> **Equation Attributes (.l/.m)**
> - Parse and store equation attributes where semantically relevant
> - Foundation for conversion pipeline
> - Effort: 4-6 hours

GAMS equation attributes:
- `.l` (level): Equation left-hand side value
- `.m` (marginal): Equation dual value (shadow price)
- Used post-solve to inspect equation values
- Example: `display eq1.l, eq1.m;`

Current parser state:
- Variable attributes (.l, .m, .lo, .up, .fx) already supported (Sprint 8)
- Equation attributes not yet supported
- Similar grammar patterns to variable attributes

### What Needs to Be Done

**1. GAMS Documentation Survey (1 hour)**

1.1. Read GAMS User Guide on equation attributes
   - Section on equation attributes
   - Difference between equation.l and variable.l
   - When are equation attributes meaningful (post-solve only?)

1.2. Catalog equation attribute types
   - .l (level): LHS value
   - .m (marginal): Dual value
   - .lo, .up, .scale: Equation bounds/scaling?
   - Are there others?

1.3. Identify semantic constraints
   - Can equation attributes appear in pre-solve context?
   - Are they read-only or writable?
   - Where can they appear (display? assignments? expressions?)

**2. GAMSLib Pattern Analysis (45 minutes)**

2.1. Search GAMSLib for equation attribute usage
   ```bash
   grep -r "\\.l" data/gamslib/*.gms | grep -v "variable"
   grep -r "\\.m" data/gamslib/*.gms | grep -v "variable"
   ```

2.2. Catalog equation attribute patterns
   - Display statements: `display eq1.l;`
   - Assignments: `p = eq1.m;` (copy marginal to parameter?)
   - Expressions: `x = 2 * eq1.l;` (use level in expression?)

2.3. Identify most common usage
   - Which attributes used most? (.l? .m?)
   - Which context? (display? assignment? expression?)

**3. Grammar Design (45 minutes)**

3.1. Review existing variable attribute grammar
   - `src/gams/gams_grammar.lark`: `ref_bound` rule
   - Current: `ref_bound: IDENTIFIER "." BOUND_K`
   - BOUND_K: `/(lo|up|fx|l|m)/i`

3.2. Design equation attribute grammar extension
   - Option A: Reuse ref_bound (works for both variables and equations)
   - Option B: New rule `eq_attr: IDENTIFIER "." EQ_ATTR_K` where EQ_ATTR_K = `/(l|m)/i`
   - Recommendation: Option A (simpler, reuses existing code)

3.3. Test grammar conflicts
   - Does reusing ref_bound cause ambiguity?
   - How to distinguish variable.l from equation.l? (semantic, not grammar)

**4. Semantic Handler Design (45 minutes)**

4.1. Design IR representation for equation attributes
   - Add to EquationDef: `.l_value: Optional[float] = None`
   - Add to EquationDef: `.m_value: Optional[float] = None`
   - Similar to VariableDef attributes

4.2. Design attribute access handling
   - When user accesses eq.l, what to return?
   - Pre-solve: None? Error? Mock value?
   - Post-solve: Actual value (not in parser scope)

4.3. Design storage strategy
   - **Sprint 9 scope:** Parse and store (mock/store approach like Sprint 8 options)
   - **Future scope:** Populate with solver results (Sprint 10+)
   - **Current:** Store attribute access, don't evaluate

**5. Test Fixture Design (30 minutes)**

5.1. Identify test cases
   - Display equation attributes: `display eq.l;`
   - Assign to parameter: `p = eq.m;`
   - Expression with attribute: `x = 2 * eq.l;`
   - Error case: Invalid attribute (eq.z?)

5.2. Create fixture structure
   - `tests/fixtures/equation_attributes/01_display.gms`
   - `tests/fixtures/equation_attributes/02_assignment.gms`
   - `tests/fixtures/equation_attributes/03_expression.gms`
   - `tests/fixtures/equation_attributes/expected_results.yaml`

**6. Documentation (30 minutes)**

6.1. Create research document
   - File: `docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md`
   - Sections:
     - GAMS equation attribute overview
     - Attribute types (.l, .m, others)
     - Grammar design (reuse ref_bound)
     - Semantic handler design
     - IR representation
     - Test fixture strategy

6.2. Estimate implementation effort
   - Grammar: 0.5h (minimal changes)
   - Semantic handler: 2-3h (attribute access logic)
   - IR changes: 0.5h (add fields to EquationDef)
   - Tests: 1-2h
   - Total: 4-6h (validates estimate in PROJECT_PLAN.md)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document exists
ls -la docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md

# Verify grammar design section
grep "Grammar Design" docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md

# Verify EquationDef IR changes documented
grep "EquationDef" docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md

# Count attribute types cataloged
grep -c "Attribute:" docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/EQUATION_ATTRIBUTES_RESEARCH.md` (300-500 lines)
- GAMS equation attribute catalog (.l, .m, others)
- Grammar design (reuse ref_bound or new rule)
- Semantic handler design (mock/store approach)
- IR representation design (EquationDef enhancements)
- Test fixture strategy (3-4 fixtures)
- GAMSLib usage pattern analysis
- Implementation effort estimate (4-6h)

### Acceptance Criteria

- [ ] GAMS User Guide sections on equation attributes reviewed
- [ ] Equation attribute types cataloged (.l, .m, others)
- [ ] GAMSLib search for equation attribute patterns completed
- [ ] Grammar design completed (reuse ref_bound or new rule)
- [ ] Semantic handler design completed (mock/store approach)
- [ ] IR representation designed (EquationDef enhancements)
- [ ] Test fixture structure defined (3-4 fixtures)
- [ ] Implementation guide created
- [ ] Effort estimate validated (should align with 4-6h in PROJECT_PLAN.md)

---

## Task 9: Design Performance Baseline & Budget Framework

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Unknowns 9.4.1-9.4.4: Baseline metrics, harness, storage, monitoring)

### Objective

Design performance baseline measurement framework and test suite performance budgets. Address Sprint 8 retrospective recommendation #5: "Establish test suite performance budget on Day 0."

### Why This Matters

Sprint 8 retrospective emphasized "test performance matters throughout sprint" (lines 421-425). Test optimization on Day 9 benefited Days 1-8 retroactively. Establishing performance budget on Day 0 benefits ALL sprint days.

PROJECT_PLAN.md Performance Baseline & Budget (lines 241-248):
> - Establish benchmark harness for parse/convert times
> - **NEW:** Establish test suite performance budgets:
>   - Fast tests (`make test`): <30s (currently 24s ✅)
>   - Full suite (`make test-all`): <5min baseline
> - **Sprint 8 Lesson:** Set up performance budget on Day 0 for all-day benefits

### Background

Sprint 8 test performance history:
- **Day 1-8:** Test suite ran in 120+ seconds (slow feedback loop)
- **Day 9:** Implemented slow test markers, reduced to 24 seconds (5x faster)
- **Lesson:** Performance budget should be established on Day 0, not Day 9

Current test suite performance:
- Fast tests (`make test`): ~24 seconds (1349 tests)
- Slow tests excluded with markers: ~5-10 tests marked slow
- Full suite (`make test-all`): Unknown (not measured)

Sprint 8 retrospective recommendations (lines 404-405):
> **5. Test Suite Performance Budget**
> - Goal: Establish and monitor performance budgets
> - Budget Proposal: <30s fast tests, <5min full suite

### What Needs to Be Done

**1. Performance Metrics Selection (1 hour)**

1.1. Define baseline metrics
   - **Test suite timing:**
     - Fast tests (pytest without slow markers): Total time in seconds
     - Full suite (pytest all tests): Total time in seconds
   - **Parse/convert timing:**
     - Per-model parse time: Median across 3 runs
     - Per-model convert time: Median across 3 runs (Sprint 9+)
   - **Memory usage:**
     - Peak memory per model parse
     - Peak memory per model convert
   - **AST/IR size metrics:**
     - Number of IR nodes per model
     - AST depth per model

1.2. Choose critical metrics for Sprint 9
   - **Critical:** Test suite timing (fast + full)
   - **Critical:** Per-model parse time (for dashboard)
   - **Nice-to-have:** Memory usage (defer to Sprint 10?)
   - **Nice-to-have:** AST/IR size (defer to Sprint 10?)

1.3. Define metric storage format
   ```json
   {
     "baseline_version": "v0.9.0",
     "timestamp": "2025-11-20T10:00:00Z",
     "test_suite": {
       "fast_tests_seconds": 24.3,
       "full_suite_seconds": 120.5,
       "test_count": 1349
     },
     "per_model": {
       "mhw4d.gms": {
         "parse_time_ms": 15.2,
         "parse_status": "SUCCESS"
       }
     }
   }
   ```

**2. Performance Budget Design (45 minutes)**

2.1. Define performance budgets
   - **Fast tests:** <30 seconds (currently 24s ✅, 20% margin)
   - **Full suite:** <5 minutes (to be baselined in Sprint 9)
   - **Per-model parse:** <100ms (reasonable for 10-50 line models)
   - **Per-model convert:** <200ms (to be baselined in Sprint 9)

2.2. Define budget enforcement strategy
   - **CI failure:** Fail CI if fast tests exceed 30s (strict)
   - **CI warning:** Warn if fast tests exceed 27s (90% of budget)
   - **Manual review:** If full suite exceeds 5min, investigate slow tests

2.3. Design budget adjustment policy
   - When to adjust budgets? (quarterly? per-sprint?)
   - How much margin to allow? (10%? 20%?)
   - How to handle legitimate slowdowns (new features add complexity)?

**3. Benchmark Harness Design (1 hour)**

3.1. Choose benchmarking tool
   - **Option A:** pytest-benchmark (mature, pytest integration)
   - **Option B:** timeit (stdlib, manual)
   - **Option C:** Custom harness (full control)
   - **Recommendation:** Option A (pytest-benchmark)

3.2. Design benchmark suite structure
   ```python
   # tests/benchmarks/test_parse_performance.py
   import pytest
   from pathlib import Path
   
   @pytest.mark.benchmark
   def test_parse_mhw4d(benchmark):
       """Benchmark mhw4d.gms parsing."""
       gms_file = Path("data/gamslib/mhw4d.gms")
       result = benchmark(parse_file, gms_file)
       assert result.parse_status == "SUCCESS"
   ```

3.3. Design benchmark result storage
   - Store in `docs/performance/baselines/v0.9.0.json`
   - Track historical baselines (v0.8.0, v0.7.0, etc.)
   - Compare current run to baseline (% change)

**4. CI Integration Design (45 minutes)**

4.1. Design CI performance check workflow
   - **Step 1:** Run fast tests, time execution
   - **Step 2:** Compare to budget (30s)
   - **Step 3:** Fail if exceeds budget, warn if >90% budget
   - **Step 4:** Report timing in CI summary

4.2. Design CI performance report format
   ```
   🚀 Test Performance Report
   ✅ Fast tests: 24.3s (80% of 30s budget)
   ⚠️  Full suite: 5.2min (104% of 5min budget) - INVESTIGATE
   
   Per-model parse times:
   ✅ mhw4d.gms: 15ms
   ✅ rbrock.gms: 8ms
   ⚠️  circle.gms: 110ms (110% of 100ms budget)
   ```

4.3. Design historical tracking
   - Store per-commit timing data
   - Plot trends over time (dashboard?)
   - Alert on sustained degradation (3+ commits slower)

**5. Documentation (30 minutes)**

5.1. Create design document
   - File: `docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md`
   - Sections:
     - Performance metrics (test suite, parse, convert, memory)
     - Performance budgets (fast tests <30s, full suite <5min)
     - Benchmark harness (pytest-benchmark)
     - CI integration (performance checks, reporting)
     - Baseline storage format (JSON schema)

5.2. Estimate implementation effort
   - Baseline measurement: 1h (run benchmarks, store results)
   - Budget enforcement (CI): 1h (CI workflow changes)
   - Benchmark harness: 1-2h (pytest-benchmark setup)
   - Documentation: 0.5h
   - Total: 3.5-4.5h (sum of above estimates)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify design document exists
ls -la docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md

# Verify performance budgets documented
grep "Fast tests.*<30" docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md
grep "Full suite.*<5min" docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md

# Verify benchmark harness design
grep "pytest-benchmark" docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md

# Verify baseline storage format
grep "baseline_version" docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/PERFORMANCE_FRAMEWORK.md` (400-600 lines)
- Performance metrics specification (test suite, parse, convert, memory)
- Performance budgets (<30s fast, <5min full)
- Benchmark harness design (pytest-benchmark)
- Baseline storage format (JSON schema)
- CI integration plan (performance checks, reporting)
- Implementation effort estimate (3.5-4.5h)

### Acceptance Criteria

- [ ] Performance metrics defined (test suite timing, parse timing, convert timing)
- [ ] Performance budgets defined (<30s fast tests, <5min full suite, <100ms parse)
- [ ] Benchmark harness chosen (pytest-benchmark recommended)
- [ ] Baseline storage format designed (JSON schema)
- [ ] CI integration plan defined (performance checks, budget enforcement, reporting)
- [ ] Historical tracking strategy designed (per-commit data, trend plotting)
- [ ] Documentation created (PERFORMANCE_FRAMEWORK.md)
- [ ] Effort estimate validated (should align with 4-5h in PROJECT_PLAN.md)
- [ ] Addresses Sprint 8 retrospective recommendation #5

---

## Task 10: Plan Sprint 9 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 7-9 hours  
**Deadline:** Before Sprint 9 Day 1  
**Owner:** Development team  
**Dependencies:** All tasks (1-9 must complete first)

### Objective

Synthesize all prep work (Tasks 1-9) into comprehensive Sprint 9 execution plan with day-by-day breakdown, 4 checkpoints, effort allocation, quality gates, and risk mitigation.

### Why This Matters

Sprint 9 is the most complex sprint to date: advanced parser features (grammar changes), new pipeline stage (conversion infrastructure), and test infrastructure improvements. Comprehensive planning prevents mid-sprint pivots and scope creep.

Sprint 8 PLAN.md was 1715 lines with 4 checkpoints, all passed on schedule. Sprint 9 PLAN.md should match that level of detail.

### Background

Sprint 9 estimated effort: 30-41 hours (PROJECT_PLAN.md line 282)
- Test infrastructure: 5-6h
- Advanced parser features: 15-20h
- Conversion & performance: 10-15h

Sprint 9 duration: 10-11 days (Days 0-10, Day 10 as buffer like Sprint 8)

Sprint 9 goals (from PROJECT_PLAN.md lines 164-168):
1. Parse rate: 40% → ≥30% baseline (maintain with advanced features)
2. Advanced features: i++1 indexing, model sections, equation attributes
3. Conversion pipeline: At least 1 model converts end-to-end
4. Test infrastructure: Automated fixtures, validation script, secondary blocker analysis
5. Performance: Baseline + budgets

### What Needs to Be Done

**1. Executive Summary (1 hour)**

1.1. Write Sprint 9 overview
   - Sprint goals (5 goals from PROJECT_PLAN.md)
   - Key differences from Sprint 8 (higher complexity, new pipeline stage)
   - Preparation effort summary (Tasks 1-9 total: 40-54h)
   - Critical path identification

1.2. Synthesize prep task findings
   - Task 1: 31-40 unknowns identified and verified
   - Task 2: mhw4dx.gms secondary blocker(s) documented
   - Task 3: i++1 indexing design (grammar, semantics, IR)
   - Task 4: Model sections design
   - Task 5: Conversion pipeline architecture
   - Task 6: Automated fixture framework
   - Task 7: Fixture validation script
   - Task 8: Equation attributes design
   - Task 9: Performance baseline + budget framework

**2. Day-by-Day Breakdown (3 hours)**

2.1. Define Sprint 9 schedule (10-11 days)
   - **Day 0:** Sprint planning & setup (2-3h)
     - Review prep tasks (1h)
     - Create branch, baseline checks (1h)
     - Set up performance budgets (1h)
   
   - **Days 1-2:** Test Infrastructure Improvements (5-6h)
     - Day 1: Secondary blocker analysis (2-3h), automated fixtures (1-2h)
     - Day 2: Fixture validation script (1h), performance baseline (1h)
     - **Checkpoint 1 (Day 2 End):** Test infrastructure complete
   
   - **Days 3-4:** Advanced Indexing (i++1, i--1) (8-10h)
     - Day 3: Grammar + semantic handler (4-5h)
     - Day 4: Tests + himmel16.gms validation (4-5h)
     - **Checkpoint 2 (Day 4 End):** i++1 indexing working, himmel16.gms parses
   
   - **Days 5-6:** Model Sections + Equation Attributes (9-12h)
     - Day 5: Model sections (5-6h)
     - Day 6: Equation attributes (4-6h)
     - **Checkpoint 3 (Day 6 End):** All parser features complete, hs62/mingamma parse
   
   - **Days 7-8:** Conversion Pipeline Foundation (6-8h)
     - Day 7: Converter scaffolding + IR-to-MCP mappings (4-5h)
     - Day 8: mhw4d/rbrock conversion + validation (2-3h)
     - **Checkpoint 4 (Day 8 End):** At least 1 model converts
   
   - **Day 9:** Dashboard + Performance Instrumentation (4-5h)
     - Dashboard expansion (3-4h)
     - Performance budget enforcement (1h)
   
   - **Day 10:** Documentation, PR, & Sprint Closeout (2-3h) - **BUFFER DAY**

2.2. For each day, specify:
   - Objectives
   - Tasks with time estimates
   - Quality gates
   - Deliverables

**3. Checkpoint Definitions (1.5 hours)**

3.1. Checkpoint 1 (Day 2 End): Test Infrastructure Complete
   - **Success criteria:**
     - ✅ mhw4dx.gms secondary blocker(s) documented
     - ✅ tests/test_fixtures.py validates all 13 fixtures
     - ✅ scripts/validate_fixtures.py prevents counting errors
     - ✅ Performance budgets established (<30s fast, <5min full)
     - ✅ All tests passing (no regressions)
   - **Go decision:** Continue to advanced indexing (Days 3-4)
   - **No-Go decision:** Debug fixture tests, allocate buffer hours

3.2. Checkpoint 2 (Day 4 End): i++1 Indexing Working
   - **Success criteria:**
     - ✅ i++1/i--1 grammar and semantic handler complete
     - ✅ himmel16.gms parses successfully
     - ✅ Parse rate ≥40% (himmel16.gms unlocked = 50% = 5/10 models)
     - ✅ 4-5 lead/lag indexing test fixtures passing
     - ✅ All tests passing (no regressions)
   - **Go decision:** Continue to model sections (Day 5)
   - **No-Go decision:** Assess secondary blocker, defer to Sprint 10

3.3. Checkpoint 3 (Day 6 End): All Parser Features Complete
   - **Success criteria:**
     - ✅ Model sections (mx syntax) working
     - ✅ Equation attributes (.l/.m) parsing complete
     - ✅ hs62.gms and mingamma.gms parse successfully
     - ✅ Parse rate ≥60% (hs62 + mingamma = 7/10 models)
     - ✅ All parser feature tests passing
   - **Go decision:** Continue to conversion pipeline (Days 7-8)
   - **No-Go decision:** Defer conversion to Sprint 10, focus on parser

3.4. Checkpoint 4 (Day 8 End): Conversion Pipeline Working
   - **Success criteria:**
     - ✅ Conversion pipeline infrastructure complete
     - ✅ At least 1 model converts (mhw4d or rbrock)
     - ✅ MCP JSON validates against schema
     - ✅ Dashboard shows parse/convert rates
     - ✅ All tests passing
   - **Go decision:** Polish dashboard, create PR (Days 9-10)
   - **No-Go decision:** Document conversion blockers, plan Sprint 10

**4. Effort Allocation (1 hour)**

4.1. Validate 30-41 hour budget
   - Test infrastructure: 5-6h (Days 1-2)
   - Advanced indexing: 8-10h (Days 3-4)
   - Model sections + equation attributes: 9-12h (Days 5-6)
   - Conversion pipeline: 6-8h (Days 7-8)
   - Dashboard + performance: 4-5h (Day 9)
   - Documentation: 2-3h (Day 10)
   - **Total: 34-44h** (aligns with 30-41h estimate)

4.2. Identify critical path
   - Tasks 1 → 2 → 3 → 5 → 10 (known unknowns → i++1 → conversion → plan)
   - Days 0 → 1-2 → 3-4 → 7-8 → 10 (setup → test infra → i++1 → conversion → closeout)

**5. Risk Mitigation (1 hour)**

5.1. Identify Sprint 9 risks
   - **Risk 1:** i++1 indexing more complex than 8-10h estimate
     - Mitigation: Task 3 validated estimate with deep research
     - Contingency: Use Day 10 buffer, defer equation attributes
   
   - **Risk 2:** Conversion pipeline blocks on IR gaps
     - Mitigation: Task 5 analyzed mhw4d/rbrock IR completeness
     - Contingency: Document gaps, defer to Sprint 10
   
   - **Risk 3:** himmel16.gms has secondary blocker after i++1
     - Mitigation: Task 2 completed secondary blocker analysis for mhw4dx (similar model)
     - Contingency: Accept 40% parse rate vs 50% target
   
   - **Risk 4:** Fixture tests fail on existing fixtures
     - Mitigation: Task 6 designed validation levels (start with Level 1+2)
     - Contingency: Fix fixtures manually, update expected_results.yaml
   
   - **Risk 5:** Performance budget enforcement breaks CI
     - Mitigation: Task 9 designed warning thresholds (90% budget)
     - Contingency: Adjust budgets, investigate slow tests

5.2. For each risk: Mitigation + Contingency

**6. Quality Gates (30 minutes)**

6.1. Define continuous quality gates (all days)
   - `make test` passes (100% of tests)
   - `make typecheck` passes
   - `make lint` passes
   - `make format` passes
   - Performance budget: Fast tests <30s

6.2. Define feature-specific quality gates
   - Day 2: All 13 fixtures validated automatically
   - Day 4: himmel16.gms parses, parse rate ≥40%
   - Day 6: hs62.gms + mingamma.gms parse, parse rate ≥60%
   - Day 8: At least 1 model converts to valid MCP JSON
   - Day 9: Dashboard shows parse/convert rates

**7. Deliverables & Acceptance Criteria (30 minutes)**

7.1. Compile all Sprint 9 deliverables
   - From PROJECT_PLAN.md (lines 250-259)
   - Plus deliverables from Tasks 1-9

7.2. Compile all Sprint 9 acceptance criteria
   - From PROJECT_PLAN.md (lines 261-271)
   - Plus criteria from Tasks 1-9

**8. Cross-References & Appendices (1 hour)**

8.1. Create cross-reference table
   - Map prep tasks (1-9) to sprint days
   - Map unknowns to execution validation
   - Map research docs to implementation tasks

8.2. Create appendices
   - Appendix A: Quality gates (detailed)
   - Appendix B: Sprint 9 vs Sprint 8 comparison
   - Appendix C: Lessons learned from Sprint 8
   - Appendix D: Dependencies (prep tasks, prior sprints)

**9. Document Writing (1 hour)**

9.1. Write complete PLAN.md
   - Target length: 1500-2000 lines (similar to Sprint 8's 1715 lines)
   - All sections with proper markdown formatting
   - Cross-references to prep task documents

9.2. Final review
   - Verify all day breakdowns complete
   - Verify all checkpoints have go/no-go criteria
   - Verify effort sums correctly
   - Verify cross-references valid

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify PLAN.md exists and has substantial content
ls -la docs/planning/EPIC_2/SPRINT_9/PLAN.md
wc -l docs/planning/EPIC_2/SPRINT_9/PLAN.md

# Should be 1500-2000 lines

# Verify all day sections present
grep -c "^## Day [0-9]" docs/planning/EPIC_2/SPRINT_9/PLAN.md

# Should have 11 day sections (Days 0-10)

# Verify all checkpoints present
grep -c "Checkpoint [0-9]" docs/planning/EPIC_2/SPRINT_9/PLAN.md

# Should have 4 checkpoints

# Verify cross-references to prep tasks
grep -c "Task [1-9]" docs/planning/EPIC_2/SPRINT_9/PLAN.md

# Should reference all 9 prep tasks
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (1500-2000 lines)
- Executive summary (Sprint 9 goals, strategy, prep summary)
- Day-by-day breakdown (Days 0-10)
- 4 checkpoint definitions with go/no-go criteria
- Effort allocation table (30-41h validated)
- Risk register (5+ risks with mitigation)
- Quality gates (continuous + feature-specific)
- Deliverables section (compiled from PROJECT_PLAN + Tasks 1-9)
- Acceptance criteria (compiled from PROJECT_PLAN + Tasks 1-9)
- Cross-reference table (prep tasks → sprint days)
- Appendices (quality gates, Sprint 9 vs 8, lessons, dependencies)

### Acceptance Criteria

- [ ] PLAN.md created with all required sections
- [ ] Executive summary complete (goals, strategy, prep summary, critical path)
- [ ] Day-by-day breakdown complete (Days 0-10, each with objectives, tasks, quality gates)
- [ ] 4 checkpoints defined (Days 2, 4, 6, 8) with clear go/no-go criteria
- [ ] Effort allocation validated (sums to 34-44h, aligns with 30-41h estimate)
- [ ] Risk register complete (5+ risks with mitigation + contingency)
- [ ] Quality gates defined (continuous + feature-specific)
- [ ] Deliverables section compiled (from PROJECT_PLAN + Tasks 1-9)
- [ ] Acceptance criteria compiled (from PROJECT_PLAN + Tasks 1-9)
- [ ] Cross-references complete (all prep tasks referenced)
- [ ] Appendices complete (4 appendices: quality gates, comparison, lessons, dependencies)
- [ ] Document length: 1500-2000 lines (substantial, comprehensive)
- [ ] All prep tasks (1-9) synthesized into execution plan

---

## Summary

### Total Preparation Effort

**Main Tasks (1-9):** 40-54 hours
**Task 10 (Planning):** 7-9 hours
**Total:** 47-63 hours (~6-8 working days)

### Critical Path

**Task 1** (Known Unknowns) → **Task 2** (Secondary Blocker Analysis) → **Task 3** (i++1 Research) → **Task 5** (Conversion Architecture) → **Task 10** (Detailed Schedule)

### Success Criteria

- [ ] All 10 prep tasks completed before Sprint 9 Day 1
- [ ] KNOWN_UNKNOWNS.md with 31-40 documented unknowns
- [ ] All critical unknowns verified (Tasks 1-9 dependencies resolved)
- [ ] Comprehensive research documents for all major features (i++1, model sections, conversion, etc.)
- [ ] Test infrastructure designs complete (automated fixtures, validation script, performance budget)
- [ ] Sprint 9 PLAN.md created with day-by-day breakdown and 4 checkpoints
- [ ] All prep documents cross-referenced and integrated into execution plan

### Dependencies

**Sprint 8 Retrospective:**
- `docs/planning/EPIC_2/SPRINT_8/RETROSPECTIVE.md` (lines 362-412: Recommendations)

**Sprint 8 Feature Matrix:**
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (model blocker analysis)

**PROJECT_PLAN.md:**
- Lines 162-282: Sprint 9 goals, components, deliverables, acceptance criteria

**Epic 2 Goals:**
- `docs/planning/EPIC_2/GOALS.md` (if exists)

---

## Appendix: Document Cross-References

### Sprint Goals → Prep Tasks

| Sprint Goal | Prep Tasks | Research Docs |
|-------------|------------|---------------|
| Parse rate ≥30% | Task 2, 3, 4 | LEAD_LAG_INDEXING_RESEARCH.md, MODEL_SECTIONS_RESEARCH.md |
| Advanced parser features | Task 3, 4, 8 | LEAD_LAG_INDEXING_RESEARCH.md, MODEL_SECTIONS_RESEARCH.md, EQUATION_ATTRIBUTES_RESEARCH.md |
| Conversion pipeline | Task 5 | CONVERSION_PIPELINE_ARCHITECTURE.md |
| Test infrastructure | Task 2, 6, 7, 9 | FIXTURE_TEST_FRAMEWORK.md, FIXTURE_VALIDATION_SCRIPT.md, PERFORMANCE_FRAMEWORK.md |
| Performance baseline | Task 9 | PERFORMANCE_FRAMEWORK.md |

### Sprint 8 Retrospective → Prep Tasks

| Retrospective Recommendation | Priority | Prep Task | Hours |
|-------------------------------|----------|-----------|-------|
| Secondary blocker analysis (mhw4dx) | High #1 | Task 2 | 2-3h |
| Automated fixture tests | High #2 | Task 6 | 3-4h |
| Fixture validation script | High #3 | Task 7 | 2-3h |
| Performance budget (Day 0) | Medium #5 | Task 9 | 3-4h |

### Prep Tasks → Sprint 9 Days

| Prep Task | Sprint 9 Days | Effort |
|-----------|---------------|--------|
| Task 1: Known Unknowns | Day 0 | Verify before execution |
| Task 2: Secondary Blocker Analysis | Day 1 | 2-3h (execute analysis) |
| Task 3: i++1 Research | Days 3-4 | Use research for implementation |
| Task 4: Model Sections Research | Day 5 | Use research for implementation |
| Task 5: Conversion Architecture | Days 7-8 | Use design for implementation |
| Task 6: Fixture Framework | Day 1 | 2-3h (implement framework) |
| Task 7: Validation Script | Day 2 | 1h (implement script) |
| Task 8: Equation Attributes Research | Day 6 | Use research for implementation |
| Task 9: Performance Framework | Day 0, 2, 9 | Set up budget (Day 0), baseline (Day 2), enforce (Day 9) |
| Task 10: Detailed Schedule | Day 0 | Guide execution |

---

**End of Sprint 9 Preparation Plan**
