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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — `uniform()` regenerates different random data in the MCP context. The generated MCP file (`data/gamslib/mcp/circle_mcp.gms`) retains `x(i) = uniform(1, 10)` and `y(i) = uniform(1, 10)` calls rather than hardcoded values. Each MCP execution produces different parameter values, making the KKT conditions inconsistent.

**Fix approach confirmed:** Capture computed parameter values and emit as constants. Alternative worth testing: `execseed` (GAMS random seed) to make random values deterministic. The fix is localized to `src/emit/original_symbols.py` parameter emission — no runtime GAMS execution integration needed if `execseed` works.

**Impact on Sprint 19:** Fix approach is well-scoped (1.5-2h). No change to sprint plan.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is partially correct — the house model's MCP infeasibility appears to involve constraint qualification issues, not just data. Analysis of `house_mcp.gms` listing shows contradictory complementarity conditions (e.g., `comp_maxw` requires `-x >= 0` while `comp_minw` requires `x >= 0`) and multiple uninitialized variables. The original NLP solves successfully (obj=4500 with CONOPT).

**Root cause narrowed to two possibilities:**
1. KKT complementarity pairing produces contradictory conditions for the inequality constraints
2. Variable initialization at zero creates an infeasible starting point that PATH cannot recover from

**Next step:** Extract the KKT point from the original NLP solution and verify against the MCP system. If the KKT point does satisfy the MCP, the issue is initialization; if not, the issue is in KKT formulation.

**Impact on Sprint 19:** House fix may require 2-4h (more than the 1.5h originally budgeted within the 3-4h total). Overall item effort revised to 3.5-6h.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — fixes for circle and house are isolated. Circle's fix (parameter value capture) only affects models with stochastic functions (`uniform`, `normal`). House's fix (KKT formulation or initialization) targets specific constraint/bound configurations. Neither fix modifies shared code paths used by the 20 currently-solving models.

**Regression mitigation:** Full regression test on all 20 solving models after each fix. The existing 3294-test suite provides additional safety.

**Impact on Sprint 19:** Low regression risk confirmed. No change to sprint plan.

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
❌ Status: WRONG (Prep Task 5, 2026-02-13)

**Finding:** The assumption that ~3 models fail due to missing subset declarations is **unconfirmed**. No specific failing models have been identified in any documentation. The Sprint 18 Day 1 Error 352 models (abel, qabel) were fixed by the P4 dynamic subset assignment fix, which is a different issue. Subset relationship preservation was already implemented in Sprint 17 Day 5 (`emit_original_sets()` in `src/emit/original_symbols.py:384-450`), with `SetDef.domain` properly emitting parent set syntax like `cg(genchar)`.

**Correction:** The ~3 models estimate may be stale. The actual count of models failing due to missing subset relationships could be 0 (already fixed) or unknown (needs runtime verification). Unit tests in `tests/unit/emit/test_original_symbols.py` confirm subset emission works correctly.

**Impact on Sprint 19:** Sprint 19 should start with a 1h verification pass to identify any actually-affected models before allocating the full 4-5h budget. If no models fail due to missing subsets, this item can be marked complete with minimal effort.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — the IR stores set definitions with their domain information. `SetDef.domain` in `src/ir/symbols.py:31-36` stores parent set names as a tuple (e.g., `domain=('genchar',)` for subset `cg` of `genchar`). The emitter uses this in `_format_set_declaration()` at `src/emit/original_symbols.py:188-237` to emit `cg(genchar) /a, b, c/`. The fix is emitter-only; no parser changes are needed for the basic subset declaration case.

**Impact on Sprint 19:** If any models do fail due to subset issues, the fix is localized to the emission layer. No parser changes needed.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — subset preservation and element literal quoting operate on different code paths and do not conflict. Subset domain names are quoted via `_quote_symbol()` at `src/emit/original_symbols.py:203-204`, which is independent of the `_quote_indices()` function in `expr_to_gams.py` that handles element literal quoting. Sprint 18's quoting fixes (P1, P2) did not modify subset-related code paths.

**Impact on Sprint 19:** No interaction risk. Both fixes can be implemented independently.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — a small set of GAMS reserved constants appear as identifiers. The primary affected models are the ps2_f family (ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s) which use `inf` and `eff` as set element indices, producing GAMS Errors 120, 145, 149, 340. No `GAMS_RESERVED_WORDS` constant exists in the codebase. The GAMS reserved constants needing quoting are: `inf`, `na`, `eps`, `undf`, `yes`, `no`. Reserved keywords (`set`, `model`, `solve`, etc.) and built-in function names (`abs`, `log`, etc.) from `gams_grammar.lark` also need checking.

**Impact on Sprint 19:** Fix is well-scoped. Create `GAMS_RESERVED_CONSTANTS` set in `expr_to_gams.py` and add check in `_quote_indices()`. Effort confirmed at 2-3h.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is mostly correct but incomplete. All identifier emission flows through `expr_to_gams()` for expressions, but set element emission in `src/emit/original_symbols.py` uses separate functions (`_sanitize_set_element()`, `_quote_symbol()`) that do not check reserved words. Other emission points checked:
- `src/emit/equations.py` — delegates to `expr_to_gams()` (covered)
- `src/emit/model.py` — emits equation-variable pairs without index quoting (not affected — uses equation/variable names, not element labels)
- `src/emit/templates.py` — emits variable/equation declarations without index quoting (not affected)

**Correction:** The fix needs two locations: (1) `_quote_indices()` in `expr_to_gams.py` for expression contexts, and (2) `_sanitize_set_element()` in `original_symbols.py` for set data contexts. Both are in the emit layer.

**Impact on Sprint 19:** Slightly broader scope (two files instead of one), but still within the 2-3h budget.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — GAMS correctly distinguishes quoted identifiers from keywords. GAMS uses context-sensitive keyword recognition: `Set` as a declaration keyword is recognized by position (start of statement), while `"set"` as a quoted string is always treated as a data element. The quoting mechanism is well-defined in GAMS: single quotes, double quotes, and unquoted identifiers are all handled distinctly. This was also confirmed by Sprint 18's element literal quoting fix (P1), which quotes multi-char lowercase names without breaking GAMS keyword recognition.

**Impact on Sprint 19:** No risk of keyword confusion from quoting. Low risk confirmed.

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
✅ Status: VERIFIED (Prep Task 3, 2026-02-12)

**Actual count:** 72 models (not ~95 as in PROJECT_PLAN.md, not 74 as in GOALS.md).

**Source of truth:** `data/gamslib/gamslib_status.json` contains v1.1.0 pipeline data with exactly 72 `lexer_invalid_char` models.

**Discrepancy explanation:**
- PROJECT_PLAN.md "~95" was based on older v1.0.0 data before Sprint 17 grammar fixes resolved ~25 lexer errors
- GOALS.md "74" was close but off by 2 — likely included 2 models that were reclassified during Sprint 17

**v1.2.0 re-parse:** All 72 models were re-run with the v1.2.0 parser. All 72 still fail — zero silent fixes (unlike internal_error where 21/24 were silently resolved). Sprint 18's emission-layer fixes did not affect lexer-stage parsing.

**Sprint 19 target recalibration:** "~95 → below 50" should be revised to "72 → below 30" (or equivalently "fix 43+ models") based on the corrected baseline.

**Reference:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md`

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
✅ Status: VERIFIED (Prep Task 3, 2026-02-12)

**Finding:** Of 72 models, **3 (4%)** require **directive-processing preprocessor support** as their root cause, and **1 additional model (1%)** requires only **compile-time variable expansion**. The remaining **68 models (94%)** are addressable with grammar-only changes.

**Directive-processing preprocessor models (3):**
- `clearlak`: Uses `$goto`, `$label`, `$if`, `$libinclude` — the `$` directives ARE the parse failure cause
- `cesam2`: Uses `$ifthen`/`$else`/`$endif` conditionals in data blocks
- `springchain`: Uses `$eval`, `$if`, `$set` for compile-time computation

**Variable-expansion-only preprocessor model (1):**
- `uimp`: Uses `%gams.scrdir%` compile-time variable expansion; this is preprocessor-adjacent and distinct from directive processing but still requires preprocessor involvement. In later verification (for example, Unknown 6.4), all **4** of these models are counted together as the "preprocessor-involved" set.

**Standard directives already handled:** `$offtext/$ontext/$title` are present in most models and already stripped by the existing preprocessor in `src/ir/preprocessor.py`. These are NOT parse blockers.

**Key conclusion:** The "below 50" target (recalibrated to "below 30") does NOT require new preprocessor implementation. Grammar-only changes can address 68 of 72 models; the remaining 4 require some level of preprocessor involvement (3 directive-processing, 1 variable-expansion-only).

**Reference:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Preprocessor Directive Analysis section)

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
✅ Status: VERIFIED (Prep Task 3, 2026-02-12)

**Finding:** The `LEXER_ERROR_CATALOG.md` produced by Prep Task 3 **fully subsumes** the deferred "Lexer Error Deep Analysis" item scope. The catalog includes:
- Complete subcategorization of all 72 models into 11 categories (A-K)
- Per-model failure character and root pattern identification
- Grammar-fixable vs preprocessor-required classification
- Cascading failure root cause analysis
- Recommended implementation order with effort estimates
- Preprocessor directive analysis

**Recommendation:** The 5-6h budget for the deferred "Lexer Error Deep Analysis" item should be **reallocated to implementation** (grammar fixes). No additional analysis is needed — the catalog provides everything required to begin implementation on Sprint 19 Day 1.

**Reference:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md`

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption is correct — the Sprint 18 grammar design still applies. The current put grammar rules in `src/gams/gams_grammar.lark:493-500` are unchanged from Sprint 18. The verified design from Sprint 18 Unknown 3.3 (`put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?`) is directly implementable. The `loop(j, put j.tl)` pattern (needed for stdcge) requires an additional `put_stmt_nosemi` variant, which was identified in Sprint 18 Unknown 3.2 verification. No Sprint 18 grammar changes affect put statement rules.

**Impact on Sprint 19:** Grammar work can reuse Sprint 18 research directly. No rework needed.

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
✅ Status: VERIFIED (Prep Task 5, 2026-02-13)

**Finding:** The assumption from Sprint 18 Unknown 3.2 is confirmed and still accurate. 3 of 4 models (ps5_s_mn, ps10_s, ps10_s_mn) are blocked **only** by `:width:decimals` format specifiers — no secondary issues found. stdcge is blocked by a **different** issue: `loop(j, put j.tl);` requires a `put_stmt_nosemi` grammar variant, not `:width:decimals`. stdcge does not use format specifiers at all.

**Per-model verification:**
- ps5_s_mn: Lines 151-152 use `pt(i,t):10:5` — blocked by `:width:decimals` only
- ps10_s: Line 63 uses `x.l(i):20:10` etc. — blocked by `:width:decimals` only
- ps10_s_mn: Line 147 uses `pt(i,t):10:5` — blocked by `:width:decimals` only
- stdcge: Lines 385, 397 use `put j.tl` in loop without semicolon — different issue

**Impact on Sprint 19:** `:width:decimals` fix unblocks 3 models. stdcge needs separate `put_stmt_nosemi` fix (+0.5h). Total effort confirmed at 2-2.5h for all 4 models.

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
✅ Status: VERIFIED (Prep Task 3, 2026-02-12)

**Finding:** 11 distinct subcategories identified across all 72 `lexer_invalid_char` models (not just the complex set data subset). The top syntax patterns causing failures:

1. **Compound set data (`.` separator):** 12 models — dot-separated compound keys like `coal.east.rail` in set/parameter data blocks
2. **Put statement format (`:` specifier):** 6 models — `:width:decimals` format specifiers
3. **Declaration/syntax gaps (mixed):** 7 models — `not` operator, `prod()` function contexts, model attributes, compile-time variables
4. **Special values and inline data:** 7 models — `na`/`inf` in data, table continuation `+`, preprocessor conditionals
5. **Lead/lag indexing (`+`/`-`):** 4 models — `x(t+1)` dynamic indexing syntax

**Assumption correction:** The "complex set data" subcategory contains 12 models (not 14+ as assumed in PROJECT_PLAN.md). The remaining models originally grouped under "complex set data" actually belong to other subcategories (cascading failures, special values, declaration gaps).

**Incremental grammar approach:** Yes, all grammar-fixable subcategories can be implemented incrementally. No restructuring of existing grammar rules is needed — all changes are additive (new rules or rule alternatives).

**Reference:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md`

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
✅ Status: VERIFIED (Prep Task 3, 2026-02-12)

**Finding:** With a corrected baseline of 72 (not ~95), the addressable model counts are:

| Category | Count | Notes |
|----------|-------|-------|
| Directly grammar-fixable | 43 | Subcategories A, C, D, E (partial), F (partial), G, H, I, J (partial) |
| Cascading (resolve when root cause fixed) | 15 | Subcategory B — no direct work needed |
| Preprocessor-required (directive) | 3 | clearlak, cesam2, springchain |
| Compile-time expansion only | 1 | uimp (%var% expansion; grouped with preprocessor in totals) |
| Needs investigation | 10 | Subcategory K (7 miscellaneous) + Subcategory E (3: ship, tforss, trnspwl) |

**Scenario estimates:**
- **Optimistic:** 58 fixed → 14 remaining (all grammar + cascading resolve)
- **Realistic:** 55 fixed → 17 remaining (~80% cascading resolve)
- **Conservative:** 43 fixed → 29 remaining (grammar only, no cascading)

**Target recalibration:** PROJECT_PLAN.md target "~95 → below 50" must be revised. Since baseline is 72:
- Original intent (fix ~45 models) maps to "72 → below 30"
- Even the conservative estimate (43 fixed) achieves this
- The target is achievable and likely exceeded

**Easy wins identified:** Set element descriptions (4 models, 1-2h), put format (6 models, 2-3h), special values subset (3 models, 2-3h) = ~13 models in ~6-8h

**Reference:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Grammar-Fixable Assessment section)

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
✅ Status: VERIFIED (Prep Task 2, 2026-02-12)

**Actual count:** 24 models (not 23 as assumed in PROJECT_PLAN.md).

**Distribution (3 categories, not 3-5):**
- **No objective function:** 12 models (50%) — camshape, catmix, chain, danwolfe, elec, feasopt1, lnts, partssupply, polygon, robot, rocket, srpchase
- **Circular dependency:** 9 models (37.5%) — chakra, dyncge, glider, irscge, lrgcge, moncge, quocge, splcge, twocge
- **Parser/semantic error:** 3 models (12.5%) — gastrans (index mismatch), harker (model attribute access), mathopt4 (attr_access expression)

**Key finding:** 21 of 24 models (87.5%) now parse successfully with v1.2.0 codebase. Sprint 18 fixes silently resolved these. The pipeline database (`gamslib_status.json`) is stale (v1.1.0 data). Only 3 models still fail at the parse stage.

**Assumption corrections:**
- Error types are NOT grammar ambiguity/missing production/IR crash/transformer error. They are: validation errors miscategorized as parse errors (21 models) and genuine semantic parse errors (3 models).
- The "below 15" target is already met — only 3 genuine parse failures remain after v1.2.0.
- The 21 now-parsing models will encounter translation-stage errors (no-objective, circular-dependency) when the pipeline is re-run.

**Reference:** `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md`

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
✅ Status: VERIFIED (Prep Task 2, 2026-02-12)

**Finding:** All 24 `internal_error` models can be reclassified into specific categories. The `categorize_parse_error()` function in `scripts/gamslib/error_taxonomy.py` needs 2 additional message patterns to reclassify the 21 validation-error models; the remaining 3 parse failures will still fall through to the `internal_error` catch-all until further patterns are added:
1. "no objective function" → `model_no_objective_def` (translation-stage category)
2. "circular dependency" → new `validation_circular_dep` category or existing `semantic_domain_error`

The 3 remaining parse failures are parser-stage and map logically to existing categories, but their current messages do not yet match any `categorize_parse_error()` patterns and therefore still land in `internal_error`:
- gastrans (index mismatch, "expects ... got ...") → `semantic_domain_error`
- harker (undeclared model symbol, "not declared ...") → `semantic_undefined_symbol`
- mathopt4 (unsupported attr_access, "Unsupported expression type ...") → `parser_invalid_expression`

**Regression risk assessment:** LOW. Of the 3 remaining fixes needed:
- gastrans fix (implicit index mapping in `_handle_assign`) modifies assignment handling logic — requires careful regression testing
- harker + mathopt4 fix (model attribute access) is additive — new expression type support, no modification to existing rules
- 21 of 24 models already parse with v1.2.0 with zero regressions (Sprint 18 maintained 3294-test pass rate)

**Reference:** `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md`

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
✅ Status: VERIFIED (Prep Task 6, 2026-02-13)

**Finding:** The core assumption about differentiation is correct: `x(t+1)` and `x(t)` are treated as independent variables during differentiation. The AD system's `_diff_varref()` function (`src/ad/derivative_rules.py:201-275`) uses exact tuple equality: `expr.indices == wrt_indices`. Since `IndexOffset` is a frozen dataclass, `IndexOffset("t", Const(1), False) != "t"`, so `d/dx(t) [x(t+1)] = 0` automatically. Similarly, `IndexOffset("t", Const(1), False) == IndexOffset("t", Const(1), False)`, so `d/dx(t+1) [x(t+1)] = 1`. However, AD's sum-collapse/index-substitution logic (`_apply_index_substitution` in `src/ad/derivative_rules.py:1788`) still has an explicit limitation ("IndexOffset not supported in AD yet"), so full IndexOffset support in AD is **not** complete and additional work remains in that area.

**Impact on Sprint 19:** No additional work is needed to change `_diff_varref()` itself; the verified tuple-equality behavior can be reused as-is. The remaining AD effort for IndexOffset is confined to the index-substitution / sum-collapse path (extending `_apply_index_substitution` to handle `IndexOffset` correctly, ~4h). The ~14-16h PROJECT_PLAN.md estimate can be reduced to ~8h.

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
✅ Status: VERIFIED (Prep Task 6, 2026-02-13)

**Finding:** The assumption is partially correct but the grammar changes are **already done**. The `lag_lead_suffix` rule in `src/gams/gams_grammar.lark:330-344` already supports all four forms: `CIRCULAR_LEAD` (`++`), `CIRCULAR_LAG` (`--`), `PLUS` (linear lead), `MINUS` (linear lag), each followed by `offset_expr` (NUMBER or ID). The `++` and `--` tokens are unambiguous. For `+` and `-`, the grammar resolves ambiguity by context: within `index_expr`, `+`/`-` followed by `offset_expr` is lead/lag, not arithmetic. In addition, the parser semantic code (`src/ir/parser.py:786-933`) already processes `lag_lead_suffix` into `IndexOffset` IR nodes.

**Correction:** No grammar file changes are needed, and no additional work is required in the parser semantic handler — `_process_index_expr()` already constructs `IndexOffset` nodes. The remaining work is to identify and fix the **downstream** handling of `IndexOffset` that still produces `unsup_index_offset` failures (specifically `_apply_index_substitution` in the AD module and end-to-end pipeline tracing).

**Impact on Sprint 19:** The 2h "parser spike" allocation should be spent on end-to-end IndexOffset pipeline tracing and downstream fixes (AD index substitution), not on grammar or parser work.

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
✅ Status: VERIFIED

**Finding:** The assumption is **partially correct**. Both ISSUE_392 and ISSUE_399 can be fixed without IR changes, but they require semantic handler updates, not grammar-only changes.

**Shared Root Cause:** The grammar rule `table_block: "Table"i ID "(" table_domain_list ")" (STRING | DESCRIPTION)? table_content+ SEMI` has an ambiguity — when the optional description is provided as a quoted `STRING`, it is effectively never matched as the description by Lark's Earley parser because `dotted_label: (ID | STRING)` in the `table_row` path also accepts `STRING` tokens. The parser matches the quoted description as the first row's label via `dotted_label`, collapsing the entire table into a single malformed `table_row`. `DESCRIPTION` tokens, which do not overlap with `dotted_label`, still match the optional description position unambiguously.

**Evidence:**
- `robert` model: `'expected profits'` becomes `simple_label` of a single `table_row` with 16 children (all data as `table_value` nodes)
- `like` model: `'systolic blood pressure data'` becomes `simple_label` of a single `table_row` with 48 children; `+` continuation correctly parsed as `table_continuation` but built on malformed base

**Recommended Fix:** Semantic disambiguation in `_handle_table_block()` — detect when first `table_row`'s label is a STRING token, extract it as description, and reparse remaining tokens as proper column headers and data rows. Zero grammar changes needed, zero regression risk.

**Effort Estimate:** 3-5h combined (down from 4-8h original estimate in FIX_ROADMAP.md)

**Reference:** See `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md` for full analysis with parse tree evidence.

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
❌ Status: WRONG (Prep Task 8, 2026-02-13)

**Finding:** The assumption is **wrong**. The issue has nothing to do with bound configurations or MCP pairing logic in `src/kkt/partition.py`. The root cause is a **case sensitivity mismatch** in the AD differentiation pipeline:

- `CaseInsensitiveDict.keys()` returns lowercase variable names (e.g., `acidfeed`)
- Equation AST `VarRef` nodes store original-case names from the GAMS source (e.g., `VarRef("AcidFeed")`)
- `differentiate_expr()` in `src/ad/derivative_rules.py:226` uses case-sensitive comparison: `expr.name != wrt_var` → `"AcidFeed" != "acidfeed"` → `True` → returns `Const(0.0)`
- Result: ALL derivatives are zero for mixed-case variable names, producing stationarity equations where every constraint multiplier coefficient is `0`

**Evidence:**
- alkyl (all mixed-case variable names): ALL 14 stationarity equations have `0 * nu_*` for every constraint — complete Jacobian failure (7 errors)
- bearing (mixture of cases): equations using lowercase variable names in their bodies produce correct non-zero derivatives (`stat_h`, `stat_mu`, `stat_r` for `nu_friction`), while equations using mixed-case names produce zeros (`stat_ep` for `nu_pumping_energy`, `comp_radius` for `lam_radius`) — partial failure (2 errors)
- All-lowercase models (process, himmel16, blend) produce correct stationarity equations — confirming the differentiation engine itself is correct

**Correction:** The MCP pairing logic is correct. The "unmatched equation" error is a downstream symptom of zero derivatives, not a pairing defect. Fix is to normalize `VarRef` names to lowercase at parse time in `src/ir/parser.py`.

**Impact on Sprint 19:** Effort reduced from 4-6h (FIX_ROADMAP estimate for bound edge case analysis) to 2-4h (localized parser normalization fix). May unblock additional models beyond alkyl/bearing if they use mixed-case variable names.

**Reference:** See `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md` for full analysis with code path trace and per-model evidence.

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
