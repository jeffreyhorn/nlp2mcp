# EPIC 2 Project Plan (v1.0 Track)

This plan translates `GOALS_REVISED.md` into sprint-ready guidance for Sprints 6–10 (two weeks each).

---

# Sprint 6 (Weeks 1–2): Convexity Heuristics, Critical Bug Fixes, GAMSLib Bootstrapping, UX Kickoff

**Goal:** Ship actionable convexity heuristics, close high-severity reformulation bugs, stand up GAMSLib ingestion + dashboards, and begin iterative UX improvements.

## Components
- **Convexity Heuristic Pass**
  - Implement pattern-based nonconvex detectors (nonlinear equalities, trig, bilinear, quotients, odd powers).
  - CLI flags: `--strict-convexity` (fail on warning) and default warning mode.
  - Documentation section covering when to trust MCP vs stick with NLP.
- **Critical Bug Fixes**
  - ~~Adjust KKT stationarity for maximize-sense bound multipliers.~~ **REMOVED** - No bug exists (verified 2025-11-12)
  - Implement nested min/max flattening (Option A) plus regression tests & PATH validation.
- **GAMSLib Bootstrapping**
  - Script to download/refresh target NLP models, run nightly ingestion.
  - Initial `CONVERSION_STATUS.md` with parse results and error buckets.
  - Baseline KPI: ≥10 models ingested; ≥10 % parse success.
- **UX Improvements (Iteration 1)**
  - Enhance parser/convexity error copy with line/column context and doc links.
  - Add sprint demo checklist for UX increments.

## Deliverables
- Convexity heuristic module + CLI flags + docs.
- ~~Fixed maximize multiplier~~ + nested min/max flattening with tests.
- `scripts/download_gamslib_nlp.sh`, ingestion cron, and conversion dashboard.

**Note:** Maximize multiplier bug fix removed from scope - verified no bug exists (see `SPRINT_6/TASK3_CORRECTED_ANALYSIS.md`).
- Updated error messaging + documentation describing new warnings.
- Release tag `v0.6.0`.

## Acceptance Criteria
- Heuristic warnings trigger on curated nonconvex samples and stay silent on convex baselines.
- Maximize/minimize regression suite fully green; nested min/max research cases convert and solve in PATH.
- GAMSLib ingestion runs nightly; dashboard lists ≥10 models with parse status.
- UX checklist for sprint shows completed error-messaging improvements.

---

# Sprint 7 (Weeks 3–4): Parser Enhancements Wave 1, Optional Convexity AST Pass, UX Iteration, KPI Tracking ✅ COMPLETE

**Goal:** Raise parser coverage to ≥20 %, experiment with AST-based convexity analysis if time allows, integrate KPIs/dashboards, and continue UX upgrades.

**Status:** ✅ **COMPLETE** - Completed 2025-11-16, v0.7.0 released  
**Actual Results:**
- ✅ Parse Rate: 20% achieved (2/10 GAMSLib models)
- ✅ Test Performance: 7.1x speedup (208s → 29.23s fast suite)
- ✅ Convexity UX: 100% warnings show line numbers
- ✅ CI Automation: Regression detection active
- ✅ Quality: 1287 tests passing, all checks passing

## Components
- **Parser Enhancements (Wave 1)**
  - Prioritize syntax gaps revealed by Sprint 6 telemetry (e.g., `.l/.m`, assignment statements, simple dollar conditions).
  - Update normalization + IR to support new constructs.
- **Convexity AST Analysis (Optional)**
  - Compose expression-class tracking for `--analyze-convexity` flag (CONSTANT/AFFINE/CONVEX/CONCAVE/UNKNOWN).
  - Emit detailed reports citing problematic equations.
- **Telemetry & KPIs**
  - Automate dashboard updates; KPI: ≥20 % of tracked GAMSLib models parse, ≥15 % convert.
  - Introduce PATH smoke target for simple models (if licensing available).
- **UX Improvements (Iteration 2)**
  - Add lightweight progress indicators (stage-level timers) and refine error guidance for newly supported syntax.

## Deliverables
- Parser support for top-priority GAMSLib features + regression tests.
- (If implemented) AST-based convexity analysis doc + CLI flag.
- Updated conversion dashboard with parse/convert metrics + PATH smoke stats.
- Progress indicator implementation + improved error copy.
- Release tag `v0.7.0`.

## Acceptance Criteria
- Telemetry shows ≥20 % parse success across selected GAMSLib set; dashboard auto-updates per run.
- Newly supported syntax passes unit/integration tests; previously working models unaffected.
- If AST analysis shipped, sample report matches designed expectations.
- Progress indicators reflected in CLI output; UX checklist ticked for sprint.

---

# Sprint 8 (Weeks 5–6): Parser Maturity & Developer Experience (Hybrid Strategy) ✅ COMPLETE

**Goal:** Incremental parse rate improvement (20% → 25%) with enhanced developer UX through parser error line numbers and improved diagnostics. Conservative, achievable targets based on Sprint 7 retrospective.

**Status:** ✅ **COMPLETE** - Completed 2025-11-18, v0.8.0 ready for release  
**Actual Results:**
- ✅ Parse Rate: 40% achieved (4/10 GAMSLib models) - **EXCEEDED target by 60%** (40% vs 25% target)
- ✅ Parser Features: Option statements + Indexed assignments fully implemented
- ✅ Error UX: 100% of parse errors show line numbers, 5 enhancement rules active
- ✅ Partial Metrics: Dashboard shows parse progress percentages with 4-level color coding
- ✅ Test Suite: 1349 tests passing (5x faster: 120s → 24s)
- ✅ Documentation: Comprehensive retrospective with Sprint 9 recommendations

**Strategy:** 60% Parser Maturity + 40% Infrastructure/UX (Sprint 7 Retrospective recommendation)

## Components

### Parser Enhancements (60% effort, ~15-20 hours)
- **Option Statements (High Priority)**
  - Implement `option` statement parsing (`option limrow = 0;`, `option limcol = 0;`)
  - Unlocks: mhw4dx.gms and other models using basic options
  - Effort: 6-8 hours
  - Risk: Low (grammar extension, semantic handling straightforward)
  
- **Per-Model Feature Analysis**
  - Create feature dependency matrix for all 10 GAMSLib models
  - Identify models closest to parsing (1-2 features away)
  - Prioritize features that unlock multiple models
  - Effort: 3-4 hours
  - Deliverable: `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md`

- **One Additional High-ROI Feature** (choose based on analysis)
  - Either: Simple indexed assignments (if unlocks 2+ models)
  - Or: Function call syntax improvements (if unlocks 2+ models)
  - Effort: 6-8 hours
  - Risk: Medium (grammar changes required)

### Infrastructure & UX Improvements (40% effort, ~10-15 hours)
- **Parser Error Line Numbers (High Priority)**
  - Extend SourceLocation tracking to parser errors (builds on Sprint 7 work)
  - Show precise file/line/column for all parse errors
  - Effort: 4-6 hours
  - Risk: Very Low (infrastructure exists from convexity line numbers)
  
- **Partial Parse Metrics**
  - Track percentage of statements parsed per model (not just binary pass/fail)
  - Update dashboard to show "80% parsed" for partially-supported models
  - Effort: 3-4 hours
  - Deliverable: Enhanced `docs/status/GAMSLIB_CONVERSION_STATUS.md`
  
- **Improved Error Messages**
  - Enhance parser error messages with actionable suggestions
  - Add "did you mean?" hints for common mistakes
  - Effort: 3-5 hours

## Deliverables
- Option statement support with regression tests
- One additional parser feature (indexed assignments OR function calls)
- Parser error line numbers for all parse errors
- Per-model feature dependency matrix
- Partial parse metrics in dashboard
- Improved error messages with suggestions
- Release tag `v0.8.0`

## Acceptance Criteria - All Met ✅
- ✅ **Parse Rate:** ≥25% (2.5/10 models) - **ACHIEVED 40%** (exceeded by 60%)
- ✅ **Parser Errors:** 100% of parse errors show file/line/column (matches convexity UX)
- ✅ **Feature Matrix:** All 10 models analyzed with feature dependencies documented
- ✅ **Partial Metrics:** Dashboard shows statement-level parse success (e.g., "himmel16: 42% parsed")
- ✅ **Quality:** All existing tests pass (1349 passed), new features have comprehensive test coverage
- ✅ **UX Validation:** Error messages tested with real-world models, 5 enhancement rules active

**Estimated Effort:** 25-35 hours (Sprint 7 Retrospective recommendation)  
**Actual Effort:** ~35 hours (within estimate)  
**Risk Level:** LOW (focuses on proven patterns from Sprint 7)

---

# Sprint 8b (Weeks 7–8): Advanced Parser Features & Conversion Pipeline

**Goal:** Implement advanced parser features requiring grammar changes and begin conversion pipeline work. Builds on Sprint 8's foundation with higher-complexity features.

**Strategy:** Advanced features + conversion infrastructure (deferred from original Sprint 8)

## Components

### Advanced Parser Features (~15-20 hours)
- **Advanced Indexing (i++1, i--1)**
  - Implement lead/lag indexing operators
  - Unlocks: himmel16.gms and models with sequential indexing
  - Effort: 8-10 hours
  - Risk: Medium-High (requires grammar changes, semantic complexity)
  
- **Model Sections (mx syntax)**
  - Support multi-line model declarations with `/` syntax
  - Unlocks: hs62.gms, mingamma.gms
  - Effort: 5-6 hours
  - Risk: Medium (grammar extension)
  
- **Equation Attributes (.l/.m)**
  - Parse and store equation attributes where semantically relevant
  - Foundation for conversion pipeline
  - Effort: 4-6 hours

### Conversion & Performance Instrumentation (~10-15 hours)
- **Dashboard Expansion**
  - Track parse/convert/solve rates (extend existing dashboard)
  - KPI: Monitor conversion rate on successfully parsed models
  - Effort: 3-4 hours
  
- **Conversion Pipeline Foundation**
  - Begin conversion infrastructure for successfully parsed models
  - Focus on simple models (mhw4d, rbrock) as initial targets
  - Effort: 6-8 hours
  - Risk: Medium (new pipeline stage)
  
- **Performance Baseline**
  - Establish benchmark harness for parse/convert times
  - Document baseline performance for regression tracking
  - Effort: 3-4 hours

## Deliverables
- Advanced indexing support (i++1, i--1)
- Model sections support (mx syntax)
- Equation attributes parsing (.l/.m)
- Expanded dashboard with conversion tracking
- Conversion pipeline foundation
- Performance baseline documentation
- Release tag `v0.8.1`

## Acceptance Criteria
- **Parse Rate:** ≥30% (3/10 models) - Original Sprint 8 target, achievable with advanced features
- **Advanced Features:** i++1 indexing and model sections working with comprehensive tests
- **Conversion Pipeline:** At least 1 model (mhw4d or rbrock) successfully converts end-to-end
- **Dashboard:** Tracks parse/convert/solve rates automatically
- **Performance:** Baseline benchmarks established and documented
- **Quality:** All existing tests pass, advanced features have edge case coverage

**Estimated Effort:** 25-35 hours  
**Risk Level:** MEDIUM (complex grammar changes, new pipeline stage)

---

# Sprint 9 (Weeks 9–10): Aggressive Simplification, Regression Guardrails, UX Diagnostics

**Goal:** Deliver `--simplification aggressive` informed by telemetry, integrate CI regression hooks (GAMSLib sampling, PATH smoke, performance alerts), and expand diagnostics features.

## Components
- **Aggressive Simplification & CSE**
  - Implement advanced algebraic identities, rational simplification, optional CSE, and simplification metrics (`--simplification-stats`).
  - Ensure FD validation + PATH results align with baseline; integrate with benchmarks.
- **CI Regression Guardrails**
  - Add automated GAMSLib sampling to CI (parse/convert), PATH smoke tests (where licensing permits), performance thresholds with alerting.
- **UX Improvements (Iteration 4)**
  - Introduce deeper diagnostics mode (`--diagnostic`) showing stage-by-stage stats, pipeline decisions, and simplification summaries.

## Deliverables
- Simplification engine updates + documentation + examples.
- CI workflows covering GAMSLib sampling, PATH smoke subset, performance guardrails.
- Diagnostics mode implementation and supporting docs.
- Release tag `v0.9.0`.

## Acceptance Criteria
- Simplification reduces derivative term count ≥20 % on at least half of benchmark models while keeping correctness checks green.
- CI guardrails run on every PR/nightly and block regressions per thresholds.
- Diagnostics mode validated on representative models; UX checklist updated.

---

# Sprint 10 (Weeks 11–12): Final UX Polish, Documentation Wrap, Release Readiness, v1.0.0

**Goal:** Complete diagnostics/progress UI, finalize documentation (advanced usage, GAMSLib handbook, tutorials), close outstanding bugs, and ship v1.0.0 meeting all KPIs.

## Components
- **UX & Diagnostics Finalization**
  - Polish progress indicators, diagnostics, and stats dashboards.
  - Ensure CLI outputs are consistent, localized, and documented.
- **Documentation Enhancements**
  - Expand `docs/ADVANCED_USAGE.md`, `docs/GAMSLIB_EXAMPLES.md`, API reference, and produce video scripts/walkthroughs.
  - Update release notes, changelog, and adoption guides.
- **Release Readiness & QA**
  - Ensure KPIs met (≥80 % parse, ≥60 % convert, ≥40 % solve; ≥90 % code coverage).
  - Run full regression suite, performance benchmarks, and PATH validations.
  - Finalize CI dashboards and release checklist execution.

## Deliverables
- Polished UX features (diagnostics/progress/stats) with final documentation.
- Complete documentation set (advanced usage, GAMSLib examples, API reference, video guides).
- Release notes, CHANGELOG entries, and v1.0.0 tag/sign-off artifacts.

## Acceptance Criteria
- KPIs satisfied and recorded; release checklist completed with approvals.
- Documentation covers all new capabilities and references dashboards/metrics.
- No P0/P1 bugs open; regression and performance suites green.
- PATH/GAMSLib dashboards confirm targets; v1.0.0 artifacts published.

---

## Rolling KPIs & Dashboards
- Sprint-level KPIs (parse/convert/solve, UX increments, coverage) reviewed at each retro.
- Dashboards (conversion status, performance, CI guardrails) must update automatically at least nightly.

---
