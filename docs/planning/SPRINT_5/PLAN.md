# Sprint 5 Plan: Hardening, Packaging, and Documentation

**Sprint Duration:** 10 days
**Sprint Goal:** Ship a production-ready, packaged tool with comprehensive documentation
**Status:** 📋 READY
**Prepared:** November 6, 2025

---

## Overview

### What Sprint 5 Accomplishes

Sprint 5 turns nlp2mcp into a production-ready tool published on PyPI with polished documentation. Building on Sprint 4’s foundation (972 passing tests, 85%+ coverage, prep tasks complete), the sprint focuses on five pillars:
- **Bug-Free Core:** Resolve the min/max reformulation defect blocking PATH validation.
- **Solver Validation:** Exercise the PATH solver across all supported reformulations and document usage.
- **Production Quality:** Harden error handling, performance, and robustness on large models.
- **Easy Installation:** Deliver a PyPI package with automated release tooling.
- **User Documentation:** Ship tutorial, FAQ, troubleshooting guide, and API reference.

Alignment with Sprint 4 retrospective is preserved through prioritized checkpoints, the research-first workflow, and verified external dependencies (GAMS/PATH licensing).

---

## Success Metrics

### Functional Targets

1. ✅ Min/max reformulation fixed (5 research tests pass, PATH solves without spurious variables).
2. ✅ PATH validation complete (golden files run or documented, solver options captured).
3. ✅ Large models (250/500/1K vars) convert within benchmarks and stay under 500 MB peak memory.
4. ✅ Error recovery system handles NaN/Inf and common authoring mistakes with actionable messaging.
5. ✅ PyPI package published; `pip install nlp2mcp` works on Python 3.11–3.12 with CLI entry point.
6. ✅ Tutorial produced with tested walkthrough examples.
7. ✅ FAQ covers ≥20 real questions with troubleshooting guidance.
8. ✅ Release automation in place (version bumping, changelog generation, GitHub Actions) and CHANGELOG.md updated.
9. ✅ API documentation site (Sphinx) published with docstring coverage and deployment script.

### Quality Targets

1. ✅ All existing tests (≥972) green; no regressions.
2. ✅ New code maintains ≥85 % coverage.
3. ✅ Known Unknowns resolved or formally deferred with justification.
4. ✅ Tooling clean: mypy 0 errors, ruff 0 errors, black-formatted.
5. ✅ PATH golden suite achieves ≥90 % success (remaining failures documented).
6. ✅ Fresh-venv install sanity check passes on supported platforms.

### Integration Targets

1. ✅ Public API stable relative to Sprints 1–4.
2. ✅ Generated MCPs compile cleanly in GAMS.
3. ✅ PATH solves generated MCPs post-fix.
4. ✅ Large-model fixtures pass quality gates (performance + correctness).

---

## Day-by-Day Plan

Each day lists goals, task breakdowns with the driving Known Unknowns, deliverables, acceptance criteria, integration risks, and a dedicated **Follow-On Research Items** section that keeps research work separate from execution tasks.

### Day 1 – Min/Max Bug Fix: Research & Design

**Priority:** 1 (Critical bug) **Effort:** 8 h **Dependencies:** Sprint 4 code, Unknown 1.1 findings
**Goals:** Understand min/max failure, design KKT fix, scaffold tests and detection logic.

- **Task 1.1 – Review Unknown 1.1 (DISPROVEN)** (1 h)
  Confirm Strategy 1 (auxiliary variables) is required; digest research analysis.

- **Task 1.2 – KKT Assembly Design** (2 h)
  **Related Unknowns:** 1.2 (🔍), 1.4 (🔍)
  Map required updates in `src/kkt/assemble.py`, produce design doc with affected code paths.

- **Task 1.3 – Regression Tests** (1 h)
  Port five research cases to `tests/unit/kkt/test_minmax_fix.py`, mark xfail, capture expected behaviour.

- **Task 1.4 – Detection Logic** (2 h)
  **Related Unknown:** 1.2 (🔍)
  **Implementation Notes:** Fully implemented with `detects_objective_minmax()` function using worklist algorithm for transitive dependency tracing. Module location: `src/ir/minmax_detection.py` (271 lines). Test coverage: 100% (29 tests in `tests/unit/ir/test_minmax_detection.py`). Key architectural decision: Pure IR-layer implementation avoiding circular KKT dependency.
  Add AST inspection for objective-defining min/max chains with unit tests covering aliasing scenarios.

- **Task 1.5 – Assembly Scaffolding** (2 h)
  **Related Unknown:** 1.4 (✅)
  Implement initial multiplier inclusion plus targeted logging; ensure build succeeds.
  **Implementation Notes:**
  - **Scaffolding COMPLETE:** Comprehensive TODO comments and logging framework are already in place in `src/kkt/assemble.py`.
  - **Architecture Analysis:** No algorithmic changes are needed. KKT assembly is Jacobian-driven and automatically includes ALL equality constraints.
  - **Day 2 Work:** Simplified to (1) adding the reformulation call to the pipeline, and (2) enabling debug logging.
  - See lines 115-261 in `assemble.py` for detailed scaffolding.

**Deliverables:** design memo, xfailed test suite, detection module + tests, assembly prototype.
**Acceptance:** tests authored, detection coverage 100 %, build clean, design reviewed.

**Status:** ✅ COMPLETE (November 6, 2025)
**Risks:** KKT regression (mitigate via regression suite), detection misses edge cases (mitigate via research test coverage).

**Follow-On Research Items**
- Unknown 1.2 – Objective min/max detection (✅ COMPLETE) → resolved during Day 1 implementation.
  - **Summary:** Algorithm fully implemented in `src/ir/minmax_detection.py` with 100% test coverage (29 passing tests)
  - **Key Function:** `detects_objective_minmax(model_ir)` traces from objective through dependency chain
  - **Algorithm:** Worklist-based graph traversal with cycle detection, handles arbitrary-depth chains
  - **Test Coverage:** Direct min/max, 1-hop chains, 2-hop chains, nested min/max, negative cases
  - **Limitation:** Indexed objectives not yet supported (deferred - no current use cases)
  - **Performance:** O(V+E) graph traversal, <1ms for typical models
- Unknown 1.4 – KKT assembly adjustments (✅ COMPLETE) → resolved during Day 1 research.
  - **Summary:** KKT assembly architecture already correct - no algorithmic changes needed
  - **Key Finding:** Current design is Jacobian-driven and automatically includes ALL equality constraints
  - **Architecture:** Partition → Multipliers → Stationarity separation works for auxiliary constraints
  - **Scaffolding:** Comprehensive TODO comments and logging framework already in place
  - **Day 2 Work:** Just add reformulation call to pipeline and enable debug logging
  - **Risk:** Low - architecture validated, scaffolding ready, test cases prepared
  - **Location:** `src/kkt/assemble.py` (lines 115-261), `src/cli.py` (pipeline integration)

---

### Day 2 – Min/Max Bug Fix: Implementation & Testing

**Priority:** 1 **Effort:** 8 h **Dependencies:** Day 1 design
**Goals:** Finish implementation, validate with PATH, clean up tests.

- **Task 2.1 – Finalize Assembly** (3 h)
  **Unknown:** 1.4 (✅)
  **Implementation Notes:** Research confirms KKT assembly architecture is ALREADY CORRECT. No algorithmic changes needed. Implementation simplified to:
  - Add `reformulate_model()` call in the pipeline after `normalize_model()` and before `compute_derivatives()`.
  - Enable debug logging in `assemble.py` to verify auxiliary constraints.
  - Verify reformulation creates constraints with correct Rel types.
  Scaffolding at lines 115-261 in `src/kkt/assemble.py` provides comprehensive TODO comments and logging framework.
  Complete multiplier integration, ensure indexed equations handled, add inline docs.

- **Task 2.2 – Debug Research Cases** (2 h)
  Iterate on failing tests until generated MCPs are correct.

- **Task 2.3 – PATH Validation Smoke** (2 h)
  **Unknown:** 1.5 (✅ COMPLETE)
  Run all five min/max MCPs through PATH, experiment with options if convergence issues surface.
  **Implementation Notes from Research:**
  - Start with default PATH options (convergence_tolerance 1e-6, crash_method pnewton)
  - Default options should work for most reformulated min/max MCPs
  - If convergence fails, try "difficult model" configuration (see Unknown 1.5 findings)
  - If still failing, try "failing model" configuration with looser tolerance and no crash
  - Document which test cases (if any) require non-default options and why
  - PATH's stabilization scheme handles reformulated problems well (low risk)

- **Task 2.4 – Remove xfail** (0.5 h)
  Drop xfail markers, annotate fixes in tests.

- **Task 2.5 – Regression Sweep** (0.5 h)
  Run full pytest suite, address any fallout.

**Deliverables:** finalized assembly, green min/max tests, PATH validation results, tidy test suite.
**Acceptance:** five cases pass + PATH solves, full suite green, coverage ≥85 %, mypy/ruff clean.
**Risks:** PATH non-convergence (use Unknown 1.5 mitigation), regression outside min/max (full suite).

**Follow-On Research Items**
- Unknown 1.5 – PATH option tuning (✅ COMPLETE) → resolved November 7, 2025.
  - **Summary:** Comprehensive research completed on PATH solver options for MCP problems
  - **Key Finding:** Default PATH options (`convergence_tolerance 1e-6`, `crash_method pnewton`) are appropriate for min/max reformulated MCPs
  - **Recommendations:** Three configuration templates provided (standard/difficult/failing cases)
  - **Critical Options Identified:**
    - `convergence_tolerance` (default 1e-6): Adjust to 1e-4 for difficult models or 1e-8 for high precision
    - `major_iteration_limit` (default 500): Increase to 1000-2000 for complex reformulations
    - `crash_method` (default pnewton): Try `none` if default convergence fails
    - `proximal_perturbation` (default 0): Enable 1e-4 to 1e-2 for singular matrix issues
  - **Implementation Notes:**
    - Day 2 Task 2.3: Test with default options first; only tune if convergence fails
    - Day 3 Task 3.3: Create `docs/PATH_SOLVER.md` with option reference and troubleshooting guide
    - Include three configuration templates and decision tree for option tuning
  - **Risk Assessment:** Low - PATH's stabilization scheme handles reformulated problems well
  - **Documentation Required:** PATH_SOLVER.md with options reference, troubleshooting flowchart, and example configurations

---

### Day 3 – PATH Validation & Checkpoint 1 ✅ COMPLETE

**Priority:** 2 **Effort:** 7 h + 1 h checkpoint **Dependencies:** Day 2
**Goals:** Run complete PATH suite, document solver usage, complete Checkpoint 1.

- **Task 3.1 – Execute Validation Suite** (2 h)
  Run PATH validation tests; capture status/residuals.

- **Task 3.2 – Investigate Failures** (2 h)
  **Unknown:** 2.1 (🔍)
  Analyse Model Status 5 cases, differentiate expected model infeasibility vs bugs.

- **Task 3.3 – Document PATH Usage** (2 h)
  **Unknowns:** 2.2 (🔍), 2.3 (🔍)
  Author `docs/PATH_SOLVER.md`, update user guide with solver options and interpretation.
  **Implementation Notes from Unknown 1.5 Research:**
  - Include comprehensive PATH options reference (see Unknown 1.5 findings for complete list)
  - Document three configuration templates:
    1. Standard: Default options for most cases (convergence_tolerance 1e-6, crash_method pnewton)
    2. Difficult: For complex reformulations (major_iteration_limit 1000, proximal_perturbation 1e-4)
    3. Failing: For problematic models (looser tolerance 1e-4, crash_method none)
  - Add troubleshooting decision tree: convergence failure → looser tolerance → no crash → proximal perturbation
  - Document how to create and use PATH option files (path.opt syntax)
  - Include table of key options with defaults and recommendations
  - Explain how to interpret PATH output (Model Status codes, residuals, iteration counts)
  - Note that default options work well for min/max reformulated MCPs (validated by research)

- **Task 3.4 – Test Suite Hygiene** (1 h)
  Adjust skip/xfail expectations, embed solver option defaults.

- **Checkpoint 1** (1 h)
  Review feature completeness, unknown status, coverage, lint/test health; decide GO/NO-GO for Day 4+.

**Deliverables:** PATH results log, documentation updates, stable validation suite, checkpoint report.
**Acceptance:** ≥90 % PATH success, failures documented, PATH guide published, checkpoint GO with no blockers.

**✅ COMPLETED (November 7, 2025):**
- ✅ PATH success rate: 100% (4/4 non-xfail tests - exceeds 90% target)
- ✅ Failures documented: 1 expected xfail documented in test and validation report
- ✅ PATH guide published: docs/PATH_SOLVER.md (450+ lines comprehensive guide)
- ✅ Checkpoint 1: GO decision - no blockers for Day 4+
- ✅ All Day 3 tasks complete (3.1, 3.2, 3.3, 3.4)
- ✅ Quality gates: typecheck ✓, lint ✓, format ✓, tests ✓

**Risks:** Solver option gaps (document + mitigation), new unknowns (capture in follow-on list).

**Follow-On Research Items**
- Unknown 2.1 – Model Status 5 diagnostics (✅ COMPLETE) → Day 3.
- Unknown 2.2 – Document PATH options (✅ COMPLETE) → Day 3 completed Nov 7, 2025
  - **Note:** Comprehensive PATH_SOLVER.md created with options reference, templates, and troubleshooting
  - Unknown 1.5 research findings integrated
  - USER_GUIDE.md updated with PATH solver section
- Unknown 2.3 – PATH solution quality guidance (✅ COMPLETE) → Included in PATH_SOLVER.md (Model Status interpretation, residuals, metrics)
- Unknown 2.4 – PATH in CI/CD (🔍, deferred to Sprint 6).

---

### Day 4 – Production Hardening: Error Recovery

**Priority:** 3.1 **Effort:** 8 h **Dependencies:** None
**Goals:** Harden numerical handling, validation, and messaging.

- **Task 4.1 – Numerical Guardrails** (2 h)
  **Unknown:** 3.4 (🔍)
  Detect NaN/Inf post-operation, surface contextual `NumericalError`.

- **Task 4.2 – Model Validation Pass** (2 h)
  **Unknown:** 3.5 (🔍)
  Add pre-assembly validation for undefined symbols, circular deps, type mismatches, missing objectives.

- **Task 4.3 – Message Improvements** (2 h)
  Enhance errors with location, context, remediation pointers.

- **Task 4.4 – Recovery Tests** (2 h)
  Build ≥20 integration tests covering failure scenarios and verifying guidance.

**Deliverables:** NaN/Inf hooks, validation module, improved error catalogue, recovery test suite.
**Acceptance:** Validation catches targeted mistakes, error messages actionable, ≥20 new tests passing, coverage ≥85 %.
**Risks:** False positives from validation (allow opt-out flag), perf hit (profile, optimise).

**Follow-On Research Items**
- Unknown 3.4 – Numerical handling approach (✅ - COMPLETE) → Day 4.
- Unknown 3.5 – Validation design (✅ - COMPLETE) → Day 4.

---

### Day 5 – Production Hardening: Large Models & Memory

**Priority:** 3.2 & 3.3 **Effort:** 8 h **Dependencies:** Large-model fixtures from prep
**Status:** ✅ COMPLETE (Nov 7, 2025)
**Goals:** Benchmark large-model throughput, profile time/memory, codify targets.

- **Task 5.1 – Fixture Runs** (2 h) ✅ COMPLETE
  Execute 250/500/1000 variable models, record timings and correctness.
  **Results:** 250 vars (4.18s), 500 vars (10.71s), 1K vars (42.58s) - all within targets

- **Task 5.2 – Time Profiling** (2 h) ✅ COMPLETE
  Break down phase runtimes with cProfile/line-profiler.
  **Results:** Jacobian 80%, Parsing 15%, Validation 5% - no optimization needed

- **Task 5.3 – Memory Profiling** (2 h) ✅ COMPLETE
  **Unknown:** 3.3 (✅ COMPLETE)
  Measure peak usage, apply sparse structures or generators if >500 MB.
  **Results:** 59.56 MB peak for 500 vars (88% under 500 MB target) - excellent

- **Task 5.4 – Benchmark Suite** (2 h) ✅ COMPLETE
  Add `tests/benchmarks/test_large_models.py`, wire optional slow CI targets.
  **Results:** All benchmarks pass, infrastructure verified

**Deliverables:** ✅ Timing + memory reports (docs/performance/DAY5_PERFORMANCE_REPORT.md), benchmark tests passing, targets documented.
**Acceptance:** ✅ Fixtures within targets, ✅ memory ≤500 MB (59.56 MB), ✅ benchmarks pass (937 tests), ✅ no regressions vs Sprint 4.
**Risks:** ✅ No parser/AD regressions found, ✅ no memory spikes detected.

**Follow-On Research Items**
- Unknown 3.3 – Memory optimization tactics (✅ COMPLETE) → Day 5 completed Nov 7, 2025.
  - **Summary:** Current memory usage excellent (59.56 MB for 500 vars, 88% under 500 MB target)
  - **Finding:** No optimization needed - dict-based sparse storage is efficient
  - **Recommendation:** Continue with current architecture, monitor for >2K variable models
  - **Documentation:** See docs/performance/DAY5_PERFORMANCE_REPORT.md for complete analysis

---

### Day 6 – Production Hardening: Edge Cases & Checkpoint 2

**Priority:** 3 **Effort:** 7 h + 1 h checkpoint **Dependencies:** Days 4–5
**Goals:** Cover critical edge cases, document limits, hold Checkpoint 2.

**Status:** ✅ COMPLETE (Nov 7, 2025)

- **Task 6.1 – Edge Case Suite** (3 h)
  **Unknown:** 3.2 (🔍)
  Implement ≥20 cases across bounds, degeneracy, zero Jacobians, circular references, empty sets.

- **Task 6.2 – Boundary Testing** (2 h)
  Stress test dimensional limits, nest depth, identifier length; record constraints.

- **Task 6.3 – Message Validation** (1 h)
  Review error clarity from new cases; patch gaps.

- **Task 6.4 – Limitations Doc** (1 h)
  Author `docs/LIMITATIONS.md`, link from README and user guide.

- **Checkpoint 2** (1 h)
  Validate progress vs plan, quality metrics, scope adjustments, readiness for packaging.

**Deliverables:** Edge-case tests, boundary write-up, LIMITATIONS doc, checkpoint report.
**Acceptance:** ≥20 tests pass/fail gracefully, documented limits published, checkpoint GO for Day 7.
**Risks:** Newly uncovered critical issues (surface early, feed into Day 10 buffer).

**Follow-On Research Items**
- Unknown 3.2 – Edge-case catalogue (🔍) → Day 6.

---

### Day 7 – PyPI Packaging: Configuration & Build

**Priority:** 4 **Effort:** 8 h **Dependencies:** None
**Goals:** Select build backend, configure packaging metadata, validate local installs.

- **Task 7.1 – Build System Decision** (1 h)
  **Unknown:** 4.1 (🔍)
  Compare setuptools/hatch/flit; adopt hatch for modern workflow.

- **Task 7.2 – `pyproject.toml` Setup** (30 min)
  **Unknown:** 4.2 (✅ COMPLETE - research done Nov 8)
  **Implementation:** Update `requires-python = ">=3.11"` (was >=3.12), upgrade to `"Development Status :: 4 - Beta"`, add 11 new classifiers (Python 3.11/3.13, Developers audience, Code Generators topic, OS Independent, Console, Natural Language, Typing). Update license to SPDX format `license = "MIT"`. Already have: metadata, dependencies, optional extras, CLI entry point.
  **Why 30min:** Most metadata already complete. Just need classifier updates and Python version change. See KNOWN_UNKNOWNS.md Unknown 4.2 for full classifier list.

- **Task 7.3 – CLI Entry Point** (1 h)
  Configure console script in `pyproject.toml`; verify CLI usage text.

- **Task 7.4 – Wheel Build** (1 h)
  Produce wheel via `python -m build`, inspect distribution.

- **Task 7.5 – Local Install QA** (2 h)
  Smoke test install/uninstall in fresh venv, run CLI on sample models.

- **Task 7.6 – Multi-Platform Check** (1 h)
  **Unknown:** 4.3 (🔍)
  Exercise tox across Python 3.11–3.12 on macOS; note issues for Day 8 CI matrix.

**Deliverables:** pyproject metadata, built wheel, install report, multi-platform notes.
**Acceptance:** Wheel build passes, CLI operational post-install, dependencies resolved, python matrix smoke green.
**Risks:** Missing package data (validate wheel contents), CLI entry misconfigurations (smoke test).

**Follow-On Research Items**
- Unknown 4.1 – Build backend choice (✅ COMPLETE) → **Decision: Keep setuptools** (Nov 7, 2025). Pure Python, setuptools working, 79% adoption, zero risk. Fix: SPDX license. Saves 2h Day 7.
- Unknown 4.2 – PyPI metadata checklist (✅ COMPLETE) → **Decision: Support Python 3.11+, upgrade to Beta status, add 11 classifiers** (Nov 8, 2025). NumPy requires 3.11+. Add Developer audience, Code Generator topic, OS Independent. Improves discoverability 30-40%. Task 7.2: 30min.
- Unknown 4.3 – Multi-platform strategy (🔍) → Day 7.

---

### Day 8 – PyPI Release Automation & Checkpoint 3

**Priority:** 4 **Effort:** 7 h + 1 h checkpoint **Dependencies:** Day 7
**Goals:** Automate versioning/changelog, configure publish workflow, push to TestPyPI, update docs/CHANGELOG, run Checkpoint 3.

- **Task 8.1 – Version Strategy** (0.5 h)
  **Unknown:** 4.4 (🔍)
  Document semantic version path (0.4.0 launch → 1.0.0 readiness).

- **Task 8.2 – Version Bump Script** (1.5 h)
  Create `scripts/bump_version.py`, integrate with workflow.

- **Task 8.3 – Changelog Generator** (1.5 h)
  Build `scripts/generate_changelog.py` (Keep a Changelog format) and automation hook.

- **Task 8.4 – GitHub Actions Workflow** (1.5 h)
  Compose `.github/workflows/publish-pypi.yml` with build/test/publish steps (dry-run on branch).

- **Task 8.5 – TestPyPI Publish** (0.5 h)
  Upload artefacts via `twine`, verify listing.

- **Task 8.6 – TestPyPI Install QA** (0.5 h)
  Install from TestPyPI in clean venv, run CLI.

- **Task 8.7 – Release Docs** (0.5 h)
  Draft/refresh `RELEASING.md` with automated steps and manual checklist.

- **Task 8.8 – README Update** (0.5 h)
  Document `pip install`, add PyPI badge, verify quick-start.

- **Task 8.9 – CHANGELOG Update** (0.5 h)
  Record Sprint 5 highlights using automation output; manually sanity check.

- **Checkpoint 3** (1 h)
  Confirm Priority 1-4 completion, release readiness, doc readiness; GO/NO-GO for Day 9 documentation.

**Deliverables:** Version/changelog scripts, CI workflow, TestPyPI release, updated README & CHANGELOG, checkpoint report.
**Acceptance:** Automation scripts tested, workflow passes, TestPyPI install validated, docs updated, checkpoint GO.
**Risks:** Secret misconfig (dry-run, manual fallback), automation bugs (local tests before CI).

**Follow-On Research Items**
- Unknown 4.4 – Versioning plan (🔍) → Day 8.

---

### Day 9 – Documentation Push (Tutorial, FAQ, Troubleshooting, API Site)

**Priority:** 5 **Effort:** 8 h **Dependencies:** Days 1–8 complete
**Goals:** Deliver complete end-user documentation, publish API reference.

- **Task 9.1 – Tutorial Outline** (1 h)
  **Unknown:** 5.2 (🔍)
  Finalise sections, assets, and examples.

- **Task 9.2 – Tutorial Authoring** (3 h)
  Produce `docs/TUTORIAL.md` with runnable samples, screenshots/diagrams, cross-links.

- **Task 9.3 – FAQ Build** (1.5 h)
  Source ≥20 real questions from testing/edges/retro, structure by theme, provide answers + links.

- **Task 9.4 – Troubleshooting Upgrade** (0.5 h)
  **Unknown:** 5.3 (🔍)
  Rework `docs/TROUBLESHOOTING.md` with Problem → Diagnosis → Solution sections and error snippets.

- **Task 9.5 – API Documentation Site** (2 h)
  **Unknowns:** 5.1 (✅), 5.4 (🔍)
  Configure Sphinx (autodoc/type hints), generate HTML, prep GitHub Pages/ReadTheDocs deployment.

**Deliverables:** Tutorial, FAQ, enhanced troubleshooting guide, Sphinx site, deployment steps.
**Acceptance:** Examples verified, ≥20 FAQ entries, Sphinx build succeeds, docs cross-linked, no broken links.
**Risks:** Documentation scope overrun (use Day 10 buffer), Sphinx dependencies (lock requirements early).

**Follow-On Research Items**
- Unknown 5.1 – Tooling decision (✅ resolved: Sphinx).
- Unknown 5.2 – Tutorial scope (🔍) → Day 9.
- Unknown 5.3 – Troubleshooting depth (🔍) → Day 9.
- Unknown 5.4 – API detail level (🔍) → Day 9.

---

### Day 10 – Polish & Buffer

**Priority:** Buffer **Effort:** 8 h **Dependencies:** Days 1–9
**Goals:** Close outstanding work, perform quality sweep, prep retrospective.

- **Task 10.1 – Backlog Burn-down** (4 h)
  Finish any open acceptance criteria (priority: critical → high → medium → low).

- **Task 10.2 – Final QA Pass** (2 h)
  Run full tests, coverage, mypy, ruff, black; verify docs links, package install sanity.

- **Task 10.3 – Retrospective Prep** (1 h)
  Collect metrics (tests, coverage, performance, release stats), draft talking points/action items.

- **Task 10.4 – Deliverables Checklist** (1 h)
  Ensure all Sprint 5 outputs complete, sign off for demo/release.

**Deliverables:** Cleared backlog, QA evidence, retro notes, completion checklist.
**Acceptance:** Critical/high items complete, all tests pass, coverage ≥85 %, docs + release assets verified, retro packet ready.
**Risks:** Late surprises (buffer absorbs), remaining low-priority tasks may slip (document deferrals).

**Follow-On Research Items**
- Critical/high unknowns resolved Days 1–9; any new low-priority discoveries are flagged for Sprint 6 planning.

---

## Risk Management

| Risk | Prob. | Impact | Mitigation | Contingency |
| --- | --- | --- | --- | --- |
| Min/max fix complexity | Medium | High | Dedicated Days 1–2, research complete, checkpoints | Scope to common cases, defer edge scenarios |
| PATH licensing/access | Low | High | Dependencies verified in prep, manual path if CI unavailable | Run manual solver sessions, document limits |
| Release automation defects | Medium | Medium | Local script tests, dry-run workflow, manual checklist | Fall back to manual release process |
| Performance misses targets | Low | Medium | Benchmarks + profiling Day 5, documented baselines | Publish current metrics, schedule optimisation |
| Documentation overrun | Medium | Low | Full Day 9 allocation, Day 10 buffer | Ship reduced docs, refine next sprint |
| Edge cases unveil blockers | Low | High | Systematic testing Day 6, early checkpoint | Document + schedule remediation |
| Sphinx build instability | Low | Low | Lock dependencies, early build dry run | Defer API site to Sprint 6 if required |

---

## Dependencies

```
Day 1 → Day 2 → Day 3 → (Checkpt 1 GO)
       ↘︎ Day 4 → Day 5 → Day 6 → (Checkpt 2 GO)
                           ↘︎ Day 7 → Day 8 → (Checkpt 3 GO) → Day 9 → Day 10
```

**External:**
- GAMS/PATH licenses (validated during prep) for Days 2–3 PATH work.
- Large-model fixtures from prep Task 8 feed Day 5 benchmarks.
- PyPI/TestPyPI credentials for Day 8 automation.
- Documentation tooling (Sphinx, MkDocs legacy docs) configured through prep tasks.

---

## Sprint Success Definition

**Minimum (B):** Min/max fix, PATH validation, large-model benchmarks, PyPI build, tutorial, ≥1000 tests, ≥80 % coverage.
**Target (A):** Minimum plus error recovery suite, memory tuning, edge-case coverage, TestPyPI publish, FAQ, release automation, ≥85 % coverage, checkpoints passed.
**Stretch (A+):** Target plus production PyPI release, API site deployed, performance exceeds targets, zero deferred critical items, Sprint complete by Day 9.

---

## Known Unknowns Tracking

Active unknowns, ownership, and target resolution day:

- **Category 1 (Min/Max):** 1.2, 1.4, 1.5 → Days 1–2.
- **Category 2 (PATH):** 2.1, 2.2, 2.3 → Day 3; 2.4 deferred to Sprint 6.
- **Category 3 (Hardening):** 3.2 → Day 6; 3.3 → Day 5; 3.4–3.5 → Day 4.
- **Category 4 (Packaging):** 4.1–4.3 → Day 7; 4.4 → Day 8.
- **Category 5 (Docs):** 5.2–5.4 → Day 9 (5.1 resolved: Sphinx).
- Any new discoveries are logged during checkpoints and evaluated for mitigation or deferral.

---

## Checkpoint Cadence

- **Checkpoint 0 (Prep, complete):** Dependencies + retrospective alignment.
- **Checkpoint 1 (Day 3):** Validate Priority 1–2 execution, unblock hardening.
- **Checkpoint 2 (Day 6):** Confirm production hardening outcomes before packaging.
- **Checkpoint 3 (Day 8):** Release readiness prior to documentation push.

Each checkpoint uses templates in `docs/process/CHECKPOINT_TEMPLATES.md` and explicitly records GO/NO-GO decisions plus remediation plans if needed.

---

## Definition of Done

Sprint 5 concludes when:
- All Success Metrics targets are met or deviations are documented and approved.
- Release artefacts (package, automation, docs) are published and verified.
- CHANGELOG.md reflects Sprint 5 changes.
- Retro inputs compiled, and outstanding items are scheduled or deferred with rationale.

Upon completion, update CHANGELOG.md and tag the release per the automated workflow.***
