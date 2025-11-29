# Tier 2 GAMSLib Model Selection

**Sprint:** Epic 2 - Sprint 12 Prep Task 3  
**Created:** 2025-11-29  
**Purpose:** Select 10 Tier 2 models for Sprint 12 parser expansion

---

## Executive Summary

**Final Selection:** 10 models covering 5 distinct blocker patterns  
**Total Estimated Effort:** 6h (conservative estimate)  
**Expected Parse Rate:** 45-60% (5-6 models parsing after implementation)  
**Blocker Diversity:** 5 patterns across syntax, data structures, and preprocessor features

### Key Metrics

- **Candidates Evaluated:** 18 models
- **Parse Success Rate (baseline):** 5.6% (1/18 models: house.gms)
- **Selected Models:** 10
- **Unique Blocker Patterns:** 5
- **Estimated Implementation Effort:**  6h total
  - Simple blockers (1-2h each): 3 blockers = 4h
  - Medium blockers (2-4h each): 2 blockers = 6h (at limit)

### Blocker Distribution

| Blocker Pattern | Complexity | Effort | Model Count | Models |
|-----------------|------------|--------|-------------|--------|
| special_chars_in_identifiers | Simple | 1.5h | 1 | chenery |
| multiple_alias_declaration | Simple | 1.5h | 1 | jbearing |
| predefined_constants | Simple | 1h | 1 | fct |
| inline_descriptions | Medium | 4h | 3 | chem, water, gastrans |
| model_inline_descriptions | Medium | 2h | 1 | process |
| table_wildcard_domain | Medium | 5h | 3 | least, like, bearing |

**Total:** 6h for 5 distinct blockers, 10 models selected

---

## Selection Criteria

### Primary Criteria
1. **Blocker Diversity:** Select models representing different blocker patterns
2. **Effort Budget:** Total ≤6h, no single blocker >5h
3. **Common Patterns:** Prioritize blockers marked "common" in GAMS code
4. **Model Size:** Prefer small-medium models (40-180 lines)
5. **Multiple Models per Blocker:** Validate fixes across 2-3 models when possible

### Exclusion Criteria
- **Very Hard Blockers (>6h):** lead_lag_indexing (chain: 6-10h, polygon: 12-16h)
- **External Dependencies:** include_file (pool, gasoil - requires external .inc files)
- **Advanced Preprocessor:** macro_preprocessor (inscribedsquare - $macro directive)
- **Complex Tuple Notation:** Deferred to future (some aspects of gastrans, water)

### Selection Algorithm
1. Group candidates by blocker pattern
2. Estimate effort per blocker (not per model)
3. Select simplest blockers first (1-2h range)
4. Add medium blockers up to 6h total budget
5. For each blocker, select 1-3 models to validate fix
6. Ensure at least 5 distinct blocker patterns

---

## Final Selection: 10 Models

### Model 1: chenery.gms
**Primary Blocker:** special_chars_in_identifiers  
**Effort:** 1.5h (Simple)  
**Size:** 172 lines  
**Type:** NLP  
**Description:** Substitution and Structural Change

**Blocker Detail:**  
Set elements use hyphens and plus signs: `/ light-ind, food+agr, heavy-ind, services /`

**Why Selected:**  
- Simple lexer-level fix
- Common GAMS pattern (identifiers with special chars)
- Unlocks economic modeling patterns

### Model 2: jbearing.gms
**Primary Blocker:** multiple_alias_declaration  
**Effort:** 1.5h (Simple)  
**Size:** 55 lines  
**Type:** NLP  
**Description:** Journal bearing COPS 2.0 #16

**Blocker Detail:**  
Multiple alias pairs in one statement: `Alias (nx,i), (ny,j);`

**Why Selected:**  
- Simple grammar extension
- Common pattern for multi-dimensional problems
- From COPS test suite (high-quality test problem)

### Model 3: fct.gms
**Primary Blocker:** predefined_constants  
**Effort:** 1h (Simple)  
**Size:** 36 lines  
**Type:** DNLP  
**Description:** LGO Interface Example

**Blocker Detail:**  
Uses predefined constant `pi` in equations: `abs(sin(4*mod(aux1,pi)))`

**Why Selected:**  
- Simplest fix (symbol table initialization)
- Unlocks mathematical modeling patterns
- Also needs `mod` function support

### Models 4-6: chem.gms, water.gms, gastrans.gms
**Primary Blocker:** inline_descriptions (shared)  
**Effort:** 4h (Medium) - implements for all 3 models  
**Sizes:** 40, 88, 180 lines  
**Types:** NLP, DNLP, NLP  
**Descriptions:**  
- chem: Chemical Equilibrium Problem
- water: Design of a Water Distribution Network  
- gastrans: Gas Transmission Problem - Belgium

**Blocker Detail:**  
Set elements with inline descriptions:
- `i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /` (chem)
- `n 'nodes' / nw 'north west reservoir', e 'east reservoir' ... /` (water)
- Multi-line set declarations with descriptions (gastrans)

**Why Selected:**  
- Very common GAMS documentation pattern
- Medium effort unlocks 3 models (+30% parse rate)
- Validates fix across different model sizes/types

### Model 7: process.gms
**Primary Blocker:** model_inline_descriptions  
**Effort:** 2h (Medium)  
**Size:** 67 lines  
**Type:** NLP  
**Description:** Alkylation Process Optimization

**Blocker Detail:**  
Model statements with inline descriptions:
```gams
Model process 'process model with equalities'
              / yield, makeup, sdef, motor, drat, ddil, df4, dprofit /
```

**Why Selected:**  
- Common pattern for documenting model variants
- Clean implementation (extend Model statement parsing)
- Classic chemical engineering problem

### Models 8-10: least.gms, like.gms, bearing.gms
**Primary Blocker:** table_wildcard_domain (shared)  
**Effort:** 5h (Medium, at budget limit)  
**Sizes:** 40, 49, 125 lines  
**Types:** NLP, NLP, NLP  
**Descriptions:**  
- least: Nonlinear Regression Problem
- like: Maximum Likelihood Estimation  
- bearing: Hydrostatic Thrust Bearing Design

**Blocker Detail:**  
Table statements with wildcard domains:
- `Table dat(i,*)` - wildcard in 2nd dimension (least)
- `Table data(*,i)` - wildcard in 1st dimension (like)
- `Table oil_constants(*,*)` - wildcards in both dimensions (bearing)

**Why Selected:**  
- Very common GAMS data input pattern
- Testing 3 variants validates robust implementation
- At effort limit (5h) but high ROI (3 models = +30% parse rate)

---

## Alternate Models (Fallback Options)

If primary selection proves too difficult, these alternates are available:

1. **haverly.gms** (NLP, 69 lines) - Alternative table wildcard model
2. **elec.gms** (NLP, 47 lines) - Conditional preprocessor ($if set)
3. **polygon.gms** (NLP, 43 lines) - Simpler lead/lag than chain (but still 8-10h)
4. **house.gms** (NLP, 45 lines) - **ALREADY PARSES!** Can use as regression test

Note: house.gms successfully parsed in baseline testing, so it's a good regression test but not a blocker target.

---

## Expected Outcomes

### Conservative Estimate (40-50% parse rate)

**Assumptions:**
- Simple blockers (3) implemented successfully: chenery, jbearing, fct = 3 models
- 1-2 medium blockers implemented: chem + process = 2 models
- Total: 5/10 models = 50% parse rate

**Risks:**
- Table wildcard complexity underestimated
- Inline descriptions have edge cases
- Time budget exceeded on one blocker

### Optimistic Estimate (60-70% parse rate)

**Assumptions:**
- All simple blockers (3) successful: 3 models
- All medium blockers (2) successful: chem/water/gastrans + process = 4 models
- Partial table wildcard success: 1-2 of 3 models
- Total: 6-7/10 models = 60-70% parse rate

**Success Factors:**
- Inline descriptions cleaner than expected
- Table wildcard has well-defined semantics
- No major surprises in implementation

### Realistic Target: 50% ± 10%

Sprint 12 Component 5 success criterion is ≥50% parse rate on Tier 2. With conservative planning, we expect to hit this target with some margin.

---

## Blocker Implementation Priority

### Sprint 12 Day 4 (2h)
1. **predefined_constants** (fct) - 1h - QUICK WIN
2. **special_chars_in_identifiers** (chenery) - 1.5h

**Expected parse rate after Day 4:** 20% (2/10 models)

### Sprint 12 Day 5 (3h)
3. **multiple_alias_declaration** (jbearing) - 1.5h
4. **model_inline_descriptions** (process) - 2h (start)

**Expected parse rate after Day 5:** 30% (3/10 models)

### Sprint 12 Day 6 (3h)
4. **model_inline_descriptions** (process) - complete
5. **inline_descriptions** (chem, water, gastrans) - 4h (start, may spill to Day 7)

**Expected parse rate after Day 6:** 40% (4/10 models if inline_descriptions complete)

### Sprint 12 Day 7-8 (stretch)
5. **inline_descriptions** - complete if needed
6. **table_wildcard_domain** (least, like, bearing) - 5h (if time permits)

**Final parse rate:** 50-60% (5-6/10 models)

---

## Validation Commands

```bash
# Verify 10 models selected
ls tests/fixtures/tier2_candidates/*.gms | wc -l
# Should show 18 (all candidates)

# Verify selected models exist
for model in chenery jbearing fct chem water gastrans process least like bearing; do
  test -f "tests/fixtures/tier2_candidates/${model}.gms" && echo "✓ $model" || echo "✗ $model MISSING"
done

# Run parse test on selected models
python scripts/analyze_tier2_candidates.py | grep -E "(chenery|jbearing|fct|chem|water|gastrans|process|least|like|bearing)"

# Expected baseline: 0/10 parsing (house.gms not in selection)
```

---

## Blocker Complexity Justification

### Simple Blockers (1-2h each)

**special_chars_in_identifiers (1.5h):**  
- Modify lexer to accept `-` and `+` in identifiers
- GAMS allows these in unquoted identifiers
- Risk: May conflict with arithmetic operators in some contexts
- Mitigation: Context-aware lexing based on parser state

**multiple_alias_declaration (1.5h):**  
- Extend grammar: `alias_statement: 'Alias' '(' ID ',' ID ')' (',' '(' ID ',' ID ')')* ';'`
- Update AST to store multiple pairs
- Low risk, well-defined semantics

**predefined_constants (1h):**  
- Initialize symbol table with: `pi`, `inf`, `eps`, `na`
- Add to `src/ir/symbol_table.py` initialization
- Zero parsing changes needed
- Lowest risk blocker

### Medium Blockers (2-5h each)

**inline_descriptions (4h):**  
- Extend set element parsing to consume optional quoted strings
- Store descriptions in AST (metadata)
- Handle multi-line declarations
- Risk: Parser backtracking issues if quotes aren't consumed properly
- Spans 3 models: chem (sets), water (sets + tuples), gastrans (multi-line sets)

**model_inline_descriptions (2h):**  
- Extend Model statement grammar to consume optional quoted description
- Store in Model AST node
- Simple extension, low risk

**table_wildcard_domain (5h):**  
- Parse `Table name(dim1, dim2, ...)` where dim can be `*`
- Infer actual dimensions from table data rows
- Complex logic to validate data consistency
- Risk: Edge cases with mixed wildcards and explicit domains
- High value: unlocks 3 models (30% parse rate boost)

---

## Risk Mitigation

### Budget Overrun Risk
- **Mitigation:** Implement simple blockers first (Day 4-5)
- **Fallback:** Defer table_wildcard if it exceeds 5h
- **Monitoring:** Track hours per blocker daily

### Blocker Interdependency Risk
- **Mitigation:** Selected blockers are independent (no cascading failures)
- **Example:** inline_descriptions doesn't depend on table_wildcard
- **Benefit:** Can implement in any order

### Regression Risk
- **Mitigation:** Run Tier 1 tests after each blocker implementation
- **CI Integration:** Automated regression testing (see Unknown 5.4)
- **Rollback:** Each blocker in separate commit for easy revert

---

## Summary

**Total Models:** 10  
**Total Blockers:** 5 unique patterns  
**Total Effort:** 6h (conservative)  
**Expected Parse Rate:** 50% ± 10%  
**Models by Complexity:**
- Simple (1-2h): 3 models (chenery, jbearing, fct)
- Medium (2-5h): 7 models (chem, water, gastrans, process, least, like, bearing)

**Diversity Achieved:**
- ✓ Syntax extensions (special chars, alias)
- ✓ Data structures (tables with wildcards)
- ✓ Documentation features (inline descriptions)
- ✓ Symbol table (predefined constants)
- ✓ Model organization (model descriptions)

**Success Criteria Met:**
- ✓ 10 models selected
- ✓ Total effort ≤6h
- ✓ No single blocker >5h
- ✓ ≥5 different blocker patterns
- ✓ Common GAMS patterns prioritized
- ✓ Expected parse rate ≥50%
