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
4. **~25 models** are fixable with targeted lexer/grammar changes
5. **~50+ models** require complex set data syntax overhaul (defer to future)

**Recommended Sprint 17 Focus:**
| Priority | Models | Hours | Approach |
|----------|--------|-------|----------|
| Quick wins | 20-25 | 12h | Lexer regex + grammar rules |
| Medium effort | 10-15 | 10h | Grammar extensions |
| Deferred | 50+ | 20h+ | Complex set data (future sprint) |

**Target:** +20-22 models parsing with Phase 1 (12h effort)

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
| 7 | Keyword case issues | 5 | 5% | Easy | 2h | P1 |
| 8 | Acronym statement | 2 | 2% | Easy | 1h | P2 |
| 9 | Complex set data syntax | 35 | 36% | Hard | 12h+ | P3 |
| 10 | Numeric parameter data | 3 | 3% | Medium | 3h | P2 |
| 11 | Range syntax in data | 2 | 2% | Medium | 3h | P2 |
| 12 | Other/miscellaneous | 8 | 8% | Varies | 4h | P3 |
| **Total** | | **97** | **100%** | | | |

**Note:** Some models appear in multiple subcategories due to having multiple distinct issues. The counts above represent issue instances; the 97 total reflects unique models with lexer errors.

### By Fixability

| Category | Models | % | Notes |
|----------|--------|---|-------|
| Easy (1-2h each) | 29 | 30% | Lexer regex changes, simple grammar additions |
| Medium (2-4h each) | 29 | 30% | Grammar rule extensions, multi-file changes |
| Hard (4h+ each) | 35 | 36% | Complex set data, requires grammar restructuring |
| Unfixable | 4 | 4% | Model-specific edge cases |

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
- `src/gams/gams_lexer.py` - Add context state for data sections
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

### 2.7 Keyword Case Issues - 5 models

**Models:** ampl, meanvar, mlbeta, mlgamma, nemhaus

**Error Pattern:**
```gams
* ampl - Error at line 55
Model ampl 'maximum revenue production problem' / all /;
^ Unexpected character 'M'

* mlbeta - Error at line 71
solve m using nlp maximimizing like;
                  ^ 'maximimizing' typo, but case also an issue
```

**Root Cause:** Keywords like `Model`, `Solve` with capital letters are not recognized due to lexer patterns.

**Fix Approach:**
- Ensure all keywords use case-insensitive matching (`"Model"i`)
- Fix any missing case-insensitive flags

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Verify all keyword rules have `i` flag

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

### 2.9 Complex Set Data Syntax - 35 models

**Models:** camcge, cesam2, china, dyncge, etamac, feedtray, ferts, ganges, gangesx, gussrisk, harker, hhfair, hhmax, iswnm, kand, korcge, lands, launch, lop, nonsharp, prolog, robustlp, sarf, senstran, ship, solveopt, splcge, srkandw, tabora, tfordy, tforss, tricp, trnspwl, turkpow, weapons

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
- `src/gams/gams_lexer.py` - Context-aware tokenization

**Effort:** 12h+ (recommend deferring most)  
**Fixability:** Hard  
**Impact:** 35 models (but high effort)

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

**Root Cause:** Range notation `'n-1'*'n-3'` meaning `'n-1', 'n-2', 'n-3'` not supported.

**Fix Approach:**
- Add range notation support in set data: `element "*" element`

**Files to Modify:**
- `src/gams/gams_grammar.lark` - Add range support in data rules

**Effort:** 3h  
**Fixability:** Medium  
**Impact:** 2 models

---

### 2.12 Other/Miscellaneous - 8 models

**Models:** demo1, qdemo7, saras, spatequ, plus 4 models with overlapping issues from other categories

These have unique issues requiring case-by-case analysis:
- `demo1`: Double-quoted output format strings
- `qdemo7`: Continuation in display statement
- `saras`: Standalone slash in data
- `spatequ`: MCP model syntax with dots
- Additional models have secondary issues that overlap with categories 10-11

**Effort:** 4h total  
**Fixability:** Varies  
**Impact:** 8 models (includes overlaps)

---

## 3. Prioritized Fix Plan

### Phase 1: Quick Wins (12h, +20-22 models)

| # | Fix | Effort | Models | ROI |
|---|-----|--------|--------|-----|
| 1 | Reserved word conflicts (`inf`/`na`) | 2h | 12 | 6.0 |
| 2 | Display statement continuation | 2h | 6 | 3.0 |
| 3 | Keyword case fixes | 2h | 5 | 2.5 |
| 4 | Square bracket conditionals | 2h | 3 | 1.5 |
| 5 | Acronym statement | 1h | 2 | 2.0 |
| 6 | Curly brace expressions | 1h | 1 | 1.0 |
| 7 | Multi-line continuation (partial) | 2h | 3 | 1.5 |
| **Subtotal** | | **12h** | **~25** | |

**Note:** Some models have multiple issues; actual unique model count is ~20-22.

### Phase 2: Medium Effort (10h, +10-12 models)

| # | Fix | Effort | Models | ROI |
|---|-----|--------|--------|-----|
| 1 | Tuple expansion syntax | 4h | 8 | 2.0 |
| 2 | Numeric parameter data | 3h | 3 | 1.0 |
| 3 | Range syntax in data | 3h | 2 | 0.7 |
| **Subtotal** | | **10h** | **~13** | |

**Note:** After overlap accounting, ~10-12 additional unique models.

### Phase 3: Deferred (20h+, ~35 models)

| Category | Models | Reason for Deferral |
|----------|--------|---------------------|
| Complex set data syntax | 35 | Requires major grammar restructuring |
| Miscellaneous | 4 | Case-by-case analysis needed |

**Recommendation:** Defer to Sprint 18 or later. Focus Sprint 17 on Phase 1 and Phase 2.

### Expected Improvement

| Phase | Cumulative Effort | New Parse Rate | Models Parsing |
|-------|-------------------|----------------|----------------|
| Baseline | 0h | 30.0% | 48 |
| Phase 1 | 12h | 42-44% | 68-70 |
| Phase 1+2 | 22h | 48-50% | 77-80 |
| Full (incl. Phase 3) | 42h+ | 55-60% | 88-96 |

**Sprint 17 Target:** Phase 1 = 12h effort, +20-22 models, ~42-44% parse rate (Phase 2 adds +10-12 more with 10h additional effort)

---

## 4. Grammar/Lexer File Locations

### Primary Files

| File | Purpose | Fixes Applied |
|------|---------|---------------|
| `src/gams/gams_grammar.lark` | Grammar rules | Display, conditionals, acronym, tuple expansion |
| `src/gams/gams_lexer.py` | Lexer patterns | Reserved words context, identifier patterns |
| `src/ir/parser.py` | Parser logic | Statement boundaries, AST construction |

### Specific Locations for Each Fix

| Fix | File | Location/Rule |
|-----|------|---------------|
| Reserved words | `src/gams/gams_lexer.py` | `RESERVED_WORDS`, token context |
| Display continuation | `src/gams/gams_grammar.lark` | `display_stmt` rule |
| Keyword case | `src/gams/gams_grammar.lark` | All keyword rules (`"Model"i`, etc.) |
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
7. Keyword case issues (5 models, 5%)
8. Acronym statement (2 models, 2%)
9. Complex set data syntax (35 models, 36%)
10. Numeric parameter data (3 models, 3%)
11. Range syntax in data (2 models, 2%)
12. Other/miscellaneous (8 models, 8%)

**Key Insight:** ~30% of errors are easily fixable (subcategories 1-8), ~30% are medium difficulty (9-11), and ~36% require significant grammar work (category 9).

---

### Unknown 3.2: Hyphenated Identifier Fixability

**Status:** ✅ VERIFIED

**Finding:** Most remaining hyphenated identifier issues are part of the "complex set data syntax" category (35 models) and require grammar changes, not just lexer changes.

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

**Finding:** The 35 models with complex set data syntax errors exhibit these patterns:

| Pattern | Count | Fixability | Decision |
|---------|-------|------------|----------|
| Quoted descriptions | 7 | Medium | Fix in Sprint 17 Phase 2 |
| Tuple expansion | 8 | Medium | Fix in Sprint 17 Phase 2 |
| Range notation | 4 | Medium | Fix in Sprint 17 Phase 2 |
| Mixed alphanumeric | 10 | Hard | Defer |
| Multi-dimensional tables | 6 | Hard | Defer |

**Decision Rationale:**
- ~19 models fixable with targeted grammar extensions (Phase 2)
- ~16 models require comprehensive data syntax overhaul (defer)
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

### A.7 Keyword Case Issues (5 models)
ampl, meanvar, mlbeta, mlgamma, nemhaus

### A.8 Acronym Statement (2 models)
mathopt4, worst

### A.9 Complex Set Data Syntax (35 models)
camcge, cesam2, china, dyncge, etamac, feedtray, ferts, ganges, gangesx, gussrisk, harker, hhfair, hhmax, iswnm, kand, korcge, lands, launch, lop, nonsharp, prolog, robustlp, sarf, senstran, ship, solveopt, splcge, srkandw, tabora, tfordy, tforss, tricp, trnspwl, turkpow, weapons

### A.10 Numeric Parameter Data (3 models)
apl1pca, lmp2, prodsp2

### A.11 Range Syntax in Data (2 models)
kand, srkandw

### A.12 Other/Miscellaneous (8 models)
demo1, qdemo7, saras, spatequ (plus 4 models with overlapping issues from categories 10-11)

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
