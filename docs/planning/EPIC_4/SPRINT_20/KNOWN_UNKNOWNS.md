# Sprint 20 Known Unknowns

**Created:** February 18, 2026
**Status:** Active — Pre-Sprint 20
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 20 — IndexOffset end-to-end pipeline, deferred Sprint 19 solver blockers, remaining lexer_invalid_char reduction, and full pipeline match rate improvement

---

## Overview

This document identifies all assumptions and unknowns for Sprint 20 features **before** implementation begins. This proactive approach continues the methodology that achieved excellent results in Sprint 19 (26 unknowns documented; 22 verified; zero blocking late surprises).

**Sprint 20 Scope (~50-64h across 4 workstreams):**
1. **IndexOffset end-to-end pipeline** — close remaining gaps (emit, parser, end-to-end testing of 8 blocked models)
2. **Deferred Sprint 19 solver blockers** — `.l` initialization emission (#753/#757), accounting variable detection (#764), AD condition propagation (#763), min/max objective-defining equations (#789)
3. **Remaining lexer_invalid_char reduction** — 27 remain; Subcategories G, H, I (re-check), J, K not yet addressed
4. **Translation internal error fixes and full pipeline match rate** — translate errors, objective extraction, pipeline match gap (9/25 currently match)

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 268–385 for complete Sprint 20 deliverables and acceptance criteria. See `docs/planning/EPIC_4/SPRINT_19/SPRINT_RETROSPECTIVE.md` for Sprint 19 lessons learned.

**Lessons from Sprint 19:** Known Unknowns process prevented late surprises. Key lesson: always run a CLI smoke test before declaring an issue "not fixable" (#671 was already resolved but nearly missed). Also: IndexOffset IR already existed since Sprint 9 — the prep audit prevented redundant design work.

**Epic 4 Baseline (Sprint 19 Final):** Parse 107/160 (66.9%), Translate 73, Solve 25, Full Pipeline Match 9, lexer_invalid_char 27, internal_error 6, Tests 3,579.

---

## How to Use This Document

### Before Sprint 20 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 20
1. Review daily during standup
2. Add newly discovered unknowns in the "Newly Discovered Unknowns" section
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 26
**By Priority:**
- Critical: 6 (~23%)
- High: 11 (~42%)
- Medium: 7 (~27%)
- Low: 2 (~8%)

**By Category:**
- Category 1 (Variable Initialization Emission): 4 unknowns
- Category 2 (Accounting Variable Detection): 4 unknowns
- Category 3 (AD Condition Propagation): 3 unknowns
- Category 4 (Remaining lexer_invalid_char Models): 4 unknowns
- Category 5 (Full Pipeline Match Rate): 4 unknowns
- Category 6 (IndexOffset Implementation): 4 unknowns
- Category 7 (Translation Internal Error Fixes): 2 unknowns
- Category 8 (Objective Extraction Enhancement): 1 unknown

**Estimated Research Time:** 29–37 hours (across prep tasks 2–10)

---

## Table of Contents

1. [Category 1: Variable Initialization Emission](#category-1-variable-initialization-emission)
2. [Category 2: Accounting Variable Detection](#category-2-accounting-variable-detection)
3. [Category 3: AD Condition Propagation](#category-3-ad-condition-propagation)
4. [Category 4: Remaining lexer_invalid_char Models](#category-4-remaining-lexer_invalid_char-models)
5. [Category 5: Full Pipeline Match Rate](#category-5-full-pipeline-match-rate)
6. [Category 6: IndexOffset Implementation](#category-6-indexoffset-implementation)
7. [Category 7: Translation Internal Error Fixes](#category-7-translation-internal-error-fixes)
8. [Category 8: Objective Extraction Enhancement](#category-8-objective-extraction-enhancement)
9. [Template for New Unknowns](#template-for-new-unknowns)
10. [Next Steps](#next-steps)
11. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Variable Initialization Emission

## Unknown 1.1: Does the IR currently capture `.l` variable level assignments from GAMS source?

### Priority
**Critical** — Determines whether `.l` emission is an IR parsing gap or purely an emitter gap

### Assumption
The IR parser (`src/ir/parser.py`) already parses and stores `.l` (variable level) assignments from GAMS source files. The emit layer simply needs to be extended to output these as GAMS assignment statements in the MCP prolog.

### Research Questions
1. Does `parse_file()` on `circle.gms` produce any IR node for `x.l(i) = <value>` assignments?
2. What AST node type represents attribute assignments in the IR? (`AttrAssignment`? `Assignment` with `attr` field?)
3. Are `.l` assignments stored separately from equation definitions, or mixed in with general assignments?
4. Does the IR distinguish between `.l`, `.lo`, `.up`, `.fx`, `.scale` attribute assignments?
5. If `.l` assignments are not captured, is the grammar missing the rule, or does the transformer drop them?

### How to Verify
```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
ir = parse_file('data/gamslib/raw/circle.gms')
# Look for any attribute assignments
for key in dir(ir): print(key, type(getattr(ir, key)))
"
grep -n '\.l\|var_attr\|attr_assign\|level' src/ir/parser.py | head -20
grep -n 'AttrAssign\|level\|\.l' src/ir/ast.py | head -20
```

### Risk if Wrong
If `.l` assignments are NOT captured in the IR, the fix requires both IR parser changes and emitter changes (~4–6h instead of ~2h). If the grammar rule is entirely missing, it may also affect `.lo`, `.up`, `.fx`, `.scale` — requiring a broader fix.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.2: Will `.l` initialization alone resolve PATH infeasibility for circle (#753) and bearing (#757)?

### Priority
**Critical** — Determines whether Priority 1 delivers the expected +2–4 model improvement

### Assumption
The primary reason circle and bearing fail with PATH "model status 5 locally infeasible" is poor starting point initialization. Emitting `.l` assignments in the MCP prolog will provide PATH with a good starting point close to the NLP solution, allowing it to converge.

### Research Questions
1. Does circle.gms have `.l` assignments that set starting values close to the NLP solution?
2. For bearing.gms, are `.l` assignments present, or is `.scale` (scaling) the primary blocker?
3. Does the circle MCP deterministic fix (execseed, Sprint 19 PR #750) make the starting point problem moot, or does the random data issue still affect convergence even with fixed seed?
4. Has PATH ever converged on circle/bearing when given correct starting values manually?
5. Are there other models in the "solve success" category that succeeded specifically because they had good `.l` initializations emitted?

### How to Verify
```bash
# Manually add .l assignments to circle_mcp.gms and test
# Compare before/after PATH residuals
python -m src.cli data/gamslib/raw/circle.gms
# Check if model has .l assignments in source
grep "\.l(" data/gamslib/raw/circle.gms | head -10
grep "\.l(" data/gamslib/raw/bearing.gms | head -10
```

### Risk if Wrong
If `.l` initialization is insufficient (bearing also needs `.scale`, or circle has a KKT formulation error), Priority 1 delivers fewer models than expected. Sprint 20 solve-rate improvement may be limited to +1 model instead of +2–4.

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.3: Does the MCP emit pipeline have a defined prolog section for variable initializations?

### Priority
**High** — Determines fix location and approach in the emit layer

### Assumption
The MCP emitter (`src/emit/emit_gams.py` or `src/emit/model.py`) has a logical section for "prolog" statements (executed before the MCP model solve) where `.l` assignments can be inserted.

### Research Questions
1. What is the structure of a generated `*_mcp.gms` file? (Declarations → Parameter assignments → Model statement → Solve statement?)
2. Is there an existing "prolog" concept in the emitter, or would we need to create one?
3. Does the emitter currently emit any other assignments before the `Model` statement?
4. Would `.l` assignments need to go before or after parameter data assignments?

### How to Verify
```bash
head -60 data/gamslib/mcp/circle_mcp.gms
grep -n "def emit\|prolog\|Model\|Solve\|assignment" src/emit/emit_gams.py | head -30
```

### Risk if Wrong
If the emitter has no concept of pre-solve assignments, adding `.l` initialization requires more structural changes to the emitter (~3–4h instead of ~1h).

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.4: Are there models beyond circle and bearing that would benefit from `.l` initialization?

### Priority
**Medium** — Determines the full impact of Priority 1

### Assumption
The `.l` initialization emission fix is not circle/bearing-specific. Any model in the corpus that has `.l` assignments in the original GAMS source and currently fails PATH with "locally infeasible" would benefit.

### Research Questions
1. How many models in the 219-model catalog have `.l` assignments in their GAMS source?
2. Of the 16 models that solve but don't match the reference solution, how many use `.l` assignments?
3. Are `.l` assignments common in LP/NLP models, or are they rare?

### How to Verify
```bash
grep -rl "\.l(" data/gamslib/raw/ | wc -l
grep -rl "\.l(" data/gamslib/raw/ | xargs -I{} basename {} .gms
```

### Risk if Wrong
Low impact — undercount means pleasant surprise; overcount means the fix delivers fewer models.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 2: Accounting Variable Detection

## Unknown 2.1: What is the precise structural pattern of accounting variables in mexss?

### Priority
**Critical** — Determines whether the detection algorithm is correct before implementation

### Assumption
Accounting variables in mexss follow the pattern: variable appears exclusively on the LHS of a single `=E=` equation, with no contribution to the objective function, making them definitional identities that should not receive stationarity equations.

### Research Questions
1. In mexss.gms, which specific variables are the accounting variables?
2. Do they appear on the LHS of exactly one `=E=` equation, or multiple?
3. Do they appear anywhere in the objective equation's RHS (directly or through a chain of equations)?
4. Are they indexed variables or scalars?
5. Are there similar patterns in any of the 25 currently-solving models that would be falsely classified?

### How to Verify
```bash
grep -A3 "=E=" data/gamslib/raw/mexss.gms | head -40
python -m src.cli data/gamslib/raw/mexss.gms 2>&1 | grep "accounting\|stat_x\|infeasible" | head -20
```

### Risk if Wrong
If the pattern is more complex (e.g., accounting variables appear in multiple equations, or the objective dependency is indirect), the detection algorithm will need refinement. False positive risk is critical — incorrectly excluding an optimization variable from the KKT system produces a silently wrong MCP.

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.2: Can accounting variables be reliably detected using only static IR analysis?

### Priority
**High** — Determines implementation approach (static analysis vs. runtime dependency graph)

### Assumption
The three-criterion heuristic (LHS-only occurrence + equality constraint only + no objective reachability) can be computed from the static IR without requiring a runtime dependency graph traversal or symbolic solver.

### Research Questions
1. Does the IR's `ModelIR` provide enough information to check "objective reachability" without additional analysis?
2. Is there an existing dependency graph or equation structure in the IR that could be reused?
3. Could a variable appear to be an accounting variable based on syntactic analysis but actually affect the objective through GAMS parameter computation (not captured in IR)?
4. What is the computational cost of the detection scan over a model's variable set?

### How to Verify
```bash
grep -n "dependency\|objective\|equation_map\|var_to_eq" src/ir/ast.py src/kkt/stationarity.py | head -20
# Check if ModelIR has equation-to-variable mapping
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
ir = parse_file('data/gamslib/raw/mexss.gms')
print(dir(ir))
"
```

### Risk if Wrong
If static analysis is insufficient, we need to build a runtime dependency graph — a significant architectural addition (~8–12h). In that case, defer accounting variable detection to Sprint 21.

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.3: How many models beyond mexss would benefit from accounting variable detection?

### Priority
**Medium** — Determines the ROI of this workstream

### Assumption
Accounting variable patterns (identity equations defining aggregate variables) are common enough across the 219-model corpus that fixing mexss will also unblock 1–2 additional models with the same pattern.

### Research Questions
1. Which other models in the corpus have equations of the form `total_x = sum(i, x(i))`?
2. Are any of these models currently in the "translate" or "solve" failure category?
3. Would unblocking mexss-style accounting variables change the solve count significantly?

### How to Verify
```bash
# Look for sum-assignment patterns in all raw models
grep -rl "=E=.*sum(" data/gamslib/raw/ | wc -l
```

### Risk if Wrong
Low impact — discovering fewer affected models means Priority 2 has a smaller ROI than expected but doesn't block the sprint.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.4: Will accounting variable detection break any currently-solving model?

### Priority
**High** — Critical regression check before enabling the feature

### Assumption
The detection heuristic, when applied to all 25 currently-solving models, will not incorrectly classify any optimization variable as an accounting variable.

### Research Questions
1. Do any of the 25 currently-solving models have variables that match all three accounting-variable criteria?
2. Are there edge cases where the LHS-only criterion fires incorrectly (e.g., a variable used in one equality and one inequality)?
3. Does the objective-reachability criterion handle chain-of-equality cases correctly?

### How to Verify
Apply the proposed detection algorithm to each of the 25 currently-solving models and verify: all identified "accounting variables" are genuinely definitional (cross-check with original GAMS model).

### Risk if Wrong
If even one currently-solving model is broken by false positive detection, the feature cannot ship without a guard. The test suite should catch this automatically once the detection is implemented.

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 3: AD Condition Propagation

## Unknown 3.1: What is the exact form of the `$` condition that guards the denominator in chenery?

### Priority
**High** — Determines the scope and complexity of the AD condition propagation fix

### Assumption
The chenery model uses a `$` (dollar condition) immediately adjacent to a division expression to guard against division by zero, and the AD system needs to propagate this condition into the derivative of that expression.

### Research Questions
1. What is the exact GAMS syntax of the conditional division in chenery.gms?
2. Is the `$` condition on the equation level (e.g., `eq(i)$(del(i) > 0).. expr`) or inline (e.g., `x / del(i)$( del(i) > 0)`)?
3. Does the AD system currently propagate equation-level `$` conditions into derivatives at all?
4. Is this a pattern in multiple models, or unique to chenery?
5. What GAMS error does the generated MCP produce? (EXECERROR=1 division by zero?)

### How to Verify
```bash
grep -n "\$\|del\|division\|/\s*del" data/gamslib/raw/chenery.gms | head -20
python -m src.cli data/gamslib/raw/chenery.gms 2>&1 | tail -20
# Check the generated MCP for the problematic expression
grep "del\|division" data/gamslib/mcp/chenery_mcp.gms 2>/dev/null | head -10
```

### Risk if Wrong
If `$` conditions are inline (not equation-level), propagation is much harder — the AD system would need to track conditional domains through expression trees. Estimated effort jumps from ~6–8h to ~12–16h (architectural work).

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.2: Does the AD system have any existing mechanism for condition propagation?

### Priority
**Medium** — Determines whether condition propagation is a new feature or an extension of existing code

### Assumption
The AD system (`src/ad/`) has some concept of domain/condition tracking, and the `$` condition propagation fix is an extension of existing logic rather than a completely new capability.

### Research Questions
1. How does the AD system currently handle `DollarConditional` nodes in the IR?
2. Does `_apply_index_substitution` in `src/ad/derivative_rules.py` handle `DollarConditional` correctly?
3. Is there an existing `propagate_condition` or similar concept in the KKT assembly?
4. Does the Sprint 19 IndexOffset work (`_substitute_index` + `_apply_index_substitution`) provide a pattern for condition propagation?

### How to Verify
```bash
grep -n "DollarConditional\|condition\|dollar\|propagat" src/ad/derivative_rules.py src/kkt/stationarity.py | head -30
grep -n "DollarConditional" src/ir/ast.py | head -10
```

### Risk if Wrong
If the AD system has no concept of condition tracking, implementing condition propagation requires adding a new "conditional derivative" node type to the IR — a significant architectural addition that could spill into Sprint 21.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.3: How many models have conditional denominator patterns similar to chenery?

### Priority
**Low** — ROI assessment for the AD condition propagation workstream

### Assumption
The conditional denominator pattern (division guarded by a `$` condition) affects more than just chenery — there are 2–4 additional models in the corpus with similar patterns.

### Research Questions
1. How many raw GAMS models use the pattern `expr / param_or_var $(condition)` or similar?
2. Of these, which are currently in the translate/solve failure category?

### How to Verify
```bash
grep -rl "/.*\$\|\$.*/" data/gamslib/raw/ | wc -l
```

### Risk if Wrong
Low impact — discovering fewer affected models means Priority 3 has smaller ROI than expected.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 4: Remaining lexer_invalid_char Models

## Unknown 4.1: What are the exact subcategories of the 27 remaining lexer_invalid_char models?

### Priority
**High** — Determines which grammar additions to prioritize for Sprint 20

### Assumption
Of the 27 remaining `lexer_invalid_char` models after Sprint 19, the dominant subcategories are G (set element descriptions), H (control flow), J (bracket/brace), and K (miscellaneous), with a few residual C (put statement) and D (lead/lag) models.

### Research Questions
1. How many models fall in each subcategory (G, H, J, K + residual C, D)?
2. Have any models moved from `lexer_invalid_char` to `success` or other categories since the Sprint 19 LEXER_ERROR_CATALOG was written?
3. Are there new subcategories not in the A–K taxonomy?
4. Which subcategory has the most models and thus the highest ROI for a grammar fix?
5. Are any of the 27 models in subcategory D (lead/lag) — would these be fixed automatically by the IndexOffset work?

### How to Verify
```bash
.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet 2>&1 | grep lexer_invalid_char
# Run each failing model individually to get the specific token
for model in $(list of 27 models); do
  python -m src.cli data/gamslib/raw/$model.gms 2>&1 | grep "Token\|unexpected\|Unexpected" | head -2
done
```

### Risk if Wrong
If the subcategory distribution is different than assumed (e.g., most remaining models are in K — miscellaneous, which requires investigation), Sprint 20 grammar work may deliver fewer models than the +10–15 target. This is the most likely unknown to cause scope adjustment.

### Estimated Research Time
2–3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.2: Are there lexer_invalid_char models that are already fixed by Sprint 19 work but not yet re-run?

### Priority
**Medium** — Quick win check before planning new grammar work

### Assumption
All 27 remaining lexer_invalid_char models have been re-run against the Sprint 19 final codebase and confirmed to still fail. No "silent fixes" from Sprint 19 grammar additions are lurking in the untested 27.

### Research Questions
1. When was the last full pipeline retest run? (If pre-Sprint 19, some models may have silently been fixed)
2. Do any of the 27 models use Subcategory A/B/F/I syntax that was added in Sprint 19?
3. Does the Sprint 19 `eqn_head_mixed_list` rule fix any of the remaining models?

### How to Verify
```bash
# Re-run parse-only on all 27 models against current main
.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet
```

### Risk if Wrong
If there are silent fixes, the baseline count is lower than 27 — a pleasant surprise, not a problem.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.3: Are the Subcategory G (set element descriptions) fixes straightforward grammar additions?

### Priority
**Medium** — Determines effort estimate for highest-ROI remaining subcategory

### Assumption
Subcategory G models fail because the grammar doesn't allow descriptive text (quoted strings) after set element names in set data blocks. This is a grammar-only fix with no IR changes needed.

### Research Questions
1. What is the exact failing token in Subcategory G models?
2. Is the fix a simple rule addition (e.g., `set_element: ID (STRING)?`) or does it require grammar restructuring?
3. Are there interactions with existing set data rules that could cause regressions?

### How to Verify
```bash
# Pick a Subcategory G model and run with parse trace
python -c "
from lark import Lark
import sys; sys.setrecursionlimit(50000)
# Parse with debug output to see failing rule
"
```

### Risk if Wrong
If Subcategory G requires IR changes (e.g., storing descriptions in the IR), effort increases from ~2h to ~4h.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.4: Do lead/lag (Subcategory D) lexer failures get resolved by IndexOffset grammar work?

### Priority
**High** — Determines whether indexOffset workstream and lexer workstream can share a deliverable

### Assumption
The 2 remaining Subcategory D (lead/lag) models in `lexer_invalid_char` will be fixed as a side effect of the IndexOffset grammar additions in the Sprint 20 IndexOffset workstream, without needing separate lexer work.

### Research Questions
1. Which specific models are still in Subcategory D after Sprint 19?
2. Does the IndexOffset grammar added in Sprint 19 (PR #785) cover the failing tokens in these models?
3. Are there lead/lag syntax variants in these models not covered by `offset_paren`/`offset_func`?

### How to Verify
```bash
# Run ampl and otpop (the Subcategory D models) through current parser
python -m src.cli data/gamslib/raw/ampl.gms 2>&1 | head -20
python -m src.cli data/gamslib/raw/otpop.gms 2>&1 | head -20
```

### Risk if Wrong
If Subcategory D models need separate grammar additions beyond IndexOffset work, lexer effort increases by ~2h.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 5: Full Pipeline Match Rate

## Unknown 5.1: What is the primary cause of the 16-model solve-success / pipeline-match gap?

### Priority
**Critical** — Determines Sprint 20 strategy for Priority 5 (full pipeline match rate)

### Assumption
The majority of the 16 models that solve but don't match the reference solution fail because of poor starting point initialization (missing `.l` assignments), meaning the `.l` emission fix (Priority 1) will automatically resolve many of these matches as a side effect.

### Research Questions
1. For each of the 16 non-matching models, what is the objective value gap (MCP vs NLP)?
2. How many of the 16 have `.l` assignments in their GAMS source?
3. How many have objective gaps that suggest they found a different local minimum vs. a numerical precision issue?
4. Are any of the 16 models provably non-convex (where multiple local minima exist)?
5. Do any of the 9 currently-matching models succeed specifically because they initialized well?

### How to Verify
```bash
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
# Find models with MCP solve success but no pipeline match
models = data['models']
for m in models:
    solve = m.get('mcp_solve', {})
    comparison = m.get('solution_comparison', {})
    if solve.get('status') == 'success' and comparison.get('objective_match') == False:
        print(m.get('model_name', '<unknown>'), 'gap:', comparison.get('relative_difference'))
"
```

### Risk if Wrong
If the gap is caused by KKT formulation errors (not initialization), Pipeline Match improvement requires debugging individual model KKT systems — a much harder, model-specific task (~4–8h per model). Sprint 20 match rate target may be unachievable without PATH author consultation.

### Estimated Research Time
2–3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.2: Is the solution comparison tolerance calibrated correctly for all solving models?

### Priority
**High** — Determines if any "non-matches" are actually matches within appropriate tolerance

### Assumption
The current solution comparison uses a fixed relative tolerance (e.g., 1% or 0.1%) that is appropriate for all 25 solving models. No currently non-matching models are actually within acceptable tolerance under a tighter or different tolerance policy.

### Research Questions
1. What tolerance is currently used for the full pipeline match check?
2. Are any of the 16 non-matching models within 5% of the reference solution (possibly matching with looser tolerance)?
3. Should some models have model-specific tolerances based on their problem scaling?
4. Does the comparison use relative tolerance, absolute tolerance, or both?

### How to Verify
```bash
grep -n "tolerance\|tol\|atol\|rtol\|match" src/validation/ -r | head -20
# Find the comparison function and its tolerance parameter
```

### Risk if Wrong
If the tolerance is too tight, loosening it could convert several non-matches to matches — a quick win without any code changes to the solver. If the tolerance is too loose, we may be incorrectly counting some models as matching.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.3: Do any of the 16 non-matching models have scale-related issues (`.scale` attribute)?

### Priority
**Medium** — Determines whether `.scale` emission is needed for Sprint 20

### Assumption
Scaling issues (`.scale` attribute in GAMS) are secondary to initialization issues. Most of the 16 non-matching models can be fixed without `.scale` emission support. `.scale` is a Sprint 21+ item.

### Research Questions
1. How many of the 16 non-matching models use `.scale` attributes in their GAMS source?
2. Does PATH perform better when scales are set correctly vs. not at all?
3. Is `.scale` emission feasible in Sprint 20, or should it be explicitly deferred?

### How to Verify
```bash
grep -rl "\.scale(" data/gamslib/raw/ | xargs -I{} basename {} .gms
```

### Risk if Wrong
If `.scale` turns out to be the primary blocker for several models, the `.l` emission fix (Priority 1) will have limited impact on the match rate, and Sprint 20's Priority 5 target of 10+ matches may not be achievable.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.4: Are any of the 9 currently-matching models at risk of regression from Sprint 20 changes?

### Priority
**High** — Critical regression check for all four workstreams

### Assumption
The 9 models currently achieving full pipeline match (ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport) will not be broken by any of the Sprint 20 code changes.

### Research Questions
1. Do any of the 9 matching models use lead/lag indexing (IndexOffset workstream risk)?
2. Do any use accounting-variable-like patterns (accounting variable detection risk)?
3. Do any have conditional denominators (AD condition propagation risk)?
4. Are all 9 currently part of the golden-file test suite?

### How to Verify
```bash
make test
# Check which models are in golden file tests
grep -r "ajax\|blend\|demo1\|himmel11\|house\|mathopt2\|prodmix\|rbrock\|trnsport" tests/ | grep "golden\|fixture\|parametrize" | head -20
```

### Risk if Wrong
If a Sprint 20 change breaks any of the 9 matching models, the full pipeline match count drops below 9 — a regression. The test suite should catch this, but only if golden-file tests exist for all 9 models.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 6: IndexOffset Implementation

## Unknown 6.1: What is the current pipeline failure stage for each of the 8 IndexOffset-blocked models?

### Priority
**Critical** — Determines remaining work and revised effort estimate for the IndexOffset workstream

### Assumption
After Sprint 19's AD integration (PRs #779, #785), the 8 blocked models have moved from `lexer_invalid_char` or `internal_error` to a later failure stage (translate or solve). The remaining work is ≤4h of emit/parser fixes and end-to-end testing.

### Research Questions
1. What is the current pipeline status of each of the 8 models: ampl, otpop, and 6 others?
2. Do any of the 8 models still fail at the parse stage after Sprint 19?
3. Do any fail at translate (if AD still has gaps)?
4. Does any fail at solve (PATH infeasibility — unrelated to IndexOffset)?
5. Is the Sprint 19 xfail test (`sum-collapse-with-IndexOffset-wrt`) the last remaining AD gap?

### How to Verify
```bash
for model in ampl otpop launch robert pak mine tabora sparta; do
  echo "=== $model ==="
  python -m src.cli data/gamslib/raw/$model.gms 2>&1 | tail -5
done
```

### Risk if Wrong
If any of the 8 models still fail at the parse stage (grammar gap), the IndexOffset workstream needs more grammar work than estimated. If AD still has gaps beyond the xfail test, the ~4h estimate increases to ~8h.

### Estimated Research Time
1–2 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.2: Does the xfail test (sum-collapse-with-IndexOffset-wrt) represent a real blocker for any model?

### Priority
**High** — Determines whether the Sprint 19 xfail test needs to be fixed in Sprint 20

### Assumption
The one xfail test (`sum-collapse-with-IndexOffset-wrt`, deferred from Sprint 19 Day 12) represents an edge case that doesn't affect any of the 8 blocked models in practice. It can be fixed in Sprint 20 as a cleanup item without blocking model translation.

### Research Questions
1. What exactly does the xfail test test? Which expression pattern triggers it?
2. Do any of the 8 blocked models have `sum(...)` expressions with IndexOffset inside the summand that would trigger this case?
3. Is the issue in `_apply_index_substitution` when processing Sum nodes with IndexOffset bases?
4. What is the correct fix — extend `_apply_index_substitution` to handle Sum collapse, or prevent Sum collapse when IndexOffset bases are present?

### How to Verify
```bash
# Find the xfail test
grep -rn "xfail\|sum.collapse.*IndexOffset\|IndexOffset.*wrt" tests/ | head -10
# Run it to see the failure mode
python -m pytest tests/ -k "IndexOffset" -v 2>&1 | tail -20
```

### Risk if Wrong
If the xfail case is a real blocker for one of the 8 models, fixing it moves from a cleanup item to a critical path item — adding ~3h to the IndexOffset workstream.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.3: Does the emit layer correctly handle circular lead/lag (`++`/`--`) syntax?

### Priority
**Medium** — Determines whether circular IndexOffset is covered by existing code

### Assumption
The existing `_format_mixed_indices()` in the emit layer handles both linear (`+`/`-`) and circular (`++`/`--`) lead/lag syntax correctly, since the `INDEX_OFFSET_DESIGN_OPTIONS.md` stated "Emit layer already handles IndexOffset via `_format_mixed_indices()`."

### Research Questions
1. Does `_format_mixed_indices()` in `src/emit/expr_to_gams.py` have a case for circular offset?
2. The Sprint 19 design document mentioned `himmel16` uses `i++1` — does this model currently translate successfully?
3. Are there any of the 8 blocked models that use circular (not linear) lead/lag?

### How to Verify
```bash
grep -n "circular\|\\+\\+\|--\|format_mixed\|IndexOffset" src/emit/expr_to_gams.py | head -20
python -m src.cli data/gamslib/raw/himmel16.gms 2>&1 | tail -5
```

### Risk if Wrong
If circular lead/lag isn't handled by the emit layer, 1–2 models may still fail after all other IndexOffset work is done — requiring an additional ~2h fix.

### Estimated Research Time
30 minutes

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.4: Will all 8 IndexOffset-blocked models translate and solve after the remaining gaps are closed?

### Priority
**Medium** — Final acceptance check for the IndexOffset workstream

### Assumption
All 8 models blocked by IndexOffset issues will successfully translate and generate a valid MCP once the remaining gaps (emit, parser, xfail test) are closed. Solve infeasibility (PATH model status 5) is not expected for these models.

### Research Questions
1. Are any of the 8 models non-convex (PATH may fail regardless of correct formulation)?
2. Do any of the 8 models have other blocking issues beyond IndexOffset (e.g., the `orani` model had cross-indexed sums as a separate issue)?
3. Will all 8 produce objective values matching the reference NLP?

### How to Verify
After implementing all IndexOffset fixes: run each model through the full pipeline and verify PATH model status and objective value.

### Risk if Wrong
If some models have secondary blockers (not IndexOffset-related), they won't solve even after IndexOffset is fixed — the workstream delivers fewer models than expected.

### Estimated Research Time
Verification during Sprint 20 implementation (not a prep task).

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 7: Translation Internal Error Fixes

## Unknown 7.1: How many models currently fail with internal_error at the translate stage, and what are their root causes?

### Priority
**High** — Determines scope and feasibility of the translation internal error workstream

### Assumption
Approximately 5 models fail with `internal_error` at the translate stage (as stated in PROJECT_PLAN.md). Their root causes are primarily missing derivative rules or IR construction crashes, each fixable in 1–2h with targeted code changes.

### Research Questions
1. What is the current count of translate-stage internal errors (may have changed after Sprint 19's 46 new parsed models)?
2. For each failing model, what is the specific exception type and location (file, function, line)?
3. Are any of the translate failures related to IndexOffset (would be fixed by IndexOffset workstream)?
4. Are any due to newly-parsed models entering translate for the first time after Sprint 19?
5. Do any require architectural changes (deferred) vs. targeted rule additions (Sprint 20)?

### How to Verify
```bash
.venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | grep -A2 "internal_error.*translate\|translate.*internal"
# Run each failing model individually to get stack trace
```

### Risk if Wrong
If there are significantly more than 5 translate failures (e.g., 10–15 after the Sprint 19 parse improvement), the translate error workstream will exceed its 6–8h budget. Some may need to be deferred to Sprint 21.

### Estimated Research Time
2–3 hours

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 7.2: Are any translate internal errors caused by the same root cause (systematic fix vs. case-by-case)?

### Priority
**Medium** — Determines whether a single fix resolves multiple models

### Assumption
At least 2 of the translate internal errors share a common root cause (e.g., all fail on the same missing AD rule for a specific function like `log` or `exp` in a specific context), allowing a single fix to unblock multiple models.

### Research Questions
1. Do any translate failures share the same exception type and call stack?
2. Are there any GAMS functions (like `arctan`, `log10`, `sigmoid`) that are parsed but lack derivative rules?
3. Do any failures occur in the same function (`_build_stationarity_equations`, `_compute_gradient`, etc.)?

### How to Verify
```bash
# Collect stack traces for all translate failures and compare
python -m pytest tests/integration/ -k "translate" -v 2>&1 | grep "Error\|Traceback\|File" | sort | uniq -c | sort -rn
```

### Risk if Wrong
Low impact — if each failure has a unique root cause, the workstream takes more calendar time (sequential debugging) but the same total effort.

### Estimated Research Time
30 minutes (part of Task 5 work)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 8: Objective Extraction Enhancement

## Unknown 8.1: How many `model_no_objective_def` models exist and what patterns do they use?

### Priority
**Medium** — Determines scope of the objective extraction enhancement workstream

### Assumption
Approximately 5 models fail with `model_no_objective_def` (objective variable not identified). These use implicit objective patterns (e.g., objective defined in a constraint rather than a `minimize obj` statement) that can be detected with pattern matching.

### Research Questions
1. What is the current count of `model_no_objective_def` failures?
2. What are the specific patterns (e.g., `min_nlp /all/` solve statement without explicit objective declaration)?
3. Can objective detection be improved without changing the IR (purely at the model assembly level)?
4. PROJECT_PLAN.md targets "at least 3 of 5" — is 5 the correct model count?
5. Are any `model_no_objective_def` models also blocked by lexer or translate issues (compounding failures)?

### How to Verify
```bash
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
models = data['models']
no_obj = [m['model_name'] for m in models
          if m.get('nlp2mcp_translate', {}).get('status') == 'failure'
          and (m.get('nlp2mcp_translate', {}).get('error') or {}).get('category') == 'model_no_objective_def']
print('no_objective_def models:', sorted(no_obj))
"
```

### Risk if Wrong
If the count is higher than 5 (e.g., 10–12 models), the objective extraction workstream is larger than planned. If the patterns are very diverse (no common fix), the "at least 3 of 5" target may be unachievable in Sprint 20.

### Estimated Research Time
1 hour

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Template for New Unknowns

Use this template when adding unknowns discovered during Sprint 20:

```markdown
## Unknown X.Y: [Descriptive title]

### Priority
**[Critical/High/Medium/Low]** — [One-sentence reason]

### Assumption
[The assumption being made that needs to be validated]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify
[Bash commands or experiments]

### Risk if Wrong
[Impact on sprint if assumption is incorrect]

### Estimated Research Time
[N hours]

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE
```

---

# Next Steps

## Before Sprint 20 Day 1

1. **Task 2 (IndexOffset Audit):** Verify Unknowns 6.1, 6.2, 6.3
2. **Task 3 (lexer_invalid_char Catalog):** Verify Unknowns 4.1, 4.2, 4.3, 4.4
3. **Task 4 (.l Emission Investigation):** Verify Unknowns 1.1, 1.2, 1.3, 1.4
4. **Task 5 (Translate Error Audit):** Verify Unknowns 7.1, 7.2
5. **Task 6 (Pipeline Match Analysis):** Verify Unknowns 5.1, 5.2, 5.3, 5.4
6. **Task 7 (Accounting Variable Design):** Verify Unknowns 2.1, 2.2, 2.3, 2.4
7. **Task 8 (Sprint 19 Retrospective Review):** Inform Unknown 3.1, 3.2
8. **Task 9 (Baseline Snapshot):** Verify Unknown 4.2 (re-confirm 27 count)
9. **Task 10 (Sprint 20 Plan):** Uses all verified unknowns to calibrate sprint schedule

## During Sprint 20

- Update this document daily with new findings
- Add newly discovered unknowns in the Newly Discovered section
- Update "Verification Results" for each unknown as it is confirmed or corrected

## Newly Discovered Unknowns

*(Add unknowns discovered during Sprint 20 here)*

---

# Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns. All tasks should update the Verification Results sections in this document upon completion.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Audit IndexOffset End-to-End Pipeline State | 6.1, 6.2, 6.3 | Run 8 models through pipeline; check xfail test; verify emit layer |
| Task 3: Catalog Remaining lexer_invalid_char Subcategories | 4.1, 4.2, 4.3, 4.4 | Re-run 27 models; reclassify into subcategories; check D overlap with IndexOffset |
| Task 4: Investigate .l Initialization Emission Gap | 1.1, 1.2, 1.3, 1.4 | Trace .l through IR; check emit structure; manually test circle/bearing |
| Task 5: Audit Translate internal_error Models | 7.1, 7.2, 8.1 | Run full pipeline; collect stack traces; identify patterns; check no_objective_def count |
| Task 6: Investigate Full Pipeline Match Divergence | 5.1, 5.2, 5.3, 5.4 | Analyze 16 non-matching models; check tolerance; check .scale usage; verify golden files |
| Task 7: Design Accounting Variable Detection | 2.1, 2.2, 2.3, 2.4 | Study mexss; formalize algorithm; test false positive risk on 25 solving models |
| Task 8: Review Sprint 19 Retrospective Action Items | 3.1, 3.2 (partial) | Retrospective mentions AD condition propagation scope; confirm chenery pattern |
| Task 9: Snapshot Baseline Metrics | 4.2 (confirms 27 count) | Re-run full pipeline; confirms all baseline numbers including lexer_invalid_char count |
| Task 10: Plan Sprint 20 Detailed Schedule | Integrates all verified unknowns | Uses findings from Tasks 2–9 to calibrate sprint plan |
