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
- Critical: 5 (~19%)
- High: 10 (~38%)
- Medium: 10 (~38%)
- Low: 1 (~4%)

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
✅ Status: VERIFIED

**Findings (2026-02-19):** The IR captures `.l` **partially** — constant values only. See `L_INIT_EMISSION_DESIGN.md`.

**Constant `.l` IS captured** (stored in `VariableDef.l` / `VariableDef.l_map`). Example: bearing's `R.l = 6.0`, `mu.l = 6e-6` — these are stored via `_set_bound_value()` in `_apply_variable_bound`.

**Expression-based `.l` is NOT captured.** In `_handle_assign` (parser.py ~line 3562), when `is_variable_bound = True` and `_extract_constant()` raises (non-constant expr), the code does `return` — silently dropping the `.l` expression. Affects 8 models: circle, circpack, glider, hs62, lnts, mlbeta, mlgamma, robot.

**Fix requires 3 files:** `src/ir/symbols.py` (add `l_expr`/`l_expr_map` fields), `src/ir/parser.py` (store expr instead of drop), `src/emit/emit_gams.py` (emit new fields). Effort: ~3.5–4h (was ~2h assuming emit-only).

**Assumption was WRONG:** The assumption that `.l` was fully parsed and only the emit layer needed extending was incorrect. The gap is in the parser.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `L_INIT_EMISSION_DESIGN.md` Finding 1.2.

**Circle (#753) — high confidence `.l` fix resolves infeasibility.** circle.gms lines 46–48 set `a.l`, `b.l`, `r.l` to the centroid of the data point cloud — a warm start close to the optimal enclosing circle. Without these, PATH starts from all-zero (r=0 at lower bound boundary) and fails. The Sprint 19 PR #750 determinism fix ensures stable random data. With `.l` emission, PATH will receive a well-chosen starting point.

**Bearing (#757) — `.l` is NOT the blocker.** Bearing's constant `.l` assignments (R.l=6.0, mu.l=6e-6, etc.) are ALREADY captured and emitted by the current pipeline. Bearing translates successfully. The blocker is 6 `.scale` assignments (`mu.scale`, `h.scale`, `W.scale`, `PL.scale`, `Ep.scale`, `Ef.scale`) that tell GAMS/PATH how to normalize variables for numerical stability. `.scale` is not in `VariableDef` and is not emitted. Bearing needs a separate `.scale` emission fix.

**Assumption was PARTIALLY WRONG:** `.l` emission resolves circle but NOT bearing. Priority 1 delivers +1 model certain (circle) + 1–2 possible (circpack/glider/robot), not +2–4.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `L_INIT_EMISSION_DESIGN.md` Finding 1.3.

**Yes — a complete initialization section already exists.** `src/emit/emit_gams.py` lines ~170–240 contain a variable initialization loop added in Sprint 18 Day 3. It reads `var_def.l_map` (indexed) and `var_def.l` (scalar), and emits GAMS assignments **after declarations and before the Model/Solve statement** — exactly the right location. No new "prolog" concept needs to be created.

The section already works for bearing.gms (constant `.l` values) and all 28 models with constant `.l`. The gap is purely that it doesn't read `l_expr`/`l_expr_map` fields (which don't exist yet).

**Assumption was CORRECT:** The emitter has the right structure. The fix is additive (read new fields) rather than structural (no architectural changes needed).

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `L_INIT_EMISSION_DESIGN.md` Finding 1.4.

**8 models have expression-based `.l = expr` (currently missed):** circle, circpack, glider, hs62, lnts, mlbeta, mlgamma, robot

**28 models** have constant `.l` assignments and are already benefiting from the existing initialization code.

**Total models with any `.l =` assignment:** 55 of ~219 catalog models.

Of the 8 expression-based models:
- mlbeta, mlgamma: also blocked at parse stage (lexer_invalid_char) — `.l` fix won't unblock until parse is fixed
- circle: expected to solve after fix (PATH warm-start)
- circpack, glider, hs62, robot: possible solve improvement (currently untested / unknown PATH status)

**Assumption was CORRECT:** The fix is not circle/bearing-specific. Multiple models benefit. Bearing is excluded (its `.l` is already emitted; `.scale` is its blocker).

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
✅ Status: VERIFIED — 2026-02-19

**Findings:**
- mexss has exactly 4 accounting variables: `phipsi`, `philam`, `phipi`, `phieps`
- All are **scalar free variables** (no `Positive Variable` declaration, no bounds)
- Each appears as the LHS of exactly one `=E=` equation (apsi, alam, api, aeps respectively)
- None appear on the RHS of their own defining equation
- All four appear **only** in the objective-defining equation (`obj`: `phi = phipsi + philam + phipi - phieps`)
- All four pass all three originally-proposed criteria (C1, C2, C3)
- The same structural pattern (original, non-tightened C1–C3) fires on **demo1** (4 vars), **himmel11** (3 vars), and **house** (3 vars) — all currently solving; under the originally proposed criteria these are false positives (later tightened C3 correctly treats **himmel11** and **house** as safe)
- See `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` §1–§4 for full characterization

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
✅ Status: VERIFIED — 2026-02-19

**Findings:**
- **C1–C4 (structural criteria) are statically computable** from `ir.equations` and `ir.objective` alone; no runtime dependency graph is required for detection
- Criteria use: `edef.relation`, `edef.domain`, `lhs_rhs[0]` type, AST walk (`contains_var`)
- Computational cost: O(E · AST_size) — negligible for all known models
- **C5 (correctness / false-positive prevention) is NOT statically computable** — it requires checking whether forced multiplier values create contradictions with complementarity conditions
- **Recommendation: defer accounting variable detection to Sprint 21** until a safe C5 criterion can be formulated
- See `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` §3 for full feasibility table

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
✅ Status: VERIFIED — 2026-02-19

**Findings:**
- **214 of 219 corpus models contain `=E=` equations**; 176 contain `=E=.*sum(` patterns
- mexss is the **only currently-failing model** confirmed to be unblocked by correct accounting variable detection (model_status=5, Locally Infeasible)
- At least 3 currently-solving models (demo1, himmel11, house) share the same structural pattern and would be affected by any naive implementation
- Full corpus-wide scan for accounting variable candidates timed out (>2 min); exact count not computed
- Impact: fixing mexss alone adds +1 to the pipeline match count (25→26 solve, 9→10 match) — **modest ROI**
- See `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` §7 for corpus analysis

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
✅ Status: VERIFIED — 2026-02-19

**Findings:**
- **MODERATE FALSE POSITIVE RISK confirmed.** With tightened C3 (v must appear in E_obj), the candidate set narrows:
  - **himmel11** (`g2`, `g3`, `g4`): ✅ Safe — vars appear in no other equation (fail tightened C3)
  - **house** (`a1`, `a2`, `l`): ✅ Safe — vars appear in chained EQ equations, not E_obj (fail tightened C3)
  - **demo1** (`revenue`, `mcost`, `labcost`, `labearn`): ❌ **FALSE POSITIVE** — vars appear in `income` (E_obj), identical pattern to mexss
- The test suite (pipeline solve test for demo1) would catch the demo1 regression automatically
- Root cause: the static heuristic cannot distinguish mexss (infeasible due to multiplier contradiction) from demo1 (consistent despite same structural pattern)
- **Criterion C5** (multiplier consistency check) is required before accounting variable detection can safely ship
- See `docs/planning/EPIC_4/SPRINT_20/ACCOUNTING_VAR_DETECTION_DESIGN.md` §4–§5 for detailed false positive analysis and recommendation

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
✅ Status: VERIFIED

**Findings (2026-02-19):** All 27 models re-run and reclassified. See `LEXER_ERROR_CATALOG_UPDATE.md`.

**Subcategory distribution (Sprint 20 baseline):**

| Subcategory | Name | Count | Models |
|-------------|------|-------|--------|
| A | Compound Set Data | 6 | indus, mexls, paperco, sarf, turkey, turkpow |
| B | Cascading | 3 | fdesign, nemhaus, nonsharp |
| D | Lead/Lag (→IndexOffset) | 2 | mine, pindyck |
| E | Inline Scalar Data | 3 | cesam2, gussrisk, trnspwl |
| H | Control Flow | 2 | iobalance, lop |
| J | Bracket/Brace | 3 | mathopt3, saras, springchain |
| K | Miscellaneous | 1 | dinam |
| **L** | **Set-Model Exclusion (NEW)** | **5** | **camcge, cesam, ferts, spatequ, tfordy** |
| **M** | **Unsupported Declarations (NEW)** | **2** | **senstran, worst** |

**Two new subcategories identified:** L (Set-Model Exclusion: `/ all - setname /`) and M (Unsupported Declarations: `File`, `Acronym` keywords).

**Top-3 ROI:** L (5 models, 1–2h), A (6 models, 3–4h), B (3 models, 0h cascading).

**Assumption was wrong:** The dominant remaining categories are NOT G/H/J/K — they are A (6 models) and the new L (5 models). G is fully resolved (0 models remain). The old C (Put Statement) and I (Model/Solve) categories are fully resolved.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** All 27 models re-run against current main. Count confirmed at exactly **27** — no silent fixes from Sprint 19 apply to the remaining models. The 45 models fixed in Sprint 19 were correctly accounted for; the remaining 27 all have distinct failure tokens not addressed by Sprint 19 grammar additions.

**Zero regression:** No new models entered `lexer_invalid_char` after Sprint 19.

**Assumption was correct:** The 27 remaining models were genuinely unaffected by Sprint 19 work and require new grammar additions to fix.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** Subcategory G is **fully resolved** — 0 models remain. Sprint 19 fixed all 3 Subcategory G models (ganges, gangesx, weapons). The question of whether G fixes are straightforward is moot for Sprint 20.

**Implication:** The "set element description" grammar rule added in Sprint 19 was sufficient for all known G patterns. No G-category work is needed in Sprint 20.

**Assumption was partially wrong:** The assumption that G models would still be present was incorrect — G is completely resolved. The remaining catalog is dominated by A (6 models) and the new subcategory L (5 models).

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
✅ Status: VERIFIED

**Findings (2026-02-19):** The 2 remaining Subcategory D models are `mine` and `pindyck`. Both are **cascading** failures from lead/lag expressions — they will resolve automatically when the Sprint 20 IndexOffset `to_gams_string()` fix is applied (same fix that closes sparta/tabora/otpop).

- `mine`: Equation `pr(k,l+1,i,j)..` uses `l+1` lead; grammar fails on this, then cascades to `x.up(l,i,j)`. The grammar already supports `offset_paren`/`offset_func` from Sprint 19 PR #785 — the remaining gap is at the `to_gams_string()` level.
- `pindyck`: Loop `loop(t$to(t), r.l(t) = r.l(t-1)-d.l(t))` uses `t-1` lag; cascades to `display` statement. Same root.

**Assumption was correct:** No separate grammar additions are needed for Subcategory D beyond the IndexOffset workstream work already planned for Sprint 20.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `PIPELINE_MATCH_ANALYSIS.md` Section 1–2 for full per-model analysis.

**16 models: 15 mismatch + 1 comparison error (port).** Classified into 4 types:

| Type | Count | Models |
|------|-------|--------|
| Tolerance too tight | 5 | chem, dispatch, hhmax, mhw4d, mhw4dx |
| Missing .l init (expr-based, dropped by IR) | 2 | abel, chakra |
| Multiple optima / different local KKT point | 5 | alkyl, himmel16, mathopt1, process, trig |
| LP multi-model / wrong model selected | 3 | aircraft, apl1p, apl1pca |
| Obj not tracked (MCP obj=null) | 1 | port |

**Initialization (`.l` emission) is NOT the dominant cause.** Only 2 of 16 are missing expression-based `.l` inits. 5 models have `.l` correctly emitted but PATH still finds a different stationary point (non-convex).

**Predicted match improvement from `.l` fix:** +1 to +2 (9 → 10–11). Abel high confidence (param-based expr); chakra medium (formula with `ord()`).

**Assumption was WRONG:** The majority cause is not missing initialization. Tolerance (5) and multiple optima (5) are equally significant. The `.l` fix alone does not dominate match rate improvement.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `PIPELINE_MATCH_ANALYSIS.md` Sections 3–4.

**Tolerances used:** `DEFAULT_ATOL=1e-8`, `DEFAULT_RTOL=1e-6` (set in `scripts/gamslib/test_solve.py:78-79`).

**Formula:** `|nlp_obj - mcp_obj| <= atol + rtol * max(|nlp_obj|, |mcp_obj|)`

**5 models fail only due to tight tolerance** — their absolute differences are tiny (1e-4 to 5e-4) but exceed the combined tolerance. All 5 would pass with `rtol=1e-4`:

| Model | Abs Diff | Required rtol |
|-------|----------|---------------|
| mhw4d / mhw4dx | 1.0e-4 | 3.6e-6 |
| hhmax | 2.0e-4 | 1.4e-5 |
| chem | 5.0e-4 | 1.1e-5 |
| dispatch | 4.0e-4 | 5.0e-5 |

**These are PATH vs. IPOPT solver precision differences**, not structural mismatches.

**Within 5%:** apl1p (3.3% gap) would pass at `rtol=0.05` — too loose. alkyl (6.8%) would not.

**Assumption was PARTIALLY WRONG:** The tolerance IS too tight for 5 models — they are genuine solver-precision near-matches. Raising `rtol` to `1e-4` would add 5 matches (9 → 14) with no code changes, but this change is a separate decision from the `.l` emission fix.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `PIPELINE_MATCH_ANALYSIS.md` Section 7.

**Zero models among the 16 non-matching use `.scale`.** Checked all 15 mismatch models + port for `varname.scale` assignments in raw `.gms` source — none found.

**`.scale` is NOT a primary or secondary blocker** for any of the 16 divergences. The only model in the full catalog where `.scale` is a known blocker is `bearing` (Sprint 19 deferred issue #757) — which is NOT in the non-matching set because bearing doesn't even reach the solve stage.

**Assumption was CORRECT:** `.scale` emission is a Sprint 21+ item and does not affect the 16-model pipeline match gap.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** See `PIPELINE_MATCH_ANALYSIS.md` Section 5.

**None of the 9 matching models use patterns targeted by Sprint 20 workstreams:**
- IndexOffset (lead/lag): None
- `.scale` assignments: None
- Dollar conditions (`$(...)`) in equations: None
- Accounting variable patterns: All use standard equality constraints

**Test coverage gap confirmed:** None of the 9 matching models have end-to-end golden-file or solve-level test coverage. Only `rbrock` appears in integration tests (parse-only: `test_rbrock_gms_parses`). The 9 models are NOT protected by the test suite against regression.

**Regression risk is LOW but non-zero.** Sprint 20 grammar/parser changes could affect these models even if they don't use targeted syntax. Recommendation: add golden-file tests for the 9 models as a Sprint 20 task.

**Assumption was PARTIALLY WRONG:** The assumption that all 9 are in the golden-file test suite was incorrect — none are. The assumption that Sprint 20 changes won't affect them is likely correct given the non-overlap with targeted patterns.

---

# Category 6: IndexOffset Implementation

## Unknown 6.1: What is the current pipeline failure stage for each of the 8 IndexOffset-blocked models?

### Priority
**Critical** — Determines remaining work and revised effort estimate for the IndexOffset workstream

### Assumption
After Sprint 19's AD integration (PRs #779, #785), the 8 blocked models have moved from `lexer_invalid_char` or `internal_error` to a later failure stage (translate or solve). The remaining work is ≤4h of emit/parser fixes and end-to-end testing.

### Research Questions
1. What is the current pipeline status of each of the 8 models: launch, mine, sparta, tabora, ampl, otpop, robert, pak?
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
✅ Status: VERIFIED

**Findings (2026-02-19):** Ran all 8 models via `python -m src.cli`. Results:

| Model  | Prev Stage | Current Stage | Error |
|--------|-----------|--------------|-------|
| launch | parse=success, solve=failure | ✅ translate success | None — Sprint 19 AD work unblocked |
| mine   | parse=failure | ✅ translate success | None — grammar fix unblocked parse + translate |
| ampl   | parse=success, translate=not_tested | ✅ translate success | None |
| robert | parse=success, solve=failure | ✅ translate success | None |
| pak    | parse=success, solve=failure | ✅ translate success | None |
| sparta | parse=failure | ❌ emit failure | `NotImplementedError: Unary minus with complex operand not supported: Call(ord, (SymbolRef(l)))` |
| tabora | parse=failure | ❌ emit failure | `NotImplementedError: Unary minus with complex operand not supported: Call(ord, (SymbolRef(a)))` |
| otpop  | parse=failure | ❌ stationarity failure | `NotImplementedError: Complex offset expressions not yet supported: Binary(-, Call(card, ...), Call(ord, ...))` |

**Key finding:** 5 of 8 models now translate successfully — better than the ~4h estimate assumed. The 3 remaining failures are all in `IndexOffset.to_gams_string()` in `src/ir/ast.py`: it handles `Const`, `SymbolRef`, and `Unary("-", SymbolRef/Const)` offsets, but not `Unary("-", Call(...))` (sparta/tabora) or `Binary(op, Call, Call)` (otpop).

See `INDEXOFFSET_AUDIT.md` for full per-model analysis and revised effort estimate (~3h).

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
✅ Status: VERIFIED

**Findings (2026-02-19):** The xfail test is `test_diff_sum_over_t_with_lead` in `tests/unit/ad/test_index_offset_ad.py`. It tests: `d/dx(t1+1) [sum(t, x(t+1))]` should collapse to `1`. Currently `_sum_should_collapse()` and `_is_concrete_instance_of()` expect `str` wrt-indices, not `IndexOffset`, so the sum doesn't collapse (xfail strict=True, currently passing as expected-failure).

**Does it affect any of the 8 blocked models?** No. For the 3 still-failing models:
- sparta/tabora: fail at emit stage, before AD sum-collapse is relevant
- otpop: fails at stationarity index replacement (`indices_as_strings()`), before sum-collapse

**Recommendation:** Cleanup item, not critical path. Fix in Sprint 20 alongside `to_gams_string()` fixes, but not a blocker for any model.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** `_format_mixed_indices()` (src/emit/expr_to_gams.py) fully supports circular lead/lag. It delegates to `idx.to_gams_string()` for every `IndexOffset` it encounters. `IndexOffset.to_gams_string()` handles all circular cases:

- `Const(1)`, `circular=True` → `"i++1"` ✅
- `Const(-2)`, `circular=True` → `"i--2"` ✅  
- `SymbolRef("j")`, `circular=True` → `"i++j"` ✅
- `Unary("-", SymbolRef("j"))`, `circular=True` → `"i--j"` ✅

All 4 patterns are covered by passing unit tests in `tests/unit/emit/test_expr_to_gams.py::TestIndexOffset`.

**Circular lead/lag is NOT a blocker for any of the 8 models.** The 3 failing models (sparta, tabora, otpop) use complex arithmetic offsets (`ord()`, `card()` function calls), not `++`/`--` circular syntax.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** True translate internal_error count is **2** (not 5 — status JSON was stale). See `TRANSLATE_ERROR_AUDIT.md`.

**3 models now SUCCESS:** orani, prolog, ramsey — fixed by Sprint 19 work but status JSON not refreshed.

**2 genuine internal errors remain:**
- `maxmin.gms`: `ValueError: smin() expects 2 arguments, got 3` — AD rule `_diff_smin` only handles 2-arg scalar form; maxmin uses 3-arg aggregation form `smin(n, nn, sqrt(...))`. **Deferred** (~4–6h architectural).
- `mlbeta.gms`: `ValueError: Differentiation of 'loggamma' requires digamma/psi` — `loggamma` derivative unavailable in GAMS. **Permanently infeasible**.

**Additional non-internal_error failures:**
- 4 models `codegen_numerical_error`: Inf/NaN parameter values (decomp, gastrans, gtm, ibm1). Deferred.
- 1 model `timeout`: iswnm. Deferred.

**Assumption was WRONG:** "~5 models, 6–8h" estimate from PROJECT_PLAN.md is incorrect. Only 2 true internal errors; both deferred. The translate error budget should be reallocated to `model_no_objective_def` fix (13 models, ~2–3h — see Unknown 8.1).

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
✅ Status: VERIFIED

**Findings (2026-02-19):** The 2 remaining translate internal errors do NOT share a common root cause — they are distinct:
- maxmin: smin aggregation form (AD structural gap)
- mlbeta: loggamma/digamma unavailability (GAMS limitation, permanently infeasible)

**No systematic fix opportunity** for these 2 models. Each requires independent architectural work; mlbeta cannot be fixed at all.

**However**, the `model_no_objective_def` category (14 models, Unknown 8.1) shows a strong systematic pattern: 13 models share the same `$if set workSpace` preprocessor bug. A single fix to `process_conditionals` would unblock 13 models simultaneously — the highest-ROI systematic fix available.

**Assumption was WRONG:** The assumption that shared root causes exist among translate internal errors is false. But a better systematic opportunity exists in the parse-stage `model_no_objective_def` category.

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
✅ Status: VERIFIED

**Findings (2026-02-19):** `model_no_objective_def` is a **parse-stage** failure category (not translate-stage as assumed). Count: **14 models**. See `TRANSLATE_ERROR_AUDIT.md` Part 3.

**Root cause (13 of 14 models): `process_conditionals` preprocessor bug.**
All 13 have an unclosed `$if` directive that causes `process_conditionals` to incorrectly exclude the `solve` statement. The most common pattern (10 models) is:
```gams
$if set workSpace <model>.workSpace = %workSpace%

solve <model> using nlp minimizing/maximizing <var>;
```
Other variants: `$if not set np $set np 25` (elec — unclosed, excludes everything through EOF), `$ifI` (feasopt1), `$if set noscenred $goTo` (clearlak), `$if %uselicd%` (partssupply), `$if not set DIM` + `$ifE` (srpchase). In all cases, `process_conditionals` misidentifies the inline single-line `$if` guard as an unclosed multi-line block, causing the following `solve` statement to be excluded.

**Models (13 with `$if` bug):** camshape, catmix, chain, clearlak, danwolfe, elec, feasopt1, lnts, partssupply, polygon, rocket, robot, srpchase

**14th model (lmp2):** Solve is inside a doubly-nested loop — Issue #749 only extracts from one level of nesting.

**Fix location:** `src/ir/preprocessor.py` `process_conditionals()` — detect inline single-line `$if` guards (statement on same line as `$if`); don't carry exclusion to next line.

**Effort estimate:** ~2–3h (preprocessor fix + tests). High ROI: +13 models parsing → potential +5–8 new parse successes (COPS models may have other blockers after parsing).

**PROJECT_PLAN.md "5 models" estimate:** Was wrong — actual count is 14. And most fixes require a preprocessor change, not objective extraction enhancement. Objective extraction (e.g., `lmp2` doubly-nested loop) is secondary.

**Assumption was WRONG:** `model_no_objective_def` is not primarily an objective-extraction problem — it's a preprocessor `$if` handling bug eating the `solve` statement.

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
