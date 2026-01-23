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

**Problem:** `expr_to_gams.py` generates `-(expr)` at equation start which GAMS rejects as two operators in a row (`..` then `-`).

**Affected Models (10):** himmel11, house, least, mathopt1, mathopt2, mhw4d, mhw4dx, process, rbrock, sample

**GAMS Error 445:** "More than one operator in a row"

**Actual Error Example (from house_mcp.gms):**
```gams
* Current output (FAILS):
stat_x.. ... + -(y * -1) * lam_minp + ...
stat_y.. ... + -(b - x) * lam_minp + ...

* Should be:
stat_x.. ... + ((-1) * (y * -1)) * lam_minp + ...
stat_y.. ... + ((-1) * (b - x)) * lam_minp + ...
```

**Root Cause Location:** `src/emit/expr_to_gams.py` lines 185-197

The `Unary` case handling adds parentheses when there's a parent operator, but the issue occurs at equation definition start where the unary minus follows `..` which GAMS treats as an operator context.

**Fix Strategy:**
```python
# In expr_to_gams.py, Unary case:
case Unary(op, child):
    child_str = expr_to_gams(child, parent_op=op)
    if isinstance(child, Binary):
        child_str = f"({child_str})"
    # ALWAYS wrap unary minus as multiplication to avoid GAMS error 445
    if op == "-":
        return f"((-1) * {child_str})"
    return f"{op}{child_str}"
```

**Effort:** 0.5 days (4 hours)
- Code change in expr_to_gams.py: 1 hour
- Update golden files: 1 hour
- Testing with all 10 affected models: 2 hours

---

#### S-2: Set Element Quoting Consistency

**Problem:** Generated MCP files have inconsistent quoting of set elements. Single-letter elements are unquoted while multi-character elements with digits are quoted.

**Affected Models (3):** chem, dispatch, port

**GAMS Errors:** 171 (Domain violation), 340 (Label/element name conflict)

**Actual Error Example (from chem_mcp.gms):**
```gams
* Current output (INCONSISTENT):
comp_lo_x_H.. x(H) - 0.001 =G= 0;           * unquoted
comp_lo_x_H2.. x("H2") - 0.001 =G= 0;       * quoted
...
stat_x(c).. ... + sum(i, a(c,c) * nu_cdef(i)) ...  * should be a(i,c)

* Model statement also inconsistent:
comp_lo_x_H.piL_x("H"),    * quoted
comp_lo_x_N.piL_x("N"),    * quoted but x(N) above was unquoted
```

**Root Cause Location:** `src/emit/expr_to_gams.py` function `_quote_indices()` (lines 62-94)

The heuristic quotes identifiers containing digits but leaves single letters unquoted. GAMS requires consistent quoting.

**Fix Strategy:**
```python
# In expr_to_gams.py, change _quote_indices to always quote set elements:
def _quote_indices(indices: tuple[str, ...]) -> list[str]:
    """Quote all element labels in index tuples for GAMS syntax."""
    return [f'"{idx}"' for idx in indices]
```

Also fix in `src/emit/model.py` function `_format_variable_with_indices()` (lines 32-56) to always quote consistently.

**Note:** GAMS supports both single and double quotes for set elements. The key issue is consistency - currently some elements are quoted (`x("H2")`) while others are not (`x(H)`). The fix will quote ALL set element references using double quotes to match GAMS conventions and ensure consistent parsing.

**Effort:** 0.5 days (4 hours)
- Code change in expr_to_gams.py: 1 hour
- Code change in model.py: 0.5 hours
- Update golden files: 0.5 hours
- Testing with chem, dispatch, port: 2 hours

---

#### S-3: Scalar Declaration Fix

**Problem:** Scalars with descriptions but no identifier names are emitted incorrectly.

**Affected Model (1):** dispatch

**GAMS Errors:** 409 (Unrecognizable item), 191 (Closing quote missing)

**Actual Error Example (from dispatch_mcp.gms):**
```gams
* Current output (FAILS):
Scalars
    b00 /0.0/
    'loss equation constant' /0.040357/     * ERROR: no identifier!
    demand /0.0/
    'total power demand in MW' /210.0/      * ERROR: no identifier!
    trace /0.0/
;

* Should be (option 1 - skip description-only scalars):
Scalars
    b00 /0.0/
    demand /0.0/
    trace /0.0/
;

* Or (option 2 - generate synthetic names):
Scalars
    b00 /0.0/
    loss_eq_const 'loss equation constant' /0.040357/
    demand /0.0/
    power_demand 'total power demand in MW' /210.0/
    trace /0.0/
;
```

**Root Cause Location:** `src/emit/original_symbols.py` function `emit_original_parameters()` (lines 79-158)

The IR is storing description strings as scalar names when parsing GAMS files with description-only declarations. This is a parse/IR issue, not just emit.

**Fix Strategy (Option 1 - Filter):**
```python
# In original_symbols.py, emit_original_parameters():
# Skip scalars whose names look like descriptions (contain spaces or quotes)
if " " in scalar_name or "'" in scalar_name:
    continue  # Skip description-only entries
```

**Effort:** 0.25 days (2 hours)
- Diagnose exact IR issue: 0.5 hours
- Code fix: 0.5 hours
- Testing with dispatch: 1 hour

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

## Detailed Implementation Task List (Days 6-8)

### Day 6: Priority 1 Parser Fixes

#### Morning (4 hours): P-1 Keyword Case Handling

| Task | File | Description | Est. |
|------|------|-------------|------|
| 6.1.1 | `src/gams/gams_grammar.lark` | Add `free_var_decl`, `positive_var_decl`, `negative_var_decl` rules | 1h |
| 6.1.2 | `src/gams/gams_grammar.lark` | Ensure case-insensitive matching with `"Free"i` syntax | 0.5h |
| 6.1.3 | `tests/gams/test_keywords.py` | Add tests for `Free Variable`, `Positive Variable` | 1h |
| 6.1.4 | - | Run against 9 affected models: ampl, apl1p, apl1pca, jobt, moncge, nemhaus, qfilter, wall, worst | 1h |
| 6.1.5 | - | Run `make test` and `make typecheck` | 0.5h |

#### Afternoon (4 hours): P-2 and P-3

| Task | File | Description | Est. |
|------|------|-------------|------|
| 6.2.1 | `src/gams/gams_grammar.lark` | Enhance `SET_ELEMENT_ID` to allow number-start: `/[a-zA-Z0-9_][a-zA-Z0-9_+\-]*/` | 0.5h |
| 6.2.2 | `tests/gams/test_set_elements.py` | Add tests for `1964-i`, `89-07` style elements | 0.5h |
| 6.2.3 | - | Verify no conflicts with numeric literals (disambiguation testing) | 1h |
| 6.2.4 | - | Run against 3 models: abel, ajax, immun | 0.5h |
| 6.3.1 | `src/gams/gams_grammar.lark` | Enhance `abort_stmt` to support `abort$(cond) 'msg', var;` | 1h |
| 6.3.2 | `tests/gams/test_abort.py` | Add tests for dollar-conditioned abort with display list | 0.5h |
| 6.3.3 | - | Run against 3 models: cclinpts, imsl, trigx | 0.5h |
| 6.3.4 | - | Full test suite: `make test && make typecheck` | 0.5h |

**Day 6 Checkpoint:** +15 parse models expected

---

### Day 7: Priority 2 Parser Fixes

#### Morning (4 hours): P-4 Tuple Expansion (Part 1)

| Task | File | Description | Est. |
|------|------|-------------|------|
| 7.1.1 | `src/gams/gams_grammar.lark` | Design `tuple_expansion` grammar rule | 1h |
| 7.1.2 | `src/gams/gams_grammar.lark` | Integrate with `set_data` and `param_data` rules | 1h |
| 7.1.3 | `src/ir/parser.py` | Handle `tuple_expansion` AST transformation | 1h |
| 7.1.4 | `tests/gams/test_tuple_expansion.py` | Add tests for `(a,b).c` expansion | 1h |

#### Afternoon (4 hours): P-4 Complete + P-5

| Task | File | Description | Est. |
|------|------|-------------|------|
| 7.2.1 | - | Run tuple expansion against 12 models: aircraft, airsp, clearlak, mine, pdi, pinene, pollut, qsambal, ramsey, srcpm, synheat, turkey | 1h |
| 7.2.2 | - | Debug and fix edge cases | 1h |
| 7.3.1 | `src/gams/gams_grammar.lark` | Extend `set_member` to allow quoted descriptions: `SET_ELEMENT_ID (STRING)?` | 0.5h |
| 7.3.2 | - | Ensure interaction with P-2 (hyphenated elements) works | 0.5h |
| 7.3.3 | - | Run against 7 models: agreste, camcge, egypt, fawley, korcge, nebrazil, srcpm | 0.5h |
| 7.3.4 | - | Full test suite and GAMSLIB integration test | 0.5h |

**Day 7 Checkpoint:** +19 additional parse models expected (total +34)

---

### Day 8: Solve Stage Fixes

#### Morning (4 hours): S-1 Unary Minus Formatting

| Task | File | Description | Est. |
|------|------|-------------|------|
| 8.1.1 | `src/emit/expr_to_gams.py` | Modify `Unary` case to always emit `((-1) * expr)` for minus | 0.5h |
| 8.1.2 | `tests/emit/test_expr_to_gams.py` | Add/update tests for unary minus handling | 0.5h |
| 8.1.3 | `tests/golden/*.gms` | Update golden files with new unary minus format | 0.5h |
| 8.1.4 | - | Regenerate MCP files for 10 affected models | 0.5h |
| 8.1.5 | - | Compile each with `gams model.gms action=c` to verify no Error 445 | 1h |
| 8.1.6 | - | Run full solve on 10 models, capture results | 1h |

#### Afternoon (4 hours): S-2 and S-3

| Task | File | Description | Est. |
|------|------|-------------|------|
| 8.2.1 | `src/emit/expr_to_gams.py` | Modify `_quote_indices` to always quote with double quotes | 0.5h |
| 8.2.2 | `src/emit/model.py` | Update `_format_variable_with_indices` for consistent quoting | 0.5h |
| 8.2.3 | `tests/emit/test_*.py` | Update emit tests for new quoting style | 0.5h |
| 8.2.4 | - | Regenerate and test chem, dispatch, port | 0.5h |
| 8.3.1 | `src/emit/original_symbols.py` | Filter out description-only scalars in `emit_original_parameters` | 0.5h |
| 8.3.2 | - | Test with dispatch model | 0.5h |
| 8.3.3 | - | Full test suite: `make test && make typecheck` | 0.5h |
| 8.3.4 | - | Full GAMSLIB integration test, update metrics | 0.5h |

**Day 8 Checkpoint:** Up to +14 additional solve successes expected (projected 13-14/17 models solving; actual gain depends on overlap across S-1, S-2, and S-3)

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

## Phase 3 Implementation Dependencies

### Parser Dependencies (Days 6-7)

| File | Purpose | Verified |
|------|---------|----------|
| `src/gams/gams_grammar.lark` | Main GAMS grammar (604 lines) | ✓ |
| `src/ir/parser.py` | AST transformation and parsing | ✓ |
| `tests/gams/` | Grammar test suite | Pending |

**Key Grammar Observations:**
1. `var_kind` already handles `POSITIVE_K`, `NEGATIVE_K`, `BINARY_K`, `INTEGER_K` but not space-separated variants like `Free Variable`
2. `SET_ELEMENT_ID` pattern: `/[a-zA-Z_][a-zA-Z0-9_+\-]*/` - needs extension to allow number-start
3. `abort_stmt` supports `abort$`, `abort$ STRING` but not `abort$(cond) msg, var;` format
4. Grammar has `desc_text` and `DESC_TEXT` handling for inline descriptions

### Emit Dependencies (Day 8)

| File | Purpose | Lines | Key Functions |
|------|---------|-------|---------------|
| `src/emit/expr_to_gams.py` | Expression → GAMS syntax | 260 | `expr_to_gams()`, `_quote_indices()` |
| `src/emit/model.py` | MCP model emission | 216 | `emit_model_mcp()`, `_format_variable_with_indices()` |
| `src/emit/original_symbols.py` | Sets/Params/Scalars emission | 158 | `emit_original_parameters()` |
| `src/emit/emit_gams.py` | Main orchestrator | 184 | `emit_gams_mcp()` |
| `src/emit/templates.py` | Variables/Equations blocks | 278 | `emit_variables()`, `emit_equations()` |
| `src/emit/equations.py` | Equation definitions | 154 | `emit_equation_definitions()` |

**Key Emit Observations:**
1. `expr_to_gams.py:185-197` - `Unary` case needs `((-1) * expr)` rewrite for unary minus
2. `expr_to_gams.py:62-94` - `_quote_indices()` heuristic uses digit detection; needs always-quote
3. `model.py:32-56` - `_format_variable_with_indices()` should always quote set elements consistently
4. `original_symbols.py:79-158` - `emit_original_parameters()` doesn't validate scalar names

### Test Dependencies

| Directory | Purpose |
|-----------|---------|
| `tests/emit/test_expr_to_gams.py` | Expression conversion tests |
| `tests/emit/test_model.py` | MCP model emission tests |
| `tests/golden/*.gms` | Golden file comparisons |
| `data/gamslib/mcp/*.gms` | Generated MCP files for 17 models |

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
| 2026-01-22 | Day 5: Added detailed solve fix documentation with actual error examples, root cause locations, and specific fix strategies for S-1, S-2, S-3 |

---

*Roadmap finalized as part of Sprint 16 Day 5: Solve Gap Analysis and Roadmap Finalization*
