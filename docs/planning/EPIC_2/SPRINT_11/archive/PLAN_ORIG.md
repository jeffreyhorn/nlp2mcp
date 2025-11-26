# Sprint 11 Detailed Plan

**Sprint Duration:** 10 working days (2 weeks)  
**Sprint Goal:** Aggressive Simplification + CI Regression Guardrails + Diagnostics  
**Sprint Theme:** "Quality Infrastructure & Optimization"  
**Target:** ≥20% derivative term reduction on ≥50% of benchmark models  
**Status:** PLANNED  
**Total Effort:** 27.5-28.5 hours budgeted (baseline 25.5-26.5h + IPOPT 2h)

---

## Executive Summary

This plan implements a **quality-focused, infrastructure-strengthening approach** for Sprint 11 based on comprehensive prep task analysis (Tasks 1-11). Key decisions:

1. **Primary Features (MUST-Have):**
   - **Aggressive Simplification** (12.5h) - 6 HIGH-priority transformations
   - **CI Regression Guardrails** (9h) - Matrix builds, performance baselines, multi-metric thresholds
   - **Diagnostics Mode** (4-5h) - Text-based timing and metrics

2. **Secondary Feature (If Time Permits):**
   - **IPOPT Prototype** (2h) - Open-source MCP solver for CI validation

3. **Deferred to Sprint 12:**
   - Nested/Subset Indexing (maxmin.gms) - 10-14h, HIGH complexity
   - CSE Advanced Features (T5.2-T5.4) - 6h
   - PATH CI Integration - 6-8h (licensing unclear)
   - Aggressive Simplification MEDIUM priority - 2h
   - JSON Diagnostics - 2h

**Scope Decision:** Baseline (25.5-26.5h) + IPOPT (2h) = **27.5-28.5h (92-95% capacity utilization)**

**Confidence:** 90% (all features are low-risk with strong research foundation)

---

## Sprint 11 Goals

### Primary Goals

1. **Aggressive Simplification:**
   - Implement 8-step transformation pipeline
   - Achieve ≥20% derivative term reduction on ≥50% of benchmark models
   - Safety heuristics: 150% size budget, automatic rollback
   - Performance overhead <10%

2. **CI Regression Guardrails:**
   - Matrix builds for parallelization (10 min → 2-3 min)
   - Performance baseline tracking (rolling + golden baselines)
   - Multi-metric thresholds (parse, convert, performance)
   - Per-PR reporting with deltas

3. **Diagnostics Mode:**
   - Stage-level timing (5 pipeline stages)
   - Simplification pass breakdowns (8 passes)
   - Memory tracking per stage
   - Text table output with 3 verbosity levels

### Secondary Goals (If Time Permits)

4. **IPOPT Prototype:**
   - Install IPOPT in CI environment
   - Implement Fischer-Burmeister reformulation
   - Validate accuracy on 3 GAMSLib models
   - Create nightly smoke test workflow

### Success Criteria

- [ ] Aggressive simplification reduces terms by ≥20% on ≥50% of models
- [ ] CI workflow runs on every PR in <3 minutes
- [ ] Performance baselines tracked with 20%/50% thresholds
- [ ] Diagnostics validated on representative models
- [ ] All tests pass with ≥95% coverage maintained
- [ ] No regressions in existing functionality

---

## Effort Summary

| Feature | Effort (Hours) | Priority | Sprint 11 Status |
|---------|----------------|----------|------------------|
| **Aggressive Simplification (HIGH)** | 12.5 | P0 | ✅ PRIMARY |
| ├─ Pipeline infrastructure (3 passes) | 3.0 | P0 | ✅ MUST |
| ├─ Factoring transformations | 3.5 | P0 | ✅ MUST |
| ├─ Associativity & division | 3.0 | P0 | ✅ MUST |
| └─ Variable cancellation & testing | 3.0 | P0 | ✅ MUST |
| **CI Regression Guardrails** | 9.0 | P0 | ✅ PRIMARY |
| ├─ GAMSLib matrix builds | 4.0 | P0 | ✅ MUST |
| ├─ Performance baselines | 3.0 | P0 | ✅ MUST |
| └─ Multi-metric thresholds | 2.0 | P0 | ✅ MUST |
| **Diagnostics Mode (text tables)** | 4-5 | P1 | ✅ PRIMARY |
| **IPOPT Prototype** | 2.0 | P1 | ⚠️ SECONDARY |
| **TOTAL BASELINE** | **25.5-26.5** | | **85-88% capacity** |
| **TOTAL WITH IPOPT** | **27.5-28.5** | | **92-95% capacity** |

**Deferred Features:**
- Nested Indexing (maxmin.gms): 10-14h → Sprint 12
- CSE Advanced (T5.2-T5.4): 6h → Sprint 12
- PATH CI Integration: 6-8h → Sprint 12
- Simplification MEDIUM priority: 2h → Sprint 12
- JSON Diagnostics: 2h → Sprint 12

---

## Day-by-Day Schedule

### Overview

| Day | Focus | Deliverables | Hours | Milestone |
|-----|-------|--------------|-------|-----------|
| 1 | CI matrix builds + convert tracking | Matrix workflow, convert_rate metric | 4h | CI foundation |
| 2 | Performance baselines + thresholds | Baseline storage, comparison script | 5h | CI complete |
| 3 | Simplification pipeline (start) | Pipeline class, 3 basic passes | 3h | Pipeline foundation |
| 4 | Factoring transformations | Common factor, fraction combining | 3.5h | High-value transforms |
| 5 | Associativity & division | Associative regrouping, division simplify | 3h | **MID-SPRINT CHECKPOINT** |
| 6 | Variable cancellation + testing | Cancellation detection, benchmarking | 3h | Simplification complete |
| 7 | Diagnostics mode (implementation) | Stage timing, breakdowns, memory | 2.5h | Diagnostics foundation |
| 8 | Diagnostics mode (formatting) | Text tables, 3 verbosity levels | 2h | Diagnostics complete |
| 9 | IPOPT prototype + integration tests | IPOPT install, smoke tests, integration | 4h | Full integration |
| 10 | Documentation + retrospective | Update docs, run tests, retrospective | 3h | Sprint complete |

**Critical Path:** Days 1-2 (CI) → Days 3-6 (Simplification) → Days 7-8 (Diagnostics) → Day 10 (Complete)

---

## Detailed Daily Schedule

### **Day 1: CI Matrix Builds + Convert Rate Tracking**

**Date:** TBD  
**Goal:** Enable parallel CI testing and track conversion success rate  
**Effort:** 4 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Tasks

**Task 1.1: Add matrix build to GAMSLib regression workflow (2h)**
- File: `.github/workflows/gamslib-regression.yml`
- Add matrix strategy for 10 Tier 1 models:
  ```yaml
  strategy:
    matrix:
      model: [circle, himmel16, hs62, mathopt1, maxmin, mhw4d, mhw4dx, mingamma, rbrock, trig]
  ```
- Parallelize model testing (10 models × 1 min = 10 min → 2-3 min total)
- Add job consolidation step for aggregate results

**Task 1.2: Add convert_rate tracking (1.5h)**
- Modify `scripts/measure_parse_rate.py`:
  - Add `measure_convert_rate()` function
  - Track parse success + IR generation + MCP generation
  - Output both parse_rate and convert_rate
- Update baseline format to include both metrics
- Test on all 10 Tier 1 models

**Task 1.3: Add PR comment reporting (30 min)**
- File: `.github/workflows/gamslib-regression.yml`
- Add step to post summary table as PR comment:
  ```
  | Metric | Main | PR | Delta |
  |--------|------|----|----- |
  | Parse Rate | 90% | 90% | 0% ✅ |
  | Convert Rate | 80% | 85% | +5% ✅ |
  ```
- Include per-model status (pass/fail/degraded)

#### Deliverables

- [ ] Matrix build workflow running (2-3 min total CI time)
- [ ] Convert rate tracked alongside parse rate
- [ ] PR comment reporting implemented
- [ ] Tested on sample PR

#### Dependencies

- None (infrastructure work)

#### Acceptance Criteria

- [ ] CI workflow completes in <3 minutes (down from 10 min)
- [ ] Both parse_rate and convert_rate reported
- [ ] PR comment shows metrics with deltas vs main branch
- [ ] All quality checks pass

#### Risks

**Risk:** Matrix build configuration errors  
**Mitigation:** Test workflow on feature branch before merging  
**Fallback:** Keep sequential builds if matrix fails, debug later

---

### **Day 2: Performance Baselines + Multi-Metric Thresholds**

**Date:** TBD  
**Goal:** Track performance regressions and enforce quality thresholds  
**Effort:** 5 hours  
**Risk:** LOW  
**Confidence:** 90%

#### Tasks

**Task 2.1: Create baseline storage structure (1.5h)**
- Create `baselines/` directory structure:
  ```
  baselines/
    performance/
      rolling/         # Latest from main branch
      golden/          # Sprint milestones
    parse_rate/        # Git-tracked
  ```
- Set up git-lfs for performance baselines (large files)
- Create baseline format (JSON):
  ```json
  {
    "sprint": 11,
    "date": "2025-12-XX",
    "models": {
      "circle.gms": {"parse_time_ms": 45, "convert_time_ms": 120},
      ...
    }
  }
  ```

**Task 2.2: Implement comparison script (1.5h)**
- File: `scripts/compare_performance.py`
- Compare current run vs rolling baseline
- Calculate deltas for each model
- Apply thresholds:
  - 20% warning (log warning but pass)
  - 50% failure (fail CI check)
- Account for variance (statistical tolerance)

**Task 2.3: Add multi-metric thresholds (1h)**
- File: `.github/workflows/gamslib-regression.yml`
- Add threshold checks:
  - Parse rate: 5% warning, 10% failure
  - Convert rate: 5% warning, 10% failure
  - Performance: 20% warning, 50% failure
- Per-model status tracking (pass/warn/fail)

**Task 2.4: Create GitHub Actions job (1h)**
- Add `performance-regression-check` job
- Run comparison script
- Post results as PR comment
- Fail PR if any metric exceeds failure threshold

#### Deliverables

- [ ] Baseline storage structure created
- [ ] Git-lfs configured for performance data
- [ ] Comparison script implemented and tested
- [ ] Multi-metric thresholds enforced in CI
- [ ] GitHub Actions job running

#### Dependencies

- Day 1: Convert rate tracking (needed for thresholds)

#### Acceptance Criteria

- [ ] Performance baselines tracked for all 10 models
- [ ] Comparison script detects regressions accurately
- [ ] Multi-metric thresholds working (parse, convert, performance)
- [ ] PR fails if metrics exceed thresholds
- [ ] All quality checks pass

#### Risks

**Risk:** Git-lfs setup complexity  
**Mitigation:** Use simple JSON files initially, add git-lfs later if needed  
**Fallback:** Git-track performance baselines (small file size)

**Risk:** Variance in CI performance measurements  
**Mitigation:** Run multiple iterations, use median value  
**Fallback:** Increase thresholds (30%/70%) if too noisy

---

### **Day 3: Simplification Pipeline Infrastructure**

**Date:** TBD  
**Goal:** Create transformation pipeline with basic passes  
**Effort:** 3 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Tasks

**Task 3.1: Create SimplificationPipeline class (1h)**
- File: `src/ir/simplification_pipeline.py`
- Class structure:
  ```python
  class SimplificationPipeline:
      def __init__(self, max_iterations=5, size_budget=1.5):
          self.passes = []
          self.max_iterations = max_iterations
          self.size_budget = size_budget
          
      def add_pass(self, pass_fn, priority, name):
          # Add transformation pass
          
      def apply(self, expr, metrics=None):
          # Apply all passes with fixpoint iteration
  ```

**Task 3.2: Implement basic transformation passes (1.5h)**
- **Pass 1: Like-term combination** (T1.2)
  - Combine: `2*x + 3*x → 5*x`
  - Pattern: Same variable, same exponent
- **Pass 2: Common factor extraction** (T1.1)
  - Factor: `a*x + b*x → (a+b)*x`
  - Pattern: Common multiplier
- **Pass 3: Fraction combining** (T1.4)
  - Combine: `a/c + b/c → (a+b)/c`
  - Pattern: Same denominator

**Task 3.3: Add size budget enforcement (30 min)**
- Measure expression size before/after each transformation
- Size metric: count of AST nodes
- Reject transformation if new_size > old_size * 1.5
- Automatic rollback on budget violation

#### Deliverables

- [ ] SimplificationPipeline class implemented
- [ ] 3 basic transformation passes working
- [ ] Size budget enforced
- [ ] Unit tests for each pass

#### Dependencies

- None (builds on existing `simplify()` infrastructure)

#### Acceptance Criteria

- [ ] Pipeline applies transformations in order
- [ ] Fixpoint iteration (max 5 iterations)
- [ ] Size budget prevents explosion
- [ ] All passes tested independently
- [ ] Quality checks pass

#### Risks

**Risk:** Transformation interference (passes conflict)  
**Mitigation:** Test passes in isolation first, then combined  
**Fallback:** Adjust pass ordering if conflicts detected

---

### **Day 4: Factoring Transformations**

**Date:** TBD  
**Goal:** Implement high-value factoring transformations  
**Effort:** 3.5 hours  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Tasks

**Task 4.1: Implement associativity normalization (1h)**
- **Pass 4: Associativity** (T2.1)
- Left-associate additions: `(a+b)+c` → `a+(b+c)`
- Enables like-term detection across nesting
- Preserve semantics (use SymPy associativity rules)

**Task 4.2: Implement division simplification (1h)**
- **Pass 5: Division simplification** (T3.1)
- Simplify: `(a*b)/a → b` (if a ≠ 0)
- Cancel common factors in numerator/denominator
- Add cancellation detection heuristic

**Task 4.3: Implement multi-term factoring (1h)**
- **Pass 6: Multi-term factoring** (T1.3)
- Factor: `a*x*y + b*x*y → (a+b)*x*y`
- Pattern: Multiple common factors
- Use SymPy `factor()` with safety checks

**Task 4.4: Testing and benchmarking (30 min)**
- Unit tests for each transformation
- Test on benchmark models
- Measure term reduction
- Document which models benefit most

#### Deliverables

- [ ] Associativity normalization implemented
- [ ] Division simplification implemented
- [ ] Multi-term factoring implemented
- [ ] Tests pass for all transformations
- [ ] Benchmark results documented

#### Dependencies

- Day 3: Pipeline infrastructure

#### Acceptance Criteria

- [ ] All 3 transformations working correctly
- [ ] No size explosions (budget enforced)
- [ ] Tested on ≥5 benchmark models
- [ ] Term reduction measured
- [ ] Quality checks pass

#### Risks

**Risk:** Division by zero in cancellation  
**Mitigation:** Add symbolic analysis to detect non-zero denominators  
**Fallback:** Conservative heuristic (cancel only literals and named variables)

**Risk:** Factoring creates larger expressions  
**Mitigation:** Size budget rejects transformations that expand  
**Fallback:** Make factoring opt-in if causes issues

---

### **Day 5: Associativity & Division (Advanced)**

**Date:** TBD  
**Goal:** Complete remaining high-priority transformations  
**Effort:** 3 hours  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Tasks

**Task 5.1: Implement variable cancellation (1.5h)**
- **Pass 7: Variable cancellation** (T3.2)
- Cancel: `(x*y)/x → y` (symbolic cancellation)
- Heuristics:
  - Only cancel if variable appears once in numerator
  - Check for non-zero constraints
  - Preserve domain restrictions
- Use SymPy `cancel()` with validation

**Task 5.2: Integration testing (1h)**
- Test all 6 transformations together
- Verify no conflicts between passes
- Test on complex expressions
- Benchmark on all 10 Tier 1 models

**Task 5.3: Mid-Sprint Checkpoint (30 min)**
- Run full test suite
- Measure term reduction on benchmark models
- Expected: ≥20% reduction on ≥3 models
- Document checkpoint results

#### Deliverables

- [ ] Variable cancellation implemented
- [ ] Integration tests pass
- [ ] Benchmark results collected
- [ ] **MID-SPRINT CHECKPOINT COMPLETE**

#### Dependencies

- Days 3-4: All previous transformation passes

#### Acceptance Criteria

- [ ] Variable cancellation working correctly
- [ ] All 6 passes work together without conflicts
- [ ] ≥20% term reduction on ≥3 models (checkpoint target)
- [ ] No size explosions or incorrect transformations
- [ ] Quality checks pass

#### Risks

**Risk:** Checkpoint shows <20% reduction  
**Mitigation:** Analyze which transformations are ineffective, adjust heuristics  
**Contingency:** Adjust target to ≥15% on ≥50% models

---

### **Day 6: Simplification Testing + Benchmarking**

**Date:** TBD  
**Goal:** Comprehensive testing and final validation  
**Effort:** 3 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Tasks

**Task 6.1: Add metrics collection (1h)**
- Implement `--simplification-stats` flag
- Collect per-pass metrics:
  - Terms reduced
  - Time spent
  - Transformations applied
  - Size changes
- Pretty-print summary table

**Task 6.2: Benchmark all models (1h)**
- Run aggressive simplification on all 10 Tier 1 models
- Measure term reduction percentage
- Document which models benefit most
- Verify ≥20% reduction on ≥50% of models

**Task 6.3: Validation and testing (1h)**
- Add finite difference (FD) validation tests
- Verify transformations preserve semantics
- Test edge cases (zero division, empty expressions)
- Run full test suite

#### Deliverables

- [ ] Metrics collection implemented
- [ ] Benchmark results for all models
- [ ] ≥20% term reduction on ≥50% of models achieved
- [ ] FD validation confirms correctness
- [ ] All tests pass

#### Dependencies

- Day 5: All transformations complete

#### Acceptance Criteria

- [ ] ≥20% derivative term reduction on ≥5 models (50%)
- [ ] Metrics show which passes provide most value
- [ ] FD validation passes (semantics preserved)
- [ ] Performance overhead <10%
- [ ] Quality checks pass

#### Milestone

**🎯 AGGRESSIVE SIMPLIFICATION COMPLETE** - ≥20% term reduction achieved

---

### **Day 7: Diagnostics Mode (Implementation)**

**Date:** TBD  
**Goal:** Implement stage-level timing and breakdowns  
**Effort:** 2.5 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Tasks

**Task 7.1: Add stage-level timing (1h)**
- File: `src/ir/diagnostics.py`
- Track 5 pipeline stages:
  1. Parse (grammar → AST)
  2. Semantic (symbol resolution)
  3. Simplification (8 passes)
  4. IR Generation (AST → IR)
  5. MCP Generation (IR → MCP)
- Use `time.perf_counter()` for microsecond precision

**Task 7.2: Add memory tracking (30 min)**
- Track memory deltas per stage
- Use `tracemalloc` module
- Report peak memory and delta per stage
- <2% overhead target

**Task 7.3: Add simplification pass breakdowns (1h)**
- Track per-pass metrics:
  - Time spent
  - Transformations applied
  - Terms before/after
  - Size changes
- Store in structured format for reporting

#### Deliverables

- [ ] Stage-level timing implemented
- [ ] Memory tracking per stage
- [ ] Simplification pass breakdowns
- [ ] <2% performance overhead

#### Dependencies

- Day 6: Simplification complete (needed for pass breakdowns)

#### Acceptance Criteria

- [ ] 5 pipeline stages timed accurately
- [ ] Memory tracking shows deltas
- [ ] 8 simplification passes tracked independently
- [ ] Overhead <2% for summary mode
- [ ] Quality checks pass

#### Risks

**Risk:** Memory tracking overhead >2%  
**Mitigation:** Make memory tracking opt-in (detailed mode only)  
**Fallback:** Remove memory tracking if overhead too high

---

### **Day 8: Diagnostics Mode (Formatting)**

**Date:** TBD  
**Goal:** Implement text table output with verbosity levels  
**Effort:** 2 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Tasks

**Task 8.1: Implement text table formatting (1h)**
- Create pretty-printed tables using `str.format()`
- Box-drawing characters for borders
- Column alignment (left for names, right for numbers)
- Example output:
  ```
  ┌──────────────────┬─────────┬──────────┐
  │ Stage            │ Time    │ Memory   │
  ├──────────────────┼─────────┼──────────┤
  │ Parse            │ 45 ms   │ +2.1 MB  │
  │ Semantic         │ 12 ms   │ +0.8 MB  │
  │ Simplification   │ 230 ms  │ +5.2 MB  │
  │ IR Generation    │ 67 ms   │ +1.9 MB  │
  │ MCP Generation   │ 89 ms   │ +3.1 MB  │
  └──────────────────┴─────────┴──────────┘
  ```

**Task 8.2: Implement verbosity levels (30 min)**
- **Minimal** (default): No diagnostics output
- **Summary** (`--diagnostic`): Stage-level timing table
- **Detailed** (`--diagnostic --verbose`): Stage + pass-level breakdowns

**Task 8.3: Testing and validation (30 min)**
- Test on representative models
- Verify output formatting
- Check performance overhead
- Test all verbosity levels

#### Deliverables

- [ ] Text table formatting implemented
- [ ] 3 verbosity levels working
- [ ] Tested on representative models
- [ ] Output is readable and useful

#### Dependencies

- Day 7: Diagnostics data collection

#### Acceptance Criteria

- [ ] Text tables render correctly
- [ ] Summary mode shows stage-level timing
- [ ] Detailed mode shows pass-level breakdowns
- [ ] <2% overhead for summary, <5% for detailed
- [ ] Quality checks pass

#### Milestone

**🎯 DIAGNOSTICS MODE COMPLETE** - Text-based diagnostics validated

---

### **Day 9: IPOPT Prototype + Integration Testing**

**Date:** TBD  
**Goal:** Add IPOPT solver support and full integration testing  
**Effort:** 4 hours (2h IPOPT + 2h integration)  
**Risk:** LOW  
**Confidence:** 90%

#### Morning (2 hours): IPOPT Prototype

**Task 9.1: Install IPOPT in CI (30 min)**
- File: `.github/workflows/nightly-ipopt-tests.yml`
- Add IPOPT installation:
  ```yaml
  - name: Install IPOPT
    run: |
      sudo apt-get update
      sudo apt-get install -y coinor-libipopt-dev
  ```
- Verify installation with version check

**Task 9.2: Implement Fischer-Burmeister reformulation (1h)**
- File: `src/solvers/ipopt_solver.py`
- Reformulate MCP as NLP using Fischer-Burmeister function:
  - `FB(a,b) = sqrt(a² + b²) - a - b`
  - Minimize `||FB(F(x), x-l)||` for lower bounds
- Create IPOPT problem interface

**Task 9.3: Create smoke tests (30 min)**
- File: `tests/integration/test_ipopt_smoke.py`
- 4 smoke tests:
  1. Trivial MCP (known solution)
  2. hansmcp.gms (simple economic equilibrium)
  3. Infeasible MCP (should detect)
  4. Unbounded MCP (should detect)

#### Afternoon (2 hours): Integration Testing

**Task 9.4: Run full integration tests (1h)**
- Test all Sprint 11 features together:
  - Aggressive simplification + IPOPT solve
  - CI guardrails + diagnostics output
  - Performance baselines with simplified models
- Verify no feature interactions cause issues

**Task 9.5: Validate on benchmark models (1h)**
- Run IPOPT on 3 GAMSLib models
- Compare results with PATH (local testing)
- Document accuracy (<1% disagreement expected)
- Create nightly workflow for IPOPT tests

#### Deliverables

- [ ] IPOPT installed in CI
- [ ] Fischer-Burmeister reformulation working
- [ ] 4 smoke tests passing
- [ ] IPOPT validated on 3 GAMSLib models
- [ ] Nightly workflow created
- [ ] Integration tests pass

#### Dependencies

- Day 2: CI infrastructure (for nightly workflow)

#### Acceptance Criteria

- [ ] IPOPT installs successfully in CI
- [ ] Smoke tests pass (4/4)
- [ ] Accuracy within 1% of PATH on test models
- [ ] Nightly workflow runs automatically
- [ ] All integration tests pass

#### Risks

**Risk:** IPOPT installation fails in CI  
**Mitigation:** Test on Ubuntu 20.04 and 22.04 environments  
**Fallback:** Defer IPOPT to Sprint 12, focus on integration testing only

**Risk:** Fischer-Burmeister accuracy insufficient  
**Mitigation:** Use tight convergence tolerances  
**Fallback:** Document accuracy limitations, use for smoke tests only

---

### **Day 10: Documentation + Retrospective**

**Date:** TBD  
**Goal:** Complete Sprint 11, document results, prepare retrospective  
**Effort:** 3 hours  
**Risk:** NONE  
**Confidence:** 100%

#### Tasks

**Task 10.1: Update documentation (1h)**
- Update `docs/FEATURES.md` with new features:
  - Aggressive simplification
  - CI regression guardrails
  - Diagnostics mode
  - IPOPT solver support
- Document usage examples
- Add configuration options

**Task 10.2: Run full test suite (30 min)**
- Run all tests: `make test`
- Verify all quality checks: `make typecheck lint format`
- Run benchmark suite
- Document final metrics

**Task 10.3: Create Sprint 11 log (1h)**
- File: `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`
- Document all PRs merged
- Record metrics progression
- Note any deviations from plan
- List key decisions made

**Task 10.4: Prepare retrospective (30 min)**
- File: `docs/planning/EPIC_2/SPRINT_11/RETROSPECTIVE.md`
- What went well
- What could improve
- Action items for Sprint 12
- Lessons learned

#### Deliverables

- [ ] Documentation updated
- [ ] Full test suite passes
- [ ] Sprint log complete
- [ ] Retrospective prepared
- [ ] Sprint 11 officially complete

#### Dependencies

- All previous days complete

#### Acceptance Criteria

- [ ] All features documented
- [ ] All tests pass (100%)
- [ ] Sprint log captures all work
- [ ] Retrospective identifies improvements
- [ ] Ready to start Sprint 12

#### Milestone

**🎉 SPRINT 11 COMPLETE** - Quality infrastructure established

---

## Checkpoints

### Day 5 Checkpoint: Simplification Progress

**Goal:** Validate aggressive simplification is on track

**Expected Results:**
- ≥20% term reduction on ≥3 models (60% of final target)
- All 6 HIGH-priority transformations implemented
- Pipeline infrastructure working
- No size explosions or correctness bugs

**Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| ≥20% on ≥3 models | On Track | Continue as planned |
| ≥15% on ≥3 models | Acceptable | Continue, may need tuning |
| <15% on most models | Behind | Analyze effectiveness, adjust heuristics |

**Contingency Plans:**
- If <15% reduction: Adjust target to ≥15% on ≥50% models
- If size explosions: Tighten budget to 120% instead of 150%
- If correctness bugs: Add more FD validation, fix issues on Day 6

### Day 8 Checkpoint: CI + Diagnostics Validation

**Goal:** Validate infrastructure is working

**Expected Results:**
- CI workflow running in <3 minutes
- Performance baselines tracking all models
- Diagnostics mode producing useful output
- Multi-metric thresholds enforced

**Decision Matrix:**

| Component | Status | Action |
|-----------|--------|--------|
| CI <3 min | ✅ | Excellent |
| CI 3-5 min | ⚠️ | Optimize matrix or defer some checks to nightly |
| CI >5 min | ❌ | Reduce model count or test frequency |

**Contingency Plans:**
- If CI too slow: Reduce to 5 canary models instead of 10
- If baselines noisy: Increase variance tolerance or use median of 3 runs
- If diagnostics overhead >5%: Reduce granularity or make fully opt-in

### Day 10 Checkpoint: Sprint Completion

**Goal:** Validate all acceptance criteria met

**Expected Results:**
- ≥20% term reduction on ≥5 models (50%)
- CI running on every PR in <3 min
- Diagnostics validated on representative models
- All tests passing
- No regressions

**Final Validation:**
- Run full test suite (must pass 100%)
- Benchmark all features
- Compare vs Sprint 10 baseline (no regressions)
- Document any deviations from plan

---

## Risk Mitigation

### Risk 1: Expression Size Explosion

**Probability:** 30%  
**Impact:** HIGH (unusable expressions, performance degradation)

**Mitigation:**
- ✅ 150% size budget enforced at every transformation
- ✅ Automatic rollback if budget exceeded
- ✅ Cancellation detection before expansive operations
- ✅ Depth limit prevents pathological nesting
- ✅ Fixpoint iteration limit (max 5 iterations)

**Contingency:**
- If explosions occur: Tighten budget to 120%
- If still occurs: Disable specific transformations
- If persistent: Make aggressive simplification opt-in

**Indicators:**
- Day 5 checkpoint: If >10% of expressions exceed budget
- Day 6 benchmarking: If any model shows >2x size increase

### Risk 2: Incorrect Transformations

**Probability:** 20%  
**Impact:** CRITICAL (wrong KKT conditions, incorrect MCP solve)

**Mitigation:**
- ✅ Comprehensive unit tests for each transformation (50+ cases)
- ✅ Finite difference validation (opt-in via `--validate`)
- ✅ PATH solver alignment in CI regression tests
- ✅ Extensive test coverage on benchmark models
- ✅ Symbolic equivalence checks where applicable

**Contingency:**
- If FD validation fails: Reject transformation and raise error
- If PATH results differ: Document divergence, investigate root cause
- If systematic errors: Disable transformation until fixed

**Indicators:**
- Day 6 benchmarking: Any FD validation failures
- Day 9 integration: Any PATH result differences >1%

### Risk 3: Performance Overhead >10%

**Probability:** 25%  
**Impact:** MEDIUM (user frustration, slower conversion)

**Mitigation:**
- ✅ Performance budgeting with timeout enforcement
- ✅ Metrics collection identifies bottleneck passes
- ✅ Early termination if overhead exceeds threshold
- ✅ Profile and optimize before completion
- ✅ Benchmarking on representative models

**Contingency:**
- If overhead >10%: Profile and optimize hot paths
- If still >10%: Make aggressive simplification opt-in
- If persistent: Reduce transformation scope (fewer passes)

**Indicators:**
- Day 6 benchmarking: Total simplification time
- Day 8 performance baselines: Regression check

### Risk 4: Insufficient Term Reduction

**Probability:** 35%  
**Impact:** MEDIUM (fails target, limited value)

**Mitigation:**
- ✅ Prioritize high-value transformations (factoring, fractions)
- ✅ Test on benchmark models early (Day 5 checkpoint)
- ✅ Iterate on heuristics based on results
- ✅ Document which model types benefit most
- ✅ Adjustable target (≥15% fallback)

**Contingency:**
- If <20% on <50% models: Adjust target to ≥15% on ≥50%
- If <15% on most models: Analyze which transforms ineffective
- If systematic: Add more transformations in Sprint 12

**Indicators:**
- Day 5 checkpoint: If <15% on most models
- Day 6 benchmarking: Final term reduction percentages

### Risk 5: CI Time Inflation

**Probability:** 20%  
**Impact:** MEDIUM (slower PR feedback, developer friction)

**Mitigation:**
- ✅ Matrix builds reduce time 70% (10 min → 2-3 min)
- ✅ Incremental test scope (parse+convert per-PR, solve nightly)
- ✅ Caching for dependencies and models
- ✅ Still within GitHub Actions free tier (<2000 min/month)

**Contingency:**
- If CI >3 min: Reduce to 5 canary models
- If CI >5 min: Move full suite to nightly only
- If persistent: Use self-hosted runner for parallelization

**Indicators:**
- Day 1: Matrix build runtime
- Day 2: Full workflow runtime with all checks

### Risk 6: PATH Licensing Blocks Integration

**Probability:** 50%  
**Impact:** MEDIUM (no end-to-end validation)

**Mitigation:**
- ✅ IPOPT alternative prototyped (open-source, no licensing)
- ✅ Contact PATH maintainer proactively
- ✅ Self-hosted runner option (if needed)
- ✅ Defer comprehensive PATH testing to Sprint 12

**Contingency:**
- If PATH licensing unclear: Use IPOPT exclusively
- If PATH not available: Validate with FD checks only
- If persistent: Research other MCP solvers

**Indicators:**
- Day 9: IPOPT installation and accuracy
- Pre-sprint: PATH licensing response

### Risk 7: Diagnostics Performance Overhead

**Probability:** 15%  
**Impact:** LOW (slightly slower conversions)

**Mitigation:**
- ✅ <2% overhead target for summary mode
- ✅ <5% overhead target for detailed mode
- ✅ Opt-in flag (no overhead if not enabled)
- ✅ Minimal instrumentation (stage-level only)

**Contingency:**
- If overhead >2%: Reduce granularity
- If overhead >5%: Make memory tracking optional
- If persistent: Stage-level only, no pass-level

**Indicators:**
- Day 7: Overhead measurement with instrumentation
- Day 8: Performance regression check

---

## Dependencies Map

### Feature Dependencies

```
CI Regression Guardrails (Days 1-2)
  ├─ Depends on: None (infrastructure)
  ├─ Enables: Performance tracking for all features
  └─ Required by: IPOPT nightly workflow

Aggressive Simplification (Days 3-6)
  ├─ Depends on: None (independent)
  ├─ Enables: Diagnostics pass breakdowns
  └─ Required by: Diagnostics mode

Diagnostics Mode (Days 7-8)
  ├─ Depends on: Aggressive Simplification (for pass metrics)
  ├─ Enables: Better debugging for all features
  └─ Required by: None (optional)

IPOPT Prototype (Day 9)
  ├─ Depends on: CI infrastructure (nightly workflow)
  ├─ Enables: MCP validation without PATH
  └─ Required by: None (optional)
```

### Implementation Order

**Week 1 (Days 1-5):**
1. Days 1-2: CI Regression Guardrails (foundation)
2. Days 3-5: Aggressive Simplification (core feature)
3. Day 5: Mid-sprint checkpoint

**Week 2 (Days 6-10):**
4. Day 6: Simplification testing and benchmarking
5. Days 7-8: Diagnostics Mode (depends on simplification)
6. Day 9: IPOPT + Integration Testing
7. Day 10: Documentation and retrospective

**Critical Path:** Days 1-2 (CI) → Days 3-6 (Simplification) → Days 7-8 (Diagnostics) → Day 10

**Parallel Opportunities:**
- CI work (Days 1-2) can overlap with simplification design
- Diagnostics implementation (Day 7) can start while simplification benchmarking (Day 6) wraps up
- IPOPT prototype (Day 9) is independent of diagnostics

---

## Success Metrics

### Primary Metrics

**Aggressive Simplification:**
- ✅ Target: ≥20% derivative term reduction on ≥50% of models
- Measurement: Count derivative terms before/after simplification
- Baseline: Current term counts (to be measured)
- Success: ≥5 out of 10 models show ≥20% reduction

**CI Regression Guardrails:**
- ✅ Target: CI runtime <3 minutes on every PR
- Measurement: GitHub Actions workflow duration
- Baseline: Current 10 minutes (sequential)
- Success: 70% reduction via matrix parallelization

**Diagnostics Mode:**
- ✅ Target: <2% overhead for summary, <5% for detailed
- Measurement: Conversion time with/without diagnostics
- Baseline: Current conversion times
- Success: Negligible performance impact

**IPOPT Prototype:**
- ✅ Target: <1% accuracy difference vs PATH
- Measurement: Solution comparison on test models
- Baseline: PATH solutions (gold standard)
- Success: IPOPT validates MCP correctness

### Secondary Metrics

**Test Coverage:**
- ≥95% coverage maintained
- 50+ new tests for simplification
- 10+ tests for diagnostics
- 4 smoke tests for IPOPT

**Quality:**
- All quality checks pass (typecheck, lint, format, test)
- No regressions in existing models
- Zero bugs in production

**Performance:**
- Aggressive simplification overhead <10%
- CI workflow <3 minutes
- Diagnostics overhead <5%
- No memory leaks

### Sprint 11 Definition of Done

- [ ] Aggressive simplification achieves ≥20% term reduction on ≥50% models
- [ ] CI regression guardrails running on every PR in <3 minutes
- [ ] Performance baselines tracked with 20%/50% thresholds
- [ ] Diagnostics mode validated on representative models
- [ ] IPOPT prototype working with <1% accuracy difference
- [ ] All tests pass with ≥95% coverage
- [ ] No regressions in existing functionality
- [ ] All quality checks pass
- [ ] Documentation updated
- [ ] Retrospective complete

---

## Deferred Features

### Deferred to Sprint 12

**Nested/Subset Indexing (maxmin.gms):**
- Effort: 10-14 hours
- Risk: HIGH (grammar recursion, semantic complexity)
- Rationale: Better to implement ALL maxmin.gms blockers together
- Sprint 12 scope: Complete Tier 1 coverage (100% parse rate)

**CSE Advanced Features (T5.2-T5.4):**
- Effort: 6 hours
- Risk: MEDIUM
- Rationale: T5.1 (expensive functions) sufficient for Sprint 11
- Sprint 12 scope: Nested CSE, multiplicative CSE, CSE with aliasing

**PATH CI Integration:**
- Effort: 6-8 hours
- Risk: MEDIUM (licensing unclear)
- Rationale: IPOPT provides 90% of value with zero licensing risk
- Sprint 12 scope: Add PATH if licensing confirmed

**Aggressive Simplification (MEDIUM priority):**
- Effort: 2 hours
- Risk: LOW
- Rationale: HIGH-priority transformations sufficient
- Sprint 12 scope: Add if benchmark results show need

**JSON Diagnostics Output:**
- Effort: 2 hours
- Risk: LOW
- Rationale: Text tables sufficient for Sprint 11
- Sprint 12 scope: JSON enables automation and dashboards

### Sprint 12 Proposal

**Theme:** "Complete Tier 1 Coverage"

**Goals:**
- Implement nested/subset indexing (maxmin.gms → 100%)
- Add CSE advanced features
- Add PATH CI integration (if licensing permits)
- Enhance simplification with MEDIUM-priority transforms
- Add JSON diagnostics output

**Estimated Effort:** 23-40 hours

**Expected Outcome:** 10/10 Tier 1 models at 100% parse rate

---

## Cross-References

### Prep Tasks

- **Task 1:** PREP_PLAN.md → Sprint 11 planning structure
- **Task 2:** maxmin.gms Research → Deferred to Sprint 12
- **Task 3:** Simplification Architecture → Days 3-6 implementation
- **Task 4:** CSE Research → T5.1 deferred (would add 5h)
- **Task 5:** Factoring Prototype → Covered by Task 3 catalog
- **Task 6:** CI Framework Survey → Days 1-2 implementation
- **Task 7:** GAMSLib Sampling → Test all 10 models decision
- **Task 8:** PATH Integration → IPOPT alternative (Day 9)
- **Task 9:** Diagnostics Architecture → Days 7-8 implementation
- **Task 10:** Documentation Guide → Process established
- **Task 11:** Interaction Testing → Deferred to Sprint 12

### Documentation

- `docs/planning/EPIC_2/SPRINT_11/prep_task_synthesis.md` → Planning foundation
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` → Schedule template
- `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md` → Lessons learned

### Code References

- `src/ir/simplification_pipeline.py` → New file (Days 3-6)
- `src/ir/diagnostics.py` → New file (Days 7-8)
- `src/solvers/ipopt_solver.py` → New file (Day 9)
- `.github/workflows/gamslib-regression.yml` → Updated (Days 1-2)
- `scripts/compare_performance.py` → New file (Day 2)

---

## Notes for Sprint Execution

### Daily Best Practices

1. **Daily Progress Tracking:**
   - Update `SPRINT_LOG.md` after each day
   - Document any deviations from plan
   - Note decisions made and rationale

2. **Continuous Testing:**
   - Run quality checks before committing: `make typecheck lint format test`
   - Test on representative models daily
   - Validate no regressions

3. **Incremental Documentation:**
   - Update feature docs as you implement
   - Document design decisions in code comments
   - Keep `SPRINT_LOG.md` current

### Checkpoint Execution

1. **Day 5 Checkpoint (CRITICAL):**
   - Run benchmark suite
   - Measure term reduction on all models
   - Document results in `SPRINT_LOG.md`
   - Use decision matrix to determine next steps

2. **Day 8 Checkpoint:**
   - Validate CI workflow runtime
   - Check performance baseline tracking
   - Verify diagnostics overhead
   - Confirm infrastructure working

3. **Day 10 Final Checkpoint:**
   - Run full test suite (must pass 100%)
   - Validate all acceptance criteria
   - Compare vs Sprint 10 baseline
   - Document completion

### Risk Management

1. **Monitor Risk Indicators:**
   - Day 3-4: Expression size during transformations
   - Day 5: Term reduction percentages
   - Day 6: FD validation results
   - Day 1-2: CI workflow runtime

2. **Activate Mitigations Early:**
   - Don't wait for disaster
   - Use contingency plans proactively
   - Adjust targets if needed

3. **Communication:**
   - Document all decisions
   - Update plan if deviations occur
   - Prepare retrospective as you go

### Testing Strategy

1. **Unit Tests:**
   - Write tests before implementation (TDD)
   - Test each transformation independently
   - Cover edge cases and error conditions

2. **Integration Tests:**
   - Test feature combinations
   - Validate on real GAMS models
   - Check for unexpected interactions

3. **Benchmarking:**
   - Test on all 10 Tier 1 models
   - Measure term reduction percentages
   - Track performance overhead

### Quality Gates

**Before committing:**
- [ ] All tests pass
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Code formatted
- [ ] Documentation updated

**Before marking day complete:**
- [ ] Day's acceptance criteria met
- [ ] `SPRINT_LOG.md` updated
- [ ] No known blockers for next day

**Before sprint complete:**
- [ ] All acceptance criteria met
- [ ] Full test suite passes
- [ ] No regressions detected
- [ ] Documentation complete
- [ ] Retrospective prepared

---

## Time Budget

### Total Capacity

**Sprint Duration:** 10 working days  
**Hours per day:** ~3-4 hours (realistic, sustainable pace)  
**Total Available:** 30-40 hours  
**Recommended Utilization:** 85-95% (27.5-28.5h of 30h)

### Actual Schedule

**Primary Features (MUST-Have):**
- Days 1-2: CI Regression Guardrails - 9h
- Days 3-6: Aggressive Simplification - 12.5h
- Days 7-8: Diagnostics Mode - 4.5h
- **Subtotal:** 26h (87% of 30h capacity)

**Secondary Features (If Time Permits):**
- Day 9: IPOPT Prototype - 2h
- **Total with IPOPT:** 28h (93% of 30h capacity)

**Buffer:**
- Day 9: Integration Testing - 2h
- Day 10: Documentation + Retrospective - 3h
- Unallocated - 2h
- **Total buffer:** 7h (2h already allocated + 5h additional)

**Capacity Check:**
- Baseline (26h): ✅ 87% utilization, 4h buffer
- With IPOPT (28h): ✅ 93% utilization, 2h buffer
- Total capacity (30h): ✅ Fits comfortably

### Contingency Time

**Built-in buffers:**
- Day 5 checkpoint: Can adjust scope if behind
- Day 9: Integration testing is flexible
- Day 10: Documentation can compress if needed

**Emergency buffers:**
- Skip IPOPT prototype (save 2h)
- Reduce diagnostics to stage-level only (save 1h)
- Compress documentation time (save 1h)
- **Available contingency:** 4h

---

**End of Sprint 11 Plan**

**Next Steps:**
1. Review and approve this plan
2. Set sprint dates
3. Create GitHub project board
4. Begin Day 1 implementation
5. Track daily progress in `SPRINT_LOG.md`

**Success Criteria:** All primary features complete, ≥20% term reduction achieved, CI <3 min, diagnostics validated, all tests pass.
