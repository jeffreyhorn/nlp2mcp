# Sprint 12 Known Unknowns

**Sprint:** Sprint 12 - Measurement, Polish, and Tier 2 Expansion  
**Epic:** Epic 2 - Multi-Solver MCP Server  
**Created:** 2025-11-29  
**Status:** Active (Pre-Sprint)  
**Owner:** Sprint Team

---

## Executive Summary

This document catalogs **27 known unknowns** across **7 categories** that represent critical uncertainties for Sprint 12. These unknowns span term reduction measurement methodology (7 unknowns), multi-metric threshold implementation (4 unknowns), JSON diagnostic schema design (3 unknowns), PATH solver integration (4 unknowns), Tier 2 GAMSLib expansion (4 unknowns), CI workflow testing (3 unknowns), and cross-cutting process concerns (2 unknowns).

**Estimated Research Effort:** 21-28 hours (covered by prep tasks)  
**High Priority Unknowns:** 11 (41%)  
**Critical Path Unknowns:** 8 (30%)

Sprint 12 preparation tasks (Tasks 2-10 in PREP_PLAN.md) are explicitly designed to verify these unknowns before sprint execution begins. The Task-to-Unknown mapping (Appendix A) shows which prep tasks address which unknowns.

---

## How to Use This Document

**During Prep Phase:**
- Review unknowns before starting each prep task
- Update "Verification Results" as research completes
- Flag new unknowns discovered during research
- Adjust sprint plan if verification reveals high risks

**During Sprint:**
- Reference verified assumptions when making decisions
- Challenge assumptions if new evidence emerges
- Document actual outcomes vs. assumptions

**Each Unknown Includes:**
- **ID:** Unique identifier (Category.Number)
- **Priority:** HIGH/MEDIUM/LOW based on sprint impact
- **Assumption:** Current best guess (to be verified)
- **Research Questions:** Specific questions to answer
- **How to Verify:** Research approach
- **Risk if Wrong:** Impact of incorrect assumption
- **Estimated Research Time:** Hours needed
- **Owner:** Who verifies (default: Sprint Team)
- **Verification Results:** Findings (updated during prep)

---

## Summary Statistics

| Category | Count | High Priority | Research Hours |
|----------|-------|---------------|----------------|
| Term Reduction Benchmarking | 7 | 4 | 6-8h |
| Multi-Metric Thresholds | 4 | 3 | 4-5h |
| JSON Diagnostic Output | 3 | 1 | 2-3h |
| PATH Solver Integration | 4 | 2 | 3-4h |
| Tier 2 GAMSLib Expansion | 4 | 1 | 4-5h |
| CI Workflow Testing | 3 | 0 | 1-2h |
| Process & Documentation | 2 | 0 | 1-2h |
| **TOTAL** | **27** | **11** | **21-28h** |

---

## Category 1: Term Reduction Benchmarking

### 1.1 Baseline Metric Selection

**Priority:** HIGH  
**Assumption:** We will use (a) total term count, (b) expression depth, and (c) parse time as primary metrics for measuring term reduction effectiveness.

**Research Questions:**
- What metrics best capture "simplification" benefits?
- Are term count reductions correlated with parse time improvements?
- Do we need separate metrics for different expression types (equations vs. constraints)?
- Should we measure AST node counts or just surface-level term counts?

**How to Verify:**
- Analyze Sprint 11 transformation functions to identify what they optimize
- Review existing parse timing data to find correlations
- Survey academic literature on expression simplification metrics
- Prototype metric collection on 2-3 Tier 1 models

**Risk if Wrong:**
- We measure irrelevant metrics that don't reflect actual value (MEDIUM impact)
- Benchmarking results are misleading or unactionable (HIGH impact)
- Sprint 12 conclusions cannot inform future optimization work (MEDIUM impact)

**Estimated Research Time:** 2-3h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 2, 2025-11-29)

**Findings:**
- Selected TWO metrics: (1) Operation Count - AST node count via existing `_expression_size()`, (2) Term Count - additive components via custom `count_terms()`
- Operation count measures computational complexity, term count measures visual/conceptual complexity
- Both metrics are O(n) traversals with <0.1% overhead
- Dropped expression depth and parse time (not relevant to transformation effectiveness)

**Evidence:**
- Existing `SimplificationPipeline._expression_size()` already validated in Sprint 11
- Term counting aligns with user perception of simplification (fewer additive components)
- Both traverse AST once, fast implementation confirmed via code analysis

**Decision:**
- Use operation count (AST nodes) AND term count (additive components)
- Sprint 11 success criterion focuses on terms ("≥20% term reduction")
- Operations provide secondary metric for computational complexity

**Impact:**
- De-risks Sprint 12 benchmarking with proven, fast metrics
- Two complementary views of simplification effectiveness

---

### 1.2 Baseline Collection Approach

**Priority:** HIGH  
**Assumption:** We can collect "before transformation" baselines by temporarily disabling all 11 Sprint 11 transformations, running parser on Tier 1 models, and storing raw metrics in `tests/fixtures/baselines/`.

**Research Questions:**
- Can we disable transformations without breaking the parser?
- Do we need a feature flag or temporary code modification?
- How do we ensure baselines are reproducible across runs?
- Should baselines be per-model or aggregated across all 10 Tier 1 models?

**How to Verify:**
- Review transformation pipeline architecture in `nlp2mcp/parser/`
- Identify where transformations are applied (likely in parse_to_ast)
- Test disabling transformations on 1 model to verify parser still works
- Design baseline storage format (JSON or CSV)

**Risk if Wrong:**
- Cannot collect valid "before" baselines (CRITICAL impact - blocks entire benchmarking)
- Baselines include partial transformations, skewing results (HIGH impact)
- Baseline data format is incompatible with analysis tools (MEDIUM impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 9)*

---

### 1.3 Statistical Significance Thresholds

**Priority:** MEDIUM  
**Assumption:** We will consider term reductions of ≥10% to be "meaningful" and require statistical significance at p<0.05 for claiming improvements.

**Research Questions:**
- What constitutes a "meaningful" reduction in term count?
- Do we need statistical tests for a population of only 10 models?
- Should we use median or mean for aggregate metrics?
- Are there outlier models that need special handling?

**How to Verify:**
- Review historical parse data to understand natural variance
- Calculate coefficient of variation for existing metrics
- Research appropriate statistical tests for small sample sizes
- Prototype analysis with Sprint 11 timing data

**Risk if Wrong:**
- We claim "improvements" that are within noise margins (MEDIUM impact)
- We miss real improvements by setting thresholds too high (LOW impact)
- Results lack credibility for future decision-making (MEDIUM impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 2, 2025-11-29)

**Findings:**
- Threshold: ≥20% reduction on ≥50% of models (per Sprint 12 success criteria)
- NO statistical testing for sample of 10 models (sample too small, measurements deterministic)
- Success criterion is absolute (≥20% on ≥5 models), not statistical

**Evidence:**
- Sample size (n=10) too small for meaningful p-values
- AST traversal measurements are deterministic (zero variance)
- Sprint 11 prototype showed 39.2% average on synthetic examples, so 20% on real models is conservative

**Decision:**
- Use absolute threshold: ≥20% term reduction
- Apply to ≥50% of models (5 out of 10)
- No statistical tests (not applicable for deterministic measurements)

**Impact:**
- Clear, actionable success criteria
- No ambiguity from statistical interpretation

---

### 1.4 Granular vs. Aggregate Reporting

**Priority:** HIGH  
**Assumption:** We will report both per-transformation metrics (which functions contribute most to reduction) AND aggregate metrics (total impact of all transformations combined).

**Research Questions:**
- Can we measure transformations individually or only in combination?
- How do we handle transformation interdependencies (e.g., normalize_negation enables other simplifications)?
- Should we use an ablation study approach (remove one transformation at a time)?
- What is the right level of granularity for actionable insights?

**How to Verify:**
- Map transformation function call graph to identify dependencies
- Design measurement protocol (all-on vs. all-off vs. ablation)
- Estimate effort for each approach (ablation = 11x runs per model)
- Prototype granular measurement on 1 model

**Risk if Wrong:**
- Cannot identify which transformations deliver most value (HIGH impact)
- Measurement effort explodes with ablation testing (MEDIUM impact)
- Results don't inform prioritization for future transformations (MEDIUM impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 2, 2025-11-29)

**Findings:**
- Chosen approach: AGGREGATE reporting (all transformations on vs all off)
- Defer per-transformation ablation study to future sprints
- Collect baseline with all 11 transformations enabled, optionally with all disabled for comparison

**Evidence:**
- Sprint 12 goal is to validate Sprint 11 success criterion (aggregate reduction)
- Ablation study requires 11× overhead (11 runs per model × 10 models = 110 runs)
- Transformation interdependencies complicate attribution (some transformations enable others)
- Can add granular analysis in future sprint if needed for optimization

**Decision:**
- Aggregate metrics: avg reduction, models meeting threshold
- Implementation effort: 2-3h (Sprint 12 Day 1-2)
- Ablation study effort: 20-30h (deferred to future sprint if ROI justifies)

**Impact:**
- Focuses Sprint 12 on validation, not detailed analysis
- Leaves optimization decisions for future sprints based on aggregate results

---

### 1.5 Performance Overhead Measurement

**Priority:** MEDIUM  
**Assumption:** Metric collection will add <5% overhead to parse time and can be toggled via environment variable or CLI flag.

**Research Questions:**
- Where should we instrument code to collect metrics?
- Can we use existing timing infrastructure or need new tooling?
- How do we isolate metric collection overhead from actual parse time?
- Should metrics be collected in CI or only on-demand?

**How to Verify:**
- Review existing timing code in parser (likely uses `time.perf_counter()`)
- Test adding metric collection to 1 model and measure overhead
- Design toggling mechanism (env var vs. CLI flag vs. config file)
- Verify metric collection doesn't interfere with normal CI runs

**Risk if Wrong:**
- Metric collection slows down CI unacceptably (MEDIUM impact)
- Overhead measurement is confounded with actual parse changes (LOW impact)
- We cannot easily enable/disable collection for benchmarking (LOW impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 7)*

---

### 1.6 Baseline Drift Over Time

**Priority:** LOW  
**Assumption:** Baselines collected in Sprint 12 will remain valid for at least 2-3 sprints unless we intentionally modify transformation functions.

**Research Questions:**
- Should we re-collect baselines periodically?
- How do we detect when baselines are stale?
- Do we version baselines or always use latest?
- What triggers baseline recollection (code changes, model updates, etc.)?

**How to Verify:**
- Design baseline versioning scheme (git SHA, sprint number, timestamp)
- Identify baseline invalidation triggers (transformation code changes)
- Add documentation on when to recollect baselines
- Consider adding CI check to detect stale baselines

**Risk if Wrong:**
- Future benchmarking uses outdated baselines (LOW impact - can recollect)
- Baseline recollection becomes ad-hoc and inconsistent (LOW impact)
- We waste time recollecting baselines unnecessarily (LOW impact)

**Estimated Research Time:** 0.5h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 9)*

---

### 1.7 Actionability of Results

**Priority:** HIGH  
**Assumption:** Benchmarking results will clearly indicate whether to (a) invest in more transformations, (b) optimize existing ones, or (c) focus elsewhere.

**Research Questions:**
- What benchmark results would justify investing in 10+ more transformations?
- If results show minimal impact, what alternative approaches should we consider?
- How do we translate "X% term reduction" into user-facing value?
- Should we benchmark against external parsers for comparison?

**How to Verify:**
- Define decision criteria before running benchmarks (avoid confirmation bias)
- Draft "interpretation guide" for different result scenarios
- Consider end-user perspective (does term reduction matter to them?)
- Review project goals to ensure benchmarking aligns with Epic 2 objectives

**Risk if Wrong:**
- Benchmarking becomes "data for data's sake" without actionable insights (MEDIUM impact)
- Results don't inform Sprint 13+ roadmap decisions (HIGH impact)
- We optimize metrics that don't correlate with user value (MEDIUM impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 2, 2025-11-29)

**Findings:**
- Decision criteria defined for interpreting benchmark results
- Links metrics to user value: operation reduction → faster evaluation, term reduction → simpler code/debugging
- Provides Sprint 13+ roadmap guidance based on results

**Evidence:**
- Defined 4 result scenarios: ≥20% (SUCCESS), 15-19% (PARTIAL), 10-14% (INVESTIGATE), <10% (RETHINK)
- Each scenario has clear next action
- Sprint 13+ guidance: ≥30% = invest in more transformations, 20-30% = optimize existing, <20% = focus elsewhere

**Decision:**
- **≥20% on ≥50% models:** SUCCESS - Sprint 11 validated, continue with transformations
- **15-19%:** PARTIAL - Investigate low-performers, consider targeted optimizations
- **10-14%:** INVESTIGATE - Review measurement methodology, check for bugs  
- **<10%:** RETHINK - Transformations may not be effective, consider alternatives

**User Value Mapping:**
- Operation reduction → Faster evaluation (if expressions evaluated repeatedly)
- Term reduction → Simpler code generation, easier debugging
- Both → Smaller MCP model files

**Impact:**
- Clear decision framework prevents "data for data's sake"
- Actionable roadmap guidance for Sprint 13+

---

## Category 2: Multi-Metric Threshold Implementation

### 2.1 Metric Selection and Prioritization

**Priority:** HIGH  
**Assumption:** We will implement 3-4 metrics in CI (parse rate, parse time, diagnostic coverage, maybe term reduction) with independent thresholds for each.

**Research Questions:**
- Which metrics are most critical for regression detection?
- Should metrics be weighted or all treated equally?
- Do we need per-model thresholds or just aggregate?
- Can we start with 2 metrics and add more incrementally?

**How to Verify:**
- Review existing CI guardrails (currently only parse rate)
- Analyze historical failures to identify what metrics would have caught them
- Survey industry best practices for parser CI testing
- Draft initial metric set with rationale for each

**Risk if Wrong:**
- We implement too many metrics and get alert fatigue (MEDIUM impact)
- We miss critical regressions because we didn't test the right metrics (HIGH impact)
- Metrics conflict with each other (e.g., optimize speed at cost of coverage) (MEDIUM impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 4, 2025-11-29)

**Findings:**
- Selected 3 metrics: parse_rate, convert_rate, performance (avg_time_ms)
- All metrics treated equally (no weighting) but different threshold sensitivities
- Aggregate thresholds only (no per-model thresholds to avoid complexity)
- Incremental approach: Start with 3, can add diagnostic_coverage later

**Evidence:**
- Surveyed 3 CI tools (Lighthouse CI, pytest-benchmark, Codecov)
- All tools support multi-metric checking with independent thresholds
- Industry pattern: 3-5 metrics is sweet spot (avoids alert fatigue)
- Metrics already in JSON output (no new instrumentation needed)

**Decision:**
- **parse_rate:** Primary quality metric (correctness)
- **convert_rate:** Secondary quality metric (completeness)
- **performance:** Optimization metric (speed)
- Deferred: diagnostic_coverage (Sprint 13+), term_reduction (not in JSON yet)

**Impact:**
- Focuses on metrics with clear regression signals
- Balances correctness and performance concerns
- Avoids instrumentation complexity

---

### 2.2 Threshold Setting Methodology

**Priority:** HIGH  
**Assumption:** Thresholds will be set at "current performance + 5% tolerance" to allow minor variance while catching real regressions.

**Research Questions:**
- What is natural variance in parse time across CI runs?
- Should thresholds be absolute (e.g., <500ms) or relative (e.g., ±5%)?
- Do we need different tolerances for different metrics?
- How often should we recalibrate thresholds as code improves?

**How to Verify:**
- Analyze parse time variance from recent CI runs (Sprint 11 data)
- Test setting strict threshold (0% tolerance) to see false positive rate
- Research dynamic threshold approaches (e.g., rolling averages)
- Prototype threshold checking with existing parse data

**Risk if Wrong:**
- Thresholds are too strict, causing false positive CI failures (MEDIUM impact)
- Thresholds are too loose, allowing real regressions to slip through (HIGH impact)
- Threshold maintenance becomes burdensome (LOW impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 4, 2025-11-29)

**Findings:**
- **Relative thresholds** selected (% change from baseline) not absolute values
- Different tolerances per metric based on expected variance
- Dual-threshold approach: warn + fail per metric
- Recalibration strategy: Monitor Sprint 12-13, adjust if flaky

**Evidence:**
- Lighthouse CI, pytest-benchmark, Codecov all use relative thresholds
- Relative thresholds auto-adjust as baseline improves
- Performance metrics have higher variance than parse/convert rates

**Decision:**
- **parse_rate:** warn=5%, fail=10% (strict, correctness critical)
- **convert_rate:** warn=5%, fail=10% (strict, quality critical)
- **performance:** warn=20%, fail=50% (loose, accounts for system variance)
- **Methodology:**
  - For metrics where **higher is better** (e.g., `parse_rate`, `convert_rate`):
    `relative_change = (baseline - current) / baseline`
  - For metrics where **lower is better** (e.g., `avg_time_ms`):
    `relative_change = (current - baseline) / baseline`

**Recalibration Strategy:**
- Monitor false positive/negative rates in Sprint 12-13
- Tighten thresholds as parser stabilizes (Sprint 14+)
- Document adjustments in CHANGELOG.md

**Impact:**
- Self-adjusting thresholds work across changing baselines
- Looser perf thresholds reduce flaky CI failures
- Dual thresholds provide early warning before hard failure

---

### 2.3 CI Integration Architecture

**Priority:** HIGH  
**Assumption:** We can extend `test_tier1_models.py` to collect and validate multiple metrics without major CI workflow refactoring.

**Research Questions:**
- Should metrics be checked in existing test file or separate CI step?
- How do we report threshold violations (test failure vs. warning)?
- Can we use pytest fixtures to avoid duplicating model runs?
- Do we need to store historical metrics for trending?

**How to Verify:**
- Review current `test_tier1_models.py` architecture
- Identify extension points for adding metric collection
- Test adding a second metric (parse time) to existing test
- Design output format for multi-metric results

**Risk if Wrong:**
- CI implementation is fragile and breaks frequently (MEDIUM impact)
- Metric collection duplicates test runs, slowing CI (HIGH impact)
- Results are hard to interpret or debug when failures occur (MEDIUM impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 4, 2025-11-29)

**Findings:**
- **Extend check_parse_rate_regression.py** (not test_tier1_models.py)
- Separate CI step (not pytest integration)
- No model duplication - script reads existing JSON reports
- Historical trending deferred (use baseline from git)

**Evidence:**
- Reviewed check_parse_rate_regression.py - already has CLI args for multi-metric
- Script just needs implementation (args parsed but ignored currently)
- measure_parse_rate.py already generates JSON with all 3 metrics
- No pytest plugin needed (standalone script simpler)

**Decision:**
- **Architecture:** Extend check_parse_rate_regression.py
- **Integration:** Separate CI workflow step after measure_parse_rate.py
- **Reporting:** Markdown table output for PR comments
- **Storage:** No database needed, use git for baseline comparison

**Backward Compatibility:**
- Legacy mode: Use --threshold (single metric, parse_rate only)
- New mode: Use --parse-warn/--parse-fail etc. (multi-metric)
- Both modes coexist in same script

**Impact:**
- Minimal code changes (extend existing script)
- No pytest complexity
- Works with existing CI infrastructure

---

### 2.4 Backward Compatibility with Sprint 11

**Priority:** MEDIUM  
**Assumption:** Multi-metric implementation will not invalidate Sprint 11 regression guardrails or require rewriting existing tests.

**Research Questions:**
- Can new metrics coexist with existing parse rate checks?
- Do we need to migrate existing tests or just add new ones?
- Will multi-metric failures be distinguishable from parse failures?
- Should we version the CI configuration?

**How to Verify:**
- Review Sprint 11 CI implementation in detail
- Identify potential conflicts with new metric collection
- Test running both old and new checks side-by-side
- Plan migration path if refactoring is needed

**Risk if Wrong:**
- Sprint 11 gains are lost due to CI refactoring bugs (HIGH impact)
- We create two parallel CI systems that diverge over time (MEDIUM impact)
- Migration effort exceeds expected 3-4h budget (LOW impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 4, 2025-11-29)

**Findings:**
- **100% backward compatible** - no migration required
- Legacy and multi-metric modes coexist in same script
- Mode auto-detected based on CLI args provided
- No breaking changes to existing CI workflows

**Evidence:**
- Reviewed check_parse_rate_regression.py implementation
- Legacy mode uses --threshold arg (single metric, parse_rate only)
- Multi-metric mode uses --parse-warn/--parse-fail etc.
- Both modes can run simultaneously during transition

**Decision:**
- **Sprint 12 transition:** Add multi-metric args to CI, keep legacy as fallback
- **Sprint 13+:** Deprecate legacy mode (print warning)
- **Sprint 14+:** Remove legacy support (breaking change with advance notice)

**Migration Path:**
```bash
# Sprint 11 (still works in Sprint 12+)
--threshold 0.10

# Sprint 12+ (recommended)
--parse-warn 0.05 --parse-fail 0.10 --convert-warn 0.05 ...
```

**Impact:**
- Zero risk to Sprint 11 regression guardrails
- Gradual migration path (no forced upgrade)
- No CI downtime or test rewrites needed

---

## Category 3: JSON Diagnostic Output

### 3.1 Schema Design Complexity

**Priority:** HIGH  
**Assumption:** We can design a simple JSON schema that maps directly to current text diagnostic output without requiring major parser refactoring.

**Research Questions:**
- What is the current diagnostic data structure in memory?
- Can we serialize it directly to JSON or need transformation?
- Should JSON schema match text format 1:1 or be more structured?
- Do we need JSON Schema validation or just ad-hoc format?

**How to Verify:**
- Trace diagnostic generation code in `nlp2mcp/parser/diagnostics.py`
- Document current data structures (errors, warnings, metadata)
- Draft initial JSON schema using JSON Schema spec
- Test serializing 1-2 diagnostic outputs to JSON

**Risk if Wrong:**
- JSON implementation requires rewriting diagnostic subsystem (HIGH impact - scope creep)
- Schema is overly complex and hard to consume (MEDIUM impact)
- Schema is too simple and loses information from text output (MEDIUM impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 5, 2025-11-30)

**Findings:**
- **Direct serialization** with minor enhancements
- Current `to_json()` method in DiagnosticReport is 90% complete
- Only additions: schema_version, generated_at, summary fields
- No parser refactoring required

**Evidence:**
- Reviewed src/ir/diagnostics.py (lines 1-196)
- DiagnosticReport uses simple JSON-compatible types (str, float, bool, dict)
- StageMetrics.details is dict[str, Any] - already serializable
- to_json() method exists (lines 116-131) - just needs metadata

**Decision:**
- **Complexity:** LOW - Extend existing to_json() → to_json_v1()
- **Schema:** v1.0.0 with SemVer versioning
- **Fields:** schema_version, generated_at, model_name, total_duration_ms, overall_success, stages, summary
- **Implementation:** <4 hours for Sprint 12 Day 7

**Impact:**
- No major refactoring needed
- Low risk, straightforward implementation
- Full coverage of text diagnostic data

---

### 3.2 Output Format Selection

**Priority:** MEDIUM  
**Assumption:** We will output newline-delimited JSON (NDJSON) for streaming compatibility, with one JSON object per diagnostic event.

**Research Questions:**
- Should we use NDJSON, JSON array, or single JSON object?
- Do consumers need streaming output or can they wait for full parse?
- How do we handle incremental diagnostic updates during long parses?
- Should JSON be pretty-printed or minified?

**How to Verify:**
- Research common diagnostic output formats (LSP, compiler JSON, etc.)
- Consider use cases: CLI consumption, MCP integration, CI parsing
- Test JSON output size vs. text output for typical models
- Prototype NDJSON output with Python `json.dumps()` per event

**Risk if Wrong:**
- Output format is incompatible with downstream consumers (MEDIUM impact)
- JSON output is too verbose, slowing down CI (LOW impact)
- We need to support multiple formats, increasing complexity (LOW impact)

**Estimated Research Time:** 0.5-1h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 5, 2025-11-30)

**Findings:**
- **Single JSON object** per model (not NDJSON or JSON array)
- Simplest for CLI use case (one model per invocation)
- jq-friendly for CI scripts
- NDJSON deferred to future batch processing needs

**Evidence:**
- Researched common diagnostic formats (LSP, compiler JSON outputs)
- Analyzed use cases: CLI (single model), CI (artifact storage), trending
- Tested example JSON sizes: ~3-4KB indented, ~2KB compact
- NDJSON only beneficial for streaming multiple models

**Decision:**
- **Format:** Single JSON object
- **Rationale:** CLI processes one model at a time
- **Size:** Negligible (<5KB per report)
- **CI Integration:** Store as artifacts, parse with jq
- **Future:** Add NDJSON support if measure_parse_rate.py needs it

**Trade-offs:**
- ✅ Simple, standard JSON
- ✅ jq-friendly (standard tooling)
- ❌ Not optimized for streaming multiple models (acceptable for Sprint 12)

**Impact:**
- Clear decision enables straightforward implementation
- Standard JSON tooling (no special parsers)
- Easy CI integration with existing tools

---

### 3.3 Backward Compatibility

**Priority:** MEDIUM  
**Assumption:** Text diagnostic output will remain the default; JSON will be opt-in via `--format json` CLI flag without breaking existing users.

**Research Questions:**
- Can we add format flag without changing default behavior?
- Do existing tests assume text output?
- Should we test both formats in CI or just text?
- How do we deprecate text output in future if JSON becomes standard?

**How to Verify:**
- Review CLI argument parsing in main entry point
- Audit tests for hardcoded text output assumptions
- Add `--format` flag and verify default unchanged
- Document migration path for future text deprecation

**Risk if Wrong:**
- Breaking change disrupts existing integrations (HIGH impact)
- We maintain two output formats indefinitely (LOW impact - acceptable)
- Test coverage gaps emerge between formats (MEDIUM impact)

**Estimated Research Time:** 0.5h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 5, 2025-11-30)

**Findings:**
- **--format flag** with text default (100% backward compatible)
- JSON output opt-in via explicit flag
- No breaking changes to existing --diagnostics behavior
- Both formats tested in CI

**Evidence:**
- Reviewed CLI argument structure in existing codebase
- Existing --diagnostics flag outputs text to stderr
- Adding --format flag with default="text" preserves behavior
- Similar pattern used by industry tools (gcc -fdiagnostics-format, rustc --error-format)

**Decision:**
```bash
# Existing behavior (unchanged)
gams2mcp model.gms --diagnostics
# → Text output to stderr

# New behavior (opt-in)
gams2mcp model.gms --diagnostics --format json
# → JSON output to stderr
```

**Backward Compatibility Guarantees:**
- ✅ Existing scripts using --diagnostics unchanged
- ✅ Text remains default format
- ✅ No changes to DiagnosticReport.to_text() API
- ✅ JSON opt-in only (explicit flag required)

**Test Coverage:**
- Unit tests: Both text and JSON outputs
- Integration tests: CLI with --format flag
- Regression: Verify text output unchanged from Sprint 11

**Migration Path:**
- Sprint 12: Both formats supported
- Sprint 13+: JSON becomes recommended (docs)
- Sprint 15+: Consider JSON as default (with deprecation warning for text)

**Impact:**
- Zero risk to existing users
- Smooth migration path to JSON
- Both formats maintainable long-term

---

## Category 4: PATH Solver Integration

### 4.1 License Compatibility with MIT

**Priority:** HIGH  
**Assumption:** PATH solver's license is compatible with nlp2mcp's MIT license for CI testing purposes (not redistribution).

**Research Questions:**
- What is PATH's current license (as of 2025)?
- Does license allow automated testing in CI?
- Can we download PATH binaries or must we build from source?
- Are there usage restrictions (academic only, commercial restrictions)?

**How to Verify:**
- Fetch PATH documentation from official sources
- Review LICENSE file in PATH distribution
- Consult UW-Madison legal/licensing page
- Draft email to PATH maintainers for clarification if needed

**Risk if Wrong:**
- License prohibits CI use, requiring alternative approach (HIGH impact)
- We violate license terms unknowingly (CRITICAL impact - legal risk)
- Restrictions limit future commercial use of nlp2mcp (MEDIUM impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 6)*

---

### 4.2 CI Installation Method

**Priority:** HIGH  
**Assumption:** We can install PATH solver in GitHub Actions CI using apt-get (Ubuntu) or conda, without requiring manual binary downloads.

**Research Questions:**
- Is PATH available in standard package repositories?
- Do we need to use GAMS-provided PATH or standalone distribution?
- Can we cache PATH installation across CI runs?
- What is installation time impact on CI duration?

**How to Verify:**
- Search for PATH in apt repositories (Ubuntu 22.04)
- Check conda-forge for PATH packages
- Research GAMS PATH distribution options
- Test installing PATH in local Docker container (ubuntu:22.04)

**Risk if Wrong:**
- No automated installation method exists (MEDIUM impact - requires manual setup)
- Installation takes >5 minutes, slowing CI significantly (LOW impact)
- Different CI runners have different PATH versions (MEDIUM impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 6)*

---

### 4.3 PATH Model Availability

**Priority:** MEDIUM  
**Assumption:** GAMSLib contains 5-10 MCP models that use PATH solver and are suitable for CI testing.

**Research Questions:**
- How many GAMSLib models use PATH vs. other MCP solvers?
- Are PATH models representative of real-world usage?
- Do PATH models require GAMS license or work standalone?
- Should we test PATH in Sprint 12 or defer to Sprint 13?

**How to Verify:**
- Survey GAMSLib Tier 1 and Tier 2 models for solver tags
- Check which models are marked as "MCP" or "complementarity"
- Review PATH documentation for model format requirements
- Assess whether PATH testing fits Sprint 12 scope

**Risk if Wrong:**
- No suitable PATH models exist in GAMSLib (MEDIUM impact - need external models)
- PATH testing scope exceeds Sprint 12 budget (HIGH impact)
- PATH models fail for reasons unrelated to parser (LOW impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 6)*

---

### 4.4 Integration Scope (Defer vs. Implement)

**Priority:** MEDIUM  
**Assumption:** Sprint 12 will complete PATH licensing research and draft CI integration plan, but actual implementation (CI workflow changes, PATH installation) will be deferred to Sprint 13 if effort exceeds 3-5h.

**Research Questions:**
- What is minimum viable PATH integration for Sprint 12?
- Can we defer implementation if licensing/installation is complex?
- Should PATH be a separate CI job or integrated into existing tests?
- What is effort estimate for full PATH integration?

**How to Verify:**
- Complete unknowns 4.1-4.3 first to assess complexity
- Draft PATH integration plan with effort breakdown
- Identify decision point for defer vs. implement
- Document deferral criteria in sprint plan

**Risk if Wrong:**
- We over-commit to PATH integration and delay other Sprint 12 work (MEDIUM impact)
- We under-invest and PATH remains perpetually deferred (LOW impact)
- Licensing issues discovered too late to pivot (HIGH impact)

**Estimated Research Time:** 0.5h (planning only)  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 6)*

---

## Category 5: Tier 2 GAMSLib Expansion

### 5.1 Model Selection Criteria

**Priority:** MEDIUM  
**Assumption:** We will select 10 Tier 2 models based on (a) diversity of features used, (b) increasing complexity, and (c) known parse challenges from prior analysis.

**Research Questions:**
- What features are under-represented in current Tier 1 (10 models)?
- Should we prioritize models that use CSE, PATH, or other advanced features?
- Do we select models randomly or target specific complexity levels?
- Should we include models expected to fail to test error handling?

**How to Verify:**
- Analyze Tier 1 feature coverage (which GAMS constructs are tested)
- Survey Tier 2 candidates (GAMSLib models 11-50) for feature diversity
- Review prior parse attempts to identify known blockers
- Draft selection criteria and rank top 15 candidates

**Risk if Wrong:**
- Tier 2 models are too similar to Tier 1, not expanding coverage (MEDIUM impact)
- Models are too complex, all fail and provide no learning (MEDIUM impact)
- Selection is arbitrary and not defensible (LOW impact)

**Estimated Research Time:** 2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 3, 2025-11-29)

**Findings:**
- Selected 10 Tier 2 models using diversity heuristic
- Criteria: (a) blocker diversity (6 unique patterns), (b) effort budget (15h total, 4h high-priority), (c) common GAMS patterns, (d) model size 40-180 lines
- Feature coverage: syntax extensions, data structures, documentation features, symbol table, model organization
- Models NOT in Tier 1, all NLP/DNLP type (no MINLP)

**Evidence:**
- Analyzed 18 candidate models from GAMSLib catalog
- Parse success rate: 5.6% (1/18 - house.gms parses)
- Blocker distribution: 8 syntax errors, 4 table wildcards, 2 preprocessor, 1 loop, 1 alias, 1 file I/O
- Created TIER_2_MODEL_SELECTION.md with full analysis

**Decision:**
- **Selected 10 models:** chenery, jbearing, fct, chem, water, gastrans, process, least, like, bearing
- **6 blocker patterns:** special_chars_in_identifiers (1.5h), multiple_alias_declaration (1.5h), predefined_constants (1h), inline_descriptions (4h), model_inline_descriptions (2h), table_wildcard_domain (5h)
- **Total effort:** 15h (4h high-priority, 6h medium-priority, 5h stretch goal)

**Impact:**
- Clear implementation roadmap for Sprint 12 Days 4-8
- Blocker diversity ensures broad parser improvement
- Effort budget fits within Sprint 12 timeline

---

### 5.2 Target Parse Rate Feasibility

**Priority:** MEDIUM  
**Assumption:** We can achieve ≥50% parse rate (5/10 models) on Tier 2 without implementing new transformations, relying on Sprint 11 parser improvements.

**Research Questions:**
- What is current parse rate on Tier 2 candidates (before Sprint 12)?
- What are common failure modes in Tier 2 models?
- Can we fix failures with minor bug fixes or need major features?
- Should we adjust target to 40% or 60% based on pilot results?

**How to Verify:**
- Run current parser (Sprint 11 code) on 10 Tier 2 candidates
- Categorize failures (syntax errors, unsupported features, bugs, etc.)
- Estimate effort to fix each failure category
- Assess whether 50% is achievable within Sprint 12 budget

**Risk if Wrong:**
- Target is too ambitious, we fail to meet 50% (MEDIUM impact - morale)
- Target is too conservative, we hit 80%+ and under-invested (LOW impact)
- Failures require features beyond Sprint 12 scope (HIGH impact)

**Estimated Research Time:** 1-2h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 3, 2025-11-29)

**Findings:**
- Current baseline: 5.6% parse rate on Tier 2 candidates (1/18 models)
- Target: ≥50% parse rate (5/10 models) is FEASIBLE
- Failure modes categorized: syntax errors (44%), table wildcards (22%), preprocessor (11%), other (23%)
- All selected blockers required to reach 50% parse rate are fixable within Sprint 12 budget (10h total: simple + medium)

**Evidence:**
- Ran parse analysis on 18 candidates, documented all failure modes
- Complexity estimates: Simple (3 blockers, 4h), Medium (2 blockers, 6h)
- Conservative estimate: 50% parse rate (5/10 models = all simple blockers + all medium blockers)
- Optimistic estimate: 60-70% parse rate (6-7/10 models = simple + medium + partial table wildcard)

**Decision:**
- Target: **50% ± 10% parse rate** (5-6/10 models)
- Success criterion: ≥50% aligns with Sprint 12 Component 5 goal
- Effort allocation: Days 4-6 for simple/medium blockers, Days 7-8 for stretch goals
- No major features required (Sprint 11 parser foundation sufficient)

**Impact:**
- Realistic target with built-in margin
- Clear success criteria for Sprint 12
- Provides actionable roadmap for implementation

---

### 5.3 Blocker Documentation Process

**Priority:** LOW  
**Assumption:** For each Tier 2 failure, we will create a structured blocker report (template-based) identifying root cause, required fix, and estimated effort.

**Research Questions:**
- What information is most useful in a blocker report?
- Should blockers be GitHub issues, markdown files, or inline comments?
- How do we track blockers across sprints (lifecycle, ownership)?
- Should we triage blockers by priority or just document all equally?

**How to Verify:**
- Review existing issue templates for relevance
- Draft blocker report template with required fields
- Test creating 2-3 blocker reports for known Tier 1 issues
- Decide on storage location (GitHub issues vs. `docs/blockers/`)

**Risk if Wrong:**
- Blocker reports are inconsistent and hard to use (LOW impact)
- We spend too much time documenting vs. fixing (LOW impact)
- Blockers are forgotten and not addressed in future sprints (MEDIUM impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 8)*

---

### 5.4 Regression Risk from Tier 2 Fixes

**Priority:** MEDIUM  
**Assumption:** Bug fixes for Tier 2 models will not regress Tier 1 parse rate, as validated by existing CI guardrails.

**Research Questions:**
- How do we ensure Tier 2 fixes don't break Tier 1 models?
- Should we run Tier 1 tests before each Tier 2 fix?
- Do we need additional regression tests for edge cases?
- What is rollback plan if regression occurs?

**How to Verify:**
- Verify CI runs Tier 1 tests on all PRs (check GitHub Actions config)
- Test introducing a intentional regression to confirm CI catches it
- Review PR checklist to ensure Tier 1 validation is mandatory
- Document rollback procedure in CONTRIBUTING.md

**Risk if Wrong:**
- Tier 2 fixes silently break Tier 1 models (HIGH impact - violates guarantees)
- We discover regressions late in sprint, requiring rework (MEDIUM impact)
- Fear of regressions slows down Tier 2 development (LOW impact)

**Estimated Research Time:** 0.5-1h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 3, 2025-11-29)

**Findings:**
- Existing CI runs Tier 1 tests on all PRs via `.github/workflows/ci.yml`
- Tier 1 regression guardrails are in place (10/10 models must parse)
- Sprint 12 will add Tier 2 test suite with 10 new models
- Rollback procedure: revert PR if regression detected

**Evidence:**
- Reviewed `.github/workflows/` directory (CI configuration exists)
- Confirmed `tests/integration/test_tier1_models.py` runs on every PR
- PR template includes regression testing checklist
- Git history shows revert capability

**Decision:**
- Tier 2 fixes WILL NOT regress Tier 1 (validated by CI)
- Add Tier 2 test suite in parallel to Tier 1 (independent thresholds)
- Mandatory: All PRs must pass both Tier 1 (100%) and Tier 2 (≥current) tests
- Rollback: Use `git revert <commit>` if regression slips through

**Impact:**
- Low regression risk (automated CI validation)
- Clear rollback procedure
- Tier 1 guarantees maintained through Sprint 12

---

## Category 6: CI Workflow Testing Checklist

### 6.1 Workflow Coverage Identification

**Priority:** LOW  
**Assumption:** Current CI has 3-4 critical workflows (tests, type checking, linting, maybe dependency checks) that should be on PR checklist.

**Research Questions:**
- What GitHub Actions workflows are currently defined?
- Which workflows are mandatory vs. optional?
- Are there manual checks that should be automated?
- Should checklist include documentation updates, changelog entries?

**How to Verify:**
- List all workflows in `.github/workflows/`
- Review recent PR merge history to identify manual checks
- Survey common PR review comments for recurring issues
- Draft checklist with 5-10 items

**Risk if Wrong:**
- Checklist is incomplete and misses critical checks (MEDIUM impact)
- Checklist is too long and becomes ignored (LOW impact)
- Automated checks are duplicated in checklist (LOW impact)

**Estimated Research Time:** 0.5h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 3, 2025-11-29)

**Findings:**
- Current CI has 5 workflows in `.github/workflows/`: ci.yml (main), docs, release, dependabot, codeql
- Mandatory workflows: ci.yml (tests, type checking, linting)
- Optional workflows: docs (build check), codeql (security)
- Manual checks: changelog updates, documentation updates

**Evidence:**
- Listed all workflow files via `ls .github/workflows/`
- Main CI runs: pytest, mypy, ruff (lint), black (format)
- Tier 1 tests are part of main CI (mandatory)
- Coverage reports generated but not blocking

**Decision:**
- **CI checklist items (mandatory):**
  1. All tests pass (pytest)
  2. Type checking passes (mypy)
  3. Linting passes (ruff)
  4. Formatting passes (black)
  5. Tier 1 regression tests pass (10/10 models)
  6. Tier 2 regression tests pass (≥current rate)
- **Manual checklist items:**
  7. CHANGELOG.md updated
  8. Documentation updated (if API changes)

**Impact:**
- Clear CI coverage definition
- 6 automated checks + 2 manual checks
- Foundation for PR checklist template

---

### 6.2 Checklist Enforcement Mechanism

**Priority:** LOW  
**Assumption:** We will use GitHub PR template with checkboxes; enforcement is social (reviewer responsibility) not automated.

**Research Questions:**
- Should checklist be in PR template or CONTRIBUTING.md?
- Do we need CODEOWNERS or branch protection rules?
- Can we auto-check some items with GitHub Actions?
- What happens if PR author skips checklist items?

**How to Verify:**
- Review existing PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
- Research GitHub PR checklist best practices
- Test creating PR with checklist to verify UX
- Decide on enforcement level (suggestion vs. requirement)

**Risk if Wrong:**
- Checklist is ignored by contributors (MEDIUM impact - defeats purpose)
- Over-enforcement creates friction and slows development (LOW impact)
- Checklist becomes outdated as CI evolves (LOW impact)

**Estimated Research Time:** 0.5h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 3, 2025-11-29)

**Findings:**
- Existing PR template at `.github/PULL_REQUEST_TEMPLATE.md` has basic checklist
- Enforcement is SOCIAL (reviewer responsibility), not automated
- GitHub branch protection can enforce status checks but not template checkboxes
- Best practice: Combine template checklist + automated CI checks

**Evidence:**
- Reviewed PR template structure
- Researched GitHub branch protection options (status checks only)
- Confirmed no automated checkbox validation available in GitHub
- Current workflow: reviewers check template before approval

**Decision:**
- **Enforcement level: SOCIAL with AUTOMATED backup**
  - PR template includes 8-item checklist (see Unknown 6.1)
  - Automated checks (items 1-6) enforced via GitHub status checks
  - Manual checks (items 7-8) enforced via reviewer diligence
- **Branch protection:** Require ci.yml workflow to pass before merge
- **Social contract:** Contributors expected to complete checklist before requesting review

**Impact:**
- Balanced approach (not overly rigid)
- Critical checks automated, documentation checks manual
- Clear expectations for contributors

---

### 6.3 Integration with Multi-Metric Thresholds

**Priority:** LOW  
**Assumption:** PR checklist will include verifying multi-metric thresholds pass, with link to CI results for evidence.

**Research Questions:**
- How do contributors verify thresholds passed (CI logs, summary comment)?
- Should checklist link to specific CI job output?
- Do we need a separate checklist item for each metric?
- What if thresholds fail but PR author has justification?

**How to Verify:**
- Review how CI results are surfaced in GitHub PR UI
- Test whether threshold violations are clearly visible
- Design checklist item wording for clarity
- Document override process for intentional threshold changes

**Risk if Wrong:**
- Contributors don't know how to verify thresholds (LOW impact)
- Checklist item is vague and not actionable (LOW impact)
- Legitimate threshold changes are blocked by checklist (MEDIUM impact)

**Estimated Research Time:** 0.5h  
**Owner:** Sprint Team  
**Verification Results:** ✅ VERIFIED (Task 4, 2025-11-29)

**Findings:**
- Single checklist item covers all metrics (not per-metric items)
- CI status visible in GitHub PR checks UI
- PR comment table provides detailed status
- Override process: justification + maintainer approval + label

**Evidence:**
- GitHub Actions shows check results in PR UI (✓/✗ status)
- PR comment format designed with Markdown table for clarity
- Industry pattern: Single "regression check" item with details link

**Decision:**

**PR Checklist Item:**
```markdown
- [ ] **Multi-metric regression check passes** (see CI status below)
  - Parse Rate: Must not regress >10% (warn at 5%)
  - Convert Rate: Must not regress >10% (warn at 5%)
  - Performance: Must not regress >50% (warn at 20%)
```

**Override Process:**
1. Review CI output for specific metric failures
2. Justify regression in PR description (e.g., "Expected 15% perf regression due to AST refactor")
3. Request explicit approval from maintainer
4. Add `override: metrics` label to PR
5. Document regression in CHANGELOG.md

**Link to CI Output:**
- GitHub Actions check result (click "Details")
- PR comment shows detailed multi-metric table
- Link to raw JSON report in comment

**Impact:**
- Clear expectations for contributors
- Flexible override process for intentional changes
- Centralized verification (single checklist item)

---

## Category 7: Process & Documentation

### 7.1 Sprint 12 Scope Management

**Priority:** MEDIUM  
**Assumption:** Sprint 12 will defer LOW-priority items if HIGH+MEDIUM tasks exceed 28h, maintaining focus on measurement and polish over feature expansion.

**Research Questions:**
- What is our velocity based on Sprint 10-11 actuals?
- How much contingency time should we reserve for unknowns?
- What is minimum viable Sprint 12 (must-have vs. nice-to-have)?
- How do we decide mid-sprint to defer items?

**How to Verify:**
- Review Sprint 10-11 actual hours vs. planned (from RETROSPECTIVE.md)
- Calculate realistic capacity for Sprint 12 (accounting for holidays, etc.)
- Define "Sprint 12 success criteria" independent of scope
- Document deferral decision criteria in sprint plan

**Risk if Wrong:**
- We over-commit and deliver nothing completely (HIGH impact)
- We under-commit and miss opportunities for impact (LOW impact)
- Scope creep occurs without conscious deferral decisions (MEDIUM impact)

**Estimated Research Time:** 1h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 10)*

---

### 7.2 Dependency on External Research

**Priority:** LOW  
**Assumption:** Sprint 12 prep tasks will resolve all critical unknowns; no external dependencies (licensing approvals, third-party library releases, etc.) will block sprint execution.

**Research Questions:**
- Does PATH licensing require email correspondence with delays?
- Do any tasks depend on external library updates?
- Are there knowledge gaps requiring expert consultation?
- What is plan B if external dependencies don't resolve in time?

**How to Verify:**
- Review all unknowns for external dependencies
- Identify blockers that cannot be resolved by sprint team alone
- Draft contingency plans for each external dependency
- Front-load external research in prep phase (complete by Task 6)

**Risk if Wrong:**
- Sprint starts with unresolved blockers (HIGH impact - delays)
- We discover external dependencies mid-sprint (MEDIUM impact - rework)
- Contingency plans are inadequate and sprint fails (HIGH impact)

**Estimated Research Time:** 0.5h  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task 10)*

---

## Template for Adding New Unknowns

When research during prep tasks uncovers new unknowns, add them using this template:

```markdown
### X.Y [Unknown Title]

**Priority:** HIGH/MEDIUM/LOW  
**Assumption:** [Current best guess about how this will work]

**Research Questions:**
- [Question 1]
- [Question 2]
- [Question 3]

**How to Verify:**
- [Research approach step 1]
- [Research approach step 2]
- [Research approach step 3]

**Risk if Wrong:**
- [Impact 1] (severity)
- [Impact 2] (severity)
- [Impact 3] (severity)

**Estimated Research Time:** Xh  
**Owner:** Sprint Team  
**Verification Results:** *(To be completed during Task N)*
```

Update the Summary Statistics table and Task-to-Unknown mapping when adding unknowns.

---

## Appendix A: Task-to-Unknown Mapping

This table shows which Sprint 12 prep tasks verify which known unknowns. Each task is designed to answer specific research questions before sprint execution begins.

| Prep Task | Unknowns Verified | Research Hours | Notes |
|-----------|-------------------|----------------|-------|
| **Task 1: Create Known Unknowns List** | *(All unknowns cataloged)* | 2-3h | Meta-task; creates this document |
| **Task 2: Research Term Reduction Measurement** | 1.1, 1.3, 1.4, 1.7 | 3-4h | Metric selection, statistical methods, granularity, actionability |
| **Task 3: Survey Tier 2 GAMSLib Models** | 5.1, 5.2, 5.4, 6.1, 6.2 | 2-3h | Model selection, feasibility, regression risk, CI checklist |
| **Task 4: Research Multi-Metric Thresholds** | 2.1, 2.2, 2.3, 2.4, 6.3 | 2h | Metric selection, thresholds, CI integration, compatibility |
| **Task 5: Design JSON Diagnostics Schema** | 3.1, 3.2, 3.3 | 1-2h | Schema complexity, output format, backward compatibility |
| **Task 6: Draft PATH Licensing Email** | 4.1, 4.2, 4.3, 4.4 | 1h | License research, installation, model availability, scope |
| **Task 7: Prototype Simplification Metrics** | 1.5, 1.2 (partial) | 3-4h | Performance overhead, baseline collection (prototype) |
| **Task 8: Create Tier 2 Blocker Template** | 5.3 | 1-2h | Blocker documentation process |
| **Task 9: Set Up Baseline Storage** | 1.2, 1.6 | 1-2h | Baseline collection, drift over time |
| **Task 10: Plan Sprint 12 Detailed Schedule** | 7.1, 7.2 | 4-5h | Scope management, external dependencies |

**Coverage Summary:**
- **27 unknowns** mapped to **9 prep tasks** (Tasks 2-10)
- **Task 1** is meta-task creating this document
- **All HIGH-priority unknowns** (11 total) verified by critical path tasks (2, 4, 5, 6)
- **External dependency unknowns** (4.1-4.4) front-loaded in Task 6 to allow pivot time
- **Measurement unknowns** (1.1-1.7) split across Tasks 2, 7, 9 for incremental validation

**Unknown-to-Task Reverse Mapping:**

| Category | Unknowns | Primary Task | Secondary Tasks |
|----------|----------|--------------|-----------------|
| 1. Term Reduction | 1.1, 1.3, 1.4, 1.7 | Task 2 | Task 7 (1.5), Task 9 (1.2, 1.6) |
| 2. Multi-Metric | 2.1, 2.2, 2.3, 2.4 | Task 4 | Task 10 (integration check) |
| 3. JSON Diagnostics | 3.1, 3.2, 3.3 | Task 5 | None |
| 4. PATH Integration | 4.1, 4.2, 4.3, 4.4 | Task 6 | None |
| 5. Tier 2 Expansion | 5.1, 5.2, 5.3, 5.4 | Task 3 | Task 8 (5.3) |
| 6. CI Checklist | 6.1, 6.2, 6.3 | Task 3 | Task 4 (6.3) |
| 7. Process | 7.1, 7.2 | Task 10 | None |

**Verification Workflow:**
1. Before starting each prep task, review relevant unknowns from this document
2. During task execution, actively research and answer the listed questions
3. After task completion, update "Verification Results" section with findings
4. Flag any new unknowns discovered and add them to this document
5. If verification reveals HIGH risk, escalate to sprint planning (Task 10) for mitigation

---

**Document Status:** ✅ COMPLETE (Task 1 deliverable)  
**Last Updated:** 2025-11-29  
**Next Review:** Before Task 10 (sprint planning) to validate all unknowns resolved
