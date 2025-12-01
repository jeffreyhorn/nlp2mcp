# Sprint 12 Plan (REVISED): Measurement, Polish, and Tier 2 Expansion

**Sprint:** Sprint 12 (Weeks 13-14)  
**Epic:** Epic 2 - Multi-Solver MCP Server  
**Start Date:** TBD (after prep completion)  
**Duration:** 10 working days  
**Total Capacity:** 80 hours (10 days × 8 hours/day)  
**Allocated Effort:** 65-72 hours  
**Buffer:** 8-15 hours (10-19%)  
**Theme:** Validate Sprint 11 achievements, complete technical debt, expand to Tier 2, add deferred features

---

## Executive Summary

Sprint 12 validates Sprint 11's aggressive simplification through quantitative measurement, completes half-implemented multi-metric thresholds, expands parser coverage to Tier 2 GAMSLib models, and pulls forward deferred features to utilize the full 80-hour capacity. This sprint emphasizes measurement over new features while expanding scope to match available time.

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
5. **Additional Features:** Dashboard integration, performance trending, LOW priority transformations (if needed)
6. **Documentation:** Update KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md

**Capacity Utilization:**
- Original plan: 22-27h (28-34% of 80h capacity)
- Revised plan: 65-72h (81-90% of 80h capacity)
- Added scope: ~40h of deferred features, expanded validation, and documentation

---

## Scope & Effort Allocation

### Total Hours: 65-72h (of 80h capacity)

| Phase | Days | Components | Original | Revised | Change |
|-------|------|------------|----------|---------|--------|
| **Measurement & Validation** | 1-3 | Benchmarking, Multi-Metric | 7-10h | 9-12h | +2h validation |
| **Tier 2 Expansion** | 4-6 | Model Selection, Blockers | 7-9h | 18-22h | +11-13h scope |
| **Polish & Integration** | 7-8 | JSON, PATH, CI, Dashboard | 4-6h | 16-20h | +12-14h features |
| **Extended Features** | 9 | LOW priority items, trending | 0h | 12-14h | NEW |
| **Buffer & Validation** | 10 | Contingency, Final Testing | 3-4h | 10-14h | +7-10h depth |

### Scope by Priority

**HIGH Priority (Must Do - 20-24h):**
1. Term Reduction Benchmarking (6-8h, expanded validation)
2. Multi-Metric Threshold Implementation (3-4h)
3. Tier 2 Expansion - Core + Extended (10-12h, more models/blockers)

**MEDIUM Priority (Should Do - 28-32h):**
4. JSON Diagnostics Output (3h, with CI integration)
5. Tier 2 Expansion - Additional Candidates (6-8h, stretch to 60%+)
6. PATH Solver CI Integration (3-5h, conditional)
7. CI Workflow Testing Checklist (2h, with examples)
8. Dashboard Integration (4-6h, pulled forward from deferred)
9. Performance Trending (4-6h, pulled forward from deferred)

**LOW Priority (Conditional - 17-26h):**
10. Additional transformations if <20% reduction (6-8h)
11. Naming convention alignment (1-2h)
12. CSE temp propagation (2-3h, if user feedback available)
13. Transformation catalog alignment (1-2h, documentation)
14. Extended Tier 2 analysis (4-6h, push to 70%+ parse rate)
15. Documentation updates (2-3h, KNOWN_UNKNOWNS, PREP_PLAN, CHANGELOG)

---

## Prep Task Synthesis

All 10 Sprint 12 preparation tasks completed successfully (21-28h estimated, actual time tracked in PREP_PLAN.md):

### Task 1: Known Unknowns (27 unknowns identified)
- **Status:** ✅ COMPLETE
- **Key Findings:** 27 unknowns across 7 categories, all assigned to verification tasks
- **Impact:** Comprehensive risk catalog enables proactive mitigation
- **Sprint 12 Update:** Day 10 will update KNOWN_UNKNOWNS.md with verification results

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
- **Revised Scope:** With 80h capacity, expand to implement medium+stretch blockers

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
- **Revised Scope:** With 80h capacity, apply template to all 6 blockers

### Task 9: Baseline Storage Infrastructure
- **Status:** ✅ COMPLETE - MERGED (PR #343)
- **Deliverables:**
  - baselines/simplification/ with README and placeholder
  - baselines/multi_metric/ with README and placeholder
  - scripts/update_baselines.sh executable script
  - docs/infrastructure/BASELINES.md
- **Impact:** Infrastructure ready, no Day 1 setup blockers

### Task 10: Sprint 12 Detailed Schedule
- **Status:** ✅ COMPLETE (original PLAN.md)
- **Revision:** This document (PLAN_REVISED.md) resizes to 80h capacity

### Unknowns Status

**Verified:** 25/27 unknowns (93%) in original prep

**Remaining (to verify in Task 10):**
- 7.1: Sprint 12 Scope Management → ✅ VERIFIED in PLAN.md (now resized to 80h)
- 7.2: Dependency on External Research → ✅ VERIFIED in PLAN.md

**Resolution Rate:**
- Category 1 (Term Reduction): 7/7 verified ✅
- Category 2 (Multi-Metric): 4/4 verified ✅
- Category 3 (JSON): 3/3 verified ✅
- Category 4 (PATH): 4/4 verified ✅
- Category 5 (Tier 2): 4/4 verified ✅
- Category 6 (CI): 3/3 verified ✅
- Category 7 (Process): 2/2 verified ✅

---

## Day-by-Day Schedule

### Day 1: Measurement Infrastructure Setup (3-4h)

**Focus:** Component 1 (Term Reduction Benchmarking - Part 1)

**Tasks:**
1. Send PATH licensing email to ferris@cs.wisc.edu (15 min)
   - Use template from Task 6
   - Track response for Day 7 checkpoint
2. Implement SimplificationMetrics class (75-90 min)
   - Location: `src/ir/metrics.py` (new file)
   - Based on Task 7 prototype EnhancedSimplificationMetrics
   - Fields: model, ops_before, ops_after, terms_before, terms_after, execution_time_ms, transformations_applied
   - Methods: to_dict(), calculate_reductions()
3. Implement count_terms() function (45-60 min)
   - Location: `src/ir/metrics.py`
   - Use Task 7 prototype implementation (validated 0% error)
   - Add docstring with examples
   - Unit tests: test_count_terms.py with 15+ test cases (expanded from 10)
4. Instrument simplification pipeline (60-75 min)
   - Update `src/ir/simplification_pipeline.py`
   - Add optional metrics collection to apply() method
   - Collect before/after metrics when enabled
   - No changes to transformation functions (instrumentation only)

**Deliverables:**
- [ ] PATH email sent (tracked in email client)
- [ ] src/ir/metrics.py with SimplificationMetrics and count_terms()
- [ ] tests/unit/test_metrics.py with ≥15 test cases
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
- [ ] count_terms() validated on 15+ expressions (including Task 7 examples)
- [ ] Pipeline instrumentation works on rbrock.gms without errors
- [ ] make test-fast completes in <30s
- [ ] PATH email sent and delivery confirmed

**Time Budget:** 3-4 hours

---

### Day 2: Baseline Collection & Multi-Metric Backend (4-5h)

**Focus:** Component 1 (Part 2) + Component 2 (Part 1)

**Tasks:**
1. Create measure_simplification.py script (120-150 min)
   - Location: `scripts/measure_simplification.py`
   - CLI: `--model MODEL` or `--model-set tier1` 
   - Functionality:
     - Load model and parse to AST
     - Run simplification with metrics collection
     - Aggregate results across all models
     - Output JSON matching baselines/simplification/README.md schema
   - Output: JSON to stdout or `--output FILE`
   - Example: `./scripts/measure_simplification.py --model-set tier1 --output baselines/simplification/baseline_sprint11.json`

2. Populate baseline_sprint11.json (45-60 min)
   - Run measure_simplification.py on all 10 Tier 1 models
   - Validate JSON against schema (jq validation)
   - Update metadata: commit SHA, timestamp, sprint "sprint11"
   - Commit baseline to git
   - Run extended validation (verify on 3 additional synthetic models)

3. Implement multi-metric threshold backend (75-90 min)
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
- [ ] Extended validation on synthetic models

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
- [ ] Extended validation passes on synthetic models

**Time Budget:** 4-5 hours

---

### Day 3: Validation & Checkpoint (2-3h)

**Focus:** Component 1 (Part 3) + Component 2 (Part 2) + Checkpoint

**Tasks:**
1. Analyze baseline_sprint11.json results (45-60 min)
   - Calculate aggregate metrics:
     - Average term reduction percentage across 10 models
     - Average operation reduction percentage
     - Models meeting ≥20% threshold
   - Identify top 3 most effective transformations
   - Create analysis summary in `docs/SIMPLIFICATION_BENCHMARKS.md`
   - Include per-transformation effectiveness breakdown

2. Extend measure_parse_rate.py for unified metrics (45-60 min)
   - Add `--all-metrics` flag
   - Track parse_rate, convert_rate, performance in single JSON
   - Output format matching baselines/multi_metric/README.md schema
   - Populate baselines/multi_metric/baseline_sprint12.json placeholder

3. Update CI workflow for multi-metric (30-45 min)
   - Edit `.github/workflows/gamslib-regression.yml`
   - Replace single parse-rate check with multi-metric check
   - Add all 6 threshold arguments (warn/fail for each metric)
   - Update PR comment template to show all 3 metrics
   - Add example PR comment to documentation

**Deliverables:**
- [ ] docs/SIMPLIFICATION_BENCHMARKS.md with detailed analysis
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
  - **If <15% average:** ❌ FAIL - Add LOW priority transformations Day 9 (defer some Tier 2 work)

**Risks & Mitigation:**
- Risk: Results show <20% reduction
  - Mitigation: LOW priority transformations ready (6-8h on Day 9)
  - Fallback: Document actual reduction, adjust future expectations

**Success Criteria:**
- [ ] Checkpoint decision made based on actual data
- [ ] All 3 metrics (parse, convert, performance) tracked in CI
- [ ] PR comment format validated (table with ✅/⚠️/❌)
- [ ] Components 1 & 2 complete and functional
- [ ] Per-transformation effectiveness documented

**Time Budget:** 2-3 hours

---

### Day 4: Tier 2 Model Analysis & High-Priority Blockers (7-8h)

**Focus:** Component 5 (Tier 2 Expansion - Part 1 + Part 2)

**Tasks:**
1. Download 10 Tier 2 candidate models (15 min)
   - Use `scripts/download_tier2_candidates.sh` from Task 3
   - Models: chenery, jbearing, fct, chem, water, gastrans, process, least, like, bearing
   - Location: `tests/fixtures/gamslib/tier2/`

2. Run parse failure analysis (60-75 min)
   - Use `scripts/analyze_tier2_candidates.py` from Task 3
   - Classify failures by blocker pattern
   - Generate `tests/fixtures/tier2_candidates/analysis_results.json`
   - Validate against Task 3 predictions
   - Identify frequency and complexity of each blocker

3. Prioritize blockers using Task 8 template (60-75 min)
   - Apply classification schema (Frequency, Complexity, Category, Criticality)
   - Calculate priority scores for each blocker
   - Create `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md`
   - Fill template for all discovered blockers
   - Sort by priority, select top blockers fitting 12h budget (expanded from 6h)

4. Implement Blocker #1 (HIGH priority, 90-120 min)
   - Based on priority analysis
   - Likely: special_chars_in_identifiers (1.5h) OR predefined_constants (1h)
   - Update lexer/grammar
   - Add AST nodes if needed
   - Unit tests (8-12 test cases)
   - Integration test (affected model parses)

5. Implement Blocker #2 (HIGH priority, 90-120 min)
   - Based on priority analysis
   - Likely: multiple_alias_declaration (1.5h)
   - Grammar extension
   - Symbol table updates
   - Unit tests
   - Integration test

6. Create implementation plan for Days 5-6 (30 min)
   - Document remaining blockers for Days 5-6
   - Effort estimates (with 80h capacity, allocate 10-12h more for Tier 2)
   - Stretch goal: 60%+ Tier 2 parse rate (6+ models)

**Deliverables:**
- [ ] 10 Tier 2 models downloaded
- [ ] Parse failure analysis complete (JSON results)
- [ ] TIER_2_BLOCKER_ANALYSIS.md with prioritized blockers
- [ ] 2 high-priority blockers implemented and tested
- [ ] 2-3 Tier 2 models now parsing
- [ ] Implementation plan for Days 5-6 (10-12h scope)

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Blockers differ from Task 3 predictions
  - Mitigation: Template flexible, re-prioritize based on actual failures
- Risk: Blocker more complex than estimated
  - Mitigation: With 80h capacity, more time available for complex blockers

**Success Criteria:**
- [ ] Blocker analysis matches template format
- [ ] Priority scores calculated for all blockers
- [ ] ≥2 blockers fully implemented and tested
- [ ] ≥2 Tier 2 models parsing (cumulative)
- [ ] All Tier 1 tests still passing (no regressions)

**Time Budget:** 7-8 hours

---

### Day 5: Tier 2 Medium-Priority Blocker Implementation (6-7h)

**Focus:** Component 5 (Part 3) - Implement medium-priority blockers

**Tasks:**
1. Implement Blocker #3 (MEDIUM priority, 90-120 min)
   - Based on Day 4 priority analysis
   - Likely: inline_descriptions (2h) or partial thereof
   - Grammar changes for optional description strings
   - AST node updates
   - Unit tests for basic cases

2. Implement Blocker #4 (MEDIUM priority, 90-120 min)
   - Based on Day 4 priority analysis
   - Example: table_wildcard_domain or model_specific_constructs
   - Grammar extension
   - Symbol table updates if needed
   - Unit tests

3. Implement Blocker #5 (MEDIUM priority, 90-120 min)
   - Based on Day 4 priority analysis
   - Push toward ≥50% Tier 2 parse rate (5/10 models)
   - Full testing and integration validation

4. Polish and integration testing (60-90 min)
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

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Blocker more complex than estimated
  - Mitigation: Stop at allocated time, continue on Day 6
- Risk: Fix breaks Tier 1 models
  - Mitigation: Run full Tier 1 regression after each blocker

**Success Criteria:**
- [ ] ≥3 blockers fully implemented and tested
- [ ] ≥5 Tier 2 models parsing (cumulative, ≥50% rate)
- [ ] All Tier 1 tests still passing (no regressions)
- [ ] Code quality: typecheck ✅, lint ✅, format ✅

**Time Budget:** 6-7 hours

---

### Day 6: Tier 2 Stretch Blockers & Checkpoint (5-6h)

**Focus:** Component 5 (Part 4) + Checkpoint

**Tasks:**
1. Implement Blocker #6 (STRETCH goal, 90-120 min)
   - Stretch toward ≥60% Tier 2 parse rate (6+ models)
   - Based on Day 4-5 progress
   - May be partial implementation if complex

2. Measure Tier 2 parse rate (30 min)
   - Run ingest_gamslib.py on all 10 Tier 2 models
   - Calculate parse rate: (models parsed / 10) × 100%
   - Update baselines/multi_metric/baseline_sprint12.json with Tier 2 results
   - Document which models parse and which fail

3. Create Tier 2 documentation (45-60 min)
   - `docs/TIER_2_MODELS.md`: List of 10 models with status
   - `docs/TIER_2_IMPLEMENTATION_PLAN.md`: Blockers implemented, remaining work
   - Document expected vs actual results
   - Detailed blocker analysis for remaining failures

4. Extended Tier 2 candidate analysis (90-120 min, NEW with 80h capacity)
   - If ≥60% achieved: Analyze 5 additional Tier 2 candidates
   - Identify next-sprint blockers
   - Create roadmap for 80%+ overall parse rate
   - Document in TIER_2_IMPLEMENTATION_PLAN.md

**Deliverables:**
- [ ] Tier 2 parse rate measured and documented
- [ ] docs/TIER_2_MODELS.md with detailed status
- [ ] docs/TIER_2_IMPLEMENTATION_PLAN.md
- [ ] Extended candidate analysis (if ≥60% achieved)
- [ ] Commit: "Complete Tier 2 expansion (≥50% parse rate)"

**Decision Point: DAY 6 CHECKPOINT**

**Checkpoint Criteria:**
- **Trigger:** Tier 2 parse rate measured
- **Metric:** Percentage of 10 Tier 2 models successfully parsing
- **Success:** ≥50% (5/10 models) = ≥75% overall (15/20 total)
- **Decisions:**
  - **If ≥60% (6+ models):** ✅ EXCEEDS - Proceed with extended analysis
  - **If 50-59% (5 models):** ✅ MEETS - Proceed to Day 7
  - **If 40-49% (4 models):** ⚠️ PARTIAL - Document, continue to Day 7
  - **If <40% (<4 models):** ❌ BELOW - Document limitation, focus on polish

**Risks & Mitigation:**
- Risk: Parse rate <50%
  - Mitigation: With 80h capacity, more time available for recovery
  - Fallback: Document remaining blockers for Sprint 13

**Success Criteria:**
- [ ] Tier 2 parse rate ≥50% (5/10 models)
- [ ] Overall parse rate ≥75% (15/20 models: 10 Tier 1 + 5 Tier 2)
- [ ] All blockers documented with effort estimates
- [ ] Extended analysis complete (if exceeds expectations)

**Time Budget:** 5-6 hours

---

### Day 7: JSON Diagnostics & PATH Decision (6-7h)

**Focus:** Component 3 (JSON Diagnostics) + Component 4 (PATH Decision) + Dashboard (Part 1)

**Tasks:**
1. Implement JSON diagnostics output (120-150 min)
   - Update `src/ir/diagnostics.py`
   - Extend DiagnosticReport with to_json() method
   - Use schema from Task 5 (v1.0.0)
   - Add --format flag: `--diagnostics --format json`
   - Default: text (backward compatible)
   - Output to stdout or --output FILE

2. Create JSON schema documentation (45 min)
   - Copy Task 5 examples to `docs/schemas/diagnostics_v1.0.0.json`
   - Document in `docs/JSON_DIAGNOSTICS.md`
   - Include CI usage examples (jq queries)
   - Add validation examples

3. Integrate JSON diagnostics with CI (45-60 min)
   - Update CI workflow to store JSON as artifacts
   - Example: `--diagnostics --format json --output diagnostics.json`
   - Upload artifacts for historical trending
   - Document in CI_REGRESSION_GUARDRAILS.md

**Decision Point: DAY 7 CHECKPOINT (PATH Licensing)**

**Checkpoint Criteria:**
- **Trigger:** 1 week since PATH email sent (Day 1)
- **Metric:** Email response status
- **Decisions:**
  - **Approved for GitHub Actions:** ✅ Implement PATH (2-3h on Day 7)
  - **Denied or restricted:** ⚠️ Document decision, keep IPOPT
  - **No response:** ⚠️ Send follow-up, proceed with IPOPT
  - **Self-hosted runner required:** ⚠️ Evaluate feasibility, likely defer

**Tasks (if PATH approved):**
4. Install PATH in CI (90-120 min) - CONDITIONAL
   - Download PATH solver (free version: 300 vars / 2000 nonzeros)
   - Add to GitHub Actions workflow
   - Create smoke test suite (4 tests from Sprint 11 research)
   - Validate PATH vs IPOPT accuracy (<1% difference)

**Tasks (if PATH denied/no response):**
4. Document PATH decision (45 min) - CONDITIONAL
   - Create `docs/infrastructure/PATH_SOLVER_DECISION.md`
   - Document email exchange, licensing terms, decision rationale
   - Note IPOPT as primary solver, PATH deferred
   - Recommendation for future (self-hosted runner or commercial license)

5. Start dashboard infrastructure (60-90 min, NEW with 80h capacity)
   - Create `scripts/generate_dashboard.py` skeleton
   - Parse JSON diagnostics from CI artifacts
   - Set up Chart.js integration
   - Initial HTML template

**Deliverables:**
- [ ] JSON diagnostics implemented (--format json works)
- [ ] docs/schemas/diagnostics_v1.0.0.json
- [ ] docs/JSON_DIAGNOSTICS.md
- [ ] CI artifacts storing JSON diagnostics
- [ ] PATH decision made and documented OR PATH implemented in CI
- [ ] Dashboard infrastructure started

**Risks & Mitigation:**
- Risk: JSON schema evolves during implementation
  - Mitigation: Stick to Task 5 schema v1.0.0, defer changes to v1.1.0
- Risk: No PATH response
  - Mitigation: Proceed with IPOPT, document decision

**Success Criteria:**
- [ ] --diagnostics --format json produces valid JSON matching schema
- [ ] CI workflow stores JSON artifacts
- [ ] PATH decision finalized (implemented, documented, or deferred)
- [ ] Dashboard infrastructure ready for Day 8 completion
- [ ] All quality checks passing

**Time Budget:** 6-7 hours

---

### Day 8: Dashboard Completion & CI Checklist (6-7h)

**Focus:** Component 6 (CI Checklist) + Dashboard (Part 2) + Documentation Polish

**Tasks:**
1. Complete dashboard implementation (120-180 min, NEW with 80h capacity)
   - Implement Chart.js visualizations:
     - Stage timing chart (bar chart: Parse, Semantic, Simplification, IR, MCP)
     - Simplification effectiveness over time (line chart: Sprints 10-12)
     - Transformation application frequency (pie chart)
     - Model comparison table (heatmap)
   - Fetch diagnostic JSON from CI artifacts API
   - Generate static HTML dashboard
   - Host on GitHub Pages or CI artifacts

2. Create CI workflow testing guide (60-75 min)
   - Document: `docs/infrastructure/CI_WORKFLOW_TESTING.md`
   - Sections:
     - Syntax validation (yamllint, actionlint)
     - File path verification (paths exist in repo)
     - Permission checks (secrets, GITHUB_TOKEN)
     - Matrix build testing (all combinations)
     - Common pitfalls (Sprint 11 lessons learned)
   - Include command examples for local testing
   - Add actionlint integration to make targets

3. Update PR template with checklist (30-45 min)
   - Edit `.github/pull_request_template.md`
   - Add "CI Workflow Changes" section
   - Checklist items:
     - [ ] Workflow syntax validated locally
     - [ ] File paths verified
     - [ ] Matrix builds tested
     - [ ] Secrets/permissions documented
     - [ ] CI passes on PR before merge
   - Link to CI_WORKFLOW_TESTING.md guide

4. Performance trending infrastructure (90-120 min, NEW with 80h capacity)
   - Create `docs/performance/TRENDS.md`
   - Table format: Sprint | Parse Rate | Convert Rate | Test Time | Simplification
   - Populate with Sprints 8-12 data
   - Create automation script for updates
   - Optional: Chart.js visualizations integrated with dashboard

5. Polish Sprint 12 documentation (30-45 min)
   - Review all docs created in Sprint 12
   - Fix formatting, typos, broken links
   - Ensure consistency across documents
   - Update table of contents where needed

**Deliverables:**
- [ ] Dashboard complete and deployed (GitHub Pages or artifacts)
- [ ] docs/infrastructure/CI_WORKFLOW_TESTING.md
- [ ] Updated .github/pull_request_template.md
- [ ] docs/performance/TRENDS.md with historical data
- [ ] All Sprint 12 docs polished and consistent
- [ ] Commit: "Add dashboard, CI checklist, and performance trending"

**Decision Points:** None

**Risks & Mitigation:**
- Risk: Dashboard complexity exceeds estimate
  - Mitigation: Simplify visualizations, use templates
- Risk: Checklist too prescriptive
  - Mitigation: Keep short (5-7 items), focus on high-impact issues

**Success Criteria:**
- [ ] Dashboard accessible and functional (shows ≥3 sprints data)
- [ ] CI testing guide covers all common pitfalls
- [ ] PR template checklist actionable and concise
- [ ] Performance trending shows Sprints 8-12
- [ ] All documentation reviewed and polished

**Time Budget:** 6-7 hours

---

### Day 9: Extended Features & Low Priority Items (12-14h)

**Focus:** LOW priority items, additional validation, conditional transformations

**Scenario A: Day 3 Checkpoint Success (≥20% reduction) - 12-14h available**

**Tasks:**
1. Naming convention alignment (60-90 min)
   - Review `src/ir/` and `src/ad/` for inconsistent naming
   - Align with PROJECT_PLAN.md conventions
   - Create naming standards document
   - Update CONTRIBUTING.md with guidelines

2. Transformation catalog alignment (60-90 min)
   - Update `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md`
   - Mark implementation status for all 18 patterns
   - Create summary table (implemented/deferred/merged)
   - Cross-reference with SIMPLIFICATION_BENCHMARKS.md

3. CSE temp variable propagation (120-180 min, if time permits)
   - Implement temp preservation in MCP generation
   - Preserve `cse_tmp_*` variables in output
   - Add `--cse-inline` flag for backward compatibility
   - Test suite validating both modes
   - Example outputs

4. Extended Tier 2 validation (120-180 min)
   - Run longer benchmark runs on all 20 models (Tier 1 + Tier 2)
   - Synthetic test generation for edge cases
   - Multi-metric threshold resilience checks
   - Performance profiling and optimization
   - Document results

5. Additional documentation polish (60-90 min)
   - Review all Epic 2 documentation
   - Update cross-references
   - Ensure consistency across sprints
   - Prepare for Epic 2 completion

**Scenario B: Day 3 Checkpoint Failure (<15% reduction) - 12-14h needed**

**Tasks:**
1. Implement LOW priority transformations (6-8h)
   - T5.2: Nested Expression CSE (2h)
   - T2.3: Common Denominator (2h)
   - T5.4: CSE with Aliasing (2h)
   - T3.3: Multiplication-Division Reordering (2h, optional)
   - Test suite (10+ tests per pattern)

2. Re-measure simplification effectiveness (60-90 min)
   - Run measure_simplification.py with new transformations
   - Update baseline_sprint11.json
   - Validate ≥20% target now met
   - Update SIMPLIFICATION_BENCHMARKS.md

3. Extended validation and testing (120-180 min)
   - Comprehensive regression testing
   - Edge case validation
   - Performance impact assessment
   - Documentation updates

**Deliverables:**
- [ ] Scenario A: ≥2 LOW priority items complete
- [ ] Scenario B: LOW priority transformations implemented and validated
- [ ] Extended validation results documented
- [ ] All code quality checks passing

**Decision Points:**
- Choose Scenario A or B based on Day 3 checkpoint result
- Prioritize items based on time remaining and value

**Success Criteria:**
- [ ] Time used productively (not idle)
- [ ] If Scenario A: Naming conventions aligned, catalog updated
- [ ] If Scenario B: ≥20% reduction target now met
- [ ] Extended validation complete
- [ ] No critical blockers for Day 10

**Time Budget:** 12-14 hours

---

### Day 10: Documentation Updates & Final Validation (10-14h)

**Focus:** Documentation completion, comprehensive validation, retrospective

**Tasks:**
1. Update KNOWN_UNKNOWNS.md verification status (60-90 min, REQUIRED)
   - Mark all 27 unknowns with verification results
   - Document which unknowns were validated vs. remain open
   - Update resolution status for each category
   - Add Sprint 12 learnings to inform Sprint 13

2. Update PREP_PLAN.md Task 10 status (60-90 min, REQUIRED)
   - Mark Task 10 (Sprint 12 Detailed Schedule) as COMPLETE
   - Add result summary: actual vs estimated effort for all 10 days
   - Document checkpoint decisions and outcomes
   - Note any deviations from plan
   - Calculate total prep effort (21-28h estimated vs actual)

3. Create CHANGELOG.md entries (60-90 min, REQUIRED)
   - Sprint 12 section with all deliverables
   - Categorize: Features, Improvements, Bug Fixes, Documentation
   - Link to relevant PRs and docs
   - Format following existing CHANGELOG structure
   - Include metrics: parse rate, reduction %, models supported

4. Run comprehensive validation (90-120 min)
   - All 20 models (10 Tier 1 + 10 Tier 2)
   - Validate parse rates:
     - Tier 1: 100% (10/10) - no regressions
     - Tier 2: ≥50% (5/10) - success criterion
     - Overall: ≥75% (15/20)
   - Run full test suite: make test (expect <2 min)
   - Quality checks: make typecheck && make lint && make format
   - CI workflows all green
   - Run verification commands:
     - Check PLAN_REVISED.md structure
     - Verify 10 day headings present
     - Confirm 3 checkpoints documented

5. Extended benchmark validation (120-180 min, NEW with 80h capacity)
   - Longer benchmark runs on all models
   - Performance profiling and optimization
   - Multi-metric resilience testing
   - Synthetic edge case generation and testing
   - Comprehensive regression suite
   - Document all validation results

6. Sprint 12 Retrospective (90-120 min)
   - Create `docs/planning/EPIC_2/SPRINT_12/RETROSPECTIVE.md`
   - Sections:
     - What went well (e.g., prep tasks, measurement approach, 80h utilization)
     - What could improve (e.g., estimation accuracy)
     - Action items for Sprint 13
     - Velocity analysis (planned 65-72h vs actual)
     - Buffer utilization analysis
     - Checkpoint effectiveness review
   - Capacity utilization: 80h available, X used, Y% efficiency
   - Compare revised plan (65-72h) vs actual

7. Update PROJECT_PLAN.md (45-60 min)
   - Mark Sprint 12 complete
   - Update Epic 2 progress
   - Note Sprint 12 results and metrics
   - Identify Sprint 13 priorities

8. Create Sprint 12 PR (30 min)
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
- [ ] Extended validation results documented
- [ ] RETROSPECTIVE.md complete
- [ ] PROJECT_PLAN.md updated
- [ ] Sprint 12 PR created
- [ ] All documentation updated

**Decision Points:** None

**Success Criteria:**
- [ ] All required documentation updates complete
- [ ] KNOWN_UNKNOWNS.md: 27/27 unknowns addressed
- [ ] PREP_PLAN.md: Task 10 status/result/summary documented
- [ ] CHANGELOG.md: Sprint 12 entry complete
- [ ] All PRIMARY acceptance criteria met (see below)
- [ ] Zero critical bugs or regressions
- [ ] Documentation complete and accurate
- [ ] Sprint 12 ready for merge and Sprint 13 planning
- [ ] Verification commands run successfully

**Time Budget:** 10-14 hours

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
│  │        - Day 9: Scenario A (extended features)
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
│                             - Day 9: Implement LOW priority transformations (Scenario B)
│                             - Re-measure simplification with new patterns
│                             - Target: ≥20% with additional transformations
│                             - Fallback: Document limitation if still <15%
```

### Day 6 Checkpoint: Tier 2 Parse Rate

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

### Day 7 Checkpoint: PATH Licensing Decision

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

---

## Risk Register

### Risk 1: Benchmarking Reveals <20% Reduction

**Category:** Technical  
**Likelihood:** Low (Sprint 11 prototype: 39%)  
**Impact:** Medium (affects success criterion but transformations available)  
**Trigger:** Day 3 checkpoint shows <15% average reduction

**Mitigation:**
- LOW priority transformations ready (T5.2, T2.3, T5.4, T3.3: 6-8h)
- Task 2 research validated measurement methodology
- Task 7 prototype confirmed 0% counting error
- With 80h capacity: More time available for transformation implementation

**Contingency Plan:**
- Day 3: Document results, proceed to Tier 2
- Day 9: Implement 2-3 additional transformations (6-8h, Scenario B)
- Re-measure with new transformations
- If still <15%: Document actual reduction, adjust expectations for Sprint 13
- Extended validation time available Day 10

**Assignment:** Day 3 checkpoint decision

---

### Risk 2: Tier 2 Blockers Extremely Complex (>10h each)

**Category:** Technical  
**Likelihood:** Medium  
**Impact:** Medium (affects parse rate target, but extended time available)  
**Trigger:** Day 4 analysis reveals no blockers <6h

**Mitigation:**
- Task 3 pre-selected diverse models (6 blocker patterns, 15h total)
- Task 8 template enables rapid re-prioritization
- Alternate candidates available (18 evaluated)
- With 80h capacity: 18-22h allocated to Tier 2 (vs. original 7-9h)

**Contingency Plan:**
- Day 4: Re-run analysis on alternate candidates
- Select easier models if primary set too complex
- With extended time: Can tackle more complex blockers
- Acceptable outcome: 40-49% Tier 2 parse rate (still unlocks 4 models)
- Document complex blockers for Sprint 13
- Day 9: Additional blocker implementation if needed

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
- With 80h capacity: More time available for follow-up or self-hosted setup

**Contingency Plan:**
- Day 7: Document no-response scenario
- Send follow-up email with urgency note
- Proceed with IPOPT as primary solver
- If self-hosted runner needed: Evaluate feasibility (<4h acceptable with 80h capacity)
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
- With 80h capacity: More debug time available (3-4h vs. 1-2h)

**Contingency Plan:**
- Day 2: Debug failures (2-3h embedded buffer, extended from 1-2h)
- If >3h: Mark convert_rate as experimental, exclude from thresholds
- Document known issues in CI_REGRESSION_GUARDRAILS.md
- Full fix deferred to Sprint 13 if needed
- Extended validation on Day 10 to catch edge cases

**Assignment:** Day 2 baseline collection

---

### Risk 5: JSON Schema Evolution During Implementation

**Category:** Technical  
**Likelihood:** Low  
**Impact:** Low (schema versioned, more time for refinement)  
**Trigger:** Day 7 implementation reveals missing fields

**Mitigation:**
- Task 5 created 3 example JSON files (success, partial, failure)
- Schema v1.0.0 locked, changes require v1.1.0
- With 80h capacity: More time for schema refinement if needed

**Contingency Plan:**
- Day 7: Stick to schema v1.0.0 strictly
- Document discovered limitations in JSON_DIAGNOSTICS.md
- Plan v1.1.0 for Sprint 13 if needed
- Extended time allows for more thorough schema validation

**Assignment:** Day 7 JSON implementation

---

### Risk 6: Dashboard Complexity Exceeds Estimate

**Category:** Technical  
**Likelihood:** Medium (new feature, learning curve)  
**Impact:** Low (nice-to-have feature)  
**Trigger:** Day 7-8 dashboard implementation takes >6h

**Mitigation:**
- Chart.js widely used, good documentation
- Static HTML generation (no backend complexity)
- Task 5 JSON schema provides structured data
- With 80h capacity: More time allocated (6-7h vs. original deferral)

**Contingency Plan:**
- Day 7-8: Use simple templates/examples
- Simplify visualizations if needed (fewer chart types)
- Core functionality: Stage timing and simplification trends
- Advanced features: Defer to Sprint 13 if time runs out
- Fallback: Basic HTML table instead of charts

**Assignment:** Day 7-8 dashboard implementation

---

### Risk 7: Documentation Updates Take Longer Than Estimated

**Category:** Process  
**Likelihood:** Medium  
**Impact:** Low (extended time available)  
**Trigger:** Day 10 documentation updates exceed 3h

**Mitigation:**
- Clear requirements: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md
- Templates and examples from previous sprints
- With 80h capacity: 10-14h allocated to Day 10 (vs. 1-2h)

**Contingency Plan:**
- Day 10: Prioritize required updates first
- KNOWN_UNKNOWNS.md: 60-90 min (27 unknowns)
- PREP_PLAN.md: 60-90 min (Task 10 summary)
- CHANGELOG.md: 60-90 min (Sprint 12 entries)
- Extended validation: Use remaining time
- Retrospective: 90-120 min allocated

**Assignment:** Day 10 documentation

---

## Success Criteria

### PRIMARY (Must Achieve)

1. ✅ **Term Reduction Validated**
   - Metric: Average term reduction percentage across 10 Tier 1 models
   - Target: ≥20% on ≥50% models (5+ models)
   - Verification: baselines/simplification/baseline_sprint11.json + SIMPLIFICATION_BENCHMARKS.md
   - Fallback: 15-19% acceptable if transformations added on Day 9
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

7. ✅ **Documentation Updates Complete** (NEW with 80h capacity)
   - KNOWN_UNKNOWNS.md: Verification status for all 27 unknowns
   - PREP_PLAN.md: Task 10 status/result/summary documented
   - CHANGELOG.md: Sprint 12 entries complete
   - Verification: All documents updated and reviewed
   - **Checkpoint:** Day 10

### SECONDARY (Stretch Goals)

1. ⭐ **Tier 2 ≥60% Parse Rate**
   - Target: 6+ models (exceeds 50% goal)
   - Impact: Overall parse rate 80% (16/20)
   - Extended candidate analysis for Sprint 13

2. ⭐ **Term Reduction ≥30% Average**
   - Target: Exceeds 20% goal significantly
   - Validates transformation effectiveness
   - Per-transformation breakdown documented

3. ⭐ **Dashboard Integration Complete** (Pulled forward from deferred)
   - Deliverable: HTML dashboard with charts
   - Charts: Stage timing, simplification trends, transformation frequency
   - Hosted: GitHub Pages or CI artifacts
   - Effort: 6-7h (Day 7-8)

4. ⭐ **Performance Trending Implemented** (Pulled forward from deferred)
   - Deliverable: docs/performance/TRENDS.md
   - Data: Sprints 8-12 with parse rate, test time, simplification
   - Optional: Chart.js visualizations
   - Effort: 2-3h (Day 8)

5. ⭐ **Naming Convention Standardized**
   - Options: Consistent T-numbers or descriptive names
   - Mapping table: T-number ↔ descriptive name ↔ function
   - Documentation: CONTRIBUTING.md guidelines
   - Effort: 1-2h (Day 9)

6. ⭐ **LOW Priority Transformations** (If Day 3 checkpoint fails)
   - Patterns: T5.2 (Nested CSE), T2.3 (Common Denominator), T5.4 (CSE Aliasing)
   - Target: Achieve ≥20% reduction with additional patterns
   - Effort: 6-8h (Day 9 Scenario B)

7. ⭐ **CSE Temp Propagation** (If time permits)
   - Feature: Preserve cse_tmp_* variables in output
   - Flag: --cse-inline for backward compatibility
   - Effort: 2-3h (Day 9)

### Quality Gates (Continuous)

- ✅ All tests passing: Fast <30s, full <2 min
- ✅ No Tier 1 regressions (100% maintained)
- ✅ Quality checks: typecheck ✅, lint ✅, format ✅
- ✅ CI green: All workflows passing
- ✅ Documentation: All deliverables documented
- ✅ Verification commands successful

---

## Buffer Strategy

**Total Capacity:** 80 hours  
**Allocated Work:** 65-72 hours  
**Buffer:** 8-15 hours (10-19%)

### Allocation

1. **Embedded Buffer (2-3h):**
   - Days 1-9: ±10-20 min per day for unknowns
   - Absorbed in daily estimates (e.g., "3-4h" includes 15 min buffer)

2. **Day-Specific Buffers:**
   - Day 9: Flexible allocation based on checkpoint outcomes (12-14h)
   - Day 10: Extended validation and documentation (10-14h)
   - Total dedicated buffer: 22-28h (Days 9-10)

3. **Contingency Usage:**
   - Checkpoint failures: Day 9 allocated for recovery
   - Extended features: Day 9 allocated if all checkpoints pass
   - Documentation depth: Day 10 has ample time for thoroughness

### Usage Scenarios

**Scenario A: All checkpoints pass (15h available buffer)**
- Days 1-8: 2-3h absorbed in estimates
- Day 9: 12-14h for extended features (dashboard, trending, naming, catalog)
- Day 10: 10-14h for validation and documentation (comfortable pace)

**Scenario B: One checkpoint fails (10-12h available buffer)**
- Days 1-8: 3-4h absorbed for checkpoint recovery
- Day 9: 12-14h for recovery + partial extended features
- Day 10: 10-12h for validation and documentation

**Scenario C: Multiple checkpoints fail (8-10h available buffer)**
- Days 1-8: 5-6h absorbed for multiple recoveries
- Day 9: 12-14h for final recovery efforts
- Day 10: 10h focused validation and required documentation

**Validation:**
- Sprint 11 buffer utilization: 10% (1.6h of 16h scope)
- Sprint 12 allocation: 10-19% (8-15h of 80h capacity)
- Conservative estimate accounts for expanded scope

---

## Unknown Verification (All Complete)

### Unknown 7.1: Sprint 12 Scope Management

**Assumption:** Sprint 12 scope is realistic given Sprint 10-11 velocity.

**Verification Method:**
- Analyze Sprint 10-11 actual vs estimated effort
- Calculate realistic Sprint 12 capacity
- Define minimum viable Sprint 12 (PRIMARY criteria only)

**Findings:**

**Sprint 10 Velocity:**
- Estimated: 35-42h
- Actual: ~38h
- Accuracy: +2% (excellent estimation)

**Sprint 11 Velocity:**
- Estimated: 29-36h
- Actual: ~32h
- Accuracy: -3% (excellent estimation)
- Buffer utilization: 10%

**Sprint 12 Capacity Calculation:**
- Available: 80h (10 days × 8h/day)
- Original plan: 22-27h (28-34% utilization - UNDER-ALLOCATED)
- Revised plan: 65-72h (81-90% utilization - APPROPRIATE)
- Historical average: 35h per sprint
- Revised scope: ~2x historical average (acceptable with deferred items)

**Minimum Viable Sprint 12:**
- PRIMARY criteria only: 20-24h
- If scope reduction needed: Defer dashboard, trending, LOW transformations
- **Decision:** 65-72h scope is realistic with 80h capacity

**Risk:** LOW - Sprint 12 revised scope is 81-90% of available capacity

**Verification Status:** ✅ VERIFIED (resized to 80h capacity)

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
   - **Mitigation:** Professional email template, send Day 1
   - **80h Capacity Impact:** More time for self-hosted runner setup if needed (up to 4h)

2. **GAMSLib Model Availability (Component 5)**
   - Dependency: GAMSLib models downloadable
   - Timeline: Day 4 download
   - **Plan B:** Use cached models from Task 3
   - Risk: VERY LOW (models already downloaded in prep)
   - **Mitigation:** Models cached in repo during prep

3. **No Other External Dependencies**
   - All other components self-contained
   - No third-party API calls
   - No external data sources

**Front-Loading Strategy:**
- PATH email: Day 1 (maximizes 7-day response window)
- Tier 2 models: Pre-downloaded in Task 3
- All prep tasks: Completed before sprint start

**Contingency for PATH:**
- Day 7 checkpoint evaluates 4 scenarios
- All scenarios have clear action plans
- No scenario blocks sprint completion
- With 80h capacity: Can invest in self-hosted runner if needed

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
| 10. Sprint 12 Schedule | ✅ | 4-5h | PLAN.md + PLAN_REVISED.md |

**Total Prep Effort:** 21-28h estimated, actual tracked in PREP_PLAN.md

**Unknowns Verified:** 27/27 (100%) ✅

**Sprint 12 Ready:** All infrastructure, research, and planning complete

**Day 10 Update Required:** Mark Task 10 complete with actual vs estimated effort

---

## Changes from Original PLAN.md

### Scope Expansion (80h Capacity)

**Original Plan:** 22-27h (28-34% of 80h capacity)  
**Revised Plan:** 65-72h (81-90% of 80h capacity)  
**Added Scope:** ~40h

### Specific Changes

1. **Phase Rebalancing:**
   - Measurement & Validation: 7-10h → 9-12h (+2h validation depth)
   - Tier 2 Expansion: 7-9h → 18-22h (+11-13h, more models/blockers)
   - Polish & Integration: 4-6h → 16-20h (+12-14h, dashboard + trending)
   - Extended Features: 0h → 12-14h (NEW, Day 9)
   - Buffer & Validation: 3-4h → 10-14h (+7-10h documentation + depth)

2. **Features Pulled Forward from Deferred:**
   - Dashboard Integration (4-6h) - Days 7-8
   - Performance Trending (4-6h) - Day 8
   - Naming Convention Alignment (1-2h) - Day 9
   - Catalog Alignment (1-2h) - Day 9
   - CSE Temp Propagation (2-3h, conditional) - Day 9

3. **Expanded Tier 2 Work:**
   - More blockers: 6 total (vs. 3-4 in original)
   - Extended analysis: 5 additional candidates if ≥60%
   - More implementation time: 18-22h (vs. 7-9h)
   - Stretch goal: 60%+ parse rate

4. **Documentation Requirements Added:**
   - KNOWN_UNKNOWNS.md verification status (Day 10, 60-90 min)
   - PREP_PLAN.md Task 10 status/result/summary (Day 10, 60-90 min)
   - CHANGELOG.md Sprint 12 entries (Day 10, 60-90 min)
   - Verification commands documented and scheduled

5. **Extended Validation:**
   - Day 2: Synthetic model validation
   - Day 9: Comprehensive regression testing
   - Day 10: Extended benchmark runs, profiling, resilience checks
   - Total validation time: ~6-8h (vs. 2-3h)

6. **Buffer Allocation:**
   - Original: 3-4h (Days 9-10)
   - Revised: 8-15h (embedded + Days 9-10)
   - More conservative with expanded scope

### Maintained from Original

- All 3 checkpoints (Days 3, 6, 7) with decision trees
- All PRIMARY success criteria
- Risk register structure (7 risks)
- 10-day schedule format
- Prep task synthesis
- Unknown verification sections

---

## Next Steps

1. **Review & Approval:**
   - Team review of PLAN_REVISED.md
   - Validate 80h capacity allocation
   - Confirm expanded scope is appropriate
   - Verify checkpoint criteria remain valid

2. **Sprint 12 Start:**
   - Create sprint12-complete branch
   - Send PATH email (Day 1 first task)
   - Begin Day 1 tasks (SimplificationMetrics, count_terms)

3. **Daily Execution:**
   - Follow day-by-day schedule
   - Make checkpoint decisions based on actual data
   - Track actual vs estimated effort
   - Adjust Day 9-10 based on checkpoint outcomes

4. **Sprint 12 End:**
   - Day 10: Update KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md
   - Complete retrospective with 80h capacity analysis
   - Update PROJECT_PLAN.md
   - Create Sprint 12 → main PR
   - Begin Sprint 13 planning

---

**Document Status:** ✅ COMPLETE (REVISED for 80h capacity)  
**Ready for:** Sprint 12 Execution  
**Estimated Duration:** 10 working days (65-72h productive work + 8-15h buffer)  
**Success Probability:** HIGH (based on Sprint 10-11 velocity, comprehensive prep, appropriate scope)  
**Capacity Utilization:** 81-90% (industry best practice: 80-85%)
