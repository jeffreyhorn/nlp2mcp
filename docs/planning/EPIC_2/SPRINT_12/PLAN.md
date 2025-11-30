# Sprint 12 Plan: Measurement, Polish, and Tier 2 Expansion

**Sprint:** Sprint 12 (Weeks 13-14)  
**Epic:** Epic 2 - Multi-Solver MCP Server  
**Start Date:** TBD (after prep completion)  
**Duration:** 10 working days  
**Total Effort:** 22-27 hours  
**Theme:** Validate Sprint 11 achievements, complete technical debt, expand to Tier 2

---

## Executive Summary

Sprint 12 validates Sprint 11's aggressive simplification through quantitative measurement, completes half-implemented multi-metric thresholds, and expands parser coverage to Tier 2 GAMSLib models. This sprint emphasizes measurement over new features, ensuring Sprint 11's 11 transformation functions deliver the promised ≥20% term reduction.

**Sprint 11 Context:**
- ✅ 100% Tier 1 parse rate (10/10 models)
- ✅ 11 transformation functions implemented
- ✅ 3 CSE variants (extract, hoist, propagate)
- ✅ Text diagnostics with <2% overhead
- ⚠️ Technical debt: Multi-metric thresholds CLI accepted but not implemented
- ⚠️ Unknown: Actual term reduction percentage (estimated 20-40%, unvalidated)

**Sprint 12 Goals:**
1. **Measurement:** Validate ≥20% term reduction on ≥50% Tier 1 models
2. **Technical Debt:** Complete multi-metric threshold backend logic
3. **Expansion:** Achieve ≥50% parse rate on 10 Tier 2 models (≥75% overall: 15/20)
4. **Polish:** JSON diagnostics, PATH decision, CI process improvements

---

## Scope & Effort Allocation

### Total Hours: 22-27h

| Phase | Days | Components | Effort |
|-------|------|------------|--------|
| **Measurement & Validation** | 1-3 | Benchmarking, Multi-Metric | 7-10h |
| **Tier 2 Expansion** | 4-6 | Model Selection, Blocker Implementation | 6-8h |
| **Polish & Integration** | 7-8 | JSON, PATH, CI Checklist | 6-7h |
| **Buffer & Validation** | 9-10 | Contingency, Final Testing | 3-4h |

### Scope by Priority

**HIGH Priority (Must Do - 10-14h):**
1. Term Reduction Benchmarking (4-6h)
2. Multi-Metric Threshold Implementation (3-4h)
3. Tier 2 Expansion - Core Blockers (3-4h)

**MEDIUM Priority (Should Do - 9-10h):**
4. JSON Diagnostics Output (2h)
5. Tier 2 Expansion - Medium Blockers (3-4h)
6. PATH Solver CI Integration (2-3h, conditional)
7. CI Workflow Testing Checklist (1h)

**LOW Priority (Deferred Unless Day 3 Checkpoint Triggered - 18-28h):**
8. Additional transformations if <20% reduction
9. Dashboard integration
10. CSE temp propagation
11. Other deferred items

---

## Prep Task Synthesis

All 10 Sprint 12 preparation tasks completed successfully (21-28h estimated, actual time tracked in PREP_PLAN.md):

### Task 1: Known Unknowns (27 unknowns identified)
- **Status:** ✅ COMPLETE
- **Key Findings:** 27 unknowns across 7 categories, all assigned to verification tasks
- **Impact:** Comprehensive risk catalog enables proactive mitigation

### Task 2: Term Reduction Measurement Research
- **Status:** ✅ COMPLETE
- **Key Decisions:**
  - Metrics: Operation count (_expression_size) + Term count (count_terms)
  - Baseline: Empty SimplificationPipeline for "before", full pipeline for "after"
  - Storage: JSON format with per-model and aggregate metrics
  - Overhead: <0.1% theoretical (fast AST traversal)
- **Impact:** Clear methodology ready for Days 1-2 implementation

### Task 3: Tier 2 Model Selection (10 models selected)
- **Status:** ✅ COMPLETE
- **Key Findings:**
  - Baseline parse rate: 5.6% (1/18 candidates)
  - 6 blocker patterns identified
  - Estimated effort: 15h total (4h high, 6h medium, 5h stretch)
- **Selected Models:** chenery, jbearing, fct, chem, water, gastrans, process, least, like, bearing
- **Impact:** Diverse model set maximizes parser coverage gains

### Task 4: Multi-Metric Threshold Research
- **Status:** ✅ COMPLETE
- **Key Decisions:**
  - Exit code strategy: Check all metrics, exit worst status (Option B)
  - Architecture: Extend check_parse_rate_regression.py (no new script)
  - Thresholds: parse_rate (5%/10%), convert_rate (5%/10%), performance (20%/50%)
  - PR format: Table with ✅/⚠️/❌ indicators
- **Impact:** Industry-validated patterns reduce CI flakiness risk

### Task 5: JSON Diagnostics Schema
- **Status:** ✅ COMPLETE
- **Key Decisions:**
  - Schema v1.0.0 with SemVer versioning
  - Format: Single JSON object per model
  - Backward compatibility: --format flag (text default)
  - Complexity: Direct serialization, no refactoring needed
- **Impact:** 3 example files validate schema for Day 7-8 implementation

### Task 6: PATH Licensing Email
- **Status:** ✅ COMPLETE
- **Deliverable:** Professional email template ready to send Day 1
- **Decision tree:** 4 scenarios (approve/deny/no response/self-hosted)
- **Impact:** Async research front-loaded to maximize response window

### Task 7: Simplification Metrics Prototype
- **Status:** ✅ COMPLETE
- **Key Findings:**
  - Accuracy: 0% error (exceeds <5% target)
  - Performance: 7.53% overhead (exceeds <1% but acceptable for benchmarking mode)
  - Feasibility: count_terms() proven on 3 models
- **Impact:** Validates measurement approach before full implementation

### Task 8: Tier 2 Blocker Analysis Template
- **Status:** ✅ COMPLETE
- **Key Findings:**
  - Priority formula: Frequency + (5 - Complexity)
  - Budget algorithm: Cumulative sum stops at 6h
  - 3 example analyses: special_chars, alias, inline_descriptions
- **Impact:** Systematic prioritization framework for Days 4-6

### Task 9: Baseline Storage Infrastructure
- **Status:** ✅ COMPLETE - MERGED (PR #343)
- **Deliverables:**
  - baselines/simplification/ with README and placeholder
  - baselines/multi_metric/ with README and placeholder
  - scripts/update_baselines.sh executable script
  - docs/infrastructure/BASELINES.md
- **Impact:** Infrastructure ready, no Day 1 setup blockers

### Task 10: Sprint 12 Detailed Schedule
- **Status:** 🔵 IN PROGRESS (this document)

### Unknowns Status

**Verified:** 25/27 unknowns (93%)

**Remaining (to verify in Task 10):**
- 7.1: Sprint 12 Scope Management
- 7.2: Dependency on External Research

**Resolution Rate:**
- Category 1 (Term Reduction): 7/7 verified ✅
- Category 2 (Multi-Metric): 4/4 verified ✅
- Category 3 (JSON): 3/3 verified ✅
- Category 4 (PATH): 4/4 verified ✅
- Category 5 (Tier 2): 4/4 verified ✅
- Category 6 (CI): 3/3 verified ✅
- Category 7 (Process): 0/2 verified (this task)

---

## Day-by-Day Schedule

### Day 1: Measurement Infrastructure Setup (2-3h)

**Focus:** Component 1 (Term Reduction Benchmarking - Part 1)

**Tasks:**
1. Send PATH licensing email to ferris@cs.wisc.edu (15 min)
   - Use template from Task 6
   - Track response for Day 7 checkpoint
2. Implement SimplificationMetrics class (60-75 min)
   - Location: `src/ir/metrics.py` (new file)
   - Based on Task 7 prototype EnhancedSimplificationMetrics
   - Fields: model, ops_before, ops_after, terms_before, terms_after, execution_time_ms, transformations_applied
   - Methods: to_dict(), calculate_reductions()
3. Implement count_terms() function (30-45 min)
   - Location: `src/ir/metrics.py`
   - Use Task 7 prototype implementation (validated 0% error)
   - Add docstring with examples
   - Unit tests: test_count_terms.py with 10+ test cases
4. Instrument simplification pipeline (45-60 min)
   - Update `src/ir/simplification_pipeline.py`
   - Add optional metrics collection to apply() method
   - Collect before/after metrics when enabled
   - No changes to transformation functions (instrumentation only)

**Deliverables:**
- [ ] PATH email sent (tracked in email client)
- [ ] src/ir/metrics.py with SimplificationMetrics and count_terms()
- [ ] tests/unit/test_metrics.py with ≥10 test cases
- [ ] Instrumented SimplificationPipeline (backward compatible)
- [ ] All existing tests still passing (make test-fast)

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Instrumentation breaks existing tests
  - Mitigation: Make metrics collection opt-in (default: disabled)
- Risk: count_terms() edge cases not covered
  - Mitigation: Use Task 7 validated implementation verbatim

**Success Criteria:**
- [ ] SimplificationMetrics class passes all tests
- [ ] count_terms() validated on 10+ expressions (including Task 7 examples)
- [ ] Pipeline instrumentation works on rbrock.gms without errors
- [ ] make test-fast completes in <30s
- [ ] PATH email sent and delivery confirmed

**Time Budget:** 2-3 hours

---

### Day 2: Baseline Collection & Multi-Metric Backend (3-4h)

**Focus:** Component 1 (Part 2) + Component 2 (Part 1)

**Tasks:**
1. Create measure_simplification.py script (90-120 min)
   - Location: `scripts/measure_simplification.py`
   - CLI: `--model MODEL` or `--model-set tier1` 
   - Functionality:
     - Load model and parse to AST
     - Run simplification with metrics collection
     - Aggregate results across all models
     - Output JSON matching baselines/simplification/README.md schema
   - Output: JSON to stdout or `--output FILE`
   - Example: `./scripts/measure_simplification.py --model-set tier1 --output baselines/simplification/baseline_sprint11.json`

2. Populate baseline_sprint11.json (30-45 min)
   - Run measure_simplification.py on all 10 Tier 1 models
   - Validate JSON against schema (jq validation)
   - Update metadata: commit SHA, timestamp, sprint "sprint11"
   - Commit baseline to git

3. Implement multi-metric threshold backend (60-90 min)
   - Update `scripts/check_parse_rate_regression.py`
   - Add read_baseline() to parse multi-metric JSON
   - Implement check_all_metrics() function:
     - Parse rate: compare current vs baseline
     - Convert rate: compare current vs baseline
     - Performance: compare avg time vs baseline
   - Exit code logic: 0 (pass), 1 (warn), 2 (fail)
   - Return worst status across all 3 metrics

**Deliverables:**
- [ ] scripts/measure_simplification.py (executable, --help works)
- [ ] baselines/simplification/baseline_sprint11.json (valid JSON, ≥10 models)
- [ ] Updated check_parse_rate_regression.py with multi-metric support
- [ ] Unit tests for multi-metric threshold logic

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Baseline collection reveals <20% reduction
  - Mitigation: Defer decision to Day 3 checkpoint (don't block Day 2)
- Risk: Convert rate baseline missing data
  - Mitigation: Use measure_parse_rate.py with --all-metrics flag

**Success Criteria:**
- [ ] measure_simplification.py runs on all 10 Tier 1 models without errors
- [ ] baseline_sprint11.json matches schema exactly
- [ ] Multi-metric backend passes unit tests (warn/fail thresholds trigger correctly)
- [ ] Baseline committed to git with proper metadata

**Time Budget:** 3-4 hours

---

### Day 3: Validation & Checkpoint (1-2h)

**Focus:** Component 1 (Part 3) + Component 2 (Part 2) + Checkpoint

**Tasks:**
1. Analyze baseline_sprint11.json results (30-45 min)
   - Calculate aggregate metrics:
     - Average term reduction percentage across 10 models
     - Average operation reduction percentage
     - Models meeting ≥20% threshold
   - Identify top 3 most effective transformations
   - Create analysis summary in `docs/SIMPLIFICATION_BENCHMARKS.md`

2. Extend measure_parse_rate.py for unified metrics (30-45 min)
   - Add `--all-metrics` flag
   - Track parse_rate, convert_rate, performance in single JSON
   - Output format matching baselines/multi_metric/README.md schema
   - Populate baselines/multi_metric/baseline_sprint12.json placeholder

3. Update CI workflow for multi-metric (15-30 min)
   - Edit `.github/workflows/gamslib-regression.yml`
   - Replace single parse-rate check with multi-metric check
   - Add all 6 threshold arguments (warn/fail for each metric)
   - Update PR comment template to show all 3 metrics

**Deliverables:**
- [ ] docs/SIMPLIFICATION_BENCHMARKS.md with analysis
- [ ] Updated measure_parse_rate.py with --all-metrics
- [ ] baselines/multi_metric/baseline_sprint12.json populated
- [ ] Updated .github/workflows/gamslib-regression.yml
- [ ] Commit: "Complete Components 1 & 2: Benchmarking and Multi-Metric"

**Decision Point: DAY 3 CHECKPOINT**

**Checkpoint Criteria:**
- **Trigger:** baseline_sprint11.json analysis complete
- **Metric:** Average term reduction percentage across 10 Tier 1 models
- **Success:** ≥20% average reduction on ≥5 models (50% threshold)
- **Decisions:**
  - **If ≥20% average:** ✅ SUCCESS - Proceed to Tier 2 (Day 4)
  - **If 15-19% average:** ⚠️ PARTIAL - Document limitation, proceed to Tier 2
  - **If <15% average:** ❌ FAIL - Add LOW priority transformations (defer Tier 2 to Days 7-8)

**Risks & Mitigation:**
- Risk: Results show <20% reduction
  - Mitigation: LOW priority transformations ready (Item #8 from DEFERRED_TO_SPRINT_12.md)
  - Effort: 6-8h to add trig identities, exp/log identities
  - Fallback: Document actual reduction, adjust future expectations

**Success Criteria:**
- [ ] Checkpoint decision made based on actual data
- [ ] All 3 metrics (parse, convert, performance) tracked in CI
- [ ] PR comment format validated (table with ✅/⚠️/❌)
- [ ] Components 1 & 2 complete and functional

**Time Budget:** 1-2 hours

---

### Day 4: Tier 2 Model Analysis (2h)

**Focus:** Component 5 (Tier 2 Expansion - Part 1)

**Tasks:**
1. Download 10 Tier 2 candidate models (15 min)
   - Use `scripts/download_tier2_candidates.sh` from Task 3
   - Models: chenery, jbearing, fct, chem, water, gastrans, process, least, like, bearing
   - Location: `tests/fixtures/gamslib/tier2/`

2. Run parse failure analysis (45-60 min)
   - Use `scripts/analyze_tier2_candidates.py` from Task 3
   - Classify failures by blocker pattern
   - Generate `tests/fixtures/tier2_candidates/analysis_results.json`
   - Validate against Task 3 predictions

3. Prioritize blockers using Task 8 template (45-60 min)
   - Apply classification schema (Frequency, Complexity, Category, Criticality)
   - Calculate priority scores for each blocker
   - Create `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md`
   - Fill template for all discovered blockers
   - Sort by priority, select top blockers fitting 6h budget

4. Create implementation plan (15 min)
   - High-priority (Days 4-5): 3-4h blockers
   - Medium-priority (Day 6): 2-3h blockers if time permits
   - Document plan in TIER_2_BLOCKER_ANALYSIS.md

**Deliverables:**
- [ ] 10 Tier 2 models downloaded
- [ ] Parse failure analysis complete (JSON results)
- [ ] TIER_2_BLOCKER_ANALYSIS.md with prioritized blockers
- [ ] Implementation plan for Days 5-6 (3-6h scope)

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Blockers differ from Task 3 predictions
  - Mitigation: Template flexible, re-prioritize based on actual failures
- Risk: All blockers >6h complexity
  - Mitigation: Select easier models from alternate candidates, document limitation

**Success Criteria:**
- [ ] Blocker analysis matches template format
- [ ] Priority scores calculated for all blockers
- [ ] Implementation plan fits 6h total budget (Days 5-6)
- [ ] Top 3 blockers identified for Day 5 implementation

**Time Budget:** 2 hours

---

### Day 5: Tier 2 High-Priority Blocker Implementation (3-4h)

**Focus:** Component 5 (Part 2) - Implement top-priority blockers

**Tasks:**
1. Implement Blocker #1 (1-1.5h)
   - Based on Day 4 priority analysis
   - Likely: special_chars_in_identifiers (1.5h) OR predefined_constants (1h)
   - Update lexer/grammar
   - Add AST nodes if needed
   - Unit tests (5-10 test cases)
   - Integration test (affected model parses)

2. Implement Blocker #2 (1-1.5h)
   - Based on Day 4 priority analysis
   - Likely: multiple_alias_declaration (1.5h)
   - Grammar extension
   - Symbol table updates
   - Unit tests
   - Integration test

3. Implement Blocker #3 (1-1.5h)
   - Based on Day 4 priority analysis
   - Likely: Start inline_descriptions (4h total, partial on Day 5)
   - Grammar changes for optional description strings
   - AST node updates
   - Unit tests for basic cases

**Deliverables:**
- [ ] 2-3 blockers fully implemented
- [ ] Unit tests passing for all implemented blockers
- [ ] 2-3 Tier 2 models now parsing (integration tests)
- [ ] Code committed: "Tier 2: Implement high-priority blockers (Day 5)"

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Blocker more complex than estimated
  - Mitigation: Stop at 1.5h, defer to Day 6 or Sprint 13
- Risk: Fix breaks Tier 1 models
  - Mitigation: Run full Tier 1 regression after each blocker

**Success Criteria:**
- [ ] ≥2 blockers fully implemented and tested
- [ ] ≥2 Tier 2 models parsing (cumulative)
- [ ] All Tier 1 tests still passing (no regressions)
- [ ] Code quality: typecheck ✅, lint ✅, format ✅

**Time Budget:** 3-4 hours

---

### Day 6: Tier 2 Medium-Priority Blockers & Checkpoint (2-3h)

**Focus:** Component 5 (Part 3) + Checkpoint

**Tasks:**
1. Complete any Day 5 partial work (30-60 min)
   - Finish inline_descriptions if started Day 5
   - Polish and test

2. Implement additional blockers if time permits (60-90 min)
   - Target: Reach ≥50% Tier 2 parse rate (5/10 models)
   - Based on Day 4 priority list
   - Possible: model_inline_descriptions (2h) or partial table_wildcard_domain

3. Measure Tier 2 parse rate (15 min)
   - Run ingest_gamslib.py on all 10 Tier 2 models
   - Calculate parse rate: (models parsed / 10) × 100%
   - Update baselines/multi_metric/baseline_sprint12.json with Tier 2 results

4. Create Tier 2 documentation (15-30 min)
   - `docs/TIER_2_MODELS.md`: List of 10 models with status
   - `docs/TIER_2_IMPLEMENTATION_PLAN.md`: Blockers implemented, remaining work
   - Document expected vs actual results

**Deliverables:**
- [ ] Tier 2 parse rate measured
- [ ] docs/TIER_2_MODELS.md
- [ ] docs/TIER_2_IMPLEMENTATION_PLAN.md
- [ ] Commit: "Complete Tier 2 expansion (≥50% parse rate)"

**Decision Point: DAY 6 CHECKPOINT**

**Checkpoint Criteria:**
- **Trigger:** Tier 2 parse rate measured
- **Metric:** Percentage of 10 Tier 2 models successfully parsing
- **Success:** ≥50% (5/10 models) = ≥75% overall (15/20 total)
- **Decisions:**
  - **If ≥60% (6+ models):** ✅ EXCEEDS - Document success, proceed to Day 7
  - **If 50-59% (5 models):** ✅ MEETS - Document success, proceed to Day 7
  - **If 40-49% (4 models):** ⚠️ PARTIAL - Document as partial success, proceed to Day 7
  - **If <40% (<4 models):** ❌ BELOW - Defer complex blockers to Sprint 13, document limitation

**Risks & Mitigation:**
- Risk: Parse rate <50%
  - Mitigation: Acceptable if 40-49% (still unlocks 4 new models)
  - Fallback: Document remaining blockers for Sprint 13

**Success Criteria:**
- [ ] Tier 2 parse rate ≥50% (5/10 models)
- [ ] Overall parse rate ≥75% (15/20 models: 10 Tier 1 + 5 Tier 2)
- [ ] All blockers documented with effort estimates
- [ ] Remaining work identified for Sprint 13

**Time Budget:** 2-3 hours

---

### Day 7: JSON Diagnostics & PATH Decision (3-4h)

**Focus:** Component 3 (JSON Diagnostics) + Component 4 (PATH Decision)

**Tasks:**
1. Implement JSON diagnostics output (90-120 min)
   - Update `src/ir/diagnostics.py`
   - Extend DiagnosticReport with to_json() method
   - Use schema from Task 5 (v1.0.0)
   - Add --format flag: `--diagnostics --format json`
   - Default: text (backward compatible)
   - Output to stdout or --output FILE

2. Create JSON schema documentation (30 min)
   - Copy Task 5 examples to `docs/schemas/diagnostics_v1.0.0.json`
   - Document in `docs/JSON_DIAGNOSTICS.md`
   - Include CI usage examples (jq queries)

3. Integrate JSON diagnostics with CI (30 min)
   - Update CI workflow to store JSON as artifacts
   - Example: `--diagnostics --format json --output diagnostics.json`
   - Upload artifacts for historical trending
   - Document in CI_REGRESSION_GUARDRAILS.md

**Decision Point: DAY 7 CHECKPOINT (PATH Licensing)**

**Checkpoint Criteria:**
- **Trigger:** 1 week since PATH email sent (Day 1)
- **Metric:** Email response status
- **Decisions:**
  - **Approved for GitHub Actions:** ✅ Implement PATH (2-3h on Day 7-8)
  - **Denied or restricted:** ⚠️ Document decision, keep IPOPT (<1% accuracy difference acceptable)
  - **No response:** ⚠️ Defer to Sprint 13, send follow-up, proceed with IPOPT
  - **Self-hosted runner required:** ⚠️ Evaluate feasibility, likely defer to Sprint 13

**Tasks (if PATH approved):**
4. Install PATH in CI (60-90 min) - CONDITIONAL
   - Download PATH solver (free version: 300 vars / 2000 nonzeros)
   - Add to GitHub Actions workflow
   - Create smoke test suite (4 tests from Sprint 11 research)
   - Validate PATH vs IPOPT accuracy (<1% difference)

**Tasks (if PATH denied/no response):**
4. Document PATH decision (30 min) - CONDITIONAL
   - Create `docs/infrastructure/PATH_SOLVER_DECISION.md`
   - Document email exchange, licensing terms, decision rationale
   - Note IPOPT as primary solver, PATH deferred
   - Recommendation for future (self-hosted runner or commercial license)

**Deliverables:**
- [ ] JSON diagnostics implemented (--format json works)
- [ ] docs/schemas/diagnostics_v1.0.0.json
- [ ] docs/JSON_DIAGNOSTICS.md
- [ ] CI artifacts storing JSON diagnostics
- [ ] PATH decision made and documented OR PATH implemented in CI

**Risks & Mitigation:**
- Risk: JSON schema evolves during implementation
  - Mitigation: Stick to Task 5 schema v1.0.0, defer changes to v1.1.0
- Risk: No PATH response
  - Mitigation: Proceed with IPOPT, document decision

**Success Criteria:**
- [ ] --diagnostics --format json produces valid JSON matching schema
- [ ] CI workflow stores JSON artifacts
- [ ] PATH decision finalized (implemented, documented, or deferred)
- [ ] All quality checks passing

**Time Budget:** 3-4 hours

---

### Day 8: CI Checklist & Documentation Polish (1-2h)

**Focus:** Component 6 (CI Workflow Testing Checklist) + Documentation

**Tasks:**
1. Create CI workflow testing guide (45-60 min)
   - Document: `docs/infrastructure/CI_WORKFLOW_TESTING.md`
   - Sections:
     - Syntax validation (yamllint, actionlint)
     - File path verification (paths exist in repo)
     - Permission checks (secrets, GITHUB_TOKEN)
     - Matrix build testing (all combinations)
     - Common pitfalls (Sprint 11 lessons learned)
   - Include command examples for local testing

2. Update PR template with checklist (15-30 min)
   - Edit `.github/pull_request_template.md`
   - Add "CI Workflow Changes" section
   - Checklist items:
     - [ ] Workflow syntax validated locally
     - [ ] File paths verified
     - [ ] Matrix builds tested
     - [ ] Secrets/permissions documented
     - [ ] CI passes on PR before merge
   - Link to CI_WORKFLOW_TESTING.md guide

3. Polish Sprint 12 documentation (15-30 min)
   - Review all docs created in Sprint 12
   - Fix formatting, typos, broken links
   - Ensure consistency across documents
   - Update table of contents where needed

**Deliverables:**
- [ ] docs/infrastructure/CI_WORKFLOW_TESTING.md
- [ ] Updated .github/pull_request_template.md
- [ ] All Sprint 12 docs polished and consistent
- [ ] Commit: "Add CI workflow testing checklist and documentation"

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Checklist too prescriptive, slows PRs
  - Mitigation: Keep checklist short (5-7 items), focus on common issues

**Success Criteria:**
- [ ] CI testing guide covers all common pitfalls
- [ ] PR template checklist actionable and concise
- [ ] All Sprint 12 documentation reviewed and polished
- [ ] Goal: Zero CI-fix follow-up PRs in Sprint 13

**Time Budget:** 1-2 hours

---

### Day 9: Buffer & Optional Items (2-3h)

**Focus:** Contingency buffer + Quick-win LOW priority items

**Scenario A: No Checkpoint Failures (2-3h available)**

**Optional Tasks (pick based on interest/value):**
1. Dashboard Integration (2-3h) - Requires Component 3 complete
   - Create `scripts/generate_dashboard.py`
   - Parse JSON diagnostics from CI artifacts
   - Generate HTML dashboard with charts (parse rate trend, conversion status)
   - Host on GitHub Pages or CI artifacts

2. Naming Convention Alignment (1h)
   - Review `src/ir/` and `src/ad/` for inconsistent naming
   - Align with PROJECT_PLAN.md conventions
   - Update docs with naming standards

3. Performance Trending (2-3h)
   - Extend baseline storage with historical performance data
   - Create time-series charts (parse time, simplification time over sprints)
   - Integrate with dashboard if implemented

**Scenario B: Checkpoint Failures (2-3h needed for recovery)**

**Recovery Tasks:**
- If Day 3 <20% reduction: Add LOW priority transformations (6-8h - partial implementation)
- If Day 6 <50% Tier 2: Debug complex blockers, extend to Day 9
- If Day 7 PATH issues: Self-hosted runner research and setup

**Deliverables:**
- [ ] At least 1 optional item completed (if no failures)
- [ ] OR checkpoint recovery complete (if failures occurred)

**Decision Points:**
- Choose optional items based on sprint progress and remaining time

**Success Criteria:**
- [ ] Buffer time used productively (not idle)
- [ ] No critical blockers remaining for Day 10

**Time Budget:** 2-3 hours

---

### Day 10: Final Validation & Retrospective (1-2h)

**Focus:** Sprint closure, validation, retrospective

**Tasks:**
1. Run comprehensive validation (30-45 min)
   - All 20 models (10 Tier 1 + 10 Tier 2)
   - Validate parse rates:
     - Tier 1: 100% (10/10) - no regressions
     - Tier 2: ≥50% (5/10) - success criterion
     - Overall: ≥75% (15/20)
   - Run full test suite: make test
   - Quality checks: make typecheck && make lint && make format
   - CI workflows all green

2. Update Sprint 12 documentation (15-30 min)
   - Mark all completed components in PLAN.md
   - Update PROJECT_PLAN.md with Sprint 12 results
   - Document actual vs estimated effort
   - Note deferred items for Sprint 13

3. Sprint 12 Retrospective (30-45 min)
   - Create `docs/planning/EPIC_2/SPRINT_12/RETROSPECTIVE.md`
   - Sections:
     - What went well (e.g., prep tasks, measurement approach)
     - What could improve (e.g., estimation accuracy)
     - Action items for Sprint 13
     - Velocity analysis (planned 22-27h vs actual)
   - Buffer utilization analysis

4. Create Sprint 12 PR (15 min)
   - Branch: sprint12-complete → main
   - Title: "Sprint 12: Measurement, Polish, and Tier 2 Expansion"
   - Description: Summary of all deliverables
   - Link to RETROSPECTIVE.md
   - Request review

**Deliverables:**
- [ ] All 20 models validated (parse rates confirmed)
- [ ] Full test suite passing (make test <2 min)
- [ ] RETROSPECTIVE.md complete
- [ ] Sprint 12 PR created
- [ ] All documentation updated

**Decision Points:** None

**Success Criteria:**
- [ ] All PRIMARY acceptance criteria met (see below)
- [ ] Zero critical bugs or regressions
- [ ] Documentation complete and accurate
- [ ] Sprint 12 ready for merge and Sprint 13 planning

**Time Budget:** 1-2 hours

---

## Checkpoint Decision Trees

### Day 3 Checkpoint: Term Reduction Results

```
Baseline Analysis Complete
│
├─ Average ≥20% reduction on ≥5 models?
│  ├─ YES → ✅ SUCCESS
│  │        - Document results in SIMPLIFICATION_BENCHMARKS.md
│  │        - Proceed to Tier 2 (Day 4)
│  │        - Sprint 12 primary goal achieved
│  │
│  └─ NO → Evaluate reduction percentage
│           │
│           ├─ 15-19% average → ⚠️ PARTIAL SUCCESS
│           │                   - Document actual reduction
│           │                   - Proceed to Tier 2 (Day 4)
│           │                   - Note: Below target but useful improvement
│           │
│           └─ <15% average → ❌ NEEDS IMPROVEMENT
│                             - Defer Tier 2 to Days 7-8
│                             - Add LOW priority transformations (Days 4-6)
│                             - Re-measure on Day 6
│                             - Fallback: Document limitation if still <15%
```

### Day 6 Checkpoint: Tier 2 Parse Rate

```
Tier 2 Parse Rate Measured
│
├─ Parse rate ≥50% (5+ models)?
│  ├─ ≥60% (6+ models) → ✅ EXCEEDS EXPECTATIONS
│  │                     - Document success
│  │                     - Proceed to Day 7 (JSON + PATH)
│  │                     - Consider additional Tier 2 models in Sprint 13
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
│  │
│  └─ <40% (<4 models) → ❌ BELOW EXPECTATIONS
│                        - Defer complex blockers to Sprint 13
│                        - Document limitation
│                        - Proceed to Day 7 (don't block JSON/PATH)
│                        - Re-evaluate Tier 2 strategy in retrospective
```

### Day 7 Checkpoint: PATH Licensing Decision

```
PATH Email Response Status (1 week since Day 1)
│
├─ Approved for GitHub Actions?
│  ├─ YES, cloud CI allowed → ✅ IMPLEMENT PATH
│  │                          - Install PATH in CI (2-3h)
│  │                          - 4-test smoke suite
│  │                          - Validate accuracy vs IPOPT
│  │                          - Update docs
│  │
│  ├─ YES, but self-hosted runner required → ⚠️ EVALUATE FEASIBILITY
│  │                                          - Estimate setup cost
│  │                                          - If <2h: Implement
│  │                                          - If >2h: Defer to Sprint 13
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

---

## Risk Register

### Risk 1: Benchmarking Reveals <20% Reduction

**Category:** Technical  
**Likelihood:** Low (Sprint 11 prototype: 39%)  
**Impact:** High (invalidates success criterion)  
**Trigger:** Day 3 checkpoint shows <15% average reduction

**Mitigation:**
- Component 7 ready (LOW priority transformations: trig identities, exp/log identities)
- Task 2 research validated measurement methodology
- Task 7 prototype confirmed 0% counting error

**Contingency Plan:**
- Day 3: Defer Tier 2 to Days 7-8
- Days 4-6: Implement 2-3 additional transformations (6-8h)
- Day 6: Re-measure with new transformations
- If still <15%: Document actual reduction, adjust expectations for Sprint 13

**Assignment:** Day 3 checkpoint decision

---

### Risk 2: Tier 2 Blockers Extremely Complex (>10h each)

**Category:** Technical  
**Likelihood:** Medium  
**Impact:** Medium (affects parse rate target)  
**Trigger:** Day 4 analysis reveals no blockers <6h

**Mitigation:**
- Task 3 pre-selected diverse models (6 blocker patterns, 15h total)
- Task 8 template enables rapid re-prioritization
- Alternate candidates available (18 evaluated)

**Contingency Plan:**
- Day 4: Re-run analysis on alternate candidates (chenery → demandq, dipole, etc.)
- Select easier models if primary set too complex
- Acceptable outcome: 40-49% Tier 2 parse rate (still unlocks 4 models)
- Document complex blockers for Sprint 13

**Assignment:** Day 4 blocker analysis

---

### Risk 3: PATH No Response by Day 7

**Category:** External Dependency  
**Likelihood:** High (1 week response time optimistic)  
**Impact:** Low (IPOPT fallback working, <1% accuracy difference)  
**Trigger:** Day 7 checkpoint, no email response

**Mitigation:**
- Task 6 email template professional and specific
- Sent Day 1 to maximize response window
- IPOPT already working, PATH is nice-to-have

**Contingency Plan:**
- Day 7: Document no-response scenario
- Send follow-up email with urgency note
- Proceed with IPOPT as primary solver
- Re-evaluate in Sprint 13 if response arrives

**Assignment:** Day 7 checkpoint decision

---

### Risk 4: Convert Rate Tracking Reveals Pipeline Bugs

**Category:** Technical  
**Likelihood:** Medium  
**Impact:** Medium (blocks multi-metric completion)  
**Trigger:** Day 2 baseline collection shows unexpected convert rate failures

**Mitigation:**
- Sprint 11 convert rate informal tracking (no major issues)
- measure_parse_rate.py already tracks parse → MCP pipeline
- Task 4 research validated architecture

**Contingency Plan:**
- Day 2: Debug failures (1-2h embedded buffer)
- If >2h: Mark convert_rate as experimental, exclude from thresholds
- Document known issues in CI_REGRESSION_GUARDRAILS.md
- Full fix deferred to Sprint 13 if needed

**Assignment:** Day 2 baseline collection

---

### Risk 5: JSON Schema Evolution During Implementation

**Category:** Technical  
**Likelihood:** Low  
**Impact:** Low (schema versioned)  
**Trigger:** Day 7 implementation reveals missing fields

**Mitigation:**
- Task 5 created 3 example JSON files (success, partial, failure)
- Schema v1.0.0 locked, changes require v1.1.0

**Contingency Plan:**
- Day 7: Stick to schema v1.0.0 strictly
- Document discovered limitations in JSON_DIAGNOSTICS.md
- Plan v1.1.0 for Sprint 13 if needed

**Assignment:** Day 7 JSON implementation

---

### Risk 6: CI Workflow Testing Checklist Overhead

**Category:** Process  
**Likelihood:** Medium  
**Impact:** Low (slows PRs slightly)  
**Trigger:** Sprint 13 feedback on checklist being too prescriptive

**Mitigation:**
- Keep checklist short (5-7 items)
- Focus on high-impact items (syntax, paths, permissions)
- Optional guidance in CI_WORKFLOW_TESTING.md

**Contingency Plan:**
- Sprint 13 retrospective: Evaluate checklist adoption
- Refine based on feedback
- Remove low-value items

**Assignment:** Day 8 checklist creation

---

## Success Criteria

### PRIMARY (Must Achieve)

1. ✅ **Term Reduction Validated**
   - Metric: Average term reduction percentage across 10 Tier 1 models
   - Target: ≥20% on ≥50% models (5+ models)
   - Verification: baselines/simplification/baseline_sprint11.json + SIMPLIFICATION_BENCHMARKS.md
   - Fallback: 15-19% acceptable if transformations added
   - **Checkpoint:** Day 3

2. ✅ **Multi-Metric CI Complete**
   - Metrics: parse_rate, convert_rate, performance
   - Target: All 3 metrics functional with warn/fail thresholds
   - Verification: .github/workflows/gamslib-regression.yml + PR comment
   - Exit codes: 0 (pass), 1 (warn), 2 (fail)
   - **Checkpoint:** Day 3

3. ✅ **Tier 2 Parse Rate ≥50%**
   - Metric: Tier 2 models successfully parsing
   - Target: ≥50% (5/10 models) = ≥75% overall (15/20 total)
   - Verification: ingest_gamslib.py results + TIER_2_MODELS.md
   - Fallback: 40-49% acceptable (partial success)
   - **Checkpoint:** Day 6

4. ✅ **JSON Diagnostics Functional**
   - Feature: --diagnostics --format json
   - Target: Valid JSON matching schema v1.0.0
   - Verification: CI artifacts + docs/JSON_DIAGNOSTICS.md
   - Backward compatible: text format default
   - **Checkpoint:** Day 7

5. ✅ **PATH Decision Documented**
   - Decision: Implemented, documented, or deferred
   - Target: Clear decision with rationale
   - Verification: CI workflow OR docs/infrastructure/PATH_SOLVER_DECISION.md
   - Acceptable: Any outcome (approve/deny/defer)
   - **Checkpoint:** Day 7

6. ✅ **CI Process Improvements**
   - Deliverable: CI workflow testing checklist
   - Target: Zero CI-fix follow-up PRs in Sprint 13
   - Verification: PR template + CI_WORKFLOW_TESTING.md
   - Metric: Track in Sprint 13 retrospective
   - **Checkpoint:** Day 8

### SECONDARY (Stretch Goals)

1. ⭐ **Tier 2 ≥60% Parse Rate**
   - Target: 6+ models (exceeds 50% goal)
   - Impact: Overall parse rate 80% (16/20)

2. ⭐ **Term Reduction ≥30% Average**
   - Target: Exceeds 20% goal significantly
   - Validates transformation effectiveness

3. ⭐ **Dashboard Integration**
   - Deliverable: HTML dashboard with charts
   - Requires: JSON diagnostics complete
   - Effort: 2-3h (Day 9 optional)

4. ⭐ **Performance Trending**
   - Deliverable: Time-series charts
   - Requires: Historical baseline data
   - Effort: 2-3h (Day 9 optional)

5. ⭐ **One or More LOW Priority Items**
   - Options: Naming convention, CSE temp propagation, additional docs
   - Effort: 1-3h each
   - Conditional: Day 9 buffer available

### Quality Gates (Continuous)

- ✅ All tests passing: Fast <30s, full <2 min
- ✅ No Tier 1 regressions (100% maintained)
- ✅ Quality checks: typecheck ✅, lint ✅, format ✅
- ✅ CI green: All workflows passing
- ✅ Documentation: All deliverables documented

---

## Buffer Strategy

**Total Buffer:** ~5 hours (23% of 22-27h scope)

### Allocation

1. **Embedded Buffer (1-2h):**
   - Days 1-8: ±15 min per day for unknowns
   - Absorbed in daily estimates (e.g., "2-3h" includes 15 min buffer)

2. **Day 9 Buffer (2-3h):**
   - Dedicated contingency day
   - Use for checkpoint recovery OR optional items
   - Flexible allocation based on sprint progress

3. **Day 10 Buffer (1-2h):**
   - Final validation and polish
   - Retrospective and PR creation
   - Minimal technical work (documentation focus)

### Usage Scenarios

**Scenario A: All checkpoints pass (5h available)**
- Days 1-8: 1h absorbed in estimates
- Day 9: 2-3h for optional items (dashboard, trending, naming)
- Day 10: 1-2h for validation and retrospective

**Scenario B: One checkpoint fails (3-4h available)**
- Days 1-8: 1-2h absorbed for checkpoint recovery
- Day 9: 2-3h for continued recovery or partial optional items
- Day 10: 1h for validation (minimal retrospective)

**Scenario C: Multiple checkpoints fail (2-3h available)**
- Days 1-8: 2-3h absorbed for multiple recoveries
- Day 9: 2-3h for final recovery efforts
- Day 10: 1h minimal validation, defer retrospective

**Validation:**
- Sprint 11 buffer utilization: 10% (1.6h of 16h scope)
- Sprint 12 allocation: 23% (5h of 22-27h scope)
- Conservative estimate accounts for measurement unknowns

---

## Unknown Verification (7.1 and 7.2)

### Unknown 7.1: Sprint 12 Scope Management

**Assumption:** Sprint 12 scope of 19-28h is realistic given Sprint 10-11 velocity.

**Verification Method:**
- Analyze Sprint 10-11 actual vs estimated effort
- Calculate realistic Sprint 12 capacity
- Define minimum viable Sprint 12 (PRIMARY criteria only)

**Findings:**

**Sprint 10 Velocity:**
- Estimated: 35-42h
- Actual: ~38h (documented in SPRINT_10/RETROSPECTIVE.md)
- Accuracy: +2% (excellent estimation)

**Sprint 11 Velocity:**
- Estimated: 29-36h
- Actual: ~32h (documented in SPRINT_11/RETROSPECTIVE.md)
- Accuracy: -3% (excellent estimation)
- Buffer utilization: 10% (1.6h of 16h scope)

**Sprint 12 Capacity Calculation:**
- Historical average: (38 + 32) / 2 = 35h per sprint
- Sprint 12 estimate: 22-27h (midpoint: 24.5h)
- Safety margin: 24.5h / 35h = 70% of historical capacity
- **Conclusion:** Conservative scope, high confidence

**Minimum Viable Sprint 12:**
- PRIMARY criteria only: 10-14h
  - Component 1: Term reduction (4-6h)
  - Component 2: Multi-metric (3-4h)
  - Component 5 (partial): Tier 2 core blockers (3-4h)
- If scope reduction needed: Defer Components 3, 4, 6 to Sprint 13
- **Decision:** 22-27h scope is realistic, minimum viable = 10-14h

**Risk:** LOW - Sprint 12 scope is 70% of historical capacity

**Verification Status:** ✅ VERIFIED

---

### Unknown 7.2: Dependency on External Research

**Assumption:** PATH licensing response will arrive within Sprint 12, or non-response won't block sprint.

**Verification Method:**
- Identify all external dependencies in Sprint 12
- Document plan B for each dependency
- Front-load external research to maximize response window

**Findings:**

**External Dependencies Identified:**

1. **PATH Licensing (Component 4)**
   - Dependency: Email response from ferris@cs.wisc.edu
   - Timeline: Sent Day 1, decision Day 7 (1 week)
   - **Plan B:** IPOPT fallback (already working)
   - Risk: LOW (IPOPT adequate, <1% accuracy difference)
   - **Mitigation:** Professional email template (Task 6), send Day 1

2. **GAMSLib Model Availability (Component 5)**
   - Dependency: GAMSLib models downloadable
   - Timeline: Day 4 download
   - **Plan B:** Use cached models from Task 3 (tests/fixtures/tier2_candidates/)
   - Risk: VERY LOW (models already downloaded in prep)
   - **Mitigation:** Models cached in repo during prep

3. **No Other External Dependencies**
   - All other components self-contained
   - No third-party API calls
   - No external data sources

**Front-Loading Strategy:**
- PATH email: Day 1 (maximizes 7-day response window)
- Tier 2 models: Pre-downloaded in Task 3 (no Day 4 dependency)
- All prep tasks: Completed before sprint start (no in-sprint research blockers)

**Contingency for PATH:**
- Day 7 checkpoint evaluates 4 scenarios
- All scenarios have clear action plans (implement, document, defer)
- No scenario blocks sprint completion

**Risk:** LOW - Only 1 external dependency with robust fallback

**Verification Status:** ✅ VERIFIED

---

## Prep Task Completion Summary

### All 10 Prep Tasks Complete ✅

| Task | Status | Effort | Key Deliverable |
|------|--------|--------|-----------------|
| 1. Known Unknowns | ✅ | 2-3h | 27 unknowns, 7 categories |
| 2. Term Reduction Research | ✅ | 3-4h | Measurement methodology |
| 3. Tier 2 Model Selection | ✅ | 2-3h | 10 models, 6 blockers |
| 4. Multi-Metric Research | ✅ | 2h | Threshold architecture |
| 5. JSON Schema Design | ✅ | 1-2h | Schema v1.0.0 |
| 6. PATH Email Template | ✅ | 1h | Email ready to send |
| 7. Metrics Prototype | ✅ | 3-4h | 0% error, 7.5% overhead |
| 8. Blocker Template | ✅ | 1-2h | Priority formula |
| 9. Baseline Infrastructure | ✅ MERGED | 2h | baselines/, scripts/, docs/ |
| 10. Sprint 12 Schedule | ✅ | 4-5h | This document |

**Total Prep Effort:** 21-28h estimated, actual tracked in PREP_PLAN.md

**Unknowns Verified:** 27/27 (100%) ✅

**Sprint 12 Ready:** All infrastructure, research, and planning complete

---

## Next Steps

1. **Review & Approval:**
   - Team review of PLAN.md
   - Validate hour estimates
   - Confirm checkpoint criteria

2. **Sprint 12 Start:**
   - Create sprint12-complete branch
   - Send PATH email (Day 1 first task)
   - Begin Day 1 tasks (SimplificationMetrics, count_terms)

3. **Daily Execution:**
   - Follow day-by-day schedule
   - Make checkpoint decisions based on actual data
   - Update PLAN.md with actual vs estimated effort

4. **Sprint 12 End:**
   - Day 10 retrospective
   - Update PROJECT_PLAN.md
   - Create Sprint 12 → main PR
   - Begin Sprint 13 planning

---

**Document Status:** ✅ COMPLETE  
**Ready for:** Sprint 12 Execution  
**Estimated Duration:** 10 working days (22-27h)  
**Success Probability:** HIGH (based on Sprint 10-11 velocity, comprehensive prep)
