# Sprint 17 Known Unknowns

**Created:** January 28, 2026  
**Status:** Active - Pre-Sprint 17  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 17 Translation/Solve Improvements, Final Assessment & Release v1.1.0

---

## Executive Summary

This document identifies all assumptions and unknowns for Sprint 17 features **before** implementation begins. Sprint 17 is the final sprint of Epic 3, focused on addressing remaining translation and solve failures, completing final testing and documentation, and releasing v1.1.0.

**Sprint 17 Scope:**
1. Translation Improvements (~8-10h) - Address 27 translation failures
2. Solve Improvements (~6-8h) - Fix remaining solve failures and mismatches
3. Final Assessment (~6-8h) - Complete test runs with comprehensive comparison
4. Documentation & Release (~6-8h) - User guides, infrastructure docs, v1.1.0 release

**Reference:** See `docs/planning/EPIC_3/PROJECT_PLAN.md` lines 455-576 for complete Sprint 17 deliverables and acceptance criteria.

**Sprint 16 Key Results (Starting Point):**
- Parse success rate: 30.0% (48/160 models)
- Translation success rate: 43.8% (21/48 of parsed models)
- Solve success rate: 52.4% (11/21 of translated models)
- Full pipeline success rate: 3.1% (5/160 models)
- Successful models: himmel11, hs62, mathopt1, mathopt2, rbrock

**Sprint 17 Targets:**
- Parse: ≥70% (112 models)
- Translate: ≥60% of parsed
- Solve: ≥80% of translated
- Full pipeline: ≥50% (80 models)
- Improvement: ≥25% improvement over baseline

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 16: 27 unknowns verified, 100% completion rate
- Sprint 15: 26 unknowns verified, comprehensive baseline established
- Sprint 14: 26 unknowns, all verified or deferred appropriately

---

## How to Use This Document

### Before Sprint 17 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 17
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 27  
**Verified:** 0 (0%)  
**Remaining:** 27 (100%)

**By Priority:**
- Critical: 7 (26%) - 0 verified, 7 remaining
- High: 11 (41%) - 0 verified, 11 remaining
- Medium: 7 (26%) - 0 verified, 7 remaining
- Low: 2 (7%) - 0 verified, 2 remaining

**By Category:**
- Category 1 (Translation Improvements): 7 unknowns
- Category 2 (Solve Improvements): 5 unknowns
- Category 3 (Parse Improvements): 6 unknowns
- Category 4 (Detailed Error Analysis): 5 unknowns
- Category 5 (Fix Complexity Estimation): 4 unknowns

**Estimated Research Time:** 30-38 hours (spread across prep phase)

---

## Table of Contents

1. [Category 1: Translation Improvements](#category-1-translation-improvements)
2. [Category 2: Solve Improvements](#category-2-solve-improvements)
3. [Category 3: Parse Improvements](#category-3-parse-improvements)
4. [Category 4: Detailed Error Analysis](#category-4-detailed-error-analysis)
5. [Category 5: Fix Complexity Estimation](#category-5-fix-complexity-estimation)
6. [Template for New Unknowns](#template-for-new-unknowns)
7. [Next Steps](#next-steps)
8. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Translation Improvements

## Unknown 1.1: What specific functions are missing from the AD module that cause `diff_unsupported_func` errors?

### Priority
**Critical** - Affects 6 models (22% of translation failures)

### Assumption
The `diff_unsupported_func` errors are caused by missing derivative rules for specific GAMS intrinsic functions (gamma, beta, erf, etc.) that can be added to the AD module with known mathematical formulas.

### Research Questions
1. Which specific functions trigger `diff_unsupported_func` in each of the 6 models?
2. Are the derivative rules mathematically straightforward or do they require special cases?
3. Are there library dependencies needed (e.g., scipy for special functions)?
4. Can some functions be approximated or do they need exact derivatives?
5. Are there nested function calls complicating the derivatives?

### How to Verify

**Test Case 1: Extract failing functions**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome == "diff_unsupported_func") | "\(.model_name): \(.translate_error)"'
```

**Test Case 2: Check AD module for missing rules**
```bash
grep -n "def diff_" src/ad/*.py | head -30
# List all currently supported derivatives
```

**Test Case 3: Look up derivative formulas**
- gamma(x): ψ(x) * gamma(x) where ψ is digamma
- erf(x): 2/√π * exp(-x²)
- Check GAMS documentation for function semantics

### Risk if Wrong
- Functions may require complex special-case handling
- Missing library dependencies could block implementation
- Some functions may not have closed-form derivatives

### Estimated Research Time
2-3 hours (function extraction, formula lookup, feasibility assessment)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.2: Can `model_domain_mismatch` errors be fixed by improving domain propagation in the IR?

### Priority
**Critical** - Affects 6 models (22% of translation failures)

### Assumption
Domain mismatch errors occur when variable indices don't align with equation indices, and can be fixed by improving how the IR tracks and propagates domain information.

### Research Questions
1. What specific domain mismatches cause these 6 failures?
2. Are mismatches due to IR construction or later processing?
3. Is domain propagation happening during normalization or translation?
4. Can mismatches be detected earlier (at parse time) for better errors?
5. Are there patterns in the failing models (sparse indices, alias sets)?

### How to Verify

**Test Case 1: Examine domain mismatch details**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome == "model_domain_mismatch") | .translate_error'
```

**Test Case 2: Trace domain propagation**
- Add debug logging to IR domain tracking
- Run one failing model with verbose output
- Identify where domain information is lost

**Test Case 3: Compare with successful models**
- Find similar model that succeeds
- Compare domain handling differences

### Risk if Wrong
- Domain propagation may require significant IR refactoring
- May need parser changes to capture domain correctly
- Could be a fundamental design issue rather than a bug

### Estimated Research Time
2-3 hours (error analysis, IR tracing, pattern identification)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.3: How should `model_no_objective_def` errors be handled for feasibility problems?

### Priority
**High** - Affects 5 models (19% of translation failures)

### Assumption
Models without explicit objective functions are feasibility problems that can be handled by either adding a dummy objective (minimize 0) or reformulating as constraint satisfaction.

### Research Questions
1. Are these actual feasibility problems or models with implicit objectives?
2. Does GAMS allow models without MINIMIZE/MAXIMIZE statements?
3. How does PATH solver handle MCP without objective?
4. Should we add `minimize 0` or use a different formulation?
5. What's the mathematical correctness of adding dummy objectives?

### How to Verify

**Test Case 1: Examine model files**
```bash
for model in $(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.translate_outcome == "model_no_objective_def") | .model_name'); do
    echo "=== $model ==="
    grep -i "minimize\|maximize\|model.*using" data/gamslib/raw/$model.gms
done
```

**Test Case 2: Check GAMS documentation**
- How does GAMS handle CNS (Constrained Nonlinear System) model type?
- What's the expected behavior for feasibility problems?

**Test Case 3: Test dummy objective**
- Manually add `minimize 0` to a failing model
- Test if it translates and solves correctly

### Risk if Wrong
- Dummy objectives may change solution behavior
- Some models may truly need different handling
- Mathematical equivalence may not hold

### Estimated Research Time
1-2 hours (model analysis, GAMS research, prototype testing)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.4: Can `unsup_index_offset` errors be resolved with enhanced index arithmetic?

### Priority
**High** - Affects 3 models (11% of translation failures)

### Assumption
Index offset operations (e.g., `X(i-1)`, `A(t+1)`) can be supported by tracking index arithmetic in the IR and generating appropriate GAMS code.

### Research Questions
1. What specific index offset patterns appear in the 3 failing models?
2. Does the IR currently support index arithmetic operations?
3. How should offset indices be handled in derivatives (∂/∂X(i-1))?
4. Are offsets used in sum/prod operators (more complex)?
5. What's the GAMS semantics for out-of-bounds index offsets?

### How to Verify

**Test Case 1: Extract offset patterns**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome == "unsup_index_offset") | "\(.model_name): \(.translate_error)"'
```

**Test Case 2: Check IR index representation**
```python
# Review src/ir/symbols.py for index handling
# Can indices be expressions, not just symbols?
```

**Test Case 3: Test simple offset case**
- Create minimal model with `X(i-1)` reference
- Trace through parser → IR → translation

### Risk if Wrong
- Index arithmetic may require IR redesign
- Derivatives with offsets are mathematically complex
- Out-of-bounds handling may differ from GAMS

### Estimated Research Time
2 hours (pattern extraction, IR analysis, feasibility assessment)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.5: What causes `unsup_dollar_cond` errors and how complex is the fix?

### Priority
**Medium** - Affects 1 model (4% of translation failures)

### Assumption
Dollar conditional expressions (`$(condition)`) in equations can be handled by converting to indicator constraints or conditional expressions in the generated MCP.

### Research Questions
1. What specific dollar conditional pattern triggers the error?
2. Is the condition on variables, sets, or parameters?
3. Can dollar conditionals be expanded at translation time?
4. Does PATH solver support conditional/indicator constraints?
5. Is there a simple workaround (big-M reformulation)?

### How to Verify

**Test Case 1: Examine the failing model**
```bash
model=$(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.translate_outcome == "unsup_dollar_cond") | .model_name')
grep '\$' data/gamslib/raw/$model.gms | head -20
```

**Test Case 2: Research MCP conditional handling**
- How does GAMS handle dollar conditions in MCP models?
- What does PATH solver accept?

### Risk if Wrong
- Dollar conditionals may require significant IR changes
- Big-M reformulation may cause numerical issues
- May need to defer to future sprint

### Estimated Research Time
1 hour (pattern extraction, research)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.6: What causes `codegen_numerical_error` and is it data-dependent?

### Priority
**Low** - Affects 1 model (4% of translation failures)

### Assumption
The numerical error during code generation is caused by extreme parameter values or divisions that can be fixed with bounds checking or scaling.

### Research Questions
1. What specific numerical operation causes the error?
2. Is it division by zero, overflow, or underflow?
3. Is the error in the model data or in code generation logic?
4. Can the error be caught and reported more clearly?
5. Is the model mathematically well-posed?

### How to Verify

**Test Case 1: Extract error details**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome == "codegen_numerical_error") | {model: .model_name, error: .translate_error}'
```

**Test Case 2: Add debug logging**
- Add try/catch around numerical operations in codegen
- Identify specific line/operation causing failure

### Risk if Wrong
- May be a fundamental model issue, not a bug
- Fix may require model-specific workarounds

### Estimated Research Time
1 hour (error tracing, root cause analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.7: Will fixing translation issues improve the translate rate or reveal new issues?

### Priority
**Medium** - Affects Sprint 17 target setting

### Assumption
Fixing the identified translation issues will improve translate success rate toward the 60% target without revealing significant new translation blockers.

### Research Questions
1. Are there hidden dependencies between translation issues?
2. Could fixing one issue cause others to appear?
3. Do newly-parsing models (from parse fixes) have new translation issues?
4. Is 60% translate rate realistic given the model complexity?
5. Should we set intermediate checkpoints?

### How to Verify

**Test Case 1: Analyze translation issue independence**
- Review the 27 failures for common patterns
- Check if multiple issues affect same models

**Test Case 2: Run incremental tests**
- After each translation fix, retest all models
- Track new issues that emerge

### Risk if Wrong
- Translation improvements may be slower than expected
- New blockers may appear as others are fixed
- 60% target may need revision

### Estimated Research Time
1 hour (analysis, planning)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 2: Solve Improvements

## Unknown 2.1: What causes the 8 remaining `path_syntax_error` failures?

### Priority
**Critical** - Directly affects solve success rate

### Assumption
The remaining 8 path_syntax_error failures are caused by patterns in emit_gams.py that weren't fixed in Sprint 16 and can be addressed with targeted emit fixes.

### Research Questions
1. What specific GAMS syntax errors occur in each model?
2. Are these new patterns or edge cases of fixed patterns?
3. Can we generate and examine the failing MCP files?
4. Are the errors in equations, variable declarations, or model statements?
5. How many different root causes are there (1-2 or many)?

### How to Verify

**Test Case 1: List affected models**
```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.solve_outcome == "path_syntax_error") | .model_name'
```

**Test Case 2: Generate and compile MCP**
```bash
for model in $(affected models); do
    python -m nlp2mcp.cli $model --emit-only -o /tmp/$model_mcp.gms
    gams /tmp/$model_mcp.gms
done
```

**Test Case 3: Categorize GAMS errors**
- Error 445: Operator sequence issues
- Error 924: MCP separator issues
- Other error codes?

### Risk if Wrong
- May be diverse issues requiring many small fixes
- Some patterns may be unfixable without major emit_gams changes
- Could reveal deeper IR issues

### Estimated Research Time
2-3 hours (MCP generation, GAMS compilation, error analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.2: Why do 10 models have solve failures/mismatches despite successful translation?

### Priority
**High** - Affects 80% solve target

### Assumption
The 10 solve failures are caused by a mix of PATH solver configuration issues, numerical tolerance settings, and potentially nlp2mcp bugs that can be diagnosed and fixed.

### Research Questions
1. What are the specific solve outcomes for each of 10 models?
2. Are failures due to solver convergence, objective mismatch, or status mismatch?
3. Do failing models have unusual characteristics (size, nonlinearity, bounds)?
4. Can PATH solver options be tuned to improve convergence?
5. Are any failures due to incorrect MCP formulation?

### How to Verify

**Test Case 1: Categorize solve outcomes**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome != null and .solve_outcome != "solve_success") | {model: .model_name, outcome: .solve_outcome}'
```

**Test Case 2: Compare NLP vs MCP solutions**
- For objective mismatches, compare values
- Check if within reasonable tolerance
- Identify systematic bias

**Test Case 3: Test solver options**
```bash
# Try different PATH settings
# iterlimit, tolerance, pivoting strategy
```

### Risk if Wrong
- Some failures may be inherent to models (non-convex, poorly scaled)
- PATH solver limitations may not be fixable
- 80% target may be too ambitious

### Estimated Research Time
2-3 hours (outcome analysis, solver experiments)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.3: Can PATH solver configuration be improved to handle more models?

### Priority
**High** - Could improve solve rate without code changes

### Assumption
PATH solver has configuration options (tolerances, iteration limits, pivoting strategies) that can be tuned to improve solve success rate.

### Research Questions
1. What PATH solver options are currently being used?
2. What options are available for tuning?
3. Do different models need different settings?
4. Can we detect when default settings fail and retry with alternatives?
5. What's the performance impact of more aggressive settings?

### How to Verify

**Test Case 1: Document current settings**
```python
# Check how PATH is invoked in nlp2mcp
grep -r "path\|PATH" src/solve/*.py
```

**Test Case 2: Research PATH documentation**
- Available options and their effects
- Recommended settings for difficult problems

**Test Case 3: Experiment with options**
- Test failing models with different settings
- Document which settings help which models

### Risk if Wrong
- Settings that help some models may hurt others
- Performance overhead of retry strategies
- Limited improvement potential

### Estimated Research Time
2 hours (settings research, experiments)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.4: Are objective mismatches due to numerical tolerance or actual bugs?

### Priority
**Medium** - Affects solution validation accuracy

### Assumption
Objective mismatches between NLP and MCP solutions are primarily due to numerical tolerance differences and can be addressed by adjusting comparison thresholds.

### Research Questions
1. How large are the objective value differences?
2. Are differences systematic or random?
3. What tolerance is currently used for comparison?
4. Do reformulation steps introduce numerical error?
5. Is the NLP reference solution reliable?

### How to Verify

**Test Case 1: Extract objective values**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome == "compare_objective_mismatch") | {model: .model_name, nlp_obj: .nlp_objective, mcp_obj: .mcp_objective}'
```

**Test Case 2: Analyze magnitude of differences**
- Relative error vs absolute error
- Pattern in which models have larger errors

**Test Case 3: Test with relaxed tolerance**
- Increase tolerance and re-compare
- Determine reasonable tolerance bounds

### Risk if Wrong
- Loose tolerance may accept incorrect solutions
- Tight tolerance may reject equivalent solutions
- May be actual bugs rather than tolerance issues

### Estimated Research Time
1-2 hours (data analysis, tolerance testing)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.5: Is 80% solve success rate achievable given model complexity?

### Priority
**Medium** - Affects target feasibility assessment

### Assumption
The 80% solve success target is achievable because remaining failures are primarily due to fixable emit_gams.py bugs and solver configuration, not fundamental model issues.

### Research Questions
1. What percentage of failures are due to nlp2mcp bugs vs model issues?
2. Are failing models particularly complex or non-standard?
3. What's the solve rate for "easy" vs "hard" models?
4. Should we stratify targets by model complexity?
5. What's a realistic best-case solve rate?

### How to Verify

**Test Case 1: Categorize failures by root cause**
- nlp2mcp bug: Fixable
- Model issue: Not fixable
- Solver limitation: Possibly fixable

**Test Case 2: Analyze model characteristics**
- Size, nonlinearity, conditioning
- Correlate with solve success/failure

### Risk if Wrong
- 80% target may be unrealistic
- Effort may be wasted on unfixable issues
- Need to adjust expectations

### Estimated Research Time
1 hour (analysis, planning)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 3: Parse Improvements

## Unknown 3.1: What subcategories exist within the 97 `lexer_invalid_char` errors?

### Priority
**Critical** - Largest blocker (61% of parse failures)

### Assumption
The 97 lexer_invalid_char errors can be subcategorized into fixable patterns (hyphenated identifiers, special characters, quote handling) with varying fix complexity.

### Research Questions
1. How do the 97 errors break down by specific character/pattern?
2. What percentage are hyphenated identifier variants?
3. What percentage are special character issues (quotes, etc.)?
4. Are there patterns requiring grammar changes vs lexer changes?
5. Which subcategories have highest ROI (models/effort)?

### How to Verify

**Test Case 1: Extract error patterns**
```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .parse_error' | sort | uniq -c | sort -rn
```

**Test Case 2: Categorize by character type**
- Hyphen issues: `set-element`, `var-name`
- Quote issues: `'string'`, `"string"`
- Special chars: `@`, `#`, etc.

**Test Case 3: Estimate fixability**
- Simple lexer regex update: Easy
- Grammar rule changes: Medium
- Parser architecture changes: Hard

### Risk if Wrong
- Subcategories may be more diverse than expected
- Some patterns may be unfixable without major refactor
- +15-25 model target may be optimistic or conservative

### Estimated Research Time
2-3 hours (error extraction, categorization, analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.2: Can remaining hyphenated identifier patterns be fixed with lexer changes alone?

### Priority
**High** - Potentially high-ROI fix

### Assumption
Remaining hyphenated identifier issues can be addressed by extending the lexer regex patterns without requiring parser or grammar changes.

### Research Questions
1. What hyphenated patterns still fail after Sprint 16 fixes?
2. Are failures due to lexer tokenization or grammar rules?
3. Do some patterns conflict with operators (minus sign)?
4. Can we add negative lookahead to distinguish hyphen from minus?
5. What's the risk of breaking existing working patterns?

### How to Verify

**Test Case 1: Find hyphen-related failures**
```bash
grep -l '\-' data/gamslib/raw/*.gms | while read f; do
    model=$(basename $f .gms)
    if cat tests/output/pipeline_results.json | jq -e ".models[] | select(.model_name == \"$model\" and .parse_outcome == \"lexer_invalid_char\")" > /dev/null; then
        echo $model
    fi
done
```

**Test Case 2: Test lexer changes**
- Modify lexer regex
- Run on sample failing models
- Check for regressions

### Risk if Wrong
- Grammar changes may be needed
- Hyphen/minus ambiguity may be fundamental
- Could break working models

### Estimated Research Time
2 hours (pattern analysis, lexer experimentation)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.3: What causes the 14 `internal_error` parse failures?

### Priority
**High** - May indicate bugs or edge cases

### Assumption
Internal errors are caused by unhandled edge cases in the parser that can be fixed by adding proper error handling or extending grammar coverage.

### Research Questions
1. What specific internal errors occur (stack traces, error messages)?
2. Are errors in lexer, parser, or post-processing?
3. Do errors occur on specific GAMS constructs?
4. Are these defensive errors (expected) or actual bugs?
5. How many different root causes are there?

### How to Verify

**Test Case 1: Extract internal error details**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.parse_outcome == "internal_error") | {model: .model_name, error: .parse_error}'
```

**Test Case 2: Run with debug logging**
- Enable verbose parser output
- Trace where errors occur
- Categorize by root cause

### Risk if Wrong
- May be diverse issues requiring many fixes
- Some may be fundamental parser limitations
- Could indicate larger architecture issues

### Estimated Research Time
2 hours (error extraction, debugging)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.4: Are complex set data syntax patterns fixable or should they be deferred?

### Priority
**Medium** - Part of lexer_invalid_char subcategory

### Assumption
Complex set data syntax (nested structures, special formatting) can be handled by grammar extensions or should be documented as known limitations.

### Research Questions
1. What "complex set data" patterns appear in failing models?
2. Are these standard GAMS or unusual constructs?
3. What grammar changes would be needed?
4. Is full support necessary or can we skip these models?
5. What's the ROI compared to simpler fixes?

### How to Verify

**Test Case 1: Extract complex set patterns**
- Review error messages mentioning set data
- Examine source files for patterns

**Test Case 2: Research GAMS syntax**
- What set data formats are valid?
- Are there deprecated/uncommon formats?

### Risk if Wrong
- May require significant grammar work
- Could be low ROI if few models affected
- May have unforeseen interactions

### Estimated Research Time
1-2 hours (pattern research, feasibility assessment)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.5: How much of the 70% parse target depends on lexer fixes vs other improvements?

### Priority
**Medium** - Affects Sprint 17 planning

### Assumption
Reaching 70% parse rate (from 30%) requires +64 models, primarily achievable through lexer fixes (+40-50) with remaining from other improvements (+14-24).

### Research Questions
1. How many models are blocked purely by lexer issues?
2. How many have multiple blocking issues (lexer + other)?
3. What other parse improvements are needed (grammar, preprocessor)?
4. Is 70% realistic or should we set intermediate target?
5. What's the minimum viable improvement for Epic 3 success?

### How to Verify

**Test Case 1: Categorize all parse failures**
- lexer_invalid_char: 97
- internal_error: 14
- Other categories: ?

**Test Case 2: Estimate fix coverage**
- If we fix X% of lexer issues → Y models
- If we fix internal errors → Z models
- Total potential: Y + Z

### Risk if Wrong
- 70% may be unrealistic without major effort
- May need to adjust Epic 3 success criteria
- Could overcommit Sprint 17 scope

### Estimated Research Time
1 hour (data analysis, planning)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.6: Will parse improvements reveal new translation or solve issues?

### Priority
**Medium** - Affects overall pipeline improvement

### Assumption
As more models parse successfully, some will have new translation or solve issues, but the overall improvement trajectory remains positive.

### Research Questions
1. What's the historical ratio of parse → translate → solve success?
2. Are newly-parsing models likely to be "harder"?
3. Should we expect translate rate to drop as parse rate increases?
4. How should we track cascade effects?
5. Is overall pipeline success the right metric?

### How to Verify

**Test Case 1: Analyze Sprint 16 cascade**
- Parse: 34 → 48 (+14 models)
- Translate: 17 → 21 (+4 of 14 new, 29%)
- Solve: 3 → 11 (+8 models)
- Pattern: Not all improvements cascade

**Test Case 2: Project Sprint 17**
- If parse: 48 → 112 (+64)
- Expected new translate: +64 × 44% ≈ +28
- Expected new solve: +28 × 52% ≈ +15

### Risk if Wrong
- Pipeline targets may be misaligned
- Could focus on wrong stage
- May need different metrics

### Estimated Research Time
1 hour (analysis, projection)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 4: Detailed Error Analysis

## Unknown 4.1: Can error patterns be automatically categorized for faster triage?

### Priority
**High** - Affects analysis efficiency

### Assumption
Error messages contain enough structure (error codes, patterns) to enable automatic categorization, reducing manual analysis time.

### Research Questions
1. What structure exists in error messages?
2. Can we regex-match error categories?
3. Are GAMS error codes consistent and documented?
4. Should categorization be added to reporting module?
5. What's the accuracy of automatic categorization?

### How to Verify

**Test Case 1: Analyze error message structure**
```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | .parse_error // .translate_error // .solve_error' | head -50
```

**Test Case 2: Build categorization regex**
```python
patterns = {
    'lexer_char': r'Unexpected character',
    'domain_mismatch': r'domain.*mismatch',
    'unsupported_func': r'unsupported.*function',
}
```

**Test Case 3: Validate accuracy**
- Run automatic categorization
- Compare to manual categorization
- Measure precision/recall

### Risk if Wrong
- Automatic categorization may miss nuances
- Could misclassify related but different errors
- May require ongoing maintenance

### Estimated Research Time
1-2 hours (pattern analysis, prototype)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.2: What error information is most useful for debugging?

### Priority
**Medium** - Affects developer productivity

### Assumption
Useful debugging information includes: error message, line/column, source context, and stack trace (for internal errors).

### Research Questions
1. What information is currently captured in pipeline results?
2. What additional info would speed up debugging?
3. Should we capture more context (surrounding code)?
4. Is source file location preserved through pipeline?
5. How do developers currently debug failures?

### How to Verify

**Test Case 1: Review current error capture**
```bash
cat tests/output/pipeline_results.json | jq '.models[0]' | head -50
# What fields are available?
```

**Test Case 2: Survey debugging workflow**
- How are errors currently investigated?
- What information is missing?

### Risk if Wrong
- Captured info may be insufficient
- Too much info may be noise
- May need infrastructure changes

### Estimated Research Time
1 hour (analysis, survey)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.3: Are there correlations between error categories and model characteristics?

### Priority
**Medium** - May enable smarter prioritization

### Assumption
Error categories correlate with model characteristics (size, type, age), which can inform prioritization of fixes.

### Research Questions
1. Do larger models fail more often?
2. Do certain model types (NLP, MIP, CNS) have different error profiles?
3. Are older GAMSLib models more likely to use deprecated syntax?
4. Can we predict error likelihood from model metadata?
5. Should we prioritize by model importance?

### How to Verify

**Test Case 1: Extract model metadata**
```bash
# Model type, size, age from GAMSLib
```

**Test Case 2: Correlate with errors**
- Error category vs model type
- Error category vs model size
- Error category vs creation date

### Risk if Wrong
- Correlations may be weak or spurious
- May lead to wrong prioritization
- Metadata may not be reliable

### Estimated Research Time
1 hour (correlation analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.4: How should error analysis results feed into fix prioritization?

### Priority
**Medium** - Affects Sprint 17 planning

### Assumption
Error analysis should produce a prioritized list of fixes based on: (1) models affected, (2) fix complexity, and (3) cascade potential.

### Research Questions
1. What weighting should be used for prioritization?
2. Should ROI (models/effort) be the primary metric?
3. How to handle dependencies between fixes?
4. Should we prioritize end-to-end success or stage-by-stage?
5. How often should priorities be reassessed?

### How to Verify

**Test Case 1: Design prioritization formula**
```
Priority Score = (Models Affected × Cascade Factor) / Effort Hours
```

**Test Case 2: Apply to current errors**
- Calculate scores for all error categories
- Rank by score
- Validate against intuition

### Risk if Wrong
- Wrong prioritization wastes effort
- May miss high-value fixes
- Dependencies may invalidate ordering

### Estimated Research Time
1 hour (formula design, validation)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.5: What sample size is needed for reliable error pattern identification?

### Priority
**Low** - Affects analysis methodology

### Assumption
Analyzing 3-5 sample errors per category is sufficient to identify patterns and root causes.

### Research Questions
1. Is 3-5 samples enough or should we analyze all?
2. How should samples be selected (random, diverse, representative)?
3. Do some categories need more samples than others?
4. Can we use statistical sampling techniques?
5. What's the trade-off between thoroughness and speed?

### How to Verify

**Test Case 1: Analyze with different sample sizes**
- 3 samples → patterns identified?
- 5 samples → additional insights?
- All samples → diminishing returns?

**Test Case 2: Validate pattern reliability**
- Identify patterns from sample
- Test patterns on remaining errors
- Measure hit rate

### Risk if Wrong
- Too few samples: Miss important patterns
- Too many samples: Wasted effort
- Biased selection: Incorrect conclusions

### Estimated Research Time
30 minutes (methodology decision)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 5: Fix Complexity Estimation

## Unknown 5.1: How accurate are effort estimates for grammar/lexer changes?

### Priority
**High** - Affects Sprint 17 scheduling

### Assumption
Grammar and lexer changes can be estimated at 1-2 hours for simple fixes, 2-4 hours for medium, and 4-8 hours for complex changes, based on Sprint 16 experience.

### Research Questions
1. How did Sprint 16 estimates compare to actuals?
2. What factors caused estimate errors?
3. Are there hidden dependencies that add time?
4. Should we add buffer for testing/regression?
5. How much time is spent on non-coding work?

### How to Verify

**Test Case 1: Review Sprint 16 actuals**
- Estimated vs actual for each fix
- Calculate estimation accuracy
- Identify systematic bias

**Test Case 2: Factor in testing time**
- Unit tests for each fix
- Regression testing
- Documentation updates

### Risk if Wrong
- Underestimates lead to scope creep
- Overestimates lead to conservative targets
- Sprint 17 may be over/under-committed

### Estimated Research Time
1 hour (historical analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.2: What's the typical testing overhead for each fix type?

### Priority
**Medium** - Affects total effort calculation

### Assumption
Testing overhead is approximately 30-50% of implementation time: 30% for simple fixes (unit tests), 50% for complex fixes (integration tests).

### Research Questions
1. How many tests are needed per fix type?
2. What's the cost of regression testing?
3. Are there existing test patterns to follow?
4. Should we automate fix validation?
5. What's the cost of CI pipeline runs?

### How to Verify

**Test Case 1: Analyze Sprint 16 testing**
- New tests added per fix
- Time spent on test writing
- CI pipeline impact

**Test Case 2: Define testing standards**
- Unit tests required
- Integration tests required
- Performance tests (if applicable)

### Risk if Wrong
- Insufficient testing leads to regressions
- Excessive testing slows progress
- CI bottleneck issues

### Estimated Research Time
1 hour (analysis, standards definition)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.3: Are there hidden dependencies between fixes that affect ordering?

### Priority
**Medium** - Affects Sprint 17 sequencing

### Assumption
Most fixes are independent and can be parallelized, with only a few dependencies (e.g., lexer fix before grammar fix).

### Research Questions
1. What dependencies exist between planned fixes?
2. Can we identify blocking dependencies?
3. Should fixes be batched by dependency?
4. Are there conflicts between fixes?
5. What's the critical path for improvements?

### How to Verify

**Test Case 1: Map fix dependencies**
- List all planned fixes
- Identify prerequisites for each
- Build dependency graph

**Test Case 2: Identify conflicts**
- Fixes that modify same code
- Fixes that may interact negatively

### Risk if Wrong
- Ordering issues cause rework
- Blocked fixes delay progress
- Conflicts cause bugs

### Estimated Research Time
1 hour (dependency analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.4: How should we handle fixes that require major refactoring?

### Priority
**Low** - May not apply to Sprint 17

### Assumption
If a fix requires major refactoring (>8 hours), it should be deferred to future work unless critical for Sprint 17 targets.

### Research Questions
1. What threshold defines "major refactoring"?
2. How to assess if refactoring is necessary vs nice-to-have?
3. Should we do incremental refactoring or defer entirely?
4. What's the risk of technical debt from deferral?
5. How do we document deferred refactoring?

### How to Verify

**Test Case 1: Define refactoring criteria**
- Touches >5 files
- Changes core abstractions
- Requires extensive testing
- >8 hours estimated

**Test Case 2: Assess current fixes**
- Which planned fixes might need refactoring?
- What's the deferral impact?

### Risk if Wrong
- Major refactoring derails sprint
- Technical debt accumulates
- Wrong deferral decisions

### Estimated Research Time
30 minutes (criteria definition)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Template for New Unknowns

```markdown
## Unknown X.Y: [Brief description]

### Priority
**[Critical/High/Medium/Low]** - [Impact statement]

### Assumption
[What we assume to be true]

### Research Questions
1. [Specific question 1]
2. [Specific question 2]
3. [Specific question 3]

### How to Verify

**Test Case 1: [Name]**
```bash
# Commands to verify
```

**Test Case 2: [Name]**
[Description of verification approach]

### Risk if Wrong
- [Risk 1]
- [Risk 2]
- [Risk 3]

### Estimated Research Time
[X hours] ([what the time covers])

### Owner
[Owner name/team]

### Verification Results
🔍 Status: INCOMPLETE
```

---

# Next Steps

## Immediate Actions (Before Sprint 17 Day 1)

1. **Task 2: Detailed Error Analysis**
   - Run error extraction queries
   - Categorize all errors by pattern
   - Estimate fix complexity for each category

2. **Task 3: Translation Deep Dive**
   - Analyze 27 translation failures
   - Identify AD vs emit changes needed
   - Prioritize by impact and effort

3. **Task 4: MCP Compilation Analysis**
   - Generate MCP files for 8 path_syntax_error models
   - Compile with GAMS and capture errors
   - Map to emit_gams.py patterns

4. **Task 5: Lexer/Parser Improvement Plan**
   - Subcategorize 97 lexer errors
   - Estimate fixability of each subcategory
   - Create prioritized fix plan

5. **Task 6: Solve Investigation Plan**
   - Categorize 10 solve failures
   - Test PATH solver configurations
   - Identify fixable vs inherent issues

## During Sprint 17

1. Update verification status as unknowns are resolved
2. Add newly discovered unknowns
3. Track which fixes resolve which unknowns
4. Adjust targets based on findings

---

# Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Detailed Error Analysis | 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5 | Error extraction and categorization |
| Task 3: Translation Deep Dive | 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 | All translation improvement unknowns |
| Task 4: MCP Compilation Analysis | 2.1, 2.4 | Path syntax errors and output validation |
| Task 5: Lexer/Parser Improvement Plan | 3.1, 3.2, 3.4, 3.5 | Lexer subcategories and fix planning |
| Task 6: Solve Failure Investigation Plan | 2.2, 2.3, 2.5 | Solve failures and PATH configuration |
| Task 7: Documentation Inventory | - | No unknowns; documentation-focused |
| Task 8: Release Checklist | 5.1, 5.2, 5.3, 5.4 | Fix complexity and scheduling estimation |
| Task 9: Plan Sprint 17 Detailed Schedule | 3.5, 3.6 | Integrates all findings into schedule |

## Detailed Mapping

### Task 2: Detailed Error Analysis
**Unknowns Verified:** 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5

- **Unknown 3.1:** Subcategorizing lexer_invalid_char requires detailed error extraction
- **Unknown 3.3:** Internal error analysis requires examining specific error details
- **Unknown 4.1:** Automatic categorization feasibility assessed during analysis
- **Unknown 4.2:** Useful debug information identified through analysis process
- **Unknown 4.3:** Correlations identified by cross-referencing error data with model metadata
- **Unknown 4.4:** Prioritization formula validated against analyzed data
- **Unknown 4.5:** Sample size methodology tested during analysis

### Task 3: Translation Deep Dive
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

- **Unknown 1.1:** Missing AD functions identified by examining diff_unsupported_func errors
- **Unknown 1.2:** Domain mismatch patterns identified through detailed analysis
- **Unknown 1.3:** No-objective models analyzed for feasibility handling
- **Unknown 1.4:** Index offset patterns extracted and categorized
- **Unknown 1.5:** Dollar conditional patterns examined
- **Unknown 1.6:** Numerical errors traced to root cause
- **Unknown 1.7:** Translation improvement cascade assessed

### Task 4: MCP Compilation Analysis
**Unknowns Verified:** 2.1, 2.4

- **Unknown 2.1:** Path syntax error root causes identified through MCP generation/compilation
- **Unknown 2.4:** Objective mismatch analysis requires examining MCP output

### Task 5: Lexer/Parser Improvement Plan
**Unknowns Verified:** 3.1, 3.2, 3.4, 3.5

- **Unknown 3.1:** Lexer error subcategorization is core task
- **Unknown 3.2:** Hyphenated identifier fixability assessed
- **Unknown 3.4:** Complex set data patterns evaluated for fix/defer decision
- **Unknown 3.5:** Parse target breakdown calculated

### Task 6: Solve Failure Investigation Plan
**Unknowns Verified:** 2.2, 2.3, 2.5

- **Unknown 2.2:** Solve failure root causes categorized
- **Unknown 2.3:** PATH solver configuration options researched
- **Unknown 2.5:** 80% solve target feasibility assessed

### Task 8: Release Checklist
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

- **Unknown 5.1:** Effort estimates validated against Sprint 16 experience
- **Unknown 5.2:** Testing overhead standards defined
- **Unknown 5.3:** Fix dependencies mapped for scheduling
- **Unknown 5.4:** Major refactoring criteria established

### Task 9: Plan Sprint 17 Detailed Schedule
**Unknowns Verified:** 3.5, 3.6

- **Unknown 3.5:** Parse target breakdown integrated into schedule
- **Unknown 3.6:** Cascade effects factored into planning

---

## References

- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Sprint 17 section (lines 455-576)
- [SPRINT_RETROSPECTIVE.md](../SPRINT_16/SPRINT_RETROSPECTIVE.md) - Lessons and recommendations
- [SPRINT_BASELINE.md](../../testing/SPRINT_BASELINE.md) - Sprint 16 baseline metrics
- [GAMSLIB_STATUS.md](../../testing/GAMSLIB_STATUS.md) - Current model status
- [baseline_metrics.json](../../testing/gamslib/baseline_metrics.json) - Quantitative data
