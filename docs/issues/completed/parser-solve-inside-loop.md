# Parser: Solve Statement Not Supported Inside Loop Blocks

**GitHub Issue:** #414  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/414  
**Status:** Open  
**Priority:** High  
**Component:** Parser  
**Tier 2 Candidate:** pool.gms  

## Problem Statement

The parser fails when encountering `solve` statements inside `loop` blocks. This is blocking pool.gms from parsing completely.

## Current Behavior

**Parse Error:**
```
Error: Parse error at line 835, column 7: Unexpected character: 'p'
  solve poolprob minimizing cost using nlp;
        ^
```

**Failing Example from pool.gms (lines 683-740):**
```gams
loop(case,
   // extract domains and data
   comp(comp_) = ComponentData(case,comp_,'up');
   ...
   
   // set variable bounds
   q.up(comp,pool) = ComponentPoolFraction(case,comp,pool);
   ...
   
   solve poolprob minimizing cost using nlp;
   
   rep1(case, 'RawMat') = card(comp);
   rep1(case, 'Products') = card(pro);
   ...
);
```

The solve statement at line 727 is inside a loop block, but the parser doesn't recognize solve statements as valid executable statements within loops.

## Expected Behavior

The parser should successfully parse `solve` statements inside:
- Loop blocks
- If blocks  
- Any other control flow structures

Solve statements are commonly used inside loops to solve the same model multiple times with different data (as in pool.gms, which solves for multiple test cases).

## GAMS Language Specification

In GAMS, the `solve` statement can appear anywhere a regular statement can appear, including:
- At the top level
- Inside loop blocks
- Inside if/elseif/else blocks
- Inside nested control structures

**Syntax:**
```gams
solve model_name {minimizing|maximizing} objective_var using solver_type;
```

**Example patterns:**
```gams
* Top-level solve
solve mymodel minimizing cost using nlp;

* Inside loop
loop(scenario,
   data(i) = scenario_data(scenario, i);
   solve mymodel minimizing cost using nlp;
   results(scenario) = cost.l;
);

* Inside if block
if(condition,
   solve mymodel minimizing cost using nlp;
);
```

## Technical Analysis

### Current Grammar State

Looking at `src/gams/gams_grammar.lark`:

**Loop statement definition (line 299):**
```lark
loop_stmt: LOOP_K "(" id_list "," exec_stmt+ ")" SEMI
```

**Executable statements (line 304):**
```lark
?exec_stmt: display_stmt_nosemi
          | abort_stmt_nosemi
          | option_stmt
          | assignment_stmt
          | SEMI
```

**Solve statement definition (line 253):**
```lark
solve_stmt: "Solve"i ID obj_sense ID "using"i solver_type SEMI
```

The issue is that `solve_stmt` is NOT included in the `exec_stmt` rule, so it cannot appear inside loop or if blocks.

### Required Changes

Add `solve_stmt` to the `exec_stmt` rule:

```lark
?exec_stmt: display_stmt_nosemi
          | abort_stmt_nosemi
          | option_stmt
          | solve_stmt           // Add this line
          | assignment_stmt
          | SEMI
```

Note: Unlike display_stmt and abort_stmt which have `_nosemi` versions because the if/loop grammar handles semicolons differently, solve_stmt already includes its semicolon in its definition, so we can add it directly.

Actually, we may need to create a `solve_stmt_nosemi` version for consistency with the pattern. Let me check the pattern more carefully:

- `if_stmt` uses: `exec_stmt+` where exec_stmt items don't include trailing SEMI
- But `solve_stmt` definition already includes SEMI

We have two options:
1. Create `solve_stmt_nosemi` version and add that to exec_stmt
2. Keep solve_stmt as-is since its SEMI is already part of the rule

Looking at option_stmt, it includes SEMI and is already in exec_stmt, so we can follow that pattern.

## Implementation Plan

### 1. Update Grammar (src/gams/gams_grammar.lark)

Add `solve_stmt` to the `exec_stmt` rule:

```lark
?exec_stmt: display_stmt_nosemi
          | abort_stmt_nosemi
          | option_stmt
          | solve_stmt           // Add this
          | assignment_stmt
          | SEMI
```

### 2. Testing Strategy

**Unit Tests:**
- Solve statement at top level (already works)
- Solve statement inside loop block
- Solve statement inside if block
- Solve statement inside nested structures (loop inside if, etc.)
- Multiple solve statements in same loop

**Integration Tests:**
- Verify pool.gms parses successfully past line 727
- Test the full loop structure with solve statement

**Test Examples:**
```gams
* Test 1: Solve in loop
loop(i,
   x.up = bounds(i);
   solve mymodel minimizing cost using nlp;
);

* Test 2: Solve in if
if(condition,
   solve mymodel minimizing cost using nlp;
);

* Test 3: Pool.gms pattern
loop(case,
   data(i) = case_data(case, i);
   solve poolprob minimizing cost using nlp;
   results(case) = cost.l;
);
```

## Acceptance Criteria

1. ✅ Grammar includes solve_stmt in exec_stmt rule
2. ✅ Parser correctly handles solve statements inside loops
3. ✅ Parser correctly handles solve statements inside if blocks
4. ✅ pool.gms parses successfully past line 727
5. ✅ All existing tests continue to pass
6. ✅ New tests cover solve in loop/if patterns
7. ✅ Quality gates pass (typecheck, lint, format, test)

## Related Issues

- Issue #409: Pool.gms missing include file (completed)
- Issue #412: Conditional sum syntax (completed)
- Issue #413: Option statement with multiple assignments (completed)

This is the next blocker preventing pool.gms from parsing completely.

## References

- GAMS Documentation: [The Solve Statement](https://www.gams.com/latest/docs/UG_SolveStatement.html)
- GAMS Documentation: [Loop Statement](https://www.gams.com/latest/docs/UG_LoopStatement.html)
- File: `tests/fixtures/tier2_candidates/pool.gms` (line 727)
- GAMS Library: pool.gms is model 237 in GAMSLib

## Notes

This is a straightforward fix - just adding one line to the grammar. The solve_stmt definition already exists and works at the top level; it just needs to be included in the list of statements that can appear inside control flow blocks.
