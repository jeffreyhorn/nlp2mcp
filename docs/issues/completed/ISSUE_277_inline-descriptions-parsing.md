# Issue: Support Inline Text Descriptions in Declarations

**GitHub Issue:** #277 - https://github.com/jeffreyhorn/nlp2mcp/issues/277  
**Status:** Open  
**Priority:** Medium  
**Effort:** 2-3 hours  
**Blocking:** hs62.gms parsing  

## Description

GAMS allows inline text descriptions in variable, parameter, and equation declarations. This syntax is not currently supported by the parser, blocking hs62.gms from parsing.

## Example Syntax

```gams
diff   optcr - relative distance from global;
```

The syntax pattern is:
```
<identifier> <whitespace> <description_text> ;
```

Where the description text is free-form text that appears between the identifier and the semicolon.

## Current Behavior

Parser fails with:
```
Parse error at line 44, column 14: Unexpected character: '-'
  diff   optcr - relative distance from global;
               ^
```

## Expected Behavior

Parser should accept inline descriptions and either:
1. Store them as metadata on the IR node, or
2. Ignore them (like comments)

## Impact

**Blocks:** hs62.gms (Sprint 9 target model)  
**Parse Rate Impact:** +10% (1/10 models)

## Related Files

- `tests/fixtures/gamslib/hs62.gms` - Line 44
- `src/gams/gams_grammar.lark` - Needs grammar rule for inline descriptions
- `src/ir/parser.py` - Semantic handler for storing/ignoring descriptions

## GAMS Documentation

Inline descriptions are part of standard GAMS syntax for documenting symbols at declaration time. They're distinct from:
- Block comments (`* comment` or `$ontext...$offtext`)
- End-of-line comments (`// comment`)
- Explanatory text (standalone text lines)

## Suggested Implementation

1. **Grammar change** (1h):
   ```lark
   variable_decl: ID description? SEMI
   description: /[^;]+/  // Any text until semicolon
   ```

2. **Semantic handler** (0.5h):
   - Option A: Store in Variable/Equation/Parameter metadata
   - Option B: Parse and discard (simpler, matches current approach)

3. **Testing** (0.5-1h):
   - Test inline descriptions on variables, equations, parameters
   - Test hs62.gms parsing
   - Test empty descriptions, multi-word descriptions

## Verification

After implementation:
```bash
python -m src.ir.parser tests/fixtures/gamslib/hs62.gms
# Should parse successfully
```

Parse rate should increase from 40% to 50% (5/10 models).

## Discovery Context

Discovered during Sprint 9 Day 6 while implementing equation attributes. The planning assumption that "model sections unlock hs62.gms" was incorrect - hs62.gms is actually blocked by this inline description syntax.

See: `docs/planning/EPIC_2/SPRINT_9/checkpoint3_assessment.md`

## References

- hs62.gms line 44: `diff   optcr - relative distance from global;`
- PREP_PLAN.md line 1235 (incorrect assumption documented)
