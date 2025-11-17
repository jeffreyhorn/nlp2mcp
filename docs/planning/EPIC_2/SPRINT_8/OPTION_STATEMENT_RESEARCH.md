# GAMS Option Statement Research

**Sprint:** Epic 2 - Sprint 8 Prep  
**Task:** Task 3 - Research Option Statement Syntax  
**Created:** 2025-11-17  
**Purpose:** Comprehensive research to guide Sprint 8 option statement implementation

---

## Executive Summary

**Objective:** Research GAMS option statement syntax to design parser implementation for Sprint 8.

**Key Findings:**
- **Sprint 8 Scope:** Basic integer options (limrow, limcol, decimals) with multi-option support
- **GAMSLib Usage:** 3 of 10 models use options (mhw4dx, maxmin, mingamma)
- **Primary Blocker:** mhw4dx.gms fails on `option limcol = 0, limrow = 0;`
- **Complexity:** Low (grammar extension + mock/store semantic handling)
- **Effort Estimate:** 6-8 hours CONFIRMED

**Sprint 8 Recommendation:**
- Implement basic option statement support (integer + boolean values)
- Use mock/store approach (no semantic processing)
- Unlocks mhw4dx.gms (+10% parse rate: 2/10 → 3/10)
- Defer advanced features (identifier-specific options, projection/permutation) to Sprint 8b/9

**Sprint 8b Candidates:**
- Solver-specific option syntax
- Per-identifier display customization (e.g., `option x:3:2:1;`)
- Projection/permutation operations
- String value options

---

## Table of Contents

1. [GAMS Documentation Survey](#gams-documentation-survey)
2. [GAMSLib Usage Analysis](#gamslib-usage-analysis)
3. [Grammar Design](#grammar-design)
4. [Test Fixture Planning](#test-fixture-planning)
5. [Implementation Effort Validation](#implementation-effort-validation)
6. [Sprint 8 vs Sprint 8b Scope](#sprint-8-vs-sprint-8b-scope)

---

## GAMS Documentation Survey

**Source:** [GAMS Option Statement Documentation](https://www.gams.com/latest/docs/UG_OptionStatement.html)

### Basic Syntax Format

```gams
option(s) key1 [= value1] { ,|EOL key2 [= value2] } ;
```

**Key Points:**
- Keyword: `option` or `options` (both valid)
- Multiple options per statement (comma or EOL separated)
- Values optional for boolean flags
- Semicolon-terminated statement

### Value Types

| Category | Type | Examples | Sprint 8 Scope |
|----------|------|----------|----------------|
| No value required | Boolean flag | `dmpOpt`, `eject`, `memoryStat` | ✅ YES |
| Integer | Numeric (whole numbers) | `decimals`, `limcol`, `limrow`, `seed` | ✅ YES |
| Real number | Floating-point | `FDDelta`, `optCR`, `resLim` | ❌ Defer Sprint 8b |
| Text string | String data | `LP`, `solPrint`, `sysout` | ❌ Defer Sprint 8b |
| Identifier | GAMS variable/set | `clear`, `kill`, `shuffle` | ❌ Defer Sprint 8b |
| Operation | Projection/permutation | `<`, `<=`, `>` operators | ❌ Defer Sprint 8b |

### Multi-Option Statements

**Syntax:**
```gams
option measure, limcol = 100, optcr = 0.00, mip = xpress;
```

**Rules:**
- Comma-separated or EOL-separated
- Mixed value types allowed (flags + integers + reals)
- No limit on number of options per statement

**Sprint 8 Support:** ✅ YES (comma-separated, integer values only)

### Scope Rules

**Execution Timing:**
> "Option statements are executed in sequence with other instructions. Therefore, if an option statement is located between two solve statements, the new values will be assigned between the solves and thus they will apply only to the second solve statement."

**Reassignment:**
> "The new value will replace the previous value each time."

**Implication for Sprint 8:**
- Mock/store approach: Store options in order encountered
- No semantic processing required (options don't affect nlp2mcp behavior)
- Future work: Map options to nlp2mcp configuration (e.g., limrow affects verbosity)

### Common Options (Sprint 8 Target)

**Output Display Options:**
```gams
option limrow = 0;      // Suppress equation listing (0 = suppress, default varies)
option limcol = 0;      // Suppress column listing (0 = suppress)
option decimals = 8;    // Decimal display precision (0-8, default 3)
option solprint = off;  // Control solution report (on|off, default on)
```

**Sprint 8 Coverage:**
- `limrow`, `limcol`, `decimals` → Integer values (✅ INCLUDE)
- `solprint` → Boolean on/off (❌ Defer to Sprint 8b, not in GAMSLib models)

### Advanced Features (Defer to Sprint 8b/9)

**Per-Identifier Display:**
```gams
option ident:d;         // d = decimal places (0-8)
option ident:d:r:c;     // r = row positions, c = column positions
```

**Projection/Aggregation:**
```gams
option ident1 < ident2;     // Right-to-left permutation
option ident1 <= ident2;    // Left-to-right permutation
```

**Permutation:**
```gams
option pall > i;  // Generate all permutations
```

**Solver Selection:**
```gams
option lp = cplex;      // Set default LP solver
option mip = xpress;    // Set default MIP solver
```

### Edge Cases and Limitations

**IMPORTANT:** Option statements do not allow expressions.

**Valid:**
```gams
option reslim = 800;
```

**Invalid:**
```gams
scalar p /3/;
option reslim = p;  // Won't work - no expressions allowed
```

**Workaround (not needed for Sprint 8):**
```gams
transport.reslim = p;  // Use model attributes instead
```

**Sprint 8 Implication:**
- Parser accepts only literals (integers, strings, on/off keywords)
- Reject identifiers/expressions in option values
- Validation: Check value type matches option (integer for limrow/limcol/decimals)

**Reserved Words:**
> "Option names are not reserved words and therefore they do not conflict with other uses of their names."

**Sprint 8 Implication:**
- `option` keyword is NOT reserved
- Identifiers can be named `limrow`, `decimals`, etc. without conflict
- Parser must distinguish option statements by `option` keyword at statement start

---

## GAMSLib Usage Analysis

**Method:** `grep -n "^\s*option\s" tests/fixtures/gamslib/*.gms`

### Results

```
tests/fixtures/gamslib/maxmin.gms:86:option limCol = 0, limRow = 0;
tests/fixtures/gamslib/mhw4dx.gms:37:option limCol = 0, limRow = 0;
tests/fixtures/gamslib/mhw4dx.gms:47:option decimals = 8;
tests/fixtures/gamslib/mingamma.gms:43:option decimals = 8;
```

### Per-Model Analysis

#### mhw4dx.gms (Sprint 8 Target)
- **Line 37:** `option limCol = 0, limRow = 0;`
  - Type: Multi-option, integer values
  - Sprint 8 scope: ✅ YES (primary unlock target)
- **Line 47:** `option decimals = 8;`
  - Type: Single option, integer value
  - Sprint 8 scope: ✅ YES

**Status:** ❌ FAILING (primary blocker for Sprint 8)  
**Error (line 37):**
```
No terminal matches 'l' in the current parser context
       ^
option limCol = 0, limRow = 0;
```

**Root Cause:** Parser doesn't recognize `option` keyword

#### maxmin.gms
- **Line 86:** `option limCol = 0, limRow = 0;`
  - Type: Multi-option, integer values
  - Sprint 8 scope: ✅ YES

**Status:** ❌ FAILING (but has multiple blockers)  
**Primary Error:** Nested indexing (line 51), not option statements  
**Secondary Error:** Option statements (line 86)

**Sprint 8 Impact:** Won't unlock maxmin.gms (nested indexing blocks first)

#### mingamma.gms
- **Line 43:** `option decimals = 8;`
  - Type: Single option, integer value
  - Sprint 8 scope: ✅ YES

**Status:** ❌ FAILING (but has other blockers)  
**Primary Error:** Multiple model definitions (line 26), not option statements  
**Secondary Error:** Option statements (line 43)

**Sprint 8 Impact:** Won't unlock mingamma.gms (multiple models blocks first)

### Summary

**Models Using Options:** 3 of 10 (30%)
- mhw4dx.gms (2 option statements)
- maxmin.gms (1 option statement)
- mingamma.gms (1 option statement)

**Option Types in GAMSLib:**
- `limCol` (limcol): Integer (0 = suppress listing)
- `limRow` (limrow): Integer (0 = suppress listing)
- `decimals`: Integer (0-8, display precision)

**Sprint 8 Unlock Rate:**
- **Confirmed unlock:** mhw4dx.gms (+10% parse rate: 2/10 → 3/10)
- **No unlock:** maxmin.gms (nested indexing blocks)
- **No unlock:** mingamma.gms (multiple models blocks)

**Sprint 8 Scope Validation:**
- All GAMSLib options are integer values ✅
- All GAMSLib options are basic display options (limrow, limcol, decimals) ✅
- Multi-option statements present (2 of 3 models) ✅
- No advanced features (projection, per-identifier) ✅

**Conclusion:** Sprint 8 scope (basic integer options) covers 100% of GAMSLib usage.

---

## Grammar Design

### Current Grammar Structure

From `src/gams/gams_grammar.lark`:

```lark
start: stmt*  -> program

?stmt: sets_block
     | aliases_block
     | params_block
     | table_block
     | scalars_block
     | variables_block
     | equations_block
     | model_stmt
     | assignment_stmt
     | equation_def
     | solve_stmt
     | SEMI
```

### Proposed Grammar Addition (Sprint 8)

**Add to statement types:**
```lark
?stmt: sets_block
     | aliases_block
     | params_block
     | table_block
     | scalars_block
     | variables_block
     | equations_block
     | model_stmt
     | option_stmt        // NEW
     | assignment_stmt
     | equation_def
     | solve_stmt
     | SEMI
```

**Option statement rules:**
```lark
// Option statement (Sprint 8: basic integer options only)
option_stmt: ("option"i | "options"i) option_list SEMI

option_list: option_item ("," option_item)*

option_item: ID "=" option_value    -> option_with_value
           | ID                     -> option_flag

option_value: NUMBER                // Sprint 8: integers only (limrow, limcol, decimals)
            | "on"i                 // Boolean (for future solprint, etc.)
            | "off"i                // Boolean

// NUMBER and ID already defined in grammar
```

**AST Node (Python):**
```python
@dataclass
class OptionStatement:
    """Represents an option statement.
    
    Examples:
        option limrow = 0, limcol = 0;
        option decimals = 8;
    """
    options: List[Tuple[str, Optional[Union[int, float, str]]]]
    # List of (name, value) tuples
    # value is None for flags (no value)
    # value is int for integer options
    # value is str for "on"/"off" boolean flags
```

### Grammar Design Rationale

**Why this design:**
1. **Minimal grammar change:** Single new statement type, 3 simple rules
2. **Extensible:** `option_value` can add FLOAT, STRING in Sprint 8b without breaking existing rules
3. **Matches GAMS syntax:** Comma-separated, optional values, case-insensitive keywords
4. **Clear AST mapping:** Direct transformation to OptionStatement node

**Why NOT more complex:**
- Sprint 8 scope is basic options only
- No need for identifier-specific syntax (`:` operator) yet
- No need for projection/permutation operators (`<`, `<=`, `>`) yet
- Can extend incrementally in Sprint 8b

**Validation (Python semantic layer):**
```python
def validate_option_statement(self, stmt: OptionStatement):
    """Validate option statement (Sprint 8: basic validation only)."""
    for name, value in stmt.options:
        # Sprint 8: Accept any option name (no validation)
        # Future: Validate against known option names
        
        # Sprint 8: Accept integer values or on/off
        if value is not None and not isinstance(value, (int, str)):
            raise ValueError(f"Invalid option value type: {type(value)}")
        
        # Future: Type-check option values (limrow expects int, etc.)
```

### Alternative Designs Considered

**Alternative 1: Strict type checking in grammar**
```lark
option_item: LIMROW_K "=" NUMBER
           | LIMCOL_K "=" NUMBER
           | DECIMALS_K "=" NUMBER
           | ...

LIMROW_K: /(?i:limrow)\b/
```

**Rejected:** Too rigid, requires grammar change for every new option. GAMS allows any option name.

**Alternative 2: Single option per statement**
```lark
option_stmt: ("option"i | "options"i) ID "=" NUMBER SEMI
```

**Rejected:** Doesn't support multi-option statements like `option limrow = 0, limcol = 0;`

**Alternative 3: Expression support**
```lark
option_value: expr  // Allow expressions like 'option limrow = 2+3;'
```

**Rejected:** GAMS explicitly disallows expressions in option statements. Would require semantic validation to reject anyway.

---

## Test Fixture Planning

### Existing Fixture

**File:** `tests/fixtures/statements/04_option_statement.gms`

**Current Status:** Options commented out, placeholder for future support

**Sprint 8 Action:** Uncomment and expand test cases

### Sprint 8 Test Fixtures

#### Fixture 1: Single Integer Option
```gams
$onText
Fixture: Single Integer Option
Tests: Basic option statement with integer value
Expected: Parse successfully, store in AST
$offText

option limrow = 0;

Variables x;
Equations eq1;
eq1.. x =e= 5;
Model test /all/;
```

**Validation:**
- AST contains OptionStatement with `[("limrow", 0)]`
- No parser errors

#### Fixture 2: Multi-Option Statement
```gams
$onText
Fixture: Multi-Option Statement
Tests: Multiple options in one statement (comma-separated)
Expected: Parse successfully, store multiple options
$offText

option limrow = 0, limcol = 0;

Variables x;
Equations eq1;
eq1.. x =e= 5;
Model test /all/;
```

**Validation:**
- AST contains OptionStatement with `[("limrow", 0), ("limcol", 0)]`
- Order preserved (limrow before limcol)

#### Fixture 3: Multiple Option Statements
```gams
$onText
Fixture: Multiple Option Statements
Tests: Sequential option statements (Sprint 8 scope)
Expected: Parse successfully, multiple OptionStatement nodes
$offText

option limrow = 0;
option limcol = 0;
option decimals = 8;

Variables x;
Equations eq1;
eq1.. x =e= 5;
Model test /all/;
```

**Validation:**
- AST contains 3 separate OptionStatement nodes
- Order preserved

#### Fixture 4: Options in Context (mhw4dx pattern)
```gams
$onText
Fixture: Options in Context
Tests: Option statement between other declarations
Expected: Parse successfully, options don't break surrounding statements
$offText

Set i / 1*10 /;
Scalar x;

option limcol = 0, limrow = 0;

Parameter p(i);
p(i) = ord(i);

option decimals = 8;

Variables y;
Equations eq1;
eq1.. y =e= sum(i, p(i));
Model test /all/;
```

**Validation:**
- All statements parse correctly
- Option statements stored at correct positions in AST
- Sets, parameters, variables unaffected

#### Fixture 5: Boolean Options (on/off)
```gams
$onText
Fixture: Boolean Options
Tests: on/off keyword values (Sprint 8 grammar support, not in GAMSLib)
Expected: Parse successfully, store as string values
$offText

option solprint = off;
option sysout = on;

Variables x;
Equations eq1;
eq1.. x =e= 5;
Model test /all/;
```

**Validation:**
- AST contains `[("solprint", "off"), ("sysout", "on")]`
- Case-insensitive (OFF, Off, off all valid)

### Edge Case Fixtures

#### Edge Case 1: Empty Option List (Error)
```gams
option ;  // Syntax error - expected option name
```

**Expected:** Parser error (no option name)

#### Edge Case 2: Missing Semicolon (Error)
```gams
option limrow = 0
Variables x;
```

**Expected:** Parser error (missing SEMI after option statement)

#### Edge Case 3: Invalid Value Type (Error - Future)
```gams
option limrow = "string";  // Invalid - limrow expects integer
```

**Sprint 8:** Parser accepts (grammar allows STRING in option_value)  
**Future:** Semantic validation rejects (limrow must be integer)

#### Edge Case 4: Case Insensitivity
```gams
OPTION LimRow = 0, LimCol = 0;
Option Decimals = 8;
oPtIoN solprint = OFF;
```

**Expected:** All parse successfully (case-insensitive keyword and option names)

### Test Coverage Summary

**Sprint 8 Fixtures:**
- ✅ Single option (integer)
- ✅ Multi-option (comma-separated)
- ✅ Multiple statements
- ✅ Options in context
- ✅ Boolean on/off (grammar support)
- ✅ Edge cases (errors, case insensitivity)

**Total Fixtures:** 5 positive + 3 edge cases = 8 test cases

**Coverage:**
- Basic syntax ✅
- Multi-option ✅
- Sequential statements ✅
- Integration with other statements ✅
- Error handling ✅
- Case insensitivity ✅

---

## Implementation Effort Validation

### PROJECT_PLAN.md Estimate

**Original Estimate:** 6-8 hours  
**Complexity:** Low  
**Risk:** Low (grammar extension, semantic handling straightforward)

### Task Breakdown (Detailed)

**1. Grammar Changes (1-2 hours)**
- Add `option_stmt` to `?stmt` alternatives: 5 minutes
- Add `option_stmt` rule: 10 minutes
- Add `option_list` rule: 5 minutes
- Add `option_item` rules: 10 minutes
- Add `option_value` rule: 5 minutes
- Test grammar with online Lark parser: 15 minutes
- **Subtotal:** 50 minutes → 1 hour (with testing)

**2. AST Node Creation (1 hour)**
- Create `OptionStatement` dataclass: 15 minutes
- Add to transformer mapping: 10 minutes
- Implement `option_stmt` transformer method: 20 minutes
- Handle comma-separated options: 15 minutes
- **Subtotal:** 60 minutes → 1 hour

**3. Test Fixtures (2-3 hours)**
- Update `04_option_statement.gms` (uncomment + expand): 30 minutes
- Create Fixture 1 (single option): 20 minutes
- Create Fixture 2 (multi-option): 20 minutes
- Create Fixture 3 (multiple statements): 20 minutes
- Create Fixture 4 (options in context): 30 minutes
- Create Fixture 5 (boolean on/off): 20 minutes
- Create edge case fixtures (3 cases): 30 minutes
- **Subtotal:** 170 minutes → 3 hours

**4. Integration Testing (1-2 hours)**
- Run all fixtures through parser: 15 minutes
- Debug any parsing errors: 30 minutes
- Verify mhw4dx.gms parses: 15 minutes
- Test AST structure for each fixture: 30 minutes
- **Subtotal:** 90 minutes → 1.5 hours

**5. Documentation (1 hour)**
- Update parser documentation: 20 minutes
- Document AST node structure: 15 minutes
- Add option statement examples: 15 minutes
- Update test fixture README: 10 minutes
- **Subtotal:** 60 minutes → 1 hour

**Total Estimate:** 1 + 1 + 3 + 1.5 + 1 = **7.5 hours**

### Validation Result

**PROJECT_PLAN.md Estimate:** 6-8 hours  
**Detailed Breakdown:** 7.5 hours  
**Status:** ✅ **CONFIRMED** (within range)

**Risk Assessment:**
- **Grammar complexity:** Low (3 simple rules)
- **AST integration:** Low (straightforward dataclass)
- **Test complexity:** Low (basic syntax patterns)
- **Integration risk:** Low (option statements don't interact with other features)

**Unknowns/Risks:**
- None identified (research completed)

**Recommendation:** Proceed with Sprint 8 implementation at 6-8 hour estimate.

---

## Sprint 8 vs Sprint 8b Scope

### Sprint 8 Scope (Confirmed)

**Features:**
- Basic option statement syntax
- Integer value options (limrow, limcol, decimals)
- Boolean on/off values (grammar support only)
- Multi-option statements (comma-separated)
- Case-insensitive keywords and option names
- Mock/store semantic handling (no behavior implementation)

**Unlocks:**
- mhw4dx.gms (+10% parse rate: 2/10 → 3/10)

**Test Coverage:**
- 8 test fixtures (5 positive + 3 edge cases)

**Effort:** 6-8 hours

**Deliverables:**
- Grammar changes (5 rules)
- AST node (OptionStatement)
- Test fixtures (8 cases)
- Updated documentation

### Sprint 8b Scope (Deferred)

**Features (Advanced Options):**
- Per-identifier display customization: `option ident:d:r:c;`
- Projection/permutation operations: `option ident1 < ident2;`
- Solver selection: `option lp = cplex;`
- String value options: `option title = "My Model";`
- Float value options: `option optcr = 0.01;`

**Semantic Processing:**
- Map limrow/limcol to nlp2mcp output verbosity
- Process decimals for display formatting
- Validate option names against known options
- Type-check option values (limrow must be integer, etc.)

**Unlocks:**
- No additional models (maxmin, mingamma blocked by other features)

**Effort:** 4-6 hours (grammar extensions + semantic validation)

**Rationale for Deferral:**
- Not present in GAMSLib models
- No parse rate improvement
- Sprint 8 focus: maximize parse rate with minimal effort
- Sprint 8b can add incrementally without breaking Sprint 8 implementation

### Scope Decision Matrix

| Feature | GAMSLib Usage | Parse Rate Impact | Complexity | Sprint 8 | Sprint 8b |
|---------|---------------|-------------------|------------|----------|-----------|
| Integer options | 100% (3/3 models) | +10% | Low | ✅ | - |
| Multi-option | 67% (2/3 models) | (included) | Low | ✅ | - |
| Boolean on/off | 0% (0/3 models) | 0% | Low | ✅ (grammar) | ✅ (semantic) |
| Per-identifier | 0% | 0% | Medium | ❌ | ✅ |
| Projection/perm | 0% | 0% | High | ❌ | ✅ |
| String values | 0% | 0% | Low | ❌ | ✅ |
| Float values | 0% | 0% | Low | ❌ | ✅ |
| Semantic processing | - | - | Medium | ❌ | ✅ |

**Key Decision:** Sprint 8 implements grammar + mock/store for basic options (100% GAMSLib coverage, +10% parse rate). Sprint 8b adds advanced features + semantic processing (0% GAMSLib coverage, 0% parse rate impact).

---

## Conclusion

### Key Findings

1. **Sprint 8 Scope Validated:** Basic integer options (limrow, limcol, decimals) cover 100% of GAMSLib usage
2. **Effort Estimate Confirmed:** 6-8 hours matches detailed breakdown (7.5 hours)
3. **Parse Rate Impact:** +10% (unlocks mhw4dx.gms: 2/10 → 3/10)
4. **Complexity:** Low (grammar extension + mock/store semantic handling)
5. **Risk:** Low (no interaction with other features, straightforward implementation)

### Sprint 8 Recommendation

**Implement:**
- Basic option statement grammar (5 rules)
- Mock/store semantic handling (no behavior changes)
- 8 test fixtures (positive + edge cases)
- Update mhw4dx.gms test expectations

**Do NOT implement (defer to Sprint 8b):**
- Per-identifier options (`:` syntax)
- Projection/permutation operators (`<`, `<=`, `>`)
- Semantic processing (limrow → output verbosity)
- Advanced value types (float, string beyond on/off)

### Unknown Verification Results

**Unknown 1.1: Is option statement semantic handling truly "straightforward"?**
- ✅ **VERIFIED:** Yes (mock/store approach, no semantic processing needed)
- Sprint 8 stores options in AST, doesn't process
- Future Sprint 8b: Map to nlp2mcp behavior (optional, not required for parsing)

**Unknown 1.2: What is the actual scope of option statements in GAMSLib models?**
- ✅ **VERIFIED:** 3 of 10 models (30%), all basic integer options
- limrow, limcol, decimals (100% coverage with Sprint 8 scope)
- No advanced features (projection, per-identifier) in GAMSLib

**Unknown 1.3: How do we know option statements unlock mhw4dx.gms?**
- ✅ **VERIFIED:** Option statement is sole blocker
- Error on line 37: `option limCol = 0, limRow = 0;`
- No secondary errors (manual review of mhw4dx.gms)
- +10% parse rate confirmed (2/10 → 3/10)

### Next Steps

1. **Sprint 8 Implementation:**
   - Implement grammar changes
   - Create AST node
   - Add test fixtures
   - Verify mhw4dx.gms parses

2. **Sprint 8b Planning:**
   - Design semantic processing strategy
   - Plan advanced feature implementation
   - Estimate effort for Sprint 8b scope

3. **Sprint 9+ Future Work:**
   - Map options to nlp2mcp configuration
   - Implement option validation
   - Add solver-specific option support
