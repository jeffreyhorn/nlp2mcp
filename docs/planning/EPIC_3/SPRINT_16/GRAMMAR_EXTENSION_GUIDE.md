# GAMS Grammar Extension Guide

**Created:** January 18, 2026  
**Purpose:** Guide for safely extending the GAMS grammar for Sprint 16 parser improvements  
**Related Task:** Sprint 16 Prep Task 5 - Survey GAMS Grammar Extension Patterns

---

## Executive Summary

This guide documents the structure of the nlp2mcp GAMS grammar (`src/gams/gams_grammar.lark`) and provides patterns for safely extending it to handle additional GAMS syntax. The primary use case for Sprint 16 is improving handling of dollar control options ($ontext/$offtext, $include) that currently cause 86.5% of parse failures.

**Key Findings:**
- Grammar has 604 lines with well-organized sections
- Uses Earley parser with ambiguity resolution
- Dollar control is already partially handled via `%ignore` directives
- Extension patterns are straightforward but require regression testing
- Lexer-level patterns (via `%ignore`) are the safest approach for skipping content

---

## Table of Contents

1. [Current Grammar Analysis](#current-grammar-analysis)
2. [Grammar Structure Overview](#grammar-structure-overview)
3. [Extension Patterns](#extension-patterns)
4. [Dollar Control Handling](#dollar-control-handling)
5. [Lark Best Practices](#lark-best-practices)
6. [Testing Checklist](#testing-checklist)
7. [Risk Assessment](#risk-assessment)

---

## Current Grammar Analysis

### File Statistics

| Metric | Value |
|--------|-------|
| File Location | `src/gams/gams_grammar.lark` |
| Total Lines | 604 |
| Rule Count | ~80 rules |
| Terminal Count | ~50 terminals |
| Parser Type | Earley (with ambiguity="resolve") |

### Parser Configuration

From `src/ir/parser.py:122-127`:

```python
return Lark.open(
    _GRAMMAR_PATH,
    parser="earley",
    start="start",
    maybe_placeholders=False,
    ambiguity="resolve",
)
```

**Configuration Notes:**
- **Earley parser**: Handles ambiguous grammars gracefully
- **ambiguity="resolve"**: Automatically selects simplest derivation when ambiguous
- **maybe_placeholders=False**: Optional rules don't create placeholder nodes

### Major Sections

| Section | Lines | Description |
|---------|-------|-------------|
| Header/Comments | 1-10 | Grammar description and notes |
| Start Rule | 11-15 | `start: stmt*` entry point |
| Statement Types | 16-35 | Top-level statement alternatives |
| Block Definitions | 36-100 | Sets, Parameters, Variables, Equations blocks |
| Declarations | 101-200 | Set/param/var/scalar declarations |
| Table Handling | 201-250 | Table block parsing |
| Assignments/Bounds | 251-300 | Assignment statements, lvalues |
| Indexing | 301-350 | Index expressions, lag/lead |
| Equations | 351-400 | Equation definitions |
| Solve/Model | 401-450 | Solve statements, model declarations |
| Control Flow | 451-500 | If, loop, option statements |
| I/O Statements | 501-550 | File, put, display, abort |
| Expressions | 551-580 | Expression grammar (precedence-based) |
| Tokens | 581-604 | Terminal definitions, %ignore directives |

---

## Grammar Structure Overview

### Entry Point

```lark
start: stmt*  -> program
```

All GAMS files are parsed as a sequence of statements.

### Statement Types

```lark
?stmt: sets_block
     | aliases_block
     | params_block
     | table_block
     | scalars_block
     | variables_block
     | equations_block
     | model_stmt
     | option_stmt
     | if_stmt
     | loop_stmt
     | display_stmt
     | abort_stmt
     | file_stmt
     | put_stmt
     | putclose_stmt
     | execute_stmt
     | assignment_stmt
     | equation_def
     | solve_stmt
     | SEMI
```

The `?` prefix means this rule is "inlined" - its children are promoted directly to the parent.

### Terminal Definitions

Key terminal patterns:

```lark
// Identifiers
ID: ESCAPED | /[a-zA-Z_][a-zA-Z0-9_]*/
SYMBOL_NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
SET_ELEMENT_ID.2: /[a-zA-Z_][a-zA-Z0-9_+\-]*/

// Operators
DOLLAR.10: "$"  // Higher priority to prevent consumption by ignore

// Numbers
NUMBER: SIGNED_NUMBER
```

### Current Ignore Patterns

```lark
%ignore WS_INLINE
%ignore /(?m)^\s*\*.*$/               // GAMS inline comments: * at line start
%ignore /\/\/.*?$/m                    // // comments
%ignore /(?si)\$ontext.*?\$offtext/    // Block comments (case insensitive)
%ignore /\$(?![\(\s])[a-z]+[^\n]*/i    // $ directives (not $ operator)
%ignore NEWLINE
```

**Critical Insight:** The grammar already handles `$ontext/$offtext` via `%ignore`. The issue is that the regex may not match all variations in GAMSLIB models.

---

## Extension Patterns

### Pattern 1: Adding New Statement Types

**Use Case:** Supporting a new top-level statement (e.g., `$include`).

**Pattern:**
```lark
// Add to statement alternatives
?stmt: existing_statements
     | NEW_STATEMENT_TYPE

// Define the new statement
new_statement_type: "keyword"i argument_list SEMI
```

**Example - Adding acronym statement:**
```lark
?stmt: ... | acronym_stmt

acronym_stmt: "acronym"i ID ("," ID)* SEMI
```

**Safety Notes:**
- Add to end of statement alternatives to minimize precedence impact
- Use case-insensitive matching with `"keyword"i`
- End with SEMI for consistency

### Pattern 2: Adding New Terminals

**Use Case:** Recognizing new token types (e.g., special characters).

**Pattern:**
```lark
// Define terminal with regex
NEW_TOKEN: /pattern/
NEW_TOKEN.5: /pattern/  // With priority (higher = matched first)

// Use in rules
some_rule: existing | NEW_TOKEN
```

**Example - Supporting Unicode identifiers:**
```lark
UNICODE_ID: /[\p{L}_][\p{L}\p{N}_]*/
```

**Safety Notes:**
- Higher priority terminals match first
- Test for conflicts with existing terminals
- Consider using `%import common.UNICODE_LETTER` for standard patterns

### Pattern 3: Extending Existing Rules with Alternatives

**Use Case:** Adding syntax variations to existing constructs.

**Pattern:**
```lark
// Original
existing_rule: pattern1 | pattern2

// Extended (using %extend or direct modification)
existing_rule: pattern1 | pattern2 | pattern3
```

**Example - Supporting square brackets in indexing:**
```lark
// Already done in grammar
ref_indexed.2: ID "(" index_list ")"   -> symbol_indexed
             | ID "[" index_list "]"   -> symbol_indexed
```

**Safety Notes:**
- Use same tree alias (`-> symbol_indexed`) for semantic equivalence
- Test both syntaxes in unit tests
- Ensure no ambiguity with other rules

### Pattern 4: Adding Ignore Patterns for Content Skipping

**Use Case:** Skipping content that shouldn't be parsed (comments, directives).

**Pattern:**
```lark
%ignore /regex_pattern/flags
```

**Example - Current dollar control handling:**
```lark
%ignore /(?si)\$ontext.*?\$offtext/    // Block comments
%ignore /\$(?![\(\s])[a-z]+[^\n]*/i    // Single-line directives
```

**Safety Notes:**
- Use non-greedy quantifiers (`.*?`) to avoid over-matching
- Test with nested/edge cases
- Ensure pattern doesn't match valid syntax

### Pattern 5: Optional Elements

**Use Case:** Making parts of syntax optional.

**Pattern:**
```lark
rule: required_part optional_part?

// Or with default alternatives
rule: required_part (option1 | option2)?
```

**Example - Optional semicolons (already in grammar):**
```lark
sets_block: ("Sets"i | "Set"i) set_decl+ SEMI?
```

**Safety Notes:**
- Optional elements can create ambiguity
- Test with and without the optional part
- Consider if omission should trigger warnings

---

## Dollar Control Handling

### Current State

The grammar already handles basic dollar control via `%ignore`:

```lark
%ignore /(?si)\$ontext.*?\$offtext/    // Block comments
%ignore /\$(?![\(\s])[a-z]+[^\n]*/i    // Single-line directives
```

### Why Models Still Fail

Based on Sprint 15 analysis, 109 models fail with `lexer_invalid_char`. Potential causes:

1. **Pattern mismatch**: The regex may not match all variations
2. **Whitespace issues**: `$ontext` with leading whitespace may not match
3. **Nested constructs**: `$if` inside `$ontext` blocks
4. **Encoding issues**: Non-ASCII characters in directive names

### Recommended Improvements

#### Option A: Enhanced Ignore Pattern (Low Risk)

Update the `$ontext/$offtext` pattern to be more permissive:

```lark
// Current
%ignore /(?si)\$ontext.*?\$offtext/

// Enhanced - handle whitespace before $
%ignore /(?sim)^\s*\$ontext.*?\$offtext/
```

**Pros:** Minimal change, backward compatible  
**Cons:** May still miss edge cases

#### Option B: Explicit Rule with Skip (Medium Risk)

Create an explicit rule that captures and discards dollar blocks:

```lark
// Define terminal for entire block
DOLLAR_BLOCK: /(?si)\$ontext.*?\$offtext/

// Add to ignore
%ignore DOLLAR_BLOCK
```

**Pros:** More explicit, easier to debug  
**Cons:** Requires terminal definition

#### Option C: Preprocessing (Low Grammar Risk)

Add preprocessing step in Python before parsing:

```python
def preprocess_gams(source: str) -> str:
    """Remove dollar control blocks before parsing."""
    # Remove $ontext...$offtext blocks
    source = re.sub(r'(?si)\$ontext.*?\$offtext', '', source)
    # Remove single-line directives
    source = re.sub(r'(?im)^\s*\$[a-z]+.*$', '', source)
    return source
```

**Pros:** Full control, easy to debug, no grammar changes  
**Cons:** Additional processing step, may hide useful info

### Recommended Approach for Sprint 16

**Start with Option A** (enhanced ignore pattern) as it's lowest risk. If that doesn't achieve target improvement, implement **Option C** (preprocessing) which provides full control without grammar risk.

---

## Lark Best Practices

### 1. Parser Selection

| Parser | When to Use |
|--------|-------------|
| Earley | Default choice; handles ambiguity gracefully |
| LALR | When performance is critical and grammar is unambiguous |

The current grammar uses Earley, which is appropriate for GAMS's complex syntax.

### 2. Ambiguity Handling

**Current setting:** `ambiguity="resolve"`

This automatically picks the "simplest" derivation when multiple parses are possible. This is appropriate for production use.

For debugging ambiguities:
```python
parser = Lark.open(grammar, ambiguity="explicit")
# Ambiguous nodes appear as _ambig in the tree
```

### 3. Terminal Priorities

Higher priority terminals are matched first:

```lark
DOLLAR.10: "$"        // Priority 10 - matched before lower priorities
ID: /[a-zA-Z_]\w*/    // Default priority 0
DESC_TEXT.-1: /pattern/  // Priority -1 - matched after defaults
```

**Rule:** Use priorities sparingly and only when needed to resolve conflicts.

### 4. Rule Aliases

Use `-> alias` to normalize different syntaxes:

```lark
// Both produce same tree structure
ref_indexed.2: ID "(" index_list ")"   -> symbol_indexed
             | ID "[" index_list "]"   -> symbol_indexed
```

### 5. Inline Rules

Use `?` prefix for rules that should be "transparent":

```lark
?stmt: sets_block | params_block | ...
// Children appear directly under parent, not under "stmt" node
```

### 6. Error Recovery

Lark provides limited error recovery (LALR only). For Earley parser, handle errors in Python:

```python
try:
    tree = parser.parse(text)
except UnexpectedCharacters as e:
    # Handle lexer error
    raise ParseError(f"Unexpected character at line {e.line}")
except UnexpectedToken as e:
    # Handle parser error
    raise ParseError(f"Unexpected token at line {e.line}")
```

---

## Testing Checklist

### Before Making Grammar Changes

- [ ] Create a failing test case that demonstrates the syntax to be supported
- [ ] Identify the specific grammar rule(s) to modify
- [ ] Check for potential conflicts with existing rules
- [ ] Backup current grammar (git handles this)

### Making Grammar Changes

- [ ] Add terminal definition if introducing new token type
- [ ] Add rule or rule alternative
- [ ] Use tree aliases (`-> name`) for semantic equivalence
- [ ] Set appropriate priorities if needed
- [ ] Add comments explaining the change

### After Making Grammar Changes

- [ ] Run the new failing test - should now pass
- [ ] Run full parser test suite: `pytest tests/parser/ tests/unit/gams/test_parser.py -v`
- [ ] Run on GAMSLIB sample: `python scripts/gamslib/batch_parse.py --limit 10`
- [ ] Check for ambiguity warnings in verbose mode
- [ ] Compare parse success rate before/after

### Regression Testing Protocol

```bash
# 1. Baseline - record current state
python scripts/gamslib/batch_parse.py --json > baseline.json

# 2. Make grammar change

# 3. Retest
python scripts/gamslib/batch_parse.py --json > after.json

# 4. Compare
# Check: No previously-passing models now fail
# Check: Some previously-failing models now pass
```

### Test Categories

| Category | Test Files | Purpose |
|----------|------------|---------|
| Unit Tests | `tests/unit/gams/test_parser.py` | Core parsing functionality |
| Feature Tests | `tests/parser/test_*.py` | Specific syntax features |
| Performance | `tests/unit/gams/test_parser_performance.py` | Parsing speed |
| Integration | `scripts/gamslib/batch_parse.py` | Real-world models |

---

## Risk Assessment

### Low Risk Changes

| Change Type | Risk Level | Mitigation |
|-------------|------------|------------|
| Add new `%ignore` pattern | Low | Test doesn't match valid syntax |
| Add new statement type at end of alternatives | Low | Comprehensive tests |
| Add new terminal with explicit priority | Low | Check for conflicts |

### Medium Risk Changes

| Change Type | Risk Level | Mitigation |
|-------------|------------|------------|
| Modify existing rule alternatives | Medium | Extensive regression testing |
| Change terminal priorities | Medium | Test all affected terminals |
| Add ambiguous alternatives | Medium | Use Earley with resolve |

### High Risk Changes

| Change Type | Risk Level | Mitigation |
|-------------|------------|------------|
| Change parser type (Earley → LALR) | High | Full test suite + manual review |
| Modify expression precedence | High | Mathematical validation |
| Remove existing rules/terminals | High | Deprecation warning first |

### Sprint 16 Risk Mitigation

For the planned dollar control improvements:

1. **Use `%ignore` pattern enhancement** (Low Risk)
   - Minimal change to existing grammar
   - Easy to revert if issues arise

2. **Run full regression suite** before merging
   - All 34 currently-passing models must still pass
   - Target: 10-30 additional models passing

3. **Implement changes incrementally**
   - One pattern at a time
   - Test after each change

---

## Appendix: Grammar Quick Reference

### Common Terminals

| Terminal | Pattern | Description |
|----------|---------|-------------|
| `ID` | `/[a-zA-Z_][a-zA-Z0-9_]*/` | Identifier |
| `NUMBER` | `SIGNED_NUMBER` | Numeric literal |
| `STRING` | `/"[^"]*"\\|'[^']*'/` | Quoted string |
| `SEMI` | `;` | Statement terminator |
| `DOLLAR` | `$` | Dollar operator (priority 10) |

### Common Rules

| Rule | Purpose |
|------|---------|
| `start` | Entry point |
| `stmt` | Any top-level statement |
| `expr` | Expression (with precedence) |
| `index_list` | Comma-separated indices |
| `id_list` | Comma-separated identifiers |

### Useful Lark Directives

| Directive | Purpose |
|-----------|---------|
| `%ignore PATTERN` | Skip matching content |
| `%import common.X` | Import standard terminal |
| `%override rule` | Replace rule definition |
| `%extend rule` | Add alternatives to rule |

---

## References

- [Lark Grammar Documentation](https://lark-parser.readthedocs.io/en/stable/grammar.html)
- [Lark Parser Classes](https://lark-parser.readthedocs.io/en/stable/classes.html)
- [GAMS Documentation - Dollar Control Options](https://www.gams.com/latest/docs/UG_DollarControlOptions.html)
- Sprint 15 Baseline Analysis: `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md`
