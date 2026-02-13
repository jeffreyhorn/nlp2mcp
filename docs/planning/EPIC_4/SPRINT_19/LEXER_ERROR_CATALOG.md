# Lexer Invalid Character Error Catalog

**Created:** February 12, 2026
**Sprint:** 19 Prep Task 3
**Purpose:** Complete subcategorization of all `lexer_invalid_char` failures to prioritize grammar work for Sprint 19

---

## Executive Summary

**Total lexer_invalid_char models:** 72 (not ~95 as assumed in PROJECT_PLAN.md, not 74 as in GOALS.md)

**v1.2.0 re-parse results:** All 72 still fail — zero silent fixes (unlike internal_error where 21/24 were silently resolved by Sprint 18 changes)

**Subcategories identified:** 11 (A through K)

**Grammar-fixable assessment:**
- **~43–45 models** directly fixable with grammar/parser changes
- **~15–22 models** cascading failures (will resolve when root cause in another model's subcategory is fixed)
- **Remaining models (~7)** miscellaneous/complex (require deeper investigation; exact count depends on final classification)

**Sprint 19 target validation:** The PROJECT_PLAN.md target of "~95 → below 50" needs recalibration. Actual baseline is 72 (not ~95). With an estimated 43–45 directly fixable + 15–22 cascading (~58–67 addressable), the revised target should be "72 → below 30" or equivalently "fix ~60+ models."

---

## Baseline Correction

| Source | Reported Count | Actual Count | Notes |
|--------|---------------|--------------|-------|
| PROJECT_PLAN.md | ~95 | 72 | Significantly overstated; based on older v1.0.0 data |
| GOALS.md | 74 | 72 | Close but still 2 off; may include 2 models reclassified in Sprint 17 |
| gamslib_status.json (v1.1.0) | 72 | 72 | Accurate — this is the source of truth |

**Pipeline status distribution (219 total models in gamslib_status.json):**

| Status | Count |
|--------|-------|
| success | 62 |
| lexer_invalid_char | 72 |
| unknown | 59 |
| internal_error | 24 |
| semantic_undefined_symbol | 2 |

---

## Subcategory Overview

| ID | Subcategory | Count | Grammar-Fixable? | Priority | Estimated Effort |
|----|-------------|-------|------------------|----------|-----------------|
| A | Tuple/Compound Set Data Syntax | 12 | Yes (grammar) | P1 — High ROI | 6-8h |
| B | Cascading Parse Failures | 15 | Indirect (fix root cause) | P2 — Depends on others | 0h (resolved by other fixes) |
| C | Put Statement Format | 6 | Yes (grammar) | P1 — Known design | 2-3h |
| D | Lead/Lag Indexing | 4 | Yes (grammar + IR) | P2 — Needs IndexOffset | 3-4h |
| E | Special Values and Inline Data | 7 | Yes (grammar) | P1 — Quick wins | 2-3h |
| F | Declaration/Syntax Gaps | 7 | Yes (grammar) | P1 — Moderate | 4-5h |
| G | Set Element Descriptions | 4 | Yes (grammar) | P1 — Quick win | 1-2h |
| H | Control Flow | 2 | Yes (grammar) | P2 — Moderate | 2-3h |
| I | Model/Solve Statement Issues | 5 | Yes (grammar) | P1 — Moderate | 3-4h |
| J | Bracket/Brace Syntax | 3 | Partial (2 preprocessor, 1 grammar) | P2 — Mixed | 2-3h |
| K | Miscellaneous | 7 | Varies | P3 — Investigation needed | 4-6h |
| | **Total** | **72** | | | **~30-41h** |

---

## Subcategory A: Tuple/Compound Set Data Syntax (12 models)

### Description
Models use multi-dimensional set element tuples with dot-separated compound keys (e.g., `set s / a.b.c, d.e.f /`) or tuple data in parameter/table blocks. The grammar does not currently support these compound set element forms in data statements.

### Failing Pattern
```gams
Set map(i,j,k) / coal.east.rail, coal.west.truck /;
Parameter cost(i,j) / coal.east 10, oil.west 20 /;
```

The parser encounters the `.` character between set elements and fails with `lexer_invalid_char`.

### Models (12)

| Model | Failing Character | Failing Line Context | Notes |
|-------|------------------|---------------------|-------|
| china | `.` | Compound set data `guangdong.steel` | Multi-dimensional mapping |
| dinam | `.` | Compound set data in parameter | Dynamic model |
| egypt | `.` | Compound set data `set.element` | Resource model |
| indus | `.` | Compound set data in parameter | Industrial model |
| kand | `.` | Compound set data in set definition | Transport model |
| marco | `.` | Compound set data `sector.region` | CGE model |
| paklive | `.` | Compound set data in parameter | Livestock model |
| sarf | `.` | Compound set data in table | South Africa model |
| shale | `.` | Compound set data in set | Energy model |
| srkandw | `.` | Compound set data in set | Extended transport |
| tfordy | `.` | Compound set data in parameter | Dynamic transport |
| turkey | `.` | Compound set data in set/parameter | Turkey economy model |

### Fix Approach
Extend grammar to support dotted compound set elements in data statements. Add `compound_set_element` rule: `ID ("." ID)+`. This must work in set data blocks, parameter data blocks, and table row headers.

### Estimated Effort
6-8 hours (grammar extension + parser handler + testing)

### Sprint 19 ROI
**High** — 12 models directly, plus potentially resolving 1 cascading model (paperco in subcategory B).

---

## Subcategory B: Cascading Parse Failures (15 models)

### Description
These models fail at a character that is not the root cause. The actual failure occurs because an earlier construct in the file is not parseable, causing the parser to enter an error state and fail on a subsequent valid token. Fixing the root cause construct (which belongs to another subcategory) will resolve the cascading failure.

### Root Cause Analysis

| Model | Failing Char | Root Cause | Root Subcategory | Root Pattern |
|-------|-------------|------------|------------------|--------------|
| agreste | `)` | `prod()` function not in all contexts | E/F | `prod(j, expr)` in equation |
| ampl | `+` | Lead/lag indexing `x(t+1)` | D | Lead/lag syntax |
| camcge | `)` | `prod()` function in equation | E/F | `prod(j, expr)` in equation |
| cesam | `$` | Complex cascading from earlier syntax | K | Multiple issues |
| fawley | `(` | `not` operator in conditional | F | `not (condition)` |
| fdesign | `[` | Bracket conditional `$[cond]` in complex context | J | `$[expr]` after error state |
| feedtray | `)` | Variable naming conflict with function | F | Identifier `feed(i)` vs function |
| gtm | `)` | `log()` function in non-standard context | F | `log(expr)` parsing issue |
| iswnm | `;` | Equation without semicolon | F | Missing `;` after equation |
| korcge | `)` | `prod()` function in equation | E/F | `prod(j, expr)` in equation |
| nebrazil | `(` | `not` operator in conditional | F | `not (condition)` |
| nonsharp | `=` | Subset parameter syntax `acol(col)` | F | Subset as equation index |
| otpop | `+` | Lead/lag indexing `x(t+1)` | D | Lead/lag syntax |
| paperco | `.` | Compound set data | A | Dotted element syntax |
| worst | `$` | Dollar suffix in complex context | K | `$` conditional after error |

### Fix Strategy
No direct grammar work needed for these 15 models. They will be resolved when the root cause subcategories (A, D, E, F, J, K) are fixed. After implementing fixes for those subcategories, re-run these 15 models to confirm resolution.

### Cascading Root Cause Distribution

| Root Cause | Count | Resolving Subcategory |
|-----------|-------|----------------------|
| `prod()` function in equations | 3 | E/F (Declaration/Syntax Gaps) |
| Lead/lag indexing | 2 | D (Lead/Lag Indexing) |
| `not` operator | 2 | F (Declaration/Syntax Gaps) |
| Bracket conditional | 1 | J (Bracket/Brace Syntax) |
| Variable naming conflict | 1 | F (Declaration/Syntax Gaps) |
| `log()` function context | 1 | F (Declaration/Syntax Gaps) |
| Equation semicolon | 1 | F (Declaration/Syntax Gaps) |
| Compound set data | 1 | A (Tuple/Compound Set Data) |
| Dollar suffix/complex | 2 | K (Miscellaneous) |
| Subset parameter syntax | 1 | F (Declaration/Syntax Gaps) |

### Estimated Effort
0 hours direct — resolved by other subcategory fixes.

---

## Subcategory C: Put Statement Format (6 models)

### Description
Models use GAMS `put` statement format specifiers with the `:width:decimals` syntax (e.g., `put x:8:2`). The grammar does not support the colon-based format specifier.

### Failing Pattern
```gams
put x:8:2;
put "text":20;
put @10 y:12:4;
```

The parser fails at the `:` character following a put expression.

### Models (6)

| Model | Failing Character | Failing Line Context | Notes |
|-------|------------------|---------------------|-------|
| apl1pca | `:` | `put ... :width:decimals` | Portfolio model with put output |
| prodsp2 | `:` | `put ... :width:decimals` | Production scheduling |
| ps10_s | `:` | `put ... :width:decimals` | Put statement test model |
| ps10_s_mn | `:` | `put ... :width:decimals` | Put statement test variant |
| ps5_s_mn | `:` | `put ... :width:decimals` | Put statement test variant |
| stdcge | `:` | `put ... :width:decimals` | CGE with report writing |

### Fix Approach
Implement the `put_format` grammar rule designed in Sprint 18: `put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?`. This was already researched and verified in Sprint 18 Unknown 3.3.

### Estimated Effort
2-3 hours (grammar already designed; implementation + testing)

### Sprint 19 ROI
**High** — 6 models with known, pre-designed fix. Lowest risk of all subcategories.

---

## Subcategory D: Lead/Lag Indexing (4 models)

### Description
Models use GAMS lead/lag indexing syntax (`x(t+1)`, `x(t-1)`) for dynamic optimization. The grammar does not distinguish lead/lag offsets from arithmetic within index expressions.

### Failing Pattern
```gams
x(t+1) =e= x(t) + dx(t);
y(t-1) =l= y(t);
```

The parser fails at the `+` or `-` character within index parentheses when it expects a `)`.

### Models (4)

| Model | Failing Character | Failing Line Context | Notes |
|-------|------------------|---------------------|-------|
| launch | `+` | `x(t+1)` in equation | Launch vehicle optimization |
| mine | `+` | `x(t+1)` in equation | Mine scheduling |
| sparta | `-` | `x(t-1)` in equation | Spatial model |
| tabora | `+` | `x(t+1)` in equation | Tabora model |

### Fix Approach
This is tied to the IndexOffset IR design (Prep Task 6, Sprint 19 component). Grammar needs a `lead_lag_index` rule that recognizes `ID +/- NUMBER` within index positions. This interacts with AD (automatic differentiation) and KKT generation.

### Estimated Effort
3-4 hours (grammar + parser; IR and AD work is separate Sprint 19 component)

### Sprint 19 ROI
**Medium** — 4 models directly + 2 cascading models (ampl, otpop from subcategory B). Total: 6 models. But requires IndexOffset IR design to be complete for full pipeline benefit.

### Note
An additional 4 models with lead/lag syntax are in the `unknown` pipeline status (not `lexer_invalid_char`), bringing the total lead/lag-blocked models to ~8 as documented in GOALS.md.

---

## Subcategory E: Special Values and Inline Data (7 models)

### Description
Models use GAMS special values (`na`, `inf`, `eps`, `undf`), inline data constructs, or compile-time expressions in data statements that the grammar does not handle.

### Failing Pattern
```gams
Parameter p / a na, b inf /;
Set s / 1*card(i) /;
$eval n card(s)
Table t(i,j)
    + col3  col4    * table continuation
```

### Models (7)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| cesam2 | `$` | `$ifthen`/`$else`/`$endif` conditionals in data | Preprocessor conditionals |
| ferts | `+` | Table continuation with `+` | Table continuation syntax |
| gussrisk | `=` | Inline data assignment in complex context | Inline data |
| lands | `+` | Table continuation or inline expression | Land use model |
| ship | `:` | Data format or special syntax | Shipping model |
| tforss | `.` | Dotted element in special context | Transport model variant |
| trnspwl | `#` | `#` character in data or comment | Transport model |

### Fix Approach
Mixed approach needed:
- `cesam2`: Requires preprocessor conditional support (`$ifthen`/`$else`/`$endif`) — likely out of Sprint 19 scope
- `ferts`, `lands`: Table continuation with `+` — related to ISSUE_392
- `gussrisk`: Inline data syntax extension
- `ship`, `tforss`, `trnspwl`: Individual investigation needed

### Estimated Effort
2-3 hours for the grammar-fixable subset; some models may require preprocessor support

### Sprint 19 ROI
**Medium** — Mixed fixability. 4-5 models likely addressable with grammar changes.

---

## Subcategory F: Declaration/Syntax Gaps (7 models)

### Description
Models use valid GAMS syntax constructs that are missing from the grammar — operator keywords, declaration forms, or statement patterns not yet implemented.

### Models (7)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| imsl | `(` | Function call in unexpected context | Math library model |
| qdemo7 | `=` | Complex assignment syntax | QCP demo model |
| robustlp | `{` | Curly brace in non-expression context | Robust optimization |
| solveopt | `.` | Model attribute access `model.optfile` | Solve options model |
| tricp | `(` | Parameterized equation form | Tridiagonal model |
| uimp | `%` | Compile-time variable `%gams.scrdir%` | Import model |
| wall | `(` | Complex indexed expression | Wall model |

### Fix Approach
Each model has a distinct missing grammar construct:
- `robustlp`: Extend curly brace support to more contexts
- `solveopt`: Add model attribute access (`.optfile`, `.solprint`, etc.)
- `uimp`: Compile-time variable expansion (`%var%`) — may need preprocessor
- Others: Individual grammar rule additions

### Estimated Effort
4-5 hours (multiple distinct grammar additions)

### Sprint 19 ROI
**Medium** — 7 models, but each requires a different fix. Plus resolves several cascading models in subcategory B (prod, not, log, semicolon, naming, subset patterns = ~8 cascading models).

---

## Subcategory G: Set Element Descriptions (4 models)

### Description
Models use quoted descriptions after set elements that the grammar doesn't handle in all contexts, or use complex multi-word set element forms.

### Failing Pattern
```gams
Set i / elem1 "First element description"
        elem2 "Second element description" /;
```

### Models (4)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| ganges | `"` | Quoted set element description | River basin model |
| gangesx | `"` | Quoted set element description | Extended Ganges model |
| lop | `"` | Quoted description in complex set | Linear optimization |
| weapons | `"` | Quoted description after set element | Weapons allocation |

### Fix Approach
Extend the `set_member` rule to support quoted descriptions in all set definition contexts. Sprint 17 added partial support (Phase 2, Day 7) but not all contexts are covered.

### Estimated Effort
1-2 hours (extend existing partial support)

### Sprint 19 ROI
**High** — 4 models with minimal effort. Builds on Sprint 17 work.

---

## Subcategory H: Control Flow (2 models)

### Description
Models use GAMS control flow constructs (`for`, `while`, `repeat/until`) or complex loop patterns not fully supported in the grammar.

### Models (2)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| iobalance | `;` | Complex control flow with `for` loop | IO balance model |
| lmp2 | `(` | Loop with complex index expression | LMP model |

### Fix Approach
Add `for` loop statement rule and extend `loop` statement to handle complex index expressions.

### Estimated Effort
2-3 hours

### Sprint 19 ROI
**Low** — Only 2 models. Implement if time permits.

---

## Subcategory I: Model/Solve Statement Issues (5 models)

### Description
Models use `model`/`solve` statement patterns not currently supported — including model attribute access, solve statement variants, or model definition syntax extensions.

### Models (5)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| mlbeta | `=` | Model definition syntax | Beta distribution model |
| mlgamma | `=` | Model definition syntax | Gamma distribution model |
| pdi | `.` | Model attribute access | PDI model |
| qsambal | `=` | Complex solve/model syntax | Samuelson QCP variant |
| sambal | `=` | Complex solve/model syntax | Samuelson model |

### Fix Approach
Extend model definition and solve statement grammar rules. Add model attribute access support (`.modelStat`, `.objVal`, etc.) — this overlaps with the harker/mathopt4 fix from internal_error Task 2.

### Estimated Effort
3-4 hours

### Sprint 19 ROI
**Medium** — 5 models. Model attribute access fix benefits both lexer_invalid_char and internal_error categories.

---

## Subcategory J: Bracket/Brace Syntax (3 models)

### Description
Models use bracket or brace syntax in contexts the grammar doesn't support, or use `$` preprocessor directives as the actual failing character.

### Models (3)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| clearlak | `$` | `$goto`, `$label`, `$if`, `$libinclude` preprocessor directives | **Only model where `$` is the actual unexpected character** |
| mathopt3 | `[` | Square bracket in expression context | Math optimization |
| springchain | `$` | `$eval`, `$if`, `$set` compile-time directives | Spring chain model |

### Fix Approach
- `clearlak`: Requires preprocessor directive support (`$goto`, `$label`, `$libinclude`) — likely out of Sprint 19 scope
- `mathopt3`: Extend square bracket support to additional expression contexts
- `springchain`: Requires compile-time evaluation (`$eval`, `$set`) — may need preprocessor

### Preprocessor Note
`clearlak` and `springchain` are the only 2 models (out of 72) where preprocessor directives are the actual root cause of the lexer failure. All other models using `$ontext/$offtext/$title` are handled by existing preprocessor comment stripping.

### Estimated Effort
2-3 hours (for mathopt3; clearlak and springchain may be out of scope)

### Sprint 19 ROI
**Low** — 1 grammar-fixable model (mathopt3). Other 2 require preprocessor support.

---

## Subcategory K: Miscellaneous (7 models)

### Description
Models with unique or hard-to-classify failure patterns that don't fit neatly into other subcategories. Each requires individual investigation.

### Models (7)

| Model | Failing Character | Root Pattern | Notes |
|-------|------------------|-------------|-------|
| mexls | `(` | Complex expression syntax | Mexican model |
| nemhaus | `(` | Nemhauser model — complex indexing | Combinatorial model |
| pindyck | `(` | Complex function call context | Energy model |
| saras | `;` | Statement boundary issue | Refinery model |
| senstran | `(` | Complex expression syntax | Sensitivity analysis |
| spatequ | `.` | Dotted syntax in equations | Spatial equilibrium |
| turkpow | `(` | Complex expression pattern | Turkish power model |

### Fix Approach
Each model needs individual investigation. Common theme: complex expression syntax the parser can't handle — likely requires understanding the specific GAMS construct used.

### Estimated Effort
4-6 hours (individual investigation per model)

### Sprint 19 ROI
**Low** — 7 models but high investigation cost per model. Defer to later sprint if time-constrained.

---

## Preprocessor Directive Analysis

### Question Addressed
Unknown 4.2: "Are there preprocessor directives in lexer_invalid_char models that require preprocessor support rather than grammar fixes?"

### Findings

All 72 models were checked for preprocessor directives. Results:

**Standard directives (handled by existing preprocessor stripping):**
- `$offtext/$ontext/$title` — present in most models; already handled
- `$offdigit/$ondigit` — present in some models; not a parse blocker

**Advanced directives (require preprocessor implementation):**

| Directive | Models Using It | Is It the Failure Cause? |
|-----------|----------------|-------------------------|
| `$goto`, `$label` | clearlak, srkandw | Yes (clearlak only) |
| `$if` | clearlak, srkandw, cesam2, springchain | Yes (clearlak, cesam2, springchain) |
| `$libinclude` | clearlak, srkandw | Yes (clearlak only) |
| `$ifthen/$else/$endif` | cesam2 | Yes |
| `$eval`, `$set` | springchain | Yes |

**Key finding:** **4 models** out of 72 require some form of preprocessor support as their root cause: **3** with advanced directive processing (clearlak, cesam2, springchain, as listed above) and **1** (`uimp`) that only needs simple `%var%` expansion. The remaining **68 models** (94%) are addressable with grammar-only changes.

---

## Grammar-Fixable Assessment

### Summary

| Category | Directly Fixable | Cascading (Free) | Preprocessor Required | Needs Investigation |
|----------|-----------------|-------------------|----------------------|-------------------|
| A: Tuple/Compound Set Data | 12 | — | — | — |
| B: Cascading Failures | — | 15 | — | — |
| C: Put Statement Format | 6 | — | — | — |
| D: Lead/Lag Indexing | 4 | — | — | — |
| E: Special Values/Inline | 4-5 | — | 1 (cesam2) | 1-2 |
| F: Declaration/Syntax Gaps | 5-6 | — | 1 (uimp) | — |
| G: Set Element Descriptions | 4 | — | — | — |
| H: Control Flow | 2 | — | — | — |
| I: Model/Solve Issues | 5 | — | — | — |
| J: Bracket/Brace | 1 | — | 2 (clearlak, springchain) | — |
| K: Miscellaneous | — | — | — | 7 |
| **Total** | **43-45** | **15** (up to 22) | **4** | **8-9** |

### Optimistic vs Conservative Estimates

| Scenario | Models Fixed | Remaining | Notes |
|----------|-------------|-----------|-------|
| **Optimistic** (all grammar + cascading resolve) | 65 | 7 | All cascading models resolve; misc investigated |
| **Realistic** (grammar fixes + most cascading) | 55-58 | 14-17 | ~80% of cascading resolve; some misc deferred |
| **Conservative** (grammar only, no cascading) | 43-45 | 27-29 | Only directly fixable models; cascading TBD |

---

## Recommended Sprint 19 Implementation Order

### Phase 1: Quick Wins (P1, ~6-8h, ~22 models)

| Priority | Subcategory | Models | Effort | Cumulative |
|----------|-------------|--------|--------|------------|
| 1 | G: Set Element Descriptions | 4 | 1-2h | 4 |
| 2 | C: Put Statement Format | 6 | 2-3h | 10 |
| 3 | E: Special Values (grammar subset) | 4-5 | 2-3h | 14-15 |

### Phase 2: Core Grammar Work (P1, ~10-13h, ~19+ models)

| Priority | Subcategory | Models | Effort | Cumulative |
|----------|-------------|--------|--------|------------|
| 4 | A: Tuple/Compound Set Data | 12 | 6-8h | 26-27 |
| 5 | I: Model/Solve Issues | 5 | 3-4h | 31-32 |
| 6 | Re-test cascading (B) | ~10-12 | 0h (verify) | 41-44 |

### Phase 3: Advanced Grammar (P2, ~8-10h, ~8+ models)

| Priority | Subcategory | Models | Effort | Cumulative |
|----------|-------------|--------|--------|------------|
| 7 | F: Declaration/Syntax Gaps | 5-6 | 4-5h | 46-50 |
| 8 | D: Lead/Lag Indexing | 4+2 cascading | 3-4h | 50-56 |
| 9 | Re-test cascading (B) | ~3-5 | 0h (verify) | 53-61 |

### Phase 4: If Time Permits (P3, ~8-12h, ~9+ models)

| Priority | Subcategory | Models | Effort | Cumulative |
|----------|-------------|--------|--------|------------|
| 10 | H: Control Flow | 2 | 2-3h | 55-63 |
| 11 | J: Bracket/Brace (mathopt3) | 1 | 1h | 56-64 |
| 12 | K: Miscellaneous | 0-7 | 4-6h | 56-71 |

### Out of Sprint 19 Scope

| Item | Models | Reason |
|------|--------|--------|
| Preprocessor directives (clearlak, cesam2, springchain) | 3 | Requires preprocessor implementation — deferred |
| Compile-time variables (uimp) | 1 | Requires `%var%` expansion — deferred |
| Miscellaneous deep investigation | 0-7 | High effort per model; investigate as time permits |

---

## Cross-References

### Unknowns Verified by This Analysis

| Unknown | Finding | Status |
|---------|---------|--------|
| **4.1** (Current count) | 72 models (not ~95 or 74). Pipeline data is v1.1.0 baseline. All 72 still fail with v1.2.0. | ✅ VERIFIED |
| **4.2** (Preprocessor directives) | Only 3 of 72 models (4%) require preprocessor support. 69 models (96%) addressable with grammar-only changes. | ✅ VERIFIED |
| **4.3** (Overlap with deferred analysis) | This catalog fully subsumes the deferred "Lexer Error Deep Analysis" item scope. The 5-6h budget can be reallocated to implementation. | ✅ VERIFIED |
| **6.1** (Specific syntax constructs) | 11 subcategories identified with specific GAMS syntax patterns. Top patterns: compound set data (12), put format (6), declaration gaps (7), special values (7). | ✅ VERIFIED |
| **6.4** (Addressable with grammar-only) | 43-45 models directly fixable + up to 22 cascading = 65 addressable. "Below 50" target from PROJECT_PLAN.md needs recalibration to "below 30" (since baseline is 72, not ~95). | ✅ VERIFIED |

### Related Documents

- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknowns 4.1, 4.2, 4.3, 6.1, 6.4
- `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md` — Task 3 definition
- `docs/planning/EPIC_4/PROJECT_PLAN.md` — Sprint 19 scope and targets
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 lexer_invalid_char goals
- `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md` — Put format grammar design (subcategory C)
- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` — Sprint 17 lexer subcategories (predecessor analysis)

### Overlap with Other Sprint 19 Components

| Component | Overlap | Notes |
|-----------|---------|-------|
| Internal Error Investigation | Model attribute access fix (harker/mathopt4) also fixes subcategory I models (pdi, solveopt) | Shared grammar work |
| IndexOffset IR Design | Lead/lag grammar (subcategory D) is the parser side of IndexOffset | Coordinated implementation |
| Sprint 18 Deferred: Put Statement | Subcategory C is exactly the deferred put statement format item | Direct overlap — same work |
| Sprint 18 Deferred: Lexer Analysis | This catalog fully covers the deferred analysis scope | Reallocate 5-6h to implementation |
| FIX_ROADMAP ISSUE_392 | Table continuation affects subcategory E models (ferts, lands) | Partial overlap |

---

## Appendix: Complete Model List (72 models)

| # | Model | Subcategory | Failing Char | Grammar-Fixable? |
|---|-------|-------------|-------------|-----------------|
| 1 | agreste | B (Cascading) | `)` | Indirect (prod) |
| 2 | ampl | B (Cascading) | `+` | Indirect (lead/lag) |
| 3 | apl1pca | C (Put Format) | `:` | Yes |
| 4 | camcge | B (Cascading) | `)` | Indirect (prod) |
| 5 | cesam | B (Cascading) | `$` | Indirect (complex) |
| 6 | cesam2 | E (Special Values) | `$` | No (preprocessor) |
| 7 | china | A (Tuple/Compound) | `.` | Yes |
| 8 | clearlak | J (Bracket/Brace) | `$` | No (preprocessor) |
| 9 | dinam | A (Tuple/Compound) | `.` | Yes |
| 10 | egypt | A (Tuple/Compound) | `.` | Yes |
| 11 | fawley | B (Cascading) | `(` | Indirect (not) |
| 12 | fdesign | B (Cascading) | `[` | Indirect (bracket) |
| 13 | feedtray | B (Cascading) | `)` | Indirect (naming) |
| 14 | ferts | E (Special Values) | `+` | Yes |
| 15 | ganges | G (Set Descriptions) | `"` | Yes |
| 16 | gangesx | G (Set Descriptions) | `"` | Yes |
| 17 | gtm | B (Cascading) | `)` | Indirect (log) |
| 18 | gussrisk | E (Special Values) | `=` | Yes |
| 19 | imsl | F (Declaration Gaps) | `(` | Yes |
| 20 | indus | A (Tuple/Compound) | `.` | Yes |
| 21 | iobalance | H (Control Flow) | `;` | Yes |
| 22 | iswnm | B (Cascading) | `;` | Indirect (nosemi) |
| 23 | kand | A (Tuple/Compound) | `.` | Yes |
| 24 | korcge | B (Cascading) | `)` | Indirect (prod) |
| 25 | lands | E (Special Values) | `+` | Yes |
| 26 | launch | D (Lead/Lag) | `+` | Yes |
| 27 | lmp2 | H (Control Flow) | `(` | Yes |
| 28 | lop | G (Set Descriptions) | `"` | Yes |
| 29 | marco | A (Tuple/Compound) | `.` | Yes |
| 30 | mathopt3 | J (Bracket/Brace) | `[` | Yes |
| 31 | mexls | K (Miscellaneous) | `(` | Investigate |
| 32 | mine | D (Lead/Lag) | `+` | Yes |
| 33 | mlbeta | I (Model/Solve) | `=` | Yes |
| 34 | mlgamma | I (Model/Solve) | `=` | Yes |
| 35 | nebrazil | B (Cascading) | `(` | Indirect (not) |
| 36 | nemhaus | K (Miscellaneous) | `(` | Investigate |
| 37 | nonsharp | B (Cascading) | `=` | Indirect (subset) |
| 38 | otpop | B (Cascading) | `+` | Indirect (lead/lag) |
| 39 | paklive | A (Tuple/Compound) | `.` | Yes |
| 40 | paperco | B (Cascading) | `.` | Indirect (tuple) |
| 41 | pdi | I (Model/Solve) | `.` | Yes |
| 42 | pindyck | K (Miscellaneous) | `(` | Investigate |
| 43 | prodsp2 | C (Put Format) | `:` | Yes |
| 44 | ps10_s | C (Put Format) | `:` | Yes |
| 45 | ps10_s_mn | C (Put Format) | `:` | Yes |
| 46 | ps5_s_mn | C (Put Format) | `:` | Yes |
| 47 | qdemo7 | F (Declaration Gaps) | `=` | Yes |
| 48 | qsambal | I (Model/Solve) | `=` | Yes |
| 49 | robustlp | F (Declaration Gaps) | `{` | Yes |
| 50 | sambal | I (Model/Solve) | `=` | Yes |
| 51 | saras | K (Miscellaneous) | `;` | Investigate |
| 52 | sarf | A (Tuple/Compound) | `.` | Yes |
| 53 | senstran | K (Miscellaneous) | `(` | Investigate |
| 54 | shale | A (Tuple/Compound) | `.` | Yes |
| 55 | ship | E (Special Values) | `:` | Yes |
| 56 | solveopt | F (Declaration Gaps) | `.` | Yes |
| 57 | sparta | D (Lead/Lag) | `-` | Yes |
| 58 | spatequ | K (Miscellaneous) | `.` | Investigate |
| 59 | springchain | J (Bracket/Brace) | `$` | No (preprocessor) |
| 60 | srkandw | A (Tuple/Compound) | `.` | Yes |
| 61 | stdcge | C (Put Format) | `:` | Yes |
| 62 | tabora | D (Lead/Lag) | `+` | Yes |
| 63 | tfordy | A (Tuple/Compound) | `.` | Yes |
| 64 | tforss | E (Special Values) | `.` | Yes |
| 65 | tricp | F (Declaration Gaps) | `(` | Yes |
| 66 | trnspwl | E (Special Values) | `#` | Yes |
| 67 | turkey | A (Tuple/Compound) | `.` | Yes |
| 68 | turkpow | K (Miscellaneous) | `(` | Investigate |
| 69 | uimp | F (Declaration Gaps) | `%` | No (preprocessor) |
| 70 | wall | F (Declaration Gaps) | `(` | Yes |
| 71 | weapons | G (Set Descriptions) | `"` | Yes |
| 72 | worst | B (Cascading) | `$` | Indirect (dollar) |
