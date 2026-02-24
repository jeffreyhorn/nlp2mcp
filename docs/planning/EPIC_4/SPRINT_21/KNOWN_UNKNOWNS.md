# Sprint 21 Known Unknowns

**Created:** 2026-02-23
**Status:** Active - Pre-Sprint 21
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 21 macro expansion, error triage, solve quality improvement, PATH convergence investigation, and solution comparison enhancement

---

## Overview

This document identifies all assumptions and unknowns for Sprint 21 features **before** implementation begins. This proactive approach continues the highly successful methodology from Sprints 4–20 that prevented late-stage surprises.

**Sprint 21 Scope:**
1. `%macro%` Expansion in Preprocessor (~4–8h)
2. internal_error Triage — 7 Models (~6–10h)
3. Solve Quality — path_syntax_error — 45 Models (~8–12h)
4. Deferred Sprint 20 Issues — 13 Issues (~8–12h)
5. Full Pipeline Match Rate Improvement (~4–6h)
6. Semantic Error Resolution (~2h)
7. Emerging Translation Blockers (~4–6h)
8. PATH Convergence Investigation (~8–10h)
9. Solution Comparison Enhancement (~4–5h)

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 389–505 for complete Sprint 21 deliverables and acceptance criteria.

**Lessons from Previous Sprints:**
- Sprint 20: Lexer error subcategory catalog (Day 4) enabled prioritized grammar fixes → parse rate 112→132/160
- Sprint 19: Smoke-test-before-declaring-issues-not-fixable lesson (Issue #671)
- Sprint 7: Known Unknowns process achieved 25 unknowns, zero blocking issues
- Sprint 4–6: 22–23 unknowns per sprint, all resolved on schedule

**Sprint 20 Key Learning:** Catalog-first approach (systematically classifying error populations before fixing) was the highest-leverage technique. Sprint 21 should apply the same methodology to path_syntax_error (45 models) and internal_error (7 models).

---

## How to Use This Document

### Before Sprint 21 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 21
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4–8 hours)
- **Medium:** Wrong assumption will cause minor issues (2–4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 27
**By Priority:**
- Critical: 7 (unknowns that could derail sprint or prevent acceptance criteria)
- High: 11 (unknowns requiring upfront research)
- Medium: 6 (unknowns that can be resolved during implementation)
- Low: 3 (nice-to-know, low impact)

**By Category:**
- Category 1 (`%macro%` Expansion): 4 unknowns
- Category 2 (internal_error Triage): 3 unknowns
- Category 3 (path_syntax_error): 4 unknowns
- Category 4 (Deferred Sprint 20 Issues): 3 unknowns
- Category 5 (Match Rate Improvement): 3 unknowns
- Category 6 (Semantic Error Resolution): 2 unknowns
- Category 7 (Emerging Translation Blockers): 2 unknowns
- Category 8 (PATH Convergence): 3 unknowns
- Category 9 (Solution Comparison): 3 unknowns

**Estimated Research Time:** 30–38 hours (spread across prep tasks and early sprint days)

---

## Table of Contents

1. [Category 1: `%macro%` Expansion in Preprocessor](#category-1-macro-expansion-in-preprocessor)
2. [Category 2: internal_error Triage](#category-2-internal_error-triage)
3. [Category 3: Solve Quality — path_syntax_error](#category-3-solve-quality--path_syntax_error)
4. [Category 4: Deferred Sprint 20 Issues](#category-4-deferred-sprint-20-issues)
5. [Category 5: Full Pipeline Match Rate Improvement](#category-5-full-pipeline-match-rate-improvement)
6. [Category 6: Semantic Error Resolution](#category-6-semantic-error-resolution)
7. [Category 7: Emerging Translation Blockers](#category-7-emerging-translation-blockers)
8. [Category 8: PATH Convergence Investigation](#category-8-path-convergence-investigation)
9. [Category 9: Solution Comparison Enhancement](#category-9-solution-comparison-enhancement)

---

# Category 1: `%macro%` Expansion in Preprocessor

## Unknown 1.1: Is simple string substitution sufficient for `$eval` expressions in GAMSlib?

### Priority
**Critical** — Determines scope of the `$eval` evaluator; underestimating complexity blocks springchain and potentially other models

### Assumption
`$eval` expressions in the GAMSlib corpus use only simple integer arithmetic (addition, subtraction, multiplication) that can be handled by Python's `eval()` on sanitized integer expressions, without needing a full expression parser.

### Research Questions
1. What `$eval` expressions appear in springchain.gms? Are they purely integer arithmetic (e.g., `%N%-2`)?
2. Do any other GAMSlib models use `$eval`? If so, what expression types?
3. Does GAMS `$eval` support string operations, function calls, or floating-point math?
4. Can we safely use Python `int(eval(...))` on macro-expanded expressions, or do we need a dedicated evaluator?

### How to Verify
**Test Case 1:** Parse springchain.gms `$eval` lines and extract all `$eval` expressions
**Test Case 2:** Survey GAMSlib corpus for `$eval` usage: `grep -rl '$eval' data/gamslib/raw/*.gms`
**Test Case 3:** Attempt `int(eval(expr))` on each extracted expression after macro substitution

### Risk if Wrong
- **Integer-only assumption wrong:** Need to build a full expression evaluator (4–6h additional work)
- **Security risk:** Using Python `eval()` on untrusted input is dangerous; need sanitization
- **Sprint blocker:** springchain is a Priority 1 target model

### Estimated Research Time
2–3 hours

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: How many GAMSlib models use compile-time macros beyond saras and springchain?

### Priority
**High** — Determines whether macro expansion has broader impact than the 2 known blocked models

### Assumption
Only saras and springchain are blocked by macro expansion. Other models in the 160-model corpus either don't use macros or use macros that are already handled by the preprocessor's directive stripping.

### Research Questions
1. How many of the 160 models contain `$set`, `$setglobal`, or `$eval` directives?
2. How many of the 160 models contain `%name%` macro references?
3. Are any of the 10 lexer_invalid_char models blocked specifically by unexpanded macros?
4. Are any models currently parsing "incorrectly" because macros were stripped instead of expanded?

### How to Verify
**Test Case 1:** `grep -rl '\$set\b\|\$setglobal\b\|\$eval\b' data/gamslib/raw/*.gms | wc -l`
**Test Case 2:** `grep -rl '%[A-Za-z]' data/gamslib/raw/*.gms | wc -l`
**Test Case 3:** Cross-reference macro-using models with parse failure list

### Risk if Wrong
- **Broader impact than expected:** May need to reprioritize macro expansion to earlier in sprint
- **Incorrect parse results:** Models may be parsing with wrong data due to unexpanded macros

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: What system macros (`%system.X%`) does GAMS support, and which are needed?

### Priority
**High** — saras uses `%system.nlp%`; need to know what value to return and what other system macros exist

### Assumption
`%system.nlp%` returns the solver name for NLP problems (e.g., "CONOPT" or "MINOS"), and we can return a reasonable default. No other system macros are used in the GAMSlib corpus.

### Research Questions
1. What does `%system.nlp%` return in a standard GAMS environment?
2. What other `%system.X%` macros exist (e.g., `%system.lp%`, `%system.mip%`)?
3. How does saras use `%system.nlp%` — is it in a conditional, a display statement, or model logic?
4. What default value should we return if no solver is configured?

### How to Verify
**Test Case 1:** Read saras.gms and trace `%system.nlp%` usage
**Test Case 2:** Search GAMS documentation for system environment variables
**Test Case 3:** `grep -r '%system' data/gamslib/raw/*.gms` to find all system macro usage

### Risk if Wrong
- **Wrong default value:** saras may produce incorrect output or fail to parse
- **Missing system macros:** Other models may silently produce wrong results

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.4: Should macro expansion happen before or after other preprocessing steps?

### Priority
**Medium** — Ordering affects correctness; wrong order may cause cascading failures

### Assumption
Macro expansion should happen as the first preprocessing step, before directive stripping, comment removal, and normalization — matching GAMS's own compile-time processing order.

### Research Questions
1. Does GAMS process `$set`/`$eval` before or after `$ontext`/`$offtext` blocks?
2. Can macros be defined inside `$ontext`/`$offtext` blocks (should they be ignored)?
3. Does macro expansion interact with `$eolcom` or `$title` directives?
4. What is the correct ordering: macro expansion → directive stripping → normalization?

### How to Verify
**Test Case 1:** Create a GAMS file with macro definition inside `$ontext` block — verify it's not expanded
**Test Case 2:** Review GAMS documentation for compile-time processing order
**Test Case 3:** Test macro expansion before vs. after `$ontext` stripping on springchain

### Risk if Wrong
- **Incorrect preprocessing order:** Macros expanded inside comments or stripped blocks
- **Cascading errors:** Later preprocessing steps see unexpanded or incorrectly expanded text

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: internal_error Triage

## Unknown 2.1: Do the 7 internal_error models fail for the same IR builder reason or distinct reasons?

### Priority
**Critical** — Determines whether batch fixes are possible (one fix for multiple models) or each needs individual work

### Assumption
The 7 models (clearlak, imsl, indus, sarf, senstran, tfordy, turkpow) fail for 2–3 distinct root causes, enabling batch fixes that address multiple models per fix.

### Research Questions
1. What exception type and message does each model produce?
2. Which IR builder function (`src/ir/parser.py`) crashes for each model?
3. Are any models failing in the same function with the same error pattern?
4. Are the failures during set/parameter declaration, equation building, or variable processing?
5. Do any failures involve table data parsing (known to be fragile)?

### How to Verify
**Test Case:** Run each model through `parse_file()` with traceback capture:
```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
for m in ['clearlak','imsl','indus','sarf','senstran','tfordy','turkpow']:
    try: parse_file(f'data/gamslib/raw/{m}.gms')
    except Exception as e:
        import traceback; traceback.print_exc()
```

### Risk if Wrong
- **All distinct causes:** 7 separate fixes needed (1–2h each = 7–14h, exceeding 6–10h budget)
- **Common cause assumption wrong:** Time wasted looking for patterns that don't exist

### Estimated Research Time
2–3 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The 7 models fail for **5 distinct root causes**, not 2–3 as assumed. The distribution is:
- **Lead/lag indexing in parameter assignments:** 3 models (imsl, sarf, tfordy) — `_extract_indices()` rejects `lag_lead_suffix` in parameter context
- **Undefined symbol from missing `$libInclude`:** 1 model (clearlak) — `ScenRedParms` declared in external `scenred.gms`
- **Variable index arity mismatch:** 1 model (indus) — `ppc` declared as scalar but used with 2 indices
- **Malformed `if` statement parsing:** 1 model (senstran) — bare identifier `pors` not recognized as condition
- **Table row index mismatch:** 1 model (turkpow) — dotted index notation `hydro-4.1978` not split

Batch-fix potential exists for the lead/lag subcategory (3 models, one fix), but the other 4 models each need individual fixes. Total estimated effort: 7–11h (slightly above the 6–10h budget).

See `INTERNAL_ERROR_CATALOG.md` for full per-model analysis.

---

## Unknown 2.2: Are any internal_error models blocked by lead/lag syntax (`x(t-1)`, `x(t+1)`)?

### Priority
**High** — Lead/lag is a known gap in the IR builder; if multiple models use it, this becomes a Sprint 21 workstream

### Assumption
Lead/lag syntax is not the primary blocker for the 7 internal_error models; most failures are caused by table data parsing or symbol resolution issues.

### Research Questions
1. Do any of the 7 models use lead/lag syntax (e.g., `x(t-1)`, `x(t+1)`, `x(t++1)`)?
2. If so, how many equations use lead/lag in each model?
3. Does the Lark grammar already parse lead/lag syntax, or does it fail at parse stage?
4. Is lead/lag a translation-stage issue (IR builder) rather than parse-stage?

### How to Verify
**Test Case:** `grep -n 't-1\|t+1\|t++\|t--' data/gamslib/raw/{clearlak,imsl,indus,sarf,senstran,tfordy,turkpow}.gms`

### Risk if Wrong
- **Lead/lag is primary blocker:** Need to implement lead/lag in IR builder (4–6h additional)
- **Underestimated scope:** Sprint 21 Priority 2 budget may be insufficient

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** Lead/lag **IS** the primary blocker — 3/7 models (imsl, sarf, tfordy) fail specifically because `_extract_indices()` at line 610-614 of `src/ir/parser.py` rejects any `lag_lead_suffix` in parameter assignment context. This contradicts the assumption that lead/lag is NOT the primary blocker.

Specific lead/lag patterns found:
- **imsl:** `m+floor((ord(n)-1)/k)` and `m+1` (linear lead, 2 instances)
- **sarf:** `t++(cs(c,"start",s)-1)` (circular lead, 1 instance)
- **tfordy:** `te+3`, `t-1`, `t-2` (linear lead/lag, 3 instances) plus 4 more in equation domains

The grammar already parses all these patterns correctly via `lag_lead_suffix` (linear_lead, linear_lag, circular_lead, circular_lag). The issue is exclusively in the IR builder, not the parser.

Additionally, 1 model (tfordy) has lead/lag patterns in non-blocking contexts: tfordy has lead/lag in equation domains (lines 189-195) which may be a secondary issue after the parameter assignment fix.

---

## Unknown 2.3: Can internal_error models be fixed incrementally, or do they require architectural changes?

### Priority
**Medium** — Affects Sprint 21 scheduling: incremental fixes can be spread across days; architectural changes need dedicated blocks

### Assumption
Each internal_error model can be fixed with a targeted, incremental change to `src/ir/parser.py` (adding a new handler, fixing an edge case) without requiring architectural refactoring of the IR builder.

### Research Questions
1. For each model's error, is the fix a new case handler or a fundamental design limitation?
2. Do any fixes require changes to the ModelIR data structure?
3. Do any fixes require changes to the Lark grammar (upstream of IR builder)?
4. Can fixes be landed independently without cross-model regressions?

### How to Verify
**Test Case:** After diagnosing root causes (Unknown 2.1), assess whether each fix is:
- A: Add handler/case (1–2h, incremental)
- B: Grammar change + handler (2–4h, incremental)
- C: Architecture change (4–8h, needs design)

### Risk if Wrong
- **Architecture change needed:** One model's fix may block or break others
- **Schedule disruption:** Architectural changes can't be time-boxed easily

### Estimated Research Time
1 hour (after Unknown 2.1 is resolved)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:** All 7 internal_error models can be fixed with targeted, incremental changes. No architectural refactoring is required.

Fix assessment per model:
- **imsl, sarf, tfordy (lead/lag):** **Type A** — add handler/case in `_extract_indices()` to extract base index and offset expression. No grammar changes needed (grammar already parses correctly). No ModelIR changes needed (offset info can be stored in existing structures). Fixes can be landed independently. **Effort: 2–3h** (shared across all 3).
- **senstran (if statement):** **Type B** — grammar adjustment or handler update in `_handle_if_stmt` to accept bare identifier as condition. Minor, no architecture change. **Effort: 2–3h**.
- **turkpow (table dotted index):** **Type A** — update `_parse_param_data_items` to split dotted indices based on domain cardinality. **Effort: 1–2h**.
- **indus (index arity):** **Type A** — make `_make_symbol` more lenient for index arity mismatches. **Effort: 1–2h**.
- **clearlak (missing include):** **Type A** — reclassify as `missing_include` or add lenient auto-declare. **Effort: 1h**.

No fix requires changes to the ModelIR data structure. No fix requires changes to the Lark grammar (except possibly senstran). All fixes can be landed independently without cross-model regressions.

---

# Category 3: Solve Quality — path_syntax_error

## Unknown 3.1: Are the 45 path_syntax_error models caused by a few root causes or many distinct issues?

### Priority
**Critical** — Determines whether Sprint 21 Priority 3 can achieve high leverage (one fix for many models) or requires scattered fixes

### Assumption
The 45 path_syntax_error models cluster into 4–6 root cause subcategories, with the top 2–3 subcategories accounting for 30+ of the 45 models.

### Research Questions
1. What PATH error messages appear in the solver output for each model?
2. Do most failures occur at the same point in the MCP file (e.g., Model statement, complementarity pairing)?
3. Are equation name formatting issues (e.g., illegal characters) a common root cause?
4. Are domain mismatches (equation indexed over different set than paired variable) common?
5. How many models fail before PATH even starts (MCP syntax error) vs. during solving?

### How to Verify
**Test Case 1:** Run 15–20 representative path_syntax_error models through the full pipeline with verbose output
**Test Case 2:** Collect PATH error messages and cluster by pattern
**Test Case 3:** Inspect generated MCP files for the most common structural issues

### Risk if Wrong
- **Many distinct causes:** 8–12h budget insufficient for 45 scattered fixes
- **Few causes but complex fixes:** One root cause may require emitter redesign (>12h)
- **Misclassified errors:** Some "path_syntax_error" may actually be translation errors

### Estimated Research Time
3–4 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The 45 models cluster into **9 distinct root cause subcategories**, not 4–6 as assumed. However, the top 3 subcategories DO account for 32/45 models (71%), exceeding the assumed 30+. The subcategories are:

1. **A: Missing parameter/Table data** — 16 models (36%) — IR builder does not capture Table data blocks
2. **C: Uncontrolled set in stationarity equations** — 9 models (20%) — translator emits free set indices
3. **E: Set index quoted as string literal** — 7 models (16%) — emitter quotes set references as strings
4. **B: Domain violation in emitted data** — 5 models (11%) — emitter outputs out-of-domain elements
5. **D: Negative exponent needs parentheses** — 3 models (7%) — emitter outputs `** -N` without parens
6. **G: Set index reuse in sum** — 2 models (4%) — translator reuses controlling index
7. **F: GAMS built-in function collision** — 1 model — `gamma`/`psi` are reserved
8. **I: MCP variable unreferenced** — 1 model — variable in model statement but not in equations
9. **J: Equation-variable dimension mismatch** — 1 model — pairing dimensions don't match

The assumption of 4–6 subcategories was partially wrong (9 subcategories), but the core insight that a few fixes address most models was correct. Total estimated effort: 15–22h (above the 8–12h budget; triage needed).

See `PATH_SYNTAX_ERROR_CATALOG.md` for full per-model analysis.

---

## Unknown 3.2: Is the MCP Model statement generated correctly for all equation-variable pairings?

### Priority
**Critical** — The GAMS MCP Model statement pairs equations with variables for complementarity; wrong pairings cause PATH syntax errors

### Assumption
The emitter (`src/emit/emit_gams.py`) correctly generates the `Model` statement with proper equation-variable pairings for all 120 translatable models.

### Research Questions
1. Does the Model statement list all equations and their paired variables?
2. Are "free" variables (no bounds) handled correctly in the Model statement?
3. Are indexed equations paired with correctly-indexed variables?
4. Does the Model statement handle objective variable / objective equation pairing?
5. Are bound multiplier equations paired with their bound slack variables?

### How to Verify
**Test Case 1:** For a known-working model (e.g., trnsport), inspect Model statement structure
**Test Case 2:** For a known-failing model, compare Model statement against expected pairing
**Test Case 3:** Count equation/variable pairs in Model statement vs. expected count

### Risk if Wrong
- **Systematic pairing errors:** Could affect all 45 path_syntax_error models at once
- **Subtle indexing issues:** Model may compile but produce wrong complementarity conditions

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The MCP Model statement is NOT generated correctly for all pairings. Two specific issues were found:

1. **Subcategory I (nemhaus):** The Model statement includes variable `xb` and `y` paired with equations, but these variables do not appear in any model equation. GAMS error $483: "Mapped variables have to appear in the model." This is a translator bug where the MCP model statement includes variables that were eliminated or not referenced during KKT generation.

2. **Subcategory J (pdi):** The Model statement pairs an equation with a variable of different dimensionality. GAMS error $70: "The dimensions of the equ.var pair do not conform." This is a translator bug in equation-variable pairing logic.

Additionally, the assumption that the emitter "correctly generates pairings for all 120 translatable models" is misleading — of the 96 models that translate, 45 fail at GAMS compilation (path_syntax_error), so the emitter does NOT produce correct output for all translatable models.

However, the Model statement pairing issue is a minor contributor (2/45 models, 4%). The dominant issues are missing data (16 models) and stationarity equation generation (9 models).

---

## Unknown 3.3: Are there GAMS identifier naming rules that the emitter violates?

### Priority
**High** — GAMS has strict identifier naming rules; violations cause compile-time errors that manifest as path_syntax_error

### Assumption
The emitter generates GAMS-legal identifiers for all equations, variables, and parameters in the MCP output. No identifier exceeds GAMS's 63-character limit or uses reserved keywords.

### Research Questions
1. What is GAMS's maximum identifier length (63 characters)?
2. Does the emitter generate identifiers that exceed this limit (e.g., `stat_very_long_variable_name_with_many_indices_i_j_k`)?
3. Does the emitter use any GAMS reserved keywords as identifiers?
4. Are stationarity equation names (e.g., `stat_x`) always legal GAMS identifiers?
5. Do any generated identifiers contain illegal characters (spaces, hyphens, etc.)?

### How to Verify
**Test Case 1:** For 10 path_syntax_error models, check all generated identifiers against GAMS naming rules
**Test Case 2:** Check maximum identifier length in generated MCP files
**Test Case 3:** `grep -oP '\b\w{60,}\b' data/gamslib/mcp/*_mcp.gms | head -20`

### Risk if Wrong
- **Identifier length violations:** Simple truncation fix (1–2h) but may affect many models
- **Reserved keyword collisions:** Need renaming strategy

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED (with nuance)

**Findings:** The emitter does violate GAMS identifier naming rules, but in a specific and limited way:

1. **GAMS built-in function collision (Subcategory F, 1 model):** mingamma uses `gamma` and `psi` as variable names, which are GAMS built-in functions. The emitter outputs `gamma(x1)` and `psi(x1)` which GAMS interprets as function calls, not variable references. GAMS errors $121 (set expected) and $140 (unknown symbol).

2. **Set index quoting (Subcategory E, 7 models):** Not strictly an identifier length/naming issue, but the emitter quotes set names as string literals (`"J"` instead of `J`), which GAMS doesn't resolve.

3. **Identifier length:** No violations found. Generated identifiers (e.g., `stat_aweight`, `comp_lo_b3`, `nu_balance`) are all well under the 63-character GAMS limit.

4. **Reserved keywords:** Only the `gamma`/`psi` collision was found. No other GAMS reserved keywords are used as identifiers.

The assumption that "all generated identifiers are GAMS-legal" is mostly correct (only 1 model has a reserved word collision), but the quoting issue (7 models) is a related but distinct problem.

---

## Unknown 3.4: How many path_syntax_error models fail due to translate-stage issues vs. emitter-stage issues?

### Priority
**High** — Distinguishes between IR/translator bugs (deeper fixes) and emitter formatting bugs (shallower fixes)

### Assumption
Most path_syntax_error models fail due to emitter-stage issues (incorrect MCP formatting, wrong Model statement) rather than translator-stage issues (incorrect KKT/stationarity computation).

### Research Questions
1. For each failing model, does the MCP file compile in GAMS (`gams file.gms --compile-only`)?
2. If it compiles, does PATH produce a meaningful error or just "infeasible"?
3. If it doesn't compile, is the error in the Model statement, equation definitions, or variable declarations?
4. Are there models where the IR/translator produces mathematically wrong stationarity equations?

### How to Verify
**Test Case 1:** For 10 failing models, attempt `gams *_mcp.gms --compile-only` to separate compile errors from solve errors
**Test Case 2:** For compile-passing models, examine PATH solver output for specific error messages

### Risk if Wrong
- **Translator bugs dominant:** Fixes require changes to KKT assembly, not just emitter (much harder)
- **Mixed causes:** Need both translator and emitter fixes, doubling the work

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The assumption that "most fail due to emitter-stage issues" is WRONG. The failures are roughly evenly distributed across all three pipeline stages:

| Pipeline Stage | Model Count | % of Total | Subcategories |
|---------------|-------------|-----------|---------------|
| **Parser (IR builder)** | 16 | 36% | A (missing Table data) |
| **Emitter (formatting)** | 15 | 33% | B (domain violation), D (exponent parens), E (index quoting) |
| **Translator (KKT generation)** | 14 | 31% | C (uncontrolled set), F (reserved word), G (index reuse), I (variable unreferenced), J (dimension mismatch) |

Key finding: The **parser stage** is actually the largest single contributor (16/45 = 36%), not the emitter. The IR builder's failure to capture Table data is the dominant root cause. This was unexpected — the assumption was that parser-stage issues would be minimal since these models all parse successfully; the Table data issue is specifically about data not being stored in the IR, not about parse failure.

The emitter and translator each contribute about a third of the failures, with distinct fix strategies:
- **Emitter fixes** (15 models): formatting corrections — relatively simple
- **Translator fixes** (14 models): KKT generation and domain handling — more complex

---

# Category 4: Deferred Sprint 20 Issues

## Unknown 4.1: Which of the 13 deferred issues overlap with Sprint 21 Priority 1–3 work?

### Priority
**High** — Overlap identification prevents duplicate work and enables efficient scheduling

### Assumption
Issues #837 (springchain) and #840 (saras) fully overlap with Priority 1 (macro expansion). Some other deferred issues may be partially resolved by Priority 2 (internal_error) or Priority 3 (path_syntax_error) work.

### Research Questions
1. Does fixing macro expansion (#837, #840) automatically resolve any other deferred issues?
2. Do any of the 7 internal_error models correspond to deferred issues (#763, #764, #765)?
3. Do any path_syntax_error fixes resolve deferred solve-quality issues (#826, #827, #828)?
4. Which deferred issues are completely independent of Priority 1–3 work?

### How to Verify
**Test Case 1:** Cross-reference deferred issue model names with internal_error and path_syntax_error model lists
**Test Case 2:** After macro expansion is implemented, retest saras and springchain to verify issue closure
**Test Case 3:** After internal_error fixes, check if chenery (#763), mexss (#764), orani (#765) status changes

### Risk if Wrong
- **Undiscovered overlaps:** Duplicate work on the same model from different angles
- **Missed dependencies:** Fixing one issue may break or enable another

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The overlap is broader than assumed. #837 and #840 do fully overlap with Priority 1 (correct), but additional overlaps exist:

1. **Full Priority 1 overlaps (2 issues):** #837 (springchain) and #840 (saras) — both need `$eval`/`$set`/`%macro%` expansion, which is exactly Priority 1 work
2. **Partial Priority 3 overlaps (2 issues):** #810 (lmp2) appears in path_syntax_error Subcategory A (missing Table data); #827 (gtm) appears in Subcategory B (domain violation)
3. **No Priority 2 overlaps:** None of the 13 deferred issue models appear in the 7 internal_error models (clearlak, imsl, indus, sarf, senstran, tfordy, turkpow)
4. **Already resolved (3 issues):** #763 (chenery — fixed in Sprint 20), #810 (lmp2 — loop extraction fixed), #835 (bearing — `.scale` emission added)
5. **Completely independent (7 issues):** #764 (mexss), #765 (orani), #757 (bearing solver), #826 (decomp), #828 (ibm1), #830 (gastrans), #789 (min/max)

The assumption that "only #837 and #840 overlap" was wrong — 4 issues have overlaps (2 full + 2 partial), and 3 are already resolved (including 1 that also has a partial overlap). Only 7 of 13 are truly independent.

---

## Unknown 4.2: Is the gastrans Jacobian timeout (#830) a fundamental performance issue or a dynamic subset bug?

### Priority
**Medium** — gastrans Jacobian took ~22 hours in Sprint 20 testing; understanding the root cause determines whether to fix or defer

### Assumption
The timeout is caused by dynamic subset expansion creating an exponential blowup in the Jacobian computation, not a fundamental limitation of the AD system.

### Research Questions
1. How many terms does the gastrans Jacobian actually have?
2. Is the Jacobian dense or sparse? What is the expected sparsity pattern?
3. Does the dynamic subset fallback (falling back to parent set) create unnecessary Jacobian entries?
4. Would fixing the dynamic subset handling reduce Jacobian computation from hours to seconds?

### How to Verify
**Test Case 1:** Profile the Jacobian computation for gastrans with timing per equation
**Test Case 2:** Count Jacobian nonzeros expected vs. actual
**Test Case 3:** Compare gastrans Jacobian time with a similar-sized model that doesn't use dynamic subsets

### Risk if Wrong
- **Fundamental performance issue:** gastrans may never be tractable without sparse Jacobian redesign
- **Dynamic subset fix insufficient:** Other models may have similar timeout issues

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:** The timeout is **both** a dynamic subset bug AND a performance issue, confirming the assumption that dynamic subset expansion causes the blowup.

1. **Dynamic subset bug:** Dynamic subsets `ap`, `as`, `aij` have 0 static members in the IR because their values are populated at GAMS runtime (e.g., `ap(a) = not as(a)`). The parser captures the `SetDef` with `domain=('a',)` but empty `members=[]`.

2. **Fallback mechanism:** `resolve_set_members()` in `src/ad/index_mapping.py` (lines 163-191) falls back to parent sets when members are empty. For `aij(a,i,i)`, this means 24×20×20 = 9,600 instances instead of the correct ~24 arc tuples.

3. **Combinatorial explosion:** The Jacobian computation loop iterates over all equation instances × all variable instances. With fallback to parent sets: ~11 equations × 9,600 instances × 7 variables × ~9,600 var instances ≈ billions of operations. Even with sparsity filtering (`referenced_vars` check), this remains intractable.

4. **Fix feasibility:** Preserving dynamic subset members during parsing would reduce the enumeration space by ~400× (from 9,600 to ~24 for `aij`). However, the Jacobian also lacks general sparsity optimization (no early domain-mismatch termination).

5. **Estimated effort:** 8-10h total (4-6h for parser dynamic subset preservation + 2-4h for Jacobian sparsity improvements). A quick mitigation (Jacobian timeout with error message) takes ~1h.

**Recommendation:** Defer to Sprint 22+ due to high effort. Add 1h Jacobian timeout as optional quick win.

---

## Unknown 4.3: Can the min/max objective reformulation issue (#789) be resolved within Sprint 21's scope?

### Priority
**Medium** — Issue #789 affects min/max in objective-defining equations; may require changes to the KKT assembly

### Assumption
Issue #789 (min/max reformulation producing spurious variables) can be resolved with a targeted fix to the KKT assembly or emitter, without requiring a fundamental redesign of the reformulation strategy.

### Research Questions
1. What specifically is "spurious" about the variables generated by min/max reformulation?
2. Does the issue affect all min/max usage or only objective-defining cases?
3. Is the fix in the reformulation logic, the KKT assembly, or the emitter?
4. How many models are blocked by this issue?

### How to Verify
**Test Case 1:** Read `docs/issues/ISSUE_789_minmax-reformulation-spurious-variables.md` for full details
**Test Case 2:** Identify which models use min/max in objective equations
**Test Case 3:** Trace the spurious variable generation through the code

### Risk if Wrong
- **Fundamental redesign needed:** Min/max reformulation strategy may need replacement (8–12h)
- **Broader impact:** Fix may affect non-objective min/max usage

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED

**Findings:** Yes, #789 can be resolved within Sprint 21's scope with a targeted fix (2-3h), confirming the assumption.

1. **Structural fix already done:** The spurious lambda variables bug was already fixed — system now correctly has 10 variables/10 equations instead of 14/14.

2. **Remaining issue is well-understood:** When min/max defines the objective variable (`minimize z` where `z = min(x,y)`), the epigraph reformulation produces `ν = -1` (from `∂L/∂z = 1 + ν = 0`), which then requires `λ₀ + λ₁ = -1` — infeasible since λ ≥ 0.

3. **Fix approach:** Detect when min/max defines the objective variable and use direct constraints (`z ≤ x, z ≤ y`) instead of the auxiliary variable approach. This is a targeted change in `src/kkt/reformulation.py`'s `reformulate_min()` / `reformulate_max()` functions.

4. **Scope:** The fix only affects objective-defining min/max cases. Non-objective min/max (in regular constraints) continues to use the existing epigraph reformulation, which works correctly.

5. **No fundamental redesign needed:** The fix is a conditional branch in the reformulation logic, not an architectural change.

**Recommendation:** Do in Sprint 21 as Priority 4 item #1 (highest leverage among deferred issues).

---

# Category 5: Full Pipeline Match Rate Improvement

## Unknown 5.1: What is the primary divergence cause for the 17 solve-but-no-match models?

### Priority
**Critical** — Determines the fix strategy for closing the 33-solve / 16-match gap (Sprint 21 target: 20+ matches)

### Assumption
The primary divergence cause is `.l` initialization differences — the MCP solver starts from different initial points than the NLP solver, leading to different local optima for non-convex models. For convex models, the divergence is due to tolerance differences.

### Research Questions
1. How many of the 17 non-matching models are convex vs. non-convex?
2. For convex non-matching models, what are the relative differences? (tolerance issue vs. real divergence)
3. For non-convex non-matching models, are they finding different local optima?
4. Does adding `.l` initialization to the MCP improve match rates?
5. Are any models producing NaN/Inf objectives? (emitter bug, not divergence)

### How to Verify
**Test Case 1:** List all 17 models with their relative objective difference
**Test Case 2:** Cross-reference with convexity status in gamslib_status.json
**Test Case 3:** For the 5 closest near-matches, test with relaxed tolerance (1e-2 instead of 1e-4)

### Risk if Wrong
- **Initialization not the cause:** `.l` emission work from Sprint 20 may have no match rate impact
- **Tolerance too tight:** May be matching more models than reported if tolerance is relaxed
- **Fundamental formulation issues:** MCP may be mathematically different from NLP for some models

### Estimated Research Time
2–3 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The assumption that the primary divergence cause is `.l` initialization differences is WRONG. The analysis of all 17 models reveals a diverse set of root causes:

1. **KKT formulation correctness issues (dominant cause):**
   - **IndexOffset gradient bug** (2-4 models: chakra, catmix, possibly abel, qabel): `_diff_varref()` in `src/ad/derivative_rules.py` cannot match `IndexOffset("t", Const(-1))` against concrete index strings, producing zero gradients for lagged/lead variables. This causes missing stationarity terms and convergence to trivial/initial points.
   - **LP bound multiplier gaps** (4 models: apl1p, apl1pca, sparta, aircraft): Verified_convex LP models with 3-79% mismatch strongly suggests missing bound dual variables in the KKT system.
   - **Possible objective sign errors** (2 models: abel, qabel): MCP objective much larger than NLP, consistent with maximizing instead of minimizing a quadratic penalty.
   - **Formulation over-constraints** (1 model: himmel16): Duplicate objective equations force trivial solution.

2. **Local optima / solver convergence (secondary cause, 5 models):** weapons (highly nonconvex exponential structure, 7822 iterations), chenery (calibration sensitivity), process (bilinear constraints), trig (multi-modal trigonometric landscape), mathopt1 (degenerate equality constraint).

3. **Tolerance issue (1 model):** port (0.134% difference, LP degeneracy).

4. **Data mismatch (1 model):** circle (different random seeds between NLP and MCP).

**Distribution by root cause category:**
| Root Cause | Count | % of 17 |
|-----------|-------|---------|
| KKT formulation bugs | 7-9 | 41-53% |
| Nonconvex local optima | 5 | 29% |
| Tolerance | 1 | 6% |
| Data mismatch | 1 | 6% |
| Initialization | 1 | 6% |

**Key insight:** `.l` emission is necessary but NOT sufficient — all 33 solving models already have `.l` values emitted. The bottleneck is KKT formulation correctness, not initialization.

See `SOLVE_MATCH_GAP_ANALYSIS.md` for full per-model analysis.

---

## Unknown 5.2: Which near-match models (rel_diff < 1e-2) can be fixed with tolerance or initialization changes?

### Priority
**High** — Near-matches are the lowest-hanging fruit for improving match rate from 16 to 20+

### Assumption
At least 4–6 of the 17 non-matching models have relative differences < 1e-2 and can be brought to match status by: (a) relaxing match tolerance, (b) adding `.l` initialization, or (c) fixing `.scale` emission.

### Research Questions
1. How many models have rel_diff < 1e-3 (very close to matching)?
2. How many models have rel_diff between 1e-3 and 1e-2 (close to matching)?
3. For each near-match, what is the specific objective value difference?
4. Would a relative tolerance of 1e-3 (instead of exact match) be appropriate?
5. Does port (rel_diff 1.3e-3, from Sprint 20 analysis) match with relaxed tolerance?

### How to Verify
**Test Case 1:** Sort 17 models by relative objective difference
**Test Case 2:** Test near-matches with tolerance 1e-3, 1e-2, 1e-1
**Test Case 3:** For each near-match, compare MCP `.l` values with GAMS `.l` values

### Risk if Wrong
- **No near-matches:** All 17 models diverge significantly, making 20+ target harder
- **Wrong tolerance:** Relaxing tolerance may give false positives (wrong solution accepted)

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** Only **2 models** (not 4-6) have rel_diff < 1e-2:

| Model | Rel Diff | Type | Fixable? |
|-------|----------|------|----------|
| port | 0.00134 (0.134%) | LP, verified_convex | **Yes** — tolerance adjustment (rtol=2e-3) |
| chakra | 0.00707 (0.71%) | NLP, likely_convex | **Yes** — IndexOffset gradient fix |

**Category A (near-match) count: 2, not 4-6.** The assumption that "at least 4-6 models have rel_diff < 1e-2" was wrong.

**Why only 2:** The 17 non-matching models have a bimodal distribution — 2 near-matches (rel_diff < 1%), then a large gap to the next cluster at 3.3% (apl1p). There are no models in the 1e-3 to 1e-2 range between port and apl1p.

**Fixability assessment:**
- **port** (rtol=2e-3): YES — pure tolerance/solver-numerics issue. Both NLP and MCP report optimal. Adjusting comparison tolerance from 1e-4 to 2e-3 would classify port as matching. Effort: <1h.
- **chakra** (IndexOffset gradient fix): YES — the stationarity equations are missing gradient terms due to `_diff_varref()` not handling IndexOffset indices. Fixing derivative_rules.py would produce correct KKT conditions. Effort: 3-4h.

**Beyond Category A:** Fixing the IndexOffset gradient bug may also help Category B models catmix (rel_diff=1.0 but same root cause) and potentially abel/qabel. Combined with LP bound investigation, the realistic improvement is 16 → 18-20 matches.

See `SOLVE_MATCH_GAP_ANALYSIS.md` for full analysis.

---

## Unknown 5.3: Does the Sprint 20 `.l` emission work actually improve match rates?

### Priority
**High** — Sprint 20 invested 4+ hours in `.l` emission; unknown whether it helps match rate

### Assumption
The `.l` initialization emission implemented in Sprint 20 (Days 1–3) will improve match rates for models where the NLP solution depends on a good starting point, particularly non-convex models.

### Research Questions
1. How many of the 33 solving models have `.l` values emitted in their MCP?
2. For models with `.l` emission, does the MCP solver converge to the same solution as GAMS?
3. Are there models where `.l` emission hurts (moves starting point away from optimal)?
4. Is `.l` emission working correctly for indexed variables?

### How to Verify
**Test Case 1:** Count MCP files with `.l` assignments: `grep -l '\.l(' data/gamslib/mcp/*_mcp.gms | wc -l`
**Test Case 2:** Compare match rate with and without `.l` emission (if possible to toggle)
**Test Case 3:** For a non-matching model with `.l` values, check if GAMS finds the same solution

### Risk if Wrong
- **No improvement:** `.l` emission doesn't help match rate; need different approach
- **Incorrect `.l` values:** Emitted values may be wrong, hurting convergence

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
❌ **Status:** WRONG (partially)

**Findings:** The `.l` emission work is necessary infrastructure but does NOT directly improve match rates as assumed.

**Evidence:**
1. **All 33 solving models already have `.l` values emitted.** Every MCP file in `data/gamslib/mcp/` contains `.l` initialization lines (1-102 lines per file, depending on model size). The Sprint 20 `.l` emission work is fully deployed across the solve-success population.

2. **16 models match, 17 don't — but ALL have `.l` emission.** The `.l` emission is a necessary condition for solving (PATH needs starting points) but is NOT the differentiating factor between matching and non-matching models.

3. **The non-matching models fail for structural reasons, not initialization:**
   - 7-9 models have KKT formulation bugs (missing gradient terms, sign errors, bound gaps)
   - 5 models converge to different local optima despite having `.l` values
   - 1 model has data mismatch, 1 has tolerance issue

4. **`.l` emission quality varies:**
   - Some models have generic initialization (all set to 1): apl1p, sparta, port
   - Some have proper model-specific initialization: alkyl, chenery, catmix
   - The quality of initialization correlates weakly with match success — some well-initialized models still don't match (alkyl, chenery), while some generically-initialized models do match (ajax, trnsport)

**Conclusion:** Sprint 20's `.l` emission work was essential infrastructure that enabled 33 models to solve (vs. potentially fewer without any `.l` values). However, it is NOT the bottleneck for the 17-model match gap. Improving match rate requires fixing KKT formulation correctness issues, not better initialization.

**Partial verification:** The assumption that `.l` emission "improves match rates for non-convex models" is partially true in that it enables solving, but wrong in that it's the primary lever for improving match rate from 16 to 20+.

See `SOLVE_MATCH_GAP_ANALYSIS.md` for full analysis.

---

# Category 6: Semantic Error Resolution

## Unknown 6.1: Are the 7 semantic_undefined_symbol models caused by `$include` references?

### Priority
**High** — If all 7 models use `$include` to define symbols, they cannot be fixed without `$include` support (which is out of Sprint 21 scope)

### Assumption
Most of the 7 semantic_undefined_symbol models reference symbols defined in `$include` files. Since nlp2mcp doesn't support `$include`, these models should be documented and excluded from metrics rather than fixed.

### Research Questions
1. Which of the 7 models contain `$include` directives?
2. For models with `$include`, are the undefined symbols defined in the included files?
3. For models without `$include`, what causes the undefined symbol — is it a parser bug or a GAMSLIB source issue?
4. Are any of the 7 models fixable within Sprint 21 without `$include` support?

### How to Verify
**Test Case 1:** Run each of the 7 models through `parse_file()` and capture the undefined symbol name
**Test Case 2:** `grep -l '\$include' data/gamslib/raw/{model1,model2,...}.gms` for each model
**Test Case 3:** For each `$include` model, check if the included file exists and defines the missing symbol

### Risk if Wrong
- **Not `$include` related:** Some models may have parser bugs that are fixable (missed opportunity)
- **All `$include` related:** Sprint 21 Semantic Error Resolution workstream has nothing to fix

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The assumption that "most of the 7 models reference symbols defined in `$include` files" is WRONG. **None** of the 7 models are caused by `$include` references. All 7 fail because the nlp2mcp parser/IR builder doesn't recognize certain GAMS built-in functions or language features:

1. **Missing GAMS built-in functions in grammar (5 models):**
   - camcge, feedtray: Missing `sign()` — GAMS built-in for sign of argument (-1, 0, +1)
   - cesam2: Missing `centropy()` — GAMS built-in for cross-entropy computation
   - sambal: Missing `mapval()` — GAMS built-in for extended range arithmetic classification
   - procmean: Missing `betareg()` — GAMS built-in for regularized incomplete Beta function
   - All 4 functions are listed in the GAMS commands reference but missing from the FUNCNAME regex in `gams_grammar.lark`

2. **Missing Acronym handler in IR builder (1 model):**
   - worst: `Acronym future, call, puto;` — grammar parses via `acronym_stmt` rule (line 650) but IR builder has no handler, so acronym values are never registered as known symbols

3. **sameas() string literal misinterpretation (1 model):**
   - cesam: `$(not sameas(ii,"ROW"))` — IR builder rejects `"ROW"` as undefined symbol reference in sameas() condition, but it's a quoted set element name

**Key finding:** All 7 are fixable parser/IR bugs. None should be excluded from metrics. The FUNCNAME fix alone (adding `sign|centropy|mapval|betareg`) would unblock 5 of 7 models in ~30min.

See `SEMANTIC_ERROR_AUDIT.md` for full per-model analysis.

---

## Unknown 6.2: Should semantic_undefined_symbol models be excluded from pipeline metrics?

### Priority
**Medium** — Affects how we count parse success and whether Sprint 21 parse target (135/160) is realistic

### Assumption
Models that fail due to `$include` references should be reclassified as "unsupported" rather than "parse failure," since they require features outside Sprint 21 scope.

### Research Questions
1. How many of the 7 models are genuinely unsupported vs. fixable?
2. If we exclude `$include`-dependent models, what is the effective denominator for parse rate?
3. Does GAMS documentation indicate which GAMSlib models are self-contained vs. requiring includes?
4. Should we create a new error category (e.g., `requires_include`) for these models?

### How to Verify
**Test Case 1:** Determine fixable vs. unsupported count from Unknown 6.1 results
**Test Case 2:** Recalculate parse rate with adjusted denominator
**Test Case 3:** Review how Sprint 20 handled similar exclusions (convexity filtering)

### Risk if Wrong
- **Incorrect metrics:** Parse rate may be misleading if unsupported models inflate the denominator
- **Scope creep:** Attempting to fix `$include` models would blow Sprint 21 budget

### Estimated Research Time
30 minutes (after Unknown 6.1 is resolved)

### Owner
Development team

### Verification Results
❌ **Status:** WRONG

**Findings:** The assumption that "models failing due to `$include` references should be reclassified as unsupported" is WRONG because **none** of the 7 models fail due to `$include` references. All 7 are fixable parser/IR bugs:

1. **No models should be excluded:** All 7 `semantic_undefined_symbol` models fail due to nlp2mcp parser/IR builder bugs, not external dependencies or GAMSLIB source errors.

2. **The effective denominator should NOT change:** Since all 7 are fixable, they should remain in the 160-model denominator. No reclassification to "unsupported" is warranted.

3. **No new error category needed:** The `semantic_undefined_symbol` category correctly describes the symptom. The root causes are:
   - 5 models: missing GAMS built-in functions in grammar FUNCNAME regex (fix: ~30min)
   - 1 model: missing Acronym handler in IR builder (fix: ~1-2h)
   - 1 model: sameas() string literal misinterpretation (fix: ~1h)

4. **Metric impact after fixes:**
   - Current parse rate: 132/160 (82.5%)
   - After FUNCNAME fix: 137/160 (85.6%) — +5 models
   - After all 3 fixes: 139/160 (86.9%) — +7 models
   - Sprint 21 parse target (≥135/160): exceeded by FUNCNAME fix alone

**Conclusion:** These models represent easy wins, not exclusion candidates. The FUNCNAME fix alone (~30min) exceeds the Sprint 21 parse target.

See `SEMANTIC_ERROR_AUDIT.md` for full per-model analysis.

---

# Category 7: Emerging Translation Blockers

## Unknown 7.1: How many newly-parsed models will fail in translation?

### Priority
**Medium** — Sprint 21 parse improvements may increase parse count from 132 to 135+, but new parses may immediately fail in translation

### Assumption
As Sprint 21 fixes internal_error and lexer_invalid_char issues, approximately 5–10 newly-parsing models will enter the translation pipeline. Of these, ~50% will translate successfully and ~50% will hit new translation blockers.

### Research Questions
1. Of the 28 currently-failing parse models, how many are close to parsing (1–2 fixes away)?
2. For models that will newly parse, what translation challenges are expected? (new derivative rules, new IR constructs?)
3. Does the translator already handle all constructs that the newly-parsing models will contain?
4. Are there translation patterns we've never seen before in the newly-parsing models?

### How to Verify
**Test Case 1:** After fixing internal_error models (Priority 2), run them through translation and record results
**Test Case 2:** After macro expansion (Priority 1), run springchain/saras through translation
**Test Case 3:** Tally new translation failures by error type

### Risk if Wrong
- **Higher failure rate:** >50% translation failure would require more Priority 7 work
- **Novel translation patterns:** New constructs may require significant translator work

### Estimated Research Time
1 hour (estimated based on prior sprint experience)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Will macro-expanded models introduce new translation patterns?

### Priority
**Medium** — springchain and saras may contain GAMS constructs not yet seen in translatable models

### Assumption
After macro expansion, springchain and saras will use standard GAMS constructs (equations, variables, sets, parameters) that the translator already handles.

### Research Questions
1. What equation/constraint patterns does springchain use after macro expansion?
2. Does saras use any advanced GAMS features (e.g., dynamic sets, conditional equations)?
3. Are there new function calls or operators in these models that the AD system doesn't support?
4. Do the models use lead/lag syntax that would require IR builder changes?

### How to Verify
**Test Case 1:** After macro expansion, parse springchain and examine the IR
**Test Case 2:** After macro expansion, run saras through translation and check for errors
**Test Case 3:** Compare equation patterns against known-working translatable models

### Risk if Wrong
- **New patterns:** May need translator extensions before models can translate
- **AD gaps:** New expression types may require new differentiation rules

### Estimated Research Time
1 hour (after Priority 1 macro expansion is implemented)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 8: PATH Convergence Investigation

## Unknown 8.1: How many models fail with `path_solve_terminated` vs. other PATH failure modes?

### Priority
**Critical** — Determines the scope of Sprint 21's PATH Convergence Investigation workstream (8–10h budget)

### Assumption
Current baseline (per `gamslib_status.json`) shows that some solving models already fail with `path_solve_terminated` (e.g., `camshape`). The PATH convergence investigation targets models that solve but produce wrong answers (the 17 non-matching models) plus any models where PATH terminates early with `path_solve_terminated`.

### Research Questions
1. Among the 88 solve-stage failures, how many are `path_solve_terminated` (PATH ran but didn't converge)?
2. How many are `path_syntax_error` (PATH couldn't start due to MCP syntax issues)?
3. How many are translation failures that prevent MCP generation entirely?
4. For `path_solve_terminated` models, what does PATH's iteration log say?
5. Are there models where PATH reports "locally infeasible" vs. "maximum iterations exceeded"?

### How to Verify
**Test Case 1:** Classify all 88 solve failures into subcategories based on error output
**Test Case 2:** For `path_solve_terminated` models, examine PATH iteration logs
**Test Case 3:** For `path_solve_terminated` models, test with relaxed tolerances and increased iteration limits

### Risk if Wrong
- **More `path_solve_terminated` than expected:** 8–10h may be insufficient for systematic analysis
- **No `path_solve_terminated`:** PATH convergence investigation has no direct targets (focus shifts to match quality)

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.2: Can PATH solver options (tolerances, iteration limits) improve convergence for near-convergent models?

### Priority
**High** — If solver options can rescue some models, this is a low-effort way to increase solve count

### Assumption
Adjusting PATH solver options (e.g., `option mcp=PATH; PATH.optfile = 1;` with relaxed convergence tolerance) can improve convergence for 3–5 additional models.

### Research Questions
1. What PATH solver options control convergence (tolerance, iteration limit, crash method)?
2. Does the MCP emitter currently set any PATH options?
3. For models that PATH terminates on, does increasing iteration limit help?
4. Does relaxing convergence tolerance (e.g., from 1e-8 to 1e-6) rescue any models?
5. Does PATH's crash method selection affect convergence for non-convex models?

### How to Verify
**Test Case 1:** For 3–5 `path_solve_terminated` models, test with `convergence_tolerance = 1e-6`
**Test Case 2:** For the same models, test with `major_iteration_limit = 10000`
**Test Case 3:** Compare solve success rate with default vs. relaxed options

### Risk if Wrong
- **Options don't help:** All `path_solve_terminated` models have fundamental formulation issues
- **Options too loose:** Relaxed tolerance produces "solved" status but wrong answer

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 8.3: Is the KKT system generated by nlp2mcp mathematically equivalent to GAMS's own MCP formulation?

### Priority
**Critical** — If our KKT → MCP transformation has systematic errors, all solve/match results are unreliable

### Assumption
The KKT system generated by nlp2mcp (stationarity + complementarity + feasibility) is mathematically equivalent to the MCP that GAMS would generate from the same NLP, modulo numerical differences from different AD implementations.

### Research Questions
1. For a simple model (e.g., trnsport), does our MCP have the same number of equations and variables as GAMS's MCP?
2. Are stationarity equations correct (∇f + Σλᵢ∇gᵢ + Σμⱼ∇hⱼ = 0)?
3. Are complementarity pairings correct (λᵢ ⊥ gᵢ, not λᵢ ⊥ -gᵢ)?
4. Are bound multiplier signs correct (πL ≥ 0 for lower bounds, πU ≥ 0 for upper bounds)?
5. For matching models, do the dual variable values agree with GAMS's duals?

### How to Verify
**Test Case 1:** For trnsport, manually verify KKT system against hand-derived KKT
**Test Case 2:** For 3 matching models, compare dual variable values
**Test Case 3:** For 3 non-matching models, check if stationarity residuals are zero at GAMS's solution

### Risk if Wrong
- **Systematic KKT error:** All MCPs have the same bug; matches may be coincidental
- **Sign convention error:** Complementarity conditions may be reversed
- **Missing terms:** Stationarity equations may miss some derivative terms

### Estimated Research Time
3 hours

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 9: Solution Comparison Enhancement

## Unknown 9.1: What comparison metrics beyond objective value are meaningful for MCP validation?

### Priority
**High** — Sprint 21 includes "Solution Comparison Enhancement" to extend beyond objective value matching

### Assumption
Comparing primal variable values, dual variable values, and complementarity residuals (in addition to objective value) provides a more robust validation of MCP correctness.

### Research Questions
1. Can we extract primal variable values from PATH solver output?
2. Can we extract dual variable values (multipliers) from PATH solver output?
3. What is a meaningful tolerance for primal/dual comparison? (absolute vs. relative)
4. How do we handle differently-named variables in NLP vs. MCP? (e.g., MCP adds `lam_*`, `stat_*`)
5. Are complementarity residuals useful for detecting formulation errors even when objectives match?

### How to Verify
**Test Case 1:** For trnsport (known matching model), extract primal and dual values from both NLP and MCP solutions
**Test Case 2:** Compare primal values — do they agree within tolerance?
**Test Case 3:** Compute complementarity residuals (λᵢ * gᵢ) — are they near zero?

### Risk if Wrong
- **Can't extract values:** PATH output format may not include all needed information
- **Tolerance too strict:** Primal/dual comparison fails for numerically valid solutions
- **Meaningless metrics:** Complementarity residuals may always be zero if PATH converges

### Estimated Research Time
2 hours

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 9.2: What is the right tolerance framework for model-appropriate comparison?

### Priority
**Medium** — Different models have different scales; a single tolerance may be too strict for some and too loose for others

### Assumption
A combined relative/absolute tolerance (e.g., `abs(a-b) < max(atol, rtol * max(abs(a), abs(b)))`) with defaults `atol=1e-6, rtol=1e-4` works for most models.

### Research Questions
1. What objective value scales are present across the 33 solving models? (range from 0.001 to 1e12?)
2. Does relative tolerance work for models with objective near zero?
3. Should tolerance be model-specific (based on GAMS's own convergence tolerance)?
4. How does GAMS report solution quality — do we have access to this information?

### How to Verify
**Test Case 1:** Tabulate objective values for all 33 solving models to understand scale range
**Test Case 2:** Apply proposed tolerance formula to all 33 models — how many match?
**Test Case 3:** Compare with GAMS's own optimality tolerance for each model

### Risk if Wrong
- **Too strict:** Models that are correctly solving are flagged as non-matching
- **Too loose:** Models with formulation errors are incorrectly classified as matching

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 9.3: Can the comparison framework detect specific formulation errors?

### Priority
**Low** — Nice-to-have diagnostic capability; not required for Sprint 21 acceptance criteria

### Assumption
By comparing primal values, dual values, and complementarity residuals independently, the comparison framework can pinpoint whether a mismatch is caused by: (a) wrong objective gradient, (b) wrong constraint Jacobian, (c) wrong complementarity pairing, or (d) different local optimum.

### Research Questions
1. If the objective matches but primal values differ — what does this indicate?
2. If primal values match but duals differ — what does this indicate?
3. If complementarity residuals are large — is it always a formulation error?
4. Can we build a diagnostic decision tree from comparison results?

### How to Verify
**Test Case 1:** For a matching model, intentionally introduce a gradient error and observe what comparison metrics change
**Test Case 2:** For a matching model, intentionally introduce a Jacobian error and observe
**Test Case 3:** Document the diagnostic patterns

### Risk if Wrong
- **Diagnostic not reliable:** Comparison patterns don't uniquely identify error types
- **Low priority:** Minimal sprint impact if diagnostic is incomplete

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Template for Adding New Unknowns During Sprint

```markdown
## Unknown X.N: [Question]

### Priority
**[Critical/High/Medium/Low]** — [Brief justification]

### Assumption
[What we currently assume]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify
**Test Case 1:** [Description]
**Test Case 2:** [Description]

### Risk if Wrong
- [Risk 1]
- [Risk 2]

### Estimated Research Time
[X hours]

### Owner
[Team/Person]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

# Newly Discovered Unknowns

*Add unknowns discovered during Sprint 21 here, then categorize and assign priority.*

---

# Confirmed Knowledge (Resolved Unknowns)

*Move resolved items here with findings during prep and sprint execution.*

---

## Next Steps

1. **Before Sprint 21 Day 1:** Research and verify all Critical unknowns (1.1, 2.1, 3.1, 3.2, 5.1, 8.1, 8.3)
2. **Before Sprint 21 Day 1:** Research and verify all High unknowns
3. **During Sprint 21:** Update verification results as work progresses
4. **At checkpoints:** Review for newly discovered unknowns
5. **Post-sprint:** Move all resolved unknowns to Confirmed Knowledge section

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Research GAMS Macro Expansion Semantics | 1.1, 1.2, 1.3, 1.4 | Full macro expansion research covers all Category 1 unknowns |
| Task 3: Catalog internal_error Root Causes | 2.1, 2.2, 2.3 | Running 7 models reveals root causes, lead/lag usage, and fix complexity |
| Task 4: Catalog path_syntax_error Root Causes | 3.1, 3.2, 3.3, 3.4 | Systematic triage of 45 models reveals clustering, pairing, naming, and stage issues |
| Task 5: Triage Deferred Sprint 20 Issues | 4.1, 4.2, 4.3 | Issue review identifies overlaps, gastrans root cause, and min/max scope |
| Task 6: Analyze Solve-Match Gap | 5.1, 5.2, 5.3 | Gap analysis reveals divergence causes, near-matches, and `.l` emission impact |
| Task 7: Audit semantic_undefined_symbol Models | 6.1, 6.2 | Model-by-model audit determines `$include` vs. parser bug vs. source error |
| Task 8: Snapshot Baseline Metrics | 8.1 | Pipeline retest captures current solve failure subcategory counts |
| Task 9: Review Sprint 20 Retrospective | *(process alignment, no specific unknowns)* | Ensures process recommendations are applied |
| Task 10: Plan Sprint 21 Detailed Schedule | *(integrates all verified unknowns)* | Uses findings from Tasks 2–9 to create data-driven schedule |

### Coverage Analysis

- **All 27 unknowns mapped:** 20 unknowns are directly verified by prep Tasks 2–8
- **7 unknowns not directly mapped during prep:** 7.1, 7.2 (Emerging Translation Blockers), 8.2, 8.3 (PATH Convergence), 9.1, 9.2, 9.3 (Solution Comparison) — these are inherently sprint-time unknowns that can only be fully verified after Priority 1–2 fixes are implemented
