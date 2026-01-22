# Sprint 16 Improvement Roadmap

**Created:** January 22, 2026
**Purpose:** Prioritized list of improvements for Sprint 16 parser and solve stages
**Methodology:** Priority Score = Models Affected / Effort (in days)

---

## Executive Summary

This roadmap identifies and prioritizes improvements to the nlp2mcp pipeline based on the detailed gap analysis from LEXER_ERROR_ANALYSIS.md, PATH_ERROR_ANALYSIS.md, and baseline_metrics.json.

**Key Finding:** Dollar control handling is already implemented. The primary blockers are:
1. **Parse stage:** GAMS data syntax features (hyphenated elements, tuple expansion, keyword case)
2. **Solve stage:** MCP code generation bugs in emit_gams.py (unary minus, quoting)

**Sprint 16 Focus:**
- Priority 1 (High Confidence): +15 parse models through 3 targeted grammar fixes, +14 solve models through 3 emit_gams.py fixes
- Priority 2 (Medium Confidence): +19 parse models through 2 additional grammar fixes
- Total potential: +34 parse models + 14 solve models (note: some model overlaps exist between subcategories)

---

## Priority 1: High Confidence Improvements

These fixes have clear patterns, well-defined solutions, and high confidence of success.

### Parse Stage Fixes

| ID | Fix | Models | Effort | Score | Confidence | Status |
|----|-----|--------|--------|-------|------------|--------|
| P-1 | Keyword case (`Free Variable`, `Model`) | 9 | 0.5d | 18.0 | High | Planned |
| P-2 | Hyphenated set elements (number-start like `1964-i`) | 3 | 0.5d | 6.0 | High | Planned |
| P-3 | Abort statement syntax (`abort$(...) msg, var`) | 3 | 0.5d | 6.0 | High | Planned |

**Subtotal:** 15 models, 1.5 days

#### P-1: Keyword Case Handling

**Problem:** GAMS is case-insensitive, but combined keywords like `Free Variable` fail because the lexer sees `Free` followed by unexpected `Variable`.

**Affected Models (9):** ampl, apl1p, apl1pca, jobt, moncge, nemhaus, qfilter, wall, worst

**Example Error:**
```gams
* apl1p: char 'V' at line 43
Free Variable tcost 'total cost';
```

**Fix Strategy:**
```lark
// Add combined keyword rules
free_var_decl: "Free"i "Variable"i var_list
positive_var_decl: "Positive"i "Variable"i var_list
negative_var_decl: "Negative"i "Variable"i var_list
```

**Effort:** 0.5 days (4 hours)
- Grammar change: 2 hours
- Testing: 2 hours

---

#### P-2: Hyphenated Set Elements (Number-Start)

**Problem:** Set elements starting with numbers followed by hyphens (e.g., `1964-i`, `89-07`) are not recognized.

**Affected Models (3):** abel, ajax, immun

**Example Error:**
```gams
* abel: char '-' at line 18
k 'horizon' / 1964-i, 1964-ii, 1964-iii, 1964-iv /
```

**Fix Strategy:**
```lark
// Current pattern
SET_ELEMENT_ID: /[a-zA-Z_][a-zA-Z0-9_+\-]*/

// Enhanced pattern to allow number start
SET_ELEMENT_ID: /[a-zA-Z0-9_][a-zA-Z0-9_+\-]*/
```

**Effort:** 0.5 days (4 hours)
- Pattern change: 1 hour
- Disambiguation testing: 3 hours (ensure no conflicts with numeric literals)

---

#### P-3: Abort Statement Syntax

**Problem:** Complex abort statements with dollar conditions and display lists are not fully supported.

**Affected Models (3):** cclinpts, imsl, trigx

**Example Error:**
```gams
* cclinpts: char ',' at line 39
abort$(b0 < 0) 'b0 should be positive', b0;
```

**Fix Strategy:**
```lark
// Current (incomplete)
abort_stmt: "abort"i condition? STRING?

// Enhanced
abort_stmt: "abort"i condition? (STRING ("," display_item)*)? ";"
display_item: ID | expression
```

**Effort:** 0.5 days (4 hours)
- Grammar change: 2 hours
- Testing with all 3 models: 2 hours

---

### Solve Stage Fixes

| ID | Fix | Models | Effort | Score | Confidence | Status |
|----|-----|--------|--------|-------|------------|--------|
| S-1 | Unary minus formatting | 10 | 0.5d | 20.0 | High | Planned |
| S-2 | Set element quoting consistency | 3 | 0.5d | 6.0 | High | Planned |
| S-3 | Scalar declaration fix | 1 | 0.25d | 4.0 | High | Planned |

**Subtotal:** 14 models, 1.25 days (all solve failures)

#### S-1: Unary Minus Formatting

**Problem:** `emit_gams.py` generates `-(expr)` which GAMS rejects. Should be `(-1)*(expr)`.

**Affected Models (10):** himmel11, house, least, mathopt1, mathopt2, mhw4d, mhw4dx, process, rbrock, sample

**GAMS Error 445:** "Operand expected after - operator"

**Fix Strategy:**
```python
# In emit_gams.py, change:
def emit_unary_minus(expr):
    return f"-({emit_expr(expr)})"

# To:
def emit_unary_minus(expr):
    return f"((-1)*({emit_expr(expr)}))"
```

**Effort:** 0.5 days (4 hours)
- Code change: 1 hour
- Testing: 3 hours

---

#### S-2: Set Element Quoting Consistency

**Problem:** Generated MCP files have inconsistent quoting of set elements, causing GAMS errors 171/340.

**Affected Models (3):** chem, dispatch, port

**Fix Strategy:**
- Ensure all set elements with special characters are quoted
- Use consistent quoting style throughout emit_gams.py

**Effort:** 0.5 days (4 hours)

---

#### S-3: Scalar Declaration Fix

**Problem:** Missing identifier name in scalar declarations.

**Affected Model (1):** dispatch

**Fix Strategy:** Minor fix in scalar emission code.

**Effort:** 0.25 days (2 hours)

---

## Priority 2: Medium Confidence Improvements

These fixes have clear patterns but require more complex grammar changes.

| ID | Fix | Models | Effort | Score | Confidence | Status |
|----|-----|--------|--------|-------|------------|--------|
| P-4 | Tuple expansion syntax `(a,b).c` | 12 | 1.5d | 8.0 | Medium | Planned |
| P-5 | Quoted set descriptions | 7 | 1d | 7.0 | Medium | Planned |

**Subtotal:** 19 models, 2.5 days

#### P-4: Tuple Expansion Syntax

**Problem:** GAMS supports tuple expansion in set data like `(a,b).c` which expands to `a.c, b.c`.

**Affected Models (12):** aircraft, airsp, clearlak, mine, pdi, pinene, pollut, qsambal, ramsey, srcpm, synheat, turkey

**Example Error:**
```gams
* aircraft: char '(' at line 54
k(j) 'revenue lost' / (route-1,route-2) 13, (route-3,route-4) 8 /
```

**Fix Strategy:**
```lark
// Add tuple expansion rule
tuple_expansion: "(" id_list ")" ("." ID)?
id_list: ID ("," ID)*

// Update set_data to include tuple_expansion
set_data: "{" set_element+ "}" | "/" set_element+ "/"
set_element: (ID | tuple_expansion) (STRING)? (NUMBER)?
```

**Effort:** 1.5 days (12 hours)
- Grammar design: 4 hours
- Implementation: 4 hours
- Testing: 4 hours

**Medium Confidence Reason:** Tuple expansion interacts with other data syntax; may have edge cases.

---

#### P-5: Quoted Set Descriptions

**Problem:** Set elements with inline quoted descriptions after hyphenated identifiers fail.

**Affected Models (7):** agreste, camcge, egypt, fawley, korcge, nebrazil, srcpm

**Example Error:**
```gams
* agreste: char ''' at line 17
c 'crops' / cotton-h 'cotton-herbaceo', corn-g 'corn grain' /
```

**Fix Strategy:**
```lark
// Extend set_member rule to allow quoted descriptions
set_member: SET_ELEMENT_ID (STRING)?
```

**Effort:** 1 day (8 hours)
- Grammar change: 3 hours
- Handling interaction with hyphenated elements: 3 hours
- Testing: 2 hours

**Medium Confidence Reason:** Combines with P-2 fix; may need coordinated implementation.

---

## Priority 3: Lower Priority / Deferred

### Parse Stage (Defer Investigation)

| ID | Fix | Models | Reason for Deferral |
|----|-----|--------|---------------------|
| P-6 | Numeric context in param data | 11 | Complex disambiguation, overlaps with P-4 |
| P-7 | Operator context issues | 9 | Requires case-by-case analysis |
| P-8 | Dot notation variations | 5 | Low impact, complex |
| P-9 | Complex set data (other) | 91 | High effort, needs grammar restructuring |

### Translation Stage (Sprint 17)

| ID | Fix | Models | Reason for Deferral |
|----|-----|--------|---------------------|
| T-1 | `model_no_objective_def` | 5 | Requires feasibility reformulation design |
| T-2 | `diff_unsupported_func` | 5 | Requires new derivative rules (gamma, etc.) |
| T-3 | `unsup_index_offset` | 3 | Requires domain arithmetic analysis |
| T-4 | `model_domain_mismatch` | 2 | Requires improved domain propagation |
| T-5 | `unsup_dollar_cond` | 1 | Requires conditional expression handling |
| T-6 | `codegen_numerical_error` | 1 | Edge case, low priority |

**Sprint 17 Deferral Rationale:**
1. Parse improvements in Sprint 16 will change which models reach translation
2. Parse improvements unblock 109+ models vs. translation fixes affecting 17 models
3. Some translation issues may resolve with better parsing
4. Sprint 16 scope already includes reporting + parse + solve improvements

---

## Implementation Schedule

### Sprint 16 Days 6-7: Parser Implementation

| Day | Tasks | Expected Outcome |
|-----|-------|------------------|
| Day 6 AM | P-1: Keyword case handling | +9 models |
| Day 6 PM | P-2: Hyphenated elements, P-3: Abort syntax | +6 models |
| Day 7 AM | P-4: Tuple expansion (start) | In progress |
| Day 7 PM | P-4: Tuple expansion (complete), P-5: Quoted descriptions | +19 models |

### Sprint 16 Day 8: Solve Improvements

| Day | Tasks | Expected Outcome |
|-----|-------|------------------|
| Day 8 AM | S-1: Unary minus formatting | +10 solve successes |
| Day 8 PM | S-2: Set element quoting, S-3: Scalar fix | +4 solve successes |

---

## Success Metrics

### Expected Outcomes by Priority Level

| Level | Parse Rate | Parse Improvement | Solve Rate | Full Pipeline |
|-------|------------|-------------------|------------|---------------|
| **P1 Only (Min)** | 31% (49/160) | +15 models | 76% (13/17) | 5% (8/160) |
| **P1 + P2 (Target)** | 43% (68/160) | +34 models | 100% (17/17) | 8% (13/160) |
| **All Sprint 16** | 47% (75/160) | +41 models | 100% | 10% (16/160) |

### Regression Safeguards

1. **Before each change:** Verify all 34 baseline-passing models still parse
2. **After each change:** Run `make test` and `make typecheck`
3. **End of day:** Full GAMSLIB integration test

---

## References

- `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` - Detailed parse error analysis
- `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` - Solve error analysis
- `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md` - Sprint 15 baseline
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Unknowns 7.1, 7.2 for methodology
- `docs/testing/FAILURE_ANALYSIS.md` - Generated failure report

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-22 | Initial roadmap created based on Day 4 gap analysis |

---

*Roadmap created as part of Sprint 16 Day 4: Parse and Translate Gap Analysis*
