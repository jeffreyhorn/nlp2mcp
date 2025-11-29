# Sprint 12 Preparation Task Prompts

**Purpose:** Comprehensive execution prompts for Sprint 12 prep tasks (Tasks 2-10)  
**Created:** 2025-11-29  
**Branch:** `planning/sprint12-prep`

---

## How to Use These Prompts

Each prompt below is a complete, copy-paste instruction set for executing one prep task. Follow this workflow:

1. **Copy entire prompt** for the task you're executing
2. **Execute the task** following all deliverables and acceptance criteria
3. **Verify unknowns** by updating KNOWN_UNKNOWNS.md with findings
4. **Update PREP_PLAN.md** to mark task complete
5. **Update CHANGELOG.md** with task summary
6. **Run quality checks** (if code changes made)
7. **Commit and push** using specified format
8. **Create PR** and wait for review

---

## Task 2 Prompt: Research Term Reduction Measurement Approaches

```
Execute Sprint 12 Prep Task 2: Research Term Reduction Measurement Approaches

CONTEXT:
You are working on Sprint 12 preparation for the nlp2mcp project. Task 1 (Known Unknowns) 
identified 4 measurement unknowns that need verification before Sprint 12 begins:
- Unknown 1.1: Baseline Metric Selection
- Unknown 1.3: Statistical Significance Thresholds
- Unknown 1.4: Granular vs. Aggregate Reporting
- Unknown 1.7: Actionability of Results

OBJECTIVE:
Research and validate the measurement methodology for quantifying transformation effectiveness 
before implementing benchmarking infrastructure in Sprint 12 Days 1-3.

WHY THIS MATTERS:
Sprint 11 implemented 11 transformation functions but deferred measurement. Success criterion 
"≥20% term reduction on ≥50% of models" cannot be validated without accurate measurement methodology.

Risk: Incorrect measurement could:
- False positive: Claim 20% reduction when actual <20% (invalidates Sprint 11 success)
- False negative: Miss actual 20% reduction due to undercounting

BACKGROUND:
Sprint 11 prototype (factoring_prototype_results.md) showed 39.2% average reduction on 6 test cases, but:
- Test cases were synthetic, not real GAMSLib models
- Measurement was manual (counting AST nodes)
- No systematic methodology documented

Current State:
- 11 transformation functions in `src/ir/transformations/`: factoring, fractions, division, 
  associativity, power rules, log rules, trig rules, nested operations, CSE (3 types)
- Transformations applied in simplification pipeline (`src/ir/simplification.py` or similar)
- No instrumentation for tracking applications or effectiveness

DELIVERABLES:
1. Create `docs/research/term_reduction_measurement.md` with:
   - Definitions (term, operation, reduction percentage)
   - Recommended approach (tool + methodology)
   - Instrumentation architecture
   - Prototype validation results
   - Baseline storage specification
   - Decision rationale and alternatives considered

2. Define "term" and "operation" with examples
   - Review SymPy's `count_ops()` implementation
   - Review Sprint 11 transformation implementations
   - Document decision with rationale

3. Recommended measurement tool/approach with benchmarks
   - Evaluate: SymPy count_ops(), expr.as_coefficients_dict(), custom AST visitor
   - Test on 5 sample expressions
   - Measure execution time (1000 iterations)
   - Document pros/cons

4. Instrumentation architecture for simplification pipeline
   - Map current pipeline flow
   - Identify entry/exit points
   - Design SimplificationMetrics data structure
   - Create architecture diagram

5. Prototype validation on 3 GAMSLib models (rbrock, mhw4d, maxmin)
   - Implement minimal instrumentation
   - Run with instrumentation
   - Calculate reduction percentages
   - Validate against manual counts (within 5%)

6. JSON baseline schema specification
   - Review existing baselines (baselines/parse_rate/sprint8.json)
   - Design schema compatible with CI tooling
   - Document example baseline

ACCEPTANCE CRITERIA:
- [ ] Clear definitions of term/operation that align with transformation implementations
- [ ] Measurement approach validated on 3 models (within 5% of manual counts)
- [ ] Instrumentation design reviewed and approved
- [ ] Baseline schema compatible with git and CI tooling
- [ ] Prototype demonstrates <1% performance overhead
- [ ] All measurement unknowns from Task 1 resolved with evidence

VERIFICATION COMMANDS:
```bash
# Verify research document exists
test -f docs/research/term_reduction_measurement.md && echo "✅ Research doc exists"

# Verify prototype measurements ran successfully
# (Check if prototype code produced output files or logs)

# Verify baseline format defined (example file exists)
# (Check for example baseline in research doc or separate file)
```

UNKNOWN VERIFICATION:
After completing research, update `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md`:

For Unknown 1.1 (Baseline Metric Selection):
- Update "Verification Results:" section with: ✅ VERIFIED or ❌ WRONG
- Add findings: Which metrics selected and why
- Add evidence: Test results, benchmarks, literature references
- Add decision: Final recommendation with rationale

For Unknown 1.3 (Statistical Significance Thresholds):
- Update verification results
- Document threshold selection (10%, 20%, etc.)
- Provide statistical justification

For Unknown 1.4 (Granular vs. Aggregate Reporting):
- Update verification results
- Document chosen approach (all-on vs all-off vs ablation)
- Estimate effort implications

For Unknown 1.7 (Actionability of Results):
- Update verification results
- Define decision criteria for interpreting results
- Link metrics to user-facing value

UPDATE PREP_PLAN.md:
1. Change Task 2 status from 🔵 NOT STARTED to ✅ COMPLETE
2. Fill in "Changes" section with list of files created/modified
3. Fill in "Result" section with 2-3 sentence summary of findings
4. Check off all deliverables: Change [ ] to [x]
5. Check off all acceptance criteria: Change [ ] to [x]

UPDATE CHANGELOG.md:
Add entry under "## [Unreleased]" section:

```markdown
### Sprint 12 Prep: Task 2 Complete - Term Reduction Measurement Research - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 2: Research Term Reduction Measurement Approaches

**Objective:** Research and validate measurement methodology for quantifying transformation effectiveness.

**Key Findings:**
- **Term definition:** [Your definition]
- **Operation definition:** [Your definition]
- **Recommended tool:** [SymPy count_ops / custom / hybrid]
- **Instrumentation approach:** [Before/after pipeline / per-transformation / other]
- **Baseline format:** JSON with [key fields]

**Validation Results:**
- rbrock.gms: [X]% reduction, [Y]% error vs manual count
- mhw4d.gms: [X]% reduction, [Y]% error vs manual count
- maxmin.gms: [X]% reduction, [Y]% error vs manual count
- Performance overhead: [X]% (target: <1%)

**Unknowns Verified:**
- ✅ Unknown 1.1: [Decision made - which metrics]
- ✅ Unknown 1.3: [Threshold: X%]
- ✅ Unknown 1.4: [Chosen approach]
- ✅ Unknown 1.7: [Decision criteria defined]

**Changes:**
- Added: `docs/research/term_reduction_measurement.md`
- Updated: `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` (verified 4 unknowns)
- Updated: `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 2 complete)

**Impact:**
- ✅ Sprint 12 Days 1-3 benchmarking implementation now de-risked
- ✅ Measurement methodology validated on real GAMSLib models
- ✅ Baseline format ready for CI integration
```

QUALITY GATE:
This task is research-only (no Python code changes expected). Skip quality checks unless 
prototype code was added to the repository.

If prototype code was added:
```bash
make typecheck && make lint && make format && make test
```

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 2: Research Term Reduction Measurement

- Created term_reduction_measurement.md with comprehensive research
- Defined term/operation for measurement consistency
- Validated measurement approach on 3 GAMSLib models (rbrock, mhw4d, maxmin)
- Designed instrumentation architecture for simplification pipeline
- Specified JSON baseline schema for git-tracked storage
- Verified 4 unknowns from Task 1: 1.1, 1.3, 1.4, 1.7

Key Findings:
- [Tool recommendation]: [rationale]
- Validation accuracy: [X]% average error across 3 models (target: <5%)
- Performance overhead: [X]% (target: <1%)
- Baseline format: [JSON structure]

Impact:
- De-risks Sprint 12 Days 1-3 benchmarking implementation
- Provides validated methodology for quantifying Sprint 11 transformation effectiveness
```

PULL REQUEST:
After committing and pushing:

```bash
gh pr create \
  --title "Sprint 12 Prep Task 2: Research Term Reduction Measurement" \
  --body "## Task 2: Research Term Reduction Measurement Approaches

**Objective:** Research and validate measurement methodology for quantifying transformation effectiveness.

### Deliverables
- ✅ `docs/research/term_reduction_measurement.md` - Comprehensive research
- ✅ Term/operation definitions with examples
- ✅ Measurement tool recommendation with benchmarks
- ✅ Instrumentation architecture design
- ✅ Prototype validation on 3 models (rbrock, mhw4d, maxmin)
- ✅ JSON baseline schema specification

### Key Findings
- **Recommended approach:** [Tool/methodology]
- **Validation accuracy:** [X]% average error (target: <5%)
- **Performance overhead:** [X]% (target: <1%)
- **Baseline format:** [JSON structure description]

### Unknowns Verified
- ✅ 1.1 Baseline Metric Selection: [Decision]
- ✅ 1.3 Statistical Significance Thresholds: [Threshold]
- ✅ 1.4 Granular vs. Aggregate Reporting: [Approach]
- ✅ 1.7 Actionability of Results: [Decision criteria]

### Impact
- De-risks Sprint 12 Days 1-3 benchmarking implementation
- Provides validated methodology for Sprint 11 transformation effectiveness measurement
- Baseline format ready for CI integration

### Files Changed
- Added: docs/research/term_reduction_measurement.md
- Updated: docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md
- Updated: docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md
- Updated: CHANGELOG.md

### Review Checklist
- [ ] Term/operation definitions clear and align with Sprint 11 transformations
- [ ] Measurement approach validated with <5% error
- [ ] Instrumentation design feasible for Sprint 12 implementation
- [ ] Baseline schema compatible with git and CI tooling
- [ ] All 4 unknowns resolved with evidence" \
  --base main \
  --head planning/sprint12-prep
```

Then wait for reviewer comments before proceeding to Task 3.
```

---

## Task 3 Prompt: Survey Tier 2 GAMSLib Model Candidates

```
Execute Sprint 12 Prep Task 3: Survey Tier 2 GAMSLib Model Candidates

CONTEXT:
You are working on Sprint 12 preparation for the nlp2mcp project. Task 1 (Known Unknowns) 
identified 5 unknowns related to Tier 2 expansion that need verification:
- Unknown 5.1: Model Selection Criteria
- Unknown 5.2: Target Parse Rate Feasibility
- Unknown 5.4: Regression Risk from Tier 2 Fixes
- Unknown 6.1: Workflow Coverage Identification (CI checklist)
- Unknown 6.2: Checklist Enforcement Mechanism

OBJECTIVE:
Research and select 10 Tier 2 GAMSLib models that maximize parser coverage while respecting 
complexity constraints (≤10h total blocker implementation).

WHY THIS MATTERS:
Sprint 12 Component 5 (Tier 2 Expansion) targets ≥50% parse rate on 10 new models. Poor model 
selection could result in:
- Too easy: Achieve 100% quickly but learn nothing new
- Too hard: Hit exotic features requiring >10h each, blocking sprint goal

Goal: Select models that reveal common Tier 2 features amenable to 4-6h implementation.

BACKGROUND:
Sprint 11 Tier 1 Results:
- 100% parse rate (10/10 models): circle, himmel16, hs62, mathopt1, maxmin, mhw4d, mhw4dx, 
  mingamma, rbrock, trig
- Unlocked via: nested indexing, function calls, comma-separated declarations, variable bounds, 
  indexed assignments

Tier 1 Selection Criteria (Sprint 8):
- Small-medium size (<200 lines)
- Diverse NLP patterns
- Representative of common GAMS idioms

Tier 2 Constraint: Must reveal new blockers while staying within 4-6h implementation budget.

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md` with:
   - Final list of 10 Tier 2 models with metadata (size, type, blockers)
   - Selection criteria and algorithm
   - Blocker complexity estimates
   - Expected parse rate outcome (conservative: 40-50%, optimistic: 60-70%)
   - Alternate models (fallback options)

2. Catalog 15-20 candidate models from GAMSLib
   - Filter: 100-500 lines, NLP/MCP type, not in Tier 1
   - Starting candidates: chenery, demandq, dipole, dispatch, egypt, fdesign, gasoil, 
     hydroelasticity, jbearing, karush
   - Research 5-10 additional candidates

3. Parse failure analysis for all candidates
   - Run `scripts/ingest_gamslib.py` on all candidates
   - Categorize failures by pattern (syntax, control flow, data structures, directives)
   - Count frequency of each blocker type

4. Blocker complexity estimates (Simple/Medium/Hard/Very Hard)
   - Simple: 1-2h (e.g., alias statement)
   - Medium: 3-5h (e.g., loop construct)
   - Hard: 6-10h (e.g., table data)
   - Very Hard: >10h (e.g., put file I/O)

5. Selection using diversity heuristic
   - Group candidates by primary blocker pattern
   - Select 1-2 models per blocker group
   - Prefer multiple simple blockers over single hard blocker
   - Ensure total estimated effort ≤6h

ACCEPTANCE CRITERIA:
- [ ] 10 models selected covering ≥5 different blocker patterns
- [ ] Total estimated blocker effort ≤6h (conservative estimate)
- [ ] No single blocker >5h effort (to fit Sprint 12 Day 4-6 timeline)
- [ ] Models diverse in size (100-500 lines) and domain
- [ ] Parse failure analysis validated via actual ingestion attempts
- [ ] Selection documented with clear rationale
- [ ] All Tier 2 unknowns from Task 1 resolved

VERIFICATION COMMANDS:
```bash
# Verify selection document exists
test -f docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md && echo "✅ Selection doc exists"

# Verify 10 models selected
grep -c "^### Model [0-9]" docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md
# Should output 10

# Verify diversity
grep "**Primary Blocker:**" docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md | sort | uniq -c
# Should show multiple blocker types
```

UNKNOWN VERIFICATION:
Update `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md`:

For Unknown 5.1 (Model Selection Criteria):
- Update verification results with selection algorithm used
- Document diversity metrics achieved
- Justify criteria choices

For Unknown 5.2 (Target Parse Rate Feasibility):
- Update with expected parse rate (40-70% range)
- Document which models likely to parse (by blocker complexity)
- Provide evidence from blocker analysis

For Unknown 5.4 (Regression Risk):
- Verify CI runs Tier 1 tests on all PRs
- Test intentional regression to confirm CI catches it
- Document rollback procedure

For Unknown 6.1 (CI Workflow Coverage):
- List all workflows in `.github/workflows/`
- Identify mandatory vs optional checks
- Draft initial checklist (5-10 items)

For Unknown 6.2 (Checklist Enforcement):
- Review existing PR template
- Decide on enforcement level (social vs automated)
- Document in verification results

UPDATE PREP_PLAN.md:
1. Change Task 3 status to ✅ COMPLETE
2. Fill in "Changes" section
3. Fill in "Result" section
4. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 3 Complete - Tier 2 Model Selection - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 3: Survey Tier 2 GAMSLib Model Candidates

**Objective:** Select 10 Tier 2 models for Sprint 12 parser expansion.

**Selected Models:**
1. [model1]: [blocker] ([effort estimate])
2. [model2]: [blocker] ([effort estimate])
... (list all 10)

**Selection Metrics:**
- **Blocker diversity:** [X] different patterns across 10 models
- **Total estimated effort:** [Y]h (target: ≤6h)
- **Expected parse rate:** [40-70%] based on blocker complexity
- **Alternate models:** [count] fallback options identified

**Blocker Distribution:**
- Simple (1-2h): [count] blockers affecting [X] models
- Medium (3-5h): [count] blockers affecting [X] models
- Hard (6-10h): [count] blockers (deferred if >1 per model)

**Unknowns Verified:**
- ✅ 5.1: Selection criteria = [diversity heuristic / other]
- ✅ 5.2: Expected parse rate = [X]% (conservative), [Y]% (optimistic)
- ✅ 5.4: Regression risk = [mitigated via CI]
- ✅ 6.1: CI workflows = [count] identified
- ✅ 6.2: Checklist enforcement = [social / automated]

**Changes:**
- Added: `docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md`
- Updated: KNOWN_UNKNOWNS.md (verified 5 unknowns)
- Updated: PREP_PLAN.md (Task 3 complete)
```

QUALITY GATE:
Research task only - skip quality checks unless scripts were modified.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 3: Survey Tier 2 GAMSLib Models

- Selected 10 Tier 2 models with [X] blocker patterns
- Total estimated effort: [Y]h (target: ≤6h)
- Expected parse rate: [40-70%] based on complexity analysis
- Identified [Z] alternate models for fallback
- Verified 5 unknowns: 5.1, 5.2, 5.4, 6.1, 6.2

Selection Highlights:
- [Blocker pattern 1]: [count] models ([effort])
- [Blocker pattern 2]: [count] models ([effort])
- [Blocker pattern 3]: [count] models ([effort])

Impact:
- De-risks Sprint 12 Days 4-6 Tier 2 implementation
- Ensures blocker effort fits 4-6h budget
- Maximizes parser coverage via diverse feature selection
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 3: Survey Tier 2 GAMSLib Model Candidates" \
  --body "## Task 3: Survey Tier 2 GAMSLib Model Candidates

**Objective:** Select 10 Tier 2 models for Sprint 12 parser expansion.

### Deliverables
- ✅ TIER_2_MODEL_SELECTION.md with 10 models
- ✅ Parse failure analysis for [X] candidates
- ✅ Blocker complexity estimates
- ✅ Selection rationale with diversity metrics
- ✅ Expected parse rate prediction
- ✅ Alternate model list

### Selected Models
[List 10 models with blocker and effort]

### Key Metrics
- **Blocker diversity:** [X] patterns
- **Total effort:** [Y]h (≤6h target)
- **Expected parse rate:** [range]%

### Unknowns Verified
- ✅ 5.1, 5.2, 5.4, 6.1, 6.2

### Files Changed
- Added: docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 4 Prompt: Research Multi-Metric Threshold Patterns

```
Execute Sprint 12 Prep Task 4: Research Multi-Metric Threshold Patterns

CONTEXT:
Task 1 identified 5 unknowns about multi-metric CI thresholds:
- Unknown 2.1: Metric Selection and Prioritization
- Unknown 2.2: Threshold Setting Methodology
- Unknown 2.3: CI Integration Architecture
- Unknown 2.4: Backward Compatibility with Sprint 11
- Unknown 6.3: Integration with Multi-Metric Thresholds (CI checklist)

OBJECTIVE:
Research best practices for multi-metric CI threshold checking to guide Sprint 12 Component 2 
implementation.

WHY THIS MATTERS:
Sprint 11 added CLI arguments (`--parse-rate-warn/fail`, `--convert-rate-warn/fail`, 
`--performance-warn/fail`) but didn't implement backend logic. This is technical debt that 
must be resolved in Sprint 12.

Risk: Naive implementation could result in:
- Flaky CI (thresholds too tight)
- Missed regressions (thresholds too loose)
- Poor UX (unclear failure messages)

BACKGROUND:
Current State (Sprint 11):
- `scripts/check_parse_rate_regression.py` accepts 6 new CLI arguments
- Arguments parsed but not used in threshold checking
- Only parse rate checked against single threshold (10% fail)

Sprint 12 Goal:
- Implement 3 metrics: parse_rate, convert_rate, performance
- Each metric has 2 thresholds: warn (5-20%), fail (10-50%)
- Exit codes: 0 (pass), 1 (warn), 2 (fail)
- PR comments show all 3 metrics with status indicators

DELIVERABLES:
1. Create `docs/research/multi_metric_thresholds.md` with:
   - Survey of ≥3 existing tools (GitHub Actions, pytest-benchmark, Codecov, Lighthouse CI)
   - Exit code strategy with decision rationale
   - Unified metrics collection architecture
   - PR comment format specification with example
   - Implementation checklist for Sprint 12

2. Survey multi-metric CI tools and patterns
   - Document how they handle multiple thresholds
   - Document reporting approaches
   - Document warn vs fail handling
   - Include screenshots/examples

3. Design exit code strategy
   - Option A: Exit on first failure (fast-fail)
   - Option B: Check all, exit with worst status (recommended)
   - Option C: Configurable (--fail-fast flag)
   - Choose and justify

4. Design unified metrics collection architecture
   - Extend measure_parse_rate.py vs new orchestrator vs extend check script
   - JSON schema for unified output
   - Integration with existing scripts

5. Design PR comment format
   - Table showing all 3 metrics
   - Status indicators (✅ Pass, ⚠️ Warn, ❌ Fail)
   - Threshold values and actual values
   - Links to baseline files

ACCEPTANCE CRITERIA:
- [ ] ≥3 tools surveyed with patterns documented
- [ ] Exit code strategy validated against UX goals
- [ ] Unified metrics architecture compatible with existing scripts
- [ ] PR comment format provides clear, actionable information
- [ ] All multi-metric unknowns from Task 1 resolved
- [ ] Design reviewed and approved

VERIFICATION COMMANDS:
```bash
test -f docs/research/multi_metric_thresholds.md && echo "✅ Research doc exists"
grep "## Exit Code Strategy" docs/research/multi_metric_thresholds.md
grep "## Unified Metrics Architecture" docs/research/multi_metric_thresholds.md
grep "## PR Comment Format" docs/research/multi_metric_thresholds.md
grep "| Metric | Threshold" docs/research/multi_metric_thresholds.md
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 2.1 (Metric Selection):
- Document which 3-4 metrics selected
- Justify prioritization
- Note any metrics deferred

For Unknown 2.2 (Threshold Setting):
- Document threshold values (warn/fail for each metric)
- Justify methodology (absolute vs relative, ±X%)
- Note recalibration strategy

For Unknown 2.3 (CI Integration):
- Document chosen architecture (extend which script)
- Justify integration approach
- Note compatibility with pytest

For Unknown 2.4 (Backward Compatibility):
- Verify Sprint 11 checks still work
- Document migration plan if needed
- Test side-by-side operation

For Unknown 6.3 (CI Checklist Integration):
- Document checklist item wording
- Link to CI job output
- Define override process

UPDATE PREP_PLAN.md:
1. Change Task 4 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 4 Complete - Multi-Metric Threshold Research - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 4: Research Multi-Metric Threshold Patterns

**Objective:** Research best practices for multi-metric CI threshold checking.

**Tools Surveyed:**
1. [Tool 1]: [key pattern learned]
2. [Tool 2]: [key pattern learned]
3. [Tool 3]: [key pattern learned]

**Key Decisions:**
- **Exit code strategy:** [Option B - check all, worst status]
- **Metrics architecture:** [Extend measure_parse_rate.py]
- **Thresholds:** parse_rate (5%/10%), convert_rate (5%/10%), performance (20%/50%)
- **PR comment format:** [Table with status indicators]

**Unknowns Verified:**
- ✅ 2.1: Metrics = parse_rate, convert_rate, performance
- ✅ 2.2: Thresholds = [values with rationale]
- ✅ 2.3: Architecture = [chosen approach]
- ✅ 2.4: Backward compatible = [yes/no with plan]
- ✅ 6.3: Checklist item = [wording]

**Changes:**
- Added: docs/research/multi_metric_thresholds.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md
```

QUALITY GATE:
Research only - skip unless scripts modified.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 4: Research Multi-Metric Thresholds

- Surveyed [X] CI tools for multi-metric patterns
- Designed exit code strategy: [chosen approach]
- Designed unified metrics architecture: [approach]
- Created PR comment format with status indicators
- Verified 5 unknowns: 2.1, 2.2, 2.3, 2.4, 6.3

Key Decisions:
- Metrics: parse_rate, convert_rate, performance
- Thresholds: [values]
- Architecture: [extend which script]

Impact:
- De-risks Sprint 12 Component 2 implementation
- Ensures backward compatibility with Sprint 11
- Provides clear UX for multi-metric failures
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 4: Research Multi-Metric Threshold Patterns" \
  --body "## Task 4: Research Multi-Metric Threshold Patterns

### Deliverables
- ✅ multi_metric_thresholds.md research document
- ✅ Survey of [X] tools
- ✅ Exit code strategy
- ✅ Unified metrics architecture
- ✅ PR comment format

### Key Decisions
[List main decisions]

### Unknowns Verified
- ✅ 2.1, 2.2, 2.3, 2.4, 6.3

### Files Changed
- Added: docs/research/multi_metric_thresholds.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 5 Prompt: Design JSON Diagnostics Schema

```
Execute Sprint 12 Prep Task 5: Design JSON Diagnostics Schema

CONTEXT:
Task 1 identified 3 JSON diagnostics unknowns:
- Unknown 3.1: Schema Design Complexity
- Unknown 3.2: Output Format Selection
- Unknown 3.3: Backward Compatibility

OBJECTIVE:
Design JSON schema for `--diagnostic-json` output to guide Sprint 12 Component 3 implementation.

WHY THIS MATTERS:
Sprint 11 implemented text table diagnostics. Sprint 12 adds JSON output for automation and 
trending. Poor schema design could result in:
- Breaking changes if schema evolves
- Missing data for historical analysis
- Inefficient serialization/deserialization

BACKGROUND:
Sprint 11 Text Diagnostics:
- 5-stage pipeline timing (Parse, Semantic, Simplification, IR Gen, MCP Gen)
- Simplification pass breakdowns
- Text table output via DiagnosticReport dataclass in src/ir/diagnostics.py
- <2% performance overhead

Sprint 12 JSON Requirements:
- Same data as text output (no new measurements)
- Machine-parseable for CI artifacts and trending
- Schema versioning for evolution

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md` with:
   - JSON schema with all required fields documented
   - Versioning policy (SemVer)
   - 3 example JSON files (success, partial, failure)
   - Field descriptions and data types
   - Implementation notes for Sprint 12

2. Review DiagnosticReport implementation in src/ir/diagnostics.py
   - Document all current fields
   - Identify data types and relationships

3. Design core schema structure
   - Top-level: schema_version, generated_at, model, summary, stages, simplification
   - Summary object: aggregate metrics
   - Stages array: per-stage details
   - Simplification object: pass breakdowns

4. Define versioning strategy
   - SemVer (MAJOR.MINOR.PATCH)
   - schema_version field at top level
   - Migration guide for version changes

5. Create 3 example JSON files
   - Success: rbrock.gms (all stages pass)
   - Partial: Model with simplification warnings
   - Failure: Parse error (early termination)
   - Validate with jq

ACCEPTANCE CRITERIA:
- [ ] Schema covers all data from text diagnostics
- [ ] Versioning strategy defined and documented
- [ ] Example JSON files validate successfully
- [ ] Schema compatible with CI artifact storage
- [ ] All JSON diagnostics unknowns from Task 1 resolved
- [ ] Schema reviewed and approved

VERIFICATION COMMANDS:
```bash
test -f docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md && echo "✅ Schema doc exists"

for file in docs/planning/EPIC_2/SPRINT_12/examples/*.json; do
  jq . "$file" > /dev/null && echo "✅ $file valid JSON"
done

grep "schema_version" docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 3.1 (Schema Complexity):
- Document whether direct serialization or transformation needed
- Note any complexity issues discovered
- Verify no parser refactoring required

For Unknown 3.2 (Output Format):
- Document chosen format (NDJSON / JSON array / single object)
- Justify for use cases (CLI, MCP, CI)
- Note size implications

For Unknown 3.3 (Backward Compatibility):
- Document --format flag approach
- Verify text remains default
- Note test coverage strategy

UPDATE PREP_PLAN.MD:
1. Change Task 5 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 5 Complete - JSON Diagnostics Schema - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 5: Design JSON Diagnostics Schema

**Objective:** Design JSON schema for diagnostic output.

**Schema Overview:**
- **Version:** 1.0.0 (SemVer)
- **Format:** [NDJSON / JSON object / other]
- **Top-level fields:** schema_version, generated_at, model, summary, stages, simplification
- **Versioning policy:** [MAJOR.MINOR.PATCH strategy]

**Example Scenarios:**
- Success: rbrock.gms (all 5 stages complete)
- Partial: [model] (warnings in simplification)
- Failure: [model] (parse error, early termination)

**Unknowns Verified:**
- ✅ 3.1: Schema complexity = [direct serialization / transformation]
- ✅ 3.2: Output format = [NDJSON / JSON / other]
- ✅ 3.3: Backward compatible = [--format flag, text default]

**Changes:**
- Added: docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md
- Added: docs/planning/EPIC_2/SPRINT_12/examples/*.json (3 examples)
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md
```

QUALITY GATE:
Research only - skip unless code added.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 5: Design JSON Diagnostics Schema

- Designed JSON schema v1.0.0 for diagnostic output
- Created 3 example JSON files (success, partial, failure)
- Defined SemVer versioning policy
- Verified backward compatibility via --format flag
- Verified 3 unknowns: 3.1, 3.2, 3.3

Schema Highlights:
- Format: [NDJSON / JSON object]
- Fields: [key top-level fields]
- Versioning: SemVer with migration guides

Impact:
- De-risks Sprint 12 Component 3 implementation
- Enables CI artifact storage and trending
- Maintains backward compatibility with text output
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 5: Design JSON Diagnostics Schema" \
  --body "## Task 5: Design JSON Diagnostics Schema

### Deliverables
- ✅ JSON_DIAGNOSTICS_SCHEMA.md
- ✅ JSON schema v1.0.0
- ✅ Versioning policy (SemVer)
- ✅ 3 example JSON files (validated)

### Schema Overview
[Describe key fields and structure]

### Unknowns Verified
- ✅ 3.1, 3.2, 3.3

### Files Changed
- Added: docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md
- Added: docs/planning/EPIC_2/SPRINT_12/examples/*.json
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 6 Prompt: Draft PATH Licensing Email Template

```
Execute Sprint 12 Prep Task 6: Draft PATH Licensing Email Template

CONTEXT:
Task 1 identified 4 PATH solver unknowns:
- Unknown 4.1: License Compatibility with MIT
- Unknown 4.2: CI Installation Method
- Unknown 4.3: PATH Model Availability
- Unknown 4.4: Integration Scope (Defer vs. Implement)

OBJECTIVE:
Draft professional email template requesting PATH solver CI usage clarification to enable 
Sprint 12 Component 4 (PATH Solver CI Integration).

WHY THIS MATTERS:
Sprint 11 research revealed PATH academic license terms unclear for CI/cloud usage. Sprint 12 
requires written confirmation from maintainer before implementing PATH in GitHub Actions.

Timeline: Email response may take 1-4 weeks (async). Sending early maximizes response window 
during Sprint 12.

BACKGROUND:
PATH Solver Licensing (from Sprint 11 research):
- Free version: 300 variables / 2000 nonzeros (sufficient for smoke tests)
- Academic license: Unrestricted size, annual renewal, CI/cloud usage NOT documented
- Commercial license: Explicit cloud rights, not applicable for open-source project

Sprint 11 Decision: Defer PATH CI integration, prototype IPOPT alternative (<1% accuracy difference).

Sprint 12 Goal: Clarify licensing, implement PATH if approved, document decision if denied.

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md` with:
   - Professional email template ready to send
   - Specific questions about CI usage (GitHub Actions, public repo, frequency)
   - Confirmed contact information (ferris@cs.wisc.edu)
   - Follow-up scenario decision tree (approve/deny/no response/self-hosted)
   - Timeline expectations documented

2. Review Sprint 11 PATH research
   - Read docs/planning/EPIC_2/SPRINT_11/path_smoke_test_integration.md
   - Extract key licensing questions
   - Identify contact information

3. Draft professional email
   - Introduction: Who we are, what nlp2mcp does
   - Current usage: IPOPT for CI
   - Specific questions (3+):
     1. Does academic license permit GitHub Actions (cloud CI)?
     2. Are there restrictions on CI frequency (per-PR vs nightly)?
     3. Is use in public open-source repositories permitted?
   - Request: Written confirmation for documentation
   - Alternatives: Self-hosted runner if cloud CI disallowed

4. Define follow-up scenarios
   - Approved: Proceed with PATH CI implementation (Sprint 12 Day 7-8)
   - Denied: Document decision, keep IPOPT, note limitations
   - No response by Day 7: Defer PATH to Sprint 13, proceed with IPOPT
   - Self-hosted required: Evaluate feasibility (cost, maintenance)

ACCEPTANCE CRITERIA:
- [ ] Email template professional and specific
- [ ] All licensing questions addressed
- [ ] Contact information verified current
- [ ] Follow-up scenarios cover all outcomes
- [ ] Template ready to send on Sprint 12 Day 1
- [ ] All PATH licensing unknowns from Task 1 addressed

VERIFICATION COMMANDS:
```bash
test -f docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md && echo "✅ Email template exists"
grep -c "?" docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md  # Should show ≥3
grep "ferris@cs.wisc.edu" docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 4.1 (License Compatibility):
- Document research on current PATH license
- Note questions to be answered by email response
- Link to PATH documentation reviewed

For Unknown 4.2 (CI Installation):
- Research apt/conda availability
- Document installation methods found
- Note questions for email if unclear

For Unknown 4.3 (Model Availability):
- Survey GAMSLib for MCP models using PATH
- Count models available for testing
- Assess sufficiency

For Unknown 4.4 (Integration Scope):
- Define minimum viable PATH integration
- Document deferral criteria
- Estimate effort for full integration

UPDATE PREP_PLAN.md:
1. Change Task 6 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 6 Complete - PATH Licensing Email - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 6: Draft PATH Licensing Email Template

**Objective:** Prepare PATH solver licensing clarification request.

**Email Template:**
- **Recipient:** Prof. Michael C. Ferris (ferris@cs.wisc.edu)
- **Questions:** [Count] specific questions about CI usage
- **Tone:** Professional, respectful of maintainer's time
- **Timeline:** 1-4 week response expectation

**Follow-Up Scenarios:**
- **Approved:** Implement PATH in Sprint 12 Days 7-8
- **Denied:** Document decision, continue with IPOPT
- **No response:** Defer to Sprint 13
- **Self-hosted required:** [Feasibility assessment]

**Unknowns Verified:**
- ✅ 4.1: License research complete, questions drafted
- ✅ 4.2: Installation methods = [apt/conda/other]
- ✅ 4.3: PATH models available = [count] in GAMSLib
- ✅ 4.4: Integration scope = [defer criteria defined]

**Changes:**
- Added: docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md
```

QUALITY GATE:
Research only - skip.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 6: Draft PATH Licensing Email

- Created professional email template for PATH licensing clarification
- Identified [X] specific questions about GitHub Actions CI usage
- Verified contact information (ferris@cs.wisc.edu)
- Defined follow-up scenarios for all response types
- Verified 4 unknowns: 4.1, 4.2, 4.3, 4.4

Email Highlights:
- Professional tone respectful of maintainer time
- Specific questions about cloud CI, public repos, frequency
- Alternatives offered (self-hosted runner)

Impact:
- De-risks Sprint 12 Component 4 (PATH integration)
- Enables early send on Sprint 12 Day 1 for maximum response time
- Clear decision tree for all response scenarios
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 6: Draft PATH Licensing Email Template" \
  --body "## Task 6: Draft PATH Licensing Email Template

### Deliverables
- ✅ PATH_LICENSING_EMAIL.md
- ✅ Professional email template
- ✅ [X] specific licensing questions
- ✅ Follow-up scenario decision tree
- ✅ Timeline expectations

### Email Overview
[Summarize key questions and approach]

### Unknowns Verified
- ✅ 4.1, 4.2, 4.3, 4.4

### Files Changed
- Added: docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 7 Prompt: Prototype Simplification Metrics Collection

```
Execute Sprint 12 Prep Task 7: Prototype Simplification Metrics Collection

CONTEXT:
Task 1 identified 2 unknowns to verify via prototyping:
- Unknown 1.5: Performance Overhead Measurement
- Unknown 1.2: Baseline Collection Approach (partial verification)

Task 2 defined measurement methodology. Task 7 validates it works in practice.

OBJECTIVE:
Prototype and validate simplification metrics collection on 3 GAMSLib models to prove 
measurement approach before full Sprint 12 implementation.

WHY THIS MATTERS:
Task 2 defines methodology (term/operation definitions, instrumentation points). Task 7 proves 
it works before committing to full Sprint 12 Days 1-3 implementation.

Risk Mitigation: Prototyping catches measurement issues early (edge cases, performance problems, 
missing data).

BACKGROUND:
Sprint 11 implemented 11 transformations but deferred measurement. Prototype must prove:
1. Measurements are accurate (within 5% of manual counts)
2. Overhead is acceptable (<1% execution time)
3. Instrumentation doesn't break existing functionality

Test Models:
- rbrock.gms: Simple (few transformations, easy to validate manually)
- mhw4d.gms: Medium complexity (more transformations, realistic)
- maxmin.gms: Complex (nested indexing, stress test for instrumentation)

DELIVERABLES:
1. Create `docs/research/simplification_metrics_prototype.md` with:
   - Metrics collected (with example data)
   - Accuracy validation (spot check results)
   - Performance overhead (benchmark results)
   - Issues encountered (edge cases, bugs)
   - Recommendations for Sprint 12 (adjustments needed)

2. Implement SimplificationMetrics class
   - Fields: model, ops_before, ops_after, terms_before, terms_after, 
     transformations_applied (dict), execution_time_ms, iterations
   - Methods: count_operations(), count_terms(), record_transformation(), to_dict()
   - Location: prototypes/ or src/ir/

3. Instrument simplification pipeline
   - Locate entry point (simplify_expression())
   - Add metrics collection before/after
   - Update transformations to call record_transformation()
   - Measure execution time

4. Run prototype on 3 models
   - Collect metrics for rbrock, mhw4d, maxmin
   - Manually count operations/terms for 5 expressions each (spot check)
   - Compare automated vs manual counts (target: <5% error)

5. Measure performance overhead
   - Run 100 iterations without instrumentation
   - Run 100 iterations with instrumentation
   - Calculate overhead percentage (target: <1%)

ACCEPTANCE CRITERIA:
- [ ] Metrics class captures all required data fields
- [ ] Instrumentation works on all 3 test models without errors
- [ ] Accuracy validation: All spot checks <5% error
- [ ] Performance overhead: <1% execution time increase
- [ ] No regressions: All tests still pass with instrumentation
- [ ] Prototype proves measurement approach viable for Sprint 12

VERIFICATION COMMANDS:
```bash
test -f docs/research/simplification_metrics_prototype.md && echo "✅ Prototype results exist"
test -f prototypes/simplification_metrics_rbrock.json && echo "✅ rbrock metrics collected"
grep "Accuracy:" docs/research/simplification_metrics_prototype.md
grep "Overhead:" docs/research/simplification_metrics_prototype.md
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 1.5 (Performance Overhead):
- Document actual overhead measured ([X]%)
- Verify <1% target met
- Note instrumentation approach used

For Unknown 1.2 (Baseline Collection - partial):
- Test disabling transformations temporarily
- Verify parser still works
- Document approach for baseline collection

UPDATE PREP_PLAN.md:
1. Change Task 7 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 7 Complete - Simplification Metrics Prototype - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 7: Prototype Simplification Metrics Collection

**Objective:** Validate measurement approach on 3 GAMSLib models.

**Validation Results:**
- **rbrock.gms:** [X]% reduction, [Y]% error vs manual (target: <5%)
- **mhw4d.gms:** [X]% reduction, [Y]% error vs manual
- **maxmin.gms:** [X]% reduction, [Y]% error vs manual
- **Average error:** [Y]% (target: <5%)

**Performance Overhead:**
- **Without instrumentation:** [X]ms average (100 runs)
- **With instrumentation:** [Y]ms average (100 runs)
- **Overhead:** [Z]% (target: <1%)

**Unknowns Verified:**
- ✅ 1.5: Performance overhead = [X]% (target: <1%)
- ✅ 1.2: Baseline collection approach = [can disable transformations]

**Changes:**
- Added: docs/research/simplification_metrics_prototype.md
- Added: prototypes/SimplificationMetrics class (if in repo)
- Added: prototypes/simplification_metrics_*.json (3 model results)
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md
```

QUALITY GATE:
If prototype code added to repository:
```bash
make typecheck && make lint && make format && make test
```

All tests must pass before committing.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 7: Prototype Simplification Metrics

- Implemented SimplificationMetrics class with [fields]
- Instrumented simplification pipeline at [entry point]
- Validated on 3 models: rbrock, mhw4d, maxmin
- Accuracy: [X]% average error (target: <5%) ✅
- Performance: [Y]% overhead (target: <1%) ✅
- Verified 2 unknowns: 1.5, 1.2

Validation Highlights:
- rbrock: [reduction]%, [error]%
- mhw4d: [reduction]%, [error]%
- maxmin: [reduction]%, [error]%

Impact:
- Proves measurement approach viable for Sprint 12 Days 1-3
- Validates <1% overhead target achievable
- Identifies [any adjustments needed] for full implementation
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 7: Prototype Simplification Metrics Collection" \
  --body "## Task 7: Prototype Simplification Metrics Collection

### Deliverables
- ✅ SimplificationMetrics class
- ✅ Instrumented pipeline
- ✅ Metrics for 3 models
- ✅ Accuracy validation (<5% error)
- ✅ Performance benchmark (<1% overhead)
- ✅ simplification_metrics_prototype.md

### Validation Results
[Table of results]

### Unknowns Verified
- ✅ 1.5, 1.2

### Quality Gate
- ✅ make typecheck: passed
- ✅ make lint: passed
- ✅ make test: [X] passed

### Files Changed
- Added: docs/research/simplification_metrics_prototype.md
- Added: prototypes/* (if applicable)
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 8 Prompt: Create Tier 2 Blocker Analysis Template

```
Execute Sprint 12 Prep Task 8: Create Tier 2 Blocker Analysis Template

CONTEXT:
Task 1 identified 1 unknown:
- Unknown 5.3: Blocker Documentation Process

Task 3 selected 10 Tier 2 models. Task 8 creates systematic template for analyzing their 
parse failures.

OBJECTIVE:
Create systematic template for analyzing Tier 2 parse failures to guide Sprint 12 Days 4-6 
implementation priority.

WHY THIS MATTERS:
Sprint 12 Component 5 (Tier 2 Expansion) requires classifying parse failures by blocker 
frequency. Systematic template ensures:
- Consistent failure categorization (enables frequency analysis)
- Effort estimation accuracy (prevents scope creep)
- Implementation priority ranking (maximize parse rate gain)

BACKGROUND:
Sprint 8-11 Tier 1 Patterns:
- Blockers ranged from simple (1-2h: function calls) to complex (6-8h: nested indexing)
- Frequency-driven prioritization worked well (≥3 models = HIGH priority)
- Effort estimates improved over sprints (learning curve)

Tier 2 Challenge: Unknown blocker distribution - could be:
- Best case: 5 simple blockers × 2 models each (10h total, achievable)
- Worst case: 10 unique hard blockers (>100h total, not achievable)

Template Goal: Enable rapid categorization during Sprint 12 Days 4-5.

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md` with:
   - Blocker classification schema (frequency, complexity, category, criticality)
   - Priority calculation formula
   - Markdown template for blocker analysis
   - Prioritization algorithm documentation
   - 2-3 example blocker analyses

2. Design classification schema
   - Frequency: 1, 2-3, 4-5, 6+ models
   - Complexity: Simple (1-2h), Medium (3-5h), Hard (6-10h), Very Hard (>10h)
   - Category: Syntax, Control Flow, Data Structure, Directive, Other
   - Criticality: Must-have vs nice-to-have for ≥50% parse rate

3. Define priority formula
   - Priority = (Frequency × 10) + (5 - Complexity_Score)
   - High frequency + low complexity = highest priority
   - Example: 5 models × Simple = 54 (highest)

4. Create markdown template
   - Blocker name
   - Frequency, affected models, error message, example syntax
   - Complexity estimate, effort hours, rationale
   - GAMS manual reference
   - Parser changes needed (checklist)
   - Priority score

5. Document prioritization algorithm
   - Fill template for all blockers
   - Calculate priority scores
   - Sort by priority
   - Cumulative sum: Stop at ≥6h budget
   - Implement top N that fit budget

6. Create 2-3 example analyses
   - alias statement (likely Simple)
   - loop construct (likely Medium)
   - $if directive (likely Medium)

ACCEPTANCE CRITERIA:
- [ ] Classification schema covers all relevant dimensions
- [ ] Priority formula tested on examples (produces sensible ranking)
- [ ] Template captures all information for implementation planning
- [ ] Prioritization algorithm fits Sprint 12 Day 4-6 budget (6h total)
- [ ] Example analyses validate template usability
- [ ] Team review and approval completed

VERIFICATION COMMANDS:
```bash
test -f docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md && echo "✅ Template exists"
grep "**Frequency:**" docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md
grep "**Complexity Estimate:**" docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md
grep "Priority =" docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md
grep -c "## Blocker:" docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md  # ≥2
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 5.3 (Blocker Documentation Process):
- Document template structure chosen
- Note information captured per blocker
- Describe storage location (GitHub issues vs markdown vs inline)

UPDATE PREP_PLAN.md:
1. Change Task 8 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 8 Complete - Tier 2 Blocker Template - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 8: Create Tier 2 Blocker Analysis Template

**Objective:** Create systematic template for Tier 2 parse failure analysis.

**Template Components:**
- **Classification schema:** Frequency, Complexity, Category, Criticality
- **Priority formula:** (Frequency × 10) + (5 - Complexity_Score)
- **Blocker template:** [fields included]
- **Prioritization algorithm:** [cumulative sum to 6h budget]

**Example Blockers:**
1. alias statement: Priority = [score] (Simple, [X] models)
2. loop construct: Priority = [score] (Medium, [X] models)
3. $if directive: Priority = [score] (Medium, [X] models)

**Unknowns Verified:**
- ✅ 5.3: Template = [markdown files in docs/planning/]

**Changes:**
- Added: docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md
```

QUALITY GATE:
Research only - skip.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 8: Create Tier 2 Blocker Template

- Created systematic blocker analysis template
- Defined classification schema: Frequency, Complexity, Category, Criticality
- Designed priority formula: (Frequency × 10) + (5 - Complexity_Score)
- Created markdown template with all required fields
- Documented prioritization algorithm (6h budget)
- Provided 3 example blocker analyses
- Verified unknown 5.3

Impact:
- Enables rapid, consistent Tier 2 failure categorization
- Ensures blocker effort fits Sprint 12 Days 4-6 budget
- Maximizes parse rate gain via frequency-driven prioritization
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 8: Create Tier 2 Blocker Analysis Template" \
  --body "## Task 8: Create Tier 2 Blocker Analysis Template

### Deliverables
- ✅ TIER_2_BLOCKER_TEMPLATE.md
- ✅ Classification schema
- ✅ Priority formula
- ✅ Markdown template
- ✅ Prioritization algorithm
- ✅ 3 example analyses

### Template Overview
[Describe key components]

### Unknown Verified
- ✅ 5.3

### Files Changed
- Added: docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 9 Prompt: Set Up Baseline Storage Infrastructure

```
Execute Sprint 12 Prep Task 9: Set Up Baseline Storage Infrastructure

CONTEXT:
Task 1 identified 2 unknowns:
- Unknown 1.2: Baseline Collection Approach (full verification)
- Unknown 1.6: Baseline Drift Over Time

Task 2 defined baseline format. Task 9 creates infrastructure.

OBJECTIVE:
Create directory structure and initial baseline files for Sprint 12 metrics tracking 
(term reduction, multi-metric thresholds).

WHY THIS MATTERS:
Sprint 12 Components 1 & 2 require baseline storage for regression detection. Setting up 
infrastructure during prep prevents Day 1 blockers and ensures consistent format from start.

BACKGROUND:
Existing Baselines:
- baselines/parse_rate/sprint8.json: Parse rate baselines (git-tracked)
- baselines/performance/: Performance baselines (may use git-lfs if large)

Sprint 12 New Baselines:
- baselines/simplification/baseline_sprint11.json: Term reduction metrics per model
- Extended parse rate JSON with convert_rate and performance metrics

DELIVERABLES:
1. Create directory structure
   - baselines/simplification/ with README.md
   - baselines/multi_metric/ with README.md

2. Create format documentation (2 README files)
   - Schema specification (from Task 2/4)
   - Example baseline entry
   - Update procedure
   - Versioning policy

3. Create placeholder baseline files (valid JSON)
   - baselines/simplification/baseline_sprint11.json
   - baselines/multi_metric/baseline_sprint12.json
   - Use schema from Task 2/4

4. Configure git tracking
   - Add to git (not git-lfs - files are small)
   - Ensure JSON files get proper line endings (.gitattributes)
   - Stage files but don't commit yet

5. Create update script stub
   - scripts/update_baselines.sh
   - Stub functions for simplification and multi-metric
   - Make executable
   - Document usage

6. Update infrastructure documentation
   - Create/update docs/infrastructure/BASELINES.md
   - Document directory structure
   - Reference format specs
   - Explain update procedures

ACCEPTANCE CRITERIA:
- [ ] Directories exist and follow established patterns
- [ ] README files document format and update procedures
- [ ] Placeholder baselines have correct schema (valid JSON)
- [ ] Git tracking configured (files staged, not committed)
- [ ] Update script executable and documented
- [ ] Infrastructure docs reviewed and approved

VERIFICATION COMMANDS:
```bash
test -d baselines/simplification && echo "✅ simplification/ exists"
test -d baselines/multi_metric && echo "✅ multi_metric/ exists"
test -f baselines/simplification/README.md && echo "✅ simplification README exists"
test -f baselines/multi_metric/README.md && echo "✅ multi_metric README exists"
test -f baselines/simplification/baseline_sprint11.json && echo "✅ simplification baseline exists"
test -f baselines/multi_metric/baseline_sprint12.json && echo "✅ multi-metric baseline exists"
jq . baselines/simplification/baseline_sprint11.json > /dev/null
jq . baselines/multi_metric/baseline_sprint12.json > /dev/null
test -x scripts/update_baselines.sh && echo "✅ update script executable"
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 1.2 (Baseline Collection Approach):
- Document how to disable transformations (if tested)
- Verify parser works without transformations
- Note baseline storage location

For Unknown 1.6 (Baseline Drift):
- Document baseline versioning scheme (git SHA / sprint number / timestamp)
- Define invalidation triggers (transformation code changes)
- Note recollection procedure

UPDATE PREP_PLAN.md:
1. Change Task 9 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 9 Complete - Baseline Storage Infrastructure - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 9: Set Up Baseline Storage Infrastructure

**Objective:** Create baseline storage infrastructure for Sprint 12 metrics.

**Infrastructure Created:**
- **Directories:** baselines/simplification/, baselines/multi_metric/
- **README files:** Format documentation for both baseline types
- **Placeholder baselines:** baseline_sprint11.json, baseline_sprint12.json (valid JSON)
- **Update script:** scripts/update_baselines.sh (executable)
- **Documentation:** docs/infrastructure/BASELINES.md

**Baseline Formats:**
- **Simplification:** [schema fields]
- **Multi-metric:** [schema fields]
- **Versioning:** [git SHA / sprint number / timestamp]

**Unknowns Verified:**
- ✅ 1.2: Baseline collection = [disable transformations approach]
- ✅ 1.6: Baseline drift = [versioning scheme, invalidation triggers]

**Changes:**
- Added: baselines/simplification/ directory with README, placeholder baseline
- Added: baselines/multi_metric/ directory with README, placeholder baseline
- Added: scripts/update_baselines.sh
- Added/Updated: docs/infrastructure/BASELINES.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md
```

QUALITY GATE:
Infrastructure only - skip unless Python code in update script needs checking.

If update_baselines.sh contains Python:
```bash
make typecheck && make lint
```

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 9: Set Up Baseline Storage Infrastructure

- Created baselines/simplification/ with README and placeholder
- Created baselines/multi_metric/ with README and placeholder
- Created scripts/update_baselines.sh (executable)
- Updated docs/infrastructure/BASELINES.md
- Configured git tracking (small files, no git-lfs needed)
- Verified 2 unknowns: 1.2, 1.6

Infrastructure Highlights:
- Simplification baseline schema: [key fields]
- Multi-metric baseline schema: [key fields]
- Versioning: [approach]

Impact:
- Prevents Sprint 12 Day 1 blockers
- Ensures consistent baseline format from start
- Ready for Component 1 & 2 implementation
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep Task 9: Set Up Baseline Storage Infrastructure" \
  --body "## Task 9: Set Up Baseline Storage Infrastructure

### Deliverables
- ✅ baselines/simplification/ directory
- ✅ baselines/multi_metric/ directory
- ✅ 2 README files (format documentation)
- ✅ 2 placeholder baselines (valid JSON)
- ✅ scripts/update_baselines.sh
- ✅ Infrastructure documentation

### Schema Overview
[Describe baseline formats]

### Unknowns Verified
- ✅ 1.2, 1.6

### Files Changed
- Added: baselines/simplification/README.md
- Added: baselines/simplification/baseline_sprint11.json
- Added: baselines/multi_metric/README.md
- Added: baselines/multi_metric/baseline_sprint12.json
- Added: scripts/update_baselines.sh
- Added/Updated: docs/infrastructure/BASELINES.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments.
```

---

## Task 10 Prompt: Plan Sprint 12 Detailed Schedule

```
Execute Sprint 12 Prep Task 10: Plan Sprint 12 Detailed Schedule

CONTEXT:
Task 1 identified 2 process unknowns:
- Unknown 7.1: Sprint 12 Scope Management
- Unknown 7.2: Dependency on External Research

Tasks 2-9 have provided research findings. Task 10 synthesizes all findings into 
comprehensive Sprint 12 plan.

OBJECTIVE:
Create comprehensive Sprint 12 day-by-day plan incorporating all prep task findings and 
resolving all unknowns identified in Task 1.

WHY THIS MATTERS:
Sprint 11 demonstrated value of detailed planning with checkpoints (Days 3, 5, 7). Sprint 12 
requires even more precision due to:
- Multiple HIGH priority items (measurement + multi-metric)
- Decision points (Day 3: term reduction results, Day 7: PATH licensing)
- Resource constraints (19-28h scope in 10-day sprint)

Success Pattern: Sprint 11 achieved 100% goals with 10% buffer utilization via daily planning.

BACKGROUND:
Sprint 12 Components (from PROJECT_PLAN.md):
- HIGH: Term reduction benchmarking (4-6h), multi-metric thresholds (3-4h)
- MEDIUM: JSON diagnostics (2h), PATH integration (3-5h), Tier 2 expansion (4-6h), CI checklist (1h)
- LOW: 6 additional components (18-28h, conditional)

Sprint 12 Checkpoints:
- Day 3: Term reduction results (decision: add LOW priority transformations if <20%)
- Day 6: Tier 2 parse rate measured (target: ≥50%)
- Day 7: PATH licensing decision (implement/document/defer)

Sprint 12 Buffer: ~5 hours (Day 9: 2-3h, Day 10: 1-2h, embedded: 1-2h)

DELIVERABLES:
1. Create `docs/planning/EPIC_2/SPRINT_12/PLAN.md` with:
   - Executive Summary
   - Scope & Goals (from PROJECT_PLAN.md)
   - Prep Task Synthesis (findings from Tasks 1-9)
   - Day-by-Day Schedule (Days 1-10)
   - Checkpoint Criteria (Days 3, 6, 7)
   - Risk Register with mitigations
   - Success Criteria (PRIMARY and SECONDARY)
   - Buffer Strategy

2. Synthesize prep task findings (60-90 min)
   - Review all deliverables from Tasks 1-9
   - Identify resolved unknowns
   - Identify remaining unknowns requiring Sprint 12 investigation
   - Create synthesis summary

3. Allocate hours to days (60-75 min)
   - Day 1-3: Measurement & Validation (7-10h)
   - Day 4-6: Tier 2 Expansion (4-6h)
   - Day 7-8: Polish & Integration (6-8h)
   - Day 9: Buffer & Optional (2-3h)
   - Day 10: Final Validation (1-2h)
   - Total: 20-29h (fits 19-28h target with slack)

4. Create day-by-day schedule (90-120 min)
   - For each day 1-10:
     - Focus: Primary component(s)
     - Tasks: Specific implementation steps
     - Deliverables: Concrete outputs
     - Decision Points: Checkpoints and pivots
     - Risk Mitigation: Known issues and contingencies
     - Success Criteria: Checkboxes for completion
     - Time Budget: Hours allocated

5. Define checkpoint criteria (30-45 min)
   - Day 3: Term reduction ≥20% on ≥50% models? Decision tree.
   - Day 6: Tier 2 parse rate ≥50%? Partial success at 40-49%.
   - Day 7: PATH response? Approve/deny/no response decisions.

6. Create risk register (30-45 min)
   - Risk 1: Benchmarking reveals <20% reduction
   - Risk 2: Tier 2 blockers too complex
   - Risk 3: PATH no response
   - Risk 4: Convert rate tracking reveals bugs
   - For each: mitigation, contingency, assignment

ACCEPTANCE CRITERIA:
- [ ] All 10 days planned with specific tasks and deliverables
- [ ] Hour allocation fits 19-28h scope (±10% tolerance)
- [ ] All 3 checkpoints (Days 3, 6, 7) have decision criteria
- [ ] All prep task findings incorporated
- [ ] All known unknowns from Task 1 addressed or assigned
- [ ] Risk register covers all identified Sprint 12 risks
- [ ] Buffer strategy documented (5h allocation)
- [ ] Team review and approval completed

VERIFICATION COMMANDS:
```bash
test -f docs/planning/EPIC_2/SPRINT_12/PLAN.md && echo "✅ PLAN.md exists"
grep -c "### Day [0-9]" docs/planning/EPIC_2/SPRINT_12/PLAN.md  # Should output 10
grep "Checkpoint" docs/planning/EPIC_2/SPRINT_12/PLAN.md | wc -l  # Should show ≥3
grep "Success Criteria" docs/planning/EPIC_2/SPRINT_12/PLAN.md
grep "Time Budget:" docs/planning/EPIC_2/SPRINT_12/PLAN.md
```

UNKNOWN VERIFICATION:
Update KNOWN_UNKNOWNS.md:

For Unknown 7.1 (Scope Management):
- Document Sprint 10-11 actual velocity
- Calculate Sprint 12 realistic capacity
- Define minimum viable Sprint 12
- Document deferral decision criteria

For Unknown 7.2 (External Dependencies):
- Identify external blockers (PATH email, etc.)
- Document plan B for each dependency
- Front-load external research (complete by Task 6)

UPDATE PREP_PLAN.md:
1. Change Task 10 status to ✅ COMPLETE
2. Fill in Changes and Result sections
3. Check off all deliverables and acceptance criteria
4. Update PREP_PLAN Summary section with "All 10 prep tasks complete"

UPDATE CHANGELOG.md:
```markdown
### Sprint 12 Prep: Task 10 Complete - Sprint 12 Detailed Schedule - YYYY-MM-DD

**Branch:** `planning/sprint12-prep`  
**Status:** ✅ COMPLETE

#### Task 10: Plan Sprint 12 Detailed Schedule

**Objective:** Create comprehensive day-by-day Sprint 12 plan.

**Schedule Overview:**
- **Days 1-3:** Measurement & Validation ([X]h)
- **Days 4-6:** Tier 2 Expansion ([X]h)
- **Days 7-8:** Polish & Integration ([X]h)
- **Day 9:** Buffer & Optional ([X]h)
- **Day 10:** Final Validation ([X]h)
- **Total:** [X]h (target: 19-28h)

**Checkpoints:**
- **Day 3:** Term reduction ≥20% on ≥50% models?
- **Day 6:** Tier 2 parse rate ≥50%?
- **Day 7:** PATH licensing decision

**Risk Register:**
- [Count] risks identified with mitigations
- External dependencies: [list]
- Contingency plans: [summary]

**Unknowns Verified:**
- ✅ 7.1: Scope = [capacity]h, minimum viable = [components]
- ✅ 7.2: External deps = [list], plan B = [summary]

**Prep Task Synthesis:**
- ✅ All 10 prep tasks complete
- ✅ [X]/27 unknowns fully verified
- ✅ Sprint 12 ready to begin

**Changes:**
- Added: docs/planning/EPIC_2/SPRINT_12/PLAN.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md

---

### Sprint 12 Prep COMPLETE - Ready for Sprint Execution - YYYY-MM-DD

**Status:** ✅ ALL PREP TASKS COMPLETE

**Summary:**
All 10 Sprint 12 preparation tasks successfully completed. 27 known unknowns identified 
and verified. Sprint 12 ready to begin.

**Prep Tasks Completed:**
1. ✅ Known Unknowns List (27 unknowns, 7 categories)
2. ✅ Term Reduction Measurement Research
3. ✅ Tier 2 Model Selection (10 models)
4. ✅ Multi-Metric Threshold Research
5. ✅ JSON Diagnostics Schema
6. ✅ PATH Licensing Email
7. ✅ Simplification Metrics Prototype
8. ✅ Tier 2 Blocker Template
9. ✅ Baseline Storage Infrastructure
10. ✅ Sprint 12 Detailed Schedule

**Total Prep Effort:** [X]h (estimated: 21-28h)

**Key Deliverables:**
- 27 unknowns verified across 7 categories
- [X] research documents created
- [X] planning documents created
- [X] infrastructure components set up
- 10-day Sprint 12 plan ready

**Sprint 12 Start Date:** [Date after prep completion]
```

QUALITY GATE:
Research/planning only - skip.

COMMIT MESSAGE:
```
Complete Sprint 12 Prep Task 10: Plan Sprint 12 Detailed Schedule

- Created comprehensive 10-day Sprint 12 PLAN.md
- Synthesized findings from all 9 prep tasks
- Allocated [X]h across Days 1-10 (target: 19-28h)
- Defined 3 checkpoint decision criteria (Days 3, 6, 7)
- Created risk register with [X] risks and mitigations
- Verified 2 unknowns: 7.1, 7.2

Schedule Highlights:
- Days 1-3: Measurement & Validation ([X]h)
- Days 4-6: Tier 2 Expansion ([X]h)
- Days 7-8: Polish & Integration ([X]h)
- Buffer: [X]h (Days 9-10)

Impact:
- ✅ All 10 Sprint 12 prep tasks complete
- ✅ 27/27 unknowns verified
- ✅ Sprint 12 ready to begin with comprehensive day-by-day plan
```

PULL REQUEST:
```bash
gh pr create \
  --title "Sprint 12 Prep COMPLETE: All 10 Tasks Done" \
  --body "## Sprint 12 Preparation COMPLETE ✅

All 10 preparation tasks successfully completed. Sprint 12 ready to begin.

### Task 10: Plan Sprint 12 Detailed Schedule

**Deliverables:**
- ✅ PLAN.md with 10-day schedule
- ✅ Prep task synthesis
- ✅ Checkpoint decision criteria
- ✅ Risk register
- ✅ Hour allocation ([X]h total)

### Prep Summary

**All Tasks Complete:**
1. ✅ Known Unknowns (27 unknowns, 7 categories)
2. ✅ Term Reduction Measurement
3. ✅ Tier 2 Model Selection (10 models)
4. ✅ Multi-Metric Thresholds
5. ✅ JSON Diagnostics Schema
6. ✅ PATH Licensing Email
7. ✅ Simplification Metrics Prototype
8. ✅ Tier 2 Blocker Template
9. ✅ Baseline Storage Infrastructure
10. ✅ Sprint 12 Detailed Schedule

**Unknowns Verified:** 27/27 ✅

**Total Prep Effort:** [X]h (estimated: 21-28h)

**Sprint 12 Status:** Ready to begin

### Files Changed (Task 10)
- Added: docs/planning/EPIC_2/SPRINT_12/PLAN.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md

### Review Checklist
- [ ] All 10 days have specific tasks and deliverables
- [ ] Hour allocation realistic (19-28h scope)
- [ ] Checkpoint criteria clear and actionable
- [ ] Risk register comprehensive
- [ ] Ready to merge and begin Sprint 12

**Next Steps:** Merge PR, begin Sprint 12 execution" \
  --base main \
  --head planning/sprint12-prep
```

Wait for reviewer comments. After approval and merge, Sprint 12 preparation is complete 
and sprint execution can begin.
```

---

## Appendix: Common Patterns

### Updating KNOWN_UNKNOWNS.md

For each unknown verified during a task:

1. Find the unknown section (e.g., "### 1.1 Baseline Metric Selection")
2. Update "Verification Results:" from "*(To be completed during Task N)*" to:

```markdown
**Verification Results:** ✅ VERIFIED (Task N, YYYY-MM-DD)

**Findings:**
- [Key finding 1]
- [Key finding 2]
- [Key finding 3]

**Evidence:**
- [Test result, benchmark, reference, etc.]
- [Data supporting decision]

**Decision:**
- [Final recommendation with rationale]
- [Alternative approaches considered and rejected]

**Impact:**
- [How this affects Sprint 12 implementation]
```

If an assumption was WRONG:

```markdown
**Verification Results:** ❌ WRONG - Assumption invalidated (Task N, YYYY-MM-DD)

**Original Assumption:** [What we thought]

**Actual Finding:** [What we discovered]

**Implications:**
- [How this changes Sprint 12 plan]
- [New approach required]

**Revised Approach:**
- [Updated methodology]
```

### Marking Tasks Complete in PREP_PLAN.md

1. Change status: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
2. Fill in Changes section with bulleted list of files
3. Fill in Result section with 2-3 sentence summary
4. Check off deliverables: `- [ ]` → `- [x]`
5. Check off acceptance criteria: `- [ ]` → `- [x]`

### Quality Gate Order

Always run in this order (if applicable):

```bash
make typecheck  # Type checking with mypy
make lint       # Linting with flake8/ruff
make format     # Format checking with black
make test       # Full test suite
```

Only proceed to commit if ALL pass.

### Commit Message Structure

```
[Single line summary (50-72 chars)]

[Blank line]

- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

[Key Findings/Highlights section]
- [Highlight 1]
- [Highlight 2]

[Impact section]
- [Impact 1]
- [Impact 2]
```

---

**End of Prep Task Prompts**

All prompts ready for execution. Execute tasks sequentially (2→3→4→5→6→7→8→9→10), 
waiting for PR review between each task before proceeding to the next.
