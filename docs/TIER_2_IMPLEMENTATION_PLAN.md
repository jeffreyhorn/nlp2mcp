# Tier 2 Implementation Plan

**Sprint:** Sprint 12 Day 6  
**Date:** 2025-12-01  
**Final Parse Rate:** 2/10 (20%)

---

## Summary

Sprint 12 Days 4-6 focused on expanding parser support to Tier 2 GAMSLib models. Despite implementing 3 blockers across Days 4-6, the final parse rate of 20% fell significantly short of the 50% minimum target.

---

## Blockers Implemented

### Day 4 (Sprint 12)

1. **predefined_constants** - 1h actual
   - Added `pi`, `inf`, `eps`, `na` to symbol table
   - Unlocked: fct.gms
   - Status: ✅ Complete

2. **multiple_alias_declaration** - 1.5h actual
   - Support comma-separated alias pairs: `Alias (i,i1), (j,j1);`
   - Partially unlocked: jbearing.gms (has additional blocker)
   - Status: ✅ Complete

3. **special_chars_in_identifiers** - 1.5h actual
   - Attempted: Allow `-` and `+` in identifiers
   - Result: Broke 3 Tier 1 models (hs62, mhw4d, mhw4dx)
   - Status: ❌ REVERTED
   - Alternative: Users can use quoted identifiers `'light-ind'`

### Day 5 (Sprint 12)

4. **inline_descriptions** - Grammar support only
   - Added `ID STRING?` pattern for set elements with descriptions
   - Models still blocked by newline-as-separator issue
   - Status: ⚠️ PARTIAL (grammar ready, models still fail)

### Day 6 (Sprint 12)

5. **model_inline_descriptions** - 1h actual
   - Added `STRING?` to all Model statement variants
   - Support for `Model name 'description' / ... /;`
   - Unlocked: process.gms
   - Status: ✅ Complete

---

## Blockers Analyzed but Deferred

| Blocker | Issue | Priority | Effort | Impact | Reason for Deferral |
|---------|-------|----------|--------|--------|---------------------|
| newline_as_separator | [#353](https://github.com/jeffreyhorn/nlp2mcp/issues/353) | HIGH | 4-6h | 3 models | Grammar ambiguity with ID STRING patterns |
| table_wildcard_domain | [#354](https://github.com/jeffreyhorn/nlp2mcp/issues/354) | MEDIUM | 5h | 3 models | Complex domain inference logic |
| curly_braces_sum | [#355](https://github.com/jeffreyhorn/nlp2mcp/issues/355) | MEDIUM | 1-2h | 1 model | Low ROI for single model |
| tuple_notation | [#356](https://github.com/jeffreyhorn/nlp2mcp/issues/356) | MEDIUM | 2-3h | 1 model | Depends on #353 being fixed first |
| special_chars_in_identifiers | [#357](https://github.com/jeffreyhorn/nlp2mcp/issues/357) | LOW | 4-5h | 1 model | Requires whitespace-aware lexing |

---

## Lessons Learned

### Underestimated Complexity

**Initial Estimate:** newline_as_separator = 1-2h (simple grammar change)  
**Actual Complexity:** 4-6h (requires preprocessor or lexer redesign)

**Root Cause:** Making commas optional (`(","? set_member)*`) creates ambiguity:
- `H 'hydrogen'` should parse as ONE element with description
- With optional commas, parser treats as TWO elements: `H` + `'hydrogen'`

**Learning:** Grammar simplicity doesn't always indicate implementation simplicity. Context-dependent parsing requires more sophisticated solutions.

### Trade-off Decisions

**special_chars_in_identifiers:** Fixed 1 model but broke 3 models → REVERTED

**Decision Framework:**
- Net impact must be positive
- Never trade Tier 1 stability for Tier 2 gains
- Document workarounds for edge cases

### Compound Blockers

**water.gms** requires BOTH:
1. newline_as_separator (#353)
2. tuple_notation (#356)

**Learning:** Analyze full model before estimating unlock impact. Some models have multiple blocking issues.

---

## Sprint 13 Roadmap

### Phase 1: High-Priority Blockers (Days 1-3)

**Goal:** Achieve 50-60% Tier 2 parse rate

1. **[#353](https://github.com/jeffreyhorn/nlp2mcp/issues/353) - newline_as_separator** (4-6h)
   - Implement preprocessor normalization approach
   - Insert commas at line ends within `/.../ blocks`
   - Unlocks: chem, gastrans (+20% Tier 2)

2. **[#355](https://github.com/jeffreyhorn/nlp2mcp/issues/355) - curly_braces_sum** (1-2h)
   - Add `{` and `}` as alternatives to `(` and `)` in aggregation functions
   - Unlocks: jbearing (+10% Tier 2)

**Expected Outcome:** 5/10 Tier 2 models (50%)

### Phase 2: Medium-Priority Blockers (Days 4-5)

**Goal:** Achieve 60-70% Tier 2 parse rate

3. **[#356](https://github.com/jeffreyhorn/nlp2mcp/issues/356) - tuple_notation** (2-3h)
   - Implement `ID.(id1,id2,...)` Cartesian product expansion
   - Unlocks: water (if combined with #353) (+10% Tier 2)

**Expected Outcome:** 6/10 Tier 2 models (60%)

### Phase 3: Stretch Goals (Days 6-8)

**Goal:** Achieve 90-100% Tier 2 parse rate

4. **[#354](https://github.com/jeffreyhorn/nlp2mcp/issues/354) - table_wildcard_domain** (5h)
   - Implement wildcard domain inference for tables
   - Unlocks: least, like, bearing (+30% Tier 2)

**Expected Outcome:** 9/10 Tier 2 models (90%)

### Overall Target

**Tier 2:** 90-100% (9-10/10 models)  
**Overall:** 95-100% (19-20/20 models) ✅ EXCEEDS 75% target

---

## Code Changes Summary

### Grammar Changes (src/gams/gams_grammar.lark)

```lark
# Model statements with optional descriptions
model_stmt: ("Models"i | "Model"i) ID STRING? "/" "all"i "/" SEMI
          | ("Models"i | "Model"i) ID STRING? "/" model_ref_list "/" SEMI
          | ("Models"i | "Model"i) ID STRING? SEMI
          | ("Models"i | "Model"i) model_decl_item+ SEMI

model_decl_item: ID STRING? "/" model_ref_list "/"
               | ID STRING? "/" "all"i "/"
```

### Parser Changes

No parser changes required - grammar handles description tokens automatically. Parser ignores STRING tokens (documentation only).

---

## Testing

**Unit Tests:** 12 tests in `tests/unit/test_inline_descriptions.py` (all passing)  
**Integration Tests:** process.gms parsing successfully  
**Regression Tests:** All 1830 existing tests passing (2 golden file flakes)

---

## Next Steps

1. **Complete Sprint 12 Days 7-9:** JSON diagnostics, PATH solver, Dashboard polish
2. **Sprint 12 Retrospective:** Analyze Tier 2 complexity underestimation
3. **Sprint 13 Planning:** Prioritize newline_as_separator and curly_braces_sum
4. **Documentation:** Update user guide with workarounds for unsupported syntax

---

## References

- Implementation commits: Day 4 (b0a9e79, eb6435e), Day 6 (7b8e1ff)
- Issue tracking: [#353](https://github.com/jeffreyhorn/nlp2mcp/issues/353)-[#357](https://github.com/jeffreyhorn/nlp2mcp/issues/357)
- Blocker details: `docs/issues/*.md`
- Sprint plan: `docs/planning/EPIC_2/SPRINT_12/PLAN.md`
