# Sprint 11: Items Deferred to Sprint 12

**Document Purpose:** Comprehensive list of features, improvements, and technical debt items deferred from Sprint 11 to Sprint 12, with sufficient detail for sprint planning.

**Sprint 11 Status:** ✅ COMPLETE - All primary goals achieved (100% Tier 1 parse rate, 11 transformations, 3 CSE features, CI guardrails, diagnostics)

**Sprint 12 Theme Proposal:** "Measurement, Polish, and Tier 2 Expansion"

---

## Overview

Sprint 11 successfully delivered all primary features but deferred 12 items to Sprint 12 for various reasons:
- **Technical Debt:** Half-implemented features (multi-metric thresholds)
- **Measurement Infrastructure:** Quantitative validation needed (term reduction benchmarking)
- **Nice-to-Have Features:** JSON output, dashboards, additional transformations
- **Process Improvements:** Naming conventions, CI checklists
- **Expansion:** Tier 2 model coverage
- **Blocked Items:** PATH solver (licensing unclear)

**Total Deferred Effort:** 35-53 hours (24-35h excluding LOW priority)

---

## HIGH Priority Items (Critical for Sprint 12)

### 1. Term Reduction Benchmarking and Measurement

**Category:** Aggressive Simplification - Measurement Infrastructure  
**Effort:** 4-6 hours  
**Priority:** HIGH  
**Status:** Not started (deferred from Sprint 11)

#### Problem Statement
Sprint 11 implemented 11 transformation functions for aggressive simplification but did not implement quantitative measurement. Success criterion "≥20% term reduction on ≥50% of models" remains unvalidated. Need benchmarking infrastructure to:
1. Measure actual term reduction per model
2. Identify which transformations provide most value
3. Detect simplification regressions in CI

#### Scope
- **Metrics to Track:**
  - Operation count before/after simplification (add, mul, div, exp, log, etc.)
  - Term count reduction percentage
  - Transformations applied (which of 11 functions triggered)
  - Expression depth before/after
  - Execution time per transformation pass

- **Implementation:**
  - Extend `scripts/measure_parse_rate.py` with `--measure-simplification` flag
  - Add `SimplificationMetrics` class to track reduction stats
  - Instrument simplification pipeline to record transformation applications
  - Generate per-model and aggregate reports

- **Baseline Storage:**
  - Create `baselines/simplification/baseline_sprint11.json` with Sprint 11 metrics
  - Track in git (small files, infrequent updates)
  - Format: `{"model": "rbrock", "ops_before": 150, "ops_after": 95, "reduction_pct": 36.7, ...}`

- **CI Integration:**
  - Add simplification regression check to `gamslib-regression.yml`
  - Threshold: Fail if average reduction drops >10% from baseline
  - Warning if any model regresses >20%

#### Deliverables
1. `scripts/measure_simplification.py` - Benchmarking script
2. `baselines/simplification/baseline_sprint11.json` - Sprint 11 baseline
3. `docs/SIMPLIFICATION_BENCHMARKS.md` - Results analysis
4. CI workflow integration with regression detection
5. Report showing which transformations are most/least effective

#### Acceptance Criteria
- ✅ Quantitative reduction metrics for all 10 Tier 1 models
- ✅ Validate ≥20% average reduction (or adjust transformations if not met)
- ✅ Baseline stored and tracked in git
- ✅ CI fails if simplification regresses >10%
- ✅ Report identifies top 3 most effective transformations per model

#### Dependencies
- None (can start immediately)

#### Risks
- May reveal that current transformations don't meet 20% target → Need LOW priority transformations (Item #3)
- Measurement overhead might slow CI → Use sampling or nightly runs

---

### 2. Multi-Metric Threshold Implementation (Complete)

**Category:** CI Regression Guardrails - Infrastructure  
**Effort:** 3-4 hours  
**Priority:** HIGH  
**Status:** Technical debt (CLI arguments accepted but not implemented)

#### Problem Statement
Sprint 11 Day 8 added CLI arguments for multi-metric thresholds but didn't implement the backend logic:
- `--parse-rate-warn=N`, `--parse-rate-fail=N`
- `--convert-rate-warn=N`, `--convert-rate-fail=N`
- `--performance-warn=N`, `--performance-fail=N`

Currently these arguments are accepted but don't affect behavior. This is confusing and creates technical debt.

#### Scope
- **Complete Implementation:**
  - Implement threshold checking in `scripts/check_parse_rate_regression.py`
  - Add `read_metrics()` function to parse baseline JSON (parse_rate, convert_rate, performance)
  - Implement comparison logic with warn/fail exit codes
  - Proper error messages showing which metric triggered threshold

- **Integrate measure_parse_rate.py:**
  - `scripts/measure_parse_rate.py` already tracks parse_rate and convert_rate
  - Extend to track performance metrics (conversion time per model)
  - Output unified JSON: `{"parse_rate": 100.0, "convert_rate": 90.0, "avg_time_ms": 1250, ...}`

- **Update CI Workflow:**
  - `.github/workflows/gamslib-regression.yml` uses all 3 metrics
  - Thresholds: `--parse-rate-warn=5 --parse-rate-fail=10 --convert-rate-warn=5 --convert-rate-fail=10 --performance-warn=20 --performance-fail=50`
  - PR comment shows all 3 metrics with status (✅/⚠️/❌)

#### Deliverables
1. Functional `check_parse_rate_regression.py` with all threshold arguments working
2. Unified metrics JSON output from `measure_parse_rate.py`
3. Updated CI workflow using all 3 metrics
4. Test suite validating threshold behavior
5. Documentation update in `docs/infrastructure/CI_REGRESSION_GUARDRAILS.md`

#### Acceptance Criteria
- ✅ All CLI arguments functional with proper threshold checking
- ✅ CI workflow uses all 3 metrics (parse, convert, performance)
- ✅ Exit codes: 0 (pass), 1 (warn), 2 (fail)
- ✅ PR comments show all 3 metrics with visual status indicators
- ✅ Test suite validates warn/fail thresholds trigger correctly

#### Dependencies
- None (can start immediately)

#### Risks
- convert_rate tracking may expose new failures in pipeline → Need debugging time
- Performance variance on CI runners (±10%) → Thresholds account for this (20%/50%)

---

## MEDIUM Priority Items (Important but Not Blocking)

### 3. JSON Diagnostics Output

**Category:** Diagnostics Mode - Output Formats  
**Effort:** 2 hours  
**Priority:** MEDIUM  
**Status:** Not started (text output implemented in Sprint 11)

#### Problem Statement
Sprint 11 implemented `--diagnostic` flag with text table output. This covers 90% of use cases but lacks machine-parseable format for automation, trending, and programmatic analysis.

#### Scope
- **JSON Schema Design:**
  ```json
  {
    "summary": {
      "total_duration_ms": 1234,
      "overall_success": true,
      "stages_completed": 5
    },
    "stages": [
      {
        "name": "Parse",
        "duration_ms": 123,
        "status": "success",
        "input_size": 1024,
        "output_size": 2048
      },
      ...
    ],
    "simplification": {
      "iterations": 3,
      "transformations_applied": 45,
      "term_reduction_pct": 32.5,
      "passes": [
        {
          "name": "Factoring",
          "transformations": 12,
          "term_reduction": 8
        },
        ...
      ]
    }
  }
  ```

- **Implementation:**
  - Add `--diagnostic-json` flag (mutually exclusive with `--diagnostic`)
  - Serialize `DiagnosticReport` dataclass to JSON
  - Support output to stdout, stderr, or file (`--diagnostic-output=file.json`)
  - Backward compatible with existing `--diagnostic` (text output)

- **CI Integration:**
  - Store diagnostic JSON as CI artifacts (30-day retention)
  - Enable historical trending and analysis

#### Deliverables
1. `--diagnostic-json` flag implementation
2. JSON schema documentation in `docs/DIAGNOSTICS.md`
3. Example JSON outputs for 3 representative models
4. CI artifact storage integration
5. Unit tests for JSON serialization

#### Acceptance Criteria
- ✅ `--diagnostic-json` outputs valid JSON to stdout or file
- ✅ Schema documented with field descriptions
- ✅ Backward compatible with `--diagnostic` (text remains default)
- ✅ CI stores diagnostic JSON as artifacts
- ✅ JSON validates against schema

#### Dependencies
- None (extends existing diagnostics infrastructure)

#### Follow-On Work
- Item #5 (Dashboard Integration) consumes JSON output

---

### 4. PATH Solver CI Integration

**Category:** MCP Validation - Solve Testing  
**Effort:** 3-5 hours (if licensing approved)  
**Priority:** MEDIUM (blocked on licensing clarification)  
**Status:** Blocked (IPOPT prototype implemented as alternative)

#### Problem Statement
Sprint 11 implemented IPOPT-based MCP smoke tests due to unclear PATH academic license terms for CI/cloud usage. PATH provides <1% accuracy improvement over IPOPT but requires licensing clarification.

#### Scope
- **Licensing Clarification (async, non-blocking):**
  - Contact: Michael C. Ferris (ferris@cs.wisc.edu)
  - Request: Written confirmation that PATH academic license permits GitHub Actions CI usage
  - Timeline: May take 1-4 weeks for response

- **Implementation (if approved):**
  - Install PATH in GitHub Actions via GAMS distribution (~2 min install)
  - Replace IPOPT smoke tests with PATH for higher accuracy
  - 4-test smoke suite (same as IPOPT):
    1. Trivial 2×2 MCP (x+y=1, x=y, x,y≥0)
    2. hansmcp.gms (5 variables, Hansen 1979 example)
    3. Infeasible MCP (x≥0, y≥2, x+y=1)
    4. Unbounded MCP (x-y=0, x,y free)
  - Nightly CI validation (not per-PR due to ~5 min runtime)
  - Fallback to IPOPT if PATH unavailable

- **Decision Matrix:**
  - **If approved:** Implement PATH, keep IPOPT as fallback
  - **If denied:** Keep IPOPT only, document limitation
  - **If no response:** Continue IPOPT, defer PATH indefinitely

#### Deliverables
1. Email to PATH maintainer requesting CI usage permission
2. Decision documented in `docs/infrastructure/PATH_LICENSING.md`
3. If approved: PATH smoke tests in nightly CI workflow
4. If denied: Documentation of IPOPT limitations vs PATH
5. Comparison report: IPOPT vs PATH accuracy on 10 test MCPs

#### Acceptance Criteria
- ✅ Written confirmation from PATH maintainer (or denial/no response)
- ✅ Decision documented with rationale
- ✅ If approved: PATH installed in nightly CI, smoke tests passing
- ✅ If denied: IPOPT remains, limitations documented
- ✅ Fallback mechanism tested (IPOPT if PATH unavailable)

#### Dependencies
- Blocked on PATH maintainer response (async)

#### Risks
- Maintainer may not respond → Proceed with IPOPT after 4 weeks
- Licensing denied → IPOPT sufficient for most use cases (<1% accuracy difference)

---

### 5. Tier 2 GAMSLib Model Exploration

**Category:** Parser Coverage - Model Expansion  
**Effort:** 4-6 hours (research + initial implementation)  
**Priority:** MEDIUM  
**Status:** Not started (Sprint 11 achieved 100% Tier 1)

#### Problem Statement
Sprint 11 achieved 100% Tier 1 parse rate (10/10 models). Natural next step is expanding coverage to Tier 2 models to identify new parser gaps and increase overall parse rate.

#### Scope
- **Tier 2 Model Selection (10 models):**
  - Criteria: Diversity of GAMS features, small-medium size, representative NLP patterns
  - Candidates from GAMSLib: chenery, demandq, dipole, dispatch, egypt, fdesign, gasoil, hydroelasticity, jbearing, karush
  - Avoid: Very large models (>1000 lines), solver-specific syntax, exotic features

- **Parse Failure Analysis:**
  - Run `scripts/ingest_gamslib.py` on Tier 2 models
  - Classify failures by blocker category (new categories beyond Tier 1)
  - Prioritize blockers by frequency (most common = highest impact)
  - Examples from past: `alias` statements, `loop` constructs, advanced `$` directives

- **Implementation Plan:**
  - Create `docs/planning/EPIC_2/SPRINT_12/TIER_2_IMPLEMENTATION_PLAN.md`
  - Effort estimates per blocker category
  - Prioritization: HIGH (affects >3 models), MEDIUM (2-3 models), LOW (1 model)
  - Sprint 12 scope: Implement HIGH priority blockers only

- **CI Integration:**
  - Add Tier 2 models to nightly CI (not per-PR, too slow)
  - Separate workflow: `tier2-validation.yml`
  - Target: ≥50% Tier 2 parse rate by Sprint 12 end (5/10 models)

#### Deliverables
1. Tier 2 model list (10 models) with selection rationale
2. Parse failure analysis with blocker taxonomy
3. `TIER_2_IMPLEMENTATION_PLAN.md` with effort estimates
4. Nightly CI workflow for Tier 2 validation
5. Baseline: `baselines/parse_rate/tier2_sprint12.json`

#### Acceptance Criteria
- ✅ Tier 2 model list documented and validated
- ✅ Parse failure analysis complete (blocker categories identified)
- ✅ Implementation plan with effort estimates per blocker
- ✅ Tier 2 added to nightly CI workflow
- ✅ Target: ≥50% Tier 2 parse rate by Sprint 12 end (5/10 models)

#### Dependencies
- None (100% Tier 1 complete, ready to expand)

#### Risks
- Tier 2 may reveal complex features requiring >10h effort → Defer to Sprint 13
- Parser complexity increasing → Need refactoring before adding more features

---

### 6. CI Workflow Testing Checklist

**Category:** Process - Quality Assurance  
**Effort:** 1 hour  
**Priority:** MEDIUM  
**Status:** Not started (process improvement from retrospective)

#### Problem Statement
Sprint 11 had 2 follow-up PRs fixing CI workflow issues:
- PR fixing GITHUB_TOKEN permissions
- PR fixing file path (`sprint8.json` → `sprint11.json`)

These issues could be prevented with pre-flight testing checklist.

#### Scope
- **PR Template Enhancement:**
  - Add "CI Workflow Changes" section to `.github/pull_request_template.md`
  - Checklist items (if workflow files modified):
    - [ ] Workflow syntax validated (`actionlint` or GitHub validator)
    - [ ] File paths verified (no hardcoded sprint numbers)
    - [ ] Permissions tested (no GITHUB_TOKEN errors)
    - [ ] Secrets/variables exist in repo settings
    - [ ] Matrix strategy tested with actual values
    - [ ] Workflow triggered in test branch before PR

- **Documentation:**
  - Create `docs/infrastructure/CI_WORKFLOW_TESTING.md`
  - Step-by-step guide for testing workflows locally/in fork
  - Common pitfalls and solutions
  - Links to GitHub Actions documentation

- **Tooling (optional, +1h):**
  - Add `make lint-workflows` target using `actionlint`
  - Pre-commit hook suggestion (optional, not enforced)

#### Deliverables
1. Updated `.github/pull_request_template.md` with CI checklist
2. `docs/infrastructure/CI_WORKFLOW_TESTING.md` guide
3. Optional: `make lint-workflows` target
4. Team adoption (track in Sprint 12 retrospective)

#### Acceptance Criteria
- ✅ PR template includes CI workflow testing checklist
- ✅ Documentation covers common workflow issues
- ✅ At least 1 sprint with zero CI-fix follow-up PRs
- ✅ Team feedback positive (retrospective review)

#### Dependencies
- None

#### Risks
- Checklist may be ignored → Monitor adoption, adjust if needed

---

## LOW Priority Items (Nice-to-Have)

### 7. LOW Priority Transformations (5 patterns)

**Category:** Aggressive Simplification - Additional Patterns  
**Effort:** 6-8 hours  
**Priority:** LOW (conditional on Item #1 benchmarking results)  
**Status:** Not started (deferred pending measurement)

#### Problem Statement
Sprint 11 implemented 11 HIGH/MEDIUM priority transformations. Transformation catalog documents 5 additional LOW priority patterns that were deferred due to complexity or uncertain benefit.

**Key Decision:** Only implement if Item #1 (Term Reduction Benchmarking) reveals <20% average reduction with current transformations.

#### Patterns to Implement (if needed)

##### T2.3: Common Denominator (2h)
- **Pattern:** `a/b + c/d → (a*d + c*b)/(b*d)`
- **Benefit:** Enables factoring in combined numerator
- **Complexity:** High - must detect when beneficial vs explosion
- **Example:** `x/y + z/w → (x*w + z*y)/(y*w)` then factor numerator
- **Risk:** Expression size explosion if not careful

##### T3.3: Multiplication-Division Reordering (2h)
- **Pattern:** `(x * y) / z → x * (y / z)` when beneficial
- **Benefit:** Enables cancellation opportunities (e.g., if `y = z*k` then `x * (z*k / z) → x * k`)
- **Complexity:** Requires heuristics to avoid numerical instability
- **Example:** `(2 * (x*y)) / x → 2 * ((x*y) / x) → 2 * y`
- **Risk:** Floating-point precision loss in some cases

##### T5.2: Nested Expression CSE (2h)
- **Pattern:** Extract CSE from nested expressions (e.g., inside function calls)
- **Current limitation:** CSE only operates on top-level expressions
- **Benefit:** 5-10% additional reduction on complex models with nested `exp`, `log`, etc.
- **Example:** `exp(x+y) + sin(x+y) → t1 = x+y; exp(t1) + sin(t1)`
- **Complexity:** Requires recursive traversal and context tracking

##### T5.3: Multiplicative Subexpression CSE (1h)
- **Pattern:** `x*y` appearing in multiple terms
- **May be redundant:** Factoring (T1.1) already handles this
- **Benefit:** Marginal if factoring works well
- **Example:** `x*y + 2*x*y → (x*y) * (1 + 2)` (but factoring does this better)
- **Decision:** Likely skip this one even if implementing others

##### T5.4: CSE with Aliasing (2h)
- **Pattern:** Reuse existing variable assignments instead of creating temps
- **Current limitation:** CSE always creates new `cse_tmp_*` variables
- **Benefit:** Cleaner generated code, fewer temps
- **Example:** Given `scalar t1; t1 = x+y;` in model, expression `(x+y)^2` reuses `t1` instead of creating `cse_tmp_0`
- **Complexity:** Requires expression canonicalization and symbol table aliasing
- **Implementation:** Track variable-to-expression mappings, match before creating temps

#### Implementation Strategy
1. Run Item #1 benchmarking on all 10 Tier 1 models
2. If average reduction ≥20%: **Skip LOW priority transformations** (current ones sufficient)
3. If average reduction <20%: Implement patterns in priority order:
   - First: T5.2 (Nested CSE) - likely highest additional value
   - Second: T2.3 (Common Denominator) - enables more factoring
   - Third: T5.4 (CSE Aliasing) - code quality improvement
   - Fourth: T3.3 (Reordering) - numerical stability concerns
   - Skip: T5.3 (Multiplicative CSE) - redundant with factoring

#### Deliverables (if implemented)
1. Implementation of selected patterns in `src/ir/transformations/`
2. Comprehensive test suite (10+ tests per pattern)
3. Updated transformation catalog with implementation status
4. Benchmarking results showing incremental improvement
5. Documentation of which patterns to use when

#### Acceptance Criteria
- ✅ Only implement if current transformations <20% average reduction
- ✅ Each pattern must pass cost/benefit analysis before implementation
- ✅ Test suite ≥10 tests per implemented pattern
- ✅ Benchmarking shows incremental improvement (≥5% additional reduction)
- ✅ Document decision to skip patterns if current transformations sufficient

#### Dependencies
- **Blocked by:** Item #1 (Term Reduction Benchmarking)

#### Risks
- May not be needed at all if current transformations sufficient → Low risk (good problem to have)
- Implementation complexity may exceed estimates → Defer individual patterns if needed

---

### 8. Dashboard Integration for Diagnostics

**Category:** Diagnostics Mode - Visualization  
**Effort:** 4-6 hours  
**Priority:** LOW  
**Status:** Not started (text + JSON outputs sufficient for now)

#### Problem Statement
Diagnostics mode provides text tables and JSON output (Item #3) but lacks visual dashboard for trend analysis and historical comparison.

#### Scope
- **HTML Dashboard Generation:**
  - Input: Diagnostic JSON files from CI artifacts
  - Output: Static HTML dashboard with charts and tables
  - Technology: Chart.js or similar (no backend needed)

- **Visualizations:**
  - Stage timing chart (bar chart: Parse, Semantic, Simplification, IR, MCP)
  - Simplification effectiveness over time (line chart: Sprint 10 → 11 → 12)
  - Transformation application frequency (pie chart: which transformations used most)
  - Model comparison table (heatmap: which models benefit most from simplification)
  - Historical trends (line chart: performance over sprints)

- **GitHub Pages Integration:**
  - Host dashboard at `https://jeffreyhorn.github.io/nlp2mcp/diagnostics/`
  - Auto-update from CI artifacts (GitHub Actions workflow)
  - Compare across sprint baselines (Sprint 10 vs 11 vs 12)
  - Link from README.md for easy access

- **Data Management:**
  - Fetch diagnostic JSON from CI artifacts API
  - Aggregate across multiple runs (per model, per sprint)
  - Store processed data in `docs/diagnostics/data/` for GitHub Pages

#### Deliverables
1. HTML dashboard template with Chart.js integration
2. Data aggregation script (`scripts/aggregate_diagnostics.py`)
3. GitHub Pages deployment workflow
4. Dashboard accessible at public URL
5. README.md link to dashboard

#### Acceptance Criteria
- ✅ Dashboard accessible at GitHub Pages URL
- ✅ Shows at least 3 sprints of historical data (Sprints 10, 11, 12)
- ✅ Interactive charts (hover for details, zoom, filter)
- ✅ Auto-updates from CI runs (nightly or per-sprint)
- ✅ Mobile-friendly responsive design

#### Dependencies
- **Requires:** Item #3 (JSON Diagnostics Output)

#### Risks
- Chart.js learning curve → Use simple templates/examples
- GitHub Pages deployment complexity → Well-documented process

---

### 9. CSE Temp Variable Propagation

**Category:** Aggressive Simplification - Code Generation  
**Effort:** 2-3 hours  
**Priority:** LOW (pending user feedback)  
**Status:** Not started (current behavior: temps inlined)

#### Problem Statement
Currently CSE generates temporary variables (`cse_tmp_0`, etc.) during simplification but inlines them back into expressions during MCP generation. This prevents inspection/debugging of CSE decisions.

**User Feedback Needed:** Is seeing CSE temps in final output valuable or just clutter?

#### Scope
- **Current Behavior:**
  ```gams
  * CSE creates: t1 = exp(x+y)
  * Final output: obj.. z =e= exp(x+y) + 2*exp(x+y);  (inlined)
  ```

- **Proposed Behavior:**
  ```gams
  Scalar cse_tmp_0 = exp(x+y);
  obj.. z =e= cse_tmp_0 + 2*cse_tmp_0;
  ```

- **Implementation:**
  - Preserve CSE temps in symbol table during MCP generation
  - Emit `Scalar cse_tmp_N = <expr>;` declarations before equations
  - Update expression references to use temp variables
  - Add `--cse-inline` flag to toggle behavior (default: preserve temps)

- **Benefits:**
  - Debugging: See exactly what CSE extracted
  - Performance: Solvers may benefit from explicit temp variables
  - Clarity: Clearer understanding of optimization decisions

- **Drawbacks:**
  - Output verbosity: More lines in generated GAMS code
  - Naming conflicts: Must ensure `cse_tmp_*` names unique
  - Solver compatibility: Some solvers may not handle extra scalars well

#### Deliverables
1. Implementation of temp preservation in MCP generation
2. `--cse-inline` flag to restore inlining behavior
3. Test suite validating both modes
4. Example outputs showing difference
5. User feedback collection (GitHub discussion or issue)

#### Acceptance Criteria
- ✅ CSE temps appear in generated GAMS code by default
- ✅ Temps correctly referenced in equations (no dangling references)
- ✅ `--cse-inline` restores Sprint 11 behavior (temps inlined)
- ✅ No naming conflicts with user variables
- ✅ User feedback collected on temp visibility preference

#### Dependencies
- None (extends existing CSE implementation)

#### Risks
- Users may prefer inlined behavior → Make it optional with flag
- Temp naming conflicts → Use unique prefix like `_nlp2mcp_cse_tmp_`

---

### 10. Transformation Catalog Alignment

**Category:** Aggressive Simplification - Documentation/Implementation  
**Effort:** 1-2 hours (documentation) OR 6-8 hours (implementation)  
**Priority:** LOW  
**Status:** Documentation-implementation mismatch

#### Problem Statement
Transformation catalog documents 18 patterns, but implementation provides 11 functions. Gap of 7 patterns creates confusion about what's available.

**7 Pattern Gap Breakdown:**
- 5 LOW priority patterns (see Item #7) - deferred pending benchmarking
- 2 patterns merged into other functions (T4.3 = T2.2)

#### Scope - Option A: Documentation Update (1-2h)
- Update `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md`
- Mark each pattern with implementation status:
  - ✅ **IMPLEMENTED** (Sprint 11)
  - ⏸️ **DEFERRED** (Sprint 12+ conditional on benchmarking)
  - 🔀 **MERGED** (functionality in another pattern)
  - ❌ **NOT PLANNED** (decided against implementation)

- Create summary table:
  ```markdown
  | Pattern | Status | Implementation | Notes |
  |---------|--------|----------------|-------|
  | T1.1 Factoring | ✅ IMPLEMENTED | Sprint 11 | src/ir/transformations/factoring.py |
  | T2.3 Common Denom | ⏸️ DEFERRED | Sprint 12+ | Pending benchmarking results |
  ...
  ```

- Update README.md and `docs/SIMPLIFICATION.md` explaining which patterns are active

#### Scope - Option B: Implement Remaining (6-8h)
- See Item #7 (LOW Priority Transformations)
- Only pursue if benchmarking shows need

#### Deliverables (Option A - Recommended)
1. Updated transformation_catalog.md with status markers
2. Summary table showing implementation status
3. Updated README.md/SIMPLIFICATION.md with active patterns list
4. Clear indication of which patterns are production-ready

#### Acceptance Criteria
- ✅ All 18 catalog patterns have clear status (implemented/deferred/merged/not planned)
- ✅ Summary table easy to scan
- ✅ User-facing docs (README, SIMPLIFICATION.md) reflect actual implementation
- ✅ No confusion about which patterns are available

#### Dependencies
- Option B blocked by Item #1 (benchmarking)

#### Recommendation
**Option A** (documentation) is sufficient unless benchmarking reveals need for Option B.

---

### 11. Consistent Transformation Naming Convention

**Category:** Process - Documentation Standards  
**Effort:** 1 hour  
**Priority:** LOW  
**Status:** Not started (process improvement from retrospective)

#### Problem Statement
Sprint 11 used mixed naming: T-numbers (T1.1, T5.2) and descriptive names (factoring, CSE). This caused confusion in PRs and reviews about which transformation is being discussed.

#### Scope
- **Decision Needed:** Choose one convention
  - **Option A:** T-numbers everywhere (T1.1, T2.1, T5.2)
    - Pro: Catalog reference clear
    - Con: Less readable ("T1.1" vs "factoring")
  
  - **Option B:** Descriptive names everywhere (factoring, fractions, CSE)
    - Pro: More readable, self-documenting
    - Con: Catalog cross-reference harder
  
  - **Option C:** Hybrid (descriptive in code/docs, T-numbers in catalog only)
    - Pro: Best of both worlds
    - Con: Requires mapping table

- **Recommended:** Option C (hybrid with mapping table)

- **Update All Documentation:**
  - Code comments: Use descriptive names
  - CHANGELOG.md: Use descriptive names with T-number reference
  - transformation_catalog.md: Primary reference with both
  - CONTRIBUTING.md: Document convention for new transformations

- **Create Mapping Table:**
  ```markdown
  | T-Number | Descriptive Name | Function |
  |----------|------------------|----------|
  | T1.1 | Common Factor Extraction | factor_common_terms() |
  | T2.1 | Fraction Combining | combine_fractions() |
  ...
  ```

#### Deliverables
1. Decision documented in CONTRIBUTING.md
2. Mapping table in transformation_catalog.md
3. All Sprint 11 documentation updated to match convention
4. Template for adding new transformations with both names

#### Acceptance Criteria
- ✅ Single naming convention documented and applied
- ✅ Mapping table shows T-number ↔ descriptive name ↔ function
- ✅ All documentation updated (CHANGELOG, README, catalog, code comments)
- ✅ CONTRIBUTING.md includes transformation naming guidelines
- ✅ Future PRs follow convention (verify in Sprint 12 retrospective)

#### Dependencies
- None

#### Risks
- None (pure documentation task)

---

### 12. Performance Trending and Visualization

**Category:** CI Regression Guardrails - Analytics  
**Effort:** 4-6 hours  
**Priority:** LOW  
**Status:** Not started (valuable for retrospectives but not blocking)

#### Problem Statement
CI tracks regression baselines but lacks historical trending visualization. Retrospectives would benefit from sprint-over-sprint performance charts.

#### Scope
- **Markdown Table (2-3h):**
  - Create `docs/performance/TRENDS.md`
  - Table format:
    ```markdown
    | Sprint | Parse Rate | Convert Rate | Test Time | Simplification | Models Parsed |
    |--------|------------|--------------|-----------|----------------|---------------|
    | 8      | 40%        | 40%          | 24s       | N/A            | 4/10          |
    | 9      | 60%        | 60%          | 26s       | N/A            | 6/10          |
    | 10     | 90%        | 90%          | 27s       | N/A            | 9/10          |
    | 11     | 100%       | 100%         | 16.79s    | 39.2%          | 10/10         |
    | 12     | ?          | ?            | ?         | ?              | ?/20          |
    ```
  - Update manually at end of each sprint (or automate)

- **GitHub Pages Charts (optional, +2-3h):**
  - Chart.js line charts showing trends
  - Visualizations:
    - Parse rate over time (line chart)
    - Test suite performance (bar chart: Sprint 8-12)
    - Simplification effectiveness (line chart with confidence intervals)
  - Host at `https://jeffreyhorn.github.io/nlp2mcp/trends/`

- **Automation (optional, +1-2h):**
  - GitHub Actions workflow to update TRENDS.md
  - Fetch data from baseline JSONs
  - Generate markdown table automatically
  - Commit to repo or publish to GitHub Pages

#### Deliverables
1. `docs/performance/TRENDS.md` with at least 3 sprints of data
2. Optional: GitHub Pages with interactive charts
3. Optional: Automation workflow for updates
4. Link from README.md to trends documentation

#### Acceptance Criteria
- ✅ TRENDS.md shows at least 3 sprints (8, 9, 10, 11)
- ✅ Table includes: parse rate, convert rate, test time, simplification effectiveness
- ✅ Updated at Sprint 12 end with Sprint 12 data
- ✅ Easy to read and understand (clear headers, units)
- ✅ Optional: Charts embedded in GitHub Pages

#### Dependencies
- None (historical data already available)

#### Risks
- Manual updates may be forgotten → Add to sprint checklist or automate

---

## Summary and Recommendations

### Effort Breakdown by Priority

| Priority | Items | Effort Range | Recommended |
|----------|-------|--------------|-------------|
| HIGH | 2 | 7-10h | ✅ Must do |
| MEDIUM | 4 | 12-18h | ✅ Should do |
| LOW | 6 | 16-25h | ⚠️ Conditional |
| **Total** | **12** | **35-53h** | **19-28h recommended** |

### Sprint 12 Recommended Scope

**Primary Theme:** "Measurement, Polish, and Tier 2 Expansion"

**HIGH Priority (Must Do - 7-10h):**
1. Term Reduction Benchmarking (4-6h) - Validates Sprint 11 success criteria
2. Multi-Metric Threshold Implementation (3-4h) - Completes technical debt

**MEDIUM Priority (Should Do - 12-18h):**
3. JSON Diagnostics Output (2h) - Enables automation
4. PATH Solver Integration (3-5h) - If licensing approved (async)
5. Tier 2 Model Exploration (4-6h) - Primary Sprint 12 goal
6. CI Workflow Testing Checklist (1h) - Process improvement

**Total Recommended Scope:** 19-28 hours (fits typical sprint capacity)

**LOW Priority (Defer Unless Needed):**
- Item #7: LOW Priority Transformations (6-8h) - Only if benchmarking shows <20% reduction
- Item #8: Dashboard Integration (4-6h) - Nice-to-have, defer to Sprint 13
- Item #9: CSE Temp Propagation (2-3h) - Pending user feedback
- Item #10: Catalog Alignment (1-2h) - Do documentation-only option
- Item #11: Naming Convention (1h) - Quick win if time permits
- Item #12: Performance Trending (4-6h) - Defer to Sprint 13

### Decision Points

**Day 3 Checkpoint:** Has Item #1 (benchmarking) revealed <20% average reduction?
- **If yes:** Add Item #7 (LOW priority transformations) to sprint
- **If no:** Skip Item #7, proceed with Tier 2 expansion

**Day 7 Checkpoint:** Has PATH maintainer responded?
- **If approved:** Implement Item #4 (PATH integration)
- **If denied or no response:** Keep IPOPT, document decision

**Day 10 Retrospective:** Review LOW priority items
- Which items should move to Sprint 13?
- Which items can be permanently deferred or removed?

---

## Sprint 12 Success Criteria (Proposed)

1. ✅ **Term Reduction Validated:** ≥20% average reduction on ≥50% of Tier 1 models (or transformations adjusted)
2. ✅ **Multi-Metric CI Complete:** All 3 metrics (parse, convert, performance) tracked with thresholds
3. ✅ **Tier 2 Parse Rate:** ≥50% (5/10 models) parsing successfully
4. ✅ **JSON Diagnostics:** Implemented and documented
5. ✅ **PATH Decision:** Licensing clarified and decision implemented
6. ✅ **Process Improvements:** CI checklist adopted, zero follow-up fix PRs

**Stretch Goals:**
- LOW priority transformations (if benchmarking reveals need)
- Dashboard integration (if time permits)
- Naming convention standardized

---

## Cross-References

- **Sprint 11 Retrospective:** `docs/planning/EPIC_2/SPRINT_11/RETROSPECTIVE.md` (Action Items section)
- **Transformation Catalog:** `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md` (LOW priority patterns)
- **PATH Research:** `docs/planning/EPIC_2/SPRINT_11/path_smoke_test_integration.md` (licensing investigation)
- **Diagnostics Architecture:** `docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md` (JSON deferral rationale)
- **CI Survey:** `docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md` (multi-metric design)

---

**Document Status:** ✅ Ready for Sprint 12 Planning  
**Next Steps:** Review with stakeholders, finalize Sprint 12 scope, create detailed PLAN.md
