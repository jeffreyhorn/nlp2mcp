# EPIC 2 Goals (Revised): Advanced Features & Real-World Validation

**Timeline:** 10 weeks (5 two-week sprints)  
**Target Release:** v1.0.0  
**Status:** Planning Phase (incorporates GOALS_REVIEW feedback)

---

## Overview

Epic 2 builds on the v0.5.0-beta foundation to reach v1.0.0 by expanding parser coverage, validating against real-world GAMSLib models, improving diagnostics, and delivering advanced analysis tooling. This revision prioritizes early ingestion of real-world models, frontloads critical bug fixes, stages convexity work, and introduces sprint-level KPIs to track progress toward release.

## Strategic Themes

1. **Real-World Validation Early & Often** – ingest GAMSLib models from Sprint 6 onward
2. **Parser Completeness & Bug Fixes** – unblock real workloads before new features
3. **Advanced Analysis & Simplification** – informed by telemetry gathered earlier
4. **User Experience Continuously** – incremental UX improvements each sprint
5. **Quality Guardrails** – rolling KPIs, regression dashboards, CI automation

---

## Goal Categories

### 1. Convexity Detection & Warnings (Staged Delivery)

**Priority:** HIGH  
**Estimated Effort:** 1.5 sprints (split across Sprints 6–7)  
**Reference:** `docs/research/convexity_detection.md`

#### Motivation
Users need timely warnings when converting nonconvex NLPs to MCPs. We will deliver heuristic detection quickly (Sprint 6) and add deeper AST-based analysis once telemetry proves value (Sprint 7+).

#### Sprint 6 Objectives – Heuristic Layer
- Detect blatant nonconvex patterns (nonlinear equalities, trig functions, bilinear terms, quotients, odd powers).
- Always-on warnings post-parse; `--strict-convexity` flag to fail hard.
- Update docs with do/don’t guidance and examples.

#### Sprint 7 Objectives – AST-Based Analysis (if time allows)
- Optional `--analyze-convexity` pass that classifies expressions using composition rules.
- Detailed report with reformulation hints tied to GAMSLib findings.

#### Success Criteria
- Sprint 6: Heuristic warnings fire on curated nonconvex models without flagging convex cases.
- Sprint 7: AST mode available behind flag, tied to telemetry; documentation includes decision tree for users.

---

### 2. Critical Bug Fixes & Nested Min/Max Support (Frontloaded)

**Priority:** HIGH  
**Estimated Effort:** 1 sprint (S6) + spillover (S7)  
**References:** ~~`MAXIMIZE_BOUND_MULTIPLIER_BUG.md`~~ (no bug exists), `NESTED_MINMAX_REQUIREMENTS.md`

#### Objectives
- ~~**Maximize bound multiplier sign bug:** Fix stationarity sign handling for maximize objectives; add regression tests.~~ **REMOVED** - No bug exists (verified 2025-11-12)
- **Nested min/max flattening:** Implement Option A flattening plus roadmap for Option B; ship tests + PATH validation.
- Bundle both fixes with the convexity sprint to reuse reformulation/test scaffolding.

#### Success Criteria
- All maximize/minimize regression suites green.
- Nested min/max research cases convert/solve; no “function not supported” errors.
- Known-blocker backlog cleared before new parser work.

---

### 3. GAMSLib NLP Validation (Pulled Forward & Continuous)

**Priority:** HIGH  
**Estimated Effort:** Sprints 6–8 (overlapping other work)

#### Sprint 6 Initiatives
- Automate download + catalog of targeted GAMSLib NLPs.
- Run nightly ingestion, bucket parser errors, and publish initial “parseability” metrics.
- Stand up `tests/fixtures/gamslib/CONVERSION_STATUS.md` dashboard immediately.

#### Sprint 7 Goals
- Prioritize parser enhancements by error frequency from telemetry.
- Target KPI: **≥20 %** of selected GAMSLib models parse successfully by end of Sprint 7.

#### Sprint 8 Goals
- Complete top parser features, add nested min/max Option B if needed, wire conversion pipeline.
- KPIs: **≥50 %** parse, **≥30 %** convert; start PATH solve tracking.

#### Ongoing
- Track parse/convert/solve metrics each sprint retro.
- Use telemetry to drive documentation (unsupported features, workarounds) and to tune convexity warnings.

---

### 4. Aggressive Algebraic Simplification (Data-Driven)

**Priority:** MEDIUM  
**Estimated Effort:** Sprint 9 (dependent on telemetry)

#### Preconditions
- Performance dashboard established by end of Sprint 8 (based on GAMSLib runs).
- Simplification KPIs defined (e.g., 20 % derivative reduction on tracked models).

#### Objectives
- Implement `--simplification aggressive` rules + optional CSE.
- Provide metrics (`--simplification-stats`) and regression tests tied to GAMSLib benchmarks.
- Ensure FD validation and PATH results match baseline.

#### Success Criteria
- Demonstrated simplification benefit on ≥50 % of benchmark models without correctness regressions.
- Performance dashboards updated automatically in CI.

---

### 5. Enhanced User Experience (Incremental Each Sprint)

**Priority:** MEDIUM  
**Estimated Effort:** 0.5 sprint capacity per iteration (Sprints 6–10)

#### Rolling Objectives
- **Sprint 6–7:** Improve parser/convexity error copy, add line/column context, link to docs.
- **Sprint 7–8:** Introduce lightweight progress indicators and initial `--stats` output while parser work evolves.
- **Sprint 9–10:** Expand to diagnostics mode, detailed stats dashboard, and final polish.

#### Success Criteria
- UX improvements land every sprint (track via sprint demo checklist).
- By Sprint 10, diagnostics/progress features satisfy original Goal 5 vision without last-minute crunch.

---

### 6. Documentation Enhancements (Parallel Track)

**Priority:** MEDIUM  
**Estimated Effort:** Continuous

- Align documentation drops with feature availability (e.g., convexity guide in Sprint 6, GAMSLib handbook Sprint 8).
- Add rolling updates to `docs/GAMSLIB_EXAMPLES.md`, `docs/ADVANCED_USAGE.md`, API docs and video scripts.

---

### 7. Quality, KPIs & Regression Guardrails

**Priority:** HIGH  
**Estimated Effort:** Ongoing

#### Sprint-Level KPIs
- **S6:** Convexity heuristics shipped, ≥10 GAMSLib models ingested nightly.
- **S7:** Parser coverage ≥20 %, conversion dashboard live.
- **S8:** Parser ≥50 %, conversion ≥30 %; performance dashboard auto-updated.
- **S9:** Simplification metrics integrated into CI; PATH smoke tests sample GAMSLib models.
- **S10:** UX/diagnostics complete; v1.0.0 release criteria met.

#### Regression Automation
- Expand CI with GAMSLib sampling, PATH smoke runs (where licensing allows), coverage/performance reporting.
- Flag regressions on dashboards and require mitigations before release tagging.

---

## Revised Sprint Breakdown

### Sprint 6 (Weeks 1–2): Convexity Heuristics, High-Severity Bugs, GAMSLib Bootstrapping, Initial UX polish
- Ship heuristic convexity warnings + CLI flags.
- ~~Fix maximize-bound multiplier bug and~~ nested min/max flattening.
- Automate GAMSLib downloads, run nightly ingestion, publish initial dashboard (goal: ≥10 models processed, ≥10 % parse success).
- Improve error messaging for new warnings + parser failures.
- **Deliverable:** v0.6.0 (convexity warnings, bug fixes, GAMSLib ingestion tooling, initial UX upgrades).

### Sprint 7 (Weeks 3–4): Parser Enhancements Wave 1, Convexity AST Pass (if feasible), UX iteration, KPIs tracking
- Prioritize parser features based on telemetry; push coverage to ≥20 %.
- Optional AST-based convexity pass (behind flag) leveraging real models.
- Update conversion dashboard with parse/convert metrics; integrate PATH smoke target for easy models.
- Add lightweight progress indicators and context-rich errors for new syntax.
- **Deliverable:** v0.7.0 (expanded parser, optional convexity analysis, dashboards with KPIs).

### Sprint 8 (Weeks 5–6): Parser Enhancements Wave 2, Nested min/max Option B (if needed), Conversion/Performance KPIs
- Finish high-priority parser targets (conditional expressions, `.l/.m` attributes, etc.).
- Implement nested min/max Option B if telemetry still shows gaps.
- Achieve ≥50 % parse, ≥30 % convert on target GAMSLib set; start logging PATH solve success.
- Stand up automated performance dashboard comparing NLP vs MCP solves; feed data into docs.
- UX: add `--stats` and refined progress indicators informed by real runs.
- **Deliverable:** v0.8.0 (broad parser coverage, nested min/max robustness, conversion + performance KPIs).

### Sprint 9 (Weeks 7–8): Aggressive Simplification + CI Regression Hooks + Continued UX
- Build `--simplification aggressive`, CSE, and metrics instrumentation using earlier benchmarks.
- Wire CI guardrails: PATH smoke subset, GAMSLib sampling, performance alerts.
- Continue UX increments (diagnostics logging, better CLI summaries).
- **Deliverable:** v0.9.0 (aggressive simplification with metrics, regression automation, enhanced diagnostics).

### Sprint 10 (Weeks 9–10): Final UX Polish, Documentation Wrap, Release Readiness, v1.0.0
- Complete diagnostics/progress dashboards, advanced documentation (GAMSLib handbook, advanced usage, video scripts).
- Finalize GAMSLib conversion targets, ensure KPIs hit release thresholds.
- Address remaining bugs from telemetry, execute release checklist.
- **Deliverable:** v1.0.0 (production-grade with documented GAMSLib coverage, UX polish, and guardrails).

---

## Success Metrics (Updated)

- **Parser Coverage:** Sprint KPIs culminating in ≥80 % of targeted GAMSLib NLPs parse; tracked per sprint.
- **Conversion & Solve:** ≥60 % convert, ≥40 % solve by Sprint 10; intermediate KPIs enforced S7–S9.
- **Test Coverage:** ≥90 % maintained; coverage trend reported in CI each sprint.
- **Performance:** Benchmarks recorded S8 onward; aggressive simplification must not increase average conversion time >20 % vs baseline.
- **UX Adoption:** Positive user feedback on convexity warnings, diagnostics, and stats (survey or beta program).

---

## Risks & Mitigations (Reframed)

| Risk | Mitigation | Sprint Timing |
| --- | --- | --- |
| **GAMSLib complexity stalls parser** | Start ingestion Sprint 6, slice features via telemetry, define KPIs per sprint | S6–S8 |
| **Convexity work overruns** | Stage heuristics vs AST, ship heuristics regardless | S6–S7 |
| **Aggressive simplification lacks data** | Delay until S9 with dashboards in place | S7–S9 |
| **UX gets squeezed** | Reserve budget each sprint, track via demo checklist | S6–S10 |
| **Performance regressions unnoticed** | CI dashboards + regression alerts tied to benchmarks | S8–S10 |
| **Scope creep** | Use KPIs/checkpoints to cut/add work; focus on GAMSLib readiness | All |

---

## References (Unchanged)

- Internal research docs (convexity, bug analyses, EPIC 1 summary)
- External: GAMS Model Library, GAMS docs, PATH manual, Boyd & Vandenberghe

---

## Changelog

- **2025-11-10:** Revised goals and sprint plan to incorporate GOALS_REVIEW recommendations (earlier GAMSLib ingestion, staged convexity, bundled bug fixes, rolling UX/perf work, sprint KPIs, CI guardrails).***
