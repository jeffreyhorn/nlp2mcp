# Sprint 21 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 21 begins
**Timeline:** Complete before Sprint 21 Day 1
**Goal:** Research macro expansion architecture, triage error categories, catalog path_syntax_error root causes, and establish baseline metrics so Sprint 21 can execute against data-driven priorities without mid-sprint surprises

**Key Insight from Sprint 20:** Sprint 20 achieved all 8 committed targets by combining systematic error catalogs with targeted fixes. The lexer error subcategory catalog (Day 4) enabled prioritized grammar work that pushed parse rate from 112/160 to 132/160. Apply the same catalog-first approach to Sprint 21's path_syntax_error and internal_error populations.

---

## Executive Summary

Sprint 21 focuses on nine workstreams (from `docs/planning/EPIC_4/PROJECT_PLAN.md`):
1. **`%macro%` expansion in preprocessor** — implement `$set`/`$eval`/`%name%` support to unblock saras, springchain (#837, #840)
2. **internal_error triage** — 7 models (clearlak, imsl, indus, sarf, senstran, tfordy, turkpow) that parse but crash in the IR builder
3. **Solve quality / path_syntax_error** — 45 models that translate but produce MCP files PATH cannot process
4. **Deferred Sprint 20 issues** — 13 open issues spanning AD, stationarity, domain handling, and macro expansion
5. **Full pipeline match rate** — close the 33-solve / 16-match gap
6. **Semantic error resolution** — 7 `semantic_undefined_symbol` models
7. **Emerging translation blockers** — newly-parsed models hitting translation failures
8. **PATH convergence investigation** — systematic analysis of `path_solve_terminated` models
9. **Solution comparison enhancement** — extend beyond objective value matching

Sprint 20 final metrics (baseline): parse 132/160 (82.5%), translate 120/132 (90.9%), solve 33/120 (27.5%), match 16/33 (48.5%), tests 3,715, lexer_invalid_char 10, internal_error 7, semantic_undefined_symbol 7.

This prep plan produces the research, catalogs, baselines, and design artifacts needed to begin Sprint 21 Day 1 without context-building overhead.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 21 Known Unknowns List | Critical | 2–3h | None | All workstreams |
| 2 | Research GAMS Macro Expansion Semantics | Critical | 3–4h | Task 1 | Priority 1: `%macro%` expansion |
| 3 | Catalog internal_error Root Causes (7 Models) | High | 2–3h | Task 1 | Priority 2: internal_error triage |
| 4 | Catalog path_syntax_error Root Causes (45 Models) | High | 3–4h | Task 1 | Priority 3: Solve quality |
| 5 | Triage Deferred Sprint 20 Issues | High | 2–3h | Tasks 1, 3, 4 | Priority 4: Deferred issues |
| 6 | Analyze Solve-Match Gap (17 Models) | High | 2–3h | Task 1 | Priority 5: Match rate |
| 7 | Audit semantic_undefined_symbol Models | Medium | 1–2h | Task 1 | Semantic error resolution |
| 8 | Snapshot Baseline Metrics & Pipeline Retest | Medium | 1–2h | None | All workstreams |
| 9 | Review Sprint 20 Retrospective Action Items | Medium | 1h | None | Process improvement |
| 10 | Plan Sprint 21 Detailed Schedule | Critical | 3–4h | All tasks | Sprint planning |

**Total Estimated Time:** ~20–28 hours (~3–4 working days)

**Critical Path:** Task 1 → Tasks 2, 3, 4 (parallel) → Task 5 → Task 10

---

## Task 1: Create Sprint 21 Known Unknowns List

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** None

### Objective

Create `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md` with all significant unknowns across Sprint 21's nine workstreams. Categorize by domain, assign priority, and identify the verification method for each unknown.

### Why This Matters

The Known Unknowns process has been rated highly since Sprint 4 (consistently preventing mid-sprint architectural surprises). Sprint 20 had 26 unknowns across 8 categories. Sprint 21 introduces a new subsystem (macro expansion) and two large triage populations (45 path_syntax_error, 7 internal_error) — all prime sources of unknowns.

### Background

Sprint 20 retrospective (`docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md`) identified these as highest-risk unknowns going into Sprint 21:
- **Macro expansion scope:** How complex are `$eval` expressions in the GAMSlib corpus? Is simple string substitution sufficient, or do we need arithmetic evaluation?
- **path_syntax_error clustering:** Are the 45 failures caused by a few root causes or many distinct issues?
- **internal_error heterogeneity:** Are the 7 models failing for the same IR builder reason, or 7 distinct bugs?
- **Solve-match gap:** Is the 17-model gap (33 solve, 16 match) caused by initialization, scaling, tolerances, or fundamental formulation issues?
- **Semantic error source:** Are the 7 `semantic_undefined_symbol` models GAMSLIB source issues or nlp2mcp parser bugs?

Previous research documents:
- `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` — Sprint 20 unknowns (template reference)
- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` — subcategory catalog methodology
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md` lines 300–362 — Sprint 21 recommendations
- `docs/issues/ISSUE_837_springchain-bracket-expr-scalar-data.md` — macro expansion scope
- `docs/issues/ISSUE_840_saras-system-nlp-macro.md` — system macro details

### What Needs to Be Done

1. **Review Sprint 20 retrospective** recommendations section (lines 300–362)
2. **Review all 10 active issue files** in `docs/issues/` to extract unknowns
3. **Review Sprint 20 KNOWN_UNKNOWNS.md** for any unresolved unknowns carrying forward
4. **Draft KNOWN_UNKNOWNS.md** with:
   - 6+ categories: Macro Expansion, internal_error, path_syntax_error, Deferred Issues, Match Rate, Semantic Errors
   - For each unknown: assumption, verification method, priority, owner, estimated research time
   - Target: 20–30 unknowns total
5. **Identify which unknowns can be resolved during prep** vs. which are sprint work

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify document exists and has sufficient content
ls docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md
wc -l docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md
# Should be 200+ lines with 20+ unknowns

# Verify all categories present
grep -c "^##" docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md
# Should be 6+ category headings
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/KNOWN_UNKNOWNS.md` with 20–30 unknowns across 6+ categories
- Task-to-Unknown mapping appendix linking prep tasks 2–9 to verified unknowns

### Acceptance Criteria

- [ ] Document created with 20+ unknowns across 6+ categories
- [ ] All unknowns have assumption, verification method, and priority
- [ ] All Critical/High unknowns have verification plan
- [ ] Unknowns cover all 9 Sprint 21 workstreams
- [ ] Unresolved Sprint 20 unknowns carried forward where applicable
- [ ] Research time estimated for each unknown

---

## Task 2: Research GAMS Macro Expansion Semantics

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Research GAMS `$set`/`$eval` directive semantics and `%name%` macro expansion to produce a design document for the preprocessor macro subsystem (Sprint 21 Priority 1).

### Why This Matters

Sprint 21 Priority 1 (4–8h) depends entirely on understanding the GAMS macro expansion model. The preprocessor currently strips `$set`/`$eval` directives without executing them. Implementing macro expansion without understanding the full semantics risks mid-sprint redesign.

Two models are immediately blocked: saras (`%system.nlp%`) and springchain (`$set`/`$eval`/`%N%`/`%NM1%`). Additional models in the corpus may use macros in ways not yet identified.

### Background

- `docs/issues/ISSUE_837_springchain-bracket-expr-scalar-data.md` — springchain uses `$set N 10`, `$set NM1 9`, `$eval N2 %N%-2` with `%N%`/`%NM1%`/`%N2%` expansion in equation bodies
- `docs/issues/ISSUE_840_saras-system-nlp-macro.md` — saras uses `%system.nlp%` system environment variable
- `src/ir/preprocessor.py` — current `strip_unsupported_directives()` handles `$set`/`$eval` by removing them
- GAMS documentation: `$set`, `$setglobal`, `$eval`, `$ifi`, `%name%` expansion rules

### What Needs to Be Done

1. **Read GAMS documentation** on compile-time macro directives:
   - `$set name value` — local macro definition
   - `$setglobal name value` — global macro definition
   - `$eval name expression` — evaluate expression and assign result
   - `$ifi %name%==value` — conditional compilation
   - `%name%` — macro expansion (case-insensitive)
   - `%system.X%` — system environment macros
2. **Survey GAMSlib corpus** for macro usage patterns:
   - `grep -l '\$set\b\|\$eval\b\|\$setglobal\b' data/gamslib/raw/*.gms`
   - Count how many of the 160 models use macros
   - Classify patterns: simple string substitution, arithmetic `$eval`, conditional `$ifi`, system macros
3. **Analyze springchain** (`data/gamslib/raw/springchain.gms`) in detail:
   - Document all `$set`/`$eval`/`%name%` usage
   - Determine what evaluation capabilities are needed for `$eval`
   - Identify whether simple integer arithmetic suffices or if general expressions are required
4. **Analyze saras** (`data/gamslib/raw/saras.gms`) in detail:
   - Document `%system.nlp%` usage context
   - Determine what system macros need to be supported
5. **Design preprocessor macro subsystem:**
   - Macro store data structure
   - Expansion algorithm (single-pass vs. iterative)
   - `$eval` expression evaluator scope (integers only? floats? string operations?)
   - System macro registry (which `%system.X%` values to support)
   - Error handling for undefined macros
6. **Write design document** with architecture, API, and test plan

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify design document exists
ls docs/planning/EPIC_4/SPRINT_21/MACRO_EXPANSION_DESIGN.md

# Verify corpus survey results
grep -rl '\$set\b' data/gamslib/raw/*.gms 2>/dev/null | wc -l
# Document the count

# Verify springchain analysis
grep -n '%[A-Za-z]' data/gamslib/raw/springchain.gms 2>/dev/null | head -20
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/MACRO_EXPANSION_DESIGN.md` — design document with architecture, scope, and test plan
- Corpus survey results: count and classification of macro usage patterns across 160 models
- Updated `KNOWN_UNKNOWNS.md` Category 1 unknowns marked as resolved

### Acceptance Criteria

- [ ] GAMS macro directive semantics documented (`$set`, `$eval`, `$setglobal`, `%name%`)
- [ ] GAMSlib corpus surveyed: macro usage count and pattern classification
- [ ] springchain `$set`/`$eval` usage fully analyzed
- [ ] saras `%system.nlp%` usage fully analyzed
- [ ] Preprocessor macro subsystem designed (store, expansion, `$eval` scope)
- [ ] System macro registry defined
- [ ] Design document created with test plan
- [ ] Implementation approach confirmed for Sprint 21 Day 1

---

## Task 3: Catalog internal_error Root Causes (7 Models)

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Run the 7 internal_error models through `parse_file()`, capture the error tracebacks, and classify root causes into subcategories to enable prioritized fixes during Sprint 21 Priority 2.

### Why This Matters

Sprint 21 Priority 2 allocates 6–10h to fix 7 internal_error models. Without a root cause catalog, work would proceed model-by-model in arbitrary order. A catalog enables: (a) grouping models with the same root cause for batch fixes, (b) identifying which fixes have the highest leverage, and (c) estimating per-model effort more accurately.

This mirrors the Sprint 20 lexer error subcategory catalog that successfully guided grammar work.

### Background

- Sprint 20 final metrics: 7 models fail with `internal_error` (parse stage)
- Target models: clearlak, imsl, indus, sarf, senstran, tfordy, turkpow
- These models parse the Lark grammar but crash during IR builder (`src/ir/parser.py`) tree-walking
- Likely root causes include: table row index mismatches, lead/lag syntax not handled in IR, undefined references during symbol resolution
- Sprint 20 lexer catalog methodology: `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md`

### What Needs to Be Done

1. **Run each model** through `parse_file()` with full traceback capture:
   ```python
   import sys; sys.setrecursionlimit(50000)
   from src.ir.parser import parse_file
   for model in ['clearlak', 'imsl', 'indus', 'sarf', 'senstran', 'tfordy', 'turkpow']:
       try:
           parse_file(f'data/gamslib/raw/{model}.gms')
       except Exception as e:
           print(f"=== {model} ===")
           import traceback; traceback.print_exc()
   ```
2. **Extract the error type and location** from each traceback (file, line, function, exception class)
3. **Classify into subcategories** by root cause:
   - A: Table row index mismatch (e.g., data row has more/fewer elements than header)
   - B: Lead/lag syntax (`x(t-1)`, `x(t+1)`) not handled in IR builder
   - C: Undefined symbol reference during IR construction
   - D: Other (document each individually)
4. **Count models per subcategory** and identify batch-fix opportunities
5. **Estimate fix effort** per subcategory (1h, 2h, 4h)
6. **Write catalog document** with per-model findings and recommended fix order

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify catalog document exists
ls docs/planning/EPIC_4/SPRINT_21/INTERNAL_ERROR_CATALOG.md

# Verify all 7 models covered
grep -c "^###" docs/planning/EPIC_4/SPRINT_21/INTERNAL_ERROR_CATALOG.md
# Should be 7+ (one per model)

# Smoke-test: confirm models still fail
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
for m in ['clearlak','imsl','indus','sarf','senstran','tfordy','turkpow']:
    try: parse_file(f'data/gamslib/raw/{m}.gms'); print(f'{m}: OK')
    except: print(f'{m}: FAIL')
"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/INTERNAL_ERROR_CATALOG.md` — per-model root cause analysis with subcategory classification
- Recommended fix order based on batch-fix potential and model count

### Acceptance Criteria

- [ ] All 7 internal_error models run and tracebacks captured
- [ ] Root causes classified into subcategories (A, B, C, D...)
- [ ] Models grouped by subcategory for batch fixes
- [ ] Fix effort estimated per subcategory
- [ ] Recommended fix order documented
- [ ] Catalog document created

---

## Task 4: Catalog path_syntax_error Root Causes (45 Models)

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Run the 45 path_syntax_error models through the full pipeline, capture the PATH error output, and classify root causes into subcategories. This is the largest single error population and the key to Sprint 21 Priority 3.

### Why This Matters

Sprint 21 Priority 3 allocates 8–12h to reduce path_syntax_error. These are models that successfully translate to MCP but produce files that PATH cannot process. Without root cause clustering, the 8–12h would be spent investigating models one-by-one. A catalog identifies the highest-leverage fixes — if 20/45 models fail for the same reason, one fix addresses 20 models.

### Background

- Sprint 20 final metrics: 45 models fail with `path_syntax_error` (solve stage)
- These models parse, build IR, and emit MCP files — but PATH rejects the MCP with syntax/structure errors
- Potential root causes: malformed equation names, domain mismatches in equation/variable pairs, stationarity system issues, missing variable declarations, incorrect complementarity pairing
- Sprint 20 retrospective recommendation: "Systematic triage (similar to Sprint 20 lexer error catalog) to identify highest-leverage fixes"
- Pipeline test script: `scripts/gamslib/run_full_test.py`

### What Needs to Be Done

1. **Get the list of 45 path_syntax_error models** from the most recent pipeline run (`data/gamslib/gamslib_status.json`)
2. **For a representative sample** (at least 15–20 models), examine the generated MCP file and PATH error output:
   - What does the PATH error message say?
   - What line of the MCP file is problematic?
   - What is the root cause in the emitter/translator?
3. **Classify into subcategories:**
   - A: Malformed equation name (e.g., illegal GAMS characters)
   - B: Domain mismatch (equation domain ≠ variable domain in Model statement)
   - C: Missing variable declaration
   - D: Incorrect complementarity pairing (wrong variable paired with equation)
   - E: Stationarity system issue (equation structure invalid)
   - F: Other (document each)
4. **Count models per subcategory** and identify highest-leverage fixes
5. **Estimate fix effort** per subcategory
6. **Write catalog document** with findings, subcategory counts, and recommended attack order

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify catalog document exists
ls docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md

# Verify status file has path_syntax_error models
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
pse = [m for m,v in data.items() if v.get('error_category') == 'path_syntax_error']
print(f'path_syntax_error models: {len(pse)}')
"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` — subcategory classification with model counts and root cause analysis
- Prioritized fix order based on model count per subcategory and estimated effort

### Acceptance Criteria

- [ ] path_syntax_error model list extracted from pipeline status
- [ ] At least 15–20 models analyzed in detail
- [ ] Root causes classified into subcategories (A–F+)
- [ ] Models counted per subcategory
- [ ] Fix effort estimated per subcategory
- [ ] Highest-leverage fixes identified (most models per fix)
- [ ] Catalog document created with recommended attack order

---

## Task 5: Triage Deferred Sprint 20 Issues

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 3, 4 (catalogs inform overlap with deferred issues)

### Objective

Review all 13 deferred Sprint 20 issues, assess current status, identify overlaps with other Sprint 21 priorities, and recommend which to tackle in Sprint 21 vs. defer further.

### Why This Matters

Sprint 21 Priority 4 allocates 8–12h for 13 deferred issues. Not all may be tractable within Sprint 21's scope — some (e.g., #830 gastrans Jacobian timeout) may require architectural changes. Triaging now prevents wasting sprint time on issues that should be deferred. Additionally, some deferred issues overlap with other priorities (e.g., #837/#840 overlap with Priority 1 macro expansion).

### Background

Deferred issues from Sprint 20 (from `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 418–433):

| Issue | Model | Problem |
|---|---|---|
| #763 | chenery | AD condition propagation |
| #764 | mexss | Accounting variable stationarity |
| #765 | orani | CGE model type incompatible |
| #757 | bearing | Non-convex initialization |
| #810 | lmp2 | Solve in doubly-nested loop |
| #826 | decomp | Empty stationarity equation |
| #827 | gtm | Domain violations from zero-fill |
| #828 | ibm1 | Missing bound multipliers |
| #830 | gastrans | Jacobian timeout (dynamic subset) |
| #835 | bearing | .scale emission (partially done) |
| #837 | springchain | Bracket expr + macro expansion |
| #840 | saras | `%system.nlp%` system macro |
| #789 | — | Min/max in objective equations |

Active issue files: `docs/issues/ISSUE_757_*.md`, `docs/issues/ISSUE_764_*.md`, etc.

### What Needs to Be Done

1. **Review each of the 10 active issue files** in `docs/issues/` (not all 13 have files; some may be in `docs/issues/completed/`)
2. **For each issue, assess:**
   - Current status: still blocked? partially resolved? resolved by Sprint 20 work?
   - Overlap with Sprint 21 priorities (e.g., #837/#840 → Priority 1 macro expansion)
   - Estimated fix effort (in Sprint 21 context, with new capabilities)
   - Dependencies on other Sprint 21 work
3. **Categorize each issue:**
   - **Do in Sprint 21:** tractable, high leverage, overlaps with planned work
   - **Defer to Sprint 22+:** requires architectural change, low leverage, blocked by external factors
4. **Create prioritized triage document** with recommendations

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify all 13 issues accounted for
ls docs/issues/ISSUE_757_*.md docs/issues/ISSUE_763_*.md docs/issues/ISSUE_764_*.md \
   docs/issues/ISSUE_765_*.md docs/issues/ISSUE_789_*.md docs/issues/ISSUE_810_*.md \
   docs/issues/ISSUE_826_*.md docs/issues/ISSUE_827_*.md docs/issues/ISSUE_828_*.md \
   docs/issues/ISSUE_830_*.md docs/issues/ISSUE_835_*.md docs/issues/ISSUE_837_*.md \
   docs/issues/ISSUE_840_*.md 2>/dev/null | wc -l

# Check for any that moved to completed
ls docs/issues/completed/ISSUE_810_*.md docs/issues/completed/ISSUE_835_*.md 2>/dev/null
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md` — per-issue assessment with Sprint 21 / defer recommendation
- Overlap map showing which deferred issues are addressed by Sprint 21 Priority 1–3 work

### Acceptance Criteria

- [ ] All 13 deferred issues reviewed
- [ ] Current status assessed for each
- [ ] Overlaps with Sprint 21 priorities identified (especially #837/#840 → Priority 1)
- [ ] Each issue categorized as "Do in Sprint 21" or "Defer to Sprint 22+"
- [ ] Fix effort estimated for "Do" items
- [ ] Triage document created

---

## Task 6: Analyze Solve-Match Gap (17 Models)

**Status:** :large_blue_circle: NOT STARTED
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Identify the 17 models that solve but don't match (33 solve - 16 match = 17 gap) and classify the divergence causes. This directly supports Sprint 21 Priority 5 (match rate improvement, 16→20+).

### Why This Matters

Sprint 21 Priority 5 targets 20+ matches (currently 16). To plan targeted fixes, we need to understand why 17 models solve successfully but produce different objective values from the reference GAMS solution. Some may be near-matches fixable with tolerance adjustments; others may indicate fundamental formulation issues.

### Background

- Sprint 20 final: 33 solve, 16 match → 17 gap
- Sprint 20 `PIPELINE_MATCH_ANALYSIS.md` identified some near-matches (e.g., port at rel_diff 1.3e-3)
- Divergence causes may include: `.l` initialization differences, `.scale` handling, domain handling, solver settings (PATH options), or genuine MCP formulation issues
- Sprint 20 emitter now supports `.l` initialization (Sprint 20 Days 1–3 work)

### What Needs to Be Done

1. **Extract the 17 non-matching solve-success models** from `data/gamslib/gamslib_status.json`
2. **For each model, record:**
   - GAMS reference objective value
   - MCP solved objective value
   - Relative difference
   - Absolute difference
3. **Sort by relative difference** (smallest first — these are closest to matching)
4. **Classify divergence causes:**
   - A: Near-match (rel_diff < 1e-2) — likely tolerance or minor initialization issue
   - B: Moderate divergence (1e-2 < rel_diff < 1.0) — possible scaling or domain issue
   - C: Large divergence (rel_diff > 1.0) — likely formulation issue
   - D: Solve succeeds but objective is NaN/Inf — emitter bug
5. **For the top 5 near-match models**, investigate the specific cause:
   - Compare `.l` initialization
   - Check if `.scale` values differ
   - Check if domain handling differs
6. **Write analysis document** with recommended fixes ordered by effort/impact

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify analysis document exists
ls docs/planning/EPIC_4/SPRINT_21/SOLVE_MATCH_GAP_ANALYSIS.md

# Verify solve-match gap count
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
solve = [m for m,v in data.items() if v.get('solve_success')]
match = [m for m,v in data.items() if v.get('match')]
print(f'Solve: {len(solve)}, Match: {len(match)}, Gap: {len(solve)-len(match)}')
"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/SOLVE_MATCH_GAP_ANALYSIS.md` — per-model divergence analysis sorted by relative difference
- Top 5 near-match investigation findings with recommended fixes

### Acceptance Criteria

- [ ] All 17 non-matching solve-success models identified
- [ ] Relative and absolute differences recorded for each
- [ ] Models classified into divergence categories (A–D)
- [ ] Top 5 near-match models investigated in detail
- [ ] Recommended fixes documented with effort estimates
- [ ] Analysis document created

---

## Task 7: Audit semantic_undefined_symbol Models

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Medium
**Estimated Time:** 1–2 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** Task 1 (Known Unknowns)

### Objective

Determine whether the 7 `semantic_undefined_symbol` models are failing due to GAMSLIB source issues (models that reference undefined symbols intentionally) or nlp2mcp parser/IR bugs that can be fixed.

### Why This Matters

Sprint 21 includes a "Semantic Error Resolution (~2h)" workstream for these 7 models. The resolution strategy depends entirely on whether these are source issues or bugs: source issues get documented and excluded from metrics; bugs get fixed. Making this determination during prep saves sprint time.

### Background

- Sprint 20 final metrics: 7 models fail with `semantic_undefined_symbol`
- These models parse the grammar and build partial IR, but reference symbols (sets, parameters, variables) not defined in the model file
- Possible causes: `$include` references to external files (nlp2mcp doesn't support `$include`), conditional compilation blocks that define symbols, or genuine GAMSLIB source errors

### What Needs to Be Done

1. **Get the list of 7 semantic_undefined_symbol models** from `data/gamslib/gamslib_status.json`
2. **For each model, run** `parse_file()` and capture the undefined symbol name and context
3. **Check the original GAMS source** for each undefined symbol:
   - Is it defined in a `$include` file? → Cannot fix without `$include` support
   - Is it defined in a conditional block (`$if`/`$ifi`)? → May be fixable with macro expansion
   - Is it a GAMSLIB source error? → Document and exclude
   - Is it an nlp2mcp parser bug (symbol defined but not captured)? → Fix
4. **Classify each model** and write findings

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify audit document exists
ls docs/planning/EPIC_4/SPRINT_21/SEMANTIC_ERROR_AUDIT.md

# Verify count
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
sue = [m for m,v in data.items() if v.get('error_category') == 'semantic_undefined_symbol']
print(f'semantic_undefined_symbol: {len(sue)}: {sue}')
"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/SEMANTIC_ERROR_AUDIT.md` — per-model findings with classification
- Clear recommendation: fix vs. document-and-exclude for each model

### Acceptance Criteria

- [ ] All 7 semantic_undefined_symbol models identified
- [ ] Undefined symbol name and context captured for each
- [ ] Root cause classified (missing `$include`, conditional block, source error, parser bug)
- [ ] Each model classified as "fixable" or "exclude"
- [ ] Audit document created

---

## Task 8: Snapshot Baseline Metrics & Pipeline Retest

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Medium
**Estimated Time:** 1–2 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** None

### Objective

Run the full pipeline test and snapshot baseline metrics at the start of Sprint 21 prep. This establishes the ground truth against which Sprint 21 progress will be measured.

### Why This Matters

Sprint 20 established a baseline at commit `dc390373` (112/160 parse, 96/112 translate, 27/96 solve, 10/27 match). Sprint 21 needs a fresh baseline reflecting all Sprint 20 work (25 PRs merged). The PROJECT_PLAN.md Sprint 21 note says "parse 132/160, translate 120/132, solve 33/120, match 16/33" — this needs to be verified as the actual starting point.

### Background

- Sprint 20 final metrics (from retrospective): parse 132/160, translate 120/132, solve 33, match 16, tests 3,715
- Pipeline retest command: `.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet` (parse only) or full pipeline
- Baseline snapshot file: `docs/planning/EPIC_4/SPRINT_21/BASELINE_METRICS.md`
- Sprint 20 baseline reference: `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md`

### What Needs to Be Done

1. **Run full test suite:** `make test` — verify all tests pass, record count
2. **Run full pipeline retest:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
3. **Record all metrics:**
   - Parse: X/160
   - Translate: X/Y
   - Solve: X
   - Match: X
   - Tests: X passed, X skipped, X xfailed
   - Error categories: lexer_invalid_char, internal_error, semantic_undefined_symbol, etc.
4. **Compare with Sprint 20 retrospective values** — confirm consistency
5. **Write baseline document** with commit hash, date, and all metrics

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Run tests
make test 2>&1 | tail -5

# Run pipeline
.venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | tail -20

# Verify baseline document
ls docs/planning/EPIC_4/SPRINT_21/BASELINE_METRICS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/BASELINE_METRICS.md` — snapshot with commit hash, date, and all pipeline metrics
- Confirmation that Sprint 20 retrospective values match current state

### Acceptance Criteria

- [ ] Full test suite passes (3,715+ tests)
- [ ] Full pipeline retest completed
- [ ] All metric categories recorded
- [ ] Values compared with Sprint 20 retrospective
- [ ] Baseline document created with commit hash

---

## Task 9: Review Sprint 20 Retrospective Action Items

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Medium
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** None

### Objective

Review the Sprint 20 retrospective to ensure all action items and process recommendations are captured in Sprint 21 planning.

### Why This Matters

Sprint 20 retrospective identified 5 process recommendations and multiple technical recommendations. Need to verify Sprint 21 plan addresses all of these, and that no action items were overlooked.

### Background

- `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md` — full retrospective
- Lines 300–362: Sprint 21 technical recommendations (already incorporated into PROJECT_PLAN.md)
- Lines 351–361: Process recommendations (5 items, now in PROJECT_PLAN.md Sprint 21 section)
- Lines 365–381: Final metrics for tracking
- Lines 383–440: What Went Well / What Could Be Improved / What We'd Do Differently

### What Needs to Be Done

1. **Read Sprint 20 retrospective** sections: "What Could Be Improved" and "What We'd Do Differently"
2. **Extract all action items** (explicit and implied)
3. **Map each action item** to Sprint 21 plan or prep task:
   - Already captured → note as "addressed"
   - Not captured → add to Sprint 21 plan or create new prep task
4. **Verify process recommendations** (5 items) are reflected in Sprint 21 working practices
5. **Document mapping** in brief alignment document

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify alignment document exists
ls docs/planning/EPIC_4/SPRINT_21/RETROSPECTIVE_ALIGNMENT.md

# Verify all 5 process recommendations referenced
grep -c "process" docs/planning/EPIC_4/SPRINT_21/RETROSPECTIVE_ALIGNMENT.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/RETROSPECTIVE_ALIGNMENT.md` — mapping of Sprint 20 action items to Sprint 21 plan
- Confirmation that all critical action items are addressed

### Acceptance Criteria

- [ ] Sprint 20 retrospective fully reviewed
- [ ] All action items extracted
- [ ] Each mapped to Sprint 21 plan or identified as gap
- [ ] All 5 process recommendations confirmed in Sprint 21 practices
- [ ] Alignment document created

---

## Task 10: Plan Sprint 21 Detailed Schedule

**Status:** :large_blue_circle: NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 21 Day 1
**Owner:** Development team
**Dependencies:** All tasks (1–9)

### Objective

Create the detailed day-by-day Sprint 21 execution plan incorporating all prep research, catalogs, and design documents.

### Why This Matters

Sprint 21 has 46–68h of work across 9 workstreams. A detailed schedule with day-by-day task assignments, dependency chains, and checkpoint gates ensures work proceeds in optimal order and nothing falls through the cracks.

### Background

- Sprint 20 plan: `docs/planning/EPIC_4/SPRINT_20/PLAN.md` — 15-day schedule with workstream assignments
- Sprint 20 execution prompts: `docs/planning/EPIC_4/SPRINT_20/prompts/PLAN_PROMPTS.md` — day-by-day execution guides
- Sprint 21 scope from `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 389–505
- Sprint 21 acceptance criteria: parse ≥135/160, lexer_invalid_char ≤5, internal_error ≤3, solve ≥36, match ≥20

### What Needs to Be Done

1. **Review all prep task outputs** (Tasks 1–9 deliverables)
2. **Allocate workstreams to days** based on:
   - Dependencies (macro expansion before models that use macros)
   - Effort estimates (from catalogs and design documents)
   - Risk (high-risk items early)
   - Checkpoint gates (pipeline retests at regular intervals)
3. **Create day-by-day schedule** with:
   - Workstream assignments per day
   - Specific tasks and deliverables
   - Time estimates
   - Dependencies on prior days
   - Verification commands
4. **Define checkpoint gates** (e.g., Day 5, Day 10, Day 14)
5. **Create execution prompts** (`docs/planning/EPIC_4/SPRINT_21/prompts/PLAN_PROMPTS.md`)
6. **Define acceptance criteria** per day and overall

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
# Verify plan exists
ls docs/planning/EPIC_4/SPRINT_21/PLAN.md

# Verify execution prompts exist
ls docs/planning/EPIC_4/SPRINT_21/prompts/PLAN_PROMPTS.md

# Verify all acceptance criteria referenced
grep -c "acceptance" docs/planning/EPIC_4/SPRINT_21/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_21/PLAN.md` — detailed day-by-day schedule with workstream assignments
- `docs/planning/EPIC_4/SPRINT_21/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- Sprint 21 sprint log template: `docs/planning/EPIC_4/SPRINT_21/SPRINT_LOG.md`

### Acceptance Criteria

- [ ] Day-by-day schedule created covering entire sprint
- [ ] All 9 workstreams assigned to specific days
- [ ] Time estimates per day sum to 46–68h total
- [ ] Dependencies documented between days
- [ ] Checkpoint gates defined
- [ ] Execution prompts created for each day
- [ ] Sprint log template created
- [ ] Acceptance criteria defined per day and overall
- [ ] Plan reviewed and approved

---

## Summary and Critical Path

### Critical Path (Must Complete Before Sprint 21 Day 1)

1. **Task 1: Known Unknowns** (2–3h) — FIRST (unblocks all research tasks)
2. **Task 2: Macro Expansion Research** (3–4h) — CRITICAL (new subsystem design)
3. **Task 10: Plan Sprint 21** (3–4h) — LAST (depends on all other tasks)

**Total Critical Path Time:** ~8–11 hours

### High Priority (Should Complete Before Sprint 21)

3. **Task 3: internal_error Catalog** (2–3h) — parallel with Tasks 2, 4
4. **Task 4: path_syntax_error Catalog** (3–4h) — parallel with Tasks 2, 3
5. **Task 5: Deferred Issues Triage** (2–3h) — after Tasks 3, 4
6. **Task 6: Solve-Match Gap Analysis** (2–3h) — parallel with Tasks 3, 4

**Total High Priority Time:** ~9–13 hours

### Medium Priority (Complete Before or Early in Sprint 21)

7. **Task 7: Semantic Error Audit** (1–2h)
8. **Task 8: Baseline Metrics** (1–2h) — can run any time
9. **Task 9: Retrospective Review** (1h) — can run any time

**Total Medium Priority Time:** ~3–5 hours

### Overall Prep Time: 20–28 hours (~3–4 working days)

---

## Success Criteria for Prep Phase

- [ ] Known Unknowns document created (20+ unknowns, 6+ categories)
- [ ] Macro expansion design document completed
- [ ] internal_error root cause catalog completed (7 models)
- [ ] path_syntax_error root cause catalog completed (45 models)
- [ ] Deferred issues triaged (13 issues, do/defer categorization)
- [ ] Solve-match gap analyzed (17 models)
- [ ] Semantic error models audited (7 models)
- [ ] Baseline metrics snapshotted and verified
- [ ] Sprint 20 retrospective action items confirmed
- [ ] Sprint 21 detailed schedule created

**Overall Goal:** No blockers, no surprises, data-driven sprint start with catalogs and designs ready

---

## Appendix: Document Cross-References

### Sprint Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` lines 389–505 — Sprint 21 scope and acceptance criteria

### Epic Goals
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 strategic goals (GAMSLIB LP/NLP/QCP coverage)

### Prior Sprint Work
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md` — Sprint 20 retrospective with Sprint 21 recommendations
- `docs/planning/EPIC_4/SPRINT_20/SPRINT_LOG.md` — Sprint 20 daily progress
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` — Sprint 20 schedule (template reference)
- `docs/planning/EPIC_4/SPRINT_20/LEXER_ERROR_CATALOG_UPDATE.md` — catalog methodology reference
- `docs/planning/EPIC_4/SPRINT_20/PIPELINE_MATCH_ANALYSIS.md` — solve-match analysis reference
- `docs/planning/EPIC_4/SPRINT_20/BASELINE_METRICS.md` — Sprint 20 baseline (comparison reference)
- `docs/planning/EPIC_4/SPRINT_20/KNOWN_UNKNOWNS.md` — Sprint 20 unknowns (template reference)

### Active Issues
- `docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md`
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`
- `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md`
- `docs/issues/ISSUE_789_minmax-reformulation-spurious-variables.md`
- `docs/issues/ISSUE_826_decomp-empty-stationarity-equation.md`
- `docs/issues/ISSUE_827_gtm-domain-violation-zero-fill.md`
- `docs/issues/ISSUE_828_ibm1-locally-infeasible-stationarity.md`
- `docs/issues/ISSUE_830_gastrans-jacobian-dynamic-subset-timeout.md`
- `docs/issues/ISSUE_837_springchain-bracket-expr-scalar-data.md`
- `docs/issues/ISSUE_840_saras-system-nlp-macro.md`

### Research Documents
- `docs/research/gamslib_parse_errors.md` — parse error analysis
- `docs/research/gamslib_kpi_definitions.md` — KPI definitions for pipeline metrics
- `docs/research/minmax_objective_reformulation.md` — min/max reformulation strategies (relevant to #789)

### Key Source Files
- `src/ir/preprocessor.py` — preprocessor (macro expansion target)
- `src/ir/parser.py` — IR builder (internal_error fixes)
- `src/gams/gams_grammar.lark` — Lark grammar
- `src/cli.py` — CLI entry point
- `scripts/gamslib/run_full_test.py` — pipeline retest script

---

**Document Created:** 2026-02-23
**Sprint 21 Target Start:** TBD
**Next Steps:** Execute prep tasks in order (Task 1 first), verify completion, begin Sprint 21
