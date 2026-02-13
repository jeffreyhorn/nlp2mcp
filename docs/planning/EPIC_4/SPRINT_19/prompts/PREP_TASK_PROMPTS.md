# Sprint 19 Prep Task Prompts

Each prompt below is a self-contained instruction set for completing one Sprint 19 Prep Task.
Copy the prompt for the task you want to execute and use it in a new Claude Code session.

---

## Prompt: Prep Task 2 — Classify internal_error Failure Modes

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 2: Classify internal_error Failure Modes.

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task2`

## Objective

Run all 23 `internal_error` models with debug parser output to classify failure modes before Sprint 19 implementation. This directly feeds the "internal_error Investigation" component (6-8h in sprint). Sprint 19 targets reducing internal_error from 23 to below 15.

## Background

- internal_error models: 23 models fail during parsing with internal errors
- Per PROJECT_PLAN.md, these need classification into: grammar ambiguity, missing production, IR construction crash, transformer error
- Sprint 18 focused on emission-layer fixes and deferred all parser work
- Research context: `docs/research/gamslib_parse_errors.md`, `docs/research/preprocessor_directives.md`
- Pipeline results: `data/gamslib/gamslib_status.json`
- Grammar: `src/gams/gams_grammar.lark`
- Parser: `src/ir/parser.py`

## What to Do

1. Identify all 23 internal_error models from pipeline results database
2. Run each model with verbose/debug parser output
3. Capture and categorize each error:
   - **Grammar ambiguity:** Multiple parse paths, unexpected token resolution
   - **Missing production:** Syntax construct not in grammar
   - **IR construction crash:** Parser succeeds but IR transformer fails
   - **Transformer error:** Semantic analysis failure during tree transformation
4. Group models by root cause pattern
5. Identify which patterns are quickest to fix (low-hanging fruit)
6. Estimate effort per pattern group
7. Document findings in `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` with classification of all 23 models
- Error category distribution (count per category)
- Recommended fix order (easiest/highest-ROI first)
- Effort estimates per category

## Verify Known Unknowns

This task verifies Unknowns **7.1** and **7.2** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

For each unknown, update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with:
  - Evidence (data, counts, specific examples)
  - Whether the original assumption was correct
  - Any corrections or adjustments needed
  - Impact on Sprint 19 planning

### Unknown 7.1: What is the distribution of internal_error failure types?
- **Assumption:** 23 models can be classified into 3-5 failure types; most common affects 8+ models
- **Verify:** Run all 23 models with debug output, capture error type/message/stack trace, group by root cause

### Unknown 7.2: Can internal_error fixes be made without breaking currently-parsing models?
- **Assumption:** Fixes are additive (new rules) and won't break 62 currently-parsing models
- **Verify:** Assess whether identified fixes require modifying existing grammar rules vs. adding new ones

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 2:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md`:

```markdown
### Sprint 19 Prep Task 2: Classify internal_error Failure Modes - YYYY-MM-DD

**Branch:** `planning/sprint19-task2`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary of findings]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 7.1 | [Verified/Wrong] | [Brief finding] |
| 7.2 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 2: Classify internal_error Failure Modes

- Created INTERNAL_ERROR_ANALYSIS_PREP.md with classification of all 23 models
- [Summarize key findings: N categories, top pattern, quickest fixes]
- Verified Unknowns 7.1, 7.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 2 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task2
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 2: Classify internal_error Failure Modes" \
  --body "## Summary
Completes Prep Task 2: Classify internal_error Failure Modes.

## Changes
- Created \`INTERNAL_ERROR_ANALYSIS_PREP.md\` with classification of all 23 internal_error models
- Verified Unknowns 7.1, 7.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 2 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 7.1: Distribution of internal_error failure types
- 7.2: Regression risk assessment for internal_error fixes

## Acceptance Criteria
- [ ] All 23 internal_error models run with debug output
- [ ] Each model classified into one of: grammar ambiguity, missing production, IR crash, transformer error
- [ ] Models grouped by root cause pattern
- [ ] Fix priority order defined (ROI-based)
- [ ] Effort estimates per pattern group documented
- [ ] Top 8+ quickest to fix models identified
- [ ] Unknowns 7.1, 7.2 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 3 — Catalog lexer_invalid_char Subcategories

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 3: Catalog lexer_invalid_char Subcategories.

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task3`

## Objective

Fully subcategorize the ~95 lexer_invalid_char failures to prioritize grammar work for Sprint 19. This feeds the "lexer_invalid_char Fixes" component (14-18h in sprint) and the deferred "Lexer Error Deep Analysis" item (5-6h). Sprint 19 targets reducing lexer_invalid_char from ~95 to below 50.

## Background

- Sprint 18 initial analysis: `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md` (Days 4-5 methodology)
- Prior parse error research: `docs/research/gamslib_parse_errors.md`, `docs/research/gamslib_parse_errors_preliminary.md`
- PROJECT_PLAN.md estimates: Complex set data (8-10h, 14+ models), Compile-time constants (3-4h), Remaining clusters (3-4h)
- Grammar: `src/gams/gams_grammar.lark`
- Pipeline results: `data/gamslib/gamslib_status.json`
- Sprint 17 lexer analysis: `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md`

## What to Do

1. Query pipeline results to get current list of all lexer_invalid_char models
2. Run each model with verbose lexer output to capture exact error location
3. Extract the character/token causing the lexer failure
4. Group by failure pattern:
   - **Complex set data syntax** (multi-dimensional assignments, compound operations)
   - **Compile-time constants** (`1*card(s)`, `ord(s)` in ranges)
   - **Dollar control options** (`$ontext/$offtext`, `$if`, `$setglobal`)
   - **Put/display statements** (format specifiers, output routing)
   - **Semicolon/continuation issues** (missing terminators, line continuation)
   - **Other/novel** (patterns not previously identified)
5. Count models per subcategory
6. Cross-reference with PROJECT_PLAN.md estimates — validate or correct
7. Identify which subcategories are addressable with grammar-only changes vs. requiring preprocessor support
8. Prioritize by model count and implementation feasibility
9. Document in `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` with full subcategorization
- Model count per subcategory (validated against PROJECT_PLAN.md estimates)
- Grammar-change-feasibility assessment per subcategory
- Recommended implementation order for Sprint 19

## Verify Known Unknowns

This task verifies Unknowns **4.1, 4.2, 4.3, 6.1, 6.4** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

For each unknown, update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Unknown 4.1: What is the current lexer_invalid_char count, and has it changed since v1.2.0?
- **Assumption:** Approximately 95 models with lexer_invalid_char errors
- **Verify:** Run full pipeline and count lexer_invalid_char failures; resolve discrepancy between GOALS.md (74) and PROJECT_PLAN.md (~95)

### Unknown 4.2: Are there preprocessor directives in lexer_invalid_char models that require preprocessor support?
- **Assumption:** Most failures are grammar-fixable; some need preprocessor
- **Verify:** Grep all lexer_invalid_char models for `$` directives; classify as grammar-fixable vs preprocessor-required

### Unknown 4.3: What is the overlap between deferred "Lexer Error Deep Analysis" and this task?
- **Assumption:** This task produces the catalog; the sprint item builds on it with fix plans
- **Verify:** Compare deliverables of this task with PROJECT_PLAN.md deferred item spec

### Unknown 6.1: What specific GAMS syntax constructs cause complex set data failures?
- **Assumption:** Multi-dimensional set assignments, compound operations, data-statement syntax
- **Verify:** Extract failing line from each complex set data model; identify 3-5 most common patterns

### Unknown 6.4: How many models are addressable with grammar-only changes?
- **Assumption:** At least 45 of ~95 can be fixed with grammar changes
- **Verify:** Calculate grammar-fixable count from catalog results

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 3:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 3: Catalog lexer_invalid_char Subcategories - YYYY-MM-DD

**Branch:** `planning/sprint19-task3`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary of findings]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 4.1 | [Verified/Wrong] | [Brief finding] |
| 4.2 | [Verified/Wrong] | [Brief finding] |
| 4.3 | [Verified/Wrong] | [Brief finding] |
| 6.1 | [Verified/Wrong] | [Brief finding] |
| 6.4 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 3: Catalog lexer_invalid_char Subcategories

- Created LEXER_ERROR_CATALOG.md with full subcategorization of N models
- [Summarize: N subcategories, top patterns, grammar-fixable count]
- Verified Unknowns 4.1, 4.2, 4.3, 6.1, 6.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 3 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task3
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 3: Catalog lexer_invalid_char Subcategories" \
  --body "## Summary
Completes Prep Task 3: Catalog lexer_invalid_char Subcategories.

## Changes
- Created \`LEXER_ERROR_CATALOG.md\` with full subcategorization
- Verified Unknowns 4.1, 4.2, 4.3, 6.1, 6.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 3 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 4.1: Current lexer_invalid_char count
- 4.2: Preprocessor directive impact
- 4.3: Overlap with deferred Lexer Error Deep Analysis
- 6.1: Complex set data syntax constructs
- 6.4: Grammar-only addressable count

## Acceptance Criteria
- [ ] All lexer_invalid_char models cataloged with exact error location
- [ ] Models grouped into 5+ subcategories with counts
- [ ] PROJECT_PLAN.md estimates validated or corrected
- [ ] Grammar-only vs. preprocessor-required distinction made
- [ ] Implementation order recommended (highest ROI first)
- [ ] Total addressable count estimated (to validate <50 target)
- [ ] Unknowns 4.1, 4.2, 4.3, 6.1, 6.4 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 4 — Analyze Cross-Indexed Sum Patterns (ISSUE_670)

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670).

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task4`

## Objective

Deeply analyze the cross-indexed sum problem in KKT stationarity equations to produce a concrete fix design before Sprint 19 implementation. This is the highest-ROI item from the FIX_ROADMAP (6 models blocked, P1 priority). ISSUE_670 causes GAMS Error 149 "Uncontrolled set entered as constant."

## Background

- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 1 section)
- Sprint 18 Day 8 investigation: `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md`
- KKT stationarity code: `src/kkt/stationarity.py`, `src/kkt/assemble.py`
- Expression-to-GAMS converter: `src/emit/expr_to_gams.py` (already has index aliasing for GAMS Error 125)
- Related research: `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`
- Issue doc: `docs/issues/ISSUE_670_cross-indexed-sums-error-149.md`
- Affected models: abel, qabel, chenery, mexss, orani, robert (secondary)
- FIX_ROADMAP effort estimate: 8-16 hours

## What to Do

1. Read `src/kkt/stationarity.py` and trace how stationarity equations are built
2. For each of the 6 affected models, extract the specific constraint causing ISSUE_670:
   - What is the original constraint structure?
   - What does the differentiated stationarity equation look like?
   - Which index becomes "uncontrolled"?
3. Identify the common pattern across all 6 models
4. Design the fix — evaluate at least these options:
   - **Option A:** Wrap uncontrolled indices in sum expressions during stationarity generation
   - **Option B:** Add index scoping metadata to the IR during differentiation
   - **Option C:** Post-process stationarity equations to detect and fix uncontrolled indices
5. Evaluate each option for: implementation complexity, regression risk, compatibility with existing index aliasing in `expr_to_gams.py`
6. Recommend preferred approach with implementation sketch
7. Define test strategy (unit tests + model validation)
8. Document in `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` with fix design
- Per-model analysis of the cross-indexed sum pattern
- Recommended fix approach with implementation sketch
- Test strategy document
- Effort estimate refinement (narrow from 8-16h)

## Verify Known Unknowns

This task verifies Unknowns **8.1** and **8.2** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

For each unknown, update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Unknown 8.1: What is the exact code path that produces uncontrolled indices in stationarity equations?
- **Assumption:** Issue occurs in `src/kkt/stationarity.py` when differentiating constraints with sums over non-domain indices; fix is localized to stationarity builder
- **Verify:** Trace stationarity generation for abel model; identify exact line where uncontrolled index is introduced; determine if fix needs one module or multiple

### Unknown 8.2: Do all 6 ISSUE_670 models share the same cross-indexed sum pattern?
- **Assumption:** All 6 models have the same fundamental pattern (sum over non-domain index)
- **Verify:** Extract the specific constraint from each model; compare patterns; determine if one fix covers all

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 4:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670) - YYYY-MM-DD

**Branch:** `planning/sprint19-task4`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary of findings — common pattern, recommended fix, refined estimate]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 8.1 | [Verified/Wrong] | [Brief finding] |
| 8.2 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670)

- Created ISSUE_670_DESIGN.md with fix design for 6 affected models
- [Summarize: common pattern, recommended approach, refined estimate]
- Verified Unknowns 8.1, 8.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 4 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task4
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670)" \
  --body "## Summary
Completes Prep Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670).

## Changes
- Created \`ISSUE_670_DESIGN.md\` with per-model analysis and fix design
- Verified Unknowns 8.1, 8.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 4 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 8.1: Exact code path producing uncontrolled indices
- 8.2: Whether all 6 models share same pattern

## Acceptance Criteria
- [ ] All 6 affected models analyzed with specific constraint patterns documented
- [ ] Common cross-indexed sum pattern identified and described
- [ ] At least 2 fix approaches evaluated with pros/cons
- [ ] Preferred approach recommended with implementation sketch
- [ ] Compatibility with existing expr_to_gams.py index aliasing assessed
- [ ] Test strategy defined (unit tests + 6-model validation)
- [ ] Effort estimate refined from 8-16h range
- [ ] Unknowns 8.1, 8.2 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 5 — Audit Sprint 18 Deferred Item Readiness

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 5: Audit Sprint 18 Deferred Item Readiness.

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task5`

## Objective

Verify that all 5 Sprint 18 deferred items have sufficient context, code pointers, and test plans for efficient Sprint 19 implementation. Ensure no prerequisites are missing. Sprint 18 deferred 5 items (~17-21h) when architectural limitations were discovered.

## Background

- PROJECT_PLAN.md Sprint 18 Deferred Items section (lines 155-188)
- Sprint 18 SPRINT_LOG.md: `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md`
- Sprint 18 research: `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md`, `TABLE_DATA_ANALYSIS.md`, `COMPUTED_PARAM_ANALYSIS.md`
- Source files: `src/emit/emit_gams.py`, `src/emit/model.py`, `src/emit/expr_to_gams.py`, `src/gams/gams_grammar.lark`

## What to Do

For each of the 5 deferred items, verify readiness:

### Item 1: MCP Infeasibility Bug Fixes (3-4h)
- Confirm circle and house model failure modes are still as documented
- Verify `uniform()` random data issue in circle is reproducible
- Check if Sprint 18 emission fixes changed any relevant code paths
- Identify exact source file locations for fixes

### Item 2: Subset Relationship Preservation (4-5h)
- Confirm the ~3 affected models and their specific failures
- Verify `src/emit/emit_gams.py` and `src/emit/model.py` code locations still valid
- Check if Sprint 18 emission changes affected set/subset handling
- Identify test models and expected outcomes

### Item 3: Reserved Word Quoting (2-3h)
- Confirm the ~2 affected models and the specific reserved words
- Verify `src/emit/expr_to_gams.py` is still the right location
- Check if Sprint 18 quoting fixes partially addressed this
- List all GAMS reserved words that need quoting

### Item 4: Lexer Error Deep Analysis (5-6h)
- Define scope boundary with Task 3 (lexer_invalid_char catalog)
- Determine if Task 3 output satisfies this item or if additional work is needed
- Clarify deliverable: what does "complete" look like?

### Item 5: Put Statement Format Support (2.5h)
- Review `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md`
- Verify grammar extension location in `src/gams/gams_grammar.lark`
- Confirm 4 target models: ps5_s_mn, ps10_s, ps10_s_mn, stdcge
- Check if any of these models have secondary issues beyond put format

Document in `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md`.

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` with per-item readiness assessment
- Updated code pointers for each item (source files, line numbers)
- Identified blockers or missing prerequisites
- Confirmed or updated effort estimates

## Verify Known Unknowns

This task verifies Unknowns **1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.3, 5.1, 5.2** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

For each unknown, update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Category 1 — MCP Infeasibility Bug Fixes:
- **1.1:** Does circle's `uniform()` require capturing original values or a different approach?
- **1.2:** What is the root cause of house's MCP infeasibility?
- **1.3:** Will fixing circle and house affect currently-solving models?

### Category 2 — Subset Relationship Preservation:
- **2.1:** Which specific models fail due to missing subset relationships?
- **2.2:** Does the IR preserve set-subset relationship metadata?
- **2.3:** Will subset preservation interact with Sprint 18's element literal quoting fix?

### Category 3 — Reserved Word Quoting:
- **3.1:** Which GAMS reserved words appear as identifiers in the corpus?
- **3.2:** Does quoting in expr_to_gams.py cover all emission contexts?
- **3.3:** Will quoting reserved words break GAMS keyword recognition?

### Category 4/5 — Lexer/Put:
- **4.3:** Overlap between deferred Lexer Error Deep Analysis and Prep Task 3
- **5.1:** Does Sprint 18 put format grammar design still apply?
- **5.2:** Do 4 target put-statement models have issues beyond put format?

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 5:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 5: Audit Sprint 18 Deferred Item Readiness - YYYY-MM-DD

**Branch:** `planning/sprint19-task5`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary — readiness status per item, any blockers found, effort adjustments]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 1.1 | [Verified/Wrong] | [Brief finding] |
| 1.2 | [Verified/Wrong] | [Brief finding] |
| 1.3 | [Verified/Wrong] | [Brief finding] |
| 2.1 | [Verified/Wrong] | [Brief finding] |
| 2.2 | [Verified/Wrong] | [Brief finding] |
| 2.3 | [Verified/Wrong] | [Brief finding] |
| 3.1 | [Verified/Wrong] | [Brief finding] |
| 3.2 | [Verified/Wrong] | [Brief finding] |
| 3.3 | [Verified/Wrong] | [Brief finding] |
| 4.3 | [Verified/Wrong] | [Brief finding] |
| 5.1 | [Verified/Wrong] | [Brief finding] |
| 5.2 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 5: Audit Sprint 18 Deferred Item Readiness

- Created DEFERRED_ITEMS_AUDIT.md with readiness assessment for all 5 items
- [Summarize: readiness status, blockers, effort adjustments]
- Verified Unknowns 1.1-1.3, 2.1-2.3, 3.1-3.3, 4.3, 5.1-5.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 5 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task5
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 5: Audit Sprint 18 Deferred Item Readiness" \
  --body "## Summary
Completes Prep Task 5: Audit Sprint 18 Deferred Item Readiness.

## Changes
- Created \`DEFERRED_ITEMS_AUDIT.md\` with per-item readiness assessment
- Verified 12 Unknowns (1.1-1.3, 2.1-2.3, 3.1-3.3, 4.3, 5.1-5.2)
- Updated PREP_PLAN.md Task 5 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 1.1-1.3: MCP infeasibility (circle uniform(), house root cause, regression risk)
- 2.1-2.3: Subset preservation (affected models, IR metadata, quoting interaction)
- 3.1-3.3: Reserved word quoting (word list, emission contexts, keyword conflict)
- 4.3: Lexer Deep Analysis overlap with Task 3
- 5.1-5.2: Put format design validity, secondary issues

## Acceptance Criteria
- [ ] All 5 deferred items audited with current code pointers
- [ ] Each item has confirmed affected models and failure modes
- [ ] Sprint 18 code changes checked for impact on each item
- [ ] Overlap between Lexer Error Deep Analysis and Task 3 clarified
- [ ] No missing prerequisites identified (or blockers documented)
- [ ] Effort estimates confirmed or updated
- [ ] All 12 unknowns verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 6 — Research IndexOffset IR Design Options

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 6: Research IndexOffset IR Design Options.

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task6`

## Objective

Research and evaluate design options for the IndexOffset IR node type, which will support GAMS lead/lag syntax (`t+1`, `t-1`, `t++1`, `t--1`). This feeds the "IndexOffset IR Design" component (4h in sprint). IndexOffset support is needed for 8 models blocked at the translate stage.

## Background

- PROJECT_PLAN.md IndexOffset section (lines 232-242): design + parser spike
- GOALS.md: "Translation Stage: IndexOffset Support — Implement lead/lag indexing (8 models blocked)"
- Existing IR AST: `src/ir/ast.py` (current node types)
- Related research: `docs/research/multidimensional_indexing.md`
- GAMS semantics: `x(t+1)` = value at next period, `x(t-1)` = previous period
- Circular variants: `x(t++1)` wraps around set boundaries
- Sprint 18 Day 3 fix: `src/emit/expr_to_gams.py` already handles `IndexOffset` objects in `_format_mixed_indices()`

## What to Do

1. Read `src/ir/ast.py` to understand current IR node structure
2. Study GAMS lead/lag syntax and semantics (linear, circular, multi-period)
3. Evaluate IR design options:
   - **Option A: IndexOffset as child of VarRef** — offset stored as attribute of variable reference
   - **Option B: IndexOffset as wrapper node** — new AST node wrapping index expressions
   - **Option C: IndexOffset as modified index** — transform index in-place with offset metadata
4. For each option, assess: parser integration, AD compatibility, KKT generation, GAMS emission, circular vs linear distinction
5. Recommend preferred design with rationale
6. Sketch parser grammar changes needed in `src/gams/gams_grammar.lark`
7. Identify the 8 blocked models by name
8. Document in `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` with evaluated options
- Recommended IR design with rationale
- Grammar change sketch for `src/gams/gams_grammar.lark`
- Impact assessment across all 4 pipeline stages (parser, AD, KKT, emit)

## Verify Known Unknowns

This task verifies Unknowns **7.3** and **7.4** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

For each unknown, update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Unknown 7.3: How should IndexOffset interact with automatic differentiation?
- **Assumption:** `x(t+1)` and `x(t)` are independent variables during differentiation
- **Verify:** Review GAMS documentation on dynamic models; study 1-2 blocked models for expected MCP structure

### Unknown 7.4: What grammar changes are needed to parse GAMS lead/lag syntax?
- **Assumption:** Extend index expression rule; `+`/`-` in index positions are lead/lag, not arithmetic
- **Verify:** Review GAMS syntax rules; prototype grammar rule; check for conflicts with arithmetic

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 6:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 6: Research IndexOffset IR Design Options - YYYY-MM-DD

**Branch:** `planning/sprint19-task6`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary — recommended design, key trade-offs, grammar sketch]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 7.3 | [Verified/Wrong] | [Brief finding] |
| 7.4 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 6: Research IndexOffset IR Design Options

- Created INDEX_OFFSET_DESIGN_OPTIONS.md with 3+ design options evaluated
- [Summarize: recommended design, key trade-off, grammar sketch]
- Verified Unknowns 7.3, 7.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 6 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task6
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 6: Research IndexOffset IR Design Options" \
  --body "## Summary
Completes Prep Task 6: Research IndexOffset IR Design Options.

## Changes
- Created \`INDEX_OFFSET_DESIGN_OPTIONS.md\` with evaluated design options
- Verified Unknowns 7.3, 7.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 6 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 7.3: IndexOffset interaction with automatic differentiation
- 7.4: Grammar changes needed for lead/lag syntax

## Acceptance Criteria
- [ ] Current IR AST node structure documented
- [ ] GAMS lead/lag semantics fully described (linear, circular, multi-period)
- [ ] At least 3 design options evaluated with pros/cons
- [ ] Each option assessed against all 4 pipeline stages
- [ ] Preferred design recommended with rationale
- [ ] Grammar change sketch provided
- [ ] 8 blocked models identified by name
- [ ] Unknowns 7.3, 7.4 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 7 — Analyze Table Parsing Issues (ISSUE_392, ISSUE_399)

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399).

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task7`

## Objective

Analyze the two table parsing issues from the FIX_ROADMAP to understand the grammar gaps and produce fix plans for Sprint 19. ISSUE_392 (table continuation) blocks the `like` model; ISSUE_399 (table description as header) blocks the `robert` model.

## Background

- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 2-3 sections)
- Sprint 18 table research: `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md`
- General table research: `docs/research/RESEARCH_SUMMARY_TABLE_SYNTAX.md`
- Grammar: `src/gams/gams_grammar.lark` (table_block rule)
- Parser: `src/ir/parser.py` (table semantic handler)
- Sprint 18 SPRINT_LOG.md Day 8: robert classified primarily as ISSUE_399

## What to Do

### ISSUE_392: Table Continuation (`+` syntax)
1. Read the `like` model's table block to understand the exact continuation pattern
2. Review current table grammar rule in `src/gams/gams_grammar.lark`
3. Identify where the `+` continuation marker needs to be handled
4. Determine if the grammar already supports `+` but the semantic handler drops data
5. Design grammar and/or handler fix
6. Estimate data recovery (currently 4/62 values captured, 93.5% loss)

### ISSUE_399: Table Description as Header
1. Read the `robert` model's table block to see the description pattern
2. Trace how the parser processes table headers
3. Identify why quoted descriptions are treated as column headers
4. Design fix to distinguish quoted descriptions from column identifiers
5. Estimate data recovery (currently 4/9 values captured, 55% loss)

Document in `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md`.

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md` with per-issue analysis
- Grammar change proposals for each issue
- Fix implementation plans with test strategies
- Confirmed or updated effort estimates (FIX_ROADMAP says 2-4h each)

## Verify Known Unknowns

This task verifies Unknown **8.3** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

Update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Unknown 8.3: Can table continuation (ISSUE_392) and table description (ISSUE_399) be fixed with grammar changes alone?
- **Assumption:** Both can be fixed with grammar rule changes and/or semantic handler updates, without IR changes
- **Verify:** Read grammar and handler code; determine if grammar-only or handler-only or both; check for regression risk

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 7:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399) - YYYY-MM-DD

**Branch:** `planning/sprint19-task7`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary — root causes, fix approaches, effort estimates]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 8.3 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399)

- Created TABLE_PARSING_ANALYSIS.md with per-issue analysis
- [Summarize: root causes, fix approaches, effort estimates]
- Verified Unknown 8.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 7 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task7
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399)" \
  --body "## Summary
Completes Prep Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399).

## Changes
- Created \`TABLE_PARSING_ANALYSIS.md\` with per-issue analysis and fix proposals
- Verified Unknown 8.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 7 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 8.3: Whether grammar-only fixes are sufficient for table parsing

## Acceptance Criteria
- [ ] \`like\` model table block analyzed for ISSUE_392
- [ ] \`robert\` model table block analyzed for ISSUE_399
- [ ] Current grammar rule and semantic handler reviewed
- [ ] Root cause identified for each issue (grammar gap vs. handler bug)
- [ ] Fix approach documented for each issue
- [ ] Test strategy defined (unit tests + model validation)
- [ ] Unknown 8.3 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 8 — Analyze MCP Pairing Issues (ISSUE_672)

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 8: Analyze MCP Pairing Issues (ISSUE_672).

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task8`

## Objective

Analyze the MCP pairing failures for alkyl and bearing models to understand the bound edge cases causing empty equations, and design a fix plan. ISSUE_672 blocks 2 models with "MCP pair has empty equation but variable is NOT fixed" errors.

## Background

- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` (Priority 4 section)
- MCP pairing logic: `src/kkt/partition.py` (or related KKT module)
- Model pair emission: `src/emit/model.py`
- Sprint 18 Days 4-5 fix: `src/kkt/partition.py` — case sensitivity fix for bound multiplier keys
- FIX_ROADMAP effort estimate: 4-6 hours
- These models reach the solve stage but fail at MCP model construction

## What to Do

1. Run alkyl and bearing models through the pipeline to reproduce the exact error
2. Examine the variable bounds in each model:
   - Which variables have unusual bound configurations?
   - Are there variables with `.fx` (fixed), equal `.lo`/`.up`, or missing bounds?
3. Trace through MCP pairing logic to identify where empty equations are generated
4. Determine why the pairing logic doesn't handle these bound configurations
5. Design fix approach:
   - Should empty equations be filtered out?
   - Should the variable be treated as fixed?
   - Should the pairing logic be adjusted for these bound patterns?
6. Define test cases for the fix
7. Document in `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md` with per-model analysis
- Identified bound configurations causing empty equations
- Fix approach with implementation plan
- Confirmed or updated effort estimate (FIX_ROADMAP says 4-6h)

## Verify Known Unknowns

This task verifies Unknown **8.4** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

Update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Unknown 8.4: What bound configurations cause empty MCP equations in ISSUE_672?
- **Assumption:** Specific bound configurations (equal .lo/.up, .fx bounds) cause the issue in partition.py
- **Verify:** Run both models, list variable bounds, trace MCP pairing logic for failing pairs

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 8:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 8: Analyze MCP Pairing Issues (ISSUE_672) - YYYY-MM-DD

**Branch:** `planning/sprint19-task8`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary — bound configurations found, fix approach, effort estimate]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 8.4 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 8: Analyze MCP Pairing Issues (ISSUE_672)

- Created ISSUE_672_ANALYSIS.md with per-model analysis
- [Summarize: bound configurations, fix approach, effort estimate]
- Verified Unknown 8.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 8 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task8
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 8: Analyze MCP Pairing Issues (ISSUE_672)" \
  --body "## Summary
Completes Prep Task 8: Analyze MCP Pairing Issues (ISSUE_672).

## Changes
- Created \`ISSUE_672_ANALYSIS.md\` with per-model analysis and fix design
- Verified Unknown 8.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 8 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 8.4: Bound configurations causing empty MCP equations

## Acceptance Criteria
- [ ] Both alkyl and bearing models analyzed with exact error reproduced
- [ ] Bound configurations causing the issue documented
- [ ] MCP pairing logic traced and failure point identified
- [ ] Fix approach designed with test strategy
- [ ] Effort estimate confirmed or updated
- [ ] Unknown 8.4 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 9 — Verify Sprint 19 Baseline Metrics

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 9: Verify Sprint 19 Baseline Metrics.

## Branch Setup

1. Start from the `main` branch (checkout and pull latest)
2. Create a new branch: `planning/sprint19-task9`

## Objective

Verify that v1.2.0 baseline metrics are accurate and establish the starting point for Sprint 19 acceptance criteria. Sprint 18 retrospective noted "Day 11 vs final metrics discrepancy" as a lesson learned — verify upfront this time.

## Background

- Sprint 18 final metrics from SPRINT_LOG.md Day 14:
  - Parse: 62/160 (38.8%)
  - Translate: 48
  - Solve: 20
  - path_syntax_error: 7
  - Full Pipeline: 7
  - Test count: 3294
- Release tag: v1.2.0 on main
- Sprint 19 targets from PROJECT_PLAN.md:
  - lexer_invalid_char: ~95 → below 50
  - internal_error (parse): 23 → below 15
  - Parse rate: ≥55% of valid corpus
- Pipeline results: `data/gamslib/gamslib_status.json`

## What to Do

1. Run full test suite on current main branch and verify all 3294 tests pass
2. Run full pipeline on all GAMSLIB models and capture metrics:
   - Parse success count
   - Translate success count
   - Solve success count
   - Full pipeline success count
   - Error category breakdown (lexer_invalid_char, internal_error, path_syntax_error, path_solve_terminated)
3. Compare against Sprint 18 Day 14 reported numbers
4. Document any discrepancies
5. Confirm Sprint 19 acceptance criteria targets are correctly calibrated
6. Document in `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` with verified numbers
- Error category breakdown (counts per category)
- Confirmation that Sprint 19 targets are correctly calibrated
- Any discrepancies documented with explanation

## Verify Known Unknowns

This task verifies Unknowns **4.1** and **6.4** from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

For each unknown, update KNOWN_UNKNOWNS.md:
- Change `🔍 Status: INCOMPLETE` to `✅ VERIFIED` or `❌ WRONG (see correction below)`
- Add a **Findings** subsection under "Verification Results" with evidence, whether the assumption was correct, any corrections, and impact on Sprint 19

### Unknown 4.1: What is the current lexer_invalid_char count, and has it changed since v1.2.0?
- **Assumption:** Approximately 95 models with lexer_invalid_char errors
- **Verify:** Run full pipeline and count; resolve discrepancy between GOALS.md (74) and PROJECT_PLAN.md (~95)

### Unknown 6.4: How many models are addressable with grammar-only changes?
- **Assumption:** At least 45 of ~95 can be fixed with grammar changes
- **Verify:** Cross-reference with Task 3 catalog results if available; otherwise document current baseline for later validation

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 9:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 9: Verify Sprint 19 Baseline Metrics - YYYY-MM-DD

**Branch:** `planning/sprint19-task9`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary — metrics confirmed/discrepancies found, target calibration status]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` - [description]

#### Unknowns Verified
| Unknown | Status | Finding |
|---------|--------|---------|
| 4.1 | [Verified/Wrong] | [Brief finding] |
| 6.4 | [Verified/Wrong] | [Brief finding] |
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 9: Verify Sprint 19 Baseline Metrics

- Created BASELINE_METRICS.md with verified v1.2.0 numbers
- [Summarize: metrics confirmed/discrepancies, target calibration]
- Verified Unknowns 4.1, 6.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 9 status to COMPLETED
- Updated CHANGELOG.md"

git push origin planning/sprint19-task9
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 9: Verify Sprint 19 Baseline Metrics" \
  --body "## Summary
Completes Prep Task 9: Verify Sprint 19 Baseline Metrics.

## Changes
- Created \`BASELINE_METRICS.md\` with verified v1.2.0 baseline numbers
- Verified Unknowns 4.1, 6.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 9 → COMPLETED
- Updated CHANGELOG.md

## Unknowns Verified
- 4.1: Current lexer_invalid_char count
- 6.4: Grammar-only addressable model count

## Acceptance Criteria
- [ ] Full test suite passes (3294 tests, zero failures)
- [ ] Pipeline metrics verified against Sprint 18 Day 14 numbers
- [ ] Error category breakdown captured (lexer_invalid_char, internal_error counts)
- [ ] Sprint 19 acceptance criteria targets validated
- [ ] Any discrepancies documented and explained
- [ ] Unknowns 4.1, 6.4 verified and documented"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```

---

## Prompt: Prep Task 10 — Plan Sprint 19 Detailed Schedule

```
You are working in the nlp2mcp project repository root. Run all commands from the repo root.
Complete Sprint 19 Prep Task 10: Plan Sprint 19 Detailed Schedule.

## Branch Setup

1. Start from the `main` branch (checkout and pull latest — ensure all prior task PRs have been merged first)
2. Create a new branch: `planning/sprint19-task10`

## Objective

Create a detailed day-by-day Sprint 19 plan incorporating all prep work findings, Known Unknowns research, and FIX_ROADMAP priorities. This is the final prep task — it synthesizes all earlier research (Tasks 1-9) into an actionable 14-day schedule. Sprint 19 is 43-53 hours across 5 workstreams.

## Background

- PROJECT_PLAN.md Sprint 19 section (lines 147-264): component breakdown and acceptance criteria
- FIX_ROADMAP: `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md`: recommended week 1/week 2 split
- Sprint 18 retrospective: checkpoint methodology (Days 1, 6, 11) rated highly
- All prep task outputs (Tasks 1-9) — read these documents first:
  - `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Task 1)
  - `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` (Task 2)
  - `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Task 3)
  - `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` (Task 4)
  - `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` (Task 5)
  - `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` (Task 6)
  - `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md` (Task 7)
  - `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md` (Task 8)
  - `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` (Task 9)

## What to Do

1. **Review all prep task outputs** and extract key findings:
   - Task 2: Which internal_error patterns to fix first? How many quick wins?
   - Task 3: Which lexer subcategories to tackle? Grammar-fixable count?
   - Task 4: ISSUE_670 recommended fix — how many days?
   - Task 5: Any deferred item blockers? Effort adjustments?
   - Task 6: IndexOffset design ready? Grammar spike feasible?
   - Task 7: Table parsing fix complexity?
   - Task 8: MCP pairing fix complexity?
   - Task 9: Baseline metrics — targets correctly calibrated?

2. **Create day-by-day schedule (14 days):**
   - Assign workstreams to specific days
   - Sequence by dependency (deferred items and FIX_ROADMAP P1 first, as they unblock models)
   - Schedule checkpoints (Days 1, 6, 11 following Sprint 18 pattern)
   - Include pipeline retest days

3. **Define per-day:** tasks/subtasks, expected deliverables, integration risks, complexity estimates, Known Unknowns to verify

4. **Create contingency plans:**
   - What if ISSUE_670 fix takes longer than estimated?
   - What if grammar changes cause regressions?
   - What if internal_error classification reveals deeper issues?
   - Which items can be descoped if needed?

5. **Define acceptance criteria per checkpoint**

6. Document in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`

## Deliverables

- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` with complete sprint plan
- Day-by-day schedule (14 days)
- Checkpoint criteria (Days 1, 6, 11)
- Contingency plans for scope overruns
- Integration with FIX_ROADMAP priorities
- All unknowns integrated into schedule with verification assignments

## Verify Known Unknowns

This task verifies **All** remaining unknowns from `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`.

Review all unknowns and ensure each has been addressed by a previous task or is scheduled for verification during Sprint 19 Day 1. For any unknowns still marked `🔍 Status: INCOMPLETE` that should have been verified by Tasks 2-9, flag them and document what's still needed.

Update KNOWN_UNKNOWNS.md:
- Add a summary at the top showing verification progress (e.g., "22/26 verified, 4 deferred to Sprint 19 Day 1")
- Ensure all Critical/High unknowns are either VERIFIED or scheduled for Day 1 verification

## Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md`, update Task 10:
1. Change status from `🔵 NOT STARTED` to `✅ **COMPLETED** (current date)`
2. Fill in the **Changes** section with what was created/modified
3. Fill in the **Result** section with key findings summary
4. Check off all acceptance criteria checkboxes (`- [ ]` → `- [x]`)
5. Update Deliverables with check marks
6. Also update the **Summary > Success Criteria** section at the bottom — check off all completed items

## Update CHANGELOG.md

Add an entry under `## [Unreleased]` in `CHANGELOG.md` (after any existing unreleased entries):

```markdown
### Sprint 19 Prep Task 10: Plan Sprint 19 Detailed Schedule - YYYY-MM-DD

**Branch:** `planning/sprint19-task10`
**Status:** ✅ COMPLETE

#### Summary
[Brief summary — schedule structure, key sequencing decisions, contingency approach]

#### Deliverables
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` - [description]

#### Prep Phase Complete
All 10 prep tasks complete. Sprint 19 ready to begin:
- [N]/26 unknowns verified
- 14-day schedule with 3 checkpoints
- Contingency plans for [N] major risks
```

## Quality Gate

If any Python source files were modified (not just docs), run:
```bash
make typecheck && make lint && make format && make test
```
All checks must pass before committing.

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 19 Prep Task 10: Plan Sprint 19 Detailed Schedule

- Created PLAN.md with 14-day schedule across 5 workstreams
- [Summarize: key sequencing decisions, checkpoint criteria, contingencies]
- Reviewed all KNOWN_UNKNOWNS.md verification status
- Updated PREP_PLAN.md Task 10 status to COMPLETED; prep phase complete
- Updated CHANGELOG.md"

git push origin planning/sprint19-task10
```

## Create Pull Request

```bash
gh pr create \
  --base main \
  --title "Sprint 19 Prep Task 10: Plan Sprint 19 Detailed Schedule [PREP COMPLETE]" \
  --body "## Summary
Completes Prep Task 10: Plan Sprint 19 Detailed Schedule. **All 10 prep tasks are now complete.**

## Changes
- Created \`PLAN.md\` with complete 14-day Sprint 19 schedule
- Reviewed all Known Unknowns verification status
- Updated PREP_PLAN.md Task 10 → COMPLETED; prep phase marked complete
- Updated CHANGELOG.md

## Sprint 19 Prep Phase Complete
All 10 prep tasks complete. Sprint 19 is ready to begin.

## Acceptance Criteria
- [ ] Plan created with all 14 days detailed
- [ ] All 5 workstreams assigned to specific days
- [ ] FIX_ROADMAP items (ISSUE_670, 392, 399, 672) integrated into schedule
- [ ] Checkpoints defined (Days 1, 6, 11) with go/no-go criteria
- [ ] All days have integration risks and complexity estimates
- [ ] Known Unknowns verification schedule included
- [ ] Contingency plans documented for each major risk
- [ ] Pipeline retest scheduled (at least Day 11)
- [ ] All unknowns from KNOWN_UNKNOWNS.md integrated into daily schedule"
```

Then wait for reviewer comments. Use `gh pr view --comments` to check for feedback. Address any review comments before merging.
```
