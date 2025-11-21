# Issue: Support abort$ Statements Inside if-Block Bodies

**GitHub Issue:** TBD (create at https://github.com/jeffreyhorn/nlp2mcp/issues/new)  
**Status:** Open  
**Priority:** Medium  
**Effort:** 3-4 hours  
**Blocking:** mingamma.gms parsing  

## Description

GAMS allows `abort$[conditional]` statements inside if-statement bodies. This syntax is not currently supported by the parser, blocking mingamma.gms from parsing.

The grammar currently supports `abort$` as a top-level statement, but not as a statement within if-block bodies.

## Example Syntax

```gams
if(m1.solveStat <> %solveStat.capabilityProblems%,
   abort$[abs(x1delta) > xtol or abs(y1delta) > ytol] "inconsistent results with gamma";
);
```

## Current Behavior

Parser fails with:
```
Parse error at line 60, column 1: Unexpected character: ')'
  );
  ^
```

The parser accepts the if-statement opening but fails to recognize `abort$` as a valid statement inside the if-block body, causing it to fail on the closing `);`.

## Expected Behavior

Parser should accept `abort$` statements (with or without conditionals) as valid statements within if-block bodies.

## Impact

**Blocks:** mingamma.gms (Sprint 9 target model)  
**Parse Rate Impact:** +10% (1/10 models)

## Related Files

- `tests/fixtures/gamslib/mingamma.gms` - Lines 58-60, 62-64
- `src/gams/gams_grammar.lark` - Line 231 (abort_stmt currently defined)
- `src/gams/gams_grammar.lark` - If-statement body needs to include abort_stmt

## Current Grammar

**Existing abort support:**
```lark
abort_stmt: "abort"i ("$" expr)? STRING? SEMI
```

**Problem:** abort_stmt is likely not included in the if-statement body production.

## Suggested Implementation

1. **Grammar analysis** (0.5h):
   - Locate if-statement body production in grammar
   - Verify which statement types are currently allowed
   - Check if abort_stmt is in the statement alternatives

2. **Grammar fix** (0.5h):
   ```lark
   // If-statement body should include abort_stmt
   if_body: statement+
   statement: assign_stmt
            | abort_stmt       // Add this if missing
            | display_stmt
            | solve_stmt
            | ... other statements
   ```

3. **Semantic handler** (1h):
   - Ensure abort$[...] conditional syntax is properly handled
   - May need to handle square bracket syntax `$[...]` vs parenthesis `$(...)`
   - Store or mock abort statements (mock/store approach like Sprint 8)

4. **Testing** (1-1.5h):
   - Test abort$ in if-blocks with conditionals
   - Test abort$ with string messages
   - Test mingamma.gms parsing
   - Test nested if-blocks with abort statements

## Verification

After implementation:
```bash
python -m src.ir.parser tests/fixtures/gamslib/mingamma.gms
# Should parse successfully
```

Parse rate should increase from 40% to 50% (5/10 models).

## Additional Notes

**mingamma.gms does NOT use equation attributes** - it only uses variable attributes (.l, .lo). The planning assumption that equation attributes would unlock mingamma.gms was incorrect.

The actual uses in mingamma.gms:
```gams
Line 17: x1.lo = 0.01;              # Variable bound
Line 18: x2.lo = 0.01;              # Variable bound
Line 45: x1delta = x1.l - x1opt;    # Variable .l attribute
Line 46: y1delta = y1.l - y1opt;    # Variable .l attribute
Line 50: display x1.l, x2.l, ...    # Variable .l attributes
```

## Discovery Context

Discovered during Sprint 9 Day 6 while implementing equation attributes. The planning assumption that "equation attributes unlock mingamma.gms" was incorrect - mingamma.gms is actually blocked by this if-block statement support issue.

See: `docs/planning/EPIC_2/SPRINT_9/mingamma_blocker_analysis.md`

## References

- mingamma.gms lines 58-60: First abort$ in if-block
- mingamma.gms lines 62-64: Second abort$ in if-block
- Grammar line 231: Current abort_stmt production
- PREP_PLAN.md line 1236 (incorrect assumption documented)
