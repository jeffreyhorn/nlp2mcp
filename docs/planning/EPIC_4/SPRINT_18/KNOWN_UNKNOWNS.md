# Sprint 18 Known Unknowns

**Created:** February 5, 2026
**Status:** Active - Pre-Sprint 18
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 18 GAMSLIB syntactic validation, emit_gams.py solve fixes, and parse quick wins

---

## Overview

This document identifies all assumptions and unknowns for Sprint 18 features **before** implementation begins. This proactive approach continues the highly successful methodology from previous sprints that prevented late-stage surprises.

**Sprint 18 Scope:**
1. GAMSLIB Syntactic Correctness Validation (~10-12h) — test_syntax.py, SYNTAX_ERROR_REPORT.md, corpus reclassification, infeasible/unbounded documentation
2. emit_gams.py Solve Fixes — Part 1 (~10-12h) — table data emission, computed parameter assignments
3. Parse Quick Win: Put Statement Format (~2h) — `:width:decimals` syntax support

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 9-86 for complete Sprint 18 deliverables and acceptance criteria.

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 4: 23 unknowns, zero blocking issues
- Sprint 5: 22 unknowns, all resolved on schedule
- Sprint 6: 22 unknowns, enabled realistic scope setting
- Sprint 7: 25 unknowns, informed parser prioritization
- Sprint 17: Retrospective identified solve-vs-pipeline metric confusion — a known unknown would have caught this earlier

**Epic 4 Key Context:** Baseline (v1.1.0) — Parse 61/160 (38.1%), Translate 42/61 (68.9%), Solve 12/42 (28.6%), Full Pipeline 12/160 (7.5%). Sprint 18 is the first sprint of Epic 4, targeting full GAMSLIB coverage.

---

## How to Use This Document

### Before Sprint 18 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 18
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

**Total Unknowns:** 24
**By Priority:**
- Critical: 4 (unknowns that could derail sprint)
- High: 9 (unknowns requiring upfront research)
- Medium: 7 (unknowns that can be resolved during implementation)
- Low: 4 (nice-to-know, low impact)

**By Category:**
- Category 1 (GAMSLIB Syntactic Validation): 8 unknowns
- Category 2 (emit_gams.py): 8 unknowns
- Category 3 (Parse Quick Win): 4 unknowns
- Category 4 (Infrastructure & Process): 4 unknowns

**Estimated Research Time:** 22-32 hours (full range; prep plan uses 24-30 hour working range)

---

## Table of Contents

1. [Category 1: GAMSLIB Syntactic Validation Unknowns](#category-1-gamslib-syntactic-validation-unknowns)
2. [Category 2: emit_gams.py Unknowns](#category-2-emit_gamspy-unknowns)
3. [Category 3: Parse Quick Win Unknowns](#category-3-parse-quick-win-unknowns)
4. [Category 4: Infrastructure & Process Unknowns](#category-4-infrastructure--process-unknowns)

---

# Category 1: GAMSLIB Syntactic Validation Unknowns

## Unknown 1.1: Does `gams action=c` reliably detect all syntax errors?

### Priority
**Critical** — Core to syntactic validation component

### Assumption
Running `gams <model>.gms action=c` will correctly identify all models with GAMS-level syntax errors (mismatched parentheses, undefined symbols, etc.) and return a non-zero exit code for failures.

### Research Questions
1. Does `action=c` catch all compile-time errors, or only a subset?
2. What exit code does GAMS return on compilation failure vs. success?
3. Are there models that pass `action=c` but fail at execution time with errors that look like syntax issues?
4. Does `action=c` follow `$include` directives and check included files?
5. How does `action=c` interact with `$if`/`$else` conditionals — does it check both branches?

### How to Verify

**Test Case 1: Known syntax error model**
```bash
gams camcge.gms action=c
echo $?
# Expected: non-zero exit code
```

**Test Case 2: Known clean model**
```bash
gams himmel11.gms action=c
echo $?
# Expected: exit code 0
```

**Test Case 3: Model with runtime-only errors**
```bash
# Find a model with division by zero in parameter computation
gams <model>.gms action=c
# Expected: exit code 0 (action=c skips execution)
```

**Test Case 4: Model with $include**
```bash
gams <model_with_include>.gms action=c
# Expected: compilation follows includes
```

**Test Case 5: Model with conditional compilation**
```bash
gams <model_with_if>.gms action=c
# Expected: document behavior — does it check both branches?
```

### Risk if Wrong
- **False negatives:** Models with syntax errors pass `action=c` and remain in corpus, inflating denominator
- **False positives:** Clean models fail `action=c` due to environmental issues, shrinking corpus incorrectly
- **Script redesign:** If `action=c` is unreliable, need alternative validation approach (>8h rework)

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 5, 2026):**

1. **Exit codes confirmed:** `gams action=c` returns exit code 0 for successful compilation, exit code 2 for compilation errors.

2. **All 160 corpus models compile successfully.** Tested all models; zero GAMS syntax errors found.

3. **Error detection is reliable:** Intentional syntax error test confirmed that `action=c` correctly identifies and reports errors with detailed messages in .lst file.

4. **`camcge` compiles successfully** — contrary to the original assumption that it had mismatched parentheses. The nlp2mcp `lexer_invalid_char` error is due to multi-line expression continuation that nlp2mcp doesn't handle, not a GAMS syntax issue.

5. **Conditional compilation:** Not tested in depth, but irrelevant since no models have syntax errors.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` for full test results.

---

## Unknown 1.2: How many GAMSLIB models actually have GAMS syntax errors?

### Priority
**High** — Determines corpus denominator and metric recalculation impact

### Assumption
Between 5 and 15 of the 160 convex models have GAMS-level syntax errors, reducing the valid corpus to approximately 145-155 models.

### Research Questions
1. How many of the 99 parse-failing models fail because of GAMS syntax errors vs. nlp2mcp limitations?
2. Is `camcge` the only known syntax-error model, or are there more?
3. Do any of the 61 currently-parsing models have hidden GAMS compilation issues?
4. What is the overlap between `lexer_invalid_char` failures and GAMS syntax errors?
5. Will the syntax error count significantly change the pipeline metrics when recalculated?

### How to Verify

**Step 1:** Run `gams action=c` on a stratified sample of 12+ models (5 passing, 5 `lexer_invalid_char`, 2 known issues)
**Step 2:** Extrapolate from sample to estimate total syntax error count
**Step 3:** Cross-reference with nlp2mcp pipeline failure categories
**Step 4:** Calculate impact on corpus denominator and all pipeline percentages

### Risk if Wrong
- **Overestimate (>20 errors):** Corpus shrinks dramatically, metrics jump artificially — misleading progress signal
- **Underestimate (<3 errors):** Syntactic validation component delivers less value than planned
- **Wrong classification:** Some nlp2mcp limitations misclassified as GAMS errors or vice versa

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings (February 5, 2026):**

**Original assumption was WRONG.** The assumption was 5-15 models have GAMS syntax errors. The actual count is **ZERO**.

| Test Category | Models Tested | GAMS Errors Found |
|---------------|---------------|-------------------|
| Full corpus | 160 | 0 |
| lexer_invalid_char | 74 | 0 |
| internal_error | 23 | 0 |
| semantic_undefined_symbol | 2 | 0 |

**Key insight:** ALL 99 nlp2mcp parse failures are due to nlp2mcp grammar/parser limitations, NOT GAMS-level syntax errors. The corpus does not need to be reduced.

**Impact:**
- Corpus denominator remains 160 (no reduction)
- `syntax_error` exclusion reason currently has count 0 (no models require it), but remains supported in schema for future discoveries
- Sprint 18 syntactic validation component is simpler than planned (~50% time savings)

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` for full test results.

---

## Unknown 1.3: Can GAMS .lst file error messages be parsed programmatically?

### Priority
**High** — Required for `test_syntax.py` and SYNTAX_ERROR_REPORT.md generation

### Assumption
GAMS .lst files contain compilation errors in a consistent, parseable format with error type, message, and line number that can be extracted programmatically.

### Research Questions
1. What is the exact format of compilation errors in .lst files?
2. Are error messages consistent across different types of syntax errors?
3. Do .lst files use standard delimiters (e.g., `****` markers) that can be reliably parsed?
4. Are line numbers in .lst files 1-indexed and relative to the original source?
5. How are errors from `$include`d files reported — with the included file path?

### How to Verify

**Test Case 1: Compile model with known error**
```bash
gams camcge.gms action=c
cat camcge.lst | grep -A5 "\*\*\*\*"
# Expected: consistent error format with line number and message
```

**Test Case 2: Compare multiple error formats**
- Compile 3+ models with different error types
- Compare .lst output format
- Identify common parsing pattern

**Test Case 3: Error from included file**
- Find a model that includes files
- Introduce an error in the included file
- Check if .lst reports the correct file and line

### Risk if Wrong
- **Inconsistent format:** Need multiple parsing strategies, `test_syntax.py` becomes complex
- **Missing line numbers:** SYNTAX_ERROR_REPORT.md less useful for GAMS team
- **Encoding issues:** Non-ASCII characters in .lst files break parser

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 5, 2026):**

The .lst file error format is consistent and parseable:

**Error format structure:**
```
<line_number>  <source_code>
****           $<error_code1>,<error_code2>,...
**** <code>  <error_message>

**** N ERROR(S)   M WARNING(S)
```

**Example (from intentional syntax error test):**
```
   4  a(i) = i + ;
****           $148,119,133
**** 119  Number (primary) expected
**** 133  Incompatible operands for addition
**** 148  Dimension different

**** 3 ERROR(S)   0 WARNING(S)
```

**Regex patterns for parsing:**
```python
ERROR_CODE_LINE = r'^\*\*\*\*\s+\$[\d,]+$'
ERROR_MESSAGE = r'^\*\*\*\*\s+(\d+)\s+(.+)$'
ERROR_SUMMARY = r'^\*\*\*\*\s+(\d+)\s+ERROR\(S\)'
```

**Note:** While the format is parseable, no actual errors were found in the 160-model corpus, so this capability is not needed for Sprint 18.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` Appendix B.

---

## Unknown 1.4: Are the 2 `model_infeasible` models inherently infeasible or MCP formulation bugs?

### Priority
**Critical** — Determines whether models are excluded or kept as bugs to fix

### Assumption
At least one of the 2 `model_infeasible` models is inherently infeasible (the NLP itself has no feasible solution), while the other may be an MCP formulation bug.

### Research Questions
1. Which 2 models are flagged as `model_infeasible`?
2. Does the original NLP solve successfully with GAMS (model status 1 = optimal)?
3. If the NLP is feasible but the MCP is infeasible, what's wrong with the KKT formulation?
4. Are there unbounded models in the corpus that should also be excluded?
5. Can infeasible models produce meaningful MCP formulations, or should they always be excluded?

### How to Verify

**Step 1:** Query `gamslib_status.json` for `model_infeasible` entries
**Step 2:** For each model, solve the original NLP:
```bash
gams <model>.gms
# Check: Model Status 1 = optimal (NLP is feasible)
# Check: Model Status 4 = infeasible (NLP truly infeasible)
```
**Step 3:** If NLP is feasible but MCP is infeasible → KKT bug → keep in corpus
**Step 4:** If NLP is infeasible → would require future schema work to add `infeasible` exclusion reason (out of scope for Sprint 18)
**Step 5:** Check for unbounded indicators across all models

### Risk if Wrong
- **Wrong exclusion:** Excluding a model that has a fixable MCP bug reduces our corpus unnecessarily
- **Wrong inclusion:** Keeping a truly infeasible model wastes solve debugging time in later sprints
- **Missed unbounded:** Unbounded models cause degenerate KKT conditions, confusing failure analysis

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Finding:** Both `model_infeasible` models are **MCP formulation bugs**, NOT inherently infeasible NLPs.

**Models identified:**
| Model | MCP Status | Original NLP Status | Determination |
|-------|------------|---------------------|---------------|
| circle | Model Status 5 (Locally Infeasible) | **Optimal** (obj=5.277) | KKT bug |
| house | Model Status 5 (Locally Infeasible) | **Optimal** (obj=4500) | KKT bug |

**Investigation details:**

1. **circle** - Smallest circle problem
   - Original NLP: Solves optimally with CONOPT (r ≈ 5.277)
   - MCP: PATH reports "Locally Infeasible" after 760 iterations
   - **Root cause:** The original uses random data (`uniform(1,10)`), which generates different data each run. The MCP output re-runs `uniform()` generating different points than the NLP, causing infeasibility.

2. **house** - House plan design
   - Original NLP: Solves optimally with CONOPT (total area = 4500 sq ft)
   - MCP: PATH reports "Locally Infeasible" but shows objective 27.7055 (incorrect)
   - **Root cause:** Likely constraint qualification failure or incorrect Lagrangian formulation

**Unbounded models check:** None found. All models with `mcp_solve` results have either `model_optimal` (12 models), `model_infeasible` (2 models), `path_syntax_error` (17 models), or `path_solve_terminated` (11 models).

**Recommendation:** Keep both models in corpus as **bugs to fix**, not candidates for exclusion. An `infeasible` exclusion reason is not needed for these models. However, `circle` may need special handling due to random data regeneration.

---

## Unknown 1.5: What exclusion categories should the database support?

### Priority
**High** — Schema design for corpus reclassification

### Assumption
Three exclusion reasons were initially assumed: `syntax_error`, `infeasible`, `unbounded`. Investigation revealed only `syntax_error` is needed (see Verification Results below). The final schema supports: `syntax_error`, `data_dependency`, `license_restricted`, `other`.

### Research Questions
1. Are three categories sufficient, or do we need more (e.g., `excluded_duplicate`, `excluded_nonconvex`)?
2. Should exclusion be a separate field or embedded in `pipeline.status`?
3. How should excluded models interact with existing pipeline data — retain or clear?
4. Should exclusion be reversible (model returns to corpus if GAMS team fixes syntax error)?
5. How do reporting scripts currently calculate metrics — will they automatically respect exclusions?

### How to Verify

**Step 1:** Review `gamslib_status.json` schema and `src/reporting/` code
**Step 2:** Identify all possible reasons for exclusion
**Step 3:** Design schema that supports current and future exclusion reasons
**Step 4:** Verify reporting scripts can filter excluded models without breaking

### Risk if Wrong
- **Insufficient categories:** Need to redesign schema later when new exclusion reasons emerge
- **Breaking change:** Reporting scripts crash on new schema fields
- **Data loss:** Clearing pipeline data for excluded models loses useful diagnostic info

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Finding:** Only **one exclusion reason is currently needed**: `syntax_error`. The other two assumed reasons (`infeasible`, `unbounded`) are not needed based on investigation.

**Analysis of exclusion needs:**

| Exclusion Reason | Needed? | Evidence |
|------------------|---------|----------|
| `syntax_error` | ✅ Yes | Task 2 found 0 GAMS syntax errors in current gamslib. Reason needed for potential future discoveries or if GAMS team reports syntax issues. |
| `infeasible` | ❌ No | Both `model_infeasible` models (circle, house) are MCP bugs, not inherently infeasible NLPs. Keep in corpus. |
| `unbounded` | ❌ No | No unbounded models found in corpus. All solve attempts completed normally. |

**Revised recommendation:**
1. Implement `exclusion.reason = "syntax_error"` for models with confirmed GAMS syntax errors
2. Do NOT add `infeasible` or `unbounded` to the `reason` enum at this time
3. Use `exclusion.reason = "other"` with `exclusion.details` for ad-hoc exclusions without schema changes

**Schema suggestion (aligned with SCHEMA_DESIGN.md):**
```json
{
  "model_id": "hypothetical_model",
  "exclusion": {
    "excluded": true,
    "reason": "syntax_error",
    "details": "GAMS compilation error: unmatched parenthesis",
    "reversible": true
  }
}
```

This design is extensible — new exclusion reasons can be added to the enum in future schema versions, or use `reason="other"` with `details` for ad-hoc cases.

---

## Unknown 1.6: How should metrics be recalculated with a reduced valid corpus?

### Priority
**High** — Affects all Sprint 18+ metric comparisons

### Assumption
All pipeline metrics (parse rate, translate rate, solve rate, full pipeline) should use the valid corpus (total - excluded) as denominator, and both "total corpus" and "valid corpus" metrics should be tracked for transparency.

### Research Questions
1. Should Sprint 17 baseline metrics be retroactively recalculated against the valid corpus?
2. How to present the metric change to avoid confusion (e.g., "parse rate improved from 38.1% to 43.2% after corpus reclassification")?
3. Should the valid corpus denominator be stored in the database or calculated dynamically?
4. Do reporting scripts (`status_analyzer.py`, `progress_analyzer.py`, `generate_report.py`) need code changes?
5. Should GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md auto-reports be updated to show both denominators?

### How to Verify

**Step 1:** Calculate hypothetical metrics with corpus reduced by 5, 10, and 15 models
**Step 2:** Review `src/reporting/` source to identify all denominator references
**Step 3:** Prototype metrics recalculation with reduced corpus
**Step 4:** Verify reporting scripts can handle the new denominator

### Risk if Wrong
- **Metric confusion:** Stakeholders don't understand why metrics changed between sprints
- **Reporting bugs:** Scripts break or show incorrect percentages
- **Historical comparison:** Can't compare Sprint 17 vs Sprint 18 metrics meaningfully

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**Decision:** Do NOT retroactively recalculate v1.1.0 baseline.

**Metrics recalculation rules:**

| Metric | Formula | Denominator |
|--------|---------|-------------|
| Parse Rate | parse_success / valid_corpus | valid_corpus |
| Translate Rate | translate_success / parse_success | parse_success |
| Solve Rate | solve_success / translate_success | translate_success |
| Full Pipeline | full_success / valid_corpus | valid_corpus |

**Key decisions:**
1. Only Parse Rate and Full Pipeline use `valid_corpus` as denominator
2. Translate and Solve rates are relative to previous stage (unchanged)
3. Historical baseline NOT retroactively changed
4. Store both `total_corpus` and `valid_corpus` in `baseline_metrics.json` for transparency

**Reporting script impact:**
- `data_loader.py`: No changes needed (uses `baseline_metrics.json`)
- `status_analyzer.py`: Minor update to add `valid_corpus` to `StatusSummary`
- `progress_analyzer.py`: Add `denominator_note` for sprint comparisons
- `markdown_renderer.py`: Display valid corpus count in reports

**Current situation:** Since Task 2 found 0 GAMS syntax errors, `valid_corpus = total_corpus = 160`. No immediate script changes are required.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md` Section "Metrics Recalculation Rules".

---

## Unknown 1.7: Does `gams action=c` require solver licensing?

### Priority
**Medium** — Could block CI/automated testing if license needed

### Assumption
`gams action=c` (compile only) does NOT require solver licensing — it only checks GAMS syntax without invoking any solver.

### Research Questions
1. Can `action=c` run with a demo/community GAMS license?
2. Does compilation check require access to solver-specific declarations (e.g., `option mcp=path`)?
3. Can `test_syntax.py` run in CI environments without a full GAMS license?
4. What GAMS license is currently available on the development machine?

### How to Verify

**Test:** Run `gams action=c` on a model that references PATH solver:
```bash
gams model_with_path.gms action=c
# Expected: compiles successfully (solver not invoked during compilation)
```

### Risk if Wrong
- **CI blocked:** Can't run `test_syntax.py` in CI without GAMS license
- **Development blocked:** Developers without full license can't validate syntax
- Low overall impact since development already has GAMS installed

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

Solver licensing is NOT required for `action=c` compilation:

| Test Case | Solver Used | Exit Code | Result |
|-----------|-------------|-----------|--------|
| cesam.gms | MCP solver (PATH) | 0 | ✅ Compiles without license |
| All 160 models | Various | 0 | ✅ All compile regardless of solver |

**Key findings:**
1. `action=c` restricts GAMS to compilation phase — solvers are never invoked
2. The `solve` statement is parsed but NOT executed in compile-only mode
3. No license warnings or errors appear during compilation
4. `test_syntax.py` can run in any environment with a GAMS installation (even demo/community)

**Conclusion:** CI and developer environments can use `gams action=c` without full solver licensing.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/GAMS_ACTION_C_RESEARCH.md` Part 2, Test Scenario 9.

---

## Unknown 1.8: What is the expected runtime for compiling all 160 models?

### Priority
**Low** — Affects `test_syntax.py` design (sequential vs. parallel)

### Assumption
Compiling all 160 models sequentially with `gams action=c` takes less than 30 minutes, making sequential execution acceptable for `test_syntax.py`.

### Research Questions
1. How long does `gams action=c` take for a single model (small, medium, large)?
2. Is the bottleneck GAMS startup time or actual compilation?
3. Would parallel execution significantly reduce total time?
4. Should `test_syntax.py` include a progress bar or timeout per model?

### How to Verify

**Test:** Time compilation of 5 models:
```bash
time gams himmel11.gms action=c    # Small model
time gams trnsport.gms action=c    # Medium model
time gams camcge.gms action=c      # Large model (with error)
```
Extrapolate: 160 models × average_time = total_time

### Risk if Wrong
- **Too slow:** Script takes hours, needs parallelization (adds complexity)
- Low impact — can always add parallelization later

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 5, 2026):**

| Metric | Value |
|--------|-------|
| Average compilation time per model | 0.16 seconds |
| Total time for 160 models | 25.9 seconds |
| Estimated with script overhead | ~30-45 seconds |

**Key findings:**
1. Sequential execution is fast enough — no parallelization needed
2. GAMS startup time dominates (compilation itself is instantaneous for most models)
3. No timeout handling needed — all models complete in <1 second
4. A progress bar would be nice but not essential given the ~30 second total runtime

**Conclusion:** The assumption is verified. `test_syntax.py` can use simple sequential execution.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/CORPUS_SURVEY.md` Finding 4.

---

# Category 2: emit_gams.py Unknowns

## Unknown 2.1: Which specific models fail due to table data emission?

### Priority
**Critical** — Must confirm before implementing fix

### Assumption
Approximately 4 of the 17 `path_syntax_error` models fail specifically because `src/emit/original_symbols.py` cannot correctly emit GAMS table data structures in the MCP output.

### Research Questions
1. Which of the 17 `path_syntax_error` models use GAMS tables in their original source?
2. For table-using models, does the generated MCP output contain malformed table syntax?
3. What specific table structures fail: 1-D, 2-D, multi-dimensional?
4. Is the root cause in `original_symbols.py` or in the IR representation of tables?
5. Are there models that use tables but currently succeed (providing positive examples)?

### How to Verify

**Step 1:** List all `path_syntax_error` models from database
**Step 2:** For each, check original source for `Table` declarations
**Step 3:** For table-using models, generate MCP output and compare table sections
**Step 4:** Compile MCP output with GAMS to get specific error line/message
**Step 5:** Trace error to `original_symbols.py` code

### Risk if Wrong
- **Wrong model list:** Fix targets wrong models, no improvement in solve count
- **Wrong root cause:** Fix doesn't address actual emission bug, wasted sprint time
- **Estimate off:** More or fewer than 4 models affected, schedule needs adjustment

### Estimated Research Time
3-4 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings (February 6, 2026):**

**The original assumption was WRONG.** Zero models fail due to table data emission. Tables are parsed as `ParameterDef` objects and emit correctly.

| Finding | Detail |
|---------|--------|
| Table data failures | **0 models** |
| Actual failure categories | See Unknown 2.6 for full taxonomy |

**Key insight:** GAMS tables are parsed into `ParameterDef` with the table data stored in `values`. The `emit_original_parameters()` function handles this correctly. The assumption that table data emission was a major blocker was incorrect.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md` for detailed analysis of all 17 `path_syntax_error` models.

---

## Unknown 2.2: Which specific models fail due to computed parameter assignments?

### Priority
**Critical** — Must confirm before implementing fix

### Assumption
Approximately 4 of the 17 `path_syntax_error` models fail specifically because `src/emit/original_symbols.py` cannot correctly emit computed parameter assignments (expressions in parameter definitions) in the MCP output.

### Research Questions
1. Which `path_syntax_error` models use computed parameter assignments (not static data)?
2. What types of computed parameters fail: simple expressions, conditional, loop-based?
3. Does the emitter attempt to re-emit the expression or emit the computed value?
4. Is the root cause missing expression handling or wrong syntax generation?
5. Are there overlap models that have both table data AND computed parameter issues?

### How to Verify

**Step 1:** From the `path_syntax_error` catalog (Task 4 Step 1), isolate non-table failures
**Step 2:** For each, check original source for parameter assignments with expressions
**Step 3:** Compare original parameter definitions with emitted MCP output
**Step 4:** Identify the specific emission failure (missing assignment, wrong syntax, etc.)

### Risk if Wrong
- **Wrong model list:** Similar to Unknown 2.1 — fix targets wrong models
- **Wrong approach:** If the fix requires IR changes, not just emitter changes, the 4-5h estimate is too low
- **Overlap with tables:** Some models may have both issues, complicating diagnosis

### Estimated Research Time
3-4 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**5 models** fail due to computed parameter assignment emission:

| Model | Parameters | Computation Type | Needed for MCP? |
|-------|-----------|------------------|-----------------|
| ajax | `mtr(m,avail-h)`, `par(g,demand)` | Intermediate calc | No |
| demo1 | `croprep(revenue,c)`, `croprep(crep,total)`, `labrep(total,lrep)` | Post-solve reporting | No |
| mathopt1 | `report(x1,diff)`, `report(x2,diff)` | Post-solve comparison | No |
| mexss | `d(steel,j)`, `muf(i,j)`, `muv(j)`, `mue(i)`, `pd(c)`, `pv(c)`, `pe(c)` | Pre-processing | No (overlap with set quoting) |
| sample | `w(h)`, `tpop`, `k1(h,j)`, `k2(j)` | Pre-processing | No (ordering issue) |

**Key insight:** All computed parameter assignments can be SKIPPED entirely:
- Post-solve assignments (demo1, mathopt1) are never needed for MCP
- Pre-processing assignments (ajax, mexss, sample) fail due to ordering/dependency issues
- The KKT transformation uses static parameter values from `emit_original_parameters()`

**Recommended fix:** Skip `emit_computed_parameter_assignments()` entirely (2h effort).

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md` for detailed analysis.

---

## Unknown 2.3: Are table data and computed parameters the top two emit_gams.py blockers?

### Priority
**High** — Validates Sprint 18 scope and prioritization

### Assumption
Table data emission and computed parameter assignments are the two highest-impact emit_gams.py fixes, collectively unblocking ~8 of the 17 `path_syntax_error` models.

### Research Questions
1. What is the complete breakdown of `path_syntax_error` failure subcategories?
2. Are there other emit_gams.py issues (e.g., set emission, variable declarations) that affect more models?
3. Could fixing a different issue unblock more models with less effort?
4. What are the remaining ~9 `path_syntax_error` models blocked by?
5. Should Sprint 18 priorities be adjusted based on the actual failure breakdown?

### How to Verify

**Step 1:** Catalog all 17 `path_syntax_error` models by failure subcategory
**Step 2:** Count models per subcategory
**Step 3:** Rank subcategories by model count (highest impact first)
**Step 4:** Verify that table data + computed params are #1 and #2

### Risk if Wrong
- **Mispriorization:** Sprint 18 focuses on lower-impact fixes while higher-impact ones are deferred
- **Schedule waste:** 10-12h allocated to emit_gams.py produces fewer than expected model fixes
- **Opportunity cost:** Better ROI fixes exist but are not in Sprint 18 scope

### Estimated Research Time
1-2 hours (part of Tasks 4 and 5 analysis)

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings (February 6, 2026):**

**The original assumption was WRONG.** Table data and computed parameters are NOT the top two blockers. The actual taxonomy is:

| Category | Models | Count | Top Blocker? |
|----------|--------|-------|--------------|
| Set element quoting | ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut | 6 | **#1** |
| Computed parameter assignment | ajax, demo1, mathopt1, mexss, sample | 5 | **#2** |
| Bound multiplier dimension | alkyl, bearing, + 3 partial | 5 | **#3** |
| Multi-dim parameter data | chenery, orani, + 1 partial | 3 | #4 |
| Undefined function (psi) | mingamma | 1 | #5 |
| MCP mapping issues | least | 1 | #6 |
| **Table data emission** | **none** | **0** | **NOT A BLOCKER** |

**Key insight:** The top blockers are:
1. Set element quoting (6 models, 2-3h fix) - BEST ROI
2. Computed parameter assignment (5 models, but skip is 2h fix)
3. Bound multiplier dimension (5 models, 4-5h fix)

Table data emission was assumed to be a top blocker but is actually not an issue at all.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md` for complete taxonomy.

---

## Unknown 2.4: Does fixing table data emission require IR changes or only emitter changes?

### Priority
**High** — Affects implementation complexity and time estimate

### Assumption
Table data emission can be fixed entirely within `src/emit/original_symbols.py` without changes to the IR, parser, or other modules.

### Research Questions
1. Does the IR correctly represent table data structures, or is information lost during parsing?
2. Can `original_symbols.py` access all necessary table information (headers, data, dimensions)?
3. Are there table features that the parser doesn't capture (e.g., sparse tables, column headers)?
4. Would fixing the emitter alone produce correct GAMS table syntax for all affected models?
5. If IR changes are needed, how extensive are they?

### How to Verify

**Step 1:** Read `src/emit/original_symbols.py` — understand current table emission logic
**Step 2:** Read `src/ir/symbols.py` — check how table data is stored in IR
**Step 3:** For an affected model, compare IR table representation with original GAMS source
**Step 4:** Determine if IR contains sufficient information for correct emission

### Risk if Wrong
- **IR changes needed:** Implementation expands from 4-5h to 8-12h, schedule impact
- **Parser changes needed:** Even more scope expansion if parser doesn't capture table structure
- **Cascading effects:** IR changes may require updating normalization, AD, or KKT modules

### Estimated Research Time
2-3 hours (part of Task 4 analysis)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED (N/A - Table data emission not needed)

**Findings (February 6, 2026):**

**This unknown is moot** because table data emission is not a blocker. However, the analysis confirms:

1. **Tables are parsed correctly:** The parser handles `Table` blocks and stores data in `ParameterDef.values`
2. **IR representation is sufficient:** No IR changes needed for table emission
3. **Emitter works correctly:** `emit_original_parameters()` handles table data properly

The original question assumed table data emission was broken, but it works correctly. No fix is needed.

**Evidence:** All 17 `path_syntax_error` models were analyzed. None fail due to table data emission. See `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md`.

---

## Unknown 2.5: Should computed parameter fixes re-emit expressions or emit static values?

### Priority
**High** — Design decision affecting fix approach

### Assumption
Computed parameter fixes should re-emit the original computation expression rather than evaluating and emitting static values, because static values may not be available without running the GAMS model.

### Research Questions
1. Does the IR store the computation expression for computed parameters?
2. If the IR only stores the final value, can we recover the expression?
3. Do computed parameters depend on other computed parameters (chains)?
4. Would emitting static values be simpler and equally correct?
5. Are there cases where re-emitting the expression produces different results than the original?

### How to Verify

**Step 1:** Check IR representation of computed parameters vs. static parameters
**Step 2:** For affected models, determine if expressions or values are available
**Step 3:** Test both approaches on a simple case:
```gams
Parameter a(i); a(i) = 2 * ord(i);
```
- Re-emit: `a(i) = 2 * ord(i);`
- Static: `Parameter a(i) / i1 2, i2 4, i3 6 /;`

### Risk if Wrong
- **Expression not available:** IR doesn't store expressions, must use static values (or change IR)
- **Expression changed:** Re-emitting in different context produces different semantics
- **Dependencies broken:** Computed parameter depends on model data not available in MCP output

### Estimated Research Time
2-3 hours (part of Task 5 analysis)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**Design Decision: SKIP computed parameter assignments entirely.**

Analysis of all 5 affected models shows:
1. **Post-solve assignments** (demo1, mathopt1): Never needed for MCP - used for reporting
2. **Pre-processing assignments** (ajax, mexss, sample): Fail due to ordering/dependency issues

**Why SKIP is the right approach:**
- The IR stores expressions in `ParameterDef.expressions`, but re-emitting them fails due to:
  - Missing dependencies (symbols not defined in MCP context)
  - Wrong ordering (values referenced before computed)
  - Set element quoting issues (overlaps with another fix)
- Emitting static values requires evaluating GAMS expressions in Python (complex)
- The KKT transformation uses static parameter data from `emit_original_parameters()`
- MCP formulation doesn't need these intermediate computed values

**Implementation:**
```python
def emit_computed_parameter_assignments(model_ir: ModelIR) -> str:
    # Skip all computed parameter assignments for MCP output
    return ""
```

**Effort:** 2 hours (vs. 8-10h for complex re-emit/static approach)
**Risk:** Low - verified that 12 currently-solving models don't use computed param assignments

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/COMPUTED_PARAM_ANALYSIS.md` for detailed rationale.

---

## Unknown 2.6: What is the full `path_syntax_error` failure taxonomy?

### Priority
**Medium** — Useful for Sprint 18 and future sprint planning

### Assumption
The 17 `path_syntax_error` models can be classified into 4-6 distinct failure subcategories, with table data and computed parameters being the two largest.

### Research Questions
1. What are all the distinct failure modes in the 17 `path_syntax_error` models?
2. How many models fall into each subcategory?
3. Are there single-model failures (unique issues) vs. clustered failures (shared root cause)?
4. Which subcategories are easiest to fix (quick wins for Sprint 19)?
5. Is the taxonomy stable, or will new failure modes emerge as other issues are fixed?

### How to Verify

**Step 1:** For each `path_syntax_error` model, generate MCP output and compile with GAMS
**Step 2:** Extract the GAMS compilation error message
**Step 3:** Categorize errors into subcategories
**Step 4:** Create a taxonomy table with model counts per subcategory

### Risk if Wrong
- **Incomplete taxonomy:** Missing failure modes cause surprises in Sprint 18
- **Wrong categorization:** Models misclassified, fix applied to wrong issue
- Low overall risk — taxonomy improves over time

### Estimated Research Time
2-3 hours (part of Tasks 4 and 5)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

The complete taxonomy of 17 `path_syntax_error` models has been established:

| Category | Models | Count | GAMS Error Codes | Fix Location |
|----------|--------|-------|------------------|--------------|
| Set element quoting | ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut | 6 | 120, 145, 149, 340 | emit/expr_to_gams.py |
| Computed param assignment | ajax, demo1, mathopt1, mexss, sample | 5 | 121, 140, 141, 148 | emit/original_symbols.py |
| Bound multiplier dimension | alkyl, bearing (+ 3 partial) | 5 | 69, 483 | kkt/bound_multipliers.py |
| Multi-dim parameter data | chenery, orani (+ 1 partial) | 3 | 161, 170 | emit/original_symbols.py |
| Undefined function (psi) | mingamma | 1 | 140, 121 | emit/expr_to_gams.py |
| MCP mapping issues | least | 1 | 66, 256 | emit/model.py |

**Key findings:**
1. **6 distinct categories** (matches assumption of 4-6)
2. **Table data is NOT a category** (contrary to original assumption)
3. **Clustered failures:** ps2_* family + pollut (6 models) share set element quoting root cause
4. **Quick wins:** Set element quoting (2-3h for 6 models), skip computed params (2h for 5 models)
5. **Taxonomy is stable:** Based on GAMS compilation errors, not nlp2mcp internals

**Recommended Sprint 18 priorities by ROI:**
1. Set element quoting: 6 models / 2.5h = 2.4 ROI
2. Skip computed params: 5 models / 2h = 2.5 ROI
3. psi→digamma: 1 model / 1.5h = 0.7 ROI

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/TABLE_DATA_ANALYSIS.md` for detailed model-by-model analysis.

---

## Unknown 2.7: Will emit_gams.py fixes break currently-solving models?

### Priority
**Medium** — Regression risk assessment

### Assumption
Fixing table data emission and computed parameter assignments will not affect models that currently solve successfully (the 12 `model_optimal` models).

### Research Questions
1. Do any of the 12 currently-solving models use tables or computed parameters?
2. If so, are they using the same code paths that will be modified?
3. Can we run regression tests on all 12 solving models after each fix?
4. Is there a risk that changing `original_symbols.py` affects models that don't use tables/params?

### How to Verify

**Step 1:** Check whether any of the 12 solving models use tables or computed parameters
**Step 2:** After implementing fixes, re-run pipeline on all 12 solving models
**Step 3:** Verify all 12 still achieve `model_optimal`
**Step 4:** If any regress, roll back and investigate

### Risk if Wrong
- **Regression:** Fixing new models breaks existing ones — net zero or negative progress
- **Subtle bugs:** Fix passes for new models but introduces a subtle issue in existing ones
- Medium risk — mitigated by running full pipeline retest (Sprint 18 Day 6)

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.8: How will the pipeline retest be structured after emit_gams.py fixes?

### Priority
**Low** — Process question, not blocking

### Assumption
The pipeline retest (Sprint 18 Day 6) will re-run the full pipeline on all valid corpus models, recording updated metrics in `gamslib_status.json` and comparing to the v1.1.0 baseline.

### Research Questions
1. Should the retest run on all 160 models or only the valid corpus?
2. Should excluded models be retested (to verify exclusion is correct)?
3. How long does a full pipeline retest take?
4. Should the retest include the solution comparison stage (which Sprint 17 skipped)?

### How to Verify

**Step 1:** Time a full pipeline run on current codebase
**Step 2:** Design retest script or procedure
**Step 3:** Define what "success" looks like for the retest

### Risk if Wrong
- **Incomplete retest:** Missing models or stages leads to inaccurate metrics
- Low impact — can re-run if initial retest is insufficient

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: Parse Quick Win Unknowns

## Unknown 3.1: Is the `:width:decimals` syntax the only put statement format specifier?

### Priority
**Medium** — Grammar design completeness

### Assumption
The primary put statement format specifier is `:width:decimals`, but there may also be a three-part variant `:width:decimals:exponent` for scientific notation.

### Research Questions
1. What is the full GAMS put statement format specifier syntax?
2. Is there a `:width:decimals:exponent` variant?
3. Can format specifiers apply to any put item (variables, parameters, text, expressions)?
4. Are there other format controls (alignment, padding, sign display)?
5. Does the `:` separator conflict with any existing GAMS syntax in our grammar?

### How to Verify

**Step 1:** Review GAMS documentation for put statement format specifiers
**Step 2:** Test with GAMS:
```gams
file f /output.txt/; put f;
put 3.14159:10:4 /;      * width 10, 4 decimals
put 3.14159:10:4:2 /;    * width 10, 4 decimals, 2 exponent digits (if supported)
put 'text':20 /;          * text with width
```
**Step 3:** Document the full syntax for grammar extension

### Risk if Wrong
- **Incomplete grammar:** Fix handles `:width:decimals` but misses `:width:decimals:exponent`, leaving some models unparseable
- **Grammar conflict:** `:` separator conflicts with other syntax rules
- Low overall risk — can extend grammar incrementally

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Finding:** There is no `:width:decimals:exponent` variant. Supported per-item forms are `:width` and `:width:decimals` (optionally with alignment).

**Full syntax specification:**
- `item:width` - width only
- `item:width:decimals` - width and decimals
- `item:{<|>|<>}width:decimals` - with optional alignment prefix (`<` left, `>` right, `<>` center)

Scientific notation is controlled by global file settings (`.nr=2`), not per-item format specifiers.

**Source:** GAMS UG_Put documentation, verified February 6, 2026

---

## Unknown 3.2: Do the 4 target put-statement models have secondary blocking issues?

### Priority
**High** — Determines if parse quick win actually unblocks models

### Assumption
The 4 target models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge) fail ONLY because of the `:width:decimals` syntax, and fixing it will allow them to parse successfully.

### Research Questions
1. For each model, is `:width:decimals` the ONLY parse failure?
2. Are there other unsupported GAMS features in these models (e.g., put_utility, file statements)?
3. After fixing `:width:decimals`, do any models hit new parse errors?
4. Are these models simple enough to also translate and solve, or only parse?
5. What pipeline stage would each model reach after the fix?

### How to Verify

**Step 1:** For each model, attempt to parse with current grammar — record error
**Step 2:** Manually edit model to remove `:width:decimals` syntax
**Step 3:** Re-parse — does the model now succeed?
**Step 4:** If not, record the secondary error
**Step 5:** For models that parse, attempt translate and solve

### Risk if Wrong
- **Wasted effort:** Fix allows parsing but secondary errors mean models still fail
- **False progress:** Claim "+4 parse models" but none actually progress through pipeline
- Medium risk — even partial progress (parsing) has value

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Finding:** 3 of 4 models fail due to `:width:decimals`. One model (stdcge) has a DIFFERENT blocking issue.

**Per-model results:**

| Model | Blocks on `:width:decimals`? | Secondary Issues | Fix Will Help? |
|-------|------------------------------|------------------|----------------|
| ps5_s_mn | ✅ Yes | None | ✅ Yes |
| ps10_s | ✅ Yes | None | ✅ Yes |
| ps10_s_mn | ✅ Yes | None | ✅ Yes |
| stdcge | ❌ No | Missing `put_stmt_nosemi` | ❌ No (separate fix) |

**stdcge issue:** Uses `loop(j, put j.tl);` without semicolon before loop close. Requires `put_stmt_nosemi` variant for `exec_stmt_final`.

**Conclusion:** The `:width:decimals` fix will unblock **3 models**. stdcge needs a separate `put_stmt_nosemi` grammar fix (~30 min additional work).

---

## Unknown 3.3: Will the grammar extension conflict with existing colon usage in GAMS?

### Priority
**Medium** — Grammar correctness

### Assumption
Adding `:width:decimals` support to put statement rules won't create ambiguity with other GAMS uses of the colon character (e.g., in set definitions, conditional assignments).

### Research Questions
1. Where else does GAMS use the colon character?
2. Can Lark disambiguate `:` in put statements from `:` in other contexts?
3. Is the put statement scope clearly bounded (between `put` keyword and `;`)?
4. Are there edge cases where `:` could be ambiguous?

### How to Verify

**Step 1:** Search GAMS grammar for all colon usages
**Step 2:** Design grammar rule that only matches `:` after put items
**Step 3:** Run existing test suite after grammar change — verify no regressions

### Risk if Wrong
- **Grammar ambiguity:** Parser produces wrong AST for existing models
- **Regression:** Currently-parsing models break
- Medium risk — Lark's priority rules can usually resolve ambiguity

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Finding:** No conflict. The colon in format specifiers is context-specific to `put_item`.

**Existing colon usage in grammar:**
- `option_format` rule: `ID ":" NUMBER (":" NUMBER)*` - e.g., `option decimals:8`

**Why no conflict:**
1. Put format specifiers only match within `put_item` context
2. `put_item` is only matched inside `put_stmt`
3. `option_stmt` and `put_stmt` are separate statement rules
4. The `:` format suffix is only parsed in `put_item` via `put_format`, so it can't be confused with `option_format` or other statement contexts

**Grammar design:** Add `put_format` rule that only applies within `put_item`:
```lark
put_item: STRING put_format?
        | "/" -> put_newline
        | expr put_format?

put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?
PUT_ALIGN: "<>" | "<" | ">"
```

---

## Unknown 3.4: Are put statements semantically significant for MCP generation?

### Priority
**Low** — Determines how much effort to invest in put statement support

### Assumption
Put statements are output/reporting statements with no effect on the mathematical model. They can be parsed and skipped (not translated to MCP) without affecting correctness.

### Research Questions
1. Do put statements only produce output, or can they have side effects?
2. Can we safely parse and ignore put statements for MCP generation purposes?
3. Is there any interaction between put statements and model variables/equations?
4. Should the emitter include put statements in MCP output or strip them?

### How to Verify

**Step 1:** Review GAMS documentation — confirm put statements are output-only
**Step 2:** Check if any target models depend on put statement results for model behavior
**Step 3:** Confirm MCP generation doesn't need put statement information

### Risk if Wrong
- **Functional impact:** Put statements affect model behavior (extremely unlikely)
- Very low risk — put statements are universally output-only in GAMS

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Finding:** Put statements are output-only with no side effects on the mathematical model.

**Put statement purposes:**
- Writing results to CSV files
- Generating reports after solve
- Debugging output

**Semantic significance:** None for MCP generation. Put statements:
- Do not affect variable values
- Do not modify equations
- Do not influence the optimization problem
- Are only used for post-solve reporting

**Recommendation:** Parse and ignore put statements for MCP generation. The emitter does not need to include put statements in MCP output.

---

# Category 4: Infrastructure & Process Unknowns

## Unknown 4.1: Is the v1.1.0 baseline accurate and reproducible?

### Priority
**High** — Sprint 18 acceptance criteria depend on accurate baseline

### Assumption
The v1.1.0 baseline metrics (Parse 61/160, Translate 42/61, Solve 12/42, Full Pipeline 12/160) are accurate, reproducible, and consistent with `gamslib_status.json`.

### Research Questions
1. Do all 3204 tests pass on current main branch?
2. Does `gamslib_status.json` contain exactly the reported counts?
3. Are there any discrepancies between documented metrics and actual database state?
4. Is the "Full Pipeline 12/160" metric actually solve-stage success (Sprint 17 didn't re-run comparison)?
5. What is the true full pipeline count if comparison is re-run?

### How to Verify

**Step 1:** Run `pytest tests/ -v` on main — verify 3204+ tests pass
**Step 2:** Query database and count pipeline statuses
**Step 3:** Compare counts with documented v1.1.0 metrics
**Step 4:** Record baseline commit hash and verification date

### Risk if Wrong
- **Metrics drift:** Sprint 18 measures progress against wrong baseline, misleading results
- **Confusion:** Solve vs. full pipeline confusion from Sprint 17 carries into Sprint 18
- Medium risk — verification is straightforward

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**The v1.1.0 baseline is accurate and reproducible.**

| Metric | Expected | Verified | Status |
|--------|----------|----------|--------|
| Test suite | 3204+ pass | 3204 passed, 10 skipped, 1 xfailed | ✅ |
| Parse success | 61 | 61 | ✅ |
| Parse failure | 99 | 99 | ✅ |
| Translate success | 42 | 42 | ✅ |
| Translate failure | 19 | 19 | ✅ |
| Solve (model_optimal) | 12 | 12 | ✅ |
| Convex models (corpus) | 160 | 160 | ✅ |

**Verified 12 model_optimal models:** apl1p, blend, himmel11, hs62, mathopt2, mhw4d, mhw4dx, prodmix, rbrock, trig, trnsport, trussm

**Baseline verification:**
- Commit hash: `aed804ae50d2296464b17dfe22b6c8e69edf236d`
- Verification date: February 6, 2026
- Branch: `planning/sprint18-task9`

**Note:** "Full Pipeline 12/160" refers to solve-stage success. Sprint 17 did not re-run the solution comparison stage, so this is a proxy metric. See Unknown 4.3 for comparison stage status.

---

## Unknown 4.2: Does the database schema support adding new fields without breaking existing tools?

### Priority
**Medium** — Schema extensibility

### Assumption
Adding `gams_syntax` and `exclusion` fields to `gamslib_status.json` entries won't break existing scripts that read the database, because they access specific fields by name and ignore unknown fields.

### Research Questions
1. Do `src/reporting/` scripts use strict schema validation or flexible field access?
2. Will adding new top-level fields to a JSON entry cause any script to crash?
3. Do scripts iterate over all fields or only access known ones?
4. Is there a JSON schema definition that would need updating?
5. Are there external tools (notebooks, dashboards) that read the database?

### How to Verify

**Step 1:** Review `src/reporting/status_analyzer.py`, `failure_analyzer.py`, `progress_analyzer.py`
**Step 2:** Check for strict field access vs. flexible access patterns
**Step 3:** Add a dummy field to one entry and run reporting scripts
**Step 4:** Verify no crashes or incorrect behavior

### Risk if Wrong
- **Scripts crash:** Adding new fields breaks reporting — blocks Sprint 18 progress
- **Silent errors:** Scripts ignore new fields but produce wrong metrics
- Medium risk — fixable but could waste 2-4 hours during sprint

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**Adding new fields will NOT break existing tools.**

**Evidence from code review:**

1. **`src/reporting/data_loader.py`:**
   - Uses `baseline_metrics.json`, not `gamslib_status.json`
   - Uses `@dataclass` with `from_dict()` methods that explicitly extract known fields
   - Unknown fields are silently ignored (not iterated over)

2. **`src/reporting/analyzers/*.py`:**
   - Access specific fields via `baseline.parse.success`, etc.
   - No iteration over all model_entry fields
   - No strict schema validation at runtime

3. **`data/gamslib/schema.json`:**
   - Uses `additionalProperties: false` for strict validation
   - **DOES need updating** to add `gams_syntax` and `exclusion` definitions
   - This is a documentation/validation concern, not a runtime crash risk

4. **External tools:**
   - No external notebooks or dashboards currently read `gamslib_status.json`
   - `baseline_metrics.json` is the primary aggregated data source

**Schema extensibility design:**
- Add `gams_syntax` and `exclusion` as **optional** properties in `model_entry`
- Bump `schema_version` to `"2.1.0"` (minor version = backward-compatible)
- Existing tools ignore new fields; new tools can read them

**Conclusion:** Schema changes are safe. Update `schema.json` to document the new fields for validation purposes.

**Evidence:** See `docs/planning/EPIC_4/SPRINT_18/SCHEMA_DESIGN.md` Section "Migration Strategy".

---

## Unknown 4.3: Should Sprint 18 re-run the solution comparison stage?

### Priority
**Medium** — Affects Full Pipeline metric accuracy

### Assumption
Sprint 18 should re-run the solution comparison stage during the Day 6 pipeline retest, to establish a true Full Pipeline metric (not just solve-stage success as in Sprint 17).

### Research Questions
1. How long does the solution comparison stage take for all solving models?
2. Is the comparison infrastructure still functional from Sprint 16?
3. What tolerance should be used for solution matching?
4. Will newly-solving models (from emit_gams.py fixes) need comparison baselines?
5. Should comparison failures be tracked as a new pipeline category?

### How to Verify

**Step 1:** Review Sprint 16 comparison infrastructure
**Step 2:** Run comparison on current 12 solving models
**Step 3:** Document results and time required
**Step 4:** Decide if comparison should be part of Sprint 18 standard pipeline

### Risk if Wrong
- **Metric ambiguity:** Without comparison, "Full Pipeline" remains a proxy for solve success
- **Missed regressions:** Models that solve but give wrong answers go undetected
- Medium risk — comparison can be added in Sprint 19 if not feasible in Sprint 18

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**Sprint 18 does NOT need to re-run the solution comparison stage for baseline verification.**

**Rationale:**
1. The current 12 `model_optimal` models have been verified to solve correctly with PATH
2. Solution comparison was completed in Sprint 16 for those models
3. Re-running comparison for baseline verification would not change the metrics
4. Sprint 18 focus is on emit_gams.py fixes, not comparison infrastructure

**Recommendation:**
- For Sprint 18 Day 6 pipeline retest: Record solve stage success/failure
- Newly-solving models (from emit_gams.py fixes) should be manually verified
- Full comparison stage can be re-enabled in Sprint 19 if needed

**Comparison infrastructure status:**
- `src/pipeline/compare.py` exists and is functional
- Last full comparison run: Sprint 16
- Time estimate for full comparison: ~30 minutes for 12 models

---

## Unknown 4.4: Are there any GAMS environment changes since v1.1.0 that could affect results?

### Priority
**Low** — Environmental stability check

### Assumption
The GAMS installation (version 51.3.0, PATH solver 5.2.01) has not changed since Sprint 17, and will produce identical compilation and solve results.

### Research Questions
1. Has GAMS been updated since Sprint 17?
2. Has PATH solver version changed?
3. Are there any environment variable changes that could affect GAMS behavior?
4. Could OS updates affect GAMS performance or behavior?

### How to Verify

```bash
gams --version   # Expected: 51.3.0
which gams       # Expected: known location
```

### Risk if Wrong
- **Version mismatch:** New GAMS version produces different compilation results
- **Solver changes:** PATH updates change solve behavior
- Very low risk — unlikely to change between sprints

### Estimated Research Time
15 minutes

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings (February 6, 2026):**

**GAMS environment is unchanged since v1.1.0.**

| Component | Version | Status |
|-----------|---------|--------|
| GAMS Base Module | 51.3.0 (38407a9b, Oct 27, 2025) | ✅ Unchanged |
| PATH Solver | 103001 (libpath52.dylib) | ✅ Unchanged |
| GAMS Location | /Library/Frameworks/GAMS.framework/Versions/51/Resources/ | ✅ Standard |
| Platform | macOS (DEX-DEG x86 64bit) | ✅ Compatible |

**Environment verification:**
```bash
$ gams ?
GAMS Base Module 51.3.0 38407a9b Oct 27, 2025 DEG x86 64bit/macOS

$ which gams
/Library/Frameworks/GAMS.framework/Versions/51/Resources/gams
```

**Conclusion:** The GAMS environment is stable. Results from Sprint 18 will be directly comparable to v1.1.0 baseline.

---

## Template for New Unknowns

When new unknowns are discovered during Sprint 18, use this template:

```markdown
## Unknown X.N: [Title]

### Priority
**[Critical/High/Medium/Low]** — [Brief justification]

### Assumption
[What we currently assume to be true]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify
[Concrete test cases or experiments]

### Risk if Wrong
[Impact on sprint if assumption is incorrect]

### Estimated Research Time
[Hours]

### Owner
[Team/person]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

1. Complete all prep tasks (Tasks 2-9) which verify these unknowns
2. Update this document with verification results as research is completed
3. Resolve all Critical unknowns before Sprint 18 Day 1
4. Resolve all High unknowns before their implementation day
5. Use as living document during sprint — add new unknowns as discovered
6. Review daily during standup

**Success Criteria:**
- All Critical unknowns (4) resolved before Day 1
- All High unknowns (9) resolved before their implementation day
- Medium unknowns resolved during implementation
- Low unknowns can be deferred or resolved opportunistically
- Zero late-surprise discoveries that require >4 hours of unplanned work

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from PREP_PLAN.md) verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Survey GAMSLIB Corpus for Syntax Error Indicators | 1.1, 1.2, 1.3, 1.8 | Sample compilation tests scope the validation work; tests `action=c` behavior, error format, and runtime |
| Task 3: Research GAMS `action=c` Compilation Mode | 1.1, 1.3, 1.7, 1.8 | Deep research into `action=c` semantics, exit codes, .lst format, licensing, and timing |
| Task 4: Analyze emit_gams.py Table Data Failures | 2.1, 2.3, 2.4, 2.6 | Identifies affected models, validates table data is top blocker, checks IR vs emitter scope, catalogs failure taxonomy |
| Task 5: Analyze emit_gams.py Computed Parameter Failures | 2.2, 2.3, 2.5, 2.6 | Identifies affected models, validates computed params are top blocker, decides re-emit vs static approach, extends taxonomy |
| Task 6: Audit Put Statement `:width:decimals` Syntax | 3.1, 3.2, 3.3, 3.4 | Full put statement syntax research, verifies target models, checks grammar conflicts, confirms semantic insignificance |
| Task 7: Review Infeasible/Unbounded Model Status | 1.4, 1.5 | Investigates 2 infeasible models, determines exclusion categories needed |
| Task 8: Design Corpus Reclassification Schema | 1.5, 1.6, 4.2 | Designs exclusion schema, metrics recalculation rules, and verifies reporting script compatibility |
| Task 9: Verify Sprint 18 Baseline Metrics | 4.1, 4.3, 4.4 | Verifies v1.1.0 baseline, checks comparison stage status, confirms GAMS environment unchanged |
| Task 10: Plan Sprint 18 Detailed Schedule | 2.7, 2.8 | Schedule incorporates regression testing plan and pipeline retest structure |

**Coverage Check:**
- All 24 unknowns are covered by at least one prep task
- Critical unknowns (1.1, 1.4, 2.1, 2.2) have dedicated tasks with thorough analysis
- Some unknowns are verified by multiple tasks (e.g., 1.1 by Tasks 2 and 3; 2.3 by Tasks 4 and 5)
- Tasks 4 and 5 share the `path_syntax_error` failure taxonomy work (Unknown 2.6)

---

## Document History

- February 5, 2026: Initial creation (pre-Sprint 18, Task 1 of PREP_PLAN.md)
