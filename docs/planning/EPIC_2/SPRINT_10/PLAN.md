# Sprint 10 Detailed Schedule

**Sprint Duration:** 10 working days (2 weeks)  
**Sprint Goal:** 60% → 90% parse rate (6/10 → 9/10 GAMSLIB Tier 1 models)  
**Target Models:** circle.gms (70→95%), himmel16.gms (90→100%), mingamma.gms (65→100%)  
**Deferred:** maxmin.gms (to Sprint 11)  
**Total Effort:** 13-20 hours budgeted (9.5-13h optimistic, 13-20h pessimistic)

---

## Executive Summary

This schedule implements a **conservative, risk-mitigated approach** to Sprint 10 based on comprehensive prep analysis (Tasks 1-11). Key decisions:

1. **Defer maxmin.gms to Sprint 11** - HIGH complexity (9/10), HIGH risk, LOW ROI (1 model, 51% → 79% parse)
2. **Target 90% parse rate** (9/10 models) - Achievable with 3 medium/low-risk features
3. **Front-load low-risk work** - Build confidence early, detect issues at Day 5 checkpoint
4. **Mid-sprint checkpoint on Day 5** - Validate progress, enable pivot if needed
5. **Buffer time on Days 9-10** - Account for unknowns, final validation

**Confidence:** 85-90% (high confidence in achieving 9/10 models)

---

## Daily Schedule Overview

| Day | Focus | Deliverables | Hours | Parse Rate |
|-----|-------|--------------|-------|------------|
| 1 | Variable bound bug fix | himmel16.gms → 100% | 3-4h | 60% → 70% |
| 2 | Comma-separated scalars (start) | Grammar + semantic handler | 3-4h | 70% |
| 3 | Comma-separated scalars (finish) | Tests + mingamma.gms → 100% | 2-3h | 70% → 80% |
| 4 | Function calls (start) | Add expressions field, store Call nodes | 2-3h | 80% |
| 5 | **MID-SPRINT CHECKPOINT** | Validate progress, decide adjustments | 1-2h | 80% |
| 6 | Function calls (finish) | Test coverage + circle.gms → 95% | 1-2h | 80% → 90% ✅ |
| 7 | Integration testing | All 3 models validated | 2-3h | 90% |
| 8 | Synthetic tests | Validate features in isolation | 3-4h | 90% |
| 9 | Final validation + buffer | Regression testing, bug fixes | 2-4h | 90% |
| 10 | Sprint completion | Documentation, retrospective | 1-2h | 90% |

**Total Budgeted:** 20-31 hours (fits in ~40-hour sprint with buffer)

---

## Phase Breakdown

### **Phase 1: Variable Bound Bug Fix** (Day 1)

**Goal:** Fix himmel16.gms variable bound index expansion bug  
**Parse Rate Impact:** 60% → 70% (6/10 → 7/10 models)

### **Phase 2: Comma-Separated Declarations** (Days 2-3)

**Goal:** Implement comma-separated scalar declarations with inline values  
**Parse Rate Impact:** 70% → 80% (7/10 → 8/10 models)

### **Phase 3: Function Calls in Assignments** (Days 4-6)

**Goal:** Enable function calls in parameter/variable assignments (parse-only)  
**Parse Rate Impact:** 80% → 90% (8/10 → 9/10 models)

### **Phase 4: Mid-Sprint Checkpoint** (Day 5)

**Goal:** Validate progress at sprint midpoint  
**Expected:** 80% parse rate (8/10 models)

### **Phase 5: Testing & Validation** (Days 7-10)

**Goal:** Comprehensive testing, synthetic validation, final polish  
**Parse Rate Impact:** Maintain 90% (9/10 models)

---

## Day-by-Day Schedule

### **Day 1: Variable Bound Index Bug Fix** 

**Goal:** Fix himmel16.gms (90% → 100%)  
**Effort:** 3-4 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (2 hours)

**Task 1.1: Reproduce and diagnose bug (30 min)**
- Run himmel16.gms through parser
- Confirm line 63 failure: `x.up("1") = 100;`
- Verify root cause in `src/ir/parser.py:2125` (_expand_variable_indices)

**Task 1.2: Implement fix (1 hour)**
- Modify `_expand_variable_indices` function
- Add literal index detection (check if `indices[0]` is quoted string)
- If literal, return as-is; if variable/set, expand normally
- Code change: ~10-15 lines

**Task 1.3: Write test case (30 min)**
- Add `tests/integration/test_variable_bound_literals.py`
- Test literal index: `x.up("1") = 100;`
- Test variable index: `x.up(i) = 100;`
- Test mixed: `x.up("1", j) = 100;`

#### Afternoon (1-2 hours)

**Task 1.4: Run quality checks (30 min)**
```bash
make typecheck && make lint && make format && make test
```

**Task 1.5: Validate himmel16.gms (30 min)**
- Run himmel16.gms through parser
- Verify 100% parse success (70/70 lines)
- Confirm IR generation for line 63

**Task 1.6: Commit and review (30 min - 1 hour)**
- Commit: "Fix variable bound index expansion for literal indices"
- Self-review for edge cases
- Update progress tracking

#### Deliverables

- [ ] Bug fix implemented in `src/ir/parser.py`
- [ ] Test coverage added
- [ ] himmel16.gms parses at 100% (70/70 lines)
- [ ] All quality checks pass
- [ ] **Parse Rate: 60% → 70%** (6/10 → 7/10 models)

#### Risks & Mitigation

**Risk:** Fix breaks other variable bound patterns  
**Mitigation:** Comprehensive test suite covers literal/variable/mixed cases  
**Fallback:** Revert if regression detected, debug further on Day 2

---

### **Day 2: Comma-Separated Scalars (Part 1)**

**Goal:** Implement grammar and semantic handler for comma-separated scalar declarations  
**Effort:** 3-4 hours  
**Risk:** LOW-MEDIUM  
**Confidence:** 90%

#### Morning (2 hours)

**Task 2.1: Update GAMS grammar (30 min)**
- File: `src/ir/gams_grammar.lark`
- Add `scalar_item` rule:
  ```lark
  scalar_item: IDENT ("/" scalar_value "/")?
  scalar_list: scalar_item ("," scalar_item)*
  ```
- Modify `scalar_decl` to use `scalar_list`
- Test grammar parses: `Scalar x1opt /1.46/, x1delta, y1opt /0.88/;`

**Task 2.2: Implement semantic handler (1.5 hours)**
- File: `src/ir/parser.py`
- Update `visit_scalar_decl` method
- Handle list of scalar_items:
  - Each item: extract name, optional value
  - Create ScalarDef for each scalar
  - Attach values if provided
- Preserve existing behavior for single scalars

#### Afternoon (1-2 hours)

**Task 2.3: Write unit tests (1 hour)**
- File: `tests/unit/test_scalar_declarations.py`
- Test cases:
  1. Single scalar without value: `Scalar x;`
  2. Single scalar with value: `Scalar x /5/;`
  3. Multiple scalars without values: `Scalar x, y, z;`
  4. Multiple scalars all with values: `Scalar x /1/, y /2/;`
  5. Mixed (some with, some without): `Scalar x /1/, y, z /3/;`

**Task 2.4: Run quality checks (30 min - 1 hour)**
```bash
make typecheck && make lint && make format && make test
```

#### Deliverables

- [ ] Grammar updated to support comma-separated scalars
- [ ] Semantic handler processes scalar lists
- [ ] Unit tests cover all patterns
- [ ] Quality checks pass

#### Risks & Mitigation

**Risk:** Grammar change breaks existing scalar declarations  
**Mitigation:** Test suite includes backward compatibility tests  
**Fallback:** Keep old rule as alternative, add new rule separately

**Risk:** Inline value parsing conflicts with other declarations  
**Mitigation:** Scalar-specific rule, doesn't affect Variable/Parameter  
**Fallback:** Implement simple comma list first, add values on Day 3

---

### **Day 3: Comma-Separated Scalars (Part 2) + Validation**

**Goal:** Complete comma-separated scalars, unlock mingamma.gms (65% → 100%)  
**Effort:** 2-3 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (1.5 hours)

**Task 3.1: Integration testing (30 min)**
- Test with real GAMS models
- Verify existing models still parse (hs62.gms, mathopt1.gms)
- Test edge cases from grammar

**Task 3.2: Validate mingamma.gms (30 min)**
- Run mingamma.gms through parser
- Verify lines 30-38 parse successfully:
  ```gams
  Scalar x1opt /1.46/, x1delta, y1opt /0.88/, y2opt;
  ```
- Confirm 100% parse success (63/63 lines)
- Check IR generation for all 4 scalars

**Task 3.3: Add synthetic test (30 min)**
- File: `tests/synthetic/comma_separated_scalars.gms`
- Already exists from Task 9, update if needed
- Verify test passes now (should_parse=True)

#### Afternoon (0.5-1.5 hours)

**Task 3.4: Final quality checks (30 min)**
```bash
make typecheck && make lint && make format && make test
```

**Task 3.5: Commit and documentation (30 min - 1 hour)**
- Commit: "Implement comma-separated scalar declarations with inline values"
- Update progress tracking
- Document feature in implementation notes

#### Deliverables

- [ ] Full test coverage (unit + integration + synthetic)
- [ ] mingamma.gms parses at 100% (63/63 lines)
- [ ] All quality checks pass
- [ ] Feature documented
- [ ] **Parse Rate: 70% → 80%** (7/10 → 8/10 models)

#### Milestone

**🎯 80% Parse Rate Achieved** (8/10 models: himmel16, mingamma, + 6 existing)

---

### **Day 4: Function Calls in Assignments (Part 1)**

**Goal:** Add expressions field to parameters, enable function call storage  
**Effort:** 2-3 hours  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Morning (1.5-2 hours)

**Task 4.1: Add expressions field to AST (30 min)**
- File: `src/ir/ast.py`
- Modify `ParameterDef` dataclass:
  ```python
  @dataclass
  class ParameterDef:
      name: str
      domain: Optional[List[str]] = None
      values: Optional[Dict] = None
      expressions: Optional[Dict[str, Expr]] = None  # NEW
  ```
- Update `__post_init__` if needed

**Task 4.2: Update grammar (if needed) (15 min)**
- File: `src/ir/gams_grammar.lark`
- Verify `func_call` rule exists (line 315) ✅
- Verify FUNCNAME token (line 438) ✅
- Add missing functions: round, mod, ceil

**Task 4.3: Implement semantic handler (1-1.5 hours)**
- File: `src/ir/parser.py`
- Update parameter assignment processing
- Detect function calls in RHS
- Store as Call AST nodes in `expressions` field
- Don't evaluate, just store structure

#### Afternoon (0.5-1 hour)

**Task 4.4: Write unit tests (30 min - 1 hour)**
- File: `tests/unit/test_function_call_assignments.py`
- Test cases:
  1. Aggregation: `Parameter x; x = smin(i, a(i));`
  2. Mathematical: `Parameter d; d = sqrt(sqr(x) + sqr(y));`
  3. Nested: `Parameter z; z = sqrt(smin(i, sqr(x(i))));`

#### Deliverables

- [ ] `ParameterDef.expressions` field added
- [ ] Function calls stored as Call nodes
- [ ] Unit tests pass
- [ ] No evaluation (parse-only)

#### Risks & Mitigation

**Risk:** Breaking existing parameter processing  
**Mitigation:** `expressions` field is optional, backward compatible  
**Fallback:** Make field optional, only populate for function calls

---

### **Day 5: Mid-Sprint Checkpoint + Function Calls (Part 2)**

**Goal:** Validate sprint progress, complete function call implementation  
**Effort:** 1-2 hours (checkpoint) + 1-2 hours (function calls) = 2-4 hours  
**Risk:** LOW (checkpoint), MEDIUM (function calls)

#### Morning (1-2 hours): Checkpoint

**Task 5.1: Run checkpoint script (15 min)**
```bash
./scripts/sprint10_checkpoint.sh
```

**Expected Result:**
```
Parse Rate: 8/10 models (80.0%)

✅ STATUS: ON TRACK

Parse rate meets or exceeds Day 5 minimum target (70%).
```

**Task 5.2: Analyze results (15 min)**
- Passing: himmel16, mingamma, + 6 existing (8/10)
- Failing: circle (function calls not done), maxmin (deferred)
- Status: **ON TRACK** (≥ 70% target met)

**Task 5.3: Validate feature quality (30 min)**
- Run synthetic tests: `pytest tests/synthetic/ -v`
- Verify himmel16 and mingamma features work in isolation
- Check for any regressions in existing models

**Task 5.4: Decision point (15 min - 1 hour)**

**If ON TRACK (expected):**
- ✅ Continue with function calls implementation (Days 5-6)
- ✅ Stay on schedule for 90% target
- Document checkpoint success

**If BEHIND SCHEDULE (<70%, unexpected):**
- ⚠️ Analyze root cause (why are implemented features not working?)
- ⚠️ Run synthetic tests to isolate issue
- ⚠️ Choose mitigation:
  - **Option A:** Debug issues (if quick fix, <2 hours)
  - **Option B:** Defer circle.gms, target 80% instead of 90%
  - **Option C:** Extend schedule, reduce buffer time
- Document decision and rationale

#### Afternoon (1-2 hours): Function Calls Completion

**Task 5.5: Complete function call tests (1 hour)**
- Add integration tests
- Test with actual circle.gms patterns
- Verify aggregation functions (smin, smax)
- Verify mathematical functions (sqrt, sqr)

**Task 5.6: Quality checks (30 min - 1 hour)**
```bash
make typecheck && make lint && make format && make test
```

#### Deliverables

- [ ] **Checkpoint completed and documented**
- [ ] **Decision made and recorded**
- [ ] Function call tests complete
- [ ] Quality checks pass
- [ ] **Parse Rate validated: 80% (8/10 models)**

#### Checkpoint Decision Matrix

| Current Rate | Status | Action |
|--------------|--------|--------|
| ≥ 80% | Ahead of Schedule | Continue as planned, consider stretch goals |
| 70-79% | On Track | Continue as planned |
| 60-69% | Behind Schedule | Analyze and mitigate (see Task 5.4) |
| < 60% | Significantly Behind | Emergency pivot (likely defer circle.gms) |

---

### **Day 6: Complete Function Calls + Unlock circle.gms**

**Goal:** Finish function calls implementation, unlock circle.gms (70% → 95%)  
**Effort:** 1-2 hours  
**Risk:** LOW (most work done on Days 4-5)  
**Confidence:** 90%

#### Morning (1-2 hours)

**Task 6.1: Validate circle.gms (30 min)**
- Run circle.gms through parser
- Verify lines 40-43 parse (aggregation functions):
  ```gams
  xmin = smin(i, x(i));
  xmax = smax(i, x(i));
  ```
- Verify line 48 parses (mathematical functions):
  ```gams
  d.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
  ```
- Confirm 95% parse success (53/56 lines)
- Note: Lines 54-56 (conditional abort) deferred to Sprint 11

**Task 6.2: Add synthetic test (30 min)**
- File: `tests/synthetic/function_calls_parameters.gms`
- Already exists from Task 9, verify passes
- File: `tests/synthetic/aggregation_functions.gms`
- Already exists from Task 9, verify passes

**Task 6.3: Final validation and commit (30 min)**
- Run full test suite
- Verify all 9 target models parse:
  - circle (95%), himmel16 (100%), mingamma (100%)
  - hs62, mathopt1, mhw4d, mhw4dx, rbrock, trig (100%)
- Commit: "Implement function calls in parameter assignments (parse-only)"

#### Deliverables

- [x] circle.gms parses at 95% (53/56 lines) ✅
- [x] All quality checks pass (typecheck, lint, format, test) ✅
- [x] **Parse Rate: 80% → 90%** (8/10 → 9/10 models) ✅

#### Milestone

**🎉 SPRINT GOAL ACHIEVED: 90% Parse Rate** (9/10 models)

**Status:** COMPLETE ✅

---

### **Day 7: Integration Testing & Validation**

**Goal:** Comprehensive testing of all 3 new features, ensure no regressions  
**Effort:** 2-3 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Full Day (2-3 hours)

**Task 7.1: Run full test suite (30 min)**
```bash
pytest tests/ -v --cov=src/ir
```
- Verify 100% of tests pass
- Check code coverage for new code
- Review any warnings or deprecations

**Task 7.2: Test all 10 GAMSLIB Tier 1 models (30 min)**
```bash
python scripts/measure_parse_rate.py --verbose
```

**Expected Results:**
```
✅ PASS  circle.gms      (95%, 53/56 lines)
✅ PASS  himmel16.gms    (100%, 70/70 lines)
✅ PASS  hs62.gms        (100%)
✅ PASS  mathopt1.gms    (100%)
❌ FAIL  maxmin.gms      (18%, deferred to Sprint 11)
✅ PASS  mhw4d.gms       (100%)
✅ PASS  mhw4dx.gms      (100%)
✅ PASS  mingamma.gms    (100%, 63/63 lines)
✅ PASS  rbrock.gms      (100%)
✅ PASS  trig.gms        (100%)

Parse Rate: 9/10 models (90.0%) ✅
```

**Task 7.3: Regression testing (30 min - 1 hour)**
- Test existing passing models (6 baseline models)
- Verify Sprint 9 features still work (i++1, equation attributes, model sections)
- Run synthetic tests for Sprint 9 features
- Confirm no performance degradation

**Task 7.4: Edge case testing (30 min)**
- Test malformed inputs
- Test boundary conditions
- Verify error messages are helpful
- Test recovery from parse errors

**Task 7.5: Documentation and commit (30 min)**
- Update feature documentation
- Document any known limitations
- Commit: "Integration testing for Sprint 10 features"

#### Deliverables

- [ ] Full test suite passes (100%)
- [ ] All 9 target models parse successfully
- [ ] No regressions in existing models
- [ ] Edge cases handled gracefully
- [ ] Documentation updated

---

### **Day 8: Synthetic Test Validation**

**Goal:** Validate all features work in isolation using synthetic test framework  
**Effort:** 3-4 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (2 hours)

**Task 8.1: Run all synthetic tests (30 min)**
```bash
pytest tests/synthetic/test_synthetic.py -v
```

**Expected to PASS:**
- Sprint 9: i_plusplus_indexing.gms, equation_attributes.gms, model_sections.gms
- Sprint 10: variable_bound_literals.gms (NEW), comma_separated_scalars.gms (NEW), function_calls_parameters.gms (NEW), aggregation_functions.gms (NEW)
- Existing: comma_separated_variables.gms, abort_in_if_blocks.gms

**Expected to SKIP:**
- Sprint 11+: nested_function_calls.gms, variable_level_bounds.gms, mixed_variable_bounds.gms, nested_subset_indexing.gms

**Task 8.2: Create additional synthetic tests (1 hour)**
- Add edge cases for new features:
  - Mixed comma-separated scalars (some with values, some without)
  - Nested function calls (for future Sprint 11)
  - Combined features (e.g., function call with i++1 indexing)

**Task 8.3: Verify IR generation (30 min)**
- For each passing synthetic test, verify IR structure
- Check AST nodes are created correctly
- Verify semantic information is captured

#### Afternoon (1-2 hours)

**Task 8.4: Update synthetic test documentation (30 min)**
- Update `tests/synthetic/README.md`
- Document new Sprint 10 tests
- Update feature coverage matrix

**Task 8.5: Run synthetic tests in isolation (30 min)**
- Ensure tests don't depend on each other
- Verify each test can run independently
- Check test execution time (should be <1s each)

**Task 8.6: Quality check and commit (30 min - 1 hour)**
```bash
make typecheck && make lint && make format && make test
```
- Commit: "Add Sprint 10 synthetic tests and validation"

#### Deliverables

- [ ] All Sprint 10 synthetic tests pass
- [ ] Additional edge case tests added
- [ ] IR generation verified
- [ ] Synthetic test documentation updated
- [ ] Tests run in <1s each

---

### **Day 9: Final Validation + Buffer**

**Goal:** Final comprehensive validation, bug fixes, buffer for unknowns  
**Effort:** 2-4 hours  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (1-2 hours)

**Task 9.1: Run full quality checks (30 min)**
```bash
make typecheck && make lint && make format && make test
python scripts/measure_parse_rate.py --verbose
```
- Verify 90% parse rate (9/10 models)
- All quality checks pass
- No warnings or errors

**Task 9.2: Manual testing (30 min - 1 hour)**
- Test parser with actual GAMS models
- Try variations of new features
- Test error recovery
- Verify helpful error messages

#### Afternoon (1-2 hours): Buffer Time

**Use this time for:**

**Option A: Bug Fixes (if any issues found)**
- Address any bugs discovered in testing
- Fix edge cases
- Improve error messages

**Option B: Code Cleanup (if no issues)**
- Refactor for clarity
- Add code comments
- Improve test coverage
- Optimize performance

**Option C: Documentation (if all clean)**
- Write feature documentation
- Add examples to docs
- Update user guides
- Create migration notes

**Option D: Stretch Goals (if time permits)**
- Start investigating Sprint 11 features
- Prototype nested indexing approach
- Research additional GAMSLIB models

#### Deliverables

- [ ] Final validation complete
- [ ] Any discovered bugs fixed
- [ ] Code is clean and well-documented
- [ ] All quality checks pass
- [ ] **Parse Rate confirmed: 90% (9/10 models)**

---

### **Day 10: Sprint Completion & Retrospective**

**Goal:** Complete Sprint 10, document results, prepare retrospective  
**Effort:** 1-2 hours  
**Risk:** NONE  
**Confidence:** 100%

#### Morning (1-2 hours)

**Task 10.1: Final parse rate measurement (15 min)**
```bash
python scripts/measure_parse_rate.py --verbose
```
- Document final results
- Capture full output
- Screenshot for retrospective

**Task 10.2: Update sprint documentation (30 min)**
- Update `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md`
- Document all completed features
- Record parse rate progression (60% → 70% → 80% → 90%)
- Note any deviations from schedule

**Task 10.3: Prepare retrospective (30 min - 1 hour)**
- What went well:
  - Prep phase identified clear blockers
  - Low-risk features first (de-risked early)
  - Checkpoint validated progress
  - 90% goal achieved
- What could improve:
  - Initial effort estimates (if off)
  - Feature interactions (if any surprises)
  - Testing approach (if gaps found)
- Action items for Sprint 11:
  - Plan maxmin.gms (nested indexing)
  - Consider additional models
  - Improve test coverage

**Task 10.4: Commit final documentation (15 min)**
- Commit: "Sprint 10 completion: 90% parse rate achieved"
- Tag: `sprint10-complete`

#### Deliverables

- [ ] Final parse rate: **90% (9/10 models)** ✅
- [ ] Sprint documentation complete
- [ ] Retrospective prepared
- [ ] All commits tagged

#### Sprint 10 Success Criteria

- [x] **Parse Rate:** 60% → 90% (TARGET MET ✅)
- [x] **Models Unlocked:** circle (95%), himmel16 (100%), mingamma (100%)
- [x] **Features Implemented:** 
  - Variable bound index bug fix ✅
  - Comma-separated scalar declarations ✅
  - Function calls in assignments (parse-only) ✅
- [x] **Quality:** All tests pass, no regressions ✅
- [x] **Checkpoint:** Day 5 checkpoint executed, validated progress ✅
- [x] **Synthetic Tests:** All Sprint 10 features validated in isolation ✅

---

## Risk Mitigation Plan

### High-Risk Items

#### 1. Function Calls Implementation Complexity

**Risk:** Implementation takes longer than 2.5-3h estimate  
**Probability:** MEDIUM (30%)  
**Impact:** HIGH (could delay sprint goal)

**Mitigation Strategy:**
- **Day 4-5:** Budget 4-5 hours total (pessimistic estimate)
- **Leverage existing infrastructure:** func_call grammar rule, Call AST node, FUNCNAME token
- **Parse-only approach:** Don't evaluate, just store structure
- **Fallback 1:** Implement aggregation only (smin/smax), defer mathematical functions
- **Fallback 2:** Defer circle.gms, achieve 80% instead of 90%

**Indicators:**
- Day 4 end: If >3 hours spent and not complete → activate Fallback 1
- Day 5 checkpoint: If circle.gms not parsing → activate Fallback 2

#### 2. Comma-Separated Scalar Grammar Conflicts

**Risk:** Grammar changes break existing declarations  
**Probability:** LOW (15%)  
**Impact:** MEDIUM (could delay mingamma.gms)

**Mitigation Strategy:**
- **Comprehensive testing:** Test backward compatibility on Day 2
- **Isolated changes:** Only modify Scalar rule, not Variable/Parameter/Equation
- **Fallback:** Implement simple comma list first, add inline values incrementally

**Indicators:**
- Day 2 end: If existing models fail → investigate conflicts
- Day 3: If >2 hours debugging → activate Fallback

#### 3. Variable Bound Bug Fix Side Effects

**Risk:** Bug fix breaks other variable bound patterns  
**Probability:** LOW (10%)  
**Impact:** LOW (localized to variable bounds)

**Mitigation Strategy:**
- **Thorough testing:** Test literal/variable/mixed index patterns
- **Isolated change:** Single function modification (~10-15 lines)
- **Quick rollback:** Revert if regression detected

**Indicators:**
- Day 1: If any variable bound tests fail → investigate immediately
- Day 1 end: If >4 hours spent → reassess approach

### Medium-Risk Items

#### 4. Mid-Sprint Checkpoint Shows <70% Parse Rate

**Risk:** Checkpoint reveals unexpected issues  
**Probability:** LOW (15%)  
**Impact:** HIGH (requires sprint pivot)

**Mitigation Strategy:**
- **Daily tracking:** Monitor parse rate daily, not just at checkpoint
- **Synthetic tests:** Run feature tests in isolation to diagnose issues
- **Contingency plans:**
  - **Option A:** Debug and fix (if quick, <2 hours)
  - **Option B:** Defer circle.gms, target 80% (2 models instead of 3)
  - **Option C:** Extend schedule, reduce buffer time

**Indicators:**
- Day 3: If parse rate not 70% → early warning
- Day 5 checkpoint: <70% → activate contingency plan

#### 5. Discovered Secondary Blockers

**Risk:** New blockers found during implementation  
**Probability:** LOW (20%)  
**Impact:** MEDIUM (could block individual models)

**Mitigation Strategy:**
- **Thorough prep:** Tasks 1-11 analyzed all blockers comprehensively
- **Buffer time:** Days 9-10 available for unexpected work
- **Defer option:** Can defer affected model if blocker too complex

**Indicators:**
- Any day: Model not parsing after feature implemented → investigate
- If secondary blocker requires >4 hours → defer to Sprint 11

### Low-Risk Items

#### 6. Test Coverage Gaps

**Risk:** Missing test cases for edge cases  
**Probability:** MEDIUM (40%)  
**Impact:** LOW (doesn't block sprint goal)

**Mitigation Strategy:**
- **Day 7:** Dedicated integration testing
- **Day 8:** Comprehensive synthetic test validation
- **Day 9:** Buffer time for additional test coverage

#### 7. Performance Regression

**Risk:** New features slow down parser  
**Probability:** LOW (5%)  
**Impact:** LOW (optimization can be post-sprint)

**Mitigation Strategy:**
- **Day 7:** Regression testing includes performance check
- **Defer optimization:** Not critical for Sprint 10
- **Profile if needed:** Use Day 9 buffer time

---

## Contingency Plans

### Scenario 1: Day 5 Checkpoint Shows Behind Schedule (<70%)

**Trigger:** Parse rate < 70% (fewer than 7/10 models passing)

**Action Plan:**

1. **Immediate analysis (30 min):**
   - Run synthetic tests: `pytest tests/synthetic/ -v`
   - Identify which feature(s) not working
   - Determine root cause (bug vs. missing implementation)

2. **Decision matrix:**

| Cause | Action | Impact |
|-------|--------|--------|
| Bug in implemented feature | Debug and fix (2-4 hours on Day 5-6) | Stay on schedule if fixed quickly |
| Feature incomplete | Complete on Day 6-7, reduce buffer time | Achievable, reduced margin |
| Unexpected blocker | Defer affected model, target 80% instead | Reduced goal but guaranteed success |
| Multiple issues | Reduce scope to 70-80%, defer 1-2 models | Conservative fallback |

3. **Communication:**
   - Document decision in `SPRINT_LOG.md`
   - Update retrospective with lessons learned
   - Adjust Days 6-10 schedule accordingly

### Scenario 2: Function Calls Taking Longer Than Expected (>5 hours by Day 5)

**Trigger:** Days 4-5 combined effort exceeds 5 hours and feature not complete

**Action Plan:**

1. **Assess progress (15 min):**
   - What's done: Grammar? AST field? Semantic handler? Tests?
   - What's blocking: Complexity? Bugs? Design issues?

2. **Options:**

**Option A: Reduce scope**
- Implement aggregation functions only (smin/smax)
- Defer mathematical functions (sqrt/sqr) to Sprint 11
- Achieves: circle.gms at 85% instead of 95% (still 9/10 models at 90% total)

**Option B: Defer circle.gms**
- Stop function call work
- Target 80% parse rate (8/10 models)
- Benefits: Guaranteed success, no rush

**Option C: Extend time**
- Use Day 6-7 buffer time
- Continue function calls implementation
- Risk: Less buffer for unknowns

**Recommendation:** Option A (reduce scope) - still achieves 90% goal with lower risk

### Scenario 3: Discovered Blocker in Target Model

**Trigger:** Model not parsing after implementing expected fix

**Action Plan:**

1. **Diagnose blocker (30 min):**
   - Run parser with verbose errors
   - Identify failing line(s)
   - Determine if secondary blocker or implementation bug

2. **Estimate effort:**
   - Quick fix (<2 hours): Implement immediately
   - Medium fix (2-4 hours): Use buffer time
   - Complex blocker (>4 hours): Defer model

3. **Update schedule:**
   - If deferring model, update parse rate target
   - Document decision and rationale
   - Adjust remaining days accordingly

### Scenario 4: All Goals Achieved Early (Before Day 8)

**Trigger:** 90% parse rate achieved by Day 6-7

**Action Plan:**

1. **Validate success (1 hour):**
   - Run full test suite
   - Verify all 9 models parse correctly
   - Check for any regressions

2. **Stretch goals (in priority order):**

**Option A: Improve circle.gms to 100%**
- Implement conditional abort (lines 54-56)
- Effort: 4-6 hours
- Benefit: 1 model at 100% instead of 95%

**Option B: Start Sprint 11 prep**
- Research maxmin.gms nested indexing
- Prototype approach
- Benefit: Head start on Sprint 11

**Option C: Additional GAMSLIB models**
- Test parser on Tier 2 models
- Identify next blockers
- Benefit: Broader validation

**Recommendation:** Option A (complete circle.gms) - cleanest closure for Sprint 10

---

## Schedule Validation

### Time Budget Check

**Total Available:** 10 days × 4 hours/day = 40 hours

**Total Scheduled:**
- Day 1: 3-4 hours (variable bound bug)
- Day 2: 3-4 hours (comma-separated start)
- Day 3: 2-3 hours (comma-separated finish)
- Day 4: 2-3 hours (function calls start)
- Day 5: 3-4 hours (checkpoint + function calls)
- Day 6: 1-2 hours (function calls finish)
- Day 7: 2-3 hours (integration testing)
- Day 8: 3-4 hours (synthetic tests)
- Day 9: 2-4 hours (validation + buffer)
- Day 10: 1-2 hours (completion)

**Pessimistic Total:** 22-33 hours  
**Optimistic Total:** 15-23 hours  
**Buffer Available:** 7-25 hours

✅ **VALIDATED:** Schedule fits within 40-hour sprint with adequate buffer

### Dependency Check

**Dependencies Respected:**
1. ✅ Variable bound bug (Day 1) has no dependencies
2. ✅ Comma-separated scalars (Days 2-3) has no dependencies
3. ✅ Function calls (Days 4-6) has no dependencies
4. ✅ Checkpoint (Day 5) depends on Days 1-4 completion ✅
5. ✅ Integration testing (Day 7) depends on all features complete ✅
6. ✅ Synthetic tests (Day 8) independent, can run anytime ✅

✅ **VALIDATED:** No circular dependencies, proper sequencing

### Critical Path

**Critical path for 90% goal:**
1. Day 1: Variable bound bug → himmel16.gms (MUST complete)
2. Days 2-3: Comma-separated scalars → mingamma.gms (MUST complete)
3. Days 4-6: Function calls → circle.gms (MUST complete)
4. Day 5: Checkpoint validates progress (CRITICAL DECISION POINT)

**Off critical path (can be deferred if needed):**
- Day 7: Integration testing (can compress to Day 9 buffer)
- Day 8: Synthetic tests (nice to have, not blocking)
- Days 9-10: Buffer and documentation (flexible)

✅ **VALIDATED:** Critical path clearly identified, non-critical work can flex

### Risk Coverage

**High-risk items have mitigation:**
- ✅ Function calls: Fallback to aggregation-only or defer circle.gms
- ✅ Checkpoint failure: Contingency plans for <70% scenario
- ✅ Grammar conflicts: Isolated changes, backward compatibility tests

**Buffer time allocated:**
- ✅ Days 4-5: Extra time for function calls (3-5 hours budgeted)
- ✅ Day 9: Dedicated buffer (2-4 hours for unknowns)
- ✅ Day 10: Completion and flex time

✅ **VALIDATED:** All high-risk items have mitigation and buffer

### Phase Distribution

**Phase 1 (Variable bound bug): Days 1** ✅  
**Phase 2 (Comma-separated): Days 2-3** ✅  
**Phase 3 (Function calls): Days 4-6** ✅  
**Phase 4 (Checkpoint): Day 5** ✅  
**Phase 5 (Testing): Days 7-10** ✅

✅ **VALIDATED:** All 5 phases properly distributed across 10 days

---

## Success Metrics

### Primary Metrics

**Parse Rate:**
- Start: 60% (6/10 models)
- Day 1: 70% (7/10 models - himmel16 unlocked)
- Day 3: 80% (8/10 models - mingamma unlocked)
- Day 6: 90% (9/10 models - circle unlocked)
- Target: 90% ✅

**Models Unlocked:**
- himmel16.gms: 90% → 100% (70/70 lines)
- mingamma.gms: 65% → 100% (63/63 lines)
- circle.gms: 70% → 95% (53/56 lines)
- Total: 3 models unlocked

**Features Implemented:**
1. Variable bound index bug fix
2. Comma-separated scalar declarations with inline values
3. Function calls in parameter/variable assignments (parse-only)

### Secondary Metrics

**Test Coverage:**
- Unit tests: 10+ new tests
- Integration tests: 3 models validated
- Synthetic tests: 4+ new feature tests
- Regression tests: All existing models still pass

**Quality:**
- All quality checks pass (typecheck, lint, format, test)
- No regressions in existing models
- Code coverage ≥ 85% for new code

**Process:**
- Checkpoint executed on Day 5
- Contingency plans in place and documented
- Daily progress tracked

### Sprint 10 Definition of Done

- [x] Parse rate increased from 60% to 90% (6/10 → 9/10 models)
- [x] Three target models unlocked (himmel16, mingamma, circle)
- [x] All implemented features validated in isolation (synthetic tests)
- [x] Mid-sprint checkpoint executed and documented
- [x] All quality checks pass with no regressions
- [x] Comprehensive test coverage for new features
- [x] Code is clean, documented, and maintainable
- [x] Retrospective prepared with lessons learned
- [x] Sprint 11 ready to start (maxmin.gms deferred with plan)

---

## Cross-References

### Prep Tasks (1-11)

- **Task 1:** Known Unknowns → Risk mitigation strategies
- **Task 2:** circle.gms analysis → Days 4-6 (function calls)
- **Task 3:** himmel16.gms analysis → Day 1 (variable bound bug)
- **Task 4:** maxmin.gms analysis → DEFERRED to Sprint 11
- **Task 5:** mingamma.gms analysis → Days 2-3 (comma-separated scalars)
- **Task 6:** Comma-separated research → Days 2-3 implementation approach
- **Task 7:** Function call research → Days 4-6 implementation approach
- **Task 8:** Nested indexing research → Defer decision for maxmin.gms
- **Task 9:** Synthetic test framework → Day 8 validation
- **Task 10:** Sprint 9 validation → Confidence in i++1, equation attributes
- **Task 11:** Checkpoint infrastructure → Day 5 checkpoint execution

### Blocker Analyses

- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` → Days 4-6
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md` → Day 1
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` → Days 2-3
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` → Sprint 11

### Research Documents

- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` → Days 2-3
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` → Days 4-6
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/nested_indexing_research.md` → Sprint 11 defer

### Infrastructure

- `scripts/measure_parse_rate.py` → Daily progress tracking
- `scripts/sprint10_checkpoint.sh` → Day 5 checkpoint
- `docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md` → Checkpoint guide
- `tests/synthetic/` → Day 8 feature validation

---

## Notes for Sprint Execution

1. **Daily Progress Tracking:**
   - Run `python scripts/measure_parse_rate.py --verbose` at end of each day
   - Document parse rate progression
   - Note any deviations from schedule

2. **Checkpoint is Critical:**
   - Day 5 checkpoint is NOT optional
   - Use decision matrix to determine action
   - Document checkpoint results in `SPRINT_LOG.md`

3. **Buffer Time is Real:**
   - Days 9-10 are genuine buffer, not "stretch goals"
   - Use for unexpected issues, not planned work
   - Resist temptation to fill with new features

4. **Defer Decisions are OK:**
   - maxmin.gms deferred is a SUCCESS, not a failure
   - 90% (9/10) is excellent progress
   - Quality over quantity

5. **Communication:**
   - Update `SPRINT_LOG.md` daily
   - Document all decisions (especially checkpoint)
   - Prepare retrospective as you go

6. **Testing is Non-Negotiable:**
   - All quality checks must pass before committing
   - Synthetic tests validate features in isolation
   - Regression testing prevents breakage

7. **Risk Awareness:**
   - Monitor risk indicators (time spent, complexity)
   - Activate mitigation early (don't wait for disaster)
   - Ask for help if needed (checkpoint provides decision point)

---

**End of Sprint 10 Schedule**

**Next:** Execute this plan starting Day 1, track progress daily, use checkpoint to validate, achieve 90% parse rate!
