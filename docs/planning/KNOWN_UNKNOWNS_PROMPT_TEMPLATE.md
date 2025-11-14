# Known Unknowns Creation Prompt Template

## Purpose

This document provides a reusable prompt template for creating Known Unknowns documents for future sprints. The template ensures that:
1. Known Unknowns are created as Task 1 of sprint preparation
2. Each unknown is mapped to relevant prep tasks
3. Prep tasks explicitly reference which unknowns they verify
4. Unknowns serve as actionable checklists during task execution

## Background

Starting with Sprint 7, we established a bidirectional relationship between Known Unknowns and Preparation Tasks:
- **Unknowns guide tasks:** Each prep task references which unknowns it verifies
- **Tasks verify unknowns:** During task execution, verification results are added to the unknowns document

This approach ensures unknowns are not just static documentation but active research guides.

## Prompt Template

Use this prompt when creating a new sprint's Known Unknowns document:

---

### Prompt for Creating Known Unknowns

```
On a new branch, create Task 1 from the Sprint [N] Preparation Plan: Create Known Unknowns List.

REQUIREMENTS:

1. Create `docs/planning/EPIC_[X]/SPRINT_[N]/KNOWN_UNKNOWNS.md` following the format from previous sprints (e.g., Sprint 6, Sprint 7).

2. Document structure must include:
   - Executive Summary
   - How to Use This Document (with priority definitions)
   - Summary Statistics
   - Table of Contents
   - 5 main categories (adjust based on sprint scope):
     * Category 1: [Primary sprint focus, e.g., Parser Enhancements]
     * Category 2: [Secondary focus, e.g., Test Performance]
     * Category 3: [Integration focus, e.g., GAMSLib Integration]
     * Category 4: [Quality improvements, e.g., Convexity Refinements]
     * Category 5: [Infrastructure, e.g., CI/CD]
   - Template for adding new unknowns during sprint
   - Next Steps section

3. Each unknown must have:
   - Priority (Critical/High/Medium/Low)
   - Assumption being made
   - Research Questions (3-5 specific questions)
   - How to Verify (concrete test cases or experiments)
   - Risk if Wrong (impact on sprint)
   - Estimated Research Time
   - Owner
   - Verification Results (initially: "🔍 Status: INCOMPLETE")

4. CRITICAL: After creating all unknowns, analyze which prep tasks (Task 2-10) will verify each unknown:
   - Review each prep task's objective and what needs to be done
   - Identify which unknowns that task will research/verify
   - For each task, list the specific Unknown numbers it verifies

5. Create a mapping table at the end of the KNOWN_UNKNOWNS.md document:

   ## Appendix: Task-to-Unknown Mapping
   
   This table shows which prep tasks verify which unknowns:
   
   | Prep Task | Unknowns Verified | Notes |
   |-----------|-------------------|-------|
   | Task 2: [Name] | X.Y, X.Z | [Brief note] |
   | Task 3: [Name] | X.A, X.B, X.C | [Brief note] |
   | ... | ... | ... |

6. IMPORTANT: After completing the KNOWN_UNKNOWNS.md with the mapping table, you MUST update the PREP_PLAN.md to add "Unknowns Verified" metadata to each task (Tasks 2-10):
   - Add a new line after "Dependencies" that says: `**Unknowns Verified:** X.Y, X.Z`
   - Add to the task's Deliverables section: `- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns X.Y, X.Z`
   - Add to the task's Acceptance Criteria: `- [ ] Unknowns X.Y, X.Z verified and updated in KNOWN_UNKNOWNS.md`

7. Target metrics:
   - Total unknowns: 22-30 (aim for 25+)
   - Priority distribution: ~25% Critical, ~40% High, ~25% Medium, ~10% Low
   - Total research time: 28-36 hours
   - Categories: 5 major categories covering all sprint components

8. Cross-reference requirements:
   - Link to PROJECT_PLAN.md Sprint [N] deliverables
   - Link to PRELIMINARY_PLAN.md (if exists)
   - Reference lessons from previous sprint retrospectives
   - Include unknown numbers from deferred unknowns in previous sprints

9. When finished:
   - Update PREP_PLAN.md Task 1 status to COMPLETE
   - Check off all acceptance criteria for Task 1
   - Update PREP_PLAN.md Tasks 2-10 with "Unknowns Verified" sections
   - Update CHANGELOG.md with comprehensive Task 1 completion entry
   - Run quality checks: `make typecheck && make lint && make format && make test` (if any Python code changes)
   - Commit all changes with message: "Complete Sprint [N] Prep Task 1: Create Known Unknowns List"
   - Push branch to remote

EXAMPLE TASK-TO-UNKNOWN MAPPINGS (from Sprint 7):
- Task 2 (GAMSLib Analysis): Unknowns 1.3, 3.1
- Task 3 (Preprocessor Research): Unknowns 1.1, 1.4, 1.11
- Task 4 (Multi-dim Indexing): Unknowns 1.2, 1.6
- Task 5 (Test Profiling): Unknowns 2.1, 2.3, 2.4
- Task 6 (Syntax Survey): Unknowns 1.3 (contributes to), 1.9, 1.10
- Task 7 (Line Numbers): Unknown 4.1
- Task 8 (CI Setup): Unknowns 3.2, 3.3, 5.1
- Task 9 (Test Fixtures): Uses findings from Tasks 2, 3, 4
- Task 10 (Sprint Plan): Integrates all verified unknowns

DELIVERABLES:
- ✅ KNOWN_UNKNOWNS.md created with 22+ unknowns
- ✅ Task-to-Unknown mapping table in KNOWN_UNKNOWNS.md
- ✅ PREP_PLAN.md updated with "Unknowns Verified" for Tasks 2-10
- ✅ PREP_PLAN.md Task 1 status → COMPLETE, all acceptance criteria checked
- ✅ CHANGELOG.md updated with Task 1 completion entry
- ✅ All changes committed and pushed

QUALITY GATE:
- ALWAYS run `make typecheck && make lint && make format && make test` before committing Python code
- Verify all cross-references are valid
- Ensure all 22+ unknowns have complete sections (no missing fields)
- Confirm all prep tasks (2-10) have "Unknowns Verified" metadata
```

---

## Key Principles

### 1. Bidirectional Mapping
- Unknowns → Tasks: Each unknown lists which tasks will verify it
- Tasks → Unknowns: Each task lists which unknowns it verifies

### 2. Actionable Research
- Unknowns are not just documentation—they are research checklists
- Each unknown has concrete verification methods (test cases, experiments)
- During task execution, update unknowns with findings

### 3. Priority-Driven
- Critical unknowns (>8h rework if wrong) must be verified before sprint starts
- High unknowns (4-8h rework) should be verified during prep or early sprint
- Medium/Low unknowns can be resolved during implementation

### 4. Cross-Referenced
- Link to PROJECT_PLAN.md for sprint scope
- Link to previous sprint retrospectives for lessons learned
- Link to deferred unknowns from previous sprints

### 5. Living Document
- Template provided for adding unknowns during sprint
- Verification results updated as research completes
- Status tracked: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG

## Example Unknown Structure

```markdown
## Unknown X.Y: [Concise question or assumption statement]

### Priority
**[Critical/High/Medium/Low]** - [One-line impact statement]

### Assumption
[State the assumption being made. Be specific and testable.]

### Research Questions
1. [Specific question 1]
2. [Specific question 2]
3. [Specific question 3]
...

### How to Verify
[Concrete verification method with test cases or experiments]

**Test Case 1:** [Description]
```[language]
[Code example]
```
Expected: [What should happen]

**Test Case 2:** [Description]
...

### Risk if Wrong
- **[Primary risk]:** [Description with time/effort impact]
- **[Secondary risk]:** [Description]
...

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE

[This section updated during task execution with findings]
```

## Updating Verification Results

During prep task execution, update the unknown with findings:

```markdown
### Verification Results
✅ **Status:** VERIFIED  
**Verified by:** Task 3 (Preprocessor Research)  
**Date:** 2025-11-15

**Findings:**
- Mock directive handling approach is sufficient for Sprint 7 goals
- Can handle `$set`, `$if`, `$include` by recognizing and skipping
- Full preprocessing NOT required for 30% parse rate target
- Tested on 3 GAMSLib models: circle.gms, himmel16.gms, hs62.gms
- All 3 models now parse successfully with mock approach

**Decision:** Implement mock directive handling in Sprint 7 Day 1-2
```

Or if the assumption was wrong:

```markdown
### Verification Results
❌ **Status:** WRONG - Assumption was incorrect  
**Verified by:** Task 3 (Preprocessor Research)  
**Date:** 2025-11-15

**Findings:**
- Mock directive handling INSUFFICIENT for 30% parse rate
- 7/9 failed models require full conditional evaluation (`$if` branches)
- Skipping directives produces semantically incorrect AST
- Performance impact of full preprocessing: +15% parse time (acceptable)

**Corrected Assumption:**
Full preprocessing is required for Sprint 7. Mock approach would achieve only ~15% parse rate.

**Decision:** Implement full preprocessing engine in Sprint 7 Days 1-3 (revised scope)
```

## Checklist for Creating Known Unknowns

Use this checklist when following the prompt:

- [ ] KNOWN_UNKNOWNS.md created with all required sections
- [ ] 22-30 unknowns documented across 5 categories
- [ ] All unknowns have complete fields (priority, assumption, research questions, verification method, risk, time estimate, owner)
- [ ] Priority distribution appropriate (~25% Critical, ~40% High, ~25% Medium, ~10% Low)
- [ ] Total research time estimated (28-36 hours)
- [ ] Task-to-Unknown mapping table created in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Tasks 2-10 updated with "Unknowns Verified" metadata
- [ ] PREP_PLAN.md Tasks 2-10 deliverables include updating KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Tasks 2-10 acceptance criteria include verifying unknowns
- [ ] PREP_PLAN.md Task 1 status changed to COMPLETE
- [ ] PREP_PLAN.md Task 1 acceptance criteria all checked off
- [ ] CHANGELOG.md updated with Task 1 completion entry
- [ ] Cross-references valid (PROJECT_PLAN.md, PRELIMINARY_PLAN.md, previous retrospectives)
- [ ] Template for adding unknowns during sprint included
- [ ] Quality checks passed (if Python code modified)
- [ ] All changes committed with descriptive message
- [ ] Branch pushed to remote

## Benefits of This Approach

1. **Proactive Risk Management:** Issues identified before sprint execution
2. **Efficient Research:** Tasks know exactly what to verify
3. **No Forgotten Unknowns:** Explicit mapping prevents unknowns from being overlooked
4. **Living Documentation:** Verification results captured for future reference
5. **Better Estimation:** Research time estimates inform sprint planning
6. **Clear Accountability:** Each unknown has an owner and verification task
7. **Continuous Improvement:** Lessons from verification inform future sprints

## Historical Context

**Sprint 4, 5, 6:** Known Unknowns were standalone documents without explicit task mapping.
- Result: Some unknowns were forgotten or verification was unclear

**Sprint 7+:** Bidirectional mapping between unknowns and tasks.
- Result: All unknowns systematically verified, no surprises during sprint

This template formalizes the Sprint 7 approach for future sprints.

---

**Created:** 2025-11-14  
**Last Updated:** 2025-11-14  
**Owner:** Sprint Planning Team  
**Related Documents:**
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` (reference implementation)
- `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md` (shows task-to-unknown integration)
