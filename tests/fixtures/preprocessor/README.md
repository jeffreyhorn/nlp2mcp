# Preprocessor Directive Fixtures

This directory contains test fixtures for GAMS preprocessor directive handling.

## Purpose

These fixtures test the parser's ability to handle GAMS preprocessor directives including:
- `$set` - Variable definition
- `$if not set` - Conditional variable definition
- `$if/$else/$endif` - Conditional branching
- `%macro%` - Macro expansion
- `$eolCom` - End-of-line comment directives
- `$include` - File inclusion (regression test)
- `$onText/$offText` - Multi-line comment blocks

## Fixtures

### Created (9/9)

1. **simple_set.gms** - Basic $set directive with macro expansion
   - Tests: `$set myvar 100` and `%myvar%` substitution
   
2. **simple_if.gms** - Conditional variable definition
   - Tests: `$if not set n $set n 10`
   
3. **if_else.gms** - Conditional branching
   - Tests: `$if set debug` with `$else` branch
   
4. **macro_expansion.gms** - Multiple macro expansions
   - Tests: `%rows%`, `%cols%`, `%total%` substitution
   
5. **nested_if.gms** - Nested conditional statements
   - Tests: Nested `$if` directives
   
6. **eolcom.gms** - Custom end-of-line comment character
   - Tests: `$eolCom #` directive
   
7. **include_basic.gms** - File inclusion (regression)
   - Tests: `$include` directive (already supported)
   
8. **ontext_offtext.gms** - Multi-line comment blocks
   - Tests: `$onText/$offText` directives (already supported)
   
9. **combined.gms** - Multiple directives combined
   - Tests: `$eolCom`, `$if not set`, `$set`, `%macro%` together

## Expected Results

See `expected_results.yaml` for detailed expected parsing behavior for each fixture.

## Usage

```bash
# Run preprocessor fixture tests (when implemented)
pytest tests/unit/ir/test_preprocessor.py -v -k fixtures
```

## Implementation Notes

**Sprint 7 Status:**
- Preprocessor directives are mocked/stripped in Sprint 7
- Full macro expansion planned for Sprint 8-9
- Fixtures serve as specification for future implementation

**Current Behavior:**
- `$set` and `%macro%` - Extracted and expanded
- `$if not set` - Evaluated with default values
- `$eolCom`, `$onText/$offText` - Stripped/ignored
- `$include` - Fully implemented (recursive expansion)

## Coverage Matrix

| Feature | Fixture | Parse | Expand | Notes |
|---------|---------|-------|--------|-------|
| $set | simple_set | ✓ | ✓ | Basic variable definition |
| $if not set | simple_if | ✓ | ✓ | Conditional default |
| $if/$else | if_else | ✓ | Partial | Branch selection |
| %macro% | macro_expansion | ✓ | ✓ | Variable substitution |
| Nested $if | nested_if | ✓ | Partial | Nested conditionals |
| $eolCom | eolcom | ✓ | Strip | Comment marker |
| $include | include_basic | ✓ | ✓ | File inclusion |
| $onText/$offText | ontext_offtext | ✓ | Strip | Block comments |
| Combined | combined | ✓ | Partial | Multiple directives |

## Status

- **Created:** Sprint 7 Day 0
- **Fixtures:** 9/9 ✅ COMPLETE (Day 5)
- **Tests:** 0/9 (to be implemented)
