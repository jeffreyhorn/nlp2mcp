# Sprint 17 Lexer/Parser Improvement Plan

**Created:** January 29, 2026  
**Sprint:** 17 Prep - Task 5  
**Status:** Complete  
**Purpose:** Prioritized plan for addressing 97 lexer_invalid_char errors

---

## Executive Summary

This document provides a comprehensive analysis and prioritized fix plan for the 97 models that fail with `lexer_invalid_char` errors in the Sprint 16 baseline. The analysis categorizes errors into 12 distinct subcategories with varying fixability and effort estimates.

**Sprint 16 Baseline:**
- Parse success: 48/160 (30.0%)
- lexer_invalid_char failures: 97 models (86.6% of parse failures)
- Target: +20-22 models parsing (achieving ~42-44% parse rate)

**Key Findings:**
1. **12 models** fail due to `inf`/`na` reserved word conflicts (easy fix, high impact)
2. **12 models** fail due to multi-line statement continuation issues (medium fix)
3. **6 models** fail due to display statement continuation (easy fix)
4. **58 models** are fixable with targeted lexer/grammar changes (29 Easy + 29 Medium in detailed breakdown)
5. **~39 models** are hard or unfixable (33 complex set data + 6 structurally incompatible; defer to future)

**Recommended Sprint 17 Focus:**
| Priority | Models (raw) | Models (unique) | Hours | Approach |
|----------|--------------|-----------------|-------|----------|
| Quick wins | 32 | 20-22 | 12h | Lexer regex + grammar rules |
| Medium effort | 20 | 10-12 | 13h | Grammar extensions |
| Deferred (Phase 3) | 18 | 18 | 20h+ | Complex set data hard subset (14) + misc (4) |

_Note: "Models (raw)" is the sum of per-fix counts; "Models (unique)" accounts for overlap where one model has multiple issues._

**Target:** +20-22 unique models parsing with Phase 1 (12h effort); Phase 1+2 together achieves +30-34 models (~49-51% parse rate) with 25h total effort

---

## Table of Contents

1. [Subcategory Breakdown](#1-subcategory-breakdown)
2. [Detailed Subcategory Analysis](#2-detailed-subcategory-analysis)
3. [Prioritized Fix Plan](#3-prioritized-fix-plan)
4. [Grammar/Lexer File Locations](#4-grammarlexer-file-locations)
5. [Unknown Verification Summary](#5-unknown-verification-summary)

---

## 1. Subcategory Breakdown

### Complete Subcategory Summary (97 models)

| # | Subcategory | Count | % | Fixability | Effort | Priority |
|---|-------------|-------|---|------------|--------|----------|
| 1 | Reserved word conflicts (`inf`, `na`) | 12 | 12% | Easy | 2h | P1 |
| 2 | Display statement continuation | 6 | 6% | Easy | 2h | P1 |
| 3 | Multi-line statement continuation | 12 | 12% | Medium | 4h | P1 |
| 4 | Square bracket conditionals | 3 | 3% | Easy | 2h | P1 |
| 5 | Tuple expansion syntax | 8 | 8% | Medium | 4h | P2 |
| 6 | Curly brace expressions | 1 | 1% | Easy | 1h | P2 |
| 7 | Solve keyword variants & statement-boundary issues | 5 | 5% | Easy | 2h | P1 |
| 8 | Acronym statement | 2 | 2% | Easy | 1h | P2 |
| 9 | Complex set data syntax | 33 | 34% | Hard | 12h+ | P3 |
| 10 | Numeric parameter data | 3 | 3% | Medium | 3h | P2 |
| 11 | Range syntax in data | 2 | 2% | Medium | 3h | P2 |
| 12 | Other/miscellaneous | 10 | 10% | Varies | 4h | P3 |
| **Total** | | **97** | **100%** | | | |

**Note:** Each of the 97 models is assigned to exactly one primary subcategory based on its most significant blocking issue. Counts here represent unique models with no double-counting. Some models have secondary issues that appear in the detailed analysis below, but for summary purposes each model is counted only once in its primary category.

### By Fixability

| Category | Models | % | Notes |
|----------|--------|---|-------|
| Easy (typical 1-2h per pattern) | 29 | 30% | Lexer regex changes, simple grammar additions |
| Medium (typical 2-4h per pattern) | 29 | 30% | Grammar rule extensions, multi-file changes |
| Hard (typical 4h+ per pattern) | 33 | 34% | Complex set data, requires grammar restructuring |
| Unfixable | 6 | 6% | Model-specific edge cases |

**Note:** For this fixability breakdown, each of the 97 models is assigned to exactly one primary fixability category based on its most difficult issue (no overlaps). This matches the subcategory table above where each model is counted once. Effort ranges are typical implementation effort per fix/pattern, not per model.

---

## 2. Detailed Subcategory Analysis

### 2.1 Reserved Word Conflicts (`inf`, `na`) - 12 models

**Models:** ps2_f, ps2_f_eff, ps2_f_s, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps5_s_mn, ps10_s, ps10_s_mn

**Error Pattern:**
```gams
* ps2_f - Error at line 26
   theta(i) 'efficiency' / eff 0.2, inf 0.3 /
Positive Variable,    <-- Parser confused by `inf` as reserved word
```

**Root Cause:** The lexer recognizes `inf` (infinity) and `na` (not available) as reserved words. When these appear as set elements in parameter data, the parser fails on the next statement.

**Fix Approach:**
- Context-aware lexing: In set data context (`/ ... /`), treat `inf`/`na` as identifiers
- Alternative: Quote detection - allow unquoted `inf`/`na` in data

**Files to Modify:**
- `src/gams/gams_lexer.py` (to be created) - Add context state for data sections
- `src/gams/gams_grammar.lark` - Update `set_element` rule

**Effort:** 2h  
**Fixability:** Easy  
**Impact:** 12 models (highest single-fix impact)

---

### 2.2 Display Statement Continuation - 6 models

**Models:** irscge, lrgcge, moncge, quocge, stdcge, twocge

**Error Pattern:**
```gams
* irscge - Error at line 88
display Y0, F0, X0, Z0, Xp0, Xg0, Xv0, E0, M0, Q0, D0, Sp0, Sg0, Td0, Tz0, Tm0
        FF, Sf, tauz, taum;
        ^^ Unexpected character 'F'
```

**Root Cause:** Display statements spanning multiple lines are not being parsed correctly. The continuation line starting with an identifier is not recognized.

**Fix Approach:**
- Extend `display_stmt` grammar rule to handle multi-line identifier lists
- Allow whitespace-only lines followed by identifier continuation

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Update `display_stmt` rule

**Effort:** 2h  
**Fixability:** Easy  
**Impact:** 6 models

---

### 2.3 Multi-line Statement Continuation - 12 models

**Models:** agreste, cesam, fawley, fdesign, gtm, iobalance, mine, nebrazil, otpop, pdi, pindyck, uimp

**Error Pattern:**
```gams
* agreste - Error at line 271
ddev(ty).. sum(c, prdev(c,ty)*sales(c)) =e= pdev(ty) - ndev(ty);
arev..   revenue  =e= lprice*xlive + ...;
^^ Multiple equations on continuation lines
```

**Root Cause:** Multiple statements/equations defined on continuation lines after a semicolon are not properly parsed.

**Fix Approach:**
- Improve semicolon handling in equation blocks
- Better statement boundary detection

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Statement separation rules
- `src/ir/parser.py` - Statement boundary logic

**Effort:** 4h  
**Fixability:** Medium  
**Impact:** ~12 models (some overlap)

---

### 2.4 Square Bracket Conditionals - 3 models

**Models:** clearlak, procmean, springchain

**Error Pattern:**
```gams
* clearlak - Error at line 55
np(n,p)$[mod(ord(n) - 2, card(p)) = ord(p) - 1] = yes;
        ^ Unexpected character '['
```

**Root Cause:** GAMS allows `$[condition]` as alternative to `$(condition)`. Square brackets in conditionals are not supported.

**Fix Approach:**
- Add `"[" condition "]"` as alternative to `"(" condition ")"` in dollar conditionals

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Add square bracket alternative in conditional rules

**Effort:** 2h  
**Fixability:** Easy  
**Impact:** 3 models

---

### 2.5 Tuple Expansion Syntax - 8 models

**Models:** dinam, egypt, indus, marco, paklive, shale, sparta, turkey

**Error Pattern:**
```gams
* indus - Error at line 73
(basmati,irri).(bullock,'semi-mech') 1 1 1 1 1 1
^ Unexpected character '('
```

**Root Cause:** GAMS tuple expansion syntax `(a,b).(c,d)` expands to `a.c, a.d, b.c, b.d`. Not supported in grammar.

**Fix Approach:**
- Add grammar rule for tuple expansion in set/parameter data
- Rule: `"(" id_list ")" "." "(" id_list ")"` or `"(" id_list ")" "." id`

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Add `tuple_expansion` rule
- `src/ir/parser.py` - Handle tuple expansion AST

**Effort:** 4h  
**Fixability:** Medium  
**Impact:** 8 models

---

### 2.6 Curly Brace Expressions - 1 model

**Models:** procmean

**Error Pattern:**
```gams
* procmean - Error at line 46
tcdef.. tc =e= k1*T*betareg(y,alpha,beta) - k1*{(delta + a)*...}
                                               ^ Unexpected character '{'
```

**Root Cause:** GAMS allows curly braces `{}` as alternative grouping to parentheses in some contexts.

**Fix Approach:**
- Add `"{" expr "}"` as alternative to `"(" expr ")"` in expression rules

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Add curly brace alternative

**Effort:** 1h  
**Fixability:** Easy  
**Impact:** 1 model

---

### 2.7 Solve Keyword Variants & Statement-Boundary Issues - 5 models

**Models:** ampl, meanvar, mlbeta, mlgamma, nemhaus

**Error Pattern:**
```gams
* ampl - Error at line 55
Model ampl 'maximum revenue production problem' / all /;
^ Unexpected character 'M' (likely due to preceding unterminated statement, not capitalization)

* mlbeta - Error at line 71
solve m using nlp maximimizing like;
                  ^ 'maximimizing' is a typo for 'maximizing'

* meanvar - Error at line 98
solve ... maximize ...;
          ^ 'maximize' instead of 'maximizing'
```

**Root Cause:** This category includes two related issues:
1. **Spelling variants/typos in solve direction:** `maximimizing` (typo), `maximize` (variant of `maximizing`)
2. **Statement-boundary/unterminated construct issues:** `Model`/`Solve` reported as "unexpected" are likely caused by a missing statement terminator or an unfinished construct before them, not by keyword capitalization (the grammar already treats these keywords case-insensitively via `"Model"i` and `"Solve"i`)

**Fix Approach:**
- Analyze representative failing models (e.g., `mlbeta`, `meanvar`, `ampl`) to see what syntactic pattern makes `Model`/`Solve` "unexpected" (e.g., missing `;`, unterminated equation, stray characters)
- Adjust the grammar or lexer to ensure preceding constructs can terminate cleanly and to emit clearer diagnostics when they do not
- Add recognized spelling variants for solve direction keywords (`maximize`/`minimize` alongside `maximizing`/`minimizing`)
- Keep obvious typos like `maximimizing` as errors but improve the error message to hint at the likely intended keyword

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Refine solve-direction handling and, if needed, adjust statement-boundary rules or error productions to better explain "unexpected `Model`/`Solve`" cases

**Effort:** 2h  
**Fixability:** Easy  
**Impact:** 5 models

---

### 2.8 Acronym Statement - 2 models

**Models:** mathopt4, worst

**Error Pattern:**
```gams
* mathopt4 - Error at line 79
Acronym global;
        ^ Unexpected character 'g'

* worst - Error at line 41
Acronym future, call, puto;
        ^ Unexpected character 'f'
```

**Root Cause:** `Acronym` statement not supported in grammar.

**Fix Approach:**
- Add `acronym_stmt` rule: `"Acronym"i id_list ";"`

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Add `acronym_stmt` rule

**Effort:** 1h  
**Fixability:** Easy  
**Impact:** 2 models

---

### 2.9 Complex Set Data Syntax - 33 models

**Models:** camcge, cesam2, china, dyncge, etamac, feedtray, ferts, ganges, gangesx, gussrisk, harker, hhfair, hhmax, iswnm, korcge, lands, launch, lop, nonsharp, prolog, robustlp, sarf, senstran, ship, solveopt, splcge, tabora, tfordy, tforss, tricp, trnspwl, turkpow, weapons

**Note:** `kand` and `srkandw` have range syntax as their primary blocking issue and are counted under subcategory 2.11 instead.

**Error Patterns:**
1. Quoted set element descriptions: `/ cotton-h 'cotton description' /`
2. Hyphenated identifiers with numbers: `/ 'mode-1' na, 'mode-2' 3 /`
3. Range notation in data: `/ 'time-1'.('n-1'*'n-3') /`
4. Mixed alphanumeric data: `/ route-1 250, route-2 300 /`
5. Multi-dimensional table data with special syntax

**Root Cause:** GAMS has very flexible data syntax that combines identifiers, quotes, numbers, and special notation in ways the current grammar doesn't fully support.

**Fix Approach:**
- Requires significant grammar restructuring
- Need flexible `data_element` rule that handles:
  - Quoted/unquoted identifiers
  - Numeric values
  - Range notation (`*`)
  - Dot notation for tuples

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Major updates to data parsing rules
- `src/gams/gams_lexer.py` (to be created) or Lark setup in `src/ir/parser.py` - Context-aware tokenization

**Effort:** 12h+ (recommend deferring most)  
**Fixability:** Hard  
**Impact:** 33 models (but high effort)

**Recommendation:** Defer to future sprint, focus on simpler subcategories first.

---

### 2.10 Numeric Parameter Data - 3 models

**Models:** apl1pca, lmp2, prodsp2

**Error Pattern:**
```gams
* apl1pca - Error at line 117
h1 = hm1(dl) * v1("out", omega1);
   ^ Unexpected character '='
```

**Root Cause:** Parameter assignment statements outside of explicit Parameter blocks may not be recognized.

**Fix Approach:**
- Improve assignment statement recognition
- Handle implicit parameter assignments

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Assignment statement rules

**Effort:** 3h  
**Fixability:** Medium  
**Impact:** 3 models

---

### 2.11 Range Syntax in Data - 2 models

**Models:** kand, srkandw

**Error Pattern:**
```gams
* kand - Error at line 55
tn(t,n) 'time node mapping' / 'time-1'.('n-1'*'n-3'), 'time-2'.('n-4'*'n-12') /
                                            ^ Unexpected character '*'
```

**Root Cause:** While `range_expr` is already supported in `set_members` (e.g., for ranges in plain set data), these models use range expressions like `'n-1'*'n-3'` inside tuple-expansion lists following `STRING "." "(" ... ")"`, and the current grammar does not allow `range_expr` in that tuple-expansion context.

**Fix Approach:**
- Extend the grammar for tuple-expansion lists (used in constructs like `STRING "." "(" ... ")"`) to allow `range_expr` entries, not just simple elements.

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Update the tuple-expansion/`STRING "." "(" ... ")"` rule(s) to accept `range_expr` within the list

**Effort:** 3h  
**Fixability:** Medium  
**Impact:** 2 models

---

### 2.12 Other/Miscellaneous - 10 models

**Models:** demo1, qdemo7, saras, spatequ, plus 6 additional miscellaneous models

These 10 models have unique issues requiring case-by-case analysis:
- `demo1`: Double-quoted output format strings
- `qdemo7`: Continuation in display statement
- `saras`: Standalone slash in data
- `spatequ`: MCP model syntax with dots
- 6 additional models have miscellaneous issues not fitting other categories

**Clarification:** Each of these 10 models is assigned here as their primary subcategory (no double-counting with other subcategories). Of these 10, 6 may be addressable in Phase 1-2 with targeted fixes; the remaining 4 are deferred to Phase 3.

**Effort:** 4h total  
**Fixability:** Varies  
**Impact:** 10 models

---

## 3. Prioritized Fix Plan

### Phase 1: Quick Wins (12h, +20-22 models)

| # | Fix | Effort | Models | ROI |
|---|-----|--------|--------|-----|
| 1 | Reserved word conflicts (`inf`/`na`) | 2h | 12 | 6.0 |
| 2 | Display statement continuation | 2h | 6 | 3.0 |
| 3 | Solve keyword spelling/case fixes | 2h | 5 | 2.5 |
| 4 | Square bracket conditionals | 2h | 3 | 1.5 |
| 5 | Acronym statement | 1h | 2 | 2.0 |
| 6 | Curly brace expressions | 1h | 1 | 1.0 |
| 7 | Multi-line continuation (partial) | 2h | 3 | 1.5 |
| **Subtotal** | | **12h** | **32** | |

**Note:** The 32 models above is a raw count; some models have multiple issues. After overlap accounting, the actual unique model count is ~20-22.

### Phase 2: Medium Effort (13h, +10-12 models)

| # | Fix | Effort | Models | ROI |
|---|-----|--------|--------|-----|
| 1 | Tuple expansion syntax | 4h | 8 | 2.0 |
| 2 | Quoted set descriptions | 3h | 7 | 2.3 |
| 3 | Numeric parameter data | 3h | 3 | 1.0 |
| 4 | Range syntax in data | 3h | 4 | 1.3 |
| **Subtotal** | | **13h** | **~22** | |

**Note:** After overlap accounting, ~10-12 additional unique models. The 19 models from complex set data that are fixable in Phase 2 (7 quoted descriptions + 8 tuple expansion + 4 range notation) overlap with subcategory 9.

### Phase 3: Deferred (20h+, 18 models)

| Category | Models | Reason for Deferral |
|----------|--------|---------------------|
| Complex set data syntax (hard subset) | 14 | Mixed alphanumeric (8) + multi-dimensional tables (6) |
| Miscellaneous (deferred subset) | 4 | Case-by-case analysis needed |
| **Total** | **18** | |

**Clarification:** 
- Of the 33 models in subcategory 9 (Complex set data syntax), 19 are addressable in Phase 2 (quoted descriptions, tuple expansion, range notation); the remaining 14 are deferred here.
- Of the 10 models in subcategory 12 (Other/Miscellaneous), 6 are addressable in Phase 1-2; the remaining 4 are deferred here.
- The 18 deferred models = 14 (complex set data hard subset) + 4 (misc deferred).
- For subcategory 2.3 (multi-line continuation, 12 models), Phase 1 targets the 3 easiest; the remaining 9 also exhibit secondary issues covered by other subcategories but are still counted under 2.3 as their primary category (no double-counting).

**Recommendation:** Focus Sprint 17 on Phase 1 and Phase 2. Defer hard complex set data patterns to Sprint 18 or later.

### Expected Improvement

| Phase | Cumulative Effort | New Parse Rate | Models Parsing |
|-------|-------------------|----------------|----------------|
| Baseline | 0h | 30.0% | 48 |
| Phase 1 | 12h | 42-44% | 68-70 |
| Phase 1+2 | 25h | 49-51% | 78-82 |
| Full (incl. Phase 3) | 42h+ | 55-60% | 88-96 |

**Sprint 17 Target:** Phase 1 = 12h effort, +20-22 models, ~42-44% parse rate (Phase 2 adds +10-12 more with 13h additional effort)

---

## 4. Grammar/Lexer File Locations

### Primary Files

| File | Purpose | Fixes Applied |
|------|---------|---------------|
| `src/gams/gams_grammar.lark` | Grammar rules | Display, conditionals, acronym, tuple expansion |
| `src/gams/gams_lexer.py` (planned) | Lexer patterns module to be added | Reserved words context, identifier patterns |
| `src/ir/parser.py` | Parser logic | Statement boundaries, AST construction |

### Specific Locations for Each Fix

| Fix | File | Location/Rule |
|-----|------|---------------|
| Reserved words | `src/gams/gams_lexer.py` (planned) | `RESERVED_WORDS`, token context (to be implemented) |
| Display continuation | `src/gams/gams_grammar.lark` | `display_stmt` rule |
| Solve direction / statement boundaries | `src/gams/gams_grammar.lark` | Solve-direction handling, statement-boundary rules |
| Square brackets | `src/gams/gams_grammar.lark` | `dollar_cond` rule |
| Acronym | `src/gams/gams_grammar.lark` | New `acronym_stmt` rule |
| Curly braces | `src/gams/gams_grammar.lark` | `expr` rule alternatives |
| Tuple expansion | `src/gams/gams_grammar.lark` | `set_data`, `param_data` rules |
| Range syntax | `src/gams/gams_grammar.lark` | `set_element_range` rule |

---

## 5. Unknown Verification Summary

### Unknown 3.1: Lexer Error Subcategories

**Status:** ✅ VERIFIED

**Finding:** The 97 lexer_invalid_char errors break down into 12 distinct subcategories:
1. Reserved word conflicts (12 models, 12%)
2. Display statement continuation (6 models, 6%)
3. Multi-line statement continuation (12 models, 12%)
4. Square bracket conditionals (3 models, 3%)
5. Tuple expansion syntax (8 models, 8%)
6. Curly brace expressions (1 model, 1%)
7. Keyword variants & statement-boundary issues (5 models, 5%)
8. Acronym statement (2 models, 2%)
9. Complex set data syntax (33 models, 34%)
10. Numeric parameter data (3 models, 3%)
11. Range syntax in data (2 models, 2%)
12. Other/miscellaneous (10 models, 10%)

**Key Insight:** ~30% of errors are easily fixable (subcategories 1-8), ~5% are medium difficulty (subcategories 10-11), ~34% require significant grammar work (subcategory 9), and ~10% are miscellaneous/edge cases (subcategory 12).

---

### Unknown 3.2: Hyphenated Identifier Fixability

**Status:** ✅ VERIFIED

**Finding:** Most remaining hyphenated identifier issues are part of the "complex set data syntax" category (33 models) and require grammar changes, not just lexer changes.

**Specific Patterns:**
- Number-prefixed hyphenated elements (`1964-i`): Requires lexer pattern extension
- Hyphenated elements with quoted descriptions: Requires grammar rule for `set_element STRING`
- Hyphenated elements in tuple notation: Requires tuple expansion grammar support

**Risk Assessment:**
- Low risk for lexer-only changes (number-prefix patterns)
- Medium risk for grammar changes (may affect existing parsing)
- Recommendation: Test each change against full model suite before committing

**Conclusion:** Some patterns can be fixed with lexer changes (3-5 models), but most require grammar extensions (30+ models).

---

### Unknown 3.4: Complex Set Data Fixability

**Status:** ✅ VERIFIED (Decision: Partial defer)

**Finding:** The 33 models with complex set data syntax errors exhibit these patterns:

| Pattern | Count | Fixability | Decision |
|---------|-------|------------|----------|
| Quoted descriptions | 7 | Medium | Fix in Sprint 17 Phase 2 |
| Tuple expansion | 8 | Medium | Fix in Sprint 17 Phase 2 |
| Range notation | 4 | Medium | Fix in Sprint 17 Phase 2 |
| Mixed alphanumeric | 8 | Hard | Defer |
| Multi-dimensional tables | 6 | Hard | Defer |

**Decision Rationale:**
- ~19 models fixable with targeted grammar extensions (Phase 2)
- ~14 models require comprehensive data syntax overhaul (defer)
- ROI favors fixing simpler patterns first

**Recommendation:** Fix quoted descriptions, tuple expansion, and range notation in Sprint 17. Defer mixed alphanumeric and multi-dimensional table patterns to future sprint.

---

### Unknown 3.5: Parse Target Breakdown

**Status:** ✅ VERIFIED

**Finding:** Achieving 70% parse rate (112 models) breakdown:

| Source | Models | Notes |
|--------|--------|-------|
| Current baseline | 48 | Sprint 16 result |
| Lexer fixes (Phase 1) | +20-22 | Quick wins |
| Lexer fixes (Phase 2) | +10-12 | Medium effort |
| Other parse improvements | +5-10 | Internal errors, etc. |
| **Achievable Total** | **83-92** | **52-58%** |

**Gap Analysis:**
- 70% target = 112 models
- Achievable with current plan = 83-92 models (52-58%)
- Gap = 20-29 models

**Conclusion:** 70% parse rate is **optimistic** with current approach. More realistic targets:
- **Conservative:** 52% (83 models) with Phase 1 + Phase 2
- **Stretch:** 58% (92 models) with Phase 1 + Phase 2 + internal error fixes
- **70% requires:** Complex set data overhaul (Phase 3) + additional work

**Recommendation:** Revise Sprint 17 parse target to 55% (88 models), which is achievable with Phase 1 + Phase 2 + some internal error fixes.

---

## Appendix A: Model Lists by Subcategory

### A.1 Reserved Word Conflicts (12 models)
ps10_s, ps10_s_mn, ps2_f, ps2_f_eff, ps2_f_s, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps5_s_mn

### A.2 Display Statement Continuation (6 models)
irscge, lrgcge, moncge, quocge, stdcge, twocge

### A.3 Multi-line Statement Continuation (12 models)
agreste, cesam, fawley, fdesign, gtm, iobalance, mine, nebrazil, otpop, pdi, pindyck, uimp

### A.4 Square Bracket Conditionals (3 models)
clearlak, procmean, springchain

### A.5 Tuple Expansion Syntax (8 models)
dinam, egypt, indus, marco, paklive, shale, sparta, turkey

### A.6 Curly Brace Expressions (1 model)
procmean

### A.7 Solve Keyword Spelling/Case Issues (5 models)
ampl, meanvar, mlbeta, mlgamma, nemhaus

### A.8 Acronym Statement (2 models)
mathopt4, worst

### A.9 Complex Set Data Syntax (33 models)
camcge, cesam2, china, dyncge, etamac, feedtray, ferts, ganges, gangesx, gussrisk, harker, hhfair, hhmax, iswnm, korcge, lands, launch, lop, nonsharp, prolog, robustlp, sarf, senstran, ship, solveopt, splcge, tabora, tfordy, tforss, tricp, trnspwl, turkpow, weapons

### A.10 Numeric Parameter Data (3 models)
apl1pca, lmp2, prodsp2

### A.11 Range Syntax in Data (2 models)
kand, srkandw

### A.12 Other/Miscellaneous (10 models)
demo1, qdemo7, saras, spatequ, plus 6 additional miscellaneous models

---

## Appendix B: Effort Estimation Methodology

### Estimation Approach
- **Easy (1-2h):** Single-rule grammar change or lexer pattern update
- **Medium (2-4h):** Multiple rule changes, requires testing across model suite
- **Hard (4h+):** Grammar restructuring, significant logic changes

### Risk Factors
- Grammar changes may cause regressions in currently-parsing models
- Lexer context changes require careful state management
- Some fixes may reveal secondary issues in affected models

### Testing Strategy
1. Create test cases for each subcategory before implementing fixes
2. Run full parse suite after each change
3. Track regression rate (target: 0 regressions)
