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

# Sprint 7 (Weeks 3–4): Parser Enhancements Wave 1, Optional Convexity AST Pass, UX Iteration, KPI Tracking

**Goal:** Raise parser coverage to ≥20 %, experiment with AST-based convexity analysis if time allows, integrate KPIs/dashboards, and continue UX upgrades.

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

# Sprint 8 (Weeks 5–6): Parser Enhancements Wave 2, Nested Min/Max Option B, Conversion & Performance KPIs, UX Iteration

**Goal:** Achieve ≥50 % parse and ≥30 % conversion on target GAMSLib models, add nested min/max Option B if required, and stand up automated performance dashboards while continuing UX work.

## Components
- **Parser Enhancements (Wave 2)**
  - Implement remaining high-impact features (multi-dimensional sets, equation attributes, conditional expressions, selected `display`/`option` statements).
  - Harden normalization and IR storage of `.l/.m` where semantically relevant.
- **Nested Min/Max Option B (Conditional)**
  - If telemetry shows flattening insufficient, add multi-pass reformulation for mixed min/max expressions.
- **Conversion & Performance Instrumentation**
  - Expand dashboard to track parse/convert/solve rates; KPI: ≥50 % parse, ≥30 % convert, ≥10 % solve.
  - Establish benchmark harness comparing NLP solver vs MCP PATH times; log to `docs/benchmarks/GAMSLIB_PERFORMANCE.md`.
- **UX Improvements (Iteration 3)**
  - Add `--stats` output summarizing pipeline timings, derivatives, and convexity notes.

## Deliverables
- Parser feature implementations + regression suites.
- Option B nested min/max support (if triggered) with docs/tests.
- Automated conversion/performance dashboards fed by nightly runs.
- `--stats` CLI mode + documentation updates.
- Release tag `v0.8.0`.

## Acceptance Criteria
- KPIs met: ≥50 % parse and ≥30 % convert across target set; metrics published automatically.
- PATH solve tracking initiated with notes on failures (convexity, solver limits).
- Performance report generated for baseline models; comparisons documented.
- UX checklist shows stats output functioning and validated against real models.

---

# Sprint 9 (Weeks 7–8): Aggressive Simplification, Regression Guardrails, UX Diagnostics

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

# Sprint 10 (Weeks 9–10): Final UX Polish, Documentation Wrap, Release Readiness, v1.0.0

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
