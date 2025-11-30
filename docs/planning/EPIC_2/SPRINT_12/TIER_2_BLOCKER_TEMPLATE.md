# Tier 2 Blocker Analysis Template

**Sprint:** Epic 2 - Sprint 12 Prep Task 8  
**Created:** 2025-11-30  
**Purpose:** Systematic template for analyzing Tier 2 parse failures to guide implementation priority

---

## Overview

This template provides a systematic framework for analyzing Tier 2 model parse failures, estimating implementation effort, and prioritizing blockers for Sprint 12 Days 4-6 (6h total budget).

### Key Principles

1. **Frequency-Driven Prioritization:** Blockers affecting multiple models have higher priority
2. **Effort-Bounded Selection:** Total implementation must fit within 6h budget
3. **Consistent Categorization:** All blockers analyzed using same schema
4. **Implementation Focus:** Capture information needed for parser changes

---

## Classification Schema

### Frequency

Number of Tier 2 models affected by this blocker:

- **1 model:** Low frequency (Priority Score: 10)
- **2-3 models:** Medium frequency (Priority Score: 25)
- **4-5 models:** High frequency (Priority Score: 45)
- **6+ models:** Very high frequency (Priority Score: 65)

### Complexity

Estimated implementation effort:

- **Simple (1-2h):** Lexer/grammar-only changes, minimal AST impact
  - Examples: Special chars in identifiers, alias syntax variations
  - Complexity Score: 1

- **Medium (3-5h):** Grammar + AST + tests, moderate scoping changes
  - Examples: Inline descriptions, predefined constants, model attributes
  - Complexity Score: 3

- **Hard (6-10h):** Complex grammar, new AST nodes, semantic analysis
  - Examples: Table data structures, loop constructs, conditional compilation
  - Complexity Score: 6

- **Very Hard (>10h):** Major parser refactoring or deferred features
  - Examples: Macro preprocessor, put file I/O, complex indexing chains
  - Complexity Score: 10

### Category

Blocker type for organization:

- **Syntax:** Lexer or grammar patterns (e.g., identifier rules, statement forms)
- **Control Flow:** Loops, conditionals, branches
- **Data Structure:** Tables, multi-dimensional data, complex assignments
- **Directive:** Preprocessor commands ($if, $include, $macro)
- **Semantic:** Symbol resolution, scoping, type checking
- **Other:** Miscellaneous or hybrid patterns

### Criticality

Impact on Sprint 12 ≥50% parse rate goal:

- **Must-have:** Required to reach ≥50% parse rate (5+ models)
- **Nice-to-have:** Improves parse rate but not critical for goal
- **Stretch:** Low priority, only if time permits

---

## Priority Formula

```
Priority Score = (Frequency Score) + (5 - Complexity Score)
```

### Rationale

- **High frequency + Low complexity = Highest priority**
  - Example (hypothetical maximum): 5 models × Simple = 45 + (5-1) = 49  
    _(Note: No actual blocker currently matches this profile in this sprint.)_
  - Example (actual highest-priority blocker): 3 models × Medium = 25 + (5-3) = 27 (inline_descriptions)
  
- **Low frequency + Low complexity = Medium priority**
  - Example: 1 model × Simple = 10 + (5-1) = 14
  
- **High frequency + High complexity = Medium-High priority**
  - Example: 5 models × Hard = 45 + (5-6) = 44
  
- **Low frequency + High complexity = Lowest priority**
  - Example: 1 model × Very Hard = 10 + (5-10) = 5

### Priority Bands

- **≥40:** **HIGH** - Implement first (high frequency blockers)
- **20-39:** **MEDIUM** - Implement if time permits after HIGH
- **<20:** **LOW** - Defer to future sprints unless trivial

---

## Prioritization Algorithm

### Step 1: Analyze All Blockers

For each Tier 2 model parse failure:
1. Identify root cause blocker pattern
2. Fill out blocker template (see below)
3. Calculate priority score

### Step 2: Deduplicate and Aggregate

1. Group models by blocker pattern
2. Update frequency counts (models per blocker)
3. Recalculate priority scores with updated frequency

### Step 3: Sort by Priority

1. Sort blockers by priority score (descending)
2. Within same priority, sort by complexity (ascending - easier first)

### Step 4: Cumulative Budget Selection

```
total_effort = 0
selected_blockers = []

for blocker in sorted_blockers:
    if total_effort + blocker.effort <= 6h:
        selected_blockers.append(blocker)
        total_effort += blocker.effort
    else:
        break  # Budget exhausted
```

### Step 5: Implementation Order

Implement selected blockers in priority order:
1. HIGH priority blockers first (≥40 score)
2. MEDIUM priority blockers next (20-39 score)
3. Stop when 6h budget consumed

---

## Blocker Template

Use this template for each unique blocker pattern:

```markdown
## Blocker: [Blocker Name]

### Classification

**Frequency:** [1 / 2-3 / 4-5 / 6+] models  
**Affected Models:** [model1.gms, model2.gms, ...]  
**Complexity:** [Simple / Medium / Hard / Very Hard]  
**Category:** [Syntax / Control Flow / Data Structure / Directive / Semantic / Other]  
**Criticality:** [Must-have / Nice-to-have / Stretch]  
**Priority Score:** [Calculated: (Frequency Score) + (5 - Complexity Score)]

### Error Message

```
[Paste actual parser error message from logs]
```

### Example Syntax

```gams
[Paste minimal example from failing model]
```

### GAMS Manual Reference

- **Section:** [e.g., "2.4 Set Declarations"]
- **Page:** [e.g., "User's Guide p. 45"]
- **Link:** [URL to online GAMS documentation]

### Complexity Estimate

**Effort:** [X hours]

**Rationale:**
[Explain why this complexity level - what parser components need changes]

**Breakdown:**
- Lexer changes: [X min]
- Grammar rules: [X min]
- AST nodes: [X min]
- Semantic analysis: [X min]
- Tests: [X min]
- Documentation: [X min]

### Parser Changes Needed

- [ ] Lexer: [Describe token changes if any]
- [ ] Grammar: [Describe production rules to add/modify]
- [ ] AST: [Describe new node types or modifications]
- [ ] Semantic: [Describe symbol table or type checking changes]
- [ ] Tests: [Describe test coverage needed]
- [ ] Docs: [Describe documentation updates]

### Implementation Notes

[Any additional context, edge cases, or dependencies]

### Related Patterns

[List similar or related blocker patterns if any]

---
```

---

## Example Blocker Analyses

### Example 1: Special Characters in Identifiers

## Blocker: special_chars_in_identifiers

### Classification

**Frequency:** 1 model  
**Affected Models:** chenery.gms  
**Complexity:** Simple  
**Category:** Syntax  
**Criticality:** Nice-to-have  
**Priority Score:** 10 + (5-1) = 14

### Error Message

```
Parse error at line 14: Unexpected token '-' in set element
Expected: identifier
Got: 'light-ind'
```

### Example Syntax

```gams
Set i sectors /
    light-ind
    food+agr
    heavy-ind
    services
/;
```

### GAMS Manual Reference

- **Section:** "2.2.3 Identifiers"
- **Page:** User's Guide p. 18
- **Link:** https://www.gams.com/latest/docs/UG_Language.html#UG_Language_Identifiers

GAMS allows hyphens and plus signs in set element identifiers, but our lexer treats them as operators.

### Complexity Estimate

**Effort:** 1.5 hours

**Rationale:**
Lexer-level change to identifier token rules. Requires distinguishing between operator context and identifier context.

**Breakdown:**
- Lexer changes: 30 min (update identifier regex to allow `-` and `+`)
- Grammar rules: 0 min (no changes needed)
- AST nodes: 0 min (identifiers already supported)
- Semantic analysis: 15 min (ensure symbol table handles special chars)
- Tests: 30 min (test cases for various special char combinations)
- Documentation: 15 min (update lexer docs)

### Parser Changes Needed

- [x] Lexer: Modify identifier token pattern to accept `[a-zA-Z_][a-zA-Z0-9_\-+]*`
- [ ] Grammar: No changes (identifiers already used in set elements)
- [ ] AST: No changes (string identifiers already supported)
- [ ] Semantic: Verify symbol table lookup works with special chars
- [x] Tests: Add test cases for `light-ind`, `food+agr`, edge cases like `--`, `++`
- [x] Docs: Update lexer documentation with identifier rules

### Implementation Notes

- **Edge case:** Must still parse `-` and `+` as operators in expressions
- **Context sensitivity:** Inside set declarations = identifier, elsewhere = operator
- **Alternative:** Use quoted strings `"light-ind"` but this breaks GAMS compatibility

### Related Patterns

- Underscore in identifiers (already supported)
- Numbers in identifiers (already supported)

---

### Example 2: Multiple Alias Declaration

## Blocker: multiple_alias_declaration

### Classification

**Frequency:** 1 model  
**Affected Models:** jbearing.gms  
**Complexity:** Simple  
**Category:** Syntax  
**Criticality:** Nice-to-have  
**Priority Score:** 10 + (5-1) = 14

### Error Message

```
Parse error at line 8: Unexpected token ',' after alias pair
Expected: ';'
Got: ','
Context: Alias (nx,i), (ny,j);
```

### Example Syntax

```gams
Alias (nx,i), (ny,j);
```

Current parser only supports single alias pair per statement:
```gams
Alias (nx,i);
Alias (ny,j);
```

### GAMS Manual Reference

- **Section:** "2.7 The Alias Statement: Multiple Names for a Set"
- **Page:** User's Guide p. 34
- **Link:** https://www.gams.com/latest/docs/UG_Language.html#UG_Language_AliasStatement

GAMS allows comma-separated alias pairs in single statement.

### Complexity Estimate

**Effort:** 1.5 hours

**Rationale:**
Grammar extension to allow list of alias pairs. Minimal AST and semantic impact.

**Breakdown:**
- Lexer changes: 0 min (all tokens already supported)
- Grammar rules: 30 min (change from single pair to comma-separated list)
- AST nodes: 15 min (extend Alias node to hold multiple pairs)
- Semantic analysis: 30 min (iterate over pairs, register each alias)
- Tests: 30 min (test single pair, multiple pairs, edge cases)
- Documentation: 15 min (update grammar docs)

### Parser Changes Needed

- [ ] Lexer: No changes needed
- [x] Grammar: Change `alias_stmt: 'Alias' '(' ID ',' ID ')' ';'` to `alias_stmt: 'Alias' alias_pair (',' alias_pair)* ';'` where `alias_pair: '(' ID ',' ID ')'`
- [x] AST: Extend `Alias` node from `(set_name, alias_name)` to `[(set1, alias1), (set2, alias2), ...]`
- [x] Semantic: Loop over pairs in semantic analyzer, register each alias in symbol table
- [x] Tests: Test `Alias (nx,i), (ny,j), (nz,k);` and single pair for backward compatibility
- [x] Docs: Update grammar documentation

### Implementation Notes

- **Backward compatibility:** Single pair `Alias (nx,i);` must still work
- **Validation:** Check for duplicate aliases across pairs
- **Symbol table:** Each alias gets own entry pointing to original set

### Related Patterns

- Comma-separated variable declarations (already implemented in Sprint 9)
- Multiple set declarations (different pattern - uses `Set i, j, k;`)

---

### Example 3: Inline Descriptions

## Blocker: inline_descriptions

### Classification

**Frequency:** 3 models  
**Affected Models:** chem.gms, water.gms, gastrans.gms  
**Complexity:** Medium  
**Category:** Syntax  
**Criticality:** Must-have  
**Priority Score:** 25 + (5-3) = 27

### Error Message

```
Parse error at line 42: Unexpected string after identifier
Expected: ';' or assignment operator
Got: "production capacity"
Context: Parameter cap(i) "production capacity";
```

### Example Syntax

```gams
Parameter cap(i) "production capacity";
Variable x(i,j) "shipment quantity from i to j";
Equation supply(i) "supply constraint at location i";
```

Current parser expects:
```gams
Parameter cap(i);  # No inline description
```

### GAMS Manual Reference

- **Section:** "3.3 Parameter Declarations"
- **Page:** User's Guide p. 47
- **Link:** https://www.gams.com/latest/docs/UG_Language.html#UG_Language_ParameterDeclarations

GAMS allows optional quoted string after declaration for documentation.

### Complexity Estimate

**Effort:** 4 hours

**Rationale:**
Grammar changes for 3 statement types (Parameter, Variable, Equation), AST extension, semantic handling.

**Breakdown:**
- Lexer changes: 0 min (string literals already supported)
- Grammar rules: 60 min (modify param_decl, var_decl, eq_decl to accept optional string)
- AST nodes: 45 min (add `description: Optional[str]` field to Parameter, Variable, Equation nodes)
- Semantic analysis: 30 min (store description in symbol table for documentation)
- Tests: 60 min (test all 3 statement types with/without descriptions, edge cases)
- Documentation: 45 min (update grammar and AST docs, examples)

### Parser Changes Needed

- [ ] Lexer: No changes (string literals already tokenized)
- [x] Grammar: 
  - `param_decl: 'Parameter' ID index_expr? string_literal? ';'`
  - `var_decl: 'Variable' ID index_expr? string_literal? ';'`
  - `eq_decl: 'Equation' ID index_expr? string_literal? ';'`
- [x] AST: Add `description: Optional[str] = None` to Parameter, Variable, Equation classes
- [x] Semantic: Store description in symbol table metadata
- [x] Tests: 
  - Test parameter with description: `Parameter cap(i) "capacity";`
  - Test variable with description: `Variable x(i,j) "shipment";`
  - Test equation with description: `Equation supply(i) "supply constraint";`
  - Test without description (backward compat): `Parameter cap(i);`
- [x] Docs: Document inline description syntax in grammar reference

### Implementation Notes

- **Optional feature:** Descriptions are purely for documentation, don't affect semantics
- **Backward compatibility:** Existing declarations without descriptions must still parse
- **Multi-line descriptions:** GAMS doesn't support multi-line, only single quoted strings
- **Impact:** Unlocks 3 models simultaneously (chem, water, gastrans)

### Related Patterns

- Model inline descriptions (different syntax: `Model transport /all/ "transport model";`)
- Set element descriptions (already supported in some contexts)

---

## Prioritization Summary

Based on the 6 blockers identified in TIER_2_MODEL_SELECTION.md:

| Blocker | Frequency | Complexity | Category | Priority Score | Effort | Models Unlocked |
|---------|-----------|------------|----------|----------------|--------|-----------------|
| inline_descriptions | 3 | Medium | Syntax | 27 | 4h | 3 |
| special_chars_in_identifiers | 1 | Simple | Syntax | 14 | 1.5h | 1 |
| multiple_alias_declaration | 1 | Simple | Syntax | 14 | 1.5h | 1 |
| predefined_constants | 1 | Simple | Syntax | 14 | 1h | 1 |
| model_inline_descriptions | 1 | Medium | Syntax | 12 | 2h | 1 |
| table_wildcard_domain | 3 | Medium | Data Structure | 27 | 5h | 3 |

### Recommended Implementation Order (6h Budget)

**Phase 1: Top Priority Implementation (4h total)**
1. **inline_descriptions** - 4h → Unlocks 3 models (chem, water, gastrans)
   - Priority: 27 (MEDIUM band, but highest score)
   - Reason: Best ROI (3 models for 4h effort)

**Phase 2: Secondary Priority (2h additional, 6h total)**
2. **multiple_alias_declaration** - 1.5h → Unlocks 1 model (jbearing)
   - Priority: 14 (LOW band)
   - Reason: Simple syntax fix
   
3. **predefined_constants** - 0.5h remaining budget → Partial implementation
   - Priority: 14 (LOW band)
   - Reason: May complete if inline_descriptions takes <4h

**Deferred (beyond 6h budget):**
- special_chars_in_identifiers (1.5h) - Lower priority simple fix
- model_inline_descriptions (2h) - Related to #1 but lower frequency
- table_wildcard_domain (5h) - Medium complexity, stretch goal

### Expected Parse Rate

**Conservative (4h spent):** 3/10 models = 30% (inline_descriptions only)  
**Realistic (6h spent):** 4-5/10 models = 40-50% (inline_descriptions + 1-2 simple blockers)  
**Optimistic (8h spent):** 6-7/10 models = 60-70% (add model_inline_descriptions + special_chars)

---

## Usage During Sprint 12

### Day 4: Blocker Analysis (1-2h)

1. Run parser on all 10 Tier 2 models
2. Collect error messages and line numbers
3. Fill out blocker template for each unique pattern
4. Calculate priority scores
5. Sort and select blockers fitting 6h budget

### Day 5-6: Implementation (6h)

1. Implement blockers in priority order
2. Test against affected models after each fix
3. Stop when budget consumed or ≥50% parse rate achieved

### Continuous Tracking

- Update this document as blockers are implemented
- Mark completed blockers with ✅
- Track actual effort vs estimated effort
- Adjust future estimates based on actuals

---

## Template Maintenance

**Version:** 1.0  
**Last Updated:** 2025-11-30  
**Owner:** Sprint 12 Team

### Changelog

- **2025-11-30:** Initial template creation (Task 8)
- **TBD:** Updates based on Sprint 12 actual usage

### Feedback

After Sprint 12 completion, update this template with:
- Accuracy of effort estimates (% variance)
- Missing fields in template
- Priority formula effectiveness
- Suggested improvements for future sprints
