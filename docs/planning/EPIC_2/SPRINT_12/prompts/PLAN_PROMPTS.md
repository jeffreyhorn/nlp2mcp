# Sprint 12 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 12 (Days 1-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint 12 Overview:**
- **Epic:** Epic 2 - Multi-Solver MCP Server
- **Duration:** 10 working days
- **Total Capacity:** 80 hours (10 days × 8 hours/day)
- **Allocated Effort:** 75-84 hours
- **Theme:** Measurement, Polish, and Tier 2 Expansion

---

## Day 1 Prompt: Measurement Infrastructure Setup + Extended Testing

**Branch:** `sprint12-day1-measurement-setup`

**Objective:** Implement term reduction measurement infrastructure with comprehensive testing and validation

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 1 (Term Reduction Measurement) unknowns 1.1-1.7
- Read `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` - Review Task 2 (Term Reduction Measurement Research) and Task 7 (Simplification Metrics Prototype)
- Review `docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md` - Email template to send on Day 1

**Tasks to Complete (7-8 hours):**

1. **Send PATH licensing email to ferris@cs.wisc.edu** (15 min)
   - Use template from `docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md`
   - Track response for Day 7 checkpoint
   - Save sent email confirmation for documentation

2. **Implement SimplificationMetrics class** (75-90 min)
   - Location: `src/ir/metrics.py` (new file)
   - Based on Task 7 prototype EnhancedSimplificationMetrics
   - Fields: model, ops_before, ops_after, terms_before, terms_after, execution_time_ms, transformations_applied
   - Methods: to_dict(), calculate_reductions()
   - Add comprehensive docstrings with usage examples

3. **Implement count_terms() function** (45-60 min)
   - Location: `src/ir/metrics.py`
   - Use Task 7 prototype implementation (validated 0% error)
   - Recursive AST traversal to count operation nodes
   - Add docstring with examples
   - Unit tests: create `tests/unit/test_metrics.py` with 15+ test cases (expanded from prototype's 10)

4. **Instrument simplification pipeline** (60-75 min)
   - Update `src/ir/simplification_pipeline.py`
   - Add optional metrics collection to apply() method
   - Collect before/after metrics when enabled
   - No changes to transformation functions (instrumentation only)
   - Ensure backward compatibility (metrics disabled by default)

5. **Extended testing and validation** (180-240 min)
   - Edge case testing: nested expressions, complex factorizations
   - Performance profiling: measure overhead on large expressions (>500 operations)
   - Integration testing: run on 5 Tier 1 models (subset validation)
   - Documentation: Add inline examples and usage notes to metrics.py
   - Code review preparation: ensure clean, well-documented code

**Deliverables:**
- [ ] PATH email sent (tracked in email client)
- [ ] `src/ir/metrics.py` with SimplificationMetrics and count_terms()
- [ ] `tests/unit/test_metrics.py` with ≥15 test cases
- [ ] Instrumented SimplificationPipeline (backward compatible)
- [ ] All existing tests still passing (make test-fast)
- [ ] Extended testing complete (edge cases, performance profiling)
- [ ] Integration validation on 5 Tier 1 models
- [ ] Code documentation complete and ready for review

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] SimplificationMetrics class passes all tests
  - [ ] count_terms() validated on 15+ expressions (including Task 7 examples)
  - [ ] Pipeline instrumentation works on rbrock.gms without errors
  - [ ] make test-fast completes in <30s
  - [ ] PATH email sent and delivery confirmed
  - [ ] Extended testing demonstrates <10% overhead on realistic expressions
  - [ ] Integration validation shows consistent results across 5 models
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 1 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 1 section
  - Document PATH email sent
  - Note any implementation decisions made
  - See `docs/planning/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 1: Measurement Infrastructure Setup" \
                --body "Completes Day 1 of Sprint 12 PLAN.md

   ## Deliverables
   - SimplificationMetrics class with count_terms()
   - 15+ unit tests for metrics
   - Instrumented SimplificationPipeline
   - Extended validation on 5 Tier 1 models
   - PATH licensing email sent
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 247-295)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   # Check if review is complete
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 247-295)
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 2: Term Reduction Measurement Research)
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 7: Simplification Metrics Prototype)
- `docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md`

---

## Day 2 Prompt: Baseline Collection & Multi-Metric Backend + Extended Validation

**Branch:** `sprint12-day2-baseline-multi-metric`

**Objective:** Create measurement script, collect baseline data, implement multi-metric threshold backend, and validate with synthetic models

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 1 (unknowns 1.1-1.7) and Category 2 (unknowns 2.1-2.4)
- Read `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` - Review Task 2 (Measurement Research) and Task 4 (Multi-Metric Threshold Research)
- Ensure Day 1 deliverables are complete (SimplificationMetrics available)

**Tasks to Complete (8-9 hours):**

1. **Create measure_simplification.py script** (120-150 min)
   - Location: `scripts/measure_simplification.py`
   - CLI: `--model MODEL` or `--model-set tier1` 
   - Functionality:
     - Load model and parse to AST
     - Run simplification with metrics collection
     - Aggregate results across all models
     - Output JSON matching baselines/simplification/README.md schema
   - Output: JSON to stdout or `--output FILE`
   - Example: `./scripts/measure_simplification.py --model-set tier1 --output baselines/simplification/baseline_sprint11.json`

2. **Populate baseline_sprint11.json** (45-60 min)
   - Run measure_simplification.py on all 10 Tier 1 models
   - Validate JSON against schema (jq validation)
   - Update metadata: commit SHA, timestamp, sprint "sprint11"
   - Commit baseline to git
   - Run extended validation (verify on 3 additional synthetic models)

3. **Implement multi-metric threshold backend** (75-90 min)
   - Update `scripts/check_parse_rate_regression.py`
   - Add read_baseline() to parse multi-metric JSON
   - Implement check_all_metrics() function:
     - Parse rate: compare current vs baseline
     - Convert rate: compare current vs baseline
     - Performance: compare avg time vs baseline
   - Exit code logic: 0 (pass), 1 (warn), 2 (fail)
   - Return worst status across all 3 metrics

4. **Extended validation and synthetic testing** (180-240 min)
   - Create 3 synthetic test models with known characteristics:
     - Model A: Heavy factorization opportunities (expected: 40-50% reduction)
     - Model B: Minimal simplification (expected: <10% reduction)
     - Model C: Mixed transformations (expected: 20-30% reduction)
   - Run measure_simplification.py on synthetic models
   - Validate against expected reduction percentages
   - Test multi-metric threshold logic with edge cases
   - Document synthetic model creation for future testing

**Deliverables:**
- [ ] `scripts/measure_simplification.py` (executable, --help works)
- [ ] `baselines/simplification/baseline_sprint11.json` (valid JSON, ≥10 models)
- [ ] Updated `scripts/check_parse_rate_regression.py` with multi-metric support
- [ ] Unit tests for multi-metric threshold logic
- [ ] Extended validation on synthetic models
- [ ] 3 synthetic test models created and documented
- [ ] Synthetic model results match expected reduction ranges

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] measure_simplification.py runs on all 10 Tier 1 models without errors
  - [ ] baseline_sprint11.json matches schema exactly
  - [ ] Multi-metric backend passes unit tests (warn/fail thresholds trigger correctly)
  - [ ] Baseline committed to git with proper metadata
  - [ ] Extended validation passes on synthetic models
  - [ ] Synthetic models demonstrate measurement accuracy (within 5% of expected)
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 2 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 2 section
  - Document baseline results (high-level summary)
  - Note any unexpected findings
  - See `docs/planning/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 2: Baseline Collection & Multi-Metric Backend" \
                --body "Completes Day 2 of Sprint 12 PLAN.md

   ## Deliverables
   - measure_simplification.py script
   - baseline_sprint11.json with 10 Tier 1 models
   - Multi-metric threshold backend
   - 3 synthetic test models with validation
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 297-367)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 297-367)
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 2: Term Reduction Measurement Research)
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 4: Multi-Metric Threshold Research)
- `baselines/simplification/README.md` (JSON schema definition)

---

## Day 3 Prompt: Validation, Analysis & Checkpoint

**Branch:** `sprint12-day3-validation-checkpoint`

**Objective:** Analyze baseline results, implement full multi-metric CI integration, perform comprehensive validation, and make critical Day 3 checkpoint decision

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review all Category 1 and Category 2 unknowns
- Read `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` - Review Task 4 (Multi-Metric Threshold Research)
- Ensure Day 2 deliverables complete (baseline_sprint11.json available)
- Review `docs/planning/EPIC_2/SPRINT_12/PLAN.md` lines 1011-1090 for checkpoint decision tree

**Tasks to Complete (7-8 hours):**

1. **Analyze baseline_sprint11.json results** (45-60 min)
   - Calculate aggregate metrics:
     - Average term reduction percentage across 10 models
     - Average operation reduction percentage
     - Models meeting ≥20% threshold
   - Identify top 3 most effective transformations
   - Create analysis summary in `docs/SIMPLIFICATION_BENCHMARKS.md`
   - Include per-transformation effectiveness breakdown

2. **Extend measure_parse_rate.py for unified metrics** (45-60 min)
   - Add `--all-metrics` flag
   - Track parse_rate, convert_rate, performance in single JSON
   - Output format matching `baselines/multi_metric/README.md` schema
   - Populate `baselines/multi_metric/baseline_sprint12.json` placeholder

3. **Update CI workflow for multi-metric** (30-45 min)
   - Edit `.github/workflows/gamslib-regression.yml`
   - Replace single parse-rate check with multi-metric check
   - Add all 6 threshold arguments (warn/fail for each metric)
   - Update PR comment template to show all 3 metrics
   - Add example PR comment to documentation

4. **Extended validation and edge case testing** (180-240 min)
   - Validate measurement accuracy on edge cases:
     - Very large expressions (>500 operations)
     - Deeply nested expressions (>10 levels)
     - Expressions with no simplification opportunities
   - Cross-validate top 3 models with manual analysis
   - Test multi-metric thresholds with simulated regressions
   - Document edge case behavior

5. **Prepare comprehensive checkpoint evidence** (60-90 min)
   - Compile detailed reduction statistics
   - Create visualization/tables for retrospective
   - Document transformation effectiveness ranking
   - Prepare decision evidence for checkpoint meeting

**Deliverables:**
- [ ] `docs/SIMPLIFICATION_BENCHMARKS.md` with detailed analysis
- [ ] Updated `measure_parse_rate.py` with --all-metrics
- [ ] `baselines/multi_metric/baseline_sprint12.json` populated
- [ ] Updated `.github/workflows/gamslib-regression.yml`
- [ ] Extended validation complete on edge cases
- [ ] Checkpoint evidence prepared and compiled
- [ ] Commit: "Complete Components 1 & 2: Benchmarking and Multi-Metric"

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Checkpoint decision made based on actual data
  - [ ] All 3 metrics (parse, convert, performance) tracked in CI
  - [ ] PR comment format validated (table with ✅/⚠️/❌)
  - [ ] Components 1 & 2 complete and functional
  - [ ] Per-transformation effectiveness documented
  - [ ] Edge case validation demonstrates robustness
  - [ ] Comprehensive checkpoint evidence compiled
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 3 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 3 section
  - **CRITICAL:** Document Day 3 checkpoint decision with full rationale
  - Record actual term reduction percentage achieved
  - Note which scenario (A or B) will be followed on Day 9
  - See `docs/planning/incremental_documentation_guide.md` for checkpoint documentation template
- [ ] **CHECKPOINT:** Document Day 3 checkpoint outcome in `PLAN.md`:
  - [ ] If ≥20% average: ✅ SUCCESS - Document results, proceed to Day 4, Day 9 Scenario B
  - [ ] If 15-19% average: ⚠️ PARTIAL - Document actual reduction, proceed to Day 4
  - [ ] If <15% average: ❌ NEEDS IMPROVEMENT - Proceed to Day 4, Day 9 Scenario A (implement LOW priority transformations)

**Day 3 Checkpoint Decision Tree:**

```
Baseline Analysis Complete
│
├─ Average ≥20% reduction on ≥5 models?
│  ├─ YES → ✅ SUCCESS
│  │        - Document results in SIMPLIFICATION_BENCHMARKS.md
│  │        - Proceed to Tier 2 (Day 4)
│  │        - Sprint 12 primary goal achieved
│  │        - Day 9: Scenario B (extended features)
│  │
│  └─ NO → Evaluate reduction percentage
│           │
│           ├─ 15-19% average → ⚠️ PARTIAL SUCCESS
│           │                   - Document actual reduction
│           │                   - Proceed to Tier 2 (Day 4)
│           │                   - Day 9: Consider partial transformations
│           │                   - Note: Below target but useful improvement
│           │
│           └─ <15% average → ❌ NEEDS IMPROVEMENT
│                             - Proceed to Tier 2 (Day 4)
│                             - Day 9: Implement LOW priority transformations (Scenario A)
│                             - Re-measure simplification with new patterns
│                             - Target: ≥20% with additional transformations
│                             - Fallback: Document limitation if still <15%
```

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 3: Validation, Analysis & Checkpoint" \
                --body "Completes Day 3 of Sprint 12 PLAN.md

   ## Deliverables
   - SIMPLIFICATION_BENCHMARKS.md analysis
   - Multi-metric CI integration complete
   - Edge case validation complete
   
   ## Day 3 Checkpoint Result
   [Document checkpoint outcome here: SUCCESS/PARTIAL/NEEDS IMPROVEMENT]
   - Average term reduction: XX%
   - Models meeting ≥20%: X/10
   - Decision: [Scenario A or B for Day 9]
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 369-447)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 369-447)
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 1011-1090) - Checkpoint Decision Tree
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 4: Multi-Metric Threshold Research)
- `baselines/multi_metric/README.md` (JSON schema)

---

## Day 4 Prompt: Tier 2 Model Analysis & High-Priority Blockers

**Branch:** `sprint12-day4-tier2-analysis`

**Objective:** Download Tier 2 candidates, analyze parse failures, prioritize blockers, and implement 2 high-priority blockers

**⚠️ TIME-BOX WARNING:** Maximum 8 hours on this day. Stop at 8h regardless of status.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 5 (Tier 2 Models) unknowns 5.1-5.4
- Read `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` - Review Task 3 (Tier 2 Model Selection) and Task 8 (Tier 2 Blocker Analysis Template)
- Review `docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md` - Selected 10 models and blocker predictions
- Review `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md` - Template for blocker analysis

**Tasks to Complete (8h max - TIME-BOXED):**

1. **Download 10 Tier 2 candidate models** (15 min)
   - Use `scripts/download_tier2_candidates.sh` from Task 3
   - Models: chenery, jbearing, fct, chem, water, gastrans, process, least, like, bearing
   - Location: `tests/fixtures/gamslib/tier2/`

2. **Run parse failure analysis** (60-75 min)
   - Use `scripts/analyze_tier2_candidates.py` from Task 3
   - Classify failures by blocker pattern
   - Generate `tests/fixtures/tier2_candidates/analysis_results.json`
   - Validate against Task 3 predictions
   - Identify frequency and complexity of each blocker

3. **Prioritize blockers using Task 8 template** (60-75 min)
   - Apply classification schema (Frequency, Complexity, Category, Criticality)
   - Calculate priority scores for each blocker
   - Create `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md`
   - Fill template for all discovered blockers
   - Sort by priority, select top blockers fitting 12h budget (expanded from 6h)

4. **Implement Blocker #1** (90-120 min, HIGH priority)
   - Based on priority analysis
   - Likely: special_chars_in_identifiers (1.5h) OR predefined_constants (1h)
   - Update lexer/grammar
   - Add AST nodes if needed
   - Unit tests (8-12 test cases)
   - Integration test (affected model parses)

5. **Implement Blocker #2** (90-120 min, HIGH priority)
   - Based on priority analysis
   - Likely: multiple_alias_declaration (1.5h)
   - Grammar extension
   - Symbol table updates
   - Unit tests
   - Integration test

6. **Create implementation plan for Days 5-6** (30 min)
   - Document remaining blockers for Days 5-6
   - Effort estimates (with 80h capacity, allocate 10-12h more for Tier 2)
   - Stretch goal: 60%+ Tier 2 parse rate (6+ models)

**Deliverables:**
- [ ] 10 Tier 2 models downloaded
- [ ] Parse failure analysis complete (JSON results)
- [ ] `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md` with prioritized blockers
- [ ] 2 high-priority blockers implemented and tested
- [ ] 2-3 Tier 2 models now parsing
- [ ] Implementation plan for Days 5-6 (10-12h scope)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Blocker analysis matches template format
  - [ ] Priority scores calculated for all blockers
  - [ ] ≥2 blockers fully implemented and tested
  - [ ] ≥2 Tier 2 models parsing (cumulative)
  - [ ] All Tier 1 tests still passing (no regressions)
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 4 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 4 section
  - Update parse rate table (add row if Tier 2 rate changed)
  - Document which blockers were implemented
  - Note time-box adherence (stopped at 8h?)
  - See `docs/planning/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 4: Tier 2 Model Analysis & High-Priority Blockers" \
                --body "Completes Day 4 of Sprint 12 PLAN.md

   ## Deliverables
   - 10 Tier 2 models downloaded
   - TIER_2_BLOCKER_ANALYSIS.md with priorities
   - 2 high-priority blockers implemented
   - 2-3 Tier 2 models now parsing
   
   ## Parse Rate Update
   - Tier 2: X/10 (XX%)
   - Overall: (10 + X)/20 (XX%)
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 449-525)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 449-525)
- `docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md`
- `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_TEMPLATE.md`
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 3 and Task 8)

---

## Day 5 Prompt: Tier 2 Medium-Priority Blocker Implementation

**Branch:** `sprint12-day5-tier2-medium-blockers`

**Objective:** Implement 3 medium-priority Tier 2 blockers to reach 40-50% Tier 2 parse rate

**⚠️ TIME-BOX WARNING:** Maximum 8 hours on this day. Stop at 8h regardless of status. Goal: 4-5 models parsing.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 5 unknowns
- Ensure Day 4 deliverables complete (TIER_2_BLOCKER_ANALYSIS.md with prioritized list)
- Review `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md` - Implementation plan for Days 5-6

**Tasks to Complete (8h max - TIME-BOXED):**

1. **Implement Blocker #3** (90-120 min, MEDIUM priority)
   - Based on Day 4 priority analysis
   - Likely: inline_descriptions (2h) or partial thereof
   - Grammar changes for optional description strings
   - AST node updates
   - Unit tests for basic cases

2. **Implement Blocker #4** (90-120 min, MEDIUM priority)
   - Based on Day 4 priority analysis
   - Example: table_wildcard_domain or model_specific_constructs
   - Grammar extension
   - Symbol table updates if needed
   - Unit tests

3. **Implement Blocker #5** (90-120 min, MEDIUM priority)
   - Based on Day 4 priority analysis
   - Push toward ≥50% Tier 2 parse rate (5/10 models)
   - Full testing and integration validation

4. **Polish and integration testing** (60-90 min)
   - Run full Tier 1 regression suite
   - Validate all implemented blockers on Tier 2 models
   - Fix any edge cases or conflicts
   - Document implemented patterns

**Deliverables:**
- [ ] 3 medium-priority blockers fully implemented
- [ ] Unit tests passing for all implemented blockers
- [ ] 3-5 Tier 2 models now parsing (cumulative: 5+ total)
- [ ] All Tier 1 tests still passing
- [ ] Code committed: "Tier 2: Implement medium-priority blockers (Day 5)"

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] ≥3 blockers fully implemented and tested
  - [ ] ≥4-5 Tier 2 models parsing (cumulative, 40-50% rate)
  - [ ] All Tier 1 tests still passing (no regressions)
  - [ ] Code quality: typecheck ✅, lint ✅, format ✅
  - [ ] Time-box respected (stopped at 8h if needed)
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 5 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 5 section
  - Update parse rate table (Tier 2 and overall rates)
  - Document which 3 blockers were implemented
  - Note if time-box limit was reached
  - See `docs/planning/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 5: Tier 2 Medium-Priority Blockers" \
                --body "Completes Day 5 of Sprint 12 PLAN.md

   ## Deliverables
   - 3 medium-priority blockers implemented
   - 4-5 Tier 2 models now parsing (cumulative)
   - All Tier 1 tests still passing
   
   ## Parse Rate Update
   - Tier 2: X/10 (XX%)
   - Overall: (10 + X)/20 (XX%)
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 527-587)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 527-587)
- `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md` (Day 4 output)

---

## Day 6 Prompt: Tier 2 Stretch Blockers & Checkpoint

**Branch:** `sprint12-day6-tier2-stretch-checkpoint`

**Objective:** Implement stretch blocker, measure Tier 2 parse rate, make Day 6 checkpoint decision, and conditionally analyze additional candidates

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 5 unknowns
- Ensure Day 5 deliverables complete (4-5 Tier 2 models parsing)
- Review `docs/planning/EPIC_2/SPRINT_12/PLAN.md` lines 1091-1139 for Day 6 checkpoint decision tree

**Tasks to Complete (7-8 hours - includes contingent analysis):**

1. **Implement Blocker #6** (90-120 min, STRETCH goal)
   - Stretch toward ≥60% Tier 2 parse rate (6+ models)
   - Based on Day 4-5 progress
   - May be partial implementation if complex

2. **Measure Tier 2 parse rate** (30 min)
   - Run ingest_gamslib.py on all 10 Tier 2 models
   - Calculate parse rate: (models parsed / 10) × 100%
   - Update `baselines/multi_metric/baseline_sprint12.json` with Tier 2 results
   - Document which models parse and which fail

3. **Create Tier 2 documentation** (45-60 min)
   - `docs/TIER_2_MODELS.md`: List of 10 models with status
   - `docs/TIER_2_IMPLEMENTATION_PLAN.md`: Blockers implemented, remaining work
   - Document expected vs actual results
   - Detailed blocker analysis for remaining failures

4. **Extended Tier 2 candidate analysis** (90-120 min, CONDITIONAL on ≥60%)
   - **IF ≥60% achieved:** Analyze 5 additional Tier 2 candidates
   - Identify next-sprint blockers
   - Create roadmap for 80%+ overall parse rate
   - Document in TIER_2_IMPLEMENTATION_PLAN.md
   - **IF <60%:** Skip this task, use time for documentation polish

**Deliverables:**
- [ ] Tier 2 parse rate measured and documented
- [ ] `docs/TIER_2_MODELS.md` with detailed status
- [ ] `docs/TIER_2_IMPLEMENTATION_PLAN.md`
- [ ] Extended candidate analysis (if ≥60% achieved)
- [ ] Commit: "Complete Tier 2 expansion (≥50% parse rate)"

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Tier 2 parse rate ≥50% (5/10 models)
  - [ ] Overall parse rate ≥75% (15/20 models: 10 Tier 1 + 5 Tier 2)
  - [ ] All blockers documented with effort estimates
  - [ ] Extended analysis complete (if exceeds expectations)
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 6 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 6 section
  - Update parse rate table (final Tier 2 and overall rates)
  - **CRITICAL:** Document Day 6 checkpoint decision with rationale
  - Note whether extended analysis was performed
  - See `docs/planning/incremental_documentation_guide.md` for checkpoint template
- [ ] **CHECKPOINT:** Document Day 6 checkpoint outcome in `PLAN.md`:
  - [ ] If ≥60% (6+ models): ✅ EXCEEDS - Document success, performed extended analysis
  - [ ] If 50-59% (5 models): ✅ MEETS - Document success, proceed to Day 7
  - [ ] If 40-49% (4 models): ⚠️ PARTIAL - Document partial success, proceed to Day 7
  - [ ] If <40% (<4 models): ❌ BELOW - Document limitation, focus on polish

**Day 6 Checkpoint Decision Tree:**

```
Tier 2 Parse Rate Measured
│
├─ Parse rate ≥50% (5+ models)?
│  ├─ ≥60% (6+ models) → ✅ EXCEEDS EXPECTATIONS
│  │                     - Document success
│  │                     - Extended analysis: 5 additional candidates
│  │                     - Create roadmap for 80%+ overall parse rate
│  │                     - Proceed to Day 7 (JSON + PATH + Dashboard)
│  │
│  ├─ 50-59% (5 models) → ✅ MEETS EXPECTATIONS
│  │                      - Document success
│  │                      - Proceed to Day 7
│  │                      - Overall: 15/20 = 75% parse rate ✅
│  │
│  ├─ 40-49% (4 models) → ⚠️ PARTIAL SUCCESS
│  │                      - Document as partial success
│  │                      - Proceed to Day 7
│  │                      - Overall: 14/20 = 70% (below 75% target)
│  │                      - Note remaining blockers for Sprint 13
│  │                      - Consider additional blocker work on Day 9
│  │
│  └─ <40% (<4 models) → ❌ BELOW EXPECTATIONS
│                        - Document limitation and analysis
│                        - Identify why blockers were harder than expected
│                        - Defer complex blockers to Sprint 13
│                        - Proceed to Day 7 (don't block JSON/PATH/Dashboard)
│                        - Re-evaluate Tier 2 strategy in retrospective
│                        - Consider revisiting blocker prioritization
```

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 6: Tier 2 Stretch Blockers & Checkpoint" \
                --body "Completes Day 6 of Sprint 12 PLAN.md

   ## Deliverables
   - Tier 2 parse rate measured and documented
   - TIER_2_MODELS.md and TIER_2_IMPLEMENTATION_PLAN.md
   - Extended analysis (if applicable)
   
   ## Day 6 Checkpoint Result
   [Document checkpoint outcome: EXCEEDS/MEETS/PARTIAL/BELOW]
   - Tier 2 parse rate: X/10 (XX%)
   - Overall parse rate: (10+X)/20 (XX%)
   - Extended analysis performed: [Yes/No]
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 589-655)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 589-655)
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 1091-1139) - Day 6 Checkpoint Decision Tree
- `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md`

---

## Day 7 Prompt: JSON Diagnostics & PATH Decision

**Branch:** `sprint12-day7-json-path-dashboard`

**Objective:** Implement JSON diagnostics output, make PATH decision based on email response, and start dashboard infrastructure

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 3 (JSON Diagnostics) and Category 4 (PATH Solver)
- Read `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` - Review Task 5 (JSON Diagnostics Schema) and Task 6 (PATH Licensing Email)
- Review `docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md` - Schema v1.0.0 specification
- Review `docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md` - Email sent on Day 1
- Check email for PATH response (1 week since Day 1)
- Review `docs/planning/EPIC_2/SPRINT_12/PLAN.md` lines 1140-1171 for Day 7 checkpoint decision tree

**Tasks to Complete (8-9 hours):**

1. **Implement JSON diagnostics output** (120-150 min)
   - Update `src/ir/diagnostics.py`
   - Extend DiagnosticReport with to_json() method
   - Use schema from Task 5 (v1.0.0)
   - Add --format flag: `--diagnostics --format json`
   - Default: text (backward compatible)
   - Output to stdout or --output FILE

2. **Create JSON schema documentation** (45 min)
   - Copy Task 5 examples to `docs/schemas/diagnostics_v1.0.0.json`
   - Document in `docs/JSON_DIAGNOSTICS.md`
   - Include CI usage examples (jq queries)
   - Add validation examples

3. **Integrate JSON diagnostics with CI** (45-60 min)
   - Update CI workflow to store JSON as artifacts
   - Example: `--diagnostics --format json --output diagnostics.json`
   - Upload artifacts for historical trending
   - Document in CI_REGRESSION_GUARDRAILS.md

**Decision Point: DAY 7 CHECKPOINT (PATH Licensing)**

Check PATH email response status. Based on response, complete ONE of the following tasks:

**Tasks (if PATH approved for GitHub Actions):**
4A. **Install PATH in CI** (90-120 min) - CONDITIONAL
   - Download PATH solver (free version: 300 vars / 2000 nonzeros)
   - Add to GitHub Actions workflow
   - Create smoke test suite (4 tests from Sprint 11 research)
   - Validate PATH vs IPOPT accuracy (<1% difference)

**Tasks (if PATH denied/no response/self-hosted required):**
4B. **Document PATH decision** (45 min) - CONDITIONAL
   - Create `docs/infrastructure/PATH_SOLVER_DECISION.md`
   - Document email exchange, licensing terms, decision rationale
   - Note IPOPT as primary solver, PATH deferred
   - Recommendation for future (self-hosted runner or commercial license)

5. **Start dashboard infrastructure** (60-90 min)
   - Create `scripts/generate_dashboard.py` skeleton
   - Parse JSON diagnostics from CI artifacts
   - Set up Chart.js integration
   - Initial HTML template

6. **Extended dashboard widgets** (90-120 min)
   - Add parse rate trend visualization
   - Add transformation effectiveness charts
   - Add model-by-model breakdown table
   - Create responsive layout for mobile viewing

**Deliverables:**
- [ ] JSON diagnostics implemented (--format json works)
- [ ] `docs/schemas/diagnostics_v1.0.0.json`
- [ ] `docs/JSON_DIAGNOSTICS.md`
- [ ] CI artifacts storing JSON diagnostics
- [ ] PATH decision made and documented OR PATH implemented in CI
- [ ] Dashboard infrastructure started with basic widgets

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] --diagnostics --format json produces valid JSON matching schema
  - [ ] CI workflow stores JSON artifacts
  - [ ] PATH decision finalized (implemented, documented, or deferred)
  - [ ] Dashboard infrastructure ready for Day 8 completion
  - [ ] All quality checks passing
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 7 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 7 section
  - **CRITICAL:** Document Day 7 checkpoint (PATH decision) with full context
  - Note whether PATH was implemented or deferred
  - Document dashboard progress
  - See `docs/planning/incremental_documentation_guide.md` for checkpoint template
- [ ] **CHECKPOINT:** Document Day 7 PATH decision in `PLAN.md`:
  - [ ] If approved for cloud CI: ✅ Implemented PATH in CI
  - [ ] If self-hosted required: ⚠️ Evaluated feasibility, [implemented/deferred]
  - [ ] If denied: ⚠️ Documented decision, kept IPOPT
  - [ ] If no response: ⚠️ Sent follow-up, documented deferral

**Day 7 Checkpoint Decision Tree:**

```
PATH Email Response Status (1 week since Day 1)
│
├─ Approved for GitHub Actions?
│  ├─ YES, cloud CI allowed → ✅ IMPLEMENT PATH
│  │                          - Install PATH in CI (2-3h Day 7)
│  │                          - 4-test smoke suite
│  │                          - Validate accuracy vs IPOPT
│  │                          - Update docs
│  │
│  ├─ YES, but self-hosted runner required → ⚠️ EVALUATE FEASIBILITY
│  │                                          - Estimate setup cost
│  │                                          - With 80h capacity: If <4h, implement
│  │                                          - If >4h: Defer to Sprint 13
│  │                                          - Document decision
│  │
│  ├─ NO, denied → ⚠️ DOCUMENT DECISION
│  │               - Keep IPOPT as primary solver
│  │               - Document licensing restriction
│  │               - Note <1% accuracy difference acceptable
│  │               - Consider commercial license for future
│  │
│  └─ NO RESPONSE → ⚠️ DEFER TO SPRINT 13
│                    - Send follow-up email
│                    - Proceed with IPOPT
│                    - Document in PATH_SOLVER_DECISION.md
│                    - Re-evaluate in Sprint 13 if response received
```

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 7: JSON Diagnostics & PATH Decision" \
                --body "Completes Day 7 of Sprint 12 PLAN.md

   ## Deliverables
   - JSON diagnostics with schema v1.0.0
   - CI integration for JSON artifacts
   - Dashboard infrastructure started
   
   ## Day 7 Checkpoint (PATH Decision)
   [Document PATH outcome: IMPLEMENTED/DEFERRED/DENIED]
   - Email response: [APPROVED/DENIED/NO RESPONSE]
   - Action taken: [describe]
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 659-742)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 659-742)
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 1140-1171) - Day 7 Checkpoint Decision Tree
- `docs/planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md`
- `docs/planning/EPIC_2/SPRINT_12/PATH_LICENSING_EMAIL.md`
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` (Task 5 and Task 6)

---

## Day 8 Prompt: Dashboard Completion & CI Checklist

**Branch:** `sprint12-day8-dashboard-ci-checklist`

**Objective:** Complete dashboard implementation with visualizations, create CI workflow testing guide, update PR template, add performance trending

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review Category 6 (CI/CD Process) unknowns
- Ensure Day 7 deliverables complete (dashboard infrastructure started)
- Review existing CI workflows in `.github/workflows/`

**Tasks to Complete (7-8 hours):**

1. **Complete dashboard implementation** (120-180 min)
   - Implement Chart.js visualizations:
     - Stage timing chart (bar chart: Parse, Semantic, Simplification, IR, MCP)
     - Simplification effectiveness over time (line chart: Sprints 10-12)
     - Transformation application frequency (pie chart)
     - Model comparison table (heatmap)
   - Fetch diagnostic JSON from CI artifacts API
   - Generate static HTML dashboard
   - Host on GitHub Pages or CI artifacts

2. **Create CI workflow testing guide** (60-75 min)
   - Document: `docs/infrastructure/CI_WORKFLOW_TESTING.md`
   - Sections:
     - Syntax validation (yamllint, actionlint)
     - File path verification (paths exist in repo)
     - Permission checks (secrets, GITHUB_TOKEN)
     - Matrix build testing (all combinations)
     - Common pitfalls (Sprint 11 lessons learned)
   - Include command examples for local testing
   - Add actionlint integration to make targets

3. **Update PR template with checklist** (30-45 min)
   - Edit `.github/pull_request_template.md`
   - Add "CI Workflow Changes" section
   - Checklist items:
     - [ ] Workflow syntax validated locally
     - [ ] File paths verified
     - [ ] Matrix builds tested
     - [ ] Secrets/permissions documented
     - [ ] CI passes on PR before merge
   - Link to CI_WORKFLOW_TESTING.md guide

4. **Performance trending infrastructure** (90-120 min)
   - Create `docs/performance/TRENDS.md`
   - Table format: Sprint | Parse Rate | Convert Rate | Test Time | Simplification
   - Populate with Sprints 8-12 data
   - Create automation script for updates
   - Optional: Chart.js visualizations integrated with dashboard

5. **Polish Sprint 12 documentation** (30-45 min)
   - Review all docs created in Sprint 12
   - Fix formatting, typos, broken links
   - Ensure consistency across documents
   - Update table of contents where needed

**Deliverables:**
- [ ] Dashboard complete and deployed (GitHub Pages or artifacts)
- [ ] `docs/infrastructure/CI_WORKFLOW_TESTING.md`
- [ ] Updated `.github/pull_request_template.md`
- [ ] `docs/performance/TRENDS.md` with historical data
- [ ] All Sprint 12 docs polished and consistent
- [ ] Commit: "Add dashboard, CI checklist, and performance trending"

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Dashboard accessible and functional (shows ≥3 sprints data)
  - [ ] CI testing guide covers all common pitfalls
  - [ ] PR template checklist actionable and concise
  - [ ] Performance trending shows Sprints 8-12
  - [ ] All documentation reviewed and polished
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 8 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 8 section
  - Document dashboard deployment location
  - Note CI checklist additions
  - See `docs/planning/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 8: Dashboard Completion & CI Checklist" \
                --body "Completes Day 8 of Sprint 12 PLAN.md

   ## Deliverables
   - Dashboard complete with Chart.js visualizations
   - CI_WORKFLOW_TESTING.md guide
   - Updated PR template with CI checklist
   - Performance trending (TRENDS.md)
   
   ## Dashboard URL
   [Include dashboard URL if deployed]
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 744-819)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 744-819)
- `.github/workflows/` (existing CI workflows for reference)

---

## Day 9 Prompt: Contingent Features & Recovery

**Branch:** `sprint12-day9-contingent-features`

**Objective:** Based on Day 3 checkpoint outcome, either implement LOW priority transformations (Scenario A) or optional features (Scenario B)

**⚠️ CRITICAL:** Review Day 3 checkpoint outcome in SPRINT_LOG.md to determine which scenario to follow.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - Review all unknowns
- Read `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md` - Check Day 3 checkpoint decision
- Review `docs/planning/EPIC_2/SPRINT_12/PLAN.md` lines 98-127 for Optional Feature Priority Order
- Determine scenario based on Day 3 checkpoint:
  - **Scenario A:** Day 3 checkpoint FAIL (<15% reduction) → Implement LOW priority transformations
  - **Scenario B:** Day 3 checkpoint SUCCESS (≥20% reduction) → Optional features (only if Days 1-8 on schedule)

---

### SCENARIO A: Day 3 Checkpoint FAIL (<15% reduction)

**Tasks to Complete (7-8 hours):**

1. **Implement HIGH-value LOW priority transformations** (5-6h)
   - T5.2: Nested Expression CSE (2h) - highest value for complex models
   - T2.3: Common Denominator (2h) - known improvement for fraction-heavy models
   - T5.4: CSE with Aliasing (2h) - covers remaining CSE gaps
   - Test suite (10+ tests per pattern)

2. **Re-measure simplification effectiveness** (60-90 min)
   - Run measure_simplification.py with new transformations
   - Update baseline_sprint11.json
   - Validate ≥20% target now met
   - Update SIMPLIFICATION_BENCHMARKS.md
   - Document improvement vs baseline

**Deliverables (Scenario A):**
- [ ] 3 LOW priority transformations implemented
- [ ] ≥20% reduction target met with new transformations
- [ ] SIMPLIFICATION_BENCHMARKS.md updated
- [ ] Test suite passing

**Success Criteria (Scenario A):**
- [ ] ≥20% average reduction achieved
- [ ] All transformations tested and validated
- [ ] Ready for Day 10 validation

---

### SCENARIO B: Day 3 Checkpoint SUCCESS (≥20% reduction)

**⚠️ PREREQUISITE CHECK:** Only proceed if Days 1-8 are on schedule. If any previous day overruns occurred, skip optional features and prepare for Day 10.

**Tasks to Complete (7-9 hours):**

Complete tasks in priority order (see deferral priority in PLAN.md lines 98-127):

1. **IF time available:** Dashboard integration expansion (2-3h)
   - Only if Days 7-8 dashboard work complete
   - Add additional dashboard widgets
   - Enhanced visualization features
   - User feedback integration

2. **IF time available:** Performance trending enhancements (2-3h)
   - Only if Day 8 trending work complete
   - Historical trend analysis
   - Performance regression detection
   - Trend visualization improvements

3. **IF time available:** Transformation catalog alignment (2h)
   - Review all transformations in codebase
   - Compare against TRANSFORMATION_CATALOG.md
   - Update catalog with any missing patterns
   - Document transformation interactions

4. **IF time available:** Naming convention alignment (2h)
   - Review Sprint 10/11 code for naming inconsistencies
   - Align with PROJECT_CONVENTIONS.md
   - Update variable/function names where needed
   - No functional changes, code clarity only

**DO NOT IMPLEMENT (defer unless explicitly approved):**
- CSE temporary variable propagation (requires user feedback - DEFER FIRST per priority)
- Extended Tier 2 analysis beyond 60%
- Additional experimental transformations

**Deliverables (Scenario B):**
- [ ] ≥1 optional feature complete (prioritized by value)
- [ ] All code quality checks passing
- [ ] Documentation updated for implemented features

**Success Criteria (Scenario B):**
- [ ] Time used productively on highest-value items
- [ ] No introduction of technical debt
- [ ] Ready for Day 10 validation
- [ ] All work well-documented

---

**Quality Checks (Both Scenarios):**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria (Both Scenarios):**
- [ ] All success criteria met (see scenario-specific criteria above)
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 9 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 9 section
  - Document which scenario was followed (A or B)
  - If Scenario A: Update parse rate table with new reduction percentages
  - If Scenario B: Document which optional features were implemented
  - See `docs/planning/incremental_documentation_guide.md` for templates

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   # For Scenario A:
   gh pr create --title "Sprint 12 Day 9: LOW Priority Transformations (Recovery)" \
                --body "Completes Day 9 of Sprint 12 PLAN.md - Scenario A

   ## Deliverables
   - 3 LOW priority transformations implemented
   - ≥20% reduction target achieved
   - SIMPLIFICATION_BENCHMARKS.md updated
   
   ## Reduction Improvement
   - Original: XX%
   - New: XX%
   - Target met: ✅
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 821-910)" \
                --base main

   # OR for Scenario B:
   gh pr create --title "Sprint 12 Day 9: Optional Features" \
                --body "Completes Day 9 of Sprint 12 PLAN.md - Scenario B

   ## Deliverables
   - [List optional features implemented]
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 821-910)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 821-910)
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 98-127) - Optional Feature Priority Order
- `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md` (Day 3 checkpoint decision)

---

## Day 10 Prompt: Documentation Updates & Final Validation

**Branch:** `sprint12-day10-validation-docs`

**Objective:** Update all required documentation (KNOWN_UNKNOWNS, PREP_PLAN, CHANGELOG), run comprehensive validation, create retrospective, and prepare Sprint 12 completion PR

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md` - All 27 unknowns to verify
- Read `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md` - Task 10 to mark complete
- Review `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md` - All entries to summarize
- Ensure Days 1-9 complete

**Tasks to Complete (8-9 hours):**

1. **Update KNOWN_UNKNOWNS.md verification status** (60-90 min, REQUIRED)
   - Mark all 27 unknowns with verification results
   - Document which unknowns were validated vs. remain open
   - Update resolution status for each category
   - Add Sprint 12 learnings to inform Sprint 13

2. **Update PREP_PLAN.md Task 10 status** (60-90 min, REQUIRED)
   - Mark Task 10 (Sprint 12 Detailed Schedule) as COMPLETE
   - Add result summary: actual vs estimated effort for all 10 days
   - Document checkpoint decisions and outcomes
   - Note any deviations from plan
   - Calculate total prep effort (21-28h estimated vs actual)

3. **Create CHANGELOG.md entries** (60-90 min, REQUIRED)
   - Sprint 12 section with all deliverables
   - Categorize: Features, Improvements, Bug Fixes, Documentation
   - Link to relevant PRs and docs
   - Format following existing CHANGELOG structure
   - Include metrics: parse rate, reduction %, models supported

4. **Run comprehensive validation** (90-120 min, REQUIRED)
   - All 20 models (10 Tier 1 + 10 Tier 2)
   - Validate parse rates:
     - Tier 1: 100% (10/10) - no regressions
     - Tier 2: ≥50% (5/10) - success criterion
     - Overall: ≥75% (15/20)
   - Run full test suite: make test (expect <2 min)
   - Quality checks: make typecheck && make lint && make format
   - CI workflows all green

5. **Sprint 12 Retrospective** (60-90 min, REQUIRED)
   - Create `docs/planning/EPIC_2/SPRINT_12/RETROSPECTIVE.md`
   - Sections:
     - What went well (e.g., prep tasks, measurement approach, 80h utilization)
     - What could improve (e.g., estimation accuracy)
     - Action items for Sprint 13
     - Velocity analysis (planned 75-84h vs actual)
     - Buffer utilization analysis
     - Checkpoint effectiveness review
   - Capacity utilization: 80h available, X used, Y% efficiency
   - Compare final plan (75-84h) vs actual

6. **Update PROJECT_PLAN.md** (30-45 min, REQUIRED)
   - Mark Sprint 12 complete
   - Update Epic 2 progress
   - Note Sprint 12 results and metrics
   - Identify Sprint 13 priorities

7. **Create Sprint 12 PR** (30 min, REQUIRED)
   - Branch: sprint12-complete → main
   - Title: "Sprint 12: Measurement, Polish, and Tier 2 Expansion"
   - Description: Summary of all deliverables
   - Link to RETROSPECTIVE.md
   - Include metrics table
   - Request review

**Deliverables:**
- [ ] KNOWN_UNKNOWNS.md updated with verification results
- [ ] PREP_PLAN.md Task 10 marked complete with results
- [ ] CHANGELOG.md Sprint 12 section complete
- [ ] All 20 models validated (parse rates confirmed)
- [ ] Full test suite passing (make test <2 min)
- [ ] RETROSPECTIVE.md complete
- [ ] PROJECT_PLAN.md updated
- [ ] Sprint 12 PR created
- [ ] All required documentation updated

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All required documentation updates complete
  - [ ] KNOWN_UNKNOWNS.md: 27/27 unknowns addressed
  - [ ] PREP_PLAN.md: Task 10 status/result/summary documented
  - [ ] CHANGELOG.md: Sprint 12 entry complete
  - [ ] All PRIMARY acceptance criteria met (see PLAN.md lines 1172-1227)
  - [ ] Zero critical bugs or regressions
  - [ ] Documentation complete and accurate
  - [ ] Sprint 12 ready for merge and Sprint 13 planning
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
- [ ] Check off Day 10 in `README.md`
- [ ] Log progress to `CHANGELOG.md` (already part of Task 3)
- [ ] **FINAL UPDATE** to `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`:
  - Add PR entry to Day 10 section
  - Complete all metrics tables (final values)
  - Document all checkpoint outcomes (summary)
  - Add retrospective highlights
  - Mark sprint as COMPLETE
  - See `docs/planning/incremental_documentation_guide.md` for final update template

**Pull Request & Review:**
After committing and pushing all changes:

1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 12 Day 10: Documentation Updates & Final Validation" \
                --body "Completes Day 10 of Sprint 12 PLAN.md

   ## Deliverables
   - KNOWN_UNKNOWNS.md verified (27/27)
   - PREP_PLAN.md Task 10 complete
   - CHANGELOG.md Sprint 12 entries
   - RETROSPECTIVE.md complete
   - All validation passing
   
   ## Final Metrics
   - Parse rate: XX/20 (XX%)
   - Term reduction: XX%
   - Test time: <2 min
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/PLAN.md (lines 912-996)" \
                --base main
   ```

2. The PR creation will automatically trigger a Copilot review request

3. Wait for Copilot's review completion. Check review status every minute:
   ```bash
   gh pr view --json reviews -q '.reviews[] | select(.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "COMMENTED")'
   ```
   
   Continue checking every minute until you find a complete review or 20 minutes have elapsed.

4. Address all review comments:
   - Read each comment carefully
   - Make necessary code fixes
   - Run quality checks again after fixes
   - Commit and push fixes
   - Reply to comments indicating what was fixed

5. Once approved, merge the PR:
   ```bash
   gh pr merge --squash
   ```

**After Day 10 PR is merged:**

6. **Create Sprint 12 Completion PR** (30 min)
   - Create branch `sprint12-complete` from `main`
   - Ensure all Days 1-10 are merged
   - Create final PR to mark sprint complete:
   ```bash
   gh pr create --title "Sprint 12 Complete: Measurement, Polish, and Tier 2 Expansion" \
                --body "Marks Sprint 12 as complete

   ## Sprint 12 Summary
   - Duration: 10 days
   - Actual effort: [X hours]
   - Capacity utilization: [X%]
   
   ## Key Achievements
   - Term reduction measured: [XX%] average
   - Tier 2 parse rate: [X/10] ([XX%])
   - Overall parse rate: [XX/20] ([XX%])
   - Multi-metric CI implemented
   - JSON diagnostics complete
   - [Additional achievements]
   
   ## Checkpoints
   - Day 3: [SUCCESS/PARTIAL/FAIL] - [XX%] reduction
   - Day 6: [EXCEEDS/MEETS/PARTIAL/BELOW] - [X/10] Tier 2 models
   - Day 7: PATH [IMPLEMENTED/DEFERRED/DENIED]
   
   ## Reference
   - docs/planning/EPIC_2/SPRINT_12/RETROSPECTIVE.md
   - docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md" \
                --base main
   ```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 912-996)
- `docs/planning/EPIC_2/SPRINT_12/PLAN.md` (lines 1172-1227) - SUCCESS CRITERIA (PRIMARY)
- `docs/planning/EPIC_2/SPRINT_12/KNOWN_UNKNOWNS.md`
- `docs/planning/EPIC_2/SPRINT_12/PREP_PLAN.md`
- `docs/planning/EPIC_2/SPRINT_12/SPRINT_LOG.md`
- `docs/planning/incremental_documentation_guide.md`

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents listed
   - Create the specified branch from main:
     ```bash
     git checkout main
     git pull
     git checkout -b [branch-name]
     ```
   - Understand all tasks and time estimates
   - Check for any checkpoint decisions from previous days

2. **During the day:**
   - Complete tasks in the order listed
   - Run quality checks after each significant code change
   - Track progress against time estimates
   - Document decisions in SPRINT_LOG.md as you go (don't wait until end of day)
   - For checkpoint days (3, 6, 7): Evaluate criteria carefully and document decision immediately

3. **End of day:**
   - Verify all deliverables are complete
   - Run final quality checks (typecheck, lint, format, test)
   - Check off all completion criteria
   - Update PLAN.md (mark day complete)
   - Update README.md (check off day)
   - Update CHANGELOG.md (log changes)
   - Update SPRINT_LOG.md (add PR entry, update metrics, document decisions)
   - Commit all changes and push to branch
   - Create PR with gh CLI
   - Wait for and address Copilot review
   - Merge once approved

4. **For checkpoint days (3, 6, 7):**
   - Evaluate checkpoint criteria carefully based on actual results
   - Document decision with clear rationale in SPRINT_LOG.md
   - Update PLAN.md with checkpoint outcome
   - Follow decision tree in PLAN.md for next steps
   - For Day 3: Decision affects Day 9 scenario selection
   - For Day 6: Decision may trigger extended analysis
   - For Day 7: Decision determines PATH implementation path

5. **For time-boxed days (4, 5):**
   - Set a timer for maximum hours (8h)
   - Stop work at time limit regardless of completion status
   - Document what was accomplished vs. planned
   - Note any deferred work for next day or sprint

6. **Quality check reminders:**
   - ALWAYS run before committing code changes
   - Can skip for documentation-only commits
   - Fix all issues before creating PR
   - Re-run after addressing review comments

7. **SPRINT_LOG.md updates:**
   - Update incrementally throughout each day
   - Don't wait until end of sprint
   - Document decisions when made (capture context while fresh)
   - Update parse rate table whenever rates change
   - See `docs/planning/incremental_documentation_guide.md` for detailed templates

---

## Notes

- **Self-contained prompts:** Each day's prompt includes all necessary context and prerequisites
- **Quality checks:** Always run before committing code (skip for docs-only commits)
- **Time estimates:** Use as guidelines; actual time may vary. Note variances in SPRINT_LOG.md
- **Checkpoint decisions:** Critical for sprint success. Document thoroughly with rationale.
- **SPRINT_LOG.md:** Update incrementally throughout sprint, not just at end. This captures context and decisions while fresh.
- **Review process:** Copilot reviews are automatic on PR creation. Wait for completion before merging.
- **Line numbers:** Reference specific PLAN.md sections for detailed task descriptions
- **Branch naming:** Follow suggested names for consistency across sprint
- **Time-boxing:** Days 4-5 have strict 8h limits. Respect these to prevent downstream delays.
- **Scenario-based work:** Day 9 work depends on Day 3 checkpoint. Check SPRINT_LOG.md for decision.
- **Day 10 is comprehensive:** Allow full 8-9h for documentation, validation, and retrospective
- **Sprint completion:** After Day 10 PR merges, create final sprint completion PR for visibility

---

## Sprint 12 Quick Reference

**Days and Focus:**
- Day 1: Measurement infrastructure + extended testing (7-8h)
- Day 2: Baseline collection + multi-metric backend (8-9h)
- Day 3: Validation + analysis + **CHECKPOINT** (7-8h) - Determines Day 9 scenario
- Day 4: Tier 2 analysis + high blockers (8h max, TIME-BOXED)
- Day 5: Tier 2 medium blockers (8h max, TIME-BOXED)
- Day 6: Tier 2 stretch + **CHECKPOINT** (7-8h) - May trigger extended analysis
- Day 7: JSON diagnostics + PATH **CHECKPOINT** + dashboard start (8-9h)
- Day 8: Dashboard completion + CI checklist + trending (7-8h)
- Day 9: **CONTINGENT** - Scenario A (recovery) or B (optional features) (7-9h)
- Day 10: Documentation + validation + retrospective (8-9h)

**Critical Checkpoints:**
- **Day 3:** Term reduction ≥20%? → Affects Day 9 work
- **Day 6:** Tier 2 ≥50%? → May trigger extended analysis
- **Day 7:** PATH approved? → Affects implementation path

**Key Metrics to Track:**
- Term reduction percentage (target: ≥20%)
- Tier 2 parse rate (target: ≥50%, 5/10 models)
- Overall parse rate (target: ≥75%, 15/20 models)
- Test execution time (target: <2 min)

**Success Criteria (PRIMARY):**
1. Term reduction validated (≥20% on ≥5 models)
2. Multi-metric CI complete (3 metrics with thresholds)
3. Tier 2 parse rate ≥50% (overall ≥75%)
4. JSON diagnostics functional
5. PATH decision documented
6. CI process improvements (checklist, guide)
7. Documentation updates complete

**Total Capacity:** 80 hours (10 days × 8h/day)
**Allocated Effort:** 75-84 hours
**Buffer:** -4 to +5 hours (94-105% utilization)
