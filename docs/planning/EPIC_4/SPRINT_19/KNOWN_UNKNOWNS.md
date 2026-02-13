# Sprint 19 Known Unknowns

**Created:** February 12, 2026
**Status:** Active — Pre-Sprint 19
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 19 Major Parse Push, Sprint 18 Deferred Items, and architectural issue resolution

---

## Overview

This document identifies all assumptions and unknowns for Sprint 19 features **before** implementation begins. This proactive approach continues the methodology that achieved excellent results in Sprint 18 (24 unknowns documented; all critical/high items verified; zero late surprises).

**Sprint 19 Scope (43-53 hours across 5 workstreams):**
1. Sprint 18 Deferred Items (~17-21h) — MCP bug fixes, subset preservation, reserved word quoting, lexer analysis, put statement format
2. lexer_invalid_char Fixes (~14-18h) — Complex set data syntax, compile-time constants, remaining clusters
3. internal_error Investigation (~6-8h) — Error classification and initial fixes (23 → below 15)
4. IndexOffset IR Design (~4h) — Lead/lag indexing design and parser spike
5. FIX_ROADMAP Items — Cross-indexed sums (ISSUE_670), table continuation (ISSUE_392), table description (ISSUE_399), MCP pairing (ISSUE_672)

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 147-264 for complete Sprint 19 deliverables and acceptance criteria. See `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` for architectural issue priorities.

**Lessons from Sprint 18:** Known Unknowns process rated as top success factor. Key lesson: assumptions about top blockers were wrong (table data emission assumed to be #1 blocker, but actual #1 was set element quoting). Upfront verification prevented wasted effort.

**Epic 4 Key Context:** Baseline (v1.2.0) — Parse 62/160, Solve 20, path_syntax_error 7, Full Pipeline 7. Sprint 19 targets: lexer_invalid_char ~95 → below 50, internal_error 23 → below 15, parse rate ≥55%.

---

## How to Use This Document

### Before Sprint 19 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 19
1. Review daily during standup
2. Add newly discovered unknowns in the "Newly Discovered Unknowns" section
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 26
**By Priority:**
- Critical: 8 (unknowns that could derail sprint)
- High: 13 (unknowns requiring upfront research)
- Medium: 5 (unknowns that can be resolved during implementation)
- Low: 0 (nice-to-know, low impact; none currently identified)

**By Category:**
- Category 1 (MCP Infeasibility Bug Fixes): 3 unknowns
- Category 2 (Subset Relationship Preservation): 3 unknowns
- Category 3 (Reserved Word Quoting): 3 unknowns
- Category 4 (Lexer Error Deep Analysis): 3 unknowns
- Category 5 (Put Statement Format Support): 2 unknowns
- Category 6 (Complex Set Data Syntax): 4 unknowns
- Category 7 (internal_error & IndexOffset): 4 unknowns
- Category 8 (Cross-Indexed Sums & Architectural Issues): 4 unknowns

**Estimated Research Time:** 30-38 hours

---

## Table of Contents

1. [Category 1: MCP Infeasibility Bug Fixes](#category-1-mcp-infeasibility-bug-fixes)
2. [Category 2: Subset Relationship Preservation](#category-2-subset-relationship-preservation)
3. [Category 3: Reserved Word Quoting](#category-3-reserved-word-quoting)
4. [Category 4: Lexer Error Deep Analysis](#category-4-lexer-error-deep-analysis)
5. [Category 5: Put Statement Format Support](#category-5-put-statement-format-support)
6. [Category 6: Complex Set Data Syntax](#category-6-complex-set-data-syntax)
7. [Category 7: internal_error & IndexOffset](#category-7-internal_error--indexoffset)
8. [Category 8: Cross-Indexed Sums & Architectural Issues](#category-8-cross-indexed-sums--architectural-issues)

---

# Category 1: MCP Infeasibility Bug Fixes

## Unknown 1.1: Does the circle model's `uniform()` issue require capturing original random values or a different approach?

### Priority
**Critical** — Determines fix strategy for circle model (one of 2 MCP infeasibility bugs)

### Assumption
The circle model's MCP infeasibility is caused by `uniform()` regenerating different random data in the MCP context. Capturing and hardcoding the original random values in the MCP output will fix the infeasibility.

### Research Questions
1. Does the circle model use `uniform()` in parameter initialization only, or also in constraints?
2. If we hardcode the original random values, do we need to intercept them at parse time or at GAMS execution time?
3. Can the IR capture the evaluated values from the original NLP solve, or only the expression `uniform(1,10)`?
4. Are there other models in the corpus that use `uniform()` or other stochastic functions?
5. Would setting a GAMS random seed (`execseed`) be a simpler alternative to value capture?

### How to Verify
- Run `gams circle.gms` twice and compare parameter values — confirm they differ
- Test with `execseed=12345` — does fixing the seed make the MCP solvable?
- Check IR representation of `uniform()` calls — is the expression or the value stored?

### Risk if Wrong
- Fix approach requires GAMS execution integration (capturing values at runtime), which is far more complex than simple IR manipulation (~12h instead of ~3h)
- Seed approach may not work if `uniform()` is called in a non-deterministic order

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.2: What is the root cause of the house model's MCP infeasibility?

### Priority
**Critical** — Determines fix strategy for house model (one of 2 MCP infeasibility bugs)

### Assumption
The house model's MCP infeasibility is caused by a constraint qualification failure or incorrect Lagrangian formulation, not a data issue like circle.

### Research Questions
1. Does the original NLP solve successfully with CONOPT? (Known: yes, obj=4500)
2. What specific constraint qualification is violated in the MCP formulation?
3. Are there active constraints at the optimal solution whose multipliers have wrong signs?
4. Does the KKT system have the correct number of equations and variables?
5. Is the issue in stationarity generation, bound multiplier handling, or MCP pairing?

### How to Verify
- Compare the original NLP solution (variable values, multipliers) with the MCP system
- Check stationarity equations for the house model by hand for a few key variables
- Run the MCP with relaxed bounds to see if it converges to a different solution

### Risk if Wrong
- If the issue is in KKT assembly (not just emission), the fix may require changes to `src/kkt/stationarity.py` or `src/kkt/assemble.py`, significantly expanding scope from 3-4h to 8-12h
- May reveal a systemic issue affecting other models

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.3: Will fixing circle and house affect any currently-solving models?

### Priority
**Medium** — Regression risk for MCP bug fixes

### Assumption
Fixes for circle and house are isolated to those models' specific issues (random data for circle, formulation for house) and will not affect the 20 currently-solving models.

### Research Questions
1. Do the fixes touch shared code paths (stationarity, bound multipliers, emission)?
2. If the fix modifies `src/kkt/` modules, which other models use the same code paths?
3. Can we scope the fix to model-specific handling or must it be a general change?

### How to Verify
- After implementing fixes, run full regression on all 20 solving models
- Check if fix changes any code path used by currently-solving models

### Risk if Wrong
- Regression in solving models (net zero or negative progress)
- Medium risk — mitigated by regression testing

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 2: Subset Relationship Preservation

## Unknown 2.1: Which specific models fail due to missing subset relationships?

### Priority
**High** — Must confirm affected models before implementing fix

### Assumption
Approximately 3 models fail because `src/emit/emit_gams.py` does not preserve set-subset relationships (e.g., `Set i(j)` declaring i as a subset of j) in emitted domain declarations.

### Research Questions
1. Which of the current pipeline failures are caused by missing subset declarations?
2. What specific GAMS error codes do these models produce?
3. Do these models fail at parse, translate, or solve stage?
4. Are the subset relationships captured in the IR (`ModelIR`), or lost during parsing?
5. What GAMS syntax is needed in the MCP output to declare subsets correctly?

### How to Verify
- Query pipeline results for models with GAMS Error 140 ("Unknown symbol") or Error 149 ("Uncontrolled set")
- For each candidate, check original source for `Set i(j)` or `Set i(*) / subset_elements /` declarations
- Generate MCP output and compare set declarations with original

### Risk if Wrong
- Wrong model list means fix targets wrong issue (wasted 4-5h)
- If subset info is lost during parsing, fix requires parser changes (not just emitter), expanding scope

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.2: Does the IR preserve set-subset relationship metadata?

### Priority
**High** — Determines whether fix is emitter-only or requires parser changes

### Assumption
The IR stores set definitions with their domain information (parent set), and the emitter simply doesn't use this information when generating set declarations.

### Research Questions
1. How does `src/ir/symbols.py` represent set definitions — is there a `domain` or `parent_set` attribute?
2. Does the parser extract subset relationships from GAMS source?
3. If the IR doesn't preserve this information, what parser changes are needed?
4. How does the IR handle `Set i(j)` vs `Set i / elem1, elem2 /` — are these represented differently?

### How to Verify
- Read `src/ir/symbols.py` `SetDef` class and check for domain/parent attributes
- Parse a model with subset declarations and inspect the IR
- Check if `emit_original_sets()` in `src/emit/original_symbols.py` has access to domain info

### Risk if Wrong
- If IR doesn't store subset info, fix requires parser changes (~4h extra)
- Sprint 18 emission fixes may have changed how set info is stored

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.3: Will subset preservation interact with Sprint 18's element literal quoting fix?

### Priority
**Medium** — Interaction risk between two emission fixes

### Assumption
The subset preservation fix and the Sprint 18 element literal quoting fix operate on different code paths and will not conflict.

### Research Questions
1. Does element literal quoting affect set element references in subset declarations?
2. Could a subset declaration like `Set i(j) / 'elem1', 'elem2' /` require both quoting AND subset handling?
3. Are there models that need both fixes simultaneously?

### How to Verify
- Check if any of the ~3 subset-affected models also have quoting issues
- Review the Sprint 18 quoting fix in `src/emit/expr_to_gams.py` for set declaration handling

### Risk if Wrong
- Fixes conflict, requiring careful integration (2-3h extra debugging)
- Low probability — emission code paths are fairly independent

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 3: Reserved Word Quoting

## Unknown 3.1: Which GAMS reserved words appear as identifiers in the corpus?

### Priority
**High** — Must have complete list before implementing quoting

### Assumption
A small set of GAMS reserved words (e.g., `set`, `model`, `solve`, `variable`, `equation`, `parameter`, `table`, `option`, `display`, `put`, `file`, `loop`, `if`, `else`, `while`, `for`, `repeat`, `until`, `abort`, `scalar`) appear as user-defined identifiers in approximately 2 models, causing GAMS compilation errors in the MCP output.

### Research Questions
1. Which specific models use GAMS reserved words as identifiers?
2. Which reserved words are used as identifiers (complete list)?
3. What GAMS error codes result from unquoted reserved word identifiers?
4. Is the GAMS reserved word list documented anywhere, or must we derive it from the grammar?
5. Do reserved words need quoting in all contexts (set elements, parameters, variables) or only some?

### How to Verify
- Search all GAMSLIB model source files for identifiers matching GAMS reserved words
- Compile affected models with `gams action=c` to confirm the error
- Test quoting the identifier and recompiling to confirm the fix

### Risk if Wrong
- Incomplete reserved word list means some models still fail after the fix
- If reserved words need different quoting in different contexts, fix is more complex

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.2: Does quoting reserved words in `expr_to_gams.py` cover all emission contexts?

### Priority
**High** — Determines if fix is localized or requires changes across multiple emitters

### Assumption
Adding reserved word quoting to `src/emit/expr_to_gams.py` is sufficient because all identifier emission flows through this module.

### Research Questions
1. Do set declarations in `src/emit/original_symbols.py` also emit identifiers that could be reserved words?
2. Does `src/emit/model.py` emit identifiers in the Model MCP declaration?
3. Does `src/emit/templates.py` emit identifiers in equation/variable declarations?
4. Are there other emission points that could produce unquoted reserved words?

### How to Verify
- Trace all identifier emission paths across the emit module
- Check if `original_symbols.py`, `model.py`, and `templates.py` emit raw identifiers

### Risk if Wrong
- Fix only covers expressions, but reserved words in set/variable declarations still cause errors
- Need to add quoting to multiple modules (2-3h extra)

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.3: Will quoting reserved words break GAMS keyword recognition?

### Priority
**Medium** — Correctness risk

### Assumption
GAMS correctly distinguishes between quoted identifiers (e.g., `'set'`) and keywords (`Set`), so quoting a reserved word used as an identifier will not confuse the GAMS parser.

### Research Questions
1. Does GAMS use case-insensitive keyword matching?
2. If a set element is named `'model'`, does GAMS correctly parse it as a data element, not a keyword?
3. Are there GAMS contexts where quoting changes semantics (e.g., `'i'` vs `i` in set element references)?

### How to Verify
- Test with GAMS:
  ```gams
  Set s / 'set', 'model', 'variable' /;
  Parameter p(s) / 'set' 1, 'model' 2, 'variable' 3 /;
  Display p;
  ```
- Confirm compilation and correct output

### Risk if Wrong
- Quoting introduces new errors instead of fixing old ones
- Low risk — GAMS quoting is well-defined for identifiers

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 4: Lexer Error Deep Analysis

## Unknown 4.1: What is the current lexer_invalid_char count, and has it changed since v1.2.0?

### Priority
**High** — Sprint 19 target (reduce from ~95 to below 50) depends on accurate baseline

### Assumption
There are approximately 95 models with `lexer_invalid_char` errors, as reported in the Epic 4 GOALS.md baseline.

### Research Questions
1. What is the exact current count of `lexer_invalid_char` models?
2. Did any Sprint 18 fixes (grammar changes, emission fixes) affect the lexer_invalid_char count?
3. Are there models that were `lexer_invalid_char` in v1.1.0 but changed status in v1.2.0?
4. Is the GOALS.md count of 74 or ~95 the correct baseline? (GOALS.md says 74, PROJECT_PLAN.md says ~95)
5. What is the discrepancy between these numbers?

### How to Verify
- Run full pipeline on v1.2.0 codebase and count `lexer_invalid_char` failures
- Compare with GOALS.md and PROJECT_PLAN.md numbers
- Resolve any discrepancy

### Risk if Wrong
- Sprint 19 target calibrated to wrong baseline — either too easy or impossible
- Critical for Task 3 (lexer catalog) and Task 9 (baseline metrics)

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.2: Are there preprocessor directives (`$if`, `$include`, `$setglobal`) in lexer_invalid_char models that require preprocessor support rather than grammar fixes?

### Priority
**Critical** — Determines which models are addressable with grammar-only changes

### Assumption
Most lexer_invalid_char failures are caused by unsupported GAMS syntax that can be addressed with grammar extensions. Some failures may be caused by preprocessor directives that require a GAMS preprocessor implementation.

### Research Questions
1. How many lexer_invalid_char models use `$if`, `$include`, `$setglobal`, or other preprocessor directives?
2. For models with preprocessor directives, is the directive itself the parse failure or is it incidental?
3. Can we ignore preprocessor directives (treat as comments) for parse purposes?
4. Does implementing preprocessor support require a separate preprocessing pass before parsing?
5. What percentage of the ~95 models are addressable without preprocessor support?

### How to Verify
- Grep all lexer_invalid_char model sources for `$` directives
- For each, determine if the `$` directive is the parse failure point
- Classify models as "grammar-fixable" vs "preprocessor-required"

### Risk if Wrong
- If most models need preprocessor support, the "below 50" target requires preprocessor implementation (not in Sprint 19 scope, major scope expansion)
- Grammar-only fixes yield fewer than expected improvements

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.3: What is the overlap between the deferred "Lexer Error Deep Analysis" item and Prep Task 3?

### Priority
**Medium** — Scope clarity between prep and sprint work

### Assumption
Prep Task 3 (Catalog lexer_invalid_char Subcategories) will produce the subcategorization, and the deferred "Lexer Error Deep Analysis" sprint item (5-6h) will build on it with detailed fix plans and initial implementation.

### Research Questions
1. Does the Prep Task 3 output fully satisfy the deliverable for the deferred "Lexer Error Deep Analysis" (`LEXER_ERROR_ANALYSIS.md`)?
2. If so, should the 5-6h deferred item budget be reallocated to implementation?
3. What additional analysis does the sprint item need beyond the prep task catalog?

### How to Verify
- Compare Prep Task 3 deliverable spec with PROJECT_PLAN.md deferred item deliverable spec
- Identify any gaps between the two

### Risk if Wrong
- Duplicate work (same analysis done in prep and sprint, wasting 5-6h)
- Or incomplete analysis (prep task assumed to cover it, but sprint needs deeper dive)

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 5: Put Statement Format Support

## Unknown 5.1: Does the Sprint 18 put format grammar design from KNOWN_UNKNOWNS.md still apply?

### Priority
**High** — Determines if grammar work can reuse Sprint 18 research

### Assumption
The grammar design from Sprint 18 Unknown 3.3 (verified: `put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?`) is still valid and can be directly implemented in Sprint 19.

### Research Questions
1. Were any grammar changes made in Sprint 18 that affect the put statement rules?
2. Does the verified design from Sprint 18 handle all 4 target models (ps5_s_mn, ps10_s, ps10_s_mn, stdcge)?
3. Is the `put_stmt_nosemi` variant (needed for stdcge) included in the design?
4. What about the `loop(j, put j.tl)` pattern — does the design handle this?

### How to Verify
- Read current `src/gams/gams_grammar.lark` put statement rules
- Compare with Sprint 18 KNOWN_UNKNOWNS.md Unknown 3.3 design
- Check if the design handles all 4 target models

### Risk if Wrong
- Grammar design needs rework, adding 1-2h to Sprint 19
- Low risk — Sprint 18 design was well-researched

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.2: Do the 4 target put-statement models have issues beyond put format syntax?

### Priority
**High** — Determines actual unblock count from put format fix

### Assumption
Sprint 18 Unknown 3.2 verified that 3 of 4 models (ps5_s_mn, ps10_s, ps10_s_mn) are blocked only by `:width:decimals`, while stdcge needs a separate `put_stmt_nosemi` fix. This is assumed to still be accurate.

### Research Questions
1. Has the pipeline status of these 4 models changed since Sprint 18?
2. Could Sprint 18 grammar changes have affected these models?
3. After fixing put format, will these models parse fully or hit other errors?

### How to Verify
- Run current parser on all 4 models — confirm same errors as Sprint 18
- If errors have changed, re-analyze

### Risk if Wrong
- Models have new blockers discovered only during implementation (wasted 2.5h)
- Low risk — Sprint 18 analysis was thorough

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 6: Complex Set Data Syntax

## Unknown 6.1: What specific GAMS syntax constructs cause the lexer_invalid_char failures in the complex set data subcategory?

### Priority
**Critical** — Largest subcategory (14+ models), determines grammar change scope

### Assumption
The complex set data subcategory includes multi-dimensional set assignments, compound set operations, and data-statement syntax that the current grammar doesn't support. These require grammar rule additions or modifications.

### Research Questions
1. What are the 3-5 most common GAMS syntax patterns that cause failures?
2. Are these patterns documented in GAMS reference manual?
3. Can they be added to the grammar incrementally (one pattern at a time)?
4. Do any patterns require restructuring existing grammar rules (breaking changes)?
5. How many models does each pattern affect?

### How to Verify
- Extract the failing line/character from each of the 14+ models
- Group by syntax pattern
- For each pattern, write a minimal GAMS example and attempt to add a grammar rule

### Risk if Wrong
- Grammar changes are more extensive than estimated (8-10h → 14-18h)
- Some patterns conflict with existing rules, causing regressions
- Critical for Sprint 19 lexer_invalid_char target

### Estimated Research Time
3-4 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.2: Will grammar additions for complex set data cause ambiguities with existing rules?

### Priority
**High** — Regression risk for grammar changes

### Assumption
New grammar rules can be added without creating ambiguities with existing Lark grammar rules. Lark's Earley/LALR parser can handle the additional rules.

### Research Questions
1. Does Lark report ambiguity warnings for the current grammar?
2. Will adding data statement rules conflict with parameter or table parsing?
3. What parser strategy does the grammar use (Earley vs LALR)? Does this affect ambiguity handling?
4. Can we use Lark priority rules to resolve any ambiguities?

### How to Verify
- Run Lark grammar compilation with new rules — check for warnings
- Run full test suite after each grammar addition — verify no regressions
- Use `lark.ambiguity` option to detect ambiguous parses

### Risk if Wrong
- Grammar ambiguities cause existing tests to fail (regression)
- Ambiguity resolution changes parse results for currently-parsing models

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.3: Can compile-time constant expressions like `1*card(s)` be handled at the grammar level?

### Priority
**High** — Determines approach for compile-time constants subcategory (3-4h in sprint)

### Assumption
Expressions like `1*card(s)` in set/parameter ranges can be parsed as expressions in the grammar and evaluated during IR construction. No separate preprocessor pass is needed.

### Research Questions
1. What compile-time functions does GAMS support in ranges? (`card()`, `ord()`, others?)
2. Can these expressions appear in set definitions, parameter ranges, or both?
3. Does the current grammar support `card()` and `ord()` as expressions?
4. Would the IR need to evaluate these expressions, or can they be preserved symbolically?
5. Are there models where the range expression depends on runtime data?

### How to Verify
- List all compile-time functions used in lexer_invalid_char models
- Test if adding `card(s)` to expression rules in the grammar parses correctly
- Check if IR construction can handle the new expressions

### Risk if Wrong
- If evaluation is needed (not just parsing), fix requires an expression evaluator (~6h instead of 3-4h)
- If runtime data is needed, fix is impossible without a full GAMS interpreter

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.4: How many of the ~95 lexer_invalid_char models are addressable with grammar-only changes in Sprint 19?

### Priority
**Critical** — Validates the "below 50" target

### Assumption
At least 45 of the ~95 models can be fixed with grammar-only changes (no preprocessor required), making the "below 50" target achievable.

### Research Questions
1. After cataloging all subcategories (Task 3), how many models fall into grammar-fixable categories?
2. Are there "easy wins" (single-pattern fixes that unblock many models)?
3. What is the realistic count after accounting for models with multiple issues?
4. Should the target be adjusted based on the catalog results?

### How to Verify
- Combine Task 3 output (subcategory catalog) with Unknown 4.2 output (preprocessor analysis)
- Calculate: grammar-fixable count = total - preprocessor-required - multi-issue models

### Risk if Wrong
- Target "below 50" is not achievable, requiring scope adjustment mid-sprint
- Or target is too easy, and Sprint 19 could have been more ambitious

### Estimated Research Time
1 hour (depends on Task 3 results)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 7: internal_error & IndexOffset

## Unknown 7.1: What is the distribution of internal_error failure types?

### Priority
**Critical** — Determines which patterns to fix first (target: 23 → below 15)

### Assumption
The 23 internal_error models can be classified into 3-5 failure types: grammar ambiguity, missing production, IR construction crash, and transformer error. The most common type affects 8+ models and is the best fix target.

### Research Questions
1. What are the exact error messages for each of the 23 models?
2. Do models cluster by error type (same error pattern → same root cause)?
3. Which error type has the highest count (best ROI for fixing)?
4. Are there quick-fix patterns (e.g., adding a missing grammar rule) vs. deep fixes (IR redesign)?
5. How many models need to be fixed to hit "below 15" (at least 9)?

### How to Verify
- Run all 23 models with `--debug` or verbose parser output
- Capture error type, message, and stack trace
- Group by root cause pattern

### Risk if Wrong
- If errors are diverse (23 unique issues), fixing 9 requires 9 separate fixes (much more effort than 6-8h)
- If the most common pattern affects only 3-4 models, multiple patterns must be fixed

### Estimated Research Time
3-4 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 7.2: Can internal_error fixes be made without breaking currently-parsing models?

### Priority
**High** — Regression risk for parser changes

### Assumption
Grammar and IR changes to fix internal_error models will not break the 62 currently-parsing models. The fixes are additive (new rules) rather than modifying existing rules.

### Research Questions
1. Do any internal_error fixes require modifying existing grammar rules?
2. If so, do the modified rules affect currently-parsing models?
3. Can we use Lark's rule priority system to add new rules without changing existing behavior?
4. What is the regression test strategy — run all 62 parsing models after each change?

### How to Verify
- After each fix, run full test suite (3294 tests)
- Additionally parse all 62 currently-parsing models and verify same AST output

### Risk if Wrong
- Regression: fixing new models breaks existing ones — net zero or negative progress
- Sprint 18 had zero regressions across 3294 tests — maintain this standard

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 7.3: How should the IndexOffset IR node interact with automatic differentiation?

### Priority
**Critical** — Core design question for IndexOffset IR design

### Assumption
IndexOffset nodes (representing `x(t+1)`, `x(t-1)`) can be treated as independent variables during differentiation — `d/dx(t+1) [x(t+1)]` = 1, and `d/dx(t) [x(t+1)]` = 0. This follows the standard approach in dynamic optimization.

### Research Questions
1. Is the "independent variable" assumption correct for all GAMS lead/lag use cases?
2. In dynamic models, are `x(t)` and `x(t+1)` treated as different variables in the optimization?
3. Does the KKT system need separate stationarity equations for `x(t)` and `x(t+1)`?
4. How do existing tools (GAMS itself, AMPL) handle differentiation of lead/lag expressions?
5. Are there cases where `x(t+1)` appears in the objective and requires special gradient handling?

### How to Verify
- Review GAMS documentation on dynamic models and lead/lag semantics
- Study 1-2 of the 8 blocked IndexOffset models to understand the expected MCP structure
- Compare with GAMS-generated MCP output (if available) for a simple dynamic model

### Risk if Wrong
- If differentiation treatment is wrong, the entire IndexOffset implementation produces incorrect KKT systems
- Would require redesigning the AD module's handling of IndexOffset (~8h rework)

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 7.4: What grammar changes are needed to parse GAMS lead/lag syntax?

### Priority
**High** — Determines parser spike effort (2h allocated in sprint)

### Assumption
GAMS lead/lag syntax (`x(t+1)`, `x(t-1)`, `x(t++1)`, `x(t--1)`) can be parsed by extending the index expression rule in the grammar. The `+` and `-` operators within index positions need to be recognized as lead/lag rather than arithmetic.

### Research Questions
1. How does GAMS distinguish `x(t+1)` (lead) from `x(t + 1)` (arithmetic)?
2. Is lead/lag syntax only valid in certain contexts (loops, dynamic equations)?
3. Can the grammar handle multi-period offsets (`x(t+2)`, `x(t-3)`)?
4. How to handle circular variants (`x(t++1)`, `x(t--1)`) — same rule or separate?
5. Does the current index expression rule need modification or can we add an alternative?

### How to Verify
- Review GAMS documentation for lead/lag syntax rules
- Write test GAMS models with various lead/lag patterns
- Prototype grammar rule in `gams_grammar.lark` and test parsing

### Risk if Wrong
- Grammar change conflicts with arithmetic in index expressions (breaking regression)
- Lead/lag syntax more complex than assumed, requiring deeper grammar restructuring

### Estimated Research Time
1-2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 8: Cross-Indexed Sums & Architectural Issues

## Unknown 8.1: What is the exact code path that produces uncontrolled indices in stationarity equations (ISSUE_670)?

### Priority
**Critical** — Highest-ROI fix item (6 models blocked)

### Assumption
The uncontrolled index issue occurs during stationarity equation generation in `src/kkt/stationarity.py` when differentiating constraints that contain sums over indices not in the equation domain. The fix is localized to the stationarity builder.

### Research Questions
1. At what point in stationarity generation does the uncontrolled index appear?
2. Does the issue originate in differentiation (AD module) or in equation construction (KKT module)?
3. Is the cross-indexed sum pattern detected by `src/emit/expr_to_gams.py`'s existing index aliasing?
4. Does the fix need changes in one module or across multiple modules (parser, AD, KKT, emit)?
5. Can the fix be scoped to wrap uncontrolled indices in sums during emission, or must it be fixed at the KKT level?

### How to Verify
- Trace the stationarity equation generation for abel model (simplest of the 6)
- Identify exact line in `src/kkt/stationarity.py` where uncontrolled index is introduced
- Check if `expr_to_gams.py` index aliasing detects this pattern

### Risk if Wrong
- If the fix requires AD module changes, scope expands from 8-16h to 16-24h
- If fix is across multiple modules, integration risk increases significantly

### Estimated Research Time
3-4 hours

### Owner
Development team

### Verification Results
✅ Status: VERIFIED (Prep Task 4, 2026-02-13)

**Finding:** The assumption is correct — the issue originates in `src/kkt/stationarity.py` and the fix is localized to the stationarity builder. No AD module changes are needed.

**Exact code path:**

1. `build_stationarity_equations()` creates stationarity equations with `domain = var_def.domain`
2. `_add_indexed_jacobian_terms()` processes each constraint's Jacobian entry
3. `_replace_indices_in_expr()` converts concrete element labels to symbolic set names. For parameters with `prefer_declared_domain=True`, it can map a variable-domain index to the wrong set name (e.g., mapping `"p1"` to `"np"` from the parameter's declared domain instead of `"p"` from the variable domain)
4. The sum wrapping logic in the stationarity builder only compares `mult_domain_set` vs `var_domain_set`. It does **not** check whether the derivative expression itself contains additional free indices outside both domains

**Two sub-problems identified:**
- **Sub-problem A:** Index replacement in `_replace_matching_indices()` can produce wrong symbolic names when parameter declared domain differs from the stationarity context
- **Sub-problem B:** No detection of uncontrolled indices within the derivative expression itself

**Fix scope:** Localized to `stationarity.py` — add a `_collect_free_indices()` utility to detect uncontrolled indices and wrap them in sums. No changes needed to AD, parser, or emit modules.

**Impact on Sprint 19:** Effort estimate narrowed from 8-16h to 10-14h. Single-module fix with low regression risk.

---

## Unknown 8.2: Do all 6 ISSUE_670 models share the same cross-indexed sum pattern?

### Priority
**High** — Determines if one fix covers all models or multiple fixes needed

### Assumption
All 6 models (abel, qabel, chenery, mexss, orani, robert-secondary) have the same fundamental pattern: a sum over an index that is not in the equation domain, producing an uncontrolled index reference in the stationarity equation.

### Research Questions
1. Do all 6 models use `sum(index, ...)` where `index` is not in the equation domain?
2. Are there variations — e.g., nested sums, product of sums, conditional sums?
3. Does robert's cross-indexed sum differ from the other 5 (since it's a secondary issue)?
4. Are there models with related but different patterns that would benefit from the same fix?

### How to Verify
- Extract the specific constraint causing ISSUE_670 from each of the 6 models
- Compare the sum patterns — document similarities and differences
- Determine if one fix pattern covers all variations

### Risk if Wrong
- If patterns differ, need multiple fix strategies (8-16h becomes 16-24h)
- If robert's pattern is fundamentally different, it may not be fixable with the same approach

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
✅ Status: VERIFIED (Prep Task 4, 2026-02-13)

**Finding:** The assumption is correct — all 6 models share the same fundamental pattern. One fix (free index detection + sum wrapping) covers all variations.

**Common pattern:** A constraint `eq(d)` contains `sum(s, f(d,s)*x(s,v))`. When forming the stationarity condition for `x(v)`, the derivative contributes a term like `f(d,v)` multiplied by the multiplier over `d`. Indices in `var_domain ∪ mult_domain` (often including `d`) are therefore controlled; the cross-index bug arises when the derivative introduces an *additional* index not in `var_domain ∪ mult_domain` (typically the original summation index or a mismatched subset/superset index), which then remains free/uncontrolled in `stat_x(v)`.

**Per-model patterns:**

| Model | Constraint | Cross-Index Expression | Uncontrolled Index |
|-------|-----------|----------------------|-------------------|
| abel | criterion | `sum((k,n,np), ... w(n,np,k)*x(np,k))` | `np` |
| qabel | criterion | Same as abel | `np` |
| chenery | sup(i) | `sum(j, aio(j,i)*p(j))` | `j` (potential — current AD produces diagonal `aio(i,i)`) |
| mexss | mbf, mbi, mbr, cc | `sum(cf, ... - a(c,p) ...)` | `c` (superset of `cf`/`ci`/`cr`/`m`) |
| orani | indc, pric | `sum(sp, alpha(c,sp,i)*p(c,sp))` | `sp` |
| robert | sb, pd | `sum(p, a(r,p)*x(p,tt))` + `c(p,t)` subset mismatch | `t` (subset of `tt`) |

**Variations identified (all handled by one fix):**
- **Simple cross-index:** chenery (single sum, single cross-index)
- **Multi-index sum:** abel/qabel (sum over multiple indices with matrix)
- **Subset indexing:** mexss (parameter indexed by subset `cf` of set `c`)
- **Multi-level cross-indexing:** orani (nested cross-references)
- **Subset/superset mismatch:** robert (`t` is subset of `tt`)

**Impact on Sprint 19:** One fix approach covers all 6 models. No need for multiple fix strategies.

---

## Unknown 8.3: Can table continuation (ISSUE_392) and table description (ISSUE_399) be fixed with grammar changes alone?

### Priority
**High** — Determines implementation approach for table parsing fixes

### Assumption
ISSUE_392 (table continuation with `+`) and ISSUE_399 (table description treated as header) can be fixed with grammar rule changes and/or semantic handler updates in the parser, without IR changes.

### Research Questions
1. Does the grammar already have a rule for `+` continuation in tables?
2. If the grammar rule exists, is the issue in the semantic handler (`src/ir/parser.py`)?
3. For ISSUE_399, is the description-vs-header distinction parseable at the grammar level or requires semantic analysis?
4. Will these fixes affect other table-using models that currently parse correctly?

### How to Verify
- Read `src/gams/gams_grammar.lark` table rules
- Read `src/ir/parser.py` table semantic handler
- Test grammar changes on `like` (ISSUE_392) and `robert` (ISSUE_399) models
- Run regression on all currently-parsing models with tables

### Risk if Wrong
- If IR changes needed, scope expands for each issue (2-4h → 6-8h each)
- Grammar changes may affect existing table parsing (regression risk)

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 8.4: What bound configurations cause empty MCP equations in ISSUE_672?

### Priority
**Medium** — 2 models blocked (alkyl, bearing)

### Assumption
The empty MCP equation issue is caused by specific bound configurations (e.g., variables with equal `.lo` and `.up`, or `.fx` bounds) that the MCP pairing logic in `src/kkt/partition.py` doesn't handle correctly.

### Research Questions
1. What specific variable bounds do alkyl and bearing use?
2. Are there variables with `.fx` bounds that should be treated as fixed?
3. Does the MCP pairing logic check for fixed variables before creating pairs?
4. Is the issue in KKT assembly (empty stationarity equation) or MCP pairing (pairing an empty equation with a non-fixed variable)?
5. Are there other models with similar bound configurations that don't trigger this bug?

### How to Verify
- Run alkyl and bearing through the pipeline and examine the MCP pairing output
- List all variables and their bounds for each model
- Trace the MCP pairing logic for the failing variable/equation pairs

### Risk if Wrong
- If the issue is in KKT assembly, fix requires stationarity.py changes (4-6h → 8-10h)
- If bound configurations are highly model-specific, fix may not generalize

### Estimated Research Time
2-3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Template for Adding New Unknowns During Sprint

```markdown
## Unknown X.N: [Title]

### Priority
**[Critical/High/Medium/Low]** — [Brief justification]

### Assumption
[What we currently assume]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify
[Concrete test cases or experiments]

### Risk if Wrong
[Impact on sprint if assumption is wrong]

### Estimated Research Time
[Time estimate]

### Owner
[Team or individual]

### Verification Results
🔍 Status: INCOMPLETE
```

---

# Newly Discovered Unknowns

*Add unknowns discovered during Sprint 19 here, then categorize.*

---

# Confirmed Knowledge (Resolved Unknowns)

*Move resolved items here with findings.*

---

## Next Steps

1. **Prep Tasks 2-9:** Research and verify all Critical and High unknowns before Sprint 19 Day 1
2. **Sprint 19 Day 1:** Review all unknowns at standup; verify any remaining INCOMPLETE items
3. **During Sprint 19:** Update verification results as implementation progresses; add newly discovered unknowns
4. **Sprint 19 Checkpoints (Days 1, 6, 11):** Review unknown status at each checkpoint

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Classify internal_error Failure Modes | 7.1, 7.2 | Directly classifies all 23 internal_error models and assesses regression risk |
| Task 3: Catalog lexer_invalid_char Subcategories | 4.1, 4.2, 4.3, 6.1, 6.4 | Full subcategorization reveals pattern distribution, preprocessor needs, and addressable count |
| Task 4: Analyze Cross-Indexed Sum Patterns (ISSUE_670) | 8.1, 8.2 | Traces exact code path and compares patterns across all 6 affected models |
| Task 5: Audit Sprint 18 Deferred Item Readiness | 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.3, 5.1, 5.2 | Audits all 5 deferred items; verifies code pointers, affected models, and prerequisites for each |
| Task 6: Research IndexOffset IR Design Options | 7.3, 7.4 | Evaluates AD interaction and grammar change requirements for IndexOffset |
| Task 7: Analyze Table Parsing Issues (ISSUE_392, ISSUE_399) | 8.3 | Determines if grammar-only fixes are sufficient for table parsing |
| Task 8: Analyze MCP Pairing Issues (ISSUE_672) | 8.4 | Identifies bound configurations causing empty MCP equations |
| Task 9: Verify Sprint 19 Baseline Metrics | 4.1, 6.4 | Confirms exact lexer_invalid_char count and validates Sprint 19 targets |
| Task 10: Plan Sprint 19 Detailed Schedule | All | Integrates all verified unknowns into the 14-day schedule |
