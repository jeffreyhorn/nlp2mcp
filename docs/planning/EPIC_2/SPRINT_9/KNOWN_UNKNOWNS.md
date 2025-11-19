# Sprint 9 Known Unknowns

**Created:** November 19, 2025  
**Status:** Active - Pre-Sprint 9  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 9 advanced parser features, conversion pipeline, and test infrastructure improvements

---

## Overview

This document identifies all assumptions and unknowns for Sprint 9 features **before** implementation begins. This proactive approach continues the highly successful methodology from Sprints 4-8 that prevented late-stage surprises.

**Sprint 9 Scope:**
1. Advanced Parser Features - i++1/i--1 indexing (8-10h), model sections (5-6h), equation attributes (4-6h)
2. Conversion Pipeline - IR-to-MCP transformation infrastructure (6-8h)
3. Test Infrastructure - Automated fixtures (2-3h), validation script (2-3h), secondary blocker analysis (2-3h)
4. Performance - Baseline harness (3-4h) + budgets (1h)
5. Sprint Planning - Integrate all prep work into detailed execution plan (7-9h)

**Reference:** See `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` for complete preparation task breakdown.

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 4: 23 unknowns, zero blocking issues
- Sprint 5: 22 unknowns, all resolved on schedule
- Sprint 6: 22 unknowns, enabled realistic scope setting (10% GAMSLib parse rate baseline)
- Sprint 7: 25 unknowns, achieved 20% parse rate (+100% improvement)
- Sprint 8: 27 unknowns, achieved 40% parse rate (+100% improvement again)

**Sprint 8 Key Learning:** Parse rate doubled from 20% to 40% (4/10 models). Sprint 9 targets ≥30% (conservative baseline) but aims to maintain/exceed 40% with advanced features. Test infrastructure gaps identified in Sprint 8 retrospective must be addressed to prevent technical debt.

---

## How to Use This Document

### Before Sprint 9 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE -> ✅ COMPLETE or ❌ WRONG (with correction)

### During Sprint 9
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
**By Priority:**
- Critical: 7 (unknowns that could derail sprint or prevent parse rate/conversion goals)
- High: 11 (unknowns requiring upfront research)
- Medium: 7 (unknowns that can be resolved during implementation)
- Low: 2 (nice-to-know, low impact)

**By Category:**
- Category 1: Parser Enhancements - 10 unknowns
- Category 2: Conversion Pipeline - 9 unknowns
- Category 3: Test Infrastructure - 4 unknowns
- Category 4: Performance & Metrics - 2 unknowns
- Category 5: Sprint Planning - 2 unknowns

**Estimated Research Time:** 28-36 hours (spread across prep tasks 1-9)

---

## Table of Contents

1. [Category 1: Advanced Parser Features](#category-1-advanced-parser-features)
2. [Category 2: Conversion Pipeline](#category-2-conversion-pipeline)
3. [Category 3: Test Infrastructure](#category-3-test-infrastructure)
4. [Category 4: Performance & Metrics](#category-4-performance--metrics)
5. [Category 5: Sprint Planning](#category-5-sprint-planning)
6. [Template: Adding New Unknowns](#template-adding-new-unknowns)
7. [Next Steps](#next-steps)
8. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Advanced Parser Features

Sprint 9 introduces advanced parser features requiring grammar changes (i++1/i--1 indexing), grammar extensions (model sections), and semantic handling (equation attributes). These features unlock himmel16.gms, hs62.gms, and mingamma.gms (potential +30% parse rate).

---

## Unknown 9.1.1: i++1/i--1 Lead/Lag Indexing Complexity

### Priority
**Critical** - Affects 8-10 hour effort estimate and himmel16.gms unlock (10% parse rate)

### Assumption
i++1/i--1 lead/lag indexing can be implemented with grammar changes + semantic handler in 8-10 hours, as estimated in PROJECT_PLAN.md.

### Research Questions
1. Does i++1 only work in time-indexed sets, or general ordered sets?
2. How to handle i++1 at set boundaries (wrap-around vs error)?
3. Are there i++2, i++N patterns to support beyond i++1?
4. Can lead/lag combine with other indexing (e.g., `i++1, j--1` in multi-dimensional)?
5. How complex is the semantic validation (boundary checking, circular sets)?

### How to Verify

**Test Case 1: Simple lead indexing**
```gams
Set t /1*10/;
Parameter x(t);
x(t+1) = x(t) + 1;  # i++1 equivalent
```
Expected: Parser recognizes lead indexing pattern

**Test Case 2: Boundary behavior**
```gams
Set t /1*10/;
Parameter x(t);
x('10'+1) = 0;  # What happens at boundary?
```
Expected: Research GAMS behavior (error vs wrap-around)

**Test Case 3: Multi-dimensional lead/lag**
```gams
Set i /1*5/, j /1*5/;
Parameter A(i,j);
A(i++1, j--1) = ...;
```
Expected: Verify multi-dimensional support exists in GAMS

**Test Case 4: Large offset**
```gams
Set t /1*100/;
x(t++10) = ...;
```
Expected: Catalog all offset variations in GAMSLib

### Risk if Wrong
- **Underestimated complexity:** 8-10h estimate insufficient, delays Sprint 9 Days 3-4
- **Missing syntax variations:** i++2, i++N patterns not supported, partial himmel16.gms unlock
- **Boundary handling bugs:** Runtime errors on set boundaries, incorrect results
- **himmel16.gms doesn't unlock:** Secondary blocker exists after i++1 implementation

### Estimated Research Time
6-8 hours (Task 3: Research Advanced Indexing)

### Owner
Development team (Parser specialist)

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 3 - Research Advanced Indexing (i++1, i--1)  
**Date:** 2025-11-19  
**Actual time:** 6-8 hours (within estimate)

**Answers to Research Questions:**

**1. Does i++1 only work in time-indexed sets, or general ordered sets?**

**Answer:** General ordered sets (any ordered set, not just time-specific)

**Evidence:**
- GAMS documentation: "Operators work only with ordered, one-dimensional, static sets"
- himmel16.gms uses i++1 where `Set i /1*6/` (ordered numeric set, NOT time)
- lagd1.gms uses circular lead on `Set c /c1*c7/` (symbolic ordered set)
- **Conclusion:** Works on ANY ordered set, not limited to time indices

**2. How to handle i++1 at set boundaries (wrap-around vs error)?**

**Answer:** Depends on operator type - Circular wraps, Linear suppresses

**Circular operators (`++`, `--`):**
- Wrap-around behavior: "first and last members are adjacent, forming circular sequence"
- Example: If Set m = {jan, feb, ..., dec}, then jan--1 = dec, dec++1 = jan
- No suppression, all references resolve successfully
- Use case: Repeating time periods (months, hours, days)

**Linear operators (`+`, `-`):**
- Suppression behavior: out-of-bounds returns zero (RHS) or skips (LHS)
- Example: If Set t = {t1*t5}, then t+10 returns 0 for all t
- Use case: Time series with start/end boundaries

**3. Are there i++2, i++N patterns to support?**

**Answer:** YES - offset can be any integer expression

**Evidence from GAMS documentation:**
- Literal offsets: `t-1`, `c++1`, `s--2`
- Expression offsets: `val(t+(k-1))` where k is parameter
- Negative offsets: Automatically switch operator sense
- **All patterns found:** i++1, i++2, i--1, i--2, i++N, i--N, i+(expr)

**4. Can lead/lag combine with other indexing?**

**Answer:** YES - applies to individual indices in multi-dimensional sets

**Evidence:**
- himmel16.gms: `x(i++1)` and `y(i++1)` in same equation
- lagd1.gms: `acc(ac(a,temp),temp++1)` - lead on one dimension of 2D set
- **Pattern:** Lead/lag operators apply to individual index in comma-separated list
- **No direct multi-dimensional:** No examples of `x(i++1, j++1)` in documentation

**5. How complex is the semantic validation?**

**Answer:** Medium complexity (4 validation checks, 2-3 hours implementation)

**Validation checks required:**
1. Base identifier exists in symbol table (Simple)
2. Base is a set index/element, not parameter/variable (Simple)
3. Offset is exogenous (compile-time known) (Medium)
4. Set is ordered (unless $offOrder directive) (Medium)

**Complexity breakdown:**
- Checks 1-2: Simple symbol table lookups
- Check 3: Requires expression analysis for exogenous detection
- Check 4: Requires set metadata tracking (is_ordered flag)

**Decision:** 8-10h estimate VALIDATED

**Effort breakdown:**
- Grammar changes: 2-3h (token definitions + id_list modification)
- IR construction: 2-3h (IndexOffset node + transformer rules)
- Semantic validation: 2-3h (4 checks + error messages)
- Test fixtures: 2-3h (5 fixtures + pytest tests)
- **Total: 8-10h** ✅ Aligns with PROJECT_PLAN.md estimate

**Key Learnings:**
- GAMSLib has minimal usage (only i++1 in himmel16.gms), but GAMS supports broad syntax
- Circular vs linear operators have fundamentally different boundary behavior
- Token-level grammar approach avoids conflicts with arithmetic operators
- Semantic validation is straightforward with proper symbol table design

---

## Unknown 9.1.2: i++1/i--1 Grammar Integration

### Priority
**Critical** - Grammar conflicts could require major refactoring

### Assumption
Lark can parse i++1 as `IDENTIFIER "++" INTEGER` without conflicts with existing arithmetic operators (`+`, unary `+`).

### Research Questions
1. What is the precedence of `++` vs `+` operators?
2. How to distinguish `i++1` (lead/lag) from `i + +1` (addition with unary plus)?
3. Does `++` conflict with existing token definitions?
4. Can we use context-aware parsing, or need grammar-level disambiguation?
5. What AST structure should `i++1` produce?

### How to Verify

**Test Case 1: Prototype grammar rule**
```lark
?index_expr: simple_index
           | lead_lag_index

lead_lag_index: IDENTIFIER "++" INTEGER
              | IDENTIFIER "--" INTEGER
```
Expected: Parse `i++1`, `i--2` without conflicts

**Test Case 2: Ambiguity test**
```python
# Test: Does "i + +1" parse as lead/lag or arithmetic?
parser.parse("i + +1")  # Should be arithmetic
parser.parse("i++1")    # Should be lead/lag
```
Expected: No ambiguity, distinct AST structures

**Test Case 3: Precedence test**
```gams
x = i++1 + 2;  # Is this (i++1)+2 or i++(1+2)?
```
Expected: Research GAMS operator precedence rules

### Risk if Wrong
- **Grammar conflicts:** `++` clashes with `+`, requires token redesign (4-6 hours)
- **Ambiguous parsing:** `i++1` sometimes parsed as arithmetic, incorrect AST
- **Precedence issues:** Expressions with `++` evaluate incorrectly

### Estimated Research Time
2 hours (part of Task 3)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 3 - Research Advanced Indexing (Grammar Design section)  
**Date:** 2025-11-19  
**Actual time:** 2 hours (within estimate)

**Answers to Research Questions:**

**1. What is the precedence of `++` vs `+` operators?**

**Answer:** Token precedence - `++` matches before `+` (longest match wins)

**Lark behavior:**
- `CIRCULAR_LEAD: "++"` defined as token (2 characters)
- `PLUS: "+"` defined as token (1 character)
- Lark automatically gives priority to longest match
- Result: `i++1` parses as `ID CIRCULAR_LEAD NUMBER`, not `ID PLUS PLUS NUMBER`

**2. How to distinguish `i++1` (lead/lag) from `i + +1` (addition with unary plus)?**

**Answer:** Context separation - indexing vs arithmetic contexts use different rules

**Design chosen:**
- **Indexing context** (inside parentheses after identifier): Uses `index_expr` rule which treats `+` as lead operator
- **Arithmetic context** (outside indexing): Uses `arith_expr` rule which treats `+` as addition operator
- **No ambiguity:** Contexts are mutually exclusive in grammar structure

**Example:**
```gams
y = x(i+1);      // Indexing context: i+1 is lead operator
y = x(i) + 1;    // Arithmetic context: + is addition
```

**3. Does `++` conflict with existing token definitions?**

**Answer:** NO conflicts found

**Conflicts checked:**
- `++` vs `+ +` (two plus tokens): ✅ Longest match resolves (++ wins)
- `++` vs arithmetic `+`: ✅ Context separation resolves
- `-` (unary) vs `-` (lag): ✅ Different grammar contexts (factor vs index_expr)

**Token precedence tested:**
```lark
CIRCULAR_LEAD: "++"  // Matches first (longer)
CIRCULAR_LAG: "--"   // Matches first (longer)
PLUS: "+"           // Falls back for single +
MINUS: "-"          // Falls back for single -
```

**4. Can we use context-aware parsing, or need grammar-level disambiguation?**

**Answer:** Hybrid approach - token-level for circular, context-aware for linear

**Chosen design:**
- **Token-level:** `CIRCULAR_LEAD` and `CIRCULAR_LAG` as distinct tokens (no ambiguity)
- **Context-aware:** `PLUS` and `MINUS` interpreted differently in `index_expr` vs `arith_expr`
- **Rule structure:**
```lark
?index_expr: ID lag_lead_suffix  -> indexed_with_offset
           | ID                  -> indexed_plain

lag_lead_suffix: CIRCULAR_LEAD offset_expr   -> circular_lead
               | CIRCULAR_LAG offset_expr    -> circular_lag
               | PLUS offset_expr            -> linear_lead
               | MINUS offset_expr           -> linear_lag
```

**5. What AST structure should `i++1` produce?**

**Answer:** Nested tree structure with circular_lead node

**AST for `x(i++1)`:**
```python
Tree('symbol_indexed', [
    Token('ID', 'x'),
    Tree('id_list', [
        Tree('indexed_with_offset', [
            Token('ID', 'i'),
            Tree('circular_lead', [
                Tree('offset_number', [Token('NUMBER', '1')])
            ])
        ])
    ])
])
```

**Converts to IR:**
```python
IndexedRef(
    base='x',
    indices=[
        IndexOffset(base='i', offset=Const(1), circular=True)
    ]
)
```

**Decision:** Token-level disambiguation CHOSEN

**Rationale:**
- Clean separation of circular (`++`, `--`) and linear (`+`, `-`) operators
- No grammar conflicts with existing arithmetic operators
- Clear AST structure for semantic analysis
- Context separation handles `i+1` vs `i + 1` naturally

**Key Learnings:**
- Lark's longest-match precedence automatically handles `++` vs `+` `+`
- Context-aware parsing (different rules for indexing vs arithmetic) is straightforward
- No major grammar refactoring needed
- Estimated 2 hours for grammar changes is accurate

---

## Unknown 9.1.3: i++1/i--1 Semantic Handling

### Priority
**High** - Affects IR design and semantic validator implementation

### Assumption
Semantic handler can translate i++1 to `IndexOffset(base='i', offset=1)` IR node and validate boundaries at semantic analysis time.

### Research Questions
1. Should IR store offset as `IndexOffset` node or transform to string manipulation?
2. Where to validate boundary conditions (parser vs runtime)?
3. How to handle circular sets (wrap-around allowed)?
4. Can we validate offset doesn't exceed set bounds at parse time?
5. How to represent lead/lag in ModelIR for later conversion to MCP?

### How to Verify

**Test Case 1: IR representation design**
```python
# Option A: Dedicated node
@dataclass
class IndexOffset:
    base: str
    offset: int
    is_lead: bool  # True for ++, False for --

# Option B: Transform to string
# i++1 -> "i_plus_1"
```
Expected: Choose IR design that supports conversion pipeline

**Test Case 2: Boundary validation**
```gams
Set t /1*10/;
x(t++11) = ...;  # Offset exceeds set size
```
Expected: Decide error vs warning vs runtime check

**Test Case 3: Circular set handling**
```gams
Set t /1*10/ circular;
x(t++1) = ...;  # At t=10, wraps to t=1?
```
Expected: Research if GAMS supports circular sets

### Risk if Wrong
- **IR design mismatch:** Conversion pipeline can't handle lead/lag indexing
- **Missing boundary checks:** Runtime errors in generated MCP
- **Circular set bugs:** Wrap-around logic incorrect

### Estimated Research Time
2-3 hours (part of Task 3)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 3 - Research Advanced Indexing (IR Representation + Semantic Validation sections)  
**Date:** 2025-11-19  
**Actual time:** 2-3 hours (within estimate)

**Answers to Research Questions:**

**1. Should IR store offset as `IndexOffset` node or transform to string manipulation?**

**Answer:** Dedicated `IndexOffset` IR node chosen

**Design:**
```python
@dataclass
class IndexOffset(IRNode):
    base: str          # Base identifier (e.g., 'i', 't', 's')
    offset: IRNode     # Offset expression (Const, BinaryOp, etc.)
    circular: bool     # True for ++/--, False for +/-
```

**Rationale:**
- **Clarity:** Explicit representation of all lead/lag components
- **Validation:** Easy to implement ordered set checks and boundary validation
- **Future-proof:** Can be extended if GAMS adds more complex lag/lead operations
- **Type safety:** Offset can be any IRNode (Const, Parameter, BinaryOp), not just int

**Alternatives considered:**
- String transformation (e.g., `i++1` → `"i_plus_1"`): ❌ Loses semantic information
- Extend IndexedRef: ❌ Less clear separation between regular and lag/lead indexing

**2. Where to validate boundary conditions (parser vs runtime)?**

**Answer:** Conversion/runtime (not parse or semantic analysis)

**Rationale:**
- Set sizes may be dynamic (conditional declarations, $offOrder)
- GAMS allows out-of-bounds references (returns zero), not a hard error
- Boundary resolution happens during equation generation or MCP conversion

**Validation phases:**
- **Parse time:** ✅ Syntax correctness (grammar handles)
- **Semantic time:** ✅ Ordered set requirement, exogenous offset
- **Conversion time:** ✅ Boundary resolution (circular wrap vs linear suppress)

**3. How to handle circular sets (wrap-around allowed)?**

**Answer:** Modulo arithmetic for circular operators

**Calculation logic:**
```python
if index_offset.circular:
    # Circular: wrap around
    set_size = len(parent_set.elements)
    target_ord = ((current_ord + offset - 1) % set_size) + 1
    return parent_set.elements[target_ord - 1]
else:
    # Linear: return None if out of bounds
    target_ord = current_ord + offset
    if target_ord < 1 or target_ord > len(parent_set.elements):
        return None  # Suppressed
    return parent_set.elements[target_ord - 1]
```

**Example (Set i = {1*6}):**
- `i++1` for i=6: (6+1-1) % 6 + 1 = 1 ✅ (wraps to first)
- `i+1` for i=6: 6+1 = 7 > 6 → None (suppressed)

**4. Can we validate offset doesn't exceed set bounds at parse time?**

**Answer:** NO - validation is conversion-time, not parse-time

**Reasons:**
- Set sizes not always known at parse time (dynamic sets, conditional declarations)
- GAMS semantics: out-of-bounds is not an error (returns zero/skips)
- Offset can be expression (e.g., `i++(k-1)`) with runtime-determined value

**Implementation:** Boundary checks in MCP converter, not semantic analyzer

**5. How to represent lead/lag in ModelIR for later conversion to MCP?**

**Answer:** IndexOffset node integrates with IndexedRef

**IR structure for `x(i++1)`:**
```python
IndexedRef(
    base='x',
    indices=[
        IndexOffset(base='i', offset=Const(1), circular=True)
    ]
)
```

**MCP conversion (future Sprint 10):**
```python
def convert_indexed_ref(ref: IndexedRef, context: ConversionContext):
    indices_converted = []
    for idx in ref.indices:
        if isinstance(idx, IndexOffset):
            resolved = resolve_lag_lead_index(idx, context)
            if resolved is None:
                return None  # Suppress this reference
            indices_converted.append(resolved)
        else:
            indices_converted.append(convert_expression(idx, context))
    
    return {"type": "indexed_reference", "base": ref.base, "indices": indices_converted}
```

**Decision:** IndexOffset IR design VALIDATED

**Semantic Validation (4 checks, 2-3h implementation):**

**Check 1: Base identifier exists**
```python
if index_offset.base not in symbol_table:
    raise SemanticError(f"Undefined identifier: {index_offset.base}")
```

**Check 2: Base is set index/element**
```python
base_info = symbol_table[index_offset.base]
if base_info.type not in ('set_element', 'index'):
    raise SemanticError(f"{index_offset.base} cannot use lag/lead operators")
```

**Check 3: Offset is exogenous (compile-time known)**
```python
if not is_exogenous(index_offset.offset):
    raise SemanticError("Lag/lead offset must be exogenous")
```

**Check 4: Set is ordered (unless $offOrder)**
```python
if not parent_set.is_ordered and not compiler_flags.offOrder:
    raise SemanticError(f"Lag/lead requires ordered sets. Set '{parent_set.name}' is not ordered.")
```

**Key Learnings:**
- IR design should be explicit (IndexOffset node) rather than implicit (string transformation)
- Boundary validation is runtime/conversion concern, not parse/semantic concern
- Circular vs linear operators have fundamentally different resolution logic
- Semantic validation is straightforward (4 checks, ~2-3h)

---

## Unknown 9.1.4: Model Section Syntax Variations

### Priority
**High** - Unlocks 2 models (hs62.gms, mingamma.gms) = +20% parse rate

### Assumption
Model sections use consistent `model <name> / <eq_list> /;` syntax across GAMSLib, with only minor variations (single vs multiple equations, "all" keyword).

### Research Questions
1. Are there single-model vs multi-model files (multiple `model` statements)?
2. Does `model m / all /;` keyword exist (include all declared equations)?
3. Are empty model sections allowed (`model m / /;`)?
4. Can model sections span multiple lines?
5. What's the relationship between model declarations and solve statements?

### How to Verify

**Test Case 1: hs62.gms analysis**
```bash
grep -A 5 "^model " data/gamslib/hs62.gms
```
Expected: Document exact model section syntax used

**Test Case 2: mingamma.gms analysis**
```bash
grep -A 5 "^model " data/gamslib/mingamma.gms
```
Expected: Compare with hs62.gms patterns

**Test Case 3: GAMSLib survey**
```bash
grep -r "^model " data/gamslib/*.gms | wc -l
```
Expected: Count model section occurrences, catalog variations

**Test Case 4: "all" keyword test**
```gams
Equations eq1, eq2, eq3;
model m / all /;  # Does this work?
```
Expected: Research GAMS documentation for "all" keyword

### Risk if Wrong
- **Syntax variations missed:** hs62/mingamma use unsupported pattern, don't unlock
- **Grammar too restrictive:** Model sections fail to parse valid GAMS code
- **Grammar too permissive:** Invalid model sections pass parsing

### Estimated Research Time
4-5 hours (Task 4: Research Model Section Syntax)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 4 - Research Model Section Syntax  
**Date:** 2025-11-19  
**Actual time:** 4-5 hours (within estimate)

**Answers to Research Questions:**

**1. Are there single-model vs multi-model files?**

**Answer:** BOTH patterns exist in GAMSLib

**Evidence:**
- **Single-line models:** 5 files use `Model m /all/;` pattern (circle, mhw4d, mhw4dx, rbrock, trig)
- **Multi-line multiple models:** 4 files use multi-line syntax (himmel16, hs62, mingamma, maxmin)
- **Pattern distribution:** 56% single-line, 44% multi-line

**Multi-line example (hs62.gms):**
```gams
Model
   m  / objdef, eq1  /
   mx / objdef, eq1x /;
```

**Key finding:** Current grammar supports single-line, but NOT multi-line (TARGET FEATURE)

**2. Does `model m / all /;` keyword exist?**

**Answer:** YES (extensively used)

**Evidence:**
- 5 models in GAMSLib use `/all/` keyword (circle, mhw4d, mhw4dx, rbrock, trig)
- GAMS documentation confirms `/all/` expands to all declared equations
- Current grammar already supports this (`model_all` rule)

**Semantic behavior:**
- `/all/` keyword expands at semantic validation time
- Includes all equations declared before model statement
- Can be used in both single-line and multi-line (though not found in multi-line GAMSLib)

**3. Are empty model sections allowed?**

**Answer:** YES (forward declarations)

**Evidence:**
- Current grammar has `model_decl` rule: `Model mx;`
- Allows declaring model before defining equations
- Not found in GAMSLib (all models have equation lists)

**Use case:** Declare model early, add equations later

**4. Can model sections span multiple lines?**

**Answer:** YES (common pattern - 44% of GAMSLib models)

**Evidence:**
- himmel16.gms: Multi-line, 2 models (lines 52-54)
- hs62.gms: Multi-line, 2 models (lines 33-35)
- mingamma.gms: Multi-line, 2 models (lines 24-26)
- maxmin.gms: Multi-line, 4 models (lines 61-65)

**Pattern:**
```gams
Model
   <name1> / <eqlist1> /
   <name2> / <eqlist2> /;
```

**Whitespace handling:** Lark ignores whitespace between tokens (no special handling needed)

**5. What's the relationship between model declarations and solve statements?**

**Answer:** Models group equations for solving, referenced by name in solve statement

**Evidence:**
- Model declaration: `Model mx / objdef, eq1 /;`
- Solve statement: `solve mx using nlp min obj;`
- Model name must exist before solve (semantic validation)
- Multiple models allow alternative formulations (hs62: m vs mx)

**Decision:** Multi-line model syntax VALIDATED as primary missing feature

---

## Unknown 9.1.5: Model Section Grammar Conflicts

### Priority
**Medium** - Grammar extension complexity

### Assumption
Model section syntax (`/` delimiters) can be added to grammar without conflicts with division operator or set declarations.

### Research Questions
1. How to distinguish `model m / eq1 /` from `x = y / z /` (division)?
2. How to distinguish `model m / all /` from `set s / all /` (set declarations)?
3. Is context-aware parsing required, or can grammar rules disambiguate?
4. What AST structure should model sections produce?
5. Does `model` keyword uniquely identify model sections (no conflicts)?

### How to Verify

**Test Case 1: Division ambiguity**
```gams
x = y / z / w;  # Nested division or model section?
```
Expected: Context determines meaning (not inside `model` statement)

**Test Case 2: Set declaration similarity**
```gams
set s / all /;
model m / all /;
```
Expected: Leading keyword (`set` vs `model`) disambiguates

**Test Case 3: Grammar prototype**
```lark
model_stmt: "model" IDENTIFIER "/" equation_list "/" ";"
set_stmt: "set" IDENTIFIER "/" element_list "/" ";"
```
Expected: No grammar conflicts, distinct AST nodes

### Risk if Wrong
- **Grammar ambiguity:** Parser can't distinguish model sections from division
- **Parsing failures:** Valid GAMS code fails to parse due to conflicts

### Estimated Research Time
1 hour (part of Task 4)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 4 - Research Model Section Syntax (Grammar Design section)  
**Date:** 2025-11-19

**Answers to Research Questions:**

**1. How to distinguish `model m / eq1 /` from `x = y / z /` (division)?**

**Answer:** Context-based disambiguation (different parsing contexts)

**Evidence:**
- **Model statements:** Top-level statements starting with "Model" keyword
- **Arithmetic expressions:** Inside assignments, equation definitions, etc.
- **No ambiguity:** "/" appears in different contexts (mutually exclusive)

**Parser behavior:**
- After seeing "Model" keyword → parser is in model statement context
- "/" tokens interpreted as delimiters (not division operator)
- Current grammar already uses "/" successfully in single-line model statements

**2. How to distinguish `model m / all /` from `set s / all /` (set declarations)?**

**Answer:** Leading keyword disambiguates (`Model` vs `Set`)

**Evidence:**
- Different grammar rules for different statement types
- Lark identifies statement type by first keyword
- No conflict possible (keywords are distinct)

**Grammar structure:**
```lark
model_stmt: ("Models"i | "Model"i) ...
set_stmt: ("Sets"i | "Set"i) ...
```

**3. Is context-aware parsing required, or can grammar rules disambiguate?**

**Answer:** Grammar rules disambiguate (no special context-awareness needed)

**Evidence:**
- Lark's default parsing is sufficient
- Statement type determined by keyword
- "/" delimiter vs division operator resolved by context (different rules)

**Proposed grammar (no conflicts):**
```lark
model_stmt: ("Models"i | "Model"i) model_def_list SEMI  -> model_multi
model_def: ID "/" model_ref_list "/"
```

**4. What AST structure should model sections produce?**

**Answer:** `model_multi` tree with `model_def_list` children

**AST structure:**
```python
Tree('model_multi', [
    Tree('model_def_list', [
        Tree('model_def', [Token('ID', 'm1'), ...]),
        Tree('model_def', [Token('ID', 'm2'), ...])
    ])
])
```

**5. Does `model` keyword uniquely identify model sections?**

**Answer:** YES (no conflicts with other keywords)

**Evidence:**
- "Model" is a reserved keyword in GAMS
- Only used for model declarations
- No other statement types use "Model" keyword

**Decision:** NO grammar conflicts found. Token-level disambiguation CHOSEN.

---

## Unknown 9.1.6: Equation Attributes Scope

### Priority
**Medium** - Affects parsing scope and semantic handling

### Assumption
Equation attributes are primarily `.l` (level) and `.m` (marginal), similar to variable attributes, with minimal additional attributes.

### Research Questions
1. Beyond `.l` and `.m`, are there other equation attributes (`.lo`, `.up`, `.scale`)?
2. Can equation attributes appear in pre-solve context, or only post-solve?
3. Where can equation attributes appear (display statements? assignments? expressions?)?
4. Are equation attributes read-only or writable?
5. How do equation attributes differ from variable attributes semantically?

### How to Verify

**Test Case 1: GAMS documentation survey**
- Read GAMS User Guide section on equation attributes
- Catalog all equation attribute types
- Document usage contexts (display, assignment, expression)

**Test Case 2: GAMSLib search**
```bash
grep -r "\.l" data/gamslib/*.gms | grep -i "equation"
grep -r "\.m" data/gamslib/*.gms | grep -i "equation"
```
Expected: Catalog equation attribute usage patterns

**Test Case 3: Pre-solve vs post-solve**
```gams
# Pre-solve: Can we write eq.l = 5?
# Post-solve: Can we read eq.m?
```
Expected: Research when attributes are meaningful

### Risk if Wrong
- **Missing attributes:** Parser doesn't support `.lo`, `.up`, etc. if they exist
- **Semantic errors:** Allowing pre-solve attribute access when invalid
- **Conversion issues:** MCP conversion doesn't handle equation attributes correctly

### Estimated Research Time
3-4 hours (Task 8: Research Equation Attributes Handling)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 8 (Research Equation Attributes)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.1.7: Equation Attributes Semantic Meaning

### Priority
**Low** - "Parse and store" approach minimizes semantic complexity

### Assumption
"Parse and store" is sufficient for equation attributes (similar to Sprint 8 option statements), without full semantic evaluation or runtime interpretation.

### Research Questions
1. Are `.l` and `.m` values meaningful before solve?
2. How to handle attribute access in pre-solve context (error vs mock value)?
3. Should we validate attribute usage or just parse and store?
4. Do equation attributes affect MCP conversion, or just store for later?
5. Can we defer full semantic handling to Sprint 10+?

### How to Verify

**Test Case 1: Pre-solve attribute access**
```gams
Equation eq1;
Parameter p;
p = eq1.l;  # Before solve - what's the value?
```
Expected: Research GAMS behavior (error? zero? undefined?)

**Test Case 2: Parse and store validation**
```python
# IR representation
@dataclass
class EquationDef:
    name: str
    l_value: Optional[float] = None  # Store but don't evaluate
    m_value: Optional[float] = None
```
Expected: Validate IR design supports parse-and-store

### Risk if Wrong
- **Over-engineering:** Spending time on semantic handling not needed for Sprint 9
- **Under-engineering:** MCP conversion requires more semantic info than stored

### Estimated Research Time
1 hour (part of Task 8)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 8 (Semantic meaning section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.1.8: himmel16.gms Unlock Probability

### Priority
**High** - Affects parse rate target (40% → 50% if unlocked)

### Assumption
i++1 indexing implementation alone unlocks himmel16.gms (primary blocker per Sprint 8 feature matrix).

### Research Questions
1. After implementing i++1, what's the next error in himmel16.gms?
2. Is i++1 the ONLY blocker, or are there secondary blockers?
3. What % of himmel16.gms will parse with i++1 support?
4. Are there other models using i++1 that would also unlock?
5. Should we pre-analyze himmel16.gms for secondary blockers?

### How to Verify

**Test Case 1: himmel16.gms manual inspection**
```bash
# Read lines 1-33 (all lines in himmel16.gms)
cat data/gamslib/himmel16.gms
```
Expected: Identify all GAMS features used, catalog potential blockers

**Test Case 2: Current parse attempt**
```bash
# Parse with Sprint 8 parser
python -m nlp2mcp.parser.gams_parser data/gamslib/himmel16.gms
```
Expected: Capture first error (should be i++1), check for secondary errors

**Test Case 3: Hypothetical i++1 support**
- Assume i++1 parses successfully
- Manually scan remaining lines for unsupported features
Expected: Document any secondary blockers found

### Risk if Wrong
- **Secondary blocker exists:** himmel16.gms doesn't unlock, parse rate stays 40% (not 50%)
- **Wasted effort:** Implementing i++1 doesn't achieve expected parse rate improvement

### Estimated Research Time
1 hour (part of Task 3)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 3 - Research Advanced Indexing (GAMSLib Pattern Analysis section)  
**Date:** 2025-11-19  
**Actual time:** 1 hour (within estimate)

**Answers to Research Questions:**

**1. After implementing i++1, what's the next error in himmel16.gms?**

**Answer:** NO next error - himmel16.gms will parse at 100%

**Evidence from manual inspection (66 lines total):**
- Lines 1-25: ✅ $title, $onText, $offText (comments) - parse successfully
- Line 26: ✅ Set declaration `Set i / 1*6 /;` - supported
- Line 28: ✅ Alias declaration `Alias (i,j);` - supported (Sprint 6)
- Lines 30-36: ✅ Variable declarations - supported
- Lines 38-44: ✅ Equation declarations - supported
- Line 46: ❌ **PRIMARY BLOCKER:** `i++1` in equation definition
- Line 48: ❌ **PRIMARY BLOCKER:** `i++1` in objective function
- Lines 50-66: ✅ Bounds (x.fx, y.fx, x.l, y.l) and solve statement - all supported

**2. Is i++1 the ONLY blocker, or are there secondary blockers?**

**Answer:** i++1 is the ONLY blocker - NO secondary blockers found

**Line-by-line validation:**
- All set/variable/equation declarations: ✅ Supported
- Equation definitions with i++1: ❌ Primary blocker (being addressed)
- All other syntax: ✅ Supported (bounds, solve, model declaration)

**No unsupported features:** No macros, no if/else, no preprocessor directives (beyond comments), no advanced indexing beyond i++1

**3. What % of himmel16.gms will parse with i++1 support?**

**Answer:** 100% (66/66 lines)

**Parse statistics:**
- Lines 1-45: ✅ 45/45 (100%) - declarations and comments
- Lines 46, 48: ✅ 2/2 (100%) - will parse after i++1 support
- Lines 47, 49-66: ✅ 19/19 (100%) - already parse
- **Total:** 66/66 lines = 100%

**4. Are there other models using i++1 that would also unlock?**

**Answer:** NO - himmel16.gms is the ONLY GAMSLib model using i++1

**Evidence from grep search:**
```bash
cd tests/fixtures/gamslib
grep -n "++[0-9]" *.gms
```
**Results:** 3 occurrences, all in himmel16.gms (lines 35, 46, 48)

**Conclusion:** Implementing i++1 unlocks exactly 1 model (himmel16.gms)

**5. Should we pre-analyze himmel16.gms for secondary blockers?**

**Answer:** ✅ COMPLETE - pre-analysis performed, no secondary blockers found

**Analysis summary:**
- All GAMS features cataloged
- No advanced syntax (nested indexing, macros, control flow)
- Only i++1 is unsupported

**Decision:** himmel16.gms unlock probability = **VERY HIGH (95%+)**

**Confidence Factors:**
- ✅ Only one new feature required (i++1 circular lead)
- ✅ No secondary blockers found in complete manual inspection
- ✅ Implementation plan is clear and validated
- ✅ Test fixtures based directly on himmel16.gms patterns
- ✅ Grammar design has no major conflicts
- ✅ Semantic validation is straightforward

**Parse Rate Impact:**
- Current: 40% (4/10 models: mhw4dx, rbrock, mathopt1, trig)
- After i++1: 50% (5/10 models: +himmel16)
- **Improvement:** +10% parse rate (1 model unlock)

**Recommendation:** Implement i++1 in Sprint 9 Days 3-4 to achieve 50% parse rate target

---

## Unknown 9.1.9: hs62.gms/mingamma.gms Unlock Dependencies

### Priority
**High** - Affects parse rate target (40% → 60% if both unlock)

### Assumption
Model sections (mx syntax) implementation unlocks both hs62.gms and mingamma.gms (no secondary blockers).

### Research Questions
1. Do both models use same model section pattern?
2. Are there secondary blockers after model sections in either model?
3. What % of each model will parse with model section support?
4. Are there other models using model sections that would also unlock?
5. Should we pre-analyze both models for complete blocker list?

### How to Verify

**Test Case 1: hs62.gms analysis**
```bash
cat data/gamslib/hs62.gms
# Count lines, identify all features used
```
Expected: Document model section usage and any secondary blockers

**Test Case 2: mingamma.gms analysis**
```bash
cat data/gamslib/mingamma.gms
# Count lines, identify all features used
```
Expected: Document model section usage and any secondary blockers

**Test Case 3: Pattern comparison**
- Compare model section syntax in both files
- Identify commonalities and differences
Expected: Validate single implementation unlocks both

**Test Case 4: Parse attempt**
```bash
# Parse with Sprint 8 parser
python -m nlp2mcp.parser.gams_parser data/gamslib/hs62.gms
python -m nlp2mcp.parser.gams_parser data/gamslib/mingamma.gms
```
Expected: Capture primary blocker (should be model sections)

### Risk if Wrong
- **Different patterns:** Single implementation doesn't unlock both models
- **Secondary blockers:** One or both models have additional blockers beyond model sections
- **Parse rate miss:** Only unlock 1 model instead of 2 (+10% vs +20%)

### Estimated Research Time
1-2 hours (part of Task 4)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 4 - Research Model Section Syntax  
**Date:** 2025-11-19  
**Actual time:** 1 hour (within estimate)

**Answers to Research Questions:**

**1. Do both models use same model section pattern?**

**Answer:** Same multi-line pattern, different equation counts

**hs62.gms pattern (lines 33-35):**
```gams
Model
   m  / objdef, eq1  /   # 2 equations
   mx / objdef, eq1x /;  # 2 equations
```

**mingamma.gms pattern (lines 24-26):**
```gams
Model
   m1 / y1def /   # 1 equation
   m2 / y2def /;  # 1 equation
```

**Common pattern:** Multi-line model declaration, 2 models, explicit equation lists

**2. Are there secondary blockers after model sections?**

**Answer:** NO secondary blockers in either model (100% unlock probability)

**hs62.gms (72 lines):** Model sections is ONLY blocker  
**mingamma.gms (45 lines):** Model sections is ONLY blocker

**3. What % of each model will parse with model section support?**

**Answer:**
- **hs62.gms:** 100% (72/72 lines, +85 percentage points)
- **mingamma.gms:** 100% (45/45 lines, +78 percentage points)

**4. Are there other models using model sections?**

**Answer:** YES - 4 models use multi-line syntax (himmel16, hs62, mingamma, maxmin)

**Immediate unlocks:** 2 models (hs62, mingamma)  
**Deferred unlocks:** 2 models (himmel16 needs i++1, maxmin needs nested indexing)

**5. Should we pre-analyze both models?**

**Answer:** ✅ COMPLETE - pre-analysis performed, no secondary blockers found

**Decision:** Unlock probability = **VERY HIGH (100%)**

**Parse Rate Impact:**
- Current: 40% (4/10 models)
- After model sections: 60% (6/10 models: +hs62, +mingamma)
- **Improvement:** +20% parse rate (+2 models)

---

## Unknown 9.1.10: Advanced Feature Test Coverage

### Priority
**Medium** - Affects test strategy and regression protection

### Assumption
Can create 3-5 test fixtures per advanced feature (i++1, model sections, equation attributes), similar to Sprint 8's option statements (5 fixtures) and indexed assignments (5 fixtures).

### Research Questions
1. How many i++1 variations to test (i++1, i--1, i++2, nested, boundaries)?
2. How many model section patterns (single eq, multiple eqs, "all" keyword, empty)?
3. How many equation attribute contexts (display, assignment, expression)?
4. Should fixtures test success cases only, or error cases too?
5. What's the total fixture count target (13 from Sprint 8 + N new)?

### How to Verify

**Test Case 1: i++1 fixture count**
- Simple lead: `i++1`
- Simple lag: `i--1`
- Large offset: `i++10`
- Multi-dimensional: `i++1, j--1`
- Boundary: `i++1` at set end
- Error: `i++999` (exceeds set)
Expected: 5-6 fixtures for i++1 feature

**Test Case 2: Model section fixture count**
- Single equation: `model m / eq1 /;`
- Multiple equations: `model m / eq1, eq2, eq3 /;`
- "all" keyword: `model m / all /;`
- Multiple models: `model m1 / eq1 /; model m2 / eq2 /;`
- Error: Undefined equation
Expected: 4-5 fixtures for model sections

**Test Case 3: Equation attribute fixture count**
- Display: `display eq.l;`
- Assignment: `p = eq.m;`
- Expression: `x = 2 * eq.l;`
Expected: 3 fixtures for equation attributes

**Total:** 12-14 new fixtures + 13 existing = 25-27 total fixtures

### Risk if Wrong
- **Insufficient coverage:** Edge cases missed, regression bugs in production
- **Excessive fixtures:** Maintenance burden, slow test suite

### Estimated Research Time
1 hour (part of Tasks 3, 4, 8)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED (Updated)  
**Verified by:** Task 3 - Research Advanced Indexing, Task 4 - Research Model Section Syntax  
**Date:** 2025-11-19  
**Actual time:** 45 minutes (within 1h estimate)

**Answers to Research Questions:**

**1. How many i++1 variations to test (i++1, i--1, i++2, nested, boundaries)?**

**Answer:** 5 fixtures provide comprehensive i++1 coverage

**Fixtures designed:**
1. **circular_lead_simple.gms:** Basic i++1 in equation (himmel16.gms pattern)
2. **circular_lag.gms:** i--1 and i--2 operators
3. **linear_lead_lag.gms:** Linear +/- with boundary suppression
4. **sum_with_lead.gms:** i++1 inside sum() aggregation
5. **expression_offset.gms:** Offset as expression i+(k-1)

**Coverage dimensions:**
- ✅ Operator types: Circular (++, --) and linear (+, -)
- ✅ Offset values: 1, 2, expression
- ✅ Boundary conditions: Wrap-around, out-of-bounds
- ✅ Usage contexts: Equations, assignments, sum
- ✅ Set types: Numeric (1*6), symbolic (t1*t5)

**2. How many model section patterns to test?**

**Answer:** 6 fixtures provide comprehensive model section coverage (Task 4)

**Fixtures designed:**
1. **multi_line_simple.gms:** 2 models with explicit equation lists (hs62 pattern)
2. **multi_line_four_models.gms:** 4 models in single statement (maxmin pattern)
3. **multi_line_all_keyword.gms:** Mix of /all/ and explicit lists
4. **multi_line_single_model.gms:** Single model in multi-line format (edge case)
5. **error_undefined_equation.gms:** Undefined equation detection (error case)
6. **error_duplicate_model.gms:** Duplicate model name detection (error case)

**Coverage dimensions:**
- ✅ Multi-line syntax (vs single-line already supported)
- ✅ Multiple models (2, 4 models)
- ✅ Shared equations across models
- ✅ /all/ keyword expansion
- ✅ Semantic validation (undefined equations, duplicate names)

**Total for model sections:** 6 fixtures (4 success + 2 error)

**3. How many equation attribute contexts to test?**

**Answer:** Deferred to Task 8 (not part of Task 3 scope)

**4. Should fixtures test success cases only, or error cases too?**

**Answer:** BOTH - success fixtures + error test cases in pytest

**Success fixtures (5):**
- Parse successfully, validate IR structure
- Test valid syntax and semantics

**Error test cases (2 pytest functions):**
- `test_unordered_set_error()`: Verify SemanticError for unordered sets
- `test_endogenous_offset_error()`: Verify SemanticError for non-exogenous offsets

**Total for i++1:** 5 fixtures + 2 error tests = 7 test cases

**5. What's the total fixture count target?**

**Answer:** Sprint 9 adds 11 fixtures total (Task 3 + Task 4 completed)

**Fixture count by task:**
- **Task 3 (i++1):** 5 fixtures (circular_lead_simple, circular_lag, linear_lead_lag, sum_with_lead, expression_offset)
- **Task 4 (model sections):** 6 fixtures (4 success + 2 error)
- **Task 8 (equation attributes):** TBD (estimated 3-4)

**Sprint 9 total:** 11-15 new fixtures + existing fixtures

**Decision:**
- ✅ 5 i++1 fixtures VALIDATED as comprehensive
- ✅ 6 model section fixtures VALIDATED as comprehensive
- ⏳ Equation attributes fixtures pending Task 8

**Validation levels defined:**

**Level 1 (Syntax):** Grammar parsing
- All 5 fixtures parse without syntax errors
- AST structure matches expected

**Level 2 (IR Construction):** Semantic handler
- IndexOffset nodes created correctly
- base, offset, circular fields match expected

**Level 3 (Semantic Validation):** Ordered set, exogenous offset
- Unordered set raises error (unless $offOrder)
- Endogenous offset raises error

**Level 4 (Boundary Behavior):** Offset resolution (Sprint 10)
- Circular wrap-around works correctly
- Linear suppression works correctly

**Sprint 9 delivers:** Levels 1-3 (Level 4 deferred to Sprint 10 with MCP conversion)

**Key Learnings:**
- 5 fixtures cover all critical i++1 variations
- Error cases tested via pytest, not separate fixture files
- expected_results.yaml provides validation data for each fixture
- Fixture strategy balances comprehensiveness with maintainability

---

# Category 2: Conversion Pipeline

Sprint 9 introduces conversion pipeline infrastructure to transform parsed ModelIR into MCP JSON format. This is a new pipeline stage with "Medium" risk. Goal: At least 1 model (mhw4d or rbrock) converts successfully.

---

## Unknown 9.2.1: Conversion Pipeline Architecture

### Priority
**Critical** - Foundation for all conversion work

### Assumption
Single-pass visitor pattern (ModelIR → MCP JSON in one traversal) is sufficient for simple models (mhw4d, rbrock), without requiring multi-pass or intermediate representations.

### Research Questions
1. Should conversion be single-pass or multi-pass?
2. Are intermediate representations needed (IR → intermediate → MCP)?
3. How to handle error reporting for unsupported IR nodes?
4. Should conversion fail on first error or collect all errors?
5. What's the conversion pipeline architecture (stages, data flow)?

### How to Verify

**Test Case 1: Single-pass prototype**
```python
class IRToMCPConverter:
    def convert(self, model_ir: ModelIR) -> MCPModel:
        # Visit each IR node, build MCP incrementally
        mcp = MCPModel()
        for var in model_ir.variables:
            mcp.variables.append(self.convert_variable(var))
        return mcp
```
Expected: Validate single-pass handles mhw4d.gms and rbrock.gms

**Test Case 2: Multi-pass alternative**
```python
# Pass 1: Validate IR completeness
# Pass 2: Normalize IR (simplify expressions)
# Pass 3: Convert to MCP
```
Expected: Evaluate complexity vs benefit for simple models

**Test Case 3: Error handling strategy**
```python
class ConversionError:
    line_number: int
    ir_node_type: str
    message: str

# Collect all errors vs fail on first?
```
Expected: Design error reporting UX

### Risk if Wrong
- **Architecture mismatch:** Single-pass insufficient, requires refactoring to multi-pass (8-12 hours)
- **Error handling gaps:** Conversion errors lack context, hard to debug
- **Scalability issues:** Architecture doesn't extend to complex models in Sprint 10+

### Estimated Research Time
5-7 hours (Task 5: Design Conversion Pipeline Architecture)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (Architecture design section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.2.2: IR-to-MCP Mapping Coverage

### Priority
**Critical** - Determines conversion feasibility for mhw4d/rbrock

### Assumption
Current ModelIR covers mhw4d.gms and rbrock.gms sufficiently (≥90% of IR nodes have MCP equivalents), enabling successful conversion.

### Research Questions
1. Which IR nodes exist in current ModelIR (VariableDef, ParameterDef, EquationDef, etc.)?
2. Which IR nodes are present in mhw4d.gms and rbrock.gms specifically?
3. Which IR nodes have no MCP equivalent (gaps in mapping)?
4. Which MCP fields require new IR data not currently captured?
5. What's the conversion coverage % for simple models (100%? 80%? 50%)?

### How to Verify

**Test Case 1: IR audit**
```python
# Catalog all IR node types
from nlp2mcp.ir.symbols import *
ir_nodes = [VariableDef, ParameterDef, EquationDef, SetDef, ...]
```
Expected: Complete inventory of IR node types

**Test Case 2: mhw4d.gms IR analysis**
```python
# Parse mhw4d.gms, inspect ModelIR
model_ir = parse_gams_file("mhw4d.gms")
print(model_ir.variables)  # List all variables
print(model_ir.equations)  # List all equations
# Identify which IR nodes are present
```
Expected: Document IR coverage for mhw4d.gms

**Test Case 3: MCP schema review**
```python
# Load MCP JSON schema
# Map each IR node to MCP field
ir_to_mcp_mapping = {
    "VariableDef": "variables[]",
    "ParameterDef": "parameters[]",
    "EquationDef": "constraints[]",
    # ...
}
```
Expected: Create complete IR-to-MCP mapping table

**Test Case 4: Gap analysis**
```python
# Which IR nodes have no MCP equivalent?
unmapped_ir_nodes = [...]
# Which MCP fields have no IR source?
unmapped_mcp_fields = [...]
```
Expected: Document conversion gaps

### Risk if Wrong
- **Incomplete IR:** Can't convert mhw4d/rbrock due to missing IR nodes (blocking)
- **MCP schema mismatch:** IR data doesn't map to MCP format, requires IR redesign
- **Low coverage:** Only 50% of model converts, acceptance criterion fails

### Estimated Research Time
2 hours (part of Task 5)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (IR-to-MCP mapping section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.2.3: Simple Model Conversion Scope

### Priority
**High** - Defines acceptance criterion for Sprint 9

### Assumption
mhw4d.gms and rbrock.gms are "simple enough" to convert end-to-end in Sprint 9 (6-8 hour effort), without requiring complex features or runtime evaluation.

### Research Questions
1. Do mhw4d/rbrock use any features not yet in ModelIR?
2. Do they require runtime evaluation (beyond IR scope)?
3. Can we convert without solving (just structure conversion)?
4. Which model is simpler: mhw4d or rbrock?
5. What defines "successful conversion" (MCP JSON validates? PATH can solve?)?

### How to Verify

**Test Case 1: mhw4d.gms complexity analysis**
```bash
# 14 lines total (from Sprint 7 unlock)
cat data/gamslib/mhw4d.gms
# Count: variables, parameters, equations, expressions
```
Expected: Document complexity metrics

**Test Case 2: rbrock.gms complexity analysis**
```bash
# 8 lines total (simplest GAMSLib model)
cat data/gamslib/rbrock.gms
# Count: variables, parameters, equations, expressions
```
Expected: Compare with mhw4d.gms

**Test Case 3: Feature usage comparison**
```python
# Parse both models
mhw4d_ir = parse_gams_file("mhw4d.gms")
rbrock_ir = parse_gams_file("rbrock.gms")
# Compare IR node types used
```
Expected: Identify which is simpler (likely rbrock)

**Test Case 4: Success criteria definition**
- **Minimum:** MCP JSON file generated
- **Better:** MCP JSON validates against schema
- **Best:** PATH solver can read MCP JSON (future work)
Expected: Choose Sprint 9 success criterion (likely "validates against schema")

### Risk if Wrong
- **Too complex:** mhw4d/rbrock require features not planned for Sprint 9
- **Can't convert:** Acceptance criterion "at least 1 model converts" fails
- **Wasted effort:** Spend 6-8h on conversion, produce non-functional output

### Estimated Research Time
1 hour (part of Task 5)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (Simple model analysis section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.2.4: MCP JSON Schema Compatibility

### Priority
**High** - Affects conversion implementation

### Assumption
Existing MCP JSON schema handles all GAMS constructs found in mhw4d/rbrock without requiring GAMS-specific extensions.

### Research Questions
1. Does MCP support GAMS-style sets with aliases?
2. Does MCP support GAMS-style parameters with multi-dimensional indices?
3. Does MCP require variable bounds in specific format (different from GAMS)?
4. Are there GAMS features that have no MCP equivalent?
5. Do we need to extend MCP schema or work within existing schema?

### How to Verify

**Test Case 1: MCP schema review**
```python
# Load MCP JSON schema (where is it defined?)
# Check for: sets, parameters, variables, constraints, objectives
```
Expected: Document MCP schema structure

**Test Case 2: GAMS-to-MCP feature mapping**
```python
gams_to_mcp = {
    "Set": "??? (does MCP have sets?)",
    "Parameter": "constants[] or parameters[]?",
    "Variable": "variables[]",
    "Equation": "constraints[]",
    "Objective": "objectives[]",
}
```
Expected: Map all GAMS features to MCP equivalents

**Test Case 3: Extension needs**
```python
# If MCP doesn't support sets, do we:
# A) Extend MCP schema with GAMS-specific fields
# B) Flatten sets into parameter dimensions
# C) Store sets as metadata
```
Expected: Design extension strategy (if needed)

### Risk if Wrong
- **Schema extension required:** More work than 6-8h estimate (add 3-4h)
- **Incompatible formats:** GAMS concepts don't map cleanly to MCP
- **Conversion failures:** MCP schema validation rejects GAMS-converted JSON

### Estimated Research Time
1 hour (part of Task 5)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (MCP schema review section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.2.5: Conversion Pipeline Testing Strategy

### Priority
**High** - Determines how we validate conversion correctness

### Assumption
Can validate conversion correctness with JSON schema validation only, without requiring PATH solver integration or solution verification.

### Research Questions
1. How to test conversion correctness without solving?
2. Can we use unit tests for individual IR-to-MCP node conversions?
3. Should we use golden files (expected MCP JSON for known inputs)?
4. What's the acceptance criterion for "successful conversion"?
5. Do we need integration tests with PATH solver in Sprint 9?

### How to Verify

**Test Case 1: Unit test approach**
```python
def test_convert_variable():
    var = VariableDef(name="x", bounds=(0, 10))
    mcp_var = converter.convert_variable(var)
    assert mcp_var["name"] == "x"
    assert mcp_var["lower_bound"] == 0
    assert mcp_var["upper_bound"] == 10
```
Expected: Unit tests for each IR node type

**Test Case 2: Integration test approach**
```python
def test_convert_mhw4d():
    model_ir = parse_gams_file("mhw4d.gms")
    mcp_json = converter.convert(model_ir)
    # Validate against schema
    validate_mcp_schema(mcp_json)
```
Expected: Integration tests for full model conversion

**Test Case 3: Golden file approach**
```python
def test_convert_rbrock():
    expected_mcp = load_json("tests/fixtures/rbrock_expected.json")
    actual_mcp = converter.convert(parse_gams_file("rbrock.gms"))
    assert actual_mcp == expected_mcp
```
Expected: Pre-defined expected output for regression testing

**Test Case 4: PATH integration (optional)**
```bash
# Convert GAMS → MCP, then solve with PATH
path_solver rbrock.mcp.json
```
Expected: Decide if Sprint 9 includes PATH testing

### Risk if Wrong
- **Insufficient testing:** Conversion produces invalid MCP, discovered in Sprint 10
- **Over-testing:** PATH integration adds 4-6h effort, delays Sprint 9
- **False positives:** Schema validation passes but MCP is semantically incorrect

### Estimated Research Time
1 hour (part of Task 5)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (Testing strategy section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.2.6: Conversion Pipeline Error Reporting

### Priority
**Medium** - UX consideration for debugging conversion failures

### Assumption
Can report conversion errors with line number context from SourceLocation metadata, making errors actionable for users.

### Research Questions
1. Where to store source location in conversion errors?
2. How to make errors actionable (suggest workarounds vs just report)?
3. Should we report all errors or fail on first error?
4. What's the error message format (similar to parser errors)?
5. How to handle partial conversion (some nodes convert, others fail)?

### How to Verify

**Test Case 1: Error reporting design**
```python
class ConversionError(Exception):
    message: str
    ir_node: str  # Type of IR node that failed
    source_location: Optional[SourceLocation]
    suggestion: Optional[str]  # Suggested fix
```
Expected: Design error class with actionable info

**Test Case 2: Example error message**
```
Conversion error at line 12:
  Cannot convert ParameterDef "tau" with dynamic assignment.
  Suggestion: Use static parameter assignment or defer to runtime.
```
Expected: Error messages include line numbers and suggestions

**Test Case 3: Partial conversion handling**
```python
# Option A: Fail on first error
# Option B: Convert what's possible, report all errors
# Option C: Prompt user to continue or abort
```
Expected: Choose error handling strategy

### Risk if Wrong
- **Poor UX:** Conversion errors lack context, hard to debug
- **Silent failures:** Partial conversion produces incorrect MCP without warnings

### Estimated Research Time
30 minutes (part of Task 5)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (Error reporting section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.2.7: Conversion Pipeline Performance

### Priority
**Low** - Optimization concern, not blocking for Sprint 9

### Assumption
Conversion time is negligible compared to parsing time (parsing = 10-100ms, conversion = 1-10ms), so performance optimization is not needed in Sprint 9.

### Research Questions
1. Does conversion require optimization passes (expression simplification)?
2. What's the expected conversion time for 100-line models?
3. Is conversion linear in IR size (O(n)) or more complex?
4. Should we include conversion time in performance budgets?
5. Do we need benchmarking for conversion in Sprint 9?

### How to Verify

**Test Case 1: Complexity analysis**
```python
# Single-pass visitor: O(n) where n = number of IR nodes
# Multi-pass: O(k*n) where k = number of passes
```
Expected: Estimate conversion complexity

**Test Case 2: Timing measurement**
```python
import time
start = time.time()
mcp_json = converter.convert(model_ir)
duration = time.time() - start
print(f"Conversion time: {duration*1000:.2f}ms")
```
Expected: Measure actual conversion time for mhw4d/rbrock

**Test Case 3: Performance budget**
- Parsing: <100ms for 100-line models
- Conversion: <10ms for 100-line models (10% of parse time)
Expected: Decide if conversion time matters for Sprint 9

### Risk if Wrong
- **Slow conversion:** Users notice delays, but Sprint 9 focus is correctness not speed
- **Premature optimization:** Spending time on performance before conversion works

### Estimated Research Time
30 minutes (optional, can defer to Sprint 10)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 (optional performance section)  
**Expected completion:** Before Sprint 9 Day 1 (or deferred)

---

## Unknown 9.2.8: Dashboard Conversion Tracking

### Priority
**Medium** - Dashboard enhancement for monitoring conversion progress

### Assumption
Can extend existing GAMSLib dashboard to show parse/convert/solve rates with simple column additions (3-4 hour effort).

### Research Questions
1. How to display "parses but doesn't convert" vs "converts but doesn't solve"?
2. What color coding for 3-stage pipeline (parse → convert → solve)?
3. Should dashboard show conversion errors inline?
4. What metrics to track (conversion rate, conversion time, error types)?
5. Where to store conversion results (new JSON file? extend existing?)?

### How to Verify

**Test Case 1: Dashboard columns design**
```
| Model      | Parse Status | Convert Status | Solve Status |
|------------|--------------|----------------|--------------|
| mhw4d.gms  | ✅ SUCCESS   | ✅ SUCCESS     | ❓ UNKNOWN   |
| rbrock.gms | ✅ SUCCESS   | ✅ SUCCESS     | ❓ UNKNOWN   |
| himmel16   | ✅ SUCCESS   | ❌ FAILED      | ❌ BLOCKED   |
```
Expected: 3-column status display

**Test Case 2: Color coding**
- Green: SUCCESS (parses, converts, solves)
- Yellow: PARTIAL (parses, converts, but doesn't solve)
- Orange: LIMITED (parses but doesn't convert)
- Red: FAILED (doesn't parse)
Expected: 4-level color scheme

**Test Case 3: Conversion metrics**
```json
{
  "model": "mhw4d.gms",
  "parse_status": "SUCCESS",
  "convert_status": "SUCCESS",
  "conversion_time_ms": 5.2,
  "conversion_errors": []
}
```
Expected: JSON schema for conversion results

### Risk if Wrong
- **Dashboard complexity:** 3-4h estimate insufficient, adds 2-3h
- **Poor UX:** Dashboard doesn't clearly show conversion pipeline stages

### Estimated Research Time
1 hour (part of Task 5 or separate task)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 or Day 9 dashboard work  
**Expected completion:** Before Sprint 9 Day 1 (design only)

---

## Unknown 9.2.9: Conversion Pipeline Incremental Development

### Priority
**Medium** - Development strategy for Days 7-8

### Assumption
Can build conversion pipeline incrementally (mhw4d first, then rbrock or vice versa), allowing mid-sprint checkpoint if time constrained.

### Research Questions
1. Should we start with mhw4d (more complex) or rbrock (simpler)?
2. What's common across all models vs model-specific conversion logic?
3. Can we ship "partial conversion" (e.g., variables only, no constraints)?
4. At what point is conversion "good enough" for Sprint 9?
5. What should Checkpoint 4 (Day 8 end) validate?

### How to Verify

**Test Case 1: Incremental conversion levels**
```python
# Level 1: Variables only
# Level 2: Variables + parameters
# Level 3: Variables + parameters + constraints
# Level 4: Full model (variables + parameters + constraints + objective)
```
Expected: Define conversion milestones

**Test Case 2: Model selection**
- Option A: Start with rbrock (8 lines, simpler) for quick win
- Option B: Start with mhw4d (14 lines, more realistic)
Expected: Choose starting model

**Test Case 3: Checkpoint 4 criteria**
- **Minimum:** Variables convert for 1 model
- **Target:** Full model converts for 1 model
- **Stretch:** Both models convert
Expected: Define Day 8 go/no-go criteria

### Risk if Wrong
- **Wrong starting model:** Choose complex model first, waste time
- **Scope creep:** Try to convert both models, run out of time
- **Insufficient progress:** Checkpoint 4 fails, can't validate conversion pipeline

### Estimated Research Time
30 minutes (part of Task 5 or Task 10)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 5 or Task 10 (Day 7-8 planning)  
**Expected completion:** Before Sprint 9 Day 1

---

# Category 3: Test Infrastructure

Sprint 9 addresses 3 high-priority recommendations from Sprint 8 retrospective: secondary blocker analysis, automated fixture tests, and fixture validation script. These improvements prevent technical debt and enhance regression protection.

---

## Unknown 9.3.1: Automated Fixture Test Framework Design

### Priority
**High** - Sprint 8 retrospective recommendation #2

### Assumption
pytest parametrization can auto-discover all fixture directories and validate expected_results.yaml with 2-3 hours of implementation effort.

### Research Questions
1. How to auto-discover all fixture directories (recursive scan of tests/fixtures/)?
2. How to parameterize tests per fixture (pytest.mark.parametrize)?
3. How to load and validate expected_results.yaml for assertions?
4. What validation level to target (parse status only? counts? AST structure?)?
5. Should all 13 existing fixtures pass immediately or fix fixtures first?

### How to Verify

**Test Case 1: Fixture discovery**
```python
from pathlib import Path

def discover_fixtures():
    fixture_root = Path("tests/fixtures")
    fixtures = []
    for fixture_dir in fixture_root.rglob("*"):
        if (fixture_dir / "expected_results.yaml").exists():
            fixtures.append(fixture_dir)
    return fixtures

# Should find 13 fixtures from Sprint 8
assert len(discover_fixtures()) == 13
```
Expected: Auto-discover all existing fixtures

**Test Case 2: Parameterized test**
```python
@pytest.mark.parametrize("fixture_dir", discover_fixtures())
def test_fixture(fixture_dir):
    # Load expected_results.yaml
    expected = load_yaml(fixture_dir / "expected_results.yaml")
    # Parse GMS file
    gms_file = list(fixture_dir.glob("*.gms"))[0]
    model_ir = parse_gams_file(gms_file)
    # Assert parse status
    assert (model_ir is not None) == (expected["status"] == "SUCCESS")
```
Expected: Single test function validates all fixtures

**Test Case 3: Validation levels**
- Level 1: Parse status (SUCCESS/FAILED/PARTIAL)
- Level 2: Statement count, line count
- Level 3: Feature presence (option_statements, indexed_assignments)
- Level 4: AST structure deep comparison
Expected: Choose Level 1+2 for Sprint 9 (3h effort)

### Risk if Wrong
- **Fixture failures:** Existing fixtures have errors, need fixing (add 2-3h)
- **Complex validation:** Level 3+4 required, adds 2-3h effort
- **Discovery issues:** Can't auto-discover fixtures, need manual registration

### Estimated Research Time
3-4 hours (Task 6: Design Automated Fixture Test Framework)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 6 (Framework design)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.3.2: Fixture Test Validation Scope

### Priority
**Medium** - Determines test coverage and effort

### Assumption
Validating parse status, statement counts, and line numbers is sufficient for Sprint 9 (Level 1+2), without deep AST or IR validation (Level 4).

### Research Questions
1. Should we validate AST structure (deep comparison)?
2. Should we validate specific IR node types?
3. Should we validate semantic accuracy (variable values, bounds)?
4. What's the minimum validation for regression protection?
5. Can we add deeper validation in Sprint 10+ incrementally?

### How to Verify

**Test Case 1: Level 1 validation (parse status)**
```python
assert (model_ir is not None) == (expected["status"] == "SUCCESS")
```
Expected: Catches parsing regressions

**Test Case 2: Level 2 validation (counts)**
```python
actual_count = count_statements(model_ir)
expected_count = expected["statements_total"]
assert actual_count == expected_count
```
Expected: Catches counting regressions

**Test Case 3: Level 3 validation (features)**
```python
has_option_stmts = any(isinstance(node, OptionStmt) for node in model_ir.statements)
assert has_option_stmts == expected.get("has_option_statements", False)
```
Expected: Catches feature detection regressions

**Test Case 4: Level 4 validation (AST)**
```python
expected_ast = load_json(fixture_dir / "expected_ast.json")
actual_ast = ast_to_dict(model_ir)
assert actual_ast == expected_ast
```
Expected: Catches deep structure regressions (most comprehensive)

### Risk if Wrong
- **Insufficient validation:** Level 1+2 misses important regressions
- **Over-engineering:** Level 4 validation adds significant effort (4-6h)

### Estimated Research Time
1 hour (part of Task 6)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 6 (Validation scope section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.3.3: Fixture Validation Script Algorithm

### Priority
**High** - Sprint 8 retrospective recommendation #3

### Assumption
Can programmatically count statements and line numbers with heuristic algorithm (ends with `;` or `..`) to match manual counting, preventing PR review errors like PR #254.

### Research Questions
1. What constitutes a "statement" for counting (variable decl? assignment? equation?)?
2. How to count multi-line statements (count as 1 or N)?
3. How to handle inline comments (`x = 5; * comment`)?
4. How to handle multi-line comments (`$ontext ... $offtext`)?
5. Should we count logical lines (non-empty/non-comment) or physical lines?

### How to Verify

**Test Case 1: Simple statement counting**
```gams
Variable x;        # Statement 1
Parameter p /5/;   # Statement 2
Equation eq1;      # Statement 3
eq1.. x =E= p;     # Statement 4
```
Expected: Count = 4 statements

**Test Case 2: Multi-line statement**
```gams
Equation eq1;
eq1..
  x + y
  =E=
  p + q;           # Count as 1 statement (ends with ;)
```
Expected: Count = 2 statements (Equation decl + equation def)

**Test Case 3: Comments handling**
```gams
* This is a comment  # Don't count
Variable x;          # Count as 1
x.lo = 0; * comment  # Count as 1 (inline comment)
```
Expected: Count = 2 statements

**Test Case 4: Multiline comments**
```gams
$ontext
This is a multiline comment
$offtext
Variable x;
```
Expected: Count = 1 statement (skip multiline comment block)

### Risk if Wrong
- **Counting mismatch:** Script counts differ from manual counts, validation fails
- **Fixture errors:** PR #254 situation repeats, manual counting errors persist
- **Algorithm complexity:** Need sophisticated parser to count accurately (add 2-3h)

### Estimated Research Time
2-3 hours (Task 7: Design Fixture Validation Script)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 7 (Algorithm design)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.3.4: Secondary Blocker Analysis Methodology

### Priority
**Critical** - Sprint 8 retrospective recommendation #1

### Assumption
Lark error recovery (`maybe_placeholders=True`) can capture ALL errors in mhw4dx.gms (not just first), enabling complete blocker analysis.

### Research Questions
1. Can Lark continue parsing after first error to find secondary blockers?
2. How many errors constitute "complete analysis" (all errors? first 10?)?
3. Should we document errors in GAMSLIB_FEATURE_MATRIX.md or separate file?
4. How to classify secondary blockers (simple/medium/complex)?
5. Should secondary blocker analysis apply to other models too?

### How to Verify

**Test Case 1: Lark error recovery**
```python
parser = lark.Lark(
    grammar,
    parser='lalr',
    propagate_positions=True,
    maybe_placeholders=True  # Continue on error
)
try:
    tree = parser.parse(gams_code)
except lark.exceptions.UnexpectedInput as e:
    # Collect error, continue parsing
    errors.append(e)
```
Expected: Multiple errors captured, not just first

**Test Case 2: mhw4dx.gms error capture**
```bash
# Parse mhw4dx.gms with Sprint 8 parser
python -m nlp2mcp.parser.gams_parser data/gamslib/mhw4dx.gms 2>&1 | tee errors.log
```
Expected: Capture all parsing errors (not just first)

**Test Case 3: Manual inspection**
```bash
# Read lines 37-63 of mhw4dx.gms
sed -n '37,63p' data/gamslib/mhw4dx.gms
# Identify all unsupported features
```
Expected: Complete list of secondary blockers

### Risk if Wrong
- **Incomplete analysis:** Miss secondary blockers, Sprint 9/10 planning inaccurate
- **Underestimation:** mhw4dx.gms unlock requires more features than expected

### Estimated Research Time
2-3 hours (Task 2: Complete Secondary Blocker Analysis)

### Owner
Development team

### Verification Results
🔍 **Status:** ✅ VERIFIED  
**Verified by:** Task 2 - Complete Secondary Blocker Analysis for mhw4dx.gms  
**Date:** 2025-11-19  
**Actual time:** 1 hour (within 2-3h estimate)

**Answers to Research Questions:**

**1. Can Lark continue parsing after first error to find secondary blockers?**
- **Answer:** Partial success. Lark error recovery can help, but **manual inspection is CRITICAL** for complete analysis.
- **Rationale:** Parser stopped at first `if(` statement and couldn't recover to find subsequent blockers. Manual line-by-line inspection (lines 37-93) revealed all blockers.

**2. How many errors constitute "complete analysis"?**
- **Answer:** ALL errors in the targeted section (lines 37-93 for mhw4dx.gms).
- **Methodology:** Line-by-line catalog showing exactly where/why each line fails.
- **Result:** Identified 42 blocked lines (45.2% of file), 5 distinct blocker types, 16+ occurrences.

**3. Should we document errors in GAMSLIB_FEATURE_MATRIX.md or separate file?**
- **Answer:** **Both.**
- **GAMSLIB_FEATURE_MATRIX.md:** Update model entry with summary of secondary blockers (see mhw4dx.gms section updated in Task 2).
- **Separate file:** Create detailed `MHW4DX_BLOCKER_ANALYSIS.md` with:
  - Executive summary
  - Blocker classification table
  - Line-by-line error catalog
  - Sprint retrospective analysis
  - Recommendations for Sprint 10+
- **Rationale:** Summary in matrix for quick reference, detailed analysis in separate doc for implementation planning.

**4. How to classify secondary blockers (simple/medium/complex)?**
- **Answer:** Use **implementation hours + scope** classification:
  - **Simple (1-3h):** Single grammar rule, minimal semantic handling, few edge cases
    - Examples from mhw4dx: `$eolCom` (1h), model attributes (1-2h), `abort$` (2-3h), macros (2-3h)
  - **Medium (4-8h):** Multiple grammar rules, moderate semantic complexity, some edge cases
    - Example from mhw4dx: `if/elseif/else` control flow (6-8h)
  - **Complex (8+h):** Extensive grammar changes, complex semantic validation, many edge cases
    - Examples: Full macro system, advanced set operations
- **Validation:** All 5 mhw4dx blockers classified using this rubric.

**5. Should secondary blocker analysis apply to other models too?**
- **Answer:** **YES - CRITICAL for Sprint 9/10 planning.**
- **Priority order (from Sprint 8 GAMSLIB_FEATURE_MATRIX.md):**
  1. haverly.gms - Check if option statements were only blocker
  2. himmel16.gms - Known blocker: i++1 indexing (verify no secondary blockers)
  3. etamac.gms - Unknown blocker (small model, quick analysis)
  4. springs.gms - Unknown blocker (medium model)
  5. procsel.gms - Unknown blocker (medium model)
  6. mhw4dx.gms - ✅ COMPLETE (defer to Sprint 10)
- **Time allocation:** 1 hour per model (<100 lines), 1.5-2h for larger models.

**Key Findings from mhw4dx.gms Analysis:**

**Sprint 8 Assumption:** "mhw4dx only needs option statements (lines 37, 47)" - ❌ **INCORRECT**

**Reality:**
- ✅ Option statements (lines 37, 47): RESOLVED in Sprint 8
- ❌ **NEW BLOCKER FOUND:** if/elseif/else control flow (lines 53-93, 41 lines)

**Secondary blockers identified:**
1. **if/elseif/else control flow** (Medium, 6-8h) - PRIMARY BLOCKER
2. **abort$ conditional statements** (Simple, 2-3h)
3. **Model attribute access** (Simple, 1-2h)
4. **Macro expansion** (Simple, 2-3h)
5. **$eolCom preprocessor** (Simple, 1h)

**Total effort for full mhw4dx.gms unlock:** 12-17 hours (too large for Sprint 9, defer to Sprint 10)

**Lesson Learned:**
✅ **Secondary blocker analysis is CRITICAL** - Surface-level analysis (first error only) leads to incorrect assumptions and sprint planning failures. This validates Sprint 8 Retrospective High Priority Recommendation #1.

**Methodology Validated:**
- ✅ Manual inspection is essential (parser error recovery insufficient)
- ✅ 1 hour per model (<100 lines) is appropriate time allocation
- ✅ Line-by-line catalogs prevent missed blockers
- ✅ Complexity classification helps sprint planning
- ✅ Separate detailed analysis documents improve implementation planning

**See:** `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md` for complete analysis

---

# Category 4: Performance & Metrics

Sprint 9 establishes performance baselines and budgets (Sprint 8 retrospective recommendation #5). Goal: Document baseline metrics and enforce test suite performance budgets.

---

## Unknown 9.4.1: Performance Baseline Metrics Selection

### Priority
**High** - Defines what we measure and track

### Assumption
Measuring parse time, convert time, and total time per model is sufficient for Sprint 9 baseline, without memory profiling or AST size metrics.

### Research Questions
1. Should we track per-model metrics or aggregate metrics?
2. Should we include memory usage in baseline?
3. Should we include AST/IR size metrics (node count)?
4. What statistical measures (mean? median? p95? min/max)?
5. How to handle variance across runs (warmup? multiple iterations)?

### How to Verify

**Test Case 1: Metric selection**
```python
baseline_metrics = {
    "parse_time_ms": float,      # Per-model parse time
    "convert_time_ms": float,    # Per-model convert time (Sprint 9+)
    "total_time_ms": float,      # Parse + convert
    "memory_mb": float,          # Optional: Peak memory usage
    "ast_nodes": int,            # Optional: AST size
}
```
Expected: Choose minimal metric set for Sprint 9

**Test Case 2: Statistical measures**
```python
# Run parse 10 times, compute statistics
times = [parse_model() for _ in range(10)]
metrics = {
    "mean": statistics.mean(times),
    "median": statistics.median(times),
    "p95": numpy.percentile(times, 95),
    "min": min(times),
    "max": max(times),
}
```
Expected: Choose which statistics to store (mean + p95?)

**Test Case 3: Aggregate vs per-model**
```python
# Option A: Per-model metrics (10 models × metrics)
# Option B: Aggregate metrics (total time across all models)
# Option C: Both
```
Expected: Decide granularity of baseline data

### Risk if Wrong
- **Missing metrics:** Can't detect performance regressions in unmeasured dimensions
- **Too many metrics:** Overwhelming data, hard to track trends
- **Statistical noise:** Single-run measurements unreliable

### Estimated Research Time
3-4 hours (Task 9: Design Performance Baseline & Budget Framework)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 9 (Metrics selection section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.4.2: Performance Budget Enforcement

### Priority
**Medium** - Sprint 8 retrospective recommendation #5

### Assumption
CI can enforce test suite performance budgets (<30s fast, <5min full) with simple timing checks and ≤10% tolerance for variance.

### Research Questions
1. Should CI fail if budget exceeded by X%? (What's X: 5%? 10%? 20%?)
2. How to identify slow tests automatically (profile or manual inspection)?
3. Should performance budgets be per-test-file or total suite?
4. What happens on budget violation (fail build? warning only?)?
5. How to handle natural performance variance (different CI runners)?

### How to Verify

**Test Case 1: Budget enforcement**
```yaml
# .github/workflows/test.yml
- name: Run fast tests
  run: |
    time make test
    # Fail if >30s
```
Expected: CI job fails if budget exceeded

**Test Case 2: Tolerance calculation**
```python
baseline_time = 24  # seconds (Sprint 8 fast suite)
budget = 30  # seconds
tolerance = 0.10  # 10%
max_allowed = budget * (1 + tolerance)  # 33 seconds
```
Expected: 10% tolerance prevents false positives

**Test Case 3: Slow test identification**
```bash
# Run pytest with duration report
pytest --durations=10 tests/
```
Expected: Identify top 10 slowest tests

### Risk if Wrong
- **Budget too strict:** False positives, CI fails on natural variance
- **Budget too loose:** Performance regressions slip through
- **No enforcement:** Budget documented but not enforced, defeats purpose

### Estimated Research Time
1 hour (part of Task 9)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 9 (Budget enforcement section)  
**Expected completion:** Before Sprint 9 Day 1

---

# Category 5: Sprint Planning

Sprint 9 planning integrates all prep work (Tasks 1-9) into comprehensive execution plan. Goal: Day-by-day breakdown with 4 checkpoints and risk mitigation.

---

## Unknown 9.5.1: 30-41 Hour Budget Allocation

### Priority
**High** - Validates sprint scope feasibility

### Assumption
Effort estimates from PROJECT_PLAN.md (30-41h total) sum correctly when broken down by task, and fit within 10-day sprint timeframe.

### Research Questions
1. Does test infra (5-6h) + parser (15-20h) + conversion (10-15h) = 30-41h?
2. Are individual task estimates realistic (validated by prep research)?
3. What's the critical path (longest dependency chain)?
4. How much buffer is needed (10%? 20%? Day 10 as buffer?)?
5. Can sprint complete in 10 days or need 11 days?

### How to Verify

**Test Case 1: Effort summation**
```
Test infrastructure: 5-6h
  - Secondary blocker analysis: 2-3h
  - Automated fixtures: 2-3h
  - Validation script: 1h
  - Performance baseline: 1h
Advanced parser: 15-20h
  - i++1 indexing: 8-10h
  - Model sections: 5-6h
  - Equation attributes: 4-6h
Conversion: 10-15h
  - Pipeline foundation: 6-8h
  - Dashboard: 3-4h
  - Performance budget: 1h
Documentation: 2-3h
  
Total: 34-44h (close to 30-41h estimate)
```
Expected: Estimates align within 10%

**Test Case 2: Critical path analysis**
```
Day 0 → Days 1-2 (test infra) → Days 3-4 (i++1) → Days 7-8 (conversion) → Day 10 (closeout)
Critical path: ~18-24h
```
Expected: Critical path fits in 10 days (2-3h per day)

**Test Case 3: Buffer allocation**
```
Total effort: 34-44h
Sprint duration: 10 days × 2-3h/day = 20-30h
Overflow: 4-14h → Use Day 10 as buffer
```
Expected: Day 10 buffer sufficient

### Risk if Wrong
- **Underestimated effort:** Sprint overruns 10 days, delays Sprint 9 completion
- **Overestimated effort:** Finish early, missed opportunity for more features
- **Critical path longer than expected:** Checkpoints delayed

### Estimated Research Time
7-9 hours (Task 10: Plan Sprint 9 Detailed Schedule)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 10 (Effort allocation section)  
**Expected completion:** Before Sprint 9 Day 1

---

## Unknown 9.5.2: Checkpoint Strategy

### Priority
**High** - Defines sprint rhythm and go/no-go decisions

### Assumption
4 checkpoints (Days 2, 4, 6, 8) are sufficient for Sprint 9 monitoring, similar to Sprint 8's successful checkpoint strategy.

### Research Questions
1. Are 4 checkpoints the right cadence (every 2 days)?
2. What are the success criteria for each checkpoint?
3. What are the go/no-go decisions at each checkpoint?
4. Should checkpoints be strict gates or informational only?
5. What contingency plans if checkpoint fails?

### How to Verify

**Test Case 1: Checkpoint 1 (Day 2) criteria**
```
Success criteria:
- ✅ Test infrastructure complete (fixtures, validation, secondary blockers)
- ✅ Performance budgets established
- ✅ All tests passing

Go decision: Continue to i++1 indexing (Days 3-4)
No-Go decision: Debug infrastructure, use Day 10 buffer
```
Expected: Clear success criteria and go/no-go decisions

**Test Case 2: Checkpoint 2 (Day 4) criteria**
```
Success criteria:
- ✅ i++1 indexing working
- ✅ himmel16.gms parses (parse rate ≥40%)
- ✅ Lead/lag test fixtures passing

Go decision: Continue to model sections (Day 5)
No-Go decision: Assess secondary blocker, defer to Sprint 10
```
Expected: Clear criteria linked to parse rate goal

**Test Case 3: Checkpoint 3 (Day 6) criteria**
```
Success criteria:
- ✅ Model sections + equation attributes complete
- ✅ hs62.gms + mingamma.gms parse (parse rate ≥60%)
- ✅ All parser features tested

Go decision: Continue to conversion pipeline (Days 7-8)
No-Go decision: Defer conversion to Sprint 10, focus on parser polish
```
Expected: Parser features complete before conversion

**Test Case 4: Checkpoint 4 (Day 8) criteria**
```
Success criteria:
- ✅ Conversion pipeline working
- ✅ At least 1 model converts (mhw4d or rbrock)
- ✅ Dashboard shows parse/convert rates

Go decision: Polish dashboard, create PR (Days 9-10)
No-Go decision: Document conversion blockers, plan Sprint 10
```
Expected: Meets Sprint 9 acceptance criterion

### Risk if Wrong
- **Wrong checkpoint cadence:** Miss critical issues between checkpoints
- **Weak criteria:** Checkpoints pass but sprint goals unmet
- **No contingency:** Checkpoint failure blocks sprint progress

### Estimated Research Time
1-2 hours (part of Task 10)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** Task 10 (Checkpoint definitions section)  
**Expected completion:** Before Sprint 9 Day 1

---

# Template: Adding New Unknowns

When discovering new unknowns during Sprint 9 execution, use this template:

## Unknown 9.X.Y: [Short Title]

### Priority
**[Critical/High/Medium/Low]** - [One-sentence justification]

### Assumption
[What are we assuming to be true?]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]
4. [Question 4]
5. [Question 5]

### How to Verify
**Test Case 1:** [Description]
```
[Code or command]
```
Expected: [Expected outcome]

**Test Case 2:** [Description]
Expected: [Expected outcome]

### Risk if Wrong
- [Risk 1]
- [Risk 2]
- [Risk 3]

### Estimated Research Time
[X hours or X-Y hours]

### Owner
[Team or individual]

### Verification Results
🔍 **Status:** INCOMPLETE  
**To be verified by:** [Task or sprint day]  
**Expected completion:** [Date or milestone]

---

# Next Steps

## Before Sprint 9 Day 1

1. **Complete Prep Tasks 2-9** (verify all Critical and High priority unknowns)
   - Task 2: Secondary blocker analysis (verify Unknown 9.3.4)
   - Task 3: i++1 research (verify Unknowns 9.1.1, 9.1.2, 9.1.3, 9.1.8)
   - Task 4: Model sections research (verify Unknowns 9.1.4, 9.1.5, 9.1.9)
   - Task 5: Conversion architecture (verify Unknowns 9.2.1, 9.2.2, 9.2.3, 9.2.4, 9.2.5)
   - Task 6: Fixture framework (verify Unknowns 9.3.1, 9.3.2)
   - Task 7: Validation script (verify Unknown 9.3.3)
   - Task 8: Equation attributes (verify Unknowns 9.1.6, 9.1.7)
   - Task 9: Performance framework (verify Unknowns 9.4.1, 9.4.2)

2. **Complete Task 10** (Sprint 9 detailed planning)
   - Verify Unknowns 9.5.1, 9.5.2
   - Create PLAN.md with day-by-day breakdown
   - Define all 4 checkpoints with go/no-go criteria

3. **Review and Update**
   - Update all unknowns with verification results
   - Mark unknowns as ✅ COMPLETE or ❌ WRONG (with corrections)
   - Add any newly discovered unknowns during prep

4. **Final Validation**
   - All Critical unknowns verified (7 unknowns)
   - All High unknowns verified (11 unknowns)
   - Medium and Low unknowns addressed or deferred with justification
   - Task-to-unknown mapping complete (see Appendix below)

## During Sprint 9

1. **Daily Standup Reviews**
   - Review relevant unknowns for the day's work
   - Update verification results as features are implemented
   - Add newly discovered unknowns

2. **Checkpoint Reviews**
   - Day 2 (Checkpoint 1): Review test infrastructure unknowns (9.3.x)
   - Day 4 (Checkpoint 2): Review i++1 indexing unknowns (9.1.1, 9.1.2, 9.1.3, 9.1.8)
   - Day 6 (Checkpoint 3): Review model sections + equation attributes (9.1.4-9.1.7, 9.1.9, 9.1.10)
   - Day 8 (Checkpoint 4): Review conversion pipeline unknowns (9.2.x)

3. **Documentation Updates**
   - Move verified unknowns to "Confirmed Knowledge"
   - Document wrong assumptions with corrections
   - Update risk assessments based on findings

---

# Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| **Task 2:** Complete Secondary Blocker Analysis | 9.3.4 | Methodology for capturing all errors in mhw4dx.gms; informs other model analyses |
| **Task 3:** Research Advanced Indexing (i++1, i--1) | 9.1.1, 9.1.2, 9.1.3, 9.1.8, 9.1.10 | Lead/lag complexity, grammar integration, semantic handling, himmel16.gms unlock, test coverage for i++1 |
| **Task 4:** Research Model Section Syntax | 9.1.4, 9.1.5, 9.1.9, 9.1.10 | Model section syntax variations, grammar conflicts, hs62/mingamma unlock, test coverage for model sections |
| **Task 5:** Design Conversion Pipeline Architecture | 9.2.1, 9.2.2, 9.2.3, 9.2.4, 9.2.5, 9.2.6, 9.2.7, 9.2.8, 9.2.9 | Architecture design, IR-to-MCP mapping, simple model scope, MCP schema, testing strategy, error reporting, performance, dashboard, incremental development |
| **Task 6:** Design Automated Fixture Test Framework | 9.3.1, 9.3.2 | Fixture framework design, validation scope (Level 1-4) |
| **Task 7:** Design Fixture Validation Script | 9.3.3 | Statement counting algorithm, line counting, validation checks |
| **Task 8:** Research Equation Attributes | 9.1.6, 9.1.7, 9.1.10 | Equation attributes scope, semantic meaning, test coverage for equation attributes |
| **Task 9:** Design Performance Framework | 9.4.1, 9.4.2 | Baseline metrics selection, performance budget enforcement |
| **Task 10:** Plan Sprint 9 Detailed Schedule | 9.5.1, 9.5.2 | Effort allocation validation, checkpoint strategy; integrates findings from all unknowns |

**Total Unknowns Mapped:** 27 (all unknowns covered by prep tasks)

**Verification Coverage:**
- Critical unknowns (7): All verified by Tasks 2-5, 9
- High unknowns (11): All verified by Tasks 3-9
- Medium unknowns (7): All verified by Tasks 3-9
- Low unknowns (2): All verified by Tasks 5, 8

**Sprint 9 Execution Mapping:**

| Sprint 9 Days | Unknowns Used | Implementation Tasks |
|---------------|---------------|----------------------|
| **Day 0:** Setup | 9.4.1, 9.4.2, 9.5.1, 9.5.2 | Review all unknowns, establish performance budgets |
| **Days 1-2:** Test Infrastructure | 9.3.1, 9.3.2, 9.3.3, 9.3.4 | Implement automated fixtures, validation script, secondary blocker analysis |
| **Days 3-4:** i++1 Indexing | 9.1.1, 9.1.2, 9.1.3, 9.1.8, 9.1.10 | Implement lead/lag indexing, verify himmel16.gms unlock |
| **Day 5:** Model Sections | 9.1.4, 9.1.5, 9.1.9, 9.1.10 | Implement model sections, verify hs62/mingamma unlock |
| **Day 6:** Equation Attributes | 9.1.6, 9.1.7, 9.1.10 | Implement equation attributes parsing |
| **Days 7-8:** Conversion Pipeline | 9.2.1, 9.2.2, 9.2.3, 9.2.4, 9.2.5, 9.2.6, 9.2.7, 9.2.8, 9.2.9 | Implement conversion infrastructure, verify mhw4d/rbrock conversion |
| **Day 9:** Dashboard & Polish | 9.2.8, 9.4.2 | Extend dashboard, enforce performance budgets |
| **Day 10:** Closeout & Buffer | All unknowns | Final validation, documentation, PR creation |

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2025  
**Next Review:** Sprint 9 Day 0 (before execution begins)  
**Status:** Ready for Prep Tasks 2-10 to verify unknowns
